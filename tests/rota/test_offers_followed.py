"""
The follow check of frame 144, held by direct tests.

A refusal that names a call records it in `ctx.offers` (`api._offer`).
`sandbox.dry_run` sends that call through the real doors on the same `ctx`
and puts `ctx` back. The hook in `conftest.py` does this for every refusal
that a test meets through `Sandbox.call`. These tests hold the doors of
`tests.encode` that the table ranks first, frame 135's project-id door, and
the instrument itself.

An offer that the doors refuse today is a finding, and a strict xfail holds
it here. `KNOWN_REFUSED_OFFERS` in `conftest.py` names the same finding, so
the other tests that meet it stay green.
"""
from __future__ import annotations

import pytest

from rota.core import sandbox
from rota.core.sandbox import build
from rota.roles import api
from tests.rota.test_t0_sandbox import (  # noqa: F401
    _PRORATE, _a_criterion, _a_stored_test, _answer_tester, _challenge_tester,
    _challenge_wake, db)


def _refused(sb, op, **kwargs):
    """The refusal of `op(**kwargs)`, and the offers it recorded."""
    with pytest.raises(ValueError) as exc:
        sb.call(op, **kwargs)
    return str(exc.value), list(sb.ctx.offers)


def _admitted(sb, offer):
    res = sandbox.dry_run(sb, offer.op, offer.args, offer.then)
    return res.admitted, res.refusal


_PRORATES = "prorating a mid-month upgrade charges the unused remainder"


# -- tests.encode, the stored-test doors (the table's rank 1) ---------------

def test_the_stored_path_offer_is_admitted(db):
    """`api.py`'s stored-path door: "send this encode again with path=...".
    The named call replaces t1 at its own path."""
    _a_criterion(db, _PRORATES)
    _a_stored_test(db)
    sb = _challenge_tester(db)
    said, offers = _refused(sb, "tests.encode", id="t1", criterion_id="c1",
                            path="q.py", body=_PRORATE + " # fixed")
    assert said == "t1 is stored at p.py. To replace it, send this encode again with path='p.py'."
    assert [(o.op, o.args["path"], o.args["id"]) for o in offers] == [
        ("tests.encode", "p.py", "t1")]
    assert _admitted(sb, offers[0]) == (True, None)
    assert sb.ctx.writes == []


def test_the_other_batch_offer_of_a_new_id_is_admitted(db):
    """"Choose another id": the offer marks the id as the seat's to invent,
    and a fresh id is admitted."""
    _a_criterion(db, _PRORATES)
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b2','i1','running')")
    _a_stored_test(db, batch_id="b2")
    sb = _challenge_tester(db)
    said, offers = _refused(sb, "tests.encode", id="t1", criterion_id="c1",
                            path="p.py", body=_PRORATE + " # fixed")
    assert said.endswith("Choose another id.")
    assert offers[0].args["id"] is api.INVENT
    assert _admitted(sb, offers[0]) == (True, None)


def test_the_same_criterion_clash_offer_of_the_stored_id_is_admitted(db):
    """"send this encode again with id=...": the stored id replaces its own
    test at its own file."""
    _a_criterion(db, _PRORATES)
    _a_stored_test(db)
    sb = _challenge_tester(db)
    said, offers = _refused(sb, "tests.encode", id="t9", criterion_id="c1",
                            path="p.py", body=_PRORATE + " # fixed")
    assert "send this encode again with id='t1'" in said
    assert [o.args["id"] for o in offers] == ["t1"]
    assert _admitted(sb, offers[0]) == (True, None)


# -- frame 135's project-id door ---------------------------------------------

def test_a_project_id_at_a_new_path_is_offered_a_new_id_that_lands(db):
    """Night 120 s140: a new test under a project id at its own new path.
    The new id at that path is admitted."""
    _a_criterion(db, _PRORATES)
    _a_stored_test(db, id="inh_022b8a87", criterion_id=None,
                   path="tests/test_utils/test_confirm.py")
    sb = _answer_tester(db)
    _, offers = _refused(sb, "tests.encode", id="inh_022b8a87", criterion_id="c1",
                         path="tests/test_utils/test_echo_json.py",
                         body=_PRORATE + " # new", batch_id="b1")
    assert len(offers) == 1 and offers[0].args["id"] is api.INVENT
    assert _admitted(sb, offers[0]) == (True, None)


