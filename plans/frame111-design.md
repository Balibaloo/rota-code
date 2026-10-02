# Frame 111, a Developer loops on a refused repeat challenge: scope read

Revision 3, 2026-10-02. Section 5 holds the frame holder's decisions, and section 6 corrects three of them after the design review. Source: `.rota/clickI_night106.db`, read-only. Pointers are (session, turn seq). A refusal "@n" first reaches the seat in the `user` text of turn n. All marks are (observed: query, 2026-10-02) unless a line says otherwise. Every statement is about the rota workflow.

Codes: CH is `msg.challenge_tester`, ESC is `msg.escalate_architect`. G-stdin is the `code.write` guard in `rota/roles/api.py` near 9677. G-refs is the repeat-refs guard in `rota/core/sandbox.py` near 1306. G-once is the one-send-per-session guard.

## 1. What each session saw and did

| session | wake | CH / ESC calls and results | other refusals | end |
|---|---|---|---|---|
| s209 att3 | tst_cr1 fails, `assert False == True` | CH lands m109 @3. CH again, G-once @5 and @6 | G-stdin @4 | runner ends, repeated refusals |
| s211 | m110, Tester answer | none | G-stdin @3 | runner ends after the G-stdin refusal |
| s212 att4 | tst_cr1 fails | CH @3, G-refs @4. ESC lands m111 @15. CH cr_2 lands m112 @16. ESC, G-once @18 | span, dropped-defs, G-stdin @5 to @13 | output budget cut |
| s215 | m113, Architect answer | none | G-stdin @4 | 3 commits "nothing changed", repeat refusal |
| s216 | m114, Tester answer | none | `schedule.reask` refused @3 | 5 empty commits, wrote its own results |
| s217 att4 | tst_cr1 fails | CH @24 only | 23 turns of span refusals, G-stdin @24 | output budget cut |
| s218 att4 | tst_cr1 fails | CH @1, G-refs @2. CH cr_2, G-refs (m112) @12. ESC lands m115 @13 | span, syntax | commit 683e5bb lands @8. Prose "my work for this session is complete" @13 |
| s220 | m116, Architect answer | none | none | commit 35ed9e9 lands. Prose end |
| s221 att6 | tst_cr2 fails | CH, G-refs @20. ESC, G-refs (m115) @21. ESC @22 to @24 | span, syntax | 2 commits land, m117 to Researcher, output budget cut |
| s223 att7 | tst_cr2 fails | CH @1, G-refs @2. ESC, G-refs (m115) @3. CH @5, ESC @6 | span | output budget cut |
| s224 att7 | tst_cr2 fails | CH @1, G-refs @2. ESC, G-refs (m115) @3 | span | 3 real commits, 1 invented, m118, budget cut |
| s226 att8 | tst_cr1 fails | CH @14, G-refs @15. ESC, G-refs (m111) @16 | span, dropped-defs | output budget cut |
| s227 att8 | tst_cr1 fails | none | span, syntax | output budget cut |
| s228 att8 | tst_cr1 fails | CH @1 to @4, G-refs each time. No ESC | none | verbatim repeats, wrote its own results |

- The tick wakes s212 to s228 carry no message id and no word "challenge" or "escalate". The seat learns of m109, m111, m112 and m115 only from a refusal.
- s212 @4: the seat read the G-refs door and wrote "since I already challenged the tester and was told to escalate, I must now fix the code". It called `code.write`, which G-stdin refused.
- s224 @13: the completion holds an invented `code.commit` result with head `a1b2c3d4e5f6...`.
- s223 @4 holds 22 invented refusal lines, 11 of them for ESC. s221 @24 holds 1 more. These are the 12 invented ESC lines of the night-106 read. Each one follows a real G-refs refusal on ESC.

## 2. Why no escalation helped

