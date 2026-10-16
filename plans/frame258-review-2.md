# Frame 258, review 2: the diff review of 59030519, pass 2

Rota workflow throughout. Read-only review on the worktree `C:/Users/roman/rota_review_258` at 59030519. Date 2026-10-16. Opus.

Verdict: **accept**. No high finding. 7 low findings for the night, and 1 low outside the points.

## (a) The verdict on each point

1. W1 holds. No tried reply agrees, then corrects, and still reads as agreement alone, except replies that use "correct" as a verb (finding 5).
2. W2 has three kinds of wrong spare and one kind of wrong refusal. The stop list is too narrow for batch talk, and it lets "don" through (findings 1 to 4).
3. count2.py counts what the report says. The re-run gives the same output. The 5 and 5 are right. One docstring count is wrong (finding 6).
4. Both old assertions were measurements, not rulings. The change contradicts no ruling in LAWS.md, DECISIONS.md or the archive.
5. The one caller passes `request_texts`. The default is safe. No prompt and no op list changed.
6. m359 is a wrong spare, and the predicate should refuse it.

## Point 1: W1, agreement alone

`_AGREEMENT_ALONE` fullmatches the joined sentences against the `_AGREE` words plus "so", "and", "then", "please", "I approve", and "this/that/it/the page/everything ... matches/is right/looks right". Any word outside the set breaks the match, so the predicate fails safe (observed: `f258r2/shapes.py`, 2026-10-16).

Shapes tried, with the result (observed: `f258r2/shapes.py`):

- Read as NOT alone, so the contest stays open: "ok, but keep it small", "Ok, go ahead, but keep it small.", "Yes, then make it smaller.", "ok so go ahead and fix it", "Not ok", "Ok, the others are wrong", "Ok. Then again, no.", "Yes, correct it", "That's right", "Approve it", "Ok, and approve the page".
- Read as alone, rightly: "Yes, that is right, thanks", "Looks good to me, go ahead.", "yes please, and then the others", "Ok?".
- Read as alone, wrongly: "Fine, correct the rest.", "Ok, correct everything else.", "Right, so correct the others.", "Good, right, so correct". Finding 5.

The wrong shapes use "correct" as a verb. "the rest", "the others" and "everything else" are `_AGREE` phrases, so the instruction reads as agreement (reasoned: `_AGREE` at api.py 8750). No night shows the shape (observed: 0 contests outside the 5 known over the 73 night databases, tips AL to AS and the older clickI copies, `f258r2/p1_other.py`). The near misses "That's right" and "Approve it" read as not alone. They only leave a wrong contest open, as before (reasoned).

The new branch sits before the `request_lines` check, so it reaches confirm pages too. Over the nights, 1332 present rulings and 181 confirm rulings rest on agreement alone. No such page holds a question mark, so no "yes" answers a question that asks for a contest (observed: `f258r2/p1_verbs.py`). No shift or clarify ruling rests on agreement alone (observed: the same probe).

## Point 2: W2, the content-word match

The stop list `_BATCH_TALK`: change, team, work, fix, failing, test, keep, going, drop, please, want, line, page, rather, again, give, review, one, like, with plural forms. Judgement: the list holds the words of the three observed replies and little else. It lacks branch, diff, file, code, commit, broke, pass, try, time and the stems before "n't". The cut of a final "s" runs before the subtraction, so "fails" and "fixes" stay as "fail" and "fixe" (observed: the word sets in `shapes.py`).

Wrong spares, a sentence about the batch that spares line 1 (observed: `shapes.py`, request echo_json unless named):

- A build verb at the start: "Please make sure the tests pass.", "Use the same branch.", "Take your time and fix it properly.", "Show me the diff first." Finding 1.
- The request's own subject: "Please don't drop the JSON change.", "Keep the echo helper, the team is close.", "The new helper broke the pager tests, so fix them." m359 is the observed case of this kind. Finding 2.
- The token "don": "Please don't drop this change." spares line 1 against the request text "Add a quiet flag so the command doesn't print anything, and don't write the log." `_prose_words` keeps "don" from "don't". Finding 3.

Wrong refusals, a sentence that corrects the request and is refused (observed: `shapes.py`): "Sort the keys.", "Instead, emit YAML.", "Actually I want pretty output with an indent of two.", "Can you have it accept a list too?". Each shares no word and opens with no build verb. Finding 4.

## Point 3: the count script

count2.py opens every `clickI_night*.db`, 73 files, read-only. It reads landed rulings, skips clarify asks and `m_shift` asks, and keys the page order on `per_item` (observed: `f258/count2.py`). The re-run against the worktree api.py matches `count2_post.out` with no difference (observed: `f258r2/count2_rerun.out`, diff exit 0).

- P1: 1513 rulings on agreement alone, 5 with a contest, 1508 all approve. The 5 are 121 m119, 138 m161, 139 m132, 147 m182 and 151 m23 (observed).
- P2: 5 line-1 contests reach the m263 guard. 2 are spared, m264 and m359. 3 are refused, m167, m219 and m46 (observed).
- The databases outside the glob add no agreement-alone contest. The live `clickI.db` holds m23 "ok", which the night 151 copy already holds (observed: `f258r2/p1_other.py`).
- The `_names_request` docstring says the guard "met 4 line-1 contests, and 3 were about the batch". The count shows 5 and 4. Finding 6.
- The count reads `items.text` at the night end. A contested wake amends an item text, so the live text at the ruling can differ. Finding 7.

## Point 4: the two changed old assertions