def test_a_challenged_project_test_is_offered_its_own_file_and_a_new_id(db):
    """A challenge of the project test that sends it to a new file gets two
    calls, its own file or a new id. The doors admit both."""
    from rota.core.harness import inherited_id
    pid = inherited_id("tests/test_utils/test_confirm.py")
    _a_criterion(db, _PRORATES)
    _a_stored_test(db, id=pid, criterion_id="c1",
                   path="tests/test_utils/test_confirm.py")
    sb = _challenge_wake(db, [pid])
    _, offers = _refused(sb, "tests.encode", id=pid, criterion_id="c1",
                         path="tests/test_utils/test_new.py", body=_PRORATE + " # moved")
    assert [(o.args["id"], o.args["path"]) for o in offers] == [
        (pid, "tests/test_utils/test_confirm.py"),
        (api.INVENT, "tests/test_utils/test_new.py")]
    for o in offers:
        assert _admitted(sb, o) == (True, None), o


def test_a_project_id_at_its_own_path_is_offered_a_new_id_that_lands(db):
    """The finding of frame 144 pass 1: the new id kept the seat's path, the
    project test's file, and the clash door refused it. Frame 343: the offer
    names a new file beside the project file."""
    _a_criterion(db, _PRORATES)
    _a_stored_test(db, id="inh_022b8a87", criterion_id=None,
                   path="tests/test_utils/test_confirm.py")
    sb = _answer_tester(db)
    _, offers = _refused(sb, "tests.encode", id="inh_022b8a87", criterion_id="c1",
                         path="tests/test_utils/test_confirm.py",
                         body=_PRORATE + " # new", batch_id="b1")
    assert offers[0].args["path"] == "tests/test_utils/test_confirm_c1.py"
    assert _admitted(sb, offers[0]) == (True, None)


# The finding of frame 144 pass 1 is fixed by frame 204: the invented-literal
# door stages its row itself and admits the encode with the added import.
def test_the_added_import_offer_is_admitted(db):
    _a_criterion(db, _PRORATES)
    sb = _answer_tester(db)
    body = ("from billing import prorate\ndef test_it():\n"
            "    m = pytest.MonkeyPatch()\n"
            "    assert prorate(999, 1, 3) == 'default_answer'\n")
    said, offers = _refused(sb, "tests.encode", id="t1", criterion_id="c1",
                            path="p.py", body=body, batch_id="b1")
    assert said.startswith("the test uses pytest and never imports it")
    assert offers[0].args["body"] == "import pytest\n" + body
    assert _admitted(sb, offers[0]) == (True, None)


_EIGHT = ("from billing import prorate\ndef test_it():\n"
          "    assert prorate('alpha', 'bravo', 'charlie', 'delta', 'echo', "
          "'foxtrot', 'golf', 'hotel') == 1\n")


def test_the_literal_door_admits_eight_owed_literals_in_one_row(db):
    """The finding of frame 144 pass 2 named six of eight literals, and the
    encode sent again met the same door for the other two. Frame 204: the
    door stages one `invented` row for all eight and admits the encode."""
    _a_criterion(db, _PRORATES)
    sb = _answer_tester(db)
    assert sb.call("tests.encode", id="t1", criterion_id="c1", path="p.py",
                   body=_EIGHT, batch_id="b1")
    (row,) = [w for w in sb.ctx.writes if w[0] == "ledger"]
    assert row[2]["kind"] == "invented"
    assert "golf" in row[2]["default_taken"] and "hotel" in row[2]["default_taken"]


def test_an_argument_error_leaves_no_offer_of_the_call_before(db):
    """The offers are cleared before the argument check, so a call that
    fails it holds none of the last call's offers (review point 9)."""
    from rota.core.sandbox import ArgumentError
    _a_criterion(db, _PRORATES)
    _a_stored_test(db)
    sb = _challenge_tester(db)
    _refused(sb, "tests.encode", id="t1", criterion_id="c1", path="q.py",
             body=_PRORATE + " # fixed")
    assert sb.ctx.offers
    with pytest.raises(ArgumentError):
        sb.call("tests.encode", id="t1", criterion_id="c1", path="q.py",
                body=_PRORATE, no_such=1)
    assert sb.ctx.offers == []


# -- code.write ---------------------------------------------------------------

@pytest.mark.xfail(strict=True, reason=(
    "finding of frame 144 pass 1: _code_write, the cut door, 'To add after it "
    "send start=, end='. The seat's text replaces the def, so the text added "
    "after it defines the name twice"))
