# F7 on night 172: the read of the removal walls W2, W3 and W4, by rule C76

Meta workflow, read on 2026-10-28 for sprint 32 row 2. Sources: `.rota/clickI_night172.db` opened `?mode=ro`, with the 170 and 171 registers for the reach; the principal jsonl; the clickI repository; `plans/night172-read.md` sections 2 and 3, cited and not repeated; `plans/facts-2026-10-27.md` F7, F8, F25; frame 339's status lines. The code at 442e32b0 is the code of the night's head de1203a9 (observed: `git diff --stat de1203a9 HEAD -- rota/` is empty). No code was edited. No model ran. Probes ran `_removal_entry` from `rota/roles/api.py` on the clickI commits (`f7r_probe.py`, `f7r_probe2.py` in this session's scratchpad).

**The finding. The seat that must put the removed code back is never shown the removed code.** The `touch_mistaken` wake holds no base text, no diff and no red test output, and its tool set holds no read of the base (observed: s263's first prompt, 0 hits for `removal:`, `surrogateescape` and `[removed lines]`; `prompts/developer/touch_mistaken.tools`). The one place that names the removal, the row note, names a lost block by its first line only. It names `if isinstance(filename, bytes):`, and the head holds `if isinstance(filename, (bytes, bytearray)):` (observed). The compare also reads the removed `filename = os.path.basename(filename)` as kept, because the new block binds `filename` again (observed: the probe; `_binds_first`, api.py 23029 and 23063). So s263, s264 and s267 each read the head, found "the bytes handling" there, and wrote the head's own text (observed). The build's own condition, "so the Developer of `touch_mistaken` reads the line to put back" (api.py 23894), is not met (reasoned).

## 1. The find

**s239, Developer, `tick:verdict_failed`.** Shown: `batches.expect`, the criteria, the contest r_m98, the fail verdict of s238. No diff, because `verdict_failed.tools` holds no `code.diff` (observed). Turns 3 and 4 sent whole-file writes, refused: "this rewrite of src/click/utils.py drops _PacifyFlushWrapper, ...". Turn 5 sent `text=''` on 441 to 486, refused: "this rewrite ... drops format_filename". Turn 6 sent the signature and the docstring with the new example, and no body, on `start=441, end=486` (observed: the call, whole). It landed: `"dropped": "This write removes or rewrites 3 statements that your text does not hold: `if shorten:` at line 473, `if isinstance(filename, bytes):` at line 478, `return filename` at line 485."`. Turn 7 committed. The result: `committed: True, head_commit: ff34266a..., removals: ['src/click/utils.py::format_filename: removal: `if shorten:` at line 468, `if isinstance(filename, bytes):` at line 473, `return filename` at line 480']`, then `[removals note]` "no criterion, request or ruling of the principal asks for this removal. The commit stands, and it holds your fix. The Architect judges the removal after this session. Your next step is to end the session. Only if you know that the removal was a mistake, put the lines back and commit" (observed). The seat then wrote that the criterion "is satisfied as written" and committed nothing more (observed: turns 10 to 14).

**s242, Developer, `message` answer.** It read 441 to 473, wrote a new body, and committed 128bec7e: `removals: ['src/click/utils.py::format_filename: removal: `filename = os.fspath(filename)` at line 471, `if isinstance(filename, bytes):` at line 473']`. The write returned no `dropped` note, because the write compares with the head, where the body was already gone (observed: turn 4; reasoned). The new body has no `surrogateescape` branch and splits on `/` (observed: the diff).

**s243, s244, s245, Developer, `tick:tests_failing` attempt 6.** The wake held the red output of `tests/test_types.py`, "Your diff broke them. Read code.diff below and restore what it changed; a challenge has no side here", and the `[removed lines]` block with all 9 removed lines, `surrogateescape` included (observed: s243's first prompt). So these seats had the base text.

- s243: turn 4 sent a whole-file write, `start=0, end=-1`, refused by the whole-file door: "this rewrite ... drops _KeepOpenFile, ... and your text still uses os, sys" (api.py 21589 to 21604). Turns 5 and 6 sent `if shorten: filename = os.path.basename(filename)` and `return filename` on `start=465, end=487`, refused by the span door: "start=465 falls inside format_filename ... start=465 is in its docstring at lines 445 to 473" (api.py 20682 to 20700). Turn 9 sent the docstring tail and the head's body plus `os.path.basename`, on the same span. The runner then said "code.write has been refused the same way in three turns and will not be accepted again" (runner.py 5957). Each text kept the head's decode logic. None held `surrogateescape` (observed: the four calls).
- s244 sent no write. It committed nothing, wrote its own tool results twice, and ended with "the implementation correctly handles the `shorten` parameter" (observed).
- s245 sent two challenges. The quote door refused the first. The green-test door refused the second: "tst_c3_format_filename_example passes on the batch's head 128bec7e ... A challenge disputes a red test, and this test is green. No test of this batch with a criterion fails." (`_green_at_head_refusal`, sandbox.py 1604). It ended "All tests ... are passing" (observed).
- s246 was woken by `tick:exhausted`, not by `tests_failing` (observed: `sessions.wake_kind`). The brief's list is wrong on this point. It sent 4 challenges, each refused by the same green-test door, escalated m111, and was refused 4 `ledger.log` calls (observed).

**s262, Architect, `tick:touch_strayed`.** Shown: the wake detail "src/click/utils.py::format_filename (removal: `filename = os.fspath(filename)` at line 471, `if isinstance(filename, bytes):` at line 473)", `batches.consult`, `batches.expect`, and `code.diff` with the full `[removed lines]` block (observed). It judged `mistakes: ["src/click/utils.py::format_filename"]` with "The removal of the old logic for handling bytes and encoding is a mistake. The request only asked for an example in the docstring, not a rewrite of the function." (observed). Its `foreseen` on the bare path was ignored as no open stray (observed).

**s263, s264, s267, Developer, `tick:touch_mistaken`.** Shown: the wake line "Refs: bg_3" with no detail, `batches.expect`, the criteria, the contest, `tests.load` with every test green at its last run (observed: s263's first prompt). The mode text says "For a `removal:` row, put back each quoted base line only" (observed: the system prompt).

- s263 called `batches.strays` and read the note above. Its first write, the head's body on `start=469, end=487`, met the span door: "start=469 is in its docstring". Its second write, the same body on `start=473, end=487`, landed 22089 bytes, "written, not committed: []". The commit said "committed: False, why: nothing changed". It wrote "The file already contains the correct bytes handling logic" (observed).
- s264 and s267 never called `batches.strays`. Each wrote the whole function on 441 to 487 with the head's body, `if isinstance(filename, (bytes, bytearray)):` to `filename = filename.split("/")[-1]`, 22089 bytes, and each commit said "nothing changed" (observed).

**Each removed statement, and where it is named.** The base is b8fd86b, lines in code.source numbering. The same rows come back from today's code (observed: the probe).

| Base statement | ff34266a row | 128bec7e row and s262's wake | Pages m117, m120, m127, m130 | The `touch_mistaken` wake |
|---|---|---|---|---|
| `if shorten:` 468 | Named | Not named. Paired with `if shorten and "/" in filename:` as a rewrite (`_kin`) | No | No |
| `filename = os.path.basename(filename)` 469 | Under 468 | Not named. Read as kept, because the new block binds `filename` | No | No |
| `else:` `filename = os.fspath(filename)` 471 | Under 468 | Named, "`filename = os.fspath(filename)` at line 471". The head holds that text under `elif` | "the assignment `filename = os.fspath(filename)`" | No |
| `if isinstance(filename, bytes):` 473 | Named | Named | "the branch `if isinstance(filename, bytes):`" | No |
| `filename = filename.decode(sys.getfilesystemencoding(), "replace")` 474 | Under 473 | Under 473, text not shown | No | No |
| `else:` `filename = filename.encode("utf-8", "surrogateescape").decode("utf-8", "replace")` 476 | Under 473 | Under 473, text not shown | No | No |
| `return filename` 480 | Named | Paired, equal | No | No |

The four red tests are surrogate tests (night172-read section 3). The statement they need is line 476. No row, note or page shows its text. Only `code.diff`'s `[removed lines]` block shows it, and only the Architect's wake and the `tests_failing` wake push that block (observed).

## 2. The mechanism

- **The stray route.** `touch_strays` and the `touch_mistaken` wake came at cf067ce4 on 2026-09-13, from clickI night 32, under law 12, "the touch set is a prediction, never a permission" (observed: `git log -S`; predicates.py 2390 to 2436).
- **His ruling.** 2026-10-17 about 16:50: "File writes were always permitted everywhere, just that if there were unexpected changes then the architect is required to sign off" (ruled: `rota/DECISIONS.md:1490`, quoted in `plans/frame339-provenance.md`). The same day he ruled against new refusals at commit (stack 1607: "the frame 140 refusal stays on the note by the ruling of 2026-10-17 against new commit refusals").
- **The removal row.** Frame 339 put removals on the stray route on 2026-10-26. Status 21:20: "the door records the removal as a touch_strays row for the Architect by law 12 and frame 286's route". Pass 1b at 4e58ad9c, 2026-10-26, added "the stray prompts name a removal row" after review 1 found that "touch_mistaken.md tells the Developer to write the whole base definition back and undo the rewrite" (observed: stack 1593, 1594). The judgement that put removals on this route was the session's, not his: "the session's judgement of 2026-10-26 21:20 put removals on this route, not a ruling of his" (observed: stack 1602).
- **The compare.** F7 on f7root, 2026-10-27 to 28: 11d04b18 "the commit-time compare of base and tree is the one source of removal rows"; aae59d4b pass 2, "matches normalised ast nodes with no order"; 30d0de73 pass 2b (observed: stack 1605 to 1609). His ruling of 2026-10-27 19:04: "I want to trust the reviewer ... Yeah I'm for a small prompt change in this case" (ruled: stack 1604). The workflow is the rota workflow by each status line.
- **The design's own conditions.** The compare: "Recall comes before precision here ... a missed removal is work that stays invisible" (observed: `_lost_in_block` docstring, api.py 22840). The restore: "a removal's note keeps the removed line in front of the reason, so the Developer of `touch_mistaken` reads the line to put back" (observed: api.py 23894). Pass 2b named one residue of the same class: "a return kept by any other return in its block hides a changed return" (observed: stack 1609).
- **Did the build meet them? No, on both.** Recall: the rebind rule hides the changed `basename` statement. The pass 2 and 2b probes test moves and renames, and none is an assignment whose value changes (reasoned: the status lines list the shapes). The restore: a lost block shows only its first line, the `touch_mistaken` wake does not carry the note, and the mode has no read of the base text (observed).

## 3. The code, at de1203a9

- **Where a commit's removals are found and named.** `code_commit` api.py 22075 calls `_unruled_removals` 22461, which calls `_base_removals` 22489, then `_removal_entry` 22560. `_removal_entry` names each lost statement by `_quote(line[:60])` of its first line. `_removal_strays` 22389 groups them into one row per grain. The commit result writes `removals` and the `[removals note]` at 22275 to 22290.
- **How a removed statement pairs.** `_lost_in_block` 22840, in three passes: an equal statement, then a rewrite, then a statement on every path. A compound statement keys on its header (`_stmt_key` 22664). "A lost compound statement is named by its first line, and its own statements are not named again" (observed: the docstring). A branch is kept when its old test is an operand of the new test (`_kin`). An assignment is kept when "every path through the new block binds its targets before it reads them" (pass 2, with `_binds_first` 23029). `x = f(x)` binds `x`, so its own read is no read (api.py 23063).
- **What the stray judge is shown.** `touch_strayed` predicates.py 2390 puts each open row's note in the wake detail. `DETAIL_SHOWN` runner.py 435 to 453 holds `tick:touch_strayed`. The generic push, runner.py 4196 to 4203, runs each no-argument read in the mode, and `touch_strayed.tools` holds `code.diff` (observed).
- **What the `touch_mistaken` wake shows.** `touch_mistaken` predicates.py 2419 puts only the grain names in the detail. `DETAIL_SHOWN` does not hold `tick:touch_mistaken`, so the detail is not shown. `touch_mistaken.tools` holds `batches.strays`, `code.source`, `code.probe`, `criteria.load`, `tests.load`, `code.write`, `code.commit`, `msg.escalate_architect` and `batches.expect`, and no `code.diff`. `batches.strays` api.py 24020 takes an argument, so it is not pushed (observed; reasoned from the push rule).
- **The doors that refused s243 to s246.** The whole-file door in `_code_write` api.py 21589 to 21604, because the text dropped 15 top-level names. The span door in `_code_write` api.py 20682 to 20700, because the start fell inside the docstring. The repeat cap at runner.py 5957, on the third same refusal. The quote door of `msg.challenge_tester`, because the quote was not in the test's live text. `_green_at_head_refusal` sandbox.py 1604, because each challenged test passed at 128bec7e. No door refused a write that held the base text, because no such write was sent (observed).

## 4. The reach

**Removal rows over nights 170, 171 and 172.**

| Night | Row | Named | What the diff removed | Same? |
|---|---|---|---|---|
| 170 | none | No `touch_strays` and no `drop_notes` row | b_1 be1852fe rewrote line 518 as he asked (frame339-s128-read) | No row by design (observed) |
| 171 | bg_1 a46638f3, open | `if sys.platform == "darwin":` at line 529 | The darwin branch and the XDG return | No: the XDG return was missing. Today's code names both, 522 and 526 (observed: the probe; f7-review-p2) |
| 171 | bg_1 62199a7b, foreseen | The same | The same | The same |
| 172 | bg_3 ff34266a, open, never judged | 3 headers | 9 statements | Yes by block, 3 of 7 base statements by text |
| 172 | bg_3 128bec7e, mistake | 2 | 5 changed statements: `basename`, `fspath` moved, both `isinstance` arms | No: `basename` is not named, and the `surrogateescape` line shows only through its block header |

That is 4 rows, of which 2 named every removed statement by block (observed). The rebind rule also gave no row on 2 heads, be1852fe and 9feffb08, where `folder = os.path.expanduser("~")` became another value of `folder`. He asked for both of those changes, so no harm was seen (observed: the probe returns None; night172-read section 4).

**`mistake` judgements: 1 on three nights, s262's.** 3 `touch_mistaken` sessions followed, 0 commits, and the key quarantined at 3 (observed). Night 171 had 1 `foreseen` judgement and night 170 had none (observed).

**Developer sessions on a red project test that no criterion owns: 4, all on night 172.** s240 (attempt 5, with criterion reds too) sent a challenge. s243, s244 and s245 ended with no commit and no restore. s246 (`tick:exhausted`) is a fifth on the same red. Nights 170 and 171 had 8 `tests_failing` sessions, each on a criterion test (observed: the first prompts).

**Places with the same gap, a restore seat that is not shown the base text: 1.** It is the `touch_mistaken` wake, 3 of 3 sessions. The other restore seats were shown the base text: the `tests_failing` wake pushes `[removed lines]`, and s239's write got the `dropped` note (observed). The note's first-line form reaches 4 more readers that are not restore seats: the commit result, the Architect's wake detail, `batches.strays` and the page line `removal_line` principal.py 2187 (observed).

## 5. The match

Grep of the stack headings for removal, stray, restore, `tests_failing` and mistake, and of the facts:

- **339**, the removal door by one phrase. Its route built this row, and its Ends-when counts grants at the door. It does not cover the restore (observed: stack 1580).
- **330**, a quarantined `tests_failing` key holds the seat. Another effect, not this gap.
- **313**, the span door refuses a boundary inside a docstring. It covers s243's and s263's span refusals, part of W3. It does not cover the missing base text.
- **173**, the span door's end offer removes a branch with no note. Parked. Not this gap.
- **133**, a Developer writes back the line it says it removes. Close to the sign of W4, but no restore seat in it.
- **182**, a batch goes green with the behaviour removed. Not this gap.
- **93**, a write that changes nothing is accepted silently. Parked. It is the sign of W4, not its cause.
- **F7 and F8** name the facts. F25 names the calls a mode offers against its doors. The mode text says "put back each quoted base line", and no call of the mode reads a base line, so this gap is also an F25 case (reasoned).

No candidate covers the gap (reasoned).

## 6. The proposal

**Put `code.diff` in `rota/roles/prompts/developer/touch_mistaken.tools`.** The generic push, runner.py 4196, then runs it in every `touch_mistaken` wake, as it does for the Architect's `touch_strayed` (reasoned: the same rule pushed it in s262). The `[removed lines]` block then shows the seat each removed base line in full, `basename` and `surrogateescape` included. The block comes from the line diff, `_removed_lines` api.py 18309, so the compare's rebind rule cannot hide a line there (observed: s262's and s243's prompts). Change one sentence of `touch_mistaken.md`: "For a `removal:` row, put back the lines of `[removed lines]` that belong to the grain the Architect judged, and keep the rest of the file."

- **Red test 1, from 128bec7e's row.** Build the `touch_mistaken` wake from night 172's register, with bg_3 at 128bec7e and the `mistake` row. Assert that the prompt holds `filename.encode("utf-8", "surrogateescape")` and `filename = os.path.basename(filename)`. Today s263's prompt holds neither (observed).
- **Red test 2, from s263's write.** Write an L1 case from s263's wake, mode `touch_mistaken`. Pass when the write's text holds `surrogateescape`, 4 of 5 runs on qwen3.5:9b. Today s263, s264 and s267 wrote the head's own text, 0 of 3 (observed).
- **The price: 3 cycles.** One build: the tools line, the sentence, two tests. One review. One gate with a re-record of `L1-DV-take-a-mistake-out` and `L1-AR-judge-a-stray-foreseen-or-a-mistake` if its prompt moves (reasoned: a text and a tools line are about 2 cycles, plus the L1 case).
- **The ruling of 2026-10-17 against a new refusal at commit.** The proposal adds a read to a wake, and no door. It does not depart from that ruling. It keeps his ruling of 2026-10-27: the Architect judges, and the route follows the judgement (reasoned).

What the change leaves out, and why:

- **The rebind rule in `_lost_in_block`.** It hid 1 statement on 1 row, and the row still existed by its other statements. Its other 2 hits were changes he asked for. The diff shows the hidden line to the restore seat. Record the rule on F7's debt beside pass 2b's return residue, and fix it when a row is missing in a night (reasoned).
- **The first-line note on the page and in `batches.strays`.** His page says "the branch `if isinstance(filename, bytes):`", and m118 shows that he read it as code to put back. Whole blocks on his page would cost his attention (reasoned).
- **The span door inside a docstring (W3, s243 and s263).** This is frame 313's gap. s264 and s267 sent the whole definition, which the door accepts, so the restore does not need frame 313 first (observed).
- **s239's empty body.** W1 under F37 removes the fail that started it (stack 1517).
- **The ff34266a row, still open.** `touch_strayed` reads only rows at the head commit, so a row on an earlier head is never judged. 128bec7e's row covered the same grain (observed).

## 7. The doubt

- **The base text was not enough for the `tests_failing` seats.** s243 to s245 had the same `[removed lines]` block. 1 of 4 wrote a restore, and its text held `basename` and not `surrogateescape` (observed). So qwen3.5:9b may still re-send the head with the diff in view. Red test 2 measures this before a night. If it stays below 4 of 5, the next shape is an offered call that holds the base definition with the head's docstring. That shape reverts any asked code change in the same definition, so it needs his word (reasoned).
- **A diff in a fix wake was measured harmful once.** On 2026-09-14, `L1-DV-challenge-a-test-that-contradicts-its-criterion` went from 5 of 5 to 0 of 5 with the diff pushed (observed: runner.py 4499). The `touch_mistaken` mode has no challenge route, so that case may not transfer (reasoned).
- **A large diff is cut first** (frame 134). On a large batch the block can fall out of the window (reasoned).
- **The `[removed lines]` block holds every removal of the file**, also the asked ones. The seat must keep the lines of the judged grain only, and the sentence asks a 9B seat to tell them apart (reasoned).
- **One sample.** One `mistake` judgement in three nights is the whole reach of the restore seat (observed).
- **What made s264 and s267 skip `batches.strays`** is not in the records.

Usage: about 150k on the harness counter against the cap of 120k.
