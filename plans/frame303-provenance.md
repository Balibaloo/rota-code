# Frame 303: the provenance of a textless `propose` and the request row it made

Written 2026-10-21 by one agent of session 5389be74, cap 80k. Sources: the
checkout at 66832c54, `.rota/clickI_night157.db`, the git history and the
archives. Line numbers in `rota/roles/api.py` are below line 1760 and sit
outside the region another agent edits today.

## The provenance in five sentences

The `propose` edge from the Architect to the Vision Keeper was born mute by
design: the graph of 2026-08-09 gives it no prose slot, and the commit of
2026-08-15 measured words on the three dispute verbs, lost three cases, and
took the words back (observed: `rota/design/graph.json` lines 870 to 876;
commit 43f7ae96; `rota/SYSTEM.md` line 64). The Vision Keeper's brief has
told the seat since 2026-08-09 to "assert it as an item, which puts it in
front of the principal at the next signoff like anything else" (observed:
`rota/roles/prompts/vision_keeper/propose.md` lines 9 to 11, unchanged
since 6afbbad1). The assert door refuses a seat-made request on a
`challenge` wake only, with the words "only the principal asks for work",
and admits the same write on a `propose` wake (observed: `rota/roles/api.py`
lines 1438 to 1449, commit 81f27127, 2026-10-14). The page then lists any
`in_scope` item that is not observed and not a description under "You
asked", so a `reasoned` item the seat wrote reads as his ask (observed:
`rota/roles/principal.py`, `_is_request_item`; `item_provenance` of
`bg_1_item` is `reasoned`, `none`). Night 91 made the same row,
`bg_1_summary`, on the same wake, and he approved it (observed:
`plans/archive/quarantine-revive-design-2026-09-24.md` lines 22 to 32).

## 1. Which ruling made `propose` and its wake, and what a proposal carries

- The edge is in the first design graph: `{"s": "architect", "t":
  "vision_keeper", "v": "propose", "n": "seam / refactor plan", "rows":
  "all"}`. It has no `prose` key, so the binder gives it no words
  parameter (observed: `rota/design/graph.json` lines 870 to 876; commit
  33474a00, 2026-08-09, "extract the design graph and make it the loaded
  wiring").
- The brief is as old. Commit 6afbbad1 of 2026-08-09, "every mode has a
  prompt", added `rota/prompts/gatekeeper/propose.md`. Its text is the text
  of today, word for word (observed: `git show 6afbbad1:rota/prompts/
  gatekeeper/propose.md` against the checkout). Commit 627fb593 of
  2026-08-24 renamed the seat to Vision Keeper and changed no sentence of
  this brief (observed: `git log --follow` on the file).
- Words were tried and taken back. Commit 43f7ae96 of 2026-08-15, Roman's
  commit from the L1 case measurements: "challenge, propose and escalate got
  words and lost them again: three cases broke, the clearest being a
  Developer that read the code and criteria and asked a question instead of
  writing the fix ... The line stays where the evidence put it: words where
  a question the refs can't carry exists, mute everywhere else." The same
  commit wrote `rota/SYSTEM.md` line 64: "challenge · propose · escalate,
  *refs only — words cost three cases*" (observed: the commit body and
  `git log -S`). The workflow was the case register, not a grill.
- What the design says a proposal carries: a "seam / refactor plan" by refs
  (the graph). The story behind it: "`Architect` proposes a boundary plan;
  `Vision Keeper` drafts it as structural items whose criteria are
  behaviour preserved, boundary exists; it goes to signoff like any scope.
  The principal funds seams explicitly or declines them knowingly"
  (observed: `rota/design/stories.json` line 989). `rota/ONBOARDING.md`
  line 587 lists the step as "seam plan (optional) ... as structural items
  for signoff", output "proposal, items", status "not built".
- The Architect's side: "a seam the structure cannot carry is
  `msg.propose_vision_keeper`, not a decision" (observed: `rota/ROLES.md`
  lines 157 to 159) and "`msg.propose_vision_keeper` with the seam. A
  refactor is scope, and scope is not yours to grant" (observed:
  `rota/roles/prompts/architect/escalate.md` line 16, and the same line in
  `exhausted.md` line 13).
