# Frame 246, review 1 of 401bbf3f: the gap note carries words and no raw tick key

Verdict: accept with one fix owed before the frame closes. The diff removes the raw key from every fact the nights showed. The test is red at the parent for the right reason. One latent leak remains: the README reconcile key renders as `@prose`. The re-recorded case changed its reply from `found` to `none_found`. Reviewer: Opus, read-only, worktree `C:/Users/roman/rota_r246` at 401bbf3f, 2026-10-15. Meta workflow.

## (a) Verdicts on the points

1. The words: partly. "settling the boundary of" and "comparing the account with" use rota terms. "checking the claim" holds. See finding 2.
2. The constraint-zero line: nothing is lost. No test and no recorded case expects the old line.
3. Reach: only the blindspot facts change. No reader parses `given up after the attempt bound:` or `-|tick:`.
4. `ORDER BY tick_key`: rows now win by role name, so `vision_keeper` rows lose first. No night page changed by it.
5. The test: red at the parent on the `tick:` assertion, green at 401bbf3f, 0 CR bytes.
6. The re-recorded case: the reply changed. It attests `none_found` now, and it attested `found` before.
7. Night 149 must count the blindspot session's `gap` notes and their outcome, beside the ratio line.

## (b) The answers

### 1. The words

The quarantine means that the scheduler gave up on one onboarding task after three attempts (`rota/core/scheduler.py:2267`). The key is `role|tick:kind|refs`. The three kinds the nights showed mean these things.

- `boundary`: the Architect reads one file that an outside party touches, a manifest or an authoring surface, and decides whether it sets a rule (`boundary_subjects`, `scheduler.py:1173-1187`). "settling the boundary of .readthedocs.yaml" does not say that to a newcomer. "Boundary" is a rota word. Propose: "reading .readthedocs.yaml for the rules it sets for outside users".
- `challenge`: the Critic tests one load-bearing claim, a constraint, an item, a term or an area (`challenge_subjects`, `scheduler.py:1230-1249`). "checking the claim click_paramtype" holds. The id drops its table, so a person cannot tell a rule from a request line. Propose, low: "checking the rule click_paramtype" for `constraints`, and "checking the request line ..." for `items`.
- `reconcile`: the Vision Keeper compares one prose file with the account that the team built from the code (`_reconcile_wakes`, `scheduler.py:680-708`). "the account" is a rota word. Propose: "checking docs/parameters.md against what the team learned from the code".
- The README area is `@prose` with no colon. The ref rule keeps `@prose` whole, so the fact shows `@prose` (finding 1).
- `survey` and every other kind fall back to "work on". "work on src/store" holds for a person.

### 2. The constraint-zero line

`render_state` has filtered the same key since 865db3e6 (`rota/roles/principal.py:409-410`), and `_stalled_keys` filters it too (`principal.py:1165`). The constraint-zero predicate is scheduler bookkeeping: "Nobody's judgement" (`rota/core/predicates.py:1789-1818`). An area that is still unread keeps its own `tick:survey` quarantine, and that row still gives a fact in words. So the facts lose nothing a person can act on. A search of `rota`, `tests` and the case YAML for `attempt bound: ` and `given up after` found no expectation of the old line.

### 3. Reach

The change touches `code_gaps` only. Its one consumer is the blindspot session of the Liaison, through `code.gaps`. The Liaison copies a fact into a `ledger.log` note of kind `gap`, and `render_page` prints the note as it is (scope report, line 16). No code reads the text of a `gap` note back, and no code parses `-|tick:` out of a note. The other routes of the key to the principal are outside this diff (findings 4 and 5).

### 4. `ORDER BY tick_key` and the six-row limit

Before the diff, the query had no order, so SQLite returned the rows in rowid order: the first six quarantines won. Now the rows sort by the key, which starts with the role. So `architect` and `critic` rows win, and `vision_keeper` rows lose first. The probe with eight rows dropped both reconcile rows (probe 1). Over the 72 night databases in `D:/repos/rota/.rota`, no database holds more than six quarantined keys outside constraint zero (probe 3). So no night page changed by the order. The order is stable. The bias toward the alphabet is a design choice that nobody ruled (finding 3).

### 5. The test

The new test fails at 401bbf3f~1 on the first assertion. The facts hold `given up after the attempt bound: -|tick:constraint_zero|` and the boundary key (probe 4). That is the right reason. At 401bbf3f, the new test and the blindspot test pass, 2 passed. `git show 401bbf3f` holds 0 CR bytes, and `api.py` at the commit holds 0.

### 6. The re-recorded case `L1-LI-say-what-the-run-could-not-see`

The reply changed (observed: `case_runs` in `D:/repos/rota/tests/rota/cassettes.db`, read-only, 2026-10-15).

