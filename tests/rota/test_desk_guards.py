"""
Four guards from one re-record (2026-09-01), each attributed from a transcript.

The register's reds after the triage collapse split cleanly into "the role
found the right act and misaddressed it": a Critic quoting the vacuous test
at the Developer, an Architect reporting the constraint instead of the batch,
a Vision Keeper minuting its own edit under a prefixed id the previous guard
coached it into, a Critic judging what it had just put in dispute, and a
Tester woken about a term with no criterion in view at all. Each is refused
or supplied where the state already says what is right.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.core.predicates import Wake


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, provenance, approval, "
                 "approval_ver, version) VALUES ('i1','closing keeps invoices',"
                 "'in_scope','decided','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','i1','close an account')")
    conn.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
                 "VALUES ('g1','account','the billing entity','decided')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text, term_refs) VALUES "
                 "('c1','tk1','closing an account leaves its invoices in place',"
                 "'[\"g1\"]')")
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) VALUES "
                 "('b1','i1','running','abc123')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('b1','tk1')")
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                 "VALUES ('tst1','b1','c1','test_close.py',"
                 "\"assert close_account('a1') is not None\")")
    conn.commit()
    return conn


def test_a_challenge_is_the_sessions_verdict_until_it_lands(db):
    sb = build("critic", db, batch_id="b1", mode="review")
    sb.call("msg.challenge_tester", refs=["c1", "tst1"],
            quotes=["closing an account leaves its invoices in place",
                    "assert close_account('a1') is not None"])
    with pytest.raises(ValueError, match="already challenged the tester"):
        sb.call("verdicts.emit", batch_id="b1", result="fail",
                failed_criterion="c1")


def test_a_bare_call_of_the_surface_name_is_a_call_of_the_surface(db):
    """
    tipsK, 2026-09-09: the surface is `main.py::calculate_tip`. The test
    did `from main import calculate_tip` and called it. Compared whole, the
    door said the test never calls the surface, three sessions, quarantine,
    nothing merged.
    """
    db.execute("UPDATE criteria SET surface_refs = '[\"main.py::calculate_tip\"]' "
               "WHERE id = 'c1'")
    db.execute("DELETE FROM tests")
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    got = sb.call("tests.encode", id="tst9", criterion_id="c1",
                  path="tests/test_tip.py",
                  body="from main import calculate_tip\n"
                       "def test_calculate_tip():\n"
                       "    assert calculate_tip(100, 10) == 10\n")
    assert got, "the encode must land"
    # tipsAC: the Tester invented a `Bill` class and imported it from main.
    # Nothing defines it and no criterion names it.
    with pytest.raises(ValueError, match="imports Bill from main, and main.py defines no such name"):
        sb.call("tests.encode", id="tst11", criterion_id="c1",
                path="tests/test_tip3.py",
                body="from main import calculate_tip, Bill\n"
                     "def test_calculate_tip():\n"
                     "    assert calculate_tip(Bill(100, 2)) == [50, 50]\n")
    # tipsU: the surface lives in main.py, the test imported it from a
    # module that does not exist, ImportError at collection, quarantine.
    with pytest.raises(ValueError, match="lives in main.py and this test imports from billing"):
        sb.call("tests.encode", id="tst10", criterion_id="c1",
                path="tests/test_tip2.py",
                body="from billing import calculate_tip\n"
                     "def test_calculate_tip():\n"
                     "    assert calculate_tip(100, 10) == 10\n")


def test_a_rewrite_keeps_what_the_criteria_and_other_files_use(db, tmp_path):
    """
    tipsO, 2026-09-09: the Developer writes before the Tester now, so on
    the first write no test protects anything. The first write replaced a
    module of four functions with one. The criterion's surface named a
    vanished one, the test then imported it, and the fix loop ran to the
    step cap. The criteria's surfaces and other files' imports hold too.
    """
    root = tmp_path / "wt"; root.mkdir()
    (root / "script.py").write_text("def close_account(a):\n    return 'invoices'\n"
                                    "def other():\n    return 1\n"
                                    "def helper():\n    return 2\n", encoding="utf-8")
    (root / "app.py").write_text("from script import helper\n", encoding="utf-8")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("DELETE FROM tests")
    db.execute("UPDATE criteria SET surface_refs = '[\"script.py::close_account\"]' "
               "WHERE id = 'c1'")
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    with pytest.raises(ValueError, match="drops close_account, helper"):
        sb.call("code.write", path="script.py", text="def run():\n    return 1\n")
    out = sb.call("code.write", path="script.py",
                  text="def close_account(a):\n    return 'invoices'\n"
                       "def helper():\n    return 2\n"
                       "def run():\n    return 1\n")
    assert out["bytes"]


def test_the_developer_writes_no_test_file_and_keeps_the_main_guard(db, tmp_path):
    """
    tipsR, 2026-09-09: the Developer rewrote the Tester's test file to
    import a module that does not exist, and rewrote main.py from the
    interactive program to one function. The harness ran the database's
    copy of the test and passed. The merge carried both files. The merged
    program printed nothing and its own test suite was broken.
    """
    root = tmp_path / "wt"; root.mkdir()
    (root / "main.py").write_text(
        "def run():\n    return 1\n\nif __name__ == \"__main__\":\n    run()\n",
        encoding="utf-8")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    with pytest.raises(ValueError, match="test file, and the tests are the Tester's"):
        sb.call("code.write", path="tests/test_x.py", text="def test_x():\n    pass\n")
    with pytest.raises(ValueError, match="entry point"):
        sb.call("code.write", path="main.py", text="def split(t, n):\n    return t / n\n")
    # tipsV: the entry point keeps every definition, referenced or not.
    # Four walks lost the program to a main.py that kept only the feature.
    with pytest.raises(ValueError, match="drops run, and the program's entry point"):
        sb.call("code.write", path="main.py",
                text="def split(t, n):\n    return t / n\n\n"
                     "if __name__ == \"__main__\":\n    split(1, 1)\n")
    out = sb.call("code.write", path="main.py",
                  text="def run():\n    return 1\n\ndef split(t, n):\n    return t / n\n\n"
                       "if __name__ == \"__main__\":\n    run()\n")
    assert out["bytes"]


def test_two_answers_on_the_same_rows_end_the_questions(db):
    """
    tipsAB, 2026-09-09: the Tester asked the Terminologist about one
    criterion's term 71 times in nine wordings, alternating two ref sets so
    the exact-refs door never fired. Two answers are the bound.
    """
    m = ("INSERT INTO messages (id, thread_id, from_role, to_role, verb, body_refs, "
         "body_text, cause_id, seq, status) VALUES (?,?,?,?,?,?,?,?,?,?)")
    db.execute(m, ("q1", "t", "tester", "terminologist", "question", '["c1"]', "what?", None, 1, "answered"))
    db.execute(m, ("a1", "t", "terminologist", "tester", "answer", '["g1"]', None, "q1", 2, "answered"))
    db.execute(m, ("q2", "t", "tester", "terminologist", "question", '["c1", "g1"]', "and?", None, 3, "answered"))
    db.execute(m, ("a2", "t", "terminologist", "tester", "answer", '["g1"]', None, "q2", 4, "answered"))
    db.commit()
    from rota.roles import prompts
    sb = build("tester", db, batch_id="b1", mode="tests_missing",
               allow=prompts.mode_tools("tester", "tests_missing"))
    with pytest.raises(ValueError, match="answered 2 questions of yours.*triage"):
        sb.call("msg.question_terminologist", refs=["c1"], question="but really?")


def test_a_commit_defines_the_surface_the_criteria_name(db, tmp_path):
    """
    tipsX, 2026-09-09: the criterion named `main.py::split_bill`, the
    Developer repurposed `calculate_tip` and committed three times without
    defining `split_bill`. Every test of it failed at import.
    """
    import subprocess

    root = tmp_path / "wt"; root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "script.py").write_text("def other():\n    return 1\n", encoding="utf-8")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE criteria SET surface_refs = '[\"script.py::close_account\"]' "
               "WHERE id = 'c1'")
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    with pytest.raises(ValueError, match="does not define script.py::close_account"):
        sb.call("code.commit", message="half done")
    sb.call("code.write", path="script.py",
            text="def other():\n    return 1\n\ndef close_account(a):\n    return 'x'\n")
    out = sb.call("code.commit", message="the surface exists")
    assert out.get("committed") is not False


def test_a_file_defines_each_name_once(db, tmp_path):
    """
    tipsS, 2026-09-09: a second `calculate_tip(total, people)` above the
    tip function. Python kept the last one, the test got the tip instead of
    the share, and the fix loop ran to the step cap.
    """
    root = tmp_path / "wt"; root.mkdir()
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    with pytest.raises(ValueError, match="defines calculate_tip twice"):
        sb.call("code.write", path="calc.py",
                text="def calculate_tip(t, n):\n    return t / n\n\n"
                     "def calculate_tip(t, p):\n    return t * p / 100\n")
    assert sb.call("code.write", path="calc.py",
                   text="def split_bill(t, n):\n    return t / n\n\n"
                        "def calculate_tip(t, p):\n    return t * p / 100\n")["bytes"]


def test_labelled_quotes_are_read_not_crashed_on(db):
    """
    qwen2.5:14b sent `quotes={"criterion": ..., "test": ...}` on the register
    (2026-09-09). The door crashed on `.split` and the Critic's challenge, the
    one act 8B never reached, was lost to a Python error.
    """
    sb = build("critic", db, batch_id="b1", mode="review")
    sb.call("msg.challenge_tester", refs=["c1", "tst1"],
            quotes={"criterion": "closing an account leaves its invoices in place",
                    "test": "assert close_account('a1') is not None"})
    assert sb.ctx.outbound


def test_a_developer_challenge_does_not_block_the_verdict(db):
    # Recipient-scoped (ruled 2026-09-03): a tester-challenge disputes the
    # measuring instrument, so no verdict may land on top of it; a
    # developer-challenge disputes the code, which is what a fail verdict
    # records. The verb-generic form refused a correct fail-naming-its-
    # criterion verdict five of five (CR-fail-names-its-criterion).
    sb = build("critic", db, batch_id="b1", mode="review")
    sb.call("msg.challenge_developer", refs=["c1"],
            quotes=["closing an account leaves its invoices in place"])
    # The structural fork (2026-09-03): a fail must claim its criterion's
    # test encodes it before the tool will land the verdict.
    sb.call("verdicts.claim_encodes", criterion_id="c1", encodes=True)
    out = sb.call("verdicts.emit", batch_id="b1", result="fail",
                  failed_criterion="c1")
    assert out["result"] == "fail"


def test_a_report_from_a_batch_wake_names_the_batch(db):
    wake = Wake("architect", "tick:exhausted", refs=("b1",))
    sb = build("architect", db, batch_id="b1", mode="exhausted", wake=wake)
    db.execute("INSERT INTO constraints (id, headline, text, provenance) VALUES "
               "('cn1','exports never buffer','memory stays flat','decided')")
    db.commit()
    with pytest.raises(ValueError, match="add 'b1' to refs"):
        sb.call("msg.report_liaison", refs=["cn1"])
    sb.call("msg.report_liaison", refs=["cn1", "b1"])


def test_a_prefixed_item_id_is_still_a_minute(db):
    from rota.roles import prompts
    sb = build("vision_keeper", db, mode="message",
               allow=prompts.mode_tools("vision_keeper", "message"))
    sb.call("problem.assert", id="i1", text="users can close their account",
            kind="in_scope")
    with pytest.raises(ValueError, match="row you wrote this session"):
        sb.call("decisions.author", id="i1", text="the principal rejected it")
    with pytest.raises(ValueError, match="minuting your own edit"):
        sb.call("decisions.author", id="c_i1", text="the principal rejected it")


def test_a_tester_woken_about_a_term_sees_the_criteria_that_use_it(db):
    db.execute("UPDATE batches SET status = 'pending'")
    db.commit()
    wake = Wake("tester", "message", refs=("g1",))
    sb = build("tester", db, mode="answer", wake=wake)
    rows = sb.call("criteria.load")
    assert [r["id"] for r in rows] == ["c1"], rows


# --- S0 walk eight: the challenge loop nobody could see out of -------------


def _encode(sb, body):
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    return sb.call("tests.encode", id="tst_new", criterion_id="c1",
                   path="tests/test_greet.py", body=body)


def test_a_test_that_reads_stdin_cannot_pass_under_pytest(db):
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    with pytest.raises(ValueError, match="captures stdin"):
        _encode(sb, "def test_greet():\n    assert input('name: ') == 'Alice'")
    # Fed in, it is a test -- once the chosen name is on the ledger.
    sb.call("ledger.log", about_ref="c1", about_table="criteria",
            assumption="the test assumes Alice as a sample name")
    _encode(sb, "from script import greet\n"
                "def test_greet(monkeypatch):\n"
                "    monkeypatch.setattr('builtins.input', lambda _='': 'Alice')\n"
                "    assert greet() == 'closing Alice'")


def test_a_name_the_test_never_imports_is_a_nameerror(db):
    """Walk nine's one landed test: `assert test_valid_input()` against a
    name defined nowhere. The floor puts the project on the import path;
    the test says where the thing comes from."""
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    with pytest.raises(ValueError, match=r"uses test_valid_input and never"):
        _encode(sb, "def test_greet():\n    assert test_valid_input()")
    # Walk twelve: a module used as a name and imported nowhere.
    with pytest.raises(ValueError, match=r"uses script and never imports"):
        _encode(sb, "def test_greet():\n    assert script.run('x') == 'closing x'")


def test_two_tests_may_not_share_a_file(db):
    """Walk twelve: two tests named tests/test_input_validation.py and the
    second overwrote the first on disk."""
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c2','tk1','the account is tombstoned')")
    db.commit()
    with pytest.raises(ValueError, match="already tst1's file"):
        sb.call("tests.triage", criterion_id="c2", verdict="encodable")
        sb.call("tests.encode", id="tst_new", criterion_id="c2",
                path="test_close.py",
                body="from script import close_account\n"
                     "def test_tomb():\n    assert close_account('a') == 'invoices'")


def test_an_assert_on_a_constant_checks_nothing(db):
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    with pytest.raises(ValueError, match="verdict='cannot'"):
        _encode(sb, "def test_meta():\n    # replace when available\n    assert True")


def test_a_module_that_reads_stdin_at_import_dies_at_collection(db, tmp_path):
    root = tmp_path / "wt"; root.mkdir()
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    with pytest.raises(ValueError, match="input\\(\\) at module level \\(line 3\\)"):
        sb.call("code.write", path="script.py",
                text="def greet(n):\n    return f'Hello {n}!'\n"
                     "name = input('Enter your name: ')\nprint(greet(name))\n")
    out = sb.call("code.write", path="script.py",
                  text="def greet(n):\n    return f'Hello {n}!'\n\n"
                       "if __name__ == '__main__':\n"
                       "    print(greet(input('Enter your name: ')))\n")
    assert out["created"]


def test_the_same_escalation_twice_is_refused_toward_the_answer(db):
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m1','th','developer','architect',"
               "'escalate','[\"c1\", \"tst1\"]',1,'answered')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status, cause_id) VALUES ('m2','th','architect',"
               "'developer','answer','[\"c1\"]',2,'answered','m1')")
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    with pytest.raises(ValueError, match="act on the answer"):
        sb.call("msg.escalate_architect", refs=["c1", "tst1"])


def test_code_in_the_reply_is_told_it_landed_nowhere(db, tmp_path):
    from rota.core.runner import run_session
    from rota.llm.llm import Pins, ScriptedBackend
    root = tmp_path / "wt"; root.mkdir()
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    backend = ScriptedBackend([
        "Here is the fix:\n```python\ndef greet(n):\n    return n\n```",
        "Done.",
    ])
    out = run_session(db, Wake("developer", "tick:tests_failing", refs=("b1",)),
                      backend=backend, pins=Pins(model="scripted"))
    assert "wrote code into its reply" in out.errors
    _, user = backend.calls[1]
    assert "a reply is not a file" in user


def test_a_tested_criterion_is_shown_as_tested_and_owes_nothing(db):
    """Walk eleven: three criteria tested, one not, and every wake
    re-triaged and re-encoded all four."""
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c2','tk1','the account is tombstoned')")
    db.commit()
    rows = {r["id"]: r for r in sb.call("criteria.load")}
    assert rows["c1"]["tested_by"] == "tst1"
    assert "tested_by" not in rows["c2"]
    out = sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    assert "already encodes it" in out["next"]


def test_an_answer_met_with_the_same_wall_is_derived_unresolved(db):
    """Walk eleven: five answered questions about one criterion, each
    followed by the same refused encode, and `criterion_repair` never
    fired because nothing said the answer did not land. Any encode wall
    met with the answer in view is that evidence."""
    from rota.core.runner import run_session
    from rota.llm.llm import Pins, ScriptedBackend
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c2','tk1','unit tests must validate the behaviour')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m1','th','tester','terminologist',"
               "'question','[\"c2\"]',1,'answered')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status, cause_id) VALUES ('m2','th','terminologist',"
               "'tester','answer','[\"c2\"]',2,'answered','m1')")
    db.commit()
    backend = ScriptedBackend([
        "TOOL: tests.triage(criterion_id='c2', verdict='encodable')\n"
        "TOOL: tests.encode(id='tst_9', criterion_id='c2', "
        "path='tests/test_meta.py', body='def test_meta():\\n    assert True')",
        "Done.",
    ])
    out = run_session(db, Wake("tester", "message", message_id="m2",
                               refs=("m2",)),
                      backend=backend, pins=Pins(model="scripted"))
    assert out.committed, out.errors
    row = db.execute("SELECT status FROM messages WHERE id='m1'").fetchone()
    assert row["status"] == "unresolved", "the wall is the reask"


def test_a_tester_cannot_hold_a_test_whose_run_reached_stdin(db):
    """Walk seventeen: the challenge carried the OSError, the Tester held,
    and the test cannot pass however the code is written."""
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
               "result, attempt, output) VALUES ('r1','b1','tst1','abc123',"
               "'fail',1,'E  OSError: pytest: reading from stdin while output "
               "is captured!')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m1','th','developer','tester',"
               "'challenge','[\"c1\", \"tst1\"]',1,'open')")
    db.commit()
    from rota.roles import prompts
    sb = build("tester", db, batch_id="b1", mode="challenge",
               allow=prompts.mode_tools("tester", "challenge"),
               wake=Wake("tester", "message", message_id="m1", refs=("m1",)))
    with pytest.raises(ValueError, match="cannot pass against any implementation"):
        sb.call("msg.answer_developer", refs=["c1", "tst1"])


def test_a_commit_resets_the_failing_ticks_attempts(db):
    """Walk seventeen: four, three, two tests failing across three commits
    and the third session was the quarantine -- progress counted as
    dispatch without progress. A new head commit is the wake stopping
    being produced, from the counter's point of view."""
    from rota.core.db import _lift_quarantines
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined) "
               "VALUES ('developer|tick:tests_failing|b1', 2, 0)")
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined) "
               "VALUES ('tester|tick:tests_missing|b1', 2, 0)")
    db.commit()

    from rota.core.db import Write
    W = Write(table="batches", row_id="b1", values={"head_commit": "def456"})

    _lift_quarantines(db, W)
    rows = {r["tick_key"]: r["attempts"] for r in db.execute(
        "SELECT tick_key, attempts FROM tick_attempts")}
    assert "developer|tick:tests_failing|b1" not in rows, "progress resets"
    assert rows["tester|tick:tests_missing|b1"] == 2, "an unrelated debt keeps its count"


