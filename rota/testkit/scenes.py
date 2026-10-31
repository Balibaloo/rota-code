"""
Scenes: wide states that the real loop reaches (frame 144, item 3).

A night database is not a test tier. A scene is the state that a night
reaches, built on every run by the loop of a night: `loop.step`, the crank
that `rota run` turns. No scene is stored as a database (ruled: the holding
session and the Principal, 2026-10-05).

A build is a run of the night's walk (`probes/walk.py`) and nothing else
(the rule of the review of 2d7cc73, and of the review of 7a056ce0,
2026-10-05). Each step is one iteration of the walk: the principal answers
every open ask through `principal.pump`, the walk answers every Liaison
sentence that has no page, and then one `loop.step` runs. The loop
computes the frontier, performs a scheduler action or picks a wake, counts
the dispatch, starts a batch, runs the session and cascades. A scene never
picks a wake. It holds two scripts, and each answers what the loop asks:

- The seats' script answers a session by the key of the wake that the loop
  dispatched. A key is `scheduler.tick_key` for a tick or an action, and
  `role|verb|refs` for a message. A wake that the script does not answer
  fails the build, with its key and the frontier in the error.
- The principal's script answers an ask by its verb and refs. The walk
  answers every ask before it steps, so an ask that the script leaves open
  fails the build.

The principal also says a sentence, through `talk.open_with`, the intake of
the TUI. A night's walk says one sentence when it starts, and the walk
before it stops at quiet or at a merge. So `say` fails the build at any
other point.

The differences from a night (the review of 7a056ce0, finding 7):

- A night's walk sets `ROTA_ONESHOT=1` by default, and the gauntlet clears
  it (`probes/gauntlet_click.sh`, line 12, `export ROTA_ONESHOT=`), so a
  night runs each session turn by turn, and so does a scene. The two differ
  only from a walk that runs alone, outside the gauntlet.
- A night's principal answers a confirm or a present in words, and a
  Liaison session then lands the verdict through `rulings.rule` (night 121,
  s197 then s198). A scene's principal lands the verdict itself. Words on
  every page would add a Liaison session to each ask, about one step in
  four, so the difference stays. A clarify is answered in words, as on a
  night.
- Every night of 119 to 121 ends with `-|tick:constraint_zero|` at
  (3, 1, 1), quarantined and reported. A scene runs only the survey phase
  of onboarding, and holds no such row. The night's row names no area,
  and the night's end holds no unbound area that explains it, so the step
  that wrote it was not found.
- The sentences of a scene go through `talk.open_with`, as at the TUI. A
  night's walk writes the same two rows with its own ids, `e_p<n>` and
  `m_p<n>`. The walk's answer to a Liaison sentence uses the walk's own SQL
  and ids (`answer_replies`).

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
    # The pins of every session of the build. S6 runs at the night's window,
    # because its rule is about the cut at 16384 (doctrine 2).
    pins: Pins = PINS

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
    """Answer every wake of `role|kind` that no exact key answers. A function
    that the loop never calls fails the build, as a session does."""
    sc.seats[role_kind] = fn
    sc.ids.setdefault("_every_unused", set()).add(role_kind)


def rule(sc: Scene, verb: str, refs: list[str], per_item: dict, text: str = "",
         answer: str = "verdict") -> None:
    """The principal's answer to the ask of `verb` on exactly `refs`. The
    answer is a verdict by default. `answer="converse"` is words, as the
    night's walk answers a clarify."""
    sc.answers.setdefault((verb, tuple(refs)), []).append((per_item, text, answer))


def _frontier(conn) -> list[str]:
    """The loop's own frontier, with each wake's detail, for an error's text.
    The cockpit's read-only view keeps a quarantined key that the loop
    drops, so it would name a wake that the loop cannot pick."""
    conn.execute("SAVEPOINT error_frontier")
    try:
        return [f"{key_of(conn, w)} ({w.detail})" if w.detail else key_of(conn, w)
                for w in scheduler.frontier(conn, True)]
    finally:
        conn.execute("ROLLBACK TO error_frontier")
        conn.execute("RELEASE error_frontier")


def _session_for(sc: Scene, conn, wake: Wake) -> Session:
    key = key_of(conn, wake)
    if key in sc.landing:
        return sc.landing.pop(key)
    queue = sc.seats.get(key)
    if queue:
        return queue.pop(0)
    role_kind = f"{wake.role}|{wake.kind}"
    any_ = sc.seats.get(role_kind)
    if callable(any_):
        sc.ids.setdefault("_every_unused", set()).discard(role_kind)
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
        sc.ids["_lines"] = lines
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
        if not queue and ask.verb == "present":
            # The door appends the request's rows to the refs the Liaison
            # sent (frame 190's design, 2.1). A script names the refs the
            # seat sent, so the stamped tail is read off before the lookup.
            # The door records the rows it added, the code line's key
            # `guess:<item>` among them (frame 298, pass 2).
            stamped = set(principal.request_rows(self.sc.conn, ask.refs)) | set(
                principal.door_rows(self.sc.conn, ask.message_id, "stamped"))
            for n in range(len(ask.refs) - 1, 0, -1):
                if not set(ask.refs[n:]) <= stamped:
                    break
                queue = self.sc.answers.get((ask.verb, tuple(ask.refs[:n])))
                if queue:
                    break
        if not queue:
            return None
        per_item, text, verb = queue.pop(0)
        self.sc.steps.append(f"principal|{ask.verb}|{','.join(ask.refs)}")
        # The twin check replays the answers by the step they came at.
        self.sc.ids.setdefault("log_answers", []).append(
            (len(self.sc.ids.get("log", [])), ask.verb, list(ask.refs), per_item, text, verb))
        return principal.Answer(verb, text=text, per_item=per_item)


class _NoServer:
    """The backend that `loop.step` receives. The seam on `run_session`
    replaces it in every session, so a call here is a session that the seam
    missed. It names no host, so `note_spill` reads no card."""
    name = "no server"

    def complete(self, *a, **kw):
        raise AssertionError("a session reached the backend that names no seat")


