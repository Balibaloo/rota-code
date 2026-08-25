"""The model bench: speed, discipline and judgement, on anyone's machine.

Every fixture is a snapshotted view with mechanical scoring -- no checkouts,
no databases, no network beyond the local model server. The batteries can
fail, on purpose: the challenge set contains a claim whose correct verdict
is a break (the plant), and a harness whose scores cannot reach zero is a
harness being trusted rather than used.

    python -m probes.bench.run --models llama3.1:8b,qwen2.5:14b
    python -m probes.bench.run --models qwen3:8b --pull

The report, per model: does it fit the GPU (the single number that dominates
everything -- a model 2GB over VRAM decodes at one twentieth the speed),
prefill and decode rates, what those equate to in onboarding wall-time, a
discipline score (did it act in the shapes the system parses), and judgement
scores per capability (frame, senses, verdicts) so per-task routing falls
out of the same table.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from probes.downstream import default_backend  # noqa: E402
from rota.llm.llm import Pins  # noqa: E402

HERE = Path(__file__).parent
# The measured per-turn profile of a real onboarding: ~4k tokens in, ~300
# out, ~1.5 turns per session; sessions ~= 5 + 2*areas + words + surfaces
# + challenge cap. See ONBOARDING.md.
TURN_IN, TURN_OUT, TURNS_PER_SESSION = 4000, 300, 1.5
SIZES = {"small (5 areas)": 60, "medium (23 areas)": 105, "large (100 areas)": 250}


def measure_speed(backend, model: str, nothink: str = "") -> dict:
    pins = Pins(model=model, temperature=0.0, num_ctx=12288)
    # Warm the model first: the first call pays the load, which is not a
    # property of the model's speed.
    backend.complete(nothink + "Reply: ok", "ok?", pins)
    filler = ("The quick brown fox jumps over the lazy dog. " * 400)
    t0 = time.time()
    backend.complete(nothink + "Answer with the single word: done.", filler, pins)
    prefill_s = time.time() - t0
    prefill_rate = (len(filler) / 4) / max(prefill_s, 0.01)

    t0 = time.time()
    got = backend.complete(
        nothink + "You are a counting machine.",
        "Count from 1 to 120 as plain comma-separated numbers, nothing else.",
        pins)
    decode_s = time.time() - t0
    out_toks = max(len(got.text) / 4, 1)
    decode_rate = out_toks / max(decode_s, 0.01)
    return {"prefill_tok_s": round(prefill_rate),
            "decode_tok_s": round(decode_rate, 1)}


def gpu_fit(model: str) -> str:
    try:
        ps = subprocess.run(["ollama", "ps"], capture_output=True, text=True,
                            timeout=15).stdout
        for line in ps.splitlines():
            if line.split() and model.split(":")[0] in line.split()[0]:
                if "100% GPU" in line:
                    return "fits fully"
                m = re.search(r"(\d+)%/(\d+)% CPU/GPU", line)
                if m:
                    return f"partial offload ({m.group(2)}% GPU)"
        return "unknown"
    except Exception:
        return "unknown"


def turn_seconds(speed: dict) -> float:
    return TURN_IN / max(speed["prefill_tok_s"], 1) \
        + TURN_OUT / max(speed["decode_tok_s"], 0.1)


def score_frame(completion: str, truth: dict) -> tuple[int, int]:
    answers = {}
    for line in completion.splitlines():
        m = re.match(r"\s*(?:[-*\d.]+\s*)?`?([^\s:`]+?)`?\s*:\s*"
                     r"\**(program|attached|attach|ignore|boundary|surface)\**",
                     line, re.I)
        if m:
            k = m.group(2).lower()
            answers[m.group(1).strip("`*-").rstrip("/")] = (
                "attached" if k == "attach" else
                "boundary" if k == "surface" else k)
    hit = sum(1 for path, allowed in truth.items()
              if answers.get(path) in allowed)
    return hit, len(truth)


def score_define(completion: str, truth: dict) -> tuple[int, int]:
    low = completion.lower()
    m = re.search(r"sense_short\s*=\s*[\"']([^\"']+)", completion)
    sense = (m.group(1) if m else completion[-400:]).lower()
    trapped = any(t.lower() in sense for t in truth["must_not_contain"])
    disciplined = "glossary.amend" in low
    return (0 if trapped else 1) + (1 if disciplined else 0), 2


def score_challenge(completion: str, truth: dict) -> tuple[int, int]:
    low = completion.lower()
    said = ("falsified" if "challenge.break" in low else
            "unfounded" if "challenge.dismiss" in low else
            "stands" if "challenge.uphold" in low else "none")
    return (1 if said == truth["expected_verdict"] else 0), 1


def score_recover(completion: str, truth: dict) -> tuple[int, int]:
    """The single most predictive discipline trait measured in the live
    runs: shown its own refused call, does the model change the call?"""
    differs = truth["must_differ_from"] not in completion
    engages = any(t.lower() in completion.lower()
                  for t in truth["must_contain_any"])
    return (1 if differs else 0) + (1 if engages else 0), 2


def score_read(completion: str, truth: dict) -> tuple[int, int]:
    text = completion.strip()
    pts = tot = 0
    if "must_start" in truth:
        tot += 1
        pts += 1 if text.upper().startswith(truth["must_start"]) else 0
    if "must_not_start" in truth:
        tot += 1
        pts += 0 if text.upper().startswith(truth["must_not_start"]) else 1
    if "must_contain_all" in truth:
        tot += 1
        pts += 1 if all(t.lower() in text.lower()
                        for t in truth["must_contain_all"]) else 0
    if "must_contain_any" in truth:
        tot += 1
        pts += 1 if any(t.lower() in text.lower()
                        for t in truth["must_contain_any"]) else 0
    return pts, tot


def score_decline(completion: str, truth: dict) -> tuple[int, int]:
    low = completion.lower()
    honest = any(t.lower() in low for t in truth["must_contain_any"])
    restrained = not any(t.lower() in low for t in truth["must_not_contain"])
    return (1 if honest else 0) + (1 if restrained else 0), 2


def score_orient(completion: str, truth: dict) -> tuple[int, int]:
    low = completion.lower()
    named = any(t.lower() in low for t in truth["must_contain_any"])
    acted = all(t.lower() in low for t in truth["must_contain_all2"])
    return (1 if named else 0) + (1 if acted else 0), 2


SCORERS = {"frame": score_frame, "define": score_define,
           "challenge": score_challenge, "recover": score_recover,
           "read": score_read, "decline": score_decline,
           "orient": score_orient}


def evict_others(model: str) -> None:
    """One candidate on the card at a time. Measured without this: granite
    benched at 92% GPU because the previous model was still resident, and
    every fit and speed column after the first was polluted."""
    try:
        ps = subprocess.run(["ollama", "ps"], capture_output=True, text=True,
                            timeout=15).stdout
        for line in ps.splitlines()[1:]:
            name = (line.split() or [""])[0]
            if name and name != model:
                subprocess.run(["ollama", "stop", name], capture_output=True,
                               timeout=30)
    except Exception:
        pass


def run_model(backend, model: str) -> dict:
    evict_others(model)
    # qwen3-family models reason by default; the hidden tokens sank the 4b
    # to 0.1 tok/s and unparseable answers. The bench measures the acting
    # register, so thinking is disabled where the template understands it.
    nothink = "/no_think\n" if model.startswith(("qwen3", "qwen3.5")) else ""
    pins = Pins(model=model, temperature=0.0, num_ctx=12288)
    speed = measure_speed(backend, model, nothink)
    fit = gpu_fit(model)
    cases = [fx for fxfile in sorted(HERE.glob("fixtures/*.json"))
             for fx in json.loads(fxfile.read_text(encoding="utf-8"))]
    print(f"  {fit}, ~{turn_seconds(speed):.0f}s a turn: "
          f"{len(cases)} cases, roughly "
          f"{len(cases) * turn_seconds(speed) / 60:.0f} min", flush=True)
    per_kind: dict[str, list[int]] = {}
    for n, fx in enumerate(cases, 1):
        started = time.time()
        got = backend.complete(nothink + fx["system"], fx["user"], pins).text
        hit, total = SCORERS[fx["kind"]](got, fx["truth"])
        per_kind.setdefault(fx["kind"], [0, 0])
        per_kind[fx["kind"]][0] += hit
        per_kind[fx["kind"]][1] += total
        print(f"    {n:2d}/{len(cases)}  {fx['id']:32s} {hit}/{total}"
              f"  {time.time() - started:5.1f}s", flush=True)
    ts = turn_seconds(speed)
    times = {name: round(n * TURNS_PER_SESSION * ts / 60)
             for name, n in SIZES.items()}
    return {"model": model, "fit": fit, **speed,
            "turn_s": round(ts, 1), "onboarding_minutes": times,
            "scores": {k: f"{v[0]}/{v[1]}" for k, v in per_kind.items()}}


def render(results: list[dict]) -> None:
    for r in results:
        print(f"\n=== {r['model']}")
        print(f"  fit: {r['fit']}   prefill {r['prefill_tok_s']} tok/s   "
              f"decode {r['decode_tok_s']} tok/s   turn ~{r['turn_s']}s")
        print("  onboarding: " + "   ".join(
            f"{k}: ~{v}min" for k, v in r["onboarding_minutes"].items()))
        print("  judgement: " + "   ".join(
            f"{k} {v}" for k, v in sorted(r["scores"].items())))
    print("\n(the challenge battery contains a planted falsehood; a model "
          "that upholds everything scores low there BY DESIGN -- a battery "
          "that cannot fail proves nothing)")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", required=True,
                    help="comma-separated ollama model names")
    ap.add_argument("--pull", action="store_true",
                    help="ollama pull models that are not local (asks sizes "
                         "first is the seat's job; here it just pulls)")
    args = ap.parse_args(argv)
    backend = default_backend()
    results = []
    for model in [m.strip() for m in args.models.split(",") if m.strip()]:
        if args.pull:
            subprocess.run(["ollama", "pull", model], check=False)
        print(f"benching {model} ...", flush=True)
        results.append(run_model(backend, model))
    render(results)
    return 0


if __name__ == "__main__":
    sys.exit(main())
