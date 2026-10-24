# Night 163, W6: why item 2 stopped quietly

## 0. The cause

**`session_commit` marks a fresh principal message `answered` when its
Liaison session lands nothing, because frame 267's retry covers only a
reply to a page.** That is cause 6: the rule reads "the session committed"
as "the message was answered", and no rule, invariant or walk test then
sees the open request (reasoned: section 2). The four refusals that made
s145 barren are cause 9: the paste door's text sends the seat back to a
clarify and never names `brief.segment` (reasoned: section 1, step 4).

## 1. The trail

1. The walk seeds entry e_p2 and message m_p2: principal to liaison,
   `converse`, refs `["e_p2"]`, `cause_id` NULL, seq 44 (observed).
2. s145, Liaison on qwen3:8b, wakes on m_p2 with `current_request` s1.
3. Turns 1 to 4 each send `msg.clarify_principal(refs=["e_p2"])`. Turn 1
   pastes his whole sentence and adds "Is this still the correct
   approach?". Turns 2 to 4 send one rephrase that keeps a run of his
   words. `tool_calls` holds 3 clarify rows, seq 3 to 5, because the repeat
   door stops turn 4 (observed: `turns`, `tool_calls`, turn 5 "repeated
   its previous turn verbatim twice; ended").
4. Each refusal ends "Ask the one thing you do not know, in your words"
   (observed: `rota/core/sandbox.py` 3229 to 3243, a9e0bd1f, 2026-09-13).
   The text points at a better clarify. It never says that a request is
   work for `brief.segment` (reasoned).
5. The route existed. `converse.tools` holds `brief.intake`,
   `brief.segment` and `msg.confirm_principal`, and `converse.md` line 2
   says `brief.intake(verdict='work')` "if the message asks for anything
   at all" (observed: `rota/roles/prompts/liaison/`). The seat called none
   of them. Its turn-1 question copies the example at `converse.md` line
   111, "Is that still right?", a clarify on a ratified statement
   (reasoned: the wording).
6. s145 commits with nothing. m_p2 ends `answered`, attempts 1, with no
   statement on e_p2 and no message caused by it (observed).
7. The walk then prints "quiet after 1 steps" (reasoned: section 2).

## 2. The dispatch and the quiet test

**The dispatch.** `open_tips` in `rota/core/scheduler.py`, about line 84,
wakes a role on a `status = 'open'` message (observed). The session's end
is `session_commit`, `rota/core/db.py` 931. Its trigger branches, lines
1062 to 1131 (observed):

| Line | Fires when | m_p2 |
|---|---|---|
| 1074 unresolved | verb in `OWED_A_REPLY` (challenge, propose, escalate), line 743 | no |
| 1089 | verb is `challenge` and the session is barren | no |
| 1102 | `_page_under_reply` gives a returned page | no page |
| 1110 retry | `_page_under_reply` gives a page and attempts < 2 | no page |
| **1118 answered** | the rest, unless barren and already unresolved | **yes** |

`_page_under_reply`, `db.py` 775 to 803, returns None unless the trigger
has a `cause_id`, line 789 (observed). A fresh request has none, so it
falls to line 1118, and lines 1119 to 1122 write `answered` (observed).
Nothing records the miss: no `unresolved_note`, no page note. The
refusals live only in `turns` (observed: the m_p2 row).

**The provenance.** "The trigger message is answered once its session
commits" dates from b519a246, 2026-08-10, or before (observed: `git log
-S`). Line 1118's guard is b85650e9, 2026-09-13, the challenge case. The
retry is 0582873a, 2026-10-16, frame 267, for night 151's m178, a reply to
a page: "A converse session on a page reply that stages no rulings row ...
leaves the reply open" (observed: the commit body). Its `cause_id` guard
at line 789 scoped the fix to page replies (observed: blame). A fresh
request has the same shape, and the frame did not name it (reasoned).

**The invariant is blind too.** I9 skips every verb in `CARRIES`, and
`converse` is in it (observed: `rota/tools/invariants.py` 48, 221).

**The quiet test.** `probes/walk.py` 243 to 316 (observed). A step answers
`pending_asks`, open messages to the principal, then `pending_replies`, a
Liaison line with no page. Then `step()` runs, and when it returns no
wake, line 305 prints "quiet after {i} steps" and records `stuck`. Each
of these reads an open message or a tick predicate. m_p2 is `answered`,
and no predicate reads "a principal entry that no statement spans and no
message answers". So the walk reads quiet one step after s145 (reasoned).

## 3. The count over nights 154 to 163

Principal `converse` messages that woke a Liaison session, and those with
nothing landed: no message caused by them, no statement on their entry, no
ruling with them as the reply (observed: `n163_w6_count.py` in session
a0790d20's scratchpad, over `messages`, `sessions`, `statements`,
`rulings`).

| Night | Woke: fresh, reply | Nothing landed: fresh, reply | Retried |
|---|---|---|---|
| 154 | 3, 34 | 0, 4 | 3 |
| 155 | 3, 51 | 0, 2 | 1 |
| 156 | 3, 40 | 0, 2 | 2 |
| 157 | 3, 37 | 0, 5 | 3 |
| 158 | 3, 27 | 0, 4 | 2 |
| 159 | 3, 44 | 0, 4 | 3 |
| 160 | 3, 28 | 0, 0 | 0 |
| 161 | 3, 33 | 0, 0 | 0 |
| 162 | 3, 32 | 0, 2 | 1 |
| 163 | 3, 30 | **1 (m_p2)**, 1 (m102) | 1 |
| **Total** | **30, 356** | **1, 24** | **16** |

- The fresh miss is new: 1 of 30 fresh wakes, m_p2 only (observed).
- 16 of 24 reply misses got frame 267's second session. The other 8 are
  second replies to a page already retried, such as m176 (observed).

## 4. The candidate frame

**### 3xx. A fresh request whose Liaison session lands nothing is marked
answered, so the request stops and the walk reads quiet (2026-10-24)**

- Site: `session_commit` in `rota/core/db.py`, the answered branch at line
  1118, and the `cause_id` guard of frame 267 in `_page_under_reply` at
  line 789. Cause 6 by the guide, with cause 9 at `sandbox.py` 3238.
- Ends when: first, the mechanism: a principal `converse` with no cause,
  whose session lands no statement and sends nothing, stays open with the
  session's last refusal as its note, wakes once more with that note in
  its head, and on the second miss reaches him as a line that his request
  did not reach the team and why, with s145 on m_p2 as the red test;
  second, on a night, fresh requests that end `answered` with nothing
  landed, from 1 of 3 on night 163 to 0, with the reply misses at frame
  267's count; third, a fresh request that still stops quietly, read as a
  session, closes the frame when its cause is not this one.

**Retry or report.** The smallest fix is the retry: drop the `cause_id`
guard so a fresh request takes the branch at line 1110, one predicate and
one test (reasoned). The retry alone does not meet the composition. After
the second miss there is no page to return, so line 1118 still writes
`answered` and the request stops quietly (reasoned: lines 1118 to 1129).
The composition says "Nothing stops quietly. Every open obligation stays
visible and countable until something discharges it" (observed:
`plans/composition.md` 50). So the composition prefers the report. Build
the retry first, then the report, about 2 cycles (reasoned).

**The paste door.** Its refusal at `sandbox.py` 3238 should name
`brief.segment` for a request, or the retry meets the same refusals
(reasoned: cause 9's cheap fix; frame 267's commit body).

## 5. What to doubt

1. Why s145 chose clarify at turn 1 is a reading from the copied "still
   right" wording and the `current_request` block (reasoned).
2. Section 3 counts messages, statements and rulings, not `brief.intake`
   rows or uncaused asks. The 8 single-session reply misses were not read.
3. The walk seeds m_p2 directly, and the I9 exemption may be deliberate.
   Neither was read.

## Usage

One reader on Opus, read only, no model run. About 65k in, 10k out.
