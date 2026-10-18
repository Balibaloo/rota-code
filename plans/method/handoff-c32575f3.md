# Momentum note of session c32575f3, peer name rota-9d

Message rota-9d for anything this note withholds or you doubt. I keep the
last of my context to answer, and I stop when you message the word
released. Read `CLAUDE.md` first, then
`python -m rota.tools.state --sid <your sid>`, then this, then the pointers
the frames name. Written on 2026-10-18 at about 19:35, at the hand-off.
Meta workflow.

## What happened in this session, in rota's terms

Frame 298 ran its night. Night 157 merged nothing in 363 sessions, but it
moved the deaths off the request line: 0 of 2 batches died on a line-1
ruling, against 2 of 3 on night 156, M0 7 of 8, M3 0 of 5, M4 0 cancels.
Both batches then died where the tests and the review decide. The read is
`plans/night157-read.md`, and the sprint 14 order is at the top of the
stack, at 3d5fe03d.

Frame 297 was taken while the night ran and built in six passes, 095db1c4
to 37bbc243, four reviews, three clean gates. Its premise was wrong on the
records: the note `l_cab4458639` was s214's own, bg_2's batch-start
Developer, logged after frame 283's door refused its fourth commit, not a
relay Developer's. The provenance is `plans/frame297-provenance.md`. The
fix has two parts. The ledger door refuses a Developer's note on a path with
an open dropped note when the text does not name the removal, reading the
tree first. The runner discards a Developer session's uncommitted writes
at every session end, the failed path and the boot included, closes the
dropped notes of those paths, and the next Developer reads "discarded
before you" in `batches.expect`. The discard enforces law 4 as Roman
ratified it on 2026-09-16; the history is `plans/frame297-discard-history.md`.
The question went to him at about 17:11 as a low with a timer, he disputed
the facts once and the records held, and the repair was taken by timeout.

Two general defects fell out. `code.write` wrote CRLF through
`Path.write_text` on Windows, and a plain LF fix broke CRLF checkouts under
`core.autocrlf=true`; a write now keeps the file's own line ending. The
`_says` token rule rejected `echo(` when a word character followed it, so
frame 283's close missed s215's honest note.

## What I believe, and what to doubt

Doubt first the discard's reach: review 4 put back seven path shapes and
left two locked files, named exactly, and nobody has yet watched a night
with it. Night 158 measures frame 297 on page notes that cite uncommitted
lines, 0 of 3 on night 157, and sessions that inherited a write, 5 on
night 157. Doubt second frame 298's W4: the guess rewrites reach no page,
because a park, a batch plan and a new item version each replace the
rewrite. It is measured at night 158 before any fix. Doubt third the
gate of pass 6 at 37bbc243: it was running when this note was written.
Read frame 297's last status line for its result.

The baseline is still f9f5cd19 of 15:51, in `.rota-gate.json` of the
checkout and `C:/Users/roman/rota_g297`. Every gate of this session ran
from `rota_g297` with frame 298's closing register copied in: a gate
worktree without `tests/rota/cassettes.db` prints "the register is absent"
and counts 25 reds gone, operating-facts line 691.

## The held frames and what is live

- Frame 298: validating on its third batch at night 158, closing commit
  d2e85f79. Night 157's files: `.rota/clickI_night157.db`,
  `.rota/night157_report.txt`, `.rota/night157_truth.txt`.
- Frame 297: mechanism closed at 37bbc243 on a clean gate, validating at
  night 158. Residues named in reviews 3 and 4: a mixed-ending file, the
  whole-file write with no dropped note, `harness.py` and `scaffold.py`
  on `write_text`.
- Frames 283 with 140, 296, 143, 258, 220, 286, 282, 290: validating, the
  counts in the read's section 1. 296 and 258 are at night 2 of 3.
- Frames 299 and 300: free now that frame 298's night ran. 299 first.
- Worktrees of mine: `C:/Users/roman/rota_r297` and
  `C:/Users/roman/rota_g297`. Briefs and reports are under
  `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/c32575f3-13b3-4420-a2aa-defc2ca8caea/scratchpad/`,
  `f297_*`, `n157_*`.
- The next night runs from a worktree at the sprint's closing commit.

## Roman's last words, with time

- About 17:25: "What's the question?"
- About 17:30: "The second builder works in a different copy of the
  worksite, it never sees the part". The records disagreed, and I told him
  so. He gave no A or B.
