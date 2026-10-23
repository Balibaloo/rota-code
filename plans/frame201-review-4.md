# Frame 201, review 4: pass 3 at a11545ed, the hold on a Critic's first pass

Verdict: accept a11545ed for the register run. The code does what the
commit says, and the change is the seven files only. The measured 3 of 3
of probe (c) does not transfer to the shipped hold. On the recorded case,
the lines door refuses the first pass twice, and the hold first fires on
turn 3. So the register run is the first measurement of the shipped shape,
and the run must include `L1-CR-fail-names-its-criterion`.

Reviewer on Opus, read-only. Worktree `C:/Users/roman/rota_r201b` at
a11545ed, parent 404dcb68. Probes ran through `rota.core.sandbox.build` on
temporary databases. No gate, no re-record and no model call ran.

## Findings

| # | finding | status | severity |
|---|---|---|---|
| 1 | The recorded case meets the hold on turn 3, after two lines refusals, not on turn 1 | CONFIRMED | high |
| 2 | The hold reaches the seat as an `ERROR` line in the results block, after two `ERROR` lines on the same call | CONFIRMED | medium |
| 3 | The shipped words differ from probe (c) in seven places, and two of them invite "send the same call again" | CONFIRMED | medium |
| 4 | After the hold, a pass that names a different line lands with no question on that line | CONFIRMED | medium |
| 5 | The doubtful-criterion case can turn a right pass into a wrong fail | PLAUSIBLE | medium |
| 6 | The fail route works, but the challenge route is closed once turn 1 claimed True | CONFIRMED | low |
| 7 | The hold fires again in every new session that has no landed verdict, the answer mode included | CONFIRMED | low |
| 8 | The test repairs hide the hold from no pass-path test, and one flag is redundant | CONFIRMED | low |

### 1. The recorded case meets the hold on turn 3 (high, CONFIRMED)

The case's turn 1 claims `encodes=True` and sends a pass whose `lines=`
value holds three lines. The lines door of pass 2 refuses that value
before the hold runs. Probe P1 shows the `LinesRefusal` "the value for c1
holds 3 lines, and a pass names one added line per criterion". The
recorded prompt of the case's turn 4 shows the same history. Turns 1 and 2
are refused, turn 2 gets the `NOTE` of two refusals, and turn 3 lands
`lines={"c_c2e7a4": "    delete(\"invoices\", account_id)"}`.

With a11545ed, turn 3's pass is the first pass that the door admits, so
the hold fires there. Probe (c) put its reply after turn 1, on a history
with no refusal. The seat that meets the shipped hold has read two
refusals that each said "send the pass again". The 3 of 3 is therefore a
measurement of a different prompt.

Fix: probe the shipped reply on the case's turn 3 prompt, three ids, before
the register run, or read that case first in the run.

### 2. The error line (medium, CONFIRMED by reading)

`rota/core/runner.py:5039` renders every exception of a call as
`ERROR {tag}: {exc}`. The tag is `verdicts.emit` on a turn with one call,
and `verdicts.emit(batch_id='b_…')` on a turn with two. The runner joins
the transcript into one user message (`runner.py:4303`). So the seat reads
the hold as one more refusal of its call, directly below its own reply.

Probe (c) sent `OK verdicts.claim_encodes` and a line that starts
`HELD verdicts.emit(result='pass'):`, as a new chat turn after an assistant
turn. The shipped shape changes both the word and the turn structure. A
weak model can read `ERROR` as "the call was wrong", and the hold does not
say that the call was right in form.

The hold is a `ValueError`, not a `LinesRefusal`. So it does not enter
`refused_pass`, and it adds no `NOTE`. It does enter `outcome.errors`,
which the scenes allow through `PASS_HELD`.

Fix: raise a `PassHeld(ValueError)` and print `HELD {tag}:` for it at
`runner.py:5039`, three lines, which restores the measured prefix.

### 3. The words against probe (c) (medium, CONFIRMED)

The shipped reply for turn 3 of the case, as the seat reads it:

```
ERROR verdicts.emit: your first pass of this session is held, and it has not landed. Criterion c_c2e7a4: "deleting an account tombstones it and keeps its invoices". Your line for c_c2e7a4: `delete("invoices", account_id)`. Does that line do what the criterion says, or the opposite? Then send verdicts.emit again with the verdict you now hold. If each line does what its criterion says, send the same pass again. If a line does the opposite, send a fail on its criterion. Call `verdicts.claim_encodes('<criterion id>', encodes=...)` first, as for any fail.
```

Probe (c)'s reply, from `ctl.py` of session 81fe1025:

```
OK verdicts.claim_encodes
HELD verdicts.emit(result='pass'): before the pass lands, answer for c_c2e7a4. The criterion says: "deleting an account tombstones it and keeps its invoices". Your line holds 'delete("invoices", account_id)'. Does that line do what the criterion says, or the opposite? Say which in one sentence. Then send the pass again if it does what the criterion says, or claim and fail on c_c2e7a4 if it does the opposite.
```

The differences:

1. The prefix. `HELD …: before the pass lands, answer for c` against
   `ERROR …: your first pass of this session is held, and it has not
   landed`. The shipped words say what the runner did, not what the seat
   must answer.
2. The place. Probe (c) followed turn 1. The shipped hold follows two
   refusals (finding 1).
3. The criterion. "The criterion says: "…"" against "Criterion c_x: "…"".
4. The line. Probe (c) quoted one line that the runner chose, in single
   quotes. The shipped reply quotes the seat's own value in backticks. On
   turn 3 the line is the same line.
