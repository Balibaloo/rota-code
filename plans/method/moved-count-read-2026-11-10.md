# The turns where a measured count moved, 2026-11-10

One reader and one pass. An agent on Opus wrote this page for frame 364, from `plans/method/moved-count-brief-2026-11-10.md`. It opened each database with `immutable=1`, and dry run 6 as a copy with its `-wal`. It ran read-only git commands and changed no other file. `S` is the scratch folder `C:\Users\roman\AppData\Local\Temp\claude\6d9eb18c9e6274ab\1efd37b1-058e-4b19-8ab1-e1a6c654a389\scratchpad\moved\`. The scripts are `series.py`, `moves.py`, `commits.py`, `link.py`, `grade.py`, `summary2.py` and `reverse.py`. Every candidate is one row of `S\cands.tsv`.

## Result

1. **46 moves hold**, at 36 nights, in 8 series. 14 of them reverse within six nights. 123 one-night moves do not hold (observed: `moves.txt`).
2. **20 moves get the grade "conditions changed"**: the requests, the seat, the start, the walks or the run harness changed at the move's night (observed: part 3).
3. **The other 26 moves** have 510 candidate commits in their three turns before, at 23 nights. By grade: mechanism seen 47 (wall 35, plan 5, neither 7), change seen in the rows 156 (114, 23, 19), timing only 307 (167, 53, 87). By move, the best grade is mechanism seen for 14 moves and change seen for 12 (observed: `summary2.txt`).
4. **The strongest observations.**
   - 21 of the 26 graded moves hold a change of conditions inside their own eight nights, the five nights of the base and the three of the move. Only five moves have a window with no change: merged at 121, 126 and 144, waits behind at 122, and sessions per merge at 159 (observed: `win2.py`).
   - 73 of 85 turns from night 87 to night 172 have a move in the next three runs. So a change before a move is near certain by timing alone. The reverse view finds a move after 18 of its 20 largest changes, and the two others sit where the rule cannot place a move (observed: `reverse.txt`; reasoned).
   - The clearest mechanism is night 96. Frame 90's new brief line sits in the review session of the one merged batch, in 1 of its 9 sessions and in 0 of the 302 other sessions. Night 95 quarantined that review key, and night 96 did not (observed: part 4). Its window also holds three harness changes (observed).
5. **What I could not find**: a measure of the noise between equal runs, a database of night 134, a night log for nights 82 to 84, the page texts of nights 82 to 132, and an origin for 135 of 1,207 commits (observed: part 7).

## 1. The series

Night 129 is `night129_partial`, its only file. Night 134 has no database. A session counts at the night that started it: the key is the database's `config.created_at`, the session id and its `prompt_hash`. "Kept" sessions come from an earlier night of the same database. "Replayed" sessions are onboarding sessions from the night cassette, with about zero model time. The commit share is the share of new live Developer sessions with a `batches` receipt or `"committed": true` (the rule of `product-model-read`). "Waits behind" is the class `pend_behind` of `product-stops-read`: a batch still `pending` at the end and not parked by the seat. Model hours are `sum(turns.ms)` of the new sessions. Night hours run from the start to the night log's last write, from `runs.tsv` (observed).

| night | batches | merged | sessions | per merge | waits behind | Developer commit share | before first batch start | model h | night h |
|---|---|---|---|---|---|---|---|---|---|
| 82 | 1 | 0 | 164 | - | 0 | 24% of 17 | 117 | 1.33 | - |
| 83 | 0 | 0 | 243 | - | 0 | - | - | 1.9 | - |
| 84 | 0 | 0 | 274 | - | 0 | - | - | 1.99 | - |
| 85 | 0 | 0 | 125 | - | 0 | - | - | 0.64 | - |
| 86 | 2 | 0 | 203 | - | 1 | 6% of 16 | 144 | 1.32 | - |
| 87 | 1 | 0 | 746 | - | 0 | 24% of 21 | 131 | 8.48 | 9.2 |
| 88 | 3 | 0 | 191 | - | 2 | 0% of 3 | 136 | 1.04 | 1.2 |
| 89 | 3 | 0 | 191 | - | 2 | 0% of 3 | 138 | 0.92 | 1.0 |
| 90 | 3 | 0 | 243 | - | 2 | 43% of 21 | 140 | 1.25 | 1.5 |
| 91 | 1 | 0 | 278 | - | 0 | 19% of 43 | 141 | 3.6 | 4.0 |
| 92 | 3 | 1 | 301 | 301 | 1 | 20% of 45 | 142 | 3.05 | 3.3 |
| 93 | 4 | 0 | 236 | - | 3 | 42% of 12 | 130 | 3.05 | 3.4 |
| 94 | 3 | 0 | 278 | - | 1 | 31% of 36 | 131 | 3.77 | 4.3 |
| 95 | 2 | 0 | 219 | - | 1 | 29% of 7 | 131 | 1.13 | 1.4 |
| 96 | 4 | 1 | 311 | 311 | 0 | 38% of 26 | 131 | 2.31 | 2.8 |
| 97 | 4 | 1 | 256 | 256 | 1 | 30% of 20 | 131 | 1.97 | 2.3 |
| 98 | 2 | 1 | 244 | 244 | 0 | 25% of 16 | 131 | 1.56 | 1.9 |
| 99 | 3 | 0 | 198 | - | 2 | 0% of 3 | 131 | 1.13 | 1.3 |
| 100 | 3 | 1 | 249 | 249 | 1 | 38% of 16 | 131 | 1.88 | 2.2 |
| 101 | 1 | 0 | 169 | - | 0 | 50% of 24 | 131 | 1.83 | 2.2 |
| 102 | 3 | 2 | 286 | 143 | 0 | 42% of 45 | 131 | 2.7 | 3.4 |
| 103 | 1 | 1 | 2 (+169 kept) | 2 | 0 | - | 131 (0 new) | 0.01 | 0.0 |
| 104 | 1 | 1 | 1 (+170 kept) | 1 | 0 | - | 131 (0 new) | 0.01 | 0.1 |
| 105 | 3 | 0 | 202 | - | 2 | 25% of 4 | 130 | 0.97 | 1.2 |
| 106 | 3 | 0 | 259 | - | 1 | 39% of 33 | 130 | 2.5 | 3.0 |
| 107 | 3 | 0 | 213 | - | 2 | 25% of 16 | 126 | 1.62 | 1.9 |
| 108 | 3 | 0 | 365 | - | 0 | 17% of 59 | 130 | 3.08 | 3.8 |
| 109 | 3 | 0 | 251 | - | 1 | 51% of 35 | 130 | 2.7 | 3.2 |
| 110 | 3 | 0 | 0 (+251 kept) | - | 1 | - | 130 (0 new) | 0.0 | 0.0 |
| 111 | 3 | 0 | 6 (+251 kept) | - | 1 | 25% of 4 | 130 (0 new) | 0.19 | 0.2 |
| 112 | 3 | 0 | 97 (+251 kept) | - | 0 | 17% of 29 | 130 (0 new) | 1.58 | 1.8 |
| 113 | 3 | 0 | 228 | - | 2 | 40% of 10 | 130 | 0.91 | 1.1 |
| 114 | 3 | 1 | 133 (+140 kept) | 133 | 0 | 56% of 27 | 130 (0 new) | 1.42 | 2.0 |
| 115 | 3 | 0 | 203 | - | 2 | 60% of 10 | 128 | 1.32 | 1.5 |
| 116 | 3 | 1 | 244 | 244 | 1 | 27% of 11 | 130 | 1.01 | 1.2 |
| 117 | 3 | 0 | 252 | - | 1 | 30% of 23 | 130 | 1.52 | 1.8 |
| 118 | 3 | 1 | 246 | 246 | 1 | 22% of 23 | 125 | 1.2 | 1.5 |
| 119 | 3 | 1 | 291 | 291 | 0 | 39% of 31 | 129 | 1.77 | 6.3 |
| 120 | 3 | 2 | 249 | 124 | 0 | 43% of 14 | 129 | 1.48 | 1.8 |
| 121 | 3 | 0 | 382 | - | 0 | 39% of 54 | 129 | 2.77 | 3.5 |
| 122 | 3 | 0 | 206 | - | 2 | 12% of 8 | 129 | 0.68 | 0.8 |
| 123 | 4 | 0 | 253 | - | 3 | 35% of 17 | 129 | 1.25 | 1.4 |
| 124 | 4 | 0 | 221 | - | 3 | 38% of 8 | 129 | 0.92 | 1.1 |
| 125 | 3 | 0 | 220 | - | 2 | 15% of 13 | 129 | 0.83 | 1.0 |
| 126 | 3 | 1 | 249 | 249 | 1 | 59% of 17 | 129 | 1.32 | 1.6 |
| 127 | 3 | 1 | 280 | 280 | 0 | 32% of 34 | 129 | 1.63 | 2.2 |
| 128 | 3 | 2 | 274 | 137 | 0 | 45% of 20 | 129 | 1.5 | 1.9 |
| 129 | 2 | 1 | 189 | 189 | 0 | 45% of 11 | 129 | 0.89 | 1.2 |
| 130 | 3 | 1 | 84 (+176 kept) | 84 | 0 | 54% of 26 | 129 (0 new) | 1.22 | 2.1 |
| 131 | 4 | 2 | 212 (+131 kept) | 106 | 0 | 26% of 34 | 129 (0 new) | 1.99 | 2.7 |
| 132 | 4 | 2 | 331 | 166 | 0 | 33% of 24 | 129 | 2.02 | 2.6 |
| 133 | 8 | 1 | 590 | 590 | 1 | 17% of 12 | 154 | 2.79 | 3.5 |
| 135 | 0 | 0 | 268 | - | 0 | - | - | 1.15 | 1.4 |
| 136 | 4 | 2 | 569 | 284 | 1 | 50% of 6 | 143 | 2.96 | 3.7 |
| 137 | 15 | 1 | 352 | 352 | 0 | 32% of 19 | 182 | 2.92 | 3.7 |
| 138 | 3 | 1 | 396 | 396 | 0 | 24% of 58 | 137 | 3.82 | 4.6 |
| 139 | 3 | 2 | 283 | 142 | 0 | 30% of 20 | 156 | 2.24 | 2.7 |
| 140 | 2 | 1 | 326 | 326 | 0 | 33% of 9 | 264 | 2.1 | 2.6 |
| 141 | 2 | 1 | 198 | 198 | 0 | 100% of 4 | 151 | 3.5 | 3.8 |
| 142 | 4 | 0 | 573 | - | 0 | 12% of 56 | 141 | 4.53 | 5.7 |
| 143 | 6 | 1 | 528 | 528 | 0 | 15% of 33 | 306 | 3.17 | 4.0 |
| 144 | 5 | 0 | 618 | - | 0 | 24% of 55 | 238 | 4.96 | 6.1 |
| 145 | 4 | 0 | 439 | - | 0 | 21% of 75 | 122 | 4.9 | 6.0 |
| 146 | 8 | 0 | 494 | - | 0 | 33% of 54 | 160 | 3.63 | 4.8 |
| 147 | 4 | 3 | 352, 85 replayed | 117 | 0 | 41% of 32 | 130 | 1.69 | 2.3 |
| 148 | 3 | 3 | 209, 84 replayed | 70 | 0 | 25% of 12 | 119 | 0.57 | 0.8 |
| 149 | 2 | 1 | 255, 93 replayed | 255 | 0 | 24% of 17 | 125 | 0.79 | 1.2 |
| 150 | 2 | 0 | 527, 98 replayed | - | 0 | 0% of 6 | 147 | 0.81 | 1.1 |
| 151 | 4 | 2 | 336, 99 replayed | 168 | 0 | 26% of 38 | 126 | 1.54 | 2.1 |
| 152 | 3 | 3 | 297, 99 replayed | 99 | 0 | 32% of 19 | 121 | 1.06 | 1.4 |
| 153 | 3 | 2 | 288, 98 replayed | 144 | 0 | 23% of 26 | 121 | 1.46 | 1.8 |
| 154 | 4 | 2 | 407, 99 replayed | 204 | 0 | 28% of 57 | 126 | 2.09 | 2.8 |
| 155 | 5 | 0 | 381, 99 replayed | - | 0 | 20% of 10 | 124 | 0.94 | 1.3 |
| 156 | 3 | 1 | 352, 99 replayed | 352 | 0 | 9% of 32 | 160 | 1.19 | 1.6 |
| 157 | 2 | 0 | 363, 90 replayed | - | 0 | 16% of 43 | 139 | 1.66 | 2.2 |
| 158 | 3 | 2 | 291, 99 replayed | 146 | 0 | 28% of 29 | 119 | 1.2 | 1.7 |
| 159 | 4 | 1 | 413, 99 replayed | 413 | 0 | 25% of 32 | 122 | 1.46 | 2.1 |
| 160 | 3 | 0 | 314, 94 replayed | - | 0 | 20% of 30 | 115 | 1.09 | 1.6 |
| 161 | 5 | 2 | 410, 99 replayed | 205 | 0 | 19% of 53 | 118 | 1.74 | 2.4 |
| 162 | 3 | 2 | 422, 99 replayed | 211 | 0 | 11% of 56 | 123 | 1.92 | 2.7 |
| 163 | 2 | 0 | 265, 97 replayed | - | 0 | 10% of 29 | 120 | 1.09 | 1.5 |
| 164a | 0 | 0 | 161, 99 replayed | - | 0 | - | - | 0.02 | 0.1 |
| 164 | 2 | 0 | 261, 99 replayed | - | 0 | 19% of 26 | 127 | 1.14 | 1.7 |
| 165 | 3 | 0 | 427, 99 replayed | - | 0 | 18% of 56 | 125 | 2.64 | 3.8 |
| 166 | 3 | 2 | 213, 99 replayed | 106 | 0 | 27% of 11 | 130 | 0.97 | 1.4 |
| 167 | 6 | 0 | 344, 7 replayed | - | 0 | 10% of 31 | 124 | 2.07 | 2.4 |
| 168 | 3 | 0 | 226, 87 replayed | - | 1 | 6% of 18 | 121 | 0.66 | 0.9 |
| 169 | 1 | 0 | 153, 99 replayed | - | 0 | 0% of 14 | 121 | 0.38 | 0.5 |
| 170 | 3 | 2 | 230, 82 replayed | 115 | 0 | 33% of 9 | 127 | 0.49 | 0.8 |
| 171 | 2 | 1 | 231, 105 replayed | 231 | 0 | 33% of 12 | 125 | 0.61 | 0.9 |
| 172 | 3 | 2 | 275, 44 replayed | 138 | 0 | 29% of 17 | 122 | 0.87 | 1.3 |
| 173 | 3 | 3 | 244, 99 replayed | 81 | 0 | 38% of 8 | 122 | 0.88 | 1.4 |
| 174 | 3 | 3 | 232, 91 replayed | 77 | 0 | 58% of 12 | 121 | 1.06 | 1.7 |
| 175 | 3 | 2 | 340, 89 replayed | 170 | 0 | 44% of 16 | 119 | 1.43 | 2.2 |

The dry runs and blind run 1 form the second series, with the request, the repository and the rota commit. The build session sat in the seat of dry runs 1 to 9, and a headless Claude agent with the request only sat in blind run 1. Group D ran every desk. No dry run has a night log (observed: the turns list, column 1; `product-model-read`, section 1; `plans/dry-blind1/recipe.md`:5; `plans/dry9-read-2026-11-10.md`:3).

| run | request, repository, commit | batches | merged | sessions | per merge | commit share | before start | model h |
|---|---|---|---|---|---|---|---|---|
| dry1 | `click.pause()` returns True, clickI, `321ccef4` by date | 1 | 1 | 311 | 311 | 6% of 18 | 144 | 1.52 |
| dry2 | tip percentage ValueError, tipsI, `a84a1cf4` | 2 | 1 | 97 | 97 | 12% of 8 | 54 | 0.37 |
| dry3 | `canonsort_keys()` duplicate key, icalendarI, `44088319` | 1 | 1 | 206 | 206 | 50% of 4 | 179 | 2.2 |
| dry4 | the fold sentence, icalendarI, `97939168` | 1 | 0 | 234 | - | 27% of 22 | 177 | 1.5 |
| dry5 | the fold sentence, icalendarI, `79b1cdb0` | 1 | 0 | 265 | - | 18% of 11 | 206 | 1.84 |
| dry6 | the fold sentence, icalendarI, `cd03aa46` | 0 | 0 | 89 | - | - | - | 0.88 |
| dry6b | the fold sentence, icalendarI, `3b209833` | 0 | 0 | 137 | - | - | - | 0.55 |
| dry6c | the fold sentence, icalendarI, `3b209833` | 1 | 0 | 58 (+137 kept) | - | 14% of 7 | 151 (14 new) | 0.22 |
| dry7 | the fold sentence, icalendarI, `dbd8d920` | 1 | 0 | 223 | - | 26% of 35 | 153 | 1.6 |
| dry8 | the fold sentence, icalendarI, `33c1e697` | 1 | 0 | 199 | - | 29% of 14 | 156 | 1.17 |
| blind1 | a negative bill refused, tipsI, `787d7112` | 0 | 0 | 39 | - | - | - | 0.12 |
| dry9 | the fold sentence, icalendarI, `d856c51d` | 1 | 0 | 236 | - | 35% of 17 | 158 | 1.83 |

## 2. The moves

The rule, written into `moves.py` before its first run:

- Order the nights by number, 164a before 164. Leave out the files with fewer than 50 new sessions: nights 103, 104, 110 and 111.
- A value counts only where it has a meaning: the commit share needs 5 or more Developer sessions, sessions per merge needs a merge, and "before start" needs a batch start.
- At position i, B is the median of the 5 values before i, and A is the median of the values at i, i+1 and i+2. A move starts at i when the distance from A to B is d or more and each of the three values lies on A's side of the midpoint of A and B. Consecutive positions that qualify are one move.
- A one-night move: one value lies d or more from B, and the next value does not.
- d is 1 for batches, merged and waits behind, 25% of B for sessions, 30% of B for sessions per merge, 15 points for the commit share, 20 sessions for "before start", and 0.75 for model hours.

The rule needs five earlier values, so nights 82 to 87 cannot hold a move (reasoned). No series only drifts. Merged rises by thirds, with medians 0, 1 and 1.5. Sessions per merge falls, 246, 198 and 146. Batches stays at 3 in each third (observed: `moves.json`). The dry runs hold no move: the fold sentence runs 8 times, 6 of them with a batch, and merges 0 times, and the other four runs each hold one request (observed). 14 moves reverse within six nights: batches 131 and 163, merged 118 and 121, waits behind 88, 115, 119 and 122, sessions 136, 139 and 142, per merge 128, model hours 88 and 91 (observed). One-night moves that do not hold (observed): batches 22, at nights 90, 91, 93, 95, 97, 101, 124, 129, 133, 135, 137, 141, 146, 150, 151, 155, 157, 159, 161, 164, 169, 171. Merged 21, at 92, 98, 99, 101, 102, 114, 116, 120, 132, 135, 136, 139, 142, 149, 150, 152, 157, 158, 160, 162, 166. Waits behind 16, at 90, 92, 93, 96, 98, 99, 102, 107, 108, 112, 113, 114, 121, 133, 136, 168. Sessions 15, at 87, 101, 106, 108, 112, 114, 121, 127, 130, 141, 149, 150, 165, 167, 169. Per merge 11, at 114, 120, 131, 138, 139, 141, 143, 148, 152, 156, 170. Commit share 15, at 93, 101, 108, 112, 115, 118, 122, 125, 126, 133, 136, 147, 150, 156, 169. Before start 5, at 137, 140, 144, 150, 156. Model hours 18, at 87, 99, 102, 105, 121, 122, 133, 135, 138, 140, 142, 145, 150, 154, 164a, 165, 167, 169.

The 26 other moves, with parts 3 and 4. "Candidates" counts the distinct commits to `rota/` and `probes/` in the three turns before the night. Each kind reads wall/plan/neither, the three origins. A commit counts in each kind that it touches. The grades read M (mechanism seen), S (change seen in the rows, link to the count not shown) and T (timing only), each as wall/plan/neither, with the best grade of a commit over the series of that night.

| night | moves | conditions changed at the night | candidates | kinds, wall/plan/neither | grades, wall/plan/neither |
|---|---|---|---|---|---|
| 88 | batches 0 to 3, waits behind 0 to 2, model hours 1.9 to 1 | none | 28 | door 2/0/7 prompt 2/0/1 cap 1/1/3 code 2/2/17 probes 0/0/10 | M 0/0/6 S 2/0/3 T 0/2/15 |
| 90 | sessions 191 to 278 | none | 32 | door 0/0/3 cap 0/2/1 code 1/13/14 probes 0/0/4 | M 0/2/1 S 0/0/1 T 1/11/16 |
| 94 | waits behind 2 to 1 | none | 20 | door 0/9/0 prompt 0/5/0 cap 2/0/0 code 2/9/1 probes 0/1/3 | M 0/0/0 S 0/6/0 T 2/8/4 |
| 96 | merged 0 to 1 | none | 16 | door 5/4/0 prompt 5/0/0 cap 4/0/0 code 11/0/0 probes 1/0/0 | M 2/0/0 S 0/1/0 T 10/3/0 |
| 98 | batches 4 to 3 | none | 19 | door 11/0/3 prompt 2/0/0 code 3/5/0 | M 0/0/0 S 7/0/0 T 4/5/3 |
| 105 | merged 1 to 0 | none | 21 | door 1/0/6 prompt 1/0/5 cap 0/0/3 code 1/0/6 probes 0/0/5 | M 0/0/0 S 1/0/5 T 1/0/14 |
| 116 | commit share 51.4 to 27.3 | none | 6 | cap 0/0/1 code 3/0/3 | M 0/0/0 S 2/0/0 T 1/0/3 |
| 118 | merged 0 to 1 | none | 9 | door 3/0/0 code 1/3/2 | M 0/0/0 S 3/1/1 T 1/2/1 |
| 119 | waits behind 1 to 0 | none | 12 | door 5/0/0 code 3/3/1 | M 2/0/0 S 2/1/1 T 4/2/0 |
| 121 | merged 1 to 0 | none | 13 | door 2/0/0 cap 1/0/0 code 11/0/0 | M 0/0/0 S 7/0/0 T 6/0/0 |
| 122 | waits behind 0 to 3 | none | 12 | door 4/0/0 cap 1/0/0 code 9/0/0 | M 2/0/0 S 3/0/0 T 7/0/0 |
| 126 | merged 0 to 1 | none | 24 | door 9/4/1 cap 3/0/0 code 5/0/6 probes 1/2/0 rule 0/0/1 | M 1/0/0 S 6/1/1 T 5/3/7 |
| 127 | waits behind 2 to 0 | none | 29 | door 10/5/2 cap 3/0/0 code 8/1/8 probes 1/3/0 | M 0/1/0 S 8/1/1 T 8/3/7 |
| 128 | per merge 249 to 137 | none | 24 | door 6/3/3 code 8/1/8 probes 0/2/0 | M 1/0/0 S 5/1/2 T 6/2/7 |
| 131 | batches 3 to 4, commit share 45.5 to 26.5 | none | 13 | door 1/3/6 prompt 0/1/0 code 1/2/3 | M 0/0/0 S 0/3/2 T 2/0/6 |
| 139 | sessions 396 to 283 | none | 17 | door 12/0/0 prompt 10/0/0 code 15/0/0 probes 1/0/0 | M 8/0/0 S 3/0/0 T 6/0/0 |
| 142 | sessions 326 to 573 | none | 27 | door 12/2/1 prompt 2/3/0 cap 1/0/0 code 13/5/0 | M 1/0/0 S 7/2/1 T 12/4/0 |
| 144 | merged 1 to 0 | none | 20 | door 10/4/0 prompt 7/3/0 cap 2/0/0 code 4/0/0 | M 0/0/0 S 9/3/0 T 6/2/0 |
| 145 | before start 238 to 130 | none | 27 | door 13/6/0 prompt 10/4/0 cap 2/0/0 code 7/2/0 | M 4/2/0 S 9/3/0 T 7/2/0 |
| 151 | merged 1 to 2 | none | 26 | door 19/0/0 prompt 1/0/0 code 10/0/0 | M 3/0/0 S 9/0/0 T 14/0/0 |
| 154 | sessions 297 to 381 | none | 24 | door 11/0/0 code 15/2/0 probes 1/0/0 | M 0/0/0 S 11/0/0 T 11/2/0 |
| 156 | batches 4 to 3 | none | 43 | door 27/0/1 prompt 5/0/0 cap 1/0/0 code 17/2/3 rule 1/0/0 | M 0/0/0 S 9/0/1 T 29/2/2 |
| 159 | per merge 146 to 211 | none | 48 | door 40/0/2 prompt 8/0/1 code 22/0/0 | M 11/0/0 S 11/0/0 T 24/0/2 |

The 20 moves at a change of conditions, at 13 nights, take no commit grade (observed: `summary2.txt`, which also counts their kinds). Night 91: model hours 1.2 to 3, at walks 3 to 1 and run harness 2b60571, 26 candidates. Night 95: model hours 3 to 2, at run harness d0e8df5, 17 candidates. Night 112: model hours 2.5 to 1.4, at start fresh to continues night 109 and walks 3 to 0, 2 candidates. Night 115: waits behind 0 to 1, at start continues night 113 to fresh, 9 candidates. Night 133: per merge 137 to 352, before start 129 to 154, at seat script to agent and run harness e3cf660 51f1bf6 f9d8d2c, 10 candidates. Night 136: sessions 268 to 396, model hours 2 to 3, at walks 2 to 3, 14 candidates. Night 138: batches 4 to 3, at run harness 61a0f41, 16 candidates. Night 147: sessions 528 to 255, before start 160 to 125, model hours 4.5 to 0.8, at start fresh to replayed onboarding and run harness 85930c6 5d5d755 3a1da93 c6d507d, 41 candidates. Night 148: batches 5 to 2, at run harness be5b067, 46 candidates. Night 163: batches 3 to 2, merged 2 to 0, sessions 410 to 261, at requests R1 to R2 and run harness f301eb5, 83 candidates. Night 165: batches 2 to 3, at requests R2 with item 2 first to R2 rotated and walks 2 to 3, 23 candidates. Night 170: commit share 9.7 to 33.3, at walks 1 to 3, 61 candidates. Night 172: merged 0 to 3, per merge 205 to 81, at run harness 5b59b63, 116 candidates.

## 3. The conditions

The script compares each move's night with the night before it in the series (observed: `grade.py`, `cond`). The requests are R0 (night 82), none (83 to 85), R1 (86 to 162) and R2 (163 to 175), with the order of the night log's launch line. The seat is the script before night 133 and the agent from 133. The models are group A to night 84, C on nights 167 and 168, and B elsewhere, with the pins of nights 82 and 86. The start is "continues" when more than 50 sessions come from an earlier night, "replayed" when more than 20 onboarding sessions come from the cassette, "warm" when the launch line says so, and else "fresh". The length is the count of `== walk` lines in the night log. The harness is a commit in the turn before that touches a run file of `probes/`: `walk.py`, `gauntlet_click.sh`, `agent_principal.py`, `seam_start.py`, `night_cassette.py`, `seed_night_cassettes.py`, `warm_stamp.py` or a `principal_brief` page.

- 20 of 46 moves sit at a change: harness 14, walks 6, start 5, requests 4, seat 2. A move can hold more than one. The models changed at no move's night, and nights 167 to 169 hold no move that holds (observed: `win2.py`).
- The eight-night windows of the 26 other moves hold changes too: harness 15, walks 13, start 9, models 4, requests 4, seat 2. Only merged 121, 126 and 144, waits behind 122 and per merge 159 have none (observed: `win2.py`).
- Night 88's base holds nights 83 to 85 with no batch, and nights 83 and 84 ran group A. So its three moves compare against another set of conditions (observed; reasoned).

## 4. The candidates, by kind and by origin

The origin of a commit comes from the frame it names. The script reads "frame N" in the subject or the body first. Else it takes a frame block of the stack that names the short hash, and else the merge commit that joined it. A frame in column 6 of `turns-list-2026-11-10.md`, at or before the commit's turn, gives "wall". A frame in a table row of the two meta pages, or in a Sprint, long term plan, redirect or batches section of the stack, gives "plan". The subject words "Roman" and "sprint" also give "plan". All else is "neither" (observed: `commits.py`, `link.py`).

- Over all 1,207 commits of the window: wall 680, plan 282, neither 245. 135 of the 245 name no frame anywhere (observed). Column 7 counts 1,213 commits on `rota/` and 60 on `probes/`, by path and with merges, and this page does not count again. The 510 graded candidates by kind, wall/plan/neither: door 203/40/35, prompt 53/16/7, cap 21/3/8, other code 172/50/72, probes 5/8/22, rule or record with no code 1/0/1 (observed).
- The other code, by part, wall/plan/neither: runner 85/15/31, harness of tests 35/12/13, principal seat 31/4/0, llm 24/6/15, build tool 13/22/16, scheduler 19/7/1, db and schema 18/8/3, predicates 17/5/0, lifecycle 9/1/0, loop 4/4/4 (observed).

The grade is by script. The diff gives texts: string literals of 24 or more characters, prompt lines of 30 or more, and `tick:` names. Condition 2 holds when a text appears in `turns.system`, `turns.user`, `sessions.wake_kind`, `wake_detail` or the seat log after the change and in none of the three nights before, or the reverse for a removed text. Condition 3 holds when the text appears in a session of the moved count: a session that names a merged batch, the writer of a batch row, a session of a waiting batch, a later batch start, a Developer session, a session before the first batch start, or the role and wake group whose count changed most (observed: `grade.py`). The reader checked the four rows below by hand. The other 43 rest on the script alone.

| night, move | commit, frame, origin | condition 1: the diff | condition 2: the rows | condition 3: the units |
|---|---|---|---|---|
| 96, merged 0 to 1 | `f9f6edc9a`, frame 90, wall | `structural_review.md` adds "When no constraint other than `k0` is in range, no constraint binds this diff." | the line is in nights 96, 97 and 98, and in none of 93 to 95. Night 95 quarantines `architect\|tick:structural_review\|bg_1` at 3 attempts. Night 96 has no such key | night 96 s144, architect, `tick:structural_review` on the merged bg_1, holds the line in 5 turns. 1 of 9 sessions of the merged batch, 0 of 302 others |
| 151, merged 1 to 2 | `7a2cb843d` and `966a978fb`, frame 243, wall | `runner.py` adds `CONTESTS_KEY = "the principal contested these criteria"` and `f"{cid}: He contested this text: {text}"` | the block is in nights 149 to 153 and in none of the three nights before the change | night 152: 16 of 34 sessions of merged batches, for example s203, Developer, `tick:batch_start` on bg_2. 10 of 263 others |
| 159, per merge 146 to 211 | `8b1566c86`, frame 201, wall | `api.py` adds `_HOLD_SAY = "Say which in one sentence, and send the call in the same reply."` | the text is in nights 159 to 161 and in none before | night 161: 5 of 31 sessions of merged batches, 0 of 379 others |
| 139, sessions 396 to 283 | `2c602d1bb`, frame 190, wall | the landing brief adds "`items` to the Vision Keeper, `glossary_terms` and `criteria` to the ..." | the line is in nights 137 to 141 and in none before. It appears two nights before the move | the Liaison's message sessions fall from 133.6 to 68.3 a night. Night 139: 19 of 65 of them hold the line, 0 of 218 others |

The grade "mechanism seen" is weak by construction in three ways (reasoned). A brief line reaches every session of its desk, so condition 3 holds for any edit of the brief of the moved units. Condition 3 does not ask that the other units lack the text, so the counts of the other sessions in the table above are the only test of that. And a reworded text can be new while its old form never fired in the three nights before.

## 5. The reverse view

The pool is every commit to `rota/` from night 82 to the turn before night 172, so three turns follow each one. Lines are the lines added and removed under `rota/` (observed: `reverse.py`). 73 of the 85 turns from night 87 to night 172 have a move in the next three runs, so 86% of any changes have one (observed). A change that moved nothing is not visible at this rate (reasoned).

| origin | the ten largest, lines | a move in the three turns after |
|---|---|---|
| wall | `61a0f41d2` 1,029, `5480f6b61` 948, `a304084bf` 692, `f934ec212` 661, `aae59d4b3` 594, `0118233f7` 573, `63d9042ce` 525, `11d04b18f` 511, `2dace61be` 449, `358fed110` 425 | 10 of 10 |
| plan or neither | `f3205688f` 1,060, `f35a7585a` 915, `33dbaa35a` 660, `9522746a1` 623, `b0a2086e5` 614, `ac1b83ede` 539, `efde1aea9` 529, `a47b69e6c` 483, `592371dea` 472, `c888968b9` 468 | 8 of 10. `33dbaa35a` and `ac1b83ede` land before night 83, and nights 83 to 85 cannot hold a move by the rule |

## 6. The dry runs

- The second table of part 1 holds the request, the repository and the commit of each run. The request changes at dry4 and stays the same in every later run with a batch. The fold sentence merged in none of its 6 runs with a batch. The repository icalendarI merged once, on dry3's request, so the repository alone does not separate the groups (observed; reasoned).
- The commit changes at dry4 too. From `44088319` to `97939168` are 10 commits on `rota/` and 655 lines added, all of them frame 362's onboarding passes. To `d856c51d` are 164 commits and 9,680 lines added (observed: `git rev-list`, `git diff --shortstat`).
- The seat, the models and the fresh start are the same for dry1 to dry9. Only blind run 1 changes the seat, and it formed no batch (observed).
- No run holds the fold sentence at dry3's commit, and no later run holds a merged request. So the request and the commit cannot be told apart (reasoned).

## 7. Limits, and what the reader could not find

- One reader and one pass. The script graded 510 candidates. The reader checked four by hand (part 4).
- No pair of equal runs with a fresh start exists, so the noise is not measured. The thresholds d are the reader's, and a move is a description of the rows, not a test (reasoned).
- The session key follows the database. 68 batches of the stops read share their first session with an earlier night by content. This page counts those sessions as new when the database is new (observed).
- Nights 82 to 86 and dry run 1 have a commit "by date" only. Nights 82 to 84 have no night log, so their walks are not known. The page texts of nights 82 to 132 are not stored, so condition 2 cannot see a page change there (observed: `product-stops-read`).
- 135 commits name no frame in a message, a stack block or a merge (observed). A commit can lie in two ranges when a run started from a worktree. The script takes each commit once, from `git log A..B` (observed).
- Condition 3 has no unit for a fall of "waits behind". The script uses the later batch starts in its place (reasoned).

## A reading, apart from the tables

Most moves sit at, or near, a change of the run's conditions. The commits before a move almost always exist, because a move follows 86% of turns. So the commit grades say little about cause, and the four checked rows are the strongest the records hold. Night 96 is the one case where a wall, its fix, the text in the merged batch's own session and the end of a quarantine line up. Its window still holds harness changes. A pair of equal runs at two commits is what would separate a change from the noise (reasoned).
