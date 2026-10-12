"""
Frame 204, pass 2: the conflict hold on the merge, and the doors in front of it.

Night 143 (2026-10-12) wrote 37 `conflict` rows, and 0 of 37 was a
disagreement. 34 came from reconcile sessions that quoted the account row
they were about as one side. The door now refuses a side that restates the
row it is about, and a conflict about a decision alone.

`lifecycle.mergeable` holds a batch while a seat still owes an answer that
reaches the batch's rows (frame 204's design, section 4). No test here calls
a model.
"""
from __future__ import annotations

import json

import pytest

from rota.core import lifecycle
from rota.core.db import init_db
from rota.core.predicates import Wake
from rota.core.sandbox import build


# ---------------------------------------------------------------------------
# The merge hold, section 4.
# ---------------------------------------------------------------------------

@pytest.fixture
def ready(tmp_path):
    """A batch that merges today: a test per criterion, green, and a pass."""
    conn = init_db(tmp_path / "r.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1','closing keeps invoices','in_scope',"
                 "'approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','i1','close an account')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('c1','tk1','closing an account leaves its invoices')")
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) "
                 "VALUES ('b1','i1','running','abc')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('b1','tk1')")
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                 "VALUES ('tst1','b1','c1','tests/test_close.py','assert 1')")
    conn.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
                 "result) VALUES ('r1','b1','tst1','abc','pass')")
    conn.execute("INSERT INTO verdicts (id, batch_id, commit_sha, result) "
                 "VALUES ('critic:b1:abc','b1','abc','pass')")
    conn.commit()
    assert lifecycle.mergeable(conn, "b1") is None
    return conn


def _msg(conn, mid, frm, to, verb, refs, status="open", seq=1, cause=None,
         thread=None, note=None):
    conn.execute(
        "INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
        "verb, body_refs, seq, status, unresolved_note) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (mid, cause, thread or mid, frm, to, verb, json.dumps(refs), seq,
         status, note))
    conn.commit()


def _note(conn, lid, about, kind, author="developer", table="tests"):
    conn.execute("INSERT INTO ledger (id, about_ref, about_table, "
                 "default_taken, kind, status, author) VALUES "
                 "(?,?,?,?,?,'open',?)",
                 (lid, about, table, "the test and its criterion disagree "
                  "on what closing keeps", kind, author))
    conn.commit()


def test_an_open_challenge_holds_the_merge(ready):
    _msg(ready, "m1", "developer", "tester", "challenge", ["c1", "tst1"])
    assert lifecycle.mergeable(ready, "b1") == "waiting on tester: m1"


def test_an_open_question_holds_the_merge(ready):
    _msg(ready, "m1", "developer", "terminologist", "question", ["c1"])
    assert lifecycle.mergeable(ready, "b1") == "waiting on terminologist: m1"


def test_an_unresolved_question_with_a_next_rung_holds_the_merge(ready):
    """The `unresolved` predicate names the Architect as the next rung, so
    a seat still owes the question a reply."""
    _msg(ready, "m1", "developer", "terminologist", "question", ["c1"],
         status="unresolved", note="the answer did not say which sense")
    assert lifecycle.mergeable(ready, "b1") == "waiting on architect: m1"


def test_a_routed_conflict_row_holds_the_merge_and_is_named(ready):
    """The seat logged the conflict and asked the owner through an edge."""
    _note(ready, "l_c", "tst1", "conflict")
    _msg(ready, "m1", "developer", "tester", "challenge", ["tst1"])
    assert lifecycle.mergeable(ready, "b1") == "waiting on tester: m1, l_c"


def test_a_path_note_reaches_its_batch_through_its_session(ready):
    """Night 138: two rows under `tests/test_utils/` reached no item. The
    session that wrote the row names the batch (design, section 4, step 2)."""
    path = "tests/test_utils/helpers.py"
    ready.execute("INSERT INTO sessions (id, role, seq, committed, wake_kind, "
                  "wake_refs) VALUES ('s1','developer',1,1,'tick:tests_failing',"
                  "'[\"b1\"]')")
    ready.execute("INSERT INTO receipts (session_id, table_name, row_id, "
                  "new_version) VALUES ('s1','ledger','l_p',1)")
    _note(ready, "l_p", path, "scope", table=path)
    _msg(ready, "m1", "developer", "vision_keeper", "question", [path])
    assert lifecycle.mergeable(ready, "b1") == "waiting on vision_keeper: m1, l_p"


