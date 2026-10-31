# What the method rewrite forgot: a read of 2026-10-31

Read-only gather, 2026-10-31, at head 6baaacb6. Sources: `git log`, grep
over `plans/stack.md` and `plans/archive/stack-2026-10-*.md`, the reads of
2026-10-20 to 2026-10-31, `tests/rota/walks.jsonl`, and the memory
archive. `plans/stack.md` was not read whole.

## Result

The three largest gaps are these.

1. **Roman's order of 2026-09-14 stopped and nobody closed or continued it.**
   Frame 4 ("Roman's order from here") is open at the stack's foot. Its
   last status is 2026-09-21, and steps 4 to 7 are unbuilt. The completion
   line needs "click and two more lineage repositories merge cold". No
   tips walk is in `walks.jsonl` after 2026-09-14, and no icalendar walk
   is in it at all. G1 (dynamic stacks), the language seam, the seat as
   an exchange and the principal's flow have no frame and no status line
   since 2026-10-01. Every frame since 2026-10-01 works on click alone.
2. **The stack says that 41 frames wait on Roman, and his ruling says that nothing does.**
   41 lines read "Waits on: Roman's order" (stack.md 2686 to 5048).
   Roman ruled on 2026-10-18 02:35: "Nothing blocks on me for multiple
   sessions". A parked list with no heading sits at the stack's tail
   (lines 5101 to 5233, under frame 314). It holds September items that
   wait on his read or his call. One of them is the DECISIONS rulings draft.
3. **Seven ruled records have no reader in the method pages, and the composition's open items are still open.**
   `rota/MAP.md` has no citation anywhere since 2026-09-13, but
   `COMPLETION.md` line 4 and `operating-facts.md` line 33 send a reader
   to it. `ROLES.md`, `plans/principal-flow.md`, `SEAT.md` and `SYSTEM.md`
   are not named in `intent.md`, `reference.md` or `CLAUDE.md`.
   `composition.md` "Open" holds two candidate sentences and one
   DECISIONS item from 2026-09-16, and no frame took them.

Rows per section: 1: 12, 2: 19, 3: 14, 4: 7, 5: 30.

## 1. Ruled records against the citations since 2026-10-18

"Arch" counts the archives `stack-2026-10-18` to `stack-2026-10-31`.
"Named" lists the method pages that name the file.

| Record | Last edit | stack.md | Arch | Named in | Reading | Source |
|---|---|---|---|---|---|---|
| `rota/MAP.md` | 2026-09-13 | 0 | 0 | none | Forgotten. COMPLETION.md:4 and operating-facts.md:33 still point to it | grep, git log |
| `rota/DECISIONS.md` | 2026-10-27 | 8 | 11 | reference.md:522, CLAUDE.md | Live | grep |
| `rota/LAWS.md` | 2026-10-18 | 5 | 12 | reference.md:522, CLAUDE.md | Live | grep |
| `rota/ROLES.md` | 2026-10-18 | 0 | 5 | none | Read by frames, no method page sends a reader | grep |
| `plans/principal-flow.md` | 2026-09-16 | 1 (frame 1, September) | 0 | none | Forgotten. Core entry 10 | grep stack.md |
| `plans/method/design.md` | 2026-10-18 | 11 | 18 | intent, reference, CLAUDE.md | Live | grep |
| `plans/composition.md` | 2026-09-16 | 3 | 0 | intent.md:6, reference.md:79 (C25), CLAUDE.md | Named, its "Open" section is not acted on | grep |
| `rota/COMPLETION.md` | 2026-09-17 | 17 (3 dated 2026-10-31, the rest Sept frames 1, 2, 4) | 0 | intent.md:20, reference.md:187, CLAUDE.md, all since 6baaacb6 today | Unnamed 2026-10-18 to 2026-10-31 | git log -S |
| COMPLETION "The order from here" | 2026-09-17 | 5 (frame 4, last status 2026-09-21) | 0 | none | Forgotten | stack.md:4750-4790 |
| COMPLETION "Post-core list" | 2026-09-17 | 1 (stack.md:5229, the tail list) | 0 | none | A pointer only | stack.md:5229 |
| `rota/SEAT.md`, `rota/SYSTEM.md` | 2026-09-16, 2026-10-01 | 0, 1 | 0, 0 | none | Unread since October | grep |
| `rota/REGISTER.md`, `rota/ONBOARDING.md`, `rota/README.md` | 2026-10-18, 09-19, 09-19 | 0, 0, 2 | 0 | none | Unread since 2026-10-18 | grep |

