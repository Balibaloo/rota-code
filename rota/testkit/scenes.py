"""
Scenes: wide states that code builds through the real ops (frame 144, item 3).

A night database is not a test tier. A scene is the state that a night
reaches, built on every run by the real ops: the scheduler's ticks, the
runner's sessions with a scripted backend, `lifecycle`, the harness and real
git on the sample repository. No scene is stored as a database (ruled: the
holding session and the Principal, 2026-10-05).

Each builder returns a `Scene`. The tests in `tests/rota/test_scenes_*.py`
build each scene once per module, send the catalogue's wrong calls and the
sweep's right calls through `Sandbox.call`, and never commit a session, so
the scene does not move under them.

Two deviations from "the real ops" hold for every scene, each for a reason:

- `provision.ensure_env` is a stub. It lays a venv and runs pip, 8.5 s for
  each batch start (observed: frame 144 pass 5, 2026-10-05). The harness
  then runs the project's tests with rota's own interpreter, which is its
  documented fallback. No scene asserts on the environment.
- The principal's words are rows, as in `test_arc_seam.py`: the principal is
  not a seat, and `record_entry` is the op that the gate's landing calls.
"""
from __future__ import annotations

import contextlib
import json
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from ..core import harness, lifecycle
from ..core.db import init_db
from ..core.runner import run_session
from ..core.scheduler import Wake, predicate_wakes
from ..llm.llm import Pins, ScriptedBackend
from ..roles.principal import record_entry
from . import gitfixture

PINS = Pins(model="scripted", temperature=0.0, num_ctx=4096)


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


# -- the engine, as `test_arc_seam.py` drives it --------------------------------

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


def tick(conn, kind: str, ref: str | None = None) -> Wake:
    """The next wake of `kind`, with `ref` in its refs when one is given."""
    wakes = [w for w in predicate_wakes(conn)
             if w.kind == kind and (ref is None or ref in w.refs)]
    if not wakes:
        raise AssertionError(f"{kind} never fired for {ref}")
    return wakes[0]


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


def _base(name: str, tmp: Path) -> Scene:
    repo = gitfixture.make(tmp, name="scene")
    conn = init_db(tmp / "rota.db")
    # `project_root` is a fact about the repository, not a declared setting,
    # so it goes straight into the table, as in `test_arc_seam.py`.
    conn.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)",
                 (str(repo.root),))
    conn.commit()
    return Scene(name, conn, repo, tmp)


def _says(conn, mid: str, verb: str, seq: int, text: str | None = None,
          to: str = "liaison", frm: str = "principal") -> None:
    """A message from outside the seats: the principal's words or verdict."""
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
                 "VALUES (?, ?, ?, ?, ?, ?)", (mid, f"t_{mid}", frm, to, verb, seq))
    if text is not None:
        record_entry(conn, mid, text)
    conn.commit()


def _latest(conn, to_role: str, verb: str) -> str:
    return conn.execute("SELECT id FROM messages WHERE to_role = ? AND verb = ? "
                        "ORDER BY rowid DESC", (to_role, verb)).fetchone()["id"]


