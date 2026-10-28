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

import ast
import json
import logging
import os
import posixpath
import re
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from . import config as config_mod
from . import lifecycle as lifecycle_mod
from . import sandbox as sandbox_mod
from ..design import graph as graph_mod
from ..llm import llm, toolproto, toolschema
from ..roles import api, prompts
from .db import (COPIES_END, OutboundMessage, REPEAT_END, SessionResult, Turn,
                 Write, session_commit, session_fail, session_note, table_of,
                 tables_of)
from .identity import NATURAL_KEYS
from .scheduler import Wake, claim, not_retired, release

_log = logging.getLogger(__name__)

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
    # The native calls of each completion, in step with `completions`, and
    # the functions the session offered. A grader reads them, because a
    # native call is not in the text (frame 323).
    native: list[list] = field(default_factory=list)
    offered: list[str] = field(default_factory=list)


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



def routed_pins(conn: sqlite3.Connection, pins: "llm.Pins", wake: Wake) -> "llm.Pins":
    """
    The pins a wake's session runs with: the routed model for the role, and
    the run's pins for that model. Rebuilding Pins from three fields dropped
    every other pin on the way to a night; the profile's per-model think
    (finding 81, 2026-09-15) is the one that mattered.

    The Architect's relay wake runs with think on, and every other wake
    keeps the profile's think (frame 244, pass 2b). On 2026-10-15, think on
    left the declined files in 0 of 5 samples on s152, s119 and s172, and
    in 4 or 5 of 5 on s125. With think off they stayed on all four seats
    (`f244/p2_think_replay.out`, `f244/p2_think_replay_148.out`). On night
    149 the rule reaches 5 Architect relay wakes, and 2 of 5 contest a
    batch's files.
    """
    import dataclasses as _dc
    routed = config_mod.routed_model(
        config_mod.get(conn, "model_routing"), wake.kind, wake.role)
    model = routed or pins.model
    think = None
    window = None
    try:
        from ..llm import profile as _profile
        prof = _profile.of_run(conn)
        think = (prof.think or {}).get(model) if prof else None
        # The role's own window, when the profile names one. Night 81
        # (2026-09-16): the Developer's fix-loop wake ran 11480 tokens
        # against the shared 12288. It applies with or without a routed
        # model for the role.
        window = (prof.context or {}).get(wake.role) if prof else None
    except Exception:
        think = None
    relay_think = (wake.role == "architect" and wake.kind == "message"
                   and wake.detail == "relay")
    if not routed and not window and not relay_think:
        return pins
    if relay_think:
        think = True
    return _dc.replace(pins, model=model,
                       think=think if think is not None else pins.think,
                       num_ctx=window if window else pins.num_ctx)

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


def _asks_about_entries(conn: sqlite3.Connection, body_refs: str | None) -> bool:
    """True when every ref of a question is an entry of the transcript."""
    from .db import refs_of

    refs = [r for r in refs_of(body_refs) if isinstance(r, str)]
    return bool(refs) and all(
        conn.execute("SELECT 1 FROM entries WHERE id = ?", (r,)).fetchone()
        for r in refs)


def answer_about(conn: sqlite3.Connection, clarify_id: str) -> list[str] | None:
    """The rows a reply to the clarify `clarify_id` is about, or None.

    The asker's refs come first, then the clarify's refs that the asker did
    not name. None means the clarify has no asker. The answering prompt and
    the clarify door of `rulings.rule` read this one set. On night 158 the
    prompt showed m144's `[cr_2, tst_02]`, the door keyed on m145's
    `[tst_02]`, and the door refused the revise of cr_2 (frame 306).
    """
    clarify = conn.execute("SELECT body_refs, cause_id FROM messages WHERE id = ?",
                           (clarify_id,)).fetchone()
    if clarify is None:
        return None
    asker = conn.execute(
        "SELECT body_refs FROM messages WHERE id = ?",
        (clarify["cause_id"],)).fetchone() if clarify["cause_id"] else None
    if asker is None:
        return None
    from ..roles.api import _table_of_ref

    own = json.loads(clarify["body_refs"] or "[]")
    # An asker's ref joins only when it names a row a ruling can carry. On
    # night 144 the door admitted m385, a message id, and landed it in
    # `per_item` (frame 306, review 1, finding 2).
    about = [r for r in json.loads(asker["body_refs"] or "[]")
             if isinstance(r, str) and (_table_of_ref(conn, r) or table_of(
                 conn, r, among=("batches",)))]
    return about + [r for r in own if r not in about]


# The converse wake's `current_request` carries this sentence as `relation`
# (frame 193's design, 2.G.1).
CURRENT_REQUEST_RELATION = (
    "This is the request before these words. The new words continue it only "
    "when they name the same function or the same feature. Otherwise they are "
    "a new request, and you leave `supersedes` out.")


def message_entry_id(conn: sqlite3.Connection, message_id: str) -> str | None:
    """The entry a principal message's session segments, or None."""
    # The message's own words come first. A reply to a clarify carries the
    # clarify's refs, and on a clarify about an entry those name the old
    # entry, so a request in the reply was segmented against the words it
    # answered (the diff review of 0baacf55, finding 1).
    own = conn.execute("SELECT id FROM entries WHERE id = ?",
                       (f"e_{message_id}",)).fetchone()
    if own:
        return own["id"]
    # A driver's message names its entry in its refs: `m_p1` carries
    # `e_p1`. A derivation by name alone refused every brief.segment of
    # clickI night 17 with "no entry to segment against".
    from .db import refs_of

    msg = conn.execute("SELECT body_refs FROM messages WHERE id = ?",
                       (message_id,)).fetchone()
    for ref in refs_of(msg["body_refs"]) if msg else []:
        if conn.execute("SELECT 1 FROM entries WHERE id = ?", (ref,)).fetchone():
            return ref
    return None


def live_criteria(conn, col: str) -> str:
    """`scheduler.live_criteria`, imported late as this module's other
    scheduler reads are."""
    from .scheduler import live_criteria as live

    return live(conn, col)


def _page_acts(wake: Wake, conn: sqlite3.Connection | None) -> dict | None:
    """His ruling's drops and added line, on a criterion relay wake only.

    None on any other wake, so no other prompt changes (frame 306, pass 1b).
    """
    if (conn is None or wake is None or not wake.message_id
            or wake.role != "terminologist"
            or _mode_key(wake, conn) != "criterion_repair"):
        return None
    row = conn.execute("SELECT verb, body_refs FROM messages WHERE id = ?",
                       (wake.message_id,)).fetchone()
    if row is None or row["verb"] != "relay":
        return None
    try:
        refs = json.loads(row["body_refs"] or "[]")
    except (TypeError, ValueError):
        return None
    from ..roles.api import criteria_page_acts

    return criteria_page_acts(conn, refs)


def _wake_allow(wake: Wake, conn: sqlite3.Connection | None) -> list[str] | None:
    """The mode's tools, and the criteria ops his ruling asks for on this wake.

    A tool in `criterion_repair.tools` is an invitation on every wake. So
    `criteria.retire` comes only when the ruling drops a line, and
    `criteria.specify` only when it adds one (frame 306, pass 1b).
    """
    allow = prompts.mode_tools(wake.role, _mode_key(wake, conn))
    acts = _page_acts(wake, conn)
    if allow is None or not acts:
        return allow
    extra = (["criteria.retire"] if acts["retire"] else []) + (
        ["criteria.specify"] if acts["add"] else [])
    return allow + [t for t in extra if t not in allow]


def _page_act_lines(wake: Wake, conn) -> list[str]:
    """The lines that tell the seat what his ruling drops and adds."""
    acts = _page_acts(wake, conn) or {}
    lines = [f"His ruling drops the line of {cid}. Retire it with "
             f"criteria.retire(id='{cid}')." for cid in acts.get("retire") or ()]
    for ticket, sentence in acts.get("add") or ():
        lines.append(f"He asks for a new line: {sentence!r}. Write it with "
                     f"criteria.specify under ticket {ticket}.")
    return lines


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
                "SELECT c.verb AS cause_verb, c.id AS cause_id, c.body_refs AS cause_refs "
                "FROM messages m LEFT JOIN messages c ON c.id = m.cause_id WHERE m.id = ?",
                (wake.message_id,)).fetchone()
            # A reply to a park ask is words on a page that stays open. It
            # has no desk to relay to, so it is not `answering` (frame 87).
            from .scheduler import park_ask_batch

            if row and row["cause_id"] and park_ask_batch(row["cause_id"]):
                return "landing"
            # A clarify on an entry asked what the principal wants. The reply
            # is a request, and only `converse` has `brief.intake` to land it.
            # In `answering` the words landed on no row, because an entry is
            # no ledger row (the diff review of 0baacf55, finding 1; ruled:
            # Roman, 2026-10-08, the park ask is a page with rows, point 4).
            if row and row["cause_verb"] == "clarify" and _asks_about_entries(
                    conn, row["cause_refs"]):
                return "converse"
            if row and row["cause_verb"] == "clarify":
                return "answering"
            # And a reply to a confirm or a present is a ruling to read
            # (ruled 2026-09-10: the seat is text, no parser reads it).
            if row and row["cause_verb"] in ("confirm", "present"):
                return "landing"
        # A ruling on a criterion goes to the mode that respecifies it and
        # tells the Tester. A tool added to `relay` is an invitation
        # (measured: `decisions.author` in a relay mode, 2026-09-03), and
        # `criterion_repair` already holds both calls (frame 142's design,
        # 2.F, amendment 4). Only a park page's ruling, and only criteria:
        # a term ruling beside one needs `glossary.adopt`, which the repair
        # mode lacks (the diff review of b0a2086e, finding 1).
        if (verb == "relay" and wake.role == "terminologist" and conn is not None
                and wake.message_id):
            from .scheduler import park_criterion_relay

            if park_criterion_relay(conn, wake.message_id):
                return "criterion_repair"
        # A ruling on a touch note's batch line goes to the mode that writes
        # the prediction. `annotate` already holds `batches.annotate`, and a
        # tool added to `relay` is an invitation, the reason of the repair key
        # above (frame 190's design, 2.2,
        # the batch line, point 4).
        if (verb == "relay" and wake.role == "architect" and conn is not None
                and wake.message_id):
            from .scheduler import batch_relay, guess_relay

            # A ruling on a code line goes to the mode that writes the guess
            # (frame 298's design, 3.4, point 5).
            if guess_relay(conn, wake.message_id):
                return "guess"
            if batch_relay(conn, wake.message_id):
                return "annotate"
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


# The tick wakes whose detail is said to the role. Only these: a detail
# line on every tick changed the Liaison's observed_entries reply from a
# bracketed list to a bare one (click night 47, 2026-09-14), on a wake no
# register case carries the live detail of. A kind joins this set with a
# case that carries its detail (`detail:` in the case file).
DETAIL_SHOWN = {"tick:tests_missing",
                # Which findings the Critic upheld, so the Developer knows the
                # finding passed the Critic (frame 88, 2026-09-27).
                "tick:finding_violated",
                # Which upheld finding exhausted the loop (frame 88).
                "tick:findings_exhausted",
                # Which budget stopped the batch. A batch with no red test
                # wakes this rung too (frame 330, review of pass 5, finding 1).
                "tick:exhausted",
                # Which batch is parked and on which key (frame 87).
                "tick:park_ask",
                # Which earlier item the shift question is about, and where
                # it stands (frame 193's design, 2.F.1).
                "tick:request_shift",
                # Which ticket of the item has no criterion (frame 322).
                "tick:criteria",
                # Which grains strayed, and the removed line of a removal
                # (frame 339). No case carries this detail yet.
                "tick:touch_strayed"}


def _mistake_rows(conn: sqlite3.Connection, batch_id: str) -> list[str]:
    """Each `mistake` row at the batch's head, as `path (note)`, the form
    `touch_strayed` shows the Architect."""
    rows = conn.execute(
        "SELECT s.path, s.note FROM touch_strays s JOIN batches b "
        "ON b.id = s.batch_id AND s.commit_sha = b.head_commit "
        "WHERE s.batch_id = ? AND s.status = 'mistake' ORDER BY s.path",
        (batch_id,)).fetchall()
    return [f"{r['path']} ({r['note']})" if r["note"] else r["path"]
            for r in rows]


def compose_system(role: str, sb: sandbox_mod.Sandbox, *, instructions: str,
                   oneshot: bool = False, native: bool = False) -> str:
    """
    The system prompt, whole: who you are and what you may do.

    Split out of `build_prompt` so that a reader of the register can compose
    it. The cassette key covers this text, and `prompt_hash` covers the brief
    alone, which is a strict prefix of it. So a tools edit moved the key and
    left every result reading green against recordings the suite could no
    longer replay (observed: frame 54, 117 of 117 cases, 2026-09-21).

    The sandbox must already carry `_order`, because `signatures()` reads it.
    `session_sandbox` sets it before it returns.
    """
    # Under native calls the list loses its `TOOL:` prefix, because the
    # prefix teaches the text form that the native block forbids (frame 323).
    marker = "" if native else "TOOL: "
    fns = "\n".join(f"  {marker}{sig}" for sig in sb.signatures())
    calling = (
        f"Call the offered tools directly. Make one tool call for each use "
        f"of a function from the list above. Write no `TOOL:` line, because "
        f"a native call is the only form that runs.\n\n"
        if native else
        f"Call one per line. `TOOL:` is a literal marker — write those five "
        f"characters, then the function name from the list above, then its "
        f"arguments in brackets:\n"
        f"  TOOL: artefact.verb(key='value')\n"
        f"Only `artefact.verb` and `key` stand in for something; everything "
        f"else on that line is written exactly as shown.\n\n")
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
        # fix for it is not an improvement. The text lives in `calling` above.
        f"{calling}"
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
    return system


def _last_word_lines(conn, wake: Wake) -> list[str]:
    """
    The principal's last ruling on each criterion the repair's question names.

    Night 144's s546 woke on the Tester's question m379. Its prompt held no
    word of ruling r_c4bf70291d, so it put back the flag he had contested
    (frame 226). None when no ruling names the criterion.
    """
    from ..roles.principal import last_ruling_on

    lines: list[str] = []
    ruled_refs: list[str] = []
    for mid in wake.refs:
        row = conn.execute("SELECT body_refs FROM messages WHERE id = ?",
                           (mid,)).fetchone()
        try:
            refs = json.loads(row["body_refs"] or "[]") if row else []
        except (TypeError, ValueError):
            refs = []
        for ref in refs:
            # A retired criterion takes no repair (frame 306, pass 1c).
            if not isinstance(ref, str) or not conn.execute(
                    "SELECT 1 FROM criteria WHERE id = ?"
                    + live_criteria(conn, "retired_by"), (ref,)).fetchone():
                continue
            # An approve's words are about other lines of its page. Night
            # 144's r_373fbae7da approved this criterion and asked about
            # line 3 (the review of 33cd99b2, finding 4).
            ruled = last_ruling_on(conn, ref)
            if ruled is None or ruled["verdict"] not in ("contest", "revise"):
                continue
            # Only the sentences on this row. Night 165's s132 woke for c1,
            # got his sentences on lines 2 to 7, and wrote "Delete lines 5
            # and 6" as c1's text (frame 306, W-A).
            words = _words_on_rows(conn, ruled["id"], ruled["words"], [ref])
            legend = _line_legend(conn, ruled["id"], words, woken=ref)
            lines.append(
                f"\nThe principal's last word on this criterion, {ref} "
                f"(ruling {ruled['id']}, {ruled['verdict']}):\n"
                + "\n".join([words, *legend]))
            # With no legend the wake keeps the sentence of 03f6e900, so its
            # recorded prompts stay green (the review of 2a464938, finding 2).
            lines.append(("Write the behaviour his words ask for. His line "
                          "numbers name lines of his page, listed above. "
                          if legend else
                          "Write the criterion in the principal's words. ")
                         + "Do not send the sentence he contested.")
            if ref not in ruled_refs:
                ruled_refs.append(ref)
    # Night 149's s178 held his words six times and no text he contested.
    # It wrote "UsageError" back into 3 of 6 criteria (frame 243, review 2,
    # finding 5). The block shows the texts, as on the relay wake. The
    # legend stands once, under the quote. Two legends of one ruling can
    # name different lines (the review of 2a464938, finding 3).
    block = _contest_block(conn, [{"id": ref} for ref in ruled_refs],
                           on_rows=True, legend=False)
    if block:
        lines.append(f"\n[{CONTESTS_KEY}]\n{block}")
    return lines


def _words_on_rows(conn, rid: str, words: str, cids: list[str]) -> str:
    """The sentences of ruling `rid`'s words that bear on any of `cids`, in
    his order. The whole words when no sentence is kept, when no page
    order is recorded at his reply, or when a row's line is not known."""
    from ..roles.principal import seen_order

    # Without the order of frame 272, `_ruling_line` reads today's render.
    # That render can put the row on another line and drop the sentence
    # that rules it, as a probe of night 144's r_c4bf70291d shows.
    row = conn.execute("SELECT reply_id FROM rulings WHERE id = ?",
                       (rid,)).fetchone()
    if not (row and seen_order(conn, row["reply_id"], None)):
        return words
    ruled = {"id": rid, "words": words}
    rows: set[int] = set()
    for cid in cids:
        # A check line is its criterion's row (the re-check of 2ece9cd2).
        lines = api._ruling_rows(conn, ruled, cid)
        if lines is None:
            return words
        rows |= lines
    # A sentence with no line number continues the sentence before it.
    # "Line 4 is wrong. Delete it." put "Delete it." on c1's wake, with no
    # referent but line 2 (the review of 2a464938, finding 1). A sentence
    # before any line number stays on every row.
    out: list[str] = []
    bound: set[int] | None = None
    for sentence in api._RULING_SENTENCE.split(words):
        refs = api._line_reading(sentence).named
        if refs:
            bound = set(refs)
        if bound is None or bound & rows:
            out.append(sentence)
    return " ".join(out) if out else words


def _line_legend(conn, rid: str, words: str,
                 woken: str | None = None) -> list[str]:
    """One line for each page line that ruling `rid`'s words name: the row
    that stood on that line of his page. Empty when the words name no line.
    With `woken`, a row of another criterion says it is not this repair.

    His words stay verbatim, and the legend stands beside them (composition
    line 106). The seat never sees his page, so "line 3" had no referent.
    Night 165's s359 read "remove both lines" as docstring lines and cut 17
    of them (frame 306, W-A).
    """
    from ..roles.principal import ruled, seen_order

    row = conn.execute("SELECT reply_id FROM rulings WHERE id = ?",
                       (rid,)).fetchone()
    # Only the order `principal.land` recorded at his reply (frame 272).
    # Today's render can put another row on his line, as night 158's did.
    order = seen_order(conn, row["reply_id"], None) if row else []
    if not order:
        return []
    named: set[int] = set()
    for ref in api._line_reading(words, len(order)).refs:
        if ref.word == "note":
            continue
        named |= ref.lines
    # The text he read first is `old_text` of the ruling's rows.
    texts = {r["ref"]: r["old_text"] for r in ruled(conn, ruling=rid, landed=False)}
    out: list[str] = []
    for n in sorted(x for x in named if 1 <= x <= len(order)):
        rid_n = order[n - 1]
        test = conn.execute("SELECT criterion_id FROM tests WHERE id = ?",
                            (rid_n,)).fetchone()
        if test is not None:
            tag = _other_row(woken, test["criterion_id"])
            out.append(f"On his page, line {n} was the check of "
                       f"{test['criterion_id']}{tag}.")
            continue
        # The text he read first. A row he did not contest keeps its text.
        text = texts.get(rid_n)
        if not isinstance(text, str):
            got = conn.execute(
                "SELECT text FROM criteria WHERE id = ? ORDER BY version DESC",
                (rid_n,)).fetchone() or conn.execute(
                "SELECT text FROM items WHERE id = ?", (rid_n,)).fetchone()
            text = got["text"] if got else None
        tag = _other_row(woken, rid_n)
        out.append(f"On his page, line {n} was {rid_n}{tag}: {text}" if text
                   else f"On his page, line {n} was {rid_n}{tag}.")
    return out


def _other_row(woken: str | None, rid: str) -> str:
    """The mark for a legend row that is not the woken criterion, else "".

    The c1 wake said "line 3 was c2" beside "change line 3 so ...", and
    night 165's seat copied other rows' sentences into c1 (the review of
    2a464938, finding 4). The mark stands in brackets before his text. After
    the text, a comma joined it to the criterion (the re-check of 2ece9cd2).
    """
    if woken is None or rid == woken:
        return ""
    return " (another criterion, not this repair)"


CONTESTS_KEY = "the principal contested these criteria"


def contests_on(conn, ref: str) -> list[dict]:
    """
    Every contest ruling on criterion `ref`, oldest first: its id, the text
    he contested, and his words.

    The words and the text come from the `rulings` row whole. `text` is None
    for a ruling older than `rulings.texts`. A stale ruling does not count,
    as in `last_ruling_on` (frame 243).
    """
    from ..roles.principal import ruled

    # The rows on `ref` in `ruled_refs_live` (the seam design, 3.1).
    return [{"id": r["ruling_id"], "text": r["old_text"], "words": r["words"],
             "seq": r["ruling_seq"]}
            for r in ruled(conn, [ref], landed=False)
            if r["verdict"] == "contest" and r["words"]]


def _contest_block(conn, rows: list, on_rows: bool = False,
                   legend: bool = True) -> str:
    """
    The principal's contests on the pushed criteria, as plain lines.

    The block stands apart from the criteria rows. A key on one row only
    makes `_as_table` refuse the list, and the whole push turns into JSON
    (frame 243, review 1, finding 2). His words refer to the text he read,
    so that text goes first (finding 1). Empty when he contested none.

    One entry per ruling, oldest first, with each criterion's text under it
    and his words once. On night 149's s190, one entry per criterion said
    each ruling's words six times (frame 243, review 2, finding 2).

    A legend under his words names the row on each page line they name.
    `on_rows` keeps only his sentences on the pushed rows, for the repair
    wake (frame 306, W-A). `legend` False drops the legend, because the
    repair wake shows it under the quote.
    """
    rulings: dict[str, dict] = {}
    for r in rows:
        if not (isinstance(r, dict) and isinstance(r.get("id"), str)):
            continue
        for c in contests_on(conn, r["id"]):
            entry = rulings.setdefault(
                c["id"], {"seq": c["seq"], "words": c["words"], "on": []})
            entry["on"].append((r["id"], c["text"]))
    lines: list[str] = []
    for rid, entry in sorted(rulings.items(), key=lambda kv: kv[1]["seq"]):
        lines.append(f"ruling {rid}:")
        lines.append(f"He contested {', '.join(cid for cid, _ in entry['on'])}.")
        for cid, text in entry["on"]:
            if not text:
                continue
            # Frame 328, item 5: night 168's sessions read the old text here,
            # and 18 of 65 challenge turns quoted it. So a replaced text says
            # so first, and the live text stands under it.
            row = conn.execute("SELECT text, retired_by FROM criteria "
                               "WHERE id = ?", (cid,)).fetchone()
            live = row["text"] if row else None
            if row and row["retired_by"]:
                # Review of pass 1, finding 8: a retired row has no live text.
                lines.append(f"{cid}: He contested this text, and the "
                             f"criterion is retired now: {text}")
            elif live and " ".join(live.split()) != " ".join(text.split()):
                lines.append(f"{cid}: He contested this text, and it is "
                             f"replaced now: {text}")
                lines.append(f"{cid}: The live text is: {live}")
            else:
                lines.append(f"{cid}: He contested this text: {text}")
        words = entry["words"]
        if on_rows:
            words = _words_on_rows(conn, rid, words,
                                   [cid for cid, _ in entry["on"]])
        lines.append(f"He said: {words}")
        if legend:
            lines.extend(_line_legend(conn, rid, words))
    return "\n".join(lines)


def _relay_contest_block(conn, role: str, inbound: dict[str, Any]) -> str:
    """
    The contest block for the criteria a relay asks the Terminologist to
    respecify. Empty for any other wake.

    This wake pushes no `criteria.load`. The relay's refs list the criteria,
    so the block follows the relay. Night 149's s190 held the ruling's words
    in `principal_said` and no text he contested. It wrote back the words he
    had declined three times (frame 243, interview 2). The block adds the
    contested texts and the earlier rulings' words.

    Only a criterion this relay contests gets the block. Night 149's m133
    relayed his approve on cr_5, and old contests there would invite a
    rewrite of a criterion he kept (frame 243, review 2, finding 1).
    """
    if role != "terminologist" or inbound.get("verb") != "relay":
        return ""
    verdict = inbound.get("principal_verdict")
    if not isinstance(verdict, dict):
        return ""
    rows = [{"id": ref} for ref in inbound.get("refs") or ()
            if isinstance(ref, str) and verdict.get(ref) == "contest"
            and conn.execute(
                "SELECT 1 FROM criteria WHERE id = ?"
                + live_criteria(conn, "retired_by"), (ref,)).fetchone()]
    return _contest_block(conn, rows)


