"""probes/night_cassette.py: the night's onboarding replays recorded wakes.

Frame 233, step 1. Night 145 against night 144 gave 85 of 85 identical first
replies to identical whole prompts (plans/night-reuse-investigation.md, part
4 D). So an onboarding wake with a recorded prompt takes the recording, and
a walk never reads or writes the night cassette, because a replayed walk
session is not a new sample (part 4 D, Risk).
"""
import importlib.util
import json
import sqlite3

import pytest

from rota import paths
from rota.core.db import init_db
from rota.core.runner import run_session
from rota.core.scheduler import Wake
from rota.llm.llm import Completion, Pins

MODULE = paths.REPO / "probes" / "night_cassette.py"
SEED = paths.REPO / "probes" / "seed_night_cassettes.py"


def _module(path=MODULE):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(autouse=True)
def _own_tally():
    """The fake's calls stay out of the suite's tally. `conftest.py` saves the
    tally to `.rota-timings.json`, and a fake record that costs nothing makes
    the next estimate of a record near zero (frame 233's review, finding 3)."""
    from rota.llm import cassettes

    tally = cassettes.TALLY     # `conftest.py` holds this object, so restore it in place
    saved = (tally.replays, tally.records, tally.replay_seconds, tally.record_seconds)
    yield
    (tally.replays, tally.records, tally.replay_seconds, tally.record_seconds) = saved


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


def test_begin_drops_the_counts_of_a_session_that_failed(tmp_path, monkeypatch):
    """A failed session never reads `name`, so its calls counted in the next
    session's `sessions.backend` (frame 233's review, finding 1)."""
    night = _module()
    monkeypatch.setenv("ROTA_NIGHT_CASSETTES", str(tmp_path / "cassettes.db"))
    monkeypatch.setenv("WALK_REPLAY", "1")
    pins = Pins(model="scripted")
    wrapped = night.wrap(Counting(), "onboarding")
    wrapped.complete("sys", "recorded", pins)
    assert wrapped.name == "counting"

    wrapped.begin()
    wrapped.complete("sys", "new", pins)        # a live call, then the session fails
    wrapped.begin()
    wrapped.complete("sys", "recorded", pins)   # the next session replays whole
    assert wrapped.name == "cassette:counting"


def _night_db(path):
    """A night with two onboarding sessions, one native session and one walk
    session. The walk starts at the session the first sentence woke."""
    conn = init_db(path)
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
                 "VALUES ('m_p1','t_p1','principal','liaison','converse',1)")
    pins = json.dumps(Pins(model="qwen3:8b", num_ctx=16384).as_dict())
    rows = [("s1", 1, None, [("sys a", "user a1", "TOOL: x()"), ("sys a", "user a2", "Done.")]),
            ("s2", 2, None, [("sys b", "user b", "nothing to do")]),
            ("s3", 3, None, [("sys c", "user c", "")]),
            ("s4", 4, "m_p1", [("sys d", "user d", "Done.")])]
    for sid, seq, trigger, turns in rows:
        conn.execute("INSERT INTO sessions (id, role, trigger_msg, committed, seq, pins_json, "
                     "backend) VALUES (?, 'liaison', ?, 1, ?, ?, 'ollama')",
                     (sid, trigger, seq, pins))
        for n, (system, user, completion) in enumerate(turns, 1):
            conn.execute("INSERT INTO turns (session_id, seq, system, user, completion) "
                         "VALUES (?,?,?,?,?)", (sid, n, system, user, completion))
    conn.commit()
    conn.close()


def test_the_seed_fills_the_night_cassette_from_the_onboarding_turns(tmp_path, monkeypatch):
    _night_db(tmp_path / "night.db")
    before = (tmp_path / "night.db").read_bytes()
    cassette = tmp_path / "night_cassettes.db"
    counts = _module(SEED).seed(tmp_path / "night.db", cassette)
    assert counts == {"sessions": 2, "turns": 3, "present": 0, "notes": 0,
                      "native": 1, "walk": 1}, counts
    assert (tmp_path / "night.db").read_bytes() == before, "the seed wrote the night"

    # The seeded key is the key the wrap looks up.
    monkeypatch.setenv("ROTA_NIGHT_CASSETTES", str(cassette))
    monkeypatch.setenv("WALK_REPLAY", "1")
    fake = Counting()
    wrapped = _module().wrap(fake, "onboarding")
    pins = Pins(model="qwen3:8b", num_ctx=16384)
    assert wrapped.complete("sys a", "user a2", pins).text == "Done."
    assert wrapped.complete("sys b", "user b", pins).text == "nothing to do"
    assert fake.calls == 0
    wrapped.complete("sys c", "user c", pins)
    wrapped.complete("sys d", "user d", pins)
    assert fake.calls == 2, "a native or a walk turn was seeded"
    again = _module(SEED).seed(tmp_path / "night.db", cassette)
    assert again["present"] == 3 and again["turns"] == 0, again


