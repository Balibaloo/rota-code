# Frame 237, passes 1c to 1e: review 3 of 91d681c0

Rota workflow. Read-only review on the worktree `C:/Users/roman/rota_rv237c` at 91d681c0, over 872c44b1. Reviewer: Opus, 2026-10-14.

Verdict: the commit stands. 0 high, 3 low. All three points hold.

## (a) Verdicts

1. The dropped expectation: holds. Both recorded pages show every file of `src/billing` whole, with no cut sign.
2. The history: holds. No ruling holds a survey count. The ceiling of three was a case author's bound from 2026-08-27.
3. The brief sentence: holds. "Record at most five words." is STE, and it does not contradict the "two beats eight" sentence.

## Point 1. The dropped expectation

The cassette table holds two rows whose system text carries "Record at most five words." and whose user text carries `[code.area]` (observed: 2026-10-14, probe P1). Row `5e9d9027`, the survey case, user 4351 characters, shows six own files. Row `0caf8f7e`, the resurvey case, user 4706 characters, shows seven own files, `proration.py` among them. Each row also shows `src/store/__init__.py` and `src/catalog/pricing.py` as imports. The sample repository, `rota/testkit/samplerepo.py:340-455`, defines the same six files under `src/billing`. In both pages the counts of "first part only", "not_shown", "not shown", "CUT" and "code.source" are 0. So no `code.source` read is owed on either case. Both completions carry 5 `glossary.amend(` calls.

The signs that `code_area` (`rota/roles/api.py:10411-10612`) writes when it leaves a file out:

- A file cut to its head carries the label suffix " (first part only)". An own file that does not fit whole gets this label, and the first omitted file can get it too.
- A file left out entirely goes to `omitted`, and the result then carries a `not_shown` key. Its text comes from `cut_note` (`rota/core/runner.py:700-717`): "CUT this area's files: N of M files are not shown. `code.source` any of ... if the ones above leave a word unexplained."
- A cut own head does not enter `omitted`. So a page can show "(first part only)" with no `not_shown` key. Search for both signs.

## Point 2. The history

`git log -S "0..3"` on the case file names bd761809 (2026-08-27, "every red attributed"). That commit created `L1-TE-resurvey-an-area-that-moved` as Loop 5's case, with `glossary_terms: {count: "0..3"}`. The commit gives no reason for three. The case comment says only that a term is "plausible but not owed". This predates the frame numbers. `git log -S "stays"` names 9fad96a4 (2026-09-13, "four reds re-earned"). That commit attributed the 0/5 red and wrote that the ceiling "stays", because the criteria brief's "six is many" was not the resurvey's. That line is an attribution by the build session, not a ruling by Roman. The 89622a1d hit is the reconcile case's "the ceiling stays", which is a different case.

`rota/DECISIONS.md`, `rota/LAWS.md` and `plans/archive/` hold no count for the survey. The only count rulings near the Terminologist are for criteria: "three is usual and six is many" (`plans/archive/completion-diary.md:1276`, `rota/roles/prompts/terminologist/criteria.md:34`). The survey brief before a2344b87 had no count sentence. Frame 237 pass 1 wrote "Two to five words is the common count", and this commit made it a cap. So the cap of five crosses no ruling. None.

## Point 3. The brief sentence

"Record at most five words." is an imperative of five words, in the active voice, with one instruction. It is STE. "Word" keeps one meaning in the brief: a glossary term written as one `glossary.amend` call. The sentence "Two you have understood beats eight you have named." states a preference for quality over count. It does not set a count, so the cap does not contradict it. The "eight" now names a count the cap forbids. The contrast still reads as "fewer and understood", so it needs no edit.

## (b) Findings

1. `tests/rota/cases/l1_survey.yaml:31-33`. Low. CONFIRMED. The survey case comment says "the seat wrote four terms". The recorded completion `5e9d9027` carries 5 amend calls (probe P1). Fix: write "four, then five under the cap" or drop the number.
2. Outside the points. `tests/rota/cases/l1_survey.yaml`, both Terminologist survey cases. Low. CONFIRMED that no case covers the path. Probe P2 lists the only two Terminologist survey cases, and neither carries `calls`. Both pages show the area whole. So no case asserts the brief's `code.source` read for a cut area. The old `calls: [code.source]` never tested that path either, because the pages were whole. Fix: push a frame for a case on an area larger than the 10000-character budget, which expects `code.source` of an omitted file.
3. Outside the points. `rota/roles/api.py:10544-10551`. Low. PLAUSIBLE. A path that is not a file, or that fails to read, is skipped with no sign on the page. The seat then cannot know that a file is missing. The sample repository does not trigger this path. Fix: add such a path to `omitted`, so `cut_note` names it.

## (c) Probes

- P1: `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4a757f92-bd97-4750-9830-bd149134e576/scratchpad/rv237/p1_pages.py`. It opens `D:/repos/rota/tests/rota/cassettes.db` read-only (the worktree has no copy). It selects cassette rows with the new brief and a `[code.area]` page, lists the file labels and counts the cut signs and the amend calls. A second inline call counted "CUT" and "unexplained" in the same two pages: 0 each.
- P2: an inline `python -c` from the worktree that loads every `tests/rota/cases/*.yaml` and prints each Terminologist survey case with its `writes` and `calls`.
- A read-only query of `case_runs` for the two cases after 2026-10-14T22: green live runs at 22:35 to 22:36 and 23:11, green replays at 23:18 and 23:19.
- Git reads: `git show HEAD`, `git log -S` for "0..3", "stays", "0..4", "Two to five words" and the resurvey case id, and `git show` of bd761809, 9fad96a4 and 89622a1d. Greps of `rota/DECISIONS.md`, `rota/LAWS.md`, `plans/archive/` and the briefs.

No gate, no model, no re-record. No tracked file was edited.

## (d) Usage

Estimate from this context, because the harness line holds the exact figure: about 45k input tokens, about 6k output tokens, about 51k in all. This is over the 25k cap. Sub-agents: none.
