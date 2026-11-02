# Design: what a principal's drop does to a row the team observed (2026-11-02)

A design page by C76 step 3b for frame 357, after `plans/dry1-turn17-read-2026-11-02.md`. Read-only at bcb03cb5 on `rota/foundation`. The copies `dry1w10` and `dry1w11` under the scratchpad of 066a0dbd were opened with `mode=ro`. The live dry1 database was not opened. No code changed.

## Result

Recommend shape B with shape D: a drop on an observed row lands as his objection on file, the row stays the team's fact, and no seat argues with him or asks him again; separately, the re-survey after a merge goes to the ledger and not to a page (frame 358). Shape B keeps "observed from the code" and "decided by the Principal" as two records, stops work he did not ask for, and keeps the notes visible, where shape A would let one sentence of his remove a commitment that protects outside callers.

Question for Roman: when you tell the team "drop these notes" about notes they wrote down from the code, should the notes leave the team's work, or stay as the team's record with your "not mine" on file and nobody asking you again (recommended: stay, with your objection on file)?

## 1. Four facts the code holds now

### 1.1 How a drop lands, per line kind

The read's section 5 table holds at bcb03cb5 (observed: the lines below).

- A statement ends. `_drop_statements` writes `dropped` on a proposed statement that a landed `contest`/`drop` row names (observed: `rota/roles/principal.py` 3829 to 3849).
- A request item ends. `_item_drops` keeps only the refs where `_is_request_item` is true (observed: principal.py 3858 to 3874). `land` then writes `dropped` instead of `contested` (observed: principal.py 3684 to 3690).
- `_is_request_item` excludes `how_it_works`, an `observed` row, a delivered row and a description (observed: principal.py 611 to 627). So a drop on any of them lands `contested` (observed: principal.py 3687 to 3689).
- A constraint and a glossary term have no reader in `land`. The verdict goes to the Architect and the Terminologist in relay mode (observed: the read, section 1, s290).
- A criterion retires through `_dropped_line`, which reads `grant(conn, id, "drop")` (observed: `rota/roles/api.py` 6865 to 6890).
- The menu offers `drop` on every `other` line and maps it to `("contest", "drop", "row")` (observed: `_MENU_BASE` and `_OPTION_ROWS`, api.py 14335 to 14378). `line_menu` adds `add <quote>` on an item of kind `other` (observed: api.py 14486 to 14508).

### 1.2 What an observed row is, and who writes it

- Provenance is a view over `refs`. A row is `observed` when its refs reach a grain or a reference and no landed ruling or ratified statement (observed: `rota/core/schema.sql` 126 to 166; `rota/LAWS.md` law 11, "found, not chosen").
- The Architect's survey writes the constraints. Its question is "who outside the area would break" when a name is renamed or removed (observed: `rota/roles/prompts/architect/survey.md` 12 to 30).
- The Vision Keeper's orient mode writes the description `how_it_works` with `problem.assert` (observed: `rota/roles/prompts/vision_keeper/orient.md` 13 to 15).
- An observed row becomes `decided` only through `model.adopt` or `glossary.adopt`. `_adopt_rows` writes a `ruling` ref, and only for a row the ruling approves (observed: api.py 2689 to 2731).
- The account page of frame 241 shows the rows that no request owns. `account_rows` and `account_page_refs` pick them, and the Liaison's present door sends them as their own page (observed: principal.py 1837 to 1858; `rota/core/sandbox.py` 4480 and 4955, "ruled: Roman, 2026-10-28 09:10").

### 1.3 What the seats can do with a contested observed row

- The Vision Keeper on `tick:contested` has two routes. It amends with `problem.assert` "when they said what they meant instead", or it defends once with `decisions.author` (observed: `rota/roles/prompts/vision_keeper/contested.md` 11 to 29). It has no route for "no, and nothing instead".
- The Vision Keeper cannot write the end word. `problem_set_approval` refuses `dropped`: "only the principal's drop ends {id}" (observed: api.py 2342 to 2343).
- The Architect leaves a contested constraint `observed`. "A contested row is not yours to fix in this session... With no approved id, end the session with no call" (observed: `rota/roles/prompts/architect/relay.md` 12 to 17).
- The Terminologist does the same. Its first real decision "comes through the challenge path" (observed: `rota/roles/prompts/terminologist/relay.md` 12 to 14).

### 1.4 What reads an observed row into later work

- `constraints_for_grains` loads every global, unbound or unresolved constraint, and every constraint bound to a touched grain. It reads no approval and no ruling (observed: `rota/core/scheduler.py` 3183 to 3219). `model.consult` returns it to the seats (observed: api.py 4486 to 4509).
- `account_page_refs` puts `how_it_works` first and then each owed row not on an open page and not approved (observed: principal.py 1845 to 1858). It reads no drop.
- `observed_entries` puts a row to him once, by the refs of every `present` message (observed: `rota/core/predicates.py` 688 to 702). Its limbo list sends rows of an answered present with no verdict to `do:defer_baseline` (observed: predicates.py 726 to 754).
- `grant` already gives a way back. "a plain approve after a drop ends the drop" (observed: the docstring of `granted`, principal.py 941 to 954).

