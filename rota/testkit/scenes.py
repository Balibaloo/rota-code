"""
Scenes: wide states that the real loop reaches (frame 144, item 3).

A night database is not a test tier. A scene is the state that a night
reaches, built on every run by the loop of a night: `loop.step`, the crank
that `rota run` turns. No scene is stored as a database (ruled: the holding
session and the Principal, 2026-10-05).

A build is a run of `loop.step` and nothing else (the rule of the review of
2d7cc73, 2026-10-05). The loop pumps the principal, computes the frontier,
performs a scheduler action or picks a wake, counts the dispatch, starts a
batch, runs the session and cascades. A scene never picks a wake. It holds
two scripts, and each answers what the loop asks:

- The seats' script answers a session by the key of the wake that the loop
  dispatched. A key is `scheduler.tick_key` for a tick or an action, and
  `role|verb|refs` for a message. A wake that the script does not answer
  fails the build, with its key and the frontier in the error.
- The principal's script answers an ask by its verb and refs, through the
  `principal` argument of `loop.step`. An ask with no answer is deferred.

The principal also speaks between two steps, through `talk.open_with`, the
intake of the TUI. That is the principal's own act, and not the loop's.

The seams. Each one replaces one thing that a test cannot run, and nothing
else:

- `loop.run_session`, the name that `loop.step` calls, is wrapped for the
  build. The wrapper reads the wake that the loop dispatched and passes the
  seat's lines as the backend. Every other argument goes on unchanged. The
  backend is the one argument that a night gives a real model.
- `provision.ensure_env` is a stub. It lays a venv and runs pip, 8.5 s for
  each batch start (observed: frame 144 pass 5, 2026-10-05). The harness
  then runs the project's tests with rota's own interpreter, which is its
  documented fallback. No scene asserts on the environment.
- The backend that `loop.step` receives names no server, so `note_spill`
  reads no card and writes nothing (`loop._spill_endpoint`).

`config.project_root` is a row, as in `test_arc_seam.py`. It is a fact about
the repository and not a declared setting, and no op writes it.

Each builder returns a `Scene`. The tests in `tests/rota/test_scene_*.py`
build each scene once per module, send the catalogue's wrong calls and the
sweep's right calls through `Sandbox.call`, and never commit a session, so
the scene does not move under them.
"""
from __future__ import annotations

import contextlib
import json
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from ..core import harness, loop, scheduler
from ..core.db import init_db
from ..core.scheduler import Wake
from ..llm.llm import Pins, ScriptedBackend
from ..roles import principal
from . import gitfixture

PINS = Pins(model="scripted", temperature=0.0, num_ctx=4096)
# The steps of a build before it fails as a loop that never reaches its end.
LIMIT = 160


@dataclass
class Session:
    """One session of a seat: its lines, or a function of the scene and the
    wake that returns them, and the notes of the runner it may meet."""
    lines: Any
    allow: tuple[str, ...] = ()


@dataclass
class Scene:
    """A built state: the database, the sample repository and the ids, and
    the two scripts that answer the loop."""
    name: str
    conn: sqlite3.Connection
    repo: gitfixture.SampleRepo
    root: Path
    ids: dict = field(default_factory=dict)
    # The seats' script: a wake's key to the sessions it answers, in order.
    # A key of `role|kind` holds one function that answers every wake of
    # that role and kind.
    seats: dict = field(default_factory=dict)
    # The principal's script: an ask's verb and refs to its answers.
    answers: dict = field(default_factory=dict)
    # A call that a test lands on the loop's pick of its key.
    landing: dict = field(default_factory=dict)

    def close(self) -> None:
        self.conn.close()
        gitfixture.cleanup(self.repo)

    @property
    def steps(self) -> list[str]:
        return self.ids.setdefault("steps", [])


# -- the engine: the loop's own crank ----------------------------------------------

def key_of(conn, wake: Wake) -> str:
    """The key that the scripts answer. A tick or an action has the
    scheduler's own key. A message has its role, its verb and its refs, so
    that the key does not hold a message id."""
    if wake.kind != "message":
        return scheduler.tick_key(wake)
    row = conn.execute("SELECT verb, body_refs FROM messages WHERE id = ?",
                       (wake.message_id,)).fetchone()
    refs = [r for r in json.loads(row["body_refs"] or "[]") if isinstance(r, str)]
    return f"{wake.role}|{row['verb']}|{','.join(refs)}"


def seat(sc: Scene, key: str, *sessions) -> None:
    """Add sessions to the seats' script under `key`. A session is a list of
    lines, a function, or a `Session`."""
    sc.seats.setdefault(key, []).extend(
        s if isinstance(s, Session) else Session(s) for s in sessions)


def every(sc: Scene, role_kind: str, fn: Callable) -> None:
    """Answer every wake of `role|kind` that no exact key answers."""
    sc.seats[role_kind] = fn


def rule(sc: Scene, verb: str, refs: list[str], per_item: dict, text: str = "") -> None:
    """The principal's answer to the ask of `verb` on exactly `refs`."""
    sc.answers.setdefault((verb, tuple(refs)), []).append((per_item, text))


def _frontier(conn) -> list[str]:
    return [f"{key_of(conn, w)} ({w.detail})" if w.detail else key_of(conn, w)
            for w in scheduler.frontier_readonly(conn, True)]


def _session_for(sc: Scene, conn, wake: Wake) -> Session:
    key = key_of(conn, wake)
    if key in sc.landing:
        return sc.landing.pop(key)
    queue = sc.seats.get(key)
    if queue:
        return queue.pop(0)
    any_ = sc.seats.get(f"{wake.role}|{wake.kind}")
    if callable(any_):
        return Session(any_)
    raise AssertionError(f"the scene's script has no answer for {key} "
                         f"(attempt {wake.attempt}, {wake.detail!r}); the frontier: "
                         f"{_frontier(conn)}")


@contextlib.contextmanager
def _seated(sc: Scene):
    """The seam on `loop.run_session`, for the reason in the module's text."""
    real = loop.run_session

    def run(conn, wake, *, backend=None, **kw):
        s = _session_for(sc, conn, wake)
        lines = s.lines(sc, wake) if callable(s.lines) else list(s.lines)
        sc.ids["_allow"] = s.allow
        return real(conn, wake, backend=ScriptedBackend(lines + ["done"]), **kw)

    loop.run_session = run
    try:
        yield
    finally:
        loop.run_session = real


