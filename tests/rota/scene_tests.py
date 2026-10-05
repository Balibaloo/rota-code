"""
The tests that every scene file shares (frame 144, item 3).

Each `test_scene_<name>.py` takes these by `make(name)`. A scene is built
once per module and read by every test in it. A catalogue call and a sweep
call go through `Sandbox.call` and never commit, so the scene does not
move. The conftest's follow check and fact check run on every refusal
that a call meets. One file per scene lets the gate's workers build the
scenes side by side.
"""
from __future__ import annotations

import time

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


def make(name: str, parts: tuple[str, ...] = ("calls", "again")) -> dict:
    """The fixture and the shared tests of the scene `name`. `calls` holds
    the catalogue, the sweep and the check that the calls move nothing.
    `again` holds the second build. A slow scene puts `again` in a file of
    its own, so that a second worker builds it."""

    @pytest.fixture(scope="module")
    def scene(tmp_path_factory):
        t = time.perf_counter()
        sc = scenes.BUILDERS[name](tmp_path_factory.mktemp(name))
        sc.ids["built_in"] = round(time.perf_counter() - t, 1)
        sc.ids["rows"] = scenes.rows(sc, FREE)
        yield sc
        sc.close()

    @pytest.mark.parametrize("call", [_param(c) for c in scenes.catalogue()
                                      if c.scene == name] or _none())
    def test_a_known_wrong_call_is_refused_by_its_door(scene, call):
        # A row that a door answers names the door and its words. A held
        # row has no door yet, so it has no words to name.
        assert call.held or (call.door and call.words), call.name
        exc = scenes.send(scene, call)
        assert exc is not None, f"{call.op} landed: {call.args}"
        site = sandbox._raise_site(exc)
        top = site.rsplit(" in ", 1)[-1] if site else ""
        assert call.door in site.split(" < ")[-1] or top == call.door, (site, str(exc))
        assert str(exc).startswith(call.words), str(exc)

    @pytest.mark.parametrize("call", [_param(c) for c in scenes.sweep()
                                      if c.scene == name] or _none())
    def test_a_right_call_lands(scene, call):
        exc = scenes.send(scene, call)
        assert exc is None, f"{call.op} was refused: {exc}"

    def test_the_calls_leave_the_scene_as_it_was_built(scene):
        assert scenes.rows(scene, FREE) == scene.ids["rows"]

    def test_a_second_build_gives_equal_rows_and_lands_a_right_call_per_op(scene, tmp_path):
        again = scenes.BUILDERS[name](tmp_path)
        try:
            got = scenes.rows(again, FREE)
            moved = {t for t in got if got[t] != scene.ids["rows"].get(t)}
            assert not moved, f"the tables that differ: {sorted(moved)}"
            # `send` stages a call and never commits. One right call of each
            # op goes through a whole session on this build, so the doors of
            # the commit path meet it too.
            first: dict[str, scenes.Call] = {}
            for call in scenes.sweep():
                if call.scene == name:
                    first.setdefault(call.op, call)
            for call in first.values():
                scenes.land(again, call)
        finally:
            again.close()

    out = {"scene": scene}
    if "calls" in parts:
        out.update({
            "test_a_known_wrong_call_is_refused_by_its_door":
                test_a_known_wrong_call_is_refused_by_its_door,
            "test_a_right_call_lands": test_a_right_call_lands,
            "test_the_calls_leave_the_scene_as_it_was_built":
                test_the_calls_leave_the_scene_as_it_was_built})
    if "again" in parts:
        out["test_a_second_build_gives_equal_rows_and_lands_a_right_call_per_op"] = \
            test_a_second_build_gives_equal_rows_and_lands_a_right_call_per_op
    return out
