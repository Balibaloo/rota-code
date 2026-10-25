# Momentum note of session 0699ee05, peer name rota-bc

Message rota-bc for anything this note withholds or you doubt. I keep the
last of my context to answer, and I stop when you message the word
released. Read `CLAUDE.md` first, then
`python -m rota.tools.state --sid <your sid>`, then this, then the pointers
the frames name. Written on 2026-10-25 at 18:30, with night 166 live since
18:25. Meta workflow.

## What happened in this session, in rota's terms

I took the stack from rota-3c at 13:11 during frame 323's think re-run.
Roman was present all afternoon and ruled four times, all on frame 323's
status lines: the think run stopped at 14:26; a native tool-calling test
on four cases both models fail came first; a pause at 15:59; a resume at
17:50. Night 166 waited on the test by his order and launched at 18:25.

Frame 323 moved from "which model" to "which protocol". Native tool
calling existed in pieces and reached no run: a profile could ask for it,
the runner sent schemas, and nothing executed a native reply. Three
passes on one implementer and three reviews wired it end to end, opt-in
by a profile's `native_tools = true`, text mode byte-identical over 325
prompts. On the branch as 6132e6ed, edfbab34 and 25e35498, plus 741d2d06
for the shipped-profile count. The gate on 741d2d06 shows the four known
Tester reds of frame 281 and nothing else.

The trial ran twice from the worktree `C:/Users/roman/rota_p323n`. The
second, at ae8a6573, 15:08 to 15:35: Gemma 0 of 4 cases, qwen3.5:9b 2 of
4, the Tester case from 0 of 5 on text to 5 of 5. The why-read,
`f323_native_read.md` in my scratchpad, found that three of the four
cases cannot pass on any model as built: an empty code index, no
`project_root` in the Tester fixture, no `ledger.log` in the Terminologist
deliver set. Qwen's own wall is the `refs` door that refuses a JSON string
list with no form shown. Gemma's own wall under native with think off is
that it writes no text, reads once a turn and repeats. Frames 326 and 327
hold the rota faults, parked for the economy, which reads 20 live of 10.

Also today: the standby watcher waits one day instead of two hours,
55c00b3b. Roman's three side questions and their numbers are on frame
323's line of 15:37: model swaps cost about 10 percent of a night's model
wall, 326 switches in a day; the `gpu-unlock` module buys 2 to 5 percent
and needs Linux; one model on every seat removes the swaps.

## What I believe, and what to doubt

Doubt first the per-model table of frame 323. The register measures fit
to Qwen, not capability: every case is a Qwen fault fixed, and three of
the trial's four cases are red by construction. The reading I gave Roman,
and he did not contest: the night is the instrument that is not built
against Qwen. Doubt second the "text before" column I quoted for Qwen at
15:37; the register holds no think-off qwen3.5:9b text rows for three of
the cases, and the rows that exist are qwen3:8b. Doubt third the Gemma
switch recommendation of the morning, the Critic on Gemma: two models do
not fit the card together, so it waits on the Titan fit. Doubt fourth
night 166 itself: it is the first night with the native code on the
branch, text mode by profile, so any change in its numbers is not the
native code unless a run bound a native profile, and review 3 found none.

## Open questions for Roman

Frame 323: the Gemma night's timing, after frames 326 and 327. Frames
114 and 115 since 2026-10-02. Frames 314 and 315 wait on his read. The
frame economy at 20 of 10 is his re-order. A cleanup he did not yet rule:
eight of ten shipped profiles are one-shot trial records.

## Where things are

- Night 166: `C:/Users/roman/rota_n166` at 741d2d06, cold, items 163
  rotated, launched 18:25 by `.rota/launch_night166.sh`. The launcher
  writes no log file of its own; the gauntlet's records appear under
  `.rota/` as `night166*` and `clickI_night166*` as the walks run. Read
  each CYCLE line as it lands, then the end, then the read.
- Native trial: `f323_native_run.sh`, `f323_native_run.log`,
  `f323_native_suite_gemma4.txt`, `f323_native_suite_qwen3.5.txt`,
  `f323_native_read.md`, `f323_think_read.md`, all in
  `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0699ee05-aed4-42bd-b867-004e80f7d047/scratchpad/`.
  The register copy `C:/Users/roman/rota_cassettes_f323.db` holds every
  trial row; rows before af2dd132 are stamped `text`.
- Review probes: `p323r/`, `p323s/`, `r3/` in the same scratchpad.
- Worktrees: `rota_g301` at 741d2d06, the gate's; `rota_p323n` at
  af2dd132, on the branch, free to remove; `rota_n166`, the night's.
- Review 3's six low findings are on frame 323's line of 15:54, not yet
  frames: `profile_pins` keys at 16384 under a named profile,
  `migrate_register` rebuilds keys without tools, three guards.

First after the take: watch night 166's CYCLE lines. At its end, the read,
then the gate from `rota_g301` at the head. Then frames 326 and 327 in
order, and the Gemma night when Roman says so.