def test_a_path_note_of_another_batch_holds_nothing(ready):
    path = "tests/test_utils/helpers.py"
    ready.execute("INSERT INTO sessions (id, role, seq, committed, wake_kind, "
                  "wake_refs) VALUES ('s1','developer',1,1,'tick:tests_failing',"
                  "'[\"b9\"]')")
    ready.execute("INSERT INTO receipts (session_id, table_name, row_id, "
                  "new_version) VALUES ('s1','ledger','l_p',1)")
    _note(ready, "l_p", path, "scope", table=path)
    _msg(ready, "m1", "developer", "vision_keeper", "question", [path])
    assert lifecycle.mergeable(ready, "b1") is None


def test_a_quarantined_question_holds_nothing(ready):
    """Review finding 2: nothing moves a message out of `quarantined`, so a
    hold on it would never end. The quarantine is the release."""
    _msg(ready, "m1", "developer", "terminologist", "question", ["c1"],
         status="quarantined")
    assert lifecycle.mergeable(ready, "b1") is None


def test_a_question_the_triage_made_unresolved_holds_nothing(ready):
    """`schema.sql`: a Tester's triage can create a question unresolved, and
    nobody owes that question a reply."""
    _msg(ready, "m1", "tester", "terminologist", "question", ["c1", "tk1"],
         status="unresolved", note="the item says one thing and c1 another")
    assert lifecycle.mergeable(ready, "b1") is None


def test_a_conflict_row_on_a_pair_with_no_edge_holds_nothing(ready):
    """Review finding 1: no seat is woken by a ledger row, so a hold on it
    waits on a page. Under `auto` the row parks with the others."""
    _note(ready, "l_c", "tst1", "conflict", author="architect")
    assert lifecycle.mergeable(ready, "b1") is None


def test_an_answer_releases_the_merge(ready):
    _msg(ready, "m1", "developer", "tester", "challenge", ["c1", "tst1"])
    assert lifecycle.mergeable(ready, "b1") == "waiting on tester: m1"
    ready.execute("UPDATE messages SET status = 'answered' WHERE id = 'm1'")
    _msg(ready, "m2", "tester", "developer", "answer", ["c1", "tst1"],
         cause="m1", thread="m1", seq=2)
    assert lifecycle.mergeable(ready, "b1") is None


def test_the_review_gate_still_reads_after_the_hold(ready):
    from rota.core import config

    config.set(ready, "merge_gate", "review")
    assert lifecycle.mergeable(ready, "b1") == "waiting on the principal's review"


# ---------------------------------------------------------------------------
# The wait: a seat that challenged or escalated is not offered new work.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("verb,to", [("challenge", "tester"),
                                     ("escalate", "architect")])
def test_a_role_that_challenged_or_escalated_waits(ready, verb, to):
    from rota.core.scheduler import waiting_filter

    work = Wake("developer", "tick:tests_failing", refs=("b1",))
    tip = Wake("developer", "message", refs=("m9",))
    assert waiting_filter(ready, [work, tip]) == [work, tip]
    _msg(ready, "m1", "developer", to, verb, ["c1", "tst1"])
    assert waiting_filter(ready, [work, tip]) == [tip]


# ---------------------------------------------------------------------------
# The `ledger.log` door: night 143's misplaced conflicts.
# ---------------------------------------------------------------------------

ACCOUNT = ("Users define commands and options using decorators in Python "
           "functions, which Click then uses to parse and execute inputs.")


@pytest.fixture
def account(tmp_path):
    conn = init_db(tmp_path / "a.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('defines_commands',?,'in_scope',"
                 "'approved',1,1)", (ACCOUNT,))
    conn.execute("INSERT OR IGNORE INTO code_index (grain, grain_kind) "
                 "VALUES ('README.md', 'path')")
    conn.commit()
    return conn


