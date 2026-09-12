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
import os
import re
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from . import config as config_mod
from . import sandbox as sandbox_mod
from ..design import graph as graph_mod
from ..llm import llm, toolproto, toolschema
from ..roles import api, prompts
from .db import OutboundMessage, SessionResult, Turn, Write, session_commit
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
        # Counting rows assumes a dense 1..N sequence, but sessions can leave
        # gaps: a staged message may be dropped before commit (e.g. the runner
        # guard that strips a confirm when Liaison chats). The next session
        # would then reuse an id that already exists. Use the highest numeric
        # suffix already in the table instead.
        row = conn.execute(
            f"SELECT COALESCE(MAX(CAST(SUBSTR(id, ?) AS INTEGER)), 0) AS n "
            f"FROM {table} WHERE id GLOB ?",
            (len(prefix) + 1, f"{prefix}[0-9]*"),
        ).fetchone()
        return f"{prefix}{row['n'] + offset + 1}"
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


# Law 10 -- inquiry is free. The verb an inquiry arrives on, so the session's
# mode is derived from the wake rather than chosen by whoever dispatches it.
#
# `ask` is the only one: it is drawn three times in the graph, all from Liaison
# to an artefact's owner, and it is the whole of the read-only route. `answer`
# is deliberately not here even though it is the same conversation -- a
# Developer woken by a Terminologist's answer writes code with it, so the verb
# says nothing about whether the session may write.
READONLY_VERBS = {"ask"}


def session_mode(wake: Wake) -> str:
    """
    Whether this session may write, decided by what woke it.

    Law 10 says every principal message is handled read-only first, and the law
    table says the guarantee is `sandbox.build(mode="readonly")` building no
    write functions at all. Nothing derived it: `loop.run` called `run_session`
    without a mode and took the `"normal"` default, so the only readonly
    sessions this system had ever run were in tests.

    It was not visible because the three `ask` modes narrow to reads in their
    `.tools` files anyway -- so the law held by three hand-maintained lists
    agreeing with it, which is exactly the arrangement law 10 was written to
    replace. A `.tools` file that gains a writer is a silent breach; a mode
    derived here cannot be.
    """
    if wake.kind == "message" and (wake.detail or "") in READONLY_VERBS:
        return "readonly"
    return "normal"


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
        # Same shape as `verdict` above: `reopen` means two different things
        # depending on what caused it. Vision Keeper's `challenge` mode sends
        # it once, as a revocation notice -- elect amend or restart. Its
        # `elect` mode then sends it *again*, on the same batch, to hand the
        # now-amended item back -- "so their next session starts from the
        # amended text", per that mode's own brief. Both land Developer in
        # `reopen` mode, which offers nothing but `elect_vision_keeper`, so
        # the second one relit the first one's question instead of the work
        # it was meant to unblock: elect -> reopen -> elect -> reopen, ten
        # rounds deep on one empty-project run, never once writing code. The
        # cause distinguishes them exactly as it does for `verdict`.
        if verb == "reopen" and conn is not None and wake.message_id:
            row = conn.execute(
                "SELECT c.verb AS cause_verb FROM messages m "
                "LEFT JOIN messages c ON c.id = m.cause_id WHERE m.id = ?",
                (wake.message_id,)).fetchone()
            if row and row["cause_verb"] == "elect":
                return "batch_start"
        # A principal `converse` whose cause is a `clarify` is a reply, not a
        # request. The reply goes to the owner of the rows the question was
        # about. That needs the relay tools. Offering them in `converse`
        # taught qwen3:8b to relay a plain question to the Vision Keeper 5/5
        # (G1, 2026-09-09). The cause keys the mode, as for `verdict` above.
        if (verb == "converse" and wake.role == "liaison" and conn is not None
                and wake.message_id):
            row = conn.execute(
                "SELECT c.verb AS cause_verb FROM messages m "
                "LEFT JOIN messages c ON c.id = m.cause_id WHERE m.id = ?",
                (wake.message_id,)).fetchone()
            if row and row["cause_verb"] == "clarify":
                return "answering"
            # And a reply to a confirm or a present is a ruling to read
            # (ruled 2026-09-10: the seat is text, no parser reads it).
            if row and row["cause_verb"] in ("confirm", "present"):
                return "landing"
        return verb
    if wake.kind.startswith("tick:"):
        return wake.kind.split(":", 1)[1]
    return wake.kind


def _briefs_hash(instructions: str) -> str:
    """
    A short digest of the composed brief this session was given.

    Not `prompt_hash`, which covers the whole prompt including the pushed
    working set — so it differs between two sessions that read an identical
    brief, and cannot answer the question the evaluation loop turns on: *were
    these two runs told the same thing*.
    """
    import hashlib

    if not instructions:
        return ""
    return hashlib.sha256(instructions.encode("utf-8")).hexdigest()[:16]


def build_prompt(role: str, sb: sandbox_mod.Sandbox, wake: Wake,
                 pushed: dict[str, Any], instructions: str,
                 inbound: dict[str, Any] | None = None,
                 oneshot: bool = False) -> tuple[str, str]:
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
        f"You are {role.replace('_', ' ')}. This is a single session: you are woken once, you act, "
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
        # `VK-answer-a-scope-inquiry`, `TS-apply-a-term` and `TS-hold-a-test`,
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
        + (
            # One wake, one completion (evaluated 2026-09-02, COMPLETION.md
            # 3.32; not yet ruled default): the harness truncates a oneshot
            # session after its first completion regardless of what the
            # model was told, which made the earlier measurement of this
            # shape unfair on its own terms -- the model was never told the
            # turn it was given was the only one, so it planned for a next
            # turn that the harness had already decided would not come, and
            # was truncated in the middle of a plan it was never warned to
            # finish. The prompt now says what the harness does.
            f"This is your only reply — there is no next turn to act in. "
            f"Put your whole plan here, in order: every call you have "
            f"decided on, one per line. What you do not decide now is not "
            f"decided this session; if it is still owed, whatever wakes "
            f"next picks it up, not you. Do not hold a call back because "
            f"you expect to see its answer and act on that after — there "
            f"is no after.\n"
            f"Emit no tool calls when you are done."
            if oneshot else
            f"Results come back on your next turn, never inside this one. Ask for "
            f"everything you need to know in one go — several questions cost one "
            f"turn. But once you have asked anything, stop: what you do about the "
            f"answers is next turn's work, and anything you write now was decided "
            f"without them.\n"
            f"Emit no tool calls when you are done."
        )
    )

    body = [f"You were woken by: {wake.kind}"]
    if wake.message_id:
        body.append(f"Inbound message: {wake.message_id} ({wake.detail})")
    if wake.refs:
        body.append(f"Refs: {', '.join(wake.refs)}")
        # The subject, said plainly. A define session read `Refs: @term:note`
        # and defined `@term`; the sigil is for the scheduler, not the role.
        from .scheduler import PROGRAM, is_area, term_of

        subject = wake.refs[0]
        if term_of(subject):
            body.append(f"The word: {term_of(subject)}")
        elif subject == PROGRAM:
            body.append("The subject: the whole program")
        elif is_area(subject) and wake.kind == "tick:survey":
            body.append(f"The area: {subject}")
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
            body.append(f"\n[{key}]\n{_render(value, PUSH_CHARS)}")
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
# A pushed read is the wake, not a result the session asked for, and it is
# rendered at its own cap. Measured on `cnt_14b`: `[code.area]` had been
# repacked to show an area its own files -- 13,726 characters for
# `src/intents` -- and the wake showed 5,900 of them with "TRUNCATED after 6000
# ... ask for the next range", which a push has no range to ask for. Every
# survey in the run, and every define whose concordance ran long, had been
# reading a cut working set and nobody had said so. The pushes budget
# themselves (code.area 14,000, code.front its own), so the cap here is a
# backstop a page above them; `_fit` still keeps the whole prompt in the
# window, announced.
PUSH_CHARS = 20000

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
# A sentence of intent naming a tool: "I will challenge the Tester",
# "the next step is to run code.commit". Paired with a tool name from the
# working set at the call site, so a passing mention is not an intent.
INTENT = re.compile(r"\b(?:I will|I'll|I am going to|I should|next step is to|"
                    r"let me|I need to)\b", re.IGNORECASE)

