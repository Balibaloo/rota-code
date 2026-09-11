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
    out = D.recommend(found, machine, bench, ["judge", "desk", "prose"], num_ctx=12288, resident=1)
    assert out["judge"].model == "llama3.1:8b" and out["judge"].fit == "in_vram"
    # The best-scoring desk model spills to RAM; the one that fits wins.
    assert out["desk"].model == "qwen3:8b"
    # No benchmark for the group: nothing is ranked, the caller shows the list.
    assert out["prose"] is None
