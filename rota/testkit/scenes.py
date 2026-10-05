"""
Scenes: wide states that code builds through the real ops (frame 144, item 3).

A night database is not a test tier. A scene is the state that a night
reaches, built on every run by the real ops: the scheduler's ticks, the
runner's sessions with a scripted backend, `lifecycle`, the harness and real
git on the sample repository. No scene is stored as a database (ruled: the
holding session and the Principal, 2026-10-05).

Every step of a build is a wake that the real frontier holds at that moment,
performed as `loop.step` performs it (`turn`). The principal answers through
`principal.pump`, the gate that `loop.step` calls first, and speaks first
through `talk.open_with`, the intake of the TUI. So a scene is a state that
the real scheduler, the real ops and the real gates produce (the rule of the
review of 906b765, 2026-10-05).

Each builder returns a `Scene`. The tests in `tests/rota/test_scene_*.py`
build each scene once per module, send the catalogue's wrong calls and the
sweep's right calls through `Sandbox.call`, and never commit a session, so
the scene does not move under them.

Three deviations from "the real ops" hold, each for a reason:

- `provision.ensure_env` is a stub. It lays a venv and runs pip, 8.5 s for
  each batch start (observed: frame 144 pass 5, 2026-10-05). The harness
  then runs the project's tests with rota's own interpreter, which is its
  documented fallback. No scene asserts on the environment.
- `config.project_root` is a row, as in `test_arc_seam.py`. It is a fact
  about the repository and not a declared setting, and no op writes it.
- `turn` does not call `cascade_wakes`, `cycle` or `note_spill` after a
  session. The three read rows and write none, except `note_spill`, which
  reads the card of an Ollama server, and a scripted run has none.
"""
from __future__ import annotations

import contextlib
import json
import re
import sqlite3
from dataclasses import dataclass, field, replace
from pathlib import Path

from ..core import harness, lifecycle, loop, scheduler
from ..core.db import init_db
from ..core.runner import run_session
from ..core.scheduler import Wake
from ..llm.llm import Pins, ScriptedBackend
from ..roles import principal
from . import gitfixture

PINS = Pins(model="scripted", temperature=0.0, num_ctx=4096)
# The role of a scheduler action. `loop.step` performs a wake of this role,
# or of a `do:` kind, itself and before any session.
SCHEDULER = "-"


@dataclass
class Scene:
    """A built state: the database, the sample repository and the ids."""
    name: str
    conn: sqlite3.Connection
    repo: gitfixture.SampleRepo
    root: Path
    ids: dict = field(default_factory=dict)

    def close(self) -> None:
        self.conn.close()
        gitfixture.cleanup(self.repo)


# -- the engine: one turn of the crank, as `loop.step` takes it ---------------------

def drive(conn, wake: Wake, script: list[str], allow: tuple[str, ...] = (), **kw):
    """One session of `wake` with a scripted completion through the real
    doors. Fails when the session does not commit, or meets a note that
    `allow` does not name."""
    outcome = run_session(conn, wake, backend=ScriptedBackend(script + ["done"]),
                          pins=PINS, **kw)
    if not outcome.committed:
        raise AssertionError(f"{wake} failed: {outcome.errors}")
    # A scripted turn that a door refuses is a scene that drifted. The note
    # on the prompt's size is about the 4096 window, and a cut note is the
    # runner's account of a push it shortened. Neither is a door.
    refused = [e for e in outcome.errors
               if not e.startswith(("prompt over budget", "cut ", *allow))]
    if refused:
        raise AssertionError(f"{wake} met a refusal: {refused}")
    conn.commit()
    return outcome


def _short(w: Wake) -> str:
    return f"{w.role}|{w.kind}|{w.message_id or ''}|{','.join(w.refs)}|{w.detail}"


def _action(w: Wake) -> bool:
    """`loop.step`'s own test for a wake that the scheduler performs."""
    return w.role in ("", SCHEDULER) or w.kind.startswith("do:")


