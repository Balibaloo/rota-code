"""Night 46 (2026-09-14): the Tester and the Developer read every session
they were given and still could not act, because the wake or the refusal
withheld the one fact each needed."""
import pytest

from rota.core.db import init_db
from rota.core import predicates
from rota.core.runner import push_working_set, run_session
from rota.core.sandbox import build
from rota.core.scheduler import Wake
from rota.llm.llm import Completion, Pins, ScriptedBackend
from rota.roles import prompts


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, "
                 "approval_ver, version) VALUES ('i1','closing keeps invoices',"
                 "'in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','i1','close an account')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('c1','tk1','closing an account leaves its invoices in place')")
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) VALUES "
                 "('b1','i1','running','abc123')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                 "VALUES ('tst1','b1','c1','test_close.py',"
                 "\"assert close_account('a1') is not None\")")
    conn.commit()
    return conn


def _encode(sb, body):
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    return sb.call("tests.encode", id="tst_new", criterion_id="c1",
                   path="tests/test_greet.py", body=body)


def test_the_fix_wake_pushes_the_red_tests_and_the_code_they_call(tmp_path):
    """34 inherited bodies, 467,000 characters, cut at 20,000: the failing
    test and what the harness said never arrived."""
    root = tmp_path / "proj"; (root / "src" / "click").mkdir(parents=True)
    (root / "src" / "click" / "utils.py").write_text(
        "import json\n\n\ndef echo(message):\n    print(message)\n\n\n"
        "def echo_json(obj, indent=2):\n    print(json.dumps(obj, indent=indent))\n")
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('project_root', ?)", (str(root),))
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) VALUES "
               "('echo_json','Add an echo_json helper','in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','echo_json','add echo_json')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c1','tk1','echo_json prints JSON')")
    db.execute("INSERT INTO batches (id, item_id, status, head_commit) VALUES ('b1','echo_json','running','abc123')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    db.execute("INSERT INTO code_index (grain, grain_kind) VALUES ('src/click/utils.py','path')")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES "
               "('tst_red','b1','c1','tests/test_echo_json.py',"
               "'from click.utils import echo_json\n\ndef test_x(capsys):\n    echo_json({})\n    assert capsys.readouterr().out == \"{}\"')")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES "
               "('inh_1','b1',NULL,'tests/test_basic.py','def test_basic():\n    assert True')")
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, output, attempt) VALUES "
               "('r1','b1','tst_red','abc123','fail','AssertionError: assert \"{}\\n\" == \"{}\"',1)")
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, output, attempt) VALUES "
               "('r2','b1','inh_1','abc123','pass','1 passed',1)")
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    pushed = push_working_set("developer", sb, Wake("developer", "tick:tests_failing", refs=("b1",)))
    red = pushed["tests.load"]["the batch's tests, not passing"]
    assert [r["id"] for r in red] == ["tst_red"]
    assert "AssertionError" in red[0]["said"]
    assert pushed["tests.load"]["passing, not shown"] == "1 test(s)"
    assert "code.probe" not in pushed, "an empty probe is a note, not a read"
    span = pushed["code.source"]["src/click/utils.py::echo_json"]
    assert "def echo_json" in span["text"]
    assert "def echo(" not in span["text"], "the span is the definition, not the file"


def _red_test_push(db, messages=()):
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, "
               "output, attempt) VALUES ('r1','b1','tst1','abc123','fail',"
               "'NameError: close_account',1)")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES "
               "('tst2','b1','c1','test_other.py','def test_y():\n    assert True')")
    for row in messages:
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                   "body_refs, body_text, seq, status, cause_id) VALUES "
                   "(?,?,?,?,?,?,?,?,?,?)", row)
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    return push_working_set("developer", sb, Wake("developer", "tick:tests_failing",
                                                  refs=("b1",)))["tests.load"]


def test_the_fix_wake_shows_the_thread_on_a_red_test(db):
    """Night 106 (2026-10-02): no tick wake carried m109 to m115, and the
    seat sent the challenge again at attempts 4 to 8 (frame 111)."""
    shown = _red_test_push(db, [
        ("m1", "th", "developer", "tester", "challenge", '["c1", "tst1"]',
         "the test asserts what c1 never says", 1, "answered", None),
        ("m2", "th", "tester", "developer", "answer", '["c1", "tst1"]',
         "closing an account leaves its invoices in place", 2, "open", "m1"),
        ("m3", "th2", "developer", "architect", "escalate", '["tst1"]',
         None, 3, "answered", None),
        ("m4", "th2", "architect", "developer", "answer", '["c1"]',
         None, 4, "open", "m3"),
        ("m5", "th3", "developer", "architect", "escalate", '["c1", "tst1"]',
         None, 5, "open", None),
        ("m6", "th4", "developer", "tester", "challenge", '["c1", "tst2"]',
         None, 6, "open", None),
        ("m7", "th5", "developer", "tester", "challenge", '["tst1"]',
         None, 7, "answered", None),
        ("m8", "th5", "tester", "developer", "answer", '["tst1"]',
         "x" * 700, 8, "open", "m7"),
        # Night 108 (2026-10-02): the Architect's own challenge on the test
        # is not the Developer's thread.
        ("m9", "th6", "architect", "vision_keeper", "challenge", '["c1", "tst1"]',
         None, 9, "open", None),
    ])
    # First, because the push cut removes the last key first (dad15d9 review).
    assert list(shown)[:3] == ["challenges and escalations on these tests",
                               "after these", "the batch's tests, not passing"]
    thread = shown["challenges and escalations on these tests"]
    assert thread[:3] == [
        {"id": "m1", "verb": "challenge", "to": "tester", "test": "tst1",
         "answer": "closing an account leaves its invoices in place"},
        {"id": "m3", "verb": "escalate", "to": "architect", "test": "tst1",
         "answer": "answered with no words"},
        {"id": "m5", "verb": "escalate", "to": "architect", "test": "tst1",
         "answer": "not answered yet"},
    ]
    assert [t["id"] for t in thread] == ["m1", "m3", "m5", "m7"]
    long = thread[3]["answer"]
    assert long.startswith("x" * 600 + "\nCUT the answer m8: 100 of 700 characters are not shown.")
    assert "x" * 601 not in long


def test_the_fix_wake_with_no_thread_pushes_no_thread_key(db):
    shown = _red_test_push(db)
    assert "the batch's tests, not passing" in shown
    assert "challenges and escalations on these tests" not in shown
    assert "after these" not in shown


def _thread_answer(db, status, answer=None):
    rows = [("m97", "th", "developer", "architect", "escalate", '["c1", "tst1"]',
             None, 1, status, None)]
    if answer is not None:
        rows.append(("m98", "th", "architect", "developer", "answer",
                     '["c1", "tst1"]', answer, 2, "open", "m97"))
    shown = _red_test_push(db, rows)
    return shown, shown["challenges and escalations on these tests"][0]["answer"]


@pytest.mark.parametrize("status", ["answered", "unresolved"])
def test_a_closed_prior_with_no_answer_row_reads_closed_in_the_thread(db, status):
    """Night 111 (2026-10-03): the thread said m97 was "not answered yet",
    and the door said that m97 was answered (frame 111)."""
    _, answer = _thread_answer(db, status)
    assert answer == f"closed ({status}) with no answer row"


def test_an_open_prior_with_no_answer_row_is_not_answered_yet(db):
    _, answer = _thread_answer(db, "open")
    assert answer == "not answered yet"


