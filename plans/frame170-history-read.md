# Frame 170, a merge's review leaves no trace: the history read

Written 2026-10-07 05:10 by a read agent on Opus for session 6cc11c8b. Meta
workflow: this record reads the build session's records. The seats it
describes are the rota workflow.

**Result.** The history settles that a fail carries a reason for the
Developer, that a remark is allowed and not required, that a finding has no
`why`, and that the Critic's pass needs no words. No record rules that a
pass or a finding must leave words a person can read. The destination's
words, "a merged change they can read", are the only line that points that
way, and no ruling reads them as a demand on the review. Three questions
stay open. The closing section lists them.

## 1. `rota/LAWS.md`

- Law 2: "Judgement crosses a role boundary only as structured findings —
  ids and states. Verdicts, receipts, per-item rulings. The reasoning is
  written into the decision record by whoever decided, and reached by
  following a ref." And: "A finding is `{constraint_id, status, grain}` and
  has no `why` column. The schema enforces the law rather than the prompt
  asking for it." The enforcement table repeats it: "`findings` has no
  `why` column; message bodies carry refs".
- Law 2 sends reasoning to the decision record, not to nowhere. A
  person who wants the why follows a ref to a `decisions` row. The law
  does not say that the row must exist.
- Law 3, amended: the Architect's judgement "is a gate rather than an
  input, so it has nobody to tell; the verdict lands as rows the merge gate
  reads".
- Law 8, the merge gate: "harness, then Critic, then Architect. Cheap checks
  loop; expensive checks run once. Most failures are failures of intent, so
  screen there first". The enforcement line: "`lifecycle.mergeable` returns
  the reason, in review order". That reason is the gate's own, not the
  Critic's.
- Law 12: "Constraint zero — *"this codebase is not yet understood"*, bound
  to the repo minus surveyed areas — makes ignorance safe on day one. It is
  starved by positive survey records ("surveyed, no constraints found"
  counts), never removed by judgement." The code's headline for k0 is
  `"this area has not been surveyed"` (`rota/onboarding/boot.py:39`). So a
  finding on k0 says, by law, that the area is not surveyed. It says nothing
  of the change.
- Law 12 also: the expected touch set "make[s] "was this change
  incidental?" answerable at review time instead of arguable."
- L0 names the Critic as answerable for "whether it was done, and done
  well".

No law names a pass's words or a reason on a verdict.

## 2. `rota/DECISIONS.md`

- "Git: do not rebase mid-batch": "a verdict is a judgement on a specific
  commit." A further consequence: "PR versus auto-merge is a config switch
  ... The principal already signs off at item level, so a diff-level gate
  is redundant when supervised and essential when unattended." This is the
  one entry that names a person's read of a diff. It calls a diff-level
  gate essential when nobody supervises. The night runs unattended.
- "What deterministic checks cannot catch, and what stands there instead"
  (the principal's correction, 2026-08-29): the stand-ins include
  "adversarial passes (the Critic against cited source — itself a model,
  so sampled and fallible)" and "the human made cheap (the trail's
  architecture exists so a spot-check costs minutes)". The claim is "no
  invisible, unattributable, irreversible errors".
- "The principal's flow: five rulings (2026-09-13)", ruling 4: "The
  Critic's cost is accepted." It rules the Critic's order, not its words.
- "The seat as an exchange (2026-09-12)": "Roman at the TUI with his own
  sentences stays the final test, after click merges cold."
- No entry rules what a pass carries, what a reason carries, or what a
  finding on k0 means for a merge.

## 3. Frame 88 and the archive

Frame 88, "The criterion that stuck three nights is an indent and a
ruling, not a newline", `plans/archive/stack-2026-10-01.md`, line 111.

