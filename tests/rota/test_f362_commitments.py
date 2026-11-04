"""
Frame 362, slice pass 2: the stated commitment and the Architect's push.

The harvest of pass 1 writes commitment candidates, and nothing read them.
This pass gives `constraints` three columns, `party`, `behaviour` and
`witness`, that only the Architect writes through `model.amend`. The
Architect's survey wake gets the candidates bound to its area pushed as
`[model.witnesses]`, capped. The design is
`plans/design-onboarding-2026-11-03.md`, section 4.2, steps 1 and 2, and
the record is section 7 of the deep dive of the same date.
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pytest

from rota.core.db import Write, _apply_write, init_db
from rota.core.runner import build_prompt, push_working_set, session_sandbox
from rota.core.scheduler import Wake
from rota.onboarding import harvest
from rota.roles import api

FOLD = '''"""Lines as RFC 5545 folds them."""


def fold(line, limit=75):
    """Fold the line.

    A line holds at most 75 octets.
    """
    return line
'''
THING = '''def keep(x):
    # See issue #1501: the escape stays whole.
    return x
'''
ROW = re.compile(r"^- (cc_[0-9a-f]{12}) ", re.M)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


@pytest.fixture
def tree(tmp_path):
    """Two areas: `src/pkg` with an export and a numeric default, and
    `src/other` with an issue comment. The harvest runs at commit `c1`."""
    root = tmp_path / "proj"
    _write(root / "src/pkg/__init__.py", '__all__ = ["fold"]\n')
    _write(root / "src/pkg/fold.py", FOLD)
    _write(root / "src/other/thing.py", THING)
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)",
               (str(root),))
    for grain, kind, area in (("src/pkg/__init__.py", "path", "src/pkg"),
                              ("src/pkg/fold.py", "path", "src/pkg"),
                              ("src/pkg/fold.py::fold", "symbol", "src/pkg"),
                              ("src/other/thing.py", "path", "src/other")):
        db.execute("INSERT INTO code_index (grain, grain_kind, area) "
                   "VALUES (?, ?, ?)", (grain, kind, area))
    db.execute("INSERT INTO constraints (id, headline, text) VALUES "
               "('older', 'an older row', 'Programs outside read it.')")
    assert harvest.record(db, root, "c1") == 3
    db.commit()
    yield root, db
    db.close()


def _id(db, kind):
    return db.execute("SELECT id FROM commitment_candidates WHERE kind = ? "
                      "ORDER BY rowid DESC", (kind,)).fetchone()["id"]


def _survey(db, area="src/pkg"):
    wake = Wake("architect", "tick:survey", refs=(area,))
    sb = session_sandbox(db, wake)
    return wake, sb


def _land(db, sb):
    """Apply the session's staged writes, as the pipeline does at commit."""
    for table, row_id, values in sb.ctx.writes:
        _apply_write(db, Write(table, row_id, values), "architect")
    db.commit()


def _state(db, witness, party="other calendar programs"):
    wake, sb = _survey(db)
    out = sb.call("model.amend", headline="src/pkg/fold.py::fold",
                  text="Other calendar programs read the folded lines.",
                  party=party, behaviour="lines fold at 75 octets",
                  witness=witness)
    return sb, out


# ---------------------------------------------------------------------------
# The columns
# ---------------------------------------------------------------------------

def test_the_columns_exist_and_the_harvest_leaves_them_empty(tree):
    root, db = tree
    cols = {r["name"] for r in db.execute("PRAGMA table_info(constraints)")}
    assert {"party", "behaviour", "witness"} <= cols
    row = db.execute("SELECT party, behaviour, witness FROM constraints "
                     "WHERE id = 'older'").fetchone()
    assert tuple(row) == ("", "", "")
    # A second harvest of a new commit writes no constraint column.
    db.execute("UPDATE constraints SET party = 'p', behaviour = 'b', "
               "witness = 'wk_x' WHERE id = 'older'")
    db.commit()
    _write(root / "src/other/thing.py", THING + "# See issue #1600.\n")
    harvest.record(db, root, "c2")
    db.commit()
    row = db.execute("SELECT party, behaviour, witness FROM constraints "
                     "WHERE id = 'older'").fetchone()
    assert tuple(row) == ("p", "b", "wk_x")
    # Law 1: the harvester's source holds no write to `constraints`.
    src = Path(harvest.__file__).read_text(encoding="utf-8")
    assert not re.search(r"(INSERT\s+(OR\s+\w+\s+)?INTO|UPDATE)\s+constraints\b",
                         src, re.I)


