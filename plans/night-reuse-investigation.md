# Frame 231: reduce a night's cost by reusing previous nights, the investigation

Read-only investigation by an agent on Opus, 2026-10-13 18:59. Meta workflow
for the instruments, rota workflow for the seats. Code read at `67ccabe7`.
Databases opened `mode=ro`. Scripts in the scratchpad of session e669185f:
`phase_stats.py`, `xnight.py`, `xturns.py`, `roman_words.py`.

## 0. The result

Recorded wakes (option D) is the first option to build. The data shows that
a model call at temperature 0 gives the same reply on the next night when
the prompt is the same. 85 of 85 onboarding sessions of night 145 whose
first prompt night 144 had recorded gave the same first reply, byte for byte
(observed: `xturns.py`, turns of `clickI_night144.db` against
`clickI_night145.db`, 2026-10-13). 80 of 80 onboarding sessions that read no
principal answer had the same prompt on both nights, under changes to
`api.py`, `sandbox.py`, `runner.py`, `db.py` and `scheduler.py` between the
two commits (observed: the same script, and `git diff 492126aa 95157596`).
So the prompt text is an exact invalidation key. It sees a brief change, a
tool-list change, a door change and a predicate change, because each one
changes a prompt or a wake. A stamp of file hashes cannot see that. The
19 sessions that missed all read the agent principal's answers, which Opus
wrote differently on the two nights (observed: s6 to s8 and s89 to s104 of
night 145, each on a principal message or after one).

Order by saving per cycle of build:

1. D, recorded wakes, onboarding only: 3 cycles. Saves about 25 to 45 of
   37 to 59 onboarding minutes.
2. E, the principal replayed, onboarding only: 2 cycles. Saves the last
   19 sessions, 5 to 16 asks and 0.74 to 2.39 dollars.
3. G with C, one walk from a walk-boundary snapshot, per frame and by
   choice: 4 to 5 cycles. Saves 60 to 145 minutes a skipped walk, and loses
   that walk's counts.
4. A, the warm restore by briefs: 1 to 2 cycles. D supersedes it.
5. F, a shorter onboarding: 0 cycles with `--no-prose`. Do not use for a
   measured night, because the walks then start from another baseline.
6. B, the rewindable database: 8 to 10 cycles. D with E gives the same
   skip of the unchanged prefix with no undo of writes.

## 1. What a night costs today, measured

Wall clock from the `== ` markers of `.rota/night143.log`, `night144.log`
and `night145.log`. Sessions and model minutes from `sessions` and
`turns.ms`, with the phase cut at the first session whose trigger message is
at or after the sentence post `m_p1`, `m_p2` or `m_p3`. The cut for night
145's onboarding gives 104 sessions, and `.rota/clickI_warm.db`, which
night 145 wrote at 09:27, holds the same 104 sessions (observed: the check
validates the cut). Principal calls and dollars from
`.rota/clickI.principal.jsonl`, rows of kind `call`, by night and phase.

| Night, phase | Wall | Sessions | Model min | Steps, asks | Principal calls, dollars |
|---|---|---|---|---|---|
| 143 onboarding | 12:05-13:04, 59 min | 197 | 47.5 | 218, 16 | 16, 2.27 |
| 143 walk 1 | 13:04-13:33, 29 min | 70 | 23.5 | 84, 13 | 13, 1.80 |
| 143 walk 2 | 13:33-14:31, 58 min | 102 | 41.3 | 126, 13 (merged) | 13, 1.87 |
| 143 walk 3 | 14:31-about 16:06, 95 min | 159 | 77.8 | none logged | 20, 2.87 |
| 144 onboarding | 23:17-00:12, 55 min | 172 | 45.3 | 193, 16 | 16, 2.39 |
| 144 walk 1 | 00:12-02:37, 145 min | 208 | 118.1 | 250 (cap), 28 | 28, 4.25 |
| 144 walk 2 | 02:37-03:46, 69 min | 113 | 56.1 | 141, 16 | 16, 2.40 |
| 144 walk 3 | 03:46-05:25, 99 min | 125 | 78.0 | 153, 12 | 13, 1.93 |
| 145 onboarding | 08:50-09:27, 37 min | 104 | 31.1 | 114, 5 | 5, 0.74 |
| 145 walk 1 | 09:27-10:40, 73 min | 65 | 58.7 | 82, 6 | 7, 1.01 |
| 145 walk 2 | 10:40-11:40, 60 min | 66 | 47.2 | 86, 8 | 8, 1.17 |
| 145 walk 3 | 11:40-14:49 (stopped), 189 min | 204 | 157.1 | none logged | 18, 2.72 |

