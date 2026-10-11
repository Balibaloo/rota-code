# Frame 204, pass 1b review: the seven findings of review 1

STANDS: 7 of 7 findings fixed, 0 high, 1 low new (N1), 34 cases newly stale.

The pass fixes H1 and L1 to L5 with a probe each, and L4 holds for the offered words. The rendered brief carries the words in the same system text that the text protocol sends. The one new defect is low: the slot also renders in the 24 modes that do not offer `ledger.log`, with all nine words.

Reviewer: Opus, read-only, worktree `C:/Users/roman/rota_rv204` at 6307f965, 2026-10-11. Probes are in the scratchpad, `rv204b/`. No model was called. No suite-wide command ran.

## (a) Verdicts

1. The seven findings: fixed. H1 holds in 25 of 25 modes, and L1 to L5 each pass a probe. L6 was a design question and is out of scope.
2. The text-protocol tool line: costs nothing. The words are in the brief, and the brief is the head of the same system text as the `TOOL:` line.
3. Outside the findings: one low defect (N1). The tie-break, the fault branch and the agenda refusal break nothing that a probe found.
4. Stale cases: 92 for qwen3:8b at 6307f965, 58 at b00aaa59, so pass 1b adds 34. No case leaves the stale set.

## (b) Findings

### N1. The slot names all nine words in the 24 modes that do not offer `ledger.log`

- Severity: low. CONFIRMED.
- Where: `rota/roles/prompts.py:100-111` (`fill_kinds`), with the slot in `architect/base.md:47`, `terminologist/base.md:42`, `tester/base.md:24`, `vision_keeper/base.md:41`.
- A shared base renders the slot in every mode of the role. `mode_kinds` returns None for a `.tools` file with no kinds line, so `fill_kinds` falls back to `LOG_KINDS`.
- Probe P4 shows 24 modes with no `ledger.log` in their `.tools` whose brief now says "Its `kind=` is one word: `conflict`, `scope`, `invented`, `finding`, `default`, `gap`, `blocked`, `fault` or `other`". The list includes `architect/relay`, `terminologist/relay` and `vision_keeper/relay`.
- The base invitation to `ledger.log` in those modes is older than frame 204. Pass 1b makes it longer, and it names `gap` and `finding`, which no mode with a kinds line offers.
- The cost: frame 204 removed the call from the relay modes, and their brief now invites the call more. Part of the 34 new stale cases are modes with no `ledger.log`, for example `L1-VK-relay-the-ruling`, `L1-AR-annotate-a-batch` and `L1-TE-amend-glossary`.
- Fix: in `fill_kinds`, when `mode_tools(role, mode)` excludes `ledger.log`, remove the sentence that holds the slot, and re-record.

## Point 1. The seven findings, one probe each

Probe P1, `rv204b/p1_briefs.py`, composes every mode whose working set holds `ledger.log`. It checks that each paragraph that names `ledger.log` names every offered word, or dictates `kind="w"` with an offered `w`.

```
modes offering ledger.log rendered: 25
(no BAD line)
```

Three modes, quoted from the composed text:

- `developer/answer`: "**If the answer still leaves you a choice to make, `ledger.log` it and take the choice.** Its `kind=` is one word: `invented`, `default`, `scope`, `conflict`, `blocked`, `fault` or `other`."
- `liaison/blindspot`: "For each gap that matters, one entry with `ledger.log` and `kind="gap"`." Then: "Each `ledger.log` has one `kind=`: `gap`, `blocked`, `fault` or `other`."
- `vision_keeper/reconcile`: "that is a conflict, and you cannot rule on it ... `ledger.log(about_ref=<the item id it touches, or the README's path>, about_table="items", assumption="README says <X>; the code shows <Y>", kind="conflict")`".

H1, the dictated calls. Probe P3, `rv204b/p3_door.py`, sends each dictated form through the door with the mode's words:

```
vision_keeper deliver default -> {'id': 'l_c45eefa32b'}
vision_keeper reconcile conflict -> {'id': 'l_82eeba2cf9'}
developer challenge scope -> {'id': 'l_9d82ca6e32'}
vision_keeper slicing scope -> {'id': 'l_9d82ca6e32'}
```

H1, the Tester's brief: `tester/tests_missing.md:46` now says "Encode the test: `tests.encode` writes the assumption to the ledger for you." The mode's piece holds no `ledger.log` invitation now. Review 1, point 5, showed that the literal door stages `invented` with the seat as author.

L5, the CHECK (P3):

```
ledger kind blocked refused CHECK constraint failed: kind IN ('default','unaddressed_answer','invented','scope','gap','finding','conflict','other')
ledger kind fault refused CHECK constraint failed: (same)
ledger kind default admitted
```

L2, the guards on a fault (P3, `terminologist/normal`, ref `i1`, an item id):

```
fault -> {'fault': 'f_a49d6db758', 'call': 'unknown', 'note': 'the fault is recorded for the people who build rota. ...'}
blocked, assumption "stuck" -> REFUSED an assumption is a sentence a reader learns from. ...
```