## 2. The axes

- **Where the end is written.** A status on the row: only items and statements carry one, and constraints have no status column (observed: schema.sql 242 to 249). An `item_parks` row of kind `drop`: the table names `items(id)` only (observed: schema.sql 833 to 841). A `ruled_refs` grant: it exists for every kind already, with no schema change (observed: the read's r_m147 rows; `grant`, principal.py 845). So only the grant covers the four kinds (reasoned: the three tables).
- **What the end means.** Gone from his pages. Gone from the team's work. Or objection on file, with the row kept.
- **Who reads it.** The page builders (`account_page_refs`, `observed_entries`). The loaders (`constraints_for_grains`, `problem.baseline`). The contest path (`land`'s state write, the `contested` predicate, the verdict relay).
- **What the seat is offered on an observed line.** `drop`, a new option such as "not mine", or no such option.

## 3. Candidate shapes

The prices use the anchors of `plans/operating-facts.md` line 250: "a door text or a number, 2; an instrument fix, 3" cycles (observed).

### A. The read's proposal: one end reader beside `_item_drops`

`land` takes each ref that a landed `contest`/`drop` names, and that is no statement and no request item, out of the contest relay. One helper reads the end from `grant(conn, ref, "drop")`. `constraints_for_grains`, `account_page_refs` and the limbo list of `observed_entries` skip a dropped row (observed: the read, section 6).

- Cost: 3 cycles after this page (reasoned: an instrument fix).
- Changes: the rulings door family, because `drop` on an observed row then means "gone from the work". It touches law 12, "Constraints protect external commitments only", because a sentence of his removes a commitment from structural review (reasoned). Needs Roman's ruling.
- Failure: on m145 he wrote "Drop every note and build nothing" (observed: the read, section 1). Under A, `get_current_context`, bound to `src/click/globals.py`, leaves `constraints_for_grains` (observed: its binding on dry1w11). A later request that renames it then passes structural review with no warning, and a program that imports `click.get_current_context` breaks (reasoned: the survey's own question, survey.md 12 to 15). The Liaison also ruled line 1, the description, as a drop (observed: the read, Result item 3). Under A the description leaves the work, and no seat holds the account of the project (reasoned).
- Measure: re-land r_m147 on a writable copy of dry1w10. The `contested` predicate gives 0 wakes (control 1). `constraints_for_grains` over the bound grains loads 0 of the 15 (control 15). `account_page_refs` of the 16 rows gives [] (control 22 refs).

### B. A drop on an observed row is an objection on file

`land` reads the same grant, and for an observed row it writes no approval change and puts the ref in no contest relay. The row stays `observed` and stays loaded. `account_page_refs` and the limbo list skip a row that holds his drop, because his answer is given. The state view and the account section show the row with "you said: not mine". A later approve takes the objection back through `grant`.

- Cost: 3 cycles for `land` and the two page readers. Add 2 cycles if the option on an observed line is renamed from `drop` to "not mine" (reasoned: a door text).
- Changes: the rulings door family, because `drop` on an observed row means an objection and not an end. The rename changes a page form. Needs Roman's ruling. No law changes: law 11's "A challenge to an observed or reasoned entry forces its first ruling" holds, because the drop is that ruling on file (reasoned).
- Failure: he means "this note is false about the code", for example a constraint that names a function no caller uses. Under B the false constraint keeps loading into structural review, and his objection has no reader there (reasoned). The cost is a review wake that is too strict, not silent breakage, by the loader's own rule "degradation lands on expensive, never on wrong" (observed: the docstring of `model_consult`, api.py 4491 to 4494).
- Measure: re-land r_m147 on a writable copy of dry1w10. `how_it_works` keeps `approved` (control `contested`). The `contested` predicate gives 0 wakes (control 1). No `tick:contested` key in `tick_attempts` (control attempts 3, quarantined 1). `account_page_refs` of the 16 rows gives [] (control 22). `constraints_for_grains` still loads 15 of 15, on purpose. Open asks from the turn: 0 (control 4, m152, m154, m156 and m157).

### C. Refuse the drop on an observed row

The menu offers no `drop` on an observed line. The door refuses a ruling `drop` there with a sentence: the row is the code's fact, use rewrite when the note is wrong, or approve.

- Cost: 2 cycles (reasoned: a door text and a menu entry).
- Changes: a page form and the rulings door family. Needs Roman's ruling.
- Failure: m147's "Drop every note" then fits no option. The Liaison clarifies, which is one more ask to him, or picks `other`, which lands `contest` with no act (observed: `_OPTION_ROWS`, api.py 14377). The description then loops to quarantine as on turn 17 (reasoned: the same path, section 1.1). So C alone fails his reply. C works only with a "not mine" option, and that option is shape B.
- Measure: on dry1w10, the door refuses `drop` on the 16 observed lines. The count of turn 17's loop does not move without B (reasoned).

### D. Frame 358 alone: the re-survey rows to the ledger, no end state

After a merge, the rows of a re-survey go to the ledger and not to a present page. No change to what `drop` means.

- Cost: 3 cycles (observed: frame 358's Waits-on line, stack line 1639).
- Changes: the put-once rule of the `observed_entries` predicate. No door family, no prompt shape and no law. No ruling is needed unless it removes the account page (observed: the read, section 6).
- Failure: the first onboarding present and the account page still offer `drop` on observed rows (observed: `_MENU_BASE`). Dry1's m91 was an account page of six onboarding notes (observed: frame 357's Site line). A drop there lands as on turn 17, with no end and a loop on the description (reasoned).
- Measure: on dry1w10, the merge of bg_1 gives 0 present pages of survey rows (control: m145, 16 rows). On the nights, survey presents after a merge, from 11 pages on 7 of 9 merge nights toward 0 (observed: frame 358's Site line).

## 4. Control: the dry1 copies under the current code

From `scratchpad/f357d/control.py` of session 208997ee, run on both copies with `mode=ro` (observed).

| Reader | dry1w10 (before turn 17) | dry1w11 (after turn 17) |
|---|---|---|
| Refs with a landed `contest`/`drop` | 12 | 30 |
| Of them, observed constraints | 0 | 15, all `observed`, basis `code` |
| Of them, observed items | 0 | 1, `how_it_works` |
| `how_it_works` approval | `approved` | `contested` |
| `grant(how_it_works, "drop")` | none | yes |
| Dropped constraints loaded by `constraints_for_grains` over every bound grain | 0 | 15 of 21 loaded |
| `account_page_refs` of the dropped refs | 6 | 22, `how_it_works` first, the 15 constraints among them |
| `contested` predicate | no wake | 1 wake, `vision_keeper`, `how_it_works` |
| `tick_attempts` on the contested key | none | attempts 3, quarantined 1, reported 1 |
| `observed_entries` | no wake | no wake (put-once holds) |
| Open asks to him | m144, m145 | m152, m154, m156, m157 |
| `item_parks` | 1 row, kind `now` | 1 row, kind `now` |

The grant is already on file for all 16 observed rows. So shapes A and B need no new write, only readers (reasoned: the table).

## 5. Recommendation

Build D first and B next, after Roman's ruling on the meaning of drop (reasoned: D needs no ruling and removes turn 17's page at the source; B covers the reach that D leaves, the onboarding page and the account page).

The reason, in the composition's words (observed: `plans/composition.md`):

- "The structure holds a model of its shape... as records observed from the code. The Principal holds the shape in their head." His drop cannot change what the code does. Under A, the team's model of the code then disagrees with the code (reasoned).
- "A record says whether it was observed from the code or the world, reasoned by a seat, or decided by the Principal." Under B, the observed row and his objection are two records with two writers. Under A, his ruling overwrites a fact that he did not observe (reasoned).
- "no work happens that the Principal did not ask for". Under B, no seat defends a row he refused, and no clarify returns. Turn 17 made three defends, three clarifies and a repeat page (observed: the read, section 1).
- "and no work stays invisible" and "Nothing stops quietly". Under B, the row and his objection stay visible and countable (reasoned).
- "The tool never rules for the Principal". Under B the tool reads his drop as he gave it and does not widen it into a removal from the work (reasoned).

The review of frame 357, H1, found that a dropped description "becomes an account row" and that "Nothing writes an item back from `dropped`" (observed: `plans/f357-review-p2.md` lines 23 and 36). Shape B writes no `dropped` status, and a later approve takes the objection back through `grant`, so H1's reason does not apply to B (reasoned).

Left out of both shapes: the Liaison's over-read of "every note" onto line 1 and the read-backs, the false footer "'ok' approves all of this and starts building", and the side finding on m146 (observed: the read, section 6).

### The question for Roman, in plain words

The situation: you asked for one change, the team built it, and it merged. After the merge, the team read the whole project again. They wrote down fifteen notes about the code, such as "other programs call this function by this name, so do not rename it". They also kept their one paragraph on how the project works. They showed you all of it. You answered: "I asked for none of these notes. Drop every note and build nothing."

What happens today: the notes stay in the team's work, and the paragraph is marked as disputed. The team member who owns the paragraph tries to defend it three times. You get three questions back and the same page again.

What happens next, option 1, the notes leave the work: nobody asks you again. The team forgets that other programs call that function. A later change can rename it with no warning, and those programs break. To get a note back, you approve it on a later page.

What happens next, option 2, the notes stay with your objection on file: nobody asks you again and nobody argues with you. The team keeps the notes as its record of what the code does, and you see "you said: not mine" beside them. A later change that touches that function still gets the warning. If a note is wrong about the code, you say "rewrite" and the team corrects it.

Recommended: option 2. The notes describe the code and not your request, so your "not mine" belongs beside them, not in place of them.

## Usage

About 125k tokens on this agent's counter, against a cap of about 80k (observed: the session's token counter, start to the page write). The control probe is `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/208997ee-71a2-496f-83aa-e1425ff49524/scratchpad/f357d/control.py`.
