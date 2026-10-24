Does not stand. A revise of a note now slips past the keep door that refuses the same ruling as a contest.

# Frame 305, review of dcf7a6e3, the team-note case

The review read dcf7a6e3 on 52fe49e1 in `C:/Users/roman/rota_p305b`. The reviewer edited no tracked file. The two test files pass, 12 of 12.

## (a) Verdicts by point

1. Holds. A revise of a note lands exactly as a contest. The ledger row resolves, a decision keeps his words, and the carrier contests the note's row. Nothing is lost silently.
2. Fails. The change test misreads his words. "I don't understand line 2" (night 160, m11, a team's note) reads as a change. The test also reads "Leave line 11 as it is" as a change. See findings 1 and 2.
3. Partly holds. "not needed" as a drop matches the plain sense. His transcript holds no "not needed" about a line. The extra "don't need" pattern turns a change request into a drop. See finding 4.
4. Holds. `rulings.rule(ask=...)` is a real route at api.py 11234. The landing brief and three other refusals name it in the same form.
5. Fails in part. The new sentence is incomplete, and the m400 refusal lost its pointer to the request. The pinned string still checks the whole text, so no assertion count is lost. See finding 3.
6. Holds. The diff has four hunks: the new helpers at 11061 and the door at 11370 to 11411. `_KEEP_CHANGE` (10698), `_names_request` (10837) and frame 201's hold have no change. The diff has no CR byte and no debug print.

## (b) Findings

1. api.py 11376 with 11552. Severity high. Confidence high. CONFIRMED. The reversal door collects only lines ruled `contest`. Before this change a note revise never got this far. Now "Leave line 11 as it is." refuses a contest of line 11 and admits a revise of line 11. In `principal.land` the revise then lands as "overruled at signoff" (principal.py 2158 to 2213). The door rules against his keep. Law 6 breaks.
   Fix: count a note's admitted revise in `contested` at 11552, and skip `_CUE_KEEP` clauses in `_note_words`.

2. api.py 11097 to 11110. Severity low. Confidence high. CONFIRMED. The "any other word asks a change" rule reads a confusion or an agreement as a change. Night 160 m11 "I don't understand line 2" names a team's note and returns "change". Night 160 m45 "Line 2 and its check now say what I want" returns "change". "Line 11: no." also returns "change". A revise then closes the note as overruled, where the right call is `ask` or approve.
   Fix: admit "change" only on a clause with a change verb or a fault cue, and treat "understand" and "what I want" clauses as no change.

3. api.py 11407 to 11411 and tests/rota/test_request_page.py 649 to 653. Severity low. Confidence high. CONFIRMED by reading. The new sentence says "revise it only on words that say the change". The door also needs the words to name the note's line by number. A quote or an inherited reference does not count. In the m400 case his words asked to rewrite a request line. The old sentence "revise rewrites a line of what the principal asked for" pointed there. The new sentence points the Liaison back at the note.
   Fix: say "revise it only on words that name line N and say the change", and keep the request pointer when `said` is None.

4. api.py 11066. Severity low. Confidence high. CONFIRMED. The probe ruled "Line 11 should say that callers don't need to change anything." This is a change request, and `_note_words` returns "drop". "Line 11 should say the escaping is not needed." also returns "drop". His night 161 words use this shape: "people who already call confirm() don't need to change anything". The refusal then withholds the change route.
   Fix: skip the drop match when the clause holds "should say" or another `_KEEP_CHANGE`-style rewrite cue before it.

5. Outside the points. api.py 11084 to 11088. Severity low. Confidence high. CONFIRMED. The "own" test compares the first four letters only. "Remove line 11." on a note that holds "removed" returns "own", not "drop". The refusal then calls a plain drop ambiguous.
   Fix: give "own" only when the clause quotes the note's words around the drop word.

6. Outside the points. principal.py 2148 to 2235. Severity low. Confidence high. CONFIRMED. Revise and contest of a ledger row write the same rows. Only the string in `config.verdict:<id>` differs, and every reader takes both. The door's split between the drop and the change routes moves no data. It costs the Liaison one refused call on each drop.
   Fix: record this in the frame. A ruling on whether a drop and a change of a note need different landings is a question for Fable.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/51917779-9e71-4bcd-b8e5-e5cbc8b1f811/scratchpad/r305/`. Each one ran from the worktree root.

- `probe_land2.py`: ruled line 11 revise, then contest, on the frame 305 fixture, then ran `apply_rulings`. Both closed `l_9`, wrote the same decision and the same verdict refs.
- `probe_words.py`: ran `_note_words` on every reply of nights 160 and 161 in `.rota/clickI.principal.jsonl`.
- `probe_pages.py`: printed the named lines of m11, m45 and the shift page. Line 2 of m11 is a team's note.
- `probe_cases.py`: ran `_note_words` on nine edge sentences against two note texts.
- `probe_door.py`: ran `rulings.rule` through the sandbox with revise and contest on four sentences. "Leave line 11 as it is." refused the contest and admitted the revise.
- The night 161 database opened read-only. s357's page held line 11 as `l_5acefaa094`, an `unaddressed_answer` note about `tst_v2_format`.
- `pytest tests/rota/test_frame305_note_revise.py tests/rota/test_frame296_revise_note_text.py`: 12 passed.

## (d) Usage

Input tokens about 75k. Output tokens about 9k. Total about 84k. The harness gave no exact count.