def item(sc: Scene, n: int, sentence: str, problem: str, term: str, sense: str,
         ticket: str, criterion: str) -> None:
    """One sentence of the principal to a batch `b<n>` with one ticket and
    one criterion, through the Liaison, the Vision Keeper, the
    Terminologist, the Product Owner's slicing and the Architect's grouping."""
    conn, seq = sc.conn, 100 * n
    _says(conn, f"m_in{n}", "converse", seq + 1, sentence)
    drive(conn, Wake("liaison", "message", f"m_in{n}", detail="converse"), [
        f"TOOL: brief.segment(id='s{n}', span_entry='e_m_in{n}', span_start=0, "
        f"span_end={len(sentence)}, text='{sentence}')",
        f"TOOL: msg.confirm_principal(refs=['s{n}'])",
    ])
    _says(conn, f"m_ok{n}", "verdict", seq + 3)
    drive(conn, Wake("liaison", "message", f"m_ok{n}", detail="verdict"), [
        f"TOOL: brief.ratify(id='s{n}')",
        f"TOOL: msg.deliver_vision_keeper(refs=['s{n}'])",
        f"TOOL: msg.deliver_terminologist(refs=['s{n}'])",
        f"TOOL: msg.deliver_architect(refs=['s{n}'])",
    ])
    drive(conn, Wake("vision_keeper", "message", _latest(conn, "vision_keeper", "deliver"),
                     detail="deliver"), [
        f"TOOL: problem.assert(id='i{n}', text='{problem}', kind='in_scope')",
    ])
    drive(conn, Wake("terminologist", "message", _latest(conn, "terminologist", "deliver"),
                     detail="deliver"), [
        f"TOOL: glossary.amend(term='{term}', sense_short='{sense}', "
        f"sense_body='In billing, {term} means {sense}.')",
    ])
    gid = conn.execute("SELECT id FROM glossary_terms WHERE term = ?",
                       (term,)).fetchone()["id"]
    # The Liaison's relay of the principal's sign-off, as `test_arc_seam.py`
    # writes it: the gate that produces it is the principal's.
    _says(conn, f"m_sign{n}", "relay", seq + 20, to="vision_keeper", frm="liaison")
    drive(conn, Wake("vision_keeper", "message", f"m_sign{n}", detail="relay"), [
        f"TOOL: problem.set_approval(id='i{n}', approval='approved')",
    ])
    drive(conn, tick(conn, "tick:slicing", f"i{n}"), [
        f"TOOL: tickets.slice(id='tk{n}', item_id='i{n}', text='{ticket}')",
    ])
    drive(conn, tick(conn, "tick:criteria"), [
        f"TOOL: criteria.specify(id='c{n}', ticket_id='tk{n}', text='{criterion}', "
        f"term_refs=['{gid}'])",
    ])
    grouping = tick(conn, "tick:grouping")
    drive(conn, Wake("architect", "tick:grouping", refs=grouping.refs), [
        f"TOOL: batches.group(id='b{n}', item_id='i{n}', ticket_ids=['tk{n}'])",
    ])


def start(sc: Scene, batch: str) -> Path:
    """`lifecycle.start`, which makes the worktree and runs `harness.inherit`."""
    with _no_venv():
        lifecycle.start(sc.conn, batch)
    sc.conn.commit()
    return Path(sc.conn.execute("SELECT worktree FROM batches WHERE id = ?",
                                (batch,)).fetchone()["worktree"])


def develop(sc: Scene, batch: str, kind: str, writes: list[tuple[str, str]],
            message: str) -> str:
    """A Developer session of `kind` that writes each `(path, text)` whole and
    commits. Returns the batch's head."""
    script = [f"TOOL: code.write(path={p!r}, text={t!r})" for p, t in writes]
    drive(sc.conn, Wake("developer", kind, refs=(batch,)),
          script + [f"TOOL: code.commit(message={message!r})"], batch_id=batch)
    return sc.conn.execute("SELECT head_commit FROM batches WHERE id = ?",
                           (batch,)).fetchone()["head_commit"]


def run_tests(sc: Scene, batch: str) -> list:
    with _no_venv():
        out = harness.run(sc.conn, batch)
    sc.conn.commit()
    return out


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


# -- S1: two batches that share the project's tests -----------------------------------

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


def _upgrade_wrong(k: int) -> str:
    """The module with a charge that is `k` cents too much, so each attempt
    is a new diff and the test stays red."""
    return UPGRADE.replace("days_in_period)\n", f"days_in_period) + {k}\n")


def encode(sc: Scene, batch: str, body: str = TEST_BODY) -> None:
    """The Tester's `tests_missing` wake: triage, then one test at the root,
    whose name matches `harness.inherit`'s pattern `test_*.py`."""
    drive(sc.conn, tick(sc.conn, "tick:tests_missing", batch), [
        "TOOL: tests.triage(criterion_id='c1', verdict='encodable')",
        f"TOOL: tests.encode(id='t1', criterion_id='c1', path={TEST_PATH!r}, "
        f"body={body!r})",
    ], batch_id=batch)


def judge(sc: Scene, batch: str, result: str = "pass") -> None:
    drive(sc.conn, tick(sc.conn, "tick:review", batch), [
        f"TOOL: criteria.load(batch_id={batch!r})",
        f"TOOL: tests.load(batch_id={batch!r})",
        f"TOOL: verdicts.emit(batch_id={batch!r}, result={result!r})",
    ], batch_id=batch)


