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
    red = pushed["tests.load"]["the batch's tests, not passing"]
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


def test_a_bare_list_of_refs_may_hold_a_path():
    """click night 47 (2026-09-14): the Liaison copied 44 observed refs
    unbracketed, ending `., src/click`; the slash broke the run and the
    present was refused three times to quarantine."""
    from rota.llm import toolproto
    calls = toolproto.extract("TOOL: msg.present_principal(refs=argument, choice, ., src/click, text='the page')")
    call = calls[0]
    assert not isinstance(call, toolproto.ToolError), getattr(call, "reason", call)
    assert call.args["refs"] == ["argument", "choice", ".", "src/click"], call.args


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
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, approval_ver, version) VALUES "
               "('echo_json','Add an echo_json helper','in_scope','decided','approved',1,1)")
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


def test_a_write_may_not_change_a_definition_no_criterion_names(tmp_path):
    """Click nights 47 and 48 (2026-09-14): asked for echo_json next to echo,
    the Developer's span write replaced echo with a simplified copy; 19 of
    click's own tests failed; nine fix rounds called it unrelated."""
    proj = tmp_path / "proj"; (proj / "src" / "click").mkdir(parents=True)
    original = "import sys\n\n\ndef echo(message, nl=True):\n    sys.stdout.write(str(message) + (chr(10) if nl else ''))\n    sys.stdout.flush()\n"
    (proj / "src" / "click" / "utils.py").write_text(original)
    wt = tmp_path / "wt"; (wt / "src" / "click").mkdir(parents=True)
    (wt / "src" / "click" / "utils.py").write_text(original)
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('project_root', ?)", (str(proj),))
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, approval_ver, version) VALUES "
               "('i1','Add echo_json next to echo','in_scope','decided','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1','add echo_json next to echo')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) VALUES "
               "('c1','tk1','echo_json prints an object as JSON','[\"src/click/utils.py::echo_json\"]')")
    db.execute("INSERT INTO batches (id, item_id, status, worktree) VALUES ('b1','i1','running',?)", (str(wt),))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    simplified = 'import sys\n\n\ndef echo(message):\n    print(message)\n\n\ndef echo_json(obj, indent=2):\n    import json\n    print(json.dumps(obj, indent=indent))\n'
    with pytest.raises(ValueError, match=r"changes echo, and no criterion of this batch names it") as exc:
        sb.call("code.write", path="src/click/utils.py", text=simplified)
    assert "start=6, end=6" in str(exc.value), str(exc.value)
    added = original + '\n\ndef echo_json(obj, indent=2):\n    import json\n    print(json.dumps(obj, indent=indent))\n'
    assert sb.call("code.write", path="src/click/utils.py", text=added)["bytes"]
    # After a bad write landed elsewhere, the restoring write passes: echo back to the project's own, echo_json kept.
    assert sb.call("code.write", path="src/click/utils.py", text=added)["bytes"], "restoring the project's own echo passes"


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
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, approval_ver, version) VALUES "
               "('i1','x','in_scope','decided','approved',1,1)")
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
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, approval_ver, version) VALUES "
               "('i1','confirm takes a default_on_eof flag','in_scope','decided','approved',1,1)")
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
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, approval_ver, version) VALUES ('i1','x','in_scope','decided','approved',1,1)")
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
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, approval_ver, version) VALUES ('i1','x','in_scope','decided','approved',1,1)")
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


def test_a_function_reading_input_by_another_name_is_seen(db, tmp_path):
    """Click night 52 (2026-09-14): `visible_prompt_func = input` at module
    level, confirm() reads through it, a test called confirm() directly and
    pytest raised OSError for the whole loop."""
    root = tmp_path / "wt"; (root / "src" / "click").mkdir(parents=True)
    (root / "src" / "click" / "termui.py").write_text("visible_prompt_func = input\n\n\ndef _readline_prompt(func, text):\n    return func(text)\n\n\ndef confirm(text, default=None):\n    value = _readline_prompt(visible_prompt_func, text)\n    return value == 'y'\n")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    with pytest.raises(ValueError, match=r"confirm\(\) reads input\(\) internally"):
        _encode(sb, "from click.termui import confirm\n\ndef test_x():\n    assert confirm('ok?', default=True) is True")


def test_a_span_that_covers_whole_inner_statements_is_a_legal_edit(tmp_path):
    """Click night 52 (2026-09-14): a span inside confirm() was refused as
    cutting through confirm, three sessions running, with only the
    whole-function spans offered."""
    wt = tmp_path / "wt"; (wt / "src").mkdir(parents=True)
    src = "def confirm(text):\n    while True:\n        try:\n            value = input(\n                text)\n        except EOFError:\n            raise SystemExit()\n        if value == 'y':\n            return True\n        return False\n"
    (wt / "src" / "termui.py").write_text(src)
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, approval_ver, version) VALUES ('i1','x','in_scope','decided','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1','x')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) VALUES ('c1','tk1','confirm returns the default on EOF','[\"src/termui.py::confirm\"]')")
    db.execute("INSERT INTO batches (id, item_id, status, worktree) VALUES ('b1','i1','running',?)", (str(wt),))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    # line 4 is inside the two-line assignment (lines 3 to 5): a cut, named at its own depth
    with pytest.raises(ValueError, match=r"cuts through assign .*lines 3 to 5"):
        sb.call("code.write", path="src/termui.py", text="            pass", start=3, end=4)
    # the try statement is lines 2 to 7: whole inner statements, a legal edit of confirm
    fix = '        try:\n            value = input(text)\n        except (EOFError, OSError):\n            return None\n'
    assert sb.call("code.write", path="src/termui.py", text=fix, start=2, end=7)["bytes"]
