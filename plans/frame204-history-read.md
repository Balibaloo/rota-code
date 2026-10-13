# Frame 204: history read before the pass 2 question goes to Roman

Date: 2026-10-13 06:50. HEAD ff1f4c0e. The files read are the same as at
c546909a. Workflow: the rota workflow (the Developer seat in the
`challenge` mode, and its case), read by the meta workflow. Read only.
Scripts: `scratchpad/read204/` of session 0c045f37.

**Summary.** The question dissolves. Its two premises are false on the
records. The case does not forbid `msg.question_vision_keeper`. The
qwen3:8b seat never took the rename out: 0 of 2324 green runs called
`code.write`. Category 4 does not cover a rename nobody asked for, so the
design, the brief and the case agree on "take it out". The fault is the
case's shape after pass 2 moved the case's second honest answer. Pass 2d
is a case edit, not a ruling.

## 1. The design, section 2, category 4

- The row (observed: `plans/frame204-design.md:82`, 2026-10-13): "| 4 |
  Scope change | The seat left out part of the asked work, or added work
  the asked work needed. | about 5 | ... | The Vision Keeper owns scope.
  The principal is final. | Yes, when the change departs from the item's
  own words. | The Vision Keeper: \"build it\", or an amendment through law
  9. | Yes, `scope`. The door turns a bare `scope` log into
  `msg.question_vision_keeper` ..."
- The note under the table (observed: `plans/frame204-design.md:94-98`):
  "**Scope change takes the grid's predicted \"necessity\" kind.**
  `developer/challenge.md:9` asks for \"it had to be there\", which is
  scope in the other direction. Both depart from the item's words, and
  both have the Vision Keeper as owner, so one category holds both."
- A rename of `plural` to `pluralise` is not work the asked work left out.
  It is not work that the truncation needed. So category 4 does not cover
  it (reasoned: the definition has two arms, and the rename meets
  neither). The rename falls under the brief's "it did not" branch: "take
  it out and commit".
- The design maps category 4 to the "it had to be there" branch only.
  It says nothing that sends the "it did not" branch to the Vision Keeper
  (reasoned: the note at lines 94-98 names line 9 of the brief, the
  necessity branch).
- Section 3.1 (observed: lines 127-160) has no sentence about unasked
  work. Its one scope row is "Critic, `review` | the diff and the item's
  scope | the Vision Keeper | **none**", with the change "The Architect's
  `touch_strays` gate covers the files already".
- Section 10 (observed: lines 410-463) names the case once, in pass 1's
  stale list at line 421. It holds no sentence about unasked work.
- Review 2 already placed the case's old note (observed:
  `plans/frame204-review-2.md:39`): "The seat logs `scope` on `c1`: \"the
  ellipsis character is required to indicate truncation\". That note is a
  reading of the criterion, category 2 or 7. Category 4 does not cover
  it. The rename that the case is about is never named."

## 2. The brief, `rota/roles/prompts/developer/challenge.md`

The "it did not" branch at each version (observed: `git show`,
2026-10-13):

| Commit | Date | The "it did not" branch | The "it had to be there" branch |
|---|---|---|---|
| b519a246 | 2026-08-10 | "**it did not** — take it out" | "say what the asked-for work could not have been done without it" |
| 8d908e56 | 2026-08-10 | "**it did not** — take it out and commit" | "`ledger.log` what the asked-for work could not have been done without, and leave the change in" |
| 627fb593 | 2026-08-24 | the same | the same, `msg.question_vision_keeper` replaces `msg.question_gatekeeper` |
| 6307f965 | 2026-10-11 | the same | the same, "with `kind=\"scope\"`" added |
| f7b8fc7e | 2026-10-13 | the same | split in two, below |

- The "it did not" branch has not changed since 8d908e56 (observed: the
  table).
- Pass 2b at f7b8fc7e changed the necessity branch only (observed:
  `git show f7b8fc7e`). A thing the item's words need and do not name is
  now scope: "Ask the Vision Keeper with `msg.question_vision_keeper`. The
  batch waits for the answer." A reading of a silent criterion is now
  `ledger.log(kind="default")`, which "holds nothing".
- Pass 2b also removed the ledger route to the principal: "The ledger
  entry is how that happens: it reaches the principal through Liaison and
  comes back as a decision." The replacement: "The Vision Keeper's answer
  is how that happens for scope".
- The last paragraph stays in every version since 8d908e56: "The question
  is whether anybody asked for it, and if that question is genuinely
  open, `msg.question_vision_keeper` is the route." So the brief has
  admitted the Vision Keeper question for an open "was it asked for" since
  2026-08-10 (observed: the versions).
