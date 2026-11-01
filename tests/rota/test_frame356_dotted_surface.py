"""
Frame 356: a dotted surface ref resolves to its index row, at specify time
and at read time.

dry1's Terminologist s139 sent `surface_refs=['click.pause']` to
`criteria.specify`. The index held `src/click/termui.py::pause` and
`examples/termui/termui.py::pause`, and no grain `click.pause`. The vet kept
the ref as written. The encode door then refused every test body, because no
test calls a name `click.pause` (plans/dry1-third-wall-read-2026-11-01.md,
sections 1, 2 and 5). Pass 2 answers review 1 (plans/f356-review-p1.md):
the fixture holds only rows of dry1's index, and the indexer writes no
`path::Class.name` row.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.testkit.fixtures import seed_provenance

ITEM = "pause_waits_for_a_key"
LIBRARY = "src/click/termui.py::pause"

# The rows of dry1's code_index for these names, copied as the index holds
# them, in its order. The index holds `Context` as a class and no method row.
DRY1_SYMBOLS = (
    ("examples/termui/termui.py::pause", "function"),
    ("src/click/termui.py::pause", "function"),
    ("src/click/core.py::Context", "class"),
    ("src/click/utils.py::echo", "function"),
    ("src/click/_termui_impl.py::getchar", "function"),
    ("src/click/termui.py::getchar", "function"),
)
# dry1's row for `Context` spans these lines of src/click/core.py.
CONTEXT_LINES = (207, 956)


def _write_core(root):
    """A stand-in for click's core.py with `Context` at dry1's lines.

    Review 2, finding 1: the method grain needs the class body to define
    the method. `nothing_here` is a nested def, so it is no method.
    """
    start, end = CONTEXT_LINES
    body = ['    """A stand-in for click.Context."""',
            "",
            "    def invoke(self, callback, /, *args, **kwargs):",
            "        return callback(*args, **kwargs)",
            "",
            "    def forward(self, cmd, /, *args, **kwargs):",
            "        def nothing_here():",
            "            return None",
            "        return nothing_here()"]
    lines = ([f"# line {n}" for n in range(1, start)] + ["class Context:"]
             + body + ["    # body"] * (end - start - len(body)))
    pkg = root / "src" / "click"
    pkg.mkdir(parents=True)
    # click's package re-exports `Context`, so `from click import Context`
    # meets the import door and not the misplaced-name door.
    (pkg / "__init__.py").write_bytes(b"from .core import Context\n")
    (pkg / "core.py").write_bytes(("\n".join(lines) + "\n").encode())


@pytest.fixture
def db(tmp_path):
    _write_core(tmp_path)
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
                 "('project_root', ?)", (str(tmp_path),))
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version, priority) VALUES (?, ?, 'in_scope', 'approved', 1, 1, 1)",
                 (ITEM, "Make click.pause() wait for a key."))
    seed_provenance(conn, "items", ITEM, "decided")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk_1', ?, 'click.pause() waits for a key')", (ITEM,))
    for path in sorted({g.split("::")[0] for g, _ in DRY1_SYMBOLS}):
        conn.execute("INSERT INTO code_index (grain, grain_kind) "
                     "VALUES (?, 'path')", (path,))
    for grain, kind in DRY1_SYMBOLS:
        lines = CONTEXT_LINES if grain.endswith("::Context") else (0, 0)
        conn.execute("INSERT INTO code_index (grain, grain_kind, sym_kind, "
                     "line_start, line_end) VALUES (?, 'symbol', ?, ?, ?)",
                     (grain, kind, *lines))
    conn.execute("INSERT INTO frame_rulings (id, kind, reason) VALUES "
                 "('examples', 'attached', 'Contains example code')")
    conn.execute("INSERT INTO frame_rulings (id, kind, reason) VALUES "
                 "('src', 'program', 'Source code for the main package')")
    conn.commit()
    return conn


def _vet(db, ref):
    from rota.roles.api import _vet_surface

    ctx = build("terminologist", db, mode="criteria").ctx
    return _vet_surface(ctx, [ref], required=False, ticket_id="tk_1")


def _specify(db, ref):
    sb = build("terminologist", db, mode="criteria")
    sb.call("criteria.specify", id="c_1", ticket_id="tk_1", text="x",
            surface_refs=[ref])
    return json.loads(sb.ctx.writes[-1][2]["surface_refs"])


def test_s139_dotted_click_pause_stores_the_programs_row(db):
    assert _vet(db, "click.pause") == [LIBRARY]
    assert _specify(db, "click.pause") == [LIBRARY]


@pytest.mark.parametrize("ref", ["pause", "click.pause()", "click.termui.pause",
                                 "termui.pause", LIBRARY])
def test_every_form_of_the_ref_stores_the_same_row(db, ref):
    assert _vet(db, ref) == [LIBRARY]


def test_a_dotted_ref_with_no_row_stays_as_written(db):
    assert _vet(db, "click.nothing_here") == ["click.nothing_here"]


def test_a_method_ref_stores_its_class_row_and_the_method(db):
    """Review 1, finding 1: the indexer does not descend into a class body,
    so the method goes after the class row."""
    assert _vet(db, "click.Context.invoke") == [
        "src/click/core.py::Context.invoke"]
    assert _vet(db, "Context.invoke") == ["src/click/core.py::Context.invoke"]


def _repair(db, ref):
    from rota.roles.api import _vet_surface

    ctx = build("terminologist", db, mode="criteria").ctx
    return _vet_surface(ctx, [ref], required=True, ticket_id="tk_1")


@pytest.mark.parametrize("ref", ["click.Context.invok", "click.Context.nothing_here",
                                 "click.nothing_here"])
def test_a_method_the_class_does_not_define_is_no_surface(db, ref):
    """Review 2, finding 1: a typo after a class grain stored a method grain,
    and skipped the near-match scan and the repair door's rule that a
    surface exists. A nested def is no method of the class. The item names
    `pause`, so `criteria.specify` refuses any other surface by another
    door, and the vet stands for the specify call here."""
    assert _vet(db, ref) == [ref]
    with pytest.raises(ValueError, match="is not a symbol the index knows"):
        _repair(db, ref)


def test_the_module_part_narrows_the_rows(db):
    """Review 1, finding 3: `os.path` is no module of the row, and
    `click.termui` picks one of the two `getchar` rows."""
    assert _vet(db, "os.path.echo") == ["os.path.echo"]
    assert _vet(db, "click.core.pause") == ["click.core.pause"]
    assert _vet(db, "click.termui.getchar") == ["src/click/termui.py::getchar"]
    with pytest.raises(ValueError, match="getchar names 2 symbols"):
        _vet(db, "click.getchar")


@pytest.fixture
def tester(db):
    """dry1's tk_1 criterion as stored before the fix, in a running batch."""
    def make(surface):
        db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                   "VALUES ('c_1', 'tk_1', 'pause waits for a key press', ?)",
                   (json.dumps(surface),))
        db.execute("INSERT INTO batches (id, item_id, status, head_commit) "
                   "VALUES ('b1', ?, 'running', 'abc123')", (ITEM,))
        db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                   "('b1', 'tk_1')")
        db.commit()
        sb = build("tester", db, batch_id="b1", mode="tests_missing")
        sb.call("tests.triage", criterion_id="c_1", verdict="encodable")
        return sb
    return make