def test_an_answer_row_with_no_words_is_answered_with_no_words(db):
    _, answer = _thread_answer(db, "unresolved", answer="")
    assert answer == "answered with no words"


_AFTER_THESE = ("A listed message that is answered or closed is refused if sent "
                "again on these refs. Make one real change to the code the test "
                "calls, or end the session with no call.")


@pytest.mark.parametrize("status,answer", [("answered", None),
                                           ("open", "the test stands")])
def test_the_thread_carries_the_way_out_after_it(db, status, answer):
    """Night 111 (2026-10-03): by turn 17 the window had dropped both
    refusals, and s252 sent the challenge a third time (frame 111)."""
    shown, _ = _thread_answer(db, status, answer)
    keys = list(shown)
    assert keys[:2] == ["challenges and escalations on these tests", "after these"]
    assert shown["after these"] == _AFTER_THESE


def test_a_thread_where_every_entry_waits_adds_no_way_out(db):
    shown, answer = _thread_answer(db, "open")
    assert answer == "not answered yet"
    assert list(shown)[:2] == ["challenges and escalations on these tests",
                               "the batch's tests, not passing"]
    assert "after these" not in shown


@pytest.mark.parametrize("bad", ["not json", "", '{"a": "tst1"}'])
def test_a_corrupt_refs_row_does_not_hide_the_thread(db, bad):
    """The review of dad15d9 (2026-10-02): one row whose body_refs was not
    JSON made json_each raise for every test, and the key never appeared.
    A JSON object's values are no refs either."""
    shown = _red_test_push(db, [
        ("m1", "th", "developer", "tester", "challenge", bad, None, 1, "open", None),
        ("m2", "th2", "developer", "tester", "challenge", '["c1", "tst1"]',
         None, 2, "open", None),
    ])
    assert shown["challenges and escalations on these tests"] == [
        {"id": "m2", "verb": "challenge", "to": "tester", "test": "tst1",
         "answer": "not answered yet"}]


def test_the_missing_tests_wake_names_the_criteria_without_a_test(db):
    """Shown six criteria and three tests, the Tester re-encoded the three
    that had tests and routed one that had none."""
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c2','tk1','the account is tombstoned')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c3','tk1','the owner is told')")
    db.commit()
    wakes = predicates.tests_missing(db)
    assert len(wakes) == 1
    assert wakes[0].refs == ("b1",)
    assert wakes[0].detail == "without a test: c2, c3"


def test_a_tick_wake_says_its_detail_to_the_role(db):
    from rota.core.runner import build_prompt
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c2','tk1','the account is tombstoned')")
    db.commit()
    wake = predicates.tests_missing(db)[0]
    sb = build("tester", db, batch_id="b1", mode="tests_missing",
               allow=prompts.mode_tools("tester", "tests_missing"))
    _system, user = build_prompt("tester", sb, wake, {}, "MODE: tests_missing")
    assert "without a test: c2" in user


def test_a_library_module_never_imported_gets_the_line_to_add(db):
    """`json.loads` with no `import json`: the hint said to import the
    function the criterion names, which the test had already done."""
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    with pytest.raises(ValueError, match=r"Add the line `import json`"):
        _encode(sb, "from script import close_account\n"
                    "def test_x():\n    assert json.loads(close_account('a1')) == {}")


def test_every_invented_literal_is_named_in_one_refusal(db):
    """'key', then 'nested', then 'array': one literal per turn, each logged
    and re-sent, until the session ran out. Frame 204: the door stages one
    `invented` row that names every literal, and admits the encode."""
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    _encode(sb, "from script import close_account\n"
                "def test_x():\n    assert close_account('alpha_corp') == 'beta_corp'")
    (row,) = [w for w in sb.ctx.writes if w[0] == "ledger"]
    text = row[2]["default_taken"]
    import re
    assert re.search(r"assumes \w+_corp and \w+_corp where the material is silent", text), text


def test_a_criterion_that_names_the_file_asks_for_the_definition_there(db, tmp_path):
    """L1-DV-build-a-clear-criterion (2026-09-14): 'money(1999) returns
    $19.99 from src/notify/formatting.py', templates.py already held a
    money, and the duplicate door sent the Developer to the wrong file."""
    root = tmp_path / "wt"; (root / "src" / "notify").mkdir(parents=True)
    (root / "src" / "notify" / "templates.py").write_text(
        "def money(cents):\n    return str(cents)\n\n\ndef render(t):\n    return t\n")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE criteria SET text = ? WHERE id = 'c1'",
               ("money(1999) returns '$19.99' from src/notify/formatting.py",))
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    assert sb.call("code.write", path="src/notify/formatting.py",
                   text="def money(cents):\n    return f'${cents / 100:.2f}'\n")["bytes"]
    with pytest.raises(ValueError, match="already defines render"):
        sb.call("code.write", path="src/notify/other.py",
                text="def render(t):\n    return t.upper()\n")


@pytest.fixture
def vk_db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO entries (id, author, text, ts_order) "
                 "VALUES ('u1','principal','let users delete their account',1)")
    # Frame 303: a deliver has the principal's message as its cause, as on
    # a night. A statement ref would join the refs of every report.
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
                 "VALUES ('m0','t1','principal','liaison','converse',0)")
    conn.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
                 "verb, seq) VALUES ('m1','m0','t1','liaison','vision_keeper',"
                 "'deliver',1)")
    return conn


def _vk():
    return Wake(role="vision_keeper", kind="message", message_id="m1", detail="deliver")


def test_a_refusal_on_a_multi_call_turn_names_the_call(vk_db):
    """Six encodes a turn, three refused, and no way to tell which three."""
    backend = ScriptedBackend([
        "TOOL: problem.assert(id='i1', text='users can delete their account', kind='in_scope')\n"
        "TOOL: problem.assert(id='i2', text='and export it', kind='bogus_kind')",
        "Done.",
    ])
    outcome = run_session(vk_db, _vk(), backend=backend, pins=Pins(model="scripted"))
    assert outcome.committed, outcome.errors
    second = backend.calls[1][1]
    assert "ERROR problem.assert(id='i2'):" in second, second[-1500:]
    assert "ERROR problem.assert(id='i1')" not in second


def test_a_cut_reply_does_not_also_report_the_cut_call_as_a_parse_error(vk_db):
    """The parse error's own hint ("put it between triple quotes") was
    followed literally, and the next four encodes arrived as a docstring."""

    class Cut(ScriptedBackend):
        def complete(self, system, user, pins, tools=None):
            c = super().complete(system, user, pins, tools)
            if len(self.calls) == 1:
                return Completion(text=c.text, pins=pins, backend=self.name,
                                  raw={"done_reason": "length"})
            return c

    backend = Cut([
        "TOOL: problem.assert(id='i1', text='users can delete their account', kind='in_scope')\n"
        "TOOL: problem.assert(id='i2', text='and export their data before the",
        "Done.",
    ])
    outcome = run_session(vk_db, _vk(), backend=backend, pins=Pins(model="scripted"))
    assert outcome.committed, outcome.errors
    second = backend.calls[1][1]
    # Frame 121's diff review, finding 2: the line says where the cut fell.
    assert ("ERROR reply cut: your reply was cut at the output budget before "
            "it ended. The cut fell inside the last call, so that call did not "
            "run. The results of the calls before it that ran follow. Send less "
            "in one reply: one or two calls, then read their results.") in second, \
        second[-1500:]
    assert "nothing was written" not in second
    assert "unterminated argument list" not in second, second[-1500:]
    assert vk_db.execute("SELECT COUNT(*) n FROM items").fetchone()["n"] == 1, "the whole call before the cut ran"