## 2. The core list and the order against today

| Entry (COMPLETION.md) | Owed there | A frame since 2026-10-01? | Source |
|---|---|---|---|
| A1, the interview | Brief re-record, Researcher route, two cold walks | No. "Researcher route" 0 hits, `a1-seed` 1 hit (stack-2026-10-14). "interview" hits are seat interviews, not A1 | grep |
| A7, cost before commitment | Rides the gauntlet | No frame on A7. The stray chain fired on night 175: s269 judged `criteria.json` a mistake | criteria-json-write-read-2026-10-29.md s1 |
| E1, amendment | Pinned test for the merged half, two tipsI walks | No. One history read only (stack-2026-10-21:112) | grep |
| A5, conflicting sources | Re-record, walk on a repo seeded with one conflict | Partly: frame 204 rebuilt the reconcile half (2026-10-11/12). No seeded walk | stack.md:2614, 2639 |
| B5, questions | Struck as built | n/a | COMPLETION.md:115 |
| D3, hollow verification | Night on the gemma-critic profile | Touched: `encodes-nothing` measured on its gemma pin to 2026-10-29, `verdict_failed` fixes to 2026-10-30. No frame on D3 | grep archives |
| G1, dynamic stacks | Largest unbuilt piece | No. 0 hits for dynamic stack, language seam, `language.facts`, toolchain | grep |
| F1, budgets | Parked until a remote provider | No (the "F1" hits are an unrelated fix label) | grep |
| 9, the seat as an exchange | First exchanges on tipsI and click | No frame. Sprint 35 (2026-10-31) puts the session in the seat, the nearest move | stack.md:17-42 |
| 10, the principal's flow | Stage 1 after click's cold merge | No | grep |
| Completion line, part 2 | click and two more lineage repos merge cold | click: 9 merges, last 2026-10-25. tips: last walk 2026-09-14. icalendar: no walk | walks.jsonl |
| Order step 1, the benchmark | | Done 2026-09-14 | COMPLETION.md:245 |
| Order step 2, routing | | Not needed (2026-09-15, 2026-09-17) | stack.md:4770 |
| Order step 3, finding 42 | | Built and reviewed 2026-09-18. "Frame 33's walk" is still an open list line | stack.md:1465, 4790 |
| Order step 4, the language seam | | Not built. No frame | frame 4 status 2026-09-21 |
| Order step 5, breadth | | Not done. No tips or icalendar walk since 2026-09-14 | walks.jsonl |
| Order step 6, long-run noise test | | Not run. "noise test" 0 hits in October | grep |
| Order step 7, ship the loop | | Not done | frame 4 |
| Frame 4 itself | | Open, unclaimed, last status 2026-09-21 | stack.md:4750-4796 |

## 3. Questions to Roman with no answer in the records

| Question | File:line | Note |
|---|---|---|
| A refusing door for a write of rota's own record (`_rota_record`) departs from law 12 and frame 114's ruling | stack.md:75-82 | Says "open below". No question text and no frame below |
| Cause 8's close rule of 2026-10-15 against C76 step 7 | stack.md:1635 (frame 341) | "Asked when a frame first reaches three nights at 0 of 0". Nights stopped 2026-10-29, so the trigger cannot fire |
| Does clause 3 still apply under the L3R loop of 2026-10-29 | stack.md:1833 (frame 326) | "Roman decides". Not asked |
| Does a request page show the account at all | stack.md:2098 (frame 264, parked) | Conditional on two reads. Not reached |
| The design question on cause 11 | stack.md:2215 (frame 276) | Conditional on a read. Not reached |
| May a test pass a literal the criterion does not name | stack.md:4883 (frame 281) | Conditional on a history read. Not reached |
| Frame 61, an unmet obligation visible only while pointed at | stack.md:4287 (parked) | "Waits on: Roman's order" |
| 41 frames, "Waits on: Roman's order" | stack.md:2686 to 5048 | Stale against the ruling of 2026-10-18 02:35 |
| The inert Stop hook `really_blocked.py`: delete or give it the allowlist | stack.md:5161-5166 | "Roman's call". The hook still names COMPLETION.md |
| The DECISIONS rulings draft waits on Roman's read | stack.md:5225 | `plans/decisions-rulings-draft.md`, last edit 2026-09-16, 0 citations in October |
| The reference drift predicate and the law-13 schema test | stack.md:5230-5233 | "Neither is in COMPLETION.md" |
| Candidate sentence: a seat that asks another seat waits in the same session | composition.md:139 | Tentative ruling, "until the code confirms". 0 October hits for "depth cap" |
| Candidate sentence: a seat that waits on the Principal ends and resumes from records | composition.md:140-142 | As above |
| "DECISIONS: rulings live in config without a writer or a version. Open." | composition.md:152 | Frames 293 and 300 are near it. Neither closes it |