class _Principal:
    """The principal's script, as a `PrincipalBackend`."""
    name = "scene"

    def __init__(self, sc: Scene):
        self.sc = sc

    def respond(self, ask: principal.Ask) -> principal.Answer | None:
        queue = self.sc.answers.get((ask.verb, tuple(ask.refs)))
        if not queue:
            return None
        per_item, text = queue.pop(0)
        self.sc.steps.append(f"principal|{ask.verb}|{','.join(ask.refs)}")
        return principal.Answer("verdict", text=text, per_item=per_item)


class _NoServer:
    """The backend that `loop.step` receives. The seam on `run_session`
    replaces it in every session, so a call here is a session that the seam
    missed. It names no host, so `note_spill` reads no card."""
    name = "no server"

    def complete(self, *a, **kw):
        raise AssertionError("a session reached the backend that names no seat")


def step(sc: Scene) -> loop.Step:
    """One `loop.step`, with the scene's scripts. Fails when the loop is
    quiescent, or a session does not commit, or meets a refusal."""
    conn = sc.conn
    with _no_venv(), _seated(sc):
        sc.ids["_allow"] = ()
        st = loop.step(conn, backend=_NoServer(), pins=PINS, principal=_Principal(sc),
                       principal_present=True)
    conn.commit()
    if st.wake is None:
        raise AssertionError(f"the loop is quiescent: {st.note}; the frontier: "
                             f"{_frontier(conn)}")
    key = key_of(conn, st.wake)
    sc.steps.append(key)
    if st.outcome is None:
        return st
    if not st.outcome.committed:
        raise AssertionError(f"{key} failed: {st.outcome.errors}")
    # A scripted turn that a door refuses is a scene that drifted. The note on
    # the prompt's size is about the 4096 window, and a cut note is the
    # runner's account of a push it shortened. Neither is a door.
    refused = [e for e in st.outcome.errors
               if not e.startswith(("prompt over budget", "cut ", *sc.ids["_allow"]))]
    if refused:
        raise AssertionError(f"{key} met a refusal: {refused}")
    return st


def play(sc: Scene, until: Callable[[sqlite3.Connection], Any], limit: int = LIMIT) -> None:
    """Turn the crank until `until` holds."""
    for _ in range(limit):
        if until(sc.conn):
            return
        step(sc)
    raise AssertionError(f"{sc.name}: no end after {limit} steps; the last: "
                         f"{sc.steps[-8:]}")


def end_frontier(sc: Scene) -> list[str]:
    """The frontier at the scene's end, by key: what the loop would pick from."""
    return [key_of(sc.conn, w) for w in scheduler.frontier_readonly(sc.conn, True)]


@contextlib.contextmanager
def _no_venv():
    """`provision.ensure_env` as a stub, for the reason in the module's text."""
    from ..core import provision
    real = provision.ensure_env
    provision.ensure_env = lambda root, **kw: (None, "scene: no venv")
    try:
        yield
    finally:
        provision.ensure_env = real


def _has(sql: str, *args) -> Callable:
    return lambda conn: conn.execute(sql, args).fetchone() is not None


def ran(batch: str, test: str | None = None, result: str | None = None) -> Callable:
    """The harness ran at the batch's head: one run, or the run of `test`."""
    sql = ("SELECT 1 FROM test_runs r JOIN batches b ON b.id = r.batch_id "
           "AND r.commit_sha = b.head_commit WHERE b.id = ?")
    args: list = [batch]
    if test:
        sql += " AND r.test_id = ?"
        args.append(test)
    if result:
        sql += " AND r.result = ?"
        args.append(result)
    return _has(sql, *args)


def _base(name: str, tmp: Path, bind: bool = False) -> Scene:
    """The sample repository, a database, and the onboarding's survey phase.
    Every night is onboarded. Without an onboarding, a Developer's first
    commit indexes the code, the phase turns to `frame`, and the scheduler
    holds every deliver until the frame is judged."""
    repo = gitfixture.make(tmp, name="scene")
    conn = init_db(tmp / "rota.db")
    conn.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)",
                 (str(repo.root),))
    conn.commit()
    sc = Scene(name, conn, repo, tmp)
    survey(sc, bind)
    return sc


# -- the shared seats ------------------------------------------------------------------

def item(sc: Scene, n: int, priority: int) -> None:
    """The principal's sentence of item `n`, and the seats that carry it to a
    batch `b<n>` with one ticket and one criterion: the Liaison's segment
    and confirm, the three delivers, the Vision Keeper's item, the
    Terminologist's term, the Architect's read of the model, the sign-off
    through the Liaison's present and relay, the Vision Keeper's priority,
    the slicing, the criterion and the grouping. The principal approves the
    confirm and the sign-off."""
    from ..tools.talk import open_with
    sentence, problem, term, sense, ticket, criterion = ITEMS[n]
    conn = sc.conn
    mid = open_with(conn, sentence)
    entry = json.loads(conn.execute("SELECT body_refs FROM messages WHERE id = ?",
                                    (mid,)).fetchone()[0])[0]
    s, i, tk = f"s{n}", f"i{n}", f"tk{n}"
    seat(sc, f"liaison|converse|{entry}", [
        f"TOOL: brief.segment(id='{s}', span_entry='{entry}', span_start=0, "
        f"span_end={len(sentence)}, text='{sentence}')",
        f"TOOL: msg.confirm_principal(refs=['{s}'])",
    ])
    rule(sc, "confirm", [s], {s: "approve"})
    seat(sc, f"liaison|verdict|{s}", [
        f"TOOL: brief.ratify(id='{s}')",
        f"TOOL: msg.deliver_vision_keeper(refs=['{s}'])",
        f"TOOL: msg.deliver_terminologist(refs=['{s}'])",
        f"TOOL: msg.deliver_architect(refs=['{s}'])",
    ])
    seat(sc, f"vision_keeper|deliver|{s}", [
        f"TOOL: problem.assert(id='{i}', text='{problem}', kind='in_scope')"])
    seat(sc, f"terminologist|deliver|{s}", [
        f"TOOL: glossary.amend(term='{term}', sense_short='{sense}', "
        f"sense_body='In billing, {term} means {sense}.')"])
    # The Architect reads its model against the sentence and finds nothing
    # to propose, as most of a night's Architect delivers do.
    seat(sc, f"architect|deliver|{s}", ["TOOL: model.consult()"])
    seat(sc, f"vision_keeper|tick:signoff|{i}", [f"TOOL: msg.submit_liaison(refs=['{i}'])"])
    seat(sc, f"liaison|submit|{i}", [f"TOOL: msg.present_principal(refs=['{i}'])"])
    rule(sc, "present", [i], {i: "approve"})
    seat(sc, f"liaison|verdict|{i}", [f"TOOL: msg.relay_vision_keeper(refs=['{i}'])"])
    seat(sc, f"vision_keeper|relay|{i}", [
        f"TOOL: problem.prioritize(id='{i}', priority={priority})"])
    seat(sc, f"vision_keeper|tick:slicing|{i}", [
        f"TOOL: tickets.slice(id='{tk}', item_id='{i}', text='{ticket}')"])

    def criteria(sc: Scene, wake: Wake) -> list[str]:
        gid = sc.conn.execute("SELECT id FROM glossary_terms WHERE term = ?",
                              (term,)).fetchone()["id"]
        return [f"TOOL: criteria.specify(id='c{n}', ticket_id='{tk}', text='{criterion}', "
                f"term_refs=['{gid}'])"]
    seat(sc, f"terminologist|tick:criteria|{i}", criteria)
    seat(sc, f"architect|tick:grouping|{tk}", [
        f"TOOL: batches.group(id='b{n}', item_id='{i}', ticket_ids=['{tk}'])"])