(observed: the logs, the three databases and the principal record,
2026-10-13; night 143's walk-3 end is the log's modification time.)

- Onboarding is 10 to 24 percent of a night's wall clock: 37 of 359
  minutes on night 145, 55 of 368 on night 144, 59 of about 241 on night
  143 (observed: the table).
- On night 145, the onboarding's model time splits as follows. The Vision
  Keeper's 38 reconcile wakes take 15.8 minutes. The Architect's 2 survey
  wakes take 3.7. The Critic's 12 challenges take 3.2. The Terminologist's
  20 defines take 2.6. The 12 Liaison message wakes take 1.7. The rest is
  under 1 minute each (observed: `clickI_warm.db`, `turns.ms` by role and
  `wake_kind`).
- The walks are 76 to 90 percent of a night, and the principal's dollars
  are under 6 dollars a night: 5.64 on night 145 (observed: the table).
- Non-model wall time is small in onboarding, about 6 minutes on night 145
  (37 wall against 31.1 model), and about 13 to 32 minutes a walk
  (observed: the table, wall minus model minutes).

Which phase each frame of sprint 3 needs to re-run (reasoned: the first
session of the seat in night 145, from `sessions` by `seq`, and the sites
in `plans/stack.md`):

| Frame | Seat and mode | First wake in night 145 | Walks that carry its count |
|---|---|---|---|
| 226, the criterion repair | Terminologist `criterion_repair` | s286, walk 3 | walk 3 on nights 144 and 145 |
| 213, the cancelled batch's test | Tester relay, the page, the Architect | Tester s127, walk 1 | three of four batches, walks 1 to 3 |
| 173, the span door | Developer `code.write` | Developer s123, walk 1 | s209 in walk 2, s386 in walk 3 |
| 229, the cycle door | Developer | s123, walk 1 | s386 in walk 3 |
| 228, the touch judge | Architect `touch_strayed` | s432, walk 3 | walk 3 |

No frame changes onboarding. Every frame's seat wakes in walk 1 already,
because the Developer and the Tester wake on the first batch at s123 and
s127, 18 and 22 sessions after walk 1 starts (observed: night 145). So a
restore at a walk boundary saves onboarding only for frames 213, 173 and
229. It saves walks 1 and 2 for frames 226 and 228 only if the read gives
up walks 1 and 2's counts.

## 2. What exists in the code

### 2.1 The warm snapshot

- Writer: `probes/walk.py:142` `write_snapshot()`, called at line 288 when
  `WALK_ONBOARD_ONLY=1`. The snapshot holds onboarding and no sentence. It
  calls `probes/warm_stamp.py` `write(run)` (observed: `git show
  67ccabe7:probes/walk.py`).
- The stamp: the hash of every brief and `.tools` file of each (role, mode)
  that committed a session, each role's `base`, plus a hard set
  (`graph.json`, `boot.py`, `predicates.py`, `scheduler.py`, `schema.sql`,
  `db.py`, the profiles) and a soft set (`runner.py`, `roles/api.py`,
  `sandbox.py`). The stamp is `.rota/clickI_warm.json`, written at
  95157596 by night 145 (observed: the file).
- Reader: `probes/gauntlet_click.sh` lines 70 to 87. A warm start runs when
  `GAUNTLET_COLD` is not 1 and `warm_stamp.py check` returns 0. It copies
  `clickI_warm.db` over `clickI.db`, relocates the project root and sets
  `WALK_FROM_WARM=1`. The check goes cold when a hard file changed, when the
  profile routes differently, or after four warm nights. A soft change only
  logs (observed: the script and `warm_stamp.py`).