def _files_contest_block(inbound: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """
    The message to show, and the principal's words on a files contest.

    On a relay that contests a batch's touch list, his words leave
    `principal_said` and stand in a block under the list, as frame 243 puts
    contest words under `[criteria.load]`. On night 148, s152 and s119 read
    his words in `principal_said` and kept the files he declined. Try 2's
    shape E, this block with the annotate brief's dispute sentence, moved
    s152 in 5 of 5 and s119 in 3 of 5, and broke 0 of 15 right calls
    (`plans/frame244-try-2.md`, 2026-10-15). The inbound itself keeps the
    words for the session row. Any other message shows as before.

    The block never lists a path of `expected` or `possible`. The night-149
    interview found that s125 and s172 read the old heading, "he contested
    these files", as his own list of the files the change touches
    (`plans/frame244-interview-2.md`, 2026-10-15). That list was the touch
    note's prediction, with kept files beside declined ones. So the block
    lists the parser's disputed paths alone. When the parser found none,
    the block lists no path and points to his words.
    """
    touch = inbound.get("touch")
    said = inbound.get("principal_said")
    verdict = inbound.get("principal_verdict")
    if not (isinstance(touch, dict) and said and isinstance(verdict, dict)):
        return inbound, ""
    contested = [b for b in touch if verdict.get(b) == "contest"]
    if not contested:
        return inbound, ""
    shown = {k: v for k, v in inbound.items() if k != "principal_said"}
    disputed: list[str] = []
    for b in contested:
        for path in (touch[b] or {}).get("disputed") or ():
            if isinstance(path, str) and path not in disputed:
                disputed.append(path)
    if disputed:
        lines = ["The principal said these files have nothing to do with "
                 "this change. Leave them out:", *disputed]
    else:
        lines = ["The principal said that some of the files above have "
                 "nothing to do with this change. His words name them. "
                 "Leave them out."]
    lines.append(f"He said: {said}")
    return shown, "\n".join(lines)


def build_prompt(role: str, sb: sandbox_mod.Sandbox, wake: Wake,
                 pushed: dict[str, Any], instructions: str,
                 inbound: dict[str, Any] | None = None,
                 oneshot: bool = False,
                 native: bool = False) -> tuple[str, str]:
    """
    System prompt = who you are and what you may do; user prompt = why you woke.

    The working set is *pushed* rather than fetched. Having `model.consult()`
    available does not mean a cold session will call it, and a role that
    re-derives what it was already given wastes a turn. Tools are for going
    deeper than the push.
    """
    system = compose_system(role, sb, instructions=instructions,
                            oneshot=oneshot, native=native)

    body = [f"You were woken by: {wake.kind}"]
    if wake.message_id:
        body.append(f"Inbound message: {wake.message_id} ({wake.detail})")
        caused = _answer_cause_line(sb.ctx.conn, wake)
        if caused:
            body.append(caused)
        missed = _missed_reply_line(sb.ctx.conn, wake)
        if missed:
            body.append(missed)
    subject_word = ""
    if wake.refs:
        body.append(f"Refs: {', '.join(wake.refs)}")
        # The subject, said plainly. A define session read `Refs: @term:note`
        # and defined `@term`; the sigil is for the scheduler, not the role.
        from .scheduler import PROGRAM, is_area, term_of

        subject = wake.refs[0]
        if term_of(subject):
            subject_word = term_of(subject)
            body.append(f"The word: {subject_word}")
        elif subject == PROGRAM:
            body.append("The subject: the whole program")
        elif is_area(subject) and wake.kind == "tick:survey":
            body.append(f"The area: {subject}")
    if wake.kind.startswith("tick:") and wake.attempt >= 2:
        # A retry at temperature zero repeats the first session unless the
        # prompt moves. Night 88 (2026-09-23): four tick wakes ran three
        # times each, user and completion identical every time. The sentence
        # is outside `DETAIL_SHOWN`, because it is not a kind's detail. It is
        # a fact of the dispatch, and it holds for every tick kind. It says
        # "did not clear this wake" and not "recorded nothing", because a
        # retry can write and still leave the wake undrained (night 87,
        # `developer|tick:tests_failing|bg_1`).
        cap = config_mod.get(sb.ctx.conn, "tick_attempt_cap")
        body.append(
            f"This is attempt {wake.attempt} of {cap} on this wake. The earlier "
            f"attempt did not clear this wake, so the same answer will not clear "
            f"it. Do something the earlier attempt did not.")
    if (wake.kind in DETAIL_SHOWN and wake.detail
            and wake.detail not in (wake.kind.split(":", 1)[1], subject_word)):
        # What the predicate knows about the subject, said to the role:
        # "without a test: c1, c2", "attempt 2 of 10". clickI night 46
        # (2026-09-14): the Tester had to diff six criteria against three
        # tests to find the three it was woken for, and got it wrong. Not
        # the tick's own name (a case wake's default detail) and not the
        # word already said above.
        body.append(wake.detail)
    if wake.kind == "tick:touch_mistaken" and wake.refs:
        # Each judged row with its note, read here and not put in the
        # detail. `cycles._key` holds the detail, and the Architect writes a
        # new note on each head, so a bounce would get a new key each round
        # (F7 review p3b, finding 8). Night 172's s263 read "Refs: bg_3" only.
        body.extend(_mistake_rows(sb.ctx.conn, wake.refs[0]))
    if wake.kind == "tick:criterion_repair":
        body.extend(_last_word_lines(sb.ctx.conn, wake))
    # Frame 317: a Tester woken by an answer reads the same failed runs as a
    # challenged one. s370 saw them and fixed tst_v3. s364 did not.
    if inbound and role == "tester" and wake.detail in ("challenge", "answer"):
        # Frame 110's interview: inside an escaped JSON string the seat read
        # the challenge as a criterion question. Asked in plain words, it
        # blamed the test. The JSON below stays as it is for other readers.
        body.extend(_failed_run_blocks(inbound))
        # Frame 223, night 153: 0 of 3 seats read the callable that raised,
        # though the brief told them to call `code.source`.
        raised = _raised_signature_pushes(sb, inbound)
        if raised:
            pushed = {**pushed, **raised}
    if role == "tester" and (wake.kind == "tick:tests_missing" or inbound):
        # Frame 143, night 154: s199 asserted `confirm(...) == "y"` with no
        # line of `confirm` in its prompt. The interview's replay put the
        # surface before `[batches.expect]`, and that order gave 3 of 3.
        surfaces = _criterion_surface_pushes(sb, wake, inbound)
        if surfaces:
            keys = list(pushed)
            at = keys.index("batches.expect") if "batches.expect" in keys else len(keys)
            pushed = {**{k: pushed[k] for k in keys[:at]}, **surfaces,
                      **{k: pushed[k] for k in keys[at:]}}
    if inbound:
        body.append("\nThe reports that came back:" if "reports" in inbound
                    else "\nThe message that woke you:")
        shown, block = _files_contest_block(inbound)
        if role == "tester" and wake.detail == "answer":
            # Frame 317, pass 1b: a test with a block above shows once. The
            # second copy cost about 4,700 characters on s364's wake.
            rows = shown.get("resolved_refs") or {}
            kept = {k: v for k, v in rows.items()
                    if not _has_failed_run_block(v)}
            if len(kept) != len(rows):
                shown = {**shown, "resolved_refs": kept}
        body.append(json.dumps(shown, indent=2, default=str))
        if block:
            body.append("\n" + block)
        contests = _relay_contest_block(sb.ctx.conn, role, inbound)
        if contests:
            body.append(f"\n[{CONTESTS_KEY}]\n{contests}")
        acts = _page_act_lines(wake, sb.ctx.conn)
        if acts:
            body.append("\n" + "\n".join(acts))
    if pushed:
        # Say that these have *already run*. Without it a survey session spent
        # four of its eight turns calling `code.survey` again -- the results were
        # in front of it and it re-fetched them, then ran out of budget before
        # attesting, which is what left `tick_survey` undrained on a real repo.
        #
        # The sentence is false for the fix wake's `tests.load`, which a call
        # returns as raw rows and not as the pushed summary. Frame 121 named
        # `tests.load` here, and two green cases fell to 3 of 5: the runs
        # called it 2 to 5 times. So the bytes stay, and the repeat call's
        # return is a frame of its own.
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
# A source span is the one result that has to arrive whole: a function the
# Developer is about to edit. Night 79 (2026-09-15, finding 82): version_option
# is 207 lines and 8692 characters; at 6000 the 9B fetched it in two cut
# pieces, asked for the same cut span five more times and never wrote.
# Sentence two's function fitted in one result and it wrote at turn 9.
# 14000 characters is about 3500 tokens of a 12288 window, and the
# estimate flag on the completion says when a prompt outgrows it.
SOURCE_CHARS = 14000
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
# The decision record's own share of a push, budgeted below the backstop above.
# Night 87 (2026-09-20, frame 46's design review, probe 2 over 463 pushes):
# `decisions.search` was 55.5 per cent of every pushed character, and its median
# push was 20,105 characters -- `PUSH_CHARS` plus the truncation notice. So it
# saturated the backstop on nearly every push. The site runs up to six queries
# and the op has no LIMIT, so the cut chose the rows and nobody chose the cut.
# Worse, the backstop's notice says to ask for the next range, and a push has no
# range to ask for. 6,000 is `RESULT_CHARS`: what one asked-for result may cost,
# spent here on a read nobody asked for.
DECISIONS_PUSH_CHARS = 6000
# What one turn's results may sum to. The per-result caps above are per
# result, and nothing added them up: two `code.source` reads in one reply are
# 28,000 characters, and `_fit_budget(12288, 4000)` is 20,391 -- so one turn
# could produce more than the whole session may hold. Measured: two capped
# source reads exceed the budget on 1,367 of 1,367 recorded turns at 12,288,
# and still exceed it at 16,384 whenever the system prompt runs past 4,522
# characters.
#
# The number is the two caps it is made of, and the arithmetic is the point:
#
#   one source span whole, at SOURCE_CHARS      14,000  (night 79: a cut span
#                                                        is re-asked, not read)
#   one other result at its own cap             + 6,000
#                                               = 20,000
#
# A probe is the other result this has to carry: 60 rows render about 2,200 and
# never more than RESULT_CHARS, so probe-then-read costs about 16,200 and fits
# whole. Two source reads do not, and the second one is cut where `_render`
# says the cut fell. Sizing this below 16,200 would bite the source read the
# seat actually needs, which is the failure recorded above at night 79.
TURN_RESULT_CHARS = SOURCE_CHARS + RESULT_CHARS
# Under this, a result says nothing a session can act on, so it is withheld
# whole and named instead of being served as a stub.
MIN_RESULT_CHARS = 400
# What `_render`'s own cut notice costs, at its longest: the `cut_note` sentence
# plus the `code.source` call that fetches the rest of a span.
_CUT_NOTE_CHARS = 300

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

# The name stays because nightcount.py counts the sign with it (frame 232).
FABRICATED_RESULT = toolproto.INVENTED_RESULT

# A call name in backticks alone on its line, then a colon. Night 147's
# surveys wrote "`glossary.amend`:" over a list of words (frame 237).
_LISTED_HEAD = re.compile(r"^\s*`([A-Za-z_]\w*\.[A-Za-z_]\w*)`\s*:\s*$")


def listed_not_called(text: str, called: Any, allowed: Any) -> list[str]:
    """
    The call names a reply writes as a heading over a list, with no call.

    On night 147, 5 of 8 survey sessions on `src/click` wrote
    "`glossary.amend`:" and the words as a list under it. The parser finds
    no call in such a list, so nothing ran, and the record showed only the
    refused attest. Interviewed, the seat called its list "descriptions of
    what I would record, not runnable calls" (frame 237).

    `called` is the names the parser found in the same reply. The parser
    alone decides what ran, because it reads bullets and bare calls that a
    line pattern misses (frame 237's review, finding 1). `allowed` is the
    calls the mode offers, so a heading for any other name is prose. Names
    come in the order of the reply, each once.
    """
    lines = text.splitlines()
    names: list[str] = []
    for i, line in enumerate(lines):
        head = _LISTED_HEAD.match(line)
        if not head:
            continue
        name = head.group(1)
        if name in names or name in called or name not in allowed:
            continue
        if any(nxt.strip() for nxt in lines[i + 1:]):
            names.append(name)
    return names


# The rows behind a page, while they fit beside the page itself. Half a 12,288
# window is the budget on overflow (finding 79), the brief and the page take
# most of it, and 6,000 characters of rows is what is left. A four-line page is
# about 600.
LANDING_ROWS_CHARS = 6_000


def cut_note(what: str, not_shown: int, total: int, unit: str, call: str) -> str:
    """
    The one wording every cut uses, and the one place that owns it.

    Six wordings said the same thing, and four of eighteen strings named a call
    the seat could make (frame 46's design review, section 2.6, 2026-09-20). A
    pushed read was told to ask for the next range, and a push has no range to
    ask for, so the recovery sentence named nothing a seat could call.

    The order is the order of the seat's questions: what was cut, how much is
    not shown, then the call that returns it. `CUT` leads, so one word finds
    every cut in a prompt, a session record or a test.

    `call` is a whole sentence. A site with no call to name says so plainly,
    because naming a call that does not work is worse than naming none.
    """
    return (f"CUT {what}: {not_shown:,} of {total:,} {unit} are not shown. "
            f"{call}")


_WAKE_CUT_CALL = "Nothing returns a wake. Ask by name for the reads you need."
# The note of a wake an earlier turn cut. The runner stores the cut wake, so
# the note carries the only record of the uncut length (frame 119's diff
# review, finding 2: a second cut printed 4,634 of 18,182, not of 47,547).
_WAKE_CUT = re.compile(r"\nCUT your wake: [\d,]+ of ([\d,]+) characters are "
                       r"not shown\. " + re.escape(_WAKE_CUT_CALL) + r"\Z")


def _render_cut(text: str, limit: int, reply: bool = False) -> str:
    """
    Cut, saying so. The same contract `_render` keeps for a tool result.

    A text that an earlier cut already holds is cut from its kept part, and
    the note keeps the uncut total. A kept part inside the limit comes back
    as it is.

    A cut reply gets its own note. Night 119's s263 read `CUT your wake` on
    its own reply and found no next call (frame 121's interview, C). The
    caller cuts a reply only when the reply held no call, so no call ran.
    """
    if len(text) <= limit:
        return text
    if reply:
        return text[:limit] + chr(10) + cut_note(
            "your reply", len(text) - limit, len(text), "characters",
            f"The first {limit:,} characters stand above. No call in your "
            f"reply ran. Send one call, and keep your prose short.")
    earlier = _WAKE_CUT.search(text)
    body = text[:earlier.start()] if earlier else text
    total = int(earlier.group(1).replace(",", "")) if earlier else len(text)
    if earlier and len(body) <= limit:
        return text
    return body[:limit] + chr(10) + cut_note(
        "your wake", total - limit, total, "characters", _WAKE_CUT_CALL)


# The phrase the eviction notice carries, and the phrase the repeat line reads
# to learn that the middle is gone. One place, so the notice and the reader of
# the notice cannot drift apart. The notice's text is unchanged: 270 of 18,435
# cassettes carry it (measured 2026-09-20).
_EVICTED_PHRASE = "dropped to fit the window"

# How often one key's result is rendered in a session. Rule 2 of frame 77
# serves an answer the window took, so that no line ever points at a block the
# seat cannot see. A result larger than the room the exchange leaves is evicted
# on every turn, and serving it on every turn is night 88's s137 again, so the
# fourth asking is refused (the design review of frame 77, finding 3,
# 2026-09-23). The refusal names the window, because night 99's s132 had
# room for its results (frame 100).
SERVE_CAP = 3

# The pointer of the repeat refusal. It stays where the answer stands: frame
# 119 removed it everywhere, and night 115's s33 to s35 then repeated ten
# calls (reverted by 4d5757db, 2026-10-04).
_IN_THIS_PROMPT = "The answer is in this prompt."
_DROPPED_AFTER = "The window dropped the answer after this line"


def _repoint(transcript: list[str], kinds: list[str],
             pointers: list[tuple[str, str, str]], answered: dict[str, str],
             served: dict[str, int], sb: Any) -> list[tuple[str, str, str]]:
    """
    Correct a repeat refusal that the newest fit made false.

    Returns the pointers that still stand, and the loop checks them after the
    next fit. One check was not enough: a refusal from turn N said the answer
    was in the prompt at turn N+2, where that fit dropped it (frame 169's
    review, finding 1, probe F).

    The refusal is written against the prompt the seat just read, and `_fit`
    runs before the seat reads the refusal. Night 126's s159 was told at turn
    20 that the answer was in the prompt, and the fit had dropped it (frame
    169). Frame 46 found the same fault in the old repeat line, 2026-09-21.

    The new sentence states the fact and the step the runner gives next. Under
    the serve cap, the next asking is served again by rule 2 of frame 77. At
    the cap, the next asking is refused, so the step is the cap's own step.
    A DECISIONS.md rule says a refusal is satisfiable or says why not.
    """
    if not pointers:
        return []
    user = "\n\n".join(transcript)
    # The same test as `evicted` in the loop, so the promise below holds:
    # the next asking is a repeat of an evicted answer.
    evicted = _EVICTED_PHRASE in user
    kept: list[tuple[str, str, str]] = []
    for key, line, name in pointers:
        answer = answered.get(key)
        # A write since the refusal forgot the answer, and the next asking is
        # served as new. The old pointer then makes no claim this check owns,
        # so it leaves.
        if answer is None:
            continue
        at = next((i for i in range(len(transcript) - 1, -1, -1)
                   if kinds[i] == _RESULTS and line in transcript[i]), None)
        # The fit took the line itself, so no false sentence is left to
        # replace. The pointer leaves.
        if at is None:
            continue
        # The answer stands, so the sentence is true and stays word for word.
        # A later fit can still drop the answer, so the pointer stays.
        if not evicted or answer in user:
            kept.append((key, line, name))
            continue
        # From here the sentence is replaced once, and the pointer leaves.
        # The new sentence makes no claim about a later prompt.
        if served.get(key, 0) >= SERVE_CAP:
            bound = _bound_of(sb, name)
            step = (f"{_DROPPED_AFTER}, and it was served three times. "
                    + (f"Ask {name} for {bound}, or finish without it."
                       if bound else "Act without it, or finish."))
        else:
            step = (f"{_DROPPED_AFTER}, so ask once more and it is served "
                    f"again.")
        # Every copy of the line, because one pointer stands for identical
        # lines at two turns. The newest copy alone left the older one false
        # (frame 169's second look, probe B).
        for i in range(at + 1):
            if kinds[i] == _RESULTS and line in transcript[i]:
                transcript[i] = transcript[i].replace(
                    line, line.replace(_IN_THIS_PROMPT, step))
    return kept


def _dropped_note(dropped: int) -> str:
    """What the middle eviction leaves in place of the blocks it took."""
    return (f"[{dropped} earlier exchange(s) {_EVICTED_PHRASE}. "
            f"Your instructions and your latest results are intact; "
            f"re-read anything you still need.]")


# The floor under a cut exchange. Two thousand characters is about 500 tokens:
# enough for the seat's own last sentence and one result to survive as
# something to act on.
_MIN_EXCHANGE = 2000


def _exchange_cut(text: str, limit: int) -> str:
    """
    Cut a block of the latest exchange, saying so. The wake's own contract,
    with one difference: the notice is paid for out of the limit rather than
    added to it, so the block that comes back is inside the room it was given
    and `_fit` can promise a number a test can assert.
    """
    if len(text) <= limit:
        return text
    keep = limit
    for _ in range(4):
        note = chr(10) + cut_note(
            "this exchange", len(text) - keep, len(text), "characters",
            "Nothing returns an earlier turn. Call again what you still need.")
        if keep + len(note) <= limit:
            break
        keep = max(limit - len(note), 0)
    return text[:keep] + note


def _cap_exchange(transcript: list[str], budget: int) -> list[str]:
    """
    Cut the latest exchange when it alone will not fit.

    `_fit` keeps the first block and the last two, and capped only the first.
    The last two were neither capped nor summed, so the trim could not get
    under the budget when the latest exchange was itself over it -- and it did
    not try. Night 85 and night 86: 86 of 366 and 57 of 825 turns went over,
    and every session the server cut had an over-budget turn first.

    The two blocks are the seat's own reply and the results it asked for. They
    share what the rest of the transcript leaves, half each, and a block under
    its half keeps everything and lends the remainder to the other. Never below
    `_MIN_EXCHANGE`, because a notice alone tells a session nothing.

    Fewer than three blocks is not an exchange: at two, `transcript[-2:]` is
    the wake itself, which the cut above has already bounded.
    """
    if len(transcript) < 3:
        return transcript
    room = max(budget - sum(len(t) + 2 for t in transcript[:-2]), _MIN_EXCHANGE)
    reply, results = transcript[-2:]
    if len(reply) + len(results) + 4 <= room:
        return transcript
    share = max((room - 4) // 2, _MIN_EXCHANGE // 2)
    if len(reply) <= share:
        reply_room, results_room = len(reply), room - 4 - len(reply)
    elif len(results) <= share:
        reply_room, results_room = room - 4 - len(results), len(results)
    else:
        reply_room = results_room = share
    return transcript[:-2] + [_exchange_cut(reply, reply_room),
                              _exchange_cut(results, results_room)]


def _cap_tail_reply(transcript: list[str], kinds: list[str], budget: int,
                    note_room: int, native: bool = False) -> list[str]:
    """
    Cut the latest reply when the tail leaves no middle unit any room.

    Night 99, s132, turn 13: a 30,894-character reply against a 26,309
    budget left negative room, and every middle block went. Turns 15 to 18
    then read four spans again (frame 108). `_cap_exchange` cut the tail only
    after the middle was gone.

    The cap cuts the reply only. The runner sizes the results block, and its
    cut names the call that fetches the rest (frame 108, revision 2). The
    tail gets a third of the budget at least, and a small wake lends it the
    part of the wake's two thirds that the wake does not use. The results
    are paid for out of that room, and the reply keeps the rest.

    The cap fires only when no middle unit can fit beside the tail as it
    stands. A tail that leaves room for one unit is not this defect, and
    the packing handles it as before. The cut lands only when a trial pack
    of the cut transcript keeps a middle results block.

    The cut reply starts with its stub. `_exchange_cut` keeps a prefix, so a
    call after the prose or a call with a large argument fell outside it.
    The reply then stubbed to no call on a later turn (the diff review of
    frame 108's pass 1, finding 2). A reply that starts with its stub needs
    no prefix. A stub that takes half the room or more, and a stub whose
    call line does not parse again, fall back to the plain cut. Frame 117
    holds the second case.
    """
    middle, middle_kinds = transcript[1:-2], kinds[1:-2]
    smallest = _smallest_unit(middle, middle_kinds, native)
    if smallest is None:
        return transcript
    fixed = len(transcript[0]) + 2 + sum(len(t) + 2 for t in transcript[-2:])
    # The packing charges the notice only when a block drops. A middle that
    # fits whole once tier 1 stubs its replies drops nothing, so the tail
    # takes no cut (the diff review of frame 108's pass 2, finding 1).
    if _NOTICE not in middle_kinds and fixed + sum(
            _unit_chars(block, kind, native)
            for block, kind in zip(middle, middle_kinds)) <= budget:
        return transcript
    if budget - fixed - note_room >= smallest:
        return transcript
    third = budget // 3
    tail_room = max(third, budget - (len(transcript[0]) + 2) - third)
    reply, results = transcript[-2:]
    reply_room = max(tail_room - 4 - len(results), _MIN_EXCHANGE // 2)
    if len(reply) <= reply_room:
        return transcript
    stub = _stub(reply, native)
    plain = _exchange_cut(reply, reply_room)
    # The plain cut serves when its own stub still lists every call: a call
    # inside the kept prefix showed twice under a stub prefix (the diff
    # review of frame 108's pass 3, finding 2).
    if (stub == _STUB_EMPTY or reply.startswith(stub)
            or _stub(plain, native) == stub
            or len(stub) + 1 >= reply_room // 2
            or _stub(stub, native) != stub):
        cut = plain
    else:
        cut = stub + chr(10) + _exchange_cut(
            reply, max(reply_room - len(stub) - 1, 0))
    # The cut lands only when a trial pack keeps a middle read. A test on
    # the smallest unit was not enough, because the packing drops oldest
    # first: in 362 of 2,131 cuts the reply was cut and the middle still
    # emptied (the diff review of frame 108's pass 3, finding 1). The trial
    # runs `_pack`, never `_fit`, so the cap does not recurse. A runner note
    # alone is no read, so it buys no cut (frame 119, pass 4).
    capped = transcript[:-2] + [cut, results]
    trial, trial_kinds = _pack(capped, kinds, budget, note_room, native)
    if not _reads_in(trial[1:-2], trial_kinds[1:-2]):
        return transcript
    return capped


def _smallest_unit(middle: list[str], kinds: list[str],
                   native: bool = False) -> int | None:
    """
    The fewest characters one middle unit can keep after the packing.

    The packing never keeps a reply alone beside nothing. `drop()` takes a
    results block with the reply of its turn, and tier 4 drops the rest. So
    the unit is a results block plus the stub of its reply. Notices are not
    units, because the packing charges the notice apart (the diff review of
    frame 108's pass 1, finding 1).

    A reply with no results after it is no unit. Its stub passed for room,
    the cap stayed off, and the middle kept stubs and no read (frame 119's
    diff review, finding 3).
    """
    units = []
    for i, (block, kind) in enumerate(zip(middle, kinds)):
        if kind == _RESULTS:
            size = len(block) + 2
            if i > 0 and kinds[i - 1] == _REPLY:
                size += _unit_chars(middle[i - 1], _REPLY, native)
            units.append(size)
    return min(units) if units else None


def _unit_chars(block: str, kind: str, native: bool = False) -> int:
    """
    The characters one middle block holds after tier 1, its separator
    included. Tier 1 puts a stub in place of a reply only when the stub is
    shorter (the diff review of frame 108's pass 2, finding 2).
    """
    if kind == _REPLY:
        return min(len(block), len(_stub(block, native))) + 2
    return len(block) + 2


def _fit_budget(num_ctx: int, system_chars: int) -> int:
    """
    The characters a session's transcript may hold, for `_fit`.

    Half the window, because half is what a session gets when it overflows:
    ollama collapses a prompt over `num_ctx` to `num_ctx / 2 + 2` and keeps the
    tail (finding 79). The old budget was two thirds of the window at four
    characters to the token, about 8,250 tokens on a 12,288 window. That is
    above the 6,146 the records plan against, so `_fit` never fired on a wake
    the server would cut (the diff review of 8ebbae1). The system prompt is
    charged against the same budget, and 3.97 characters to the token is the
    measured ratio for these models.
    """
    return max(2000, int(num_ctx / 2 * 3.97) - system_chars)


# The kind of each transcript block. The runner names the kind when it
# appends the block, and `_fit` reads the kind. Parity by position is false
# after the first eviction: night 99, s132, held a results block after the
# notice at turns 9, 10, 11 and 13 (frame 100's design review).
_WAKE, _REPLY, _RESULTS, _NOTICE = "wake", "reply", "results", "notice"

# A stub keeps each call line of an old reply, cut to this length. Night 99,
# s132: replies of 7,373 to 21,121 characters took the room, and the source
# results of 2,186 to 8,642 characters went (frame 100).
_STUB_CALL_CHARS = 200
_STUB_EMPTY = "[your reply of an earlier turn]"

# A `code.source` result as the runner writes it into a results block, served
# the first time or served again after an eviction. `_as_block` puts the
# scalars on the head line, so path, start and end are legible (frame 100).
_SOURCE_RESULT = re.compile(
    r"^OK code\.source -> (?:the earlier answer was .*?ran again: )?"
    r"path: ([^,\n]+), start: (\d+), end: (\d+)", re.MULTILINE)
# `_render` names the line where it cut a span. Night 99, s132, turn 12: the
# read of 0-688 was cut at line 457, so it did not hold 457-688 (frame 100).
_SOURCE_CUT_AT = re.compile(r"The cut fell at line (\d+): code\.source\(")
# `_exchange_cut` names no line, so a block it cut covers no span.
_EXCHANGE_CUT = "CUT this exchange"
# The repeat lines of the runner. They point at an earlier answer and hold
# none, so a block of them only is no read (frame 119, pass 4).
_PUSHED_REPEAT = "was run for you before you started."
_ASKED_REPEAT = "unchanged since you asked earlier this session."
# The result line of a call that holds an answer, as the runner writes it.
_OK_LINE = re.compile(
    r"^OK [\w.]+ -> (?!" + re.escape(_PUSHED_REPEAT) + "|"
    + re.escape(_ASKED_REPEAT) + ")", re.MULTILINE)


def _reads_in(blocks: list[str], kinds: list[str]) -> bool:
    """
    Whether a results block among `blocks` holds an answer of a call.

    Night 115, s73: the only middle results block was the runner's reply-cut
    note, and the wake lost 4,707 characters of source for it (frame 119,
    pass 3). A block of repeat lines only holds no answer either (pass 4).
    """
    return any(kind == _RESULTS and _OK_LINE.search(block)
               for block, kind in zip(blocks, kinds))


def _append(transcript: list[str], kinds: list[str], kind: str,
            block: str) -> None:
    """
    Append one block and its kind together. Every append goes through here,
    so a new append site cannot put the two lists out of step (frame 100).
    """
    transcript.append(block)
    kinds.append(kind)


def _stub(reply: str, native: bool = False) -> str:
    """
    An old reply as its call lines only. The results of the turn say what ran,
    so the call lines are enough to read them by (frame 100, night 99, s132).

    The calls are the ones the parser finds, because the parser finds `TOOL:`
    anywhere in a line. A call in a list item or in backticks ran, so its
    stub keeps it (the diff review of frame 100's pass 1, finding 2). Each
    call is its first line, cut to `_STUB_CALL_CHARS`.

    A native session also keeps the `name(...)` lines that
    `_with_native_lines` wrote. Without them an old native reply became
    `_STUB_EMPTY`, and the history again showed only results (frame 323).
    A text session never reads such a line, so its stubs do not change.
    """
    calls = [(f"{toolproto.MARKER} {call.raw}".splitlines() or [""])[0]
             [:_STUB_CALL_CHARS]
             for call in toolproto.extract(reply)
             if isinstance(call, toolproto.ToolCall)]
    if native:
        calls += [line[:_STUB_CALL_CHARS] for line in reply.splitlines()
                  if _NATIVE_LINE.match(line)]
    return chr(10).join(calls) or _STUB_EMPTY


# A line that `_with_native_lines` writes: a dotted name, then its brackets.
_NATIVE_LINE = re.compile(r"[a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]*\(")


def _source_spans(block: str) -> list[tuple[str, int, int]]:
    """
    The (path, start, end) of each `code.source` result in a results block.
    The end is the line where `_render` cut the span, when it cut one.

    A result with no `[text]` marker holds no source. `_render` cuts before
    the marker when a long `defs` head takes the cap, and the head still
    names the whole span (the diff review of frame 100's pass 1, finding 1).
    """
    found = list(_SOURCE_RESULT.finditer(block))
    spans = []
    for i, match in enumerate(found):
        stop = found[i + 1].start() if i + 1 < len(found) else len(block)
        if block.find("[text]", match.end(), stop) < 0:
            continue
        end = int(match.group(3))
        cut = _SOURCE_CUT_AT.search(block, match.end(), stop)
        if cut:
            end = min(end, int(cut.group(1)))
        spans.append((match.group(1).strip(), int(match.group(2)), end))
    return spans


def _fit(transcript: list[str], kinds: list[str],
         budget: int, native: bool = False) -> tuple[list[str], list[str]]:
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

    The middle goes by kind, in tiers, and oldest first inside a tier (frame
    100). Age alone dropped the reads and kept the replies. Night 99, s132:
    the replies took the room, and the seat read span 346-390 eight times.

    1. An old reply becomes a stub of its call lines.
    2. A results block goes when newer blocks hold all of its source spans.
       Then the other results blocks go, except the newest read of each
       distinct span.
    3. The newest read of each distinct span goes, oldest first.
    4. Whatever is left goes, so the budget holds.

    A results block that goes takes the reply of its turn with it.

    `kinds` names the kind of each block, and the two lists come back aligned.
    """
    if len(kinds) != len(transcript):
        raise ValueError(f"{len(kinds)} kinds for {len(transcript)} blocks")
    if sum(len(t) + 2 for t in transcript) <= budget:
        return transcript, kinds

    # The wake is kept whole *unless it alone will not fit*, which it can be:
    # the pushed working set lives in it, and on a 1,357-grain area that was
    # 198,366 characters. Protecting it unconditionally meant the one block that
    # could overflow the window on its own was the one block never trimmed.
    # Two thirds of the budget for the wake, not half: the pushed working set
    # is the part of the prompt the session was woken to read, and a source
    # push the size the area deserves is most of it.
    #
    # The share yields to half when two thirds keep no middle read. Night 113,
    # s153, turn 16: the wake at two thirds and a third for the tail left the
    # middle no room, and the seat read utils.py again (frame 119). Both
    # shares stay fixed from the budget, because frame 108 ruled a share sized
    # from the middle circular. Trial packs only choose between them. A cut
    # that keeps no more reads loses wake for nothing, and the stored wake
    # never grows back (frame 119's diff review, finding 1). So the wake takes
    # half only when two thirds keep no read and half keeps one. A first turn
    # keeps two thirds, the case of b8c18fe.
    # A read is what `_reads_in` names.
    def keeps_a_read(room: int) -> bool:
        trial = [_render_cut(transcript[0], room)] + transcript[1:]
        trial_note = len(_dropped_note(len(trial))) + 2
        trial = _cap_tail_reply(trial, kinds, budget, trial_note, native)
        out, trial_kinds = _pack(trial, kinds, budget, trial_note, native)
        return _reads_in(out[1:-2], trial_kinds[1:-2])

    wake_room = (budget * 2) // 3
    if (len(transcript) >= 4 and _reads_in(transcript[1:-2], kinds[1:-2])
            and len(transcript[0]) > budget // 2
            and not keeps_a_read(wake_room) and keeps_a_read(budget // 2)):
        wake_room = budget // 2
    if len(transcript[0]) > wake_room:
        transcript = [_render_cut(transcript[0], wake_room)] + transcript[1:]

    # The cut above runs on every turn. It once sat behind an early return on
    # a transcript of fewer than four blocks, and turns one to three hold one
    # to three blocks -- so an oversized wake was never cut at all. Night 85
    # (2026-09-18): two landing sessions were sent a 17,220 token wake into a
    # 12,288 window, ollama kept the tail, and each seat answered as a generic
    # assistant with no tool call. Only the middle eviction below needs four.
    if len(transcript) < 4:
        return _cap_exchange(transcript, budget), kinds

    # The notice is part of the prompt, so the packing pays for it. Unreserved,
    # the transcript came back up to 116 characters over the budget and
    # `_cap_exchange` read the deficit as room it could lend (the diff review
    # of 34c3e72, F5). Reserved at the longest it can be, which is the notice
    # for every block dropping.
    note_room = len(_dropped_note(len(transcript))) + 2
    transcript = _cap_tail_reply(transcript, kinds, budget, note_room,
                                 native)
    out, out_kinds = _pack(transcript, kinds, budget, note_room, native)
    return _cap_exchange(out, budget), out_kinds


def _pack(transcript: list[str], kinds: list[str], budget: int,
          note_room: int, native: bool = False) -> tuple[list[str], list[str]]:
    """
    Pack the middle by the tiers of `_fit`, and keep the head and the tail.

    `_fit` packs with this function, and so does the trial of
    `_cap_tail_reply`. One function, so the trial and the real pack cannot
    drift (the diff review of frame 108's pass 3, finding 1). The caller
    applies `_cap_exchange` to the result.
    """
    head, tail = transcript[:1], transcript[-2:]
    # Each middle block as [text, kind, kept]. A stub changes the text, and
    # a drop clears `kept`.
    middle = [[block, kind, True]
              for block, kind in zip(transcript[1:-2], kinds[1:-2])]
    fixed = sum(len(t) + 2 for t in head + tail)
    old_notices = sum(1 for _, kind, _ in middle if kind == _NOTICE)
    dropped = 0

    def over() -> bool:
        held = sum(len(block) + 2 for block, kind, kept in middle
                   if kept and kind != _NOTICE)
        noted = note_room if (dropped or old_notices) else 0
        return fixed + held + noted > budget

    def drop(at: int) -> None:
        # A results block takes the reply of its turn with it. A stub left
        # alone shows a call with no answer, and the seat can then believe a
        # refused write landed (the diff review of frame 100's pass 1,
        # finding 3). N counts both blocks.
        nonlocal dropped
        middle[at][2] = False
        dropped += 1
        if (middle[at][1] == _RESULTS and at > 0
                and middle[at - 1][1] == _REPLY and middle[at - 1][2]):
            middle[at - 1][2] = False
            dropped += 1

    # Tier 1: old replies become stubs. A stub drops no block, so N stays.
    for entry in middle:
        if not over():
            break
        if entry[1] == _REPLY:
            stub = _stub(entry[0], native)
            if len(stub) < len(entry[0]):
                entry[0] = stub

    # The results blocks the eviction can still see, oldest first. The tail's
    # results stay, so they count as the newer reads.
    def reads() -> list[tuple[int, list[tuple[str, int, int]], bool]]:
        found = [(i, _source_spans(block), _EXCHANGE_CUT not in block)
                 for i, (block, kind, kept) in enumerate(middle)
                 if kept and kind == _RESULTS]
        found += [(len(middle) + i, _source_spans(block),
                   _EXCHANGE_CUT not in block)
                  for i, (block, kind) in enumerate(zip(tail, kinds[-2:]))
                  if kind == _RESULTS]
        return found

    def covered(at: int, spans: list[tuple[str, int, int]]) -> bool:
        newer = [span for i, held, whole in reads() if i > at and whole
                 for span in held]
        return bool(spans) and all(
            any(path == p and start >= s and end <= e for p, s, e in newer)
            for path, start, end in spans)

    # Tier 2, first half: a span that a newer block holds is a copy. Night
    # 99, s132, held span 346-390 more than once, and a distinct span went
    # first (frame 100's design review).
    for i, entry in enumerate(middle):
        if not over():
            break
        if entry[2] and entry[1] == _RESULTS and covered(
                i, _source_spans(entry[0])):
            drop(i)

    # The newest read of each distinct span, which tier 3 drops last. A pin
    # per path let one file's distinct spans go by age. Night 99, s132, turn
    # 8: every read held a distinct span, so the pins were all of them, and
    # spans 390-450 and 450-688 went by age under both rules. The re-reads
    # at turns 16 to 18 follow turn 13, whose 30,894-character reply in the
    # last two blocks was larger than the budget, so the whole middle went.
    # `_cap_tail_reply` above saves those reads (frame 108, after the diff
    # review of frame 100's pass 2, finding 1).
    newest: dict[tuple[str, int, int], int] = {}
    for i, held, _ in reads():
        for span in held:
            newest[span] = i
    pinned = set(newest.values())

    # Tier 2, second half, and tier 3. Tier 3 drops the pinned reads, oldest
    # first.
    for keep_pinned in (True, False):
        for i, entry in enumerate(middle):
            if not over():
                break
            if (entry[2] and entry[1] == _RESULTS
                    and (i not in pinned or not keep_pinned)):
                drop(i)

    # Tier 4: the stubs and any block of another kind, so the budget holds.
    for i, entry in enumerate(middle):
        if not over():
            break
        if entry[2] and entry[1] != _NOTICE:
            drop(i)

    if not dropped:
        kept = [(block, kind) for block, kind, keep in middle if keep]
    else:
        # An earlier notice counts as a dropped block, as before frame 100.
        kept = ([(_dropped_note(dropped + old_notices), _NOTICE)]
                + [(block, kind) for block, kind, keep in middle
                   if keep and kind != _NOTICE])
    out = head + [block for block, _ in kept] + tail
    out_kinds = kinds[:1] + [kind for _, kind in kept] + kinds[-2:]
    return out, out_kinds


def _prompt_overrun(system: str, user: str, budget: int, num_ctx: int) -> str:
    """
    The assembled prompt against its budget, measured before the send.

    Nothing measured the whole prompt on the way out. The one whole-prompt
    number arrived with the reply, from `truncated`, which only `OllamaBackend`
    assigns -- so the check was dead for every replayed case, and frame 43
    shipped that fault once already (frame 46's design review, 2026-09-20).
    This runs above every backend, so a cassette exercises it.

    Two limits, and the smaller binds. The budget is
    `_fit_budget(num_ctx, len(system))`, which charged the system prompt
    already, so the whole prompt's room is that budget plus the system prompt,
    and that is `_fit`'s promise about the string the backend receives. It is
    also the only limit that `len(system)` cancels out of, which made the
    measurement blind at the floor: `max(2000, ...)` holds the budget up when
    the system prompt is large, and `len(system) + 2000` can be more than the
    window's half (the diff review of 0cc624b, finding 3). Half the window at
    3.97 characters to the token is the other limit, and it binds there.

    The promise is a precondition, not a theorem. A fuzz of 4,000 transcripts
    broke it 1,540 times: `_cap_exchange` returns a two-block transcript
    untouched, and at the `max(2000, ...)` floor it lends room the budget does
    not hold. The runner reaches neither shape today, because it appends a
    reply and a results block on every turn.

    Measure only. Line 3 of frame 46 owns the wording of a cut, so this names
    the largest part and how far past the budget the prompt went.
    """
    limit = min(len(system) + budget, int(num_ctx / 2 * 3.97))
    whole = len(system) + len(user)
    if whole <= limit:
        return ""
    part, size = (("the system prompt", len(system)) if len(system) >= len(user)
                  else ("the transcript", len(user)))
    return (f"prompt over budget by {whole - limit} characters: {part} is the "
            f"largest part at {size}")


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
    # A result the seat asked for has no next range unless it is a span, so the
    # sentence says what this result can do and nothing more.
    call = "Nothing returns the rest of this result. Ask for a narrower part."
    # A source span cut mid-function: say the line the cut fell at and the
    # call that fetches the rest. Night 74 (2026-09-15, finding 77): the 9B
    # read version_option (207 lines, 8692 characters) six times, saw the
    # same first 6000 each time, and never reached the line it had to
    # change. "Ask for the next range" without the number is no range.
    if isinstance(result, dict) and "text" in result and isinstance(result.get("start"), int):
        marker = "[text]" + chr(10)
        at = text.find(marker)
        if 0 <= at < limit:
            emitted = text[at + len(marker):limit].count(chr(10))
            cut_line = result["start"] + emitted
            call = (f"The cut fell at line {cut_line}: "
                    f"code.source(path='{result.get('path')}', start={cut_line}, "
                    f"end={result.get('end')}) returns the rest.")
    return text[:limit] + chr(10) + cut_note(
        "the result", len(text) - limit, len(text), "characters", call)


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


def disputed_paths(conn: sqlite3.Connection, ref: str,
                   paths: list[str]) -> list[str]:
    """
    The paths of a prediction that his ruling on `ref` takes off.

    A path is disputed when his newest landed ruling on `ref` has the act
    `remove` with that path as its target. A ruling with no act disputes
    nothing, so the guess stays whole and the seat reads his words. Night
    133 to 156 read the "no" words of his reply by twelve patterns, and
    each review found a form they missed (frame 298). The record replaces
    them (the seam design, 3.3, P10).
    """
    from ..roles.principal import granted

    return [p for p in paths if granted(conn, ref, "remove", p)]


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
    # is the landed verdict naming it, the latest wins, and its entry is the
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
    # `principal_verdict` in the message; this is what makes that true. Relay
    # only, and only the rows this relay carries -- a ruling fans out one
    # relay per owner, and each owner sees its own.
    #
    # The whole chain, not one hop. A reply to a clarify is read and relayed
    # in the same Liaison session, so the relay's cause is the reply and the
    # ruling is one hop further up. Measured on night 84 (2026-09-17): every
    # relay m101 to m129 had the report as its cause, none carried a verdict,
    # and the Terminologist's `glossary.adopt` was refused for three sessions
    # in a row.
    #
    # The Terminologist's answer to the Tester walks the same chain. The
    # principal's words about a check ruled a criterion, the Terminologist
    # repaired it and answered with refs alone, and the Tester rewrote the
    # test from the criterion text in all 6 such wakes of night 145
    # (frame 213, route A). The ruling says the Tester rewrites the test
    # from the ruled words (ruled: Roman, 2026-10-08, the park ask is a page
    # with rows, point 2). No new edge: law 2 holds, the words arrive as
    # `principal_said` through the ruling's own chain.
    answered = (row["verb"] == "answer" and row["from_role"] == "terminologist"
                and wake.role == "tester")
    if (row["verb"] == "relay" or answered) and not ruling and row["cause_id"]:
        from ..roles.principal import chain_verdict

        found = chain_verdict(conn, row["cause_id"])
        carried = found[1] if found else {}
        mine = {r: v for r, v in carried.items() if r in out["refs"]}
        # A ruled test row travels as its criterion (frame 213, route B).
        # Its ruling keeps its own key, beside the criterion's own ruling.
        # Written over the criterion, an approve became a revise, and the
        # repair brief told the seat to rewrite approved words (the review
        # of f252df24, finding 1).
        tested = {}
        for r, v in carried.items():
            if v not in ("contest", "revise"):
                continue
            test = conn.execute("SELECT criterion_id FROM tests WHERE id = ?",
                                (r,)).fetchone()
            if test and test["criterion_id"] in out["refs"]:
                tested[r] = v
        if tested:
            out["principal_test_verdict"] = tested
        if mine:
            out["principal_verdict"] = mine
        if mine or tested:
            reason = entry_for(conn, found[0])
            if reason:
                out.setdefault("principal_said", reason)

    # Frame 317, pass 1b: a Tester answer resolves the tests of its own
    # batch only, the batch the session works in.
    wake_batch = None
    if wake.role == "tester" and wake.detail == "answer":
        from .loop import _batch_of

        wake_batch = _batch_of(conn, wake)
    resolved = _resolve_refs(conn, out["refs"], role=wake.role,
                             detail=wake.detail, batch_id=wake_batch)
    if resolved:
        out["resolved_refs"] = resolved
    # A ruling on a batch line corrects the prediction, so the Architect sees
    # the prediction it corrects. The brief says to drop a path the words
    # dispute and keep the others (frame 190's design, 2.2, the batch line,
    # point 6; frame 244's try 2, shape C).
    from .scheduler import batch_relay

    if row["verb"] == "relay" and batch_relay(conn, trigger):
        from .lifecycle import touch_set

        out["touch"] = {b: touch_set(conn, b) for b in out["refs"]}
        # The path his ruling removes leaves `expected`. In the interview
        # of the red re-annotate case, the seat kept `tests/test_defaults.py`
        # because `expected` listed it, and it said that list outweighed
        # `principal_said` (plans/frame190-interview.md, 2026-10-09).
        for b, touch in out["touch"].items():
            if not touch or out.get("principal_verdict", {}).get(b) not in (
                    "contest", "revise"):
                continue
            # `possible` too: after m85 the symbol the words called unrelated
            # stayed there, and run 4 wrote it back (the diff review of
            # 0ffc97b7, finding 5).
            disputed = disputed_paths(
                conn, b, touch.get("expected", []) + touch.get("possible", []))
            touch["disputed"] = disputed
            for key in ("expected", "possible"):
                touch[key] = [p for p in touch.get(key, []) if p not in disputed]
    # A ruling on a code line corrects the guess the principal read, as the
    # send door stamped it. The Architect sees the item, that set, and the
    # paths the words call wrong, the shape of the batch relay above (frame
    # 298's design, 3.4, point 6). A relay holds one item's key in practice,
    # so the first key's set is the one shown.
    from .scheduler import guess_relay

    if row["verb"] == "relay" and guess_relay(conn, trigger) and out["refs"]:
        key = out["refs"][0]
        item_id = key.split(":", 1)[1]
        item = conn.execute("SELECT id, text FROM items WHERE id = ?",
                            (item_id,)).fetchone()
        if item:
            out["item"] = {"id": item["id"], "text": item["text"]}
        shown_row = conn.execute("SELECT value FROM config WHERE key = ?",
                                 (f"guess_target:{row['cause_id']}",)).fetchone()
        try:
            shown = json.loads(shown_row["value"]) if shown_row else {}
        except (TypeError, ValueError):
            shown = {}
        target = shown.get(key) if isinstance(shown, dict) else None
        rows = conn.execute(
            "SELECT grain, grain_kind FROM touch_guesses WHERE item_id = ? "
            "AND item_ver = ? AND ruling_id = ? ORDER BY rowid",
            (item_id, target[0], target[1])).fetchall() if (
                isinstance(target, list) and len(target) == 2) else []
        paths = [r["grain"] for r in rows if r["grain_kind"] == "path"]
        symbols = [r["grain"] for r in rows if r["grain_kind"] == "symbol"]
        disputed: list[str] = []
        if out.get("principal_verdict", {}).get(key) in ("contest", "revise"):
            disputed = disputed_paths(conn, key, paths + symbols)
        out["guess"] = [p for p in paths + symbols if p not in disputed]
        out["disputed"] = disputed
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
                                        if r not in out.get("resolved_refs", {})],
                                 role=wake.role, detail=wake.detail,
                                 batch_id=wake_batch)
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
            # The answer is about the rows the door keyed on, the asker's
            # with the clarify's (frame 306, review 1, finding 3).
            about = (answer_about(conn, c["id"])
                     or json.loads(c["body_refs"] or "[]"))
            if not refs_here & set(about):
                continue
            reply = conn.execute(
                "SELECT id FROM messages WHERE from_role = 'principal' "
                "AND cause_id = ? ORDER BY seq DESC LIMIT 1", (c["id"],)).fetchone()
            if not reply:
                continue
            said = entry_for(conn, reply["id"])
            if said:
                prior.append({"question": c["body_text"], "principal_said": said,
                              "about": about})
        if prior:
            out["prior_answers"] = prior

    # Chat memory: a Liaison intake session sees the recent back-and-forth so
    # greetings and follow-ups are answered in context. This is the one place
    # where a role is deliberately given history; the no-memory rule still
    # holds for every other mode.
    if row["to_role"] == "liaison" and row["verb"] == "converse":
        out["recent_chat"] = _recent_chat(conn, trigger, page=row["cause_id"])
        # A request with no cause may follow up the current one. The seat
        # needs that request's statement id to copy into `supersedes` (frame
        # 193's design, 2.F.6). The door admits a ratified statement only, so
        # the wake offers no other (frame 193, pass 2b).
        if not row["cause_id"] and row["from_role"] == "principal":
            from ..roles.principal import ratified_request

            seq = conn.execute("SELECT seq FROM messages WHERE id = ?",
                               (trigger,)).fetchone()["seq"]
            cur = ratified_request(conn, before_seq=seq)
            # The relation says what the block is. Night 138's s270 and s353
            # read the block as the request the new words belong to, and
            # both named it as the cause in their interviews (frame 193's
            # design, 2.G.1).
            if cur:
                out["current_request"] = {"statement": cur["statements"][0],
                                          "text": cur["texts"][0],
                                          "relation": CURRENT_REQUEST_RELATION}

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
            from .scheduler import park_ask_batch

            park = bool(clarify and park_ask_batch(clarify["id"]))
            if clarify and clarify["verb"] == "clarify" and not park:
                answering: dict[str, Any] = {"question": clarify["body_text"]}
                asker = conn.execute(
                    "SELECT from_role, body_refs FROM messages WHERE id = ?",
                    (clarify["cause_id"],)).fetchone() if clarify["cause_id"] else None
                if asker:
                    answering["asked_by"] = asker["from_role"]
                    answering["about"] = answer_about(conn, clarify["id"]) or []
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
                    resolved_row["table"] = _label(conn, ref, resolved_row)
                answering["about_rows"] = about_rows
                out["answering"] = answering
            # A reply to a page. The Liaison reads the words against the
            # page and records the ruling. It needs the page as the person
            # saw it, the numbered lines in order, the words, and what was
            # said back and forth on this page before.
            if clarify and (clarify["verb"] in ("confirm", "present") or park):
                from ..roles.principal import page_ask, render_page, seen_order

                page_refs = json.loads(clarify["body_refs"] or "[]")
                # A park page numbers the item and its criteria, so the
                # ruling lands on its rows as on every present (ruled: Roman,
                # 2026-10-08, the park ask is a page with rows). The returned
                # line is the principal's, not the seat's (frame 267, ruled
                # by the holding session at review 1).
                page = render_page(conn, clarify["verb"], page_refs,
                                   clarify["body_text"], ask_id=clarify["id"],
                                   returned=False)[0]
                # Each line names the row he saw on it at this reply (fact
                # F28).
                order = seen_order(conn, trigger, page_ask(clarify))
                # No page id here. `_recent_chat` already names another
                # page in words, "row <ref> of page <id>", and a reply to
                # this page keeps its line numbers, so the seat tells the two
                # apart without an id (frame 272, review 1, finding 2, read
                # again at the gate of d6a36081). A `page_id` key in this
                # block costs one run of five on L1-LI-a-correction-in-a-
                # sentence-contests-the-line-it-is-about on qwen3:8b: 1 of 5
                # with the key and 2 of 5 without, on the same brief and the
                # same load, each twice; the same text read 3 of 5 on the
                # loads before (measured 2026-10-23 19:40 to 19:55, register
                # `case_runs`). The case sits at the model's floor.
                landing: dict[str, Any] = {
                    "page_kind": clarify["verb"],
                    "page": page,
                    "lines": {str(i + 1): ref for i, ref in enumerate(order)},
                    "reply": row["body_text"] or "",
                }
                # The rows, while they fit. A present of 77 lines sent every
                # row twice -- `resolved_refs` and `landing.line_rows` were the
                # same 21,402 characters -- in a 17,220 token wake against a
                # 12,288 window (measured on night 85, 2026-09-18). Ollama
                # collapses an oversized prompt to half the window and keeps
                # the tail, so the brief at the front is what dies and the seat
                # answers as a generic assistant.
                #
                # Cut to index depth rather than dropped, which is the rule
                # every other read here keeps. The page carries the prose of
                # every line already, so what stays is the id and the kind of
                # row each line is, in one map. A seat that needs a whole row
                # calls `rulings.line`. Night 85's own 79-line wake measures
                # 5,593 tokens this way, against 17,220.
                line_rows = _resolve_refs(conn, order)
                for ref, resolved_row in line_rows.items():
                    resolved_row["table"] = _label(conn, ref, resolved_row)
                # A row he saw can leave the tables after his reply. The
                # line names it, so the Liaison rules the other lines (the
                # F26 review, finding 1). Only a page with such a line gets
                # the key, so no recorded prompt changes.
                from ..roles.principal import READING_REF, ruled_ref_home

                gone = {str(i + 1): (
                    f"no table holds {ref} now. The line takes no ruling, and "
                    f"a ruling on it lands as a fault")
                    for i, ref in enumerate(order)
                    if not str(ref).startswith(READING_REF)
                    and ruled_ref_home(conn, ref) is None}
                if gone:
                    landing["gone_lines"] = gone
                # A read-back line names the rows of an earlier reply by
                # their ids here, so the seat can rule a row his words
                # correct. The page he reads shows no id (the review of pass
                # 5b, finding 6). Only a page with the line gets the key.
                from ..roles.principal import READING_REF, read_back_rows

                back = {str(i + 1): [
                    {k: r[k] for k in ("ref", "line", "verdict", "act", "target")}
                    for r in read_back_rows(conn, ref[len(READING_REF):])]
                    for i, ref in enumerate(order)
                    if str(ref).startswith(READING_REF)}
                if back:
                    landing["read_back"] = back
                # Both copies, measured together. The gate read `line_rows`
                # alone, which is built from the page's rendered order, while
                # `resolved_refs` is built from the wake's refs -- always the
                # larger set. A present of night 85's refs plus the zero
                # constraint renders no numbered line at all, so `line_rows`
                # was 2 characters, the gate said "fits", and 21,855
                # characters of `resolved_refs` travelled: 7,949 tokens
                # against a 6,146 budget (the diff review of 8ebbae1).
                also = json.dumps(out.get("resolved_refs") or {}, default=str)
                both = len(json.dumps(line_rows, default=str)) + len(also)
                if both <= LANDING_ROWS_CHARS:
                    landing["line_rows"] = line_rows
                    fits = True
                else:
                    fits = False
                    landing["lines"] = {
                        str(i + 1): f"{ref} ({' and '.join(tables_of(conn, ref)) or 'row'})"
                        for i, ref in enumerate(order)}
                    dropped = len(set(order) | set(out.get("resolved_refs") or {}))
                    # Not `cut_note` yet. This string is inside a recorded
                    # prompt, so one wording here costs a re-record:
                    # `L1-LI-a-long-page-is-ruled-without-the-rows` went stale
                    # on it (frame 46, line 3, 2026-09-20). It already names
                    # `rulings.line`, so the seat has its call.
                    landing["rows_not_shown"] = (
                        f"the {dropped} rows behind this page do not fit this "
                        f"window. Every line is on the page. "
                        f"`rulings.line` reads the row behind one line")
                # The Liaison's own questions under the principal's replies
                # travel too, marked asked, as `recent_chat` marks them.
                # Night 135's s224 saw four answers and no question, and
                # asked the answered question a fourth time (frame 142,
                # night 135's read, fix 5).
                # His answers read through `said`. A clarify answer lands
                # with no `body_text`, and night 172's walls hid it (W7).
                from ..roles.principal import said as his_words

                earlier = []
                for r in conn.execute(
                        "SELECT id, from_role, body_text FROM messages "
                        "WHERE ((cause_id = ? AND verb = 'converse' AND id != ?) "
                        "  OR (from_role = 'liaison' AND to_role = 'principal' "
                        "      AND verb IN ('clarify', 'converse') AND cause_id IN "
                        "      (SELECT id FROM messages WHERE cause_id = ? "
                        "       AND from_role = 'principal'))) "
                        "ORDER BY seq",
                        (clarify["id"], row["id"], clarify["id"])):
                    text = (his_words(conn, r["id"]) or None
                            if r["from_role"] == "principal" else r["body_text"])
                    if text is None:
                        continue
                    turn = {"from_role": r["from_role"], "body_text": text}
                    if turn["from_role"] == "liaison":
                        turn["asked"] = True
                    earlier.append(turn)
                if earlier:
                    landing["earlier_exchange"] = earlier
                out["landing"] = landing
                # The words live in `landing.reply`, once. Beside a field
                # named `asks`, both 8B models answered the "question" by
                # sending the words back (2026-09-10, 5/5).
                out.pop("asks", None)
                # The same rows a second time, under the wake's own key. They
                # stay while both copies together fit. Above that they are the
                # 21,402 characters that killed night 85, and a live seat
                # ruled all 77 lines correctly without them (the diff review
                # of 8ebbae1, qwen3:8b at num_ctx 12288, 5,565 tokens).
                if not fits:
                    out.pop("resolved_refs", None)
                    # And the ids a third time. `landing.lines` numbers the
                    # same 79 ids, which is the form the ruling is written in.
                    out.pop("refs", None)

    # Signoff disclosure (ruled 2026-09-03): the principal gates what an item
    # says and cannot gate what is absent, so the absence is computed here and
    # handed to the presenter. A ratified statement no item reflects is a
    # dropped want vanishing through slicing with no trace -- the one gap the
    # signoff reader cannot see from the items alone. Mechanics locate it;
    # the present carries it; the principal rules on it.
    if row["to_role"] == "liaison" and row["verb"] == "submit":
        from ..roles.principal import uncovered_statements

        uncovered = uncovered_statements(conn)
        if uncovered:
            out["uncovered_statements"] = uncovered

    return out


def _resolve_contest(conn: sqlite3.Connection, item: str) -> dict[str, Any]:
    """
    The ruling that contested `item`, and the principal's reason for it.

    The ruling is a landed row of `ruled_refs_live` on `item`. An item can
    be contested more than once -- amended, re-presented, contested again
    -- so the latest landed ruling is the one that stands. Nothing
    contested it: nothing to say, and the owner is woken with the item alone,
    as before. The row is the record, so the `verdict:` map in config is not
    read (the seam design, 3.4; the review of pass 2).
    """
    from ..roles.principal import entry_for, ruled

    # law 9: a revise is an amendment, so it wakes the owner with the words
    # A revise carries the principal's replacement words, so it wakes the
    # owner as a contest does. Read for `contest` only, night 136's revise
    # of the confirm item reached the Vision Keeper with the item alone
    # (frame 190's design, 2.2.2).
    for r in reversed(ruled(conn, [item])):
        if r["verdict"] not in ("contest", "revise"):
            continue
        mid = r["verdict_id"] or r["reply_id"]
        out: dict[str, Any] = {"refs": [item],
                               "principal_verdict": {item: r["verdict"]}}
        reason = entry_for(conn, mid) if mid else ""
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


def _page_named_lines(text: str, page_id: str, order: list[str]) -> str:
    """`text` with each line reference of page `page_id` named by its row.

    "Line 2" becomes "row <ref> of page <page_id>". A number past the page
    stays a line, as "line 9 of page <page_id>".
    """
    from ..roles.api import _line_reading

    def named(ref) -> str:
        parts = [f"row {order[n - 1]}" if 1 <= n <= len(order) else f"line {n}"
                 for n in sorted(ref.lines)]
        said = (", ".join(parts[:-1]) + " and " + parts[-1]
                if len(parts) > 1 else parts[0])
        said += f" of page {page_id}"
        return said[0].upper() + said[1:] if ref.text[0].isupper() else said

    # The line parser reads by sentence: a bare "3 is wrong" counts at a
    # sentence start only (frame 305, review 1, finding 1).
    out, at = [], 0
    for ref in _line_reading(text, len(order)).refs:
        out += [text[at:ref.start], named(ref)]
        at = ref.end
    return "".join(out) + text[at:]


def _recent_chat(conn: sqlite3.Connection, current_msg_id: str,
                 limit: int = 8, page: str | None = None) -> list[dict[str, Any]]:
    """Recent principal/liaison converse turns, newest last, excluding the wake.

    `page` is the page the wake answers. A principal reply names the page it
    answered. Its line numbers name rows of that page when the page is not
    `page`.
    """
    # Questions count as turns. This selected `converse` alone, so Liaison
    # could not see what it had already asked. A role with no memory, shown
    # the answer but not the question, cannot tell the ground has moved.
    # `interrupt_cap` says never repeat and always reframe. That needs the
    # last question in view.
    #
    # A principal turn with no `body_text` is read from its entry. The walk
    # and the agent principal write the words as an entry alone, so night
    # 132's s220 never saw e_p4, the same sentence one turn before (frame
    # 142's design, 2.C, point 7).
    #
    # A reply's line numbers belong to the page it answered. Night 159's s239
    # read m106's "Line 1", which answered page m105, as a fault of page
    # m116. The row id alone is not enough: m51 of night 158 faulted the
    # guess line of m50, and m89 shows that guess as line 2 too (frame 272;
    # `plans/frame305-interview.md`, section 6).
    from ..roles.api import message_entry
    from ..roles.principal import seen_order
    from .db import PAGE_VERBS

    out: list[dict[str, Any]] = []
    for r in conn.execute(
            "SELECT id, from_role, verb, body_text, body_refs, cause_id FROM messages "
            "WHERE verb IN ('converse', 'clarify') "
            "  AND from_role IN ('principal', 'liaison') "
            "  AND to_role IN ('principal', 'liaison') "
            "  AND id != ? "
            "ORDER BY seq DESC", (current_msg_id,)):
        text = r["body_text"] or ""
        if not text and r["from_role"] == "principal":
            text = message_entry(conn, r)[1]
        if not text:
            continue
        turn: dict[str, Any] = {"from": r["from_role"]}
        answered = conn.execute(
            "SELECT id, verb, body_text, body_refs FROM messages WHERE id = ? "
            f"AND to_role = 'principal' AND verb IN ({','.join('?' * len(PAGE_VERBS))})",
            (r["cause_id"], *PAGE_VERBS)).fetchone() if (
                r["from_role"] == "principal" and r["cause_id"]) else None
        if answered:
            turn["page"] = answered["id"]
            if answered["id"] != page:
                # The order he saw at this reply, by the one reader (fact
                # F28). A render reads today's rows, and 73 of 693 rows named
                # on nights 158 and 159 were not the row he saw (frame 272,
                # review 1, finding 1). A reply with no record keeps his
                # numbers, so the reader takes the record only.
                order = seen_order(conn, r["id"], None)
                if order:
                    text = _page_named_lines(text, answered["id"], order)
        turn["text"] = text
        out.append(turn | ({"asked": True} if r["verb"] == "clarify" else {}))
        if len(out) >= limit:
            break
    return list(reversed(out))


def _answer_cause_line(conn: sqlite3.Connection, wake) -> str:
    """
    The line that names what an answer answers, or "".

    Design 200 pass 2b: interviewed in its context, the s282 case's seat did
    not see its own escalation, so the brief's wordless-answer branch had no
    fact in front of it (`plans/frame200-interviews.md`). Only an answer to
    the woken role's own challenge or escalation gets the line, so no other
    wake's prompt moves.
    """
    if wake.detail != "answer" or not wake.message_id:
        return ""
    row = conn.execute(
        "SELECT q.id, q.verb, q.body_refs FROM messages a "
        "JOIN messages q ON q.id = a.cause_id "
        "WHERE a.id = ? AND q.from_role = ? "
        "AND q.verb IN ('challenge', 'escalate')",
        (wake.message_id, wake.role)).fetchone()
    if row is None:
        return ""
    try:
        refs = [r for r in json.loads(row["body_refs"] or "[]")
                if isinstance(r, str)]
    except (TypeError, ValueError):
        refs = []
    noun = "escalation" if row["verb"] == "escalate" else row["verb"]
    return (f"This answers your {noun} {row['id']} about "
            f"{', '.join(refs) or 'no rows'}")


def _missed_reply_line(conn: sqlite3.Connection, wake) -> str:
    """
    The line that says an earlier session on this reply landed no ruling, or "".

    Frame 267: a reply to a page that a session ended on with no ruling
    stays open and wakes the Liaison again. At temperature zero the same
    prompt gives the same calls, so the second wake must differ. Only a
    principal reply that carries `session_commit`'s note gets the line, so
    no other wake's prompt moves.

    Frame 320: a new request, with no cause, takes the same retry. Its
    line says that the session landed nothing, because a request owes no
    ruling.
    """
    if wake.detail != "converse" or not wake.message_id:
        return ""
    from .db import PAGE_VERBS, UNREAD_HEAD

    # A request has no cause, or a Liaison chat line as its cause: his
    # resend after the line of `unread_line` (frame 320, review 1, finding 1).
    row = conn.execute(
        "SELECT r.unresolved_note, p.verb AS cause_verb FROM messages r "
        "LEFT JOIN messages p ON p.id = r.cause_id "
        "WHERE r.id = ? AND r.verb = 'converse' AND r.from_role = 'principal' "
        "AND r.status = 'open' AND r.unresolved_note IS NOT NULL "
        "AND (r.cause_id IS NULL "
        "OR (p.from_role = 'liaison' AND p.to_role = 'principal' "
        "AND p.verb = 'converse' AND p.body_text LIKE ?) "
        f"OR p.verb IN ({','.join('?' * len(PAGE_VERBS))}))",
        (wake.message_id, UNREAD_HEAD + "%", *PAGE_VERBS)).fetchone()
    if row is None:
        return ""
    note = row["unresolved_note"].strip()
    stop = "" if note.endswith((".", "!", "?")) else "."
    if row["cause_verb"] not in PAGE_VERBS:
        return (f"A session on this request ended with nothing landed. Its "
                f"last refusal or error: {note}{stop}")
    return (f"A session on this reply ended with no ruling. Its last refusal "
            f"or error: {note}{stop}")


def _resolve_refs(conn: sqlite3.Connection, refs,
                  role: str | None = None,
                  detail: str | None = None,
                  batch_id: str | None = None) -> dict[str, Any]:
    """Refs to rows, one hop deep. Nothing those rows point at in turn.
    `role` and `detail` are the woken role and the wake's detail, the verb
    on a message wake. Only a Tester challenge reads a test's whole output."""
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
            # The value is the view's. Today's word for a row that rests on
            # the world is `cited` (`db.shown_provenance`).
            ("items", "id, text, kind, approval, "
                      "(SELECT CASE WHEN p.basis = 'world' THEN 'cited' "
                      "             ELSE p.provenance END "
                      " FROM item_provenance p WHERE p.id = items.id) AS provenance"),
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
                # The table travels with the row: a Vision Keeper handed a
                # relay of criteria approved them as items, ten refusals
                # (clickI night 38, 2026-09-13).
                resolved[ref] = {**dict(hit), "table": table}
                # The flag rides only on a description, so the rows of every
                # other item keep the text the recordings hash (frame 80).
                if table == "items" and _is_description(conn, ref):
                    resolved[ref]["is_description"] = 1
                # A disputed test travels with its last run. S0 walk eight:
                # the Developer challenged, the Tester held -- "the test
                # checks the greeting is displayed" -- nine rounds, while
                # the harness output said OSError: reading from stdin. The
                # Tester never saw it; a test's run is the one fact about
                # it that is not its own words, and the dispute is about
                # exactly that.
                if table == "tests":
                    run = conn.execute(
                        # The test's own batch only: an inherited test keeps
                        # its id across batches (frame 210).
                        "SELECT result, output FROM latest_runs WHERE test_id = ? "
                        "AND batch_id = (SELECT batch_id FROM tests WHERE id = latest_runs.test_id)",
                        (ref,)).fetchone()
                    if run:
                        out = run["output"] or ""
                        # A Tester challenge gets the whole stored output,
                        # which `harness.run_test` caps at 2000 characters.
                        # The 700 tail of night 106's `_03` held parser
                        # frames and not the test's own call line (frame
                        # 110, revision 2). Every other wake keeps the tail,
                        # so its prompt does not move.
                        whole = role == "tester" and detail == "challenge"
                        keep = out if whole else out[-700:]
                        # Frame 317, pass 1b: a Tester answer keeps the tail,
                        # because a 9b seat's window is 16k tokens. s410's
                        # `KeyError` sat 1929 characters from the end, so
                        # the raising line comes first.
                        resolved[ref]["last_run"] = {
                            "result": run["result"],
                            "output_tail": keep}
                        if (role == "tester" and detail == "answer"
                                and run["result"] != "pass"):
                            # The state reads the whole output. The tail of
                            # s364's tst_v2 run holds no assert line.
                            resolved[ref]["last_run"].update(
                                raising_line=_raising_line_head(out),
                                state=("failed before any assertion"
                                       if _failed_before_assertion(
                                           hit["body"] or "", out)
                                       else "failed"))
                        arranged = (None if whole or run["result"] == "pass"
                                    else _arrange_raise_tail(conn, hit, out))
                        if arranged is not None:
                            resolved[ref]["last_run"] = {
                                "result": run["result"],
                                "output_tail": arranged,
                                "label": FAILED_BEFORE_ASSERTION}
                break
        else:
            # Frame 115, design 200 change 4: law 2 keeps words off an
            # Architect answer, so its words travel as a decision row. A
            # message wake shows the row's text. 10 of 10 Architect answers
            # to the Developer on nights 138 and 139 carried refs alone. A
            # page or a rulings line passes no role and keeps its text.
            if role is not None:
                hit = conn.execute(
                    "SELECT id, author, text FROM decisions WHERE id = ?",
                    (ref,)).fetchone()
                if hit:
                    resolved[ref] = {**dict(hit), "table": "decisions"}
            # Frame 303: a report carries refs only (ruled 2026-08-15), so
            # the Liaison relays what the refs say. Night 162's s232 got
            # `["b_2"]` and no row. It wrote its brief's invoice example as
            # the question m110. A batch travels with its item's text, its
            # state and its last verdict. Other seats keep their prompts.
            if role == "liaison" and ref not in resolved:
                batch = _batch_row(conn, ref)
                if batch:
                    resolved[ref] = batch
    if role == "tester" and detail == "answer":
        # Frame 317, night 161: an answer refs criteria only. So s364 and
        # s410 saw no test and no run, and s364 removed the fix that
        # s315 made after it read "is not installed". Each criterion's
        # test now travels, and the blocks for a test ref fire for it.
        # Only a test of the wake's batch travels (pass 1b): night 161's
        # m237 named cr_1, whose test tst_4 sat in b_3.
        named = []
        for row in list(resolved.values()):
            if batch_id is None or row.get("table") != "criteria":
                continue
            test = conn.execute(
                "SELECT t.id FROM tests t JOIN criteria c ON c.id = t.criterion_id "
                "JOIN batch_tickets bt ON bt.ticket_id = c.ticket_id "
                " AND bt.batch_id = t.batch_id "
                "WHERE t.criterion_id = ? AND t.batch_id = ? "
                # Review 1, F2: a retired ticket owes no test, as in
                # `tests_missing`, so its test does not travel.
                + not_retired(conn, "bt.ticket_id")
                + " ORDER BY t.rowid DESC LIMIT 1",
                (row["id"], batch_id)).fetchone()
            if test and test["id"] not in resolved and test["id"] not in named:
                named.append(test["id"])
        if named:
            resolved.update(_resolve_refs(conn, named, role=role,
                                          detail=detail))
    return resolved


def _batch_row(conn: sqlite3.Connection, ref: str) -> dict[str, Any] | None:
    """A batch as the Liaison relays it: the item's words, the state, the
    head commit and the last verdict. A merge is the state `merged`."""
    hit = conn.execute(
        "SELECT b.id, b.item_id, i.text AS item_text, b.status, b.head_commit "
        "FROM batches b LEFT JOIN items i ON i.id = b.item_id "
        "WHERE b.id = ?", (ref,)).fetchone()
    if not hit:
        return None
    row = {**dict(hit), "table": "batches"}
    verdict = conn.execute(
        # The commit travels beside the word. A pass on an older commit is
        # no pass on the head (frame 303, review 1, finding 2).
        "SELECT result, commit_sha, failed_criterion, reason FROM verdicts "
        "WHERE batch_id = ? ORDER BY rowid DESC LIMIT 1", (ref,)).fetchone()
    if verdict:
        # Empty fields say nothing, so they stay out of the prompt.
        row["last_verdict"] = {k: v for k, v in dict(verdict).items() if v}
    return row


def _raising_line_head(output: str) -> str:
    """Each raising line and its two neighbours, when the 700 tail lacks it.

    The raising lines are the cause and the last raise that
    `harness.error_at` names (fact F5). Night 160's tst_v6 kept its
    `KeyError` cause outside the tail (frame 317). A word search for "Error"
    picked a source line on night 160, seq 243 (review 1 of frame 317, F3).
    Lines inside the tail give "".
    """
    from .harness import error_at

    tail_from = len(output) - 700
    lines = output.splitlines(keepends=True)
    starts, at = [], 0
    for line in lines:
        starts.append(at)
        at += len(line)
    found = error_at([line.rstrip("\r\n") for line in lines])
    out = ""
    for i in dict.fromkeys(i for i in (found.cause, found.line) if i is not None):
        if starts[i] < tail_from:
            lo, hi = max(i - 1, 0), min(i + 2, len(lines))
            out += "".join(lines[lo:hi]).rstrip("\n") + "\n...\n"
    return out


# Frame 110's label, given to every reader of a red row whose test raised in
# its arrange step (frame 304).
FAILED_BEFORE_ASSERTION = "the test failed before any assertion"

# A pytest location line: `path.py:6: ` or `path.py:696: AttributeError`.
_LOCATION = re.compile(r"^(\S.*?\.py):(\d+):(?: .*)?$")


def _arrange_raise_tail(conn: sqlite3.Connection, test: Any,
                        output: str) -> str | None:
    """The tail from the test-body line that raised, or None.

    Frame 304, night 158: s187's tst_02 raised on its arrange line inside
    `mock.py`. The 700 tail started inside `mock.py` and held no test line,
    and dec_123 and dec_124 blamed the code. The rule: the test file's frame
    names a line before the first surface call and before the first
    `assert`, and every later frame lies outside the worktree's source. Then
    the tail starts at the `>` line of the test's frame. A frame in the
    project's own code keeps today's tail.
    """
    for marker in ("During handling of the above exception, another "
                   "exception occurred:",
                   "The above exception was the direct cause of the "
                   "following exception:"):
        if marker in output:
            return None
    lines = output.splitlines()
    path = (test["path"] or "").replace("\\", "/")
    found = [(i, m.group(1).replace("\\", "/"), int(m.group(2)))
             for i, ln in enumerate(lines) if (m := _LOCATION.match(ln))]
    own = [f for f in found if path and (f[1] == path
                                         or f[1].endswith("/" + path))]
    if not own or found[-1] is own[0]:
        return None
    at, _, lineno = own[0]
    row = conn.execute(
        "SELECT b.worktree FROM batches b JOIN tests t ON t.batch_id = b.id "
        "WHERE t.id = ?", (test["id"],)).fetchone()
    root = (row["worktree"] if row else None) or ""
    later = [f for f in found if f[0] > at and f not in own]
    # Review 1, F2: a frame in the project's own code after the test's frame
    # means the code ran and raised, so the code can be at fault.
    if (not later or found[-1] in own
            or any(_in_source(f[1], root) for f in later)):
        return None
    try:
        tree = ast.parse(test["body"] or "")
    except SyntaxError:
        return None
    crit = conn.execute("SELECT surface_refs FROM criteria WHERE id = ?",
                        (test["criterion_id"],)).fetchone()
    try:
        refs = json.loads((crit["surface_refs"] if crit else None) or "[]")
    except ValueError:
        refs = []
    surface = {str(s).rsplit("::", 1)[-1] for s in refs}
    marks = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Assert)]
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            fn = n.func
            name = (fn.attr if isinstance(fn, ast.Attribute) else
                    fn.id if isinstance(fn, ast.Name) else "")
            if name in surface:
                marks.append(n.lineno)
    if marks and lineno >= min(marks):
        return None
    start = next((i for i in range(at - 1, -1, -1)
                  if lines[i].startswith(">")), at)
    return "\n".join(lines[start:])


def _in_source(where: str, root: str) -> bool:
    """Whether a pytest location path lies in the worktree's own source.

    Review 1 of frame 304, F1: with the worktree and Python on one drive,
    pytest prints a library frame as `..\\..\\Python\\...`. The path resolves
    against the worktree, and a path that leaves the worktree is outside.
    """
    root = (root or "").replace("\\", "/")
    root = posixpath.normpath(root).lower() if root else ""
    where = where.replace("\\", "/")
    if re.match(r"^([A-Za-z]:/|/)", where):
        full = posixpath.normpath(where).lower()
    elif root:
        full = posixpath.normpath(root + "/" + where).lower()
    else:
        full = posixpath.normpath(where).lower()
        if full == ".." or full.startswith("../"):
            return False
        return not any(p in ("site-packages", ".venv", "venv")
                       for p in full.split("/"))
    if root and not full.startswith(root + "/"):
        return False
    rel = full[len(root) + 1:] if root else full
    return not any(p in ("site-packages", ".venv", "venv")
                   for p in rel.split("/"))


_CHAINED = ("During handling of the above exception, another exception "
            "occurred:",
            "The above exception was the direct cause of the following "
            "exception:")

# The modules a test imports that are not the project's code.
_TEST_LIBS = frozenset({"pytest", "_pytest", "unittest", "mock"})

# An error on an object of a class: `'FakeStdin' object has no attribute
# 'readline'`, or `'FakeStdin' object is not iterable`.
_STUB_ERROR = re.compile(
    r"^E\s+(\w+Error): '(\w+)' object (?:has no attribute '(\w+)'|is not \w+)")

# A call that leaves out a required argument of the callee.
_MISSING_ARGS = re.compile(
    r"^E\s+TypeError: (\w+)\(\) missing \d+ required "
    r"(?:positional|keyword-only) arguments?: (.+)$")

# A project name that the head lacks: an import, a module attribute or a
# name. A mock's attribute is no project name, so it is not read here.
_MISSING_NAME = re.compile(
    r"cannot import name '(\w+)'|No module named '([\w.]+)'"
    r"|module '[\w.]+' has no attribute '(\w+)'|name '(\w+)' is not defined")


def arrange_fault(body: str, path: str, output: str, surface: set[str],
                  criterion: str = "", root: str = "",
                  adds: str = "") -> dict | None:
    """The line where a red test fails in its own arrange step, or None.

    Frame 304, night 159: bg_2's tests failed on a plain `FakeStdin` class
    and on `confirm()` with no `text`, and pass 1's door read a mock's spec
    only. The rule: a red test whose run never reaches an assertion of the
    surface's result cannot be passed by any code. The run shows that rule
    in three forms.

    1. `stub`: an `E` line names an object of a class that the test body
       defines, and the class lacks the attribute. The run fails on the
       test's own stub, wherever the stub is read. The caller makes this
       form a note, not a refusal (review 2, finding 2): the right code
       may never read what the stub lacks.
    2. `arrange`: the test's frame raises on a line before the first
       `assert` and the first surface call. Every later frame lies outside
       the worktree's source, and the line names no project import. A
       missing name that `adds` names gives None, because the batch adds
       it. `adds` holds the item text, the criteria and the touch rows.
       An ImportError on an import line gives None for every name.
    3. `signature`: the run raises a TypeError at a surface call in the
       test's frame, for a required argument that the criterion does not
       name.

    A raise inside the project's code, or an assertion, gives None. The
    caller reads only a run whose word is `fail`.
    """
    import sys as _sys
    try:
        tree = ast.parse(body or "")
    except SyntaxError:
        return None
    src = (body or "").splitlines()
    lines = (output or "").splitlines()

    def _text(n: int) -> str:
        return src[n - 1].strip() if 0 < n <= len(src) else ""

    # 1. The stub. A chained run still counts: night 159's tst_cr1 caught
    # the stub's AttributeError and failed on its own assertion after it.
    classes = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    for ln in lines:
        m = _STUB_ERROR.match(ln)
        if not m or m.group(2) not in classes:
            continue
        cls, attr = classes[m.group(2)], m.group(3)
        held = set()
        for t in cls.body:
            if isinstance(t, (ast.FunctionDef, ast.AsyncFunctionDef)):
                held.add(t.name)
            elif isinstance(t, (ast.Assign, ast.AnnAssign)):
                for tg in (t.targets if isinstance(t, ast.Assign) else [t.target]):
                    if isinstance(tg, ast.Name):
                        held.add(tg.id)
        if attr and attr in held:
            continue
        return {"rule": "stub", "line": cls.lineno, "quote": _text(cls.lineno),
                "error": ln[1:].strip(), "name": cls.name, "attr": attr}

    if any(marker in output for marker in _CHAINED):
        return None
    path = (path or "").replace("\\", "/")
    found = [(i, m.group(1).replace("\\", "/"), int(m.group(2)))
             for i, ln in enumerate(lines) if (m := _LOCATION.match(ln))]
    own = [f for f in found if path and (f[1] == path
                                         or f[1].endswith("/" + path))]
    if not own:
        return None
    kind = re.search(r":\d+: ([\w.]+)$", lines[found[-1][0]])
    kind = kind.group(1) if kind else ""
    if not kind or kind.endswith("AssertionError"):
        return None
    from .harness import error_line

    shown = error_line(output) or kind
    at, _, lineno = own[0]

    def _callee(n: ast.Call) -> str:
        fn = n.func
        return (fn.attr if isinstance(fn, ast.Attribute) else
                fn.id if isinstance(fn, ast.Name) else "")

    asserts = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Assert)]
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and _callee(n) in surface]

    # 3. The signature. The call raises before the callee's frame opens, so
    # the test's frame is the last frame of the run.
    if len(own) == 1 and found[-1] == own[0]:
        for ln in lines:
            m = _MISSING_ARGS.match(ln)
            if not m or m.group(1) not in surface:
                continue
            if not any(_callee(c) == m.group(1)
                       and c.lineno <= lineno <= (c.end_lineno or c.lineno)
                       for c in calls):
                continue
            missing = re.findall(r"'(\w+)'", m.group(2))
            # A criterion that names the argument may change it, so a
            # right change can make the call pass.
            if not missing or any(re.search(rf"\b{re.escape(a)}\b", criterion or "")
                                  for a in missing):
                return None
            return {"rule": "signature", "line": lineno, "quote": _text(lineno),
                    "error": ln[1:].strip(), "name": m.group(1),
                    "attr": missing}

    # 2. The arrange step.
    later = [f for f in found if f[0] > at]
    if any(f in own or _in_source(f[1], root) for f in later):
        return None
    marks = asserts + [c.lineno for c in calls]
    if marks and lineno >= min(marks):
        return None
    # Frame 304, pass 2c: the head lacks a module that the Developer or an
    # install adds. The same import at module level is a collection error,
    # where the door is silent. So a failed import line is no test fault.
    if kind.rsplit(".", 1)[-1] in ("ImportError", "ModuleNotFoundError") and any(
            isinstance(n, (ast.Import, ast.ImportFrom))
            and n.lineno <= lineno <= (n.end_lineno or n.lineno)
            for n in ast.walk(tree)):
        return None
    std = set(getattr(_sys, "stdlib_module_names", ())) | _TEST_LIBS
    project = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name.split(".")[0] not in std:
                    project.add((a.asname or a.name).split(".")[0])
        elif isinstance(n, ast.ImportFrom):
            if n.level or (n.module or "").split(".")[0] not in std:
                project.update(a.asname or a.name for a in n.names)
    for n in ast.walk(tree):
        if getattr(n, "lineno", None) != lineno:
            continue
        if isinstance(n, ast.Name) and n.id in project:
            return None
        # A patch target such as "click.termui.x" names project code that
        # a change can add.
        if (isinstance(n, ast.Constant) and isinstance(n.value, str)
                and "." in n.value
                and n.value.split(".")[0] not in std):
            return None
    # Review 2, finding 1: a name the batch's rows name is a name the batch
    # adds, so its absence at the head is no fault of the test. A mock's
    # missing attribute is not a project name, so night 158's tst_02 stays.
    missing = _MISSING_NAME.search(shown)
    if missing and adds:
        name = next(g for g in missing.groups() if g)
        if any(re.search(rf"\b{re.escape(p)}\b", adds)
               for p in name.split(".") if p):
            return None
    return {"rule": "arrange", "line": lineno, "quote": _text(lineno),
            "error": shown, "name": None, "attr": None}


