# Mass 6, the instruments: a blind read, 2026-11-10

Meta workflow. Read at e956c737 by one agent of session 7fd2421e. The read changes no other file.

## 1. The list, and how I found it

I read `plans/method/reference.md` whole, three sections of `plans/operating-facts.md`, `rota/COMPLETION.md` lines 1 to 152, and the docstring of each file in `rota/tools/`.
I listed `probes/`, `.rota/`, `.handover/` and `.claude/hooks/`. Then I indexed every shell, agent and read call of the session transcripts.
An instrument is on the list when a rule, a tool text or a call shows a session that looks at it to know something.

Group 1, the state of the build (11):
G1.1 the state print, `rota/tools/state.py`. G1.2 the status lines of `plans/stack.md`, written by `rota/tools/status.py` or by a script.
G1.3 the order heading at the top of the stack. G1.4 the peers table, `handover.py peers`. G1.5 the hand-off commands and `.handover/log.jsonl`.
G1.6 the momentum note, `plans/method/handoff-<sid>.md`. G1.7 the context count hook, `.claude/hooks/context_count.py`.
G1.8 the rulings search, `rota/tools/rulings.py`. G1.9 the map, `rota/tools/map.py`. G1.10 `git log` and `git status`.
G1.11 the capability list of `rota/COMPLETION.md` and the capability on a frame's Sprint line.

Group 2, whether rota works (19):
G2.1 the gate, `rota/tools/gate.py`, and its baseline `.rota-gate.json`. G2.2 the touched tests, by `pytest`. G2.3 the case register, `case_runs`, read by SQL.
G2.4 `rota/tools/casestatus.py`. G2.5 the diff review by the reviewer agent. G2.6 the night, `probes/gauntlet_click.sh` and `probes/walk.py`, with its log.
G2.7 the night read by an agent, `plans/night<N>-read.md`. G2.8 `rota/tools/nightreport.py`. G2.9 `rota/tools/nightcount.py`.
G2.10 the walk register, `tests/rota/walks.jsonl`. G2.11 the dry run with the session in the seat, and its read page.
G2.12 the interview, `probes/frame37/interview_turn.py`. G2.13 the replay and seam probes, `probes/frame37/replay_*.py`, `probes/seam_start.py`, `probes/frame164/`.
G2.14 the door count of rule C35. G2.15 the answer keys, `probes/cnt/score.py`, `probes/consult.py`, `rota/ANSWER_KEY*.md`.
G2.16 the blind test, `plans/understanding-test-blind-2026-11-03.md`. G2.17 the seat exchange, `probes/seat.py`.
G2.18 the row checkers, `rota/tools/invariants.py`, `audit.py`, `faults.py`. G2.19 the older probes: `probes/bench/`, `triage.py`, `probe_tools.py`, `probes/frame122/`, the cockpit with `tests/rota/lens_check.js`, `probes/wake_dump.py`, `probes/progress.py`.

How I counted. T is the transcripts: 100 sessions and 1,181 agents, 62,318 shell calls, 2026-10-10 to 2026-11-10 in UTC. A use in T is a call that runs the tool.
R is the records: 5,048 dated status lines of the stack and its archives, 2026-09-14 to 2026-11-10. A mention in R is not a use.
A is an artefact: a file of `.rota/`, `.handover/log.jsonl`, `tests/rota/walks.jsonl`, `.rota-gate.json`, or a first commit date.
Weeks are ISO weeks. W41 holds 2 days of T, W43 holds 4, W46 holds 2. The per-week numbers below run W41 to W46 unless a row says other.

## 2. One row per instrument