- History: `c680901b` (2026-09-14) built the warm start, `7f35bd44` the
  stamp, `46f24656` (2026-09-15) the profile check, `3faf0960` (2026-09-24)
  made warm the default at Roman's word (observed: `git log -S clickI_warm`
  and `git log -S GAUNTLET_COLD`).
- Why nights 143 to 145 ran cold: each launcher sets `GAUNTLET_COLD=1`
  (observed: `.rota/launch_night140.sh` to `launch_night145.sh`). 41 of 59
  launchers set it. The rule is in `plans/operating-facts.md` line 157: set
  it "when a soft file moved (the runner, the desks, the sandbox)". Between
  each pair of night commits from 3f2e974e to 67ccabe7, `api.py` and
  `sandbox.py` changed in 6 of 6 intervals, and a hard file changed in 4 of
  6. An onboarding brief changed in 3 of 6: `vision_keeper/reconcile.md`
  twice and `architect/base.md` once (observed: `git diff --name-only`,
  2026-10-13). So the stamp alone goes cold in 4 of 6, and the soft rule
  makes it 6 of 6. The last warm nights were 130 and 131 on 2026-10-08
  (observed: `WARM:` lines in the logs).

### 2.2 The seam start

`probes/seam_start.py` (frame 104, 2026-10-01) restores a run database
paired with a batch commit, recreates each running or deferred batch's
worktree, `.venv` and test files, and runs one walk with `WALK_FROM_SEAM=1`
(observed: the file and `plans/frame104-seam-start.md`). Nights 103, 104,
110, 111 and 112 used it, and no launcher after night 112 did (observed:
`grep GAUNTLET_SEAM_DB .rota/launch_night*.sh`). `GAUNTLET_FROM=N` also
exists and starts a warm night at sentence N with nothing before it
(observed: `gauntlet_click.sh` lines 96 to 111).

### 2.3 The per-session provenance

- `sessions.briefs_hash` is `sha256(instructions)[:16]` of the composed
  brief, `prompts.compose(role, mode)`, which is the base brief and the
  mode's brief (observed: `runner.py:300` and `:3331`). It covers one
  role's one mode, not all briefs, and not the `TOOL:` lines or the
  runner's session prose.
- `sessions.prompt_hash` is in `pins_json` and the column. On night 145 it
  equals the hash of the first turn's prompt: 85 sessions match on both
  keys (observed: `xnight.py`). 436 distinct values over 439 sessions, so
  it is near-unique a session (observed).
- The cassette key, `rota/llm/cassettes.py:198` `key_for`, hashes the
  model, temperature, `num_ctx`, protocol, the whole system text and the
  user text. It sees every byte the model sees (observed: the code).
- `pins_json` holds `temperature: 0.0` and `seed: null` on night 145
  (observed: s1 and s50).

### 2.4 The write path

- `db.session_commit` (`rota/core/db.py:803`) writes the session row, the
  writes, the receipts, the messages, the turns, the tool calls and the
  checkpoint in one transaction (observed: the code).
- A receipt holds `session_id, table_name, row_id, new_version` and no
  before-value (observed: `schema.sql:820`).
- `_apply_write` (`db.py:440`) runs `UPDATE ... SET` on an existing row,
  `INSERT OR REPLACE` on a junction row and `DELETE` on a clear. The old
  value is lost (observed: the code).