def annotate(sc: Scene, n: int, paths: list[str], read: bool = True) -> None:
    """The Architect's touch set for batch `b<n>`, and the Liaison's touch
    note, which the principal reads and acknowledges when `read`."""
    b, i = f"b{n}", f"i{n}"
    seat(sc, f"architect|tick:annotate|{b}", [
        f"TOOL: batches.annotate(batch_id={b!r}, paths={paths!r})"])
    seat(sc, f"liaison|tick:touch_note|{b},{i}", [
        f"TOOL: msg.present_principal(refs=[{b!r}, {i!r}])"])
    if read:
        rule(sc, "present", [b, i], {i: "approve"})


def commit(writes: list[tuple[str, str]], message: str) -> list[str]:
    """A Developer session that writes each `(path, text)` whole and commits."""
    return ([f"TOOL: code.write(path={p!r}, text={t!r})" for p, t in writes]
            + [f"TOOL: code.commit(message={message!r})"])


def encode(body: str = None) -> list[str]:
    """The Tester's `tests_missing` session: triage, then one test at the
    root, whose name matches `harness.inherit`'s pattern `test_*.py`."""
    return ["TOOL: tests.triage(criterion_id='c1', verdict='encodable')",
            f"TOOL: tests.encode(id='t1', criterion_id='c1', path={TEST_PATH!r}, "
            f"body={(body or TEST_BODY)!r})"]


def judge(batch: str, result: str = "pass") -> list[str]:
    return [f"TOOL: criteria.load(batch_id={batch!r})",
            f"TOOL: tests.load(batch_id={batch!r})",
            f"TOOL: verdicts.emit(batch_id={batch!r}, result={result!r})"]


# An empty session on a fix wake: the seat's note is the state, a dispatch
# with no drain.
IDLE = Session([], allow=("ended a tick with nothing done",))
# The Liaison's question on a parked b1.
PARK_ASK = ["TOOL: msg.clarify_principal(refs=['i1', 'b1'], "
            "question='b1 failed four times. Change the criterion, or abandon b1?')"]


def worktree(sc: Scene, batch: str) -> Path:
    return Path(sc.conn.execute("SELECT worktree FROM batches WHERE id = ?",
                                (batch,)).fetchone()["worktree"])


# -- the sample's own text, changed by a line --------------------------------------

def sample(path: str) -> str:
    from .samplerepo import FILES
    return FILES[path]


def _charges_red(k: int = 1) -> str:
    """`src/billing/charges.py` with `prorate` off by `k` cents, which turns
    the project's `tests/test_charges.py` red."""
    text = sample("src/billing/charges.py")
    old = "    return round(amount_cents * days_used / days_in_period)\n"
    assert old in text
    return text.replace(old, f"    return round(amount_cents * days_used / days_in_period) + {k}\n")


ITEMS = {
    1: ("prorate a mid-month upgrade", "a mid-month upgrade is prorated",
        "proration", "the share of a charge for the days used",
        "prorate an upgrade",
        "an upgrade of 3000 cents used 10 of 30 days charges 1000 cents"),
    2: ("let people export their invoices", "invoices can be exported",
        "export", "a file of the invoices for finance",
        "export invoices", "an export lists every invoice"),
    3: ("send a receipt after each payment", "a payment sends a receipt",
        "receipt", "the message that confirms a payment",
        "send receipts", "a payment sends one receipt"),
}

# The Developer's module of item 1, right and wrong, and the Tester's test.
UPGRADE = ("from src.billing.charges import prorate\n\n\n"
           "def upgrade_charge(amount_cents, days_used, days_in_period):\n"
           "    return prorate(amount_cents, days_used, days_in_period)\n")
UPGRADE_PATH = "src/billing/upgrade.py"
TEST_PATH = "test_upgrade.py"
TEST_BODY = ("from src.billing.upgrade import upgrade_charge\n\n\n"
             "def test_an_upgrade_charges_the_days_used():\n"
             "    assert upgrade_charge(3000, 10, 30) == 1000\n")
# The Developer's module of item 2.
EXPORT_PATH = "src/billing/export.py"
EXPORT = ("from src.billing.invoices import issue_invoice\n\n\n"
          "def export_invoices(invoices):\n"
          "    return [dict(invoice) for invoice in invoices]\n")


def _upgrade_wrong(k: int) -> str:
    """The module with a charge that is `k` cents too much, so each attempt
    is a new diff and the test stays red."""
    return UPGRADE.replace("days_in_period)\n", f"days_in_period) + {k}\n")


# -- S1: two batches that share the project's tests -----------------------------------

