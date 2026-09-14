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
    conn.execute("INSERT INTO items (id, text, kind, provenance, approval, "
                 "approval_ver, version) VALUES ('i1','closing keeps invoices',"
                 "'in_scope','decided','approved',1,1)")
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
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, approval_ver, version) VALUES "
               "('echo_json','Add an echo_json helper','in_scope','decided','approved',1,1)")
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
    red = pushed["tests.load"]["not passing"]
    assert [r["id"] for r in red] == ["tst_red"]
    assert "AssertionError" in red[0]["said"]
    assert pushed["tests.load"]["passing, not shown"] == "1 test(s)"
    assert "code.probe" not in pushed, "an empty probe is a note, not a read"
    span = pushed["code.source"]["src/click/utils.py::echo_json"]
    assert "def echo_json" in span["text"]
    assert "def echo(" not in span["text"], "the span is the definition, not the file"


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
    and re-sent, until the session ran out."""
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    with pytest.raises(ValueError) as exc:
        _encode(sb, "from script import close_account\n"
                    "def test_x():\n    assert close_account('alpha_corp') == 'beta_corp'")
    text = str(exc.value)
    assert "'alpha_corp'" in text and "'beta_corp'" in text, text
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
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
                 "VALUES ('m1','t1','liaison','vision_keeper','deliver',1)")
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
    assert "reply cut" in second
    assert "unterminated argument list" not in second, second[-1500:]
    assert vk_db.execute("SELECT COUNT(*) n FROM items").fetchone()["n"] == 1, "the whole call before the cut ran"
