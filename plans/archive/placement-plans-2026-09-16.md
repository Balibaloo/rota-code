# Placement of the 15 plans under plans/composition.md

Re-derived 2026-09-16 against the ratified page. Read-only. Every plan was
read at its head, its headings, and its status sections. Build claims were
checked against the code where a plan makes one.

## Summary

KEEP 6. ARCHIVE 6. PLACE 3.

- KEEP: a1-seed-interview-at-intent, amendment-and-conflicts,
  decisions-rulings-draft, principal-flow, seat-exchange, wake-audit.
- ARCHIVE: lost-work-audit, p4-scope-disclosure, responsibility-audit,
  rota-llm-configuration-proposal, rota-split, second-seat.
- PLACE: cockpit-presentation, greenfield-setup, model-setup.

Placement count, re-derived: 10 of 15 place under a page line. The five
that do not are the three PLACE plans and two of the ARCHIVE plans
(rota-split and second-seat), which reach the page only through "The
build session" and describe the build session's history, not rota.
That matches the earlier test's count of 10 and 5.

## The table

| Plan | Date | Status | Page line or section | Recommendation | Reason |
|---|---|---|---|---|---|
| a1-seed-interview-at-intent.md | ruled 2026-09-03, standing 2026-09-12 | Ruled. Pieces 1 and 4 built and pinned (`test_signoff_assumptions.py`, `sandbox._bind_send`). Pieces 2, 3 (the generator) and 5 (cold walks) owed. | The Liaison: "It infers intent, then checks and clarifies with the Principal." The Principal: "Approval of intent is required before work starts." | KEEP | A live build order with owed pieces. The page line is its parent. |
| amendment-and-conflicts.md | ruled 2026-09-12, measured to 2026-09-13 | Ruled. Level 2 built. Seven walks (tipsAU to tipsBB), no merge yet. Conflict page built 2026-09-12 (`@prose:<path>` wakes). Two owed: a re-record and a docs/ walk. | Flows: "Only a ratified amendment to something approved revokes work downstream." Flows: "It never settles a conflict." | KEEP | Live. Both halves place on one Flows line each. |
| cockpit-presentation.md | written 2026-08-24, filed in plans/ 2026-09-13 | Standing design. Six-step build order. Steps 1 and 2 have words in `rota/cockpit/tui.py` (pulse, replay, playhead). Not measured against its own "done when" lines. | NONE. Nearest: Purpose, "no work stays invisible". | PLACE | Live design. No page line names a screen, an observer, or the operator. See below. |
| decisions-rulings-draft.md | 2026-09-13 | Draft. 59 rulings in 226 lines. 19 entries wait for a person's eye. `rota/DECISIONS.md` is still 1425 lines, so the draft has not replaced it. | Records: "A ruling is a record. The Principal rules, the Liaison writes it, and it carries a version." Docs behind the page: "DECISIONS: rulings live in config without a writer or a version." | KEEP | The draft is the input to frame 18's DECISIONS work. It places on the line that motivates it. It lacks writer and version columns, which the page line requires. |
| greenfield-setup.md | filed 2026-09-03, ruled 2026-09-12 | Ruled core (dynamic stacks, piece 0 stack detection, Node as the second language). Not built. Scheduled after click merges cold. Only manifest name lists exist in code (`onboarding/lexicon.py`, `roles/api.py`). | NONE. Nearest: The parties, "The project" paragraph. | PLACE | Live and ruled. The page's destination names "a small Python repository" and has no line for a project with no code. See below. |
| lost-work-audit.md | 2026-09-13 | Audit ran. One lost mechanism found and ported (bb7c3d2). Doc corrections handed to the documentation pass. Two small owed items (law-13 schema test, `reference_drift` predicate). Neither appears in `rota/COMPLETION.md`. | Records: "A session commits or discards before it ends, so its output stays attributable." | ARCHIVE | A historical record. Its conclusion is the Records line above. Before the move, put the two owed items and the doc corrections into frame 18 or COMPLETION, or they vanish with the file. |
| model-setup.md | 2026-09-11 | Header says "Not built. Not ruled." Stale. Steps 1, 2, 3, 6 and 9 exist: `probes/walk.py` result row, `rota/llm/discover.py`, `keys.py`, `ModelSetup` modal on alt+m (`cockpit/screens.py:619`), `cockpit/server.py:418`. Steps 4, 5, 7, 8, 10 open. | NONE. Nearest: The parties, "A model is a component." The ceiling. | PLACE | A standing design with open steps. The page treats a model as given and says nothing about choosing or fitting one. See below. Fix the status line first. |
| p4-scope-disclosure.md | ruled 2026-09-03, piece 2 built 2026-09-12 | Built, both pieces. `touch_note` predicate (`predicates.py:704`), `principal.near_code` (`principal.py:425`), pinned in `test_signoff_assumptions.py`. The judged guess stays a conditional measured change. | Flows: "A prediction never blocks. Only a fact or a ruling gates." | ARCHIVE | Done. Its conclusion lives on that Flows line and in the code. The conditional item is a one-line note for the register, not a plan. |
| principal-flow.md | design 2026-09-12, five rulings 2026-09-13 | Ruled. Stage 1 waits on click's first cold merge. `batch_dep_facts` table exists with no writer. No `slice_read` in code. Two rulings owed before stage 2 (hold at design time, default path). | The Principal: "Approval of intent is required before work starts. Sign-offs after that, including on merges, are opt-in." Flows: "The tool never ... treats silence as consent." | KEEP | Live design with a named wait. Ruling 2 ("there is no silence") is the page's silence line. `operating-facts.md:276` names it as the design. |
| responsibility-audit.md | 2026-09-02, CLOSED 2026-09-03 | Closed audit. Rulings R1 to R14, findings P1 to P11. Phases 2 to 5 are already in `plans/archive/`. Its links to phase 4 and 5 files lack the `archive/` prefix. | The parties: "The Principal is in the team." (R3, one principal). Purpose. | ARCHIVE | An audit that ran and closed. Its conclusions are the page's parties section. Before the move: R1 to R14 are cited by `rota/COMPLETION.md` (2) and `rota/TESTS.md` (6) and are absent from the rulings draft. Copy the rulings log into the rulings register or keep a pointer. `operating-facts.md:246` cites P10/P11 by this path. |
| rota-llm-configuration-proposal.md | undated text, filed 2026-09-13 | Superseded. `BackendConfig` does not exist. Profiles (`rota/llm/profile.py`, 2026-09-09) took its place. `Pins` built. "Do not add a UI" is overtaken by the `ModelSetup` modal. | Records: "A record's identity derives from its content, not from when it was made." (the cassette key). The parties: "A model is a component." (weak) | ARCHIVE | Its conclusion lives in `model-setup.md`, "What exists today", and in the code. Nothing in it is still a plan. |
| rota-split.md | 2026-09-14 | Happened. A record of what moved and a SHA lookup guide. Its facts are in `plans/operating-facts.md:7-18`. The commit map is already in `plans/archive/`. | The build session: "Its records are this page, the stack, and the memory directory." (indirect, through operating-facts) | ARCHIVE | A historical record of the build session. `operating-facts.md:15` and `second-seat.md:41` point to `plans/rota-split.md`. Update both pointers. |
| seat-exchange.md | ruled 2026-09-12, findings to 2026-09-13 | Ruled. Harness built (`probes/seat.py`, `plans/exchanges/`). Findings 1 to 11: doors landed for 2, 4, 5, 7, 10. Cases owed for 1, 3, 6, 8. Finding 9 waits on Roman. | The Liaison: "It carries words both ways." The ceiling: "The feedback rate is the ceiling." | KEEP | Live measurement of the Liaison as a person meets it. The findings table is the loop's record. |
| second-seat.md | 2026-09-12, edited 2026-09-15 | A session brief. `rota/seat2` is fully merged, zero commits ahead, tip 2026-09-12. `plans/second-seat-log.md` was never created. The clone `D:\repos\rota-code-seat2` exists. | The build session: "The same composition applies to the session that builds rota, as a second instance with its own rules." | ARCHIVE | Superseded. The brief partitions work by file ownership. The composition and `CLAUDE.md` assign work by frame on the stack ("Roman assigns. You do not pick."). A second peer now claims a frame. `operating-facts.md:18` points to this file. Update it. |
| wake-audit.md | started 2026-09-13, last 2026-09-16, 67 commits | Live. 86 findings, most closed with a door, a push, or a brief line. Findings 85 and 86 are from night 81 and 82, today. | The parties: "Each seat wakes cold, acts once, and ends. Nothing accumulates in a conversation. Everything accumulates in records." Records: "A seat restarts from records." | KEEP | The loop's live log. Every finding tests one wake against that page line. |