class _CutFirst(ScriptedBackend):
    """The first reply stops at the output budget."""

    def complete(self, system, user, pins, tools=None):
        c = super().complete(system, user, pins, tools)
        if len(self.calls) == 1:
            return Completion(text=c.text, pins=pins, backend=self.name,
                              raw={"done_reason": "length"})
        return c


def test_a_cut_reply_whose_last_call_is_whole_says_the_cut_broke_no_call(vk_db):
    """
    Frame 121's diff review, finding 2. In 39 of 77 cut events of nights
    113 to 119 the last parsed call was whole, and 29 show an `OK` line for
    it. The line says that the cut broke no call, and never that nothing was
    written.
    """
    backend = _CutFirst([
        "TOOL: problem.assert(id='i1', text='users can delete their account', kind='in_scope')\n"
        "I will now explain at length why the account matters and",
        "Done.",
    ])
    outcome = run_session(vk_db, _vk(), backend=backend, pins=Pins(model="scripted"))
    assert outcome.committed, outcome.errors
    second = backend.calls[1][1]
    assert ("ERROR reply cut: your reply was cut at the output budget before "
            "it ended. The cut fell after the last call, so it broke no call. "
            "The results of the calls that ran follow. Send less in one reply: "
            "one or two calls, then read their results.") in second, second[-1500:]
    assert "OK problem.assert" in second, second[-1500:]
    assert "the last call did not run" not in second
    assert "nothing was written" not in second
    assert vk_db.execute("SELECT COUNT(*) n FROM items").fetchone()["n"] == 1


@pytest.mark.parametrize("reply", [
    "I think about the account. " * 400,
    # A bare call, with no `TOOL:` marker, cut in the middle parses to no
    # call (the diff review, finding 4). One sentence holds for both shapes.
    "I record it.\nproblem.assert(id='i1', text='" + "users can delete their account " * 300,
], ids=["prose", "a bare call cut in the middle"])
def test_a_cut_reply_with_no_whole_call_says_no_call_ran_in_both_lines(vk_db, reply):
    """
    Frame 121's interview, C and B1. Night 119's s263 read `CUT your wake`
    on its own prose reply and found no next call. The retry runs only when
    the cut reply held no whole call, so the cut note and the ERROR line both
    say that no call ran, and neither says that a last call was lost.
    """
    backend = _CutFirst([reply, "Done."])
    run_session(vk_db, _vk(), backend=backend, pins=Pins(model="scripted"))
    second = backend.calls[1][1]
    total = len(reply)
    assert (f"\nCUT your reply: {total - 4000:,} of {total:,} characters are "
            f"not shown. The first 4,000 characters stand above. No call in "
            f"your reply ran. Send one call, and keep your prose short.") \
        in second, second[-600:]
    assert ("ERROR reply cut: your reply was cut at the output budget before "
            "it ended. It held no whole call, so no call ran and nothing was "
            "written. Send one call, or end with one sentence.") in second
    assert "CUT your wake" not in second
    assert "the last call did not run" not in second
    assert vk_db.execute("SELECT COUNT(*) n FROM items").fetchone()["n"] == 0


def test_the_fix_wake_header_keeps_its_bytes_beside_the_summary(db):
    """
    Frame 121, pass 4. A header that named `tests.load` took two green
    cases to 3 of 5, and their runs called `tests.load` 2 to 5 times. So a
    wake that pushes the summary keeps the old sentence byte for byte.
    """
    from rota.core.runner import build_prompt
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, "
               "output, attempt) VALUES ('r1','b1','tst1','abc123','fail',"
               "'NameError: close_account',1)")
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    wake = Wake("developer", "tick:tests_failing", refs=("b1",))
    pushed = push_working_set("developer", sb, wake)
    assert isinstance(pushed["tests.load"], dict), "the push is not the summary"
    _system, user = build_prompt("developer", sb, wake, pushed, "MODE: tests_failing")
    assert ("\nAlready run for you, with the results below. Calling any of "
            "these again returns the same thing and costs you a turn:\n") in user
    assert "summary below" not in user


def test_a_bare_list_of_refs_may_hold_a_path():
    """click night 47 (2026-09-14): the Liaison copied 44 observed refs
    unbracketed, ending `., src/click`; the slash broke the run and the
    present was refused three times to quarantine."""
    from rota.llm import toolproto
    calls = toolproto.extract("TOOL: msg.present_principal(refs=argument, choice, ., src/click, text='the page')")
    call = calls[0]
    assert not isinstance(call, toolproto.ToolError), getattr(call, "reason", call)
    assert call.args["refs"] == ["argument", "choice", ".", "src/click"], call.args


def test_a_bare_list_of_refs_may_hold_a_second_sense_id():
    """click night 84 (2026-09-17): the survey of `src/click` wrote
    second-sense rows like `group#src_click`; the Liaison copied 56 refs
    bare, the rewrite never matched on the hash, and the present was
    refused three times to quarantine before session 1."""
    from rota.llm import toolproto
    calls = toolproto.extract(
        "TOOL: msg.present_principal(refs=argument, argument#src_click, ., src/click, round_no=1)")
    call = calls[0]
    assert not isinstance(call, toolproto.ToolError), getattr(call, "reason", call)
    assert call.args["refs"] == ["argument", "argument#src_click", ".", "src/click"], call.args
    assert call.args["round_no"] == 1, call.args


def test_the_fix_wake_separates_the_projects_own_tests_and_pushes_the_diff(tmp_path):
    """click night 47 (2026-09-14): 19 of click's own tests failed at the
    Developer's commit; the push read their imports and pushed 20,000
    characters of types.py; the Developer wrote an essay about Choice."""
    import subprocess
    root = tmp_path / "proj"; (root / "src" / "click").mkdir(parents=True)
    utils = root / "src" / "click" / "utils.py"
    utils.write_text('def echo(message):\n    print(message)\n')
    git = ["git", "-c", "user.email=t@t", "-c", "user.name=t"]
    subprocess.run([*git, "init", "-q"], cwd=root, check=True)
    subprocess.run([*git, "add", "."], cwd=root, check=True)
    subprocess.run([*git, "commit", "-q", "-m", "base"], cwd=root, check=True)
    utils.write_text('def echo(message):\n    return message\n')
    subprocess.run([*git, "commit", "-q", "-am", "broke echo"], cwd=root, check=True)
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('project_root', ?)", (str(root),))
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) VALUES "
               "('echo_json','Add an echo_json helper','in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','echo_json','add echo_json')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c1','tk1','echo_json prints JSON')")
    db.execute("INSERT INTO batches (id, item_id, status, head_commit, worktree) VALUES "
               "('b1','echo_json','running','abc123',?)", (str(root),))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    db.execute("INSERT INTO code_index (grain, grain_kind) VALUES ('src/click/utils.py','path')")
    body = 'from click.utils import echo\n\ndef test_echo(capsys):\n    echo(1)\n    assert capsys.readouterr().out'
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES ('inh_1','b1',NULL,'tests/test_echo.py',?)", (body,))
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, output, attempt) VALUES "
               "('r1','b1','inh_1','abc123','fail','AssertionError',1)")
    # Frame 207: the sentence "passed before this batch" needs a base run.
    db.execute("INSERT INTO config (key, value) VALUES "
               "('base_run:b1', '{\"inh_1\": {\"result\": \"pass\"}}')")
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    pushed = push_working_set("developer", sb, Wake("developer", "tick:tests_failing", refs=("b1",)))
    shown = pushed["tests.load"]
    assert "the batch's tests, not passing" not in shown
    assert [r["id"] for r in shown["the project's own tests, not passing at your commit"]] == ["inh_1"]
    assert "Your diff broke them" in shown["what that means"]
    assert "code.source" not in pushed, "the project's own tests do not pull their imports' source"
    assert "-    print(message)" in pushed["code.diff"]["diff"]


