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
                      "native": 1, "walk": 1, "cut": 0}, counts
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


class Cut(Counting):
    """A model whose reply stops at the output budget, as Ollama says it."""

    def complete(self, system, user, pins, tools=None):
        self.calls += 1
        return Completion(text="TOOL: code.write(", pins=pins, backend=self.name,
                          raw={"done_reason": "length"})


def test_a_cut_reply_replays_cut_and_a_whole_reply_replays_whole(tmp_path, monkeypatch):
    """Night 147's s71, s24, s41, s9 and s81 replayed a cut reply as whole. The
    runner then ran the call that the cut had blocked, and the session ran live
    from the next turn (frame 233, pass 4)."""
    night = _module()
    monkeypatch.setenv("ROTA_NIGHT_CASSETTES", str(tmp_path / "cassettes.db"))
    monkeypatch.setenv("WALK_REPLAY", "1")
    pins = Pins(model="scripted")
    cut, whole = Cut(), Counting()
    night.wrap(cut, "onboarding").complete("sys", "cut", pins)
    night.wrap(whole, "onboarding").complete("sys", "whole", pins)

    replayed = night.wrap(Counting(), "onboarding")
    again = replayed.complete("sys", "cut", pins)
    assert replayed.hits == 1 and again.text == "TOOL: code.write("
    assert again.raw.get("done_reason") == "length", again.raw
    plain = replayed.complete("sys", "whole", pins)
    assert replayed.hits == 2 and not plain.raw, plain.raw


#: The `cassettes` table before frame 233 moved the stop reason onto it.
OLD_CASSETTES = (
    "CREATE TABLE cassettes (key TEXT PRIMARY KEY, model TEXT NOT NULL, "
    "temperature REAL NOT NULL, num_ctx INTEGER NOT NULL, prompt_hash TEXT NOT NULL, "
    "system TEXT NOT NULL, user TEXT NOT NULL, completion TEXT NOT NULL, "
    "tool_calls TEXT NOT NULL DEFAULT '[]', backend TEXT NOT NULL, "
    "hits INTEGER NOT NULL DEFAULT 0)")


def _old_cassette(path, pins, rows, side=None):
    """A cassette file of the old schema, with the night's side table when
    `side` maps keys to reasons."""
    from rota.llm.cassettes import key_for

    conn = sqlite3.connect(path)
    conn.execute(OLD_CASSETTES)
    keys = {}
    for user, completion in rows:
        keys[user] = key_for("sys", user, pins, "text")
        conn.execute("INSERT INTO cassettes VALUES (?,?,?,?,?,?,?,?,'[]','old',0)",
                     (keys[user], pins.model, pins.temperature, pins.num_ctx,
                      pins.prompt_hash, "sys", user, completion))
    if side is not None:
        conn.execute("CREATE TABLE done_reasons (key TEXT PRIMARY KEY, "
                     "done_reason TEXT NOT NULL)")
        for user, reason in side.items():
            conn.execute("INSERT INTO done_reasons VALUES (?, ?)", (keys[user], reason))
    conn.commit()
    conn.close()


def test_a_cassette_without_the_reason_column_replays_and_gains_it(tmp_path, monkeypatch):
    """A cassette written before frame 233 holds no `done_reason` column. It
    replays, and its rows read no stop reason."""
    pins = Pins(model="scripted")
    path = tmp_path / "old.db"
    _old_cassette(path, pins, [("old", "nothing to do")])

    night = _module()
    monkeypatch.setenv("ROTA_NIGHT_CASSETTES", str(path))
    monkeypatch.setenv("WALK_REPLAY", "1")
    fake = Counting()
    replayed = night.wrap(fake, "onboarding").complete("sys", "old", pins)
    assert fake.calls == 0 and replayed.text == "nothing to do" and not replayed.raw
    cols = {r[1] for r in sqlite3.connect(path).execute("PRAGMA table_info(cassettes)")}
    assert "done_reason" in cols


