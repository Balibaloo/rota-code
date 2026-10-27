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

from ..core.runner import new_id


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
    asks = pending_asks(conn)
    if asks:
        head = ("Waiting on you." if len(asks) == 1
                else f"Waiting on you: {len(asks)} things. The first is:")
        return head + chr(10) + asks[0].rendered

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

    out: list[str] = []
    if merged:
        out.append(f"Done: {merged} change{'s' if merged > 1 else ''} built, "
                   "tested and merged.")
    # A parked row is shown quietly, as a count that asks nothing (ruled:
    # Roman, 2026-10-11 15:00, frame 204's design, section 4).
    # Each kind has its own words: a `scope` row is not a choice (frame
    # 316's review 2, finding 2). `ledger.list(shipped=...)` shows the rows.
    kinds = dict(conn.execute("SELECT kind, COUNT(*) FROM ledger "
                              "WHERE status = 'parked' GROUP BY kind").fetchall())
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
        carry = "They carry" if merged > 1 else "It carries"
        out[-1] += f" {carry} {listed}. Ask me to show them."
    # A cold cockpit sees the cycle the walk printed, read from the rows
    # (ruled: Roman, 2026-09-24, an alert first). The line goes under what
    # is stuck.
    from ..core.cycles import cycle as _cycle
    try:
        looping = _cycle(conn)
    except Exception:                   # noqa: BLE001 -- a state page never fails on an alert
        looping = None

    def gave_up_on(keys):
        return ", ".join(
            f"{k.split('|')[1].replace('tick:', '')} for "
            f"{k.split('|')[2] or 'the whole project'}" for k in keys)

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
    capped = [b for b in held if not keyed[b]]

    # The line shows only while no ask is open: before the Liaison writes
    # the park ask, or when its wake is quarantined. No gate is open then,
    # so the line names no contest (observed: frame 87's review of b23d17b,
    # 2026-09-30). The ask comes next only while `park_ask` owes it and its
    # wake is live. A quarantined wake writes nothing (observed: frame 87's
    # review of 4a0ab5c, 2026-09-30).
    from ..core.predicates import park_ask as _park_ask
    from ..core.scheduler import tick_key

    coming = {w.refs[1] for w in _park_ask(conn) if not conn.execute(
        "SELECT 1 FROM tick_attempts WHERE tick_key = ? AND quarantined = 1",
        (tick_key(w),)).fetchone()}
    from ..core.scheduler import (park_ask_id, park_message_rests, park_reds,
                                  park_ruling)

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
                return (f"Stuck: {b} stops here. It breaks {', '.join(files)}. "
                        "A new commit on the change starts it again.")
            ruled = park_ruling(conn, mid) or {}
            if any(v != "approve" for v in ruled.values()):
                return (f"Stuck: {b} is parked. The team rewrites the lines you "
                        "corrected, and I show you the page again after that.")
            return (f"Stuck: {b} stops here. You approved its checks as they "
                    f"stand, and {len(own)} of them still fail. A new commit "
                    "on the change starts it again.")
        return (f"Stuck: {b} is parked. The team gave up on: {gave_up_on(keys)}."
                + (" The other changes go on." if running or pending else "")
                + " A new commit on the change starts it again."
                + (" I ask you about it next." if b in coming else ""))

    parked_lines = [parked_line(b, keys) for b, keys in keyed.items() if keys]
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
    gave_up = [r["tick_key"] for r in conn.execute(
        "SELECT tick_key FROM tick_attempts WHERE quarantined = 1 "
        "AND tick_key NOT LIKE '%tick:constraint_zero%'")
        if r["tick_key"] not in parked_keys]
    if gave_up:
        out.append(f"Stuck. The team gave up on: {gave_up_on(gave_up)}. "
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
            "SELECT COUNT(DISTINCT t.test_id) FROM test_runs t "
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
    """The first `E   ` line of a pytest run, without its marker. When that
    line is a traceback frame, the last `E   ` line."""
    # pytest cuts the `FAILED` line's reason to the terminal width: night
    # 132's run tr248 ends `assert F...` (frame 142's design review, finding 5).
    lines = [x[1:].strip() for x in (output or "").splitlines() if x.startswith("E   ")]
    if not lines:
        return ""
    # A collection error puts the traceback frame first and the error last.
    # Night 168's m53 showed him only the file and the line (frame 336).
    line = lines[-1] if re.match(r'File ".*", line \d+', lines[0]) else lines[0]
    # The line's own period goes, because check_line's tail adds one.
    return line.removesuffix(".")


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
    run = conn.execute("SELECT result, output FROM test_runs WHERE test_id = ? "
                       "AND batch_id = (SELECT batch_id FROM tests WHERE id = test_runs.test_id) "
                       "ORDER BY rowid DESC LIMIT 1", (test_id,)).fetchone()
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
    r = conn.execute(sql + " ORDER BY r.ruling_seq DESC LIMIT 1",
                     tuple(args)).fetchone()
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

    The rows come from `ruled_refs_live`, one row per ruling and ref (the
    seam design, pass 1). `words` stays the whole reply in this pass, so
    each reader gets the answer it got from `per_item`.
    """
    r = conn.execute(
        "SELECT ruling_id, verdict, reply_words, old_text FROM ruled_refs_live "
        "WHERE ref = ? AND ruling_status != 'stale' "
        "ORDER BY ruling_seq DESC LIMIT 1", (ref,)).fetchone()
    if r is None:
        return None
    return {"id": r["ruling_id"], "verdict": r["verdict"],
            "words": r["reply_words"] or "", "text": r["old_text"]}


def ruled(conn: sqlite3.Connection, refs=None, *, reply: str | None = None,
          ruling: str | None = None, ask: str | None = None,
          landed: bool = True, newest: bool = False,
          item: str | None = None) -> list[sqlite3.Row]:
    """The rows of `ruled_refs_live` that a reader asks for, oldest first.

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
    if newest:
        last = {r["ref"]: r for r in rows}
        rows = [r for r in rows if last[r["ref"]] is r]
    return rows


def ruled_words(conn: sqlite3.Connection, refs, *, item: str | None = None,
                skip=frozenset()) -> list[str]:
    """His landed words on any of `refs`, one text per ruling, oldest first.

    The words are the rows' own. A ruling that also rules a ref of `skip`
    gives none. One reader serves the criteria push, the slicing push, the
    Developer's start window and the removal door (frame 322, proposal
    lines 1 and 3).
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
RULED_ACTS = ("drop", "keep", "rewrite", "add", "remove")
TARGET_KINDS = ("row", "check", "sentence", "identifier", "source_line",
                "path", "request")
# The ref of the read-back line of one reply (the seam design, 2.3).
READING_REF = "reading:"


def ruled_ref_home(conn: sqlite3.Connection, ref: str) -> str | None:
    """The table that holds `ref`, or None.

    `_table_of_ref` knows the ledger's homes. A page also numbers a batch, a
    ledger row and a code line, and the read-back line names a reply."""
    from .api import _table_of_ref, guess_item

    if not isinstance(ref, str) or not ref:
        return None
    if ref.startswith(READING_REF):
        return "messages" if conn.execute(
            "SELECT 1 FROM messages WHERE id = ?",
            (ref[len(READING_REF):],)).fetchone() else None
    item = guess_item(ref)
    if item is not None:
        return "items" if conn.execute(
            "SELECT 1 FROM items WHERE id = ?", (item,)).fetchone() else None
    table = _table_of_ref(conn, ref)
    if table is not None:
        return table
    return next((t for t in RULED_HOMES if conn.execute(
        f"SELECT 1 FROM {t} WHERE id = ?", (ref,)).fetchone()), None)


# The tables beside `LEDGER_HOMES` that a page or a question names. A ledger
# note can be about a ruling, and a question can be about a decision (frame
# 316's m191, frame 306's clarify about).
RULED_HOMES = ("batches", "ledger", "entries", "decisions", "rulings",
               "findings", "verdicts", "references_")


def ruling_rows(conn: sqlite3.Connection, ruling_id: str, page: list | None,
                reading: dict, *, words: str = "", source: str = "reading",
                words_from: str | None = None,
                unheld: str = "refuse") -> list[dict]:
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
    """
    from ..core.db import ruled_ref_id
    from .api import guess_item

    if source not in ("reading", "keypress", "backfill"):
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
        table = ruled_ref_home(conn, ref)
        if table is None and unheld == "skip":
            continue
        if table is None:
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
        if table != "messages" and guess_item(ref) is None and any(
                c[1] == "version"
                for c in conn.execute(f"PRAGMA table_info({table})")):
            got = conn.execute(f"SELECT version FROM {table} WHERE id = ?",
                               (ref,)).fetchone()
            version = got["version"] if got else None
        rows.append({
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
            "ref_version": version, "source": source})
    return rows


def insert_ruling_rows(conn: sqlite3.Connection, rows: list[dict]) -> None:
    """Insert the rows `ruling_rows` built. A replay of the same ruling
    builds the same ids, so the insert ignores a row on file."""
    for row in rows:
        cols = list(row)
        conn.execute(
            f"INSERT OR IGNORE INTO ruled_refs ({', '.join(cols)}) "
            f"VALUES ({', '.join('?' for _ in cols)})", [row[c] for c in cols])


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


def request_of(conn: sqlite3.Connection, item: str) -> str | None:
    """The entry of the request an item belongs to, or None when the item
    cites no statement, such as the account or an observed behaviour."""
    best = None
    for r in conn.execute(
            "SELECT r.target FROM refs r WHERE r.src_table = 'items' "
            "AND r.src_id = ? AND r.kind = 'statement'", (item,)):
        root = _root_statement(conn, r["target"])
        row = conn.execute(
            "SELECT e.id, e.ts_order FROM statements s JOIN entries e "
            "ON e.id = s.span_entry WHERE s.id = ?", (root,)).fetchone()
        if row is not None and (best is None or row["ts_order"] < best[1]):
            best = (row["id"], row["ts_order"])
    return best[0] if best else None


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
    from ..core.scheduler import aside_items, not_described

    cur = cur if cur is not None else current_request(conn)
    if not cur:
        return []
    here = set(cur["entries"])
    at = min(_entry_order(conn, e) for e in cur["entries"])
    aside = aside_items(conn)
    out: list[tuple[int, str]] = []
    for r in conn.execute(
            "SELECT i.id FROM items i WHERE i.kind = 'in_scope' "
            "AND i.approval IN ('approved', 'contested', 'draft')"
            + not_described(conn, "i.id") + " ORDER BY i.id"):
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
    from ..core.runner import _is_description
    from ..core.scheduler import aside_items

    aside = aside_items(conn)
    best = None
    for item in _reached(conn, refs):
        # The account belongs to no request, as in `off_page`. A description
        # citing s3 put the confirm item off its own page (the review of
        # e406e976, finding 1).
        if item in aside or _is_description(conn, item):
            continue
        entry = request_of(conn, item)
        if entry is None:
            continue
        order = _entry_order(conn, entry)
        if best is None or order > best[1]:
            best = (entry, order)
    return best[0] if best else None


def off_page(conn: sqlite3.Connection, refs: list) -> set[str]:
    """
    The refs that a page of one request does not number (2.F.7). A row
    whose items are all set aside, or all of another request than the page's,
    leaves the page. A note about a delivered item of an earlier request
    stays, so a ruling closes it. The send door drops the same rows, so a
    page's refs and its numbered rows are one set.
    """
    from ..core.runner import _is_description
    from ..core.scheduler import aside_items

    aside = aside_items(conn)
    # Requests are told apart by their boundaries. A run with no request
    # message has one request, and every open item keeps its line (frame
    # 190's design, 2.F, amendment 2).
    req = page_request(conn, refs) if current_request(conn, unread=False) else None
    out: set[str] = set()
    for ref in refs or []:
        if not isinstance(ref, str):
            continue
        items = _items_reached(conn, ref)
        if not items:
            continue
        if all(i in aside for i in items):
            out.add(ref)
            continue
        if req is None:
            continue
        # The account belongs to no request, whatever statement it cites.
        # Night 133's m283 dropped `defines_commands_and_options`, which
        # cites s1, and each sign-off submitted it again (the review of
        # 61a0f41d, finding 2).
        if all(_is_description(conn, i) for i in items):
            continue
        others = [request_of(conn, i) for i in items]
        if not all(e is not None and e != req for e in others):
            continue
        is_note = conn.execute("SELECT 1 FROM ledger WHERE id = ?", (ref,)).fetchone()
        if is_note and all(_delivered(conn, i) for i in items):
            continue
        out.add(ref)
    return out


def request_rows(conn: sqlite3.Connection, refs: list[str]) -> list[str]:
    """
    The request's own rows for a page: each item, then its criteria by id.

    The items are the ones the refs reach. When the refs reach none, they
    are every open request. When no request is open, the row is the account,
    which renders under its own heading.
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
        if not isinstance(ref, str) or ref in off:
            continue
        for item in _items_reached(conn, ref):
            if item not in items and item not in held and _is_request_item(conn, item):
                items.append(item)
    if not items:
        aside = aside_items(conn) | held
        items = [i for i in open_requests(conn) if i not in aside]
        cur = current_request(conn, unread=False)
        mine = [i for i in items if cur and request_of(conn, i) in cur["entries"]]
        items = mine or items
    if not items:
        account = conn.execute(
            "SELECT 1 FROM items WHERE id = 'how_it_works'").fetchone()
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
                   batch: str | None, keys: list[str]) -> int | None:
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
    for key in sorted(keys or []):
        if "|tick:tests_missing|" not in key:
            continue
        keyed = (key.split("|", 2) + [""])[2].split(",")
        if set(keyed) & set(batches):
            row = conn.execute("SELECT attempts FROM tick_attempts WHERE tick_key = ?",
                               (key,)).fetchone()
            return row["attempts"] if row else 0
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
                  park: bool = False, stalled: list[str] | None = None) -> list[int]:
    """
    Render the request's rows of a page first: the principal's words, each
    item, its code line, and its criteria with their `check:` lines. Append
    to `out` and `order`, and return the line numbers of the items.

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
            tries = None if park else _gave_up_tries(conn, r, batch, stalled or [])
            if tries is None:
                out.append("     check: none yet.")
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
    keys: list[str] = []
    for r in conn.execute(
            "SELECT tick_key FROM tick_attempts WHERE quarantined = 1 "
            "AND tick_key NOT LIKE '%tick:constraint_zero%' ORDER BY tick_key"):
        keyed = (r["tick_key"].split("|", 2) + ["", ""])[2].split(",")
        if set(keyed) & set(batches):
            keys.append(r["tick_key"])
    return keys


def _stalled_words(conn: sqlite3.Connection, keys: list[str]) -> str:
    """'the team could not write the tests after 3 attempts', one part per
    key, in the words of TICK_WORDS and never the tick's name."""
    return "; ".join(f"{_tick_words(kind)} after {_tries(n)}"
                     for kind, n in _stuck_ticks(conn, "", keys))


def _stuck_ticks(conn: sqlite3.Connection, batch: str,
                 keys: list[str] | None = None) -> list[tuple[str, int]]:
    """
    The batch's quarantined ticks as (kind, attempts), from `tick_attempts`.

    `keys` names the keys of a page's wake. None reads the live keys of the
    batch. The stopped page and the shift page both read this, so the two
    pages cannot disagree. Night 160's m45 said "stopped work" on a green
    change, and m53 then said "nothing from you" (frame 312's provenance).
    """
    out = []
    for key in (_stalled_keys(conn, [batch]) if keys is None else keys):
        row = conn.execute("SELECT attempts FROM tick_attempts WHERE tick_key = ?",
                           (key,)).fetchone()
        kind = (key.split("|", 2) + ["", ""])[1].replace("tick:", "")
        out.append((kind, row["attempts"] if row else 0))
    return out


# A tick's kind as the principal reads it. The page contract shows his
# words, never rota's names (frame 312, review 1, finding 1).
TICK_WORDS = {
    "review": "the review gave no verdict",
    "tests_failing": "the tests still fail",
    "tests_missing": "the team could not write the tests",
    "verdict_failed": "the review failed the change",
    "do:preempt": "the change was set aside",
    "do:park": "the change was stopped",
    "challenge": "a challenge got no answer",
    "contested": "a contested line got no answer",
    "quarantined": "the team could not report a stopped step",
    "agenda": "a question to you got no answer",
    "constraint_zero": "the team could not read the code first",
    "batch_start": "the change could not start",
    "touch_strayed": "the change went outside the files it expected",
}


def _tick_words(kind: str) -> str:
    return TICK_WORDS.get(kind, "a step of the team")


def _tries(n: int) -> str:
    return f"{n} attempt{'' if n == 1 else 's'}"


def _review_only(ticks: list[tuple[str, int]]) -> bool:
    """True when every stuck tick is a review. The review fires only on a
    green harness at the head, so its tests passed at its last attempt."""
    return bool(ticks) and all(kind == "review" for kind, _ in ticks)


TEAM_NOTES =("The team's notes. A seat wrote each of these where your words "
              "were silent. They are not your request.")


def _park_page(conn: sqlite3.Connection, batch: str,
               refs: list[str]) -> tuple[str, list[str]]:
    """The park message as the principal reads it: a page with the item and
    its criteria, or a note when the batch is its one ref."""
    from ..core.scheduler import failing_attempt, park_reds

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
        "AND criterion_id IS NOT NULL", (batch,)).fetchall()
    tries = failing_attempt(conn, batch)
    out.append(f"This change stopped. The team tried {tries} "
               f"time{'' if tries == 1 else 's'}, and {len(own)} of its "
               f"{len(checks)} checks still fail.")
    request_block(conn, refs, order, out, batch=batch, park=True)
    head = conn.execute("SELECT head_commit FROM batches WHERE id = ?",
                        (batch,)).fetchone()
    at_head = [r for r in own if head is None or head["head_commit"] is None
               or r.get("commit_sha") in (None, head["head_commit"])] or own
    last = [f"{r['path'] or r['test_id']} failed: {_failure_line(r['output']) or 'no reason shown'}."
            for r in at_head[:2]]
    if last:
        out.append("The last attempt: " + " ".join(last))
    out.append("Reply 'ok' if every line says what you want. The team then "
               "stops here and tells you.")
    out.append("Name a line to correct only that line. Ask, if something here "
               "is unclear.")
    return chr(10).join(out), order


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
        "SELECT result FROM test_runs WHERE batch_id = ? AND rowid IN "
        "(SELECT MAX(rowid) FROM test_runs WHERE batch_id = ? GROUP BY test_id)",
        (batch["id"], batch["id"])).fetchall()
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
    from .api import _LINE_REF, _SENTENCE, _ref_lines

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
        "SELECT body_text FROM messages WHERE id = ? AND cause_id = ? "
        "AND from_role = 'principal'",
        (reply_id.group(1) if reply_id else None, ask_id)).fetchone()
    lines: set[int] = set()
    # By sentence, as the line reader reads: a bare "3 is wrong" counts at
    # a sentence start (frame 305, review 1, finding 1).
    for sentence in _SENTENCE.split((reply and reply["body_text"]) or ""):
        for ref in _LINE_REF.finditer(sentence):
            lines |= _ref_lines(ref)
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
    return (f"{back}\n{page}" if back else page), order


