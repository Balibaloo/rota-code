# The review of the seam design of his ruling as one record per ref, 2026-10-27

Read only. The design is `plans/rulings-seam-design-2026-10-26.md`. The review started at cfaf8f39. The head moved to 2c8e7e13 during the review. The new commits change `predicates.py`, `scheduler.py`, `runner.py` and a developer prompt only. No pytest ran, no model was called, and no night database was opened.

## Verdict

The design stands with changes. The record and the passes are sound. The read-back line and the span checker each have a path that reads silence as consent or drops a measured refusal. Seven changes are owed before pass 1. Findings 1 to 6 and 9 are high.

## (a) The points

1. The record: stands with changes, CONFIRMED. The row is write-once, but `_land_shift` is a third writer that the design does not name. The view has no order column and no source column (findings 6, 7, 8).
2. The writer: 3 of the 9 landing cases need the object, and none of them carries an act. The measure in doubt 1 is not enough as written (finding 10).
3. The checker: C3 and C4 keep their cases. C2's unnamed-contest branch keeps s281 refused. The faulted approve of C1 and C2 and the latest-answer rule of C5 do not survive the span input (findings 4, 5).
4. The readers: the six sampled mappings hold. Section 3 misses three readers of his words (finding 9).
5. The read-back: the code of frame 193 keeps the line, but the meaning of the rule refuses it. The every-line rule reads an unanswered line as an approve. The shift and park pages cannot take the line (findings 1, 2, 3).
6. The order: no conflict. 39ce5842 does not edit `land`, and it is in head as ff8fcf22. Pass 5 can run beside pass 4, and both touch `rulings_rule` (finding 11).
7. The smallest place: a third design covers F1, F2 and F3 at about 11 cycles (finding 12).

### Point 1, the record

The table is consistent with the composition's Records. `composition.md` line 47 says "Every record has one writer", and line 60 says that the identity derives from the content. A `ruled_refs` row has one builder, `ruling_rows`, and its id is a hash of its content. These columns break the rule or are owed:

- `rulings.status` and `rulings.verdict_id` have three writers: `land` at `principal.py` 2435, `_land_shift` at 2517 and `apply_rulings` at 2558. The view derives `status` from that column. This is the fact today, and the design keeps it. The design must say so.
- `_land_shift` inserts a `rulings` row at `principal.py` 2519 to 2523. Section 1.3 names two callers only. Section 3.1 maps `_land_shift` as a reader of rows that no writer stages (finding 6).
- `superseded` needs an order, and the hash id gives none. Today's readers order by `rulings.rowid DESC` (`api.py` 2319, `principal.py` 779, 743) (finding 8).
- `provenance` reads "decided" for a keypress, but no column records the source (finding 7).
- `rulings.status` already holds `stale` for a closed ask. The view uses `stale` for a newer `ref_version`, and the view does not map the old `stale` (finding 8).

### Point 2, the writer

The docstring of `rulings_rule` (`api.py` 12442 to 12445) records a second function in the tool list, `msg.converse_principal`. That function drew a converse 5 of 5 on 2026-09-10. An object value is not a second function, so the docstring is no evidence about the object form.

`tests/rota/cases/l1_landing.yaml` holds 9 cases. Three of them write a contest: "a-named-line-is-contested", "a-dropped-line-is-a-contest" and "a-correction-in-a-sentence". One writes "park" and five write approves only. `l1_answering.yaml` writes no ruling. So today 3 of 10 calls need the object. No case carries an act or a target.

The measure in doubt 1 therefore tests the object form on 3 calls and never tests `act` or `target`. The flat `acts` map is a correct fallback, but the measure cannot choose between the two forms. Change: add one landing case from night 169's m36 and m37, "remove the line at 518", and run both forms 5 times on the 4 cases.

### Point 3, the checker

The five doors of `frame339-reach.md` section 2, rows C1 to C5:

