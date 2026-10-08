# Frame 41, an agent principal behind the walk's seam: pass 1

Status: written by the implementer on 2026-10-08, commit f9d8d2c2. Meta
workflow.

## What landed

- `probes/agent_principal.py`: `class AgentPrincipal` with `respond(ask)`,
  `pump(conn)`, `chat(conn, reply)` and `finish(quiet)`. `find_binary` finds
  the binary, and `call_model` makes one headless call per page.
- `probes/principal_brief.md`: the system prompt. It holds the three
  requests, the current request from `WALK_PHASE`, the three facts, the four
  answer rules and the last five pages and answers.
- `probes/walk.py`: the walk picks the agent when `WALK_AGENT` is set. A
  Liaison chat turn goes through `chat`. Two failed calls on one ask print
  `PRINCIPAL DOWN`, write `record(..., "principal down")` and exit 2.
- `probes/gauntlet_click.sh`: `export WALK_AGENT="${GAUNTLET_AGENT:-}"`.
- `tests/rota/test_agent_principal.py`: seven tests with the model call
  stubbed.

## Deviations

1. The agent has its own `pump(conn)`, a copy of `principal.pump`. The
   reason: the land row needs the landed message id, and `principal.pump`
   returns ids without the ask they belong to.
2. The words `(nothing)` on a page are a deferral. The ask goes into
   `replied`, and nothing lands. The brief names `(nothing)` for chat turns
   only. A page always asks something, so the code does not land the token
   as words.
3. An ask-back answered with `(nothing)` closes the Liaison's question and
   lands nothing on the page.
4. The `next` row at the end of the walk also holds the status of the ask
   and the ids of the principal's replies.

## The real call (observed: 2026-10-08, about 10:03)

`call_model("opus", ..., "Reply with the one word: ready", ...)` returned
`'ready'`, `duration_ms` 1408, `total_cost_usd` 0.122144. The peers table
before and after the call differed only in the heartbeat ages of two
standby rows. No new row appeared.

## The gate (observed: 2026-10-08, 10:30)

```
suite: 25 failed, 3354 passed, 32 skipped, 17 xfailed, 18 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (4): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-CR-fail-names-its-criterion], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (2): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names]
stale (0): none
time: 1207.6s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The baseline is 658abb6, 940 commits behind the tree. The four new reds
are not this pass's reds (observed: 2026-10-08). The map red fails with
the walk changes stashed. No file under `rota/` or the L1 cases imports
the probes this pass touched.
