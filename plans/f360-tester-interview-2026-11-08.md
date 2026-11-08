# Frame 360: the interview of the Tester on the split word

Written 2026-11-08 12:18. Case `L1-TS-the-run-shows-a-split-word`,
`tests/rota/cases/l1_tester.yaml` line 1694, qwen3:8b, num_ctx 12288.
Rule C33 of `plans/method/reference.md` section 10.

## Result

The wake never shows the input of the Architect's program. The wake shows
the printout and then says "Write the result that the criterion's words
give for that input". No input is in front of the Tester, and no fold
width is in front of it. In 4 of 5 runs the Tester rebuilt the input from
the printout, joined "wo ⏎ rds" back into "words", and asserted that
`_foldline` gives the line back unchanged. In the interview, 5 of 5 runs
said that nothing was missing. That answer disagrees with the record, and
the disagreement is the finding.

The prompt also does not say what ⏎ means. The word "split" is only in
the item and in the criterion, and in the sample sentence itself.

The smallest change that the record supports: show the program's call,
with its input and its width, beside the printout, and say in the same
line what ⏎ marks. Measure it with the same case, re-recorded, 5 samples
on qwen3:8b, at the threshold of 4 of 5.

## 1. The condition that turns the interview on

`tests/rota/test_l1.py` lines 180 to 189 run `interview.conduct` when
both `ROTA_INTERVIEW` and `ROTA_L1` are set. The interview runs only for a
failed run that holds `outcome.user`. It makes one live call to
`OllamaBackend()` with the module pins `PINS`, so its model is
`ROTA_MODEL`. It has no cassette. `interview.record` writes the answers,
the ids that the prompt held and the calls to `case_interviews`.

`outcome.user` is the first wake (`rota/core/runner.py` line 5602), so the
interview quotes the printout back to the model.

## 2. What the Tester saw

The five gate recordings are `case_runs` seq 667888 to 667892, live, at
2026-11-08T12:09:28. The prompt is in `cassettes`, rowid 69954 for run 1.
The system turn is 7779 characters and is the same in all five runs. The
first user turn is 1754 characters.

The printout line and the two sentences, verbatim, as line 5 of the user
turn:

> The architect ran one program on the code, and it printed: This is a
> very long line that needs to be folded at a space so that wo ⏎ rds are
> not split but keep everything else as before.. The run shows what the
> code does, not what was asked. Write the result that the criterion's
> words give for that input.

The criterion's words, as `criteria.load` shows them:

> When _foldline folds a long line that holds spaces, each fold falls at a
> space, so that no word is split across the fold.

The item's words, as `batches.expect` shows them:

> When icalendar writes a long line, fold it at a space where it can, so
> that a word is not split, and keep everything else as before.

What the prompt holds, from the record:

- The fold width. Nothing in the system turn or the user turn says 75 or
  any width. The program text `_foldline("...", 75)` is in the fixture's
  `claim_runs.program` and is not in the wake. `claim_run_words` in
  `rota/roles/api.py` line 23280 renders only the stdout.
- The input. "That input" has no referent in the wake. The only text that
  can serve as an input is the printout.
- The mark ⏎. Nothing in the prompt says what ⏎ means.
  `claim_printout` turns each CR LF and space of a fold into " ⏎ ". A
  reader who is not told that rule sees "wo ⏎ rds" and no line break.
- The word "split". It occurs in the item ("a word is not split"), in the
  criterion ("no word is split across the fold") and inside the printout,
  because the sample sentence says "words are not split". The rule
  applies to the output of `_foldline` only. The prompt gives no rule that
  holds across the whole wake.
- The place of the printout. It is at character 375 of the user turn,
  before `[criteria.load]` at character 1110. It stays at the same place
  in every later turn. The 600-character cap of `claim_printout` does not
  apply, because the printout is 123 characters. No "(cut)" occurs, and
  the context does not evict the printout.

What the Tester sent, by the record:

| Run | First encode | Last encode |
|---|---|---|
| 1 | `_foldline("<line>") == "<line>"` | `_foldline() == "<line>"` with a stdin stream |
| 2 | `_foldline("<line>") == "<line>"` | `_foldline() == "<line>"` with a stdin stream |
| 3 | `assert "_foldline" in line` | captured stdout `== "<line>"` |
| 4 | `_foldline("<line>") == "<line>"` | `_foldline() == "<line>"` |
| 5 | `_foldline("<line>")` with no import | captured stdout `== "<line>"` |

`<line>` is the printout with " ⏎ " removed and "wo" and "rds" joined back
into "words". No run asserted on a fold, and no run gave a width.

A second fact from the record: a door turned the Tester away from the
return value in 4 of 5 runs. The first error in runs 1, 2 and 4 says "the
criterion, its ticket or the principal's words say it prints". None of
the three says "prints". The only word of the `PRINTS` family
(`rota/roles/api.py` line 9241) in that material is "writes", in the item.
After the error the runs moved to stdin streams and to captured stdout.
I did not trace the door's branch. The cause is plausible, not confirmed.

