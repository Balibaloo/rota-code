"""
Fact F35: the predicted files of a batch, less the paths his words decline.

The audit of 2026-10-27, part b, F35, found two partial readers of the
prediction and about twelve raw reads of `batch_touch`, and none of them
dropped the paths his ruling removes. On night 170 the Tester was shown the
test paths his words declined, and the test-file door refused 12 sends
(plans/night170-read.md, W1). `lifecycle.predicted_rows` and
`lifecycle.predicted_files` are now the one reader for the doors and the
seat's working view.

P4 (ruled R16/R17, 2026-09-03): the page puts the Architect's own rows to
the principal as a sense check. So `touch_set` keeps those rows.

Each test of a moved reader is red on the parent commit 28873d55 and green
after it. The last test pins the one-reader property.
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import pytest

from rota.core.db import init_db
from rota.core.lifecycle import (needs_structural_review, predicted_files,
                                 predicted_rows, touch_set)
from rota.core.runner import push_working_set
from rota.core.sandbox import build
from rota.core.scheduler import Wake
from rota.roles import api, prompts
from rota.roles.principal import insert_ruling_rows, ruling_rows

DECLINED = "tests/test_defaults.py"


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
                 "VALUES ('i1','let confirm take a default','in_scope','approved',1,1)")
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1','i1','running')")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1','confirm default')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('c1','tk1','confirm returns the default')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    conn.executemany(
        "INSERT INTO batch_touch (batch_id, grain, grain_kind, confidence) "
        "VALUES ('b1', ?, ?, ?)",
        [("src/click/termui.py", "path", "expected"),
         ("tests/test_termui.py", "path", "expected"),
         (DECLINED, "path", "expected"),
         (f"{DECLINED}::test_basic_defaults", "symbol", "possible"),
         ("src/click/termui.py::confirm", "symbol", "possible")])
    conn.commit()
    yield conn
    conn.close()


def _decline(db, target: str = DECLINED) -> None:
    """One landed ruling on the batch whose act removes `target`."""
    words = "The defaults tests have nothing to do with confirm."
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_text, seq) VALUES ('m1','t1','principal','liaison','answer',"
               "?,1)", (words,))
    per_item = {"b1": {"verdict": "revise", "act": "remove", "target": target,
                       "words": words}}
    db.execute("INSERT INTO rulings (id, ask_id, per_item, words, status) VALUES "
               "('r1','m1',?,?,'landed')", (json.dumps({"b1": "revise"}), words))
    insert_ruling_rows(db, ruling_rows(db, "r1", None, per_item, words=words))
    db.commit()


def _sb(db, role="developer", mode="batch_start"):
    return build(role, db, batch_id="b1", mode=mode,
                 allow=prompts.mode_tools(role, mode))


def test_predicted_files_drops_the_file_his_words_decline_and_its_symbols(db):
    _decline(db)
    assert predicted_files(db, "b1") == ["src/click/termui.py", "tests/test_termui.py"]
    assert DECLINED not in {r["grain"].split("::")[0] for r in predicted_rows(db, "b1")}


def test_predicted_files_reads_the_staged_rows_and_drops_a_declined_one(db):
    _decline(db)
    staged = [("batch_touch", "b1:docs/x.md", {"batch_id": "b1", "grain": "docs/x.md",
                                               "grain_kind": "path", "confidence": "expected"}),
              ("batch_touch", f"b1:{DECLINED}", {"batch_id": "b1", "grain": DECLINED,
                                                 "grain_kind": "path", "confidence": "expected"})]
    assert predicted_files(db, "b1", staged) == [
        "src/click/termui.py", "tests/test_termui.py", "docs/x.md"]


def test_with_no_ruling_the_prediction_is_the_architects_rows(db):
    assert predicted_files(db, "b1") == [
        "src/click/termui.py", DECLINED, "tests/test_termui.py"]


def test_the_page_keeps_the_architects_own_rows(db):
    """P4: the sense check shows what the Architect predicted."""
    _decline(db)
    assert DECLINED in touch_set(db, "b1")["expected"]


def test_needs_structural_review_ignores_a_binding_on_a_declined_path(db):
    db.execute("INSERT INTO constraints (id, headline) VALUES ('k1','defaults stay')")
    db.execute("INSERT INTO constraint_bindings (constraint_id, grain, grain_kind) "
               "VALUES ('k1', ?, 'path')", (DECLINED,))
    db.commit()
    assert needs_structural_review(db, "b1") is True
    _decline(db)
    assert needs_structural_review(db, "b1") is False


def test_the_tests_missing_push_drops_the_declined_test_path(db):
    """Night 170, W1: the Tester's `touch` named the declined test file."""
    _decline(db)
    sb = _sb(db, "tester", "tests_missing")
    pushed = push_working_set("tester", sb, Wake("tester", "tick:tests_missing",
                                                 refs=("b1",)))
    assert pushed.get("touch") == ["tests/test_termui.py"]


def test_batches_expect_drops_the_declined_grains(db):
    _decline(db)
    out = _sb(db).call("batches.expect")
    assert out["expected to touch"] == ["src/click/termui.py", "tests/test_termui.py"]
    assert out["might touch"] == ["src/click/termui.py::confirm"]


def test_a_surface_in_a_declined_file_is_outside_the_batch(db):
    _decline(db)
    sb = _sb(db)
    with pytest.raises(Exception) as got:
        api._surface_outside_batch(sb.ctx, "tk1", [f"{DECLINED}::test_lookup"])
    assert "lives in tests/test_defaults.py" in str(got.value)


