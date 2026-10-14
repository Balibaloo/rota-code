# Frame 237, pass 1: the diff review of the survey brief and the runner's account

Rota workflow, the Terminologist's survey after a merge. Written 2026-10-14 20:33 by the review agent of the meta workflow. Worktree `C:/Users/roman/rota_rv237` at a2344b87, over its parent bb8655eb. Read-only.

Verdict: revise. The account line names a call that the parser ran, and the shipped attest example was never replayed. Findings: 2 high, 5 low.

## (a) The verdict on each point

1. The account on the night: no miss on the night's shapes. The counts behind "8 of 8" are wrong (finding 3).
2. The hook's place: the line reaches `session_note` and not the seat's next turn. The fixture rule holds (finding 4, finding 5).
3. The head pattern: the pattern does not see s323's one-line shape, and that is correct. The parser ran that shape as a call.
4. The brief: STE holds in the new sentences. No contradiction. The placeholder reads as a placeholder, but the shipped text was never replayed (finding 2).
5. The budget: the brief fits. No rule bounds a brief's size. The owning register cases are stale (finding 7).
6. The tests: all 3 are red on the parent. The bullet call, the duplicate head and the empty list have no test (finding 1).
7. STE and CR bytes: 0 CR bytes in the three files. The account text and comments are acceptable.

## Point 1. The account on the night's completions

Probe `p1_night.py` ran `listed_not_called` on every turn's completion of the nine sessions (observed: 2026-10-14).

| Session | Turns with names | Names returned |
|---|---|---|
| s187, s193 | 1 to 6 | `glossary.amend`, `code.source` on each turn |
| s188, s194 | 1 to 6 | both names on turns 1, 2, 4, 5, 6; `code.source` alone on turn 3 |
| s189, s195 | none | `[]` on every turn |
| s323 | none | `[]` on every turn |
| s68 | 1, 2 | `glossary.amend`, `code.source` |
| s69 | none | `[]` on every turn |

No miss and no false name on the night. The empty result on s189 and s195 is correct. Those two sessions never wrote a `glossary.amend` line in any turn. They wrote `TOOL: code.source(...)` calls only, and the parser ran them. So "8 of 8 survey sessions wrote the prose list" is false. The prose list under a head is 5 of 8: s187, s188, s193, s194 and s68.

## Point 2. The hook's place

The line goes to `outcome.errors` only. The seat's next turn reads the `feedback` list (`runner.py:3824` to `4402`), and `outcome.errors` never enters it. So the seat does not see the line. On night 147, s187 turn 2 received the generic "this session has written nothing" nudge, and the seat repeated the list for 5 more turns.

The line reaches `session_note` on a committed session. The test asserts that, and s187 committed on the night. On an uncommitted session the line is lost. `session_fail` (`db.py:1180`) writes only the exception, and `loop.py:60` prints only `errors[-1:]`. The pass report's deviation 2 says the line reaches the failure line of `loop.py`. That is false in the usual order (finding 5).

Probe `p3_s323.py` applied the fixture's own expression, `err.split(":", 1)[0].strip()`, to the line for three names. Each head is `written as a list under its name, not as calls`, with no dot. The rule holds. `scenes.py:330` raises on any error line outside its allow list. No scripted scene text holds the head shape (observed: a grep over the worktree's `.py`, `.json`, `.yaml` and `.txt` files, only the new test matched).

## Point 3. The head pattern

`_LISTED_HEAD` needs the line to end at the colon. The s323 line "`glossary.amend`: `term="parameter"`, ..." has text after the colon, so the pattern does not match it. That is correct. Probe `p3_s323.py` ran `extract_lenient` on the two s323 turns. Turn 1 gave two `glossary.amend` calls with `sense_body` and `sense_short` and no `term`, and the runner refused them for the missing `term`. Turn 2 gave two calls with `term`, and `tool_calls` seq 10 and 11 hold them with `term='parameter'` and `term='context'`. So the parser runs that shape. A line that says "None ran" would be false there.

## Point 4. The brief

The new sentences are STE: one topic each, active, short. The edited attest sentence keeps the old dash, "— not a symbol, not a line number:". That sentence is now new text, so STE applies to it. This is low and not a finding.

The count sentence does not contradict the paragraph below it. "Two to five words is the common count when an area has new words" stays under eight. Its condition leaves `none_found` the answer for an area with no new words.

The placeholder `<a path [code.area] printed>` most likely reads as a placeholder (reasoned). In the interview the seat said the only example, `artefact.verb`, was "not present in my working set", so the 9b does not copy a value it sees as generic. In the pass replay with `src/click/core.py` as the example, the seat cited `__init__.py`, `globals.py` and `_utils.py`, not the example path. But the replayed brief is not the shipped brief (finding 2). `system-P1.txt` line 33 holds `citations=["src/click/core.py"]`. The commit message's "7 amend calls a run in 3 of 3 replays" belongs to that text.

## Point 5. The budget

