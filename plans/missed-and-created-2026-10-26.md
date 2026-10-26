# The partial fixes since 2026-10-12: the problems they made, and the solutions nobody carries

Roman asked on 2026-10-26 at about 22:3x: "did we miss any real solutions and did we create any problems with the partial fixes". Read only, at head 6a78491f. Sources: `plans/closed-reach-2026-10-26.md` and parts a to d, the prevalence and groups pages, the fourteen `plans/frame<n>-agency-read.md`, `plans/stack.md`, the night reads 156 to 169, and `git show`, `git log -S` and `git grep` at the named commits. "Carried" means that an open frame's block or a sprint 26 row names the one-reader mechanism, not only a door fix at the fact.

## The result

- Created problems: 28 fixes added a reader, a rule, a refusal, a scene or a test that a later frame, gate or night paid for (observed: table 1). Six more wait for a payer, and four closes hid a fact (observed: the note under table 1).
- Missed solutions: 18 proposals that no open frame and no sprint 26 row carries, and 20 fixes that wrote a rule beside a reader that already held the fact (observed: tables 2a and 2b). 38 in all. 7 of the 20 sit at a fact of table 2a (observed: the Night column of 2b).
- 9 of the 18 proposals showed their fact on a night since 2026-10-12, under another frame's name or as a new cause. One of the 9 is reasoned (observed: table 2a, last column).
- The largest created problem is frame 283's removal refusal. It stopped night 169 and refused right commits on nights 163 and 168 (observed: row 1).

## 1. Created problems

