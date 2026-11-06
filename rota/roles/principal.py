"""
The principal seam.

The principal is a node in the graph but not a role in the system — it is a person
at a terminal. Arc tests, however, need a *scripted* principal keyed to step index.
Both must satisfy one protocol, or T2 can never run without retrofitting one.

The protocol is deliberately narrow, and mirrors exactly the edges the graph
grants Liaison toward the principal:

    receive : confirm | clarify | present   (Liaison -> principal)
    emit    : converse | verdict            (principal -> Liaison)

Nothing else crosses. A principal backend cannot write an artefact, cannot address
another role, and cannot see the frontier — it answers questions and holds final
authority, which is the whole of its power.
"""
from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass, field
from typing import Protocol

from ..core.db import (READING_REF, guess_item, mark_answered, table_of,
                       tables_of)
from ..core.runner import new_id
from ..core.db import journal_author


@dataclass
class Ask:
    """Something Liaison has put to the principal and is waiting on."""
    message_id: str
    verb: str                     # confirm | clarify | present
    refs: list[str] = field(default_factory=list)
    rendered: str = ""
    # The rulable rows in the order the page shows them. "2: no" means the
    # second numbered line, not the second ref.
    order: list[str] = field(default_factory=list)


@dataclass
class Answer:
    verb: str                     # converse | verdict | reply
    text: str = ""
    per_item: dict[str, str] = field(default_factory=dict)   # ref -> approve|contest|revise


class PrincipalBackend(Protocol):
    name: str

    def respond(self, ask: Ask) -> Answer | None:
        """Answer, or None to defer. Deferring is always allowed."""


class ScriptedPrincipal:
    """
    Canned answers keyed by step index, for arc tests.

    Deferral is representable — a `None` in the script means the principal saw the
    ask and chose not to answer yet, which the system must survive rather than
    treat as an error.
    """

    name = "scripted"

    def __init__(self, script: list[Answer | None]):
        self.script = list(script)
        self.seen: list[Ask] = []

    def respond(self, ask: Ask) -> Answer | None:
        self.seen.append(ask)
        return self.script.pop(0) if self.script else None


class TranscriptPrincipal:
    """
    Answers from a fixed mapping of verb -> answer, replaying indefinitely.

    Useful for the T1 cases that need *a* principal without caring which one; the
    scripted variant is for arcs where the sequence is the point.
    """

    name = "transcript"

    def __init__(self, answers: dict[str, Answer]):
        self.answers = answers
        self.seen: list[Ask] = []

    def respond(self, ask: Ask) -> Answer | None:
        self.seen.append(ask)
        return self.answers.get(ask.verb)


class ConsolePrincipal:                                    # pragma: no cover
    """The human. Same protocol, stdin instead of a script."""

    name = "console"

    def _read(self) -> str | None:
        """
        None on a closed stdin, which is a deferral rather than a crash.

        Piping a single line in took a whole run down with an `EOFError` raised
        inside `pump` -- the loop reached the point of asking the principal,
        which was the thing being proved, and died on the way to the question.
        """
        try:
            return input("> ").strip()
        except EOFError:
            print("(stdin closed — deferred)")
            return None

    def respond(self, ask: Ask) -> Answer | None:
        print(f"\n{ask.rendered or ask.refs}")
        if ask.verb in ("confirm", "present"):
            print(REPLY_HELP)
        raw = self._read()
        if not raw:
            return None
        return parse_reply(ask, raw)


REPLY_HELP = ("  Reply in your own words. The Liaison reads the reply against "
              "the page and lands it, or asks. Blank = decide later.")


def parse_reply(ask: Ask, text: str) -> Answer:
    """
    A person's words to an ask, as the Answer that carries them.

    No parser reads the words. Ruled 2026-09-10: the Liaison is the natural
    language seat, and a keyword list ("ok", "lgtm") was the layer that told
    a person "no" is not a reply. A reply to a confirm or a present lands as
    a `reply`: the ask stays open, the words go to the Liaison in `landing`
    mode, and the Liaison records the ruling it read (`rulings.rule`) or
    asks back. A reply to a park ask is a `reply` too. A reply to any other
    clarify is the answer, as before.

    Scripts do not come through here. A scripted principal builds a verdict
    `Answer` with `per_item` and lands it through the same door.
    """
    raw = text.strip()
    if not words_keep_open(ask):
        return Answer(verb="converse", text=raw)
    return Answer(verb="reply", text=raw)


def words_keep_open(ask: Ask) -> bool:
    """
    Whether words alone leave this ask open: a confirm, a present or a park ask.

    A park ask waits for a commit or a contest (ruled: Roman, 2026-09-27: a
    given-up batch waits for the principal). Words change nothing on the
    batch. A words answer closed the ask, and the contest the page named then
    had no gate to go through (observed: frame 87's review of b23d17b,
    2026-09-30).
    """
    from ..core.scheduler import park_ask_batch

    return (ask.verb in ("confirm", "present")
            or bool(park_ask_batch(ask.message_id or "")))


# ---------------------------------------------------------------------------
# The pump: move asks to the principal and answers back onto the frontier.
# ---------------------------------------------------------------------------

def pending_asks(conn: sqlite3.Connection) -> list[Ask]:
    """Open questions addressed to the principal.

    `converse` replies from Liaison are displayed, not asked — they carry prose
    rather than a decision, so they do not become a principal gate.

    An open shift question is returned alone, and every other ask waits
    open and unchanged behind it. An ask about an earlier request is held
    until the principal answers its shift question, and an ask about an item
    set aside is held until the item resumes. Night 137's principal answered
    walk 2's page m161 after walk 3's request (frame 193's design, 2.F.1
    and 2.F.4).

    ruling: frame 193, Roman 2026-10-10, the shift question blocks the asks behind it
    """
    rows = conn.execute(
        "SELECT id, verb, body_refs, body_text FROM messages "
        "WHERE status = 'open' AND to_role = 'principal' "
        "  AND verb != 'converse' ORDER BY seq").fetchall()
    shift = [r for r in rows if r["id"].startswith(SHIFT_ASK)]
    if shift:
        rows = shift
    else:
        held = held_asks(conn)
        rows = [r for r in rows if r["id"] not in held]
    return [
        Ask(message_id=r["id"], verb=r["verb"],
            refs=json.loads(r["body_refs"]),
            rendered=(page := render_page(conn, r["verb"],
                                          json.loads(r["body_refs"]),
                                          r["body_text"], ask_id=r["id"]))[0],
            order=page[1])
        for r in rows
    ]


def pending_replies(conn: sqlite3.Connection) -> list[Ask]:
    """Open Liaison `converse` replies that should be displayed to the principal."""
    return [
        Ask(message_id=r["id"], verb=r["verb"],
            refs=json.loads(r["body_refs"]),
            rendered=r["body_text"] or "")
        for r in conn.execute(
            "SELECT id, verb, body_refs, body_text FROM messages "
            "WHERE status = 'open' AND to_role = 'principal' AND verb = 'converse' "
            "ORDER BY seq")
    ]


def park_behind(conn: sqlite3.Connection, item: str, *,
                as_id: bool = False) -> str | None:
    """The statement of the request a parked item waits behind, its text or
    with `as_id` its id, or None."""
    row = conn.execute(
        "SELECT a.body_refs FROM item_parks p JOIN messages v ON v.id = p.cause_id "
        "JOIN messages a ON a.id = v.cause_id WHERE p.item_id = ? "
        "ORDER BY p.seq DESC, p.rowid DESC LIMIT 1", (item,)).fetchone()
    if row is None:
        return None
    for ref in json.loads(row["body_refs"] or "[]"):
        s = conn.execute("SELECT text FROM statements WHERE id = ?", (ref,)).fetchone()
        if s is not None:
            return ref if as_id else s["text"]
    return None


def aside_lines(conn: sqlite3.Connection) -> list[str]:
    """
    The state page's record of what the principal put aside: one block per
    request a parked item waits behind, and the dropped items. The record
    stays visible, as the composition's Records ask (frame 193's design,
    2.F.4).
    """
    from ..core.scheduler import park_kind

    try:
        rows = conn.execute("SELECT DISTINCT item_id FROM item_parks "
                            "ORDER BY item_id").fetchall()
    except sqlite3.OperationalError:
        return []
    behind: dict[str, list[str]] = {}
    dropped: list[str] = []
    for r in rows:
        item = r["item_id"]
        kind = park_kind(conn, item)
        text = conn.execute("SELECT text FROM items WHERE id = ?", (item,)).fetchone()
        text = (text["text"] if text else item).rstrip(".")
        if kind == "drop":
            dropped.append(f"  {text}.")
        elif kind == "park":
            asks = sum(1 for m in conn.execute(
                "SELECT body_refs FROM messages WHERE status = 'open' AND to_role "
                "= 'principal' AND verb != 'converse'")
                if (got := _reached(conn, json.loads(m["body_refs"] or "[]")))
                and got <= {item})
            notes = sum(1 for n in conn.execute(
                "SELECT id FROM ledger WHERE status = 'open'")
                if item in _items_reached(conn, n["id"]))
            # No page numbers a set-aside item, so a "resume" word has no
            # line to land on (the review of 61a0f41d, finding 6).
            behind.setdefault(park_behind(conn, item) or "the new request", []).append(
                f"  {text}. {asks} open page{'' if asks == 1 else 's'}, {notes} open "
                f"note{'' if notes == 1 else 's'}. It comes back when that request "
                f"is delivered or dropped.")
    out: list[str] = []
    for said, lines in behind.items():
        # A statement ends with a full stop, and ".:" reads as a typo (the
        # review of e406e976, finding 3).
        out.append(f"Waiting behind {said.rstrip('.')}:")
        out.extend(lines)
    if dropped:
        out.append("Dropped:")
        out.extend(dropped)
    return out


# The shipped line's words for the parked rows of each ledger kind (frame
# 204's design, section 4). The kinds not named here count as notes.
PARKED_WORDS = (
    (("default",), "choice the team made where you said nothing",
     "choices the team made where you said nothing"),
    (("invented",), "invented test value", "invented test values"),
    (("scope",), "change of scope the team noted", "changes of scope the team noted"),
    (("conflict",), "disagreement that no one on the team could answer",
     "disagreements that no one on the team could answer"),
    (("unaddressed_answer",), "question your answer left open",
     "questions your answer left open"),
)

# The shipped line for a merged batch whose head is a claim: the code already
# held the item, and the merge added tests only (frame 360, ruled: Roman,
# 2026-11-02 17:14, shape A of the design page).
CLAIMED_LINE = "No code changed. These tests show the code already does this."


def render_state(conn: sqlite3.Connection) -> str:
    """
    Where the run is, in words, for the person who waits on it.

    Every seat could say what the machine did: wake kinds, role names, row
    counts. No seat could say what happened. Measured as the principal
    (tips9, 2026-09-04): a walk built the code, failed six of seven tests,
    climbed the escalation ladder, and went quiet. Nothing was pending, so
    nothing was shown. A stopped run and a thinking run were the same picture.

    The state is composed here once, like an ask. First what waits on you,
    because that line asks for something. Then what shipped. Then what is
    stuck and what would move it. Read from the rows, so it is true of a
    database opened cold.
    """
    # A run that stopped because the model does not answer says so first.
    # Nothing else moves until the model answers (frame 355, pass 2).
    from ..core.db import get_config

    down = get_config(conn, "model_down")
    state = _render_state(conn)
    return f"{down}{chr(10)}{state}" if down else state


def _render_state(conn: sqlite3.Connection) -> str:
    """The state lines of `render_state`, without a stop of the run."""
    asks = pending_asks(conn)
    if asks:
        head = ("Waiting on you." if len(asks) == 1
                else f"Waiting on you: {len(asks)} things. The first is:")
        # His objections stay visible while an ask waits (review p3 of
        # frame 357, L1).
        mine = len(objected_rows(conn))
        tail = f"{chr(10)}Rows you said are not yours: {mine}" if mine else ""
        return head + chr(10) + asks[0].rendered + tail

    def count(sql):
        row = conn.execute(sql).fetchone()
        return row[0] if row else 0

    # Frame 204: the count of open faults, and no rows. The principal sees
    # that rota failed and is asked nothing (design, section 7, reader 3).
    faults = count("SELECT COUNT(*) FROM faults WHERE status = 'open'")
    fault_line = (f"Rota itself failed {faults} time{'s' if faults > 1 else ''} "
                  "this run. The people who build it have the list."
                  if faults else None)

    merged = count("SELECT COUNT(*) FROM batches WHERE status = 'merged'")
    running = count("SELECT COUNT(*) FROM batches WHERE status = 'running'")
    pending = count("SELECT COUNT(*) FROM batches WHERE status = 'pending'")
    approved = count("SELECT COUNT(*) FROM items WHERE approval = 'approved'")

    # Frame 360 (ruled: Roman, 2026-11-02 17:14): a claimed batch merged
    # its tests and no code, so it is not "built". A database older than
    # the mark has no claim.
    from ..core.db import _has_column

    claimed = (count("SELECT COUNT(*) FROM batches WHERE status = 'merged' "
                     "AND claimed_head IS NOT NULL "
                     "AND claimed_head = head_commit")
               if _has_column(conn, "batches", "claimed_head") else 0)
    built = merged - claimed

    out: list[str] = []
    if built:
        out.append(f"Done: {built} change{'s' if built > 1 else ''} built, "
                   "tested and merged.")
    # A parked row is shown quietly, as a count that asks nothing (ruled:
    # Roman, 2026-10-11 15:00, frame 204's design, section 4).
    # Each kind has its own words: a `scope` row is not a choice (frame
    # 316's review 2, finding 2). `ledger.list(shipped=...)` shows the rows.
    # The re-survey row has its own sentence below, so it leaves this count.
    from ..core.predicates import (FIRST_TOUCH_WORDS, LAZY_WORDS,
                                   RESURVEY_WORDS, lazy_count, resurvey_count)

    # A lazy row shown at first touch, and the record of that touch, are
    # the team's notes, not choices. The touch note showed them (frame 361).
    kinds = dict(conn.execute(
        "SELECT kind, COUNT(*) FROM ledger WHERE status = 'parked' "
        "AND substr(default_taken, 1, ?) != ? "
        "AND substr(default_taken, 1, ?) != ? "
        "AND substr(default_taken, 1, ?) != ? GROUP BY kind",
        (len(RESURVEY_WORDS), RESURVEY_WORDS, len(LAZY_WORDS), LAZY_WORDS,
         len(FIRST_TOUCH_WORDS), FIRST_TOUCH_WORDS)).fetchall())
    if merged and kinds:
        words = []
        for kind, one, many in PARKED_WORDS:
            n = sum(kinds.pop(k, 0) for k in kind)
            if n:
                words.append(f"{n} {one if n == 1 else many}")
        n = sum(kinds.values())
        if n:
            words.append(f"{n} other note{'s' if n > 1 else ''} from the team")
        listed = (words[0] if len(words) == 1
                  else ", ".join(words[:-1]) + " and " + words[-1])
        # The tail joins the Done line only. On the claimed line, "They
        # carry" read as the tests (frame 360, review p1, F3).
        if built:
            carry = "They carry" if built > 1 else "It carries"
            out[-1] += f" {carry} {listed}. Ask me to show them."
        else:
            out.append(f"The merged work carries {listed}. Ask me to show them.")
    if claimed:
        out.append(CLAIMED_LINE)
    # A re-survey after a merge asks nothing, so the state view shows it as
    # one sentence and no page (frame 358).
    notes = resurvey_count(conn) if merged else 0
    if notes:
        out.append(f"After the merge the team re-read the project and recorded "
                   f"{notes} note{'s' if notes > 1 else ''}. Ask me to show them.")
    # Under `lazy` the read asks nothing, so the view shows one sentence and
    # no page, in the shape of the re-survey line (ruled: Roman, 2026-11-03
    # 01:05, the design's 3.5).
    # The line promises no listing. The only listing, `ledger.list(shipped=)`
    # in the converse mode, finds rows of a merged item, and a lazy row
    # reaches no item (frame 361, pass 1b).
    # The line names every lazy row: the rows that wait, the rows a change
    # showed, and the rows that bind no code. A parked row that no count
    # names is invisible work (the second look of frame 361, finding 2).
    from ..core.lifecycle import first_touch_records

    waiting = lazy_count(conn)
    records = first_touch_records(conn)
    unbound = sum(len(h.get("rows") or ()) for h in records if h.get("batch") is None)
    shown = sum(len(h.get("rows") or ()) for h in records if h.get("batch") is not None)
    total = waiting + unbound + shown
    if total:
        parts = []
        if waiting:
            parts.append(f"{waiting} wait{'s' if waiting == 1 else ''} in the "
                         "ledger until a change touches "
                         f"{'it' if waiting == 1 else 'them'}")
        if shown:
            parts.append(f"{shown} {'was' if shown == 1 else 'were'} shown "
                         "when a change touched them")
        if unbound:
            parts.append(f"{unbound} bind{'s' if unbound == 1 else ''} no code")
        listed = (parts[0] if len(parts) == 1
                  else ", ".join(parts[:-1]) + ", and " + parts[-1])
        out.append(f"The team read the project and recorded {total} "
                   f"note{'s' if total > 1 else ''}. {listed[0].upper()}{listed[1:]}.")
    # F7, pass 1b: the summary after the merge names each removal that no
    # grant of his allows. It is information, and it holds nothing.
    gone = merged_removal_line(conn) if merged else ""
    if gone:
        out.append(gone)
    # A reading of a delivered request rides no page, so the state view
    # shows it, in the words the page uses (ruled: Roman, 2026-10-28 09:10,
    # frame 344; every answer is read back, ruled 2026-10-26 22:5x). No page
    # takes an answer to it, so the line asks for none (the review of P9,
    # finding 4).
    late = [line.removesuffix(READ_BACK_ASK)
            for line in (reading_line(conn, r) for r in readings_owed(conn)
                         if reading_delivered(conn, r)) if line]
    if late:
        out.append("Your answers about delivered work, as the team read them:")
        out += [f"  - {line}" for line in late]
    # A row he dropped stays the team's record of the code, so the view
    # shows it with his objection. No page asks him about it again (ruled:
    # Roman, 2026-11-02 11:43, frame 357, shape B).
    objected = objected_rows(conn)
    if objected:
        from ..core.runner import _resolve_refs

        rows = _resolve_refs(conn, objected)
        out.append(ACCOUNT_TODAY)
        for ref in objected:
            row = rows.get(ref)
            row = row if isinstance(row, dict) else {}
            text = next((row[k] for k in ("text", "headline", "body",
                                          "sense_short") if row.get(k)), ref)
            out.append(f"  - {text} ({NOT_MINE})")
    # A cold cockpit sees the cycle the walk printed, read from the rows
    # (ruled: Roman, 2026-09-24, an alert first). The line goes under what
    # is stuck.
    from ..core.cycles import cycle as _cycle
    try:
        looping = _cycle(conn)
    except Exception:                   # noqa: BLE001 -- a state page never fails on an alert
        looping = None

    # A parked batch is an open obligation, so the page counts it until a
    # commit discharges it. After night 93's park the page read "Done: 3"
    # only (observed: frame 86's pass 3 review, 2026-09-25).
    from ..core.scheduler import given_up, parked
    deferred = [r["id"] for r in conn.execute(
        "SELECT id FROM batches WHERE status = 'deferred' ORDER BY id")]
    held = [b for b in deferred if parked(conn, b)]
    # A deferred batch that is not parked waits for its resume, so it is
    # work in progress. A new commit on a parked batch left the page silent
    # until `batch_start` resumed it (observed: frame 86's pass 4 review,
    # 2026-09-25).
    pending += len(deferred) - len(held)
    # A batch parked on a quarantined key has its own line, and its keys
    # leave the gave-up line: its siblings still run. After a words answer
    # to the park ask the page said "nothing moves" (observed: frame 87's
    # pass 3 review, 2026-09-30). One line per batch, even at the cap too.
    keyed = {b: given_up(conn, b) for b in held}
    # A batch parked on the challenge count alone did not reach the attempt
    # cap, so it gets the park page's sentence (review p1 of frame 278, H2).
    from ..core.scheduler import challenged_reds
    looped = {b: challenged_reds(conn, b) for b in held if not keyed[b]}
    capped = [b for b in held if not keyed[b] and not looped[b]]

    # The line shows only while no ask is open: before the Liaison writes
    # the park ask, or when its wake is quarantined. No gate is open then,
    # so the line names no contest (observed: frame 87's review of b23d17b,
    # 2026-09-30). The ask comes next only while `park_ask` owes it and its
    # wake is live. A quarantined wake writes nothing (observed: frame 87's
    # review of 4a0ab5c, 2026-09-30).
    from ..core.predicates import park_ask as _park_ask
    from ..core.scheduler import quarantined_keys, tick_key

    # `quarantined_keys` is the one reader of a quarantine (fact F20).
    quarantined = set(quarantined_keys(conn))
    coming = {w.refs[1] for w in _park_ask(conn)
              if tick_key(w) not in quarantined}
    from ..core.scheduler import (park_ask_id, park_message_rests, park_reds,
                                  park_ruling, park_untested)

    def parked_line(b: str, keys: list[str]) -> str:
        # A park message that rests is the report: a note says the change
        # stops here, and a page approved whole with a check still red is
        # the ceiling (ruled: Roman, 2026-10-08, points 3 and 5).
        mid = park_ask_id(conn, b)
        row = conn.execute("SELECT body_refs FROM messages WHERE id = ?",
                           (mid,)).fetchone()
        if row is not None and park_message_rests(conn, mid):
            own, project = park_reds(conn, b)
            if b in json.loads(row["body_refs"] or "[]"):
                files = sorted({r["path"] or r["test_id"] for r in project})
                if files:
                    return (f"Stuck: {b} stops here. It breaks {', '.join(files)}. "
                            "A new commit on the change starts it again.")
                # No project red: another check stopped the batch. Dry run 5's
                # removal check gave "It breaks ." (wall 14), so the line says
                # what stopped it.
                stopped = _stalled_words(conn, keys) if keys else ""
                return (f"Stuck: {b} stops here. "
                        + (f"{_capital(stopped)}. " if stopped else
                           "No check of the project fails. ")
                        + "A new commit on the change starts it again.")
            ruled = park_ruling(conn, mid) or {}
            if any(v != "approve" for v in ruled.values()):
                return (f"Stuck: {b} is parked. The team rewrites the lines you "
                        "corrected, and I show you the page again after that.")
            # With no check to count, "0 of them still fail" says nothing
            # true (ruled: Roman, 2026-11-01, the amendment of point 3).
            if not own and park_untested(conn, b):
                return (f"Stuck: {b} stops here. You approved its lines as they "
                        "stand, and the team could not write the tests. A new "
                        "commit on the change starts it again.")
            return (f"Stuck: {b} stops here. You approved its checks as they "
                    f"stand, and {len(own)} of them still fail. A new commit "
                    "on the change starts it again.")
        return (f"Stuck: {b} is parked. {_capital(_stalled_words(conn, keys))}."
                + (" The other changes go on." if running or pending else "")
                + " A new commit on the change starts it again."
                + (" I ask you about it next." if b in coming else ""))

    parked_lines = [parked_line(b, keys) for b, keys in keyed.items() if keys]
    parked_lines += [f"Stuck: {b} is parked. " + " ".join(map(_looped_words, rows))
                     + " A new commit on the change starts it again."
                     for b, rows in looped.items() if rows]
    if capped:
        parked_lines.append(
            f"Stuck: {', '.join(capped)} {'is' if len(capped) == 1 else 'are'} "
            "parked. The tests failed past the attempt cap, and the team has "
            "run out of things to try. A new commit on the change starts it "
            "again. Tell me what to change.")
    parked_keys = {k for keys in keyed.values() for k in keys}
    # A tick tried past its cap and quarantined is the team giving up. It
    # outranks "building": on tipsH (2026-09-09) the Critic reviewed six times
    # without a verdict, was quarantined, the batch stayed running, and the
    # seat said "Building" because nothing else was pending.
    from ..core.scheduler import quarantined_keys

    # A step he dropped is no stall to him, so "Stuck" does not stay for
    # ever (review p4 of frame 354, finding 2).
    gave_up = [k for k in quarantined_keys(conn, constraint_zero=False,
                                           first_come=True, groups=False,
                                           ruled=False)
               if k not in parked_keys]
    if gave_up:
        # The words of a kind name who failed, so the line does not say the
        # team twice (review of F20 pass 1, finding 4).
        out.append(f"Stuck: {'; '.join(_gave_up_words(conn, gave_up))}. "
                   "Nothing waits on you, and nothing moves until that is "
                   "cleared. Tell me what to change.")
        out.extend(parked_lines)
        if looping is not None:
            out.append(looping.line())
        if fault_line:
            out.append(fault_line)
        return chr(10).join(out)
    out.extend(parked_lines)
    if running or pending:
        # At the batch's head commit, the harness's own notion of "now". The
        # first version picked the latest run by MAX(id), and ids are strings:
        # 'tr9' sorts after 'tr11', so a run that had gone green still read as
        # "1 test failing" (tipsH, 2026-09-09).
        failing = count(
            "SELECT COUNT(DISTINCT t.test_id) FROM latest_runs t "
            "JOIN batches b ON b.id = t.batch_id "
            "WHERE b.status = 'running' AND t.result != 'pass' "
            "AND t.commit_sha = b.head_commit")
        if failing:
            out.append(
                f"Stuck: the code is written, but {failing} test"
                f"{'s are' if failing > 1 else ' is'} still failing, and the "
                "team has run out of things to try. Tell me what to change, "
                "or what the tests should check.")
        else:
            out.append(f"Building: {running + pending} change"
                       f"{'s' if running + pending > 1 else ''} in progress.")
    out.extend(aside_lines(conn))
    if not out:
        if approved:
            out.append(f"Nothing waits on you and nothing is building. "
                       f"{approved} thing{'s' if approved > 1 else ''} approved so far.")
        else:
            out.append("Nothing waits on you and nothing is building. "
                       "Tell me what you want. I take it from there.")
    if looping is not None:
        out.append(looping.line())
    if fault_line:
        out.append(fault_line)
    return chr(10).join(out)


