# Frame 328, the residue: review of 130d0629

Verdict: the change stands. It has four low findings and one outside finding, and none of them blocks the change.

The commit is `130d0629`, "fix(core): the criterion half reads one unpaired outer quote mark", on `4bb2656b`. The review worked read-only in `C:/Users/roman/rota_r328r`, a detached head at `130d0629`. It ran no model call.

## (a) The points

1. Holds. A quote of the older text is refused in all eight forms of the probe. These include bare, s336, s327, m189, an opening mark only, a closing mark only and an opening `"`. A quote below the floor is refused as short.
2. Holds, with findings 2 and 3. Seventeen of the twenty probe quotes pass, including texts that start or end with a mark. The other three quotes are right quotes with an apostrophe and one trailing mark, and the door refuses them. HEAD refuses them too, so the change adds no refusal of a right quote.
3. Holds. The diff has three hunks in `sandbox.py`, and the test half of `_cites` is the same text as at `4bb2656b`. `_code_only`, `_unescaped`, `_escaped_view`, `_challenge_repeat_refusal`, `_same_refs_refusal` and `_green_at_head_refusal` have no hunk. The new refusal block runs only for `table == "criteria"`.
4. Holds on the criterion refusal, with finding 1. The short refusal still shows the raw form only.
5. Holds. The completions of s336 seq 5 and s327 seq 3 hold the fixtures with each backslash doubled. That is the source form of the call, and the binder reads `\'` as `\'`. The m189 fixture is in `messages.body_text` verbatim.
6. The seven files give `1 failed, 111 passed in 13.11s`. The red test is `test_invoke_door.py::test_a_session_with_no_batch_reads_the_root` with "DID NOT RAISE <class 'ValueError'>" at line 381. The same test is red on a `git archive` copy of `4bb2656b`, which has no `_seat_forms`. The failure is in `tests.encode` of a Tester with `batch_id=None`. That path does not call `_challenge_evidence`, so the failure does not touch the quote check.
7. Holds, with finding 4. The commit touches no existing test. It adds one file, and it removes no assertion and no pin.

## (b) Findings

1. `rota/core/sandbox.py:1381`, low, CONFIRMED. The short refusal shows the raw quote and does not show the form the door counted. Probe `p1` sent `'(a/b/c.txt)'.`, which is 14 characters. The refusal said "holds `'(a/b/c.txt)'.`, and it is shorter than 12 characters". The escaped `'\'c.txt\''.` is 12 characters, and it gets the same text. A seat that counts its own quote reads a contradiction. Fix: in the `short` branch, name the `_seat_forms` form and its length when that form differs from the raw quote.
2. `rota/core/sandbox.py:1316`, low, CONFIRMED. A closing mark is cut only when no opening mark comes first and the cut leaves the marks paired. The opening cut has no such gate. Probe `p2` used the live text "The function's docstring shows that shorten=True gives c.txt." The probe sent that text with one trailing `'`, then the same text with `'.` in place of the full stop. The door refused both quotes. Its refusal says that the door "drops one outer quote mark at each end", but it shows the read form with the mark still there. HEAD also refuses these quotes, so this is no regression. Fix: append the cut form without the parity gate, because `[q]` and the other forms still come first.
3. `rota/core/sandbox.py:1309`, low, CONFIRMED. The pairing rule of the display order gives the wrong first form when a paired quote holds an apostrophe. Probe `p4` sent `'The function\'s docstring shows that shorten=True gives c.txt.'` against version 2 of the row. The refusal showed "the quote is `The function's docstring shows that shorten=True gives c.txt.'`" with the trailing mark kept. Version 2 of c_1 holds "function's", so a seat that quotes it inside paired marks can get this text. Fix: put the inner form first whenever the closing mark matched.
4. `tests/rota/test_frame328_criterion_quote.py:141`, low, CONFIRMED by a read. The floor test matches only `^quotes= holds \``, and every refusal of this door starts with that text. So the test does not pin the floor reason. Probe `p1` shows that both cases now give "shorter than 12 characters". Fix: match "shorter than 12 characters" in both cases.
5. Outside. `rota/core/sandbox.py:1288`, low, CONFIRMED. The rule now admits a quote whose last two characters are not in the live text. Probe `p1` sent `'returns 'c.t'.` against "... returns 'c.txt'." and it passed through the form `returns 'c.t`. The form is still a span of 12 characters, so the floor holds. Pass 1 recorded this residue as open question 3. Fix: none needed if the frame accepts open question 3. Otherwise, demand a closing mark only where the form ends at the end of the row.

## (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4cdad7e1-c78d-472d-86ab-f4c72d52763e/scratchpad/r328r/probe_quote.py`. It builds the test file's batch with a given criterion text and sends `msg.challenge_tester` through `build`. `p1` covers points 1 and 4, `p2` covers point 2, and `p4` prints the refusals in full. The probe printed that `sandbox` loaded from the worktree.
- An inline read-only probe opened `D:/repos/rota/.rota/clickI_night167.db` with `mode=ro`. It compared the fixtures with `turns.completion` and `messages.body_text`.
- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4cdad7e1-c78d-472d-86ab-f4c72d52763e/scratchpad/r328r/old` holds `git archive 4bb2656b`. The red test ran there. Deviation: the brief asked for the run in the same worktree. That needs a tree change, and the review rules forbid one.
- pytest ran the seven test files at `130d0629` with `ROTA_MODEL=qwen3:8b`.

## (d) Usage

The harness reports about 59k tokens used in this review, measured from the budget counter. It does not report the split between input and output. The brief's cap was about 50k, and the review went past it by about 9k.
