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
    """
    return [
        Ask(message_id=r["id"], verb=r["verb"],
            refs=json.loads(r["body_refs"]),
            rendered=(page := render_page(conn, r["verb"],
                                          json.loads(r["body_refs"]),
                                          r["body_text"], ask_id=r["id"]))[0],
            order=page[1])
        for r in conn.execute(
            "SELECT id, verb, body_refs, body_text FROM messages "
            "WHERE status = 'open' AND to_role = 'principal' "
            "  AND verb != 'converse' ORDER BY seq")
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

    merged = count("SELECT COUNT(*) FROM batches WHERE status = 'merged'")
    running = count("SELECT COUNT(*) FROM batches WHERE status = 'running'")
    pending = count("SELECT COUNT(*) FROM batches WHERE status = 'pending'")
    approved = count("SELECT COUNT(*) FROM items WHERE approval = 'approved'")

    out: list[str] = []
    if merged:
        out.append(f"Done: {merged} change{'s' if merged > 1 else ''} built, "
                   "tested and merged.")
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
    if not out:
        if approved:
            out.append(f"Nothing waits on you and nothing is building. "
                       f"{approved} thing{'s' if approved > 1 else ''} approved so far.")
        else:
            out.append("Nothing waits on you and nothing is building. "
                       "Tell me what you want. I take it from there.")
    if looping is not None:
        out.append(looping.line())
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
    """The first `E   ` line of a pytest run, without its marker."""
    # pytest cuts the `FAILED` line's reason to the terminal width: night
    # 132's run tr248 ends `assert F...` (frame 142's design review, finding 5).
    for line in (output or "").splitlines():
        if line.startswith("E   "):
            return line[1:].strip()
    return ""


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
    run = conn.execute("SELECT result, output FROM test_runs WHERE test_id = ? "
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

    row = conn.execute(
        "SELECT i.kind, p.provenance FROM items i "
        "JOIN item_provenance p ON p.id = i.id WHERE i.id = ?", (ref,)).fetchone()
    return bool(row and row["kind"] == "in_scope" and ref != "how_it_works"
                and row["provenance"] != "observed"
                and not _is_description(conn, ref))


def _items_reached(conn: sqlite3.Connection, ref: str, hop: bool = True) -> list[str]:
    """The items that one ref reaches. A ledger row reaches what its
    `about_ref` reaches, one step and no further."""
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
    items: list[str] = []
    for ref in refs or []:
        if not isinstance(ref, str):
            continue
        for item in _items_reached(conn, ref):
            if item not in items and _is_request_item(conn, item):
                items.append(item)
    if not items:
        items = open_requests(conn)
    if not items:
        account = conn.execute(
            "SELECT 1 FROM items WHERE id = 'how_it_works'").fetchone()
        return ["how_it_works"] if account else []
    out: list[str] = []
    for item in items:
        out.append(item)
        out += [r["id"] for r in conn.execute(
            "SELECT c.id FROM criteria c JOIN tickets t ON t.id = c.ticket_id "
            "WHERE t.item_id = ? ORDER BY c.id", (item,))]
    return out


def _gave_up_tries(conn: sqlite3.Connection, criterion: str,
                   batch: str | None) -> int | None:
    """The attempts of a quarantined `tests_missing` key of a batch that
    holds the criterion, or None when no such key exists."""
    if batch:
        batches = [batch]
    else:
        batches = [r["batch_id"] for r in conn.execute(
            "SELECT bt.batch_id FROM batch_tickets bt "
            "JOIN criteria c ON c.ticket_id = bt.ticket_id "
            "JOIN batches b ON b.id = bt.batch_id "
            "WHERE c.id = ? AND b.status NOT IN ('merged', 'abandoned')", (criterion,))]
    for r in conn.execute(
            "SELECT tick_key, attempts FROM tick_attempts WHERE quarantined = 1 "
            "AND tick_key LIKE '%|tick:tests_missing|%' ORDER BY tick_key"):
        keyed = (r["tick_key"].split("|", 2) + [""])[2].split(",")
        if set(keyed) & set(batches):
            return r["attempts"]
    return None


def request_block(conn: sqlite3.Connection, refs: list[str], order: list[str],
                  out: list[str], *, said: list[tuple[str, str]] | None = None,
                  near: bool = False, batch: str | None = None,
                  park: bool = False) -> list[int]:
    """
    Render the request's rows of a page first: the principal's words, each
    item, and each item's criteria with their `check:` lines. Append to
    `out` and `order`, and return the line numbers of the items.

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
                if near:
                    found = near_code(conn, items[r])
                    if found:
                        out.append("     code that names these words: " + ", ".join(found))
        if group_must:
            out.append("It must:")
        for r in group_must:
            order.append(r)
            out.append(f"  {len(order)}. {crit[r][0]}")
            mine = [t["id"] for t in conn.execute(
                "SELECT id FROM tests WHERE criterion_id = ? "
                + ("AND batch_id = ? " if batch else "") + "ORDER BY id",
                (r, batch) if batch else (r,))]
            for t in mine:
                out.append(f"     check: {check_line(conn, t)}")
            if mine:
                continue
            # The Tester writes no test before the head commit, so a touch
            # note reads "none yet". A quarantined `tests_missing` key means
            # the team stopped trying. Night 136's m96 said nothing of cr_3
            # (frame 190's design, 2.5).
            tries = None if park else _gave_up_tries(conn, r, batch)
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
    """'tests_missing for bg_2, 3 attempts', one part per key."""
    parts = []
    for key in keys:
        bits = (key.split("|", 2) + ["", ""])[:3]
        row = conn.execute("SELECT attempts FROM tick_attempts WHERE tick_key = ?",
                           (key,)).fetchone()
        tries = row["attempts"] if row else 0
        parts.append(f"{bits[1].replace('tick:', '')} for {bits[2] or 'the whole project'}, "
                     f"{tries} attempt{'' if tries == 1 else 's'}")
    return "; ".join(parts)


