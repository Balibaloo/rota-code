"""
The mandatory fork: a judgment that cannot be skipped.

The principal's question set the experiment: "are we sure we framed the
escalation correctly to the roles?" We were not. The three-way routing had
been in the Tester's brief the whole time, as prose under a production
headline -- and headline-following is exactly what both models do, measured
across all three routing reds. So the judgment becomes an act: every
criterion gets a `tests.triage` verdict before it gets anything else, and an
encode is only legal for a criterion claimed `encodable`. Both doors are
completions.

The verdict collapsed to two-way 2026-09-01, on the fork's own measurement:
can/cannot arrives at 14B, the word/sentence/fact taxonomy is beyond every
local tier tested -- and the taxonomy only ever picked a desk, which the
`unresolved` ladder and `criterion_repair` pick mechanically. `cannot` goes
to the nearest desk and climbs; the three named kinds survive as sharper
claims for a model that genuinely holds the distinction.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.sandbox import ArgumentError, build


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, "
                 "approval_ver, version) VALUES ('i1','x','in_scope',"
                 "'approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('t1','i1','y')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('c1','t1','register(u) stores the email lowercased')")
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES "
                 "('b1','i1','running')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('b1','t1')")
    conn.commit()
    return conn


def _tester(db):
    return build("tester", db, batch_id="b1", mode="tests_missing")


def test_an_encode_with_no_branch_claim_is_refused(db):
    """The gate arms with the mode, not with usage: the very first encode of
    a session that never triaged anything is the case that matters most."""
    sb = _tester(db)
    with pytest.raises(ValueError, match="triage verdict"):
        sb.call("tests.encode", id="ts1", criterion_id="c1", path="t.py",
                body="assert True")


def test_a_claimed_criterion_encodes(db):
    sb = _tester(db)
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    out = sb.call("tests.encode", id="ts1", criterion_id="c1",
                  path="test_register.py",
                  body="def test_lowercase():\n"
                       "    from app import register, lookup\n"
                       "    register('u1','A@B.co')\n"
                       "    assert lookup('u1').email == 'a@b.co'")
    assert out["id"] == "ts1"


def test_each_cannot_verdict_names_its_owner(db):
    sb = _tester(db)
    owners = {
        "ambiguous_word": "terminologist",
        "no_machine_check": "vision_keeper",
        "outside_fact": "researcher",
    }
    for verdict, owner in owners.items():
        out = sb.call("tests.triage", criterion_id="c1", verdict=verdict)
        assert owner in out["next"], (verdict, out)


def test_a_routing_verdict_does_not_license_an_encode(db):
    """Claiming 'no_machine_check' and then encoding anyway is the exact
    both-doors-in-one-turn disease, refused."""
    sb = _tester(db)
    sb.call("tests.triage", criterion_id="c1", verdict="no_machine_check")
    with pytest.raises(ValueError, match="was triaged no_machine_check in this session"):
        sb.call("tests.encode", id="ts1", criterion_id="c1", path="t.py",
                body="assert True")


def test_the_verdict_vocabulary_is_closed(db):
    from rota.core.sandbox import ENUMS_BY_OP
    assert ENUMS_BY_OP[("tests", "triage")]["verdict"] == (
        "encodable", "cannot", "ambiguous_word", "no_machine_check",
        "outside_fact", "contradicts_request")
    sb = _tester(db)
    with pytest.raises(ArgumentError, match="not one of"):
        sb.call("tests.triage", criterion_id="c1", verdict="maybe")


def test_a_bare_cannot_is_a_complete_verdict_at_the_nearest_desk(db):
    """The collapse: no diagnosis owed. The next-step names the Terminologist
    and says the climb is mechanical, and the criterion is exactly as
    encode-blocked as under any sharp verdict."""
    sb = _tester(db)
    out = sb.call("tests.triage", criterion_id="c1", verdict="cannot")
    assert "terminologist" in out["next"], out
    assert "climbs" in out["next"], "the promise is the point: no diagnosis owed"
    with pytest.raises(ValueError, match="was triaged cannot in this session"):
        sb.call("tests.encode", id="ts1", criterion_id="c1", path="t.py",
                body="def test_x():\n    assert True")


def test_a_criterion_already_questioned_is_not_asked_again(db):
    """`tests_missing` fires per batch while any criterion lacks a test, so a
    routed criterion meets the mode again on the next wake. The triage's
    next-step deflects, and the send guard makes the deflection unskippable
    -- one open question per criterion, in both statuses the ladder owns."""
    for status in ("open", "unresolved"):
        db.execute("DELETE FROM messages")
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                   "verb, body_refs, seq, status) VALUES ('m1','th1','tester',"
                   "'terminologist','question','[\"c1\"]',1,?)", (status,))
        db.commit()
        sb = _tester(db)
        out = sb.call("tests.triage", criterion_id="c1", verdict="cannot")
        assert "already asked" in out["next"], (status, out)
        with pytest.raises(ValueError, match="already has your open question"):
            sb.call("msg.question_terminologist", refs=["c1"],
                    question="what does easy mean")


def test_an_answered_question_frees_the_criterion(db):
    """The guard reads the thread's state, not its history: an answered
    question is a finished conversation, and a new one is legal."""
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
               "verb, body_refs, seq, status) VALUES ('m1','th1','tester',"
               "'terminologist','question','[\"c1\"]',1,'answered')")
    db.commit()
    sb = _tester(db)
    out = sb.call("tests.triage", criterion_id="c1", verdict="cannot")
    assert "already asked" not in out["next"], out
    sb.call("msg.question_terminologist", refs=["c1"],
            question="the answer did not cover the export format")


def test_modes_without_the_fork_are_untouched(db):
    """The gate exists only where the mode offers the claim: the Tester's
    answer/repair flow re-encodes against new words without a triage door,
    and arming the gate there would refuse a flow that has no key."""
    from rota.roles import prompts

    sb = build("tester", db, batch_id="b1", mode="answer",
               allow=prompts.mode_tools("tester", "answer"))
    assert not hasattr(sb.ctx, "triaged"), \
        "no triage in the mode, no gate on the encode"

def test_cannot_climbs_once_the_terminologist_has_answered_twice(db):
    """
    Night 63 (2026-09-14): the Tester triaged `cannot`, was told to ask the
    Terminologist, was refused a third question because two were answered,
    triaged `cannot` again, three sessions. The rung is a fact of the message
    log, so the hint climbs with it.
    """
    import json
    refs = json.dumps(["c1"])
    for n in (1, 2):
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                   "body_refs, status, round_no, seq) VALUES (?, 'th1', 'tester', "
                   "'terminologist', 'question', ?, 'answered', 0, ?)",
                   (f"q{n}", refs, 2 * n - 1))
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                   "body_refs, status, round_no, seq, cause_id) VALUES (?, 'th1', "
                   "'terminologist', 'tester', 'answer', ?, 'answered', 0, ?, ?)",
                   (f"a{n}", refs, 2 * n, f"q{n}"))
    db.commit()
    out = _tester(db).call("tests.triage", criterion_id="c1", verdict="cannot")
    assert "vision_keeper" in out["next"] and "terminologist has answered 2" in out["next"]


def test_a_check_by_raise_is_a_check(db):
    """A try/except that re-raises as AssertionError, ended on `assert True`,
    checks something; the constant-assertion wall must not take it."""
    sb = _tester(db)
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    body = """from app import register

