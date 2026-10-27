# The root-cause audit of facts F19 to F37 at head, half b, 2026-10-27

Frame 344, half b. Read only, at head 85db4dcd on `rota/foundation`. The code under `rota/` is the code of 26a44700 (observed: `git diff --stat 26a44700 85db4dcd -- rota/` is empty). Readers were counted with `python -m rota.tools.map fn`, `git grep -nE` and an `ast` map of each hit to its function (encl.py in the session scratchpad). Night counts come from `plans/facts-2026-10-27.md` for nights 160 to 169 and from `plans/night170-read.md` section 4 for night 170.

## The result

- 19 facts: FIXED 4 (F30, F34, F36, F37), PARTIAL 9 (F19, F20, F21, F24, F25, F26, F27, F28, F32), OPEN, CAUSE KNOWN 6 (F22, F23, F29, F31, F33, F35), OPEN, CAUSE UNKNOWN 0 (observed: sections below).
- 7 closed frames sit under no fact: 207, 189, 251 FIXED; 233 leaves a residue with a known place; 231, 293, 323 have no fact (observed: the last section).
- The top three gaps by reach times nights since 160: F20 (152), F19 (126), F25 (105) (reasoned: the ranking table).
- Sprint 26 moved F19, F20 and F21 part of the way. No fact of this half reached one reader in that sprint (observed: commits 41e31768, 3b19e5ec, ff8fcf22, d8e94e29).

## Where the code disagrees with the facts file

The code wins in each case below.

1. F19: line numbers moved, and two new functions now compose the forms of a quote: `_quote_forms` sandbox.py 976 and `_shown_views` 955. `_cites` now calls `_quote_reads` (observed: sandbox.py 1798).
2. F20: `_quarantined_tries` is not found at head. `exhausted` reads through `stopped_bouncing` (observed: predicates.py 1064, grep).
3. F21: `_stalled_words` principal.py 1717 is no second words table now. It reads `TICK_WORDS` through `_tick_words` (observed: ff8fcf22). Two other word rules exist that the file does not name: `gave_up_on` inside `render_state` 367 and `kind_words` inside `code_gaps` api.py 16349 (observed).
4. F22: a fifth helper exists, `ruled_ref_home` principal.py 987, added at efde1aea. Four table lists now exist: `LEDGER_HOMES` api.py 13814, `_REF_TABLES` runner.py 3707, `RULED_TABLES` sandbox.py 903, `RULED_HOMES` principal.py 1014 (observed).
5. F24: two inline copies stand, at `verdicts_emit` api.py 14166 and `_refuse_after_challenge` 18833. The copy in `verdicts_emit` has no `route != "triage"` filter, so it differs from `_sent_this_session` (observed).
6. F25: a brief checker exists, `test_a_mode_names_no_function_it_does_not_offer` tests/rota/test_prompts.py 526. A refusal follower exists, `sandbox.follow` 5375 with `api._offer` 288 (observed). The file says no reader checks a brief.
7. F27: `_unruled_removal` is not found at head (observed: grep).
8. F31: the named one reader, `_plain_words` api.py 7741, strips identifiers. It does not decide whether a text is about documentation. Five word lists decide that (observed: F31 below).
9. F36: `reach_line` has no caller in `rota/tools/status.py` at head. The gate came out at 150d13b7 by Roman's ruling of 2026-10-26 about 22:5x (observed: grep, `git show --stat 150d13b7`).
10. F37: `_pass_lines_check` reads live criteria through `_live_rows` (observed: api.py 14616). `_added_lines` api.py 17148 has 0 callers (observed: map).

## The facts

### F19. A seat's call text at its escape level and call form

