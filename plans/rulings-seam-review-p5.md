# The rulings seam, review of pass 5 at 899879de: the read-back line

## Verdict

Pass 5 stands with changes. The commit is clean of pass 4. The line, the "ok" path and the door exemption work as built. Two high findings stay open. First, his contest of the read-back cannot reach a ref that the new page does not hold, so a misreading stays on file with no route back to him (point 3). Second, the Liaison brief still says "every line gets a ruling" and "approves the others", so the model can approve the line for him (point 2). The new test file passes, 10 of 10.

## (a) The points

0. Contamination: none, CONFIRMED. No hunk of 899879de belongs to pass 4.
1. The line: holds, CONFIRMED. One line, last, on present and confirm only, written from the columns, ref in `body_refs`.
2. Confirmation: the code holds, CONFIRMED. The Liaison brief defeats the exemption, high, PLAUSIBLE (finding 2).
3. The deviation: fails, CONFIRMED, high. A contest reaches only refs that the new page holds (finding 1).
4. The line form: not enough, low, CONFIRMED. Two "ok" replies give two identical lines (finding 3).
5. The night principal: answers the line, CONFIRMED with a fake model call. Night 170 measures the Liaison mapping of "ok", not a check.
6. Weakened assertions: none in old files. The new file leaves the send-door exclusion and the model-approve path untested, low.

### Point 0, contamination

`git diff d449a696 899879de --stat` names 6 files. The patch files `runner.py`, `test_frame283_removal_on_ruling.py` and `test_frame339_removal_stray.py` are absent from the commit. The `api.py` hunks of the patch sit at 1359 to 1916, 6091 to 7865, 12756, 12780 and 20806 to 21545. The `principal.py` hunk of the patch adds code at 786. The `api.py` hunks of the commit are at 12590 to 12651 (the empty ruling), 12921 (the every-line rule) and 13665 (`_table_of_ref`). Each of them names `READING_REF`. The `principal.py` hunks of the commit are the read-back code at 983, 1919, 2147, 2400, 2654 and 2716. `git grep` at 899879de finds no "3.3, P11" text and no `granted(`. `_asks_removal` is at the same place in d449a696 and 899879de, and the base line `_note_words(words, order.index` is still there. So the pass 4 hunk at 12756 is not in the commit. The worktree has no change.

### Point 1, the line

CONFIRMED by probe A, section P1. A reply that rules three refs (approve, approve, contest with `remove how_it_works`) renders through `pending_asks` as one line, last:

`3. Your answer "3 is wrong: a fixed 15 percent, nobody ...", as the team read it: line 3 is wrong: remove how_it_works; 2 lines approved. Say ok, or say what we misread.`

The order ends with `reading:m10`. A shift page with the same ref renders no line, and its order drops the ref. `reading_line` reads `ruled()` rows, so no model writes the text. The send door at `sandbox.py` 4714 adds `readings_owed` for present and confirm only, and not for a park page or a shift page. No test covers that exclusion at the door (point 6). A page that holds the ref keeps the line after the reply is confirmed (finding 4).

### Point 2, confirmation

CONFIRMED by the test file and probe A, sections P2b and P2c. An "ok" with every line approve writes the `reading:` approve row. Each row of the reply then has `confirmed_by` set to the "ok" reply, and `provenance` reads `decided`. If the Liaison leaves the line out, `api.py` 12929 does not refuse, and the reply stays owed.

The gap is the Liaison. `rota/roles/prompts/liaison/landing.md` 33 says "A reply that says line 3 is wrong contests line 3 and approves the others". Line 49 says "Every line gets a ruling". The pass did not change the brief. Probe P2b sends the words "2 is fine, and 1 is fine as well." with an approve on line 3, the read-back line. The door takes the approve, and all three rows read `confirmed_by = m12`. So the door exemption works only when the model leaves the line out, and the brief tells the model not to (finding 2).

### Point 3, the deviation and the contest

CONFIRMED by probe A, section P3a. The test passes only because its page lists all three refs of the first reply again. On a real page, the refs belong to the new request. In probe P3a, page 2 holds `s1` and the read-back line. He says "2 is wrong: line 3 was not a remove. Keep how_it_works."