| # | Frame, commit | What it added | What it broke or hid | Who paid |
|---|---|---|---|---|
| 1 | 283, 92e240fc (10-21) and 2acc7b5c (10-23) | `_unruled_removal` refuses a removed base statement for want of his permission. Pass 2 added a `line N` matcher that no brief asked for. 17 frame-140 tests now assert the refusal | Law 12 and the ruling of 2026-10-17 send a stray to the Architect. The door refuses right rewrites, and its route names a tool the seat lacks (observed: `frame339-agency-read.md` sections 1 and 3; the body of 2acc7b5c) | Night 163 W1; night 168 W10, 6 right commits; night 169 W1, the loop that stopped the night, 28 refusals; frame 339, sprint 26 row 1; 22 scenes to rewrite (observed) |
| 2 | 297, the ledger door, made read-only at ae1747bd (10-18) | A ledger door for a cause that was wrong, about 4 cycles | Dead code (observed: `closed-reach-d.md`, 297) | Frame 283 found it dead (observed: part d) |
| 3 | 330, ec33c1f7 (10-26) | `_quarantined_tries` (scheduler.py 1742) matches 1 of 10 stuck keys, beside `given_up` (1712) that lists all 10. A second words table beside `TICK_WORDS` | The 9 other keys stay stuck. Scenes encode the old quiet (observed: `frame330-agency-read.md` section 4) | Gate 24fd4638: 25 new reds, 20 from scenes, then pass 4; night 169 stalled on `batch_start`; pass 5 rebuilds on `given_up`. 9 cycles against 3 (observed: stack.md 1365, 1376, 1395) |
| 4 | 329, 1db6d00b to a875a798 (10-26 03:05) | The twin refusal tail offers `msg.challenge_vision_keeper` with no `quotes=` | An offer that the quote door refuses (observed: the diff; `agency-groups-2026-10-26.md` section 2) | Night 169 W2: his contest of crit_3 took four relays and four pages (observed: `night169-read.md` 63) |
| 5 | 221, 6761443b (10-14) | Pass 1c replaced the shared `last_ruling_on` with its own landed-only query | One shared reader became two rules (observed: part a) | Frames 238 the same day, 263, 316, 322, 337, 339 (observed: part a) |
| 6 | 238, 252feb0e and 89b523b2 (10-14) | `_landed_approval` (api.py 2307), a fourth newest-first loop | It differs from `last_ruling_on` on an `open` row. 11 own reads at head (observed: part b) | Frames 268, 274, 322, 337, 338; sprint 26 row 3, about 10 cycles (observed) |
| 7 | 213, 57c1a869 (10-14) | `_red_line_refusal`, a fourth reader of `test_runs` not bound to the batch, one day after frame 210 bound 6 of 18 | Three order rules, and one more unbound reader (observed: part a) | Frames 306, 318, 330 met the same rows with new readers; 333 and 336 both edit `_red_line_refusal` (observed: part a; groups section 2) |
| 8 | 245, 01df5c4c (10-15) | `_tests_green` (predicates.py 1295), a copy of `_test_is_red` | Two copies of one SQL (observed: part b) | Frames 317 and 318 each wrote a new newest-run query (observed: part b) |
| 9 | 230, 0d0f4771 (10-15) | A copy of `is_runner_call`. Its docstring says it reads `_plain_invoked`, and it does not call it | Five readers with four receiver rules at head (observed: part b) | Frames 254, 222 pass 1d, 301 (observed: part b) |
| 10 | 202, 6419a40b and three more passes (10-14) | Three new rules at the respecify door beside `_named_new_callables` | Two doors decide one fact two ways, by review 3 (observed: part b) | Frames 324 and 262 (observed: part b) |
| 11 | 222, c5f67351 (10-16) | `_package_definer` beside `_package_definers`, and `_project_module_of`, a fourth module rule | The NameError door and the surface door disagree on `src.` (observed: part c) | Frame 260, open; frame 301 (observed: part c) |
| 12 | 219, 7b0a9aac (10-15) | An author check copied into `decisions_author` and `_stage_reason` | The copy keys on the role and not the session (observed: part b) | Frame 243 wrote a third copy; frame 280, open (observed: part b) |
| 13 | 246, 401bbf3f (10-15) | Words for a tick key at `code_gaps` alone | The page showed `@claim:` keys two nights later (observed: part b) | Frame 253, open; frames 312 and 330 wrote two more copies (observed: part b) |
| 14 | 296, at 1dc02594 (10-21) | A number-or-quote check beside `_names_request` | The two give opposite answers on m125 (observed: part c) | Frames 337, 322, 305 (observed: part c) |
| 15 | 273, 000dfa78; 277, 8b290211 (10-17) | `_vacuous`, then `_only_reads`: three rules for "can this assert fail" | A tautology that no rule reads (observed: part c) | Night 157 W6; night 158 W2, which became frame 304; 328's `_own_assertions` (observed: the night reads; part c) |
| 16 | 301, at f6a80169 (10-24) | A hop and an own `import click` rule beside `_click_names` | 2 own rules became 4 at head. Every rule names the library click (observed: part d) | Frame 304 added two rules; nights 159 W2 and 162 W5 under 304 (observed) |
| 17 | 302, df3ab34c and 997ec895 (10-23) | `file_half` and `test_shaped`, a sixth path-form rule beside `_grain_path` | Passes 1b and 1c re-derived the `::` fold (observed: part d) | Frame 328 added `normpath` at `tests_encode` only (observed: part d) |
| 18 | 256, 15cbf388 and f0b2924c (10-16) | "through" in `_LINE_REF` and not in `_WORDS_FAULT`. `_faulted_approve` with its own cue list | Two range rules disagree. The approve check reads one night's cues (observed: part b; `frame337-agency-read.md` section 4) | Frames 263, 306, 308 wrote range rules, 282 the en dash; night 168 W7, frame 337 (observed; the W7 link is reasoned) |
| 19 | 305, c12c42b7; 308, 045ab3b1 (10-23 to 10-24) | Each widened its own cue list on the same evening. `_note_words` is one more rule | 7 readers with 6 own rules (observed: part d) | Frames 329, 337, 338, 339 at the same words (observed: part d) |
| 20 | 267, 98b7b562 (10-16) | `REFUSED_END` beside `REPEAT_END`, and the runner keeps its own copy of the text | About 10 places set or read the answered mark (observed: part c) | Frame 320, open (observed: part c) |
| 21 | 325, a31e7514 and 0c3cccbc (10-25) | A quiet `default` after intent, and a page kind query | 22 pins outside the recorded cases; `no such column: kind` on an old database (observed: stack.md 1555, 1556) | Gate 0c3cccbc: 34 new reds, reverted at 65ce095e and 16b56fe4; gate 65ce095e: 13 new reds, then pass 1d (observed) |
| 22 | 322, acb1180d; 7d37adcd (10-25, 10-26) | A new twin refusal text. A documentation door that refuses a headline word | Frame 257's pin went red. The door refuses the symptom, and no frame holds the cause, row 5 (observed: stack.md 1594; `frame322-agency-read.md` section 4) | Gate acb1180d, then pass 1c moved the pin; row 5 stays hidden (observed) |
| 23 | 306, 080f7d8f (10-24) | A test id inside the `order` rows | A reader of `order` failed to unpack, and 5 pins went red (observed: stack.md 1829) | Gate 080f7d8f: 11 new reds, then pass 2b (observed) |
| 24 | 234, the brief line at 90efc430 (10-14) | One Liaison brief line on line 1 | `L1-LI-a-separate-request-is-later` fell from 15 of 15 to 9 of 15 (observed: stack-2026-10-15 line 22) | The same gate, judged in the frame (observed) |
| 25 | 7bfdd2b8 and 40b16f78 (10-25) | Two more shipped model profiles | The profile pin counted 10 of 12 (observed: stack.md 1518) | Gate 4dc36732, then f95689d4 (observed) |
| 26 | 251, 76512284 (10-15) | The wall guide prices a fix at one door as the norm | Later frames counted reach as cases at one door (observed: part b) | Frame 341, open (observed) |