def two_batches(tmp: Path) -> Scene:
    """S1. b1 starts, takes in the project's tests, and its Developer's commit
    turns `tests/test_charges.py` red. The principal's second sentence then
    arrives. In the loop's order, b1's fix wake goes before item 2's
    sign-off: the Developer commits once more and stays red, then ends three
    sessions with nothing done, and the key is quarantined. The Liaison
    reports it. Item 2's sign-off then ranks it above item 1, and the
    preempt defers b1. b2 starts, takes in the project's tests again under
    the same ids (frame 130's wall), and its Developer commits the export.
    The scene ends when the harness has run at b2's head."""
    sc = _base("two_batches", tmp)
    item(sc, 1, 1)
    annotate(sc, 1, ["src/billing/charges.py"])
    seat(sc, "developer|tick:batch_start|b1",
         commit([("src/billing/charges.py", _charges_red())], "prorate the remainder"))
    play(sc, ran("b1"))
    sc.ids["head1"] = sc.conn.execute(
        "SELECT head_commit FROM batches WHERE id = 'b1'").fetchone()[0]
    item(sc, 2, 2)
    seat(sc, "developer|tick:tests_failing|b1",
         commit([("src/billing/charges.py", _charges_red(2))], "round the remainder"),
         IDLE, IDLE, IDLE)
    seat(sc, "liaison|tick:quarantined|b1", ["TOOL: msg.present_principal(refs=['b1'])"])
    rule(sc, "present", ["b1"], {"b1": "approve"})
    # b1 is deferred with a quarantined key, so it is parked, and the loop
    # wakes the Liaison to ask. The principal leaves the ask open.
    seat(sc, "liaison|tick:park_ask|i1,b1", PARK_ASK)
    annotate(sc, 2, [EXPORT_PATH])
    seat(sc, "developer|tick:batch_start|b2",
         commit([(EXPORT_PATH, EXPORT)], "export invoices"))
    play(sc, ran("b2"))
    sc.ids.update(wt1=worktree(sc, "b1"), wt2=worktree(sc, "b2"),
                  charges=harness.inherited_id("tests/test_charges.py"))
    return sc


# -- S2: a merged batch's Tester file is a project test of the next batch ---------

def merged_then_next(tmp: Path) -> Scene:
    """S2. b1 runs the whole path: the Developer's module, the harness, the
    Tester's `test_upgrade.py` at the root, the harness again, a pass verdict
    and the merge, which delivers the test in a commit of its own (click
    night 50). b2 then starts, and `harness.inherit` takes the delivered
    file in as a project test of b2. Item 1 ranks above item 2, so b1
    starts first and nothing preempts it. The scene ends when the harness
    has run at b2's head."""
    sc = _base("merged_then_next", tmp)
    item(sc, 1, 2)
    play(sc, _has("SELECT 1 FROM batches WHERE id = 'b1'"))
    item(sc, 2, 1)
    annotate(sc, 1, [UPGRADE_PATH])
    annotate(sc, 2, [EXPORT_PATH])
    seat(sc, "developer|tick:batch_start|b1",
         commit([(UPGRADE_PATH, UPGRADE)], "charge an upgrade"))
    seat(sc, "tester|tick:tests_missing|b1", encode())
    seat(sc, "critic|tick:review|b1", judge("b1"))
    # Constraint zero binds nothing once every area is surveyed, so it is
    # global and every batch owes a structural review, as on nights 119 to
    # 124. Nights 119 and 121 hold a satisfied finding on it.
    seat(sc, "architect|tick:structural_review|b1", [
        f"TOOL: findings.find(id='f1', batch_id='b1', constraint_id='k0', "
        f"status='satisfied', grain={UPGRADE_PATH!r})"])
    seat(sc, "developer|tick:batch_start|b2",
         commit([(EXPORT_PATH, EXPORT)], "export invoices"))
    play(sc, ran("b2"))
    sc.ids.update(delivered=harness.inherited_id(TEST_PATH))
    return sc


# -- S5: a test at version 2 after an answered challenge -----------------------------

def challenged(tmp: Path) -> Scene:
    """S5. The Tester's first test asserts the full price, the harness is red,
    and the Developer challenges it with the criterion's words and the
    test's. The Tester's challenge wake replaces t1 under its stored id, so
    t1 is at version 2, and the harness is green on the same commit. The
    scene ends at that run."""
    sc = _base("challenged", tmp)
    item(sc, 1, 1)
    annotate(sc, 1, [UPGRADE_PATH])
    seat(sc, "developer|tick:batch_start|b1",
         commit([(UPGRADE_PATH, UPGRADE)], "charge an upgrade"))
    seat(sc, "tester|tick:tests_missing|b1", encode(TEST_BODY.replace("== 1000", "== 3000")))
    seat(sc, "developer|tick:tests_failing|b1", [
        "TOOL: msg.challenge_tester(refs=['c1', 't1'], quotes=["
        "'an upgrade of 3000 cents used 10 of 30 days charges 1000 cents', "
        "'assert upgrade_charge(3000, 10, 30) == 3000'])"])
    seat(sc, "tester|challenge|c1,t1", [
        f"TOOL: tests.encode(id='t1', criterion_id='c1', path={TEST_PATH!r}, "
        f"body={TEST_BODY!r})"])
    play(sc, ran("b1", "t1", "pass"))
    sc.ids.update(challenge=sc.conn.execute(
        "SELECT id FROM messages WHERE verb = 'challenge'").fetchone()["id"])
    return sc


# -- S3 and S4: the park ------------------------------------------------------------

