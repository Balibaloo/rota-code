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

import json
import re

import pytest

from rota.core.db import init_db
from rota.core.sandbox import ArgumentError, build
from rota.core.predicates import Wake
from rota.testkit.fixtures import seed_provenance


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, "
                 "approval_ver, version) VALUES ('i1','closing keeps invoices',"
                 "'in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','i1','close an account')")
    conn.execute("INSERT INTO glossary_terms (id, term, sense_short) "
                 "VALUES ('g1','account','the billing entity')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('c1','tk1','closing an account leaves its invoices in place')")
    # The relation holds what the column holds: the readers read the relation.
    conn.execute("INSERT INTO refs (src_table, src_id, kind, target) VALUES "
                 "('criteria','c1','term','g1')")
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


def _unloadable_tree(db, tmp_path, module_text, surface):
    """A worktree whose surface module fails at import, and the criterion on it."""
    root = tmp_path / "wt"
    rel = surface.split("::", 1)[0]
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(module_text, encoding="utf-8")
    (root / "src" / "click").mkdir(parents=True, exist_ok=True)
    (root / "src" / "click" / "__init__.py").write_text("", encoding="utf-8")
    (root / "src" / "click" / "decorators.py").write_text(
        "def version_option():\n    return None\n", encoding="utf-8")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE criteria SET surface_refs = ? WHERE id = 'c1'",
               (json.dumps([surface]),))
    db.execute("DELETE FROM tests")
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    return sb


@pytest.mark.parametrize("body, old", [
    # The "no module of that name" hint.
    ("from imagepipe import process_commands\n"
     "def test_x():\n    assert process_commands() is None\n",
     "Import the surface from its own module"),
    # The "It is defined in" refusal.
    ("from src.click.decorators import process_commands\n"
     "def test_x():\n    assert process_commands() is None\n",
     "It is defined in examples.imagepipe.imagepipe"),
])
def test_the_import_hints_never_offer_a_module_that_does_not_load(db, tmp_path, body, old):
    """
    Frame 215's review 1, finding 2, probe p3: two more refusals offered
    the import of a module that fails at import in the sandbox.
    """
    sb = _unloadable_tree(db, tmp_path, "import rota_absent_pil_module\n\n\n"
                          "def process_commands():\n    return None\n",
                          "examples/imagepipe/imagepipe.py::process_commands")
    with pytest.raises(ValueError) as refused:
        sb.call("tests.encode", id="tst_4", criterion_id="c1",
                path="tests/test_v.py", body=body)
    said = str(refused.value)
    assert old not in said
    assert "does not load in the sandbox" in said
    assert "msg.question_terminologist(refs=['c1']" in said


def test_an_error_text_the_console_cannot_print_still_reads_as_a_load_failure(db, tmp_path):
    """
    Frame 215's review 1, finding 3, probe p2's `pkg.uni`: the child's print
    failed on a non-cp1252 character, the probe returned an empty string,
    and the door offered the import again.
    """
    sb = _unloadable_tree(db, tmp_path,
                          "raise RuntimeError('café ☃ fails')\n\n\n"
                          "def uni_run():\n    return None\n",
                          "pkg/uni.py::uni_run")
    with pytest.raises(ValueError) as refused:
        sb.call("tests.encode", id="tst_4", criterion_id="c1", path="tests/test_v.py",
                body="def test_x():\n    assert uni_run() is None\n")
    said = str(refused.value)
    assert "add `from pkg.uni import uni_run`" not in said
    assert "does not load in the sandbox" in said and "RuntimeError" in said


def test_the_encode_doors_never_force_an_import_that_does_not_load(db, tmp_path):
    """
    Frame 215, night 142's s542 on m382: the surface was
    `examples/imagepipe/imagepipe.py::process_commands`, and the module
    imports `PIL`, which the sandbox lacks. The Tester sent tst_4 without
    the import. The surface door and the NameError door told it to import
    the module 17 times, and every landed test failed at import. The doors
    now check that the module loads before they offer the line.
    """
    root = tmp_path / "wt"
    (root / "examples" / "imagepipe").mkdir(parents=True)
    pipe = root / "examples" / "imagepipe" / "imagepipe.py"
    # The first import is a module the sandbox lacks, as `PIL` was.
    pipe.write_text("import rota_absent_pil_module\n\n\n"
                    "def process_commands():\n    return None\n", encoding="utf-8")
    (root / "src" / "click").mkdir(parents=True)
    (root / "src" / "click" / "__init__.py").write_text("", encoding="utf-8")
    (root / "src" / "click" / "testing.py").write_text(
        "class CliRunner:\n    pass\n", encoding="utf-8")
    (root / "src" / "click" / "decorators.py").write_text(
        "def version_option():\n    return None\n", encoding="utf-8")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE criteria SET surface_refs = "
               "'[\"examples/imagepipe/imagepipe.py::process_commands\"]' "
               "WHERE id = 'c1'")
    db.execute("DELETE FROM tests")
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    # s542's tst_4 (seq 4): the imagepipe line swapped for another
    # module's callable. The surface door refused it.
    no_import = ("from click.testing import CliRunner\n"
                 "import sys\n"
                 "from src.click.decorators import version_option\n"
                 "\n"
                 "def test_version_output_includes_python():\n"
                 "    runner = CliRunner()\n"
                 "    result = runner.invoke(version_option, ['--show-python', '--version'])\n"
                 "    assert result.exit_code == 0\n"
                 "    expected_version = f\"{sys.version_info.major}.{sys.version_info.minor}"
                 ".{sys.version_info.micro}\"\n"
                 "    assert expected_version in result.output\n")
    with pytest.raises(ValueError) as refused:
        sb.call("tests.encode", id="tst_4", criterion_id="c1",
                path="tests/test_version_option_include_python.py", body=no_import)
    said = str(refused.value)
    assert "Import the surface from its own module" not in said
    assert "does not load in the sandbox" in said
    assert "rota_absent_pil_module" in said
    assert "msg.question_terminologist(refs=['c1']" in said
    # The NameError door: the test calls the surface and never imports it.
    calls = ("from click.testing import CliRunner\n"
             "def test_version_output_includes_python():\n"
             "    assert process_commands() is None\n")
    with pytest.raises(ValueError) as refused:
        sb.call("tests.encode", id="tst_4", criterion_id="c1",
                path="tests/test_version_option_include_python.py", body=calls)
    said = str(refused.value)
    assert "add `from examples.imagepipe.imagepipe import" not in said
    assert "does not load in the sandbox" in said
    assert "msg.question_terminologist(refs=['c1']" in said
    # A module that loads keeps today's two doors word for word.
    pipe.write_text("def process_commands():\n    return None\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Import the surface from its own module"):
        sb.call("tests.encode", id="tst_4", criterion_id="c1",
                path="tests/test_version_option_include_python.py", body=no_import)
    with pytest.raises(ValueError, match="add `from examples.imagepipe.imagepipe import "
                                         "process_commands`"):
        sb.call("tests.encode", id="tst_4", criterion_id="c1",
                path="tests/test_version_option_include_python.py", body=calls)


def _click_tree(db, tmp_path, surface):
    """A worktree whose surface modules load, a conftest with one fixture,
    and the criterion on `surface`."""
    root = tmp_path / "wt"
    for rel, text in {
            "src/click/__init__.py": "",
            "src/click/termui.py": "def confirm(text, default=False):\n    return default\n",
            "src/click/decorators.py": "def version_option(*a, **k):\n    return lambda f: f\n",
            "src/click/testing.py": "class CliRunner:\n    pass\n",
            "src/billing/__init__.py": "",
            "src/billing/accounts.py": "def close_account(account_id):\n    return False\n",
            "tests/conftest.py": "import pytest\n\n\n@pytest.fixture(scope='function')\n"
                                "def runner(request):\n    return None\n"}.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE criteria SET surface_refs = ? WHERE id = 'c1'",
               (json.dumps([surface]),))
    db.execute("DELETE FROM tests")
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    return sb


def _refused(sb, body):
    with pytest.raises(ValueError) as refused:
        sb.call("tests.encode", id="tst_4", criterion_id="c1",
                path="tests/test_v.py", body=body)
    return str(refused.value)


def test_the_name_error_hint_names_the_surface_import_for_the_surface_and_its_module(db, tmp_path):
    """
    Frame 222, shape 1: the unbound name is the surface's symbol or its
    module, so the surface import binds it. The module form names the
    line that binds the module, not the symbol.
    """
    sb = _click_tree(db, tmp_path, "src/click/termui.py::confirm")
    said = _refused(sb, "def test_confirm_default_off():\n"
                        "    assert confirm('y/n') is False\n")
    assert "add `from src.click.termui import confirm`" in said, said
    said = _refused(sb, "def test_confirm_default_off():\n"
                        "    assert termui.confirm('y/n') is False\n")
    assert "add `from src.click import termui`" in said, said
    assert "import confirm`" not in said, said


def test_the_name_error_hint_takes_a_pytest_fixture_as_a_test_argument(db, tmp_path):
    """
    Frame 222, shape 2: night 143's s320 used `monkeypatch` in a test that
    did not take it, and the door said four times to add the surface
    import, which binds no fixture. A conftest's fixture is the same shape.
    """
    sb = _click_tree(db, tmp_path, "src/click/termui.py::confirm")
    said = _refused(sb, "from click.termui import confirm\nimport sys\nimport io\n\n"
                        "def test_confirm_default_off():\n"
                        "    # default_on_eof is False by default.\n"
                        "    # When stdin is closed (EOF), confirm() should raise an exception,\n"
                        "    # not return a default value.\n"
                        "    with monkeypatch.context() as mp:\n"
                        "        mp.setattr(sys, \"stdin\", io.StringIO(\"\"))\n"
                        "        with pytest.raises(SystemExit):\n"
                        "            confirm(\"y/n\")\n"
                        "        assert True")
    assert "monkeypatch is a pytest fixture" in said, said
    assert "def test_confirm_default_off(monkeypatch)" in said, said
    assert "add `from" not in said, said
    # The project's tests/conftest.py defines `runner`.
    said = _refused(sb, "def test_version_option_show_python():\n"
                        "    def cli():\n        pass\n"
                        "    result = runner.invoke(cli, ['--version'])\n"
                        "    assert 'Python' in result.output\n")
    assert "runner is a pytest fixture" in said, said
    assert "add `from" not in said, said


@pytest.mark.parametrize("surface, body, name, line", [
    # The register case L1-TS-apply-a-term-and-write-the-test, as the
    # recording holds it: `ledger` stands in for close_account. On pass 1's
    # text the Tester wrote `ledger = []` as a fake, four runs of five.
    ("src/billing/accounts.py::close_account",
     "def test_closing_account_leaves_invoices_in_ledger():\n"
     "    assert 'invoices for closed accounts' in ledger.log", "ledger",
     "add `from src.billing.accounts import close_account`"),
    # Frame 222's review 1, finding 1: a body that already imports the
    # surface is not told to add the line again.
    ("src/billing/accounts.py::close_account",
     "from src.billing.accounts import close_account\n"
     "def test_closing_account_leaves_invoices_in_ledger():\n"
     "    assert 'invoices for closed accounts' in ledger.log", "ledger",
     "the body already imports close_account"),
])
def test_the_name_error_hint_calls_the_surface_in_place_of_a_stand_in(
        db, tmp_path, surface, body, name, line):
    """
    Frame 222, shape 3a: the body never calls the surface, so the unbound
    name stands in for it, as frame 82 saw with `ledger`, `app` and
    `create_account`. The hint names the surface's line, and it asks for
    no definition of the name.
    """
    sb = _click_tree(db, tmp_path, surface)
    said = _refused(sb, body)
    assert f"{name} is not the criterion's surface" in said, said
    assert line in said, said
    assert "owes a definition" not in said, said
    if "already imports" in line:
        assert "add `from" not in said, said


@pytest.mark.parametrize("body, name, line", [
    # Night 146's s485: the body imports version_option and passes the
    # stand-in to the runner. Replaced by the surface, it met the
    # plain-function door (frame 222's review 1, finding 1).
    ("from click.decorators import version_option\n"
     "from click.testing import CliRunner\n\n"
     "def test_version_option_show_python_enabled():\n"
     "    # When show_python flag is enabled, output includes Python version\n"
     "    runner = CliRunner()\n"
     "    result = runner.invoke(cli_app_with_version_option, [\"--show-python\", \"--version\"])\n"
     "    assert result.exit_code == 0\n"
     "    assert \"3.10\" in result.output  # major.minor.micro format",
     "cli_app_with_version_option", "the body already imports version_option"),
    # Night 143's s464: no import of the surface.
    ("def test_version_option_show_python():\n"
     "    # Run command with version option enabled\n"
     "    result = runner.invoke(cli, [\"--version\", \"--show-python\"])\n"
     "    assert \"Python\" in result.output\n"
     "    \n"
     "    # Run command with version option disabled (default)\n"
     "    result = runner.invoke(cli, [\"--version\"])\n"
     "    assert \"Python\" not in result.output",
     "cli", "add `from src.click.decorators import version_option`"),
])
def test_the_name_error_hint_owes_a_command_that_a_runner_invokes(db, tmp_path, body, name, line):
    """
    Frame 222, shape 3a on `.invoke`: the stand-in is a click command the
    test owes, which the surface decorates or calls, as s549's seq 4 wrote.
    """
    sb = _click_tree(db, tmp_path, "src/click/decorators.py::version_option")
    said = _refused(sb, body)
    assert f"{name} is a click command the test owes" in said, said
    assert "`@click.command()`" in said, said
    assert line in said, said
    assert f"in place of {name}" not in said, said


def test_a_surface_named_like_a_fixture_gets_the_surface_line(db, tmp_path):
    """
    Frame 222's review 1, finding 3: the tree's conftest defines `runner`,
    and the surface is named `runner`. The surface is read first.
    """
    sb = _click_tree(db, tmp_path, "src/click/testing.py::runner")
    said = _refused(sb, "def test_runner():\n    assert runner() is None\n")
    assert "add `from src.click.testing import runner`" in said, said
    assert "pytest fixture" not in said, said


def test_the_name_error_hint_says_the_test_owes_a_helper_beside_the_surface(db, tmp_path):
    """
    Frame 222, shape 3b: the register case
    L1-TS-encode-a-criterion-the-principal-corrected calls the surface and
    a helper it never defines. The door said four times to add the surface
    import, which binds no helper.
    """
    sb = _click_tree(db, tmp_path, "src/billing/accounts.py::close_account")
    said = _refused(sb, "from src.billing.accounts import close_account\n"
                        "def test_close_account_returns_false_for_never_opened_account():\n"
                        "    account_id = generate_unique_account_id()\n"
                        "    result = close_account(account_id)\n"
                        "    assert result is False")
    assert "The test owes a definition of generate_unique_account_id" in said, said
    assert "If a library defines generate_unique_account_id" in said, said
    assert "add `from" not in said, said


def test_the_name_error_hint_imports_a_name_the_project_defines(db, tmp_path):
    """
    Frame 222, shape 4: night 149's s195 used `CliRunner`, which the
    project defines in `testing.py`. The hint of pass 1b said to call
    confirm in place of it, 14 times of 15. The fixture tree is not
    installed, so the line keeps `src.`.
    """
    sb = _click_tree(db, tmp_path, "src/click/termui.py::confirm")
    said = _refused(sb, "from click.termui import confirm\n\n"
                        "def test_confirm_default_on_eof():\n"
                        "    runner = CliRunner()\n"
                        "    result = runner.invoke(runner.make_click_command(lambda: None), input=\"\")\n"
                        "    assert result.exit_code == 0")
    assert ("CliRunner is defined in src.click.testing of the project: "
            "add `from src.click.testing import CliRunner`") in said, said
    assert "in place of CliRunner" not in said, said


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


def test_an_overload_stub_is_not_a_second_definition(db, tmp_path):
    """clickI night 32 (2026-09-13): termui.py carries three `@t.overload`
    stubs of `prompt` above the one body. Every span write to the file was
    refused as a duplicate, three identical sessions to quarantine."""
    root = tmp_path / "wt"; root.mkdir()
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    text = ("import typing as t\n\n"
            "@t.overload\ndef prompt(text: str, default: None = None) -> str: ...\n\n"
            "@t.overload\ndef prompt(text: str, default: int) -> int: ...\n\n"
            "def prompt(text, default=None):\n    return default\n\n"
            "def confirm(text):\n    return True\n")
    assert sb.call("code.write", path="termui.py", text=text)["bytes"]
    with pytest.raises(ValueError, match="defines confirm twice"):
        sb.call("code.write", path="termui.py",
                text=text + "\ndef confirm(text, default_on_eof=None):\n    return default_on_eof\n")


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


def test_a_second_verdict_on_one_commit_is_refused(db, tmp_path):
    # Frame 107. The Terminologist's answer wakes the Critic after its
    # verdict landed, so the tool refuses a second verdict on the same
    # commit (ruled: Roman, 2026-10-01: the Critic's doubt about a
    # criterion goes to the Terminologist, the writer of the criteria).
    # A pass names a line per criterion (frame 170), so b1 gets a diff.
    from tests.rota.test_verdict_lines import a_batch_repo
    line = "def close_account(account_id): return 'closed'"
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'",
               (a_batch_repo(tmp_path, line),))
    db.commit()
    sb = build("critic", db, batch_id="b1", mode="review")
    # The test is about a second verdict, not the first-pass hold of frame
    # 201, pass 3. So the hold counts as spent.
    sb.ctx.pass_held = True
    sb.call("verdicts.emit", batch_id="b1", result="pass", lines={"c1": line})
    with pytest.raises(ValueError, match="already landed"):
        sb.call("verdicts.emit", batch_id="b1", result="pass")
    # A verdict on file from an earlier session counts the same.
    db.execute("INSERT INTO verdicts (id, batch_id, commit_sha, result) "
               "VALUES ('critic:b1:abc123','b1','abc123','pass')")
    db.commit()
    sb = build("critic", db, batch_id="b1", mode="answer")
    sb.ctx.pass_held = True
    with pytest.raises(ValueError, match="already landed"):
        sb.call("verdicts.emit", batch_id="b1", result="pass")
    # A new commit is a new diff, and it gets its own verdict.
    db.execute("UPDATE batches SET head_commit = 'def456' WHERE id = 'b1'")
    db.commit()
    out = sb.call("verdicts.emit", batch_id="b1", result="pass",
                  lines={"c1": line})
    assert out["id"] == "critic:b1:def456"


def test_a_report_from_a_batch_wake_names_the_batch(db):
    wake = Wake("architect", "tick:exhausted", refs=("b1",))
    sb = build("architect", db, batch_id="b1", mode="exhausted", wake=wake)
    db.execute("INSERT INTO constraints (id, headline, text) VALUES "
               "('cn1','exports never buffer','memory stays flat')")
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
            assumption="the test assumes Alice as a sample name", kind="invented")
    _encode(sb, "from script import greet\n"
                "def test_greet(monkeypatch):\n"
                "    monkeypatch.setattr('builtins.input', lambda _='': 'Alice')\n"
                "    assert greet() == 'closing Alice'")


# Frame 111. Night 106 (2026-10-02): bg_2's tests assigned `sys.stdin`, and
# `code.write` refused every fix as unshielded. One AST check serves both doors.
# Each shielded body but `builtins_input` holds no word the old check read,
# so the old check refused it. `builtins_input` keeps today's acceptance.
_ASK = "def ask():\n    return input('name: ')\n"
_SHIELDS = {
    "assigned": "def test_ask():\n    sys.stdin = io.StringIO('')\n",
    "setattr_sys": "def test_ask():\n    setattr(sys, 'stdin', io.StringIO(''))\n",
    "patch_object": "def test_ask():\n  with mock.patch.object(sys, 'stdin', io.StringIO('')):\n",
    "tuple": "def test_ask():\n    sys.stdin, old = io.StringIO(''), sys.stdin\n",
    "builtins_input": "def test_ask(monkeypatch):\n"
                      "    monkeypatch.setattr('builtins.input', lambda _='': '')\n",
    "none": "def test_ask():\n",
    "comment": "def test_ask():\n    # sys.stdin is captured under pytest\n",
    "attribute": "def test_ask():\n    ns = mock.Mock()\n    ns.input = 3\n",
    "client": "def test_ask():\n    client = mock.Mock()\n    client.patch('/v1.input')\n",
    "bare_patch": "def test_ask():\n  with mock.patch('sys.stdin'):\n",
}
_SHIELDED = ["assigned", "setattr_sys", "patch_object", "tuple", "builtins_input"]
_UNSHIELDED = ["none", "comment", "attribute", "client", "bare_patch"]


def _asker(shield):
    return ("import io\nimport sys\nfrom unittest import mock\nfrom script import ask\n\n"
            + _SHIELDS[shield] + "    assert ask() == ''\n")


def _stdin_db(db, tmp_path, script=None):
    root = tmp_path / "wt"; root.mkdir()
    if script:
        (root / "script.py").write_text(script)
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()


def _write_ask(db, shield):
    db.execute("DELETE FROM tests")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('tst1','b1','c1','tests/test_ask.py',?)", (_asker(shield),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    return sb.call("code.write", path="script.py", text=_ASK)


@pytest.mark.parametrize("shield", _SHIELDED)
def test_a_shielded_test_lets_a_reader_of_input_be_written(db, tmp_path, shield):
    _stdin_db(db, tmp_path)
    assert _write_ask(db, shield)["created"]


@pytest.mark.parametrize("shield", _UNSHIELDED)
def test_an_unshielded_test_refuses_a_reader_of_input(db, tmp_path, shield):
    _stdin_db(db, tmp_path)
    with pytest.raises(ValueError, match="ask reads input\\(\\) internally, and a "
                       "test in this batch calls ask\\(\\) directly with no "
                       "monkeypatch or sys.stdin assignment shielding it"):
        _write_ask(db, shield)


@pytest.mark.parametrize("shield", _SHIELDED)
def test_a_shielded_test_of_a_reader_of_input_is_encoded(db, tmp_path, shield):
    _stdin_db(db, tmp_path, _ASK)
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    # The literal door reads 'stdin' as a chosen word, a fact apart from this one.
    sb.call("ledger.log", about_ref="c1", about_table="criteria",
            assumption="the test assumes stdin is the stream ask reads", kind="invented")
    assert _encode(sb, _asker(shield))


@pytest.mark.parametrize("shield", _UNSHIELDED)
def test_an_unshielded_test_of_a_reader_of_input_is_refused(db, tmp_path, shield):
    _stdin_db(db, tmp_path, _ASK)
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    with pytest.raises(ValueError, match="ask\\(\\) reads input\\(\\) internally "
                       "\\(script.py\\), and this test calls ask\\(\\) directly"):
        _encode(sb, _asker(shield))


def test_a_test_that_calls_input_itself_needs_a_shield_in_code(db):
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    with pytest.raises(ValueError, match="captures stdin"):
        _encode(sb, "import sys\n\ndef test_greet():\n"
                    "    # sys.stdin and builtins are captured\n"
                    "    assert input() == ''")
    sb2 = build("tester", db, batch_id="b1", mode="tests_missing")
    assert _encode(sb2, "import io\nimport sys\n\ndef test_greet():\n"
                        "    sys.stdin = io.StringIO('')\n"
                        "    assert input() == ''")


@pytest.mark.parametrize("body, want", [
    ("object(1)", set()),                                        # finding 4
    ("ns.input = 3", set()),                                     # finding 1
    ("client.patch('/v1.input')", set()),                        # finding 1
    ("setattr(ns, 'input', 3)", set()),                          # finding 1
    ("mock.patch('sys.stdin')", set()),                          # finding 3
    ("mock.patch.object(sys, 'stdin')", set()),                  # finding 3
    ("mock.patch('sys.stdin', new=io.StringIO(''))", {"sys.stdin"}),
    ("sys.stdin, old = io.StringIO(''), sys.stdin", {"sys.stdin"}),  # finding 5
    ("[sys.stdin, *rest] = [io.StringIO('')]", {"sys.stdin"}),
    ("import script\nmonkeypatch.setattr(script, 'input', f)", {"script.input"}),
    ("monkeypatch.setattr('click.termui.visible_prompt_func', f)",
     {"click.termui.visible_prompt_func"}),
    ("with patch('builtins.input', side_effect=EOFError()): pass", {"builtins.input"}),
])
def test_the_stdin_shield_reads_only_a_stream_or_a_module_name(body, want):
    """The diff review of 538b84a (2026-10-02, frame 111) found a shield on
    any attribute named input, a bare stdin patch, and a crash on object()."""
    import ast
    from rota.roles.api import _stdin_shields
    assert _stdin_shields(ast.parse(body)) == want


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


def test_an_unbound_name_is_told_the_import_the_surface_names(db):
    """Frame 82: a Tester invented ledger, app and create_account five runs
    of five. The criterion carries the surface, so the Wall names the line.
    Frame 222: the surface's own name gets the line, which binds it. The
    `ledger` body never calls the surface, so `ledger` stands in for it,
    and the hint names the surface's line and asks for no definition."""
    db.execute("UPDATE criteria SET surface_refs = "
               "'[\"src/billing/accounts.py::close_account\"]' WHERE id = 'c1'")
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    with pytest.raises(ValueError) as exc:
        _encode(sb, "def test_close():\n    assert close_account('a1') is False")
    assert "The criterion's surface is src/billing/accounts.py::close_account" in str(exc.value)
    # The fake repository has no build system, so pytest imports from its root.
    assert "add `from src.billing.accounts import close_account`" in str(exc.value)
    with pytest.raises(ValueError) as exc:
        _encode(sb, "def test_close():\n    assert ledger.close('a1') == 'kept'")
    assert "ledger is not the criterion's surface" in str(exc.value)
    assert "add `from src.billing.accounts import close_account`" in str(exc.value)
    assert "owes a definition" not in str(exc.value)


def test_an_installed_project_is_told_the_import_without_src(db, tmp_path):
    """An installed src layout is imported by its package name."""
    root = tmp_path / "wt"; root.mkdir()
    (root / "setup.py").write_text("from setuptools import setup\nsetup()\n")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE criteria SET surface_refs = "
               "'[\"src/billing/__init__.py::close_account\"]' WHERE id = 'c1'")
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    with pytest.raises(ValueError) as exc:
        _encode(sb, "def test_close():\n    assert close_account('a1') is False")
    assert "add `from billing import close_account`" in str(exc.value)


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


def _answered_escalation(db, answer_refs):
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m1','th','developer','architect',"
               "'escalate','[\"c1\", \"tst1\"]',1,'answered')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status, cause_id) VALUES ('m2','th','architect',"
               "'developer','answer',?,2,'answered','m1')", (answer_refs,))
    db.commit()
    from rota.roles import prompts
    return build("developer", db, batch_id="b1", mode="tests_failing",
                 allow=prompts.mode_tools("developer", "tests_failing"))


def test_the_same_escalation_twice_is_refused_toward_the_answer(db):
    """Night 106 (2026-10-02): s223 and s224 met "act on the answer", and
    the answer m116 held no words and no new row (frame 111)."""
    sb = _answered_escalation(db, '["c1"]')
    with pytest.raises(ValueError) as exc:
        sb.call("msg.escalate_architect", refs=["c1", "tst1"])
    assert str(exc.value) == (
        "you sent escalate to architect on exactly these refs already (m1) "
        "and they answered (m2) with no row beyond your own refs. Sending it "
        "again is the same argument again. The attempt cap carries this batch "
        "to the ladder: make one real change to the code the test calls, or "
        "end the session with no call")


def test_the_same_refs_in_another_order_are_the_same_escalation(db):
    """Frame 111's design review (2026-10-02): the door compared the JSON
    text, so the same refs in another order escaped it."""
    sb = _answered_escalation(db, '["c1"]')
    with pytest.raises(ValueError, match=r"exactly these refs already \(m1\)"):
        sb.call("msg.escalate_architect", refs=["tst1", "c1"])


def test_a_repeat_escalation_is_told_the_rows_the_answer_added(db):
    sb = _answered_escalation(db, '["c1", "g1", "tk1"]')
    with pytest.raises(ValueError) as exc:
        sb.call("msg.escalate_architect", refs=["c1", "tst1"])
    assert str(exc.value) == (
        "you sent escalate to architect on exactly these refs already (m1) "
        "and they answered (m2): the answer points at g1, tk1 -- code.source "
        "those rows, write the change they call for, and commit")


def test_a_challenge_that_waits_for_its_answer_is_not_sent_twice(db):
    """Night 108 (2026-10-02): s307 to s328 sent one challenge each on the
    refs of m190 while the Tester answered none, and nine landed."""
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m1','th','developer','tester',"
               "'challenge','[\"tst1\", \"c1\"]',1,'open')")
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    quotes = ["closing an account leaves its invoices in place",
              "assert close_account('a1') is not None"]
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", refs=["c1", "tst1"], quotes=quotes)
    assert str(exc.value) == (
        "you sent challenge to tester on exactly these refs already (m1) and it "
        "waits for an answer. A second copy is the same question twice, and the "
        "answer comes to a later wake. Until then: code.source the code the "
        "test calls and write the change that makes it pass, or end the session "
        "with no call")
    # Once the Tester answers, the answered door speaks, and this one does not.
    # The sentence names the answer and one step (frame 132's design, 3.4).
    db.execute("UPDATE messages SET status = 'answered' WHERE id = 'm1'")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status, cause_id) VALUES ('m2','th','tester',"
               "'developer','answer','[\"c1\", \"tst1\"]',2,'open','m1')")
    db.commit()
    sb2 = build("developer", db, batch_id="b1", mode="tests_failing",
                allow=prompts.mode_tools("developer", "tests_failing"))
    with pytest.raises(ValueError) as exc:
        sb2.call("msg.challenge_tester", refs=["c1", "tst1"], quotes=quotes)
    assert str(exc.value) == (
        "you sent challenge to tester on exactly these refs already (m1) and "
        "they answered (m2). Sending it again is the same argument again. "
        "Send msg.escalate_architect on the same refs.")


@pytest.mark.parametrize("status", ["answered", "unresolved"])
def test_a_closed_escalation_with_no_answer_row_is_not_pending(db, status):
    """Night 109 (2026-10-03): the Architect turned escalation m97 into a
    challenge to the Vision Keeper. m97 read 'answered' with no answer row,
    and "it waits for an answer" refused 11 escalations all night."""
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m97','th','developer','architect',"
               "'escalate','[\"tst1\", \"c1\"]',1,?)", (status,))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    with pytest.raises(ValueError) as exc:
        sb.call("msg.escalate_architect", refs=["c1", "tst1"])
    assert str(exc.value) == (
        f"you sent escalate to architect on exactly these refs already (m97) "
        f"and they answered ({status}) with no row beyond your own refs. Sending "
        f"it again is the same argument again. The attempt cap carries this "
        f"batch to the ladder: make one real change to the code the test calls, "
        f"or end the session with no call")


def test_an_open_escalation_with_no_answer_row_waits(db):
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m97','th','developer','architect',"
               "'escalate','[\"tst1\", \"c1\"]',1,'open')")
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    with pytest.raises(ValueError) as exc:
        sb.call("msg.escalate_architect", refs=["c1", "tst1"])
    assert str(exc.value) == (
        "you sent escalate to architect on exactly these refs already (m97) and "
        "it waits for an answer. A second copy is the same question twice, and "
        "the answer comes to a later wake. Until then: code.source the code the "
        "test calls and write the change that makes it pass, and commit it, or "
        "end the session with no call")


