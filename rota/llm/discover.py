"""
Discovery for model setup: the providers on this machine, the models each
can serve, what the machine can hold, and a recommendation by fit.

plans/model-setup.md, step 2. Four pure-ish functions and no side effect.
`recommend` is pure: it takes what the others found and a benchmark table
and returns one model per capability group with its fit. No model is loaded
to get a number: the weight size comes from the provider's registry and the
KV cache from the model's metadata at the proposed context.

Discovery refuses to run while a run is driving: one GPU, and a load evicts
the walk's models. The caller checks `run_state` before calling here; this
module does not open a database.
"""
from __future__ import annotations

import json
import os
import platform
import subprocess
import urllib.request
from dataclasses import dataclass, field
from typing import Any

OLLAMA = "http://localhost:11434"
LLAMACPP = "http://localhost:8080"


@dataclass(frozen=True)
class Provider:
    name: str            # ollama | llamacpp | <profile name> for a remote
    kind: str            # ollama | litellm
    endpoint: str
    remote: bool = False
    key_env: str = ""


@dataclass(frozen=True)
class Model:
    provider: str
    name: str
    size_bytes: int | None = None          # weights on disk, from the registry
    meta: dict = field(default_factory=dict)   # block_count, head_count_kv, key_length, value_length
    parameter_size: str = ""
    quantization: str = ""


@dataclass(frozen=True)
class System:
    platform: str
    ram_bytes: int | None
    vram_total_bytes: int | None     # None means "cannot say", never zero
    vram_free_bytes: int | None
    unified: bool = False            # Apple Silicon: VRAM is RAM


@dataclass(frozen=True)
class Fit:
    model: str
    provider: str
    fit: str                         # in_vram | spills | does_not_fit | unknown
    weights_bytes: int | None
    kv_bytes: int | None
    need_bytes: int | None
    score: float | None              # from the benchmark table, None when unrecorded


