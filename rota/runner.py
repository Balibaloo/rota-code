"""
The session runner. One message in, one atomic commit out.

A session is a function:

    (fixture database, one inbound message) -> (writes, outbound messages, receipt)

No hidden state, no shared context, no conversation memory. That is what makes
every role testable by seed -> inject -> run -> assert on deltas, and it is why
chat-history-as-memory had to go: the working set replaces it.

The loop is short on purpose. Wake with a prompt built from the role's pushed
working set, read `TOOL:` calls out of the completion, dispatch them against the
sandbox, feed results back, and stop when the model emits no more calls or the
iteration cap trips. Then commit everything at once, or nothing.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass, field
from typing import Any

from . import (api, graph as graph_mod, llm, prompts, sandbox as sandbox_mod,
               toolproto, toolschema)
from .db import OutboundMessage, SessionResult, Write, session_commit
from .scheduler import Wake, claim, release

MAX_ITERATIONS = 12


@dataclass
class RunOutcome:
    session_id: str
    committed: bool
    iterations: int
    completions: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    result: SessionResult | None = None


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def _mode_key(wake: Wake, conn: sqlite3.Connection | None = None) -> str:
    """
    Which prompt piece this wake selects.

    A message wake is keyed by its verb; a tick by the tick's name. Both are
    enumerable — the verbs from the graph, the ticks from the scheduler — so the
    set of modes a role has is a fact about the system rather than a convention.

    One refinement the gates force: a principal `verdict` means two different things
    depending on what it answers. After a `confirm` it is ratification (L1);
    after a `present` it is a signoff ruling to relay. Same verb, different job,
    so the mode is keyed by the *cause* rather than by the verb alone. Without
    this the two gates would share one prompt and neither would be right.
    """
    if wake.kind == "message":
        verb = wake.detail or ""
        if verb == "verdict" and conn is not None and wake.message_id:
            row = conn.execute(
                "SELECT c.verb AS cause_verb FROM messages m "
                "LEFT JOIN messages c ON c.id = m.cause_id WHERE m.id = ?",
                (wake.message_id,)).fetchone()
            if row and row["cause_verb"] == "present":
                return "verdict_signoff"
        return verb
    if wake.kind.startswith("tick:"):
        return wake.kind.split(":", 1)[1]
    return wake.kind


def build_prompt(role: str, sb: sandbox_mod.Sandbox, wake: Wake,
                 pushed: dict[str, Any], instructions: str,
                 inbound: dict[str, Any] | None = None) -> tuple[str, str]:
    """
    System prompt = who you are and what you may do; user prompt = why you woke.

    The working set is *pushed* rather than fetched. Having `model.consult()`
    available does not mean a cold session will call it, and a role that
    re-derives what it was already given wastes a turn. Tools are for going
    deeper than the push.
    """
    fns = "\n".join(f"  TOOL: {sig}" for sig in sb.signatures())
    system = (
        f"{instructions.strip()}\n\n"
        f"You are {role}. This is a single session: you are woken once, you act, "
        f"you end. You have no memory of previous sessions and will have none of "
        f"this one.\n\n"
        f"Your working set is exactly these functions. Nothing else exists:\n{fns}\n\n"
        f"Call one per line, in this form:\n"
        f"  TOOL: artefact.verb(key='value')\n"
        f"Emit no tool calls when you are done."
    )

    body = [f"You were woken by: {wake.kind}"]
    if wake.message_id:
        body.append(f"Inbound message: {wake.message_id} ({wake.detail})")
    if wake.refs:
        body.append(f"Refs: {', '.join(wake.refs)}")
    if inbound:
        body.append("\nThe message that woke you:")
        body.append(json.dumps(inbound, indent=2, default=str))
    if pushed:
        body.append("\nYour working set:")
        for key, value in pushed.items():
            body.append(f"\n[{key}]\n{json.dumps(value, indent=2, default=str)}")
    return system, "\n".join(body)


def resolve_inbound(conn: sqlite3.Connection, wake: Wake) -> dict[str, Any]:
    """
    The content of the triggering message, resolved one hop.

    A message carries refs, not prose — conclusions travel, reasoning stays home.
    But a role woken by refs alone cannot act on them without a fetch it has no
    reason to think of, so the refs are resolved here to exactly one level: the
    rows they name, nothing those rows point at in turn.

    Principal entries are the exception that needs handling: the principal's actual
    words are not yet an artefact when Liaison is woken to record them, so they
    are carried on the message itself.
    """
    if not wake.message_id:
        return {}

    row = conn.execute(
        "SELECT id, from_role, verb, body_refs, round_no FROM messages WHERE id = ?",
        (wake.message_id,)).fetchone()
    if not row:
        return {}

    out: dict[str, Any] = {
        "from": row["from_role"], "verb": row["verb"],
        "refs": json.loads(row["body_refs"] or "[]"),
    }

    from .principal import entry_for, verdict_for

    text = entry_for(conn, wake.message_id)
    if text:
        out["principal_said"] = text
        # Already in the transcript, recorded mechanically. The role is told its
        # id so it can segment against it rather than re-appending it.
        recorded = conn.execute(
            "SELECT id FROM entries WHERE id = ?",
            (f"e_{wake.message_id}",)).fetchone()
        if recorded:
            out["entry_id"] = recorded["id"]
            out["already_recorded"] = True
    ruling = verdict_for(conn, wake.message_id)
    if ruling:
        out["principal_verdict"] = ruling

    resolved = {}
    for ref in out["refs"]:
        for table, cols in (
            ("statements", "id, text, status"),
            ("items", "id, text, kind, approval"),
            ("criteria", "id, ticket_id, text"),
            ("tickets", "id, item_id, text"),
            ("constraints", "id, headline"),
            ("glossary_terms", "id, term, sense_short"),
            ("ledger", "id, about_ref, default_taken"),
        ):
            hit = conn.execute(
                f"SELECT {cols} FROM {table} WHERE id = ?", (ref,)).fetchone()
            if hit:
                resolved[ref] = dict(hit)
                break
    if resolved:
        out["resolved_refs"] = resolved

    # Sibling reports in the same thread: harvest cannot dedupe what it cannot see.
    if row["verb"] == "report":
        siblings = [dict(r) for r in conn.execute(
            "SELECT id, from_role, body_refs FROM messages "
            "WHERE verb = 'report' AND id != ? ORDER BY seq", (wake.message_id,))]
        if siblings:
            out["other_reports"] = siblings

    return out


def push_working_set(role: str, sb: sandbox_mod.Sandbox, wake: Wake) -> dict[str, Any]:
    """
    What arrives in the prompt without being asked for.

    Deliberately small: the index of what this role owns, plus whatever its wake
    points at. Everything else stays behind a tool call.
    """
    pushed: dict[str, Any] = {}
    for name in sb.functions():
        artefact, verb = name.split(".", 1)
        if verb in ("consult", "list"):          # own-artefact index, cheap by design
            try:
                pushed[name] = sb.call(name)
            except TypeError:
                continue                          # needs arguments; leave it to the model
    return pushed


def run_session(
    conn: sqlite3.Connection,
    wake: Wake,
    *,
    backend: llm.Backend | None = None,
    pins: llm.Pins | None = None,
    instructions: str = "",
    mode: str = "normal",
    batch_id: str | None = None,
    max_iterations: int = MAX_ITERATIONS,
    native_tools: bool | None = None,
    g: graph_mod.Graph | None = None,
) -> RunOutcome:
    """
    Wake one role with one message, run its tool loop, commit atomically.

    On any failure the session never happened: nothing is committed, the claim is
    released, and the trigger message stays on the frontier with its attempt
    count raised. Enough failures and boot quarantines it.
    """
    g = g or graph_mod.load()
    backend = backend or llm.default_backend()
    pins = pins or llm.Pins()

    # Instructions = base + the piece for whatever woke this session. A role's
    # modes are enumerable from the graph, so which piece loads is derived rather
    # than chosen.
    if not instructions:
        try:
            instructions = prompts.compose(wake.role, _mode_key(wake, conn))
        except prompts.MissingPrompt:
            instructions = ""

    session_id = new_id("s")
    entry_id = None
    if wake.message_id:
        row = conn.execute(
            "SELECT id FROM entries WHERE id = ?",
            (f"e_{wake.message_id}",)).fetchone()
        entry_id = row["id"] if row else None

    sb = sandbox_mod.build(wake.role, conn, mode=mode, batch_id=batch_id,
                           session_id=session_id, entry_id=entry_id, g=g,
                           allow=prompts.mode_tools(wake.role, _mode_key(wake, conn)))
    sb.ctx.trigger = wake.message_id

    claim(conn, wake.role, session_id, wake.message_id)
    if wake.message_id:
        conn.execute("UPDATE messages SET attempts = attempts + 1 WHERE id = ?",
                     (wake.message_id,))

    outcome = RunOutcome(session_id=session_id, committed=False, iterations=0)

    try:
        pushed = push_working_set(wake.role, sb, wake)
        inbound = resolve_inbound(conn, wake)
        system, user = build_prompt(wake.role, sb, wake, pushed, instructions, inbound)
        pins = pins.with_prompt(system + user)

        transcript = [user]
        allowed = set(sb.functions())

        # Native function calling where the model supports it. This removes the
        # failure that cost the most with small models: dropping the TOOL:
        # marker, which made a session commit *empty* — success-shaped failure.
        # The TOOL: protocol remains for models without tool support, which is
        # exactly what it is for.
        use_native = native_tools
        if use_native is None:
            use_native = getattr(backend, "name", "") == "ollama" and                 llm.supports_tools(pins.model)
        schemas = toolschema.schemas_for_sandbox(sb) if use_native else None

        for iteration in range(1, max_iterations + 1):
            outcome.iterations = iteration
            completion = backend.complete(system, "\n\n".join(transcript), pins)
            outcome.completions.append(completion.text)

            calls = toolproto.extract_lenient(completion.text, allowed)
            if not calls:
                break

            feedback = []
            for call in calls:
                if isinstance(call, toolproto.ToolError):
                    outcome.errors.append(call.reason)
                    feedback.append(f"ERROR {call.raw}: {call.reason}")
                    continue
                err = toolproto.validate(call, allowed)
                if err:
                    outcome.errors.append(err.reason)
                    feedback.append(f"ERROR {call.raw}: {err.reason}")
                    continue
                try:
                    result = sb.call(call.name, **call.args)
                    feedback.append(f"OK {call.name} -> "
                                    f"{json.dumps(result, default=str)[:1200]}")
                except Exception as exc:               # tool error, not session-fatal
                    outcome.errors.append(f"{call.name}: {exc}")
                    feedback.append(f"ERROR {call.name}: {exc}")

            transcript.append(completion.text)

            # A role that has sent its outbound message has, in almost every
            # mode, finished. Without saying so the model keeps going and starts
            # inventing work — an Liaison intake session will happily fabricate
            # a second principal entry, which is the one thing it must never do.
            if sb.ctx.outbound:
                feedback.append(
                    "You have sent your message. Your work for this session is "
                    "complete — emit no further tool calls."
                )
            transcript.append("\n".join(feedback))

        result = SessionResult(
            session_id=session_id,
            role=wake.role,
            trigger_msg=wake.message_id,
            mode=mode,
            writes=[_as_write(w) for w in sb.ctx.writes],
            messages=_messages_from(sb, wake, session_id),
            tool_calls=sandbox_mod.drain_calls(sb.ctx),
            pins=pins.as_dict(),
        )
        session_commit(conn, result)
        outcome.committed = True
        outcome.result = result
        return outcome

    except Exception as exc:
        outcome.errors.append(f"session failed: {exc!r}")
        release(conn, wake.role)
        sandbox_mod.drain_calls(sb.ctx)
        return outcome


def _as_write(staged: tuple) -> Write:
    """Staged writes are (table, row_id, values) or (..., amends)."""
    table, row_id, values, *rest = staged
    return Write(table, row_id, values, amends=rest[0] if rest else True)


def _messages_from(sb: sandbox_mod.Sandbox, wake: Wake, session_id: str) -> list[OutboundMessage]:
    """Outbound messages staged by the role during its session."""
    out = []
    for m in sb.ctx.outbound:
        out.append(OutboundMessage(
            id=m["id"], to_role=m["to_role"], verb=m["verb"],
            body_refs=m["body_refs"], round_no=m["round_no"],
            cause_id=m.get("cause_id") or wake.message_id,
            thread_id=None,
        ))
    return out