def _failed_before_assertion(body: str, output: str) -> bool:
    """Whether a failed run stopped before any assertion of the test ran.

    The rule: the run failed before any assertion when the body has no
    `assert` line that the output names, or when the output's error line
    comes before the first line that names a body `assert` line. A traceback
    shows the test's own lines down to the failing one, so an assertion that
    ran and failed shows its line before the error.
    """
    asserts = [s.strip() for s in body.splitlines()
               if s.strip().startswith("assert")]
    # A chained traceback prints the cause first, with its own `E ` line,
    # and the test's section last. Night 107 (2026-10-02): s151's test
    # caught a TypeError and asserted on its text, the cause's `E ` line
    # sat above the assert, and the label read "before any assertion" on
    # a test that reached its own line 11. The last section is the test's.
    for marker in ("During handling of the above exception, another "
                   "exception occurred:",
                   "The above exception was the direct cause of the "
                   "following exception:"):
        if marker in output:
            output = output.rsplit(marker, 1)[1]
    lines = output.splitlines()
    named = next((i for i, line in enumerate(lines)
                  if any(a in line for a in asserts)), None)
    if named is None:
        return True
    from .harness import error_at

    first_error = error_at(lines).line
    return first_error is not None and first_error < named


def _has_failed_run_block(row: Any) -> bool:
    """Whether `_failed_run_blocks` prints a block for this resolved row."""
    if not isinstance(row, dict) or row.get("table") != "tests":
        return False
    run = row.get("last_run")
    return bool(run) and run.get("result") != "pass"