def test_register_accepts_lowercase():
    try:
        register('U@X')
    except TypeError as e:
        raise AssertionError(str(e)) from e
    assert True
"""
    try:
        sb.call("tests.encode", id="ts_raise", criterion_id="c1", path="tests/test_r.py", body=body)
    except ValueError as exc:
        assert "on a constant" not in str(exc), exc


# Frame 273, night 152: Tester s295 encoded tst_ver_opt_show_py with
# `or True` on every assert. The test could not fail, and the batch merged
# the parameter with none of its behaviour.
S295_BODY = """from click.decorators import version_option

def test_version_option_show_python_flag():
    # Test that show_python setting is off by default
    @version_option(show_python=False)
    def cmd1():
        pass

    # Test that show_python=True appends Python version
    @version_option(show_python=True)
    def cmd2():
        pass

    # Verify the decorator accepts show_python parameter
    assert hasattr(cmd1, '_show_python') or True  # decorator should handle this
    assert hasattr(cmd2, '_show_python') or True
"""


def _encode_or_true(db, body, tid="ts_or"):
    sb = _tester(db)
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    return sb.call("tests.encode", id=tid, criterion_id="c1",
                   path="tests/test_v.py", body=body)


def test_an_or_true_on_every_assert_is_refused(db):
    with pytest.raises(ValueError) as exc:
        _encode_or_true(db, S295_BODY)
    text = str(exc.value)
    assert "`assert hasattr(cmd1, '_show_python') or True`" in text, text
    assert "the `or True` makes the assertion true" in text, text
    assert "Remove the `or True`" in text, text
    assert "verdict='cannot'" in text, text


def _not_this_door(db, body):
    assert _encode_or_true(db, body) == {"id": "ts_or"}


def test_an_or_with_a_name_is_not_vacuous(db):
    # The name is bound, so the undefined-name wall stays out of the way.
    body = S295_BODY.replace("or True", "or flag").replace(
        "    # Verify the decorator", "    flag = False\n    # Verify the decorator")
    _not_this_door(db, body)


def test_an_and_true_is_not_refused_by_the_constant_door(db):
    _not_this_door(db, S295_BODY.replace("or True", "and True"))


def test_one_real_assert_beside_an_or_true_is_admitted(db):
    body = S295_BODY.replace(
        "assert hasattr(cmd2, '_show_python') or True",
        "assert hasattr(cmd2, '_show_python')")
    _not_this_door(db, body)


# Frame 277, night 153: two admitted asserts could never fail and held no
# constant. Tester s256 turn 4 encoded tst_ver_opt_show_py with an operand
# that reads the interpreter alone. It hid the red test until m132.
S256_BODY = """from click.decorators import version_option
from click.testing import CliRunner
import sys
import click

