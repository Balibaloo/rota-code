# Frame 243, the try record: the counts on the night databases

Frame 243, the merged code carries the format the principal declined twice.
The pass landed at 7a2cb843 before its counts. This record holds the counts.
It holds numbers only and argues nothing. Written 2026-10-15 11:15 at
43f722d4. Meta workflow, about rota workflow records.

Every database opened read-only, `file:...?mode=ro`. The scripts are
`f243/try_count.py`, `f243/try_detail.py` and `f243/try_tot.py` in session
dae006d1's scratchpad. The per-night output is `f243/try_out.json` there.

## 0. The nights

- Counted: 66 files, nights 82 to 148 without 134. Night 129 counts from
  `clickI_night129_partial.db`, because no full file exists (observed: `ls
  .rota/clickI_night*.db`, 2026-10-15).
- Skipped: `clickI_night87_partial.db`, `clickI_night91_partial.db`,
  `clickI_night91_walk1.db` and `clickI_night109_cut.db`. Each is a copy of
  part of a night that has a full file. No night 134 file exists.
- Skipped: `clickI.db`, the current database. The brief counts the night
  files only.
- Every counted file holds `decisions`, `rulings`, `tool_calls`, `sessions`,
  `turns`, `criteria` and `receipts`. Nights 83 and 84 hold the tables with 0
  decision rows (observed: `sqlite_master`, 2026-10-15).
- Nights 129 (partial) and 130 hold the same session s152 and the same
  target `d_7924932a52`. Both count as they stand (observed: try_detail,
  2026-10-15).

## 1. The supersede door

How a call is counted: a row of `tool_calls` with `fn = 'decisions.author'`
whose `args_summary` holds `supersedes='<id>'`, not `supersedes=None`. The
table logs every call a session sent, landed or refused (reasoned:
`rota/core/db.py:888` inserts `result.tool_calls` whole). A repeat of the
same call counts each time.

How the call's author is known: the seat column, `sessions.role` on
`tool_calls.session_id`. Not the mode.

How a principal's decision is known: `decisions.author = 'principal'` in the
night's final state. The door reads the author at call time. Since frame 200
pass 5, fix 7, no write changes a row's author (reasoned: the check at
`decisions_author`, `rota/roles/api.py`).

### 1.1 a of n

**a = 379 of n = 745** over the 66 nights (observed: all counted files,
`select session_id, args_summary from tool_calls where fn='decisions.author'`
then `authors[target] == 'principal'`, 2026-10-15). Night 87 alone holds
290 of the 379. Without night 87, a = 89 of n = 447.

Every one of the 379 comes from a `vision_keeper` session, except s215 on
night 145 and s451 on night 144, which are `architect` (observed: the same
query, `sessions.role`, 2026-10-15).

The other 366 calls of n: 129 name a decision that is not the principal's
(N, below), and 237 name an id that is not a decision. Of the 237, 218 name
an `items` row and 19 name no row (observed: the same query, `id in items`,
2026-10-15). The items branch or `_must_exist` refuses those before the
supersede door reads them (reasoned: the order in `decisions_author` at
7618bfb5).

The a calls by night, session, seat and target (observed: the same query,
2026-10-15):

| Night | Calls | Session (seat), target |
|---|---|---|
| 87 | 290 | s122 (vision_keeper) `d_c98d3e32a9` 1; s531 `d_06f7771804` 3; 95 sessions s351 to s745 `d_11db7c3f76` 286 |
| 90 | 5 | s133 1, s154 4 (vision_keeper), `d_eccd93ad44` |
| 92 | 4 | s165 (vision_keeper), `d_96b569916e` |
| 96 | 2 | s187 (vision_keeper), `d_e79ba6217b` |
| 97 | 5 | s187 (vision_keeper), `d_adbac76a58` |
| 106 | 3 | s175 (vision_keeper), `d_db6de101a2` |
| 113 | 2 | s216 (vision_keeper), `d_7f38551388` |
| 115 | 10 | s162 5, s172 5 (vision_keeper), `d_b446ab4182` |
| 117 | 3 | s146 (vision_keeper), `d_fc06c424d6` |
| 121 | 5 | s207 4, s257 1 (vision_keeper), `d_77defaa3ff` |
| 129 (partial) | 7 | s152 5, s163 2 (vision_keeper), `d_7924932a52` |
| 130 | 5 | s152 (vision_keeper), `d_7924932a52` |
| 138 | 6 | s201 3, s236 3 (vision_keeper), `d_e09e9bd7cf` |
| 143 | 10 | s267 4 `d_a27bd5baac`; s467 4, s504 2 `d_33f8c35a52` (vision_keeper) |
| 144 | 5 | s417 4 (vision_keeper), s451 1 (architect), `d_123dce47f7` |
| 145 | 11 | s215 1 (architect), s222 4 (vision_keeper) `d_e5f744505b`; s426 6 (vision_keeper) `d_f50da634e2` |
| 147 | 3 | s327 (vision_keeper), `d_c3b9ba110e` |
| 148 | 3 | s189 (vision_keeper), `d_565d2845d4` |