def test_a_closed_challenge_with_no_answer_row_admits_one_resend(db):
    """Frame 132: a closed challenge that no answer row names is not the
    Tester's judgement. The door admits one re-send, with today's result and
    no note (ruled: the judging session, 2026-10-05, option 1)."""
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m1','th','developer','tester',"
               "'challenge','[\"c1\", \"tst1\"]',1,'answered')")
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    out = sb.call("msg.challenge_tester", reason=REASON, refs=["c1", "tst1"],
                  quotes=["closing an account leaves its invoices in place",
                          "assert close_account('a1') is not None"])
    assert out == {"id": "m2", "to": "tester", "verb": "challenge"}


def test_a_repeat_challenge_is_told_the_rung_as_a_sentence(db):
    """Night 111 (2026-10-03): s252 read "-- msg.escalate_architect" at
    turn 6 and sent the same challenge again (frame 111)."""
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m96','th','developer','tester',"
               "'challenge','[\"tst1\", \"c1\"]',1,'answered')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status, cause_id) VALUES ('m98','th','tester',"
               "'developer','answer','[\"c1\", \"tst1\"]',2,'open','m96')")
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", refs=["c1", "tst1"],
                quotes=["closing an account leaves its invoices in place",
                        "assert close_account('a1') is not None"])
    assert str(exc.value) == (
        "you sent challenge to tester on exactly these refs already (m96) and "
        "they answered (m98). Sending it again is the same argument again. "
        "Send msg.escalate_architect on the same refs.")
    assert " -- " not in str(exc.value)


# Frames 132 and 145: the same-refs door on the Developer's challenge to the
# Tester. The newest prior on the same refs decides. The first three tests
# send the recorded call of each night on that night's rows, because
# `_challenge_evidence` matches the quotes against the rows.
NOTE = "the session woken by it wrote nothing and sent nothing"
N122_CRIT = 'The callable `echo_json` accepts any Python object and writes its JSON representation to the stream using `json.dumps(obj, separators=(",", ":"))`, followed by a single newline.'
N122_TEST = 'def test_echo_json_compact():\n    from click.testing import CliRunner\n    from io import StringIO\n    import sys\n    from src.click.utils import echo_json\n    \n    runner = CliRunner()\n    with runner.isolated_filesystem():\n        output = StringIO()\n        old_stdout = sys.stdout\n        sys.stdout = output\n        echo_json({"key": "value"})\n        sys.stdout = old_stdout\n        assert output.getvalue() == "{\\"key\\": \\"value\\"}\\n"'
N119_CRIT = 'When `version_option` is invoked, if `show_python` is true, the output message must include the running Python version string.'
N119_TEST = 'from click.decorators import version_option\n\ndef test_version_option_shows_python():\n    # Arrange: create a dummy command and apply the decorator with show_python=True\n    @version_option(show_python=True)\n    def dummy_cmd(ctx, param, value):\n        return "dummy"\n    \n    # Act & Assert: The option added by the decorator should be present in the command\'s options.\n    assert hasattr(dummy_cmd.params[0], "name")'
N119_CRIT3 = 'When `show_python` is false, the output message must not include the running Python version string.'
# Version 1 of tst_v3, copied from the prompt of s250's first turn. The row
# moved to version 2 later that night.
N119_TEST3 = 'from click.decorators import version_option\n\ndef test_version_option_does_not_show_python_when_false():\n    # Arrange: create a dummy command and apply the decorator with show_python=False\n    @version_option(show_python=False)\n    def dummy_cmd(ctx, param, value):\n        return "dummy"\n    \n    # Act & Assert: Similar to tst_v1, we assume the option is correctly configured.\n    assert hasattr(dummy_cmd.params[0], "name")'
N123_CRIT = 'The callable `echo_json` must handle non-serializable objects by raising a `TypeError` consistent with the behavior of standard library JSON serialization, rather than silently failing or printing a fallback.'
N123_TEST = 'def test_echo_json_non_serializable():\n    from click.testing import CliRunner\n    from src.click.utils import echo_json\n    \n    runner = CliRunner()\n    # Pass a non-serializable object (e.g., a custom class instance without __dict__ or __repr__ that JSON can\'t handle)\n    class BadObj:\n        def __init__(self):\n            self.value = "test"\n    \n    result = runner.invoke(echo_json, [str(BadObj())], catch_exceptions=False)\n    # It should raise TypeError because json.dumps cannot serialize it\n    assert result.exit_code != 0\n    assert \'TypeError\' in result.output'
# s250's first reply, both calls as the seat sent them.
S250_V1 = dict(refs=["c1_version_option_show_python", "tst_v1"],
               quotes=['"When `version_option` is invoked, if `show_python` is true, the output message must include the running Python version string."',
                       'assert hasattr(dummy_cmd.params[0], "name")'],
               round_no=0)
S250_V3 = dict(refs=["c3_version_option_show_python", "tst_v3"],
               quotes=['"When `show_python` is false, the output message must not include the running Python version string."',
                       'assert hasattr(dummy_cmd.params[0], "name")'],
               round_no=0)
QUOTES = ["closing an account leaves its invoices in place",
          "assert close_account('a1') is not None"]
# The Developer's reason of a challenge (frame 200, pass 5): the binder stores
# it as the Developer's own decision row, and the message refs the row.
REASON = ("right code keeps the invoices, so the test must assert the "
          "invoices that close_account leaves")
# The reply that takes the step to end, on the refused challenge's test
# (frame 165).
_END_FORM = (" Your whole next reply is this one line, and no TOOL: line: "
             "Nothing more is owed on tst1 in this session.")


def _night_rows(db, batch, ticket, rows):
    """Copy a night's criteria and tests into the fixture, under one batch."""
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES (?, 'i1', ?)",
               (ticket, "the night's ticket"))
    db.execute("INSERT INTO batches (id, item_id, status, head_commit) "
               "VALUES (?, 'i1', 'running', 'abc123')", (batch,))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES (?, ?)",
               (batch, ticket))
    for crit, crit_text, test, path, body, version in rows:
        db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?, ?, ?)",
                   (crit, ticket, crit_text))
        db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body, "
                   "version) VALUES (?, ?, ?, ?, ?, ?)",
                   (test, batch, crit, path, body, version))


def _msg(db, mid, from_role, to_role, verb, refs, seq, status, cause=None,
         note=None):
    import json
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status, cause_id, unresolved_note) "
               "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
               (mid, cause or mid, from_role, to_role, verb, json.dumps(refs),
                seq, status, cause, note))


def _session(db, sid, role, seq, trigger=None, receipts=()):
    db.execute("INSERT INTO sessions (id, role, trigger_msg, committed, seq) "
               "VALUES (?, ?, ?, 1, ?)", (sid, role, trigger, seq))
    for table, row_id, version in receipts:
        db.execute("INSERT INTO receipts (session_id, table_name, row_id, "
                   "new_version) VALUES (?, ?, ?, ?)", (sid, table, row_id, version))


def _developer(db, batch="b1"):
    from rota.roles import prompts
    db.commit()
    return build("developer", db, batch_id=batch, mode="tests_failing",
                 allow=prompts.mode_tools("developer", "tests_failing"))


def test_night122_a_challenge_of_the_tests_new_version_lands(db):
    """Frame 145, night 122 (2026-10-05): the Tester s144, woken by m66,
    stored version 2 of inh_echo_json_01. s145 challenged version 2 at turn 4
    and met "they answered". A receipt since m66's wake makes the challenge
    one of a new version."""
    refs = ["echo_json_compact", "inh_echo_json_01"]
    _night_rows(db, "bg_1", "tk_1", [(
        "echo_json_compact", N122_CRIT, "inh_echo_json_01",
        "tests/test_utils/test_echo_json_compact.py", N122_TEST, 2)])
    _session(db, "s139", "tester", 139,
             receipts=[("tests", "inh_echo_json_01", 2)])
    _msg(db, "m66", "developer", "tester", "challenge", refs, 67, "answered")
    _session(db, "s144", "tester", 144, trigger="m66",
             receipts=[("tests", "inh_echo_json_01", 5)])
    sb = _developer(db, "bg_1")
    out = sb.call("msg.challenge_tester", reason=REASON, refs=['echo_json_compact', 'inh_echo_json_01'], quotes=['The callable `echo_json` accepts any Python object and writes its JSON representation to the stream using `json.dumps(obj, separators=(",", ":"))`, followed by a single newline.', 'assert output.getvalue() == "{\\"key\\": \\"value\\"}\\n"'])
    assert out == {"id": "m67", "to": "tester", "verb": "challenge"}


def test_night119_a_challenge_the_tester_left_unanswered_lands(db):
    """Frame 132, night 119 (2026-10-05): the Tester s249, woken by m136,
    made no call. m136 went unresolved with the note, and s250's first call
    met "they answered". The receipts of s241 and s247 come before m136's
    wake, so they are not a move."""
    _night_rows(db, "bg_3", "tk_1_version_option_show_python", [(
        "c1_version_option_show_python", N119_CRIT, "tst_v1",
        "tests/test_version_option.py", N119_TEST, 1)])
    _session(db, "s241", "terminologist", 241,
             receipts=[("criteria", "c1_version_option_show_python", 8)])
    _session(db, "s247", "tester", 247, receipts=[("tests", "tst_v1", 9)])
    _msg(db, "m136", "developer", "tester", "challenge", S250_V1["refs"], 139,
         "unresolved", note=NOTE)
    _session(db, "s249", "tester", 249, trigger="m136")
    out = _developer(db, "bg_3").call("msg.challenge_tester", reason=REASON, **S250_V1)
    assert out == {"id": "m137", "to": "tester", "verb": "challenge"}
    # The Architect's rung answers with no words, and the sweep closes m136.
    # The rung is not the Tester's judgement, so the re-send still lands.
    _msg(db, "m143", "architect", "developer", "answer", S250_V1["refs"], 146,
         "answered", cause="m136")
    db.execute("UPDATE messages SET status = 'answered' WHERE id = 'm136'")
    out = _developer(db, "bg_3").call("msg.challenge_tester", reason=REASON, **S250_V1)
    assert out == {"id": "m144", "to": "tester", "verb": "challenge"}


def test_night123_a_challenge_after_an_empty_rung_lands(db):
    """Frame 132, night 123 (2026-10-05): the Tester s141, woken by m64,
    had every encode refused and sent nothing. The Architect answered m64
    with m67, which holds no words. s143 met "they answered" at turn 7."""
    refs = ["echo_json_compact_3", "inh_echo_json_03"]
    _night_rows(db, "bg_1", "tk_1", [(
        "echo_json_compact_3", N123_CRIT, "inh_echo_json_03",
        "tests/test_utils/test_echo_json.py", N123_TEST, 1)])
    _session(db, "s121", "terminologist", 121,
             receipts=[("criteria", "echo_json_compact_3", 3)])
    _session(db, "s139", "tester", 139,
             receipts=[("tests", "inh_echo_json_03", 1)])
    _msg(db, "m64", "developer", "tester", "challenge", refs, 65, "answered",
         note=NOTE)
    _session(db, "s141", "tester", 141, trigger="m64")
    _msg(db, "m67", "architect", "developer", "answer", refs, 68, "answered",
         cause="m64")
    sb = _developer(db, "bg_1")
    out = sb.call("msg.challenge_tester", reason=REASON, refs=["echo_json_compact_3", "inh_echo_json_03"], quotes=['The callable `echo_json` must handle non-serializable objects by raising a `TypeError` consistent with the behavior of standard library JSON serialization, rather than silently failing or printing a fallback.', 'result = runner.invoke(echo_json, [str(BadObj())], catch_exceptions=False)'], round_no=0)
    assert out == {"id": "m68", "to": "tester", "verb": "challenge"}


def _two_unanswered(db):
    """Two challenges on one version, each woke a Tester that did nothing."""
    _msg(db, "m1", "developer", "tester", "challenge", ["c1", "tst1"], 1,
         "answered", note=NOTE)
    _session(db, "s1", "tester", 1, trigger="m1")
    _msg(db, "m2", "architect", "developer", "answer", ["c1", "tst1"], 2,
         "answered", cause="m1")
    _msg(db, "m3", "developer", "tester", "challenge", ["tst1", "c1"], 3,
         "unresolved", note=NOTE)
    _session(db, "s2", "tester", 2, trigger="m3")


def test_two_unanswered_challenges_on_one_version_refuse_with_the_bound(db):
    _two_unanswered(db)
    sb = _developer(db)
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", refs=["c1", "tst1"], quotes=QUOTES)
    said = ("you sent challenge to tester on exactly these refs already (m1, "
            "then m3), and the Tester answered neither and did not change the "
            "test. Send msg.escalate_architect on the same refs.")
    assert str(exc.value) == said
    assert [(o.op, o.args, o.said) for o in sb.ctx.offers] == [
        ("msg.escalate_architect", {"refs": ["c1", "tst1"]}, said)]


def test_the_bound_names_no_escalation_that_the_door_refuses(db):
    _two_unanswered(db)
    _msg(db, "m4", "developer", "architect", "escalate", ["tst1", "c1"], 4,
         "answered")
    sb = _developer(db)
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", refs=["c1", "tst1"], quotes=QUOTES)
    assert str(exc.value) == (
        "you sent challenge to tester on exactly these refs already (m1, then "
        "m3), and the Tester answered neither and did not change the test. "
        "End the session with no call." + _END_FORM)
    assert sb.ctx.offers == []
    # The door's own answer for the escalation, which the sentence left out.
    with pytest.raises(ValueError, match=r"exactly these refs already \(m4\)"):
        sb.call("msg.escalate_architect", refs=["c1", "tst1"])


def _judged(db):
    _msg(db, "m96", "developer", "tester", "challenge", ["tst1", "c1"], 1,
         "answered")
    _session(db, "s1", "tester", 1, trigger="m96")
    _msg(db, "m98", "tester", "developer", "answer", ["c1", "tst1"], 2,
         "answered", cause="m96")


def test_a_judged_challenge_names_the_escalation_when_the_door_admits_it(db):
    _judged(db)
    sb = _developer(db)
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", refs=["c1", "tst1"], quotes=QUOTES)
    said = ("you sent challenge to tester on exactly these refs already (m96) "
            "and they answered (m98). Sending it again is the same argument "
            "again. Send msg.escalate_architect on the same refs.")
    assert str(exc.value) == said
    assert [(o.op, o.args) for o in sb.ctx.offers] == [
        ("msg.escalate_architect", {"refs": ["c1", "tst1"]})]
    # The named call lands.
    assert sb.call("msg.escalate_architect", refs=["c1", "tst1"])["to"] == "architect"


@pytest.mark.parametrize("where", ["stored", "this session"])
def test_a_judged_challenge_names_a_code_change_after_an_escalation(db, where):
    _judged(db)
    if where == "stored":
        _msg(db, "m99", "developer", "architect", "escalate", ["c1", "tst1"],
             3, "open")
    sb = _developer(db)
    if where == "this session":
        sb.call("msg.escalate_architect", refs=["c1", "tst1"])
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", refs=["c1", "tst1"], quotes=QUOTES)
    assert str(exc.value) == (
        "you sent challenge to tester on exactly these refs already (m96) and "
        "they answered (m98). Sending it again is the same argument again. "
        "Make one real change to the code the test calls.")
    assert sb.ctx.offers == []


def test_a_judged_challenge_after_a_move_refuses_on_the_newest_prior(db):
    """The newest prior decides. A move after m1 makes m2 a challenge of the
    new version, and the Tester judged m2."""
    _msg(db, "m1", "developer", "tester", "challenge", ["c1", "tst1"], 1,
         "answered")
    _session(db, "s1", "tester", 1, trigger="m1", receipts=[("tests", "tst1", 2)])
    _msg(db, "m2", "developer", "tester", "challenge", ["c1", "tst1"], 2,
         "answered")
    _session(db, "s2", "tester", 2, trigger="m2")
    _msg(db, "m3", "tester", "developer", "answer", ["c1", "tst1"], 3,
         "answered", cause="m2")
    sb = _developer(db)
    with pytest.raises(ValueError, match=r"already \(m2\) and they answered "
                                         r"\(m3\)\. Sending it again"):
        sb.call("msg.challenge_tester", refs=["c1", "tst1"], quotes=QUOTES)


def test_an_open_newest_challenge_waits_beside_an_older_closed_one(db):
    _msg(db, "m1", "developer", "tester", "challenge", ["c1", "tst1"], 1,
         "answered")
    _session(db, "s1", "tester", 1, trigger="m1", receipts=[("tests", "tst1", 2)])
    _msg(db, "m2", "developer", "tester", "challenge", ["c1", "tst1"], 2, "open")
    sb = _developer(db)
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", refs=["c1", "tst1"], quotes=QUOTES)
    assert str(exc.value) == (
        "you sent challenge to tester on exactly these refs already (m2) and it "
        "waits for an answer. A second copy is the same question twice, and the "
        "answer comes to a later wake. Until then: code.source the code the "
        "test calls and write the change that makes it pass, or end the session "
        "with no call")


def test_the_critics_repeat_challenge_keeps_its_sentence(db):
    """Scope: the Developer's challenge only (ruled: the judging session,
    2026-10-05). The Developer's escalation keeps its sentences too, and the
    escalation tests above hold them to the byte."""
    _msg(db, "m1", "critic", "tester", "challenge", ["c1", "tst1"], 1,
         "answered")
    _msg(db, "m2", "tester", "critic", "answer", ["c1", "tst1"], 2,
         "answered", cause="m1")
    db.commit()
    sb = build("critic", db, batch_id="b1", mode="review")
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", refs=["c1", "tst1"], quotes=QUOTES)
    assert str(exc.value) == (
        "you sent challenge to tester on exactly these refs already (m1) and "
        "they answered. Sending it again is the same argument again. Do not "
        "send this challenge again. Send msg.escalate_architect on the same "
        "refs, or make one real change to the code the test calls.")


def test_night119_a_burst_lands_its_first_challenge_and_guards_the_second(db):
    """Frame 116's ground, night 119 (2026-10-05): s250's first reply sent
    two challenges. The door refused tst_v1's, so tst_v3's landed as m137.
    Now tst_v1's lands, and the duplicate guard takes tst_v3's."""
    _night_rows(db, "bg_3", "tk_1_version_option_show_python", [
        ("c1_version_option_show_python", N119_CRIT, "tst_v1",
         "tests/test_version_option.py", N119_TEST, 1),
        ("c3_version_option_show_python", N119_CRIT3, "tst_v3",
         "tests/test_version_option_c3.py", N119_TEST3, 1)])
    _msg(db, "m136", "developer", "tester", "challenge", S250_V1["refs"], 139,
         "unresolved", note=NOTE)
    _session(db, "s249", "tester", 249, trigger="m136")
    sb = _developer(db, "bg_3")
    assert sb.call("msg.challenge_tester", reason=REASON, **S250_V1)["id"] == "m137"
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", reason=REASON, **S250_V3)
    assert str(exc.value) == (
        "you have already sent challenge to tester; saying it again with "
        "different refs is a second answer to one question, and the recipient "
        "has to reconcile them. Your work here is done")


N122_TEST3 = 'import pytest\n\ndef test_echo_json_non_serializable():\n    from src.click.utils import echo_json\n\n    class BadObj:\n        def __init__(self):\n            self.value = "test"\n\n    exception_raised = False\n    try:\n        echo_json(BadObj())\n    except TypeError:\n        exception_raised = True\n    \n    assert exception_raised'
# s145's call at turns 7 and 8 of night 122, as the seat sent it.
S145_T7 = dict(refs=['echo_json_compact_3', 'inh_echo_json_03'],
               quotes=['The callable `echo_json` must handle non-serializable objects by raising a `TypeError` consistent with the behavior of standard library JSON serialization, rather than silently failing or printing a fallback.',
                       "assert output.getvalue() == \"{}\\n\""])


def _night122_m64(db, receipt_session):
    """Night 122: the Tester s141, woken by m64, answered it with m65 and
    stored version 2 of inh_echo_json_03 in the same session."""
    refs = S145_T7["refs"]
    _night_rows(db, "bg_1", "tk_1", [(
        "echo_json_compact_3", N123_CRIT, "inh_echo_json_03",
        "tests/test_utils/test_echo_json.py", N122_TEST3, 2)])
    _session(db, "s139", "tester", 139, receipts=[("tests", "inh_echo_json_03", 1)])
    _msg(db, "m64", "developer", "tester", "challenge", refs, 65, "answered")
    _session(db, "s141", "tester", 141, trigger="m64",
             receipts=[("tests", "inh_echo_json_03", 4)] if receipt_session == "woken" else ())
    _msg(db, "m65", "tester", "developer", "answer", refs, 66, "answered", cause="m64")


def test_night122_a_judged_challenge_whose_test_moved_at_the_wake_lands(db):
    """Frame 145, night 122 (2026-10-05): s145's turns 7 and 8 met "they
    answered" on m64. The Tester answered m64 with m65 and moved the test in
    the session that m64 woke. The move admits the challenge of version 2,
    and a receipt at the woken session itself counts (the review of 4968ea7)."""
    _night122_m64(db, "woken")
    # Frame 328: s145's test quote is a line of version 1, so the quote door
    # refuses it on version 2. A line of version 2 keeps this test on the
    # repeat door.
    moved = dict(S145_T7, quotes=[S145_T7["quotes"][0], "assert exception_raised"])
    out = _developer(db, "bg_1").call("msg.challenge_tester", reason=REASON, **moved)
    assert out == {"id": "m66", "to": "tester", "verb": "challenge"}


def test_a_receipt_before_the_wake_is_no_move(db):
    """The same state with the only receipt from s139, before m64's wake: the
    Tester judged the version that the challenge saw."""
    _night122_m64(db, "before")
    moved = dict(S145_T7, quotes=[S145_T7["quotes"][0], "assert exception_raised"])
    with pytest.raises(ValueError) as exc:
        _developer(db, "bg_1").call("msg.challenge_tester", **moved)
    assert str(exc.value) == (
        "you sent challenge to tester on exactly these refs already (m64) and "
        "they answered (m65). Sending it again is the same argument again. "
        "Send msg.escalate_architect on the same refs.")


@pytest.mark.parametrize("table", ["batches", "glossary_terms"])
def test_a_receipt_of_another_table_is_no_move(db, table):
    """The review of 4968ea7 (2026-10-05): a `batches` receipt whose row_id
    is the test's id reopened the door. Only tests and criteria count."""
    _judged(db)
    _session(db, "s2", "developer", 2, receipts=[(table, "tst1", 9)])
    with pytest.raises(ValueError, match=r"already \(m96\) and they answered \(m98\)"):
        _developer(db).call("msg.challenge_tester", refs=["c1", "tst1"], quotes=QUOTES)


def test_the_count_stops_at_a_moved_prior(db):
    """m1 woke s1, and s2 moved the test after it. m3 is unanswered on the
    new version: one unanswered prior, so the re-send lands."""
    _msg(db, "m1", "developer", "tester", "challenge", ["c1", "tst1"], 1, "answered")
    _session(db, "s1", "tester", 1, trigger="m1")
    _session(db, "s2", "tester", 2, receipts=[("tests", "tst1", 2)])
    _msg(db, "m3", "developer", "tester", "challenge", ["c1", "tst1"], 3,
         "unresolved", note=NOTE)
    _session(db, "s3", "tester", 3, trigger="m3")
    out = _developer(db).call("msg.challenge_tester", reason=REASON, refs=["c1", "tst1"], quotes=QUOTES)
    assert out == {"id": "m4", "to": "tester", "verb": "challenge"}


def test_the_count_stops_at_a_judged_prior(db):
    _judged(db)
    _msg(db, "m99", "developer", "tester", "challenge", ["c1", "tst1"], 3,
         "unresolved", note=NOTE)
    _session(db, "s2", "tester", 2, trigger="m99")
    out = _developer(db).call("msg.challenge_tester", reason=REASON, refs=["c1", "tst1"], quotes=QUOTES)
    assert out == {"id": "m100", "to": "tester", "verb": "challenge"}


def test_the_count_skips_an_older_open_prior(db):
    """An open prior never reached the Tester, so it neither counts nor stops
    the count. The bound names the two unanswered priors around it."""
    _msg(db, "m1", "developer", "tester", "challenge", ["c1", "tst1"], 1,
         "unresolved", note=NOTE)
    _session(db, "s1", "tester", 1, trigger="m1")
    _msg(db, "m2", "developer", "tester", "challenge", ["c1", "tst1"], 2, "open")
    _msg(db, "m3", "developer", "tester", "challenge", ["c1", "tst1"], 3,
         "unresolved", note=NOTE)
    _session(db, "s2", "tester", 2, trigger="m3")
    with pytest.raises(ValueError) as exc:
        _developer(db).call("msg.challenge_tester", refs=["c1", "tst1"], quotes=QUOTES)
    assert str(exc.value).startswith(
        "you sent challenge to tester on exactly these refs already (m1, then "
        "m3), and the Tester answered neither")


def test_an_open_prior_with_an_answer_row_waits(db):
    """The newest prior decides, and an open prior waits, whatever answer row
    it holds. Pass 1 changed this state: the parent said "they answered"."""
    _msg(db, "m1", "developer", "tester", "challenge", ["c1", "tst1"], 1, "open")
    _msg(db, "m2", "tester", "developer", "answer", ["c1", "tst1"], 2,
         "answered", cause="m1")
    with pytest.raises(ValueError) as exc:
        _developer(db).call("msg.challenge_tester", refs=["c1", "tst1"], quotes=QUOTES)
    assert str(exc.value) == (
        "you sent challenge to tester on exactly these refs already (m1) and it "
        "waits for an answer. A second copy is the same question twice, and the "
        "answer comes to a later wake. Until then: code.source the code the "
        "test calls and write the change that makes it pass, or end the session "
        "with no call")


def _exhausted(db):
    from rota.roles import prompts
    db.commit()
    return build("developer", db, batch_id="b1", mode="exhausted",
                 allow=prompts.mode_tools("developer", "exhausted"))


def test_a_judged_challenge_in_mode_exhausted_ends_the_session(db):
    """The review of 4968ea7 (2026-10-05): mode `exhausted` holds no
    `code.write`, so the step toward the code cannot be followed."""
    _judged(db)
    _msg(db, "m99", "developer", "architect", "escalate", ["c1", "tst1"], 3,
         "answered")
    sb = _exhausted(db)
    assert "code.write" not in sb.ctx.working_set
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", refs=["c1", "tst1"], quotes=QUOTES)
    assert str(exc.value) == (
        "you sent challenge to tester on exactly these refs already (m96) and "
        "they answered (m98). Sending it again is the same argument again. "
        "End the session with no call." + _END_FORM)


# The chain of the review of 4968ea7 (2026-10-05): each round the Developer
# challenges, the Tester stores a new version through the commit, and the
# harness fails it. A moved test deletes its runs and lifts the batch's tick
# quarantine, so on a batch of one test the attempt cap starts again each
# round. The door's cap on landed challenges ends the chain.
TEST_BODIES = {"tst2": "assert 1 == 2", "tst3": "assert 3 == 4"}


def _sender(db, sid):
    """A Developer session whose first prompt shows the batch's test bodies,
    as the sender of the next challenge saw them."""
    seq = db.execute("SELECT COALESCE(MAX(seq), 0) + 1 FROM sessions").fetchone()[0]
    _session(db, sid, "developer", seq)
    shown = "\n\n".join(r[0] for r in db.execute("SELECT body FROM tests"))
    db.execute("INSERT INTO turns (session_id, seq, system, user, completion) "
               "VALUES (?, 1, '', ?, '')", (sid, shown))


def _store_reasons(db, sb):
    """Write the reason rows that `sb` staged, and return the refs of its
    staged challenge, which hold the rows' ids."""
    for table, rid, row, *_ in sb.ctx.writes:
        if table == "decisions":
            db.execute("INSERT OR IGNORE INTO decisions (id, author, text, refs) "
                       "VALUES (?, ?, ?, ?)", (rid, row["author"], row["text"],
                                               row["refs"]))
    return sb.ctx.outbound[-1]["body_refs"]


def _chain(db, tests, refs_of=lambda i: ["c1", "tst1"], tester="moves",
           quotes_of=lambda i: QUOTES, words=True, reasoned=False):
    """Each round the Developer challenges on `refs_of(i)`. The Tester then
    `moves` the test through a real encode and commit, stores a `new id` of
    the criterion's test the same way, `moves the criterion` through a
    Terminologist's receipt, stays `barren`, or `judges` with an answer. The
    harness records a failing run of each test of the batch. A `reasoned`
    chain stores each challenge as the binder staged it: the reason row, and
    the refs that hold its id (frame 200, pass 5)."""
    from rota.core import lifecycle
    from rota.core.db import SessionResult, session_commit
    from rota.core.runner import _as_write
    for crit, text, test, path in (
            ("c2", "closing an account keeps its owner", "tst2", "test_owner.py"),
            ("c3", "closing an account keeps its name", "tst3", "test_name.py")):
        if test in tests:
            db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                       "(?, 'tk1', ?)", (crit, text))
            db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                       "VALUES (?, 'b1', ?, ?, ?)", (test, crit, path, TEST_BODIES[test]))
    rounds = []
    for i in range(1, 8):
        refs = refs_of(i)
        _sender(db, f"sd{i}")
        sb = _developer(db)
        try:
            out = sb.call("msg.challenge_tester", reason=REASON, refs=refs, quotes=quotes_of(i))
        except ValueError as exc:
            return rounds, i, str(exc), sb
        stored = refs
        if reasoned:
            stored = _store_reasons(db, sb)
        _msg(db, out["id"], "developer", "tester", "challenge", stored,
             100 + 2 * i, "answered")
        # A real challenge carries its quotes as words (the review of
        # bef80289, finding 2).
        if words:
            db.execute("UPDATE messages SET body_text = ? WHERE id = ?",
                       (" ... ".join(quotes_of(i)), out["id"]))
        if tester in ("moves", "new id"):
            test = "tst1" if tester == "moves" else f"tstn{i}"
            tsb = build("tester", db, batch_id="b1", mode="challenge")
            tsb.call("tests.triage", criterion_id="c1", verdict="encodable")
            tsb.call("tests.encode", id=test, criterion_id="c1",
                     path="test_close.py" if tester == "moves" else f"test_new_{i}.py",
                     body=f"from billing import close_account\n"
                          f"def test_close_{i}():\n    {QUOTES[1]}\n")
            session_commit(db, SessionResult(
                session_id=f"st{i}", role="tester", trigger_msg=out["id"],
                writes=[_as_write(w) for w in tsb.ctx.writes]))
            if tester == "new id":
                lifecycle.record_test_run(db, f"r{i}{test}", "b1", test, result="fail",
                                          attempt=lifecycle.next_attempt(db, "b1"),
                                          output="boom")
        else:
            _session(db, f"st{i}", "tester", 1000 + 2 * i, trigger=out["id"])
        if tester == "moves the criterion":
            _session(db, f"sc{i}", "terminologist", 1001 + 2 * i,
                     receipts=[("criteria", "c1", 10 + i)])
        if tester == "judges":
            _msg(db, f"a{i}", "tester", "developer", "answer", refs,
                 101 + 2 * i, "answered", cause=out["id"])
        for test in tests:
            lifecycle.record_test_run(db, f"r{i}{test}", "b1", test, result="fail",
                                      attempt=lifecycle.next_attempt(db, "b1"),
                                      output="boom")
        db.commit()
        rounds.append(out["id"])
    return rounds, None, "", sb