- C1, `_line_reading` and `_line_cues`: the contest side survives, because the span must name and fault its line. The approve side does not survive. `reading_fault` runs only on rows that are not an approve (design 2.2). `_faulted_approve` (`api.py` 12048) refuses an approve of a line that the words fault, and it needs the whole reply. Night 149's s212 and the six nights in its docstring are the cases (finding 4).
- C2, `_unnamed_contest`: s281 stays refused. Its contests on lines 5, 6 and 8 to 11 need a span that names each line. A span with no line number spares only `item_lines` (`api.py` 12188 to 12191), and the notes lines are not item lines. The guard holds only if the branch keeps `item_lines` and `request_lines`. `_agreed_contest` reads "the words name no line" over the whole reply. Give it `words_from` whole and not the span.
- C3, `code_line_faulted` and `pointer_fault`: the span keeps the case when it holds the files clause. PLAUSIBLE.
- C4, `_quotes_line`: the span keeps the case when the quote is inside the span. A contiguous span can hold two sentences. PLAUSIBLE.
- C5, `_earlier_reading`: the case is lost. The latest answer about a line wins (`api.py` 12216 to 12221, frame 337 review 1 finding 1). A span from m76, "Line 5 is wrong", passes even when a later answer says "Line 5 is fine" (finding 5).

### Point 4, the readers

Six mappings were sampled and read at head. Each holds:

- `_confirm_landed` `api.py` 656: an ask lookup on `rulings.status`. Holds.
- `_landed_approval` `api.py` 2307: the newest landed verdict on `id`. Holds, if the view has an order (finding 8).
- `last_ruling_on` `principal.py` 769: holds. Today it also reads open rulings (`status != 'stale'`), and the view reads landed rows. `apply_rulings` lands a row right after the commit, so the window is small.
- `park_ruling` `scheduler.py` 1861: the rows cover the page refs. Holds.
- `_keep_cancels` `api.py` 6760: a pure regex helper of P7. Deleted. Holds.
- `contested_statement` `principal.py` 716: holds, if `ruled()` takes the ask verb and the reply seq through a join on `messages`.

The design misses these readers of his words:

- `_removal_strays` `api.py` 20606 and `_silent_note_refusal` `api.py` 21282. Each calls `_ruling_texts` and `_unruled_gone`, which P1 deletes (finding 9).
- `push_working_set` `runner.py` 4412. It pushes `_ruling_texts` to the Developer under `START_RULED_KEY`. After pass 2 it shows the span per row, not the whole reply.
- `resolve_inbound` `runner.py` 2666 fills `earlier_exchange`. The writer needs it to find `words_from`. The object form in 2.1 has no `words_from`, so the writer must derive it by a search: the reply first, then the earlier answers.
- `_last_word_lines` `runner.py` 567, `criteria_page_acts` 6574, `criteria_retire` 6627 and `tests_retire` 6660 call `last_ruling_on`. They keep working only if `ruled()` returns the dict keys `id`, `verdict`, `words` and `text`.

### Point 5, the read-back

Frame 193's rule is `off_page` (`principal.py` 982), called at 1664. It drops a ref whose items are aside or of another request. A `reading:<reply id>` ref reaches no item through `_items_reached`, so the code keeps the line. The meaning of the rule, "a page is about one request", refuses a line about an answer to another request. The design follows Roman's ruling of 22:5x, "every time". Record the departure from frame 193's design 2.F.7 as an amendment, or show the line only on pages of the same request.

The read-back fails on three paths:

- The every-line rule (`api.py` 12767 to 12773) refuses a map without the line, and its text says "A line the reply does not contest is approve". A reply that ignores line 7 then confirms the reading through the Liaison. That is silence read as consent (finding 1).
- `_page_body` returns early for a park page and a shift page (`principal.py` 1652 to 1655). The shift map refuses "approve" (`api.py` 11096 to 11099). A clarify numbers no line (`api.py` 12501 to 12511) (finding 2).
- `rulings_rule` renders the page again at the time of the ruling (`api.py` 12492). A line that derives from the view can be gone, or can name another reply, when his answer arrives (finding 3).