## The PLACE plans

### cockpit-presentation.md

The page has one face to the Principal, the Liaison. The Principal "can
interrogate any detail through the Liaison". No line names a screen, an
observer, or an operator. The cockpit is a second surface. In practice it
is the build session's instrument: the ruling "the seat drives, the cockpit
answers" and the operator loop both put a person at the cockpit to read a
run. The plan's four registers (contract, happening, evidence, cause) map
onto Records lines: evidence flows up, reasoning stays reachable by a
pointer. Proposal: the parent is "The build session", and the page stays
silent on rendering. The plan is detail under that section. If Roman means
the Principal, not the assistant, to read the cockpit, the parent is
Purpose, "no work stays invisible", and the parties section needs one line
that names a surface beside the Liaison. Also note the plan is dated
2026-08-24 and never measured against its own "done when" lines.

### greenfield-setup.md

The destination names "a small Python repository". Greenfield starts from
an empty folder. Roman ruled on 2026-09-12 that dynamic stacks are core,
for new and existing repositories, with Node as the second language. The
plan is live and ruled, and the page has no line for a project with no
code. The nearest parent is "The project" paragraph: the structure holds
the project's shape "as records observed from the code". Piece 0 (the stack
read from a manifest, provenance `observed`) fits that line. Piece 1 (the
stack for an empty folder) does not. The plan gives that ruling to the
Architect with provenance `decided`. The page reserves "decided" for the
Principal: "A record says whether it was observed from the code or the
world, or decided by the Principal." Proposal: the parent is "The project".
Either the page adds one sentence there ("A project with no code yet takes
its shape from the Principal's words"), or the plan changes piece 1 so the
stack for an empty folder is a page the Principal approves, not an Architect
row marked decided. The second is the smaller change and matches the page.

### model-setup.md

The page treats a model as a given: "A model is a component." Choosing a
model, fitting it to the machine, and recording what vouches for it are
operator work before the composition runs. No page line covers that. The
nearest hooks are "A model is a component" and The ceiling: "A weak model is
trusted only as far as the loop that checks it is short." The plan's
"Benchmarks are the ground truth" section makes the register that loop, so
the recommendation half of the plan does place under The ceiling. The setup
screen half does not. Proposal: the parent is "A model is a component", the
page stays silent on setup, and the plan is detail under The parties.
Before the placement, correct the plan's status line. It says "Not built.
Not ruled." Steps 1, 2, 3, 6 and 9 of its order are in the code, dated
2026-09-11, and the modal's docstring cites the plan by step number.

## Cross-check: plans/archive/ today

`commit-map-rota-split-20260914.tsv`, `completion-diary.md`,
`enforcement-verification.md`, `feasibility-audit.md`, `probe-2026-09-16.md`,
`quality-dependency.md`, `responsibility-allocation.md`,
`rota-probe-repositories.md`, `stack-2026-09-16.md`, `superseded-present.md`,
`system-prompt-fixer.md`.

Convention seen: a file keeps its name. The diary and the stack archive
carry "archived <date>" in the first heading. The audit phases 2 to 5 carry
no archive note. `responsibility-audit.md` still links two of them without
the `archive/` prefix, so a `git mv` of the audit fixes those links only if
the links are rewritten with it.

## Pointers that break on the six archive moves

- `plans/operating-facts.md:15` to `plans/rota-split.md`.
- `plans/operating-facts.md:18` to `plans/second-seat.md`.
- `plans/operating-facts.md:246` to `plans/responsibility-audit.md`.
- `plans/second-seat.md:41` to `plans/rota-split.md` (moves with it).
- `rota/COMPLETION.md` (2) and `rota/TESTS.md` (6) cite rulings R1 to R17 by
  number with no path. They stay valid only while the rulings log is
  reachable.
- `plans/lost-work-audit.md:41` cites `plans/amendment-and-conflicts.md`
  by line number. The line numbers no longer hold (the file is 96 lines).