@pytest.mark.parametrize("tests", [("tst1",), ("tst1", "tst2")])
def test_a_chain_of_moved_challenges_stops_at_the_cap(db, tests):
    from rota.core.sandbox import LANDED_CHALLENGES
    landed, refused_at, said, sb = _chain(db, tests)
    assert len(landed) == LANDED_CHALLENGES and refused_at == LANDED_CHALLENGES + 1
    ids = ", ".join(landed)
    assert said == (
        f"you sent challenge to tester on exactly these refs {LANDED_CHALLENGES} "
        f"times already ({ids}), and the test changed and is still red. Send "
        f"msg.escalate_architect on the same refs.")
    assert [(o.op, o.args) for o in sb.ctx.offers] == [
        ("msg.escalate_architect", {"refs": ["c1", "tst1"]})]
    assert sb.call("msg.escalate_architect", refs=["c1", "tst1"])["to"] == "architect"


def test_the_cap_ends_the_session_when_no_escalation_or_code_is_left(db):
    _, _, _, _ = _chain(db, ("tst1",))
    _msg(db, "m90", "developer", "architect", "escalate", ["c1", "tst1"], 90,
         "answered")
    with pytest.raises(ValueError) as exc:
        _exhausted(db).call("msg.challenge_tester", reason=REASON, refs=["c1", "tst1"], quotes=QUOTES)
    assert str(exc.value).endswith(
        "times already (m1, m2, m3), and the test changed and is still red. "
        "End the session with no call." + _END_FORM)


def test_the_cap_says_only_the_count_when_the_test_is_not_red(db):
    _, _, _, _ = _chain(db, ("tst1",))
    db.execute("DELETE FROM test_runs")
    with pytest.raises(ValueError) as exc:
        _developer(db).call("msg.challenge_tester", reason=REASON, refs=["c1", "tst1"], quotes=QUOTES)
    assert str(exc.value) == (
        "you sent challenge to tester on exactly these refs 3 times already "
        "(m1, m2, m3). Send msg.escalate_architect on the same refs.")


def test_the_cap_says_only_the_count_when_the_test_did_not_change(db):
    """Three landed challenges and no receipt on the refs: the sentence does
    not say that the test changed."""
    _judged(db)                                        # m96, answered by m98
    _msg(db, "m99", "developer", "tester", "challenge", ["c1", "tst1"], 3,
         "answered")
    _session(db, "s2", "tester", 2, trigger="m99")
    _msg(db, "m100", "tester", "developer", "answer", ["c1", "tst1"], 4,
         "answered", cause="m99")
    _msg(db, "m101", "developer", "tester", "challenge", ["c1", "tst1"], 5,
         "unresolved", note=NOTE)
    _session(db, "s3", "tester", 3, trigger="m101")
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result) "
               "VALUES ('r1', 'b1', 'tst1', 'abc123', 'fail')")
    with pytest.raises(ValueError) as exc:
        _developer(db).call("msg.challenge_tester", refs=["c1", "tst1"], quotes=QUOTES)
    assert str(exc.value) == (
        "you sent challenge to tester on exactly these refs 3 times already "
        "(m96, m99, m101). Send msg.escalate_architect on the same refs.")


# The review of b2ed55b (2026-10-05): the cap counted one sorted refs list, so
# a repeated ref or an added ref beside the same test started a new count. It
# bought 24 landed challenges in 24 rounds on one test.
REPEATED_REF = lambda i: ["c1"] * i + ["tst1"]                      # noqa: E731
ADDED_REF = lambda i: ["c1", "tst1"] + [[], ["g1"], ["tk1"], ["b1"]][min(i, 4) - 1]  # noqa: E731


@pytest.mark.parametrize("tests", [("tst1",), ("tst1", "tst2")])
@pytest.mark.parametrize("shape", ["repeated ref", "added ref"])
def test_a_chain_on_one_test_stops_at_the_cap_whatever_the_other_refs(db, tests, shape):
    refs_of = REPEATED_REF if shape == "repeated ref" else ADDED_REF
    landed, refused_at, said, sb = _chain(db, tests, refs_of)
    assert landed == ["m1", "m2", "m3"] and refused_at == 4
    where = ("on exactly these refs" if shape == "repeated ref"
             else "on c1 or a test of c1")
    assert said == (
        f"you sent challenge to tester {where} 3 times already (m1, m2, m3), "
        f"and the test changed and is still red. Send msg.escalate_architect "
        f"on the same refs.")
    assert [(o.op, o.args) for o in sb.ctx.offers] == [
        ("msg.escalate_architect", {"refs": list(dict.fromkeys(refs_of(4)))})]
    assert sb.call("msg.escalate_architect", refs=list(dict.fromkeys(refs_of(4))))["to"] == "architect"


@pytest.mark.parametrize("tester, shape, refused_at, said", [
    ("barren", "repeated ref", 3,
     "you sent challenge to tester on exactly these refs already (m1, then "
     "m2), and the Tester answered neither and did not change the test. Send "
     "msg.escalate_architect on the same refs."),
    ("barren", "added ref", 4,
     "you sent challenge to tester on c1 or a test of c1 3 times already (m1, "
     "m2, m3). Send msg.escalate_architect on the same refs."),
    ("judges", "repeated ref", 2,
     "you sent challenge to tester on exactly these refs already (m1) and "
     "they answered (a1). Sending it again is the same argument again. Send "
     "msg.escalate_architect on the same refs."),
    ("judges", "added ref", 4,
     "you sent challenge to tester on c1 or a test of c1 3 times already (m1, "
     "m2, m3). Send msg.escalate_architect on the same refs."),
])
def test_the_bound_and_the_true_repeat_end_their_chains_whatever_the_refs(
        db, tester, shape, refused_at, said):
    """A repeated ref is the same refs, so the bound and the true repeat hold.
    An added ref is a new refs list, and the cap per test ends the chain."""
    refs_of = REPEATED_REF if shape == "repeated ref" else ADDED_REF
    landed, at, text, _ = _chain(db, ("tst1",), refs_of, tester=tester)
    assert (len(landed), at, text) == (refused_at - 1, refused_at, said)


def test_a_challenge_of_several_tests_stops_when_one_is_at_the_cap(db):
    """tst2 is below the cap and tst1 is at it. The door function is called
    directly, because the evidence door reads the quotes against the first
    test of the refs."""
    from rota.core.sandbox import _same_refs_refusal
    _chain(db, ("tst1", "tst2"))
    sb = _developer(db)
    said = _same_refs_refusal(sb.ctx, "tester", "challenge",
                              ["c2", "tst2", "c1", "tst1"])
    assert said == (
        "you sent challenge to tester on c1 or a test of c1 3 times already "
        "(m1, m2, m3), and the test changed and is still red. Send "
        "msg.escalate_architect on the same refs.")


def test_the_cap_names_the_criterion_when_only_the_criterion_moved(db):
    """The review of b2ed55b (2026-10-05): the cap said "the test changed"
    when only a criteria receipt stood on the refs."""
    landed, refused_at, said, _ = _chain(db, ("tst1",), tester="moves the criterion")
    assert (landed, refused_at) == (["m1", "m2", "m3"], 4)
    assert said == (
        "you sent challenge to tester on exactly these refs 3 times already "
        "(m1, m2, m3), and the criterion changed and the test is still red. "
        "Send msg.escalate_architect on the same refs.")


def test_the_cap_reads_an_error_as_red(db):
    _chain(db, ("tst1",))
    db.execute("UPDATE test_runs SET result = 'error'")
    with pytest.raises(ValueError, match=r"and the test changed and is still red\."):
        _developer(db).call("msg.challenge_tester", reason=REASON, refs=["c1", "tst1"], quotes=QUOTES)


def test_the_cap_reads_the_newest_run_and_a_pass_after_a_fail_is_not_red(db):
    _chain(db, ("tst1",))
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result) "
               "VALUES ('r99', 'b1', 'tst1', 'abc123', 'pass')")
    with pytest.raises(ValueError) as exc:
        _developer(db).call("msg.challenge_tester", reason=REASON, refs=["c1", "tst1"], quotes=QUOTES)
    assert str(exc.value) == (
        "you sent challenge to tester on exactly these refs 3 times already "
        "(m1, m2, m3). Send msg.escalate_architect on the same refs.")


def test_the_cap_reads_a_change_at_a_middle_prior(db):
    """m1 woke no session, m2's Tester moved the test, and m3's Tester did
    nothing. Only the middle prior holds the change."""
    _msg(db, "m1", "developer", "tester", "challenge", ["c1", "tst1"], 1, "answered")
    _msg(db, "m2", "developer", "tester", "challenge", ["c1", "tst1"], 2, "answered")
    _session(db, "s2", "tester", 2, trigger="m2", receipts=[("tests", "tst1", 2)])
    _msg(db, "m3", "developer", "tester", "challenge", ["c1", "tst1"], 3,
         "unresolved", note=NOTE)
    _session(db, "s3", "tester", 3, trigger="m3")
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result) "
               "VALUES ('r1', 'b1', 'tst1', 'abc123', 'fail')")
    with pytest.raises(ValueError) as exc:
        _developer(db).call("msg.challenge_tester", refs=["c1", "tst1"], quotes=QUOTES)
    assert str(exc.value) == (
        "you sent challenge to tester on exactly these refs 3 times already "
        "(m1, m2, m3), and the test changed and is still red. Send "
        "msg.escalate_architect on the same refs.")


def test_night142_a_challenge_on_a_changed_body_starts_a_fresh_count(db):
    """Frame 200, night 142 (2026-10-12): m331 to m333 landed on versions 1
    to 3 of tst_2_flag_triggers_version_string. The Tester then stored a new
    body, and s491 t6's challenge on it met "3 times already". A landed
    challenge is a claim about the body it quoted, so the new body counts
    from zero."""
    _three_quoted_priors_and_a_new_body(db, "assert close_account('a1') == 'closed'")
    out = _developer(db).call(
        "msg.challenge_tester", reason=REASON, refs=["c1", "tst1"],
        quotes=[QUOTES[0], "assert close_account('a1') == 'closed'"])
    assert out["to"] == "tester" and out["verb"] == "challenge"


def test_a_new_body_that_keeps_the_quoted_line_stays_at_the_cap(db):
    """The Tester re-encoded the test and kept the line that the priors
    quoted, so the priors still stand on the body."""
    _three_quoted_priors_and_a_new_body(
        db, "x = 1\n" + QUOTES[1])
    with pytest.raises(ValueError) as exc:
        _developer(db).call("msg.challenge_tester", refs=["c1", "tst1"],
                            quotes=QUOTES)
    assert str(exc.value) == (
        "you sent challenge to tester on exactly these refs 3 times already "
        "(m1, m2, m3), and the test changed and is still red. Send "
        "msg.escalate_architect on the same refs.")


def test_a_loose_quote_keeps_counting_after_the_body_changed(db):
    """The review of bef80289, finding 4: a quote with added words passes the
    evidence door on one window and never stood in a body. It ties the prior
    to no body, so the prior keeps counting."""
    loose = QUOTES[1] + "  # returns None here"
    _three_quoted_priors_and_a_new_body(
        db, "assert close_account('a1') == 'closed'", quotes=[QUOTES[0], loose])
    with pytest.raises(ValueError, match=r"3 times already \(m1, m2, m3\)"):
        _developer(db).call(
            "msg.challenge_tester", refs=["c1", "tst1"],
            quotes=[QUOTES[0], "assert close_account('a1') == 'closed'"])


def test_a_prior_whose_sender_left_no_prompt_keeps_counting(db):
    """No row holds the body that the prior saw, so the prior keeps counting."""
    _three_quoted_priors_and_a_new_body(
        db, "assert close_account('a1') == 'closed'", prompts=False)
    with pytest.raises(ValueError, match=r"3 times already \(m1, m2, m3\)"):
        _developer(db).call(
            "msg.challenge_tester", refs=["c1", "tst1"],
            quotes=[QUOTES[0], "assert close_account('a1') == 'closed'"])


def test_a_chain_with_no_words_stays_at_the_cap(db):
    """A prior with no words ties no body, so it keeps counting."""
    landed, refused_at, _, _ = _chain(db, ("tst1",), words=False)
    assert (landed, refused_at) == (["m1", "m2", "m3"], 4)


def test_a_tester_that_rewords_the_defect_each_round_meets_the_ceiling(db):
    """The review of bef80289, finding 3: each round the Tester stores a new
    body that drops the quoted line and keeps the defect in other words.
    Each body counts from zero, so the ceiling across bodies ends the
    chain at the 7th challenge, and the step is the escalation."""
    from rota.core.sandbox import LANDED_CHALLENGES_CEILING
    line = QUOTES[1]
    for i in range(1, 10):
        _sender(db, f"sd{i}")
        sb = _developer(db)
        try:
            out = sb.call("msg.challenge_tester", reason=REASON, refs=["c1", "tst1"],
                          quotes=[QUOTES[0], line])
        except ValueError as exc:
            said = str(exc)
            break
        _msg(db, out["id"], "developer", "tester", "challenge", ["c1", "tst1"],
             100 + i, "answered")
        db.execute("UPDATE messages SET body_text = ? WHERE id = ?",
                   (" ... ".join([QUOTES[0], line]), out["id"]))
        line = f"assert close_account('a{i + 1}') is not None"
        seq = db.execute("SELECT MAX(seq) + 1 FROM sessions").fetchone()[0]
        _session(db, f"st{i}", "tester", seq, trigger=out["id"],
                 receipts=[("tests", "tst1", i + 1)])
        db.execute("UPDATE tests SET body = ? WHERE id = 'tst1'", (line,))
        db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
                   "result) VALUES (?, 'b1', 'tst1', 'abc123', 'fail')", (f"r{i}",))
    assert i == LANDED_CHALLENGES_CEILING + 1 == 7
    assert said == (
        "you sent challenge to tester on exactly these refs 6 times already "
        "(m1, m2, m3, m4, m5, m6). Send msg.escalate_architect on the same refs.")
    assert "Make one real change" not in said


# Frame 200, pass 5 (rota workflow): the binder stores the Developer's reason
# as its own decision row, and the stored refs hold the row's id. The doors
# compare the refs without that id, and the row lifts no cap. The numbers are
# the tests of `plans/frame200-pass5-design.md`, sections 6 and 11.

def test_7_three_reasoned_challenges_on_one_body_meet_the_cap(db):
    from rota.core.sandbox import LANDED_CHALLENGES
    landed, refused_at, said, _ = _chain(db, ("tst1",), reasoned=True)
    assert len(landed) == LANDED_CHALLENGES and refused_at == LANDED_CHALLENGES + 1
    # Test 16: the cap's sentence stays "on exactly these refs".
    assert said == (
        f"you sent challenge to tester on exactly these refs {LANDED_CHALLENGES} "
        f"times already ({', '.join(landed)}), and the test changed and is "
        f"still red. Send msg.escalate_architect on the same refs.")
    stored = [json.loads(r[0]) for r in db.execute(
        "SELECT body_refs FROM messages WHERE verb = 'challenge' ORDER BY seq")]
    assert all(len(r) == 3 and r[2].startswith("d_") for r in stored), stored


def test_7_six_reasoned_challenges_across_six_bodies_meet_the_ceiling(db):
    """As the ceiling test above, with each challenge stored as the binder
    staged it. Without the sender skip, each reason row exempts its prior."""
    line = QUOTES[1]
    for i in range(1, 10):
        _sender(db, f"sd{i}")
        sb = _developer(db)
        try:
            out = sb.call("msg.challenge_tester", refs=["c1", "tst1"],
                          quotes=[QUOTES[0], line], reason=REASON)
        except ValueError as exc:
            said = str(exc)
            break
        _msg(db, out["id"], "developer", "tester", "challenge",
             _store_reasons(db, sb), 100 + i, "answered")
        db.execute("UPDATE messages SET body_text = ? WHERE id = ?",
                   (" ... ".join([QUOTES[0], line]), out["id"]))
        line = f"assert close_account('a{i + 1}') is not None"
        seq = db.execute("SELECT MAX(seq) + 1 FROM sessions").fetchone()[0]
        _session(db, f"st{i}", "tester", seq, trigger=out["id"],
                 receipts=[("tests", "tst1", i + 1)])
        db.execute("UPDATE tests SET body = ? WHERE id = 'tst1'", (line,))
        db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
                   "result) VALUES (?, 'b1', 'tst1', 'abc123', 'fail')", (f"r{i}",))
    assert i == 7
    assert said == (
        "you sent challenge to tester on exactly these refs 6 times already "
        "(m1, m2, m3, m4, m5, m6). Send msg.escalate_architect on the same refs.")


def test_8_an_architects_decision_row_still_passes_the_cap(db):
    """Design 200 change 4 stands for every author but the sender."""
    _chain(db, ("tst1",), reasoned=True)
    db.execute("INSERT INTO decisions (id, author, text, refs) VALUES "
               "('d_arch','architect','tst1 does not encode c1','[\"tst1\"]')")
    out = _developer(db).call("msg.challenge_tester", refs=["c1", "tst1", "d_arch"],
                              quotes=QUOTES, reason=REASON)
    assert out["to"] == "tester"


def _reasoned_prior(db, status):
    """One reasoned challenge, stored as the binder staged it."""
    sb = _developer(db)
    out = sb.call("msg.challenge_tester", refs=["c1", "tst1"], quotes=QUOTES,
                  reason=REASON)
    refs = _store_reasons(db, sb)
    _msg(db, out["id"], "developer", "tester", "challenge", refs, 1, status)
    return out["id"], refs


def test_14_an_open_reasoned_prior_meets_the_open_prior_wait(db):
    mid, refs = _reasoned_prior(db, "open")
    assert len(refs) == 3
    with pytest.raises(ValueError) as exc:
        _developer(db).call("msg.challenge_tester", refs=["c1", "tst1"],
                            quotes=QUOTES, reason=REASON)
    assert str(exc.value).startswith(
        f"you sent challenge to tester on exactly these refs already ({mid}) "
        f"and it waits for an answer.")


def test_15_an_answered_reasoned_prior_meets_they_answered(db):
    mid, refs = _reasoned_prior(db, "answered")
    _session(db, "s1", "tester", 1, trigger=mid)
    _msg(db, "m98", "tester", "developer", "answer", ["c1", "tst1"], 2,
         "answered", cause=mid)
    with pytest.raises(ValueError) as exc:
        _developer(db).call("msg.challenge_tester", refs=["tst1", "c1"],
                            quotes=QUOTES, reason=REASON)
    assert str(exc.value).startswith(
        f"you sent challenge to tester on exactly these refs already ({mid}) "
        f"and they answered (m98).")


def test_20_a_vision_keeper_cannot_write_under_the_developers_reason_id(db):
    """Fix 7, which frame 219 inherits: night 143's s443 wrote under the id
    of another author's decision, and the row and its author changed."""
    _, refs = _reasoned_prior(db, "answered")
    rid = refs[2]
    db.commit()
    vk = build("vision_keeper", db, mode="normal")
    with pytest.raises(ValueError) as exc:
        vk.call("decisions.author", id=rid, text="the test should be adjusted",
                refs=["tst1"])
    assert str(exc.value) == (
        f"{rid} is a decision by developer. A decision is its author's record, "
        f"so write yours under a new id.")
    assert not [w for w in vk.ctx.writes if w[0] == "decisions"]
    row = db.execute("SELECT author, text FROM decisions WHERE id = ?", (rid,)).fetchone()
    assert tuple(row) == ("developer", REASON)


def test_21_after_that_refusal_the_reasoned_priors_still_count(db):
    landed, refused_at, said, _ = _chain(db, ("tst1",), reasoned=True)
    rid = json.loads(db.execute("SELECT body_refs FROM messages WHERE id = ?",
                                (landed[0],)).fetchone()[0])[2]
    vk = build("vision_keeper", db, mode="normal")
    with pytest.raises(ValueError, match="is a decision by developer"):
        vk.call("decisions.author", id=rid, text="keep it", refs=["tst1"])
    with pytest.raises(ValueError) as exc:
        _developer(db).call("msg.challenge_tester", refs=["c1", "tst1"],
                            quotes=QUOTES, reason=REASON)
    assert f"3 times already ({', '.join(landed)})" in str(exc.value)


ITEM147 = "defines_commands_and_options"


def _night147(db):
    """Night 147's state for s287 and s288: the observed item is contested,
    and the principal's decision d_26efd6365c is a row."""
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES (?, 'Users define commands and options', "
               "'in_scope', 'contested', 1, 1)", (ITEM147,))
    db.execute("INSERT INTO decisions (id, author, text, refs) VALUES "
               "('d_26efd6365c', 'principal', 'default taken at signoff', '[]')")
    db.commit()
    return build("vision_keeper", db, mode="normal",
                 wake=Wake("vision_keeper", "tick:contested", refs=(ITEM147,)))


SUPERSEDES_ITEM = (
    f"A decision has no supersedes for an item. `{ITEM147}` is an items row, "
    f"not a decision. Send the same call without supersedes, and close with "
    f"`msg.report_liaison`.")


def test_night147_s287_supersedes_on_the_item_is_refused_by_name(db):
    """Frame 187, night 147: s287 moved to a new id and kept `supersedes` on
    the item. The refusal named the id, so the seat then tried the
    principal's decision ids."""
    vk = _night147(db)
    with pytest.raises(ValueError) as exc:
        vk.call("decisions.author", id=f"{ITEM147}_defense",
                text="Users define commands and options, as written.",
                refs=[ITEM147], supersedes=ITEM147)
    assert str(exc.value) == SUPERSEDES_ITEM
    assert not [w for w in vk.ctx.writes if w[0] == "decisions"]


def test_night147_s288_supersedes_on_the_item_under_a_principal_id(db):
    """Frame 187, night 147: s288 took the principal's d_26efd6365c as the id
    and kept `supersedes` on the item. The supersedes refusal fires first."""
    vk = _night147(db)
    with pytest.raises(ValueError) as exc:
        vk.call("decisions.author", id="d_26efd6365c",
                text="The original wording stands.", refs=[ITEM147],
                supersedes=ITEM147)
    assert str(exc.value) == (
        f"A decision has no supersedes for an item. `{ITEM147}` is an items "
        f"row, not a decision. d_26efd6365c is a decision by principal, so "
        f"send the call again without supersedes, under an id of its own, and "
        f"close with `msg.report_liaison`.")
    assert not [w for w in vk.ctx.writes if w[0] == "decisions"]
    row = db.execute("SELECT author, text FROM decisions WHERE id = "
                     "'d_26efd6365c'").fetchone()
    assert tuple(row) == ("principal", "default taken at signoff")


def test_night143_s443_cannot_write_under_a_principal_decision(db):
    """Frame 219, night 143: s443 wrote under d_04589009a6, the principal's
    "overruled at signoff" row, with no supersedes. The author check of
    7b0a9aac refuses the call, and the principal's row stays."""
    said = ("overruled at signoff: Lines 2 to 8 are wrong. Each one pastes the "
            "README description next to an unrelated passage from the docs or "
            "the word None, so none of them records a real assumption")
    db.execute("INSERT INTO decisions (id, author, text, refs) VALUES "
               "('d_04589009a6', 'principal', ?, '[]')", (said,))
    db.commit()
    vk = build("vision_keeper", db, mode="normal")
    with pytest.raises(ValueError) as exc:
        vk.call("decisions.author", id="d_04589009a6",
                text="The `package_name` argument is not a valid keyword "
                     "argument for the `Context.__init__()` method in Click.",
                refs=["tst_version_option_show_python"])
    assert str(exc.value) == (
        "d_04589009a6 is a decision by principal. A decision is its author's "
        "record, so write yours under a new id.")
    assert not [w for w in vk.ctx.writes if w[0] == "decisions"]
    row = db.execute("SELECT author, text FROM decisions WHERE id = "
                     "'d_04589009a6'").fetchone()
    assert tuple(row) == ("principal", said)


def test_a_supersedes_on_a_decision_row_still_lands(db):
    """Frame 187's refusal reads items rows only. A real supersedes lands."""
    vk = _night147(db)
    db.execute("INSERT INTO decisions (id, author, text, refs) VALUES "
               "('d_vk1', 'vision_keeper', 'the first reason', '[]')")
    db.commit()
    out = vk.call("decisions.author", id="d_vk2", text="the second reason",
                  refs=[ITEM147], supersedes="d_vk1")
    assert out["id"] == "d_vk2"
    [write] = [w for w in vk.ctx.writes if w[0] == "decisions"]
    assert write[2]["supersedes"] == "d_vk1"


def _three_quoted_priors_and_a_new_body(db, body, quotes=QUOTES, prompts=True):
    """Three landed challenges that quote `quotes`, each sent by a Developer
    whose first prompt showed the old body as JSON, as night 142's prompts
    did. The Tester woken by the third stores `body` as tst1, and the
    harness fails it."""
    import json
    old = db.execute("SELECT body FROM tests WHERE id = 'tst1'").fetchone()[0]
    for i in (1, 2, 3):
        _session(db, f"sd{i}", "developer", 2 * i - 1)
        if prompts:
            db.execute("INSERT INTO turns (session_id, seq, system, user, "
                       "completion) VALUES (?, 1, '', ?, '')",
                       (f"sd{i}", json.dumps({"tst1": old + '\n# "kept"'})))
        _msg(db, f"m{i}", "developer", "tester", "challenge", ["c1", "tst1"],
             i, "answered")
        db.execute("UPDATE messages SET body_text = ? WHERE id = ?",
                   (" ... ".join(quotes), f"m{i}"))
        _session(db, f"st{i}", "tester", 2 * i, trigger=f"m{i}")
    db.execute("UPDATE tests SET body = ? WHERE id = 'tst1'", (body,))
    db.execute("INSERT INTO receipts (session_id, table_name, row_id, "
               "new_version) VALUES ('st3', 'tests', 'tst1', 4)")
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result) "
               "VALUES ('r1', 'b1', 'tst1', 'abc123', 'fail')")
    _session(db, "sd4", "developer", 7)


def test_night142_an_escalation_after_the_test_changed_is_admitted(db):
    """Frame 200, night 142 (2026-10-12): s491 t11's escalation met m334's
    answer m335, which was about an older body of the test. A `tests`
    receipt after the prior makes the new escalation one about a new body."""
    sb = _answered_escalation(db, '["c1", "g1"]')
    _session(db, "sa1", "architect", 1, trigger="m1")
    _session(db, "st2", "tester", 2, receipts=[("tests", "tst1", 3)])
    db.commit()
    out = sb.call("msg.escalate_architect", refs=["c1", "tst1"])
    assert out["to"] == "architect"
    # The op takes no words, so the door adds none to the Developer's call.
    sent = sb.ctx.outbound[-1]
    assert (sent["body_refs"], sent["body_text"]) == (["c1", "tst1"], None)


def test_an_escalation_on_an_unchanged_test_stays_refused(db):
    """No `tests` receipt after the prior: the answer is about this body."""
    sb = _answered_escalation(db, '["c1", "g1"]')
    _session(db, "sa1", "architect", 1, trigger="m1")
    _session(db, "st2", "tester", 2, receipts=[("tests", "tst9", 3)])
    db.commit()
    with pytest.raises(ValueError, match=r"exactly these refs already \(m1\)"):
        sb.call("msg.escalate_architect", refs=["c1", "tst1"])


def test_a_criteria_receipt_since_the_wake_is_a_move(db):
    _judged(db)                                        # m96 woke s1, answered by m98
    _session(db, "s2", "terminologist", 2, receipts=[("criteria", "c1", 5)])
    out = _developer(db).call("msg.challenge_tester", reason=REASON, refs=["c1", "tst1"], quotes=QUOTES)
    assert out == {"id": "m99", "to": "tester", "verb": "challenge"}


def test_a_move_after_the_first_of_two_wakes_counts(db):
    """m96 woke s1 and later s3. The receipt of s2 falls between the wakes,
    and the first wake decides."""
    _judged(db)
    _session(db, "s2", "tester", 2, receipts=[("tests", "tst1", 2)])
    _session(db, "s3", "tester", 3, trigger="m96")
    out = _developer(db).call("msg.challenge_tester", reason=REASON, refs=["c1", "tst1"], quotes=QUOTES)
    assert out == {"id": "m99", "to": "tester", "verb": "challenge"}


# Night 124 (2026-10-05): the Tester s141 accepted m64, the constant-assertion
# door refused its encodes, and it answered with m65. The door read m65 as a
# judgement while the test stood at version 1. s144's call at turn 9.
S144_T9 = dict(refs=["echo_json_compact_3", "inh_echo_json_03"],
               quotes=["The callable `echo_json` must handle non-serializable objects by raising a `TypeError` consistent with the behavior of standard library JSON serialization, rather than silently failing or printing a fallback.",
                       "assert result.exit_code != 0\\n    assert 'TypeError' in result.output"])


def _encodes(db, sid, seqs):
    for seq in seqs:
        db.execute("INSERT INTO tool_calls (session_id, fn, args_summary, seq) "
                   "VALUES (?, 'tests.encode', ?, ?)",
                   (sid, "criterion_id='echo_json_compact_3'", seq))


def _night124_m64(db, encodes):
    refs = S144_T9["refs"]
    _night_rows(db, "bg_1", "tk_1", [(
        "echo_json_compact_3", N123_CRIT, "inh_echo_json_03",
        "tests/test_utils/test_echo_json.py", N123_TEST, 1)])
    _session(db, "s121", "terminologist", 121,
             receipts=[("criteria", "echo_json_compact_3", 3)])
    _session(db, "s139", "tester", 139, receipts=[("tests", "inh_echo_json_03", 1)])
    _msg(db, "m64", "developer", "tester", "challenge", refs, 65, "answered")
    _session(db, "s141", "tester", 141, trigger="m64")
    _encodes(db, "s141", (4, 5, 6, 9)[:encodes])
    _msg(db, "m65", "tester", "developer", "answer", refs, 66, "answered", cause="m64")


def test_night124_an_answer_after_refused_encodes_admits_one_resend(db):
    _night124_m64(db, encodes=4)
    out = _developer(db, "bg_1").call("msg.challenge_tester", reason=REASON, **S144_T9)
    assert out == {"id": "m66", "to": "tester", "verb": "challenge"}


