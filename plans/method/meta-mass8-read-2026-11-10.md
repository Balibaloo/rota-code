# Mass 8: how the way of working changes itself, a blind read

Meta workflow. Read-only, 2026-11-10. The read used the reference page, the
brief, the memory directory, the stack and its archives, the frame 287
pages and git history. It did not read the meta review, the meta map or the
mass 3 read.

## Result

1. The way of working learns by writing text, and text alone rarely changes
   later work. Of 12 dated lessons, 5 changed later work and 7 did not.
2. A tool that does the step changed later work in 3 of 3 cases, for the
   part the tool covers. A memory or a rule text changed later work in 1 of
   8 cases, and that one change reverted when the memory was archived.
3. Roman starts most changes. He started 22 of 33 dated changes, the session
   started 10, and Roman's general word plus the session's reasoning started
   1. No agent finding started a change, but agents measured the two largest.
4. Nothing measures whether a rule is used or true. Roman ruled the purpose
   of the method on 2026-10-17 18:19: "nothing measurable, we stay aware of
   all relevant points previously discussed without clutter". Two one-time
   reads measured rules: 18 of 118 rules failed again after the rule
   (2026-10-17), and 0 of 14 fixes reached the source (2026-10-26).
5. Retirement happened once, in frame 287, on 2026-10-18. Since then the
   reference page only grows: 99 entries and 600 lines at the sweep, 104
   entries and 725 lines now.
6. The main doubt: a strike count measures noticing, not failure. One rule
   failed in 167 commits after its memory was archived, and no record
   noticed it.

## 1. The counts

### The reference page

`plans/method/reference.md` holds 104 entries in 13 moments (observed: a
parse of the `- [tag]` lines, 2026-11-10). An entry can carry more than one
mark.

Marks in the entries: ruled 57, observed 26, no origin named 25, reasoned
10, adopted from the kit 2, no mark found 1. By the first mark only: ruled 53, no origin named 25, observed 21,
reasoned 3, kit 1, none 1.

By the earliest date the entry cites: August 2, September 32, October 1 to
17: 36, October 18 to 31: 8, November 1, undated 25. The undated 25 are the
25 entries with "no origin named".

The largest moments are 10, a wall's placement and fix (111 lines), and 11,
a question to Roman (80 lines). Sections 5 and 11 hold 13 entries each, the
most of any moment.

### Growth of the files in lines

`CLAUDE.md`: 5 lines on 2026-09-04, 108 on 09-16, 321 on 09-20, 420 on
10-02, 584 on 10-16, 314 on 10-18 (frame 287), 323 on 10-31 and now.
`reference.md`: 600 on 10-18, 684 on 10-31, 725 now (observed: `git show`
at the last commit of each date). Brief plus reference: 939 lines on
10-18, 1,048 now. The growth moved to the reference page, about 4 lines a
day.

### Memory files

- Live: 20 files and the index `MEMORY.md` (19 lines, 4.6 kB). Archived: 30
  files, all moved by frame 287 on 2026-10-18.
- 24 of 50 files carry a strike count. The counts sum to about 86.
- Two habits hold 51 of the 86 strikes: the backslash patch, 30, and the
  status time, 15 in the archived memory plus 6 in its successor.
- 9 live memories were written after 2026-10-18, and 8 of them are rota
  habits. The live `reserve-empty-means-unarmed.md` is a 2-line fragment.

## 2. Twelve lessons and what happened next

"Repeat" means the same sign appears in a later record or a strike.

