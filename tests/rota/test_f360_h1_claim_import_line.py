"""
Frame 360, H1 pass 2c: the claim wake names the import line, and the door
of `code.run` quotes the right line when the import is close to the touch.

The register case `L1-AR-run-the-code-at-a-claim` recorded 0 of 5 on
qwen3:8b. Each of the 5 programs imported `src.icalendar.parser.string`,
and 3 of the 5 named `foldline` for `_foldline`. The wake named the touch
as a path, and the seat turned the path into a module. The Tester's door
names the line itself for the same cause (frame 260).
"""
from __future__ import annotations

from tests.rota.test_f360_h1_claim_run import (  # noqa: F401
    SOURCE, STRING_PY, _architect, _claim_wakes, _git, _refusal, project,
    rows)

LINE = "from icalendar.parser.string import _foldline"


def test_the_detail_names_the_import_line_of_the_touch(rows):
    detail = _claim_wakes(rows)[0].detail

    assert (f"Import the function of the touch with this line, copied "
            f"exactly: `{LINE}`.") in detail, detail
    assert "src.icalendar" not in detail, detail
    assert "Import the function of the touch from its module" not in detail


def test_a_path_only_touch_keeps_the_present_sentence(rows):
    rows.execute("DELETE FROM code_index")
    rows.commit()

    detail = _claim_wakes(rows)[0].detail

    assert "copied exactly" not in detail, detail
    assert "import _foldline" not in detail, detail
    assert ("Import the function of the touch from its module, call it with "
            "one example from the request") in detail, detail


def test_the_src_prefix_is_refused_with_the_right_line(project):
    """Runs 1 and 5 of the recording, to the import line."""
    db, _ = project
    text = ("from src.icalendar.parser.string import _foldline\n"
            "print(_foldline('a b', limit=75))\n")

    said = _refusal(_architect(db), text)

    assert said == ("The program imports `src.icalendar.parser.string`, and "
                    "the project imports as `icalendar.parser.string`. Use "
                    f"this line: `{LINE}`."), said


def test_a_close_name_is_refused_with_the_right_line(project):
    """Runs 2 to 4 of the recording named `foldline`. The fork defines
    `foldline` as an alias, so this touch drops the alias."""
    db, root = project
    (root / SOURCE).write_bytes(
        STRING_PY.replace("\n\nfoldline = _foldline\n", "\n").encode("utf-8"))
    _git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qam",
         "no alias")
    head = _git(root, "rev-parse", "HEAD").strip()
    db.execute("UPDATE batches SET head_commit = ?, claimed_head = ?",
               (head, head))
    db.commit()
    text = ("from icalendar.parser.string import foldline\n"
            "print(foldline('a b', limit=75))\n")

    said = _refusal(_architect(db), text)

    assert said == ("The program imports `foldline`, and the touch defines "
                    f"`_foldline`. Use this line: `{LINE}`."), said


def test_the_present_refusals_hold_on_an_unrelated_import_and_a_bare_text(
        project):
    db, _ = project

    assert _refusal(_architect(db), "import textwrap\nprint(textwrap.fill('a'))\n") == (
        "The program imports nothing from the touch, so send a program that "
        "imports a name from icalendar.parser.string and calls it.")
    assert _refusal(_architect(db), "text").startswith(
        "The door got `text`, which is not a program")


def test_the_right_import_still_runs(project):
    db, _ = project

    out = _architect(db).call("code.run", text=f"{LINE}\nprint(_foldline('a b'))\n")

    assert out["returncode"] == 0, out