def _failed_run_blocks(inbound: dict[str, Any]) -> list[str]:
    """Plain text for each challenged test whose last run failed.

    One block per test: a heading line, the test's body, and the failure
    output, all unescaped.
    """
    blocks: list[str] = []
    for ref, row in (inbound.get("resolved_refs") or {}).items():
        if not _has_failed_run_block(row):
            continue
        run = row["last_run"]
        body = row.get("body") or ""
        output = run.get("output_tail") or ""
        state = run.get("state") or (
            "failed before any assertion"
            if _failed_before_assertion(body, output) else "failed")
        # Frame 317, pass 1b: a Tester answer's raising line, when the tail
        # lacks it. Every other wake has no such key.
        output = (run.get("raising_line") or "") + output
        blocks.append(f"\n[last run of {ref}: {state}]\n"
                      f"The test's body:\n{body.rstrip()}\n"
                      f"The failure output:\n{output.rstrip()}")
    return blocks


# A Python traceback frame. The path holds no quote mark.
_TRACE_FRAME = re.compile(r'^\s*File "([^"]+)", line (\d+), in (\S+)', re.M)


def _raised_signature_pushes(sb: sandbox_mod.Sandbox,
                             inbound: dict[str, Any]) -> dict[str, Any]:
    """The signature of the callable that raised, for each challenged test.

    Frame 223, night 153: every Tester read `'test_version_option' is not
    installed` and no Tester saw the parameters of the callable that raised.
    The interview of three seats found the signature in front of 0 of 3.

    The rule, per failed run: take the last traceback frame whose path is a
    path grain of the code index. `code.source` gives that file's top-level
    definitions, and the push reads the one whose span holds the line. The
    push is the `def` line through the parameter list and the docstring's
    first line, of the definition `_raising_span` names, and the lines from
    the guard to the raise. One push per test. A frame outside the index, a
    line outside every top-level definition, or a line on no `raise`
    statement pushes nothing.
    """
    import ast as _ast
    import textwrap as _textwrap

    if "code.source" not in sb.functions():
        return {}
    conn = sb.ctx.conn
    out: dict[str, Any] = {}
    for _ref, row in (inbound.get("resolved_refs") or {}).items():
        if not isinstance(row, dict) or row.get("table") != "tests":
            continue
        run = row.get("last_run")
        if not run or run.get("result") == "pass":
            continue
        frames = _TRACE_FRAME.findall(run.get("output_tail") or "")
        hit = None
        for path, line, _name in reversed(frames):
            path = path.replace("\\", "/")
            if conn.execute("SELECT 1 FROM code_index WHERE grain = ? "
                            "AND grain_kind = 'path'", (path,)).fetchone():
                hit = (path, int(line))
                break
        if hit is None:
            continue
        path, line = hit
        try:
            # The spans come from the file the run read, not from the index.
            # A batch moves lines, and the index holds main's lines. Night
            # 145: three frames at `decorators.py:526` sat in no indexed span.
            head = sb.call("code.source", path=path, start=0, end=1)
            defs = head.get("defs") or {} if isinstance(head, dict) else {}
        except Exception as exc:                           # noqa: BLE001
            # Review 1 of frame 223, point 6: a failed push is never silent.
            _log.warning("raised-signature push: code.source %s: %s: %s",
                         path, type(exc).__name__, exc)
            continue
        # A span is 0-based, and its end is one line past the definition.
        held = [(e - s, n, s, e) for n, (s, e) in defs.items() if s < line <= e]
        if not held:
            continue
        _, top_name, start, end = min(held)
        try:
            got = sb.call("code.source", path=path, start=start, end=end)
            text = got.get("text") or "" if isinstance(got, dict) else ""
            top = _ast.parse(_textwrap.dedent(text)).body[0]
        except Exception as exc:                           # noqa: BLE001
            _log.warning("raised-signature push: %s::%s: %s: %s",
                         path, top_name, type(exc).__name__, exc)
            continue
        # Review 1 of frame 223, finding 3: push only for a frame on a
        # `raise`. Night 142's `strip_ansi` frame was a `return`, and the
        # defect sat in its caller. A test module's frame is no raise either.
        found = _raising_span(top, line - start)
        if found is None:
            continue
        func, lo, hi = found
        first = func.body[0]
        doc = (isinstance(first, _ast.Expr) and isinstance(first.value, _ast.Constant)
               and isinstance(first.value.value, str))
        # ast lines are 1-based within the read text. A docstring keeps its
        # first line, and a body without one stops before its first statement.
        keep = first.lineno if doc else first.lineno - 1
        name = (top_name if func is top
                else f"{top_name}.{func.name}")
        key = f"code.source {path}::{name}"
        if key in out:
            continue
        rows = text.splitlines()
        lines = rows[func.lineno - 1:max(keep, func.lineno)]
        shown = {"path": path, "start": start + func.lineno - 1,
                 "end": start + func.lineno - 1 + len(lines),
                 "text": "\n".join(lines)}
        # Frame 223, interview 2, replay C: the lines from the guard to the
        # raise moved 2 of 4 turns off a made-up name. Three sentences moved
        # 0 of 12. The signature alone moved 0 of 5 runs. A flat string, so
        # the render shows it as a block. A nested dict renders as one
        # escaped line (frame 110's interview).
        shown["raised at"] = f"lines {start + lo} to {start + hi}"
        shown["the lines that raised"] = "\n".join(rows[lo - 1:hi])
        out[key] = shown
    return out