- Not every write goes through the pipeline. The map tool names raw
  writers: `scheduler.sweep_checkpoints`, `lifecycle.defer` and `abandon`,
  `onboarding/boot.onboard` on `config`. The scheduler and lifecycle also
  write `batches`, `tick_attempts`, `test_runs` and the click checkout's
  git state (observed: `python -m rota.tools.map table checkpoints` and
  `table sessions`; the git state from `seam_start.py`'s docstring).
- So "undo every write of the sessions after N" is not a delete by
  session. It needs a before-image of each changed row, a journal of the
  raw writers, and the click checkout's branches, worktrees and merges
  (reasoned: the three facts above).

### 2.5 The register and cassettes

- `RecordingBackend` (`cassettes.py:321`) wraps a real backend. On a hit it
  replays the recorded completion, and on a miss it calls the model and
  records. `ReplayOnlyBackend` (`:377`) fails on a miss (observed: the
  code).
- `probes/walk.py:126` builds the night's backend from the run's profile:
  `pins, backend = _prof.pins_for(None), _prof.backend()`. One wrap at that
  line puts a night behind `RecordingBackend` (observed: the code).
- `loop._spill_endpoint` does not follow a wrapping backend, so the card
  reading needs the wrapper to pass `host` or `default` through (observed:
  `loop.py:105-120`).
- The register's cassettes database is a release asset with a `live` flag
  (frame 66). A night must use its own file, never the register's
  (reasoned: frame 66 found that a replay under a new load read as a new
  experiment).
- The night's `turns` table holds `system`, `user`, `completion` and `ms`
  per call, and `pins_json` holds the key's other fields. So a night's
  database can seed the next night's cassettes with no recording night
  (reasoned: the columns match `key_for`; the protocol is `text` unless the
  run used native tools, which a seed script must check).
- Cross-night measurement, night 145 against night 144 (observed:
  `xturns.py`, 2026-10-13):
  - Onboarding: 85 of 104 sessions had a recorded first prompt, 85 of 85
    gave the same first completion, 74 sessions were identical in every
    turn. 271 of 363 turns and 27.0 of 31.1 model minutes replay by prefix.
  - Walks: 9 of 335 sessions had a recorded first prompt. 24 of 2,152
    turns and 1.7 of 262.9 model minutes replay.
  - `plans/operating-facts.md` line 691 says a recorded prompt gave the
    recorded reply "at 3 of 4 turns", and `cassettes.py:174` says "Temp-0
    is stable within a model load and not across (measured)". The 85 of 85
    is one more observation, not a proof.

### 2.6 The principal's record

- `probes/agent_principal.py` `_ask_model` writes one `call` row per page:
  night, phase, message id, verb, page, words, ok, duration, dollars,
  model, clock. It does not store the system prompt, which holds the
  phase line and the last pages with their answers (observed: lines 150 to
  197).
- Pages repeat little across nights: night 145 had 2 of 5 onboarding pages
  seen on an earlier night, and 1 of 7, 1 of 8 and 2 of 18 in the walks.
  Night 144 had 5 of 16 onboarding pages seen before (observed: the record,
  pages compared by phase and text).
- A replay key needs the system prompt's hash beside the page, because the
  same page after other answers is another question (reasoned:
  `system_prompt()` puts the recent pages in the prompt).

### 2.7 The phase boundaries

- A walk starts at `== walk N` in `gauntlet_click.sh` and ends when
  `walk.py` reports quiet, merged or the step cap (observed: the script and
  the logs).
- A walk needs the walk before it. Walk 2 of night 145 carried walk 1's
  echo_json batch: the principal put it aside at m75. Walk 3 answered walk
  2's confirm batch at m120 and m122. Night 143's walk 2 merged into the
  click main branch (observed: the principal record and the logs).
- `restore_click` resets click to `2c8cd3a` and deletes every batch branch
  and worktree. So a walk-2 or walk-3 restore needs the main branch's merge
  commits and each live batch's head, which `seam_start.py` restores for
  batches and not for main (reasoned: `restore_click` and the seam
  docstring).

## 3. The history and the rulings

- `plans/composition.md:57`: "A seat restarts from records. There is no
  snapshot." Line 105: "A seat restarts from records. The snapshot design
  is dropped." Ratified 2026-09-16. The dropped design is a seat's
  suspend-and-resume: law 5's checkpoint of a working set, from which a
  seat resumes (observed:
  `plans/archive/checkpoint-check-2026-09-16.md`). The `checkpoints` table
  has one insert and no caller passes a checkpoint (observed: the same
  record). The line rules out a seat-level snapshot in the rota workflow.
  It does not rule out a run-level restore in the meta workflow. The warm
  start runs since 2026-09-14 and the seam start since 2026-10-01 under
  Roman's rulings (reasoned: both restore the whole run database before any
  seat wakes, and each seat then restarts from records).