def _merged(conn) -> int:
    return conn.execute("SELECT COUNT(*) FROM batches WHERE status = 'merged'").fetchone()[0]


def answer_replies(conn, text: str) -> list[str]:
    """The walk's answer to a Liaison sentence with no page under it: the
    reply is marked answered, and the principal says `text` as a new turn
    whose cause is the reply. The SQL is `probes/walk.py`'s own, so the ids
    are the walk's: `e_p<n>` and `m_p<n>` in the thread `t_p1`."""
    made = []
    for rep in principal.pending_replies(conn):
        conn.execute("UPDATE messages SET status = 'answered' WHERE id = ?",
                     (rep.message_id,))
        n = 1 + conn.execute("SELECT COUNT(*) FROM entries WHERE id LIKE 'e_p%'").fetchone()[0]
        seq = 1 + (conn.execute("SELECT MAX(seq) FROM messages").fetchone()[0] or 0)
        ts = 1 + (conn.execute("SELECT MAX(ts_order) FROM entries").fetchone()[0] or 0)
        conn.execute("INSERT INTO entries (id, author, ts_order, text) "
                     "VALUES (?,'principal',?,?)", (f"e_p{n}", ts, text))
        conn.execute("INSERT INTO messages (id, cause_id, cause_kind, thread_id, from_role, "
                     "to_role, verb, body_refs, seq) VALUES (?,?,'message','t_p1','principal',"
                     "'liaison','converse',?,?)",
                     (f"m_p{n}", rep.message_id, f'["e_p{n}"]', seq))
        made.append(f"e_p{n}")
    conn.commit()
    return made


def step(sc: Scene, quiet: bool = False) -> loop.Step:
    """One iteration of the night's walk (`probes/walk.py`), with the
    scene's scripts: the principal answers every open ask, the walk answers
    every Liaison sentence with no page, and then one `loop.step` runs with
    no principal, as the walk calls it. Fails when an ask stays open after
    the principal's turn, or the loop is quiescent and `quiet` is false, or
    a session does not commit, or meets a refusal.

    The walk answers every ask before it steps, so an ask that the script
    leaves open is a state that no night reaches."""
    conn = sc.conn
    if principal.pending_asks(conn):
        principal.pump(conn, _Principal(sc))
        conn.commit()
        left = open_asks(sc)
        if left:
            raise AssertionError(f"{sc.name}: the principal's script has no answer for "
                                 f"{left}; the walk answers every ask before it steps")
    for entry in answer_replies(conn, WALK_ANSWER):
        sc.ids.setdefault("log_replies", []).append((len(sc.ids.get("log", [])), entry))
    merged = _merged(conn)
    with _no_venv(), _seated(sc):
        sc.ids["_allow"] = ()
        sc.ids["_lines"] = None
        st = loop.step(conn, backend=_NoServer(), pins=sc.pins)
    conn.commit()
    key = key_of(conn, st.wake) if st.wake is not None else None
    sc.ids.setdefault("log", []).append({"key": key, "lines": sc.ids["_lines"]})
    # The walk says a sentence only at quiet or after a merge.
    sc.ids["_may_speak"] = st.wake is None or _merged(conn) > merged
    if st.wake is None:
        if quiet:
            return st
        raise AssertionError(f"the loop is quiescent: {st.note}; the frontier: "
                             f"{_frontier(conn)}")
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


def play_to_quiet(sc: Scene, limit: int = LIMIT) -> None:
    """Turn the crank until a step finds the loop quiet, where the night's
    walk ends and the next walk says the next sentence."""
    for _ in range(limit):
        if step(sc, quiet=True).wake is None:
            return
    raise AssertionError(f"{sc.name}: not quiet after {limit} steps; the last: "
                         f"{sc.steps[-8:]}")


def say(sc: Scene, text: str) -> str:
    """The principal's sentence, through `talk.open_with`. A night's walk
    says one sentence when it starts, and the walk before it ended at quiet
    or at a merge. So a sentence at any other point fails the build, and so
    does a second sentence with no step between."""
    from ..tools.talk import open_with
    if not sc.ids.get("_may_speak", "log" not in sc.ids):
        last = sc.ids["log"][-1]["key"] if sc.ids.get("log") else "a sentence"
        raise AssertionError(f"{sc.name}: the walk says no sentence here: the last step "
                             f"was {last}, not quiet and no merge")
    sc.ids["_may_speak"] = False
    sc.ids.setdefault("log_said", []).append((len(sc.ids.get("log", [])), text))
    return open_with(sc.conn, text)


def end_frontier(sc: Scene) -> list[str]:
    """The frontier at the scene's end, by key: what the loop would pick
    from. It is `scheduler.frontier`, the loop's own, and not the cockpit's
    read-only view. The loop's frontier writes its quarantines first. The
    connection is in autocommit mode, so the read runs inside a savepoint
    that rolls back, and the scene does not move."""
    conn = sc.conn
    conn.execute("SAVEPOINT end_frontier")
    try:
        return [key_of(conn, w) for w in scheduler.frontier(conn, True)]
    finally:
        conn.execute("ROLLBACK TO end_frontier")
        conn.execute("RELEASE end_frontier")


def open_asks(sc: Scene) -> list[tuple]:
    """The asks open to the principal, by verb and refs."""
    return [(a.verb, *a.refs) for a in principal.pending_asks(sc.conn)]


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


def _base(name: str, tmp: Path, bind: bool = False,
          prepare: Callable[[gitfixture.SampleRepo], None] | None = None,
          pins: Pins = PINS) -> Scene:
    """The sample repository, a database, and the onboarding's survey phase.
    Every night is onboarded. Without an onboarding, a Developer's first
    commit indexes the code, the phase turns to `frame`, and the scheduler
    holds every deliver until the frame is judged. `prepare` changes the
    scene's copy of the repository before the onboarding reads it. The
    template stays as it is, so no recorded case of the sample goes stale."""
    repo = gitfixture.make(tmp, name="scene")
    if prepare is not None:
        prepare(repo)
    conn = init_db(tmp / "rota.db")
    conn.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)",
                 (str(repo.root),))
    conn.commit()
    sc = Scene(name, conn, repo, tmp, pins=pins)
    survey(sc, bind)
    return sc