def test_a_re_encoded_test_is_owed_a_fresh_run(db):
    """Walk eighteen: the fixed test never ran, because the batch already
    had runs at the head commit, and everyone read the stale result."""
    from rota.core.db import Write, _lift_quarantines
    from rota.core.predicates import harness
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
               "result, attempt, output) VALUES ('r1','b1','tst1','abc123',"
               "'fail',1,'E  OSError: reading from stdin while output is captured')")
    db.commit()
    assert harness(db) == [], "tested at this commit: nothing owed"
    _lift_quarantines(db, Write(table="tests", row_id="tst1",
                                values={"body": "def test_x():\n    assert 1"}))
    assert not db.execute("SELECT 1 FROM test_runs WHERE test_id='tst1'").fetchone(), \
        "the old body's runs are gone"
    assert [w.refs for w in harness(db)] == [("b1",)], "a run is owed again"


def test_a_pass_supersedes_the_fail_before_it(db):
    """Walk nineteen: all four tests green, and the Developer woken on a
    fail row from an earlier run, rewrote working code and broke it."""
    from rota.core.predicates import tests_failing, review
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
               "result, attempt, output) VALUES ('r1','b1','tst1','abc123',"
               "'fail',1,'boom')")
    db.commit()
    assert [w.refs for w in tests_failing(db)] == [("b1",)]
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
               "result, attempt, output) VALUES ('r2','b1','tst1','abc123',"
               "'pass',2,'.')")
    db.commit()
    assert tests_failing(db) == [], "the newest row is the result"