def test_a_challenge_hint_never_names_a_test_with_no_criterion(db):
    """click night 47 (2026-09-14): "send refs=['None', 'inh_5f7b1750']",
    sent exactly that, four turns."""
    body = 'def test_x():\n    assert False'
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES ('inh_1','b1',NULL,'tests/test_x.py',?)", (body,))
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, output, attempt) VALUES "
               "('r1','b1','inh_1','abc123','fail','AssertionError',1)")
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", refs=["tk1", "inh_1"], quotes="x")
    text = str(exc.value)
    assert "'None'" not in text, text
    assert "project's own" in text and "code.diff" in text, text


def test_a_write_that_changes_a_definition_no_criterion_names_lands_with_a_note(tmp_path):
    """Click nights 47 and 48 (2026-09-14): asked for echo_json next to echo,
    the Developer's span write replaced echo with a simplified copy; 19 of
    click's own tests failed; nine fix rounds called it unrelated. Frame 286:
    law 12 permits the write, and the commit records it for the Architect."""
    proj = tmp_path / "proj"; (proj / "src" / "click").mkdir(parents=True)
    original = "import sys\n\n\ndef echo(message, nl=True):\n    sys.stdout.write(str(message) + (chr(10) if nl else ''))\n    sys.stdout.flush()\n"
    (proj / "src" / "click" / "utils.py").write_text(original)
    wt = tmp_path / "wt"; (wt / "src" / "click").mkdir(parents=True)
    (wt / "src" / "click" / "utils.py").write_text(original)
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('project_root', ?)", (str(proj),))
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) VALUES "
               "('i1','Add echo_json next to echo','in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1','add echo_json next to echo')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) VALUES "
               "('c1','tk1','echo_json prints an object as JSON','[\"src/click/utils.py::echo_json\"]')")
    db.execute("INSERT INTO batches (id, item_id, status, worktree) VALUES ('b1','i1','running',?)", (str(wt),))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    simplified = 'import sys\n\n\ndef echo(message):\n    print(message)\n\n\ndef echo_json(obj, indent=2):\n    import json\n    print(json.dumps(obj, indent=indent))\n'
    out = sb.call("code.write", path="src/click/utils.py", text=simplified)
    assert out["bytes"], "the write lands"
    note = out["not named"]
    assert "changes echo, and no criterion of the batch names it" in note, note
    assert "Architect's judgement" in note and "start=6, end=6" in note, note
    assert (wt / "src" / "click" / "utils.py").read_text() == simplified
    added = original + '\n\ndef echo_json(obj, indent=2):\n    import json\n    print(json.dumps(obj, indent=indent))\n'
    assert sb.call("code.write", path="src/click/utils.py", text=added)["bytes"]
    # After a bad write landed elsewhere, the restoring write passes: echo back to the project's own, echo_json kept.
    assert sb.call("code.write", path="src/click/utils.py", text=added)["bytes"], "restoring the project's own echo passes"


_ECHO = "import sys\n\n\ndef echo(message, nl=True):\n    sys.stdout.write(str(message))\n"
_ECHO_JSON = "\n\ndef echo_json(obj):\n    print(obj)\n"


def _unnamed_batch(tmp_path):
    """A project repository, a batch worktree forked from it, a prediction
    of utils.py and one criterion that names echo_json only."""
    import subprocess

    def git(where, *args):
        subprocess.run(["git", "-C", str(where), "-c", "user.name=t",
                        "-c", "user.email=t@t", *args], check=True, capture_output=True)
    proj = tmp_path / "proj"; (proj / "src" / "click").mkdir(parents=True)
    git(proj, "init", "-q")
    (proj / "src" / "click" / "utils.py").write_text(_ECHO)
    git(proj, "add", "-A")
    git(proj, "commit", "-q", "-m", "base")
    wt = tmp_path / "wt"
    git(proj, "worktree", "add", "-q", "-b", "batch/b1", str(wt))
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('project_root', ?)", (str(proj),))
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) VALUES "
               "('i1','Add echo_json next to echo','in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1','add echo_json')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) VALUES "
               "('c1','tk1','echo_json prints an object','[\"src/click/utils.py::echo_json\"]')")
    db.execute("INSERT INTO batches (id, item_id, status, worktree) VALUES ('b1','i1','running',?)", (str(wt),))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind) VALUES ('b1','src/click/utils.py','path')")
    db.commit()
    return proj, wt, db, git


def test_the_commit_records_an_unnamed_definition_as_a_stray_the_architect_judges(tmp_path):
    """Frame 286: utils.py was predicted, so the path-grain detector saw
    nothing. The changed echo is a stray at definition grain, and the
    Architect's judgement on that grain closes it."""
    _proj, _wt, db, _git = _unnamed_batch(tmp_path)
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    changed = "import sys\n\n\ndef echo(message):\n    print(message)\n" + _ECHO_JSON
    assert "not named" in sb.call("code.write", path="src/click/utils.py", text=changed)
    out = sb.call("code.commit", message="echo_json beside echo")
    assert out["committed"], out
    assert out["definitions outside the criteria"] == ["src/click/utils.py::echo"], out
    assert "outside_prediction" not in out, "the file itself was predicted"
    rows = [w[2] for w in sb.ctx.writes if w[0] == "touch_strays"]
    assert [(r["path"], r["status"]) for r in rows] == [("src/click/utils.py::echo", "open")]
    sha = out["head_commit"]
    db.execute("UPDATE batches SET head_commit = ? WHERE id = 'b1'", (sha,))
    db.execute("INSERT INTO touch_strays (batch_id, commit_sha, path, status) VALUES "
               "('b1', ?, 'src/click/utils.py::echo', 'open')", (sha,))
    db.commit()
    arch = build("architect", db, mode="touch_strayed",
                 allow=prompts.mode_tools("architect", "touch_strayed"))
    judged = arch.call("batches.judge_touch", batch_id="b1",
                       foreseen=["src/click/utils.py::echo"], reason="echo needed the flag")
    assert judged["foreseen"] == ["src/click/utils.py::echo"] and "ignored" not in judged
    status = {w[2]["path"]: w[2]["status"] for w in arch.ctx.writes if w[0] == "touch_strays"}
    assert status == {"src/click/utils.py::echo": "foreseen"}
    touch = [w[2] for w in arch.ctx.writes if w[0] == "batch_touch"]
    assert [(t["grain"], t["grain_kind"]) for t in touch] == [("src/click/utils.py::echo", "symbol")]


