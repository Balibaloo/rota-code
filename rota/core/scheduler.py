"""
The scheduler: stateless, disposable, ~one loop.

It holds nothing. The frontier is a query, the schedule is derived, claims and
checkpoints are rows. Killing and restarting it at any moment loses nothing —
that is a required property with its own test, and it is what makes hand-rolling
it safe: this file can be deleted and rewritten against the database contract.

Frontier = open message tips ∪ tick predicates evaluated against current state.

The second half matters as much as the first. An approved item with no tickets is
not a message, it is a *state*; nothing would ever wake Vision Keeper for it. Because the
predicates are re-evaluated every pass, residual work cannot be lost — deferred
batches, half-sliced items, criteria-less tickets are all re-derived from state.
That is also why the scheduler can be thrown away: pending work was never held in
memory to lose.

Quiescence = no open tips + no predicate firing + no schedulable batch.
"""
from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass, field
from graphlib import CycleError, TopologicalSorter
from typing import Callable, Iterable

from ..design import graph as graph_mod


@dataclass(frozen=True)
class Wake:
    """One unit of work: a role to wake, and what woke it."""
    role: str
    kind: str                       # 'message' | tick name | 'cascade'
    message_id: str | None = None
    refs: tuple[str, ...] = ()
    detail: str = ""
    # Which dispatch of this wake this is. The dispatcher sets it from
    # `tick_attempts`, so the number the role reads is the number the
    # quarantine counts. Out of `__str__`, so no log line moves.
    attempt: int = 1
    # The tick key's count that this dispatch made, 0 when it made none.
    # `undo_dispatch` gives back against it only, so a direct `run_session`
    # never undoes an earlier dispatch (frame 355, review 1, finding 4).
    counted: int = field(default=0, compare=False, repr=False)
    # The quarantined messages a `tick:quarantined` wake counted. A report
    # marks these told and no others. Dry1's m5 names no row, so no ref
    # can name it (frame 355, review 1, finding 5).
    message_ids: tuple[str, ...] = field(default=(), compare=False,
                                       repr=False)

    def __str__(self) -> str:
        src = self.message_id or self.detail or ""
        return f"{self.role}<-{self.kind}({src})"


# ---------------------------------------------------------------------------
# Message tips
# ---------------------------------------------------------------------------

def open_tips(conn: sqlite3.Connection) -> list[Wake]:
    """
    Messages awaiting a session: open, not quarantined, addressed to a role.

    Messages to the principal are open too, but the principal is not schedulable — it
    answers when it answers. They are excluded here and surfaced by the agenda
    tick instead.

    Reports inside a broadcast round are excluded for the same kind of reason:
    they are not addressed to a session, they are addressed to a *harvest*.
    `tick_round_close` says why — dedupe "is impossible if Liaison wakes per
    report" — and until this exclusion existed the scheduler did exactly that.
    Tips are `traffic`, band 0; round_close is `gate`, band 20. The first report
    won the race every time, Liaison clarified from the one report it could see,
    and the `harvested` check then suppressed round_close permanently. The round
    was in the design, in the docstring, and in the prompt, and it never ran.

    A report *outside* a broadcast thread still tips, and that is the whole of
    what `report` mode is for: the top of the escalation ladder, where Vision Keeper
    has run out of rungs and the next step is a person.
    """
    # A ratified statement is delivered to owners who write against the
    # account, and the account is orientation's. tipsAI (2026-09-10): the
    # sentence arrived before orientation ran, the Vision Keeper's deliver
    # session found no account and wrote the feature as the account, and
    # nothing sliced it. The deliver waits until onboarding is done; the
    # confirm, the ratification and the transcript do not.
    hold_deliver = onboarding_phase(conn) not in ("done", "none")
    rows = conn.execute(
        "SELECT id, to_role, verb FROM messages m "
        "WHERE status = 'open' AND to_role != 'principal' "
        "  AND NOT (verb = 'deliver' AND ?) "
        "  AND NOT (verb = 'report' AND to_role = 'liaison' AND EXISTS ("
        "    SELECT 1 FROM messages d WHERE d.thread_id = m.thread_id "
        "      AND d.verb = 'deliver' AND d.from_role = 'liaison')) "
        # A report answering an `ask` is not addressed to a session either. It
        # marks the ask unresolved, and the ladder carries it from there; left
        # tipping as well, Liaison hears about the same question twice and the
        # `report` brief tells it the ladder is exhausted when it has barely
        # started.
        "  AND NOT (verb = 'report' AND EXISTS ("
        "    SELECT 1 FROM messages a WHERE a.id = m.cause_id "
        "      AND a.verb = 'ask')) "
        # Three answers compose into one reply -- the design's sentence, and
        # the same shape the broadcast round solved for reports: an answer to
        # an ask is addressed to a harvest, not a session. It does not tip
        # while a sibling ask in the thread is still open, and when the last
        # owner has spoken only the latest answer tips, carrying the round.
        # Without this the fan-out made the reply a race: whichever owner
        # answered first wrote what the principal read.
        "  AND NOT (verb = 'answer' AND EXISTS ("
        "    SELECT 1 FROM messages q WHERE q.id = m.cause_id "
        "      AND q.verb = 'ask') "
        "   AND (EXISTS (SELECT 1 FROM messages o WHERE o.thread_id = m.thread_id "
        "                  AND o.verb = 'ask' AND o.status = 'open') "
        "    OR m.seq < (SELECT MAX(a2.seq) FROM messages a2 "
        "                JOIN messages q2 ON q2.id = a2.cause_id "
        "                WHERE a2.thread_id = m.thread_id "
        "                  AND a2.verb = 'answer' AND a2.status = 'open' "
        "                  AND q2.verb = 'ask'))) "
        "ORDER BY seq", (hold_deliver,)
    ).fetchall()
    return [
        Wake(role=r["to_role"], kind="message", message_id=r["id"], detail=r["verb"])
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Tick predicates. Each is a pure query over current state.
# ---------------------------------------------------------------------------

def report_is_settled(conn: sqlite3.Connection, refs: list[str]) -> bool:
    """
    Whether a report is a role saying it has finished rather than asking.

    Every ref names a row in a terminal state -- an item at `approval:
    approved`, a statement at `status: ratified` -- and there is nothing in it
    for anyone to relay.

    This was Liaison's to work out, in prose: "cross off the reports that are
    already settled ... the row says which it is". Two things were wrong with
    that. Liaison does not make decisions; its responsibility is lossless
    communication, and deciding a role has finished is a decision. And the
    lookup is mechanical -- an item at `approved` is approved -- so putting it
    in a model's head buys the risk of it being got wrong and nothing else.

    Underneath sat a livelock that the *correct* behaviour caused. `harvested`
    counts Liaison's own clarify and present messages, so a round it rightly
    ended in silence was never marked harvested and this predicate fired
    forever. The only way to make the system progress was to message the
    principal about a settled round -- the system rewarded the failure and
    punished the right answer, and the L1 case for it could not have passed
    without hanging the scheduler.

    Empty refs are not settled. A report carrying nothing has said nothing that
    can be checked, and it is the one that most needs a person.
    """
    if not refs:
        return False
    for ref in refs:
        row = conn.execute(
            "SELECT approval FROM items WHERE id = ?", (ref,)).fetchone()
        if row is not None:
            if row["approval"] != "approved":
                return False
            continue
        row = conn.execute(
            "SELECT status FROM statements WHERE id = ?", (ref,)).fetchone()
        if row is not None:
            if row["status"] != "ratified":
                return False
            continue
        # A glossary sense, a constraint, a criterion: real rows with no
        # terminal marker of this kind. Unsettled, which is the safe way round
        # -- two senses of one word is exactly the round's business.
        return False
    return True


def open_reports(conn: sqlite3.Connection, thread: str) -> list[sqlite3.Row]:
    """The reports in a thread that are still asking for something."""
    from .db import refs_of

    return [r for r in conn.execute(
        "SELECT id, from_role, body_refs FROM messages "
        "WHERE thread_id = ? AND verb = 'report' ORDER BY seq", (thread,))
        if not report_is_settled(conn, refs_of(r["body_refs"]))]


def tick_round_close(conn: sqlite3.Connection) -> list[Wake]:
    """
    Liaison harvests once a broadcast's whole subtree has terminated.

    A round exists for one reason: dedupe. Two roles reporting the same blocker
    in different vocabulary must become one question, which is impossible if
    Liaison wakes per report. Waiting is the feature.

    A role with nothing to say emits nothing — the committed session is the
    terminator, so silence is legible without a null-message convention.
    """
    broadcasts = conn.execute(
        "SELECT DISTINCT thread_id FROM messages WHERE verb = 'deliver' AND from_role = 'liaison'"
    ).fetchall()

    wakes = []
    for b in broadcasts:
        thread = b["thread_id"]
        # Every recipient of the broadcast has committed, and nothing in the
        # subtree is still open (a terminologist->vision_keeper challenge keeps it open).
        pending = conn.execute(
            "SELECT COUNT(*) AS n FROM messages "
            "WHERE thread_id = ? AND status = 'open' AND to_role != 'liaison'",
            (thread,),
        ).fetchone()["n"]
        if pending:
            continue
        # Reports harvested already?
        harvested = conn.execute(
            "SELECT COUNT(*) AS n FROM messages "
            "WHERE thread_id = ? AND from_role = 'liaison' AND verb IN ('clarify','present')",
            (thread,),
        ).fetchone()["n"]
        # Only the reports still asking for something. A round where every role
        # reported itself done is a round with nothing to communicate, and
        # Liaison is not woken for it at all -- which is also what stops this
        # predicate firing forever over a round that was rightly met in silence.
        open_ = open_reports(conn, thread)
        if open_ and not harvested:
            wakes.append(Wake("liaison", "tick:round_close", refs=(thread,),
                              detail=f"{len(open_)} report(s)"))
    return wakes


def not_described(conn: sqlite3.Connection, col: str, of: str = "item") -> str:
    """
    An SQL condition that drops the rows whose item is a description. `col`
    holds an item id, or a ticket id when `of` is "ticket".

    A description asks for nothing, so it is never cut and never owes
    criteria (ruled: Roman, 2026-09-24, frame 80). The condition is empty on
    a run database that predates the column. `frontier_readonly`, the trace
    view and the CLI open such a database read-only and never run `init_db`.
    """
    from .db import _has_column

    if not _has_column(conn, "items", "is_description"):
        return ""
    described = "SELECT id FROM items WHERE is_description = 1"
    if of == "ticket":
        described = f"SELECT id FROM tickets WHERE item_id IN ({described})"
    return f" AND {col} NOT IN ({described})"


def not_retired(conn: sqlite3.Connection, col: str) -> str:
    """
    An SQL condition that drops a retired ticket. `col` holds a ticket id.

    A ticket is retired when a newer slice of its item exists: its
    `item_ver` is below the newest `item_ver` of the item's tickets. A NULL
    is unknown and stays live, so an older database does not move (frame
    190's design, 2.F, amendment 4). The condition is empty on a run
    database that predates the column.
    """
    from .db import _has_column

    if not _has_column(conn, "tickets", "item_ver"):
        return ""
    return (f" AND {col} NOT IN (SELECT r.id FROM tickets r WHERE r.item_ver < "
            f"(SELECT MAX(n.item_ver) FROM tickets n WHERE n.item_id = r.item_id))")


def live_criteria(conn: sqlite3.Connection, col: str) -> str:
    """
    An SQL condition that drops a retired criterion. `col` holds a
    criterion's `retired_by`.

    His ruling that drops a criterion line retires the row, and the row stays
    with its ruling (frame 306, pass 1b). The condition is empty on a run
    database that predates the column.
    """
    from .db import _has_column

    if not _has_column(conn, "criteria", "retired_by"):
        return ""
    return f" AND {col} IS NULL"


def live_tests(conn: sqlite3.Connection, col: str) -> str:
    """
    An SQL condition that drops a test of a retired criterion. `col` holds a
    test id.

    The test and its runs stay in the table as the record. A red run of it
    holds no merge and parks no batch, because he dropped its line (frame
    306, pass 2, finding 2).
    """
    from .db import _has_column

    if not _has_column(conn, "criteria", "retired_by"):
        return ""
    # A test he retired by its own line drops out too (frame 306, W-A).
    own = (" UNION SELECT id FROM tests WHERE retired_by IS NOT NULL"
           if _has_column(conn, "tests", "retired_by") else "")
    return (f" AND {col} NOT IN (SELECT t.id FROM tests t JOIN criteria c "
            f"ON c.id = t.criterion_id WHERE c.retired_by IS NOT NULL{own})")


# The items whose newest `item_parks` row puts them aside: the principal said
# later or drop on the shift page (frame 193's design, 2.F.4).
_ASIDE = ("SELECT p.item_id FROM item_parks p WHERE p.kind IN ('park', 'drop') "
          "AND p.rowid = (SELECT q.rowid FROM item_parks q WHERE q.item_id = "
          "p.item_id ORDER BY q.seq DESC, q.rowid DESC LIMIT 1)")


def _has_parks(conn: sqlite3.Connection) -> bool:
    return bool(conn.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' "
                             "AND name = 'item_parks'").fetchone())


def not_parked(conn: sqlite3.Connection, col: str, of: str = "item") -> str:
    """
    An SQL condition that drops an item set aside, or its ticket or batch.
    `col` holds an item id, a ticket id when `of` is "ticket", or a batch id
    when `of` is "batch".

    The shape of `not_described`. A set-aside item wakes no seat and opens no
    batch until a resume (frame 193's design, 2.F.4). The condition is empty
    on a database with no `item_parks` table.
    """
    if not _has_parks(conn):
        return ""
    aside = _ASIDE
    if of == "ticket":
        aside = f"SELECT id FROM tickets WHERE item_id IN ({aside})"
    elif of == "batch":
        aside = f"SELECT id FROM batches WHERE item_id IN ({aside})"
    return f" AND {col} NOT IN ({aside})"


def park_kind(conn: sqlite3.Connection, item_id: str) -> str | None:
    """The kind of the item's newest `item_parks` row, or None."""
    if not _has_parks(conn):
        return None
    row = conn.execute("SELECT kind FROM item_parks WHERE item_id = ? "
                       "ORDER BY seq DESC, rowid DESC LIMIT 1", (item_id,)).fetchone()
    return row["kind"] if row else None


def aside_items(conn: sqlite3.Connection) -> set[str]:
    """Every item set aside: its newest `item_parks` row is park or drop."""
    if not _has_parks(conn):
        return set()
    return {r[0] for r in conn.execute(_ASIDE)}


def tick_slicing(conn: sqlite3.Connection) -> list[Wake]:
    """
    Vision Keeper slices tickets from items whose approval postdates their last
    amendment. Fires per *gate result* rather than per item: one session with the
    whole batch of approvals is cheaper and better informed.
    """
    # The account is not sliced. `how_it_works` is the whole program in four
    # sentences, the first item on the page. The behaviours beside it are what
    # tickets come from. Measured on a cold walk (tipsE, 2026-09-08): the
    # account was approved with no ticket, this predicate woke Vision Keeper,
    # Vision Keeper sliced nothing from it, and the predicate woke it again.
    # Fifty sessions, no batch, no ask.
    # An observed item is the record of what the code does today: found,
    # not decided, and approving it on the page ratifies the description.
    # It is not a build order. Sliced, it sent the Developer to rewrite
    # behaviour that exists (tipsK, tipsT, 2026-09-09).
    # An item amended after its delivery is new work. Its tickets went out
    # in a merged batch; the merge records the item's version under
    # `delivered:<item>`, and an approval of a later version slices again.
    # Without this the corrected split sat approved at version 9 with one
    # spent ticket and the run went quiet (tipsAH, 2026-09-09, from the
    # seat).
    # An item amended before its delivery is new work too. Its old ticket
    # and criteria predate the principal's words, and `grouping` put them in
    # a new batch (frame 190's design, 2.F, amendment 4). The cancel of the
    # ruling of 2026-09-12 takes the running batch first, because it fires
    # while the item is not approved. A ticket with no `item_ver` is unknown
    # and never sliced again.
    from .db import _has_column

    amended = (
        "       OR (i.version > (SELECT MAX(t.item_ver) FROM tickets t "
        "                        WHERE t.item_id = i.id) "
        "           AND NOT EXISTS (SELECT 1 FROM tickets t "
        "                          JOIN batch_tickets bt ON bt.ticket_id = t.id "
        "                          JOIN batches b ON b.id = bt.batch_id "
        "                          WHERE t.item_id = i.id "
        "                            AND b.status NOT IN ('merged', 'abandoned'))) "
    ) if _has_column(conn, "tickets", "item_ver") else ""
    rows = conn.execute(
        "SELECT i.id FROM items i "
        "JOIN item_provenance p ON p.id = i.id "
        "WHERE i.kind = 'in_scope' AND i.approval = 'approved' "
        "  AND i.approval_ver >= i.version "
        "  AND i.id != 'how_it_works' "
        "  AND p.provenance != 'observed' "
        # An item set aside is not sliced until it resumes (frame 193's
        # design, 2.F.4).
        + not_described(conn, "i.id") + not_parked(conn, "i.id") +
        "  AND (i.id NOT IN (SELECT item_id FROM tickets) "
        "       OR i.version > COALESCE((SELECT CAST(value AS INTEGER) FROM config "
        "                                 WHERE key = 'delivered:' || i.id), 0) "
        "          AND NOT EXISTS (SELECT 1 FROM tickets t "
        "                          JOIN batch_tickets bt ON bt.ticket_id = t.id "
        "                          JOIN batches b ON b.id = bt.batch_id "
        "                          WHERE t.item_id = i.id "
        "                            AND b.status NOT IN ('merged', 'abandoned')) "
        "          AND EXISTS (SELECT 1 FROM config WHERE key = 'delivered:' || i.id)"
        + amended + ")"
    ).fetchall()
    if not rows:
        return []
    # An amended item is a new debt under the same tick key. The key's old
    # quarantine, earned before the amendment, is forgotten once per
    # version and the forgetting is on record, so live evidence is never
    # erased: the corrected split sat quarantined under its own key from
    # three slicing sessions of the first delivery (tipsAH, 2026-09-09).
    for r in rows:
        ver = conn.execute("SELECT version FROM items WHERE id = ?",
                           (r["id"],)).fetchone()["version"]
        seen = conn.execute("SELECT value FROM config WHERE key = ?",
                            (f"resliced:{r['id']}",)).fetchone()
        if seen is None or int(seen["value"]) != ver:
            from .db import forget_keys

            forget_keys(conn, [f"vision_keeper|tick:slicing|{r['id']}"])
            conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                         (f"resliced:{r['id']}", str(ver)))
    return [Wake("vision_keeper", "tick:slicing", refs=tuple(r["id"] for r in rows))]