def test_the_add_after_offer_of_a_cut_span_is_admitted(tmp_path):
    from rota.core.db import init_db
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
                 "VALUES ('i1','x','in_scope','approved',1,1)")
    root = tmp_path / "wt"
    root.mkdir()
    (root / "m.py").write_text("@dec\n@dec2(\n    1)\ndef f():\n    a = 1\n    return a\nx = 1\n")
    conn.execute("INSERT INTO batches (id, item_id, status, worktree) "
                 "VALUES ('b1','i1','running',?)", (str(root),))
    conn.commit()
    from rota.roles import prompts
    sb = build("developer", conn, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    _, offers = _refused(sb, "code.write", path="m.py", start=3, end=6,
                         text="def f():\n    return 1\n")
    after = [o for o in offers if o.said.startswith("To add after it")]
    assert after
    assert _admitted(sb, after[0]) == (True, None)


def test_a_text_that_breaks_the_parser_gets_the_cut_refusal(tmp_path):
    """200000 nested minus signs make ast.parse raise MemoryError. The cut
    door's offer of the whole def then holds INVENT, and the seat meets the
    refusal that it met before c888968 (the review of 8726a13, high 1)."""
    sb = _developer(tmp_path, "def a(\n    x,\n):\n    return x\n")
    said, offers = _refused(sb, "code.write", path="m.py", start=0, end=1,
                            text="-" * 200000 + "1")
    assert said == (
        "start=0, end=1: end=1 falls inside a (lines 0 to 4 in code.source "
        "numbering). Line 0 is 'def a('. Line 1 is '    x,'. To replace a whole "
        "send start=0, end=4. To add after it send start=4, end=4.")
    whole = [o for o in offers if o.said.startswith("To replace a whole")]
    assert [o.args["text"] for o in whole] == [api.INVENT]


@pytest.mark.xfail(strict=True, reason=(
    "finding of frame 144 pass 3: _code_write at an insert, _future_door. A "
    "text that ast.parse cannot hold raises MemoryError, and the session "
    "crashes where a refusal belongs"))
def test_an_insert_of_a_text_that_breaks_the_parser_is_refused(tmp_path):
    sb = _developer(tmp_path, "def a(\n    x,\n):\n    return x\n")
    with pytest.raises(ValueError):
        sb.call("code.write", path="m.py", start=4, end=4, text="-" * 200000 + "1")


def test_a_new_finding_in_an_xfail_test_turns_its_report_red():
    """An xfail mark holds one known finding. Another finding of the hook in
    the same test fails it (the review of 8726a13, low 3)."""
    from types import SimpleNamespace

    from tests.rota.conftest import unhide
    report = SimpleNamespace(when="call", outcome="skipped", wasxfail="one finding",
                             longrepr=None)
    unhide(report, ["door code.write ..."])
    assert report.outcome == "failed" and not hasattr(report, "wasxfail")
    assert "door code.write" in report.longrepr
    known = SimpleNamespace(when="call", outcome="skipped", wasxfail="one finding")
    unhide(known, [])
    assert known.outcome == "skipped" and known.wasxfail == "one finding"


def test_a_helper_of_two_doors_gives_two_door_identities(tmp_path):
    """`_end_offer` serves the cut door and the cross-block door. Its line
    alone read as one door for both (the review of 8726a13, low 4)."""
    sb = _developer(tmp_path, "def g():\n    try:\n        a = 1\n    finally:\n"
                              "        d = (\n            4)\n")
    said = "To stop where the body of try ends send end=3."
    sites = []
    for end in (5, 4):          # a cut boundary, then a whole one in another block
        msg, offers = _refused(sb, "code.write", path="m.py", start=2, end=end,
                               text="        a = 2\n")
        assert said in msg
        sites += [o.site for o in offers if o.said == said]
    assert len(sites) == 2
    assert [s.split(" < ")[0].rsplit(" in ", 1)[1] for s in sites] == ["_end_offer"] * 2
    assert sites[0] != sites[1]
    assert all(s.endswith(" in _code_write") for s in sites)


def test_an_unsent_offer_sends_its_span_with_the_lines_it_holds(tmp_path):
    """The text of "To stop where ... ends send end=3." is the seat's, so the
    offer is not sent. Its span goes to the doors with its own lines, and
    one line more is refused (the review of 8726a13, low 6)."""
    sb = _developer(tmp_path, "def g():\n    try:\n        a = 1\n    finally:\n"
                              "        d = (\n            4)\n")
    kwargs = {"path": "m.py", "start": 2, "end": 5, "text": "        a = 2\n"}
    with pytest.raises(ValueError) as exc:
        sb.call("code.write", **kwargs)
    offer = next(o for o in sb.ctx.offers if o.said.startswith("To stop where"))
    [rec] = sandbox.follow(sb, "code.write", kwargs, exc.value, [offer])
    assert rec["skipped"] and rec["span_only"] and rec["second"] is None
    late = api.Offer(offer.op, {**offer.args, "end": 4}, (), offer.frames, offer.said)
    [rec] = sandbox.follow(sb, "code.write", kwargs, exc.value, [late])
    assert rec["second"].startswith("ValueError: start=2, end=4 crosses"), rec


# -- the fact check (frame 144, change 1(d)) --------------------------------------

def _developer(tmp_path, src):
    from rota.core.db import init_db
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
                 "VALUES ('i1','x','in_scope','approved',1,1)")
    root = tmp_path / "wt"
    root.mkdir()
    (root / "m.py").write_text(src)
    conn.execute("INSERT INTO batches (id, item_id, status, worktree) "
                 "VALUES ('b1','i1','running',?)", (str(root),))
    conn.commit()
    from rota.roles import prompts
    return build("developer", conn, batch_id="b1", mode="batch_start",
                 allow=prompts.mode_tools("developer", "batch_start"))