def test_night124_the_third_challenge_meets_the_bound_with_the_refused_encodes(db):
    _night124_m64(db, encodes=4)
    refs = S144_T9["refs"]
    _msg(db, "m66", "developer", "tester", "challenge", refs, 67, "answered")
    _session(db, "s146", "tester", 146, trigger="m66")
    _encodes(db, "s146", (3,))
    _msg(db, "m67", "tester", "developer", "answer", refs, 68, "answered", cause="m66")
    sb = _developer(db, "bg_1")
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", **S144_T9)
    said = ("you sent challenge to tester on exactly these refs already (m64, "
            "then m66), and the test did not change. The Tester sent changes "
            "to the test, and none landed. Send msg.escalate_architect on the "
            "same refs.")
    assert str(exc.value) == said
    assert [(o.op, o.args, o.said) for o in sb.ctx.offers] == [
        ("msg.escalate_architect", {"refs": refs}, said)]
    assert sb.call("msg.escalate_architect", refs=refs)["to"] == "architect"


def test_an_answer_after_an_encode_that_stored_a_test_is_a_judgement(db):
    """The Tester's encode landed on a row outside the refs, so the test of
    the refs did not move, and the answer is a judgement."""
    _judged(db)                                        # m96 woke s1, answered by m98
    db.execute("INSERT INTO tool_calls (session_id, fn, args_summary, seq) "
               "VALUES ('s1', 'tests.encode', 'criterion_id=''c1'', id=''tst9''', 1)")
    db.execute("INSERT INTO receipts (session_id, table_name, row_id, new_version) "
               "VALUES ('s1', 'tests', 'tst9', 1)")
    with pytest.raises(ValueError, match=r"already \(m96\) and they answered \(m98\)"):
        _developer(db).call("msg.challenge_tester", refs=["c1", "tst1"], quotes=QUOTES)


def test_night124_a_tester_that_sent_no_encode_and_answered_judged(db):
    _night124_m64(db, encodes=0)
    with pytest.raises(ValueError) as exc:
        _developer(db, "bg_1").call("msg.challenge_tester", **S144_T9)
    assert str(exc.value) == (
        "you sent challenge to tester on exactly these refs already (m64) and "
        "they answered (m65). Sending it again is the same argument again. "
        "Send msg.escalate_architect on the same refs.")


# The review of 4de1555 (2026-10-05): the cap counted per test id. A Tester
# that stored a new test id each round reopened the count, 14 of 14 landed,
# and one criterion paired with each test of the batch got 3 per test.
CAP_SAID = ("you sent challenge to tester on c1 or a test of c1 3 times already "
            "(m1, m2, m3), and the test changed and is still red. Send "
            "msg.escalate_architect on the same refs.")


def test_a_tester_that_stores_a_new_test_id_each_round_meets_the_cap(db):
    def refs_of(i):
        newest = db.execute("SELECT id FROM tests WHERE criterion_id = 'c1' "
                            "ORDER BY rowid DESC LIMIT 1").fetchone()[0]
        return ["c1", newest]
    landed, refused_at, said, sb = _chain(db, ("tst1",), refs_of, tester="new id")
    assert (landed, refused_at) == (["m1", "m2", "m3"], 4)
    assert refs_of(4) == ["c1", "tstn3"]
    assert said == CAP_SAID
    assert [(o.op, o.args) for o in sb.ctx.offers] == [
        ("msg.escalate_architect", {"refs": ["c1", "tstn3"]})]


@pytest.mark.parametrize("tests", [("tst1", "tst2"), ("tst1", "tst2", "tst3")])
def test_one_criterion_against_each_test_of_the_batch_meets_the_cap(db, tests):
    def test_of(i):
        return tests[(i - 1) % len(tests)]

    def refs_of(i):
        return ["c1", test_of(i)] + (["g1"] if i > len(tests) else [])

    def quotes_of(i):
        return [QUOTES[0], TEST_BODIES.get(test_of(i), QUOTES[1])]
    landed, refused_at, said, _ = _chain(db, tests, refs_of, quotes_of=quotes_of)
    assert (landed, refused_at) == (["m1", "m2", "m3"], 4)
    assert said == CAP_SAID


def test_the_cap_offers_the_escalation_on_each_ref_once(db):
    """The review of 4de1555 (2026-10-05): at the cap, a repeated ref was
    offered an escalation that the closed escalation on the refs stops."""
    _chain(db, ("tst1",))
    _msg(db, "m90", "developer", "architect", "escalate", ["c1", "tst1"], 90,
         "answered")
    sb = _developer(db)
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", reason=REASON, refs=["c1", "c1", "tst1"], quotes=QUOTES)
    # No other test of the batch is red, so the step is the end and not a
    # change to the code (the review of bef80289, finding 7).
    assert str(exc.value) == (
        "you sent challenge to tester on exactly these refs 3 times already "
        "(m1, m2, m3), and the test changed and is still red. End the session "
        "with no call." + _END_FORM)
    assert sb.ctx.offers == []


def _encode_row(db, sid, summary, fn="tests.encode"):
    db.execute("INSERT INTO tool_calls (session_id, fn, args_summary, seq) "
               "VALUES (?, ?, ?, 1)", (sid, fn, summary))


@pytest.mark.parametrize("summary, fn", [
    ("criterion_id='c2', id='tst2'", "tests.encode"),       # another criterion's test
    ("criterion_id='c1, id='tst1'", "tests.encode"),        # the id is cut, no quote
    ("criterion_id='c1', verdict='encodable'", "tests.triage"),
    # Two matches: the body's text forges one. The read is not trusted.
    ("body='a, criterion_id='c1', b', criterion_id='c2', id='tst2'", "tests.encode"),
])
def test_an_answer_stays_a_judgement_unless_an_encode_of_the_refs_was_refused(
        db, summary, fn):
    """The review of 4de1555 (2026-10-05): a refused encode of another
    criterion's test made the answer on tst1 read as no judgement."""
    _judged(db)                                        # m96 woke s1, answered by m98
    _encode_row(db, "s1", summary, fn)
    with pytest.raises(ValueError, match=r"already \(m96\) and they answered \(m98\)"):
        _developer(db).call("msg.challenge_tester", refs=["c1", "tst1"], quotes=QUOTES)


@pytest.mark.parametrize("refs", [["c1"], ["tst1"]])
def test_a_refused_encode_matches_a_criterion_named_directly_or_through_a_test(
        db, refs):
    from rota.core.sandbox import _same_refs_refusal
    _msg(db, "m96", "developer", "tester", "challenge", refs, 1, "answered")
    _session(db, "s1", "tester", 1, trigger="m96")
    _msg(db, "m98", "tester", "developer", "answer", refs, 2, "answered", cause="m96")
    _encode_row(db, "s1", "criterion_id='c1', id='tst1'")
    assert _same_refs_refusal(_developer(db).ctx, "tester", "challenge", refs) is None


def test_an_encode_in_a_session_of_another_role_is_not_the_testers(db):
    _judged(db)
    _session(db, "s2", "architect", 2, trigger="m96")
    _encode_row(db, "s2", "criterion_id='c1', id='tst1'")
    with pytest.raises(ValueError, match=r"already \(m96\) and they answered \(m98\)"):
        _developer(db).call("msg.challenge_tester", refs=["c1", "tst1"], quotes=QUOTES)


@pytest.mark.parametrize("receipt", [("s1", "criteria", "c9"), ("s2", "tests", "tst9")])
def test_only_a_tests_receipt_of_the_tester_lands_a_change(db, receipt):
    """s1's encode of c1 was refused, so the answer is no judgement. A
    criteria receipt of s1, or a tests receipt of another role's session
    that m96 woke, does not land the Tester's change."""
    _judged(db)
    _encode_row(db, "s1", "criterion_id='c1', id='tst1'")
    _session(db, "s2", "architect", 2, trigger="m96")
    db.execute("INSERT INTO receipts (session_id, table_name, row_id, new_version) "
               "VALUES (?, ?, ?, 1)", receipt)
    out = _developer(db).call("msg.challenge_tester", reason=REASON, refs=["c1", "tst1"], quotes=QUOTES)
    assert out == {"id": "m99", "to": "tester", "verb": "challenge"}


def test_the_bound_says_none_landed_when_one_of_two_priors_answered(db):
    """m1's Tester did nothing. m3's Tester had its encode refused, and it
    answered. "Answered neither" is false, so the new form stands."""
    _msg(db, "m1", "developer", "tester", "challenge", ["c1", "tst1"], 1,
         "unresolved", note=NOTE)
    _session(db, "s1", "tester", 1, trigger="m1")
    _msg(db, "m3", "developer", "tester", "challenge", ["c1", "tst1"], 3, "answered")
    _session(db, "s2", "tester", 2, trigger="m3")
    _encode_row(db, "s2", "criterion_id='c1', id='tst1'")
    _msg(db, "m4", "tester", "developer", "answer", ["c1", "tst1"], 4,
         "answered", cause="m3")
    with pytest.raises(ValueError) as exc:
        _developer(db).call("msg.challenge_tester", refs=["c1", "tst1"], quotes=QUOTES)
    assert str(exc.value) == (
        "you sent challenge to tester on exactly these refs already (m1, then "
        "m3), and the test did not change. The Tester sent changes to the "
        "test, and none landed. Send msg.escalate_architect on the same refs.")


def test_the_cap_counts_only_the_developers_challenges_to_the_tester(db):
    for i, (frm, to, verb) in enumerate(
            [("critic", "tester", "challenge")] * 3
            + [("developer", "architect", "challenge")] * 3
            + [("developer", "tester", "question")] * 3, start=1):
        _msg(db, f"x{i}", frm, to, verb, ["c1", "tst1"], i, "answered")
    out = _developer(db).call("msg.challenge_tester", reason=REASON, refs=["c1", "tst1"], quotes=QUOTES)
    assert out["to"] == "tester"


def _rows_on(db, refs, ids, seq=50):
    for n, mid in enumerate(ids):
        _msg(db, mid, "developer", "tester", "challenge", refs, seq + n, "answered")


def test_the_cap_names_the_first_criterion_at_the_cap(db):
    """c1 holds 3 and c2 holds 4. The refs name c1 first, so the sentence
    counts c1."""
    from rota.core.sandbox import _same_refs_refusal
    _chain(db, ("tst1", "tst2"))
    _rows_on(db, ["c2", "tst2"], ["y1", "y2", "y3", "y4"])
    said = _same_refs_refusal(_developer(db).ctx, "tester", "challenge",
                              ["c1", "tst1", "c2", "tst2"])
    assert said.startswith(
        "you sent challenge to tester on c1 or a test of c1 3 times already "
        "(m1, m2, m3)")


def test_refs_that_name_no_criterion_or_test_keep_the_count_of_the_same_refs(db):
    """The newest prior is unanswered and the one before it judged, so the
    door would admit, and the cap counts the three priors on ['g1']."""
    from rota.core.sandbox import _same_refs_refusal
    _msg(db, "x1", "developer", "tester", "challenge", ["g1"], 1, "answered")
    _msg(db, "x2", "developer", "tester", "challenge", ["g1"], 2, "answered")
    _session(db, "s2", "tester", 2, trigger="x2")
    _msg(db, "x3", "tester", "developer", "answer", ["g1"], 3, "answered", cause="x2")
    _msg(db, "x4", "developer", "tester", "challenge", ["g1"], 4, "unresolved", note=NOTE)
    _session(db, "s4", "tester", 4, trigger="x4")
    said = _same_refs_refusal(_developer(db).ctx, "tester", "challenge", ["g1"])
    assert said.startswith(
        "you sent challenge to tester on exactly these refs 3 times already "
        "(x1, x2, x4).")


def test_refs_that_name_a_criterion_and_no_test_count_for_the_criterion(db):
    from rota.core.sandbox import _same_refs_refusal
    _rows_on(db, ["c1"], ["x1"], seq=1)
    _rows_on(db, ["c1", "g1"], ["x2"], seq=2)
    _rows_on(db, ["c1", "tk1"], ["x3"], seq=3)
    said = _same_refs_refusal(_developer(db).ctx, "tester", "challenge", ["c1", "b1"])
    assert said == (
        "you sent challenge to tester on c1 or a test of c1 3 times already "
        "(x1, x2, x3). Send msg.escalate_architect on the same refs.")


def test_a_test_with_no_criterion_counts_for_itself(db):
    from rota.core.sandbox import _same_refs_refusal
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('tst0', 'b1', NULL, 'test_zero.py', 'assert 0 == 1')")
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result) "
               "VALUES ('r0', 'b1', 'tst0', 'abc123', 'fail')")
    for i, extra in enumerate(([], ["g1"], ["tk1"]), start=1):
        _rows_on(db, ["tst0"] + extra, [f"x{i}"], seq=i)
        _session(db, f"s{i}", "tester", i, trigger=f"x{i}",
                 receipts=[("tests", "tst0", i + 1)])
    said = _same_refs_refusal(_developer(db).ctx, "tester", "challenge", ["tst0", "b1"])
    assert said == (
        "you sent challenge to tester with tst0 in the refs 3 times already "
        "(x1, x2, x3), and the test changed and is still red. Send "
        "msg.escalate_architect on the same refs.")


def test_the_cap_reads_red_on_the_counted_criterions_test_only(db):
    """tst1 passes and tst2 fails. The sentence is about c1, so it does not
    say that the test is still red."""
    from rota.core.sandbox import _same_refs_refusal
    _chain(db, ("tst1", "tst2"))
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result) "
               "VALUES ('r99', 'b1', 'tst1', 'abc123', 'pass')")
    said = _same_refs_refusal(_developer(db).ctx, "tester", "challenge",
                              ["c1", "tst1", "tst2"])
    assert said == (
        "you sent challenge to tester on c1 or a test of c1 3 times already "
        "(m1, m2, m3). Send msg.escalate_architect on the same refs.")


def test_the_criterion_form_needs_a_red_test(db):
    _chain(db, ("tst1",), tester="moves the criterion")
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result) "
               "VALUES ('r99', 'b1', 'tst1', 'abc123', 'pass')")
    with pytest.raises(ValueError) as exc:
        _developer(db).call("msg.challenge_tester", reason=REASON, refs=["c1", "tst1"], quotes=QUOTES)
    assert str(exc.value) == (
        "you sent challenge to tester on exactly these refs 3 times already "
        "(m1, m2, m3). Send msg.escalate_architect on the same refs.")


def test_the_test_form_comes_before_the_criterion_form(db):
    _chain(db, ("tst1",))
    _session(db, "sc", "terminologist", 9000, receipts=[("criteria", "c1", 9)])
    with pytest.raises(ValueError, match=r"and the test changed and is still red\."):
        _developer(db).call("msg.challenge_tester", reason=REASON, refs=["c1", "tst1"], quotes=QUOTES)


def test_the_criterion_form_reads_only_the_criterion_of_this_call(db):
    """The review of 4de1555 (2026-10-05): three challenges on [c2, tst1],
    each followed by a criteria receipt on c2. The call on [c1, tst1] met
    "the criterion changed", and c1 never changed."""
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c2','tk1','closing an account keeps its owner')")
    for i in (1, 2, 3):
        _msg(db, f"m{i}", "developer", "tester", "challenge", ["c2", "tst1"],
             10 * i, "answered")
        _session(db, f"s{i}", "tester", 10 * i, trigger=f"m{i}")
        _session(db, f"t{i}", "terminologist", 10 * i + 1,
                 receipts=[("criteria", "c2", i)])
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result) "
               "VALUES ('r1', 'b1', 'tst1', 'abc123', 'fail')")
    with pytest.raises(ValueError) as exc:
        _developer(db).call("msg.challenge_tester", refs=["c1", "tst1"], quotes=QUOTES)
    assert str(exc.value) == (
        "you sent challenge to tester on c1 or a test of c1 3 times already "
        "(m1, m2, m3). Send msg.escalate_architect on the same refs.")
    # c2 in the call's refs is not the counted criterion, so its receipts
    # still do not make "the criterion changed".
    from rota.core.sandbox import _same_refs_refusal
    said = _same_refs_refusal(_developer(db).ctx, "tester", "challenge",
                              ["c1", "tst1", "c2"])
    assert said == (
        "you sent challenge to tester on c1 or a test of c1 3 times already "
        "(m1, m2, m3). Send msg.escalate_architect on the same refs.")


def test_the_cap_reads_the_test_of_the_call_before_the_criterions_others(db):
    """tst1 moved and is red. tst1b, the other test of c1, passes, and the
    call names tst1b. The sentence is about tst1b."""
    from rota.core.sandbox import _same_refs_refusal
    _chain(db, ("tst1",))
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('tst1b', 'b1', 'c1', 'test_close_b.py', 'assert 2 == 2')")
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result) "
               "VALUES ('r99', 'b1', 'tst1b', 'abc123', 'pass')")
    said = _same_refs_refusal(_developer(db).ctx, "tester", "challenge", ["c1", "tst1b"])
    assert said == (
        "you sent challenge to tester on c1 or a test of c1 3 times already "
        "(m1, m2, m3). Send msg.escalate_architect on the same refs.")


def test_an_answer_with_null_refs_added_no_row(db):
    """The diff review of 538b84a (2026-10-02): `null` as body_refs made
    json.loads return None, and enumerate(None) raised."""
    sb = _answered_escalation(db, "null")
    with pytest.raises(ValueError, match=r"\(m2\) with no row beyond your own refs"):
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
        sb.call("msg.answer_developer", refs=["c1", "tst1"],
                quotes="leaves its invoices in place")


def test_a_moved_red_resets_the_failing_ticks_attempts(db):
    """Walk seventeen: four, three, two tests failing across three commits
    and the third session was the quarantine -- progress counted as
    dispatch without progress. Frame 318: the progress is the red moving
    at the new head, not the head commit alone (night 162)."""
    from rota.core.db import _lift_quarantines, lift_on_red_move, red_before
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
               "result, attempt, output) VALUES ('r1','b1','tst1','abc123',"
               "'fail',1,'E  AssertionError: no invoices')")
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined) "
               "VALUES ('developer|tick:tests_failing|b1', 2, 0)")
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined) "
               "VALUES ('tester|tick:tests_missing|b1', 2, 0)")
    db.commit()

    from rota.core.db import Write
    W = Write(table="batches", row_id="b1", values={"head_commit": "def456"})

    _lift_quarantines(db, W, moved=True)
    rows = {r["tick_key"]: r["attempts"] for r in db.execute(
        "SELECT tick_key, attempts FROM tick_attempts")}
    assert rows["developer|tick:tests_failing|b1"] == 2, "the red has not run yet"
    before = red_before(db, "b1")
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
               "result, attempt, output) VALUES ('r2','b1','tst1','def456',"
               "'pass',2,'')")
    assert lift_on_red_move(db, "b1", "def456", before)
    rows = {r["tick_key"]: r["attempts"] for r in db.execute(
        "SELECT tick_key, attempts FROM tick_attempts")}
    assert "developer|tick:tests_failing|b1" not in rows, "progress resets"
    assert rows["tester|tick:tests_missing|b1"] == 2, "an unrelated debt keeps its count"


def test_a_head_commit_still_revives_the_batchs_keys(db):
    """Night 91's fix revives a quarantine on a move of its subject only. A
    new head commit is progress and stays a move, though `code.commit`
    writes it with `amends` False (frame 80)."""
    from rota.core.db import SessionResult, Write, session_commit
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, "
               "reported) VALUES ('critic|tick:review|b1', 3, 1, 1)")
    db.commit()
    session_commit(db, SessionResult(
        session_id="s_code", role="developer",
        writes=[Write("batches", "b1", {"head_commit": "def456"},
                      amends=False)]))
    assert not db.execute("SELECT 1 FROM tick_attempts WHERE tick_key = "
                          "'critic|tick:review|b1'").fetchone(), "progress revives"


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
                                values={"body": "def test_x():\n    assert 1"}),
                      moved=True)
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
    sb.call("msg.challenge_tester", reason=REASON, refs=["c2", "tst2"],
            quotes=["closing an account leaves its invoices in place",
                    "assert tombstone('a') == 'gone'"])
    assert sb.ctx.outbound[-1]["to_role"] == "tester"
    # A paraphrase of any criterion is still refused.
    sb2 = build("developer", db, batch_id="b1", mode="tests_failing",
                allow=prompts.mode_tools("developer", "tests_failing"))
    with pytest.raises(ValueError, match="Quote, not paraphrase"):
        sb2.call("msg.challenge_tester", reason=REASON, refs=["c2", "tst2"],
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
             assumption="the test assumes closing as a sample", kind="invented")
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


def test_a_respecified_criterion_moves_its_version(db):
    """Night 91's fix revives a quarantine only when its subject moves. A
    respecify wrote with `amends` False, so a repaired criterion moved
    nothing and the Tester that gave up on it never woke (frame 80)."""
    from rota.core.db import SessionResult, session_commit
    from rota.core.runner import _as_write
    from rota.roles import prompts
    sb = build("terminologist", db, mode="criterion_repair",
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    sb.call("criteria.respecify", id="c1",
            text="closing an account keeps every invoice it issued",
            surface_refs=["close_account"])
    writes = [_as_write(w) for w in sb.ctx.writes]
    (crit,) = [w for w in writes if w.table == "criteria"]
    assert crit.amends, "a respecify is an amendment"
    session_commit(db, SessionResult(session_id="s_re", role="terminologist",
                                     writes=writes))
    row = db.execute("SELECT version FROM criteria WHERE id = 'c1'").fetchone()
    assert row["version"] == 2, "the criterion's version moves"


def _keeper(db, mode, onboarding=False):
    from rota.roles import prompts
    return build("vision_keeper", db, mode=mode, onboarding=onboarding,
                 allow=prompts.mode_tools("vision_keeper", mode))


def _delivered(db, sb, refs=()):
    """Wake `sb` on a Liaison deliver that the principal's message caused.

    Frame 303: a new request item needs the principal's words as its cause,
    and a sandbox with no trigger has none.
    """
    if not db.execute("SELECT 1 FROM messages WHERE id = 'm_deliver'").fetchone():
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                   "verb, seq) VALUES ('m_said', 't_d', 'principal', "
                   "'liaison', 'converse', 900)")
        db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
                   "to_role, verb, body_refs, seq) VALUES ('m_deliver', "
                   "'m_said', 't_d', 'liaison', 'vision_keeper', 'deliver', ?, "
                   "901)", (json.dumps(list(refs)),))
        db.commit()
    sb.ctx.trigger = "m_deliver"
    sb.ctx.wake_kind = "message"
    return sb


def _land(db, sb, session_id):
    """Land a sandbox's staged writes the way the runner does."""
    from rota.core.db import SessionResult, session_commit
    from rota.core.runner import _as_write
    session_commit(db, SessionResult(
        session_id=session_id, role=sb.ctx.role,
        writes=[_as_write(w) for w in sb.ctx.writes]))


def test_a_described_item_returns_to_the_owner_as_a_draft(db):
    """clickI night 91 (2026-09-24): the summary of Click was cut into a
    ticket that asked for nothing. The keeper describes it instead. The
    version stays, so no batch is cancelled or reopened (frame 80)."""
    from rota.core.predicates import cancel, reopen
    from rota.core.scheduler import tick_signoff
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('bg_1_summary','Click is a toolkit',"
               "'in_scope','approved',1,1)")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES "
               "('b9','bg_1_summary','merged')")
    db.commit()
    sb = _keeper(db, "slicing")
    sb.call("problem.describe", id="bg_1_summary")
    (w,) = [w for w in sb.ctx.writes if w[0] == "items"]
    assert w[2] == {"is_description": 1, "approval": "draft"} and w[3] is False
    _land(db, sb, "s_desc")
    row = db.execute("SELECT version, approval, is_description FROM items "
                     "WHERE id = 'bg_1_summary'").fetchone()
    assert tuple(row) == (1, "draft", 1), "the version stays"
    assert any("bg_1_summary" in w.refs for w in tick_signoff(db)), \
        "the owner sees the word"
    assert cancel(db) == [] and reopen(db) == [], "nothing built is disturbed"


def test_the_describe_door_keeps_the_owners_words_and_live_work(db):
    """Night 91's challenges named the one real request, not the summary. A
    describe with no door could take real work off the path (frame 80)."""
    sb = _keeper(db, "challenge")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('echo_json','echo prints json','in_scope',"
               "'approved',1,1)")
    seed_provenance(db, "items", "echo_json", "decided")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('bg_1_summary','Click is a toolkit',"
               "'in_scope','approved',1,1)")
    db.commit()
    with pytest.raises(ValueError, match="principal's own words"):
        sb.call("problem.describe", id="echo_json")
    with pytest.raises(ValueError, match="has work in batch b1"):
        sb.call("problem.describe", id="i1")
    assert sb.call("problem.describe", id="bg_1_summary")["described"]


def test_an_item_read_from_the_code_is_a_description_by_construction(db):
    """An onboarding item and the account say what the software is. Any
    other assert stages no flag, so an amendment keeps it (frame 80)."""
    def staged(sb, id):
        return [w[2] for w in sb.ctx.writes if w[0] == "items" and w[1] == id][-1]

    sb = _keeper(db, "orient", onboarding=True)
    sb.call("problem.assert", id="parses_options",
            text="the program reads flags from the command line")
    assert staged(sb, "parses_options")["is_description"] == 1

    sb = _delivered(db, _keeper(db, "deliver"))
    sb.call("problem.assert", id="export_csv",
            text="the program exports the recipes as a csv file")
    assert "is_description" not in staged(sb, "export_csv")
    sb.call("problem.assert", id="how_it_works",
            text="a billing tool that closes accounts and keeps invoices")
    assert staged(sb, "how_it_works")["is_description"] == 1


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