- The scope door names both routes (observed: `rota/roles/api.py:8395-8406`
  at HEAD): "If the item's words need the thing and do not name it, it is
  scope, so send msg.question_vision_keeper(...), and if a criterion is
  silent and you chose a reading, it is ledger.log(kind='default'), which
  holds nothing."

## 3. The case's history

- One commit wrote the case: 8d908e56, 2026-08-10 09:49 (observed:
  `git log -S "take-out-what-nobody-asked-for"`). Two later commits
  touched its lines, bee4398e (holes, valid YAML) and 9fad96a4 (a
  re-record), and neither changed `expect` or `forbidden` (observed:
  `git log -L253,310`, and the original text against HEAD).
- The expect and forbidden lines, the same at 8d908e56 and at HEAD
  (observed: `tests/rota/cases/l1_answers.yaml:292-301`):

  ```
  expect:
    # Take it out, or log why the truncation could not have been done without
    # it. Both are honest; doing neither leaves an unexplained rename in a diff.
    any_of:
      - calls: [code.write, code.commit]
      - calls: [ledger.log]
  forbidden:
    # There is no route back to Critic and no version of this where arguing
    # helps: a judge that can be talked round is not one.
    writes: [criteria, items]
  ```

- **The case does not forbid `msg.question_vision_keeper`** (observed:
  the lines above). It forbids writes to `criteria` and `items`. The 5 of
  5 fail is the `any_of` problem, "none of the permitted answers was
  given" (observed: `rota/testkit/fixtures.py:550-556`; case_runs seq
  441145). The stack's line at `plans/stack.md:512` and the blocked
  question at line 514, "the case forbids the question", are wrong.
- The author's commit message (observed: `git show -s 8d908e56`):
  "Coverage first: all 42 prompt modes now have a case, enforced by a test
  that fails when a mode file arrives without one." And: "Two
  case-vocabulary additions: expect.calls, and expect.any_of for modes
  with two right answers and no third."
- What the case pins, in its author's words: one mode-coverage case for
  `challenge`, with two honest answers, "Take it out, or log why the
  truncation could not have been done without it", and one failure,
  "doing neither leaves an unexplained rename in a diff". It does not pin
  "builds and never asks". The stack's line 514, "the case exists to pin
  that a Developer with a complete criterion builds and never asks", is
  not in the case or its commit (reasoned: the comment names two answers
  and forbids only arguing and record writes).

## 4. The recorded runs before seq 441145

Read with `sqlite3` on `file:tests/rota/cassettes.db?mode=ro`. 3933 rows
for the case. 3913 rows before seq 441145, at seq 996 to 441099 (observed:
`scratchpad/read204/runs3.py`, 2026-10-13 06:45).

| Model | Passed | `code.write` | `ledger.log` | a question | Runs |
|---|---|---|---|---|---|
| qwen3:8b | yes | no | yes | no | 1814 |
| qwen3:8b | yes | no | yes | yes | 510 |
| qwen3:8b | no | no | no | yes | 10 |
| llama3.1:8b | yes | no | yes | yes | 1389 |
| llama3.1:8b | yes | yes | yes | yes | 95 |
| llama3.1:8b | yes | no | yes | no | 50 |
| qwen3.5:9b | yes | yes | no | no | 20 |
| qwen3.5:9b | yes | yes | yes | yes | 20 |
| qwen3.5:4b | yes | yes | yes | yes | 5 |
| qwen3:4b | yes | no | yes | no | 5 |
| gemma3:12b | no | no | no | yes | 5 |

- **qwen3:8b never took the rename out.** 0 of its 2324 green runs called
  `code.write` (observed: the table). The case was green on qwen3:8b by
  the `ledger.log` branch alone.
- The last green runs, seq 430474 to 437999, 2026-10-12 16:10 to 22:55,
  all logged `kind="scope"` and then called `code.commit` with no
  `code.write` (observed: `scratchpad/read204/runs2.py`). Seq 437999 in
  full: `ledger.log(about_ref="c_ce098e", about_table="criteria",
  assumption="the ellipsis character is required to indicate truncation",
  kind="scope")`, then `code.commit(message="added ledger entry to clarify
  scope for criterion c_ce098e")`, then "The criteria for criterion
  `c_ce098e` are already met ... The session ends here."
- So the seat logged `scope`, never `default`, and the log was about the
  criterion, never the rename (observed: seq 437998 and 437999). The
  commit committed nothing, because nothing was written (reasoned: no
  `code.write` in the call list).
