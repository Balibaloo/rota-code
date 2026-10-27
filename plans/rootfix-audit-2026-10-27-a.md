# Root-cause audit of facts F1 to F18 at head, 2026-10-27, part a

Frame 344, half a. Read only at head 85db4dcd on `rota/foundation`. The code under `rota/` is the same as at 26a44700, the head of night 170 (observed: `git diff --stat 26a44700 85db4dcd -- rota/` is empty). Readers were re-counted with `map table|fn` and with an `ast` scan that maps each `git grep`-style hit to its enclosing function (`readers.py` and `fnscan.py` in session c66eae69's scratchpad). Test kit and `rota/tools` hits are left out of the counts unless named.

## 0. The result

- **FIXED: 0 of 18.** No fact reads one reader at every reader (observed: sections F1 to F18).
- **PARTIAL: 10.** F1, F2, F3, F4, F8, F9, F10, F11, F12, F18. A one reader or one record exists, and readers still read by their own rule.
- **OPEN, CAUSE KNOWN: 7.** F5, F7, F13, F14, F15, F16, F17.
- **OPEN, CAUSE UNKNOWN: 1.** F6.
- **The top three gaps by reach times nights:** F2 (19 own-rule readers, 6 nights, 114), F4 (32 own-rule readers, 3 nights, 96), F7 (13 finders, 6 nights, 78). The table is in section 2.
- Sprint 26 moved four facts at the source: F1 and F3 onto the `ruled_refs` record, F9 onto `areas.kind_of`, and F18 onto `_quote_reads` (observed: commits efde1aea, 5480f6b6, dfc16500, 41e31768). Each left a residue. The residues are listed per fact.
- The facts list 48 closed-frame places at F1 to F18, and some frames sit at two facts. 8 fixes now sit under a one reader, 7 sit partly under one, and 32 still stand alone. One, 297, was a wrong premise (observed and reasoned: the "closed frames" line of each fact).
- The facts file is wrong at head in five places. The code wins: `_package_definer` is not in the tree at 8ca76b40 or at head. `ruled_clarify_criteria` and `ruled_test_criteria` are gone. The F2 constants `_WORDS_FAULT`, `_DROP_LINE` and `_LINES` are gone. F4's `_test_is_red` has 1 caller, so "the one reader" is nominal. F5 misses two readers, `_failure_line` and `_run_view` (observed: grep at head).

## 1. The facts

### F1. His newest ruling on a ref

**Readers now.** The record is `ruled_refs` with its view `ruled_refs_live`, schema.sql, one row per ruling and ref (observed: efde1aea). `principal.ruled` (principal.py 908) is the one reader, with 16 callers (observed: `map fn ruled`). `grant`, `granted`, `open_adds`, `ruled_words`, `_his_rows` and `ruled_rows` wrap it (observed). 13 functions still name `FROM rulings` (observed). 8 of them are writers or key lookups of one row's `reply_id`, not a ruling rule: `land`, `_land_shift`, `apply_rulings`, `backfill_ruled_refs`, `_words_on_rows`, `_line_legend`, `_ruling_order`, `_ruling_id` (observed: their SQL is `WHERE id = ?` or a status write).

Of the 21 readers at 8ca76b40: 14 now call `ruled` or a wrapper, or read the view: `term_collision`, `contests_on`, `park_ruling`, `_confirm_landed`, `_reply_sentence_fault`, `_assert_words_fault` (through `_reply_sentence_fault`), `_landed_approval`, `_ruling_texts`, `contested_statement`, `last_ruling_on`, `chain_verdict` for its rows, `_line_legend` for `old_text`, and the replacements of `ruled_clarify_criteria` and `ruled_test_criteria` (`scheduler.ruled_rows`, `ruled_criteria`) (observed). `_retired_carry` reads no ruling now (observed).

**Still by their own rule: 5.** A keypress verdict map lives in a second store, `config` key `verdict:<message>`. `verdict_for` (principal.py 3039) reads it, and `chain_verdict`, `verdict_rows` (scheduler.py 1961), `_principal_relay` (api.py 2524) and `resolve_inbound` (runner.py 1976) read that map before or beside `ruled_refs` (observed: grep `verdict:`). `ruled_refs` also holds the same verdict with `source = 'keypress'` (observed: `_insert_keypress_ruling`). Two stores can disagree (reasoned). `last_ruling_on` and `contested_statement` query the view with their own SQL and not through `ruled`. They read the same view and the same status rule, so this report does not count them as own rules (reasoned).

**Verdict: PARTIAL.** 5 of 21 readers read a parallel store.

**Closed frames.**
- 213: its ruled-test mapping now reads `ruled_rows`, under the one reader (observed). Its test-to-criterion half is F6 and stands alone.
- 221: `_assert_words_fault` reads his rows through `_reply_sentence_fault` and `ruled` (observed). Under.
- 225: `problem_set_approval` still takes the approval from `_principal_relay`, the config map (observed). Stands alone.
- 226, 227: `last_ruling_on` reads the view (observed). Under. 227's second source, `_verdict_of`, reads `chain_verdict` and so the config map first (observed). Partly under.
- 238: `_landed_approval` calls `ruled(..., newest=True)` (observed: api.py 2306). Under.
- 129: the wake-kind branches of `_assert_words_fault` stand. They decide who owns the item's words, which no record holds (reasoned: closed-reach-a, 129).

**Proposal.** Read the keypress verdict from `ruled_refs` rows with `source = 'keypress'`, and remove the `config` `verdict:` map. `verdict_for` becomes a call of `ruled(conn, reply=mid)`. Readers moved: `verdict_for`, `chain_verdict`, `verdict_rows`, `_principal_relay`, `resolve_inbound`, and `land` as the writer. Price: 3 cycles, an instrument-sized change at one function with five callers (reasoned). Night evidence: the register count of verdicts whose config map and keypress rows differ goes to 0. F1 walled nights 166, 167 and 168, and nights 169 and 170 show no F1 wall (observed: facts file, `night170-read.md` section 5). So the night evidence is a register check, not a wall count.

**Departure.** None. The keypress row is his own act and is `decided` (observed: `ruled_refs_live.provenance`, schema.sql). Law 11, "Provenance derives from the refs" (rota/LAWS.md 279), supports one store.

### F2. The page lines his words name, fault, drop or approve

**Readers now.** 20 functions read one of `_LINE_REF`, `_PAGE_CUE`, `_LINE_FAULT`, `_LINE_CHECK`, `_CUE_BARE_FAULT`, `_LINE_WORD` (observed: scan at head). `_WORDS_FAULT`, `_DROP_LINE` and `_LINES` are not at head (observed: grep). Six readers of 8ca76b40 are gone: `_drops_whole_line`, `_sentence_hits`, `_words_fault_on`, `_keep_cancels`, `_line_dropped_on`, `_ruling_words_on` (observed: not found). Their drop and fault reads moved to `grant(conn, id, "drop")` on the record (observed: `_dropped_line`, api.py 6419). One new regex reader exists, `_earlier_sources` (observed).

The record holds a `line` per ref, but the line is the ref's place on the page, set by `ruling_rows` from the page order (observed: principal.py 1018 to 1090). It is not what his words name. `_line_reading` (api.py 11289) parses his words into lines, and only `rulings_rule` and `_earlier_reading` call it (observed).

**Still by their own rule: 19 of 20.** `_line_legend`, `_page_named_lines`, `_words_on_rows`, `_about_a_check`, `_agreed_contest`, `_cue_clauses`, `_earlier_reading`, `_earlier_sources`, `_item_sentences`, `_line_cues`, `_line_refusal`, `_live_cues`, `_note_words`, `_page_reply_fault`, `_unnamed_contest`, `_unnumbered`, `pointer_fault`, `rulings_rule`, `returned_line` (observed). Eleven of them are checks inside the `rulings.rule` door on the Liaison's reading (observed: they sit at api.py 11333 to 12600).

**Verdict: PARTIAL.** The record exists for the act. His line references are still read by 19 regex readers.

**Closed frames.**
- 234: its `_LINE_REF` and cue lists stand among the 19 (observed). Stands alone.
- 256: the "to" and "through" split is gone with `_WORDS_FAULT` (observed: not found). The range rule now sits in `_LINE_REF` and `_ref_lines`, shared by regex readers but not by a record (reasoned). Partly under.
- 282: the en dash sits in `_LINE_REF`, shared (observed). Partly under.
- 258, 305, 308: `_names_request`, `_line_cues`, `returned_line`, `_note_words` and `_LINE_FAULT` stand (observed). Stand alone.
- 255: at the source, `built_line_faulted` (observed: closed-reach-b). Its inputs are this fact.

**Proposal.** Make `_line_reading` the one parser of his words into page lines and acts. All 19 readers call it, and the door checks compare the Liaison's `ruled_refs` rows with its result. The cue lists move into that one function. Price: a seam, 8 cycles, because the `rulings.rule` door and `land` both change and a night must read it (reasoned: the anchors of `plans/operating-facts.md` 247). Night evidence: the `rulings.rule` refusal count, 29 in 11 sessions on night 170 (W6), and the W4 count, 1 contest of a line he did not fault (observed: `night170-read.md` section 6). Both fall on night 171 or later.

**Departure.** None found. His words stay verbatim and the legend stands beside them (composition line 106, cited at runner.py 645). The proposal changes the parser, not the words.

### F3. What his words permit or ask of a named target

**Readers now.** The record holds `act`, `target_kind` and `target` per ref (observed: schema.sql). `grant`, `granted` and `open_adds` read it (observed: principal.py 795 to 891). Of the 11 permission readers P1 to P11: `_words_remove_a_kind`, `_removal_asks`, `_line_dropped_on`, `_drops_whole_line`, `_words_fault_on`, `_page_added_lines` are gone (observed: not found). `ruling_drops_line`, `_unruled_gone`, `_other_line`, `disputed_paths` and `_ruling_texts` now read the record (observed: 5480f6b6, fnscan).

**Still by their own rule: 7.** `_asks_removal` with `_removal_spans` read the request and criterion text by phrase (observed: api.py 21252 to 21330). `_note_words`, `_names_request`, `_faulted_approve` and `_page_reply_fault` read his words by phrase inside the ruling door (observed). `criteria_respecify` matches tokens of his words at api.py 6902 (observed). `_asks_removal`'s docstring says a miss "records a stray for the Architect and refuses nothing" since frame 339 (observed: api.py 21301). So its residue cannot refuse work, and it routes to F8 (reasoned).

A gap in the record: night 170's "no new test is needed" reached no row, and no act or row records it (observed: `night170-read.md` section 3 item 9, W2). The act list is `drop`, `keep`, `rewrite`, `add`, `remove` (observed: schema.sql). The Liaison could have ruled the check line `rewrite` with his words, so the gap may be the reading and not the list (reasoned). The read of s215's reading would show which.

**Verdict: PARTIAL.** 7 of 11 readers keep a phrase rule. 4 of the 7 sit in the ruling door, and their place is F2's parser.

**Closed frames.**
- 298: `disputed_paths` reads the record (observed). Under.
- 221: under, as in F1.
- 263: `_PAGE_CUE` stands in `_page_reply_fault` (observed). Stands alone.
- 296: its number-or-quote check beside `_names_request` was not found by name at head. `_names_request` stands (observed). Stands alone, by the record of closed-reach-c.

**Proposal.** The four door phrase readers move with F2 to `_line_reading`. `criteria_respecify` 6902 reads `grant` for the target. `_asks_removal` stays a hint, because its miss records a stray and refuses nothing (reasoned). Price: inside F2's seam, plus 2 for the door text of the Liaison's act on a check (reasoned). Night evidence: W5, acts that name fewer targets than his words, 2 rulings on night 170, and W2, an answer that reaches no row, 3 answers (observed: `night170-read.md` section 2).

**Departure.** None. "It is never a ledger row written on the principal's behalf" (rota/LAWS.md 188) holds, because the act stays the Liaison's reading of his words.

### F4. The newest run of a test in its batch

**Readers now.** 34 functions read `FROM test_runs` or `JOIN test_runs` outside the test kit (observed). One is new since 8ca76b40: `_run_view`, sandbox.py 1014, which takes the newest run by `rowid` with no batch filter (observed). `_test_is_red` (sandbox.py 2371) has 1 caller, `_challenge_cap_refusal`, and `_tests_green` (predicates.py 1303), its copy, has 1 caller, `unresolved` (observed: `map fn`).

**Still by their own rule: 32 of 34.**

**Verdict: PARTIAL, nominal.** A one reader exists by its docstring, and 32 readers query the table themselves.

**Closed frames.** 210, 239, 245 and 317 each bound some readers to the batch or wrote one more newest-run query (observed: closed-reach-a and b). None of their fixes sits under a shared reader (observed: the 32). All four stand alone.

**Proposal.** One view `latest_runs` in schema.sql: the newest run per test and batch, by one order rule, as `ruled_refs_live` does for rulings. The 32 readers read the view. Price: a seam, 8 to 10 cycles, three order rules to merge (reasoned: closed-reach-a 210). Night evidence: W3 and W16 on night 170, s201's "broke an existing passing test (inh_fe7f4bfc)" while that test passed 7 of 7 runs (observed: `night170-read.md` section 3 item 4). The count of challenges or faults that name a red the newest batch run does not show goes from 1 to 0.

**Departure.** None. A test counts for its own batch only, frame 239's fact, which the view keeps (reasoned).

### F5. The error line of a red run

**Readers now.** 15 functions: the 12 of 8ca76b40 with `_own_assertions` renamed `_own_reds` (api.py 17847), plus `_failure_line` (principal.py 512) and `_run_view` (sandbox.py 1014), which the facts file did not count (observed). They use four rules: the first `E ` line, the last `E   ` line after a frame, `E\s` lines with `>` lines, and the native traceback frame (observed). `error_line()` is not at head (observed: grep).

**Verdict: OPEN, CAUSE KNOWN.** The place is `harness.py`, where the run output is made (reasoned: frame 336's proposal).

**Closed frames.** 223 (`_TRACE_FRAME`) and 317 (a first-`E` copy) stand alone (observed: both rules at head).

**Proposal.** `harness.error_line(output)`, called by the 15. Price: 3 to 4 cycles, an instrument and a mechanical sweep by `rota.tools.sweep` (reasoned). Night evidence: frame 336's measure, pages whose check row shows a red with no error text, 3 of 3 on night 168, no sample on night 170 (observed: `night170-read.md` section 4).

**Departure.** None.

### F6. The criterion of a test

**Readers now.** 46 functions name `criterion_id` beside `tests`, an upper bound by word match (observed). Partial helpers: `ruled_criteria` (scheduler.py 2010, 1 caller), `_criteria_of_tests` (sandbox.py 2393, 2 callers), `ledger_items` (lifecycle.py 636, 4 callers) (observed).

**Verdict: OPEN, CAUSE UNKNOWN.** The records show no night where two readers gave two answers. Table 2a row 2 finds none, and night 164 W-A is linked by its text only (observed: facts file F6). The read that would show it: one probe that runs each of the 46 readers' queries on night 170's register for tests with a null `criterion_id`, a retired criterion, and an inherited test, and lists the answers that differ.

**Closed frames.** 209 (a None guard at one place), 213 (a test-to-criterion map) and 317 (a ninth lookup) stand alone (observed: closed-reach-a and d; the 46 at head).

**Proposal.** The probe first, 1 to 2 cycles. If it finds disagreement, one helper `criterion_of(conn, ref)` with the guard, 3 cycles (reasoned). Night evidence: frame 338's measure, relays of a ruled test row that end with no acting call, 2 of 2 on night 168, no sample on night 170 (observed).

**Departure.** None. "The principal never rules on a test" (ruled: Roman, 2026-10-08, cited at scheduler.py 2014) stays: the helper maps a test row to its criterion as `ruled_criteria` does.

### F7. A removed base statement

**Readers now.** 13 removal finders: `_removed_lines`, `_unread_drop_refusal`, `_gone_statements`, `_unruled_gone`, `_base_held`, `_changed_unnamed_defs`, `_whole_drop`, `_tail_drop`, `_drop_note`, `_lost_statements`, `_rewritten_heads`, `_removal_strays` (new, 076ea892), `_escalation_over_removed_grain` (observed). `_unruled_removal` and `_removing_commit` are gone (observed). `_base_text` has 5 callers (observed: `map fn _base_text`).

Both commit doors read only a `drop_notes` row or a reply note, and only `code.write` opens one, through `_drop_note` (observed: `plans/frame339-s128-read.md` section 2). So the removal fact is decided per write by `_lost_statements` and `_rewritten_heads`, and the commit never compares the base with the tree on its own (observed: the same section). On night 170, s128's rewrite of `folder = os.path.expanduser("~")` opened no note, and `drop_notes` and `touch_strays` held 0 rows (observed: the same read, section 0). That read finds the door passed by design, because the rule reads a same-target rewrite as no removal (observed). So this report does not count night 170 as an F7 wall (reasoned).

**Verdict: OPEN, CAUSE KNOWN.** No one reader. The place is a commit-time compare of `_base_text` with the tree, with `_gone_statements`, for every path the batch changed (reasoned: the s128 read's counterfactual found line 518 that way, section 2).

**Closed frames.**
- 283: the per-write `drop_notes` detection stands, and it is the input of both doors (observed). Stands alone.
- 220: at the source, `_base_text` (observed).
- 297: wrong premise, no fix at this fact (observed: closed-reach-d).

**Proposal.** `_removal_strays` takes its removals from one base-against-tree compare at the commit, and the note stays the seat's information before the commit (frame 135). The per-write detectors become the note text only. Readers moved: `_removal_strays`, `_unread_drop_refusal`'s `opened` list, `_base_held`, `_tail_drop`, `_whole_drop`, `_escalation_over_removed_grain`. Price: a seam, 8 cycles, because the source of the removal fact changes from a note to the tree (reasoned). Whether a same-target rewrite is a removal is a question the seam must answer, and the s128 read leaves it open. Night evidence: frame 339's measure needs a night with the removal shape (observed: s128 read, section 5). The count is stray rows on removals against commits whose tree lacks a base statement, from 0 of 1 on night 170 to 1 of 1.

**Departure.** None. "Nothing rejects a diff for straying" (rota/LAWS.md 339) holds, because the compare records a stray and refuses nothing.

### F8. An unexpected change is a stray for the Architect

**Readers now.** `touch_strays` has 8 readers and 7 writer sites (observed: `map table touch_strays`). The removal door now records a stray and does not refuse (observed: 076ea892, `_removal_strays`). `touch_strayed` wakes the Architect (observed). The producer `_outside_prediction` folds paths through `divergence.stray_paths` and `divergence._norm`, which uses `lstrip("./")` (observed: divergence.py 104 to 124). `_grain_path` warns that `lstrip("./")` turns `.github/ci.py` into `github/ci.py` (observed: api.py, `_grain_path`).

**Still by their own rule: 1.** `stray_paths` with `_norm`. The removal strays depend on F7's notes (observed: F7).

**Verdict: PARTIAL.**

**Closed frames.** 286: `code.write` writes a stray row, and since 076ea892 the removal door does too (observed). Under. 236: no fix was built (observed: closed-reach-b). Whether `_predicted_touch` still reads only `batch_touch` was not read here: not found.

**Proposal.** `stray_paths` folds with `_grain_path` (with F11). Price: 2 cycles (reasoned). The removal half rides on F7. Night evidence: stray rows whose path the producer and the judge key differently, 0 expected. No night since 160 shows this sign (observed: facts file, nights 161, 162, 169 are the removal and merge walls).

**Departure.** None.

### F9. The program partition of a path

**Readers now.** `areas.kind_of` (areas.py 82) is the one reader, built by dfc16500 and 816902fc (observed). Its callers by name: `propose`, `stresses`, `_named_callables`, `_program_rank`, `_vet_surface` twice, `_test_dirs`, `_program_modules`, `_refuse_program_path`, `_frame_ranked`, `_defined_in_tree`, and `tests_encode` (observed: `map fn kind_of`, the scan of tests_encode 9589). `indexer.parse_file` calls `languages.kind_of`, another function of the same name (observed).

**Still by their own rule: 4.** `_is_test_path` (api.py 23669), called by `_code_write` twice, `_outside_prediction` and `_unnamed_def_strays`. The inline test rule in `_code_write` at api.py 19924. `push_working_set` (runner.py 4519, 4535) by a `tests/` prefix. `harness.inherit` (harness.py 292) by glob patterns (observed). `_is_prose_ref` keeps its pattern by design (observed: dfc16500's message).

**Verdict: PARTIAL.**

**Closed frames.** 215: `_program_rank` reads `kind_of` (observed). Partly under. Its `_surface_outside_batch` half is F10 and stands alone.

**Proposal.** The four call `kind_of`, with `_test_shaped` for the basename shape. Price: 2 to 3 cycles, a sweep (reasoned). Night evidence: frame 324's measure held at 0 of 2 on night 170 (observed). The count that would move is stray rows on test files that the frame marks program, from not counted to 0.

**Departure.** The code at head departs, not the proposal. Roman ruled on 2026-10-26 20:37 that "the basename gives the shape of a test file, and the frame's kind says whether the file is part of the program" (cited at api.py 7317). `_is_test_path` decides the program question by a path pattern.

### F10. The surface a criterion names

**Readers now.** The same 8 functions as at 8ca76b40 (observed). Both doors now call `_vet_surface` (observed: api.py 6089, 6840, 6970). The specify door adds `_surface_names_what_the_item_names`, which reads `_named_new_callables` (observed). The respecify door adds `_surface_outside_batch`, which reads the item, statement, ticket words and touch rows by its own rule (observed: api.py 5511).

**Still by their own rule: 3.** `_surface_outside_batch`, `_named_callables` (known names in the item text), `code_callables` (its ranking) (observed).

**Verdict: PARTIAL.**

**Closed frames.** 202: the respecify rules stand (observed). 215: the same. Both stand alone, and `_vet_surface` is now shared (observed). Partly under.

**Proposal.** One reader `item_callables(ctx, ticket_id)` that returns the known and the new names the item gives. Both doors and `_surface_outside_batch` read it. Price: 3 cycles (reasoned). Night evidence: frame 324's bare-symbol repeat count, 0 of 3 on night 170, and 165 W-H (observed).

**Departure.** None.

### F11. The path form of a file a seat names

**Readers now.** 43 functions split `::` by their own call, and 26 call `_grain_path` (observed). 34 split and do not call `_grain_path`, an upper bound, because some take the name half (observed). Among them `stray_paths`, `file_half` and `kind_of` (observed).

**Verdict: PARTIAL.**

**Closed frames.** 228: the judge reads `_grain_path`, and the producer folds by `_norm` (observed). Stands alone. 302: `file_half` splits by its own rule (observed). Stands alone.

**Proposal.** The path-half splits call `_grain_path`, by `rota.tools.sweep`. Price: 2 cycles (reasoned). Night evidence: none since 160 (observed: facts file). This gap ranks last.

**Departure.** None.

### F12. The click names and the runner target in a test body

**Readers now.** About 23 functions read `click`, a runner or `.invoke` by a wider grep, an upper bound (observed). `_click_names` has 4 callers and `_plain_invoked` has 1 (observed: `map fn`). `_is_runner_call` exists twice as nested copies (api.py 8418, 8474), beside `is_runner_call` (8829) (observed).

**Still by their own rule: about 18.** Among them `_invoked_commands`, `_invoked_command_calls`, `_callable_invoked`, both `_is_runner_call`, `is_runner_call`, `_arrange_run_refusal`, `_spec_mock_raise`, `_outside_commands_step`, `_wrap` (observed).

**Verdict: PARTIAL.**

**Closed frames.** 230, 254, 301: their receiver rules stand (observed: the three `_is_runner_call` copies). All stand alone.

**Proposal.** One reader of a test body's calls into the project's command library. It takes the library from the index, not the literal "click". Price: 3 cycles (reasoned). Night evidence: 162 W5, frame 304, parked (observed).

**Departure.** None. The proposal follows "I want to prevent over fitting" (ruled: 2026-10-15 01:54, W). The literal "click" departs from it (reasoned: closed-reach-d, 301).

### F13. The module that defines a name

**Readers now.** `_dotted_module` (2 callers), `_module_load_error` (5 call sites in `tests_encode`), `_project_module_of` (1), `_package_definers` (1, `_code_write`), with `_defined_in_tree` and `_program_modules` beside them (observed). `_package_definer`, which closed-reach-c names, is not found at 8ca76b40 or at head (observed).

**Verdict: OPEN, CAUSE KNOWN.** The place is the code index, which holds every symbol's file (reasoned: the grains are `path::name`).

**Closed frames.** 229 and 222 stand alone (observed: four rules at head).

**Proposal.** One reader `module_of(conn, name)` over the index rows and `kind_of`. Price: 3 cycles (reasoned). Night evidence: 161 W4 and 162 W1, "a test module is not an installed package", linked by text only (observed: facts file).

**Departure.** None.

### F14. Whether an assert can fail

**Readers now.** `_vacuous`, `_only_reads`, `_reads_interpreter_alone` and `_cannot_fail_because` are nested in `tests_encode` (observed: `map fn`). `challenge_vacuous` (api.py 16664) and `_own_reds` (17847) are beside them (observed).

**Verdict: OPEN, CAUSE KNOWN.** Three rules for one fact sit in one function, and the challenge channel has a fourth (observed).

**Closed frames.** 273 and 277 stand alone (observed: both rules nested at head).

**Proposal.** One predicate at module level, read by `tests_encode` and `challenge_vacuous`. Price: 3 cycles (reasoned). Night evidence: W9 on night 170, 5 refusals, and the door held (observed: `night170-read.md` section 2).

**Departure.** None.

### F15. Which request owns a row

**Readers now.** The 9 rules of 8ca76b40 stand (observed: `ledger_items`, `_is_description`, `_owner_of_ref`, `_owner_call`, `_is_request_item`, `current_request`, `request_of`, `page_request`, `off_page`). `request_of` has 7 callers, `_is_request_item` 10 (observed: `map fn`).

**Verdict: OPEN, CAUSE KNOWN.** `request_of` is the candidate, and `request_of` and `off_page` disagree on a description (observed: closed-reach-c, 274).

**Closed frames.** 198 and 274 stand alone (observed).

**Proposal.** One reader `request_of` over the ledger, criteria, tests, notes and page rows. The 8 others call it. Price: a seam, 8 cycles, because what owns a description needs a decision (reasoned). Night evidence: frames 316 and 325, nights 161, 162, 163 and 165 (observed: facts file).

**Departure.** None found.

### F16. A reply that landed nothing is not answered

**Readers now.** 17 functions outside the test kit set or read the mark (observed). `forget` is gone, and `architect_decision_on` and `stage` are new (observed). `REFUSED_END` and `REPEAT_END` have a copy in db.py and in runner.py (observed: db.py 1085, runner.py 37).

**Verdict: OPEN, CAUSE KNOWN.** `session_commit` is the candidate writer (observed: facts file).

**Closed frames.** 267 stands alone (observed: the two copies at head).

**Proposal.** `session_commit` sets the mark, and only with a landed row of the session. `land`, `_land_shift`, `close_park_asks` and `close_stale_park_asks` go through it. Price: 3 to 4 cycles (reasoned). Night evidence: W17 on night 170, 21 sessions with no landed write and no message, and W3's s202 to s212 (observed).

**Departure.** None.

### F17. The criteria a session holds now, staged over landed

**Readers now.** 7 functions read `ctx.writes` for criteria (observed). One is new: `_quote_refusal`, sandbox.py 1536, from sprint 26 (observed). `criteria_respecify` reads no staged criteria (observed: not in the list).

**Verdict: OPEN, CAUSE KNOWN.** The place is one overlay helper on the context (reasoned).

**Closed frames.** 257 stands alone (observed: closed-reach-d, and the respecify door at head).

**Proposal.** `criteria_now(ctx, ticket_id)`, read by the 7 and by `criteria_respecify`. Price: 3 cycles (reasoned). Night evidence: W8 on night 170, 9 twin refusals (observed). Frame 329's measure holds at 0 on its fourth night (observed: `night170-read.md` section 4).

**Departure.** None.

### F18. The live text a quote must match

**Readers now.** `_quote_reads` (sandbox.py 991) is the one reader, through `_span_of`, `_quote_forms` and `_shown_views` (observed: 41e31768, 3b19e5ec). `_reads_row`, `_answer_evidence`, `_challenge_evidence`, `_cites` and `_quote_refusal` call it (observed). `_quotes_span` and `_in_code` are gone (observed).

**Still by their own rule: 2.** `_red_line_refusal` (sandbox.py 1318) checks that a quote holds the failing line by its own compare. `_quoted_body_gone` (2520) checks the prior quote by its own rule (observed). `_quote_refusal` reads staged criteria by F17's own rule (observed).

**Verdict: PARTIAL.**

**Closed frames.** None since 2026-10-12 (observed: facts file).

**Proposal.** The two compare through `_quote_reads`. Price: 2 cycles (reasoned). Night evidence: s202's three quotes with `�` were refused by the one reader as "not a span of the live text" (observed: sandbox.py 1121, `night170-read.md` section 3 item 5). The cause of the `�` is not read (observed: the same read, section 7). Read it before the count: it can be a view `_shown_views` lacks.

**Departure.** None. The rule is "a contiguous span of the disputed row, verbatim" (ruled: Roman, 2026-08-26, rota/DECISIONS.md 1294).

## 2. The table

| Fact | Verdict | Own rule now | Proposal place | Price | Departure |
|---|---|---|---|---|---|
| F1 | PARTIAL | 5 | keypress verdict from `ruled_refs`, not `config` | 3 | no |
| F2 | PARTIAL | 19 | `_line_reading` the one parser | 8 | no |
| F3 | PARTIAL | 7 | F2's parser; `grant` in respecify | +2 on F2 | no |
| F4 | PARTIAL, nominal | 32 | view `latest_runs` | 8 to 10 | no |
| F5 | OPEN, KNOWN | 15 | `harness.error_line` | 3 to 4 | no |
| F6 | OPEN, UNKNOWN | 46, upper bound | probe first, then `criterion_of` | 1 to 2, then 3 | no |
| F7 | OPEN, KNOWN | 13 | commit-time `_base_text` compare | 8 | no |
| F8 | PARTIAL | 1 | `stray_paths` on `_grain_path` | 2 | no |
| F9 | PARTIAL | 4 | `kind_of` at the four | 2 to 3 | no; head departs |
| F10 | PARTIAL | 3 | `item_callables` | 3 | no |
| F11 | PARTIAL | 34, upper bound | `_grain_path` sweep | 2 | no |
| F12 | PARTIAL | about 18 | one test-call reader by the index | 3 | no |
| F13 | OPEN, KNOWN | 6 | `module_of` over the index | 3 | no |
| F14 | OPEN, KNOWN | 6 | one module-level predicate | 3 | no |
| F15 | OPEN, KNOWN | 9 | `request_of` | 8 | no |
| F16 | OPEN, KNOWN | 17 | `session_commit` | 3 to 4 | no |
| F17 | OPEN, KNOWN | 7 | `criteria_now` | 3 | no |
| F18 | PARTIAL | 2 | `_quote_reads` at two | 2 | no |

### The gaps by rank

Score is the own-rule readers now times the nights walled since 160, night 170 included (observed: the facts file's night lines and `night170-read.md` section 5). A night linked by text only counts.

| Rank | Fact | Own rule | Nights | Score |
|---|---|---|---|---|
| 1 | F2 | 19 | 6: 160, 161, 163, 165, 166, 170 | 114 |
| 2 | F4 | 32 | 3: 162, 164, 170 | 96 |
| 3 | F7 | 13 | 6: 163, 164, 165, 167, 168, 169 | 78 |
| 4 | F6 | 46, upper bound | 1: 164, by text | 46 |
| 5 | F15 | 9 | 4: 161, 162, 163, 165 | 36 |
| 6 | F16 | 17 | 2: 163, 170 | 34 |
| 7 | F17 | 7 | 4: 166, 167, 169, 170 | 28 |
| 8 | F3 | 7 | 3: 160, 169, 170 | 21 |
| 9 | F12 | about 18 | 1: 162 | 18 |
| 10 | F1 | 5 | 3: 166, 167, 168 | 15 |
| 10 | F5 | 15 | 1: 168 | 15 |
| 12 | F13 | 6 | 2: 161, 162 | 12 |
| 12 | F14 | 6 | 2: 166, 170 | 12 |
| 14 | F9 | 4 | 2: 165, 167 | 8 |
| 15 | F10 | 3 | 2: 165, 167 | 6 |
| 15 | F18 | 2 | 3: 167, 168, 169 | 6 |
| 17 | F8 | 1 | 3: 161, 162, 169 | 3 |
| 18 | F11 | 34 | 0 | 0 |

F6's score rests on an upper bound and a text link, so its rank is weak (reasoned). F12's own-rule count is also an upper bound (observed: section F12).

F2 and F3 share one place, `_line_reading`, so one seam covers 26 own-rule readers and scores 135 together (reasoned).

## 3. The doubt

1. Every own-rule count comes from name and pattern scans. A function that re-derives a fact with no shared word is missed. F6, F11 and F12 are upper bounds (reasoned).
2. A key lookup of one `rulings` row by id is not counted as an F1 own rule. A reader could disagree with that line (reasoned).
3. The night links that the facts file marks "reasoned" stay in the score. F6, F13 and F3's night 160 rest on text alone (observed: facts file).
4. Prices use the anchors of `plans/operating-facts.md` 247, and no price was measured (reasoned).
5. Closed frame 296's own check and frame 236's `_predicted_touch` state were not read at head: not found.
6. Usage: one agent, no sub-agents, about 110k tokens.
