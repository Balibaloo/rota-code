# Frame 204: the categories of a seat's note

Read-only, Fable, 2026-10-11 15:40, an agent of session be3ef742, 166.1k on the harness line against 200k (ruled: Roman, 2026-10-11, the ideation runs on Fable and its goal is the categories). The harness refused the report write; this file keeps the report's categories, the owner table, the grid and the questions, and drops the placement of the twelve notes and the longer example lists. Built from the structure, every seat's `ledger.log` modes and the briefs' sentences, twelve sources a gap can be in and nine actions a seat can take, then tested against `plans/frame204-corpus.md`. Rota workflow.

## 1. The fact that shapes the rest

A note has one writer in name and three in fact (observed: `rota/roles/api.py`): the seat's own `ledger.log`; a door that writes the words and offers the call back (`tests.encode` at `api.py:6983-7001`, `challenge.break` at `api.py:10182-10187`, `ledger.unaddressed` at `api.py:7905`); and the blindspot tick. 163 of 583 fresh notes carry a door's words, 221 more echo a ruling, and a seat's own choice in its own words is 39, 7%. A category set that starts from "the seat picks a kind" starts from a small minority. The doors already pick a kind for what they write, and pick it well.

## 2. The space against the corpus

The structure predicts six of the corpus's eight masses: gap label, dictated literal, real choice, tool fault, critic finding, unaddressed. It missed two, ruling echo (221) and work log (65), which no brief offers and which come from a session with nothing left to do (reasoned: `developer/batch_start.md:47-49`; `terminologist/relay.md:14` still invites a note on a contest). The space splits two masses by owner: real choice into default behaviour, conflict and scope cut; tool fault into blocked by the record (68, adoption and lookup faults) and tool fault proper (27). The space predicts four kinds the corpus lacks: necessity ("it had to be there"), a world assumption, a term sense chosen between two, a statement's silence.

## 3. The eleven categories, with examples (observed: the corpus)

1. **Invented value.** A literal the test or the code chose where the material gives none. "test chooses name, age, Alice"; "EOF simulated by empty StringIO, not closed stdin".
2. **Default behaviour.** A behaviour chosen where the criteria are silent; the briefs' own category. "Preserved existing 'one-retry' behavior by restoring the break statement, as criteria are silent on this edge case"; "The surface must be 'version_option' itself, not 'custom_version_option'". About 30 of the door's 103 "the test assumes" notes are these, hidden in the literal's template.
3. **Conflict.** Two rows disagree, and the seat built to one side or stopped. Nine; all paged, six contested, read by neither row's owner. "The criterion c_1 states separators=(",", ":") but the test expects spaces after colon; assuming the test expectation is correct"; "The surface_refs for c_2, c_4, c_5 are listed as ::echo, but the criterion text and all criteria are about echo_json".
4. **Scope cut.** The seat left a part of the asked work out and says so. About five. "The confirm function does not exist in the current codebase; its implementation is out of scope for this batch"; "The test files are owned by the Tester and cannot be written by me. I must leave them as-is and assume my implementation is correct".
5. **Blocked by the record.** The block is in a ruling's reach or a relay, not the code. 68. "Adoption of c_6 blocked because the ruling names an ID that exists in criteria but not in glossary_terms"; "constraint b_1 is not found in model".
6. **Tool fault.** A door refused or the environment failed. 27. "body string with quotes/escapes rejected repeatedly"; "two tests in one file overwrite each other on disk".
7. **Trace.** A step, a plan or a state. 65. "Adding default_on_eof parameter to confirm() function signature"; "test body missing assert".
8. **Echo.** A ruling restated by the seat it reached. 221, refused since commit 2dace61b. "The principal contests the criterion, and no action is required here". The Architect's onboarding critiques of page lines sit here too.
9. **Finding.** A judgement on a claim with a source, written by the `challenge.break` door. 24.
10. **Gap.** A mechanical survey gap, one word. 16 fresh.
11. **Unaddressed.** The Principal's answer did not touch the row. 20.

## 4. Per category: the decision, the owner, the merge, the word (reasoned: the composition's lines on who rules, and the owner table in `liaison/answering.md`)

