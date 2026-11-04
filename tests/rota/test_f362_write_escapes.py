"""Frame 362, dry run 5, wall 10: the write one escape level too deep.

s216 retyped `src/icalendar/parser/string.py` whole, with two backslashes
for each backslash of the source. The file parsed, and no door compared the
escape level of the write with the file. The fixtures are the file at
99619246 and at 670629b3, the commit that the write made.
"""
from __future__ import annotations

import pathlib
import subprocess

import pytest

from rota.core.sandbox import build
from rota.roles import api, prompts
from tests.rota.test_frame283_removal_on_ruling import _git, db  # noqa: F401

DATA = pathlib.Path(__file__).resolve().parent / "fixtures" / "dry5_string"
PATH = "src/icalendar/parser/string.py"
BASE = (DATA / "string_99619246.py.txt").read_text(encoding="utf-8")
WROTE = (DATA / "string_670629b3.py.txt").read_text(encoding="utf-8")


def _developer(db, tmp_path):
    root = tmp_path / "wt"
    (root / PATH).parent.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / PATH).write_text(BASE, encoding="utf-8", newline="")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "99619246")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'bg_3'", (str(root),))
    db.commit()
    sb = build("developer", db, batch_id="bg_3", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    return sb, root


def test_the_dry_run_write_meets_43_of_60_doubled_lines():
    added = [line for line in WROTE.splitlines()
             if line not in set(BASE.splitlines())]
    assert len(added) == 60
    assert len(api.doubled_escape_lines(BASE.splitlines(), WROTE)) == 43


def test_the_write_door_refuses_a_retype_one_escape_level_too_deep(db, tmp_path):
    """s216 seq 16: the whole-file write of 670629b3. The door refuses it,
    names the count, and offers the same write with those escapes halved."""
    sb, root = _developer(db, tmp_path)
    sb.ctx.offers = []
    with pytest.raises(ValueError) as got:
        sb.call("code.write", path=PATH, text=WROTE)
    said = str(got.value)
    assert said.startswith(f"43 of the {len(WROTE.splitlines())} lines you "
                           "wrote equal lines of " + PATH), said
    assert (root / PATH).read_text(encoding="utf-8") == BASE
    (offer,) = [o for o in sb.ctx.offers if o.op == "code.write"]
    assert api.doubled_escape_lines(BASE.splitlines(), offer.args["text"]) == []
