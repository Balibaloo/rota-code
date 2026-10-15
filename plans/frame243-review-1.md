# Frame 243, review 1 of 26940b74 (source in 7618bfb5)

Reviewer: a read-only Opus agent, 2026-10-15. Worktree: `C:/Users/roman/rota_r243` at 26940b74.
Workflow: the rota workflow, the seats.

Verdict: accept with two fixes. Both doors work on night 148's data. The words reach the right seats and rows. Two defects stay. The contest label points at the current text, and a contest makes the whole criteria push fall back from a table to JSON.

## (a) Verdicts on the points

1. The words: CONFIRMED. At HEAD both wakes carry the words whole after `text`. At e11dde47 they do not.
2. The reach: CONFIRMED as briefed. Only Developer and Tester wakes, only `contest` verdicts on that criterion id. A `revise` verdict does not land (finding 3).
3. The size: CONFIRMED by code and probe. No new size rule. Three contests add about 830 characters. `_fit` cuts the wake tail, `code.read`, and says so.
4. The label: CONFIRMED defect, low. "Line 2" names a page line the seat never saw. Show the contested text from `rulings.texts`, and do not strip the words (finding 1).
5. The supersede door: CONFIRMED. s189's call is refused at HEAD and lands at e11dde47. Seat-on-seat is admitted. The offer carries id, text, refs, resolves_ledger.
6. The tests: CONFIRMED. 3 red at e11dde47, 31 green at HEAD. No old test line changed. Three of the new tests skip without `.rota/clickI_night148.db` (finding 4).
7. Stale: CONFIRMED that stale 0 is right. `key_for` hashes the whole user text, which holds the pushed rows. No recorded Developer or Tester case seeds a contest ruling.

## (b) Findings

1. `rota/core/runner.py:486-491`, low, CONFIRMED. The label "the principal said, contesting it" binds the words to the current `text`. The words contest an older text. In night 148 they say "Line 2 is wrong because ... not from sys.version". The current text already says `sys.version_info`. So the seat reads a contest of a sentence it cannot see. Also every landed contest shows forever, after a later approve too. Night 148's r_3340e1e9d9 (rowid 18) approves `ver_opt_show_py` after r_4c8fd5d3ad. A stripped form loses the reason and still hides the target. Fix: push each contest as `{"he contested this text": texts[ref], "he said": words}`, and keep the words whole.
2. `rota/core/runner.py:484-492` with `_as_table` at `runner.py:1442-1448`, low, CONFIRMED. One contested row gives that row a key the other rows lack. `_as_table` then refuses ragged rows, so the whole `criteria.load` push renders as JSON. Probe p2: two rows at e11dde47 render as a table, and at HEAD as JSON with every key repeated and every quote escaped. Every criterion in a contested batch changes form and size. Fix: add the key to every row, with an empty list where no contest exists, or render the words as a line after the table.
3. `rota/core/runner.py:470`, low, CONFIRMED. `contest_words` keeps `verdict == "contest"` only. `_last_word_lines` (`runner.py:436`) and `principal.py:717` treat `revise` as a correction too. Probe p4: a `revise` ruling on the criterion pushes nothing. Fix: accept `("contest", "revise")`, and say the verdict in the label, or record why `revise` stays out.
4. `tests/rota/test_pushes.py:199` and `tests/rota/test_criterion_contest.py:367`, low, CONFIRMED. The three night-148 tests read `.rota/clickI_night148.db` from the checkout and skip when it is absent. In this worktree they skip: 28 passed, 3 skipped. A gate run from a worktree therefore never runs the pass's red-to-green tests. Fix: copy the two rulings rows and two decisions rows into a fixture file under `tests/`.
5. `rota/core/runner.py:2879-2885`, low, PLAUSIBLE. The Critic also reads `criteria.load`, and it gets no words. A Critic can then refuse code that follows his words but not the text. The design limits the reach to the builders. Fix: none in this pass. Name the Critic in the frame's walk read.
6. `rota/roles/api.py:9614-9629`, low, PLAUSIBLE. After the refusal, the seat writes its decision without `supersedes`. Night 148's principal then approved d_74_challenge_ver_opt_show_py in r_3340e1e9d9. With the door, his d_565d2845d4 and the approved seat decision both stand, and no row links them. Fix: none in the door. Check in the walk that a reader of decisions does not show both as current.

## (c) Probes

All probes sit in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4754aaec-e35a-4a71-8b57-5004abc1aae8/scratchpad/f243/`. The night-148 database was opened with `?mode=ro` only.

- `r1_p1.py`: lists night 148's rulings, r_4c8fd5d3ad's words and texts, the current criterion text, and the two decisions.
- `plug/r243plug.py`: a pytest plugin that points `NIGHT148` at the checkout's database read-only. With it, HEAD gives 31 passed. Without it, HEAD gives 28 passed and 3 skipped.
- `parent/`: `git archive e11dde47 rota` plus HEAD's tests. With the plugin it gives 3 failed and 28 passed. The failures are the two wake tests (`'term_refs' == 'the principa...'`) and the s189 door test (`DID NOT RAISE`).
- `r1_p2.py`: renders the pushed criteria rows through `_render` at HEAD and at the parent, for one row and for two rows.
- `r1_p3.py`: scans `tests/rota/cases/*.yaml` for Developer or Tester cases with a contest. It found none.
- `r1_p4.py`: a `revise` ruling pushes no words. Three contests render 1,154 characters.

The row as the Developer and the Tester see it at HEAD:

```
[{"id": "ver_opt_show_py", "ticket_id": "tk_1", "text": "If the show_python flag is enabled on version_option, the output format must be \"{command} {python_version}\" where python_version is obtained from sys.version_info.major.minor.micro and appended to the end of the normal version message.", "the principal said, contesting it": ["Line 2 is wrong because the Python version should come from sys.version_info as major.minor.micro, not from sys.version. It should also be added to the end of the normal version message, not replace that message with just the command name and the Python version."], "term_refs": "[]"}]
```

## (d) Usage

The harness did not give this agent its own counts. Estimate: about 60k input tokens, 9k output tokens, 69k total. Read the harness line for the real numbers.
