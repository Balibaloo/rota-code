# Night 155, walk 1, CYCLE 1: the Critic review of bg_1

Read 2026-10-18 01:06, read-only, from `.rota/clickI.db` and `.rota/night155.log`.
Rota workflow, read by the meta workflow. The night ran from
`C:/Users/roman/rota_night155` at 64fa6b6a.

Result first: the three Critic sessions s138, s139 and s140 each judged bg_1
a pass and never landed the verdict. Each one quoted the diff line
`out = json.dumps(obj, separators=(',', ':'))` inside a single-quoted string
in the `lines` dict. The single quotes in the line closed the string early.
No `verdicts` row was written, so `tick:review` woke again until the tick cap
quarantined it. The batch was then abandoned by a later seat's call, not by
the cap.

## 1. The three Critic sessions

All three sessions ran on qwen3.5:9b at temperature 0.0 and 16384 tokens
(observed: `sessions`). All three were shown the same facts (observed:
`turns`, turn 1 of each):

- The one criterion `echo_json_helper`: "The function `echo_json` must not
  print any additional text ... before or after the JSON output."
- The test `inh_05f7b1750` in `tests/test_utils/test_echo_json.py`, last
  result `pass`, and the inherited project tests, all `pass`.
- The diff of `src/click/utils.py`, 11 added lines. The line that matters is
  `+    out = json.dumps(obj, separators=(',', ':'))`.

s139 and s140 also read "This is attempt 2 of 3" and "attempt 3 of 3" in
turn 1 (observed: `turns`). No session read a red test or a contradicting
diff. Each session's judgement, a pass, was right for the diff (reasoned:
the function writes `json.dumps` and a newline, and nothing else).

**s138.** It called `verdicts.claim_encodes(criterion_id='echo_json_helper',
encodes=True)`, and the call returned OK. Then it sent `verdicts.emit` four
times with `lines={'echo_json_helper': '    out = json.dumps(obj,
separators=(',', \":\"))'}` and close variants. The parser refused every one
(observed: `turns` 2 to 5):

```
ERROR TOOL: verdicts.emit(batch_id='bg_1', result='pass', reason='', lines={'echo_json_helper': '    out =): could not parse arguments: ':' expected after dictionary key (<unknown>, line 1)
```

The session ended on "repeated its previous turn verbatim twice". No
`verdicts.emit` row is in `tool_calls` for s138, because the call never
parsed (observed: `tool_calls`).

**s139.** It sent the same `claim_encodes`, OK, then `verdicts.emit` with
`lines={'echo_json_helper': '    out = json.dumps(obj, separators=(',', ':'))'}`.
That text is valid Python. It parses as a dict with two keys,
`echo_json_helper` and `', '`. The lines door refused it (observed: turn 2):

```
ERROR verdicts.emit(batch_id='bg_1'): ', ' is not a criterion of batch bg_1. Its criteria are echo_json_helper. Send the pass again with lines= naming each of them once
```

The seat then escaped the quotes and dropped the comma,
`separators=(\'\', \':\')`. The added-line door refused that (observed: turn 3):

```
ERROR verdicts.emit: the line for echo_json_helper, "out = json.dumps(obj, separators=('', ':'))", is not an added line of the diff of batch bg_1. Copy one line of the [diff] block that starts with +, without the +, and send the pass again. The added line nearest to it: "out = json.dumps(obj, separators=(',', ':'))". If no added line meets echo_json_helper, that is a fail on it: `verdicts.claim_encodes('echo_json_helper', encodes=...)` first, as for any fail
```

The seat repeated the comma-less call and ended on the verbatim repeat.

**s140.** Its turns are the same as s139's, call for call and refusal for
refusal (observed: `turns`, 351 lines of each dump with the same calls). The
prompts differ only in the attempt number, and the temperature is 0.0.

**What landed.** `sessions.committed` is 1 for all three, and `receipts`
holds no row for s138, s139 or s140 (observed: `receipts`, 2026-10-18 01:06).
`verdicts` is empty (observed). The OK of `claim_encodes` wrote no receipt
(observed). So the three sessions committed nothing.

## 2. Why the wake repeated