`plans/operating-facts.md`, "Rulings on briefs and doors", holds no number for the size of a brief. Its rule is line 291: measure a brief change with the register case that owns the behaviour, plus a cold walk. The shipped brief is 1555 characters, not 1544. The placeholder is 11 characters longer than the replayed path. The window is in tokens, not characters. The s187 turn 1 prompt, system and user together, is 4884 tokens (observed: the interview, 2026-10-14). The brief adds about 70 to 80 tokens (reasoned: 283 characters at the turn's own ratio). The prompt then is about 4960 tokens, so it fits the 16384 window and the overflow plan of 8192. The largest later turn, s188 turn 6, is about 7700 tokens by the same ratio, and it still fits. The two owning register cases are stale and unmeasured (finding 7).

## Point 6. The tests

All three new tests are red on the parent (observed: the `parent/` copy, `3 failed in 11.52s`). Two fail on the import, and the account test fails on `sum(...) == 1` with 0. The whole file is green on the worktree, `82 passed in 94.73s`.

Probe `p6_branches.py` ran the untested branches through `listed_not_called` and `extract_lenient`:

| Shape under the head | `listed_not_called` | Parser ran |
|---|---|---|
| a bare `glossary.amend(...)` line | `[]` | `glossary.amend` |
| `- TOOL: glossary.amend(...)` | `['glossary.amend']` | `glossary.amend` |
| `1. TOOL: glossary.amend(...)` | `['glossary.amend']` | `glossary.amend` |
| `- glossary.amend(...)` | `['glossary.amend']` | `glossary.amend` |
| the same head twice | `['glossary.amend']` | nothing |
| an empty list, then the next head | both names | nothing |
| an empty list at the end | `[]` | nothing |
| `foo.bar`, not a seat call | `['foo.bar']` | nothing |

The bare call works. Two heads of one name give one name. A head over an empty list at the end gives nothing. A head over an empty list followed by another head is named, which is acceptable. The bullet and numbered rows are false names (finding 1).

## Point 7. STE and CR bytes

The three files hold 0 CR bytes, and `git ls-files --eol` shows `i/lf w/lf` for each (observed). The first clause of the account line, "written as a list under its name, not as calls:", has no subject. It is a log line, and the fixture rule forces the head shape, so it is acceptable. The comment at `runner.py:3617`, "no reason that no word landed", is hard to read. It is not a finding.

## (b) Findings

1. `rota/core/runner.py:677` to `689`. High. CONFIRMED: probe `p6_branches.py` shows the account names `glossary.amend` and says "None ran" when the call line under the head starts with `- ` or `1. `. The parser ran each of those calls. `called()` reads a line-start regex, and the parser accepts more shapes. Fix: decide "called" from the names in `calls` that `extract_lenient` returned, and add a test for a bullet `TOOL:` line under a head.
2. `rota/roles/prompts/terminologist/survey.md:28` and the commit message. High. CONFIRMED: `f237/system-P1.txt` line 33 cites `src/click/core.py`, and the shipped line cites `<a path [code.area] printed>`. No replay ran the shipped text, so "7 amend calls a run in 3 of 3 replays" is a claim about another brief. Fix: replay the shipped brief on s187 turn 1 and one non-click survey turn, and record the counts.
3. `rota/core/runner.py:666`, the docstring of `test_a_call_name_over_a_list_is_named_as_no_call`, and the commit message. Low. CONFIRMED: probe `p1_night.py` shows 5 of 8 sessions wrote a head over a list. s189 and s195 wrote no amend, and s323 wrote the one-line shape that the parser ran. Fix: write "5 of 8" in both docstrings, and correct `plans/night147-read.md` section 7 with an observed mark.
4. `rota/core/runner.py:3620` to `3625`. Low. CONFIRMED: the line goes to `outcome.errors` only, and the next turn of the seat reads `feedback`. s187 received the generic nudge and repeated the list on 5 later turns. Fix: the holding session decides whether the seat half is in scope and records it; if yes, add the sentence to `feedback`.
5. `scratchpad/f237/pass1-report.md:104`. Low. CONFIRMED by a read: `loop.py:60` prints only `errors[-1:]`, and `session_fail` writes only the exception. The line reaches the record of a committed session only. Fix: correct the claim in the pass record, with no code change.
6. `rota/core/runner.py:684` to `688`. Low. CONFIRMED: probe `p6_branches.py` names `foo.bar`, a name outside the seat's calls, and the line tells the reader "`TOOL: foo.bar(...)`". Fix: keep only the names in `allowed`, in the same edit as finding 1.
7. The register cases `L1-TE-survey-an-area-for-its-terms` and `L1-TE-resurvey-an-area-that-moved`. Low. CONFIRMED from the gate lines in the pass report: both cases are stale and not re-recorded. `plans/operating-facts.md` line 291 rules that the owning case measures a brief change. Fix: re-record both cases on the main card before the frame closes.

Outside the points: finding 6, and the `scenes.py:330` reader in point 2.

## (c) Probes

All are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4a757f92-bd97-4750-9830-bd149134e576/scratchpad/rv237/`.

- `p1_night.py`: `listed_not_called` on every turn of the nine sessions in `clickI_night147.db`, read-only, and the `tool_calls` rows of each.
- An inline `python -c` read of the s189 and s323 turns 1 and 2, of the head lines of every turn, and of the s187 turn 2 user text and its `SESSION ENDED` turn.
- `p3_s323.py`: `extract_lenient` on the two s323 turns, the `tool_calls` rows from seq 9, and the fixture's head expression on the account line for three names.
- `p6_branches.py`: eight shapes under a head, through `listed_not_called` and `extract_lenient`.
- `parent/`: `git archive bb8655eb` of `rota`, `tests` and the pytest files, with the new test file from HEAD, then pytest `-k` on the three tests: 3 failed.
- The worktree: pytest on `tests/rota/test_onboarding_phases.py`, 82 passed. A CR count and `git ls-files --eol` on the three files. A render of the brief through `prompts.piece`, 1554 characters.

## (d) Usage

About 78k input tokens, about 10k output tokens, about 88k in all, from the context counter. The brief's cap was 40k, and this review spent about twice the cap. No GPU and no model ran.
