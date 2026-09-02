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
    with pytest.raises(ValueError, match="drops close_account, which the batch's tests import"):
        sb.call("code.write", path="script.py", text="def run():\n    return 1\n")
    # Dropping a function nobody imports is the Developer's business.
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
