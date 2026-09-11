"""Model setup, step 2: discovery's pure parts. No provider is called here."""
from __future__ import annotations

from rota.llm import discover as D


def test_the_kv_numbers_are_read_whatever_the_family_prefix():
    info = {"qwen3.block_count": 36, "qwen3.attention.head_count_kv": 8,
            "qwen3.attention.key_length": 128, "qwen3.attention.value_length": 128,
            "qwen3.attention.head_count": 32, "general.name": "x"}
    meta = D._kv_meta(info)
    assert meta == {"block_count": 36, "head_count_kv": 8, "key_length": 128, "value_length": 128}
    # K and V, 36 layers, 8 heads, 128 each, at 12288 tokens, two bytes: 1.8 GiB.
    assert D.kv_cache_bytes(meta, 12288) == 36 * 8 * 256 * 12288 * 2
    assert D.kv_cache_bytes({}, 12288) is None


def test_fit_is_weights_plus_cache_against_vram_then_ram():
    meta = {"block_count": 36, "head_count_kv": 8, "key_length": 128, "value_length": 128}
    m = D.Model("ollama", "qwen3:8b", size_bytes=5 << 30, meta=meta)
    machine = D.System("windows", ram_bytes=32 << 30, vram_total_bytes=10 << 30, vram_free_bytes=2 << 30)
    one = D.fit_of(m, machine, 12288, resident=1)
    assert one.fit == "in_vram" and one.need_bytes == (5 << 30) + one.kv_bytes
    two = D.fit_of(m, machine, 12288, resident=2)
    assert two.fit == "spills"
    none = D.fit_of(m, D.System("linux", None, None, None), 12288)
    assert none.fit == "unknown"
    big = D.Model("ollama", "huge", size_bytes=64 << 30, meta=meta)
    assert D.fit_of(big, machine, 12288).fit == "does_not_fit"


def test_recommend_ranks_recorded_models_by_score_within_fit():
    meta = {"block_count": 36, "head_count_kv": 8, "key_length": 128, "value_length": 128}
    found = [D.Model("ollama", "llama3.1:8b", 5 << 30, meta),
             D.Model("ollama", "qwen3:8b", 5 << 30, meta),
             D.Model("ollama", "big:70b", 40 << 30, meta),
             D.Model("ollama", "new:1b", 1 << 30, meta)]
    machine = D.System("windows", 32 << 30, 10 << 30, 2 << 30)
    bench = [{"model": "llama3.1:8b", "capability": "judge", "score": 0.9},
             {"model": "qwen3:8b", "capability": "judge", "score": 0.7},
             {"model": "big:70b", "capability": "desk", "score": 0.95},
             {"model": "qwen3:8b", "capability": "desk", "score": 0.8}]
    bench.append({"model": "new:1b", "capability": "judge", "score": 1.0, "cases": 1})
    out = D.recommend(found, machine, bench, ["judge", "desk", "prose"], num_ctx=12288, resident=1)
    # One case does not outrank nine: new:1b is shown, never ranked.
    assert out["judge"].model == "llama3.1:8b" and out["judge"].fit == "in_vram"
    # The best-scoring desk model spills to RAM; the one that fits wins.
    assert out["desk"].model == "qwen3:8b"
    # No benchmark for the group: nothing is ranked, the caller shows the list.
    assert out["prose"] is None