def test_a_symbol_grain_with_a_leading_dot_slash_judges_its_definition_row(tmp_path):
    """Frame 286, review 1, low 1: `./src/click/utils.py::echo` matched no
    row. Frame 228 saw the `./` shape from the Architect."""
    _proj, _wt, db, _git = _unnamed_batch(tmp_path)
    db.execute("UPDATE batches SET head_commit = 'abc' WHERE id = 'b1'")
    db.execute("INSERT INTO touch_strays (batch_id, commit_sha, path, status) VALUES "
               "('b1', 'abc', 'src/click/utils.py::echo', 'open')")
    db.commit()
    arch = build("architect", db, mode="touch_strayed",
                 allow=prompts.mode_tools("architect", "touch_strayed"))
    judged = arch.call("batches.judge_touch", batch_id="b1",
                       mistakes=["./src/click/utils.py::echo"], reason="a second copy")
    assert judged["mistakes"] == ["src/click/utils.py::echo"] and "ignored" not in judged, judged


def test_a_batch_with_no_worktree_reads_the_root_file_as_the_base(tmp_path):
    """Frame 286, review 1, low 3: a merged batch has no worktree, as
    code_diff reaches it. The root file holds the base, so a restore of the
    root's source changes no name."""
    from rota.roles import api
    proj, _wt, db, _git = _unnamed_batch(tmp_path)
    db.execute("UPDATE batches SET worktree = NULL WHERE id = 'b1'")
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    changed = "import sys\n\n\ndef echo(message):\n    print(message)\n"
    assert api._changed_unnamed_defs(sb.ctx, "src/click/utils.py", changed, _ECHO + _ECHO_JSON) == []


def test_a_write_that_restores_the_base_definition_lands_with_no_note_and_no_stray(tmp_path):
    """Night 154's s130: the door read the project root's working file, not
    the batch's base, so a restore of the base's own definition read as a
    change. The base is the fork, read as frame 220 reads it."""
    proj, wt, db, git = _unnamed_batch(tmp_path)
    # The batch's first commit changed echo. The root's working file moved too.
    (wt / "src" / "click" / "utils.py").write_text("import sys\n\n\ndef echo(message):\n    print(message)\n")
    git(wt, "commit", "-q", "-am", "batch 1")
    (proj / "src" / "click" / "utils.py").write_text("import sys\n\n\ndef echo(m):\n    return m\n")
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    out = sb.call("code.write", path="src/click/utils.py", text=_ECHO + _ECHO_JSON)
    assert out["bytes"] and "not named" not in out, out
    committed = sb.call("code.commit", message="echo back, echo_json beside it")
    assert committed["committed"], committed
    assert "definitions outside the criteria" not in committed, committed
    assert [w for w in sb.ctx.writes if w[0] == "touch_strays"] == []


def test_the_diff_names_the_definitions_the_batch_changed_unasked(tmp_path):
    import subprocess
    proj = tmp_path / "proj"; (proj / "src").mkdir(parents=True)
    original = 'def echo(m):\n    print(m)\n'
    (proj / "src" / "utils.py").write_text(original)
    wt = tmp_path / "wt"; (wt / "src").mkdir(parents=True)
    (wt / "src" / "utils.py").write_text(original)
    git = ["git", "-c", "user.email=t@t", "-c", "user.name=t"]
    subprocess.run([*git, "init", "-q"], cwd=wt, check=True)
    subprocess.run([*git, "add", "."], cwd=wt, check=True)
    subprocess.run([*git, "commit", "-q", "-m", "base"], cwd=wt, check=True)
    (wt / "src" / "utils.py").write_text('def echo(m):\n    return m\n\n\ndef echo_json(o):\n    print(o)\n')
    subprocess.run([*git, "commit", "-q", "-am", "change"], cwd=wt, check=True)
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('project_root', ?)", (str(proj),))
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) VALUES "
               "('i1','x','in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1','x')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) VALUES ('c1','tk1','echo_json prints','[\"src/utils.py::echo_json\"]')")
    db.execute("INSERT INTO batches (id, item_id, status, head_commit, worktree) VALUES ('b1','i1','running','abc',?)", (str(wt),))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    out = sb.call("code.diff")
    assert out["definitions this batch changed that no criterion names"] == {"src/utils.py": ["echo"]}, out


def test_a_relative_import_protects_what_a_rewrite_would_drop(tmp_path):
    """Click night 49, walk 2 (2026-09-14): a span write cut termui.py after
    confirm, dropping style and nineteen more; core.py imports them with
    `from .termui import style`, which the importer scan did not read; all
    43 tests failed at import for the rest of the batch."""
    wt = tmp_path / "wt"; (wt / "src" / "click").mkdir(parents=True)
    (wt / "src" / "click" / "termui.py").write_text('def confirm(text):\n    return True\n\n\ndef style(text):\n    return text\n')
    (wt / "src" / "click" / "core.py").write_text('from .termui import style\n\n\ndef render(t):\n    return style(t)\n')
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) VALUES "
               "('i1','confirm takes a default_on_eof flag','in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1','the flag')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) VALUES ('c1','tk1','confirm returns the default on EOF','[\"src/click/termui.py::confirm\"]')")
    db.execute("INSERT INTO batches (id, item_id, status, worktree) VALUES ('b1','i1','running',?)", (str(wt),))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    cut = 'def confirm(text, default_on_eof=False):\n    return default_on_eof\n'
    with pytest.raises(ValueError, match=r"drops style"):
        sb.call("code.write", path="src/click/termui.py", text=cut)


def test_a_test_that_closes_stdin_is_refused(db):
    """Click night 50, walk 2 (2026-09-14): two EOF tests did sys.stdin.close()
    and failed against a correct confirm() for ten rounds."""
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    with pytest.raises(ValueError, match="closes sys.stdin"):
        _encode(sb, "import sys\nfrom script import close_account\ndef test_x():\n    sys.stdin.close()\n    assert close_account('a1') is None")


def test_the_developer_commit_leaves_the_testers_files_out_and_the_merge_delivers_them(tmp_path):
    """Click night 50 (2026-09-14): a first encode was committed and merged,
    the Tester's re-encode reached only the database, and walk 2 inherited
    a test that could never pass."""
    import subprocess
    from rota.core import lifecycle, worktrees
    git = ["git", "-c", "user.email=t@t", "-c", "user.name=t"]
    proj = tmp_path / "proj"; proj.mkdir()
    (proj / "app.py").write_text('def add(a, b):\n    return a + b\n')
    subprocess.run([*git, "init", "-q", "-b", "main"], cwd=proj, check=True)
    subprocess.run([*git, "add", "."], cwd=proj, check=True)
    subprocess.run([*git, "commit", "-q", "-m", "base"], cwd=proj, check=True)
    subprocess.run([*git, "worktree", "add", "-q", "-b", "batch/b1", str(tmp_path / "wt")], cwd=proj, check=True)
    wt = tmp_path / "wt"
    (wt / "tests").mkdir()
    (wt / "tests" / "test_add.py").write_text('def test_add():\n    assert False  # the first encode\n')
    (wt / "app.py").write_text('def add(a, b):\n    return a + b\n\n\ndef sub(a, b):\n    return a - b\n')
    sha = worktrees.commit(wt, "add sub", exclude=("tests/test_add.py",))
    assert sha
    committed = subprocess.run([*git, "show", "--name-only", "--format=", "HEAD"], cwd=wt, capture_output=True, text=True).stdout.split()
    assert committed == ["app.py"], committed
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('project_root', ?)", (str(proj),))
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) VALUES ('i1','x','in_scope','approved',1,1)")
    db.execute("INSERT INTO batches (id, item_id, status, head_commit, worktree) VALUES ('b1','i1','running',?,?)", (sha, str(wt)))
    body = 'from app import add\n\ndef test_add():\n    assert add(1, 2) == 3\n'
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES ('t1','b1',NULL,'tests/test_add.py',?)", (body,))
    db.commit()
    lifecycle.merge(db, "b1")
    delivered = subprocess.run([*git, "show", "main:tests/test_add.py"], cwd=proj, capture_output=True, text=True).stdout
    assert "add(1, 2) == 3" in delivered, delivered
    assert "the first encode" not in delivered


