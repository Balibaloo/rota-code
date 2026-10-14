# Frame 240, pass 1: the diff review of be5e63d9

Reviewer: a read-only agent on the worktree `C:/Users/roman/rota_rv240` at be5e63d9, over cb253a75. Rota workflow. Date: 2026-10-14.

## Verdict

Accept. The lift lands on a changed approval and stays off on a same-value write. The probes confirm both at HEAD and the defect at the parent. Counts: 0 high, 2 low. Both low findings are outside the points.

## (a) The verdict on each point

1. The night's key: PASS. HEAD lifts the key on contested to approved and keeps the key on approved to approved. The parent keeps the key in both cases.
2. The lift's width: PASS. The width equals the width of `session_commit` for an item write. No ruling forbids a lifted key. The `-|do:park|<bid>` key stays.
3. STE and CR bytes: PASS. The comment is STE within limits. Both files hold 0 CR bytes.

## Point 1, the night's key

Night 147's database holds `vision_keeper|tick:contested|defines_commands_and_options` at 3, 1, 1. The item is `approved` at version 1 after m148. The probe built the state with the item `contested`, the key at 3, 1, 1, and an open `present` that names the item. The probe then landed `Answer(verb="verdict", per_item={item: "approve"})` through `land`.

- HEAD, contested start: `land` returns the relay id `m10`. The item goes `approved`. The key row count is 0.
- HEAD, approved start: `land` returns `m10`. The `UPDATE` changes 0 rows. The key row count stays 1.
- Parent cb253a75, contested start: the key row count stays 1. The new test fails at line 60, `1 failed, 1 passed`.
- Parent, approved start: the key stays. The test passes.

The rowcount gate holds frame 80's rule. `approval IS NOT ?` in the `WHERE` makes the rowcount 0 on a same-value write.

## Point 2, the lift's width

The `Write` is `items`, the ref, `{"approval": state}`, `update`. The lift receives `moved=True`. The `commit` flag is false, so the fifth parameter is `"\x00"`, and the `NOT LIKE` excludes nothing. The four patterns match every quarantined key whose refs list holds the item id as one element. The probe deleted these keys on a contested-to-approved landing:

- `vision_keeper|tick:contested|<item>`
- `liaison|tick:park_ask|<item>,bg_1` (the park ask names the item first, `predicates.py:1723`)
- `-|do:preempt|bg_1,<item>`
- `developer|tick:reopen|bg_1,<item>`
- `liaison|tick:quarantined|x,<item>,y`

The `-|do:park|bg_1` key stays, because the park key names the batch only (`predicates.py:1534`). The lift's LIKE does not match a batch id from an item id. The ruling of frame 86's pass 4 review forbids a commit from lifting the park key. The ruling does not cover an approval write, and the park key stays anyway. `session_commit` already lifts the same set when a seat writes an item approval through the pipeline. The landing therefore adds no new width. Each lift here needs a principal keypress that changes the row, so law 6 still bounds a loop by the principal's own rulings.

## Point 3, STE and CR bytes

`tr -cd '\r' | wc -c` gives 0 for `rota/roles/principal.py` and 0 for `tests/rota/test_frame240_land_lifts.py`. The comment has five sentences. The longest sentence has 25 words and describes, so the 25-word limit holds. "Law 6." is a fragment. The fragment is the repository's usual pointer form, and it is not a finding.

## (b) Findings

1. Outside. `rota/core/db.py:596-601`, severity low, CONFIRMED. The lift builds LIKE patterns from the raw row id. SQLite LIKE reads `_` as one wildcard character and ignores ASCII case. The probe landed an approve on `defines_commands_and_options`. The lift also deleted the quarantined keys `...|definesXcommands_and_options` and `...|DEFINES_COMMANDS_AND_OPTIONS`. The defect is older than this commit, and `land` is one more caller. A collision needs two item ids that differ only at an underscore or in case. Fix: escape `%`, `_` and `\` in the row id and add `ESCAPE '\'`, or match with `instr` on the split refs.
2. Outside. `rota/roles/principal.py:1898` and `:2063`, severity low, PLAUSIBLE. `land` resolves a ledger row through a raw `UPDATE ledger SET status` with no lift. `_subject_state` counts a status change as a move. A quarantined `liaison|tick:unresolved|<ledger id>` key then outlives the entry, which is frame 240's shape on another table. The probe did not test whether the walk's end reports such a key. Fix: read the rowcount and call `_lift_quarantines` with a `Write("ledger", ...)` when the row moved.

Note, not a finding: the pass report shows the gate at 9 new reds from the checkout. This review ran no gate, as the brief says, and does not judge those reds.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4a757f92-bd97-4750-9830-bd149134e576/scratchpad/rv240/`.

- A read-only `sqlite3` query on `D:/repos/rota/.rota/clickI_night147.db` read `tick_attempts` and the item row.
- `parent/` holds `git archive cb253a75 rota`, with `test_p1.py`, a copy of the new test. Pytest from `parent/` imports the parent package (checked: `rota.__file__`). Result: `1 failed, 1 passed`.
- From the worktree, `pytest tests/rota/test_frame240_land_lifts.py -q` gives `2 passed`.
- `probe_width.py` runs with `PYTHONPATH` set to the worktree. The probe seeds nine quarantined keys, lands an approve from `contested` and from `approved`, and prints each key as kept or lifted.
- A `tr -cd '\r' | wc -c` count on the two files.

## (d) Usage

About 22k input tokens and 7k output tokens, about 29k in total. These are the agent's estimates. Read the harness line for the true count.