The night principal is `probes/agent_principal.py`. Its brief says "Approve the page when every line says what you asked for. When one line does not, name that line". Its prompt holds its recent pages and its own answers (`system_prompt`, lines 197 to 201). So it answers the line on a present page or a confirm page and does not stall there. On a shift page or a park page the approve is refused. The page comes back once with a note (`page_key`, frame 267), and then the walk stalls on it.

Night 170 then measures how often the agent agrees with the Liaison's reading of the agent's own words. It also measures how the Liaison maps a page-wide "ok" onto the reading line. It does not measure Roman. The count "rows unconfirmed at the night's end" mostly counts replies with no next page.

### Point 6, the order

39ce5842 changes `rota/core/predicates.py`, `rota/core/scheduler.py` and `tests/rota/test_frame330_stopped_bouncing.py` (observed: `git show --stat`). It does not change `principal.py`, so it does not edit `land`. The head holds it as ff8fcf22. The worktree `C:/Users/roman/rota_r330` does not exist (observed: `git worktree list`). The scheduler hunks are in `given_up`, `stopped_bouncing`, `stop_detail` and `parked`. Pass 2's `park_ruling`, `ruled_clarify_criteria`, `ruled_test_criteria` and `verdict_rows` are other functions. So pass 1 waits for nothing.

Pass 5 touches `_page_body` and `off_page` in `principal.py`, `_table_of_ref` and the keys and the every-line rule in `rulings_rule`, the view and `basis` in `schema.sql`, and `nightreport.py`. Pass 4 touches P1 to P11 in `api.py` and `disputed_paths` in `runner.py`. P11, `_note_words`, is called inside `rulings_rule` at 12610. So both passes edit `rulings_rule` in different hunks. They can run side by side if pass 5 owns the keys block and pass 4 owns the P11 call.

### Point 7, the smallest place

A third design covers the reach at about 11 cycles. Keep C1 to C5 on the whole reply, as `frame339-reach.md` section 5 says: "a record would not replace them; they would check it". Add only step 1, the span check, to pass 1. Move the 8 deleted F2 readers into pass 2, because they read `line` and `ref` only. Pass 3 and its count then go, which saves 3 cycles. That design also avoids findings 4 and 5.

One more fact supports it. Frame 337's earlier-answer fix is already in `_unnamed_contest` (`api.py` 12172 to 12178, "Night 168's m76 said Line 5 is wrong"). So the s193 red test of section 4 can already be green at head. PLAUSIBLE: no test ran.

## (b) Findings

