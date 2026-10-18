"""The rulings search over a small tree of records: the match rule, the
order of print, the cap and the four named forms."""
from __future__ import annotations

from pathlib import Path

import pytest

from rota.tools import rulings

LAWS = """# The laws

### 1. Single writer — one writer per row

Every row has one
writer.

### 2. Conclusions travel; reasoning stays home

A message carries the conclusion.
Line two.
Line three.
Line four.
Line five.
Line six is past the head.

### 12. Constraints protect external commitments only

The touch route is law 12's door.
"""

ARCHIVE = """# Stack, closed

### 41. The relay keeps declined files (2026-10-01)

- **Site: `batches.annotate` in `rota/roles/api.py`.** Rota workflow.
- The principal said the pager tests
  have nothing to do with this. Law 2 holds.

### 42. A second frame (2026-10-02)

- **Site: the cockpit.** Names frame 41 and law 21.
"""

LEDGER = """# Rulings

### R1. The notes answer goes to the principal

- Keys: notes answer, principal page
- Body: he wants pager tests out.
"""


@pytest.fixture
def tree(tmp_path: Path, monkeypatch) -> Path:
    monkeypatch.delenv(rulings.SKIP_ENV, raising=False)
    (tmp_path / "rota").mkdir()
    (tmp_path / "rota" / "LAWS.md").write_bytes(LAWS.encode("utf-8"))
    (tmp_path / "plans" / "archive").mkdir(parents=True)
    (tmp_path / "plans" / "archive" / "stack-2026-10-02.md").write_bytes(
        ARCHIVE.encode("utf-8"))
    (tmp_path / "plans" / "rulings.md").write_bytes(LEDGER.encode("utf-8"))
    return tmp_path


def run(tree: Path, capsys, *argv: str) -> list[str]:
    assert rulings.main(list(argv), root=tree) == 0
    return capsys.readouterr().out.splitlines()


def test_a_phrase_across_a_line_break_matches(tree, capsys):
    out = run(tree, capsys, "pager tests have nothing")
    assert any("plans/archive/stack-2026-10-02.md:3" in line for line in out)


def test_case_folds(tree, capsys):
    out = run(tree, capsys, "SINGLE", "WRITER")
    assert out == ["1. Single writer — one writer per row rota/LAWS.md:3"]


def test_every_word_matches_inside_one_unit(tree, capsys):
    # "writer" sits in law 1 and "conclusion" in law 2, so no unit holds both.
    out = run(tree, capsys, "writer", "conclusion")
    assert out[0].startswith("nothing matched writer conclusion")


def test_keys_print_before_body_hits(tree, capsys):
    out = run(tree, capsys, "principal")
    assert out[0] == "KEY R1. The notes answer goes to the principal plans/rulings.md:3"
    assert any(line.startswith("41.") for line in out[1:])
    assert not any(line.startswith("R1.") for line in out)


def test_the_skip_variable_leaves_the_ledger_out(tree, capsys, monkeypatch):
    monkeypatch.setenv(rulings.SKIP_ENV, "1")
    out = run(tree, capsys, "principal")
    assert not any("rulings.md" in line for line in out)


def test_the_zero_hit_line(tree, capsys):
    out = run(tree, capsys, "zebra")
    assert out == ["nothing matched zebra; read rota/LAWS.md and "
                   "plans/composition.md whole"]


def test_ten_body_hits_per_source_and_the_cap(tree, capsys, monkeypatch):
    many = "".join(f"### {n}. Frame about apples {'x' * 150}\n\napples\n\n"
                   for n in range(100, 200))
    (tree / "plans" / "archive" / "stack-2026-10-03.md").write_bytes(
        many.encode("utf-8"))
    out = run(tree, capsys, "apples")
    assert len(out) == 11
    assert out[-1] == "... 90 more in plans/archive"
    assert all(len(line) < 200 for line in out)
    monkeypatch.setattr(rulings, "CAP_CHARS", 500)
    out = run(tree, capsys, "apples")
    assert out[-2] == "cap of 500 characters reached; hits per source:"
    assert out[-1] == "  plans/archive 100"


def test_the_law_form(tree, capsys):
    out = run(tree, capsys, "law", "2")
    assert out[0] == "LAW 2. Conclusions travel; reasoning stays home rota/LAWS.md:8"
    assert out[1:6] == ["  A message carries the conclusion.", "  Line two.",
                        "  Line three.", "  Line four.", "  Line five."]
    # Frame 41 names law 2. Frame 42 names law 21, which is not law 2.
    assert any(line.startswith("41.") for line in out[6:])
    assert not any(line.startswith("42.") for line in out[6:])


def test_the_frame_form(tree, capsys):
    (tree / "plans" / "stack.md").write_bytes(b"# Stack\n")
    out = run(tree, capsys, "frame", "41")
    assert out[0].startswith("FRAME 41. The relay keeps declined files")
    assert out[1].startswith("  - **Site: `batches.annotate`")
    assert any(line.startswith("42.") for line in out[2:])


def test_the_file_and_door_forms(tree, capsys):
    out = run(tree, capsys, "file", "rota/roles/api.py")
    assert out == ["41. The relay keeps declined files (2026-10-01) "
                   "plans/archive/stack-2026-10-02.md:3"]
    out = run(tree, capsys, "door", "batches.annotate")
    assert out[0].startswith("41.")


def test_wide_adds_the_plans_files_claude_md_and_composition(tree, capsys):
    (tree / "plans" / "frame9-design.md").write_bytes(b"# Design\n\nquokka\n")
    (tree / "plans" / "night9-read.md").write_bytes(b"# Read\n\nquokka\n")
    (tree / "plans" / "composition.md").write_bytes(b"# Composition\n\nquokka\n")
    (tree / "CLAUDE.md").write_bytes(b"# The assistant\n\nquokka\n")
    assert run(tree, capsys, "quokka") == ["Read plans/night9-read.md:1"]
    out = run(tree, capsys, "--wide", "quokka")
    assert out == ["Read plans/night9-read.md:1",
                   "Composition plans/composition.md:1",
                   "The assistant CLAUDE.md:1",
                   "Design plans/frame9-design.md:1"]


def test_no_query_prints_the_usage(tree, capsys):
    assert rulings.main([], root=tree) == 2
    assert capsys.readouterr().out.startswith("usage:")