def test_a_branch_claim_does_not_hold_the_act_behind_it(db, tmp_path):
    """Walk twenty-one: seven triages, seven encodes held behind them, a
    prose turn, and the refusals arrived after the session could answer."""
    from rota.core.runner import run_session
    from rota.llm.llm import Pins, ScriptedBackend
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c2','tk1','the account is tombstoned')")
    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
               "('e1','principal',1,'tombstone the account, invoices stay')")
    db.commit()
    backend = ScriptedBackend([
        "TOOL: tests.triage(criterion_id='c2', verdict='encodable')\n"
        "TOOL: tests.encode(id='tst_9', criterion_id='c2', path='tests/test_t.py', "
        "body='from script import tombstone\\ndef test_t():\\n"
        "    assert tombstone(\"account\") == \"tombstoned\"')",
        "Done.",
    ])
    out = run_session(db, Wake("tester", "tick:tests_missing", refs=("b1",)),
                      backend=backend, pins=Pins(model="scripted"))
    _, user = backend.calls[1]
    assert "NOT RUN" not in user, "a claim is not a lookup; the encode ran"
    assert db.execute("SELECT 1 FROM tests WHERE id='tst_9'").fetchone(), out.errors


def test_code_is_written_in_a_batch_or_not_at_all(db, tmp_path):
    """Walk twenty-three: a Developer woken by a message before any batch
    wrote into the project root, then met "no batch" at commit."""
    from rota.roles import prompts
    sb = build("developer", db, mode="normal")
    with pytest.raises(ValueError, match="no batch: code is written"):
        sb.call("code.write", path="script.py", text="x = 1\n")