| Category | Decision needed | Who can take it | Should a merge wait | Can the seat name it in one word |
|---|---|---|---|---|
| Invented value | Usually none | The criterion's owner, the Terminologist; the Principal only on request | No | The door names it for tests; a Developer's needs `invented` |
| Default behaviour | Yes | The Principal is final; the criterion's owner can say the criterion covers it first | Opt-in only (the composition: sign-offs after intent are opt-in) | Yes, `default`; the encode door's template must let the seat tell it from a literal |
| Conflict | Yes, before the build, or the build takes a side | The owner of one of the two rows; never the Principal first | Yes: a batch built on an unanswered conflict ships a guess (night 138's `c_1`) | Yes, `conflict`; its record is a message with an owner, not a ledger row |
| Scope cut | Yes | The Vision Keeper owns scope; the Principal is final | Yes, when the cut is of the item's own words | Yes, `scope` |
| Blocked by the record | Yes, by the structure | The build session; the Principal never | No, and the batch does not advance anyway | Yes, `blocked` |
| Tool fault | None in rota | Nobody in rota; one register line | No | Yes, `fault` |
| Trace | None | Nobody | No | No; the door refuses a note that names no choice and no silence |
| Echo | None | Nobody; the guard refuses it | No | No; the door |
| Finding | Yes | The judged row's owner, through the challenge path | No for a merge; yes for an adoption | The door |
| Gap | A reading | The Principal reads | No | The door |
| Unaddressed | The same question again | The Principal | No | The door |

Two things the table says that no note says: only default behaviour and scope cut are owed to the Principal, about 45 of 583, two a night, and night 139's page of seven held zero of them; only conflict and scope cut have a case for a merge to wait, and both wait on a seat's answer, not on a page. So "do the notes block the merge" splits in three: a disclosure never blocks; a question with an owner blocks until the owner answers; the Principal's hold is a third switch that he turns on.

## 5. The grid: how the set generalises

Two questions place any note, and the cell gives its discharge (reasoned: every category lands in one cell; `vision_keeper/deliver.md:23` asks the first already).

| | Chose and proceeded | Could not choose | Did not need to choose |
|---|---|---|---|
| **Owed to the Principal** | default behaviour, scope cut | unaddressed | gap |
| **Owed to a row's owner seat** | invented value, finding | conflict | |
| **Owed to nobody in rota** | | blocked | tool fault, trace, echo |

The first question: if this is wrong, who has to say so. The second: did I pick. The seat does not pick from a list; it answers the two questions and the cell is the kind. The doors keep naming what they name today, and a door never writes an echo. A note in the "owed to nobody" row is not a ledger row: an obligation stays visible until discharged, and a trace was never an obligation. The residue: the Architect's onboarding critiques are findings written as notes because the onboarding modes have no finding call for a line, a mode's defect; the empty cell "owed to an owner, did not need to choose" is the check that the grid is not padded; the 950 Vision Keeper onboarding lines are not placed, so the grid should be tried on a sample before the set is called complete.

## 6. What the categories imply for who answers

- A default or a scope cut is the ledger's own business: a disclosure owed to the Principal, closed by his keypress and nothing else (ruled: DECISIONS 2026-09-03), on the request's page before the merge when he opted in, and in the merged request's state view when he did not (ruled: DECISIONS 2026-09-12, point 2). Law 8's "never saw" is met by "seen", which the page's refs record already (observed: frame 193's 2.F.7). Seen is not ruled; night 139's three sessions were spent because the page asked for a ruling on lines that needed a reading.
- A conflict is a message written in the wrong book. The route should run at log time, from the seat to the owner, with the batch waiting for the answer in the same session (ruled: the composition's Open section). The Developer's answer and exhausted modes lack the call (frame 171). This is the one category where the merge should wait, and it waits on a seat.
- An invented value goes to the criterion's owner as a count, not to the Principal as lines.
- Blocked, tool fault, trace and echo leave the ledger: the first two become one register line each for the build session, the last two are refused at the door or land in the transcript.
- The Architect's review when the Principal opts out: of the eleven categories the Architect can check exactly one by a predicate, a default whose row reaches a constraint's binding (law 12's mechanical intersection). Every other check is judgement, and law 8 forbids a gate on judgement. So the review is a predicate with no model call, joined to the existing structural review. Under the ceiling, the loop that would check an Architect's judgement is the Principal's later amendment, the longest loop rota has.

## 7. The questions for Roman, as stories

1. **[high] The builder's diary and the wall.** A builder puts the socket on the left because the drawing did not say. He writes it in the site diary and the wall goes up. Today the owner must sign every diary line, and when he reads it after the wall is up he can only order the wall redone. The choice: the owner reads the diary when he wants, each line listed until he has read it; or the builder waits at the door with the diary open, on every job, or only on the jobs the owner marks. Recommended: read when he wants, and he marks the jobs where the builder waits. That is the composition's opt-in line, built.
2. **[med] Two builders, one drawing.** The electrician's plan says one thing and the test sheet another. The one who notices writes it in the diary and builds to the test sheet. The choice: the line goes to the owner with the night's other lines; or the builder phones the person who drew the plan and waits before he builds. Recommended: the phone call, and the wall waits, because a guess built in is a guess the owner pays to take out.
3. **[low] Alice.** The tester needed a name and wrote "Alice". Each invented name as a line to approve, or one count per job in the state view with the names a click away? Recommended: the count. Night 139's page of seven held four of these and no decision the owner could make.
4. **[med] The engineer who reviews when the owner is away.** The owner says "do not call me for every wall". The engineer reads the diary before each wall and knocks only when a line touches the building code. The choice: the engineer reads every line and judges, the same junior who files "nothing to see" on most walls today (frame 179: `k0` is the only constraint in every structural review); or a rule picks out the lines that touch the code, with no judgement. Recommended: the rule.
