# Night 106, the read

Night 106 ran from a worktree at bf74640, launched 2026-10-02 10:40 cold, ended 13:40 with bg_1 parked past the attempt cap and bg_2 given up. NIGHTCOUNT: 259 sessions, 1231 turns; made up 108 turns in 47 sessions, developer 22; ran anyway 2 writes after an invention, 10 with a landed commit; dangling pointers 101 turns, 18 sessions; repeats 1 wake, 2 sessions. Read on Opus from `.rota/night106_report.txt` (195 lines) with 8 queries on `.rota/clickI_night106.db`, 94.6k on the harness line (observed: 2026-10-02 13:50). Rota workflow unless marked.

## 1. Frame 109, the challenge parses

No turn holds `ERROR TOOL: msg.challenge_tester`. Nine challenges landed, `developer->tester challenge 9` in the print. Every `quotes` was a list of two, except three-item lists in `s202` and `s203`. Every refusal came from a content rule: "you have already sent challenge to tester", "names no test", "on exactly these refs already (m109) and they answered", "inh_022b8a87 has no criterion". Night 105 had zero landed and twelve parser refusals.

| Session, wake | Landed | Refused |
|---|---|---|
| `s141` bg_1 attempt 2 | m64 | none |
| `s143` attempt 3 | m65 | 3x already sent |
| `s145` attempt 3 | m66 | 2x names no test, 2x already sent |
| `s147` attempt 5 | m67 | one call cut mid-quote |
| `s152` attempt 8 | m70 | none |
| `s154` attempt 9 | m71 | 1x already sent |
| `s156` attempt 10 of 10 | m72 | 3x already sent |
| `s209` bg_2 attempt 3 | m109 | 2x already sent |
| `s212` attempt 4 | m112 | 2x already answered |
| `s218` to `s228` attempts 4 to 8 | none | all "on exactly these refs already" |

Repeated wakes on an unchanged tree: `s143`/`s145` on bg_1; `s201`/`s202`, `s203`/`s204`/`s205`, `s223`/`s224`, `s226`/`s227`/`s228` on bg_2. The print's repeat line counts one pair. The attempt-8 CYCLE was a true repeat at head 9c7f3b7b, three sessions, no commit.

## 2. What the Tester did with each challenge

| Challenge | Tester | Act | Result |
|---|---|---|---|
| m64 | `s142` | 5 encodes refused | nothing |
| m65 | `s144` | reply cut | nothing |
| m66 | `s146` | encode `inh_echo_json_01` | v2 |
| m67 | `s148` | encode `_03` | v2 |
| m70 | `s153` | encode `_03` | v3 |
| m71 | `s155` | encode `_03` | v4 |
| m72 | `s157` | encode `_01` | v3 |
| m109 | `s210` | 4 refused, new test `tst_cr1_accepts_arg`, answer m110 | defended |
| m112 | `s214` | answer m114 | defended |

`inh_echo_json_02` never changed and still invokes the plain function. `_01` and `_03` were rewrapped in `@command() def cli(obj)` and pass a dict or `BadObj()` as a CLI argument, so they stay broken. At 54161df5 to 3202eb7e only `_02` failed; from af4cbede on all three fail, after the rewrites. bg_1 ends at 861061a0 failing all three. bg_2 ends at 9c7f3b7b failing `inh_022b8a87`, `inh_51d478df` and `tst_cr1_default_arg`.

## 3. The two stalls

bg_1: the ladder ran to attempt 10 of 10 in `s156`, then `do:park: deferred bg_1; its ladder is spent`. Commits: `s131` 33d71e5e, 54161df5; `s141` 1cc25a5d; `s145` 5da5a9cd, bfcc9218; `s147` 3202eb7e; `s151` af4cbede; `s159` a8ccaf0d on "echo_json already meets criteria"; `s167` 861061a0.

bg_2: `tests_failing|bg_2 attempts=3 quarantined=1`. Its original failures are inherited project tests, `inh_022b8a87` and `inh_51d478df`, which a challenge cannot reach, "has no criterion". Commits: `s200` cfd2281d; `s202` ac2028da; `s218` 683e5bbc; `s220` 35ed9e90; `s221` b11c4b3c, 1e36bddd; `s224` 90254d2e, 4ec2b052, 9c7f3b7b.

## 4. Made up, developer 22

A Developer completion that holds its own `OK` or `ERROR` result line. Tools: `code.source` 166 lines in 16 sessions; `code.write` 35 in 9; `msg.challenge_tester` 13 in 2; `msg.escalate_architect` 12 in 2; `code.commit` 11 in 6; `code.diff` 8 and `tests.load` 4 in `s227`. Mode: tests_failing 17, batch_start 3, message 2. The five "ran anyway" shas are `s141` 1cc25a5d, `s151` af4cbede, `s200` cfd2281d, `s224` 90254d2e and 4ec2b052, each in a session that also invented a `code.commit` line.

## 5. Dangling pointers

The print does not define the term, and no turn holds the word. Unanswered from the print.

## 6. Other facts

The Tester's rewrites raised bg_1 from one failure to three. The "already sent on exactly these refs" refusal fired 20 or more times, and the Developers looped on it instead of escalating. Walk 3 ran bg_3's grouping, annotation and approval only, 0 commits. `s156` at attempt 10 of 10 still sent a challenge.

## Correction, 2026-10-02 14:35

Section 2 says only `_02` failed before af4cbede. A re-encode deletes the test's earlier runs (`rota/core/db.py:576-580`), so the runs table no longer holds the early failures of `_01` and `_03`; at m66 the wake showed `_01` red with `AttributeError`. All three failed from the start. Also, no challenge named `_02`: the Developer challenged `_03` five times and `_01` twice (observed: frame 110's scope read of the `messages` table, 2026-10-02).