def test_a_module_may_not_import_its_own_package_at_module_level(tmp_path):
    """Click night 51 (2026-09-14): `from click import command` at the top of
    utils.py, which click/__init__.py imports; every test failed at import
    and the loop ran to the cap."""
    wt = tmp_path / "wt"; (wt / "src" / "click").mkdir(parents=True)
    (wt / "src" / "click" / "__init__.py").write_text('from .utils import echo as echo\nfrom .core import command as command\n')
    (wt / "src" / "click" / "core.py").write_text('def command():\n    return None\n')
    (wt / "src" / "click" / "utils.py").write_text('def echo(m):\n    print(m)\n')
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) VALUES ('i1','x','in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1','x')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) VALUES ('c1','tk1','echo_json prints','[\"src/click/utils.py::echo_json\"]')")
    db.execute("INSERT INTO batches (id, item_id, status, worktree) VALUES ('b1','i1','running',?)", (str(wt),))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    cyclic = 'from click import command\n\n\ndef echo(m):\n    print(m)\n\n\ndef echo_json(o):\n    print(o)\n'
    with pytest.raises(ValueError, match="a cycle"):
        sb.call("code.write", path="src/click/utils.py", text=cyclic)
    relative = 'from .core import command\n\n\ndef echo(m):\n    print(m)\n\n\ndef echo_json(o):\n    print(o)\n'
    assert sb.call("code.write", path="src/click/utils.py", text=relative)["bytes"]


def test_the_cycle_door_names_the_module_that_defines_the_name_or_says_none_does(tmp_path):
    """Click night 145 (2026-10-13), frame 229: s386 wrote `from click import
    Click` in decorators.py and the door said `from .core import ...`. No
    module of click defines Click, so 37 of 37 tests failed at import."""
    wt = tmp_path / "wt"; pkg = wt / "src" / "click"; pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text('from .core import Command as Command\nfrom .decorators import command as command\n')
    (pkg / "core.py").write_text('class Command:\n    pass\n')
    (pkg / "utils.py").write_text('from .core import Command\n')
    (pkg / "decorators.py").write_text('def command():\n    return None\n')
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) VALUES ('i1','x','in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1','x')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) VALUES ('c1','tk1','group works','[\"src/click/decorators.py::group\"]')")
    db.execute("INSERT INTO batches (id, item_id, status, worktree) VALUES ('b1','i1','running',?)", (str(wt),))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    tail = '\n\n\ndef command():\n    return None\n\n\ndef group():\n    return None\n'
    with pytest.raises(ValueError) as ex:
        sb.call("code.write", path="src/click/decorators.py", text="from click import Click" + tail)
    msg = str(ex.value)
    assert "a cycle" in msg and "No module of click defines Click" in msg, msg
    assert "from .core import" not in msg, "s386 was sent to core for a name core lacks"
    with pytest.raises(ValueError) as ex:
        sb.call("code.write", path="src/click/decorators.py", text="from click import Command" + tail)
    msg = str(ex.value)
    assert "Import Command from core, `from .core import Command`" in msg, msg
    assert "utils" not in msg, "an import of the name is not its definition"
    # Frame 229's review, low 2: the file under write defines command itself.
    with pytest.raises(ValueError) as ex:
        sb.call("code.write", path="src/click/decorators.py", text="from click import command" + tail)
    msg = str(ex.value)
    assert "This file defines command already; drop the import of command" in msg, msg
    assert "No module of click defines command" not in msg, msg
    # Frame 229's review, low 3: every imported name gets its own hint.
    with pytest.raises(ValueError) as ex:
        sb.call("code.write", path="src/click/decorators.py", text="from click import Command, Click" + tail)
    msg = str(ex.value)
    assert "imports Command, Click from click" in msg, msg
    assert "`from .core import Command`" in msg and "No module of click defines Click" in msg, msg


def test_a_function_reading_input_by_another_name_is_seen(db, tmp_path):
    """Click night 52 (2026-09-14): `visible_prompt_func = input` at module
    level, confirm() reads through it, a test called confirm() directly and
    pytest raised OSError for the whole loop."""
    root = tmp_path / "wt"; (root / "src" / "click").mkdir(parents=True)
    (root / "src" / "click" / "termui.py").write_text("visible_prompt_func = input\n\n\ndef _readline_prompt(func, text):\n    return func(text)\n\n\ndef confirm(text, default=None):\n    value = _readline_prompt(visible_prompt_func, text)\n    return value == 'y'\n")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    with pytest.raises(ValueError, match=r"confirm\(\) reads input\(\) through visible_prompt_func"):
        _encode(sb, "from click.termui import confirm\n\ndef test_x():\n    assert confirm('ok?', default=True) is True")


def test_a_span_that_covers_whole_inner_statements_is_a_legal_edit(tmp_path):
    """Click night 52 (2026-09-14): a span inside confirm() was refused as
    cutting through confirm, three sessions running, with only the
    whole-function spans offered."""
    wt = tmp_path / "wt"; (wt / "src").mkdir(parents=True)
    src = "def confirm(text):\n    while True:\n        try:\n            value = input(\n                text)\n        except EOFError:\n            raise SystemExit()\n        if value == 'y':\n            return True\n        return False\n"
    (wt / "src" / "termui.py").write_text(src)
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) VALUES ('i1','x','in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1','x')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) VALUES ('c1','tk1','confirm returns the default on EOF','[\"src/termui.py::confirm\"]')")
    db.execute("INSERT INTO batches (id, item_id, status, worktree) VALUES ('b1','i1','running',?)", (str(wt),))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    # line 4 is inside the two-line assignment (lines 3 to 5): a cut, named at its own depth
    with pytest.raises(ValueError, match=r"falls inside assignment .*lines 3 to 5"):
        sb.call("code.write", path="src/termui.py", text="            pass", start=3, end=4)
    # the try statement is lines 2 to 7: whole inner statements, a legal edit of confirm
    fix = '        try:\n            value = input(text)\n        except (EOFError, OSError):\n            return None\n'
    assert sb.call("code.write", path="src/termui.py", text=fix, start=2, end=7)["bytes"]


def test_a_patch_of_builtins_input_does_not_reach_an_alias(db, tmp_path):
    """Click night 53 (2026-09-14): the test patched builtins.input, confirm()
    read through visible_prompt_func bound at import, OSError all loop."""
    root = tmp_path / "wt"; (root / "src" / "click").mkdir(parents=True)
    (root / "src" / "click" / "termui.py").write_text("visible_prompt_func = input\n\n\ndef confirm(text, default=None):\n    return visible_prompt_func(text) == 'y'\n")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    with pytest.raises(ValueError, match="click.termui.visible_prompt_func"):
        _encode(sb, "from click.termui import confirm\n\ndef test_x(monkeypatch):\n    monkeypatch.setattr('builtins.input', lambda _='': 'y')\n    assert confirm('ok?') is True")
    # patching the alias, or stdin, passes the door
    ok = "from click.termui import confirm\n\ndef test_x(monkeypatch):\n    monkeypatch.setattr('click.termui.visible_prompt_func', lambda _='': 'y')\n    assert confirm('ok?') is True"
    sb2 = build("tester", db, batch_id="b1", mode="tests_missing")
    assert _encode(sb2, ok)


