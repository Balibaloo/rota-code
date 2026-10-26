# Frame 293's rulings ledger, matched by cause against his ruling on a ref, 2026-10-26

Rule C76 step 4. Read only, at 328ae4b4. The issue: his words and verdicts on a page sit as free text in the rota `rulings` table, and about 20 readers re-derive what he ruled (`plans/frame339-reach.md` lines 19 to 45, P1 to P11, C1 to C5, S1 to S4). The candidate: frame 293, `plans/archive/stack-2026-10-18.md` lines 3 to 15.

## The result

Frame 293 is not a match. It matches the shape and not the layer (reasoned: sections 1 and 2). Its ledger holds the build session's rulings from Roman, keyed by search words, in a Markdown file. The 20 readers need the Principal's ruling on one ref of one page, in the register, at the time a door runs. No reader in `rota/` can read the ledger, and the ledger has no ref (observed: section 3). The ledger's entry form does carry the split that the composition asks for, verbatim words beside a reading marked confirmed or reasoned. That form is the one lesson to copy (reasoned: section 4).

## 1. What frame 293 built and left unbuilt

- `rota/tools/rulings.py`, 293 lines at head: the search by words, `file`, `door`, `law` and `frame` over the ledger, the laws, the roles, the decisions, the briefs, the archive and the night reads (observed: f0ee0424, 276 lines and 11 tests). `--wide` adds `plans/*.md`, the brief and the composition (observed: 39472e4d, 12 tests). `tests/rota/test_tools_rulings.py` holds the tests (observed).
- `plans/rulings.md`, 358 lines, 44 entries R1 to R44 (observed: dca17dd0). Each entry has `Keys:`, `Situation:`, `Said:`, `Means:`, `Rule:` and `Supersedes:` (observed: lines 7 to 13). R1 to R20 date 2026-09-03 to 09-30, R21 to R44 date 10-01 to 10-10 (observed: the stack, 01:45 and 01:56).
- 13 `Means:` lines are his confirmed reading, 2 of them in part, and the rest are the agent's, marked (reasoned) (observed: the stack, 01:45 and 01:56; `plans/rulings.md` lines 100 to 348).
- Unbuilt: the full back-fill, any writer after 2026-10-10, and any reader of the ledger (observed: the stack, 01:58, "The full back-fill is not pushed"). `plans/method/design.md` lines 98 to 101 keep the search and rule "No ledger" (observed).
- The verdict: by the asker's words 0 of 11, by structural keys 2 of 11 in part, both by the frame number (observed: `pass4-report.md` as quoted in the stack, 01:58). The reports `f293/*.md` are not in the repository (observed: `find`).

## 2. Is the ledger the structured record per ref

No, in whole and in part (reasoned). The two records differ on each axis.

| Axis | `plans/rulings.md` | What the 20 readers need |
|---|---|---|
| Who rules | Roman, to the build session (observed: R1 to R44) | The Principal of a night, to the Liaison (observed: `schema.sql` 663 to 670) |
| Key | free `Keys:` words and the frame number | a ref: a criterion, a page line, an item, a test row (observed: `per_item`, `schema.sql` 674) |
| Store | Markdown under `plans/` | the `rulings` table in the register (observed: `schema.sql` 671) |
| Reader | a session or an agent by search | a door at run time (observed: `frame339-reach.md` table) |
| Verdict | none per ref | approve, contest or revise per ref (observed: `principal.py` 45) |
| Target and act | none | the line or path, and drop, keep, rewrite or add (reasoned: `frame339-reach.md` line 72) |

The two share the shape "a fact held once as free text, re-derived by N readers" (observed: `plans/agency-groups-2026-10-26.md` line 7). The fix of one cannot serve the other (reasoned).

## 3. Which readers could read the ledger today

None of the 20 (observed: `git grep` finds no reader of `plans/rulings.md` in `rota/` outside `rota/tools/rulings.py` and its test). Against the record the readers need, the existing `rulings` row already serves the verdict part (observed: `frame339-reach.md` line 72, `_ruling_texts`, P6, P7 and P10 gate on `per_item` first). The columns the row lacks:

- An act and a target: P1, P2, P3, P6 (the drop), P7, P10 and P11, seven of eleven permission readers (reasoned: `frame339-reach.md` line 72).
- A target only, a page line or a source line: P4, P5, S1 to S4, and C1 and C5 by `_LINE_REF` (reasoned: the table; line 49, "one pattern serves two meanings").
- The span of his words per ref: P8, P9 and C4 (reasoned: they read the added or named words, not a verdict).
- C1 to C5 stay as checks of the record against his words, not as readers of it (reasoned: `frame339-reach.md` line 72).

## 4. The composition's "confirmed reading is a second record"

The ledger implements the split for the build session only, by hand: `Said:` holds the words, and `Means:` holds the reading marked confirmed or reasoned (observed: `plans/rulings.md` lines 4 and 100). The ledger does not implement it for rota (reasoned: section 2). In rota, `messages` holds the words, `rulings.words` holds a copy, and `per_item` holds the Liaison's reading (observed: `schema.sql` 663 to 685). No column marks the reading confirmed, and grep finds no step that shows the reading back to the Principal (observed: grep "read back", "confirm the reading" in `principal.py`, `api.py`, `runner.py`). `ROLES.md` 67 to 69 asks for that check (observed).

The one record per ref would carry (reasoned):

1. `ref`: the row it rules, as `per_item` keys it today.
2. `verdict`: approve, contest or revise.
3. `act`: drop, keep, rewrite, add or remove, null on approve.
4. `target`: a page line, a source path and line, or an identifier, with its kind.
5. `words`: the verbatim span of his reply that rules this ref, checked by group 1's span rule (`agency-groups` line 13).
6. `confirmed_by`: the message id of his reply that confirms the reading, or null. Null never reads as approval, because "silence approves" is gone (ruled: 2026-09-13, `plans/rulings.md` R3).

## 5. The proposal

1. Close group 2 first as one pass in order 337, 338, 322, with no new column: one reader of `rulings` by ref, at 9 to 10 cycles (observed: `agency-groups` lines 51 and 61).
2. Then a seam with its own night: the Liaison's `rulings_rule` call writes `act`, `target` and `words` per ref, and C1 to C5 check them (reasoned: `frame339-reach.md` line 72; the call form changes the brief, so cassettes re-record).
3. P1 to P11 read `act` and `target` in place of their patterns, seven at once (reasoned: line 72). Count the night's refusals before and after (ruled: `wall-guide.md` section 3, "the count").
4. `confirmed_by` waits for Roman: a read-back costs his attention on each reply, and the composition puts that attention first (reasoned: `composition.md` line 22).
5. Price: the pass 9 to 10 cycles, the seam about 4 cycles and one night, about 14 in all. Frame 293's tool and ledger are reused for nothing here (reasoned: the anchors in `operating-facts.md`, 10k a cycle).

## 6. The doubt

1. I did not read the 20 readers' code. The column map of section 3 rests on `frame339-reach.md` and its line 72 (reasoned).
2. The read-back may exist under a word I did not grep, such as the sign-off page approve (reasoned: one grep of three files).
3. The seam price of 4 cycles has no anchor of a schema and brief change in one frame (reasoned).
