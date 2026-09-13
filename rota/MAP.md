# rota, the map

What exists, where it is, and what is owed. Written 2026-09-13 from the
code, after the lost-work audit (`plans/lost-work-audit.md`). Every
mechanism named here is cited to its file. A claim without a citation is
not written here. Rulings stay in `DECISIONS.md`; the walk diary stays in
`COMPLETION.md`; this page is the one to read first.

## 1. The shape

Eight desks, one scheduler, one seat.

- **The desks** are roles in `design/graph.json`: liaison, vision_keeper,
  terminologist, architect, tester, developer, critic, researcher. The
  graph grants each role its reads, writes and message verbs; a role
  cannot do what the graph does not name (`core/sandbox.py`, `build`).
- **The scheduler** is 43 predicates over the SQLite state
  (`core/predicates.py`, `@predicate`): 17 start, 16 fix, 9 gate, 1
  traffic. A predicate produces wakes; `core/loop.py` dispatches one wake
  per step; `core/runner.py` runs the session, one model turn at a time,
  and commits its writes atomically (`core/db.py`, `session_commit`). A
  failed session leaves its row with `committed = 0` and its error as its
  last turn (`db.session_fail`).
- **The seat** is the principal's side: pages rendered from rows
  (`roles/principal.py`), replies landed through one door
  (`principal.land`), read by the Liaison's `landing` mode, and applied as
  rulings (`rulings.rule`, `apply_rulings`). The four pages are one
  surface (DECISIONS, 2026-09-12): confirm, present (signoff), the touch
  note, and the clarify.
- **The state** is 44 tables in `core/schema.sql`. Artefacts carry
  versions and receipts; runtime bookkeeping does not (`db.py`,
  `TABLES_OF_ARTEFACT`). No table carries a clock
  (`tests/rota/test_schema_has_no_clock.py`).

## 2. Where judgement lives and where facts live

- **Briefs** hold judgement: `roles/prompts/<role>/<mode>.md`, one mode
  per wake kind (`runner._mode_key`), with `<mode>.tools` narrowing the
  functions shown. 80 modes across the eight roles.
- **Doors** hold facts about files, the database and the index: a
  `ValueError` in `roles/api.py` (tools) or `core/sandbox.py` (message
  and write rules). A door never decides what a role should have judged;
  it refuses what a fact makes wrong, and names the route. The rule and
  its test are in memory as "mechanical doors" and in DECISIONS.
- **The register** measures both: 114 cases in `tests/rota/cases/*.yaml`,
  replayed from `tests/rota/cassettes.db` (git LFS) by `test_l1.py` and
  `test_l3.py`, recorded live with `ROTA_L1=1`. A case pins its bar model
  with `model:`. A red carries an attribution note in the case file or is
  owed a fix. State on 2026-09-13 under qwen3:8b: 19 reds, all attributed.
- **The walks** measure the whole: `probes/walk.py` (one run, one
  sentence, a yes-only principal), `probes/gauntlet_click.sh` (three
  sentences on click), `probes/seat.py` (the agent at the seat, turn by
  turn). Every walk writes a row to `tests/rota/walks.jsonl`: 81 rows, 7
  merges.

## 3. The delivery loop, in order

1. **Intake.** The principal's sentence is an entry; the Liaison confirms
   the statements (`awaiting_confirm`), the Vision Keeper asserts items
   (`slicing` after signoff), the Terminologist specifies criteria per
   ticket (`criteria`), the Architect groups tickets into a batch
   (`grouping`) and predicts its touch (`annotate`).
2. **Signoff.** The present page carries the items and the open
   assumptions, seven a page (`sandbox.PAGE_ASSUMPTIONS`); approve is a
   decision at the keypress, contest re-derives through `contested`.
3. **The touch note.** Before the batch builds, the predicted touch is put
   to the principal as a sense check (`touch_note`, `lifecycle.touch_set`).
4. **Build.** The Tester encodes one test per criterion from the criterion
   alone (`tests_missing`); the Developer writes spans and commits
   (`batch_start`, `code.write`, `code.commit`); the harness runs the
   batch's tests and the repository's own (`harness`); failing tests wake
   the Developer (`tests_failing`), bounded by `loop_cap`.
5. **Divergence.** A commit that touches paths the prediction never named
   writes `touch_strays` rows; the Architect judges each foreseen or a
   mistake (`touch_strayed`, `batches.judge_touch`); a mistake wakes the
   Developer (`touch_mistaken`). A test that asserts a literal the
   material never gave is refused at encode (`core/divergence.py`).
