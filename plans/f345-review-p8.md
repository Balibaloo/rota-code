# Frame 345, review p8: seam7root at 12c2f5f5 (parent 747d99ab)

READY. The land holds on safety. No red is new against the parent.

## (a) Verdicts

1. HOLDS. The diff adds reads of the row's table (`_is_touch_line`, `_line_kind`) and of the line's paths (`_shown_paths`, `_shown_entries`). `_path_name_rank` and the `_names_path` read on the word form are gone. The one word code reads is the seat's separator `and` in `_excluded_paths`. No verb or cue of his words is read.
2. HOLDS. `test_a_path_off_the_line_is_refused_with_the_lines_paths` runs `rulings.rule` on M77 twice: `exclude src/click/core.py` is refused once with `Line 5 lists src/click/_compat.py, src/click/termui.py, tests/test_basic.py`, and a bare `exclude` is refused with `exclude names the paths to take off`. No `rulings` write stays staged. A criterion line is refused with its kind (`line 2 is a criterion, and it lists no files`).
3. HOLDS. `_insert_landed_rows` spreads one landed row per path for an exclude only, by `spread`. `one_row_per_ref` keeps the other paths beside the top row only when the top row is an exclude. `ruled(newest=True)` keeps every row of the newest `ruling_id` per ref. `test_two_excludes_on_one_line_both_count_after_the_land` proves the landed table, `ruled`, `ruled(newest=True)` and `disputed_paths` all see two paths. The other readers that group by ref: see finding 1. Each sees the two rows right, because each reads the verdict or the ruling id, which the two rows share.
4. HOLDS. The prompt is 40 lines. The exclude bullet's form `"5": "exclude src/a.py, tests/test_a.py"` is the comma list `_excluded_paths` splits. `exclude utils.py` matches by the one shown path that ends with `/utils.py`.
5. HOLDS. Branch: 2 failed, 90 passed. Parent (D:/repos/rota, code at 747d99ab): the same 2 failed, 82 passed. The reds are `test_s159s_drop_on_lines_2_to_8_lands_as_contest` and `test_a_phrase_maps_by_its_first_word` in `test_frame193_pass1.py`. Both fail at the parent with the same refusal (`line 6: no words of his name line 6`). No new red.

## (b) Findings

1. rota/core/scheduler.py:2051 and rota/core/sandbox.py:4750. Low. CONFIRMED by read: `ruled_rows` returns `[r["ref"] for r in rows if verdict in (contest, revise)]`, so an exclude ref now appears twice in the list. Both consumers use the list as a membership test or filter it to criteria, so the duplicate changes nothing. The other readers by ref (api.py:1425, 1879, 2404; principal.py:796, 1016; scheduler.py:1934; nightreport.py:207) read the verdict or the ruling id, which the two rows share. Fix: none needed. A `dict.fromkeys` on the list removes the duplicate if a later reader counts.
2. rota/roles/principal.py:3594-3613. Low. CONFIRMED by the test's landed order: `read` is the newest reading row, which is the last extra, so the landed own row takes `tests/test_options.py` and the extra takes `tests/test_defaults.py`. The reading's own row held the reverse. The set of paths is the same, so no reader is wrong. Fix: pick `read` as the row whose `id` equals `ruled_ref_id(rid, ref)` when one exists, so the landed own row mirrors the reading's own row.
3. rota/roles/api.py:11672. Low. PLAUSIBLE: `path.lower() == "and"` is the one seat word code reads. The prompt names commas as the separator, so the seat has no reason to write `and`. Fix: keep, or drop the branch and let `and` refuse with the line's paths.

## (c) Probes

- Branch run: `cd C:/Users/roman/rota_seam7 && env -u ROTA_L1 python -m pytest tests/rota/test_seam2_word_per_line.py tests/rota/test_frame193_pass1.py tests/rota/test_ruled_refs.py tests/rota/test_f2_rulings_words.py -q -p no:cacheprovider`: 2 failed, 90 passed.
- Parent run: the same command in D:/repos/rota (code at the parent, docs commits only above 747d99ab): 2 failed, 82 passed, same two names.
- `git diff 747d99ab..HEAD -- rota/` read whole for point 1.
- `wc -l rota/roles/prompts/liaison/landing.md`: 40.
- `rota.tools.map table ruled_refs` and grep of `ruled(`, `one_row_per_ref(`, `ruled_rows(` for point 3, with each caller read in context.
- No probe file was written. Point 2 is covered by the branch's own tests, which ran green.

## (d) Usage

Input about 290k tokens across 9 calls. Output about 7k tokens. Total about 297k.
