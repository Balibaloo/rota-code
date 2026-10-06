"""
Frame 164: text where an op declares a number or a truth value.

Night 126, s249 turn 5 sent `problem.prioritize(priority='high')` and got OK.
SQLite kept the word in `items.priority`, an INTEGER column, and every
`loop.step` after it crashed in `next_batch`. The binder now converts the
text that the declared type reads, and refuses any other text.
"""
from __future__ import annotations

import inspect
import sqlite3
from pathlib import Path

import pytest

from rota.core import sandbox
from rota.core.db import Write, _apply_write, connect, init_db
from rota.core.sandbox import ArgumentError, build, validate_args
from rota.core.scheduler import next_batch
from rota.roles import api

NIGHT126 = Path("D:/repos/rota/.rota/clickI_night126.db")
ITEM = "version_option_show_python"


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _item(db, item_id="i1"):
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES (?, 'x', 'in_scope', 'approved', 1, 1)",
               (item_id,))


def _typed_scalars() -> list[tuple[str, str, str, str]]:
    """(art, verb, parameter, kind) for each op parameter of a scalar type.
    Read from the registry, so a new op with a typed scalar joins by itself."""
    out = []
    for (art, verb), fn in sorted(api.REGISTRY.items()):
        try:
            sig = inspect.signature(fn, eval_str=True)
        except (NameError, TypeError):
            sig = inspect.signature(fn)
        for name, p in sig.parameters.items():
            kind = sandbox._scalar_kind(p.annotation)
            if name != "ctx" and kind:
                out.append((art, verb, name, kind))
    return out


TYPED = _typed_scalars()


def test_s249s_word_for_a_priority_is_refused_and_writes_nothing(db):
    _item(db, ITEM)
    sb = build("vision_keeper", db)
    with pytest.raises(ArgumentError) as err:
        sb.call("problem.prioritize", id=ITEM, priority="high")
    assert str(err.value) == (
        "problem.prioritize: priority='high' is a word where "
        "problem.prioritize takes a whole number; send priority=1, "
        "priority=2 or another whole number")
    assert sb.ctx.writes == []


def test_s180s_digit_for_a_priority_lands_as_the_integer_1(db):
    _item(db, ITEM)
    sb = build("vision_keeper", db)
    assert sb.call("problem.prioritize", id=ITEM, priority="1") == {
        "id": ITEM, "priority": 1}
    (table, row, values, amends), = sb.ctx.writes
    assert (table, row, values, amends) == ("items", ITEM, {"priority": 1}, False)
    assert type(values["priority"]) is int


def test_a_word_for_a_truth_value_is_refused_and_true_converts(db):
    _item(db)
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('t1','i1','x')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c1','t1','the flag returns the default on EOF')")
    sb = build("critic", db)
    with pytest.raises(ArgumentError) as err:
        sb.call("verdicts.claim_encodes", criterion_id="c1", encodes="yes")
    assert str(err.value) == (
        "verdicts.claim_encodes: encodes='yes' is a word where "
        "verdicts.claim_encodes takes true or false; send encodes=true or "
        "encodes=false")
    assert sb.ctx.verdict_claims == {}
    assert sb.call("verdicts.claim_encodes", criterion_id="c1",
                   encodes="false")["encodes"] is False
    assert sb.ctx.verdict_claims == {"c1": False}


def test_a_value_of_the_declared_type_and_a_default_none_pass_unchanged():
    def f(a: int, b: float, c: bool, d: int | None = None):
        pass
    kw = {"a": 3, "b": 2.5, "c": False, "d": None}
    assert validate_args(f, kw) is None
    assert kw == {"a": 3, "b": 2.5, "c": False, "d": None}
    kw = {"a": " 7 ", "b": "0.5", "c": "True", "d": "-1"}
    assert validate_args(f, kw) is None
    assert kw == {"a": 7, "b": 0.5, "c": True, "d": -1}
    assert "takes a number" in validate_args(f, {"a": 1, "b": "nan", "c": 1})


@pytest.mark.skipif(not NIGHT126.exists(), reason="night 126's database is absent")
def test_next_batch_on_night_126_returns_bg_3_after_s249s_call(tmp_path):
    """The copy holds the item at 1, as s243 left it. s249's call goes
    through the door, and the scheduler's next batch is bg_3. The night's
    own file opens read-only, for the copy only."""
    copy = tmp_path / "night126.db"
    night = sqlite3.connect(f"file:{NIGHT126.as_posix()}?mode=ro&immutable=1",
                            uri=True)
    into = sqlite3.connect(str(copy))
    try:
        night.backup(into)
    finally:
        into.close()
        night.close()
    conn = connect(copy)
    try:
        conn.execute("UPDATE items SET priority = 1 WHERE id = ?", (ITEM,))
        sb = build("vision_keeper", conn)
        with pytest.raises(ArgumentError):
            sb.call("problem.prioritize", id=ITEM, priority="high")
        for t, rid, values, *rest in sb.ctx.writes:
            _apply_write(conn, Write(t, rid, values, amends=rest[0] if rest else True))
        assert [r["id"] for r in next_batch(conn)] == ["bg_3"]
    finally:
        conn.close()


def test_the_count_finds_the_typed_scalars_of_night_126():
    assert ("problem", "prioritize", "priority", "int") in TYPED
    assert ("verdicts", "claim encodes", "encodes", "bool") in TYPED


@pytest.mark.parametrize("art,verb,name,kind", TYPED,
                         ids=[f"{a}.{v}.{n}" for a, v, n, _ in TYPED])
def test_every_typed_scalar_refuses_the_word_high(art, verb, name, kind):
    fn = api.REGISTRY[(art, verb)]
    try:
        sig = inspect.signature(fn, eval_str=True)
    except (NameError, TypeError):
        sig = inspect.signature(fn)
    sig = sig.replace(parameters=[p for n, p in sig.parameters.items() if n != "ctx"])
    # The other required arguments get a value of their own type, so the
    # missing-argument check does not speak first.
    kw = {}
    for n, p in sig.parameters.items():
        if p.default is inspect.Parameter.empty:
            k = sandbox._scalar_kind(p.annotation)
            kw[n] = sandbox._SCALAR_EXAMPLE[k] if k else "x"
    kw[name] = "high"

    def target(**_):
        pass
    target.__signature__ = sig
    problem = validate_args(target, kw, op=(art, verb))
    assert problem is not None and problem.startswith(f"{name}='high' is a word where ")
    assert kw[name] == "high"
