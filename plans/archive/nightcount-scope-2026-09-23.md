# Scope report: the night's four counters (frame 76)

Read-only report by a reviewer agent on 2026-09-23 15:35, 83k on the
harness line against 30k priced and a 40k cap, 57 tool calls. Meta
workflow. The frame is 76, every night counts what the model made up and
what the runner ran anyway. The findings below are the agent's, marked as
it marked them.

## Findings that change the counters

1. **Counter 1 must read `completion`, not the feedback line in `user`**
   (CONFIRMED: `rota/core/db.py:897-899` stores each turn's whole
   assembled prompt in `user`, so the feedback line persists into every
   later turn of the session; `db.py:907-924` `session_note` writes the
   runner's errors as a final turn). Probe on night 88: 56 turns match
   `FABRICATED_RESULT` in `completion` across 36 sessions, and all 36
   carry a `SESSION ENDED` note with `wrote its own tool results`. The
   feedback line appears in `user` of 106 turns in 31 sessions. So frame
   75's count overcounted turns and undercounted sessions. Fix: count
   turns whose `completion` matches `FABRICATED_RESULT`, imported from
   `rota.core.runner`, and sessions whose note carries the phrase.
2. **Counter 2's real results sit in the next turn's `user`** (CONFIRMED:
   a write result inside the fabricated completion reads 0 on nights 86,
   88 and 89 and 7 on 90; inside the next turn's `user` it reads 1, 0, 0
   and 8). Every fabricating session on every night has
   `sessions.committed = 1`. So frame 75's "23 writes on night 90" counted
   old feedback lines beside later writes. Fix: for each made-up turn,
   read `turns.user` at `seq + 1` of the same session, and print both
   numbers, made up and ran anyway.
3. **The repeat line has three eras** (CONFIRMED by `git log -S` and
   `git merge-base --is-ancestor`). `5c76af2`, 2026-08-11: `unchanged
   since you asked earlier this session; the answer is above.` `b645f3d`,
   2026-08-13: `was run for you before you started; the answer is in the
   list above.` `59cb2ad`, 2026-09-21: both tails replaced with `What
   {call.name} returned then still stands.` Nights 85 to 88 lack `59cb2ad`,
   nights 89 and 90 have it. The substrings `was run for you before you`
   and `unchanged since you asked` match every era. Counter 3 by those:
   77, 50, 51 and 83 prompts on nights 86, 88, 89 and 90.
4. **Counter 4 as worded gives 11 on night 88, not frame 58's 12**
   (CONFIRMED: `SELECT count(*) FROM sessions s WHERE EXISTS (SELECT 1
   FROM sessions e WHERE e.prompt_hash = s.prompt_hash AND e.wake_kind =
   s.wake_kind AND e.seq < s.seq)`). Five groups of 16 sessions: four
   consecutive triples at 78-80, 94-96, 137-139 and 162-164, which frame
   58 named, and `tick:quarantined` liaison at seq 1, 81, 97 and 167,
   which it did not. Fix: print groups, members and repeats.
5. **The eviction notice and the fabrication feedback are era-free**
   (CONFIRMED: `re-read anything you still need` since `5c76af2`; the
   feedback line and the regex `^\s*(?:OK|ERROR)\s+[a-z_]+\.[a-z_]+\s*(?:->|:)`
   since `feb11d3`, both 2026-08-11, unchanged).
6. Night 90's database is `.rota/clickI.db`, not `clickI_night90.db`
   (CONFIRMED: `.rota/launch_night90.sh:22,28`). The archive rename is
   manual, and `require` accepts a run name or a path.

## Where the report is rendered

- `render_state` at `rota/roles/principal.py:183-258` is the principal's
  sentence, "Stuck. The team gave up on: ...". It reads `batches`,
  `items`, `tick_attempts` and `test_runs`, never `turns` or `sessions`.
  Four callers: `rota/cli.py:721` (`cmd_agenda`),
  `rota/tools/onboard_run.py:122`, `probes/walk.py:268`,
  `probes/seat.py:161-162`. Four counter lines there would reach `rota
  agenda` and the seat probe, and print three times a night.
- The walk's end, `probes/walk.py:266-272`: `record()` appends a JSON row
  to `tests/rota/walks.jsonl`; `probes/progress.py:161-171` writes the
  44-column block to `RUNS/progress_{run}.md` and `.rota/progress.md`;
  `finish` at `:65-72` writes `RUNS/progress_ref_{run}.json`. None holds a
  turn fact. Night 90's log ends `quiet after 30 steps, 5 asks` / `---` /
  the state sentence / `GAUNTLET-DONE 12:20` / `launcher done 12:20 exit
  0`. Each walk prints `== walk N HH:MM` first
  (`probes/gauntlet_click.sh:72,77,82`).

## The command shape to copy

`rota/tools/audit.py:211-233`: `main(argv)`, `paths = [require(argv[0])]
if argv else sorted(RUNS.glob("*.db"))`, `connect_readonly(p)`, one line
per run and a total. `connect_readonly` at `rota/core/db.py:149-156` opens
`?mode=ro` with `query_only`. `require` at `rota/cli.py:95-110` resolves a
run name and lists the runs on a miss. Tests of `audit()` in
`tests/rota/test_refs.py:491` and `tests/rota/test_chaos_inquiry.py:140`.
The fixture pattern is inline: `tests/rota/test_progress.py:20-23`,
`init_db(tmp_path / "clickI.db")` then raw `INSERT INTO sessions (id,
role, wake_kind, wake_detail, committed, seq, mode, model)`. No test
writes `turns`; `session_fail` (`db.py:887-904`) and `session_note`
(`db.py:907-924`) are the writers a fixture can call.

## Frame 58's measure

Frame 58 kept no SQL (CONFIRMED: commit `dfdb5e4` names the sessions in
prose, "a session-by-session `prompt_hash` comparison"; no `probes/frame58/`).
The query in finding 4 reproduces its four triples and one group more.

## Where the count belongs

Recommended: a new module `rota/tools/nightcount.py` shaped on
`audit.py`, one line per counter, importing `FABRICATED_RESULT` from the
runner. Command `python -m rota.tools.nightcount clickI`, or a path, and
no argument audits every `*.db` in `RUNS`. Call site
`probes/gauntlet_click.sh:84`, one line before `GAUNTLET-DONE`, so the
night prints it once after the third walk and an archived database gets
the same command later.

Alternative, rejected: four lines in `render_state`. It is a sentence for
the person who waits, it is printed by three other callers, it opens no
`turns`, and a night would print it three times.