def test_a_cut_refusal_quotes_lines_that_are_true(tmp_path):
    """The cut door's spans and quoted lines are checked against the file."""
    sb = _developer(tmp_path, "def a(\n    x,\n):\n    return x\n")
    _refused(sb, "code.write", path="m.py", start=0, end=1, text="def a(x):\n")
    facts = sandbox.check_facts(sb, sb.ctx.facts)
    assert {f["kind"] for f in facts} >= {"span", "line_text"}
    assert all(f["ok"] for f in facts), facts


def test_the_fact_check_reads_a_span_and_a_line_against_the_tree(tmp_path):
    """A span that ends one line early and a line that counts from 1 stayed
    green under a check of bounds only (the review of 8726a13, high 2)."""
    sb = _developer(tmp_path, "@dec\ndef f():\n    return 1\nx = 1\n")
    f_ = (("head", "def f():"), ("name", "f"), ("node", "FunctionDef"), ("path", "m.py"))
    dec = (("path", "m.py"), ("quote", "@dec"))
    after = (("end_of", "f"), ("path", "m.py"))
    facts = [api.Fact("span", (0, 3), f_), api.Fact("span", (0, 2), f_),
             api.Fact("line", 0, dec), api.Fact("line", 1, dec),
             api.Fact("span", (3, 3), after), api.Fact("span", (4, 4), after)]
    assert [r["ok"] for r in sandbox.check_facts(sb, facts)] == [
        True, False, True, False, True, False]


_B2_INSIDE = (
    "start=1, end=4: start=1 falls inside a (lines 0 to 4 in code.source numbering). "
    "start=1 is inside the decorators of a, which start at line 0. Line 1 is '@other'. "
    "Line 3 is '    return x'. Your text's first line is line 2 of the file, so a span "
    "that replaces it starts at start=2. To edit inside a send start=3, which is where "
    "the body of a starts. To replace a whole send start=0, end=4. To add after it send "
    "start=4, end=4.")
_B2_BELOW = (
    "start=2, end=4: start=2 falls inside a (lines 0 to 4 in code.source numbering). "
    "start=2 is below the decorators of a, which start at line 0. Line 2 is 'def a(x):'. "
    "Line 3 is '    return x'. To edit inside a send start=3, which is where the body "
    "of a starts. To replace a whole send start=0, end=4. To add after it send start=4, "
    "end=4.")


@pytest.mark.parametrize("dec", ["@dec(" + "-" * 400 + "1)", "@dec" + ".a" * 2000,
                                 "@ dec . more(1)"],
                         ids=["minus400", "attr2000", "spaced"])
