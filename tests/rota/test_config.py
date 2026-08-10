"""
The settings the principal owns, and the two ways to stop.

The point of these is not that get/set works. It is that every cap the system
enforces is reachable from one place, and that `stop` and `halt` stay different
verbs — a distinction that collapses the moment someone treats one as a slower
version of the other.
"""
from __future__ import annotations

import pytest

from rota.core import config
from rota.core import loop
from rota.core.db import init_db
from rota.llm.llm import Pins, ScriptedBackend


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def test_defaults_come_from_the_declaration(db):
    assert config.get(db, "loop_cap") == 10
    assert config.get(db, "interrupt_cap") == 3
    assert config.get(db, "merge_gate") == "auto"


def test_an_undeclared_key_is_an_error_not_a_default(db):
    """
    Silently returning a default for a typo means the caller reads one value
    forever while believing they set another — the failure is invisible at the
    call site and at the setting site both.
    """
    with pytest.raises(config.UnknownSetting):
        config.get(db, "loop_capp")
    with pytest.raises(config.UnknownSetting):
        config.set(db, "loop_capp", 4)


def test_values_are_validated_against_the_declaration(db):
    with pytest.raises(ValueError):
        config.set(db, "merge_gate", "sometimes")
    with pytest.raises(ValueError):
        config.set(db, "loop_cap", "ten")
    config.set(db, "merge_gate", "review")
    assert config.get(db, "merge_gate") == "review"


def test_the_two_caps_are_separate_numbers(db):
    """
    Both are "how many times before we stop", and merging them is the obvious
    tidy-up. One spends compute and the other spends the principal; tuning the
    cheap one would silently change how often a person gets interrupted.
    """
    assert config.SETTINGS["loop_cap"].default != config.SETTINGS["interrupt_cap"].default
    config.set(db, "loop_cap", 40)
    assert config.get(db, "interrupt_cap") == 3


def test_no_cap_is_hard_coded():
    """
    Every enforced limit is declared. `tests_failing` had a literal 10 in it and
    `boot` took a cap as an argument nobody passed — both policy wearing the
    clothes of an implementation detail.
    """
    import inspect

    from rota.core import boot
    from rota.core import predicates
    for module in (predicates, boot):
        src = inspect.getsource(module)
        assert "config.get" in src, f"{module.__name__} enforces caps without reading them"


# ---------------------------------------------------------------------------
# stop and halt
# ---------------------------------------------------------------------------

def test_halt_stops_dispatch(db):
    config.halt(db)
    assert not config.dispatchable(db)
    s = loop.step(db, backend=ScriptedBackend([]), pins=Pins(model="scripted"))
    assert s.wake is None
    assert "halted" in s.note


def test_a_halted_system_says_so_rather_than_looking_finished(db):
    """
    "Quiescent" and "halted" are both an empty log. Only one of them means the
    work is done, and a halt that reads as completion is how a system gets
    declared finished while stopped.
    """
    config.halt(db)
    s = loop.step(db, backend=ScriptedBackend([]), pins=Pins(model="scripted"))
    assert "halted" in s.note and "resume" in s.note


def test_stop_drains_rather_than_preempting(db):
    """`stop` waits for what is running; `halt` does not. With a claim held they
    must report differently, or the two verbs are one verb."""
    db.execute("INSERT INTO claims (role, session_id) VALUES ('developer','s1')")

    config.stop(db)
    stopping = loop.step(db, backend=ScriptedBackend([]), pins=Pins(model="scripted"))
    assert not stopping.quiescent and "in flight" in stopping.note

    config.halt(db)
    halted = loop.step(db, backend=ScriptedBackend([]), pins=Pins(model="scripted"))
    assert halted.quiescent


def test_nothing_resumes_on_its_own(db):
    """An automatic resume would make halted a slow version of running."""
    config.halt(db)
    for _ in range(3):
        loop.step(db, backend=ScriptedBackend([]), pins=Pins(model="scripted"))
    assert config.get(db, "run_state") == "halted"

    config.resume(db)
    assert config.dispatchable(db)


def test_intake_still_lands_while_halted(db):
    """
    Recording what the principal said costs nothing and revokes nothing. A
    stopped system that also stopped listening is just a broken one — and the
    work would be waiting anyway when it resumed.
    """
    from rota.roles.principal import Answer, TranscriptPrincipal

    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
               "VALUES ('m1','t1','liaison','principal','confirm',1)")
    config.halt(db)

    s = loop.step(db, backend=ScriptedBackend([]), pins=Pins(model="scripted"),
                  principal=TranscriptPrincipal(
                      {"confirm": Answer(verb="converse", text="yes, go on")}))

    assert s.principal_messages, "a halted system stopped listening"
    assert db.execute("SELECT COUNT(*) n FROM entries").fetchone()["n"] == 1


def test_the_sampled_suites_do_not_pin_a_smaller_window():
    """
    The window was raised to 12288 because the largest prompts were ~9.2k and
    were being clipped -- from the front, where the role is told who it is. The
    suites kept their own `num_ctx=8192`, so every measurement of whether the
    system works was taken through the fault it had just fixed.

    A pin is not wrong in itself. A pin *below* the default is, because that is
    the shape the drift took and nothing noticed for weeks.
    """
    import re
    from rota.llm.llm import DEFAULT_NUM_CTX
    from rota import paths

    for name in ("test_l1.py", "test_l3.py"):
        src = (paths.REPO / "tests" / "rota" / name).read_text(encoding="utf-8")
        for pinned in re.findall(r"Pins\([^)]*num_ctx\s*=\s*(\d+)", src):
            assert int(pinned) >= DEFAULT_NUM_CTX, (
                f"{name} pins num_ctx={pinned} below the default "
                f"{DEFAULT_NUM_CTX}; prompts will be clipped at the front")