- No row holds a seam. The design names a "seam / refactor plan", but no
  table of the schema is a seam, so the refs can name only a batch, a
  criterion or a test. On night 157 the four `propose` calls carried
  `['bg_1']`, `['cr_3', 'tst_confirm_eof_default_off']` twice and
  `['crit_show_python_version', 'tst_show_python_version']` (observed:
  `tool_calls` where `fn = 'msg.propose_vision_keeper'`). The conclusion
  "the structure cannot carry this" crosses with no pointer to any
  reasoning, which is cause 15 (reasoned: the composition, "Conclusions
  cross a boundary. Reasoning stays where it was made, reachable by a
  pointer"; `plans/wall-guide.md` line 627).
- Later design built on the item path. Frame 200's pass 2d of 2026-10-11
  wrote `RECEIPT_RULES`: `("architect", "vision_keeper", "propose"):
  "items"`, with the comment "`vision_keeper/propose.md`: assert the
  proposal as an item, and both are answers" (observed: `rota/core/db.py`
  lines 683 to 688). An `items` write is the designed receipt of a
  proposal.

## 2. Does the propose door check for words, and what does the wake show

- No. The binder builds two `send` signatures. An edge with `prose` gets
  `send(refs, <prose>, round_no=0)` and the line `if not {arg}: raise
  ValueError(f'{_label} needs {_prose}=: {_why}')` (observed:
  `rota/core/sandbox.py` lines 4040 to 4056). An edge without `prose` gets
  `def send(refs: list[str], round_no: int = 0): return stage(refs,
  round_no)` and the doc "Send a 'propose' message to vision_keeper. refs:
  list of ids." (observed: `rota/core/sandbox.py` lines 4085 to 4088). The
  propose edge has no `prose`, so the call has no body to check. The
  message row holds `body_text` NULL (observed: `messages` row `m94`,
  `body_refs '["bg_1"]'`, `body_text None`).
- s204 was an Architect woken by `tick:exhausted`, "attempt 10 of 10",
  refs `["bg_1"]`, on qwen3:8b. Its eleventh call was
  `msg.propose_vision_keeper(refs=['bg_1'])` (observed: `sessions` and
  `tool_calls` for `s204`).
- s205's turn 1 prompt, around the proposal (observed: `turns` for `s205`,
  seq 1):

  ```
  You were woken by: message
  Inbound message: m94 (propose)

  The message that woke you:
  {
    "from": "architect",
    "verb": "propose",
    "refs": [
      "bg_1"
    ]
  }

  Already run for you, with the results below. Calling any of these again
  returns the same thing and costs you a turn:

  [problem.consult]
  [{"id": "default_on_eof", "kind": "in_scope", ... "headline": "confirm()
  takes a default_on_eof flag: ..."}, {"id": "defines_commands_and_options",
  ... "is_description": 1}, ... {"id": "provides_command_line_interface",
  ... "is_description": 1}]
  ```

  The wake names the batch id and nothing about it. The seat's
  `wake_refs` column is `[]`, so the assert door later reads no statement
  words to compare against (observed: `sessions` row `s205`, column
  `wake_refs`; `rota/roles/api.py` lines 1725 to 1737, the `said` set).
- s205's turns 2 to 6: `problem.consult` again, `decisions.search("bg_1")`
  returning `[]`, `decisions.author(id="bg_1", ...)` refused on the id,
  `decisions.author(id="bg_1_decision", ...)` landed, `problem.assert(id=
  "bg_1", kind="in_scope", ...)` refused on the id, then turn 6's
  `problem.assert(id="bg_1_item", kind="in_scope", text=...)` landed. The
  text of every call is the six-sentence account of Click, which the seat
  composed from the `problem.consult` headlines, plus nothing about a seam
  (observed: `turns` for `s205`, seq 3 to 6; `receipts` rows `('s205',
  'decisions', 'bg_1_decision')` and `('s205', 'items', 'bg_1_item')`).