18 nights hold a call of a. The other 48 counted nights hold 0.

### 1.2 b of N

**b = 0 of N = 129** (observed for N: the same query, `target in decisions
and authors[target] != 'principal'`, 2026-10-15). N by night: 85 6, 87 8,
91 38, 92 5, 95 6, 98 13, 108 3, 113 1, 118 2, 119 1, 120 6, 121 14, 123 3,
125 3, 138 7, 140 4, 143 2, 144 3, 145 4. 123 of the 129 are
`vision_keeper` calls. 6 are `architect` calls, 2 on night 144 and 4 on
night 145 (observed: try_detail, 2026-10-15).

b is 0 by construction, not by a run (reasoned: the predicate at
7618bfb5). The door refuses only when `over["author"] == "principal"`, read
from the `decisions` row the call names. A call whose target is not the
principal's row cannot meet that test. A target in `staged` skips the door.
A call from the role `principal` skips the door.

### 1.3 m of M

**m = 4643 of M = 5036** decision rows over the 66 nights have the author
`principal` (observed: all counted files, `select author from decisions`,
2026-10-15). By night, the last six: 143 51 of 71, 144 72 of 109, 145 16 of
48, 146 27 of 46, 147 21 of 34, 148 9 of 18.

### 1.4 What the supersede did

The one query: `select d.id, d.author, d.supersedes from decisions d join
decisions p on p.id = d.supersedes where p.author = 'principal' and
d.author != 'principal'`. It shows which supersede rows landed. It does not
show an effect on a merge or the ledger, so the effect is "not read".

Landed rows by night (observed: that query, 2026-10-15): 87 7, 90 1, 92 0,
96 0, 97 1, 106 1, 113 1, 115 1, 117 2, 121 1, 129 (partial) 1, 130 1, 138
1, 143 2, 144 1, 145 2, 147 0, 148 1. Night 148's row is
`d_74_challenge_ver_opt_show_py` over `d_565d2845d4`. Night 145 holds one
`architect` row, `dec_1_confirm_default_on_eof` over `d_e5f744505b`.

The effect on the merge: not read. The scope read found no reader of
`decisions.supersedes` in `rota/core` or `rota/roles` (observed:
`plans/frame243-scope.md` section 0, grep at 92c4f126, 2026-10-15).

## 2. The record shape, its reach

The block counts as `contests_on` reads: a `rulings` row whose `per_item`
gives a criterion `contest`, `status != 'stale'`, and non-empty `words`.

### 2.1 Contest rulings

**362 rows of `rulings` hold a `contest` value over the 66 nights, and 29 of
them carry `texts`** (observed: all counted files, `select per_item, texts
from rulings`, 2026-10-15). Nights 82 to 132 hold 1 contest row in all, on
night 121, and none on a criterion.

The column `rulings.texts` exists from night 145. Nights 82 to 144 do not
have it (observed: `PRAGMA table_info(rulings)`, 2026-10-15).

86 of the 362 contest a criterion id. All 86 are non-stale and carry words,
so the block reads all 86 (observed: the same query, `id in criteria`,
2026-10-15).

| Night | Contest rows | With texts | On a criterion |
|---|---|---|---|
| 133 | 55 | no column | 0 |
| 135 | 15 | no column | 0 |
| 136 | 50 | no column | 0 |
| 137 | 17 | no column | 6 |
| 138 | 23 | no column | 10 |
| 139 | 16 | no column | 4 |
| 140 | 16 | no column | 2 |
| 141 | 9 | no column | 1 |
| 142 | 30 | no column | 17 |
| 143 | 32 | no column | 11 |
| 144 | 37 | no column | 6 |
| 145 | 18 | 14 | 14 |
| 146 | 23 | 9 | 9 |
| 147 | 15 | 5 | 5 |
| 148 | 5 | 1 | 1 |

### 2.2 Wakes that would carry the block