# -- the shared seats ------------------------------------------------------------------

def item(sc: Scene, n: int, priority: int, words: tuple | None = None) -> None:
    """The principal's sentence of item `n`, and the seats that carry it to a
    batch `b<n>` with one ticket and one criterion: the Liaison's segment
    and confirm, the three delivers, the Vision Keeper's item, the
    Terminologist's term, the Architect's read of the model, the sign-off
    through the Liaison's present and relay, the Vision Keeper's priority,
    the slicing, the criterion and the grouping. The principal approves the
    confirm and the sign-off. `words` replaces `ITEMS[n]`."""
    sentence, problem, term, sense, ticket, criterion = words or ITEMS[n]
    conn = sc.conn
    mid = say(sc, sentence)
    entry = json.loads(conn.execute("SELECT body_refs FROM messages WHERE id = ?",
                                    (mid,)).fetchone()[0])[0]
    sc.ids[f"entry{n}"] = entry
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
    # The Architect guesses the code of each request before the sign-off
    # (frame 298's design, 4.1). It writes the files the scene annotates
    # later, or the first source file of the index.
    every(sc, "architect|tick:guess", _guess)
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


def _guess(sc: Scene, wake: Wake) -> list[str]:
    """The Architect's guess for the item the wake names: the paths the scene
    annotates for it, or the first source file the index holds."""
    item_id = wake.refs[0]
    paths = sc.ids.get(f"guess_paths:{item_id}")
    if not paths:
        row = sc.conn.execute(
            "SELECT grain FROM code_index WHERE grain_kind = 'path' "
            "AND grain NOT LIKE 'tests/%' ORDER BY grain LIMIT 1").fetchone()
        paths = [row["grain"]] if row else ["README.md"]
    return [f"TOOL: batches.guess(item_id={item_id!r}, paths={list(paths)!r}"
            f"{_new_files(sc, paths)})"]


def _new_files(sc: Scene, paths: list[str]) -> str:
    """The `new_files` argument for the paths the index does not hold, or
    nothing. The ops refuse an unindexed file the call does not name as new
    (frame 302)."""
    indexed = {r["grain"] for r in sc.conn.execute(
        "SELECT grain FROM code_index WHERE grain_kind = 'path'")}
    new = [p for p in paths if p not in indexed]
    return f", new_files={new!r}" if new else ""


def annotate(sc: Scene, n: int, paths: list[str], read: bool = True) -> None:
    """The Architect's touch set for batch `b<n>`, and the Liaison's touch
    note, which the principal reads and acknowledges when `read`."""
    b, i = f"b{n}", f"i{n}"
    sc.ids[f"guess_paths:{i}"] = list(paths)
    # The index is read at the wake, because a batch can index a file first.
    seat(sc, f"architect|tick:annotate|{b}", Session(lambda sc, wake: [
        f"TOOL: batches.annotate(batch_id={b!r}, paths={paths!r}"
        f"{_new_files(sc, paths)})"]))
    seat(sc, f"liaison|tick:touch_note|{b},{i}", [
        f"TOOL: msg.present_principal(refs=[{b!r}, {i!r}])"])
    if read:
        rule(sc, "present", [b, i], {i: "approve"})


def walk_turn(sc: Scene, n: int) -> None:
    """The seats for the walk's answer `n` to a Liaison sentence with no
    page. The walk says its stock sentence as a new turn (`answer_replies`).
    The Liaison reads it as work, segments it and asks the principal to
    confirm, the principal approves, and the Liaison ratifies and delivers
    it, as night 121 did at s279 to s281 after each park ask. The three
    seats read their own records against the statement and find nothing to
    add, because the sentence asks for no change."""
    entry, s = f"e_p{n}", f"sp{n}"
    seat(sc, f"vision_keeper|deliver|{s}", ["TOOL: problem.consult()"])
    seat(sc, f"terminologist|deliver|{s}", ["TOOL: glossary.consult()"])
    seat(sc, f"architect|deliver|{s}", ["TOOL: model.consult()"])
    seat(sc, f"liaison|converse|{entry}", [
        "TOOL: brief.intake(verdict='work')",
        f"TOOL: brief.segment(id='{s}', span_entry='{entry}', span_start=0, "
        f"span_end={len(WALK_ANSWER)}, text='{WALK_ANSWER}')",
        f"TOOL: msg.confirm_principal(refs=['{s}'])"])
    rule(sc, "confirm", [s], {s: "approve"})
    seat(sc, f"liaison|verdict|{s}", [
        f"TOOL: brief.ratify(id='{s}')",
        f"TOOL: msg.deliver_vision_keeper(refs=['{s}'])",
        f"TOOL: msg.deliver_terminologist(refs=['{s}'])",
        f"TOOL: msg.deliver_architect(refs=['{s}'])"])


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


# The added line of `UPGRADE` that meets c1. A pass names it (frame 170).
UPGRADE_LINE = "return prorate(amount_cents, days_used, days_in_period)"


# The start of the reply that holds a session's first pass (frame 201, pass 3).
PASS_HELD = "verdicts.emit: before the pass lands, answer for"


def judge(batch: str, result: str = "pass",
          lines: dict | None = None) -> list[str] | Session:
    """The Critic's review. A pass names, by default, c1's line of `UPGRADE`,
    the module that both scenes that judge commit.

    The runner holds the first pass of a session and asks the seat its own
    question (frame 201, pass 3). The scripted seat then takes the route
    that the hold's reply names: it sends the same pass again."""
    if result == "pass" and lines is None:
        lines = {"c1": UPGRADE_LINE}
    named = f", lines={lines!r}" if result == "pass" else ""
    emit = f"TOOL: verdicts.emit(batch_id={batch!r}, result={result!r}{named})"
    head = [f"TOOL: criteria.load(batch_id={batch!r})",
            f"TOOL: tests.load(batch_id={batch!r})", emit]
    if result != "pass":
        return head
    return Session(head + [emit], allow=(PASS_HELD,))