S197_TURN5 = (
    'from click.testing import CliRunner\n'
    'from click.termui import confirm\n'
    'import click\n'
    '\n'
    'def cli_app_with_confirm():\n'
    '    """A simple CLI app that calls confirm().""" \n'
    '    @click.command()\n'
    '    def cmd():\n'
    '        confirm("Are you sure?", default=False)\n'
    '    return cmd\n'
    '\n'
    'def test_confirm_aborts_when_stdin_closed():\n'
    '    """Test that confirm() aborts when stdin is closed and default_on_eof is False (default).\n'
    '    \n'
    '    This covers cr_2_confirm_default_on_eof and cr_4_confirm_default_on_eof.\n'
    '    When default_on_eof is not passed (defaults to False) or is explicitly False,\n'
    '    and stdin is closed, confirm() should abort.\n'
    '    """\n'
    '    runner = CliRunner()\n'
    '    # Simulate closed stdin by providing an empty stream\n'
    '    result = runner.invoke(cli_app_with_confirm(), input="")\n'
    '    assert result.exit_code != 0  # Should abort')


def _termui_alias_batch(db, tmp_path):
    root = tmp_path / "wt"; (root / "src" / "click").mkdir(parents=True)
    (root / "src" / "click" / "termui.py").write_text("visible_prompt_func = input\n\n\ndef confirm(text, default=None):\n    return visible_prompt_func(text) == 'y'\n")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE criteria SET surface_refs = ? WHERE id = 'c1'", ('["src/click/termui.py::confirm"]',))
    db.commit()


def test_confirm_inside_a_command_that_cliRunner_invokes_with_input_passes_the_stdin_door(db, tmp_path):
    """Click night 149 (2026-10-15), frame 254: s197 sent confirm() inside a
    local @click.command() run by CliRunner().invoke(..., input=""), the
    principal's recipe. The door refused it four times. It passes on bg_2's
    head, because CliRunner.isolation gives the command its input stream."""
    _termui_alias_batch(db, tmp_path)
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    assert _encode(sb, S197_TURN5)["id"] == "tst_new"
    # The command by its own name, a group's subcommand, and input= by name.
    direct = ("from click.testing import CliRunner\nfrom click.termui import confirm\nimport click\n\n"
              "@click.group()\ndef cli():\n    pass\n\n@cli.command()\ndef ask():\n    confirm('ok?')\n\n"
              "def test_x():\n    result = CliRunner().invoke(cli, ['ask'], input='y')\n    assert result.exit_code == 0")
    sb2 = build("tester", db, batch_id="b1", mode="tests_missing")
    assert _encode(sb2, direct)["id"] == "tst_new"


def test_a_stdin_read_with_no_invoke_with_input_still_refuses_and_names_the_route(db, tmp_path):
    """Frame 254: the admission covers a command that CliRunner.invoke runs
    with input= only. A read at module level, in a plain function, in a
    command run with no input=, or under `@runner.command()` still meets
    pytest's captured stdin. The refusal names the principal's route."""
    _termui_alias_batch(db, tmp_path)
    head = "from click.testing import CliRunner\nfrom click.termui import confirm\nimport click\n\n"
    bodies = [
        # module level, inside the test function
        head + "def test_x():\n    assert confirm('ok?', default=True) is True",
        # a plain function passed to invoke
        head + "def ask():\n    confirm('ok?')\n\ndef test_x():\n    assert CliRunner().invoke(ask, input='').exit_code != 0",
        # a command run with no input=
        head + "@click.command()\ndef cmd():\n    confirm('ok?')\n\ndef test_x():\n    assert CliRunner().invoke(cmd).exit_code != 0",
        # CliRunner has no command method
        head + "def test_x():\n    runner = CliRunner()\n\n    @runner.command()\n    def cmd():\n        confirm('ok?')\n\n"
               "    assert runner.invoke(cmd, input='').exit_code != 0",
    ]
    for body in bodies:
        sb = build("tester", db, batch_id="b1", mode="tests_missing")
        with pytest.raises(ValueError) as ex:
            _encode(sb, body)
        msg = str(ex.value)
        assert "where stdin is captured" in msg, (body, msg)
        assert "CliRunner().invoke(cmd, input='y')" in msg, (body, msg)


def test_a_fragment_that_is_the_tail_of_a_try_names_the_whole_statement(tmp_path):
    """Click night 53 (2026-09-14): `except ...:` sent alone, three sessions."""
    wt = tmp_path / "wt"; (wt / "src").mkdir(parents=True)
    src = 'def confirm(text):\n    while True:\n        try:\n            value = input(text)\n        except EOFError:\n            raise SystemExit()\n        return value\n'
    (wt / "src" / "termui.py").write_text(src)
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) VALUES ('i1','x','in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1','x')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) VALUES ('c1','tk1','confirm returns the default on EOF','[\"src/termui.py::confirm\"]')")
    db.execute("INSERT INTO batches (id, item_id, status, worktree) VALUES ('b1','i1','running',?)", (str(wt),))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    tail = '        except (EOFError, OSError):\n            return None\n'
    with pytest.raises(ValueError, match=r"To replace try whole send start=2, end=6\."):
        sb.call("code.write", path="src/termui.py", text=tail, start=3, end=6)  # leaves `try:` with no body: the merge fails


def test_the_word_stdin_in_a_comment_does_not_stand_the_input_door_down(db, tmp_path):
    """Click night 54 (2026-09-14): a comment said "when stdin is closed",
    the body patched builtins.input, and the alias scan stood down."""
    root = tmp_path / "wt"; (root / "src" / "click").mkdir(parents=True)
    (root / "src" / "click" / "termui.py").write_text("visible_prompt_func = input\n\n\ndef confirm(text, default=None):\n    return visible_prompt_func(text) == 'y'\n")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    with pytest.raises(ValueError, match="click.termui.visible_prompt_func"):
        _encode(sb, "from click.termui import confirm\nfrom unittest.mock import patch\n\ndef test_x():\n    # when stdin is closed, confirm returns the default\n    with patch('builtins.input', side_effect=EOFError()):\n        assert confirm('ok?', default=True) is True")


def test_a_private_helper_no_criterion_names_is_noted(tmp_path):
    """Click night 55 (2026-09-14): `_format_default` rewritten whole while
    adding a flag to confirm(); three of click's prompt tests broke. Frame
    286: the write lands, and the note names the private helper too."""
    proj = tmp_path / "proj"; (proj / "src").mkdir(parents=True)
    original = 'def _format_default(d):\n    return d\n\n\ndef confirm(text, default=None):\n    return _format_default(default)\n'
    (proj / "src" / "termui.py").write_text(original)
    wt = tmp_path / "wt"; (wt / "src").mkdir(parents=True)
    (wt / "src" / "termui.py").write_text(original)
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('project_root', ?)", (str(proj),))
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) VALUES ('i1','x','in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1','x')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) VALUES ('c1','tk1','confirm takes default_on_eof','[\"src/termui.py::confirm\"]')")
    db.execute("INSERT INTO batches (id, item_id, status, worktree) VALUES ('b1','i1','running',?)", (str(wt),))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    rewritten = "def _format_default(d):\n    return 'yes' if d else 'no'\n\n\ndef confirm(text, default=None, default_on_eof=False):\n    return _format_default(default)\n"
    out = sb.call("code.write", path="src/termui.py", text=rewritten)
    assert "changes _format_default, and no criterion" in out["not named"], out


