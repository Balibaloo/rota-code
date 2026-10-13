# Frame 226 and frame 227, review of pass 1 (commit 33cd99b2)

Read-only diff review in the rota workflow. Worktree: C:/Users/roman/rota_rv226 at 33cd99b2. The commit's own parent is 84abe873. The range 88cbbe5a..84abe873 holds plans commits only. Reviewer: an Opus agent, 2026-10-13.

## (a) Verdicts on the points

1. PASS. The commit touches the seven files the report names. The blobs hold no CR byte (git show counts 0).
2. PASS. init_db adds rulings.texts with the default '{}' to the night's copy. last_ruling_on reads all 272 per_item refs with no error.
3. PASS WITH DEFECTS. s546's text is refused with the words and the token. Two false refusals exist: findings 1 and 2.
4. PASS. The wake quotes the newest ruling verbatim. One mode changes its prompt: terminologist criterion_repair.
5. PASS. The contested sentence sent back is refused. The same words with no contest keep the note. An approve never refuses.
6. PASS. s537, s583 and s591 relays select criterion_repair under the commit's _mode_key. The sentence is in the right file.
7. PASS. Four pinning tests are red on the parent. Three control tests and the no-ruling prompt test stay green, by design.

## (b) Findings

1. api.py:4838-4845 (criteria_respecify, the contested-token rule). Severity high. CONFIRMED.
   The contested set is "tokens of the contested text minus tokens of the current text". So any name that one repair drops becomes forbidden, also a name that the principal asked for.
   Probe p3 case C: the contested text is V14, the current text drops `version_option`, and the new text is V15. The door refuses with "the principal contested version_option". WORDS_374 says "a parameter that the developer passes to version_option".
   The seat can then never name the function that the criterion is about, until a new ruling lands.
   Fix: remove from the contested set every token whose text occurs in the principal's words, compared in lower case.
   Check: `--show-python` does not occur in WORDS_374, so s546 is still refused after the fix.

2. api.py:4838-4845. Severity low. CONFIRMED.
   A legitimate text that names the token in a negation is refused. Probe p3 case B: "The option is not `--show-python`." is refused. Case B2, the bare flag "do not type --show-python", is refused too.
   The cost is one retry, because the refusal tells the seat to write without the token.
   Fix: accept the false refusal and say in the refusal "do not name it, also not to deny it", or skip tokens that follow "not" or "no".

3. principal.py:1950-1956 and principal.py:2036 (land and _land_shift, raw INSERT). Severity low. PLAUSIBLE.
   These writers insert a ruling row without texts. A contest that lands by this path gets '{}', so the door and the frame 227 refusal stay silent.
   Night 144 shows 0 rows with this path and a non-empty per_item, so no night case hits it today.
   Fix: write texts from the criteria rows in the same INSERT, or record that this path carries no contest.

4. runner.py:410-442 (_last_word_lines). Severity low. PLAUSIBLE.
   The block writes a heading for the newest ruling whatever its verdict. After an approve on a later page, the heading quotes words about other lines, under "(ruling r_373fbae7da, approve)".
   Night 144 shows this shape for ver_opt_show_py: the last ruling is an approve whose words ask about line 3, `custom_version_option`.
   Fix: write the block only for contest and revise, or keep it and accept the noise.

Outside the points: none further.

## Point details

- Point 1. git show --stat 33cd99b2: db.py, runner.py, schema.sql, api.py, principal.py, criterion_repair.md, test_criterion_contest.py. The checkout files hold CRLF from core.autocrlf, so the bytes in the blobs are the measure.
- Point 2. Before init_db the rulings columns end at version. After it the columns end at texts, every row holds '{}'. last_ruling_on on bg_5 returns r_c4bf70291d, contest, text None. rulings.rule writes texts for contest and revise refs from the criteria row. test_a_contest_of_a_criterion_line_keeps_the_text_it_contested pins that path on night 132's page.
- Point 3. Counted tokens: a backquoted span, a flag of the form --name, and an identifier with an underscore, all in lower case. V14 gives {version_option, --show-python}. V15 gives {version_option, show_python}. V16 gives {version_option, --show-python, clirunner}. The set for s546 is {--show-python}. A text without the flag that changes the words is admitted. A criterion with no ruling admits V16.
- Point 4. prompts.compose is base(role) plus piece(role, mode). The commit changes only the piece criterion_repair.md. The runner block runs only on tick:criterion_repair, which keys the same mode. Stale modes: 1, terminologist criterion_repair. Case files that hold that mode: l1_answers.yaml, l1_terminologist.yaml, l1_tester.yaml, l1_unresolved.yaml.
- Point 5. Probe p3 case D: an approve ruling with the same words returns unchanged and the old note. last_ruling_on returns the newest non-stale ruling, so a relay of an approve sees an approve. A revise with the same words is refused (case E), which is correct. A case-only change counts as the same words and is refused (case F).
- Point 6. m378, m407 and m415 are relays to the terminologist, each with refs ["ver_opt_show_py"] and a verdict as cause. park_criterion_relay returns True for each, and _mode_key returns criterion_repair. The relay wake does not get the runner block, because its kind is message.
- Point 7. On the parent with only the test file: 5 failed, 3 passed. The fifth red is the INSERT into the missing column. With schema.sql and db.py copied in: 4 failed, 4 passed. On the commit: test_criterion_contest.py and test_prompts.py give 40 passed.

