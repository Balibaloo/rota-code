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
import re
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
    # What the session was actually shown. Kept so a failure can be interviewed
    # about its inputs afterwards rather than about its reasoning -- "name the
    # ids you were given" is checkable against this; "why did you do that" is
    # a story. Never fed back into a prompt, so it does not touch replay.
    system: str = ""
    user: str = ""


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
        # `artefact.verb` below is a placeholder formatted exactly like the real
        # entries above -- same indent, same `TOOL:` prefix, because that is how
        # `fns` is built -- and two roles duly reported it in an exit interview
        # as a tool they had looked for and did not have.
        #
        # Removing it and pointing at the list instead was tried, and measured
        # across the whole of L1: 13 failures became 16. It fixed
        # `GK-answer-a-scope-inquiry`, `TS-apply-a-term` and `TS-hold-a-test`,
        # and broke `DV-build-a-clear-criterion`, `DV-challenge-a-test`,
        # `TE-survey-an-area`, `TE-amend-glossary`, `CR-pass-a-conforming-diff`
        # and `TS-fix-a-test-that-asserts-more`. A worked example earns its keep
        # somewhere other than where it misleads, so it stays until there is a
        # version that measures better -- the confusion is real and the obvious
        # fix for it is not an improvement.
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
        # Say that these have *already run*. Without it a survey session spent
        # four of its eight turns calling `code.survey` again -- the results were
        # in front of it and it re-fetched them, then ran out of budget before
        # attesting, which is what left `tick_survey` undrained on a real repo.
        body.append(
            "\nAlready run for you, with the results below. Calling any of these "
            "again returns the same thing and costs you a turn:")
        for key, value in pushed.items():
            # Through the same cap a *requested* result goes through. The push
            # was raw, so `code.survey` on icalendar's `src/icalendar` -- 1,357
            # of the repository's 1,731 grains in one area -- arrived as 198,366
            # characters, roughly 49,000 tokens against a 12,288 window. The
            # prompt was four times the context before the session took a turn,
            # Ollama cut it from the front, the brief went with it, and
            # twenty-five sessions read three things and stopped.
            #
            # The same call costs 6,086 characters when the model asks for it.
            # One rule for how much of anything a session sees, whether it asked
            # or not -- and this is the path where it matters more, because
            # nobody chose to fetch it.
            body.append(f"\n[{key}]\n{_render(value)}")
    return system, "\n".join(body)


# How much of a tool result the model is shown. This was 1200 characters, and it
# was silently the most expensive number in the system.
#
# `code.source(path, start=0, end=400)` returns four hundred *lines* and did its
# job. The result was then cut to 1200 characters before the model saw it, which
# for a Python file is the module docstring and the imports -- so an Architect
# surveying `signature.py` received a paragraph about signing requests and wrote
# a constraint paraphrasing it. It was not skimming. That paragraph was the whole
# of what arrived.
#
# Handed the actual source in a probe, the same model at the same temperature
# named the signature base string, the base string URI, RFC 2616's lowercase
# scheme and host, RFC 3986, RFC 2818's port-443 rule and RFC 2616 s5.1.2 --
# every one real, attributed and checkable, with no inventions. The ceiling was
# never the model.
#
# A cap is still needed: 12k of context does not hold an 852-line file. But it
# has to be big enough to carry an answer, and truncation has to *say so* -- a
# silent cut is indistinguishable from a short answer, and the model has no
# reason to ask for the rest of something it does not know was cut.
RESULT_CHARS = 6000

