# Frame 287, read D: what a build session's context is spent on

Meta workflow. Read-only agent on Opus, 2026-10-17. The sources are the build transcripts
`0e37e9d7`, `d7c5dc6d`, `b0dce033`, `eefbf293`, `1cf2843b` and `cc1d654e`, plus the files of the
checkout. Scripts: `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d7c5dc6d-485b-4232-840c-a248ec516e0f/scratchpad/f287/ctx/`
(`fixed.py`, `events.py`, `cat.py`, `cycles.py`, `outtok.py`, `reads.py`, `stack.py`, and one `ev_<sid>.tsv`
per session). Transcript times are UTC. Local time is UTC+1 (observed: `git log` on plans/stack.md
prints +0100).

Units: "ctx" is `input_tokens + cache_read_input_tokens + cache_creation_input_tokens` of an
assistant record, which is the window that turn used. A size in "chars" is characters. A size in
"tok" without "ctx" is chars divided by four (reasoned: the brief's estimate where no usage field
exists). The chars/4 estimate is low for JSON and code. Section 1 shows the gap: 43k by chars/4
against 62.4k measured.

## The page: where the window goes

1. A session starts at 62.4k ctx before it does any work. Roughly 21k of that is tool schemas,
   10.6k is CLAUDE.md and the memory index, and 12.5k of the schemas belong to five tools that
   no recent session called (observed: section 1).
2. A standby spends about 12k more on wakes before it takes a frame. The take itself then costs
   27k to 38k ctx, and 58% to 78% of its tool output is `plans/stack.md` (observed: section 2).
3. A cycle costs the holding session 9.0k ctx at the median (mean 11.3k). The largest parts
   are the model's own output (4.7k tok, about half of it thinking), the brief, the agent's
   report, and the status-line script (observed: section 3).
4. Over a session that reaches 300k, the visible content is about 150k tok of a 285k to 300k
   growth. About 75k is thinking, and the rest is the gap between chars/4 and real tokens
   (observed: section 4).
5. The state is carried (stack, records, status writes, hand-off tool) at 32% to 51% of the
   visible content. Deciding (code, reports, night data, gate) takes 14% to 30%. The stack
   alone is 15% to 45% (observed: section 4).

The three largest items a design could stop loading or load smaller:

| Item | Today | Smaller form | Saving (reasoned) |
|---|---|---|---|
| Stack reads, at the take and inside the session | 698k chars, 3629 lines, 55% status lines. A take reads 32k to 60k chars of it. A session reads 89k to 244k chars of it. | One current-state block per held frame (the five fields and the last status line), with the history in a file nobody loads by default | Per hand-off about 7k to 14k tok. Per session about 20k to 55k tok. |
| Tool schemas that no build session calls | Artifact 35.1k, Workflow 5.5k, ScheduleWakeup 4.8k, ReportFindings 2.3k, ReadNotifications 2.2k chars: 0 calls in 5 sessions | Leave them out of the build sessions' tool set | About 12.5k tok by chars/4, and more by real tokens, once per session. The window carries it on every turn. |
| Standby wakes, and the per-turn hook and reminder text | 62.4k to 74.2k ctx before the take (d7c5dc6d). The hook text of 390 chars fires 58 times in one session. | A standby that wakes once on a claim. A hook line that fires once per session or only on a prompt from Roman. | About 10k ctx per hand-off for the wakes. About 5k tok per session for the hook. |

## 1. The fixed load of a turn

- First assistant record of `d7c5dc6d`, 2026-10-17T01:15Z: 62,380 ctx (2 input, 10,655 cache
  creation, 51,723 cache read) (observed: transcript, first assistant record). Six other
  sessions of 2026-10-15 to 10-17 start at 61.0k to 62.5k. On 2026-09-17, sessions started at
  about 49.1k (observed: `90522022` first record). The fixed load grew by about 13k in a month.
- System prompt, 3 blocks: 17,024 chars, about 4.3k tok (observed: first `api-request-shape`).
- Tool schemas, 19 tools: 85,614 chars, about 21.4k tok. The largest are Artifact 35,085,
  PowerShell 9,483, Workflow 5,504, AskUserQuestion 5,069, Agent 4,989, ScheduleWakeup 4,778
  (observed: same record).
