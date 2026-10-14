"""probes/night_cassette.py: the night's onboarding replays recorded wakes.

Frame 233, step 1. Night 145 against night 144 gave 85 of 85 identical first
replies to identical whole prompts (plans/night-reuse-investigation.md, part
4 D). So an onboarding wake with a recorded prompt takes the recording, and
a walk never reads or writes the night cassette, because a replayed walk
session is not a new sample (part 4 D, Risk).
"""
import importlib.util

from rota import paths
from rota.core.db import init_db
from rota.core.runner import run_session
from rota.core.scheduler import Wake
from rota.llm.llm import Completion, Pins

MODULE = paths.REPO / "probes" / "night_cassette.py"


def _module():
    spec = importlib.util.spec_from_file_location("night_cassette", MODULE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Counting:
    """A model that counts the calls that reach it."""

    name = "counting"
    host = "http://127.0.0.1:11434"

    def __init__(self):
        self.calls = 0

    def complete(self, system, user, pins, tools=None):
        self.calls += 1
        return Completion(text="nothing to do", pins=pins, backend=self.name)


def _seeded(path):
    conn = init_db(path)
    conn.execute("INSERT INTO entries (id, author, text, ts_order) "
                 "VALUES ('u1','principal','let users delete their account',1)")
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
                 "VALUES ('m1','t1','liaison','vision_keeper','deliver',1)")
    return conn


def _session(tmp_path, name, backend):
    """One session on a fresh database. Two databases seeded alike give the
    same prompt, so the second session's key is the first one's."""
    conn = _seeded(tmp_path / f"{name}.db")
    wake = Wake(role="vision_keeper", kind="message", message_id="m1", detail="deliver")
    outcome = run_session(conn, wake, backend=backend, pins=Pins(model="scripted"))
    assert outcome.committed, outcome.errors
    return conn.execute("SELECT backend FROM sessions").fetchone()["backend"]


def test_an_onboarding_wake_replays_and_a_walk_wake_runs_live(tmp_path, monkeypatch):
    night = _module()
    cassette = tmp_path / "night" / "cassettes.db"
    monkeypatch.setenv("ROTA_NIGHT_CASSETTES", str(cassette))
    monkeypatch.setenv("WALK_REPLAY", "1")

    fake = Counting()
    first = _session(tmp_path, "on1", night.wrap(fake, "onboarding"))
    second = _session(tmp_path, "on2", night.wrap(fake, "onboarding"))
    assert fake.calls == 1, "the second onboarding wake reached the model"
    assert first == "counting"
    assert second.startswith("cassette:"), second

    walk = Counting()
    for name in ("w1", "w2"):
        assert night.wrap(walk, "sentence 1") is walk
        assert _session(tmp_path, name, night.wrap(walk, "sentence 1")) == "counting"
    assert walk.calls == 2, "a walk wake took a recording"

    # The card reading still reaches the server behind the wrap.
    from rota.core.loop import _spill_endpoint
    assert _spill_endpoint(night.wrap(fake, "onboarding")) == Counting.host


def test_a_missing_cassette_is_empty_and_an_unset_flag_records_only(tmp_path, monkeypatch):
    night = _module()
    cassette = tmp_path / "absent" / "cassettes.db"
    monkeypatch.setenv("ROTA_NIGHT_CASSETTES", str(cassette))
    monkeypatch.delenv("WALK_REPLAY", raising=False)

    fake = Counting()
    for name in ("a", "b"):
        assert _session(tmp_path, name, night.wrap(fake, "onboarding")) == "counting"
    assert fake.calls == 2, "an onboarding without WALK_REPLAY=1 took a recording"
    assert cassette.exists(), "the live onboarding left no recording for the next night"