def turn(sc: "Scene", role: str, kind: str, ref: str | None = None,
         script: list[str] | tuple = (), allow: tuple[str, ...] = ()) -> Wake:
    """One step of `loop.step`, on the wake of `role` and `kind` that the
    frontier holds now, with `ref` in its refs or as its message.

    The frontier is the loop's own call, so its quarantine marks land as in
    a night. The wake is the frontier's object, with its detail. A scheduler
    action goes first, as in `loop.step`: a session is refused while one
    waits. A session's dispatch is counted, and a second dispatch carries
    its attempt. A batch start makes the worktree before the session.
    """
    conn = sc.conn
    with _no_venv():
        ready = scheduler.frontier(conn, principal_present=True)
        mine = [w for w in ready
                if (w.role == role or (role == SCHEDULER and _action(w))) and w.kind == kind
                and (ref is None or ref in w.refs or w.message_id == ref)]
        if not mine:
            raise AssertionError(f"the frontier does not hold {role}|{kind}|{ref}: "
                                 f"{[_short(w) for w in ready]}")
        wake = mine[0]
        acts = [w for w in ready if _action(w)]
        if acts and acts[0] != wake:
            raise AssertionError(f"the loop performs {_short(acts[0])} before "
                                 f"{_short(wake)}")
        sc.ids.setdefault("steps", []).append(_short(wake))
        if acts:
            scheduler.note_dispatch(conn, wake)
            loop._perform(conn, wake)
            conn.commit()
            return wake
        n = scheduler.note_dispatch(conn, wake)
        if n >= 2:
            wake = replace(wake, attempt=n)
        batch = loop._batch_of(conn, wake)
        if wake.kind == "tick:batch_start" and batch:
            lifecycle.start(conn, batch)
        drive(conn, wake, list(script), allow, batch_id=batch)
        if wake.kind == "tick:quarantined":
            # `loop.step`'s own line: said out loud, so stop saying it.
            conn.execute("UPDATE tick_attempts SET reported = 1 WHERE quarantined = 1")
        conn.commit()
        return wake


def answer(sc: "Scene", verb: str, per_item: dict, text: str = "") -> str | None:
    """The principal's verdict on the first open ask of `verb` whose refs
    hold every key of `per_item`, through `principal.pump`. The principal
    defers each ask before it, as a `None` in the script does. Returns the
    verdict's id, or None when the gate lands no message, as on an
    acknowledged touch note."""
    asks = principal.pending_asks(sc.conn)
    at = [i for i, a in enumerate(asks) if a.verb == verb and set(per_item) <= set(a.refs)]
    if not at:
        raise AssertionError(f"no open {verb} on {sorted(per_item)}: "
                             f"{[(a.message_id, a.verb, a.refs) for a in asks]}")
    made = principal.pump(sc.conn, principal.ScriptedPrincipal(
        [None] * at[0] + [principal.Answer("verdict", text=text, per_item=per_item)]))
    sc.conn.commit()
    sc.ids.setdefault("steps", []).append(f"principal|verdict|{asks[at[0]].message_id}")
    return made[0] if made else None


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


def _latest(conn, to_role: str, verb: str) -> str:
    return conn.execute("SELECT id FROM messages WHERE to_role = ? AND verb = ? "
                        "ORDER BY rowid DESC", (to_role, verb)).fetchone()["id"]


# -- the shared steps -----------------------------------------------------------------

