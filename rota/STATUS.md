# Where this is, and what is next

Written down because the failure list is the working document now, and it is
the thing a fresh session would otherwise re-derive by running everything.

Regenerate the numbers with `python -m rota.cockpit.server` and the **progress**
tab, or `node tests/rota/lens_check.js` for the viewer.

---

## Green

| | |
|---|---|
| deterministic suite | **276 passed**, 6 skipped, ~4½ min |
| cases | **59** across 13 files |
| prompt modes with a case | **48 / 48** |
| L1 actions covered | 44 / 117 *(credited by side-effect, generous)* |
| L2 situations covered | **48 / 48** |
| L3 handoff pairs | 6 / 24 |
| last run | **45/56** L1-L2, **4/6** L3, 27 min |

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

## The 13 failures — the working list

Down from 20, and the ones that went were almost all harness rather than model.
Found with `python -m rota.tools.triage --failing`, which groups by *mechanism*
so that one bug across five cases reads as one bug.

### Fixed, and what they turned out to be

    parse: `true` rejected as a syntax error          150 rejections, 2 cases
    parse: positional args refused by the parser       40, 2 cases
    parse: `TOOL:` read as a slot to fill in           the whole silent cluster
    parse: `text=...` became Python's Ellipsis         killed sessions at commit
    signature: `ledger.log(id=)` rejected 170 times    error now names about_ref
    working set: Terminologist could not read a term   `deliver` took lookup away
    fixture: Tester asked for a batch it never saw     derived from the criterion
    harness: a dict reaching SQLite killed a session   annotation now checked
    harness: **both suites pinned num_ctx=8192**       prompts clipped at the front
    unfair case: round_close with no reports           the predicate cannot fire it

### Still failing

    L1-AR-group-into-batches           session dies, FOREIGN KEY
    L1-AR-route-an-escalation          reported to liaison instead of escalating
    L1-AR-survey-an-area               writes two attestations where one is asked
    L1-DV-apply-the-answer-and-carry-on   asks again instead of building
    L1-DV-challenge-a-test…            calls code.write when it must not
    L1-DV-fix-the-code-not-the-test    challenges instead of fixing
    L1-DV-fix-what-the-verdict-names   questions the gatekeeper first
    L1-GK-amend-a-contested-item       writes nothing
    L1-LI-the-reports-came-back-clean  presents when silence is right
    L1-LI-two-questions…               a question sent without its ref
    L1-TS-hold-a-test-that-is-right    rewrites a test that was correct
    L3-scope-becomes-a-ticket-with-criteria     hop 1 sends nothing
    L3-a-failed-verdict-turns-into-a-fix        hop 1 sends nothing

Three of these are Developer refusing to write code and asking a question
instead, which is one behaviour and probably one fix. Two are Liaison speaking
when the right answer is silence. `blind:` counts in the triage output are
completions that committed after a read in the same breath — still the largest
single pattern.

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
