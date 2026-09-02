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


def test_a_quoted_test_is_the_testers_dispute(db):
    sb = build("critic", db, batch_id="b1", mode="review")
    with pytest.raises(ValueError, match=r"challenge_tester\(refs=\['c1', 'tst1'\]"):
        sb.call("msg.challenge_developer", refs=["c1", "tst1"],
                quotes=["closing an account leaves its invoices in place",
                        "assert close_account('a1') is not None"])
    # The same evidence on the right channel goes through.
    sb.call("msg.challenge_tester", refs=["c1", "tst1"],
            quotes=["closing an account leaves its invoices in place",
                    "assert close_account('a1') is not None"])


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