def two_batches(tmp: Path) -> Scene:
    """S1. Two items, two batches. b1 starts, takes in the project's tests,
    and its Developer's commit turns `tests/test_charges.py` red. b1 is
    deferred, as the loop's preempt does, and b2 starts and takes in the
    project's tests again under the same ids (frame 130's wall)."""
    sc = _base("two_batches", tmp)
    for n in (1, 2):
        item(sc, n, *ITEMS[n])
    wt1 = start(sc, "b1")
    head1 = develop(sc, "b1", "tick:batch_start",
                    [("src/billing/charges.py", _charges_red())],
                    "prorate the remainder")
    run_tests(sc, "b1")
    lifecycle.defer(sc.conn, "b1")
    sc.conn.commit()
    wt2 = start(sc, "b2")
    run_tests(sc, "b2")
    sc.ids.update(wt1=wt1, wt2=wt2, head1=head1,
                  charges=harness.inherited_id("tests/test_charges.py"))
    return sc


# -- S2: a merged batch's Tester file is a project test of the next batch ---------

def merged_then_next(tmp: Path) -> Scene:
    """S2. b1 runs the whole path: the Developer's module, the Tester's
    `test_upgrade.py` at the root, a green harness, a pass verdict and the
    merge, which delivers the test in a commit of its own (click night 50).
    b2 then starts, and `harness.inherit` takes the delivered file in as a
    project test of b2."""
    sc = _base("merged_then_next", tmp)
    for n in (1, 2):
        item(sc, n, *ITEMS[n])
    start(sc, "b1")
    develop(sc, "b1", "tick:batch_start", [(UPGRADE_PATH, UPGRADE)], "charge an upgrade")
    encode(sc, "b1")
    run_tests(sc, "b1")
    judge(sc, "b1")
    lifecycle.merge(sc.conn, "b1")
    sc.conn.commit()
    start(sc, "b2")
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
    item(sc, 1, *ITEMS[1])
    start(sc, "b1")
    develop(sc, "b1", "tick:batch_start", [(UPGRADE_PATH, UPGRADE)], "charge an upgrade")
    encode(sc, "b1", TEST_BODY.replace("== 1000", "== 3000"))
    run_tests(sc, "b1")
    drive(sc.conn, tick(sc.conn, "tick:tests_failing", "b1"), [
        "TOOL: msg.challenge_tester(refs=['c1', 't1'], quotes=["
        "'an upgrade of 3000 cents used 10 of 30 days charges 1000 cents', "
        "'assert upgrade_charge(3000, 10, 30) == 3000'])",
    ], batch_id="b1")
    ch = _latest(sc.conn, "tester", "challenge")
    drive(sc.conn, Wake("tester", "message", ch, detail="challenge"), [
        f"TOOL: tests.encode(id='t1', criterion_id='c1', path={TEST_PATH!r}, "
        f"body={TEST_BODY!r})",
    ], batch_id="b1")
    run_tests(sc, "b1")
    sc.ids.update(challenge=ch)
    return sc


# -- S3 and S4: the park ------------------------------------------------------------