- The door refuses the key `l_1`, with the text "'l_1' is not a line of the page". `api.py` 12693 to 12708 also refuses a contest or a revise of a row from another request (frame 193, 2.F.7).
- The Liaison can only contest `reading:m10`. The old `l_1` row stays `landed`, `contest`, `remove`, with no `confirmed_by`. The item `how_it_works` stays `contested`, because the act ran before the read-back.
- `readings_owed` drops the first reply, because a landed row now rules its `reading:` ref (deviation 2).
- The next page reads back his contest reply as `Your answer "2 is wrong: line 3 was not a ...", as the team read it: 1 line approved.` The contest of the reading is a row on a `reading:` ref, so `reading_line` leaves it out.

What he sees after a contest: his correction appears only as the cut quote, next to "1 line approved". The wrong reading is never shown to him again, and nothing on file is corrected. If his reply rules only the read-back line, the reply has no row outside `reading:`. It is then owed nothing, and he sees no line at all. Design 2.3 item 2 says that the Liaison writes new rows on the refs that his words correct. The doors forbid that whenever those refs are off the page.

### Point 4, the line form

CONFIRMED by probe B, low. Two "ok" replies on separate pages wait. The next page shows two lines that are the same, word for word: `Your answer "ok", as the team read it: 1 line approved. Say ok, or say what we misread.` He cannot tell which page each line is about, so he cannot contest one of them. A second gap: the clause "line 3" uses the numbers of the old page. In probe P1 the read-back is line 3 of the new page, and its text says "line 3 is wrong". The rating is low because an approve-only line holds little to misread. The cost is high when he wants to contest one of the lines. Fix: name the subject of the earlier page, the ref of its line 1, and name the ref in each clause in place of "line N".

### Point 5, the night principal

CONFIRMED by probe C, with a fake `call` in place of the model. `AgentPrincipal.respond` sends the whole page, read-back line last, and lands the words as `Answer(verb='reply', text='ok')`. When the Liaison maps "ok" to an approve of every line, the three rows of the reply become confirmed. The probe does not show what the model writes. The brief rule is "Approve the page when every line says what you asked for". A read-back line is not a thing that the agent asked for, so the rule fits the line poorly. The prompt cuts each recent page at 1500 characters (`RECENT_CHARS`). So the model may not see the old line that "line 3" names, but it still sees its own words.

Night 170 measures three things from the line. The first is how often the reply of the agent touches the read-back line at all. The second is how the Liaison maps a page-wide "ok" onto the line (finding 2). The third is the night report line `read-back: N rows of M replies unconfirmed`. It always counts at least the last reply, because only the next reply confirms a reply. Night 170 does not measure whether a person catches a misreading. A contest from the agent also hits finding 1, so night 170 cannot show a correction that lands.

### Point 6, weakened assertions

CONFIRMED by the stat: the pass changed no old test file. `tests/rota/test_read_back.py` is new and passes, 10 of 10. Three gaps, low:

- `test_a_contest_supersedes_and_the_next_page_reads_the_new_rows_once` lists the old refs on the new page, so it hides finding 1.
- `test_a_reply_that_ignores_the_line_confirms_nothing` gives the Liaison a map without line 3. It does not test a model that follows `landing.md` and approves line 3.
- `test_the_send_door_writes_the_reading_ref_into_the_page` tests present and confirm. No test shows that the door writes no `reading:` ref on a park page or a shift page. `assert len(clauses) <= 3` repeats the equality above it.

## (b) Findings

1. `rota/roles/api.py` 12682 to 12708, against design 2.3 item 2 and `rota/roles/principal.py` 1008 to 1020 (`readings_owed`). High. CONFIRMED by probe P3a. A contest of the read-back cannot write rows on the refs it corrects when the new page does not hold them. The contested reply then leaves the owed list, and its wrong rows stay landed and reasoned. Fix: on a contest of `reading:<reply>`, admit the refs of that reply as keys past the off-page rule, and keep the reply owed until a newer landed row rules those refs.
2. `rota/roles/prompts/liaison/landing.md` 33 and 49, with `rota/roles/api.py` 12929. High. PLAUSIBLE: probe P2b shows that the door takes an approve of the line on words that skip it. The brief tells the model to rule every line and to approve the lines that he does not name. Fix: tell the Liaison to rule the read-back line only on "ok" to the whole page or on words about the line, and refuse a `reading:` approve when another line is contested.
3. `rota/roles/principal.py` 1036 to 1054 (`reading_line`). Low. CONFIRMED by probe B. Two approve-only replies give identical lines, and "line N" names a line of a page that he no longer sees. Fix: name the line 1 ref of the earlier page in the line, and the ref in each clause.
4. `rota/roles/principal.py` 2147 to 2151, and `confirmed_by` in `rota/core/schema.sql` 782 to 786. Low. CONFIRMED by probe P2c. A second open page that holds the same ref still shows the line after "ok". His later contest of that line then changes nothing, because `confirmed_by` takes any landed approve. Fix: render a `reading:` ref only while `readings_owed` holds it.

