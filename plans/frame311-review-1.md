# Frame 311, review 1: passes 1 and 1b at 9206e141

Read on Opus, read-only, in the worktree `C:/Users/roman/rota_r311` at
`9206e141`, 2026-10-24. The night databases and `tests/rota/cassettes.db`
were opened with `?mode=ro`. No gate, no re-record and no full suite ran.

## The verdict

Put `9206e141` on the branch after frame 257's commit and the gate. The
predicate matches the ruling, and both refusals read it. The tests carry the
exact night-160 calls, and `tests/rota/test_verdict_lines.py` is green, 92
passed. No recorded case reaches the new predicate. The five findings are
low. Findings 1 and 2 are text fixes for a pass 1c, or for the same gate if
the assistant wants them in.

- Point 1: PASS. The per-criterion read replaces the joined query, and both refusals read it. The comment rule exceeds the literal ruling (finding 4).
- Point 2: PASS with one known miss. No behaviour criterion on nights 140 to 160 holds a word. s188's text still gets the refusal (finding 3).
- Point 3: PASS. The tests carry the exact night-160 arguments, and the fixture diff matches bg_2's added lines.
- Point 4: PASS. None of the six cases goes red from the predicate. The prompt change makes all six stale only.
- Point 5: PASS with two text faults. The seat can act on the sentence. "No such line" now has two referents (finding 2).

## Point 1: the predicate

- `_ASKS_FOR_DOCS` is `("docstring", "documentation")` at `rota/roles/api.py:12410`. `_asks_for_docs` case-folds the text and matches a substring (`api.py:12417-12420`).
- The joined query of the provenance (`api.py:12515` at `cab91420`, `12710` at `6413e4ee`) is gone. `texts_of` reads `c.id, c.text` once (`api.py:12617-12621`). The quote check reads `texts_of.values()` (`api.py:12743`).
- The block refusal reads `kinds_of[cid]` at `api.py:12701` and `12719`. The single refusal reads it at `api.py:12781`. No other site in the file reads the kinds. `_first_pass_hold` has its own `c.id, c.text` query and reads no kind.
- For a documentation criterion, a docstring line and a comment read as code (`None`). For any other criterion, `kinds_of[cid]` is the unchanged list. So frame 180's refusal holds for every other criterion.
- The comment line follows the same rule. The ruling names a docstring line only. The comment rule is the provenance's reasoned extension, not a ruling (finding 4).

## Point 2: the leak, both ways

Probe p1 read the `criteria` table. Probe p4 read every `[criteria.load]` row of every prompt, nights 140 to 160. All 21 databases exist. These texts hold a documentation word or a near word:

| Night | Id | Words | Asks for | Effect of 9206e141 |
|---|---|---|---|---|
| 142 | `c2_flag_triggers_version_string` | "help text" | behaviour: the flag "does not affect help text" | none, no word |
| 157 | `crit_show_python_help`, 3 versions | "help text" | the `help=` string, a code line | none, no word, correct |
| 160 | `ver_opt_show_py_help` | "help text", "document" | the `help=` string, a code line | none, no word, correct |
| 160 | `cr_3_confirm_default_on_eof`, the s188 version | "documented", "help text of confirm()" | the docstring of a function | refusal still fires, wrong |
| 160 | `cr_3_confirm_default_on_eof`, v7 and its two longer forms | "docstring" | the docstring | admitted, correct |

- One way: no text on nights 140 to 160 holds "docstring" or "documentation" and asks for behaviour. So no docstring line now meets a behaviour criterion on these nights. A negated mention would leak (finding 5).
- The other way: the s188 text asks for the docstring in other words, and the refusal still fires on it. The help text of a function is its docstring, so the ruling covers the s188 text. The pass 1b report names this miss: 1 refusal in 1 of 15 sessions (finding 3).

## Point 3: the red tests

- s206: `S206_CALL` matches the completion of `turns` s206 seq 1 character for character (probe p6). The test lands the pass through the hold.
- s205: `S205_CALL` matches the call in the s205 turn 1 completion. The seat wrote "does not enable" where the diff has "do not enable". So 4 of the 5 parts are held, and the test asserts those 4. The fixture's added lines match the `+` lines of bg_2 in the s205 prompt (probe p6).
- The s205 test asserts the cap text with "lines of the docstring" and without "does nothing that a criterion asks for".
- s146: both calls match `tool_calls` s146 seq 5 and 6 (probe p5). Both stay refused with the exact night text.
- s134: `test_s134_pass_naming_import_json_is_refused` is unchanged. The import kind is outside `_DOC_KINDS`, so the predicate cannot reach the call.
- The help-string guard uses `ver_opt_show_py_help` verbatim from the `criteria` table, and "work is documented.". Both get the frame 180 text.
- `ROTA_MODEL=qwen3:8b pytest tests/rota/test_verdict_lines.py -q -n 0` gave 92 passed in 23.08s.

## Point 4: the six stale cases

None of the six expectations goes red under the new predicate. The prompt hash changes, so all six go stale.