# An empty session on a fix wake: the seat's note is the state, a dispatch
# with no drain.
IDLE = Session([], allow=("ended a tick with nothing done",))
# The walk's own answer to every clarify (`probes/walk.py`, its default).
WALK_ANSWER = "yes to all of it. keep it simple."
# The Tester's test of c1 on `prorate` itself, for a batch with no module.
PRORATE_TEST = ("from src.billing.charges import prorate\n\n\n"
                "def test_an_upgrade_charges_the_days_used():\n"
                "    assert prorate(3000, 10, 30) == 1000\n")
# The Liaison's park message on a parked b1. The door writes the page's rows
# from the records (frame 142, ruled: Roman, 2026-10-08).
PARK_ASK = ["TOOL: msg.present_principal(refs=['i1', 'b1'])"]


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
    turns `tests/test_charges.py` red. The Developer commits once more and
    stays red, then ends three sessions with nothing done, and the key is
    quarantined. The quarantined key stops the bounce, so law 6's three
    rungs wake one by one with nothing done (frame 330). Before frame 330
    the loop went quiet here, and on night 168 that quiet held the one batch
    seat. The Liaison reports the quarantine. The Tester's wake on b1's
    missing test comes next. Its new test row lifts the key
    (`db._lift_quarantines`), and three more empty sessions quarantine the
    key again. The ladder is spent, so no rung wakes. The Liaison reports it
    again, and the loop is quiet. So the walk ends, and the next walk says
    item 2.

    Item 2 ranks above item 1. Right after its grouping b2 can start, and
    the spent ladder parks b1 (`do:park`, frame 86's path). Before frame 330
    the preempt deferred b1 here. The Liaison then sends the park page: the
    item and c1, whose own test is red. The walk with no words approves
    every line. That is the ceiling: the page rests, and the park asks
    nothing more (frame 142, ruled: Roman, 2026-10-08, point 5). b2 then
    starts, takes in the project's tests again under the same ids (frame
    130's wall), and its Developer commits the export. The scene ends when
    the harness has run at b2's head.

    Night 121 holds the same order up to the park, bg_2 from its start at
    s212: two quarantines of `tests_failing` with the Tester between (s224,
    s226, s243), and the preempt after the grouping (s276). The scene now
    departs from night 121 at the ladder and at the park. Night 121 then
    asked three times, because its park ask had no row to rule (s277, s282,
    s287). The page ends that loop."""
    sc = _base("two_batches", tmp)
    play_to_quiet(sc)
    item(sc, 1, 1)
    annotate(sc, 1, ["src/billing/charges.py"])
    seat(sc, "developer|tick:batch_start|b1",
         commit([("src/billing/charges.py", _charges_red())], "prorate the remainder"))
    seat(sc, "developer|tick:tests_failing|b1",
         commit([("src/billing/charges.py", _charges_red(2))], "round the remainder"),
         IDLE, IDLE, IDLE, IDLE, IDLE, IDLE)
    seat(sc, "liaison|tick:quarantined|b1", ["TOOL: msg.present_principal(refs=['b1'])"],
         ["TOOL: msg.present_principal(refs=['b1'])"])
    rule(sc, "present", ["b1"], {"b1": "approve"})
    rule(sc, "present", ["b1"], {"b1": "approve"})
    seat(sc, "tester|tick:tests_missing|b1", encode(PRORATE_TEST))
    _climb(sc, "b1")
    play_to_quiet(sc)
    sc.ids["head1"] = sc.conn.execute(
        "SELECT head_commit FROM batches WHERE id = 'b1'").fetchone()[0]
    item(sc, 2, 2)
    # Item 2's statement is a new request while item 1 is approved and not
    # merged, so the Liaison asks which goes first. The walk answers now,
    # which keeps the park page and the order (frame 193's design, 2.F.10).
    seat(sc, "liaison|tick:request_shift|i1,s2",
         ["TOOL: msg.present_principal(refs=['i1', 's2'])"])
    rule(sc, "present", ["i1", "s2"], {"i1": "now"})
    # The park page numbers the item and c1, whose own test is red. The
    # walk with no words approves every line, which is the ceiling: the
    # page rests, and the park asks nothing more (frame 142).
    seat(sc, "liaison|tick:park_ask|i1,b1", PARK_ASK)
    rule(sc, "present", ["i1", "c1"], {"i1": "approve", "c1": "approve"})
    annotate(sc, 2, [EXPORT_PATH])
    seat(sc, "developer|tick:batch_start|b2",
         commit([(EXPORT_PATH, EXPORT)], "export invoices"))
    play(sc, ran("b2"))
    sc.ids.update(wt1=worktree(sc, "b1"), wt2=worktree(sc, "b2"),
                  charges=harness.inherited_id("tests/test_charges.py"))
    return sc


def _climb(sc: Scene, batch: str) -> None:
    """Seat law 6's three rungs on `batch`, each a session with nothing done.

    A quarantined `tests_failing` key stops the bounce, so the ladder climbs
    and the spent ladder parks the batch (frame 330). Before frame 330 the
    loop went quiet here, and on night 168 that quiet held the seat."""
    from ..core.predicates import LADDER

    for role in LADDER:
        seat(sc, f"{role}|tick:exhausted|{batch}", IDLE)


# -- S2: a merged batch's Tester file is a project test of the next batch ---------

def merged_then_next(tmp: Path) -> Scene:
    """S2. b1 runs the whole path: the Developer's module, the harness, the
    Tester's `test_upgrade.py` at the root, the harness again, a pass verdict
    and the merge, which delivers the test in a commit of its own (click
    night 50). The walk stops at the merge, and the next walk says item 2.
    The merge changed `src/billing` and the root, so the loop picks the
    Terminologist's and the Architect's survey of both areas again, after
    item 2's ratification. b2 then starts, and `harness.inherit` takes the
    delivered file in as a project test of b2. The scene ends when the
    harness has run at b2's head.

    Night 120 holds the same order: bg_1's merge after s149, the next
    sentence at s150, and the surveys of the merged areas at s155 to s158,
    before the next batch. Night 119 merges in its second walk and says the
    third sentence after it."""
    sc = _base("merged_then_next", tmp)
    play_to_quiet(sc)
    item(sc, 1, 1)
    annotate(sc, 1, [UPGRADE_PATH])
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
    play(sc, _has("SELECT 1 FROM batches WHERE status = 'merged'"))
    # The walk stops at the merge, and the next walk says the next sentence.
    item(sc, 2, 2)
    annotate(sc, 2, [EXPORT_PATH])
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
    play_to_quiet(sc)
    item(sc, 1, 1)
    annotate(sc, 1, [UPGRADE_PATH])
    seat(sc, "developer|tick:batch_start|b1",
         commit([(UPGRADE_PATH, UPGRADE)], "charge an upgrade"))
    seat(sc, "tester|tick:tests_missing|b1", encode(TEST_BODY.replace("== 1000", "== 3000")))
    # Frame 200, pass 5: a Developer challenge carries its reason, and the
    # message refs the reason's row. The row's id derives from the reason
    # and the two refs, so the Tester's key names it.
    import hashlib
    reason = ("right code charges 1000 cents for 10 of 30 days, so the test "
              "must assert 1000")
    rid = "d_" + hashlib.sha256(f"{reason}|c1|t1".encode()).hexdigest()[:10]
    seat(sc, "developer|tick:tests_failing|b1", [
        "TOOL: msg.challenge_tester(refs=['c1', 't1'], quotes=["
        "'an upgrade of 3000 cents used 10 of 30 days charges 1000 cents', "
        f"'assert upgrade_charge(3000, 10, 30) == 3000'], reason={reason!r})"])
    seat(sc, f"tester|challenge|c1,t1,{rid}", [
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
    commit, and the next frontier quarantines the key. The quarantined key
    stops the bounce, so law 6's three rungs wake one by one with nothing
    done (frame 330). Before frame 330 the loop went quiet here, and on
    night 168 that quiet held the one batch seat. The Liaison tells the
    principal on the `quarantined` wake, and the loop is then quiet. So the
    walk ends, and the next walk says item 2. Item 2 ranks above item 1.
    Right after its grouping b2 can start, and the spent ladder parks b1
    (`do:park`, frame 86's path). Before frame 330 the preempt deferred b1
    here. The Liaison's `park_ask` wake opens the ask, and the scene ends
    there, before the walk answers it. Night 121 holds the same order, from
    bg_2's start at s212 to the park ask at s277, except the ladder and the
    park. The scene `two_batches` holds the answer.

    The design named b3 behind b1 by a `batch_dep_facts` row (S4). No op in
    `rota/` writes that table, and nights 119 to 124 hold no row in it
    (observed: the review of 906b765, 2026-10-05). So no night reaches "b3
    behind b1", and the scene holds no such row. In the night's order a
    third item can come only at the next quiet, after b2 has run, so the
    scene holds no b3 (the review of 7a056ce0, finding 1). What the scene
    proves for S4 is that the park keeps b1 out of `next_batch`, with b2
    pending beside it."""
    sc = _base("park", tmp)
    play_to_quiet(sc)
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
    _climb(sc, "b1")
    # The walk ends at quiet, and the next walk says item 2.
    play_to_quiet(sc)
    item(sc, 2, 2)
    # The shift question, answered now, as in `two_batches` (frame 193's
    # design, 2.F.10).
    seat(sc, "liaison|tick:request_shift|i1,s2",
         ["TOOL: msg.present_principal(refs=['i1', 's2'])"])
    rule(sc, "present", ["i1", "s2"], {"i1": "now"})
    seat(sc, "liaison|tick:park_ask|i1,b1", PARK_ASK)
    play(sc, lambda conn: scheduler.open_park_ask(conn, "b1"))
    sc.ids.update(key="developer|tick:tests_failing|b1",
                  ask=scheduler.open_park_ask(sc.conn, "b1"))
    return sc


# -- S6: a large module, and the delivery wakes at the night's window ---------------

LEDGER_PATH = "src/billing/ledger.py"
# The night's window. Nights 119 to 126 run every seat at 16384 (`num_ctx` in
# `sessions`), and item 5's rule is about the cut at that window.
NIGHT_PINS = Pins(model="scripted", temperature=0.0, num_ctx=16384)
# The fee rule in the module as found, in the Developer's first commit, and in
# the fix. The criterion asks for 150 cents on 3000 cents ten days late.
FEE_FOUND = "amount_cents * days_late // 1000"
FEE_FIRST = "amount_cents * days_late // 100"
FEE_FIXED = "amount_cents * days_late * 5 // 1000"
LATE = ("charge a fee on a late payment", "a late payment is charged a fee",
        "late fee", "the charge for each day a payment is late",
        "charge late fees",
        "a payment of 3000 cents that is 10 days late is charged a fee of 150 cents")
LATE_TEST = ("from src.billing.ledger import late_fee\n\n\n"
             "def test_a_late_payment_is_charged_its_fee():\n"
             "    assert late_fee(3000, 10) == 150\n")
LATE_TEST_PATH = "test_late_fee.py"
# The project's own test of the ledger. The Developer's first commit adds a
# cent to every rate, so this test goes red and the diff holds every rate.
LEDGER_TEST_PATH = "tests/test_ledger.py"
LEDGER_TEST = ("from src.billing.ledger import rate_001, rate_199\n\n\n"
               "def test_a_rate_is_per_mille_of_the_amount():\n"
               "    assert rate_001(3000) == 3\n"
               "    assert rate_199(3000) == 597\n")


def ledger(fee: str = FEE_FOUND, extra: str = "") -> str:
    """A module of about 1,000 lines with a `__future__` header. `late_fee`
    sits at about line 900. `extra` goes at the end of every rate, so a
    change of it is a diff of 199 lines. The text is the same on every
    build, so two builds give the same rows."""
    lines = ['"""The ledger: one small rule for each kind of charge."""',
             "from __future__ import annotations", "", ""]

    def rate(n: int) -> list[str]:
        return [f"def rate_{n:03d}(amount_cents: int) -> int:",
                f'    """The charge of kind {n}: {n} per mille of the amount."""',
                f"    return amount_cents * {n} // 1000{extra}", "", ""]
    for n in range(1, 180):
        lines += rate(n)
    lines += ["def late_fee(amount_cents: int, days_late: int) -> int:",
              '    """The fee for a payment that is `days_late` days late."""',
              f"    return {fee}", "", ""]
    for n in range(180, 200):
        lines += rate(n)
    return "\n".join(lines).rstrip("\n") + "\n"


def _commit_ledger(repo: gitfixture.SampleRepo) -> None:
    """The project's own module, committed on the scene's copy before the
    onboarding, as a module that a night's repository already holds."""
    (repo.root / LEDGER_PATH).write_text(ledger(), encoding="utf-8", newline="\n")
    (repo.root / LEDGER_TEST_PATH).write_text(LEDGER_TEST, encoding="utf-8", newline="\n")
    gitfixture.git(repo.root, "add", LEDGER_PATH, LEDGER_TEST_PATH)
    gitfixture.git(repo.root, "commit", "-q", "-m", "the ledger")


def large_module(tmp: Path) -> Scene:
    """S6. The repository holds `src/billing/ledger.py`, 1,000 lines with a
    `__future__` header, and its `late_fee` at about line 900 charges too
    little. The project's `tests/test_ledger.py` tests two rates. Every
    session runs at the night's window, 16384. Item 1 asks for the fee that
    the criterion names. The scene holds the four delivery wakes of one
    batch, each a session of the loop's own pick:

    1. `developer|tick:batch_start|b1`: the Developer writes the module
       whole with a fee that is still wrong and a cent added to every rate,
       and commits. The project's test goes red, and the diff holds 199
       changed lines. The loop picks the fix wake before the Tester's, so
       three empty fix sessions quarantine the key. The quarantined key
       stops the bounce, so law 6's three rungs wake one by one with
       nothing done (frame 330). Before frame 330 the loop went quiet
       here, and on night 168 that quiet held the one batch seat. No other
       batch waits, so nothing parks b1. The Liaison reports the
       quarantine. Night 121 holds the same order up to the ladder (scene
       `two_batches`).
    2. `tester|tick:tests_missing|b1`: the Tester encodes the criterion's
       test at the root. Its new row lifts the key, and the harness runs
       the test red.
    3. `developer|tick:tests_failing|b1`, the last fix session: the wake
       holds the batch's red test, the project's red test and the large
       diff, as night 119's s259 did (frame 134). The Developer writes the
       rates back and the right fee, and commits. The harness runs green.
    4. `developer|tick:verdict_failed|b1`, after the Critic claims that the
       test encodes c1 and fails the batch on it. The Developer ends the
       session with nothing done.

    The first turn of a session is the wake as the seat read it, after the
    cut. `wake_prompt` reads it. The scene ends when the fourth wake's
    session is on record."""
    sc = _base("large_module", tmp, prepare=_commit_ledger, pins=NIGHT_PINS)
    play_to_quiet(sc)
    item(sc, 1, 1, LATE)
    annotate(sc, 1, [LEDGER_PATH])
    seat(sc, "developer|tick:batch_start|b1",
         commit([(LEDGER_PATH, ledger(FEE_FIRST, " + 1"))], "charge the late fee"))
    seat(sc, "tester|tick:tests_missing|b1", [
        "TOOL: tests.triage(criterion_id='c1', verdict='encodable')",
        f"TOOL: tests.encode(id='t1', criterion_id='c1', path={LATE_TEST_PATH!r}, "
        f"body={LATE_TEST!r})"])
    seat(sc, "developer|tick:tests_failing|b1", IDLE, IDLE, IDLE,
         commit([(LEDGER_PATH, ledger(FEE_FIXED))], "charge five per mille a day"))
    _climb(sc, "b1")
    seat(sc, "liaison|tick:quarantined|b1", ["TOOL: msg.present_principal(refs=['b1'])"])
    rule(sc, "present", ["b1"], {"b1": "approve"})
    seat(sc, "critic|tick:review|b1", [
        "TOOL: criteria.load(batch_id='b1')",
        "TOOL: tests.load(batch_id='b1')",
        "TOOL: verdicts.claim_encodes(criterion_id='c1', encodes=True)",
        "TOOL: verdicts.emit(batch_id='b1', result='fail', failed_criterion='c1', "
        "reason='the fee is not rounded to whole cents for every amount')"])
    seat(sc, "developer|tick:verdict_failed|b1", IDLE)
    play(sc, _has("SELECT 1 FROM sessions WHERE role = 'developer' "
                  "AND wake_kind = 'tick:verdict_failed'"))
    return sc


# The four delivery wakes of S6, by the role and the kind of their session.
DELIVERY_WAKES = (("developer", "tick:batch_start"), ("tester", "tick:tests_missing"),
                  ("developer", "tick:tests_failing"), ("developer", "tick:verdict_failed"))


def wake_prompt(sc: Scene, role: str, kind: str) -> str:
    """The first user prompt of the last session of `role` on `kind`: the
    wake as the seat read it, after the cut. The last fix session is the
    one that holds both red tests."""
    row = sc.conn.execute(
        "SELECT t.user FROM turns t JOIN sessions s ON s.id = t.session_id "
        "WHERE s.role = ? AND s.wake_kind = ? ORDER BY s.rowid DESC, t.seq LIMIT 1",
        (role, kind)).fetchone()
    assert row is not None, f"no session of {role} on {kind}"
    return row["user"]


# The header of a pushed block, as `runner.build_prompt` writes it: a blank
# line, then the key. The key is a function name, `artefact.fn`, or the one
# key `the item` (`runner.push_working_set`). A block's own text holds other
# lines in brackets: `[removed lines]` and `[diff]` in `code.diff`, `[text]`
# in `code.prose`, and JSON rows. None of them is a header (the delta review
# of b43b99d6, its fifth low). A TOML table such as `[project.scripts]` in a
# pushed source is dotted too, so `blocks` keeps only a registered artefact.
_BLOCK = re.compile(r"(?<=\n\n)\[([a-z_]+\.[a-z_]+|the item)\]$", re.MULTILINE)
# The note that `runner._render_cut` puts at the end of a cut wake.
_WAKE_CUT_NOTE = re.compile(r"\nCUT your wake: [\d,]+ of [\d,]+ characters are not shown\.")


def blocks(prompt: str) -> dict[str, bool]:
    """Each pushed block of a wake, by its key, and whether it is whole. The
    wake cut keeps the front and ends with its note. So every block before
    the last is whole, and the last block is whole only when no note ends
    the wake."""
    from ..roles import api
    head, marker, pushed = prompt.partition("\nAlready run for you")
    artefacts = {t for t, _ in api.REGISTRY} | {"msg"}
    keys = [k for k in (_BLOCK.findall(pushed) if marker else [])
            if k == "the item" or k.split(".", 1)[0] in artefacts]
    cut = bool(_WAKE_CUT_NOTE.search(prompt))
    return {k: not (cut and i == len(keys) - 1) for i, k in enumerate(keys)}


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
    play_to_quiet(sc)
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
            "challenged": challenged, "park": park, "critic": critic, "review": review,
            "large_module": large_module}
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
    unused(sc, name)
    return sc