1. **Readers now.** 21 functions (observed: map and grep). The quote face reads through one composition: `_quote_reads`, `_quote_holds`, `_quote_refusal` and `_cites` call `_quote_forms` and `_shown_views`. `_shown_views` asks the parser through `api._call_values` api.py 17940, and `_call_keeps`, `_raw_advice`, `_escape_refusal` and `_note_collection_error` read the same `_call_values` (observed). Three hand rules of the call syntax stand inside `_quote_forms`: `_seat_forms` 1439, `_one_backslash` 1476 and `_unescaped` 1490 (observed). `_shown_views` copies the views of `runner._render` by hand with `json.dumps` and `_escaped_view` (observed: sandbox.py 966). `_escape_note` api.py 22925 keeps its own rule for a decoded `\n` (observed). The parser functions `_third_reading`, `_stray_quote`, `_refuse_joined_strings`, `extract` and `extract_lenient` are the source, in one module, toolproto.py (observed).
2. **Verdict: PARTIAL.** One reader exists, `api._call_values`. 5 of 21 still read by their own rule: `_seat_forms`, `_one_backslash`, `_unescaped`, the view list of `_shown_views`, `_escape_note` (observed).
3. **Closed frames.** None since 2026-10-12 (observed: the facts file).
4. **Proposal.** Place: `sandbox._quote_forms` and `_shown_views`. Derive each form from `_call_values` and each view from `runner._render`, and delete the three hand rules. `_escape_note` reads `_call_values`. Readers moved: 5. Price: an instrument, 3. The parser refusals of open frames 155, 156, 137, 160, 266 and 327 already sit at the source, so each is a door text, 2 (reasoned). Night evidence: night 168 W2 refused 16 of 19 test-half quotes on `\\`, and night 170 W13 s211 repeated one call form 3 times. Both go to 0 over 3 nights (observed: `plans/night168-read.md` 105, `plans/night170-read.md` 69).
5. **Departure: no.** The ruling of 2026-08-26 asks for "a contiguous span of the disputed row, verbatim, whitespace-normalised" (observed: DECISIONS.md 1294). A form that the parser stores from the seat's text stays verbatim (reasoned).

### F20. A quarantined key, the stalled seat and the lift

1. **Readers now.** 19 functions read quarantined keys (observed: grep `quarantined = 1` and the callers of `given_up`). 11 read through `given_up` scheduler.py 1712: `park_ask`, `_running_given_up`, `stopped_bouncing`, `stop_detail`, `exhausted`, `park_owns`, `park_ask_id`, `close_stale_park_asks`, `parked`, and in part `quarantined` and `render_state` (observed: map). Of the 11 readers of 8ca76b40, 9 now call `given_up`, `_quarantined_tries` is gone, and `quarantined` predicates.py 1715 runs its own SELECT before the `given_up` filter (observed). 10 functions parse keys by their own rule: `quarantined`, `render_state` principal.py 439, `_stalled_keys` 1705, `_gave_up_tries` 1458, `code_gaps` api.py 16351, `land` 2494 (a direct delete, a lift outside `_lift_quarantines`), `loop.step` 336, `_next_rung` 1143, `_abandoned` 673, `_survey_wakes` 1073 (observed). `given_up` takes a key with one ref only, and `_stalled_keys` takes a key with any of a page's batches in its ref list, so two rules decide "the keys of a batch" (observed). The lift is one function, `_lift_quarantines` db.py 642, and the writes that skip it stand (observed: frame 242 open, stack.md 2473).
2. **Verdict: PARTIAL.** One reader exists for a batch subject, `given_up`. 10 of 19 still read by their own rule (observed).
3. **Closed frames.** 240 put a second call of `_lift_quarantines` on a raw write. It still stands alone, because raw writes of a subject's state still skip the lift (observed: frame 242 open; reasoned: no write helper at head).
4. **Proposal.** Place: scheduler.py. One `quarantined_keys(conn, subject=None, pairs=False)` and one key parser `key_parts(tick_key)` replace the ten own parses. The lift goes on the write that changes a subject's state, in `db._apply_write` or one state-write helper, and not on every commit, so frame 318 keeps its own rule. Readers moved: 10 readers and the delete in `land`. Price: a seam, 8 to 10. Night evidence: walks that end with a pending batch and a quarantined key (night 168 W5, night 169's stop, night 170 W1 and W2), and the constraint tick at onboarding (nights 160, 166 to 170). Both go to 0 over 3 nights (observed: the facts file F20, `plans/night170-read.md` 57, 58, 70).
5. **Departure: no.** The ruling of 2026-09-27 says a deferred batch's given-up key waits for the principal (observed: scheduler.py 1751, frame 87). The new reader keeps that filter (reasoned).