def _quiet_line(conn: sqlite3.Connection, refs: list[str]) -> str:
    """
    The count line for ledger rows of kind `other`: the count and the seats.

    The line names no row's words. A seat's account of its own state reached
    him as his assumption on night 165's m172, and he asked three times to
    remove it (frame 325's provenance, section 1).
    """
    seats: list[str] = []
    for ref in refs:
        row = conn.execute("SELECT author FROM ledger WHERE id = ?",
                           (ref,)).fetchone()
        seat = "the " + str(row[0] if row else "team").replace("_", " ").title()
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

    refs = list(refs or [])
    # A page is about one request. A row of an item set aside, or of another
    # request than the page's, is no line here (frame 193's design, 2.F.7).
    if verb == "present":
        off = off_page(conn, refs)
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
        in_block |= {r for r in refs if isinstance(r, str) and r.startswith("guess:")
                     and r[len("guess:"):] in in_block}
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
            out.append(f"  {len(order)}. {shown}")

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
    if verb == "present" and keys and touches:
        # A quarantined batch is no plan any more. Night 136's m96 opened
        # "Before I build this" on a batch the Tester had given up on
        # (frame 190's design, 2.F, amendment 6). A review with no verdict
        # is no code fault. Night 160's m45 said "stopped work" on a change
        # whose 35 tests passed (frame 312's provenance, section 3).
        ticks = _stuck_ticks(conn, batches[0], keys)
        if _review_only(ticks):
            out.append(f"The review of this change stopped after "
                       f"{_tries(max(n for _, n in ticks))} with no verdict. "
                       "Its tests passed at the review's last attempt.")
        else:
            out.append("The team stopped work on this change.")
        asked = request_block(conn, refs, order, out, batch=batches[0],
                              stalled=keys)
        numbered(does + account)
        out.append(f"The team gave up: {_stalled_words(conn, keys)}.")
        out.append("The team expects to touch:")
        numbered(touches)
        out.append("Reply 'ok' if every line says what you want. Name a line "
                   "to correct only that line. Ask, if something here is "
                   "unclear." + _name_request(asked))
    elif verb == "present" and touches:
        out.append("Before I build this, here is what I expect to touch.")
        asked = request_block(conn, refs, order, out, batch=batches[0],
                              stalled=keys)
        numbered(does + account)
        out.append("The team expects to touch:")
        numbered(touches)
        if zero:
            out.append("  Some of that code has not been read yet. I cannot say "
                       "what a change there might break.")
        out.append("This is a prediction, not a promise. Reply 'ok' to go "
                   "ahead. Reply with words if something concerns you."
                   + _name_request(asked))
    elif verb == "present" and zero and not (said or account or described
                                             or does or does_not or in_block):
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
                              code=code_stamp(conn, ask_id), stalled=keys)
        guessed = [n for n, r in enumerate(order, 1) if r.startswith("guess:")]
        if account:
            out.append("What we are building:")
            numbered(account)
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
        out.append("Reply in your own words. 'ok' approves all of this and "
                   "starts building. Name a line to correct only that line. "
                   "Ask, if something here is unclear." + _name_request(asked)
                   + _name_guess(guessed))
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
    if t["commitments"]:
        parts.append("commitments: " + ", ".join(
            f"{c['headline']} (bound to {c['bound_to']})"
            for c in t["commitments"]))
    return "; ".join(parts)


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


