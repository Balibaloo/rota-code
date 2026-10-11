# Frame 204 corpus read: the seats' ledger notes, nights 120 to 139

Read-only, Opus, 2026-10-11 15:20, an agent of session be3ef742, 144.7k on the harness line against 120k. The harness refused the report write, so this file is the report as returned, less the per-night table and the example lists, which the scripts regenerate: `extract.py`, `dump.py`, `classify.py`, `examples.py`, `notes.json` and `classified.json` under the session scratchpad `corpus204/`, with the database copies in `corpus204/db/`. Rota workflow.

## 0. The corpus

- The 872 rows hold only 583 fresh notes. Each night starts from a snapshot, so 289 rows are the same id with the same writer session, carried into a later night (observed: `l_a8c3fa9360` has writer `s87` on 16 nights). Fresh is the honest unit.
- Night 134 has no database. Night 129 exists only as `clickI_night129_partial.db`, and the read includes it.
- Fresh notes per author: architect 184, tester 154, terminologist 119, developer 66, liaison 36, critic 24 (observed).

## 1. The masses

Rules written in `classify.py` after a read of all 616 texts that are not gap labels, grouped by author. Masses C, D and F each hold about 5 to 8 misfiles (reasoned: hand check).

| Mass | Rows | Fresh | What it is |
|---|---|---|---|
| A gap label | 256 | 16 | One word (`term`, `surface`, `prose`, `source`) about an onboarding area. No content. |
| B dictated literal | 115 | 103 | "the test assumes X where the material is silent". A `tests.encode` refusal dictates the text. |
| C real choice | 39 | 39 | A pick under silent criteria, in the seat's own words. This is the ledger's stated purpose. |
| D tool fault | 120 | 95 | A refusal, a failed tool or a missing row, written as a note. |
| E ruling echo | 233 | 221 | A seat on a relay wake restates or guesses why the principal ruled. |
| F work log | 65 | 65 | Intent, progress, diagnosis or status. No choice. |
| G critic falsified | 24 | 24 | Written by the `challenge` code, not by a seat's `ledger.log`. |
| H unaddressed question | 20 | 20 | `kind = unaddressed_answer`: "the answer did not address the question: ...". |

Per author, in rows: Liaison A 256, H 20. Tester B 115, D 37, F 19, C 19. Architect E 171, D 25. Terminologist E 62, D 47, C and F 10. Developer C and F 56, D 11. Critic G 24.

Mass E is a burst on nights 133 to 136, 207 of 221 fresh notes, and falls to 1, 4 and 0 on nights 137 to 139 (observed). Commit `2dace61b` (2026-10-09) added the door that refuses a row about a ruled row, and the architect relay brief now says "Do not log an assumption about it". `rota/roles/prompts/terminologist/relay.md:14` still says "If the contest tells you an assumption you made, `ledger.log` it" (observed: `git log -S`).

Examples, verbatim, fresh rows (observed). B: "the test assumes 'Are you sure?' and 'custom_default' where the material is silent" (n127); "the test assumes lambda x: x where the material is silent" (n128). C: "The criteria are silent on how to append the Python version string. I assume it should be appended directly after the existing %(version)s placeholder" (n132); "echo_json must be a Click command to work with CliRunner.invoke(), even though criteria only specify output format requirements" (n126); "The criterion c_1 states separators=(",", ":") but the test expects spaces after colon; assuming the test expectation is correct" (n138); "EOF simulated by empty StringIO, not closed stdin" (n120). D: "Cannot encode test for echo_json_compact due to parsing limitations in tests.encode tool; body string with quotes/escapes rejected repeatedly" (n120); "Principal ratified e_p13 for adoption but row does not exist; no creation tool available to instantiate it" (n132); "The principal contested this constraint, but it is not a row in model_areas" (n136). E: "The principal ruled to contest this term because lines 1-3 are vague sentences" (n133); "group refers to a collection of related items or entities" (n135); "The principal contested all seven constraints, and none of them are approved for adoption" (n136). F: "Adding default_on_eof parameter to confirm() function signature" (n131); "All three criteria for the confirm() EOF behavior have been specified" (n136). G: "the Critic falsified items:echo_json_compact_v2 against @claim:items:echo_json_compact_v2: the probe for def echo_json returned an empty list" (n126). H: "Should the 'version_option_show_python' flag be implemented in this change, or is it a separate request?" (n133); "Should echo_json(obj) be added as a helper next to echo?" (n136).

Synthesis (reasoned: from the counts). A real pick in the seat's own words appears in 39 of 583 fresh notes, 7%. Three forces fill the rest: doors dictate the text (the `tests.encode` refusal writes B, the `challenge` code writes G); a relay wake turns a ruling into a row about that ruling (E); a seat that a tool refuses has no other place to put the refusal, so the refusal becomes a note (D). The ledger is the only free-text channel that a door accepts from a seat, and the seats use it as one.

