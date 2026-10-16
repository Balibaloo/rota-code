# Frame 267, the scope read: a principal's reply consumed with no ruling

Read-only scope read, 2026-10-16 17:47. Rota workflow, unless a line says
meta workflow. Sources: the code at HEAD 0213c1db, and the night's copy
`.rota/clickI_night151.db`, opened `mode=ro`. `rota/llm/toolproto.py` was
not read.

## 1. The reply's path

**Answer: the reply is consumed at the session's commit, by one line in
`session_commit`, whatever the session wrote. No code reads the rulings
table before it marks the reply answered** (observed: `rota/core/db.py`
lines 916 to 955, 2026-10-16).

The path, in order:

1. The principal driver writes the reply. `probes/agent_principal.py`
   `respond` (line 247) returns `Answer(verb="reply")` for a `present`, and
   `principal.land` writes m178: `verb='converse'`, `from_role='principal'`,
   `to_role='liaison'`, `cause_id='m177'`, `status='open'` (observed: the
   m178 row).
2. The wake. `scheduler.open_tips` (`rota/core/scheduler.py` line 54)
   selects every open message with `to_role != 'principal'`. m178 is one,
   so it wakes the Liaison with `Wake(kind="message", detail="converse")`
   (observed: `sessions` row s336, `wake_kind='message'`,
   `wake_detail='converse'`).
3. The dispatch count. `run_session` in `rota/core/runner.py` line 3567
   runs `UPDATE messages SET attempts = attempts + 1` on the trigger
   before the model is called (observed: m178 `attempts = 1`).
4. The end. The repeat door, `runner.py` lines 4007 to 4011, ends a
   session whose last three completions are equal:
   `outcome.errors.append("repeated its previous turn verbatim twice; ended")`.
   The session still commits, `committed = 1`.
5. The consume. `session_commit`, `rota/core/db.py` from line 916:

   ```
   barren = not result.writes and not result.messages
   ...
   if (trig and trig["status"] == "open" and result.checkpoint is None
           and _owes_a_reply(trig) ...):          # -> 'unresolved'
   elif barren and trig and trig["verb"] == "challenge" ...:  # -> 'unresolved'
   elif not (barren and was_unresolved):
       conn.execute("UPDATE messages SET status = 'answered' WHERE id = ?",
                    (result.trigger_msg,))       # line 952
   ```

   `_owes_a_reply` reads `OWED_A_REPLY = ("challenge", "propose",
   "escalate")` (line 666), so a `converse` never takes the first branch.
   The second branch is for a `challenge` only. A barren converse session
   falls to line 952 and the reply reads `answered` (reasoned: the three
   branches; observed: m178 `status='answered'`).
6. The ruling. A ruling lands only when `rulings_rule`
   (`rota/roles/api.py` line 9260) stages a `rulings` row and
   `principal.apply_rulings` (`rota/roles/principal.py` line 2123) turns
   it into a verdict through `land`, which closes the ask. No row was
   staged, so nothing closed m177.