def tick_criteria(conn: sqlite3.Connection) -> list[Wake]:
    """
    Terminologist writes criteria for tickets that have none. Fires per *item*: criteria
    written for one ticket in isolation is how you get criteria that contradict
    their siblings.
    """
    rows = conn.execute(
        "SELECT DISTINCT t.item_id AS item_id FROM tickets t "
        "WHERE t.id NOT IN (SELECT ticket_id FROM criteria)"
        + not_described(conn, "t.item_id") + not_retired(conn, "t.id")
        # An item set aside owes no criteria while it waits (2.F.4).
        + not_parked(conn, "t.item_id")
    ).fetchall()
    return [
        Wake("terminologist", "tick:criteria", refs=(r["item_id"],),
             detail=criteria_detail(conn, r["item_id"]))
        for r in rows
    ]


def criteria_tickets(conn: sqlite3.Connection, item_id: str,
                     written: set[str] = frozenset()) -> tuple[list, list]:
    """
    The live tickets of an item, split into those with no criterion and
    those with one. Each is a pair of the id and the headline. `written`
    holds ticket ids that a staged write covers.

    The test is `tick_criteria`'s own, so the wake and the list agree.
    """
    rows = conn.execute(
        "SELECT t.id AS id, substr(t.text, 1, 120) AS headline, "
        "t.id IN (SELECT ticket_id FROM criteria) AS covered "
        "FROM tickets t WHERE t.item_id = ?" + not_retired(conn, "t.id")
        + " ORDER BY t.rowid", (item_id,)).fetchall()
    empty = [(r["id"], r["headline"]) for r in rows
             if not r["covered"] and r["id"] not in written]
    covered = [(r["id"], r["headline"]) for r in rows
               if r["covered"] or r["id"] in written]
    return empty, covered


def criteria_detail(conn: sqlite3.Connection, item_id: str) -> str:
    """
    The criteria wake's detail: each ticket with no criterion first, then
    each covered ticket.

    Night 163, item `clear()`: the wake named the item only. s199 wrote three
    criteria on tk_1 and none on tk_2, and three attempts wrote invented
    cases (frame 322, cause 9). The detail names a row state, not a meaning
    (the rule of 2026-09-09).
    """
    # One line, because `Wake.__str__` puts the detail in the log line.
    empty, covered = criteria_tickets(conn, item_id)
    parts = [f"No criterion yet: {tid} ({head})." for tid, head in empty]
    parts += [f"Covered: {tid} ({head})." for tid, head in covered]
    return " ".join(parts)


def tick_batch_start(conn: sqlite3.Connection) -> list[Wake]:
    """
    Start the next batch: schedulable, ordered first, and nothing running
    (Developer is single-instance).

    Schedulable is the revocation predicate: the batch's item must be approved
    *and* that approval must postdate the item's last amendment.
    """
    running = conn.execute(
        "SELECT id, head_commit FROM batches WHERE status = 'running' ORDER BY id"
    ).fetchall()
    if running:
        # A running batch with no commit is a start that did not land.
        # tipsAI (2026-09-10): the Developer's one session read the code,
        # logged a plan and called commit with nothing written; the call
        # was refused, the session ended, and no predicate woke anyone
        # again. The batch stayed running with no commit and the run went
        # quiet. The start is owed until a commit exists. The tick
        # quarantine caps the repeats, keyed by the batch.
        stalled = [r["id"] for r in running if not r["head_commit"]
                   and conn.execute(
                       "SELECT 1 FROM sessions WHERE role = 'developer' "
                       "AND wake_kind = 'tick:batch_start' AND committed = 1 "
                       "AND wake_refs LIKE ?",
                       (f'%"{r["id"]}"%',)).fetchone()]
        if not stalled:
            return []
        # law 4: failure is bounded
        # A re-fire at temperature zero with the same wake is the same
        # session again. Night 73 (2026-09-15): three identical 22-turn
        # sessions at batch_start, no write, quarantined. The attempt count
        # is a fact of this table and the wake carries it. `DETAIL_SHOWN`
        # hides this detail, so the door in `loop.step` is what makes the
        # second session differ from the first (frame 58, 2026-09-23).
        from . import config

        row = conn.execute("SELECT attempts FROM tick_attempts WHERE tick_key = ?",
                           (f"developer|tick:batch_start|{stalled[0]}",)).fetchone()
        n = int(row["attempts"]) + 1 if row else 2
        # The cap comes from the configuration, so this sentence and the
        # dispatcher's retry sentence read one cap.
        cap = config.get(conn, "tick_attempt_cap")
        # Night 156's s215 read "nothing written" after s214 left a write in
        # the tree. The account's own words say what the end discarded
        # (frame 297).
        from .lifecycle import last_discard

        gone, stayed = last_discard(conn, stalled[0])
        last = (f"the last session committed nothing. The runner discarded its "
                f"writes to {', '.join(gone)}." if gone else
                "the last session ended with nothing written and nothing committed")
        if stayed:
            last = (f"{last if gone else 'the last session committed nothing.'} "
                    f"The runner could not put back {', '.join(stayed)}.")
        return [Wake("developer", "tick:batch_start", refs=(stalled[0],),
                     detail=f"attempt {n} of {cap}: {last}")]

    candidates = next_batch(conn)
    if not candidates:
        return []
    first = candidates[0]
    if first["status"] == "deferred" and first["head_commit"]:
        # A deferred batch with commits is a resume, not a fresh start. Night
        # 92's start wake carried no attempt, so the Developer found its own
        # flag and did nothing (observed: night 92, 2026-09-24). Law 5 still
        # restarts it from its rows, and `lifecycle.start` keeps its worktree.
        return [Wake("developer", "tick:batch_start", refs=(first["id"],),
                     detail=_resume_detail(conn, first["id"]))]
    return [Wake("developer", "tick:batch_start", refs=(first["id"],))]


def _resume_detail(conn: sqlite3.Connection, batch_id: str) -> str:
    """The attempt a deferred batch left, and its tests that still fail."""
    # A test's latest run is its result, as `tests_failing` reads it.
    rows = conn.execute(
        "SELECT test_id, result, attempt FROM latest_runs WHERE batch_id = ? "
        "ORDER BY test_id", (batch_id,)).fetchall()
    attempt = max((r["attempt"] or 1 for r in rows), default=0)
    failing = sorted((r["test_id"] for r in rows if r["result"] in ("fail", "error")),
                     key=_by_number)
    if not rows:
        return "resume: the batch has commits and no test run yet"
    if not failing:
        return f"resume after attempt {attempt}: all {len(rows)} tests pass"
    shown = ", ".join(failing[:10]) + (f" and {len(failing) - 10} more"
                                       if len(failing) > 10 else "")
    return (f"resume after attempt {attempt}: {len(failing)} of {len(rows)} "
            f"tests failing: {shown}")


def signoff_drafts(conn: sqlite3.Connection) -> list[str]:
    """
    The draft items a signoff submits, in id order. A parked draft is not
    one of them (frame 193's design, 2.F.4).

    This is the one reader of the set (F32). `tick_signoff` wakes on it, and
    the submit door refuses a submit that leaves out one of its woken items.
    law 8: signoff is per-item approval, presented as one document.
    """
    return [r["id"] for r in conn.execute(
        "SELECT id FROM items WHERE approval = 'draft'"
        + not_parked(conn, "id") + " ORDER BY id")]


def tick_signoff(conn: sqlite3.Connection) -> list[Wake]:
    """
    Draft items with no gate open on them: Vision Keeper submits them for approval.

    Fires per *set* rather than per item, because Signoff presents one document —
    the principal is approving an interpretation, and interpretations are read
    whole. An item already awaiting a verdict is not resubmitted.
    """
    from .lifecycle import touch_notes

    # A draft set aside is not submitted, and an ask held behind the shift
    # question is not an open gate (frame 193's design, 2.F.4).
    from ..roles.principal import held_asks

    drafts = signoff_drafts(conn)
    if not drafts:
        return []
    # A touch note is set aside (P4, 2026-09-03): this guard exists so an
    # interpretation is not submitted twice, and a note nobody has to answer
    # left open would otherwise freeze every later signoff behind it.
    skip = set(touch_notes(conn)) | held_asks(conn)
    pending = sum(1 for r in conn.execute(
        "SELECT id FROM messages WHERE status = 'open' "
        "AND verb IN ('submit', 'present')") if r["id"] not in skip)
    if pending:
        return []
    return [Wake("vision_keeper", "tick:signoff", refs=tuple(drafts))]


# Terms first, because constraints are written in glossary terms; observed
# baseline last, because it describes behaviour in those terms. Named rather
# than inlined so the obligation set can see which roles onboarding wakes —
# buried in the loop below, the three survey modes were invisible to it, and
# they were the three that turned out to have no prompt at all.
# Which roles survey each area, and in what order, once the program has been
# oriented and its words defined.
#
# Vision Keeper used to be the third pass, per area, and wrote sentences about
# code -- `getRelativePath: returns the relative path` -- because a folded
# directory is not where a product's behaviour lives. Its pass is the first one
# now, over the whole program (`tick_orient`), and every later phase is written
# with its account in front of it. The per-area mode files survive, unoffered;
# putting the role back here is one edit and a re-measurement.
SURVEY_ORDER = ("terminologist", "architect")

# Onboarding subjects that are not areas. A wake carries its subject in
# `refs[0]`; for a survey that is a path, for the orientation it is the whole
# program, and for the define phase it is one word. Sigilled so nothing that
# consumes an area can mistake one for a directory.
PROGRAM = "@program"
PROSE = "@prose"
TERM_PREFIX = "@term:"
FRAME = "@frame"
REORIENT = "@reorient"
CLAIM_PREFIX = "@claim:"
BLINDSPOTS = "@blindspots"
SURFACE_PREFIX = "@surface:"
# The whole set, for the ref door: a `@` ref is legal when it names an area
# this run declared, and these are the subjects that are not directories.
# `@surface:` belongs here, and was missed: `_boundary_wakes` wakes the
# Architect on one, so the boundary session could ref its own subject and no
# other session could name it (the diff review of 8ebbae1).
PSEUDO_AREAS = (PROGRAM, PROSE, FRAME, REORIENT, BLINDSPOTS)
PSEUDO_AREA_PREFIXES = (TERM_PREFIX, CLAIM_PREFIX, SURFACE_PREFIX)
ONBOARDING_TICKS = ("tick:frame", "tick:orient", "tick:reconcile",
                    "tick:define", "tick:survey", "tick:reorient",
                    "tick:boundary", "tick:challenge", "tick:blindspot")


def is_area(subject: str | None) -> bool:
    """A path under the checkout, as opposed to `@program` or `@term:x`."""
    return bool(subject) and not str(subject).startswith("@")


def term_of(subject: str | None) -> str:
    return subject[len(TERM_PREFIX):] if subject and subject.startswith(TERM_PREFIX) else ""


def surface_of(subject: str | None) -> str:
    """`@surface:intentsSchema.yaml` is the subject `intentsSchema.yaml`."""
    return (subject[len(SURFACE_PREFIX):]
            if subject and subject.startswith(SURFACE_PREFIX) else "")


def onboarding_phases(conn: sqlite3.Connection) -> tuple[str, ...]:
    """The phases this run performs, in order. A setting the principal owns."""
    from . import config

    raw = config.get(conn, "onboarding_phases")
    return tuple(p.strip() for p in str(raw).split(",") if p.strip())


def _abandoned(conn: sqlite3.Connection, kind: str) -> set[str]:
    """Subjects of quarantined ticks of this kind, by `refs[0]`."""
    return {key_parts(k)[2][0]
            for k in quarantined_keys(conn, kind=kind) if key_parts(k)[2]}


def _frame_wakes(conn: sqlite3.Connection) -> list[Wake]:
    """
    The frame has not been judged.

    v2's first stage: one Architect session classifies the tree -- program,
    attached, ignore, boundary -- before anything reads it, because the
    partition decides what every later session can see, and a 14B judge
    measured 34/38 on six repositories where the name heuristics fail two
    (probes/partition_judge.py). The attest re-pins; `none_found` means the
    heuristic frame stands, and is the honest common answer for a
    conventionally-shaped checkout.
    """
    if not conn.execute("SELECT 1 FROM code_index LIMIT 1").fetchone():
        return []
    if FRAME in _abandoned(conn, "tick:frame"):
        return []
    done = conn.execute("SELECT 1 FROM survey_records WHERE area = ?",
                        (FRAME,)).fetchone()
    return [] if done else [Wake("architect", "tick:frame", refs=(FRAME,))]


def tick_frame(conn: sqlite3.Connection) -> list[Wake]:
    return _frame_wakes(conn) if onboarding_phase(conn) == "frame" else []


def _repin_after_frame(conn: sqlite3.Connection) -> None:
    """
    Apply the judged frame, once, lazily.

    The judge's rulings land when its session commits -- after any op has
    returned -- so the re-pin cannot run inside the attest. It runs here
    instead: the first frontier computation that sees the @frame record
    re-derives partition, lexicon and constraint zero over the ruled table,
    and a flag keeps it from running twice. Deterministic: same rulings,
    same frame, whenever it fires.
    """
    flag = conn.execute(
        "SELECT value FROM config WHERE key = 'frame_repinned'").fetchone()
    if flag and flag["value"] == "1":
        return
    if not conn.execute("SELECT 1 FROM survey_records WHERE area = ?",
                        (FRAME,)).fetchone():
        return
    root = conn.execute(
        "SELECT value FROM config WHERE key = 'project_root'").fetchone()
    if not root:
        return
    from ..onboarding.boot import repin

    repin(conn, root["value"])
    conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
                 "('frame_repinned', '1')")


def _orient_wakes(conn: sqlite3.Connection) -> list[Wake]:
    """
    The program has not been oriented: nobody has said what it does for its
    user, and every later phase is written with that account in front of it.

    One wake, for the whole program, to the role answerable for what the
    project is. Discharged by its survey record -- `found` with items under
    it, or `none_found`, which is a real answer about a tree that is all
    plumbing -- or by the attempt bound.
    """
    if not conn.execute("SELECT 1 FROM code_index LIMIT 1").fetchone():
        return []
    if PROGRAM in _abandoned(conn, "tick:orient"):
        return []
    done = conn.execute("SELECT 1 FROM survey_records WHERE area = ?",
                        (PROGRAM,)).fetchone()
    return [] if done else [Wake("vision_keeper", "tick:orient", refs=(PROGRAM,))]


def _reconcile_wakes(conn: sqlite3.Connection) -> list[Wake]:
    """
    The README has not been read against the account.

    The orientation is written from code alone -- prose is hearsay from absent
    authors -- and then the README is read *as a check*: where it and the
    account disagree, "the README is stale" and "the code has a bug" are the
    two readings and only the principal can say which, so each disagreement is
    a ledger entry the agenda puts to them. One wake, after the orientation,
    only when there is prose to reconcile.
    """
    from . import config

    try:
        if config.get(conn, "prose_sources") == "off":
            return []
    except Exception:                                       # pragma: no cover
        pass
    if not conn.execute(
            "SELECT 1 FROM code_index WHERE grain_kind = 'path' "
            "AND (grain LIKE 'README%' OR grain LIKE 'readme%') LIMIT 1").fetchone():
        return []
    if not conn.execute("SELECT 1 FROM survey_records WHERE area = ?",
                        (PROGRAM,)).fetchone():
        return []
    # One area per prose file, the README first as `@prose`, then each file
    # under docs/ as `@prose:<path>`. clickI (2026-09-12): 37 prose files
    # under docs/ went unread because the phase read only the README, and a
    # conflict between two sources is a page the principal always sees
    # (DECISIONS.md, "The seat's four pages are one surface").
    # One wake per group of open files, not per file (frame 354). One file a
    # session spent 39 or 40 sessions a night on clickI, nights 170 to 175,
    # and a 40-step run ended inside the phase.
    # Only a quarantined group of one abandons its file. A group of several
    # at the bound wakes each file alone, because one hard file broke the
    # group and lost its neighbours (review of frame 354, finding 1). Each
    # key of tick_attempts counts its own wakes, so a file alone gets the
    # full bound after its group spent one.
    abandoned, alone = set(), set()
    for k in quarantined_keys(conn, kind="tick:reconcile"):
        # `regrouped_key` is the one test (review p4 of frame 354, finding 6).
        (alone if regrouped_key(k) else abandoned).update(key_parts(k)[2])
    done = {r["area"] for r in conn.execute(
        "SELECT area FROM survey_records WHERE area = ? OR area LIKE ?",
        (PROSE, PROSE + ":%"))}
    open_areas = [a for a in prose_areas(conn)
                  if a not in abandoned and a not in done]
    groups = [(a,) for a in open_areas if a in alone]
    groups += prose_groups(conn, [a for a in open_areas if a not in alone])
    return [Wake("vision_keeper", "tick:reconcile", refs=group)
            for group in groups]


