"""
Frame 343: the test-file door offers a new file beside a project test file.

Night 170 s196, turn 1: the Tester sent `tests.encode` with
`path='tests/test_formatting.py'` on b_3. `harness.inherit` had made that
file a row of the batch, so the clash door refused, with no call to send.
Sixteen encodes met the same text, and the walk stopped.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from rota.core.harness import inherited_id
from rota.core.sandbox import build
from rota.core import sandbox
from rota.roles.api import INVENT, _beside_project_test
from tests.rota.test_t0_sandbox import (  # noqa: F401
    _PRORATE, _challenge_wake, db)

_CRIT = "c_1_format_filename_example"
_PROJECT = "tests/test_formatting.py"


def _batch_with_a_project_test(db):
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i1','export for finance','in_scope',"
               "'approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) "
               "VALUES ('tk1','i1','export for finance')")
    for cid, text in ((_CRIT, "prorating a mid-month upgrade charges the "
                       "unused remainder"),
                      ("c2", "a downgrade takes effect next period")):
        db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?, 'tk1', ?)",
                   (cid, text))
    db.execute("INSERT INTO batches (id, item_id, status) "
               "VALUES ('b1','i1','running')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) "
               "VALUES ('b1','tk1')")
    # The row `harness.inherit` writes: the derived id, and no criterion.
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES (?, 'b1', NULL, ?, 'def test_old():\n    pass\n')",
               (inherited_id(_PROJECT), _PROJECT))
    db.commit()


def _tester(db):
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    sb.call("tests.triage", criterion_id=_CRIT, verdict="encodable")
    return sb


def test_an_encode_at_a_project_test_file_is_offered_a_file_beside_it(db):
    """The red case: the door names one new file, and the call lands."""
    _batch_with_a_project_test(db)
    sb = _tester(db)
    with pytest.raises(ValueError) as exc:
        sb.call("tests.encode", id="t_c1", criterion_id=_CRIT, path=_PROJECT,
                body=_PRORATE, batch_id="b1")
    said = str(exc.value)
    beside = "tests/test_formatting_c_1_format_filename_example.py"
    assert "holds the project's own tests" in said, said
    assert f"path={beside!r}" in said, said
    [offer] = [o for o in sb.ctx.offers if o.op == "tests.encode"]
    assert offer.args == {"id": "t_c1", "criterion_id": _CRIT, "path": beside,
                          "body": _PRORATE, "batch_id": "b1"}

    out = sb.call("tests.encode", **offer.args)
    assert out == {"id": "t_c1"}, out
    staged = [w for w in sb.ctx.writes if w[0] == "tests"]
    assert [(w[1], w[2]["path"]) for w in staged] == [("t_c1", beside)]


def test_a_clash_with_a_testers_test_keeps_the_text_of_today(db):
    """A file that a Tester's test holds is not the project's. The door
    keeps the text of walk twelve and offers no file."""
    _batch_with_a_project_test(db)
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('t_c2', 'b1', 'c2', 'tests/test_down.py', ?)", (_PRORATE,))
    db.commit()
    sb = _tester(db)
    with pytest.raises(ValueError) as exc:
        sb.call("tests.encode", id="t_c1", criterion_id=_CRIT,
                path="tests/test_down.py", body=_PRORATE, batch_id="b1")
    said = str(exc.value)
    assert ("tests/test_down.py is already t_c2's file; two tests in one "
            "file overwrite each other on disk") in said, said
    assert "project's own tests" not in said
    assert not [o for o in sb.ctx.offers if o.op == "tests.encode"]


def test_the_seats_own_row_does_not_take_the_path_beside(db):
    """Pass 1b: a row of the seat's own id at the path beside is the row
    the same id replaces, so the path stays free for that id. A row of
    another id takes the path, and a number follows the name."""
    from rota.roles.api import _beside_project_test

    _batch_with_a_project_test(db)
    beside = "tests/test_formatting_c_1_format_filename_example.py"
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('t_c1', 'b1', ?, ?, ?)", (_CRIT, beside, _PRORATE))
    db.commit()
    sb = _tester(db)
    assert _beside_project_test(sb.ctx, _PROJECT, _CRIT, "b1", "t_c1") == beside
    assert _beside_project_test(sb.ctx, _PROJECT, _CRIT, "b1", "t_other") == (
        "tests/test_formatting_c_1_format_filename_example_2.py")


_PID = inherited_id(_PROJECT)


def _fix_project_row(db, criterion_id=_CRIT):
    """A landed challenge fix gives the project row a criterion."""
    db.execute("UPDATE tests SET criterion_id = ? WHERE id = ?",
               (criterion_id, _PID))
    db.commit()


def test_a_challenge_of_a_project_row_offers_its_own_id_at_its_file(db):
    """Review of pass 1b, finding 1: a wake that challenges the project row
    sent a new id beside it, so the challenged test stayed and ran beside the
    fix, as in frame 123. The offer is the project id at its own file."""
    _batch_with_a_project_test(db)
    sb = _challenge_wake(db, [_PID])
    with pytest.raises(ValueError) as exc:
        sb.call("tests.encode", id="t_fix", criterion_id=_CRIT, path=_PROJECT,
                body=_PRORATE, batch_id="b1")
    assert f"this wake challenges {_PID}" in str(exc.value), exc.value
    [offer] = [o for o in sb.ctx.offers if o.op == "tests.encode"]
    assert (offer.args["id"], offer.args["path"]) == (_PID, _PROJECT)
    assert sb.call("tests.encode", **offer.args) == {"id": _PID}


def test_a_new_id_for_the_criterion_of_a_fixed_project_row_is_the_one_test_note(db):
    """Finding 2: outside a challenge, the project row holds the criterion
    after a fix. A second test of that criterion gets the one-test note."""
    _batch_with_a_project_test(db)
    _fix_project_row(db)
    sb = _tester(db)
    out = sb.call("tests.encode", id="t_new", criterion_id=_CRIT,
                  path=_PROJECT, body=_PRORATE, batch_id="b1")
    assert out.get("unchanged") and out["id"] == _PID, out
    assert "one criterion takes one" in out["note"]
    assert not [w for w in sb.ctx.writes if w[0] == "tests"]


def test_a_replace_at_a_file_shared_with_a_project_row_is_not_sent_beside(db):
    """Finding 3: a Tester row and a project row at one file. The beside
    offer met the stored-path door, which sent the call back, for good."""
    _batch_with_a_project_test(db)
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('t1', 'b1', ?, ?, ?)", (_CRIT, _PROJECT, _PRORATE))
    db.commit()
    sb = _tester(db)
    with pytest.raises(ValueError) as exc:
        sb.call("tests.encode", id="t1", criterion_id=_CRIT, path=_PROJECT,
                body=_PRORATE + " # fixed", batch_id="b1")
    assert "two tests in one file overwrite each other" in str(exc.value), exc.value
    assert not [o for o in sb.ctx.offers if o.op == "tests.encode"]


def test_the_missing_import_offer_for_a_project_id_lands_in_one_hop(db):
    """Finding 4: the missing-import door runs before the project-id door.
    It kept the project id, and the next call met that door."""
    _batch_with_a_project_test(db)
    sb = _tester(db)
    body = "def test_it():\n    assert json.loads('[1]') == [1]\n"
    with pytest.raises(ValueError):
        sb.call("tests.encode", id=_PID, criterion_id=_CRIT, path=_PROJECT,
                body=body, batch_id="b1")
    [offer] = [o for o in sb.ctx.offers if o.op == "tests.encode"]
    assert offer.args["id"] is INVENT
    assert offer.args["path"] == "tests/test_formatting_c_1_format_filename_example.py"
    assert offer.args["body"] == "import json\n" + body
    res = sandbox.dry_run(sb, offer.op, offer.args, offer.then)
    assert (res.admitted, res.refusal) == (True, None)


def test_the_criterion_part_of_the_beside_name_is_at_most_40_characters(db):
    """Finding 5: a long criterion id in a deep folder can pass the Windows
    path limit of 260 characters."""
    _batch_with_a_project_test(db)
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    got = _beside_project_test(sb.ctx, _PROJECT, "c_1_" + "x" * 100, "b1")
    assert got == "tests/test_formatting_c_1_" + "x" * 36 + ".py", got


def test_the_tests_missing_brief_sends_a_project_file_beside_it():
    """Frame 343, reach R3: the touch line of the brief names project test
    files, so the brief says where the new test goes."""
    text = (Path(__file__).resolve().parents[2] / "rota" / "roles" / "prompts"
            / "tester" / "tests_missing.md").read_text(encoding="utf-8")
    flat = " ".join(text.split())
    assert ("A path under `touch` that already holds the project's tests is "
            "not yours. Put your test in a new file beside it.") in flat
