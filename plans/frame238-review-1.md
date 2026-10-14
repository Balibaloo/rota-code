# Frame 238, pass 1: the diff review of the set_approval door

Review of 252feb0e over 9624565c on the worktree `C:/Users/roman/rota_rv238`. Rota workflow, the Vision Keeper's `problem.set_approval` door. Read-only. Date 2026-10-14.

**Verdict: accept.** The pass repairs night 147's case at HEAD, and the parent admits it. The findings are four, all low. They can go to a pass 1b or to a later frame. None blocks the walk.

## (a) The verdict on each point

1. Pass. At HEAD the door refuses all four of s285's calls. At the parent the two item calls land as `contested`.
2. Pass, with finding 2. The prefilter only widens, and the parse decides. The chain's ruling wins over a newer landed ruling on the id.
3. Pass. The relay with `contest` still lands. The relay with `approve` and a call of `contested` meets the old relay branch. Its text is right.
4. Pass. Only `relay.tools` offers `problem.set_approval`, so the defect cannot pass through the other three wakes. No pass 1b is needed for a second branch.
5. Pass. The id list never reads empty. Both texts are true. Finding 1 is the false clause in the other refusal.
6. Two of the four tests are red on the parent. The fallback path, the null cause and the "some refs are rows" text have no test (finding 3).
7. Pass. The texts follow STE, and no pronoun names the principal. The two files hold 0 carriage-return (CR) bytes.

## Point 1: the night's case

The probe `p1.py` copies `clickI_night147.db` and cuts the records to s285's moment. It deletes the rulings after rowid 31 (r_6b1268aa4d) and the messages after m136 (seq 138). It builds the Vision Keeper's sandbox in the `relay` mode with the trigger m136. Then it makes s285's four calls, once with the worktree's code and once with the parent's code from `git archive 9624565c`.

At HEAD (observed: 2026-10-14):

- `constraints:click_context`, `contested`: refused, "...; the relay names ['constraints:click_context', 'constraints:click_log'], and they are not items rows. Answer what the relay names, or end the session".
- `constraints:click_log`, `contested`: the same refusal.
- `confirm_default_on_eof`, `contested`: refused, "the principal approved confirm_default_on_eof on m131, ruling r_6b1268aa4d, and this relay does not name it. Leave it." The chain path found the ruling.
- `defines_commands_and_options`, `contested`: refused, "the principal approved defines_commands_and_options on m86, ruling r_fc68f68228, and this relay does not name it. Leave it." The chain's ruling does not name the id, so the fallback found r_fc68f68228.

At the parent, the two constraint calls get the old list of the first six item ids. The two item calls return `{'id': ..., 'approval': 'contested'}`. That is night 147's defect.

## Point 2: the fallback

The prefilter is `per_item LIKE '%"<id>"%'`, with `json.dumps` quotes on the id. The quotes stop a substring match: `"confirm_default_on_eof"` does not match `"cr_1_confirm_default_on_eof"`. An id that equals a value word matches. On night 147, `approve` matches 29 rows and `contest` matches 15, and the parse finds 0 of them. The `_` wildcard widens the match in the same way. The probe `p2.py` checked all 86 ids in night 147's rulings, and the prefilter missed no row for any id. Both writers in `principal.py` (lines 1987 and 2069) store `per_item` with `json.dumps`, and the door uses the same function, so the escapes agree. Case D in `p3.py` puts `cr_1_<id>` as a key and `<id>` as a value, and the door admits the call. So the fallback does not read the wrong row.

The newest landed row is the principal's latest word in rowid order. On night 147 the words change in both directions on ten ids. For example, `defines_commands_and_options` reads approve, approve, contest, approve, and `ver_opt_show_py` reads revise, approve. A `revise` is not in the approve set, so the door admits a contest after a revise. The one gap is the order of the two sources. The chain's ruling comes first, even when a newer landed ruling names the id. Case C in `p3.py` adds a newer ruling that contests the item, and the door still refuses the contest on the chain's older approve (finding 2).

## Point 3: the relay that names the item

Case A2 in `p3.py` has a relay verdict of `{item: contest}`. A call of `approved` meets the relay branch: "the principal ruled confirm_default_on_eof contest. land wrote `contested`, and the contested wake carries the words. Leave it". The new test `test_a_relay_that_names_the_item_with_contest_still_contests_it` shows that the `contested` call lands. Case A has a relay verdict of `{item: approve}` and a call of `contested`. The old relay branch at `api.py:1688` refuses first: "the principal ruled confirm_default_on_eof approve. land wrote `approved`. Leave it". The new branch does not run, because `ruling` is not None. The text is right.

## Point 4: the wakes that are not relays

The runner builds each session with `allow=prompts.mode_tools(role, _mode_key(wake, conn))` (`runner.py:3284`). In the Vision Keeper's prompts, only `relay.tools` holds `problem.set_approval`. `contested.tools`, `challenge.tools` and `exhausted.tools` do not hold the op, and the three `.md` files do not name it. So a seat on those wakes cannot call the door, and the defect cannot pass through there. The new test on a `normal` mode wake reaches the door only because a sandbox in a mode with no `.tools` file allows every op. The runner keys each mover session's prompt mode from its wake (reasoned: `_mode_key`). A second branch is not a pass 1b. A second branch becomes a later frame only when a mode other than the relay gains `problem.set_approval`.

## Point 5: `_must_exist` on a relay