- Line 103, "Checkpoints are opt-in", uses the word for a point where the
  principal spends attention, not for the table (observed: the archive
  record).
- `plans/operating-facts.md` line 152: a warm snapshot behind a schema mark
  stops at the door. Line 154: a seam snapshot older than an in-place
  column fails, so the restore opens it through `init_db`. Line 155: a seam
  carries the source night's `tick_attempts`. Line 175: the night script
  keeps one generation, `clickI_prev.db`, so a night's database is copied
  to `clickI_night<N>.db` at once (observed: the file).
- `DECISIONS.md` and `LAWS.md` carry no line on warm, snapshot, replay or
  rewind (observed: `grep`). `git log -S rewind` finds only frame 231's
  push, `17ecb046` (observed).
- Memory `rota-iteration-speed.md` (2026-09-14): standing permission for
  phase-optimised plans, "snapshot at the phase boundary the run actually
  tests", and "Further boundaries worth a snapshot when a night tests one
  desk: after the touch note (Developer nights), after the first commit
  (Tester and review nights). Not built yet." (observed: the memory file).

Roman's words in the build transcripts, his typed messages, timestamps as
the transcript writes them, which reads about one hour behind the records'
local clock (observed: `roman_words.py` over 102 transcripts, 2026-10-13):

- 2026-09-17T17:22: "Does this still use the warm onboarding system?"
- 2026-09-24T01:22: "Do we still have the warm onboarding system to cache
  onboarding?"
- 2026-09-24T01:23: "Why is this not always on? This has automatic
  invalidation right?" (recorded as the ruling of 2026-09-24 02:27).
- 2026-09-29T04:43: "So did we fix and restart from warm?"
- 2026-10-01T01:32: "Is there any way to speed up iteration of the
  nights?" (frame 104, the seam start, followed).
- 2026-10-13T17:37: "we used to be merging, now we are working on systems
  that impact this?  are we still using the onboarded checkpoints?  are we
  only implementing a few small fixes a night, slower than they are being
  generated?"
- 2026-10-13T17:46: "Checkpoints should only be dropped if the briefs that
  made them have been affected, is it cheap to make a system that tracks
  what briefs have beeen used to make a certain state of db, and if any
  brief changes, rewind the db down to when the last brief that was used."
- 2026-10-13T17:49: "so not a full checkpoint per session but a rewindable
  database  the biggest issue, mm ok that sounds too convoluted, should we
  just keep working the way we are?"
- 2026-10-13T17:50: "ok im not confident about the approach, the goal is
  reduce iteration cost by reusing previous nights, Please do a complete
  investigation of possibilities"

Roman's 2026-09-24 question, "This has automatic invalidation right?", is
the requirement every option below is judged on (reasoned: he made warm the
default on that condition).

## 4. The options

Each option has six lines: what, exists, build, saves, invalidates, risk.
Savings are per night, from section 1.

### A. Warm restore conditioned on briefs

- What: restore `clickI_warm.db` when no brief of a mode that woke during
  onboarding changed, compared by `briefs_hash` per role and mode, and
  else run cold.
- Exists: all of the restore, and a stamp that already hashes each
  onboarding mode's `.md` and `.tools` (section 2.1). The cold choice is a
  launcher habit, `GAUNTLET_COLD=1`, not the stamp.
- Build: 1 to 2 cycles. In `probes/warm_stamp.py`, move `scheduler.py`,
  `db.py`, `graph.json` and `predicates.py` to a set that only logs, or
  compare each recorded session's `briefs_hash` with
  `prompts.compose(role, mode)` of the tree. Drop the soft-file rule from
  `plans/operating-facts.md` line 157.
- Saves: the whole onboarding, 37 to 59 minutes, 114 to 218 steps, 5 to 16
  asks, 0.74 to 2.39 dollars, 31 to 47 model minutes. By briefs alone, warm
  in 3 of the last 6 intervals (section 2.1).
- Invalidates: an onboarding mode's brief or tool list. The system knows by
  the hash. It does not know about a door, a predicate or a runner change
  that alters an onboarding session, because `briefs_hash` does not cover
  the `TOOL:` lines, the session prose or a tool result.
