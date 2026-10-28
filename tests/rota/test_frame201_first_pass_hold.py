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
    from rota.roles import api
    with pytest.raises(api.PassHeld) as exc:
        sb.call("verdicts.emit", batch_id="b1", result="pass", **kwargs)
    assert not _verdicts(sb), "a held pass stages no verdict"
    return str(exc.value)


# F37: the one-line hold names the list form, because s238 of night 172 read
# the hold as "one line per criterion" and failed a right pass.
_MORE = ("If the criterion needs more than that line, send the pass again "
         "with the added lines that meet it together, as a list.")


def _asked(cid: str, text: str, line: str) -> str:
    return (f"before the pass lands, answer for {cid}. The criterion says: "
            f"\"{text}\". Your line holds '{line}'. Does that line do what "
            f"the criterion says, or the opposite? {_MORE} Say which in "
            f"your own words, and in the same reply send the same pass again "
            f"or your own fail on the criterion.")


def test_the_recorded_turn_gets_the_hold(case):
    """The case's turn: the seat passes with the line that deletes the
    invoices. The reply has probe (c)'s words, with the seat's own line
    (review 4, finding 3)."""
    said = _held(_critic(case), lines={C1: L_INVOICES})
    assert said == _asked(C1, C1_TEXT, L_INVOICES)


def test_the_runner_prints_the_hold_as_held(case):
    """Review 4, finding 2: the seat reads the hold under `HELD`, as probe
    (c) sent it, and not under `ERROR`."""
    from rota.core.predicates import Wake
    from rota.core.runner import run_session
    from rota.llm.llm import Pins, ScriptedBackend

    call = f"TOOL: verdicts.emit(batch_id='b1', result='pass', lines={{'c1': {L_INVOICES!r}}})"
    backend = ScriptedBackend([call, call, "Done."])
    run_session(case, Wake("critic", "tick:review", refs=("b1",)),
                backend=backend, pins=Pins(model="scripted"), batch_id="b1")
    prompt = backend.calls[1][1]
    assert f"HELD verdicts.emit: {_asked(C1, C1_TEXT, L_INVOICES)}" in prompt
    assert "ERROR verdicts.emit" not in prompt
    (row,) = case.execute("SELECT result FROM verdicts").fetchall()
    assert row["result"] == "pass"


def test_the_hold_offers_no_fail_route(case):
    """Night 161, s133: the hold asked about three lines and offered a claim
    and a fail on each. The seat took the fail on a right pass. The hold now
    keeps its question and names no call for the fail route (frame 201,
    sprint 18, pass 1)."""
    _two_criteria(case)
    sb = _critic(case)
    said = _held(sb, lines={C1: L_INVOICES, C2: L_NONE})
    assert "Does that line do what the criterion says, or the opposite?" in said
    # The reply names no call for the fail route. A criterion text may
    # hold the word "claim", so the check reads call text only (review 5).
    assert "claim_encodes" not in said and "verdicts.emit" not in said
    assert "result='fail'" not in said and "claim and fail" not in said
    assert not [o for o in sb.ctx.offers
                if o.op == "verdicts.claim_encodes"
                or o.args.get("result") == "fail" or o.then]
    [offer] = sb.ctx.offers
    assert offer.op == "verdicts.emit" and offer.args["result"] == "pass"


def test_a_held_pass_sent_again_lands_in_a_session(case):
    """Night 161, s226: the seat claimed, passed with a line of two parts,
    and read a hold that offered the fail. The seat now reads the pass route
    only, sends the same pass again, and the pass lands."""
    from rota.core.predicates import Wake
    from rota.core.runner import run_session
    from rota.llm.llm import Pins, ScriptedBackend

    two = {C1: f"{L_LOAD}\n    if rec is None:"}
    claim = f"TOOL: verdicts.claim_encodes(criterion_id='{C1}', encodes=True)"
    call = f"TOOL: verdicts.emit(batch_id='b1', result='pass', lines={two!r})"
    backend = ScriptedBackend([f"{claim}\n{call}", call, "Done."])
    run_session(case, Wake("critic", "tick:review", refs=("b1",)),
                backend=backend, pins=Pins(model="scripted"), batch_id="b1")
    prompt = backend.calls[1][1]
    assert "HELD verdicts.emit" in prompt
    assert "or the opposite?" in prompt
    assert "claim and fail" not in prompt
    (row,) = case.execute("SELECT result FROM verdicts").fetchall()
    assert row["result"] == "pass"


