# Where this is, and what is next

Written down because the failure list is the working document now, and it is
the thing a fresh session would otherwise re-derive by running everything.

Regenerate the numbers with `python -m rota.cockpit.server` and the **progress**
tab, or `node tests/rota/lens_check.js` for the viewer.

---

## Green

| | |
|---|---|
| deterministic suite | **258 passed**, 6 skipped, ~4½ min |
| cases | **59** across 13 files |
| prompt modes with a case | **48 / 48** |
| L1 actions covered | 44 / 117 *(credited by side-effect, generous)* |
| L2 situations covered | **48 / 48** |
| L3 handoff pairs | 4 / 24 |
| last run | **37/54** L1-L2, **2/5** L3, 13 min |

Onboarding is built end to end: tree-sitter index over 7 languages, dependency
edges, area partitioning, constraint zero, 15 tests.

The cockpit has three tabs (graph · live · progress), five lenses on one canvas,
a case browser with per-run transcripts, and a six-colour semantic palette
documented at the top of `graphview.js`.

---

## The machine facts, so they are not re-measured

* **RTX 3080, 10 GB VRAM. 32 GB RAM.**
* `llama3.1:8b` is the only viable local model. 4.9 GB, 0.2s warm, fits entirely
  in VRAM at `num_ctx=12288`.
* `qwen3.5:9b` has native tool calling but spills ~27% to CPU at 8k and takes
  >100s a turn. `gemma4:31b` needs ~20 GB and swaps the machine.
* **12288, not 8192.** Pushing the full working set put the largest prompts at
  ~9.2k tokens; at 8192 they were silently truncated *from the front*, which is
  where the system prompt is. Ollama's `prompt_eval_count` is now checked
  against the window and an overflow is reported as a session error.
* Never unload a model with a request that names it — `/api/generate` loads the
  model in order to serve the request, including one whose only purpose is
  `keep_alive: 0`. Kill the runner process instead.

---

## The 20 failures — the working list

Every one has a transcript in the cases panel. The job is to classify each as
**unfair case** / **under-briefed role** / **model out of depth**, which is the
first time that has been answerable from evidence rather than by inference.

### Tester writes nothing — 4 cases, one root cause?

    L1-TS-encode-a-criterion              0/5   expected writes to tests, got 0
    L1-TS-apply-a-term-and-write-the-test 0/5   expected writes to tests, got 0
    L1-TS-fix-a-test-that-asserts-more…   0/5   expected writes to tests, got 0
    L1-TS-hold-a-test-that-is-right       0/5   forbidden write to tests

Four of Tester's five cases. The signature was cleared of suspicion once —
`tests.encode(id, criterion_id, path, body, batch_id=None)` is correct — so
this is the largest single cluster and the first to look at.

### The survey trio — 3 cases, never passed

    L1-TE-survey-an-area-for-its-terms     0/5   no code.source, no attestation
    L1-AR-survey-an-area-for-its-commit…   0/5   no survey_records written
    L1-GK-survey-an-area-for-what-it-does  0/5   no code.source

All three open by consulting their own artefact and stopping. They now wake
holding the area's 17 grains, so the fixture is not the problem.

### The ladder — 3 cases, brand new, never tuned

    L1-AR-route-an-escalation              0/5   reported to liaison instead
    L2-AR-place-a-block-developer-could…   0/5   answered developer instead
    L2-GK-end-it-rather-than-send-it-back   0/5   sent nothing at all

### Liaison — 3 cases

    L1-LI-put-a-contradiction-back-unres…  0/5   no clarify to principal
    L1-LI-put-the-open-assumptions-to-a-…  0/5   message sent without its refs
    L1-LI-nothing-came-back-so-nothing-…   0/5   presented when silence was right

### Developer — 3 cases

    L1-DV-apply-the-answer-and-carry-on    0/5   asked again instead of building
    L1-DV-fix-the-code-not-the-test        0/5   challenged instead of fixing
    L1-DV-log-the-choice-the-criteria-…    0/5   built it, logged nothing

### Gatekeeper — 1 case

    L1-GK-amend-a-contested-item           0/5   no amendment written

### L3 — 3 of 5 chains

    L3-scope-becomes-a-ticket-with-criteria
    L3-a-challenge-reaches-the-role-that-can-answer-it
    L3-a-failed-verdict-turns-into-a-fix        ← was hitting the repo leak;
                                                  re-run before trusting it

Passing: `ratified statement → scope` and `ratified statement → term`. Those two
are the design's central bet holding — a message carrying only refs was enough
for a cold stranger to act.

**Every failure is 0/5.** Not one is stochastic. These are systematic, which is
the most useful property the list has.

---

## Next, in order

1. **Re-run L3** now the checkout leak is fixed, so its three failures are
   trustworthy.
2. **Classify all 20 from their transcripts.** Fix what is under-briefed, correct
   what is unfair, record what is beyond an 8B with the reason written down.
3. **Extend L3** once the vocabulary claim has been tested properly. 4 of 24
   pairs, and it is the tier the whole design rests on.

## Still genuinely unbuilt

**3Bd — environment lifecycle.** Law 9's *"processes and ports die with it;
half-dead environments are forbidden"* has no implementation. Nothing spawns a
process, so nothing can orphan one. Deliberately deferred, not forgotten.

## Habits worth keeping

* `node tests/rota/lens_check.js` before trusting the viewer. `node --check`
  passes a call to a function that was never written; this does not.
* Assert the anchor matched before a scripted edit. Three silent `str.replace`
  no-ops today, one of which shipped exactly that broken reference.
* A pass rate says a case is failing. Only the transcript says whether the case
  was unfair, the role under-briefed, or the model out of its depth.
