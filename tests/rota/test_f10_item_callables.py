"""
F10 of the root-fix audit of 2026-10-27: the surface a criterion names.

`item_callables` is the one reader of the callables an item gives. It reads
the item, its live statements and the ticket, and it splits the names into
the ones the index holds and the new ones. Before it, the specify door, the
repair's `_vet_surface` and `_surface_outside_batch` each read the item by
their own rule, and the three rules disagreed. Each test below is one place
where the old rule and the reader disagree.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from tests.rota.test_criteria_surface import _index, _night142


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _item(db, text, ticket=""):
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i9', ?, 'in_scope', 'approved', 1, 1)", (text,))
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk9','i9',?)",
               (ticket,))
    db.commit()


def _specify(db, surface):
    sb = build("terminologist", db, mode="criteria")
    return sb.call("criteria.specify", id="c9", ticket_id="tk9",
                   text="confirm returns the default when stdin is closed",
                   surface_refs=surface)


def test_a_function_named_in_words_is_a_name_the_index_holds(db):
    """The old known rule took a snake_case word only. "The function named
    confirm" names `confirm`, and the index holds it, so a surface on
    another callable tests another behaviour."""
    _index(db, "src/click/termui.py::confirm", "src/click/termui.py::prompt")
    _item(db, "Change the function named confirm so that it returns the "
              "default on EOF.")
    with pytest.raises(ValueError, match="the item names confirm"):
        _specify(db, ["prompt"])
    assert _specify(db, ["confirm"])["id"] == "c9"


def test_a_method_the_item_calls_is_a_name_the_index_holds(db):
    """The old rule matched `%::invoke`, so a method `Context.invoke` was not
    in the index, and the door refused the right surface as old behaviour."""
    _index(db, "src/click/core.py::Context.invoke")
    _item(db, "The invoke() method must pass the parent context on.")
    out = _specify(db, ["Context.invoke"])
    assert out["id"] == "c9"


def test_a_new_name_in_a_statement_is_a_name_the_item_gives(db):
    """The repair's `_vet_surface` read the item and the ticket only. A
    statement of the item that names the new helper gives that name, as
    `_surface_outside_batch` already read it (frame 215)."""
    from rota.roles.api import _vet_surface

    _night142(db)
    db.execute("UPDATE statements SET text = text || ' Put it in a new helper "
               "named python_suffix.' WHERE id = 's4'")
    db.commit()
    ctx = build("terminologist", db, mode="criterion_repair").ctx
    assert _vet_surface(ctx, ["python_suffix"], required=True,
                        ticket_id="tk_2") == ["python_suffix"]


def test_a_plain_word_of_the_ticket_does_not_admit_a_surface_outside_the_batch(db):
    """`_surface_outside_batch` took every word as a name. The ticket says
    "the message" in English, and that admitted an `examples/` callable
    named `message`. A name is given in a callable's form (night 116's
    form rule)."""
    from rota.roles.api import _surface_outside_batch

    _night142(db)
    _index(db, "examples/imagepipe/imagepipe.py::message")
    ctx = build("terminologist", db, mode="criterion_repair").ctx
    with pytest.raises(ValueError, match="No word of the request"):
        _surface_outside_batch(ctx, "tk_2",
                               ["examples/imagepipe/imagepipe.py::message"])
    # A name in identifier form that the index holds still admits it.
    _index(db, "examples/imagepipe/imagepipe.py::version_option")
    _surface_outside_batch(ctx, "tk_2",
                           ["examples/imagepipe/imagepipe.py::version_option"])


_API = pathlib.Path(__file__).resolve().parents[2] / "rota" / "roles" / "api.py"


def _functions(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    src = path.read_text(encoding="utf-8")
    return {n.name: ast.get_source_segment(src, n) for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef)}


def test_item_callables_is_the_one_reader_of_the_names_an_item_gives():
    """The pin of F10. The kind-word form rule lives in `item_callables`
    alone, and the item's words come from `_item_words` alone. The three
    surface readers call `item_callables` and read no item row."""
    kind_rule = "(?:function|callable|method|helper|decorator)"
    pkg = pathlib.Path(__file__).resolve().parents[2] / "rota"
    holders = []
    for path in pkg.rglob("*.py"):
        for name, src in _functions(path).items():
            if kind_rule in src:
                holders.append(name)
    assert holders == ["item_callables"]
    fns = _functions(_API)
    assert "_named_new_callables" not in fns
    assert "_named_existing_callables" not in fns
    for name in ("_vet_surface", "_surface_names_what_the_item_names",
                 "_surface_outside_batch"):
        assert "item_callables(" in fns[name], name
        assert "FROM tickets" not in fns[name], name
        assert "statements" not in fns[name].split('"""')[-1], name