## 3. The interview

Run on 2026-11-08 at 12:17, by:

```
ROTA_L1=1 ROTA_INTERVIEW=1 ROTA_MODEL=qwen3:8b ROTA_NUM_CTX=12288 pytest 'tests/rota/test_l1.py::test_l1_case[L1-TS-the-run-shows-a-split-word]'
```

The 25 session calls replayed from the cassettes of 12:09, so the five
sessions are the five recorded ones. The five interview calls were live.
The case failed 0 of 5, as recorded. `case_interviews` seq 451 to 455.

Answers, verbatim, run 1 (runs 2, 4 and 5 are the same in form):

> 1. You were asked to write tests for the criterion `c_a589b8` and
>    determine if it could be encoded into a testable form.
> 2. The ids you were given are: `b_ea9481`, `c_a589b8`, `tk_d15043`.
> 3. The functions you called are: `batches.expect`, `criteria.load`,
>    `glossary.lookup`, `references.load`, `tests.triage`, `tests.encode`,
>    `ledger.log`. You considered but did not call:
>    `msg.question_researcher`, `msg.question_terminologist`,
>    `msg.question_vision_keeper`.
> 4. Nothing.

Run 3, verbatim:

> 1. You were asked to write a test that verifies the criterion about
>    folding a long line at a space so that no word is split across the
>    fold.
> 2. The ids given were: `b_bc6439`, `c_076a52`, `tk_48ca31`.
> 3. The functions called were: `batches.expect`, `criteria.load`,
>    `glossary.lookup`, `references.load`, `tests.triage`, `tests.encode`.
>    Considered but not called: none.
> 4. Nothing was needed to decide.

## 4. The interview against the record

- Question 1, the job. 4 of 5 runs say "write tests ... determine if it
  could be encoded". Run 3 names the fold rule. No run names the claim
  that no code changed, the Architect's run or the printout. The wake
  carries all three in lines 4 and 5.
- Question 2, the ids. 4 of 5 omit the item id, for example `i_9d8bad`,
  that `tickets.load` shows. Run 2 lists it. No run invents an id. The
  ids are not the gap here.
- Question 3, the calls. Runs 1, 3 and 5 omit `tests.consult` and
  `tickets.load`. Runs 3 and 5 omit the repeated encodes. No run names a
  call it did not make.
- Question 4, the gap. 5 of 5 say "Nothing". The record says that the
  wake asked for "the result that the criterion's words give for that
  input" and held no input and no width. The answer and the record
  disagree, and that disagreement is the evidence of C33.

The fixed questions do not ask about the printout. The interview can show
that the Tester did not notice a missing input. The interview cannot show
how the Tester read "wo ⏎ rds". An input question for this case would be
"Copy the line the architect's program printed, and give the input of
that program." That question is outside this frame.

## 5. What the prompt lacked, from the record

1. The input of the run. The wake shows the output and asks for the
   result "for that input", and the input is not shown. The Tester then
   uses the only text that it has, the printout, as the input.
2. The fold width. With no width, the line of 123 characters has no
   reason to fold. "Keep everything else as before" then gives the line
   back unchanged, and that is the assertion of 4 of 5 runs.
3. The meaning of ⏎. A reader who is not told the mark sees no line break
   and no split, so "wo ⏎ rds" does not read as a split word.
4. A word of the case, not of the wake: the sample sentence says "words
   are not split". The printout repeats the rule as text. That can make
   the printout read as a statement and not as an output. A re-record
   that keeps this sentence keeps the confound.

The place of the printout is not the cause. It is early in the user turn,
it is short, and nothing cuts it.

## 6. Proposal (a proposal only, nothing is changed)

Change one line of the wake. `claim_run_words` shows the call that the
program made, with its input and its width, and says what the mark
means. For example:

> The architect ran `_foldline("This is a very long ... before.", 75)` on
> the code, and it printed: ... so that wo ⏎ rds are not split .... A ⏎
> marks a fold: a line break and then a space.

The source of the call is `claim_runs.program`, which is on record for
every run. The change is general. Any claim run gives the Tester an
output, and the output has no meaning without its input.

The measure:

1. Re-record `L1-TS-the-run-shows-a-split-word` on qwen3:8b, 5 samples,
   num_ctx 12288, with `ROTA_INTERVIEW=1`.
2. The case passes at 4 of 5.
3. Each test calls `_foldline` with a width and asserts on the fold, not
   on the unchanged line.
4. If the case stays red, read the new interviews. An answer to question
   4 that still says "Nothing" with the input in the wake points away
   from the wake and at the door that says "prints".

The door that says "prints" is a second candidate. It fired in 4 of 5
runs on material that says "writes" and not "prints". A judge decides
whether it is part of this frame. Its measure is the same re-record.
