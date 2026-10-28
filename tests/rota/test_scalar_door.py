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

NIGHTS = Path("D:/repos/rota/.rota")
NIGHT115 = NIGHTS / "clickI_night115.db"
NIGHT126 = NIGHTS / "clickI_night126.db"
ITEM = "version_option_show_python"
TICKET = "tk_1_version_option_show_python"
HIGH = ("priority='high' is a word where problem.prioritize takes a whole "
        "number; send priority=1, priority=2 or another whole number")


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _night_copy(night: Path, tmp_path) -> sqlite3.Connection:
    """A backup of a night's database in `tmp_path`. The night's own file
    opens read-only and immutable."""
    copy = tmp_path / night.name
    src = sqlite3.connect(f"file:{night.as_posix()}?mode=ro&immutable=1", uri=True)
    into = sqlite3.connect(str(copy))
    try:
        src.backup(into)
    finally:
        into.close()
        src.close()
    return connect(copy)


def _refused(sb, dotted: str, **kw):
    """Send one call that a door refuses, under a hook that collects the
    refusal, and send its offers through frame 144's follow check and fact
    check. Returns the sentence, the offers, the follow records and the fact
    records."""
    got = []
    prev, sandbox._ON_REFUSAL = sandbox._ON_REFUSAL, lambda *a: got.append(a)
    try:
        with pytest.raises(ArgumentError) as err:
            sb.call(dotted, **kw)
    finally:
        sandbox._ON_REFUSAL = prev
    assert len(got) == 1, "the refusal reached no follow check"
    _, name, args, exc, offers, facts = got[0]
    return (str(err.value), offers, sandbox.follow(sb, name, args, exc, offers),
            sandbox.check_facts(sb, facts))


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
    conn = _night_copy(NIGHT126, tmp_path)
    try:
        conn.execute("UPDATE items SET priority = 1 WHERE id = ?", (ITEM,))
        sb = build("vision_keeper", conn)
        with pytest.raises(ArgumentError):
            sb.call("problem.prioritize", id=ITEM, priority="high")
        for t, rid, values, *rest in sb.ctx.writes:
            _apply_write(conn, Write(t, rid, values, amends=rest[0] if rest else True),
                         sb.ctx.role)
        assert [r["id"] for r in next_batch(conn)] == ["bg_3"]
    finally:
        conn.close()


def test_the_offer_of_s249s_turn_5_is_recorded_and_admitted(db, monkeypatch):
    """The review of pass 1, finding 2: the offer and the hook in
    `Sandbox.call` had no test that fails without them."""
    monkeypatch.setattr(api, "RECORD", True)
    _item(db, ITEM)
    sb = build("vision_keeper", db)
    said, offers, recs, facts = _refused(sb, "problem.prioritize", id=ITEM,
                                         priority="high")
    assert said == f"problem.prioritize: {HIGH}"
    assert [(o.op, o.args) for o in offers] == [
        ("problem.prioritize", {"id": ITEM, "priority": 1})]
    assert [(r["second"], r["said_in_refusal"], r["bad_args"]) for r in recs] == [
        (None, True, [])]
    assert facts == []
    assert sb.ctx.writes == []


@pytest.mark.parametrize("night,seat", [(NIGHT126, "s249 turn 3"),
                                        (NIGHT115, "s200 turn 3")])
def test_a_ticket_id_with_a_word_gets_one_refusal_that_names_both(
        night, seat, tmp_path, monkeypatch):
    """The review of pass 1, finding 1. The seat sent the ticket's id with
    the word. The offer carries the ticket's item and the number, and the
    doors admit it."""
    if not night.exists():
        pytest.skip(f"{night.name} is absent")
    monkeypatch.setattr(api, "RECORD", True)
    conn = _night_copy(night, tmp_path)
    try:
        sb = build("vision_keeper", conn)
        said, offers, recs, facts = _refused(sb, "problem.prioritize",
                                             id=TICKET, priority="high")
        assert said == (
            f"problem.prioritize: {HIGH}. The id is wrong too: '{TICKET}' is "
            f"a row of tickets, not of items, and its item is '{ITEM}'. Send "
            f"id='{ITEM}' with the number")
        assert [o.args for o in offers] == [{"id": ITEM, "priority": 1}]
        assert [r["second"] for r in recs] == [None]
        assert [f["ok"] for f in facts] == [True]
        assert sb.ctx.writes == []
    finally:
        conn.close()


@pytest.mark.skipif(not NIGHT115.exists(), reason="night 115's database is absent")
def test_an_absent_id_with_a_word_gets_the_id_doors_offer(tmp_path, monkeypatch):
    """s200 turn 4 sent an id that no table holds. The id is the seat's to
    choose, so the offer carries `api.INVENT`, as the id door's offer does."""
    monkeypatch.setattr(api, "RECORD", True)
    conn = _night_copy(NIGHT115, tmp_path)
    try:
        sb = build("vision_keeper", conn)
        said, offers, recs, facts = _refused(
            sb, "problem.prioritize", id="tk_2_version_option_show_python",
            priority="high")
        assert said.startswith(
            f"problem.prioritize: {HIGH}. The id is wrong too: "
            f"'tk_2_version_option_show_python' is no row of items; items rows "
            f"are [")
        assert said.endswith("]. Send the id of a row of items with the number")
        (offer,) = offers
        assert offer.args == {"id": api.INVENT, "priority": 1}
        assert facts and all(f["ok"] for f in facts)
    finally:
        conn.close()


def test_a_padded_true_and_the_digits_are_truth_values():
    def f(flag: bool):
        pass
    for text, want in ((" true ", True), ("1", True), ("0", False),
                       ("False\n", False)):
        kw = {"flag": text}
        assert validate_args(f, kw) is None
        assert kw["flag"] is want


def test_an_optional_scalar_annotation_object_is_read():
    """`int | None` and `Optional[int]` as objects, not as strings: the
    binder's signature holds objects when `eval_str` succeeds."""
    import typing
    for ann in (int | None, typing.Optional[int]):
        def f(**_):
            pass
        f.__signature__ = inspect.Signature([inspect.Parameter(
            "n", inspect.Parameter.KEYWORD_ONLY, default=None, annotation=ann)])
        kw = {"n": "3"}
        assert validate_args(f, kw) is None and kw["n"] == 3
        assert validate_args(f, {"n": "many"}).startswith("n='many' is a word")


def test_a_call_with_no_op_names_the_function():
    def stub(a: float):
        pass
    assert validate_args(stub, {"a": "x"}) == (
        "a='x' is a word where stub takes a number; send a=1.0, a=2.5 or "
        "another number")


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
