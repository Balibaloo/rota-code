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

# The columns that two builds may give differently: the hashes of a prompt
# that holds pytest's run time (`scenes.FREE`). Under pytest the conftest
# pins git's clock, so the commit shas repeat.
FREE = scenes.FREE


def _param(call):
    marks = [pytest.mark.xfail(strict=True, reason=f"held by {call.held}")] if call.held else []
    return pytest.param(call, id=call.name, marks=marks)


def make(name: str) -> dict:
    """The fixture and the four shared tests of the scene `name`."""

    @pytest.fixture(scope="module")
    def scene(tmp_path_factory):
        t = time.perf_counter()
        sc = scenes.BUILDERS[name](tmp_path_factory.mktemp(name))
        sc.ids["built_in"] = round(time.perf_counter() - t, 1)
        sc.ids["rows"] = scenes.rows(sc, FREE)
        yield sc
        sc.close()

    @pytest.mark.parametrize("call", [_param(c) for c in scenes.catalogue()
                                      if c.scene == name] or [pytest.param(None, marks=pytest.mark.skip(reason="no row"))])
    def test_a_known_wrong_call_is_refused_by_its_door(scene, call):
        exc = scenes.send(scene, call)
        assert exc is not None, f"{call.op} landed: {call.args}"
        site = sandbox._raise_site(exc)
        top = site.rsplit(" in ", 1)[-1] if site else ""
        assert call.door in site.split(" < ")[-1] or top == call.door, (site, str(exc))
        assert str(exc).startswith(call.words), str(exc)

    @pytest.mark.parametrize("call", [_param(c) for c in scenes.sweep()
                                      if c.scene == name] or [pytest.param(None, marks=pytest.mark.skip(reason="no row"))])
    def test_a_right_call_lands(scene, call):
        exc = scenes.send(scene, call)
        assert exc is None, f"{call.op} was refused: {exc}"

    def test_the_calls_leave_the_scene_as_it_was_built(scene):
        assert scenes.rows(scene, FREE) == scene.ids["rows"]

    def test_two_builds_give_equal_rows(scene, tmp_path):
        again = scenes.BUILDERS[name](tmp_path)
        try:
            got = scenes.rows(again, FREE)
        finally:
            again.close()
        moved = {t for t in got if got[t] != scene.ids["rows"].get(t)}
        assert not moved, f"the tables that differ: {sorted(moved)}"

    return {"scene": scene,
            "test_a_known_wrong_call_is_refused_by_its_door":
                test_a_known_wrong_call_is_refused_by_its_door,
            "test_a_right_call_lands": test_a_right_call_lands,
            "test_the_calls_leave_the_scene_as_it_was_built":
                test_the_calls_leave_the_scene_as_it_was_built,
            "test_two_builds_give_equal_rows": test_two_builds_give_equal_rows}