### F21. A tick key in words for a person

1. **Readers now.** 9 (observed). `TICK_WORDS` principal.py 1745 through `_tick_words` 1762 serves `_stalled_words`, `stop_detail`, `_shift_where`, `_shift_waits` and `_page_body` (observed: grep). Two rules stand alone. `gave_up_on` inside `render_state` 367 prints the raw kind and ref, for example "tests_missing for b_3". `kind_words` inside `code_gaps` api.py 16349 is a second words table (observed).
2. **Verdict: PARTIAL.** One reader exists, `_tick_words`. 2 of 9 read by their own rule (observed).
3. **Closed frames.** 246 put words on the key at `code_gaps` alone. Those words still stand alone (observed: `kind_words`).
4. **Proposal.** Place: `_tick_words`. `render_state` and `code_gaps` call it. Readers moved: 2. Price: a door text, 2. Night evidence: night 167 W11 and night 170 W14 and W15. A page with a tick name goes to 0 over 3 nights (observed: the facts file, `plans/night170-read.md` 70, 71). W15, "check: none yet", comes from `_gave_up_tries` reading the page's keys, which is F20 (observed: principal.py 1674).
5. **Departure: no.** The page contract shows his words, never rota's names (observed: principal.py 1742, frame 312, review 1).

### F22. The table an id lives in

1. **Readers now.** 33 call sites of five helpers: `_must_exist` 20, `_table_of_ref` 5, `runner._table_of` 4, `_owner_of_ref` 3, `ruled_ref_home` 1 (observed: map). Each helper keeps its own list of tables (observed: the four lists above).
2. **Verdict: OPEN, CAUSE KNOWN.** No one reader exists. `ruled_ref_home` is the widest and already calls `_table_of_ref` (observed: principal.py 987).
3. **Closed frames.** 187 added an inline check at 1 of 20 `_must_exist` callers. The helper set grew from 3 to 5 since, so the fix still stands alone (observed: map; the inline check by name: not found). 309 sits at the source for its own fact (observed: part d).
4. **Proposal.** Place: one `table_of(conn, ref)` in db.py over one table register, with the `guess:` and `reading:` prefixes. `_table_of_ref`, `_table_of`, `ruled_ref_home` and `_owner_of_ref` call it. `_must_exist` names the table that holds the id on a miss. Readers moved: 5 helpers, 33 sites. Price: an instrument, 3. Night evidence: night 170 W13, s209 `model.adopt` 3 refusals on b_3 and s200 `tests.encode` on a b_1 id. A repeated id refusal in one session goes to 0 over 3 nights (observed: `plans/night170-read.md` 69).
5. **Departure: no.** Not found.

### F23. A journal row has one author

1. **Readers now.** 4 author checks in 2 functions: 3 in `decisions_author` api.py 13911 (14007, 14030, 14046) and 1 in `_stage_reason` sandbox.py 2747 (observed). Each check keys on the role (observed: `ctx.role`). `db._apply_write` db.py 509 updates an existing row of any table and reads no table kind (observed).
2. **Verdict: OPEN, CAUSE KNOWN.** No one reader exists. `identity.py` declares 13 journal tables, and only `decisions` has a check (observed: identity.py 84 to 115).
3. **Closed frames.** 219 copied the check into two functions. Frame 243 added a third. They still stand alone (observed: the four checks).
4. **Proposal.** Place: `db._apply_write`. A write that changes the author column of a journal row refuses. Readers moved: the 4 checks. The 12 other journal tables gain the rule. Price: a seam, 8, because every journal write and its recorded cases pass through it (reasoned). Night evidence: night 166 W-G, `decisions.author` on his decision, goes to 0 over 3 nights (observed: the facts file F23).
5. **Departure: no.** LAWS.md law 1: "Journals ... may have several writers but one author per entry, append-only" (observed: rota/LAWS.md 95). Open frame 280 asks whether the author is the session or the role. The law does not say. That is one question for Roman before the build (reasoned).