def item(sc: Scene, n: int, priority: int) -> None:
    """One sentence of the principal to a batch `b<n>` with one ticket and one
    criterion, each step a wake of the frontier: the Liaison's segment and
    confirm, the principal's verdict, the three delivers, the Vision Keeper's
    item, the Terminologist's term, the Architect's read of the model, the
    sign-off through the Liaison's present and relay, the Vision Keeper's
    priority, the slicing, the criterion and the grouping."""
    from ..tools.talk import open_with
    sentence, problem, term, sense, ticket, criterion = ITEMS[n]
    conn = sc.conn
    mid = open_with(conn, sentence)
    entry = json.loads(conn.execute("SELECT body_refs FROM messages WHERE id = ?",
                                    (mid,)).fetchone()[0])[0]
    turn(sc, "liaison", "message", mid, [
        f"TOOL: brief.segment(id='s{n}', span_entry='{entry}', span_start=0, "
        f"span_end={len(sentence)}, text='{sentence}')",
        f"TOOL: msg.confirm_principal(refs=['s{n}'])",
    ])
    ok = answer(sc, "confirm", {f"s{n}": "approve"})
    turn(sc, "liaison", "message", ok, [
        f"TOOL: brief.ratify(id='s{n}')",
        f"TOOL: msg.deliver_vision_keeper(refs=['s{n}'])",
        f"TOOL: msg.deliver_terminologist(refs=['s{n}'])",
        f"TOOL: msg.deliver_architect(refs=['s{n}'])",
    ])
    turn(sc, "vision_keeper", "message", _latest(conn, "vision_keeper", "deliver"), [
        f"TOOL: problem.assert(id='i{n}', text='{problem}', kind='in_scope')",
    ])
    turn(sc, "terminologist", "message", _latest(conn, "terminologist", "deliver"), [
        f"TOOL: glossary.amend(term='{term}', sense_short='{sense}', "
        f"sense_body='In billing, {term} means {sense}.')",
    ])
    # The Architect reads its model against the sentence and finds nothing
    # to propose, as most of a night's Architect delivers do.
    turn(sc, "architect", "message", _latest(conn, "architect", "deliver"), [
        "TOOL: model.consult()",
    ])
    turn(sc, "vision_keeper", "tick:signoff", f"i{n}", [
        f"TOOL: msg.submit_liaison(refs=['i{n}'])",
    ])
    turn(sc, "liaison", "message", _latest(conn, "liaison", "submit"), [
        f"TOOL: msg.present_principal(refs=['i{n}'])",
    ])
    signed = answer(sc, "present", {f"i{n}": "approve"})
    turn(sc, "liaison", "message", signed, [
        f"TOOL: msg.relay_vision_keeper(refs=['i{n}'])",
    ])
    turn(sc, "vision_keeper", "message", _latest(conn, "vision_keeper", "relay"), [
        f"TOOL: problem.prioritize(id='i{n}', priority={priority})",
    ])
    turn(sc, "vision_keeper", "tick:slicing", f"i{n}", [
        f"TOOL: tickets.slice(id='tk{n}', item_id='i{n}', text='{ticket}')",
    ])
    gid = conn.execute("SELECT id FROM glossary_terms WHERE term = ?",
                       (term,)).fetchone()["id"]
    turn(sc, "terminologist", "tick:criteria", f"i{n}", [
        f"TOOL: criteria.specify(id='c{n}', ticket_id='tk{n}', text='{criterion}', "
        f"term_refs=['{gid}'])",
    ])
    turn(sc, "architect", "tick:grouping", f"tk{n}", [
        f"TOOL: batches.group(id='b{n}', item_id='i{n}', ticket_ids=['tk{n}'])",
    ])


def annotate(sc: Scene, batch: str, paths: list[str]) -> None:
    """The Architect's touch set for a pending batch, and the Liaison's touch
    note, which the principal reads and acknowledges."""
    item_id = sc.conn.execute("SELECT item_id FROM batches WHERE id = ?",
                              (batch,)).fetchone()[0]
    turn(sc, "architect", "tick:annotate", batch, [
        f"TOOL: batches.annotate(batch_id={batch!r}, paths={paths!r})",
    ])
    turn(sc, "liaison", "tick:touch_note", batch, [
        f"TOOL: msg.present_principal(refs=[{batch!r}, {item_id!r}])",
    ])
    answer(sc, "present", {item_id: "approve"})


def develop(sc: Scene, batch: str, kind: str, writes: list[tuple[str, str]],
            message: str, allow: tuple[str, ...] = ()) -> str:
    """A Developer session on the frontier's wake of `kind`, which writes each
    `(path, text)` whole and commits. Returns the batch's head."""
    script = [f"TOOL: code.write(path={p!r}, text={t!r})" for p, t in writes]
    turn(sc, "developer", kind, batch,
         script + [f"TOOL: code.commit(message={message!r})"], allow)
    return sc.conn.execute("SELECT head_commit FROM batches WHERE id = ?",
                           (batch,)).fetchone()["head_commit"]


