# F16 review, pass 1: 7da194de and 99964faa on f16root

Verdict: NOT READY. One high defect blocks the land: the reopen that hands the batch back now climbs and holds the merge. The night evidence of the fact does not reach the fix. The worktree is `C:/Users/roman/rota_f16`. The parent is ae9b99c6.

## (a) Verdicts

1. HOLDS. `mark_answered` is the one writer under `rota/` outside `testkit/scenes.py:274`. The inline verb sets that remain are other facts, except `invariants.CARRIES` (finding 6).
2. HOLDS for questions and asks, FAILS for the reopen handback. P1 open with note, P2 answered, P3 unresolved. Real non-citing work on a handback reopen counts as nothing (finding 1).
3. submit, elect and verdict: the briefs support the decision. reopen: the brief supports only the first reopen. The second reopen wakes `batch_start`, which owes no reply (finding 1).
4. YES, sessions now wait. The Developer waits on its open `elect`. A merge holds on an open `ask`, `propose`, `submit`, `reopen` or `elect`. No scene test shows either change (finding 4).
5. PARTLY. The pin goes red on a new tuple, list, set or SQL `IN` list. An `OR` chain and a second `==` test pass. The dispute pair is a different fact, but the skip is by content, not by site (finding 5).
6. ZERO of the 21 W17 triggers are a question or an ask. Two are owed verbs, and both went unresolved on the parent already (finding 2).
7. NONE stale by grep. No case and no cassette holds `UNRECEIVED_NOTE` or the old note text.

## (b) Findings

1. **The handback reopen climbs after real work.** `rota/core/db.py:1002` with `_owes_a_reply` at 1271. Severity high. CONFIRMED.
   - The elect brief tells the Vision Keeper to send `msg.reopen_developer` again. `runner.py:340` gives a reopen caused by an `elect` the `batch_start` mode.
   - `batch_start` writes the batch and sends nothing. `_received` finds no message and no write on the item ref.
   - Probe P6 on a night 170 copy: the reopen went `unresolved`, the ladder woke `liaison` in `tick:unresolved`, and `waiting_on_a_seat` returned `waiting on liaison: mr2`.
   - The real shape is tipsAL s75: m37 is a reopen caused by elect m36, and s75 committed code (receipt `batches b1`) and sent nothing.
   - Fix: in `_owes_a_reply`, exempt a `reopen` whose cause verb is `elect`, the key that `runner.py:340` reads.
2. **The fix does not reach its night evidence, and the s202 claim is wrong.** Commit 7da194de body, and the docstring and line 78 of `test_f16_answered_mark.py`. Severity high. CONFIRMED.
   - s202 is the Architect on m80, an `escalate` from the Developer. It is not a Liaison on a fresh request, and not an `ask`.
   - `escalate` was in `OWED_A_REPLY` at the parent, with the receipt rule "message". m80 in the night 170 register holds `UNRECEIVED_NOTE`, so the parent left it unresolved.
   - The 21 W17 triggers: 0 question or ask, s150 a challenge and s202 an escalate (both with notes on the parent), 2 Liaison converse rows on the paths of frames 267 and 320, 17 relay, answer, report or tick wakes.
   - The test pins the s202 shape with a synthetic `ask` m91 that the night never held. A W17 count on the next night cannot fall because of F16.
   - Fix: correct the commit body and the test, and name the real reach of finding 3 as the measure of the frame.
3. **The real reach is barren question wakes, and no night has measured it.** `rota/core/db.py:1513`. Severity low. PLAUSIBLE.
   - On nights 143 to 165, 43 question wakes sent nothing and wrote nothing: 41 to the Researcher and 2 to the Terminologist. One `submit` (night 143 s282) and one `elect` (night 160 s267) did the same.
   - All 45 read answered on their night. Under the head, each goes unresolved and climbs, and the ladder can end at the Liaison and the principal.
   - Law 6 asks for this climb. The cost to the attention of the principal is not measured.
   - Fix: count the new `tick:unresolved` wakes on the first night after the land, and record the count in the frame.