def render_ask(conn: sqlite3.Connection, verb: str, refs: list[str],
               question: str | None = None) -> str:
    """The page alone. `render_page` also returns the numbered rows' order."""
    return render_page(conn, verb, refs, question)[0]


def _strip_comment(line: str) -> str:
    """A line of code without its `#` comment. A `#` inside a string stays."""
    quote = ""
    for n, ch in enumerate(line):
        if quote:
            if ch == quote and line[n - 1] != chr(92):
                quote = ""
        elif ch in "'\"":
            quote = ch
        elif ch == "#":
            return line[:n].rstrip()
    return line.rstrip()


def _failure_line(output: str | None) -> str:
    """The error line of a pytest run, without its marker (fact F5)."""
    from ..core.harness import error_line

    # pytest cuts the `FAILED` line's reason to the terminal width: night
    # 132's run tr248 ends `assert F...` (frame 142's design review, finding 5).
    # The line's own period goes, because check_line's tail adds one.
    return error_line(output).removesuffix(".")


def check_line(conn: sqlite3.Connection, test_id: str) -> str:
    """
    One line that says what a test checks, read from its row: the test's
    name, the call it makes, the expression it asserts, and its last result.
    """
    # Mechanical, never written by a model. A model's line is a second
    # reading between the test and the principal, and the principal never
    # rules on a test (ruled: Roman, 2026-10-08, the park ask is a page
    # with rows, point 2).
    row = conn.execute("SELECT body FROM tests WHERE id = ?", (test_id,)).fetchone()
    lines = [_strip_comment(x) for x in ((row["body"] if row else "") or "").splitlines()]
    lines = [x for x in lines if x.strip()]
    name = next((m.group(1) for x in lines
                 for m in [re.match(r"\s*def test_?(\w*)\s*\(", x)] if m), "")
    words = " ".join(name.replace("_", " ").split()) or test_id
    assertion = next((x.strip()[len("assert"):].strip() for x in lines
                      if x.strip().startswith("assert ")), "")
    parts = [words]
    if assertion:
        # The call separates two tests of one criterion: night 132's cr_1
        # and cr_3 differ only in the call (frame 142's design, 2.F).
        read = set(re.findall(r"[A-Za-z_]\w*", assertion))
        at = next(i for i, x in enumerate(lines) if x.strip().startswith("assert "))
        call = next((x.strip() for x in reversed(lines[:at])
                     for m in [re.match(r"\s*([A-Za-z_]\w*)\s*=[^=]", x)]
                     if m and m.group(1) in read), "")
        if call:
            parts.append(f"calls {call}")
        parts.append(f"expects {assertion}")
    # The test's own batch only: an inherited test keeps its id across
    # batches (frame 210).
    run = conn.execute("SELECT result, output FROM latest_runs WHERE test_id = ? "
                       "AND batch_id = (SELECT batch_id FROM tests WHERE id = latest_runs.test_id)",
                       (test_id,)).fetchone()
    if run is None:
        tail = "Not run yet."
    elif run["result"] in ("fail", "error"):
        why = _failure_line(run["output"])
        tail = f"Fails: {why}." if why else "Fails."
    else:
        tail = "Passes."
    return ", ".join(parts) + ". " + tail


def _is_request_item(conn: sqlite3.Connection, ref: str) -> bool:
    """Whether the row is an item of the principal's request: in scope, not
    the account, not what the code does today, and not a description."""
    from ..core.runner import _is_description

    # A delivered item is no open request, by the version rule of
    # `open_requests`. A note about a delivered criterion put echo_json, at
    # v3 and delivered at v3, under "You asked:" (the delta review of
    # 2c602d1b, finding 7).
    row = conn.execute(
        "SELECT i.kind, i.version, p.provenance, "
        "       (SELECT CAST(value AS INTEGER) FROM config "
        "        WHERE key = 'delivered:' || i.id) AS delivered FROM items i "
        "JOIN item_provenance p ON p.id = i.id WHERE i.id = ?", (ref,)).fetchone()
    return bool(row and row["kind"] == "in_scope" and ref != "how_it_works"
                and row["provenance"] != "observed"
                and row["version"] > (row["delivered"] or 0)
                and not _is_description(conn, ref))


def _items_reached(conn: sqlite3.Connection, ref: str | None, hop: bool = True) -> list[str]:
    """The items that one ref reaches. A ledger row reaches what its
    `about_ref` reaches, one step and no further."""
    # No ref reaches no item. A caller can pass a NULL column, as the
    # agenda's swap did for an inherited test on night 141 (frame 209).
    if not ref:
        return []
    # A challenge row names its item as `items:<id>`. Night 137's
    # `challenge_items_confirm_with_default_on_eof` reached nothing (frame
    # 193's design, 2.F.9, finding 7).
    # A code line's key `guess:<item>` is a page alias of its item, so
    # `off_page` keeps it on its own request's page (frame 298's design,
    # 2.1, point 4).
    head, sep, rest = ref.partition(":")
    if sep and rest and head in ("items", "criteria", "tickets", "batches", "guess"):
        ref = rest
    if conn.execute("SELECT 1 FROM items WHERE id = ?", (ref,)).fetchone():
        return [ref]
    for sql in ("SELECT t.item_id FROM criteria c JOIN tickets t ON t.id = c.ticket_id "
                "WHERE c.id = ?",
                "SELECT item_id FROM tickets WHERE id = ?",
                "SELECT item_id FROM batches WHERE id = ?"):
        row = conn.execute(sql, (ref,)).fetchone()
        if row is not None:
            return [row[0]]
    cited = [r[0] for r in conn.execute(
        "SELECT src_id FROM refs WHERE src_table = 'items' AND kind = 'statement' "
        "AND target = ? ORDER BY src_id", (ref,))]
    if cited:
        return cited
    if hop:
        row = conn.execute("SELECT about_ref FROM ledger WHERE id = ?", (ref,)).fetchone()
        if row is not None and row["about_ref"]:
            return _items_reached(conn, row["about_ref"], hop=False)
    return []


def open_requests(conn: sqlite3.Connection) -> list[str]:
    """The requests not yet delivered at their version, most important first.

    An open request is an in-scope item that cites a ratified statement, is
    not observed and not a description, and whose version is above its
    `delivered:<item>` row. `tick_slicing` reads the same version rule.
    """
    from ..core.scheduler import not_described

    # The highest priority first, as the batch list orders it
    # (`api.batches_list`), then the id.
    return [r["id"] for r in conn.execute(
        "SELECT i.id FROM items i JOIN item_provenance p ON p.id = i.id "
        "WHERE i.kind = 'in_scope' AND i.id != 'how_it_works' "
        "  AND p.provenance != 'observed' "
        # A dropped item is no request (frame 357, pass 2).
        "  AND i.approval != 'dropped' "
        + not_described(conn, "i.id") +
        "  AND EXISTS (SELECT 1 FROM refs r JOIN statements s ON s.id = r.target "
        "              WHERE r.src_table = 'items' AND r.src_id = i.id "
        "                AND r.kind = 'statement' AND s.status = 'ratified') "
        "  AND i.version > COALESCE((SELECT CAST(value AS INTEGER) FROM config "
        "                            WHERE key = 'delivered:' || i.id), 0) "
        "ORDER BY i.priority DESC, i.id")]


# ---------------------------------------------------------------------------
# The request boundary (frame 193's design, 2.1 as amended by 2.F).
#
# A request is a principal `converse` with no cause: the walk and the TUI
# both write one with the entry as its ref. A page sent about an earlier
# request is held from the principal's view until the principal answers the
# shift question, because a question changes nothing (the composition, Flows).
# ---------------------------------------------------------------------------

SHIFT_ASK = "m_shift_"


def _request_entries(conn: sqlite3.Connection, body_refs: str | None) -> list[str]:
    """The entries a request message carries, in their order."""
    try:
        refs = json.loads(body_refs or "[]")
    except (TypeError, ValueError):
        return []
    return [r for r in refs if isinstance(r, str) and conn.execute(
        "SELECT 1 FROM entries WHERE id = ?", (r,)).fetchone()]


def current_request(conn: sqlite3.Connection, *, before_seq: int | None = None,
                    unread: bool = True) -> dict | None:
    """
    The newest request boundary, or None.

    A request with a statement is a boundary. A request that is still open
    is a boundary until a seat reads it, so a page is held in the step before
    any session runs. A request read as a question has no statement and is
    no boundary (2.1, point 4). A request whose every statement supersedes
    one of an earlier request is a follow-up and no boundary (2.F.6).
    `before_seq` reads the request before that point, and `unread` False
    skips an open request with no statement.
    """
    sql = ("SELECT id, seq, status, body_refs FROM messages WHERE from_role = "
           "'principal' AND to_role = 'liaison' AND verb = 'converse' "
           "AND cause_id IS NULL")
    args: tuple = ()
    if before_seq is not None:
        sql += " AND seq < ?"
        args = (before_seq,)
    for m in conn.execute(sql + " ORDER BY seq DESC", args).fetchall():
        entries = _request_entries(conn, m["body_refs"])
        if not entries:
            continue
        marks = ",".join("?" * len(entries))
        stmts = conn.execute(
            f"SELECT id, text, supersedes FROM statements WHERE span_entry IN ({marks}) "
            "ORDER BY id", tuple(entries)).fetchall()
        if not stmts:
            if unread and m["status"] == "open":
                return {"id": m["id"], "seq": m["seq"], "entries": entries,
                        "statements": [], "texts": []}
            continue
        if all(s["supersedes"] for s in stmts):
            continue
        own = [s for s in stmts if not s["supersedes"]]
        return {"id": m["id"], "seq": m["seq"], "entries": entries,
                "statements": [s["id"] for s in own],
                "texts": [s["text"] for s in own]}
    return None


def contested_statement(conn: sqlite3.Connection, sid: str, *,
                        confirm_only: bool = False,
                        before_seq: int | None = None) -> str | None:
    """
    The id of the newest ruling on statement `sid` when that ruling is
    `contest`, else None.

    A stale ruling does not count. `confirm_only` reads the rulings of the
    confirm pages that name `sid`, and only landed ones. `before_seq` skips a
    ruling whose reply came at or after that point (frame 193's design, 2.G.3
    and 2.G.4).
    """
    # A dropped statement stays contested. Dry1's approve m78 came after the
    # drop r_m75, was the newest ruling, and `brief_ratify` admitted it
    # (frame 357).
    dropped = statement_drop(conn, sid)
    if dropped:
        return dropped
    # The rows on `sid` in `ruled_refs_live`, newest first (the seam
    # design, 3.1).
    sql = ("SELECT r.ruling_id, r.verdict FROM ruled_refs_live r "
           "JOIN messages a ON a.id = r.ask_id "
           "LEFT JOIN messages p ON p.id = r.reply_id "
           "WHERE r.ruling_status != 'stale' AND r.ref = ?")
    args: list = [sid]
    if confirm_only:
        sql += (" AND r.ruling_status = 'landed' AND a.verb = 'confirm' "
                "AND a.body_refs LIKE ?")
        args.append(f'%"{sid}"%')
    if before_seq is not None:
        sql += " AND COALESCE(p.seq, a.seq) < ?"
        args.append(before_seq)
    # Inside one ruling the newest row wins: a landed or keypress row over
    # the reading, as in `ruled` (fact F1, review 1, finding 3).
    r = conn.execute(sql + " ORDER BY r.ruling_seq DESC, r.row_seq DESC "
                     "LIMIT 1", tuple(args)).fetchone()
    return r["ruling_id"] if r is not None and r["verdict"] == "contest" else None


def contested_texts(conn: sqlite3.Connection, per_item: dict) -> dict[str, str]:
    """
    The current text of each criterion that `per_item` contests or revises.

    A criterion keeps no history, so every writer of a ruling row stores the
    text the principal ruled on here (frame 226, the review of 33cd99b2,
    finding 3).
    """
    texts: dict[str, str] = {}
    for ref, ruling in (per_item or {}).items():
        if ruling not in ("contest", "revise"):
            continue
        row = conn.execute("SELECT text FROM criteria WHERE id = ?",
                           (ref,)).fetchone()
        if row is not None:
            texts[ref] = row["text"]
    return texts


def last_ruling_on(conn: sqlite3.Connection, ref: str) -> dict | None:
    """
    The newest ruling on `ref`, or None.

    The dict holds the ruling's id, the verdict on `ref`, the principal's
    words, and the text `ref` held when he ruled, or None for an older
    ruling. A stale ruling does not count, as in `contested_statement`. The
    repair wake and the respecify door read this one function (frame 226).

    The rows come from `ruled`, the newest row on `ref`, so his keypress
    or the landed verdict wins over the reading of the same ruling (the
    seam design, pass 1; fact F1, review 1, finding 3). `words` stays the
    whole reply in this pass, so each reader gets the answer it got from
    `per_item`.
    """
    rows = ruled(conn, [ref], landed=False, newest=True)
    if not rows:
        return None
    r = rows[-1]
    return {"id": r["ruling_id"], "verdict": r["verdict"],
            "words": r["reply_words"] or "", "text": r["old_text"]}


def _target_key(said) -> str:
    """A target as the readers compare it: case-folded, with no quote marks,
    no backticks and no leading dashes around it."""
    return str(said or "").strip().strip("`'\"").lstrip("-").strip().casefold()


def grant(conn: sqlite3.Connection, ref: str, act: str,
          target=None) -> sqlite3.Row | None:
    """The newest landed row on `ref` with an act, when it grants `act` on
    `target`, or None.

    `target` None asks for the act on any target. A string or a list of
    strings asks for a row whose target is one of them. A row with a null
    act grants nothing, and a row with a null target grants only the call
    with no target (composition.md, Flows: "never ... treats silence as
    consent").

    A later row with no act takes back an act on the row itself: an act
    with no target, or with the kind `row` or `check`. Every later verdict
    on the ref names the row itself. A later row with no act keeps an act
    with a named target of another kind, as night 169's m37 on
    `get_app_dir:518`. When a target is given, the newest row with an act
    on that target decides. With no target, the newest row whose act is
    `act`, or whose act is on the row itself or on a target of `act`,
    decides. An `add` never ends another act (composition.md: "Only a
    ratified amendment to something approved revokes work downstream"; the
    reviews of pass 4, P4-3, and of pass 4c, P4c-2 and P4c-4).

    A later row with no act never ends an `add`. The add's target is a new
    line that is not on the page, so a plain verdict on the row it rides on
    says nothing about it. An add ends only by a later `keep` on the row,
    or by a later act on the row whose words hold the add's words.
    `criteria_page_acts` also ends it when a live criterion of the ticket
    holds its words (composition.md: nothing stops quietly; the review of
    pass 4d).
    """
    if not isinstance(ref, str) or not ref:
        return None
    rows = ruled(conn, [ref])
    wanted = ({_target_key(t)
               for t in ([target] if isinstance(target, str) else target) if t}
              if target is not None else None)
    if act == "add":
        adds = [r for r in open_adds(conn, ref)
                if wanted is None or (r["target"] is not None
                                      and _target_key(r["target"]) in wanted)]
        return adds[-1] if adds else None
    if wanted is not None:
        found = [i for i, r in enumerate(rows) if r["act"] is not None
                 and r["target"] is not None
                 and _target_key(r["target"]) in wanted]
    else:
        # A later act on the same named target replaces the act on this
        # ask too, so a keep on m37's line ends m37's remove.
        named = {_target_key(r["target"]) for r in rows
                 if r["act"] == act and not _on_the_row(r)}
        found = [i for i, r in enumerate(rows) if r["act"] == act
                 or (r["act"] not in (None, "add")
                     and (_on_the_row(r) or _target_key(r["target"]) in named))]
    if not found or rows[found[-1]]["act"] != act:
        return None
    row = rows[found[-1]]
    if _on_the_row(row) and any(r["act"] is None for r in rows[found[-1] + 1:]):
        return None
    return row


def open_adds(conn: sqlite3.Connection, ref: str) -> list[sqlite3.Row]:
    """Every landed `add` row on `ref` that no later row ended, oldest
    first.

    A later `keep` on the row ends an add, and so does a later act whose
    words hold the add's words. A later row with no act ends none. Two adds
    in other words both stay open, because the composition says nothing
    stops quietly (the review of pass 4d and 4e, P4de-2)."""
    if not isinstance(ref, str) or not ref:
        return []
    rows = ruled(conn, [ref])
    out = []
    for i, row in enumerate(rows):
        if row["act"] != "add":
            continue
        said = _fold(row["words"])
        if not any(later["act"] == "keep" or (later["act"] is not None and said
                                              and said in _fold(later["words"]))
                   for later in rows[i + 1:]):
            out.append(row)
    return out


def _fold(text) -> str:
    """Words as a span check compares them: case-folded, with each run of
    white space read as one space."""
    return " ".join(str(text or "").split()).casefold()


def _on_the_row(row) -> bool:
    """Whether an act is on the row itself: it has no target, or its target
    is the row or its check. A later verdict on the ref speaks to it."""
    return row["target"] is None or row["target_kind"] in ("row", "check")


def granted(conn: sqlite3.Connection, ref: str, act: str,
            target=None) -> bool:
    """True when his newest landed ruling on `ref` grants `act` on `target`.

    Every reader of what his words permit reads this one function, and none
    reads his words by a phrase (the seam design, pass 4). `grant` gives the
    row itself, for a reader that needs its line or its words.

    A later row with no act takes back an act on the row itself, with no
    target or with the kind `row` or `check`. It keeps an act with a named
    target of another kind. So a plain approve after a drop ends the drop,
    and a plain approve after m37 keeps its grant on `get_app_dir:518`. A
    later act on the same target replaces an act, and an `add` never ends a
    drop (the reviews of pass 4, P4-3, and of pass 4c, P4c-2 and P4c-4)."""
    return grant(conn, ref, act, target) is not None


def ruled(conn: sqlite3.Connection, refs=None, *, reply: str | None = None,
          ruling: str | None = None, ask: str | None = None,
          landed: bool = True, newest: bool = False,
          item: str | None = None, every: bool = False) -> list[sqlite3.Row]:
    """The rows of `ruled_refs_live` that a reader asks for, oldest first.

    A ruling gives one row per ref, the newest, at the place of its first
    row: a landed row, else a keypress row, else the reading's row (fact
    F1). `every` keeps each row, for `verdict_for`, which picks the source.

    `refs` keeps the rows on those refs. `item` adds a page key that names
    the item after a colon, as `guess:<item>`. `reply` keeps the rows of
    the newest landed ruling of that reply or verdict message. `ruling`
    and `ask` keep the rows of one ruling or of the rulings on one ask.
    `landed` keeps landed rulings only, else every ruling that is not
    stale. `newest` keeps the newest row on each ref.

    One query serves every reader of his ruling, so no reader re-derives it
    from `per_item` (the seam design, 3; composition.md, Records).
    """
    sql = ["SELECT * FROM ruled_refs_live WHERE "
           + ("ruling_status = 'landed'" if landed else "ruling_status != 'stale'")]
    args: list = []
    if refs is not None or item is not None:
        refs = [r for r in (refs or []) if isinstance(r, str)]
        alt = [f"ref IN ({','.join('?' * len(refs))})"] if refs else []
        args += refs
        if item is not None:
            key = f":{item}"
            alt.append("substr(ref, -?) = ?")
            args += [len(key), key]
        sql.append(f"({' OR '.join(alt)})" if alt else "0")
    if reply is not None:
        sql.append("ruling_id = (SELECT id FROM rulings WHERE status = 'landed' "
                   "AND (reply_id = ? OR verdict_id = ?) ORDER BY rowid DESC LIMIT 1)")
        args += [reply, reply]
    if ruling is not None:
        sql.append("ruling_id = ?")
        args.append(ruling)
    if ask is not None:
        sql.append("ask_id = ?")
        args.append(ask)
    rows = conn.execute(" AND ".join(sql) + " ORDER BY ruling_seq, row_seq",
                        tuple(args)).fetchall()
    if not every:
        rows = one_row_per_ref(rows)
    if newest:
        # The rows of the newest ruling per ref: an exclude keeps a row per
        # path (frame 345, pass 7b).
        last = {r["ref"]: r["ruling_id"] for r in rows}
        rows = [r for r in rows if last[r["ref"]] == r["ruling_id"]]
    return rows


def one_row_per_ref(rows: list) -> list:
    """One row per ruling and ref: the newest, at the place of the first.

    `land` writes the keypress rows and the `landed` rows beside the
    reading's rows of the same ruling (fact F1). A reader of a ruling's
    rows reads one row for each ref it rules, so it counts no ref twice.

    An exclude lands one row per path. So when the newest row is an
    exclude, the newest row of each other path of the same source and
    verdict stays beside it (frame 345, pass 7b)."""
    last = {(r["ruling_id"], r["ref"]): r for r in rows}
    out, seen = [], set()
    for r in rows:
        key = (r["ruling_id"], r["ref"])
        if key in seen:
            continue
        seen.add(key)
        top = last[key]
        if top["act"] != "exclude":
            out.append(top)
            continue
        paths = {p["target"]: p for p in rows
                 if (p["ruling_id"], p["ref"]) == key and p["act"] == "exclude"
                 and p["source"] == top["source"]
                 and p["verdict"] == top["verdict"]
                 and p["target"] != top["target"]}
        out += [*paths.values(), top]
    return out


def ruled_words(conn: sqlite3.Connection, refs, *, item: str | None = None,
                skip=frozenset()) -> list[str]:
    """His landed words on any of `refs`, one text per ruling, oldest first.

    The words are the rows' own. A ruling that also rules a ref of `skip`
    gives none. Its one caller is `api._ruling_texts`, which `code_commit`
    and `ledger_log` read (frame 322, proposal lines 1 and 3). The pushes
    show his whole reply on the same key set, through
    `runner._ruled_block` (frame 362).
    """
    rows = ruled(conn, refs, item=item)
    skipped = {r["ruling_id"] for r in ruled(conn, list(skip))} if skip else set()
    out: list[str] = []
    seen: set[tuple[str, str]] = set()
    for r in rows:
        said = (r["words"] or "").strip()
        if not said or r["ruling_id"] in skipped or (r["ruling_id"], said) in seen:
            continue
        seen.add((r["ruling_id"], said))
        out.append(said)
    return out


# The words a `ruled_refs` row stores. The verdicts are the stored words of
# `RULING_WORDS` and `SHIFT_WORDS` (the seam design's review, finding 6).
RULED_VERDICTS = ("approve", "contest", "revise", "resume", "park", "now",
                  "drop")
# `exclude` takes a path off a prediction and deletes no code. No deletion
# reader asks for it, so `granted` never reads it as a removal (seam pass 3b).
RULED_ACTS = ("drop", "keep", "rewrite", "add", "remove", "exclude")
TARGET_KINDS = ("row", "check", "sentence", "identifier", "source_line",
                "path", "request")
def ruled_ref_home(conn: sqlite3.Connection, ref: str) -> str | None:
    """The table that holds `ref`, or None.

    `db.table_of` finds the row (F22). A page numbers the ledger's homes, a
    batch, a ledger row and a code line, and the read-back line names a
    reply. A row of any other table is no line of a page."""
    from .api import LEDGER_HOMES
    from ..core.scheduler import rowless_key

    if not isinstance(ref, str):
        return None
    # A stopped step that names no row is a line he rules on. Its home is
    # its quarantine row, so his ruling stages no false fault (review p4 of
    # frame 354, finding 4).
    if rowless_key(conn, ref):
        return "tick_attempts"
    if ref.startswith(READING_REF) or guess_item(ref) is not None:
        return table_of(conn, ref)
    return table_of(conn, ref, among=LEDGER_HOMES + RULED_HOMES)


# The tables beside `LEDGER_HOMES` that a page or a question names. A ledger
# note can be about a ruling, and a question can be about a decision (frame
# 316's m191, frame 306's clarify about). This is a scope rule, and the order
# picks one table when an id lives in two (F22).
RULED_HOMES = ("batches", "ledger", "entries", "decisions", "rulings",
               "findings", "verdicts", "references_")