def run_tests(sc: Scene, batch: str) -> None:
    """The harness, on the frontier's `do:harness` wake."""
    turn(sc, SCHEDULER, "do:harness", batch)


def worktree(sc: Scene, batch: str) -> Path:
    return Path(sc.conn.execute("SELECT worktree FROM batches WHERE id = ?",
                                (batch,)).fetchone()["worktree"])


# -- the sample's own text, changed by a line --------------------------------------

def sample(path: str) -> str:
    from .samplerepo import FILES
    return FILES[path]


def _charges_red() -> str:
    """`src/billing/charges.py` with `prorate` off by one cent, which turns
    the project's `tests/test_charges.py` red."""
    text = sample("src/billing/charges.py")
    old = "    return round(amount_cents * days_used / days_in_period)\n"
    assert old in text
    return text.replace(old, "    return round(amount_cents * days_used / days_in_period) + 1\n")


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


def encode(sc: Scene, batch: str, body: str = TEST_BODY) -> None:
    """The Tester's `tests_missing` wake: triage, then one test at the root,
    whose name matches `harness.inherit`'s pattern `test_*.py`."""
    turn(sc, "tester", "tick:tests_missing", batch, [
        "TOOL: tests.triage(criterion_id='c1', verdict='encodable')",
        f"TOOL: tests.encode(id='t1', criterion_id='c1', path={TEST_PATH!r}, "
        f"body={body!r})",
    ])


def judge(sc: Scene, batch: str, result: str = "pass") -> None:
    turn(sc, "critic", "tick:review", batch, [
        f"TOOL: criteria.load(batch_id={batch!r})",
        f"TOOL: tests.load(batch_id={batch!r})",
        f"TOOL: verdicts.emit(batch_id={batch!r}, result={result!r})",
    ])


# -- S1: two batches that share the project's tests -----------------------------------

def two_batches(tmp: Path) -> Scene:
    """S1. b1 starts, takes in the project's tests, and its Developer's commit
    turns `tests/test_charges.py` red. The principal's second sentence then
    arrives, and its sign-off ranks item 2 above item 1. The preempt defers
    b1, b2 starts, takes in the project's tests again under the same ids
    (frame 130's wall), and its Developer commits the export.

    The Developer rows of the catalogue and the sweep are sent on b2's start
    wake, which the frontier held one step before the scene's end."""
    sc = _base("two_batches", tmp)
    item(sc, 1, 1)
    annotate(sc, "b1", ["src/billing/charges.py"])
    head1 = develop(sc, "b1", "tick:batch_start",
                    [("src/billing/charges.py", _charges_red())],
                    "prorate the remainder")
    run_tests(sc, "b1")
    item(sc, 2, 2)
    turn(sc, SCHEDULER, "do:preempt", "b1")
    annotate(sc, "b2", [EXPORT_PATH])
    develop(sc, "b2", "tick:batch_start", [(EXPORT_PATH, EXPORT)], "export invoices")
    run_tests(sc, "b2")
    sc.ids.update(wt1=worktree(sc, "b1"), wt2=worktree(sc, "b2"), head1=head1,
                  charges=harness.inherited_id("tests/test_charges.py"))
    return sc


# -- S2: a merged batch's Tester file is a project test of the next batch ---------