## Outside

- Outside, low, PLAUSIBLE. The act of a reading runs before the read-back. In probe P1, `how_it_works` is `contested` after the first reply. With finding 1, a misread `remove` has no route back from the read-back. Design 2.4 accepts the act, but it relies on the contest path that finding 1 blocks.
- Outside, low, PLAUSIBLE. A later reading on the same refs supersedes the rows of the earlier reply. `readings_owed` then drops that reply without a read-back. The first try of probe B, two "ok" replies on the same refs, left one reply owed. A misreading of the earlier reply is then never shown to him.
- Outside, low, CONFIRMED by reading. `ruled_refs_live` still uses `CREATE VIEW IF NOT EXISTS`, and nothing drops it. Only `provenance` is built again on `init_db`. The parent already had `confirmed_by`, so this pass breaks no old run database. A later change to that view will not reach an old database.

## (c) Probes

The three probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/e03f97fc-cdd4-4daa-864c-2ca4d7ef42a5/scratchpad/p5rev/`. Each one runs from the worktree root on new temp databases, with the helpers of `tests/rota/test_read_back.py`.

- `probe_a.py`: P1 renders the line through `pending_asks` and on a shift page, and shows `parse_reply(ask, "ok")`. P3a sends a contest of the line on a page without `l_1`. P2b sends an approve of the line on words that skip it. P2c sends "ok" on one of two pages that hold the same ref, then a contest on the other page. Its P4 section failed on a duplicate message id, and probe B replaces it.
- `probe_b.py`: two "ok" replies on separate refs, and the next page.
- `probe_c.py`: `AgentPrincipal.respond` with a fake model call that answers "ok", then the landing.
- Also: `pytest -p no:cacheprovider tests/rota/test_read_back.py -q` gave 10 passed. `git diff`, `git grep` and the hunk headers of the pass 4 patch gave the point 0 result.

## (d) Usage

- Input tokens: about 75k, an estimate from the budget counter.
- Output tokens: about 16k, an estimate.
- Total: about 90k. The cap of the brief was about 50k, and the review went over it.

## Pass 5b, the re-check of ff212ce3

Pass 5b does not stand yet. The door now takes a corrected row and refuses the approve of probe P2b, and finding 4 is fixed. Two gaps stay. On the night, a contest of the read-back still lands without the corrected rows (high). The approve guard reads the `words` argument of the Liaison and not his reply, so `words="ok"` still confirms a reading that his reply skips (high).

The tree is a `git archive` of ff212ce3 in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/e03f97fc-cdd4-4daa-864c-2ca4d7ef42a5/scratchpad/p5b_tree`. The probes are `probe_a_5b.py`, `probe_b_5b.py`, `probe_c_5b.py` and `probe_d_5b.py` in `p5rev/`, and each one ran from the tree root.

### Point 1, the two high findings again

Finding 1: fixed at the door, CONFIRMED by probe D. A contest of the line can now rule the earlier row only by its ref, and not by the act target:

- The key `l_1` lands. The old `l_1` row (`contest`, `remove`) becomes `superseded`, and the new row is `l_1` approve. The next page reads back the contest reply as `2 lines approved`.
- The key `how_it_works`, the target that the read-back text names, gets the refusal `'how_it_works' is not a line of the page. The page numbers its rows 1 to 2; use those numbers`.
- Probe P3b sends a contest of the line alone. The door accepts it. The first reply then leaves `readings_owed`, and its wrong rows stay landed and unconfirmed, as at 899879de.

On the night, the contest lands as in P3b, high, PLAUSIBLE. The line shows the target and not the ref. The landing wake builds `line_rows` from the order of the page at `runner.py` 2617, and the implementer reports that the wake lists no row of the earlier reply. The refusal text then sends the Liaison back to the page numbers. Fix: list the row refs of each read-back line in the landing wake, and refuse a contest of a `reading:` line that rules none of its rows.

Finding 2: fixed for the tested form, CONFIRMED by probe P2b. The words "2 is fine, and 1 is fine as well." with an approve of line 3 get the refusal `line 3 is his read-back line, and only his words confirm it`. Finding 4 is fixed: probe P2c shows no line on the second page after "ok". Low finding 3 is not fixed: probe B still shows two identical lines.