- Risk: a door change that moves onboarding goes unseen until the fifth
  night. Night 144 to 145 moved no onboarding prompt outside the
  principal's answers (observed: 80 of 80, section 0), but that is one
  pair of nights. A night that measures onboarding must run cold.

### B. The rewindable database

- What: undo every write of the sessions after the last session whose
  brief still matches the tree, and resume the night from there.
- Exists: receipts name the rows a session changed, without the old value
  (section 2.4). `seam_start.py` restores batches from a database.
- Build: 8 to 10 cycles. An undo log of before-images by SQLite triggers on
  the 48 tables or in `session_commit` and every raw writer
  (`rota/core/db.py`, `scheduler.py`, `lifecycle.py`), a git journal of the
  click checkout (main, batch branches, worktrees, `.venv`), the agent
  principal's `recent` list, and a mid-walk resume in `probes/walk.py`.
- Rewind point: the first session `s` whose recorded `briefs_hash` differs
  from `prompts.compose(s.role, mode(s))` of the tree, which is computable
  offline (reasoned: the runner composes it the same way). For night 145
  and a Developer door that is s123, 18 sessions into walk 1. For frame
  226's repair it is s286 in walk 3, for frame 228 s432.
- Partial walk: the night opens mid-walk with a batch half built, open
  pages unanswered and a principal with no recent pages. The walk loop
  must restart its counters from the records (reasoned).
- Saves: onboarding plus the walk prefix before the rewind point. Walk 1
  starts its Developer and Tester at s123 and s127, so for 3 of 5 sprint-3
  frames the saving is onboarding plus about 11 model minutes. For frame
  226, 173 model minutes. For frame 228, about 290 (observed: night 145).
- Invalidates: a brief change by `briefs_hash`. A door change shows in no
  hash, so a door frame, which is most of sprint 3, rewinds to the wrong
  point (reasoned: section 2.3).
- Risk: a high risk. Three nights rewound to one point measure one history
  three times, so a ratio over three nights is one sample. A missed raw
  writer leaves a state no night ever made.

### C. Phase snapshots at each walk boundary

- What: `walk.py` writes the run database and the click state at each `==
  walk N`, and a night starts at the first walk the frame's site affects.
- Exists: the onboarding snapshot, the seam restore for batches, and
  `GAUNTLET_FROM` (sections 2.1, 2.2).
- Build: 4 to 5 cycles. `probes/walk.py` writes `clickI_walk<N>.db` and the
  main head. `probes/seam_start.py` restores main's merges and every live
  batch. `probes/gauntlet_click.sh` takes `GAUNTLET_FROM` with the walk
  snapshot. A map from a `Site:` file to the modes it serves and the first
  walk each mode wakes in.
- Saves: for sprint 3, onboarding only, the same as A, because every
  frame's seat wakes in walk 1 (section 1). It saves walks only with G.
- Invalidates: the walk snapshot carries the sessions of the walks before,
  under the old code. Any change to a seat that woke before the boundary
  makes the snapshot a state the new code would not make (reasoned).
- Risk: medium. The `Site:` field names files, and `api.py` serves every
  seat, so the map gives walk 1 for most frames (reasoned).

### D. Recorded wakes

- What: a model call whose cassette key, the whole prompt and the pins,
  matches a recording of an earlier night takes the recorded reply and
  spends no GPU. Any changed byte runs live.
- Exists: `RecordingBackend`, `key_for`, `open_dev_db`, the per-turn
  `turns` rows of every night database, and the `sessions.backend` column
  that would read `cassette:ollama` on a replay (section 2.5).
- Build: 3 cycles. Wrap the backend at `probes/walk.py:126` in
  `RecordingBackend` over a night-only file `.rota/night_cassettes.db`,
  when `WALK_REPLAY=1` and the phase is onboarding. Pass `host` and
  `default` through for the card reading (`rota/llm/cassettes.py`). A seed
  script, `probes/seed_night_cassettes.py`, fills the file from the last
  night's `turns` and `pins_json`. `rota/tools/nightcount.py` prints the
  replayed sessions and turns. `probes/gauntlet_click.sh` drops
  `GAUNTLET_COLD=1` from the launcher template and sets the flag.
