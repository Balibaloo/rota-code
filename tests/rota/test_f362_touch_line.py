"""
Frame 362, slice pass 4: the touch line gains the commitment part.

The design is `plans/design-onboarding-2026-11-03.md`, section 4.2, step 5.
The touch line to the principal names each stated commitment that binds a
touched path, in one sentence: "It must keep: <behaviour>, because
<party> depend on it." The sentences are the set that the Critic's push
carries for the batch, in the push's order. No other part of the page
carries a commitment row (section 3.5).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from rota.core.db import init_db
from rota.core.runner import BOUND_KEY, push_working_set, session_sandbox
from rota.core.scheduler import Wake
from rota.onboarding import harvest
from rota.onboarding.boot import refresh_constraint_zero
from rota.roles.principal import render_page, touch_words

FOLD = '''"""Lines as RFC 5545 folds them."""


def fold(line, limit=75):
    """Fold the line.

    A line holds at most 75 octets.
    """
    return line
'''
DOC = ("Folding\n=======\n\n"
       "A content line holds at most 75 characters, as RFC 5545 says.\n")
THING = "def keep(x):\n    return x\n"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


@pytest.fixture
def db(tmp_path):
    """Batch `b1` of item `it` touches `src/pkg/fold.py`. The harvest runs
    at commit `c1`, and both areas have a survey record."""
    root = tmp_path / "proj"
    _write(root / "src/pkg/fold.py", FOLD)
    _write(root / "src/other/thing.py", THING)
    _write(root / "docs/fold.rst", DOC)
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)",
                 (str(root),))
    for grain, kind, area in (("src/pkg/fold.py", "path", "src/pkg"),
                              ("src/pkg/fold.py::fold", "symbol", "src/pkg"),
                              ("src/other/thing.py", "path", "src/other")):
        conn.execute("INSERT INTO code_index (grain, grain_kind, area) "
                     "VALUES (?, ?, ?)", (grain, kind, area))
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('it', 'fold at a space', 'in_scope', "
                 "'approved', 1, 1)")
    conn.execute("INSERT INTO batches (id, item_id, status) "
                 "VALUES ('b1', 'it', 'running')")
    conn.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind, "
                 "confidence) VALUES ('b1', 'src/pkg/fold.py', 'path', "
                 "'expected')")
    harvest.record(conn, root, "c1")
    for area in ("src/pkg", "src/other"):
        conn.execute("INSERT INTO survey_records (id, area, outcome) "
                     "VALUES (?, ?, 'none_found')", (f"sv_{area}", area))
    refresh_constraint_zero(conn)
    conn.commit()
    yield conn
    conn.close()


def _state(conn, cid, party, behaviour, kind="numeric_default",
           path="src/pkg/fold.py", grain="src/pkg/fold.py"):
    """A stated commitment, as `model.amend` lands one, bound to `grain`."""
    c = dict(conn.execute(
        "SELECT * FROM commitment_candidates WHERE kind = ? AND path = ?",
        (kind, path)).fetchone())
    conn.execute(
        "INSERT INTO constraints (id, headline, text, is_global, party, "
        "behaviour, witness) VALUES (?, ?, ?, 0, ?, ?, ?)",
        (cid, f"{path}: {behaviour}", "Outside readers break.", party,
         behaviour, harvest.witness_key(c["kind"], c["path"], c["text"])))
    conn.execute("INSERT INTO constraint_bindings (constraint_id, grain, "
                 "grain_kind, resolves) VALUES (?, ?, 'path', 1)", (cid, grain))
    conn.commit()


def _critic_ids(conn) -> list[str]:
    """The stated commitments of the Critic's push, in its order."""
    wake = Wake("critic", "tick:review", refs=("b1",))
    pushed = push_working_set("critic", session_sandbox(conn, wake, batch_id="b1"),
                              wake)
    return [r["id"] for r in pushed.get(BOUND_KEY) or () if "party" in r]


def _touch_line(conn) -> str:
    """The touch line as the principal reads it on the touch note."""
    page, _ = render_page(conn, "present", ["b1", "it"], returned=False)
    lines = [ln for ln in page.splitlines() if "expected to touch" in ln]
    assert len(lines) == 1, page
    return lines[0]


def test_one_bound_commitment_adds_one_sentence(db):
    _state(db, "fold_octets", "other calendar programs",
           "a folded line holds at most 75 octets")
    line = _touch_line(db)
    print(line)
    assert line.endswith("expected to touch src/pkg/fold.py. It must keep: a "
                         "folded line holds at most 75 octets, because other "
                         "calendar programs depend on it.")
    assert _critic_ids(db) == ["fold_octets"]
    # The sentence is the one part that carries the row (design 3.5).
    assert "commitments:" not in line
    assert line.count("75 octets") == 1


def test_no_bound_commitment_adds_no_words(db):
    # A stated commitment on another path binds nothing of this batch.
    _state(db, "keep_whole", "importers of the package", "keep returns x",
           grain="src/other/thing.py")
    line = _touch_line(db)
    print(line)
    assert _critic_ids(db) == []
    assert "must keep" not in line
    assert line.endswith("expected to touch src/pkg/fold.py")
    assert touch_words(db, "b1") == ("the work for: fold at a space; expected "
                                     "to touch src/pkg/fold.py")


def test_two_bound_commitments_follow_the_critics_order(db):
    # Stated in the reverse of the push's order, so the line cannot take
    # the order of the writes.
    _state(db, "z_fold_octets", "other calendar programs",
           "a folded line holds at most 75 octets.")
    _state(db, "a_doc_claim", "readers of the docs",
           "the docs and the fold name one limit", kind="doc_claim",
           path="docs/fold.rst")
    line = _touch_line(db)
    print(line)
    assert _critic_ids(db) == ["a_doc_claim", "z_fold_octets"]
    first = ("It must keep: the docs and the fold name one limit, because "
             "readers of the docs depend on it.")
    second = ("It must keep: a folded line holds at most 75 octets, because "
              "other calendar programs depend on it.")
    assert line.endswith(f"src/pkg/fold.py. {first} {second}")