def test_a_cut_at_deep_decorators_gets_the_refusal_of_b2ed55b(tmp_path, dec):
    """`ast.unparse` of the first decorator recursed, and 400 nested minus
    signs or a chain of 2000 attributes crashed the seat. The head now comes
    from the decorator's own line. A spaced decorator read false with the
    unparsed head (the review of fed7c58, high 1 and low 4). The refusals
    are the bytes of b2ed55b."""
    sb = _developer(tmp_path, "\n".join([dec, "@other", "def a(x):", "    return x", ""]))
    for start, want in ((1, _B2_INSIDE), (2, _B2_BELOW)):
        said, _ = _refused(sb, "code.write", path="m.py", start=start, end=4,
                           text="def a(x):\n    return 1\n")
        assert said == want
        facts = sandbox.check_facts(sb, sb.ctx.facts)
        assert [f["kind"] for f in facts].count("line") == 1
        assert all(f["ok"] for f in facts), facts


def test_a_line_quote_starts_the_line_at_a_word_boundary():
    """`@dec` passed on `@decorate(1)` while the check read `in` (the review
    of fed7c58, low 4)."""
    holds = sandbox._line_holds
    assert holds("@dec(1)", {"quote": "@dec"})[0]
    assert holds("  @ dec . more(1)", {"quote": "@ dec . more"})[0]
    assert not holds("@decorate(1)", {"quote": "@dec"})[0]
    assert not holds("x = 1  # @dec", {"quote": "@dec"})[0]
    assert holds('    """Doc and more', {"docstring": True, "quote": "Doc and mo"})[0]
    assert not holds('    """Other', {"docstring": True, "quote": "Doc"})[0]


def test_a_decorator_line_off_by_one_reads_false_on_a_twin_decorator(tmp_path):
    """With `@dec` above `@dec.b`, the decorator door's line moved down by
    one still passed: `.` is a word boundary (the review of ee17f70, low
    3). The line's head up to its bracket must be the quote."""
    holds = sandbox._line_holds
    assert not holds("@dec.b", {"quote": "@dec"})[0]
    assert holds("@dec.b(1)", {"quote": "@dec.b"})[0]
    sb = _developer(tmp_path, "@dec\n@dec.b\ndef a(x):\n    return x\n")
    said, _ = _refused(sb, "code.write", path="m.py", start=1, end=4,
                       text="def a(x):\n    return 1\n")
    assert "decorators of" in said
    [line] = [f for f in sb.ctx.facts if f.kind == "line"]
    assert all(r["ok"] for r in sandbox.check_facts(sb, sb.ctx.facts))
    moved = api.Fact("line", line.value + 1, line.where, line.site)
    assert not sandbox.check_facts(sb, [moved])[0]["ok"]


def test_a_span_that_names_a_statement_and_no_head_reads_false():
    """A span fact with a `node` and an empty `head` skipped the head
    check, so a door that lost its head stayed green (the review of
    ee17f70, low 4). A `match_case` has no line of its own and keeps the
    span check."""
    lines = ["def f():", "    return 1"]
    named = {"node": "FunctionDef", "name": "f"}
    assert sandbox._span_holds(lines, 0, 2, {**named, "head": "def f():"})[0]
    assert not sandbox._span_holds(lines, 0, 2, {**named, "head": ""})[0]
    assert not sandbox._span_holds(lines, 0, 2, named)[0]
    case = ["match x:", "    case 1:", "        y = 1"]
    assert sandbox._span_holds(case, 1, 3, {"node": "match_case", "head": ""})[0]


def test_the_line_of_a_compile_refusal_is_read_by_compiling_the_text():
    """Python 3.14 gives no `exc.text` for an error of the compile stage, so
    the check held such a line to its bounds only (the review of fed7c58,
    low 3)."""
    sb = sandbox.SimpleNamespace(ctx=None)
    text = "x = 1\nfrom __future__ import annotations\ny = 2\n"
    at = (("quote", None), ("text", text))
    facts = [api.Fact("line", n, at) for n in (1, 2, 0)]
    assert [r["ok"] for r in sandbox.check_facts(sb, facts)] == [True, False, False]


def test_a_nested_statement_of_the_same_type_does_not_stand_in():
    """A span fact with a type and no name matched any statement of that
    type, so (1, 3) passed for the outer if at (0, 3) (the review of
    fed7c58, low 10)."""
    lines = ["if a:", "    if b:", "        x = 1", "y = 2"]
    outer = {"node": "If", "name": None, "head": "if a:"}
    assert sandbox._span_holds(lines, 0, 3, outer)[0]
    assert not sandbox._span_holds(lines, 1, 3, outer)[0]
    assert sandbox._span_holds(lines, 1, 3, {**outer, "head": "if b:"})[0]


