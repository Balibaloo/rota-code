"""Frame 304, night 162 (2026-10-24): the arrange door refused s351's and
s364's bodies on `custom_version_option()` with no `callback`. Its step
read "Call `custom_version_option` with `callback`". The batch changes
`version_option`, so the step sent s351 further into the wrong function,
and s351 filed faults 12 and 13. Cause 9: a door's text points the wrong
way. The step names the criterion's surface that the batch touches, and
never a name that only the body or the traceback holds."""
from rota.core.sandbox import build
from rota.roles import api
from tests.rota.test_frame304_arrange_door import _git_batch, _ran
from tests.rota.test_night46_context import db  # noqa: F401

# Word for word from .rota/clickI_night162.db: s351's second body for
# tst_c3_version_off, and the criterion as s351's turn 1 showed it.
S351_TST_C3 = (
    'def test_version_message_excludes_python_version():\n'
    '    import click\n'
    '    from click.testing import CliRunner\n'
    '    from click.decorators import custom_version_option\n'
    '    @click.command()\n'
    '    @custom_version_option(message="Version: %(version)s")\n'
    '    def cli():\n'
    '        pass\n'
    '\n'
    '    runner = CliRunner()\n'
    '    result = runner.invoke(cli, [])\n'
    '    assert "3.10.0" not in result.output')
C3_TEXT = ("When the setting show python is off (the default), the printed "
           "message does not include the Python version string.")
C3_REFS = ('["src/click/decorators.py::custom_version_option", '
           '"src/click/decorators.py::version_option"]')
PATH = "tests/test_version_option_show_python_off.py"
# The run is built in pytest's form. The night stored the refusal only.
S351_RUN = (
    "    def test_version_message_excludes_python_version():\n"
    "        import click\n"
    "        from click.testing import CliRunner\n"
    "        from click.decorators import custom_version_option\n"
    "        @click.command()\n"
    ">       @custom_version_option(message=\"Version: %(version)s\")\n"
    "E       TypeError: custom_version_option() missing 1 required "
    "positional argument: 'callback'\n\n"
    "tests\\test_version_option_show_python_off.py:6: TypeError\n"
    "1 failed in 0.1s")


def _step(said: str) -> str:
    return said.split("no code can pass it. ", 1)[1]


def _version_batch(db, tmp_path, refs):
    _git_batch(db, tmp_path)
    db.execute("UPDATE criteria SET text = ?, surface_refs = ? WHERE id = 'c1'",
               (C3_TEXT, refs))
    db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind, "
               "confidence) VALUES ('b1', "
               "'src/click/decorators.py::version_option', 'symbol', "
               "'possible')")
    db.commit()


def test_s351_step_names_the_surface_the_batch_changes(db, tmp_path, monkeypatch):
    _version_batch(db, tmp_path, C3_REFS)
    _ran(monkeypatch, S351_RUN)
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    said = api._arrange_run_refusal(sb.ctx, "b1", "c1", PATH, S351_TST_C3)
    assert said and "no code can pass it." in said
    step = _step(said)
    assert "`version_option`" in step
    assert "custom_version_option" not in step
    assert "Line 6 raises `TypeError` before the call under test" in step


def test_a_criterion_with_no_surface_names_the_line_and_no_function(
        db, tmp_path, monkeypatch):
    _version_batch(db, tmp_path, "[]")
    body = 'def test_x():\n    cfg = {}["key"]\n    assert cfg == 1\n'
    run = ("    def test_x():\n"
           ">       cfg = {}[\"key\"]\n"
           "E       KeyError: 'key'\n\n"
           "tests\\test_cfg.py:2: KeyError\n1 failed in 0.1s")
    _ran(monkeypatch, run)
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    said = api._arrange_run_refusal(sb.ctx, "b1", "c1", "tests/test_cfg.py", body)
    assert said and "no code can pass it." in said
    step = _step(said)
    assert step.startswith("Line 2 raises `KeyError` before the call "
                           "under test runs. Fix line 2 so that it runs.")
    assert "`" not in step.replace("`KeyError`", "").split(" If ")[0]
    assert "Call `" not in step