## (c) Probes

All probes are in C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/fb742825-a1dc-4485-a872-f0c34a3f30b0/scratchpad/rv226.

- n144copy.db: a copy of clickI_night144.db. Every probe ran on the copy.
- p2.py: shows the rulings columns before and after init_db, then calls last_ruling_on on every per_item ref.
- p6.py: reads m378, m407, m415 and m379, runs park_criterion_relay, and runs _mode_key on the three relay wakes.
- p3.py: uses the test file's fixtures. It prints the token sets and runs respecify on cases A to F.
- A worktree at 88cbbe5a, C:/Users/roman/rota_rv226_parent, ran the new test file twice. The worktree is removed.

## (d) Usage

The reviewer has no harness count. The estimate is about 60k input tokens, 9k output tokens, 69k total. Read the harness line for the true count.

## Second look at 81ce21b7

Reviewer: a read-only agent on Opus, worktree C:/Users/roman/rota_rv226b at 81ce21b7, 2026-10-13. Workflow: the rota workflow, frames 226 and 227, pass 1b.

### (a) Verdicts

1. The high is closed. Probe p3 at 81ce21b7 admits case C (`version_option` in his words) and refuses s546's `--show-python`.
2. Holds. `land` and `_land_shift` call `contested_texts`, and `rulings_rule` calls it. The stored form is the same JSON dict on all three paths.
3. Holds. An approve no longer adds the block. A contest or a revise adds the same two lines as at the parent. `build_prompt` calls the block only on `tick:criterion_repair`.
4. Holds for the commit. 81ce21b7 alone touches the four files. The three new tests fail on the parent source and pass at the commit. The diff holds no CR byte.

### (b) Findings

1. rota/roles/api.py:4841-4844, low, CONFIRMED. The new filter `t not in his` is a substring test. A contested `--show` is admitted again when his words name `--show-python`. Probe p8 printed `back= []`. Fix: match a token against `_named_tokens(contested["words"])`, or on word bounds.
2. rota/roles/principal.py:2060, low, CONFIRMED. `_land_shift` rules park, now and drop on items, never contest or revise. Its new `texts` is always `{}`. Probe p7 stored `'{}'` for r_m445. The call is harmless. Fix: none needed, or drop the call and write `'{}'`.
3. Range note, low, CONFIRMED. The range 0302650d..81ce21b7 holds nine commits. Eight are plans commits, and 0af8c129 edits tests/rota/cases/l1_answers.yaml for frame 204. The "four files" holds for 81ce21b7 against 81ce21b7^ only. Fix: name the parent as 81ce21b7^ in the next brief.

Outside the points: none. The approve-after-contest case is consistent. The wake and `criteria_respecify` both read the newest ruling through `last_ruling_on`, so an approve hides an older contest in both places.

### (c) Probes

All probes are under C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/fb742825-a1dc-4485-a872-f0c34a3f30b0/scratchpad/rv226.

- p3.py: re-run at 81ce21b7 with PYTHONPATH set to the worktree. A, B and B2 refuse. C admits. D admits as unchanged. E and F refuse.
- p7.py: copies n144copy.db to n144p7.db. It runs `land` with a contest on `ver_opt_show_py` and `_land_shift` with a drop on `cj_serializable_revised`. Row r_m444 stores the criterion text. The text equals what `contested_texts` returns, which is the `rulings_rule` helper. Row r_m445 stores `{}`. The `rulings_rule` path is shown by the test `test_a_contest_of_a_criterion_line_keeps_the_text_it_contested` on night 132's fixture, which passes.
- par/: `git archive` of rota at 0302650d plus tests at 81ce21b7. pytest on test_criterion_contest.py: 3 failed, 8 passed. The three failures are the three new tests. At 81ce21b7: 11 passed.
- p8 (inline `python -c`): the substring test on `--show` against words that name `--show-python`.
- CR count: `git diff 0302650d 81ce21b7 | grep -c` on the CR byte printed 0.

### (d) Usage

Input tokens: about 21k. Output tokens: about 4k. Total: about 25k. The harness line is the authority.