## 2. Two kinds

Rule: a question for the owner asks something and names a row that exists in its `about_table`; a working note asks nothing; "neither" holds the rest.

| | Rows | Fresh |
|---|---|---|
| question for the owner | 54 | 54 |
| working note | 539 | 490 |
| neither: no content | 264 | 24 |
| neither: asks, names no row | 15 | 15 |

The 54 questions are G 24, H 20, E 8 and C 2. 44 of the 54 come from code paths, not from a seat's `ledger.log` (observed: G from `api.py:10183`, H from `kind = unaddressed_answer`). So a seat's own note asks its owner something in about 10 of 563 fresh seat notes. The split needs a third kind: a fault report to the operator; most of D belongs there (reasoned: D asks nothing of the row's owner).

## 3. Who ever read them

| Mass | Rows | Paged | Approve / contest / revise | Open at the night's end | Seat read-back |
|---|---|---|---|---|---|
| A | 256 | 256 | 209 / 47 / 0 | 0 | 18 (carried rows only) |
| B | 115 | 96 | 68 / 18 / 0 | 19 | 1 |
| C | 39 | 35 | 27 / 7 / 0 | 4 | 0 |
| D | 120 | 103 | 64 / 38 / 0 | 17 | 0 |
| E | 233 | 198 | 29 / 164 / 4 | 36 | 0 |
| F | 65 | 57 | 48 / 5 / 2 | 8 | 2 |
| G | 24 | 22 | 18 / 4 / 0 | 2 | 0 |
| H | 20 | 18 | 5 / 12 / 0 | 5 | 1 |

496 of 583 fresh notes reached a page to the principal, 85%. Tool faults reached the principal as assumptions to approve: 103 D rows were paged and 38 got a contest. E drew 164 contests out of 197 rulings, and each contest woke a relay seat that wrote the next E row; the comment near `api.py:7822` records the same loop on night 136, "117 of 213 lines on the agenda pages were such rows". A seat read a note back in a later wake for 4 of 567 fresh notes that are not gap labels: no seat used a note as input to its next decision, except through the principal's page. No `challenges` row names a ledger id (observed).

## 4. The faults

D holds 120 rows, 95 fresh. B is a fault class too: a `tests.encode` refusal in the same session dictates the exact text of all 103 fresh B notes (observed: "the test chooses" appears in the writer's turns for 103 of 103). The B door, verbatim from `api.py:6990`: "the test chooses {named}, and nothing in the criterion, its ticket, the glossary or the principal's words says it. That is an assumption, and it is logged where it is made: ledger.log(...) -- then send this encode again unchanged". A sibling door at `api.py:6958` dictates "the test assumes {uses_return} returns what it prints".

| Door | Fresh D | Refusal text quoted |
|---|---|---|
| `glossary.adopt`: the ruled id is not a glossary row | 44 | "adopt what the ruling names"; "no creation tool available"; "The tool refuses to invent an ID" |
| row lookup: the ruled ref is not a row | 24 | "it is not a row in model_areas"; "constraint not found because it was not loaded" |
| `tests.encode` parse and escape | 9 | "body string with quotes/escapes rejected repeatedly" |
| `tests.encode` import path | 3 | "the error message insists on click.decorators" |
| test-file ownership and test write | 8 | "owned by the Tester and cannot be modified by me"; "two tests in one file overwrite each other on disk" |
| `code.write` | 3 | "code.write is unavailable"; "code.write calls failed due to parsing issues" |
| pytest stdin and harness | 2 | "a harness bug, not a code bug" |
| other or misfiled | 5 | "duplicate specification attempts were rejected" |

In the writers' turns for D and E, `ERROR ledger.log:` occurs at least 24 times, and a pre-filled assumption, "The principal contested this constraint, but it is not a row in model_areas.", occurs 216 times across prompts.

## 5. Cost to catch a wrong assumption before a merge

| Mass | Fresh | Must read | Why |
|---|---|---|---|
| A | 16 | 0 | One word; the assumption is on the page. |
| B | 103 | about 30 | 30 name a behaviour, an exception type, a default or a return type; 73 name only prompt strings or dictionary keys. |
| C | 39 | 39 | Each pick goes into the diff; one contradicts a criterion (n138, separators). |
| D | 95 | about 3 | Faults are for the operator; three hide a pick. |
| E | 221 | about 10 | About 7 invent a sense; the rest repeat the principal. |
| F | 65 | about 5 | A few hide a pick inside a plan. |
| G | 24 | 24 | Each is a finding against a claim. |
| H | 20 | 20 | Each is an open question. |

About 131 of 583 fresh notes, 22%, need a reviewer before a merge, and about 452 can be skipped from the text alone (reasoned: the column's sum). Most of the 131 are the seats' own picks (C), the behavioural third of B, and the two masses that code writes (G and H), which already reach the principal.