1. `rota/roles/api.py` 12767 to 12773. High. CONFIRMED by reading. The every-line rule makes the Liaison rule the read-back line, and its text says that a line he did not contest is approve. A reply that ignores the line then confirms the reading. Fix: exempt `reading:` refs from the every-line rule, and leave an unnamed reading line unconfirmed.
2. `rota/roles/principal.py` 1652 to 1655, `rota/roles/api.py` 11096 to 11099 and 12501 to 12511. High. CONFIRMED by reading. A park page and a shift page return before the line is added. The shift map refuses "approve", and a clarify numbers no line. Fix: put the line on present and confirm pages only, and say so in section 2.3.
3. `rota/roles/api.py` 12492. High. PLAUSIBLE: `render_page` builds the order again at the time of the ruling. A line that derives from the view can move between the send and the reply. Fix: write `reading:<reply id>` into the ask's `body_refs` at the send, and render from the refs.
4. `rota/roles/api.py` 12048 (`_faulted_approve`) against design 2.2. High. CONFIRMED by reading. `reading_fault` runs only on rows that are not an approve, so an approve of a line that his words fault is no longer refused. Fix: keep the faulted-approve branch on the whole reply, and run it once per ruling.
5. `rota/roles/api.py` 12216 to 12221 (`_earlier_reading`). High. CONFIRMED by reading. The latest answer about a line wins today. A span from an earlier answer passes when a later answer reverses it. Fix: the C5 branch reads every answer after `words_from` for the same line.
6. `rota/roles/principal.py` 2517 to 2523 (`_land_shift`) and `rota/roles/api.py` 11072, 12568. High. CONFIRMED by reading. `_land_shift` writes a `rulings` row that section 1.3 does not route through `ruling_rows`. The stored verdicts include `park` and `resume`, and the design lists `later` instead. Fix: route `_land_shift` through `ruling_rows`, and list the stored words of `RULING_WORDS` and `SHIFT_WORDS`.
7. `rota/roles/principal.py` 2433 to 2445. Low. PLAUSIBLE. A keypress on an ask with an open Liaison row lands that row, so keypress rows keyed on the same `ruling_id` and `ref` collide with the Liaison's rows. No column tells the view that a row came from a keypress. Fix: add a `source` column (reading, keypress, backfill), and key keypress rows on the verdict message.
8. Design 1.2, against `rota/roles/api.py` 2319 and `rota/core/schema.sql` 678 to 679. Low. CONFIRMED by reading. The view has no order for `superseded`, and its `stale` collides with `rulings.status` `stale`. Fix: order by `rulings.rowid`, map the old `stale` to its own status, and rename the new one, for example `outdated`.
9. `rota/roles/api.py` 20606 and 21282, `rota/core/runner.py` 4412. High. CONFIRMED by grep. `_removal_strays` and `_silent_note_refusal` call `_unruled_gone` and `_ruling_texts`, and `push_working_set` calls `_ruling_texts`. Section 3 names none of them. Fix: add the first two to pass 4 with P1, and the third to pass 2.
10. Design section 7, doubt 1, against `rota/roles/api.py` 12442 to 12445 and `tests/rota/cases/l1_landing.yaml`. Low. CONFIRMED by reading. The cited misuse was a second function, not a value shape. The 9 cases hold 3 contests and no act. Fix: measure both forms on the 3 contest cases and one new case from night 169's m37.
11. Design 3.5, pass 1 row. Low. CONFIRMED by `git show --stat 39ce5842`. Pass 5 of frame 330 does not edit `land`, and it is in head. Fix: remove the wait on frame 330 from pass 1.
12. Design "The smaller designs". Low. PLAUSIBLE. A design that keeps C1 to C5 on the whole reply covers F1, F2 and F3 in about 11 cycles. Fix: price that design beside the 14-cycle design, and let the count of findings 4 and 5 decide.
13. Outside. Design 1.3 against `rota/roles/api.py` 12866. Low. CONFIRMED by reading. `_table_of_ref` returns None there and the code skips the ref. It refuses nothing today. Fix: state that the refusal is new code in pass 1.
14. Outside. The head moved from cfaf8f39 to 2c8e7e13 during the review. Low. CONFIRMED by `git log`. The design's line numbers in `scheduler.py` are now about 11 lines low. Fix: read the line numbers again at the head when pass 1 starts.

## (c) Probes

No probe file was written. Every probe was a read-only command in `D:/repos/rota`:

- `python -m rota.tools.map fn` on `rulings_rule`, `last_ruling_on`, `land`, `_page_body`, `off_page`, `park_ruling` and eight more. `map table rulings` for the 9 writers and 24 readers.
- `sed -n` reads of `api.py`, `principal.py`, `runner.py`, `scheduler.py`, `schema.sql` and `probes/agent_principal.py` at the lines cited above.
- `grep` of `tests/rota/cases/*.yaml` for `rulings` writes and contests. `grep -rn` of `rota/` for `earlier_exchange`, `_ruling_texts(`, `FROM rulings` and `JOIN rulings`.
- `git show --stat 39ce5842 ff8fcf22 d8e94e29`, `git merge-base --is-ancestor`, `git worktree list`, and the hunk headers of `git diff cfaf8f39 HEAD`.

## (d) Usage

Input tokens: about 95k, an estimate. Output tokens: about 15k, an estimate. Total: about 110k. The brief's cap was about 60k, and the review went over it.
