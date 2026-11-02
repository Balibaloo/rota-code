# Frame 330, review p4: the park ceiling reads every ruled line

Commit `e9b522ca` in `C:/Users/roman/rota_f354r`. `git log -1 --oneline` printed `e9b522ca fix(roles): a park page's contest of a check line keeps the verdict open`.

## Result

Verdict: **hold**. The fix works on the seat path only. The dry1 wall came through the Liaison path, and the fix does nothing on that path.

- High 1, CONFIRMED. On `apply_rulings`, the ceiling still closes the verdict on the dry1w9 copy. `apply_rulings` builds an `Ask` with no `order` (`rota/roles/principal.py:4115-4116`). So `lines` in `land` (`principal.py:3734`) is `ask.refs` only, and `tst_waited` is no ref. The probe re-landed `r_m139` through `apply_rulings`, and `m140` landed `answered`. All three park rulings on the copy (`r_m79`, `r_m128`, `r_m139`) carry a `reply_id`, so all three took this path. Fix: build `lines` from `ask.order or seen_order(conn, _reply_of(conn, ruling_id), ask)`, as `principal.py:3473` does, and add one test through `apply_rulings`. Price: two lines and one test, about 20 minutes. The probe shows that `seen_order` for `m139` returns the recorded order.
- Medium: none.
- Low 1, PLAUSIBLE. In `stage_park_relay` (`rota/core/sandbox.py:5264`), `c not in rows` also drops a test row's criterion when that criterion is itself a verdict row off the page. The case is a non-park page where an `about_ref` contest adds the criterion, and the principal contests the criterion's test as a page line. The criterion then reaches no relay. No case on the copy shows this. Fix: take the criteria of the verdict's test rows by a `tests` query, and do not subtract `rows`. Price: about 10 minutes.

## Point 1: the ceiling

The verdict lands `open` only when `land` gets the order. The probe `p1_ceiling.py` gave these results on the copy:

- A. `land` with the recorded order `order:m139`, as `probe_land.py` does: `m140` lands `open`.
- B. `apply_rulings` with `r_m139` set back to `open`: `m140` lands `answered`. This is High 1.
- B2. `land` with `ruling_id='r_m139'` and no order: `answered`. This is the same path as B.
- C. Every line `approve`, with the order: `answered`. Point 5 of the park ruling of 2026-10-08 holds.
- E. An approve of the refs only: `answered`.
- D. A `verdict` answer with an empty `per_item` and the text "ok" lands `open`. Its `body_refs` are the four page refs, so a Liaison wakes in `verdict_signoff` and has nothing contested to send. The predicate `all(per_item.get(r) == "approve" for r in ask.refs)` causes this result. That predicate is the same at the parent, so the commit causes no regression here.

`tst_waited` is a line of the order and no ref. The recorded `per_item` of `r_m139` contests `tst_waited` only.

## Point 2: the relay

The relay chain holds when the verdict is open. The probe `p2_relay_counter.py` ran from path A.

1. The verdict `m140` wakes the Liaison, and `_mode_key` gives `verdict_signoff`. CONFIRMED.
2. `stage_park_relay` stages `m141` to the Terminologist with `["tk_1_criteria_waited"]` and cause `m140`. CONFIRMED.
3. `park_criterion_relay(m141)` is True, and `_mode_key` for the Terminologist's wake gives `criterion_repair`. CONFIRMED.
4. `resolve_inbound` for the Terminologist carries `principal_verdict` `{"tk_1_criteria_waited": "approve"}` and `principal_test_verdict` `{"tst_waited": "contest"}`. CONFIRMED.
5. The Terminologist calls `msg.answer_tester`. PLAUSIBLE. This step is a model step. The door at `rota/roles/api.py:7276-7288` refuses a rewrite of the approved words and offers `msg.answer_tester(refs=['tk_1_criteria_waited'])`.
6. With an answer from the Terminologist to the Tester, `resolve_inbound` for the Tester carries `principal_test_verdict` `{"tst_waited": "contest"}` and `principal_said`. CONFIRMED with a hand-made answer row.

On path B, no Liaison wakes, so no step of this chain runs.

## Point 3: the counter

`_ruled_park` returns True, and the counter restarts. On the copy, `next_attempt('bg_1')` was 11 before the move. The chain was verdict, relay, then the Terminologist's answer. A Tester `tests` update of `tst_waited` through `session_commit` gave `next_attempt == 1`. `_ruled_park(bg_1, None)` is False. `_ruled_park` reads `park_ruling` and not the verdict's status. So it is True on path B too, but on path B no Tester move exists to trigger it.

## Point 4: other pages