# The mandatory forks: verdicts a session claims, not answers it looks up.
CLAIMS = {"tests.triage", "brief.intake"}

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
    # Two thirds of the budget for the wake, not half: the pushed working set
    # is the part of the prompt the session was woken to read, and a source
    # push the size the area deserves is most of it.
    wake_room = (budget * 2) // 3
    if len(transcript[0]) > wake_room:
        transcript = [_render_cut(transcript[0], wake_room)] + transcript[1:]

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


def _as_block(result: Any) -> str | None:
    """
    A result carrying text, as text.

    Everything fell through to `json.dumps`, so a tool handing over source
    handed over an escaped JSON string: every newline `\n`, every
    em-dash `\u2014`, every quote `\"`. `code.area` exists to give a
    session the system "as source" -- its docstring argues the case at length
    -- and what arrived instead was, verbatim from `cnt_p`:

        {"area": "src/variables/providers", "source": "----- 
        src/variables/index.ts \u2014 imported by this area -----\n\n
        import { getVariableValues } from \"./templateVariables\";\n..."}

    `code.source` the same, under `text`. Every file every survey session has
    ever read, in every run in this repository, arrived escaped -- and `d`'s
    whole design is handing over source rather than a list of names.

    Scalars stay on a header line so nothing is lost -- `path`, `start`,
    `end`, `not_shown` are all still there and still legible -- and the long
    text is written out plainly beneath it.
    """
    if not isinstance(result, dict) or not result:
        return None
    body = {k: v for k, v in result.items()
            if isinstance(v, str) and (chr(10) in v or len(v) > 200)}
    if not body:
        return None
    head = {k: v for k, v in result.items() if k not in body}
    lines: list[str] = []
    if head:
        lines.append(", ".join(f"{k}: {v}" for k, v in head.items()))
    for k, v in body.items():
        lines.append(f"{chr(10)}[{k}]{chr(10)}{v}")
    return chr(10).join(lines)


def _render(result: Any, limit: int = RESULT_CHARS) -> str:
    """A tool result as the model sees it, saying plainly when it was cut."""
    if isinstance(result, str):
        text = result
    else:
        text = (_as_table(result) or _as_block(result)
                or json.dumps(result, default=str))
    if len(text) <= limit:
        return text
    note = (f"... TRUNCATED after {limit} of {len(text)} characters. "
            f"Ask for the next range if you need it.")
    return text[:limit] + "\n" + note