The count is 28, because rows 15 and 19 hold two fixes each (observed: the table). Six are not counted, because no later frame, gate or night has paid yet (observed: the records): frame 261's door SQL that lacked `not_parked` (65ee8ca1); frame 307's own parse in `_guess_section`; frame 336's second collection detector at principal.py 522 beside `_COLLECT_HEADER`; frame 335's `_one_backslash` (sandbox.py 1325); frame 200's two inline copies of `_sent_this_session`; frame 340's two refusals. `plans/method-reach-2026-10-26.md` reads frame 340's refusals as a departure from his ruling of 2026-10-18 02:25 that nobody asked him about (observed: stack.md 1293). Four closes hid a fact. Frames 228, 229 and 236 closed on three nights of 0 at a door that never fired, and frame 198 named a park that did not exist (observed: parts a and b). Frame 342 holds the zero baseline.

## 2a. Proposals that no frame carries

| # | Fact and proposal | Source | The reader that exists at head | Night that showed it |
|---|---|---|---|---|
| 1 | One newest-run reader of `test_runs` in its batch, for 24 readers | 210, 239, 245, 317 (parts a, b, d) | `_test_is_red`, sandbox.py 2244 | Night 162 W1b, under 318 (reasoned: the lift needs "the red moved") |
| 2 | One test-to-criterion reader, for about 17 lookups | 209, 213, 317 (parts a, d) | partial: `ledger_items`, lifecycle.py 636; `ruled_test_criteria` | None found |
| 3 | One `path::name` and path-form reader, for 20 own splits | 228, 302 (parts b, d) | `_grain_path`, api.py 17072 | Night 157 W5 and night 158 W6 as a new cause 8; night 159 W5 under 302 (observed) |
| 4 | One click-name reader, with no library name in the rule | 301 (part d) | `_click_names`, api.py 8663 | Night 159 W2 and night 162 W5, under 304 (observed) |
| 5 | One reader of the table that an id lives in | 187 (part b) | `_table_of_ref` api.py 13463; `_table_of` runner.py 3903; `_owner_of_ref` sandbox.py 911 | None found |
| 6 | One "can this assert fail" reader | 273, 277 (part c) | `_vacuous` api.py 9797; `_only_reads` 9853; `_own_assertions` 17447 | Night 157 W6, near 269; night 158 W2, then 304 (observed) |
| 7 | One "this session sent a challenge" reader | 200 (part a) | `_sent_this_session`, sandbox.py 1831 | None found |
| 8 | One model-host constant for six copies | 235 (part a) | none; two toml files still say localhost | None. No night uses those profiles (reasoned) |
| 9 | The night instruments read the stamp and the commit once | 232, 307 (parts a, d) | `code_stamp`, api.py 11971 | Night 158 W7 and night 159 W7, cause 13 (observed; the link to 232 is reasoned) |
| 10 | One rule for "a batch's test files are furniture" | 297 (part d) | `_uncommitted`, api.py 16986, copied at lifecycle.py 289 | None found |
| 11 | The journal registers agree on `test_run_journal` | 309 (part d) | `tools/audit.py` `_ids`; identity.py 108 | None found |
| 12 | One base-against-tree reader for 10 removal finders | 283 (part d) | `_removed_lines` api.py 16754; `_base_text` 21073 | Night 163 W1 and night 168 W10 under 283; night 169 W1 under 339 (observed) |
| 13 | The three renderers read the `order:` record | 272 (part d) | `order:<reply id>`, read by `_line_legend` and `_ruling_order` | None after the close (observed: night 156 W8 came before it) |
| 14 | One reader of staged over landed criteria, for 10 readers | 257 (part d) | none; each reader of `ctx.writes` has its own rule | Night 167 W3, under 328 (observed) |
| 15 | `_about_text` applies the docstring exemption | 321 (part d) | `_about_text`, api.py 7885 | None found |
| 16 | 328 lines 3 to 5: the Tester briefs, `_own_assertions` notes, the contested block marks a superseded text | `frame328-agency-read.md` section 5 | `_own_assertions` api.py 17447; the contested block, runner.py 764 | Night 168 W3, under 328 and parked 285 (observed) |
| 17 | One text pass: 322 item 4 and 333 item 4, `quotes=` in every refusal that offers a challenge | `agency-groups-2026-10-26.md` section 2. Sprint 26 names no text pass | none | Night 169 W2, under 329 (observed) |
| 18 | `code.write` takes the runner exemption of `tests_encode` | 254 (part b) | the `free_calls` helper of 0865fe13 | None found |