def test_words_about_a_statement_go_as_a_clarify_that_names_it(db):
    """G1-what-the-brief-already-holds: the Liaison claimed chat, answered
    from the brief word for word, and ref'd the entry. The chat claim is
    gone, so the words land on their row as one clarify (ruled: Roman,
    2026-10-08, the park ask is a page with rows, point 4)."""
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
    with pytest.raises(ArgumentError, match="always land on a row"):
        sb.call("brief.intake", verdict="chat")
    sb.call("msg.clarify_principal", refs=["s1"],
            question="We decided that invoices are kept for seven years after the "
                     "account is closed. Is that still right?")
    assert sb.ctx.outbound[-1]["body_refs"] == ["s1"]


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
    owed a ledger row. Frame 204: the door stages the row itself, kind
    `invented`, and admits the encode, so the seat spends no turn on a
    dictated `ledger.log` (design, section 7)."""
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    assert _encode(sb, "from script import prompt_text\n"
                       "def test_greet():\n"
                       "    assert prompt_text() == 'Enter your name: '")
    (row,) = [w for w in sb.ctx.writes if w[0] == "ledger"]
    assert row[2]["kind"] == "invented" and row[2]["author"] == "tester"
    assert row[2]["about_ref"] == "c1"
    assert row[2]["default_taken"] == (
        "the test assumes Enter your name:  where the material is silent")
    # The row is staged with the test, and a second encode owes nothing.
    assert [w[0] for w in sb.ctx.writes] == ["ledger", "tests"]
    sb.ctx.writes.clear()
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, kind, "
               "author) VALUES ('l_x', 'c1', 'criteria', ?, 'invented', 'tester')",
               (row[2]["default_taken"],))
    db.commit()
    assert _encode(sb, "from script import prompt_text\n"
                       "def test_greet():\n"
                       "    assert prompt_text() == 'Enter your name: '")
    assert [w[0] for w in sb.ctx.writes] == ["tests"]


def test_the_returns_door_offers_a_default(db, tmp_path):
    """Frame 204: a test that asserts on a return chose a behaviour, so the
    returns door names `default` (design, section 2)."""
    root = tmp_path / "wt"; root.mkdir()
    (root / "script.py").write_text("import json" + chr(10) + "def echo_json(obj):" + chr(10)
                                    + "    print(json.dumps(obj))" + chr(10), encoding="utf-8")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE criteria SET surface_refs = '[\"echo_json\"]' WHERE id = 'c1'")
    db.execute("INSERT OR IGNORE INTO entries (id, author, ts_order, text) VALUES "
               "('e9', 'principal', 9, 'echo_json prints the object')")
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    body = ("from script import echo_json" + chr(10) + "def test_x():" + chr(10)
            + "    result = echo_json({'a': 1})" + chr(10) + "    assert result" + chr(10))
    with pytest.raises(ValueError, match="kind='default'"):
        sb.call("tests.encode", id="tst_r", criterion_id="c1", path="tests/test_r.py", body=body)
    assert sb.ctx.offers[0].args["kind"] == "default"


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
    _delivered(db, sb, ("s1",))
    sb.call("problem.assert", id="i9", text="closing an account keeps its "
            "invoices for seven years", kind="in_scope")
    pairs = [w for w in sb.ctx.writes if w[0] == "refs"]
    assert pairs and pairs[0][1] == "items:i9:statement:s1"
    assert pairs[0][2] == {"src_table": "items", "src_id": "i9", "kind": "statement",
                           "target": "s1", "resolves": 1}
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
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('how_it_works', ?, 'in_scope', 'approved', 1, 1)",
               ("The program is a tip calculator: it takes a total and a percentage "
                "and prints the tip and the total with tip.",))
    db.commit()
    sb = _delivered(db, build("vision_keeper", db, mode="normal",
                              allow=prompts.mode_tools("vision_keeper", "deliver")))
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
    # A span replaces the lines code.source showed, and the file keeps the
    # rest (clickI night 16, 2026-09-12: a long module does not fit one reply).
    sb.call("code.write", path="script.py", text="def close_account(a):\n    return 2\n",
            start=0, end=2)
    assert (root / "script.py").read_text(encoding="utf-8") == "def close_account(a):\n    return 2\n"
    sb.call("code.write", path="script.py", text="def opened(a):\n    return 3\n", start=2, end=-1)
    body = (root / "script.py").read_text(encoding="utf-8")
    assert "def opened" in body and "def close_account" in body
    with pytest.raises(ValueError, match="does not exist"):
        sb.call("code.write", path="other.py", text="x = 1\n", start=3, end=4)


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

    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i2','show the python version','in_scope','approved',1,1)")
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
    db.execute("INSERT INTO constraints (id, headline) VALUES "
               "('k1','calculate_tip is called by main')")
    seed_provenance(db, "constraints", "k1", "observed")
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


def test_an_escalation_reads_a_worktree_that_lives_under_dot_rota(db, tmp_path):
    """Found by reading (2026-09-16): the door excluded '.rota' on absolute
    parts, and a batch worktree is <project>/.rota/worktrees/<batch>, so every
    file was excluded and every escalation over an identifier grain was refused
    as undefined, whatever the code held."""
    root = tmp_path / ".rota" / "worktrees" / "b1"; root.mkdir(parents=True)
    (root / "main.py").write_text("def calculate_tip(t, p):" + chr(10) + "    return t * p" + chr(10), encoding="utf-8")
    db.execute("UPDATE batches SET worktree = ?, head_commit = 'abc' WHERE id = 'b1'", (str(root),))
    db.execute("INSERT INTO constraints (id, headline) VALUES ('k1','calculate_tip is called by main')")
    seed_provenance(db, "constraints", "k1", "observed")
    db.execute("INSERT INTO findings (id, batch_id, constraint_id, commit_sha, status, grain) "
               "VALUES ('f1','b1','k1','abc','violated','calculate_tip')")
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="normal",
               allow=prompts.mode_tools("developer", "finding_violated"))
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
    db.execute("INSERT INTO constraints (id, headline) VALUES "
               "('k1','display_results is called by main')")
    seed_provenance(db, "constraints", "k1", "observed")
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
    (root / "src" / "click" / "main.py").write_text("def main():" + chr(10) + "    pass" + chr(10), encoding="utf-8")
    db.execute("UPDATE criteria SET surface_refs = '[\"echo_json\"]' WHERE id = 'c1'")
    db.commit()
    with pytest.raises(ValueError, match="src/click/echo_json.py"):
        sb.call("code.write", path="echo_json.py", text="def echo_json(o):\n    return o\n")
    with pytest.raises(ValueError, match="src/click/echo_json.py"):
        sb.call("code.write", path="main.py", text="def echo_json(o):" + chr(10) + "    return o" + chr(10))
    assert sb.call("code.write", path="src/click/echo_json.py",
                   text="def echo_json(o):\n    return o\n")["bytes"]


def test_observed_items_and_the_account_are_never_sliced(db):
    """clickI night 9 (2026-09-11): tickets for three observed items and for
    the account, sixteen criteria for the account, one batch of five tickets
    of which one was asked for."""
    from rota.roles import prompts

    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('seen','click parses arguments','in_scope','approved',1,1)")
    seed_provenance(db, "items", "seen", "observed")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('how_it_works','a cli library','in_scope','approved',1,1)")
    seed_provenance(db, "items", "how_it_works", "observed")
    db.commit()
    sb = build("vision_keeper", db, mode="normal",
               allow=prompts.mode_tools("vision_keeper", "slicing"))
    with pytest.raises(ValueError, match="is observed"):
        sb.call("tickets.slice", id="tk_x", item_id="seen", text="parse arguments")
    with pytest.raises(ValueError, match="never sliced"):
        sb.call("tickets.slice", id="tk_y", item_id="how_it_works", text="the whole")
    assert sb.call("tickets.slice", id="tk_z", item_id="i1", text="close an account")["id"]


def _summary_item(db, described=0):
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version, is_description) VALUES ('bg_1_summary',"
               "'the software is a toolkit called Click','in_scope','approved',"
               "1,1,?)", (described,))
    db.commit()


def _tickets_staged(sb):
    return [w[1] for w in sb.ctx.writes if w[0] == "tickets"]


def test_a_slice_after_a_describe_stages_no_ticket(db):
    """L1-VK-slice-a-description (2026-09-24): the seat described the item
    and then sliced it on the next turn. A description has no tickets, so
    the slice answers and writes nothing (frame 80)."""
    _summary_item(db)
    sb = _keeper(db, "slicing")
    sb.call("problem.describe", id="bg_1_summary")
    out = sb.call("tickets.slice", id="tk_1", item_id="bg_1_summary",
                  text="the software is a toolkit called Click")
    assert out["unchanged"] and "is a description" in out["note"], out
    assert _tickets_staged(sb) == []


def test_a_describe_after_a_slice_leaves_no_ticket_staged(db):
    """L1-VK-slice-a-description: the seat sent a slice and a describe for
    one item in one reply. The describe takes the slice back (frame 80)."""
    _summary_item(db)
    sb = _keeper(db, "slicing")
    sb.call("tickets.slice", id="tk_1", item_id="bg_1_summary",
            text="the software is a toolkit called Click")
    out = sb.call("problem.describe", id="bg_1_summary")
    assert "tk_1" in out["note"], out
    assert _tickets_staged(sb) == []


def test_a_slice_on_an_item_described_on_file_answers_with_the_note(db):
    """A description on file has no tickets, from any mode that can slice.
    The answer names the reason and ends the session (frame 80)."""
    _summary_item(db, described=1)
    sb = _keeper(db, "slicing")
    out = sb.call("tickets.slice", id="tk_1", item_id="bg_1_summary",
                  text="the software is a toolkit called Click")
    assert out["unchanged"] and "has no tickets" in out["note"], out
    assert _tickets_staged(sb) == []


def test_an_invented_bare_surface_is_refused(db):
    """clickI night 9: range_argument and get_usage as surfaces."""
    from rota.roles import prompts

    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i9', 'The share lives in a new function named split_bill.', "
               "'in_scope', 'approved', 1, 1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk9','i9','split the bill')")
    db.commit()
    sb = build("terminologist", db, mode="normal",
               allow=prompts.mode_tools("terminologist", "criteria"))
    with pytest.raises(ValueError, match="range_argument is a name the index does not hold"):
        sb.call("criteria.specify", id="c_9", ticket_id="tk9", text="each share is equal",
                surface_refs=["range_argument"])
    assert sb.call("criteria.specify", id="c_9", ticket_id="tk9", text="each share is equal",
                   surface_refs=["split_bill"])["id"] == "c_9"


def test_a_long_source_read_maps_its_definitions(db, tmp_path):
    """clickI night 11 (2026-09-11): the Developer paged a long file four
    hundred lines at a time and never found the function."""
    root = tmp_path / "wt"; root.mkdir()
    body = "\n".join(["import os", ""] + [f"def f{i}():\n    return {i}\n" for i in range(300)]
                     + ["def confirm(text, default=False):\n    return default\n"])
    (root / "termui.py").write_text(body, encoding="utf-8")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    out = sb.call("code.source", path="termui.py", start=0, end=400)
    assert out["lines"] > 400 and "confirm" in out["defs"]
    start, end = out["defs"]["confirm"]
    assert "def confirm" in sb.call("code.source", path="termui.py", start=start, end=end)["text"]


def test_the_account_s_observed_items_are_not_re_asserted_into_a_build(db):
    """clickI night 18 (2026-09-12): delivering the principal's sentence, the
    Vision Keeper asserted its item and then the three onboarding items
    again, word for word. A decided wake writes decided, so the account
    became buildable, 119 criteria, a batch ahead of the sentence's. The
    same words on an observed row are refused; the principal's words land."""
    from rota.roles import prompts

    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('parses_commands', ?, 'in_scope', 'approved', 1, 1)",
               ("When a user types a command, the toolkit parses it into arguments and "
                "options using the script's defined commands.",))
    seed_provenance(db, "items", "parses_commands", "observed")
    db.commit()
    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
               "('e1','principal',1,'Commands accept a --json flag that prints the parsed arguments as JSON.')")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, status) "
               "VALUES ('s1','e1',0,10,'Commands accept a --json flag that prints the parsed "
               "arguments as JSON.','ratified')")
    db.commit()
    from types import SimpleNamespace
    sb = build("vision_keeper", db, mode="normal",
               allow=prompts.mode_tools("vision_keeper", "deliver"),
               wake=SimpleNamespace(refs=("s1",), kind="message", message_id=None))
    _delivered(db, sb, ("s1",))
    with pytest.raises(ValueError, match="observed row"):
        sb.call("problem.assert", id="parses_commands",
                text="When a user types a command, the toolkit parses it into arguments "
                     "and options using the script's defined commands.")
    # Night 19: the same item paraphrased past the words door. Not the
    # principal's words either: the statement on the wake says something else.
    with pytest.raises(ValueError, match="not the principal's words"):
        sb.call("problem.assert", id="parses_commands",
                text="When a user runs a command, the toolkit turns it into structured "
                     "data, options and arguments, from the commands the script defines.")
    # The principal's words change it: a different behaviour under the same name lands.
    sb.call("problem.assert", id="parses_commands",
            text="Commands accept a --json flag that prints the parsed arguments as JSON.")
    sb.call("problem.assert", id="echo_json",
            text="Add an echo_json helper next to echo that prints an object as JSON.")


def test_nearly_the_same_words_are_the_same_criterion(db):
    """clickI night 18 (2026-09-12): 63 criteria for one flag, 55 in one
    reply, "the usage string must include --show-python" beside "the usage
    string must explicitly list --show-python". Word overlap is a fact."""
    from rota.roles import prompts

    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i9', 'version_option takes a show_python flag.', "
               "'in_scope', 'approved', 1, 1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk9','i9','the flag')")
    db.commit()
    sb = build("terminologist", db, mode="normal",
               allow=prompts.mode_tools("terminologist", "criteria"))
    sb.call("criteria.specify", id="c_1", ticket_id="tk9",
            text="The usage string must include the --show-python flag as an available option",
            surface_refs=["show_python"])
    with pytest.raises(ValueError, match="nearly the same words"):
        sb.call("criteria.specify", id="c_2", ticket_id="tk9",
                text="The usage string must always include the --show-python flag as an available option",
                surface_refs=["show_python"])
    # Two sentences that share a subject and differ in what they claim are
    # two criteria (the door is near-verbatim only, 0.85).
    sb.call("criteria.specify", id="c_2b", ticket_id="tk9",
            text="The usage string must explicitly list the --show-python flag under options",
            surface_refs=["show_python"])
    sb.call("criteria.specify", id="c_3", ticket_id="tk9",
            text="With the flag set, the message ends with the running Python version as major.minor.micro",
            surface_refs=["show_python"])


def test_the_architect_groups_the_tickets_its_wake_named(db):
    """tipsAV (2026-09-12): woken for the amended item's new ticket, the
    Architect grouped two tickets already in a pending batch, four turns
    running. The wake names the unbatched tickets; that is the set."""
    from types import SimpleNamespace
    from rota.roles import prompts

    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i2', 'print each share', 'in_scope', 'approved', 1, 1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk2','i2','print the shares')")
    db.commit()
    sb = build("architect", db, mode="grouping",
               allow=prompts.mode_tools("architect", "grouping"),
               wake=SimpleNamespace(refs=("tk2",), kind="tick:grouping", message_id=None))
    with pytest.raises(ValueError, match="not among the tickets you were woken to group"):
        sb.call("batches.group", id="b9", ticket_ids=["tk1"], item_id="i1")
    assert sb.call("batches.group", id="b9", ticket_ids=["tk2"], item_id="i2")["id"] == "b9"


def test_a_criterions_words_are_not_an_item(db):
    """tipsAX (2026-09-12): answering the Terminologist's challenge, the
    Vision Keeper asserted the challenged criterion's sentence as a new item
    under the criterion's own id, and the run built it as scope."""
    from rota.roles import prompts

    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i9', 'split the bill between the payers', 'in_scope', "
               "'approved', 1, 1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk9','i9','split it')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c_9', 'tk9', "
               "'The function divides the sum of the bill and the tip by the number of payers.')")
    db.commit()
    sb = _delivered(db, build("vision_keeper", db, mode="normal",
                              allow=prompts.mode_tools("vision_keeper", "challenge")))
    with pytest.raises(ValueError, match="a criterion of an item that exists"):
        sb.call("problem.assert", id="c_9_item",
                text="The function divides the sum of the bill and the tip by the number of payers.")
    sb.call("problem.assert", id="tip_rounding", text="The tip is rounded to the nearest cent.")


def test_a_bare_surface_is_found_in_a_worktree_under_dot_rota(db, tmp_path):
    """clickI night 22 (2026-09-12): echo_json defined in src/click/echo_json.py,
    and the commit refused for a tree that did not define it. The worktree
    lives under .rota/worktrees, and the scan dropped every file in it."""
    import subprocess

    root = tmp_path / ".rota" / "worktrees" / "b1"; root.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "script.py").write_text("def other():" + chr(10) + "    return 1" + chr(10), encoding="utf-8")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE criteria SET surface_refs = '[\"close_account\"]' WHERE id = 'c1'")
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    with pytest.raises(ValueError, match="does not define close_account"):
        sb.call("code.commit", message="half done")
    sb.call("code.write", path="helpers.py",
            text="def close_account(a):" + chr(10) + "    return 'x'" + chr(10))
    out = sb.call("code.commit", message="the surface exists, in a new file under .rota")
    assert out.get("committed") is not False


def test_a_src_layout_surface_is_imported_by_its_dotted_module(db, tmp_path):
    """clickI night 23 (2026-09-12): the surface lived in src/click/core.py,
    the test imported `from click.core import ...`, and the door compared
    the stem `core` with the first segment `click`, refused twelve turns
    running, and told the Tester `from core import`, which cannot import."""
    root = tmp_path / "wt"; (root / "src" / "pkg").mkdir(parents=True)
    (root / "src" / "pkg" / "core.py").write_text(
        "def calculate_tip(t, p):" + chr(10) + "    return t * p / 100" + chr(10), encoding="utf-8")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE criteria SET surface_refs = '[\"src/pkg/core.py::calculate_tip\"]' WHERE id = 'c1'")
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    with pytest.raises(ValueError, match="from pkg.core import calculate_tip"):
        sb.call("tests.encode", id="tst_a", criterion_id="c1", path="tests/test_a.py",
                body="from core import calculate_tip" + chr(10) + "def test_a():" + chr(10)
                     + "    assert calculate_tip(100, 10) == 10" + chr(10))
    got = sb.call("tests.encode", id="tst_b", criterion_id="c1", path="tests/test_b.py",
                  body="from pkg.core import calculate_tip" + chr(10) + "def test_b():" + chr(10)
                       + "    assert calculate_tip(100, 10) == 10" + chr(10))
    assert got, "the dotted import lands"


def test_a_test_imports_only_modules_the_tree_has(db, tmp_path):
    """clickI night 24 (2026-09-12): three tests began `from echo import
    echo_json`; no module named echo exists, every one died at collection,
    and the Developer spent its fix sessions challenging the wrong test."""
    root = tmp_path / "wt"; root.mkdir()
    (root / "main.py").write_text("def calculate_tip(t, p):" + chr(10) + "    return t * p / 100" + chr(10), encoding="utf-8")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE criteria SET surface_refs = '[\"main.py::calculate_tip\"]' WHERE id = 'c1'")
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    with pytest.raises(ValueError, match="imports echo, and no module of that name exists"):
        sb.call("tests.encode", id="tst_a", criterion_id="c1", path="tests/test_a.py",
                body="from echo import calculate_tip" + chr(10) + "def test_a():" + chr(10)
                     + "    assert calculate_tip(100, 10) == 10" + chr(10))
    got = sb.call("tests.encode", id="tst_b", criterion_id="c1", path="tests/test_b.py",
                  body="import json" + chr(10) + "from main import calculate_tip" + chr(10)
                       + "def test_b():" + chr(10) + "    assert calculate_tip(100, 10) == 10" + chr(10))
    assert got


def test_a_bare_surface_s_module_is_named_from_the_tree(db, tmp_path):
    """clickI night 25 (2026-09-12): the surface was bare `echo_json`, defined
    in src/click/echo_json.py, and the refusal listed .devcontainer, .github
    and .venv as the modules there. The tree names the module."""
    root = tmp_path / "wt"; (root / "src" / "pkg").mkdir(parents=True); (root / ".venv").mkdir()
    (root / "src" / "pkg" / "helper.py").write_text(
        "def calculate_tip(t, p):" + chr(10) + "    return t * p / 100" + chr(10), encoding="utf-8")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE criteria SET surface_refs = '[\"calculate_tip\"]' WHERE id = 'c1'")
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    with pytest.raises(ValueError, match="from pkg.helper import calculate_tip") as exc:
        sb.call("tests.encode", id="tst_a", criterion_id="c1", path="tests/test_a.py",
                body="from helper import calculate_tip" + chr(10) + "def test_a():" + chr(10)
                     + "    assert calculate_tip(100, 10) == 10" + chr(10))
    assert ".venv" not in str(exc.value)


def test_a_challenge_that_names_no_test_is_told_the_failing_ones(db):
    """clickI night 26 (2026-09-12): woken for a failing test, the Developer
    named a criterion with no test of its own and was refused with no way
    forward. The batch's failing tests are a fact the wake carries."""
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES "
               "('tst_x', 'b1', 'c1', 'tests/test_x.py', 'def test_x():" + chr(10) + "    assert 0')")
    db.execute("INSERT INTO test_runs (batch_id, test_id, result, output) VALUES ('b1', 'tst_x', 'fail', 'E assert 0')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c_other', 'tk1', 'another thing')")
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="tests_failing")
    with pytest.raises(ValueError, match=r"send refs=\['c1', 'tst_x'\]"):
        sb.call("msg.challenge_tester", refs=["c_other"], quotes=["another thing"])


def test_an_assumption_whose_halves_match_is_a_restatement(db):
    """seat2 on click (2026-09-12): reconcile logged "the README says X. The
    code shows X" nineteen times, and every one reached the person at the
    seat as an assumption to rule on."""
    from rota.roles import prompts

    db.execute("INSERT OR IGNORE INTO code_index (grain, grain_kind) VALUES ('README.md', 'path')")
    db.commit()
    sb = build("vision_keeper", db, mode="normal", area="@prose",
               allow=prompts.mode_tools("vision_keeper", "reconcile"))
    with pytest.raises(ValueError, match="say the same words"):
        sb.call("ledger.log", about_ref="README.md", about_table="items",
                assumption="the README says Click parses arguments into Python objects. The code shows Click parses arguments into Python objects.", kind="conflict")
    out = sb.call("ledger.log", about_ref="README.md", about_table="items",
                  assumption="the README says accounts can be merged; the code shows no merge path at all", kind="conflict")
    assert out


def test_a_surface_imported_from_a_module_that_lacks_it_is_pointed_at_its_file(db, tmp_path):
    """tipsAY (2026-09-12): `from split_bill import split_bill` against an
    empty split_bill/__init__.py while main.py held the function; four tests
    died at collection and the Developer challenged the Tester for it."""
    root = tmp_path / "wt"; (root / "calc").mkdir(parents=True)
    (root / "calc" / "__init__.py").write_text("", encoding="utf-8")
    (root / "main.py").write_text("def calculate_tip(t, p):" + chr(10) + "    return t * p / 100" + chr(10), encoding="utf-8")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE criteria SET surface_refs = '[\"calculate_tip\"]' WHERE id = 'c1'")
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    with pytest.raises(ValueError, match="calc/__init__.py does not define calculate_tip.*from main import calculate_tip"):
        sb.call("tests.encode", id="tst_a", criterion_id="c1", path="tests/test_a.py",
                body="from calc import calculate_tip" + chr(10) + "def test_a():" + chr(10)
                     + "    assert calculate_tip(100, 10) == 10" + chr(10))
    assert sb.call("tests.encode", id="tst_b", criterion_id="c1", path="tests/test_b.py",
                   body="from main import calculate_tip" + chr(10) + "def test_b():" + chr(10)
                        + "    assert calculate_tip(100, 10) == 10" + chr(10))


def test_a_test_that_uses_a_printing_surfaces_return_value_logs_the_assumption(db, tmp_path):
    """clickI night 28 (2026-09-13): the sentence said echo_json prints an
    object as JSON, the one test used its return value, the helper printed
    and returned None, and both desks ran to quarantine. Same shape as an
    invented literal: log the assumption, then the encode goes through."""
    root = tmp_path / "wt"; root.mkdir()
    (root / "script.py").write_text("import json" + chr(10) + "def echo_json(obj, indent=2):" + chr(10)
                                    + "    print(json.dumps(obj, indent=indent))" + chr(10), encoding="utf-8")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE criteria SET text = 'echo_json prints the object as JSON, indented', "
               "surface_refs = '[\"echo_json\"]' WHERE id = 'c1'")
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    body = ("from script import echo_json" + chr(10) + "def test_x():" + chr(10)
            + "    result = echo_json({'a': 1})" + chr(10) + "    assert result.startswith('{')" + chr(10))
    with pytest.raises(ValueError, match="uses what echo_json returns"):
        sb.call("tests.encode", id="tst_r", criterion_id="c1", path="tests/test_r.py", body=body)
    # The criterion itself says it prints, so no ledger row lifts the door
    # (night 45, 2026-09-14): the test reads what printed.
    sb.call("ledger.log", about_ref="c1", about_table="criteria",
            assumption="the test assumes echo_json returns what it prints", kind="default")
    with pytest.raises(ValueError, match="says it prints"):
        sb.call("tests.encode", id="tst_r", criterion_id="c1", path="tests/test_r.py", body=body)
    printed = ("from script import echo_json" + chr(10) + "def test_x(capsys):" + chr(10)
               + "    echo_json({'a': 1})" + chr(10) + "    out = capsys.readouterr().out" + chr(10)
               + "    assert out.startswith('{')" + chr(10))
    assert sb.call("tests.encode", id="tst_r", criterion_id="c1", path="tests/test_r.py", body=printed)


def test_a_clarify_may_quote_the_principals_own_words(db):
    """clickI night 29 (2026-09-13): "default_on_eof" is the flag in the
    principal's own sentence, and a clarify about it was refused as the
    Liaison's bookkeeping."""
    from rota.roles import prompts

    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
               "('e_p9','principal',9,'Let confirm() take a default_on_eof flag.')")
    db.commit()
    sb = build("liaison", db, mode="normal", allow=prompts.mode_tools("liaison", "unresolved"))
    sb.call("msg.clarify_principal", refs=["e_p9"],
            question="Should 'default_on_eof' apply when stdin is closed by a pipe as well?")
    with pytest.raises(ValueError, match="bookkeeping"):
        sb.call("msg.clarify_principal", refs=["e_p9"],
                question="What should 'batch_start_v2' do when stdin is closed?")


def test_a_clarify_that_pastes_the_principals_sentence_back_is_refused(db):
    """seat1 page 4 (2026-09-12): the reply went to its owner, the owner
    answered, and the Liaison asked the principal what they had said, with
    the whole reply pasted into the question. Eight of their words in a
    row is the fact. A short quote that anchors a question passes."""
    from rota.roles import prompts

    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
               "('e_p10','principal',10,'3 is wrong: each share is the total with "
               "tip divided by the number of people, and every share is equal.')")
    db.commit()
    sb = build("liaison", db, mode="normal", allow=prompts.mode_tools("liaison", "unresolved"))
    with pytest.raises(ValueError, match="own sentence"):
        sb.call("msg.clarify_principal", refs=["e_p10"],
                question="The principal said that 3 is wrong: each share is the total "
                         "with tip divided by the number of people, and every share "
                         "is equal. Does this mean the split is equal for all people?")
    sb.call("msg.clarify_principal", refs=["e_p10"],
            question="You said 'every share is equal'. Does the person who "
                     "paid the tip pay a share too?")