def ruling_rows(conn: sqlite3.Connection, ruling_id: str, page: list | None,
                reading: dict, *, words: str = "", source: str = "reading",
                words_from: str | None = None,
                unheld: str = "refuse", held: tuple = ()) -> list[dict]:
    """
    The `ruled_refs` rows of one ruling: one row per ref of `reading`.

    `reading` maps each ref to a verdict word, or to an object with
    `verdict` and, optionally, `act`, `target`, `target_kind`, `words` and
    `words_from`. `page` is the order of the page as the door read it, so a
    ref on the page keeps its line number. `words` is the whole reply, and a
    row with no words of its own carries it. The caller stages or inserts
    the rows: `rulings.rule` stages them, `land` inserts them.

    law 6: nothing is ruled on the principal's behalf. So the writer refuses
    a ref that no table holds, a verdict that is not stored, and an act that
    is not one of the acts (frame 300's red test). `unheld="skip"` builds no
    row for a ref that no table holds, and refuses nothing for it.
    `unheld="keep"` builds the row. Only `land` asks it, for the verdict it
    computed: a contest of a note's `about_ref` carries to the desk that
    assumed it, as the config map carried it before fact F1.
    `held` names the stopped steps that `land` read before it lifted or
    marked them, so their home is their quarantine row.
    """
    from ..core.db import ruled_ref_id
    from .api import guess_item

    if source not in ("reading", "keypress", "backfill", "landed"):
        raise ValueError(f"{source!r} is not a source of a ruled row")
    order = list(page or [])
    rows: list[dict] = []
    for ref, value in (reading or {}).items():
        value = {"verdict": value} if isinstance(value, str) else dict(value or {})
        verdict = value.get("verdict")
        if verdict not in RULED_VERDICTS:
            raise ValueError(
                f"{ref}: {verdict!r} is not a stored verdict. A row takes "
                f"{', '.join(RULED_VERDICTS)}")
        # Review p6 of frame 354, finding 2: the lift runs before the rows,
        # so `ruled_ref_home` found no home and staged a false fault.
        table = "tick_attempts" if ref in held else ruled_ref_home(conn, ref)
        if table is None and unheld == "skip":
            continue
        if table is None and unheld != "keep":
            raise ValueError(
                f"{ref!r} is a row that no table holds, so a ruling on it rules "
                f"nothing. Rule the rows of the page")
        act = value.get("act") or None
        if act is not None and act not in RULED_ACTS:
            raise ValueError(
                f"{ref}: {act!r} is not an act. An act is "
                f"{', '.join(RULED_ACTS)}, or none")
        kind = value.get("target_kind") or None
        if kind is not None and kind not in TARGET_KINDS:
            raise ValueError(
                f"{ref}: {kind!r} is not a target kind. A target kind is "
                f"{', '.join(TARGET_KINDS)}, or none")
        # A code line and a read-back line are no row with a version: the
        # home is the item or the reply, and their versions are not his.
        version = None
        if table not in (None, "messages") and guess_item(ref) is None and any(
                c[1] == "version"
                for c in conn.execute(f"PRAGMA table_info({table})")):
            got = conn.execute(f"SELECT version FROM {table} WHERE id = ?",
                               (ref,)).fetchone()
            version = got["version"] if got else None
        own = {
            "id": ruled_ref_id(ruling_id, ref), "ruling_id": ruling_id,
            "ref": ref, "line": order.index(ref) + 1 if ref in order else None,
            "verdict": verdict, "act": act, "target_kind": kind,
            "target": (str(value["target"]).strip() or None)
            if value.get("target") is not None else None,
            "words": (str(value.get("words") or "").strip()
                      or (words or "").strip()),
            "words_from": (value["words_from"] if "words_from" in value
                           else words_from),
            "old_text": contested_texts(conn, {ref: verdict}).get(ref),
            "ref_version": version, "source": source}
        rows += _identifier_grants(table, own)
        rows.append(own)
        # A page can show one row on two lines: night 174's m47 showed the
        # glossary term `parameter` on lines 8 and 47. Each line keeps its
        # own row, keyed by its line number, so no line reads as unruled
        # (frame 345, pass 5). The first line keeps the id of the ref.
        for line in [n for n, r in enumerate(order, 1) if r == ref][1:]:
            again = {**own, "id": ruled_ref_id(ruling_id, f"{ref}|line {line}"),
                     "line": line}
            rows += _identifier_grants(table, again)
            rows.append(again)
    return rows


def _identifier_grants(table: str | None, own: dict) -> list[dict]:
    """The grant rows of the names that his words on a contested criterion
    ask for, from the line parser's reading (fact F3).

    `criteria.respecify` lets a contested name come back only on a grant
    row with the name as its target. The Liaison's brief asks for no such
    target, so the record writes one for each name of the contested text
    that his words name (the F2 review, finding 2). The rows come before
    the Liaison's own row, so its act still decides every untargeted read.
    """
    from .api import _line_reading, _named_tokens

    if table != "criteria" or own["verdict"] not in ("contest", "revise"):
        return []
    names = (_line_reading(own["words"]).names
             & _named_tokens(own["old_text"] or "")) - {own["target"]}
    return [{**own, "id": f"{own['id']}~{name}", "act": "rewrite",
             "target_kind": "identifier", "target": name}
            for name in sorted(names)]


def insert_ruling_rows(conn: sqlite3.Connection, rows: list[dict]) -> None:
    """Insert the rows `ruling_rows` built. A replay of the same ruling
    builds the same ids, so the insert ignores a row on file."""
    for row in rows:
        cols = list(row)
        conn.execute(
            f"INSERT OR IGNORE INTO ruled_refs ({', '.join(cols)}) "
            f"VALUES ({', '.join('?' for _ in cols)})", [row[c] for c in cols])


# The words of a verdict on the read-back line. An approve with no act
# goes into the count clause (the seam design, 2.3).
_READ_BACK_VERDICT = {"approve": "is approved", "contest": "is wrong",
                      "revise": "is to change", "park": "waits",
                      "now": "comes first", "drop": "is dropped",
                      "resume": "resumes",
                      # A stopped step takes the words of its own menu. Its
                      # approve is his 'drop', and its contest or revise is
                      # his 'try again' (review p5 of frame 354, finding 1).
                      # A retry is never "is wrong" (review p6, finding 1).
                      "step approve": "is dropped",
                      "step contest": "runs again",
                      "step revise": "runs again"}
# The read-back line quotes the start of his answer. A clock time in the
# page changes the prompt of every recorded case on each run.
READ_BACK_WORDS = 8
# The ask that ends a read-back line on a page. The state view leaves it out.
READ_BACK_ASK = " Say ok, or say what we misread."


def _step_key(ref) -> bool:
    """The ref is a tick key, so its page line is a stopped step."""
    return isinstance(ref, str) and "|tick:" in ref


def _step_retry(ref, verdict) -> bool:
    """His ruling runs the stopped step `ref` again."""
    return _step_key(ref) and verdict in ("contest", "revise")


def _step_name(conn: sqlite3.Connection, key: str) -> str:
    """The words of the stopped step `key`, with no count of attempts."""
    from ..core.scheduler import key_parts

    kind = key_parts(key)[1].replace("tick:", "")
    what = _key_about(conn, key)
    return f"{_tick_words(kind)}{f' for {what}' if what else ''}"


def _key_about(conn: sqlite3.Connection, key: str) -> str:
    """The words of what the tick key `key` is about, or ''."""
    from ..core.scheduler import key_parts

    refs = key_parts(key)[2]
    # A key of kind `quarantined` holds another tick key as its ref. The
    # comma split cut that key raw, so the page said "for critic|tick:..."
    # (review p8 of frame 354, finding 5). The inner step is read by its
    # own words, in quotes.
    inner = ",".join(refs)
    if _step_key(inner):
        return f'"{_step_name(conn, inner)}"'
    return ", ".join(w for w in (_ref_words(conn, r) for r in refs) if w)


def _row_name(conn: sqlite3.Connection, ref) -> str:
    """A row of an earlier page by its words, in quotes, or '' when the row
    has none: a step by `_step_name`, an item or a criterion by its text."""
    # Review p8 of frame 354, finding 3: the step words are a clause, so
    # they go in quotes and the sentence keeps one verb.
    if _step_key(ref):
        return f'the step "{_step_name(conn, ref)}"'
    # `tables_of` is the one reader of an id's table (fact F22).
    from ..core.db import table_of

    table = table_of(conn, ref, among=("items", "criteria"))
    if table is None:
        return ""
    # `table_of` reads `guess:<item>` as its item, and that line is the
    # guess, not the item. No row has the ref as its id, so the caller
    # names the line by its number.
    row = conn.execute(f"SELECT text FROM {table} WHERE id = ?",
                       (ref,)).fetchone()
    text = ((row["text"] or "") if row is not None else "").strip()
    return f'"{text}"' if text else ""


def _is_reading(ref) -> bool:
    return isinstance(ref, str) and ref.startswith(READING_REF)


def readings_owed(conn: sqlite3.Connection,
                  page: list | None = None) -> list[str]:
    """The `reading:<reply id>` refs that the next page reads back, oldest
    first. `page` names the refs of a present or a confirm page, and then
    only the readings that ride that page come back (`page_readings`).

    A reply is owed while the Liaison's landed reading of it has rows and no
    landed row rules its read-back line. His approve confirms the rows. His
    contest makes new rows, and the next page reads those back once. A
    keypress row and a back-filled row are no reading, so they owe nothing
    (the seam design, 2.3; ruled: Roman, 2026-10-26 22:5x, "every time").
    """
    out: list[str] = []
    # A step retry is read back too, so `read_back_rows`, the line and the
    # landing wake agree (ruled: Roman, 2026-10-26 22:5x, "every time").
    for r in conn.execute(
            "SELECT reply_id FROM ruled_refs_live WHERE source = 'reading' "
            "AND reply_id IS NOT NULL AND ruling_status = 'landed' "
            "AND status != 'superseded' AND confirmed_by IS NULL "
            "AND substr(ref, 1, ?) != ? GROUP BY reply_id "
            "ORDER BY MIN(ruling_seq)",
            (len(READING_REF), READING_REF)).fetchall():
        ref = READING_REF + r["reply_id"]
        if not conn.execute(
                "SELECT 1 FROM ruled_refs_live WHERE ref = ? "
                "AND ruling_status = 'landed'", (ref,)).fetchone():
            out.append(ref)
    return out if page is None else page_readings(conn, page, out)


def page_readings(conn: sqlite3.Connection, refs: list,
                  readings: list[str]) -> list[str]:
    """The readings of `readings` that ride the page of `refs`.

    A page is about one request, so a reading rides the page of its own
    request. A page of no request takes the account's readings. A reading
    of a delivered request rides no page, and the state view shows it
    (ruled: Roman, 2026-10-28 09:10, frame 344). A run with no request
    message has one request, so every reading of it rides.
    """
    live = [r for r in readings if not reading_delivered(conn, r)]
    if not current_request(conn, unread=False):
        return live
    req = page_owner(conn, [r for r in refs or [] if not _is_reading(r)])
    return [r for r in live if request_of(conn, r) == req]


def reading_delivered(conn: sqlite3.Connection, ref: str) -> bool:
    """True when the request of a reading is delivered or dropped."""
    from ..core.predicates import _request_finished

    req = request_of(conn, ref)
    return req is not None and _request_finished(conn, {"entries": [req]})


def read_back_rows(conn: sqlite3.Connection, reply: str,
                   shown: list | tuple = ()) -> list:
    """The rows that the read-back line of reply `reply` reads back, one
    per ref. The line says how the team read his words, so only the
    reading's rows count, never a keypress row or a `landed` row (fact F1,
    review 1, finding 2). A `reading:` ref is the line itself. The line and
    the landing wake read this one function.

    `shown` is the order of the page that carries the line. A retry of a
    step that the page shows is no row here, because the step's own line
    says "You asked me to try it again" (review p7 of frame 354, finding 1).
    """
    return one_row_per_ref([
        r for r in ruled(conn, reply=reply, every=True)
        if r["source"] in ("reading", "backfill")
        and not _is_reading(r["ref"])
        and not (_step_retry(r["ref"], r["verdict"]) and r["ref"] in shown)])


def reading_line(conn: sqlite3.Connection, ref: str,
                 shown: list | tuple = ()) -> str | None:
    """The read-back line of `reading:<reply id>`, written from the columns,
    or None when the reply has no row.

    No model writes the line. A row on a `reading:` ref is never read back,
    so the chain ends at his approve (the seam design, 2.3). `shown` is the
    order of the page, as `read_back_rows` reads it."""
    reply = ref[len(READING_REF):]
    rows = read_back_rows(conn, reply, shown)
    if not rows:
        return None
    words = said(conn, reply).split()
    quote = " ".join(words[:READ_BACK_WORDS]) + (
        " ..." if len(words) > READ_BACK_WORDS else "")
    clauses: list[str] = []
    approves = 0
    for r in rows:
        # A ruling on a page with no line has one row on the page itself.
        # His word is read back, so he learns that it ruled nothing (review
        # p7 of frame 354, finding 5; ruled: Roman, 2026-10-26 22:5x).
        # The line rides a later page, and that page has lines. So the line
        # names the earlier page (review p8 of frame 354, finding 4).
        if r["ref"] == r["ask_id"]:
            clauses.append("the earlier page had no line, so your answer "
                           "landed on no line")
            continue
        step = f"step {r['verdict']}"
        verdict = (step if _step_key(r["ref"]) and step in _READ_BACK_VERDICT
                   else r["verdict"])
        if verdict == "approve" and not r["act"]:
            approves += 1
            continue
        where = f"line {r['line']}" if r["line"] else "a row"
        # The page of this line does not show the row, so the line number
        # of the earlier page names nothing here (review p7, finding 1). A
        # drop and an approve name the row by its words too (review p8,
        # finding 1).
        if r["ref"] not in shown:
            where = _row_name(conn, r["ref"]) or (
                f"line {r['line']} of the earlier page" if r["line"] else "a row")
        clause = f"{where} {_READ_BACK_VERDICT.get(verdict, verdict)}"
        if r["act"]:
            clause += f": {r['act']} {r['target'] or ''}".rstrip()
        clauses.append(clause)
    if approves:
        clauses.append(f"{approves} line{'s' if approves != 1 else ''} approved")
    return (f'Your answer "{quote}", as the team read it: '
            f"{'; '.join(clauses)}.{READ_BACK_ASK}")


def ratified_request(conn: sqlite3.Connection, *,
                     before_seq: int | None = None) -> dict | None:
    """
    The current request with its ratified statements only, or None.

    `supersedes` names a statement the principal ratified. `current_request`
    also lists a proposed statement, so the wake offered one and the door
    refused it (frame 193, pass 2b: G1's s_99cb32 fell to 2 of 5). The wake
    and the door read this one function, so they name the same statement.
    """
    cur = current_request(conn, before_seq=before_seq, unread=False)
    if not cur or not cur["statements"]:
        return None
    marks = ",".join("?" * len(cur["statements"]))
    done = {r["id"] for r in conn.execute(
        f"SELECT id FROM statements WHERE id IN ({marks}) AND status = 'ratified'",
        tuple(cur["statements"]))}
    # law 9: a contested statement is revoked until its owner amends it
    # A statement the principal contested on its confirm page is not the
    # request before the new words. Night 138's wake offered s1 after m138's
    # contest, and s353 copied it into `supersedes` (frame 193's design,
    # 2.G.4).
    done = {sid for sid in done if not contested_statement(
        conn, sid, confirm_only=True, before_seq=before_seq)}
    keep = [k for k, sid in enumerate(cur["statements"]) if sid in done]
    if not keep:
        return None
    return {**cur, "statements": [cur["statements"][k] for k in keep],
            "texts": [cur["texts"][k] for k in keep]}


def _root_statement(conn: sqlite3.Connection, sid: str) -> str:
    """Follow `supersedes` to the statement a follow-up said again."""
    seen = {sid}
    while True:
        row = conn.execute("SELECT supersedes FROM statements WHERE id = ?",
                           (sid,)).fetchone()
        if row is None or not row["supersedes"] or row["supersedes"] in seen:
            return sid
        sid = row["supersedes"]
        seen.add(sid)


def uncovered_statements(conn: sqlite3.Connection) -> list[dict]:
    """
    The ratified statements that no item reflects, as id and text.

    A follow-up and the statement it says again are one request, so an item
    that cites either covers both. The sign-off listed s5 as uncovered while
    the version item cited s3 (the review of 61a0f41d, finding 3).
    """
    cited = {_root_statement(conn, r["target"]) for r in conn.execute(
        "SELECT DISTINCT target FROM refs WHERE src_table = 'items' "
        "AND kind = 'statement'")}
    return [{"id": r["id"], "text": r["text"]} for r in conn.execute(
        "SELECT id, text FROM statements WHERE status = 'ratified' ORDER BY id")
        if _root_statement(conn, r["id"]) not in cited]


def row_items(conn: sqlite3.Connection, ref: str | None) -> list[str] | None:
    """The items one row is about: an item, a criterion, a ticket, a batch,
    a test, a ledger row, a read-back line or a page ref. None when the row
    is an inherited test, which reaches no item and no writer's batch."""
    if not ref:
        return []
    # A read-back line is about the rows it reads back, so it rides the
    # page of their request. Night 172's m47 read back e_p1's answers on
    # e_p2's confirm page (P8; ruled: Roman, 2026-10-28 09:10, frame 344).
    if _is_reading(ref):
        out: list[str] = []
        for r in read_back_rows(conn, ref[len(READING_REF):]):
            out += [i for i in row_items(conn, r["ref"]) or [] if i not in out]
        return out
    # `_items_reached` has no `tests` lookup. Night 162's l_71e52c9d0a on
    # `tst_c2_version_on` reached no item (frame 316, pass 2).
    row = conn.execute("SELECT about_ref FROM ledger WHERE id = ?", (ref,)).fetchone()
    target = row["about_ref"] if row is not None and row["about_ref"] else ref
    test = conn.execute("SELECT criterion_id FROM tests WHERE id = ?",
                        (target,)).fetchone()
    if test is not None:
        # An inherited test has no criterion, so its row reaches no request
        # (frame 209; frame 316's review 2, finding 4).
        if not test["criterion_id"]:
            return None
        return _items_reached(conn, test["criterion_id"])
    return _items_reached(conn, ref)


def requests_of(conn: sqlite3.Connection, ref: str | None) -> set[str | None]:
    """The request of each item one row reaches. None in the set stands for
    an item of no request: the account, a description or an observed
    behaviour."""
    return {_item_request(conn, i) for i in row_items(conn, ref) or []}


def request_of(conn: sqlite3.Connection, ref: str | None) -> str | None:
    """The entry of the one request that owns a row, or None.

    This is the one reader of the fact (F15). An item of no request shares
    any row, so a row of one request and the account is that request's.
    Night 161's s1 reaches `echo_json` and `how_it_works` (F15 review 1,
    finding 2). A row of no request or of two requests has no owner."""
    owners = _owners(conn, ref)
    return next(iter(owners)) if len(owners) == 1 else None


def _owners(conn: sqlite3.Connection, ref: str | None) -> set[str]:
    """The requests that own a row. A row that reaches no item is owned
    through the statements it names, so a confirm page's statement has its
    request before any item cites it."""
    items = row_items(conn, ref)
    if items:
        return {_item_request(conn, i) for i in items} - {None}
    # Night 172's m17 confirmed e_p1 before any item cited s1, and it read
    # back the onboarding answer m14 (P8, the night 172 read, W8).
    if not ref or items is None:
        return set()
    names = ([r["ref"] for r in read_back_rows(conn, ref[len(READING_REF):])]
             if _is_reading(ref) else [ref])
    # A seat's note about a statement is the request's row, as the sign-off's
    # lineage rows are (P9).
    note = conn.execute("SELECT about_ref FROM ledger WHERE id = ?",
                        (ref,)).fetchone()
    if note is not None and note["about_ref"]:
        names.append(note["about_ref"])
    out: set[str] = set()
    for sid in names:
        row = _statement_request(conn, sid) if isinstance(sid, str) else None
        if row is not None:
            out.add(row[0])
    return out


def page_owner(conn: sqlite3.Connection, refs: list) -> str | None:
    """The request a page is about, or None for a page of no request.

    The newest request its rows reach, as `page_request` reads it. A page
    whose rows reach no item takes the request of the statement it names,
    so a confirm page of a new request is that request's page."""
    req = page_request(conn, refs)
    if req is not None:
        return req
    best = None
    for ref in refs or []:
        if not isinstance(ref, str) or _is_reading(ref) or row_items(conn, ref):
            continue
        for entry in _owners(conn, ref):
            order = _entry_order(conn, entry)
            if best is None or order > best[1]:
                best = (entry, order)
    return best[0] if best else None


def _item_request(conn: sqlite3.Connection, item: str) -> str | None:
    """The entry of the request an item belongs to, or None when the item
    cites no statement or is a description."""
    from ..core.runner import _is_description

    # The account belongs to no request, whatever statement it cites. Night
    # 133's m283 dropped `defines_commands_and_options` off later pages, and
    # each sign-off submitted it again (the review of 61a0f41d, finding 2).
    # A description that cites a new statement ended the park before the
    # work existed (the review of a1bd448f, finding 1).
    if _is_description(conn, item):
        return None
    best = None
    for r in conn.execute(
            "SELECT r.target FROM refs r WHERE r.src_table = 'items' "
            "AND r.src_id = ? AND r.kind = 'statement'", (item,)):
        row = _statement_request(conn, r["target"])
        if row is not None and (best is None or row[1] < best[1]):
            best = row
    return best[0] if best else None


def _statement_request(conn: sqlite3.Connection,
                       sid: str) -> tuple[str, int] | None:
    """The entry of a statement's request and its order, or None. The one
    walk from a statement to its request: a follow-up is the request of
    the statement it says again (F15)."""
    row = conn.execute(
        "SELECT e.id, e.ts_order FROM statements s JOIN entries e "
        "ON e.id = s.span_entry WHERE s.id = ?",
        (_root_statement(conn, sid),)).fetchone()
    return (row["id"], row["ts_order"]) if row is not None else None


def _entry_order(conn: sqlite3.Connection, entry: str) -> int:
    row = conn.execute("SELECT ts_order FROM entries WHERE id = ?", (entry,)).fetchone()
    return int(row["ts_order"]) if row else 0


def _delivered(conn: sqlite3.Connection, item: str) -> bool:
    row = conn.execute(
        "SELECT i.version, (SELECT CAST(value AS INTEGER) FROM config "
        "WHERE key = 'delivered:' || i.id) AS d FROM items i WHERE i.id = ?",
        (item,)).fetchone()
    return bool(row and row["d"] is not None and row["version"] <= row["d"])


def shift_ask_id(item: str, request_id: str) -> str:
    """The id of the one shift question for an earlier item and a request."""
    return f"{SHIFT_ASK}{item}_{request_id}"


def open_earlier_items(conn: sqlite3.Connection, cur: dict | None = None,
                       *, asked: bool = True) -> list[str]:
    """
    The items of an earlier request that the shift question is about: not
    delivered, `approved`, `contested` or `draft`, not set aside, and not yet
    answered for the current request (2.F.1). The oldest request first.
    `asked` False also leaves out an item whose question is already sent.
    """
    from ..core.scheduler import aside_items

    cur = cur if cur is not None else current_request(conn)
    if not cur:
        return []
    here = set(cur["entries"])
    at = min(_entry_order(conn, e) for e in cur["entries"])
    aside = aside_items(conn)
    out: list[tuple[int, str]] = []
    # `request_of` gives a description no request, so no description is
    # an earlier request's item (F15).
    for r in conn.execute(
            "SELECT i.id FROM items i WHERE i.kind = 'in_scope' "
            "AND i.approval IN ('approved', 'contested', 'draft') ORDER BY i.id"):
        item = r["id"]
        if item in aside or _delivered(conn, item):
            continue
        entry = request_of(conn, item)
        if entry is None or entry in here or _entry_order(conn, entry) >= at:
            continue
        sent = conn.execute("SELECT status FROM messages WHERE id = ?",
                            (shift_ask_id(item, cur["id"]),)).fetchone()
        if sent is not None and (sent["status"] != "open" or not asked):
            continue
        out.append((_entry_order(conn, entry), item))
    return [i for _, i in sorted(out)]


def held_items(conn: sqlite3.Connection) -> set[str]:
    """The items whose pages the principal does not see now: set aside, or
    an earlier request's item while its shift question is unanswered."""
    from ..core.scheduler import aside_items

    return aside_items(conn) | set(open_earlier_items(conn))


def _reached(conn: sqlite3.Connection, refs: list) -> set[str]:
    items: set[str] = set()
    for ref in refs or []:
        if isinstance(ref, str):
            items.update(_items_reached(conn, ref))
    return items


def held_asks(conn: sqlite3.Connection) -> set[str]:
    """The open asks to the principal that wait behind the shift question:
    every ref that reaches an item reaches a held item (2.F.1, 2.F.4)."""
    held = held_items(conn)
    if not held:
        return set()
    out: set[str] = set()
    for r in conn.execute(
            "SELECT id, body_refs FROM messages WHERE status = 'open' "
            "AND to_role = 'principal' AND verb != 'converse'"):
        if r["id"].startswith(SHIFT_ASK):
            continue
        reached = _reached(conn, json.loads(r["body_refs"] or "[]"))
        if reached and reached <= held:
            out.add(r["id"])
    return out