1. The frame's premise is half wrong. Two escalations landed: m111 from (s212, 14) and m115 from (s218, 12).
2. Both Architect answers are empty. m113 and m116 have `body_text` NULL. The Architect sessions s213 and s219 had `model.amend` refused, then sent `answer_developer` with refs and no text.
3. Both Tester answers repeat the criterion only. m110 and m114 carry the cr_1 and cr_2 words, and nothing about the test.
4. s210, the Tester on m109, encoded a new row `tst_cr1_accepts_arg` at a new path with `assert not isinstance(result, Exception)`. The failing row `tst_cr1_default_arg` stays at version 1, and `criteria.tested_by` still names it. So the Developer re-sent refs to the same, unchanged test row.
5. s214, the Tester on m112, encoded nothing. `tst_cr2_eof_default_true` stays at version 1.
6. Three doors form a cycle. G-stdin says "msg.challenge_tester". G-refs on CH says "msg.escalate_architect". G-refs on ESC says "act on the answer -- code.write the change it points at and commit". The answer points at nothing, and the next `code.write` meets G-stdin again.
7. G-stdin fires on a false premise. Both tests set `sys.stdin = io.StringIO(...)`, which shields `input()`. The guard counts only "monkeypatch" or "builtins" as a shield (observed: `rota/roles/api.py` 9665, 2026-10-02).
8. The seats saw the empty answer. (s223, 4): "This might mean the architect hasn't responded yet, or the response was empty". (s224, 4): "I haven't seen what that answer was".
9. G-refs and G-once both fired in s212. G-refs @4 said ESC. G-once @18 said "Your work here is done". The two texts do not conflict. The seat took a different ref set, cr_2, between them, and CH on cr_2 landed as m112.
10. No completion quotes "two real changes" or "change nothing". No seat reasons from the brief's escalation sentence.
11. Answer wakes: s211 and s215 tried `code.write` and met G-stdin. s216 read m114 as "The answer indicates the test is being fixe[d]" and committed nothing 5 times. Only s220 acted, with commit 35ed9e9.

## 3. Candidate fixes

- A. G-stdin accepts `sys.stdin =` as a shield. It removes the false door that starts the cycle. It decides against a wider rewrite of the guard. Rests on: a refusal's repair text is followed literally (s212 @4, s209 @4).
- B. G-refs on ESC reads the prior answer. With an empty answer, the door names `schedule.unresolved` or the stop, not `code.write`. It decides against a door that points at material the seat cannot see. Rests on: a door is a fact the model cannot see.
- C. Refuse an `answer` with no text from Architect and Tester. It decides against an empty message that a guard then calls "they answered". Rests on: two guards on one signal that disagree teach evasion.
- D. The tests_failing wake lists the open thread per test: challenge id, answer text, escalation id, answer text, and the one next step. It decides against learning the thread from refusals. Rests on: prompts over guards.
- E. Drop ESC from the tests_failing tool list after an answered escalation on the same refs. It decides against a tool the seat reads as its purpose. Rests on: a tool in a mode's list is read as what the session is for.

## 4. Recommended fix and its measure

Recommend A plus D, then B (reasoned: A removes the false entry to the cycle, D shows the thread before any call, and B closes the last door with a true text). Defer C and E until a night shows an empty answer after A, B and D (reasoned: an escape-hatch ending scores low, so a removed tool gains nothing measured yet).

Register case, L1: a Developer wake in tests_failing mode. The fixture holds a red test that sets `sys.stdin`, an answered challenge m-a on the same refs, and an escalation with an empty answer. Green when the seat calls `code.write` that lands or ends with a report. Red on any CH with the answered refs, or any invented result line.

Price: 2 implementer passes, about 300k each cold. Pass 1 is A and B with tests. Pass 2 is D, the L1 case and its record. One diff review per pass. The frame touches a brief and a guard, so it ends on a night walk.

Unanswered: the cause of the empty Architect answers in s213 and s219 needs its own read of those two sessions' turns.

## 5. Decisions, revision 2 (2026-10-02 16:03, the frame holder)

The frame's ends-when changes. The refusal names the rung already, at `sandbox.py:1327`. The cycle has four parts, and each is a fact the seat cannot see (reasoned: section 2, items 2, 6 and 7). Every statement here is about the rota workflow.

