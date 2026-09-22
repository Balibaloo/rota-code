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

Three changes, and the third is the point.

**3.1 `build_prompt` splits.** A new `compose_system(role, sb, *, instructions,
oneshot) -> str` holds every line of the system text. `build_prompt` calls it
and keeps the user prompt, so `run_session` reaches the same text by the same
path it uses today. No behaviour moves.

**3.2 The sandbox setup is extracted from `run_session`.** The block that
builds `sb`, sets `sb._order` and derives the mode key becomes one function
that takes a connection and a wake. `run_session` calls it. So does the new
reader. This is the line that makes it *one* composition: the measured
alternative, a reader that re-derives the wake and the allow list for itself,
was wrong on 19 of 121 cases.

**3.3 A reader composes from a case.** A new `system_text_for(case)` in the
testkit seeds an in-memory database the way `run_case` does, builds the wake
the way `run_case` does, calls the extracted setup, and calls
`compose_system`. It stops there. It never pushes a working set, never
resolves an inbound message, never makes a git worktree and never calls a
model.

**3.4 The match widens.** `matching_runs` adds `AND system_hash = ?` under
`keyed`. The wanted hash comes from `system_text_for(case)`.

## 4. The two questions for the review

**Question 1: how a chain is matched.** A chain's recorded `system_hash` is
over both legs joined. Leg two's wake comes from what leg one actually did, so
no reader can compose it from the case alone. Two answers:

- **Replay the chain from the cassettes.** No model call. Measured at 5.4
  seconds for the 7 chains, on disk with the worktree. A replay that hits a
  missing cassette means the case is stale, which is the right answer. The
  cost is that a report now replays, and a report that replays can fail for
  reasons that are not about the question it was asked.
- **Match a chain on leg one's hash alone.** Cheap and composable from the
  case. It misses an edit that moves only leg two's tools.

**This session recommends the replay**, because the column already means both
legs and a narrower match would be a third definition of the key. The review
should say whether the report may replay.

**Question 2: where `system_text_for` lives.** It belongs beside `run_case` in
`rota/testkit/fixtures.py`, because it shares that function's setup. But
`rota/tools/casestatus.py` and `rota/cockpit/progress.py` would then import
the testkit to read a register. The review should say whether that import is
acceptable or whether the composition moves to a third module that both the
testkit and the tools import.

## 5. What this costs each reader

Three readers call the match (observed: `python -m rota.tools.map`, 2026-09-22).

| Reader | Where | Added cost |
| --- | --- | --- |
| the gate's stale line | `rota/tools/gate.py:131` | about 1 s, against a 579 s gate |
| the cockpit's L1 panel | `rota/cockpit/progress.py:234` | about 1 s per call. The panel is served at its own endpoint and not at `/state.json`, so it is not on the fast poll |
| the CLI report | `rota/tools/casestatus.py` | about 1 s, or 6.4 s if chains replay |

## 6. The acceptance

1. One function composes the system text, and `run_session` and the report
   both call it. No second composition exists in the tree.
2. The report matches on `system_hash`.
3. A test asserts that a tools edit makes a case read stale, and that the same
   edit leaves `prompt_hash` unchanged.
4. A test asserts that the composed hash for a case equals the hash the suite
   records for that case.
5. The gate reads zero stale and zero new reds after the change, because the
   measured restale count is zero.
6. The report's own runtime is named in the closing status, measured.

## 7. What is not in this frame

The 21 failing cases stay failing. Frame 49 closed on the count and not on the
causes. Frame 55, a recorded green does not reproduce live, is the next frame
in batch A and this frame does not touch it.
