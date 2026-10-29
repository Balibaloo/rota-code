# Frame 345, review p3: commit 27291602 on seam2root (parent 7df90d09)

Verdict: NOT READY. The match binds wrong words to lines in 4 of the 24 replies. The act refusal then asks the seat for words that the one-word form cannot carry.

## (a) Verdict on each point

1. Match: WRONG in 4 of 24 replies (findings 1 to 3). It reads a verdict in one place, `_APPROVES`, as the brief allows.
2. Word table: MATCHES step 2. The exclude path comes from the line's prediction. `remove` defaults to `row`, which the prompt contradicts (finding 5).
3. Prompt (41 lines): it states the read-back rule and the ask rule. `now` has no example. One sentence contradicts the code (finding 5).
4. No new door: HOLDS. `_clause_spans` reuses `_CUE_CLAUSE`. The three new regexes name lines, not rulings. The `acts` refusal is a shape refusal that the brief orders.
5. l1_landing: no expectation contradicts the new form. The three drop cases expect `drop`/`row`, and `drop` maps to `row`. Two replies get a risky match (finding 6).
6. Tests: 171 passed, 7 xfailed. The f25 and night173 changes move calls to the object form or delete tests of the removed shift door. I did not read the f2 and ruled_refs diffs line by line.
7. Lost run: the seat gave line 1 `drop`, and line 1 showed "no words". The act check refused twice with the same text, and the runner ended the run. The change caused the loop (finding 2).
8. Split: SOUND BUT DOUBLE. A clarify has no numbered lines, so it cannot use `line_words`. Two writers of `shape_of` stay in `rulings_rule` (finding 7).

## (b) Findings

1. rota/roles/api.py `line_words`, about line 13420. High. CONFIRMED. A line number inside a reason or a quote names that line. In n172-m80-m81, "about lines 1 to 5" binds line 1 to the clause "The second line is wrong ... drop it". In n174-m47-m48, the quote "also remove lines 17, 18" binds lines 17 and 18 to the line 68 complaint. In n174-m53-m55, "added to line 3" binds line 3 to all three sentences, including "Change line 7" and "Change line 9". Fix: bind a line only to the clause where its number is the subject. Show a line named in a later clause as a second, separate quote.
2. rota/roles/api.py `_word_shape` 11612 and the act checks near 14411. High. CONFIRMED in seam2_after.txt lines 261 to 267. A line with "no words" that takes an act word gets `words` "". The check then says "Copy the words of his reply". The one-word form has no slot for words, so the seat repeats its call and the run ends. Fix: refuse an act word on a "no words" line with one sentence that says the line has no words of his and names `approve` or `ask`.
3. rota/roles/api.py `line_words`, the carry rule. Low. CONFIRMED. A clause with no number takes the lines of the clause before it. In n170-m58-m59, "Please keep what clear() prints exactly as it is now" binds to lines 5 and 6. The case expects that request as an `add` on lines 1 to 4. An ordinal with a noun other than "line" misses: in n172-m80-m81, "The first request is right" names no line. Fix: carry a clause to the lines before it only inside one sentence.
4. rota/roles/api.py `line_words`, `whole`. Low. CONFIRMED by code read. `_APPROVES` and `_BARE_AGREEMENT` read a verdict to choose the whole-reply binding. The brief allows this ("when it approves the page"). It is the one place where the match reads meaning. Fix: none in this pass. Record it as the one verdict read in the match.
5. rota/roles/prompts/liaison/landing.md line 19 against `_WORD_KINDS` 11607. Low. PLAUSIBLE. The prompt says that `remove` is "never a page line". The code gives `remove` the kind `row` on any line that is not a guess or a batch row. A1589b6d then retires the criterion. The brief says "a code line he names is source_line". The code tests the row, not his words. Fix: give `remove` the kind `source_line` only when his words hold a `file:line` or a code name, and otherwise refuse with the `drop` form.
6. tests/rota/cases/l1_landing.yaml lines 95 and 357. Low. PLAUSIBLE. "no, it should print the total ..." names no line, so `his_words` shows the whole reply beside every line. In "remove lines 7 and 8 and finish with line 2 alone", line 2 shows "remove lines 7 and 8". Neither case was re-run live under the new prompt. Fix: run the 12 l1_landing cases live once with ROTA_L1=1, then record them.
7. rota/roles/api.py `rulings_rule` 14278 and 14507. Low. CONFIRMED by code read. A page refuses `acts`, and a clarify still takes it. The acts loop now serves only a clarify. `answering.md` still teaches the map. Fix: move the clarify answer to the object form in a later pass, and then delete the acts loop.
8. Outside: rota/core/runner.py 2421. Low. CONFIRMED by code read. The runner shows `his_words` on a shift page. `rulings_rule` builds `his_lines` only when the page is not a shift page. The seat sees a match that code does not use. Fix: skip `his_words` when the page is the shift page.
9. Outside: rota/roles/api.py 14412. Low. PLAUSIBLE. The long form `{"verdict": "contest", "act": "drop"}` sets `line_n` to None, so `_word_shape` does not run. The long form gets no copied words and no `target_kind`. The brief says the door accepts both forms. Fix: run `_word_shape` for the long form too, and fill only the parts that it leaves empty.

## (c) Probes

- p1: a heredoc in the scratchpad ran `line_words` on all 24 replies of `l3_rulings.yaml` and compared the bindings with `expect_lines`. Output: C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/161c371b-f6a2-4d73-aebc-bae776885ab7/scratchpad/p3_lw.txt.
- p2: `python -c` printed the n174-m53-m55 reply and its line 3 binding.
- p3: grep on seam2_after.txt lines 253 to 469 for the n174-m53-m55 runs.
- p4: the five test files of point 6, ROTA_L1 unset, ROTA_MODEL=qwen3:8b: 171 passed, 7 xfailed in 47.87s.
- p5: grep on `l1_landing.yaml` for the replies and the `text_includes` expectations.

## (d) Usage

Input tokens: about 52k. Output tokens: about 9k. Total: about 61k. The 40k cap was exceeded.