- Instructions block: 42,518 chars, about 10.6k tok. Of that, CLAUDE.md is 33,519 chars (about
  8.4k tok) and MEMORY.md is 8,685 chars (about 2.2k tok) (observed: first `api-request-blob`
  and `wc -c`).
- Skill listing 17,593 chars (about 4.4k tok), deferred-tool, agent and MCP listings 9,544 chars
  (about 2.4k tok), environment and context reminders about 2.2k chars (observed: attachments).
- Sum by chars/4: about 43k tok against 62.4k measured. The gap is tokenization of schemas and
  markup (reasoned: JSON with short keys tokenizes near 3 chars a token).
- Hooks (`.claude/settings.json`): `UserPromptSubmit` runs the "Standing instruction" echo (390
  chars) and `context_count.py`. `Stop` runs `really_blocked.py`. The echo fires on every
  prompt, task notifications included: 58 times, 22,651 chars, in `0e37e9d7` after its take
  (observed: `hook_additional_context` attachments).
- Harness reminders after the take in `0e37e9d7`: output style 11,115 chars (117 times),
  batching 10,496 (82), total tokens 4,692 (92). With the hook, about 52.6k chars, about 13k tok
  per session (observed: attachments, 12:31Z to 16:54Z).
- Not loaded at start: `plans/composition.md` 6,782 chars, `plans/stack.md` 695,013 chars. Both
  enter only by a read (observed: `wc -c`).

## 2. A hand-off's reads

The take window is from the `take` command to the first agent launch, or to the state reply when
no agent launched.

**`d7c5dc6d`, taken 16:53Z from `0e37e9d7`, frame 283** (observed: `ev_d7c5dc6d.tsv` rows 28 to 46).
Ctx before the take 74,196. At the first launch 112,450. The take cost 38.3k ctx.

| Read | chars |
|---|---|
| watcher output and `take` | 703 |
| `git log` and composition page | 7,209 |
| momentum note `handoff-0e37e9d7.md`, stack lines 1 to 80, `## ` headings | 11,025 |
| stack lines 80 to 115 and held-frame headings | 2,441 |
| stack 861 to 960 (frames 283, 287) | 2,116 |
| stack 867 to 906, frame 283's status lines cut at 2,500 chars | 16,185 |
| stack 907 to 925 and frame 143's newest lines | 11,678 |
| sender's task output, worktrees | 3,954 |
| `wmic` gate processes, gate output size | 7,161 |
| `git log`, gate worktree listing | 1,936 |
| claim script, worktree checkout | 1,285 |
| total tool output | about 65.7k chars, stack about 38k (58%) |

**`0e37e9d7`, taken 12:31Z from `eefbf293`, frame 223** (observed: `ev_0e37e9d7.tsv` rows 20 to 36).
Ctx 74,582 to 111,088 at the state reply: 36.5k ctx. No agent launched, because night 154 ran.
Tool output: composition and git 7,244, momentum note 5,540, stack 59,461 (headings 334, lines 1
to 116 6,905, 80 frame headings 10,386, frames 223 and 281 17,903, five frames' fields 1,851, a
grep for `blocked`, `[high]` and `[med]` 22,082), night log 2,479. The stack is 78% of about 76k.

**`b0dce033`, taken 01:15Z from `1cf2843b`, frame 274** (observed: `ev_b0dce033.tsv` rows 6 to 15).
Ctx 66,501 to 93,256: 26.8k ctx. Composition, momentum note and git 12,459 chars. Stack 38,709
chars in three reads.

Before the take, each standby spent ctx on wakes: `d7c5dc6d` went from 62,380 to 74,196 over
seven wakes, two `/standby` prompts of 3,579 chars and one peers table of 7,431 chars (observed:
rows 0 to 27).

## 3. A cycle

Cycles in `0e37e9d7`, 15:40Z to 16:54Z (16:40 to 17:54 local). A cycle is cut at each agent
launch or `SendMessage`. It holds everything between the previous launch and this one: the
report that came in, the reads, the status script, the prose, the brief and the launch. That
gives 11 cycles, frames 283, 143 and 114 (observed: `cycles.py` on `ev_0e37e9d7.tsv`).