The branch runs only when `_relay_refs` returns a list that is not empty. So the id list never reads empty. When no ref is a row of the table, the text is "the relay names [...], and they are not items rows. Answer what the relay names, or end the session". That text is true on m136. In the relay mode, "Answer what the relay names" has no op for a constraint, so "or end the session" is the exit the seat can take. When the relay names an item that exists and the call names another, the text is "the relay names [X], and the items rows among them are [X]". That text is true, and it shows the seat the right id. The branch covers every caller of `_must_exist` on a relay wake. The map shows 20 callers. The three relay modes (Architect, Terminologist, Vision Keeper) reach only `problem_set_approval` and `problem_prioritize` among them. So the wider scope changes no other seat today (reasoned: the `.tools` files and the map).

The false text is in the other door. On a relay that names the id but carries no verdict for it, the new refusal says "this relay does not name it". Relay m147 names `confirm_default_on_eof`, and its cause m146 is a `converse` with the landed ruling r_640b861a13. A probe on m147 got "the principal approved confirm_default_on_eof on m145, ruling r_640b861a13, and this relay does not name it. Leave it." The refusal is the right result, because the principal approved the item. The clause is false (finding 1).

## Point 6: the tests

The probe ran the HEAD test file against the parent's code in `parent/`. The result is `2 failed, 2 passed`. These two tests are red on the parent:

- `test_a_relay_cannot_contest_an_item_the_landed_ruling_approved`
- `test_a_missing_row_on_a_relay_lists_the_relays_refs`

The other two tests pin the old rules and are green on the parent, as intended. At HEAD the whole file is `102 passed, 4 xfailed`. A test covers the chain path through `chain_verdict`: the fixture's ruling r_6b1268aa4d names the item, and its `verdict_id` is m133. Three branches have no test. The first is the fallback, which night 147 needs for `defines_commands_and_options`. The second is a relay whose `cause_id` is null. Case B in `p3.py` shows that this relay reaches the fallback and refuses. The third is the "items rows among them" text of `_must_exist`. The route sentence with `decisions.author` has no test, and no mode can show it (finding 4).

## Point 7: STE and the bytes

The refusal texts use the active voice and short sentences. "It" in "does not name it" has its referent in the same sentence. "They" in the `_must_exist` text refers to the refs, not to the principal. No text or comment names the principal with a pronoun. A byte count finds 0 CR bytes in `rota/roles/api.py` and in `tests/rota/test_request_page.py`.

## (b) Findings

1. `rota/roles/api.py:1695-1706`, low, CONFIRMED. The new branch checks only that `_relay_refs(ctx)` is not empty. It does not check that the relay omits the id, which the commit body states. On m147, which names `confirm_default_on_eof`, the refusal says "this relay does not name it". The probe `p1.py m147` showed the text. The result is right and the clause is false.
   Fix: keep the predicate, and write "and this relay does not name it" only when `id not in _relay_refs(ctx)`.
2. `rota/roles/api.py:1759-1773`, low, CONFIRMED. `_landed_approval` takes the chain's ruling before a newer landed ruling on the id. Case C in `p3.py` adds a newer ruling that contests the item, and the door still refuses the contest on the older approve. A relay that waits while a newer ruling lands can meet this order.
   Fix: take the higher rowid of the chain's row and the newest landed row that names the id.
3. `tests/rota/test_request_page.py:1002-1070`, low, CONFIRMED. No test covers the fallback, a relay with a null `cause_id`, or the "items rows among them" text. Night 147's `defines_commands_and_options` call needs the fallback, and probes `p1.py` and `p3.py` case B ran these paths.
   Fix: add one test where the chain's ruling does not name the id and an older ruling approves it, and one test with a null cause.
4. `rota/roles/api.py:1701-1703`, low, CONFIRMED. The route sentence with `decisions.author` cannot show. Only `relay.tools` offers `problem.set_approval`, and `relay.tools` does not offer `decisions.author`. The implementer's report gives the same reading.
   Fix: remove the route sentence, or keep it with a test that builds a mode that holds both ops.

Outside the points: no new defect. The implementer's open points 2 and 3 are outside this pass's site: the `tick_attempts` quarantine, and the constraint refs that reach the relay mode. They need their own frames.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/f3b11814-a94a-4967-b659-274275321190/scratchpad/rv238/`.

- `q1.py`, `q2.py`, `q3.py`: read-only queries on `clickI_night147.db` for the rulings, the messages m125 to m150, the `verdict:` config rows, the items and the Vision Keeper's sessions.
- `p1.py ROOT TRIGGER RULING_ROWID_MAX CALLS`: copies the night database, cuts it to the trigger's moment, and calls the door in the `relay` mode. Runs: m136 at HEAD and at the parent, and m147, m141 and m143 at HEAD.
- `parent/`: `git archive 9624565c` of `rota`, `tests`, `pytest.ini`, `pyproject.toml` and `rota_serial_plugin.py`, with the HEAD test file over the parent's. `pytest -n0 -k` on the four new tests gave `2 failed, 2 passed`.
- `p2.py`: compares the LIKE prefilter with the parsed `per_item` for the 86 ids of night 147, and lists the ids whose words change.
- `p3.py ROOT`: synthetic cases on the test module's helpers. A: a relay `approve` and a `contested` call. A2: a relay `contest` and an `approved` call. B: a relay with a null cause. C: a chain approve and a newer contest. D: a substring key and a value.
- `pytest tests/rota/test_request_page.py -q` at HEAD from the worktree: `102 passed, 4 xfailed`.

## (d) Usage

The harness counter showed about 70k tokens of context growth over the review. Output was about 12k tokens. The total is about 80k, which is over the 50k cap by about 30k. Read the harness line for the exact figure.
