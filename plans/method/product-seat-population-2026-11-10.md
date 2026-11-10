# The seat's recorded pages, by run, 2026-11-10

Written by session 1efd37b1 for frame 364, from the table of one Explore
agent, about 109k. The page is an inventory. It holds no finding about
the pages.

## Result

All 11 runs keep a state database, and the 11 databases hold 134 pages
to the Principal. No database stores the text of a page. Only blind
run 1 keeps each page whole as the seat saw it.

A page is a `messages` row with `to_role='principal'` and a verb that is
not `converse`. A reply that landed is a `rulings` row with
`status='landed'`. The counts come from read-only queries (observed: the
agent's queries, and this session's draw script for the page counts).

`T` is `C:/Users/roman/AppData/Local/Temp/claude/`.

| run | repository | database | pages | landed rulings, on pages | other record of the page text |
|---|---|---|---|---|---|
| dry1, four measures | clickI | `.rota/dry1.db` | 41 | 47 on 40 | the build sessions' transcripts; copies `dry1wN` before each turn |
| dry2 | tipsI | `.rota/dry2.db` | 10 | 10 on 9 | transcript 208997ee; copies `dry2w1` to `dry2w5` |
| dry3 | icalendarI | `.rota/dry3.db` | 10 | 14 on 10 | transcript ce483c7b; copies `dry3w1` to `dry3w7` |
| dry4 | icalendarI | `.rota/dry4.db` | 15 | 20 on 13 | transcript 07f209e6; copies `dry4w1` to `dry4w8` |
| dry5 | icalendarI | `T/d--repos-rota/9f60e445-30b5-431b-b448-1ab48919fbaf/scratchpad/dry5/runs/dry5.db` | 15 | 22 on 14 | `t1.log` to `t9.log` beside it |
| dry6 | icalendarI | `T/d--repos-rota/94cb1260-d91d-4109-aa38-7528925f5f83/scratchpad/dry6/runs/dry6.db` | 4 | 5 on 4 | `t1.log` to `t5.log` |
| dry6b | icalendarI | `T/6d9eb18c9e6274ab/1b9e813c-4464-4439-95c2-d0e1bf698557/scratchpad/dry6b/runs/dry6b_after_turn4/dry6b.db` | 5 | 4 on 4 | `dry6b/t1.log` to `t4.log` |
| dry6c | icalendarI | `T/6d9eb18c9e6274ab/1b9e813c-4464-4439-95c2-d0e1bf698557/scratchpad/dry6b/runs/dry6b.db` | 8 new | 7 new, on 6 | `dry6b/t5.log` to `t9.log` |
| dry7 | icalendarI | `T/6d9eb18c9e6274ab/8b2312ef-0b14-4322-a20c-908058cac23b/scratchpad/dry7/runs/dry7.db` | 11 | 13 on 9 | `dry7/t1.log` to `t7c.log` |
| dry8 | icalendarI | `T/6d9eb18c9e6274ab/13b7eef8-9ba8-4251-a72e-fd3511e65682/scratchpad/dry8/runs/dry8.db` | 13 | 10 on 7 | `dry8/turns/t1.txt` to `t5.txt` |
| blind1 | tipsI | `T/6d9eb18c9e6274ab/5ee5ec0b-9675-4645-967d-eab60d0ca52e/scratchpad/blind1/runs/blind1.db` | 2 | 1 on 1 | `blind1/seat/exchange.jsonl`, each page whole and each reply |

## Where a page and a reply are held

- The page: `messages`, columns `id`, `seq`, `verb`, `status`,
  `body_refs`, `body_text`. Only a clarify keeps its question in
  `body_text`. `render_page()` in `rota/roles/principal.py` builds the
  text from the rows at the time of the call.
- The reply: a `messages` row with `from_role='principal'`,
  `verb='converse'` and `cause_id` of the page, written by `land()`.
- The landed reading: `rulings`, with `ask_id`, `reply_id`, `words`,
  `per_item`, `status`. The detail by row is in `ruled_refs`.

## Limits on a draw

- Dry runs 6b and 6c share one database. The copy
  `dry6b_after_turn4` is the end of dry run 6b.
- The four measures of dry run 1 are in one database.
- A page rendered from a final database shows the rows at the end of the
  run, not the page as shown. The copies before each turn are closer.
- The turn logs of dry runs 5 to 8 show the agenda at the end of a turn,
  cut at 60 lines. Some logs show no page.
- Pages open at the end of a run: dry4 1, dry7 2, dry8 5, blind1 1.
- The `.rota/dry*.db` files were opened on 2026-11-10 and can hold a
  back-fill of `ruled_refs`. Nobody checked the page rows for a change.
- The probe material of blind run 1 (`*_probe`) is not the run.
- Copies with the same names in other scratchpads are not the runs' own
  records.

## The draw for the read of mass 1

Seed 364, `random.Random(364).sample`, by run in the order of the table,
on the pages in `seq` order. Two pages per run, four for dry run 1
because the database holds four measures, and both pages of blind run 1.
The script is `draw_seat.py` in this session's scratchpad.

| run | drawn pages |
|---|---|
| dry1 | m2 confirm, m3 present, m17 present, m_park_421158fa15_bg_1 present |
| dry2 | m17 present, m24 present |
| dry3 | m14 clarify, m16 clarify |
| dry4 | m40 present, m46 clarify |
| dry5 | m16 clarify, m47 clarify |
| dry6 | m4 present, m12 present |
| dry6b | m2 confirm, m12 present |
| dry6c | m26 present, m37 clarify |
| dry7 | m2 confirm, m14 clarify |
| dry8 | m18 clarify, m_park_e65413c486_bg_1 present |
| blind1 | m2 confirm, m4 present |

24 of 134 pages: 4 confirm, 12 present, 8 clarify. One drawn page is
open, m4 of blind run 1. The 13 pages open at the end of a run gave one
page to the draw.