The predicate `review`, `rota/core/predicates.py` lines 1307 to 1342 of the
worktree, wakes the Critic for a running batch with a head commit, a green
`test_runs` set at that commit, a test of every criterion, and **no
`verdicts` row for `batch_id = b.id AND commit_sha = b.head_commit`**
(observed: the query). bg_1 had head `9fdfdaf0`, green test runs at that
commit (`tr33` to `tr35` and the rest, attempt 5), and a test of
`echo_json_helper` (observed: `test_runs`, `tests`). The row the three
sessions failed to write is the `verdicts` row for bg_1 at `9fdfdaf0`. With
no row, the predicate fired the same wake three times. `tick_attempts` holds
`critic|tick:review|bg_1` at 3 attempts, quarantined 1, reported 1
(observed). The cap is `tick_attempt_cap`, 3, in `rota/core/config.py`
(observed).

## 3. Why the batch was abandoned

The batch was abandoned by `do:cancel`, and a seat's call caused it. The
cycle cap only quarantined the tick (observed: the order below).

1. The quarantine woke the Liaison s141 on `tick:quarantined`, "1 abandoned:
   review for bg_1 (critic), 3 attempts". It presented m48, "The team stopped
   work on this change." The batch was still `running` then (observed:
   `sessions`, the log line after `CYCLE`).
2. He answered m49: "Please don't drop this change. Fix it and run the review
   again." The verdict m50 was relayed to the Architect, m51, and s144 wrote
   three `batch_touch` rows (observed: `messages`, `receipts`). Nothing
   re-opened the review tick (reasoned: the quarantine lifts only on a write
   that moves a row its refs name, `_lift_quarantines` in `rota/core/db.py`;
   the touch rows are not a head move).
3. The agenda tick s146 presented m52 with three ledger notes, all with
   `about_ref` `echo_json_helper`, a criterion (observed: s146 turn 1). He
   corrected lines 1, 3 and 5 of that page, m53.
4. The verdict m54 carried `principal_verdict` `{"echo_json": "contest",
   "l_1aa639f24a": "contest", "l_a372614e42": "contest"}` (observed: s148
   turn 1). His words name page lines and tests, not the item (observed:
   m53). The Liaison s148 relayed `echo_json` to the Vision Keeper, m55.
