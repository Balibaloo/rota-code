# One composition of the system text: design record

Frame 63, one composition of the system text. Written 2026-09-22 by session
`590c7382`, peer name rota-dc. Meta workflow.

This record is the input to the frame's design review. It settles what the
repair is, and it names the two questions the review must answer.

## 1. The fault, in one paragraph

A cassette is keyed by the whole system text the model receives. The
register's report matches a result row on the case id, the brief's
`prompt_hash`, the model, the window, the temperature, the protocol and the
extras. It does not match on the system text. The brief is a strict prefix of
the system text and never the whole of it. So an edit to a `.tools` file, a
tool signature or the runner's session prose moves the cassette key, leaves
`prompt_hash` alone, and the case reads green while the suite cannot replay it
(observed: frame 54's measurement over 117 of 117 single-session cases,
2026-09-21).

Frame 54 added the `system_hash` column and writes it on every row. It could
not match on it, because no reader could compose the system text.

## 2. What the frame's first read measured

All five numbers below are observed on 2026-09-21 and 2026-09-22 by this
session, from the register at `tests/rota/cassettes.db` and the tree at
commit `fcbdd65`.

**The re-record is zero.** 121 single-session cases and 7 chains compose a
system text whose hash every one of their matching rows already carries. No
case falls below its threshold when the match widens. The migration read each
row's hash off the cassette that earned it, so the register is already keyed
to the text the tree composes now.

**The fault is real and the widened match catches it.** One extra keyword on
one advertised signature moves the system hash from `977a50befc0595d2` to
`00e96f24768b0dfc`. `prompt_hash` does not move.

**A second reading of the case is the wrong design.** A hand-rolled
composition that skipped the fixture agreed with the real one on 102 of 121
cases. 13 raised on a foreign key and 6 gave a different hash. The repair must
share the setup, not re-derive it.

**The system text does not need the session.** It needs the sandbox. With the
user prompt's two inputs stubbed out, `push_working_set` and
`resolve_inbound`, the composition is byte-identical for 121 of 121 cases.

**And it is cheap.** Over an in-memory database, with no git worktree,
composing all 121 single-session cases costs **1.01 seconds**, 8.3 ms a case.
The same composition through the full `run_case` setup costs 67 seconds. The
67 seconds is the session's setup and not the text's.

## 3. The repair

Revision 2, 2026-09-22 01:28. The design review answered both questions and
found two high faults. Section 3 and section 4 are rewritten. Section 9 lists
what changed and why.

Four changes, and the fourth is new.

**3.1 `build_prompt` splits.** A new `compose_system(role, sb, *, instructions,
oneshot) -> str` holds every line of the system text. `build_prompt` calls it
and keeps the user prompt, so `run_session` reaches the same text by the same
path it uses today. No behaviour moves.

**`compose_system` is pure only if the sandbox already carries `_order`**
(observed: the design review's read of `rota/core/runner.py:1976`,
2026-09-22). `run_session` sets `sb._order` after `sandbox.build` returns, and
`sb.signatures()` reads it. So the extracted setup in 3.2 sets `_order` before
it returns, and no caller may set it afterwards.

**`oneshot` is `os.environ.get("ROTA_ONESHOT")`**, read at
`rota/core/runner.py:2008`. The reader reads the same variable the same way.

**3.2 The sandbox setup is extracted from `run_session`.** The block at
`rota/core/runner.py:1966-1989` becomes one function. `run_session` calls it.
So does the new reader, and so does the cockpit's prompt preview in 3.5.