def park(tmp: Path) -> Scene:
    """S3 and S4, one scene. b1 reaches attempt 5 of 10: the harness runs
    after the Developer's first commit, again after the Tester's test, which
    is red, and after each of three more commits, red each time. The
    scheduler's `tests_failing` wake is then dispatched three times with no
    commit, and the next frontier quarantines the key. The Liaison tells the
    principal on the `quarantined` wake. Item 2 arrives and ranks above
    item 1, the preempt defers b1, and the Liaison's `park_ask` wake opens
    the ask, which the principal leaves open. Item 3 then arrives. The
    scene ends when b3's touch note is sent, before the principal reads it,
    and the loop's next pick is b2's start.

    The design named b3 behind b1 by a `batch_dep_facts` row (S4). No op in
    `rota/` writes that table, and nights 119 to 124 hold no row in it
    (observed: the review of 906b765, 2026-10-05). So no night reaches "b3
    behind b1", and the scene holds no such row. What the scene proves for
    S4 is that the park keeps b1 out of `next_batch`."""
    sc = _base("park", tmp)
    item(sc, 1, 1)
    annotate(sc, 1, [UPGRADE_PATH])
    seat(sc, "developer|tick:batch_start|b1",
         commit([(UPGRADE_PATH, _upgrade_wrong(1))], "charge an upgrade"))
    seat(sc, "tester|tick:tests_missing|b1", encode())
    seat(sc, "developer|tick:tests_failing|b1",
         *[commit([(UPGRADE_PATH, _upgrade_wrong(k))], f"charge an upgrade, attempt {k}")
           for k in range(2, 5)], IDLE, IDLE, IDLE)
    seat(sc, "liaison|tick:quarantined|b1", ["TOOL: msg.present_principal(refs=['b1'])"])
    # The principal reads it. A present on a batch alone is acknowledged.
    rule(sc, "present", ["b1"], {"b1": "approve"})
    play(sc, _has("SELECT 1 FROM tick_attempts WHERE reported = 1"))
    item(sc, 2, 2)
    seat(sc, "liaison|tick:park_ask|i1,b1", PARK_ASK)
    annotate(sc, 2, [EXPORT_PATH])
    play(sc, lambda conn: scheduler.open_park_ask(conn, "b1"))
    item(sc, 3, 1)
    # The principal answers in the pump of the step that also picks the next
    # wake, and the next wake is b2's start. So the scene ends with b3's
    # touch note sent and not yet read.
    annotate(sc, 3, ["src/notify/delivery.py"], read=False)
    play(sc, _has("SELECT 1 FROM messages WHERE verb = 'present' "
                  "AND body_refs = '[\"b3\", \"i3\"]'"))
    sc.ids.update(key="developer|tick:tests_failing|b1",
                  ask=scheduler.open_park_ask(sc.conn, "b1"))
    return sc


# -- S7: review with a bound constraint ----------------------------------------------

CONSTRAINT = "a charge is a whole number of cents"
CHARGES = "src/billing/charges.py"


def survey(sc: Scene, bind: bool = False) -> None:
    """Onboarding with the survey phase alone: each area's Terminologist and
    then each area's Architect, as the loop picks them, and constraint zero
    after each survey, as the loop performs it. With `bind`, the Architect
    reads `src/billing/charges.py` and binds the constraint there. Every
    other survey attests none found on a grain of its area.

    The phases are a setting the principal owns (`onboarding_phases`).
    The default runs eight more phases, and none of them can bind a file:
    only a survey or a boundary session reads code and amends the model."""
    from ..core import config
    from ..onboarding import boot
    conn = sc.conn
    boot.onboard(conn, sc.repo.root)
    config.set(conn, "onboarding_phases", "survey")
    conn.commit()

    def none_found(sc: Scene, wake: Wake) -> list[str]:
        area = wake.refs[0]
        if bind and wake.role == "architect" and area == "src/billing":
            return [
                f"TOOL: code.source(path={CHARGES!r})",
                f"TOOL: model.amend(headline={CONSTRAINT!r}, text='Money is stored "
                f"and charged in whole cents, never in fractions.', "
                f"bindings=[{CHARGES!r}])",
                f"TOOL: surveys.attest(outcome='found', citations=[{CHARGES!r}])",
            ]
        grain = sc.conn.execute(
            "SELECT grain FROM code_index WHERE area = ? AND grain_kind = 'path' "
            "ORDER BY grain", (area,)).fetchone()["grain"]
        return [f"TOOL: surveys.attest(outcome='none_found', citations=[{grain!r}])"]
    every(sc, "terminologist|tick:survey", none_found)
    every(sc, "architect|tick:survey", none_found)
    play(sc, lambda conn: scheduler.onboarding_phase(conn) == "done")


def critic(tmp: Path, name: str = "critic") -> Scene:
    """S7 up to the Critic. The Architect's survey binds one constraint to
    `src/billing/charges.py`, and its annotation of b1 names that file. The
    Liaison puts the observed constraint to the principal, who approves it.
    b1's Developer makes `prorate` divide and never round, which violates
    the constraint, and adds the upgrade module. The Tester's test does not
    encode its criterion: it asserts only that the charge is positive. The
    project's tests stay green, because their numbers divide exactly. The
    scene ends when the harness has run t1, and the loop's next pick is
    the Critic's review of b1."""
    sc = _base(name, tmp, bind=True)
    k = sc.conn.execute("SELECT id FROM constraints WHERE headline = ?",
                        (CONSTRAINT,)).fetchone()["id"]
    sc.ids["constraint"] = k
    seat(sc, f"liaison|tick:observed_entries|{k}",
         [f"TOOL: msg.present_principal(refs=[{k!r}])"])
    rule(sc, "present", [k], {k: "approve"})
    seat(sc, f"liaison|verdict|{k}", [f"TOOL: msg.relay_architect(refs=[{k!r}])"])
    seat(sc, f"architect|relay|{k}", [f"TOOL: model.adopt(ids=[{k!r}])"])
    item(sc, 1, 1)
    annotate(sc, 1, [CHARGES, UPGRADE_PATH])
    divides = sample(CHARGES).replace(
        "    return round(amount_cents * days_used / days_in_period)\n",
        "    return amount_cents * days_used / days_in_period\n")
    seat(sc, "developer|tick:batch_start|b1",
         commit([(CHARGES, divides), (UPGRADE_PATH, UPGRADE)], "charge an upgrade"))
    seat(sc, "tester|tick:tests_missing|b1", encode(TEST_BODY.replace(" == 1000\n", " > 0\n")))
    play(sc, ran("b1", "t1"))
    return sc


def review(tmp: Path, sc: Scene | None = None) -> Scene:
    """S7. The scene `critic`, then the Critic passes the batch, as a Critic
    that misses the weak test does. So the scene stops at the Architect's
    structural review. The review is owed because the touch set meets the
    binding. Given a built `critic` scene, the build goes on from it."""
    sc = sc or critic(tmp, "review")
    seat(sc, "critic|tick:review|b1", judge("b1"))
    play(sc, _has("SELECT 1 FROM verdicts WHERE batch_id = 'b1'"))
    return sc


BUILDERS = {"two_batches": two_batches, "merged_then_next": merged_then_next,
            "challenged": challenged, "park": park, "critic": critic, "review": review}
# A scene that goes on from another scene's end. One module builds the chain
# once, so the review costs one build and not two.
AFTER = {"review": "critic"}


def chain(name: str) -> list[str]:
    """The scenes that a build of `name` passes, in order."""
    return chain(AFTER[name]) + [name] if name in AFTER else [name]