def _encode(sb, call, imports="import click"):
    return sb.call("tests.encode", id="tst1", criterion_id="c_1",
                   path="tests/test_pause.py",
                   body=f"{imports}\n"
                        f"def test_pause(monkeypatch):\n"
                        f"    monkeypatch.setattr('click.termui.getchar', lambda echo=False: 'x')\n"
                        f"    assert {call} is None\n")


@pytest.mark.parametrize("call, imports", [
    ("click.pause()", "import click"),
    ("pause()", "from click.termui import pause")])
def test_a_stored_dotted_ref_passes_a_body_that_calls_it(tester, call, imports):
    """Issue 1: dry1's three criteria hold `click.pause`, stored before the
    vet resolved it. The never-calls check reads the ref as its row."""
    sb = tester(["click.pause"])
    assert _encode(sb, call, imports)


def test_a_body_that_calls_neither_is_refused_by_the_surface_name(tester):
    sb = tester(["click.pause"])
    with pytest.raises(ValueError, match="this test never calls 'click.pause'"):
        _encode(sb, "click.echo('x')")


def test_a_stored_method_ref_passes_a_call_of_the_method(tester):
    sb = tester(["click.Context.invoke"])
    assert sb.call("tests.encode", id="tst1", criterion_id="c_1",
                   path="tests/test_pause.py",
                   body="import click\n"
                        "def test_invoke():\n"
                        "    ctx = click.Context(click.Command('x'))\n"
                        "    assert ctx.invoke(lambda: 3) == 3\n")


METHOD = "src/click/core.py::Context.invoke"
INVOKE_BODY = ("def test_invoke():\n"
               "    ctx = Context()\n"
               "    assert ctx.invoke(lambda: 3) == 3\n")


def _encode_body(sb, body):
    return sb.call("tests.encode", id="tst1", criterion_id="c_1",
                   path="tests/test_invoke.py", body=body)


def test_a_stored_method_grain_hints_an_import_of_its_class(tester):
    """Review 2, finding 2: the hint read `from click.core import
    Context.invoke`, and that line does not parse."""
    sb = tester([METHOD])
    with pytest.raises(ValueError) as e:
        _encode_body(sb, "from click import Context\n" + INVOKE_BODY)
    assert "`from click.core import Context`" in str(e.value)
    assert "Context.invoke`" not in str(e.value)


def test_a_stored_method_grain_passes_an_import_of_its_class(tester):
    sb = tester([METHOD])
    assert _encode_body(sb, "from click.core import Context\n" + INVOKE_BODY)


def test_a_ref_with_no_name_names_the_step_the_tester_can_take(tester):
    """Review 1, finding 2: "call it" cannot help when no part of the ref
    is a name. The refusal says so and names the question to the
    Terminologist, which every Tester mode at this door holds (F25)."""
    sb = tester(["press any key"])
    with pytest.raises(ValueError) as e:
        _encode(sb, "click.pause()")
    assert "'press any key', and the index holds no such surface" in str(e.value)
    assert "msg.question_terminologist(refs=['c_1']" in str(e.value)
    assert "tests.triage" not in str(e.value)