def merged_then_next(tmp: Path) -> Scene:
    """S2. b1 runs the whole path: the Developer's module, the harness, the
    Tester's `test_upgrade.py` at the root, the harness again, a pass verdict
    and the merge, which delivers the test in a commit of its own (click
    night 50). b2 then starts, and `harness.inherit` takes the delivered
    file in as a project test of b2. Item 1 ranks above item 2, so b1
    starts first and nothing preempts it."""
    sc = _base("merged_then_next", tmp)
    item(sc, 1, 2)
    item(sc, 2, 1)
    annotate(sc, "b1", [UPGRADE_PATH])
    annotate(sc, "b2", [EXPORT_PATH])
    develop(sc, "b1", "tick:batch_start", [(UPGRADE_PATH, UPGRADE)], "charge an upgrade")
    run_tests(sc, "b1")
    encode(sc, "b1")
    run_tests(sc, "b1")
    judge(sc, "b1")
    # Constraint zero binds nothing once every area is surveyed, so it is
    # global and every batch owes a structural review, as on nights 119 to
    # 124. Nights 119 and 121 hold a satisfied finding on it.
    turn(sc, "architect", "tick:structural_review", "b1", [
        f"TOOL: findings.find(id='f1', batch_id='b1', constraint_id='k0', "
        f"status='satisfied', grain={UPGRADE_PATH!r})",
    ])
    turn(sc, SCHEDULER, "do:merge", "b1")
    develop(sc, "b2", "tick:batch_start", [(EXPORT_PATH, EXPORT)], "export invoices")
    run_tests(sc, "b2")
    sc.ids.update(delivered=harness.inherited_id(TEST_PATH))
    return sc


# -- S5: a test at version 2 after an answered challenge -----------------------------

def challenged(tmp: Path) -> Scene:
    """S5. The Tester's first test asserts the full price, the harness is red,
    and the Developer challenges it with the criterion's words and the
    test's. The Tester's challenge wake replaces t1 under its stored id, so
    t1 is at version 2, and the harness is green on the same commit."""
    sc = _base("challenged", tmp)
    item(sc, 1, 1)
    annotate(sc, "b1", [UPGRADE_PATH])
    develop(sc, "b1", "tick:batch_start", [(UPGRADE_PATH, UPGRADE)], "charge an upgrade")
    run_tests(sc, "b1")
    encode(sc, "b1", TEST_BODY.replace("== 1000", "== 3000"))
    run_tests(sc, "b1")
    turn(sc, "developer", "tick:tests_failing", "b1", [
        "TOOL: msg.challenge_tester(refs=['c1', 't1'], quotes=["
        "'an upgrade of 3000 cents used 10 of 30 days charges 1000 cents', "
        "'assert upgrade_charge(3000, 10, 30) == 3000'])",
    ])
    ch = _latest(sc.conn, "tester", "challenge")
    turn(sc, "tester", "message", ch, [
        f"TOOL: tests.encode(id='t1', criterion_id='c1', path={TEST_PATH!r}, "
        f"body={TEST_BODY!r})",
    ])
    run_tests(sc, "b1")
    sc.ids.update(challenge=ch)
    return sc


# -- S3 and S4: the park ------------------------------------------------------------

def park(tmp: Path) -> Scene:
    """S3 and S4, one scene. b1 reaches attempt 5 of 10: the harness runs
    after the Developer's first commit, again after the Tester's test, which
    is red, and after each of three more commits, red each time. The
    scheduler's `tests_failing` wake is then
    dispatched three times with no commit, and the next frontier marks the
    key. `quarantine_overrun` marks it, because `frontier` runs it first.
    `quarantine_stalled` marks a key at the same count, but it finds this
    one marked already. The Liaison tells the principal on the
    `quarantined` wake. Items 2 and 3 arrive, item 2 ranks above item 1,
    the preempt defers b1, and the Liaison's `park_ask` wake opens the ask.

    The design named b3 behind b1 by a `batch_dep_facts` row (S4). No op in
    `rota/` writes that table, and nights 119 to 124 hold no row in it
    (observed: the review of 906b765, 2026-10-05). So no night reaches "b3
    behind b1", and the scene holds no such row. What the scene proves for
    S4 is that the park keeps b1 out of `next_batch`, and b2 and b3 wait in
    priority order."""
    sc = _base("park", tmp)
    item(sc, 1, 1)
    annotate(sc, "b1", [UPGRADE_PATH])
    develop(sc, "b1", "tick:batch_start", [(UPGRADE_PATH, _upgrade_wrong(1))],
            "charge an upgrade")
    run_tests(sc, "b1")
    encode(sc, "b1")
    run_tests(sc, "b1")
    for k in range(2, 5):
        develop(sc, "b1", "tick:tests_failing", [(UPGRADE_PATH, _upgrade_wrong(k))],
                f"charge an upgrade, attempt {k}")
        run_tests(sc, "b1")
    for _ in range(3):
        # The seat's note on an empty session is the state: a dispatch
        # with no drain.
        turn(sc, "developer", "tick:tests_failing", "b1",
             allow=("ended a tick with nothing done",))
    # The first call of the next `frontier`, made here to read its count.
    sc.ids["overrun"] = scheduler.quarantine_overrun(sc.conn)
    sc.conn.commit()
    turn(sc, "liaison", "tick:quarantined", "b1", [
        "TOOL: msg.present_principal(refs=['b1'])",
    ])
    # The principal reads it. A present on a batch alone is acknowledged.
    answer(sc, "present", {"b1": "approve"})
    item(sc, 2, 2)
    turn(sc, SCHEDULER, "do:preempt", "b1")
    turn(sc, "liaison", "tick:park_ask", "b1", [
        "TOOL: msg.clarify_principal(refs=['i1', 'b1'], "
        "question='b1 failed four times. Change the criterion, or abandon b1?')",
    ])
    annotate(sc, "b2", [EXPORT_PATH])
    item(sc, 3, 1)
    annotate(sc, "b3", ["src/notify/delivery.py"])
    sc.ids.update(key="developer|tick:tests_failing|b1",
                  ask=scheduler.open_park_ask(sc.conn, "b1"))
    return sc