def park(tmp: Path) -> Scene:
    """S3 and S4, one scene. b1 reaches attempt 5 of 10: five commits, each
    with a red harness. Its `tests_failing` wake is then dispatched three
    times with no commit, so `quarantine_overrun` marks the key. Item 2 is
    raised above item 1, the loop's preempt defers b1, and the Liaison's
    `park_ask` wake opens the ask. b2 and b3 are pending, and b3 declares b1
    as its predecessor."""
    from ..core import loop, predicates, scheduler
    sc = _base("park", tmp)
    for n in (1, 2, 3):
        item(sc, n, *ITEMS[n])
    # No op writes `batch_dep_facts` (observed: no insert in `rota/`,
    # 2026-10-05), so the declared order is a row.
    sc.conn.execute("INSERT INTO batch_dep_facts (before_batch, after_batch) "
                    "VALUES ('b1', 'b3')")
    sc.conn.commit()
    start(sc, "b1")
    develop(sc, "b1", "tick:batch_start", [(UPGRADE_PATH, _upgrade_wrong(1))],
            "charge an upgrade")
    encode(sc, "b1")
    run_tests(sc, "b1")
    for k in range(2, 6):
        develop(sc, "b1", "tick:tests_failing", [(UPGRADE_PATH, _upgrade_wrong(k))],
                f"charge an upgrade, attempt {k}")
        run_tests(sc, "b1")
    failing = Wake("developer", "tick:tests_failing", refs=("b1",))
    for _ in range(3):
        scheduler.note_dispatch(sc.conn, failing)
        # The seat's note on an empty session is the state: a dispatch
        # with no drain.
        drive(sc.conn, failing, [], allow=("ended a tick with nothing done",),
              batch_id="b1")
    scheduler.frontier(sc.conn)             # runs `quarantine_overrun`
    sc.conn.commit()
    _says(sc.conn, "m_prio", "relay", 900, to="vision_keeper", frm="liaison")
    drive(sc.conn, Wake("vision_keeper", "message", "m_prio", detail="relay"), [
        "TOOL: problem.prioritize(id='i2', priority=5)",
    ])
    (pre,) = predicates.REGISTRY["preempt"].fn(sc.conn)
    loop._perform(sc.conn, pre)
    (ask,) = predicates.REGISTRY["park_ask"].fn(sc.conn)
    drive(sc.conn, ask, [
        "TOOL: msg.clarify_principal(refs=['i1', 'b1'], "
        "question='b1 failed five times. Change the criterion, or abandon b1?')",
    ])
    sc.ids.update(key="developer|tick:tests_failing|b1",
                  ask=scheduler.open_park_ask(sc.conn, "b1"))
    return sc


# -- S7: review with a bound constraint ----------------------------------------------

CONSTRAINT = "a charge is a whole number of cents"
CHARGES = "src/billing/charges.py"


def review(tmp: Path) -> Scene:
    """S7. The Architect's model holds one constraint, bound to
    `src/billing/charges.py`. b1's Developer makes `prorate` divide and
    never round, which violates it, and adds the upgrade module. The
    Tester's test does not encode its criterion: it asserts only that the
    charge is positive. The project's tests stay green, because their
    numbers divide exactly. So the scene stops at the Critic's review
    wake."""
    from ..onboarding import boot
    sc = _base("review", tmp)
    # A binding names a file that the seat read and the index holds. The
    # Architect reads code in its survey of an area, after onboarding. The
    # survey wake names its area, as the scheduler's `tick:survey` does.
    boot.onboard(sc.conn, sc.repo.root)
    sc.conn.commit()
    drive(sc.conn, Wake("architect", "tick:survey", refs=("src/billing",)), [
        f"TOOL: code.source(path={CHARGES!r})",
        f"TOOL: model.amend(headline={CONSTRAINT!r}, text='Money is stored and "
        f"charged in whole cents, never in fractions.', bindings=[{CHARGES!r}])",
    ])
    item(sc, 1, *ITEMS[1])
    start(sc, "b1")
    divides = sample(CHARGES).replace(
        "    return round(amount_cents * days_used / days_in_period)\n",
        "    return amount_cents * days_used / days_in_period\n")
    develop(sc, "b1", "tick:batch_start", [(CHARGES, divides), (UPGRADE_PATH, UPGRADE)],
            "charge an upgrade")
    encode(sc, "b1", TEST_BODY.replace(" == 1000\n", " > 0\n"))
    run_tests(sc, "b1")
    sc.ids.update(constraint=sc.conn.execute(
        "SELECT id FROM constraints WHERE headline = ?", (CONSTRAINT,)).fetchone()["id"])
    return sc


