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
    rows = conn.execute(
        "SELECT i.id FROM items i "
        "WHERE i.kind = 'in_scope' AND i.approval = 'approved' "
        "  AND i.approval_ver >= i.version "
        "  AND i.id != 'how_it_works' "
        "  AND i.provenance != 'observed' "
        "  AND (i.id NOT IN (SELECT item_id FROM tickets) "
        "       OR i.version > COALESCE((SELECT CAST(value AS INTEGER) FROM config "
        "                                 WHERE key = 'delivered:' || i.id), 0) "
        "          AND NOT EXISTS (SELECT 1 FROM tickets t "
        "                          JOIN batch_tickets bt ON bt.ticket_id = t.id "
        "                          JOIN batches b ON b.id = bt.batch_id "
        "                          WHERE t.item_id = i.id "
        "                            AND b.status NOT IN ('merged', 'abandoned')) "
        "          AND EXISTS (SELECT 1 FROM config WHERE key = 'delivered:' || i.id))"
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
            conn.execute("DELETE FROM tick_attempts WHERE tick_key = ?",
                         (f"vision_keeper|tick:slicing|{r['id']}",))
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
    ).fetchall()
    return [
        Wake("terminologist", "tick:criteria", refs=(r["item_id"],))
        for r in rows
    ]


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
                       "AND wake_kind = 'tick:batch_start' AND wake_refs LIKE ?",
                       (f'%"{r["id"]}"%',)).fetchone()]
        return [Wake("developer", "tick:batch_start", refs=(stalled[0],))] if stalled else []

    candidates = [r["id"] for r in conn.execute(
        "SELECT b.id AS id FROM batches b JOIN items i ON i.id = b.item_id "
        "WHERE b.status IN ('pending','deferred') "
        "  AND i.approval = 'approved' AND i.approval_ver >= i.version "
        "ORDER BY i.priority DESC, b.id"
    ).fetchall()]
    if not candidates:
        return []

    order = schedule_order(conn)
    ranked = sorted(candidates, key=lambda b: order.index(b) if b in order else len(order))
    return [Wake("developer", "tick:batch_start", refs=(ranked[0],))]


def tick_signoff(conn: sqlite3.Connection) -> list[Wake]:
    """
    Draft items with no gate open on them: Vision Keeper submits them for approval.

    Fires per *set* rather than per item, because Signoff presents one document —
    the principal is approving an interpretation, and interpretations are read
    whole. An item already awaiting a verdict is not resubmitted.
    """
    from .lifecycle import touch_notes

    drafts = [r["id"] for r in conn.execute(
        "SELECT id FROM items WHERE approval = 'draft' ORDER BY id")]
    if not drafts:
        return []
    # A touch note is set aside (P4, 2026-09-03): this guard exists so an
    # interpretation is not submitted twice, and a note nobody has to answer
    # left open would otherwise freeze every later signoff behind it.
    pending = conn.execute(
        "SELECT COUNT(*) n FROM messages "
        "WHERE status = 'open' AND verb IN ('submit', 'present')"
    ).fetchone()["n"] - len(touch_notes(conn))
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
ONBOARDING_TICKS = ("tick:frame", "tick:orient", "tick:reconcile",
                    "tick:define", "tick:survey", "tick:reorient",
                    "tick:boundary", "tick:challenge", "tick:blindspot")


def is_area(subject: str | None) -> bool:
    """A path under the checkout, as opposed to `@program` or `@term:x`."""
    return bool(subject) and not str(subject).startswith("@")


def term_of(subject: str | None) -> str:
    return subject[len(TERM_PREFIX):] if subject and subject.startswith(TERM_PREFIX) else ""