def _page_order(conn: sqlite3.Connection, ask: Ask) -> list[str]:
    """The rows the page numbers, as `rulings_rule` reads them. A ruling
    from `apply_rulings` carries no order, and the line numbers of the
    words need one."""
    # This order can differ from the order the Liaison ruled on. The window
    # is an earlier open ruling that lands first in the same `apply_rulings`
    # loop and moves a row. The batch's line then shifts, and `land` drops
    # the contest with no error (frame 255, review 1, finding 2). Night 150
    # counts it before a frame stages the refs on the `rulings` row.
    row = conn.execute("SELECT body_text FROM messages WHERE id = ?",
                       (ask.message_id,)).fetchone()
    return render_page(conn, ask.verb, list(ask.refs),
                       row["body_text"] if row else None,
                       ask_id=ask.message_id)[1]


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

    closed = conn.execute(
        "UPDATE messages SET status = 'answered' "
        "WHERE id = ? AND status = 'open'", (ask.message_id,)).rowcount
    if not closed:
        return None
    # A landed answer to a stopped page lifts the quarantined Developer start
    # key it shows, once, because the page closes here. The next Developer
    # reads his ruling. Night 163's m115 to m139 restarted the team only
    # through corrections he did not mean (frame 312, review w5, finding 2).
    for key in door_rows(conn, ask.message_id, "stalled"):
        if key.startswith("developer|tick:batch_start|"):
            conn.execute("DELETE FROM tick_attempts WHERE tick_key = ? "
                         "AND quarantined = 1", (key,))
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
    per_item = dict(answer.per_item or {})
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
            order = ask.order or (_page_order(conn, ask) if faulted else [])
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

                    order = ask.order or _page_order(conn, ask)
                    if not code_line_faulted(answer.text or "", order, key):
                        continue
                per_item[batch_id] = ruling
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
    closed_here: list[str] = []
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
                from ..core.runner import _is_description

                # The account belongs to no request, as in `off_page`. A
                # description cites the earliest request, so the skip lost
                # the contest of a note about `how_it_works` (frame 274's
                # review 1, finding 1).
                # The owner comes from the items the note reaches, not from
                # its `about_ref` alone. `request_of` reads an item id only,
                # so a note about `cr_1` had no owner, and night 161's m234
                # contested the merged confirm item's `cr_1` (frame 316,
                # `plans/frame316-provenance.md`, repair 1). A note that
                # reaches no item keeps the carrier.
                reached = _items_reached(conn, row["about_ref"])
                owners = {None if _is_description(conn, item)
                          else request_of(conn, item) for item in reached}
                elsewhere = bool(owners) and all(
                    o is not None and o != page_req for o in owners)
                if page_req is None or not elsewhere:
                    per_item[row["about_ref"]] = "contest"
        conn.execute(
            "INSERT INTO decisions (id, author, text, refs, resolves_ledger) "
            "VALUES (?, 'principal', ?, ?, ?)",
            (new_id("d", conn), text, json.dumps([row["about_ref"]]), ref))
        conn.execute("UPDATE ledger SET status = 'resolved' WHERE id = ?", (ref,))
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
    for ref, ruling in per_item.items():
        if ref in closed_here:
            continue
        state = {"approve": "approved", "contest": "contested",
                 "revise": "contested"}.get(ruling)
        if state is None:
            continue
        moved = conn.execute(
            "UPDATE items SET approval = ?, approval_ver = version "
            "WHERE id = ? AND approval IS NOT ?", (state, ref, state)).rowcount
        # An approval change is an exit from a quarantine. This raw write
        # skipped the lift, so night 147's approve left the contested tick
        # quarantined, and the walk's end said the team gave up (frame 240).
        # Frame 87 fixed the same shape in `boot.py`. The rowcount keeps frame
        # 80's rule: a same-value write revives nothing. Law 6.
        if moved:
            from ..core.db import Write, _lift_quarantines

            _lift_quarantines(conn, Write("items", ref, {"approval": state},
                                          op="update", amends=False), True)

    refs = [r for r in (list(per_item) if answer.per_item else ask.refs)
            if r not in closed_here]
    # A page whose every row closed at the keypress leaves nothing for an
    # owner to do. The verdict is the record and lands answered. Relayed,
    # it woke the Terminologist with a ruling on a done row; it adopted the
    # ledger id, was refused, logged the refusal as a new assumption, and
    # the agenda put that row to the principal: 36 rounds (tipsQ,
    # 2026-09-09). A ruling whose every line was a request approve off the
    # sign-off page leaves nothing either.
    approved_here = [r for r in closed_here if per_item.get(r) == "approve"]
    settled = (bool(answer.per_item) and not refs
               and len(approved_here) == len(closed_here))
    # A park page approved whole is the ceiling. The team stops here and the
    # parked line says so, so no Liaison session wakes on the verdict
    # (ruled: Roman, 2026-10-08, the park ask is a page with rows, point 5).
    from ..core.scheduler import park_ask_batch

    if (ask.verb == "present" and park_ask_batch(ask.message_id or "")
            and ask.refs and all(per_item.get(r) == "approve" for r in ask.refs)):
        settled = True
    conn.execute(
        "INSERT INTO messages (id, cause_id, cause_kind, thread_id, from_role, "
        "to_role, verb, body_refs, seq, status) "
        "VALUES (?, ?, 'message', ?, 'principal', 'liaison', ?, ?, ?, ?)",
        (msg_id, ask.message_id, thread, answer.verb, json.dumps(refs), seq,
         "answered" if settled else "open"),
    )

    # Per-item verdicts travel as refs; the ruling itself is recorded so
    # Liaison can relay it without re-asking. An approved row closed here is
    # not in it: a taken default needs no relay. A contested one stays: its
    # author has to hear the words.
    remaining = {r: v for r, v in per_item.items() if r not in approved_here}
    if remaining:
        conn.execute(
            "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
            (f"verdict:{msg_id}", json.dumps(remaining)),
        )
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
    if ruling_id is None:
        conn.execute(
            "UPDATE rulings SET status = 'landed', verdict_id = ? "
            "WHERE ask_id = ? AND status = 'open'", (msg_id, ask.message_id))
        on_file = conn.execute(
            "SELECT 1 FROM rulings WHERE ask_id = ?", (ask.message_id,)).fetchone()
        if on_file is None:
            _insert_keypress_ruling(conn, ask, msg_id, per_item,
                                    (answer.text or "").strip())
    return msg_id


