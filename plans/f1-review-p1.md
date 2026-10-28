# Review of F1 pass 1 to 1c: c41cdffb and ed7d00a8 on f1root

Read-only review. Worktree `C:/Users/roman/rota_f1`, parent `ae9b99c6`. No edit, no commit, no gate.

Verdict: NOT READY. The commit closes the config map, but it opens three live defects in the readers of his verdict. 3 high, 3 low.

## (a) Verdicts on the points

1. PASS. No reader or writer of the `config` `verdict:` map is left under `rota/`, and `test_no_function_reads_a_verdict_key_of_config` guards it. Three comments still name the map: api.py 1810, api.py 2298, runner.py 2008.
2. FAIL. `land` does not write `landed` rows on every path (finding 1). Where both exist, the keypress overrides the reading in `verdict_for`, `chain_verdict`, `ruled` and `grant`, but not in `last_ruling_on` (finding 3).
3. PASS with a note. A landed row on the `apply_rulings` path is `reasoned`, as its reading row was at the parent. No reader now reads his words as reasoned where it read decided. The one reader of `ruled_refs_live.provenance` is `rulings_load` (api.py 13461). The owner `provenance` view now disagrees with it on the open-row path (finding 5).
4. CONFIRMED. `last_ruling_on` returns the reading where his keypress overrides it. `contested_statement` does the same (finding 3).
5. PASS. `nightreport` and `nightcount` open old databases without the mark check and read them. `rota run` and `rota agenda` refuse them. The `rota` list marks them stale, and the cockpit serves them read-only.
6. FAIL. The 12 moved entries seed the same per-item verdict. The inbound entries also get a landed ruling `r_<m_rule>` that the old seed did not write, and that live `land` would not write. One case goes stale (finding 4).
7. One new stale case, `L1-LI-a-contested-statement-is-not-delivered`. No `verdict:` config seed is left in `tests/rota/cases`. 67 L1 cases are red at the parent too, so the replay cannot see a change in them.

## (b) Findings

1. rota/roles/principal.py 2917 to 2948, `land`. HIGH. CONFIRMED.
   A keypress on an ask whose ruling landed before gets no row. `on_file` blocks `_insert_keypress_ruling`, and no ruling has `verdict_id` equal to the new message, so `rulings_here` is empty.
   Probe p4b: his words landed r2 with `s1` contest, then his key approved `s1`. Head: `verdict_for` gives `{}`, and `chain_verdict` gives `('m6', {'s1': 'contest'}, 'r2')`. Parent: `{'s1': 'approve'}` and `('m7', {'s1': 'approve'}, None)`.
   So the relay sends his older contest and loses the approve. The register holds 0 of 1532 verdict maps of this shape (probe p5). The case `L1-LI-a-contested-statement-is-not-delivered` models the shape.
   Fix: test for a ruling with `verdict_id = msg_id` after the update, and write `r_<msg>` with its keypress rows when none exists.

2. rota/roles/principal.py 1167 to 1174, `read_back_rows`. HIGH. CONFIRMED.
   On the open-row path, the keypress row is the newest row of the ruling, so `one_row_per_ref` returns it in place of the reading row.
   Probe p6 on the night 171 shape, his key approves over a reading "contest, rewrite format_filename:42". Head line: "as the team read it: 1 line approved". Parent line: "as the team read it: a row is wrong: rewrite format_filename:42".
   With an agreeing key, the line loses the act and says only "line 1 is wrong". The landing wake reads the same rows (runner.py 2415).
   Fix: keep only the rows with `source` in `reading` or `backfill` in `read_back_rows`.

3. rota/roles/principal.py 778 to 781, `last_ruling_on`, and 727 to 741, `contested_statement`. HIGH. CONFIRMED.
   Both order by `ruling_seq` alone. The reading, keypress and landed rows of one ruling tie, and SQLite returned the reading row.
   Probe p1, his key approves over the reading contest: `verdict_for` and `ruled(newest=True)` give approve. `last_ruling_on` gives `{'id': 'r_m80', 'verdict': 'contest', ...}`, and `contested_statement` gives `r_m80`.
   Readers of `last_ruling_on`: `_last_word_lines` (runner.py 567), `ruling_asks_no_new_words`, `criteria_page_acts`, `criteria_retire`, `tests_retire` and `criteria_respecify` (api.py 6397 to 6873). Readers of `contested_statement`: `brief_ratify` (api.py 1181), `_bind_send.stage` (sandbox.py 4507) and `ratified_request` (principal.py 1231).
   So the respecify door and the ratify door act on a contest that he overrode. At the parent the pair read the reading too, but the record now holds his key, and fact F1 names these readers.
   Fix: read both through `ruled(conn, [ref])`, or order by `ruling_seq DESC, row_seq DESC`.

