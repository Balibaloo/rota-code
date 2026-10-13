# Frame 204, pass 4, step 0: the defaults that reach a binding other than `k0`

Status 2026-10-13 08:04: written by an agent of session 0c045f37 for frame 204, the seat's note, pass 4, step 0. Not committed.
The rows are the rota workflow's rows. The meta workflow reads them.

## Verdict

**0 defaults reach a binding other than `k0` on nights 136 to 144.** Pass 4 waits for frame 179.
The rule of design section 6 has no hit on the sample, so it measures nothing (reasoned: design section 10, pass 4, step 0).

- 9 of 9 nights were read. No database was missing (observed: `.rota/clickI_night136.db` to `.rota/clickI_night144.db`, 2026-10-13).
- 0 hits of category 2 over 9 nights, against 581 `kind = 'default'` rows (observed: the script `count.py`, 2026-10-13).
- 1 row reaches a non-`k0` binding by a criterion's surface. That row is `invented`, category 1, which section 6 excludes. See section 3.
- The binding exists, but the work goes elsewhere. Every non-`k0` binding is a `path` grain on `src/click/__init__.py`, `globals.py`, `_utils.py`, `core.py` or `cmd_status.py`, and on night 141 also `utils.py`. The defaults with a grain sit on `termui.py`, `decorators.py`, `utils.py` and the docs (observed: section 2 and the `GRAIN` lines of `grains.out`).

## Method

The scripts are in the scratchpad folder `step0` of session 0c045f37: `survey.py`, `count.py` with `count.out`, and `grains.py` with `grains.out`.
Each script opens `D:/repos/rota/.rota/clickI_night1NN.db` with `file:<path>?mode=ro`. Nothing was copied.
The session of a row comes from `receipts` where `table_name = 'ledger'`.

"Reach" follows design section 6. The script gives a row its grains by four routes:

1. `about_table = 'criteria'`: the criterion's `surface_refs`.
2. `about_table = 'tests'`: the test's `path`, and the `surface_refs` of the test's criterion.
3. An `about_ref` or an `about_table` that holds a path or a `path::symbol`.
4. A bare symbol, such as `echo_json`, resolved to its file through `code_index` symbol grains.

A symbol grain reaches a binding when its file equals the binding's `path` grain (reasoned: a symbol lives in its file, and every binding on these nights is `grain_kind = 'path'`).
The batch-time join in `needs_structural_review` (`rota/core/lifecycle.py:337-340`) matches `grain` and `grain_kind` both, so it is stricter than this count. The file-level count is therefore an upper bound.
Bindings count only with `resolves = 1` and `constraint_id != 'k0'`. `k0` has no binding rows, so it is global (observed: `constraint_bindings`, all nights).

A second pass scans the text `default_taken` for a bound path or a constraint's headline as a whole word. Section 3 lists those rows apart, because the design's rule reads `about_ref`, not prose.

## 1. The ledger rows of kind `default`

The `kind` column exists on all nine nights (observed: `PRAGMA table_info(ledger)`, 2026-10-13).
On nights 136 to 140 the kinds are only `default` and `unaddressed_answer`. On those nights `default` is the column's `DEFAULT 'default'`, not a seat's choice (reasoned: `schema.sql`'s column default, and pass 1's kinds first appear on night 141).
So on nights 136 to 140 the `default` count is every note, not category 2. Design section 2 puts category 2 at about 40 over nights 120 to 139 (reasoned: the category's definition, the grid's estimate).
The split does not change the verdict. The script tests every row of every kind, and no category-2 row reaches a non-`k0` binding (observed: `count.out`).
On nights 141 to 144 the `kind` column is pass 1's word, so the count is observed.

## 2. The constraints and their bindings

| Night | Non-`k0` constraints | Bound files (`path`, `resolves = 1`) | Global non-`k0` |
|---|---|---|---|
| 136 | 21 | `__init__.py`, `_utils.py`, `core.py`, `globals.py` | none |
| 137 | 11 | `__init__.py`, `_utils.py`, `globals.py` | none |
| 138 | 11 | `__init__.py`, `_utils.py`, `globals.py` | none |
| 139 | 12 | `__init__.py`, `_utils.py`, `globals.py`, `examples/complex/complex/commands/cmd_status.py` | none |
| 140 | 11 | `__init__.py`, `_utils.py`, `globals.py` | none |
| 141 | 18 | `__init__.py`, `globals.py`, `utils.py`, `cmd_status.py` | none |
| 142 | 16 | `__init__.py`, `globals.py` | none |
| 143 | 12 | `__init__.py`, `_utils.py`, `globals.py` | `put_echo_json_in_click_s_utils_module`, `is_global = 1`, no binding |
| 144 | 12 | `__init__.py`, `_utils.py`, `globals.py` | `echo_json_helper`, `is_global = 1`, no binding |