def page_request(conn: sqlite3.Connection, refs: list) -> str | None:
    """The newest request that a page's refs reach, set-aside items and
    descriptions apart."""
    from ..core.scheduler import aside_items

    aside = aside_items(conn)
    best = None
    # The page reads the row walk of `request_of`, so a test reaches its
    # criterion's item here as in `land` (F15 review 1, finding 1).
    # A read-back line rides the page of its request and never decides it
    # (P8).
    reached = {i for ref in refs or [] if isinstance(ref, str)
               and not _is_reading(ref) for i in row_items(conn, ref) or []}
    for item in reached:
        # `request_of` gives a description no request. A description citing
        # s3 put the confirm item off its own page (the review of e406e976,
        # finding 1).
        if item in aside:
            continue
        entry = request_of(conn, item)
        if entry is None:
            continue
        order = _entry_order(conn, entry)
        if best is None or order > best[1]:
            best = (entry, order)
    return best[0] if best else None


def _statement_status(conn: sqlite3.Connection, sid: str) -> str | None:
    """The status of statement `sid`, or None when no statement has the id."""
    row = conn.execute("SELECT status FROM statements WHERE id = ?",
                       (sid,)).fetchone()
    return row["status"] if row is not None else None


def off_page(conn: sqlite3.Connection, refs: list, *,
             confirm: bool = False) -> set[str]:
    """
    The refs that a page of one request does not number (2.F.7). A row
    whose items are all set aside, or all of another request than the page's,
    leaves the page. A note about a delivered item of an earlier request
    stays, so a ruling closes it. A row of no item, a glossary term, a
    constraint or a claim about one, leaves a request's page and rides the
    account's page. A read-back line leaves a page that `page_readings`
    does not give it. The send door drops the same rows, so a page's refs
    and its numbered rows are one set. `confirm` keeps every statement,
    because a confirm page can take his words as separate requests.
    """
    from ..core.scheduler import aside_items, rowless_key

    # A dropped item and its rows are no line, as an item set aside (frame
    # 357, pass 2: dry1's m122 put both dropped items on a page again).
    aside = aside_items(conn) | dropped_items(conn)
    # Requests are told apart by their boundaries. A run with no request
    # message has one request, and every open item keeps its line (frame
    # 190's design, 2.F, amendment 2).
    req = page_owner(conn, refs) if current_request(conn, unread=False) else None
    out: set[str] = set()
    for ref in refs or []:
        if not isinstance(ref, str):
            continue
        # The rulings door reads this set, so a read-back line is off where
        # the page leaves it out (P8).
        if _is_reading(ref):
            if ref not in page_readings(conn, refs, [ref]):
                out.add(ref)
            continue
        # A quarantined key with no row is a numbered line of the page, so
        # it stays (frame 354).
        if rowless_key(conn, ref):
            continue
        # One scoped read finds a statement (F22).
        is_statement = bool(tables_of(conn, ref, among=["statements"]))
        # A dropped statement is no line on any page, so no "ok" approves
        # it again (frame 357, dry1's m77).
        if is_statement and _statement_status(conn, ref) == "dropped":
            out.add(ref)
            continue
        # The intake door refuses a statement of another entry, so the
        # Liaison learns to say it again (frame 193, pass 3, finding 4).
        if confirm and is_statement:
            continue
        # One row walk with `land`: a note about a test of another
        # request's item leaves the page, and his answer on it contests
        # nothing (F15 review 1, finding 1).
        items = row_items(conn, ref)
        # An inherited test reaches no item and keeps its row (frame 209).
        if items is None:
            continue
        # A page is about one request. The account's own rows go on their
        # own page and never on a request's page. Night 172's m71 carried
        # 19 glossary and constraint rows (P9; frame 241; ruled: Roman,
        # 2026-10-28 09:10, frame 344). A statement of the page's request
        # stays before any item cites it.
        if not items:
            if req is not None and req not in _owners(conn, ref):
                out.add(ref)
            continue
        if all(i in aside for i in items):
            out.add(ref)
            continue
        if req is None:
            continue
        # A row whose every item has no request is the account's row, so it
        # leaves a request's page too: the account, a description or an
        # observed behaviour (F15). The review of P9: a claim about
        # how_it_works, then one about parses_and_executes_inputs, was
        # line 4 of e_p3's page.
        others = requests_of(conn, ref)
        if others <= {None}:
            out.add(ref)
            continue
        # A row that reaches the page's request and an item of no request
        # stays (F15 review 1, finding 2).
        if not all(e is not None and e != req for e in others):
            continue
        is_note = tables_of(conn, ref, among=["ledger"])
        if is_note and all(_delivered(conn, i) for i in items):
            continue
        out.add(ref)
    return out


def _approved_now(conn: sqlite3.Connection, ref: str) -> bool:
    """Whether the principal approved the item `ref` at its current version."""
    # His approve at this version is the page's answer, so the row is not
    # owed again. Dry1's m17 re-sent how_it_works after r_m10 (frame 355).
    return conn.execute(
        "SELECT 1 FROM items WHERE id = ? AND approval = 'approved' "
        "AND approval_ver = version", (ref,)).fetchone() is not None


def account_rows(conn: sqlite3.Connection, refs: list) -> list[str]:
    """The refs that are the account's own rows: a row that no request
    owns, a read-back line, an inherited test and an approved row apart."""
    return [r for r in refs or [] if isinstance(r, str) and not _is_reading(r)
            and row_items(conn, r) is not None and not _owners(conn, r)
            and not _approved_now(conn, r)]


def account_page_refs(conn: sqlite3.Connection, rows: list[str]) -> list[str]:
    """The refs of the account's page for `rows`, how_it_works first when
    the row exists and is not approved at its version, or [] when an open
    page to him shows every row or he approved it."""
    shown = {r for m in conn.execute(
        "SELECT body_refs FROM messages WHERE to_role = 'principal' "
        "AND status = 'open'") for r in json.loads(m["body_refs"] or "[]")}
    # A row that holds his drop has his answer, so no page owes it again
    # (ruled: Roman, 2026-11-02 11:43, frame 357, shape B).
    owed = [r for r in rows if r not in shown and not _approved_now(conn, r)
            and not principal_objects(conn, r)]
    if not owed:
        return []
    account = conn.execute(
        "SELECT 1 FROM items WHERE id = 'how_it_works'").fetchone()
    head = (["how_it_works"] if account and "how_it_works" not in owed
            and not _approved_now(conn, "how_it_works")
            and not principal_objects(conn, "how_it_works") else [])
    return head + sorted(owed, key=lambda r: r != "how_it_works")


def request_rows(conn: sqlite3.Connection, refs: list[str]) -> list[str]:
    """
    The request's own rows for a page: each item, then its criteria by id.

    The items are the ones the refs reach. When the refs name a request and
    reach none of its items, they are every open request. When the refs
    name no request, or no request is open, the row is the account, which
    renders under its own heading.
    """
    # Night 136's 49 agenda pages carried no line of the request, so the
    # principal's words had no row to land on (frame 190's design, 2.1).
    # Every open request has its own line. One line for the first request
    # sent a revise about another request to the wrong item (frame 190's
    # design, 2.F, amendment 2).
    # One request per page: the items of the page's request, never an item
    # set aside or held behind the shift question (frame 193's design, 2.F.7).
    from ..core.scheduler import aside_items

    off = off_page(conn, refs or [])
    held = held_items(conn)
    items: list[str] = []
    for ref in refs or []:
        if not isinstance(ref, str) or ref in off or _is_reading(ref):
            continue
        for item in row_items(conn, ref) or []:
            if item not in items and item not in held and _is_request_item(conn, item):
                items.append(item)
    # Rows of no request make the account's page, and the account row is
    # the row his words land on, so law 8 holds. The open request on that
    # page put night 172's m71 under clear() (P9; frame 241; ruled: Roman,
    # 2026-10-28 09:10, frame 344). With no account row, the page is still
    # the account's: its rows are numbered, so his words land on them, and
    # the door sends them. The open request there dropped s179's 19 rows
    # (the review of P9, finding 2).
    account = conn.execute(
        "SELECT 1 FROM items WHERE id = 'how_it_works'").fetchone()
    if not items and any(_owners(conn, r) for r in refs or []
                         if isinstance(r, str) and not _is_reading(r)):
        aside = aside_items(conn) | held
        items = [i for i in open_requests(conn) if i not in aside]
        cur = current_request(conn, unread=False)
        mine = [i for i in items if cur and request_of(conn, i) in cur["entries"]]
        items = mine or items
    if not items:
        return ["how_it_works"] if account else []
    # A retired ticket's criteria are no line. After a slice again, the page
    # listed the old criteria above the new one, and a contest went to
    # `criterion_repair` on a row nobody builds (the diff review of
    # 2dace61b, finding 1).
    # A retired criterion is no line either (frame 306, pass 1b).
    from ..core.scheduler import live_criteria, not_retired

    out: list[str] = []
    for item in items:
        out.append(item)
        out += [r["id"] for r in conn.execute(
            "SELECT c.id FROM criteria c JOIN tickets t ON t.id = c.ticket_id "
            "WHERE t.item_id = ?" + not_retired(conn, "c.ticket_id")
            + live_criteria(conn, "c.retired_by")
            + " ORDER BY c.id", (item,))]
    return out


def _gave_up_tries(conn: sqlite3.Connection, criterion: str,
                   batch: str | None, keys: list[str],
                   sent: dict[str, int] | None = None) -> int | None:
    """The attempts of a `tests_missing` key of the page's `stalled` row,
    for a batch that holds the criterion, or None when no such key exists."""
    # The page's own keys, never the live quarantine. A live read put "gave
    # up" under each criterion of night 136's open touch note m84 after a
    # later quarantine (the delta review of 2c602d1b, finding 3).
    # The page's batch counts only for a criterion of its own tickets. With
    # the batch given, every criterion on the page read as given up, another
    # item's included (the diff review of 2dace61b, finding 5).
    if batch:
        batches = [batch] if conn.execute(
            "SELECT 1 FROM batch_tickets bt JOIN criteria c ON c.ticket_id = bt.ticket_id "
            "WHERE c.id = ? AND bt.batch_id = ?", (criterion, batch)).fetchone() else []
    else:
        batches = [r["batch_id"] for r in conn.execute(
            "SELECT bt.batch_id FROM batch_tickets bt "
            "JOIN criteria c ON c.ticket_id = bt.ticket_id "
            "JOIN batches b ON b.id = bt.batch_id "
            "WHERE c.id = ? AND b.status NOT IN ('merged', 'abandoned')", (criterion,))]
    from ..core.scheduler import key_parts

    for key in sorted(keys or []):
        _, kind, keyed = key_parts(key)
        if kind == "tick:tests_missing" and set(keyed) & set(batches):
            return key_attempts(conn, key, sent)
    return None


LIVE_BATCH = ("pending", "deferred", "running")


def code_target(conn: sqlite3.Connection, item: str) -> dict | None:
    """What a request's code line shows at a send: the live batch with a
    plan, else the current guess set, else None (frame 298's design, 2.1)."""
    # A live batch's plan replaces the guess, so the principal sees one list
    # per item (frame 298's design, 2.1, point 6).
    row = conn.execute(
        "SELECT b.id FROM batches b WHERE b.item_id = ? AND b.status IN "
        f"({','.join('?' * len(LIVE_BATCH))}) AND EXISTS (SELECT 1 FROM batch_touch t "
        "WHERE t.batch_id = b.id) ORDER BY b.rowid DESC LIMIT 1",
        (item, *LIVE_BATCH)).fetchone()
    if row is not None:
        return {"batch": row["id"]}
    last = conn.execute("SELECT item_ver, ruling_id FROM touch_guesses WHERE item_id = ? "
                        "ORDER BY rowid DESC LIMIT 1", (item,)).fetchone()
    return {"guess": [last["item_ver"], last["ruling_id"]]} if last else None


def code_targets(conn: sqlite3.Connection, refs: list[str]) -> dict[str, dict]:
    """The send door's stamp: `guess:<item>` to its target, for each request
    item of the refs. A page that holds a batch of the item is a touch or a
    stopped page, and its batch line already shows the plan."""
    out: dict[str, dict] = {}
    for ref in refs or []:
        if not isinstance(ref, str) or not _is_request_item(conn, ref):
            continue
        if any(conn.execute("SELECT 1 FROM batches WHERE id = ? AND item_id = ?",
                            (r, ref)).fetchone() for r in refs if isinstance(r, str)):
            continue
        target = code_target(conn, ref)
        if target:
            out[f"guess:{ref}"] = target
    return out


def code_line(conn: sqlite3.Connection, item: str, target: dict | None) -> str:
    """The words of a code line, or '' when the target names nothing."""
    if not isinstance(target, dict):
        return ""
    batch = target.get("batch")
    if batch:
        # A batch target renders live, as a batch line does. The line keeps
        # its number when the change closes (frame 298's design, 2.1, point 2).
        row = conn.execute("SELECT status FROM batches WHERE id = ?", (batch,)).fetchone()
        if row is None or row["status"] in ("merged", "abandoned"):
            return "The team's plan for this change is closed."
        from ..core.lifecycle import touch_set

        t = touch_set(conn, batch) or {}
        parts = ["expected to touch " + (", ".join(t.get("expected") or [])
                                         or "nothing named")]
        if t.get("possible"):
            parts.append("might touch " + ", ".join(t["possible"]))
        return "The team's plan of the code this touches: " + "; ".join(parts)
    shown = target.get("guess")
    if not (isinstance(shown, list) and len(shown) == 2):
        return ""
    # A guess target renders the set the send stamped, frozen. A later set
    # is the next page's.
    rows = conn.execute(
        "SELECT grain, grain_kind FROM touch_guesses WHERE item_id = ? AND item_ver = ? "
        "AND ruling_id = ? ORDER BY rowid", (item, shown[0], shown[1])).fetchall()
    paths = [r["grain"] for r in rows if r["grain_kind"] == "path"]
    symbols = [r["grain"] for r in rows if r["grain_kind"] == "symbol"]
    if not paths:
        return ""
    words = "The team's guess at the code this touches: " + ", ".join(paths) + "."
    if symbols:
        words += " It might touch " + ", ".join(symbols) + "."
    return words


def _test_retired(conn: sqlite3.Connection, test_id: str) -> bool:
    """True when his ruling retired the test `test_id` (frame 306, W-A)."""
    from ..core.db import _has_column

    return _has_column(conn, "tests", "retired_by") and conn.execute(
        "SELECT 1 FROM tests WHERE id = ? AND retired_by IS NOT NULL",
        (test_id,)).fetchone() is not None


def is_test_row(conn: sqlite3.Connection, ref: str) -> bool:
    """True when the page row `ref` is a check line, a row of `tests`."""
    return isinstance(ref, str) and conn.execute(
        "SELECT 1 FROM tests WHERE id = ?", (ref,)).fetchone() is not None


def request_block(conn: sqlite3.Connection, refs: list[str], order: list[str],
                  out: list[str], *, said: list[tuple[str, str]] | None = None,
                  batch: str | None = None, code: dict | None = None,
                  park: bool = False, stalled: list[str] | None = None,
                  sent: dict[str, int] | None = None) -> list[int]:
    """
    Render the request's rows of a page first: the principal's words, each
    item, its code line, and its criteria with their `check:` lines. Append
    to `out` and `order`, and return the line numbers of the items.
    `sent` holds the counts of `stalled` that the send door recorded.

    `code` is the send door's stamp `code:<message id>`. A code line renders
    from it only, numbered under the item. An item with no stamp gets one
    unnumbered line that says the team has not guessed yet. A touch, stopped
    or park page has a batch line, and no code line.

    The park page renders through this block too, so its words stay as
    frame 142 landed them. `park` keeps its one difference: every item
    first, then every criterion, and no line about a test given up.
    """
    marks = ",".join("?" * len(refs))
    items = {r["id"]: r["text"] for r in conn.execute(
        f"SELECT id, text FROM items WHERE id IN ({marks})", tuple(refs))} if refs else {}
    crit = {r["id"]: (r["text"], r["item_id"]) for r in conn.execute(
        "SELECT c.id, c.text, t.item_id FROM criteria c "
        "LEFT JOIN tickets t ON t.id = c.ticket_id "
        f"WHERE c.id IN ({marks})", tuple(refs))} if refs else {}
    asked = [r for r in refs if r in items and (park or _is_request_item(conn, r))]
    must = [r for r in refs if r in crit]
    if park:
        groups = [(asked, must)]
    else:
        groups = [([i], [c for c in must if crit[c][1] == i]) for i in asked]
        loose = [c for c in must if crit[c][1] not in asked]
        if loose:
            groups.append(([], loose))
    lines: list[int] = []
    headed = False
    if said:
        out.append("You asked:")
        headed = True
        for ref, text in said:
            order.append(ref)
            out.append(f'  {len(order)}. "{text}"')
    after_must = False
    for group_items, group_must in groups:
        if group_items:
            if not headed:
                out.append("You asked:")
                headed = True
            elif after_must:
                out.append("You also asked:")
            for r in group_items:
                order.append(r)
                lines.append(len(order))
                out.append(f"  {len(order)}. {items[r]}")
                if park or batch:
                    continue
                key = f"guess:{r}"
                target = (code or {}).get(key)
                words = code_line(conn, r, target) if key in refs else ""
                if words:
                    order.append(key)
                    out.append(f"  {len(order)}. {words}")
                elif not target:
                    # The present can go out before the guess exists. No
                    # ruling is owed on this line (frame 298's design, 2.3).
                    out.append("     The team has not guessed the code this touches yet.")
        if group_must:
            out.append("It must:")
        for r in group_must:
            order.append(r)
            out.append(f"  {len(order)}. {crit[r][0]}")
            # A test of an abandoned batch checks nothing that will ship, so
            # it is no check line, except on a page about that batch. Night
            # 142's pages m109 to m191 showed such a test as the check, and
            # no seat could change it (frame 213).
            mine = [t["id"] for t in conn.execute(
                "SELECT t.id FROM tests t LEFT JOIN batches b ON b.id = t.batch_id "
                "WHERE t.criterion_id = ? "
                + ("AND t.batch_id = ? " if batch else
                   "AND COALESCE(b.status, '') != 'abandoned' ") + "ORDER BY t.id",
                (r, batch) if batch else (r,))]
            # A check line has a number and a ref in the page's sequence, so
            # his words about a test land on the test. Night 164's m121 said
            # "remove the second check under line 2", and the words landed on
            # the criterion. A test he retired is no check line (frame 306,
            # W-A).
            mine = [t for t in mine if not _test_retired(conn, t)]
            for t in mine:
                order.append(t)
                out.append(f"     {len(order)}. check: {check_line(conn, t)}")
            if mine:
                continue
            # The Tester writes no test before the head commit, so a touch
            # note reads "none yet". A quarantined `tests_missing` key means
            # the team stopped trying. Night 136's m96 said nothing of cr_3
            # (frame 190's design, 2.5).
            tries = None if park else _gave_up_tries(conn, r, batch, stalled or [],
                                                     sent)
            # A park page's row with no test says so in its one line, in
            # place of the expectation and the red mark (ruled: Roman,
            # 2026-11-01, the amendment of the park ruling's point 3).
            if park:
                out.append("     check: no test yet.")
            elif tries is None:
                out.append("     check: none yet.")
            elif not tries:
                # No count was recorded, so the line says none (frame 360,
                # wall 14).
                out.append("     check: none. The team gave up writing it.")
            else:
                out.append("     check: none. The team gave up writing it after "
                           f"{tries} tries.")
        after_must = bool(group_must)
    return lines


def _name_request(lines: list[int]) -> str:
    """The closing sentence that names the request's lines, or ''."""
    if not lines:
        return ""
    if len(lines) == 1:
        return f" To change what you asked for, name line {lines[0]}."
    return (" To change what you asked for, name its line, "
            + ", ".join(str(n) for n in lines[:-1]) + f" or {lines[-1]}.")


def _name_guess(lines: list[int]) -> str:
    """The closing sentence that names the code lines, or ''."""
    # The numbers come from the order (frame 298's design, 2.4).
    if not lines:
        return ""
    if len(lines) == 1:
        return f" To correct the code it touches, name line {lines[0]}."
    return (" To correct the code they touch, name line "
            + ", ".join(str(n) for n in lines[:-1]) + f" or {lines[-1]}.")


def _stalled_keys(conn: sqlite3.Connection, batches: list[str]) -> list[str]:
    """The quarantined tick keys that name a batch of the page."""
    from ..core.scheduler import quarantined_keys

    return quarantined_keys(conn, batches, pairs=True, constraint_zero=False,
                            groups=False)


def _stalled_words(conn: sqlite3.Connection, keys: list[str]) -> str:
    """'the team could not write the tests after 3 attempts', one part per
    key, in the words of TICK_WORDS and never the tick's name."""
    return "; ".join(_stalled_parts(conn, keys))


def _stalled_parts(conn: sqlite3.Connection, keys: list[str],
                   sent: dict[str, int] | None = None) -> list[str]:
    """The parts of `_stalled_words`, one per key."""
    return [_key_words(conn, key, kind, n)
            for key, (kind, n) in zip(keys, _stuck_ticks(conn, "", keys, sent))]


def _retries_said(conn: sqlite3.Connection, key: str) -> str:
    """The words that say he asked to run the step `key` again before, or
    "" when his newest landed ruling on it is no retry."""
    # A lift deletes the quarantine row, so `ruled_refs` is the one record
    # of his earlier tries. Without it he can loop on 'try again' and the
    # page shows no earlier try (review p4 of frame 354, finding 5).
    rows = [r["verdict"] for r in conn.execute(
        "SELECT verdict FROM ruled_refs WHERE ref = ? AND source = 'landed' "
        "ORDER BY rowid", (key,))]
    if not rows or rows[-1] not in ("contest", "revise"):
        return ""
    n = sum(v in ("contest", "revise") for v in rows)
    return (". You asked me to try it again "
            + ("once" if n == 1 else f"{n} times") + " before")


def _gave_up_words(conn: sqlite3.Connection, keys: list[str],
                   sent: dict[str, int] | None = None) -> list[str]:
    """'the team could not write the tests after 3 attempts', one part per
    key, with what the key is about."""
    # The page printed the kind's name, "tests_missing for b_3", at the end
    # of night 170. The page contract shows his words, never rota's names
    # (fact F21, frame 312, review 1, finding 1).
    from ..core.db import tables_of
    from ..core.scheduler import key_parts

    out = []
    for key, (kind, n) in zip(keys, _stuck_ticks(conn, "", keys, sent)):
        what = _key_about(conn, key)
        refs = key_parts(key)[2]
        batch = bool(refs) and all(tables_of(conn, r, among=("batches",)) for r in refs)
        out.append((_key_words(conn, key, kind, n, what), batch))
    # A batch prints as no words, so two stuck batches gave one clause twice
    # (review of P12 pass 1, finding 3). A repeated clause prints once with
    # its count.
    seen: dict[str, list[bool]] = {}
    for words, batch in out:
        seen.setdefault(words, []).append(batch)
    return [words if len(b) == 1 else
            f"{words}, on {len(b)} changes" if all(b) else f"{words}, {len(b)} times"
            for words, b in seen.items()]


# The sentence about a red test stays under 25 words (P12 of the night 172
# read). The page puts "The team gave up:" before it, so the clause gets 20.
RED_CLAUSE_WORDS = 20
# A clause names this many test files at most, and counts the rest.
RED_FILES_SHOWN = 2


def _key_words(conn: sqlite3.Connection, key: str, kind: str, n: int,
               what: str = "") -> str:
    """
    One quarantined key in words with its attempts. A `tests_failing` key
    names each red test file and its error line.
    """
    # Night 172's m120 said "the tests still fail" while every check line
    # said "Passes". The red test had no criterion, so no line named it (wall
    # W12). The test goes in prose and never as a numbered line, because the
    # principal never rules on a test (ruled: Roman, 2026-10-08, cited in
    # `check_line`).
    from ..core.scheduler import key_parts, park_reds

    # A quarantined key has at least one attempt, so 0 is a count nobody
    # recorded. A page from before the record says no count, never "after 0
    # attempts" (frame 360, wall 14).
    tail = f" after {_tries(n)}" if n else ""
    if kind == "tests_failing":
        batch = next((r for r in key_parts(key)[2] if conn.execute(
            "SELECT 1 FROM batches WHERE id = ?", (r,)).fetchone()), None)
        own, project = park_reds(conn, batch) if batch else ([], [])
        errors: dict[str, str] = {}
        for r in own + project:
            errors.setdefault(r["path"] or r["test_id"], _failure_line(r["output"]))
        if errors:
            # Two files and one error line keep the clause short. Five files
            # with their errors made 77 words (review of P12 pass 1, finding 1).
            files = list(errors)
            shown = files[:RED_FILES_SHOWN]
            more = len(files) - len(shown)
            names = shown + ([f"{more} more test file{'' if more == 1 else 's'}"]
                             if more else [])
            subject = (names[0] if len(names) == 1
                       else ", ".join(names[:-1]) + " and " + names[-1])
            head = f"{subject} still fail{'s' if len(files) == 1 else ''}{tail}"
            error = next((errors[f] for f in shown if errors[f]), "")
            room = RED_CLAUSE_WORDS - len(head.split())
            return head + (f": {_cut_words(error, room)}" if error and room > 0 else "")
    return f"{_tick_words(kind)}{f' for {what}' if what else ''}{tail}"


def _cut_words(text: str, most: int) -> str:
    """The text cut to `most` words, with ' ...' as the last word when cut."""
    words = text.split()
    return text if len(words) <= most else " ".join(words[:most - 1]) + " ..."


