"""
The tests that every scene file shares (frame 144, item 3).

Each scene has two files. `test_scene_<name>.py` takes `make(name, ...)`:
it builds the scene once per module and reads it in every test. A
catalogue call and a sweep call go through `Sandbox.call` and never commit,
so the scene does not move. `test_scene_<name>_again.py` takes
`make_again(name)`: it builds the scene a second time and lands one right
call of each op through a whole session, which moves that build. One build
per file lets the gate's workers build the ten units side by side (the
review of 7a056ce0, finding 8). A scene that goes on from another
(`scenes.AFTER`) shares that scene's files and its build.

The two builds of a scene meet in a directory that the run's workers
share. Each file writes the rows of its build there, and the file that
finishes second compares the two. So each run compares the two builds
once, whatever the order of the files. A run of one file alone compares
nothing. The second build's test prints what each scene of its chain met.

The conftest's follow check and fact check run on every refusal that a
call meets.
"""
from __future__ import annotations

import json
import os
import time
import warnings
from pathlib import Path

import pytest

from rota.core import sandbox
from rota.testkit import scenes
from rota.tools import invariants

# The columns that two builds may give differently. `scenes.rows` already
# makes each clock's reading a token, so no column is dropped whole.
FREE = scenes.FREE


def _param(call):
    marks = [pytest.mark.xfail(strict=True, reason=f"held by {call.held}")] if call.held else []
    return pytest.param(call, id=call.name, marks=marks)


def _none():
    return [pytest.param(None, marks=pytest.mark.skip(reason="no row"))]


def judge(scene, call) -> str:
    """Send a catalogue row, and check that its door refuses it with its
    words. A question gates nothing: the return is what today's doors do,
    in words for a person."""
    exc = scenes.send(scene, call)
    if call.question:
        today = "lands" if exc is None else f"is refused: {str(exc)[:160]}"
        return f"an open question, {call.question} Today the call {today}."
    # A row that a door answers names the door and its words. A held row
    # has no door yet, so it has no words to name.
    assert call.held or (call.door and call.words), call.name
    if exc is None and call.step:
        crash = scenes.land_and_step(scene, call)
        raise AssertionError(f"{call.op} landed: {call.args}; the next loop.step "
                             f"{'raised ' + crash if crash else 'ran'}")
    assert exc is not None, f"{call.op} landed: {call.args}"
    site = sandbox._raise_site(exc)
    top = site.rsplit(" in ", 1)[-1] if site else ""
    assert call.door in site.split(" < ")[-1] or top == call.door, (site, str(exc))
    assert str(exc).startswith(call.words), str(exc)
    missing = [w for w in call.holds if w not in str(exc)]
    assert not missing, f"the refusal does not hold {missing}: {exc}"
    return ""


def _meeting(factory) -> Path:
    """The directory that every worker of this run shares. Under xdist each
    worker's base directory sits in the run's own directory."""
    base = factory.getbasetemp()
    root = base.parent if os.environ.get("PYTEST_XDIST_WORKER") else base
    path = root / "scene-rows"
    path.mkdir(parents=True, exist_ok=True)
    return path


def meet(factory, name: str, side: str, rows: dict) -> str:
    """Write this build's rows, and compare them with the other build's
    rows when those are there. Returns what happened, in words."""
    here = _meeting(factory)
    mine = {t: [repr(r) for r in v] for t, v in rows.items()}
    tmp = here / f"{name}.{side}.tmp"
    tmp.write_text(json.dumps(mine), encoding="utf-8")
    os.replace(tmp, here / f"{name}.{side}.json")
    other = here / f"{name}.{'again' if side == 'first' else 'first'}.json"
    if not other.exists():
        return "the other build is not done yet, and it compares"
    theirs = json.loads(other.read_text(encoding="utf-8"))
    moved = sorted(t for t in set(mine) | set(theirs) if mine.get(t) != theirs.get(t))
    assert not moved, f"{name}: the tables that differ between the two builds: {moved}"
    return "equal"


def _invariant(name: str, known: dict[str, str]):
    marks = ([pytest.mark.xfail(strict=True, reason=f"held by {known[name]}")]
             if name in known else [])
    return pytest.param(name, id=name, marks=marks)