The paths are under `src/click/` unless named whole (observed: `survey.py`, 2026-10-13).
The constraints are onboarding's symbol claims, for example `get_current_context`, `Sentinel.UNSET` and `click.option`. Each binds the file that imports or defines the symbol.
`click_echo` on night 141 is the only binding on `src/click/utils.py`. No other night binds the file where `echo_json` lands.
The global constraints of nights 143 and 144 hold no binding. Section 6's rule reads `constraint_bindings.resolves = 1`, so a global constraint is not a hit (reasoned: section 6's text). `needs_structural_review` already returns true for a global constraint (observed: `lifecycle.py:325-330`), so those nights' batches needed a review whatever the rule says.

## 3. The intersection

**Hits of category 2: 0 on every night.**

The one structural reach is not a default:

- Night 141, session s154, row `l_db2560f0a6`, kind `invented`, author `tester`, `about_table = 'criteria'`, `about_ref = 'echo_json_compact'`. The criterion's surface `echo_json` resolves to `src/click/utils.py`, which `click_echo` binds. Text: "the test assumes key and nested where the material is silent". Category 1, so section 6 checks nothing (observed: `count.out`).

The rows that name a binding in their text only. None is category 2 on a bound grain:

- Night 136, s16, rows `l_a2abe4c2ba`, `l_b961d44cd4`, `l_1356abcf03`, `l_678428bc33`. Vision Keeper `how_it_works` notes on `items`. They quote the docs' words `Context`, `Command`, `Group`. An item carries no grain (reasoned: section 6 names criteria, tests and paths as the routes).
- Night 136, s383, `challenge_constraints_parametersource_environment`, author `critic`. "the Critic falsified constraints:parametersource_environment against src/click/core.py: ...". Category 9, a finding on a constraint row.
- Night 136, s518, `l_d8c6621aa2`, author `architect`, about `constraints:get_current_context`. "The principal contested the constraint 'get_current_context' and requested a specific change related to the version option." An echo of a ruling, category 8.
- Night 141, s15 to s46, 18 `conflict` rows by the Vision Keeper on `items`. They quote `@click.command` and `@click.option` from the docs. Category 3, on items.
- Night 142, s79 and s86, `challenge_constraints_click_file` and `challenge_constraints_click_exceptions_clickexception`, author `critic`. Category 9.
- Night 144, s176 `l_6d47c2386a` and s317 `l_b8b8a65afa`, on `items:echo_json`. They name "echo_json helper", the headline of the global constraint `echo_json_helper`, which has no binding.

One borderline row: night 136, s87, `l_c8628f6824`, author `liaison`, `model_areas:src/click`, text "source". The area holds bound files. The row is a gap, category 10, and section 6 checks nothing for a gap (observed: the row, 2026-10-13).

## 4. The defaults that reach `k0` alone

Every `kind = 'default'` row reaches `k0` alone, because no default reaches another binding.

| Night | Ledger rows | `kind = 'default'` | Of those, with a code or doc grain | Category-2 hits | `k0` alone |
|---|---|---|---|---|---|
| 136 | 217 | 210 (all notes, reasoned) | 96 | 0 | 210 |
| 137 | 94 | 92 (all notes, reasoned) | 53 | 0 | 92 |
| 138 | 71 | 71 (all notes, reasoned) | 40 | 0 | 71 |
| 139 | 63 | 63 (all notes, reasoned) | 38 | 0 | 63 |
| 140 | 64 | 62 (all notes, reasoned) | 31 | 0 | 62 |
| 141 | 47 | 8 (observed) | 3 | 0 | 8 |
| 142 | 86 | 30 (observed) | 19 | 0 | 30 |
| 143 | 65 | 15 (observed) | 7 | 0 | 15 |
| 144 | 95 | 30 (observed) | 11 | 0 | 30 |
| Total | 802 | 581 | 298 | 0 | 581 |

The grain column counts docs paths of `items` rows as grains, so it is generous. The files the defaults reach on nights 141 to 144 are `src/click/termui.py`, `src/click/decorators.py`, `src/click/utils.py`, `examples/imagepipe/imagepipe.py` and three test files (observed: the `GRAIN` lines of `grains.out`).
The defaults sit on `confirm`, `version_option` and `echo_json`. The constraints sit on the context stack, the sentinels and the package's `__init__.py`. The requests of these nights do not touch the bound files (reasoned: the two file lists do not meet, except `utils.py` on night 141).

## Verdict, restated

The total of category-2 hits over nights 136 to 144 is 0. Pass 4 waits for frame 179.
The cause is not that the bindings are empty. The onboarding constraints bind files that the nights' requests do not edit (reasoned: sections 2 and 4).
A sample that reaches a bound file needs a request on a bound file, or frame 179's constraints that bind the request's area.
