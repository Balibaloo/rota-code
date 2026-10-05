"""
The tests that every scene file shares (frame 144, item 3).

Each `test_scene_<name>.py` takes these by `make(name)`. A scene is built
once per module and read by every test in it. A catalogue call and a sweep
call go through `Sandbox.call` and never commit, so the scene does not
move. The conftest's follow check and fact check run on every refusal
that a call meets. One file per scene lets the gate's workers build the
scenes side by side. A scene that goes on from another (`scenes.AFTER`)
shares that scene's module and its build.
"""
from __future__ import annotations

import time
import warnings

import pytest

from rota.core import sandbox
from rota.testkit import scenes

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
    assert exc is not None, f"{call.op} landed: {call.args}"
    site = sandbox._raise_site(exc)
    top = site.rsplit(" in ", 1)[-1] if site else ""
    assert call.door in site.split(" < ")[-1] or top == call.door, (site, str(exc))
    assert str(exc).startswith(call.words), str(exc)
    return ""


def make(name: str, end: list[str], attempts: list[tuple],
         parts: tuple[str, ...] = ("calls", "again"),
         fixture: str = "scene", after: str | None = None) -> dict:
    """The fixture and the shared tests of the scene `name`, whose frontier
    at its end is `end`, and whose `tick_attempts` rows at its end are
    `attempts`. `calls` holds the catalogue, the sweep and the
    check that the calls move nothing. `again` holds the second build of
    the scene's whole chain and the landings. With `after`, the fixture
    goes on from the fixture of that name, so the module's tests of that
    scene must come first in the file."""
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
        sc.ids[key] = scenes.rows(sc, FREE)
        sc.ids[f"end:{name}"] = scenes.end_frontier(sc)
        sc.ids[f"attempts:{name}"] = [tuple(r) for r in sc.conn.execute(
            "SELECT tick_key, attempts, quarantined, reported FROM tick_attempts "
            "ORDER BY tick_key")]
        yield sc
        if not after:
            sc.close()

    def test_the_loop_ends_at_the_scenes_frontier(request):
        # The action wakes and the ready wakes, by key: what the loop would
        # pick from next. A guard that keeps a wake out, such as the park
        # ask's once, goes red here when it is removed. The counts are the
        # loop's bound: a lift that never runs, or a harness that spends an
        # attempt, leaves another row.
        scene = request.getfixturevalue(fixture)
        assert scene.ids[f"end:{name}"] == end
        assert scene.ids[f"attempts:{name}"] == sorted(attempts)

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

    def test_a_second_build_gives_equal_rows_and_lands_a_right_call_per_op(request, tmp_path):
        base = request.getfixturevalue(fixture)
        again = None
        try:
            for n in scenes.chain(name):
                again = scenes.build(n, tmp_path, again)
                got = scenes.rows(again, FREE)
                moved = {t for t in got if got[t] != base.ids[f"rows:{n}"].get(t)}
                assert not moved, f"{n}: the tables that differ: {sorted(moved)}"
            # `send` stages a call and never commits. One right call of each
            # op goes through a whole session on this build, each on the
            # loop's own pick, so the doors of the commit path meet it too.
            scenes.seat_landings(again)
            for wake, call in scenes.LANDINGS.get(name, []):
                scenes.land(again, wake, call)
                for row in scenes.catalogue():
                    if row.at == call:
                        today = judge(again, row)
                        if today:
                            warnings.warn(today)
        finally:
            if again is not None:
                again.close()

    out = {fixture: _scene,
           f"test_the_loop_ends_at_the_scenes_frontier{tag}":
               test_the_loop_ends_at_the_scenes_frontier}
    if "calls" in parts:
        out.update({
            f"test_a_known_wrong_call_is_refused_by_its_door{tag}":
                test_a_known_wrong_call_is_refused_by_its_door,
            f"test_a_right_call_lands{tag}": test_a_right_call_lands,
            f"test_the_calls_leave_the_scene_as_it_was_built{tag}":
                test_the_calls_leave_the_scene_as_it_was_built})
    if "again" in parts:
        out[f"test_a_second_build_gives_equal_rows_and_lands_a_right_call_per_op{tag}"] = \
            test_a_second_build_gives_equal_rows_and_lands_a_right_call_per_op
    return out