def unused(sc: Scene, name: str) -> None:
    """Fail when a session, a function, a landing or an answer of the
    scripts was never asked for: the scene then claims a step it did not
    take."""
    left = {k: len(v) for k, v in sc.seats.items() if isinstance(v, list) and v}
    left.update({k: "every" for k in sc.ids.get("_every_unused", ())})
    left.update({k: "landing" for k in sc.landing})
    left.update({f"principal|{v}|{','.join(r)}": len(q) for (v, r), q in sc.answers.items()
                 if q})
    assert not left, f"{name}: the loop never asked for {left}"


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
    batch's worktree when it is sent. `holds` names words that the refusal
    must hold anywhere in its text. With `step`, a call that lands is
    committed on a copy of the scene, and one `loop.step` runs on the copy,
    so the row's failure says what the landed call does to the loop."""
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
    holds: tuple = ()
    step: bool = False

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
# Night 126's s156, turn 2, as the seat sent it (`turns.completion`): a body
# in single quotes that holds `\"` inside a list. The parser reads `\"` as
# `"`, so line 6 of the body holds `["{"key": "value"}"]`, which is not
# Python. The body is the night's bytes (the delta review of b43b99d6, its
# fourth low). The id, the criterion and the path are the scene's, and the
# batch is the wake's.
_S156_SENT = (
    r"""TOOL: tests.encode(id='inh_echo_json_01', criterion_id='echo_json_compact', """
    r"""path='tests/test_utils/test_echo_json_compact.py', body='def test_echo_json_compact():"""
    r"""\n    from click.testing import CliRunner\n    from src.click.utils import echo_json"""
    r"""\n    \n    runner = CliRunner()\n    result = runner.invoke(echo_json, """
    r"""["{\"key\": \"value\"}"], catch_exceptions=False)\n    assert result.exit_code == 0"""
    r"""\n    assert result.output.strip() == "{\\"key\\": \\"value\\"}"\n    # Check for """
    r"""single newline at end\n    assert result.output.endswith("\\n")\n    # Check no """
    r"""extra newlines\n    assert result.output.count("\\n") == 1', batch_id='bg_1')""")