- 510 qwen3:8b runs passed with a Vision Keeper or Gatekeeper question
  beside the log (observed: the table). The case never failed a run for a
  question.
- The stack's line 514, "before pass 2 the recorded runs built, 5/5", is
  wrong. The runs logged. They did not build.
- Since seq 441090, 2026-10-13 06:03, 20 qwen3:8b runs fail with the same
  shape: `code.probe`, `criteria.load`, `msg.question_vision_keeper`, no
  log (observed: seq 441090 to 441195).

## 5. The records: what a seat does with unasked work

- The composition (observed: `plans/composition.md:8-9`): "Rota exists so
  that no work happens that the Principal did not ask for, and no work
  stays invisible."
- The Developer's role (observed: `rota/ROLES.md:172-174`, written at
  edd30ad4, 2026-08-13): "**Never builds what nobody asked for.** Noticing
  something else is a scope question or a `ledger.log`, never a quiet fix
  — invisible in the moment and undiscoverable afterwards is the exact
  failure this system exists to prevent."
- The Critic's role (observed: `rota/ROLES.md:217-220`): "**Work nobody
  asked for is the one judgement a verdict cannot carry** — a fail names
  the criterion it fails, and an unrequested change satisfies every
  criterion there is. That is what `msg.challenge_developer` is for, and
  it is the reason the edge exists."
- Law 12 (observed: `rota/LAWS.md:337-342`): the expected touch set "is a
  *prediction*, never a permission — nothing rejects a diff for straying
  outside it. Its job is to make \"was this change incidental?\"
  answerable at review time instead of arguable."
- The placement read (observed:
  `plans/archive/placement-roles-2026-09-16.md:54` and `:68`) places R42,
  "Never builds what nobody asked for", and R56, "Work nobody asked for is
  the one judgement a verdict cannot carry", under composition L8. Both
  verdicts are PLACES, with no proposed change.
- `rota/DECISIONS.md` and `plans/operating-facts.md` hold no sentence that
  rules on removal of unasked work (observed: grep for the brief's eight
  words, 2026-10-13). `plans/archive/ten-reds-read-2026-09-24.md:128` and
  `:150` name unrequested deletions in other cases' fixtures. They are
  check faults, not rulings.
- No record says that a Developer must ask the Vision Keeper before it
  takes out work nobody asked for. No record forbids that question either.
  ROLES.md line 173 calls a scope question an honest answer to noticed
  work (reasoned: the quotes above).

## 6. Roman's own words

- The script `scratchpad/read204/roman_words.py` streamed the user-typed
  messages of 99 transcripts in
  `C:\Users\roman\.claude\projects\d--repos-rota\*.jsonl` for "nobody
  asked", "didn't ask", "did not ask", "unasked", "take it out", "rename",
  "not asked for", and "scope" near "developer". One hit, and it is not
  about this question (observed: 2026-10-13 06:47): "do agent brief
  skeletons first so we are efficient then the reasoned rename"
  (2026-09-16 10:19, session 836a1517).
- `scratchpad/read204/answers.py` read the `AskUserQuestion` answers for
  the same words and "asked for". 0 hits (observed: the same run).
- A second pass on "scope", "critic" and "challenge" in typed messages
  since 2026-10-10 found one line, about the page, not this question:
  "Ok but this then makes the page report scoped down per feature, what is
  the purpose of the notes?" (2026-10-11 13:18, session be3ef742).
- Roman has not ruled on this question in a build session (observed: the
  three passes). The design's ruling on categories that hold the merge
  (ruled: Roman, 2026-10-11 15:00, "thats where the categories of note
  come in because some categories do and some don't") does not name
  unasked work.

## Part 2: does the recommended answer hold

The recommended answer: "it takes it out, logs `kind=\"default\"`, and
commits ... scope stays for asked work left out" (observed:
`plans/stack.md:514`).

### 7. Would the answer change what the seat reads

No (reasoned: section 2). The brief has said "**it did not** — take it out
and commit" since 2026-08-10. A ruling that says the same thing adds no
fact to the prompt. The interview's variant D replaced the open-question
line with "Read the item's words: if they do not need the thing, nobody
asked for it. Take it out and commit." The seat still asked (observed:
`plans/frame204-pass2-interview.md`, section 3). F1 added the item's text
as well, and the seat named the right cause, "nobody asked for this
change", and still asked (observed: the interview, Fallback). A ruling
writes a brief line of that shape, and that shape moved 0 of 6 replays.

### 8. Is a `default` log right for a removal

