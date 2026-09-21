# The register's key: design record

Frame 54, the register's match is narrower than the cassette key, with frame
60's repair folded in. Written 2026-09-21 by session 75f21e35, peer name
rota-36. Meta workflow.

**Revision 3, 2026-09-21**: Roman ruled the open question of section 9. The
register is cloned, what is useful migrates, and a full re-record is
approved. Section 9 carries it, and sections 3 and 8 follow it.

**Revision 2, 2026-09-21, after the design review.** The review returned "not
safe to build as written" with three high defects and nineteen findings. Every
correction is in the body and section 10 lists what changed and why. The
holding session re-measured the four claims that change a decision, and those
carry its own mark.

Read this with frame 54's first read in `plans/stack.md`.

## 1. The fault, in one paragraph

A recording is identified by seven things. A result is identified by three.
Four of the seven have no column in `case_runs` to hold them. So the report
cannot match what the cassette key covers, and it never could. One narrow key
gives two opposite symptoms: a case reads stale when it is green, and a case
reads green when the suite cannot replay it.

## 2. The two keys, field by field

(observed: `rota/llm/cassettes.py:105-120`, `rota/llm/llm.py:47-92`,
`rota/tools/casestatus.py:62-82`, 2026-09-21)

| Field | In the cassette key | In `case_runs` | Matched today |
| --- | --- | --- | --- |
| model | yes | yes | yes |
| temperature | yes | no | no |
| `num_ctx` | yes | no | no |
| protocol, text or native | yes | no | no |
| the system text | yes | no | in part, see below |
| the user text | yes | no | no |
| extras, the optional pins that are set | yes, when set | no | no |
| `case_id` | no | yes | yes |
| `prompt_hash` | no | yes | yes |
| `load_id` | no | yes | no, and it must stay out |

**`prompt_hash` covers the mode prompt. The comment this frame was founded on
is wrong** (observed: `rota/roles/prompts.py:94-100` and
`rota/testkit/fixtures.py:836-842`, 2026-09-21). `instructions_for` calls
`compose(role, mode_of(case))`, and `compose` is `base(role, verb)` plus
`piece(role, verb)`, where the piece is the mode prompt file. The comment at
`rota/tools/casestatus.py:71-73` says the opposite, that editing `answer.md`
leaves the hash untouched. **That comment names the wrong mechanism, and frame
54 cites it as the frame's reasoning.** The fault the frame names is real. Its
stated cause was not.

