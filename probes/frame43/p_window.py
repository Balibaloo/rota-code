"""
What a model costs at a window, and whether it spills, read from Ollama.

Frame 43, ends-when line 1. The window rises to 16384 for every wake, and
Roman's ruling of 2026-09-19 buys the evidence that it is not spilling.

The method is section 8's: send a one-token generate at the window, then read
`/api/ps`. Ollama reports `size` and `size_vram` per loaded model. The
difference is the spill, in bytes. No instrumentation of the model path is
needed.

`/api/ps` also reports `context_length`, which is the window the server
actually allocated. Read that, never the window you asked for.

Read the card the run uses. The Titan measures about double these numbers,
because it runs at two slots and allocates a KV cache for each.

Usage:

    python probes/frame43/p_window.py                     # the night's two models at 16384
    python probes/frame43/p_window.py 12288 16384 20480   # one model at three windows
    OLLAMA_HOST=http://127.0.0.1:11435 python probes/frame43/p_window.py

Set ROTA_PROBE_MODELS to a comma-separated list to measure other models.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request

HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MODELS = [m for m in (os.environ.get("ROTA_PROBE_MODELS")
                      or "qwen3:8b,qwen3.5:9b").split(",") if m]
GB = float(2 ** 30)


def _post(path: str, body: dict, timeout: float = 600.0) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(f"{HOST}{path}", data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _get(path: str, timeout: float = 10.0) -> dict:
    with urllib.request.urlopen(f"{HOST}{path}", timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def measure(model: str, num_ctx: int) -> dict | None:
    """One token at `num_ctx`, then what the server holds. None if it holds
    nothing for this model, which means the load failed."""
    _post("/api/generate", {"model": model, "prompt": "hi", "stream": False,
                            "think": False,
                            "options": {"num_ctx": num_ctx, "num_predict": 1}})
    for m in _get("/api/ps").get("models") or []:
        if m.get("name") == model or m.get("model") == model:
            size, vram = int(m.get("size") or 0), int(m.get("size_vram") or 0)
            return {"size": size, "vram": vram, "spill": size - vram,
                    "ctx": m.get("context_length")}
    return None


def main(argv: list[str]) -> int:
    windows = [int(a) for a in argv[1:]] or [16384]
    print(f"host {HOST}")
    print(f"{'model':22} {'asked':>7} {'ctx':>7} {'size':>8} {'vram':>8} {'spill':>8}")
    for model in MODELS:
        for num_ctx in windows:
            row = measure(model, num_ctx)
            if row is None:
                print(f"{model:22} {num_ctx:>7} {'-':>7} {'not loaded after the generate':>26}")
                continue
            print(f"{model:22} {num_ctx:>7} {row['ctx'] or 0:>7} "
                  f"{row['size'] / GB:>7.2f}G {row['vram'] / GB:>7.2f}G "
                  f"{row['spill'] / GB:>7.2f}G")
    print("\nA second model evicts the first on a 10 GB card. Read one row at a time.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