def build(name: str, tmp: Path, sc: Scene | None = None) -> Scene:
    """Build `name`, or go on to it from `sc`, the end of the scene before it.
    A session or an answer that the script holds and the loop never asked
    for is a scene that claims a step it did not take, so the build fails."""
    if name in AFTER:
        sc = BUILDERS[name](tmp, sc or build(AFTER[name], tmp))
    else:
        sc = BUILDERS[name](tmp)
    left = {k: len(v) for k, v in sc.seats.items() if isinstance(v, list) and v}
    left.update({f"principal|{v}|{','.join(r)}": len(q) for (v, r), q in sc.answers.items()
                 if q})
    assert not left, f"{name}: the loop never asked for {left}"
    return sc


# -- the catalogue and the sweep ---------------------------------------------------

@dataclass(frozen=True)
class Call:
    """One call on a scene, from the seat that `wake` wakes.

    A wrong call names the door that must refuse it, by the function at the
    top of the door's identity, and the first words of the refusal. A right
    call names neither and must land. `held` names the frame that holds a
    row that today's doors answer wrongly, and the row is a strict xfail.
    `question` names a row that no ruling answers yet: the test sends it
    and reports what today's doors do, and gates nothing. `at` names the
    landing on the second build after which the row is sent, for a state
    that only a landing reaches. `before` holds the calls that the same
    session sends first, such as the triage that an encode needs. An
    argument that holds `DISK` and a path takes that file's text in the
    batch's worktree when it is sent."""
    scene: str
    name: str
    wake: Wake
    op: str
    args: tuple
    door: str = ""
    words: str = ""
    held: str = ""
    before: tuple = ()
    question: str = ""
    at: str = ""

    def __str__(self) -> str:
        return self.name


def _w(role: str, kind: str, batch: str, message: str | None = None) -> Wake:
    if message:
        return Wake(role, "message", message, detail=kind, refs=(batch,))
    return Wake(role, kind, refs=(batch,))


def _encode(id: str, criterion: str, path: str, body: str) -> tuple:
    return (("id", id), ("criterion_id", criterion), ("path", path), ("body", body))


DISK = "<disk>"


def _triage(criterion: str) -> tuple:
    """The Tester's triage, which an encode in the same session needs."""
    return (("tests.triage", (("criterion_id", criterion), ("verdict", "encodable"))),)


_EXPORT_TEST = ("from src.billing.invoices import issue_invoice\n\n\n"
                "def test_an_export_lists_every_invoice():\n"
                "    assert issue_invoice\n")
# The Critic's challenge of t1, with the criterion's words and the test's.
_CHALLENGE = (("refs", ["c1", "t1"]),
              ("quotes", ["an upgrade of 3000 cents used 10 of 30 days charges 1000 cents",
                          "assert upgrade_charge(3000, 10, 30) > 0"]))
_FAIL = (("batch_id", "b1"), ("result", "fail"), ("failed_criterion", "c1"),
         ("reason", "the charge is a fraction of a cent"))
# W146: a top level that loads a name it never binds. The module imports and
# dies with a NameError, and every test of the batch goes red.
_UNBOUND = UPGRADE + "\n\nRATE = upgrade_rate\n"


def catalogue() -> list[Call]:
    """The known wrong calls, each with the scene it runs on."""
    charges = "inh_" + __import__("hashlib").sha1(b"tests/test_charges.py").hexdigest()[:8]
    delivered = "inh_" + __import__("hashlib").sha1(TEST_PATH.encode()).hexdigest()[:8]
    t2 = _w("tester", "tick:tests_missing", "b2")
    challenge = _w("tester", "challenge", "b1", "m_ch")
    return [
        # Frame 135: a project test's id under the Tester's encode. Its
        # removal is the proof of S1 (the design's section 5, item 3).
        Call("two_batches", "the project id of test_charges at its own path", t2,
             "tests.encode", _encode(charges, "c2", "tests/test_charges.py", _EXPORT_TEST),
             "tests_encode", f"{charges} is the id of the project's test",
             before=_triage("c2")),
        Call("two_batches", "the project id of test_charges at a new path", t2,
             "tests.encode", _encode(charges, "c2", "tests/test_export.py", _EXPORT_TEST),
             "tests_encode", f"{charges} is the id of the project's test",
             before=_triage("c2")),
        Call("two_batches", "a top level that loads a name it never binds",
             _w("developer", "tick:batch_start", "b2"), "code.write",
             (("path", UPGRADE_PATH), ("text", _UNBOUND)),
             "_code_write", "", held="frame 146"),
        Call("merged_then_next", "the merged batch's test id", t2, "tests.encode",
             _encode("t1", "c2", "tests/test_export.py", _EXPORT_TEST),
             "tests_encode", "t1 is", before=_triage("c2")),
        Call("merged_then_next", "the project id of the delivered test", t2,
             "tests.encode", _encode(delivered, "c2", TEST_PATH, _EXPORT_TEST),
             "tests_encode", f"{delivered} is the id of the project's test",
             before=_triage("c2")),
        # W138: no door refuses a second test on a criterion that holds a
        # stored test. Frame 138 holds it.
        Call("challenged", "a second id for the challenged criterion", challenge,
             "tests.encode", _encode("t2", "c1", "test_upgrade_two.py", TEST_BODY),
             "tests_encode", "", held="frame 138"),
        # Night 121, s143: the Tester's fix under `<id>_fixed` at a new path,
        # the shape of frame 138 (the review of 906b765, X7).
        Call("challenged", "a fix under a new id at a new path", challenge,
             "tests.encode",
             _encode("t1_fixed", "c1", "test_upgrade_fixed.py", TEST_BODY),
             "tests_encode", "", held="frame 138"),
        # Night 123, s141: a new id at the challenged test's own path. The
        # clash door refuses it (the review of 906b765, X2).
        Call("challenged", "a new id at the challenged test's own path", challenge,
             "tests.encode",
             _encode("t1_fixed", "c1", TEST_PATH, TEST_BODY.replace("1000", "1000 ")),
             "tests_encode", f"{TEST_PATH} is t1's file, and t1 is the test of this "
                             f"same criterion"),
        # The replace under the stored id at a new path. The harness deletes
        # no file, so the old one would stay on disk (the review of 2d7cc73,
        # the removal `A_stored_path`).
        Call("challenged", "the stored id at a new path", challenge, "tests.encode",
             _encode("t1", "c1", "test_upgrade_moved.py", TEST_BODY),
             "tests_encode", f"t1 is stored at {TEST_PATH}"),
        Call("critic", "a fail verdict before the claim that its test encodes",
             _w("critic", "tick:review", "b1"), "verdicts.emit",
             (("batch_id", "b1"), ("result", "fail"), ("failed_criterion", "c1")),
             "verdicts_emit", "a fail on c1 stands on its test actually encoding it"),
        # The Critic challenges the test and fails the batch in one session.
        Call("critic", "a fail verdict after a challenge in the same session",
             _w("critic", "tick:review", "b1"), "verdicts.emit", _FAIL,
             "verdicts_emit", "you have already challenged the tester this session",
             before=(("msg.challenge_tester", _CHALLENGE),
                     ("verdicts.claim_encodes", (("criterion_id", "c1"), ("encodes", True))))),
        # Night 120, and the review of 2d7cc73: a Critic's session fails the
        # batch while the same Critic's challenge, sent in an earlier
        # session, is open. Today the fail lands. No ruling says whether a
        # door must refuse it, so the row is a question and not a strict
        # xfail. The state is on the review's second build, after the
        # Critic's challenge lands and before the Tester answers it.
        Call("review", "a fail verdict while the same Critic's challenge is open",
             _w("critic", "tick:review", "b1"), "verdicts.emit", _FAIL,
             before=(("verdicts.claim_encodes", (("criterion_id", "c1"), ("encodes", True))),),
             question="may a Critic fail a batch on a criterion while its own "
                      "challenge of that criterion's test is open?",
             at="the Critic's claim that the test does not encode c1, and its challenge"),
        Call("review", "a finding on a constraint that does not exist",
             _w("architect", "tick:structural_review", "b1"), "findings.find",
             (("id", "f1"), ("batch_id", "b1"), ("constraint_id", "k_none"),
              ("status", "violated"), ("grain", CHARGES)), "findings_find",
             "no constraints row has id="),
        # Night 65: a violated finding on a file that the diff never touched
        # (the review of 2d7cc73, the removal `A_diff_touch`).
        Call("review", "a violated finding on a file the diff does not touch",
             _w("architect", "tick:structural_review", "b1"), "findings.find",
             (("id", "f1"), ("batch_id", "b1"), ("constraint_id", CONSTRAINT_ID),
              ("status", "violated"), ("grain", "src/billing/invoices.py")),
             "findings_find", "the batch's diff does not touch 'src/billing/invoices.py'"),
    ]