# -- S7: review with a bound constraint ----------------------------------------------

CONSTRAINT = "a charge is a whole number of cents"
CHARGES = "src/billing/charges.py"


def survey(sc: Scene, bind: bool = False) -> None:
    """Onboarding with the survey phase alone: each area's Terminologist and
    then each area's Architect, as the frontier offers them, and constraint
    zero after each survey, as the loop performs it. With `bind`, the
    Architect reads `src/billing/charges.py` and binds the constraint there.
    Every other survey attests none found on a grain of its area.

    The phases are a setting the principal owns (`onboarding_phases`).
    The default runs eight more phases, and none of them can bind a file:
    only a survey or a boundary session reads code and amends the model."""
    from ..core import config
    from ..onboarding import boot
    conn = sc.conn
    boot.onboard(conn, sc.repo.root)
    config.set(conn, "onboarding_phases", "survey")
    conn.commit()
    while True:
        ready = scheduler.frontier_readonly(conn, True)
        acts = [w for w in ready if _action(w)]
        if acts:
            turn(sc, SCHEDULER, acts[0].kind)
            continue
        held = [w for w in ready if w.kind == "tick:survey"]
        if not held:
            break
        role, area = held[0].role, held[0].refs[0]
        if bind and role == "architect" and area == "src/billing":
            script = [
                f"TOOL: code.source(path={CHARGES!r})",
                f"TOOL: model.amend(headline={CONSTRAINT!r}, text='Money is stored "
                f"and charged in whole cents, never in fractions.', "
                f"bindings=[{CHARGES!r}])",
                f"TOOL: surveys.attest(outcome='found', citations=[{CHARGES!r}])",
            ]
        else:
            grain = conn.execute(
                "SELECT grain FROM code_index WHERE area = ? AND grain_kind = 'path' "
                "ORDER BY grain", (area,)).fetchone()["grain"]
            script = [f"TOOL: surveys.attest(outcome='none_found', citations=[{grain!r}])"]
        turn(sc, role, "tick:survey", area, script)


def critic(tmp: Path, name: str = "critic") -> Scene:
    """S7 up to the Critic. The Architect's survey binds one constraint to
    `src/billing/charges.py`, and its annotation of b1 names that file. b1's
    Developer makes `prorate` divide and never round, which violates the
    constraint, and adds the upgrade module. The Tester's test does not
    encode its criterion: it asserts only that the charge is positive. The
    project's tests stay green, because their numbers divide exactly. So the
    frontier holds the Critic's review wake.

    The Critic's rows of S7 run here. One commit gets one verdict, so no
    state holds both the Critic's review wake and the Architect's
    structural review wake, which needs a pass verdict."""
    sc = _base(name, tmp, bind=True)
    item(sc, 1, 1)
    annotate(sc, "b1", [CHARGES, UPGRADE_PATH])
    divides = sample(CHARGES).replace(
        "    return round(amount_cents * days_used / days_in_period)\n",
        "    return amount_cents * days_used / days_in_period\n")
    develop(sc, "b1", "tick:batch_start", [(CHARGES, divides), (UPGRADE_PATH, UPGRADE)],
            "charge an upgrade")
    run_tests(sc, "b1")
    encode(sc, "b1", TEST_BODY.replace(" == 1000\n", " > 0\n"))
    run_tests(sc, "b1")
    sc.ids.update(constraint=sc.conn.execute(
        "SELECT id FROM constraints WHERE headline = ?", (CONSTRAINT,)).fetchone()["id"])
    return sc


