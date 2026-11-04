"""
Frame 362, pass 5b, section 3: the refusal's folder order and the index cut.

The review of pass 5 (plans/f362-review-pass5.md): high 2, the refusal named
`.github/workflows` first, because it sorted the test folders by depth. That
is the path of dry run 4's wall 16 and dry run 5's wall 9. Low 6: the
re-annotate push cut the index's test files at 80 in grain order, so
`test_parsing.py` was not in it, and the list did not say it was cut.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.runner import _index_test_files
from rota.roles import api
from rota.testkit.fixtures import seed_provenance

PARSING = "src/icalendar/tests/test_parsing.py"
STRING = "src/icalendar/parser/string.py"
EARLY = [f"src/icalendar/tests/test_a{i:03}.py" for i in range(100)]


@pytest.fixture
def conn(tmp_path):
    """The dry run 5 shape: `src` is program, `.github` attached, by the
    judge. 101 test files in the package's test folder, one in workflows."""
    conn = init_db(tmp_path / "rota.db")
    for prefix, kind in (("src", "program"), (".github", "attached")):
        conn.execute("INSERT INTO frame_rulings (id, kind) VALUES (?, ?)",
                     (prefix, kind))
        seed_provenance(conn, "frame_rulings", prefix, "observed")
    for g in [*EARLY, PARSING, STRING,
              ".github/workflows/test_generate_matrix.py"]:
        conn.execute("INSERT INTO code_index (grain, grain_kind) "
                     "VALUES (?, 'path')", (g,))
    conn.execute("INSERT INTO code_calls (src, dst_grain) VALUES (?, ?)",
                 (PARSING, STRING + "::_foldline"))
    conn.commit()
    return conn


def test_the_refusal_names_the_largest_test_folder_first(conn):
    with pytest.raises(ValueError) as e:
        api._refuse_program_path(conn, STRING)
    said = str(e.value)
    assert said.index("src/icalendar/tests") < said.index(".github/workflows")
    assert "src/icalendar/tests/test_string.py" in said
    assert ".github/workflows/test_string.py" not in said


def test_the_cut_list_puts_the_callers_of_the_touch_first(conn):
    files = _index_test_files(conn, touched=[STRING])
    assert files[0] == PARSING
    assert len(files) == 81
    assert files[-1] == "and 22 more test files in the index"


def test_an_uncut_list_has_no_count_row(conn):
    files = _index_test_files(conn, limit=200)
    assert len(files) == 102
    assert PARSING in files