**What s336 did to each row** (observed: `turns`, `tool_calls`,
`messages`, `rulings` and `sessions` of the night's copy):

| Row | Before s336 | After s336 |
|---|---|---|
| `messages` m178, the reply | open, attempts 0 | answered, attempts 1 |
| `messages` m177, the ask (`present`, 12 lines) | open | open |
| `rulings` with `ask_id` or `reply_id` m177 or m178 | none | none |
| `messages` caused by m178 | none | none |
| `sessions` s336 | none | role liaison, committed 1, trigger m178 |

s336's turns 1 to 3 hold one byte-identical call:
`rulings.rule(rulings={"1": "approve", "2": "contest", "3": "contest",
"4": "contest", "5": "contest", "6": "approve", "7": "contest", "8":
"approve", "9": "approve", "10": "approve", "11": "ask", "12": "approve"},
words="... and line 11 is about the JSON change, so it doesn't belong on
this page.")`. Each met `ERROR rulings.rule: line 11: 'ask' is a question
back, and a question is its own call: rulings.rule(ask="<one sentence about
line 11>") with no rulings.` Turn 4 is the runner's account, ending
`- repeated its previous turn verbatim twice; ended`. `tool_calls` logs 2
of the 3 calls (observed: `tool_calls` seq 1 and 2).

## 2. The ask's side

**Answer: m177 stays open because only a landed ruling closes a page, and
nothing wakes a seat on an open page. The agenda tick is held back by the
open page itself, and the driver answers a page once per walk** (observed:
the code below; reasoned: the three together are a dead end).

- No seat wakes on m177. `open_tips` skips `to_role = 'principal'`
  (scheduler.py line 84). A page is the principal's to answer (observed).
- The agenda waits on it. `tick_agenda` (scheduler.py line 1024) counts
  open messages to the principal, less touch notes and held asks, and
  returns `[]` while any is open (lines 1049 to 1053). So m177 open stops
  the next agenda page too (observed: the code).
- The quarantine route does not reach it. `boot.quarantine_exhausted`
  quarantines open messages at `attempts >= message_attempt_cap` (3,
  `rota/core/config.py` line 86). It runs at boot, and in `loop.py` line
  353 only after a session that failed to commit. m178 was answered at
  attempts 1, so the cap never saw it (observed: the code).
- The driver. `probes/agent_principal.py` line 248: `# Once per ask: a
  second visit is a deferral (clickI, 2026-09-16).` `respond` returns None
  for an id in `self.replied`, and `probes/walk.py` line 240 filters the
  pending asks by the same set. At a quiet walk `finish` prints `principal:
  open asks already answered: m177` (line 413) (observed: the code).
- The person. In the real seat no once-rule exists. `pending_asks`
  (`principal.py` line 168) still returns m177, so the page stays under
  "Waiting on you". Nothing on the page says that his answer was lost, so
  he waits for the team (reasoned: the render reads the ask row, which
  carries no trace of m178).

What would have woken a seat on m177: only a new reply from the
principal, a new walk process with an empty `replied` set, or a cancel of
the request. m108's ask m107 was reopened by the second of these
(section 3).

## 3. m108 of s226, the parse-refusal case

**Answer: yes, the same path and the same line, `db.py` line 952** (observed:
m108 `verb='converse'`, `status='answered'`, `attempts=1`; s226
`committed=1`, `wake_detail='converse'`; no `rulings` row and no message
caused by m108).

s226's turn 1 called `rulings={2: "revise", 3: "contest", 4: "contest"}`
and met `lines 1, 5 have no ruling`. Turns 2 to 6 sent
`5: "approve}` with a quote missing and met `unterminated argument list`
four times. Its account ends `- repeated its previous turn verbatim twice;
ended` (observed: s226 turns 1 to 7). The writes and the messages were
empty, so the session was barren, and the converse branch marked the reply
answered.

The difference is the ask's end. m107 stayed open, bg_3 merged without
the correction, and walk 3 started a new driver process with an empty
`replied` set. That driver answered m107 again with m120, which landed as
`r_8236ada2d2`, `status='landed'`, verdict m123 (observed: `rulings`,
2026-10-16). So m108's loss was repaired by the walk boundary by chance,
and m178's was not, because no walk followed walk 3 (reasoned: the
`replied` set lives in `probes/walk.py` line 65, one per process).

## 4. Prior art

**Answer: no earlier frame built a retry or a return for a reply that
lands nothing. Two mechanisms are near and cover other verbs only**
(observed: `grep -n` over `plans/stack.md`, `plans/archive/`,
`rota/DECISIONS.md` and `rota/LAWS.md` for "verbatim twice", "repeated its
previous turn", "lands nowhere", "landed nowhere", "consumed", "no
ruling", 2026-10-16; `DECISIONS.md` and `LAWS.md` live under `rota/`).

- Frame 192, `plans/stack.md` line 998: the Liaison's side. Its door makes
  a word that is not a ruling word map to `contest`, so the second call
  differs from the first. Night 137's s159 on m63 is this wall's shape:
  "the repeat door ended the session with no write, so m63 drew neither a
  ruling nor a question. The agent principal then answered the same page
  again, m64". The frame counts answers that land nowhere. It does not
  touch the reply's status. It does not cover this wall (reasoned: its
  ends-when names the refusal text only).
- Night 139's read, `plans/night139-read.md` lines 58 to 63: m142 "landed
  nowhere", s263 repeated a refused call three times, and "The loss cost
  little. m141 stays `open`. The agenda page m143 came next". It names
  frame 169, the repeat refusal, as nearest. It does not name the consume
  (observed). On that night the next page still came. On night 151 the
  open m177 held `tick_agenda` back (reasoned: section 2; why m143 came
  on night 139 with m141 open was not read).
- Frame 169, archived in `plans/archive/stack-2026-10-11.md` line 123:
  the repeat refusal's text after an eviction. Not this wall.
- Frame 174, in the code at `db.py` line 921: a session that "sent nothing
  caused by its trigger and wrote no receipt for it did not answer it", so
  the trigger goes `unresolved`. This is the exact rule this wall lacks,
  but it holds for `challenge`, `propose` and `escalate` only. The
  barren-challenge rule of clickI night 33 (line 937) is the same idea for
  `challenge`. Neither reads `converse` (observed: `OWED_A_REPLY`).
- `rota/DECISIONS.md` and `rota/LAWS.md` hold no line on a reply that
  lands nothing (observed: the grep). The composition holds the rule:
  "Nothing stops quietly. Every open obligation stays visible and
  countable until something discharges it." (`plans/composition.md`
  line 50).

## 5. The design