- Saves: on night 145, 27.0 of 31.1 onboarding model minutes and 74 whole
  sessions against night 144's recordings. The wall clock falls from 37 to
  about 10 minutes (reasoned: 6 minutes of non-model time plus 4 live model
  minutes). In walks, 1.7 of 262.9 minutes, which is about nothing.
- Invalidates: any change of the system or user text, the model, the
  temperature, `num_ctx` or the protocol. The system knows by the key
  itself, at turn grain. A changed door changes the tool result, so the
  next turn's prompt and every later reader of the changed records run
  live (observed: s6 to s8 and s89 to s104 went live on the principal's
  changed words). No stamp and no launcher habit is needed.
- Risk: low in onboarding. A replay is the reply the same prompt got on an
  earlier load, and loads differ at temperature 0 in about 1 of 4 turns by
  `operating-facts.md` line 691 and in 0 of 85 here. Keep a live onboarding
  every fifth night, as `MAX_WARM` does. In walks, a replayed session must
  not count as a new sample in a ratio, so `nightcount` must name the
  replayed sessions before D runs in a walk.

How the cassettes are shared: a night file, never the register's
`cassettes.db`, because the register is a release asset and its `live`
flag would read a night's copy as a measurement (reasoned: frame 66). The
night's randomness: temperature 0 and no seed. The key holds no clock and
no random id: 85 of 104 first prompts matched across two nights (observed).
What breaks a chain is upstream text, mostly the principal's answers.

### E. The principal replayed

- What: the agent principal's answer is replayed when the phase, the page
  and the system prompt match a recorded call, so an unchanged onboarding
  costs no Opus call and gives the same answers.
- Exists: the record holds the page, the words and the dollars per call
  (section 2.6). It does not hold the system prompt's hash.
- Build: 2 cycles. `probes/agent_principal.py` writes `system_hash` on each
  `call` row and, under `WALK_REPLAY=1` in onboarding, answers from the
  latest matching row before it calls Opus.
- Saves: 5 to 16 asks, 0.74 to 2.39 dollars and about 1 minute of Opus
  time. With D, it also makes the 19 sessions after the principal's
  answers replay, so the whole onboarding replays: the last 4.1 model
  minutes (reasoned: the misses in section 0 all follow a principal
  answer).
- Invalidates: a changed page or a changed answer before it. The key says
  so with no stamp.
- Risk: in onboarding, low, because no sprint-3 frame measures onboarding.
  In walks, high. The principal's Opus answers are the night's main source
  of variance, so a replayed principal in a walk turns three nights into
  one sample (reasoned: walks replay 1.7 of 262.9 minutes only because the
  answers and the code differ). Keep E out of the walks.

### F. A shorter onboarding

- What: drop or cache the 38 reconcile wakes, 15.8 of 31.1 model minutes.
- Exists: `rota onboard --no-prose` (`rota/cli.py:485`, `:929`) withholds
  the prose. Memory `rota-iteration-speed.md` priced it at 5 minutes on
  2026-09-14.
- Build: 0 cycles for `--no-prose`. A cache of the reconcile per click
  commit is not separable: reconcile reads each file "against the account",
  which the principal's approval at m3 shapes, so the cache is D and E
  under another name (reasoned: night 145 log line 5).
- Saves: about 16 model minutes with `--no-prose`.
- Invalidates: nothing tracks it. It is a flag.
- Risk: high for a measured night. The walks then start without the prose
  entries, which is another baseline than nights 143 to 145, and a ratio
  against night 145 compares two setups (reasoned).

### G. One walk per night

- What: run only the walk that holds the measure, from a snapshot after the
  walks before.
- Exists: `GAUNTLET_FROM=3` with a warm start skips walks 1 and 2 today,
  but walk 3 then starts with no walk-1 or walk-2 batches. That is not the
  state night 145's walk 3 met (section 2.7). With C, the snapshot is the
  real state.