### F24. This session sent a challenge

1. **Readers now.** 10: 8 callers of `_sent_this_session` sandbox.py 1958, and 2 inline copies (observed: map, grep).
2. **Verdict: PARTIAL.** 2 of 10 read by their own rule: `verdicts_emit` api.py 14166, with no triage filter, and `_refuse_after_challenge` 18833 (observed).
3. **Closed frames.** 200 is not this shape (observed: part a).
4. **Proposal.** Place: `_sent_this_session`. The two copies call it. Readers moved: 2. Price: a door text, 2. Night evidence: none since 160. A night with a triage route and a later challenge would show the `verdicts_emit` difference (reasoned).
5. **Departure: no.** Not found.

### F25. The calls a mode offers against the doors that refuse them

1. **Readers now.** 21 functions read `mode_tools` or `_wake_mode_tools` (observed: grep). The brief half has one checker: test_prompts.py 526 compares each backticked call of a brief with its mode's tools (observed). The refusal half has one follower: `sandbox.follow` 5375 sends each `_offer` record through the real doors under pytest (observed). `_params` 5344 falls back to the registry when the mode lacks the op, so the follower never checks the mode (observed). A refusal that names a call without `_offer` is not followed (observed: `api._offer` docstring; count: not counted).
2. **Verdict: PARTIAL.** One set exists, and one checker per half. The follower skips the mode, and refusals outside `_offer` skip the follower (observed).
3. **Closed frames.** 290 sits at the source. 237 is not this shape (observed: parts b, c).
4. **Proposal.** Place: `sandbox.follow`. An offered op outside `_wake_mode_tools(ctx)` is a finding. A lint over the raise texts finds a backticked call outside `_offer`. Readers moved: every `_offer` site and the unwrapped refusals. Price: an instrument, 3, and 3 for the lint. Night evidence: night 163 W1, a route names a tool the seat lacks, and night 169 W2, an offered route the next door refuses. Both go to 0 over 3 nights (observed: the facts file F25). Night 170 W7 and W16 are a wake before its batch exists, which is a producer and not this fact (reasoned: `plans/night170-read.md` 63).
5. **Departure: no.** Frame 135's law says a refusal names only a call the doors admit (observed: api.py 293). Doubt: open frame 334's heading names word senses of the Terminologist, not a mode's calls (observed: stack.md heading).

### F26. The guess stamp and the landed commit, for the night instruments

1. **Readers now.** `code_stamp` api.py 12086 has 3 callers: `rulings_rule`, `_page_body`, `land` (observed: map). `nightreport._guess_section` reads `code:<id>` by its own `_config` at 4 sites (observed: nightreport.py 353 to 370). The landed-commit half: not re-counted at head.
2. **Verdict: PARTIAL.** 1 of 4 readers of the stamp reads by its own rule (observed).
3. **Closed frames.** 307 still stands alone in the instrument. 232 sits at the source (observed: parts a, d).
4. **Proposal.** Place: `code_stamp`. The night report calls it on the night's connection. Readers moved: 1. Price: an instrument, 3. Night evidence: none since 160. Nights 158 and 159 W7 are the earlier walls (observed: the facts file).
5. **Departure: no.** Not found.

### F27. The uncommitted files of a batch