_S156 = (_S156_SENT
         .replace("id='inh_echo_json_01', criterion_id='echo_json_compact', "
                  "path='tests/test_utils/test_echo_json_compact.py'",
                  "id='t_s156', criterion_id='c2', path='tests/test_export_json.py'")
         .replace(", batch_id='bg_1')", ")"))
# The line that the parser gives, and the escape that broke it.
_S156_LINE = 'result = runner.invoke(echo_json, ["{"key": "value"}"], catch_exceptions=False)'
_S156_QUOTE = '\\"'


def _parsed(line: str) -> tuple[str, tuple]:
    """The op and the arguments of one `TOOL:` line, as the parser reads it
    from a reply, so the row carries what the seat's text became."""
    from ..llm import toolproto
    call, = toolproto.extract(line)
    return call.name, tuple(call.args.items())


def _message(role: str, verb: str, ref: str) -> Wake:
    """The wake of the newest message of `verb` to `role` whose refs hold
    `ref`. The scene's own id is read when the call is sent."""
    return Wake(role, "message", f"m?{verb}:{ref}", detail=verb, refs=())


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
        # Night 126's s156: the seat's `\"` inside a single-quoted body. The
        # door says that the body is no test, and names neither the line
        # that broke nor the quote that broke it (frame 166). The row pins
        # no first words, so a repair that rewrites the sentence's start
        # turns it green (the delta review of b43b99d6, its fourth low).
        Call("two_batches", "a body whose escaped quote breaks a line", t2,
             *_parsed(_S156), "tests_encode", "",
             held="frame 166", before=_triage("c2"), holds=(_S156_LINE, _S156_QUOTE)),
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
        # Night 126's s249, turn 5: a word in the integer column
        # `items.priority`. The door admitted it, and the next step crashed
        # in `next_batch` on bg_3's sort key. Frame 164's scalar door in
        # `Sandbox.call` refuses it now. With `step`, a call that lands again
        # shows what the next step raises on b2's sort key. The park ends as
        # night 126 did, b1 parked and b2 pending. On `two_batches` no batch
        # is a candidate of `next_batch` at the end, so no step there reads
        # the word.
        Call("park", "a word for a priority", _message("vision_keeper", "relay", "i2"),
             "problem.prioritize", (("id", "i2"), ("priority", "high")),
             "call", "problem.prioritize: priority='high' is a word where "
                     "problem.prioritize takes a whole number", step=True),
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
        # The review of 2d7cc73: a Critic's session fails the batch while the
        # same Critic's challenge, sent in an earlier session, is open. Today
        # the fail lands. No ruling says whether a door must refuse it, so
        # the row is a question and not a strict xfail. The state is on the
        # review's second build, after the Critic's challenge lands and
        # before the Tester answers it. It is not the loop's pick: after the
        # challenge lands, the frontier is the Tester's challenge wake and
        # then the Critic's review (observed: pass 8's `lands8.py`,
        # 2026-10-06). So a night reaches this state only when the Tester's
        # session on the challenge fails or is skipped. Night 120's s146 is the
        # other shape, the challenge and the fail in one session, and the
        # `critic` row above holds it (the review of 7a056ce0, finding 3).
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
    # No ledger call comes first. Frame 204 pass 1 (b00aaa59): the literal
    # door logs the literals a test chooses by itself, and `ledger.log`
    # needs a `kind` that this call never gave.
    for n, path in enumerate(sorted(p for p in FILES if p.startswith("tests/"))):
        out.append(Call("two_batches", f"the project test {path} as an encode", t2,
                        "tests.encode", _encode(f"sw{n}", "c2",
                                                path.replace("tests/test_", "tests/test_sw_"),
                                                DISK + path), before=_triage("c2")))
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
    """The wake with the scene's own message id where the call names `m_ch`,
    or a message by its verb and a ref (`_message`)."""
    if wake.kind == "message" and wake.message_id == "m_ch":
        return Wake(wake.role, "message", sc.ids["challenge"], detail=wake.detail,
                    refs=wake.refs)
    if wake.kind == "message" and wake.message_id.startswith("m?"):
        verb, _, ref = wake.message_id[2:].partition(":")
        row = sc.conn.execute(
            "SELECT id FROM messages WHERE to_role = ? AND verb = ? AND EXISTS "
            "(SELECT 1 FROM json_each(body_refs) WHERE value = ?) ORDER BY seq DESC LIMIT 1",
            (wake.role, verb, ref)).fetchone()
        assert row is not None, f"{sc.name} holds no {verb} to {wake.role} on {ref}"
        return Wake(wake.role, "message", row["id"], detail=wake.detail, refs=wake.refs)
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
    root = _root(sc, call.wake.refs[0] if call.wake.refs else None)
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


