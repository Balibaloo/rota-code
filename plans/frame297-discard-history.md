# Frame 297, the history read: does a session's end discard its uncommitted writes?

Read-only agent on Opus, 2026-10-18, for session c32575f3, brief
`f297_history_brief.md` in that session's scratchpad. Meta workflow for this
read. Rota workflow for the records read.

## Result

**A ruling of Roman exists, and it chooses commit or discard, not
disclosure.** On 2026-09-16 Roman ratified the composition with the Records
line "A session commits or discards before it ends, so its output stays
attributable", ruled "The clean-workspace rule returns", and ruled the twelve
LAWS rewordings fine, P12 among them. P12 is law 4's paragraph "A worktree with
uncommitted changes at session end is a fault. The uncommitted change never
existed" (observed: commit 9f8cbdf5, commit 9006a615, and
`plans/archive/placement-laws-2026-09-16.md:399-412`).

**No ruling chose disclosure.** Frame 150's ends-when "or says that the tree
holds an uncommitted write" is the reasoning of session c81b16d3 (rota-5d) on
2026-10-05. Roman wrote no word in that session after 11:07 UTC, and the frame
was pushed at 14:57 local (observed: the transcript of c81b16d3).

**Frame 283's cross-session note route is a session's judgement, not a
ruling.** Session 0e37e9d7 (rota-7d) took review 1's finding 6 at 17:37 on
2026-10-17 and fixed it by a `drop_notes` table per batch and path. The
finding and the fix both assume that the write survives the session
(observed: `plans/frame283-review-1.md:23`, the stack, frame 283, 17:37 and
17:45).

**The repair conforms to the ruling, with one correction.** Discard every
uncommitted write at the session's end, whether or not a commit landed earlier
in that session. The repair as briefed discards only when no commit landed,
and law 4 names the tree's state at the end, not the commit count (reasoned:
`rota/LAWS.md:169-171`).

Rating of the question for Roman: **low**. The reason is in section 5.

## 1. Which ruling or design chose disclosure over discard

### 1.1 The ruling that exists: commit or discard

- The composition was committed on 2026-09-16 02:40 with the Records line "A
  session commits or discards before it ends, so its output stays
  attributable" and the Open line "Roman ruled on 2026-09-16: ... The
  clean-workspace rule returns" (observed: `git show 9f8cbdf5`,
  `plans/composition.md:64-65` and `:120-124`). The page was ratified by Roman
  the same day (ruled: Roman, 2026-09-16, the composition's header and
  CLAUDE.md).
- The same commit listed for LAWS: "The clean-workspace rule is missing"
  (observed: `git show 9f8cbdf5`, the Open section).
- The assistant of that session added P12 to the placement report at 03:22.
  The wording is the page's Records line, and the report says "The assistant
  reads the page line as the content" (observed: commit de60f675,
  `plans/archive/placement-laws-2026-09-16.md:399-412`).