def trigger_message(conn: sqlite3.Connection, wake: Wake) -> str | None:
    """
    The message this session is replying to, which is not always a message wake.

    A rung on the `unresolved` ladder is woken by a *tick* carrying the question
    in its refs. Narrow on purpose: only a ref that resolves to a message
    counts, and every other tick carries artefact ids, so a session woken by one
    is replying to nothing and gets None.
    """
    if wake.message_id:
        return wake.message_id
    for ref in getattr(wake, "refs", ()) or ():
        if conn.execute("SELECT 1 FROM messages WHERE id = ?", (ref,)).fetchone():
            return ref
    return None


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
    # The contest's reason. A contested item wakes its owner by tick, and the
    # tick carries the item id and nothing else. The owner's brief opens with
    # "`transcript.quote` for what they actually said" -- and the owner has no
    # way to know where that is: it saw the verdict in the relay session, and
    # sessions have no memory. Measured on the tips run (2026-09-03): woken
    # cold, Vision Keeper quoted `entry_id="t1"` -- the item id, the only id
    # in front of it -- read nothing, and reported that it could not tell
    # what they objected to. Liaison asked the principal what they had
    # already said; the principal said it again; the tick fired again; the
    # same question came back verbatim. The ruling that contested the item
    # is the config verdict naming it, the latest wins, and its entry is the
    # reason. Surfaced the way a relay surfaces it, so the brief's two cases
    # -- "they said what they meant instead" and "they said no" -- can be
    # told apart by reading `principal_said`.
    if wake.kind == "tick:contested" and wake.refs:
        return _resolve_contest(conn, wake.refs[0])
    # The touch note's content (P4, 2026-09-03). A batch's predicted touch is
    # rows in `batch_touch`, which Liaison cannot read and must not judge;
    # what the seat is owed is the set read out -- expected, possible, the
    # touched ground nobody surveyed, the commitments bound to it -- and
    # mechanics compute all four. The wake names the batch; the set arrives
    # whole.
    if wake.kind == "tick:touch_note" and wake.refs:
        from .lifecycle import touch_set

        return {"touch": touch_set(conn, wake.refs[0])}
    # A tick can name a message too, and one kind does. The `unresolved`
    # ladder's rung was woken with the question in `refs` and shown nothing but
    # the id: no `principal_said`, no resolved rows, no text. Measured on the
    # click run -- Terminologist and Vision Keeper each answered with
    # `refs: ["m6"]`, the message id itself, because it was the only thing in
    # front of them. An answer naming a message names nothing the asker can
    # relay, and Liaison rightly refused to put it in front of the principal.
    trigger = trigger_message(conn, wake)
    if not trigger:
        return {}

    row = conn.execute(
        "SELECT id, from_role, to_role, verb, body_refs, body_text, round_no, "
        "cause_id FROM messages WHERE id = ?", (trigger,)).fetchone()
    if not row:
        return {}

    from .db import refs_of

    out: dict[str, Any] = {
        "from": row["from_role"], "verb": row["verb"],
        "refs": refs_of(row["body_refs"]),
    }
    # Present on one channel only, and on that one it is the whole message: the
    # Researcher shares no artefact with its asker, so the refs beside this are
    # usually empty and always insufficient.
    if row["body_text"]:
        out["asks"] = row["body_text"]

    from ..roles.principal import entry_for, verdict_for

    text = entry_for(conn, trigger)
    if text:
        out["principal_said"] = text
        # Already in the transcript, recorded mechanically. The role is told its
        # id so it can segment against it rather than re-appending it.
        recorded = conn.execute(
            "SELECT id FROM entries WHERE id = ?",
            (f"e_{trigger}",)).fetchone()
        if recorded:
            out["entry_id"] = recorded["id"]
            out["already_recorded"] = True
    ruling = verdict_for(conn, trigger)
    if ruling:
        out["principal_verdict"] = ruling

    # The ruling travels on the cause chain. A principal's verdict is keyed to
    # the message they answered (principal -> liaison), but the owner who must
    # act on it is woken by a different message: Liaison's relay, whose cause
    # is that verdict. Read by the trigger alone, the relay carries no ruling
    # and no reason, so the owner sees a draft row with no sign it was
    # contested -- and approves it. Measured on the tips run (2026-09-03): the
    # principal contested "service quality" on t1, Vision Keeper was shown t1
    # at draft and nothing else, set it approved, and the build shipped the
    # contested thing. Every owner's relay.md says the ruling is
    # `principal_verdict` in the message; this is what makes that true. One
    # hop, relay only, and only the rows this relay carries -- a ruling fans
    # out one relay per owner, and each owner sees its own.
    if row["verb"] == "relay" and not ruling and row["cause_id"]:
        carried = verdict_for(conn, row["cause_id"])
        mine = {r: v for r, v in carried.items() if r in out["refs"]}
        if mine:
            out["principal_verdict"] = mine
            reason = entry_for(conn, row["cause_id"])
            if reason:
                out.setdefault("principal_said", reason)

    resolved = _resolve_refs(conn, out["refs"])
    if resolved:
        out["resolved_refs"] = resolved
    # One name for one thing. Intake already calls the principal's words
    # `principal_said`, and an owner reached through the inquiry route is
    # holding the same words for the same reason -- so it is not a differently
    # named ref there. The briefs say "principal_said" and mean it either way.
    if "principal_said" not in out:
        said = next((r for r in resolved.values()
                     if r.get("author") == "principal" and r.get("text")), None)
        if said:
            out["principal_said"] = said["text"]
            out["entry_id"] = said["id"]

    # Sibling reports in the same thread: harvest cannot dedupe what it cannot
    # see. This is the ladder's single report now -- in-round reports are
    # harvested by `round_close` and never tip -- but a second one arriving out
    # of band is still worth showing, and `thread_id` is what keeps it to the
    # same conversation. Without that filter it pulled in every report the
    # system had ever sent.
    # The compose wake: an answer whose cause is an ask carries its round.
    # Sibling answers travel like sibling reports do, and their refs resolve
    # with the trigger's -- one session, every owner's answer, full bodies.
    # The ask's own refs resolve too, which is what puts `principal_said` in
    # front of the composer: the question is the entry the ask carries.
    if row["verb"] == "answer":
        cause = conn.execute(
            "SELECT verb, body_refs FROM messages WHERE id = "
            "(SELECT cause_id FROM messages WHERE id = ?)", (trigger,)).fetchone()
        if cause and cause["verb"] == "ask":
            extra: list[str] = refs_of(cause["body_refs"])
            siblings = [dict(r) for r in conn.execute(
                "SELECT a.id, a.from_role, a.body_refs FROM messages a "
                "JOIN messages q ON q.id = a.cause_id "
                "WHERE a.thread_id = (SELECT thread_id FROM messages WHERE id = ?) "
                "  AND a.verb = 'answer' AND q.verb = 'ask' AND a.id != ? "
                "ORDER BY a.seq", (trigger, trigger))]
            if siblings:
                out["other_answers"] = siblings
                for sib in siblings:
                    extra += refs_of(sib["body_refs"])
            more = _resolve_refs(conn, [r for r in extra
                                        if r not in out.get("resolved_refs", {})])
            if more:
                out.setdefault("resolved_refs", {}).update(more)
                if "principal_said" not in out:
                    said = next((r for r in more.values()
                                 if r.get("author") == "principal"
                                 and r.get("text")), None)
                    if said:
                        out["principal_said"] = said["text"]
                        out["entry_id"] = said["id"]

    if row["verb"] == "report":
        siblings = [dict(r) for r in conn.execute(
            "SELECT id, from_role, body_refs FROM messages "
            "WHERE verb = 'report' AND thread_id = ("
            "  SELECT thread_id FROM messages WHERE id = ?) "
            "  AND id != ? ORDER BY seq", (trigger, trigger))]
        if siblings:
            out["other_reports"] = siblings

        # What the principal has already said about these rows. A report
        # about a row the principal answered once is not a new question. On
        # the tipsG walk (2026-09-09) the Terminologist reported one collision
        # eight times, each report became a clarify, and the principal
        # answered the same thing eight times. The answers were on file. The
        # harvest could not see them. Each is the clarify's words and the
        # principal's reply, for the rows this report names.
        from ..roles.principal import entry_for
        refs_here = set(out["refs"])
        prior = []
        for c in conn.execute(
                "SELECT id, body_text, body_refs FROM messages "
                "WHERE verb = 'clarify' AND to_role = 'principal' ORDER BY seq"):
            if not refs_here & set(json.loads(c["body_refs"] or "[]")):
                continue
            reply = conn.execute(
                "SELECT id FROM messages WHERE from_role = 'principal' "
                "AND cause_id = ? ORDER BY seq DESC LIMIT 1", (c["id"],)).fetchone()
            if not reply:
                continue
            said = entry_for(conn, reply["id"])
            if said:
                prior.append({"question": c["body_text"], "principal_said": said,
                              "about": json.loads(c["body_refs"] or "[]")})
        if prior:
            out["prior_answers"] = prior

    # Chat memory: a Liaison intake session sees the recent back-and-forth so
    # greetings and follow-ups are answered in context. This is the one place
    # where a role is deliberately given history; the no-memory rule still
    # holds for every other mode.
    if row["to_role"] == "liaison" and row["verb"] == "converse":
        out["recent_chat"] = _recent_chat(conn, trigger)

        # An answer is an answer to something. A principal `converse` whose
        # cause is a clarify is a reply, not new work. A desk could not settle
        # something, and that desk still waits. Liaison saw the words and
        # nothing else, so it segmented them as a fresh request. Measured as
        # the principal (tips5, 2026-09-04): the Tester asked, the principal
        # answered in one sentence, the answer came back as three statements
        # to confirm, and the Tester asked again in other words. The chain
        # holds the context: answer, clarify, the ask that caused the clarify.
        # Nothing read it. This surfaces who asked, what, and about which rows.
        if row["cause_id"]:
            clarify = conn.execute(
                "SELECT id, verb, body_text, body_refs, cause_id FROM messages "
                "WHERE id = ?", (row["cause_id"],)).fetchone()
            if clarify and clarify["verb"] == "clarify":
                answering: dict[str, Any] = {"question": clarify["body_text"]}
                asker = conn.execute(
                    "SELECT from_role, body_refs FROM messages WHERE id = ?",
                    (clarify["cause_id"],)).fetchone() if clarify["cause_id"] else None
                if asker:
                    answering["asked_by"] = asker["from_role"]
                    answering["about"] = json.loads(asker["body_refs"] or "[]")
                else:
                    # Liaison's own question, with no desk behind it. The rows
                    # the clarify named are what the reply is about, and their
                    # owner is who acts on it. Measured (tipsF, 2026-09-08):
                    # two such clarifies carried nothing here, the brief had
                    # no row to route to, and both replies re-entered as
                    # fresh requests to confirm.
                    answering["asked_by"] = "liaison"
                    answering["about"] = (json.loads(clarify["body_refs"] or "[]")
                                          or json.loads(row["body_refs"] or "[]"))
                # The owner of a row is a fact about its table, and a bare id
                # says nothing about its table. Measured on the register
                # (2026-09-09): shown `about: ["c_ec730c"]` and a list that
                # named the Vision Keeper first, llama3.1:8b relayed a
                # criterion to the Vision Keeper 5/5. The rows travel with
                # their table, and the brief keys the owner on it.
                about_rows = _resolve_refs(conn, answering["about"])
                for ref, resolved_row in about_rows.items():
                    resolved_row["table"] = _table_of(conn, ref)
                answering["about_rows"] = about_rows
                out["answering"] = answering
            # A reply to a page. The Liaison reads the words against the
            # page and records the ruling. It needs the page as the person
            # saw it, the numbered lines in order, the words, and what was
            # said back and forth on this page before.
            if clarify and clarify["verb"] in ("confirm", "present"):
                from ..roles.principal import render_page

                page_refs = json.loads(clarify["body_refs"] or "[]")
                page, order = render_page(conn, clarify["verb"], page_refs,
                                          clarify["body_text"])
                landing: dict[str, Any] = {
                    "page_kind": clarify["verb"], "page": page,
                    "lines": {str(i + 1): ref for i, ref in enumerate(order)},
                    "reply": row["body_text"] or "",
                }
                line_rows = _resolve_refs(conn, order)
                for ref, resolved_row in line_rows.items():
                    resolved_row["table"] = _table_of(conn, ref)
                landing["line_rows"] = line_rows
                earlier = [dict(r) for r in conn.execute(
                    "SELECT from_role, body_text FROM messages "
                    "WHERE cause_id = ? AND verb = 'converse' AND id != ? "
                    "AND body_text IS NOT NULL ORDER BY seq",
                    (clarify["id"], row["id"]))]
                if earlier:
                    landing["earlier_exchange"] = earlier
                out["landing"] = landing
                # The words live in `landing.reply`, once. Beside a field
                # named `asks`, both 8B models answered the "question" by
                # sending the words back (2026-09-10, 5/5).
                out.pop("asks", None)

    # Signoff disclosure (ruled 2026-09-03): the principal gates what an item
    # says and cannot gate what is absent, so the absence is computed here and
    # handed to the presenter. A ratified statement no item reflects is a
    # dropped want vanishing through slicing with no trace -- the one gap the
    # signoff reader cannot see from the items alone. Mechanics locate it;
    # the present carries it; the principal rules on it.
    if row["to_role"] == "liaison" and row["verb"] == "submit":
        uncovered = [dict(r) for r in conn.execute(
            "SELECT id, text FROM statements WHERE status = 'ratified' "
            "AND id NOT IN (SELECT statement_id FROM item_statements) "
            "ORDER BY id")]
        if uncovered:
            out["uncovered_statements"] = uncovered

    return out


