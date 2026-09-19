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

from .llm import OLLAMA_HOST

# One default host for the package, read from the environment like
# `rota/llm/llm.py:44` does. A bare literal measured the wrong card: the
# recorder runs on 11435, and both servers answer on this box, so the
# reading looked plausible instead of failing.
OLLAMA = OLLAMA_HOST
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
class Resident:
    """
    One model the server holds right now, and the window it allocated.

    Named rather than a tuple: three unlabelled integers at a call site say
    nothing, and the third one is the whole point. `num_ctx` is
    `context_length` from `/api/ps`, and None means the server reported
    none.
    """
    name: str
    size: int                        # weights plus cache, wherever they sit
    size_vram: int                   # the part of `size` that is on the card
    num_ctx: int | None = None

    @property
    def spill(self) -> int:
        """What the server put in RAM. RAM is where the turn time goes."""
        return max(0, self.size - self.size_vram)


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


def loaded(endpoint: str = OLLAMA) -> dict[str, Resident] | None:
    """
    What Ollama holds right now: name -> `Resident`. One model at a time on
    this machine, swapped at each role change.

    `None` means the server did not answer. `{}` means it answered and holds
    nothing. The two used to share the value `{}`, so a monitor stayed
    silent when it could not see the card, which reads as good news.

    `num_ctx` is `context_length` from `/api/ps`, which is the window the
    server allocated. Read that, never the window the run asked for: a pin
    that never reached the server is the fault this reading exists to find
    (observed: probes/frame43/p_window.py, 2026-09-19).
    """
    out: dict[str, Resident] = {}
    try:
        # The body is built inside the guard, not after it. A malformed
        # answer used to raise out of here, and `setup.plan` does not
        # contain that. The 3 second timeout in `_get` stays: a monitor
        # that blocks the caller is its own fault.
        ps = _get(f"{endpoint}/api/ps")
        for m in ps.get("models") or []:
            name = m.get("name") or m.get("model")
            if not name:
                continue                 # a row that names nothing says nothing
            ctx = m.get("context_length")
            out[name] = Resident(
                name, int(m.get("size") or 0), int(m.get("size_vram") or 0),
                int(ctx) if ctx else None)
    except Exception:
        return None
    return out


def spill_of(held: dict[str, Resident] | None,
             model: str | None = None) -> dict | None:
    """
    The spill of one loaded model, in bytes. Pure: it reads no server.

    `size` minus `size_vram` is what Ollama put in RAM, and RAM is where the
    turn time goes. An empty card gives a zero row, which is a measurement.
    `None` for `held` gives `None`, because "cannot see" is not "no spill".

    `model` names the desk's model. A name the card does not hold falls back
    to the worst spill on the card, so the row never reports the wrong load
    as healthy.

    `matched` says whether the row is the model that was asked for. The
    caller needs it: a session's own window belongs beside its own model,
    and a card that holds another model must not lend its window to the
    session's pin. A night swaps models at every role change, so without
    the flag a swap can manufacture a pin-mismatch alarm.

    `num_ctx` is the window the server allocated, and it can be None on a
    server too old to report one.
    """
    if held is None:
        return None
    if not held:
        return {"model": "", "size": 0, "size_vram": 0, "spill": 0,
                "num_ctx": None, "matched": False}
    matched = bool(model) and model in held
    name = model if matched else max(
        held, key=lambda k: (held[k].spill, held[k].size))
    one = held[name]
    return {"model": name, "size": one.size, "size_vram": one.size_vram,
            "spill": one.spill, "num_ctx": one.num_ctx, "matched": matched}


def measured_of(held: dict[str, Resident] | None, name: str) -> dict:
    """
    The `fit_of` keywords for one model's measurement, or `{}` for none.

    One place builds the pair, so the plan's table and the recommendation
    beside it cannot answer from different evidence. A model the card does
    not hold has no measurement, and the metadata answers.
    """
    one = (held or {}).get(name)
    if one is None or not one.size:
        return {}
    return {"loaded_bytes": one.size, "loaded_ctx": one.num_ctx or None}