| Cycle (launch) | brief | report | status | stack read | prose | other reads | ctx delta |
|---|---|---|---|---|---|---|---|
| 283 pass 1 | 23,402* | 0 | 1,959 | 3,490 | 0 | 5,205 | 15,913 |
| 143 interview | 4,346 | 0 | 1,569 | 3,882 | 0 | 0 | 6,597 |
| 114 history read | 4,947 | 0 | 1,415 | 0 | 4,446 | 0 | 5,465 |
| 143 pass 1 | 4,619 | 6,733 | 5,691 | 2,339 | 5,682 | 29,064 | 37,270 |
| 283 pass 1b | 1,954 | 3,448 | 2,355 | 0 | 768 | 0 | 9,547 |
| 283 pass 1c | 1,683 | 2,854 | 2,256 | 0 | 827 | 0 | 3,664 |
| 283 review 1 | 4,077 | 2,256 | 4,092 | 0 | 336 | 1,290 | 9,777 |
| 283 pass 2 | 2,428 | 3,168 | 1,989 | 0 | 2,177 | 546 | 7,045 |
| 283 review 2 | 3,438 | 2,532 | 8,187 | 0 | 5,076 | 375 | 15,989 |
| 283 pass 3 | 1,968 | 426 | 1,762 | 0 | 582 | 3,951 | 9,042 |
| 283 pass 3b | 1,211 | 3,256 | 2,013 | 0 | 488 | 0 | 4,260 |

\* includes the 17,955-char sprint 12 order script. The brief itself was 4,746 chars.
The "143 pass 1" cycle holds Roman's question on frame 114 and the session's own read of LAWS,
DECISIONS and `api.py`.

- Median cycle: 11.0k visible chars (about 2.8k tok) and 9.0k ctx. Mean 11.3k ctx (observed).
- The model's output per cycle: median 4.7k tok. The visible part is about 2.6k tok. The rest,
  about 2.2k tok at the median, is thinking (observed: `outtok.py`, `output_tokens` against
  visible chars/4).
- The three largest visible parts at the median: the brief 3,438 chars, the report 2,532, the
  status script 2,013 (observed). Prose is 768 at the median, stack reads 0 at the median and
  9.7k over all 11.
- The status script is larger than the status line. It carries the old text as an anchor and
  the new line. The median status line in the stack is 373 chars (observed: section 7).
- Unseen and larger than any visible part: about 6k ctx per cycle beyond the visible chars/4.
  It is thinking plus the tokenizer gap (reasoned: 9.0k delta less 2.8k visible).

## 4. The window over a session

Whole transcripts. Classes by the command or path. "Carrying" is the stack, records, status
scripts, record writes and the hand-off tool. "Deciding" is code, agent reports and report
files, night data and gate output (observed: `cat.py`).

| | 0e37e9d7 | b0dce033 | cc1d654e |
|---|---|---|---|
| ctx first / last | 62,472 / 359,945 | 62,470 / 356,133 | 61,813 / 302,556 |
| output tokens (all) | 125,103 | 126,547 | 74,665 |
| visible content, tok | 149.8k | 152.9k | 136.2k |
| stack reads | 22.3k (14.9%) | 23.7k (15.5%) | 60.9k (44.7%) |
| other records read | 7.3k | 7.3k | 4.3k |
| status scripts | 14.7k | 15.9k | not split ** |
| record writes, hand-off tool | 4.3k | 5.1k | 3.7k |
| **carrying** | **48.5k (32%)** | **51.9k (34%)** | **69.0k (51%)** |
| code and tests read | 5.4k | 3.8k | 8.8k |
| agent reports (notifications) | 9.1k | 11.5k | 6.4k |
| report files read | 7.3k | 14.3k | 0.2k |
| night data (logs, `.db`) | 21.9k | 12.5k | 3.2k |
| gate and tests | 0.7k | 0.2k | 0.3k |
| **deciding** | **44.3k (30%)** | **42.4k (28%)** | **18.8k (14%)** |
| briefs, `SendMessage` | 17.2k | 20.9k | 17.2k |
| command text the session wrote | 9.5k | 9.8k | 11.3k |
| prose to Roman | 7.2k | 3.4k | 2.5k |
| hooks, reminders, Roman's words | 17.3k | 17.4k | 8.6k |

\*\* `cc1d654e` wrote its status lines without the `NOW=` form, so its status scripts sit in the
stack class. Its 44.7% stack share includes them (reasoned: the classifier keys on `NOW=`).

- Thinking: output tokens less the visible written part is about 75k in `0e37e9d7` (reasoned:
  125k output, about 50k visible writes).