def _resolve_contest(conn: sqlite3.Connection, item: str) -> dict[str, Any]:
    """
    The ruling that contested `item`, and the principal's reason for it.

    A verdict is a config row `verdict:<message id>` holding a map of row id
    to approve, contest or revise, keyed to the principal's message. An item
    can be contested more than once -- amended, re-presented, contested again
    -- so the latest by that message's seq is the one that stands. Nothing
    contested it: nothing to say, and the owner is woken with the item alone,
    as before.
    """
    from ..roles.principal import entry_for

    rows = conn.execute(
        "SELECT c.key, c.value FROM config c JOIN messages m "
        "ON m.id = substr(c.key, 9) WHERE c.key LIKE 'verdict:%' "
        "ORDER BY m.seq DESC").fetchall()
    for r in rows:
        ruling = json.loads(r["value"] or "{}")
        if ruling.get(item) != "contest":
            continue
        mid = r["key"][len("verdict:"):]
        out: dict[str, Any] = {"refs": [item],
                               "principal_verdict": {item: "contest"}}
        reason = entry_for(conn, mid)
        if reason:
            out["principal_said"] = reason
            recorded = conn.execute(
                "SELECT id FROM entries WHERE id = ?", (f"e_{mid}",)).fetchone()
            if recorded:
                out["entry_id"] = recorded["id"]
        resolved = _resolve_refs(conn, [item])
        if resolved:
            out["resolved_refs"] = resolved
        return out
    return {}


def _recent_chat(conn: sqlite3.Connection, current_msg_id: str,
                 limit: int = 8) -> list[dict[str, str]]:
    """Recent principal/liaison converse turns, newest last, excluding the wake."""
    # Questions count as turns. This selected `converse` alone, so Liaison
    # could not see what it had already asked. A role with no memory, shown
    # the answer but not the question, cannot tell the ground has moved.
    # `interrupt_cap` says never repeat and always reframe. That needs the
    # last question in view.
    rows = conn.execute(
        "SELECT from_role, verb, body_text FROM messages "
        "WHERE verb IN ('converse', 'clarify') "
        "  AND from_role IN ('principal', 'liaison') "
        "  AND to_role IN ('principal', 'liaison') "
        "  AND body_text IS NOT NULL AND body_text != '' "
        "  AND id != ? "
        "ORDER BY seq DESC LIMIT ?",
        (current_msg_id, limit)
    ).fetchall()
    return [{"from": r["from_role"], "text": r["body_text"] or ""}
            | ({"asked": True} if r["verb"] == "clarify" else {})
            for r in reversed(rows)]


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
            # Bodies, for the same reason `tests` above carries one: the ref
            # is a pointer to the thing, and resolving a pointer to everything
            # except the thing is what this function is for.
            #
            # These two are the artefacts the inquiry route runs on, and they
            # were the two resolving to a summary. The owner reads the full
            # sense, refs the term, and Liaison -- which writes the words the
            # principal actually reads -- was handed one line. Measured on the
            # eight maintainer questions: the owners consulted properly and the
            # replies came out as strings of one-line definitions, because that
            # is all that survived the hop.
            ("constraints", "id, headline, text"),
            ("glossary_terms", "id, term, sense_short, sense_body"),
            ("ledger", "id, about_ref, default_taken"),
            # The transcript, and it is the whole of the inquiry route.
            #
            # An `ask` carries refs and no words, so the entry id *is* the
            # question -- and this list had no `entries` row, so it resolved to
            # nothing and the owner was woken with a ref it could not follow.
            # Measured on a live run against the click database: Architect saw
            # `refs: ["e_m5"]`, no question, and answered with a description of
            # a three-layer architecture that click does not have. Answering
            # from memory is what a role does when handed nothing, and it is
            # indistinguishable afterwards from answering from the artefact.
            #
            # Entries were reachable before only through `entry_for`, which
            # looks up `e_{waking message id}` -- true on the intake hop, where
            # Liaison is woken by the very message the entry belongs to, and
            # false on every hop after it.
            ("entries", "id, author, text"),
        ):
            hit = conn.execute(
                f"SELECT {cols} FROM {table} WHERE id = ?", (ref,)).fetchone()
            if hit:
                resolved[ref] = dict(hit)
                # A disputed test travels with its last run. S0 walk eight:
                # the Developer challenged, the Tester held -- "the test
                # checks the greeting is displayed" -- nine rounds, while
                # the harness output said OSError: reading from stdin. The
                # Tester never saw it; a test's run is the one fact about
                # it that is not its own words, and the dispute is about
                # exactly that.
                if table == "tests":
                    run = conn.execute(
                        "SELECT result, output FROM test_runs WHERE test_id = ? "
                        "ORDER BY rowid DESC LIMIT 1", (ref,)).fetchone()
                    if run:
                        out = run["output"] or ""
                        resolved[ref]["last_run"] = {
                            "result": run["result"],
                            "output_tail": out[-700:] if out else ""}
                break
    return resolved


_REF_TABLES = ("statements", "items", "criteria", "tests", "tickets",
               "constraints", "glossary_terms", "ledger", "entries")


def _table_of(conn: sqlite3.Connection, ref: str) -> str | None:
    """The table a ref resolves in, or None. Same tables as `_resolve_refs`."""
    for table in _REF_TABLES:
        if conn.execute(f"SELECT 1 FROM {table} WHERE id = ?", (ref,)).fetchone():
            return table
    return None