def test_the_seed_skips_a_note_turn_and_needs_its_destination(tmp_path, capsys):
    """`db.session_note` writes a turn with an empty system and an empty user
    text. Night 146 holds 61 in onboarding, and they counted as turns and as
    present (frame 233's review 2, finding 1)."""
    _night_db(tmp_path / "night.db")
    conn = sqlite3.connect(tmp_path / "night.db")
    for n in (3, 4):
        conn.execute("INSERT INTO turns (session_id, seq, system, user, completion) "
                     "VALUES ('s1', ?, '', '', 'a note')", (n,))
    conn.commit()
    conn.close()
    seed = _module(SEED)
    cassette = tmp_path / "out" / "night_cassettes.db"
    counts = seed.seed(tmp_path / "night.db", cassette)
    assert (counts["turns"], counts["present"], counts["notes"]) == (3, 0, 2), counts
    rows = sqlite3.connect(cassette).execute(
        "SELECT COUNT(*) FROM cassettes WHERE system = '' AND user = ''").fetchone()[0]
    assert rows == 0, "a note turn became a cassette row"

    # The destination is required, so a seed from a worktree cannot land in
    # that worktree's `.rota/` (frame 233's review 2, finding 2).
    assert seed.main([str(tmp_path / "night.db")]) == 2
    assert seed.main([str(tmp_path / "night.db"), str(cassette)]) == 0
    out = capsys.readouterr().out
    assert str(tmp_path / "night.db") in out and str(cassette) in out, out


class _Model:
    """The principal's model: counts the pages that reach it."""

    def __init__(self):
        self.pages = []

    def __call__(self, model, system, page, cwd):
        self.pages.append(page)
        return {"ok": True, "words": "live words", "error": "", "duration_ms": 900,
                "total_cost_usd": 0.05}


def _principal(tmp_path, phase, model):
    import sys
    sys.path.insert(0, str(paths.REPO / "probes"))
    mod = _module(paths.REPO / "probes" / "agent_principal.py")
    return mod.AgentPrincipal(None, "opus", "r", set(), phase=phase, night="147",
                              runs=tmp_path / "runs", call=model, say=lambda *a, **k: None)


def test_an_onboarding_page_takes_the_recorded_words_and_a_walk_page_never(tmp_path, monkeypatch):
    record = tmp_path / "night146.principal.jsonl"
    rows = [{"kind": "call", "phase": "onboarding", "page": "page one", "verb": "present",
             "words": "recorded words", "ok": True},
            {"kind": "call", "phase": "sentence 1", "page": "page two", "verb": "present",
             "words": "walk words", "ok": True},
            {"kind": "land", "ask_id": "m2", "as": "reply", "landed_id": "m3"}]
    record.write_bytes("".join(json.dumps(r) + "\n" for r in rows).encode("utf-8"))
    monkeypatch.setenv("ROTA_PRINCIPAL_REPLAY", str(record))
    monkeypatch.setenv("WALK_REPLAY", "1")

    model = _Model()
    onboarding = _principal(tmp_path, "onboarding", model)
    assert onboarding._ask_model("m2", "present", "label", "page one") == "recorded words"
    assert model.pages == [], "a recorded onboarding page reached the model"
    assert onboarding._ask_model("m4", "present", "label", "page two") == "live words"
    assert onboarding._ask_model("m5", "present", "label", "page three") == "live words"
    assert len(model.pages) == 2

    walk = _principal(tmp_path, "sentence 1", model)
    assert walk._ask_model("m6", "present", "label", "page one") == "live words"
    assert len(model.pages) == 3, "a walk page took a recording"

    written = [json.loads(line) for line in
               (tmp_path / "runs" / "r.principal.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [r["model"] for r in written] == ["replay", "opus", "opus", "opus"], written
    assert written[0]["words"] == "recorded words" and written[0]["total_cost_usd"] == 0.0

    monkeypatch.delenv("WALK_REPLAY")
    unset = _principal(tmp_path, "onboarding", model)
    assert unset._ask_model("m7", "present", "label", "page one") == "live words"