4. **The wider holds have no test.** `rota/core/lifecycle.py:738` and `rota/core/scheduler.py:1535`. Severity low. CONFIRMED by grep.
   - `test_frame204_pass2.py` pins only `challenge` and `question` in the merge hold, and only `challenge` and `escalate` in the wait of the Developer.
   - An `ask` is the read-only inquiry of the Liaison. It now holds the merge of the batch it asks about. An open `elect` now filters every Developer tick, other batches included.
   - Fix: add one hold test for `ask` and one wait test for `elect`, or keep `ask` out of the merge hold by a stated rule.
5. **The pins are narrow.** `tests/rota/test_f16_answered_mark.py:150` and `:176`. Severity low. CONFIRMED.
   - The writer pin matches only the spaced SQL form of the answered status. The form with no spaces and a bound parameter pass (probe 4).
   - The list pin misses an `OR` chain of `verb =` tests and two `==` tests in Python (probe 3).
   - The skip compares content. A new owed reader that names only `challenge` and `escalate` passes, as the old Developer wait would have.
   - Fix: match the writer with a regex that allows any spaces around the equals sign, and skip the dispute pair by its four sites, not by its words.
6. **Outside: a second, contrary list of `submit`.** `rota/tools/invariants.py:48`. Severity low. CONFIRMED by read.
   - `CARRIES` holds `submit` as a carrier, so invariant I9 skips an answered submit with no reply. `OWED_A_REPLY` now says a submit owes one.
   - Fix: drop `submit` from `CARRIES`, or derive `CARRIES` as the message verbs outside `OWED_A_REPLY`.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b3bc8a66-bd69-4749-a050-07bdd1893c24/scratchpad/f16rev/`. They run `session_commit` at the head on `init_db` registers. The night registers were read through `mode=ro` URIs, and the replays ran on copies.

- `probe1.py`: P1 a fresh request with a barren Liaison wake gave `open` with `the session landed nothing and sent nothing`. P2 a barren wake on an `answer` gave `answered`. P3 a question with a glossary row on another term gave `unresolved` with `UNRECEIVED_NOTE`. P4 s202 replayed on a night 170 copy gave `unresolved` with the refusal in the note. P5 s204 replayed gave `answered`. The tipsAL replay stopped, because its schema is stale.
- `probe2.py`: P6 the handback reopen on a night 170 copy. A reopen, an elect and a second reopen were seeded on batch b_1. A Developer session wrote the batch and sent nothing. The result was `unresolved`, a Liaison ladder wake and the merge hold.
- `probe3.py`: the list pin on ten source snippets. It caught a tuple, an SQL `IN` list, a frozenset and an inline `in` pair. It missed an `OR` chain, two `==` tests, a single verb, a list with a non-verb word, and the dispute pair alone or with `deliver`.
- `probe4.py`: the writer pin. It caught the spaced form and missed the form with no spaces, the bound parameter, and the module-level form.
- Inline Python on `clickI_night170.db`: the 21 W17 sessions by trigger verb, status and note. On `clickI_night171.db`: owed-verb triggers with receipts and replies. The decision of s162 cited `c_3` at the time, by `tool_calls`, so it answered by a receipt. Night 171 holds no question or ask with a non-citing row.
- Inline Python on every register of nights 140 to 179: triggers of question, ask, submit, reopen or elect. 433 triggers, 45 with no reply and no write, 0 with a non-citing write. On every register: the reopen wakes, which found tipsAL s75.
- `pytest tests/rota/test_f16_answered_mark.py tests/rota/test_frame204_pass2.py`: 33 passed.
- Greps: `UPDATE messages`, the literal answered status, and inline verb comparisons under `rota/`. The note texts in `tests/rota/cases` and `tests/rota/cassettes.json`.

## (d) Usage

About 100k input tokens, about 10k output tokens, about 110k in total. This is over the cap of 70k.