- Commit 9006a615 at 10:48 says: "Roman ruled 2026-09-16 that the twelve
  rewordings in plans/archive/placement-laws-2026-09-16.md are fine. Ten land
  here: P1 to P8, P11 and P12. ... Law 4 gains the clean-workspace rule: a
  session commits or discards before it ends." (observed: `git show -s
  9006a615`). Frame 18 required "Roman rules on a change to LAWS before it
  lands" (observed: `plans/archive/stack-2026-09-16.md:533-545`).
- Roman's own words of 2026-09-16 are not in a transcript. The earliest
  transcript in `C:/Users/roman/.claude/projects/d--repos-rota/` starts on
  2026-09-17 (observed: the first timestamps of the oldest files). So the
  ruling stands on the commit messages and the composition, not on a quote
  (reasoned: no other record holds his words of that day).
- The older text holds the same rule. LAWS law 9 and `rota/HANDOFF.md:137`
  say "Commit-first is what bounds the loss: an uncommitted change never
  existed" (observed: `rota/LAWS.md:259-263`, `rota/HANDOFF.md:130-137`). The
  Developer's prompt says "Your worktree survives preemption; uncommitted work
  does not. A commit bounds the loss" (observed:
  `rota/roles/prompts/developer/base.md:19-20`), and "An uncommitted change
  never existed" (observed: `rota/roles/prompts/developer/batch_start.md:33`).
  The code makes both prompt sentences false today (reasoned: section 1.3).

### 1.2 The disclosure line: a session's reasoning

- Frame 150 was pushed on 2026-10-05 14:57 by session c81b16d3, peer rota-5d,
  rota workflow. Its ends-when: "the wake shows the tree that the runs ran on,
  or says that the tree holds an uncommitted write, with one test on that
  state". Its line "Waits on: Roman's order" shows no order (observed:
  `plans/stack.md:1809-1816`).
- The source is `plans/night124-read.md`, wall 3, a read on Fable. The read
  describes the sign and names "Nearest frame: none exact". It proposes no
  disclosure (observed: `plans/night124-read.md:149`).
- Roman's lines in session c81b16d3 on 2026-10-05 end at 11:07 UTC, "Please
  switch to fable for the non-implementer subagents". None names frame 150, a
  worktree or a commit (observed: the keyword script over that transcript).
- `plans/wall-guide.md`, cause 14, quotes the ends-when as "(reasoned: frame
  150's ends-when, 2026-10-05)". The same entry says "Overfits. A door on the
  wake's text. The fault is the tree, not the wake", "Not now, when. Never. The
  composition's sentence is absolute", and "Escalate. Never. The
  clean-workspace rule returned on 2026-09-16 for this sentence (ruled: Roman,
  2026-09-16, the composition, Open)" (observed: `plans/wall-guide.md:604-625`).
  So the guide itself reads disclosure as the overfit and the tree as the
  fault (reasoned: the entry's own lines).
- Frame 150 stays open and unread. The guide says "Cause 14 on frame 150, open
  and unread" (observed: `plans/wall-guide.md:861-862`). Nights 125 and 126
  counted 0 refused commits for it (observed: `plans/night125-read.md:247`,
  `plans/night126-read.md:229`). Night 138's s147 met the shape again
  (observed: `plans/stack.md:1496`, frame 194).

### 1.3 The code today

- No function in `rota/core/runner.py`, `lifecycle.py`, `loop.py`,
  `worktrees.py`, `boot.py`, `sandbox.py` or `scheduler.py` resets, restores,
  cleans or stashes a worktree (observed: a grep for `--hard`, `reset`,
  `restore`, `stash`, `clean` and `discard` over `rota/`). No commit in the
  history added such a call (observed: `git log -S'"--hard"' -- rota/`, empty).
- The Developer has no discard tool. The `code.*` names in
  `rota/roles/api.py` are `code.write`, `code.commit`, `code.diff`,
  `code.source` and `code.probe` (observed: a grep for `code.discard`,
  `code.reset` and `code.restore`, empty). So "commits or discards" cannot be
  done by the seat. Only the runner can discard (reasoned: the grep).
- Within a session the law is applied as a disclosure: `code.diff` returns
  `not committed` and `lands with: code.commit`, through `_uncommitted` at
  `rota/roles/api.py:14009-14018`, which excludes the batch's materialised test
  files as furniture (observed). That disclosure is right inside a session,
  because the session has not ended (reasoned: law 4's sentence names the
  end).
- `worktrees.batch_files` counts uncommitted files as the batch's diff
  (observed: `rota/core/worktrees.py:225-245`). So a reader of the batch's
  files sees a dead session's write as the batch's work (reasoned: the
  function's union with `changed_since(wt, None)`).
- `lifecycle.defer` says "The worktree and its commits survive — commit-first
  is what bounds the loss, because an uncommitted change never existed"
  (observed: `rota/core/lifecycle.py:140-146`). It discards nothing either.

## 2. Did frame 283 decide on purpose that a note and its write live across sessions?

**Yes, on purpose, and by a session, not by Roman.** The decision follows a
review's finding, and the finding takes the surviving write as a given fact,
not as a fault.

- Pass 1, 2026-10-17 16:41, session 0e37e9d7 (rota-7d): "a `dropped` note
  belongs to the session and the path" (observed: the stack, frame 283, status
  16:41).
- Review 1, finding 6, high, PLAUSIBLE: "outside: the session boundary,
  `rota/core/sandbox.py:717` ... The noted text stays uncommitted in the batch
  worktree when the session ends. A retry session on the same batch starts with
  no open note. Its commit lands the removal with no note, which is s388's
  shape across a session. Fix: persist the open note per batch and path, or
  read the worktree diff at the first commit of a session" (observed:
  `plans/frame283-review-1.md:23`). Neither fix discards the write (observed:
  the same line).
- The judgement, status 17:37, session 0e37e9d7: "Judged here: every finding
  is fixed in one pass" (observed: the stack, frame 283, 17:37).
- Pass 2, status 17:45: "a `drop_notes` table per batch and path in
  `schema.sql`, staged through `ctx.writes` and landed by the session's commit,
  so a retry session sees an open note" (observed: the stack, frame 283,
  17:45).
- Review 2, low 4: "A session that dies after a noted write leaves the dropped
  text uncommitted and no `drop_notes` row. The retry session commits the
  removal with no note, which is review 1's F6 shape" (observed:
  `plans/frame283-review-2.md:19`). Pass 4b answered that `session_fail` lands
  no staged row, "so `_put_note` says so" (observed: the stack, frame 283,
  18:13).
- No review of 1 to 7 and no line of `plans/frame283-count.md` names law 4,
  "discard" or "never existed" (observed: a grep of the eight files). The count
  says "The door's notes outlive a session within a batch. ... A retry session
  that commits under an earlier session's note is not counted" (observed:
  `plans/frame283-count.md:110-112`).
- The test `test_a_second_session_on_the_worktree_sees_the_note` cites "Frame
  283's review 1, finding 6" and builds a second sandbox on the same tree with
  the first session's write still in it (observed:
  `tests/rota/test_frame140_commit_beside_note.py:447-465`).
- Roman's words in session 0e37e9d7 near the build: at 15:50 UTC, "File writes
  were always permitted everywhere, just that if there were unexpected changes
  then the architect is required to sign off" (observed: the transcript, and
  `plans/frame287-roman-words.md:594-596`). The words answer a question on
  restoring a definition the batch's commits changed. They say nothing on a
  write that outlives its session (reasoned: the situation line of #621).

## 3. Roman's own words

- `python -m rota.tools.rulings` for "law 4", "discard", "uncommitted",
  "commit or discard" and "uncommitted write" returns law 4, law 9, P9 and P12
  of the placement report, frame 18 and the developer prompts. It returns no
  ruling that keeps an uncommitted write across a session (observed: the five
  queries). `rota/tools/rulings.py --help` fails as a script with an
  `ImportError`, and the module form treats `--help` as a query (observed).
- A keyword script over the 107 transcripts, user lines only, for "discard",
  "uncommitted", "session end", "commit or discard", "never existed",
  "clean.workspace", "clean worktree" and "dirty" returns 0 lines (observed:
  `f297_kw.py` in session c32575f3's scratchpad). The script returns his known
  line "Ok, and are we not over fitting?" (4754aaec, 2026-10-15 00:47 UTC), so
  it reads his lines (observed).
- A wider search for "commit", "worktree", "clean" and "workspace" returns
  standby instructions and "1 is a risk, what are the clean solutions?"
  (41cb5184, 2026-09-22 19:06 UTC). None is about a worktree at a session's
  end (observed: the same script).
- `rota/DECISIONS.md:144-148`, "Git: do not rebase mid-batch", says "Move the
  base and the judgement describes code that never existed" (observed). It is
  about the base, not the tree.
- `plans/operating-facts.md` holds no line on a session's uncommitted write
  (observed: a grep for "uncommitted", "discard" and "worktree"; the hits are
  the night restore steps and a 2026-09-13 failure).
- So Roman's words on the matter are the 2026-09-16 ruling of section 1.1,
  known through the commit messages and the composition (reasoned: sections
  1.1 and 3).

## 4. The repair against the evidence

The repair: at a Developer session's end, the runner discards the session's
uncommitted writes to the batch's worktree, the furniture test files excluded.
The runner writes the fact to its account and to the next wake's detail. The
runner closes the open dropped notes of those paths.

### 4.1 One correction and two extensions

- **Discard at every end, not only at an end with no commit.** A session that
  commits once and then writes again ends with an uncommitted write. Law 4
  calls that tree a fault (reasoned: `rota/LAWS.md:169-171`). The step is
  "discard `_uncommitted(...)` at the end", whatever the commit count.
- **The failed session too.** The `except` path of `run_session` at about
  `rota/core/runner.py:5359` ends a session as surely as a normal end. Review 2,
  low 4, is this case (reasoned: `plans/frame283-review-2.md:19`).
- **A runner that dies.** A process crash ends no session in code. Boot
  reconciles heads already (`boot.reconcile_worktrees`, law 4's carve-out), so
  boot is the place to discard a tree that differs from the head with no live
  session (reasoned: `rota/LAWS.md:155-162`).

### 4.2 s215 on night 156

- Today: s215, the second batch-start attempt on bg_2, met s214's open note at
  its first commit, before it wrote anything, and logged `l_8c98565350`, a
  removal note for a write it did not make. Its commits were refused to the
  session's end (observed: `plans/frame297-provenance.md`, sections 1 and 4).
- Under the repair: s214's end discards its write of `src/click/decorators.py`
  and closes its note. s215 starts on the head, with no open note. Its wake
  says that the last session's write to the path was discarded. s215 writes
  only for itself, and any note it logs is about its own write (reasoned: the
  repair's steps).
- s214's own note `l_cab4458639` is not touched. It was written inside s214,
  before the end (reasoned: provenance, section 1, seq 24). That case stays
  with the ledger door of provenance section 5.

### 4.3 Frame 283's cross-session route and the test at line 447

- The route loses its cross-session job. A note can outlive its session only
  while the write it names outlives it. After the discard, the dropped lines
  are back on the head, so the note has nothing to hold (reasoned: the note's
  meaning, "lines your write removed").
- The `drop_notes` table keeps its job inside a session. A note stays open
  across replies until a write puts the lines back or a ledger names them
  (observed: the stack, frame 283, 17:30 and 18:27). That is frame 283's
  validated mechanism, and the repair does not touch it (reasoned: the repair
  acts only at the end).
- The test at line 447 tests a state the repair forbids. Its first session
  "ends" with the write in the tree, and its second sandbox commits on that
  tree (observed: lines 450-465). The test still passes as written, because
  it calls no end step (reasoned: it builds `sb2` with `build(...)` and runs no
  runner). Its premise is false under the repair. Rewrite it so that the
  runner's end discards the write, closes the row, and the second session's
  `code.commit` on the clean head returns `committed: False` (reasoned: the
  repair's steps).
- Frame 283's count on nights 140 to 156 is unchanged in its numbers, because
  it counted notes and commits in one session (observed:
  `plans/frame283-count.md:110-112`). Night 156's ratio for frame 283 included
  s215, whose refusals came from s214's note (reasoned: provenance, section 4,
  the (b) row). A validating night after the repair has no such inherited
  refusal, so frame 283's ratio reads its own sessions only (reasoned).

### 4.4 Frame 150's disclosure

- The repair meets frame 150's ends-when by its first branch, "the wake shows
  the tree that the runs ran on". After the discard, the tree is the head, and
  the head is what the harness ran (reasoned: `plans/stack.md:1812`).
- The repair keeps a disclosure, but of a different fact: "your last
  session's write was discarded", not "the tree holds a write". The wake then
  tells the truth about a tree that is clean (reasoned: the repair's step 2).
- On night 124, s145 and s153 sent 29 `code.source` calls on a 705-line file
  beside red output that named line 708 (observed:
  `plans/night124-read.md:149`). Under the repair, the file is the head's file
  of 708 lines or more, and the red output matches it (reasoned: the head is
  what the runs ran on).
- Wall-guide cause 14 can then name the repair as its cheap fix and cite the
  2026-09-16 ruling (reasoned: `plans/wall-guide.md:617-624`).

### 4.5 The three batch-start attempts of a quarantine

- Today: the attempts share one tree. On night 156, s215 and s216 started in
  s214's dirty tree, and the batch was quarantined at 3 attempts and abandoned
  at m125 (observed: the stack, frame 283, status 2026-10-18 06:09). So
  attempts 2 and 3 were not retries of the batch start. They were repairs of
  s214's write (reasoned: provenance, section 1, the s215 fact).
- Under the repair: each attempt starts on the batch's head. The count of 3
  means 3 tries of the same wake on the same tree, which is what law 4's
  "Failure is bounded" counts (reasoned: `rota/LAWS.md:164-167`,
  `message_attempt_cap` at `rota/core/config.py:86`).
- The cost: an attempt that wrote a right fix and did not commit loses it. The
  runner's comment records one such case: "a session that diagnosed a real
  pytest failure correctly and wrote a fully correct fix ended on the write
  alone, before `code.commit`" (observed: `rota/core/runner.py:5114-5119`). The
  fix of that case was to keep the session running until it decides, not to
  carry the write (observed: the same comment). The prompt already tells the
  seat that uncommitted work does not survive (observed:
  `rota/roles/prompts/developer/base.md:19-20`).

### 4.6 Other readers

- `worktrees.batch_files` stops counting a dead session's write as the
  batch's diff (reasoned: section 1.3).
- The furniture rule must match `_uncommitted`: the paths in the `tests` table
  for the batch stay (observed: `rota/roles/api.py:14009-14018`). A Tester's
  materialised file is the harness's, so a Developer's end must not remove it
  (reasoned: the docstring).

### 4.7 Does a prior ruling settle it?

**Yes, in direction.** The ratified composition says the session commits or
discards, and law 4, ruled fine by Roman on 2026-09-16, says the uncommitted
change at the end is a fault and never existed (ruled: Roman, 2026-09-16,
section 1.1). Frame 150's disclosure and frame 283's cross-session route are
sessions' reasoning that departs from it (reasoned: sections 1.2 and 2). Two
details stay open in the records: who discards, because the seat has no tool
for it, and what the next wake says. Both follow from the ruling with no new
intent (reasoned: section 1.3).

By the rule of 2026-10-18, a provenance that shows a design departure is
still asked, with the repair named (ruled: Roman, 2026-10-18, M
rota-provenance-before-a-fix). So the question follows, as a confirmation.

## 5. The question for Roman

**How it came to be.** On 2026-09-16 you ruled that a session commits or
discards before it ends. The code never got the discard step. Two later
frames worked around the gap. Frame 150 planned to tell the next worker
about the left-over change. Frame 283 made its warnings outlive a worker so
that the next worker inherits them. No ruling of yours chose either.

**The story.** A builder works one shift on a shared bench. The builder cuts
out a piece of an existing part by mistake. The inspector refuses to sign the
part five times. The shift ends, and the cut part stays on the bench, unsigned.
The next builder arrives for the same job. The next builder finds the cut part
and the inspector's open warning. The next builder writes "I removed those
lines" to clear a warning about a cut that was not theirs. Then the second
builder's shift ends the same way, and so does the third. The job is given up
after three shifts.

**What happens next, option A, recommended: the bench is cleared at the end of
each shift.** The foreman puts the part back to its last signed state. The
foreman writes "the last shift's unsigned work was thrown away" in the log, and
the next builder reads that note first. The next builder starts from the signed
part, with no warning that is not theirs. Unsigned work from a shift is lost,
and the builder is told to sign as they go, which the builder's instructions
already say.

**Option B: the bench keeps the unsigned work, and the next builder is told.**
The next builder inherits the cut part and the warning, and must judge work
they did not do. This is today's behaviour plus a note. The records show it
cost night 156's batch three shifts.

**The analogy.** A shared lab notebook where only signed pages count. At the
end of the day, unsigned pencil notes are erased, and the erasure is logged.
The next person reads only signed pages and the log line.

**Recommended answer: option A**, as your 2026-09-16 ruling says. The runner
discards every unsigned change at a shift's end, a failed shift and a crashed
runner included, and closes the warnings on those parts.

**Rating: low.** The reason: your ratified composition and law 4 already
choose option A. The question confirms a departure and asks for no new intent.
The repair is one runner step and one boot step, and a revert removes it.