5. The Vision Keeper s149 called `problem.set_approval(id="echo_json",
   approval="contested")`, OK, and its receipt is `items` `echo_json`
   (observed: `tool_calls`, `receipts`). The item was `approved` before, by
   s112 (observed: `tool_calls`). m54's `resolved_refs` already shows
   `contested` at s148's wake (observed), so an inferred carrier may have
   written it first, as in frame 274 (reasoned: the order of the rows, not
   checked against the carrier's code).
6. The predicate `cancel`, `rota/core/predicates.py` line 1492, fires on a
   live batch whose item has `approval != 'approved'`. The log reads
   `do:cancel: abandoned bg_1: its item is no longer schedulable`, and
   `batches` now holds bg_1 `abandoned` (observed, 2026-10-18 01:06).

So his "Please don't drop this change" did not hold. A correction of test
notes on a later page became a contest of the item, and that contest
cancelled the batch he asked to keep (reasoned: steps 2 to 6).

## 4. Placement by `plans/wall-guide.md` section 4

Two walls, one per section above.

**Wall A, the review loop (sections 1 and 2): a case of frame 266, the call
parser's refusal of an unterminated argument.** Step 1 places it by sign.
Frame 266's status of 2026-10-17 03:39, night 153, names the same sign: three
Critic sessions send `verdicts.emit` with a `lines` dict whose inner string
breaks, repeat verbatim, the review tick quarantines at 3, and the batch goes
to him as stopped work (observed: `plans/stack.md`, frame 266). The shape is
new to the frame: the inner string holds the quote that delimits it, and it
closes early (reasoned: s138's SyntaxError and s139's two-key parse). Step 4
gives the cause: the doors were right to fire, and the steps point wrong.
The s138 refusal passes Python's text through and names no quote. The s139
and s140 refusals say "Copy one line" and do not say how to quote a line
that holds a single quote. This is cause 9, the refusal's text points the
seat wrong (reasoned). Frame 266's pass 3 helpers did not fire, because every
inner string closes (reasoned: `_open_inner` reads a string that never
closes). The s139 and s140 refusals come from the lines door of
`verdicts.emit`, which is frame 201's site. Frame 201's cause is a pass on a
contradicting diff, and this diff does not contradict, so frame 201 does not
take the case (reasoned: the residue rule). Frames 181 and 163 do not fit: no
verdict landed, and no challenge is open (observed). Frame 170 is closed
(observed: it is not a heading in `plans/stack.md`).

**Wall B, the abandonment (section 3): the sign of frames 274 and 268.** A
relay contest sets an item `contested` that his words do not name, and the
batch is cancelled. Frame 274 names the carrier as the writer for a merged
item of another request. Frame 268 names the relay's `set_approval`. Here the
item is the same request and its batch is live, so the cost is larger: a
built, green batch is abandoned against his ruling m49 (observed: section 3).
Which writer was first is open (reasoned: step 5 of section 3). Place it as a
case of frame 274 if the carrier wrote first, and of frame 268 if s149 did.

**Held frames.** Neither wall is a held frame's wall. The held frames are
283, 220, 286, 282, 290, 143 and 140. Frame 266 and frames 268 and 274 are
not held (observed: the brief's list). The cycle gives the held frames no new
data, because the Developer, Tester and fence turns before it already ran
(reasoned: the stop rule of 2026-10-09 applies only if the night loops on
this wall again).

## 5. CYCLE 2: the confirm loop on s2

Read 2026-10-18 01:16, read-only, from `.rota/clickI.db`, log line 72:
`CYCLE: period 3, rounds 3, wakes: liaison|tick:awaiting_confirm||["s2"], liaison|message|converse|[], liaison|message|verdict|[]`.

Result first: the principal's reply m104 became the new request s2. m104
answered a Liaison question that copied a sentence of the report brief, and
it was not a reply to the touch page. Each "not a new request" reply landed as
a contest of s2. A contest leaves s2 `proposed`. The predicate
`awaiting_confirm` then asked him again. No Liaison mode has a call that
withdraws a proposed statement. The loop ended only when he gave way, m121,
and s224 ratified s2 (observed: `statements`, s2 `ratified`).

### 5.1 The sessions, their calls and what landed

The reply to the touch page m92 was handled correctly (observed: `turns`,
`receipts`):

- **s193**, converse on m93: `rulings.rule(rulings={1: "contest", 2:
  "approve", 3: "approve", 4: "approve", 5: "contest"}, words="Line 5 is
  still wrong...")`. Landed: `rulings` `r_c797b602d8`.
- **s194**, verdict on m94: `msg.relay_architect(refs=["echo_json"])`, which
  returned `{"id": "m95", "to": {"architect": ["bg_3"], "vision_keeper":
  ["echo_json"]}, ...}`. No receipt. m94's `principal_verdict` was
  `{"echo_json": "contest", "bg_3": "contest"}`.

The new request came from a later Vision Keeper report (observed: `messages`
m101 to m105, `turns`):

- **s204**, report on m101, a Vision Keeper report on `e_m94`. It sent
  `msg.clarify_principal(refs=["e_m94"], question="What are the two things
  that cannot both hold, and what does each way cost?")`, which became m102.
  That question copies `rota/roles/prompts/liaison/report.md` line 22, "Name
  the two things that cannot both hold, and say what each way costs"
  (observed: grep in the worktree). No receipt.
- **s206**, converse on m104, his answer to m102, with `refs` `["e_m94"]`.
  It called `msg.confirm_principal(refs=["s1"])`, and the call was refused:

  ```
  ERROR msg.confirm_principal: The words that woke you, `e_m104`, have no statement. Segment them with `brief.segment` and confirm that statement. If they ask for nothing, call no confirm.
  ```

  It then called `brief.segment(id='s2', ...)`, which returned `OK
  brief.segment -> {"id": "s2", "span_entry": "e_m104", "span": [0, 278],
  "note": "span set from the text"}`. Next it called
  `msg.confirm_principal(refs=["s2"])`, which became m105. Landed:
  `statements` `s2`.

The four "not a new request" replies, m106, m113, m116 and m119, each ran
the same three sessions (observed: `turns`, `receipts`):

- **converse, s207, s214, s217 and s220.** Each one first sent
  `rulings.rule` with five lines, copied from the touch page's ruling, two
  times. Each of these calls was refused:

  ```
  ERROR rulings.rule: '2' is not a line of the page. The page numbers its rows 1 to 1; use those numbers
  ```

  The third call, `rulings.rule(rulings={1: "contest"}, words=...)`, landed.
  Receipts: `r_728d8427a5`, `r_5fde5f21c0`, `r_7a4508f047` and
  `r_c5aaa80603`.
- **verdict, s208, s215, s218 and s221.** Each one called
  `brief.ratify(id="s2")`, and s215 and s221 also called `msg.deliver_*`.
  Each call was refused:

  ```
  ERROR brief.ratify: the principal contested s2 in r_728d8427a5, so s2 is not ratified and not delivered. Ratify only what they accepted. When they accepted nothing, end the session with no call
  ```

  No receipt.
- **tick:awaiting_confirm, s213, s216, s219 and s222.** Each one called
  `msg.confirm_principal(refs=['s2'], round_no=0)`, which became m112, m115,
  m118 and m121. No receipt.

s223 ruled `{1: "approve"}` on m122. s224 then ratified s2 and delivered it
to the Vision Keeper and the Architect, and receipt `statements` `s2` landed.
The delivery to the Terminologist was refused on an unterminated argument
list (observed).

### 5.2 Why his words became a new request

The reply to the touch page did not become s2. s193 ruled it as a contest
of line 5, and the ruling landed (observed: 5.1). The new request came from
m104, his answer to the clarify m102 (observed: `messages`, m104 `cause_id`
m102). The route had three steps:

1. The Liaison in report mode copied its own brief's instruction as the
   question (observed: s204, `report.md:22`). He read it as a question about
   line 5 (observed: m106, "it was my answer to your question about line 5").
2. His answer came back with verb `converse` and `refs` `["e_m94"]`, an
   entry, not a page line. Converse mode asks first whether the words ask
   for work, and "keep my line as written and only take out those extra
   files" reads as work (reasoned: `converse.md` lines 14 to 22).
   `converse.tools` offers `brief.intake`, `brief.segment`,
   `msg.clarify_principal`, `msg.confirm_principal`, `brief.list`,
   `transcript.quote` and the three asks. It offers no call that rules a
   line of the open page (observed).
3. The confirm door refused a confirm of s1 and named `brief.segment` as the
   step (observed: s206 turn 2). The seat followed the step.

### 5.3 Why the four replies did not cancel s2

Each reply landed a `contest` of s2 (observed: 5.1). A contest does not
change the status of a statement. `brief_ratify` writes `ratified`, and
`brief.segment` with `supersedes` writes `superseded`. No other call in
`rota/roles/api.py` moves a statement off `proposed` (observed: grep for
statement status writes, 2026-10-18 01:16). `awaiting_confirm`, at
`rota/core/predicates.py` lines 249 to 267, wakes the Liaison for any
`proposed` statement when no confirm is open, so a contested statement
reads as a stalled one (observed: the query). In the confirm page's ruling
words, `RULING_WORDS` in `api.py` line 8881, `drop`, `remove` and `strike`
map to `contest`, and no word withdraws a statement (observed). The modes
under `rota/roles/prompts/liaison/` name no withdraw call. `drop` is a
separate word on the shift page alone, `SHIFT_WORDS` (observed). So no call
would have cancelled s2 (reasoned: the three facts above). The '2' refusals
come from the five-line ruling of the touch page, which `recent_chat`
carries (reasoned: the calls copy s193's ruling).

### 5.4 Why bg_3 was abandoned

bg_3 was abandoned in the same way as bg_1 in section 3. m94, his line
ruling on the touch page, carried `principal_verdict` `{"echo_json":
"contest", "bg_3": "contest"}` (observed: s194 turn 1). The Vision Keeper
s196 called `problem.set_approval(id="echo_json", approval="contested")`,
which returned OK, and the receipt is `items` `echo_json` (observed). Then
`cancel` logged `do:cancel: abandoned bg_3: its item is no longer
schedulable` (observed: the log). The contest of line 5 named files to
touch and not the item (observed: m93).

### 5.5 Placement by `plans/wall-guide.md` section 4

- **The new request, s2: a case of frame 214, "The Liaison copies the
  converse brief's example ask word for word, and the principal's reply to
  it lands as a new request."** Step 1 places it by sign. A copied brief
  sentence went to him as a question, his reply became a new request, and
  he corrected repeated confirms (observed: frame 214's first paragraph).
  The copied text here is `report.md:22` and not `converse.md:102`, so the
  frame's site grows by one prompt file (reasoned: the residue rule keeps
  the frame, because the cause is the same, a brief sentence sent as a
  question).
- **The loop, four confirms of a contested s2: no open frame names it.**
  Frame 192 is the closest. It is about `drop` refused as a word on a line
  ruling, and here the word maps to `contest` and lands (observed: frame
  192's first paragraph). Step 5 places it as cause 6: `awaiting_confirm`
  reads a contested `proposed` statement as a stalled one. Cause 10 is
  beside it: no mode has a call that withdraws a contested statement
  (reasoned: 5.3). This wall is a new frame candidate.
- **The '2' refusals: the sign of frame 272.** `recent_chat` carries line
  numbers from an earlier page, and the seat contests them on the current
  page (observed: frame 272's first paragraph). The door was right to
  refuse.
- **bg_3: the sign of frames 274 and 268,** the same as wall B of section 4.
- Frames 185, 184, 258 and 264 do not fit. Frame 185 is about the "later"
  word, frame 184 about an ask-back on a word, frame 258 about a contest on
  an unnamed item line, and frame 264 about account rows (observed: their
  first paragraphs).

**Held frames.** None of these walls is a held frame's wall. The held frames
are 283, 220, 286, 282, 290, 143 and 140 (observed: the brief's list).

## 6. CYCLE 3: "Later" on the second shift page does not land

Read 2026-10-18 01:26, read-only, from `.rota/clickI.db`, log line 127, in
walk 2: `CYCLE: period 1, rounds 3, wakes: liaison|message|converse|[]`.

Result first: his first "Later" landed. His second and third did not. The
shift page `m_shift_echo_json_tests_m_p2` has one line. The Liaison put a
line 2, and on s313's first call `words`, into every ruling map. The shift
door checks the word of each key before it checks that the line exists. So
it refused line 2 with "line 2 takes later, now or drop", and it never said
that the page has no line 2. The seats kept `1: "later"` right and kept
changing line 2. Three sessions ended with no ruling, and bg_5 of the item
he asked to put aside is `running` (observed: `batches`, 2026-10-18 01:26).

### 6.1 The sessions, their calls and what landed

The shift pages are present messages. `m_shift_echo_json_m_p2` has `refs`
`["echo_json", "s4"]`, and `m_shift_echo_json_tests_m_p2` has
`["echo_json_tests", "s4"]`. s4 is the new request, "Let confirm() take a
default_on_eof flag..." (observed: `messages`, s313 turn 1).

- **s311**, converse on m203, the reply to the first page. It called
  `rulings.rule(rulings={1: "later"}, words="Later. Put the first change
  aside...")`. Landed: `rulings` `r_b8bce63f1b`, and `item_parks`
  `ip_aeec38c0fe` holds `echo_json`, `park`, `shift`, from `m204`
  (observed).
- **s313**, converse on m205, the reply to the second page. It made five
  calls. The first was `{1: "contest", "words": "..."}`. The next were `{1:
  "later", 2: "approve", ... 8: "approve"}` and then `{1: "later", 2:
  "contest", 3 to 8: "approve"}`, three times. The refusals were (observed:
  turns 2 to 6):

  ```
  ERROR rulings.rule: line 1 takes later, now or drop: the question is which request goes first, and nothing about the request itself changes here.
  ERROR rulings.rule: line 2 takes later, now or drop: the question is which request goes first, and nothing about the request itself changes here.
  ERROR TOOL: rulings.rule(...: unterminated argument list: a string in the value of rulings starts at character 108 after the open bracket. The string `"approve}` has no closing quote before `, words=`, so it runs on into the next argument. Put the closing quote where that value ends, and change nothing else
  NOTE rulings.rule has been refused the same way in three turns and will not be accepted again. Finish what remains (attest, answer, end) without it
  ```

  No receipt.
- **s314**, converse on m205 again. It sent `{1: "contest", 2: "contest"}`,
  then `{1: "later", 2: "contest"}` three times. It got the same line 1 and
  line 2 refusals and ended on the verbatim repeat. No receipt (observed).
- **s315**, converse on m206, the reply to the page sent again, "Later for
  line 1 ... I don't see a line 2 on this page". It sent `{1: "contest", 2:
  "approve"}`, then `{1: "later", 2: "approve"}` two times, `{1: "contest",
  2: "approve"}`, and `{1: "later", 2: "approve"}`. Every call got a line 1
  or a line 2 refusal of the same text, and the session ended on the NOTE.
  No receipt (observed).

### 6.2 Why "Later" did not land on the second page

The page offered one line and three words (observed: s313 turn 1,
`landing.page` and `landing.lines`, which is `{"1": "echo_json_tests"}`):

```
Choose one for line 1:
  - later: put it aside until the new request is merged. Nothing more about it reaches you until then.
  - now: answer its open page first, then the new request.
  - drop: stop it. Its change is abandoned.
```

The page expected `rulings.rule(rulings={1: "later"}, words=...)` and
nothing else (reasoned: `SHIFT_WORDS`, `rota/roles/api.py` line 8891). That
is the call s311 made. The seats sent `1: "later"` with a line 2 beside it.
`_ruling_word`, `api.py` lines 8900 to 8931, checks each key's word against
`SHIFT_WORDS` and raises "line {key} takes later, now or drop" for
`approve`, `contest` or `revise`. That text names line 2 as if the page had
it (observed: the code). The plain page's check, "'2' is not a line of the
page. The page numbers its rows 1 to 1", came first in cycle 2 (section 5.1).
On the shift page the word check fired first (observed: the refusals; the
call order inside `rulings_rule` is reasoned and was not read).

Line 2 came from two places (reasoned):

- his second clause, "Line 1 also doesn't describe my request". A shift page
  has no word that corrects a description, so the seat looked for a second
  line to carry `contest`.
- `recent_chat`, which carries his reply to an earlier page, "On line 2, the
  files to touch should be only..." (observed: s313 turn 1), and the
  eight-line touch page at the end of walk 1 (observed: the log).

### 6.3 Quarantine and what the walk did next

No quarantine. `tick_attempts` holds no Liaison converse key, and the three
messages m205, m206 and m205 again count as three rounds of `converse`
(observed: `tick_attempts`, 2026-10-18 01:26). The page
`m_shift_echo_json_tests_m_p2` is still `open` (observed: `messages`). No
`item_parks` row holds `echo_json_tests`. bg_4 of that item is `abandoned`
and bg_5 is `running`. `tick_attempts` shows `architect|tick:annotate|bg_5`,
`liaison|tick:touch_note|bg_5,echo_json_tests` and
`developer|tick:batch_start|bg_5` at 1 attempt each (observed). So the walk
builds the request he asked to put aside. The log holds no line after line
127 at 01:26 (observed).

### 6.4 Placement by `plans/wall-guide.md` section 4

- **No open frame names this cause. It is a new frame candidate, cause 9,
  the refusal's text points the seat wrong.** Step 4: the door was right to
  refuse a line 2, and its text named the wrong fault, the word and not the
  missing line (reasoned: 6.2). A fix gives the line-number check first
  place on a shift page, with the plain page's text "The page numbers its
  rows 1 to 1" (reasoned, not built).
- **Frame 272 is the closest sign.** `recent_chat` carries his line numbers
  from an earlier page, and the Liaison rules them on the current page
  (observed: frame 272's first paragraph). Frame 272 says the door refused
  right. Here the door's text is wrong, so the cause differs, and the case
  is a new frame by the residue rule (reasoned).
- **Frame 265, "Now." on a shift page lands as `later`.** Same page and same
  refusal text, but its cause is cause 1, his word changed at the Liaison's
  second call. Here `later` stayed right on line 1 (observed: 6.1). It does
  not take the case.
- **Frame 185 and frame 192** are about a word with no ruling on a plain
  page. Here the word `later` exists and was sent (observed: their first
  paragraphs). They do not take the case.
- **Frame 266** is the parser's refusal, and its key-branch text fired once
  in s313 and was right: "The string `"approve}` has no closing quote before
  `, words=`" (observed). That is frame 266's validating count, not this
  wall.
- **The lost description correction** is cause 10, because a shift page
  has no route for "Line 1 also doesn't describe my request" (reasoned).
  The candidate frame carries it as a second case.

**Held frames.** This is not a held frame's wall. The held frames are 283,
220, 286, 282, 290, 143 and 140 (observed: the brief's list). The night is
on another wall with no page for the held frames, if the loop goes on
(reasoned: the stop rule of 2026-10-09).