def test_the_written_module_is_told_what_the_tests_import(db, tmp_path):
    """Walk twenty-three: the tests said `import script`, the Developer
    wrote greeting_script.py, ModuleNotFoundError three sessions running."""
    root = tmp_path / "wt"; root.mkdir()
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE tests SET body = 'import script\ndef test_x():\n"
               "    assert script.run() == 1' WHERE id = 'tst1'")
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    with pytest.raises(ValueError, match="write script.py first, helpers after"):
        sb.call("code.write", path="greeting.py", text="def run():\n    return 1\n")
    # Walks twenty-four and twenty-six: the import inside the test function,
    # indented -- a column-zero anchor saw no imports at all.
    db.execute("UPDATE tests SET body = 'def test_x():\n    from script import run\n"
               "    assert run() == 1' WHERE id = 'tst1'")
    db.commit()
    with pytest.raises(ValueError, match="write script.py first, helpers after"):
        sb.call("code.write", path="greeting.py", text="def run():\n    return 1\n")
    # The 14B walk: the right name in a folder `import script` cannot see.
    with pytest.raises(ValueError, match="not where `import script` looks"):
        sb.call("code.write", path="scripts/script.py", text="def run():\n    return 1\n")
    out = sb.call("code.write", path="script.py", text="def run():\n    return 1\n")
    assert "note" not in out
    # Once the named module exists, a helper is legal.
    out = sb.call("code.write", path="greeting.py", text="def g():\n    return 1\n")
    assert out["created"]


def test_a_misplaced_quote_is_told_whose_words_it_quotes(db):
    """Walk twenty-three: c_s1_t3's sentence quoted under refs naming
    c_s1_t4, nine identical refusals across three sessions."""
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c2','tk1','the account is tombstoned')")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('tst2','b1','c2','test_tomb.py',"
               "\"assert tombstone('a') == 'gone'\")")
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    # Walks twenty-three to twenty-seven: told whose words they were, the
    # Developer sent the identical call nine times a walk. The test's words
    # are the bar; a criterion of the same batch, verbatim, goes through.
    sb.call("msg.challenge_tester", refs=["c2", "tst2"],
            quotes=["closing an account leaves its invoices in place",
                    "assert tombstone('a') == 'gone'"])
    assert sb.ctx.outbound[-1]["to_role"] == "tester"
    # A paraphrase of any criterion is still refused.
    sb2 = build("developer", db, batch_id="b1", mode="tests_failing",
                allow=prompts.mode_tools("developer", "tests_failing"))
    with pytest.raises(ValueError, match="Quote, not paraphrase"):
        sb2.call("msg.challenge_tester", refs=["c2", "tst2"],
                 quotes=["the criterion wants the ledger balanced monthly",
                         "assert tombstone('a') == 'gone'"])


def test_an_undefined_name_anywhere_in_a_test_is_a_nameerror(db):
    """Walk twenty-five: `assert script.run(valid_input) == expected_output`
    with neither name defined -- not a call, so the call check missed it."""
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    with pytest.raises(ValueError, match="uses expected_output and never"):
        _encode(sb, "import script\ndef test_x():\n"
                    "    assert script.run('a') == expected_output")
    # Bound names of every shape are fine: args, with-as, loops, walrus.
    sb2 = build("tester", db, batch_id="b1", mode="tests_missing")
    sb2.call("ledger.log", about_ref="c1", about_table="criteria",
             assumption="the test assumes closing as a sample")
    _encode(sb2, "from script import close_account\n"
                 "def test_x(tmp_path):\n"
                 "    for name in ['closing']:\n"
                 "        with open(tmp_path / name, 'w') as fh:\n"
                 "            assert close_account(name) == 'invoices'")


def test_a_rewrite_may_not_delete_what_the_tests_import(db, tmp_path):
    """Walk twenty-five: three green tests, and the fourth's fix was a
    script.py with the three imported functions gone."""
    root = tmp_path / "wt"; root.mkdir()
    (root / "script.py").write_text("def close_account(a):\n    return 'invoices'\n"
                                    "def other():\n    return 1\n", encoding="utf-8")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE tests SET body = 'from script import close_account\n"
               "def test_x():\n    assert close_account(1) == \"invoices\"' "
               "WHERE id = 'tst1'")
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    with pytest.raises(ValueError, match="drops close_account, and the batch's tests"):
        sb.call("code.write", path="script.py", text="def run():\n    return 1\n")
    # Dropping a function nobody imports, in a module that is not the
    # entry point, is the Developer's business.
    out = sb.call("code.write", path="script.py",
                  text="def close_account(a):\n    return 'invoices'\n")
    assert out["bytes"]


def test_a_criterion_about_the_tests_is_not_a_behaviour(db):
    """Walks eleven to twenty-eight: "Unit tests must validate..." encoded
    as assert True, as an invented dict API, as calls to tests that exist
    nowhere; nothing a machine can check follows from a sentence about
    checking."""
    from rota.roles import prompts
    sb = build("terminologist", db, mode="criteria",
               allow=prompts.mode_tools("terminologist", "criteria"))
    with pytest.raises(ValueError, match="names the Tester's job"):
        sb.call("criteria.specify", id="c9", ticket_id="tk1",
                text="Unit tests must validate the script's behaviour with "
                     "valid and invalid inputs")
    sb.call("criteria.specify", id="c9", ticket_id="tk1",
            text="an empty name is answered with 'Invalid input'")


