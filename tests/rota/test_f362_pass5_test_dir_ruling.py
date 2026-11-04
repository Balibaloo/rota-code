"""
Frame 362, pass 5: the frame's ruling on a folder stops at a test directory
inside the folder.

Dry run 5 on icalendar merged nothing (plans/f362-dry5-walls-read.md,
section 3). The judge ruled the top-level entry `src` as `program`, and it
never saw `src/icalendar/tests`. `ruling_for` let `src` cover the test
files, so `_is_test_file` said False for all 162 of them. The harness
inherited one test, and the two tests that pin issue 1501 never ran.

Frame 324 (ruled: Roman, 2026-10-26 20:37): "the basename gives the shape
of a test file, and the frame's kind says whether the file is part of the
program". Both halves hold. A test-shaped file with no test directory, such
as `src/pkg/test_helpers.py`, stays in the program. A `decided` ruling on
the test directory itself still wins.
"""
from __future__ import annotations

from rota.core.db import init_db
from rota.onboarding.areas import kind_of
from rota.roles import api
from rota.testkit.fixtures import seed_provenance

TEST_FILE = "src/icalendar/tests/test_parsing.py"


def _conn(tmp_path, *rulings):
    """Rulings as `dry5.db` holds them: (prefix, kind, provenance)."""
    conn = init_db(tmp_path / "rota.db")
    for prefix, kind, provenance in rulings:
        conn.execute("INSERT INTO frame_rulings (id, kind) VALUES (?, ?)",
                     (prefix, kind))
        seed_provenance(conn, "frame_rulings", prefix, provenance)
    conn.commit()
    return conn


def _dry5(tmp_path, *more):
    return _conn(tmp_path, ("src", "program", "observed"),
                 (".github", "attached", "observed"),
                 ("docs", "attached", "observed"), *more)


def test_a_program_folder_ruling_stops_at_its_test_directory(tmp_path):
    conn = _dry5(tmp_path)
    assert kind_of(conn, TEST_FILE) == "attached"
    assert kind_of(conn, "src/icalendar/parser/string.py") == "program"
    assert kind_of(conn, "src/icalendar/tests/calendars/example.ics") == "attached"


def test_a_decided_ruling_on_the_test_directory_wins(tmp_path):
    conn = _dry5(tmp_path, ("src/icalendar/tests", "program", "decided"))
    assert kind_of(conn, TEST_FILE) == "program"


def test_a_root_tests_ruling_is_unchanged(tmp_path):
    conn = _conn(tmp_path, ("tests", "attached", "observed"))
    assert kind_of(conn, "tests/test_a.py") == "attached"


def test_a_test_shaped_file_with_no_test_directory_stays_program(tmp_path):
    # The frame 324 case: a test-shaped basename inside the program.
    conn = _conn(tmp_path, ("src", "program", "observed"))
    assert kind_of(conn, "src/pkg/test_helpers.py") == "program"
    assert not api._is_test_file(conn, "src/pkg/test_helpers.py")


def test_an_ignored_folder_keeps_its_test_directory(tmp_path):
    # Deviation from the brief: a vendored folder that the frame ignores
    # does not give its tests to the harness.
    conn = _conn(tmp_path, ("vendor", "ignore", "observed"))
    assert kind_of(conn, "vendor/lib/tests/test_x.py") == "ignore"


def test_the_doors_see_the_icalendar_test_files(tmp_path):
    conn = _dry5(tmp_path)
    assert api._is_test_file(conn, TEST_FILE)
    indexed = {TEST_FILE, "src/icalendar/tests/prop/test_vtext.py",
               "src/icalendar/tests/attr/test_attr.py",
               "src/icalendar/parser/string.py",
               ".github/workflows/test_generate_matrix.py"}
    assert api._test_dirs(indexed, conn) == {
        "src/icalendar/tests", "src/icalendar/tests/prop",
        "src/icalendar/tests/attr", ".github/workflows"}