- Build: 0 cycles with `GAUNTLET_FROM`, or with C's 4 to 5 cycles.
- Saves: on night 145, walks 1 and 2 are 133 minutes and 105.9 model
  minutes, plus 2.18 dollars. On night 144, 214 minutes.
- Invalidates: as C. The snapshot of walks 1 and 2 ran under the old code.
- Risk: lost counts. Frame 213 counts on three of four batches over walks 1
  to 3, and frame 173 counts s209 in walk 2. A walk-3-only night gives
  frames 226, 229 and 228 their counts and loses those (observed: section
  1). A frame whose walks before are the cause, as frame 229's hint in walk
  3 that started frame 228's loop, needs the history live.

### H. Added: the live seam probe

- What: the door is tested on recorded turns of earlier nights, with no
  night. The probe sends a recorded turn to the model with the new door's
  refusal and reads the next call.
- Exists: `probes/frame37/interview_turn.py`, `seamlib.py` of frames 135
  and 136. Frames 135 and 136 closed so in 184.2k and about 2 minutes of
  card time (observed: `plans/operating-facts.md` line 691).
- Build: 0 cycles a frame beyond the probe.
- Saves: a night for the first part of an ends-when, the mechanism.
- Invalidates: not applicable.
- Risk: it measures one turn, not the ratio. The rule of 2026-10-03 wants a
  ratio from a night, so H moves a wall's first check off the night and
  not the count (reasoned).

## 5. The recommendation

1. Build D for onboarding, 3 cycles, about 100k to 150k of agent tokens.
   First step, 1 cycle: wrap the backend at `probes/walk.py:126` under
   `WALK_REPLAY=1` and `WALK_PHASE=onboarding`, and seed the night file from
   `clickI_night145.db`. Site: `probes/walk.py`, `rota/llm/cassettes.py`,
   `probes/seed_night_cassettes.py`, `rota/tools/nightcount.py`,
   `probes/gauntlet_click.sh`. None of these is the implementer's current
   site, `runner.py`, `sandbox.py` and the prompts (reasoned: the git
   status of 2026-10-13).
2. Build E for onboarding, 2 cycles, in `probes/agent_principal.py`.
3. Keep onboarding cold-built but replayed. Drop `GAUNTLET_COLD=1` from the
   launcher template once D runs, and retire A: D sees every change A
   sees, and the door changes A cannot see.
4. Use G per frame by choice, and build C only when a frame's seat first
   wakes after walk 1 and its counts sit in one walk. No sprint-3 frame
   needs it except 226 and 228, whose ratios also read walk-3 history.
5. Do not build B. D with E gives the unchanged prefix at no GPU cost, and
   it needs no undo of a write.
6. Do not use F on a measured night.

The measurement that proves each saving is the next night's phase clock
against night 145's:

- D: onboarding wall under 15 minutes against 37, with at least 70 of the
  onboarding sessions on `cassette:` in `sessions.backend` and the same
  onboarding asks as the recording.
- E: onboarding principal calls 0 against 5, and 0.00 dollars against 0.74.
- G: the night's wall against 359 minutes, and the counts each frame lost.

Combinations: D and E combine, and E needs D to save GPU. D and C combine.
C and G combine. D supersedes A. D with E excludes B, because both buy the
same prefix. F excludes comparison with nights 143 to 145.

Composition lines: none of D, E, A, C or G crosses `plans/composition.md`.
Each is a meta-workflow instrument on the run, and each seat still starts
from records (reasoned: section 3). B touches no line either, but it
deletes committed records of a run, and the records are what a seat
restarts from. Bring B to Roman only if D and E do not meet the measure
(reasoned: no law was read for a rule on deleting committed rows, so a
history read comes first). E puts a recorded stand-in answer on a page. The
agent principal is already a stand-in of the meta workflow, so a replayed
answer changes no principal line, and Roman may want to know that
onboarding answers repeat night to night, rated low (reasoned).

## 6. Register lines

The frame writes none. The closing session can add one line to
`plans/operating-facts.md`, the models section: a temperature-0 call gave
the same first reply across two nights in 85 of 85 onboarding sessions,
night 144 to 145, 2026-10-13 (observed: `xturns.py`).