def test_a_respecify_with_the_same_words_repairs_nothing(db):
    from rota.roles import prompts
    sb = build("terminologist", db, mode="criterion_repair",
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    out = sb.call("criteria.respecify", id="c1",
                  text="Closing an account leaves its invoices in place.",
                  surface_refs=["close_account"])
    assert out.get("unchanged"), out
    assert not any(w[0] == "criteria" for w in sb.ctx.writes)


def test_a_fixture_the_harness_lacks_errors_at_setup(db):
    """Walk twenty-nine: four tests took `mocker` (pytest-mock, not
    installed), every run an error before the first assertion."""
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    with pytest.raises(ValueError, match="takes 'mocker', and the harness has no"):
        _encode(sb, "from script import close_account\n"
                    "def test_x(mocker):\n"
                    "    mocker.patch('builtins.input', return_value='a')\n"
                    "    assert close_account('a') == 'invoices'")
    # pytest's own fixtures and one the file defines are fine.
    sb2 = build("tester", db, batch_id="b1", mode="tests_missing")
    _encode(sb2, "import pytest\nfrom script import close_account\n"
                 "@pytest.fixture\ndef acct():\n    return 'invoices'\n"
                 "def test_x(monkeypatch, capsys, acct):\n"
                 "    assert close_account(acct) == 'invoices'")


def test_a_chat_reply_that_restates_a_statement_carries_its_ref(db):
    """G1-what-the-brief-already-holds: the Liaison claimed chat, answered
    from the brief word for word, and ref'd the entry. The system knows
    where the words came from."""
    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
               "('e1','principal',1,'how long do we keep invoices?')")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
               "text, status) VALUES ('s1','e1',0,10,'invoices are kept for "
               "seven years after the account is closed','ratified')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES ('m1','th','principal','liaison',"
               "'converse','[\"e1\"]',1)")
    db.commit()
    from rota.roles import prompts
    sb = build("liaison", db, mode="converse",
               allow=prompts.mode_tools("liaison", "converse"),
               wake=Wake("liaison", "message", message_id="m1", refs=("m1",)))
    sb.call("brief.intake", verdict="chat")
    sb.call("msg.converse_principal", refs=["e1"],
            reply="We decided that invoices are kept for seven years after the "
                  "account is closed.")
    assert "s1" in sb.ctx.outbound[-1]["body_refs"]


def test_a_verbatim_item_assert_moves_no_version(db):
    """Walk thirty-one: the ladder's last rung re-asserted the item with its
    own words, the version moved, and the batch with three green tests was
    cancelled as a revocation."""
    from rota.roles import prompts
    sb = build("vision_keeper", db, mode="exhausted",
               allow=prompts.mode_tools("vision_keeper", "exhausted"))
    out = sb.call("problem.assert", id="i1", text="Closing keeps invoices.",
                  kind="in_scope")
    assert out.get("unchanged"), out
    assert not any(w[0] == "items" for w in sb.ctx.writes)


def test_an_abandoned_batch_releases_its_tickets_for_regrouping(db):
    """Walk thirty-one: re-approved after the cancel, the item's tickets
    still belonged to the abandoned batch and nothing re-grouped them."""
    from rota.core.predicates import grouping
    assert grouping(db) == [], "tk1 is in a running batch"
    db.execute("UPDATE batches SET status = 'abandoned' WHERE id = 'b1'")
    db.commit()
    assert [w.refs for w in grouping(db)] == [("tk1",)]


def test_one_program_one_module_name_across_a_batch(db):
    """Walk thirty-two: three tests imported `script`, one imported `main`,
    and the odd one failed at import for the rest of the batch."""
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c2','tk1','the account is tombstoned')")
    db.execute("UPDATE tests SET body = 'from script import close_account\n"
               "def test_x():\n    assert close_account(1) == \"invoices\"' "
               "WHERE id = 'tst1'")
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    sb.call("tests.triage", criterion_id="c2", verdict="encodable")
    with pytest.raises(ValueError, match="other tests import script -- one program"):
        sb.call("tests.encode", id="tst_new", criterion_id="c2",
                path="tests/test_tomb.py",
                body="from main import tombstone\ndef test_t():\n"
                     "    assert tombstone('a') == 'invoices'")
    sb.call("tests.encode", id="tst_new", criterion_id="c2",
            path="tests/test_tomb.py",
            body="from script import tombstone\ndef test_t():\n"
                 "    assert tombstone('a') == 'invoices'")


def test_module_level_input_through_a_local_function_is_refused(db, tmp_path):
    """Walk thirty-two: `name = prompt_for_name()` at module level, where
    the function reads input."""
    root = tmp_path / "wt"; root.mkdir()
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    with pytest.raises(ValueError, match="reads input\\(\\) at module level \\(line 4\\)"):
        sb.call("code.write", path="script.py",
                text="def prompt():\n    return input('name: ')\n\n"
                     "name = prompt()\nprint(name)\n")


def test_a_batch_id_is_never_reused(db):
    """Walk thirty-four: after the cancel, the Architect grouped the same
    tickets under `id="b1"` and resurrected the abandoned batch, worktree
    and regressed code included. An abandonment is terminal; the new work
    is a new batch."""
    db.execute("UPDATE batches SET status = 'abandoned' WHERE id = 'b1'")
    db.commit()
    from rota.roles import prompts
    sb = build("architect", db, mode="grouping",
               allow=prompts.mode_tools("architect", "grouping"))
    with pytest.raises(ValueError, match="b1 is already a batch"):
        sb.call("batches.group", id="b1", ticket_ids=["tk1"], item_id="i1")
    out = sb.call("batches.group", id="b2", ticket_ids=["tk1"], item_id="i1")
    assert out["id"] == "b2"


def test_tests_missing_is_owed_per_criterion(db):
    """Walk nine: three encodes refused, one landed, and the batch never
    woke the Tester again -- "a batch with no tests" had one. A criterion
    with no test is the debt; a routed one (open question) is not."""
    from rota.core.predicates import tests_missing
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c2','tk1','the account is tombstoned')")
    db.commit()
    assert [w.refs for w in tests_missing(db)] == [("b1",)], "c2 has no test"
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m1','th','tester','terminologist',"
               "'question','[\"c2\"]',1,'open')")
    db.commit()
    assert tests_missing(db) == [], "routed is done until the answer wakes it"


def test_a_literal_the_material_never_said_is_an_assumption_first(db):
    """The first divergence detector: the demand for a sentence lands only
    where the material underdetermined the test. Words the criterion, its
    ticket, the glossary or the principal said are free; a chosen string is
    owed a ledger row, and the encode goes through once it has one."""
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    with pytest.raises(ValueError, match="chooses 'Enter your name: '"):
        _encode(sb, "from script import prompt_text\n"
                    "def test_greet():\n"
                    "    assert prompt_text() == 'Enter your name: '")
    sb.call("ledger.log", about_ref="c1", about_table="criteria",
            assumption="the prompt reads 'Enter your name: ' -- the material "
                       "names no wording")
    _encode(sb, "from script import prompt_text\n"
                "def test_greet():\n"
                "    assert prompt_text() == 'Enter your name: '")