def _group_by_shared_refs(reports: list[dict]) -> list[list[str]]:
    """
    Reports that are about the same thing, grouped by the refs they share.

    Dedupe is the only reason a round waits, and it was Liaison's judgement:
    "Terminologist will call it a term collision and Vision Keeper will call it a
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

    from .db import refs_of

    reports = []
    every_ref: list[str] = []
    for r in rows:
        refs = refs_of(r["body_refs"])
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
                     g: graph_mod.Graph | None = None,
                     asked: str = "") -> dict[str, Any]:
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

    # One read needs an argument the *wake* already knows, and leaving it to
    # the model cost the whole inquiry route.
    #
    # `glossary.lookup` takes a term. Callable-with-no-arguments invoked it with
    # none, which returns the miss for the empty string, and the session then
    # had the index of short senses and no full sense of anything. Measured on
    # the eight maintainer questions: `probes/consult.py` pushes exactly this --
    # "the index of short senses whole, and full bodies only for the terms the
    # question's words name -- `glossary.lookup`, mechanically" -- and scored
    # 4 of 8 where the wired route scored none.
    #
    # It is the same rule as `area` for a survey: the subject is the wake's, not
    # the role's, so the system supplies it rather than asking a cold session to
    # think of it.
    # Both, not just the lookup: the terms are enumerated from the index,
    # and a mode can hold one without the other. Architect's `unresolved`
    # has `glossary.lookup` and no `glossary.consult`, so an unguarded
    # enumeration killed the session outright -- `NotInWorkingSet` is
    # raised, not returned, and the push runs before the model sees
    # anything. 0/5 on a case that had been green.
    have = set(sb.functions())
    if asked and {"glossary.lookup", "glossary.consult"} <= have:
        bodies = {}
        for term in _terms_named_in(sb, asked):
            try:
                bodies[term] = sb.call("glossary.lookup", term=term)
            except Exception:                              # noqa: BLE001
                continue
        if bodies:
            pushed["glossary.lookup"] = bodies

    # The same rule pointed at the code index. Criteria carry `surface_refs`,
    # and demanding a callable's name from a session that has never seen the
    # code is the guard-without-an-exit shape again -- so the candidates are
    # supplied. The hint is the wake's subject: this item's ticket headlines
    # for a criteria pass, the asker's note joined in for a repair. Matching
    # is `code.surface`'s business; choosing the subject is never the role's.
    if "code.callables" in have:
        hint = asked
        if wake is not None and wake.kind == "tick:criteria" and wake.refs:
            try:
                rows = sb.call("tickets.scan", item_id=wake.refs[0]) or []
                hint += " " + " ".join(
                    r.get("headline", "") for r in rows if isinstance(r, dict))
            except Exception:                              # noqa: BLE001
                pass
        try:
            pushed["code.callables"] = sb.call("code.callables", hint=hint)
        except Exception:                                  # noqa: BLE001
            pass

    # The same rule pointed at the decision record. `decisions.search` was
    # the single largest gap in the one-wake-one-completion conversion map
    # (COMPLETION.md 3.32, 12 of 51 blocked-on-a-read cases) -- eighteen
    # modes across five roles carry the tool, every one of them told to
    # search before writing ("check the decision record", "before
    # asserting, search"), and a cold session has no habit of searching
    # any more than it has a habit of fetching. `query` is a LIKE match, so
    # pushing the whole sentence would match nothing; pushed instead is one
    # search per distinctive word of the wake's subject, capped so a long
    # sentence does not become a dozen calls' worth of prompt.
    if asked and "decisions.search" in have:
        hits: dict[str, Any] = {}
        for word in _subject_words(asked)[:6]:
            try:
                rows = sb.call("decisions.search", query=word)
            except Exception:                              # noqa: BLE001
                continue
            if rows:
                hits[word] = rows
        if hits:
            pushed["decisions.search"] = hits
    return pushed


_DECISION_STOP = frozenset("""
    the a an and or but for from with without into onto upon this that
    these those what which who when where how why please build show
    asks user users about your you their them then also just
