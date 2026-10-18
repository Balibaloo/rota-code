# Frame 287, step 4: the law each night-built door enforces

Meta workflow, read of the rota workflow's doors. Read at 1b72d475 on
2026-10-18 02:57 by an Opus agent, read-only. The script of step 4 adds
column 4 to each door's comment. The session judges this table.

## Method

1. A grep of `night[s]? [0-9]` over `rota/` (no testkit, tools or tests) found 522 lines in 17 files. A script grouped the adjacent comment lines into blocks, with the enclosing function and the first `return` or `raise` after each block.
2. A door is one refusal or one predicate. One comment block over one branch is one door. Helpers that only feed one door are one row with that door.
3. Each door's clause came from `rota/LAWS.md` (411 lines, read in full). The frame column copies the frames that the comment names. `git log -S` was not run, so a door whose comment names no frame shows `-`.
4. The marks: (observed) means the law's text names this case. (reasoned) means the law covers it by this read. `no law, mech` means the door keeps a call well formed (an id, a parse, an import, a span) and rules on no content. `no law, rules` means the door rules on content where no law does.

Every row of the tables below is (reasoned: this read, 2026-10-18) as a placement. The mark in column 3 is the strength of the law's text for that placement.

## rota/roles/api.py

| Door (line, function, refusal's first words) | Nights; frame | Law and mark | Line for the script |
|---|---|---|---|
| 705 `refuse_repeated_sentence`, "raise ValueError(" | 132; 142 | law 7, "never repeat the question" (observed) | `# law 7: any touch after the first must reframe, never repeat the question` |
| 722 `refuse_signoff_without_draft`, "refs naming every draft item" | 82, 150; 261 | law 8, "per-item approval ... presented as one document" (observed) | `# law 8: signoff is per-item approval, presented as one document` |
| 777, 793 `answered_question`, `refuse_answered_question` | 135; 142 | law 7, "never repeat the question" (observed) | `# law 7: any touch after the first must reframe, never repeat the question` |
| 822 `brief_intake`, "a bare reply is refused" | 132; - | law 2, enforcement row "message bodies carry refs" (observed) | `# law 2: judgement crosses a role boundary only as ids and states` |
| 838 `brief_intake`, shared function words | 133, 136, 137; 193 | no law, mech | - |
| 897 `brief_segment`, "is a statement, and a statement is not an" | 135; 142 | no law, mech (a foreign key) | - |
| 972 `brief_segment`, the span holds the words | 135; 142 | law 8, L1 fidelity, "did I hear you right" (reasoned) | `# law 8: L1 fidelity: the principal ratifies the segmented statements` |
| 994 `brief_segment`, words on file are a row already | 121, 135; 142, 193 | law 14, "a statement issued eleven times" (observed) | `# law 14: a re-emitted act is the same row, never a new one` |
| 1049 `brief_segment`, a statement keeps its id | 135; 142 | law 14, "Identity stamps from birth content" (reasoned) | `# law 14: identity stamps from birth content, never a model's id` |
| 1107 `brief_ratify`, `contested_refusal` | 138; 193 | law 8, L1, "the principal ratifies" (reasoned) | `# law 8: L1 fidelity: the principal ratifies the segmented statements` |
| 1330 `_page_reply_fault`, "the new text is his reply word for word" | 150; - | law 8, "Downstream roles re-decompose into their own artefacts" (reasoned) | `# law 8: downstream roles re-decompose into their own artefacts` |
| 1392 to 1488 `_assert_words_fault`, "is the principal's own words, and this wake names no" | 145, 146, 149; 129 | law 11, "decided when its refs reach a ratified statement" (reasoned) | `# law 11: decided rows rest on a ratified statement or landed ruling` |
| 1660 `problem_assert`, `raise ValueError(fault)` | 146; 221 | law 11, same clause (reasoned) | `# law 11: decided rows rest on a ratified statement or landed ruling` |
| 1681 `problem_assert`, items asserted again word for word | 18; - | law 14, "a model re-emits an act it already performed" (observed) | `# law 14: a re-emitted act is the same row, never a new one` |
| 1703 `problem_assert`, paraphrased past the door | 19; - | law 11, "decided outranks observed" (reasoned) | `# law 11: decided rows rest on a ratified statement or landed ruling` |
| 1845 `problem_assert`, the intent thread's first link | 37; - | law 11, "A row ... rests on what it cites" (reasoned) | `# law 11: a row rests on what it cites` |
| 1880 `problem_set_approval`, the relay cannot undo a ruling | 136; 190 | law 1, "exactly one writing role per row" (reasoned) | `# law 1: one writing role per row; a journal entry has one author` |
| 1894 `problem_set_approval`, the relay cannot contest the approved | 147; 238 | law 1, same clause (reasoned) | `# law 1: one writing role per row; a journal entry has one author` |
| 1976 `problem_describe`, "is the principal's own words, so it asks" | 91; 80 (docstring) | law 11, "decided ... ratified statement" (reasoned) | `# law 11: decided rows rest on a ratified statement or landed ruling` |
| 2283 `model_adopt`, a string is one id | 136; 190 | no law, mech | - |
| 3630, 3684 `_capped_ids`, `_bound_exit` | 95; - | no law, mech (refusal text) | - |
| 3853 `findings_find`, a finding id names one row across batches | 120, 128; 178 | law 14, "never from an id a model supplies" (reasoned) | `# law 14: identity stamps from birth content, never a model's id` |
| 3867 `findings_find`, "A finding names a constraint from" | 95; - | law 12, "Each constraint declares bindings" (reasoned) | `# law 12: review triggers on diff-touched grains intersecting bindings` |
| 3883 `findings_find`, the grain is a file the diff changed | 65; - | law 12, "intersection of diff-touched grains with bindings" (observed) | `# law 12: review triggers on diff-touched grains intersecting bindings` |
| 3913 `findings_find`, a satisfied row names a changed file | 114 to 128; 178 | law 12, same clause (observed) | `# law 12: review triggers on diff-touched grains intersecting bindings` |
| 3928 `findings_find`, k0 only when no other constraint is in range | 118; 178 | law 12, "Constraint zero ... starved by positive survey records" (reasoned) | `# law 12: constraint zero is starved by survey, never by judgement` |
| 4533 `tickets_slice`, observed items are not work | 9; - | law 11, "observed ... found, not chosen" (reasoned) | `# law 11: an observed row was found, not chosen; nobody asked for it` |
| 4661 `_batch_is_subject` | 98; - | no law, mech | - |
| 4733 `_area_resolves` | 85; - | no law, mech | - |
| 4850 `_vet_surface`, a callable that does not exist yet | 56; - | no law, rules | - |
| 4884 `_surface_outside_batch` | 142; 215 | no law, rules | - |
| 4976 to 5063 `_named_new_callables`, `_named_existing_callables`, `_surface_names_what_the_item_names`, "invented" surfaces | 8, 9, 70, 113, 116; - | law 11, "A row ... rests on what it cites" (reasoned) | `# law 11: a row rests on what it cites` |
| 5189 `criteria_specify`, "this says what ... says, in nearly the same words" | 18; - | law 14, "fuzzy behind named guards" (observed) | `# law 14: exact match at the door; fuzzy behind named guards` |
| 5214 `criteria_specify`, "six is many" | 38; - | law 7, contradicts (see findings) | `# law 7: every cap is a ruling, declared in config` |
| 5261, 5286, 5330, 5343, 5382 `criteria_specify` cues, `_named_tokens`, `_item_callables`, `_item_names`, `_wake_mode_tools` | 145 to 147; 202, 256 | no law, mech (word parsers) | - |
| 5430, 5487, 5577 `_surface_move_fault`, `route`, `criteria_respecify`, the surface move | 145 to 147; 202, 226 | law 11, "A row ... rests on what it cites" (reasoned) | `# law 11: a row rests on what it cites` |
| 5557 `criteria_respecify`, the surface is read first | 145; 226 | no law, mech | - |
| 5586 `criteria_respecify`, `body_text` not read | 144 to 146; - | no law, mech | - |
| 5603, 5624 `criteria_respecify`, contested words never come back | 144; 226, 227 | law 9, "A ratified amendment ... drops it to pending" (reasoned) | `# law 9: a ratified amendment drops the item to pending, stops batches` |
| 5701 `criteria_load`, another batch's test | 147; 239 | no law, mech | - |
| 5955 `batches_annotate`, the correction replaces the prediction | 136; 190 | law 12, "It is a *prediction*, never a permission" (reasoned) | `# law 12: the touch set is a prediction, never a permission` |
| 6088, 6135 `_verb_words`, `tests_triage`, the criterion says what the request says | 91; - | no law, rules | - |
| 6184 `tests_triage`, the third question climbs | 63; - | law 6, "Exhaustion escalates one rung at a time" (observed) | `# law 6: exhaustion escalates one rung at a time` |
| 6366 `_invented_literals`, the stdin shield | 106; - | no law, mech | - |
| 6460 to 6675 `_shields_input`, `_invoked_command_calls`, `_plain_invoked`, `_callable_invoked` | 119, 136 to 149; 230, 254 | no law, mech (the stdin family) | - |
| 6821 to 7162 `_returns_factory`, `_factory_misuse`, `_named`, `_plain_decorated`, `plain_def` | 119, 127, 128, 138 to 140; 200 | no law, mech (decorator factories) | - |
| 7273 `tests_encode`, a routed criterion was judged already | 91; - | no law, mech | - |
| 7349 to 7456 `tests_encode`, the stdin traps, `raise Wall(` | 50, 52 to 54, 57, 149; 254 | no law, mech | - |
| 7515 to 7641 `tests_encode`, unbound names and import lines | 46, 81, 142, 143, 149; 215, 222 | no law, mech | - |
| 7713, 7728, 7759 `tests_encode`, `_raises_a_check`, `_vacuous`, a test that cannot fail | 63, 152, 153; 147, 273, 277 | law 8, "Gates are predicates, not judgement" (reasoned) | `# law 8: gates are predicates; a test that cannot fail is no gate` |
| 7937 to 8270 `_src`, modules, imports, references, lambdas | 23 to 25, 55, 56, 80, 142, 148; 215, 230 | no law, mech | - |
| 8331 `_src`, the assumptions detector | 28; - | law 8, "nothing ships whose assumptions the principal never saw" (observed) | `# law 8: a lineage's open assumptions are presented at its gates` |
| 8365, 8382 `_src`, `_def_fact`, a decorator factory prints nothing | 80, 128; 131, 177 | no law, mech | - |
| 8449 `_kind`, prints only when the material says so | 42; - | no law, rules | - |
| 8463 `_kind`, no lift by a ledger row | 45; - | law 11, "A ledger entry is resolved by a decision that names it" (reasoned) | `# law 11: a ledger entry is resolved only by a decision naming it` |
| 8506 `_kind`, the door stages the `invented` row | 46, 120 to 139; 204 | law 8, "open assumptions are presented at its gates" (reasoned) | `# law 8: a lineage's open assumptions are presented at its gates` |
| 8524 `_kind`, a byte-for-byte re-encode is no write | 126, 147; 152, 239 | law 14, "a model re-emits an act it already performed" (observed) | `# law 14: a re-emitted act is the same row, never a new one` |
| 8550, 8561 `_kind`, project-test signs, the challenge refs | 113 to 120; 128, 135 | no law, mech | - |
| 8596, 8679 `_kind`, one test per criterion | 117; 123 | law 14, "Some keys are cardinality, not content" (observed) | `# law 14: some keys are cardinality, not content` |
| 8743, 8784, 8799 `tests_load` | 103, 138, 141; 101, 195, 210 | no law, mech | - |
| 8876 to 9347 the words door: `_is_team_note`, `_ruling_word`, `_line_reading`, `_line_cues`, `built_line_faulted`, `_line_refusal`, `_faulted_approve`, `_unnamed_contest`, `_agreed_contest`, "The words fault" | 121, 133, 136 to 151, 154; 197, 234, 250, 256, 258, 282 | law 6, "never a ledger row written on the principal's behalf" (reasoned) | `# law 6: nothing is ruled on the principal's behalf` |
| 9605 `rulings_rule`, a team note takes no revise | 136; 190 | no law, rules | - |
| 9623 `rulings_rule`, a batch line correction goes to the Architect | 136; 142, 190, 255 | law 3, "routes to the writer of the artefact holding the answer" (observed) | `# law 3: a message routes to the writer of the artefact holding the answer` |
| 9644 `rulings_rule`, the refusal names the key | 139; 197 | no law, mech | - |
| 9663 `rulings_rule`, no offer of the item contest | 136 to 149; 255 | no law, rules | - |
| 9675 `rulings_rule`, a contest rests on the words | 146; 234 | law 6, same clause as the words door (reasoned) | `# law 6: nothing is ruled on the principal's behalf` |
| 9680 `rulings_rule`, a merged line's fault is the item's | 133, 136; 255 | law 9, "Batches are complete feature sets, immutable once formed" (reasoned) | `# law 9: batches are immutable once formed; only scope recomposes one` |
| 9709 `rulings_rule`, the description is no part of the request | 150; 258 | no law, rules | - |
| 9782 `rulings_line`, "no open page" | 85; - | no law, mech | - |
| 10069 `ledger_log`, an assumption is about a row | 133, 136; 190 | law 11, "A row ... rests on what it cites" (reasoned) | `# law 11: a row rests on what it cites` |
| 10148 `ledger_log`, "Say the actual thing" | 136; 190 | no law, rules (a brief rule) | - |
| 10237, 10247 `_restates`, `_misplaced_conflict` | 143; - | no law, rules | - |
| 10308 `_refuse_an_echo` | 136; - | law 7, "never repeat the question" (reasoned) | `# law 7: any touch after the first must reframe, never repeat the question` |
| 10509 `decisions_author`, a supersede of the principal's decision | 148; 243 | law 6, "never a ledger row written on the principal's behalf" (reasoned) | `# law 6: nothing is ruled on the principal's behalf` |
| 10525 `decisions_author`, a write under an existing id | 143; 200, 219 | law 1, "one author per entry, append-only" (observed) | `# law 1: one writing role per row; a journal entry has one author` |
| 10742 `_line_held` | 130; 180 | no law, mech | - |
| 11051, 11077 `verdicts_load`, `verdicts_rule`, "is not the finding you were woken about" | 94, 101; - | law 8, "harness, then Critic, then Architect" (reasoned) | `# law 8: the merge gate runs harness, then Critic, then Architect` |
| 11654 `code_prose`, asked by path | 38; - | no law, mech | - |
| 12536 `challenge_load`, a finding review names no claim | 94; 88 | law 2, "A finding is {constraint_id, status, grain}" (reasoned) | `# law 2: judgement crosses a role boundary only as ids and states` |
| 12730, 12770 `challenge_break`, `challenge_vacuous`, "say what makes it empty: why=" | 88, 94; 59 | law 11, "a seat's own inference, with the reason on file" (reasoned) | `# law 11: a reasoned row carries its reason on file` |
| 13175 `code_source` | 11; - | no law, mech | - |
| 13218, 13233, 13323 `_batch_diff`, `_removed_lines`, `code_diff`, the fork and not HEAD~1 | 98, 100; 97 | no law, mech | - |
| 13352, 13476, 15592 `code_diff`, `_unchanged_note`, `_present`, "No commit holds it yet" | 62, 97; 93 | law 4, "The uncommitted change never existed" (observed) | `# law 4: an uncommitted change never existed` |
| 13368, 16917, 16957 `code_diff`, `_changed_unnamed_defs`, definitions no criterion names | 47, 48, 55; - | law 12, "make 'was this change incidental?' answerable" (observed) | `# law 12: the touch set is a prediction, never a permission` |
| 16934 `_changed_unnamed_defs`, the batch's base | 154; 220 | law 12, same clause as `fence.check` (reasoned) | `# law 12: the touch set is a prediction, never a permission` |
| 13626, 13846 to 13865 `_module_load_error`, `_unbound_name_hint` | 142, 143 to 149; 215, 222 | no law, mech | - |
| 14026 `code_write` | 16; - | no law, mech | - |
| 14047 `_refuse_after_challenge`, `raise EndRefusal(` | 139; 200 | no law, rules | - |
| 14194 to 14873 `_empty_write`, `_end_lost`, `_whole_parent`, `_near`, `_root_importable`, `_parse_compile` | 12, 16, 37, 40, 52, 53, 96, 97, 99, 120, 127; 92, 135, 136, 173 | no law, mech (spans and parses) | - |
| 14919 to 14992 `_decorator_name`, overload stubs, one name one definition | 32, 35, 42; - | no law, mech | - |
| 15301 to 15499 `_present`, imports, cycles, lost lines, a write already held | 49, 51, 97, 113, 120, 145; 229 | no law, mech | - |
| 15719 `_revert_refusal` | 124; - | no law, mech | - |
| 15861 `code_commit`, the parts below the tree | 22; - | no law, mech | - |
| 15895 `code_commit`, churn | 30; - | law 4, "Failure is bounded" (reasoned; the law names "the churn door") | `# law 4: failure is bounded` |
| 15915 `code_commit`, the Tester's files are not the Developer's diff | 50; - | law 1, "exactly one writing role per row" (reasoned) | `# law 1: one writing role per row; a journal entry has one author` |
| 15930 `code_commit`, "nothing changed" | 139; 200 | no law, mech | - |
| 147, 16008 to 16017 `Ctx.dropped`, `_unread_drop_refusal` | 121, 153, 154; 140, 283 | no law, mech | - |
| 16189 `_changed_kept` | 149; - | no law, mech | - |
| 16370 `_outside_prediction`, a test path is never a stray | 41; - | law 1, "exactly one writing role per row" (reasoned) | `# law 1: one writing role per row; a journal entry has one author` |
| 16434, 16466 `batches_judge_touch`, `_covers` | 41, 145; 228, 286 | no law, mech | - |
| 17326 to 17636 `_repair_broken_strings`, `_escape_note`, `_tail_drop`, `moved`, `_lost_statements` | 97 to 99, 127, 144, 145; 95, 173 | no law, mech | - |
| 457 `EndRefusal` (a class, the session ends) | 125; 153 | no law, mech | - |

## rota/core/predicates.py

| Door | Nights; frame | Law and mark | Line for the script |
|---|---|---|---|
| 298 `contested`, a set-aside item wakes no owner | 137; 193 | law 9, "stops its batches" (reasoned) | `# law 9: a ratified amendment drops the item to pending, stops batches` |
| 513 `term_collision`, an answer that missed the question parks the word | 84; - | no law, rules | - |
| 584 `grouping`, an abandoned batch is not the ticket's | 137; 80, 190, 193 | law 9, "the revocation ... stops its batches" (reasoned) | `# law 9: a ratified amendment drops the item to pending, stops batches` |
| 772 `tests_missing`, per criterion | 46, 147; 190, 239 | law 8, "Gates are predicates" (reasoned) | `# law 8: gates are predicates, not judgement` |
| 1328 `review`, every criterion has its test | 147; 239 | law 8, "harness, then Critic, then Architect" (reasoned) | `# law 8: the merge gate runs harness, then Critic, then Architect` |
| 1361 `finding_review` | 94; - | law 8, same clause (reasoned) | `# law 8: the merge gate runs harness, then Critic, then Architect` |
| 1413 `verdict_failed`, at the head commit only | 101; - | law 8, same clause (reasoned) | `# law 8: the merge gate runs harness, then Critic, then Architect` |
| 1552 `preempt`, the start's order | 92; - | law 9, "Preemption: if a reorder bumps a batch ahead" (observed; the function cites law 9 at another line) | `# law 9: a reorder ahead of the running batch preempts it` |
| 1560 `preempt`, past the cap with every rung asked | 93; 83 | law 6, "Budget exhaustion escalates one rung" (reasoned) | `# law 6: exhaustion escalates one rung at a time` |
| 1667 `quarantined`, the key carries its refs | 37; - | law 6, "quarantined says out loud what passed its cap" (observed) | `# law 6: a wake past its cap is quarantined and said out loud` |
| 1682, 1690 `quarantined`, a park owns the key, a set-aside item | 133, 137; 142, 193 | law 6, same clause (reasoned) | `# law 6: a wake past its cap is quarantined and said out loud` |
| 1776 `agenda` | 136; - | law 6, "the top rung is a page (agenda)" (observed) | `# law 6: at the Liaison it is a page, a hold or a note` |
| 2296 `touch_strayed` | 32; - | law 12, "make 'was this change incidental?' answerable" (observed) | `# law 12: the touch set is a prediction, never a permission` |

## rota/core/sandbox.py

| Door | Nights; frame | Law and mark | Line for the script |
|---|---|---|---|
| 275, 388 `_scalar_id_fault`, `validate_args` | 113 to 126; 164 | no law, mech | - |
| 1066 `_answer_mode_challenge_refusal`, "No words" | 138, 139; - | law 2, "Conclusions travel; reasoning stays home" (reasoned) | `# law 2: judgement crosses a role boundary only as ids and states` |
| 1132 `_red_line_refusal` | 142; - | no law, mech | - |
| 1235, 1259, 1270, 1319 `_send`, refs of None, the failing tests, the test's side | 26, 47, 58; 207 | no law, mech | - |
| 1302 `_send`, a project test has no side to challenge | 55; - | law 3, "Fact artefacts ... generate no contact" (reasoned) | `# law 3: fact artefacts generate no contact; nobody to ask` |
| 1402 `_escalation_over_removed_grain` | 22; - | no law, mech | - |
| 1524, 1561 `project_tests_fact` | 113, 140; 207 | no law, mech | - |
| 1651, 1670, 2228 `_code_step`, `LANDED_CHALLENGES`, `_challenge_cap_refusal` | 113 to 124, 142; 200 | law 7, contradicts (see findings) | `# law 7: every cap is a ruling, declared in config` |
| 1831, 1850 `_sender_prompt`, `_quoted_body_gone` | 142; - | no law, mech | - |
| 1905, 1912 `_without_own_reasons` | 144; 200 | law 2, "reached by following a ref" (observed; `_stage_reason` cites it) | `# law 2: the reasoning is reached by following a ref` |
| 2119, 2351 `architect_decision_on`, `_escalation_or_step` | 153; 278 | law 3, "routes to the writer of the artefact holding the answer" (reasoned) | `# law 3: a message routes to the writer of the artefact holding the answer` |
| 2382, 2414 `_end_form`, `_encodes_refused` | 124, 126; 165 | no law, mech | - |
| 2490, 2504, 2524 `_challenge_repeat_refusal` | 119, 122 to 124; 132, 145 | law 7, "never repeat the question" (observed); its cap `UNANSWERED_CHALLENGES` is a finding | `# law 7: any touch after the first must reframe, never repeat the question` |
| 2547 to 2596 `_same_refs_refusal`, act on the answer | 106, 109, 142; 200 | law 7, same clause (observed) | `# law 7: any touch after the first must reframe, never repeat the question` |
| 2643 `_same_refs_refusal`, the rung is the Architect | 111; - | law 6, "The ladder is Developer → Architect" (observed) | `# law 6: exhaustion escalates one rung at a time` |
| 2675 `_refuse_confirm_off_entry` | 138; - | law 8, L1 fidelity (reasoned) | `# law 8: L1 fidelity: the principal ratifies the segmented statements` |
| 2895 `stage`, a reopen names the amended item | 22; - | law 9, "A ratified amendment ... drops it to pending" (reasoned) | `# law 9: a ratified amendment drops the item to pending, stops batches` |
| 2912 `stage`, at most seven open assumptions | 17; - | law 8, "open assumptions are presented at its gates" (observed); the cap contradicts law 7 | `# law 8: a lineage's open assumptions are presented at its gates` |
| 2992 `stage`, a word the principal wrote | 29; - | no law, rules | - |
| 3071 `stage`, one open question per criterion | 29; - | law 7, "never repeat the question" (observed) | `# law 7: any touch after the first must reframe, never repeat the question` |
| 3127, 3145 `stage`, the Tester's answer, `EndRefusal` | 80, 125; - | no law, rules (3127); no law, mech (3145) | - |
| 3194, 3200 `stage`, the second answer, the answered question | 132, 135; 142 | law 7, same clause (observed) | `# law 7: any touch after the first must reframe, never repeat the question` |
| 3439 `stage`, the request's rows are added | 133, 136; 190 | law 8, "presented as one document" (reasoned) | `# law 8: signoff is per-item approval, presented as one document` |
| 3674 `stage`, a contested statement is not delivered | 138; 193 | law 8, L1 (reasoned) | `# law 8: L1 fidelity: the principal ratifies the segmented statements` |
| 3742 `stage`, the rows say whether a test exists | 142; 213 | no law, mech | - |
| 3789 `stage`, only contested and revised lines travel | 132; 142 | law 2, "only as structured findings -- ids and states" (reasoned) | `# law 2: judgement crosses a role boundary only as ids and states` |
| 3824 `stage`, a test row travels as its criterion | 144; 213 | law 3, "no second, hand-maintained list" (observed: the comment says "a new edge in the graph") | `# law 3: contacts derive from read and write edges; no second list` |
| 3993 `stage`, "quotes= has an empty entry" | 58; - | law 13, contradicts (see findings) | `# law 13: no date appears in a prompt` |

## rota/core/fence.py and rota/core/harness.py

| Door | Nights; frame | Law and mark | Line for the script |
|---|---|---|---|
| fence 150, 152 `check` | 38, 143; 220 | covered: the docstring cites law 12 | - |
| harness 56, 304 `tester_paths`, `record_base_run` | 140; 207 | no law, mech | - |
| harness 193 `_run_one`, warning hygiene | 55; - | no law, rules | - |
| harness 200 `_run_one`, the caught exception | 138; 195 | no law, mech | - |

## rota/core/scheduler.py and rota/core/lifecycle.py

| Door | Nights; frame | Law and mark | Line for the script |
|---|---|---|---|
| scheduler 440 `tick_batch_start`, a re-fire is the same session | 73; 58 | law 4, "Failure is bounded" (reasoned) | `# law 4: failure is bounded` |
| scheduler 1060, 1089 `tick_agenda`, `reaches_request` | 136, 141; 190, 209 | law 6, "the top rung is a page (agenda)" (reasoned) | `# law 6: at the Liaison it is a page, a hold or a note` |
| scheduler 1098 `reaches_request`, real ids to copy | 20; 190 | law 14, "never from an id a model supplies" (reasoned) | `# law 14: identity stamps from birth content, never a model's id` |
| scheduler 1411 `waiting_on` | 143; 204 | no law, mech | - |
| scheduler 1536, 1539 `next_batch`, one order | 92; - | law 9, "Preemption: if a reorder bumps a batch ahead" (reasoned) | `# law 9: a reorder ahead of the running batch preempts it` |
| scheduler 1556 `next_batch`, past `loop_cap` | 93; 87 | law 6, "Budget exhaustion escalates one rung" (reasoned) | `# law 6: exhaustion escalates one rung at a time` |
| scheduler 1603 to 1817 `park_reds`, `park_ruling`, `park_message_rests`, `park_criterion_relay` | 121, 132, 133; 142, 190 | no law, mech | - |
| scheduler 1994 `resume_behind` | 133; - | no law, rules | - |
| scheduler 2056 `parked`, a given-up batch waits for the principal | 94; - | law 6, "a page, a hold or a note for the principal" (reasoned) | `# law 6: at the Liaison it is a page, a hold or a note` |
| scheduler 2138, 2303 `note_dispatch`, `quarantine_stalled` | 92; - | law 4, "past `message_attempt_cap` the message is quarantined" (reasoned; `release` cites law 4) | `# law 4: failure is bounded; past its cap a wake is quarantined` |
| lifecycle 203 `merge`, the Tester's bodies in their own commit | 50; - | law 1, "exactly one writing role per row" (reasoned) | `# law 1: one writing role per row; a journal entry has one author` |
| lifecycle 490 `_batch_notes` | 138; - | no law, mech | - |
| lifecycle 577 `mergeable`, "criteria without a test" | 147; 239 | law 8, enforcement row "`lifecycle.mergeable` returns the reason" (observed) | `# law 8: the merge gate runs harness, then Critic, then Architect` |
| lifecycle 608 `mergeable`, "touch strayed, unjudged" | 32; - | law 12, contradicts (see findings) | `# law 12: the touch set is a prediction, never a permission` |

## Findings

### Contradicts

1. **Caps outside config, law 7** (observed: `grep` of `config.py`, 2026-10-18). Law 7 says: "`rota/config.py` declares every cap and points to its ruling. A number written into a predicate is a decision made by whoever typed it." Four caps live as literals and not in `SETTINGS`:
   - `PAGE_ASSUMPTIONS = 7`, `rota/core/sandbox.py:34`, used by `stage` at 2912.
   - `UNANSWERED_CHALLENGES = 2`, `sandbox.py:1434`, ruled by "the judging session", not the principal.
   - `LANDED_CHALLENGES = 3`, `sandbox.py:1678`, the same.
   - `len(existing) >= 6` in `criteria_specify`, `rota/roles/api.py:5225`, ruled in the criteria brief.
   The script line for these doors names law 7 so the conflict shows. The fix is a frame: move the caps into `config.py` or amend law 7 (reasoned).
2. **A date in a refusal a seat reads, law 13** (observed: `sandbox.py:3993`). Law 13 says: "Dates, deadlines and durations appear in no artefact, no plan and no prompt." The generated `send` wrapper raises "quotes= has an empty entry ... (click night 58, 2026-09-14)". The seat reads that text as a tool result. A refusal is part of the prompt by this read (reasoned).
3. **A stray blocks the merge, law 12** (reasoned: `rota/core/lifecycle.py:608`). Law 12 says: "It is a *prediction*, never a permission -- nothing rejects a diff for straying outside it." `mergeable` returns "touch strayed, unjudged" until the Architect says foreseen or mistake. The door rejects nothing, but it holds the merge on the prediction. The defence is that the hold waits on a judgement and not on a refusal. The session rules which reading holds.

### No law, rules (a door that rules where no law does)

Fifteen doors rule on content with no law behind them (reasoned: this read). Most rest on a brief rule or a ruling of Roman in DECISIONS.md, which this read did not open.

- api.py: 4850 `_vet_surface`; 4884 `_surface_outside_batch`; 6088 and 6135 `tests_triage` (one door); 8449 `_kind` prints; 9605, 9663 and 9709 `rulings_rule`; 10148 `ledger_log`; 10237 and 10247 `_restates`, `_misplaced_conflict` (one door); 14047 `_refuse_after_challenge`.
- predicates.py: 513 `term_collision`.
- sandbox.py: 2992 and 3127 `stage`.
- harness.py: 193 `_run_one`.
- scheduler.py: 1994 `resume_behind`.

### No law, mech

Fifty-three rows of doors keep a call well formed and rule on no content (reasoned). The script adds no line to them. A mechanical door is not a ruling, so design.md section 2 does not reach it (reasoned).

### The frame 114 sign

`_present` at api.py 15389 cites law 12 for nights 47 and 48. `_changed_unnamed_defs` at 16917 cites the same nights and no law (observed). The row above gives it the law 12 line.

## Coverage: doors whose comment already cites a law

Counted by function, from a script over the comments (observed, 2026-10-18):

- `rota/roles/api.py`: 8 of 108 night-citing functions cite a law. The night blocks with a law: `findings_find` 3825 (14), `decisions_author` 10477 (11), `_decorator_name` 15001 (12), `_present` 15389 (12).
- `rota/core/predicates.py`: 2 of 12 (`unresolved` 6, `preempt` 9).
- `rota/core/sandbox.py`: 1 of 20 (`stage` 3635, law 2).
- `rota/core/fence.py`: 1 of 1 (`check`, law 12).
- `rota/core/harness.py`: 0 of 3.
- `rota/core/scheduler.py`: 2 of 14 (`tick_batch_start` 5, `release` 4).
- `rota/core/lifecycle.py`: 0 of 3.

## Totals

Counted by a script over the tables above (observed, 2026-10-18).

- Doors read: 161 rows. They hold 313 comment blocks, which carry 343 of the 522 night lines in the seven files read. A row can group the blocks of one function, so a row is one door or one family of doors.
- A law found: 93 rows (29 observed, 59 reasoned, 5 that contradict a law).
- `no law`: 67 rows (15 rules, 53 mech; the row of `stage` 3127 and 3145 holds one of each).
- `contradicts`: 5 rows on three laws. Law 7: api 5214, sandbox 1651 to 2228, sandbox 2912 (the cap only), and the cap of sandbox 2490 named in its row. Law 13: sandbox 3993. Law 12: lifecycle 608.
- Already covered: 1 row (fence `check`). The four api blocks that cite a law have no row.

## Left out

- `rota/core/runner.py` (105 night lines), `rota/roles/principal.py` (24), `rota/llm/toolproto.py` (23), `rota/core/db.py` (10), `rota/core/loop.py` (8), `rota/llm/llm.py` (4), `rota/core/cycles.py` (4), `rota/core/worktrees.py` (2), `rota/llm/profile.py` (1), `rota/core/plugins/_rota_caught.py` (1). The budget covered the five named files, scheduler and lifecycle first. A first pass of principal.py found page builders and `land`, which already cites law 6 at 2029 (observed).
- `git log -S` on the refusal texts was not run. The frame column holds only the frames that the comments name.
- DECISIONS.md was not read. A `no law, rules` door can rest on a ruling recorded there.