def test_material_words_are_never_an_assumption(db):
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
               "('e1','principal',1,'it should say Hellow User!')")
    db.commit()
    _encode(sb, "from script import close_account\n"
                "def test_greet():\n"
                "    assert close_account('invoices') == 'Hellow User!'")


def test_asserting_on_print_is_always_false(db):
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    with pytest.raises(ValueError, match="print returns None"):
        _encode(sb, "def test_greet():\n    assert print('Hello Alice!')")
    # Walk thirteen: the print moved inside a comparison.
    with pytest.raises(ValueError, match="print returns None"):
        _encode(sb, "def test_greet():\n"
                    "    assert print('Hello Alice!') == 'Hello Alice!'")


def test_a_named_act_left_undone_is_told_once(db, tmp_path):
    """Walk thirteen: "I will challenge the Tester to verify..." and the
    session ended, twice, three sessions to the quarantine."""
    from rota.core.runner import run_session
    from rota.llm.llm import Pins, ScriptedBackend
    root = tmp_path / "wt"; root.mkdir()
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    backend = ScriptedBackend([
        "The tests assert functions that do not exist. I will challenge the "
        "Tester with msg.challenge_tester to verify them.",
        "Nothing more is owed.",
    ])
    out = run_session(db, Wake("developer", "tick:tests_failing", refs=("b1",)),
                      backend=backend, pins=Pins(model="scripted"))
    assert "named an act and did not perform it" in out.errors
    _, user = backend.calls[1]
    assert "a reply is not a call" in user


def test_a_tick_session_that_does_nothing_is_told_once(db, tmp_path):
    """Walk sixteen: "the test is wrong" and the session ended -- no fix, no
    challenge, no escalation, no intent phrase to catch."""
    from rota.core.runner import run_session
    from rota.llm.llm import Pins, ScriptedBackend
    root = tmp_path / "wt"; root.mkdir()
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    backend = ScriptedBackend([
        "The two-line check: does the test assert what its criterion asks "
        "for? No. The test is incorrect.",
        "Nothing is owed here.",
    ])
    out = run_session(db, Wake("developer", "tick:tests_failing", refs=("b1",)),
                      backend=backend, pins=Pins(model="scripted"))
    assert "ended a tick with nothing done" in out.errors
    _, user = backend.calls[1]
    assert "written nothing and sent nothing" in user
    assert len(backend.calls) == 2, "told once; the next prose turn stops"


def test_an_intent_with_nothing_done_is_told_once_even_unnamed(db, tmp_path):
    """Walks fourteen and fifteen: "I will address these issues by
    implementing the required functions" -- no tool named, nothing staged,
    nothing sent, three sessions to quarantine."""
    from rota.core.runner import run_session
    from rota.llm.llm import Pins, ScriptedBackend
    root = tmp_path / "wt"; root.mkdir()
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    backend = ScriptedBackend([
        "The functions are not present. I will address these issues by "
        "implementing the required functions in script.py.",
        "Nothing more is owed.",
    ])
    out = run_session(db, Wake("developer", "tick:tests_failing", refs=("b1",)),
                      backend=backend, pins=Pins(model="scripted"))
    assert "named an act and did not perform it" in out.errors


def test_a_disputed_test_travels_with_its_last_run(db):
    from rota.core.runner import _resolve_refs
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
               "result, attempt, output) VALUES ('r1','b1','tst1','abc123',"
               "'fail',1,'E  OSError: pytest: reading from stdin while output "
               "is captured!')")
    db.commit()
    out = _resolve_refs(db, ["c1", "tst1"])
    assert out["tst1"]["last_run"]["result"] == "fail"
    assert "reading from stdin" in out["tst1"]["last_run"]["output_tail"]
    assert "last_run" not in out["c1"]


def test_the_same_challenge_twice_is_refused_toward_the_door(db):
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m1','th','developer','tester',"
               "'challenge','[\"c1\", \"tst1\"]',1,'answered')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status, cause_id) VALUES ('m2','th','tester',"
               "'developer','answer','[\"c1\"]',2,'answered','m1')")
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    with pytest.raises(ValueError, match="escalate_architect"):
        sb.call("msg.challenge_tester", refs=["c1", "tst1"],
                quotes=["closing an account leaves its invoices in place",
                        "assert close_account('a1') is not None"])


def test_an_item_records_which_statement_it_reads(db):
    """The intent thread's first link: item_statements had a reader, a
    schema, and no writer, so the refs road from any artefact back to the
    principal's words ended one hop from the top in every walk."""
    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
               "('e1','principal',1,'closing keeps invoices')")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
               "text, status) VALUES ('s1','e1',0,10,'closing an account keeps "
               "its invoices','ratified')")
    db.commit()
    from rota.roles import prompts
    sb = build("vision_keeper", db, mode="message",
               allow=prompts.mode_tools("vision_keeper", "message"),
               wake=Wake("vision_keeper", "message", refs=("s1",)))
    sb.call("problem.assert", id="i9", text="closing an account keeps its "
            "invoices for seven years", kind="in_scope")
    pairs = [w for w in sb.ctx.writes if w[0] == "item_statements"]
    assert pairs and pairs[0][2] == {"item_id": "i9", "statement_id": "s1"}
    out = sb.call("problem.consult")
    row = next(r for r in out if r["id"] == "i1")
    assert row["from_statements"] == [], "existing items are untouched"


def test_the_fence_holds_a_reach_no_criterion_names(db, tmp_path):
    """
    The fence (2026-09-10): a file that reaches the network, a process, a
    removal, a path outside the project or dynamic code is refused unless
    a criterion of the batch names that behaviour. The Developer's writes
    and the Tester's tests both pass through it.
    """
    root = tmp_path / "wt"; root.mkdir()
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    with pytest.raises(ValueError, match="reaches the network at line 1"):
        sb.call("code.write", path="script.py",
                text="import requests\ndef close_account(a):\n    return 1\n")
    with pytest.raises(ValueError, match="reaches the process at line 2"):
        sb.call("code.write", path="script.py",
                text="import os\nos.system('rm -rf x')\n")
    with pytest.raises(ValueError, match="reaches the outside"):
        sb.call("code.write", path="script.py",
                text="def close_account(a):\n    return open('/etc/hosts').read()\n")
    with pytest.raises(ValueError, match="reaches the dynamic"):
        sb.call("code.write", path="script.py",
                text="def close_account(a):\n    return eval(a)\n")
    out = sb.call("code.write", path="script.py",
                  text="import json\ndef close_account(a):\n    return json.dumps(a)\n")
    assert out["bytes"]
    # A criterion that names the behaviour opens the fence.
    db.execute("UPDATE criteria SET text = ? WHERE id = 'c1'",
               ("closing an account sends an email to the owner",))
    db.commit()
    out = sb.call("code.write", path="script.py",
                  text="import smtplib\ndef close_account(a):\n    return 1\n")
    assert out["bytes"]
    # The Tester's test goes through the same fence.
    tester = build("tester", db, batch_id="b1", mode="tests_missing")
    tester.call("tests.triage", criterion_id="c1", verdict="encodable")
    with pytest.raises(ValueError, match="reaches the process"):
        tester.call("tests.encode", id="tst_new", criterion_id="c1",
                    path="tests/test_close.py",
                    body="import subprocess\ndef test_close():\n"
                         "    assert subprocess.run(['x']).returncode == 0\n")