def test_a_known_false_fact_is_known_by_its_sentence(monkeypatch):
    """The known list keyed on the function, and every fact site of
    code.write is in `_code_write`. A false fact of another door in the same
    test was hidden (the review of fed7c58, low 11). Design 200 pass 2b
    fixed the one known entry, so the test sets one of its own."""
    from tests.rota import conftest
    from tests.rota.conftest import _problems
    test = _OF_ID + "test_the_defines_twice_numbers_are_code_source_numbers"
    monkeypatch.setattr(conftest, "KNOWN_FALSE_FACTS",
                        {(test, "line_text", " twice (lines ")})
    rec = {"kind": "line_text", "ok": False, "value": "def f", "where": {},
           "site": "api.py:1 in _code_write", "why": "no"}
    assert _problems(test, [{**rec, "refusal": "m.py defines f twice (lines 1 and 3)."}]) == []
    assert _problems(test, [{**rec, "refusal": "start=1, end=4: start=1 falls inside a"}])


_OF_ID = "tests/rota/test_offers_followed.py::"


def test_a_session_records_no_offer_and_a_test_records_frames(tmp_path, monkeypatch):
    """`_offer` read the door on every refusal of a session, 0.29 ms each.
    A session now records nothing, and a test keeps the raw frames, which
    `Offer.site` reads (the review of fed7c58, low 2)."""
    sb = _developer(tmp_path, "def a(\n    x,\n):\n    return x\n")
    _, offers = _refused(sb, "code.write", path="m.py", start=0, end=1, text="def a(x):\n")
    assert offers and all(type(c) is type(sandbox._fill.__code__) and type(n) is int
                          for c, n in offers[0].frames)
    assert offers[0].site.endswith(" in _code_write")
    monkeypatch.setattr(api, "RECORD", False)
    _, offers = _refused(sb, "code.write", path="m.py", start=0, end=1, text="def a(x):\n")
    assert offers == [] and sb.ctx.facts == []


def test_a_refusal_raised_in_a_library_names_its_door(tmp_path):
    """A surrogate in the text makes `ast.parse` raise in `ast.py`. The
    identity stopped at that first frame and read '' (the review of fed7c58,
    low 5)."""
    sb = _developer(tmp_path, "x = 1\n")
    with pytest.raises(ValueError) as exc:
        sb.call("code.write", path="m.py", text="x = '" + chr(0xD800) + "'\n")
    site = sandbox._raise_site(exc.value)
    assert " in _parse_compile < " in site and site.endswith(" in _code_write")


def test_an_argument_error_of_the_binder_names_its_door(tmp_path):
    """`Sandbox.call` and `dry_run` raise a missing or an unknown argument
    themselves. The walk stopped at their frame with an empty chain, so the
    identity read '' (the review of ee17f70, low 2)."""
    sb = _developer(tmp_path, "x = 1\n")
    for kw in ({"path": "m.py"}, {"path": "m.py", "text": "x", "nope": 1}):
        with pytest.raises(sandbox.ArgumentError) as exc:
            sb.call("code.write", **kw)
        assert sandbox._raise_site(exc.value).endswith(" in call")
        res = sandbox.dry_run(sb, "code.write", kw)
        assert not res.admitted and res.site.endswith(" in dry_run"), res
    res = sandbox.dry_run(sb, "code.source", {"path": "m.py", "nope": 1})
    assert not res.admitted and res.site.endswith(" in call"), res


def test_a_test_that_never_drains_its_calls_leaves_them(tmp_path):
    """The first half of a pair: this test leaves its entry in the log.
    The next test asserts that the log starts empty."""
    sb = _developer(tmp_path, "x = 1\n")
    sb.call("code.source", path="m.py")
    assert sandbox._CALL_LOG.get(id(sb.ctx))


def test_the_next_test_starts_with_an_empty_call_log():
    """A new `ctx` can take the id of a freed one and drain its calls, so
    `test_s9_tool_calls_are_recorded_as_evidence` failed after this file
    (the review of ee17f70, low 5). The conftest empties the log after each
    test. `--dist loadfile` keeps the pair above in order on one worker."""
    assert sandbox._CALL_LOG == {}


