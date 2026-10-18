# Frame 287, step 4, the second read: the files left out and the rulings behind the fifteen

Meta workflow, read of the rota workflow's doors. This page continues
`plans/frame287-door-laws.md` with the same columns and marks, and does not
redo its rows. Read at b0bfa59a (the checkout carries an uncommitted edit of
`rota/roles/api.py`, 20 lines) on 2026-10-18 03:06 by an Opus agent,
read-only. The session judges this table.

## Method

1. Part 1: a script grouped the `night[s]? [0-9]` lines of the ten left-out files into blocks with the enclosing function and the next `return` or `raise`. The comment block and the function were read for each block that could rule on content.
2. Part 2: for each of the fifteen `no law, rules` doors, the search went DECISIONS.md, then the seat's brief, then `git log -S` and the frame's archive entry, and stopped at the first hit.
3. DECISIONS.md has no ids, so a ruling is named by the line of its heading at b0bfa59a. Every row is (reasoned: this read, 2026-10-18) as a placement. The mark in the law or ruling column is the strength of the record.

## Part 1: the ten files the first read left out

### rota/roles/principal.py (24 night lines)

| Door (line, function, refusal's first words) | Nights; frame | Law and mark | Line for the script |
|---|---|---|---|
| 177 `pending_asks`, an ask is held behind an open shift question | 137; 193 | no law, rules. Ruling: frame 193, (ruled: Roman, 2026-10-10 04:33, "Why not ask you blocking questions if you're there?") | `# ruling: frame 193, Roman 2026-10-10, the shift question blocks the asks behind it` |
| 772 `ratified_request`, a contested statement is not the request | 138; 193 | law 9, "amendment ⇒ revocation" (reasoned) | `# law 9: a contested statement is revoked until its owner amends it` |
| 1860, 1885, 1971 `land`, where a contest, a revise and an approve land | 133, 136 to 149, 144, 146, 152; 142, 190, 225, 255, 274 | law 9, "A ratified amendment ... drops it to pending" (reasoned) | `# law 9: a contest reaches the row's owner, who amends; an approve never skips it` |
| 2030 `land`, an approval change lifts a quarantine | 147; 240 | already cites law 6 (observed) | - |

Mech: 14 lines in 14 functions (`gave_up_on`, `check_line`, `_items_reached`, `off_page`, `request_rows`, `_gave_up_tries`, `request_block`, `_page_body`, `numbered` (3), `_page_order`, `chain_verdict`). These build a page or resolve a ref and refuse nothing.

### rota/core/db.py (10)

| Door | Nights; frame | Law and mark | Line for the script |
|---|---|---|---|
| 709 `_page_under_reply`, 788 `_answers_by_message`, 808 `_received`, 1003 and 1013 `session_commit`: a session that sent nothing caused by its trigger did not answer it, and the message goes `unresolved` | 33, 127, 138, 139, 151; 174, 200, 267 | law 6, "A question nobody answers climbs (`unresolved`)" (observed) | `# law 6: a question nobody answers climbs, so a barren session leaves it unresolved` |

Mech: 5 lines (`_forget_batch_counts` 3, `_why_no_ruling` 1, `session_fail` 1).

### rota/core/runner.py (107)

| Door | Nights; frame | Law and mark | Line for the script |
|---|---|---|---|
| 2318 `_resolve_contest`, a revise wakes the owner as a contest does | 136; 190 | law 9 (reasoned) | `# law 9: a revise is an amendment, so it wakes the owner with the words` |

Mech: 106 lines. They push a working set, fit a prompt to the window, render a cut, nudge a reply that holds no call, or count a repeated refusal. One of them is a cap that law 7 reaches, see Findings 4.

### The other seven files

| File | Night lines | Doors | Mech |
|---|---|---|---|
| `rota/llm/toolproto.py` | 23 | 0 | 23: the parser's repairs and hints for a malformed call |
| `rota/core/loop.py` | 8 | 0 | 8: counters, the dispatch alert, the attempt cap at boot (law 4 "Failure is bounded" covers the cap, reasoned) |
| `rota/llm/llm.py` | 4 | 0 | 4: the stream timeout and the server arguments |
| `rota/core/cycles.py` | 4 | 0 | 4: the CYCLE line |
| `rota/core/worktrees.py` | 2 | 0 | 2: the diff's file list and its base commit |
| `rota/llm/profile.py` | 1 | 0 | 1: a role's context window |
| `rota/core/plugins/_rota_caught.py` | 1 | 0 | 1: the caught-exception section of a red row |

## Part 2: the rulings behind the fifteen doors with no law

| Door | Ruling found (path, line or id) | Mark | Line for the script |
|---|---|---|---|
| api 4850 `_vet_surface`, a repair may not name a surface the program lacks | DECISIONS 1056, "The delivery wall": "the repair door requires a surface because words alone already failed there". The refusal of an unknown name at the repair is e417a94c, night 56. | (reasoned: the session that built it; the entry says "Built, 2026-08-26", no ruling) | `# ruling: DECISIONS 1056, a repair needs a surface; e417a94c: one the program has` |
| api 4884 `_surface_outside_batch` | brief `terminologist/criterion_repair.md:12-13`, "the surface is a callable in a file the batch expects to touch or the request names" | (reasoned: frame 215, pass 1, f3de0534, 2026-10-12; Roman ruled only the order, 10:36) | `# brief: criterion_repair.md, a surface sits in an expected file or the request` |
| api 6088, 6135 `tests_triage`, `contradicts_request` | DECISIONS 978, "The triage collapses to can/cannot", ruled 2026-09-01 for the two-way verdict. The sixth verdict: brief `tester/tests_missing.md:59-61`, from 88cee50c, frame 81. | (ruled: Roman, 2026-09-01, the two-way verdict); the sixth verdict (reasoned: frame 81; Roman ordered the repair at 2026-09-24 07:54, not its shape) | `# brief: tests_missing.md, a criterion that says what the request does not` |
| api 8449 `_kind`, the prints door of `tests.encode` | none. DECISIONS 943 line 957 says the opposite placement, see Findings 2. Built by 769bbf96 and af2f83f8, nights 42 and 45. | (reasoned: the session that built it, 2026-09-13 and 2026-09-14) | `# no law, no ruling: a test asserts on what the criterion says it prints` |
| api 9605 `rulings_rule`, a team note takes no revise | DECISIONS 1445, point 4, "Every word of the principal is a ruling on a row". The door: frame 190's outline, `plans/archive/stack-2026-10-10.md:5`, "a principal's words that name the item land on the item through one door". | (ruled: Roman, 2026-10-08 23:25, "sounds good"); the outline (ruled: Roman, 2026-10-09 10:31); the refusal itself (reasoned: frame 190's design, 2.2) | `# ruling: DECISIONS 1445, the principal's words land on the row they name` |
| api 9663 `rulings_rule`, the words do not fault the change's files | DECISIONS 1445, point 4, as above. The door: 4fe07692, frame 255, pass 1, on 16 of 16 files corrections. | (ruled: Roman, 2026-10-08 23:25) for the rule; the door (reasoned: frame 255, 2026-10-15) | `# ruling: DECISIONS 1445, a ruling lands on a row the words fault` |
| api 9709 `rulings_rule`, the description is no part of the request | DECISIONS 1445, point 4, as above. The door: e445aa64, frame 258. | (ruled: Roman, 2026-10-08 23:25) for the rule; the door (reasoned: frame 258, 2026-10-16) | `# ruling: DECISIONS 1445, a contest lands only on a request line it names` |
| api 10148 `ledger_log`, an assumption under four words | brief `liaison/blindspot.md:25`, "Say the actual thing" | (reasoned: frame 190's design, 2.3.2) | `# brief: blindspot.md, say the actual thing: what went unread, and why` |
| api 10237, 10247 `_restates`, `_misplaced_conflict` | brief `vision_keeper/reconcile.md:13-26`, "one call per disagreement" and "Two or three real disagreements beat ten restatements". DECISIONS 1242, "Conflicting sources", which the docstring cites, sits under Open. | (reasoned: frame 204, pass 2, night 143) | `# brief: reconcile.md, a conflict names two rows that disagree, not one restated` |
| api 14047 `_refuse_after_challenge` | brief `developer/tests_failing.md:25-33`, "Then change nothing", and 50-54 | (reasoned: frame 200; Roman's ruling of 2026-10-11 06:30 is on the answer mode's route, not on this door) | `# brief: tests_failing.md, a challenge ends the session, so change nothing after it` |
| predicates 513 `term_collision`, an answer that missed the question parks the word | brief `liaison/answering.md:62-66`, "An answer about something else is not an answer" | (reasoned: the session that built it, night 84) | `# brief: answering.md, an answer about something else parks the row unaddressed` |
| sandbox 2992 `stage`, a word the principal wrote | DECISIONS 1445, point 4, "it earns one Liaison question that names a row". The door predates it: 87f93948, night 29. | (ruled: Roman, 2026-10-08 23:25); the door (reasoned: 87f93948, 2026-09-13) | `# ruling: DECISIONS 1445, a principal's word earns a Liaison question` |
| sandbox 3127 `stage`, the Tester's answer to a challenge | DECISIONS 1248, "Challenging a test costs less", ruled and built 2026-08-26, for the quotes of a challenge. The answer's quotes: e3cbfbb0, "Roman's call, 2026-09-15". | (ruled: Roman, 2026-08-26, "why is this not obvious?"); the answer (ruled: Roman, 2026-09-15, by the commit body) | `# ruling: DECISIONS 1248, an answer that keeps the test quotes the criterion` |
| harness 193 `_run_one`, warning hygiene | DECISIONS 943, "Harness facts are refused at the door; judgement stays with the roles". The flag: a113c834, night 55. | (reasoned: the entry says "Built", no ruling) | `# ruling: DECISIONS 943, a harness fact is the door's, not a desk's` |
| scheduler 1994 `resume_behind`, only the request's work items end the park | frame 193, `plans/archive/stack-2026-10-11.md:5`, the shift question. The work-item rule: e406e976, the review of 61a0f41d, finding 1. | (ruled: Roman, 2026-10-10 04:33) for the shift question; the rule (reasoned: e406e976) | `# ruling: frame 193, Roman 2026-10-10; only the request's work items end the park` |

Counts (observed: this table, 2026-10-18): 14 of 15 doors have a ruling or a brief line behind them. 7 carry a Roman mark, 5 rest on a brief line alone, 2 rest on a DECISIONS entry marked "Built" with no ruling, and 1 has neither.

## Findings

1. **A door with no law and no ruling: the prints door, api 8449 `_kind` and its two refusals at 8473 and 8476** (observed: DECISIONS and the Tester briefs read, 2026-10-18). No Tester brief says that a test asserts on what prints. `tester/tests_missing.md:43-44` says "assert on what it returns".
2. **The prints door rules where DECISIONS keeps the line for a desk** (observed: `rota/DECISIONS.md:957`). The entry says: "whether "display" means return or print is a judgement, and walk twelve climbed it to the seat as designed." The door decides print against return from the criterion's words. The session rules whether the door is a word match (a fact) or the judgement the entry reserves (reasoned).
3. **A brief contradicts a door: `terminologist/criterion_repair.md:14`** (observed). The brief says "If the right callable does not exist yet, name it the way you intend it." `_vet_surface` at the repair refuses a name that the item, the ticket and the worktree do not give (api 4868). Frame 215's review 1, low 7, named this and left it as a one-line brief frame (observed: `plans/archive/stack-2026-10-13.md`, frame 215, 2026-10-12 11:39). No frame on the stack carries it by this read (reasoned: not checked against `plans/stack.md`).
4. **A cap outside config, law 7: the repeat stop of `run_session`** (observed: `rota/core/runner.py:4901-4916`). `refused_same[same] == 2`, `== 3` and `> 3` are literals, and `rota/core/config.py` has no repeat cap. This is the shape of the first read's Findings 1.
5. **Law 7 names `rota/config.py`, and the file is `rota/core/config.py`** (observed: `LAWS.md:204`, `ls rota/*.py`, 2026-10-18). The first read's Findings 1 quotes the law's path. A script line that cites law 7 inherits the wrong path.
6. **The first read's Findings 3, the stray hold of lifecycle 608, has a ruling** (observed: `rota/DECISIONS.md:1486-1491`, ruled: Roman, 2026-10-17, "if there were unexpected changes then the architect is required to sign off"). The hold waits on the Architect's sign-off, which is what Roman ruled. The contradiction with law 12 dissolves by this read (reasoned).
7. **Eight of the fifteen carry no Roman mark: five briefs, two "Built" entries and the prints door** (reasoned: Part 2's marks). DECISIONS 1445, point 4, carries four of the rulings doors. Its words, "Every word of the principal is a ruling on a row", are a candidate amendment to LAWS.md (reasoned).

## Left out

- `plans/stack.md` was not read, so Findings 3 does not say whether a frame carries the brief fix.
- The brief files' own `git log -S` was not run. A brief line marked (reasoned) can carry a Roman ruling in the commit that wrote it.
- The build sessions' transcripts were not read for Roman's words.
- In `runner.py`, the 106 mech lines were placed from the script's block list and a read of ten blocks, not of every block. The script names `forget` as the function for the blocks inside `run_session`, because a nested function precedes them.