# The characters of prose one reconcile session holds (frame 354). The runner
# cuts a pushed read at PUSH_CHARS, 20,000, so a group stays below that with
# room for one header line per file. The seat then sees each file whole.
PROSE_GROUP_CHARS = 18000


def prose_path(conn: sqlite3.Connection, area: str) -> str | None:
    """The file a prose area names: the root README for `@prose`, the path
    after the colon for `@prose:<path>`."""
    if area.startswith(PROSE + ":"):
        return area[len(PROSE) + 1:]
    if area != PROSE:
        return None
    return next((r["grain"] for r in conn.execute(
        "SELECT grain FROM code_index WHERE grain_kind = 'path' ORDER BY grain")
        if re.match(r"(?i)readme(\.|$)", r["grain"])), None)


def prose_groups(conn: sqlite3.Connection,
                 areas: list[str]) -> list[tuple[str, ...]]:
    """
    The open prose areas, in their order, cut into the groups one session reads.

    A group takes files until the next one would pass PROSE_GROUP_CHARS. A
    file at or over the budget is a group of one. So is a file whose size
    cannot be read, which keeps the one-file wake where no tree is known.
    """
    try:
        from .worktrees import project_root
        root = project_root(conn)
    except Exception:
        root = None
    groups: list[tuple[str, ...]] = []
    group: list[str] = []
    used = 0
    for area in areas:
        size = None
        path = prose_path(conn, area)
        if root is not None and path:
            try:
                size = (root / path).stat().st_size
            except OSError:
                size = None
        if size is None or size >= PROSE_GROUP_CHARS:
            if group:
                groups.append(tuple(group))
            groups.append((area,))
            group, used = [], 0
            continue
        if group and used + size > PROSE_GROUP_CHARS:
            groups.append(tuple(group))
            group, used = [], 0
        group.append(area)
        used += size
    if group:
        groups.append(tuple(group))
    return groups


def prose_areas(conn: sqlite3.Connection) -> list[str]:
    """The prose the reconcile phase reads, one area each: `@prose` for the
    root README, `@prose:<path>` for each prose file under docs/ or doc/."""
    docs = [r["grain"] for r in conn.execute(
        "SELECT grain FROM code_index WHERE grain_kind = 'path' "
        "AND (grain LIKE 'docs/%' OR grain LIKE 'doc/%') "
        "AND (grain LIKE '%.md' OR grain LIKE '%.rst' OR grain LIKE '%.txt') "
        "ORDER BY grain")]
    return [PROSE] + [f"{PROSE}:{p}" for p in docs]


def pending_terms(conn: sqlite3.Connection) -> list[str]:
    """
    The words the define phase still owes, best first.

    The lexicon is the project's own list -- directories, files, declared
    types, authoring keys -- and the orientation adds to it: a word the account
    of the program needed is a word the program is about, and two lexicon words
    the account says together, which the code also says together, are one
    compound (`global intent`). Both are computed here, at frontier time,
    because the items did not exist when the lexicon was built.

    A word is settled by a live glossary row in its family, by a `none_found`
    record for it, or by the attempt bound. Nothing else removes it.
    """
    import json
    import math

    from . import config
    from ..onboarding import lexicon as lex
    from ..roles.api import _singular, _slug_of

    try:
        rows = lex.ranked(conn)
    except sqlite3.Error:
        return []
    if not rows:
        return []

    toks: list[str] = []
    for r in conn.execute("SELECT i.text FROM items i JOIN item_provenance p "
                          "ON p.id = i.id WHERE p.provenance = 'observed'"):
        toks += [lex.singular(w) for w in lex.parts(r["text"] or "")]
    item_words = set(toks)
    item_bigrams = set(zip(toks, toks[1:]))

    def said_together(ws: list[str]) -> bool:
        return any(tuple(ws) == tuple(toks[i:i + len(ws)])
                   for i in range(max(0, len(toks) - len(ws) + 1)))

    scored: dict[str, tuple[float, int]] = {}
    for r in rows:
        word, score, uses = r["word"], float(r["score"]), int(r["uses"])
        ws = word.split()
        if (len(ws) == 1 and word in item_words) or (len(ws) > 1 and said_together(ws)):
            score += 3.0
        scored[word] = (score, uses)
    try:
        bigrams = json.loads(conn.execute(
            "SELECT value FROM config WHERE key = 'lexicon_bigrams'"
        ).fetchone()["value"])
    except (TypeError, ValueError, sqlite3.Error):
        bigrams = []
    for a, b, n in bigrams:
        if (a, b) in item_bigrams and f"{a} {b}" not in scored:
            scored[f"{a} {b}"] = (3.0 + min(2.0, math.log10(n + 1)) + 3.0, n)

    defined = {_singular(r["id"].split("#")[0]) for r in conn.execute(
        "SELECT id FROM glossary_terms WHERE superseded_by IS NULL")}
    declined = {term_of(r["area"]) for r in conn.execute(
        "SELECT area FROM survey_records WHERE area LIKE ?", (TERM_PREFIX + "%",))}
    abandoned = {term_of(a) for a in _abandoned(conn, "tick:define")}

    n = int(config.get(conn, "define_terms"))
    ranked = sorted(scored.items(), key=lambda kv: (-kv[1][0], -kv[1][1], kv[0]))
    picked = [word for word, _ in ranked[:n]]
    # The authoring keys, regardless of rank. `define_terms` bounds the open
    # vocabulary; the keys are the closed one -- what the project asks its
    # user to type -- and on the first run with keys in the lexicon all
    # twenty were present and none cracked the cap.
    keys = [r["word"] for r in conn.execute(
        "SELECT word FROM code_lexicon WHERE sources LIKE ? "
        "ORDER BY score DESC, uses DESC, word", ('%"key"%',))]
    # The prose's names, after the keys. The lexicon nominated them from the
    # README (frequent, emphasised, absent from the code's vocabulary); a run
    # that withholds prose has no README for a word to be the name of, so it
    # owes none of them.
    prose_words: list[str] = []
    banned: set[str] = set()
    try:
        if config.get(conn, "prose_sources") != "off":
            prose_words = [r["word"] for r in conn.execute(
                "SELECT word FROM code_lexicon WHERE sources LIKE ? "
                "ORDER BY uses DESC, word", ('%"prose"%',))]
        else:
            # A small lexicon ranks everything into `picked`, prose words
            # included -- the ban has to hold wherever the word got in.
            banned = {r["word"] for r in conn.execute(
                "SELECT word FROM code_lexicon WHERE sources = ?",
                ('["prose"]',))}
    except Exception:                                       # pragma: no cover
        pass
    out = []
    for word in (picked + [k for k in keys if k not in picked]
                 + [w for w in prose_words if w not in picked]):
        if (word in banned or _singular(_slug_of(word)) in defined
                or word in declined or word in abandoned):
            continue
        out.append(word)
    return out


def _define_wakes(conn: sqlite3.Connection) -> list[Wake]:
    # No lexicon, no words to owe: a tree with nothing declared in it, or a
    # database from before the table existed.
    if not conn.execute("SELECT 1 FROM code_lexicon LIMIT 1").fetchone():
        return []
    return [Wake("terminologist", "tick:define", refs=(TERM_PREFIX + w,))
            for w in pending_terms(conn)]


def _has_program(conn: sqlite3.Connection) -> bool:
    """Any grain in a language the index parses. Prose is not a program."""
    from ..onboarding.languages import for_path

    for r in conn.execute("SELECT DISTINCT grain FROM code_index "
                          "WHERE grain_kind = 'path'"):
        name = r["grain"].rsplit("/", 1)[-1]
        if for_path(name) is not None:
            return True
    return False


def onboarding_phase(conn: sqlite3.Connection) -> str:
    """
    Which onboarding phase is current: orient, define, survey, done -- or
    none, when nothing has been onboarded.

    Phases are strict, for the same reason roles survey in order: each one is
    written with the previous one's artefact in front of it, and an account
    written after the words were defined would have been written without
    them. The frontier narrows by situation; this is that narrowing, one level
    up from a session.
    """
    if not conn.execute("SELECT 1 FROM code_index LIMIT 1").fetchone():
        return "none"
    # A project with no program is a finished onboarding, not a small one.
    # Walked live (S0): a one-line README put orient through three sessions
    # of invented scope, the Critic challenged the invention, and one
    # sentence became five items. The index already knows the difference --
    # no grain in a language it parses means there is nothing to orient,
    # define, survey or challenge -- so the phases close mechanically, and
    # one visible record says so instead of a hundred sessions implying it.
    if not _has_program(conn):
        conn.execute(
            "INSERT OR IGNORE INTO survey_records (id, area, outcome, "
            "area_hash) VALUES ('system:@empty', '@empty', 'none_found', '')")
        return "done"
    phases = onboarding_phases(conn)
    if "frame" in phases and _frame_wakes(conn):
        return "frame"
    _repin_after_frame(conn)
    if "orient" in phases and _orient_wakes(conn):
        return "orient"
    if "reconcile" in phases and _reconcile_wakes(conn):
        return "reconcile"
    if "define" in phases and pending_terms(conn):
        return "define"
    if "survey" in phases and _survey_wakes(conn):
        return "survey"
    if "reorient" in phases and _reorient_wakes(conn):
        return "reorient"
    if "boundaries" in phases and _boundary_wakes(conn):
        return "boundaries"
    if "challenge" in phases and _challenge_wakes(conn):
        return "challenge"
    if "blindspots" in phases and _blindspot_wakes(conn):
        return "blindspots"
    return "done"


def tick_orient(conn: sqlite3.Connection) -> list[Wake]:
    return _orient_wakes(conn) if onboarding_phase(conn) == "orient" else []


def tick_reconcile(conn: sqlite3.Connection) -> list[Wake]:
    return _reconcile_wakes(conn) if onboarding_phase(conn) == "reconcile" else []


def tick_define(conn: sqlite3.Connection) -> list[Wake]:
    return _define_wakes(conn) if onboarding_phase(conn) == "define" else []


def survey_order() -> tuple[str, ...]:
    """
    The survey phases, optionally truncated for debugging.

    The three roles already run in strict phases -- Terminologist finishes every
    area before Architect starts -- so stopping after one of them is a filter on
    an order that exists rather than a new one. `ROTA_SURVEY_UNTIL=terminologist`
    runs the first phase and then goes quiescent, which cuts the loop for
    anything being measured on the glossary from a whole onboarding to a third
    of one.

    A debug affordance and nothing else: unset, this is `SURVEY_ORDER`, and a
    name that is not a survey role is ignored rather than obeyed, because a
    typo that silently ran no phases would look exactly like a system with
    nothing to do.
    """
    import os

    until = (os.environ.get("ROTA_SURVEY_UNTIL") or "").strip().lower()
    if until not in SURVEY_ORDER:
        return SURVEY_ORDER
    return SURVEY_ORDER[:SURVEY_ORDER.index(until) + 1]


def tick_survey(conn: sqlite3.Connection) -> list[Wake]:
    """The per-area survey pass, once the program is oriented and its words
    defined. `_survey_wakes` is the pass itself; this is the phase gate."""
    return _survey_wakes(conn) if onboarding_phase(conn) == "survey" else []


def _survey_wakes(conn: sqlite3.Connection) -> list[Wake]:
    """
    Onboarding: one session per elected area, per role, in the order
    Terminologist -> Architect. Terms first, because constraints are written
    in glossary terms. The observed baseline is written before either, over the
    whole program, by `tick_orient`.

    Sessions compound through artefacts, not context: area N's session consults
    its own artefact and sees everything areas 1..N-1 found.

    **Every remaining area is offered, in order, not just the first.** It used to
    return exactly one wake and `break`, which enforced the sequencing by having
    nothing else to pick — and meant one area that could not close stopped
    onboarding entirely. On the first foreign repository `oauth2/rfc6749/endpoints`
    failed to attest three times, was quarantined by the attempt bound, and took
    the seven areas behind it with it: five of twelve surveyed, frontier empty,
    system reporting itself quiescent.

    Ordering is preserved because the list is ordered and the loop takes the
    first it can dispatch. The difference is that a stuck area is now *skipped*
    rather than blocking, which is what the attempt bound was for — a bound that
    withdraws one wake and thereby withdraws six others is not a bound, it is a
    stall with a counter on it.
    """
    # `.` last, everything else alphabetically.
    #
    # It sorts first, so the first glossary session on any repository met the
    # fold-up bucket -- setup files, config, top-level scripts -- before a
    # single domain module, and `glossary.consult` shows every later session
    # what its predecessors wrote. The ANSWER_KEY predicted that the first terms
    # would be plumbing and the runs bore it out.
    #
    # `.` is *what did not belong anywhere else* by construction: `areas.py`
    # folds small directories up into it. So it is the one area whose vocabulary
    # is least likely to be the project's, and it was reliably first.
    areas = [r["area"] for r in conn.execute(
        "SELECT DISTINCT area FROM code_index WHERE area IS NOT NULL "
        "ORDER BY (area = '.'), area"
    ).fetchall()]
    if not areas:
        return []

    # An abandoned area is settled, not outstanding. Without this the role never
    # advances: one area quarantined by the attempt bound stays outstanding
    # forever, so Terminologist never "finishes" and Architect never starts.
    # Eleven of twelve areas surveyed and the frontier went empty.
    #
    # Abandonment being a *terminal* state rather than an invisible hole is the
    # point. It is recorded, it is reported to the principal, and the work behind
    # it carries on — which is what distinguishes a bound from a stall.
    # A pair of role and area. A map of area to role kept one role when both
    # roles gave up on one area, so the other role never finished (fact F20).
    abandoned = {(role, ",".join(refs)) for role, _, refs in
                 map(key_parts, quarantined_keys(conn, kind="tick:survey"))}

    # A record of a tree that is gone is not a record. The survey stamped the
    # area's aggregate content at attest time; when the index no longer
    # aggregates to the same value, the area counts as unread and the same
    # machinery re-fires -- roles, order, bounds, constraint zero's shrink,
    # none of it knows the difference between first read and re-read, which is
    # the point. An empty current aggregate means the index predates content
    # hashes; unknown matches everything, so legacy runs stay quiet until a
    # refresh rebuilds the index and the views have to be re-earned.
    from ..roles.api import area_content_hash

    current = {area: area_content_hash(conn, area) for area in areas}

    def surveyed(area: str, role: str) -> bool:
        row = conn.execute(
            "SELECT area_hash FROM survey_records WHERE area = ? AND id LIKE ? "
            "ORDER BY rowid DESC LIMIT 1", (area, f"{role}:%")).fetchone()
        if row is None:
            return False
        return current[area] == "" or row["area_hash"] == current[area]

    for role in survey_order():
        outstanding = [
            area for area in areas
            if (role, area) not in abandoned and not surveyed(area, role)
        ]
        if outstanding:
            # One role at a time, still: Terminologist finishes every area before
            # Architect starts, because constraints are written in glossary terms.
            return [Wake(role, "tick:survey", refs=(area,)) for area in outstanding]
    return []