- `land`, the ceiling. The callers are `pump` (`principal.py:3242`) and `apply_rulings` (`principal.py:4124`). The map also names `rota/testkit/scenes.py:1645`, but that call goes to the testkit's own `land` and not to this one. The new condition only narrows `settled = True`. It applies only when `park_ask_batch` names the page, so no other present changes. A shift page returns at `principal.py:3409-3410` before the ceiling, so a shift page does not change. On `pump`, `pending_asks` sets `order` (`principal.py:202`), so a contest of a check line keeps the verdict open. On `apply_rulings`, the order is empty, so nothing changes (High 1).
- `stage_park_relay`. The one caller is `run_session` (`rota/core/runner.py:6369`), after the model session. A trigger that is no verdict gives `rows is None`, so nothing changes. On a verdict from any page, the criterion of each contested test row now enters the relay to the Terminologist. On a non-park sign-off page, this widens the reach, as open question 1 of the pass report says. The reach agrees with route B. The relay of terms (no `split`) now loses the test criteria from its `body_refs`, as it already loses the contested criteria. On a shift page, the verdict rows are no tests, so nothing changes (PLAUSIBLE, by reading).

## Point 5: the tests

- The brief's command at `e9b522ca`: `150 passed, 1 skipped, 4 xfailed in 99.11s`.
- At the parent: I extracted `1a2d2014:rota` and `HEAD:tests` with `git archive` into `rv4/parent/`. Then I ran `tests/rota/test_park_page.py` there with `PYTHONPATH` set to that directory. Result: `2 failed, 33 passed`. The failures are the open verdict (`'answered' == 'open'`) and the relay (`[] == [...]`). This agrees with the pass report.
- None of the five new tests goes through `apply_rulings`. `_dry1_lands` passes `order=DRY1_ORDER` (`tests/rota/test_park_page.py:1191-1192`). This is why the suite does not show High 1.

## Point 6: recorded cases

No recorded case goes stale, by reading. The changed text is code and comments in `land` and `stage_park_relay`, and neither text reaches a prompt. `stage_park_relay` runs after the model session, so it changes no prompt of that session. The ceiling changes the status of a verdict only. Of the 27 files in `tests/rota/cases`, only `l1_liaison2.yaml` names `verdict_signoff`, and no case file names a `tst_` or `inh_` row. The gate did not run, as the brief says.

## Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/066a0dbd-4073-40a3-ae58-5d6d5157faf7/scratchpad/rv4/`. Each probe opens the dry1w9 copy with `mode=ro` and backs it up into `:memory:`.

- `p1_ceiling.py`: re-lands `r_m139` on paths A, B, B2, C, D and E, and prints the status of each verdict.
- `p2_relay_counter.py`: from path A, runs `stage_park_relay`, `park_criterion_relay`, `_mode_key`, `resolve_inbound` for the Terminologist and the Tester, `_ruled_park`, and a Tester `session_commit`. Then it prints `next_attempt`.
- `parent/`: `git archive` of `1a2d2014:rota` and `HEAD:tests`, with `pytest.ini`, `pyproject.toml` and `rota_serial_plugin.py`. I ran `test_park_page.py` there.
- One inline query listed the park rulings and their `reply_id` on the copy.

## Usage

Input tokens: about 80k. Output tokens: about 14k. Total: about 94k. These numbers are estimates, because the harness shows no exact count.

## Pass 4b

Commit `b5b7514c` in `C:/Users/roman/rota_f354r`. Verdict: **stands**. High 1 and low 1 are closed. No new finding is high or medium.

- Point 1, CONFIRMED. I ran `rv4/p1_ceiling.py` again. Through `apply_rulings`, `r_m139` lands `m140` as `open` (path B). With `ruling_id` and no order, `land` also gives `open` (path B2). The new probe `rv4/p3_allok_rulings.py` sets every line of `r_m139` to `approve` and lands it through `apply_rulings`. Then `m140` is `answered`. Paths A, C, D and E give the same results as before.
- Point 1, the order source, CONFIRMED by reading. The ceiling reads `ask.order or seen_order(conn, _reply_of(conn, ruling_id), ask)`, at `rota/roles/principal.py:3738-3739`. The read-back site at `principal.py:3473` makes the same call. `seen_order` is the one reader of the order (fact F28). The ceiling calls it only on a park page whose refs are all approved.
- Point 2, low 1 closed, PLAUSIBLE by reading. `tested` now comes from one `tests` query over `verdict_rows` (`rota/core/sandbox.py:5264-5267`), and nothing subtracts `rows`. A contested test row's criterion now enters `contested`, also when that criterion is a verdict row that is not a line of the page. The criteria relay branch uses the same list. On the dry1 path, `rv4/p2_relay_counter.py` still stages `m141` with `["tk_1_criteria_waited"]`. I did not build a fixture for a non-park page with an `about_ref` contest.
- Outside, low, PLAUSIBLE. A test row that an `about_ref` contest adds as a verdict row now sends its criterion to the relay, but it is no line of the page. The crit branch read the same rows before this pass, so the behaviour is not new. No action.
- Tests: `tests/rota/test_park_page.py` gives `36 passed in 4.69s`.