## 3. Who writes a request item, and what the door admits today

- The composition: "Every record has one writer" (observed:
  `plans/composition.md` line 47) and "Everything from outside the project
  enters through one seat, as cited records" (observed: line 76). The
  Liaison "is the one seat that faces the Principal", and "The wiring
  records the words verbatim before the Liaison wakes" (observed: lines 25
  to 28).
- Law 1: one writing role per row, and `items` is the Vision Keeper's
  table (observed: `rota/LAWS.md` lines 93 to 101). Law 11: a row is
  `decided` when its refs reach a ratified statement or a landed ruling,
  and "Every other row is `reasoned`: a seat's own inference" (observed:
  lines 279 to 291). Law 6: at the Liaison an escalation "is never a ledger
  row written on the principal's behalf (ruled 2026-09-13,
  `plans/principal-flow.md`)" (observed: lines 185 to 189). No law says in
  words that a request item needs a principal message. The nearest rule is
  the door of frame 221.
- The door: `_assert_words_fault` returns, for an id with no item row,
  "{id} is not an item. A challenge creates no request, because only the
  principal asks for work" when the trigger verb is `challenge`, and `None`
  for every other verb (observed: `rota/roles/api.py` lines 1438 to 1449;
  commit 81f27127, 2026-10-14, "the assert door keeps the principal's words
  on a decided item"). A `propose` trigger reaches `return None` at line
  1449, so the write is admitted.
- The second words door in `problem_assert` compares the text with an
  `observed` row of the same id, then with the statements in `wake_refs`.
  `bg_1_item` had no row, and `wake_refs` was empty, so neither branch ran
  (observed: `rota/roles/api.py` lines 1705 to 1737). The item landed as
  `reasoned`, basis `none`, kind `in_scope`, and reached `approved` at
  version 3 (observed: `item_provenance` and `items` for `bg_1_item`).
- The page: `_is_request_item` admits an item that is `in_scope`, not
  `how_it_works`, not `observed`, not delivered and not a description
  (observed: `rota/roles/principal.py`, the function's query and return).
  A `reasoned` item passes, so m102 and m110 listed `bg_1_item` as line 1
  under "You asked" (observed: `messages` rows `m102` and `m110`, refs
  `["bg_1_item", "guess:bg_1_item", ...]`).
- Answer: yes. Today the Vision Keeper can assert an `in_scope` request item
  with no principal message as its cause, on a `propose` wake, and the page
  shows it as his (reasoned: the three doors above, each read at the
  checkout).

## 4. Why s205 reached for an item

- The brief: "Then either assert it as an item, which puts it in front of
  the principal at the next signoff like anything else, or
  `decisions.author` refusing it with the reason. Both are answers. Leaving
  it is not: Architect is blocked on this and will not ask twice" (observed:
  `rota/roles/prompts/vision_keeper/propose.md` lines 9 to 12). The mode
  offers `problem.consult`, `problem.assert`, `decisions.search`,
  `decisions.author` and `msg.report_liaison` (observed: `propose.tools`).
  The brief never names the report.
- The seat did both halves of the "either". It authored `bg_1_decision`
  and then asserted `bg_1_item` with the same text (observed: `turns` seq 4
  to 6). The brief gives no test for which half applies, and the wake gave
  the seat no seam to judge (reasoned: section 2).
- The id refusal: "'bg_1' is already a row of batches; an artefact id is
  unique across every artefact table, or every ref to it is ambiguous. Give
  this items row an id of its own, a short name for what it says, and send
  again" (observed: `turns` seq 6, the error line). The refusal is built
  with `api._offer(ctx, ..., label, {**kwargs, "id": api.INVENT})`, so it
  offers the same call with a new id and keeps the text and the kind
  (observed: `rota/core/sandbox.py` lines 4147 to 4156). The refusal
  answered the id and endorsed the write. `bg_1_item` is the name the
  offer shaped (reasoned: `bg_1_decision` came from the same refusal one
  turn earlier).

## 5. Precedent

- Night 91, the same row. "The item `bg_1_summary` was written by the Vision
  Keeper in `s207`, woken by the Architect's `propose` `m92` in the thread
  of the Developer's `escalate` `m91` on `bg_1`. The seat called
  `problem.assert` twice, first with `id='bg_1'` and then with
  `id='bg_1_summary'`. ... The text is a summary of Click with one sentence
  on `echo_json`. The principal approved it at `m103` to `m105`", and the
  slicing tick made `tk_1_bg_1_summary` from it (observed:
  `plans/archive/quarantine-revive-design-2026-09-24.md` lines 22 to 32;
  `plans/archive/stack-2026-09-24.md` line 358). The same id refusal, the
  same suffix shape, the same approval, 27 days earlier.
- Night 93, the other outcome. Architect s156 sent
  `msg.propose_vision_keeper` with `refs=['b_1']` (m71) on `attempt 10 of
  10`, and Vision Keeper s160 sent `msg.report_liaison` with `refs=['b_1']`
  (m74), no item (observed: `plans/archive/night93-walk-2026-09-25.md`
  lines 183 to 185).
- Night 149, a propose wake rewrote his item. s232 "woke in propose mode,
  authored `d_5_confirm_default_on_eof`, and then sent `problem.assert(id=
  "confirm_default_on_eof", ...)`", the item lost his sentence, and bg_2 was
  cancelled. "Over every night database, 24 Vision Keeper `problem.assert`
  calls on an existing item came from a propose wake, and 7 landed, on
  nights 119, 124, 127, 130, 133, 146 and 149" (observed:
  `plans/night149-read.md` lines 157 to 181). Frame 221's door of
  2026-10-14 closed the decided-item case and left the new-id case open on
  a propose wake (observed: `rota/roles/api.py` lines 1438 to 1457).
