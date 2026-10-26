# Frame 322, the agency read: a fix at the source or at one door

Date 2026-10-26, read at 46e5c88b on `rota/foundation`. Read only, no
pytest, no model call. Night databases 163 and 166 read from copies in the
reader's scratchpad with `mode=ro`.

## 1. The purpose

The Site line names four mechanisms, and no ruling of Roman made any of
them. `tick_criteria` fires per item, so that criteria of one ticket do not
contradict their siblings (observed: `rota/core/scheduler.py` 430 to 435,
the docstring, present at b519a246 on 2026-08-10). The exact-twin refusal
with "a second sentence" came at 395535da on 2026-08-27, after one item got
eleven criteria with two identical (observed: `rota/roles/api.py` 6023 to
6027). The item push came at 33ddea8a on 2026-09-13, wake audit finding 3:
night 35's Terminologist wrote "without buffering delays" without the
module, so the wake got the item, "the principal said" and the source
(observed: the commit body). The retry line came at d68c38a0 on 2026-09-23
(observed: `git log -S`). All four are build decisions (reasoned: no ruled
line in the commits or the comments). The ruling that governs the gap is
older than the frame: "the principal's words always land on a row"
(ruled: Roman, 2026-10-08 23:25, `rota/DECISIONS.md` 1445).

## 2. What exists

| Record or reader | Where | What it holds or does |
|---|---|---|
| `rulings` rows keyed on the item | night 166, r_1ec1beb146 and r_a5e4b30470 | His verbatim words, `per_item` names `format_filename_example` and `guess:format_filename_example`: "only the docstring changes while the code stays the same" (observed) |
| `_ruling_texts` | `rota/roles/api.py` 20856 | Landed rulings on the item, its tickets, its criteria and `guess:<item>`, keyed by batch (observed) |
| Developer start window | `rota/core/runner.py` 4398 to 4409 | Calls `_ruling_texts` under `START_RULED_KEY`, cap 3, frame 312, 6785f35b, 2026-10-24 (observed) |
| `_retired_carry` | `runner.py` 4247, gate at 4271 | Ruled words that name the item, cap 3, only when an old ticket exists. It returns `{}` on a first generation (observed) |
| `contests_on`, `_contest_block` | `runner.py` 701, 731 | Contests on criteria rows only, for the Developer, the Tester and the repair wake (observed) |
| `last_ruling_on`, `_landed_approval` | `rota/roles/principal.py` 769, `api.py` 2307 | The newest ruling on one ref (observed) |
| Contest door reader | `api.py` 1661 to 1668 | Landed ruling words by `per_item` for the wake refs (observed) |
| `_guess_seed` | `runner.py` 4211 | The guess ruling's words for a batch (observed) |
| `criteria_tickets` | `scheduler.py` 450 | Built by this frame: the empty and covered tickets, shared by the wake and the twin refusal (observed) |
| Documentation word lists | `api.py` 5840, 5846, 7875, 13922, 13929 | Five lists that read documentation words from a text (observed) |

The record that the W-E door re-derives from a headline word was on file
before s185 wrote. The window held s3 only (observed: night 166 `turns`
s185 seq 1, the `[the item]` block). Two readers of that record exist, and
the criteria push calls neither on a first generation (reasoned: the table).

## 3. The reach

The frame places cause 9 with cause 2 behind it (observed: the Site
paragraph, `plans/night163-w7w8-read.md` section 1). Cause 9: a text points
the seat at the item and not at the empty ticket. Cause 2: his landed words
on the item are absent from the seat's window.

| # | Cause | Place | State |
|---|---|---|---|
| 1 | 9 | criteria wake detail, `scheduler.py` 444, 471; the retry line `runner.py` 902 shows it through `DETAIL_SHOWN` at 445 | fixed, bf300ce4 (observed) |
| 2 | 9 | exact-twin refusal, `api.py` 5879 | fixed, bf300ce4 (observed) |
| 3 | 9 | near-twin refusal, `api.py` 6834 to 6837: "a second sentence for the same thing is a second test of one fact", no empty ticket | open (observed) |
| 4 | 9 | six cap, `api.py` 6076 to 6081: "Otherwise the criteria are written; end", no empty ticket. s200 hit it on tk_1 at turn 4 | open (observed: the night 163 read, section 1) |
| 5 | 2 | criteria push, `runner.py` 4466 to 4486: statements by `refs` and by the same `span_entry`, no ruling on a first generation | open (observed: s185) |
| 6 | 2 | slicing push, `runner.py` 4571: the same `_retired_carry` gate | open (observed: the code) |
| 7 | 2 | Tester window, `runner.py` 4387 to 4396: contests on criteria rows only, no ruling on the item | open (reasoned: the code, no night read) |
| 8 | 2 | Developer windows past `tick:batch_start`, `runner.py` 4400 to 4401 | open (reasoned: the code, no night read) |

