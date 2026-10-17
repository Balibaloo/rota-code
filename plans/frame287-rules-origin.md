# Frame 287, read B: the rules of the method, their origins, and their cost

Meta workflow. Read-only, on Opus, 2026-10-17 18:31 by the clock. The
holding session reasons from this page alone.

## Summary

- Rules read: 118. The brief `CLAUDE.md` gives 75 (C1 to C75), the wall
  guide 13 (W1 to W13), the stack's head 10 (S1 to S10), and the memory
  files 20 that the brief does not restate (M1 to M20).
- Rules with a named origin: 64 of 118. 37 of 75 in the brief, 8 of 13 in
  the guide, 6 of 10 in the stack head, 13 of 20 in memory.
- Rules whose failure came back after the rule: 18. The largest: the
  history read before a question (5 strikes to 2026-10-17), the time from
  the clock (15 strikes to 2026-10-15), and the backslash patch (27 strikes
  to 2026-09-30).
- Rules that make a session read or carry something every turn: 7
  distinct (9 with the stack head's copies). Separately, the whole brief,
  584 lines and about 8.4k tokens, and `MEMORY.md`, 39 lines and about 2.2k
  tokens, load every turn (reasoned: 4 bytes a token on 33,519 and 8,685
  bytes).
- The main gap: the take's read list names the composition, the momentum
  note, the open frames and the memory files the frame names. It does not
  name `rota/LAWS.md`, `rota/DECISIONS.md`, the briefs, the archive, the
  transcripts or `plans/operating-facts.md`. The two rules that send a
  session to those files fire only at an escalation, and that failure
  recurred four times after the rule (observed: memory
  `rota-history-before-escalation.md`, strikes 2 to 5).

## The table

Columns: the rule, the origin, whether the failure recurred, the cost, and
what the rule stops a session from seeing. "none named" means the rule's
text carries no failure and no mark. "n/c" means not checked.

### The brief, `D:/repos/rota/CLAUDE.md`

| # | Rule (line) | Origin | Recurred? | Cost | Stops seeing |
|---|---|---|---|---|---|
| C1 | Ignore the context count below 300k; never write it (14-15, 575-584) | A peer handed off at 272k on its own estimate (no date, line 584) | n/c | Every turn: the hook's count is read and judged against three lines | none |
| C2 | At 300k finish the frame, take none, run `peers`, tell Roman (15-24) | ruled 2026-09-30, session 7448850f idle at 356k | Yes: 2026-10-11, frame 193 at about 300k waited (memory `hand-off-never-idle.md`, strike 2) | Once a session, one command | none |
| C3 | No hand-off below 400k while a held frame can move (25-29) | ruled 2026-09-27, a hand-off at about 300k left a review owed | No found: the 2026-10-07 hand-off at 295k held no frame (archive `stack-2026-10-08.md` line 15) | Once a session | none |
| C4 | Past 300k and idle, hand off at once with `hand` (29-44) | ruled 2026-10-01, a session at 299k while frames 106 and 100 waited | Yes: the same 2026-10-11 strike as C2 | Once a session: status line, commit, command | none |
| C5 | Oldest free standby under a 300k ceiling; the tool picks (45-54) | ruled 2026-09-20; observed a reserve at 152k beside one at 20k | n/c | None, the tool applies it | none |
| C6 | Act on `hand` exits 0, 4, 5 (55-65) | none named | n/c; exit 5 applied right on 2026-10-14 (archive `stack-2026-10-15.md` line 109) | Once a hand-off: read the exit and the output | none |
| C7 | A message only on exit 4, never first or alone (66-74) | the measurements in `operating-facts.md` | n/c | Once a hand-off | none |
| C8 | Never write that messaging is broken (75-78) | one hand-off arrived four minutes late (no date) | n/c | none | none |
| C9 | A hand-off is Roman's assignment; do not wait for a name (79-81) | none named | n/c | none | none |
| C10 | Write a momentum note `plans/handoff-<sid>.md` before `hand`; taker reads it, asks sender first; it leaves at the close (82-95) | ruled 2026-10-09 01:09 | n/c for loss; 29 notes stand in `plans/` on 2026-10-17, so the "leaves" clause is n/c per frame | Each hand-off: write 82 to 96 lines, about 1.4k tokens (observed: `handoff-0e37e9d7.md`, 5,682 bytes) | A transcript pointer was declined, so the taker meets Roman's words only as the sender quoted them |
| C11 | A hand-off means stop; one session holds the stack (96-102) | ruled 2026-09-20, two sessions in one checkout (118-123) | No found: "two sessions" hits after 2026-10-01 name investigations | none | none |
| C12 | A fresh-session task is a frame, not a claim (103-107) | the same, 2026-09-20 | No found | none | none |
| C13 | Push the frame, tell Roman; Roman assigns (108-117) | the same, 2026-09-20 | No found | Each frame that needs a session | Conflicts with S3, "frames are mine to open, order and close" (reasoned: the two texts) |
| C14 | A standby arms one watcher with `standby --sid` (132-137) | none named | n/c | One turn each two hours while a standby | none |
| C15 | One line, no line continuation (138-140) | a backslash breaks PowerShell (reasoned, no date) | n/c | Each arm | none |
| C16 | Do not pass a name (141-145) | one session typed a description (git `f06ffbf8`, 2026-09-20) | n/c | none | none |
| C17 | Background, timeout 7200000, prove the arm with `peers` (146-160) | the harness kill at two hours (git `78259764`, 2026-10-02) | n/c | Each arm, two commands | none |
| C18 | The watcher refuses at 300k; tell Roman (161-165) | none named | n/c | Once | none |
| C19 | Answer no permission prompt while arming (166-170) | none named | n/c | none | none |
| C20 | Act on watcher exits 0, 3, 1, 2 (171-179) | none named | n/c | Each wake | none |
| C21 | Correct the `handed` column with `holding` (180-191) | none named | Related: `holding --frame none` blocked an arm, 2026-10-16 (memory `rota-release-before-rearm.md`, 1 strike) | Each frame change | none |
| C22 | Arm one watcher only (192-196) | the tool enforces it from 2026-09-20 | n/c | none | none |
| C23 | Never spend a standby's context (197-206) | a standby went 20k to 152k in an afternoon (observed 2026-09-20, line 52) | n/c | none | none |
| C24 | Take step 1: `take --sid`, exits 0, 1, 6 (207-212) | none named | n/c | Each take | none |
| C25 | Take step 2: read the composition, then the momentum note (213-214) | the note: ruled 2026-10-09 | n/c | Each take: 152 lines (about 1.7k tokens) and about 90 lines (about 1.4k) | Not on the list: `rota/LAWS.md` (411 lines), `rota/DECISIONS.md` (1,512), the briefs in `rota/roles/prompts`, the archive (13,409 lines), the 105 transcripts, `operating-facts.md` (709). Frame 287's origin: the session that asked frame 114's question had never read LAWS.md (observed: `stack.md` line 912) |
| C26 | Take step 3: the open frames, yours and blocked on Roman, not the closed (215-216) | none named | n/c | Each take: the sprint head (about 65 lines) and the held frames, 16 at one take (observed: `stack.md` line 1031) | The closed frames, and open frames not held that share a cause: frame 220 held frame 114's cause five rows down (observed: `stack.md` line 912) |
| C27 | Take step 4: the memory files the frame names, not all (217) | none named | n/c | Each take, 15 to 114 lines a file | The memory files the frame does not name |
| C28 | Take step 5: state reply; a handed frame continues without a check (218-224) | ruled 2026-10-10 04:47, frame 193 | No: strike 1 only (memory) | Each take | none |
| C29 | Take step 6: claim with the sid prefix, peer name in the status (225-230) | none named | n/c | Each claim | none |
| C30 | On a goal, grill Roman every time, one question at a time; price each ends-when (231-239) | none named (memory `pocock-workshop-notes.md`) | The rule produced a failure: 2026-10-17 18:22, two grill questions on a goal he had discussed (memory, strike 5: "the whole design and rationale should be in the logs") | Each goal: Roman's attention | Nothing tells the session to read his discussed words first |
| C31 | An ends-when on a seat's behaviour has three parts (240-252) | ruled 2026-10-03, frame 111 | n/c | Each frame push | none |
| C32 | Read the failing turns before a cause; today's change last (253-257) | none named | Yes: the guide's placements read no turn (observed: `wall-guide.md` line 818, 2026-10-15) | Each loop cycle | none |
| C33 | Interview the seat before a second brief shape (257-269) | ruled 2026-10-02 15:02, frame 110 | n/c | One cycle a seat failure | none |
| C34 | Place each wall by the guide's section 4; cheap or escalate; every wall fixed or open (270-280) | ruled 2026-10-15, frame 251 | Yes: frame 114's question went to Roman a fourth time on 2026-10-17 while frame 220 held its cause (observed: `stack.md` line 912) | Each night read: the guide, 863 lines, about 13k tokens | The guide enters by an open frame's sign (W5); no step asks which law or design decides |
| C35 | A door or predicate carries its count every night (280-282) | none named | n/c after the rule; 17 of 26 named doors had no later count before it (observed: `wall-guide.md` line 851) | Each night, each door | none |
| C36 | A seat that judged against a fact is escalated only after a multi-sample interview (282-287) | ruled 2026-10-15 | n/c | Each such wall | none |
| C37 | Opus builds, Fable judges (288-293) | ruled 2026-09-24 01:07, frame 74's count | n/c | none | none |
| C38 | Every agent passes `model: "opus"` (294-305) | ruled 2026-10-07 00:50, a Fable day cost 437k a read | n/c | Each agent, one field | none |
| C39 | One implementer a frame, resumed; writer never reviews; fresh agent near 350k (306-313) | none named | n/c | Each pass, tokens in the status | none |
| C40 | Three agents at once, about twenty cycles a session (315-329) | ruled 2026-10-11 05:51; observed frames 199 and 195 | n/c | A cycle count carried across the session | none |
| C41 | `Site:` first; two frames on one file never held together (330-333) | the same ruling | n/c | Each push | none |
| C42 | Price in cycles; actual at the close (334-335) | the same ruling | n/c; closed frames ran a median 5 cycles against 2 to 3 priced (observed: `wall-guide.md` line 667, before the guide) | Each push and close | none |
| C43 | Reports to a file, ten lines back (336-341) | the same ruling, 10k to 15k against 3k | n/c | Each cycle | The session sees the report only for "the judgement cases" |
| C44 | The night is the hand-off boundary (342-348) | the same ruling | n/c | Each design frame | none |
| C45 | One checkout; gate and commit one at a time (349-352) | the same ruling | Related: gate run in the checkout, 2 strikes by 2026-10-12 (memory `rota-gate-from-a-worktree.md`) | Each gate | none |
| C46 | A push is a placement; a `Sprint:` line; no "Waits on: Roman's order" (353-368) | ruled 2026-10-12 23:40, 24 frames unplaced | Yes: the line stands in archive `stack-2026-10-14.md` 77 and 152, `stack-2026-10-15.md` 213 and 241, `stack-2026-10-17.md` 27, `stack.md` 1295, 1317, 1327 (observed 2026-10-17; push dates n/c, some may predate the rule and never have been swept) | Each push one line; each night read a re-cut | none |
| C47 | The session picks the next night's wall (369-377) | ruled 2026-10-12 23:52 | n/c | none | none |
| C48 | The sprint order never pauses the session (378-386) | ruled 2026-10-16 22:33, a 20-minute timer on sprint 10 | No: strike 1 only | Each night read, one notification | none |
| C49 | Two features wait on a night (387-389) | none named | n/a | Carried every turn with no action | none |
| C50 | Same edit in more than three files is a script (391-396) | none named | n/c | Each such edit | none |
| C51 | Touched tests, then the gate; read five lines and the stale line (397-401) | none named | Related: gate piped through tail, 2 strikes by 2026-09-24 (memory) | Each pass | The log |
| C52 | Ask the map tool before grep (402-406) | none named (git `128c68c9`, 2026-09-17) | n/c | Each code search | Code only: the map has no key for a ruling, a frame or a law |
| C53 | A design review; a diff review after every pass (407-414) | ruled 2026-09-27, frame 86's four reviews | No found: no "no diff review" after 2026-09-29 | About 100k a design review; one review a pass | The reviewer never reads the reasoning |
| C54 | A frame on the seats ends on a walk from a worktree (415-421) | none named | n/c | Each such frame, a night | none |
| C55 | Stop a night that loops on another frame's wall (422-431) | ruled 2026-10-09 20:19, night 137 | Yes, by the step cap: night 142 walk 1 on 2026-10-12 05:14 (archive `stack-2026-10-13.md` 104), night 146 walk 1 on 2026-10-14 (archive `stack-2026-10-14.md` 47), night 150 walk 2 on 2026-10-16 (`stack.md` 1028). Which frame each loop belonged to is n/c except night 150 | At every CYCLE line, name the frame | none |
| C56 | A loop on no held frame's site stops the night (432-438) | taken by timeout 2026-10-16 07:23, night 150 | No found | At the first CYCLE line | none |
| C57 | Escalate as a blocked frame; four triggers (439-442) | none named | n/c | Each block | none |
| C58 | Before a block, an agent reads LAWS, DECISIONS, archive, facts, briefs, `git log -S` (443-450) | ruled 2026-10-03, frames 114 and 115 | Yes: 2026-10-04 (strike 2), 2026-10-12 (3), 2026-10-17 (4, frame 114 again), 2026-10-17 18:22 (5) (memory `rota-history-before-escalation.md`) | One Opus agent, about 100k, a question | Fires only at a question; the take and the placement never read these files |
| C59 | Before any question, read the records and transcripts; test the answer (451-465) | ruled 2026-10-04 14:52 | Yes: the same strikes 3 to 5 | The same agent | The same |
| C60 | Escalation by `AskUserQuestion` or `PushNotification` (466-476) | ruled 2026-09-20 | n/c | Each stop | none |
| C61 | One notification a stop; none for progress (477-481) | none named | n/c | none | none |
| C62 | Rate each question high, medium or low (482-486) | ruled 2026-10-02, 5 h 18 min idle on two low questions | The timer this rule set paused sprint 10 on 2026-10-16 (C48's origin) | Each question | none |
| C63 | Rating first word; low by notification and a 20-minute timer (487-498) | ruled 2026-10-02 | Applied: "taken by timeout" in archive 2026-10-04 to 2026-10-17 | Each question, a timer | none |
| C64 | Every conclusion carries a mark; observations dated (499-505) | none named in the brief (S8 gives 2026-09-16) | n/c | Every turn that writes a conclusion | none |
| C65 | Copying a claim never observes it (506-508) | none named | Yes: inherited questions sent unread on 2026-10-12 (frame 198) and 2026-10-17 (frame 114) (memory strikes 3 and 4) | Each copied claim | none |
| C66 | Say which workflow (509) | none named in the brief (S8: ruled 2026-09-16) | n/c | Every statement about records | none |
| C67 | Five lines a frame; reasoning to a record file (510-512) | ruled 2026-09-27, frame 86's 130 lines | Yes: `stack.md` holds 3,618 lines for 119 frames, about 30 a frame; frame 287's status lines run to about 1,000 characters each (observed 2026-10-17, lines 910-920) | Each status | none |
| C68 | Name with every frame number; status time from the clock (512-516) | none named in the brief (S7: 2026-09-21, frame 52) | Yes for the time: strikes 13 to 15 on 2026-10-12, 10-13, 10-15 (memory `rota-status-time-from-clock.md`) | Every mention, every status | none |
| C69 | A measurement writes one register line (517) | none named | n/c | Each measuring frame | none |
| C70 | A retry-cost failure goes to `operating-facts.md` keyed by its error text; a habit to memory with strikes (518-526) | proposed 2026-09-23 | n/c | Each failure | A failure that is not an error text has no key |
| C71 | Closed frames leave; commit the stack alone after every change (527) | none named | n/c | A commit each change | The archive, after the close |
| C72 | Never edit another session's frame, except waits-on (528) | none named | n/c | none | none |
| C73 | Decide judgement and completion; check own instruction files with Roman (529-531) | none named | n/c | none | none |
| C74 | Conventional Commits, no co-author footer (534-536) | none named | 1 strike 2026-10-09 (memory) | Each commit | none |
| C75 | Simplified Technical English for all prose (538-584) | ruled 2026-09-04 (memory `ste-output-format.md`; git `6aa64fea`, 2026-09-08) | n/c | Every reply, every turn | none |

### The wall guide, `D:/repos/rota/plans/wall-guide.md`

| # | Rule (line) | Origin | Recurred? | Cost | Stops seeing |
|---|---|---|---|---|---|
| W1 | Every wall a read names is fixed cheaply, escalated, or open with its reason (22-33) | ruled 2026-10-15, "try to fix everything", "Reasonably" | n/a | Each wall a frame; the stack holds 119 frames (observed: `stack.md` headings, 2026-10-17) | none |
| W2 | The guide is the record the designer restarts from (37-44) | observed: each hand-off relearned the judgement (fit review section 1); ruled 2026-10-15 | n/c | Each night read, 863 lines | Laws and decisions: the guide cites DECISIONS by line, not by question |
| W3 | Each cause entry: confirm, cheap fix, overfits, not now, escalate (119-131) | ruled 2026-10-15 | n/c | Per wall, one entry | none |
| W4 | Cause 16: name the residue by cause; merge frames under one cause (653-685) | ruled 2026-10-03, the residue rule | Yes: frame 287's heading says walls are filed "by their sign" (observed: `stack.md` line 910, 2026-10-17) | Each night read | none |
| W5 | Step 1: is the sign an open frame's sign? (756-764) | ruled 2026-10-03 | Yes: frame 114, 2026-10-17 (see C34) | Each wall: the stack's headings | The law or design that decides the case; it is asked nowhere in steps 1 to 8 |
| W6 | Step 2: is the instrument right? Cause 13 (765-766) | none named | n/c | Each wall | none |
| W7 | Step 3: his words or his page first. Causes 1, 11 (767-770) | none named | n/c | Each wall | none |
| W8 | Step 4: a door fired? Causes 8, 9, 10, 7 (771-775) | none named | n/c | Each wall | none |
| W9 | Step 5: the rule read the rows it means? Causes 6, 12, 14, 15 (776-779) | none named | n/c | Each wall | none |
| W10 | Step 6: the fact in the prompt? Causes 2, 3, 4 (780-782) | none named | n/c | Each wall, the night database | none |
| W11 | Step 7: interview in the exact context (783-786) | ruled 2026-10-02 15:02 | n/c | One cycle | none |
| W12 | Step 8: decide; two reads before any question (787-793) | ruled 2026-10-15 and 2026-10-04 14:52 | Yes, as C58 | Each wall | The two reads come after placement, not before it |
| W13 | A door at 0 of 0 for three nights closes; its count line stays (802-805) | ruled 2026-10-15, "Yeah" | n/c | Each night | none |

### The stack's head, `D:/repos/rota/plans/stack.md`

| # | Rule (line) | Origin | Recurred? | Cost | Stops seeing |
|---|---|---|---|---|---|
| S1 | Push before starting; pop when ends-when holds (12-13) | Roman, 2026-09-14 (line 8) | n/c | Each frame | none |
| S2 | Dated status line at every change and before compaction (14-15) | the same | n/c | Each change | none |
| S3 | Frames are mine to open, order and close (16-17) | none named | n/a | none | Conflicts with C13 and the brief's line 229, "Roman assigns. You do not pick" |
| S4 | Linear; a waiting frame says which (18) | none named | n/c | none | none |
| S5 | Five lines; peer name in the status (19-20) | none named; copy of C67 | as C67 | as C67 | none |
| S6 | Sid in the heading; popped frame verbatim to `archive/stack-<date>.md` (21-23) | none named | n/c | Each close | The archive is keyed by close date, not by frame number or file |
| S7 | Name with every number (24-30) | adopted 2026-09-21, frame 52 | n/c | Every mention | none |
| S8 | Marks, workflow name, dated observations (31-38) | ruled 2026-09-16; adopted 2026-09-20, frame 50 | as C68 | Every conclusion | none |
| S9 | `Site:` and cycles (39-45) | ruled 2026-10-11 05:51; copy of C41, C42 | as C42 | Each push | none |
| S10 | Three agents, twenty cycles, hand off at a night (46-48) | the same; copy of C40, C44 | n/c | Each session | none |

### Memory rules not restated in the brief, `C:\Users\roman\.claude\projects\d--repos-rota\memory\`

Origins are from the index line and the strike lines read. Files not read in
full are marked so.

| # | Rule (file) | Origin | Recurred? | Cost | Stops seeing |
|---|---|---|---|---|---|
| M1 | Backslash patches through Write or Edit (`heredoc-backslash-corruption.md`, 114 lines) | strikes from 2026-08-28 | Yes: 27 strikes by 2026-09-30 | Each scripted edit | none |
| M2 | Never pipe the gate; read the task output (`rota-gate-five-lines-unpiped.md`) | 2026-09-24 | Yes: 2 strikes by 2026-09-24 | Each gate | none |
| M3 | The acceptance gate runs from a worktree (`rota-gate-from-a-worktree.md`) | 1 strike 2026-10-09 | Yes: strike 2, 2026-10-12, session d609cf11 | Each gate | none |
| M4 | Re-records are cheap; run them without asking (`rota-rerecords-are-cheap.md`, 72 lines) | not read in full | n/c | none | none |
| M5 | Probes pin GIT_ENV (`rota-probes-pin-git-env.md`) | frame 70 built a repair for nothing | n/c | Each probe | none |
| M6 | Never copy over a busy register; never filter processes on own words (`rota-never-copy-over-a-busy-register.md`) | 1 strike each, 2026-10-12 | n/c | none | none |
| M7 | Run `release` before a re-arm (`rota-release-before-rearm.md`) | 1 strike 2026-10-16 | n/c | Each re-arm | none |
| M8 | Never pick a hand-off target from ListAgents (`peer-list-is-machine-wide.md`) | not read in full | n/c | none | none |
| M9 | "0 free standby" means unarmed; say both numbers (`reserve-empty-means-unarmed.md`) | not read in full | n/c | none | none |
| M10 | Read agent tokens from the harness line (`rota-agent-usage-from-harness.md`) | not read in full | Applied: status lines say "on the harness line" (archive 2026-10) | Each cycle | none |
| M11 | Loop agents wait in the foreground (`rota-loop-agents-wait-in-foreground.md`) | not read in full | n/c | Each re-record brief | none |
| M12 | Read a CYCLE line at once during a night (`rota-check-a-cycle-when-it-fires.md`) | ruled 2026-09-29, night 96 | No: strike 1 only | Each CYCLE line | none |
| M13 | An unclear hand-off goes to the previous session, not Roman (`ask-the-previous-session-first.md`) | ruled 2026-09-24 15:50 | n/c | Each take | none |
| M14 | Tell Roman what a frame changes; the number is a tag (`rota-frames-mean-not-number.md`) | ruled 2026-10-02 | n/c | Every reply to Roman | none |
| M15 | A grill question is one story in plain words (`rota-grill-in-plain-words.md`, 50 lines) | ruled 2026-09-24 | Yes: 3 strikes | Each question | none |
| M16 | Grill the purpose before content (`rota-grill-purpose-before-content.md`) | 1 strike 2026-10-15 | Yes: strike 2, 2026-10-17 18:19 (observed: `stack.md` line 919) | Each re-scope | none |
| M17 | Status summaries at the top of a reply (`plan-summaries-at-top.md`) | not read in full | n/c | Every reply | none |
| M18 | Night dollars are nominal; report asks and tokens (`rota-night-dollars-are-nominal.md`) | ruled 2026-10-16 | n/c | Each night report | none |
| M19 | Phase-optimised development plans (`rota-iteration-speed.md`, 53 lines) | Roman (not read in full) | n/c | none | none |
| M20 | Low-frequency method for vision work (`rota-low-frequency-method.md`) | not read in full | n/c | none | none |

## 1. The reading order at a take

The order is the brief's, lines 207 to 217 (observed). Sizes are lines on
2026-10-17. Tokens are estimates at 4 bytes a token (reasoned).

| Step | What | Lines | Tokens |
|---|---|---|---|
| 0 | `CLAUDE.md`, loaded by the harness | 584 | about 8.4k |
| 0 | `MEMORY.md`, loaded by the harness | 39 | about 2.2k |
| 1 | `take --sid` output | a few | under 0.1k |
| 2 | `plans/composition.md` | 152 | about 1.7k |
| 2 | `plans/handoff-<sender>.md` | 82 to 96 | about 1.4k |
| 3 | `plans/stack.md`, the sprint head and the held frames | about 65 plus about 30 a frame, 16 frames at one take | about 4k plus about 23k |
| 4 | The memory files the frame names | 15 to 114 each | about 0.5k to 2k |
| | Total | | about 40k to 45k |

What is not on the list, and what each holds (observed sizes):

- `rota/LAWS.md`, 411 lines, about 5.6k tokens. The laws a door derives
  from. Frame 114's question was answered by law 12 in one sentence.
- `rota/DECISIONS.md`, 1,512 lines, about 22k tokens. The guide cites it by
  line number.
- The briefs in `rota/roles/prompts`. What a seat is told.
- `plans/archive/stack-*.md`, 28 files, 13,409 lines. Every closed frame.
- `plans/operating-facts.md`, 709 lines, about 34k tokens. Read by section.
- `plans/wall-guide.md`, 863 lines, about 13k tokens. Read at a night read.
- The transcripts, 105 `.jsonl` files. Roman's words. Reached only by a
  keyword script at an escalation (C59).

The read list is a list of state: what is open now. It holds no list of
precedent: what was decided and why (reasoned: steps 2 to 4 name only open
and current records). The history files arrive only through C58 and C59,
which fire after a question forms. Four of the five strikes of the history
rule are questions that formed without that read (observed: memory
`rota-history-before-escalation.md`).

## 2. What the brief carries every turn

The brief is 33,519 bytes, about 8.4k tokens, every turn (observed: `wc`).
`MEMORY.md` adds 8,685 bytes, about 2.2k tokens (observed). Seven rules act
every turn: C1, C64, C66, C68, C75, M14, M17.

Rules that apply on fewer than one turn in ten, by this reading (reasoned:
each fires at an event that a session meets a few times in a few hundred
turns):

- The hand-off procedure, lines 14 to 123, 6,342 bytes, about 1.6k tokens:
  fires at 300k and 400k, once a session.
- Standby duty, lines 125 to 230, 5,121 bytes, about 1.3k tokens: fires
  only in a standby and at a take.
- The night rules, C44, C54, C55, C56: fire on a night.
- The sprint rules, C46 to C48: fire at a push and a night read.
- The escalation route and rating, C57 to C63: fire at a question.
- C49, "two features wait on a night": no action at any turn.
- The commit section: fires at a commit.

Together these are about 4k to 4.5k of the 8.4k tokens, roughly half the
brief (reasoned: byte counts of lines 14 to 230 and 353 to 498, less the
rules in that range that apply each cycle). Each rule also carries its
origin in prose, often 3 to 6 lines of a past session's story (observed:
lines 118-123, 240-252, 422-438).

## 3. The keys the records have today

| Key | File that uses it | What it finds |
|---|---|---|
| Frame number, `### n.` | `plans/stack.md` | An open frame |
| Close date | `plans/archive/stack-<date>.md` | A closed frame, only by the date it closed |
| Session id prefix | stack headings, `plans/handoff-<sid>.md` | Who held a frame |
| Error text, verbatim | `plans/operating-facts.md`, the tool sections | A failure that cost a retry |
| Memory index line | `MEMORY.md` | A habit with a strike count |
| Function, table, mode, file | `python -m rota.tools.map` | Code definitions, writers and readers |
| Law number | `rota/LAWS.md` | A law |
| Line number | `rota/DECISIONS.md` | A decision, cited as "line 943" |
| Night number | `plans/night<n>-read.md` | A night's read |
| Cause number | `plans/wall-guide.md` section 2 | A wall's cause, with October frames placed |
| Ruling date and time | "(ruled: Roman, date time)" marks | A ruling, by grep on the date only |
| Commit sha | git | A change |

Questions a session asks of the past that have no key (reasoned: no file
above is indexed by them):

- "Was this decided?" Rulings sit in the brief, stack statuses, the guide,
  memory, DECISIONS and the transcripts. No index is keyed by the question.
- "Why does this door exist?" A code comment may name a frame or a night.
  The map tool gives the function, not the ruling or the law behind it.
- "What touches this file?" `Site:` is on open frames only. The archive
  is not keyed by file. `git log -- <file>` gives commits, not frames.
- "What is next and why?" The sprint section at the top of the stack,
  reasoned, and rewritten each night read.
- "Which frames share a cause?" The guide's section 2, for October only.
- "What did Roman say about this?" The transcripts, by a keyword script.

## 4. The rota workflow's answer: how a seat's wake is built

1. A seat restarts from records, with no snapshot (observed:
   `plans/composition.md` lines 57 and 105).
2. Work is not assigned. The wake is the assignment, and outstanding work
   is re-derived from the records each pass (observed: composition 52-54).
3. `predicate_wakes` (`rota/core/scheduler.py:1331-1343`) runs every
   predicate in `REGISTRY` (`rota/core/predicates.py`) in order. Each
   predicate queries tables and yields a `Wake` with its subject (observed:
   map tool).
4. `build_prompt` (`rota/core/runner.py:607-729`) composes the system text
   by `compose_system` (347): the role's brief and its signatures.
5. The user text states the subject plainly and the predicate's detail,
   for example "without a test: c1, c2" (observed: runner 634-667).
6. It adds pushes keyed by the wake: `_failed_run_blocks`,
   `_raised_signature_pushes`, `_criterion_surface_pushes` (reads
   `criteria`), `_relay_contest_block` (reads `criteria`) (observed: map).
7. `push_working_set` (runner 3343) calls every read the graph's `reads`
   edges give the role that takes no argument, and pushes the result.
8. Every push goes through one cap, `PUSH_CHARS`, so a wake's prompt never
   exceeds the window (observed: runner 715-728).
9. Tables read on the way include `criteria`, `tests`, `test_runs`,
   `rulings`, `decisions`, `items`, `refs`, `messages` and `code_index`
   (observed: `FROM` clauses in `runner.py`; which function reads which is
   n/c beyond step 6).
10. The seat never chooses what to read for its wake. The structure keys
    the push by the wake's subject. The build session has no such builder:
    its take reads a fixed list of state files, and its precedent is
    fetched by an agent only after a question forms (reasoned: section 1
    beside steps 3 to 8).

Usage: about 75k tokens of this agent's context (reasoned: estimate from
the reads; the harness line is the measure).
