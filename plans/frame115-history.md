# Frame 115, the Architect's answer carries no words: the history read

Rota workflow. A read-only agent on Opus read the records on 2026-10-04,
116.6k on the harness line against 110k. Roman asked for the read in place
of a ruling (ruled: Roman, 2026-10-04 14:20, "investigate our decisions,
previous thoughts etc"). Every claim below is the agent's, with its mark.
This session did not run the checks again.

## The options the read judged

- (1) Stay inside law 2. The Architect authors a decision row that says
  the constraint holds, and answers with its ref. An answer that adds no
  row beyond the escalation's refs is refused.
- (2) The edge `architect -> developer: answer` gains a prose field.

## 1. The rulings and laws, oldest first

(observed: the files and commits named, 2026-10-04)

- **Law 2, 2026-08-09**, `rota/LAWS.md:112-119`, commits c941cc0 and
  7e3be75: "Judgement crosses a role boundary only as structured findings
  — ids and states. Verdicts, receipts, per-item rulings. The reasoning is
  written into the decision record by whoever decided, and reached by
  following a ref."
- **`rota/ROLES.md:267-270`, 2026-08-13**, edd30ad, under open boundaries:
  "Making prose the default across every channel is an amendment to Law 2
  rather than a change of habit."
- **b41626d, 2026-08-14**, in `tests/rota/test_roles_doc.py:198-208`: law 2
  "governs *telling*, and every pointing verb … still carries refs and
  nothing else, which is where prose would let a wrong conclusion outrun
  the row it came from. Asking is not telling." And: "A verb that carries
  words on one channel carries them on all of its channels."
- **d0411e5, 2026-08-26**: "A dedicated answer verb with words was tried
  first and the vocabulary law refused it, correctly: answer carries refs
  and no prose on every other channel … Giving it words on one channel
  would split the verb."
- **The binder's docstring**, `rota/core/sandbox.py:933-935`: "There is no
  prose field on purpose: a role that wants to explain itself writes a
  decision and refs it."
- **`plans/composition.md:48-49`, ratified 2026-09-16**: "Conclusions cross
  a boundary. Reasoning stays where it was made, reachable by a pointer."

## 2. The Tester's exception, and whether its reason transfers

- The ruling's own words are not on record. Commit e3cbfbb of 2026-09-15
  says "Roman's call, 2026-09-15". `plans/archive/stack-2026-09-16.md:322`
  says "Roman took the recommendations (23:4x)" (observed).
- The recommendation he took, line 315: give the answer "a verbatim span
  of the criterion the assertion comes from, so a conceding answer cannot
  travel and the exits are defend-with-the-words or `tests.encode`"
  (observed).
- Night 80's failure: the Tester answered "the developer is right, the
  test asserts more than the criterion asks" and kept the test. The
  Developer then made "fourteen writes in one session to bend the code to
  the tests" (observed: the archive, lines 296-311).
- The reason is different in kind. The Tester's field is `quotes`, and the
  door `_answer_evidence` refuses the answer unless the text copies a span
  of a criterion. That change narrowed what an answer can say. Option (2)
  widens the Architect's answer to free text (reasoned: the field is a
  fact door on a row's text, and not a channel for reasoning).
- The exception broke the vocabulary rule.
  `test_a_verb_carries_words_or_does_not_regardless_of_recipient` fails
  with `{'answer': 'some channels carry words and some do not'}` (observed:
  pytest, 2026-10-04). The test is in the gate's known reds,
  `.rota-gate.json:30`, since 2026-10-01
  (`plans/archive/stack-2026-10-02.md:49`).

## 3. Earlier thoughts on the Architect's answer, and measurements

- `plans/frame111-design.md` section 5 item 2 of 2026-10-02 proposed a
  required `text`. Section 6 item 1 dropped it, because the edge has no
  prose, and recommended prose. The status of 19:05 revised that to the
  row-first route (observed).
- The Architect's `escalate.md` has two answer branches, and both write a
  row first: `model.amend`, or `findings.find` with `status='satisfied'`,
  from 2d4125f of 2026-09-14 after night 68. No branch covers "the
  criterion holds, the code does not match" (observed).
- The row-first route was never measured. No night read from 105 to 116
  shows an Architect that calls `decisions.author` before an answer
  (observed: grep, 2026-10-04).
- Every Architect answer to a Developer had empty text: night 106, 2 of 2;
  night 108, 3 sent; night 109, 3 of 3; night 112, 4 of 4; nights 113, 114
  and 116, 1 each (copied from the night reads, observed 2026-10-02 to
  2026-10-04).
- The judgement door refused `model.amend` 6 times on night 108, 4 on
  night 109 and 0 on night 112. Nights 113 to 116 show 9, 11, 9 and 9
  turns, each in 4 sessions, over all Architect modes (copied, observed).

## 4. The judgement door and the row route

- The door is in `model_amend`, `rota/roles/api.py:2296-2305`. It refuses a
  constraint whose words cover 70% or more of an item's words, for an item
  of four words or more. It came in 35a61da of 2026-08-24. Its comment says
  the survey wrote each behaviour "back as a constraint, word for word"
  (observed).
- `decisions_author`, `api.py:6055-6132`, has no content door. It refuses
  only a minute of an item amended in the same session, and dangling
  foreign keys. A row that says "the constraint already holds" passes
  (observed).
- **The gap: the Developer cannot read that row.** `_resolve_refs`,
  `rota/core/runner.py:1712-1760`, resolves statements, items, criteria,
  tests, tickets, constraints, glossary terms, the ledger and entries, and
  not `decisions`. The graph gives the Developer no read edge on
  `decisions`, and no Developer `.tools` file lists one. A decision ref
  reaches the Developer as a bare id (observed).

## 5. Conflicts and amendments per option

- Option (1) fits law 2's words, "reached by following a ref". It fails
  law 2's premise today, because the Developer cannot follow that ref. It
  needs `decisions` in `_resolve_refs`, or a Developer read edge on
  decisions. Law 3 permits the edge: "Fact artefacts — transcript, code,
  decisions, ledger — generate no contact." (reasoned)
- Option (2) goes against b41626d, d0411e5 and the docstring. Under
  `ROLES.md` it is an amendment to law 2. It keeps the vocabulary test red
  unless every `answer` edge gains words or the test changes (reasoned).
- "cr_2 stands and the code does not meet it" is a verdict on rows, which
  law 2 lists as "ids and states", so it is a conclusion. "What changes
  and where" is reasoning (reasoned: `LAWS.md:114-115`).

## 6. What the history settles, and what it leaves open

The history settles that an answer carries refs, that the Tester's quotes
are a narrow fact door, and that a decision row holds the reasoning. It
leaves one question: the Developer sees the Architect's decision row
through the answer, which needs `decisions` resolved in the wake, or
`answer` becomes a verb with words on every channel, which amends law 2.

## 7. The meta records: what Roman and the assistant said

Meta workflow. Roman said the question was already discussed (ruled:
Roman, 2026-10-04 14:34, "we have already discussed this, use a subagent
to search our decisions logs, etc ie meta"). A second agent on Opus, 124.8k
on the harness line against 120k, streamed Roman's typed messages and
question answers from all 70 transcripts in
`C:\Users\roman\.claude\projects\d--repos-rota\`, 2026-09-16 to 2026-10-04.
Transcript times are UTC, and local time is UTC+1 (observed: the
transcripts, 2026-10-04).

- 2026-09-15, about 23:4x local: the Tester's quotes. No transcript exists
  for the day. The record is `plans/archive/stack-2026-09-16.md:322`,
  "Roman took the recommendations (23:4x)."
- 2026-09-16 09:54Z to 10:19Z, session 836a1517: the blocking ask. The
  assistant cited law 2: "reasoning stays where it was made, reachable by
  a pointer. The pointer exists. No seat follows it." Roman: "yes i always
  thought thats how it worked, a dev questions wakers others, and the dev
  is wiped only when needed". Then: "keep this tentative in case our
  understanding is missaligned from the code, This is low priority at the
  moment". This exchange is about a seat's session and not about the
  answer channel.
- 2026-10-02 15:09Z, session 46f23339: a notification, "Frame 115 needs a
  ruling … Recommended: the edge gains prose." No reply.
- 2026-10-02 18:00Z, session 46f23339. Roman: "Ask an agent to look for
  any historical context for your questions". The assistant, 18:05Z, after
  the read: "**Architect's reply (F-115):** add the brief branch "the
  constraint holds", answered through a decision row, and refuse a reply
  that adds no row. No wiring change." No reply on that point.
- 2026-10-03 13:33Z, sessions 46f23339 and 3d6e6173. Roman: "so for your
  question, is there any framework that would have helped you answer it?"
  The assistant: "Both questions I sent you were already answered in the
  records: law 2 from day one settles that an answer is a row and not
  words, and the 2026-09-14 commits settle that a broken project test is
  the Developer's own regression." Roman then said "ok please update
  guidance", which made the history-before-escalation rule in `CLAUDE.md`.

No ruling on frame 115 stands in Roman's own words. The discussion he
names is the exchange of 2026-10-03: the assistant said law 2 settles the
question with the row route, and he took that and ruled the guidance from
it (reasoned: the only meta exchanges on this frame). The one point never
put to him is section 4's gap, that the Developer cannot read a decision
row.

Not searched: the sub-agents' transcripts, `HANDOFF.md`, the workshop
notes, and `rota/DECISIONS.md` outside lines 384-413, 484-619 and grep
hits.

## Not read

`rota/DECISIONS.md` beyond grep hits and lines 500-540;
`plans/night106-read.md` in full; `plans/operating-facts.md` beyond a
grep; the archive beyond grep hits; the turns of s213 and s219.