""".split())


def _subject_words(text: str) -> list[str]:
    """Distinctive standalone words of a wake's subject, for a LIKE search.

    Lighter than `_terms_named_in`: that one matches against the glossary's
    own vocabulary and returns terms, not raw words. This has no index to
    match against -- the decision record is prose, not a term list -- so it
    is just the words worth searching one at a time: not grammatical
    scaffolding, not the handful of words every principal message carries
    regardless of subject ("please", "build", "show").
    """
    seen: list[str] = []
    for w in re.findall(r"[A-Za-z]+", text.lower()):
        if len(w) > 2 and w not in _DECISION_STOP and w not in seen:
            seen.append(w)
    return seen


def _terms_named_in(sb: sandbox_mod.Sandbox, asked: str) -> list[str]:
    """
    The glossary terms whose words appear in the question.

    Mechanical, and deliberately generous about word shape: the question says
    "recipes" and the glossary says "recipe", the question says "template
    variable" and the term is `TemplateVariable`. Matching on the term's own
    tokens rather than the phrase means a multi-word term is found by any of
    its words, which is the direction to err in -- a body pushed and not needed
    costs characters, and a body missing costs the answer.
    """
    words = set()
    for w in asked.split():
        w = w.strip("`'\".,?:;()[]").lower()
        if len(w) >= 3:
            words.add(w)
            words.add(w.rstrip("s"))
            words.update(p for p in w.replace("_", " ").split() if len(p) >= 3)

    found = []
    for row in sb.call("glossary.consult") or []:
        term = (row.get("term") if isinstance(row, dict) else None) or ""
        tokens = {term.lower()}
        tokens.update(t for t in term.lower().replace("_", " ").split())
        tokens.update(t.rstrip("s") for t in set(tokens))
        # CamelCase, which is most of a TypeScript glossary: the question
        # says "template variable" and the term is `TemplateVariable`.
        split = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", term)
        tokens.update(re.findall(r"[a-z]+", split.lower()))
        tokens.update(t.rstrip("s") for t in set(tokens))
        if tokens & words:
            found.append(term)
    return found


def run_session(
    conn: sqlite3.Connection,
    wake: Wake,
    *,
    backend: llm.Backend | None = None,
    pins: llm.Pins | None = None,
    instructions: str = "",
    mode: str | None = None,
    batch_id: str | None = None,
    area: str | None = None,
    max_iterations: int = MAX_ITERATIONS,
    native_tools: bool | None = None,
    g: graph_mod.Graph | None = None,
    on_completion: Any | None = None,
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
    # Passed only by tests that are testing the mode itself; every real caller
    # leaves it to the wake.
    mode = mode or session_mode(wake)
    routed = config_mod.routed_model(
        config_mod.get(conn, "model_routing"), wake.kind, wake.role)
    if routed:
        pins = llm.Pins(routed, pins.temperature, pins.num_ctx)

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
    from .scheduler import ONBOARDING_TICKS

    provenance = "observed" if wake.kind in ONBOARDING_TICKS else "decided"

    sb = sandbox_mod.build(wake.role, conn, mode=mode, batch_id=batch_id,
                           session_id=session_id, entry_id=entry_id,
                           provenance=provenance, g=g,
                           # The subject the scheduler decided: an area for a
                           # survey, `@program` for the orientation, `@term:x`
                           # for a word. Never the role's to choose.
                           area=area or (wake.refs[0]
                                 if wake.kind in ONBOARDING_TICKS and wake.refs else None),
                           allow=prompts.mode_tools(wake.role, _mode_key(wake, conn)),
                           wake=wake)
    sb._order = prompts.mode_order(wake.role, _mode_key(wake, conn)) or []
    # What this session is replying to, which is not always a message wake.
    #
    # A rung on the `unresolved` ladder is woken by a *tick* carrying the
    # question in its refs, so `message_id` is None and everything the session
    # sent came out with no cause. The chain then breaks exactly where it is
    # needed: `schedule.reask` finds the answer by its cause and refuses --
    # "the message that woke you is not a reply to a question you asked" -- so
    # the asker cannot say the second answer missed either, and the ladder
    # loops on one rung until quarantine. Measured on the click run, twice.
    #
    # Narrow on purpose: only a ref that actually resolves to a message counts.
    # Every other tick carries artefact ids in `refs` and is unaffected.
    sb.ctx.trigger = trigger_message(conn, wake)

    claim(conn, wake.role, session_id, wake.message_id)
    if wake.message_id:
        conn.execute("UPDATE messages SET attempts = attempts + 1 WHERE id = ?",
                     (wake.message_id,))

    outcome = RunOutcome(session_id=session_id, committed=False, iterations=0)

    try:
        # The one-wake-one-completion experiment (2026-09-02, unruled): the
        # model's first reply is its whole plan; execute it in order and end.
        # No holds -- there is no next turn to revise in -- and no nudges.
        # Behind an env flag so the register can measure the shape against
        # the default without touching it. Computed before the prompt is
        # built, not after: the earlier measurement of this shape truncated
        # the session without ever telling the model its turn was the only
        # one, which is not a fair test of a model told to plan for it.
        oneshot = bool(os.environ.get("ROTA_ONESHOT"))
        inbound = resolve_inbound(conn, wake)
        pushed = push_working_set(
            wake.role, sb, wake, g,
            asked=inbound.get("principal_said") or inbound.get("asks") or "")
        system, user = build_prompt(wake.role, sb, wake, pushed, instructions,
                                    inbound, oneshot=oneshot)
        outcome.system, outcome.user = system, user
        pins = pins.with_prompt(system + user)

        transcript = [user]
        held_calls: list = []
        fence_warned = False
        intent_warned = False
        noop_warned = False
        stoodby_retried = False
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
        # Text protocol unless a run asks for native tools. The default used
        # to be "native when the model supports it", and the schemas were
        # computed and never handed to the backend, so every run has in
        # fact spoken the text protocol; handing them over under that
        # default would have switched the protocol on every capable model
        # at once. Opt in per run, and the schemas travel (2026-09-09).
        use_native = bool(native_tools)
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
        # Both spellings of the same call. A pushed read is registered by its
        # no-argument key, because that is how `push_working_set` invoked it --
        # and the signature the model is shown says `code.area(area=None)`, so
        # the model writes `code.area(area='src/intents')`. Same result, `area`
        # defaults to `ctx.area`, different key. The explicit form therefore
        # counted as a *fresh* read and held everything the session wrote after
        # it, in the same reply.
        #
        # Measured: every session in one run made both calls, and what the hold
        # took was the work -- `glossary.amend(term="intent", sense_body="a type
        # of frontmatter in Obsidian notes that defines a template or action")`,
        # the best definition six runs had produced, held and never re-sent.
        # Seventeen blocks across the run, each one the turn's entire output.
        #
        # The hold is right and this is not the case it exists for: the answer
        # is not outstanding, it is already in the prompt, and the session is
        # being punished for naming the argument the signature advertises.
        pushed_keys: set[str] = set()
        for name in pushed:
            pushed_keys.add(sb.call_key(name))
            if sb.ctx.area:
                pushed_keys.add(sb.call_key(name, (), {"area": sb.ctx.area}))
                pushed_keys.add(sb.call_key(name, (sb.ctx.area,), {}))
        already_run: set[str] = set()
        turns: list[Turn] = []

        # Four characters to the token is the same rough measure the cockpit
        # uses. Two thirds of the window, because the system prompt is charged
        # against the same budget and the reply needs room to land.
        budget = max(2000, (pins.num_ctx * 4 * 2) // 3 - len(system))

        for iteration in range(1, max_iterations + 1):
            outcome.iterations = iteration
            transcript = _fit(transcript, budget)
            user = "\n\n".join(transcript)
            _started = time.perf_counter()
            completion = backend.complete(system, user, pins, tools=schemas)
            outcome.completions.append(completion.text)
            # The exact context and the exact response, kept. Everything else
            # about a session is recoverable from its rows; this is not, and it
            # is what every session that behaved oddly has turned out to need.
            turns.append(Turn(iteration, system, user, completion.text,
                              int((time.perf_counter() - _started) * 1000)))
            # The single-step hook. Called for every completion, whether or
            # not it carried a tool call — the seat's pause is "one model
            # turn", not "one dispatched call". A blocking callback here holds
            # the session mid-flight (nothing is committed yet, so nothing is
            # observable until the ordinary atomic commit at the end), which
            # is why the caller owns the decision to block at all.
            if on_completion:
                on_completion()
            if getattr(completion, "truncated", False):
                outcome.errors.append(
                    f"prompt did not fit: {completion.prompt_tokens} tokens "
                    f"evaluated against a {pins.num_ctx} window — the session "
                    f"was briefed with less than it was given")

            calls = toolproto.extract_lenient(completion.text, allowed,
                                              signatures=_param_sets(sb))
            if (completion.raw or {}).get("done_reason") == "length":
                # clickI night 16 (2026-09-12): a 688-line whole-file write
                # stopped at the output cap mid-string, the parser called it
                # an unbalanced quote, and the Developer then read the file
                # as already changed. The cap is a fact the model cannot see.
                cut = ("your reply was cut at the output budget before it "
                       "ended, so the last call did not run and nothing was "
                       "written. Send less in one reply: for a long file, "
                       "write the span you changed with start and end copied "
                       "from code.source, not the whole file")
                outcome.errors.append(cut)
                feedback.append(f"ERROR reply cut: {cut}")
            if ("```" in completion.text and not calls
                    and "code.write" in allowed and not fence_warned):
                # Walk ten: the Developer's fix, whole and correct, inside a
                # fence in its reply -- and nothing landed, because a reply
                # is not a file. Once: told, and the next fenced reply is
                # the session's real stop.
                fence_warned = True
                outcome.errors.append("wrote code into its reply")
                transcript.append(completion.text)
                transcript.append(
                    "You wrote code into your reply, and a reply is not a "
                    "file -- nothing landed. Send it as a call: "
                    "code.write(path='...', text='...') and then code.commit.")
                continue
            if (not calls and not intent_warned and INTENT.search(completion.text)
                    and (any(name in completion.text for name in allowed)
                         or not (sb.ctx.writes or getattr(sb.ctx, "outbound", [])))):
                # Walks fourteen and fifteen: "I will address these issues by
                # implementing the required functions" -- no tool named, no
                # write staged, nothing sent, three sessions running. A
                # session that has done nothing and announces it will is the
                # same silence.
                # Walk thirteen: "I will challenge the Tester to verify..."
                # and the session ended -- twice, three sessions to the
                # quarantine, nothing sent. A named tool in a sentence of
                # intent is a call the model owes; told once, and the next
                # prose turn is the real stop.
                intent_warned = True
                outcome.errors.append("named an act and did not perform it")
                transcript.append(completion.text)
                transcript.append(
                    "You said what you would do and did not do it -- a reply "
                    "is not a call. Send the call you named, as TOOL: ..., "
                    "or end by saying nothing is owed.")
                continue
            if (not calls and not noop_warned and not held_calls
                    and wake.kind.startswith("tick:")
                    and not (sb.ctx.writes or getattr(sb.ctx, "outbound", []))):
                # Walk sixteen: the two-line check answered "No, the test is
                # wrong" and the session ended -- no fix, no challenge, no
                # escalation, two sessions to quarantine. A tick exists
                # because state is owed; a session that touches nothing
                # leaves the tick to fire again with the same material.
                # Told once; the next prose turn is the real stop.
                noop_warned = True
                outcome.errors.append("ended a tick with nothing done")
                transcript.append(completion.text)
                transcript.append(
                    "You were woken because something is owed here, and this "
                    "session has written nothing and sent nothing -- the same "
                    "wake will fire again with the same material. Act on your "
                    "conclusion with a call: fix it, dispute it with the "
                    "evidence quoted, or escalate it. If truly nothing is "
                    "owed, say so and stop.")
                continue
            if not calls:
                # A session ending with held calls never superseded is the
                # model standing by them. The hold exists so an act can be
                # revised once the reads' answers are in view; a model that
                # reads the answers and ends without revising has said the
                # plan stands -- measured the other way on S0 walk seven,
                # where four valid encodes were held, qwen declared "I have
                # encoded tests for all four criteria", the session ended
                # clean, and the work silently never happened.
                refused = []
                for hc in held_calls:
                    try:
                        sb.call(hc.name, *hc.pos, **hc.args)
                    except Exception as exc:           # noqa: BLE001
                        outcome.errors.append(f"{hc.name} (held): {exc}")
                        refused.append(f"ERROR {hc.name}: {exc}")
                if refused and not stoodby_retried:
                    # Walk twenty-one: seven encodes held behind seven
                    # triage reads, the model declared them done, the
                    # stood-by execution refused every one, and the session
                    # was over before the refusals could be read. A refusal
                    # is the door's half of a conversation; once, the model
                    # gets to answer it.
                    stoodby_retried = True
                    held_calls = []
                    transcript.append(completion.text)
                    transcript.append(
                        "The calls you stood by ran, and these were "
                        "refused:\n" + "\n".join(refused)
                        + "\nAnswer the refusals with corrected calls, "
                        "or end.")
                    continue
                break

            # A turn identical to the one before it is the session saying it
            # has nothing more to say. At temperature zero the model is a
            # function of its prompt, and the prompt has only grown by "the
            # answer is above"; the next completion will be this one again.
            # Measured: a 14B survey session wrote two terms, never attested,
            # and re-sent the byte-identical batch eleven times at forty
            # seconds each. The attempt bound still governs what the unfinished
            # work costs; this only stops paying for it twelve times a session.
            # Twice: the first repeat is answered ("unchanged since you asked")
            # and the model gets to read that; a third identical turn after it
            # is the fixed point.
            if (len(turns) >= 3
                    and turns[-1].completion.strip() == turns[-2].completion.strip()
                    == turns[-3].completion.strip()):
                outcome.errors.append("repeated its previous turn verbatim twice; ended")
                break

            feedback = []
            held = []
            # Any tool call this turn supersedes last turn's held tail -- the
            # model revised, and its new calls are its will. Cleared here,
            # before this turn's calls run.
            held_calls = []
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
                # Nor is any spelling of a read that was pushed. The `area`
                # variants above were the first instance; the define phase
                # produced the second in its first session, with
                # `code.concordance(term='template', limit=3)` restating the
                # subject the wake had already pushed, and the amend behind it
                # held for three turns. A pushed read's subject is fixed by the
                # wake, so a call naming it asks nothing outstanding -- and a
                # call naming something else still runs and is served; it just
                # cannot hold the work the session has already decided on.
                # A branch claim is not a lookup. `tests.triage` and
                # `brief.intake` are graph reads, and holding the act
                # behind them cost walk twenty-one every test: seven
                # triages, seven encodes held, a prose turn, and the
                # refusals arrived after the session could answer.
                fresh_read = (call.name in read_fns and key not in already_run
                              and key not in pushed_keys
                              and call.name not in pushed
                              and call.name not in CLAIMS)

                # The terminal act is never held. Attesting closes the subject
                # and ends the session, and its evidence check already refuses
                # a citation of anything the session did not open -- so a read
                # ahead of it in the same batch runs first and the attest can
                # only cite what that read opened. Held, it was the call that
                # never ran: a survey session re-sent its reads and its attest
                # every turn, each turn's reads were fresh, and the attest sat
                # behind them for twelve turns until the area was abandoned.
                if (not oneshot and seen_read and call.name not in read_fns
                        and call.name != "surveys.attest"):
                    held = [c.raw or getattr(c, "name", "?") for c in calls[i:]]
                    held_calls = list(calls[i:])
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

            # One wake, one completion: once the reply has committed to
            # something -- a write, a message, a terminal act -- that is the
            # model's whole plan, executed in order, and the session ends; no
            # later turn revises it. A turn that only read is not a plan yet.
            # Measured live (S0 walk, 2026-09-03): the unconditional break
            # ended a session after a single `model.load` with nothing else
            # attempted -- the architect never saw the result, wrote nothing,
            # and no predicate re-woke it. The walk went quiet at step 4, 0
            # statements.
            #
            # "Decided something" is `ctx.writes` or `ctx.outbound` being
            # non-empty -- the same boundary the rest of this runner and
            # every op in `roles/api.py` already builds on, not a
            # rebuilt-from-call-names guess. A call-name heuristic
            # (`not in read_fns`) needed two hand-carved exceptions inside a
            # single hour: `code.commit` on an unchanged tree returns
            # `{"committed": False}` instead of raising, and `code.write`
            # is explicitly documented as outside the transaction ("the
            # filesystem is outside the transaction") -- a session that
            # diagnosed a real pytest failure correctly and wrote a fully
            # correct fix ended on the write alone, before `code.commit`,
            # and the fix was discarded uncommitted. `ctx.writes`/
            # `ctx.outbound` already get this right without special-casing:
            # every real op appends to `ctx.writes` on success, no read
            # does, and `code.write`/a no-op `code.commit` don't either --
            # by the same design that keeps `verdicts.claim_encodes` (a
            # staged judgement, not yet a verdict) off it too.
            if oneshot and (sb.ctx.writes or sb.ctx.outbound):
                break

            # A role that has sent its outbound message has, in almost every
            # mode, finished. Without saying so the model keeps going and starts
            # inventing work — an Liaison intake session will happily fabricate
            # a second principal entry, which is the one thing it must never do.
            # Everywhere, build modes included. Scoping this away from
            # them (walk twenty-two) sent DV-challenge-a-test from 5/5 to
            # 0/5 on the register: told nothing after its correct
            # challenge, the Developer went on to write code against the
            # very test it had put in dispute. A challenge sent is the
            # session's last word on that test.
            if sb.ctx.outbound:
                feedback.append(
                    "You have sent your message. Your work for this session is "
                    "complete — emit no further tool calls."
                )
            transcript.append("\n".join(feedback))

            # Liaison's intake mode is documented as one answer per message --
            # chat, an inquiry, or work, never two -- so once it has actually
            # sent that answer, asking the model again can only solicit a
            # second one. Scoped to this one role+mode: an unscoped version of
            # this check broke Architect's escalation routing, which
            # legitimately sends two messages (report, then challenge) in one
            # session. See rota-loop-termination-fix memory for the two
            # earlier attempts this replaced.
            if (wake.role == "liaison"
                    and _mode_key(wake, conn) in ("converse", "answering", "landing")
                    and sb.ctx.outbound):
                break
            # The same fact for a ruling: once the reply is read, the
            # session's job is done. Given a second turn, qwen3:8b read the
            # reply correctly and then echoed it back to the principal as a
            # converse, 5/5 on both contest cases (2026-09-10).
            if (wake.role == "liaison" and _mode_key(wake, conn) == "landing"
                    and any(w[0] == "rulings" for w in (sb.ctx.writes or []))):
                break

            # And when saying so is not enough, stop.
            #
            # Asking nicely held for most modes and not for the ones that matter:
            # Vision Keeper answering a scope inquiry sent `answer` three times with
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
            # before challenging the Vision Keeper, which is the whole of what the
            # case is about. 5/5 to 0/5.
            #
            # Three attempts, each fixing one case and breaking another. The
            # terminal condition is not derivable from the channel list: "who
            # this mode may talk to" does not say "what finishes this job", and
            # every rule that infers one from the other is guessing. What is
            # here is the least-wrong of the three and it is a heuristic, not a
            # law -- the iteration cap is still the real backstop.
            reachable = {_recipient_of(f, g) for f in allowed if f.startswith("msg.")}
            reachable.discard("")
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

            # A frame session ends when the tree is classified. The attest
            # would be better -- and at both model sizes the judge assigned
            # everything and never made it: llama 0/5 recording, qwen twice
            # live, each re-sending the batch until the identical-turn rule
            # fired. The record already follows the writes everywhere else,
            # so here it is derived at the end of the turn that judged.
            if wake.kind == "tick:frame" and any(
                    w[0] == "frame_rulings" for w in sb.ctx.writes):
                _derive_frame_record(conn, sb)
                break

            # A challenge session ends on its verdict, the same shape as a
            # survey ending on its attest.
            if wake.kind == "tick:challenge" and any(
                    w[0] == "challenges" for w in sb.ctx.writes):
                break

            # A slicing session ends on the turn that slices. Measured three
            # ways on L1-VK-slice: the first turn is right in every brief
            # variant (one ticket, the item's own words) and every later
            # turn, prompted again by the open loop, invents -- 4, 3 and 6
            # tickets under three briefs, 1 and green when the session ends
            # here. The judgement stays the model's: its one reply carries
            # as many slices as it judges right.
            if wake.kind == "tick:slicing" and any(
                    w[0] == "tickets" for w in sb.ctx.writes):
                break

            # And a define session ends when its word has landed. It has no
            # attestation to end on -- the glossary row *is* the result -- and
            # without this the first run of the phase wrote `provider` on turn
            # two and re-sent the same batch for ten more, each re-amending
            # the row and the last of them buying a bogus `sense=` tag.
            if wake.kind == "tick:define" and any(
                    w[0] == "glossary_terms" for w in sb.ctx.writes):
                break

            # A collision session ends the same way, on the write that is its
            # verdict: a synthesis or a `glossary.same`, both of which leave one
            # row superseded by another. Not on a plain amend -- a session may
            # correct a reading before it composes them. Without this the first
            # 14B collision wrote its synthesis on turn three and re-sent the
            # identical call five more times, a minute each, until the
            # third-identical rule ended it.
            if wake.kind == "tick:term_collision" and any(
                    w[0] == "glossary_terms" and (w[2] or {}).get("superseded_by")
                    for w in sb.ctx.writes):
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
            # Both, because `message_id` answers "why did this run" for exactly
            # one kind of wake and the others are the common case.
            wake_kind=wake.kind,
            wake_detail=wake.detail,
            wake_refs=tuple(wake.refs),
            # The brief as it was on disk when this ran, so two runs can be
            # told apart by the only other thing that shapes an artefact.
            briefs_hash=_briefs_hash(instructions),
            mode=mode,
            writes=[_as_write(w) for w in sb.ctx.writes],
            messages=_messages_from(sb, wake, session_id),
            tool_calls=sandbox_mod.drain_calls(sb.ctx),
            turns=turns,
            pins=pins.as_dict(),
            backend=getattr(backend, "name", ""),
            refusals=list(getattr(sb.ctx, "refusals", []) or []),
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
        # A ruling the Liaison read lands now, through the one door, after
        # the reading is on record. Inside the session it would land a
        # ruling from a session that then died.
        if any(w.table == "rulings" for w in result.writes):
            from ..roles.principal import apply_rulings

            apply_rulings(conn)
        outcome.committed = True
        outcome.result = result
        return outcome

    except Exception as exc:
        outcome.errors.append(f"session failed: {exc!r}")
        release(conn, wake.role)
        sandbox_mod.drain_calls(sb.ctx)
        return outcome


def _recipient_of(fn: str, g) -> str:
    """`msg.question_vision_keeper` -> `vision_keeper`: the recipient is the
    role id the function name ends with, matched against the graph's roles,
    because a role id may itself contain an underscore."""
    name = fn.split(".", 1)[1] if "." in fn else fn
    known = getattr(g, "roles", None) if g is not None else None
    known = known() if callable(known) else (known or [])
    roles = sorted(known, key=len, reverse=True)
    for r in roles:
        if name.endswith("_" + r):
            return r
    return name.rsplit("_", 1)[1] if "_" in name else ""


def _param_sets(sb) -> dict:
    """{function: (required params, all params)} for the unlabelled-block
    parse. The sandbox's bound functions carry the real signature."""
    import inspect

    out = {}
    for name in sb.functions():
        art, fn = name.split(".", 1)
        try:
            sig = inspect.signature(getattr(sb[art], fn))
        except (TypeError, ValueError, KeyError, AttributeError):
            continue
        req = {n for n, prm in sig.parameters.items() if prm.default is inspect.Parameter.empty}
        out[name] = (req, set(sig.parameters))
    return out


