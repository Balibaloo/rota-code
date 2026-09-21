# The register's key: design record

Frame 54, the register's match is narrower than the cassette key, with frame
60's repair folded in. Written 2026-09-21 by session 75f21e35, peer name
rota-36, after the frame's first read. Meta workflow.

Read this with the frame's first read in `plans/stack.md`, which carries the
measurements this design answers.

## 1. The fault, in one paragraph

A recording is identified by seven things. A result is identified by three.
Four of the seven have no column in `case_runs` to hold them. So the report
cannot match what the cassette key covers, and it never could. One narrow key
gives two opposite symptoms: a case reads stale when it is green, and a case
reads green when the suite cannot replay it.

## 2. The two keys, field by field

(observed: `rota/llm/cassettes.py:105-120`, `rota/llm/llm.py:47-92`,
`rota/tools/casestatus.py:75-82`, 2026-09-21)

| Field | In the cassette key | In `case_runs` | Matched by the report |
| --- | --- | --- | --- |
| model | yes | yes | yes |
| temperature | yes | no | no |
| `num_ctx` | yes | no | no |
| protocol, text or native | yes | no | no |
| the system text | yes | no | no |
| the user text | yes | no | no |
| extras: `max_tokens`, `top_p`, `seed`, `repeat_penalty`, `think` | yes, when set | no | no |
| `case_id` | no | yes | yes |
| `prompt_hash` | no | yes | yes |
| `load_id` | no | yes | no |

**`prompt_hash` is not in the cassette key.** It is a sha256 of
`fixtures.instructions_for(case)`, first 16 characters, written by
`record_case_run`. It fingerprints the role's instructions and nothing else.
The mode prompt and the case's own user text move without changing it.

## 3. What the design adds

`case_runs` gains four columns, each with a default that is true of every
existing row after the backfill of section 4:

| Column | Type | Default | Why |
| --- | --- | --- | --- |
| `num_ctx` | INTEGER | 12288 | The largest single cause of a false state. It is in the key and it is set by an ambient variable. |
| `temperature` | REAL | 0.0 | Every cassette in the register is at 0.0, so the column is cheap and it closes the field. |
| `protocol` | TEXT | `'text'` | A native recording and a text recording answer differently. The key separates them and the report must too. |
| `extras` | TEXT | `'{}'` | The set optional pins, as the same JSON `Pins.extras()` builds. `think` is the live one: finding 81 showed a Tester answer change completely on it. |

The report's `WHERE` clause then matches `case_id`, `prompt_hash`, `model`,
`num_ctx`, `temperature`, `protocol` and `extras`.

**The system and user text stay out of the match, and `prompt_hash` stays in
it.** Storing the full text per result row would duplicate the cassette table
at 204058 rows. `prompt_hash` is the proxy, and widening what it covers is
section 6.

## 4. The backfill

(ruled: Roman, 2026-09-21, asked with two other answers)

The existing 204058 rows are written off, not re-recorded. A re-record can
spend a green the live model does not give back, which frame 55 observed on
2026-09-20.

1. Every row takes `num_ctx` 12288, `temperature` 0.0, `protocol` `'text'`,
   `extras` `'{}'`.
2. **A row whose cassette is findable at 8192 by its own text takes 8192.**
   3513 of 18604 cassettes are at 8192. The join is not stored, so it is
   rebuilt: for a case, take its system and user text, call `key_for` at 12288
   and at 8192, and see which key the `cassettes` table holds. A case that
   resolves to 8192 backfills its rows at 8192.
3. A case that resolves to neither, or to both, keeps 12288 and is listed in
   the migration's own report. **The list is the record**, and the count goes
   in the frame's closing status.

**The write-off is a claim about history and it is marked as one.** The
migration writes a row in a note, not only in the schema, so a later reader
knows the four columns before a given `seq` are a default and not a
measurement.

## 5. The door

(ruled: Roman, 2026-09-21, asked with two other answers: one door covers both
variables, so frames 54 and 60 share one repair)

Two ambient variables join the cassette key without saying so.
`ROTA_MODEL` is frame 60's. `ROTA_NUM_CTX` is this read's, and
`rota/HARDWARE_GUIDE.md:159` tells the reader to set it to 16384, which no
cassette in the register holds.

The door runs where the suite builds its pins. It compares the key the run
would build against what the register holds, and it refuses with the
variable's name when the register holds nothing at that key.

**It refuses, and it does not warn.** A warning is what the repository has
today: the run proceeds, every cassette misses, `record_case_run` writes
nothing because `_is_unmeasured` returns early at
`rota/llm/cassettes.py:360-361`, and `casestatus` then reports the previous
greens with no stale and no new red. A whole suite run in which nothing
replayed leaves the register saying green. That is the state the door exists
to make impossible.

**The refusal names three things**: the variable, the value it holds, and the
values the register does hold. A reader who set `ROTA_NUM_CTX=16384` on the
guide's instruction must be told that the register is at 12288 and 8192.

## 6. What this design does not do

- **It does not widen `prompt_hash`.** The mode prompt is still outside it, so
  a mode prompt edit still leaves a case reading green. The fix is to hash the
  composed prompt instead of the role's instructions, and that restales every
  case at once, which is frame 49's work and not this frame's. The obligation
  is named here so it stays countable.
- **It does not re-record anything.** Frame 49 owns the re-records, and it
  waits on this frame for the true count.
- **It does not touch the nights.** The register runs at 12288 and the nights
  at 16384, and closing that gap needs recordings that do not exist. This
  frame makes the gap visible. Frame 49 decides what to do about it.

## 7. The tests that pin it

1. A prompt-text change makes a case read stale. This is the frame's own
   ends-when line 4, and it is the symptom nothing could catch.
2. A `num_ctx` change makes a case read stale.
3. A `think` pin change makes a case read stale.
4. A run whose ambient variables build a key the register does not hold is
   refused, and the message names the variable.
5. The backfill leaves every pre-existing green readable. Run the report
   before and after the migration on a copy, and the counts match.
6. A native-protocol recording does not answer for a text-protocol run.

## 8. The acceptance

- The gate green before the commit, the stale line read.
- The true stale count measured and recorded, replacing the 72 in frame 49.
- A read-only diff review on a worktree at the commit, because the frame
  changes the schema.
- No night walk. The register is meta-workflow tooling and it is not on the
  seats' delivery path.