TEAM_NOTES = ("The team's notes. A seat wrote each of these where your words "
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


def render_page(conn: sqlite3.Connection, verb: str, refs: list[str],
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
    the quarantined tick keys of the page. None reads them from
    `tick_attempts` for the batches the page names.
    """
    from ..core.runner import _resolve_refs
    from ..core.scheduler import park_ask_batch
    from ..onboarding.boot import ZERO

    parked_batch = park_ask_batch(ask_id or "")
    if parked_batch and verb == "present":
        return _park_page(conn, parked_batch, list(refs or []))

    refs = list(refs or [])
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
    keys = (list(stalled) if stalled is not None
            else _stalled_keys(conn, batches)) if verb == "present" else []
    if verb == "present" and keys and touches:
        # A quarantined batch is no plan any more. Night 136's m96 opened
        # "Before I build this" on a batch the Tester had given up on
        # (frame 190's design, 2.F, amendment 6).
        out.append("The team stopped work on this change.")
        asked = request_block(conn, refs, order, out, batch=batches[0])
        numbered(does + account)
        out.append(f"The team gave up on: {_stalled_words(conn, keys)}.")
        out.append("The team expects to touch:")
        numbered(touches)
        out.append("Reply 'ok' if every line says what you want. Name a line "
                   "to correct only that line. Ask, if something here is "
                   "unclear." + _name_request(asked))
    elif verb == "present" and touches:
        out.append("Before I build this, here is what I expect to touch.")
        asked = request_block(conn, refs, order, out, batch=batches[0])
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
        asked = request_block(conn, refs, order, out, said=said, near=True)
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
            for ref, text in does:
                numbered([(ref, text)])
                near = near_code(conn, text)
                if near:
                    out.append("     code that names these words: " + ", ".join(near))
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
        if zero:
            out.append("Some of this code has not been read yet. I will flag "
                       "anything I touch there.")
        out.append("Reply in your own words. 'ok' approves all of this and "
                   "starts building. Name a line to correct only that line. "
                   "Ask, if something here is unclear." + _name_request(asked))
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


STOP_WORDS = frozenset("""
the a an and or of to in on for with from by at as is are be can could
should will would that this these those it its their there user users
program system when where what which who how not no into over under
""".split())


def near_code(conn, text: str, cap: int = 3) -> list[str]:
    """
    The files whose symbols carry a word of this item's text.

    P4 piece 2 (plans/p4-scope-disclosure.md), in its mechanical form: at
    signoff nothing is sliced, so the Architect's guess is judgement the 8B
    tier has not earned. This is not a guess. It is the index, read for the
    item's own words, and the page labels it as that. A symbol `Invoice`
    names the word "invoices", and the file that defines it is where a
    change about invoices is likely to look.
    """
    words = set()
    for raw in text.lower().split():
        w = "".join(ch for ch in raw if ch.isalnum() or ch == "_")
        if len(w) >= 4 and w not in STOP_WORDS:
            words.add(w)
            if w.endswith("s"):
                words.add(w[:-1])
    if not words:
        return []
    hits: dict[str, int] = {}
    for row in conn.execute(
            "SELECT grain FROM code_index WHERE grain_kind = 'symbol'"):
        grain = row["grain"]
        path, _, name = grain.partition("::")
        lname = name.lower()
        if any(w in lname for w in words):
            hits[path] = hits.get(path, 0) + 1
    ranked = sorted(hits.items(), key=lambda kv: (-kv[1], kv[0]))
    return [path for path, _ in ranked[:cap]]


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


def _signoff_page(conn: sqlite3.Connection, message_id: str | None) -> bool:
    """Whether the present is the sign-off page: its cause is a `submit`."""
    row = conn.execute(
        "SELECT c.verb FROM messages m JOIN messages c ON c.id = m.cause_id "
        "WHERE m.id = ?", (message_id,)).fetchone() if message_id else None
    return bool(row and row["verb"] == "submit")


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

    # A touch note is read, not ruled on (P4, R7: nothing waits on it). The
    # batch's ref is never a row the principal rules, so it leaves the
    # ruling; what is left, if it is all approve, is an acknowledgement --
    # the note closes and wakes nobody. A contest or revise on the item lands
    # as any ruling does: the owner amends it, the version moves, and the
    # revocation is what ends the batch (loop 6) -- the lever the note is for.
    per_item = dict(answer.per_item or {})
    if ask.verb == "present" and answer.verb == "verdict":
        batches = {r["id"] for r in conn.execute("SELECT id FROM batches")}
        if batches & set(ask.refs):
            per_item = {k: v for k, v in per_item.items() if k not in batches}
            if all(v == "approve" for v in per_item.values()):
                return None

    # An "ok" off the sign-off page approves nothing of the request. The
    # door stamps the request's rows on every page, and the item's approval
    # belongs to the sign-off gate (law 8). An approve there would have
    # approved a contested item before its owner amended it, night 133's
    # wall 5 (frame 190's design, 2.F, amendment 1). The park page keeps
    # its own rows and its own rulings.
    from ..core.scheduler import park_ask_batch

    if (ask.verb == "present" and answer.verb == "verdict" and per_item
            and not park_ask_batch(ask.message_id or "")
            and not _signoff_page(conn, ask.message_id)):
        stamped = set(request_rows(conn, ask.refs))
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
    # Approve takes the default. Contest overrules it, with the words, and
    # contests the row the assumption was about: the principal rejected the
    # reading, so the row is amended by its owner through the contested
    # loop, with `principal_said` in front of it. Either way the ledger id
    # leaves the relay's refs -- the owner has nothing to apply to it, and
    # told to `set_approval` a ledger id it would only be refused. Measured
    # first the other way (2026-09-03): `decisions.author` handed to the
    # relay mode drew fourteen decisions a session, five of five, on the
    # plain approve case too. The tool in the list was the invitation.
    # (`per_item` is the ruling less any batch ref -- see the touch-note
    # door above.)
    closed_here: list[str] = []
    for ref, ruling in list(per_item.items()):
        if ruling not in ("approve", "contest", "revise"):
            continue
        row = conn.execute(
            "SELECT id, about_ref, default_taken FROM ledger "
            "WHERE id = ? AND status = 'open'", (ref,)).fetchone()
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
            if not (about and about["provenance"] == "observed"):
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
        conn.execute(
            "UPDATE items SET approval = ?, approval_ver = version "
            "WHERE id = ? AND approval IS NOT ?", (state, ref, state))

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
            conn.execute(
                "INSERT OR IGNORE INTO rulings (id, ask_id, per_item, words, "
                "status, verdict_id) VALUES (?, ?, ?, ?, 'landed', ?)",
                (f"r_{msg_id}", ask.message_id, json.dumps(per_item),
                 (answer.text or "").strip(), msg_id))
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
            "SELECT id, per_item, reply_id, verdict_id FROM rulings "
            "WHERE status = 'landed' AND (ask_id = ? OR reply_id = ?) "
            "ORDER BY rowid DESC LIMIT 1", (mid, mid)).fetchone()
        if row:
            per_item = json.loads(row["per_item"] or "{}")
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