# The bare refs a scheduler wake names, in words. A bare ref with no entry
# is rota's own name, so it shows nothing (review of F20 pass 1, finding 2).
BARE_REF_WORDS = {"@prose": "the README", "@program": "the whole program"}


def _ref_words(conn: sqlite3.Connection, ref: str) -> str:
    """A key's ref as a person knows it, or '' for a ref he has no name for."""
    # A ref is `@area:name` or `@claim:table:id`. The name is the part a
    # person knows, so the prefix goes. The bare `@prose` is the README
    # (scheduler `_reconcile_wakes`), and a page never shows an `@` (review 1
    # of frame 246, finding 1).
    if ref.startswith("@"):
        if ":" not in ref:
            return BARE_REF_WORDS.get(ref, "")
        return ref.rsplit(":", 1)[-1]
    # A ledger id is rota's key for a question. The words of the kind say
    # the question already (review of F20 pass 1, finding 3).
    # A batch id is rota's key for a change. The words of each kind say "the
    # change" or name the red test already. Night 172's state said "for bg_3"
    # (wall W12, section 4, item 3). The one reader of an id's table is
    # `tables_of` (fact F22).
    from ..core.db import tables_of

    if tables_of(conn, ref, among=("ledger", "batches")):
        return ""
    return ref


def _stuck_ticks(conn: sqlite3.Connection, batch: str,
                 keys: list[str] | None = None,
                 sent: dict[str, int] | None = None) -> list[tuple[str, int]]:
    """
    The batch's quarantined ticks as (kind, attempts), from `tick_attempts`.

    `keys` names the keys of a page's wake. None reads the live keys of the
    batch. The stopped page and the shift page both read this, so the two
    pages cannot disagree. Night 160's m45 said "stopped work" on a green
    change, and m53 then said "nothing from you" (frame 312's provenance).
    `sent` holds the counts the send door recorded for the page, from
    `door_attempts`. A recorded count comes before the live row.
    """
    from ..core.scheduler import key_parts

    out = []
    for key in (_stalled_keys(conn, [batch]) if keys is None else keys):
        kind = key_parts(key)[1].replace("tick:", "")
        out.append((kind, key_attempts(conn, key, sent)))
    return out


def key_attempts(conn: sqlite3.Connection, key: str,
                 sent: dict[str, int] | None = None) -> int:
    """The attempts of one quarantined key: the count the send door recorded,
    else the live `tick_attempts` row, else 0 for a count nobody knows."""
    # Dry4's m63 said "after 0 attempts". A later commit moved the head of
    # bg_1, and the move lifted the key of s213's quarantine. So its row was
    # gone at the read. The page shows the count at its send, as it shows the keys at
    # its send (frame 360, wall 14). Law 1: the send door is the one writer.
    if sent and key in sent:
        return sent[key]
    row = conn.execute("SELECT attempts FROM tick_attempts WHERE tick_key = ?",
                       (key,)).fetchone()
    return int(row["attempts"]) if row else 0


def sent_attempts(conn: sqlite3.Connection, keys: list[str]) -> dict[str, int]:
    """The live count of each key that has a row, for the send door to record
    beside the keys of `stalled`."""
    return {k: n for k in keys if (n := key_attempts(conn, k))}


# A tick's kind as the principal reads it. The page contract shows his
# words, never rota's names (frame 312, review 1, finding 1).
TICK_WORDS = {
    "review": "the review gave no verdict",
    "tests_failing": "the tests still fail",
    "tests_missing": "the team could not write the tests",
    "verdict_failed": "the review failed the change",
    "do:preempt": "the change was set aside",
    "do:park": "the change was stopped",
    # The Critic's `tick:challenge` checks a claim. `code_gaps` kept these
    # words in a second table before (fact F21).
    "challenge": "the team could not check a claim",
    "boundary": "the team could not settle a boundary",
    "reconcile": "the team could not compare the account with the code",
    "survey": "the team could not read a part of the code",
    "grouping": "the team could not group the work into changes",
    "contested": "a contested line got no answer",
    "quarantined": "the team could not report a stopped step",
    "agenda": "a question to you got no answer",
    "constraint_zero": "the team could not read the code first",
    "batch_start": "the change could not start",
    "touch_strayed": "the change went outside the files it expected",
    # Night 172's m127 showed the fallback for this kind (wall W12). The
    # Developer puts back code that the Architect judged a mistake.
    "touch_mistaken": "the team could not put back code it was not asked to change",
}


def _tick_words(kind: str) -> str:
    # A kind with no entry still says what failed, with a verb (review of
    # F20 pass 1, finding 2).
    return TICK_WORDS.get(kind, "the team could not finish a step")


def _capital(text: str) -> str:
    """The text with its first letter in capitals, for a sentence start."""
    # A path is copied exactly. A stopped sentence can open with a red
    # test's path (wall W12). A test file at the root has no "/" (review of
    # P12 pass 1, finding 2).
    first = text.split(" ", 1)[0]
    if "/" in first or re.fullmatch(r"[\w.-]+\.\w+", first):
        return text
    return text[:1].upper() + text[1:]


def _tries(n: int) -> str:
    return f"{n} attempt{'' if n == 1 else 's'}"


def _review_only(ticks: list[tuple[str, int]]) -> bool:
    """True when every stuck tick is a review. The review fires only on a
    green harness at the head, so its tests passed at its last attempt."""
    return bool(ticks) and all(kind == "review" for kind, _ in ticks)


TEAM_NOTES =("The team's notes. A seat wrote each of these where your words "
              "were silent. They are not your request.")
# The heading of an account read from the code (ruled: Roman, 2026-10-17
# 04:33, frame 264: the summary stays, presented as the project today).
ACCOUNT_TODAY = "What the project does today. This is not your request:"


def _looped_words(row: dict) -> str:
    """The park sentence for one row of `challenged_reds`."""
    from ..core.scheduler import versions_words

    return (f"The team challenged the check {row['path'] or row['test_id']} "
            f"{row['challenges']} times, and wrote "
            f"{versions_words(row['versions'])} of it.")


def _park_page(conn: sqlite3.Connection, batch: str,
               refs: list[str]) -> tuple[str, list[str]]:
    """The park message as the principal reads it: a page with the item and
    its criteria, or a note when the batch is its one ref."""
    from ..core.scheduler import (TESTER_MISSING, challenged_reds,
                                  failing_attempt, given_up, key_parts,
                                  park_reds, park_untested)

    from ..core.scheduler import owed, owed_park

    held = owed_park(conn, batch)
    if held:
        return _owed_park_page(conn, batch, held, owed(conn, batch))
    own, project = park_reds(conn, batch)
    if refs == [batch]:
        files = sorted({r["path"] or r["test_id"] for r in project})
        return (chr(10).join([
            "This change stops here. It breaks checks the project had before: "
            + ", ".join(files) + ".",
            "Nothing waits on you. A new commit on the change starts it again."]), [])
    out: list[str] = []
    order: list[str] = []
    checks = conn.execute(
        "SELECT id FROM tests WHERE batch_id = ? "
        "AND (criterion_id IS NOT NULL OR commitment_id IS NOT NULL)",
        (batch,)).fetchall()
    tries = failing_attempt(conn, batch)
    if not own and park_untested(conn, batch):
        # No check exists to count, so the sentence names the Tester's
        # give-up (ruled: Roman, 2026-11-01, the amendment of point 3).
        keys = [k for k in given_up(conn, batch) if key_parts(k)[:2] == TESTER_MISSING]
        out.append("This change stopped before it had any checks, because "
                   + " and ".join(_gave_up_words(conn, keys)) + ".")
    else:
        out.append(f"This change stopped. The team tried {tries} "
                   f"time{'' if tries == 1 else 's'}, and {len(own)} of its "
                   f"{len(checks)} checks still fail.")
    # The page names the check that looped between the Developer and the
    # Tester. Dry1 turn 12 showed the seat nothing (frame 278, pass 2).
    out.extend(_looped_words(r) for r in challenged_reds(conn, batch))
    request_block(conn, refs, order, out, batch=batch, park=True)
    head = conn.execute("SELECT head_commit FROM batches WHERE id = ?",
                        (batch,)).fetchone()
    at_head = [r for r in own if head is None or head["head_commit"] is None
               or r.get("commit_sha") in (None, head["head_commit"])] or own
    # A guard test shows its commitment id beside the test (pass 3c).
    last = [f"{r['path'] or r['test_id']}"
            + (f", which guards commitment {r['commitment_id']}," if r.get("commitment_id") else "")
            + f" failed: {_failure_line(r['output']) or 'no reason shown'}."
            for r in at_head[:2]]
    if last:
        out.append("The last attempt: " + " ".join(last))
    out.append("Reply 'ok' if every line says what you want. The team then "
               "stops here and tells you.")
    out.append("Name a line to correct only that line. Ask, if something here "
               "is unclear.")
    return chr(10).join(out), order


def _owed_park_page(conn: sqlite3.Connection, batch: str, key: str,
                    found: dict) -> tuple[str, list[str]]:
    """The park page of an item whose owed write never came: what he said,
    the line he contested, and the way out (frame 87, ruled: Roman,
    2026-09-27). The other requests go on, as R7 and R10 ask (frame 362)."""
    from ..core.scheduler import key_parts, owed_tries

    # Each session that woke on the ruling is a try, the relay included.
    tries = owed_tries(conn, found["verdict"])
    text = conn.execute("SELECT text FROM items WHERE id = ?",
                        (found["item"],)).fetchone()
    guess = key_parts(key)[1] == "tick:guess"
    what, short = (("guess at the code", "guess") if guess
                   else ("plan of the code", "plan"))
    # The page shows no contested set and asks for no files he named
    # already. It says what the team did not do (the review of 36a2edd2,
    # finding 5).
    # A database with no session rows gives no count, and the page then
    # names no number.
    times = f" {tries} time{'' if tries == 1 else 's'}" if tries else ""
    out = ["This change waits before it starts.",
           f"You corrected the team's {what} this request touches. The team "
           f"tried{times}, and it did not rewrite the {short}."]
    if found["words"]:
        out.append(f'You said: "{found["words"]}"')
    out.append("You asked:")
    out.append(f"  1. {text['text'] if text else found['item']}")
    out.append("  2. The code this request touches. It waits for the team's rewrite.")
    out.append("Reply to line 2 to say again what to change, and the team tries "
               "again. Or say that you give the request up.")
    out.append("Nothing else waits on you. The other requests go on.")
    return chr(10).join(out), [found["item"], found["ref"]]


def _shift_where(conn: sqlite3.Connection, item: str) -> str:
    """'Where it stands' on the shift page: the approval, the live change,
    its head commit and its newest test runs."""
    row = conn.execute("SELECT approval FROM items WHERE id = ?", (item,)).fetchone()
    said = f"{row['approval'] if row else 'unknown'}."
    batch = _live_batch(conn, item)
    if batch is None:
        return said + " No change is built for it yet."
    return said + _built_words(conn, batch) + "".join(
        f" Its review stopped after {_tries(n)} with no verdict." if kind == "review"
        else f" The team stopped after {_tries(n)}, because {_tick_words(kind)}."
        for kind, n in _stuck_ticks(conn, batch["id"]))


def _live_batch(conn: sqlite3.Connection, item: str) -> sqlite3.Row | None:
    """The item's change that is not closed, or None."""
    return conn.execute(
        "SELECT id, head_commit FROM batches WHERE item_id = ? "
        "AND status IN ('pending', 'running', 'deferred') ORDER BY id",
        (item,)).fetchone()


def _built_words(conn: sqlite3.Connection, batch: sqlite3.Row) -> str:
    """The live change's build and its newest test runs."""
    if not batch["head_commit"]:
        return f" The change {batch['id']} is not built yet."
    runs = conn.execute(
        "SELECT result FROM latest_runs WHERE batch_id = ?",
        (batch["id"],)).fetchall()
    # A claimed batch is not built: the team claims that the code already
    # does this (frame 360, review p1, F1).
    from ..core.db import _has_column

    if _has_column(conn, "batches", "claimed_head") and conn.execute(
            "SELECT 1 FROM batches WHERE id = ? AND claimed_head = head_commit",
            (batch["id"],)).fetchone():
        failing = sum(1 for r in runs if r["result"] in ("fail", "error"))
        said = (f" The change {batch['id']} changes no code. The team claims "
                f"that the code already does this, and the tests check the "
                f"claim.")
        if not runs:
            return said + " No test has run yet."
        if not failing:
            return said + f" All {len(runs)} of its tests pass."
        return said + f" {failing} of its {len(runs)} tests fail."
    if not runs:
        return f" The change {batch['id']} is built, and no test has run yet."
    failing = sum(1 for r in runs if r["result"] in ("fail", "error"))
    if not failing:
        return (f" The change {batch['id']} is built, and all {len(runs)} "
                       f"of its tests pass.")
    return (f" The change {batch['id']} is built, and {failing} of its "
                   f"{len(runs)} tests fail.")


def _shift_waits(conn: sqlite3.Connection, item: str) -> str:
    """'What it waits on': the item's open pages, read with the hold, and its
    open notes."""
    pages = []
    for r in conn.execute(
            "SELECT id, verb, body_refs, body_text FROM messages WHERE status = "
            "'open' AND to_role = 'principal' AND verb != 'converse' ORDER BY seq"):
        if r["id"].startswith(SHIFT_ASK):
            continue
        refs = json.loads(r["body_refs"] or "[]")
        reached = _reached(conn, refs)
        if reached and reached <= {item}:
            pages.append(len(render_page(conn, r["verb"], refs, r["body_text"],
                                         ask_id=r["id"])[1]))
    notes = sum(1 for r in conn.execute(
        "SELECT id FROM ledger WHERE status = 'open'")
        if item in _items_reached(conn, r["id"]))
    parts = []
    if len(pages) == 1:
        parts.append(f"one page to you with {pages[0]} lines")
    elif pages:
        parts.append(f"{len(pages)} pages to you with "
                     + ", ".join(str(n) for n in pages[:-1])
                     + f" and {pages[-1]} lines")
    if notes:
        parts.append(f"{notes} note{'' if notes == 1 else 's'}")
    # A quarantined tick holds the change until a move revives it (law 6).
    # Night 160's m53 read "nothing from you" on a stuck review, and he
    # parked the change (frame 312's provenance, section 4).
    batch = _live_batch(conn, item)
    for kind, _ in (_stuck_ticks(conn, batch["id"]) if batch else []):
        parts.append("a new start of its review" if kind == "review"
                     else f"a new start of its work, because {_tick_words(kind)}")
    return ", and ".join(parts) + "." if parts else "nothing from you."


def _shift_page(conn: sqlite3.Connection, refs: list[str]) -> tuple[str, list[str]]:
    """
    The shift question as the principal reads it: the new request, the
    earlier request that is not finished, and three answers for its one line
    (frame 193's design, 2.F.2). The refs are the earlier item and the new
    request's statement.
    """
    item = next((r for r in refs if conn.execute(
        "SELECT 1 FROM items WHERE id = ?", (r,)).fetchone()), None)
    said = [conn.execute("SELECT text FROM statements WHERE id = ?", (r,)).fetchone()
            for r in refs if r != item]
    new = " ".join(s["text"] for s in said if s is not None)
    if item is None:
        return f"You asked for something new: {new}", []
    text = conn.execute("SELECT text FROM items WHERE id = ?", (item,)).fetchone()["text"]
    return chr(10).join([
        f"You asked for something new: {new}",
        "Before that you asked for this, and it is not finished:",
        f"  1. {text}",
        f"     Where it stands: {_shift_where(conn, item)}",
        f"     What it waits on: {_shift_waits(conn, item)}",
        "Choose one for line 1:",
        "  - later: put it aside until the new request is merged. Nothing more "
        "about it reaches you until then.",
        "  - now: answer its open page first, then the new request.",
        "  - drop: stop it. Its change is abandoned.",
    ]), [item]


def returned_line(conn: sqlite3.Connection, ask_id: str | None) -> str:
    """
    The line that tells the principal a page came back, or "".

    Frame 267: two sessions on a reply landed no ruling, so `session_commit`
    put the reason on the open page. The person has no name for the
    mechanism, so the line holds no id, no tool name and no refusal text.
    The line number comes from his own reply, and only when the reply names
    exactly one line. The refusal speaks to the seat, so its line is not his.
    Night 158's m122 named line 1, and his words named no line (frame 305).
    """
    from .api import _line_reading

    if not ask_id:
        return ""
    row = conn.execute(
        "SELECT unresolved_note FROM messages WHERE id = ? AND status = 'open' "
        "AND to_role = 'principal' AND unresolved_note IS NOT NULL",
        (ask_id,)).fetchone()
    if row is None:
        return ""
    # `session_commit` writes the note as "<reply id>: <refusal>".
    reply_id = re.match(r"(\w+): ", row["unresolved_note"])
    reply = conn.execute(
        "SELECT id FROM messages WHERE id = ? AND cause_id = ? "
        "AND from_role = 'principal'",
        (reply_id.group(1) if reply_id else None, ask_id)).fetchone()
    # The line parser reads by sentence: a bare "3 is wrong" counts at a
    # sentence start (frame 305, review 1, finding 1).
    lines = _line_reading(said(conn, reply["id"]) if reply else "").named
    about = f" about line {min(lines)}" if len(lines) == 1 else ""
    return ("Your last answer to this page did not reach the team. The team "
            f"could not turn your words{about} into a ruling. Answer the page "
            "again, and say for each line you want changed what to do with it.")


def render_page(conn: sqlite3.Connection, verb: str, refs: list[str],
                question: str | None = None, *,
                ask_id: str | None = None,
                stalled: list[str] | None = None,
                returned: bool = True) -> tuple[str, list[str]]:
    """
    The page of `_page_body`, with the line of `returned_line` on top.

    The line is not numbered, so the order that `parse_reply` reads does not
    move. `returned=False` leaves the line out: the Liaison's landing wake is
    the seat's view of the page, not the principal's.
    """
    page, order = _page_body(conn, verb, refs, question, ask_id=ask_id,
                             stalled=stalled)
    back = returned_line(conn, ask_id) if returned else ""
    # F7: every page to him goes through here, so a removal reaches the next
    # page about its item, whatever kind of page that is. The line is not
    # numbered, so `parse_reply` reads the same order.
    gone = removal_line(conn, refs) if returned else ""
    unnamed = account_unnamed_line(conn, ask_id) if returned else ""
    top = "\n".join(x for x in (back, unnamed, gone) if x)
    return (f"{top}\n{page}" if top else page), order


# The sentence on his next request page after an answer to the account's
# page that named no line there (the review of P9, p3, finding 1).
ACCOUNT_UNNAMED = ("Your last answer named no line of the page about the "
                   "project today, and answers about your request land on "
                   "this page.")


def account_unnamed_line(conn: sqlite3.Connection, ask_id: str | None) -> str:
    """The sentence `ACCOUNT_UNNAMED` on his first request page after his
    answer to the account's page named no line there, or "".

    The rulings door refuses such words on the account's page, and
    `session_commit` keeps the refusal as the page's note, "<reply>:
    <refusal>". The refusal speaks to the seat, so his page holds this
    sentence and no refusal text (frame 267)."""
    from .api import ACCOUNT_NO_LINE

    if not ask_id:
        return ""
    page = conn.execute(
        "SELECT seq, body_refs FROM messages WHERE id = ? AND to_role = "
        "'principal' AND verb IN ('present', 'confirm')", (ask_id,)).fetchone()
    if page is None:
        return ""
    back = conn.execute(
        "SELECT unresolved_note FROM messages WHERE to_role = 'principal' "
        "AND verb = 'present' AND seq < ? AND unresolved_note LIKE ? "
        "ORDER BY seq DESC LIMIT 1",
        (page["seq"], f"%{ACCOUNT_NO_LINE}%")).fetchone()
    reply = conn.execute(
        "SELECT seq FROM messages WHERE id = ? AND from_role = 'principal'",
        (back["unresolved_note"].split(":", 1)[0],)).fetchone() if back else None
    if reply is None or not _request_page(conn, page["body_refs"]):
        return ""
    # His next request page only: a request page between them took it.
    for r in conn.execute(
            "SELECT body_refs FROM messages WHERE to_role = 'principal' "
            "AND verb IN ('present', 'confirm') AND seq > ? AND seq < ?",
            (reply["seq"], page["seq"])):
        if _request_page(conn, r["body_refs"]):
            return ""
    return ACCOUNT_UNNAMED


def _request_page(conn: sqlite3.Connection, body_refs: str | None) -> bool:
    refs = [r for r in json.loads(body_refs or "[]") if not _is_reading(r)]
    return page_owner(conn, refs) is not None


# The removals that one page names. The rest are counted, so ten removals
# take one line (F7).
_REMOVALS_NAMED = 3
_PIECE = re.compile(r"(`+) ?(.+?) ?\1(?: at line (\d+))?")


def _removal_pieces(note: str, owner: str) -> list[dict]:
    """The gone statements of a `removal: ` note, as `_gone_statements`
    shows them: line, owner, line number and whether it is a definition.
    The Architect's reason after the list is not read."""
    out: list[dict] = []
    pos = note.find("removal: ")
    if pos < 0:
        return out
    pos += len("removal: ")
    while True:
        m = _PIECE.match(note, pos)
        if m is None:
            break
        line, no = m.group(2), m.group(3)
        # A removed definition's row is named by the definition itself.
        whole = no is None and line == owner
        out.append({"line": line, "owner": "" if whole else owner, "no": no,
                    "def": whole})
        pos = m.end()
        if not note.startswith(", ", pos):
            break
        pos += 2
    return out


def _behaviour_words(path: str, g: dict) -> str:
    """The plain words for one gone statement: what kind of code it was
    and its first line."""
    line = g["line"]
    if g["def"]:
        return f"the definition `{line}`"
    head = line.split(None, 1)[0].rstrip(":") if line.split() else ""
    kind = {"if": "the branch", "elif": "the branch", "else": "the branch",
            "case": "the branch", "match": "the branch", "for": "the loop",
            "while": "the loop", "return": "the return", "raise": "the error",
            "break": "the loop exit", "continue": "the loop step",
            "try": "the block", "except": "the error handler",
            "with": "the block", "async": "the block"}.get(head)
    if kind is None and line.startswith("@"):
        kind = "the decorator"
    elif kind is None and re.match(r"[\w.\[\]'\", ]+\s*(?:[-+*/|&]?=|:[^=]*=)[^=]", line):
        kind = "the assignment"
    elif kind is None:
        kind = "the call" if "(" in line else "the line"
    return f"{kind} `{line}`"


def removal_line(conn: sqlite3.Connection, refs: list[str]) -> str:
    """One line about the code that the live change of a page's item
    removes and that no grant of his allows, or "".

    F7. Night 171's s164 removed the macOS branch and the XDG return of
    `get_app_dir`, the Architect judged them foreseen, and no page showed
    them to him. The composition: "no work stays invisible". The line is
    information, not a gate: a sign-off by him stays opt-in. It shows
    whatever the Architect judged, and it names no row and no key."""
    batches = [b for b in (_live_batch(conn, item)
                           for item in sorted(_reached(conn, refs))) if b is not None]
    said = _removal_words(conn, batches)
    return f"The change removes code that no answer of yours allowed: {said}." if said else ""


def merged_removal_line(conn: sqlite3.Connection) -> str:
    """One line for the end-of-run summary about the code that the merged
    changes removed and that no grant of his allows, or "".

    F7, pass 1b (ruled: Roman, 2026-10-27, through the coordinator): under
    `merge_gate=auto` nothing holds the merge, so the summary he reads
    after it names each ungranted removal once. A removal that a page
    showed before the merge is named here again. No hold and no gate."""
    batches = list(conn.execute(
        "SELECT id, head_commit FROM batches WHERE status = 'merged' ORDER BY id"))
    said = _removal_words(conn, batches)
    return (f"The merged changes removed code that no answer of yours allowed: "
            f"{said}." if said else "")


def _removal_words(conn: sqlite3.Connection, batches: list) -> str:
    """The removals of the head commits of `batches` that no grant of his
    allows, in plain words: at most three named by kind, function and first
    line, and a count of the rest. "" when there is none."""
    from .api import _gone_targets, batch_ruled_refs

    places: dict[str, list[str]] = {}
    for batch in batches:
        if not batch["head_commit"]:
            continue
        ruled = None
        for r in conn.execute(
                "SELECT path, note FROM touch_strays WHERE batch_id = ? AND "
                "commit_sha = ? AND note LIKE 'removal: %' ORDER BY path",
                (batch["id"], batch["head_commit"])):
            path, _sep, owner = r["path"].partition("::")
            for g in _removal_pieces(r["note"], owner):
                if ruled is None:
                    ruled = batch_ruled_refs(conn, batch["id"])
                if any(granted(conn, x, "remove", _gone_targets(path, g))
                       for x in ruled):
                    continue
                where = (g["owner"] or path.rsplit("/", 1)[-1])
                places.setdefault(where, []).append(_behaviour_words(path, g))
    count = sum(len(v) for v in places.values())
    if not count:
        return ""
    parts: list[str] = []
    left = _REMOVALS_NAMED
    for where, said in places.items():
        if left <= 0:
            break
        shown = said[:left]
        left -= len(shown)
        parts.append(f"in {where}, " + " and ".join(shown))
    more = count - _REMOVALS_NAMED
    tail = f", and {more} more" if more > 0 else ""
    return "; ".join(parts) + tail


