# Where the work stopped, by batch, 2026-11-10

One blind reader wrote this page for the review of rota, the product. The
reader read the rows of 11 run databases and 98 night databases, the
night logs and the agent seat's log. The reader changed no other file.

## Result

1. 304 batches exist. 77 merged and 227 did not. 23 request rows never reached a batch, and 7 runs formed no batch at all (observed: queries below).
2. A model's act ends 133 of the 227 stops (59%). The Developer on qwen3.5:9b is the stuck desk in 116 of the 125 stops that name a desk (observed: `tick_attempts`, `sessions`).
3. In 58 stops the model wrote nothing that a door accepted, up to its cap. In 54 it wrote code that stayed red or failed review. In 21 the team gave up first, and the seat's contest then cancelled the batch (observed).
4. A rule of rota ends 65 stops: 47 batches wait behind a parked batch, and 18 empty batches come from a grouping loop on a contested request (observed).
5. 45 of the 47 waiting batches sit behind a model give-up. So the root is a model's act in about 85% of the stops (reasoned).
6. The seat ends 21 stops. The words of nearly all these contests name a wrong row that the team wrote (observed: `rulings.words`).
7. On nights 133 to 175, a page names the stuck step for 29 of 105 stops (28%). Only 7 pages, in nights 165 and 169, name a door's refusal of a model's commit. No page names an invented tool result (observed: the agent seat's log).
8. No page names a queue, a cancel by contest, a run end or a server failure (observed).
9. The hand read of 30 drawn batches found 3 classes wrong (10%), and 1 kind wrong (3%) (observed: the draw).
10. Over the nights, merges per night rise from 0.29 to 1.26. The give-up classes stay near 30 stops per third, and the queue stop goes away (observed).

## The population and the counts

- The 11 runs of `plans/method/product-seat-population-2026-11-10.md`. Dry runs 6b and 6c share `dry6b.db`, and this page counts it one time as `dry6bc`.
- 98 files `D:/repos/rota/.rota/clickI_night*.db`. Five are copies of another night: `night87_partial`, `night91_partial`, `night91_walk1`, `night109_cut`, `night129_partial`.
- The night logs `D:/repos/rota/.rota/night*.log`, and the agent seat's log `D:/repos/rota/.rota/clickI_night175.principal.jsonl`.

| set | batches | merged | running | deferred | abandoned | pending |
|---|---|---|---|---|---|---|
| all files | 304 | 77 | 71 | 42 | 66 | 48 |
| without the 5 copies | 296 | 76 | 66 | 41 | 66 | 47 |
| dry runs and blind run 1 | 9 | 3 | 1 | 4 | 1 | 0 |

(observed: `batches.status`)

The second group holds the requests that never reached a batch. 7 runs formed no batch: `blind1`, `dry6`, and nights 83, 84, 85, 135 and 164a. Across all runs, 23 request rows have no batch. 12 are `draft`, 8 are `approved`, and 3 are `contested`. 6 of the 23 carry a `park` row from the seat's shift answer (observed: `items`, `item_parks`). The runs with no batch end in onboarding loops or on an open page. Examples are the Terminologist's `tick:term_collision` in nights 83 and 84, `tick:awaiting_confirm` in night 164a, and an open `present` in blind run 1 (observed: the last 12 sessions of each run).

## What each state means in the code

- `abandoned` comes from `lifecycle.abandon`, only by the `do:cancel` wake. `predicates.cancel` fires when the item is not `approved`, its approval is older than its version, or its newest park row is `drop` (observed: `rota/core/predicates.py` 1975 to 2004).
- A seat's `contest` or `revise` on the item sets `approval='contested'` (observed: `rota/roles/principal.py` 4279 to 4294). So a revise of line 1 cancels the batch and its work (reasoned).
- `deferred` comes from `do:preempt`, `do:park` (cap and spent ladder), `rota interrupt`, or a merge conflict (observed: `rota/core/loop.py` 499 to 520, `lifecycle.merge`).
- `pending` waits for `batch_start`, and `batch_start` refuses while another batch runs (observed: `rota/core/lifecycle.py` 78 to 81).
- A night is three walks. A walk ends on a merge, on `quiet` (no wake fires), at 250 steps, or on a stall (observed: `probes/walk.py` 230 to 330, `probes/gauntlet_click.sh` 128 to 139).
- Of 249 walks in the night logs, 140 end `quiet`, 73 merge, 23 have no end line, 12 reach the step cap, and 1 stalls (observed: `night*.log`).

## The classes

The classes come from the rows. `stuck desk` is the role and wake kind of the quarantined `tick_attempts` key, or of the wake whose detail reads `attempt N of N`. A batch counts as `gave up` when it has such a key or detail, or a `m_park_` page. Shares are of the 227 stops.

| class | n | share | kind | desk of the last acts | act | cause | model |
|---|---|---|---|---|---|---|---|
| gave up, nothing accepted | 58 | 26% | model wrote nothing a door accepted | developer 52, tester 3, critic 2, architect 1 | `tick:tests_failing` 48, `tick:tests_missing` 3, `tick:review` 2, `tick:batch_start` 3 | the last two Developer sessions on the batch commit nothing. Writes refused, invented tool results, prose claims of done | qwen3.5:9b, architect qwen3:8b |
| waits behind a parked batch | 47 | 21% | rule of rota | none. The scheduler holds it | `batch_start` refuses while one batch runs | one batch at a time. 45 of 47 sit behind a gave-up batch | none |
| gave up, code red or failed | 46 | 20% | model wrote wrong content | developer 46 | `tick:tests_failing` 44, `tick:touch_mistaken` 1 | the Developer commits, and the own or inherited tests stay red, or the Critic fails the diff | qwen3.5:9b |
| gave up, then the seat contested | 21 | 9% | model first, seat last | developer 13, critic 2, 6 with no key left, then liaison | give-up, then `rulings.rule` with `contest` on the item, then `do:cancel` | the give-up page goes to the seat, and its answer lands as a contest of line 1 | qwen3.5:9b, liaison qwen3:8b |
| empty batch of a contested request | 18 | 8% | rule of rota | architect 17 | `tick:grouping`, `batches.group`, then `do:cancel` | `tick:grouping` wakes the Architect for a ticket whose item is contested. Each new batch is cancelled at once | qwen3:8b |
| contested at the plan page | 17 | 7% | seat contested | liaison lands the ruling | `rulings.rule` with `contest` or `revise` on the item, then `do:cancel` | the seat faults a row the team wrote: wrong files, a wrong default, its own note pasted into line 1 | liaison qwen3:8b |
| item rewritten | 8 | 4% | model wrote wrong content | vision_keeper writes the item. 6 of 8 show a give-up first | `problem.*` writes a new item version, the approval goes stale, then `do:cancel` | the Vision Keeper changes the request text with no landed contest | qwen3:8b |
| open at a cut or a copy | 7 | 3% | run ended | developer 3, tester 2, liaison 1 | the last session of the run, or a copy file | the run stopped while the batch moved | qwen3.5:9b |
| set aside by the seat | 2 | 1% | seat | none | shift answer `park` | the seat put the request behind another | none |
| dropped by the seat | 1 | 0.4% | seat | developer gave up first | shift answer `drop` | dry run 2's second item | qwen3.5:9b |
| server failed | 1 | 0.4% | model server failed | developer | 3 failed `tick:touch_mistaken` sessions, `LLMUnavailable`, then quarantine | the failed sessions spent the wake's 3 attempts (dry run 7, sessions 217 to 222) | qwen3.5:9b |
| contested mid-work | 1 | 0.4% | seat | liaison | `rulings.rule`, then `do:cancel` | as the plan page, with work in flight | qwen3:8b |

(observed: `classes.json` from `classify.py` in the scratch folder. The kinds of the item-rewritten class and the server class rest on the order of `sessions.seq`, and that order is reasoned.)

The kinds by the terminal act: model 133 (59%), rule 65 (29%), seat 21 (9%), run end 7 (3%), server 1 (0.4%). Without the 18 empty batches the model share is 133 of 209 (64%). Without the 5 copy files it is 130 of 220 (59%) (observed).

The root by cause is different (reasoned). 45 of the 47 waiting batches sit behind a model give-up. 17 of the 18 seat contests keep their words. 16 of them fault a row the team wrote, and one reads "Ok, go ahead" (observed: `rulings.words`). Counted so, about 194 of 227 stops (85%) start at a model's act.

Three counts sharpen the classes (observed):

- `wrote its own tool results` is the most frequent line of the runner's account, 9,059 lines in all sessions. `repeat refused` follows at 5,845 (`turns` that start `SESSION ENDED`).
- 8 of the 39 contests that cancelled a batch carry words that ask the team to keep going, for example "Please don't give up on this change" (night 144, bg_1) and "Ok, go ahead" (night 146, bg_7).
- The Vision Keeper wrote the seat's own words into item text: "I don't know whether that example is there, and it doesn't matter here" is the text of one batch's item (`items.text`).

## The hand check of the draw

`random.Random(364).sample(lst, 30)` over the non-merged batches sorted by the database file name and the batch id. The reader read the last three sessions of each, their last `turns.completion`, the runner's account, the quarantine keys, the park pages and the landed rulings.

| # | batch | class by query | hand read | right |
|---|---|---|---|---|
| 1 | night92 b_2 | code red | the Developer says in prose that the code is done, three times, and writes nothing | no |
| 2 | night100 bg_2 | nothing accepted | `code.write` refused inside a docstring, `msg.challenge_tester` refused as a repeat | yes |
| 3 | night110 bg_2 | nothing accepted | four invented tool results, no commit | yes |
| 4 | night146 bg_4 | gave up, then contest | the Tester's tests refused at the door, then the seat contested the item | yes |
| 5 | night101 bg_1 | code red | Critic fail, a whole-file rewrite refused, run cut | yes |
| 6 | night105 bg_3 | waits behind | touch note approved, never started | yes |
| 7 | night118 vo_group | waits behind | as 6 | yes |
| 8 | night136 bg_2 | item rewritten | the Tester gave up first on `tests_missing` | no |
| 9 | night123 bg_4 | waits behind | as 6 | yes |
| 10 | night116 bg_2 | nothing accepted | `code.write` refused, the Developer ends the session | yes |
| 11 | night150 batch_2 | gave up, then contest | Critic fail on `separators=('', '')`, then contest | yes |
| 12 | night165 bg_1 | code red | own tests red at attempt 12 of 10 | yes |
| 13 | night97 bg_3 | nothing accepted | invented tool results, a rewrite refused | yes |
| 14 | night121 bg_1 | code red | own tests red at attempt 10 of 10 | yes |
| 15 | night168 batch_2 | waits behind | the seat parked it behind the first request | no |
| 16 | night171 bg_1 | code red | red own test, then a shift park | yes |
| 17 | night119 bg_3 | code red | red tests, the Developer claims a pass | yes |
| 18 | night94 bg_3 | nothing accepted | 34 inherited tests red, few commits | yes |
| 19 | night90 echo batch | nothing accepted | red own tests, last sessions commit nothing | yes |
| 20 | night86 bg_1 | nothing accepted | claims done with a red test | yes |
| 21 | night82 bg_1 | nothing accepted | questions unresolved, no code written | yes |
| 22 | dry8 bg_1 | code red | 5 inherited tests red, span write refused | yes |
| 23 | night107 echo_new | waits behind | as 6 | yes |
| 24 | night88 bg_2 | waits behind | as 6 | yes |
| 25 | night127 bg_1 | code red | a stray file, own test red | yes |
| 26 | night115 batch_vo | waits behind | as 6 | yes |
| 27 | night110 bg_3 | waits behind | as 6 | yes |
| 28 | night92 b_3 | waits behind | as 6, night cut | yes |
| 29 | night106 bg_2 | nothing accepted | the challenge refused as a repeat, no commit | yes |
| 30 | night95 bg_1 | nothing accepted | the Architect's `structural_review` quarantined after two Critic passes | yes |

3 of 30 classes are wrong (10%). Only number 15 changes the kind, from rule to seat (3%). The reader fixed the query for number 15 before the tables above. Numbers 1 and 8 stay as the query classes them (observed: the dumps of `draw.py`).

## Pages per class

Whole page texts exist for nights 133 to 175 in the agent seat's log, and for dry runs 5 to 8 in their turn logs. Nights 82 to 132 keep only the first line of a page in `night*.log`. There, the scripted seat answers every page "yes that all looks right, go ahead" (observed: `rulings.words`, the draw).

On nights 133 to 175, 105 batches did not merge. 87 have a page whose refs name the batch. 29 have a page that names the stuck step, and 15 of those use plain words (observed: `pagecheck2.py`).

| class | a page line that names the cause, or none |
|---|---|
| nothing accepted | "The team gave up on: tests_failing for bg_#, # attempts." The step is true. It does not say that the writes were refused or invented. 14 of 19 name the step |
| code red | "The team gave up: the tests still fail after # attempts." 7 of 17 name the step. Dry run 7 names the test and the error: "... still fail after 3 attempts: TypeError: q_split() got an unexpected keyword argument 'max_length'." |
| tester stuck | "The team gave up: the team could not write the tests after 3 attempts." |
| critic stuck | "The team gave up: the review gave no verdict after 3 attempts." |
| gave up, then contest | the give-up page, for 6 of 21. No page says that the answer cancelled the change |
| waits behind | none. No page holds "behind", "queue" or "another change" |
| empty batch | none. 17 of 18 have no page that names the batch |
| contested at the plan | none. The one line with "abandoned" is the shift option "- drop: stop it. Its change is abandoned." |
| item rewritten | none names the new item version |
| open at a cut | none |
| set aside, dropped | none after the answer |
| server failed | none. Dry run 7's park page reads "The team gave up: the team could not put back code it was not asked to change after 3 attempts." |

A search of 1,435 page texts finds no "wrote its own" and no line about a desk's model. 7 pages of nights 165 and 169 name a refused commit in plain words: "A check refused the commits, because the change rewrites `return` at line 609 of src/click/termui.py, in clear(), as `return False`." (observed: `pages.json`). The end-of-walk state in nights 82 to 132 prints "Stuck. The team gave up on: tests_failing for bg_2." This line is the state view in the log, not a page (observed: `night100.log`).

## The request kinds

The kind comes from the item text of the batch. "Runs" counts the files with a batch of that kind.

| request | batches | merged | not merged | runs | top class of stop |
|---|---|---|---|---|---|
| Let confirm() take a default_on_eof flag ... | 90 | 19 | 71 | 66 | empty batch 17, waits behind 15 |
| Give version_option a show_python flag ... | 76 | 7 | 69 | 65 | waits behind 28, nothing accepted 16 |
| Add an echo_json(obj) helper next to echo ... compact JSON | 74 | 32 | 42 | 63 | code red 14, nothing accepted 13 |
| In get_app_dir on Windows, when APPDATA or LOCALAPPDATA is not set ... | 15 | 6 | 9 | 12 | contested at the plan 3 |
| Give format_filename one example in its docstring ... | 12 | 3 | 9 | 12 | code red 3, nothing accepted 3 |
| Add an echo_json(obj, indent=2) helper ... | 11 | 1 | 10 | 11 | nothing accepted 5 |
| Make clear() return True when it cleared the screen ... | 10 | 6 | 4 | 10 | nothing accepted 2 |
| When icalendar writes a long line, fold it at a space ... | 5 | 0 | 5 | 5 | code red 3 |
| item text that drifted from any request | 7 | 0 | 7 | 4 | item rewritten 2 |
| Make tip_calculator.calculate_tip() raise ValueError ... | 2 | 1 | 1 | 1 | dropped 1 |
| Make click.pause() return True ... | 1 | 1 | 0 | 1 | none |
| Make icalendar.caselessdict.canonsort_keys() raise ValueError ... | 1 | 1 | 0 | 1 | none |
| Refuse a negative bill amount ... (blind run 1) | 0 | 0 | 0 | 1 | no batch |

(observed: `items.text` by regular expression)

Two sentences never merged: the icalendar fold, in dry runs 4 to 8, and the bill amount of blind run 1, which never reached a batch. The drifted item texts never merged either. The version_option request merged in 7 of 65 runs (observed).

## The stops over time on the nights

The 93 night files without the copies, sorted by number, in three thirds of 31 (observed).

| third | nights | batches | merged per night | top stops |
|---|---|---|---|---|
| 1 | 82 to 112 | 72 | 0.29 | waits behind 25, nothing accepted 24, code red 11 |
| 2 | 113 to 145 | 117 | 0.81 | waits behind 20, code red 18, empty batch 18, nothing accepted 17, gave up then contest 10 |
| 3 | 146 to 175 | 98 | 1.26 | nothing accepted 15, contested at the plan 14, code red 12, gave up then contest 11 |

- The queue stop goes from 25 to 20 to 1. The empty batch loop appears in nights 133 and 137 only.
- The two give-up classes stay: 35, 35 and 27 stops by thirds. The main act is `tick:tests_failing` in each third.
- Contests that cancel a batch go from 0 to 13 to 26. The agent seat starts at night 133, and the scripted seat answered before it. So the change of seat explains part of this rise (reasoned).

## Limits, and what the reader could not see

- No row records the moment of a cancel or a deferral. The order of events comes from `sessions.seq` of the ruling's receipt and of the wake details (reasoned).
- The split between "nothing accepted" and "code red" reads `code.commit` calls in the Developer sessions whose `wake_refs` name the batch. A session woken by a message can miss the link, as in draw number 1.
- No query separates wrong code from a wrong test. Several Developers challenge the Tester's test, and the hand read could not settle who was right.
- 68 batches share the creating session's prompt hash and first completion with an earlier night. The nights replay the same start, so they are not independent samples.
- `lifecycle.mergeable` ran from today's code on old rows, on a read-only connection. The gate state is approximate on old schemas, and 2 calls failed.
- Page text is whole only for nights 133 to 175 and dry runs 5 to 8. For nights 82 to 132 the page classes rest on the first line of each page.
- The walk end comes from the night log. 22 nights have no end line for their last walk, and 3 nights have no log.
- The dry runs hold 6 non-merged batches. Their run ends are the build session's choice, and this page does not read those transcripts.
- The scratch scripts and their JSON outputs are in `C:\Users\roman\AppData\Local\Temp\claude\6d9eb18c9e6274ab\1efd37b1-058e-4b19-8ab1-e1a6c654a389\scratchpad\stops\`.