def spill_line(seen: dict | None) -> str:
    """
    One plain line for a spill row, or "" when nothing was read.

    The night is headless, so this line is the only place an operator sees
    the card. It names both windows when they differ, because a pin that
    never reached the server is the fault a profile file cannot disprove.
    Pure: the caller reads the row, and this writes the sentence.
    """
    if not seen:
        return ""
    if not seen.get("seen"):
        return f"CARD UNSEEN {seen.get('endpoint')}: /api/ps did not answer"
    gb = 1 << 30
    pinned, given = seen.get("num_ctx"), seen.get("allocated_ctx")
    # The mismatch is named only when both windows are known. A row for
    # another model carries neither, because a swap must not manufacture
    # this alarm.
    if pinned and given and given != pinned:
        window = f"{pinned} PINNED but {given} GIVEN"
    elif pinned or given:
        window = f"{pinned or given}"
    else:
        window = "an unstated window"
    state = "SPILLS" if (seen.get("spill") or 0) > 0 else "FITS"
    whose = "" if seen.get("matched", True) else ", another desk's model"
    return (f"CARD {state} {seen.get('model')} at {window}: "
            f"{(seen.get('size') or 0) / gb:.2f} GB resident, "
            f"{(seen.get('spill') or 0) / gb:.2f} GB in RAM{whose}")


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
           loaded_bytes: int | None = None, loaded_ctx: int | None = None) -> Fit:
    """Weights plus KV cache at `num_ctx`, against VRAM then RAM. `resident`
    is how many such models are loaded at once. Ollama keeps one resident
    and swaps at each role change (measured 2026-09-11: /api/ps shows one
    model at a time), so the default is one; a server that keeps two needs
    the set, which is the open question the plan names.

    `loaded_bytes` is a measurement from `/api/ps`, and `loaded_ctx` is the
    window the server loaded at. Pass both and the fit answers for any
    window, even when the metadata gives no KV size. Pure: it reads no
    server, so the caller passes what `loaded()` returned."""
    kv = kv_cache_bytes(model.meta, num_ctx) if model.meta else None
    weights = model.size_bytes
    if kv is None and loaded_bytes and weights and loaded_ctx:
        # The metadata cannot always give a KV size: qwen3.5:9b reports no
        # `head_count_kv`, so the need was the weights alone and every
        # window passed by construction. What the server loaded above the
        # weights is the cache at the window it loaded at, and the cache is
        # linear in the window, so the measurement gives the missing size.
        kv = max(0, loaded_bytes - weights) * num_ctx // loaded_ctx
    if weights is None and loaded_bytes is None:
        return Fit(model.name, model.provider, "unknown", None, kv, None, None)
    # A loaded model's own size is the measurement; arithmetic is the
    # estimate. The measurement holds for one window only, so it answers
    # here only while nothing gives the cache at the window asked about.
    one = loaded_bytes if (kv is None and loaded_bytes) else (weights or 0) + (kv or 0)
    need = one * max(1, resident)
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
              groups: list[str], num_ctx: int = 12288, resident: int = 1,
              held: dict[str, Resident] | None = None) -> dict[str, Fit | None]:
    """One model per capability group: the best-scoring recorded model that
    fits, else the best that spills. Unrecorded models are shown by the
    caller, never ranked here.

    `held` is what `loaded()` returned, and each model's fit reads its own
    row. Without it the pick answered from the weights alone while the plan
    beside it answered from the measurement: gemma3:12b showed `spills` at
    11.76 GB in the table and `in_vram` at 8.20 GB in the recommendation
    (observed by the diff review of frame 43, 2026-09-19)."""
    scored: dict[str, dict[str, float]] = {}
    for b in benchmarks:
        # One recorded case is not a ranking. The first table put qwen3.5:4b
        # first on two desks on the strength of one case each.
        if int(b.get("cases", 3) or 0) < 3:
            continue
        scored.setdefault(b["capability"], {})[b["model"]] = float(b["score"])
    fits = {m.name: fit_of(m, sys_, num_ctx, resident,
                           **measured_of(held, m.name)) for m in found}
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


def pull(provider: Provider, model: str, progress=None) -> dict:
    """The one side effect (plans/model-setup.md, step 8). Ollama pulls with
    streamed progress, `progress(status, completed, total)` per line. A
    llama.cpp server has no pull: the answer names the model and says found
    or not found on its endpoint. A remote provider has no pull. Never a
    guessed folder."""
    if provider.kind == "ollama":
        req = urllib.request.Request(f"{provider.endpoint}/api/pull",
                                     data=json.dumps({"model": model, "stream": True}).encode(),
                                     headers={"Content-Type": "application/json"})
        last: dict = {}
        with urllib.request.urlopen(req, timeout=3600) as resp:
            for raw in resp:
                try:
                    last = json.loads(raw.decode("utf-8"))
                except ValueError:
                    continue
                if progress:
                    progress(last.get("status", ""), last.get("completed"), last.get("total"))
                if last.get("error"):
                    return {"model": model, "pulled": False, "error": last["error"]}
        return {"model": model, "pulled": last.get("status") == "success", "status": last.get("status", "")}
    if provider.remote:
        return {"model": model, "pulled": False, "error": "a remote provider serves what it serves; nothing to pull"}
    served = {m.name for m in models(provider)}
    return {"model": model, "pulled": False,
            "found": model in served,
            "note": ("served by this endpoint" if model in served else
                     "not found on this endpoint; place the file where the server expects it and restart it")}