def _quiet_line(conn: sqlite3.Connection, refs: list[str]) -> str:
    """
    The count line for ledger rows of kind `other`: the count and the seats.

    The line names no row's words. A seat's account of its own state reached
    him as his assumption on night 165's m172, and he asked three times to
    remove it (frame 325's provenance, section 1).
    """
    seats: list[str] = []
    for ref in refs:
        author = journal_author(conn, "ledger", ref) or "team"
        seat = "the " + author.replace("_", " ").title()
        if seat not in seats:
            seats.append(seat)
    n = len(refs)
    names = (", ".join(seats[:-1]) + " and " + seats[-1]) if len(seats) > 1 \
        else seats[0]
    return (f"Not shown: {n} note{'s' if n != 1 else ''} from {names} that "
            f"{'fit' if n != 1 else 'fits'} no category.")


def _page_body(conn: sqlite3.Connection, verb: str, refs: list[str],
               question: str | None = None, *,
               ask_id: str | None = None,
               stalled: list[str] | None = None) -> tuple[str, list[str]]:
    """
    An ask as a message to a person, and the rows it numbers, in order.

    The page and the input are one contract. The page shows no ids, so the
    input cannot ask for ids. Each rulable row gets a number. A reply of
    "2: <words>" means the second numbered line. `parse_reply` reads the
    same order this returns.

    Measured as the principal (2026-09-04): asks arrived as a verb and a list
    of ids, and a newcomer could not tell what was asked or what approving
    would start. Then the ids were removed from the page while the parser
    still demanded them, and the only reply that worked was "lgtm". This
    function and `parse_reply` fix both faults together.

    `ask_id` names the message the page renders. A park message renders as
    the park page or the note, from the rows, on every read.

    A present renders the request's rows first, through `request_block`,
    and the seats' rows after them under the team's notes. `stalled` names
    the quarantined tick keys of the page. None reads the keys that the
    door recorded when the quarantined wake sent the page.
    """
    from ..core.runner import _resolve_refs
    from ..core.scheduler import park_ask_batch
    from ..onboarding.boot import ZERO

    parked_batch = park_ask_batch(ask_id or "")
    if parked_batch and verb == "present":
        return _park_page(conn, parked_batch, list(refs or []))
    if (ask_id or "").startswith(SHIFT_ASK) and verb == "present":
        return _shift_page(conn, list(refs or []))

    # The read-back lines go last on a present or a confirm page, so no
    # other line number moves. A shift page and a park page returned above,
    # because their maps take no approve (the seam design's review,
    # finding 2). The send door wrote the refs, so a later render shows
    # the same lines (finding 3).
    readings = ([r for r in refs or [] if _is_reading(r)]
                if verb in ("present", "confirm") else [])
    refs = [r for r in refs or [] if not _is_reading(r)]
    # A page is about one request. A row of an item set aside, or of another
    # request than the page's, is no line here (frame 193's design, 2.F.7).
    # A confirm page is about one request too. Night 172's confirm pages
    # ran no filter (P8; ruled: Roman, 2026-10-28 09:10, frame 344).
    if verb in ("present", "confirm"):
        off = off_page(conn, refs, confirm=verb == "confirm")
        refs = [r for r in refs if r not in off]
    resolved = _resolve_refs(conn, refs)
    # The block's rows leave every group, so no id is numbered twice. The
    # sign-off page numbered an item in the block and again under "It
    # would:" (frame 190's design, 2.F, amendment 5).
    in_block: set[str] = set()
    if verb == "present":
        crits = {r["id"] for r in conn.execute(
            f"SELECT id FROM criteria WHERE id IN ({','.join('?' * len(refs))})",
            tuple(refs))} if refs else set()
        in_block = {r for r in refs if isinstance(r, str)
                    and (r in crits or _is_request_item(conn, r))}
        # A code line renders under its item, in the block (frame 298's
        # design, 2.1, point 4).
        in_block |= {r for r in refs if guess_item(r) in in_block}
    said: list[tuple[str, str]] = []
    account: list[tuple[str, str]] = []
    does: list[tuple[str, str]] = []
    does_today: list[tuple[str, str]] = []
    described: list[tuple[str, str]] = []
    does_not: list[tuple[str, str]] = []
    terms: list[tuple[str, str]] = []
    assumed: list[tuple[str, str]] = []
    touches: list[tuple[str, str]] = []
    other: list[tuple[str, str]] = []
    quiet: list[str] = []
    # The page reads the kind itself. A `kind` on the ledger resolve changed
    # the Liaison's wake bytes, and 5 L1-LI cases went stale (frame 325's
    # review, finding 1).
    ids = [r for r in refs if isinstance(r, str)]
    # A run database that predates the column has no `other` row, as
    # `live_criteria` reads no `retired_by` there (frame 325, pass 1d).
    from ..core.db import _has_column

    kind_other = {r["id"] for r in conn.execute(
        f"SELECT id FROM ledger WHERE kind = 'other' AND id IN "
        f"({','.join('?' * len(ids))})", tuple(ids))} if ids and _has_column(
            conn, "ledger", "kind") else set()
    zero = False
    batches: list[str] = []
    for ref in refs:
        if ref in in_block:
            continue
        row = resolved.get(ref)
        if not row:
            words = touch_words(conn, ref, mark_new=verb == "present")
            if words:
                touches.append((ref, words))
                batches.append(ref)
            continue
        if row.get("id") == ZERO:
            zero = True
            continue
        if row.get("term"):
            terms.append((ref, ": ".join(
                x for x in (row["term"], row.get("sense_short")) if x)))
            continue
        if row.get("default_taken"):
            # A note that fits no category is no assumption of his. It is a
            # count with no number, so a reply cannot rule on it (frame
            # 204's design, section 8, ruled 2026-10-11 15:44).
            if ref in kind_other:
                quiet.append(ref)
                continue
            assumed.append((ref, row["default_taken"]))
            continue
        text = next((row[k] for k in ("text", "headline", "body") if row.get(k)), "")
        kind = row.get("kind")
        if kind == "in_scope":
            # What the repository already does is not a plan. seat1
            # (2026-09-12): the signoff page put the account's observed
            # behaviours under "It would:", and the person at the seat read
            # "calculate the tip" as new work. Provenance is the fact.
            if row.get("id") == "how_it_works":
                account.append((ref, text))
            elif row.get("provenance") == "observed":
                does_today.append((ref, text))
            # A description a seat wrote is neither a plan nor a fact about
            # the code. Night 91's summary named the running request as a
            # thing Click includes (frame 80).
            elif row.get("is_description"):
                described.append((ref, text))
            else:
                does.append((ref, text))
        elif kind == "out_of_scope":
            does_not.append((ref, text))
        elif "approval" not in row and row.get("status") in (
                "proposed", "ratified", "superseded", "contradicted", "clarified"):
            said.append((ref, text))
        elif text:
            other.append((ref, text))

    out: list[str] = []
    order: list[str] = []

    def numbered(rows: list[tuple[str, str]], quote: bool = False) -> None:
        for ref, text in rows:
            order.append(ref)
            shown = f'"{text}"' if quote else text
            # His objection stays beside the team's row (frame 357, shape B).
            if principal_objects(conn, ref):
                shown += f" ({NOT_MINE})"
            out.append(f"  {len(order)}. {shown}")

    def account_lines(plan: str | None = None) -> None:
        """The one print of the account rows. An account read from the code
        is the project today, not his request, on every page that shows it.
        Night 150: he contested it six times as the work. Ruled: Roman,
        2026-10-17 04:33, frame 264. An account from his statement on a new
        program is the plan, and `plan` is its heading where a page has one."""
        if not account:
            return
        today = any((resolved.get(ref) or {}).get("provenance") == "observed"
                    for ref, _ in account)
        heading = ACCOUNT_TODAY if today else plan
        if heading:
            out.append(heading)
        numbered(account)

    if verb == "confirm":
        n = len(said) or len(other) or len(refs)
        out.append("Did I hear you right? I have taken this as "
                   + ("one request:" if n == 1 else f"{n} separate requests:"))
        numbered(said, quote=True)
        numbered(other)
        out.append("Reply 'ok' if that is what you meant. Reply with words if "
                   "it is wrong. After 'ok', I work out what to build and show "
                   "you the plan before anything is written.")
    # The keys the quarantined wake sent, never the live ones. A live read
    # turned night 136's open touch note m84 into a stopped page once a key
    # came later (the diff review of 358fed11, finding 4).
    keys = (list(stalled) if stalled is not None
            else door_rows(conn, ask_id, "stalled")) if verb == "present" else []
    # The counts the quarantined wake sent too, for the same reason. Dry4's
    # m63 said "after 0 attempts" once a lift deleted the row (frame 360).
    sent = door_attempts(conn, ask_id) if stalled is None else {}
    # A key the page carries as its own ref reaches no row, so no batch
    # line says it. It gets its own numbered line (frame 354: m3 had none).
    gave_up = [(k, _gave_up_words(conn, [k], sent)[0] + _retries_said(conn, k))
               for k in keys if k in refs]
    batch_keys = [k for k in keys if k not in refs]

    def gave_up_lines() -> None:
        if gave_up:
            out.append("The team gave up on a step:")
            numbered(gave_up)
            # `land` reads his ruling on the line (review p3, finding 1).
            # The menu of the line offers the same two words (review p4,
            # finding 1).
            out.append("Reply 'try again' on a step to run it again. Reply "
                       "'drop' on it to stop it.")

    if verb == "present" and batch_keys and touches:
        # A quarantined batch is no plan any more. Night 136's m96 opened
        # "Before I build this" on a batch the Tester had given up on
        # (frame 190's design, 2.F, amendment 6). A review with no verdict
        # is no code fault. Night 160's m45 said "stopped work" on a change
        # whose 35 tests passed (frame 312's provenance, section 3).
        ticks = _stuck_ticks(conn, batches[0], keys, sent)
        most = max(n for _, n in ticks) if ticks else 0
        if _review_only(ticks):
            out.append("The review of this change stopped"
                       + (f" after {_tries(most)}" if most else "")
                       + " with no verdict. "
                       "Its tests passed at the review's last attempt.")
        else:
            out.append("The team stopped work on this change.")
        asked = request_block(conn, refs, order, out, batch=batches[0],
                              stalled=keys, sent=sent)
        numbered(does)
        account_lines()
        # One sentence per key: m127's two keys in one sentence made 32
        # words (review of P12 pass 1, finding 1).
        out.append(" ".join(f"The team gave up: {p}."
                            for p in _stalled_parts(conn, batch_keys, sent)))
        out.append("The team expects to touch:")
        numbered(touches)
        gave_up_lines()
        out.append("Reply 'ok' if every line says what you want. Name a line "
                   "to correct only that line. Ask, if something here is "
                   "unclear." + _name_request(asked))
    elif verb == "present" and touches:
        out.append("Before I build this, here is what I expect to touch.")
        asked = request_block(conn, refs, order, out, batch=batches[0],
                              stalled=keys, sent=sent)
        numbered(does)
        account_lines()
        out.append("The team expects to touch:")
        numbered(touches)
        if zero:
            out.append("  Some of that code has not been read yet. I cannot say "
                       "what a change there might break.")
        gave_up_lines()
        out.append("This is a prediction, not a promise. Reply 'ok' to go "
                   "ahead. Reply with words if something concerns you."
                   + _name_request(asked))
    elif verb == "present" and zero and not (said or account or described
                                             or does or does_not or in_block
                                             or gave_up):
        out.append("Nothing here has been read yet, so I cannot say what a "
                   "change might break. That is normal for a new or unread "
                   "project.")
        out.append("Reply 'ok' to go ahead. I will flag anything I touch that "
                   "I have not read.")
    elif verb == "present":
        out.append("Here is what I understand you want, on one page.")
        # The request first, the principal's words with it. The seats'
        # rows follow under the team's notes. Night 133's m122 put seven
        # seat rows to the principal and no line of the request.
        from .api import code_stamp

        asked = request_block(conn, refs, order, out, said=said,
                              code=code_stamp(conn, ask_id), stalled=keys,
                              sent=sent)
        guessed = [n for n, r in enumerate(order, 1) if guess_item(r) is not None]
        account_lines(plan="What we are building:")
        if described:
            out.append("How it is described:")
            numbered(described)
        if does_today:
            out.append("It does today:")
            numbered(does_today)
        if does:
            out.append("It would:")
            numbered(does)
        if does_not:
            out.append("It would not:")
            numbered(does_not)
        if assumed or terms or other:
            out.append(TEAM_NOTES)
        if assumed:
            out.append("Where you did not say, I assumed:")
            numbered(assumed)
        if terms:
            out.append("A word that means more than one thing here:")
            numbered(terms)
        numbered(other)
        if quiet:
            out.append(_quiet_line(conn, quiet))
        if zero:
            out.append("Some of this code has not been read yet. I will flag "
                       "anything I touch there.")
        gave_up_lines()
        # A page of stopped steps only has nothing to build, so its 'ok'
        # starts nothing (review p3 of frame 354, finding 4).
        # A page with no request row and no plan row has nothing to build, so
        # its 'ok' approves the page only. Night 175's m145 promised a build
        # that could not start (frame 358).
        # An account from his statement is the plan, so it builds too.
        planned = any((resolved.get(ref) or {}).get("provenance") != "observed"
                      for ref, _ in account)
        builds = bool(said or in_block or does or planned)
        stopped_only = gave_up and set(order) <= {k for k, _ in gave_up}
        if stopped_only:
            pass
        elif builds:
            out.append("Reply in your own words. 'ok' approves all of this "
                       "and starts building. Name a line to correct only "
                       "that line. Ask, if something here is unclear."
                       + _name_request(asked) + _name_guess(guessed))
        else:
            out.append("Reply in your own words. 'ok' approves this page, and "
                       "nothing is built. Name a line to correct only that "
                       "line. Ask, if something here is unclear."
                       + _name_request(asked) + _name_guess(guessed))
    elif verb == "clarify":
        out.append("I need one thing from you before I can continue.")
        if question:
            out.append(f"  {question.strip()}")
        context = [t for _, t in said + account + described + does_today + does
                   + does_not + assumed
                   + terms + other + touches]
        if context:
            out.append("This is about:")
            out += [f"  - {c}" for c in context]
        out.append("Reply in a sentence. I take it from there.")
    else:
        out += [f"  {t}" for _, t in said + account + described + does_today
                + does + does_not + assumed
                + terms + touches + other]
    # A reading he ruled on another page is no line here any more (the
    # review of pass 5, finding 4). A reading of another request is no line
    # either, as at the send door (P8).
    owed = set(readings_owed(conn, refs)) if readings else set()
    for ref in readings:
        line = reading_line(conn, ref, order) if ref in owed else None
        if line:
            order.append(ref)
            out.append(f"  {len(order)}. {line}")
    return chr(10).join(out), order


def render_refs(conn: sqlite3.Connection, refs: list[str]) -> str:
    """
    Refs as words, for the one reader who cannot follow an id.

    `Ask.rendered` has existed since the beginning and nothing ever filled it,
    so `rendered or refs` fell through to the ids every time and the principal
    -- a person -- was shown `[clarify] ['g_69d1e1', 'g_2d422b']` and asked to
    rule on it. Every role downstream of a ref can dereference it; the principal
    is the only one who cannot, which makes them the only one for whom an
    unresolved ref is the whole message.

    Roles are still forbidden to send prose. This is not prose from a role: it
    is the rows the refs already point at, read out at the edge where ids stop
    working. Law 2 governs what travels between roles, and the principal is not
    one.

    A tempting corollary is false, and was tried: that a question to the
    principal must carry something they themselves said, because the glossary is
    our filing and not theirs. `_bind_send` refused a clarify whose refs were all
    glossary terms for about an hour. `L1-LI-relay-an-answer-without-improving-it`
    expects exactly that message -- two senses of one word, no statement -- and
    had passed 335 of 340 recorded runs. "Which of these two meanings did you
    intend" is a complete question, and this function is why: the senses arrive
    as words. The rule refuted the case, so the rule went.
    """
    from ..core.runner import _resolve_refs

    resolved = _resolve_refs(conn, refs)
    lines = []
    for ref in refs:
        row = resolved.get(ref)
        if not row:
            # A batch is the one ref with no words of its own: what it means
            # to the seat is its predicted touch, read out here at the edge
            # the same way a term's two senses are (P4, 2026-09-03).
            words = touch_words(conn, ref)
            lines.append(f"  {ref}: {words}" if words else f"  {ref}")
            continue
        # The readable column differs by table and the principal does not need
        # to know which table they are looking at. A term is the one row where
        # two columns are needed: the whole reason two glossary rows reach the
        # principal at all is that the word is the same and the sense is not, so
        # rendering the word alone shows them "delete" and "delete".
        if row.get("term"):
            words = ": ".join(x for x in (row["term"], row.get("sense_short")) if x)
        elif row.get("default_taken"):
            # An assumption, read out as one: the sentence a desk wrote where
            # the principal's words were silent, and what it costs to be wrong.
            words = f"assumed: {row['default_taken']}"
        else:
            words = next((row[k] for k in ("text", "headline") if row.get(k)), "")
        lines.append(f"  {ref}: {words}" if words else f"  {ref}")
    return "\n".join(lines)


def touch_words(conn: sqlite3.Connection, batch_id: str,
                mark_new: bool = False) -> str:
    """The batch's predicted touch as words, or '' when the id is no batch.
    `mark_new` marks a predicted test path that the code index lacks."""
    from ..core.lifecycle import touch_set

    t = touch_set(conn, batch_id)
    if not t:
        return ""
    item = t["item"]

    def shown(path: str) -> str:
        # A test file the index does not hold does not exist yet. Night
        # 136's principal could not tell a predicted file from a real one
        # (frame 190's design, 2.5). The page alone marks it: a seat's
        # working set keeps the words its recordings hash.
        if not mark_new or "tests" not in path.replace(chr(92), "/").split("/")[:-1]:
            return path
        held = conn.execute("SELECT 1 FROM code_index WHERE grain = ?", (path,)).fetchone()
        return path if held else f"{path} (a new file)"

    # Words, no ids: the page shows none by contract, and seat1 (2026-09-12)
    # read "the batch for s2 (...)" to the person at the seat.
    parts = ["the work for: " + (item.get("text") or "this item")]
    parts.append("expected to touch "
                 + (", ".join(shown(p) for p in t["expected"]) if t["expected"]
                    else "nothing named"))
    if t["possible"]:
        parts.append("might touch " + ", ".join(t["possible"]))
    if t["unsurveyed"]:
        parts.append("unsurveyed ground: " + ", ".join(t["unsurveyed"]))
    # A stated commitment reaches him in its own sentence below and in no
    # other part, so no other words of understanding reach him (design B,
    # section 3.5 and section 4.2, step 5).
    from .api import commitments_held

    stated = {r["id"] for r in conn.execute(
        "SELECT id FROM constraints WHERE witness != '' AND party != ''")
              } if commitments_held(conn) else set()
    plain = [c for c in t["commitments"] if c["id"] not in stated]
    if plain:
        parts.append("commitments: " + ", ".join(
            f"{c['headline']} (bound to {c['bound_to']})" for c in plain))
    # The lazy rows wait for this moment, their first touch (frame 361).
    from ..core.lifecycle import first_touch_words

    lazy = first_touch_words(conn, batch_id, omit=stated)
    if lazy:
        parts.append(lazy)
    from .api import touch_commitments

    # One sentence per commitment, in the Critic's order, so he reads what
    # the review holds the change to (frame 362, slice pass 4).
    keep = [f"It must keep: {_clause(c['behaviour'])}, because "
            f"{_clause(c['party'])} depend on it."
            for c in touch_commitments(conn, batch_id)]
    # The gates excuse a test red at the base, so he sees the record here
    # (frame 362, pass 5b, review high 1).
    from ..core.harness import base_red_ids

    red = base_red_ids(conn, batch_id)
    if red:
        marks = ", ".join("?" for _ in red)
        files = [r["path"] for r in conn.execute(
            f"SELECT path FROM tests WHERE id IN ({marks}) ORDER BY path",
            sorted(red))]
        keep.append(f"{len(files)} of the repository's tests were red before "
                    f"this change: {', '.join(files)}.")
    return "; ".join(parts) + ("." + "".join(" " + s for s in keep) if keep else "")


def _clause(words: str) -> str:
    """Seat words as a clause inside a sentence of the page."""
    return (words or "").strip().rstrip(".").strip()


def pump(conn: sqlite3.Connection, backend: PrincipalBackend) -> list[str]:
    """
    Offer every pending ask to the principal; land any answers as new messages.

    Returns the ids of messages created. A deferred ask stays open — that is the
    agenda tick's material next time the principal shows up, and it is why deferral
    costs nothing now and reappears at the lineage's gates later.
    """
    created: list[str] = []

    for ask in pending_asks(conn):
        answer = backend.respond(ask)
        if answer is None:
            continue                       # deferral is always allowed
        msg_id = land(conn, ask, answer)
        if msg_id:
            created.append(msg_id)

    return created


def door_rows(conn: sqlite3.Connection, message_id: str | None, kind: str) -> list[str]:
    """The rows the send door recorded about a message: `stamped`, the
    request rows it added, or `stalled`, the quarantined keys of its wake."""
    row = conn.execute("SELECT value FROM config WHERE key = ?",
                       (f"{kind}:{message_id}",)).fetchone() if message_id else None
    try:
        rows = json.loads(row["value"]) if row else []
    except (TypeError, ValueError):
        return []
    return [r for r in rows if isinstance(r, str)]


def door_attempts(conn: sqlite3.Connection, message_id: str | None) -> dict[str, int]:
    """The count of each `stalled` key that the send door recorded about a
    message, as `attempts:<id>`. A page from before the record gets {}."""
    row = conn.execute("SELECT value FROM config WHERE key = ?",
                       (f"attempts:{message_id}",)).fetchone() if message_id else None
    try:
        counts = json.loads(row["value"]) if row else {}
    except (TypeError, ValueError):
        return {}
    if not isinstance(counts, dict):
        return {}
    return {k: n for k, n in counts.items() if isinstance(n, int) and n > 0}


def seen_order(conn: sqlite3.Connection, reply_id: str | None,
               ask: Ask | None) -> list[str]:
    """The rows of page `ask` in the order he saw them at reply `reply_id`.
    This is the one reader of that order (fact F28).

    `land` records the order at his reply, and the record comes first. His
    line numbers belong to the page as he saw it, and a render reads today's
    rows. Frame 272 counted 73 of 693 named rows on nights 158 and 159 that
    were not the row he saw. A reply with no record, from before frame 272,
    takes today's render of `ask`. With no `ask`, the reader takes the
    record only, for a reader that keeps his words when no record exists."""
    order = door_rows(conn, reply_id, "order")
    if order or ask is None:
        return order
    # The render can differ from the order the Liaison ruled on. The window
    # is an earlier open ruling that lands first in the same `apply_rulings`
    # loop and moves a row. The batch's line then shifts, and `land` drops
    # the contest with no error (frame 255, review 1, finding 2).
    row = conn.execute("SELECT body_text FROM messages WHERE id = ?",
                       (ask.message_id,)).fetchone()
    return render_page(conn, ask.verb, list(ask.refs),
                       row["body_text"] if row else None,
                       ask_id=ask.message_id)[1]


def page_ask(row) -> Ask:
    """The `Ask` of a `messages` row of a page, for `seen_order`."""
    return Ask(message_id=row["id"], verb=row["verb"],
               refs=json.loads(row["body_refs"] or "[]"))


def _reply_of(conn: sqlite3.Connection, ruling_id: str | None) -> str | None:
    """The reply that ruling `ruling_id` reads, or None for a verdict
    straight from the seat."""
    row = conn.execute("SELECT reply_id FROM rulings WHERE id = ?",
                       (ruling_id,)).fetchone() if ruling_id else None
    return row["reply_id"] if row else None


def _step_verdicts(per_item: dict, steps: list[str]) -> dict:
    """`per_item` with each word of a stopped step's menu read as its
    verdict. A step verdict off the menu raises ValueError."""
    # The page says 'try again' and 'drop', so a script that copies the
    # page's word lands. A stored 'drop' left the step 'Stuck' (review p5
    # of frame 354, finding 2). `_STEP_ROWS` is the one map of the words.
    from .api import _MENU_BASE, _STEP_ROWS

    out = {}
    for ref, verdict in per_item.items():
        if ref in steps and verdict not in ("approve", "contest", "revise"):
            if verdict not in _STEP_ROWS:
                raise ValueError(
                    f"{ref}: {verdict!r} moves no stopped step. A step takes "
                    f"{'; '.join(_MENU_BASE['step'])}")
            verdict = _STEP_ROWS[verdict][0]
        out[ref] = verdict
    return out