def tick_agenda(conn: sqlite3.Connection, principal_present: bool = False) -> list[Wake]:
    """
    On principal presence, with open ledger entries or gates awaiting a verdict,
    wake Liaison to present what is blocked on the principal.

    Presentation, not a gate: the principal may defer indefinitely and keep working.
    What deferral costs is deferred, not waived — open assumptions reappear at
    each of their lineage's gates.
    """
    if not principal_present:
        return []

    # If something is already open to the principal, they can see they are being
    # waited on and there is nothing to add. This is also what makes the tick
    # terminate: presenting an agenda opens a message to the principal, which
    # silences the predicate until it is answered. Without that it fires
    # forever, because Liaison has no verb that could satisfy it.
    # Less any touch note: the principal is not being waited on for one
    # (P4, R7), so it is not the reason to hold the agenda back.
    # An ask held behind the shift question waits, so it holds no agenda
    # back (frame 193's design, 2.F.4).
    from ..roles.principal import held_asks, held_items
    from .lifecycle import touch_notes

    skip = set(touch_notes(conn)) | held_asks(conn)
    awaiting = sum(1 for r in conn.execute(
        "SELECT id FROM messages WHERE status = 'open' AND to_role = 'principal'")
        if r["id"] not in skip)
    if awaiting:
        return []

    # A run database that predates the column reads every row as `default`,
    # as `live_criteria` reads no `retired_by` there (frame 325, pass 1d).
    from .db import _has_column

    kind = "kind" if _has_column(conn, "ledger", "kind") else "'default' AS kind"
    rows = conn.execute(
        f"SELECT id, about_ref, {kind} FROM ledger WHERE status = 'open' "
        "ORDER BY rowid"
    ).fetchall()
    if not rows:
        return []
    # law 6: at the Liaison it is a page, a hold or a note
    # A seat's reply row wakes no page. On night 136 each relay of a ruling
    # left one such row, the agenda fired 13 times after s514, and
    # `annotate` for bg_4 never ran (frame 190's design, 2.4).
    replies = reply_rows(conn)
    # An `other` row is a count line with no number, so it alone makes a
    # page that asks nothing (frame 204's design, section 8, frame 325).
    chosen = [r for r in rows if r["id"] not in replies
              and r["kind"] != "other"]
    # The `other` rows ride on a page that another row wakes, so its count
    # line shows them (frame 325's re-check of bda07c54).
    riders = [r for r in rows if r["id"] not in replies
              and r["kind"] == "other"]
    # A row that reaches only a held or set-aside item waits with it. After
    # m161 closed, 19 rows of the confirm item would have made confirm pages
    # (frame 193's design, 2.F.9, finding 2).
    held = held_items(conn)
    if held:
        from ..roles.principal import _items_reached as _reach

        def waits(row) -> bool:
            items = set(_reach(conn, row["id"]))
            return bool(items) and items <= held

        chosen = [r for r in chosen if not waits(r)]
        rows = [r for r in rows if not waits(r)]
    if not chosen:
        return []
    # law 8: a lineage's assumptions are presented at its gates
    # A page is about one item and carries that item's rows. Night 162's
    # version pages carried 28 rows of the two merged items, and a drop of
    # them changed a version test (frame 316, pass 2). The rows of another
    # item wait for that item's page.
    # The item of the oldest row that no page has shown goes first, so every
    # row ages onto a page before its batch merges. A running item first
    # left the queued item's rows to park unseen (frame 316's review 2,
    # finding 3). Then the running batch's item, then the open requests.
    from ..roles.principal import open_requests
    from .db import refs_of
    from .lifecycle import ledger_items

    reach = {r["id"]: ledger_items(conn, r["id"]) for r in chosen}
    found = set().union(*reach.values())
    if found:
        running = [r["item_id"] for r in conn.execute(
            "SELECT item_id FROM batches WHERE status = 'running' ORDER BY rowid")]
        merged = {r["item_id"] for r in conn.execute(
            "SELECT item_id FROM batches WHERE status = 'merged'")}
        shown: set[str] = set()
        for m in conn.execute("SELECT body_refs FROM messages "
                              "WHERE to_role = 'principal'"):
            shown.update(refs_of(m["body_refs"]))
        order = [i for r in chosen if r["id"] not in shown
                 for i in sorted(reach[r["id"]], key=lambda i: i not in running)
                 if i not in merged]
        order += running + open_requests(conn)
        order += [i for r in chosen for i in sorted(reach[r["id"]])]
        page = next(i for i in order if i in found)
        # A row of no item and no batch has no page of its own, so it rides
        # on this page and is not lost.
        chosen = ([r for r in chosen if page in reach[r["id"]]]
                  + [r for r in chosen if not reach[r["id"]]])

        def on_page(ref: str) -> bool:
            items = ledger_items(conn, ref)
            return not items or page in items

        replies = {ref for ref in replies if on_page(ref)}
        riders = [r for r in riders if on_page(r["id"])]
    # law 14: identity stamps from birth content, never a model's id
    # The wake carries the rows a page may hold, so the Liaison has real ids
    # to copy. clickI night 20 (2026-09-12): 66 open rows, and the Liaison
    # counted its own ids up, l_ab.., l_ac.., l_ad.., none of them rows, five
    # turns running. Which of the rows in front of it lead the page is still
    # the brief's; the ids are the wake's.
    # The reply rows ride after the chosen rows. The door adds the wake's
    # refs to the present, so a ruling on that page closes them (frame
    # 190's design, 2.F, amendment 3).
    from .sandbox import PAGE_ASSUMPTIONS
    first = [r["id"] for r in chosen[:PAGE_ASSUMPTIONS]]
    first += [r["id"] for r in rows
              if r["id"] in replies][:PAGE_ASSUMPTIONS - len(first)]
    first += [r["id"] for r in riders][:PAGE_ASSUMPTIONS - len(first)]
    return [Wake("liaison", "tick:agenda", refs=tuple(first),
                 detail=f"ledger={len(rows)}")]


def reply_rows(conn: sqlite3.Connection) -> set[str]:
    """
    The open ledger rows that are a seat's reply, not an assumption.

    Two kinds, the two rules `api.ledger_log` refuses at write time. The row
    names a message as its `about_ref` (frame 190's design, 2.F, amendment
    7). Or its writer was woken by a relay of a principal verdict, and the
    row is about a ref of that relay (2.3.1, the join of 1.4).
    """
    # The predicate holds the same rule as the door. `_stage_ledger` has
    # other callers, and `challenge_break` and `frame_assign` write rows
    # past the door (frame 190's design, 2.F, amendment 3).
    from .db import refs_of

    out = {r["id"] for r in conn.execute(
        "SELECT l.id FROM ledger l JOIN messages m ON m.id = l.about_ref "
        "WHERE l.status = 'open'")}
    for r in conn.execute(
            "SELECT l.id, l.about_ref, m.body_refs FROM ledger l "
            "JOIN receipts rc ON rc.table_name = 'ledger' AND rc.row_id = l.id "
            "JOIN sessions s ON s.id = rc.session_id "
            "JOIN messages m ON m.id = s.trigger_msg "
            "JOIN messages c ON c.id = m.cause_id "
            "WHERE l.status = 'open' AND m.verb = 'relay' "
            "  AND c.from_role = 'principal' AND c.verb = 'verdict'"):
        if r["about_ref"] in refs_of(r["body_refs"]):
            out.add(r["id"])
    return out


def _reorient_wakes(conn: sqlite3.Connection) -> list[Wake]:
    """
    The account has not been re-read with the vocabulary in hand.

    The bootstrap runs feedforward, so the draft account -- written cold,
    before a single word was defined -- seeds every later phase and is never
    revisited. One session closes the loop: the Vision Keeper re-reads its
    own items with the glossary and the model in front of it, after the
    surveys and before the boundary sessions consume the account. Skipped
    when there was no orientation to revise or no vocabulary to revise it
    with.
    """
    if not conn.execute("SELECT 1 FROM survey_records WHERE area = ?",
                        (PROGRAM,)).fetchone():
        return []
    if not conn.execute("SELECT 1 FROM glossary_terms LIMIT 1").fetchone():
        return []
    if REORIENT in _abandoned(conn, "tick:reorient"):
        return []
    done = conn.execute("SELECT 1 FROM survey_records WHERE area = ?",
                        (REORIENT,)).fetchone()
    return [] if done else [Wake("vision_keeper", "tick:reorient",
                                 refs=(REORIENT,))]


def tick_reorient(conn: sqlite3.Connection) -> list[Wake]:
    return _reorient_wakes(conn) if onboarding_phase(conn) == "reorient" else []


def boundary_subjects(conn: sqlite3.Connection) -> list[str]:
    """
    The files an outside party touches, mechanically enumerated.

    The survey asks its constraint question per *area*, and an area's context
    is source -- so the answers came back at symbol grain ("who imports
    getIntentsFromTFile"), which the guard rightly calls inside, and the
    first measured run held zero of the answer key's two required
    commitments. The commitments live where the outside touches the
    repository: the authoring surface (a data file the code imports and the
    user writes against) and the root manifests (what a registry or platform
    knows this project by). Both are enumerable from the index with no
    judgement; the judgement -- contract, or build furniture? -- stays with
    the session, which may attest `none_found` and often should.
    """
    from ..onboarding.areas import is_attached
    from ..onboarding.lexicon import MANIFESTS

    has_symbols = {r["g"] for r in conn.execute(
        "SELECT DISTINCT substr(grain, 1, instr(grain, '::') - 1) AS g "
        "FROM code_index WHERE grain_kind = 'symbol'")}
    out: list[str] = []
    for r in conn.execute(
            "SELECT grain, fan_in FROM code_index WHERE grain_kind = 'path' "
            "ORDER BY fan_in DESC, grain"):
        rel = r["grain"]
        name = rel.rsplit("/", 1)[-1].lower()
        # A dot-directory's yaml is a tool's configuration -- CI, hooks,
        # issue templates. The commitment such files witness (publishing to
        # a registry, a supported matrix) is stated in the root manifests,
        # which are subjects already; on the first library measured, eight
        # .github yamls filled the cap before pyproject.toml could enter.
        if is_attached(rel) or any(seg.startswith(".") for seg in rel.split("/")[:-1]):
            continue
        if name in MANIFESTS and "/" not in rel:
            out.append(rel)
            continue
        if rel in has_symbols:
            continue
        if name.endswith((".yaml", ".yml", ".toml")) or (
                name.endswith(".json") and int(r["fan_in"] or 0) > 0):
            out.append(rel)
    return out[:8]


def challenge_subjects(conn: sqlite3.Connection) -> list[str]:
    """
    The claims the Critic owes an attempt on, as `<table>:<row id>` refs.

    Sample mode: the load-bearing claims -- constraints (k0 aside: it is
    scaffolding, not a claim) and the account's items -- newest first,
    capped at twelve, because each costs a session and the expensive
    mistakes measured so far were all in these two artefacts. Full adds
    every live glossary sense and model account. Off is off.
    """
    from . import config

    try:
        mode = config.get(conn, "challenge")
    except Exception:
        mode = "sample"
    if mode == "off":
        return []
    subjects: list[str] = []
    for r in conn.execute("SELECT id FROM constraints WHERE id != 'k0' "
                          "ORDER BY rowid DESC"):
        subjects.append(f"constraints:{r['id']}")
    for r in conn.execute("SELECT id FROM items ORDER BY rowid DESC"):
        subjects.append(f"items:{r['id']}")
    if mode == "full":
        for r in conn.execute("SELECT id FROM glossary_terms WHERE "
                              "superseded_by IS NULL ORDER BY rowid DESC"):
            subjects.append(f"glossary_terms:{r['id']}")
        for r in conn.execute("SELECT id FROM model_areas ORDER BY rowid DESC"):
            subjects.append(f"model_areas:{r['id']}")
    return subjects if mode == "full" else subjects[:12]


def _challenge_wakes(conn: sqlite3.Connection) -> list[Wake]:
    """One Critic session per unchallenged load-bearing claim. A database
    from before the table existed gets no wakes, not a crashed frontier."""
    try:
        done = {r["id"] for r in conn.execute("SELECT id FROM challenges")}
    except sqlite3.OperationalError:
        return []
    gone = _abandoned(conn, "tick:challenge")
    return [Wake("critic", "tick:challenge", refs=(CLAIM_PREFIX + ref,))
            for ref in challenge_subjects(conn)
            if ref not in done and CLAIM_PREFIX + ref not in gone]


def tick_challenge(conn: sqlite3.Connection) -> list[Wake]:
    return (_challenge_wakes(conn)
            if onboarding_phase(conn) == "challenge" else [])


def _blindspot_wakes(conn: sqlite3.Connection) -> list[Wake]:
    """
    What the run could not see has not been said.

    Static tripwires catch the assumptions somebody already named; this
    session exists for the rest. The Liaison -- the role that relays to the
    principal -- reads the run's own gaps (unparsed formats, quarantined
    subjects, unchecked prose, glossary dilution) and writes the two or
    three that matter to the ledger. Last, because the gaps of a run are
    only known once the run has run.
    """
    if not conn.execute("SELECT 1 FROM survey_records WHERE area = ?",
                        (PROGRAM,)).fetchone():
        return []
    if BLINDSPOTS in _abandoned(conn, "tick:blindspot"):
        return []
    done = conn.execute("SELECT 1 FROM survey_records WHERE area = ?",
                        (BLINDSPOTS,)).fetchone()
    return [] if done else [Wake("liaison", "tick:blindspot",
                                 refs=(BLINDSPOTS,))]


def tick_blindspot(conn: sqlite3.Connection) -> list[Wake]:
    return (_blindspot_wakes(conn)
            if onboarding_phase(conn) == "blindspots" else [])


def _boundary_wakes(conn: sqlite3.Connection) -> list[Wake]:
    """One Architect session per boundary file, after the areas are surveyed:
    the constraints are written last, with the whole model in front of them."""
    done = {r["area"] for r in conn.execute(
        "SELECT area FROM survey_records WHERE area LIKE ?",
        (SURFACE_PREFIX + "%",))}
    gone = _abandoned(conn, "tick:boundary")
    return [Wake("architect", "tick:boundary", refs=(SURFACE_PREFIX + rel,))
            for rel in boundary_subjects(conn)
            if SURFACE_PREFIX + rel not in done
            and SURFACE_PREFIX + rel not in gone]


def tick_boundary(conn: sqlite3.Connection) -> list[Wake]:
    return _boundary_wakes(conn) if onboarding_phase(conn) == "boundaries" else []


TICKS: tuple[Callable[[sqlite3.Connection], list[Wake]], ...] = (
    tick_round_close,
    tick_signoff,
    tick_slicing,
    tick_criteria,
    tick_batch_start,
    tick_frame,
    tick_orient,
    tick_reconcile,
    tick_define,
    tick_survey,
    tick_reorient,
    tick_boundary,
    tick_challenge,
    tick_blindspot,
)


def predicate_wakes(conn: sqlite3.Connection, principal_present: bool = False) -> list[Wake]:
    """
    Every predicate except the message tips, for callers that want the second
    half on its own. The registry is the definition; `TICKS` above is the set of
    query bodies several of them delegate to.
    """
    from .predicates import REGISTRY, all_wakes

    tips = {id(REGISTRY["message_tips"])}
    return [w for p, w in (
        (p, w) for p in sorted(REGISTRY.values(), key=lambda p: (p.order, p.seq))
        if id(p) not in tips and (principal_present or not p.needs_principal)
        for w in p.fn(conn))]


def frontier(conn: sqlite3.Connection, principal_present: bool = False) -> list[Wake]:
    """
    The ready queue.

    It used to be `open_tips(conn) + predicate_wakes(...)`, which stated the
    frontier in two places — and the tips half was invisible to every check
    written against the predicate half. Open tips are a predicate now, so this
    is one call, ordered fix-before-start.
    """
    from .predicates import all_wakes

    # Abandonment settles *before* the question is asked, not after it.
    #
    # Quarantining is a write, and the wake list used to be computed first. On
    # the pass where an area was abandoned, `all_wakes` still held its wake —
    # `tick_survey` had no way to know it was about to be quarantined — and
    # `quarantine_stalled` then removed it and returned empty. Empty is what
    # quiescence looks like, so onboarding stopped with eleven of twelve areas
    # done by Architect, one abandoned, and Vision Keeper's entire pass of twelve
    # never offered. Calling `frontier` a second time returned thirteen wakes,
    # which is how it was found.
    #
    # Recomputing only when the first pass came back empty was not enough: the
    # frontier is rarely empty, so the same staleness hid behind any other wake
    # that happened to be ready. Marking the overrun up front means `tick_survey`
    # sees the abandonment it is supposed to skip past, in the pass where it
    # happens. The bound was always doing its job; the answer to "what is ready"
    # was computed against the state before it did.
    quarantine_overrun(conn, principal_present)
    # A batch that left its park owes no answer, so its ask closes in the
    # same pass. The Liaison writes the ask, woken by `park_ask` (ruled:
    # Roman, 2026-09-30).
    close_stale_park_asks(conn)
    # An item put aside behind a request comes back when that request is
    # delivered or dropped, in the same pass (frame 193's design, 2.F.4).
    resume_behind(conn)
    # And the other kind of overrun, which that one cannot see: a chain of
    # *distinct* messages whose edge keeps causing itself. `attempts` stays at
    # one along the whole of it, so the bound above is satisfied at every link
    # while the loop runs forever. Marked here for the same reason and in the
    # same pass -- the answer to "what is ready" has to be computed against a
    # world where the abandonment has already happened.
    quarantine_looping(conn)
    # One bound pass over every wake and the quiet park. A second pass over
    # the park alone forgot the counts of wakes that `waiting_filter` holds
    # back (review p1 of frame 330, finding 1).
    quiet = quiet_park(conn)
    bounded = quarantine_stalled(
        conn, all_wakes(conn, principal_present=principal_present) + quiet)
    return _quiet_last(conn, bounded, quiet)


def _quiet_last(conn: sqlite3.Connection, bounded: list[Wake],
                quiet: list[Wake]) -> list[Wake]:
    """The ready wakes of `bounded`, or its quiet park when none is ready.
    The park is told apart by identity, because `preempt` can return an
    equal `do:park` wake beside a challenger."""
    mine = {id(w) for w in quiet}
    ready = waiting_filter(conn, [w for w in bounded if id(w) not in mine])
    return ready or [w for w in bounded if id(w) in mine]


def frontier_readonly(conn: sqlite3.Connection, principal_present: bool = False) -> list[Wake]:
    """Read-only frontier view for the cockpit: no quarantine writes.

    It drops the keys that `quarantine_stalled` drops, by a read, and adds
    the quiet park under the same rule. So the cockpit and the status line
    show what `frontier` does (review p1 of frame 330, finding 3)."""
    from . import config
    from .predicates import all_wakes

    cap = config.get(conn, "tick_attempt_cap")
    stalled = {r["tick_key"] for r in conn.execute(
        "SELECT tick_key FROM tick_attempts WHERE attempts >= ?", (cap,))}
    quiet = quiet_park(conn)
    bounded = [w for w in all_wakes(conn, principal_present=principal_present) + quiet
               if tick_key(w) not in stalled]
    return _quiet_last(conn, bounded, quiet)