**Recommendation: extend frame 174's rule to a principal's reply. A
converse session on a page reply that stages no `rulings` row and sends
nothing to the principal leaves the reply open with the session's last
refusal. The second such session closes the reply and puts the reason on
the page, and the page asks again** (reasoned: the hook already holds every
fact it needs, `result.writes`, `result.messages`, `result.refusals` and
the trigger's `attempts`).

### 5.1 The first half: the reply is not consumed

- Hook: `session_commit`, `rota/core/db.py`, a new branch before line
  950. The condition is all of: the trigger's verb is `converse`,
  `from_role = 'principal'`, its `cause_id` names an open message to the
  principal with a verb in `confirm`, `present` or `clarify`; no write
  in `result.writes` has the table `rulings`; no message in
  `result.messages` goes to the principal (an ask-back counts as an
  answer, as now).
- The count: `messages.attempts` on the reply. It exists, and `run_session`
  increments it at dispatch (runner.py line 3567), so it is 1 at the first
  commit. No new column (reasoned).
- Action at `attempts < 2`: the reply stays `open`, and
  `unresolved_note` takes the last refusal's text from `result.refusals`,
  else the last error. `open_tips` then wakes the Liaison on it again.
- **The second wake must differ from the first.** s336 ran `qwen3:8b` at
  temperature 0.0 (observed: the `sessions` row). The same prompt gives
  the same three calls (reasoned: the repeat door's own comment, "At
  temperature zero the model is a function of its prompt"). So the
  converse wake's head carries one line when the reply has a note: "A
  session on this reply ended with no ruling. Its last refusal: <note>."
  Site: the converse wake's prompt in `rota/core/runner.py`, the same place
  where night 106's thread line goes in (line 3150 and after). Without the
  line, the second session costs one session and buys nothing.

### 5.2 The second half: the ask goes back to the principal

- Action at `attempts >= 2`: the reply goes `answered`, as now. The ask
  stays `open` and takes `unresolved_note` with the reason, prefixed by
  the reply id. The status stays `open`, because `pending_asks` reads
  `open`, and `predicates.unresolved` reads `status = 'unresolved'` only,
  so no ladder wakes (observed: predicates.py line 1132).
- The page: `render_page` (`principal.py` line 1313) puts one line at the
  top of a page whose ask has a note. Proposed words, with the line
  number taken from the refusal's `line N` when it has one:
  "Your last answer to this page did not reach the team. The lead could
  not turn your words about line 11 into a ruling. Answer the page again,
  and say for each line you want changed what to do with it." No
  identifier, no tool name, no refusal text (reasoned: the principal has
  no name for the mechanism, the rule that `predicates.quarantined`
  states).
- The driver: `probes/agent_principal.py` line 249 and `probes/walk.py`
  line 240 key `replied` on the ask id and its note, so a returned page is
  answered once more. Without this change the probe stays quiet on a
  returned page, and the night cannot measure the frame (reasoned).

### 5.3 The smallest alternative

If the second wake is judged not worth one session, skip 5.1's re-wake:
the first barren session marks the reply answered and returns the ask at
once, with the note and the page line of 5.2. This is one branch and no
prompt change. It costs the principal one more answer on every miss, where
5.1 can save that answer when the reason line moves the seat (reasoned).

The alternative named in the brief, the reply and the ask both stay open
and the agenda tick shows the ask again, does not work as stated:
`tick_agenda` returns `[]` while any page is open (scheduler.py lines 1049
to 1053), so no agenda page comes. A reply left open with no cap re-wakes
the Liaison on every pass, because `quarantine_exhausted` runs only after a
failed session (reasoned: section 2).

### 5.4 Red tests and the replay

1. `tests/rota/test_runner.py`, beside
   `test_a_barren_session_on_a_challenge_leaves_it_unresolved` (line
   1725): seed m177, a `present` to the principal, and m178, a principal
   `converse` with `cause_id='m177'` and `attempts=1`. Commit a
   `SessionResult` with `trigger_msg='m178'`, `writes=[]`, `messages=[]`
   and `refusals=[("rulings.rule", "line 11: 'ask' is a question back, and
   a question is its own call: rulings.rule(ask=\"<one sentence about line
   11>\") with no rulings.", "ValueError")]`. Red at HEAD: m178 reads
   `answered`. Green: m178 `open` with the note.
2. The same at `attempts=2`: m178 `answered`, m177 `open` with the note,
   and `pending_asks` renders the page line with "line 11".
3. A session that stages a `rulings` row, and one that sends an ask-back
   to the principal, still mark the reply answered. Both are green at
   HEAD and must stay green.
4. The replay of s336's end: a scripted backend that returns s336's turn 1
   completion three times, through `run_session` on a database seeded with
   m177 and m178, ends on the repeat door and commits barren. Assert as in
   test 1. A second run asserts that the wake text holds the reason line.
5. `tests/rota/test_agent_principal.py`: a page answered once, then given
   a note, is answered a second time and no more.

### 5.5 Price

3 cycles, about 120k on Opus for pass 1 (the branch in `session_commit`,
the wake line, the page line, the driver key, five tests) and about 100k
for the diff review, with 1 more cycle if the review finds a defect.
The night that counts the ratio is frame 258's pass 2 night, as sprint 9
holds it, so the count costs 0 cycles of its own (reasoned: the cycle
shapes of the rule of 2026-10-11 05:51; an instrument fix is 3).

Sites: `rota/core/db.py`, `rota/core/runner.py` (the converse wake head),
`rota/roles/principal.py` (`render_page`), `probes/agent_principal.py`,
`probes/walk.py`. Frame 266 edits `rota/llm/toolproto.py`, so the sites do
not meet (observed: frame 266's status line of 17:41).
