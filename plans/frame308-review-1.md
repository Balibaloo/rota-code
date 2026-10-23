# Frame 308, review 1: pass 1 at d83173ef

Verdict: accept for the night, with one medium fix before or beside it. The door refuses s220's turn 1 on the real night 158 rows, and it refuses 4 first answers in 75 ruling relays. Three of the four are true misses. One is a plausible false refusal. The medium finding is a refusal that offers a dangling ref.

Reviewer on Opus, read-only. Worktree `C:/Users/roman/rota_r308` at d83173ef, parent 9d4274b4. The probes are in session 2214bec6's scratchpad, folder `r308`, files `p1.py`, `p2.py` and `p2b.py`. Each probe ran on a copy of `clickI_night158.db`, or read the night databases with `?mode=ro`.

## Findings

| # | Finding | Status | Severity | Fix |
|---|---|---|---|---|
| F1 | The refusal offers a dangling ref as part of the route | CONFIRMED | medium | Build `full` from the given refs that `api.ref_resolves` admits, then add the missing ones. |
| F2 | s362 of night 157: a `revise` ruling that faults the code, not the check, is refused | PLAUSIBLE | low | Require a ruled criterion only when his words for its line fault the check or the words. |
| F3 | The closed text "your work here is done" can stop the seat before another ruled rewrite | PLAUSIBLE | low | Write "your work on {id} is done". |
| F4 | An approved criterion with a ruled test is outside the door, and the brief keeps a per-criterion send for it | PLAUSIBLE | low | Add such criteria to `ruled`, and say "in the same one answer" in the test paragraph. |
| F5 | The read's count script is not on disk | CONFIRMED | low | Store the count script of a read beside the read, under its own name. |
| F6 | The changed brief lines are not rewrapped, and "no test of it" now has a plural referent | CONFIRMED | low | Rewrap the paragraph, and write "no test of them yet". |

## 1. The red test

The door refuses s220's turn 1 through the real send path (CONFIRMED: `p1.py`). The probe built the Terminologist in mode `criterion_repair` on a copy of night 158, with trigger m101. It called `msg.answer_tester(refs=['cr_3_confirm_default_on_eof'])`, the call of `tool_calls` seq 11. The text:

> Your answer leaves out cr_2_confirm_default_on_eof. The principal's ruling in the relay names cr_2_confirm_default_on_eof too. Send one msg.answer_tester with every ruled criterion in refs: ['cr_3_confirm_default_on_eof', 'cr_2_confirm_default_on_eof']

The three sentences have 5, 9 and 11 words. Sentence 1 holds the fact. Sentence 2 holds the reason. Sentence 3 holds the one step and the route, with the exact refs. No answer was staged. The same call with both refs then landed as m150 (CONFIRMED: `p1.py`, point 4 probe).

## 2. Right answers refused

The door refuses 4 first answers. Three were true misses, and one is a plausible false refusal (CONFIRMED: `p2.py` and `p2b.py`).

Method: every Terminologist session of nights 140 to 158 whose trigger is a relay of a principal verdict, with two or more relay refs that are criteria marked `contest` or `revise`. That gives 75 sessions. The read says 72 relays. 20 of the 75 drew the second-answer refusal, and the read says 20. The probe ran `sandbox._ruling_answer_refusal` on each session's first `msg.answer_tester` refs, with an empty outbox and the end-of-night rows. The door spoke on 4, the same 4 that the read names. It spoke on no session outside the 20.

| Night, session | Omitted | His words for it | Earlier answer of the same relay | Reading |
|---|---|---|---|---|
| 142 s431 | cr_1 | "Line 2's check still crashes", a check fault | None. s431 is the one session on m300 | True miss |
| 157 s191 | cr_3 | "replace the color setting wording with ..." | None. s191 is the one session on m85 | True miss. s191 sent cr_3 in a second answer, and the door of 2026-08-14 refused it |
| 157 s362 | crit_show_python_version (`revise`) | "Line 5: keep it as written, but fix the code ..." | None | Plausible false refusal (F2) |
| 158 s220 | cr_2 | "Keep line 4, but fix its check" | None | True miss |

No omitted criterion was dropped by the ruling itself. No omitted criterion was answered in an earlier session of the same relay.

F2: the ruling of s362 keeps line 5's words and faults the code. The Tester's test of line 5 needs no change, so the Tester needs no answer on it. The door forces the ref into the answer. The cost is one Tester wake on a right test. The seat itself sent both refs in its last answer, so the seat read the case the same way as the door. The case occurs once in 75.

The pass report's doubt names a `revise` criterion whose words still wait for a commit. That case does not occur on the record. No relay of the 75 has one ruled criterion with a built batch and another without one (observed: end-of-night rows, so the count is approximate). The doubt does occur in a different form, F2.

## 3. The order of guards

