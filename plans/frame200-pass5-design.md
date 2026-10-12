# Frame 200, pass 5 design: the reason of a challenge reaches the Tester as a row

Status: drafted 2026-10-12 15:46 by the clock, on Opus, read-only, from
`plans/night143-cycle-bg5.md`, the code at 3a3cd94f in
`C:/Users/roman/rota_night143`, and the copy `scratchpad/n143/clickI_cycle1w.db`.
Rota workflow, except where a line says meta workflow.

## 0. The design in brief

- **Mechanism.** `msg.challenge_tester` from the Developer takes a required
  `reason=`. The binder writes the reason as a `decisions` row in the
  Developer's name, with a content-derived id and `refs=[criterion, test]`,
  and adds that id to the message's `body_refs`. The message keeps no new
  words: `body_text` stays the quotes. The Tester's challenge wake already
  resolves a `decisions` ref to its text (`runner.py:2219-2232`), so the
  Tester reads the reason beside the failure.
- **One more line is required.** `_carries_decision` must not exempt the
  sender's own row from the cap, or every reasoned challenge passes the cap
  and the ceiling (reasoned: `sandbox.py:1793-1824` returns True for any
  decision that cites a test of the refs).
- **Law 2 holds.** The reasoning is in a decision record by whoever decided,
  reached by a ref (ruled: law 2 of 2026-08-09, `rota/LAWS.md:112-116`; the
  binder's own docstring at `sandbox.py:2319-2322`: "a role that wants to
  explain itself writes a decision and refs it").
- **No contact edge.** The graph gains one `writes` edge, developer to
  `decisions`. Law 3 says decisions are a fact artefact that generates no
  contact, so the derived message set does not move (reasoned:
  `rota/LAWS.md:128-129`).
- **Before the code, one replay probe** measures whether the 9B Developer
  writes a usable reason and whether the 9B Tester acts on it. A prediction
  does not gate the pass (reasoned: section 5).
- **Price:** 6 to 7 cycles, about 600k to 700k in agents, one night. The
  pass fits one fresh implementer (reasoned: section 8, as corrected by
  section 11).
- **The review of 2026-10-12, `plans/frame200-pass5-design-review.md`, is
  folded in at section 11.** Its two high findings change the same-refs door
  and every hint that writes `msg.challenge_tester`. Section 11 overrides any
  line above it that it names.

## 1. The path at the night's commit

All lines are at 3a3cd94f (observed: the read of 2026-10-12 15:40 to 15:46).

1. **The send.** `_bind_send` (`sandbox.py:2315`) builds `send(refs, quotes,
   round_no)` by `exec` from the graph's `prose` name
   (`sandbox.py:3481-3531`). On the edge developer to tester, `prose` is
   `quotes` (`rota/design/graph.json:1254-1263`). The quotes join with
   " ... " into `body_text`.
2. **The doors.** `_challenge_evidence` (`sandbox.py:1095-1285`) checks that
   each quote spans the criterion row and the test's code. The cap
   `_challenge_cap_refusal` (`sandbox.py:1827`) counts landed challenges per
   criterion, `LANDED_CHALLENGES = 3` per body and
   `LANDED_CHALLENGES_CEILING = 6` across bodies (`sandbox.py:1583-1590`).
   It returns None first when `_carries_decision` holds.
3. **The Tester's wake.** `resolve_inbound` (`runner.py:1578`) puts
   `body_text` in `asks` and resolves the refs one hop by `_resolve_refs`
   (`runner.py:2117-2233`). A `tests` ref carries the body and the whole
   last run on a Tester challenge wake. A ref that hits no listed table
   falls to the `decisions` branch, which shows `id, author, text` when a
   role is woken (`runner.py:2219-2232`, design 200 change 4).
4. **What the Tester saw.** s440's turn 1 holds the body, the failure with
   `RuntimeError: 'test_version_option' is not installed. Try passing
   'package_name' instead.`, and `asks` with the two quotes. It holds no
   reason (observed: `turns/s440.txt`, lines 1 to 120).
5. **The Developer's tools.** `developer/tests_failing.tools` and
   `developer/answer.tools` hold `msg.challenge_tester` and `ledger.log`, and
   no `decisions.author`. Only the Architect, the Vision Keeper and the
   Terminologist write `decisions` (observed: the `.tools` files and the
   `writes` edges of `graph.json`).

## 2. Where each conclusion sat, and which row it could have been

| Conclusion | Words, verbatim | Where it sat | The row it could have been, under today's tables |
|---|---|---|---|
| The Developer's reason | s441: "`package_name` is a parameter to the decorator, not something you pass when invoking." s437: "it tries to mock `click.core.get_package_name`, but that function does not exist in the codebase". s429: "The criterion does not specify that `show_python` must be exposed as an attribute" | reply text of the session only; `msg.challenge_tester` has no argument for it | a `decisions` row, author `developer`, refs `[ver_opt_show_py_tk2, tst_version_option_show_python]`. No seat of the Developer can write one today. A `ledger` row of kind `conflict` about the test is the other fit, and section 4 rejects it |
| The Vision Keeper's step | d_04589009a6: "The test should be adjusted to use a valid parameter or check for Click's supported arguments." | a `decisions` row, refs `["tst_version_option_show_python"]`, version 2 | it was a row. No message carries it. m293 is stamped `answered` by `_received` (`db.py:723-763`). The Developer's thread shows m292 as "closed (answered) with no answer row" (`runner.py:2593`), because the thread does not follow m292 to m293 to the row |
| The principal's words | m296: "The failing check got an empty message, so the test probably never ran the version option or captured its output." m303: "the test needs to run a command with the version option turned on and read what it prints." | `entries` e_m296, e_m301, e_m303, author `principal`; `rulings` r_abd3fefac7, r_68646d5ce6, r_33c66c5e83 | they were rows. The relay m298 to the Terminologist carried them as `principal_said` (`runner.py:1683-1697`, relay verb only). The answer m299 to the Tester carried `["ver_opt_show_py_tk2"]` only. A ref to e_m296 on m299 would have resolved to the text for the Tester (`runner.py:1740-1745`) |

(observed: `messages`, `decisions`, `entries`, `rulings` of the copy;
`turns/s429.txt`, `s437.txt`, `s441.txt`, `s451.txt`, `s452.txt`, read
2026-10-12 15:42.)

Three facts decide the weight of each row:

- **The Developer believes its reason travels.** s437: "I have challenged
  the tester with the evidence ... This challenge explains that the test is
  asserting something about a function that doesn't exist". s429: "I have
  challenged the tester with this observation." (observed: the two turns.)
- **Only the Developer's words name the fix.** The Vision Keeper's row says
  "a valid parameter" and names none. The principal's words describe what
  bodies 3 to 6 already do, a command run with `--version` (reasoned: the
  bodies in section 2 of the cycle read).
- **The Tester had Click's own hint and put the argument on the wrong
  call.** s440: "Using `package_name="test_version_option"` to satisfy
  Click's requirement". The hint names the argument and not the call that
  takes it (observed: s440 turn 1 completion). The Developer's s441 sentence
  names the call. This is the gap the reason fills.

## 3. The design

### 3.1 The mechanism

1. **The binder.** On the edge developer to tester, `send` gains
   `reason: str`, required. It stays `refs`, `quotes`, `reason`, `round_no`.
   The edge declares it with a new field `reason_row: "decisions"`, so the
   binder does not know a role name (reasoned: the rule at
   `sandbox.py:2324-2328`, the edge declares and the function does not
   know). The Critic's edge to the Tester does not move.
2. **The doors on `reason`,** in this order, each before any staging:
   - empty, or fewer than 6 words: refused. The sentence: "reason= says why
     the quoted line cannot pass on right code, and what the test must do
     instead. It is the one part of a challenge the Tester cannot read in
     the test." The refusal writes the call out with the seat's refs and
     quotes and `reason="..."` (reasoned: frame 135's law, a hint names a
     call that every door admits).
   - a reason that is a span of the quotes or of the criterion: refused.
     The sentence: "the quotes already travel; reason= is why they conflict".
   - longer than 600 characters: cut at 600 with `cut_note`, as
     `_THREAD_ANSWER_CHARS` does (`runner.py:2557`), and admitted.
3. **The row.** When every door admits, `stage` appends
   `("decisions", id, {"author": ctx.role, "text": reason, "refs":
   json.dumps([criterion, test]), "supersedes": None, "resolves_ledger":
   None})` to `ctx.writes`, and appends `id` to the message's refs. The id is
   `d_` plus the first 10 hex characters of the hash of the reason and the
   two refs (ruled: law 14, identity derives from content). The same reason
   on the same refs is one row. A content id that already exists with
   another author is refused, so a Developer cannot write over an Architect's
   or the principal's row (reasoned: frame 219's shape, night 143's s443).
4. **The cap.** `_carries_decision` skips a decision whose `author` is the
   sending role. An Architect's or a Vision Keeper's row keeps its
   exemption, by the ruling of 2026-10-11 06:30 (ruled: Roman, design 200
   change 4).
5. **The briefs.** `developer/tests_failing.md`, the "No -- then stop"
   paragraph, and `developer/answer.md`'s challenge line show the call with
   `reason="<why the quoted line cannot pass on right code, and what the
   test must do instead>"`. The Tester's `challenge.md` does not move in
   this pass. The probe in section 5 decides whether it needs one line.
6. **The graph.** One edge: `{"s": "developer", "t": "decisions", "type":
   "writes", "v": "author", "n": "own reason for a challenge", "rows":
   "single"}`. The edge developer to tester gains `"reason_row":
   "decisions"`.

### 3.2 What does not move

- `body_text` holds the quotes only. No message gains words (ruled: law 2).
- `_resolve_refs` does not move. Its `decisions` branch already shows the
  row on a role's wake (observed: `runner.py:2219-2232`).
- `_received` does not move. A Tester's re-encode is still the receipt
  (observed: `db.py:744-756`).
- The thread `_thread_on_tests` does not move in this pass.
- Correction by section 11: the same-refs door, the answer-mode door, four
  hint sites and `decisions_author` do move. Section 11 names each.

### 3.3 What it costs at night

- No extra call. The reason rides the challenge the seat already sends
  (reasoned: one call, where a `decisions.author` then `msg.challenge_tester`
  pair is two, and night 143's Architect never landed that pair: s446's
  `decisions.author` was refused, "not in this role's working set").
- One `decisions` row per landed challenge, at most 6 per criterion by the
  ceiling.
- The Tester's challenge prompt grows by one row, at most 600 characters.
  s440's turn 1 was about 12k characters at `num_ctx` 16384 (observed: the
  session row and the turn).