5. The question. The words are the same for one line. "Say which in one
   sentence." is missing. That sentence made the seat write its answer
   before it wrote a call.
6. The routes. Probe (c) gave one sentence, the pass route first and the
   fail route with the id. The shipped reply gives four sentences. It
   names "send verdicts.emit again" and "send the same pass again" before
   the fail, and the fail route has no id.
7. The claim. Probe (c) said "claim and fail on c_x". The shipped reply
   names `'<criterion id>'` and `encodes=...`, with no value.

Differences 1, 2 and 7 can read as "you did wrong". Differences 2 and 6 can
read as "send the same call again". The two earlier refusals said "send
the pass again", and the hold's first route says "send the same pass
again".

Fix: ship probe (c)'s text with the seat's own line, its `HELD` prefix and
"Say which in one sentence", and name the id in the fail route.

### 4. A changed line lands unasked (medium, CONFIRMED)

Probe P4d: the first pass names `delete("invoices", account_id)` and is
held. The second pass names `delete("billing_accounts", account_id)` and
lands. Nothing asks about the new line. On the recorded case, that second
pass is a wrong pass. The hold then teaches the seat to move to a line it
can defend, not to read the line it named.

Fix: hold once more when the second pass names a line for a criterion
that the first pass did not name, and quote the new line.

### 5. The right passes (medium, PLAUSIBLE)

`L1-CR-pass-a-conforming-diff`: the latest five runs claim True and pass
with `if days_used > days_in_period:` and its `raise` line. The case has
4527 passed runs of 4538. In run 1, turn 2 sent the same pass again with
no prompt to do so, and got "already landed". The hold's reply asks "Do
those lines do what the criterion says, or the opposite?" about a guard
that refuses. The risk of a wrong fail is low here. The cost is one turn.

`L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist`: the
latest runs pass with `delete("invoices", account_id)`. That line sits
under the comment "Closing does not delete: the invoices have to survive
for seven years". The criterion says "deletes its invoices". The hold
asks about that one line, and the comment is in view. A seat that took
the comment as the rule can answer "the opposite" and fail. The hold's
reply names no route to the Terminologist question, which is the case's
expected second act. The case already fails 2316 of 2318 runs on that
message, so only its verdict count still guards anything. In run 1,
turn 2 also sent claim True and the same pass again unprompted.

To land the same verdict, each seat must send the same pass again in
turn 2. Both seats did that in the recordings, so the risk sits in the
changed turn-2 prompt, not in the habit.

Fix: read the two cases' turn 2 in the register run, and count a fail on
the doubtful case as a regression of the hold.

### 6. The fail route (low, CONFIRMED)

Probes on the case's batch, after the hold:

- P3a. Turn 1 claimed True. `emit(fail)` alone lands.
- P3c. No claim in turn 1. `claim_encodes(True)` and `emit(fail)` in one
  turn land.
- P3b. No claim in turn 1. `emit(fail)` alone is refused with "a fail on
  c1 stands on its test actually encoding it".
- P3e. Turn 1 claimed True. `claim_encodes(False)` is refused with "you
  already claimed c1's test encodes it this session", so the challenge
  route is closed.

The recorded case claims True in turn 1. So its expected fail lands by
the route the reply names, and also without the claim. The challenge to
the Tester, the other right answer, cannot follow the hold.

Fix: say "If you have not claimed c_x True this session, claim it first",
with the id.

### 7. Once a session (low, CONFIRMED)

`pass_held` is a field of `Ctx` (`api.py:156`). The runner builds one
sandbox per session (`runner.py:4041`). Probes:

- P4a. Two criteria: the first pass is held and quotes both, in order. The
  second pass lands.
- P4b. A fail at the first emit lands, and `pass_held` stays False.
- P4c. A pass with no `lines=`, with `{}` or with text gets the lines
  door's `LinesRefusal`, not the hold. `pass_held` stays False.
- P4e. A new sandbox on the same batch, after a hold with no landing,
  holds again.
- P4f. A Critic in the `answer` mode is held too.

So a seat that restarts from records meets the hold again in each session
until a verdict lands. `L1-CR-finish-the-review-with-the-answer-in-hand`
meets it on its answer wake.

Fix: none for the register run. Record in the docstring that the hold is
once a session, not once a batch.

### 8. The test repairs (low, CONFIRMED by reading)

- `test_verdict_lines.py`: the new `_land` expects the hold on the first
  emit, then sends the same emit. The hold stays visible to every
  pass-path test, and each one asserts the hold's words.
- `test_delivery.py::test_the_judgement_records_what_it_judged` sets
  `pass_held = True`. The test checks the stored commit, not the pass path.
- `test_desk_guards.py::test_a_second_verdict_on_one_commit_is_refused`
  sets the flag on two sandboxes. The test checks the second verdict. The
  flag on the second sandbox is redundant, because the "already landed"
  check runs before the hold.
- `scenes.py` `judge` and the two scripted Critics of `test_arc_seam.py`
  send the same pass again. That is the first route the reply names.
- No scripted seat takes the fail route after a hold. The new file covers
  that route at the door only.

Fix: remove the redundant flag. A scene that fails after a hold is
optional.

## Nothing else changed (CONFIRMED)

`git diff 404dcb68 a11545ed --stat` lists the seven files and 286
insertions and 21 deletions. The `api.py` diff holds three parts only:
the `pass_held` field of `Ctx`, the call in `verdicts_emit` after
`_pass_lines_check`, and `_first_pass_hold` with its two question
constants.