def test_a_crash_of_one_offer_keeps_the_records_of_the_others(tmp_path):
    """The add-after offer of a text that breaks the parser crashes its dry
    run. The other offers of the refusal keep their records (the review of
    fed7c58, low 9)."""
    sb = _developer(tmp_path, "def a(\n    x,\n):\n    return x\n")
    kwargs = {"path": "m.py", "start": 0, "end": 1, "text": "-" * 200000 + "1"}
    with pytest.raises(ValueError) as exc:
        sb.call("code.write", **kwargs)
    offers = list(sb.ctx.offers)
    recs = sandbox.follow(sb, "code.write", kwargs, exc.value, offers)
    assert len(recs) == len(offers) == 2
    assert [("MemoryError" in (r["second"] or "")) for r in recs] == [False, True]


def test_a_skip_after_a_new_finding_turns_the_report_red():
    """A test that calls `pytest.skip` after a refusal with a new finding
    reported SKIPPED (the review of fed7c58, low 9)."""
    from types import SimpleNamespace

    from tests.rota.conftest import unhide
    report = SimpleNamespace(when="call", outcome="skipped", longrepr=None)
    unhide(report, ["door code.write ..."])
    assert report.outcome == "failed"
    plain = SimpleNamespace(when="call", outcome="skipped", longrepr=None)
    unhide(plain, [])
    assert plain.outcome == "skipped"


def test_a_stored_path_refusal_quotes_the_stored_row(db):
    _a_criterion(db, _PRORATES)
    _a_stored_test(db)
    sb = _challenge_tester(db)
    _refused(sb, "tests.encode", id="t1", criterion_id="c1", path="q.py",
             body=_PRORATE + " # fixed")
    facts = sandbox.check_facts(sb, sb.ctx.facts)
    assert [(f["kind"], f["value"]) for f in facts] == [("row", "t1"), ("test_path", "p.py")]
    assert all(f["ok"] for f in facts), facts


def test_the_defines_twice_numbers_are_code_source_numbers(tmp_path):
    """Finding 5 of frame 144 pass 2, fixed in design 200 pass 2b. The door
    gave ast's numbers, which count from 1, so each number named the line
    below the def. The numbers and the facts now count from 0."""
    sb = _developer(tmp_path, "def f():\n    return 0\n")
    said, _ = _refused(sb, "code.write", path="m.py", start=2, end=2,
                       text="def f():\n    return 1\n")
    assert "defines f twice (lines 0 and 2)" in said
    facts = sandbox.check_facts(sb, sb.ctx.facts)
    assert [f["where"]["n"] for f in facts if f["kind"] == "line_text"] == [0, 2]
    assert all(f["ok"] for f in facts), facts


# Frame 144, pass 2 found that the refusal named text='''...''' for an op
# with no text argument (frame 137's sign). Frame 266, pass 2b names the
# missing bracket for this shape, so the test is green.
def test_the_parser_names_only_arguments_of_the_called_op():
    from rota.llm import toolproto
    raw = "TOOL: tests.triage(criterion_id='c1', verdict='encodable'\n"
    errors = [e for e in toolproto.extract(raw) if isinstance(e, toolproto.ToolError)]
    said = " ".join(e.reason for e in errors)
    assert "unterminated argument list" in said, said
    params = set(sandbox.inspect.signature(api.tests_triage).parameters)
    assert "text=" not in said or "text" in params, said


# -- the instrument -------------------------------------------------------------

def test_a_dry_run_puts_the_context_back(db):
    """An admitted offer stages a write inside the dry run. After it, `ctx`
    holds what it held, the lists keep their identity, and the call log and
    the database are unchanged."""
    _a_criterion(db, _PRORATES)
    _a_stored_test(db)
    sb = _challenge_tester(db)
    _, offers = _refused(sb, "tests.encode", id="t1", criterion_id="c1",
                         path="q.py", body=_PRORATE + " # fixed")
    sb.ctx.writes.append(("tests", "t_staged", {"path": "s.py"}))
    staged = sb.ctx.writes[0]
    writes, refusals = sb.ctx.writes, list(sb.ctx.refusals)
    log = list(sandbox._CALL_LOG.get(id(sb.ctx), []))
    changes = db.total_changes
    assert _admitted(sb, offers[0]) == (True, None)
    # The list and its element keep their identity (review point 4).
    assert sb.ctx.writes is writes and writes == [staged]
    assert sb.ctx.writes[0] is staged
    writes.clear()
    assert sb.ctx.refusals == refusals
    assert [o.op for o in sb.ctx.offers] == ["tests.encode"]
    assert sandbox._CALL_LOG.get(id(sb.ctx), []) == log
    assert db.total_changes == changes