def test_an_older_database_gets_the_columns(tmp_path):
    """A run database from before the pass holds the old `constraints`."""
    old = sqlite3.connect(tmp_path / "old.db")
    old.execute("CREATE TABLE constraints (id TEXT PRIMARY KEY, headline TEXT "
                "NOT NULL, text TEXT, rationale_decision TEXT, is_global INTEGER "
                "NOT NULL DEFAULT 0, version INTEGER NOT NULL DEFAULT 1)")
    old.execute("INSERT INTO constraints (id, headline) VALUES ('k', 'h')")
    old.commit()
    old.close()
    db = init_db(tmp_path / "old.db")
    assert tuple(db.execute("SELECT party, behaviour, witness FROM constraints"
                            ).fetchone()) == ("", "", "")
    cols = {r["name"] for r in db.execute("PRAGMA table_info(constraints)")}
    db.close()
    assert {"party", "behaviour", "witness"} <= cols


# ---------------------------------------------------------------------------
# The push
# ---------------------------------------------------------------------------

def test_the_survey_push_carries_the_area_candidates_and_no_others(tree):
    _, db = tree
    wake, sb = _survey(db)
    pushed = push_working_set("architect", sb, wake)
    text = pushed["model.witnesses"]
    assert set(ROW.findall(text)) == {_id(db, "export"), _id(db, "numeric_default")}
    assert _id(db, "issue_comment") not in text
    # The own file goes before the exports rule.
    assert ROW.findall(text)[0] == _id(db, "numeric_default")
    _, user = build_prompt("architect", sb, wake, pushed, instructions="")
    assert "[model.witnesses]" in user
    assert '"A line holds at most 75 octets."' in user


def test_an_area_with_no_candidate_gets_no_block(tree):
    _, db = tree
    db.execute("INSERT INTO code_index (grain, grain_kind, area) "
               "VALUES ('src/empty/e.py', 'path', 'src/empty')")
    db.commit()
    wake, sb = _survey(db, "src/empty")
    pushed = push_working_set("architect", sb, wake)
    assert "model.witnesses" not in pushed


def test_the_push_cap_cuts_and_says_so(tree):
    """60 long project-wide rows and 10 own-file rows on one area. The cut
    keeps every own-file row and counts the rest in one line."""
    _, db = tree
    for i in range(70):
        rule = "witness_file" if i < 10 else "project_wide"
        cid = f"cc_{i:012x}"
        db.execute("INSERT INTO commitment_candidates (id, kind, path, line, text) "
                   "VALUES (?, 'doc_claim', 'docs/x.rst', ?, ?)",
                   (cid, i + 1, f"Line {i} supports RFC 5545 " + "x" * 150))
        db.execute("INSERT INTO candidate_bindings (witness_id, path, rule) "
                   "VALUES (?, 'src/pkg/fold.py', ?)", (cid, rule))
    db.commit()
    kept, text = api.witness_push(db, "src/pkg")
    assert len(text) <= api.WITNESS_PUSH_CHARS
    total = len(api.area_witnesses(db, "src/pkg"))
    cut = total - len(kept)
    assert cut > 0
    assert text.splitlines()[-1] == (
        f"{cut} more candidates were cut to fit this push. The cut takes the "
        f"project-wide candidates first.")
    rules = [w["rule"] for w in kept]
    # Ten rows and the harvest's own row keep the own-file rule, and the
    # export goes before any project-wide row.
    assert rules.count("witness_file") == 11
    assert "exports" in rules
    assert rules == sorted(rules, key=api.WITNESS_RANK.index)


def test_a_contradicting_witness_is_quoted_beside_it(tree):
    _, db = tree
    nd = _id(db, "numeric_default")
    db.execute("INSERT INTO commitment_candidates (id, kind, path, line, text, "
               "contradicts) VALUES ('cc_00000000beef', 'doc_claim', "
               "'docs/api.rst', 61, 'Lines fold at 75 characters.', ?)",
               (f'["{nd}"]',))
    db.execute("UPDATE commitment_candidates SET contradicts = "
               "'[\"cc_00000000beef\"]' WHERE id = ?", (nd,))
    db.commit()
    _, text = api.witness_push(db, "src/pkg")
    assert ('It contradicts cc_00000000beef, docs/api.rst line 61: '
            '"Lines fold at 75 characters."') in text


# ---------------------------------------------------------------------------
# The door
# ---------------------------------------------------------------------------

def test_the_door_refuses_a_statement_without_a_witness(tree):
    _, db = tree
    _, sb = _survey(db)
    with pytest.raises(ValueError) as got:
        sb.call("model.amend", headline="src/pkg/fold.py::fold",
                text="Other calendar programs read the folded lines.",
                party="other calendar programs",
                behaviour="lines fold at 75 octets")
    msg = str(got.value)
    assert "names none" in msg
    # The refusal shows the correct form with an id the push showed.
    assert f'witness="{_id(db, "numeric_default")}"' in msg
    assert 'party="<who outside notices>"' in msg