## 4. Recommendations of the reads of 2026-10-20 to 2026-10-31 that no frame carries

19 reads checked. 12 carry their fix in a closed or open frame. Examples:
relay-c1 landed at c111bde9, R6 re-pinned the skipped tests at 24a4a4cb,
and W5 closed by dfc16500.

| Orphaned recommendation | Read | Where it stops |
|---|---|---|
| One reader `_rota_record` in `_code_write`, 25 lines, a question first | criteria-json-write-read-2026-10-29.md s2-s3 | Sprint 35 row text, stack.md:75-82, no frame |
| A route for a criterion met by a kept line, plus an exhaust, 2 cycles "after the seam pass lands" | critic-loop-read-2026-10-29.md | The seam landed (frame 345 closed 2026-10-30). No frame, stack.md:70-74 |
| The account page with no request: read the prompt's add example | night 175 sprint row 3 | stack.md:110-113. Frame 264 is parked |
| W8, the exact-twin check: "needs its own read before any fix, by C76" | f345 pass status, stack-2026-10-30 | No read and no frame |
| Frame 324's second clause: count the Architect sessions that repeat a bare symbol, nights 172 to 175 | f324-terminologist-s280-read-2026-10-29.md s4 | Frame 324 closed under the residue rule. The count never ran |
| The landing sentence that his earlier answers count needs a case with a real earlier answer | f347-quote-read, f335-338-close-read s3 | Frame 352 carries part of it. The case cut is not named in a frame |
| The 14 tests skipped "on named gaps" after R6 | stack-2026-10-30 status 10:46 | No frame names the 14 gaps |

## 5. The memory archive against the method pages

`C:/Users/roman/.claude/projects/d--repos-rota/memory/archive/`, 30 files.
All 30 are cited by name beside a rule in `plans/method/reference.md`.
None is cited in `intent.md`. No file is carried nowhere.

| Memory | reference.md line | Carried |
|---|---|---|
| ask-the-previous-session-first | 103 | Yes |
| hand-off-means-stopping | cited | Yes |
| hand-off-never-idle | cited | Yes, and in CLAUDE.md |
| peer-list-is-machine-wide | 633 | Yes |
| reserve-empty-means-unarmed | 622 | Yes |
| rota-agent-usage-from-harness | cited | Yes |
| rota-agents-run-on-opus | 206 | Yes |
| rota-check-a-cycle-when-it-fires | cited | Yes. Nights stopped 2026-10-29 |
| rota-frames-in-cycles | 214 | Yes |
| rota-frames-mean-not-number | cited | Yes, and in CLAUDE.md |
| rota-gate-five-lines-unpiped | 304 | Yes |
| rota-gate-from-a-worktree | cited | Yes |
| rota-handed-frame-continues | cited | Yes, and in CLAUDE.md |
| rota-handoff-momentum-note | cited | Yes |
| rota-history-before-escalation | cited | Yes |
| rota-interview-the-seat | 510 | Yes |
| rota-iteration-speed | 259 | Yes |
| rota-loop-agents-wait-in-foreground | 244 | Yes |
| rota-name-the-workflow | cited | Yes |
| rota-never-copy-over-a-busy-register | 320 | Yes |
| rota-night-dollars-are-nominal | 405 | Yes |
| rota-no-coauthor-footer | 331 | Yes, and in CLAUDE.md |
| rota-probes-pin-git-env | 255 | Yes |
| rota-release-before-rearm | 684 | Yes |
| rota-rerecords-are-cheap | 250 | Yes |
| rota-review-worktree-pattern | cited | Yes |
| rota-sprint-order-never-pauses | cited | Yes, and in CLAUDE.md |
| rota-status-time-from-clock | cited | Yes, and a live memory |
| rota-stop-a-night-that-measures-nothing | cited | Yes. Nights stopped 2026-10-29 |
| run-the-recommended-path-while-asking | 583 | Yes |

"Cited" means a grep of the file's name in reference.md returned one line.
The line was not printed for that row.