def test_a_commit_that_undoes_the_last_one_is_churn(db, tmp_path):
    """clickI night 30 (2026-09-13): twelve commits flipping a trailing
    newline, six pass verdicts each on a head the next commit left behind,
    no merge. The tree two commits back is a fact git holds."""
    import subprocess

    root = tmp_path / "wt"; root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    def commit_file(text, msg):
        (root / "script.py").write_text(text, encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", msg], check=True)
    a = "def close_account(x):" + chr(10) + "    return 1" + chr(10)
    b = "def close_account(x):" + chr(10) + "    return 1" + chr(10) + chr(10)
    commit_file(a, "a"); commit_file(b, "b")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE criteria SET surface_refs = '[\"script.py::close_account\"]' WHERE id = 'c1'")
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    sb.call("code.write", path="script.py", text=a)
    with pytest.raises(ValueError, match="undoing yourself"):
        sb.call("code.commit", message="back to a")
    sb.call("code.write", path="script.py", text=a + "def other():" + chr(10) + "    return 2" + chr(10))
    assert sb.call("code.commit", message="a real change").get("committed") is not False


def test_a_span_that_cuts_a_statement_is_told_where_the_boundaries_are(db, tmp_path):
    """clickI night 37 (2026-09-13): the span ended inside a multi-line
    signature, the merged file failed to parse, and the same write came six
    times against a refusal that named the symptom and not the cut."""
    root = tmp_path / "wt"; root.mkdir()
    (root / "m.py").write_text("import json\n\n\ndef echo(\n    message,\n    nl=True,\n):\n    print(message)\n\n\ndef other():\n    return 1\n")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    with pytest.raises(ValueError, match=r"falls inside echo \(lines 3 to 8.*start=8, end=8"):
        sb.call("code.write", path="m.py", start=5, end=8, text="def echo_json(o):\n    print(json.dumps(o))\n")
    out = sb.call("code.write", path="m.py", start=8, end=8, text="\n\ndef echo_json(o):\n    print(json.dumps(o))\n")
    assert out["bytes"]
    assert "dropped" not in out
    assert "def echo_json" in (root / "m.py").read_text() and "def other" in (root / "m.py").read_text()


def _span_refusal(db, tmp_path, src, start, end, text):
    root = tmp_path / "wt"; root.mkdir()
    (root / "m.py").write_text(src)
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    with pytest.raises(ValueError) as err:
        sb.call("code.write", path="m.py", start=start, end=end, text=text)
    return str(err.value)


def test_a_span_one_line_late_is_shown_the_file_at_its_boundaries(db, tmp_path):
    """Click night 96 (2026-09-29): s241 sent both boundaries one line late
    across two defs with no blank line between them. The refusal named only
    the second def, and the seat was editing the first."""
    src = ("def confirm(x):\n    if x:\n        return 1\n    return 0\n"
           "def pager(\n    a,\n):\n    return a\n")
    msg = _span_refusal(db, tmp_path, src, 2, 5, "    if x:\n        return 2\n")
    assert "end=5 falls inside pager (lines 4 to 8" in msg
    assert "start=2 is inside confirm (lines 0 to 4)" in msg
    assert "Line 2 is '        return 1'" in msg and "Line 4 is 'def pager('" in msg
    assert "start=1" in msg
    assert "To stop where if ends send end=3." in msg
    assert "end=4, which" not in msg


def test_a_boundary_in_a_docstring_names_the_def_and_the_docstring(db, tmp_path):
    """Click night 96 (2026-09-29): s225's end fell in get_pager_file's
    docstring, the door offered `expr`, and the seat wrote over the docstring."""
    src = ("def a():\n    x = 1\n    return x\n"
           "def b():\n    \"\"\"Doc\n    more.\n    \"\"\"\n    return 2\n")
    msg = _span_refusal(db, tmp_path, src, 2, 5, "    return 3\n")
    assert "end=5 falls inside b (lines 3 to 8" in msg
    assert "in its docstring at lines 4 to 7" in msg
    assert "expr" not in msg


def test_two_boundaries_inside_one_def_name_the_innermost_statement(db, tmp_path):
    """Click night 52 (2026-09-14): offering the whole function for an edit
    inside it looped three sessions."""
    src = "def confirm(text):\n    x = 1\n    value = f(\n        text)\n    return value\n"
    msg = _span_refusal(db, tmp_path, src, 1, 3, "    x = 2\n")
    assert "end=3 falls inside assignment (lines 2 to 4" in msg
    assert "falls inside confirm" not in msg
    assert "To replace assignment whole send start=2, end=4" in msg


def test_a_span_from_the_top_into_the_first_statement_gets_no_moved_boundary(db, tmp_path):
    """An end inside the first statement with start=0 has no moved end:
    end=0 is an empty span."""
    src = "def a(\n    x,\n):\n    return x\n\n\ndef b():\n    return 1\n"
    msg = _span_refusal(db, tmp_path, src, 0, 1, "def a(x):\n")
    assert "end=1 falls inside a (lines 0 to 4" in msg
    assert "alone" not in msg and "stop before" not in msg
    assert "To replace a whole send start=0, end=4" in msg


def test_a_moved_boundary_names_only_a_definition_as_the_thing_to_edit(db, tmp_path):
    """Frame 92's diff review (2026-09-29): an except handler's bound name
    gave "To edit err alone", and err is not a thing to edit."""
    src = ("def f():\n    try:\n        pass\n    except ValueError as err:\n        pass\n"
           "    finally:\n        y = h(\n            2)\n    return 1\n")
    msg = _span_refusal(db, tmp_path, src, 4, 7, "        pass\n")
    assert "end=7 falls inside assignment (lines 6 to 8" in msg
    assert "err alone" not in msg
    assert "To stop where except block ends send end=5." in msg
    assert "end=6" not in msg
    out = _write(db, tmp_path, 4, 5, "        pass\n")
    assert out["bytes"]


def test_two_boundaries_that_both_fall_get_no_moved_boundary(db, tmp_path):
    """Frame 92's diff review (2026-09-29): a moved start with an end still
    inside a statement is refused again at the other end."""
    src = "def a(\n    x,\n):\n    return x\ndef b(\n    y,\n):\n    return y\n"
    msg = _span_refusal(db, tmp_path, src, 1, 5, "    x,\n")
    assert "start=1 falls inside a (lines 0 to 4" in msg
    assert "end=5 also falls inside b (lines 4 to 8)" in msg
    assert "alone" not in msg and "start after" not in msg


_THREE_DEFS = ("def confirm(x):\n    y = f(\n        x)\n    return y\n"
               "def get_pager_file(a):\n    \"\"\"Doc.\"\"\"\n    return a\n"
               "def echo_via_pager(t):\n    \"\"\"Doc.\"\"\"\n    z = 1\n    return z\n")


def _write(db, tmp_path, start, end, text):
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    return sb.call("code.write", path="m.py", start=start, end=end, text=text)


def test_a_moved_start_comes_from_the_def_the_end_sits_in(db, tmp_path):
    """Click night 97 (2026-09-29): s215's start fell in confirm and its end
    in echo_via_pager. The door offered the end of confirm, and that span
    took get_pager_file whole and cut echo_via_pager."""
    msg = _span_refusal(db, tmp_path, _THREE_DEFS, 2, 10, "    z = 2\n")
    assert "To edit inside echo_via_pager send start=8, which is where the body of echo_via_pager starts." in msg
    assert "Your text replaces the docstring too." in msg
    assert "start=4, which" not in msg
    out = _write(db, tmp_path, 8, 10, "    \"\"\"Doc.\"\"\"\n    z = 2\n")
    assert out["bytes"]
    assert "def get_pager_file(a):" in (tmp_path / "wt" / "m.py").read_text()


def test_an_end_on_a_docstring_gets_the_whole_def_and_no_moved_start(db, tmp_path):
    """Click night 97 (2026-09-29): s217's end sat on get_pager_file's
    docstring. The moved start at the def's header replaced the signature
    and left the body."""
    msg = _span_refusal(db, tmp_path, _THREE_DEFS, 2, 5, "    return 0\n")
    assert "To replace get_pager_file whole send start=4, end=7." in msg
    assert "alone" not in msg and "start=4, which" not in msg
    out = _write(db, tmp_path, 4, 7, "def get_pager_file(a):\n    return None\n")
    assert out["bytes"]
    assert "def echo_via_pager(t):" in (tmp_path / "wt" / "m.py").read_text()


def test_an_end_inside_a_loop_gets_a_start_at_the_loop_body(db, tmp_path):
    """Frame 92's diff review of pass 4 (2026-09-29): an end inside a for
    loop got no moved start, and the old code offered none."""
    src = ("def a(x):\n    y = f(\n        x)\n    return y\n"
           "for i in r:\n    p = 1\n    q = 2\nz = 3\n")
    msg = _span_refusal(db, tmp_path, src, 2, 6, "    p = 9\n")
    assert "To edit inside for send start=5, which is where the body of for starts." in msg
    assert "alone" not in msg and "docstring" not in msg
    out = _write(db, tmp_path, 5, 6, "    p = 9\n")
    assert out["bytes"]


def test_a_whole_decorated_def_starts_at_its_first_decorator(db, tmp_path):
    """Frame 92's diff review of pass 4 (2026-09-29): the whole-def span
    started at the def line and left the decorator above it."""
    src = ("def a(x):\n    y = f(\n        x)\n    return y\n"
           "@dec\ndef b():\n    return 1\n")
    msg = _span_refusal(db, tmp_path, src, 2, 6, "    return 0\n")
    assert "To replace b whole send start=4, end=7." in msg
    out = _write(db, tmp_path, 4, 7, "@dec\ndef b():\n    return 2\n")
    assert out["bytes"]
    assert (tmp_path / "wt" / "m.py").read_text().count("@dec") == 1


def _passes(db, tmp_path, src, start, end):
    (tmp_path / "wt" / "m.py").write_text(src)
    lines = src.splitlines(keepends=True)
    return _write(db, tmp_path, start, end, "".join(lines[start:end]))["bytes"]


_TRY = ("def g():\n    try:\n        a = 1\n    except E:\n        b = (\n            2)\n"
        "        c = 3\n    finally:\n        d = 4\n    if x:\n        e = 5\n    elif y:\n"
        "        e = 6\n    else:\n        h = (\n            6)\n        k = 7\n")


def test_a_moved_end_in_an_elif_body_stops_before_the_else_header(db, tmp_path):
    """Frame 92's diff review of pass 5 (2026-09-29): end=14 took the else:
    header, and the else body joined the elif body."""
    msg = _span_refusal(db, tmp_path, _TRY, 12, 15, "        e = 7\n")
    assert "To stop where the body of elif ends send end=13." in msg
    assert "end=14" not in msg
    assert _passes(db, tmp_path, _TRY, 12, 13)


def test_a_moved_end_in_a_loop_body_stops_before_the_else_header(db, tmp_path):
    """Frame 92's diff review of pass 5 (2026-09-29): end=7 took the loop's
    else: header."""
    src = ("def g():\n    u = (\n        1)\n    for i in r:\n        p = 1\n        q = 2\n"
           "    else:\n        w = (\n            3)\n        v = 4\n    z = 5\n")
    msg = _span_refusal(db, tmp_path, src, 4, 8, "        p = 2\n")
    assert "To stop where the body of for ends send end=6." in msg
    assert "end=7" not in msg
    assert _passes(db, tmp_path, src, 4, 6)


def test_a_moved_end_in_a_try_body_stops_before_the_finally_header(db, tmp_path):
    """Frame 92's diff review of pass 5 (2026-09-29): end=4 took the
    finally: header."""
    src = "def g():\n    try:\n        a = 1\n    finally:\n        d = (\n            4)\n"
    msg = _span_refusal(db, tmp_path, src, 2, 5, "        a = 2\n")
    assert "To stop where the body of try ends send end=3." in msg
    assert "end=4" not in msg
    assert _passes(db, tmp_path, src, 2, 3)


def test_a_span_from_one_def_into_the_next_is_refused_with_both_edges(db, tmp_path):
    """Frame 92's diff review of pass 5 (2026-09-29): each boundary was
    whole alone, and the span removed the header of async def h."""
    src = ("x = (\n    1)\nclass C:\n    '''Doc.'''\n    a = 1\n    b = 2\n"
           "async def h():\n    '''D.'''\n    await y\n    return 1\n")
    msg = _span_refusal(db, tmp_path, src, 4, 8, "    a = 2\n")
    assert "crosses from one block to another" in msg
    # Frame 313: each block names its own lines.
    assert "start=4 is in the body of C (lines 3 to 6)." in msg
    assert "end=8 is in the body of h (lines 7 to 10)." in msg
    assert "To edit C alone send end=6, which is where C ends." in msg
    assert "To edit inside h send start=7, which is where the body of h starts." in msg
    assert "Your text replaces the docstring too." in msg
    assert "To replace the whole top-level statements send start=2, end=10." in msg
    for s, e in ((4, 6), (7, 8), (2, 10)):
        assert _passes(db, tmp_path, src, s, e)


def test_a_span_that_ends_on_a_finally_header_is_refused(db, tmp_path):
    """Frame 92's diff review of pass 5 (2026-09-29): the span 6 to 8 ended
    on the finally: header and passed."""
    msg = _span_refusal(db, tmp_path, _TRY, 6, 8, "        c = 4\n")
    assert "end=8 is in the finally block of try (lines 8 to 9)." in msg
    assert "To stop where except block ends send end=7." in msg
    assert "To replace try whole send start=1, end=9." in msg
    for s, e in ((6, 7), (1, 9)):
        assert _passes(db, tmp_path, _TRY, s, e)


def test_a_start_on_a_decorated_def_line_names_the_decorators(db, tmp_path):
    """Frame 92's diff review of pass 5 (2026-09-29): a start on the def
    line was refused with no word about the decorators."""
    src = "@dec\n@dec2(\n    1)\ndef f():\n    a = 1\n    return a\nx = 1\n"
    msg = _span_refusal(db, tmp_path, src, 3, 6, "def f():\n    return 1\n")
    assert "start=3 is below the decorators of f, which start at line 0." in msg
    assert "To replace f whole send start=0, end=6." in msg
    assert _passes(db, tmp_path, src, 0, 6)


_MATCH = ("def a():\n    x = 1\n    # note\n    y = 2\n\n\n    z = 3\n"
          "def d(v):\n    match v:\n        case 1:\n            r = 1\n            s = 2\n"
          "        case _:\n            r = 0\n    return r\n")


def test_an_edit_inside_a_case_body_is_accepted(db, tmp_path):
    """Frame 92's diff review of 6e993d0 (2026-09-29): every edit inside a
    case body was refused as falling inside match."""
    root = tmp_path / "wt"; root.mkdir()
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    for s, e in ((10, 11), (9, 12)):
        assert _passes(db, tmp_path, _MATCH, s, e)
    (root / "m.py").write_text(_MATCH)
    assert _write(db, tmp_path, 11, 11, "            t = 1\n")["bytes"]


def test_a_boundary_on_a_blank_line_between_statements_is_accepted(db, tmp_path):
    """Frame 92's diff review of 6e993d0 (2026-09-29): an insert on the
    blank lines inside a def was refused as a cut of the def."""
    root = tmp_path / "wt"; root.mkdir()
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    (root / "m.py").write_text(_MATCH)
    assert _write(db, tmp_path, 5, 5, "    w = 0\n")["bytes"]
    assert _passes(db, tmp_path, _MATCH, 4, 7)


def test_an_elif_clause_span_is_offered_the_elif_from_its_own_line(db, tmp_path):
    """Frame 92's diff review of 6e993d0 (2026-09-29): the span 9 to 11 was
    offered start=10, and the elif header was dropped."""
    src = ("def b():\n    if x:\n        y = 1\n    elif z:\n        y = 2\n"
           "    else:\n        y = 3\n    return y\n")
    msg = _span_refusal(db, tmp_path, src, 3, 5, "    elif z:\n        y = 5\n")
    assert "To replace elif whole send start=3, end=7." in msg
    assert _passes(db, tmp_path, src, 3, 7)


def test_the_refusal_names_statements_with_the_words_of_the_source(db, tmp_path):
    """Frame 92's diff review of 6e993d0 (2026-09-29): the seat read an
    elif as if, a docstring as expr and an except handler as excepthandler."""
    src = ("def f():\n    '''Doc.'''\n    try:\n        a = 1\n    except E as err:\n"
           "        b = 2\n    if p:\n        c = 3\n    elif q:\n        d = (\n            4)\n")
    msg = _span_refusal(db, tmp_path, src, 5, 10, "        b = 3\n")
    assert "To stop where except block ends send end=6." in msg
    assert "excepthandler" not in msg and "err" not in msg
    (tmp_path / "wt" / "m.py").write_text(src)
    with pytest.raises(ValueError) as err:
        _write(db, tmp_path, 1, 1, "    w = 0\n")
    assert "line 1 is the docstring of f. Your text goes before it." in str(err.value)
    assert "start=2, end=2" in str(err.value)


def test_a_span_from_a_blank_line_before_else_is_refused_with_an_offer(db, tmp_path):
    """Frame 92's diff review of 928b2dc (2026-09-29): body and orelse read
    as one list, and the span 4 to 6 raised IndexError in the door."""
    src = "def a():\n    if x:\n        y = 1\n\n    else:\n        y = 3\n    return y\n"
    msg = _span_refusal(db, tmp_path, src, 4, 6, "    else:\n        y = 4\n")
    assert "To edit inside if send start=5, which is where the else block of if starts." in msg
    assert "To replace if whole send start=1, end=6." in msg
    for s, e in ((5, 6), (1, 6)):
        assert _passes(db, tmp_path, src, s, e)


def test_a_bracketed_case_pattern_starts_at_its_case_line(db, tmp_path):
    """Frame 92's diff review of 928b2dc (2026-09-29): a case whose pattern
    starts below `case (` began at the pattern's line."""
    src = ("def d(v):\n    match v:\n        case (\n            2 | 3\n        ):\n"
           "            r = 2\n        case _:\n            r = 0\n    return r\n")
    root = tmp_path / "wt"; root.mkdir()
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    assert _passes(db, tmp_path, src, 2, 6)


def test_a_module_docstring_takes_no_insert_and_a_bare_string_is_no_docstring(db, tmp_path):
    """Frame 92's diff review of 928b2dc (2026-09-29): an insert before the
    module docstring passed, and any bare string was named a docstring."""
    src = "# head\n'''Mod.'''\ndef f():\n    x = 1\n    '''n\n    m'''\n    y = 2\n"
    msg = _span_refusal(db, tmp_path, src, 1, 1, "import os\n")
    assert "line 1 is the docstring of the module." in msg
    assert "start=2, end=2" in msg
    (tmp_path / "wt" / "m.py").write_text(src)
    with pytest.raises(ValueError) as err:
        _write(db, tmp_path, 3, 5, "    x = 2\n")
    assert "end=5 falls inside expression" in str(err.value)
    assert "docstring" not in str(err.value)


def test_a_docstring_sent_at_start_0_end_0_goes_above_the_file(db, tmp_path):
    """Frame 94 (2026-09-30): start=0, end=0 was read as the whole file,
    so a module docstring sent there replaced every line below it."""
    src = "import os\n\n\ndef f():\n    return os.sep\n"
    root = tmp_path / "wt"; root.mkdir()
    (root / "m.py").write_text(src)
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    assert _write(db, tmp_path, 0, 0, '"""Mod."""\n')["bytes"]
    assert (root / "m.py").read_text() == '"""Mod."""\n' + src


def test_an_empty_span_removes_its_lines_and_an_empty_whole_write_removes_the_file(db, tmp_path):
    """Frame 94 (2026-09-30): an empty text with a span removed the whole
    file the batch added. An empty span removes only its lines."""
    src = "def a():\n    return 1\n\n\ndef b():\n    return 2\n\n\ndef c():\n    return 3\n"
    root = tmp_path / "wt"; root.mkdir()
    (root / "m.py").write_text(src)
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    assert _write(db, tmp_path, 7, 10, "")["bytes"]
    assert (root / "m.py").read_text() == "def a():\n    return 1\n\n\ndef b():\n    return 2\n\n"
    assert _write(db, tmp_path, 4, 6, "\n")["bytes"]
    assert (root / "m.py").read_text() == "def a():\n    return 1\n\n\n\n"
    out = _write(db, tmp_path, 0, -1, "")
    assert out["removed"] == "m.py" and not (root / "m.py").exists()


def test_a_bare_expression_statement_is_named_an_expression(db, tmp_path):
    """Frame 94 (2026-09-30): the refusal named a bare call statement
    with the class name expr, a word the source never shows."""
    src = "def f():\n    x = 1\n    g(\n        x)\n    return x\n"
    msg = _span_refusal(db, tmp_path, src, 1, 3, "    x = 2\n")
    assert "end=3 falls inside expression (lines 2 to 4" in msg
    assert re.search(r"\bexpr\b", msg) is None


def test_a_case_pattern_line_that_starts_with_case_underscore_is_no_case_header(db, tmp_path):
    """Frame 94 (2026-09-30): the walk back to a case header stopped on
    any line that starts with the letters case, such as `case_ids.A`."""
    src = ("def d(v):\n    match v:\n        case (\n            case_ids.A\n"
           "            | 2\n        ):\n            r = (\n                2)\n"
           "        case _:\n            r = 0\n    return r\n")
    msg = _span_refusal(db, tmp_path, src, 3, 6, "            r = 3\n")
    assert "start=3 falls inside case (lines 2 to 8" in msg
    assert "To replace case whole send start=2, end=8." in msg
    assert _passes(db, tmp_path, src, 2, 8)


def test_a_case_pattern_line_that_starts_with_case_dot_is_no_case_header(db, tmp_path):
    """Frame 94's diff review of 44e156a (2026-09-30): a word match still
    stopped the walk on `case.A`, because a dot ends a word."""
    src = ("def d(v):\n    match v:\n        case (\n            case.A\n"
           "            | 2\n        ):\n            r = (\n                2)\n"
           "        case _:\n            r = 0\n    return r\n")
    msg = _span_refusal(db, tmp_path, src, 3, 6, "            r = 3\n")
    assert "start=3 falls inside case (lines 2 to 8" in msg
    assert "To replace case whole send start=2, end=8." in msg
    assert _passes(db, tmp_path, src, 2, 8)


def test_an_insert_above_a_future_import_is_refused_with_the_line_after_it(db, tmp_path):
    """Frame 94's diff review of 44e156a (2026-09-30): 0..0 put an import
    above `from __future__`, and compile refused the file at import."""
    src = '"""Mod."""\nfrom __future__ import annotations\n\nimport os\n'
    msg = _span_refusal(db, tmp_path, src, 0, 0, "import sys\n")
    assert "above the `from __future__` import at line 1." in msg
    assert "To add after it send start=2, end=2." in msg
    assert _write(db, tmp_path, 2, 2, "import sys\n")["bytes"]
    (tmp_path / "wt" / "m.py").write_text("from __future__ import annotations\nimport os\n")
    assert _write(db, tmp_path, 0, 0, "from __future__ import division\n")["bytes"]
    assert (tmp_path / "wt" / "m.py").read_text().startswith("from __future__ import division\n")


def test_an_insert_after_a_docstring_above_a_future_import_is_refused(db, tmp_path):
    """Frame 94's diff review of f986adb (2026-09-30): the docstring door
    offers the line after the docstring, and an insert there still lands
    above `from __future__`. A comment is no statement and passes."""
    src = '"""Mod."""\nfrom __future__ import annotations\n\nimport os\n'
    msg = _span_refusal(db, tmp_path, src, 1, 1, "import sys\n")
    assert "above the `from __future__` import at line 1." in msg
    assert "To add after it send start=2, end=2." in msg
    with pytest.raises(ValueError, match="To add after it send start=2, end=2."):
        _write(db, tmp_path, 1, 1, '"""Another."""\n')
    assert _write(db, tmp_path, 1, 1, "# a note\n")["bytes"]
    assert (tmp_path / "wt" / "m.py").read_text() == (
        '"""Mod."""\n# a note\nfrom __future__ import annotations\n\nimport os\n')
    (tmp_path / "wt" / "m.py").write_text("from __future__ import annotations\nimport os\n")
    assert _write(db, tmp_path, 0, 0, "# head\n\n")["bytes"]
    with pytest.raises(ValueError, match="To add after it send start=3, end=3."):
        _write(db, tmp_path, 0, 0, '"""Mod."""\n')


def test_a_case_header_is_found_by_its_shape_and_not_by_its_letters(db, tmp_path):
    """Frame 94's diff review of f986adb (2026-09-30): `case{`, `case-1`
    and `case"x"` are headers with no space after the word."""
    root = tmp_path / "wt"; root.mkdir()
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    for header in ('case{"a": 1}:', "case-1:", 'case"x":'):
        src = ("def d(v):\n    match v:\n        " + header + "\n            r = (\n"
               "                2)\n        case _:\n            r = 0\n    return r\n")
        assert _passes(db, tmp_path, src, 2, 5), header


def _empty_tree(db, tmp_path, src):
    root = tmp_path / "wt"; root.mkdir()
    (root / "m.py").write_text(src)
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    return root / "m.py"


def test_a_blank_insert_into_an_empty_file_keeps_the_file(db, tmp_path):
    """Frame 94's second diff review (2026-09-30): a blank insert at 0..0
    into an empty `__init__.py` the batch added removed the file."""
    f = _empty_tree(db, tmp_path, "")
    assert "removed" not in _write(db, tmp_path, 0, 0, "")
    assert f.exists()
    assert "removed" not in _write(db, tmp_path, 0, 0, "\n")
    assert f.exists()


def test_a_blank_span_that_leaves_only_blank_lines_removes_the_file(db, tmp_path):
    """Frame 94's second diff review (2026-09-30): 0..1 with an empty text
    on `x = 1` and two blank lines left a file of two newlines."""
    f = _empty_tree(db, tmp_path, "x = 1\n\n\n")
    assert _write(db, tmp_path, 0, 1, "")["removed"] == "m.py"
    assert not f.exists()


def test_a_comment_inserted_above_a_module_docstring_passes(db, tmp_path):
    """Frame 94's second diff review (2026-09-30): a comment at 0..0 above
    the module docstring was refused, and a comment leaves the docstring
    a docstring."""
    f = _empty_tree(db, tmp_path, '"""Mod."""\nx = 1\n')
    assert _write(db, tmp_path, 0, 0, "# head\n")["bytes"]
    assert f.read_text() == '# head\n"""Mod."""\nx = 1\n'
    with pytest.raises(ValueError, match="line 1 is the docstring of the module"):
        _write(db, tmp_path, 1, 1, "import os\n")


def test_a_file_that_parses_and_does_not_compile_is_refused(db, tmp_path):
    """Frame 94's second diff review (2026-09-30): a `from __future__`
    import after another statement passed ast.parse and failed at import."""
    f = _empty_tree(db, tmp_path, "import os\nx = 1\n")
    with pytest.raises(ValueError) as err:
        _write(db, tmp_path, 1, 1, "from __future__ import annotations\n")
    msg = str(err.value)
    assert "m.py is not valid Python (from __future__ imports must occur" in msg
    assert "line 1 in code.source numbering" in msg
    assert f.read_text() == "import os\nx = 1\n"


def test_a_newline_escape_the_decoder_broke_is_written_back(db, tmp_path):
    """Night 99 (2026-09-30): s134 wrote `out += "\\n"`, the decoder made
    the escape a line break, and the parse door refused the text."""
    f = _empty_tree(db, tmp_path, "import os\n")
    out = _write(db, tmp_path, 1, 1,
                 "def f(out):\n    out += \"\n\"\n    return out\n")
    assert 'out += "\\n"\n' in f.read_text()
    compile(f.read_text(), "m.py", "exec")
    assert out["repaired"] == (
        "Line 2 of your text, counting from 1, ended inside a string literal, "
        "so its line break is written as the two characters \\n.")


def test_two_broken_newline_escapes_are_both_written_back(db, tmp_path):
    """Night 99 (2026-09-30): the Developer's sessions on bg_1 wrote the
    escape more than once in one text, so every break is named."""
    f = _empty_tree(db, tmp_path, "import os\n")
    out = _write(db, tmp_path, 1, 1,
                 "def f(out):\n    out += \"\n\"\n    out += 'a\n'\n    return out\n")
    text = f.read_text()
    assert 'out += "\\n"\n' in text and "out += 'a\\n'\n" in text
    assert out["repaired"].startswith("Lines 2 and 4 of your text, counting from 1,")


def test_a_broken_string_the_next_line_does_not_close_is_refused(db, tmp_path):
    """Night 99 (2026-09-30): a repair joins a break only when the next line
    closes the same quote, so this text is refused with the escape form."""
    f = _empty_tree(db, tmp_path, "import os\n")
    with pytest.raises(ValueError) as err:
        _write(db, tmp_path, 1, 1, "def f(out):\n    out += \"\n    return out\n")
    msg = str(err.value)
    assert "Your text itself does not parse: line 2 of it, counting from 1" in msg
    assert ("In your call write the newline escape inside a string as a backslash, "
            "a backslash and n, \\\\n, because the tool decodes one \\n into a line "
            "break.") in msg
    assert f.read_text() == "import os\n"


def test_escaped_docstring_quotes_are_refused_with_the_plain_form(db, tmp_path):
    """Night 99 (2026-09-30): s133 wrote the docstring quotes as `\\"\\"\\"`
    at turns 14 and 15, and a backslash outside a string does not parse."""
    f = _empty_tree(db, tmp_path, "import os\n")
    with pytest.raises(ValueError) as err:
        _write(db, tmp_path, 1, 1,
               'def f():\n    \\"\\"\\"Doc.\\"\\"\\"\n    return 1\n')
    msg = str(err.value)
    assert ('Line 2 of your text starts with \\"\\"\\"; write the docstring '
            'quotes as three plain quotes.') in msg
    assert "In your call write the newline escape" not in msg
    assert f.read_text() == "import os\n"


# The text of s134's call at turn 21 of night 99, decoded by rota.llm.toolproto.
_S134_T21 = (
    'def echo_json(\n    obj: object,\n    nl: bool = True,\n    err: bool = False,\n'
    ') -> None:\n    """Print a JSON representation of an object to stdout or a file.\n\n'
    '    This function uses :func:`json.dumps` with compact separators and\n'
    '    no formatting characters, ensuring the output is pure JSON text\n'
    '    suitable for piping.\n\n    :param obj: The object to serialize as JSON.\n'
    '    :param nl: Print a newline after the JSON. Enabled by default.\n'
    '    :param err: Write to ``stderr`` instead of ``stdout``.\n\n'
    '    .. versionadded:: 8.17.0\n    """\n    import json\n\n    if file is None:\n'
    '        if err:\n            file = _default_text_stderr()\n        else:\n'
    '            file = _default_text_stdout()\n\n'
    '        # There are no standard streams attached to write to. For example,\n'
    '        # pythonw on Windows.\n        if file is None:\n            return\n\n'
    '    try:\n        out = json.dumps(obj, separators=(",", ":"))\n'
    '    except (TypeError, ValueError) as e:\n'
    '        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable") from e\n\n'
    '    if nl:\n        out += "\n"\n\n    file.write(out)  # type: ignore\n    file.flush()\n')


def test_the_s134_text_of_night_99_lands_with_its_escape(db, tmp_path):
    """Night 99 (2026-09-30): s134's text at turn 21 was refused at the
    parse door for `out += "\\n"`, and batch bg_1 was quarantined."""
    src = "import sys\n\n\ndef echo(m):\n    print(m)\n"
    f = _empty_tree(db, tmp_path, src)
    out = _write(db, tmp_path, 5, 5, _S134_T21)
    text = f.read_text()
    compile(text, "m.py", "exec")
    assert '        out += "\\n"\n' in text
    assert text.startswith(src)
    assert out["repaired"].startswith("Line 37 of your text, counting from 1,")


def test_a_broken_escape_in_an_indented_span_is_written_back(db, tmp_path):
    """Frame 99's diff review of edd3638 (2026-09-30): a span inside a def
    failed with `unexpected indent` before the repair started."""
    f = _empty_tree(db, tmp_path, "def f(out):\n    out = ''\n    return out\n")
    out = _write(db, tmp_path, 2, 2, "    out += \"\n\"\n")
    assert f.read_text() == "def f(out):\n    out = ''\n    out += \"\\n\"\n    return out\n"
    assert out["repaired"].startswith("Line 1 of your text, counting from 1,")


def test_a_broken_string_that_goes_on_at_a_smaller_indent_is_written_back(db, tmp_path):
    """Frame 99's second diff review of 85f7c4f (2026-09-30): the rest of
    the string at indent 2 shrank the prefix, and the view did not parse."""
    f = _empty_tree(db, tmp_path, "def f(out):\n    out = ''\n    return out\n")
    _write(db, tmp_path, 2, 2, "    out += \"a\n  b\"\n")
    assert f.read_text() == "def f(out):\n    out = ''\n    out += \"a\\n  b\"\n    return out\n"


def test_a_closing_quote_at_indent_4_under_a_span_at_indent_8_is_written_back(db, tmp_path):
    """Frame 99's second diff review of 85f7c4f (2026-09-30): the line that
    closes the string sits at a smaller indent than the span."""
    src = "def f(out):\n    if out:\n        out = ''\n    return out\n"
    f = _empty_tree(db, tmp_path, src)
    _write(db, tmp_path, 3, 3, "        out += \"a\n    b\"\n")
    assert "        out = ''\n        out += \"a\\n    b\"\n    return out\n" in f.read_text()


def test_a_broken_crlf_escape_keeps_both_escapes(db, tmp_path):
    """Frame 99's second diff review of 85f7c4f (2026-09-30): the decoder
    reads "\\r\\n" as CR LF, and the join wrote only \\n."""
    f = _empty_tree(db, tmp_path, "import os\n")
    _write(db, tmp_path, 1, 1, "sep = \"\r\n\"\n")
    assert f.read_text() == "import os\nsep = \"\\r\\n\"\n"


def test_a_crlf_join_is_named_as_four_characters(db, tmp_path):
    """Frame 99's third diff review of 5d54e9a (2026-09-30): the file held
    \\r\\n, and the landed sentence named the two characters \\n."""
    _empty_tree(db, tmp_path, "import os\n")
    out = _write(db, tmp_path, 1, 1, "sep = \"\r\n\"\n")
    assert out["repaired"] == (
        "Line 1 of your text, counting from 1, ended inside a string literal, "
        "so its line break is written as the four characters \\r\\n.")


def test_a_span_that_starts_with_a_comment_at_column_0_is_repaired(db, tmp_path):
    """Frame 99's third diff review of 5d54e9a (2026-09-30): a comment at
    column 0 set an empty prefix, and the view failed with an indent error."""
    f = _empty_tree(db, tmp_path, "def f(out):\n    out = ''\n    return out\n")
    _write(db, tmp_path, 2, 2, "# note\n    out += \"\n\"\n")
    assert f.read_text() == ("def f(out):\n    out = ''\n# note\n    out += \"\\n\"\n"
                             "    return out\n")


def test_a_whole_file_with_25_broken_escapes_is_written_back(db, tmp_path):
    """Frame 99's second diff review of 85f7c4f (2026-09-30): a cap of 20
    joins left five breaks, and the refusal discarded every join."""
    f = _empty_tree(db, tmp_path, "import os\n")
    text = "import os\n" + "".join(f"x{k} = \"a\n\"\n" for k in range(25))
    out = _write(db, tmp_path, 0, -1, text)
    body = f.read_text()
    compile(body, "m.py", "exec")
    assert body.count("\"a\\n\"\n") == 25
    assert out["repaired"].startswith("Lines 2, 4, 6,")
    assert "48 and 50 of your text" in out["repaired"]


def test_an_indented_span_that_does_not_parse_is_told_its_own_line(db, tmp_path):
    """Frame 99's diff review of edd3638 (2026-09-30): every indented span
    was told line 1, `unexpected indent`, and not the line at fault."""
    f = _empty_tree(db, tmp_path, "def f(out):\n    out = ''\n    return out\n")
    with pytest.raises(ValueError) as err:
        _write(db, tmp_path, 2, 2, "    x = 1\n    y = 2\n    z = (\n")
    assert "Your text itself does not parse: line 3 of it, counting from 1, is 'z = ('" in str(err.value)
    assert f.read_text() == "def f(out):\n    out = ''\n    return out\n"


def test_a_literal_with_two_escapes_is_joined_across_three_lines(db, tmp_path):
    """Frame 99's diff review of edd3638 (2026-09-30): two escapes in one
    literal arrive as three lines, and the middle line closes no quote."""
    f = _empty_tree(db, tmp_path, "def f():\n    return 1\n")
    out = _write(db, tmp_path, 1, 2, "    return \"a\nb\n\"\n")
    assert f.read_text() == "def f():\n    return \"a\\nb\\n\"\n"
    assert out["repaired"].startswith("Line 1 of your text, counting from 1,")


def test_a_broken_f_string_is_written_back(db, tmp_path):
    """Frame 99's diff review of edd3638 (2026-09-30): Python names a broken
    f-string `unterminated f-string literal`, and the repair skipped it."""
    f = _empty_tree(db, tmp_path, "def f(x):\n    return 1\n")
    _write(db, tmp_path, 1, 2, "    return f\"{x}\n\"\n")
    assert f.read_text() == "def f(x):\n    return f\"{x}\\n\"\n"


def test_two_joins_on_one_line_name_the_line_once(db, tmp_path):
    """Frame 99's diff review of edd3638 (2026-09-30): a second join on the
    same line named it twice, as "Lines 2 and 2"."""
    f = _empty_tree(db, tmp_path, "import os\n")
    out = _write(db, tmp_path, 1, 1, "def f():\n    return \"a\n\" + \"b\n\"\n")
    assert '    return "a\\n" + "b\\n"\n' in f.read_text()
    assert out["repaired"] == (
        "Line 2 of your text, counting from 1, ended inside a string literal, "
        "so its line break is written as the two characters \\n.")


def test_escaped_quotes_inside_a_docstring_get_no_docstring_sentence(db, tmp_path):
    """Frame 99's diff review of edd3638 (2026-09-30): a line inside a
    docstring may start with `\\"\\"\\"` as its own text."""
    _empty_tree(db, tmp_path, "import os\n")
    with pytest.raises(ValueError) as err:
        _write(db, tmp_path, 1, 1,
               'def f():\n    """Doc.\n    \\"\\"\\" is text here.\n    """\n    return (\n')
    assert "docstring quotes as three plain quotes" not in str(err.value)
    assert "Your text itself does not parse" in str(err.value)


def test_a_repaired_insert_above_a_future_import_is_refused(db, tmp_path):
    """Frame 99's diff review of edd3638 (2026-09-30): the `__future__` door
    read the broken text, passed it, and the refusal named the string."""
    f = _empty_tree(db, tmp_path, "from __future__ import annotations\nx = 1\n")
    with pytest.raises(ValueError) as err:
        _write(db, tmp_path, 0, 0, "y = \"a\n\"\n")
    assert "Python refuses any statement above the `from __future__` import at line 0" in str(err.value)
    assert f.read_text() == "from __future__ import annotations\nx = 1\n"


def test_a_blank_span_over_every_line_is_an_empty_write_of_the_file(db, tmp_path):
    """Frame 94's diff review of 44e156a (2026-09-30): 0..3 with an empty
    text left a file that holds one newline."""
    root = tmp_path / "wt"; root.mkdir()
    (root / "m.py").write_text("def a():\n    return 1\n\n")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    assert _write(db, tmp_path, 0, 3, "")["removed"] == "m.py"
    assert not (root / "m.py").exists()
    (root / "m.py").write_text("def a():\n    return 1\n")
    assert _write(db, tmp_path, 0, -2, "   ")["removed"] == "m.py"
    assert not (root / "m.py").exists()


def test_a_start_with_no_end_is_refused(db, tmp_path):
    """Frame 94's diff review of 44e156a (2026-09-30): start=4 with no end
    took the whole-file path, and the fragment became the file."""
    src = "def a():\n    return 1\n\n\ndef b():\n    return 2\n"
    msg = _span_refusal(db, tmp_path, src, 4, None, "def b():\n    return 3\n")
    assert "start=4 came with no end. Send end=-1 for the whole file" in msg
    assert (tmp_path / "wt" / "m.py").read_text() == src


def test_an_item_asserted_from_a_delivered_statement_links_to_it(db):
    """clickI night 37 (2026-09-13): one ratified statement, one item read
    from it through the Liaison's deliver, and an empty `item_statements`."""
    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES ('e_p1','principal',1,'Add echo_json next to echo.')")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, status) VALUES "
               "('s1','e_p1',0,28,'Add echo_json next to echo.','ratified')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, body_refs, seq) "
               "VALUES ('m_d','t1','liaison','vision_keeper','deliver','[\"s1\"]',1)")
    db.commit()
    from rota.roles import prompts
    sb = build("vision_keeper", db, mode="normal", allow=prompts.mode_tools("vision_keeper", "deliver"))
    sb.ctx.trigger = "m_d"
    sb.call("problem.assert", id="echo_json", text="add an echo_json helper next to echo", kind="in_scope")
    links = [w for w in sb.ctx.writes if w[0] == "refs" and w[2]["kind"] == "statement"]
    assert [(w[1], w[2]["src_id"], w[2]["target"]) for w in links] == \
        [("items:echo_json:statement:s1", "echo_json", "s1")]