def make(name: str, end: list[str], attempts: list[tuple], asks: list[tuple],
         fixture: str = "scene", after: str | None = None,
         known: dict[str, str] | None = None) -> dict:
    """The fixture and the shared tests of the scene `name`, whose frontier
    at its end is `end`, whose `tick_attempts` rows at its end are
    `attempts`, and whose open asks at its end are `asks`, by verb and refs.
    With `after`, the fixture goes on from the fixture of that name, so the
    module's tests of that scene must come first in the file. `known` names
    the invariants that the scene's end breaks today, each with the frame
    that holds the fault."""
    known = known or {}
    tag = "" if fixture == "scene" else f"_{name}"
    key = f"rows:{name}"

    @pytest.fixture(scope="module", name=fixture)
    def _scene(request, tmp_path_factory):
        t = time.perf_counter()
        if after:
            sc = scenes.build(name, None, request.getfixturevalue(after))
        else:
            sc = scenes.build(name, tmp_path_factory.mktemp(name))
        sc.ids[f"built_in:{name}"] = round(time.perf_counter() - t, 1)
        sc.ids[f"end:{name}"] = scenes.end_frontier(sc)
        sc.ids[key] = scenes.rows(sc, FREE)
        sc.ids[f"met:{name}"] = meet(tmp_path_factory, name, "first", sc.ids[key])
        sc.ids[f"attempts:{name}"] = [tuple(r) for r in sc.conn.execute(
            "SELECT tick_key, attempts, quarantined, reported FROM tick_attempts "
            "ORDER BY tick_key")]
        sc.ids[f"asks:{name}"] = scenes.open_asks(sc)
        yield sc
        if not after:
            sc.close()

    def test_the_loop_ends_at_the_scenes_frontier(request):
        # The frontier is the loop's own, `scheduler.frontier`, by key: what
        # the loop would pick from next. A guard that keeps a wake out, such
        # as the park ask's once, goes red here when it is removed. The
        # counts are the loop's bound: a lift that never runs, or a harness
        # that spends an attempt, leaves another row. The open asks are the
        # principal's: an answer removed from the script leaves its ask open.
        # This module is not a test module, so pytest does not rewrite its
        # asserts, and each one names its own values.
        scene = request.getfixturevalue(fixture)
        assert scene.ids[f"end:{name}"] == end, scene.ids[f"end:{name}"]
        assert scene.ids[f"attempts:{name}"] == sorted(attempts), scene.ids[f"attempts:{name}"]
        assert scene.ids[f"asks:{name}"] == asks, scene.ids[f"asks:{name}"]

    @pytest.mark.parametrize("call", [_param(c) for c in scenes.catalogue()
                                      if c.scene == name and not c.at] or _none())
    def test_a_known_wrong_call_is_refused_by_its_door(request, call):
        today = judge(request.getfixturevalue(fixture), call)
        if today:
            pytest.skip(today)

    @pytest.mark.parametrize("call", [_param(c) for c in scenes.sweep()
                                      if c.scene == name] or _none())
    def test_a_right_call_lands(request, call):
        exc = scenes.send(request.getfixturevalue(fixture), call)
        assert exc is None, f"{call.op} was refused: {exc}"

    def test_the_calls_leave_the_scene_as_it_was_built(request):
        scene = request.getfixturevalue(fixture)
        assert scenes.rows(scene, FREE) == scene.ids[key]

    @pytest.mark.parametrize("invariant", [_invariant(n, known) for n in invariants.INVARIANTS])
    def test_an_invariant_holds_at_the_scenes_end(request, invariant):
        # The design's change 2: I1 to I9, and I10, on every scene's end.
        # The calls of the tests above never commit, so the end is the
        # build's end.
        scene = request.getfixturevalue(fixture)
        found = [str(f) for f in invariants.check(scene.conn) if f.invariant == invariant]
        assert not found, found

    return {fixture: _scene,
            f"test_an_invariant_holds_at_the_scenes_end{tag}":
                test_an_invariant_holds_at_the_scenes_end,
            f"test_the_loop_ends_at_the_scenes_frontier{tag}":
                test_the_loop_ends_at_the_scenes_frontier,
            f"test_a_known_wrong_call_is_refused_by_its_door{tag}":
                test_a_known_wrong_call_is_refused_by_its_door,
            f"test_a_right_call_lands{tag}": test_a_right_call_lands,
            f"test_the_calls_leave_the_scene_as_it_was_built{tag}":
                test_the_calls_leave_the_scene_as_it_was_built}


def make_again(name: str) -> dict:
    """The second build of the scene `name` and of its whole chain, and the
    landings. Each scene of the chain meets the first build's rows."""

    def test_a_second_build_gives_equal_rows_and_lands_a_right_call_per_op(
            tmp_path_factory, tmp_path):
        again = None
        met = []
        try:
            for n in scenes.chain(name):
                again = scenes.build(n, tmp_path, again)
                met.append((n, meet(tmp_path_factory, n, "again",
                                    scenes.rows(again, FREE))))

            def rows_at(call: str) -> None:
                # A row that only a landing reaches is sent after it.
                for row in scenes.catalogue():
                    if row.at == call:
                        today = judge(again, row)
                        if today:
                            warnings.warn(today)
            # `send` stages a call and never commits. One right call of each
            # op goes through a whole session on this build, each on the
            # loop's own pick, so the doors of the commit path meet it too.
            scenes.land_all(again, name, rows_at)
        finally:
            if again is not None:
                again.close()
        print(met)

    return {"test_a_second_build_gives_equal_rows_and_lands_a_right_call_per_op":
            test_a_second_build_gives_equal_rows_and_lands_a_right_call_per_op}