def review(tmp: Path) -> Scene:
    """S7. The scene `critic`, then the Critic passes the batch, as a Critic
    that misses the weak test does. So the scene stops at the Architect's
    structural review. The review is owed because the touch set meets the
    binding, and because constraint zero binds nothing after the survey, as
    on nights 119 to 124."""
    sc = critic(tmp, "review")
    judge(sc, "b1")
    return sc


BUILDERS = {"two_batches": two_batches, "merged_then_next": merged_then_next,
            "challenged": challenged, "park": park, "critic": critic, "review": review}


# -- the catalogue and the sweep ---------------------------------------------------

@dataclass(frozen=True)
class Call:
    """One call on a scene, from the seat that `wake` wakes.

    A wrong call names the door that must refuse it, by the function at the
    top of the door's identity, and the first words of the refusal. A right
    call names neither and must land. `held` names the frame that holds a
    row that today's doors answer wrongly, and the row is a strict xfail.
    `before` holds the calls that the same session sends first, such as
    the triage that an encode needs. An argument that holds `DISK` and a
    path takes that file's text in the batch's worktree when it is sent."""
    scene: str
    name: str
    wake: Wake
    op: str
    args: tuple
    door: str = ""
    words: str = ""
    held: str = ""
    before: tuple = ()

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
        Call("critic", "a fail verdict before the claim that its test encodes",
             _w("critic", "tick:review", "b1"), "verdicts.emit",
             (("batch_id", "b1"), ("result", "fail"), ("failed_criterion", "c1")),
             "verdicts_emit", "a fail on c1 stands on its test actually encoding it"),
        Call("review", "a finding on a constraint that does not exist",
             _w("architect", "tick:structural_review", "b1"), "findings.find",
             (("id", "f1"), ("batch_id", "b1"), ("constraint_id", "k_none"),
              ("status", "violated"), ("grain", CHARGES)), "findings_find",
             "no constraints row has id="),
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
    both = (("refs", ["c1", "t1"]),
            ("quotes", ["an upgrade of 3000 cents used 10 of 30 days charges 1000 cents",
                        "assert upgrade_charge(3000, 10, 30) > 0"]))
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


def _filled(sc: Scene, call: Call, args) -> dict:
    root = Path(sc.conn.execute("SELECT worktree FROM batches WHERE id = ?",
                                (call.wake.refs[0],)).fetchone()["worktree"] or ".")
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
    root = Path(sc.conn.execute("SELECT worktree FROM batches WHERE id = ?",
                                (call.wake.refs[0],)).fetchone()["worktree"] or ".")
    for op, args in call.before:
        sb.call(op, **_filled(sc, call, args))
    args = _filled(sc, call, call.args)
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


def land(sc: Scene, call: Call) -> None:
    """Send a right call through a whole session that commits: the calls
    of `before`, the call, and for a `code.write` the Developer's commit.
    `send` stages a call and never commits, so only a session meets the
    doors of the commit path. This moves the scene, so a test runs it on a
    build of its own."""
    lines = [f"TOOL: {op}({_kw(_filled(sc, call, args))})" for op, args in call.before]
    lines.append(f"TOOL: {call.op}({_kw(_filled(sc, call, call.args))})")
    if call.op == "code.write":
        lines.append("TOOL: code.commit(message='a right call of the sweep')")
    batch = call.wake.refs[0] if call.wake.refs else None
    drive(sc.conn, _real_wake(sc, call.wake), lines, batch_id=batch)


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