- The rest of the growth, about 70k in `0e37e9d7`, is the chars/4 gap and message wrappers
  (reasoned: 297k growth less 150k visible less 75k thinking).

## 5. What is read and not used (by my reading of the next turns)

- `d7c5dc6d`'s take: the composition page (7.2k chars) is not quoted or cited in the state reply
  or the next ten turns. Frame 283's 40 status lines (16.2k chars) give one fact used, the
  newest line: review 3 of 7471569c is owed. The other 39 lines are not used. The stack head,
  lines 1 to 115, gives sprint 12's rows. The reply uses rows 1 and 2 only. Used: the momentum
  note (frame 287's question, the gate on 7471569c), frame 143's newest lines, the `wmic` gate
  check (the gate ran) (observed: reply at 16:58Z).
- `0e37e9d7`'s take: the 22.1k-char grep for blocked frames gave one fact: "No frame is blocked
  on Roman". The 80-heading list (10.4k chars) is used for the count line on 11 frames. The
  composition page is not cited. Used: the note's open question, frame 223's newest status
  (observed: reply at 12:32Z).
- `b0dce033`'s take: 38.7k chars of stack for a reply that uses frame 274's state, frame 264's
  block and the next step. The composition page is not cited (observed: reply at 01:16Z).
- The composition page is read at every take and cited in none of the three replies. Roman's
  rule asks for the read, so "not cited" does not mean "not used" (reasoned).

## 6. Repeated reads (five recent sessions)

Counted as a `Read`, or a `cat`, `sed`, `awk`, `grep`, `head` or `tail` that names the file.
Status scripts are excluded. `handover.py` counts are runs, not reads (observed: `reads.py`).

| Session | distinct files | read calls | stack reads | other files read more than once |
|---|---|---|---|---|
| d7c5dc6d | 18 | 33 | 7 | api.py 3, CLAUDE.md 2, operating-facts 2, MEMORY.md 2 |
| 0e37e9d7 | 35 | 95 | 17 | api.py 13, night154-read 6, test_revert_door 5, LAWS 4 |
| b0dce033 | 27 | 71 | 14 | l1_tester.yaml 9, operating-facts 6, night153-read 6, runner.py 4 |
| eefbf293 | 22 | 78 | 19 | api.py 19, test_triage_fork 4, night153-read 3 |
| 1cf2843b | 19 | 51 | 9 | test_toolproto_quotes 7, api.py 5, night152-read 4 |

- Read by every session: `plans/stack.md` and `plans/composition.md` (6,782 chars).
- The stack at each take, in lines and chars (observed: `git show` at the last stack commit
  before the take):

| Take (local) | Session | lines | chars |
|---|---|---|---|
| 10-17 00:20 | 1cf2843b | 3,369 | 610,966 |
| 10-17 02:15 | b0dce033 | 3,382 | 624,008 |
| 10-17 12:05 | eefbf293 | 3,470 | 637,221 |
| 10-17 13:31 | 0e37e9d7 | 3,491 | 659,491 |
| 10-17 17:53 | d7c5dc6d | 3,602 | 674,648 |

The stack grew by 233 lines and 64k chars in 17.5 hours (observed).

## 7. The stack as a record (today, 18:37 local)

- 3,629 lines, 698,427 chars, about 175k tok. That is more than the window that a session has
  left after its fixed load (observed: `stack.py`).
- 119 frames, all under "The batches". The "Parked" heading holds no frame (observed).
- Status lines per frame: median 3, maximum 74 (frame 204), 707 in all. Frame 243 has 67,
  frame 266 has 23, frame 283 has 19 (observed).
- Status line length: median 373 chars, 90th percentile 1,320, maximum 2,188 (observed).
- Share of the file: status lines 385,222 chars (55.2%). The five fields (Site, Ends when,
  Waits on, Sprint, Pointer) 108,043 (15.5%). Other prose inside frames 148,312 (21.2%).
  Headings 13,686. Above the frames, 43,045 chars: five sprint orders (sprints 8 to 12) and the
  "Stack" section that the file itself calls superseded since 2026-09-21 (observed).
- `plans/` holds 29 momentum notes, 142,991 chars. The rule says a note leaves when its frame
  closes (observed: `wc -c plans/handoff-*.md`). Each take reads one of them.

Usage: about 98k tokens (reasoned: the harness budget line, 14,953,582 at the start).