def sweep() -> list[Call]:
    """The right calls. Each must land (the design's change 7, and S7's
    right calls of change 5)."""
    out = []
    t2 = _w("tester", "tick:tests_missing", "b2")
    d2 = _w("developer", "tick:batch_start", "b2")
    from .samplerepo import FILES
    # The literals that a project test chooses and the criterion does not
    # say. A right session logs them first, as the literal door names.
    owed = {"tests/test_templates.py": "Welcome, Ada. and welcome and Ada"}
    for n, path in enumerate(sorted(p for p in FILES if p.startswith("tests/"))):
        log = (("ledger.log", (("about_ref", "c2"), ("about_table", "criteria"),
                               ("assumption", f"the test assumes {owed[path]} where "
                                              f"the material is silent"))),) if path in owed else ()
        out.append(Call("two_batches", f"the project test {path} as an encode", t2,
                        "tests.encode", _encode(f"sw{n}", "c2",
                                                path.replace("tests/test_", "tests/test_sw_"),
                                                DISK + path), before=_triage("c2") + log))
    # A module that does not parse in the sample, such as the planted
    # `src/auth/accounts.py`, has no right write that keeps it.
    for path in sorted(p for p in FILES if p.endswith(".py") and p.startswith("src/")
                       and _parses(FILES[p])):
        out.append(Call("two_batches", f"{path} whole with a comment", d2, "code.write",
                        (("path", path), ("text", "# a comment\n" + DISK + path))))
        out.append(Call("two_batches", f"{path} a span of one comment line", d2,
                        "code.write", (("path", path), ("text", "# a comment\n"),
                                       ("start", 0), ("end", 0))))
    both = _CHALLENGE
    critic = _w("critic", "tick:review", "b1")
    # The Developer's challenge that names both sides is not a row: its
    # `tests_failing` wake needs a red harness, and S5's build lands that
    # call through a whole session.
    out += [
        # The test does not encode c1, so the Critic's right answer is the
        # claim of False and a challenge, and a fail on the code is not.
        Call("critic", "the Critic's claim that the test does not encode c1, and its "
                       "challenge", critic, "msg.challenge_tester", both,
             before=(("verdicts.claim_encodes", (("criterion_id", "c1"),
                                                 ("encodes", False))),)),
        Call("critic", "the Critic's fail verdict after a claim of True", critic,
             "verdicts.emit",
             (("batch_id", "b1"), ("result", "fail"), ("failed_criterion", "c1"),
              ("reason", "the charge is a fraction of a cent")),
             before=(("verdicts.claim_encodes", (("criterion_id", "c1"),
                                                 ("encodes", True))),)),
        Call("review", "the Architect's violated finding",
             _w("architect", "tick:structural_review", "b1"), "findings.find",
             (("id", "f1"), ("batch_id", "b1"), ("constraint_id", CONSTRAINT_ID),
              ("status", "violated"), ("grain", CHARGES))),
    ]
    return out


CONSTRAINT_ID = "a_charge_is_a_whole_number_of_cents"


def _parses(text: str) -> bool:
    import ast
    try:
        ast.parse(text)
    except SyntaxError:
        return False
    return True


def sandbox_for(sc: Scene, call: Call):
    """The sandbox that the call's wake gives its seat, as the runner
    builds it."""
    from ..core.runner import session_sandbox
    batch = call.wake.refs[0] if call.wake.refs else None
    return session_sandbox(sc.conn, _real_wake(sc, call.wake), batch_id=batch)


def _real_wake(sc: Scene, wake: Wake) -> Wake:
    """The wake with the scene's own message id where the call names `m_ch`."""
    if wake.kind == "message" and wake.message_id == "m_ch":
        return Wake(wake.role, "message", sc.ids["challenge"], detail=wake.detail,
                    refs=wake.refs)
    return wake


def _root(sc: Scene, batch: str | None) -> Path:
    row = sc.conn.execute("SELECT worktree FROM batches WHERE id = ?", (batch,)).fetchone()
    return Path((row["worktree"] if row else None) or ".")


