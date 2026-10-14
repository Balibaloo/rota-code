# Frame 234, pass 2b: diff review 4 of the unnamed-line refusal

Rota workflow, the Liaison's `rulings.rule` door. Worktree `C:/Users/roman/rota_rv234d` at 91d8fcc3 over 695d92e5. Reviewer: an Opus agent, read-only, 2026-10-14.

## (a) Verdict

Accept. No high finding. Two low findings, which the next pass can take or leave.

1. Point 1, review 3's high through the door: closed. m131 with the added sentence is refused and names 5, 6 and 8 to 11. m263's shape lands.
2. Point 2, `item_lines`: correct for the line kinds the nights hold. 0 unnumbered corrections of a non-item line on nights 143 to 147.
3. Point 3, 143 m104 and m160: each refusal is right by the frame's rule. The seat then approves the note.
4. Point 4, STE and CR: the refusal text and the comments are STE. 0 CR bytes in the two files.

## (b) Points

Point 1. `tests/rota/test_frame234_verdict_lines.py` runs both shapes through `rulings.rule` on an 11-line page. The file gives 47 passed at HEAD. With " Please also keep the tests small." appended, the door raises "The words name lines 3, 4 and 7 and do not name lines 5, 6 and 8 to 11." m263's shape, "Line 3 is wrong because the tip is rounded. Also, take the tip in cents.", with a contest of the criterion line 4, lands with `c3: contest`. The same words with a contest of the note line 6 raise "The words name line 3 and do not name line 6."

Point 2. The call site marks a line as an item line when its id is a row of `items` or `criteria`. The probe `kinds.py` classified every ref of every present, confirm and park page on nights 143 to 147. The pages hold items, criteria, batches, ledger notes, constraints, glossary terms, model areas and statements. Five refs on night 144 and seven on night 146 are rows of both `items` and `decisions`, and the set counts them as items. No page holds a challenge row. `_is_team_note` counts ledger, constraints, glossary terms and model areas as notes, so those kinds match the frame's rule. Statements, the principal's own answers, are neither item nor note, and the set does not spare them (finding 2). The probe `p4.py` found 17 rulings with an unnumbered sentence beside an unnamed contest. The real `_line_refusal` (`p5.py`) refuses four of them: 143 m104 and m160, 145 m65, and the report's 145 m55. Each refused line is a ledger note. 146 m6 and 147 m6 contest constraints, and the words number them, so the door lets them land. The count of unnumbered corrections that fault a non-item line is 0.

Point 3. 143 m104: line 6 is the Vision Keeper's note "The echo_json helper will print an object as compact JSON on one line". The unnumbered sentence asks for the standard json module and no new dependency. That sentence does not touch the output form, so the contest of line 6 does not rest on the words. The refusal is right. The seat then approves line 6 and keeps the contest of line 3, and the words reach line 3's owner. 143 m160: line 10 is the note "The echo_json helper is defined in Click's utils module, next to echo". The words replace the request with a confirm flag, and the unnumbered sentence sets the flag's default. That sentence does not correct line 10. The refusal is right by the rule. The seat then approves the note, and the fold carries an approved note about the old echo_json request beside a contested line 2. The contest of line 2 already sends the change of request to its owner, so the note carries no new error.

Point 4. The refusal text has three sentences in the active voice, each under 20 words. The new comment has five sentences, one topic each. The docstring line for `item_lines` is one sentence. `tr -cd` counts 0 CR bytes in `rota/roles/api.py` and in the test file.

## (c) Findings

1. `rota/roles/api.py:8354-8363`, low, PLAUSIBLE. The comment says the sentence "never corrects a team note", and the code spares item and criterion lines only. A statement line, the principal's own answer, on line 2 or later is refused like a note. No ruling on nights 143 to 147 meets this case (p4.py, 0 statement rows). Fix: spare every line where `_is_team_note` is false, or name statements in the comment.
2. `tests/rota/test_frame234_verdict_lines.py:406-412`, low, CONFIRMED. `_page11` inserts c1 to c3 into `items`, and its docstring calls them criteria. No test covers the `criteria` branch of the UNION in `rulings_rule`. The night probe covers the branch: 143 m160 marks its `criteria` rows 3 to 5 as item lines. Fix: insert one criterion through the `criteria` table in `_page11`.

## (d) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4a757f92-bd97-4750-9830-bd149134e576/scratchpad/rv234/`. Each opens the night databases read-only.

- `kinds.py` and `none.py`: the table of each page ref on nights 143 to 147.
- `p4.py`: rulings with an unnumbered sentence beside an unnamed contest, by line kind, from the worktree's code.
- `p5.py`: the real `_line_refusal` at HEAD on 143 m104, m160, m326, 144 m439, 145 m65, 146 m6 and 147 m6.
- `p6.py`: the ledger rows on 143 m104's line 6 and m160's line 10.
- Pytest: `tests/rota/test_frame234_verdict_lines.py` from the worktree, 47 passed.

## (e) Usage

About 40k input tokens and 8k output tokens, about 48k in total, from the context counter. The brief's cap was 30k, and the probes ran over it.
