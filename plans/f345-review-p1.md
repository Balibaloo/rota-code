# Frame 345, review of pass 1, commit 5b525a72 on f345root

Verdict: NOT READY. 2 high, 4 low. The harness patch is safe for the other tiers, and the case data is faithful. The clarify case cannot pass, and the refusal record puts refusals on the wrong turns.

## (a) Verdicts on the numbered points

1. PASS. With no `page.lines`, the patch is a null context. The 38 Liaison L1 cases replay the same 27 greens and the same 11 reds on main and on the commit.
2. PASS for 5 of 5 cases checked by probe, and 6 more checked by eye. The lines, the row ids, the reply, the header and the cause match the judged source byte for byte. Each check is the verdict per line, plus the act and the target kind where the judge names them. The m58 case expects `ask: true` and `rulings count: 0`.
3. PARTLY. The `reading` rows exist only when the door admits the call, so the check judges what passed the door. The check ignores `rulings.status`, so a stale ruling counts as landed (finding 3).
4. FAIL. The pairing misaligns on a turn with two refusals, on a turn with a call the door admits, and on a runner error that is no refusal (finding 2). Each text is verbatim, with the function name in front.
5. PASS with a gap. The salt is deterministic per run, so runs 2 and 3 have stable prompts and replay once recorded. The three live runs are only in the worktree register, at window 16384, and the suite replays at 12288 (finding 4).
6. PASS. Exactly one runner collects each case. Counts: test_l1 160 (184 before, 157 cases now and 181 before), test_l3 7 (no change, 6 chains), test_l3_rulings 24.
7. PASS. A Liaison converse whose cause is a clarify on rows keys mode `answering` (rota/core/runner.py:373-375). The case names prompt `answering`, so the stamp and the wake agree.
8. PASS. The commit holds 4 files. It holds no cassette db, no scratch file and no user path. `tests/rota/cassettes.db` is ignored by .gitignore:32.

## (b) Findings

1. High. tests/rota/cases/l3_rulings.yaml:4830 (L3R-n175-m102-m103) with tests/rota/test_l3_rulings.py:58. CONFIRMED by code and record. The door builds clarify rows with an empty order, `[] if is_clarify else order` (rota/roles/api.py:14795), so every clarify row has `line` NULL. Night 175 recorded the same: r_m103_2 rows hold `line None`. `landed_lines` keeps only rows with `line IS NOT NULL`, so the case reports "line 1: no ruling" for a right reading. The case also seeds `order:<m103>`, an order record that production never had for a clarify. The m102 message has no `body_text`, so the answering wake shows `question: None`. The judged source holds the text in `page_he_saw`. Fix: key this case's expect by ref, read clarify rows by ref, drop the seeded order, and put `page_he_saw` into the m102 `body_text`.
2. High. tests/rota/test_l3_rulings.py:90-111 (`refusals`). CONFIRMED by probe f345_pair.py. Case A: a refusal on turn 2 after an admitted read call on turn 1 is recorded as turn 1. Case B: two refusals on turn 1 are recorded as turns 1 and 2. Case C: the runner error "ended a tick with nothing done" is recorded as a refusal. `outcome.errors` holds many runner errors that are not door refusals (rota/core/runner.py:5132-5553). Fix: pair each error with the turn whose tool result holds it, from the per-turn transcript, and keep only errors whose prefix is a called function.
3. Low. tests/rota/test_l3_rulings.py:53. CONFIRMED by reading. The query selects the ruling by `reply_id` with no status filter, so a `stale` ruling counts as landed. It also takes one ruling with `fetchone()` when the seat lands two. Fix: add `AND status = 'landed'` and fail the case when more than one ruling holds the reply.
4. Low. tests/rota/cassettes.db in the worktree. CONFIRMED by query. The 9 case_runs rows and 23 cassettes are at `num_ctx` 16384, in the ignored worktree register. The main register holds 8192 and 12288 for qwen3:8b. After the merge, the gate replays all 24 cases as STALE, and the three live runs do not count. Fix: record the next cycle with ROTA_NUM_CTX unset into the main register, and say so in the frame status.
5. Low. rota/testkit/fixtures.py:1629-1631 (`seen`). CONFIRMED by probe f345_order.py. The patch returns the `page.lines` text with the order of today's render. The two orders differ on 12 of 24 cases, for example m116-m118 renders 7 lines and the record holds 11. The door and the wake read the seeded record through `seen_order`, so they are safe. A reader of `render_page(...)[1]`, such as `pending_asks`, gets an order that does not match the text. Fix: return the seeded record order beside the text, `(text, door_rows(conn, reply_id, "order"))`.
6. Low, outside. tests/rota/cases/l3_rulings.yaml:3. PLAUSIBLE. The header names `l3_rulings_judged.yaml` as the source, but that file is untracked in the worktree and is not in the commit. A later reader cannot trace a case to its judgement. Fix: commit the judged source under plans/ or tests/rota/cases/, and point the header at it.