def land_and_step(sc: Scene, call: Call) -> str:
    """Commit the call's writes on a copy of the scene's database, as the
    runner commits a session (`db.session_commit`), and run one `loop.step`
    on the copy. Returns what the step raised, or an empty string. The
    scene's own database does not move. The copy names the scene's
    worktrees, so a row steps only while its door admits the call, and the
    step that a refusal would stop never runs."""
    from ..core import db, runner
    copy = sqlite3.connect(":memory:", isolation_level=sc.conn.isolation_level)
    copy.row_factory = sqlite3.Row
    sc.conn.backup(copy)
    try:
        wake = _real_wake(sc, call.wake)
        batch = call.wake.refs[0] if call.wake.refs else None
        sb = runner.session_sandbox(copy, wake, batch_id=batch)
        root = _root(sc, batch)
        for op, args in call.before:
            sb.call(op, **_filled(root, args))
        sb.call(call.op, **_filled(root, call.args))
        db.session_commit(copy, db.SessionResult(
            session_id="s_catalogue", role=wake.role, wake_kind=wake.kind,
            writes=[runner._as_write(w) for w in sb.ctx.writes]))
        copy.commit()
        try:
            with _no_venv():
                loop.step(copy, backend=_NoServer(), pins=sc.pins)
        except Exception as exc:                           # noqa: BLE001
            return f"{type(exc).__name__}: {exc}"
        return ""
    finally:
        copy.close()


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