The relay test runs the echo guard and the message guard on `default`, `blocked` and `fault` (`test_request_page.py:982`). It passes.

L3, a second unoffered word (P3, `developer/batch_start`):

```
gap, invented -> kind 'invented', dropped "kind='gap' is no word this mode offers, so the door dropped it and kept 'invented'. This mode offers: conflict, scope, invented, default, blocked, fault, other."
banana -> REFUSED kind='banana' is no word this mode offers. Answer three questions, ...
fault, invented -> kind 'invented'
```

L4, the door text (P5): `kind_questions(('gap','blocked','fault','other'))` names only `'gap'`, `'fault'` and `'blocked'`. `kind_questions(LOG_KINDS) == KIND_QUESTIONS` is True. Item 4 of the tie-break stays out of the text, as the pass report says.

L1, `rota agenda` on an older database. P3 builds a database from the schema of 3f2e974e with the mark `ledger-kind`, and calls `cmd_agenda`:

```
SystemExit: C:/Users/roman/AppData/Local/Temp/tmp72u29qv8/old.db: the run database is behind the current schema, so it needs a fresh onboarding: wipe it, or onboard under a new name
```

The refusal holds because pass 1 moved `SCHEMA_MARK` to `ledger-grid-faults`. The CHECK change in pass 1b moves no mark. A database at the mark of pass 1 keeps the wider CHECK. The door never writes `blocked` or `fault` to `ledger`, so that database stays safe (reasoned).

The touched test files:

```
ROTA_MODEL=qwen3:8b python -m pytest tests/rota/test_prompts.py tests/rota/test_request_page.py tests/rota/test_park_page.py -q -n 0 -p no:cacheprovider
132 passed, 4 xfailed in 6.65s
```

## Point 2. The text-protocol tool line

The silence of the tool line costs nothing. `run_session` composes the brief with `prompts.compose(wake.role, _mode_key(wake, conn))`. `compose_system` (`rota/core/runner.py:334`) puts that brief first and the `TOOL:` lines after it, in one system text. `session_sandbox` sets `ctx.log_kinds` from the same `_mode_key`, so the brief and the door read one mode.

Probe P2, `rv204b/p2_system.py`, builds the system text with `compose_system` for three modes. In `liaison/blindspot` the two places are:

```
L78: Each `ledger.log` has one `kind=`: `gap`, `blocked`, `fault` or `other`. It is about an
L96: TOOL: ledger.log(about_ref, about_table, assumption, kind)
```

In `vision_keeper/deliver`, line 67 dictates `kind="default"`, and line 107 is the bare `TOOL:` line. In `developer/batch_start`, paragraph 11 names each word with its meaning, and line 94 is the bare `TOOL:` line.

## Point 3. Outside the findings

- N1 is the one defect.
- The word order differs between the brief and the door. The brief uses the order of the `.tools` line. The reply "This mode offers" uses the order of `LOG_KINDS`. The sets are equal, so no write changes.
- `_refused_call` writes `unknown` for every fault with no call. `faults close --call unknown` then closes all of those faults at once. The night report must read `unknown` as "no call", and not as one call (reasoned).

## Point 4. Stale cases

`rota.tools.gate._stale` returns None in the worktree, because the worktree has no register. I copied `D:/repos/rota/tests/rota/cassettes.db` to the scratchpad. I pointed `paths.DEV_DB` at the copy and ran `casestatus.status('qwen3:8b')` two times: from the worktree, and from a `git archive` of b00aaa59 in the scratchpad.

```
at 6307f965 92 at b00aaa59 58 both 58 new by 1b 34 gone 0
6307f965 states: STALE 92, green 55, FAIL 6, PROV 4
tiers of the 92: L1 78, L3 5, ACT 4, L2 4, G1 1
```

The 34 new cases: 9 `L1-AR`, 8 `L1-TE`, 4 `L1-TS`, 11 `L1-VK`, 2 `L3`. The night wrote the register at 17:41 with a WAL file beside it, so the copy can lag the night by a few rows.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/59bdd13a-98f3-4dda-ba43-071cb487b114/scratchpad/rv204b/`. Each ran from the worktree root with the venv Python.

- P1, `p1_briefs.py`: composes every mode that offers `ledger.log`, and checks the words of each paragraph.
- P2, `p2_system.py`: builds the whole text-protocol system text for three modes, and prints the `ledger.log` lines.
- P3, `p3_door.py`: the dictated calls, the word drop, the fault guards, the CHECK, and `cmd_agenda` on an old database.
- P4, an inline Python call: composes the modes whose `.tools` excludes `ledger.log`, and prints each paragraph that names `kind=`.
- P5, an inline Python call: renders `kind_questions` for two narrow sets, and compares the full set with `KIND_QUESTIONS`.
- P6, an inline Python call: the stale count on the register copy `cassettes.db` and on the export `b00/`. The set of b00aaa59 is in `stale_b00.txt`.

## (d) Usage

Estimate: input about 80k tokens, output about 12k tokens, about 92k in total. The read exceeded the 50k cap. The harness line is the measure.