def _wake_criteria(wake: Wake, inbound: dict[str, Any] | None) -> list[str]:
    """The criterion ids a Tester wake is about, in the order they appear.

    A `tests_missing` wake names them in its detail. A message wake names
    them as resolved criterion rows, or as the criterion of a resolved test.
    """
    ids: list[str] = []
    if wake.kind == "tick:tests_missing" and wake.detail:
        ids += [c.strip() for c in wake.detail.split(":", 1)[-1].split(",")]
    for ref, row in ((inbound or {}).get("resolved_refs") or {}).items():
        if not isinstance(row, dict):
            continue
        if row.get("table") == "criteria":
            ids.append(row.get("id") or ref)
        elif row.get("table") == "tests" and row.get("criterion_id"):
            ids.append(row["criterion_id"])
    return list(dict.fromkeys(i for i in ids if i))


def _criterion_surface_pushes(sb: sandbox_mod.Sandbox, wake: Wake,
                              inbound: dict[str, Any] | None) -> dict[str, Any]:
    """The `def` line and the return lines of each surface the criteria name.

    Frame 143, night 154: s199 wrote `assert confirm(...) == "y"`, and
    `confirm` returns `True` or `False`. The interview found no line of the
    source in front of 3 of 3 seats. The push with the brief's sentence gave
    the right value on 3 of 3 replays (`plans/frame143-interview.md`, 3).

    One push per surface, keyed `surface path::name`. The key is not
    `code.source`, because frame 223's raised-signature push owns that key.
    The push holds the `def` line through the parameter list, then every
    `return` line and every assignment to a name a `return` gives. A surface
    whose file or definition does not resolve pushes nothing, with a log line.
    """
    import ast as _ast
    import textwrap as _textwrap

    if "code.source" not in sb.functions():
        return {}
    conn = sb.ctx.conn
    out: dict[str, Any] = {}
    for cid in _wake_criteria(wake, inbound):
        row = conn.execute("SELECT surface_refs FROM criteria WHERE id = ?",
                           (cid,)).fetchone()
        try:
            refs = json.loads(row["surface_refs"]) if row else []
        except (TypeError, ValueError):
            refs = []
        for ref in refs if isinstance(refs, list) else []:
            if not isinstance(ref, str) or "::" not in ref:
                continue
            from ..roles.api import _grain_path

            path, name = _grain_path(ref), ref.split("::", 1)[1]
            key = f"surface {path}::{name}"
            if key in out:
                continue
            shown = _surface_lines(sb, path, name, _ast, _textwrap)
            if shown is None:
                _log.info("surface push: %s does not resolve", ref)
                continue
            out[key] = shown
    return out


def _surface_lines(sb: sandbox_mod.Sandbox, path: str, name: str,
                   _ast: Any, _textwrap: Any) -> dict[str, Any] | None:
    """The signature and the return lines of `path::name`, or None."""
    top_name, _, member = name.partition(".")
    try:
        # The spans come from the file the batch reads, as frame 223 reads them.
        head = sb.call("code.source", path=path, start=0, end=1)
        defs = head.get("defs") or {} if isinstance(head, dict) else {}
        if top_name not in defs:
            return None
        start, end = defs[top_name]
        got = sb.call("code.source", path=path, start=start, end=end)
        text = got.get("text") or "" if isinstance(got, dict) else ""
        top = _ast.parse(_textwrap.dedent(text)).body[0]
    except Exception as exc:                               # noqa: BLE001
        _log.warning("surface push: %s::%s: %s: %s",
                     path, name, type(exc).__name__, exc)
        return None
    func = top
    if member:
        func = next((n for n in top.body if getattr(n, "name", None) == member),
                    None) if isinstance(top, _ast.ClassDef) else None
    if not isinstance(func, (_ast.FunctionDef, _ast.AsyncFunctionDef)) or not func.body:
        return None
    rows = text.splitlines()
    first = func.body[0]
    # The `def` line through the parameter list and the return annotation.
    sig = rows[func.lineno - 1:max(first.lineno - 1, func.lineno)]
    nodes = [n for n in _ast.walk(func) if isinstance(n, _ast.Return)
             and not _inside_nested(func, n, _ast)]
    names = {n.value.id for n in nodes if isinstance(n.value, _ast.Name)}
    for n in _ast.walk(func):
        if (isinstance(n, (_ast.Assign, _ast.AnnAssign)) and not _inside_nested(func, n, _ast)
                and any(isinstance(t, _ast.Name) and t.id in names
                        for t in (n.targets if isinstance(n, _ast.Assign) else [n.target]))):
            nodes.append(n)
    picked = sorted({ln for n in nodes
                     for ln in range(n.lineno, (n.end_lineno or n.lineno) + 1)})
    body: list[str] = []
    last = None
    for ln in picked:
        if last is None or ln != last + 1:
            body.append("    ...")
        body.append(rows[ln - 1])
        last = ln
    # Pass 1e, frame 143 read 1d: the sentence sat in the Tester's base brief.
    # It reached wakes with no surface and pulled them toward a test. So the
    # sentence rides only on the block it names.
    return {"path": path, "start": start + func.lineno - 1,
            "text": "\n".join(sig + body),
            "note": ("A test that asserts a return value asserts what "
                     "this surface returns.")}


def _inside_nested(func: Any, node: Any, _ast: Any) -> bool:
    """True when `node` sits in a `def` or a `lambda` inside `func`."""
    kinds = (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.Lambda, _ast.ClassDef)
    for inner in _ast.walk(func):
        if inner is not func and isinstance(inner, kinds):
            if any(n is node for n in _ast.walk(inner)):
                return True
    return False


def _raising_span(top: Any, at: int) -> tuple[Any, int, int] | None:
    """The definition to show, and the lines from the guard to the raise.

    `at` is the frame's line, 1-based within the text `top` was parsed from.
    The definition is the outermost `def` that holds `at`: `top` itself, or
    a method of `top` when `top` is a class. A nested closure such as
    `version_option`'s `callback` takes no parameter the test passes, so
    its `def` is not the one to show. The guard is the first `if` or
    `except` on the way down from the innermost `def` that holds `at`, so
    a chain of `elif` shows from its first test. The span ends with the
    statement that holds `at`. None unless that statement is an `ast.Raise`.
    """
    import ast as _ast

    def holds(n: Any) -> bool:
        return n.lineno <= at <= (getattr(n, "end_lineno", None) or n.lineno)

    kinds = (_ast.FunctionDef, _ast.AsyncFunctionDef)
    funcs = [n for n in _ast.walk(top) if isinstance(n, kinds) and holds(n)]
    if not funcs:
        return None
    shown = min(funcs, key=lambda n: n.lineno)
    if not shown.body:
        return None
    body = max(funcs, key=lambda n: n.lineno).body
    guard = None
    last = None
    while True:
        stmt = next((s for s in body if holds(s)), None)
        if stmt is None:
            break
        last = stmt
        if guard is None and isinstance(stmt, _ast.If):
            guard = stmt.lineno
        blocks: list[list[Any]] = []
        for name in ("body", "orelse", "finalbody"):
            blocks.append(getattr(stmt, name, None) or [])
        for h in getattr(stmt, "handlers", None) or []:
            if holds(h):
                if guard is None:
                    guard = h.lineno
                blocks.append(h.body)
        body = next((b for b in blocks if any(holds(s) for s in b)), [])
    if not isinstance(last, _ast.Raise):
        return None
    end = getattr(last, "end_lineno", None) or last.lineno
    return shown, (guard or last.lineno), end


# A fenced block, closed or cut at the end of the reply.
_FENCE_BLOCK = re.compile(r"```[^\n]*\n(.*?)(?:```|\Z)", re.S)
# A fenced block with its closing mark. A reply cut at the output budget
# ends inside its last block, so that block is not the seat's whole text.
_WHOLE_FENCE = re.compile(r"```[^\n]*\n(.*?)```", re.S)

# The runner's mark on the sentence after a fenced reply with no call. Night
# 126's s154 read the sentence with no mark as the tail of its own reply, and
# said that no such sentence stood in its prompt (frame 152's interview).
# The cut sentence above it carries the same form: `ERROR reply cut:`.
_NO_CALL = "ERROR no call: "


def _body_literal(body: str, allowed: set[str], signatures: dict | None,
                  head: str) -> str | None:
    """`body` as a value that the call parser reads back to the same text.

    The parser decodes one level of escapes, so every backslash is doubled.
    The first quote that the body does not hold wins, so most bodies carry
    no escaped quote. Night 126's s154 said that the call line had to carry
    the body (frame 152's interview, answer 7). The real parser reads each
    form back, and a form that does not return the same text is not offered.
    """
    text = body.replace("\\", "\\\\")
    forms = []
    for q in ("'", '"', "'''", '"""'):
        if q not in body and not (len(q) == 3 and body.endswith(q[0])):
            forms.append(f"{q}{text}{q}")
    forms.append("'''" + text.replace("'", "\\'") + "'''")
    for form in forms:
        calls = toolproto.extract_lenient(
            f"{toolproto.MARKER} {head}, body={form})", allowed, signatures)
        if (len(calls) == 1 and isinstance(calls[0], toolproto.ToolCall)
                and calls[0].args.get("body") == body):
            return form
    return None


def _encode_nudge(conn: sqlite3.Connection, refs: list[str], text: str,
                  allowed: set[str], signatures: dict | None = None,
                  whole: bool = False, challenge: bool = False) -> str:
    """The sentence for a test written into a reply, with the call to copy.

    The wake's refs give the values. A challenge names one test, and its row
    gives the id, the criterion and the path. An answer names one criterion,
    and its one stored test gives the id and the path, because a new id
    stores a second test of the criterion. A tick names the batch. A value
    the wake does not hold stays '...'.

    The body is the last fenced block that holds `def test`, because the
    seat's last version is its repair. `whole` reads closed blocks only, for
    a reply that the output budget cut. `challenge` says that the wake is a
    challenge, so an answer to the challenger is the other exit.
    """
    tests, crits = [], []
    for ref in refs:
        row = conn.execute("SELECT id, criterion_id, path FROM tests "
                           "WHERE id = ?", (ref,)).fetchone()
        if row:
            tests.append(row)
        elif conn.execute("SELECT 1 FROM criteria WHERE id = ?",
                          (ref,)).fetchone():
            crits.append(ref)
    args = {"id": "...", "criterion_id": "...", "path": "..."}
    if not tests and len(crits) == 1:
        args["criterion_id"] = crits[0]
        tests = conn.execute("SELECT id, criterion_id, path FROM tests "
                             "WHERE criterion_id = ?", (crits[0],)).fetchall()
    if len(tests) == 1:
        args = {k: tests[0][k] or "..." for k in args}
    stored = tests[0] if len(tests) == 1 else None
    named = ", ".join(f"{k}={v!r}" for k, v in args.items())
    head = f"tests.encode({named}"
    blocks = (_WHOLE_FENCE if whole else _FENCE_BLOCK).findall(text)
    tests = [b for b in blocks if "def test" in b]
    # A test fence that the budget cut is still a test. Its text is not
    # whole, so the call keeps the dots (frame 152's review of 1cfbe704,
    # finding 3).
    cut_test = whole and not tests and any(
        "def test" in b for b in _FENCE_BLOCK.findall(text))
    # Night 126's s154 fenced version 1 of its test with one more line
    # break, and said "Wait, that's the same". The call that the sentence
    # offered stored the failing test again (the same review, finding 1).
    same = None
    if tests and stored is not None:
        row = conn.execute("SELECT body, version FROM tests WHERE id = ?",
                           (stored["id"],)).fetchone()
        if row and (row["body"] or "").strip() == tests[-1].strip():
            same = row
    literal = (_body_literal(tests[-1], allowed, signatures, head)
               if tests and same is None else None)
    call = f"{head}, body={literal or repr('...')})"
    # The encode door refuses a criterion with no triage verdict in this
    # session, so a mode that holds the triage names it first (frame 152's
    # review of 9684e3c, point 3).
    if "tests.triage" in allowed:
        call = (f"tests.triage(criterion_id={args['criterion_id']!r}, "
                f"verdict='encodable') and then {call}")
    if same is not None:
        # The test's own batch only: an inherited test keeps its id across
        # batches (frame 210, fact F4).
        run = conn.execute("SELECT result FROM latest_runs WHERE test_id = ? "
                           "AND batch_id = (SELECT batch_id FROM tests "
                           "WHERE id = latest_runs.test_id)",
                           (stored["id"],)).fetchone()
        failed = ", which failed" if run and run["result"] != "pass" else ""
        # The answer channel is the asker's own, so a challenge wake holds
        # one `msg.answer_` call (`sandbox` keeps the asker's only). The
        # answer door asks for quotes= from the criterion.
        answers = sorted(n for n in allowed if n.startswith("msg.answer_"))
        other = ""
        if challenge and len(answers) == 1:
            other = (f", or answer the challenge: {answers[0]}(refs="
                     f"{list(refs)!r}, quotes=['...'])")
        return (f"{_NO_CALL}Your fenced test is the stored version "
                f"{same['version']}{failed}. Change the test and send it as a "
                f"call: {call}{other}.")
    if cut_test:
        return (f"{_NO_CALL}You wrote a test into your reply, and a reply is "
                f"not a stored test -- nothing landed. The output budget cut "
                f"your fenced test before it ended. Send it as a call: {call}. "
                f"Put the whole test in place of the dots of body.")
    # A fence with no test function is code, not a test (the same review,
    # point 4).
    if tests:
        # A body that no form returns whole stays '...', and the seat pastes
        # its own text (frame 152, pass 3).
        paste = ("" if literal else " Put the text of your fenced test in "
                 "place of the dots of body.")
        return (f"{_NO_CALL}You wrote a test into your reply, and a reply is "
                f"not a stored test -- nothing landed. Send it as a call: "
                f"{call}.{paste}")
    # Night 119's s247 fenced one import and 36k characters of comment. An
    # order to encode that is an order to store a non-test, so the code form
    # offers the end as the named-act nudge does (frame 152's review of
    # 5e0dd71, F3).
    return (f"{_NO_CALL}You wrote code into your reply, and a reply is not a "
            f"stored test -- nothing landed. Send it as a call: {call}, or end "
            f"by saying nothing is owed.")


def _label(conn: sqlite3.Connection, ref: str, row: dict) -> str | None:
    """The table a resolved line names. `_resolve_refs` read the row from one
    table, and that table is the label. Else `db.table_of` finds it (F22)."""
    return row.get("table") or table_of(conn, ref)


def _is_description(conn: sqlite3.Connection, item_id: str) -> bool:
    """Whether the item is a description. False on a run database that
    predates the column."""
    from .db import _has_column
    if not _has_column(conn, "items", "is_description"):
        return False
    row = conn.execute("SELECT is_description FROM items WHERE id = ?",
                       (item_id,)).fetchone()
    return bool(row and row["is_description"])


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


_TAG_ARGS = ("id", "criterion_id", "term", "path", "about_ref", "batch_id")


def _call_tag(call: Any, n_calls: int) -> str:
    """`tests.encode(id='tst_x')` on a multi-call turn; the bare name alone."""
    if n_calls < 2:
        return call.name
    args = getattr(call, "args", None) or {}
    for key in _TAG_ARGS:
        value = args.get(key)
        if isinstance(value, str) and value:
            return f"{call.name}({key}={value!r})"
    return call.name


# An answer longer than this is cut in the thread. The thread leads the
# fix wake's push, so an uncapped answer would crowd out the red tests.
_THREAD_ANSWER_CHARS = 600


def _decisions_in(conn: sqlite3.Connection, raw_refs, raw_asked) -> list[dict]:
    """The `decisions` rows that an answer's refs add to the question's refs,
    each rendered as `_resolve_refs` renders a decision. The text is cut at
    the answer's cap."""
    def _strs(raw) -> list:
        try:
            got = json.loads(raw or "[]")
        except (TypeError, ValueError):
            return []
        return [r for r in got if isinstance(r, str)] if isinstance(got, list) else []

    asked = set(_strs(raw_asked))
    out = []
    for ref in dict.fromkeys(r for r in _strs(raw_refs) if r not in asked):
        hit = conn.execute("SELECT id, author, text FROM decisions WHERE id = ?",
                           (ref,)).fetchone()
        if not hit:
            continue
        row = {**dict(hit), "table": "decisions"}
        text = row["text"] or ""
        if len(text) > _THREAD_ANSWER_CHARS:
            row["text"] = text[:_THREAD_ANSWER_CHARS] + chr(10) + cut_note(
                f"the decision {ref}", len(text) - _THREAD_ANSWER_CHARS,
                len(text), "characters", "Act on what is shown.")
        out.append(row)
    return out


def _after_these(sb: sandbox_mod.Sandbox, own: list[dict]) -> str:
    """The step after the thread on the red tests of a `tests_failing` wake.

    Frame 278, night 153: the step named the code, and the Architect's
    decision said that the test was at fault. The key is the refusal's key:
    the table, the author and the test ref. The offer stands only when the
    same-refs door admits it (reviews 1 and 2 of frame 278).
    """
    head = ("A listed message that is answered or closed is refused if sent "
            "again on these refs.")
    offer = None
    if sb.ctx.role == "developer":
        offer = sandbox_mod.decision_step(sb.ctx, [t.get("id") for t in own])
    if offer:
        return api._offer(sb.ctx, f"{head} {offer[0]}", "msg.challenge_tester",
                          offer[1])
    return (head + " Make one real change to the code the test calls, or end "
            "the session with no call.")


def _thread_on_tests(sb: sandbox_mod.Sandbox, tests: list[dict]) -> list[dict]:
    """The challenges and escalations whose refs hold a red test, each with
    its latest answer: the words, "answered with no words", "closed
    (<status>) with no answer row" or "not answered yet"."""
    thread: list[dict] = []
    for r in tests:
        # A body_refs that is not JSON, or that is a JSON object, holds no
        # test id. The review of dad15d9 (2026-10-02): one corrupt row made
        # json_each raise for every test, and the key never appeared.
        found = sb.ctx.conn.execute(
            "SELECT m.id, m.verb, m.to_role, m.status, a.id AS answer_id, "
            "a.body_text AS answer_text, a.body_refs AS answer_refs, "
            "m.body_refs AS asked_refs, a.from_role AS answer_from "
            "FROM messages m "
            "JOIN json_each(CASE WHEN json_valid(m.body_refs) "
            "  THEN m.body_refs ELSE '[]' END) j ON j.value = ? "
            "LEFT JOIN messages a ON a.id = ("
            "  SELECT x.id FROM messages x WHERE x.cause_id = m.id "
            "  AND x.verb = 'answer' ORDER BY x.seq DESC LIMIT 1) "
            "WHERE m.verb IN ('challenge', 'escalate') "
            # The woken role's own messages only. Night 108 (2026-10-02):
            # the Architect's challenges to the Vision Keeper, m177 and m182,
            # showed as entries on the Developer's test.
            "AND m.from_role = ? "
            # SQLite does not promise to skip json_type for an invalid row.
            "AND json_type(CASE WHEN json_valid(m.body_refs) "
            "  THEN m.body_refs ELSE '[]' END) = 'array' "
            "ORDER BY m.seq", (r.get("id"), sb.ctx.role)).fetchall()
        for m in found:
            text = (m["answer_text"] or "").strip()
            # The thread reads the prior's status as the repeat-refs door
            # does. Night 111 (2026-10-03): the thread said m97 was "not
            # answered yet", and the door said that m97 was answered.
            if m["answer_id"] is None and m["status"] != "open":
                answer = f"closed ({m['status']}) with no answer row"
            elif m["answer_id"] is None:
                answer = "not answered yet"
            elif not text:
                # Frame 278, night 153: m144 answered m143 with the decision
                # dec_1_tst_ver_opt_show_py and no words. Three later wakes
                # read "answered with no words" and never saw the decision.
                # Only a row that the answer adds counts. An answer echoes
                # the asker's refs, and those hold the asker's own reason row.
                # Review 1, finding 3: a row shows only when the answer's own
                # role wrote it, so a row of another seat never reads as its.
                rows = [d for d in _decisions_in(
                    sb.ctx.conn, m["answer_refs"], m["asked_refs"])
                    if d["author"] == m["answer_from"]]
                answer = (rows[0] if len(rows) == 1 else rows) if rows \
                    else "answered with no words"
            elif len(text) > _THREAD_ANSWER_CHARS:
                answer = text[:_THREAD_ANSWER_CHARS] + chr(10) + cut_note(
                    f"the answer {m['answer_id']}", len(text) - _THREAD_ANSWER_CHARS,
                    len(text), "characters",
                    "Nothing returns a message's words. Act on what is shown.")
            else:
                answer = text
            thread.append({"id": m["id"], "verb": m["verb"], "to": m["to_role"],
                           "test": r.get("id"), "answer": answer})
    return thread


def _source_the_tests_call(sb: sandbox_mod.Sandbox,
                           tests: list[dict]) -> dict[str, Any]:
    """The definitions a failing test imports, read at their lines.

    Each `from pkg.mod import name` in a red test body names a module; the
    index's path grains say which file that is; `code.source` says where in
    it `name` is defined. Two files and three spans at most, so the push
    stays a working set and not the repository.
    """
    import ast as _ast

    paths = [r["grain"] for r in sb.ctx.conn.execute(
        "SELECT grain FROM code_index WHERE grain_kind = 'path'")]
    wanted: dict[str, set[str]] = {}
    for row in tests:
        try:
            tree = _ast.parse(row.get("body") or "")
        except SyntaxError:
            continue
        for node in _ast.walk(tree):
            if not isinstance(node, _ast.ImportFrom) or not node.module:
                continue
            tail = node.module.replace(".", "/")
            path = next((p for p in paths if p.replace("\\", "/").endswith(f"{tail}.py")
                         or p.replace("\\", "/").endswith(f"{tail}/__init__.py")), None)
            if path:
                wanted.setdefault(path, set()).update(a.name for a in node.names)
    spans: dict[str, Any] = {}
    for path, names in list(wanted.items())[:2]:
        try:
            head = sb.call("code.source", path=path, start=0, end=1)
        except Exception:                                  # noqa: BLE001
            continue
        defs = head.get("defs") or {} if isinstance(head, dict) else {}
        for name in sorted(names):
            if name not in defs or len(spans) >= 3:
                continue
            start, end = defs[name]
            try:
                spans[f"{path}::{name}"] = sb.call(
                    "code.source", path=path, start=max(0, start - 2), end=end + 2)
            except Exception:                              # noqa: BLE001
                continue
    return spans


def _red_rows_by_output(rows: list[dict]) -> list[dict]:
    """
    The project's red rows, one block per output the harness gave.

    Night 113 (2026-10-04, frame 120): a batch broke its own import, and all
    34 project rows held one traceback of 726 characters. The rows took
    28,734 characters, the push cut kept ten copies, and the window cut
    removed all of `code.source`. A shared output now shows once, then the
    count, then the tests that gave it. The count goes before the list, so a
    cut inside a long list keeps it. Only byte-identical outputs share a
    block, because a changed name or line is a different fact. A row whose
    output no other row gave keeps today's form, so its wake keeps its bytes.
    Groups keep the order of their first row.
    """
    count: dict[str, int] = {}
    for r in rows:
        said = r.get("said")
        if isinstance(said, str) and said:
            count[said] = count.get(said, 0) + 1
    out: list[dict] = []
    group: dict[str, dict] = {}
    for r in rows:
        said = r.get("said")
        if not (isinstance(said, str) and said and count[said] > 1):
            out.append({k: r.get(k) for k in ("id", "path", "said")})
            continue
        if said not in group:
            group[said] = {"said": said, "count": count[said],
                           "tests that gave this output": []}
            out.append(group[said])
        group[said]["tests that gave this output"].append(
            f"{r.get('id')} {r.get('path')}")
    return out


def _guess_seed(conn, batch_id: str) -> dict | None:
    """The current guess set of a batch's item: its paths and symbols, and
    the principal's words when the set rests on a ruling."""
    row = conn.execute("SELECT item_id FROM batches WHERE id = ?", (batch_id,)).fetchone()
    last = conn.execute(
        "SELECT item_ver, ruling_id FROM touch_guesses WHERE item_id = ? "
        "ORDER BY rowid DESC LIMIT 1", (row["item_id"],)).fetchone() if row else None
    if last is None:
        return None
    rows = conn.execute(
        "SELECT grain, grain_kind FROM touch_guesses WHERE item_id = ? AND item_ver = ? "
        "AND ruling_id = ? ORDER BY rowid",
        (row["item_id"], last["item_ver"], last["ruling_id"])).fetchall()
    seed: dict[str, Any] = {
        "paths": [r["grain"] for r in rows if r["grain_kind"] == "path"],
        "symbols": [r["grain"] for r in rows if r["grain_kind"] == "symbol"]}
    if last["ruling_id"]:
        said = conn.execute("SELECT value FROM config WHERE key = ?",
                            (f"entry:{last['ruling_id']}",)).fetchone()
        try:
            words = json.loads(said["value"]) if said else None
        except (TypeError, ValueError):
            words = said["value"] if said else None
        if isinstance(words, str) and words:
            seed["the principal said"] = words
    return seed


