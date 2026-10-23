"""
Frame 201, pass 3: the runner holds a Critic's first pass and asks the
seat's own question.

Probe (c) of `plans/frame201-interview.md` section 3 held the recorded pass
of `L1-CR-fail-names-its-criterion`. The reply quoted the criterion and the
seat's line, and asked "Does that line do what the criterion says, or the
opposite?". The seat failed the criterion in 3 of 3 runs. Every test calls
the real door through the sandbox.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from tests.rota.test_verdict_lines import _git

C1 = "c1"
C2 = "c2"
C1_TEXT = "deleting an account tombstones it and keeps its invoices"
C2_TEXT = "closing an account that does not exist returns False"
L_INVOICES = 'delete("invoices", account_id)'
L_ACCOUNT = 'delete("billing_accounts", account_id)'
L_LOAD = 'rec = load("billing_accounts", account_id)'
L_NONE = "return False"

# The recorded case's file before and after its batch commit.
_BEFORE = (
    "from ..store import load\n"
    "\n"
    "\n"
    "def close_account(account_id):\n"
    "    return True\n"
)
_AFTER = (
    "from ..store import load\n"
    "\n"
    "\n"
    "def close_account(account_id):\n"
    "    # Deletes the invoices too, which the criterion says must survive.\n"
    f"    {L_LOAD}\n"
    "    if rec is None:\n"
    f"        {L_NONE}\n"
    "    from ..store.records import delete\n"
    f"    {L_INVOICES}\n"
    f"    {L_ACCOUNT}\n"
    "    return True\n"
)


@pytest.fixture
def case(tmp_path):
    """The recorded case's batch: one criterion, and a diff that deletes the
    invoices the criterion keeps."""
    root = tmp_path / "root"
    (root / "src").mkdir(parents=True)
    _git(root, "init", "-q")
    (root / "src" / "accounts.py").write_bytes(_BEFORE.encode())
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    tree = tmp_path / "batch"
    _git(root, "worktree", "add", "-q", "-b", "batch/b1", str(tree))
    (tree / "src" / "accounts.py").write_bytes(_AFTER.encode())
    _git(tree, "commit", "-q", "-am", "delete an account")
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)",
                 (str(root),))
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1','deleting tombstones the account',"
                 "'in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','i1','delete an account')")
    conn.execute("INSERT INTO batches (id, item_id, status, worktree, "
                 "head_commit) VALUES ('b1', 'i1', 'running', ?, 'abc123')",
                 (str(tree),))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('b1', 'tk1')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "(?, 'tk1', ?)", (C1, C1_TEXT))
    conn.commit()
    return conn


def _two_criteria(conn):
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "(?, 'tk1', ?)", (C2, C2_TEXT))
    conn.commit()


def _critic(conn):
    return build("critic", conn, batch_id="b1", mode="review")


def _verdicts(sb) -> list:
    return [w for w in sb.ctx.writes if w[0] == "verdicts"]


def _held(sb, **kwargs) -> str:
    with pytest.raises(ValueError) as exc:
        sb.call("verdicts.emit", batch_id="b1", result="pass", **kwargs)
    assert not _verdicts(sb), "a held pass stages no verdict"
    return str(exc.value)


def test_the_recorded_turn_gets_the_hold(case):
    """The case's turn: the seat passes with the line that deletes the
    invoices. The reply quotes the criterion, the line and the question."""
    said = _held(_critic(case), lines={C1: L_INVOICES})
    assert said == (
        "your first pass of this session is held, and it has not landed. "
        f"Criterion c1: \"{C1_TEXT}\". Your line for c1: `{L_INVOICES}`. "
        "Does that line do what the criterion says, or the opposite? Then "
        "send verdicts.emit again with the verdict you now hold. If each "
        "line does what its criterion says, send the same pass again. If a "
        "line does the opposite, send a fail on its criterion. Call "
        "`verdicts.claim_encodes('<criterion id>', encodes=...)` first, as "
        "for any fail.")


def test_a_second_pass_lands(case):
    sb = _critic(case)
    _held(sb, lines={C1: L_INVOICES})
    out = sb.call("verdicts.emit", batch_id="b1", result="pass",
                  lines={C1: L_INVOICES})
    assert out == {"id": "critic:b1:abc123", "result": "pass"}
    assert len(_verdicts(sb)) == 1


def test_a_second_emit_that_fails_lands(case):
    sb = _critic(case)
    _held(sb, lines={C1: L_INVOICES})
    sb.call("verdicts.claim_encodes", criterion_id=C1, encodes=True)
    out = sb.call("verdicts.emit", batch_id="b1", result="fail",
                  failed_criterion=C1, reason="it deletes the invoices")
    assert out["result"] == "fail"
    (_, _, row), = _verdicts(sb)
    assert row["result"] == "fail" and row["failed_criterion"] == C1


def test_a_first_fail_lands_at_once(case):
    sb = _critic(case)
    sb.call("verdicts.claim_encodes", criterion_id=C1, encodes=True)
    out = sb.call("verdicts.emit", batch_id="b1", result="fail",
                  failed_criterion=C1, reason="it deletes the invoices")
    assert out["result"] == "fail"
    assert len(_verdicts(sb)) == 1
    assert not sb.ctx.pass_held


def test_two_criteria_are_quoted_by_id_in_order(case):
    _two_criteria(case)
    said = _held(_critic(case), lines={C2: L_NONE, C1: [L_INVOICES, L_ACCOUNT]})
    first = (f"Criterion c1: \"{C1_TEXT}\". Your lines for c1: "
             f"`{L_INVOICES}`, then `{L_ACCOUNT}`. Do those lines do what the "
             f"criterion says, or the opposite?")
    second = (f"Criterion c2: \"{C2_TEXT}\". Your line for c2: `{L_NONE}`. "
              f"Does that line do what the criterion says, or the opposite?")
    assert first in said and second in said
    assert said.index(first) < said.index(second)


def test_a_refused_pass_is_refused_before_the_hold(case):
    """The lines door speaks first, and the hold waits for a pass that would
    land."""
    sb = _critic(case)
    with pytest.raises(ValueError) as exc:
        sb.call("verdicts.emit", batch_id="b1", result="pass")
    assert "has no line" in str(exc.value)
    assert not sb.ctx.pass_held
    _held(sb, lines={C1: L_INVOICES})