def test_a_citation_refusal_names_the_file_it_wants(db):
    """
    tipsAI (2026-09-10): the Critic read main.py and cited the claim's own
    id fourteen sessions running, and the refusal said "code.source it
    first" about a file it had opened.
    """
    from rota.roles import prompts

    from rota.core.predicates import Wake
    sb = build("critic", db, mode="normal", wake=Wake(role="critic", kind="tick:challenge",
                                                     refs=("@claim:items:i1",), detail="challenge"),
               allow=prompts.mode_tools("critic", "challenge"))
    sb.ctx.opened.add("main.py")
    with pytest.raises(ValueError, match="is the claim's id, not a file.*You opened: main.py"):
        sb.call("challenge.uphold", citation="items:i1", quote="return 1", why="it does")


def test_a_delivered_statement_is_an_item_of_its_own(db):
    """
    tipsAI (2026-09-10): delivered "split the bill", the Vision Keeper
    asserted `how_it_works` as the split and then an item under the
    statement's id. The account was gone and nothing sliced the split.
    """
    from rota.roles import prompts

    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
               "('e1','principal',1,'Split the bill between the people paying')")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, "
               "status) VALUES ('s1','e1',0,10,'Split the bill between the people paying','ratified')")
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, approval_ver, "
               "version) VALUES ('how_it_works', ?, 'in_scope', 'decided', 'approved', 1, 1)",
               ("The program is a tip calculator: it takes a total and a percentage "
                "and prints the tip and the total with tip.",))
    db.commit()
    sb = build("vision_keeper", db, mode="normal",
               allow=prompts.mode_tools("vision_keeper", "deliver"))
    with pytest.raises(ValueError, match="already a row of statements"):
        sb.call("problem.assert", id="s1", text="Split the bill between the people paying")
    with pytest.raises(ValueError, match="account of the whole program"):
        sb.call("problem.assert", id="how_it_works",
                text="The software splits the total bill by asking how many people "
                     "are paying and prints each person's share.")
    # Adding to the account keeps its words, and a behaviour under its own name lands.
    sb.call("problem.assert", id="how_it_works",
            text="The program is a tip calculator: it takes a total and a percentage, "
                 "prints the tip and the total with tip, and splits the bill between "
                 "the people paying.")
    out = sb.call("problem.assert", id="split_bill",
                  text="The program asks how many people are paying and prints each share.")
    assert out["id"] == "split_bill"


def test_a_whole_file_write_with_source_spans_lands(db, tmp_path):
    """
    tipsAI (2026-09-10): the Developer copied `start=0, end=-1` from
    `code.source` onto `code.write`, three sessions running, and each
    write was refused for the extra arguments.
    """
    root = tmp_path / "wt"; root.mkdir()
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    out = sb.call("code.write", path="script.py", text="def close_account(a):\n    return 1\n",
                  start=0, end=-1)
    assert out["bytes"]
    with pytest.raises(ValueError, match="writes the whole file"):
        sb.call("code.write", path="script.py", text="def x():\n    pass\n", start=10, end=20)


def test_a_dependency_manifest_is_fenced(db, tmp_path):
    """Audit item 1 (2026-09-10): what a manifest names, pip installs and runs."""
    root = tmp_path / "wt"; root.mkdir()
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    with pytest.raises(ValueError, match="dependency manifest"):
        sb.call("code.write", path="requirements.txt", text="requests\n")
    with pytest.raises(ValueError, match="dependency manifest"):
        sb.call("code.write", path="pyproject.toml", text="[project]\nname='x'\n")
    db.execute("UPDATE criteria SET text = ? WHERE id = 'c1'",
               ("closing an account records the closure with the httpx package",))
    db.commit()
    assert sb.call("code.write", path="requirements.txt", text="httpx\n")["bytes"]


def test_rota_commits_with_the_repositorys_hooks_off(tmp_path):
    """Audit item 3 (2026-09-10): a checkout's hooks run on commit with the
    user's rights, and rota commits what a model wrote."""
    import subprocess

    from rota.core import worktrees

    repo = tmp_path / "repo"; repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "t"], check=True)
    hooks = repo / ".git" / "hooks"; hooks.mkdir(exist_ok=True)
    marker = tmp_path / "hook-ran"
    (hooks / "pre-commit").write_text(f"#!/bin/sh\ntouch '{marker.as_posix()}'\n", encoding="utf-8")
    (hooks / "pre-commit").chmod(0o755)
    (repo / "a.py").write_text("x = 1\n", encoding="utf-8")
    assert worktrees.commit(repo, "first")
    assert not marker.exists()


def test_a_root_file_cannot_shadow_the_standard_library(db, tmp_path):
    """clickI (2026-09-10): `__future__.py` at the root broke every import."""
    root = tmp_path / "wt"; root.mkdir()
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    with pytest.raises(ValueError, match="standard-library module 'json'"):
        sb.call("code.write", path="json.py", text="def dumps(x):\n    return ''\n")
    assert sb.call("code.write", path="pkg_json.py", text="def dumps(x):\n    return ''\n")["bytes"]


def test_criteria_go_to_the_item_the_wake_named(db):
    """clickI (2026-09-10): woken for one item, the Terminologist wrote the
    criteria of another, three sessions running."""
    from rota.core.predicates import Wake
    from rota.roles import prompts

    db.execute("INSERT INTO items (id, text, kind, provenance, approval, approval_ver, "
               "version) VALUES ('i2','show the python version','in_scope','decided','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk2','i2','show python')")
    db.commit()
    sb = build("terminologist", db, mode="normal",
               wake=Wake(role="terminologist", kind="tick:criteria", refs=("i2",), detail="criteria"),
               allow=prompts.mode_tools("terminologist", "criteria"))
    with pytest.raises(ValueError, match="woken for 'i2', whose tickets are \['tk2'\]"):
        sb.call("criteria.specify", id="c_x", ticket_id="tk1", text="closing keeps invoices")