SURFACE_PREFIX = "@surface:"


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
    return {
        r["tick_key"].split("|", 2)[2].split(",")[0]
        for r in conn.execute(
            "SELECT tick_key FROM tick_attempts WHERE quarantined = 1 "
            "AND tick_key LIKE ?", (f"%|{kind}|%",))
    }


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
    # One wake per prose file, the README first as `@prose`, then each file
    # under docs/ as `@prose:<path>`. clickI (2026-09-12): 37 prose files
    # under docs/ went unread because the phase read only the README, and a
    # conflict between two sources is a page the principal always sees
    # (DECISIONS.md, "The seat's four pages are one surface"). One file a
    # session, so an 8B reader has the whole file and the account in view.
    abandoned = _abandoned(conn, "tick:reconcile")
    done = {r["area"] for r in conn.execute(
        "SELECT area FROM survey_records WHERE area = ? OR area LIKE ?",
        (PROSE, PROSE + ":%"))}
    wakes = []
    for area in prose_areas(conn):
        if area in abandoned or area in done:
            continue
        wakes.append(Wake("vision_keeper", "tick:reconcile", refs=(area,)))
    return wakes


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
    for r in conn.execute("SELECT text FROM items WHERE provenance = 'observed'"):
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
    abandoned = {
        r["tick_key"].split("|", 2)[2]: r["tick_key"].split("|", 2)[0]
        for r in conn.execute(
            "SELECT tick_key FROM tick_attempts WHERE quarantined = 1 "
            "AND tick_key LIKE '%|tick:survey|%'")
    }

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
            if abandoned.get(area) != role and not surveyed(area, role)
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
    from .lifecycle import touch_notes

    awaiting = conn.execute(
        "SELECT COUNT(*) AS n FROM messages WHERE status = 'open' AND to_role = 'principal'"
    ).fetchone()["n"] - len(touch_notes(conn))
    if awaiting:
        return []

    open_ledger = conn.execute(
        "SELECT COUNT(*) AS n FROM ledger WHERE status = 'open'"
    ).fetchone()["n"]
    if not open_ledger:
        return []
    # The wake carries the rows a page may hold, oldest first, so the
    # Liaison has real ids to copy. clickI night 20 (2026-09-12): 66 open
    # rows, and the Liaison counted its own ids up, l_ab.., l_ac.., l_ad..,
    # none of them rows, five turns running. Which of the rows in front of
    # it lead the page is still the brief's; the ids are the wake's.
    from .sandbox import PAGE_ASSUMPTIONS
    first = tuple(r["id"] for r in conn.execute(
        "SELECT id FROM ledger WHERE status = 'open' ORDER BY rowid LIMIT ?",
        (PAGE_ASSUMPTIONS,)))
    return [Wake("liaison", "tick:agenda", refs=first, detail=f"ledger={open_ledger}")]


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
    quarantine_overrun(conn)
    # And the other kind of overrun, which that one cannot see: a chain of
    # *distinct* messages whose edge keeps causing itself. `attempts` stays at
    # one along the whole of it, so the bound above is satisfied at every link
    # while the loop runs forever. Marked here for the same reason and in the
    # same pass -- the answer to "what is ready" has to be computed against a
    # world where the abandonment has already happened.
    quarantine_looping(conn)
    return waiting_filter(conn, quarantine_stalled(
        conn, all_wakes(conn, principal_present=principal_present)))


def frontier_readonly(conn: sqlite3.Connection, principal_present: bool = False) -> list[Wake]:
    """Read-only frontier view for the cockpit: no quarantine writes."""
    from .predicates import all_wakes

    return waiting_filter(conn, all_wakes(conn, principal_present=principal_present))