def land(conn: sqlite3.Connection, ask: Ask, answer: Answer,
         ruling_id: str | None = None) -> str | None:
    """
    Land one answer as a message, if the ask is still open.

    `ruling_id` names the Liaison's `rulings` row when the verdict comes
    through `apply_rulings`. Without one, the verdict came straight from the
    seat, and the door writes a landed `rulings` row for it: a `ruling` ref
    targets that row, so every verdict needs one.

    The answer's door, split from `pump` so it can be hurt on its own
    (`test_chaos_confirm.py`, loop 3's injuries). Two principals can read the
    same open present -- two consoles, one checkout -- and both answer it; the
    first to land wins and the second is refused here rather than stacked,
    because two rulings on one present relay two rulings to the owner, and
    which one it applied would be decided by arrival order. And a present the
    world moved past is `superseded` at the door every present lands through
    (`db.py`, where a session's messages are inserted: a later present of the
    same row is the one to answer), so it is no longer open, and a ruling for
    it from a screen that never refreshed lands nothing -- it would approve a
    version of the row the principal never saw. Returns the new message id,
    or None when the ask was no longer open.
    """
    # Words, not a ruling. The ask stays open: the Liaison reads the words
    # in `landing` mode and records the ruling, and the ruling lands here
    # through `apply_rulings` after that session commits. The reply is a
    # principal `converse` whose cause is the ask, which is what keys the
    # mode. The words go on the message and into the transcript.
    if answer.verb == "reply":
        still_open = conn.execute(
            "SELECT 1 FROM messages WHERE id = ? AND status = 'open'",
            (ask.message_id,)).fetchone()
        if not still_open or not answer.text.strip():
            return None
        msg_id = new_id("m", conn)
        seq = conn.execute(
            "SELECT COALESCE(MAX(seq), 0) + 1 n FROM messages").fetchone()["n"]
        thread = conn.execute(
            "SELECT thread_id FROM messages WHERE id = ?", (ask.message_id,)
        ).fetchone()["thread_id"]
        conn.execute(
            "INSERT INTO messages (id, cause_id, cause_kind, thread_id, from_role, "
            "to_role, verb, body_refs, body_text, seq, status) "
            "VALUES (?, ?, 'message', ?, 'principal', 'liaison', 'converse', "
            "?, ?, ?, 'open')",
            (msg_id, ask.message_id, thread, json.dumps(ask.refs),
             answer.text.strip(), seq))
        record_entry(conn, msg_id, answer.text.strip())
        # His line numbers belong to the page as he saw it. A later render
        # reads today's rows, and night 159's m105 had lost its line 1 by
        # s239's wake (frame 272, review 1, finding 1). The record is the
        # reply's, because a second reply to the open page can see another
        # order (frame 272, review 2, finding 1).
        if ask.order:
            conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                         (f"order:{msg_id}", json.dumps(ask.order)))
        return msg_id

    # No words and no ruling is no answer. The ask stays open, as an
    # empty reply does above. The onboard-only walk of clickI (2026-09-16)
    # answered a clarify with an empty converse: the ask closed, a
    # `rulings` row of nothing landed, and `term_collision` put the same
    # question again, seventeen times. Silence is not consent.
    if not (answer.text or "").strip() and not answer.per_item:
        return None

    # A stopped step takes the words of its menu, read before the ask
    # closes, so a refused verdict leaves the ask open.
    from ..core.scheduler import rowless_key

    steps = ([k for k in door_rows(conn, ask.message_id, "stalled")
              if rowless_key(conn, k)]
             if ask.verb == "present" and answer.verb == "verdict" else [])
    given = _step_verdicts(answer.per_item or {}, steps)
    closed = mark_answered(conn, ask.message_id, only_open=True)
    if not closed:
        return None
    # A landed answer to a stopped page lifts the quarantined Developer start
    # key it shows, once, because the page closes here. The next Developer
    # reads his ruling. Night 163's m115 to m139 restarted the team only
    # through corrections he did not mean (frame 312, review w5, finding 2).
    from ..core.db import lift_keys
    from ..core.scheduler import key_parts

    lift_keys(conn, [k for k in door_rows(conn, ask.message_id, "stalled")
                     if key_parts(k)[:2] == ("developer", "tick:batch_start")])
    # The shift question changes no item. Its answer is one `item_parks` row,
    # and a drop closes the earlier request's open asks and notes (frame
    # 193's design, 2.F.3).
    if (ask.message_id or "").startswith(SHIFT_ASK) and answer.verb == "verdict":
        return _land_shift(conn, ask, answer, ruling_id)

    # A touch note is read, not ruled on (P4, R7: nothing waits on it). A
    # batch's ref leaves the ruling, except in two cases that keep a contest
    # or a revise of it: before the head commit, and after the head commit
    # when the words fault the batch's line (frame 190, frame 255). What is
    # left, if it is all approve, is an acknowledgement --
    # the note closes and wakes nobody. A contest or revise on the item lands
    # as any ruling does: the owner amends it, the version moves, and the
    # revocation is what ends the batch (loop 6) -- the lever the note is for.
    # Before the build, a contest or a revise of the batch line stays in the
    # verdict, and the relay takes it to the Architect, who wrote the
    # prediction (frame 190's design, 2.2, the batch line, point 2). After the
    # head commit, a contest or a revise stays only when the words fault the
    # line (frame 255, below). An approve of a batch line is always dropped.
    # Only a live batch keeps its line, and an approve of an item leaves a
    # touch note's verdict. A contest of the batch line kept the verdict
    # alive, and the item's approve then set a draft item approved off the
    # sign-off page (the diff review of 2dace61b, finding 4).
    per_item = dict(given)
    # A read-back line rules his own answer and no row of an owner, so it
    # leaves the relay. Its `ruled_refs` row is the record (the seam
    # design, 2.3).
    readings = {k: v for k, v in per_item.items() if _is_reading(k)}
    per_item = {k: v for k, v in per_item.items() if not _is_reading(k)}
    # A stopped step that names no row is a line he rules on. A contest or a
    # revise runs the step again, and an approve drops it. Review p3 of frame
    # 354, finding 1: his '1 contest: try again' lifted nothing. The lift is
    # `lift_keys`, the one delete of a quarantine (fact F20). No park owns
    # such a key, because `park_owns` reads a batch and the key names none
    # (frame 142's design, 2.D).
    from ..core.db import mark_ruled

    # 'ok' over a page of stopped steps only names no line, and it drops them.
    if steps and not per_item and set(ask.refs) <= set(steps):
        per_item = {k: "approve" for k in steps}
    ruled_steps = {k: v for k, v in per_item.items()
                   if k in steps and v in ("approve", "contest", "revise")}
    lift_keys(conn, [k for k, v in ruled_steps.items() if v != "approve"])
    mark_ruled(conn, [k for k, v in ruled_steps.items() if v == "approve"])
    # The answer as given names the item, whatever a filter or a resume drops.
    ruled = set(answer.per_item or {})
    if ask.verb == "present" and answer.verb == "verdict":
        rows = conn.execute("SELECT id, head_commit, status FROM batches").fetchall()
        batches = {r["id"]: (not r["head_commit"]
                             and r["status"] not in ("merged", "abandoned"))
                   for r in rows}
        # law 9: a contest reaches the row's owner, who amends; an approve never skips it
        # After the head commit, a contest or a revise of the batch line stays
        # when the words fault that line. `rulings_rule` admits the row on the
        # same predicate, so the row it admits relays to the Architect as
        # before the commit (frame 255). Over nights 136 to 149 the predicate
        # fires on 14 of 16 files corrections and refuses 9 of 9 contests the
        # words do not support. `_line_refusal` stops none of the 9 (observed:
        # `pred.py`, 2026-10-15). Frame 142's design, 2.D, dropped every such
        # row, and a files correction now reaches the Architect who wrote it.
        built = [r["id"] for r in rows if r["head_commit"]
                 and r["status"] not in ("merged", "abandoned")
                 and per_item.get(r["id"]) in ("contest", "revise")]
        if built and (answer.text or "").strip():
            from .api import _line_reading, built_line_faulted

            faulted = _line_reading(answer.text)[0]
            order = ask.order or (seen_order(conn, _reply_of(conn, ruling_id), ask)
                                  if faulted else [])
            for ref in built:
                batches[ref] = built_line_faulted(answer.text, order, ref, faulted)
        if set(batches) & set(ask.refs):
            items = {r["id"] for r in conn.execute("SELECT id FROM items")}
            per_item = {k: v for k, v in per_item.items()
                        if (k not in batches and not (k in items and v == "approve"))
                        or (k in batches and v in ("contest", "revise") and batches[k])}
            if all(v == "approve" for v in per_item.values()):
                return None

    # law 9: a contest reaches the row's owner, who amends; an approve never skips it
    # An approve lands on a row the wake put on the page, and never on a
    # request row the door stamped. An "ok" on an agenda page would have
    # approved a contested item before its owner amended it, night 133's
    # wall 5 (frame 190's design, 2.F, amendment 1). An "ok" on an account
    # page approved the stamped open requests, night 133's m212 (the diff
    # review of 358fed11, finding 1). An item's own present after an amend
    # still approves it, because the item is the wake's row. A contest or a
    # revise lands on every row. The park page writes its rows itself, and
    # the door records no stamp there.
    # law 3: a message routes to the writer of the artefact holding the answer
    # A ruling on a code line goes to the row the principal read, as the send
    # door stamped it, and never to a live lookup. An approve leaves. A batch
    # target becomes the batch's key, so frame 190's route takes it to
    # `annotate`, and a built batch keeps it only when the words fault the
    # code (frame 255). No `items` state is written for a code line, so the
    # item keeps its approval and `cancel` cannot fire (frame 298's design,
    # 3.2).
    from .api import code_stamp, guess_item

    guess_targets: dict[str, list] = {}
    # A code key whose ruling moves to its batch. The landed row of the
    # batch names the row of the key it derives from (fact F1).
    moved: dict[str, str] = {}
    if answer.verb == "verdict" and any(guess_item(k) for k in per_item):
        stamp = code_stamp(conn, ask.message_id)
        for key in [k for k in per_item if guess_item(k)]:
            ruling = per_item.pop(key)
            if ruling not in ("contest", "revise"):
                continue
            target = stamp.get(key) if isinstance(stamp.get(key), dict) else {}
            batch_id = target.get("batch")
            if batch_id:
                batch = conn.execute("SELECT head_commit, status FROM batches "
                                     "WHERE id = ?", (batch_id,)).fetchone()
                if batch is None or batch["status"] in ("merged", "abandoned"):
                    continue
                if batch["head_commit"]:
                    from .api import code_line_faulted

                    order = ask.order or seen_order(
                        conn, _reply_of(conn, ruling_id), ask)
                    if not code_line_faulted(answer.text or "", order, key):
                        continue
                per_item[batch_id] = ruling
                moved[batch_id] = key
                continue
            per_item[key] = ruling
            shown = target.get("guess")
            if not shown:
                last = conn.execute(
                    "SELECT item_ver, ruling_id FROM touch_guesses WHERE item_id = ? "
                    "ORDER BY rowid DESC LIMIT 1", (guess_item(key),)).fetchone()
                shown = [last["item_ver"], last["ruling_id"]] if last else None
            guess_targets[key] = shown
        if not per_item:
            return None

    stamped = set(door_rows(conn, ask.message_id, "stamped"))
    if ask.verb == "present" and answer.verb == "verdict" and per_item and stamped:
        per_item = {k: v for k, v in per_item.items()
                    if k not in stamped or v in ("contest", "revise")}

    msg_id = new_id("m", conn)
    seq = conn.execute(
        "SELECT COALESCE(MAX(seq), 0) + 1 n FROM messages").fetchone()["n"]
    thread = conn.execute(
        "SELECT thread_id FROM messages WHERE id = ?", (ask.message_id,)
    ).fetchone()["thread_id"]

    # A ruling on an assumption closes here, at the keypress, whichever way
    # it went: a decision row under the principal's name that resolves the
    # ledger entry -- the two writes `decisions.author` makes, made by the one
    # author a ruling has. Law 11 (an entry is resolved by a decision that
    # names it, in the same commit, and by nothing else) and SEAT.md's
    # contract (a decided row enters the record only from a keypress).
    # Approve takes the default. Contest overrules it, with the words. The
    # contest reaches the row the assumption was about only when the answer
    # gives no ruling on that row (frame 225's pass 2, below). Either way
    # the ledger id
    # leaves the relay's refs -- the owner has nothing to apply to it, and
    # told to `set_approval` a ledger id it would only be refused. Measured
    # first the other way (2026-09-03): `decisions.author` handed to the
    # relay mode drew fourteen decisions a session, five of five, on the
    # plain approve case too. The tool in the list was the invitation.
    # (`per_item` is the ruling less the batch refs that the touch-note door
    # above drops. A contest or a revise of a batch line stays before the
    # head commit, and after it when the words fault the line.)
    # A resume writes one `principal` row and no `items` row, so the item
    # returns to the state it held (frame 193's design, 2.F.4).
    resumed = [ref for ref, ruling in per_item.items() if ruling == "resume"]
    if resumed:
        seq_now = conn.execute(
            "SELECT COALESCE(MAX(seq), 0) + 1 n FROM messages").fetchone()["n"]
        for ref in resumed:
            for item in _items_reached(conn, ref):
                _write_park(conn, item, "resume", "shift", msg_id, seq_now)
            per_item.pop(ref)
    # A ruled step closed above. No owner has a row to apply it to.
    closed_here: list[str] = [k for k in ruled_steps if k in per_item]
    # The page's request, read once and only when a note's contest needs it.
    unread = object()
    page_req: object = unread
    for ref, ruling in list(per_item.items()):
        if ruling not in ("approve", "contest", "revise"):
            continue
        # A row that the merge parked while its page was open is still his
        # word to give. The ruling lands, and the row leaves `parked` (frame
        # 316's review 2, finding 1).
        row = conn.execute(
            "SELECT id, about_ref, default_taken, kind FROM ledger "
            "WHERE id = ? AND status IN ('open', 'parked')", (ref,)).fetchone()
        if row is None:
            continue
        if ruling == "approve":
            text = f"default taken at signoff: {row['default_taken']}"
        else:
            said = answer.text.strip() if answer.text else "contested at signoff"
            text = f"overruled at signoff: {said} (was assumed: {row['default_taken']})"
            # A contested assumption contests its item, unless the item is
            # what the repository already does. seat2 on click (2026-09-12):
            # contesting seven reconcile findings put two observed items
            # into the contested loop, and the run asked the Vision Keeper
            # to amend behaviour that exists. The finding was wrong; the
            # code is not.
            about = conn.execute(
                "SELECT provenance FROM item_provenance WHERE id = ?",
                (row["about_ref"],)).fetchone()
            # law 9: a contest reaches the row's owner, who amends; an approve never skips it
            # A request row that the door stamped has the principal's own
            # ruling, and a note's contest never overwrites it. The door
            # stamps every request criterion as a line, so a note about c1
            # turned an approve of c1 into a contest (the delta review of
            # 2c602d1b, finding 1). A wake's own row keeps the old rule: the
            # contest of a note about it contests it.
            # Roman ruled that a contest with words goes back to the desk that
            # assumed it (ruled: Roman, 2026-09-03, DECISIONS.md, the seed
            # interview). The build session chose the carrier on 2026-09-04:
            # the contested note contests its item, and the owner amends it.
            # Frame 225's pass 2 keeps that carrier only when the answer gives
            # no ruling on the item (2026-10-14, plans/frame225-history-read.md).
            # An explicit ruling on the item wins over an inferred one, for a
            # note of every kind. The inferred one lost bg_1 on night 144 and
            # bg_6 on night 146. On an approve, the relay takes the words to
            # the item's owner as `principal_said`, and the decision keeps them.
            # A note about an item of another request contests the note, not
            # the item. Night 152's m60 faulted a note about the merged
            # `echo_json` on the confirm page, and the carrier contested
            # `echo_json`. Over nights 130 to 152 the skip fires on 6 of 6
            # such writes and refuses 0 of 36 right calls (frame 274,
            # `plans/frame274-count.md`). The decision row and the relay
            # still take his words to the note's owner. A page with no
            # request, such as the account page, keeps the carrier.
            if row["about_ref"] not in ruled and \
                    not (about and about["provenance"] == "observed") and \
                    row["about_ref"] not in stamped:
                if page_req is unread:
                    page_req = page_request(conn, ask.refs)
                # The owner comes from the items the note reaches. A note
                # about `cr_1` once had no owner, and night 161's m234
                # contested the merged confirm item's `cr_1` (frame 316,
                # `plans/frame316-provenance.md`, repair 1). A description
                # has no request, so a note about `how_it_works` keeps its
                # contest (frame 274's review 1, finding 1). A note that
                # reaches no item keeps the carrier.
                owners = requests_of(conn, row["about_ref"])
                elsewhere = bool(owners) and all(
                    o is not None and o != page_req for o in owners)
                if page_req is None or not elsewhere:
                    per_item[row["about_ref"]] = "contest"
        conn.execute(
            "INSERT INTO decisions (id, author, text, refs, resolves_ledger) "
            "VALUES (?, 'principal', ?, ?, ?)",
            (new_id("d", conn), text, json.dumps([row["about_ref"]]), ref))
        # A closed entry lifts the keys about it (frame 242).
        from ..core.db import write_state

        write_state(conn, "ledger", ref,
                    "UPDATE ledger SET status = 'resolved' WHERE id = ?", (ref,))
        closed_here.append(ref)

    # The ruling lands on the rows it names, here, at the keypress.
    #
    # The owner used to apply it. The owner was woken with the verdict and
    # told to write the state for each ruling, from a lookup table in its own
    # brief. Measured as the principal (tips7, tips8, 2026-09-04): given five
    # refs, the model applied two, invented a third on a statement, and
    # dropped `how_it_works`. The account never left `draft`. `tick_signoff`
    # fired again. The principal got the same page again, with no exit.
    #
    # The state that follows from a ruling is not a judgement. So the state
    # lands here. The relay still goes out for the judgement half: an
    # amendment the words demand, and the order of the approved items.
    # `approval_ver` is stamped against the current version. That keeps law
    # 9 true: no batch schedules unless its approval postdates its last
    # amendment.
    # A drop ends the item, so no owner amends it and no later ruling revives
    # it. Dry1's m101 "Drop 1 and 3" landed as a contest, and the Vision
    # Keeper put his words into line 1 (frame 357, pass 2).
    ended = _item_drops(conn, ruling_id, per_item)
    # A drop on the team's row is his objection on file. The row keeps its
    # state and leaves the relay, so no seat defends it and no clarify asks
    # him again (ruled: Roman, 2026-11-02 11:43, frame 357, shape B).
    objected = _row_objections(conn, ruling_id, per_item)
    for ref, ruling in per_item.items():
        if ref in closed_here or ref in objected:
            continue
        state = "dropped" if ref in ended else {
            "approve": "approved", "contest": "contested",
            "revise": "contested"}.get(ruling)
        if state is None:
            continue
        # An approval change is an exit from a quarantine. This raw write
        # skipped the lift, so night 147's approve left the contested tick
        # quarantined, and the walk's end said the team gave up (frame 240).
        # The guard on the old value keeps frame 80's rule: a same-value write
        # revives nothing. Law 6.
        from ..core.db import write_state

        write_state(conn, "items", ref,
                    "UPDATE items SET approval = ?, approval_ver = version "
                    "WHERE id = ? AND approval IS NOT ? "
                    "AND approval != 'dropped'", (state, ref, state))

    # The open asks about the items he dropped close, by the shift drop's
    # path. Dry1's clarifies m108, m112 and m114 stayed open (review p2 of
    # frame 357, finding 3).
    if ended or objected:
        _close_asks_about(conn, ended, msg_id, rows=objected)
    gone = dropped_items(conn) | objected
    refs = [r for r in (list(per_item) if answer.per_item else ask.refs)
            if r not in closed_here and not _is_reading(r) and r not in gone]
    # A page whose every row closed at the keypress leaves nothing for an
    # owner to do. The verdict is the record and lands answered. Relayed,
    # it woke the Terminologist with a ruling on a done row; it adopted the
    # ledger id, was refused, logged the refusal as a new assumption, and
    # the agenda put that row to the principal: 36 rounds (tipsQ,
    # 2026-09-09). A ruling whose every line was a request approve off the
    # sign-off page leaves nothing either.
    # A ruled step is settled either way, and it keeps its landed row, so
    # the reader of earlier answers finds his ruling (frame 354, pass 5).
    approved_here = [r for r in closed_here if per_item.get(r) == "approve"
                     and r not in ruled_steps]
    settled = (bool(answer.per_item or ruled_steps) and not refs
               and len(approved_here) + len(ruled_steps) == len(closed_here))
    # A park page approved whole is the ceiling. The team stops here and the
    # parked line says so, so no Liaison session wakes on the verdict
    # (ruled: Roman, 2026-10-08, the park ask is a page with rows, point 5).
    # A check line is a ruled line and no ref since aa999fd1, so a contest of
    # it left the verdict closed and reached no Tester (frame 330, pass 4).
    # An "ok" that names no check line still approves the page whole.
    # `apply_rulings` passes no order, so the lines come from his reply's
    # record. Dry1's r_m139 came by that path (review p4 of frame 330, high 1).
    from ..core.scheduler import park_ask_batch

    if (ask.verb == "present" and park_ask_batch(ask.message_id or "")
            and ask.refs and all(per_item.get(r) == "approve" for r in ask.refs)):
        lines = {*ask.refs, *(ask.order or seen_order(
            conn, _reply_of(conn, ruling_id), ask))}
        if all(v == "approve" for r, v in per_item.items() if r in lines):
            settled = True
    conn.execute(
        "INSERT INTO messages (id, cause_id, cause_kind, thread_id, from_role, "
        "to_role, verb, body_refs, seq, status) "
        "VALUES (?, ?, 'message', ?, 'principal', 'liaison', ?, ?, ?, ?)",
        (msg_id, ask.message_id, thread, answer.verb, json.dumps(refs), seq,
         "answered" if settled else "open"),
    )

    # The per-row verdict is the `landed` rows of `ruled_refs` below, and
    # `verdict_for` reads them (fact F1, law 11).
    # The set the principal read, for the Architect who rewrites it (frame
    # 298's design, 3.2, point 3).
    if guess_targets:
        conn.execute(
            "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
            (f"guess_target:{msg_id}", json.dumps(guess_targets)))
    if answer.text:
        conn.execute(
            "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
            (f"entry:{msg_id}", json.dumps(answer.text)),
        )
        record_entry(conn, msg_id, answer.text)
    # The ruling as a row with a version. The Liaison's reading has its own
    # row and `apply_rulings` marks it landed after this returns. A verdict
    # from the seat lands the Liaison's open row when one is on the same
    # ask. `apply_rulings` then finds no open row and marks no second one.
    # When no row exists for the ask, the door writes one here, landed,
    # keyed by the verdict message so a replay lands the same id.
    # The verdicts landed before this one, read before this one lands.
    prior: dict = {}
    for r in conn.execute("SELECT per_item FROM rulings WHERE status = 'landed' "
                          "ORDER BY rowid"):
        prior.update(json.loads(r["per_item"] or "{}"))
    if ruling_id is None:
        opened = [r["id"] for r in conn.execute(
            "SELECT id FROM rulings WHERE ask_id = ? AND status = 'open' "
            "ORDER BY rowid", (ask.message_id,))]
        conn.execute(
            "UPDATE rulings SET status = 'landed', verdict_id = ? "
            "WHERE ask_id = ? AND status = 'open'", (msg_id, ask.message_id))
        # No open ruling on the ask: his key is a ruling of its own. An
        # earlier landed ruling on the ask does not stop it, or his approve
        # over his own earlier contest is lost (fact F1, review 1, finding 1).
        if not opened:
            _insert_keypress_ruling(conn, ask, msg_id, {**per_item, **readings},
                                    (answer.text or "").strip(),
                                    held=tuple(steps))
        # His keypress is his verdict, and the Liaison's reading is a
        # reading. So the keypress gets its own rows under the landed
        # ruling, beside the reading's rows (law 11; fact F1).
        for rid in opened:
            _insert_keypress_rows(conn, rid, ask, msg_id,
                                  {**per_item, **readings},
                                  (answer.text or "").strip(), shared=True,
                                  held=tuple(steps))
    # The verdict that the relays read is the one this door computed: a
    # stamped approve is gone, a code key is on its batch, and an approve
    # that closed a ledger row needs no relay. It lands as `landed` rows on
    # every path, also where no key was pressed (fact F1, law 11).
    remaining = {r: v for r, v in per_item.items()
                 if r not in approved_here and not _is_reading(r)}
    rulings_here = [ruling_id] if ruling_id else [
        r["id"] for r in conn.execute(
            "SELECT id FROM rulings WHERE verdict_id = ? ORDER BY rowid",
            (msg_id,))]
    for rid in rulings_here:
        _insert_landed_rows(conn, rid, ask, msg_id, remaining, moved,
                            (answer.text or "").strip())
    _drop_statements(conn, rulings_here)
    # A landed ruling on a row of a running batch moves what its seats read.
    # Night 170's m92, m98 and m103 ruled on b_3 and its criterion, and
    # `tester|tick:tests_missing|b_3` stayed (review of F20 pass 1, finding 1).
    from ..core.db import lift_batch_seats

    # A verdict the row already holds is no new act, so it lifts nothing,
    # as a commit that changes no behaviour lifts nothing (frame 318; F20
    # pass 1c). A batch's ref reaches its item, so the item's batches hold it.
    ruled = sorted({i for r, v in per_item.items()
                    if not _is_reading(r) and prior.get(r) != v
                    for i in _items_reached(conn, r)})
    if ruled:
        lift_batch_seats(conn, [r["id"] for r in conn.execute(
            "SELECT id FROM batches WHERE item_id IN (%s) ORDER BY id"
            % ",".join("?" * len(ruled)), ruled)])
    return msg_id


