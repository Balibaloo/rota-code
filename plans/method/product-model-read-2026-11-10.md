# The model as a variable in the records, 2026-11-10

A blind read for the review of rota, frame 364. The scripts and their output are in the scratch folder `C:\Users\roman\AppData\Local\Temp\claude\6d9eb18c9e6274ab\1efd37b1-058e-4b19-8ab1-e1a6c654a389\scratchpad\model\`. Every database was opened with `mode=ro`.

## Result

1. The Developer's desk ran one model, `qwen3.5:9b`, in all 109 databases: 2,232 distinct sessions. Only two nights changed a pin there: night 82 thinking on, night 86 a 12,288 window (observed: `sessions.model`, `pins_json`).
2. So no record separates the Developer's model from the code of rota, the request and the repository. No clean pair exists at that desk (observed: section 3).
3. Four model sets ran. Only the Critic (`gemma3:12b`, nights 82 to 84), the Tester and the Critic (`gemma4:12b-it-qat`, nights 167 and 168) and the Liaison (`gemma4:12b-it-qat`, every dry run) changed (observed).
4. The closest pair is nights 168 and 170: the same final item texts, two desks changed, 232 commits of rota apart. Night 168 merged 0 of 3, night 170 merged 2 of 3 (observed).
5. On the same three requests with one model set, nights 164 to 175 merged from 0 to 3. That spread is as large as the pair's difference (observed: section 3, reasoned).
6. The Developer's model stayed the same on nights 167 and 168, and its commit share fell from 27% to 8%. A stop at the Developer's desk is not a measure of the Developer's model alone (observed: section 4, reasoned).
7. No benchmark is a whole request. Most Developer register runs use `qwen3:8b`, a model that no night ran at that desk (observed: section 5).

## 1. The runs, the commits, the requests and the models

The groups are by the set of models at the desks. VK, LI and AR are the Vision Keeper, the Liaison and the Architect. TE, TS, DV and CR are the Terminologist, the Tester, the Developer and the Critic.

| group | databases | dates | rota commit | repository | models |
|---|---|---|---|---|---|
| A | nights 82, 83, 84 | 2026-09-15 to 09-17 | no record found | clickI | VK, LI, AR `qwen3:8b`. TE, TS, DV `qwen3.5:9b`. CR `gemma3:12b`. DV thinking on in night 82 |
| B | nights 85 to 166 and 169 to 175, 93 files | 2026-09-18 to 10-28 | `f320568` (night 87) to `21d145df` (night 175) | clickI | VK, LI, AR `qwen3:8b`. TE, TS, DV, CR `qwen3.5:9b`. Night 86 at `num_ctx` 12,288 |
| C | nights 167, 168 | 2026-10-26 | `40b16f78`, `e03b1098` | clickI | as B, but TS and CR `gemma4:12b-it-qat`, think off |
| D | dry runs 1 to 8 with 6b and 6c, blind run 1 | 2026-10-31 to 11-10 | see below | clickI, tipsI, icalendarI, tips | VK, AR `qwen3:8b`. LI `gemma4:12b-it-qat`. TE, TS, DV, CR `qwen3.5:9b` |

(observed: `sessions.model` by role, live sessions only, `config.profile`; the commit from the `launched ... at <sha>` line of `.rota/night<N>.log` and `night<N>_launch.log`).

- Groups B and D both name the profile `local`. The profile's Liaison changed from `qwen3:8b` to `gemma4:12b-it-qat` between them (observed: `config.profile`). The name alone does not give the models.
- Requests in group B, nights 86 to 162: "Add an echo_json(obj) helper next to echo...", "Let confirm() take a default_on_eof flag...", "Give version_option a show_python flag..." The wording varies by night (observed: `items` with `is_description=0`).
- Requests in groups B and C, nights 163 to 175: "In get_app_dir on Windows, when APPDATA or LOCALAPPDATA is not set...", "Make clear() return True when it cleared the screen...", the `format_filename` docstring example (observed).
- Group A: night 82 holds one request, "version_option has a show_python flag...". Nights 83 and 84 hold no batch (observed).
- Group D: dry run 1 `click.pause()` returns True (clickI). Dry run 2 the tip percentage ValueError (tipsI, rota `a84a1cf4`). Dry run 3 `canonsort_keys()` and a duplicate key (icalendarI, `44088319`). Dry runs 4 to 8 fold a long line at a space (icalendarI). Blind run 1 on tips holds no batch (observed: `items`; commits from the dry pages in `plans/` and the turn logs: dry 4 starts at `97939168`, dry 5 `79b1cdb0`, dry 6 `cd03aa46`, dry 6b and 6c `3b209833`, dry 7 `dbd8d920`, dry 8 `33c1e697`, blind 1 `787d7112`). No commit record for dry run 1 was found.
- Five files are copies of another night: `night87_partial`, `night91_partial`, `night91_walk1`, `night109_cut`, `night129_partial`. They are out of every count below. Seam nights 103 and 104 hold night 101's 24 Developer sessions, and nights 110 to 112 hold night 109's 35 (observed: shared session ids, turn and call counts).

## 2. Outcomes per group

The rule for a stop, per batch that did not merge: take the last Developer session of the batch. "No commit" means that session wrote no `batches` receipt and got no `"committed": true`. "Red" means it committed and the batch's `latest_runs` hold a fail or an error. "No Developer" means no Developer session names the batch. The session is matched to the batch by `wake_refs`, else by the first batch id in its first prompt.

| group | runs | batches | merged | not merged | DV stop: no commit | DV stop: red | no Developer | after the Developer | runs with a merge | merged share per run, median |
|---|---|---|---|---|---|---|---|---|---|---|
| A | 3 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 of 1 | 0 |
| B | 88 | 277 | 73 | 204 | 110 | 13 | 77 | 4 | 46 of 85 | 0.25 |
| B, seams out | 83 | 266 | 71 | 195 | 106 | 10 | 75 | 4 | 44 of 80 | 0.25 |
| C | 2 | 9 | 0 | 9 | 4 | 0 | 5 | 0 | 0 of 2 | 0 |
| D | 11 | 9 | 3 | 6 | 3 | 3 | 0 | 0 | 3 of 8 | 0 |

(observed: `batches.status`, `receipts`, `latest_runs`, the parsed results). Many "no Developer" batches are abandoned batches that a re-slice replaced (observed: status `abandoned` in nights 133, 137, 143 to 146). By distinct item, group B merged 73 of 233 items (observed).

The spread per run, written as merged / batches / Developer stops (observed):

- D: dry1 1/1/0, dry2 1/2/1, dry3 1/1/0, dry4 0/1/1, dry5 0/1/1, dry6 0/0/0, dry6b 0/0/0, dry6c 0/1/1, dry7 0/1/1, dry8 0/1/1, blind1 0/0/0.
- A: n82 0/1/1, n83 0/0/0, n84 0/0/0. C: n167 0/6/3, n168 0/3/1.
- B, nights 85 to 120: n85 0/0/0, n86 0/2/1, n87 0/1/1, n88 0/3/1, n89 0/3/1, n90 0/3/1, n91 0/1/1, n92 1/3/1, n93 0/4/1, n94 0/3/2, n95 0/2/1, n96 1/4/3, n97 1/4/2, n98 1/2/1, n99 0/3/1, n100 1/3/1, n101 0/1/0, n102 2/3/1, n103 1/1/0, n104 1/1/0, n105 0/3/1, n106 0/3/2, n107 0/3/1, n108 0/3/3, n109 0/3/2, n110 0/3/2, n111 0/3/2, n112 0/3/3, n113 0/3/1, n114 1/3/2, n115 0/3/1, n116 1/3/1, n117 0/3/2, n118 1/3/1, n119 1/3/2, n120 2/3/1.
- B, nights 121 to 175: n121 0/3/3, n122 0/3/1, n123 0/4/1, n124 0/4/1, n125 0/3/1, n126 1/3/1, n127 1/3/2, n128 2/3/1, n130 1/3/2, n131 2/4/2, n132 2/4/2, n133 1/8/1, n135 0/0/0, n136 2/4/0, n137 1/15/1, n138 1/3/2, n139 2/3/1, n140 1/2/1, n141 1/2/1, n142 0/4/4, n143 1/6/3, n144 0/5/3, n145 0/4/4, n146 0/8/4, n147 3/4/1, n148 3/3/0, n149 1/2/1, n150 0/2/1, n151 2/4/2, n152 3/3/0, n153 2/3/1, n154 2/4/2, n155 0/5/2, n156 1/3/2, n157 0/2/2, n158 2/3/1, n159 1/4/2, n160 0/3/2, n161 2/5/2, n162 2/3/1, n163 0/2/2, n164 0/2/2, n164a 0/0/0, n165 0/3/3, n166 2/3/1, n169 0/1/1, n170 2/3/1, n171 1/2/1, n172 2/3/1, n173 3/3/0, n174 3/3/0, n175 2/3/0.

## 3. The pairs closest to a clean compare

**No clean pair exists at the Developer's desk.** No run changed the Developer's model (observed: section 1). The two pin changes do not make a pair:

- Night 82, thinking on, has one request and a `gemma3:12b` Critic. Night 86, the 12,288 window, has two other requests. No commit record exists for nights 82 to 86 (observed).

The pairs closest to a clean compare at any desk:

| pair | same | differs |
|---|---|---|
| nights 168 and 170 | repository, the three final item texts, the Developer's model | TS and CR model. Rota `e03b1098` to `26a44700`: 232 commits, 27 files under `rota/`, 2,760 lines added. One day apart. The agent principal answers in each night |
| nights 166 and 167 | repository, the three item ids, the Developer's model | TS and CR model. Rota `741d2d06` to `40b16f78`: 117 commits, 8 files under `rota/`, `rota/roles/api.py` and `rota/roles/prompts/tester/challenge.md` among them. The get_app_dir item at the end of night 167 has an added sentence, "Only test the app folder tests and the utils file." The format_filename item has other words |
| dry run 1 and any group B night | repository clickI, DV, TE, TS, CR models | the Liaison model, the request (`click.pause`), three days and many commits |

(observed: `items`, `git rev-list --count`, `git diff --shortstat -- rota/`).

- Results: night 166 merged 2 of 3. Night 167 merged 0 of 6 batches on 3 items. Night 168 merged 0 of 3. Night 170 merged 2 of 3 (observed).
- The night 167 read names its own confounders: rota's doors stopped walks 2 and 3, and the Gemma Critic reached no review (observed: `plans/night167-read.md`, section 4). The night 168 read says the same of walks 2 and 3, W5 (observed: `plans/night168-read.md`, section 4).
- Repeats with one model set: nights 110 and 111 started from night 109's database at the same commit `eb7cd0d`. Both merged 0 of 3 with 2 Developer stops (observed). Nights 103 and 104 started from night 101 and both merged 1 of 1 (observed).
- The spread with one model set on the get_app_dir trio: n164 0/2, n165 0/3, n166 2/3, n169 0/1, n170 2/3, n171 1/2, n172 2/3, n173 3/3, n174 3/3, n175 2/3 (observed). The commit changed each night. The two Gemma nights fall inside that spread (reasoned).

## 4. The Developer's desk

One model, `qwen3.5:9b`, so the table is by pin and by group. A refusal is an `ERROR <fn>` line in the results that the next prompt shows. `ERROR TOOL:` lines are refusals of the call parser, not of a door.

| set | sessions | commit | refused results | top refusals |
|---|---|---|---|---|
| all, duplicates out | 2,232 | 602 (27.0%) | 7,151 of 27,966 (25.6%) | see below |
| think off, 16,384 | 2,199 | 597 (27.1%) | 7,094 of 27,631 (25.7%) | as all |
| think on, night 82 | 17 | 4 (23.5%) | 28 of 102 (27.5%) | `code.write` "is not valid Python" 15, the parser's "unterminated argument list" 6, a repeated challenge 3 |
| 12,288 window, night 86 | 16 | 1 (6.2%) | 29 of 233 (12.4%) | `code.write` "this rewrite of PATH drops ..." 13, a repeated challenge 13 |
| group A | 17 | 23.5% | 27.5% | as night 82 |
| group B | 2,047 | 27.7% | 25.1% | as all |
| group C, Gemma TS and CR | 49 | 8.2% | 43.5% | `code.commit` "a code.write in an earlier reply returned a note" 27, `msg.challenge_tester` "quotes= holds ... not in the live text" about 70 |
| group D, Gemma LI | 119 | 21.8% | 27.9% | a repeated challenge 40, a repeated question to the Vision Keeper 32 |

(observed: `receipts`, `turns.user`, `tool_calls`). Per run the commit share goes from 0% (nights 88, 89, 99, 150, 169) to 100% (night 141, 4 sessions). The refused share goes from 0% (dry run 6c) to 59% (dry run 5) (observed).

The three most common refusals over all sessions (observed):

1. A challenge sent again: "you have already sent challenge to tester; saying it again with different words" 854, and "you sent challenge to tester on exactly these refs already" 371.
2. The repeat guard: "asked three times this session and the answer has not changed; not answered again", on `code.source` 534 and `code.commit` 221.
3. The parser: "unterminated argument list: a quote inside a quoted argument", 215.

The draw: `random.Random(364).sample(pool, 5)`, the pool sorted by database file name and session id, duplicates out. The model has one value, so I drew 5 from all sessions and 5 from the thinking-on sessions of night 82 (observed: `draw.json`, `draw.txt`).

| session | wake | what the last model turn did |
|---|---|---|
| n100 s209 | tests_failing, attempt 4 | Read two criteria as a contradiction, changed the default of `default_on_eof` to True, and sent the same whole-function write again. The door refused the span |
| n119 s158 | tests_failing, attempt 6 | Sent the same write with `from .core import command` a third time. The door refused it as not valid Python. The account notes a reply cut at the output budget |
| n94 s269 | message, answer | Said that `version_option` already meets the three criteria. Its commit returned "nothing changed". Ended in prose |
| n101 s161 | message, answer | Rewrote `echo_json` in `src/click/utils.py`, committed, and ended "The batch is complete." Earlier writes were refused: a root module, a second definition, a commit that undid itself |
| n106 s215 | message, answer | The door said the test calls `confirm()` unshielded and named `msg.challenge_tester`. The model wrote `confirm` again. No challenge was sent |
| n82 s118, think on | batch_start | Its commit landed earlier. The last turn said "The batch is complete." The account lists a write that is not valid Python and a refused test-file write |
| n82 s124, think on | tests_failing, attempt 4 | Sent `msg.challenge_tester` on the `package_name` RuntimeError, then explained the test's design in prose |
| n82 s133, think on | tests_failing, attempt 7 | Three refused writes of a fragment that does not parse, an empty reply, then a reply cut at the budget |
| n82 s154, think on | message, answer | Said that the code already meets the three criteria. No commit |
| n82 s147, think on | exhausted, attempt 12 of 10 | Asked the Vision Keeper whether to build the feature, because the loaded tests do not test it |

Of the 10 last turns, 4 repeat a refused write, 4 end in prose that says the work is done or met, and 2 send a message (observed). The thinking-on sessions show the same three shapes. Five sessions per set cannot show a difference (reasoned).

## 5. The benchmarks and the register

| record | date | what it measures | fixtures | Developer result |
|---|---|---|---|---|
| `probes/bench/RESULTS.md`, the bakeoff | 2026-08-25, one row 2026-09-23 | one-shot completions on prose batteries: frame, define, read, challenge, recover | 21 fixtures, half with the composed brief, half hand-written probes | none. The encode battery was retired: one-shot completions "cannot rank behaviour that only exists through the tool channel" |
| `rota/llm/benchmarks.json` | 2026-09-12 | the register's pass share per model per role, and the walks' merge share | the register cases of that day | DV: `llama3.1:8b` 0.75 (12 cases), `qwen3:4b` 0.70, `qwen3.5:9b` 0.667 (12), `qwen3:8b` 0.60, `gemma3:12b` 0.5, `qwen3.5:4b` 0.4. Walk merge share 0.15 for every model |
| the five acts, `rota/COMPLETION.md` | 2026-09-14 | five cases, five runs, one load per model | small fixtures: "The fixtures are small; click's prompts are not" | act 3, a traceback to a change: `qwen3.5:9b` 0/5, then 5/5 with the door of finding 66. `qwen2.5:14b` 0/5. `gemma-4-26B-A4B` 5/5 |
| the register, `tests/rota/cassettes.db` | runs to 2026-11-10 | one session per L1 case, short chains in L2 and L3 | seeded small repositories with a night's ids and shapes | DV L1 runs: `qwen3:8b` 53,896 on 17 cases, 0.75. `llama3.1:8b` 10,856, 0.81. `qwen3.5:9b` 9,076 on 16 cases, 0.76. `gemma3:12b` 50, 0.50 |
| frame 323's trial, `plans/frame323-gemma-interview.md` | 2026-10-25 | `gemma4:12b-it-qat` on the recorded cases | a copy of the register | 9 Developer cases at 0 of 5. Critic 0.79 against 0.40, Tester 0.73 against 0.50 (commit `40b16f78`) |
| night-turn replays, `plans/operating-facts.md` | 2026-09-23 | one recorded click turn, several models | night 86's write turn, click's real prompt | `qwen2.5:14b` invents a signature, 471 s. `qwen3:30b-a3b` answers in prose, 510 s. Every local model writes `confirm()` from memory |

(observed: each file named; the register counts from `case_runs`, read on 2026-11-10).

- On the Developer cases that `qwen3.5:9b` shares with another model, the last 5 runs per case: `qwen3:8b` 42 of 55 against 39 of 55, `llama3.1:8b` 35 of 55 against 39, `gemma3:12b` 25 of 50 against 35, `qwen3.5:4b` 15 of 45 against 30 (observed: `register.py`).
- 6 of 25 Developer cases pin `model: qwen3.5:9b`. The rest run the shell's `ROTA_MODEL`, and the operating facts set it to `qwen3:8b` (observed: `tests/rota/cases/*.yaml`, `plans/operating-facts.md`, "Models and Ollama"). So most of the register's Developer measure is on a model that the nights do not run at that desk.
- The live register holds no Developer run of `gemma4:12b-it-qat` (observed). Frame 323's count is from a copy that I did not open.
- No benchmark is a whole request. Each one is a session, a chain of a few sessions, one turn or one completion (observed). The nights, the dry runs and `tests/rota/walks.jsonl` are the only whole-request records. The walks record a profile, not the model of each desk (observed).
- Click's real prompts: the night-turn replays, and register cases built from a night's turn file, such as `L1-DV-end-the-session-when-the-door-says-end` with `night126_s172_t2.txt` (observed). The five acts, the bakeoff and most register cases rest on small fixtures (observed).
- Outside the population, `rota/COMPLETION.md` names night 60 with a 14B Developer and night 62 with `gemma-4` at the Developer's desk. No database for them is in `.rota/` (observed). The older databases `tipsAR`, `tipsAS`, `clickI_n42` and `clickI_n70_merged` also ran `qwen3.5:9b` at the Developer's desk, `tipsAS` through the OpenAI shape (observed).

## 6. The hardware, as the records state it

- The main card is an RTX 3080 with 10 GB. The practical budget is about 8 GB. The second card is a GTX TITAN X, Maxwell, 12 GB (observed: `plans/operating-facts.md`, lines 60 to 61, 99).
- Fit: `qwen3:8b` 5.2 GB fits. `qwen3.5:9b` 6.6 GB fits at 12,288. Night 170 measured it at 5.9 GB, all in VRAM, at 16,384 (observed: line 103, `config.spill_seen`). An early line says it spills about 27% (observed: line 95). The two lines disagree.
- `qwen2.5:14b` 9.0 GB spills a little, 40 to 90 s a turn. The 27B models overflow by about 8 GB. `gemma3:12b` ran at 76% GPU, 62 s a turn, in the bakeoff (observed: lines 103 to 104, `RESULTS.md`).
- `gemma4:12b-it-qat` hangs on the 3080 past 1,536 prompt tokens. A router sends it to the Titan (observed: line 79).
- Speed: `llama3.1:8b` about 123 tok/s on the 3080 and 27 on the Titan. `qwen3.5:9b` 9 tok/s on the Titan in one line and 17.0 in another (observed: lines 61, 79, 135). The MoE `qwen3:30b-a3b` decodes at 8.3 tok/s and prefills at 92 tok/s, against 4,165 for a dense 8B (observed: `RESULTS.md`).
- A swap costs one load. The median load is 12.6 s for `gemma4:12b-it-qat`, 4.3 s for `qwen3.5:9b` and 2.8 s for `qwen3:8b`. The slowest loads take 56 to 115 s (observed: line 148).
- Model changes between consecutive live sessions: night 166, 27 in 114 sessions. Night 167, 84 in 337. Dry run 7, 58 in 223 (observed: `speed.py`). At the medians, night 167 spent some minutes on loads. The exact cost is not recorded (reasoned).
- The median Developer turn in `turns.ms` was 10.3 s with thinking on (night 82), and 1.4 to 4.1 s in the other runs I timed (observed).
- Temperature 0 repeats inside one load and not across loads. A recording on the Titan differs from one on the 3080 (observed: `RESULTS.md`, line 76).

## What the records cannot say about the model

- The effect of the Developer's model. It never changed in a whole run.
- The effect of thinking on at the Developer's desk. Night 82 has 17 sessions, one request, another Critic and no commit record.
- The effect of the Gemma Tester and Critic. Two nights, each at another commit of rota, and rota's doors stopped the walks that reached those desks.
- The effect of the Gemma Liaison. It ran only in dry runs, on other repositories and requests than the nights.
- The spread of one model set on one request at one commit. Only the seam pairs repeat a start, and they share the database up to the seam.
- Whether a register score at the Developer's desk predicts a night. The register measures mostly `qwen3:8b`, and no night ran it there.

## Limits, and what I could not see

- The stop rule is mechanical. A message-woken Developer session can name no batch, and then it falls to "no Developer" or to an earlier session.
- The refused share counts `ERROR` lines in the next prompt. It covers 27,966 of 42,789 tool-call rows. The results of a session's last model turn appear in no prompt.
- The commit share counts a session that committed at least once. It does not say the commit was right.
- I matched requests by item id and final item text. The item text can change during a run.
- `turns.ms` includes short replies and repeated prompts. The medians are not decode speeds.
- I did not read `plans/stack.md`, the product pages, the meta pages, or the register copy of frame 323. I read the night 167 and 168 pages in sections 4 and 5 only.
- I ran no model, night, gate or benchmark, and changed no file but this page.
