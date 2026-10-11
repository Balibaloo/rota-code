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


# The second look on ef96f550, pass 1b, Opus, 2026-10-11

From `rv169b/report.md` under session be3ef742's scratchpad. 41.7k on the harness line against 20k.

# Frame 169, pass 1b, review of ef96f550 (read-only second look)

## (a) Verdicts

1. Finding 1 closes. The turn N+2 shape and a turn N+3 shape both replace the sentence at the first fit that drops the answer.
2. One pointer outlives its truth. Two identical refusal lines at two turns get one pointer, and only the newest copy is replaced.
3. The brief names the wrong parent. 586730c1 is a child of ef96f550, so the test passes there. On the true parent 03bd6bd8 the new test is red.

## (b) Findings

1. rota/core/runner.py:735-760 and 4033-4037. Severity high. CONFIRMED.
   The append drops a duplicate pointer, and `_repoint` replaces the newest copy only. The older copy keeps "The answer is in this prompt." after the fit drops the answer.
   Probe B (session, num_ctx 11264): the seat asks `scope` four times. Turn 6 holds the evicted phrase and two lines. The older line still says "The answer is in this prompt." The newer line says "The window dropped the answer after this line".
   Probe C (unit on `_repoint`): two results blocks hold the same line. The call replaces block 3 only, block 1 keeps the false sentence, and the call returns [].
   Pass 1 at eb0649eb replaced the newest copy only too, so the defect is older than pass 1b (reasoned: same loop shape). Pass 1b drops the pointer after one replacement, so nothing corrects the older copy later.
   Fix: in `_repoint`, replace `line` in every `_RESULTS` block that holds it, not only the newest one.

2. Brief, point 3. Severity low. CONFIRMED.
   `git diff --stat 586730c1 ef96f550` shows only `plans/stack.md`. `git rev-parse ef96f550^` gives 03bd6bd8.
   Fix: name 03bd6bd8 as the parent in the stack's status line.

No other defect found on point 2:
- A line that leaves the transcript: `at is None` drops the pointer (read, and covered by the drop path in probe C).
- A sentence replaced once: the pointer leaves, so no second replace on the same pointer. Probe B and C show one replacement.
- A key served again: the filter at 4097-4101 drops the pointer. The old refusal block is older than the new render, and `_fit` drops older results first inside a tier. A later fit that drops the new render keeps the old refusal only by a tier order I did not probe (reasoned, PLAUSIBLE no defect).

## (c) Probes

All probes sit in `C:\Users\roman\AppData\Local\Temp\claude\d--repos-rota\be3ef742-9693-403c-954a-e176c4f04746\scratchpad\rv169b\`. All ran from the worktree `C:/Users/roman/rota_r195p1` at ef96f550, with ROTA_MODEL=qwen3:8b. No model was called.

- `test_probe169b.py::test_n3` (probe A): refusal at turn 3, a small read at turn 4, `billing` at 5, `ledger` at 6. The line says "in this prompt" at turns 4 to 6 with no eviction. Turn 7 holds the eviction and the replaced line. Finding 1 of review 1 closes at N+3.
- `test_probe169b.py::test_n2_twice_refused` (probe B): finding 1 above.
- `test_probe169b.py::test_dup_unit` (probe C): `_repoint` on two copies of one line. Finding 1 above.
- `tests/rota/test_runner.py -k repeat_refusal` at ef96f550: 4 passed.
- `parent/`: `git archive 586730c1` with the test file of ef96f550. The new test passes, because 586730c1 holds the change.
- `p2/`: `git archive 03bd6bd8` with the test file of ef96f550. `rota.core.runner` loads from `p2`. The new test fails at the last assertion: the line keeps "The answer is in this prompt." Its two setup assertions hold, so the shape is real on the parent.
- Note: a first run of `test_probe169b.py` without `-k` also collected all of `test_runner.py` through the star import. It ran in the background and changes nothing.

## (d) Usage

About 38k tokens in total, over the 20k cap. Input about 33k, output about 5k (estimate from the context count, not from the harness).

One more pass: 1 high, 1 low.