def _drop_statements(conn: sqlite3.Connection, rulings: list[str]) -> None:
    """Write `dropped` on each proposed statement that a landed row of
    `rulings` drops.

    Dry1's r_m75 dropped s2 and s3 and wrote nothing, so `awaiting_confirm`
    asked again as m77. The seat's "ok" on m77 then ratified the request he
    had dropped (frame 357; composition.md, no work he did not ask for)."""
    from ..core.db import write_state

    if not rulings:
        return
    marks = ",".join("?" * len(rulings))
    for r in conn.execute(
            f"SELECT DISTINCT rr.ref FROM ruled_refs rr JOIN statements s "
            f"ON s.id = rr.ref WHERE rr.ruling_id IN ({marks}) "
            f"AND rr.source = 'landed' AND rr.verdict = 'contest' "
            f"AND rr.act = 'drop' AND s.status = 'proposed'",
            tuple(rulings)).fetchall():
        write_state(conn, "statements", r["ref"],
                    "UPDATE statements SET status = 'dropped' "
                    "WHERE id = ? AND status = 'proposed'", (r["ref"],))


def dropped_items(conn: sqlite3.Connection) -> set[str]:
    """The items the principal dropped (frame 357, pass 2)."""
    return {r[0] for r in conn.execute(
        "SELECT id FROM items WHERE approval = 'dropped'")}


def _item_drops(conn: sqlite3.Connection, ruling_id: str | None,
                per_item: dict) -> set[str]:
    """The items that ruling `ruling_id` contests with the act `drop`.

    The act is on the Liaison's rows of the ruling, because `per_item`
    holds the verdict only. A verdict from the seat with no ruling row has
    no act, so it drops nothing. Only a request item ends, by the rule that
    makes its page line a request line. Review p2 of frame 357, finding 1:
    a drop ended the description `how_it_works`."""
    contested = [r for r, v in per_item.items() if v == "contest"]
    if not ruling_id or not contested:
        return set()
    marks = ",".join("?" * len(contested))
    return {r["ref"] for r in conn.execute(
        f"SELECT DISTINCT rr.ref FROM ruled_refs rr JOIN items i "
        f"ON i.id = rr.ref WHERE rr.ruling_id = ? AND rr.source != 'landed' "
        f"AND rr.verdict = 'contest' AND rr.act = 'drop' "
        f"AND rr.ref IN ({marks})", (ruling_id, *contested))
        if _is_request_item(conn, r["ref"])}


# The words beside a row that holds his objection (ruled: Roman, 2026-11-02
# 11:43, frame 357, shape B of `plans/design-drop-observed-row-2026-11-02.md`).
NOT_MINE = "you said: not mine"


def _team_row(conn: sqlite3.Connection, ref: str) -> bool:
    """Whether `ref` is a row the team wrote and no request owns: a
    description, an account row, a constraint or a glossary term. A
    statement and a request item have their own end, `dropped`."""
    from ..core.db import tables_of

    if not isinstance(ref, str) or not ref:
        return False
    if tables_of(conn, ref, among=["constraints", "glossary_terms"]):
        return True
    from ..core.runner import _is_description

    # The ruling covers a row observed from the code only. His own request,
    # delivered or not, keeps the contest path (review p3 of frame 357, H1).
    item = conn.execute(
        "SELECT i.approval, p.provenance FROM items i LEFT JOIN "
        "item_provenance p ON p.id = i.id WHERE i.id = ?", (ref,)).fetchone()
    return (item is not None and item["approval"] != "dropped"
            and (item["provenance"] == "observed"
                 or _is_description(conn, ref)))


def principal_objects(conn: sqlite3.Connection, ref: str) -> bool:
    """Whether his newest ruling on the team's row `ref` drops it.

    The drop is his objection on file, and the row stays the team's record
    of the code. No seat argues with him and no page asks him again. A later
    plain approve takes the objection back, by `grant` (ruled: Roman,
    2026-11-02 11:43, frame 357, shape B)."""
    return _team_row(conn, ref) and granted(conn, ref, "drop")


def _row_objections(conn: sqlite3.Connection, ruling_id: str | None,
                    per_item: dict) -> set[str]:
    """The team's rows that ruling `ruling_id` contests with the act `drop`.

    The shape of `_item_drops`: the act is on the Liaison's rows of the
    ruling. Dry1's r_m147 dropped 15 constraints and `how_it_works`. The
    description then looped to quarantine through three defends and three
    clarifies (frame 357; `plans/dry1-turn17-read-2026-11-02.md`)."""
    contested = [r for r, v in per_item.items() if v == "contest"]
    if not ruling_id or not contested:
        return set()
    marks = ",".join("?" * len(contested))
    return {r["ref"] for r in conn.execute(
        f"SELECT DISTINCT rr.ref FROM ruled_refs rr WHERE rr.ruling_id = ? "
        f"AND rr.source != 'landed' AND rr.verdict = 'contest' "
        f"AND rr.act = 'drop' AND rr.ref IN ({marks})",
        (ruling_id, *contested)) if _team_row(conn, r["ref"])}


def objected_rows(conn: sqlite3.Connection) -> list[str]:
    """The team's rows that hold his objection now, in the order of his
    rulings."""
    refs = dict.fromkeys(r["ref"] for r in conn.execute(
        "SELECT rr.ref FROM ruled_refs rr JOIN rulings u ON u.id = rr.ruling_id "
        "WHERE u.status = 'landed' AND rr.act = 'drop' ORDER BY rr.rowid"))
    return [r for r in refs if principal_objects(conn, r)]


def statement_drop(conn: sqlite3.Connection, sid: str) -> str | None:
    """The newest landed ruling that dropped statement `sid`, when `sid` is
    `dropped`, else None. A later ruling does not hide it, because the end
    status holds (frame 357)."""
    r = conn.execute(
        "SELECT rr.ruling_id FROM ruled_refs rr "
        "JOIN rulings u ON u.id = rr.ruling_id "
        "JOIN statements s ON s.id = rr.ref "
        "WHERE rr.ref = ? AND s.status = 'dropped' AND u.status = 'landed' "
        "AND rr.source = 'landed' AND rr.verdict = 'contest' "
        "AND rr.act = 'drop' ORDER BY u.rowid DESC, rr.rowid DESC LIMIT 1",
        (sid,)).fetchone()
    return r["ruling_id"] if r is not None else None


def _insert_keypress_ruling(conn: sqlite3.Connection, ask: Ask, msg_id: str,
                            per_item: dict, said: str, *,
                            held: tuple = ()) -> None:
    """The landed `rulings` row of a verdict from the seat, and its
    `ruled_refs` rows. The verdict is his own act and not a reading, so the
    rows carry the source `keypress` (the seam design, 1.3, caller 2).

    A ref that no table holds gets no row here, and the verdict lands. A
    refusal at this door would lose his answer. A ledger note can name a
    ruling that is gone, and `land` adds that ref (frame 316's m191)."""
    rid = f"r_{msg_id}"
    conn.execute(
        "INSERT OR IGNORE INTO rulings (id, ask_id, per_item, words, "
        "status, verdict_id, texts) VALUES (?, ?, ?, ?, 'landed', ?, ?)",
        (rid, ask.message_id, json.dumps(per_item), said, msg_id,
         json.dumps(contested_texts(conn, per_item))))
    _insert_keypress_rows(conn, rid, ask, msg_id, per_item, said, held=held)


def _insert_keypress_rows(conn: sqlite3.Connection, rid: str, ask: Ask,
                          msg_id: str, per_item: dict, said: str, *,
                          shared: bool = False, held: tuple = ()) -> None:
    """The `ruled_refs` rows of a verdict from the seat, under ruling `rid`.

    `shared` says that the Liaison's reading has rows under `rid` too. A
    keypress row then hashes its own key, so the reading's row on the same
    ref does not hide it."""
    from ..core.db import ruled_ref_id

    rows = ruling_rows(conn, rid, getattr(ask, "order", None), per_item,
                       words=said, source="keypress",
                       words_from=msg_id if said else None, unheld="skip",
                       held=held)
    if shared:
        for row in rows:
            row["id"] = ruled_ref_id(rid, f"keypress:{row['ref']}")
    # A skipped ref is a fault on file, so his verdict on it stays visible
    # (the review of pass 1, finding 2; composition.md, no work stays
    # invisible).
    record_unheld(conn, rid, [r for r in per_item if r not in
                              {row["ref"] for row in rows}], "principal.land")
    insert_ruling_rows(conn, rows)


def _insert_landed_rows(conn: sqlite3.Connection, rid: str, ask: Ask,
                        msg_id: str, verdict: dict, moved: dict, said: str
                        ) -> None:
    """The `landed` rows of ruling `rid`: the per-row verdict that `land`
    computed, one row per ref, which `verdict_for` reads (fact F1).

    Each row names the row it derives from: the keypress row on the ref,
    else the reading's row. A ref that `land` moved to its batch derives
    from the row of the moved key. When the reading's row on the same ref
    has the same verdict, the landed row carries its act, target and words.
    So `grant` reads the newest row and takes back no act of the reading
    (law 11). A ref that no table holds keeps its row, as the config map
    kept it, because the relay carries it to its desk."""
    from ..core.db import ruled_ref_id

    rows = ruling_rows(conn, rid, getattr(ask, "order", None), verdict,
                       words=said, source="landed",
                       words_from=msg_id if said else None, unheld="keep")
    extra: list[dict] = []
    spread: set[str] = set()
    for row in rows:
        row["id"] = ruled_ref_id(rid, f"landed:{row['ref']}")
        origin = moved.get(row["ref"], row["ref"])
        found = conn.execute(
            "SELECT * FROM ruled_refs WHERE ruling_id = ? AND ref = ? "
            "AND source != 'landed' ORDER BY source = 'keypress' DESC, "
            "rowid DESC", (rid, origin)).fetchall()
        row["derived_from"] = found[0]["id"] if found else None
        read = next((r for r in found if r["source"] != "keypress"
                     and origin == row["ref"]
                     and r["verdict"] == row["verdict"]), None)
        if read is not None:
            for col in ("act", "target_kind", "target", "words", "words_from",
                        "line"):
                if read[col] is not None and read[col] != "":
                    row[col] = read[col]
        # One exclude lands per path, so each further path of the reading
        # lands its own row. Every other act keeps one row per ref (frame
        # 345, pass 7b).
        if (read is not None and read["act"] == "exclude"
                and row["ref"] not in spread):
            spread.add(row["ref"])
            paths = [r for r in reversed(found) if r["source"] == read["source"]
                     and r["verdict"] == read["verdict"]
                     and r["act"] == "exclude" and r["target"]
                     and r["target"] != read["target"]]
            for path in {r["target"]: r for r in paths}.values():
                extra.append({**row, "id": f"{row['id']}~{path['target']}",
                              "target": path["target"],
                              "derived_from": path["id"]})
    insert_ruling_rows(conn, rows + extra)


def unheld_text(rid: str, ref: str) -> str:
    """The fault text of a ref that no table holds."""
    return (f"{ref}: no table holds this row, so ruling {rid} has no "
            f"ruled_refs row on it. The ruling's per_item keeps his verdict")


def record_unheld(conn: sqlite3.Connection, rid: str, refs: list[str],
                  call: str) -> None:
    """Insert one `faults` row for each ref of ruling `rid` that no table
    holds. The row comes from `api._stage_fault`, the one builder of a
    fault, and this door inserts it because `land` runs outside a session."""
    from types import SimpleNamespace

    from .api import _stage_fault

    ctx = SimpleNamespace(conn=conn, session_id="", role="system", writes=[])
    for ref in refs:
        _stage_fault(ctx, call, unheld_text(rid, ref), "fault")
    for _table, fid, row in ctx.writes:
        cols = ["id", *row]
        conn.execute(
            f"INSERT OR IGNORE INTO faults ({', '.join(cols)}) "
            f"VALUES ({', '.join('?' for _ in cols)})", [fid, *row.values()])


def _write_park(conn: sqlite3.Connection, item: str, kind: str, by: str,
                cause: str, seq: int) -> None:
    """One `item_parks` row. The id hashes the item and the cause (law 14),
    so a replay of the same answer writes the same row."""
    import hashlib

    pid = "ip_" + hashlib.sha256(f"{item}|{cause}".encode()).hexdigest()[:10]
    conn.execute("INSERT OR IGNORE INTO item_parks (id, item_id, kind, by, "
                 "cause_id, seq) VALUES (?, ?, ?, ?, ?, ?)",
                 (pid, item, kind, by, cause, seq))


def _close_asks_about(conn: sqlite3.Connection, items: set[str],
                      msg_id: str, rows: set[str] = frozenset()) -> None:
    """Close each open ask to the principal whose refs reach only `items`,
    with a `closed:<ask>` row that names the verdict `msg_id`. A drop is
    the whole answer to such an ask (2.F.3).

    `rows` are the team's rows that he objects to. An ask whose every ref
    other than a read-back is one of them, or reaches only `items` and
    them, also closes, because his objection answers it (frame 357, shape
    B). A constraint reaches no item, so the item test alone missed it."""
    for r in conn.execute(
            "SELECT id, body_refs FROM messages WHERE status = 'open' "
            "AND to_role = 'principal' AND verb != 'converse'").fetchall():
        named = [x for x in json.loads(r["body_refs"] or "[]")
                 if isinstance(x, str) and not _is_reading(x)]
        reached = _reached(conn, [x for x in named if x not in rows])
        if r["id"].startswith(SHIFT_ASK) or not named:
            continue
        if not reached <= items | rows or not (reached or set(named) <= rows):
            continue
        mark_answered(conn, r["id"])
        conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                     (f"closed:{r['id']}", msg_id))


def _land_shift(conn: sqlite3.Connection, ask: Ask, answer: Answer,
                ruling_id: str | None) -> str:
    """
    Land the answer to the shift question: one `item_parks` row per item,
    and no `items` row. A drop closes every open ask of the item, with a
    `closed:<message>` row, and closes its open notes as overruled. The
    verdict carries no ref, so no relay wakes a seat (2.F.3).
    """
    msg_id = new_id("m", conn)
    seq = conn.execute(
        "SELECT COALESCE(MAX(seq), 0) + 1 n FROM messages").fetchone()["n"]
    thread = conn.execute("SELECT thread_id FROM messages WHERE id = ?",
                          (ask.message_id,)).fetchone()["thread_id"]
    conn.execute(
        "INSERT INTO messages (id, cause_id, cause_kind, thread_id, from_role, "
        "to_role, verb, body_refs, seq, status) VALUES (?, ?, 'message', ?, "
        "'principal', 'liaison', 'verdict', '[]', ?, 'answered')",
        (msg_id, ask.message_id, thread, seq))
    said = (answer.text or "").strip()
    for item, kind in (answer.per_item or {}).items():
        if kind not in ("park", "now", "drop") or not conn.execute(
                "SELECT 1 FROM items WHERE id = ?", (item,)).fetchone():
            continue
        _write_park(conn, item, kind, "shift", msg_id, seq)
        if kind != "drop":
            continue
        _close_asks_about(conn, {item}, msg_id)
        # The ledger branch of `land`, with the principal's words, and no
        # contest of the item: the drop is the item's whole answer.
        for r in conn.execute("SELECT id, about_ref, default_taken FROM ledger "
                              "WHERE status = 'open'").fetchall():
            if item not in _items_reached(conn, r["id"]):
                continue
            text = (f"overruled at signoff: {said or 'dropped'} "
                    f"(was assumed: {r['default_taken']})")
            conn.execute(
                "INSERT INTO decisions (id, author, text, refs, resolves_ledger) "
                "VALUES (?, 'principal', ?, ?, ?)",
                (new_id("d", conn), text, json.dumps([r["about_ref"]]), r["id"]))
            # A closed entry lifts the keys about it (frame 242).
            from ..core.db import write_state

            write_state(conn, "ledger", r["id"],
                        "UPDATE ledger SET status = 'resolved' WHERE id = ?",
                        (r["id"],))
    if said:
        conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                     (f"entry:{msg_id}", json.dumps(said)))
        record_entry(conn, msg_id, said)
    if ruling_id is None:
        conn.execute(
            "UPDATE rulings SET status = 'landed', verdict_id = ? "
            "WHERE ask_id = ? AND status = 'open'", (msg_id, ask.message_id))
        # The same door as `land`, so the shift page's rows are written too
        # (the seam design's review, finding 6).
        if conn.execute("SELECT 1 FROM rulings WHERE ask_id = ?",
                        (ask.message_id,)).fetchone() is None:
            _insert_keypress_ruling(conn, ask, msg_id,
                                    dict(answer.per_item or {}), said)
    return msg_id


def apply_rulings(conn: sqlite3.Connection) -> list[str]:
    """
    Land every ruling the Liaison has read and nothing has landed yet.

    Called after each session commits. The Liaison's `rulings.rule` stages
    a row; this turns the row into the verdict through `land`, the one door
    a ruling has. A ruling whose ask closed meanwhile is `stale`: the page
    the principal answered is gone, and a ruling on a page nobody sees lands
    nothing. Returns the verdict message ids created.
    """
    created: list[str] = []
    for r in conn.execute(
            "SELECT id, ask_id, per_item, words FROM rulings "
            "WHERE status = 'open' ORDER BY rowid").fetchall():
        ask_row = conn.execute(
            "SELECT id, verb, body_refs, body_text FROM messages WHERE id = ?",
            (r["ask_id"],)).fetchone()
        msg_id = None
        if ask_row is not None:
            ask = Ask(message_id=ask_row["id"], verb=ask_row["verb"],
                      refs=json.loads(ask_row["body_refs"] or "[]"))
            msg_id = land(conn, ask, Answer(
                verb="verdict", per_item=json.loads(r["per_item"] or "{}"),
                text=r["words"] or ""), ruling_id=r["id"])
        closed = conn.execute(
            "SELECT status FROM messages WHERE id = ?", (r["ask_id"],)).fetchone()
        landed = msg_id is not None or (closed and closed["status"] != "open")
        conn.execute(
            "UPDATE rulings SET status = ?, verdict_id = ? WHERE id = ?",
            ("landed" if landed else "stale", msg_id, r["id"]))
        if msg_id:
            created.append(msg_id)
    return created


def record_entry(conn: sqlite3.Connection, message_id: str, text: str) -> str:
    """
    Append the principal's words to the transcript mechanically.

    The transcript is the one un-interpreted thing in the system — it exists so
    later interpretations can be checked against something. Routing it through an
    interpreter to get there is self-defeating: asking a model to retype text
    verbatim creates a paraphrase risk with no upside, costs a turn, and in
    practice produced wrong ids and a fabricated second entry.

    Liaison still *owns* the artefact; the write is attributed to its session.
    It is authored by the system on the role's behalf, the way a receipt is.
    What Liaison keeps is the part that needs judgement: segmentation.
    """
    existing = conn.execute(
        "SELECT id FROM entries WHERE id = ?", (f"e_{message_id}",)).fetchone()
    if existing:
        return existing["id"]

    uid = f"e_{message_id}"
    nxt = conn.execute(
        "SELECT COALESCE(MAX(ts_order), 0) + 1 n FROM entries").fetchone()["n"]
    conn.execute(
        "INSERT INTO entries (id, author, text, ts_order) VALUES (?, 'principal', ?, ?)",
        (uid, text, nxt))
    conn.execute(
        "INSERT INTO artefact_versions(table_name, version) VALUES ('entries', 1) "
        "ON CONFLICT(table_name) DO UPDATE SET version = version + 1")
    return uid


def said(conn: sqlite3.Connection, message_id: str | None) -> str:
    """His words of the message `message_id`, or "" when none are kept.

    This is the one reader of his words of a message. The entry
    `e_<message>` comes first, because `record_entry` writes it on every
    path of `land`. The verdict path of `land` writes no `body_text`. On
    night 172 five pages quoted his clarify answers as "" (wall W7). A
    message with no entry, as a seeded one, falls back to `body_text`."""
    if not message_id:
        return ""
    text = entry_for(conn, message_id)
    if text:
        return text
    row = conn.execute("SELECT body_text FROM messages WHERE id = ?",
                       (message_id,)).fetchone()
    return (row["body_text"] if row else "") or ""


def verdict_for(conn: sqlite3.Connection, message_id: str) -> dict[str, str]:
    """His per-row verdict in the message `message_id`, ref to verdict word.

    The record is the newest landed ruling of the message in `ruled_refs`.
    Its `landed` rows are the verdict that `land` computed, and they come
    first. A ruling that `land` did not write, as a seeded one, gives its
    keypress rows, else its reading's rows on the refs that the verdict
    message carries. This is the one reader of a verdict (fact F1, law 11).

    `land` writes no `landed` row when nothing is left to relay. Then the
    verdict message carries no ref, so the reading's rows give nothing.

    An approve that closed a ledger row at the keypress is a taken default,
    and no owner has to hear it. A `reading:` ref is the read-back line,
    and no owner acts on it.
    """
    rows = ruled(conn, reply=message_id, every=True)
    chosen = ([r for r in rows if r["source"] == "landed"]
              or [r for r in rows if r["source"] == "keypress"])
    if not chosen and rows:
        msg = conn.execute("SELECT body_refs FROM messages WHERE id = ?",
                           (message_id,)).fetchone()
        carried = set(json.loads(msg["body_refs"] or "[]")) if msg else set()
        chosen = [r for r in rows if r["ref"] in carried]
    out: dict[str, str] = {}
    for r in chosen:
        if _is_reading(r["ref"]):
            continue
        if r["verdict"] == "approve" and conn.execute(
                "SELECT 1 FROM ledger WHERE id = ? AND status = 'resolved'",
                (r["ref"],)).fetchone():
            continue
        out[r["ref"]] = r["verdict"]
    return out


def chain_verdict(
        conn: sqlite3.Connection,
        message_id: str) -> tuple[str, dict[str, str], str | None] | None:
    """
    The principal's per-row ruling on a message's cause chain.

    Returns the message that carries the words, the per-row ruling, and the
    landed `rulings` row, or None when the chain carries no ruling at all.

    One walk for two readers: the runner builds a relay's `principal_verdict`
    from it, and `api._verdict_of` decides what a session may adopt. Both read
    the same chain, so both see the same ruling.

    Two hops, because a ruling lands in two shapes. A verdict that `land`
    lands has its `landed` rows, and `verdict_for` reads them. A reply the
    Liaison reads in the same session it relays lands only the `rulings`
    row, because `land` finds the ask already answered. Night 84
    (2026-09-17): the relay climbed one cause hop, found neither, and the
    Terminologist was told the ruling was in a field the message never had.

    A `rulings` row with an empty `per_item` is not a ruling. The onboard-only
    walk of clickI landed `r_m8` with `per_item='{}'` for a words-only reply,
    and silence is not consent.
    """
    seen: set[str] = set()
    mid = message_id
    while mid and mid not in seen:
        seen.add(mid)
        verdict = verdict_for(conn, mid)
        if verdict:
            row = conn.execute(
                "SELECT id FROM rulings WHERE verdict_id = ? AND status = 'landed' "
                "ORDER BY rowid DESC LIMIT 1", (mid,)).fetchone()
            return mid, verdict, (row["id"] if row else None)
        row = conn.execute(
            "SELECT id, reply_id, verdict_id FROM rulings "
            "WHERE status = 'landed' AND (ask_id = ? OR reply_id = ?) "
            "ORDER BY rowid DESC LIMIT 1", (mid, mid)).fetchone()
        # The per-row ruling is the record per ref (the seam design, 3.1).
        per_item = ({r["ref"]: r["verdict"] for r in ruled(conn, ruling=row["id"])}
                    if row else {})
        if per_item:
            said = row["reply_id"] or row["verdict_id"] or mid
            return said, per_item, row["id"]
        nxt = conn.execute(
            "SELECT cause_id FROM messages WHERE id = ?", (mid,)).fetchone()
        mid = nxt["cause_id"] if nxt else None
    return None


def entry_for(conn: sqlite3.Connection, message_id: str) -> str:
    """
    What the principal said, from the table that owns it.

    This read a `config` key, `entry:<message_id>`, written by exactly one of
    the two paths that record an entry. The reply path above writes it.
    `talk.open_with` -- which is intake, the CLI and the TUI -- writes the
    `entries` row and not the key, so **the first thing anybody typed was
    invisible and every follow-up was visible.**

    What that looked like from outside: Liaison woken to segment a requirement,
    shown three empty lists and no sentence, answering "Hello! What would you
    like to build?" -- the correct response to an empty message. It read as a
    role choosing to chat, and it took `L1-LI-segment` and
    `L1-LI-no-report-no-question` to 0/5.

    `record_entry` names the row `e_<message_id>`, so the join needs nothing
    stored. One fact in one place: the config key is still read as a fallback
    for databases written before this, and it is no longer the authority.
    """
    row = conn.execute(
        "SELECT text FROM entries WHERE id = ?", (f"e_{message_id}",)).fetchone()
    if row is not None and row["text"]:
        return row["text"]

    legacy = conn.execute(
        "SELECT value FROM config WHERE key = ?", (f"entry:{message_id}",)).fetchone()
    return json.loads(legacy["value"]) if legacy else ""