def test_the_fence_judges_the_change_not_the_file_it_was_made_in(db, tmp_path):
    """clickI night 38 (2026-09-13): click's own utils.py calls
    os.path.expanduser at line 547, and every write to the file was refused
    for a reach the project already made."""
    root = tmp_path / "wt"; root.mkdir()
    (root / "utils.py").write_text("import os\n\n\ndef home():\n    return os.path.expanduser('~')\n\n\ndef echo(m):\n    print(m)\n")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    out = sb.call("code.write", path="utils.py", start=9, end=9,
                  text="\n\ndef echo_json(o):\n    import json\n    print(json.dumps(o))\n")
    assert out["bytes"], "a reach the file already made is not this change's"
    with pytest.raises(ValueError, match="reaches the process"):
        sb.call("code.write", path="utils.py", start=14, end=14,
                text="\n\ndef run():\n    import subprocess\n    subprocess.run(['ls'])\n")


def _fence_repo(root):
    import subprocess

    def git(*args):
        subprocess.run(["git", "-C", str(root), "-c", "user.name=t",
                        "-c", "user.email=t@t", *args], check=True, capture_output=True)
    root.mkdir()
    git("init", "-q")
    (root / "decorators.py").write_text(
        "import importlib.metadata\n\n\ndef version():\n"
        "    return importlib.metadata.version('click')\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    # The batch's head lost the base's line, as s524's head had.
    (root / "decorators.py").write_text("def version():\n    return '8'\n")
    git("commit", "-q", "-am", "head")


def test_s524s_restore_of_the_base_commits_reach_is_not_fenced(db, tmp_path):
    """Night 143 (frame 220): s524 put back the base commit's line 513,
    `import importlib.metadata`, and the fence refused it. The working file
    had lost the line, so the baseline lacked the reach (law 12)."""
    root = tmp_path / "wt"
    _fence_repo(root)
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    out = sb.call("code.write", path="decorators.py",
                  text="import importlib.metadata\n\n\ndef version():\n"
                       "    return importlib.metadata.version('click')\n")
    assert out["bytes"], "a reach the base commit made is the project's"


def test_a_reach_neither_the_file_nor_the_base_made_is_still_fenced(db, tmp_path):
    root = tmp_path / "wt"
    _fence_repo(root)
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    with pytest.raises(ValueError, match="reaches the process"):
        sb.call("code.write", path="decorators.py",
                text="import subprocess\n\n\ndef version():\n"
                     "    return subprocess.run(['ls'])\n")


_RESTORE = ("import importlib.metadata\n\n\ndef version():\n"
            "    return importlib.metadata.version('click')\n")


def test_the_base_of_a_batch_of_two_commits_is_its_fork_not_head_1(db, tmp_path):
    """Review 1, finding 5: the batch's base is the merge base with the
    project root. HEAD~1 is the batch's own first commit, which lacks the
    reach, so only the fork lets the restore land."""
    import subprocess

    def git(where, *args):
        subprocess.run(["git", "-C", str(where), "-c", "user.name=t",
                        "-c", "user.email=t@t", *args], check=True, capture_output=True)
    proj = tmp_path / "proj"; proj.mkdir()
    git(proj, "init", "-q")
    (proj / "decorators.py").write_text(_RESTORE)
    git(proj, "add", "-A")
    git(proj, "commit", "-q", "-m", "base")
    wt = tmp_path / "wt"
    git(proj, "worktree", "add", "-q", "-b", "batch/b1", str(wt))
    (wt / "decorators.py").write_text("def version():\n    return '8'\n")
    git(wt, "commit", "-q", "-am", "batch 1")
    (wt / "decorators.py").write_text("def version():\n    return '9'\n")
    git(wt, "commit", "-q", "-am", "batch 2")
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('project_root', ?)", (str(proj),))
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(wt),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    out = sb.call("code.write", path="decorators.py", text=_RESTORE)
    assert out["bytes"], "the fork holds the reach, and HEAD~1 does not"


def test_a_base_that_cannot_be_named_leaves_the_working_file_as_baseline(db, tmp_path, monkeypatch):
    """Review 1, finding 3: a database error while naming the base reached
    every fence write. The fence then judges against the working file."""
    import sqlite3
    from rota.roles import api
    root = tmp_path / "wt"
    _fence_repo(root)
    (root / "decorators.py").write_text(_RESTORE)
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()

    def broken(ctx, tree):
        raise sqlite3.OperationalError("database is locked")
    monkeypatch.setattr(api, "_batch_base", broken)
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    out = sb.call("code.write", path="decorators.py", text=_RESTORE + "\n\nX = 1\n")
    assert out["bytes"], "the working file's own reach is the project's"


def test_the_base_text_reads_an_absolute_path_as_the_repository_path(db, tmp_path):
    """Review 1, finding 4: an absolute path gave "" and the restore was
    refused again."""
    from rota.roles import api
    root = tmp_path / "wt"
    _fence_repo(root)
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    assert api._base_text(sb.ctx, root, str(root / "decorators.py")) == _RESTORE
    assert api._base_text(sb.ctx, root, "decorators.py") == _RESTORE
    # Frame 220's lows: a `..` part folds before git reads the spec.
    assert api._base_text(sb.ctx, root, "sub/../decorators.py") == _RESTORE
    assert api._base_text(sb.ctx, root, "../decorators.py") is None


def test_the_base_held_reads_an_absolute_path_as_the_repository_path(db, tmp_path):
    """Frame 220's lows: `_base_held` keeps the base's dropped line when the
    path comes absolute."""
    from rota.roles import api
    root = tmp_path / "wt"
    _fence_repo(root)
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    line = "return importlib.metadata.version('click')"
    entry = {"lines": [["version", line, 1], ["version", "gone = 1", 1]],
             "defs": ["version", "nowhere"], "whole": ["version"]}
    assert api._base_held(sb.ctx, root, str(root / "decorators.py"), entry)
    assert entry["lines"] == [["version", line, 1]], entry
    assert entry["defs"] == ["version"], entry


def test_a_seventh_criterion_on_one_ticket_is_refused(db):
    """clickI night 38 (2026-09-13): twenty-four criteria on one ticket, then
    a signoff page of twenty-five lines. Six is many; the count is a fact."""
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES ('i9','echo json','in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk9','i9','add echo_json next to echo')")
    db.commit()
    from rota.roles import prompts
    sb = build("terminologist", db, mode="criteria", allow=prompts.mode_tools("terminologist", "criteria"))
    texts = ["echo_json accepts an object and prints it",
             "the indent argument defaults to two spaces",
             "nested lists keep their order in the output",
             "a None value prints as the JSON literal null",
             "the output ends with one newline",
             "strings with quotes are escaped as JSON requires"]
    for k, text in enumerate(texts):
        sb.call("criteria.specify", id=f"c9_{k}", ticket_id="tk9", text=text,
                term_refs=[], surface_refs=[])
    with pytest.raises(ValueError, match="six is many"):
        sb.call("criteria.specify", id="c9_6", ticket_id="tk9",
                text="echo_json also serialises datetimes as ISO 8601 strings", term_refs=[], surface_refs=[])


def test_a_staged_respecify_takes_no_second_seat_under_the_cap(db):
    """Frame 329: a respecify stages no `ticket_id`. Its row on file holds
    the seat when the row is live, and a retired row holds none, so a
    rewrite of either moves the count by nothing."""
    from rota.roles import prompts
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES ('i9','echo json','in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk9','i9','add echo_json next to echo')")
    texts = ["echo_json accepts an object and prints it",
             "the indent argument defaults to two spaces",
             "nested lists keep their order in the output",
             "a None value prints as the JSON literal null",
             "the output ends with one newline"]
    for k, text in enumerate(texts):
        db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?, 'tk9', ?)",
                   (f"c9_{k}", text))
    db.execute("INSERT INTO criteria (id, ticket_id, text, retired_by) VALUES "
               "('c9_old', 'tk9', 'echo_json colours its keys', 'r_drop')")
    db.commit()
    allow = prompts.mode_tools("terminologist", "criteria") + ["criteria.respecify"]
    sb = build("terminologist", db, mode="criteria", allow=allow)
    sb.call("criteria.respecify", id="c9_0",
            text="echo_json accepts a dict and prints it as JSON", surface_refs=[])
    sb.call("criteria.respecify", id="c9_old",
            text="echo_json prints keys in the order they were given", surface_refs=[])
    sb.call("criteria.specify", id="c9_5", ticket_id="tk9",
            text="strings with quotes are escaped as JSON requires",
            term_refs=[], surface_refs=[])
    with pytest.raises(ValueError, match="six is many"):
        sb.call("criteria.specify", id="c9_6", ticket_id="tk9",
                text="echo_json also serialises datetimes as ISO 8601 strings",
                term_refs=[], surface_refs=[])


def test_a_span_whose_own_lines_do_not_parse_is_told_which_line(db, tmp_path):
    """clickI night 40 (2026-09-13): the fragment ended with a dangling
    `def echo(` copied from the file to show where it goes, and the refusal
    named the merged file's line six times over."""
    root = tmp_path / "wt"; root.mkdir()
    (root / "m.py").write_text("import json\n\n\ndef echo(\n    message,\n):\n    print(message)\n")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    with pytest.raises(ValueError, match=r"Your text itself does not parse: line 5 of it, counting from 1, is 'def echo\('"):
        sb.call("code.write", path="m.py", start=3, end=3,
                text="def echo_json(o):\n    print(json.dumps(o))\n\n\ndef echo(\n")


def test_the_criterion_under_test_speaks_first_on_print_versus_return(db):
    """clickI night 42 (2026-09-13): the criterion said "printing", a sibling
    on the same ticket said "return behavior", the union said both, and four
    tests asserting on the return value landed and failed."""
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES ('i8','echo json','in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk8','i8','add echo_json next to echo that prints an object as JSON')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) VALUES "
               "('c8a','tk8','echo_json prints the object as JSON with the given indent','[\"echo_json\"]')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) VALUES "
               "('c8b','tk8','the docstring describes the arguments and the return behavior','[\"echo_json\"]')")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b8','i8','running')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b8','tk8')")
    db.commit()
    from rota.roles import prompts
    sb = build("tester", db, batch_id="b8", mode="tests_missing",
               allow=prompts.mode_tools("tester", "tests_missing"))
    sb.call("tests.triage", criterion_id="c8a", verdict="encodable")
    with pytest.raises(ValueError, match="uses what echo_json returns"):
        sb.call("tests.encode", id="tst_8a", criterion_id="c8a", path="tests/test_echo_json.py",
                body="from click.utils import echo_json" + chr(10) + chr(10) + "def test_echo_json_prints():" + chr(10) + "    assert echo_json({'a': 1}, indent=2) == 'x'" + chr(10))

def test_a_surface_on_another_existing_callable_is_refused(db):
    """Night 70 (2026-09-15), click sentence three: the item said give
    version_option a show_python flag; the criteria carried custom_version_option,
    a real companion, as their surface; the Developer's change to version_option
    was refused as a change no criterion names. Both names are in the index."""
    from rota.roles import prompts

    for name in ("version_option", "custom_version_option"):
        db.execute("INSERT INTO code_index (grain, grain_kind, area, fan_in, sym_kind, content_hash) "
                   "VALUES (?, 'symbol', 'src/click', 0, 'function', 'h')", (f"src/click/decorators.py::{name}",))
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i70', 'give version_option a show_python flag that appends the running Python version', "
               "'in_scope', 'approved', 1, 1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk70','i70','give version_option a show_python flag')")
    db.commit()
    sb = build("terminologist", db, mode="normal",
               allow=prompts.mode_tools("terminologist", "criteria"))
    with pytest.raises(ValueError, match="the item names version_option"):
        sb.call("criteria.specify", id="c_70", ticket_id="tk70",
                text="When show_python is True, version_option appends the Python version",
                surface_refs=["src/click/decorators.py::custom_version_option"])
    out = sb.call("criteria.specify", id="c_70", ticket_id="tk70",
                  text="When show_python is True, version_option appends the Python version",
                  surface_refs=["src/click/decorators.py::version_option"])
    assert out["id"] == "c_70"

def test_a_name_the_body_defines_is_not_an_unimported_one(db):
    """Night 81 (2026-09-16): the Tester defined `def cmd(): pass` in the body,
    invoked it, and was refused for using cmd without importing it, twice."""
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    body = ("def cmd():" + chr(10) + "    return 'x'" + chr(10) + chr(10)
            + "def test_x():" + chr(10) + "    assert cmd() == 'x'" + chr(10))
    try:
        sb.call("tests.encode", id="tst_def", criterion_id="c1", path="tests/test_d.py", body=body)
    except ValueError as exc:
        assert "never imports it" not in str(exc), exc


def _lines(*rows):
    return list(rows)


# `confirm` from click 8.5.0's termui.py, lines 288 to 345 in code.source
# numbering, without its docstring. A copy, so a click upgrade does not move
# the lines (frame 95's diff review, 2026-09-30).
_CONFIRM = '''def confirm(
    text: str,
    default: bool | None = False,
    abort: bool = False,
    prompt_suffix: str = ": ",
    show_default: bool = True,
    err: bool = False,
) -> bool:
    prompt = _build_prompt(
        text,
        prompt_suffix,
        show_default,
        "y/n" if default is None else ("Y/n" if default else "y/N"),
    )

    while True:
        try:
            value = _readline_prompt(visible_prompt_func, prompt, err).lower().strip()
        except (KeyboardInterrupt, EOFError):
            raise Abort() from None
        if value in ("y", "yes"):
            rv = True
        elif value in ("n", "no"):
            rv = False
        elif default is not None and value == "":
            rv = default
        else:
            echo(_("Error: invalid input"), err=err)
            continue
        break
    if abort and not rv:
        raise Abort()
    return rv'''


def test_a_def_cut_after_a_raise_in_a_branch_names_what_it_drops():
    """Frame 95: a whole-def text that stops at a `raise` inside an except
    inside a loop drops the lines after it, and the note names them."""
    from rota.roles.api import _tail_drop
    old = _lines("def f(x):",
                 "    while True:",
                 "        try:",
                 "            v = x()",
                 "        except OSError:",
                 "            raise ValueError() from None",
                 "        if v:",
                 "            rv = v",
                 "        break",
                 "    return rv")
    text = chr(10).join(old[:6]) + chr(10)
    note = _tail_drop(old, 0, len(old), text)
    assert note == ("This write drops 4 lines that came after "
                    "`raise ValueError() from None`, from `if v:`.")


def test_a_tail_the_text_moves_into_the_branch_is_not_a_loss():
    """Frame 95: `return rv` moved into the loop's branch is the text's leaf,
    so the old `return rv` below the loop is not a loss."""
    from rota.roles.api import _tail_drop
    old = _lines("def f(x):",
                 "    rv = None",
                 "    for i in x:",
                 "        if i:",
                 "            rv = i",
                 "            break",
                 "    return rv")
    text = chr(10).join(old[:5] + ["            return rv"]) + chr(10)
    assert _tail_drop(old, 0, len(old), text) is None


def test_a_line_above_the_leaf_does_not_hide_a_loss():
    """Frame 95's diff review (2026-09-30): `return x` above the loop is a
    different line from the `return x` the write drops below it."""
    from rota.roles.api import _tail_drop
    old = _lines("def f(x):",
                 "    for i in x:",
                 "        if not i:",
                 "            raise ValueError(i)",
                 "    return x")
    text = chr(10).join(["def f(x):", "    if not x:", "        return x",
                         "    for i in x:", "        if not i:",
                         "            raise ValueError(i)"]) + chr(10)
    assert _tail_drop(old, 0, len(old), text) == (
        "This write drops 1 line that came after `raise ValueError(i)`, from `return x`.")


_TWO_BLOCKS = _lines("def f(value):",
                     "    if value is None:",
                     "        log(value)",
                     "        return 0",
                     "    value = norm(value)",
                     "    if value is None:",
                     "        log(value)",
                     "        return 0")


def test_a_text_that_stops_in_the_first_of_two_like_blocks_pairs_the_first():
    """Frame 95's diff review (2026-09-30): the last old `if value is None:`
    took the pair, and a text that stopped in the first block read nothing.
    The pairs now run in order."""
    from rota.roles.api import _tail_drop
    old = _TWO_BLOCKS + ["    warn(value)", "    return value"]
    text = chr(10).join(old[:2] + ["        raise ValueError(value)"]) + chr(10)
    assert _tail_drop(old, 0, len(old), text) == (
        "This write drops 6 lines that came after `raise ValueError(value)`, "
        "from `value = norm(value)`.")
    old = _TWO_BLOCKS + ["    return value"]
    text = chr(10).join(old[:4]) + chr(10)
    assert _tail_drop(old, 0, len(old), text) == (
        "This write drops 4 lines that came after `return 0`, from `value = norm(value)`.")


def test_a_leaf_with_no_pair_still_counts_the_drops_above_it():
    """Frame 95's diff review (2026-09-30): a whole-file write lost `return y`
    and all of `def c`, and the unpaired `raise` gave no note."""
    from rota.roles.api import _tail_drop
    old = _lines("def b(x):", "    if x:", "        y = 1", "    return y", "", "",
                 "def c():", "    pass")
    text = chr(10).join(["def b(x):", "    if x:", "        raise ValueError(x)"]) + chr(10)
    assert _tail_drop(old, 0, len(old), text) == (
        "This write drops 3 lines that came after `raise ValueError(x)`, from `return y`.")


def test_a_match_case_cut_short_names_the_cases_it_drops():
    """Frame 95's diff review (2026-09-30): `cases` was not a field of the
    walk, so a text that stopped in `case 1:` gave no note."""
    from rota.roles.api import _tail_drop
    old = _lines("def f(v):",
                 "    match v:",
                 "        case 1:",
                 "            return 1",
                 "        case _:",
                 "            r = v",
                 "    log(r)",
                 "    return r")
    text = chr(10).join(old[:4]) + chr(10)
    assert _tail_drop(old, 0, len(old), text) == (
        "This write drops 4 lines that came after `return 1`, from `case _:`.")


def test_night98_s183_confirm_cut_at_raise_abort_drops_13_lines():
    """Night 98 (2026-09-29): s183 sent span 288,345, all of `confirm`, with a
    text that stopped at `raise Abort() from None`. Commit d8d87beb deleted 13
    lines."""
    from rota.roles.api import _tail_drop
    lines = _CONFIRM.splitlines()
    cut = [i for i, x in enumerate(lines) if x.strip() == "raise Abort() from None"][0]
    note = _tail_drop(lines, 0, len(lines), chr(10).join(lines[:cut + 1]) + chr(10))
    assert note == ('This write drops 13 lines that came after `raise Abort() from None`, '
                    'from `if value in ("y", "yes"):`.')


def test_night97_tail_loop_that_ends_at_continue_drops_the_return():
    """Night 97 (2026-09-29): s214 replaced the tail of `confirm` with a loop
    that ends at `continue`, and `if abort and not rv:` to `return rv` went.
    Night 97's span was 340,352 in its own file. The span here runs from
    `while True:` to the end of `confirm`."""
    from rota.roles.api import _tail_drop
    lines = _CONFIRM.splitlines()
    w = [i for i, x in enumerate(lines) if x.strip() == "while True:"][0]
    loop = lines[w:w + 5] + [
        '        if value in ("y", "yes"):', "            rv = True", "            break",
        '        elif value in ("n", "no"):', "            rv = False", "            break",
        '        elif default is not None and value == "":', "            rv = default",
        "            break",
        "        else:", '            echo(_("Error: invalid input"), err=err)',
        "            continue"]
    # The loop's own `break` moved into each branch, deeper, so it is kept
    # (frame 95 pass 3, 2026-09-30).
    note = _tail_drop(lines, w, len(lines), chr(10).join(loop) + chr(10))
    assert note == ("This write drops 3 lines that came after `continue`, "
                    "from `if abort and not rv:`.")


def test_a_span_write_that_stops_short_lands_and_says_what_it_drops(db, tmp_path):
    """Frame 95: the write lands, and the result carries the note under
    `dropped`."""
    root = tmp_path / "wt"; root.mkdir()
    old = _lines("def f(x):", "    for i in x:", "        if not i:",
                 "            raise ValueError(i)", "        i.go()", "    return x")
    (root / "m.py").write_text(chr(10).join(old) + chr(10))
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    out = sb.call("code.write", path="m.py", start=0, end=6,
                  text=chr(10).join(old[:4]) + chr(10))
    assert out["dropped"] == ("This write drops 2 lines that came after "
                              "`raise ValueError(i)`, from `i.go()`.")
    assert "return x" not in (root / "m.py").read_text()


def test_an_insert_before_the_pair_takes_the_first_old_statement_of_its_type():
    """Frame 95's third review (2026-09-30): after an insert, the text's index
    paired `if y:` and read 1 line from `return 1`. The truth is 3 from `if y:`."""
    from rota.roles.api import _tail_drop
    old = _lines("def f(x, y):", "    a = 0", "    if x:", "        raise E",
                 "    if y:", "        pass", "    return 1")
    text = chr(10).join(["def f(x, y):", "    n0 = 0", "    a = 1",
                         "    if x is not None:", "        raise E"]) + chr(10)
    assert _tail_drop(old, 0, len(old), text) == (
        "This write drops 3 lines that came after `raise E`, from `if y:`.")


def test_an_if_that_becomes_an_elif_is_moved_not_dropped():
    """Frame 95's third review (2026-09-30): a second `if` turned into an
    `elif` read 3 lines from `if i < 0:`, and only `return x` went."""
    from rota.roles.api import _tail_drop
    old = _lines("def f(i, x):", "    if i > 0:", "        raise ValueError(i)",
                 "    if i < 0:", "        x = -i", "    return x")
    text = chr(10).join(["def f(i, x):", "    if i > 0:", "        raise ValueError(i)",
                         "    elif i < 0:", "        x = -i",
                         "        raise ValueError(x)"]) + chr(10)
    assert _tail_drop(old, 0, len(old), text) == (
        "This write drops 1 line that came after `raise ValueError(x)`, from `return x`.")


def test_a_whole_write_over_a_file_that_does_not_decode_lands_with_no_note(db, tmp_path):
    """Frame 95's third review (2026-09-30): the whole-file read of the old
    file ran outside the note's guard, so a latin-1 byte refused the write."""
    root = tmp_path / "wt"; root.mkdir()
    (root / "m.py").write_bytes(b"# caf" + bytes([0xE9]) + b"\ndef f():\n    return 1\n")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    out = sb.call("code.write", path="m.py", text="def f():\n    return 2\n")
    assert "dropped" not in out
    assert "return 2" in (root / "m.py").read_text()


def _committed_close(db, tmp_path):
    """A worktree whose one commit holds script.py, and a red run of tst1 on
    that commit, the shape night 97 left behind."""
    import subprocess
    root = tmp_path / "wt"; root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    body = chr(10).join(["def close_account(x):", "    if x:", "        pass", ""])
    (root / "script.py").write_bytes(body.encode("utf-8"))
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t",
                    "commit", "-q", "-m", "a"], check=True)
    sha = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                         capture_output=True, text=True, check=True).stdout.strip()
    said = chr(10).join(["    def test_close():",
                         ">       assert close_account('a1') is not None",
                         "E       assert None is not None",
                         "E        +  where None = close_account('a1')", "",
                         "test_close.py:2: AssertionError", "1 failed in 0.01s"])
    db.execute("UPDATE batches SET worktree = ?, head_commit = ? WHERE id = 'b1'",
               (str(root), sha))
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, "
               "attempt, output) VALUES ('r1','b1','tst1',?,'fail',5,?)", (sha, said))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    return root, body, sha, sb


def test_a_write_the_file_already_holds_says_so_and_quotes_the_red_assertion(db, tmp_path):
    """Frame 93. Night 97 (2026-09-29): s215 and s216 sent the landed text of
    `confirm` again, read `"written, not committed": []`, and the test failed
    on one commit from attempt 5 to 7."""
    import os
    root, body, sha, sb = _committed_close(db, tmp_path)
    before = os.stat(root / "script.py").st_mtime_ns
    out = sb.call("code.write", path="script.py", text=body)
    assert out["unchanged"] == (
        f"script.py already holds this text, so this write changed nothing. "
        f"Commit {sha[:8]} holds it. tst1 fails at {sha[:8]} on "
        f"`assert close_account('a1') is not None`, and pytest said "
        f"`assert None is not None`. Read what this assertion needs before the next write.")
    assert out["written, not committed"] == []
    assert os.stat(root / "script.py").st_mtime_ns == before
    assert (root / "script.py").read_bytes() == body.encode("utf-8")
    # The same fields a landed write returns (frame 93's review, 2026-09-30).
    assert out["lands with"] == "code.commit"
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES "
               "('tst2','b1','c1','test_bill.py','import billing' || char(10) || "
               "'def test_b():' || char(10) || '    assert billing')")
    db.commit()
    out = sb.call("code.write", path="script.py", text=body)
    assert out["note"] == ("the batch's tests import billing and no such module "
                           "exists in the worktree yet")


def test_an_unchanged_write_names_the_first_red_test_of_the_latest_attempt(db, tmp_path):
    """Frame 93's review (2026-09-30): with two red tests, `rowid DESC` named
    the test the harness ran last. The first by rowid is named, and the
    sentence counts the rest."""
    root, body, sha, sb = _committed_close(db, tmp_path)
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES "
               "('tst2','b1','c1','test_two.py','assert 0')")
    said = chr(10).join([">       assert 0", "E       assert 0", "", "test_two.py:1: AssertionError"])
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, "
               "attempt, output) VALUES ('r2','b1','tst2',?,'fail',5,?)", (sha, said))
    db.commit()
    out = sb.call("code.write", path="script.py", text=body)
    assert out["unchanged"] == (
        f"script.py already holds this text, so this write changed nothing. "
        f"Commit {sha[:8]} holds it. tst1 fails at {sha[:8]} on "
        f"`assert close_account('a1') is not None`, and pytest said "
        f"`assert None is not None`, and 1 more fail; tests.load lists them. "
        f"Read what this assertion needs before the next write.")


def test_a_write_that_changes_one_line_carries_no_unchanged_sentence(db, tmp_path):
    """Frame 93: a text that differs by one line is a write, and lands."""
    root, body, sha, sb = _committed_close(db, tmp_path)
    text = body.replace("        pass", "        return x")
    out = sb.call("code.write", path="script.py", text=text)
    assert "unchanged" not in out
    assert "return x" in (root / "script.py").read_text()


# `src/ui.py` from ACT-DV-edit-inside-the-function, tests/rota/cases/l1_acts.yaml.
_UI = '''import sys

visible_prompt_func = input


def _readline_prompt(func, text):
    return func(text)


def confirm(text, default=None):
    while True:
        try:
            value = _readline_prompt(visible_prompt_func, text).lower().strip()
        except (KeyboardInterrupt, EOFError):
            raise SystemExit(1)
        if value in ("y", "yes"):
            return True
        if value in ("n", "no"):
            return False
        if default is not None and value == "":
            return default


def style(text, fg=None):
    return text if fg is None else f"<{fg}>{text}</{fg}>"


def echo(message):
    sys.stdout.write(str(message) + chr(10))
'''


def _ui_worktree(db, tmp_path, name, body):
    root = tmp_path / "wt"; (root / "src").mkdir(parents=True)
    (root / "src" / name).write_bytes(body.encode("utf-8"))
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    return root, build("developer", db, batch_id="b1", mode="tests_failing",
                       allow=prompts.mode_tools("developer", "tests_failing"))


def test_a_whole_write_of_one_def_that_uses_the_dropped_helpers_is_refused(db, tmp_path):
    """ACT-DV-edit-inside-the-function (2026-09-30): every run wrote `ui.py`
    whole with `confirm` alone. `confirm` calls `_readline_prompt`, which the
    write dropped, and no door refused, because nothing imported it."""
    root, sb = _ui_worktree(db, tmp_path, "ui.py", _UI)
    lines = _UI.splitlines()
    new = chr(10).join([lines[9].replace("default=None", "default=None, default_on_eof=False")]
                       + lines[10:21]) + chr(10)
    with pytest.raises(ValueError, match=r"drops .*_readline_prompt.* your text still uses "
                                         r"them\. To change confirm alone, write only "
                                         r"confirm with start=9, end=21"):
        sb.call("code.write", path="src/ui.py", text=chr(10) * 2 + new)
    out = sb.call("code.write", path="src/ui.py", text=new, start=9, end=21)
    assert "dropped" not in out
    held = (root / "src" / "ui.py").read_text()
    assert "default_on_eof=False" in held and "def echo" in held and "import sys" in held


def test_a_whole_write_that_drops_an_unused_helper_names_the_lines_and_no_span(db, tmp_path):
    """Frame 95 pass 5: a whole-file write that keeps `keep` and drops a helper
    nothing uses lands, and the sentence counts the dropped lines. Frame 283
    pass 6: the changed `return x` inside the kept `keep` keeps one Return
    under `keep`, so the whole-file note reads it as a rewrite."""
    old = "def keep(x):\n    return x\n\n\ndef helper():\n    return 2\n"
    root, sb = _ui_worktree(db, tmp_path, "m.py", old)
    out = sb.call("code.write", path="src/m.py", text="def keep(x):\n    return x + 1\n")
    assert out["dropped"] == ("This write drops 2 lines of the old file, from "
                              "`def helper():`; write the whole file again with "
                              "those lines kept.")
    assert "start=" not in out["dropped"]


def test_a_refusal_with_two_kept_defs_offers_the_spans_last_first(db, tmp_path):
    """Frame 95 pass 6: a span write moves every line below it, so the offer
    runs bottom-up and says so."""
    old = """def a(x):
    return helper(x)


def helper(x):
    return x


def b(x):
    return helper(x) + 1
"""
    root, sb = _ui_worktree(db, tmp_path, "m.py", old)
    new = """def a(x):
    return helper(x) * 2


def b(x):
    return helper(x) + 2
"""
    with pytest.raises(ValueError) as e:
        sb.call("code.write", path="src/m.py", text=new)
    msg = str(e.value)
    assert ("write only b with start=8, end=10, and then a with start=0, end=2 "
            "(write them in this order, last first): each span") in msg