6. **Review.** The Critic reads the diff against the criteria
   (`review`, `verdicts.emit`), and a fail wakes the Developer
   (`verdict_failed`). The Architect reads the diff against the
   constraints (`structural_review`, `findings`), and a violated finding
   wakes the Developer (`finding_violated`).
7. **Merge.** `lifecycle.mergeable` says why a batch cannot merge: no
   commit, an untested criterion, no verdict on the head, a failed
   verdict, an unjudged stray, a violated finding. The scheduler merges
   (`merge`, `worktrees.integrate`).
8. **Amendment.** A reply that changes an item contests it; a running
   batch built from it is cancelled and re-batched (`cancel`, `slicing`,
   `grouping`); a merged batch stays and the amendment is a new batch
   (`plans/amendment-and-conflicts.md`, level 2).

Questions between desks travel as messages with attempt caps; an
unanswered question climbs the ladder (`unresolved`, `exhausted`) and ends
at the principal as a page. A wake dispatched past its cap is quarantined
and said out loud (`quarantined`). There is no silence: a page is a hold or
a note (DECISIONS, 2026-09-13).

## 4. Onboarding an existing repository

`orient` (the account), `reconcile` (every prose file against the account,
one session each; a disagreement is a page), `define` (terms), `survey`
(the Architect, Terminologist and Vision Keeper over every area),
`boundary`, `frame`. The code index (`code_index`, `code_edges`,
`code_lexicon`) is built by the provisioner. The lineage repositories:
oauthlib, icalendar, cnt, click, and tipsI (a two-file calculator) for the
seat walks; nodeI for the second language.

## 5. Core: what is owed (ruled 2026-09-12, read 2026-09-13)

| Capability | State | Owed | Where |
|---|---|---|---|
| A1 the interview | Built as the signoff page with open assumptions, ordered by what changes most | The submit brief's re-record; two cold walks | `roles/prompts/liaison/submit.md`, `plans/a1-seed-interview-at-intent.md` |
| A7 cost before commitment | Pieces 1 to 3 built (the note, the index line at signoff, the stray check) | Night 35 is the first walk on piece 3 | `predicates.touch_note`, `touch_strayed`, `plans/p4-scope-disclosure.md` |
| E1 amendment | Level 2 built | One pinned test for the merged half; a tipsI walk that merges after an amendment (tipsAT to tipsBC stall in the rebuilt batch on 9B judgement) | `plans/amendment-and-conflicts.md` |
| A5 conflicting sources | Built: reconcile reads each prose file | The re-record; a walk on a seeded conflict | `scheduler.prose_areas`, `predicates.reconcile` |
| B5 questions at a page | Built | Nothing; the free question is the chat surface, post-core | `roles/prompts/liaison/answering.md` |
| D3 hollow verification | gemma3:12b as the Critic passes every Critic case | A click night on the profile that merges with a real fail verdict | `llm/profiles/local-gemma-critic.toml` |
| G1 dynamic stacks | The account rules the stack; Node installed; nodeI sample built | The provisioner per stack and its nights | `plans/greenfield-setup.md` |
| F1 budgets | Turn caps and page caps | A money budget with the first remote provider | `core/config.py` |
| The seat as an exchange | `probes/seat.py`; findings 1 to 11 | More exchanges; the cases they produce | `plans/seat-exchange.md` |
| The principal's flow | Ruled; gated on click's cold merge, which happened 2026-09-13 | Stage 1: one ticket per Developer session, `batches.depend`, the worked example | `plans/principal-flow.md` |

Click merges cold since 2026-09-13 (nights 32 to 34, the same 48 lines
each time). What merged is poor: `echo_json` in two files the prediction
never named, and a test that asserts little. The stray check now catches
the first part. The quality of what merges is judgement on 8B and 9B
models, and it is the next problem.

Post-core by ruling: X1, X2, the chat surface, the web cockpit, multiple
principals, the reference-drift predicate (`plans/lost-work-audit.md`).

## 6. Running it

- `python -m rota onboard <run> --root <repo> --force --profile local`
  then `python -m rota run <run>`; the TUI is `python -m rota`.
- Two GPUs: the 3080 on `11434` runs nights; the Titan X on `11435`
  (`probes/titan_ollama.ps1`) records the register. Never a recorder and a
  walk on one card. Power modes: `probes/gpu_power.ps1`.
- A frozen run is read with `py-spy dump` on the walk's python and the
  Ollama `server.log`, never from utilisation alone.
- The register replays with `ROTA_MODEL=qwen3:8b` and no `ROTA_L1`;
  `ROTA_L1=1` records live.