1. **Readers now.** 6: 5 callers of `_uncommitted` api.py 17386, and `discard_uncommitted` lifecycle.py 264 (observed: map).
2. **Verdict: PARTIAL.** 1 of 6 reads by its own rule. `discard_uncommitted` folds a test path with `replace("\\", "/")`, and `_uncommitted` folds it with `_grain_path` (observed: lifecycle.py 288, api.py 17393).
3. **Closed frames.** 297 had a wrong premise (observed: part d).
4. **Proposal.** Place: one `batch_furniture(conn, batch_id)` in core with the `_grain_path` fold. Both readers call it. Readers moved: 2. Price: a door text, 2. Night evidence: none since 160 (observed: the facts file).
5. **Departure: no.** Law 4, "an uncommitted change never existed", holds (observed: worktrees.py 245).

### F28. The row order of a page as he saw it

1. **Readers now.** 7 (observed). `door_rows(conn, reply, "order")` principal.py 2391 serves `_ruling_order` and `land`, both with a render fallback (observed). `_recent_chat` runner.py 2627 parses `order:` by its own JSON read. `rulings_rule` api.py 12668, `rulings_line` 13260 and `resolve_inbound` runner.py 2373 number his lines by today's render (observed).
2. **Verdict: PARTIAL.** 4 of 7 read by their own rule (observed).
3. **Closed frames.** 272 now sits under `door_rows` at 2 readers of 7. 308 sits at F2's cue families (observed: part d).
4. **Proposal.** Place: one `seen_order(conn, reply_id, ask)` beside `door_rows`, the record first and the render as the fallback. Readers moved: 4. Price: an instrument, 3. Night evidence: none since 160. Frame 272 counted 73 of 693 named rows that were not the row he saw on nights 158 and 159, and that count goes to 0 (observed: runner.py 2622).
5. **Departure: no.** Not found.

### F29. The model host

1. **Readers now.** 5 copies, unchanged: `OLLAMA_HOST` llm.py 44, `DEFAULT_HOST` gate.py 65, `OLLAMA` probe_tools.py 28, and two `localhost` endpoints in `local-openai.toml` 10 and `local-openai-native.toml` 9 (observed: grep 11434).
2. **Verdict: OPEN, CAUSE KNOWN.** No one reader exists. The candidate is `llm.OLLAMA_HOST` (observed).
3. **Closed frames.** 235 stands alone (observed: the copies).
4. **Proposal.** Place: `llm.OLLAMA_HOST`. `gate.py` and `probe_tools.py` import it, and the profile loader fills the two endpoints from it. Readers moved: 4. Price: a door text, 2. Night evidence: none, because no night uses those profiles (observed: part a).
5. **Departure: no.** Not found.

### F30. The run history and its registers

1. **Readers now.** One writer, `record_test_run` lifecycle.py 404, writes at 425. One reader, `nightreport.build`, reads at 722 to 743 (observed: grep). The registers declare the table (observed).
2. **Verdict: FIXED.**
3. **Closed frames.** 309 sits at the source (observed: part d).

### F31. What a criterion's prose is about