**Its signature takes more than a connection and a wake** (observed: the
design review's probe 2, 2026-09-22). `mode` is the caller's, and
`L1-TE-challenge-an-unusable-item` declares `mode: readonly`, which drops
every write tool from the signatures. `batch_id` comes from
`_batch_of(conn, wake)`. `area` comes from the caller's own rule. So the
function takes `mode`, `batch_id` and `area` as keywords. `session_id` and
`entry_id` reach no line of the system text.

**3.3 A reader composes from a case.** A new `system_text_for(case)` in
`rota/testkit/fixtures.py`, beside `run_case`, seeds an in-memory database the
way `run_case` does, builds the wake the way `run_case` does, calls the
extracted setup, and calls `compose_system`. It stops there. It never pushes a
working set, never resolves an inbound message, never makes a git worktree and
never calls a model.

**One rule it must carry.** The brief comes from
`fixtures.instructions_for(case)`, which keys on `mode_of(case)`. The allow
list comes from `_mode_key(wake, conn)`. The two rules agree on all 121
single-session cases today (observed: the design review's probe 2,
2026-09-22). They are two rules and not one, so the reader states which it
uses where.

**3.4 The match widens, and only when the register can answer.**
`matching_runs` adds `AND system_hash = ?`.

**`carries_the_key` is not the guard for this, and using it would report every
case stale** (observed: the design review's probe 5, 2026-09-22).
`carries_the_key` asks whether the columns exist. `open_dev_db` adds them with
`DEFAULT ''` and backfills nothing, so a register written before frame 54
answers True with an empty hash on every row. `casestatus.status` never
consults `carries_the_key` at all, so its `keyed` is always True. And
`tests/rota/cassettes.db` is gitignored and pulled from a published snapshot
that carries no schema version, so this is a live case and not a theory.

So the repair adds a second predicate: **does any row carry a non-empty
`system_hash`.** The match widens only when it does.

**The match also excludes `''` and `'unbuilt'` explicitly**, with a comment,
the way the `no cassette for` rows are excluded. A crashed session stamps
`unbuilt`. Dropping such a row silently shrinks a case's denominator and moves
its count against its threshold. The register holds zero such rows today
(observed: the design review's probe 1, 2026-09-22).

**3.5 The cockpit's prompt preview joins the one composition.** This is new,
and it is the second high fault. `rota/cockpit/progress.py:478-484` builds its
own sandbox for the prompt preview a person reads. It passes no `mode`, no
`onboarding` and no `_order`, and its area rule is `case.get("tick") ==
"survey"` where the runner's is `ONBOARDING_TICKS`. **Its tool list differs
from the runner's for 18 of 121 cases** (observed: the design review's probe
4, 2026-09-22). So the tree already holds the second composition this frame
exists to remove. `message_text` calls the extracted setup.

## 4. The two questions, answered

**Question 1, chains: the report replays, and the design's premise was
wrong.** A chain's recorded `system_hash` is not always over both legs.
`run_chain` returns one leg's text when leg two never wakes, at
`rota/testkit/fixtures.py:1069`, `:1081` and `:1094`.
`L3-a-challenge-reaches-the-role-that-can-answer-it` is such a chain, and its
hash `ae4fac8c4e6a76ae` covers leg one alone (observed: the register and this
session's own composition, 2026-09-21 and 2026-09-22). **So the column means
the system texts the run actually reached.** Matching a chain on leg one alone
would compare a one-leg digest against a two-leg digest for six of seven
chains, agree by accident on the seventh, and force all seven to re-record.
Only a replay reproduces how far a chain got.

**The replay runs in `casestatus.status` and in the gate, and never in the
cockpit's panel.** `L3-a-failed-verdict-turns-into-a-fix` declares `repo:`, so
a replay shells out to git. A git worktree for an HTTP request is not
acceptable at `rota/cockpit/progress.py:234`. That panel keeps the narrow
match for chains and labels it.

**One known weakness of a replaying report, stated so nobody is surprised.** A
replay that dies for a reason that is not about the text still carries a real
`outcome.system`. The report can then read a matching hash out of a broken run
and print green. A composing report cannot do that. The chains are 7 of 128,
and this is the price of matching what the column actually means.

**Question 2, the import: `system_text_for` lives in the testkit.**
`rota/tools/casestatus.py:41` and `rota/cockpit/progress.py:26` already import
`rota/testkit/fixtures.py` at module scope, and `wanted_pins` already calls
`fixtures.instructions_for`. No rule in `CONTRIBUTING.md`, `LAWS.md` or the
briefs names a boundary (observed: the design review's grep, 2026-09-22). A
third module would split the composition from the setup it must share, which
is the one thing this frame exists to stop. `rota/tools/gate.py:129` keeps its
deferred `from . import casestatus`, so importing the gate still opens no
database.

## 4a. What this frame does not close, and why it is a frame

**`system_hash` is not the whole cassette key.** `key_for(system, user, pins)`
hashes both halves, and `pins.with_prompt(system + user)` at
`rota/core/runner.py:2016` carries both. So a drift in the **user** prompt
still moves the cassette key, leaves `prompt_hash` and `system_hash` alone,
and leaves a case green that the suite cannot replay. The user prompt is
composable from a case, because its inputs are `push_working_set` and
`resolve_inbound` over the case's own seeded database. It costs more setup and
it needs the worktree for the ten `repo:` cases this frame's read avoids.

This frame does not do it. It is pushed as its own frame, so the closing
status does not read as if the key is now whole.

## 5. What this costs each reader

**Four readers, not three.** The design review found the fourth (observed:
`python -m rota.tools.map` and the review's probe 4, 2026-09-22).

| Reader | Where | Added cost |
| --- | --- | --- |
| the gate's stale line | `rota/tools/gate.py:131` | about 1 s, against a 579 s gate. Chains replay here |
| the cockpit's L1 panel | `rota/cockpit/progress.py:234` | about 1 s per call, and no replay. The panel is served at its own endpoint and not at `/state.json`, so it is not on the fast poll |
| the CLI report | `rota/tools/casestatus.py` | about 1 s, plus 5.4 s when the chains replay |
| the cockpit's prompt preview | `rota/cockpit/progress.py:478` | none. It already builds a sandbox. It builds the wrong one for 18 of 121 cases, and this repair corrects it |

## 6. The acceptance

Revision 2. Lines 1, 4 and 6 are rewritten, because the review showed that
line 1 was already false, line 4 passed on one easy case, and line 6 could not
fail.

1. **Four call sites build a sandbox for a prompt, and all four go through the
   extracted setup**: `run_session`, `run_chain` through `run_session`,
   `system_text_for`, and `progress.message_text`. A test asserts that the
   runner's sandbox and the preview's sandbox report the same `signatures()`
   for every single-session case. That test fails today for 18 of 121.
2. The report matches on `system_hash`, and only when a row carries one.
3. A test asserts that a tools edit makes a case read stale, and that the same
   edit leaves `prompt_hash` unchanged.
4. A test asserts that `system_text_for(case)` equals the system text the run
   records, **parameterised over every case that has a matching row**. The set
   must include the `readonly` case, a `repo:` case, an area case, and the
   cases whose mode declares a tool order.
5. The gate reads zero stale and zero new reds after the change, because the
   measured restale count is zero. **This holds for the migrated register on
   this machine, and not for a register pulled from the published snapshot.**
   Acceptance 2's second predicate is what makes a pulled register safe.
6. **The whole report runs in under 10 seconds**, chains included, measured
   and named in the closing status.

## 7. What is not in this frame

The 21 failing cases stay failing. Frame 49 closed on the count and not on the
causes. Frame 55, a recorded green does not reproduce live, is the next frame
in batch A and this frame does not touch it.

The user prompt's half of the cassette key is section 4a, and it is pushed as
its own frame.

**`migrate_register.py` does not run again for this frame** (observed: the
design review's read of its `skip = chain_ids()` at line 242, 2026-09-22). It
skips every chain row. The seven chains carry real hashes because they were
re-recorded after the migration. A later reader who re-runs that tool would
drop the chains again.

**`trust()` still groups on `prompt_hash` and `load_id` only**
(`rota/llm/cassettes.py:495`). It keeps reading rows the widened match
excludes. That is not a fault of this repair, and it is named so a reader does
not find it and call it one.

## 8. The two faults the review found, in one line each

- **`carries_the_key` is the wrong guard**, and using it would report every
  case stale on a pulled register. Section 3.4.
- **A second composition is already in the tree**, at the cockpit's prompt
  preview, wrong for 18 of 121 cases. Section 3.5.

## 9. What revision 2 changed

- Section 3.1 states that `_order` must be set before `signatures()` reads it.
- Section 3.2 corrects the extracted function's signature. A connection and a
  wake cannot render the `readonly` case.
- Section 3.3 names the two mode rules, which agree today and are still two.
- Section 3.4 replaces `carries_the_key` with a predicate that asks whether
  any row carries a hash, and excludes `''` and `'unbuilt'`.
- Section 3.5 is new. The cockpit's prompt preview joins the one composition.
- Section 4 answers both questions, and corrects the premise under question 1.
  A chain's hash is not always both legs.
- Section 4a is new. The user prompt is the other half of the cassette key,
  and it becomes its own frame.
- Section 5 lists a fourth reader.
- Section 6 rewrites three of the six acceptance lines.