def test_a_challenge_may_not_name_the_projects_own_test(db):
    """Click night 55 (2026-09-14): a challenge paired ce_2 with test_termui's
    prompt test; the Tester woken by it wrote nothing; unresolved on top of
    the fix loop."""
    body = 'def test_prompt():\n    assert False'
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES ('inh_1','b1',NULL,'tests/test_termui.py',?)", (body,))
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    with pytest.raises(ValueError, match="project's own test"):
        sb.call("msg.challenge_tester", refs=["c1", "inh_1"], quotes="x")


def test_an_import_of_a_name_the_module_lacks_is_refused_for_any_name(db, tmp_path):
    """Click night 55 (2026-09-14): `from click._compat import _sentinel`,
    a name nothing defines; ImportError at collection for the batch."""
    root = tmp_path / "wt"; (root / "src" / "click").mkdir(parents=True)
    (root / "src" / "click" / "_compat.py").write_text('WIN = False\n\n\ndef strip_ansi(s):\n    return s\n')
    (root / "src" / "click" / "termui.py").write_text('def confirm(text, default=None):\n    return default\n')
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE criteria SET surface_refs = ? WHERE id = 'c1'", ('["src/click/termui.py::confirm"]',))
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    with pytest.raises(ValueError, match="_compat.py does not define _sentinel, and no criterion names it"):
        _encode(sb, "from click.termui import confirm\nfrom click._compat import _sentinel\n\ndef test_x():\n    assert confirm('ok?', default=_sentinel) is _sentinel")


def test_a_reference_to_the_surface_counts_as_using_it(db, tmp_path):
    """Click night 56 (2026-09-14): a signature criterion; the test did
    inspect.signature(confirm) and was refused for never calling confirm."""
    root = tmp_path / "wt"; (root / "src" / "click").mkdir(parents=True)
    (root / "src" / "click" / "termui.py").write_text('def confirm(text, default=None, default_on_eof=False):\n    return default\n')
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE criteria SET text = ?, surface_refs = ? WHERE id = 'c1'",
               ("confirm takes a boolean parameter named default_on_eof", '["src/click/termui.py::confirm"]'))
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    body = "import inspect\nfrom click.termui import confirm\n\ndef test_signature():\n    params = inspect.signature(confirm).parameters\n    assert 'default_on_eof' in params\n    assert params['default_on_eof'].default is False"
    assert _encode(sb, body)["id"] == "tst_new"


def test_a_repair_may_not_name_a_surface_the_program_does_not_have(db):
    """Click night 56 (2026-09-14): a repair named `inspect_signature` as the
    surface; every test of the criterion was refused for never calling it."""
    db.execute("INSERT INTO code_index (grain, grain_kind, sym_kind) VALUES ('src/click/termui.py::confirm','symbol','function')")
    db.commit()
    sb = build("terminologist", db, batch_id="b1", mode="criterion_repair",
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    with pytest.raises(ValueError, match="not a name the item or the ticket gives"):
        sb.call("criteria.respecify", id="c1", text="confirm has a boolean parameter named default_on_eof",
                surface_refs=["inspect_signature"])
    out = sb.call("criteria.respecify", id="c1", text="confirm keeps a boolean parameter named default_on_eof",
                  surface_refs=["src/click/termui.py::confirm"])
    assert out["id"] == "c1"


def test_replacing_sys_stdin_by_assignment_satisfies_the_input_door(db, tmp_path):
    """Click night 57 (2026-09-14): `sys.stdin = io.StringIO('')` with a
    restore in finally, refused three times as if nothing were patched."""
    root = tmp_path / "wt"; (root / "src" / "click").mkdir(parents=True)
    (root / "src" / "click" / "termui.py").write_text("visible_prompt_func = input\n\n\ndef confirm(text, default=None):\n    return visible_prompt_func(text) == 'y'\n")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE criteria SET surface_refs = ? WHERE id = 'c1'", ('["src/click/termui.py::confirm"]',))
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    body = "from click.termui import confirm\nimport io\nimport sys\n\ndef test_eof():\n    old = sys.stdin\n    try:\n        sys.stdin = io.StringIO('')\n        assert confirm('ok?', default=True) is True\n    finally:\n        sys.stdin = old"
    assert _encode(sb, body)["id"] == "tst_new"


def test_a_challenge_quote_of_the_criterion_pasted_into_a_test_comment_is_not_the_tests_words(db):
    """Click night 58 (2026-09-14): the Tester pasted the criterion sentence
    into a comment; the Critic's challenge with an empty test-side quote
    went through; the Tester woken by it had nothing to defend."""
    body = "from script import close_account\n\ndef test_close():\n    # closing an account leaves its invoices in place\n    assert close_account('a1') == 'gone'"
    db.execute("UPDATE tests SET body = ? WHERE id = 'tst1'", (body,))
    db.commit()
    sb = build("critic", db, batch_id="b1", mode="review")
    with pytest.raises(ValueError, match="has an empty entry"):
        sb.call("msg.challenge_tester", refs=["c1", "tst1"],
                quotes=["closing an account leaves its invoices in place", ""])
    with pytest.raises(ValueError, match="must copy tst1's exact words"):
        sb.call("msg.challenge_tester", refs=["c1", "tst1"],
                quotes=["closing an account leaves its invoices in place", "closing an account leaves its invoices in place"])
    sb.call("msg.challenge_tester", refs=["c1", "tst1"],
            quotes=["closing an account leaves its invoices in place", "assert close_account('a1') == 'gone'"])
    assert sb.ctx.outbound


def test_the_litellm_backend_takes_an_extra_body_from_the_environment(monkeypatch):
    """gemma-4 through llama-server (2026-09-14): the words sat in reasoning_content
    until the request carried chat_template_kwargs enable_thinking false."""
    from rota.llm.llm import LiteLLMBackend, Pins
    monkeypatch.setenv('ROTA_LLM_EXTRA_BODY', '{"chat_template_kwargs": {"enable_thinking": false}}')
    kw = LiteLLMBackend(api_base='http://127.0.0.1:8080/v1').kwargs('sys', 'user', Pins(model='openai/x', temperature=0.0))
    assert kw['extra_body'] == {'chat_template_kwargs': {'enable_thinking': False}}
    monkeypatch.delenv('ROTA_LLM_EXTRA_BODY')
    # Frame 65 (2026-09-23): the body always carries the think pin, because
    # the cassette key carries it. With no environment body, the pin is all
    # the body holds, and a `None` resolves to THINK_DEFAULT.
    from rota.llm.llm import THINK_DEFAULT

    assert LiteLLMBackend().kwargs('sys', 'user', Pins(model='openai/x', temperature=0.0))[
        'extra_body'] == {'chat_template_kwargs': {'enable_thinking': THINK_DEFAULT}}