### Point 2, landing.md and an approve on words that are not his reply

The new sentences of `rota/roles/prompts/liaison/landing.md`:

- "A reply that says line 3 is wrong contests line 3 and approves the others, except the read-back line."
- "Every line gets a ruling, except the read-back line."
- "The read-back line starts "Your answer". It shows the principal how the team read an earlier answer, and it is the principal's alone. Rule it only from the principal's words: approve it when the words name it or approve the whole page, and contest it when the words correct it. Otherwise leave it out. When the words correct a row of that earlier answer, rule that row by its row id beside the contest of the read-back line."

The door does not refuse an approve whose words are not his reply, CONFIRMED by probe P2d. His reply is "2 is fine, and 1 is fine as well.", and the Liaison passes `words="ok"` with an approve of line 3. The door takes it, and all three rows read `confirmed_by = m12`. The guard in `rulings_rule` reads `words`, and nothing compares `words` with the body of `ctx.trigger`. Fix: read the guard from the body text of the trigger message, not from the `words` argument.

### Findings of pass 5b

5. `rota/roles/api.py`, `rulings_rule`, the read-back approve guard after 12733. High. CONFIRMED by probe P2d. The guard reads the `words` argument of the Liaison, so one paraphrase confirms a reading that his reply skips. Fix: run the guard on the `body_text` of `ctx.trigger`.
6. `rota/core/runner.py` 2617 and the contest branch of `rulings_rule` after 12733. High. PLAUSIBLE: the code takes `l_1`, but nothing shows the Liaison that ref on the night (probes P3a and P3b). Fix: list the row refs of each read-back line in the landing wake, and refuse a contest of the line that rules none of them.
7. Outside, low, PLAUSIBLE. The implementer reports an unchanged casestatus line after the `landing.md` edit, which changes the landing prompt. The register may not key those cases on that prompt. Fix: re-check one L1-LI case against the register before night 170.

Usage of the re-check: about 12k input tokens and 4k output tokens, an estimate.

## Pass 5c, the re-check of 44bae1ce

Pass 5c stands. Both high findings of pass 5b are fixed, CONFIRMED by probe E. Two low points stay open, and the landing cases need new recordings before night 170.

The tree is a `git archive` of 44bae1ce in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/e03f97fc-cdd4-4daa-864c-2ca4d7ef42a5/scratchpad/p5c_tree`. The probe is `p5rev/probe_e_5c.py`. It is probe D with the new tree plus a wake check, and it ran from the tree root.

### Finding 6, the landing wake

Fixed, CONFIRMED. The landing wake of a page with the line now carries `read_back`, for example `{'2': [{'ref': 's1', 'line': 1, 'verdict': 'approve'}, {'ref': 'calculate_tip', 'line': 2, 'verdict': 'approve'}, {'ref': 'l_1', 'line': 3, 'verdict': 'contest', 'act': 'remove', 'target': 'how_it_works'}]}`. So the Liaison now sees `l_1` beside the target that the line names. With the key `l_1`, the old row becomes `superseded`, and the new `l_1` approve lands. On the night, a contest can land with the corrected rows, if the Liaison follows the brief.

### Finding 5, the approve guard

Fixed, CONFIRMED. The guard reads the body of `ctx.trigger`. His reply "2 is fine, and 1 is fine as well." with `words="ok"` is refused, and no row gets a `confirmed_by`. His reply "3 is right." confirms the reading. His reply "ok" confirms it with `words="ok"` and also with `words="2 is fine."`, because his reply approves the whole page.

### Open, low

8. `rota/roles/api.py`, `rulings_rule`, the contest branch. Low. CONFIRMED by probe P3b. A contest of the line that rules no row of the earlier reply still lands. The reply then leaves `readings_owed`, and its rows stay unconfirmed and are never shown again. The wake now lists the rows, so this path needs a choice of the model, which lowers the rating. Fix: refuse a contest of a `reading:` line that rules none of the refs in `read_back`.
9. `rota/core/runner.py`, the `read_back` key. Low. PLAUSIBLE. Each row carries `line`, which is the line number of the old page. A Liaison that keys the row by that number rules the line of the same number on the new page, which is another ref, and no door refuses it. Fix: drop `line` from the `read_back` rows, or name it `old_line`.

Usage of the re-check: about 8k input tokens and 3k output tokens, an estimate.