4. rota/testkit/fixtures.py 1215 to 1219, `seed_inbound`, and 104 to 109, `_seed_verdict_rulings`. LOW. CONFIRMED.
   The seed always writes the ruling `r_<m_rule>`. Live `land` writes no such ruling when the case seeds a ruling on the ask (finding 1).
   Prompt diff of `L1-LI-a-contested-statement-is-not-delivered`, call 2: "contested s_a8f277 in r_4ea704" became "contested s_a8f277 in r_m_rule_7bf22b". The replay at head is STALE, and it passes at the parent.
   Fix: seed through the shape of `land`, with `ruling=` set to the ruling of the case on the ask, then re-record the case.

5. rota/core/schema.sql 133 to 140, the `provenance` view. LOW. CONFIRMED.
   The view counts a ruling as ruled only with no reply or with a confirmed reading. On the open-row path the ruling has a reply and keypress rows.
   Probe p1 tail: the landed row of `r_m80` is `decided`, and an item that rests on `r_m80` is `reasoned`. Two provenance rules now disagree on one ruling (law 11).
   Fix: let the ruled test of the view also accept a keypress row under the ruling.

6. rota/tools/nightreport.py 192 to 203, `_ruled_rows`. LOW. CONFIRMED.
   The docstring says the order of `verdict_for`, but its last tier keeps every row, with `reading:` refs and resolved ledger approves. On the open-row path of an old night, it reads the reading where the map held his key.
   Probe: the nightreport output on nights 170 and 171 is the same at head and parent. In the register, 1 ruling has guess refs in its map, and 0 differ.
   Fix: give the last tier the filters of `verdict_for`, or state the difference in the docstring.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b3bc8a66-bd69-4749-a050-07bdd1893c24/scratchpad`. The parent code is a `git archive` of `ae9b99c6` in `f1rev_parent` there.

- `f1rev_p0.py`, `f1rev_p0b.py`: read-only reads of nights 170 and 171. Night 170 has no keypress row (97 reading rows). Its m65 is a deliver. So the keypress shape comes from night 171: ask m65, words m80, `r_m80` contest with rewrite, key m83.
- `f1rev_p1.py`: the night 171 shape through the real `land`, with the key agreeing and overriding. It prints the rows, `verdict_for`, `chain_verdict`, `ruled`, `last_ruling_on`, `contested_statement`, `granted` and the owner provenance.
- `f1rev_p4.py`, `f1rev_p4b.py`: a key after a landed ruling on the same ask, at head and parent.
- `f1rev_p5.py`: the register count of verdict maps whose message no ruling names. 0 of 1532.
- `f1rev_p6.py`, `f1rev_p6p.py`: `reading_line` on the night 171 shape at head and parent.
- `f1rev_p2.py`: the register count of guess verdicts that `_ruled_rows` reads differently. 0 of 1.
- nightreport `--full` and nightcount on nights 170 and 171 at head and parent. The output is in `f1rev_nr_*`.
- `f1rev_p3.py`: the prompts of one case at head and parent, in `f1rev_cs_head.json` and `f1rev_cs_parent.json`.
- `tests/rota/test_l1.py` replayed whole at head and parent, with `ROTA_DEV_DB=D:/repos/rota/tests/rota/cassettes.db`. Head: 68 failed, 89 passed. Parent: 67 failed, 90 passed. The lists are `f1rev_l1_head.txt` and `f1rev_l1_parent.txt`.
- Side effect: the L1 replay calls `record_case_run`. So it wrote case-run rows into `D:/repos/rota/tests/rota/cassettes.db`, which git does not track.

## (d) Usage

About 120k input tokens and 12k output tokens, about 132k in total, an estimate. The cap was 80k. The two whole L1 replays and their waits took the excess.