The count is 18 (observed: sprint 26 rows 0 to 5, and a grep of stack.md for each reader). Sprint 26 row 0, the re-cut by fact, lists these facts if it runs as written (reasoned: its brief lists every open fact with its readers).

## 2b. Fixes that wrote a rule beside a reader that existed

| Frame | The fact | The reader that existed, file and line at head | Night |
|---|---|---|---|
| 221, 238 | his newest ruling on a ref | `last_ruling_on`, principal.py 769 | carried, sprint 26 row 3 |
| 245 | the newest run of a test | `_test_is_red`, sandbox.py 2244 | 2a row 1 |
| 230 | the target of `.invoke` | `_plain_invoked`, api.py 8462 | none found |
| 202 | the callable that an item asks for | `_named_new_callables`, api.py 5656 | none found |
| 187 | the table of an id | `_table_of_ref`, api.py 13463 | none found |
| 222 | the module that defines a name | `_package_definers`, api.py 21839 | frame 260 holds it |
| 296 | his words name the request | `_names_request`, api.py 12018 | none found |
| 302 | the path form | `_grain_path`, api.py 17072 | 2a row 3 |
| 301 | the click names | `_click_names`, api.py 8663 | 2a row 4 |
| 307 | the guess stamp | `code_stamp`, api.py 11971 | 2a row 9 |
| 308 | "isn't right" is a fault | `_LINE_FAULT`, api.py 11136 | carried, row 3 |
| 283 | the removed lines; the stray route | api.py: `_removed_lines` 16754, `_base_text` 21073, `_unnamed_def_strays` 21317 | 2a row 12 |
| 297 | the uncommitted files | `_uncommitted`, api.py 16986 | 2a row 10 |
| 330 | every quarantined key; the stall words | `given_up`, scheduler.py 1712; `TICK_WORDS`, principal.py 1371 | carried, row 2 |
| 336 | a collection error | `_COLLECT_HEADER`, api.py 17603 | carried, row 4 |
| 335 | a nested text shown plainly | `_as_block`, runner.py 1867 | carried, row 4 |
| 200 | this session sent a challenge | `_sent_this_session`, sandbox.py 1831 | 2a row 7 |
| 261 | the drafts that woke a signoff | the tick's set, scheduler.py 507 at 65ee8ca1 | none found |
| 334 | a word with two senses | `term_collision`, predicates.py 349 | parked, sprint 27 |

The count is 20, because frames 221 and 238 are two fixes (observed: the table; each line by `git grep` at 6a78491f).

## 3. The doubt

1. Nights 140 to 155 and 164 to 166 have no wall table in the `| W` form, so "none found" covers nights 156 to 163 and 167 to 169 only (observed: grep).
2. Most rows rest on the four part records and the fourteen reads. Git checked the commits of rows 1, 3 to 6, 8 to 11, 13, 15, 17 and 18, and the head lines of table 2b. The other links are the records' (reasoned).
3. "Carried" is a grep of stack.md for the reader's name and the sprint 26 text. An open frame that names the fact in other words is missed, so each count of table 2a is an upper bound (reasoned).