def waiting_on(conn: sqlite3.Connection, role: str) -> list[str]:
    """
    Questions this role has asked and not had answered.

    Derived, like everything else in the register: an open outbound message
    with verb `question` is what waiting *is*, and no role has to declare it.
    """
    return [r["id"] for r in conn.execute(
        "SELECT id FROM messages WHERE from_role = ? AND verb = 'question' "
        "AND status = 'open' ORDER BY seq", (role,))]


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
    a join that exists: criteria carry `term_refs`.
    """
    import json

    from .predicates import REGISTRY

    if not wake.refs or wake.kind == "message":
        return []
    open_terms = {t for w in REGISTRY["term_collision"].fn(conn) for t in w.refs}
    if not open_terms:
        return []

    resting = []
    for r in conn.execute(
            "SELECT c.id AS cid, c.term_refs AS refs FROM criteria c "
            "JOIN batch_tickets bt ON bt.ticket_id = c.ticket_id "
            "WHERE bt.batch_id = ?", (wake.refs[0],)):
        try:
            if open_terms & set(json.loads(r["refs"] or "[]")):
                resting.append(r["cid"])
        except (ValueError, TypeError):
            continue
    return resting


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


def schedule_order(conn: sqlite3.Connection) -> list[str]:
    batches = [r["id"] for r in conn.execute("SELECT id FROM batches ORDER BY id")]
    deps: dict[str, set[str]] = {b: set() for b in batches}
    for r in conn.execute("SELECT before_batch, after_batch FROM batch_dep_facts"):
        deps.setdefault(r["after_batch"], set()).add(r["before_batch"])
        deps.setdefault(r["before_batch"], set())
    try:
        return list(TopologicalSorter(deps).static_order())
    except CycleError as exc:
        raise UnsatisfiableSchedule(str(exc)) from exc


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
# harness is exactly that — so the counter resets whenever the wake stops being
# produced, which is what draining looks like from here.
# ---------------------------------------------------------------------------

def tick_key(wake: "Wake") -> str:
    return f"{wake.role}|{wake.kind}|{','.join(wake.refs)}"


def note_dispatch(conn: sqlite3.Connection, wake: Wake) -> int:
    """Count one dispatch of this exact wake. Returns the new count."""
    if not wake.kind.startswith("tick:"):
        return 0                      # messages have their own bound already
    key = tick_key(wake)
    conn.execute(
        "INSERT INTO tick_attempts (tick_key, attempts) VALUES (?, 1) "
        "ON CONFLICT(tick_key) DO UPDATE SET attempts = attempts + 1", (key,))
    return int(conn.execute(
        "SELECT attempts FROM tick_attempts WHERE tick_key = ?",
        (key,)).fetchone()["attempts"])


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


def quarantine_overrun(conn: sqlite3.Connection) -> int:
    """
    Mark everything past the attempt bound as abandoned. Returns how many.

    Separated from `quarantine_stalled` because it needs no wake list — "has
    this been dispatched more than the cap allows" is answered by the counter
    alone — and because the *order* turned out to matter. Deciding abandonment
    after computing what is ready means the answer was computed against a world
    where the area was still outstanding, and `tick_survey` sequences roles by
    exactly that. One area stuck at the bound made the whole next role invisible.
    """
    from . import config

    cur = conn.execute(
        "UPDATE tick_attempts SET quarantined = 1 "
        "WHERE attempts >= ? AND quarantined = 0",
        (config.get(conn, "tick_attempt_cap"),))
    return cur.rowcount or 0


def quarantine_stalled(conn: sqlite3.Connection, ready: list[Wake]) -> list[Wake]:
    """
    Drop wakes that have been dispatched past the cap without draining, and
    forget counts for wakes that are no longer being produced.

    Abandonment is visible, not silent: `tick_quarantined` reports it, for the
    same reason a quarantined message does. A system that quietly stopped trying
    would report itself finished with the work undone, which is the one failure
    this whole design is arranged against.
    """
    from . import config

    cap = config.get(conn, "tick_attempt_cap")
    live = {tick_key(w) for w in ready}
    for row in conn.execute("SELECT tick_key FROM tick_attempts").fetchall():
        if row["tick_key"] not in live:
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
    if stalled:
        conn.execute(
            "UPDATE tick_attempts SET quarantined = 1 WHERE attempts >= ?", (cap,))
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


def cascade_wakes(conn: sqlite3.Connection, session_id: str,
                  g: graph_mod.Graph | None = None) -> list[Wake]:
    """
    Given a committed session's receipts, produce the wake order: owners of every
    artefact downstream of what changed, in refs-DAG order, developer never first.
    """
    from .db import ARTEFACT_OF_TABLE

    g = g or graph_mod.load()
    touched = {
        ARTEFACT_OF_TABLE[r["table_name"]]
        for r in conn.execute(
            "SELECT DISTINCT table_name FROM receipts WHERE session_id = ?", (session_id,)
        )
        if r["table_name"] in ARTEFACT_OF_TABLE
    }
    if not touched:
        return []

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
        for owner in sorted(g.writer_of(artefact)):
            w = Wake(owner, "cascade", refs=(artefact,), detail=session_id)
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
    all_areas = {r["area"] for r in conn.execute(
        "SELECT DISTINCT area FROM code_index WHERE area IS NOT NULL"
    )}
    surveyed = {r["area"] for r in conn.execute("SELECT DISTINCT area FROM survey_records")}
    return surveyed, all_areas - surveyed