**559 Developer and Tester wakes of 2402 that pushed `criteria.load` would
carry the block** (observed: all counted files, the join below, 2026-10-15).
2407 Developer and Tester sessions exist in all.

The join:

1. Take each `developer` or `tester` row of `sessions`.
2. Read its first `turns.user`. Cut the `[criteria.load]` section, up to
   the next `\n\n[`.
3. The pushed criteria are the `criteria.id` values that appear in the
   section as whole tokens.
4. A wake counts when a contest ruling on a pushed criterion was written
   before it. "Before" means the lowest `sessions.seq` among the `receipts`
   rows of that ruling is below the wake's `seq`. Every contest ruling has a
   receipt (observed: 0 contest rulings without one, 2026-10-15).

The join reads `status` in the night's final state. A ruling that went stale
later counts as stale at every wake.

| Night | Wakes with the block | Of wakes with `criteria.load` | Longest block, characters |
|---|---|---|---|
| 137 | 28 | 34 | 1989 |
| 138 | 53 | 70 | 8823 |
| 139 | 29 | 34 | 1176 |
| 140 | 23 | 23 | 280 |
| 141 | 4 | 6 | 351 |
| 142 | 96 | 109 | 4933 |
| 143 | 23 | 55 | 965 |
| 144 | 61 | 95 | 1892 |
| 145 | 128 | 128 | 6053 |
| 146 | 77 | 82 | 1598 |
| 147 | 27 | 61 | 5407 |
| 148 | 10 | 22 | 475 |

Nights 82 to 136 hold 0 such wakes. The block length uses the line shape of
`_contest_block` at 7a2cb843. Before night 145 the block has no "He
contested this text:" line, because no `texts` exist.

Night 148's 10 wakes: s190, s193, s196, s198 and s203 (developer), s191,
s192, s195, s197 and s199 (tester). Each carries `ver_opt_show_py` with
`r_4c8fd5d3ad` (observed: the join, 2026-10-15).

### 2.3 The three lows

- **`revise` rulings on criteria, which the block leaves out: 10** over the
  66 nights. By night: 137 1, 138 2, 143 1, 145 5, 147 1. The rest hold 0
  (observed: `per_item` values `revise` on a `criteria.id`, 2026-10-15).
- **Contests followed by a later approve on the same criterion, which the
  block still shows: 38 criteria.** By night: 137 3, 138 6, 139 1, 140 2,
  142 3, 143 6, 144 2, 145 2, 146 11, 147 1, 148 1 (observed: a `contest`
  on a criterion, then a later `rulings` row by rowid with `approve` on the
  same id, 2026-10-15). Night 148's one is `ver_opt_show_py`,
  `r_4c8fd5d3ad` then `r_3340e1e9d9`. s203 woke after the approve and still
  gets the block.
- **The longest contest block a night-148 wake would carry: 475
  characters**, one ruling, `r_4c8fd5d3ad` on `ver_opt_show_py`, with its
  text and his words (observed: the join, 2026-10-15). The longest on any
  night is 8823 characters, night 138.

## 3. The forward measure

The baseline is 1 of 3 merges on night 147 and 1 of 3 on night 148
(observed: `plans/night148-read.md` sections 0, 10 and 12H, 2026-10-15).
This record does not compute a new baseline.

The read that counted the 1 of 3 on night 148, from section 10 of that
read. Repeat it the same way on night 149:

1. List the merged batches: `select id, item_id, head_commit from batches
   where status = 'merged'` on the night's database.
2. For each merge, take the target repository's diff between consecutive
   merge commits. Night 148 used `2c8cd3a..002fbcb`, `002fbcb..517e61d` and
   `517e61d..a83cc50`.
3. Take the principal's words on that item from the night's principal
   record, `.rota/clickI_night<n>.principal.jsonl`, the rows of that night:
   his asks, his page words and his rulings.
4. Read the diff and the tests against those words. A merge counts when the
   merged code or its test carries a behaviour that his words declined. A
   test placed against his words, or a test that does not test its
   criterion, does not count. Night 148 counted bg_3 and not bg_1 or bg_2.
5. Write the count as k of the merges, with the chain of the counted merge
   from the `criteria`, `decisions`, `rulings` and `sessions` rows.

The read is a judgement over the diff and the words. No single query gives
the count (reasoned: section 10 reads `git diff` and the jsonl by hand).

## 4. What this record could not count

- The effect of each landed supersede on a merge or the ledger: not read.
  No one query joins a decision to a merge.
- Whether a ruling was stale at a wake's time: the databases keep only the
  final `status`.
- Night 134: no file.