def test_the_side_table_of_a_night_moves_onto_the_column(tmp_path, monkeypatch):
    """A night file of pass 4 holds the `done_reasons` side table. The first
    open copies each reason onto its row and drops the table, so one store
    holds the reason (frame 233)."""
    pins = Pins(model="scripted")
    path = tmp_path / "night.db"
    _old_cassette(path, pins, [("cut", "TOOL: code.write("), ("whole", "Done.")],
                  side={"cut": "length"})

    monkeypatch.setenv("ROTA_NIGHT_CASSETTES", str(path))
    monkeypatch.setenv("WALK_REPLAY", "1")
    wrapped = _module().wrap(Counting(), "onboarding")
    assert wrapped.complete("sys", "cut", pins).raw == {"done_reason": "length"}
    assert not wrapped.complete("sys", "whole", pins).raw
    conn = sqlite3.connect(path)
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert "done_reasons" not in tables
    assert dict(conn.execute("SELECT user, done_reason FROM cassettes")) == {
        "cut": "length", "whole": ""}


def test_the_seed_marks_a_turn_whose_next_prompt_gains_the_cut_line(tmp_path, monkeypatch):
    """A night database stores no `done_reason`. The runner opens the results
    block of a cut turn with `ERROR reply cut:`, and the line stays in the
    later prompts. So a cut is a turn whose next prompt holds one more line
    (night 146: s71's turns 2 to 4 all hold the line of turn 1)."""
    _night_db(tmp_path / "night.db")
    line = "ERROR reply cut: your reply was cut at the output budget before it ended."
    conn = sqlite3.connect(tmp_path / "night.db")
    conn.execute("DELETE FROM turns WHERE session_id = 's1'")
    for n, user, completion in ((1, "user a1", "TOOL: code.write("),
                                (2, f"user a1\n\nTOOL: code.write(\n\n{line}", "TOOL: x()"),
                                (3, f"user a1\n\n{line}\n\nTOOL: x()\n\nOK x", "Done.")):
        conn.execute("INSERT INTO turns (session_id, seq, system, user, completion) "
                     "VALUES ('s1', ?, 'sys a', ?, ?)", (n, user, completion))
    conn.commit()
    conn.close()
    cassette = tmp_path / "night_cassettes.db"
    counts = _module(SEED).seed(tmp_path / "night.db", cassette)
    assert counts["cut"] == 1 and counts["turns"] == 4, counts

    monkeypatch.setenv("ROTA_NIGHT_CASSETTES", str(cassette))
    monkeypatch.setenv("WALK_REPLAY", "1")
    wrapped = _module().wrap(Counting(), "onboarding")
    pins = Pins(model="qwen3:8b", num_ctx=16384)
    assert wrapped.complete("sys a", "user a1", pins).raw == {"done_reason": "length"}
    assert not wrapped.complete("sys a", f"user a1\n\nTOOL: code.write(\n\n{line}", pins).raw
    assert not wrapped.complete("sys b", "user b", pins).raw
    assert wrapped.hits == 3

    # Night 147's wrap ran before pass 4, so its live cut rows hold no reason.
    # A second seed gives a present key its reason when the reply is the same
    # (frame 233, pass 4b).
    out = sqlite3.connect(cassette)
    out.execute("UPDATE cassettes SET done_reason = ''")
    out.execute("UPDATE cassettes SET completion = 'other' WHERE user = 'user b'")
    out.commit()
    out.close()
    again = _module(SEED).seed(tmp_path / "night.db", cassette)
    assert again["cut"] == 1 and again["turns"] == 0, again
    rows = sqlite3.connect(cassette).execute(
        "SELECT COUNT(*) FROM cassettes WHERE done_reason != ''").fetchone()[0]
    assert rows == 1
    assert _module(SEED).seed(tmp_path / "night.db", cassette)["cut"] == 0

    # A present key whose stored reply differs keeps no reason.
    out = sqlite3.connect(cassette)
    out.execute("UPDATE cassettes SET done_reason = ''")
    out.execute("UPDATE cassettes SET completion = 'other' WHERE user = 'user a1'")
    out.commit()
    out.close()
    assert _module(SEED).seed(tmp_path / "night.db", cassette)["cut"] == 0


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
