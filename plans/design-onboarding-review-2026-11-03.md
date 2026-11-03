# Review: the design of onboarding, 2026-11-03

Reviewer: one read-only agent at bce7cf48 on `rota/foundation`. Page: `plans/design-onboarding-2026-11-03.md`. No model session started. One file written, this page. The probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/ce483c7b-be58-4d58-bfc4-db1081518842/scratchpad/review362/`.

## Result

Revise. High 4, medium 5, low 3. The direction of design B stands. Four faults change what Roman decides or what gets built.

High:

1. The page omits the `lazy` election that exists. `rota elect lazy` already sends every observed row to the ledger "awaiting first touch" (observed: cli.py 798 to 804, predicates.py 777 to 792). Question 1 misstates the ruling of 2026-08-26 as "the first picture is your call". The ruling is that the choice between `eager` and `lazy` is his. Fix: name `lazy`, recast B as `lazy` made the default plus a touched-area read, and split question 1 in two.
2. The cost basis is wrong by about three times. Of the 112 onboarding minutes on dry3, about 74 are three runaway sessions: s174 at 33.3 min (gemma4:12b), s194 at 31.4 min (a re-survey of `.` after the merge), and s175 and s176 at 9.7 min. Before the first delivery the run spent 37.6 min. The first survey of 22 areas took 13.9 min, 0.63 min an area, not 2.1 (observed: `turns.ms` per session on dry3w7). Fix: restate the cost from the per-session table. B saves about 30 min on icalendar, not 104. Correct "most of the day" in question 1.
3. Under B, the project-level commitments never reach a touched source file. Four of the five key witnesses are root files: pyproject.toml lines 42 and 80, `[project.scripts]` and the `__init__.py` exports. The rule "a commitment binds every path its witness names" binds `rfc_5545_conformance` to pyproject.toml and README.rst only. A change to `parser/string.py` then gets no RFC push, and the slice demand pass fails (reasoned: the witness lines, observed). Fix: write a binding rule for a project-level commitment, for example every source path of the package, and price it.
4. "Neighbours" has no definition that holds on the edges. The 313 edges are file imports through `__init__.py`. `parser/string.py` has 1 in-edge and 0 out-edges, and `caselessdict.py` has 0 edges. At area level, `src/icalendar/parser` has 10 neighbour areas, and `src/icalendar` has 13 of 22 (observed: `code_edges` on dry3w7). So the rule reads either one area or half the project, and the cap of four has no choice rule. Fix: define neighbours as the callers of the touched symbols through the re-exports, rank them, and measure the rule on bg_1 and on the fold sentence.

Medium:

5. The harvest kinds miss one witness and harvest the trap. The `vBroken` behaviour is in docs/how-to/parse-errors.rst lines 46 and 47, which hold none of "standard", "compatible" or "supports". Tests are not a kind, and the exports give a name only. docs/explanation/api-design.rst line 61 and parser/content_line.py line 285 say "75 characters" (observed: grep on icalendarI). Fix: add a docstring kind and a docs kind for preservation, show contradicting witnesses side by side, and score the yield and the noise.
6. The Critic exception conflicts with a second Critic rule. critic/base.md line 10 says "Do not fail a diff for a purpose you read in a docstring or a comment" (observed: 13d138b2, 2026-10-01). The fold witness is a docstring and the #1501 witness is a comment. Fix: name both sentences and the register cases that 13d138b2 taught.
7. The slice is under-priced. B prices the record kind and the push door as a seam at 8 to 10 cycles, and the slice prices the same work at 2 to 3. The slice is about 16 to 19 cycles, near the twenty that one session holds. B at 25 to 30 cycles needs more than one session, and the page does not say so (reasoned: operating-facts line 250). Fix: price the slice at 16 to 19 and B at two sessions.
8. The slice measure cannot tell the push from the request. The sentence names "the 75-octet limit", so the Tester can write the octet test from the request alone. The seeded `limit=76` break falls inside the scope that the request opens. The rule for C leaves 3 of 5 with no outcome. Fix: use "fold long lines at a space" with no limit named, seed a break outside the request, and decide the case of 3 of 5.
9. Question 2 has no provenance. It departs from the purpose line "no work happens that the Principal did not ask for" (ratified 2026-09-16) and from the Critic rule of 2026-10-01. Fix: open question 2 with the ruling, its date and the departure.

Low:

10. "A later request on the same area: 0" is true only while the area hash holds. After a merge the area is read again, and on dry3 that re-read cost 31.4 min (observed: s194). Fix: show the re-read cost in the table of 3.6.
11. Question 3 needs no ruling. Fix: move it to a notice under the recommendation.
12. The cut of `define` over the whole lexicon keeps one sense per area. A touch over two areas can still write one word twice (reasoned: key score section 3). Fix: add one line in 3.4 that the touched-area define reads the existing senses first.

## 1. Claims against sources

Verdict: stands on the doors, the ledger rows and the session counts. The minutes figure stands as a sum and misleads as a cost (finding 2).

- The lookup door reads the wake refs as glossary ids, and it returns "the rows this wake named are gone." (observed: api.py 3662 to 3669).
- `batch_start.tools` holds `model.load` and no `model.consult` (observed: the file).
- `k0` has 0 bindings and is the one unbound constraint. `constraints_for_grains` adds every unbound constraint, "unbound = global" (observed: p1.py on dry3w7, scheduler.py 3196 to 3203).
- The ledger holds 16 open `conflict` rows. `l_bf39c83516`, `l_4bf2fc80bb` and `l_7dba4c3acc` hold the three quoted claims (observed: p1.py).
- `icalendar_caselessdict` binds two docs paths and no source path (observed: p1.py). 108 of 122 bindings name a `src/` path, so "empty" holds for the touched paths only (observed).
- The onboarding wakes sum to 154 sessions and 111.6 min of 206 sessions and 131.5 min (observed: supply.py). Three sessions hold about 74 of the minutes (observed: per-session sums, finding 2).

## 2. Both ways

Verdict: stands in the main. The demand comes from the briefs, and the supply comes from the index and the harvest. Two gaps exist.

- The description has a weak consumer. The page says so in its doubts. No change is needed (reasoned).
- The harvest has no measured yield. Section 4.1 lists witness lines that a person found, not lines that a tool produced. My approximation finds 4 numeric defaults in modules that cite an RFC, 88 claim lines in 18 docs files and 7 issue comments in `src/` (observed: harvest.py). The yield on click and tips is unread (finding 5).
- The "challenge verdict" row has a consumer only by the design. On dry3 no seat read a verdict (observed: the demand read, section 4). The page does not mark the row as supply that waits for its first demand (reasoned).

## 3. Design B, the harvest

Verdict: partly real. A tool with no model finds four of the five commitments with a behaviour line, and the fifth as a bare name (observed: grep and harvest.py on `D:/repos/_AI/sample_repos/icalendarI` at 4f12af1e, the merge of bg_1 on 99619246).

| Commitment | What a deterministic harvest finds | What it cannot do |
|---|---|---|
| `rfc_5545_conformance` | pyproject.toml line 42, README.rst line 5, docs/index.rst line 7 | Bind the claim to `parser/`, `cal/` or `prop/` |
| the 75-octet fold, prediction 3 | string.py line 119 `limit: int = 75`, the line 122 docstring "75 octets", the #1501 comment | Prefer "octets" over "characters" in api-design.rst line 61 and content_line.py line 285 |
| `the_pypi_package_and_import_surface` | `requires-python`, `__all__` in `__init__.py` line 101 | Say which exports are shortcuts that importers use |
| `tzdata_and_dateutil_are_load_bearing` | pyproject.toml lines 78 to 80, "required on Windows", README.rst line 18 | Bind the dependency to `timezone/` or `prop/recur/` |
| `unknown_content_survives_round_trip` | `vBroken` in `__all__` | Find parse-errors.rst lines 46 and 47 with the kinds as written |
| `the_cli_preview_entry_point` | `[project.scripts]`, lines 139 and 140 | Nothing is missing |

The harvest finds the source lines. It cannot bind a root-file claim to a source path, and it cannot choose between two lines that contradict (reasoned: the table).

## 4. The blast radius

Verdict: revise (finding 4). The index holds `fan_in` per grain and file import edges (observed: `pragma table_info(code_index)`, `code_edges`). The edges stop at `__init__.py` re-exports. The real caller of `_foldline` is `parser/content_line.py`, and the edge table shows only `parser/__init__.py` (observed: grep, edges.py). So the Architect and the Tester get the dependents of a touched file only through the area rule. The area rule is too wide: `src/icalendar` reaches 13 of 22 areas (observed: edges.py).

## 5. The principal

Verdict: stands, with one change. He gets the description, the touch line, his questions and the Done line (reasoned: 3.5). Frame 361 needs no new ruling, because `rota elect lazy` answers it today, and the dry3 wall read says so (observed: dry3-wall1-read line 82). Frame 358 and the four term pages are answered by B only if question 1 says "the team rows never come to you as a page" (reasoned). Under `lazy`, each row waits "awaiting first touch", and the touch line of B is that first touch (reasoned: cli.py 803).

## 6. Costs and the slice

Verdict: revise (findings 2, 7, 8). Line 250 prices a cycle at about 10k of the context of the holding session. A seam with its night is 8 to 10 cycles, and a session holds about twenty (observed: operating-facts line 250). The page applies the shapes to A and to B, and then prices the same seam at 2 to 3 in the slice (observed: sections 3.B and 4.2). The sentence, the commitments and the pass are written, and the run is possible on the survey of today. The measure does not separate the push from the request (finding 8).

## 7. What the page leaves out

- The partition drift and the key re-cut: in the slice, step 7. Stands (observed: 4.2). B depends on areas more than today, because the neighbour rule reads areas (reasoned: finding 4).
- The term self-duplication: B cuts the pages, and the cause stays (finding 12).
- The survey cost on large projects: overstated (finding 2).
- The doors repair as a prerequisite: the page puts the lookup fix first. Stands (observed: section 5). The `model.load` door and the `k0` fix sit inside the push of B. Stands.
- The `lazy` election: absent (finding 1).

## 8. The questions for Roman

Verdict: revise.

- Question 1 holds two decisions, the scope of the reading and the end of the approval page. The `lazy` election already answers the second (finding 1). The question misstates its ruling. Its story says "most of the day", and the reading before the first delivery took 37.6 min (finding 2).
- Question 2 is plain, one situation, and needed. It has no provenance (finding 9).
- Question 3 is not needed now (finding 11).

## Probes

All in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/ce483c7b-be58-4d58-bfc4-db1081518842/scratchpad/review362/`, read-only, `mode=ro`:

- `p1.py dry3w7/dry3.db`: the `conflict` rows, the `k0` bindings, the unbound constraints and the `caselessdict` bindings.
- `edges.py dry3w7/dry3.db`: the edges and neighbour areas of the touched files.
- `harvest.py D:/repos/_AI/sample_repos/icalendarI`: an approximation of three harvest kinds.
- Inline: `demand/supply.py` on dry3w7, per-session minutes of the survey and account wakes, area-level neighbours, grep for the witnesses, and `git log -S` on the Critic rule.

## Usage

About 80k input tokens and 18k output tokens, about 98k in total, and 34 tool calls. Two failed writes of the whole page cost part of the output. No model session, night, gate or dry run started.