def test_the_door_refuses_a_witness_the_push_did_not_show(tree):
    _, db = tree
    with pytest.raises(ValueError) as got:
        _state(db, _id(db, "issue_comment"))
    assert "is not a candidate that [model.witnesses] showed" in str(got.value)
    with pytest.raises(ValueError) as got:
        _state(db, "cc_000000000000")
    assert "model.amend(headline=" in str(got.value)


def test_the_door_refuses_a_statement_with_no_party(tree):
    _, db = tree
    with pytest.raises(ValueError) as got:
        _state(db, _id(db, "numeric_default"), party="")
    assert "leaves one out" in str(got.value)


def test_the_door_accepts_the_three_columns(tree):
    _, db = tree
    nd = _id(db, "numeric_default")
    sb, out = _state(db, nd)
    assert out["witness"] == nd
    # The candidate's placed binding stands in for the seat's.
    assert out["bindings"] == ["src/pkg/fold.py"]
    _land(db, sb)
    row = db.execute("SELECT party, behaviour, witness, is_global FROM constraints "
                     "WHERE id = ?", (out["id"],)).fetchone()
    assert row["party"] == "other calendar programs"
    assert row["behaviour"] == "lines fold at 75 octets"
    assert row["witness"] == harvest.witness_key(
        "numeric_default", "src/pkg/fold.py", "    A line holds at most 75 octets.")
    assert row["is_global"] == 0
    # The witness path is a grain ref, so the row is observed.
    assert db.execute("SELECT 1 FROM refs WHERE src_table = 'constraints' AND "
                      "src_id = ? AND kind = 'grain' AND target = 'src/pkg/fold.py'",
                      (out["id"],)).fetchone()
    prov = db.execute("SELECT provenance FROM constraint_provenance WHERE id = ?",
                      (out["id"],)).fetchone()["provenance"]
    assert prov == "observed"


def test_an_amend_without_a_statement_writes_no_party(tree):
    _, db = tree
    sb, out = _state(db, _id(db, "numeric_default"))
    _land(db, sb)
    _, sb2 = _survey(db)
    sb2.ctx.opened = {"src/pkg/fold.py"}
    sb2.call("model.amend", headline="src/pkg/fold.py::fold",
             text="Other calendar programs read the folded lines.",
             bindings=["src/pkg/fold.py"])
    values = [v for t, _, v in sb2.ctx.writes if t == "constraints"][0]
    assert not {"party", "behaviour", "witness"} & set(values)


# ---------------------------------------------------------------------------
# The tie
# ---------------------------------------------------------------------------

def test_the_tie_survives_a_line_shift(tree):
    root, db = tree
    old = _id(db, "numeric_default")
    sb, out = _state(db, old)
    _land(db, sb)
    # Three lines above the witness move it from line 7 to line 10.
    _write(root / "src/pkg/fold.py", FOLD.replace(
        '"""Lines as RFC 5545 folds them."""',
        '"""Lines as RFC 5545 folds them."""\nimport os\nimport re\nimport sys'))
    harvest.record(db, root, "c2")
    db.commit()
    new = _id(db, "numeric_default")
    assert new != old
    key = db.execute("SELECT witness FROM constraints WHERE id = ?",
                     (out["id"],)).fetchone()["witness"]
    got = harvest.witnessed(db, key)
    assert got["id"] == new and got["line"] == 10
    rows = {w["id"]: w for w in api.area_witnesses(db, "src/pkg")}
    assert rows[new]["stated"] == out["id"]


def test_an_edit_of_the_witness_line_breaks_the_tie(tree):
    root, db = tree
    sb, out = _state(db, _id(db, "numeric_default"))
    _land(db, sb)
    _write(root / "src/pkg/fold.py", FOLD.replace("at most 75 octets",
                                                  "at most 75 octets, always"))
    harvest.record(db, root, "c2")
    db.commit()
    rows = {w["id"]: w for w in api.area_witnesses(db, "src/pkg")}
    assert rows[_id(db, "numeric_default")]["stated"] == ""


# ---------------------------------------------------------------------------
# The challenge verdict
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("verdict, shown", [("falsified", False), ("stands", True)])
def test_a_falsified_statement_takes_its_candidate_out_of_the_push(tree, verdict,
                                                                   shown):
    """No challenge verdict exists for a candidate. The verdict is on the
    stated constraint, `constraints:<id>`, so the test is on that row."""
    _, db = tree
    nd = _id(db, "numeric_default")
    sb, out = _state(db, nd)
    _land(db, sb)
    db.execute("INSERT INTO challenges (id, verdict, citation, quote) "
               "VALUES (?, ?, 'src/pkg/fold.py', 'limit=75')",
               (f"constraints:{out['id']}", verdict))
    db.commit()
    _, text = api.witness_push(db, "src/pkg")
    assert (nd in ROW.findall(text)) is shown
    if shown:
        assert f"Constraint {out['id']} states it already." in text