def quiet_park(conn: sqlite3.Connection) -> list[Wake]:
    """The `do:park` wake of the running batch with a spent ladder, read
    only when no predicate wakes any seat.

    law 6: a spent ladder goes to the principal. dry1 held its one batch
    `bg_1` as `running` with a spent ladder, and nothing woke, because
    `preempt` parks only beside a challenger (observed: dry1's fourth wall,
    2026-11-01, frame 330). A park while a seat can still move the batch
    loses its recovery: the Tester's new red test lifts the key, as night
    119's s259 did (frame 134). So the park waits for the quiet.

    A wake that `waiting_filter` holds back counts as quiet. Its seat waits
    on an answer, and the answer arrives as a message wake, which the filter
    never holds. A pending answer ends the quiet by its own wake, so the
    held wake alone cannot move the batch (review p1 of frame 330,
    finding 2).
    """
    from .predicates import spent_park

    running = conn.execute(
        "SELECT id FROM batches WHERE status = 'running'").fetchone()
    park = spent_park(conn, running["id"]) if running else None
    return [park] if park else []


def waiting_on(conn: sqlite3.Connection, role: str) -> list[str]:
    """
    Questions this role has asked and not had answered.

    Derived, like everything else in the register: an open outbound message
    with verb `question` is what waiting *is*, and no role has to declare it.

    Every verb of `db.OWED_A_REPLY` waits the same way for the Developer
    alone. A Developer that challenged a test is not woken to build again
    before the Tester answers (frame 204's design, section 3.2).
    """
    from .db import OWED_A_REPLY

    # Frame 204, pass 2c: a wait for every role skips 15 of 23 Architect ticks of night 143.
    verbs = OWED_A_REPLY if role == "developer" else ("question",)
    return [r["id"] for r in conn.execute(
        "SELECT id FROM messages WHERE from_role = ? "
        f"AND verb IN ({','.join('?' * len(verbs))}) "
        "AND status = 'open' ORDER BY seq", (role, *verbs))]


def waiting_filter(conn: sqlite3.Connection, wakes: list[Wake]) -> list[Wake]:
    """
    A role that has asked a question is not offered new work until it is
    answered. The answer still reaches it: message tips are never filtered.

    Waiting had no representation at all, and the cost is visible in the
    predicates. `tests_failing` fires for any batch with a failing run and does
    not care that the Developer is waiting on a term it cannot proceed without,
    so the role is woken with identical state, asks again -- the duplicate guard
    refuses it -- hedges, and repeats until `loop_cap` is spent. Only then does
    `exhausted` fire. The system's answer to "I am waiting" was *spend the
    budget, then escalate*, and most of a week's churn is that loop.

    Suppressing every band except traffic rather than only the wake the question
    blocks, because nothing links a message to the work it came from: messages
    carry no batch, and sessions carry no batch either. It is also the better
    rule on its own terms. A role is single-instance, so one that starts
    something new while holding an open question is holding two contexts at
    once, which is the arrangement this whole design exists to prevent. It asked;
    it waits.

    Nothing is dropped. The obligation stays on the register, the answer wakes
    the asker through its tip, and a question nobody ever answers is what
    quarantine is for.
    """
    blocked = {}
    for w in wakes:
        if w.kind == "message":
            continue                      # the answer must always get through
        if w.role not in blocked:
            blocked[w.role] = waiting_on(conn, w.role)
    return [w for w in wakes
            if w.kind == "message"
            or not (blocked.get(w.role) or rests_on_a_collision(conn, w))]


def rests_on_a_collision(conn: sqlite3.Connection, wake: Wake) -> list[str]:
    """
    Work whose criteria turn on a word with two live senses, and no ruling yet.

    The same principle as waiting, applied to somebody else's obligation rather
    than your own. A Tester woken to encode a criterion that rests on an
    unresolved collision can only guess which sense to encode, and a test
    written from the wrong one passes and pins the wrong promise -- which is
    worse than no test, because it reports as coverage.

    So it is not offered. `term_collision` has already put the word to the
    principal; this stops a second role discovering it independently and
    hedging, which is the "two roles blocked on one ambiguity are two
    discoveries" failure from the other end.

    Narrow on purpose. Only batches, only criteria, only the collision
    obligation -- the general form is "any work resting on any open obligation"
    and there is no general way to say what a wake's work rests on. This one is
    a join that exists: a criterion's `term` refs in the relation.
    """
    from .predicates import REGISTRY

    if not wake.refs or wake.kind == "message":
        return []
    open_terms = sorted({t for w in REGISTRY["term_collision"].fn(conn) for t in w.refs})
    if not open_terms:
        return []

    marks = ", ".join("?" for _ in open_terms)
    return [r["cid"] for r in conn.execute(
        "SELECT DISTINCT c.id AS cid FROM criteria c "
        "JOIN batch_tickets bt ON bt.ticket_id = c.ticket_id "
        "JOIN refs r ON r.src_table = 'criteria' AND r.src_id = c.id "
        "  AND r.kind = 'term' "
        f"WHERE bt.batch_id = ? AND r.target IN ({marks}) ORDER BY c.id",
        (wake.refs[0], *open_terms))]


def is_quiescent(conn: sqlite3.Connection, principal_present: bool = False) -> bool:
    return not frontier(conn, principal_present)


def is_quiescent_readonly(conn: sqlite3.Connection, principal_present: bool = False) -> bool:
    return not frontier_readonly(conn, principal_present)


# ---------------------------------------------------------------------------
# Ordering: a topological sort of Architect's declared dependency facts.
# Not a role — ordering carries no judgement beyond the deps.
# ---------------------------------------------------------------------------

class UnsatisfiableSchedule(RuntimeError):
    """Declared dependency facts contain a cycle. Wakes Architect."""


def _by_number(batch_id: str) -> list:
    # Text order put `b_10` before `b_2` in the fallback (observed: the
    # design review of frame 83, 2026-09-24). The numeric parts sort as numbers.
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", batch_id)]


def schedule_order(conn: sqlite3.Connection) -> list[str]:
    batches = sorted((r["id"] for r in conn.execute("SELECT id FROM batches")),
                     key=_by_number)
    deps: dict[str, set[str]] = {b: set() for b in batches}
    for r in conn.execute("SELECT before_batch, after_batch FROM batch_dep_facts"):
        deps.setdefault(r["after_batch"], set()).add(r["before_batch"])
        deps.setdefault(r["before_batch"], set())
    try:
        return list(TopologicalSorter(deps).static_order())
    except CycleError as exc:
        raise UnsatisfiableSchedule(str(exc)) from exc


