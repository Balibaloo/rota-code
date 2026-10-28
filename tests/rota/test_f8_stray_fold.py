"""
F8, an unexpected change is a stray for the Architect: the producer of a
stray folds a path with `_grain_path`, as the judge does
(plans/rootfix-audit-2026-10-27-a.md, F8).

`divergence._norm` used `lstrip("./")`, a character set. It turned
`.github/ci.py` into `github/ci.py`, so a prediction of one file covered
another, and the stray row and the judge keyed one path two ways.
"""
from __future__ import annotations

import re
from pathlib import Path

from rota.core.divergence import stray_paths, under

PACKAGE = Path(__file__).resolve().parents[2] / "rota"


def test_a_dot_directory_is_not_its_undotted_twin():
    assert stray_paths(["github/ci.py"], [".github/ci.py"]) == ["github/ci.py"]
    assert stray_paths([".github/ci.py"], ["github"]) == [".github/ci.py"]
    assert stray_paths([".github/ci.py"], [".github/"]) == []


def test_the_stray_is_keyed_as_the_judge_keys_it():
    # The judge reads `touch_strays.path` through `_grain_path`.
    assert stray_paths(["./src\\new.py"], ["src/old.py"]) == ["src/new.py"]
    assert under("./src/a.py", "src") and not under(".src/a.py", "src")


def test_no_path_fold_by_a_character_set_in_divergence():
    src = (PACKAGE / "core" / "divergence.py").read_text(encoding="utf-8")
    assert not re.search(r"lstrip\(\s*[\"']\./[\"']\s*\)", src)
    assert "def _norm" not in src