def test_a_star_import_silences_the_used_check(db, tmp_path):
    """Frame 95 pass 6: a star import can bind any name, so a dropped name
    the new text uses is not a sure break."""
    old = """def helper(x):
    return x


def keep(x):
    return helper(x)
"""
    root, sb = _ui_worktree(db, tmp_path, "m.py", old)
    sb.call("code.write", path="src/m.py",
            text="from os.path import *" + chr(10) * 3
                 + "def keep(x):" + chr(10) + "    return helper(x) + 1" + chr(10))
    assert "helper(x) + 1" in (root / "src" / "m.py").read_text()


def test_a_match_capture_binds_the_name_it_uses(db, tmp_path):
    """Frame 95 pass 6: a match capture, a star capture and a mapping rest
    bind names, so their use is not a use of the old top-level name."""
    old = """value = 1
rest = 2
tail = 3


def keep(v):
    return v
"""
    root, sb = _ui_worktree(db, tmp_path, "m.py", old)
    new = """def keep(v):
    match v:
        case {"k": value, **rest}:
            return value, rest
        case [_, *tail]:
            return tail
    return v
"""
    sb.call("code.write", path="src/m.py", text=new)
    assert "match v:" in (root / "src" / "m.py").read_text()


def test_a_dropped_shadow_of_a_builtin_is_not_refused(db, tmp_path):
    """Frame 95 pass 6: the builtin still resolves after the file's own
    shadow goes, so the file is not broken."""
    old = """def input(p):
    return p


def ask():
    return input("?")
"""
    root, sb = _ui_worktree(db, tmp_path, "m.py", old)
    sb.call("code.write", path="src/m.py", text="def ask():" + chr(10) + "    return input('x')" + chr(10))
    assert "input('x')" in (root / "src" / "m.py").read_text()


# Frame 136: a span write that removes the file's import lines. Click night
# 120 (2026-10-05): s227 meant to add `import sys` and sent start=0, end=5,
# which replaced the first five lines of decorators.py; 43 of 43 tests went
# to error at import. The header below is a trimmed copy of that file.
_HEAD = (
    "from __future__ import annotations\n"
    "\n"
    "import inspect\n"
    "import typing as t\n"
    "from functools import update_wrapper\n"
    "from gettext import gettext as _\n"
    "\n"
    'R = t.TypeVar("R")\n'
    "\n"
    "\n"
    "def pass_context(f):\n"
    "    return update_wrapper(f, f)\n"
    "\n"
    "\n"
    "def version_option(show_python=False):\n"
    "    sig = inspect.signature(version_option)\n"
    "    if show_python:\n"
    '        return _(f"Python {sys.version_info.major}")\n'
    "    return str(sig)\n"
)
_HEAD_IMPORTS = [x for x in _HEAD.splitlines() if x.startswith(("import ", "from "))]


def _right(tmp_path, *extra):
    """The file after a named call: every old import line, the new lines,
    and a module that compiles."""
    src = (tmp_path / "wt" / "m.py").read_text()
    have = src.splitlines()
    for line in _HEAD_IMPORTS + list(extra):
        assert line in have, line
    # Compile is not import (the review of 08caa8d, point 1): run the
    # module's top level too.
    exec(compile(src, "m.py", "exec", dont_inherit=True), {"__name__": "m"})
    return src


def test_a_span_that_removes_used_imports_is_refused_with_the_insert(db, tmp_path):
    """s227's call: the refusal quotes the removed lines and names the
    insert below the `from __future__` import, and that insert lands."""
    msg = _span_refusal(db, tmp_path, _HEAD, 0, 5, "import sys\n")
    assert msg == (
        "start=0, end=5 removes 'from __future__ import annotations', 'import inspect', "
        "'import typing as t' and 'from functools import update_wrapper', and the rest "
        "of m.py still uses inspect, t and update_wrapper. To add your text and keep "
        "every line, send start=1, end=1.")
    assert (tmp_path / "wt" / "m.py").read_text() == _HEAD
    assert _write(db, tmp_path, 1, 1, "import sys\n")["bytes"]
    src = _right(tmp_path, "import sys")
    assert src.startswith("from __future__ import annotations\nimport sys\n")


def test_a_span_whose_text_binds_the_names_again_lands(db, tmp_path):
    """A replace of the header that keeps every name is the seat's to make."""
    root = tmp_path / "wt"; root.mkdir()
    (root / "m.py").write_text(_HEAD)
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    text = ("from __future__ import annotations\n\nimport inspect\nimport sys\n"
            "import typing as t\nfrom functools import update_wrapper\n")
    assert _write(db, tmp_path, 0, 5, text)["bytes"]
    _right(tmp_path, "import sys")


_NO_INSPECT = ("from __future__ import annotations\n\nimport typing as t\n"
               "from functools import update_wrapper\nfrom gettext import gettext as _\n\n"
               'R = t.TypeVar("R")\n')


def test_a_replace_that_drops_a_used_import_is_told_to_carry_it(db, tmp_path):
    """A2: the text replaces the header and leaves out `import inspect`."""
    msg = _span_refusal(db, tmp_path, _HEAD, 0, 8, _NO_INSPECT)
    assert msg == (
        "start=0, end=8 removes 'import inspect', and the rest of m.py still uses "
        "inspect. To keep it, put that line at the top of your text, below any "
        "`from __future__` line, and send start=0, end=8 again.")
    text = _NO_INSPECT.replace("annotations\n", "annotations\nimport inspect\n", 1)
    assert _write(db, tmp_path, 0, 8, text)["bytes"]
    _right(tmp_path)


def test_a_future_import_below_another_line_is_told_to_go_first(db, tmp_path):
    """D, s227 turn 10: the whole header with `import sys` above
    `from __future__`. The bare compile refusal named no step, and the seat
    gave up on a repair that was one line away."""
    text = "import sys\n" + _HEAD.split("\n\n\ndef pass_context")[0] + "\n"
    msg = _span_refusal(db, tmp_path, _HEAD, 0, 8, text)
    assert msg == (
        "Python takes 'from __future__ import annotations' only above every other "
        "statement, and your text puts 'import sys' above it. Send the same call with "
        "that line first in text.")
    moved = text.replace("import sys\n", "", 1).replace(
        "annotations\n", "annotations\nimport sys\n", 1)
    assert _write(db, tmp_path, 0, 8, moved)["bytes"]
    _right(tmp_path, "import sys")


def test_a_removed_future_import_alone_is_refused(db, tmp_path):
    """The `from __future__` line binds no name the file loads, and the
    span still removes it (frame 136: 0 of 84 harmless landed writes did)."""
    msg = _span_refusal(db, tmp_path, _HEAD, 0, 1, "import sys\n")
    assert msg.startswith("start=0, end=1 removes 'from __future__ import annotations', "
                          "and the rest of m.py runs under that `from __future__` import.")
    assert "send start=1, end=1." in msg
    assert _write(db, tmp_path, 1, 1, "import sys\n")["bytes"]
    _right(tmp_path, "import sys")


def test_a_star_import_or_a_builtin_keeps_the_span_door_silent(db, tmp_path):
    """A star import can bind any name, and a builtin still resolves after
    the file's own shadow goes (frame 95)."""
    root = tmp_path / "wt"; root.mkdir()
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    (root / "m.py").write_text("import os\nimport inspect\n\n\ndef f():\n    return inspect, os\n")
    assert _write(db, tmp_path, 1, 2, "from inspect import *\n")["bytes"]
    (root / "m.py").write_text("len = None\nimport os\n\n\ndef f():\n    return len(os.sep)\n")
    assert _write(db, tmp_path, 0, 1, "import sys\n")["bytes"]


def test_a_span_refusal_names_no_call_the_doors_refuse(db, tmp_path, monkeypatch):
    """Frame 135's rule: a call is named only where the door admits it."""
    from rota.roles import api
    monkeypatch.setattr(api, "_admits", lambda *a, **k: False)
    msg = _span_refusal(db, tmp_path, _HEAD, 0, 5, "import sys\n")
    assert msg.startswith("start=0, end=5 removes 'from __future__ import annotations'")
    assert "send" not in msg
    (tmp_path / "wt" / "m.py").write_text(_HEAD)
    with pytest.raises(ValueError) as err:
        _write(db, tmp_path, 0, 8, _NO_INSPECT)
    assert "still uses inspect." in str(err.value) and "send" not in str(err.value)
    text = "import sys\n" + _HEAD.split("\n\n\ndef pass_context")[0] + "\n"
    with pytest.raises(ValueError) as err:
        _write(db, tmp_path, 0, 8, text)
    assert str(err.value).endswith("above it.")


def test_a_dry_run_leaves_the_context_and_the_disk_as_they_were(db, tmp_path, monkeypatch):
    """Ruling 1 of frame 136: `_admits` changes nothing, passes or fails,
    and a refusal starts exactly one dry run, which starts none."""
    import copy
    from rota.roles import api, prompts
    root = tmp_path / "wt"; root.mkdir()
    (root / "m.py").write_text(_HEAD)
    (root / "added.py").write_text("x = 1\n")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    ctx = sb.ctx

    def state():
        fields = {k: copy.deepcopy(v) for k, v in vars(ctx).items() if k != "conn"}
        files = {p.relative_to(root).as_posix(): p.read_bytes()
                 for p in root.rglob("*") if p.is_file()}
        return fields, files, ctx.conn.total_changes

    before = state()
    assert api._admits(ctx, "m.py", "import sys\n", 1, 1)
    assert api._admits(ctx, "added.py", "", 0, -1)
    assert not api._admits(ctx, "m.py", "import sys\n", 0, 5)
    assert state() == before
    real, dries = api._code_write, []

    def spy(*a, **k):
        dries.append(k["dry"])
        return real(*a, **k)

    monkeypatch.setattr(api, "_code_write", spy)
    with pytest.raises(ValueError, match="send start=1, end=1"):
        sb.call("code.write", path="m.py", start=0, end=5, text="import sys\n")
    assert dries == [False, True]
    after = state()
    # The sandbox records the real call's refusal, once, and the call that
    # the refusal names (frame 144). The dry run adds none.
    changed = sorted(k for k in before[0] if before[0][k] != after[0][k])
    assert changed == ["offers", "refusals"], changed
    assert [o.op for o in after[0]["offers"]] == ["code.write"]
    assert len(after[0]["refusals"]) == len(before[0]["refusals"] or []) + 1
    assert after[1:] == before[1:]


# The review of 08caa8d (frame 136, pass 2). Each test is the reviewer's case.

def test_a_replace_that_removes_an_assignment_gets_the_fact_and_no_call(db, tmp_path):
    """Point 1: A2 put `logger = logging.getLogger(__name__)` above
    `import logging`. It compiled, landed, and failed at import. Only an
    import goes back by A2, so a removed assignment gets the fact alone."""
    src = ("import logging\nimport os\nlogger = logging.getLogger(__name__)\n\n\n"
           "def f():\n    logger.info(os.sep)\n")
    msg = _span_refusal(db, tmp_path, src, 0, 3, "import logging\nimport os\nimport sys\n")
    assert msg == ("start=0, end=3 removes 'logger = logging.getLogger(__name__)', "
                   "and the rest of m.py still uses logger.")


def test_the_real_header_shape_with_a_removed_assignment_names_no_call(db, tmp_path):
    """Point 1 on decorators.py: `R = t.TypeVar("R")` is removed with the
    imports it needs, and the step would have put it above them."""
    src = _HEAD + "\n\ndef g() -> R:\n    return R\n"
    msg = _span_refusal(db, tmp_path, src, 2, 8,
                        "import inspect\nimport sys\nimport typing as t\n")
    assert msg == ("start=2, end=8 removes 'from functools import update_wrapper', "
                   "'from gettext import gettext as _' and 'R = t.TypeVar(\"R\")', and the "
                   "rest of m.py still uses R, _ and update_wrapper.")


def test_a_removed_decorated_class_is_quoted_with_its_decorator(db, tmp_path):
    """Point 2: the quote of a decorated class starts at its decorator."""
    src = ("import functools\nfrom dataclasses import dataclass\n\n\n@dataclass\n"
           "class P:\n    x: int = 1\n\n\ndef f():\n    return P(x=2), functools\n")
    msg = _span_refusal(db, tmp_path, src, 0, 7,
                        "import functools\nfrom dataclasses import dataclass\nimport sys\n")
    assert msg == ("start=0, end=7 removes '@dataclass\nclass P:\n    x: int = 1', and "
                   "the rest of m.py still uses P.")


def test_a_blank_text_over_a_used_import_gets_the_fact_and_no_call(db, tmp_path):
    """Point 3: a blank text is a deletion, and an insert of it adds nothing."""
    msg = _span_refusal(db, tmp_path, _HEAD, 2, 3, "")
    assert msg == "start=2, end=3 removes 'import inspect', and the rest of m.py still uses inspect."


def test_the_insert_goes_below_a_shebang_and_a_coding_comment(db, tmp_path):
    """Point 4: with no docstring and no `__future__` line, the insert sat
    at line 0, above `#!` and the coding comment."""
    src = ("#!/usr/bin/env python\n# -*- coding: utf-8 -*-\nimport os\nimport sys\n\n\n"
           "def f():\n    return os.sep, sys.argv\n")
    msg = _span_refusal(db, tmp_path, src, 0, 4, "import re\n")
    assert msg.endswith("To add your text and keep every line, send start=2, end=2.")
    assert _write(db, tmp_path, 2, 2, "import re\n")["bytes"]
    new = (tmp_path / "wt" / "m.py").read_text()
    assert new.startswith("#!/usr/bin/env python\n# -*- coding: utf-8 -*-\nimport re\nimport os\n")
    exec(compile(new, "m.py", "exec", dont_inherit=True), {"__name__": "m"})


def test_a_future_line_in_a_mid_file_insert_keeps_the_compile_refusal(db, tmp_path):
    """Point 5: below the file's first ordinary statement, moving a line
    inside the text cannot help, so D does not fire."""
    msg = _span_refusal(db, tmp_path, _HEAD, 10, 10,
                        "import sys\nfrom __future__ import annotations\n")
    assert msg.startswith("m.py is not valid Python (from __future__ imports must occur")
    assert "send" not in msg.lower()


def test_a_crash_in_a_dry_run_names_no_call_and_is_logged(db, tmp_path, monkeypatch, caplog):
    """Point 7: only a door's refusal means no. Any other exception leaves
    the call unnamed and leaves a trace in the log."""
    import logging
    from rota.roles import api
    real = api._code_write

    def boom(*a, **k):
        if k.get("dry"):
            raise RuntimeError("a door crashed")
        return real(*a, **k)

    monkeypatch.setattr(api, "_code_write", boom)
    with caplog.at_level(logging.ERROR, logger="rota.roles.api"):
        msg = _span_refusal(db, tmp_path, _HEAD, 0, 5, "import sys\n")
    assert "send" not in msg
    assert "code.write dry run crashed on m.py start=1 end=1" in caplog.text
    assert "a door crashed" in caplog.text


# Frame 213, pass 1, fix 5: a challenge over a red test quotes the failing
# line. Night 142, walk 1: the Architect's challenge m83 quoted the
# `expected` line of inh_echo_04 and left out the `.strip()` line, and the
# Vision Keeper s185 then wrote a false decision from it. The rows are
# rebuilt from `plans/night142-walk1-read.md`, section 1.
N142_CRIT = ("The callable `echo_json` serialises the object with the standard "
             "library `json` module.")
N142_LINES = [
    "import io",
    "import json as stdlib_json",
    "from click.utils import echo_json",
    "",
    "def test_echo_json_uses_stdlib():",
    "    obj = {\"a\": 1}",
    "    captured = io.StringIO()",
    "    echo_json(obj, file=captured)",
    "    expected = stdlib_json.dumps(obj, separators=(\",\", \":\")) + \"\\n\"",
    "    output = captured.getvalue().strip()",
    "    assert output == expected",
]
N142_TEST = "\n".join(N142_LINES) + "\n"
# The run of attempt 12 at 1cda5cb7, in pytest's own shape.
N142_RUN = ("F    [100%]\n=== FAILURES ===\n___ test_echo_json_uses_stdlib ___\n\n"
            "    def test_echo_json_uses_stdlib():\n"
            "        obj = {\"a\": 1}\n"
            ">       assert output == expected\n"
            "E       AssertionError: assert '{\"a\":1}' == '{\"a\":1}\\n'\n\n"
            "=== short test summary info ===\n"
            "FAILED tests/test_utils/test_echo_json_uses_stdlib.py::"
            "test_echo_json_uses_stdlib - AssertionError\n1 failed in 0.05s\n")
# m83's quote: a line of the test that asserts nothing.
N142_QUOTE = N142_LINES[8].strip()
N142_REFS = ["echo_json_uses_stdlib", "inh_echo_04"]


def _n142(db):
    _night_rows(db, "bg_142", "tk_142", [(
        "echo_json_uses_stdlib", N142_CRIT, "inh_echo_04",
        "tests/test_utils/test_echo_json_uses_stdlib.py", N142_TEST, 4)])
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, "
               "output, attempt) VALUES ('tr_142', 'bg_142', 'inh_echo_04', "
               "'1cda5cb7', 'fail', ?, 12)", (N142_RUN,))
    db.commit()


def test_a_challenge_to_the_tester_over_a_red_test_quotes_the_failing_line(db):
    """The Developer's channel holds the same door: the test side of the
    quote is the line the run names."""
    _n142(db)
    sb = _developer(db, "bg_142")
    with pytest.raises(ValueError, match="assert output == expected"):
        sb.call("msg.challenge_tester", reason=REASON, refs=N142_REFS,
                quotes=[N142_CRIT, N142_QUOTE])
    out = sb.call("msg.challenge_tester", reason=REASON, refs=N142_REFS,
                  quotes=[N142_CRIT, "assert output == expected"])
    assert out["verb"] == "challenge"


def test_the_exhaustion_challenge_over_a_red_test_quotes_the_failing_line(db):
    """Night 142, m83: the Architect's exhausted challenge quoted the
    `expected` line, and the door took it.

    Frame 333: each row of refs has a quote, so the criterion is quoted
    too. Each quote is a span of a row of refs, so the run's `E` line is
    no quote of the test."""
    from rota.roles import prompts

    _n142(db)
    sb = build("architect", db, batch_id="bg_142", mode="exhausted",
               allow=prompts.mode_tools("architect", "exhausted"))
    with pytest.raises(ValueError, match="assert output == expected"):
        sb.call("msg.challenge_vision_keeper", refs=N142_REFS,
                quotes=[N142_CRIT, N142_QUOTE])
    with pytest.raises(ValueError, match="not a span of the live text"):
        sb.call("msg.challenge_vision_keeper", refs=N142_REFS,
                quotes=[N142_CRIT,
                        "AssertionError: assert '{\"a\":1}' == '{\"a\":1}\\n'"])
    out = sb.call("msg.challenge_vision_keeper", refs=N142_REFS,
                  quotes=[N142_CRIT, "assert output == expected"])
    assert out["verb"] == "challenge"


def test_the_quote_door_names_the_runs_marked_line_when_it_does_not_assert(db):
    """The review of f252df24, finding 2: the run's `>` line was no assert,
    and the refusal named the body's first assert as the failing line."""
    from rota.roles import prompts

    _n142(db)
    db.execute("UPDATE test_runs SET output = ? WHERE id = 'tr_142'", (
        N142_RUN.replace(">       assert output == expected",
                         ">       output = captured.getvalue().strip()"),))
    db.commit()
    sb = build("architect", db, batch_id="bg_142", mode="exhausted",
               allow=prompts.mode_tools("architect", "exhausted"))
    with pytest.raises(ValueError) as refused:
        sb.call("msg.challenge_vision_keeper", refs=N142_REFS,
                quotes=[N142_CRIT, N142_QUOTE])
    assert "`output = captured.getvalue().strip()`" in str(refused.value)
    assert "`assert output == expected`" not in str(refused.value)


def test_the_quote_door_skips_a_marked_line_of_library_code(db):
    """The review of 126b8c4e, finding 5: on nights 143 to 145 the first `>`
    line was often click's code, and the refusal named a click line. The
    door names the first `>` line that is in the test's body."""
    from rota.roles import prompts

    _n142(db)
    db.execute("UPDATE test_runs SET output = ? WHERE id = 'tr_142'", (
        N142_RUN.replace(
            ">       assert output == expected",
            ">       prog_name = ctx.find_root().info_name\n"
            "E       AttributeError: 'NoneType' object has no attribute 'info_name'\n\n"
            "src/click/core.py:1012: AttributeError\n"
            ">       output = captured.getvalue().strip()"),))
    db.commit()
    sb = build("architect", db, batch_id="bg_142", mode="exhausted",
               allow=prompts.mode_tools("architect", "exhausted"))
    with pytest.raises(ValueError) as refused:
        sb.call("msg.challenge_vision_keeper", refs=N142_REFS,
                quotes=[N142_CRIT, N142_QUOTE])
    assert "`output = captured.getvalue().strip()`" in str(refused.value)
    assert "prog_name = ctx.find_root().info_name" not in str(refused.value)


# Frame 173: the span door's offer and the `dropped` note read the seat's
# text. The fixtures are the files the seats wrote to, from clickI.
_FIXTURES = __import__("pathlib").Path(__file__).parent / "fixtures"


def _night_file(db, tmp_path, rel, fixture):
    root = tmp_path / "wt"
    (root / rel).parent.mkdir(parents=True)
    (root / rel).write_bytes((_FIXTURES / fixture).read_bytes())
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    return sb, root / rel


S214_TEXT = ("\n        except (KeyboardInterrupt, EOFError):\n"
             "            if default_on_eof:\n                return default\n"
             "            raise Abort() from None\n")


def test_s214s_end_offer_names_the_branch_the_offered_span_removes(db, tmp_path):
    """Night 127 (2026-10-07): s214 turn 2 sent only an except clause for
    lines 342 to the end. The door offered end=352, the seat sent it, and the
    y/n branch of confirm() went with no note."""
    sb, target = _night_file(db, tmp_path, "src/click/termui.py",
                             "night127_termui_6330805a.txt")
    with pytest.raises(ValueError) as err:
        sb.call("code.write", path="src/click/termui.py", start=342, end=-1,
                text=S214_TEXT)
    msg = str(err.value)
    assert "To stop where while ends send end=352." in msg
    assert ("A write to start=342, end=352 removes "
            "`if value in (\"y\", \"yes\"):` at line 342, `break` at line 351") in msg
    out = sb.call("code.write", path="src/click/termui.py", start=342, end=352,
                  text=S214_TEXT)
    # Pass 1b: the lost `break` makes confirm() loop on a y or n answer.
    assert ("`if value in (\"y\", \"yes\"):` at line 342, `break` at line 351"
            in out["dropped"])
    assert "if value in" not in target.read_text()


S386_TEXT = (
    "from .core import Click\nimport sys\n\ndef version_option(show_python=False):\n"
    "    def decorator(f):\n        def wrapper(*args, **kwargs):\n"
    "            ctx = kwargs.get('ctx')\n            if ctx and show_python:\n"
    "                version_msg = f\"Python {sys.version_info.major}."
    "{sys.version_info.minor}.{sys.version_info.micro}\"\n"
    "                return f\"{version_msg}\\n{f(*args, **kwargs)}\"\n"
    "            return f(*args, **kwargs)\n        wrapper.__name__ = f.__name__\n"
    "        return wrapper\n    return decorator\n\n@click.command()\n"
    "@version_option(show_python=True)\ndef cli():\n    return \"Hello World\"\n\n"
    "if __name__ == '__main__':\n    cli()\n")


def test_s386s_span_over_version_option_names_the_body_it_removes(db, tmp_path):
    """Night 145 (2026-10-13): s386 wrote lines 421 to 568, the span the
    full-file door offered, and a 14-line wrapper replaced the whole body of
    version_option with no note. 37 of 37 tests went red."""
    sb, _ = _night_file(db, tmp_path, "src/click/decorators.py",
                        "night145_decorators_9375672e.txt")
    out = sb.call("code.write", path="src/click/decorators.py", start=421,
                  end=568, text=S386_TEXT)
    note = out["dropped"]
    # Frame 283, W-D: the text drops six parameters of the signature, and
    # the note door counts each one as a statement. 10 body statements and
    # 6 parameters make 16.
    assert note.startswith("This write removes or rewrites 16 statements")
    assert "`version: str | None = None,` at line 422" in note
    assert "`if message is None:` at line 487" in note
    # The review of 319c7f19, P3: eight are named, and the rest are counted.
    # Pass 1d: the `return` the night broke on is named first, then seven
    # by line, so the lines 565 and 566 are counted.
    assert note.endswith(
        "`if message is None:` at line 487, "
        "`return option(*param_decls, **kwargs)` at line 567 and 8 more.")
    assert "at line 565" not in note and "at line 566" not in note


def test_a_nested_assignment_in_the_text_does_not_hold_a_removed_one(db, tmp_path):
    """The review of 319c7f19, P2: `rv = 0` inside a new nested def hid the
    removed `rv = load()` at the span's own level."""
    root = tmp_path / "wt"; root.mkdir()
    old = _lines("def f():", "    rv = load()", "    check(rv)")
    (root / "m.py").write_text(chr(10).join(old) + chr(10))
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    text = _lines("    def inner():", "        rv = 0", "    check(rv)")
    out = sb.call("code.write", path="m.py", start=1, end=3,
                  text=chr(10).join(text) + chr(10))
    assert out["dropped"] == ("This write removes or rewrites 1 statement that your text "
                              "does not hold: `rv = load()` at line 1.")


S552_TEXT = ("    if not param_decls:\n        param_decls = (\"--version\",)\n"
             "    elif show_python and \"--show-python\" not in param_decls:\n"
             "        param_decls += (\"--show-python\",)")


def test_s552s_span_names_the_return_and_the_setdefault_lines(db, tmp_path):
    """Night 144 (2026-10-13): s552 wrote lines 554 to 564 and removed four
    kwargs.setdefault lines, the callback binding and the return of
    version_option at 4df3ef63, with no note."""
    sb, _ = _night_file(db, tmp_path, "src/click/decorators.py",
                        "night144_decorators_f484f63d.txt")
    out = sb.call("code.write", path="src/click/decorators.py", start=554,
                  end=564, text=S552_TEXT)
    note = out["dropped"]
    assert "`return option(*param_decls, **kwargs)` at line 563" in note
    assert "`kwargs.setdefault(\"is_flag\", True)` at line 558" in note
    assert "`kwargs[\"callback\"] = callback` at line 562" in note
    # The text holds the `if not param_decls:` branch, so the note keeps it out.
    assert "if not param_decls" not in note


def test_a_span_rewrite_that_keeps_every_statement_has_no_dropped_note(db, tmp_path):
    """Frame 173: a true rewrite lands with no note. The text holds every
    statement of the span in a new order, spacing and quoting, and binds
    `a` to a new value."""
    root = tmp_path / "wt"; root.mkdir()
    old = _lines("def f(x):", "    a = 1", "    b = \"two\"", "    g(a, b)",
                 "    if x:", "        return a", "    return b")
    (root / "m.py").write_text(chr(10).join(old) + chr(10))
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    from rota.roles import prompts
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    text = _lines("    b = 'two'", "    a=3", "    if x :", "        return  a",
                  "    g(a,b)", "    return b")
    out = sb.call("code.write", path="m.py", start=1, end=7,
                  text=chr(10).join(text) + chr(10))
    assert "dropped" not in out
    assert "b = 'two'" in (root / "m.py").read_text()


# Frame 261, night 150: the draft `json_only` woke the Vision Keeper's
# signoff 42 times, and 32 submits left it out. s251 is one of them.
NIGHT150_ITEMS = (
    ("confirm_default_on_eof", "Let confirm() take a default_on_eof flag"),
    ("defines_commands_and_options",
     "Users define commands and options using decorators in Python"),
    ("echo_json", "Add an echo_json(obj) helper next to echo"),
    ("how_it_works",
     "The program is a command-line interface toolkit called Click"),
    ("parses_and_executes_inputs",
     "Click parses command-line arguments and options, then executes"),
    ("provides_command_line_interface",
     "Click provides a command-line interface that users can interact with"),
)
S251_SUBMIT = [i for i, _ in NIGHT150_ITEMS]


def _night150_signoff(db, refs=("json_only",)):
    """s251's state: six items approved, `json_only` draft, and the wake
    `tick:signoff` with `Refs: json_only`."""
    for item_id, text in NIGHT150_ITEMS:
        db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                   "version) VALUES (?, ?, 'in_scope', 'approved', 1, 1)",
                   (item_id, text))
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('json_only', 'The program should cover only "
               "the confirm flag', 'in_scope', 'draft', NULL, 2)")
    db.commit()
    return build("vision_keeper", db, mode="normal",
                 wake=Wake("vision_keeper", "tick:signoff", refs=refs))


def test_night150_s251_signoff_submit_without_the_woken_draft_is_refused(db):
    vk = _night150_signoff(db)
    with pytest.raises(ValueError) as exc:
        vk.call("msg.submit_liaison", refs=list(S251_SUBMIT))
    full = S251_SUBMIT + ["json_only"]
    assert str(exc.value) == (
        f"The draft item json_only woke this signoff, and your refs leave it "
        f"out. Send msg.submit_liaison(refs={full!r}).")
    assert not vk.ctx.outbound


def test_night150_signoff_submit_with_the_woken_draft_lands(db):
    vk = _night150_signoff(db)
    vk.call("msg.submit_liaison", refs=S251_SUBMIT + ["json_only"])
    assert [m["verb"] for m in vk.ctx.outbound] == ["submit"]


def test_a_signoff_wake_with_no_draft_ref_submits_as_before(db):
    vk = _night150_signoff(db, refs=("echo_json",))
    vk.call("msg.submit_liaison", refs=["echo_json"])
    assert [m["verb"] for m in vk.ctx.outbound] == ["submit"]


def test_a_woken_draft_parked_at_the_submit_is_not_refused(db):
    # Frame 261, review 1, finding 2: the tick skips a parked draft, so the
    # door skips one parked after the tick.
    vk = _night150_signoff(db)
    db.execute("INSERT INTO item_parks (id, item_id, kind, by, cause_id, seq) "
               "VALUES ('p1', 'json_only', 'park', 'shift', 'm1', 1)")
    db.commit()
    vk.call("msg.submit_liaison", refs=list(S251_SUBMIT))
    assert [m["verb"] for m in vk.ctx.outbound] == ["submit"]


def test_four_left_out_drafts_name_the_count_and_the_ids_once(db):
    # Frame 261, review 1, finding 5: above three, the ids appear in the
    # call only.
    drafts = ["d1", "d2", "d3", "d4"]
    for d in drafts:
        db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                   "version) VALUES (?, 'A draft', 'in_scope', 'draft', NULL, 1)",
                   (d,))
    vk = _night150_signoff(db, refs=tuple(drafts))
    with pytest.raises(ValueError) as exc:
        vk.call("msg.submit_liaison", refs=["echo_json"])
    full = ["echo_json"] + drafts
    assert str(exc.value) == (
        f"4 draft items woke this signoff, and your refs leave them out. "
        f"Send msg.submit_liaison(refs={full!r}).")
