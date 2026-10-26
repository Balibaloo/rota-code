# Frame 330, the agency read: a quarantined key of a running batch

Date: 2026-10-26. Read at 46e5c88b on `rota/foundation`, read only, no pytest.
Night registers read from backup copies in the scratchpad of session 8db3a3f9,
folder `a330`. Meta workflow.

## 1. The purpose

The mechanism is the check `stopped_bouncing` in `rota/core/scheduler.py`
(1722 to 1739), read by `exhausted` (`predicates.py` 1064) and by `parked`
(`scheduler.py` 2298), which `preempt` reads for `do:park` (`predicates.py` 1638).
It closed night 168's wall W5: `batch_1` held the one batch seat with its
`tests_failing` key quarantined at attempt 6 of 10, and `batch_2` never started
(observed: `plans/frame330-provenance.md`, section 3). The build decision is
the session's, not a ruling: the provenance found "a gap, not a departure" and
no ruling of Roman's on a quarantined running batch (observed: the provenance,
section 5). It landed at ec33c1f7 (18:42), 24fd4638 (18:52) and 3bb5be4b
(19:15), all 2026-10-26, and it carries law 6 of 2026-09-13, "Budget exhaustion
escalates one rung" and "It is never silence" (observed: `rota/LAWS.md` 185 to 191).

## 2. What exists

| Record or reader | Where | What it holds |
|---|---|---|
| `given_up` | `scheduler.py` 1712 | Every quarantined seat key that names one batch, any kind |
| `parked`, deferred branch | `scheduler.py` 2296 | Parks a deferred batch on any `given_up` key (ruled: Roman, 2026-09-27) |
| `park_owns`, `park_ask` | `scheduler.py` 1832; `predicates.py` 1794 to 1835 | The page or note to him for a given-up batch, by `given_up` |
| `quarantined` | `predicates.py` 1705 to 1791 | One Liaison note per key; 1760 says "a running batch has no park" |
| `findings_exhausted` | `predicates.py` 1076 to 1121 | A second ladder door, for the findings loop at `loop_cap` (frame 88) |
| `_next_rung` | `predicates.py` 1124 to 1145 | The rung asked, from committed sessions only |
| `_stalled_keys`, `_stalled_words`, `_stuck_ticks` | `rota/roles/principal.py` 1331, 1343, 1350 | Quarantined keys of a batch and their words to him (frame 312) |
| `TICK_WORDS` | `principal.py` 1371 | Words for review, tests_failing, tests_missing, verdict_failed, batch_start, touch_strayed |
| The "Stuck" seat line | `principal.py` 440 to 449 | For tipsH, 2026-09-09: the Critic quarantined and the batch stayed running |
| `i6` invariant | `rota/tools/invariants.py` 195 | Quarantined keys that name a gone batch |
| New in this frame | `scheduler.py` 1742, 1754 | `_quarantined_tries` reads one key kind; `stop_detail` writes "the tests still fail after N tries" |

(observed: the lines named.) `_quarantined_tries` re-derives a narrow copy of
`given_up`, and `stop_detail` re-derives the `TICK_WORDS` entry "the tests still
fail" (reasoned: the same table rows, one kind instead of all, and the same words).

## 3. The reach

The cause by the code: the rules that free the seat read a loop count against
`loop_cap` only, and a seat key of a running batch quarantined at
`tick_attempt_cap` 3 is read by no seat rule, only by one Liaison note
(observed: `exhausted` 1046 to 1055, `parked` 2298 to 2309, `quarantined` 1760).
`given_up` holds the key for any kind, and only the deferred branch reads it
(observed: `scheduler.py` 2296). Instances, each a seat wake with one batch ref
on a running batch, whose quarantine leaves the batch on the seat:

1. `tests_failing`, `predicates.py` 981. Covered by the fix.
2. `verdict_failed`, `predicates.py` 1491. A Developer that commits nothing three times.
3. `finding_violated`, `predicates.py` 1535. `findings_exhausted` reads upheld rounds only, 1112.
4. `touch_mistaken`, `predicates.py` 2411.
5. `review`, `predicates.py` 1405. Observed on tipsH (`principal.py` 440), night 160 (frame 312, `tests/rota/test_frame312_stuck_review.py` 1 to 9), night 165 end state.
6. `structural_review`, `predicates.py` 1470.
7. `touch_strayed`, `predicates.py` 2389. Observed in night 145's end state on running `bg_4`.
8. `tests_missing`, `predicates.py` 845.
9. `batch_start` on a running batch with no commit, `scheduler.py` 542.
10. A ladder rung's own key, `<role>|tick:exhausted|<batch>`: `_next_rung` (1124) counts committed sessions only, so a quarantined rung is never asked, and `preempt` (1638) never parks.

(observed: each line; reasoned: each key keeps its count while the batch lives,
`scheduler.py` 2537 to 2541, and only a head commit lifts it, `db.py` 606 to 620.)
**Count: 10 instances.** Two readers bound any fix: `exhausted` iterates batches
with a failing test only (1046 to 1055), and `parked` parks only with a failing
run at head (2303 to 2309), so a green batch with keys 2 to 7 can neither climb
nor park (observed). Two fixtures encode the old answer for a running batch:
`tests/rota/test_park_page.py` 696 and `test_frame312_stuck_review.py`
(observed). Pair keys, `finding_review` and `reopen`, are out of `given_up` by
its rule (observed: 1714) and out of this count (assumed).

The end states show the tests_failing shape on 12 of the 49 night files from 120 to 169: nights
120, 122 to 125, 138, 142, 145, 151, 153, 164 and 168, each below 10, none with a
rung, and with pending batches on 122 to 125 and 168 (observed: `tick_attempts`,
`batches`, `test_runs`, `sessions`). The provenance counted 0 over nights 160 to
167 and named night 164 a near case. Its claim that frame 318 of 2026-10-24 made
the shape reachable does not hold: nights 122 to 125 date from 2026-10-05
(observed: file dates; reasoned: frame 83 alone suffices).

## 4. The fix against the reach

The built fix covers 1 of 10 (observed: the diff 1897a238..3bb5be4b,
`_quarantined_tries` matches `developer|tick:tests_failing|<batch>` only). It
leaves instances 2 to 10. It also adds a second words table beside `TICK_WORDS`.
It cost 4 passes, 148k, and 3 scenes that each encoded the old quiet
(observed: frame 330's status lines 18:32 to 19:15).

## 5. My proposal

Not the same fix. The smallest place is the one check, widened to the existing record:

1. `stopped_bouncing` reads `given_up(conn, batch_id)` for a running batch, not `_quarantined_tries` (`scheduler.py` 1712, 1739).
2. `exhausted` iterates running batches where `stopped_bouncing` holds, not only batches with a failing test (`predicates.py` 1046 to 1055); `findings_exhausted` keeps its own cap (1112).
3. `parked` accepts a `given_up` key without a failing run at head, as its deferred branch does (`scheduler.py` 2296, 2303).
4. `_next_rung` counts a role whose `tick:exhausted` key is quarantined as asked (`predicates.py` 1139 to 1145).
5. `stop_detail` takes its words from `principal._stalled_words` over `given_up`, and the second table goes (`principal.py` 1343, 1371).

Price: 1 implementer pass cold on Opus, about 75k; 1 review, about 70k; 1
resumed fix, about 24k; 1 gate, about 6k in the session. About 175k of agent
tokens and 4 cycles, about 40k of session context, or 12k at a file report each
(observed: `plans/operating-facts.md` 241 to 247 anchors; reasoned: the
scenes that seat the rungs exist now, so the pass changes no scene script).

## 6. The doubt

- A Developer rung woken on a green batch with a stuck review can read a brief that says the tests are red. Frame 88 gave the findings loop its own kind for that (observed: `predicates.py` 1113 to 1116). I did not read the rung briefs.
- I did not run the widened check against nights 145, 160 and 165, so the claim that it frees those seats is reasoned only.
- The end-state count misses walks that recovered. A key lifted later inside a night is not counted.

## Verdict

**at one door of 10**: the fix covers 1 of 10 instances, `tests_failing`. The
rest are `verdict_failed`, `finding_violated`, `touch_mistaken`, `review`,
`structural_review`, `touch_strayed`, `tests_missing`, `batch_start` on a
running batch, and a quarantined ladder rung (reasoned: sections 3 and 4).