def _get(url: str, timeout: float = 3.0, data: dict | None = None) -> Any:
    req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
    body = json.dumps(data).encode() if data is not None else None
    with urllib.request.urlopen(req, data=body, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def providers(user_profiles: list[dict] | None = None) -> list[Provider]:
    """The local providers that answer, and the remote ones a profile names."""
    out: list[Provider] = []
    try:
        _get(f"{OLLAMA}/api/tags")
        out.append(Provider("ollama", "ollama", OLLAMA))
    except Exception:
        pass
    try:
        _get(f"{LLAMACPP}/v1/models")
        out.append(Provider("llamacpp", "litellm", f"{LLAMACPP}/v1"))
    except Exception:
        pass
    for prof in user_profiles or []:
        prov = prof.get("provider") or {}
        endpoint = prov.get("endpoint") or ""
        if endpoint and "localhost" not in endpoint and "127.0.0.1" not in endpoint:
            out.append(Provider(prof.get("name", endpoint), prov.get("kind", "litellm"),
                                endpoint, remote=True, key_env=prov.get("key_env", "")))
    return out


def models(provider: Provider, key: str | None = None) -> list[Model]:
    """What one provider can serve. Ollama carries sizes and metadata; an
    OpenAI-shaped endpoint carries names only."""
    if provider.kind == "ollama":
        tags = _get(f"{provider.endpoint}/api/tags")
        out = []
        for m in tags.get("models") or []:
            meta: dict = {}
            details = m.get("details") or {}
            try:
                show = _get(f"{provider.endpoint}/api/show", timeout=10,
                            data={"model": m["name"]})
                meta = _kv_meta(show.get("model_info") or {})
            except Exception:
                pass
            out.append(Model(provider.name, m["name"], m.get("size"), meta,
                             details.get("parameter_size", ""),
                             details.get("quantization_level", "")))
        return out
    req = urllib.request.Request(f"{provider.endpoint}/models")
    if key:
        req.add_header("Authorization", f"Bearer {key}")
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return [Model(provider.name, m["id"]) for m in data.get("data") or []]


def _kv_meta(info: dict) -> dict:
    """The four numbers the KV cache needs, whatever the family prefix."""
    want = {"block_count": None, "head_count_kv": None, "key_length": None, "value_length": None}
    for k, v in info.items():
        for tail in want:
            if k.endswith("." + tail) or k.endswith(".attention." + tail):
                want[tail] = v
    # No guess for the KV heads: qwen3.5 reports none, and the query-head
    # count overstated its cache threefold against what Ollama loaded.
    # None means "cannot say"; the loaded size from /api/ps is the check.
    return {k: v for k, v in want.items() if v is not None}


def kv_cache_bytes(meta: dict, num_ctx: int, bytes_per_value: int = 2) -> int | None:
    """K and V, every layer, every KV head, at `num_ctx` tokens."""
    try:
        layers = int(meta["block_count"]); heads = int(meta["head_count_kv"])
        klen = int(meta.get("key_length") or 128); vlen = int(meta.get("value_length") or klen)
    except (KeyError, TypeError, ValueError):
        return None
    return layers * heads * (klen + vlen) * num_ctx * bytes_per_value


def system() -> System:
    """RAM, VRAM total and free, platform. None where nothing can say."""
    plat = platform.system().lower()
    ram = _ram_bytes()
    unified = plat == "darwin" and platform.machine().lower().startswith("arm")
    total, free = _vram_from_ollama()
    if total is None:
        total, free = _vram_from_nvidia_smi()
    if unified:
        total, free = ram, None
    return System(plat, ram, total, free, unified)


def _ram_bytes() -> int | None:
    try:
        import psutil  # optional
        return int(psutil.virtual_memory().total)
    except Exception:
        pass
    if platform.system() == "Windows":
        try:
            import ctypes
            class _Mem(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            m = _Mem(); m.dwLength = ctypes.sizeof(_Mem)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return int(m.ullTotalPhys)
        except Exception:
            return None
    try:
        return int(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES"))
    except (AttributeError, ValueError, OSError):
        return None


def _vram_from_ollama() -> tuple[int | None, int | None]:
    """Ollama reports no total. Its loaded models are a check, see `loaded`."""
    return None, None


def loaded(endpoint: str = OLLAMA) -> dict[str, tuple[int, int]]:
    """What Ollama holds right now: name -> (size, size_vram). One model at
    a time on this machine, swapped at each role change."""
    try:
        ps = _get(f"{endpoint}/api/ps")
    except Exception:
        return {}
    return {m["name"]: (int(m.get("size") or 0), int(m.get("size_vram") or 0))
            for m in ps.get("models") or []}


def _vram_from_nvidia_smi() -> tuple[int | None, int | None]:
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.total,memory.used",
                              "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None, None
    if out.returncode != 0 or not out.stdout.strip():
        return None, None
    total_mib, used_mib = (int(x.strip()) for x in out.stdout.strip().splitlines()[0].split(","))
    return total_mib << 20, (total_mib - used_mib) << 20


def fit_of(model: Model, sys_: System, num_ctx: int, resident: int = 1,
           loaded_bytes: int | None = None) -> Fit:
    """Weights plus KV cache at `num_ctx`, against VRAM then RAM. `resident`
    is how many such models are loaded at once. Ollama keeps one resident
    and swaps at each role change (measured 2026-09-11: /api/ps shows one
    model at a time), so the default is one; a server that keeps two needs
    the set, which is the open question the plan names."""
    kv = kv_cache_bytes(model.meta, num_ctx) if model.meta else None
    weights = model.size_bytes
    if weights is None and loaded_bytes is None:
        return Fit(model.name, model.provider, "unknown", None, kv, None, None)
    # A loaded model's own size is the measurement; arithmetic is the estimate.
    need = (loaded_bytes if loaded_bytes else (weights or 0) + (kv or 0)) * max(1, resident)
    if sys_.vram_total_bytes is None and sys_.ram_bytes is None:
        fit = "unknown"
    elif sys_.vram_total_bytes is not None and need <= sys_.vram_total_bytes:
        fit = "in_vram"
    elif sys_.ram_bytes is not None and need <= sys_.ram_bytes:
        fit = "spills"
    else:
        fit = "does_not_fit"
    return Fit(model.name, model.provider, fit, weights, kv, need, None)


def recommend(found: list[Model], sys_: System, benchmarks: list[dict],
              groups: list[str], num_ctx: int = 12288, resident: int = 1) -> dict[str, Fit | None]:
    """One model per capability group: the best-scoring recorded model that
    fits, else the best that spills. Unrecorded models are shown by the
    caller, never ranked here."""
    scored: dict[str, dict[str, float]] = {}
    for b in benchmarks:
        # One recorded case is not a ranking. The first table put qwen3.5:4b
        # first on two desks on the strength of one case each.
        if int(b.get("cases", 3) or 0) < 3:
            continue
        scored.setdefault(b["capability"], {})[b["model"]] = float(b["score"])
    fits = {m.name: fit_of(m, sys_, num_ctx, resident) for m in found}
    out: dict[str, Fit | None] = {}
    for group in groups:
        ranked = sorted(scored.get(group, {}).items(), key=lambda kv: -kv[1])
        choice = None
        for rank in ("in_vram", "spills"):
            for name, score in ranked:
                f = fits.get(name)
                if f is not None and f.fit == rank:
                    choice = Fit(f.model, f.provider, f.fit, f.weights_bytes, f.kv_bytes, f.need_bytes, score)
                    break
            if choice:
                break
        out[group] = choice
    return out


def recommend_from_record(found: list[Model], sys_: System, groups: list[str] | None = None,
                          num_ctx: int = 12288) -> dict[str, Fit | None]:
    """`recommend` over the shipped benchmarks table (plans/model-setup.md,
    step 5). Groups default to the roles the table knows."""
    from . import benchmarks as B
    table = B.load()
    caps = groups or sorted({r["capability"] for r in table
                             if not r["capability"].startswith(("transport:", "walk:"))})
    return recommend(found, sys_, table, caps, num_ctx=num_ctx, resident=1)