RULED_KEY = "the principal ruled on this item, newest last"
RETIRED_KEY = "criteria of an old ticket, written before the item changed"
# A 9b seat's window is small, so the carry keeps the last three rulings
# (frame 315, pass 1).
RULED_CAP = 3
START_RULED_KEY = "the principal's words on this change, newest last"


def _old_tickets(conn, item_id: str, before_slice: bool) -> list:
    """The item's tickets below the newest generation, oldest first."""
    from .db import _has_column

    if not _has_column(conn, "tickets", "item_ver"):
        return []
    # In the criteria wake, a live ticket is never old: an amend raises
    # the item's version above every ticket (review 1, finding 4). The
    # slicing wake runs before the new ticket exists, so there a ticket
    # below the item's version is old too.
    newer = "(SELECT MAX(n.item_ver) FROM tickets n WHERE n.item_id = t.item_id)"
    if before_slice:
        newer = f"MAX({newer}, (SELECT i.version FROM items i WHERE i.id = t.item_id))"
    return conn.execute(
        f"SELECT t.id, t.item_ver FROM tickets t WHERE t.item_id = ? "
        f"AND t.item_ver < {newer} ORDER BY t.rowid", (item_id,)).fetchall()


def _old_criteria(conn, old: list[str]) -> list:
    marks = ",".join("?" * len(old))
    return conn.execute(
        f"SELECT c.id, c.ticket_id, c.version, c.text, t.item_ver FROM criteria c "
        f"JOIN tickets t ON t.id = c.ticket_id WHERE c.ticket_id IN ({marks}) "
        f"ORDER BY c.rowid", old).fetchall() if old else []


def _item_ruled(conn, item_id: str, *, before_slice: bool = False) -> dict[str, Any]:
    """The principal's landed words on the item, on every generation.

    The key set is frame 322's: the item, `guess:<item>`, the old tickets
    and their criteria. Night 166's m69, "only the docstring changes while
    the code stays the same", landed on the item and its guess line, and
    s185's criteria prompt did not carry it on the first generation (frame
    322, proposal line 2). Every word of the principal is a ruling on a row
    (ruling of 2026-10-08, point 4).
    """
    from ..roles.principal import ruled_words

    old = [r["id"] for r in _old_tickets(conn, item_id, before_slice)]
    names = {item_id} | set(old) | {r["id"] for r in _old_criteria(conn, old)}
    # A ruling on a live ticket's criteria is that ticket's business, and
    # the seat reads those rows already. Counted here, three such rulings
    # pushed m131 and m137 out of the cap (frame 315, review 1, finding 1).
    # A ruling that names only an old ticket is carried (finding 5).
    marks = ",".join("?" * len(old))
    live = {r["id"] for r in conn.execute(
        "SELECT c.id FROM criteria c JOIN tickets t ON t.id = c.ticket_id "
        "WHERE t.item_id = ?" + (f" AND t.id NOT IN ({marks})" if old else ""),
        (item_id, *old))}
    words = ruled_words(conn, sorted(names), item=item_id, skip=live)
    return {RULED_KEY: words[-RULED_CAP:]} if words else {}


def _retired_carry(conn, item_id: str, *, before_slice: bool = False) -> dict[str, Any]:
    """An old ticket's criteria, for an item that has an old ticket. Empty
    for every other item.

    Night 161: his correction landed on tk_1's criteria at version 4. The
    item was amended, tk_2 was sliced, and the criteria wake of s282 showed
    only the statement s3 (frame 315's provenance, repair 1). His words on
    the item come from `_item_ruled` on every generation (frame 322).
    """
    old_criteria = _old_criteria(
        conn, [r["id"] for r in _old_tickets(conn, item_id, before_slice)])
    # One slicing wake holds every item due a slice, so the list keeps the
    # newest old generation only (review 1, finding 6).
    last = max((r["item_ver"] for r in old_criteria), default=None)
    criteria = [{"old ticket": r["ticket_id"], "id": r["id"],
                 "version": r["version"], "text": r["text"]}
                for r in old_criteria if r["item_ver"] == last]
    return {RETIRED_KEY: criteria} if criteria else {}


RAISE_LINES_KEY = "the raise lines of each surface this wake names"


def _criteria_raise_lines(sb: sandbox_mod.Sandbox, hint: str) -> dict[str, str]:
    """The raise lines of each callable the criteria wake's subject names.

    `_named_callables` is the lookup, the same one the source push and the
    exception door read.
    """
    from ..roles.api import RAISE_LINES_SHOWN, _callable_source, _named_callables, _raise_block

    out: dict[str, str] = {}
    for grain in _named_callables(sb.ctx, hint)[:RAISE_LINES_SHOWN]:
        found = _callable_source(sb.ctx, grain)
        if found is not None:
            out[found[0]] = _raise_block(found[1], found[2])
    return out


def _index_test_files(conn, limit: int = 80) -> list[str]:
    """The index's test files, in grain order, at most `limit` of them."""
    # F9 (ruled: Roman, 2026-10-26 20:37): the basename gives the shape and
    # the frame's kind gives the partition. A `tests/` prefix decides neither.
    from ..roles.api import _is_test_file

    rows = conn.execute("SELECT grain FROM code_index WHERE grain_kind = 'path' "
                        "ORDER BY grain")
    return [g for g in (r["grain"] for r in rows)
            if _is_test_file(conn, g)][:limit]


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
    # The retired criteria get one line right after the rows, so no seat
    # names a line for them (frame 306, W-C1: night 165's s415 to s417).
    if isinstance(pushed.get("criteria.load"), list):
        from ..roles.api import RETIRED_NOTE_KEY, retired_note

        note = retired_note(sb.ctx.conn, sb.ctx.batch_id)
        if note:
            ordered_r: dict[str, Any] = {}
            for key, value in pushed.items():
                ordered_r[key] = value
                if key == "criteria.load":
                    ordered_r[RETIRED_NOTE_KEY] = note
            pushed = ordered_r
    # The cut keeps the front of the wake, so the criteria and the tests go
    # before the diff. The diff is the push that scales with the work
    # (frame 101, night 103).
    if "code.read" in pushed:
        pushed["code.read"] = pushed.pop("code.read")
    # Frame 243, rung 5 of the ladder: the builder reads the source, not a
    # paraphrase. Night 148's s190 built from the criterion alone and
    # merged the format that ruling r_4c8fd5d3ad declined.
    # The block goes right after the criteria, which stay as they were.
    if role in ("developer", "tester") and isinstance(
            pushed.get("criteria.load"), list):
        block = _contest_block(sb.ctx.conn, pushed["criteria.load"])
        if block:
            ordered: dict[str, Any] = {}
            for key, value in pushed.items():
                ordered[key] = value
                if key == "criteria.load":
                    ordered[CONTESTS_KEY] = block
            pushed = ordered
    # The stopped page tells him the team reads his answer, and his answer
    # lifts the start key. Night 163's start windows held no word of his
    # (frame 312, review w5, re-check). The commit door reads the same set.
    if (role == "developer" and wake is not None
            and wake.kind == "tick:batch_start" and wake.refs):
        from types import SimpleNamespace

        from ..roles.api import _ruling_texts

        said = [t for t, principal in _ruling_texts(SimpleNamespace(
            conn=sb.ctx.conn, batch_id=wake.refs[0])) if principal and t.strip()]
        if said:
            pushed[START_RULED_KEY] = said[-RULED_CAP:]

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
        # Writing criteria beside a callable the ticket names, the
        # Terminologist reads that callable's module and the item's own
        # words. clickI night 35 (2026-09-13): the ticket said "next to
        # echo", the lens listed `src/click/utils.py::echo`, and the criteria
        # invented "without buffering delays" without reading it.
        if wake is not None and wake.kind == "tick:criteria" and wake.refs:
            conn = sb.ctx.conn
            item = conn.execute("SELECT text FROM items WHERE id = ?", (wake.refs[0],)).fetchone()
            # Every ratified statement of the item's entries, not only the
            # statements the item's refs name. A seat that reads one clause
            # of an entry misses the clause that bounds it (frame 322).
            said = [r["text"] for r in conn.execute(
                "SELECT s.text AS text FROM statements s WHERE s.id IN ("
                "  SELECT x.target FROM refs x JOIN statements t ON t.id = x.target "
                "  WHERE x.src_table = 'items' AND x.kind = 'statement' "
                "    AND x.src_id = ? AND t.status != 'superseded') "
                "OR (s.status = 'ratified' AND s.span_entry IN ("
                "  SELECT t.span_entry FROM refs x JOIN statements t ON t.id = x.target "
                "  WHERE x.src_table = 'items' AND x.kind = 'statement' "
                "    AND x.src_id = ?) "
                # A statement another item names is that item's words. One
                # page entry can rule two items (frame 322, review 1, finding 2).
                "  AND s.id NOT IN (SELECT o.target FROM refs o "
                "    WHERE o.src_table = 'items' AND o.kind = 'statement' "
                "      AND o.src_id != ?)) "
                "ORDER BY s.id", (wake.refs[0], wake.refs[0], wake.refs[0]))]
            if item:
                pushed["the item"] = {"text": item["text"], "the principal said": said,
                                      **_item_ruled(conn, wake.refs[0]),
                                      **_retired_carry(conn, wake.refs[0])}
            # Frame 319, review 1, finding 1: the lookup reads the whole
            # index. The pushed list held 20 of clickI's 897 symbols, and
            # s157 never got `confirm`'s source.
            from ..roles.api import (RAISE_LINES_SHOWN, _grain_path,
                                     _named_callables)

            spans: dict[str, list[tuple[int, int]]] = {}
            for grain in _named_callables(sb.ctx, hint)[:RAISE_LINES_SHOWN]:
                row = conn.execute("SELECT line_start, line_end FROM code_index "
                                   "WHERE grain = ?", (grain,)).fetchone()
                spans.setdefault(_grain_path(grain), []).append(
                    (row["line_start"], row["line_end"]) if row else (0, 0))
            if spans and "code.source" in have:
                pushed["code.source"] = {}
                for path, held in spans.items():
                    # The named callables' lines when the index holds their
                    # spans, the head of the module when it does not.
                    if any(e == 0 for _, e in held):
                        lo, hi = 0, 400
                    else:
                        lo, hi = min(s for s, _ in held), max(e for _, e in held)
                    try:
                        pushed["code.source"][path] = sb.call(
                            "code.source", path=path, start=lo, end=min(hi, lo + 400))
                    except Exception:                      # noqa: BLE001
                        continue
        # The Architect predicting a batch's touch reads by the same lens.
        # clickI night 35 (2026-09-13): the ticket said "next to echo", the
        # Architect probed `echo_json`, found nothing, and predicted a new
        # root file; `src/click/utils.py::echo` was one index row away.
        if wake is not None and wake.kind == "tick:annotate" and wake.refs:
            rows = sb.ctx.conn.execute(
                "SELECT t.text AS text FROM batch_tickets bt "
                "JOIN tickets t ON t.id = bt.ticket_id WHERE bt.batch_id = ?",
                (wake.refs[0],)).fetchall()
            hint += " " + " ".join(r["text"] or "" for r in rows)
            # The batch's prediction starts from the item's guess, and from
            # the principal's correction of it. Without the push, a right
            # correction reached no plan (frame 298's design, 1.3; review 2,
            # finding 3).
            seed = _guess_seed(sb.ctx.conn, wake.refs[0])
            if seed:
                pushed["the item's guess"] = seed
        # The guess reads by the same lens, from the item's own words
        # (frame 298's design, 3.4, point 6).
        if wake is not None and wake.kind == "tick:guess" and wake.refs:
            row = sb.ctx.conn.execute("SELECT text FROM items WHERE id = ?",
                                      (wake.refs[0],)).fetchone()
            if row:
                hint += " " + (row["text"] or "")
        try:
            pushed["code.callables"] = sb.call("code.callables", hint=hint)
        except Exception:                                  # noqa: BLE001
            pass
        # Night 162's s157 saw `confirm` as a name and `UsageError` as a
        # glossary term, and wrote "must raise UsageError". `confirm` runs
        # `raise Abort() from None` (frame 319). The wake shows what each
        # surface it names raises, by the same lines the door quotes.
        if wake is not None and wake.kind == "tick:criteria" and wake.refs:
            block = _criteria_raise_lines(sb, hint)
            if block:
                pushed[RAISE_LINES_KEY] = block

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
    # The slicing wake names the item to slice; the account of everything
    # else the program does is not that wake's work. clickI night 35
    # (2026-09-13): woken for one item and shown five, the Vision Keeper
    # sliced all five and four were refused. The pushed account keeps the
    # wake's items whole and the rest as one line each.
    if (wake is not None and wake.kind == "tick:slicing" and wake.refs
            and isinstance(pushed.get("problem.consult"), list)):
        rows = pushed["problem.consult"]
        mine = [r for r in rows if isinstance(r, dict) and r.get("id") in wake.refs]
        rest = [r.get("id") for r in rows if isinstance(r, dict) and r.get("id") not in wake.refs]
        if mine:
            # Night 161's s281 sliced from the headline alone. The item's
            # old ticket held his corrected criteria (frame 315).
            mine = [{**r, **_item_ruled(sb.ctx.conn, r["id"], before_slice=True),
                     **_retired_carry(sb.ctx.conn, r["id"], before_slice=True)}
                    for r in mine]
            pushed["problem.consult"] = {
                "to slice, this wake": mine,
                "the rest of the account, not this wake's": rest,
            }

    # The agenda wake names the page's seven; the rest of the open ledger is
    # the next pages'. clickI night 35 (2026-09-13): 51 open rows, 15,500
    # characters, pushed into a wake whose refs named seven.
    if (wake is not None and wake.kind == "tick:agenda" and wake.refs
            and isinstance(pushed.get("ledger.list"), list)):
        rows = pushed["ledger.list"]
        mine = [r for r in rows if isinstance(r, dict) and r.get("id") in wake.refs]
        rest = sum(1 for r in rows if isinstance(r, dict) and r.get("id") not in wake.refs)
        if mine:
            pushed["ledger.list"] = {
                "this page": mine,
                "open and not on this page": f"{rest} more, on the pages after this one",
            }

    # The fix wake pushes the red tests and the code they call, not the
    # inherited suite. clickI night 46 (2026-09-14): `tests.load` pushed 34
    # inherited bodies (467,000 characters), the push was cut at 20,000, the
    # one failing test and what the harness said about it never arrived,
    # and three sessions read `src/click/utils.py` seven times each and
    # wrote nothing. `code.probe` with no pattern is a note, not a read.
    if (wake is not None and wake.kind == "tick:tests_failing"
            and isinstance(pushed.get("tests.load"), list)):
        rows = pushed["tests.load"]
        red = [r for r in rows if isinstance(r, dict)
               and r.get("last_result") in ("fail", "error")]
        if red:
            green = len(rows) - len(red)
            # The batch's own tests and the project's own are two facts.
            # click night 47 (2026-09-14): 19 of click's tests failed at the
            # Developer's commit, the push read their imports and pushed
            # 20,000 characters of `types.py`, and the Developer wrote an
            # essay about Choice and File. A project test with no criterion
            # fails because of the diff; the diff is what to push.
            own = [r for r in red if r.get("criterion_id")]
            project = [r for r in red if not r.get("criterion_id")]
            # The thread on a red test is part of the red test. Night 106
            # (2026-10-02): no tick wake carried m109 to m115. The seat
            # learned of them from refusals only, and it sent the challenge
            # again at attempts 4 to 8. A wake with no thread pushes no key,
            # so the recorded prompts keep their bytes. The key goes first,
            # because the push cut at 20,000 characters removes the last key
            # first, and a long test body must not take the thread with it.
            thread = _thread_on_tests(sb, own)
            shown: dict[str, Any] = {}
            if thread:
                shown["challenges and escalations on these tests"] = thread
                # The way out sits in the wake head, which the window keeps.
                # Night 111 (2026-10-03): by turn 17 the window had dropped
                # both refusals, and s252 sent the challenge a third time.
                # A thread where every entry waits adds no key, so the
                # recorded prompts keep their bytes.
                if any(t["answer"] != "not answered yet" for t in thread):
                    shown["after these"] = _after_these(sb, own)
            if own:
                shown["the batch's tests, not passing"] = own
            if project:
                shown["the project's own tests, not passing at your commit"] = (
                    _red_rows_by_output(project))
                # Frame 207, night 140: this sentence was a constant, and
                # the test was red at the base. The base run says it now.
                fact = sandbox_mod.project_tests_fact(
                    sb.ctx, [r["id"] for r in project], offer=False)
                shown["what that means"] = (
                    f"{len(project)} test(s) with no criterion are the project's, and "
                    + (fact or "they passed before this batch. Your diff broke them. "
                       "Read code.diff below and restore what it changed; a "
                       "challenge has no side here"))
            shown["passing, not shown"] = f"{green} test(s)"
            pushed["tests.load"] = shown
            if own and "code.source" in have:
                spans = _source_the_tests_call(sb, own)
                if spans:
                    pushed["code.source"] = spans
            if project and "code.diff" in have and "code.diff" not in pushed:
                try:
                    pushed["code.diff"] = sb.call("code.diff")
                except Exception:                          # noqa: BLE001
                    pass
            if not project:
                # The diff is for the project's own tests only. Pushed on
                # every fix wake, L1-DV-challenge-a-test-that-contradicts-
                # its-criterion went 5/5 to 0/5: with its diff in view the
                # Developer wrote code and challenged, both (2026-09-14).
                pushed.pop("code.diff", None)
    # The structural review sees the constraints that bind the diff, and no
    # test ids. Night 95 (2026-09-28): the push listed all 12 constraints
    # with no bindings, and the Architect copied a test id and its
    # criterion id from `batches.expect` into its finding.
    if wake is not None and wake.kind == "tick:structural_review":
        expect = pushed.get("batches.expect")
        if isinstance(expect, dict):
            expect.pop("tests", None)
        if "model.consult" in have:
            # The unfiltered list is night 95's shape, so a fault drops the
            # push and never keeps that list (frame 90's diff review, finding 3).
            from ..onboarding.boot import ZERO
            bid = sb.ctx.batch_id or (wake.refs[0] if wake.refs else None)
            try:
                files = api._diff_files(sb.ctx, bid) if bid else None
                if files is None:
                    raise ValueError(f"no changed files for batch {bid!r}")
                # The door's helper decides the set, so the push and the
                # refusal show one list (the second diff review, 6b). The
                # brief's exit names k0, so the list always shows it, also
                # when k0 binds areas away from this diff (finding 4).
                keep = api._reaching_constraints(sb.ctx.conn, files) | {ZERO}
                pushed["model.consult"] = [
                    r for r in sb.call("model.consult")
                    if isinstance(r, dict) and r.get("id") in keep]
            except Exception:                              # noqa: BLE001
                pushed.pop("model.consult", None)
                _log.warning("structural_review push: model.consult not "
                             "filtered for batch %r, so it is not pushed",
                             bid, exc_info=True)
    # The Tester sees where the principal expects the tests. On night 136
    # the tests of bg_2 and bg_3 went to `tests/test_utils/`, and the touch
    # set and the principal named other files (frame 190's design, question
    # 5.2, ruled on the records by the holding session, 2026-10-09).
    # A test path his ruling removes is not shown while the Architect has not
    # re-annotated yet (F35). A path row that holds `::` shows its file:
    # the door refused one such path on night 170 (the review of pass 1,
    # finding 2).
    if wake is not None and wake.kind == "tick:tests_missing" and wake.refs:
        from .lifecycle import grain_file, predicted_rows
        # F9: a test file by the one reader (ruled: Roman, 2026-10-26 20:37).
        from ..roles.api import _is_test_file

        paths = list(dict.fromkeys(
            grain_file(r) for r in predicted_rows(sb.ctx.conn, wake.refs[0])
            if r["grain_kind"] == "path" and r["confidence"] == "expected"
            and _is_test_file(sb.ctx.conn, grain_file(r))))
        if paths:
            pushed["touch"] = paths
    # The Architect that corrects a prediction sees the test files that
    # exist. In the interview of the red re-annotate case, no pre-run result
    # carried `tests/test_termui.py`, and the seat made up
    # `tests/test_terminal_ui.py` from the words (plans/frame190-interview.md,
    # 2026-10-09). Only a relay of batches pushes the key, so no other
    # recorded prompt moves.
    if (role == "architect" and wake is not None and wake.message_id
            and "batches.annotate" in have):
        from .scheduler import batch_relay

        if batch_relay(sb.ctx.conn, wake.message_id):
            tests = _index_test_files(sb.ctx.conn)
            if tests:
                pushed["the index's test files"] = tests
    # The guess names one request item, and its brief says a test path is one
    # of the test files that exist (frame 298's design, 3.4, point 6).
    from .scheduler import guess_relay

    guess_tick = (wake is not None and wake.kind == "tick:guess" and bool(wake.refs))
    if role == "architect" and wake is not None and (guess_tick or (
            wake.message_id and guess_relay(sb.ctx.conn, wake.message_id))):
        row = sb.ctx.conn.execute("SELECT id, text FROM items WHERE id = ?",
                                  (wake.refs[0],)).fetchone() if guess_tick else None
        if row:
            pushed["item"] = {"id": row["id"], "text": row["text"]}
        tests = _index_test_files(sb.ctx.conn)
        if tests:
            pushed["the index's test files"] = tests
    probe = pushed.get("code.probe")
    if isinstance(probe, list) and probe and isinstance(probe[0], dict) and "note" in probe[0]:
        pushed.pop("code.probe")

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
            pushed["decisions.search"] = _budget_decision_hits(hits)
    return pushed


def _decision_dropped(word: str, kept: int, total: int) -> str:
    """
    What the budget left out for one word, in the wording every cut uses.

    The call promised "for all {total}" and could not keep it: `decisions.search`
    comes back through `_render` at `RESULT_CHARS`, the same 6,000 characters the
    push holds, so a widely matching word overruns the asked result as well. The
    sentence says what the call returns and counts nothing it cannot promise.

    The sentence stays an imperative, because `CLAUDE.md` rules the imperative
    for an instruction. No case measures the difference.
    """
    return cut_note(
        f'the rulings for "{word}"', total - kept, total, "rows",
        f'Call decisions.search(query="{word}") for that word\'s rows, as far '
        f'as one result fits.')


def _decision_block(hits: dict[str, list[Any]],
                    kept: dict[str, list[Any]]) -> dict[str, Any]:
    """The pushed block for the rows kept so far, with a notice per cut word."""
    block: dict[str, Any] = {w: rows for w, rows in kept.items() if rows}
    notes = [_decision_dropped(w, len(rows), len(hits[w]))
             for w, rows in kept.items() if len(rows) < len(hits[w])]
    if notes:
        block["not shown"] = notes
    return block


def _budget_decision_hits(hits: dict[str, list[Any]],
                          limit: int = DECISIONS_PUSH_CHARS) -> dict[str, Any]:
    """
    Up to six words' matches inside one character budget, round robin by row.

    `decisions.search` has no LIMIT and the site runs a query per subject word,
    so the rows arrived whole and `PUSH_CHARS` chose which ones the seat saw:
    the record's share of a push was 55.5 per cent, and the median push sat at
    the backstop (night 87, 2026-09-20).

    Round robin, because rank by word order is rank by the order the subject
    happened to say its words in. First come gave word one every row it had and
    the other five words' matches never arrived. Every word that matched keeps
    its first row: the op returns `substr(text,1,200)`, so six first rows are
    about 2,000 characters and the guarantee is affordable.

    Affordable is not free, and the guarantee is inside the budget rather than
    beside it. Seeded with no fit test, one 9,000-character row rendered the
    block at 6,123 against a 6,000 limit, the outer `_render` cut it again, and
    the seat read two cuts for one block (the diff review of 0cc624b, finding
    2). The last word seeded is the first dropped, so word one keeps its row. A
    row wider than the whole budget takes every seed with it, and the block is
    then its notices alone: which words matched, and what to call for each.
    """
    kept: dict[str, list[Any]] = {w: [] for w in hits}
    seeded: list[str] = []
    for word, rows in hits.items():
        if rows:
            kept[word].append(rows[0])
            seeded.append(word)
    while seeded and len(_render(_decision_block(hits, kept), limit)) > limit:
        kept[seeded.pop()] = []
    open_words = [w for w, rows in hits.items() if len(rows) > 1 and kept[w]]
    while open_words:
        for word in list(open_words):
            candidate = dict(kept)
            candidate[word] = kept[word] + [hits[word][len(kept[word])]]
            # `_render` at this limit returns the block whole while it fits, and
            # a longer cut text when it does not, so the length is the test.
            if len(_render(_decision_block(hits, candidate), limit)) > limit:
                open_words.remove(word)       # this word is full, the rest go on
                continue
            kept[word] = candidate[word]
            if len(kept[word]) == len(hits[word]):
                open_words.remove(word)
    return _decision_block(hits, kept)


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


def _norm_path(path: str) -> str:
    """One spelling of a path, so a write clears a read that spelled it
    differently. Separators only: stripping a leading dot would rename
    `.venv/x`."""
    path = path.replace("\\", "/")
    return path[2:] if path.startswith("./") else path


def _path_arg(sb: sandbox_mod.Sandbox, call: Any) -> str:
    """
    The file path a call names, or "" when it names none.

    This indexes the session's repeat memory so a write can drop the answers
    about the file it changed. It is for invalidation only and never looks a
    call up (frame 43, 2026-09-19): a path key on the lookup would answer
    "unchanged" to 667 disjoint paging reads across nights 85 and 86.
    """
    args = dict(getattr(call, "args", None) or {})
    if getattr(call, "pos", None):
        try:
            artefact, fn = call.name.split(".", 1)
            args = sandbox_mod._bind_positional(
                getattr(sb[artefact], fn), call.pos, args, call.name)
        except Exception:
            # An unbindable argument list is the dispatch's problem. No path.
            return ""
    path = args.get("path")
    return _norm_path(path) if isinstance(path, str) and path else ""