1. **Readers now.** 5 word lists decide whether a text is about documentation, all in api.py: `_NAMES_DOCS` 5844, `_HEADLINE_NAMES_DOCS` 5850, `_ABOUT_TEXT` 7812, `_ASKS_FOR_DOCS` 14289, `_ASKS_FOR_NOTES` 14298 (observed). 6 reading sites: `_docs_ticket_refusal` from `criteria_specify` and `criteria_respecify`, `tests_encode` twice through `_about_text`, `_pass_lines_check` twice (observed: map). The Tester's test-file door reads none of them (observed: `plans/night170-read.md` 57, W1).
2. **Verdict: OPEN, CAUSE KNOWN.** No one reader exists. The lists differ: `_ASKS_FOR_DOCS` holds "docstring" and "documentation", and `_NAMES_DOCS` holds "document", "docs" and "help text" too (observed).
3. **Closed frames.** 321 made one helper, `_about_text`, for its own door (observed: part d). It stands beside four other lists (observed).
4. **Proposal.** Place: one `asks_for_docs(text)` over the ruled words, read by the specify door, the respecify door, the encode door, the pass door and the Tester's test-file door. Readers moved: 6 sites and 1 door. Price: an instrument, 3, and a door text, 2. Night evidence: night 170 W1, 12 test-door refusals and a quarantine of `tester|tick:tests_missing|b_3`. Nights 165 W-G, 166 W-E and 167 W9, behaviour criteria on a docstring item. Each goes to 0 over 3 nights (observed: `plans/night170-read.md` 57, the facts file F31).
5. **Departure: yes.** The ruling: "a docstring or a comment, is evidence for a criterion only when that criterion's own words ask for the code's documentation, with the words "docstring", "document" or "help text"" (ruled: Roman, 2026-10-24 01:05, DECISIONS.md 1515 to 1531). `_ASKS_FOR_DOCS` already leaves out "document" and "help text" by frame 311 pass 1b (observed: api.py 14286). One list must take one side, so ask Roman. Recommended answer: the ruled words, with "help text" on a criterion read as documentation (reasoned).

### F32. The drafts that woke a signoff

