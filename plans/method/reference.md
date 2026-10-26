# The method's rules, by moment

This page holds every rule of the build session, the meta workflow, keyed by the moment it fires at.
Read the moment you are at, and never the whole page.
`plans/operating-facts.md` holds the measurements, and `plans/wall-guide.md` holds the wall causes.
A change to a rule is a proposed amendment in `plans/method/amendments.md` until Roman rules it.

How to read an entry. The tag in brackets is the rule's row in
`plans/frame287-rules-origin.md`: `C` is the old first section of
`CLAUDE.md` with its line, `S` the old head of `plans/stack.md`, `M` a
memory file. The mark and the origin come from the rule's own text, or from
the origin read when the text named none. `Tool:` names the tool that does
the step today. A rule whose tool does the whole step says so, and it leaves
this page when the tool is proven. Ruled words stay as Roman said them.
Swept from `CLAUDE.md` and `plans/stack.md` on 2026-10-18, frame 287, build
step 3 (ruled: Roman, 2026-10-18 02:35, "double check reasoning, then yes").

## 1. Every reply and every record

Added moment: these rules fire on every turn, so no other moment holds them.

- [C1] The hook gives the context count each turn. Do not write the count in
  a brief, a status line or a reply, and do not let it shape a frame. The
  three warnings stay in `CLAUDE.md`, section 1. Why the count arrives every
  turn: "the harness cannot know which turn is the last". A peer once handed
  off at 272k on its own estimate (observed: no date, old `CLAUDE.md` line
  123). The old text says the judgement holds to 400k. The hand line is now
  350k (ruled: Roman, 2026-10-18 02:30, "maybe last 50k not 100?", then
  "1 double check reasoning, then yes" at 02:35).
- [C75] Write all prose for a person in Simplified Technical English
  (ruled: Roman, 2026-09-04, memory `ste-output-format.md`). The rules stay
  in `CLAUDE.md`, section 4.
- [M17] Put the result or the status answer at the top of a reply. A status
  answer in the middle of a long stream is not seen (observed: memory
  `plan-summaries-at-top.md`, 2026-08-26).