- Night 148, his words on a team-written line: "I don't know what that line
  means. Your team wrote it, not me" (observed: `plans/night148-read.md`
  lines 94 to 101, candidate G).
- Textless rows of the refs-only verbs are a known family. Frame 115
  counted Architect answers with no text: 6 of 6 on night 119, 9 of 9 on
  night 121 (observed: `plans/night119-read-fable.md` line 216;
  `plans/night121-read.md` line 133). No read before night 157 names a
  textless `propose` as the cause of a request row (observed: grep of
  `plans/night1*.md` for "textless", "no text" and "_item").

## 6. What a cheap fix is allowed by the history

The records favour the second fix: the assert of a request item needs a
principal message or statement as its cause, and the propose door stays as
it is. The propose door cannot refuse an empty body, because the edge has no
body by the measured ruling of 2026-08-15, "mute everywhere else", so that
fix is a reversal of 43f7ae96 and a design change, not a door (observed:
commit 43f7ae96; `rota/core/sandbox.py` lines 4085 to 4088). The item fix is
one verb wider at a door that already says "only the principal asks for
work" (observed: `rota/roles/api.py` lines 1438 to 1449, 2026-10-14), and it
rests on "Everything from outside the project enters through one seat" and
on law 6's "never a ledger row written on the principal's behalf" (observed:
`plans/composition.md` line 76; `rota/LAWS.md` lines 185 to 189). Two records
then contradict the door and need the same edit: the brief's "assert it as
an item" at `propose.md` line 9, which becomes `msg.report_liaison` with the
refs, and `RECEIPT_RULES` at `rota/core/db.py` line 688, which counts an
`items` write as the proposal's answer (reasoned: a door that refuses the
brief's own instruction repeats frame 187's low of 2026-10-15, the brief and
the door naming different acts). The seam-plan story of `stories.json` line
989 still wants a structural item before the principal, but as a seam he
funds or declines, never under "You asked", so that story is a page label
and a later frame, not a reason to keep this door open (reasoned: the story
against cause 11, `plans/wall-guide.md` line 532).