| Instrument | Meant to show (source) | Unit of one result | First and last use | Uses per week | Known faults (who, how) |
|---|---|---|---|---|---|
| G1.1 state print | "the held frames, the count of live things, the open decisions and the leaving session's doubts" (docstring) | one stack file at one moment, by heading tags | 2026-10-18 to 2026-11-10 (T) | 189 runs, 132 by sessions: 0, 17, 48, 59, 36, 29 | five Waits-on lines read as open decisions on a citation, 2026-10-26 (`state.py` line 41) |
| G1.2 status lines | "Where are we" is answered from this file (stack head) | one frame at one clock time | 2026-09-14 to 2026-11-10 (R) | 5,048 lines, W38 to W46: 201, 354, 536, 680, 1135, 731, 947, 427, 37. Tool calls: 0, 90, 364, 761, 201, 18 | a time typed in the body, 6 strikes by 2026-10-28 (memory index) |
| G1.3 order heading | the next frames in one order, written at a run's read (C46) | one run's read | 2026-10-16 07:01 to 2026-10-31 03:04 in the part I read | 27 Sprint headings in 15 days, 23 "recommended on night N's read". None from 2026-10-31 03:04 to 2026-11-09 | not recorded |
| G1.4 peers table | "who waits in reserve" (docstring) | one checkout's mailbox, one row per session | 2026-09-20 to 2026-11-10 | 376 runs: 18, 125, 79, 85, 52, 17 | holders printed STALE until 2026-09-20. `handed` column stale, session 0549dc76. Orphan watcher beats, 2026-09-23. All in operating facts |
| G1.5 hand and take | which session holds the frame, by exit code | one hand-off | 2026-09-20 02:51 to 2026-11-10 (A) | 130 claims in the log, about 18 a week. T: 125 `hand`, 119 `take` | two sessions held frame 152, 2026-10-07 (the log). A woken taker ran no take, 2026-09-25. `holding --frame none` reads as a held frame |
| G1.6 momentum note | the sender's judgement and doubts (C10) | one hand-off | ruled 2026-10-09. 62 note files in `plans/method/` and 32 in `plans/` today | Read-tool reads 9 in T. Shell reads not counted | not recorded |
| G1.7 context hook | "the tokens in the context window" (docstring) | one session at one prompt | 2026-09-16 on | not counted. It prints on the first prompt and from 200k up | byte factor read 8 percent low, 2026-09-20. Frame 52 measured plus 9, plus 14, minus 1 percent |
| G1.8 rulings search | "which record already answers a question" | one query | 2026-10-18 to 2026-11-06 | 42 runs, 3 by sessions: 0, 13, 13, 7, 9, 0 | frame 293 pass 4, 2026-10-18: 2 of 11 answers found in part, 0 of 11 whole (agent report, T bf5baa63) |
| G1.9 map | "where a thing is, and who touches it" | one name in the code | 2026-09-17 to 2026-11-10 | 2,139 runs, 2,032 by agents: 90, 520, 366, 765, 350, 48 | a map test's number went stale at 376321b0 (operating facts) |
| G1.10 git log, git status | what is committed | one tree | whole period | 5,855 and 2,488 calls in T | not recorded |
| G1.11 capability list | "the outcome the work serves" (COMPLETION line 16) | a capability | ruled 2026-09-12. Shell reads from 2026-10-25 | Read tool 1. Shell 85: 0, 0, 1, 19, 30, 35. R: 9 of 5,048 status lines | "No frame cited the page between 2026-09-17 and 2026-10-31" (CLAUDE.md, Roman's question) |
| G2.1 gate and baseline | "The suite in five lines, with a traceback for a new red only" | one working tree against one stored baseline | 2026-09-17 to 2026-11-10 | 657 runs, 356 by sessions: 35, 223, 80, 250, 66, 3. `--baseline` 8 | worktree gate compares with itself (frame 96, 2026-09-30). Checkout gate reads the implementer's tree (review of 2c602d1b, 2026-10-09). Lock error drops a stale case (review 1h, 2026-10-12). Blind to the cut paths (session e6218d79, 2026-10-05). `--baseline` stores a flaky red (frame 199). L3R cases cannot re-record (frame 354). A dead server reads as a free card (frame 362, 2026-11-04) |
| G2.2 touched tests | a pass's own tests | one test file at one tree | whole period | 6,036 calls, 5,727 by agents: 246, 1184, 1122, 2389, 960, 135 | a `failed` line beside a fresh commit, frame 296, 2026-10-18 |
| G2.3 register by SQL | "Live pass/fail is the `case_runs` table" (operating facts) | one case, one model, one prompt hash | 2026-08 to 2026-11-10 | 901 calls, 784 by agents: 48, 212, 207, 272, 156, 6 | "A sample of five is one live call" (frame 55, 2026-09-22). `prompt_hash` misses pre-run results (frame 106). Replay at 12288, night at 16384 (2026-09-19) |
| G2.4 casestatus | "Where every model-facing case actually stands" | one case under one model | 2026-08-13. T: 2026-10-12 to 2026-11-10 | 149 runs, 28 by sessions: 0, 18, 47, 60, 15, 9 | "The report's threshold cannot bind" (2026-09-22). A count under a wrong model quoted two days as prompt drift (docstring) |
| G2.5 diff review | defects of one pass (C53) | one commit against numbered points | 2026-09-16 to 2026-11-10 | 403 reviewer agents: 19, 131, 80, 124, 38, 11 | twelve judges faulted 29 of 32 replies, adversaries overturned 23 (frame 40, 2026-09-18) |
| G2.6 night | a walk of three requests on click, end to end | one run of up to 3 requests on one repository | before 2026-09-13. Artefacts night 82 to night 175, read 2026-10-29 | 94 nights by artefact. By log time, W38 to W44: 3, 7, 24, 22, 17, 9, 3, and nights 170 to 175 in W44 by their reads. None after | crash prints no `Stuck`, night 126. Void night, night 134. Two false CYCLE lines, night 138. Night 174's label read 173 |
| G2.7 night read | walls and counts of one night | one night | 2026-09-15 to 2026-10-29 | 74 agent launches in T: 2, 28, 24, 20, 0, 0 | two models on one brief differ on 1 of 4 frames, night 119. "A night read costs about 270k to 330k" |
| G2.8 nightreport | "The rows a night's read asks for" | one night's database | 2026-10-01 to 2026-10-28 | 27 report files (A). T: 26 runs: 0, 8, 15, 3, 0, 0 | a zero from an absent table read as a fact (frame 105 review). M0 missed two pages (frame 307, 2026-10-23) |
| G2.9 nightcount | "what the model made up, and what the runner ran anyway" | one night's database | 2026-09-23 to 2026-10-28 | T: 12 runs, 2 by sessions | counted turns that sent no write (frame 77 review). A term printed with no definition, night 106 |
| G2.10 walk register | "every walk writes its result row" (commit 09cb4e24) | one walk of one request: merged, steps, asks | rows 2026-09-09 to 2026-10-25 | 156 rows, W37 90, W38 61, W39 3, W43 2. Shell reads 14 in T | a night from a worktree writes its row in the worktree. Two hand copies, 5014da1f and 893d49ba |
| G2.11 dry run | "a merged change the session can read" (long term plan, step 2) | one request on one repository, a strong model in the seat | dry1 2026-10-31 to dry8 2026-11-08 | 10 runs in 9 days: dry1 to dry8, 6b, 6c | "One row set by hand before turn 16" of dry1 (operating facts, the fourth measure) |
| G2.12 interview | what a seat read and understood (C33) | one turn of one session, one model call | 2026-09-24 to 2026-10-28 | T: 17 runs: 3, 9, 3, 2, 0, 0. R: 161 mentions | the default last turn gets "I do not know" (night 91, 2026-09-24) |
| G2.13 replay, seam | a door's effect on a recorded turn | one turn | 2026-09-23 on | direct runs 0 to 1 in T. They run from scratchpad scripts. R: replay 345, seam 155 mentions | "5 runs are 1 sample". The control matched at 3 of 4 turns (2026-10-05) |
| G2.14 door count | "fires on a of n instances, refuses b of N right calls" (C35) | one door on one night | 2026-10-05 to 2026-10-24 (R) | 38 status lines | "It does not print a door's count" (C35, of nightcount) |
| G2.15 answer keys | what the tool can answer about a project (COMPLETION, 11) | a capability on one repository | 2026-08-21. T: 2026-11-03 and 2026-11-04 | 3 direct runs of `score.py`. Consult ran inside one pass | "two keys written as controls and never run in the loop" (COMPLETION, read 2026-11-04) |
| G2.16 blind test | future work with and without the records | a capability on three repositories | page of 2026-11-03 | no run in the records I read to 2026-11-09 | not recorded |
| G2.17 seat.py | "The measurement the seat's pages lacked" (COMPLETION, 9) | one exchange of pages | commits 2026-09-12 and 2026-09-15 | 0 runs 2026-10-10 to 2026-11-09, 1 on 2026-11-10 | not recorded |
| G2.18 row checkers | laws as propositions over any run database | one run database | 2026-08-27 on | 1 direct run of `invariants`. `audit` 0, `faults` 0. `invariants` also runs in scene tests | not recorded |
| G2.19 older probes | model choice, failure shapes, cockpit truth | one model load, or one page | 2026-08 | 0 runs in T, but `probe_tools --help` once | "A bench score is a fact about a load": 3 of 4, then 1 of 4 (2026-08-26) |

## 3. The drawn uses

`random.seed(20261110)` then `random.sample(population, 6)`, per instrument, over uses before 2026-11-10. S is a session, A an agent.
Codes: P frame pushed, C frame closed, O order written, R rule written, F fix or commit, H hand-off step, L night launched, G agent or read started, K record written or corrected.
N nothing tied, I inside an agent with no session act in view, X not a run, ? result outside the view.

| Instrument (population) | The six uses: date, reader, next act |
|---|---|
| state (167) | 10-24 S at take, "No frame", claims frames H. 10-26 S after a close, "18 of 10", pushes frame 335 P. 10-28 S at take, "No frame", greps the stack N. 11-01 S after a close N. 11-04 S fixes a Waits-on line, print reads "None" K. 11-09 A N |
| status tool (1,416) | 6 S. Each prints "committed <sha>". The next acts follow the event the line records, not the line: N 6 |
| peers (362) | 10-16 S, 10-23 S: free standbys read, note written H. 10-27 S: `hand`, exit 4, message H. 10-31 A audit N. 11-04 S re-arms H. 11-06 S takes H |
| hand (123) | 10-13 `--help` X. 10-15, 10-23, 10-25, 10-27, 11-01 S: CONFIRMED in 5 to 12 s, status line, stop: H 5 |
| map (2,094) | 6 A. Each opens the named file or writes a test next: I 6 |
| rulings (42) | 5 A, I 5. 3 start with `--help`, which prints search hits. All 5 grep the records directly after. 1 X |
| gate (654) | 10-16 S commit F. 10-24 S "3 new reds, the known Tester cases", night 164 launched L. 10-25 S fix pass 1d F. 10-27 S a read of two reds G. 10-28 A polls ?. 11-01 S commit and review F |
| casestatus (140) | 3 `--help` X. 10-24 S timed out at 120 s N. 10-27 A before and after counts in a pass report I. 10-28 A counts in a review I |
| register SQL (895) | 6 A read case transcripts: 1 review verdict, 1 code edit, 4 more reads: I 6 |
| pytest (5,909) | 6 A: 2 code edits, 1 review "Stands", 3 more runs: I 6 |
| reviewer (392) | 6 S launches after a pass. The agent runs async: ? 6. R: of 329 review lines with a count, 180 name 1 high or more |
| night (94, by number) | 104 merged, frames 101 and 88 closed C. 120 read on Fable, baseline counts at frame 121 K. 154 frame 282 pushed in the night, Sprint 12 P. 164 stopped by C55, Sprint 21 O. 173 frame 343 closed, Sprint 33 C. 174 Sprint 34 O |
| night read agent (74) | 6 S launches: nights 154, 155 cycle 1, 160, 160's interview, 163, 169: ? 6. The Sprint headings tie 23 reads to an order |
| nightreport (26) | 10-21 S, 10-23 S: report, then the night read agent G 2. 10-24 S report, note, hand-off H. 3 A: 2 work on the tool itself, 1 read: I 3 |
| nightcount (12) | 5 A: 2 build the tool's counter, 1 gets "no run named '--help'", 2 count for a read: I 5. 10-27 S "No module named 'rota'", brief written without counts N |
| interview (17) | 10-14 A page `plans/frame237-interview.md`, fix candidate chosen F. 10-17 A three interviews I. 10-18 S help X. 10-23 S interview agent G. 10-23 A help X. 10-28 S night 172's s238, door code read N |
| capability list (54 shell reads) | 11-01 S frame 356 pushed and placed P. 11-04 S, 11-06 S text into status lines K 2. 3 A reads I 3 |
| walk register (14) | 10-26 S two calls: night 166's rows copied by hand K 2. 10-31 S the long term plan written O. 2 A counts I 2. 1 mention X |
| dry run (10, by name) | dry3 merge, frame 361 pushed P. dry5 walls read, fix 2 built F. dry6 stopped at 6 minutes, a known-issues list O. dry6b its sizes held a merge in review F. dry6c two wall reads G. dry7 no merge, rule C77 written R |
| under 10 uses, all taken (6) | `score.py` 3 runs, page `plans/dry3-key-score-2026-11-03.md` K 1, I 2. `invariants` 1 run I. `probe_tools --help` traceback X. `talk --help` X |

## 4. The counts

- Instruments: 30. Group 1 holds 11, group 2 holds 19.
- Units. One call, turn, query or name: 5 (G1.8, G1.9, G2.12, G2.13, G2.14). One file, case, commit or tree: 6 (G1.10, G2.1 to G2.5).
- One session, hand-off, frame or stack moment: 6 (G1.1, G1.2, G1.4 to G1.7). One run, night or run database: 6 (G1.3, G2.6 to G2.9, G2.18).
- One request on one repository: 2 (G2.10, G2.11). A capability: 4 (G1.11, G2.15, G2.16, G2.17). One model load or page: 1 (G2.19). The destination sentence: 0.
- Runs in T, 31 days. At the unit of a name, a file, a case or a commit: 10,285. That is pytest 6,036, map 2,139, register 901, gate 657, reviewer 403, casestatus 149.
- Agents make most of those calls. The 5,855 `git log` calls are left out.
- At the unit of a run or a request: about 160 (nights about 37, night reads 74, nightreport 26, nightcount 12, dry runs 10).
- At the unit of a capability: 4 (`score.py` 3, `seat.py` 1). Zero runs: `audit`, `faults`, `triage`, `onboard_run`, `bench`, cockpit, `lens_check`, `wake_dump`, `progress`.
- Drawn uses: 120. A session-level act follows 42: H 12, K 7, F 6, G 5, P 4, O 4, C 2, R 1, L 1.
- No act in view follows 78: I 42, N 13, ? 13, X 10. Ten drawn "uses" are a `--help` call or a mention.
- Acts on rota's work, 23 of the 42, come from: dry run 6, night 5, gate 5, nightreport 2, interview 2, state 1, capability list 1, walk register 1.
- State prints in T: 102. "No frame." under the asked session: 67. Live counts printed: 193, over the cap of 10: 180.
- Gate status lines with a new-red count: 529. They say 0 in 103, 1 to 5 in 221, more than 5 in 205. 314 gate lines say "known", 278 say "flaky".
- Hand-off log: 130 claims, 118 confirmed, 11 unconfirmed, 18 `no_standby`.
- Open stack, less frames 363 and 364: 56 Sprint lines, 3 name a capability or the page. 137 Waits-on lines, 47 say "Roman's order".

## 5. Per group: meant to show, shows in fact, the evidence

### Group 1

Meant to show: where the build is. CLAUDE.md says the state print gives "the held frames, the live agents and nights, and the open decisions".

Shows in fact, compared today:
- The state print reads heading tags. It prints no agent and no night: `live = len(held) + ...` at `state.py` line 357.
- Today it prints "Live things: 17 of 10". True: frames 363 and 364 name 7fd2421e. Not live: 9 of the 17 name a session whose last call is 15 to 24 days old.
- Those 9 are frames 326, 327, 322, 315, 316, 306, 266, 203 and 140. Frames 326 and 327 say "parked for the frame economy" and still count.
- A taker's first print says "No frame." because the heading still holds the sender's tag. That is 67 of 102 prints. In both drawn takes the taker then greps the stack.
- Rule C46, as amended 2026-11-10, says "`state` prints the Destination and Next lines". The code at e956c737 prints a fixed Next line and no Destination line.
- The peers table holds 134 rows. 20 read `holding`. 1 of the 20 agrees with the stack, 17 name a frame that is not open. The legend says the column is not the truth.
- The table's use is its last line. "3 free standby" is the fact a sender needs, and 5 of 6 drawn reads lead to a hand-off step.
- The hand command does what its text says: 118 of 130 claims confirmed, and 5 of 5 drawn hand-offs end in a status line and a stop.
- Status lines: W45 holds 427 lines and 201 tool calls, so over half are written by another script. The tool's reason is the clock time and the backslash.
- The order heading follows a night's read from Sprint 8 to Sprint 35. Ten dry runs from 2026-10-31 to 2026-11-08 wrote none.
- The capability list: 3 of 56 Sprint lines name it. The rule of 2026-10-31 asks each Sprint line to name it. 9 of 5,048 status lines name it.
- The hook prints "on the first prompt of a session" and "on every prompt from 200k upward". CLAUDE.md says "each turn".
- `rulings --help` prints search hits, not usage. `map table case_runs` prints "no table named case_runs", and `rota/llm/cassettes.py` line 56 creates it.

### Group 2

Meant to show: whether rota delivers. The completion line: "every partial is built, click and two more lineage repositories merge cold, and the register is green or attributed".

Shows in fact:
- The most used instruments speak about a file, a case or a commit. They accept or refuse a pass. The gate leads to a commit or a fix in 3 of 6 draws, and to an act in 5 of 6.
- The gate's baseline is at 33c1e697, 2026-11-08 17:34, 33 known reds: 27 L1, 1 L2, 2 L3, 2 L3R, 1 G1. No unit test is in it. HEAD is 28 code commits later.
- A gate line is read by hand. One drawn session called "3 new reds, the known Tester cases" clean and launched a night.
- A register count is a count of replays. "A `5/5` and a `0/5` each rest on one call." The register replays at 12288 and a night runs at 16384.
- The night is the instrument that moves the work: 6 of 6 drawn nights end in a close, a push or an order. Its repository is click in every artefact.
- Nights stop at night 175, 2026-10-29. The night tools stop with them: last `nightreport` and `nightcount` runs 2026-10-28, last interview 2026-10-28.
- The walk register has no row for nights 90 to 165 and 167 to 175, and none for a dry run. Its merges read 14 of 156 rows.
- The long term plan of 2026-10-31 cites it: "no tips walk since 2026-09-14, no icalendar walk at all, `walks.jsonl`".
- The dry run is the one instrument at the unit of the destination's object, a merged change on a repository. Dry runs 1 to 3 merged one change each, on click, tips and icalendar.
- Dry runs 4, 5, 7 and 8 end with no merge, all on icalendar, under frame 362. I found no merge line for dry runs 6, 6b and 6c: not recorded in my read.
- Results of dry runs 1 to 3 are in `plans/operating-facts.md` as "The seat's ... measure". Results of dry runs 4 to 8 are in frame 362's status lines only.
- The seat of every dry run is the session or an agent on a strong model. The ruling of 2026-10-31 00:58 says so. No run has a person alone.
- COMPLETION names a measure for four capabilities. `seat.py`: 0 runs before 2026-11-10. The keys: 3 runs. The blind test: no run recorded to 2026-11-09.
- COMPLETION says "The night summary reports whether the chain fired". `nightreport.py`, `nightcount.py`, `walk.py` and the launcher hold no capability name.

## 6. What does not fit my reading

My reading has three parts. First, use falls as the unit grows: 10,285 runs at a commit or below, about 160 at a run, 4 at a capability, none at the destination sentence.
Second, the group 1 instruments print the text of the records, and the text is older than the state. Third, a result moves the work when its unit is a pass or a night.

These do not fit, with the same weight:
- The dry run. It measures at the destination's own object, and 6 of 6 drawn runs led to an act. It is 10 uses old and it is not in a register.
- The night. Its unit is three requests, and it led to an act in 6 of 6 draws. Use did not fall with its unit until the nights stopped.
- The hand-off commands. They are group 1, and they print the truth: 118 of 130 confirmed. Part two of my reading does not hold for them.
- The walk register. It is stale, and it still set step 3 of the long term plan. A stale instrument moved the order once.
- The state print's economy line. It printed over the cap in 180 of 193 counts. One drawn print came with a park, and one was followed by a push.
- The capability list after 2026-10-31. Shell reads rise to 19, 30 and 35 a week, and one drawn read placed a frame. The page is in use again.
- The interview. Its unit is one model call, the smallest, and its use is 17 runs and falling. Part one predicts high use for a small unit.
- The reviewer. 180 of 329 counted reviews name a high finding, so the instrument is not a formality. Its results were outside my view in 6 of 6 draws.
- Ten drawn "uses" were not runs. Eight are `--help` calls on five tools, and two are mentions. `rulings` and `nightcount` have no `--help`.

## 7. What this read could not see, and where the method can bend the result

- The transcripts start on 2026-10-10. For 2026-09-14 to 2026-10-09 I have status-line mentions and artefacts only. A mention is not a use.
- Roman's own looks are not in the count. I read no cockpit, no notification and no terminal reply of his.
- I did not run the gate, `casestatus`, `nightreport`, `nightcount`, a night or a probe. For those I compared no fresh output with its files.
- The next act is read from 2 to 4 acts after the result. An async agent's result is outside that view: 13 of 120 draws.
- A probe that runs from a scratchpad script is not counted. Replay, seam, consult and fuzz runs are under-counted, perhaps to zero.
- My first patterns counted a `grep` or a `sed` of a tool's source as a run. I corrected the patterns and drew again for six instruments.
- The first draws are not in the table. The corrected counts for `nightreport` fell from 96 to 26, and for `nightcount` from 49 to 12.
- One of my own scripts lost its backslashes in a heredoc. I found it by a count of zero and repaired it.
- I left 2026-11-10 out of every draw, to stay clear of the redirect's records. The counts in section 2 include that day.
- The state print showed me the headings and last status lines of frames 363 and 364. I used the print's counts and none of those lines' claims.
- `plans/method/reference.md` C46 carries a sentence from frame 363, "after eight dry runs wrote no order". I counted the headings myself and found ten runs.
- The act codes are my judgement on short excerpts. A second reader can class the 42 I uses and the 13 N uses in another way.
- The units in section 4 are one choice per instrument. The gate replays cases of requests, so "one tree" hides that it holds request-shaped cases.
- I wrote my reading after the counts, and I chose which counts to make. The counts I did not make are the larger risk.