| # | What went wrong (date) | Form of the lesson | Repeat after the lesson? | Tool or hook, and did repeats stop? |
|---|---|---|---|---|
| 1 | Status times ahead of the clock (2026-09-23) | memory, rule C68 | yes, 15 strikes to 2026-10-15 | `status` tool, 2026-10-18, stamps the line. Prefix: no later strike found. Body: new memory 2026-10-23, 6 strikes to 2026-10-28 |
| 2 | Heredoc corrupts backslashes (before 2026-08-28) | memory, rule M1 | yes, 14 by 08-28, 27 by 09-30, 30 by 11-08 | `sweep` (09-17) and `status` (10-18) exist. Strike 30 was a status-line script written by hand. Not stopped |
| 3 | Co-author footer on commits (2026-10-09) | brief since 09-04, memory 10-09, rule C74 | see the commit counts below | none. Footers stopped while the memory lived, then came back |
| 4 | Questions sent to Roman that the records answered (2026-10-02) | memory, rules C58, C59 | yes, 4 strikes after, to 10-17 | `rulings.py` searches for the agent. Not stopped: the same sign returns in rows 5 to 8 |
| 5 | Walls fixed before their cause was read (2026-10-18, frame 298) | rule C64, memory | yes, frames 322 to 339 fixed 0 of 14 at the source | none |
| 6 | Fixes cover a median 2 of their reach (2026-10-26) | rule C76, memory | form changed, see section 7 | `state` reads the `Reach:` line. A refusal was built and ruled out the same evening |
| 7 | Questions to Roman in identifiers (2026-09-24) | memory, rule M15 | yes, two empty notifications on 10-24, a new memory with 2 strikes | none |
| 8 | An inherited "waits on" line taken as fact (2026-10-12) | memory strike, rule C65 | yes, 10-25, a 58k repeat read, a new memory | none |
| 9 | A register copy cut at 1 GiB (2026-10-12) | memory, rules M6, C45 | yes, 10-24, a copy erased a day's re-records | none. The rule text grew |
| 10 | The sprint order written at a night's read (2026-10-12) | rule C46 only | the rule stopped firing: 8 dry runs wrote no order | none. Found 2026-11-10, amended in the same hour |
| 11 | A frame number with no name (2026-09-21, 10-02) | rule C68 with S7, memory | form: see below | `status` writes "frame N, " and the first 8 words. Form changed, meaning not checked |
| 12 | A session idle past 300k (2026-09-30, 10-01) | brief in bold, memory, rule C2 | strike 2 on 10-11, none after | `handover.py hand`. Status lines cite "the idle rule" from 10-26 to 11-02 |

### The commit counts behind rows 3 and 11

Row 3, commits with a `Co-Authored-By` trailer (observed: `git log --all`
with `%(trailers)`):

September, 542 of 1,543. From 2026-10-10 to 10-22, with the memory live,
0 of 1,194. From 10-23 to 11-04, with the memory archived, 167 of about
2,600. From 11-05 to 11-10, 0 of 330. The brief held the rule the whole time. No line in the stack names the 167
footers. The cause of the stop on 2026-11-05 is not in the records.

Row 11, commit subjects that name a frame in the form "frame N, words":
87 of 1,134 (8%) from 2026-10-02 to 10-17, and 1,848 of 2,142 (86%) from
2026-10-18. The `status` tool builds the subject from the first eight words
of the status body (`rota/tools/status.py`, `summary`). For example,
"frame 173, pass 1 built the restore" names a step, not the frame.

## 3. Which form changed later work

| Form | Cases | Changed later work |
|---|---|---|
| A tool that does the step | 1 (prefix), 11, 12 | 3 of 3, for the part the tool covers |
| A tool that prints, and a rule that names a written line | 6 | 1 of 1, the form of the frames |
| A memory with a rule text | 2, 3, 4, 5, 7, 8, 9 | 1 of 7 (row 3, while the memory lived) |
| A rule text only | 10 | 0 of 1, it stopped firing in silence |

Total: 5 of 12 changed later work, and 7 did not. The tool cases fail at
their edges. Row 1 moved the error from the prefix into the body. Row 2 has
a tool that the failing session did not use. Row 11 changed the shape of
the subject and not its content.

A lesson that fails again tends to come back under a new name, not as a
higher strike count. Rows 4, 5, 7 and 8 and the memories
`rota-general-solution-from-what-exists.md` and
`rota-one-step-then-compare.md` all record one sign: the session acts on a
first reading before it reads what exists. Before the sweep that sign had
one memory with 5 strikes. After the sweep it has six memories and two
rules, with about 8 strikes. The memory of 2026-11-10 names the pattern
itself: "This is the act-before-read pattern ... at the scale of a whole
sitting".

## 4. Removal, measurement and contradiction

### Removed, merged or retired

- Frame 287, 2026-10-18, started by Roman and built by the session: 30
  memories archived, 8 pairs of rules merged under one tag, and the brief
  cut from 584 to 314 lines. One rule retired outright, the clock memory,
  because the `status` tool took its step. A successor memory came back 5
  days later.
- After frame 287: Roman ruled out one hard refusal in `status` (commit
  6e3a442c) on 2026-10-26 at 22:5x: "No don't make it a hard rule". One
  amendment (d38cd276, 23:04) was reversed one minute later (4e0dfc8d,
  23:05) after Roman's words. No entry has left the reference page.
- 4 entries say "the rule leaves this page when the tool is proven". None
  left in 23 days, and no entry defines the proof.

### Measurement

- No tool or record counts whether a rule fires, is followed or is still
  true. Roman ruled that the method has no measure (2026-10-17 18:19).
- Strike counts on the reference page froze at the sweep. M1 says 27, and
  the memory says 30. C74 says 1 strike, and 167 commits followed.
- Two reads measured rules, both one-time: frame 287 read B (18 of 118
  recurred) and `plans/agency-prevalence-2026-10-26.md` (0 of 14 at the
  source). Roman asked for both.

### Rules that contradict each other or are not followed