def _derive_frame_record(conn, sb) -> None:
    """The frame session's attest, derived from its rulings.

    Citations are the first indexed file each ruled prefix covers -- real
    grains, so `check_survey_citations` holds -- and the record only lands
    when the session did not write one itself."""
    if any(w[0] == "survey_records" for w in sb.ctx.writes):
        return                                              # pragma: no cover
    ruled = [i for t, i, *_ in sb.ctx.writes if t == "frame_rulings"]
    if not ruled:
        return                                              # pragma: no cover
    cites = []
    for prefix in ruled:
        row = conn.execute(
            "SELECT grain FROM code_index WHERE grain_kind = 'path' AND "
            "(grain = ? OR grain LIKE ?) ORDER BY grain LIMIT 1",
            (prefix, prefix + "/%")).fetchone()
        if row:
            cites.append(row["grain"])
    at = conn.execute(
        "SELECT value FROM config WHERE key = 'project_commit'").fetchone()
    rid = f"{sb.ctx.role}:@frame"
    sb.ctx.writes.append(("survey_records", rid, {
        "area": "@frame", "outcome": "found",
        "commit_sha": (at["value"] if at else "") or ""}))
    for grain in dict.fromkeys(cites):
        sb.ctx.writes.append(("survey_citations", f"{rid}:{grain}",
                              {"survey_id": rid, "grain": grain,
                               "resolves": 1}))


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