def _filled(root: Path, args) -> dict:
    out = {}
    for k, v in args:
        if isinstance(v, str) and DISK in v:
            head, _, path = v.partition(DISK)
            v = head + (root / path).read_text(encoding="utf-8")
        out[k] = v
    return out


def send(sc: Scene, call: Call) -> Exception | None:
    """Send the call through `Sandbox.call`, and return the refusal or
    None. A `code.write` changes the disk, so the file's bytes go back
    after the call, and the scene does not move."""
    sb = sandbox_for(sc, call)
    root = _root(sc, call.wake.refs[0])
    for op, args in call.before:
        sb.call(op, **_filled(root, args))
    args = _filled(root, call.args)
    target = root / args["path"] if call.op == "code.write" else None
    before = target.read_bytes() if target is not None and target.exists() else None
    try:
        sb.call(call.op, **args)
    except Exception as exc:                               # noqa: BLE001
        return exc
    finally:
        if target is not None:
            if before is None:
                target.unlink(missing_ok=True)
            else:
                target.write_bytes(before)
    return None


def land(sc: Scene, key: str, name: str) -> None:
    """Send the sweep's right call `name` through a whole session that
    commits, on the loop's pick of `key`: the calls of `before`, the call,
    and for a `code.write` the Developer's commit. `send` stages a call and
    never commits, so only a session meets the doors of the commit path.

    The loop turns until it picks `key`, and the seats' script answers
    every pick before it. A land moves the scene, so a test lands on a
    second build only."""
    call = next(c for c in sweep() if c.name == name)

    def lines(sc: Scene, wake: Wake) -> list[str]:
        root = _root(sc, loop._batch_of(sc.conn, wake))
        out = [f"TOOL: {op}({_kw(_filled(root, args))})" for op, args in call.before]
        out.append(f"TOOL: {call.op}({_kw(_filled(root, call.args))})")
        if call.op == "code.write":
            out.append("TOOL: code.commit(message='a right call of the sweep')")
        return out
    sc.landing[key] = Session(lines)
    play(sc, lambda conn: key not in sc.landing)
    assert sc.steps[-1] == key, (key, sc.steps[-3:])


# The second build of each scene lands one right call of each op of the
# sweep, in this order, each on the loop's pick of its key (the review of
# 2d7cc73, finding 5). The Developer's write lands on the review's fix wake,
# because no scene's loop picks a Developer wake of b2 after b2's start.
LANDINGS = {
    "two_batches": [
        ("tester|tick:tests_missing|b2", "the project test tests/test_charges.py as an encode"),
    ],
    "review": [
        ("architect|tick:structural_review|b1", "the Architect's violated finding"),
        ("developer|tick:finding_violated|b1", "src/billing/charges.py whole with a comment"),
        ("critic|tick:review|b1", "the Critic's claim that the test does not encode c1, "
                                  "and its challenge"),
        ("critic|tick:review|b1", "the Critic's fail verdict after a claim of True"),
    ],
}


def seat_landings(sc: Scene) -> None:
    """The seats that the loop picks between the review's landings. The
    Critic upholds the violated finding, so the Developer answers it. The
    Tester answers the Critic's challenge with the test that encodes c1."""
    seat(sc, "critic|tick:finding_review|b1,f1", [
        "TOOL: findings.load(batch_id='b1')",
        "TOOL: verdicts.rule(finding_id='f1', ruling='upheld', "
        "reason='prorate returns a fraction of a cent')"])
    seat(sc, "tester|challenge|c1,t1", [
        f"TOOL: tests.encode(id='t1', criterion_id='c1', path={TEST_PATH!r}, "
        f"body={TEST_BODY!r})"])


def _kw(args: dict) -> str:
    return ", ".join(f"{k}={v!r}" for k, v in args.items())


# -- reading a scene ------------------------------------------------------------------

def rows(sc: Scene, free: tuple[str, ...] = ()) -> dict[str, list]:
    """Every row of every table, with the scene's own root replaced by a
    token and each clock's reading replaced by a token, so two builds
    compare. `free` names columns to drop whole."""
    conn = sc.conn
    root = str(sc.root)
    out = {}
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' "
        "ORDER BY name")]
    for t in tables:
        cur = conn.execute(f"SELECT * FROM {t}")
        cols = [d[0] for d in cur.description]
        keep = [i for i, c in enumerate(cols) if f"{t}.{c}" not in free and c not in free]
        got = []
        for r in cur.fetchall():
            row = tuple(_clocked(f"{t}.{cols[i]}", _norm(r[i], root)) for i in keep)
            if t == "config" and row[0] in CLOCK_KEYS:
                row = (row[0], "<t>")
            got.append(row)
        out[t] = sorted(got, key=repr)
    return out


# The columns that hold a clock's reading inside their text. pytest's summary
# line ends with its run time, and the fix wake pushes the red run's output,
# so the run time reaches the prompt too. The run time is the one free part.
TIMED = {"test_runs.output", "turns.user", "turns.system"}
# A prompt that holds a run time has its own hash. The hash is the free part:
# `sessions.prompt_hash` becomes a token, and so does the `prompt_hash` key
# inside `sessions.pins_json`, whose other pins must repeat.
HASHED = {"sessions.prompt_hash"}
PINNED = {"sessions.pins_json"}
FREE: tuple[str, ...] = ()
# The config rows whose value is the clock at onboarding.
CLOCK_KEYS = {"created_at"}
# The columns that hold the clock alone: SQLite's `datetime('now')`.
CLOCKS = {"config_history.at"}
# pytest's own summary line: the counts, then " in <seconds>s", inside "=".
_RUN_TIME = re.compile(
    r"((?:passed|failed|errors?|skipped|xfailed|xpassed|warnings?|deselected"
    r"|no tests ran)(?: \(\w+\))? in )\d+(?:\.\d+)?s\b")


def _clocked(col: str, v):
    if not isinstance(v, str):
        return v
    if col in TIMED:
        return _RUN_TIME.sub(r"\1<t>s", v)
    if col in CLOCKS:
        return "<t>"
    if col in HASHED:
        return "<hash>"
    if col in PINNED:
        return re.sub(r'("prompt_hash": )"[0-9a-f]+"', r'\1"<hash>"', v)
    return v


def _norm(v, root: str):
    if isinstance(v, str):
        for form in (root, root.replace("\\", "/"), json.dumps(root)[1:-1]):
            v = v.replace(form, "<root>")
    return v