def test_an_escalation_over_a_removed_name_is_the_finding_restated(db, tmp_path):
    """The register (2026-09-10): the diff renamed calculate_tip, the finding
    said so, and llama escalated 5/5 instead of restoring the name."""
    root = tmp_path / "wt"; root.mkdir()
    (root / "main.py").write_text("def calculate_share(t, p, n):\n    return t / n\n",
                                  encoding="utf-8")
    db.execute("UPDATE batches SET worktree = ?, head_commit = 'abc' WHERE id = 'b1'", (str(root),))
    db.execute("INSERT INTO constraints (id, headline, provenance) VALUES "
               "('k1','calculate_tip is called by main','observed')")
    db.execute("INSERT INTO findings (id, batch_id, constraint_id, commit_sha, status, grain) "
               "VALUES ('f1','b1','k1','abc','violated','calculate_tip')")
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="normal",
               allow=prompts.mode_tools("developer", "finding_violated"))
    with pytest.raises(ValueError, match="no file in the worktree defines 'calculate_tip'"):
        sb.call("msg.escalate_architect", refs=["f1", "k1"])
    (root / "main.py").write_text("def calculate_tip(t, p):\n    return t * p\n",
                                  encoding="utf-8")
    assert sb.call("msg.escalate_architect", refs=["f1", "k1"])["id"]


def test_an_empty_commit_under_a_finding_names_the_signature_drift(db, tmp_path):
    """tipsAL (2026-09-10): display_results gained three required parameters
    and the Developer committed nothing three times, saying the constraint
    held."""
    import subprocess

    repo = tmp_path / "repo"; repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "t"], check=True)
    (repo / "main.py").write_text("def display_results(total, tip):\n    print(total, tip)\n",
                                  encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "base"], check=True)
    wt = tmp_path / "wt"; wt.mkdir()
    (wt / "main.py").write_text(
        "def display_results(total, tip, names, shares):\n    print(total, tip, names, shares)\n",
        encoding="utf-8")
    subprocess.run(["git", "-C", str(wt), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(wt), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(wt), "config", "user.name", "t"], check=True)
    subprocess.run(["git", "-C", str(wt), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(wt), "commit", "-q", "-m", "diff"], check=True)
    db.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)", (str(repo),))
    db.execute("UPDATE batches SET worktree = ?, head_commit = 'abc' WHERE id = 'b1'", (str(wt),))
    db.execute("INSERT INTO constraints (id, headline, provenance) VALUES "
               "('k1','display_results is called by main','observed')")
    db.execute("INSERT INTO constraint_bindings (constraint_id, grain, grain_kind, resolves) "
               "VALUES ('k1','main.py','path',1)")
    db.execute("INSERT INTO findings (id, batch_id, constraint_id, commit_sha, status, grain) "
               "VALUES ('f1','b1','k1','abc','violated','display_results')")
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="normal",
               allow=prompts.mode_tools("developer", "finding_violated"))
    with pytest.raises(ValueError, match="now requires names, shares.*Give names, shares defaults"):
        sb.call("code.commit", message="nothing")


def test_a_quoted_word_in_a_clarify_is_a_word_not_a_row(db):
    """tipsAM (2026-09-10): the ladder's clarify said the criterion names no
    term for 'share', and the door read 'share' as a row id."""
    from rota.roles import prompts

    sb = build("liaison", db, mode="normal",
               allow=prompts.mode_tools("liaison", "unresolved"))
    out = sb.call("msg.clarify_principal", refs=["c1"],
                  question="The criterion says 'invoices' but names no term for 'share'. "
                           "What is a share here?")
    assert out["id"]
    with pytest.raises(ValueError, match="names no row"):
        sb.call("msg.clarify_principal", refs=["c1"],
                question="Is 'tst_9' the right test, or 'c_77'?")


def test_a_new_batch_never_inherits_an_old_runs_branch(db, tmp_path):
    """clickI (2026-09-11): onboard --force wiped the database, not the
    repository; the old batch branch came back with the old run's files."""
    import subprocess

    from rota.core import worktrees

    repo = tmp_path / "repo"; repo.mkdir()
    for cmd in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(repo), *cmd], check=True)
    (repo / "main.py").write_text("x = 1\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "base"], check=True)
    # An old run's branch with a stray file on it.
    subprocess.run(["git", "-C", str(repo), "checkout", "-q", "-b", "batch/b1"], check=True)
    (repo / "__future__.py").write_text("", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "stray"], check=True)
    subprocess.run(["git", "-C", str(repo), "checkout", "-q", "-"], check=True)
    db.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)", (str(repo),))
    db.execute("UPDATE batches SET head_commit = NULL, worktree = NULL WHERE id = 'b1'")
    db.commit()
    path = worktrees.create(db, "b1")
    assert not (path / "__future__.py").exists()
    branches = subprocess.run(["git", "-C", str(repo), "branch", "--list", "batch/b1*"],
                              capture_output=True, text=True).stdout
    assert "batch/b1@" in branches


def test_the_tests_imports_exclude_the_stdlib_and_the_projects_packages(db, tmp_path):
    """clickI (2026-09-11): inherited tests import __future__, click and
    shutil, and every write of a new file was refused for missing modules."""
    root = tmp_path / "wt"; (root / "src" / "click").mkdir(parents=True)
    (root / "src" / "click" / "__init__.py").write_text("", encoding="utf-8")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE tests SET body = ? WHERE id = 'tst1'",
               ("from __future__ import annotations\nimport shutil\nimport click\n"
                "from click.testing import CliRunner\ndef test_x():\n    assert click\n",))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    assert sb.call("code.write", path="echo_json.py",
                   text="def close_account(a):\n    return 1\n")["bytes"]


def test_a_bare_surface_must_be_defined_somewhere_in_the_tree(db, tmp_path):
    """clickI (2026-09-11): surface `echo_json`, definition `echo_json_helper`,
    and the commit went through because a bare name was never checked."""
    import subprocess

    root = tmp_path / "wt"; root.mkdir()
    subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "t"], check=True)
    (root / "script.py").write_text("def echo_json_helper(f):\n    return f\n", encoding="utf-8")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE criteria SET surface_refs = '[\"echo_json\"]' WHERE id = 'c1'")
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    with pytest.raises(ValueError, match="does not define echo_json"):
        sb.call("code.commit", message="helper")
    (root / "script.py").write_text("def echo_json(obj):\n    return obj\n", encoding="utf-8")
    assert sb.call("code.commit", message="helper")["committed"]


def test_a_new_module_goes_into_the_src_package(db, tmp_path):
    """clickI (2026-09-11): main.py at the root of a src-layout library."""
    root = tmp_path / "wt"; (root / "src" / "click").mkdir(parents=True)
    (root / "src" / "click" / "__init__.py").write_text("", encoding="utf-8")
    (root / "tests").mkdir()
    nl = chr(10)
    (root / "pyproject.toml").write_text(
        "[build-system]" + nl + "requires=['flit_core']" + nl + "build-backend='flit_core.buildapi'" + nl
        + "[project]" + nl + "name='click'" + nl, encoding="utf-8")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    with pytest.raises(ValueError, match="src/click/echo_json.py"):
        sb.call("code.write", path="echo_json.py", text="def echo_json(o):\n    return o\n")
    assert sb.call("code.write", path="src/click/echo_json.py",
                   text="def echo_json(o):\n    return o\n")["bytes"]
