"""The survey bindings door: a constraint from an area survey binds a grain."""
import pytest

from rota.core.db import init_db
from rota.core.sandbox import build


def test_a_survey_constraint_binds_a_grain_of_its_area(tmp_path):
    """The survey spike (2026-09-15): ten qwen3:8b sessions, two wordings, and
    every constraint global with no binding. The tool says it now."""
    conn = init_db(tmp_path / "r.db")
    sb = build("architect", conn, area="src/store")
    sb.ctx.opened.add("src/store/connection.py")
    with pytest.raises(ValueError, match="binds the grain"):
        sb.call("model.amend", headline="src/store/connection.py::connect",
                text="WHO BREAKS: every record read goes through connect; WHAT HAPPENS: ImportError")
    out = sb.call("model.amend", headline="src/store/connection.py::connect",
                  text="WHO BREAKS: every record read goes through connect; WHAT HAPPENS: ImportError",
                  bindings=["src/store/connection.py::connect"])
    assert out


def test_a_constraint_outside_a_survey_may_be_global(tmp_path):
    conn = init_db(tmp_path / "r.db")
    sb = build("architect", conn)
    out = sb.call("model.amend", headline="the package name on the index",
                  text="WHO BREAKS: every installer of the package; WHAT HAPPENS: no such package")
    assert out