Outside, no defect of this pass: the n171-m27-m28 live run shows the door refuse line 4 with "His reply does not say that line 4 is right". The reply says "Line 4 reads my last answer correctly." The read-back door misreads his words, and that is a measured door finding for the next cycle.

## (c) Probes

All probes are in C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/161c371b-f6a2-4d73-aebc-bae776885ab7/scratchpad.

- f345_reg.db: a copy of the main register. The Liaison L1 cases replayed on D:/repos/rota and on the worktree against the copy. f345_l1_rota.txt and f345_l1_rota_f345.txt hold the two failure sets, and `diff` printed SAME.
- f345_collect.py: counts the cases per runner, with the old filter and the new filter.
- pytest --collect-only on test_l1, test_l3 and test_l3_rulings, with ROTA_NUM_CTX=16384 in the worktree.
- f345_fid.py: compares 5 cases with the judged source (lines, ids, tables, reply, header, judge line, expect).
- f345_wtreg.db and f345_bt: a copy of the worktree register, and a replay of the three recorded L3R cases with `--basetemp`. f345_rows.py printed the `reading` and `landed` rows of each run.
- f345_pair.py: calls `refusals` with three fake outcomes (cases A, B, C).
- f345_order.py with f345_dbs: seeds each case and compares the real render order with the seeded order record.

## (d) Usage

- Input tokens: about 95,000.
- Output tokens: about 14,000.
- Total: about 109,000.

## p2: review of commit d9bc5e96, pass 1b

Verdict: READY. 0 high, 1 low. All six findings of p1 closed on a probe.

### (a) Verdicts on the p1 findings

1. High 1 CLOSED. The clarify case has `page: {}`, seeds no order and carries `expect_refs` by ref. The m102 message holds the question, and the rendered page equals `page_he_saw` byte for byte. The live record at 12288 now reports "act None, expected 'drop'" by ref, so the check reaches the rows.
2. High 2 CLOSED. A probe through `_logged_calls` gave two refusals on turn 1 with turn 1 and the next calls "turn 1 rulings.rule" and "turn 2 rulings.rule". The runner error "ended a tick with nothing done" went to its own column. The replay of n175-m116-m118 shows refusals on turns 1, 2, 3 and 5, and the parse error of turn 4 as a runner error.
3. Low 1 CLOSED. `landed_lines` selects `status = 'landed'` only.
4. Low 2 CLOSED. The worktree register holds the four smoke cases at `num_ctx` 12288 with no profile, which is gate.py's `DEFAULT_NUM_CTX`. A replay of the four cases with ROTA_NUM_CTX unset played every recording and reported no STALE.
5. Low 3 CLOSED. With the patch on, `render_page` returns the seeded order. On all 23 page cases the order has the length of `page.lines` and the ids of the judged lines.
6. Low 4 CLOSED. tests/rota/cases/sources/l3_rulings_judged.yaml is committed with a two-line header, and its 30 entries equal the root file. The header of l3_rulings.yaml still names the bare file name and not the new path.

The runner's own `rulings.line` call before turn 1 changes no case. The push loop (rota/core/runner.py:4223-4230) calls each read with no arguments. `rulings.line` needs a line, so it raises `TypeError` or `ArgumentError`, and the loop skips it. Nothing goes into the prompt. `rulings_line` writes no table. The wrapper raises the same exception again, and `refusals` drops turn 0. The push catches the exception, so it is not in `outcome.errors` and does not reach the register. Production makes the same call, so the prompt hash does not change.

### (b) Findings

1. Low. tests/rota/test_l3_rulings.py:157-160 (`runner_errors`). PLAUSIBLE. A held call raises inside `Sandbox.call`, so the wrapper logs it as a refusal. The runner records it as f"{hc.name} (held): {exc}" (rota/core/runner.py:5393). The text then misses the set, and one refusal shows in both columns. Fix: match on the text after the first colon, or drop errors that contain " (held): ".

### (c) Probes

The probes are in the scratchpad named in section (c) above.

- f345_wtreg2.db and f345_bt2: a copy of the worktree register, and a replay of the four smoke cases with ROTA_NUM_CTX unset and ROTA_RUNS=1.
- f345_pair2.py: stubs `Sandbox.call`, then runs a turn 0 push, a turn with two refusals and a turn with one admitted call through `_logged_calls`, `refusals` and `runner_errors`.
- f345_order2.py: seeds each case and renders its page under `_page_as_seen`. It compares the order with the judged ids, and prints the clarify page and its order.
- An inline heredoc probe compared the rendered clarify page with `page_he_saw`.

### (d) Usage, p2

- Input tokens: about 30,000.
- Output tokens: about 6,000.
- Total: about 36,000.