# The model writing the harness's half of the conversation.
#
# An Architect woken to constrain an external commitment produced this, and then
# reasoned from it:
#
#     TOOL: model.load(ids=['s_4976a0'])
#     OK model.load -> [{'id': 's_4976a0', 'text': 'invoices have to survive ...
#     TOOL: model.consult(grains=None)
#     OK model.consult -> []
#
# Nothing ran. It predicted what the feedback would say, believed itself, and
# carried on -- and the invented results were plausible, because it had seen the
# real ones earlier in the transcript. This is the transcript format teaching the
# model to continue it, which is a harness fault and not a judgement one: the
# reply and the results are the same kind of text in the same stream.
#
# Caught and said out loud rather than silently ignored. The parser already only
# takes `TOOL:` lines, so the fabrications never became calls -- but the session
# went on believing them, which is worse than a refused call and looked like
# nothing at all.
FABRICATED_RESULT = re.compile(r"^\s*(?:OK|ERROR)\s+[a-z_]+\.[a-z_]+\s*(?:->|:)",
                               re.MULTILINE)


def _render_cut(text: str, limit: int) -> str:
    """Cut, saying so. The same contract `_render` keeps for a tool result."""
    if len(text) <= limit:
        return text
    return (text[:limit] + f"\n... the rest of your wake ({len(text) - limit:,} "
            f"characters) did not fit the window. Ask for what you need.")


