# Frame 362, slice pass 1, review of `0756c7eb` (the harvester)

Verdict: fix. The witnesses and the contradiction are right. The record has two write defects, and both must land before the push pass reads the bindings.

Worktree `C:/Users/roman/rota_r362s` at `0756c7eb`, on top of `358cb08b`. The icalendar root is `D:/tmp/rota-live/icalendar` at `99619246`. The new test file passes 19 of 19 at this commit.

## (a) Verdicts by point

1. Pass. All five key witnesses exist with the reported ids. The fold pairs with both "75 characters" lines, and no false pair exists on icalendar.
2. Over-push. `parser/string.py` gets 106 candidates and 9,595 characters, and 73 of them (7,096 characters) are project-wide. See finding 3.
3. Pass. 49 of 84 source files cite RFC 5545, and the description binds all 49. The 9 files that cite another RFC only get none of it.
4. Partial. A same-commit run writes 0, a new commit re-stamps 185, and the dry3w7 copy gains both tables. The bindings never refresh, see finding 2.
5. Defect. The hook runs at `boot.py` 115 and costs 16.0 s on icalendar in autocommit, 1.38 s in one transaction. A fault stops the onboarding.
6. Pass with one caveat. Only `harvest.record` writes the two tables. The id is stable across runs and machines, but not across a line shift (finding 8).
7. Pass. The longest text is 380 characters, a CI log line. A docs preservation witness is at most 5 lines and 192 characters, and the seat can cite its line range.
8. Not material, except the `:rfc:` form. The column rename and the `symbol` rule are sound. The `:rfc:` form adds 27 standard candidates to the `string.py` push (finding 4).

## (b) Findings

1. `rota/onboarding/harvest.py` 529-552. Severity high. CONFIRMED. `record` runs on the autocommit connection of `db.init_db` (`db.py` 142) with no transaction. Each of 7,790 statements commits alone, so the record costs 16.0 s. Inside one `BEGIN IMMEDIATE` the same record costs 1.38 s. A fault at the 50th `bind` left 50 rows stamped with the commit. The next `record` at that commit then returned 0 and kept the 50 rows for good. Fix: wrap the body of `record` in `BEGIN IMMEDIATE`, `COMMIT` and a rollback on error, as `indexer.build` does at 504.
2. `rota/onboarding/harvest.py` 549-551. Severity high. CONFIRMED. `INSERT OR IGNORE` on the key (`witness_id`, `path`) never removes or re-rules a binding. On a fixture, commit A bound the `foolib` dependency project-wide to 3 files. At commit B `pkg/a.py` imports `foolib`, and `bind` returns rule `dependency` on `pkg/a.py` only. The record still holds the 3 `project_wide` rows. A stale candidate also keeps all its bindings. Fix: delete the candidate's bindings before the insert, and drop the bindings of candidates the new harvest did not find, inside the transaction of finding 1.
3. `rota/onboarding/harvest.py` 511-516. Severity low for this slice, high for the push pass. CONFIRMED. The fallback sends 73 candidates and 7,096 characters to `parser/string.py`. Of the 73, 56 are `doc_claim` rows that cite no standard, 20 of them from `docs/contribute`, for example "The former extension supports Google style docstrings". The dive measured the same and advised to drop the kind (deep dive line 57 and 85). Fix: a `doc_claim` that cites no standard binds nothing and stays for the Architect only, which cuts the project-wide set on `string.py` from 73 to 17.
4. `rota/onboarding/harvest.py` 55 and 512-515. Severity low. CONFIRMED. The `:rfc:` role form lifts the standard rule from 3 to 39 candidates. `string.py` gets 27 of them, 2,180 characters, and most restate "RFC 5545" from reference docs. Fix: keep one bound candidate per cited standard, the root-file one first, and leave the restatements unbound.
5. `rota/onboarding/harvest.py` 67-70 and 411-412. Severity low. PLAUSIBLE. The pairing treats two different unit words of one family as a contradiction. "75 bytes" against "75 octets" names one fact, and "75 chars" against "75 characters" normalises to two units. Both would pair falsely on another repository. Fix: map the synonyms to one canonical unit before the compare (octet and byte, character and char).
6. `rota/onboarding/harvest.py` 288-292. Severity low. CONFIRMED. A source preservation candidate quotes one line. The #1501 carve-out splits into line 138 (`preservation`) and line 140 (`issue_comment`). Line 139, which names RFC 6868, is in no candidate. Fix: quote the contiguous comment block or the docstring sentence, as `_paragraph` does for docs.
7. `rota/onboarding/harvest.py` 153-154. Severity low. CONFIRMED. The docs set takes `docs/how-to/fuzz-testing-log.txt`, a CI log. It gives 2 `doc_claim` rows, one of them the longest text at 380 characters. Fix: read `.rst` and `.md` under `docs/` only, or skip a `.txt` file that is a log.
8. `rota/onboarding/harvest.py` 93-97. Severity low. PLAUSIBLE. The id hashes the line number and, for docs, the whole paragraph. An edit above a witness or beside it gives the witness a new id. The next pass ties a constraint's witness to a candidate id, so the tie breaks on an unrelated edit. Fix: the push pass decides the tie key, for example kind, path and text with no line, before it writes a tie.
9. `rota/onboarding/boot.py` 115. Severity low. CONFIRMED. A fault in `harvest.record` propagates out of `boot.onboard`, so `refresh_constraint_zero` and the report never run. The harvester is advisory, and the brief did not say it may stop the onboarding. Fix: catch the fault, record it as a stress, and continue.

Outside the points: finding 6, finding 7 and finding 9 come from reads outside the numbered points. The clock lint at `tests/rota/test_schema_has_no_clock.py` 13 matches "date" inside any word, such as "candidate" or "update". The rename to `witness_id` is a correct local answer, and a word boundary in the lint is the general fix.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/07f209e6-af4a-434b-ac50-5b4ac1e3f670/scratchpad/r362/`. Each one runs from the worktree root with the worktree first on `sys.path`.

- `p1.py`: `init_db` in a temp directory, `record` on icalendar at `99619246`. It wrote 185 in 16.0 s. A second run wrote 0 in 0.0 s. The database is `C:/Users/roman/AppData/Local/Temp/tmpohtpmdxi/h.db`.
- `p2.py`: the counts by kind and by rule, the five witnesses by id and text, the `contradicts` rows. Only the three fold rows have a non-empty `contradicts`.
- `p3.py`: the push to `parser/string.py` by rule and by kind, the RFC 5545 citers (49 of 84), the 9 other-RFC files outside the description's set, the longest texts.
- `p4.py`: the cost split (tree 0.53 s, harvest 0.48 s, bind 0.31 s), a profile, and the dry3w7 copy. The copy had neither table, gained both, harvested 185, and re-stamped 185 at a new commit.
- `p5.py`: `record` inside one transaction (1.38 s), a fault at the 50th `bind` (50 rows kept, re-run writes 0), and the fixture for the stale bindings.
- `p6.py`: `boot.onboard` with a raising `harvest.record`. The onboarding raised.
- `pytest tests/rota/test_f362_harvest.py -q`: 19 passed in 21.40 s.

## (d) Usage

The harness shows no exact counts. The estimate is about 70k input tokens and about 12k output tokens, about 82k in total.
