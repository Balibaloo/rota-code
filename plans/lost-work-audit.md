# Lost-work audit, 2026-09-13

Roman found on 2026-09-13 that the stray-touch detector (the committed
diff checked against the Architect's prediction) was described as built
and was not on `rota/foundation`. It had been built on 2026-09-03 on
`rota/touch-divergence`, a branch the history rewrites of 2026-08-28 and
2026-08-30 left behind. This audit asks what else is like it. Two sweeps,
both read-only: every branch and stash against `rota/foundation`, and
every "built" claim in the plans and rulings against the code.

The stray-touch detector itself is ported and completed in bb7c3d2
(`touch_strays`, `touch_strayed`, `touch_mistaken`, `batches.judge_touch`,
the merge hold).

## 1. Claims with no code behind them

| Source | Claim | Finding | Disposition |
|---|---|---|---|
| `rota/COMPLETION.md:692` | The hello-world walk "becomes `S0-hello-world`, the permanent floor of the story tier". | No case, test or tier of that name exists. The S0 walks live in `probes/s0_walk.py` and the walk log. | Doc: the sentence is withdrawn in the documentation pass. The floor is the walk row in `tests/rota/walks.jsonl`. |
| `rota/DECISIONS.md:55-57` | "A reference goes stale; the drift predicate wakes the role whose artefact cited it." | No predicate reads `references_.content_hash`. The column is written and never compared. | Owed, small: a `reference_drift` predicate that compares the stored hash to a refetch and wakes the citing owner. Post-core unless a walk needs it: the Researcher is on the desk, the refetch is the world. |
| `rota/LAWS.md:172-173` | Law 6: "only exhaustion at the principal converts to a ledger assumption." | The only ledger writer is `ledger.log`. Nothing converts an exhausted question at the principal into a row. | Superseded by the principal-flow ruling of 2026-09-13: there is no silence, a page is a hold or a note. The law's sentence is rewritten in the documentation pass to say that. |
| `rota/LAWS.md:173-174` | Law 6: "Cycles collapse by routing the counter-question into the suspended session." | Nothing resumes a suspended session (see law 5 below). | Post-core. Law 6 is rewritten to what holds: the ladder and the attempt caps bound a cycle; nothing resumes. |

## 2. Claims that are partial

| Source | Claim | Exists | Missing | Disposition |
|---|---|---|---|---|
| `rota/LAWS.md:163-168` (law 5) | Suspension is a cache; receipts allow a patched resume. | `checkpoints` table, the write branch in `session_commit`, `lifecycle.defer` invalidation, `checkpoint_invalid`, `sweep_checkpoints`. | No session ever sets `SessionResult.checkpoint`; nothing resumes from one. | Post-core. The law is rewritten to what holds: a deferred batch restarts from its rows. |
| `rota/LAWS.md:155-156` (law 4) | Boot hands the head-commit divergence to the woken role. | `boot.reconcile_worktrees` computes it. | It reaches only the boot report line. | Owed, small: the divergence goes into the Developer's `batch_start` wake detail. Core, because a restart mid-batch is ordinary. |
| `plans/responsibility-allocation.md:40` | C2 verified on `batch_dep_facts`. | The table and `schedule_order`'s reader. | No op writes it; `batches.depend` is listed unbuilt in COMPLETION core item 10. | Known. `plans/principal-flow.md:375` records it as a dead end; the allocation grade is corrected in the documentation pass. |
| `plans/responsibility-allocation.md:31` | B3 verified with the reference hash comparison. | The area-hash half is real. | The reference half is table 1, row 2. | Grade corrected with the drift item. |
| `rota/DECISIONS.md:768-769` | `references` carries a retrieval sequence. | `content_hash`. | No sequence column. | Doc: rewritten to the columns that exist. |
| `rota/DECISIONS.md:1045` | `code.surface` is the candidate lens. | `code.callables` is that lens. | The name in the ruling is the old one. | Doc: renamed in the documentation pass; `runner.py:1157` comment likewise. |
| `rota/LAWS.md:357` (law 13) | A build check finds no date, duration or timestamp column in the schema. | `test_ordering_contains_no_time` checks `schedule_deps` only. | No test scans the schema; `runtime_processes.started_at` exists and is asserted present by `test_docs.py:238`. | Owed, small: a test that scans `schema.sql` and allows the one runtime-bookkeeping column by name. |
| `plans/amendment-and-conflicts.md:329-330` | The prose-area mechanism is pinned by a named test. | The mechanism (`@prose`, `@prose:<path>` wakes). | The pin is `test_examples_attach_like_tests_and_docs_trip_the_wire`, a different name. | Doc: the name is corrected. |

Two more, doc-level: `LAWS.md` cites `rota/lifecycle.py` and `rota/config.py`,
now under `rota/core/`, and a `HANDOFF.md` that is not in `rota/`.

The audit did not find a second lost mechanism of the stray-touch kind in
the plans: every predicate, mode, tool, door, table, register case and test
named in the P4, A1, seat-exchange, R11, R13, model-setup and walk-door
claims resolves to code. The gaps are the oldest doctrine in LAWS.md and the
reference-drift story in DECISIONS.md.

## 3. Branches and stashes

Method: `git cherry` (patch-id equivalence) against `rota/foundation` for
every branch with commits since 2026-08-20, then for every commit it
reports as absent, the foundation commit with the same author timestamp
and a comparison of file lists and per-file diffs; merges by the same
timestamp rule. Subjects were not used: the Conventional Commits rewrite
reworded them and the 2026-08-28 wipe left 145 empty.

| Branch or stash | Commits since 2026-08-20 | Finding |
|---|---|---|
| `rota/foundation-cc-rewrite`, `rota/seat2`, `origin/rota/foundation` | 228, 424, 235 | Pure ancestors of foundation. Present. |
| `rota/foundation-wiped-20260903` | 225 (42 merges) | Every commit and merge has a foundation twin. Present. |
| `rota/foundation-pre-filter-20260828` | 145 | 38 patch-ids differ; each has a twin with the same timestamp and file list, and the only differing file is `tests/rota/cassettes.db`, which the 08-28 filter rewrote. Present. |
| `rota/touch-divergence` | 226 | One commit absent, `ed44aed` (the stray-touch detector). Ported as a re-implementation in `bb7c3d2` on 2026-09-13. |
| `stash@{0}` "Stop gate" (2026-08-30) | | A stop after the outbound message and a chat-plus-work intake. Superseded: the stop is `runner.py`'s oneshot break (`34b48c4`, `316f8ec`) and the fork is `brief.intake` (`4a58648`). Can be dropped. |
| `stash@{1}`, `{3}`, `{4}`, `{5}` (May 2026, `main`) | | Pre-rota TUI work; the substance is in the tree. |
| `stash@{2}` "Analysis breakdown" (2026-05-12, `main`) | | `src/core/workflow_phases.py` (621 lines, `PhaseOrchestrator` and friends) and 164 lines in `analysis_tools.py`. Absent everywhere. Pre-rota and outside the rewrite window; the only item with no descendant. Not rota's. |

Nothing from the rota line is lost besides `ed44aed`. The caveat: patch-id
equivalence proves a change entered foundation's history, not that a later
foundation commit kept it; that is a foundation decision and was not
audited.

## 4. What this audit changes

- The map document the documentation pass produces cites code for every
  mechanism it names, and a claim without a citation is not written.
- COMPLETION's "core by capability" list gains the two small owed items
  above (the boot hand-off, the law-13 schema test) and names the
  reference-drift predicate as post-core.
