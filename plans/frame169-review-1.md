# Frame 169 review of eb0649eb, Opus, 2026-10-11 09:17

The reviewer's report, from `rv169/report.md` under session be3ef742's scratchpad. 50.1k on the harness line against 40k. Probes `C:/Users/roman/rota_r195p1/scratch/p169.py` and `p169b.py`. Rota workflow.

# Review of frame 169, pass 1, commit eb0649eb

Worktree: C:/Users/roman/rota_r195p1, detached at eb0649eb.

## (a) Verdicts

1. True in both shapes. The span that stands keeps the pointer. The span that is gone gets the served-again line. A partly cut span is repointed only when the eviction note is in the prompt (finding 2).
2. The at-cap sentence is true, and the code path reaches it. The probe called `_repoint` directly. A full scripted session at the cap was not built.
3. An older refusal keeps "The answer is in this prompt." after a later fit drops its answer. This is the same fault class that frame 169 names, at a second distance. Pass 1 does not close it (finding 1).

## (b) Findings

1. rota/core/runner.py:3393-3394, low. CONFIRMED by probe F. `pointers.clear()` runs after one fit, so `_repoint` checks a refusal only once. A refusal from turn N still says "The answer is in this prompt." at turn N+2 when that fit drops the answer. The next asking is still served, because `evicted` at line 3879 is true. So the false line costs the seat a confused read and no lost answer. Fix: keep each pointer until its line or its answer leaves the transcript, and check it after every fit.

2. rota/core/runner.py:723, low. PLAUSIBLE. Probe E confirms the unit behaviour. Session reach is not probed. `_repoint` returns early when `_EVICTED_PHRASE` is absent. An answer that `_exchange_cut` cut at its own turn, or a wake cut by `_render_cut`, is partly gone with no note. The line then keeps "The answer is in this prompt." over a partial answer. The loop's `evicted` uses the same guard, so the next asking is refused too, and the cut note says "Call again what you still need". This shape existed before frame 169, and the frame does not name it. Fix: open a separate frame, and do not widen pass 1.

No high finding survived a probe.

Checked and clean:
- `_repoint` and `evicted` at line 3879 use the same three tests. The only difference is `answered_at < iteration`, and that test is true at the next turn. So the under-cap promise holds: the next asking takes the serve branch at line 4073.
- At the cap, the next asking meets the serve-cap refusal at line 3921. That refusal gives the same step that the repointed line gives.
- The at-cap refusal at line 3962 is reachable. After three serves, the served block holds `shown`, `evicted` is false, and `repeated` is at least 1.
- A key that a write cleared from `answered` is skipped. The skipped line stays unchanged.

## (c) Probes

- `C:/Users/roman/rota_r195p1/scratch/p169.py` calls `_repoint` on built transcripts. A: gone and under the cap gives the served-again line. C: the answer stands, so the line is unchanged. D: partly cut with the note gives the served-again line. E: partly cut with no note leaves the line unchanged. F: an older line with no pointer is unchanged. B crashed on a stub `sb`, and p169b replaces B.
- `C:/Users/roman/rota_r195p1/scratch/p169b.py` sets `_bound_of` to a stub and runs `_repoint` at served=3. With a bound: "...and it was served three times. Ask code.source for a narrower span, or finish without it." With no bound: "...Act without it, or finish."
- pytest `tests/rota/test_runner.py -k "repeat_refusal_says or keeps_its_pointer or serve_cap"` with qwen3:8b: 4 passed in 3.74s. These tests are the scripted s159 shapes at 8,192 and 12,288.
- The full gate did not run. No point needed it.

## (d) Usage

About 30k input tokens and 6k output tokens, about 36k in total. This is an estimate. Read the harness line for the exact count.

Verdict: stands. Findings: 0 high, 2 low.
