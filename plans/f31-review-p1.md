# F31 review, pass 1: fa317629 on f31root

Verdict: the commit is sound, and no finding is high. The suite of the docs
doors is green, 161 passed. Five findings are low. Two of them need a line
in the DECISIONS.md row, not a code change.

## (a) Verdicts on the points

1. Partly. `asks_for_docs` matches "docstring", "document" and "help text" as whole words, "documentation" included. It also matches "documents", "documented" and "documenting". It does not match "undocumented". The ruling's reading ("ask for") supports the verb forms and "undocumented". The bare word match also admits the noun "documents" and a negated mention (finding 1, finding 5).
2. No missed reader. `_ABOUT_TEXT` asks whether a sentence names source text, so it keeps "comments" and leaves out "help text" (frame 321, review 1). `_HEADLINE_NAMES_DOCS` asks whether a ticket headline starts a refusal, and frame 322's review keeps it narrow. Each answers a different question.
3. Yes, a docstring line now meets `ver_opt_show_py_help`. The test `test_a_help_text_criterion_takes_a_docstring_line` passes. The ruling of 2026-10-27 accepts this result, so it is not a defect. The commit's sentence "a help string is a code line, so it meets that criterion anyway" is true. It does not stop a pass on a docstring line alone.
4. The form matches the file: a dated heading, a ruled paragraph, a rule paragraph, and "The fix is". The quote matches `plans/stack.md` line 1357 word for word. One context clause overstates the 2026-10-24 ruling (finding 4).
5. None. Every reader of `_NAMES_DOCS`, `_ASKS_FOR_DOCS`, `_ASKS_FOR_NOTES`, `_asks_for` and `_asks_for_docs` now reads `asks_for_docs` or `_asks_for_notes`. A grep of the tree outside `plans/` finds no other reader. One case comment still names the old list (finding 3).

## (b) Findings

1. `rota/roles/api.py:14474` (`_DOCS_WORDS`). Low. CONFIRMED. The reader matches a ruled word that a behaviour criterion only mentions. Night 142's `c2_flag_triggers_version_string` says "it does not affect help text", and `asks_for_docs` returns True. Night 157's `crit_show_python_help` says "must not describe" the help text, and it also returns True. The reader also returns True for "loads all documents", "The Document class" and "behaves as documented". At the pass door a docstring line then counts as evidence for these criteria. Fix: record the negated mention as a known reach in the DECISIONS.md row, and pin night 142's c2 in a test.
2. `rota/roles/api.py:5862` (`_docs_ticket_refusal`). Low. CONFIRMED. The specify and respecify doors now read `_asks_for_notes`, so "changelog" admits a criterion on a docstring ticket. The old `_NAMES_DOCS` held no "changelog". The probe shows "The changelog names the shorten fix." passes now and was refused before. No ruling covers this widening, and no saved night text renders it. Fix: read `asks_for_docs` plus a bare "docs" at this door, or record the widening as reasoned in the row.
3. `tests/rota/cases/l1_terminologist_docs.yaml:36`. Low. CONFIRMED by reading. The comment says "the five words of `criteria.specify`", and the predicate matches substrings. The door now matches whole words and adds "changelog". The case and the door now disagree on "load_document" and on "changelog". Fix: name `_asks_for_notes` in the comment, and align the word list with it.
4. `rota/DECISIONS.md:1557`. Low. CONFIRMED by reading. The row says a build session dropped two words "from his ruling of 2026-10-24 01:05". The row of 2026-10-24, lines 1529 to 1534, marks the word list as "reasoned: the general form", and his words were "Yes". The ruling of 2026-10-27 is the first ruling of the words. Fix: write "from the rule reasoned from his ruling of 2026-10-24 01:05".
5. `rota/roles/api.py:14474`. Low. PLAUSIBLE. "undocumented" does not match, because no word boundary sits before "document". A criterion such as "no public function is undocumented" asks for documentation. No saved night text holds the word, so no case renders it. Fix: add an optional "un" before "document" in `_DOCS_WORDS`, with a test.

Outside the points: none past findings 2 and 3. `_docs_test_note` reads `asks_for_docs` only, and its note sits before the offer. Both test-file refusals carry it.

## (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/c66eae69-d69c-45cb-8d68-947dc45d2ac1/scratchpad/f31p/probe_texts.py`: read 573 distinct criteria texts from every `D:/repos/rota/.rota/clickI_night*.db`, opened immutable. It compared the old readers with the new ones. The pass door gained 4 texts (nights 88, 142, 157, 160) and lost 0. The specify door gained 0 and lost 0.
- An inline `python -c` call printed night 142's c2 text in full. It ran `asks_for_docs` on seven edge texts: "undocumented" False, "documents" True, "Document class" True, "as documented" True, "help-text" True, "helptext" False.
- An inline `python -c` call ran `_asks_for_notes` and the old `_NAMES_DOCS` test on "The changelog names the shorten fix.": True and False.
- `pytest` on `test_f31_asks_for_docs.py`, `test_verdict_lines.py`, `test_frame322_docs_ticket.py`, `test_frame321_prints_prose.py` and `test_frame306_check_note.py` in `C:/Users/roman/rota_f31`: 161 passed. The full gate did not run, because no point needs it.

## (d) Usage

Input tokens: about 46k. Output tokens: about 7k. Total: about 53k. The figures are estimates from the context count.