def test_the_surface_pick_reads_no_declined_symbol(db):
    _decline(db, "src/click/termui.py::confirm")
    sb = _sb(db)
    refs = ["src/click/termui.py::confirm", "src/click/termui.py::prompt"]
    assert api._surface_pick(sb.ctx, "b1", "c1", refs) == []


def test_the_arrange_door_reads_no_declined_grain_as_a_name(db, tmp_path, monkeypatch):
    _decline(db)
    root = tmp_path / "wt"
    (root / ".git").mkdir(parents=True)
    db.execute("UPDATE batches SET head_commit = 'c0' WHERE id = 'b1'")
    db.commit()
    monkeypatch.setattr(api, "_worktree_of", lambda ctx, bid=None: root)
    monkeypatch.setattr(api, "_encode_run", lambda *a, **k: ("fail", "said"))
    seen = {}

    class Seen(Exception):
        pass

    def fault(body, path, said, surface, text, root_, adds):
        seen["adds"] = adds
        raise Seen

    import rota.core.runner as runner
    monkeypatch.setattr(runner, "arrange_fault", fault)
    with pytest.raises(Seen):
        api._arrange_run_refusal(_sb(db).ctx, "b1", "c1", "tests/test_termui.py",
                                 "def test_x():\n    assert True\n")
    names = seen["adds"].splitlines()
    assert "tests/test_termui.py" in names
    assert DECLINED not in names


def test_a_write_to_a_declined_file_is_outside_the_prediction(db):
    """A test path is never a stray, so the declined file is a source file."""
    _decline(db, "src/click/termui.py")
    sb = _sb(db)
    assert api._outside_prediction(sb.ctx, "b1", ["src/click/termui.py"]) == [
        "src/click/termui.py"]


def test_a_declined_file_is_no_prediction_for_the_definition_door(db, tmp_path, monkeypatch):
    db.execute("DELETE FROM batch_touch WHERE batch_id = 'b1' AND grain != ?", (DECLINED,))
    db.commit()
    _decline(db)
    tree = tmp_path / "wt"
    (tree / "src").mkdir(parents=True)
    (tree / "src" / "a.py").write_bytes(b"def f():\n    return 1\n")
    monkeypatch.setattr(api, "_base_text", lambda ctx, root, rel: "")
    monkeypatch.setattr(api, "_changed_unnamed_defs", lambda ctx, rel, old, new: ["f"])
    sb = _sb(db)
    assert api._unnamed_def_strays(sb.ctx, tree, ["src/a.py"], []) == []


# The pin. A read of `batch_touch` or `touch_guesses` names its function
# here, with the reason it does not read `predicted_rows`.
ALLOWED = {
    # The one reader for the doors and the seat's working view.
    ("rota/core/lifecycle.py", "predicted_rows"),
    # P4: the page shows the Architect's own rows as a sense check.
    ("rota/core/lifecycle.py", "touch_set"),
    ("rota/core/predicates.py", "touch_note"),
    ("rota/roles/principal.py", "code_target"),
    # Whether the Architect wrote a prediction at all, not what it holds.
    ("rota/core/predicates.py", "annotate"),
    ("rota/core/predicates.py", "guess"),
    # The writers check their own staged rows.
    ("rota/roles/api.py", "batches_guess"),
    ("rota/roles/api.py", "batches_annotate"),
    # The item's guess before a batch exists. Its key is `guess:<item>`, and
    # each ruling on it writes a new set.
    ("rota/core/runner.py", "resolve_inbound"),
    ("rota/core/runner.py", "_guess_seed"),
    ("rota/roles/principal.py", "code_line"),
    ("rota/roles/principal.py", "land"),
    # Tools that read the raw record.
    ("rota/tools/audit.py", "orphaned_grain_refs"),
    ("rota/tools/nightreport.py", "_guess_section"),
    ("rota/tools/nightreport.py", "_seen"),
}

_TABLES = ("batch_touch", "touch_guesses")
_SQL = re.compile(r"(?i:FROM|JOIN)\s+(?:batch_touch|touch_guesses)\b")


def _reads(node: ast.AST) -> bool:
    """True when a string in `node` reads one of the tables: SQL that selects
    from it or joins it, or a compare with its name, as a staged-row read."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return _SQL.search(node.value) is not None
    if isinstance(node, ast.Compare):
        return any(isinstance(c, ast.Constant) and c.value in _TABLES
                   for c in [node.left, *node.comparators])
    return False


def _sites() -> set[tuple[str, str]]:
    root = Path(__file__).resolve().parents[2]
    out: set[tuple[str, str]] = set()
    for path in sorted((root / "rota").rglob("*.py")):
        rel = path.relative_to(root).as_posix()
        tree = ast.parse(path.read_bytes())

        def walk(node, fn):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    walk(child, child.name)
                    continue
                if _reads(child):
                    out.add((rel, fn))
                walk(child, fn)

        walk(tree, "<module>")
    return out


def test_no_second_reader_of_the_prediction_exists():
    """A new function that reads the touch rows raw must go through
    `predicted_rows`, or name its reason in ALLOWED."""
    assert _sites() - ALLOWED == set()


def test_every_allowed_site_still_reads_the_tables():
    """A stale entry hides a moved reader, so the list shrinks with the code."""
    assert ALLOWED - _sites() == set()