- Before, seq 487221 at 14:20:45: the seat put the raw key into `about_ref`, `@terminologist|tick:survey|src/store`, and the door refused it. The seat wrote one glossary note about `@program` and attested `found`.
- After, seq 488411 at 14:48:40: the seat wrote the store fact in words, `about_ref="@src/store"`, and the door took it. The seat tried the glossary note three times on `@glossary`, and the door refused each. The run carries the error `wrote its own tool results`. The seat attested `none_found` and said both gaps are "not worth a ruling".

Both runs pass, because the case expects one `survey_records` row only. The quarantine fact now reaches the ledger, and it did not before. The outcome flip shows that the seat can now judge the words as "a technical failure" and attest that nothing matters.

### 7. What night 149 read must count

Count the `gap` notes of the blindspot session and its attest outcome against night 148 s89. The ratio line counts keys on pages. A blindspot session that attests `none_found` with no note also gives zero keys, and the line then reads as a success. So the read must show that a quarantine outside constraint zero still reaches the page, in words.

## (c) Findings

1. `rota/roles/api.py:11552-11553`, severity low, CONFIRMED. The README reconcile key `vision_keeper|tick:reconcile|@prose` renders as "comparing the account with @prose". `rsplit(":", 1)` keeps a ref with no colon whole. Probe 2 printed the line. No night database holds this key (probe 3), so the leak is latent. Fix: map `@prose` to "README", and strip a leading `@` from a ref with no colon.
2. `rota/roles/api.py:11540-11542`, severity low, PLAUSIBLE. "settling the boundary of" and "comparing the account with" use rota words that the principal does not know. The cause of the frame is a page line the principal cannot read. Fix: use "reading <file> for the rules it sets for outside users" and "checking <file> against what the team learned from the code".
3. `rota/roles/api.py:11546`, severity low, CONFIRMED. `ORDER BY tick_key` sorts by role name, so the six-row limit drops the rows of the Vision Keeper first. Probe 1 showed both reconcile rows cut with eight rows. Fix: order by `rowid`, which keeps the first-come order and is stable too.
4. Outside the points. `rota/roles/principal.py:332-335` (`gave_up_on`) and `principal.py:1176-1186` (`_stalled_words`), severity low, PLAUSIBLE. The state page prints "Stuck. The team gave up on: boundary for @surface:.readthedocs.yaml". That is the kind word and the prefixed ref, the same cause on a second route. Read from the code, not rendered. Fix: one helper that writes a key in words, used by `code_gaps`, `gave_up_on` and `_stalled_words`.
5. Outside the points. `rota/core/predicates.py:1678-1715` (`quarantined`), severity low, PLAUSIBLE. The `tick:quarantined` wake of the Liaison does not filter constraint zero. Its detail reads "constraint_zero for the run, 3 attempts". The page log `clickI.principal.jsonl` shows no page with that text (probe 5). Fix: add the same `NOT LIKE '%tick:constraint_zero%'` filter to the query.
6. Outside the points. `tests/rota/cases/l1_survey.yaml:193-214`, severity low, CONFIRMED. The case expects one `survey_records` row only, so a seat that attests `none_found` passes. Seq 488411 shows the seat drift that way. Fix: expect one `ledger` row of kind `gap` that names `src/store` in words.

## (d) Probes

All probe files are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/dae006d1-0f15-4df0-b329-c022767b2f08/scratchpad/f246/r1/`.

1. `probe_words.py`: ten quarantined rows into a fresh database, then `code_gaps`. It printed six facts. Both reconcile rows and both constraint-zero rows were absent.
2. `probe_prose.py`: three rows, with `@prose` and `@prose:docs/parameters.md`. It printed "comparing the account with @prose".
3. An inline query over the 72 `D:/repos/rota/.rota/*night*.db`, read-only. No database has more than six keys outside constraint zero, and none has a `|@prose` reconcile key.
4. `parent/`: `git archive 401bbf3f~1 rota` with the tests of the commit. `pytest -k gaps_name` failed at line 2012 on the old fact lines. At 401bbf3f, `-k "gaps_name or blindspot"` gave 2 passed. The CR count in the diff and in `api.py` was 0 and 0.
5. A grep of `D:/repos/rota/.rota/clickI.principal.jsonl` for "constraint_zero" or "constraint zero" outside the key form. It found nothing.
6. Inline queries on `D:/repos/rota/tests/rota/cassettes.db` with `mode=ro`: `case_runs` seq 487221 and 488411, their calls and their errors.

## (e) Usage

The harness line holds the exact numbers. The estimate is about 60k input and 10k output, about 70k in total, against the 60k cap. No sub-agent ran.