def next_batch(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """
    Return the schedulable batches in one order, priority first, then the schedule.

    A batch is schedulable when its item is approved after its last amendment
    and every declared predecessor is merged or abandoned. `tick_batch_start`
    and `preempt` both read this order. Until night 92 they read two orders.
    The start sorted by the schedule alone and offered `b_2`. The preempt
    ranked by priority and deferred `b_2` for `b_3`. The two alternated
    nineteen times (observed: night 92, 2026-09-24). Priority chooses, and
    the schedule constrains (ruled: Roman, 2026-09-24).

    law 9: a reorder ahead of the running batch preempts it
    """
    rows = conn.execute(
        "SELECT b.id AS id, b.status AS status, b.head_commit AS head_commit, "
        "       i.priority AS priority "
        "FROM batches b JOIN items i ON i.id = b.item_id "
        "WHERE b.status IN ('pending','deferred') "
        "  AND i.approval = 'approved' AND i.approval_ver >= i.version "
        # A batch of an item set aside does not start (frame 193's design,
        # 2.F.4).
        + not_parked(conn, "b.item_id") +
        "  AND NOT EXISTS (SELECT 1 FROM batch_dep_facts d "
        "                  JOIN batches p ON p.id = d.before_batch "
        "                  WHERE d.after_batch = b.id "
        "                    AND p.status NOT IN ('merged','abandoned'))"
    ).fetchall()
    # law 6: exhaustion escalates one rung at a time
    # A batch at or past `loop_cap` is on the exhausted path, and a resume
    # cannot end it. Night 93 resumed `b_1` at attempt 11 of 10, nothing woke
    # on it, and three ready batches waited all night (observed: night 93,
    # 2026-09-25). The batch stays deferred, and `exhausted` climbs the ladder.
    # A deferred batch with a quarantined key stays out too, so its siblings
    # start while the principal decides (frame 87, ruled 2026-09-27).
    rows = [r for r in rows if not parked(conn, r["id"])]
    order = schedule_order(conn)
    place = {b: n for n, b in enumerate(order)}
    return sorted(rows, key=lambda r: (-(r["priority"] or 0),
                                       place.get(r["id"], len(order))))


def failing_attempt(conn: sqlite3.Connection, batch_id: str) -> int:
    """The highest attempt among a batch's failing tests, or 0 when none fail."""
    # Each test's latest run only, as `tests_failing` and `exhausted` read it.
    # They skip a test of a retired criterion, so this count skips it too
    # (frame 306, pass 2b).
    row = conn.execute(
        "SELECT MAX(COALESCE(attempt, 1)) AS att FROM latest_runs "
        "WHERE batch_id = ? AND result IN ('fail','error')"
        + live_tests(conn, "test_id"), (batch_id,)).fetchone()
    return int(row["att"] or 0)


def key_parts(key: str) -> tuple[str, str, tuple[str, ...]]:
    """A tick key `role|tick:kind|ref,ref` as its role, its kind and its refs."""
    # `tick_key` writes the key and this function reads it. Ten readers kept
    # their own split before (fact F20, the root-cause audit of 2026-10-27).
    role, kind, refs = ((key or "").split("|", 2) + ["", ""])[:3]
    return role, kind, tuple(r for r in refs.split(",") if r)


CONSTRAINT_ZERO = "tick:constraint_zero"

# `tick_attempts.reported` after the principal ruled on a stopped step that
# names no row. 1 means the Liaison said the step. 2 means he answered it,
# so no later page numbers the step again (frame 354, pass 5).
RULED = 2


def regrouped_key(key: str) -> bool:
    """A reconcile key of several files. The scheduler wakes each file alone,
    so the key stops nothing and no reader calls it given up."""
    # Review p2 of frame 354, finding 1, and review p3, findings 2 and 5:
    # three readers kept the group key as a stall. This is the one test.
    _, kind, refs = key_parts(key)
    return kind == "tick:reconcile" and len(refs) > 1


def quarantined_keys(conn: sqlite3.Connection,
                     subject: str | Iterable[str] | None = None, *,
                     pairs: bool = False, kind: str | None = None,
                     unreported: bool = False, constraint_zero: bool = True,
                     first_come: bool = False, groups: bool = True,
                     ruled: bool = True) -> list[str]:
    """
    The quarantined tick keys, by key or in the order they came.

    `subject` keeps a key about that subject, or about one of a list. A key is
    about a subject when its refs are that subject alone. With `pairs`, a key
    whose refs hold the subject beside another ref is about it too. `kind`
    keeps one kind. `constraint_zero=False` drops the scheduler's own
    onboarding key. The status line and the batch pages drop it. The
    quarantine page shows it as one line, because nothing stops quietly
    (frame 354). `groups=False` drops a reconcile key of several files,
    which the scheduler wakes alone, so no report calls them abandoned.
    `ruled=False` drops a key the principal answered (`RULED`).
    """
    # One reader of `tick_attempts.quarantined`, so "the keys of a batch" has
    # one rule. A key with two refs is about a pair, such as a touch note and
    # its item. The ladder reads the one-ref keys, and a page reads both
    # (fact F20, the root-cause audit of 2026-10-27). One rule for both turns
    # a test red either way. Pairs on the ladder add a key to the parked line
    # of `test_next_batch`. One ref on a page drops the shift row's key in
    # `test_frame312_stuck_review`.
    subjects = ({subject} if isinstance(subject, str)
                else None if subject is None else set(subject))
    out = []
    for r in conn.execute(
            "SELECT tick_key FROM tick_attempts WHERE quarantined = 1"
            + (" AND reported = 0" if unreported else "")
            + ("" if ruled else f" AND reported != {RULED}")
            + (" ORDER BY rowid" if first_come else " ORDER BY tick_key")):
        _, k, refs = key_parts(r["tick_key"])
        if kind is not None and k != kind:
            continue
        if not constraint_zero and k == CONSTRAINT_ZERO:
            continue
        # The scheduler wakes each file of a quarantined reconcile group
        # alone, so the group key abandons nothing. Its report said
        # "1 abandoned" after every file closed (review p2 of frame 354,
        # finding 1).
        if not groups and regrouped_key(r["tick_key"]):
            continue
        if subjects is not None and not (
                set(refs) & subjects if pairs
                else len(refs) == 1 and refs[0] in subjects):
            continue
        out.append(r["tick_key"])
    return out


def rowless_key(conn: sqlite3.Connection, key: str) -> bool:
    """The key is a quarantined tick key, and none of its refs is a batch,
    an item or a ticket. Such a key is its own ref on the quarantine page."""
    # Frame 354: the quarantine wake passed on only the refs a page names
    # (F22), so the constraint zero key gave the Liaison an empty wake.
    from .db import table_of

    if not isinstance(key, str) or "|tick:" not in key:
        return False
    # `quarantined_keys` is the one reader of the flag (fact F20). A group
    # key stops nothing, and a key he answered is no line any more.
    try:
        if key not in quarantined_keys(conn, kind=key_parts(key)[1],
                                       groups=False, ruled=False):
            return False
    except sqlite3.OperationalError:  # a database older than the table
        return False
    return not any(table_of(conn, ref, among=("batches", "items", "tickets"))
                   for ref in key_parts(key)[2])


def given_up(conn: sqlite3.Connection, batch_id: str) -> list[str]:
    """The quarantined keys of the seats' wakes that name this batch alone."""
    # A scheduler key (`-|do:park|b`) is the scheduler's own bound, not a seat.
    return [k for k in quarantined_keys(conn, batch_id)
            if key_parts(k)[0] != "-"]


def stopped_bouncing(conn: sqlite3.Connection, batch_id: str) -> bool:
    """
    The batch stopped bouncing: its failing attempt reached `loop_cap`, or it
    runs and `given_up` lists a key of it, or it runs and `challenged_reds`
    lists a red test of it.

    Law 6 says "Budget exhaustion escalates one rung" and "It is never
    silence". A seat key's cap of 3 can run out below `loop_cap`, and then
    no seat rule read it (frame 330, nights 168 and 169). `given_up` is the
    one record of those keys, for every kind. `exhausted` and `parked` read
    this one check, so the ladder climbs and the park frees the seat. A
    quarantine below the cap spends the ladder for a later `loop_cap` too,
    which is accepted because the park defers the batch and the ladder
    climbs once per batch.
    """
    from . import config

    if failing_attempt(conn, batch_id) >= config.get(conn, "loop_cap"):
        return True
    if _running_given_up(conn, batch_id):
        return True
    # The challenge count is a second bound beside the key. A re-encode
    # still lifts the key, as frame 318 rules (frame 278, pass 2).
    return _running(conn, batch_id) and bool(challenged_reds(conn, batch_id))


def _running(conn: sqlite3.Connection, batch_id: str) -> bool:
    row = conn.execute("SELECT status FROM batches WHERE id = ?",
                       (batch_id,)).fetchone()
    return row is not None and row["status"] == "running"


def challenged_reds(conn: sqlite3.Connection, batch_id: str) -> list[dict]:
    """
    Each red test of the batch that the Developer challenged at least
    `tick_attempt_cap` times, with the count and the Tester's versions.

    A challenge counts when its refs name the test and it is no longer
    open. An open challenge still waits for the Tester's round.
    """
    # Dry1 turn 12: each challenge on `tst_waited` opened its own thread at
    # round 0, and each re-encode reset the `tests_failing` key (frame 318).
    # Six challenges spent no budget, and only `loop_cap` was left. The
    # challenge names its test in its refs, so the messages count the
    # rounds and no new table is needed (frame 278, pass 2).
    from . import config

    cap = config.get(conn, "tick_attempt_cap")
    # The count restarts after the batch's last closed park ask. The ask
    # and the challenge are both messages, so `messages.seq` orders them
    # (review p1 of frame 278, L1; review p2).
    since = conn.execute(
        "SELECT COALESCE(MAX(seq), 0) AS s FROM messages WHERE status != 'open' "
        "AND substr(id, 1, ?) = ? AND substr(id, ?) = ?",
        (len(PARK_ASK), PARK_ASK, _PARK_BATCH_AT + 1, batch_id)).fetchone()["s"]
    # A body_refs that is not a JSON array holds no test id, as in
    # `runner._thread_on_tests`.
    refs = ("CASE WHEN json_valid(m.body_refs) THEN CASE WHEN "
            "json_type(m.body_refs) = 'array' THEN m.body_refs ELSE '[]' END "
            "ELSE '[]' END")
    out = []
    for red in conn.execute(
            "SELECT r.test_id, r.commit_sha, t.path FROM latest_runs r "
            "LEFT JOIN tests t ON t.id = r.test_id "
            "WHERE r.batch_id = ? AND r.result IN ('fail','error')"
            + live_tests(conn, "r.test_id") + " ORDER BY r.test_id",
            (batch_id,)).fetchall():
        n = conn.execute(
            "SELECT COUNT(*) AS n FROM messages m WHERE m.from_role = 'developer' "
            "AND m.to_role = 'tester' AND m.verb = 'challenge' "
            "AND m.status != 'open' AND m.seq > ? AND EXISTS (SELECT 1 FROM "
            "json_each(" + refs + ") j WHERE j.value = ?)",
            (since, red["test_id"])).fetchone()["n"]
        if n < cap:
            continue
        versions = [v["new_version"] for v in conn.execute(
            "SELECT rc.new_version FROM receipts rc "
            "JOIN sessions s ON s.id = rc.session_id "
            "WHERE rc.table_name = 'tests' AND rc.row_id = ? "
            "AND s.role = 'tester' ORDER BY rc.new_version",
            (red["test_id"],))]
        out.append({"test_id": red["test_id"], "path": red["path"],
                    "commit_sha": red["commit_sha"],
                    "challenges": n, "versions": versions})
    return out


def gave_up(conn: sqlite3.Connection, batch_id: str) -> bool:
    """
    The team gave up on the batch at its head: `given_up` lists a key of
    it, or its failing attempt reached `loop_cap` with a red run at its
    head commit, or `challenged_reds` lists a red test run at that commit.
    The count reads any batch status.
    """
    # Review p1 of frame 278, H2: a batch deferred on the count alone was
    # not parked, and `next_batch` chose it again. A key lifts at a new
    # head in `db._lift_quarantines`. The count has no reset, so the run
    # at an older commit ends the park the same way (frame 278, pass 2b).
    if given_up(conn, batch_id):
        return True
    # A park at `loop_cap` owes the page too. Point 3 of the park ruling
    # of 2026-10-08 sends it when a criterion's own test is red. Dry1 turn
    # 14 parked at the cap with no key, so no ask opened (frame 330, pass 3).
    from . import config

    if (failing_attempt(conn, batch_id) >= config.get(conn, "loop_cap")
            and _red_at_head(conn, batch_id)):
        return True
    head = conn.execute("SELECT head_commit FROM batches WHERE id = ?",
                        (batch_id,)).fetchone()
    head = head["head_commit"] if head else None
    return any(head is None or r["commit_sha"] in (None, head)
               for r in challenged_reds(conn, batch_id))


def versions_words(versions: list[int]) -> str:
    """'versions 3, 5 and 6', 'version 3' or 'no new version'."""
    if not versions:
        return "no new version"
    if len(versions) == 1:
        return f"version {versions[0]}"
    return ("versions " + ", ".join(str(v) for v in versions[:-1])
            + f" and {versions[-1]}")


def challenge_words(conn: sqlite3.Connection, batch_id: str) -> str:
    """'the Developer challenged tst_waited 3 times, and the Tester wrote
    versions 3, 5 and 6', one part per test of `challenged_reds`, or ''."""
    return "; ".join(
        f"the Developer challenged {r['test_id']} {r['challenges']} times, "
        f"and the Tester wrote {versions_words(r['versions'])}"
        for r in challenged_reds(conn, batch_id))


def _running_given_up(conn: sqlite3.Connection, batch_id: str) -> list[str]:
    """
    `given_up` for a running batch, less the Liaison's keys, or [] for a
    batch of any other status.
    """
    # A deferred batch's given-up key waits for the principal, and the
    # ladder does not wake on it (frame 87, ruled 2026-09-27).
    row = conn.execute("SELECT status FROM batches WHERE id = ?",
                       (batch_id,)).fetchone()
    if row is None or row["status"] != "running":
        return []
    # A Liaison key is a report about a stopped step, not a step of the
    # batch. A failed report does not stop the batch (frame 330, review of
    # pass 5, finding 3).
    return [k for k in given_up(conn, batch_id) if not k.startswith("liaison|")]


def stop_detail(conn: sqlite3.Connection, batch_id: str) -> str:
    """
    Why a batch below `loop_cap` stopped bouncing, or "" at the cap. A
    running batch with a test in `challenged_reds` adds the challenge
    words after the old text, at the cap too.

    `exhausted` and `preempt`'s park both say it. A batch at the cap keeps
    their old text. Below the cap "attempt 6 of 10" and "past its cap" are
    both false (frame 330, pass 2). The rung reads the detail in its user
    prompt, because `tick:exhausted` is in `runner.DETAIL_SHOWN`. A green
    batch wakes the rung too, so the detail is the one place that names
    the cause (frame 330, review of pass 5, finding 1).
    """
    from . import config
    # The page's words for a quarantined key, so the detail and the page
    # read one table (frame 312, review 1, finding 1).
    from ..roles.principal import _stalled_words

    cap = config.get(conn, "loop_cap")
    tries = failing_attempt(conn, batch_id)
    why = ("" if tries >= cap
           else _stalled_words(conn, _running_given_up(conn, batch_id)))
    # The rung and the park name the looped test beside the old words, so
    # the Architect and then the principal see what looped (frame 278,
    # pass 2, change 3).
    looped = challenge_words(conn, batch_id) if _running(conn, batch_id) else ""
    if not looped:
        return why
    # Below the cap the attempt clause reads as the cause, and it is false
    # there (review p1 of frame 278, L2). At the cap it is the cause.
    if tries >= cap:
        return f"attempt {tries} of {cap}; {looped}"
    return f"{why}; {looped}" if why else looped


# The id prefix of a park ask, then ten hex characters, `_` and the batch id.
# The ask's refs hold the item only, so the batch rides in the id. A prefix
# match on the batch would take `b_1_b_1` for `b_1`, so the batch is read
# at a fixed offset and compared whole (frame 87).
PARK_ASK = "m_park_"
_PARK_BATCH_AT = len(PARK_ASK) + 11          # 0-based start of the batch id


def park_reds(conn: sqlite3.Connection, batch_id: str) -> tuple[list[dict], list[dict]]:
    """
    The batch's red tests, split in two: its own, which a criterion names,
    and the project's. Each is the newest run of one test.
    """
    # The newest run per test, as `failing_attempt` reads it. "Own" is a
    # test with a criterion: night 121's own test of cr_1 is an inherited
    # id, so the id's prefix does not decide (frame 142's design, 2.A).
    rows = conn.execute(
        "SELECT r.test_id, r.output, r.commit_sha, t.path, t.criterion_id FROM latest_runs r "
        "LEFT JOIN tests t ON t.id = r.test_id "
        "WHERE r.batch_id = ? AND r.result IN ('fail','error')"
        + live_tests(conn, "r.test_id") +
        " ORDER BY r.test_id", (batch_id,)).fetchall()
    own =[dict(r) for r in rows if r["criterion_id"] is not None]
    project = [dict(r) for r in rows if r["criterion_id"] is None]
    return own, project


def park_criteria(conn: sqlite3.Connection, batch_id: str) -> list[str]:
    """The batch's criteria in id order: those of its tickets, and those its
    tests name."""
    # A criterion move lifts the park through `batch_tickets`
    # (`db._lift_quarantines`). A test's criterion is read too, because a
    # night fixture can hold the tests without the tickets. The park page
    # lists live rows only, because he dropped a retired line (frame 306,
    # pass 2, finding 2).
    live = live_criteria(conn, "c.retired_by")
    return [r["id"] for r in conn.execute(
        "SELECT c.id FROM criteria c JOIN batch_tickets bt ON bt.ticket_id = c.ticket_id "
        "WHERE bt.batch_id = ?" + live + " UNION "
        "SELECT c.id FROM criteria c JOIN tests t ON t.criterion_id = c.id "
        "WHERE t.batch_id = ?" + live + " ORDER BY 1", (batch_id, batch_id))]


TESTER_MISSING = ("tester", "tick:tests_missing")


def park_untested(conn: sqlite3.Connection, batch_id: str) -> bool:
    """True when the Tester gave up on the batch's tests and no live test of
    the batch names one of its criteria."""
    # dry1's bg_1 parked green on 34 project tests with this key given up.
    # Its park was a note, and a note has no row he can rule (ruled: Roman,
    # 2026-11-01, the park ruling's amendment, point 3's third case).
    if not any(key_parts(k)[:2] == TESTER_MISSING for k in given_up(conn, batch_id)):
        return False
    crits = park_criteria(conn, batch_id)
    if not crits:
        return False
    marks = ",".join("?" * len(crits))
    return conn.execute(
        f"SELECT 1 FROM tests t WHERE t.batch_id = ? AND t.criterion_id IN ({marks})"
        + live_tests(conn, "t.id"), (batch_id, *crits)).fetchone() is None


def park_rows(conn: sqlite3.Connection, batch_id: str) -> list[str]:
    """
    The refs of the park message: the item and the batch's criteria when a
    criterion's own test is red, or when the Tester gave up before any test
    of them existed. Else the batch alone, which is a note.
    """
    # The page goes to the principal when a criterion's own test is red. With
    # the project's tests alone red, the builder broke what worked, and the
    # team files a note (ruled: Roman, 2026-10-08, the park ask is a page
    # with rows, point 3). A batch with no test of its criteria gets the
    # page too, because his ruling on a criterion is its one restart
    # (ruled: Roman, 2026-11-01, the amendment of point 3).
    own, _ = park_reds(conn, batch_id)
    if not own and not park_untested(conn, batch_id):
        return [batch_id]
    row = conn.execute("SELECT item_id FROM batches WHERE id = ?",
                       (batch_id,)).fetchone()
    item = [row["item_id"]] if row and row["item_id"] else []
    return item + park_criteria(conn, batch_id)


def park_owns(conn: sqlite3.Connection, batch_id: str) -> bool:
    """
    A deferred batch with a quarantined key, on an item that `cancel` would
    not take: the park that the park message is about.
    """
    row = conn.execute(
        "SELECT b.status, i.approval, i.approval_ver, i.version FROM batches b "
        "LEFT JOIN items i ON i.id = b.item_id WHERE b.id = ?", (batch_id,)).fetchone()
    if row is None or row["status"] != "deferred" or not gave_up(conn, batch_id):
        return False
    # A contested item's batch goes to `do:cancel`, so nothing is asked.
    # The test is `cancel`'s own, where a NULL compares false.
    unschedulable = ((row["approval"] is not None and row["approval"] != "approved")
                     or (row["approval_ver"] is not None and row["version"] is not None
                         and row["approval_ver"] < row["version"]))
    return not unschedulable


def park_ruling(conn: sqlite3.Connection, message_id: str) -> dict | None:
    """The landed ruling of a closed park page that names every ref of the
    page, or None."""
    import json

    row = conn.execute("SELECT status, body_refs FROM messages WHERE id = ?",
                       (message_id,)).fetchone()
    if row is None or park_ask_batch(message_id) is None or row["status"] == "open":
        return None
    try:
        refs = json.loads(row["body_refs"] or "[]")
    except (TypeError, ValueError):
        return None
    # An empty map names no row. Night 132's three `{}` rulings closed three
    # asks, and each must count as a past park (frame 142's design, 2.F,
    # amendment 2).
    from ..roles.principal import ruled

    # The rows of each landed ruling on the ask (the seam design, 3.1).
    rulings: dict[str, dict] = {}
    for r in ruled(conn, ask=message_id):
        rulings.setdefault(r["ruling_id"], {})[r["ref"]] = r["verdict"]
    for per_item in rulings.values():
        if refs and all(per_item.get(ref) in ("approve", "contest", "revise")
                        for ref in refs):
            return per_item
    return None


def park_message_rests(conn: sqlite3.Connection, message_id: str) -> bool:
    """
    Whether a closed park message ends the asking: a note, or a page whose
    landed ruling names every ref of the page, whatever the verb.
    """
    import json

    row = conn.execute("SELECT status, body_refs FROM messages WHERE id = ?",
                       (message_id,)).fetchone()
    batch = park_ask_batch(message_id)
    if row is None or batch is None or row["status"] == "open":
        return False
    try:
        if batch in json.loads(row["body_refs"] or "[]"):
            return True
    except (TypeError, ValueError):
        return False
    # A contest rests the page too. Its respecify moves the versions and so
    # the id, and the re-park asks then. Before that move the page was the
    # same rows again, night 132's repeated ask (the diff review of b0a2086e,
    # finding 2).
    return park_ruling(conn, message_id) is not None


def park_verdict_page(conn: sqlite3.Connection, message_id: str | None) -> str | None:
    """The park page that a verdict answers, or None for any other message."""
    # One hop, not a walk. A walk up the chain reached an older park page
    # through a clarify or a converse, and keyed a repair on a ruling that
    # was not a park ruling (the delta review of 172b373b, finding 3).
    row = conn.execute("SELECT verb, cause_id FROM messages WHERE id = ?",
                       (message_id,)).fetchone() if message_id else None
    if row is None or row["verb"] != "verdict" or not row["cause_id"]:
        return None
    return row["cause_id"] if park_ask_batch(row["cause_id"]) else None


def park_verdict_criteria(conn: sqlite3.Connection, message_id: str | None) -> list[str]:
    """The criteria that a verdict contests or revises as lines of its page,
    in the verdict's ref order, on a park page and on every other page."""
    import json

    # Every page carries the request's criteria as lines now, so a ruling
    # on a criterion line goes to its writer from any page (frame 190's
    # design, 2.2.7). A criterion that reached the verdict through a
    # contested ledger row's `about_ref` is no line of the page, and no
    # ruling on its words (the diff review of b0a2086e, finding 1).
    if park_verdict_page(conn, message_id) is not None:
        rows = park_verdict_rows(conn, message_id)
    else:
        page = conn.execute(
            "SELECT p.body_refs FROM messages v JOIN messages p ON p.id = v.cause_id "
            "WHERE v.id = ?", (message_id,)).fetchone() if message_id else None
        try:
            lines = set(json.loads(page["body_refs"] or "[]")) if page else set()
        except (TypeError, ValueError):
            lines = set()
        rows = [r for r in verdict_rows(conn, message_id) or [] if r in lines]
    return [r for r in rows
            if conn.execute("SELECT 1 FROM criteria WHERE id = ?", (r,)).fetchone()]


def park_verdict_rows(conn: sqlite3.Connection, message_id: str | None) -> list[str]:
    """The rows of a park page that its verdict contests or revises, the item
    and the criteria, in the verdict's ref order."""
    import json

    if park_verdict_page(conn, message_id) is None:
        return []
    return verdict_rows(conn, message_id) or []


def verdict_rows(conn: sqlite3.Connection, message_id: str | None) -> list[str] | None:
    """The rows that a verdict contests or revises, in the verdict's ref
    order, on any page. None when the message is no verdict."""
    import json

    row = conn.execute("SELECT verb, body_refs FROM messages WHERE id = ?",
                       (message_id,)).fetchone() if message_id else None
    if row is None or row["verb"] != "verdict":
        return None
    from ..roles.principal import verdict_for

    per_item = verdict_for(conn, message_id)
    try:
        refs = json.loads(row["body_refs"] or "[]")
    except (TypeError, ValueError):
        return []
    return [r for r in refs if isinstance(r, str)
            and per_item.get(r) in ("contest", "revise")]


def ruled_rows(conn: sqlite3.Connection, message_id: str | None,
               writes: list | None = None) -> list[str] | None:
    """The rows that his ruling on `message_id` contests or revises, or None
    when no ruling on it is on file or staged.

    The ruling is the verdict's own map, else the newest landed `rulings`
    row of the reply or the verdict, else the `ruled_refs` rows that this
    session stages. The relay split and the mode key read this one record,
    so a converse reply filters as a verdict does. Night 164's m94 carried
    cr_1 to cr_6, the ruling contested cr_2 and cr_6, and the relay keyed
    `relay`, where no call acts (frame 338; composition.md, Records).
    """
    from ..roles.principal import ruled

    found = verdict_rows(conn, message_id)
    if found is not None or not message_id:
        return found
    rows = ruled(conn, reply=message_id)
    if rows:
        return [r["ref"] for r in rows if r["verdict"] in ("contest", "revise")]
    staged = {w[1] for w in writes or [] if w[0] == "rulings"
              and w[2].get("reply_id") in (None, message_id)}
    rows = [w[2] for w in writes or [] if w[0] == "ruled_refs"
            and w[2].get("ruling_id") in staged]
    if not rows:
        return None
    return [r["ref"] for r in rows if r["verdict"] in ("contest", "revise")]


def ruled_criteria(conn: sqlite3.Connection, message_id: str | None) -> list[str]:
    """The criteria that the ruling on `message_id` contests or revises: a
    criterion row itself, or the criterion of a test row.

    The relay split sends a ruled test row as its criterion (frame 213,
    route B), because the principal never rules on a test (ruled: Roman,
    2026-10-08, the park ask is a page with rows, point 2). One hop only: a
    ruling further up rules no row of this relay (the delta review of
    172b373b, finding 3).
    """
    out: list[str] = []
    for r in ruled_rows(conn, message_id) or []:
        if conn.execute("SELECT 1 FROM criteria WHERE id = ?", (r,)).fetchone():
            out.append(r)
        out += [t["criterion_id"] for t in conn.execute(
            "SELECT criterion_id FROM tests WHERE id = ? "
            "AND criterion_id IS NOT NULL", (r,))]
    return out


def guess_relay(conn: sqlite3.Connection, message_id: str | None) -> bool:
    """A relay whose every ref is a code line's key and whose cause is a
    verdict: the principal's correction of the Architect's guess (frame
    298's design, 3.4, point 5)."""
    import json

    row = conn.execute(
        "SELECT m.verb AS verb, m.body_refs AS refs, c.verb AS cause_verb "
        "FROM messages m LEFT JOIN messages c ON c.id = m.cause_id WHERE m.id = ?",
        (message_id,)).fetchone() if message_id else None
    if row is None or row["verb"] != "relay" or row["cause_verb"] != "verdict":
        return False
    try:
        refs = json.loads(row["refs"] or "[]")
    except (TypeError, ValueError):
        return False
    from .db import guess_item

    return bool(refs) and all(guess_item(r) is not None for r in refs)


def batch_relay(conn: sqlite3.Connection, message_id: str | None) -> bool:
    """A relay whose every ref is a batch and whose cause is a verdict: the
    principal's correction of a touch note's prediction."""
    import json

    row = conn.execute(
        "SELECT m.verb AS verb, m.body_refs AS refs, c.verb AS cause_verb "
        "FROM messages m LEFT JOIN messages c ON c.id = m.cause_id WHERE m.id = ?",
        (message_id,)).fetchone() if message_id else None
    if row is None or row["verb"] != "relay" or row["cause_verb"] != "verdict":
        return False
    try:
        refs = json.loads(row["refs"] or "[]")
    except (TypeError, ValueError):
        return False
    return bool(refs) and all(
        isinstance(r, str) and conn.execute(
            "SELECT 1 FROM batches WHERE id = ?", (r,)).fetchone() for r in refs)


def park_criterion_relay(conn: sqlite3.Connection, message_id: str | None) -> bool:
    """
    A relay whose every ref is a criterion, whose cause is a verdict, and
    whose verdict answers a park page or rules each criterion as a line of
    its page: the principal's correction of a criterion row.
    """
    import json

    # A contested ledger row reaches a criterion through `about_ref` in
    # `land`, and a clarify can name one, and neither is a ruling on its
    # words (the diff review of b0a2086e, finding 1: night 133's m327).
    # Every page numbers the request's criteria now (frame 190's design,
    # 2.2.7), so a criterion line ruled on any page counts.
    row = conn.execute("SELECT verb, body_refs, cause_id FROM messages WHERE id = ?",
                       (message_id,)).fetchone() if message_id else None
    if row is None or row["verb"] != "relay":
        return False
    try:
        refs = json.loads(row["body_refs"] or "[]")
    except (TypeError, ValueError):
        return False
    return bool(refs) and all(
        isinstance(r, str) and conn.execute(
            "SELECT 1 FROM criteria WHERE id = ?", (r,)).fetchone() for r in refs
    ) and (park_verdict_page(conn, row["cause_id"]) is not None
           or set(refs) <= set(park_verdict_criteria(conn, row["cause_id"]))
           | set(ruled_criteria(conn, row["cause_id"])))


def _park_versions(conn: sqlite3.Connection, batch_id: str) -> str:
    """The sorted `id:version` pairs of the batch's criteria and own tests."""
    # Pairs, not a sum: a sum can go down when a sibling's start takes an own
    # test with an `inh_` id, and a later bump then repeats an old id (the
    # diff review of b0a2086e, finding 4).
    crit = park_criteria(conn, batch_id)
    marks = ",".join("?" * len(crit))
    pairs = [f"c:{r['id']}:{r['version'] or 0}" for r in conn.execute(
        f"SELECT id, version FROM criteria WHERE id IN ({marks})",
        tuple(crit))] if crit else []
    # Own tests only. The project's tests are taken in again at each batch's
    # start, and a sibling's start moved their rows off this batch (frame
    # 130's wall). That ended the rest of an approved page with nothing of
    # this change moved (observed: the scene `two_batches`, 2026-10-09).
    pairs += [f"t:{r['id']}:{r['version'] or 0}" for r in conn.execute(
        "SELECT id, version FROM tests WHERE batch_id = ? "
        "AND criterion_id IS NOT NULL", (batch_id,))]
    return ",".join(sorted(pairs))


def park_ask_id(conn: sqlite3.Connection, batch_id: str) -> str:
    """
    The id of the one park message a batch's park owes, from its head, its
    keys, the versions of its criteria and tests, and the parks that ended
    before it.
    """
    import hashlib

    row = conn.execute("SELECT head_commit FROM batches WHERE id = ?",
                       (batch_id,)).fetchone()
    head = row["head_commit"] if row else None
    keys = ",".join(given_up(conn, batch_id))
    # A lift with no new head, such as a criterion move, can park again on
    # the same key. Head and keys alone then gave the old id, and no ask
    # opened (observed: frame 87's review of b23d17b, 2026-09-30). A closed
    # ask that did not rest is a past park. A message that rests, a note or
    # a page approved whole, keeps the id, so the park asks nothing more
    # until something moves (ruled: Roman, 2026-10-08, point 5). The `-|do:park|`
    # count does not move on a quarantine park.
    ended = sum(
        1 for r in conn.execute(
            "SELECT id FROM messages WHERE status != 'open' "
            "AND substr(id, 1, ?) = ? AND substr(id, ?) = ?",
            (len(PARK_ASK), PARK_ASK, _PARK_BATCH_AT + 1, batch_id)).fetchall()
        if not park_message_rests(conn, r["id"]))
    # A criterion move or a re-encoded test lifts the park with no new head.
    # The sum moves with it, so a re-park asks again (frame 142's design,
    # 2.F, amendment 2, after frame 87's review of 4a0ab5c).
    versions = _park_versions(conn, batch_id)
    seed = f"{batch_id}|{head}|{keys}|{ended}|{versions}"

    def made(text: str) -> str:
        return f"{PARK_ASK}{hashlib.sha256(text.encode()).hexdigest()[:10]}_{batch_id}"

    # A stored message is the ask only when its shape is the shape the rows
    # give now. dry1's bg_1 held a rested note from before the page rule,
    # so no page reached the seat (ruled: Roman, 2026-11-01, the amendment
    # of point 3; frame 330, pass 2b). The kind salts the id only on a
    # change of shape, so every other park keeps its id.
    mid = made(seed)
    row = conn.execute("SELECT body_refs FROM messages WHERE id = ?", (mid,)).fetchone()
    if row is not None:
        try:
            was_note = batch_id in json.loads(row["body_refs"] or "[]")
        except (TypeError, ValueError):
            was_note = False
        is_note = park_rows(conn, batch_id) == [batch_id]
        if was_note != is_note:
            mid = made(f"{seed}|{'note' if is_note else 'page'}")
    return mid


def park_rests(conn: sqlite3.Connection, batch_id: str) -> bool:
    """Whether the batch's current park message exists, is closed and rests."""
    return park_message_rests(conn, park_ask_id(conn, batch_id))


def park_ask_batch(message_id: str) -> str | None:
    """The batch a park ask is about, or None for any other message."""
    if not message_id.startswith(PARK_ASK) or len(message_id) <= _PARK_BATCH_AT:
        return None
    return message_id[_PARK_BATCH_AT:]


def open_park_ask(conn: sqlite3.Connection, batch_id: str) -> str | None:
    """The batch's open park ask, if one is open."""
    row = conn.execute(
        "SELECT id FROM messages WHERE status = 'open' AND substr(id, 1, ?) = ? "
        "AND substr(id, ?) = ?",
        (len(PARK_ASK), PARK_ASK, _PARK_BATCH_AT + 1, batch_id)).fetchone()
    return row["id"] if row else None


def close_park_asks(conn: sqlite3.Connection, batch_id: str) -> int:
    """Close the open park ask of a batch. Returns how many closed.

    The batch's commit is the landed row, so the ask owes no answer. The
    mark goes through `db.mark_answered`, its one writer (fact F16).
    """
    from .db import mark_answered
    return sum(mark_answered(conn, r["id"]) for r in conn.execute(
        "SELECT id FROM messages WHERE status = 'open' "
        "AND substr(id, 1, ?) = ? AND substr(id, ?) = ?",
        (len(PARK_ASK), PARK_ASK, _PARK_BATCH_AT + 1, batch_id)).fetchall())


def dropped_items(conn: sqlite3.Connection) -> set[str]:
    """The items whose newest park row is a drop, and the items whose
    approval is `dropped`.

    A request whose items he dropped on a page is finished too. Review p2
    of frame 357, finding 2: e_m70 read not finished, so nothing parked
    behind it resumed."""
    ended = {r[0] for r in conn.execute(
        "SELECT id FROM items WHERE approval = 'dropped'")}
    if not _has_parks(conn):
        return ended
    return ended | {r["item_id"] for r in conn.execute(
        "SELECT p.item_id FROM item_parks p WHERE p.kind = 'drop' AND p.rowid = "
        "(SELECT q.rowid FROM item_parks q WHERE q.item_id = p.item_id "
        "ORDER BY q.seq DESC, q.rowid DESC LIMIT 1)")}


def resume_behind(conn: sqlite3.Connection) -> int:
    """
    Resume each item parked behind a request that is now delivered or
    dropped. "Later" means behind the current request, so the item reads as
    it did before the park: its held asks return and its work wakes again.
    One `request` row each, cause the request's message. `land` writes the
    principal's rows, so each row has one writer (frame 193's design, 2.F.4).
    """
    if not _has_parks(conn):
        return 0
    from ..roles.principal import (SHIFT_ASK, _delivered, _request_entries,
                                   _write_park, request_of)

    n = 0
    for p in conn.execute(
            "SELECT p.item_id, p.cause_id FROM item_parks p WHERE p.kind = 'park' "
            "AND p.rowid = (SELECT q.rowid FROM item_parks q WHERE q.item_id = "
            "p.item_id ORDER BY q.seq DESC, q.rowid DESC LIMIT 1)").fetchall():
        # The park's verdict answers a shift question, whose refs name the
        # request's statement, and the statement names the request's entry.
        page = conn.execute(
            "SELECT a.id, a.body_refs FROM messages v JOIN messages a "
            "ON a.id = v.cause_id WHERE v.id = ?", (p["cause_id"],)).fetchone()
        if page is None or not page["id"].startswith(SHIFT_ASK):
            continue
        entries: set[str] = set()
        for ref in json.loads(page["body_refs"] or "[]"):
            row = conn.execute("SELECT span_entry FROM statements WHERE id = ?",
                               (ref,)).fetchone()
            if row is not None:
                entries.add(row["span_entry"])
        if not entries:
            continue
        # ruling: frame 193, Roman 2026-10-10; only the request's work items end the park
        # Only work the request asked for decides it. Night 133's account
        # item cites s1, is never delivered, and held every resume at 0 (the
        # review of 61a0f41d, finding 1).
        # A description is no item of the request: one that cites the new
        # statement ended the park before the work items existed (the
        # review of a1bd448f, finding 1). `request_of` gives it no request.
        cited = [r for r in conn.execute("SELECT id, kind FROM items")
                 if request_of(conn, r["id"]) in entries]
        mine = [r["id"] for r in cited if r["kind"] == "in_scope"]
        # A request with items and no work item asks nothing to deliver, so
        # the park ends. A request with no item yet still waits. B with
        # only out-of-scope items held A for ever (the review of e406e976,
        # finding 2).
        if not cited:
            continue
        aside = dropped_items(conn)
        if not all(_delivered(conn, i) or i in aside for i in mine):
            continue
        request = next((m for m in conn.execute(
            "SELECT id, seq, body_refs FROM messages WHERE from_role = 'principal' "
            "AND cause_id IS NULL AND verb = 'converse' ORDER BY seq")
            if set(_request_entries(conn, m["body_refs"])) & entries), None)
        if request is None:
            continue
        # The row's seq is now, so it is newer than the park it ends.
        now = conn.execute("SELECT COALESCE(MAX(seq), 0) n FROM messages").fetchone()["n"]
        _write_park(conn, p["item_id"], "resume", "request", request["id"], now)
        n += 1
    return n


def close_stale_park_asks(conn: sqlite3.Connection) -> int:
    """
    Close the open park ask of every batch that left the park.

    A commit closes its batch's ask in `db._lift_quarantines`, and a contest
    closes it in `principal.land`. An abandonment by another gate closes
    neither, and an ask about a batch that is gone owes no answer.
    """
    from .db import mark_answered
    n = 0
    for r in conn.execute(
            "SELECT id FROM messages WHERE status = 'open' AND substr(id, 1, ?) = ?",
            (len(PARK_ASK), PARK_ASK)).fetchall():
        batch = park_ask_batch(r["id"])
        row = conn.execute("SELECT status FROM batches WHERE id = ?",
                           (batch,)).fetchone()
        if row is None or row["status"] != "deferred" or not gave_up(conn, batch):
            n += mark_answered(conn, r["id"])
    return n


def parked(conn: sqlite3.Connection, batch_id: str) -> bool:
    """
    A deferred batch the team gave up on, or a batch that stopped bouncing
    whose head commit is the one that failed.
    """
    # law 6: at the Liaison it is a page, a hold or a note
    # A given-up batch put back in the chair waits for the principal (ruled:
    # Roman, 2026-09-27). Night 94 resumed `bg_1` with its `tests_failing` key
    # quarantined, nothing woke on it, and `bg_2` never started (observed:
    # night 94, 2026-09-25). A head commit lifts the key in
    # `db._lift_quarantines`, and that ends the park. A running batch parks
    # through `stopped_bouncing`: at `loop_cap`, or with a key that
    # `given_up` lists (frame 330).
    status = conn.execute("SELECT status FROM batches WHERE id = ?",
                          (batch_id,)).fetchone()
    if status and status["status"] == "deferred" and gave_up(conn, batch_id):
        return True
    if not stopped_bouncing(conn, batch_id):
        return False
    # A head commit lifts every key of a running batch but its
    # `tests_failing` key, so such a key ends its own park, as on the
    # deferred branch. A green batch has no failing run at head (frame 330,
    # pass 5). The harness judges the `tests_failing` key at a new head
    # instead (frame 318), so that key keeps the exit below.
    if any(key_parts(k)[1] != "tick:tests_failing"
           for k in _running_given_up(conn, batch_id)):
        return True
    # A head commit newer than the failing runs is a fix nobody has tested.
    # Only the harness tests it, and the harness tests running batches only.
    # Without this exit the park is for ever (observed: frame 86's pass 2
    # review, 2026-09-25). The ladder is not asked again for the new commit.
    return _red_at_head(conn, batch_id)


def _red_at_head(conn: sqlite3.Connection, batch_id: str) -> bool:
    """A failing latest run of the batch at its head commit."""
    return bool(conn.execute(
        "SELECT 1 FROM latest_runs r JOIN batches b ON b.id = r.batch_id "
        "WHERE r.batch_id = ? AND r.result IN ('fail','error') "
        "AND (b.head_commit IS NULL OR r.commit_sha = b.head_commit)",
        (batch_id,)).fetchone())


def rebuild_schedule(conn: sqlite3.Connection) -> list[str]:
    """Recompute schedule_deps from declared facts. Derived state, no receipts."""
    order = schedule_order(conn)
    conn.execute("DELETE FROM schedule_deps")
    for before, after in zip(order, order[1:]):
        conn.execute(
            "INSERT OR IGNORE INTO schedule_deps (before_batch, after_batch) VALUES (?, ?)",
            (before, after),
        )
    return order


# ---------------------------------------------------------------------------
# Claims — law 6's single-instance property, enforced by the primary key.
# ---------------------------------------------------------------------------

class RoleBusy(RuntimeError):
    """The role already has a live session. Roles are single-instance: this is
    what makes cycle collapse (resume-with-question) possible."""


def claim(conn: sqlite3.Connection, role: str, session_id: str,
          message_id: str | None = None) -> None:
    held = conn.execute("SELECT session_id FROM claims WHERE role = ?", (role,)).fetchone()
    if held:
        raise RoleBusy(f"{role} already claimed by {held['session_id']}")
    conn.execute(
        "INSERT INTO claims (role, session_id, message_id) VALUES (?, ?, ?)",
        (role, session_id, message_id),
    )


def release(conn: sqlite3.Connection, role: str) -> None:
    conn.execute("DELETE FROM claims WHERE role = ?", (role,))


# ---------------------------------------------------------------------------
# Bounded ticks. Law 4 bounds failure, and bounded only messages until a real
# repository found the hole: a survey session that never attested left its
# predicate undrained, so the identical wake was produced again, forever.
#
# The bound is on *dispatch without progress*, not on dispatch. A tick that fires
# repeatedly while work lands is the loop working — Developer bouncing on a red
# harness is exactly that. A key that names no batch resets when the wake stops
# being produced, which is what draining looks like from here. A key that names
# a batch resets when the batch moves. A head commit moves it, and so does a
# moved test or criterion of it. The key keeps its count while its wake is
# absent, until the batch is merged or abandoned. On night 92, absence let two
# rules erase each other's count for nineteen sessions (observed: night 92,
# 2026-09-24).
# ---------------------------------------------------------------------------

def tick_key(wake: "Wake") -> str:
    return f"{wake.role}|{wake.kind}|{','.join(wake.refs)}"


def note_dispatch(conn: sqlite3.Connection, wake: Wake) -> int:
    """Count one dispatch of this exact wake. Returns the new count."""
    # law 4: failure is bounded; past its cap a wake is quarantined
    # Scheduler actions count too, keyed by their refs, so a start and a
    # preempt that alternate reach the cap (observed: night 92, 2026-09-24).
    if not wake.kind.startswith(("tick:", "do:")):
        return 0                      # messages have their own bound already
    # The harness fires once for each new test with no run at the head commit.
    # Three Tester sessions on one commit would reach the cap of its batch key
    # (reasoned: the diff review of frame 83, 2026-09-24).
    if wake.kind == "do:harness":
        return 0
    key = tick_key(wake)
    conn.execute(
        "INSERT INTO tick_attempts (tick_key, attempts) VALUES (?, 1) "
        "ON CONFLICT(tick_key) DO UPDATE SET attempts = attempts + 1", (key,))
    return int(conn.execute(
        "SELECT attempts FROM tick_attempts WHERE tick_key = ?",
        (key,)).fetchone()["attempts"])


def undo_dispatch(conn: sqlite3.Connection, wake: Wake) -> None:
    """Give back the one count `note_dispatch` spent on this wake."""
    # Law 4 bounds the role's failure, and a model with no answer is the
    # instrument's failure. Dry1's m4 and m5 spent their caps on an Ollama
    # timeout (frame 355). The token binds the give-back to this dispatch's
    # own increment, so a wake that no dispatch counted gives back nothing.
    if not wake.counted:
        return
    conn.execute("UPDATE tick_attempts SET attempts = attempts - 1 "
                 "WHERE tick_key = ? AND attempts = ?",
                 (tick_key(wake), wake.counted))


def clear_dispatch(conn: sqlite3.Connection, wake: Wake) -> None:
    """The wake is gone, so whatever it was owed got paid. Forget the count."""
    conn.execute("DELETE FROM tick_attempts WHERE tick_key = ?", (tick_key(wake),))


def edge_repeats(conn: sqlite3.Connection, message_id: str,
                 limit: int = 40) -> int:
    """
    How many times this message's own edge has caused itself.

    Walks `cause_id` backwards and counts the links carrying the same
    `from_role -> to_role : verb`. One means it has not repeated.

    The chain is what nothing was reading. Every bound in this system is per
    message or per tick: `quarantine_overrun` counts `attempts` on one row and
    a fresh reply always has one, the barren guard counts sessions that produce
    nothing and a reply is something, `loop_cap` counts bounces on a batch and a
    loop can happen before a batch exists. Each reply even opens its own thread,
    so nothing counting a thread sees it either.

    `limit` bounds the walk, not the loop -- a malformed chain must not hang the
    scheduler while it is being asked whether something else is stuck.
    """
    row = conn.execute(
        "SELECT cause_id, from_role, to_role, verb FROM messages WHERE id = ?",
        (message_id,)).fetchone()
    if row is None:
        return 0
    edge = (row["from_role"], row["to_role"], row["verb"])

    seen, count, cause = {message_id}, 1, row["cause_id"]
    while cause and len(seen) < limit:
        if cause in seen:
            break                      # a cycle in the causes themselves
        seen.add(cause)
        prev = conn.execute(
            "SELECT cause_id, from_role, to_role, verb FROM messages WHERE id = ?",
            (cause,)).fetchone()
        if prev is None:
            break
        if (prev["from_role"], prev["to_role"], prev["verb"]) == edge:
            count += 1
        cause = prev["cause_id"]
    return count


def quarantine_looping(conn: sqlite3.Connection) -> list[str]:
    """
    Set aside open messages whose edge has caused itself past the cap.

    Two roles handing one thing back and forth is a livelock that looks like
    work from every angle the system had: each session commits, each sends a
    message, each message is new. Measured on a real repository -- Vision Keeper
    reopened, Developer elected, four round trips in fourteen sessions, no batch
    ever formed, still going when the step limit stopped it.

    What is bounded is *repetition*, never length. A question climbing the
    ladder touches several roles once each and is the escalation working; a
    chain that keeps arriving at the same edge is not going anywhere by
    definition, because the state that produced it is the state it produces.

    `loop_cap` is the number, reused rather than invented: it already means
    "bounces between two roles before this escalates", and a second constant for
    one idea is how the two drift.

    Quarantining is the whole action, and it is enough. `quarantined` already
    carries an abandoned message to Liaison and on to the principal, so this is
    a detector for an escalation that existed and could not be reached -- the
    same shape as the livelock guard that was pre-empting it.
    """
    from . import config

    cap = config.get(conn, "loop_cap")
    stopped = []
    for r in conn.execute(
            "SELECT id FROM messages WHERE status = 'open' ORDER BY seq").fetchall():
        if edge_repeats(conn, r["id"]) > cap:
            conn.execute("UPDATE messages SET status = 'quarantined' WHERE id = ?",
                         (r["id"],))
            stopped.append(r["id"])
    return stopped


def deepest_repeat(conn: sqlite3.Connection) -> tuple[int, str, str]:
    """
    The longest self-repeating causal chain currently open: count, edge, message.

    Exactly what `quarantine_looping` computes and throws away, returned instead
    of acted on. The bound it feeds only speaks when it fires, and by then the
    message is quarantined and the interesting part -- watching a chain climb --
    is over.

    That is the difference between the two, and it is the whole reason this
    exists: a livelock looked *healthy* in the session ticker, because every
    line was a different message and every line was new. `reopen -> elect x7`
    while it is happening is the same fact, in time to act on.

    Returns `(0, "", "")` when nothing is open, which is the ordinary case.
    """
    best = (0, "", "")
    for r in conn.execute(
            "SELECT id, from_role, to_role, verb FROM messages "
            "WHERE status = 'open' ORDER BY seq").fetchall():
        n = edge_repeats(conn, r["id"])
        if n > best[0]:
            best = (n, f"{r['from_role']}->{r['to_role']}:{r['verb']}", r["id"])
    return best


def quarantine_overrun(conn: sqlite3.Connection,
                       principal_present: bool = False) -> int:
    """
    Mark everything past the attempt bound that did not drain as abandoned.
    Returns how many.

    Separated from `quarantine_stalled` because the *order* turned out to
    matter. Deciding abandonment after computing what is ready means the
    answer was computed against a world where the area was still outstanding,
    and `tick_survey` sequences roles by exactly that. One area stuck at the
    bound made the whole next role invisible. So this runs before `frontier`
    asks what is ready, and reads the wakes only when a key is at the bound.
    """
    from . import config
    from .predicates import all_wakes

    cap = config.get(conn, "tick_attempt_cap")
    over = [r["tick_key"] for r in conn.execute(
        "SELECT tick_key FROM tick_attempts "
        "WHERE attempts >= ? AND quarantined = 0", (cap,))]
    if not over:
        return 0
    return _quarantine_live(conn, over, all_wakes(
        conn, principal_present=principal_present) + quiet_park(conn))


def _quarantine_live(conn: sqlite3.Connection, keys: Iterable[str],
                     ready: list[Wake]) -> int:
    """Quarantine each key whose wake is still ready. Returns how many."""
    # law 4: the bound is on dispatch without progress. A wake that drained
    # after its dispatch made progress, so its key keeps the count and no
    # quarantine. Dry1 turn 16: s265 resumed bg_1 at the cap, bg_1 ran green
    # and merged, and m144 told him the change could not start.
    live = {tick_key(w) for w in ready}
    stalled = [k for k in keys if k in live]
    conn.executemany("UPDATE tick_attempts SET quarantined = 1 WHERE tick_key = ?",
                     [(k,) for k in stalled])
    return len(stalled)


def quarantine_stalled(conn: sqlite3.Connection, ready: list[Wake]) -> list[Wake]:
    """
    Drop wakes that have been dispatched past the cap without draining, and
    forget counts for wakes that are no longer being produced, except a
    live batch's.

    Abandonment is visible, not silent: `tick_quarantined` reports it, for the
    same reason a quarantined message does. A system that quietly stopped trying
    would report itself finished with the work undone, which is the one failure
    this whole design is arranged against.
    """
    from . import config

    cap = config.get(conn, "tick_attempt_cap")
    live = {tick_key(w) for w in ready}
    status = {r["id"]: r["status"] for r in conn.execute("SELECT id, status FROM batches")}
    for row in conn.execute("SELECT tick_key FROM tick_attempts").fetchall():
        if row["tick_key"] not in live:
            # law 4: failure is bounded; past its cap a wake is quarantined
            # A key that names a batch keeps its count while the batch lives.
            # `running` hid the start's key during its own session, and the
            # preempt's step deleted it, nineteen times on night 92 (observed:
            # night 92, 2026-09-24). A move of the batch resets it instead, in
            # `db._lift_quarantines`.
            named = [b for b in key_parts(row["tick_key"])[2] if b in status]
            if named and not any(status[b] in ("merged", "abandoned") for b in named):
                continue
            # Except an abandoned one, which is absent *because* it was
            # abandoned. `tick_survey` reads this table and stops producing what
            # it finds quarantined, so deleting the row put the wake straight
            # back on the frontier at one attempt -- quarantine erasing its own
            # evidence, three correct rules composing into a cycle.
            #
            # icalendar ran 131 sessions inside it and stopped at the session
            # limit rather than at quiescence, its counter reading `attempts=1`
            # after some hundred and twenty dispatches of that one key.
            #
            # "No longer produced" and "no longer *allowed* to be produced" are
            # indistinguishable from the ready list, and only the first is a
            # reason to drop the debt.
            conn.execute("DELETE FROM tick_attempts WHERE tick_key = ? "
                         "AND quarantined = 0", (row["tick_key"],))

    stalled = {r["tick_key"] for r in conn.execute(
        "SELECT tick_key FROM tick_attempts WHERE attempts >= ?", (cap,))}
    _quarantine_live(conn, stalled, ready)
    return [w for w in ready if tick_key(w) not in stalled]


# ---------------------------------------------------------------------------
# Cascade — receipts wake owners along the refs DAG. No role-to-role messages
# exist anywhere in the cascade; the scheduler walks the DAG and summons owners.
# ---------------------------------------------------------------------------

class UnorderableCascade(RuntimeError):
    """The refs graph has a cycle, so "dependency order" has no meaning."""


def cascade_order(g: graph_mod.Graph | None = None) -> list[str]:
    """
    Artefacts in dependency order, derived from the graph's refs edges.

    Non-cascading refs are excluded. `model -> code` is one: it is a *binding*,
    used for the mechanical intersection that triggers structural review, not a
    path along which a change propagates. Including it closed the cycle
    model -> code -> batches -> model.

    This used to catch `CycleError` and return `sorted(deps)`. The cycle was
    always present, so the documented order in law 9 had never once run — every
    cascade since the system was built fired alphabetically, and a cascade in
    the wrong order looks exactly like one in the right order. A fallback that
    silently changes documented behaviour is worse than the failure it hides.
    """
    g = g or graph_mod.load()
    deps: dict[str, set[str]] = {a: set() for a in g.artefacts}
    for e in g.of_type("refs"):
        if not e.cascade:
            continue
        # `s refs t` means s depends on t: t is resolved first.
        deps.setdefault(e.s, set()).add(e.t)
        deps.setdefault(e.t, set())
    try:
        return list(TopologicalSorter(deps).static_order())
    except CycleError as exc:
        raise UnorderableCascade(
            f"the refs graph has a cycle, so cascade order is undefined: "
            f"{exc.args[1]}. Mark one of those refs `cascade: false` if it is a "
            f"lookup rather than a wake path.") from exc


def cascade_rows(conn: sqlite3.Connection, session_id: str) -> dict[str, list[str]]:
    """
    The rows that rest on what a session wrote, by source table.

    The walk of law 9 on the relation, two hops. The first hop finds the
    rows whose refs name the rows the receipts name: a `statement` ref to
    an amended statement, a `reference` ref to a reference, a `term` ref to
    a term, a `ruling` ref to a ruling. The second hop finds the rows whose
    `term` refs name the glossary rows the first hop found. The view flips
    on its own. This walk names the rows for the owners' wakes.
    """
    from .db import REF_KIND_OF_TABLE

    targets: dict[str, set[str]] = {}
    for r in conn.execute(
            "SELECT DISTINCT table_name, row_id FROM receipts WHERE session_id = ?",
            (session_id,)):
        kind = REF_KIND_OF_TABLE.get(r["table_name"])
        if kind:
            targets.setdefault(kind, set()).add(r["row_id"])

    def hop(kind: str, ids: set[str]) -> list[tuple[str, str]]:
        if not ids:
            return []
        marks = ", ".join("?" for _ in ids)
        return [(r["src_table"], r["src_id"]) for r in conn.execute(
            "SELECT src_table, src_id FROM refs "
            f"WHERE kind = ? AND target IN ({marks})", (kind, *sorted(ids)))]

    found: dict[str, set[str]] = {}
    terms = set(targets.pop("term", set()))
    for kind, ids in targets.items():
        for src_table, src_id in hop(kind, ids):
            found.setdefault(src_table, set()).add(src_id)
            if src_table == "glossary_terms":
                terms.add(src_id)
    for src_table, src_id in hop("term", terms):
        found.setdefault(src_table, set()).add(src_id)
    return {table: sorted(ids) for table, ids in found.items()}


def cascade_wakes(conn: sqlite3.Connection, session_id: str,
                  g: graph_mod.Graph | None = None) -> list[Wake]:
    """
    Given a committed session's receipts, produce the wake order: owners of every
    artefact downstream of what changed, in refs-DAG order, developer never first.

    A wake names its artefact first, then the row ids of that artefact
    from the relation (`cascade_rows`), sorted. One wake per (owner,
    artefact), as before the relation. The artefact order is the graph's.
    """
    from .db import ARTEFACT_OF_TABLE, TABLES_OF_ARTEFACT

    g = g or graph_mod.load()
    # A refs write is receipted under its source row (`db.receipt_of`), so a
    # receipt here always names an owner table and never the relation.
    touched = {
        ARTEFACT_OF_TABLE[r["table_name"]]
        for r in conn.execute(
            "SELECT DISTINCT table_name FROM receipts WHERE session_id = ?", (session_id,)
        )
        if r["table_name"] in ARTEFACT_OF_TABLE
    }
    if not touched:
        return []

    rows = cascade_rows(conn, session_id)
    order = cascade_order(g)
    dependents: dict[str, set[str]] = {a: set() for a in g.artefacts}
    for e in g.of_type("refs"):
        dependents.setdefault(e.t, set()).add(e.s)

    affected: set[str] = set()
    queue = list(touched & set(dependents))
    while queue:
        a = queue.pop()
        for dep in dependents.get(a, ()):
            if dep not in affected:
                affected.add(dep)
                queue.append(dep)

    wakes: list[Wake] = []
    for artefact in order:
        if artefact not in affected:
            continue
        ids = tuple(sorted({
            rid for table in TABLES_OF_ARTEFACT.get(artefact, ())
            for rid in rows.get(table, ())}))
        for owner in sorted(g.writer_of(artefact)):
            w = Wake(owner, "cascade", refs=(artefact, *ids), detail=session_id)
            if w not in wakes:
                wakes.append(w)
    return wakes


# ---------------------------------------------------------------------------
# Checkpoint invalidation — mechanical, by version stamps.
# ---------------------------------------------------------------------------

def sweep_checkpoints(conn: sqlite3.Connection) -> list[str]:
    """Invalidate any checkpoint whose working set has been overtaken."""
    invalidated = []
    for row in conn.execute("SELECT session_id, working_set FROM checkpoints WHERE valid = 1"):
        stamps = json.loads(row["working_set"])
        for table, version in stamps:
            current = conn.execute(
                "SELECT version FROM artefact_versions WHERE table_name = ?", (table,)
            ).fetchone()
            if current and int(current["version"]) > int(version):
                conn.execute(
                    "UPDATE checkpoints SET valid = 0 WHERE session_id = ?",
                    (row["session_id"],),
                )
                invalidated.append(row["session_id"])
                break
    return invalidated


# ---------------------------------------------------------------------------
# Binding intersection — the structural-review trigger, and the filter for
# binding-scoped index reads.
# ---------------------------------------------------------------------------

def constraints_for_grains(conn: sqlite3.Connection, grains: Iterable[str]) -> list[str]:
    """
    Constraints triggered by a diff touching `grains`.

    Fail-safe by construction: a constraint with no bindings is global, and a
    constraint whose bindings no longer resolve is *promoted* to global. Every
    degradation path lands on "always loaded, therefore expensive" rather than
    "filtered out, therefore wrong".
    """
    grains = list(grains)
    hits: set[str] = set()

    for r in conn.execute("SELECT id FROM constraints WHERE is_global = 1"):
        hits.add(r["id"])

    for r in conn.execute(
        "SELECT c.id AS id FROM constraints c "
        "LEFT JOIN constraint_bindings b ON b.constraint_id = c.id "
        "GROUP BY c.id HAVING COUNT(b.grain) = 0"
    ):
        hits.add(r["id"])                                  # unbound = global

    for r in conn.execute(
        "SELECT DISTINCT constraint_id AS id FROM constraint_bindings WHERE resolves = 0"
    ):
        hits.add(r["id"])                                  # unresolvable = global

    if grains:
        placeholders = ", ".join("?" for _ in grains)
        for r in conn.execute(
            f"SELECT DISTINCT constraint_id AS id FROM constraint_bindings "
            f"WHERE resolves = 1 AND grain IN ({placeholders})",
            grains,
        ):
            hits.add(r["id"])

    return sorted(hits)


def constraint_zero_area_coverage(conn: sqlite3.Connection) -> tuple[set[str], set[str]]:
    """Areas surveyed (including none_found) vs areas still under constraint zero."""
    from ..onboarding.boot import coded_areas

    all_areas = set(coded_areas(conn))
    surveyed = {r["area"] for r in conn.execute("SELECT DISTINCT area FROM survey_records")}
    return surveyed, all_areas - surveyed