The seat gets the door's refusal first, and that refusal offers a call that the dangling-refs guard refuses (CONFIRMED: `p1.py`, point 3 probe). This is F1.

Probe: `refs=['cr_3_confirm_default_on_eof', 'cr_9_nothing']`. The door refused, and its route reads `refs: ['cr_3_confirm_default_on_eof', 'cr_9_nothing', 'cr_2_confirm_default_on_eof']`. The same refs with cr_2 added then met the dangling guard: "'cr_9_nothing' names no row". So the seat spends two turns, and the first refusal names a call the doors refuse. That breaks frame 135's rule.

The other shape guards are in the right order:

- A bare string passes the door and meets the string guard of `stage`.
- No refs meets the argument check first.
- A list of one-element lists counts as no given refs. The door then offers the ruled set alone, which is a call the doors admit.

The order is right once `full` holds only refs that resolve. The fix is in F1.

## 4. The closed route

A seat that reads the closed texts knows what to do, and the route "rewrite the text" is real (CONFIRMED: `p1.py`, point 4 probe; reasoned: `criteria_respecify`).

After the full answer landed, the cr_2 respecify got:

> the principal faulted the check and not these words: '...'. The criterion stands. Your answer to the Tester carries this criterion. If his words also contradict this criterion's text, rewrite the text. If not, your work here is done

The branch fires only when the new text equals the current text. A rewrite with other words does not reach the branch, so "rewrite the text" names a call the doors admit. The text names no refused call.

Other calls in the mode at that point:

- `ledger.log` on cr_2 is refused: "the principal ruled on cr_2_confirm_default_on_eof ... Adopt what they approved, and stop."
- A second `msg.answer_tester` is refused by the door of 2026-08-14.
- `msg.answer_developer` and `msg.challenge_vision_keeper` are in the mode's tools. Neither one carries a check fix to the Tester. So the text leaves out no route that would help.

F3: "your work here is done" is said about one criterion. Another ruled criterion can still wait for its rewrite, for example cr_3 when the seat answered first. The answer commits with the session, so a later rewrite still reaches the Tester. The text tells the seat to stop before that rewrite.

F4, the closed and not carried variant: when the answer left a criterion out, the text says the answer "is closed in this session". The criterion then has no route, which is the s220 loss. The first-answer door prevents that under a relay. Two wakes stay open:

- A wake that is not a relay, which is the shape of test 7.
- A relay with an approved criterion whose test the verdict marks `contest`. `ruled` holds only criteria marked `contest` or `revise`, so the door does not ask for that criterion.

No relay of nights 140 to 158 has the mixed shape (observed: 0 relays).

## 5. The brief sentence

The new sentence has 17 words: "When the change has a commit, send one `msg.answer_tester` with every contested or revised criterion in `refs`." (CONFIRMED: read).

- "For each criterion with contest or revise, rewrite it with `criteria.respecify`" stays. That sentence is about the rewrite, so it does not contradict the new one.
- The paragraph "A ruling on a test" still says "Send `msg.answer_tester` with the criterion in `refs`". On a relay that also holds a contested criterion, that sentence reads as a second send. That is F4.
- The pass dropped the reason "so the Tester encodes the new words".
- The next sentence says "the Tester has no test of it yet", and "it" now has a plural referent.
- Lines 27 and 28 are not rewrapped, and line 28 is about 130 characters. That is F6.

Stale count: 2 L1 cases compose this brief (PLAUSIBLE: read of the case files):

- `L1-TE-a-ruled-criterion-is-respecified-and-the-tester-told`
- `L1-TE-repair-the-criterion-the-tester-cannot-encode`

An L3 chain whose Terminologist leg wakes in `criterion_repair` also goes stale. I did not count those chains. I started `rota.tools.casestatus` on both trees, which is a read-only report and not a gate. A run took more than 10 minutes, so I stopped both runs on the coordinator's word. The number is not measured.

## 6. Nothing else changed

The change is 4 files: `rota/core/sandbox.py`, `rota/roles/api.py`, `criterion_repair.md` and the new test file. The diff is 316 insertions and 3 deletions (CONFIRMED: `git diff 9d4274b4 d83173ef --stat`).

`_bind_send` (81527 bytes) and `_sent_this_session` (444 bytes) are byte for byte the same at both commits (CONFIRMED: an `ast` extraction from `git show` of each commit). `git diff 9d4274b4 HEAD -- rota tests` on `D:/repos/rota` is empty, so the main tree runs the parent's code.

One side effect, now removed: my first `casestatus` run in the worktree made an empty, ignored `tests/rota/cassettes.db`. I deleted it. `git status --ignored` now shows only `__pycache__`.

## 7. The count script (F5)

`f304_count.py` in the scratchpad is the script of frame 304's question 6, which counts arrange-step reds. It is not the count of the s220 read. A later write took its name. My recount in `p2.py` gives the read's 20 and 4, and 75 sessions where the read says 72 relays.