1. The page head says a change is a proposed amendment until Roman rules.
   `plans/method/amendments.md` holds 4 entries, all from 2026-10-18, none
   ruled and none added since. C46 was amended on 2026-11-10 as (reasoned),
   direct on the page. Its review found 16 faults (memory
   `rota-one-step-then-compare.md`).
2. C69 and C70 say a rota habit goes to the page as an amendment after the
   sweep, and memory keeps the cross-project habits. 8 rota memories came
   after.
3. C10 says the momentum note leaves the repository when its frame closes.
   60 notes remain in `plans/method/`, 4,054 lines. The tool that was to
   delete them (`wake close`) was not built.
4. C60 says the notification names the decision and the recommended
   answer. Memory `rota-question-text-in-the-terminal.md` says the
   notification is a doorbell and carries only the frame.
5. Tags collide. Commit e451ccab (2026-10-18 12:03) gave the new
   provenance rules the tags C64 and C65, which already named the marks
   rule and the copied-claim rule. 17 tags appear twice on the page, most
   as planned splits.
6. C68 cites the retired clock memory and not its live successor. 9
   entries say "Memory X holds the same rule", and several of those
   memories are archived, so no session loads them.

## 5. Who starts a change

| Set | Roman's words | The session | Session under his general word | An agent |
|---|---|---|---|---|
| The 12 lessons of section 2 | 6 (rows 4, 5, 6, 7, 11, 12) | 5 (rows 1, 2, 3, 8, 9) | 1 (row 10) | 0 |
| Commits that changed a method page after 2026-10-18 | 9 | 3 (register copy, watcher cap, C46) | 0 | 0 |
| Memories written after 2026-10-18 | 7 | 2 (status time, waits-on line) | 0 | 0 |
| Total | 22 | 10 | 1 | 0 |

Roman's lessons come from his reaction to a result, as "are we doing
proper root cause analysis?". The session's lessons come from a mechanical
sign: a wrong byte, a wrong time, a lost register or a repeated read.
Lessons about judgement come from Roman only.

## 6. What a lesson costs the next session

A take reads these files now (observed: `wc`, 2026-11-10):

| Read | Lines | When |
|---|---|---|
| `CLAUDE.md` | 323 (16.0 kB, about 4k tokens) | every turn |
| `MEMORY.md` | 19 (4.6 kB) | every turn |
| `plans/composition.md` | 152 | the take |
| The take and first-reply moments | 56 | the take |
| The state print | 21 | the take |
| The sender's note | 68 on average, up to 177 | the take |
| Total | about 640 | |

Before the sweep, on 2026-10-16, the brief was 584 lines and 33.5 kB, the
index was 39 lines and 8.7 kB, and a take read the stack for 27k to 38k
tokens (observed: `plans/frame287-context-cost.md`). Frame 287 roughly
halved the every-turn load and removed the stack read. Each later lesson
adds text at a moment, not at the take. A session at a wall now reads
section 10, 111 lines, and C76 alone is about 50 lines of it. A lesson
costs nothing at the take and more at the moment it fires.

## 7. The opposite: a lesson that made later work better

The strongest case is rule C76, the read before a fix, 2026-10-26.

- Before: the 14 frames 322 to 339 fixed 0 of 14 at the source, and their
  fixes covered a median 2 of their reach.
- After: no frame popped before 2026-10-28 carries a `Reach:` line. 17 of
  34 frames popped from 2026-10-28 to 11-08 carry one. Most read full
  reach, as "10 of 10", "11 of 11" or "4 of 4" (observed: the archive
  stacks).

What was different: the rule came from a count over 14 cases, not from one
incident. The rule asks for one written line with a number, and the state
print reads that line. The next session can see whether the step ran.

The limit: the read agent writes the `Reach:` count, and nobody checks it.
On 2026-11-08 dry run 7 gave ten walls. Seven matched older frames, and the
two frames behind the biggest wall were a month old and never built (rule
C77). The fixes reach further, and the frames still wait.

The opposite case at full strength is row 3. A one-line memory stopped the
footer, which 35% of September commits carried, for 13 days. The same rule
kept only in the brief and the reference page let 167 footers through, and
no record noticed.

## 8. What the records do not show

- The transcripts were not read. Strikes that nobody wrote down are
  invisible, so every "no repeat" in section 2 is weak.
- The cause of each footer change: the harness reminder, the model, or the
  memory. The dates fit the memory. Nothing proves the link.
- Whether the status-time errors in the body stopped after 2026-10-28, and
  whether the `Reach:` counts are true. Nobody counts either.
- Whether a session reads the reference moment at its moment.
- The review pages `plans/f*-review-p*.md`, which can hold uncounted
  repeats, and why the 4 amendments of 2026-10-18 are still open.