- [M14] Tell Roman what a frame changes in rota. The number is a tag, as
  in F-111 (ruled: Roman, 2026-10-02 18:58, "The meaning of the frame is
  important whereas the number is not", memory `rota-frames-mean-not-number.md`).
- [C68, S7, merged] Every frame carries a name of a few words in its
  heading. Every mention of the frame carries the name with the number, in
  a status line, a commit message, a message to a peer and a reply to Roman.
  "Frame 50" is an index into a file. "Frame 50, port the hand-off kit" is
  a thing Roman can answer about (adopted from the kit: 2026-09-21, frame
  52). S7 and the C68 sentence are the same rule twice.
- [C64, S8, merged] A conclusion goes to a record when it forms. Every
  conclusion carries a mark with a reason the size of a commit headline:
  (observed: where and when), (reasoned: why), or (ruled: why). An
  observation carries its date, because an observation ages. A check quoted
  without its date is a prediction that wears the word observed. A
  prediction never gates. An assertion about what a mechanism does is
  (reasoned) until you run it (adopted from the kit: 2026-09-20, frame 50).
  S8 and C64 are the same rule twice.
- [C65] Copying a claim never observes it. A claim you take from another
  record keeps that record's mark and date. One unrun claim copied into
  three records is still one claim nobody ran (observed: inherited
  questions sent unread, 2026-10-12, frame 198, and 2026-10-17, frame 114).
- [C66, S8, merged] Say which workflow a statement is about: the meta
  workflow, this build session, or the rota workflow, the seats (ruled:
  Roman, 2026-09-16, "from now on we need to be specific if we're talking
  about the meta workflow or the rota workflow", memory
  `rota-name-the-workflow.md`).
- [C73] In the smart zone you decide judgement and completion. You write
  your own instruction files and check them with Roman (no origin named).
  A change to this page is a proposed amendment, as the head says.

## 2. The take

The take is the moment a session receives a handed stack. The intent page
comes first, then the state print, then the sender's note.

- [C24] Take any hand-off that waits for you:
  `python rota/tools/handover.py take --sid <your session id>`. Exit 0
  prints a frame and the stack's commit, and the frame is yours. Exit 1
  means nothing waits, so continue. Exit 6 means a frame waits and its file
  does not open: run the command again in a minute, and take no other work
  until it opens (no origin named). The same steps stay in `CLAUDE.md`,
  "Standby duty". Tool: `handover.py take`, the rule leaves this page when
  the tool is proven.
- [C25] Read `plans/composition.md`, then the sender's momentum note, when
  one exists. The note is now `plans/method/handoff-<sender sid>.md`, and
  `handover.py` also finds the old path `plans/handoff-<sid>.md` (observed:
  `NOTE_PATHS`, 2026-10-18). The note: ruled: Roman, 2026-10-09 01:09.
  Tool: `state --from <sender sid>` prints the sender's doubts.
- [C26] Read the open frames: yours, and any blocked on Roman. Not the
  closed ones (no origin named). Tool: `state --sid <sid>`, the rule leaves
  this page when the tool is proven. The stack is the history behind the
  print, and nobody reads it whole (reasoned: the take cost 35k from the
  3,700-line stack, `plans/method/design.md`, section 1).
- [C27] Read the memory files the frame names, not all of them (no origin
  named). After this sweep, read the reference moments the held frames will
  meet in place of the rota memory files.
- [C10, the taker's part] The taker reads the note after the composition
  page and before the stack. It messages the sender for a context question
  before it asks Roman (ruled: Roman, 2026-10-09 01:09, "3 yeah would be
  good for some context questions"). The message is an option and not a
  step. The taker owns the stack from its first status line, and the sender
  stops when the taker messages it released (ruled: Roman, 2026-10-18 02:20,
  "bi directional communication seeded with a handover doc / because the
  session needs to take ownership"). Tool: `handover.py`, the dialogue.
- [M13] An unclear hand-off is a message to the session that handed it.
  Roman answers rulings only (ruled: Roman, 2026-09-24 15:50, "Message the
  previous session if not clear, unless you need to grill me", memory
  `ask-the-previous-session-first.md`). M13 and the C10 sentence say one
  thing from two sides, and both stay.

## 3. The first reply

- [C28] Reply first with the state: the open frames, and each blocked
  question with a recommended answer. Then give your reading of Roman's
  ask. **A handed frame continues without a check** (ruled: Roman,
  2026-10-10 04:47, "don't ask when you are handed over to", after a
  session took frame 193 and asked before pass 1). Start the frame's next
  step after the state reply. Check your reading first only on a frame
  Roman gives you fresh. Memory `rota-handed-frame-continues.md` holds the
  same rule. Tool: `state` prints the state.
- [C29] Claim the frame Roman gives you with the first eight characters of
  your session id in the frame's heading. The id is stable across a
  restart. The peer name is not, so write your current peer name in the
  frame's status line for messages. Roman assigns. You do not pick (no
  origin named). S6's first sentence is the same rule.

## 4. A frame's push and placement

- [C30] On a goal, grill Roman one question at a time, each with a
  recommended answer, until the work quantises into frames. A frame has an
  observable ends-when, a visible end, countable attempts or a loop through
  agents, and a named wait. At the grill, each ends-when line carries a
  token price from the anchors in `plans/operating-facts.md` and the
  behaviour the price buys. A line with a price and no behaviour becomes
  its own frame below. The closing status writes the actual beside the
  estimate, walls counted apart (no origin named, memory
  `pocock-workshop-notes.md`). Amended: a grill asks only what the records
  leave open (reasoned: `plans/method/intent.md`, after Roman, 2026-10-17
  18:23, "the whole design and rationale should be in the logs"). Before
  a grill, run the question moment's history read, section 11.
- [S1] Push a frame before you start it. Pop it when its ends-when holds
  (ruled: Roman, 2026-09-14). C30 says "Push a frame before you start it"
  too. The two are the same sentence twice.
- [S3, C13] S3 says that frames are the session's to open, order and
  close, that Roman's asks are frames marked "(Roman)", and that Roman can
  pop or reorder anything (no origin named). C13 says that when a frame
  needs a session and you are not full, you push the frame and tell Roman,
  because Roman assigns work to a session and you do not (ruled: Roman,
  2026-09-20). The rules have two scopes: C13 governs which session does
  the work, S3 governs the frames inside the one held stack (reasoned: the
  step 3 review, 2026-10-18). The intent page supports S3: "Nothing blocks
  on me for multiple sessions, so you just work through the backlog"
  (ruled: Roman, 2026-10-18 02:35).
- [C12] A task that looks like it belongs to a fresh session is a frame on
  the stack for whoever holds it next. It is not a claim posted to a
  standby (ruled: Roman, 2026-09-20).
- [S4] The stack is linear. A frame that waits on another says which (no
  origin named).
- [C41, S9, merged] Every frame's first line names its site as a fixed
  field, `Site:`, the files or the seat it edits. Two frames that share a
  file are never held together: the second waits on the first's commit.
  Reads run side by side whatever their site (ruled: Roman, 2026-10-11
  05:51, "make sure that the meta workflow adopts these"). Tool: `map`
  checks a site.
- [C42, S9, merged] Every price line carries cycles beside tokens. A cycle
  is one agent's brief, its report, the status line and the stack commit,
  about 10k of the holding session's context. A door text or a number is 2
  cycles, an instrument fix 3, a seam design with its night 8 to 10, a
  count that closes on a night 0 (ruled: Roman, 2026-10-11 05:51; observed:
  frames 199 and 195, eleven cycles, 2026-10-11).
- [C31] **An ends-when on a seat's behaviour has three parts** (ruled:
  Roman, 2026-10-03, after frame 111's close waited on a question the read
  could have answered). First, the mechanism the seat meets. Second, a
  ratio with a baseline from the night that found the wall, never a zero.
  Third, the residue rule: a session that still shows the sign is read, and
  the frame closes when its cause is not the cause the frame named. That
  cause is a new frame.
- [C67, S5, merged] A frame is five lines: what, with its `Site:` field
  first, ends when, waits on, with the price in cycles beside tokens, a
  pointer to the reasoning, and a dated status (ruled: Roman, 2026-09-27,
  after frame 86's block reached 130 lines). S5 is the same rule twice, and
  adds the peer name in the status line, which C29 holds.
- [C46] **A push is a placement** (ruled: Roman, 2026-10-12 23:40, "update
  guidance to make pushing frames a prioritization operation also", after
  twenty-four frames sat unplaced). Place the frame in the same commit, on
  a `Sprint:` line after the `Waits on:` line: `this sprint, after frame
  <n>` when the frame is a wall of a held frame, or shares a held frame's
  site and costs under three cycles. Otherwise write `next sprint, rank
  <k>` among the parked, by the wall it closes and the cycles it costs. The
  placement is (reasoned) until Roman rules it at the sprint boundary.
  "Waits on: Roman's order" is not a line a frame carries.
- [C49] Two features wait on a night: implementers on branches with one
  merge queue, after frame 200's night shows whether the one-checkout rule
  bites, and a `handed` column that lists more than one frame (no origin
  named). This entry is a parked item and not a rule.

## 5. Briefing an agent

- [C37] Opus builds, Fable judges. An implementer or a sweeper runs on
  Opus, and the session that holds the frame is Fable (ruled: Roman,
  2026-09-24 01:07, on frame 74's count: Opus 5.5 found 8 of 10 findings
  blind).
- [C38] **Every agent runs on Opus again: a read of a night, a diff review,
  a design review, a history read, an implementer, a sweeper** (ruled:
  Roman, 2026-10-07 00:50, "Please switch back to opus for the relevant
  subagents"). Pass `model: "opus"` on each agent. Fable is this session
  alone. Memory `rota-agents-run-on-opus.md` holds the same rule.
- [C40, S10, merged] **A session holds up to three agents at once and
  about twenty cycles in all** (ruled: Roman, 2026-10-11 05:51, "make sure
  that the meta workflow adopts these", after "Yes, paralelise maximally"
  at 05:36). A sprint is cut at about twenty cycles: one seam design and
  three or four small frames. More than three agents at once buys nothing,
  because every report lands in the session's context when it arrives.
  This extends the ruling of 2026-09-24 20:04 that two frames run side by
  side when they touch different files. Memory `rota-frames-in-cycles.md`
  holds the same rule.
- [C43] Every agent writes its full report to the path its brief names,
  under `plans/` for a read or a review the records point to, and under the
  scratchpad for a pass report. It returns ten lines: the verdict, the
  counts, the paths. Read the file for the judgement cases only (ruled:
  Roman, 2026-10-11 05:51; observed: whole reports cost 10k to 15k a cycle,
  ten lines about 3k).
- [C52] Ask the map tool before you grep:
  `python -m rota.tools.map fn|table|mode|file <name>`. An agent's brief
  carries the same line (observed: git `128c68c9`, 2026-09-17). Tool: `map`.
  The map has no key for a ruling, a frame or a law: `rulings.py` holds
  those.
- [C50] A change that is the same edit in more than three files is a
  script. Write the script with the Write tool and run it. Print the
  touched files, and read the diff once for the judgement cases (no origin
  named). Tool: `sweep`.
- [C50, the agent's part] An agent starts a sub-agent only when its brief
  allows it. The brief gives the sub-agent a token cap, and the agent's
  report carries the sub-agent's usage (no origin named).
- [M20] A synthesis runs in two levels: blind capped extractors to files,
  then one synthesiser that writes the page. The session judges the page
  and never the sources. Synthesis, not summary, and do not fit new input
  to existing rulings (ruled: Roman, 2026-09-16, "You are too influenced by
  me", memory `rota-low-frequency-method.md`; ruled: Roman, 2026-10-18
  02:35, "super important").
- [M11] Brief a re-record or orchestrating agent to wait for its children
  in the foreground. An agent that backgrounds its children ends its turn
  with no result, and their notices reach the holding session. Resume it
  by message to finish (observed: frame 18, 2026-09-16; 2 strikes by
  2026-10-18, memory `rota-loop-agents-wait-in-foreground.md`).
- [M10] Read an agent's token cost from the harness usage line, never from
  the agent's own estimate (observed: memory
  `rota-agent-usage-from-harness.md`, 2026-09-17).
- [M4] Re-records are cheap. Run them without asking. Never call a case
  fixed without re-earning it, and classify stale with the gate first
  (observed: memory `rota-rerecords-are-cheap.md`, 2026-09-20). Tool:
  `gate`.
- [M5] A probe that composes cassette keys outside pytest sets
  `samplerepo.GIT_ENV` first, or every Developer case that commits reads as
  a false miss (observed: frame 70 built a repair for nothing, memory
  `rota-probes-pin-git-env.md`, 2026-09-23).
- [M19] Make phase-optimised development plans without being asked:
  measure where a night's time goes, snapshot at the tested boundary, and
  re-record by exact id (ruled: Roman, 2026-09-14, memory
  `rota-iteration-speed.md`).

## 6. A pass and its review

- [C39] One implementing agent per frame. Resume it by message for each
  pass. The resume carries the tree's delta since its last pass and a
  required re-read of the files it edits. The writer never reviews its own
  diff. Near 350k, the agent writes a where-things-are note and a fresh
  agent takes the next pass. Write each pass's tokens in the status line
  beside the cold cost, about 300k a pass. If a resumed pass costs as much,
  the rule stops (no origin named).
- [C32, C33, the loop] In a loop, you diagnose and write the fix brief. An agent
  implements, re-records the touched cases, and returns the diff and the
  result. You review from a context that never read the files (no origin
  named). A one-line door is the exception.
- [C53] A design review reads the scope report and the design record
  before any code, about 100k. One read-only diff review runs after every
  pass, whatever the pass touches, on a worktree at the pass's commit, and
  the last one runs before the walk (ruled: Roman, 2026-09-27, after frame
  86's four reviews each found a defect the previous pass left; the
  narrower line was declined). Fewer, sharper points per review. Memory
  `rota-review-worktree-pattern.md` holds the observation behind it
  (observed: frame 21, 2026-09-16).
- [C53, the judging part] This session judges a design before any code. It
  judges by working back from the output: the gate on the commit, the
  findings against the known ones, spot reads of hunks. It reads the output
  in full, never the agent's reasoning (no origin named).
- [C51, the agent's part] An agent runs the touched test files first, and
  the gate once at the end of a pass: `python -m rota.tools.gate` (no
  origin named). Tool: `gate`.
- [C54] A frame that touches the seats, the briefs, the write pipeline or
  a predicate ends on a walk. The walk covers the phases the frame touched:
  onboarding for an onboarding change, a full night for the delivery path
  or when in doubt. The walk runs from a worktree at the frame's closing
  commit, because the seats read the briefs at every wake. The frame stays
  open as validating while the next frame starts in the main checkout (no
  origin named).

## 7. The gate and the commit

- [C51] Run the gate yourself before a commit and read its five lines,
  never the log. The stale line is part of every acceptance (no origin
  named). Tool: `gate`.
- [M2] Never pipe the gate through `tail` or `head`. Run it in the
  background unpiped and read the last lines of the task output (observed:
  2 strikes by 2026-09-24, memory `rota-gate-five-lines-unpiped.md`).
- [C45, M3] **One checkout.** Implementers edit one at a time in the
  checkout, and the gate and the commit stay one at a time, because the
  frames share one tree (ruled: Roman, 2026-10-11 05:51). The acceptance
  gate runs from a worktree at the commit while an implementer edits the
  checkout, with the checkout's `.rota-gate.json` and register copied in,
  or `new reds (0)` means nothing (observed: 2 strikes by 2026-10-12,
  memory `rota-gate-from-a-worktree.md`).
  The copy goes from the newer register to the older, by `max(at)` of
  `case_runs`: a gate worktree that re-recorded holds the newer one, and a
  copy from the checkout over it erased a day's re-records (observed: 1
  strike, 2026-10-24, `plans/operating-facts.md`, the gate section).
- [M6] Never `cp` over the checkout's `cassettes.db` under a running gate:
  the copy cuts it at 1 GiB. Never filter processes on a word in the
  session's own command line, because the filter kills the session's shell
  (observed: 1 strike each, 2026-10-12, memory
  `rota-never-copy-over-a-busy-register.md`).
- [M1] Write a patch that carries a backslash through the Write or Edit
  tool, never through a bash heredoc. Quote the EOF of every heredoc,
  because an unquoted heredoc runs backticks as commands. `Path.write_text`
  turns LF into CRLF on Windows, so check CR presence in the bytes after any
  scripted edit (observed: 27 strikes by 2026-09-30, memory
  `heredoc-backslash-corruption.md`). Tool: `sweep` for a many-file edit,
  and `status` for a status line.
- [C74] Commit messages follow `CONTRIBUTING.md`: Conventional Commits,
  `type(scope): summary` with a prose body, and no author or co-author
  footer, whatever a harness reminder says (observed: 1 strike 2026-10-09,
  memory `rota-no-coauthor-footer.md`). The rule stays in `CLAUDE.md`,
  section 3.
- [C71] Commit the stack alone after every change (no origin named). Tool:
  `status` commits the stack by pathspec.

## 8. A status line

- [S2] Write the status line with the date at every change and before any
  compaction (ruled: Roman, 2026-09-14). Tool: `status`.
- [C68] The status line's time comes from the clock, never from memory. A
  ruling time comes from the clock when the answer is read, not when the
  question was asked (observed: 15 strikes by 2026-10-15, memory
  `rota-status-time-from-clock.md`). Tool: `status`, the rule leaves this
  page when the tool is proven. `status --ruling` writes Roman's words at
  the frame with `--at`.
- [C67, the status part] A status line carries the numbers and the
  verdict, and the reasoning goes to a record file the pointer names (ruled:
  Roman, 2026-09-27, after frame 86's block reached 130 lines).
- [C69, C70] A frame that measures something writes one line in the
  register the measurement belongs to. A failure that cost a retry, and
  that the next session would meet the same way, becomes one line in the
  tool's section of `plans/operating-facts.md`, keyed by the error text
  verbatim, because the next session greps the sign and not the moral. A
  failure that teaches a habit of the assistant goes to memory as feedback,
  with a strike count. A one-off miss is not recorded. The closing status
  names the count of register lines the frame wrote (proposed: the
  assistant, 2026-09-23; checked with Roman in the terminal). After this
  sweep, a rota habit goes to this page as an amendment, and memory keeps
  the cross-project ones (reasoned: `plans/method/design.md`, section 3).
- [C42, the close] The closing status writes the actual cycles and tokens
  beside the estimate (ruled: Roman, 2026-10-11 05:51).
- [Assumed] A decision taken for Roman while he is away carries
  (assumed: why) in its status line, so `state --since` finds it
  (reasoned: the session, 2026-10-18, step 5's review found no findable
  assumption in 229 status lines). Tool: `state --since`.
- [C71, S6, merged] Closed frames leave the file. A popped frame moves
  verbatim to `plans/archive/stack-<date>.md` (no origin named). S6 and
  C71 are the same rule twice.
- [C72] Never edit another session's frame, except to add a waits-on line
  (no origin named).

## 9. A night: its launch, its cycle lines, its stop and its read

- [C44, S10] **The night is the hand-off boundary.** The session that
  launches a design frame's night writes the momentum note and hands off
  once every other held frame is at a commit, whatever its count. A night
  is hours on the GPU, and the read after it is the frame's largest cycle,
  so the standby's clean context takes it. This is the one hand-off below
  the hand line that the hand line allows (ruled: Roman, 2026-10-11 05:51).
  The old text says "below 400k". The hand line is now 350k.
- [M12] During a night, read a CYCLE line at once, not at the night's end:
  the failing sessions' turns, calls, commits and count. Push the frame
  while the night runs (ruled: Roman, 2026-09-29, night 96, memory
  `rota-check-a-cycle-when-it-fires.md`).
- [C55] **A night is stopped when its loop is a known open frame's wall and
  the held frame gets no new data from it** (ruled: Roman, 2026-10-09
  20:19, "ok so in the future we need to do the same", after night 137's
  walk 3 looped on frame 186's wall). At every CYCLE line, name the frame
  the cycle belongs to. When that frame is not the held one and the walks
  before gave the held frame's ratios their shape, say the three facts to
  Roman in one line, stop the night, copy the records to their night names,
  and start the read. Memory `rota-stop-a-night-that-measures-nothing.md`
  holds the same rule.
- [C56] **A loop on no held frame's site stops the night too**, read once
  at its first CYCLE line, and the read starts (taken by timeout:
  2026-10-16 07:23, rated low, after night 150's walk 2; reasoned:
  `plans/night150-read.md`, section 10).
- [C35] A door or a predicate carries its count on every night's records
  before its pass: fires on a of n instances, refuses b of N right calls
  (ruled: Roman, 2026-10-15, frame 251). Tool: `nightcount` prints the
  night's counters. It does not print a door's count.
- [M18] The night log's dollars for the Opus stand-in principal are a
  list-price estimate. Nothing is billed on Roman's subscription. Report
  asks and tokens, never cost (ruled: Roman, 2026-10-16, memory
  `rota-night-dollars-are-nominal.md`).
- [C46, the sprint end] A sprint ends at its design frame's night read. The
  session that reads the night crosses off the closed frames, moves the
  frames the night pushed into one order, and writes the order at the top
  of `plans/stack.md` as the next sprint with its date (ruled: Roman,
  2026-10-12 23:40).
- [C47] **The session picks the next night's wall itself** (ruled: Roman,
  2026-10-12 23:52, "debug planing is relatively intuitive as long as it
  doesn't open large questions that lead you to do autonomous
  investigations first"). Roman rules only when the order crosses his
  intent or the composition, or when a night's design would open a
  question large enough to need an investigation frame first.
- [C48] **The sprint order itself never pauses the session** (ruled:
  Roman, 2026-10-16 22:33, "Stop pausing for sprint orders, I will re
  prioritise if something changes"). Write the order, send one
  notification that names it and the next night's wall, and start row 1 at
  once, with no timer. Only the one question that C47 names waits on him.
  Memory `rota-sprint-order-never-pauses.md` holds the same rule.

## 10. A wall's placement and fix

- [C76] **An issue is read before it is fixed, and the read names no cause**
  (ruled: Roman, 2026-10-26 about 21:1x, "we need critical thinking and
  context retreival to solve problems", then "first evaluate the issue
  against unbuilt solutions / then do what you just did", then "yes
  update", after fourteen frames read that way fixed 0 of 14 at the
  source, `plans/agency-prevalence-2026-10-26.md`). The moment, in order:
  1. Find: the turn, what the seat was shown and what it sent, verbatim.
  2. Match by symptom against the open and the parked frames, cheap, so
     no duplicate frame opens.
  3. Read, on one agent with a brief that names the turn and a question
     and no site or cause: the purpose of the mechanism and the ruling
     or build that made it, what the code already holds for the thing by
     file and line, the reach of the placed cause as a count of every
     place with the same gap, a proposal at the smallest place that
     covers the whole reach with a price, and the agent's doubt. The
     agent retrieves and proposes. The session judges. Roman rules a
     departure only. The cap fits the task, about 120k for a read.
  4. Match by cause, both ways. The issue against unbuilt solutions: one
     that covers it takes the issue as a count, and no frame opens. A
     built or proposed solution against open issues: every frame its one
     reader closes is named, and the stack shrinks.
  5. Re-read a solution that waited before its pass, because the code
     moved. Frame 334 waited six weeks on a question answered the week
     it was asked.
  6. Build at the reach. The pass brief carries the reach count. A fix
     that covers fewer places than the count says which it leaves and
     why.
  7. Close on two counts: the reach reads one reader, and the night's
     count moved. One without the other is a residue line.
  No tool refuses for it. The session writes the reach line before any
  pass, and `state` prints it. Frame 340 built two refusals in the status
  tool and took them out again (ruled: Roman, 2026-10-26 about 22:5x, "No
  don't make it a hard rule, the model should be smart enough to do it").
  The read agent, not the session, writes the count where a read ran. C64's
  provenance read is step 3's second question and keeps its own entry.
  Memory `rota-read-before-fix.md` holds the same rule.
- [C32] In a loop, a cause goes on the stack only after the turns of the
  failing sessions are read: what each seat called, what came back, what it
  committed. What you changed that day is the last suspect (no origin
  named). The rule recurred: the guide's placements read no turn (observed:
  `plans/wall-guide.md` line 818, 2026-10-15).
- [C34] **A wall's fix is decided from `plans/wall-guide.md`** (ruled:
  Roman, 2026-10-15, "Yes rule it", frame 251). After a night's read, place
  each wall under one of the guide's causes by the questions of its section
  4, in order, and stop at the first answer that places it. A fix is cheap
  or it goes to Roman (ruled: Roman, 2026-10-15, "for now there is only
  cheap and escalate to me"). Every wall a read names is fixed, cheaply or
  by escalation, and a wall not fixed now stays an open frame with its
  reason written (ruled: Roman, 2026-10-15, "try to fix everything", then
  "Reasonably"). The guide's own rules stay in the guide.
- [C64] **Every new wall gets a provenance read before its first fix**
  (ruled: Roman, 2026-10-18 about 12:00, frame 298, "Spend the time to
  understand it before making fixes", then "Every new wall, before its
  first fix"). An agent reads which ruling made the mechanism, which build
  decision shaped it, on what date, by which workflow, and whether the
  build met the design's own condition, about one cycle, and writes it at
  the frame. The rule covers any inconsistency or issue with rota, not only
  a departure from a design. A build that departed from one of Roman's own
  rulings is still asked, and the question opens with why it is raised: the
  ruling, its date, and that the build departed from it, before the options
  (ruled: Roman, 2026-10-25 23:08, "still ask it, just make it more up front
  why its being raised", frame 328, after a question on the quote check of
  2026-08-26 read as a question he had answered). A wall that recurs under an open frame whose
  provenance is already written keeps the guide's cheap path. Frame 298's
  pointer line was a fallback of the 2026-09-03 design shipped on
  2026-09-12 before its condition was tested, and three questions reached
  Roman before anyone read that. Memory `rota-provenance-before-a-fix.md`.
- [C33, the interview] **When a seat has a fact in front of it and does not
  act on it, interview the model in its context before a second brief
  shape** (ruled: Roman, 2026-10-02 15:02, frame 110, after two brief
  shapes and a door moved nothing). An agent replays the seat's exact turn
  with `probes/frame37/interview_turn.py --seq <working turn>` and asks what
  the seat read, what it understood, and what would have moved it. The
  answers go verbatim to a record, and the fix is decided from what the
  model says. Memory `rota-interview-the-seat.md` holds the same rule.
- [C36] A seat that read the fact and judged against it is escalated only
  after the interview shows it on more than one sample (ruled: Roman,
  2026-10-15, "we have to be sure of it"). A placement from one replay
  never gates, and the night gates the close.

## 11. A question to Roman

- [C57] Escalate as a blocked frame: the question and a recommended answer.
  The triggers: a ruling is needed, a wall survives three cycles, a change
  touches the composition, or the budget is spent (no origin named).
- [C58] **Before a frame blocks on Roman, an agent reads the records for a
  prior ruling on the same question**: `LAWS.md`, `DECISIONS.md`,
  `plans/archive/`, `plans/operating-facts.md`, the briefs, and `git log
  -S` on the lines in question. The blocked frame cites what the history
  says and asks only what it leaves open (ruled: Roman, 2026-10-03, after
  frames 114 and 115 went to him as open questions). Tool: `rulings.py`
  searches by frame, file, door and law for the agent.
- [C59] **Before any question goes to Roman, new or inherited, an agent
  answers two things** (ruled: Roman, 2026-10-04 14:52, "yeah add it").
  First, what the records say: the design files, and the build sessions'
  transcripts for Roman's own words, in
  `C:\Users\roman\.claude\projects\d--repos-rota\*.jsonl`, by a keyword
  script. Second, whether the recommended answer holds against the evidence
  the frame cites. A question that the read dissolves is not asked. An
  inherited recommendation is a copied claim until this session's agent
  tests it. A grill on a goal he has discussed is an escalation too
  (observed: 5 strikes by 2026-10-17, memory
  `rota-history-before-escalation.md`). Tool: `rulings.py`.
- [C65] **A question to Roman opens with the provenance of the issue**
  (ruled: Roman, 2026-10-18 about 12:00, frame 298, "if there are any
  problems or questions to me, I need to know the provenance of the issue.
  And investigating it yourself may make the answer obvious"). The first
  lines say which ruling made the thing, which build decision shaped it,
  when, by which workflow, and what the records say about its condition.
  A provenance that shows a departure from the design is still asked, with
  the repair named, never repaired in silence (ruled: Roman, the same
  minute, "Ask me still"). Memory `rota-provenance-before-a-fix.md`.
- [M-claims] When Roman's words assert a state of the world, check the
  conversations, the code and the records before you act, and question him
  when they disagree (ruled: Roman, 2026-10-18 about 02:05, "if i say some
  bullshit i expect you to check shit like our conversations, whats
  implemented, whats documented etc and to question that", memory
  `rota-check-his-claims-first.md`). The intent page holds the same rule.
- [M-thoughts] A request for thoughts is not a request to act. Tell him,
  then wait for his word before an agent or a record moves (ruled: Roman,
  2026-10-18, memory `rota-thoughts-are-not-a-go.md`).
- [M16] After a re-scope, grill the purpose first: who reads the thing and
  which decision it eases. Confirm the value in your own words before an
  agent runs (ruled: Roman, 2026-10-15, "Do you know what the guide is
  for? Grill me", memory `rota-grill-purpose-before-content.md`; observed:
  strike 2, 2026-10-17 18:19).
- [M15] A ruling question starts from one concrete situation as a story,
  with everyday role names and today's behaviour. Then say what happens
  next under each option, with one exact analogy, and no identifiers or
  prices (ruled: Roman, 2026-09-24; observed: 3 strikes, memory
  `rota-grill-in-plain-words.md`).
- [C62] **Rate every question's impact as high, medium or low before you
  ask it, and write the rating beside the question** (ruled: Roman,
  2026-10-02, after a session waited idle 5 hours 18 minutes on two
  low-impact questions). Low means the answer sets an order, a number or a
  name, and no edit, GPU hour or composition line depends on it. Keep the
  same system (ruled: Roman, 2026-10-18 02:35, "keep the same high, med,
  low system").
- [C63] **Every notification and every question starts with the rating in
  brackets, `[high]`, `[med]` or `[low]`, as its first word** (ruled:
  Roman, 2026-10-02). In `AskUserQuestion` the prefix goes on the question
  text and on the header. A low question goes by `PushNotification` with
  the recommended answer and a 20-minute timer: arm a background
  `sleep 1200` with the Bash tool. On the wake with no reply, continue on
  the recommended answer and write "taken by timeout at <clock>" in the
  status line. A high or medium question goes by `AskUserQuestion` and
  waits. Never start the recommended work before the answer or the timeout.
  Memory `run-the-recommended-path-while-asking.md` holds the same rule.
- [C60] An escalation reaches Roman on his phone, because a decision must
  notify (ruled: Roman, 2026-09-20). Ask with `AskUserQuestion` when the
  answer is a choice between named options. Send one `PushNotification`
  that names the decision and your recommended answer when the escalation
  is a blocked frame in prose.
- [C61] Send one notification per stop, and never one per question. Do not
  notify for progress, and do not notify while Roman reads the terminal (no
  origin named).
- [Autonomy] Nothing blocks on him for sessions at a time. Decide the rest
  under a stated assumption, written where the decision is (ruled: Roman,
  2026-10-18 02:33; reasoned: `plans/method/design.md`, section 2).

## 12. The hand-off

The three warnings, 200k, 300k and 350k, stay in `CLAUDE.md`, section 1
[C2, C3, C4]. The 300k and 350k rules are there with their rulings.

- [C5] **The order is the oldest free standby under a 300k ceiling**
  (ruled: Roman, 2026-09-20). Name a session with `--to <name>` only when
  Roman names one. Tool: `handover.py hand`, the rule leaves this page when
  the tool is proven.
- [C6] Act on the exit code of `hand` (no origin named). Tool:
  `handover.py hand` prints the case.
  - 0: a named session holds the frame. Write that session id in the status
    line. Stop when the taker messages released (reasoned:
    `plans/method/design.md` section 2, after Roman, 2026-10-18 02:20; the
    old text said "Stop.").
  - 4: the claim waits unread. Name that session in the status line, and
    say the take never came. The claim returns to the queue by itself, so
    the frame moves again without a person. Stop.
  - 5: no standby can take it. The hand-off now waits on disk for the next
    standby. Say in the status line that the frame is handed to nobody
    yet. Read the command's own output before you tell Roman why. An empty
    reserve and a reserve that is all past the ceiling are different facts,
    and they need different windows. Stop.
- [M9] "0 free standby" in the peers table means that nobody is armed, not
  that nobody is available. Name the enrolled-unarmed sessions, both
  numbers, before you ask Roman to open a window (observed: memory
  `reserve-empty-means-unarmed.md`).
- [C7] A message is never the first route and never the only route. A
  message cannot carry a session id, cannot prove it landed, and spends the
  clean context the standby holds. Use a message only when the command
  reports 4: message the peer name the command prints and tell it to run
  the take command. Believe the reply only when it names the session id you
  claimed (observed: the measurements in `plans/operating-facts.md`). The
  dialogue after the take is a different message, ruled at the take,
  section 2.
- [M8] Never pick a hand-off target from the harness peer list. The list
  spans every project on the machine and shows no working directory. Use
  `rota/tools/handover.py` (observed: memory `peer-list-is-machine-wide.md`).
- [C8] Never write in a record that messaging is broken. It is not. A
  prediction never gates (observed: one hand-off arrived four minutes late,
  no date).
- [C9] A hand-off is Roman's assignment, continued. Do not wait for Roman
  to name the peer (no origin named).
- [C10, the sender's part] **A hand-off carries a momentum note beside the
  status line** (ruled: Roman, 2026-10-09 01:09, "1 yes"). Write
  `plans/method/handoff-<your sid>.md`, one page, before the command: the
  reading at altitude, what the held frame is about in rota's terms, what
  you believe and why, what to doubt first, the live agents with their note
  paths, and Roman's last rulings in his words with their time. Not facts,
  which the stack holds. The note names the sender's peer name in its first
  line. A pointer to the transcript turns was declined as too noisy (ruled:
  Roman, the same minute). The note leaves the repository when the frame it
  carries closes. The path moved from `plans/handoff-<sid>.md` (reasoned:
  `plans/method/design.md`, section 2). Memory
  `rota-handoff-momentum-note.md` holds the same rule. Tool: `handover.py
  hand` checks the note.
- [C11] **A hand-off means you stop and the stack goes to one session**
  (ruled: Roman, 2026-09-20). Never use `hand` to give side work to a
  second worker while you keep running. One session holds the stack at a
  time, because two sessions on one stack write over each other's records
  (observed: 2026-09-20, two live sessions in one checkout, both wrote
  `plans/stack.md`). Memory `hand-off-means-stopping.md` holds the same
  rule.
- [C13, the reserve] A standby's clean context is reserved for taking over.
  The reserve exists to continue this seat, and not to widen it (ruled:
  Roman, 2026-09-20). The assignment part of C13 is in section 4.
- [C2, C4, memory] Memory `hand-off-never-idle.md` holds C2 and C4: past
  300k with no frame, hand off at once (ruled: Roman, 2026-09-30, "you
  should never be idle like this"; observed: strike 2, 2026-10-11, frame
  193).

## 13. The standby

The standby's steps stay in `CLAUDE.md`, "Standby duty", byte for byte
[C14 to C23]. This section holds only what that section does not.

- [C14, C15, C16, C17, C19, C20, C21, C23] Arm one watcher with `handover.py standby --sid <sid>`, on
  one line, with no name, in the background with a `timeout` of 86400000.
  Prove the arm with `peers`. Act on the exits 0, 3, 1 and 2. Correct the
  `handed` column with `holding`. Never spend a standby's context. The
  origins: a typed description (observed: git `f06ffbf8`, 2026-09-20), the
  harness kill at two hours (observed: git `78259764`, 2026-10-02), a
  standby that went from 20k to 152k (observed: 2026-09-20). Tool:
  `handover.py standby` refuses at 300k and enforces one watcher [C18,
  C22], so those two steps leave when the tool is proven.
- [M7] After a hand-off, `holding --frame none` leaves a row that the
  standby arm reads as a held frame, "holds frame None". Run `release`
  before you arm again (observed: 1 strike 2026-10-16, memory
  `rota-release-before-rearm.md`). Tool: `handover.py release`.