def _insert_keypress_ruling(conn: sqlite3.Connection, ask: Ask, msg_id: str,
                            per_item: dict, said: str) -> None:
    """The landed `rulings` row of a verdict from the seat, and its
    `ruled_refs` rows. The verdict is his own act and not a reading, so the
    rows carry the source `keypress` (the seam design, 1.3, caller 2).

    A ref that no table holds gets no row here, and the verdict lands. A
    refusal at this door would lose his answer. A ledger note can name a
    ruling that is gone, and `land` adds that ref (frame 316's m191)."""
    rid = f"r_{msg_id}"
    rows = ruling_rows(conn, rid, getattr(ask, "order", None), per_item,
                       words=said, source="keypress",
                       words_from=msg_id if said else None, unheld="skip")
    # A skipped ref is a fault on file, so his verdict on it stays visible
    # (the review of pass 1, finding 2; composition.md, no work stays
    # invisible).
    record_unheld(conn, rid, [r for r in per_item if r not in
                              {row["ref"] for row in rows}], "principal.land")
    conn.execute(
        "INSERT OR IGNORE INTO rulings (id, ask_id, per_item, words, "
        "status, verdict_id, texts) VALUES (?, ?, ?, ?, 'landed', ?, ?)",
        (rid, ask.message_id, json.dumps(per_item), said, msg_id,
         json.dumps(contested_texts(conn, per_item))))
    insert_ruling_rows(conn, rows)


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
        for r in conn.execute(
                "SELECT id, body_refs FROM messages WHERE status = 'open' "
                "AND to_role = 'principal' AND verb != 'converse'").fetchall():
            reached = _reached(conn, json.loads(r["body_refs"] or "[]"))
            if r["id"].startswith(SHIFT_ASK) or not reached or not reached <= {item}:
                continue
            conn.execute("UPDATE messages SET status = 'answered' WHERE id = ?",
                         (r["id"],))
            conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                         (f"closed:{r['id']}", msg_id))
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
            conn.execute("UPDATE ledger SET status = 'resolved' WHERE id = ?",
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


def verdict_for(conn: sqlite3.Connection, message_id: str) -> dict[str, str]:
    row = conn.execute(
        "SELECT value FROM config WHERE key = ?", (f"verdict:{message_id}",)).fetchone()
    return json.loads(row["value"]) if row else {}


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

    Two records, because a ruling lands in two shapes. A verdict from the seat
    writes the `config` key `verdict:<id>`. A reply the Liaison reads in the
    same session it relays lands only the `rulings` row, because `land` finds
    the ask already answered. Night 84 (2026-09-17): the relay climbed one
    cause hop, found neither, and the Terminologist was told the ruling was in
    a field the message never had.

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