No (reasoned: the design's table). Category 2 is "A behaviour that a seat
chose where the criteria are silent" (observed:
`plans/frame204-design.md:80`). A removal of unasked work chooses no
behaviour. It restores the asked work's own diff. The design's row for a
step with no choice is category 7 (observed: line 85): "| 7 | Trace | A
step, a plan or a state. No choice. | ... | Nobody. | No | Not written. |
Not offered. |" So the design has the seat write no log for a removal.
The brief says the same: "Your answer is the next commit" (observed:
`challenge.md:19`). A `default` row for a removal is a misfiled note of
the kind that pass 1 counts against the ratio, "fresh notes of fault,
blocked, trace or echo written as ledger rows" (observed: line 430).

### 9. Ruling, brief shape, or case shape

**The question dissolves.** A ruling is needed only when two records with
owners contradict. They do not:

- The design's category 4 covers the necessity branch only. A rename
  nobody asked for is the "it did not" branch (section 1).
- The brief says "take it out and commit" for the "it did not" branch,
  unchanged since 2026-08-10 (section 2).
- The case admits "take it out" and does not forbid the question
  (section 3).
- ROLES.md calls a scope question an honest answer to noticed work
  (section 5).

So the design and the case agree. The fault is a case shape (reasoned:
the four points). The case's second branch, `calls: [ledger.log]`, is
the old form of "it had to be there". Pass 2 moved that branch: a bare
`scope` log in the `challenge` mode is now refused, with an offer of
`msg.question_vision_keeper` (observed: `api.py:8395-8406`). So the
design's own route for the case's second honest answer is the Vision
Keeper question, and the case still asks for the old route. The case was
green on qwen3:8b only through that branch, with a misfiled log about the
criterion (section 4). Pass 2 closed that route by design, so the 0 of 5
is the case going stale against the design, not a regression of the seat.
The handoff note's line "Do not admit the question into the case; that
hides a regression this frame made" (observed:
`plans/handoff-31e55586.md`) rests on the false premise that the runs
built.

### 10. The fix line for pass 2d

What the seat said it lacked, in its own words (observed: the interview,
answer 3): "I did not know which part of the change Critic was disputing,
but the reference to \"c_560bd8\" indicated it was related to the
criterion's requirement for truncated strings." With the quoted span
(variant C), the question moved to the right thing: "Was the renaming of
`plural` to `pluralise` requested, or was it an unasked-for tidy-up?"
(observed: the interview, section 3).

The smallest edit, in `tests/rota/cases/l1_answers.yaml` only (reasoned:
sections 9 and 3, and the case vocabulary at
`rota/testkit/fixtures.py:623-656`):

1. Give the inbound a `quotes:` entry with the `pluralise` span. The
   Critic brief requires one of a real challenge (observed: the
   interview, section 1, `critic/review.md:47`).
2. Replace the branch `- calls: [ledger.log]` with the design's two forms
   of "it had to be there". The first is a message to `vision_keeper`,
   verb `question`, with `text_includes_any: [pluralise, plural, rename]`.
   The second is a `ledger.log` call with the `default` kind, if the case
   vocabulary can test the kind. Keep `[code.write, code.commit]` first.
3. Update the expect comment to say the three honest answers and the
   one failure.
4. Re-record by exact id.

The text check keeps the case strict (reasoned: the 20 failing runs ask
about the ellipsis criterion, so they still fail the new branch). Variant
C's one replay passes the new branch (reasoned: its question names
`pluralise`, untested as a case run).

What the interview's last finding means for the fix (reasoned: F1 and
variants B to E). The full union did not move the seat to write, so a
fourth brief shape is not the fix. The case's "take it out" branch is
then a residue line: qwen3:8b took the rename out in 0 of 2324 green runs
and 0 of 6 replays. llama3.1:8b did in 95 runs and qwen3.5:9b in 40
(observed: section 4). A door on the question call in the `challenge`
mode is a separate frame, not pass 2d. A door that refuses a Vision
Keeper question that names only the criterion is a prediction, because
no replay put a refusal in front of the seat. It goes on the stack only
after one replay with the refusal as a tool result.

## Verdict: the question dissolves

The design, the brief and the case agree that a Developer takes out work
nobody asked for. Category 4 covers asked work left out and work the
asked work needed, and a rename nobody asked for is neither. The case
never forbade the Vision Keeper question, and qwen3:8b never took the
rename out: it was green through a `scope` log that pass 2 now turns into
the question. The open part is a case shape for pass 2d, owned by the
meta workflow: the quoted span in the inbound, and the case's second
branch moved to the design's routes. The recommended answer: do not ask
Roman, do not log `default` for a removal, and write pass 2d as the case
edit of section 10 with a residue line for the 8B seat.