- The criteria texts of `l1_acts.yaml`, `l1_judgement.yaml` and `l3_handoffs.yaml` hold neither word. So `_asks_for_docs` is false for every criterion, and `kinds_of[cid]` equals `kinds`. The door is the same as at `6413e4ee` for these cases.
- The cassettes hold 3245 review wakes over all models. 0 wakes have a `[criteria.load]` row with either word. 0 completions name a docstring or comment line in `lines=`. The 6 raw hits were prose, not criteria or values (probes p9, p11, p12).
- The new noun "lines of the docstring" fires only when `own` holds docstring lines. `own` holds them only under a documentation criterion. So no case text changes.
- `ACT-CR-quote-the-tests-code` and `L3-a-failed-verdict-turns-into-a-fix` record on gemma3:12b and have 0 qwen3:8b runs (probe p10). Their staleness shows on gemma3:12b only.

## Point 5: the Critic's brief sentence

- The seat can act on "A docstring or comment line is evidence only for a criterion that asks for documentation." The sentence names a kind and a condition that the seat can read in the criterion.
- The sentence does not contradict `base.md:10-11`, which forbids a fail for a purpose read in a docstring. Step 3 reads comments as grounds for a doubt, not as evidence for a pass. So step 3 does not contradict it either.
- The next sentence, "A criterion with no such line looks like it fails", now follows the docstring sentence. "Such line" can bind to "a docstring or comment line" (finding 2).
- The prompt says "asks for documentation", and the door reads two words only. A seat can read the s188 text as a request for documentation, and the door refuses it (finding 3).
- The refusal texts of the door still say that a docstring line does nothing that a criterion asks for. The prompt now says the opposite for some criteria (finding 1).

## Findings

1. `rota/roles/api.py:12708-12715` and `12787-12792`. Low. CONFIRMED. The single and the block refusal texts still say that "a comment, a plain import or a docstring line does nothing that a criterion asks for". That sentence is now false, and it contradicts the new `review.md` sentence. `test_a_docstring_line_for_another_criterion_stays_refused` asserts this text for cr_1 in a call where the same line is valid for cr_3. That is the s231 shape of night 160. A seat that reads the text can drop the correct docstring line of cr_3, and the night-160 loop comes back. Fix: for a kind in `_DOC_KINDS`, say the line meets only a criterion that asks for documentation.
2. `rota/roles/prompts/critic/review.md:11-13`. Low. PLAUSIBLE: a small model binds "such" to the nearest noun, and the docstring sentence is now nearest. "A criterion with no such line looks like it fails" can read as "no docstring line". Fix: write "A criterion with no added line that meets it looks like it fails".
3. `rota/roles/api.py:12410`. Low. CONFIRMED by probe p13: `_asks_for_docs` is False on the s188 text, "must be documented in the help text of confirm()". The ruling covers that text, and the prompt word "documentation" admits it. So the door and the brief disagree on it. The cost on night 160 was 1 refusal in 1 session. Fix: name the miss as accepted in the comment, and make `review.md` name the two words.
4. `rota/roles/api.py:12413`, `_DOC_KINDS`. Low. PLAUSIBLE: the ruling names a docstring line only, and none of the 40 refusals was a comment. The brief allowed the comment rule when the code treats the two kinds in one place. So the departure is from the words of the ruling, not from the brief. Fix: record the comment rule as reasoned in the frame, or ask Roman in one line.
5. `rota/roles/api.py:12417-12420`. Low. CONFIRMED by probe p13: "confirm() must return the default and must not change the docstring." gives True. A substring match admits a negated mention, so a docstring line then meets a behaviour criterion. Nights 140 to 160 hold no such text. Fix: accept the limit and name it in the comment, because a negation parse fits cases and not the workflow.

Outside the points: none found.

## Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0cdcac52-3588-4266-b1fb-fc5d7d31b805/scratchpad/r311/`.

- `api_base.py`: `git show 6413e4ee:rota/roles/api.py`, to find the old joined query.
- `p1_sweep.py`: the `criteria` table of `clickI_night140.db` to `clickI_night160.db`, filtered by documentation words.
- `p2_tables.py`, `p3_fmt.py`: the night-160 schema, and the `[criteria.load]` row format in the s176 prompt.
- `p4_versions.py`: every `[criteria.load]` row of every prompt, nights 140 to 160. Its output gives the table of point 2.
- `p5_calls.py`: `tool_calls` of s205, s206 and s146 on night 160, and the s205 seat text.
- `p6_diff.py`: the `+` lines of bg_2 in the first s205 prompt, and the s206 call in turn 1.
- `p7_cass.py` to `p12_detail.py`: the schema of `tests/rota/cassettes.db`, the runs of the six cases, and the review wakes with documentation words or a docstring or comment line in `lines=`.
- p13, an inline `python -c` in the worktree: `_asks_for_docs` on the s188 text, `ver_opt_show_py_help`, a negated text and the latest cr_3 text. The results were False, False, True, True.
- The test run: `ROTA_MODEL=qwen3:8b pytest tests/rota/test_verdict_lines.py -q -n 0` in the worktree gave 92 passed.

## Usage

- Input tokens: about 75k, an estimate from the context. The harness shows no counter.
- Output tokens: about 12k, an estimate.
- Total: about 87k. The cap was 25k. Most of the input was the code, the test diff and the probe output.