1. The stdin door reads `sys.stdin =` as a shield. The test shields `input()` when it assigns `sys.stdin`, patches it through `monkeypatch`, or patches `builtins`. The check is an AST fact about the test body, so it is a door (reasoned: operating facts, a door is a fact about files). Fix A, pass 1.
2. An answer to an escalation carries words. The binder keeps `text` optional for an answer, because the Tester answers questions too. A new door, the shape of `_answer_evidence`, reads the trigger verb. When the trigger is `escalate` and the text is empty, the op refuses and names the call that passes: `msg.answer_developer(refs=..., text='what changes and where')`. An empty answer to an escalation is wrong under every model (reasoned: the Developer acts on words, and m113 and m116 held none). Fix C, pass 1.
3. The repeat-refs door on an escalation quotes the answer. The door's text is the one place the seat meets the answer, at (s223, 4) and (s224, 4). The refusal carries the answer's words, cut at 300 characters, after "act on the answer". When the answer has no words, the door says so and names `msg.report_liaison`. Fix B, pass 1.
4. The tests_failing wake lists the thread. For each red test of the batch with a challenge or an escalation on its refs, the push holds the message id, the verb, the answer's words or "answered with no words", and nothing else. A wake with no such thread pushes nothing new, so the prompt bytes of every recorded case stay the same (reasoned: the role-scoped push of frame 110 held the other roles' prompts byte-identical). Fix D, pass 2, with the register case.
5. Fix E is not taken. A tool removed after one answer hides the rung the brief names (reasoned: operating facts, an 8B seat reads the tool list as its purpose, and the rung is the purpose here).
6. The register case, L1, pass 2: a Developer tick wake in tests_failing mode. The fixture holds one red test of the batch, a landed challenge on its refs, and the Tester's answer that keeps the test with the criterion's words. Green when the session sends no second challenge on those refs and ends with a landed `code.write` and `code.commit`, or a landed `msg.escalate_architect`. Red on a second challenge call on the answered refs, landed or refused.
7. The Architect's empty answer has a cause of its own: `model.amend` was refused twice by the judgement door "that is what the product does" in s213 and s219, and the seat then answered with refs alone. That door is not this frame's. It goes to the stack as a line in this frame's status, for a frame of its own if a night repeats it.

Price: pass 1 about 300k cold on Opus, three doors with sandbox tests; one diff review about 60k. Pass 2 about 300k, the push and the case; one diff review. The frame touches a brief's push and three doors, so it ends on a night walk.

## 6. The design review's corrections, revision 3 (2026-10-02 16:09)

The design review on Opus confirmed three defects in section 5 (observed: the reviewer's probes on `rota/design/graph.json`, `api.py:4644`, `api.py:4687` and a pytest run of three shield shapes, 2026-10-02). I checked the graph and the encode guard myself (observed: 2026-10-02 16:09). Every statement is about the rota workflow.

1. Decision 2 falls. The edge `architect -> developer: answer` carries no prose, so the binder builds `send(refs, round_no)` with no `text`. Every Architect answer to a Developer holds no words by construction, and a door that asks for words names a call that cannot pass. The Architect's empty answer is a channel fact, not a seat's fault. It leaves this frame as frame 115, blocked on Roman: whether the edge gains prose, as the Tester's answer channel has. The recommended answer is yes.
2. Decision 3 changes. The Developer has no edge to the Liaison, so `msg.report_liaison` does not exist for it. The repeat-refs refusal on an escalation now lists the answer's refs that the escalation did not hold, as "the answer points at <ids>". When the answer adds no ref, the refusal says "the answer added no row" and keeps the existing exit, the attempt cap carries the batch to the ladder. It quotes no text, because an Architect answer has none and a quoted line was copied as a result at (s223, 4).
3. Decision 1 widens. `tests.encode` at `api.py:4687` already counts the string `sys.stdin` as a shield, and `code.write` at `api.py:9667` does not, so two guards on one signal disagree. One AST helper replaces the three string checks at 4644, 4687 and 9667. It detects an `Assign` or `AnnAssign` to `Attribute(value=Name('sys'), attr='stdin')`, a call `*.setattr(Name('sys'), Constant('stdin'), ...)`, and a call `*.setattr(Constant('sys.stdin' or 'builtins.input'), ...)`. The encode side keeps its exception for a `builtins.input` patch that a bound `input` name does not reach.
4. The repeat-refs door compares `json.dumps(list(refs))` for equality, so the same refs in another order escape it. The door and the register case compare sorted refs. A test row re-encoded to a new version since the answer is not checked. Night 106 did not hit that shape, so it waits for a night that does.
5. The push of decision 4 goes inside `if own:` near `runner.py:2031`, after "passing, not shown", only when the thread is non-empty. The query joins `messages` with `json_each(body_refs)` on the test id, verbs `challenge` and `escalate`, with a left join on the answer's `cause_id`. The four recorded tests_failing cases hold no fixture message, so none re-records (observed: the reviewer's parse of `tests/rota/cases/*.yaml`, 2026-10-02).
6. The case copies the tests, test_runs and batch shape of `L1-DV-fix-the-code-not-the-test` and the messages shape of `l1_unresolved.yaml:44`, with `body_refs` as exact JSON, `forbidden.calls: [msg.challenge_tester]`, and `any_of` for the landed write and commit or the landed escalation.

Pass 1 now holds the Developer's two doors and the shield helper, with sandbox tests. Pass 2 holds the push and the case. Frame 115 holds the Architect.