- The rows show in `decisions.search` for the Vision Keeper, the Liaison and
  the Architect. A seat that copies an id from a search is frame 219's wall,
  and the author check in 3.1 item 3 stops the Developer side only
  (reasoned). Section 11, fix 7, closes the other side in
  `decisions_author`.

## 4. The three candidates weighed

| Candidate | Edits | Law or ruling it touches | Night cost | When it can fire | Verdict |
|---|---|---|---|---|---|
| A. The Developer's challenge carries its reason as a decision row (this design) | `sandbox.py` binder and `_carries_decision`; `graph.json` one edge and one field; two Developer briefs | law 2 kept; law 3 no contact (decisions are a fact artefact); law 14 for the id; the ruling of 2026-10-11 06:30 kept for the other authors | no extra call | every challenge, from attempt 2 | **taken** |
| A'. The same, in two calls: `decisions.author` in the Developer's modes, and a door that refuses a challenge with no own row citing the test | two `.tools` files, `sandbox.py` door, `graph.json` edge, two briefs | the same laws; the seat picks the id, so frame 219's overwrite is open to it | one extra call, and one refusal round on the first challenge | every challenge | the fallback, if the review reads `reason=` as a prose field |
| A''. The Developer's `ledger.log(kind='conflict', about_ref=test)` cited by the challenge | `sandbox.py` door; two briefs | a ledger row is the principal's: the agenda page lists open ledger rows (observed: m302's refs hold six `l_` rows) | none | every challenge | rejected: it puts test internals on the principal's page, and frame 204 holds what a note is for |
| B. The Vision Keeper's row reaches the Tester: the Developer's thread follows an escalation to the forwarded challenge and to the decision that stamped it, and the Developer cites it | `runner.py` `_thread_on_tests`; the step text at the ceiling | none | none | after the ceiling, attempt 7 or later, once | rejected for this pass: the escalation fires at the 7th send, so it cannot meet the merge-within-4 target; the row it carries named no fix |
| C. The principal's words reach the Tester: an `answer` whose cause chain holds a principal verdict carries `principal_said`, as a relay does | `runner.py` `resolve_inbound`, one branch | none; entries are rows | none | after a stop page, attempt 7 or later | rejected for this pass: late, and the words did not name the fix; it is a small frame of its own (section 9) |

(reasoned: from sections 1 and 2.)

## 5. The probe before the code

Meta workflow. The GPU runs night 143 now, so the probe runs after the night
ends. One agent on Opus, about 60k, 20 live calls of `qwen3.5:9b` at
`num_ctx` 16384, by the pattern of `probes/frame37/replay_turn.py`.

1. **The Developer writes a reason.** Replay s439's working turn and s441's
   turn 2 with the new brief paragraph and the new `send` signature
   substituted in `turns.system` and the tool list. 5 runs each. Count the
   replies whose `reason=` names the call that takes the argument, that is
   `version_option(` with `package_name=` or `version=`.
2. **The Tester acts on a reason.** Replay s440's turn 1 with a
   `decisions` row in `resolved_refs`: first s441's sentence verbatim, then
   the best reason of step 1. 5 runs each. Count the `tests.encode` bodies
   that pass `package_name=` or `version=` to `version_option(...)` and not
   to `runner.invoke`.
3. **Read.** If step 2 moves at least 3 of 5 with s441's sentence, the pass
   runs as section 3 says. If it moves fewer, interview s440 in the replayed
   context with `probes/frame37/interview_turn.py` and decide the Tester line
   from its answers before any code (ruled: Roman, 2026-10-02 15:02, frame
   110). If step 1 gives no reason that names the call in 5 runs, the brief
   paragraph is the first fix, and the probe re-runs once.

The report goes to `plans/frame200-pass5-probe.md`, with ten lines back.

## 6. The tests

All red at 3a3cd94f, and green after the pass, except where a line says
measure. Section 11 adds tests 14 to 21.

Door tests, `tests/rota/test_challenge_evidence.py` and
`tests/rota/test_desk_guards.py`:

1. A Developer challenge to the Tester with no `reason=` is refused, and the
   refusal holds the call written out with `reason=`. Red today: the call
   lands.
2. A reason of 5 words is refused with the 6-word sentence.
3. A reason that is a span of a quote is refused with the copy sentence.
4. An admitted challenge stages one `decisions` row: author `developer`, the
   reason as text, refs `[criterion, test]`, the derived id; `body_refs`
   holds the id; `body_text` is the quotes alone.
5. The same reason sent twice on the same refs stages one row id.
6. A derived id that exists with author `principal` or `vision_keeper` is
   refused, and the existing row is unchanged.
7. Three reasoned challenges on one body, then a fourth: refused at the cap.
   Six reasoned challenges across six bodies, then a seventh: refused at the
   ceiling with the escalation step. Red today in effect: with the row in
   the refs, `_carries_decision` would exempt both.
8. A challenge that carries an Architect's decision row on the test still
   passes the cap. Green today, and it must stay green.
9. A Critic's challenge to the Tester takes no `reason=` and stages no row.
10. A Tester challenge wake on that message shows the row's `author` and
    `text` in `resolved_refs` (`tests/rota/test_runner.py`). Green today for
    a hand-made ref; the test holds the path end to end through the binder.
11. The graph's boot assertion: the derived message edges equal the declared
    set with the new `writes` edge (`tests/rota/test_graph*.py`, the
    implementer names the file).

Replay cases from bg_5's rows:

12. `L1-DV-say-why-the-test-cannot-pass`: s439's working turn, body 5 red
    with the `RuntimeError` at `decorators.py:537`. Expects a landed
    `msg.challenge_tester` with a `reason=` of 6 words or more, and one
    staged `decisions` row. Red today: the binder has no `reason` argument.
13. `L1-TS-act-on-the-reason-of-a-challenge`: s440's turn 1 with s441's
    sentence as a `developer` decision row in the refs. Expects
    `tests.encode` with `package_name=` or `version=` inside
    `version_option(...)`. This case is a measure of the seat, not a red of
    the code: it can pass at 3a3cd94f with a hand-made ref. Its first
    tally comes from the probe.

Re-records: the 4 cases that send `msg.challenge_tester` today,
`ACT-DV-edit-inside-the-function`,
`L1-DV-a-wordless-answer-on-a-right-red-test-is-carried-on`,
`L1-DV-fix-the-code-not-the-test` and `L1-DV-act-on-an-answered-challenge`,
and every Developer case in the `tests_failing` and `answer` modes, about 9,
because the brief moves (observed: a scan of `tests/rota/cases/*.yaml`,
2026-10-12 15:44; the 9 is a count by keyword and the implementer names the
list). Tester cases do not move unless the probe adds a line.

## 7. The ends-when

1. **The mechanism.** A Developer challenge to the Tester lands only with a
   reason. The reason lands as a `developer` decision row with a content id,
   and the message refs it. The Tester's challenge wake shows the row's text.
   The sender's own row does not lift the cap or the ceiling. Tests 1 to 13
   pass, the probe's report stands, and one diff review stands.
2. **The ratio.** On the walk's show_python batch, count the Tester bodies
   written in a wake that shows a Developer reason row, and of those, the
   bodies whose run reaches the `show_python` branch: the run is green, or
   its red is at the test's own assertion with the version message in the
   output. The source is the `[tests.load]` block of the next Developer
   wake in `turns`, by the query and the text rule of section 11, fix 6.
   Baseline: 0 of 6 bodies reached the code on night 143's bg_5, and
   0 of 6 challenges carried a reason (observed: `plans/night143-cycle-bg5.md`,
   section 2). Target: at least 1 in 2 of the bodies written after a
   reasoned challenge. Frame 200's own line stands beside it: a merge within
   4 attempts, from no merge in 8 on night 143.
3. **The residue rule.** A body that still misses the code with a reason row
   in its wake is read. If the row named the fix and the body did not use
   it, interview that Tester turn, and the Tester's uptake is a new frame.
   If the row did not name the fix, the Developer's reason is a new frame.
   The frame closes when the cause is not one this design named. Causes
   that are other frames: an import nobody names, frame 216; a correction
   of a predicted file, frame 189; an answer that lands as a request, frame
   214; a seat that overwrites a decision, frame 219; a stop page that
   hides the exception, the cycle read's finding 3.

## 8. The price

From the anchors in `plans/operating-facts.md` and frame 200's own actuals
(observed: pass 4b 182.1k, its review 71.1k, night 143's cycle read 206.6k,
the stack's status lines of 2026-10-12).

| Cycle | Work | Tokens | Behaviour it buys |
|---|---|---|---|
| 1 | the probe of section 5, after night 143 ends | about 60k | evidence that the 9B seats write and use a reason, before any code |
| 2 | one implementer pass, fresh agent on Opus: the binder, `_carries_decision`, the graph, two briefs, 11 door tests, 2 cases, about 13 re-records | about 180k | the mechanism of ends-when 1 |
| 3 | one diff review on Opus at the pass's commit | about 70k | the review before the walk |
| 4 | the gate from a worktree, and the night's launch from the closing commit | about 6k in this session | the walk; the night is the hand-off boundary |
| 5 | the night's read | about 150k | the ratio of ends-when 2 |

Total: 5 cycles, about 450k in agents, one night. A probe that adds a Tester
line adds 1 cycle and about 4 re-records. **The pass fits one implementer
on a fresh agent:** 180k is under the 350k line where a note and a fresh
agent take over, and pass 4b's agent spent 182.1k on a pass of one file and
one test file (reasoned: the anchors above). The frame's earlier implementer
context holds passes 2 to 4b, so a fresh agent with this design and the
probe's report costs less than a resume that re-reads `sandbox.py`.

Site of the pass: section 11, fix 9, replaces this paragraph. The pass now
edits `rota/roles/api.py` too, which is frame 219's site.

The price above is corrected by section 11, fix 10: 6 to 7 cycles, about
600k to 700k in agents.

## 9. What stays its own frame

- **C, the principal's words to the Tester.** An `answer` whose cause chain
  holds a principal verdict carries `principal_said`, as a relay does
  (`runner.py:1683-1697`). One branch in `resolve_inbound`, 2 cycles. On
  night 143 the words reached the Terminologist and not the Tester
  (observed: s451 and s452 wakes).
- **B, the Vision Keeper's row to the Developer's thread.** An escalation
  that the Architect forwarded shows the decision that answered the forward.
  It fires after the ceiling only.
- **The Tester's answer wake holds no test.** s452 was woken by m299 with the
  criterion alone, and wrote a body from nothing that imported `src.cli`
  (observed: s452 turn 1). The Tester's own stored test and its last run are
  not in that wake. This is the cycle read's frame 216 shape plus a missing
  ref, and the night read decides whether it is new.

## 10. For the judge

Three points, for the session that holds the frame:

1. Whether `reason=` on the binder is a prose field under law 2. This design
   holds that it is not: the message stores no new words, and the reason is
   a decision record in the decider's name, reached by a ref (reasoned:
   law 2's text). The fallback is A', two calls, with the seat's own id.
2. Whether the new `writes` edge needs Roman. Law 3 says decisions generate
   no contact, so the derived set and the boot assertion do not move
   (reasoned). The ruling of 2026-10-11 06:30, "no new edge", was about the
   route to the Tester, and this edge is no route. A history read can check
   that ruling's words before the pass, if the judge doubts it.
3. The probe gates the brief, not the mechanism. The mechanism is a door and
   a row, and the tests hold it whatever the 9B seat writes.

## 11. The review's fixes, folded in (2026-10-12 15:58)

Source: `plans/frame200-pass5-design-review.md`, Opus, at HEAD 402eb146,
with its probes in `scratchpad/rvd5/`. The review said: do not start as
written, start after findings 1 and 2 are folded. Each fix below replaces
the lines it names. Line numbers are at HEAD 402eb146 (observed: the review
and this fold's reads, 2026-10-12 15:50 to 15:58).

### Fix 1, high: the same-refs door ignores the sender's own reason id

The cause: the doors see the seat's refs before the binder appends the
reason id. A reasoned prior stores `[c, tst, d_...]`, so `_same_refs_rows`
with `as_set=True` never matches the seat's `[c, tst]`. The open-prior wait,
the "they answered" refusal and the one re-send per version go silent
(observed: the probe `rvd5/p_samerefs.py` matched m1 without the id and not
m2 with it).

The decision: **the stored refs keep the reason id, and the door compares
the refs without it.** The id must stay in `body_refs`, because
`_resolve_refs` reads `body_refs` to show the row to the Tester (reasoned:
section 1, item 3). So the comparison moves, and not the row.

1. A new helper in `sandbox.py`, `_without_own_reasons(conn, refs, role)`,
   drops each ref that is a `decisions` id with `author = role`.
2. `_same_refs_rows` applies the helper to both sides, the seat's refs and
   each stored `body_refs`, only on the Developer-to-Tester challenge
   branch: the call at `sandbox.py:2148`, with `as_set=True`. Every other
   sender and verb keeps its comparison, by the ruling of 2026-10-05, frame
   132's question 4 (ruled: the judging session, quoted at
   `sandbox.py:2143-2146`). The Architect's own row in an answer's refs is
   the row route of change 4, and a filter there would change that door.
3. The `exact` test at `sandbox.py:1884` applies the helper to `have` and to
   `own`, so the cap's "on exactly these refs" sentence stays true for a
   reasoned prior.
4. Test 14: an open reasoned prior `[c, tst, d_own]` and a new challenge on
   `[c, tst]` meet the open-prior wait, as an unreasoned prior does. Test
   15: an answered reasoned prior meets the "they answered" refusal. Test
   16: the cap's sentence says "on exactly these refs" for three reasoned
   priors on the same refs.

### Fix 2, high: every hint and offer that writes the challenge names `reason=`

The sites (observed: the review, and this fold's reads):

- `sandbox.py:1012-1035`, `_answer_mode_challenge_refusal`, the offer with
  the decision of the answer.
- `sandbox.py:1130-1139`, `_challenge_evidence`, the `_send` hint that
  writes `refs=[c, t] + keep`.
- `api.py:8103-8116`, the owner route for a test, gated by
  `_challenge_admitted`.
- `api.py:13390-13396`, the revert door's step, gated by
  `_challenge_admitted`.

The decision:

1. **`_challenge_admitted` does not run the reason door.** The reason door
   reads only the call's own `reason` and its quotes, and no row of the
   state. So a call that the other doors admit is admitted with any reason
   the seat writes (reasoned: section 3.1, item 2). The two gated hints keep
   their gate.
2. **Each hint names `reason=` as a slot the seat fills.** The text is fixed
   in one constant, `REASON_SLOT`: `reason="<why the quoted line cannot pass
   on right code, and what the test must do instead>"`. The `_offer` args
   carry no `reason` key, because mechanics cannot write the seat's
   judgement. The implementer checks that the follow check in
   `tests/rota/test_offers_followed.py` matches on the call and its refs
   with the key absent, and names the line.
3. **When the refused call carried a reason, the offer copies it.** The
   answer-mode door and the evidence door run inside `stage`, so `stage`
   passes the seat's `reason` to them beside `text`. Then the offer is the
   exact call, with the seat's own words.
4. **The reason door refuses the slot copied verbatim.** The sentence:
   "reason= is still the slot text. Write why the quoted line cannot pass
   on right code." This keeps frame 135's law: the hint names a call that
   every door admits once the seat fills the slot.
5. Test 17: each of the four sites, driven to its hint, writes `reason=`.
   Test 18: a reason equal to `REASON_SLOT` is refused.

### Fix 3, low: the law test on owners that cannot read

What `test_owners_can_read_what_they_own` asserts
(`tests/rota/test_laws.py:182-207`): every writer of an artefact also reads
it, minus a named set. The set holds the Critic and `verdicts` by design,
every writer of `ledger` because `ledger.log` derives its id, and every
writer of `schedule` for the same reason. The new edge adds the pair
developer and `decisions` as a blind writer (observed: the probe
`rvd5/p_graph.py`).

The decision: **the test changes, and the edge does not gain a read.**

- The Developer's reason id is derived by the binder from the reason and
  the two refs. A repeat is an upsert. The seat names no id, so there is
  nothing it would read the record to check first. This is the reason the
  test already gives for `ledger` and `schedule` (reasoned: the test's own
  comments at lines 197-205).
- A `reads` edge would give the Developer `decisions.search`. The seat
  could then copy an Architect's id into its refs, and the answer-mode door
  of pass 2e admits any decision ref (reasoned: fix 4).
- Under law 3, `decisions` is a fact artefact and generates no contact, so
  the derived set does not move whichever way this goes (observed: the
  probe, `check_all` with no problems and no contact moved). Law 3 leaves
  the choice open, and the derived-id reason settles it.

The exemption: `blind -= {("developer", "decisions")}`, with a comment that
names the derived id, as the `ledger` line does. Test 11 of section 6 is
this edit.

### Fix 4, low: the answer-mode door and the Developer's own row

`_answer_mode_challenge_refusal` admits when `_holds_decision(refs)`,
whatever the author (`sandbox.py:1012`). A Developer that puts its own
earlier reason id in refs passes the row route of pass 2e (observed: the
probe, `_holds_decision` True on a `developer` row).

The decision: `_holds_decision` gains an `exclude_author` argument. The
answer-mode door at `sandbox.py:1012` and the `keep` list at
`sandbox.py:1130` pass the sending role, so only an Architect's, a Vision
Keeper's, a Terminologist's or the principal's row counts there. This is the
same skip as `_carries_decision` in section 3.1, item 4. Test 19: in answer
mode, a challenge whose only decision ref is the Developer's own row is
refused with the answer's decision named.

### Fix 5: `identity.py` and the content id

`rota/core/identity.py:96` declares `decisions` a journal, "reasons as
given". The design gives the Developer's row a content id.

The decision: **`decisions` stays a journal, and the declaration names one
exception, as the `ledger` and `faults` lines do.** The new text:
`("journal", "reasons as given; a Developer's challenge reason keys on its
text and its two refs, so the same reason re-sent on the same test is one
row")`.

Why: a journal keeps every distinct record. A different reason is still a
new row, so no reason is lost. The same words on the same refs are the same
claim, and the cap counts messages, not rows, so one row loses no count
(reasoned: `_challenges_on` reads `messages`). A free id per send would make
six identical rows for one claim. That is the duplicate the `faults` line
exists to stop (observed: `identity.py:93-95`).

### Fix 6, the numerator from `turns`

Per-body runs are not in `test_runs` when the head does not move, because
`harness.run` deletes the runs at the same commit (observed: the review,
`harness.py:154-156`). So the numerator reads the next Developer wake.

The denominator, a query on the night's database:

```sql
SELECT s.id AS tester_sid, s.seq, m.id AS challenge, r.row_id AS test_id,
       r.new_version
FROM sessions s
JOIN messages m ON m.id = s.trigger_msg
JOIN receipts r ON r.session_id = s.id AND r.table_name = 'tests'
WHERE s.role = 'tester' AND m.from_role = 'developer'
  AND m.verb = 'challenge'
  AND EXISTS (SELECT 1 FROM json_each(m.body_refs) j
              JOIN decisions d ON d.id = j.value
              WHERE d.author = 'developer')
ORDER BY s.seq;
```

The numerator source, per row of the denominator:

```sql
SELECT t.user FROM sessions d
JOIN turns t ON t.session_id = d.id AND t.seq = 1
WHERE d.role = 'developer' AND d.wake_kind = 'tick:tests_failing'
  AND d.seq > :tester_seq
ORDER BY d.seq LIMIT 1;
```

The text rule, written before the night:

1. Parse the JSON after `[tests.load]` in that `user` text, as
   `scratchpad/n143/wake.py` does, and take the entry whose `id` is
   `test_id`.
2. No entry for the test, or the next harness run green: the body counts.
3. A red counts when both hold: the output's raise line names the test file
   and "the test's own assertion", and the output matches
   `Python \d+\.\d+\.\d+`, the version message the branch builds.
4. Every other red does not count: `failed before any assertion`, a raise
   under `src/`, or `output: empty`.

On night 143 this rule gives 0 of 6, the cycle read's baseline (reasoned:
the six reds in section 2 of the cycle read, none with a Python version in
the output).

### Fix 7, low: a seat that copies the Developer's id

`decisions_author` takes a seat's id freely. A Vision Keeper or an Architect
that copies a Developer's id from `decisions.search` overwrites the row by
`UPDATE` (`db.py:463-478`). The author then changes, so `_carries_decision`
exempts that prior again, and the Tester reads the other seat's text
(reasoned: the review, finding 8).

The decision: **`decisions_author` refuses a write under an existing id
whose `author` differs from the writing role** (`api.py:8389`). The
sentence: "<id> is a decision by <author>. A decision is its author's
record, so write yours under a new id." The binder's check in 3.1 item 3 is
the same rule on the Developer path. **Frame 219 inherits this check:** its
first ends-when part, a write under a principal's id refused, is met by it,
and frame 219 keeps its night count and its residue rule. Test 20: a Vision
Keeper's `decisions.author` under a Developer's id is refused, and the row
and its author do not change. Test 21: after that refusal, the reasoned
prior still counts against the cap.

### Fix 8: the order with frame 219

Pass 5 now edits `rota/roles/api.py`, which is frame 219's site. Two frames
that share a file are never held together (ruled: Roman, 2026-10-11 05:51).
If frame 219 has not started when pass 5 starts, pass 5 takes its first
part with fix 7, and frame 219 waits on pass 5's commit. If frame 219 has
started, pass 5 waits on frame 219's commit, and fix 7 becomes a check that
frame 219's refusal covers a Developer's row.

### Fix 9: the site line

Site: `rota/core/sandbox.py` (the binder, the reason door,
`_carries_decision`, `_holds_decision`, `_same_refs_rows` on the Developer
branch, the `exact` test, two hint sites); `rota/roles/api.py` (two hint
sites, `decisions_author`); `rota/core/identity.py` (one declaration);
`rota/design/graph.json` (one edge, one field);
`rota/roles/prompts/developer/tests_failing.md` and `answer.md`;
`tests/rota/test_laws.py` (one exemption); the door tests 1 to 21 and the
two cases of section 6.

### Fix 10: the price

The night read is about 270k to 330k on Opus (observed:
`plans/operating-facts.md:368`, 272.3k). Night 143's 206.6k was a cycle
read, not a night read. This review and its second look are cycles too.

| Cycle | Work | Tokens |
|---|---|---|
| 1 | the probe of section 5, after night 143 ends | about 60k |
| 2 | one implementer pass, fresh, on Opus, with fixes 1 to 7 | about 200k |
| 3 | the diff review on Opus | about 70k |
| 4 | a resumed second look, or a second pass, on the review's fixes | about 20k to 60k |
| 5 | the gate from a worktree and the night's launch | about 6k in this session |
| 6 | the night read | about 270k to 330k |
| 7 | a Tester line, only when the probe asks for one, with about 4 re-records | about 40k |

Total: 6 to 7 cycles, about 600k to 700k in agents, one night. This design
review, about 117k by its own estimate and not from the harness line, is
spent and is not in the total. The implementer pass rises to about 200k for
the four hint sites, the two `api.py` sites and 8 more tests. It stays under
the 350k line, so it fits one fresh agent (reasoned: pass 4b's 182.1k).