def test_a_second_pass_lands(case):
    sb = _critic(case)
    _held(sb, lines={C1: L_INVOICES})
    out = sb.call("verdicts.emit", batch_id="b1", result="pass",
                  lines={C1: L_INVOICES})
    assert out == {"id": "critic:b1:abc123", "result": "pass"}
    assert len(_verdicts(sb)) == 1


def test_a_moved_line_is_held_once_more(case):
    """Review 4, finding 4: after the hold, a pass that names another line
    is asked about that line. A third pass lands, whatever its line."""
    sb = _critic(case)
    _held(sb, lines={C1: L_INVOICES})
    said = _held(sb, lines={C1: L_ACCOUNT})
    assert said == _asked(C1, C1_TEXT, L_ACCOUNT)
    out = sb.call("verdicts.emit", batch_id="b1", result="pass",
                  lines={C1: L_LOAD})
    assert out["result"] == "pass"
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
    assert said == (
        "before the pass lands, answer for c1 and c2. "
        f"Criterion c1 says: \"{C1_TEXT}\". Your lines hold '{L_INVOICES}', "
        f"then '{L_ACCOUNT}'. Do those lines do what the criterion says, or "
        "the opposite? "
        f"Criterion c2 says: \"{C2_TEXT}\". Your line holds '{L_NONE}'. Does "
        f"that line do what the criterion says, or the opposite? {_MORE} Say "
        "which in your own words, and in the same reply send the same pass "
        "again or your own fail on the criterion.")


def test_the_one_line_hold_names_the_list_form(case):
    """F37, night 172, s238: the seat read the hold on one line as "copy one
    line per criterion" and sent a fail. The hold names the list form."""
    said = _held(_critic(case), lines={C1: L_INVOICES})
    assert _MORE in said


def test_the_hold_on_many_lines_keeps_its_question(case):
    """The list form is named on the one-line hold only."""
    said = _held(_critic(case), lines={C1: [L_INVOICES, L_ACCOUNT]})
    assert "Do those lines do what the criterion says, or the opposite?" in said
    assert _MORE not in said


@pytest.mark.parametrize("piece", ["review.md", "answer.md"])
def test_each_critic_prompt_names_the_list_form(piece):
    """F37: the interview of s238 found no prompt words on two lines that
    meet one criterion together. Each piece is read from its file."""
    from pathlib import Path

    import rota.roles
    path = Path(rota.roles.__file__).parent / "prompts" / "critic" / piece
    text = " ".join(path.read_text(encoding="utf-8").split())
    assert ("When several added lines meet it together, copy them as a list, "
            "each without the `+`.") in text


def test_a_two_line_list_sent_again_lands(case):
    """F37: a pass that names two lines for one criterion, as a list, is
    held once. The same pass sent again lands on the many-form path."""
    sb = _critic(case)
    said = _held(sb, lines={C1: [L_INVOICES, L_ACCOUNT]})
    assert f"Your lines hold '{L_INVOICES}', then '{L_ACCOUNT}'." in said
    out = sb.call("verdicts.emit", batch_id="b1", result="pass",
                  lines={C1: [L_INVOICES, L_ACCOUNT]})
    assert out["result"] == "pass"
    assert len(_verdicts(sb)) == 1


def test_a_second_hold_quotes_only_the_moved_criterion(case):
    _two_criteria(case)
    sb = _critic(case)
    _held(sb, lines={C1: L_INVOICES, C2: L_NONE})
    said = _held(sb, lines={C1: L_ACCOUNT, C2: L_NONE})
    assert said == _asked(C1, C1_TEXT, L_ACCOUNT)


def test_a_refused_pass_is_refused_before_the_hold(case):
    """The lines door speaks first, and the hold waits for a pass that would
    land."""
    sb = _critic(case)
    with pytest.raises(ValueError) as exc:
        sb.call("verdicts.emit", batch_id="b1", result="pass")
    assert "has no line" in str(exc.value)
    assert not sb.ctx.pass_held
    _held(sb, lines={C1: L_INVOICES})