def session_sandbox(conn: sqlite3.Connection, wake: Wake, *,
                    mode: str | None = None,
                    batch_id: str | None = None,
                    area: str | None = None,
                    session_id: str = "",
                    entry_id: str | None = None,
                    g: graph_mod.Graph | None = None) -> sandbox_mod.Sandbox:
    """
    One wake's sandbox, for the session and for every reader of its prompt.

    The system text advertises `sb.signatures()`, and the cassette key covers
    that text. So a second way to build this sandbox is a second system text.
    The cockpit's prompt preview built its own, and its tool list differed
    from the runner's for 18 of 121 cases (observed: frame 63's design
    review, 2026-09-22).

    `_order` is set here, before the function returns, because
    `signatures()` reads it and a caller that set it afterwards would
    advertise the tools in the wrong order.

    `mode` is the sandbox's mode and not the prompt's piece. `readonly`
    builds no write functions at all, so a caller that declares it changes
    the advertised list. `session_id` and `entry_id` reach no line of the
    system text, so a reader that only composes the text leaves them out.
    """
    # Law 11, decided by the wake rather than by the role: a survey is reading
    # a codebase, so what it writes was found. Everything else was chosen.
    from .scheduler import ONBOARDING_TICKS

    # Passed only by a caller that is testing the mode itself, or by a case
    # that declares one. Every other caller leaves it to the wake.
    mode = mode or session_mode(wake)
    sb = sandbox_mod.build(wake.role, conn, mode=mode, batch_id=batch_id,
                           session_id=session_id, entry_id=entry_id,
                           onboarding=wake.kind in ONBOARDING_TICKS, g=g,
                           # The subject the scheduler decided: an area for a
                           # survey, `@program` for the orientation, `@term:x`
                           # for a word. Never the role's to choose.
                           area=area or (wake.refs[0]
                                 if wake.kind in ONBOARDING_TICKS and wake.refs else None),
                           allow=_wake_allow(wake, conn),
                           wake=wake)
    sb._order = prompts.mode_order(wake.role, _mode_key(wake, conn)) or []
    # The words `ledger.log` offers in this mode (frame 204, section 8).
    sb.ctx.log_kinds = prompts.mode_kinds(wake.role, _mode_key(wake, conn))
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
    return sb


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
    pins = routed_pins(conn, pins, wake)

    # Instructions = base + the piece for whatever woke this session. A role's
    # modes are enumerable from the graph, so which piece loads is derived rather
    # than chosen.
    if not instructions:
        try:
            instructions = prompts.compose(wake.role, _mode_key(wake, conn))
        except prompts.MissingPrompt:
            instructions = ""

    session_id = new_id("s", conn)
    entry_id = message_entry_id(conn, wake.message_id) if wake.message_id else None

    # The one composition, so that a reader of the register reaches the same
    # working set and therefore the same system text. The mode is derived
    # there and read back off the sandbox below, because a second derivation
    # here could disagree with the tools the session was actually given.
    sb = session_sandbox(conn, wake, mode=mode, batch_id=batch_id, area=area,
                         session_id=session_id, entry_id=entry_id, g=g)

    claim(conn, wake.role, session_id, wake.message_id)
    if wake.message_id:
        conn.execute("UPDATE messages SET attempts = attempts + 1 WHERE id = ?",
                     (wake.message_id,))

    outcome = RunOutcome(session_id=session_id, committed=False, iterations=0)
    turns: list[Turn] = []

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
        # Resolved before the prompt, because the prompt teaches the protocol.
        # A caller's value wins. Else the profile decides, and every profile
        # before frame 323 except `local-openai-native` leaves it off.
        use_native = (native_default(conn) if native_tools is None
                      else bool(native_tools))
        system, user = build_prompt(wake.role, sb, wake, pushed, instructions,
                                    inbound, oneshot=oneshot,
                                    native=use_native)
        outcome.system, outcome.user = system, user
        pins = pins.with_prompt(system + user)

        transcript = [user]
        # The kind of each block, beside it. `_fit` evicts by kind (frame 100).
        kinds = [_WAKE]
        held_calls: list = []
        fence_warned = False
        intent_warned = False
        noop_warned = False
        stoodby_retried = False
        allowed = set(sb.functions())
        outcome.offered = sorted(allowed)
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
        # Frame 323 adds the profile as the second way to opt in, and
        # `use_native` is set above the prompt for that reason.
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
        # What each call answered, how often that answer came back, and which
        # keys a path answers. Frame 43 (2026-09-19): `already_run` was a set
        # nothing ever cleared, so "the answer is above" was said about answers
        # that had changed. Night 86's s145 read `src/click/termui.py` at 1014
        # lines, wrote it, committed it, and was then told the file was
        # unchanged, while its next read proves 998 lines. The repeated call
        # runs either way, so the two renders are compared and the line is said
        # only when they match.
        #
        # `by_path` invalidates and never looks a call up. The lookup stays
        # keyed by the call, because a path key would answer "unchanged" to 667
        # disjoint paging reads across nights 85 and 86 -- s17 walks click.py in
        # 400-line pages -- to close a false hold that costs three batches.
        answered: dict[str, str] = {}
        # Which turn answered each key. The eviction test below needs it: an
        # answer produced in this turn cannot be in this turn's prompt, so
        # membership alone read every repeat inside one reply as evicted, and
        # three identical calls in one reply came back as three full results
        # (the diff review of 0cc624b, finding 1).
        answered_at: dict[str, int] = {}
        repeated: dict[str, int] = {}
        # How often each key's result was rendered into the feedback. Rule 2
        # serves an evicted answer again rather than pointing at a block the
        # window took, and this counter is what bounds the serving: a result
        # larger than the room is evicted every turn, so an unbounded re-serve
        # repeats night 88's s137 (the design review of frame 77, finding 3).
        served: dict[str, int] = {}
        by_path: dict[str, set[str]] = {}
        # The writes that landed in this session: the key, the turn, the
        # answer and the rows the call staged. A copy of such a call does not
        # go to its door. Night 170 refused 37 copies in 27 sessions, and
        # each refusal read as a rejection of a row that had landed (night
        # 170's W8). Law 14 keeps a journal out: saying a thing twice is two
        # events. A later write to the same rows drops the entry, because
        # the copy then changes the rows again.
        landed: dict[str, tuple[int, str, set[tuple[str, str]]]] = {}

        def staged_rows(before: list,
                        sent: int) -> tuple[set[tuple[str, str]], bool]:
            """
            The rows one call staged or withdrew, and whether it sent.

            The list is compared by object, because a door can take a staged
            row back out (`ctx.writes[:] = ...`), so a length is no measure.
            """
            now = sb.ctx.writes or []
            old = {id(w) for w in before}
            new = {id(w) for w in now}
            rows = {(w[0], w[1]) for w in now if id(w) not in old}
            rows |= {(w[0], w[1]) for w in before if id(w) not in new}
            return rows, len(getattr(sb.ctx, "outbound", None) or []) > sent

        def drop_landed(rows: set[tuple[str, str]]) -> None:
            for gone in [k for k, v in landed.items() if v[2] & rows]:
                del landed[gone]

        def enter_landed(key: str, name: str, shown: str,
                         rows: set[tuple[str, str]], sent: bool,
                         turn: int) -> None:
            """
            Enter a call that ran as a landed write, when it is one.

            Only a call that staged rows, and no journal row and no message,
            is a landed write. A file write stages no row, and a later write
            can change the file, so its copy keeps frame 93's path. Law 14
            rules that a journal holds each saying. The main loop and the
            stood-by path both call this, so one rule decides.
            """
            if (name in read_fns or not rows or sent
                    or any(NATURAL_KEYS.get(t, ("",))[0] == "journal"
                           for t, _ in rows)):
                return
            already_run.add(key)
            landed[key] = (turn, shown, rows)

        # These six move together. `already_run` says a call ran, `answered`
        # says what it gave, `answered_at` says when, `repeated` counts the
        # askings answered by a line, `served` counts the renders, and
        # `by_path` invalidates. Both findings this machinery has
        # produced came from changing one of them alone: frame 43's stale hold
        # from `already_run` without `answered`, and the diff review's triple
        # serve from `answered` without `answered_at`.

        def forget(path: str) -> None:
            """
            Drop what a path answered. A write makes those answers false.

            `already_run` is left alone, and that is the whole of the rule:
            section 9.3 rules the path index is for invalidation only and the
            hold keeps today's semantics exactly. `already_run` drives
            `fresh_read`, so discarding a key made the read of a written path
            outstanding again, and the next [read, write] batch held the write
            that used to run. A seat re-sending that batch oscillates: run,
            held, run, held (the diff review of 34c3e72, F3).

            The staleness still works without it. The call is still a repeat,
            `answered` no longer holds a render to match, so nothing can equal
            the fresh one and the new result is served.
            """
            for gone in by_path.pop(_norm_path(path), ()):
                answered.pop(gone, None)
                answered_at.pop(gone, None)
                repeated.pop(gone, None)
                served.pop(gone, None)

        turns: list[Turn] = []
        cut_retried = False
        # The same call refused the same way, counted. clickI night 42
        # (2026-09-13): a Tester session sent six encodes a turn against the
        # same six refusals for twenty-two turns, 239 refusals; a Developer
        # paraphrased a quote 110 times against "quote, not paraphrase".
        # A refusal is the door's half of a conversation; the third time
        # the same refusal answers the same call, the conversation is over.
        refused_same: dict[tuple[str, str], int] = {}
        # The refusals of a pass's lines, so the note of frame 170 speaks
        # only where its routes are true: never to a refused fail and never
        # to a verdict that already landed.
        refused_pass: set[tuple[str, str]] = set()
        stop_reason = ""
        turn_refusals: set[tuple[str, str]] = set()
        # True only while the newest answer to any call is a refusal that
        # told the seat to end with no call (frame 153). Every later answer,
        # an OK or an ERROR line, sets it again, because only the door's
        # newest word counts. `ctx.refusals` cannot serve: a message's
        # refusal never reaches it.
        told_to_end = False
        # The repeat refusals that say the answer is in this prompt: the key,
        # the exact line and the call's name. `_repoint` reads them after
        # every fit and returns the ones that still stand. A full render of
        # the key removes them below (frame 169's review, finding 1).
        pointers: list[tuple[str, str, str]] = []

        budget = _fit_budget(pins.num_ctx, len(system))

        for iteration in range(1, max_iterations + 1):
            if stop_reason:
                outcome.errors.append(stop_reason)
                break
            outcome.iterations = iteration
            transcript, kinds = _fit(transcript, kinds, budget,
                                     native=use_native)
            # The repeat refusals were true in the prompt they answered. Any
            # later fit can drop the answer before the seat reads them again
            # (frame 169, night 126's s159 turn 20, and its review's probe F).
            pointers = _repoint(transcript, kinds, pointers, answered,
                                served, sb)
            user = "\n\n".join(transcript)
            # Above every backend, because the only whole-prompt measurement ran
            # on the reply and `truncated` is an Ollama field: replayed cases
            # never reached it.
            over_budget = _prompt_overrun(system, user, budget, pins.num_ctx)
            if over_budget:
                outcome.errors.append(over_budget)
            _started = time.perf_counter()
            completion = backend.complete(system, user, pins, tools=schemas)
            outcome.completions.append(completion.text)
            # The provider's own calls. They are not in the text, so the turn
            # record and the next turn's history name each one on a line of
            # its own. Without the lines the history showed only results, and
            # Gemma sent the same three calls again (frame 323's trial).
            native_calls = _native_calls(completion) if use_native else []
            outcome.native.append(native_calls)
            said = _with_native_lines(completion.text, native_calls)
            # The exact context and the exact response, kept. Everything else
            # about a session is recoverable from its rows; this is not, and it
            # is what every session that behaved oddly has turned out to need.
            turns.append(Turn(iteration, system, user, said,
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
                # Say what happened, not what the counter reads. A cut prompt
                # reports half the window, which reads as well inside it: the
                # server collapses anything over `num_ctx` to `num_ctx / 2 + 2`
                # and keeps the tail, so the brief at the front is what goes
                # (measured 2026-09-18, finding 79).
                whole = (getattr(completion, "prompt_estimate", 0)
                         or completion.prompt_tokens)
                outcome.errors.append(
                    f"prompt did not fit: {completion.prompt_tokens} of about "
                    f"{whole} tokens evaluated against a {pins.num_ctx} "
                    f"window — the server cut the prompt from the front, "
                    f"which is where the brief is")
            # A new reply: the seat has read the last reply's results, held
            # calls included, so their `dropped` notes stop no commit (frame
            # 140).
            sb.begin_reply()

            # `call_at` carries each call's start offset in `scanned`, and
            # `scanned` is the text those offsets index into. Rule 1 below
            # compares them with the first invented result (frame 77).
            #
            # Native calls take the place of the parse, and an empty native
            # list falls back to it, so a `TOOL:` line still runs. A native
            # call comes after the text, so its offset is the text's end.
            # Rule 1 of frame 77 then drops it behind an invented result. The
            # cut test below skips native calls, because each one is whole.
            if native_calls:
                calls = native_calls
                call_at = [len(completion.text)] * len(calls)
                scanned = completion.text
            else:
                calls, call_at, scanned = toolproto.extract_lenient(
                    completion.text, allowed, signatures=_param_sets(sb),
                    with_offsets=True)
            # Frame 237. The record of night 147 showed a refused attest and
            # no cause for the empty glossary, and s187 read only the general
            # nudge and wrote the list again for five turns. So the account
            # gets one line, and the seat reads one line on its next turn.
            # The account line has no dotted name before its first colon,
            # because the fixtures count such a head as a refused call (the
            # note at `session_note` below).
            listed_note = []
            for name in listed_not_called(
                    completion.text,
                    {getattr(c, "name", None) for c in calls}, allowed):
                listed = (f"written as a list under its name, not as calls: "
                          f"`{name}`. None ran. Each call is one line, "
                          f"`{toolproto.MARKER} {name}(...)`.")
                if listed not in outcome.errors:
                    outcome.errors.append(listed)
                listed_note.append(
                    f"NOTE You wrote `{name}` as a heading over a list. A list "
                    f"runs nothing, so no `{name}` ran. Write each call on its "
                    f"own line: `{toolproto.MARKER} {name}(...)`.")
            if completion.done_reason == "length":
                # clickI night 16 (2026-09-12): a 688-line whole-file write
                # stopped at the output cap mid-string, the parser called it
                # an unbalanced quote, and the Developer then read the file
                # as already changed. The cap is a fact the model cannot see.
                cut = ("your reply was cut at the output budget before it "
                       "ended, so the last call did not run and nothing was "
                       "written. Send less in one reply: one or two calls, "
                       "then read their results. For a long file, write the "
                       "span you changed with start and end copied from "
                       "code.source, not the whole file")
                outcome.errors.append(cut)
                cut_note = cut
            else:
                cut_note = None
            # A seat that stores a test with tests.encode and writes no file.
            # A session that wrote is not told "nothing landed": night 120's
            # s140 landed its encodes and showed the test in a fence at turn
            # 6. Only a test row counts: a `ledger.log` stores no test, and the
            # night-120 replay of s140 lost the nudge to one (frame 152's
            # review of 5e0dd71, F1).
            test_seat = ("tests.encode" in allowed
                         and "code.write" not in allowed
                         and not any(w[0] == "tests" for w in sb.ctx.writes))
            if cut_note and not calls and not cut_retried:
                # clickI night 31 (2026-09-13): a Tester challenge reply ran
                # to the cap with no call in it, the cut note was appended to
                # a list the loop had not made yet, the session died on the
                # NameError, and the same wake was dispatched 69 times over
                # 98 minutes. A cut reply with no call is not the end: the
                # model reads what it sent, bounded, and the cut, once.
                #
                # The two lines state one fact: no call ran. "The last call did
                # not run" made night 119's s32 believe a call it had sent was
                # lost (frame 121's interview, B1). The sentence holds for a
                # prose reply and for a bare call cut in the middle, which
                # parses to no call (frame 121's diff review, finding 4).
                # `outcome.errors` keeps the general sentence.
                cut_retried = True
                _append(transcript, kinds, _REPLY,
                        _render_cut(completion.text, 4000, reply=True))
                said = ("ERROR reply cut: your reply was cut at the output "
                        "budget before it ended. It held no whole call, so no "
                        "call ran and nothing was written. Send one call, or "
                        "end with one sentence.")
                # Night 126's s156 wrote its repair in a whole fence, and the
                # budget cut its reply after the fence. The cut sentences stood
                # alone, and no test nudge followed. The runner holds the whole
                # reply, so it reads the fence that the shown part lost
                # (frame 152, pass 3).
                if (test_seat and not fence_warned
                        and _WHOLE_FENCE.search(completion.text)):
                    fence_warned = True
                    outcome.errors.append("wrote a test into its reply")
                    said += "\n" + _encode_nudge(
                        conn, inbound.get("refs") or list(wake.refs),
                        completion.text, allowed, _param_sets(sb), whole=True,
                        challenge=inbound.get("verb") == "challenge")
                _append(transcript, kinds, _RESULTS, said)
                continue
            if ("```" in completion.text and not calls
                    and "code.write" in allowed and not fence_warned):
                # Walk ten: the Developer's fix, whole and correct, inside a
                # fence in its reply -- and nothing landed, because a reply
                # is not a file. Once: told, and the next fenced reply is
                # the session's real stop.
                fence_warned = True
                outcome.errors.append("wrote code into its reply")
                _append(transcript, kinds, _REPLY, completion.text)
                _append(
                    transcript, kinds, _RESULTS,
                    f"{_NO_CALL}You wrote code into your reply, and a reply "
                    "is not a file -- nothing landed. Send it as a call: "
                    "code.write(path='...', text='...') and then code.commit.")
                continue
            # Night 125: the Tester s147 and s149 each wrote the repair of a
            # challenged test in a fence and sent no tests.encode. The branch
            # above needs code.write, which a Tester never holds. s147 met the
            # named-act nudge, and s149 met no nudge, because a message wake
            # gets no owed-call nudge and "Let's fix" is not an INTENT.
            # Once: told, and the next fenced reply is the session's real
            # stop, so neither nudge below answers it.
            test_fence = "```" in completion.text and not calls and test_seat
            if test_fence and not fence_warned:
                fence_warned = True
                outcome.errors.append("wrote a test into its reply")
                _append(transcript, kinds, _REPLY, completion.text)
                # A reply that the budget cut ends inside its last block, so
                # only whole blocks give a body.
                _append(transcript, kinds, _RESULTS, _encode_nudge(
                    conn, inbound.get("refs") or list(wake.refs),
                    completion.text, allowed, _param_sets(sb),
                    whole=bool(cut_note),
                    challenge=inbound.get("verb") == "challenge"))
                continue
            if (not calls and not intent_warned and not test_fence
                    and INTENT.search(completion.text)
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
                _append(transcript, kinds, _REPLY, completion.text)
                _append(
                    transcript, kinds, _RESULTS, "\n".join(listed_note + [
                        "You said what you would do and did not do it -- a "
                        "reply is not a call. Send the call you named, as "
                        "TOOL: ..., or end by saying nothing is owed."]))
                continue
            # Night 125: the door told s158 "End the session with no call.",
            # s158 obeyed, and this nudge then told it to act with a call.
            # It sent the refused challenge again. A session whose newest
            # refusal gave that step ends as the door asks (frame 153).
            if (not calls and not noop_warned and not held_calls
                    and not test_fence and wake.kind.startswith("tick:")
                    and not (sb.ctx.writes or getattr(sb.ctx, "outbound", []))
                    and not told_to_end):
                # Walk sixteen: the two-line check answered "No, the test is
                # wrong" and the session ended -- no fix, no challenge, no
                # escalation, two sessions to quarantine. A tick exists
                # because state is owed; a session that touches nothing
                # leaves the tick to fire again with the same material.
                # Told once; the next prose turn is the real stop.
                noop_warned = True
                outcome.errors.append("ended a tick with nothing done")
                _append(transcript, kinds, _REPLY, completion.text)
                _append(
                    transcript, kinds, _RESULTS, "\n".join(listed_note + [
                        "You were woken because something is owed here, and "
                        "this session has written nothing and sent nothing -- "
                        "the same wake will fire again with the same material. "
                        "Act on your conclusion with a call: fix it, dispute "
                        "it with the evidence quoted, or escalate it. If truly "
                        "nothing is owed, say so and stop."]))
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
                    # The hold keeps the turn's tail whole, so a parse error
                    # behind the held write reaches here. It has no name and
                    # runs nothing, so it gets the turn loop's answer to a
                    # parse error. Night 173's s130 read `hc.name` on one
                    # and failed (W11).
                    if isinstance(hc, toolproto.ToolError):
                        outcome.errors.append(hc.reason)
                        refused.append(f"ERROR {hc.raw}: {hc.reason}")
                        continue
                    # A held call can write the rows of a landed call, and
                    # the copy of that call must then go to its door. A held
                    # call that lands is a landed call too: the retry turn
                    # below gets the s117 shape, a re-sent batch (the W8
                    # review, finding 7).
                    staged_before = list(sb.ctx.writes or [])
                    sent_before = len(getattr(sb.ctx, "outbound", None) or [])
                    try:
                        held_result = sb.call(hc.name, *hc.pos, **hc.args)
                        told_to_end = False
                    except Exception as exc:           # noqa: BLE001
                        outcome.errors.append(f"{hc.name} (held): {exc}")
                        refused.append(f"ERROR {hc.name}: {exc}")
                        told_to_end = isinstance(exc, api.EndRefusal)
                        drop_landed(staged_rows(staged_before, sent_before)[0])
                    else:
                        rows, sent = staged_rows(staged_before, sent_before)
                        drop_landed(rows)
                        enter_landed(sb.call_key(hc.name, hc.pos, hc.args),
                                     hc.name, _render(held_result, RESULT_CHARS),
                                     rows, sent, iteration)
                if refused and not stoodby_retried:
                    # Walk twenty-one: seven encodes held behind seven
                    # triage reads, the model declared them done, the
                    # stood-by execution refused every one, and the session
                    # was over before the refusals could be read. A refusal
                    # is the door's half of a conversation; once, the model
                    # gets to answer it.
                    stoodby_retried = True
                    held_calls = []
                    _append(transcript, kinds, _REPLY, completion.text)
                    _append(
                        transcript, kinds, _RESULTS,
                        "The calls you stood by ran, and these were "
                        "refused:\n" + "\n".join(refused)
                        + "\nAnswer the refusals with corrected calls, "
                        "or end.")
                    continue
                break

            # A turn identical to the one before it is the session saying it
            # has nothing more to say. At temperature zero the model is a
            # function of its prompt, and the prompt has only grown by the
            # repeat line; the next completion will be this one again.
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
                outcome.errors.append(REPEAT_END)
                break

            # Frame 237: a reply with a list and some real calls reads the
            # note beside their results.
            feedback = list(listed_note)
            # The room this turn's results share, spent in call order. A
            # result takes the smaller of its own cap and what is left, so the
            # first read of a turn is never cut by a later one, and the refusal
            # and error lines are not charged: a seat that loses a refusal
            # sends the same call again.
            #
            # Charged against what `_fit` promises to keep -- the wake and the
            # latest exchange -- so the cut lands here, where the sentence
            # names the call that fetches the rest, rather than in
            # `_cap_exchange`, which can only say the block was cut.
            # `_render` puts its notice *outside* the limit it was given, so a
            # cut result overruns its cap by the sentence that says where the
            # cut fell. One such notice is reserved here, for the last result
            # of the turn: every earlier one is charged exactly below.
            result_room = min(TURN_RESULT_CHARS,
                              max(budget - len(transcript[0])
                                  - len(completion.text) - 6 - _CUT_NOTE_CHARS,
                                  _MIN_EXCHANGE))
            # The turn's first source read takes its own cap whatever the room
            # says: see the floor at the render below.
            source_served = False
            # One repeat refusal per key per turn. The copies are the fault it
            # exists to stop, and each one is longer than the line it replaces.
            refused_keys: set[str] = set()
            # Which keys this reply has already been served. A second copy in
            # one reply is the s71 storm, and the eviction test cannot see it:
            # an answer made this turn is not in this turn's prompt.
            served_keys: set[str] = set()
            # The copies of landed calls in this reply. The first copy of a
            # key gets the line, as the repeat refusal does. A reply of
            # copies alone ends the session below.
            copied_keys: set[str] = set()
            copies = 0
            # One test for the line and for the loop below, so the line and
            # the skipped error never disagree on which call the cut broke.
            cut_inside = (bool(cut_note) and not native_calls
                          and _cut_inside_last(calls, call_at, scanned,
                                               allowed))
            if cut_note:
                feedback.append(
                    f"ERROR reply cut: {_reply_cut_line(calls, cut_inside)}")
            held = []
            # Any tool call this turn supersedes last turn's held tail -- the
            # model revised, and its new calls are its will. Cleared here,
            # before this turn's calls run.
            held_calls = []
            seen_read = False
            # Rule 1's list: the calls this turn wrote after a result it made
            # up. Names only, and never a call object, because no path may run
            # them. The stood-by path above runs `held_calls`, so an invented
            # tail put there would land on "Done." (the design review of frame
            # 77, finding 1).
            invented_tail: list[str] = []

            fabricated = FABRICATED_RESULT.search(scanned)
            if fabricated:
                outcome.errors.append("wrote its own tool results")
                # The line above stays word for word, because nightcount
                # compares the sign across nights. The stream stop gets its
                # own line (frame 232).
                if completion.done_reason == "invented_result":
                    found = fabricated.group(0)
                    at = fabricated.start() + len(found) - len(found.lstrip())
                    outcome.errors.append(
                        f'the stream stopped at the invented result "{found.strip()}" '
                        f'on line {scanned.count(chr(10), 0, at) + 1} of the reply, '
                        f'so nothing after it was generated')
                feedback.append(
                    "You wrote tool results into your own reply -- the lines "
                    "beginning `OK ...` or `ERROR ...`. Those did not come from "
                    "me and nothing behind them ran. Only results I send back "
                    "are real. Send the calls alone and stop; I will answer.")
            for i, call in enumerate(calls):
                # Rule 1: a turn's calls run up to the first invented result,
                # and every call after it is dropped. The calls behind the
                # invention were built on it, so the seat must decide them
                # again with the real results in view. Night 86's s145 read a
                # file, invented the write's own result, and the runner wrote
                # and committed from memory (frame 75, 2026-09-23). The calls
                # arrive in text order, so the first one past the match ends
                # the turn.
                if fabricated and call_at[i] > fabricated.start():
                    invented_tail = [c.raw or getattr(c, "name", "?")
                                     for c in calls[i:]]
                    break
                if cut_inside and i == len(calls) - 1:
                    # The cut is the cause and the cut note says so. clickI
                    # night 46 (2026-09-14): the parse error's own hint
                    # ("put it between triple quotes") was followed
                    # literally, and four encodes arrived as a docstring.
                    # A whole call with an error before the cut keeps its
                    # own line (frame 121's second review, case A).
                    continue
                if isinstance(call, toolproto.ToolError):
                    outcome.errors.append(call.reason)
                    feedback.append(f"ERROR {call.raw}: {call.reason}")
                    told_to_end = False
                    continue
                err = toolproto.validate(call, allowed)
                if err:
                    outcome.errors.append(err.reason)
                    feedback.append(f"ERROR {call.raw}: {err.reason}")
                    told_to_end = False
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
                call_path = _path_arg(sb, call)
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

                # A copy of a write that landed in this session. The door
                # refused such a copy as a twin, and seats read the refusal
                # as a loss of the landed row: s117 of night 171 logged five
                # faults on it (night 170's W8). The copy changes nothing, so
                # it is answered and not run. A copy of a refused call is no
                # copy here, and it goes to its door. The answer is an OK
                # line, so it holds nothing back and is never held.
                copy = (landed.get(key) if call.name not in read_fns
                        and key in already_run else None)
                if copy is not None:
                    copies += 1
                    told_to_end = False
                    if key not in copied_keys:
                        copied_keys.add(key)
                        feedback.append(
                            f"OK {call.name} -> done at turn {copy[0]} of this "
                            f"session: {copy[1]}. It stands, and "
                            f"{api.LANDED_STANDS}.")
                    continue

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

                staged_before = list(sb.ctx.writes or [])
                sent_before = len(getattr(sb.ctx, "outbound", None) or [])
                try:
                    repeat = key in already_run
                    try:
                        result = sb.call(call.name, *call.pos, **call.args)
                    finally:
                        rows, sent = staged_rows(staged_before, sent_before)
                        drop_landed(rows)
                    # A call that ran is the newest answer, so the door's
                    # end no longer stands. The review of d77bdec, C2: a
                    # write landed after the step, and without this the
                    # session ended with the write uncommitted.
                    told_to_end = False
                    # A write is the one act that can change an answer the
                    # session already holds, so it drops what that path has
                    # been read as. A commit names the paths it reached in its
                    # result. Neither drops a write: see the registration
                    # below.
                    if call.name == "code.write" and call_path:
                        forget(call_path)
                    elif call.name == "code.commit" and isinstance(result, dict):
                        for touched in result.get("touched") or ():
                            if isinstance(touched, str):
                                forget(touched)
                    # The result's own cap, or what this turn has left of its
                    # total, whichever is smaller. `_render` says where it cut
                    # and, for a source span, the exact call that fetches the
                    # rest -- so the per-turn total reuses the sentence the
                    # per-result cap already says rather than inventing one.
                    # The notice is paid for out of what is left, so a result
                    # the turn's room binds comes back inside that room. A
                    # result its own cap binds keeps the whole cap: the
                    # reserve at the top of the turn covers that one.
                    #
                    # The turn's first source read is the exception: it takes
                    # SOURCE_CHARS whatever the room holds. `_fit` lets the
                    # wake reach two thirds of the budget, and at that size the
                    # room falls to 5,491 -- under the 6,000 at which the 9B
                    # re-asked a cut span five times and never wrote (the note
                    # at `SOURCE_CHARS` above). Repair 3 is here to stop the
                    # *second* source read, and a floor under the first still
                    # does that. `_cap_exchange` absorbs the overrun.
                    limit = (SOURCE_CHARS if call.name == 'code.source'
                             else RESULT_CHARS)
                    cap = (limit if call.name == 'code.source' and not source_served
                           else min(limit, max(result_room - _CUT_NOTE_CHARS, 0)))
                    withheld = cap < MIN_RESULT_CHARS
                    shown = (f"ran, and this turn has no room left for its "
                             f"result ({min(TURN_RESULT_CHARS, budget):,} "
                             f"characters of results already). Ask for it "
                             f"again in your next turn, on its own"
                             if withheld else _render(result, cap))
                    # The answer is the same answer, or it is not. Nothing else
                    # decides the line below, so read-after-write needs no case
                    # of its own.
                    would_repeat = repeat and answered.get(key) == shown
                    # A repeated write of the text the file holds is one act.
                    # Frame 93 answers it with a sentence that differs from
                    # the first answer, so equality alone paid full freight
                    # (the gate at 7808f3a). The sentence rides in the line.
                    same_write = (call.name == "code.write" and not withheld
                                  and isinstance(result, dict)
                                  and isinstance(result.get("unchanged"), str))
                    would_repeat = would_repeat or (repeat and same_write)
                    # And the answer is above only while the block that carried
                    # it is still in this prompt. The middle eviction takes
                    # blocks, and the repeat line then sent a seat to read a
                    # turn that is not there: 8 of 8,183 recorded prompts
                    # carried both lines, and all 8 of the 8 that could
                    # (frame 46's design record, section 2.6). The eviction
                    # notice is true as written, so the repeat line is what
                    # gives way. A repeat the eviction emptied is not
                    # suppressed.
                    #
                    # An earlier *turn* answered it, or this one did. A repeat
                    # inside one reply is answered by a block this prompt never
                    # held, so membership alone called it evicted and served it
                    # again: three identical calls in one reply came back as
                    # 14,189 characters and no refusal, against 242 characters
                    # and one refusal before the eviction test existed. That is
                    # the s71 storm the refusal stops (the diff review of
                    # 0cc624b, finding 1). The eviction notice is sticky,
                    # because `_fit` writes it back every turn, so the turn
                    # number is what separates the two cases.
                    evicted = (_EVICTED_PHRASE in user
                               and answered_at.get(key, iteration) < iteration
                               and answered.get(key, "") not in user)
                    unchanged = would_repeat and not evicted
                    # Registered after the call, never before it. Registered
                    # first, a call that failed and was then sent again with
                    # identical arguments had its success swallowed by the
                    # repeat line (frame 43, 2026-09-19).
                    #
                    # A withheld result is registered by nothing. The sentence
                    # above is the same sentence for every call, so a second
                    # withholding of the same key compared equal to the first
                    # and the seat was told the answer was unchanged since it
                    # asked -- about a result it had never been shown (the diff
                    # review of 34c3e72, F1).
                    if not withheld:
                        already_run.add(key)
                        answered[key] = shown
                        answered_at[key] = iteration
                        enter_landed(key, call.name, shown, rows, sent,
                                     iteration)
                        # A write is never indexed by the path it writes, so no
                        # invalidation reaches it. A commit changes what a read
                        # of that path returns; it does not change what the
                        # write that landed it returns. Indexed, a commit
                        # dropped the key of the write in its own reply, and
                        # the next identical write paid full freight again
                        # (frame 43, pass 2, 2026-09-19).
                        if call_path and call.name != "code.write":
                            by_path.setdefault(call_path, set()).add(key)
                    # Rule 2 of frame 77: the answer the window took is served
                    # again, and no refusal points at a block the seat cannot
                    # see. The bound moved from the askings to the renders. A
                    # key is served three times in a session, and the asking
                    # after that is refused by the room and not by the count,
                    # because a result the exchange has no room for is evicted
                    # on every turn however often it is sent (the design review
                    # of frame 77, finding 3).
                    #
                    # The storm is a second copy in one reply, and the eviction
                    # test cannot see it: an answer made this turn is not in
                    # this turn's prompt. `served_keys` is that test, and it
                    # keeps the s71 shape closed.
                    stormed = key in served_keys and served.get(key, 0) >= 2
                    if would_repeat and evicted and served.get(key, 0) >= SERVE_CAP:
                        # The seat is asked for a narrower span, which the
                        # window can hold. Night 88's s137 was served in full at
                        # turns 7, 8 and 9 and died with nothing written: a
                        # result bigger than the exchange comes back for ever
                        # and buys nothing. Frames 53 and 56 own the fitting
                        # itself; this line only stops the loop.
                        #
                        # The reason names the window, not the room. Night
                        # 99, s132: results of 2,186 to 8,642 characters in a
                        # 26,309 budget, and the other blocks took the room
                        # (frame 100). `nightreport` greps both phrases.
                        why = ("served three times this session, and the "
                               "window took it each time; not served again")
                        repeated[key] = repeated.get(key, 0) + 1
                        if key not in refused_keys:
                            refused_keys.add(key)
                            outcome.errors.append(
                                f"repeat refused: {call.name} {why}")
                            turn_refusals.add((call.name, why[:160]))
                            seat_refusals = getattr(sb.ctx, "refusals", None)
                            if seat_refusals is not None:
                                seat_refusals.append((call.name, why, "Repeat"))
                            # A span is a step only for a call that takes one.
                            # Night 119's s260 was told to ask `tests.load` for
                            # a narrower span, and `tests.load` takes
                            # `batch_id` only (frame 121's interview, D). The
                            # window took the result, so no text points at it:
                            # all 24 refusals of night 119 stood in a prompt
                            # with no copy (frame 121's diff review, 1).
                            bound = _bound_of(sb, call.name)
                            if bound:
                                step = (f"Ask {call.name} for {bound}, "
                                        f"or finish without it.")
                            else:
                                step = ("Your prompt does not hold this "
                                        "result, and the window cannot hold "
                                        "it. Act without it, or finish.")
                            feedback.append(
                                f"ERROR {_call_tag(call, len(calls))}: {why}. "
                                f"{step}")
                    elif would_repeat and not evicted and (
                            stormed or repeated.get(key, 0) >= 1):
                        # The third identical call, refused. Session s71 sent
                        # 331 calls in one reply on both nights, 327 of them
                        # answered by the line below, and those 90,000
                        # characters of repeats became turn 2's whole prompt.
                        # Counted like any other refusal: the refusal counter is
                        # the only guard that stops a seat that repeats its
                        # calls while varying the prose around them.
                        #
                        # Once per key per turn, and the later copies get no
                        # line at all. The refusal is longer than the line it
                        # replaces -- 149 characters against 90 for
                        # `surveys.consult`, 173 against 86 for `code.source` --
                        # so 327 copies of it grew the very prompt repair 2 and
                        # repair 3 exist to shrink (the diff review of 34c3e72,
                        # F4). One sentence is the warning. The copies are the
                        # fault.
                        why = ("asked three times this session and the answer "
                               "has not changed; not answered again")
                        repeated[key] = repeated.get(key, 0) + 1
                        if key not in refused_keys:
                            refused_keys.add(key)
                            # The name goes after the colon. `rota/testkit/
                            # fixtures.py:913` reads a dotted prefix as a call a
                            # guard threw out and takes it off the forbidden-call
                            # score, and this call ran: the refusal is of the
                            # answer, not of the act.
                            outcome.errors.append(
                                f"repeat refused: {call.name} {why}")
                            turn_refusals.add((call.name, why[:160]))
                            seat_refusals = getattr(sb.ctx, "refusals", None)
                            if seat_refusals is not None:
                                seat_refusals.append((call.name, why, "Repeat"))
                            # This branch is the answered-and-present case, and
                            # the sentence says so. "Use what it returned
                            # earlier" was said in exactly the evicted case,
                            # about a result the seat could not see, and rule 2
                            # sends that case to the serve below. The eviction
                            # can still take the block between this line and
                            # the reading of it, and then the key is evicted
                            # and the next asking is served again.
                            #
                            # Frame 119 put "ask once more and it is served
                            # again" here. Night 115, s33 to s35, then repeated
                            # ten calls where night 113 attested, so the
                            # sentence was reverted (frame 119, pass 3).
                            #
                            # Frame 169 keeps the sentence and checks it once
                            # more after the next fit, at `_repoint`.
                            line = (f"ERROR {_call_tag(call, len(calls))}: "
                                    f"{why}. {_IN_THIS_PROMPT}")
                            feedback.append(line)
                            # An identical line from an earlier turn is one
                            # pointer, because `_repoint` reads the newest
                            # copy of a line.
                            if (key, line, call.name) not in pointers:
                                pointers.append((key, line, call.name))
                    elif unchanged:
                        repeated[key] = repeated.get(key, 0) + 1
                        # The stalled sessions asked `surveys.consult` three
                        # times and `glossary.consult` twice, and each copy paid
                        # full freight into a transcript that was already
                        # overflowing. The answer has not changed -- nothing the
                        # session did could have changed it -- so say so in a
                        # line rather than in four thousand characters.
                        #
                        # The line names the call that returned the answer. It
                        # says nothing about where the answer sits, because a
                        # claim about this prompt is written one turn before it
                        # is read, and the eviction runs in between. `evicted`
                        # is tested against the prompt the seat has just read,
                        # so "the answer is above" was true when the guard wrote
                        # it and false when the seat read it: night 88's s137
                        # saw the span at turns 3, 4 and 5, saw it gone at turn
                        # 6, and was told at turn 6 that the answer was above.
                        # One claim removed closes that, because a line that
                        # makes no claim about this prompt cannot be one turn
                        # early.
                        #
                        # Two wordings, and the provenance is the difference.
                        # 4,907 of 18,435 cassettes carry the asked-for line and
                        # 572 carry the pushed twin (measured 2026-09-20), so
                        # each keeps the half that names how the call ran.
                        #
                        # The eviction is not what drives the repeated reads.
                        # 1,249 prompts carry this line with nothing evicted,
                        # where the answer really is above and the session asked
                        # again regardless.
                        feedback.append(
                            f"OK {call.name} -> {_PUSHED_REPEAT} What "
                            f"{call.name} returned then still stands."
                            if key in pushed_keys else
                            f"OK {call.name} -> {_ASKED_REPEAT} "
                            f"{result['unchanged']}"
                            if same_write else
                            f"OK {call.name} -> {_ASKED_REPEAT} What "
                            f"{call.name} returned then still stands.")
                    else:
                        # Charged here and nowhere else: a repeat costs a line,
                        # not a result, and a turn of repeats must not use up
                        # the room a real read needs. The `OK <name> -> ` the
                        # line carries is charged with it.
                        result_room = max(
                            0, result_room - len(shown) - len(call.name) - 7)
                        source_served = source_served or call.name == 'code.source'
                        if not withheld:
                            # The eviction emptied this key, so the result is
                            # served again and says why. The seat is told what
                            # happened and never told to read a turn the window
                            # took. Counted as a serve and not as an asking:
                            # the askings answered by a line bound the storm,
                            # and the renders bound the room (rule 2, frame
                            # 77). A withheld result was never shown, so it
                            # counts as nothing.
                            served[key] = served.get(key, 0) + 1
                            served_keys.add(key)
                            # The key is rendered in full again, so the seat
                            # reads the answer below the old refusal. The old
                            # pointer no longer names the newest copy, and it
                            # leaves (frame 169's review, finding 1).
                            pointers = [p for p in pointers if p[0] != key]
                        feedback.append(
                            f"OK {call.name} -> the earlier answer was "
                            f"{_EVICTED_PHRASE}, so this prompt does not hold "
                            f"it. {call.name} ran again: {shown}"
                            if would_repeat else f"OK {call.name} -> {shown}")
                except Exception as exc:               # tool error, not session-fatal
                    outcome.errors.append(f"{call.name}: {exc}")
                    # Six encodes in one reply, three refused: which three?
                    # clickI night 46 (2026-09-14): the Tester re-sent all
                    # six for four turns. On a multi-call turn the refusal
                    # names the call by its identifying argument.
                    # A held pass is a question, not a refusal. Probe (c)
                    # measured the `HELD` word (frame 201, review 4, finding 2).
                    word = "HELD" if isinstance(exc, api.PassHeld) else "ERROR"
                    feedback.append(f"{word} {_call_tag(call, len(calls))}: {exc}")
                    turn_refusals.add((call.name, str(exc)[:160]))
                    if isinstance(exc, api.LinesRefusal):
                        refused_pass.add((call.name, str(exc)[:160]))
                    told_to_end = isinstance(exc, api.EndRefusal)

            # Counted per turn, not per call: a reply with four calls refused
            # the same way is one turn of the conversation, not three (clickI
            # night 43, 2026-09-13, reconcile ended before it could attest).
            # The third turn is told once; a fourth ends the session.
            # Sorted, because the seat reads these lines and the cassette key
            # hashes them. A set of tuples iterates in hash-seed order, which
            # is per process, so a turn with two NOTE lines rendered them in
            # one order when recorded and the other order in a fresh process,
            # and the case missed on that turn alone (observed: frame 71,
            # ACT-DV-edit-inside-the-function, turn 8, 2026-09-23).
            for same in sorted(turn_refusals):
                refused_same[same] = refused_same.get(same, 0) + 1
                if same in refused_pass:
                    # Frame 170. The general note says the op will not be
                    # accepted, and a verdict still lands by two routes. On
                    # nights 120 and 128, 3 of 7 Critics sent one pass again
                    # in 3 or 4 later turns. The note comes on the second
                    # refusal, because a seat whose turns 1 to 3 are the
                    # same meets the verbatim stop before a third.
                    if refused_same[same] == 2:
                        feedback.append(
                            "NOTE verdicts.emit(result='pass') has been refused "
                            "the same way in two turns. It lands with "
                            "lines={'<criterion id>': '<the added line>'} for "
                            "each criterion, or as a fail after "
                            "verdicts.claim_encodes on the criterion it fails")
                    elif refused_same[same] > 3 and not stop_reason:
                        stop_reason = (f"{same[0]} was refused the same way in "
                                       f"four turns; the session ended on it")
                elif refused_same[same] == 3:
                    feedback.append(
                        f"NOTE {same[0]} has been refused the same way in three turns "
                        f"and will not be accepted again. Finish what remains "
                        f"(attest, answer, end) without it")
                elif refused_same[same] > 3 and not stop_reason:
                    stop_reason = (f"{same[0]} was refused the same way in four turns; "
                                   f"the session ended on it")
            turn_refusals = set()

            if held:
                feedback.append(
                    "NOT RUN, because you wrote them before the answers above "
                    f"came back: {', '.join(held)}. You have the answers now. "
                    "Send them again if they are still what you want.")

            if invented_tail:
                feedback.append(
                    "NOT RUN, because you wrote a tool result of your own "
                    f"ahead of them: {', '.join(invented_tail)}. The real "
                    "results of the calls that did run follow. Send the rest "
                    "again with those results in view.")

            # `said` is the text plus one line per native call. In text mode
            # it equals the text, so the history of a text run is unchanged.
            _append(transcript, kinds, _REPLY, said)

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
            #
            # Rule 1 stands above the break: a turn that invented a result has
            # calls it never ran, and ending here would leave them unrun for
            # ever. The seat gets the turn that sends them again (frame 77).
            if oneshot and (sb.ctx.writes or sb.ctx.outbound) and not invented_tail:
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
            _append(transcript, kinds, _RESULTS, "\n".join(feedback))

            # A reply of copies alone is the verbatim stop one turn early. The
            # seat says again what landed, and a next turn buys nothing (night
            # 170's W8). A repeated read beside a copy is a call, so the stop
            # does not fire: s222 of night 171 paired c_1 with
            # `glossary.lookup` at turns 4 to 6, and its session runs until
            # the seat sends no call (the W8 review, finding 3).
            if copies and copies == len(calls):
                outcome.errors.append(COPIES_END)
                break

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

        # A park verdict's contested criteria go to the Terminologist by the
        # door, whatever the session sent (the delta review of 172b373b,
        # finding 1).
        sandbox_mod.stage_park_relay(sb.ctx)
        # law 4: an uncommitted change never existed. The tree goes back to
        # HEAD before the rows land, so the closed notes land with them.
        outcome.errors.extend(_discard_at_end(conn, wake, sb.ctx, stage=True))
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
            # The mode the sandbox applied, and not the argument. A caller
            # that names none leaves it to the wake, and the record then says
            # what the session could actually do.
            mode=sb.ctx.mode,
            writes=[_as_write(w) for w in sb.ctx.writes],
            messages=_messages_from(sb, wake, session_id),
            tool_calls=sandbox_mod.drain_calls(sb.ctx),
            turns=turns,
            pins=pins.as_dict(),
            backend=getattr(backend, "name", ""),
            refusals=list(getattr(sb.ctx, "refusals", []) or []),
            errors=list(outcome.errors),
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
        after_landing(conn, result)
        # The record's half of a cut. An op that shortens what a role wrote
        # leaves a reason on the context, and `session_note` writes the runner's
        # account as the session's last turn, so a reader counts what the system
        # cut without replaying a prompt. The seat's half is the notice in the
        # result, and the two are independent on purpose: the principal's ledger
        # row is cut where the Critic has no call to change it (frame 46's
        # design record, section 2.7).
        #
        # `outcome.errors` is read by three readers, so a line added here is
        # three statements at once: the session's account through
        # `session_note`, the failure line `rota/core/loop.py` prints for an
        # uncommitted session, and the refused-call count in
        # `rota/testkit/fixtures.py`, which reads the text before a line's first
        # colon as a call name whenever it holds a dot. Never head a line here
        # with a dotted op name.
        outcome.errors.extend(getattr(sb.ctx, "cuts", None) or ())
        # After the discard, a landed note whose lines HEAD holds guards
        # nothing, so it closes in the database (frame 297's review 3,
        # finding 3).
        if wake.role == "developer" and sb.ctx.batch_id:
            lifecycle_mod.close_restored_notes(conn, sb.ctx.batch_id)
        session_note(conn, session_id, outcome.errors)
        outcome.committed = True
        outcome.result = result
        return outcome

    except Exception as exc:
        outcome.errors.append(f"session failed: {exc!r}")
        # A session that died before `build_prompt` has no system text, and
        # the register's `system_hash` column already spends '' on "written
        # before the column existed". Leaving '' here makes a crash read as a
        # legacy write-off, which is a row saying the wrong thing rather than
        # nothing (frame 54's fix pass, 2026-09-21).
        if not outcome.system:
            from ..llm.cassettes import UNBUILT

            outcome.system = UNBUILT
        release(conn, wake.role)
        sandbox_mod.drain_calls(sb.ctx)
        # The row a failed session leaves. Night 31 (2026-09-13): 69 deaths
        # on one error and nothing in the database to read.
        try:
            session_fail(
                conn, session_id=session_id, role=wake.role,
                trigger_msg=wake.message_id, wake_kind=wake.kind,
                wake_detail=wake.detail or "", wake_refs=list(wake.refs or []),
                pins={"model": pins.model, "temperature": pins.temperature,
                      "num_ctx": pins.num_ctx},
                turns=turns, error=f"{exc!r}")
        except Exception as row_exc:  # noqa: BLE001 -- the record must not hide the failure
            outcome.errors.append(f"and the failure row was not written: {row_exc!r}")
        # A failed session ends as surely as a normal one, so law 4's
        # discard runs here too (frame 297). The staged rows never land,
        # so the landed notes close in the database.
        try:
            lines = _discard_at_end(conn, wake, sb.ctx, stage=False)
            # The normal end discarded first, and then the landing failed.
            # The tree is clean now, so its lines are the record (review 4,
            # finding 1).
            held = [e for e in outcome.errors if e.startswith(
                (lifecycle_mod.DISCARDED, lifecycle_mod.NOT_PUT_BACK))]
            if not lines and held:
                session_note(conn, session_id, held)
            if lines:
                # The loop prints the last error, so the failure stays last
                # (frame 297's review 3, finding 2). The account turn comes
                # after the failure turn.
                at = next((k for k, e in enumerate(outcome.errors)
                           if e.startswith("session failed:")), len(outcome.errors))
                outcome.errors[at:at] = lines
                session_note(conn, session_id, lines)
            conn.commit()
        except Exception as gone_exc:  # noqa: BLE001 -- the record must not hide the failure
            outcome.errors.append(f"and the discard at the end failed: {gone_exc!r}")
        return outcome


def _discard_at_end(conn: sqlite3.Connection, wake: Wake, ctx, *,
                    stage: bool) -> list[str]:
    """Put a Developer session's batch worktree back to HEAD at the end, and
    return the account's lines: the paths put back, and the paths git could
    not put back. Only the Developer writes the tree, and a message wake
    gives other roles the running batch (frame 297). With `stage`, the
    closes of the open notes go to the session's own writes."""
    bid = getattr(ctx, "batch_id", None)
    if wake.role != "developer" or not bid:
        return []
    failed: list[str] = []
    gone = lifecycle_mod.discard_uncommitted(conn, bid, close_notes=not stage,
                                             failed_out=failed)
    if stage and gone:
        norm = {p.replace(chr(92), "/") for p in gone}
        for p in list(api._open_notes(ctx)):
            if os.path.normpath(p).replace(chr(92), "/") in norm:
                api._put_note(ctx, p, None)
    return lifecycle_mod.discard_lines(gone, failed)


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


# The parameters that bound a read to part of its result, and the words that
# name each one. `code.source` and `code.write` take `start` and `end`.
# `code.concordance` and `code.prose` take `limit` (frame 121's diff review,
# finding 5). A span wins, so the `code.source` line keeps its bytes.
_SPAN_PARAMS = frozenset({"start", "end"})
_LIMIT_PARAMS = frozenset({"limit"})


# The advice after every form of the cut line. Each sentence holds whether
# the last call was whole or cut.
_REPLY_CUT_ADVICE = ("Send less in one reply: one or two calls, then read "
                     "their results. For a long file, write the span you "
                     "changed with start and end copied from code.source, "
                     "not the whole file")


def native_default(conn=None) -> bool:
    """
    Whether a run speaks native tool calls when its caller does not say.

    The run's bound profile decides first. The `ROTA_PROFILE` profile
    decides next, because the register suite names its profile there and
    binds none (`llm.think_for` reads it the same way). Else the text
    protocol, so a run with no profile keeps its recordings (frame 323).
    With no connection only the environment decides, as for a register
    reader that has no run.
    """
    try:
        from ..llm import profile as _profile
        prof = _profile.of_run(conn) if conn is not None else None
        if prof is not None:
            return bool(prof.native_tools)
    except Exception:
        pass
    name = os.environ.get("ROTA_PROFILE")
    if not name:
        return False
    try:
        from ..llm import profile as _profile
        return bool(_profile.find(name).native_tools)
    except Exception:
        return False


def _native_calls(completion) -> list:
    """
    The completion's native calls, as the objects `extract_lenient` returns.

    The dispatch below the parse then runs them unchanged. A name arrives
    mangled, because a schema name cannot hold a dot (`toolschema.mangle`).
    """
    calls = []
    for nc in completion.tool_calls or []:
        name = toolschema.demangle(getattr(nc, "name", "") or "")
        args = getattr(nc, "args", None)
        if not isinstance(args, dict):
            # A string, a list or bad JSON names no arguments. Running the
            # call with none would hide the fault behind a door's refusal.
            calls.append(toolproto.ToolError(
                raw=f"{name}({args!r})"[:300],
                reason="could not parse arguments"))
            continue
        shown = ", ".join(f"{k}={v!r}" for k, v in args.items())
        calls.append(toolproto.ToolCall(name, dict(args),
                                        raw=f"{name}({shown})"))
    return calls


def _with_native_lines(text: str, calls: list) -> str:
    """
    The reply as the history shows it: the text, then one line per native
    call in call order, as `name(key=value, ...)`. With no native call it is
    the text unchanged, so a text run keeps its prompts and its recordings.
    """
    if not calls:
        return text
    lines = "\n".join(c.raw for c in calls)
    return f"{text.rstrip()}\n{lines}" if text.strip() else lines


def _cut_inside_last(calls: list, call_at: list, scanned: str,
                     allowed) -> bool:
    """
    Whether the output cut fell inside the last parsed call.

    A parse error is not a cut by itself. A whole call with a bad argument,
    then prose, then the cut, is an error of its own (frame 121's second
    review, case A). The cut broke the call only when the call runs to the
    end of the reply:

    - an argument list that never closes, which the parser writes as
      `name(...`, runs to the end by its definition;
    - any other error, or a call whose name is not a function of the role
      (`TOOL: code.wr`, case D1), runs to the end when its text does.
    """
    if not calls:
        return False
    last, at = calls[-1], call_at[-1]
    whole = isinstance(last, toolproto.ToolCall) and last.name in allowed
    if whole:
        return False
    raw = last.raw or ""
    if isinstance(last, toolproto.ToolError) and raw.endswith("(..."):
        return True
    start = scanned.find(raw, at) if raw else -1
    end = (start if start >= 0 else at) + len(raw)
    return end >= len(scanned.rstrip())


def _reply_cut_line(calls: list, inside: bool) -> str:
    """
    The cut line of a reply that held calls, built from its last call.

    "The last call did not run and nothing was written" was false in 39 of
    77 cut events of nights 113 to 119: the last parsed call was whole, and
    29 of them show an `OK` line (frame 121's diff review, finding 2). The
    runner skips a call the cut broke. The calls before it go through the
    loop, which can also hold or drop them, so the line promises results
    only for the calls that ran: 11 of 39 night events also show a `NOT
    RUN` line (frame 121's second review, findings 1 and 2).
    """
    head = "your reply was cut at the output budget before it ended"
    if not calls:
        return (f"{head}. It held no whole call, so no call ran and nothing "
                f"was written. {_REPLY_CUT_ADVICE}")
    if inside:
        before = (" The results of the calls before it that ran follow."
                  if len(calls) > 1 else "")
        return (f"{head}. The cut fell inside the last call, so that call did "
                f"not run.{before} {_REPLY_CUT_ADVICE}")
    return (f"{head}. The cut fell after the last call, so it broke no call. "
            f"The results of the calls that ran follow. {_REPLY_CUT_ADVICE}")


def _bound_of(sb, name: str) -> str | None:
    """What a smaller asking of `name` changes, read from its signature."""
    params = _param_sets(sb).get(name, (set(), set()))[1]
    if params & _SPAN_PARAMS:
        return "a narrower span"
    if params & _LIMIT_PARAMS:
        return "a smaller limit"
    return None


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
            # The ruling rests on the same grain. `frame.assign` stages the
            # row too; the second stage of one row is no write.
            api.stage_ref(sb.ctx, "frame_rulings", prefix, "grain", row["grain"])
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


def after_landing(conn: sqlite3.Connection, result: SessionResult) -> None:
    """
    What the world does once a session's writes are on record.

    Three acts, in order, and every one of them outside the session. A role that
    could perform any of them from inside would be deciding its own
    consequences, and a session that died between the act and the commit would
    leave the act with no rows to explain it.

    One function rather than three statements in `run_session`, so a test can
    land a session the way the loop lands one.
    """
    session_commit(conn, result)
    # A ruling the Liaison read lands now, through the one door, after
    # the reading is on record. Inside the session it would land a
    # ruling from a session that then died.
    if any(w.table == "rulings" for w in result.writes):
        from ..roles.principal import apply_rulings

        apply_rulings(conn)
    _refresh_index(conn, result)


def _refresh_index(conn: sqlite3.Connection, result: SessionResult) -> None:
    """
    The batch's worktree, re-indexed after the commit this session landed.

    `code.probe(pattern='echo_json')` returned nothing for a symbol the batch
    had committed (finding 42, click night 46): the index was built once at
    onboarding and nothing after a commit touched it. Keyed on the `batches`
    write that carries `head_commit`, so it is one build per Developer session
    that committed, not one per commit.

    Not inside `code.commit`: that would be a raw write on the session's
    connection, and a session that died after it would leave the index ahead of
    the rows that say the commit happened.

    A failure keeps the old index and says so in the session's record. An index
    of the wrong tree answers some probes wrongly; an emptied one tells every
    reader the codebase is gone.
    """
    landed = [w.row_id for w in result.writes
              if w.table == "batches" and "head_commit" in (w.values or {})]
    if not landed:
        return
    from ..onboarding import indexer
    from . import harness

    batch_id = landed[-1]
    tree = harness.worktree_of(conn, batch_id)
    if not tree:
        return
    try:
        indexer.refresh(conn, tree, main=False, batch_id=batch_id)
    except Exception as exc:                # noqa: BLE001 -- the index is not the session
        # Every exception, not a list of two. The session's writes are already
        # committed here, so anything that escapes reaches `run_session`'s
        # handler and fails a session whose rows are on record.
        #
        # Twice: in the session's record, for the reader of this session, and
        # under `index:<batch>`, for the next session's empty probe.
        indexer.note_refresh_failure(conn, batch_id, exc)
        session_note(conn, result.session_id,
                     [f"the code index still describes the tree as it was "
                      f"before this commit: {exc!r}"])


def _as_write(staged: tuple) -> Write:
    """Staged writes are (table, row_id, values) or (..., amends), or
    (..., "clear") for a junction table's rows that `values` names."""
    table, row_id, values, *rest = staged
    if rest and rest[0] == "clear":
        return Write(table, row_id, values, op="clear", amends=False)
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
            status=m.get("status") or "open",
            unresolved_note=m.get("unresolved_note"),
            config=dict(m.get("config") or {}),
        ))
    return out