BUILDERS = {"two_batches": two_batches, "merged_then_next": merged_then_next,
            "challenged": challenged, "park": park, "review": review}


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
        Call("challenged", "a second id for the challenged criterion",
             _w("tester", "challenge", "b1", "m_ch"), "tests.encode",
             _encode("t2", "c1", "test_upgrade_two.py", TEST_BODY),
             "tests_encode", "", held="frame 144: W138, no door refuses a second "
                                     "test on a criterion that holds one"),
        Call("review", "a fail verdict before the claim that its test encodes",
             _w("critic", "tick:review", "b1"), "verdicts.emit",
             (("batch_id", "b1"), ("result", "fail"), ("failed_criterion", "c1")),
             "verdicts_emit", "a fail on c1 stands on its test actually encoding it"),
        Call("review", "a finding on a constraint that does not exist",
             _w("architect", "tick:structural_review", "b1"), "findings.find",
             (("id", "f1"), ("batch_id", "b1"), ("constraint_id", "k_none"),
              ("status", "violated"), ("grain", CHARGES)), "findings_find", ""),
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
    rv = "review"
    both = (("refs", ["c1", "t1"]),
            ("quotes", ["an upgrade of 3000 cents used 10 of 30 days charges 1000 cents",
                        "assert upgrade_charge(3000, 10, 30) > 0"]))
    critic = _w("critic", "tick:review", "b1")
    out += [
        # The test does not encode c1, so the Critic's right answer is the
        # claim of False and a challenge, and a fail on the code is not.
        Call(rv, "the Critic's claim that the test does not encode c1, and its challenge",
             critic, "msg.challenge_tester", both,
             before=(("verdicts.claim_encodes", (("criterion_id", "c1"),
                                                 ("encodes", False))),)),
        Call(rv, "the Critic's fail verdict after a claim of True", critic, "verdicts.emit",
             (("batch_id", "b1"), ("result", "fail"), ("failed_criterion", "c1"),
              ("reason", "the charge is a fraction of a cent")),
             before=(("verdicts.claim_encodes", (("criterion_id", "c1"),
                                                 ("encodes", True))),)),
        Call(rv, "the Architect's violated finding",
             _w("architect", "tick:structural_review", "b1"), "findings.find",
             (("id", "f1"), ("batch_id", "b1"), ("constraint_id", CONSTRAINT_ID),
              ("status", "violated"), ("grain", CHARGES))),
        Call(rv, "the Developer's challenge that names both sides",
             _w("developer", "tick:tests_failing", "b1"), "msg.challenge_tester", both),
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
    wake = call.wake
    if wake.kind == "message" and wake.message_id == "m_ch":
        wake = Wake(wake.role, "message", sc.ids["challenge"], detail=wake.detail,
                    refs=wake.refs)
    return session_sandbox(sc.conn, wake, batch_id=batch)


def send(sc: Scene, call: Call) -> Exception | None:
    """Send the call through `Sandbox.call`, and return the refusal or
    None. A `code.write` changes the disk, so the file's bytes go back
    after the call, and the scene does not move."""
    sb = sandbox_for(sc, call)
    root = Path(sc.conn.execute("SELECT worktree FROM batches WHERE id = ?",
                                (call.wake.refs[0],)).fetchone()["worktree"] or ".")

    def filled(args) -> dict:
        out = {}
        for k, v in args:
            if isinstance(v, str) and DISK in v:
                head, _, path = v.partition(DISK)
                v = head + (root / path).read_text(encoding="utf-8")
            out[k] = v
        return out

    for op, args in call.before:
        sb.call(op, **filled(args))
    args = filled(call.args)
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


# -- reading a scene ------------------------------------------------------------------

def rows(sc: Scene, free: tuple[str, ...] = ()) -> dict[str, list]:
    """Every row of every table, with the scene's own root replaced by a
    token and the free columns dropped, so two builds compare."""
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
            row = tuple(_timed(_norm(r[i], root)) if f"{t}.{cols[i]}" in TIMED
                        else _norm(r[i], root) for i in keep)
            if t == "config" and row[0] in CLOCK_KEYS:
                row = (row[0], "<t>")
            got.append(row)
        out[t] = sorted(got, key=repr)
    return out


# The columns that hold a clock's reading inside their text. pytest's summary
# line ends with its run time, and the fix wake pushes the red run's output,
# so the run time reaches the prompt too. The duration is the one free part.
TIMED = {"test_runs.output", "turns.user", "turns.system"}
# The hashes of a prompt that holds a run time. `turns` keeps the prompt
# itself, compared with the run time made equal.
FREE = ("sessions.prompt_hash", "sessions.pins_json")
# The config rows whose value is the clock at onboarding.
CLOCK_KEYS = {"created_at"}


def _timed(v):
    return re.sub(r"\bin \d+(\.\d+)?s\b", "in <t>s", v) if isinstance(v, str) else v


def _norm(v, root: str):
    if isinstance(v, str):
        for form in (root, root.replace("\\", "/"), json.dumps(root)[1:-1]):
            v = v.replace(form, "<root>")
    return v