def test_custom_version_option():
    # Arrange
    def make_cli():
        @version_option(show_python=True)
        @click.command()
        def cli():
            pass
        return cli

    cli = make_cli()
    runner = CliRunner()

    # Act
    result = runner.invoke(cli, ["--version"])

    # Assert
    assert "Python" in result.output or sys.version_info[0] == 3
    assert "--python" not in result.output
"""

# Tester s198 turn 8 encoded tst_cr1_eof_default with two opposite operands.
# The batch merged it in e1caad9.
S198_BODY = """
import sys
from io import StringIO
from click.termui import confirm

def test_confirm_returns_default_when_stdin_closed_and_flag_true():
    \"\"\"When default_on_eof is True and stdin is closed, confirm() returns its own default argument instead of aborting.\"\"\"
    # Simulate closed stdin by providing an empty stream
    old_stdin = sys.stdin
    sys.stdin = StringIO('')
    try:
        result = confirm("Proceed?", default_on_eof=True)
        # The function should return a value (not raise UsageError)
        # If no default is provided, it should return None
        assert result is not None or result is None  # Should not raise an exception
    finally:
        sys.stdin = old_stdin
"""


def _refusal(db, body):
    with pytest.raises(ValueError) as exc:
        _encode_or_true(db, body)
    text = str(exc.value)
    assert "an assertion here cannot fail" in text, text
    assert "Remove the operand that cannot fail" in text, text
    assert "verdict='cannot'" in text, text
    return text


def test_an_or_on_the_interpreter_alone_is_refused(db):
    text = _refusal(db, S256_BODY)
    assert ("`assert \"Python\" in result.output or sys.version_info[0] == 3`"
            in text), text
    assert "`sys.version_info[0] == 3` reads only the Python interpreter" in text


def test_an_or_of_opposite_operands_is_refused(db):
    text = _refusal(db, S198_BODY)
    assert "`assert result is not None or result is None`" in text, text
    assert "`result is not None` and `result is None` are opposites" in text


@pytest.mark.parametrize("line", [
    "assert result == 'a' or result != 'a'",
    "assert 'a' in result or 'a' not in result",
    "assert result or not result",
])
def test_each_opposite_pair_is_refused(db, line):
    _refusal(db, S198_BODY.replace(
        "assert result is not None or result is None", line))


@pytest.mark.parametrize("line", [
    "assert \"Python\" in result.output or \"python\" in result.output",
    "assert result.exit_code == 0 or result.exception is None",
    "assert sys.version_info >= (3, 8) and \"Python\" in result.output",
    "assert \"Python\" in result.output or sys.version.split()[0] in result.output",
    "assert \"Python\" in result.output or \"Python\" in sys.stdout.getvalue()",
])
def test_an_or_that_reads_the_call_is_admitted(db, line):
    body = S256_BODY.replace(
        "assert \"Python\" in result.output or sys.version_info[0] == 3", line)
    _not_this_door(db, body)


# Review 1 of frame 277: the shapes it probed and found untested. Each name
# is bound, so the undefined-name wall stays out of the way.
_S256_LINE = "assert \"Python\" in result.output or sys.version_info[0] == 3"
_BINDINGS = ("    x = result.exit_code\n    a = result.exception\n"
             "    b = result.return_value\n    out = result.output\n"
             "    err = result.stderr_bytes\n    path = result.output\n"
             "    ok = result.exit_code == 0\n")


def _s256_with(line, binds=_BINDINGS, imports=None):
    body = S256_BODY.replace("    # Assert\n", binds + "    # Assert\n")
    if imports is not None:
        body = body.replace("import sys\n", imports)
    return body.replace(_S256_LINE, line)


@pytest.mark.parametrize("line,binds,imports", [
    ("assert x == 1 or x == 2", _BINDINGS, None),
    ("assert a is None or b is None", _BINDINGS, None),
    ("assert out or not err", _BINDINGS, None),
    (_S256_LINE, _BINDINGS + "    sys = result\n", None),
    ("assert \"Python\" in result.output or version_info[0] == 3", _BINDINGS,
     "from sys import version_info\n"),
    ("assert ok or platform.python_version()", _BINDINGS,
     "import sys\nfrom click import utils as platform\n"),
    ("assert len(sys.argv) or ok", _BINDINGS, None),
    ("assert \"Python\" in result.output or sys.version in open(\"out.log\").read()",
     _BINDINGS, None),
])
def test_an_or_the_review_probed_is_admitted(db, line, binds, imports):
    _not_this_door(db, _s256_with(line, binds, imports))


def test_a_false_interpreter_operand_is_admitted(db):
    # The operand is false on the host that runs the tests, so the
    # assertion reads `path` alone and can fail.
    import sys
    _not_this_door(db, _s256_with(
        f"assert sys.platform != {sys.platform!r} or path.endswith(\"/\")"))


def test_a_true_interpreter_operand_is_refused(db):
    import sys
    line = f"assert sys.platform == {sys.platform!r} or path.endswith(\"/\")"
    text = _refusal(db, _s256_with(line))
    assert f"`{line}`" in text, text
    assert f"`sys.platform == {sys.platform!r}` reads only" in text, text


def test_an_interpreter_operand_that_raises_is_admitted(db):
    _not_this_door(db, _s256_with(
        "assert sys.version_info[9] == 3 or path.endswith(\"/\")"))


def test_the_operand_is_quoted_as_the_seat_wrote_it(db):
    # `ast.unparse` would turn the double quotes into single quotes.
    text = _refusal(db, _s256_with("assert \"a\" in out or \"a\" not in out"))
    assert "`\"a\" in out` and `\"a\" not in out` are opposites" in text, text


# Review 2 of frame 277: the door reads the interpreter and does not
# compute, so an operand with arithmetic or a call it does not know is
# admitted and never evaluated.
def test_an_operand_with_arithmetic_is_admitted_at_once(db):
    import time
    body = _s256_with("assert sys.hexversion ** sys.hexversion or x")
    start = time.perf_counter()
    _not_this_door(db, body)
    assert time.perf_counter() - start < 5.0


@pytest.mark.parametrize("line", [
    "assert '{0.__globals__[os]}'.format(platform.system) or x",
    "assert '{0.__globals__[os]}'.format(platform.python_version) or x",
    "assert platform.release() == \"10\" or x",
    "assert sys.version.split()[0] or x",
])
def test_an_operand_the_door_does_not_read_is_admitted(db, line):
    _not_this_door(db, _s256_with(line, imports="import sys\nimport platform\n"))


def test_a_fixed_platform_call_is_refused(db):
    line = "assert platform.python_version_tuple()[0] == \"3\" or x"
    text = _refusal(db, _s256_with(line, imports="import sys\nimport platform\n"))
    assert "`platform.python_version_tuple()[0] == \"3\"` reads only" in text


def test_an_answer_to_a_challenge_quotes_the_criterion_or_is_the_fix(db):
    """
    Night 80 (2026-09-15): the Tester's answer to the Developer's challenge said
    the developer is right and kept the test; the Developer bent the code to it.
    An answer that keeps the test carries the criterion's words; a concession is
    tests.encode (Roman)."""
    from rota.roles import prompts
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES ('ts1','b1','c1','tests/test_r.py','def test_x(): assert 1')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, body_refs, status, round_no, seq) "
               "VALUES ('m1','th1','developer','tester','challenge','[\"c1\", \"ts1\"]','open',0,1)")
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="normal",
               allow=prompts.mode_tools("tester", "challenge"))
    sb.ctx.trigger = "m1"
    with pytest.raises(ValueError, match="carries the criterion's words"):
        sb.call("msg.answer_developer", refs=["c1", "ts1"], round_no=0,
                quotes="the developer is right, the test asserts more than the criterion asks")
    # Frame 333: each quote is a span of a row of refs, so prose around the
    # span is refused too.
    with pytest.raises(ValueError, match="carries the criterion's words"):
        sb.call("msg.answer_developer", refs=["c1", "ts1"], round_no=0,
                quotes="the assertion comes from: stores the email lowercased")
    out = sb.call("msg.answer_developer", refs=["c1", "ts1"], round_no=0,
                  quotes="stores the email lowercased")
    assert out["to"] == "developer"


# ---------------------------------------------------------------------------
# Frame 81: the Tester sends a criterion that contradicts the request back.
# ---------------------------------------------------------------------------

ASK = ("Add an echo_json(obj, indent=2) helper next to echo that prints an "
       "object as JSON.")
C1 = ("echo_json returns a string containing the JSON representation of obj, "
      "formatted with indent=2.")
C2 = "echo_json prints obj as JSON with two spaces of indent."


@pytest.fixture
def night91(db):
    """
    Night 91's words (2026-09-24) on c1, its ticket and its item, one
    statement behind the item, and a second criterion that agrees with the
    request. A separate fixture keeps the tests above on their own words.
    """
    db.execute("UPDATE items SET text = ? WHERE id = 'i1'", (ASK,))
    db.execute("UPDATE tickets SET text = ? WHERE id = 't1'", (ASK,))
    db.execute("UPDATE criteria SET text = ? WHERE id = 'c1'", (C1,))
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c2','t1',?)", (C2,))
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e1','principal',?,1)", (ASK,))
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
               "text, status) VALUES ('s1','e1',0,?,?,'ratified')",
               (len(ASK), ASK))
    db.execute("INSERT INTO refs (src_table, src_id, kind, target) VALUES "
               "('items','i1','statement','s1')")
    db.execute("UPDATE batches SET head_commit = 'deadbeef' WHERE id = 'b1'")
    db.commit()
    return db


def _contradicts(sb, criterion_id="c1", request_span="prints an object as JSON",
                 criterion_span="returns a string"):
    return sb.call("tests.triage", criterion_id=criterion_id,
                   verdict="contradicts_request", request_span=request_span,
                   criterion_span=criterion_span)


def _tagged(sb):
    return [m for m in sb.ctx.outbound if m.get("route") == "triage"]


def test_contradicts_request_stages_an_unresolved_question(night91):
    """The verdict is the route: one tagged question to the Terminologist,
    born unresolved, with a note that quotes both sides."""
    sb = _tester(night91)
    out = _contradicts(sb)
    assert "routed" in out["next"] and "Terminologist" in out["next"], out
    [m] = _tagged(sb)
    assert m["to_role"] == "terminologist" and m["verb"] == "question"
    assert m["status"] == "unresolved"
    assert m["body_refs"] == ["c1", "t1"]
    note = m["unresolved_note"]
    assert note.startswith("s1 says"), note
    assert "prints an object as JSON" in note and "returns a string" in note
    assert out["next"].endswith("End the session"), out
    with pytest.raises(ValueError,
                       match="c1 was triaged contradicts_request in this session"):
        sb.call("tests.encode", id="ts1", criterion_id="c1", path="t.py",
                body="def test_x():\n    assert True")


def test_each_span_is_checked_against_its_source(night91):
    sb = _tester(night91)
    with pytest.raises(ValueError, match="request_span is not in the statements"):
        _contradicts(sb, request_span="returns nothing")
    with pytest.raises(ValueError, match="criterion_span is not in the words of c1"):
        _contradicts(sb, criterion_span="prints the object")
    assert not _tagged(sb), "a refused verdict stages nothing"
    # A span on another verdict is ignored: qwen3:8b fills both on every call.
    out = sb.call("tests.triage", criterion_id="c2", verdict="encodable",
                  request_span="prints", criterion_span="prints obj as JSON")
    assert out["verdict"] == "encodable" and out["next"].startswith("encode it")
    assert not _tagged(sb), "a span on encodable stages nothing"
    _contradicts(sb, request_span="'Prints an object as JSON.'",
                 criterion_span='"returns a string."')
    assert len(_tagged(sb)) == 1


def test_the_committed_question_wakes_the_repair_and_not_the_ladder(night91):
    """Every reader on the new row, after the pipeline commits it."""
    from rota.core import db as db_mod
    from rota.core import runner
    from rota.core.predicates import criterion_repair, tests_missing, unresolved
    from rota.core.scheduler import Wake

    sb = _tester(night91)
    _contradicts(sb)
    wake = Wake("tester", "tick:tests_missing", refs=("b1",))
    db_mod.session_commit(night91, db_mod.SessionResult(
        session_id="se1", role="tester", wake_kind="tick:tests_missing",
        messages=runner._messages_from(sb, wake, "se1")))
    row = night91.execute("SELECT status, unresolved_note FROM messages "
                          "WHERE from_role = 'tester'").fetchone()
    assert row["status"] == "unresolved"
    repair = criterion_repair(night91)
    assert [w.role for w in repair] == ["terminologist"]
    assert repair[0].detail == row["unresolved_note"]
    missing = tests_missing(night91)
    assert [w.detail for w in missing] == ["without a test: c2"], missing
    assert unresolved(night91) == []


def test_one_row_per_criterion_and_later_questions_stand_beside_it(night91):
    sb = _tester(night91)
    _contradicts(sb)
    out = _contradicts(sb)
    assert "already asked" in out["next"], out
    assert len(_tagged(sb)) == 1
    sb.call("msg.question_vision_keeper", refs=["c2"],
            question="what does indent mean here")
    assert len(_tagged(sb)) == 1, "the later question removed the tagged row"
    assert any(m["to_role"] == "vision_keeper" for m in sb.ctx.outbound)


def test_the_verdict_withdraws_a_test_staged_for_the_criterion(night91):
    """Staged by hand: the wall at encodable refuses c1, so no encode of c1
    can reach the staged set through the op."""
    sb = _tester(night91)
    sb.ctx.writes.append(("tests", "ts_c1", {
        "batch_id": "b1", "criterion_id": "c1", "path": "tests/test_e.py",
        "body": "def test_e():\n    assert True"}))
    out = _contradicts(sb)
    assert out["withdrawn"] == ["ts_c1"], out
    assert "ts_c1" in out["note"]
    assert not [w for w in sb.ctx.writes if w[0] == "tests"]


def test_encodable_meets_the_wall_on_the_prints_returns_pair(night91):
    sb = _tester(night91)
    with pytest.raises(ValueError, match="contradicts_request") as exc:
        sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    assert "'returns'" in str(exc.value) and "'prints'" in str(exc.value)
    assert ("Send tests.triage(criterion_id='c1', verdict='contradicts_request', "
            "request_span='prints', criterion_span='returns')") in str(exc.value)
    out = sb.call("tests.triage", criterion_id="c2", verdict="encodable")
    assert out["verdict"] == "encodable"
    # The words the refusal quotes pass the span check as they stand.
    _contradicts(sb, request_span="prints", criterion_span="returns")
    assert len(_tagged(sb)) == 1


def test_a_later_question_on_the_routed_criterion_is_refused(night91):
    """The diff review's probe: a second row for c1 landed open and woke a
    second Terminologist session."""
    sb = _tester(night91)
    _contradicts(sb)
    [m] = _tagged(sb)
    with pytest.raises(ValueError, match=(
            f"already asked -- {m['id']} carries c1 to the Terminologist. "
            f"Encode the others or end the session")):
        sb.call("msg.question_terminologist", refs=["c1"],
                question="does echo_json print or return")
    out = sb.call("msg.question_terminologist", refs=["c2"],
                  question="what does indent mean here")
    assert out["to"] == "terminologist"
    assert len(_tagged(sb)) == 1


ECHO_JSON = ("Add an echo_json(obj, indent=2) helper next to echo that prints "
             "an object as JSON.")


def _contradicting(db):
    """The fixture of L1-TS-a-criterion-that-contradicts-the-request-goes-back:
    the request says prints and the criterion says returns."""
    db.execute("UPDATE items SET text = ? WHERE id = 'i1'", (ECHO_JSON,))
    db.execute("UPDATE tickets SET text = ? WHERE id = 't1'", (ECHO_JSON,))
    db.execute("UPDATE criteria SET text = ? WHERE id = 'c1'",
               ("echo_json returns a string containing the JSON "
                "representation of obj, formatted with indent=2.",))
    db.commit()


def test_an_encode_before_triage_offers_the_verdict_triage_accepts(db):
    """Frame 290: the encode door offered `encodable`, and the triage door
    refused it for a criterion that contradicts the request (gate re-record
    at 7471569c). The offer must name the call that lands."""
    _contradicting(db)
    sb = _tester(db)
    with pytest.raises(ValueError) as err:
        sb.call("tests.encode", id="ts1", criterion_id="c1", path="t.py",
                body="def test_x():\n    assert True")
    text = str(err.value)
    assert "verdict='contradicts_request'" in text
    assert "request_span='prints'" in text
    assert "criterion_span='returns'" in text
    assert "verdict='encodable'" not in text
    out = sb.call("tests.triage", criterion_id="c1",
                  verdict="contradicts_request", request_span="prints",
                  criterion_span="returns")
    assert out["verdict"] == "contradicts_request"


def test_an_encode_before_triage_offers_encodable_when_nothing_contradicts(db):
    sb = _tester(db)
    with pytest.raises(ValueError) as err:
        sb.call("tests.encode", id="ts1", criterion_id="c1", path="t.py",
                body="def test_x():\n    assert True")
    assert "verdict='encodable'" in str(err.value)
    assert "contradicts_request" not in str(err.value)