def _seat_review_landings(sc: Scene) -> None:
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


# The seats that each scene's landings need, by scene (the review of
# 7a056ce0, finding 5).
LANDING_SEATS: dict[str, Callable[[Scene], None]] = {"review": _seat_review_landings}


def seat_landings(sc: Scene, name: str) -> None:
    """Seat the sessions that the loop picks between the landings of `name`."""
    LANDING_SEATS.get(name, lambda sc: None)(sc)


def land_all(sc: Scene, name: str, after: Callable[[str], None] = lambda call: None) -> None:
    """Land each call of `LANDINGS[name]` in order, run `after` on the name of
    each, then fail when a seat of the landings was never asked for."""
    seat_landings(sc, name)
    for key, call in LANDINGS.get(name, []):
        land(sc, key, call)
        after(call)
    unused(sc, name)


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
# `test_run_journal.output` keeps every run's text, run time and all (frame
# 309), so a second build differs there by a hundredth of a second, and the
# gate's retry, which runs a scene file without its first build, hid that as
# flaky at three gates (observed: plans/flaky-scene-again-probe.md,
# 2026-10-23).
TIMED = {"test_runs.output", "test_run_journal.output", "turns.user",
         "turns.system"}
# A prompt that holds a run time has its own hash. The hash is the free part:
# `sessions.prompt_hash` becomes a token, and so does the `prompt_hash` key
# inside `sessions.pins_json`, whose other pins must repeat.
HASHED = {"sessions.prompt_hash"}
PINNED = {"sessions.pins_json"}
FREE: tuple[str, ...] = ()
# The config rows whose value is the clock at onboarding.
CLOCK_KEYS = {"created_at"}
# The columns that hold the clock alone: SQLite's `datetime('now')`. These are
# the two columns of the schema whose default is the clock. A landed ruling
# on a finding writes the second (observed: pass 8's twin check of the
# review's landings, 2026-10-06).
CLOCKS = {"config_history.at", "finding_rulings.at"}
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