def _fit(transcript: list[str], budget: int) -> list[str]:
    """
    Keep the session inside its window, evicting the middle rather than the front.

    Raising the result cap to 6000 fixed what the model was shown in one turn and
    broke what it was shown across several. One round of an Architect's four
    survey reads is 12,947 characters; the opening prompt is another 13,500. By
    the third round the transcript passed 12,288 tokens, and an overflowing
    prompt is cut *from the front* -- which is where the brief lives. The
    instruction "you must attest before the session ends" was the first thing
    evicted, and ten of twelve areas closed while two spun for sixty sessions
    reading and never attesting.

    So the wake survives, the latest exchange survives, and what goes is the
    middle -- older tool results the session has already acted on. Announced
    rather than silently dropped, for the same reason a cut result says so.
    """
    if sum(len(t) + 2 for t in transcript) <= budget or len(transcript) < 4:
        return transcript

    # The wake is kept whole *unless it alone will not fit*, which it can be:
    # the pushed working set lives in it, and on a 1,357-grain area that was
    # 198,366 characters. Protecting it unconditionally meant the one block that
    # could overflow the window on its own was the one block never trimmed.
    if len(transcript[0]) > budget // 2:
        transcript = [_render_cut(transcript[0], budget // 2)] + transcript[1:]

    head, tail = transcript[:1], transcript[-2:]
    room = budget - sum(len(t) + 2 for t in head + tail)
    middle: list[str] = []
    for block in reversed(transcript[1:-2]):
        if room - len(block) - 2 < 0:
            break
        middle.insert(0, block)
        room -= len(block) + 2

    dropped = len(transcript) - len(head) - len(middle) - len(tail)
    if not dropped:
        return transcript
    return head + [f"[{dropped} earlier exchange(s) dropped to fit the window. "
                   f"Your instructions and your latest results are intact; "
                   f"re-read anything you still need.]"] + middle + tail


def _as_table(result: Any) -> str | None:
    """
    A list of uniform rows as a table, or None if it is not one.

    JSON repeats every field name on every row, and an index read is nothing but
    rows. `glossary.consult` spent 989 of its 4,151 characters restating "id",
    "term", "sense_short" and "provenance" twenty-three times over -- 24% of the
    payload, and 35% of `surveys.consult`. A table carries the identical
    information at 63-73% of the size.

    Strictly better than raising the cap, which is the other way to buy the same
    headroom: a cap loses information and transposing loses none. Values are kept
    whole; only the scaffolding goes.
    """
    if not isinstance(result, list) or len(result) < 2:
        return None
    if not all(isinstance(r, dict) for r in result):
        return None
    keys = list(result[0])
    if not keys or any(list(r) != keys for r in result):
        return None      # ragged rows would silently mis-align under a header

    def cell(v: Any) -> str:
        s = v if isinstance(v, str) else json.dumps(v, default=str)
        return s.replace("|", "\\|").replace("\n", " ")

    lines = [" | ".join(keys)]
    lines += [" | ".join(cell(r[k]) for k in keys) for r in result]
    return "\n".join(lines)


def _render(result: Any) -> str:
    """A tool result as the model sees it, saying plainly when it was cut."""
    text = _as_table(result) or json.dumps(result, default=str)
    if len(text) <= RESULT_CHARS:
        return text
    note = (f"... TRUNCATED after {RESULT_CHARS} of {len(text)} characters. "
            f"Ask for the next range if you need it.")
    return text[:RESULT_CHARS] + "\n" + note


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
        # Rows written before `_bind_send` refused non-string refs can still
        # carry a dict here, and resolving one killed the receiving session
        # rather than the sending one. Skipping is right even so: an id that is
        # not an id resolves to nothing, which is what the role should be told.
        if not isinstance(ref, str) or ref in resolved:
            continue
        for table, cols in (
            ("statements", "id, text, status"),
            ("items", "id, text, kind, approval"),
            ("criteria", "id, ticket_id, text"),
            # A challenge names the test and the criterion, and only the
            # criterion resolved -- so Tester was woken to defend a test it was
            # never shown, and said so when asked: "I needed to see the test
            # itself in order to decide whether it encodes its criterion, but it
            # was not provided." It owns the artefact and its own read is
            # index-depth, which is right for a listing and useless for the one
            # row somebody is disputing. The body travels because the ref is a
            # pointer to the thing, and resolving a pointer to everything except
            # the thing is what this function is for.
            ("tests", "id, criterion_id, path, body"),
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


def _group_by_shared_refs(reports: list[dict]) -> list[list[str]]:
    """
    Reports that are about the same thing, grouped by the refs they share.

    Dedupe is the only reason a round waits, and it was Liaison's judgement:
    "Terminologist will call it a term collision and Gatekeeper will call it a
    scope ambiguity when it is one question. Merge them." But the brief also
    says what makes them one question -- both point back at the same statement
    -- and that is a join, not a decision. Liaison does not make decisions.

    So the grouping arrives done. What is left for Liaison is the part that is
    genuinely its own: turning each group into words the principal can answer.

    Connected components rather than pairwise, because A-B and B-C is one
    question in three vocabularies and pairwise grouping would send two.
    """
    parent = {r["id"]: r["id"] for r in reports}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    by_ref: dict[str, str] = {}
    for r in reports:
        for ref in r["refs"]:
            if ref in by_ref:
                union(r["id"], by_ref[ref])
            else:
                by_ref[ref] = r["id"]

    groups: dict[str, list[str]] = {}
    for r in reports:
        groups.setdefault(find(r["id"]), []).append(r["id"])
    # Ordered by the first report in each, so the rendering is stable.
    order = {r["id"]: i for i, r in enumerate(reports)}
    return sorted((sorted(g, key=order.get) for g in groups.values()),
                  key=lambda g: order[g[0]])


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

    # The reports still asking for something, by the same definition the
    # predicate woke on. A settled report is a role saying it has finished, and
    # showing it here would put Liaison back in the position of deciding which
    # ones those are -- which is not its job, and was the whole of this case's
    # failure.
    from .scheduler import open_reports

    rows = open_reports(conn, thread)
    if not rows:
        return {}

    reports = []
    every_ref: list[str] = []
    for r in rows:
        refs = json.loads(r["body_refs"] or "[]")
        every_ref.extend(refs)
        reports.append({"id": r["id"], "from": r["from_role"], "refs": refs})

    out: dict[str, Any] = {"thread": thread,
                           "reports": reports,
                           "about": _group_by_shared_refs(reports)}
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
                           allow=prompts.mode_tools(wake.role, _mode_key(wake, conn)),
                           wake=wake)
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
        outcome.system, outcome.user = system, user
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

        # Every read this session has already performed, so that re-sending one
        # is not mistaken for asking a fresh question. See the hold logic below.
        #
        # Seeded with the pushed working set, because those *have* already run --
        # the prompt says so in as many words, two paragraphs up. Starting empty
        # made that sentence false: a session that re-called a pushed read paid
        # for the rows a second time, and the call counted as a fresh question,
        # which held whatever the session had actually decided to do until the
        # following turn. Liaison's round_close spent two of its turns that way
        # before sending the message it had composed on the first one.
        pushed_keys: set[str] = {sb.call_key(name) for name in pushed}
        already_run: set[str] = set()

        # Four characters to the token is the same rough measure the cockpit
        # uses. Two thirds of the window, because the system prompt is charged
        # against the same budget and the reply needs room to land.
        budget = max(2000, (pins.num_ctx * 4 * 2) // 3 - len(system))

        for iteration in range(1, max_iterations + 1):
            outcome.iterations = iteration
            transcript = _fit(transcript, budget)
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

            if FABRICATED_RESULT.search(completion.text):
                outcome.errors.append("wrote its own tool results")
                feedback.append(
                    "You wrote tool results into your own reply -- the lines "
                    "beginning `OK ...` or `ERROR ...`. Those did not come from "
                    "me and nothing behind them ran. Only results I send back "
                    "are real. Send the calls alone and stop; I will answer.")
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
                # ...and only a read it has not already had answered. A
                # Terminologist asked five `glossary.lookup`s and then sent its
                # answer, every turn, and every turn the answer was held behind
                # reads it had already been shown. It re-sent the batch intact --
                # correctly, having been told to -- and the hold fired again on
                # the same five lookups. Twelve turns, no message, 3/5 to 0/5.
                #
                # A repeated read is not a question whose answer is outstanding.
                # The boundary exists so nobody acts on something unseen, and by
                # the second time round it has been seen.
                # Seeding does two things and only one of them was wanted.
                #
                # Not holding an action behind a read the session was already
                # handed: right, and the whole point. Not *rendering* it: it
                # cost two green cases. Told "was run for you before you
                # started", `AR-constrain-an-external-commitment` emitted no
                # further calls and ended, having never written the constraint
                # it writes perfectly well when served the rows. A true sentence
                # that reads as "there is nothing here for you".
                #
                # So a pushed read is not fresh -- it cannot hold anything --
                # but it is not a repeat either, because the session has not
                # asked before. It is served.
                key = sb.call_key(call.name, call.pos, call.args)
                fresh_read = (call.name in read_fns and key not in already_run
                              and key not in pushed_keys)

                if seen_read and call.name not in read_fns:
                    held = [c.raw or getattr(c, "name", "?") for c in calls[i:]]
                    break
                seen_read = seen_read or fresh_read

                try:
                    repeat = key in already_run
                    already_run.add(key)
                    result = sb.call(call.name, *call.pos, **call.args)
                    if repeat:
                        # The stalled sessions asked `surveys.consult` three
                        # times and `glossary.consult` twice, and each copy paid
                        # full freight into a transcript that was already
                        # overflowing. The answer has not changed -- nothing the
                        # session did could have changed it -- so say so in a
                        # line rather than in four thousand characters.
                        #
                        # Known hole, left open deliberately: "the answer is
                        # above" is false once `_fit` has evicted the middle,
                        # and `_fit`'s own notice says "re-read anything you
                        # still need" -- so the two lines contradict each other
                        # and the session is sent looking for something that was
                        # deleted. Measured across 8,183 recorded prompts: 8
                        # carry the eviction notice, and all 8 carry this line
                        # too, so it is certain whenever it can happen. It is
                        # also 0.1% of prompts, and it is not what drives the
                        # repeated reads -- 1,249 prompts carry this line with
                        # nothing evicted, where the answer really is above and
                        # the session asked again regardless. Worth closing by
                        # serving the full result when anything was dropped;
                        # not worth a full re-record on its own.
                        feedback.append(
                            f"OK {call.name} -> was run for you before you "
                            f"started; the answer is in the list above."
                            if key in pushed_keys else
                            f"OK {call.name} -> unchanged since you asked "
                            f"earlier this session; the answer is above.")
                    else:
                        feedback.append(f"OK {call.name} -> {_render(result)}")
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
            # channels its job needs, so a mode that has reached everyone those
            # channels can reach has said everything it was woken to say — one
            # recipient for `ask`, three for Liaison's broadcast, and no number
            # written down anywhere.
            #
            # Recipients rather than channels, because two channels to the same
            # role are usually *alternatives* and a tool list cannot say so.
            # `round_close` offers `msg.clarify_principal` and
            # `msg.present_principal`: one asks for a ruling, the other reports
            # something worth knowing, and the brief says send one. Requiring
            # both meant the session that got it right on turn one was handed
            # eleven more turns and spent them sending the same question again
            # split in half. The broadcast still needs all three of its
            # recipients, because they are three different roles.
            #
            # A third rule was tried and reverted: woken by a message, finish
            # when you have replied to the sender. It is right for
            # Terminologist answering a question and wrong for Architect
            # handling an escalation, whose job is to route the block somewhere
            # else -- it answered the Developer, satisfied the rule, and stopped
            # before challenging the Gatekeeper, which is the whole of what the
            # case is about. 5/5 to 0/5.
            #
            # Three attempts, each fixing one case and breaking another. The
            # terminal condition is not derivable from the channel list: "who
            # this mode may talk to" does not say "what finishes this job", and
            # every rule that infers one from the other is guessing. What is
            # here is the least-wrong of the three and it is a heuristic, not a
            # law -- the iteration cap is still the real backstop.
            reachable = {f.rsplit("_", 1)[1]
                         for f in allowed if f.startswith("msg.")}
            messaged = {m["to_role"] for m in sb.ctx.outbound}
            if reachable and reachable <= messaged:
                break

            # A survey mode has no channels at all, so the rule above never fires
            # and every survey ran to the iteration cap. Attesting is what closes
            # an area -- the same shape as sending, in a mode that sends nothing
            # -- and a session that kept going past it attested a second time
            # under a second invented id. That was the top mechanism in the run:
            # "expected writes to survey_records (1), got 2", three cases.
            if any(w[0] == "survey_records" for w in sb.ctx.writes):
                break

            # No stopping rule for "this session had nothing to do", and it is
            # not for want of trying. Tried and reverted: end the session when a
            # turn repeated only reads it already held, wrote nothing and sent
            # nothing. The reasoning was sound and the measurement was not.
            #
            # It fixed nothing. Liaison's round_close -- the case it was built
            # for -- stages its message on turn one, held behind a fresh read,
            # so `outbound` is non-empty from turn two and the rule could never
            # have fired there. And it cost two cases that were green:
            # `AR-constrain-an-external-commitment` opened with `model.consult`
            # twice, which is a pushed read and therefore two dead turns, and
            # died at turn two having never reached the constraint it went on to
            # write perfectly well when given twelve.
            #
            # The distinction it needed does not exist in the signal: "nothing
            # to do" and "slow to start" produce identical turns. A session that
            # opens by re-requesting what it was handed is the normal opening,
            # not a symptom.
            #
            # The underlying gap is real and stays open: every terminal act in
            # this loop is positive -- a message, an attestation -- so the mode
            # whose right answer is silence can only express it by falling
            # quiet, and a model with eleven turns in hand does not fall quiet.
            # Whatever closes it has to be an act the role can perform, not an
            # absence the loop infers.

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
        # Hard guard: a chat reply to the principal is mutually exclusive with
        # asking the principal to ratify statements. If Liaison both chatted and
        # segmented, drop the segmentation so the conversation does not stall
        # on a confirm gate.
        if any(m.to_role == "principal" and m.verb == "converse"
               for m in result.messages):
            result.writes = [w for w in result.writes if w.table != "statements"]
            result.messages = [
                m for m in result.messages
                if not (m.to_role == "principal" and m.verb == "confirm")]
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