**The text that is truly outside the hash is the runner's session prose and
the tool list** (observed: the holding session's own measurement over the
suite's 117 single-session cases, 2026-09-21). `instructions_for` is a strict
prefix of a cassette's `system` for **117 of 117** cases, and exact for none.
The tail is the runner's session prose and `sb.signatures()`, which is the
working set printed as `TOOL:` lines. For `ACT-TS-give-the-prompt-a-stream`
the instructions are 4395 characters and the cassette's system is 6100.

**So the false green comes from a tools edit, not a prompt edit.** A change to
a `.tools` file, a tool signature or the runner's session prose moves the
cassette key and leaves `prompt_hash` alone.

**And the text has already moved, often** (observed: the same measurement,
2026-09-21). **42 of the 117 cases hold recordings under more than one system
text**, and `L1-DV-fix-what-the-verdict-names` holds seven. The register holds
830 distinct system texts. This is not a latent gap. It is the register's
history.

## 3. What the design adds

`case_runs` gains five columns. Four are below and the fifth, `system_hash`,
is section 9's.

| Column | Type | Default | Why |
| --- | --- | --- | --- |
| `num_ctx` | INTEGER | 12288 | The largest single cause of a false state. It is in the key and an ambient variable sets it. |
| `temperature` | REAL | 0.0 | Every cassette in the register is at 0.0, so the column is cheap and it closes the field. |
| `protocol` | TEXT | `'text'` | 18570 of 18604 cassettes key as text and none as native (observed: the review's probe 5). A native recording must not answer for a text run. |
| `extras` | TEXT | `'{}'` | The set optional pins, as `Pins.extras()` builds them. `think` is the live one: 34 cassettes key at `think=True`, all `qwen3.5:9b`. |

`status()` must have a value for each before it can match on one.
`rota/tools/casestatus.py:62` builds the wanted pins with the model and the
prompt only. **The design states each source**: `num_ctx` from
`DEFAULT_NUM_CTX`, temperature 0.0, protocol `'text'` with the
18570-of-18604 measurement as the reason, and `extras` from `ROTA_PROFILE`
through the same `_think_for` rule that `tests/rota/test_l1.py:46-54` uses.

**`load_id` stays out of the match, and the design says why** (observed:
`rota/llm/cassettes.py:343-354` and `:399-421`, the review's finding 4). It is
`model@epoch//7200`, so matching on it would stale every case two hours after
its recording. It would also break `trust`, which reads several loads to
separate `provisional` from `earned`.

**A fifth column, `system_hash`, is added over the whole system text the
model receives.** Section 9 carries Roman's ruling that pays for it, and the
migration there is what fills it. `status()` computes it from the same
composed text the runner sends.

## 4. The four columns' values on a migrated row

(ruled: Roman, 2026-09-21, asked with two other answers: write the rows off,
do not re-record. **Superseded in part by the ruling in section 9**, which
clones the register and approves a full re-record. The write-off below still
governs the four columns of a row that migrates. It no longer governs the
system text, and it no longer forbids a re-record.)

**A migrated row takes 12288, 0.0, `'text'`, `'{}'`.** There is no second
step. A row that does not migrate keeps nothing, because it stays in the
clone.

**Revision 1's step 2 is deleted, because the evidence says it fires on
nothing** (observed: the review's probes 4 and 8). Step 2 would have resolved
a case to 8192 by rebuilding the join through `key_for`. The join has no
source for the system and user text outside a live run. The best available
proxy, a cassette whose system starts with the case's instructions, resolves
**0 of 128 cases to 8192 only**: 112 to 12288 only, 9 to both, 7 to neither.
Over a 5 per cent sample of `case_runs`, 10206 rows, the rule would have moved
16 rows, which is 0.16 per cent.

**The write-off is a claim about history and the migration marks it as one.**
The migration writes a note naming the first `seq` after which the four
columns are measured. Before it they are a default. The review measured that
22.9 per cent of rows cannot be separated by any available evidence, and that
number goes in the note.

**The backfill is a one-shot script and it does not run inside
`open_dev_db`** (observed: the review's probe 11, 2026-09-21). The four
`ALTER TABLE ADD COLUMN` statements take 0.004 seconds in total, because
SQLite adds a column without rewriting the table. One `UPDATE` of 178901 rows
takes **4.72 seconds**, against sqlite3's default busy timeout of 5.0 seconds,
and `pytest.ini:18` sets `-n auto --dist loadfile`. A second worker that opens
the register during the backfill can raise `database is locked`.
`open_dev_db` adds the columns only.

**The register is republished after the backfill** (observed: the review's
finding 16). The register is not tracked by git, and
`rota/testkit/cassette_store.py:328` decides whether to publish by comparing
row counts. The migration changes no counts, so `status` would say there is
nothing to publish and another checkout would pull the pre-migration file. The
frame's closing status names the new manifest tag.

## 5. The door

(ruled: Roman, 2026-09-21: one door covers the ambient variables, so frames 54
and 60 share one repair)

**Three ambient variables join the cassette key without saying so**, not two.
`ROTA_MODEL` is frame 60's. `ROTA_NUM_CTX` is the first read's, and
`rota/HARDWARE_GUIDE.md:159` tells the reader to set it to 16384, which no
cassette holds. **`ROTA_PROFILE` is the review's, finding 8**:
`tests/rota/test_l1.py:46-54` reads it and sets the `think` pin, while
`tests/rota/test_l3.py:39` and `tests/rota/test_gauntlet.py:33` do not. So one
run under a profile records the same model at two different keys.

**The door compares the field tuple, never the key** (observed: the review's
finding 6). The suite builds register pins at six sites in three files, and at
every one the system and user text do not exist yet, so no key can be built
there. The door compares the ambient model, window, temperature and think pin
against `SELECT DISTINCT model, num_ctx, temperature FROM cassettes`.

**The door fires only when the run replays** (observed: the review's finding
7). `ROTA_L1=1 ROTA_MODEL=<new model>` is how a benchmark column is recorded,
and the register already holds 11 models recorded that way. A door that
refused a new tuple would refuse every first recording. So it refuses only
when both `ROTA_L1` and `ROTA_REFRESH` are unset, which is a replay.

**The door lives in `rota_serial_plugin.py`** (observed: the review's finding
9). `rota_serial_plugin.py:10-17` records that a directory conftest never runs
on the controller under xdist, and `pytest.ini:18` sets `-n auto`. A door in
`tests/rota/conftest.py` prints once per worker, or never. The plugin is
loaded with `-p`, before any conftest and before the workers boot.

**It refuses, and it does not warn.** A warning is what the repository has
today. The run proceeds, every cassette misses, `record_case_run` returns
without writing because `_is_unmeasured` fires at
`rota/llm/cassettes.py:360-361`, and `casestatus` filters the same rows out of
what it reads.

**The claim, narrowed to what was measured** (observed: the review's probe 10,
which copied the register and ran three green cases at
`ROTA_NUM_CTX=16384`). `case_runs` held 204058 rows afterwards, unchanged, and
`casestatus` still reported 107 green, 21 FAIL, 0 stale. **The register shows
no stale and no new red. The suite goes loudly red**, with every model-facing
test failing at `tests/rota/test_l1.py:164`. Revision 1 said the run was
silent. It is silent in the register and loud in the suite, and the register
is what an acceptance reads.

## 6. The report's default model, and what it does to frame 49

(observed: the holding session's own run of both commands at 41746ca,
2026-09-21; found by the review, finding 17)

`rota/tools/casestatus.py:142` sets `ap.add_argument("--model",
default="llama3.1:8b")`, and `status()` never reads `ROTA_MODEL`.

- `python -m rota.tools.casestatus` prints `11 failing, 0 provisional, 67
  stale, 0 never measured, 50 green`.
- `python -m rota.tools.casestatus --model qwen3:8b` prints `21 failing, 0
  provisional, 0 stale, 0 never measured, 107 green`.

**So frame 49's 72 stale is a default-model artefact and not prompt drift.**
Frame 49 records that the gate's baseline said zero stale while `casestatus`
said 72, and calls it a record that disagrees with itself. **Both numbers were
right.** The gate passes `qwen3:8b` through `FALLBACK_MODEL` at
`rota/tools/gate.py:40`, whose own comment already states the cause: "under
llama `casestatus.status` calls 62 qwen-green cases stale". The fact sat in a
comment and no frame read it.

**This reprices frame 54 and frame 49.** Ends-when 6, the true stale count, is
answerable today at zero cost: 0 stale and 21 failing under the suite's model.
The schema change buys the ability to keep that zero honest. It does not buy
the number. Frame 49 is no longer a 72-case re-record.

**The fix belongs to this frame**: `--model` defaults to the same model the
gate uses, or the tool refuses when no model is named.

## 7. The tests that pin it

Revision 1 listed six and the review found two that cannot fail.

1. **A `.tools` file edit makes a case read stale.** This replaces revision
   1's "a prompt-text change", which passes before the repair and after it,
   because a mode-prompt edit already stales a case today.
2. A `num_ctx` change makes a case read stale.
3. A `think` pin change makes a case read stale, with the value coming from
   `ROTA_PROFILE` through `_think_for`.
4. A native-protocol recording does not answer for a text-protocol run.
5. **A named row carries 12288 after the migration.** This replaces revision
   1's before-and-after count comparison, which matches by construction and
   needs a 780 MB copy.
6. A replay whose ambient variables build a tuple the register does not hold
   is refused, and the message names the variable.
7. **A recording run is not refused.** `ROTA_L1=1` with a new model passes the
   door.
8. `open_dev_db` migrates an old database, and migrating twice is a no-op.
9. All four writers stamp the same columns, `rota/cli.py:612-621` included.
10. Frame 60's moved clause: the report's model default does not silently
    differ from the register's.

## 8. The acceptance

- The gate green before the commit, the stale line read **under a named
  model**.
- The true stale count measured and recorded, replacing the 72 in frame 49.
- A read-only diff review on a worktree at the commit, because the frame
  changes the schema.
- The register republished, and the closing status names the manifest tag.
- No night walk. `case_runs` has four writers and four readers, at
  `rota/cli.py:616`, `rota/cockpit/progress.py:634-651`,
  `rota/llm/benchmarks.py:35` and `rota/tools/triage.py:104`. A grep over
  `rota/roles/` and `rota/design/` returns nothing, so no seat and no runner
  reads it, and every reader names its columns. The no-walk conclusion
  survives the review.

## 9. The system text, and the clone

**Ruled by Roman, 2026-09-21**: "clone this as a backup legacy dB and migrate
over what's useful, full re-record is approved if necessary."

This is a fourth answer and it is better than the three that were offered. It
separates two things the frame had joined: **the record of what the model
did**, and **the evidence that gates an acceptance**. The clone keeps the
first for ever. The new register holds only the second.

**So ends-when 1 closes in full.** `case_runs` gains a fifth column,
`system_hash`, over the whole system text that the model receives. A tools
edit then makes a case read stale, which is correct.

**And frame 55's objection is answered.** That frame observed that a
re-record can spend a green the live model does not give back. With the clone
the green is not spent. It moves into history, where it stays readable and
where it stops gating anything.

### 9.1 The clone

`tests/rota/cassettes.db` is copied, whole and unaltered, to a legacy
database. Nothing is deleted from it and nothing is written to it after the
copy. Its name and its manifest tag go in the frame's closing status. **The
copy happens before the first schema change**, so a failed migration costs
nothing.

### 9.2 What migrates, and what does not

**Every cassette migrates as it stands.** A cassette is already keyed by the
whole text, so it is evidence about exactly one input and it needs no repair.

**A `case_runs` row migrates when the cassette it used can be identified**,
because the whole-text hash is then computable from that cassette's `system`.
The join is the review's: match the row's transcript completion against a
cassette's completion, inside the row's own case and model.

**A row whose cassette cannot be identified stays in the legacy database
only.** It is history and it is not evidence, because nothing can say what
text it measured.

**The migration reports its own numbers**, and they go in the closing status:
rows migrated, rows left behind, and cases left with fewer than their
threshold of runs. The review's proxy measured about 77 per cent identifiable
and 22.9 per cent not separable. **That is the review's number on a 5 per cent
sample and the migration measures the real one.**

### 9.3 The re-record

(ruled: Roman, 2026-09-21, "full re-record is approved if necessary")

A case left below its threshold after the migration is re-recorded. The price
is wall time on a quiet machine and not tokens, which frame 49 already
recorded. **The re-record runs under a named model and a named window**, and
the frame's closing status names both.

**Frame 49's re-records fold into this migration.** That frame's ends-when
asked for the 72 to be re-recorded or written off case by case. Section 6
shows the 72 was a default-model artefact, and this section covers whatever
the migration leaves short. Frame 49 keeps only the question of what the 21
failing cases mean.

### 9.4 What this costs that revision 2 did not

The frame grows by the clone, the fifth column, the migration script and the
re-record. It shrinks by the backfill, which is now a migration and not a
write-off, and by frame 49's separate re-record pass, which folds in. The
holding session prices the difference in the frame's status line before the
implementer starts.

## 10. What revision 2 changed, and why

| Section | Change | Source |
| --- | --- | --- |
| 2 | `prompt_hash` covers the mode prompt. The cited comment is wrong. | review finding 1, re-measured by the holding session |
| 2 | The uncovered text is the runner prose and the tool list, 117 of 117 cases, and it has moved for 42 of them. | the holding session's measurement |
| 3 | Each of the four columns gets a named source for `status()`. | review finding 12 |
| 3 | `load_id` stays out of the match, with the two reasons. | review finding 4 |
| 4 | Step 2 deleted. The 8192 resolution fires on 0 cases. | review findings 3 and 5 |
| 4 | The backfill is a one-shot script, not part of `open_dev_db`. | review finding 15 |
| 4 | The register is republished afterwards. | review finding 16 |
| 5 | `ROTA_PROFILE` is a third ambient variable. | review finding 8 |
| 5 | The door compares the field tuple, not the key. | review finding 6 |
| 5 | The door fires only on a replay, so a first recording passes. | review finding 7 |
| 5 | The door lives in the plugin, not the conftest. | review finding 9 |
| 5 | The silence claim is narrowed: silent in the register, loud in the suite. | review finding 10 |
| 6 | New section. The report's default model is the 72. | review finding 17 |
| 7 | Tests 1 and 5 replaced. Four tests added. | review findings 11, 12 and 13 |
| 8 | The four writers and four readers are named. | review finding 14 |
| 9 | New section. The system text is Roman's call. | review finding 2 |
| 9 | **Revision 3**: Roman ruled a clone, a migration and an approved full re-record. Ends-when 1 closes in full and `system_hash` is added. | ruled: Roman, 2026-09-21 |

**Two findings are recorded and left outside the frame.** The review's finding
18, that `tests/rota/conftest.py` defines `pytest_configure` twice so the
first is dead, is already parked in `plans/stack.md` from frame 30's design
review. The review's finding 19, that `routed_pins` can move the key after the
stamp, is inert today because no case seeds a profile, and it becomes live the
day one does.