def test_a_snapshot_refuses_an_attribute_it_cannot_restore(db):
    """A mutable type the snapshot does not know would be restored by a
    guess, so the dry run refuses to start (review point 4)."""
    sb = _challenge_tester(db)
    sb.ctx.odd = bytearray(b"x")
    with pytest.raises(TypeError, match="ctx.odd is a bytearray"):
        sandbox.dry_run(sb, "tests.encode", {})


class _Plain:
    """A type that keeps the default `==`, which compares identity."""

    def __init__(self, n):
        self.n = n


def test_a_dry_run_keeps_an_unchanged_object_of_an_unknown_type(db):
    """An element of a type with the default `==` kept its identity only by
    chance. Its attributes decide now (the review of 8726a13, low 5)."""
    _a_criterion(db, _PRORATES)
    _a_stored_test(db)
    sb = _challenge_tester(db)
    _, offers = _refused(sb, "tests.encode", id="t1", criterion_id="c1",
                         path="q.py", body=_PRORATE + " # fixed")
    plain, deeper = _Plain(1), {"inner": _Plain(2)}
    sb.ctx.held = held = [plain, deeper]
    assert _admitted(sb, offers[0]) == (True, None)
    assert sb.ctx.held is held and held[0] is plain and held[1] is deeper
    assert deeper["inner"].n == 2


def test_a_dry_run_restores_a_path_a_row_and_the_working_set(db):
    """A path and a sqlite3 row are values. The snapshot refused the path, and
    deepcopy cannot copy a row (the review of 8726a13, low 5). Frame 132's
    `ctx.working_set` comes back as the same object."""
    from pathlib import Path
    _a_criterion(db, _PRORATES)
    _a_stored_test(db)
    sb = _challenge_tester(db)
    _, offers = _refused(sb, "tests.encode", id="t1", criterion_id="c1",
                         path="q.py", body=_PRORATE + " # fixed")
    row = db.execute("SELECT 1 AS a").fetchone()
    sb.ctx.where, sb.ctx.row, sb.ctx.rows = Path("x.py"), row, [row]
    rows, ws = sb.ctx.rows, sb.ctx.working_set
    assert isinstance(ws, frozenset) and ws
    assert _admitted(sb, offers[0]) == (True, None)
    assert sb.ctx.where == Path("x.py") and sb.ctx.row is row
    assert sb.ctx.rows is rows and sb.ctx.rows[0] is row
    assert sb.ctx.working_set is ws


class _Slots:
    """A type with `__slots__` and the default `==`."""
    __slots__ = ("n",)

    def __init__(self, n):
        self.n = n


def test_a_dry_run_keeps_slots_and_copies_a_row_inside_a_tuple_or_object(db):
    """An unchanged object with `__slots__` lost its identity, and a row
    inside a namedtuple or an object made the dry run raise `TypeError:
    cannot pickle 'sqlite3.Row' object` (the review of fed7c58, low 8)."""
    import collections
    _a_criterion(db, _PRORATES)
    _a_stored_test(db)
    sb = _challenge_tester(db)
    _, offers = _refused(sb, "tests.encode", id="t1", criterion_id="c1",
                         path="q.py", body=_PRORATE + " # fixed")
    row = db.execute("SELECT 1 AS a").fetchone()
    pair = collections.namedtuple("Pair", "a b")(1, row)
    slots, boxed = _Slots(1), _Plain(row)
    sb.ctx.held = held = [slots, pair, boxed]
    assert _admitted(sb, offers[0]) == (True, None)
    assert held[0] is slots and held[1] is pair and held[2] is boxed
    assert held[1].b is row and held[2].n is row


def test_a_dry_run_does_not_send_a_commit():
    """git has no dry mode here, so an offered commit is not sent."""
    with pytest.raises(sandbox.DrySkipped):
        sandbox.dry_run(None, "code.commit", {})


def test_an_invented_text_is_not_sent():
    """A text the seat must write has no fresh value, so the offer is not
    sent. An invented id gets a fresh one."""
    assert sandbox._fill({"id": api.INVENT, "path": "p"}, 0) == {
        "id": "x_follow0_id", "path": "p"}
    with pytest.raises(sandbox.DrySkipped):
        sandbox._fill({"text": api.INVENT}, 0)
