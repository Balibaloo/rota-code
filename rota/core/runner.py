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

from . import sandbox as sandbox_mod
from ..design import graph as graph_mod
from ..llm import llm, toolproto, toolschema
from ..roles import api, prompts
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


_COUNTED = {"s": "sessions", "m": "messages", "tr": "test_runs"}


def new_id(prefix: str, conn: sqlite3.Connection | None = None,
           offset: int = 0) -> str:
    """
    An id that is unique in the database and the same on a replay.

    It was `uuid4`, and the randomness leaked somewhere expensive. A tool result
    goes back to the model as feedback — `OK msg.confirm_principal -> {"id":
    "m_a1b2c3d4ef"}` — so the *prompt for turn two* carried a random string.
    Cassettes are keyed on the prompt, which meant turn one replayed and every
    turn after it missed: 1140 of 1419 recordings had never been reused once,
    and re-running an unchanged case still cost a full model run.

    Counting from the table instead is deterministic where it matters and unique
    where it has to be. A fixture database starts empty, so a case replays
    byte-identically; a long-lived one keeps counting. `uuid4` remains the
    fallback for anything not table-backed, where nobody is replaying anyway.
    """
    table = _COUNTED.get(prefix)
    if conn is not None and table:
        # `offset` is what a session has staged but not committed. Messages are
        # held in the context until the commit lands atomically, so counting the
        # table alone would hand the same id to every message in one session.
        n = conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]
        return f"{prefix}{n + offset + 1}"
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
        f"Call one per line. `TOOL:` is a literal marker — write those five "
        f"characters, then the function name from the list above, then its "
        f"arguments in brackets:\n"
        f"  TOOL: artefact.verb(key='value')\n"
        f"Only `artefact.verb` and `key` stand in for something; everything "
        f"else on that line is written exactly as shown.\n\n"
        f"Two kinds of id, and telling them apart matters. An id for something "
        f"you are creating is yours to invent — make it short and unique, and "
        f"do not build it out of an id you were shown. An id for something that "
        f"already exists must be one you were given: an invented one names no "
        f"row and the call cannot land.\n"
        f"Results come back on your next turn, never inside this one. Ask for "
        f"everything you need to know in one go — several questions cost one "
        f"turn. But once you have asked anything, stop: what you do about the "
        f"answers is next turn's work, and anything you write now was decided "
        f"without them.\n"
        f"Emit no tool calls when you are done."
    )

    body = [f"You were woken by: {wake.kind}"]
    if wake.message_id:
        body.append(f"Inbound message: {wake.message_id} ({wake.detail})")
    if wake.refs:
        body.append(f"Refs: {', '.join(wake.refs)}")
    if inbound:
        body.append("\nThe reports that came back:" if "reports" in inbound
                    else "\nThe message that woke you:")
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

    A round-close wake has no single triggering message — it has a thread full of
    them — and that used to mean it was handed nothing at all. Liaison has no
    reader for messages (rightly: reading your own wake is not a capability), so
    `round_close` was told to compose what came back while being shown none of
    it. The whole round is resolved here for exactly the same reason one message
    is: it is the wake, not a fetch.
    """
    if wake.kind == "tick:round_close":
        return _resolve_round(conn, wake)
    if not wake.message_id:
        return {}

    row = conn.execute(
        "SELECT id, from_role, verb, body_refs, body_text, round_no "
        "FROM messages WHERE id = ?", (wake.message_id,)).fetchone()
    if not row:
        return {}

    out: dict[str, Any] = {
        "from": row["from_role"], "verb": row["verb"],
        "refs": json.loads(row["body_refs"] or "[]"),
    }
    # Present on one channel only, and on that one it is the whole message: the
    # Researcher shares no artefact with its asker, so the refs beside this are
    # usually empty and always insufficient.
    if row["body_text"]:
        out["asks"] = row["body_text"]

    from ..roles.principal import entry_for, verdict_for

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

    resolved = _resolve_refs(conn, out["refs"])
    if resolved:
        out["resolved_refs"] = resolved

    # Sibling reports in the same thread: harvest cannot dedupe what it cannot
    # see. This is the ladder's single report now -- in-round reports are
    # harvested by `round_close` and never tip -- but a second one arriving out
    # of band is still worth showing, and `thread_id` is what keeps it to the
    # same conversation. Without that filter it pulled in every report the
    # system had ever sent.
    if row["verb"] == "report":
        siblings = [dict(r) for r in conn.execute(
            "SELECT id, from_role, body_refs FROM messages "
            "WHERE verb = 'report' AND thread_id = ("
            "  SELECT thread_id FROM messages WHERE id = ?) "
            "  AND id != ? ORDER BY seq", (wake.message_id, wake.message_id))]
        if siblings:
            out["other_reports"] = siblings

    return out


def _resolve_refs(conn: sqlite3.Connection, refs) -> dict[str, Any]:
    """Refs to rows, one hop deep. Nothing those rows point at in turn."""
    resolved: dict[str, Any] = {}
    for ref in refs:
        if ref in resolved:
            continue
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
    return resolved


def _resolve_round(conn: sqlite3.Connection, wake: Wake) -> dict[str, Any]:
    """
    Every report in the round, each one's refs resolved one hop.

    Kept as one block on purpose. Dedupe is the only reason the round waits, and
    it is a judgement about the reports *together* -- two roles describing one
    blocker in two vocabularies is visible in the pair and invisible in either
    half. Handing them over one at a time is what the scheduler already refuses
    to do; handing them over unresolved would be the same mistake in the prompt.
    """
    thread = wake.refs[0] if wake.refs else None
    if not thread:
        return {}

    rows = conn.execute(
        "SELECT id, from_role, body_refs FROM messages "
        "WHERE thread_id = ? AND verb = 'report' ORDER BY seq", (thread,)
    ).fetchall()
    if not rows:
        return {}

    reports = []
    every_ref: list[str] = []
    for r in rows:
        refs = json.loads(r["body_refs"] or "[]")
        every_ref.extend(refs)
        reports.append({"id": r["id"], "from": r["from_role"], "refs": refs})

    out: dict[str, Any] = {"thread": thread, "reports": reports}
    resolved = _resolve_refs(conn, every_ref)
    if resolved:
        out["resolved_refs"] = resolved
    return out


def push_working_set(role: str, sb: sandbox_mod.Sandbox, wake: Wake,
                     g: graph_mod.Graph | None = None) -> dict[str, Any]:
    """
    What arrives in the prompt without being asked for.

    Everything the role can read *without being told anything it does not
    already have*. Anything that needs an argument stays behind a tool call.

    The rule used to be the verbs `consult` and `list`, and the roles it left
    out were the ones that needed it most. Critic's whole working set is
    `criteria.load`, `tests.load` and `code.read` — three batch-scoped reads
    that take no arguments, none of them named `consult` — so it woke with an
    empty prompt under a brief that says "that is everything you get, and it is
    everything you need", and answered:

        I'm ready to review a batch of code changes. Please provide the
        criteria.load, tests.load and code.read data for me to work with.

    Which is a fair reading. It was told what it would have, not told to fetch
    it, and a cold session has no habit of fetching. Callable-with-no-arguments
    is the honest rule: if the session already holds everything a read needs,
    making the model ask for it is a turn spent on nothing.
    """
    reads = {f"{e.t}.{e.v}" for e in (g or graph_mod.load()).of_type("reads")
             if e.s == role}

    pushed: dict[str, Any] = {}
    for name in sb.functions():
        if name not in reads:
            continue          # a write is never speculative; the graph says which
        try:
            pushed[name] = sb.call(name)
        except (TypeError, sandbox_mod.ArgumentError):
            continue     # needs to be told something; leave it to the model
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
    area: str | None = None,
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

    session_id = new_id("s", conn)
    entry_id = None
    if wake.message_id:
        row = conn.execute(
            "SELECT id FROM entries WHERE id = ?",
            (f"e_{wake.message_id}",)).fetchone()
        entry_id = row["id"] if row else None

    # Law 11, decided by the wake rather than by the role: a survey is reading
    # a codebase, so what it writes was found. Everything else was chosen.
    provenance = "observed" if wake.kind == "tick:survey" else "decided"

    sb = sandbox_mod.build(wake.role, conn, mode=mode, batch_id=batch_id,
                           session_id=session_id, entry_id=entry_id,
                           provenance=provenance, g=g,
                           area=area or (wake.refs[0]
                                 if wake.kind == "tick:survey" and wake.refs else None),
                           allow=prompts.mode_tools(wake.role, _mode_key(wake, conn)))
    sb.ctx.trigger = wake.message_id

    claim(conn, wake.role, session_id, wake.message_id)
    if wake.message_id:
        conn.execute("UPDATE messages SET attempts = attempts + 1 WHERE id = ?",
                     (wake.message_id,))

    outcome = RunOutcome(session_id=session_id, committed=False, iterations=0)

    try:
        pushed = push_working_set(wake.role, sb, wake, g)
        inbound = resolve_inbound(conn, wake)
        system, user = build_prompt(wake.role, sb, wake, pushed, instructions, inbound)
        pins = pins.with_prompt(system + user)

        transcript = [user]
        allowed = set(sb.functions())
        # Which of them answer a question. The graph is the authority: a read
        # edge is a read, whatever the verb happens to be called.
        read_fns = {f"{e.t}.{e.v}" for e in (g or graph_mod.load()).of_type("reads")
                    if e.s == wake.role}

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
            if getattr(completion, "truncated", False):
                outcome.errors.append(
                    f"prompt did not fit: {completion.prompt_tokens} tokens "
                    f"evaluated against a {pins.num_ctx} window — the session "
                    f"was briefed with less than it was given")

            calls = toolproto.extract_lenient(completion.text, allowed)
            if not calls:
                break

            feedback = []
            held = []
            seen_read = False
            for i, call in enumerate(calls):
                if isinstance(call, toolproto.ToolError):
                    outcome.errors.append(call.reason)
                    feedback.append(f"ERROR {call.raw}: {call.reason}")
                    continue
                err = toolproto.validate(call, allowed)
                if err:
                    outcome.errors.append(err.reason)
                    feedback.append(f"ERROR {call.raw}: {err.reason}")
                    continue

                # Acting on a read you have not seen is the fault here, and it
                # was the commonest one in the suite: 309 of 598 multi-call
                # completions did it. The Tester told a Developer its challenge
                # was wrong having never seen the criterion it had just asked for.
                #
                # So the *action* is held, not the turn. Reads all run: gathering
                # four answers costs one round trip, and the role decides once it
                # has them. Stopping at the first read instead cost a turn per
                # read, and the model spent them re-sending a batch that led with
                # another read every time -- four turns to reach a write it had
                # already written correctly in the first one, by which point it
                # believed the held calls had run.
                #
                # A run of writes still runs: a role editing four files has
                # already decided, and needs no round trip between them.
                if seen_read and call.name not in read_fns:
                    held = [c.raw or getattr(c, "name", "?") for c in calls[i:]]
                    break
                seen_read = seen_read or call.name in read_fns

                try:
                    result = sb.call(call.name, *call.pos, **call.args)
                    feedback.append(f"OK {call.name} -> "
                                    f"{json.dumps(result, default=str)[:1200]}")
                except Exception as exc:               # tool error, not session-fatal
                    outcome.errors.append(f"{call.name}: {exc}")
                    feedback.append(f"ERROR {call.name}: {exc}")

            if held:
                feedback.append(
                    "NOT RUN, because you wrote them before the answers above "
                    f"came back: {', '.join(held)}. You have the answers now. "
                    "Send them again if they are still what you want.")

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

            # And when saying so is not enough, stop.
            #
            # Asking nicely held for most modes and not for the ones that matter:
            # Gatekeeper answering a scope inquiry sent `answer` three times with
            # slightly different refs, which the duplicate guard cannot catch
            # because they are three different messages. Every one after the
            # first is the same answer restated, and the recipient has to
            # reconcile three.
            #
            # The rule is structural rather than a count. A mode narrows to the
            # channels its job needs, so a mode that has used all of them has
            # said everything it was woken to say — one for `ask`, three for
            # Liaison's broadcast, and no number written down anywhere.
            channels = {f for f in allowed if f.startswith("msg.")}
            used = {f"msg.{sandbox_mod._verb_to_attr(m['verb'])}_{m['to_role']}"
                    for m in sb.ctx.outbound}
            if channels and channels <= used:
                break

            # A survey mode has no channels at all, so the rule above never fires
            # and every survey ran to the iteration cap. Attesting is what closes
            # an area -- the same shape as sending, in a mode that sends nothing
            # -- and a session that kept going past it attested a second time
            # under a second invented id. That was the top mechanism in the run:
            # "expected writes to survey_records (1), got 2", three cases.
            if any(w[0] == "survey_records" for w in sb.ctx.writes):
                break

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
            body_refs=m["body_refs"], body_text=m.get("body_text"),
            round_no=m["round_no"],
            cause_id=m.get("cause_id") or wake.message_id,
            thread_id=None,
        ))
    return out