def test_the_benchmarks_table_is_built_from_the_record(tmp_path):
    """plans/model-setup.md step 5: register, walks and the tool check fold
    into one table; recommend reads it."""
    import json
    import sqlite3

    from rota.llm import benchmarks as B

    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE case_runs (case_id TEXT, model TEXT, prompt_hash TEXT, run_no INT, "
                 "passed INT, problems TEXT, seq INT, transcript TEXT, load_id TEXT)")
    rows = []
    seq = 0
    for cid, model, passes in (("L1-DV-a", "m1", [1, 1, 1, 1, 1]), ("L1-DV-b", "m1", [0, 0, 0, 0, 0]),
                               ("L1-DV-a", "m2", [1, 1, 1, 0, 0]), ("T0-PROVIDER-x-native-call", "m1", [1])):
        for i, p in enumerate(passes):
            seq += 1
            rows.append((cid, model, "h", i + 1, p, "[]", seq, "[]", ""))
    conn.executemany("INSERT INTO case_runs VALUES (?,?,?,?,?,?,?,?,?)", rows)
    reg = {(r["model"], r["capability"]): r for r in B.from_register(conn)}
    assert reg[("m1", "DV")]["score"] == 0.5 and reg[("m1", "DV")]["cases"] == 2
    assert reg[("m2", "DV")]["score"] == 1.0
    tc = B.from_tool_check(conn)
    assert tc == [{"model": "m1", "capability": "transport:native-call", "score": 1.0, "cases": 1,
                   "source": "toolcheck", "recorded_on": tc[0]["recorded_on"]}]
    walks = tmp_path / "walks.jsonl"
    walks.write_text(json.dumps({"profile": "p", "merged": 1}) + "\n" +
                     json.dumps({"profile": "p", "merged": 0}) + "\n", encoding="utf-8")
    w = B.from_walks(walks, {"p": ["m1"]})
    assert w[0]["model"] == "m1" and w[0]["score"] == 0.5 and w[0]["capability"] == "walk:merge"


def test_choose_picks_a_default_and_the_desks_that_differ():
    from rota.llm import discover as D, setup

    plan = setup.Plan([], D.System("x", None, None, None), [],
                      {"LI": "qwen3:8b", "VK": "qwen3:8b", "CR": "llama3.1:8b", "RS": None}, ["LI", "VK", "CR", "RS"])
    default, roles = setup.choose(plan)
    assert default == "qwen3:8b" and roles == {"critic": "llama3.1:8b"}
    assert setup.choose(setup.Plan([], plan.machine, [], {"LI": None}, ["LI"])) == ("", {})


def test_a_user_profile_is_written_from_a_shipped_one(tmp_path, monkeypatch):
    monkeypatch.setenv("ROTA_HOME", str(tmp_path))
    from rota.llm import profile, setup

    path = setup.write("mine", "local", "qwen3:8b", {"critic": "llama3.1:8b"})
    assert path == tmp_path / "profiles" / "mine.toml"
    back = profile.find("mine")
    assert back.default_model == "qwen3:8b" and back.roles == {"critic": "llama3.1:8b"}
    assert back.pins.get("num_ctx") == 12288 and "key" not in path.read_text(encoding="utf-8")


def test_capability_groups_come_from_the_modes_tools():
    """plans/model-setup.md step 7: the partition is the graph's. A mode may
    sit in a different group from its role."""
    from rota.llm import groups

    assert groups.group_of(["code.source", "code.write", "code.commit"]) == "code"
    assert groups.group_of(["transcript.quote", "msg.clarify_principal"]) == "prose"
    assert groups.group_of(["tickets.scan", "batches.group"]) == "rows"
    by = groups.by_mode()
    assert by[("architect", "survey")] == "code" and by[("architect", "grouping")] == "rows"
    assert by[("developer", "batch_start")] == "code"
    assert by[("liaison", "landing")] == "prose"
    g = groups.groups()
    assert set(g) <= {"code", "prose", "rows"} and sum(len(v) for v in g.values()) == len(by)
    assert groups.group_of_role("developer") == "code"


def test_group_rows_fold_the_roles_by_cases():
    from rota.llm import benchmarks as B

    reg = [{"model": "m", "capability": "DV", "score": 1.0, "cases": 2},
           {"model": "m", "capability": "TS", "score": 0.5, "cases": 2},
           {"model": "m", "capability": "LI", "score": 0.9, "cases": 5}]
    rows = {r["capability"]: r for r in B.by_group(reg)}
    assert rows["group:code"]["score"] == 0.75 and rows["group:code"]["cases"] == 4
    assert rows["group:prose"]["score"] == 0.9


def test_pull_on_a_remote_or_a_llamacpp_server_never_guesses(monkeypatch):
    from rota.llm import discover as D

    remote = D.Provider("acme", "litellm", "https://api.acme.test/v1", remote=True)
    assert D.pull(remote, "x")["pulled"] is False
    monkeypatch.setattr(D, "models", lambda p, key=None: [D.Model("llamacpp", "served.gguf")])
    local = D.Provider("llamacpp", "litellm", "http://localhost:8080/v1")
    assert D.pull(local, "served.gguf")["found"] and not D.pull(local, "other.gguf")["found"]