- 2026-09-27 19:06, in full: "**ruled: only the Critic can reopen a green,
  signed-off batch** (ruled: Roman, in the grill, asked as a story with
  "the complaint does not reopen it" recommended and "the complaint reopens
  it" as the third option). Meta workflow. So a finding filed after the
  Critic's pass on a batch goes to the Critic first, and only the Critic's
  fresh verdict sends the Developer back. The frame's build now has two
  parts: that route in the seats, and the test's assertion on the format."
  This ruling is about the route of a finding. It says nothing of a reason.
- The design record `plans/archive/frame88-design-2026-09-27.md` gives the
  Critic's ruling op a reason: `verdicts.rule(finding_id, ruling, reason)`
  into `finding_rulings` with a `reason` column.
- 2026-09-30 22:29, the ruling that frame 170's status calls "frame 88":
  "**ruled: the Critic reads the whole work and the criteria beside it;
  work outside the criteria gets a remark; a fail is only for a criterion
  the work does not meet as written; a doubt about a criterion is a
  challenge to the Architect; and the Critic's reason must reach the
  Developer** (ruled: Roman, in the terminal, from the story of the builder
  and the inspector ...)". Section 6 quotes Roman's own words.
- 2026-10-01 10:45, pass 1 at `13d138b`: "a remark goes in the reason".
- Frame 90, "The Architect cannot file a finding, and its empty answer
  cycles the Developer", `plans/archive/stack-2026-09-29.md`, line 3. On
  night 95 the Architect could not file a finding and quarantined the
  batch. The repair named the exit "file k0 satisfied with a changed file
  as the grain" (commit `9609e935`, 2026-09-28). Frame 90 closed on night
  96: "the Architect filed three `k0` satisfied findings in one session,
  one per changed file". The k0 exit is the session's design (reasoned), not
  a ruling of Roman. Its purpose was to unstick the gate.
- Night 98's read (`stack-2026-10-01.md`, line 352): "No finding row beyond
  three satisfied `k0` rows". A k0-only review was seen then and recorded
  as normal.
- Frame 101, 102, 107, 122 and 135 name the Critic or a verdict in their
  headings. They repair the wake, the route of a fail and the quote parser.
  None rules on a pass's words.

## 4. The briefs and their commits

`rota/roles/prompts/critic/review.md`:

- Line 26 to 28: "Is there anything here nobody asked for? One judgement
  about the change as a whole, not a line-by-line audit. Work outside the
  criteria is a remark, never a fail".
- Line 30 to 33: "A fail carries `reason=`: the criterion's words the diff
  does not meet as written and what the diff does instead, so the Developer
  reads the objection and not only the ref. A remark goes in `reason=` on
  either result."
- Line 35 to 36: "A fail names its criterion and stops. You are not writing
  a review; you are answering a question, and the Developer follows the ref
  from there." This line dates from before `b519a246` (2026-08-10).

Commits from `git log -S "reason="` on that file:

- `a025cc9e`, 2026-10-01 02:34: "The `verdicts` table gains `reason`.
  `verdicts.emit` takes it as an optional argument and never refuses it.
  ... The Critic's review mode asks for the reason on a fail ... Ruled by
  Roman on 2026-09-30, frame 88: the Critic's reason must reach the
  Developer."
- `13d138b2`, 2026-10-01 10:45: "Roman ruled on 2026-09-30 that a fail
  names a criterion the diff does not meet as written. Work outside the
  criteria is a remark in the reason." This commit wrote "A remark goes in
  `reason=` on either result".
- `376321b0`, 2026-10-01: the doubt about a criterion goes to the
  Terminologist.

The docstring of `verdicts_emit` (`rota/roles/api.py:6741` to `6745`):
"`reason`, on a fail: the criterion's words the work does not meet, and
what the work does instead. The Developer reads it beside the ref (ruled by
Roman, frame 88, 2026-09-30). Never refused, on a pass or on a fail without
one: an optional argument is filled on every call, and a refusal of it
loops the seat (observed: frame 81, 2026-09-24)."

`rota/roles/prompts/architect/structural_review.md`:

- Line 15 to 20: "`findings.find` per constraint checked: the constraint
  id, `satisfied` or `violated`, and the grain that brought it into range.
  Nothing else. There is no field for why, and that is not an oversight —
  your reasoning belongs in `decisions.author`, reachable by a ref if anyone
  ever needs it." From `b519a246`, 2026-08-10, or earlier.
- Line 22 to 24: "When no constraint other than `k0` is in range, no
  constraint binds this diff. File one finding: `k0`, `satisfied`, with a
  changed file as the grain. That row is the record that the review ran."
  From `9609e935` and `f9f6edc9`, 2026-09-28, frame 90.

`git log -S "has not been surveyed" -- rota/` names `0aaedc04` (2026-08-10,
onboarding stage 7) and `ec890aad` (2026-08-11, the artefact audit). Both
are the constraint's birth. Neither rules on its use at review.

## 5. `plans/operating-facts.md`, rulings on briefs and doors

- Line 338: "**An optional argument in an op's signature is filled on every
  call, and a refusal of it loops the seat** (observed: frame 81's
  re-record, 2026-09-24 08:58)." The case: `tests.triage` refused a span on
  the wrong verdict, and `L1-TS-encode-a-criterion` went from green to 0/5.
  The rule: "An optional argument that one branch needs is ignored on the
  others, never refused." This fact is about a refusal of a filled
  argument. It does not cover a refusal of an empty argument, which is the
  case for `reason=''` on a pass.
- Line 280: "Do not bound LLM judgements (slicing, triage, review) by
  rule."
- Line 296: "Constraint zero (k0) cannot be violated."

## 6. Roman's own words

Script: `roman_words.py` in the scripts folder. It streams the user
entries of each transcript with `origin.kind == "human"`, and the
`AskUserQuestion` answers. Times below are the transcripts' UTC. The local
clock reads one hour later.

- 2026-09-24 19:03:21Z, asked "Where does the check against the request's
  own words belong?" after night 92 merged a helper that printed nothing
  and "nobody read the change against the request": "I dont know why it's
  bad in this case but a subagent should have been driving from the
  principals seat".
- 2026-09-30 21:27:09Z, to the builder and inspector story: "Ok so why are
  the work orders and the requirements different?"
- 2026-09-30 21:29:04Z, the ruling itself: "So yes it should read into the
  work, but it can also see the criteria right? If work is out of scope it
  can criticize it,good but but strictly required, however does the
  inspector not tell the builder what's wrong?"
- 2026-10-06 23:55:22Z: "Are we writing on the right things right now?"
  The session's reply recommended "give the Critic's empty pass a frame"
  and said "A merge that nobody checked is not the destination." Roman
  answered at 23:58:12Z: "Ok". The sentence on the destination is the
  session's (reasoned), not Roman's. His "Ok" rules the order.
- No hit in 2026-09-24 to 2026-09-27 or 2026-10-06 to 2026-10-07 names the
  Critic's pass, an empty reason, or k0.

## 7. What the history settles, what it leaves open

### Settled

1. A finding has no `why`. Reasoning goes to `decisions` by ref (ruled:
   law 2, `rota/LAWS.md`, the design; the schema enforces it).
2. A fail carries a reason, and the reason reaches the Developer (ruled:
   Roman, 2026-09-30 22:29 local, "does the inspector not tell the builder
   what's wrong?"; built in `a025cc9e`).
3. A remark on work outside the criteria is allowed and is not required
   (ruled: Roman, 2026-09-30 22:29 local, "it can criticize it, good but
   [not] strictly required"; brief line from `13d138b2`).
4. The door refuses no empty `reason=` (reasoned: `a025cc9e` from the
   observed frame 81 loop, operating-facts line 338, 2026-09-24). The
   observed loop was a refusal of a filled argument. The step to "never
   refuse an empty one" is the session's inference.
5. Only the Critic reopens a green, signed-off batch (ruled: Roman,
   2026-09-27 19:06, frame 88).
6. A k0 finding with a changed file as the grain is "the record that the
   review ran" (reasoned: frame 90's design, `9609e935`, 2026-09-28, to
   unstick night 95). k0 cannot be violated (reasoned: operating-facts line
   296, a door of 2026-09-10/11).
7. The destination is "a merged change they can read" (ruled: Roman,
   agreed 2026-09-10, `plans/composition.md` line 11 to 13).
8. A diff-level gate is "essential when unattended" (ruled: DECISIONS.md,
   "Git: do not rebase mid-batch", design era).

### Open

1. Does "a merged change they can read" ask the review to say what it
   checked, or only that the code is legible to a person? No record reads
   the destination's words against the Critic's pass.
2. Does a pass owe words, or is a pass with no reason a complete verdict?
   The rulings cover a fail and a remark. None covers a pass. The brief's
   line "You are not writing a review; you are answering a question"
   predates every ruling and was never put to Roman.
3. Is a k0 finding a review? Law 12 makes k0 mean "not surveyed". Frame
   90 made a k0 `satisfied` row the proof that the review ran. No ruling
   says whether an unsurveyed area should get a structural review at all,
   or a survey before the merge, or neither.

### Each open question as a story

1. A shop owner asks a carpenter for a shelf. The carpenter builds it. The
   inspector looks and signs "passed" with nothing else. The owner comes
   home and finds a signed card on the shelf. He can see the shelf. He
   cannot see what the inspector looked at. Today that is all he gets.
   The question: is "a change you can read" the shelf, or the shelf and a
   note from the inspector?
2. The same inspector fails a shelf and writes "the bracket is missing,
   and the shelf hangs on one screw". The carpenter reads it and fixes it.
   The next shelf passes, and the inspector writes nothing. Last night a
   shelf passed whose second screw goes nowhere, because the tests never
   put weight on that side. The question: when the inspector passes a
   shelf, must the card say which loads were tried?
3. The building safety officer checks the shelf against the building's
   rules. For this wall nobody has written rules yet. The officer writes
   "no rules for this wall: fine", and that card is the only proof that
   the officer came. The question: is that card a safety check, or should
   the wall get its rules written before a shelf goes on it, or should the
   card say plainly that nothing was checked?