- m119 and m132, `test_a_plain_approval_on_a_contested_line_is_admitted`: added at 8194e3a0, pass 1b, from the first low of review 1. Review 1 called both replies plain approvals, and called the refusal right with a wrong text (observed: `plans/frame258-review-1.md`, lines 19 to 21 and 42). The old assertion was a measurement pin for one refusal text. The new assertion refuses the contest, and that agrees with review 1 (reasoned).
- m181 "Ok, go ahead.": added at 91d8fcc3, frame 234 pass 2b, as "tests pin the silence on m28 and m181" after a low of review 3. Pass 2 called the silence "silent by design", a scope choice of that door (observed: `plans/archive/stack-2026-10-15.md`, lines 29 to 31). The night 147 read lists the contest as admitted and relayed to the Architect, and bg_4 merged later (observed: `plans/night147-read.md`, lines 183 and 545). No ruling by Roman holds the row (observed: git log -S and the grep of the archive).
- Law 6 in `rota/LAWS.md` and `rota/DECISIONS.md` say that a contest goes back with words, and that "Silence approves" is gone. An explicit "ok" is words, not silence, so the change contradicts neither (reasoned: `LAWS.md` 183 to 192, `DECISIONS.md` 1363 and 1428 to 1431).

## Point 5: the new argument

The new argument is on `_line_refusal`, not on `rulings_rule`. The signature of `rulings_rule` did not change (observed: the diff). `_line_refusal` has one caller, `rulings_rule` at api.py 9491, and the call passes the ids and the `items.text` of the `asked` lines (observed: grep). With no texts, `_names_request` spares line 1 only on a build verb, so the default refuses more and spares less (reasoned: api.py 8955 to 8965). The commit touches `rota/roles/api.py` and one test file only. No prompt, op list or schema changed (observed: git show --stat). The touched test file passes, 68 passed (observed: pytest in the worktree).

## Point 6: m359

Words: "Please keep going with a fix and don't drop this change. Line 5 is wrong because it still touches the Command class in core.py, and the flag belongs only to the version option in decorators.py. Keep the change there and add the Python version to the end of the message only when the flag is on." The predicate should refuse it, because the words ask to keep the change and the last sentence restates the request for the batch (reasoned).

## (b) Findings

1. api.py 8936 to 8938, `_BUILD_VERB`. Low. CONFIRMED: "Please make sure the tests pass.", "Use the same branch.", "Take your time and fix it properly." and "Show me the diff first." spare line 1. m263 also shares "version", "interpreter" and "info" with its request, so m263 does not need the verb branch. Fix: drop the build-verb branch, or drop make, use, take and show from it, and re-check the fixture "Also, take the tip in cents."
2. api.py 8941 to 8965, `_names_request`. Low. CONFIRMED: a batch sentence that names the subject of the request spares line 1, "Please don't drop the JSON change.", and m359 on night 143. Fix: read keep, drop, give up and going in the sentence as a veto on the spare, not as words to remove.
3. api.py 8962, `words()` over `_prose_words`. Low. CONFIRMED by probe: "don" from "don't" matches a request text with "don't". 0 of 86 in_scope texts over the nights hold a negative contraction (observed: `f258r2/neg.py`). Fix: add don, doesn, isn, won and didn to `_BATCH_TALK`.
4. api.py 8921 to 8927, the line-1 refusal. Low. PLAUSIBLE: a correction of the request with no shared word and no build verb is refused, such as "Sort the keys.". The seat then approves line 1, and the correction is lost. The nights hold 1 right case, m263, and m263 passes. Fix: count the line-1 refusals on the next night, and judge each one before a wider predicate.
5. api.py 9033 to 9038, `_AGREE_PHRASE` with `_AGREE`. Low. CONFIRMED by probe: "Fine, correct the rest." reads as agreement alone, and its contest is refused. No night shows the shape. Fix: exclude "correct" when "the rest", "the others" or "everything else" follows it.
6. api.py 8949 to 8954, the `_names_request` docstring. Low. CONFIRMED: the docstring says 4 contests and 3 about the batch, and count2 shows 5 and 4. Fix: write "met 5 line-1 contests, 4 were about the batch, and the rule refuses 3".
7. count2.py, the `items.text` read. Low. PLAUSIBLE: a contested wake amends the item text during the night, so the count can match words that the live text lacked. Fix: none for this pass. Read the text at the ruling time when a night read counts the guard.

Outside the points:

8. The night 147 m181 page. Low. CONFIRMED: the page shows two request items, `version_option_show_python` and `ver_opt_show_py`, for one ask (observed: `count2_rerun.out`, line 1396). Fix: none here. The night read places it.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/70d05878-d20b-4db9-854a-2acc9b5a66bc/scratchpad/f258r2/`. Each probe imports the worktree `rota` package and opens every database with `mode=ro`.

- `p1_verbs.py`: the agreement-alone rulings over the 73 night databases by verb, the pages with a question mark, and the shift and clarify rows.
- `p1_other.py`: the same predicate over tips AL to AS, `clickI.db` and the older clickI copies.
- `shapes.py`: 20 W1 shapes and 18 W2 shapes against `_AGREEMENT_ALONE` and `_names_request`.
- `rerun.py`: runs `f258/count2.py` with the worktree on the path. Output: `count2_rerun.out`. The diff against `f258/count2_post.out` is empty.
- `neg.py`: the in_scope texts with a negative contraction over the night databases.
- pytest on `tests/rota/test_frame234_verdict_lines.py` in the worktree with `ROTA_MODEL=qwen3:8b`: 68 passed.

## (d) Usage

The agent cannot see the harness line, so these numbers are an estimate from the context counter: about 85k input tokens, about 12k output tokens, about 97k in all. The harness line is the record.
