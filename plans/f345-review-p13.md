# Review p13: pass R4 at 312b7592

## (a) Verdict

READY. No finding is high. Two findings are low.

1. Wake order: PASS. The clauses and the menus now come before `his_words`. The rebuilt wake is about 11,750 characters, so the cut at 12,838 no longer falls.
2. Other readers: PASS. Only `rota/core/runner.py` writes `his_words`, and only `test_seam2_word_per_line.py` reads it. `landing.md` and the cockpit do not name it.
3. The ask line: PASS. An `ask` alone sends the sentence. An `ask` with rulings drops the map and sends the sentence (api.py 14385 to 14401).
4. The once check: PASS. `refused` is a frozenset of exact refusal texts (api.py 13833), so the membership test is exact. The new test probe passes.
5. Tests: PASS. Two seam2 tests fail, and both fail at 283f6701 too. The runner files pass.
6. Outside: two low findings, below.

## (b) Findings

1. Low. PLAUSIBLE. `rota/roles/api.py` 14245. The new sentence follows every off-menu refusal. That includes a line where his words hold an option and the seat only misspelt the option. The seat can then ask the principal where it must correct one key. That costs his attention. Fix: say the ask sentence only when the line's words match no option, or put "correct the option" first.
2. Low. PLAUSIBLE. `rota/core/runner.py` 2502 with `api.py` 14084. The wake now shows keys such as "8 to 67". A seat that copies such a key into `rulings` gets the generic "is no clause and no page line" refusal. Fix: in that refusal, name the range key and tell the seat to use the clause key or one line number.
3. Note, not a defect. `test_a_row_on_two_lines_of_the_page_lands_a_word_on_each` and `test_two_words_on_one_ref_of_another_act_keep_one_row` fail at 312b7592 and at 283f6701. The error is "c1: the clause names no page line, and the call gives it no key". The fails come from R3, not from R4.

Point 1, the binding question. Each key is a set of line numbers in plain words, such as "1 to 7" or "1 to 7, 68". Lines with words and lines with no words never share a key, because `_words_by_range` groups by the words first. So a seat can bind each entry to its lines. In n174-m47-m48, line 68 has its own words, so the keys are "1 to 7", "8 to 67" and "68". The `clauses` block also carries the same words with their lines.

## (c) Probes

- The recorded wakes are in `tests/rota/cassettes.db`. The case id is `L3R-n174-m47-m48`. The `case_runs.prompt_hash` value does not match `cassettes.prompt_hash`, so the probe filtered on model and on the text "Line 68 misreads me". Row 65080 is the first wake that was cut: 19,678 characters, with 12,838 shown, and the cut is inside `his_words` line 50. Row 64475 is a full wake of the same case with no cut (19,494 characters).
- `scratchpad/p13_wake.py` parsed `his_words` from row 64475 (8,304 characters, 68 entries) and ran `_words_by_range` on it. The new block is about 560 characters. The splice in the probe was faulty, so the positions come from the offsets of the old keys. In the new order: `clauses` at 7,084, `menus` at about 8,723, `his_words` at about 10,331, `read_back` at about 10,891, total about 11,750. Row 65080 is 184 characters longer, so its rebuilt wake is about 11,930. That is below 12,838, so nothing is cut.
- The two changed test files ran in replay with `ROTA_L1` unset: 71 passed, 2 failed, 2 skipped. The seam2 file at 283f6701 (worktree `C:/Users/roman/rota_p13b`) gives the same 2 fails.
- `test_runner.py`, `test_runner_toolerror.py` and `test_f12_runner_reader.py` ran: 166 passed, 1 skipped.
- The probe did not run `test_l3_rulings.py`. A cassette miss there can reach for a model, and the brief forbids a live model. The 24 expected L3R fails are not checked.
- A grep searched `rota` and `tests` for readers of `his_words`. It found only the writer and the seam2 test.

## (d) Usage

Input about 60k tokens, output about 9k tokens, total about 69k. These are estimates. The brief's cap of 20k was exceeded because the cassette search needed several queries.