def _reconcile(conn):
    from rota.roles import prompts

    wake = Wake("vision_keeper", "tick:reconcile",
                refs=("@prose:docs/arguments.md",))
    return build("vision_keeper", conn, mode="normal", area="@prose",
                 allow=prompts.mode_tools("vision_keeper", "reconcile"),
                 wake=wake)


def test_a_readme_side_that_restates_the_row_is_no_conflict(account):
    """Night 143, s12 and 30 more: "the README says <the item's own text>;
    the code shows <unrelated docs text>"."""
    sb = _reconcile(account)
    with pytest.raises(ValueError, match="its own text") as exc:
        sb.call("ledger.log", about_ref="defines_commands", about_table="items",
                assumption=f"the README says {ACCOUNT}; the code shows Arguments "
                           f"are positional in nature and take a help string",
                kind="conflict")
    said = str(exc.value)
    assert "as your reading of their words" in said
    assert "surveys.attest(outcome='none_found', citations=['docs/arguments.md'])" in said


def test_a_conflict_with_one_side_only_is_no_conflict(account):
    """Night 143, s28 and s37: the whole note is the item's own text, or
    "the code shows: <the item's own text>" with no README side."""
    sb = _reconcile(account)
    for words in (ACCOUNT, f"the code shows: {ACCOUNT}"):
        with pytest.raises(ValueError, match="its own text"):
            sb.call("ledger.log", about_ref="defines_commands",
                    about_table="items", assumption=words, kind="conflict")


def test_a_conflict_about_a_decision_alone_is_refused(tmp_path):
    """A ruling is no side of a disagreement. A note about it goes back on
    the principal's page as the seat's reading of their words."""
    conn = init_db(tmp_path / "d.db")
    conn.execute("INSERT INTO decisions (id, author, text) VALUES "
                 "('d1','principal','closing keeps every invoice')")
    conn.commit()
    sb = build("vision_keeper", conn, mode="normal")
    with pytest.raises(ValueError, match="d1 is a decision"):
        sb.call("ledger.log", about_ref="d1", about_table="decisions",
                assumption="the ruling keeps invoices and my plan drops them",
                kind="conflict")


def test_a_readme_claim_that_differs_from_the_row_is_still_a_conflict(account):
    """DECISIONS of 2026-09-12, point 4: conflicting sources always ask."""
    sb = _reconcile(account)
    out = sb.call("ledger.log", about_ref="defines_commands", about_table="items",
                  assumption="the README says commands are defined in a YAML "
                             "file; the code shows " + ACCOUNT,
                  kind="conflict")
    assert out["id"].startswith("l_")


# ---------------------------------------------------------------------------
# The `ledger.log` door: a bare `scope` log, judged in design pass 3.
# ---------------------------------------------------------------------------

@pytest.fixture
def batch(tmp_path):
    conn = init_db(tmp_path / "b.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1','closing keeps invoices','in_scope',"
                 "'approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','i1','close an account')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('c1','tk1','closing an account leaves its invoices')")
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) "
                 "VALUES ('b1','i1','running','abc')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('b1','tk1')")
    conn.commit()
    return conn


def _seat(conn, mode):
    from rota.roles import prompts

    return build("developer", conn, batch_id="b1", mode="normal",
                 allow=prompts.mode_tools("developer", mode))


def test_a_scope_log_is_offered_the_vision_keepers_question(batch):
    sb = _seat(batch, "batch_start")
    with pytest.raises(ValueError, match=r"msg\.question_vision_keeper"):
        sb.call("ledger.log", about_ref="tk1", about_table="tickets",
                assumption="the confirm function does not exist, and building "
                           "it is outside this batch",
                kind="scope")


def test_a_scope_log_in_a_mode_with_no_such_call_is_a_row(batch):
    sb = _seat(batch, "tests_failing")
    out = sb.call("ledger.log", about_ref="tk1", about_table="tickets",
                  assumption="the confirm function does not exist, and building "
                             "it is outside this batch",
                  kind="scope")
    assert out["id"].startswith("l_")
