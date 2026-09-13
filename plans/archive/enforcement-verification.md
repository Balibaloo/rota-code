# Phase 5 — enforcement verification

The claims "law N is checked by X" from LAWS.md, audited: does the check
exist, does it run, does it catch what it claims? Baseline: full suite run
2026-09-02, every structural/enforcement test green (1354 passed; the 9
non-passes are model cases, classified in
[feasibility-audit.md](feasibility-audit.md)).

| law | claimed check | verified | strength |
|---|---|---|---|
| 1 single writer | `graph.check_writers` | exists ([graph.py:342](../rota/design/graph.py#L342)), green | strong — boot assertion |
| 2 conclusions travel | `findings` has no why column | schema read: id/batch/constraint/sha/status/grain/version only | strong — schema-enforced |
| 3 derived contacts | `graph.check_contacts` | exists (graph.py:354), green; derived = declared, zero exceptions | strong |
| 4 session = message | `db.session_commit` one transaction | sole sanctioned write path (db.py:6), chaos-tested (kill mid-session leaves world untouched) | strong |
| 5 suspension is cache | `sweep_checkpoints` | exists, checkpoint_invalid predicate drains | adequate |
| 6 escalation climbs | `exhausted` climbs LADDER one rung | read: rung derived from sent messages, not stored | strong |
| 7 budgets declared | `config.SETTINGS`, unknown key errors | read: UnknownSetting raised, values validated, history kept | strong |
| 8 gates in review order | `lifecycle.mergeable` returns reason | exists; harness → critic → architect order | adequate (order read, not exercised here) |
| 9 amendment cascade | `cascade_wakes`, prioritize amends=False | exists, chaos-covered | strong |
| 10 inquiry free | readonly sandbox builds no writers | sandbox mode="readonly"; a reached-for write is an ordinary tool error | strong |
| 11 provenance explicit | NOT NULL CHECK | schema-enforced | strong |
| 12 constraints external | `check_structure` | exists; structural review by grain intersection | adequate — trigger completeness inherits S2 |
| 13 time is not a concept | no time column in schema | verified: `ts_order` is "sequence, not a timestamp"; the one wall clock lives in the fetch cache, declared evidence | strong |
| 14 identity from content | `test_identity.py` | 10 tests; NATURAL_KEYS classification, phantom refusal, pinned unkeyed list | strong |

Plus the meta-check: every state has a way out — `check_terminal_states`,
`check_predicates_can_fire`, `check_states_are_reachable`,
`check_predicates_wake_real_roles` all live in predicates.py and run green.

## The two soft spots (both already filed as findings)

- **Gate presentation is discipline, not enforcement (P6, revised).** No
  validator checks that a `present_principal` at signoff carries the
  lineage's open assumptions — the submit brief demands it ("never
  omitted"), and the backstops are mechanical: `tick_agenda` re-offers
  every open ledger entry whenever the principal is present with nothing
  pending, and no assumption can close without a decision naming it. An
  assumption can slip one gate; it cannot stay unseen while open, and it
  cannot silently resolve. Weaker than a validator, stronger than the
  original finding claimed.
- **Guards are enforcement too, and they interact (P11).** The
  verdict-after-challenge guard — correct for the walks — locks a register
  case out of its expected act. The project already knows this class (two
  overreaches removed last pass); this audit measured a third. The check
  suite has no lint for guard×case interaction; the re-record discipline is
  the only detector, which makes STALE-vs-red classification (this audit's
  correction to its own baseline) worth keeping in the loop.