1. **Readers now.** 2: `tick_signoff` scheduler.py 579 and `refuse_signoff_without_draft` api.py 737. Both call `not_parked`, and the door queries `approval = 'draft'` by its own SQL (observed).
2. **Verdict: PARTIAL.** 1 of 2 reads by its own rule (observed).
3. **Closed frames.** 261 still stands alone (observed: the door's SQL).
4. **Proposal.** Place: one `signoff_drafts(conn)` from the body of `tick_signoff`, read by the door. Readers moved: 1. Price: a door text, 2. Night evidence: none since 160. Night 150's 32 of 42 omitted submits are the base (observed: api.py 742).
5. **Departure: no.** Law 8, signoff is per-item approval as one document, holds (observed: api.py 740).

### F33. A debt names its open frame

1. **Readers now.** `OWED` tests/rota/test_case_reachability.py 212, read at 285 and 298 (observed). 31 `xfail` or "until frame" marks in `tests/` (observed: grep count). `KNOWN_REFUSED_OFFERS` tests/rota/conftest.py 147 (observed). `open_frames()` is not found at head.
2. **Verdict: OPEN, CAUSE KNOWN.** No one reader exists. Frame 332 names the place (observed: stack.md heading).
3. **Closed frames.** None.
4. **Proposal.** Place: one `open_frames()` in rota/tools/state.py over `state.parse`, and one test that each debt mark names a frame in it. Readers moved: `OWED`, `KNOWN_REFUSED_OFFERS` and the marks. Price: an instrument, 3. Night evidence: none, because the fact is in the suite. The evidence is 0 debts that name a closed frame (reasoned).
5. **Departure: no.** Not found.

### F34. The night's world in the test kit

1. **Readers now.** `_with_repo` rota/testkit/fixtures.py 863, called by `run_case` 1415 and `run_chain` 1506 (observed: map). `scenes.py` 438 seeds `project_root` for scene tests, which are not recorded cases (observed).
2. **Verdict: FIXED.** The reach is 1 for recorded cases (observed). Frame 331's open work is cases with no fixture, which is coverage and not a second reader (reasoned: its heading).
3. **Closed frames.** None.

### F35. The predicted files and the paths his words decline

1. **Readers now.** 26 functions read `batch_touch`, `touch_guesses` or `disputed_paths` (observed: grep). Two partial readers exist: `lifecycle.touch_set` 498 for the seat and the page, with 4 callers, and `api._predicted_touch` 21810 for the doors, with 2 callers (observed: map). Neither drops the paths his words decline. `disputed_paths` runner.py 1959 is read only inside `resolve_inbound` (observed: map). About 12 functions read `batch_touch` raw, among them `needs_structural_review`, `annotate`, `touch_note`, `push_working_set`, `_surface_outside_batch`, `_surface_pick`, `_arrange_run_refusal`, `batches_judge_touch` and `batches_expect` (observed: grep).
2. **Verdict: OPEN, CAUSE KNOWN.** No one reader exists (observed).
3. **Closed frames.** 298 put his file words at a new parser, and that parser is still read in one function. It stands alone (observed). 244 is not this shape (observed: part b).
4. **Proposal.** Place: one `predicted_files(conn, batch_id, staged=())` in lifecycle.py. It gives path grains and the files of file-qualified symbols, less `disputed_paths`. The doors and the seat's view read it. `touch_set` keeps the Architect's own rows for the page. Readers moved: about 14. Price: a seam, 8. Night evidence: night 170 W1, 12 refusals at the Tester's test-file door against the touch set, and W5, acts that name fewer tests than he asked. Each goes to 0 over 3 nights (observed: `plans/night170-read.md` 57, 61).
5. **Departure: no, if the page keeps the Architect's rows.** P4 (ruled R16/R17, 2026-09-03): "the modification scope is put to the principal as a sense check" from "the Architect's own rows" (observed: lifecycle.py 502 to 506). A page that drops his declined paths from those rows would depart from it (reasoned).

### F36. A frame's status lines, as the status tool reads them

1. **Readers now.** `state.parse` rota/tools/state.py 170 reads a frame block, and `status.py` calls it at 78 and 185 (observed). `reach_line` 212 has callers in tests only (observed: grep). `rulings.py` 42 matches frame headings for its search and reads no status line (observed).
2. **Verdict: FIXED.** One reader, `state.parse` (observed).
3. **Closed frames.** 287 is not this shape. 342 closed by ruling (observed: stack.md, frame 342's close line).

### F37. The added code lines that a pass names

1. **Readers now.** `_pass_lines_check` api.py 14602 serves `verdicts_emit` and reads live criteria (observed). `built_line_faulted` 11855 serves `code_line_faulted`, `rulings_rule` and `land` (observed: map). `_added_lines` has 0 callers (observed).
2. **Verdict: FIXED.** Each half has one reader, and every caller calls it (observed).
3. **Closed frames.** None since 2026-10-12. Frame 189 sits here by the code (see the last section). Open frame 311's wall is the documentation word list inside `_pass_lines_check`, which is F31 (observed: api.py 14686, 14761).

## The table

| Fact | Verdict | Own rule now | Proposal place | Price | Departure |
|---|---|---|---|---|---|
| F19 | PARTIAL | 5 of 21 | `sandbox._quote_forms`, `_shown_views` on `api._call_values` and `runner._render` | 3 | no |
| F20 | PARTIAL | 10 of 19 | `scheduler.quarantined_keys` and `key_parts`; the lift on a state write | 8 to 10 | no |
| F21 | PARTIAL | 2 of 9 | `principal._tick_words` | 2 | no |
| F22 | OPEN, CAUSE KNOWN | 5 helpers, 33 sites | `db.table_of` | 3 | no |
| F23 | OPEN, CAUSE KNOWN | 4 of 4 | `db._apply_write` journal author | 8 | no (one question: session or role) |
| F24 | PARTIAL | 2 of 10 | `sandbox._sent_this_session` | 2 | no |
| F25 | PARTIAL | follower skips the mode; unwrapped refusals not counted | `sandbox.follow` and a raise-text lint | 3 + 3 | no |
| F26 | PARTIAL | 1 of 4 | `api.code_stamp` | 3 | no |
| F27 | PARTIAL | 1 of 6 | core `batch_furniture` | 2 | no |
| F28 | PARTIAL | 4 of 7 | `principal.seen_order` | 3 | no |
| F29 | OPEN, CAUSE KNOWN | 4 of 5 | `llm.OLLAMA_HOST` | 2 | no |
| F30 | FIXED | 0 | none | 0 | no |
| F31 | OPEN, CAUSE KNOWN | 5 lists, 6 sites | one `asks_for_docs` over the ruled words | 3 + 2 | yes |
| F32 | PARTIAL | 1 of 2 | `scheduler.signoff_drafts` | 2 | no |
| F33 | OPEN, CAUSE KNOWN | all | `state.open_frames` and one test | 3 | no |
| F34 | FIXED | 0 | none | 0 | no |
| F35 | OPEN, CAUSE KNOWN | about 12 of 26 | `lifecycle.predicted_files` | 8 | no, if the page keeps the Architect's rows |
| F36 | FIXED | 0 | none | 0 | no |
| F37 | FIXED | 0 | none | 0 | no |

## The gaps ranked by reach times nights since night 160

Reach is the readers at head. Nights are nights 160 to 170 with a wall at the fact (observed: the facts file, `plans/night170-read.md` section 4).

| Rank | Fact | Reach | Nights | Product |
|---|---|---|---|---|
| 1 | F20 | 19 | 8: 160, 162, 164, 166, 167, 168, 169, 170 | 152 |
| 2 | F19 | 21 | 6: 164, 165, 167, 168, 169, 170 | 126 |
| 3 | F25 | 21 | 5: 160, 161, 163, 169, 170 | 105 |
| 4 | F22 | 33 | 1: 170 | 33 |
| 5 | F31 | 6 | 5: 164, 165, 166, 167, 170 | 30 |
| 6 | F35 | 26 | 1: 170 | 26 |
| 7 | F21 | 9 | 2: 167, 170 | 18 |
| 8 | F23 | 4 | 1: 166 | 4 |
| 9 | F24, F26, F27, F28, F29, F32, F33 | 2 to 10 | 0 | 0 |

F31 ranks low by reach, but it stopped walk 3 of night 170 (reasoned: W1 is the stop, `plans/night170-read.md` 57).

## The closed frames under no fact

These are the frames of `plans/closed-reach-2026-10-26.md` (parts a, c, d) and `plans/closed-reach-b.md` that no fact of the facts file names (observed: the union of each fact's closed frames against the 67).

| Frame | Closed as | At head | Verdict |
|---|---|---|---|
| 207 | at the source | `project_tests_fact` sandbox.py 2197 has 4 callers, and `tester_paths` harness.py 64 has 2 (observed: map) | FIXED |
| 189 | not this shape, no fix | `built_line_faulted` serves `rulings_rule`, `land` and `code_line_faulted`, the batch-line rule that frame 190 changed twice (observed: map). The fact sits under F37's second half (reasoned) | FIXED |
| 251 | not this shape, a design record | The wall guide prices a fix by its reach at lines 127 to 135 since frame 341's 9dacf698 (observed) | FIXED |
| 233 | not this shape, a tool | `rota/llm/cassettes.py` stores no `done_reason`, and `runner.py` 5126 and 5382 read it. A replayed night never fires the length or the invented-result rule (observed: grep) | OPEN, CAUSE KNOWN. Place: `cassettes.py` stores and returns `done_reason`. Readers moved: 2. Price: an instrument, 3. Evidence: a replay of a recorded length stop fires the rule. Departure: no |
| 231 | not this shape, a read | no code | no fact |
| 293 | not this shape, a pilot | no code | no fact |
| 323 | not this shape, a model trial | Roman ruled "no switch, qwen3.5:9b stays in every seat" (observed: part d) | no fact |

## The doubt

1. Each reader count comes from grep on names and patterns, so each is a lower bound (reasoned).
2. The reach units differ by fact: functions for most, call sites for F22, lists and sites for F31. The ranking mixes them (reasoned).
3. F25's count of refusals that name a call without `_offer` is not counted.
4. The landed-commit half of F26 is not re-counted at head.
5. The night links come from the facts file and the night 170 read. This audit did not re-read the night records (reasoned).