The count is 8 (observed: 1 to 6; reasoned: 7 and 8).

## 4. The fix against the reach

The built fixes cover 2 of 8: rows 1 and 2 (observed: the diff of
bf300ce4). Pass 1 widened the push to statements of the same entry. That
covers 0 of the 3 absent facts on record. s3 and s4 of night 163 sit on
entries e_m65 and e_m84, and m69 of night 166 is a ruling and not a
statement (observed: `statements`, `rulings`, `f322_report.md`). Passes 2
to 3b built a documentation door at `api.py` 5849. It refuses the symptom
of row 5 on a headline that says "docstring" or "documentation" only
(observed: `_HEADLINE_NAMES_DOCS`). It does not put the words in the window.
The W-E read found the absent ruling, called it cause 2, and routed it to
frame 306 (observed: `plans/frame322-we-read.md`, section 1). Frame 306's
built reader is `_contest_block(on_rows=True)`, which reads contests on
criteria rows and not a ruling on the item (reasoned: `runner.py` 731 to
760). So no frame holds row 5. The door also re-derives a fact that the
`rulings` row holds in his words (reasoned: section 2). "Output stays the
same" on `clear()` has no door, and its rulings have no key on the item
(observed: night 166 r_m59, `per_item` empty; reasoned: s156's window not read).

## 5. The proposal

Not the same fix. Five lines, at the smallest place that covers rows 3 to 6:

1. One reader of his landed words on an item: the key set of `_ruling_texts`, item, `guess:<item>`, its tickets and criteria, newest last, cap `RULED_CAP` (`api.py` 20856, `runner.py` 4242).
2. The criteria push and the slicing push carry it on every generation under `RULED_KEY`, and `_retired_carry` keeps only the old criteria (`runner.py` 4271, 4485, 4571).
3. `_ruling_texts` and the Developer start window call the same reader, so one key set serves three seats (`runner.py` 4398 to 4409).
4. The near-twin and six-cap refusals end with the empty list of `criteria_tickets`, as `_twin_refusal` does (`api.py` 5879, 6077, 6836).
5. Red tests: s185's window holds r_1ec1beb146's words, and s200's six-cap refusal names tk_2. The W-E door stays until a night shows whether it still fires (night 166 `turns`, the night 163 read).

Price: 2 to 3 cycles. Cause 2's cheap fix is 2 cycles, and a refusal text
is 2 (observed: `plans/wall-guide.md` causes 2 and 9; `plans/operating-facts.md`
247). One pass and one review on Opus cost about 76k and 48k on this
frame's own pass 1 (observed: the status of 2026-10-25 01:01). The holding
session pays about 10k a cycle, so about 30k (observed: `operating-facts.md`
247). Rows 7 and 8 stay out until a night read shows a wall there
(reasoned: a larger push is not the fix, `wall-guide.md` cause 2).
Every criteria and slicing case whose fixture holds a ruling on its item
goes STALE once (reasoned: the cost the W-E read named for a brief change).

## 6. The doubt

1. Rows 7 and 8 come from the code. No night read shows a Tester or a Developer act wrong for lack of a ruling on the item.
2. Answer rulings with an empty `per_item`, r_m65 on night 163 and r_m59 on night 166, name no row, so a reader by keys misses s3. Not checked: whether a resolver follows m64 to e_m50 to m50, or why the 2026-10-08 rule lets them land on no row.
3. Not measured: the prompt size with three more rulings at `num_ctx` 16384, and whether qwen3.5:9b reads a ruling in its window (cause 4 or 5).

## Verdict

`at one door of 8`: the fix covers 2 of 8, the criteria wake and the
exact-twin refusal. Left: the near-twin and six-cap refusals, and the
criteria, slicing, Tester and Developer windows, which lack his landed words
on the item. The documentation door guards one symptom of row 5, on
documentation headlines only.
