# Frame 244, review 1 of 51e6ff33

Read-only review on a worktree at 51e6ff33, and on a second worktree at the
parent f6e03017 for the red run. Both worktrees are removed. Run 2026-10-15,
14:05 to 14:32 local, by a meta-workflow agent on Opus. No sub-agent ran.

## Verdict

Accept with fixes. The runner builds shape E byte for byte on all five try
cases. The tests are red at the parent for the right reason. The fixes are
low, and two are counts for the night read, not edits.

## (a) The seven points

1. Match. The runner's render of s152 and s119 equals try 2's shape E user
   text byte for byte. The same holds for s235, s345 and s124. The HEAD
   annotate piece sits verbatim in the try's E system text.
2. Reach. The block renders on an inbound with a `touch` dict, truthy
   `principal_said`, and a `contest` verdict on a batch of `touch`. Only a
   batch relay to the Architect builds `touch`. A `revise` gets no block and
   keeps the words in the JSON. A criterion contest gets no block. Two
   contested batches give one merged grain list with no batch ids and one
   `he said:` line. That case is unmeasured (finding 3).
3. No reader loses the words. `run_session` reads `asked=` from the inbound
   dict, which keeps the key. The cockpit's `message_text` renders the same
   prompt, so the page shows the block. No tool in `rota/tools`,
   `rota/cockpit` or `probes` parses `principal_said` out of the rendered
   text. The brief still says "The words are `principal_said`", and the
   JSON no longer carries that key (finding 2).
4. The sentence is a brief line, so the door rule allows it. It reads as a
   definition, and "Keep the others" narrows a dispute to the phrase
   "nothing to do with". A path he rejects for another reason, such as "echo
   itself should not change", is kept on a literal read. In the measured
   cases `disputed_paths` already removes those paths, so the narrowing did
   not show (finding 4).
5. Tests pass. At the parent, two tests fail: the block is absent, and the
   brief lacks the sentence. The three no-contest cases pass at both commits
   and assert the old render byte for byte. CR count is 0 in all three files.
6. `L1-AR-re-annotate-from-the-principals-correction`: the reply did not
   change. All five live runs call `batches.annotate(<b1>,
   ["src/click/termui.py", "tests/test_termui.py"])`, as on 2026-10-09.
   `L1-AR-annotate-a-batch` has no block and moves on the sentence alone.
   Runs 2 and 4 changed their lists, and all five still pass.
7. The night read must count the right-call breaks on contest wakes whose
   block lists a file he kept. The block's list is `expected` after the
   `disputed` filter, so it can name only the files he accepted (finding 1).

## (b) Findings

1. `rota/core/runner.py:519-525`. Severity low. CONFIRMED. The header "he
   contested these files:" lists `expected` after `resolve_inbound` removed
   the disputed paths. In the re-recorded case the block lists only
   `src/click/termui.py`, the file he said "looks right". On night 147 s235
   it lists only `src/click/termui.py::confirm`, a file he keeps. On night
   146 s247 the list is empty. The seats kept those files in the try and in
   the case, at temperature 0 only. Fix: count kept-file drops on such wakes
   in the night read, and rename the header only if the count shows a drop.
2. `rota/roles/prompts/architect/annotate.md:17`. Severity low. CONFIRMED by
   reading. "The words are `principal_said`" points to a key that the
   contest render removes. The try kept the line, so the count covers it.
   Fix: leave the line for this frame, and name it in the night read if a
   seat asks for the key.
3. `rota/core/runner.py:519-524`. Severity low. PLAUSIBLE: no night held a
   relay with two contested batches. The block merges both grain lists with
   no batch id. Fix: prefix each grain group with its batch id when more
   than one batch is contested, or log the case as unmeasured.
4. `rota/roles/prompts/architect/annotate.md:19`. Severity low. PLAUSIBLE:
   the literal read keeps a path he declines for a reason other than
   irrelevance. The `disputed_paths` filter masks the risk in every
   measured case. Fix: none now. Count the kept-but-declined paths whose
   words are not "nothing to do with" in the night read.

Outside the points:

5. `rota/core/runner.py:1907-1918`, outside. Severity low. CONFIRMED on night
   148 s119. `disputed_paths` removes `tests/test_utils/test_echo.py::test_echo`,
   a file his words keep ("its own tests in the echo test file"), and leaves
   the pager grain he declined. The block then lists the pager grain alone.
   Frame 244 depends on this heuristic, and the heuristic is not frame 244's.
   Fix: a new frame if the night shows the echo test file lost.
6. `rota/roles/prompts/architect/annotate.md:19`, outside. Severity low.
   CONFIRMED in the cassettes. The sentence is in every annotate system text,
   so plain annotate wakes move too. `L1-AR-annotate-a-batch` changed lists
   in 2 of 5 runs. Fix: none. The case still passes 5 of 5.

## (c) Probes

All probes are in the scratchpad folder
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/dae006d1-0f15-4df0-b329-c022767b2f08/scratchpad/f244/r1/`.

- `p1.py`: loads try2.py's shapers, reads turn 1 of five sessions from the
  night databases read-only, renders the message with the HEAD
  `_files_contest_block`, and compares with shape E. Result: equal on all
  five.
- `p2.py`, `p3.py`: list every files-relay wake on nights 146 to 148 with
  its verdict, `expected` and `disputed`.
- `p4.py` to `p7.py`: read `tests/rota/cassettes.db` read-only. They list
  the case runs before and after, the annotate calls, and the recordings
  whose prompt holds the block (15).
- `parent_t/test_files_contest_block.py`: a copy of the new test, run
  against the parent worktree. Result: 2 failed, 3 passed.
- The new test file at HEAD: 5 passed in 3.84s.

## (d) Usage

Estimate, the harness carries the exact count: about 80k input tokens per
turn at the end, about 1.3M input across turns, about 12k output tokens.
