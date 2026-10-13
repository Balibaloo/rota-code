# Frame 213 with candidate C, the scope read (2026-10-13 15:37)

Read-only scope read on Opus, for session e669185f. Code read at 17e67ca3.
Databases opened read-only: night 145 (`scratchpad/n145/clickI_night145.db`)
and night 144 (`.rota/clickI_night144.db`). Every statement is about the rota
workflow, the seats, unless it says meta workflow.

## 0. The answer in brief

1. The principal's words about a check reach no Tester on 11 of 11 cases.
   The cases take three routes, not one (observed: `messages`, `rulings`,
   `sessions`, `turns`, nights 144 and 145, 2026-10-13).
   - **Route A, the criterion relay drops the words: 6 cases** (m142, m171,
     m186, m246, m256, m261). The page's check line stands under a criterion
     line. The Liaison rules the criterion. The relay reaches the
     Terminologist with `principal_said`. The Terminologist respecifies the
     criterion and answers the Tester with refs and no text. **The Tester
     wakes in all 6** (s273, s322, s341, s417, s431, s439), but its wake has
     no `principal_said`, so it rewrites the test from the criterion text
     alone.
   - **Route B, a test row goes to the Vision Keeper: 4 cases** (m182, m242
     of night 145, m312 and m400 of night 144). The page is a clarify with a
     `tests` row in `about`. The Liaison rules the test row. The relay split
     knows no owner for a `tests` row, so the row goes to the Vision Keeper,
     which calls `problem.set_approval` on the test id. No Tester wakes.
   - **Route C, the whole ruling is refused: 1 case** (m316/m317, night 144).
     The Liaison put `contest` on line 8, the batch line `bg_4` with a head
     commit. `rulings.rule` refused the ruling 3 times. No ruling landed and
     no relay went out.
2. The read's sentence "no Liaison relay reached the Tester" is true, and it
   is also structural: `rota/design/graph.json` has relay edges from the
   Liaison to the Terminologist, the Architect and the Vision Keeper only
   (observed: graph.json at 17e67ca3, lines 998-1014). A Liaison relay to the
   Tester is a new edge, which is a composition change.
3. The three original sites of frame 213 (the relay refusal, the cancelled
   batch's check line, the exhaustion quote) touch **0 of the 11 cases**.
   The relay refusal fired in 4 sessions of night 145 and 2 of night 144,
   all Terminologist `msg.answer_tester` calls, none on the 11 cases.
   Night 145 had 0 cancels.
4. Recommended fix shape, inside the composition: carry the ruling's words
   on the Terminologist's answer hop (route A), and route a `tests` row of a
   ruling to its criterion's writer as a criterion relay (route B). Route C
   is another frame's wall.

## 1. The eleven cases

All rows observed in the night databases on 2026-10-13. "Wake has words"
means the string `principal_said` is in the Tester's first prompt.

| case | night | page | principal's words (head) | line ruled on | ruling | relay | seat that woke, what it called | Tester | route |
|---|---|---|---|---|---|---|---|---|---|
| m142 | 145 | m141 present, bg_3 | "I want this fixed, not dropped. Line 3's check only shows the option exists, so it should run the version option with the flag on and check that the message ends with the Python version written as major.minor.micro." | criteria cr_1..cr_3 (check lines under them) | r_b29281299a: cr_1 contest, cr_2 revise, cr_3 contest, bg_3 approve | verdict m143 -> Liaison s271 -> relay m144 to Terminologist | s272: 3x `criteria.respecify`, `msg.answer_tester` (m145, no text) | s273 woke, no words, ~30 `tests.encode` | A |
| m171 | 145 | m170 present, bg_3 | "Line 3's check is wrong because the flag belongs to the decorator, not the command line." | criteria | r_b33e2979e0: cr_1 contest, cr_2 and cr_3 revise | m172 -> s320 -> m173 to Terminologist | s321: respecify x3, answer m174 | s322 woke, no words, 10 encodes | A |
| m182 | 145 | m179 clarify about cr_2, tst_version_flag_append and 4 decisions | words in r_8644c74038: "Yes, change the version option decorator so it accepts the flag. ..." | the test row | tst_version_flag_append approve | m183 to Terminologist (cr_2), m184 to Vision Keeper (the test and 4 decisions) | s335 `glossary.adopt`; s336 `problem.set_approval approved` on the test, `problem.prioritize` | none | B |
| m186 | 145 | m185 present, bg_3 | "Lines 3 and 4 probably fail because the test command gives no version ... Give the test command a fixed version such as 1.0" | criteria | r_00a80e9257: cr_1..cr_3 contest | m187 -> s339 -> m188 | s340: respecify; cr_3's text then reads "outputting a fixed version such as 1.0" | s341 woke, no words, re-encoded from the garbled criterion | A |
| m242 | 145 | m241 clarify about cr_2_cr_3 format, tst_version_flag_format | "The test is wrong, not the code, because the version option only adds a version option to a command and never returns a message itself." | the test row | tst_version_flag_format contest, criterion approve | m243 to Terminologist, m244 to Vision Keeper | s412 `problem.set_approval contested` on the test, twice | none | B |
| m246 | 145 | m245 present, bg_4 | "The tests in lines 2 to 4 are wrong because the version option never returns a message, so they should run a command that has a fixed version like 1.0" | criteria | r_f38b69e7c3: cr_1, cr_2 contest | m247 -> s415 -> m248 | s416: respecify x2, answer m249 | s417 woke, no words, 10 encodes, a question to the Terminologist | A |
| m256 | 145 | m255 present, bg_4 | "lines 3 and 4 still call the version option directly when they should run that command and check its printed output." | criteria | r_c8757431e3: cr_1..cr_3 contest | m257 -> s429 -> m258 | s430: 3 `ledger.log`, respecify, answer m259 | s431 woke, no words | A |
| m261 | 145 | m260 present, bg_4 | "every check should run that command and look at its printed output instead of calling the version option directly." | criteria | r_58c63355f6: cr_1..cr_3 contest | m262 -> s437 -> m263 | s438: respecify, answer m264, challenge m265 to Vision Keeper | s439 woke, no words, asked m266 "which callable does a test call?" | A |
| m312 | 144 | m312 clarify about cr_1, tst_confirm_default_on_eof | answer m313: "The test is wrong to expect True. Either have it expect False or have it pass a default" | the test row | r_1096cf2263: all approve | m314 to Terminologist, m315 to Vision Keeper | s463 `glossary.adopt`; s464 `problem.set_approval` x4 | none | B |
| m400 | 144 | m399 clarify about ver_opt_show_py, tst_ver_opt_show_py_01 | "Change the test so it calls the normal version flag, because show_python is a setting the developer passes to the decorator and not a new flag that users type." | the test row | r_dd4b76b081: **tst_ver_opt_show_py_01 revise**, d_984fb7181e contest | m401 to Terminologist, m402 to Vision Keeper | s577 `glossary.adopt`; s578 `problem.set_approval` x4 | none | B |
| m316 | 144 | m316 present, bg_4 | answer m317: "The checks on lines 2, 6 and 7 should send their input through click's own test runner instead of reading the real stdin, and line 8 should drop the option default tests again." | lines 2, 4, 6, 7 revise, line 8 contest | none landed | none | s466: 3x `rulings.rule`, each refused: "line 8: bg_4 is the change's line: a prediction of what it touches, and a ruling on it moves nothing. To stop the change, contest the item confirm_default_on_eof, line 1. Otherwise approve line 8" | none | C |

Notes on the table:

- On route A the Liaison called `msg.relay_architect` each time, and the
  relay split sent the criteria to the Terminologist (observed: s271, s320,
  s339, s415, s429, s437 tool calls; the one relay message each). The repeat
  calls are the "every owner ... has its relay already" refusal (reasoned:
  one relay message per session, `sandbox.py:3627-3631` at 17e67ca3).
- m400 is the one case of the eleven that is literally candidate C's site, a
  `revise` on a `tests` row (observed: r_dd4b76b081).
- The Terminologist does fold some of the principal's test words into the
  criterion. m186's "fixed version such as 1.0" landed in cr_3's text as
  "outputting a fixed version such as 1.0", which inverts the words
  (observed: s341's prompt, 2026-10-13). The Tester then reads the criterion
  and not the principal.

## 2. The routes in the code (17e67ca3)

1. **`rulings.rule`** (`rota/roles/api.py:7717-7964`). It maps a line
   number to `order[n-1]`, or takes a row id that is in the page's refs. It
   writes one `rulings` row with `per_item`, `words` and `texts`. It does not
   send a relay. Its refusals: a revise of a team's note; any non-approve on
   a batch line whose batch is merged, abandoned, or has a head commit
   (`api.py` ~7860-7885, the route C refusal). The batch-line refusal raises
   for the whole ruling, so the other lines' revisions are lost with it
   (observed: s466).
2. **The relay** is a separate Liaison session woken by the `verdict`
   message (route A) or the same session for a clarify (route B). The split
   is at `rota/core/sandbox.py:3570-3631`. A criterion goes to the
   Terminologist (`CRITERIA_RELAY` when it is a ruled line of the page). A
   batch goes to `_owner_of_ref + BATCH_RELAY`. Any other ref goes to
   `_owner_of_ref(conn, ref) or recipient`. `RULED_TABLES`
   (`sandbox.py:867-873`) holds statements, items, glossary_terms,
   constraints and model_areas. It has no `tests` entry, so a `tests` row
   stays with the recipient the Liaison named (the Vision Keeper in all 4
   route B cases) (observed: code; m184, m244, m315, m402).
3. **The words on a wake** (`rota/core/runner.py:1646-1785`). `principal_said`
   comes from `entry_for(trigger)`, or, when the trigger's verb is `relay`,
   from `chain_verdict` walking the cause chain. A Tester woken by the
   Terminologist's `answer` gets neither: the verb is `answer`, so the chain
   walk does not run (reasoned: the `row["verb"] == "relay"` guard at
   runner.py ~1708; observed: no `principal_said` in s273, s322, s341,
   s417, s431, s439).
4. **The relay refusal** (`sandbox.py:3542-3559` at 17e67ca3; the stack's
   `3140-3156` is an older line range). It applies to the Terminologist's
   `answer` to the Tester when `park_criterion_relay(trigger)` holds. Its
   query: a batch that holds the criterion's ticket, with status not in
   (`merged`, `abandoned`) and a non-empty `head_commit`. When none, it says
   "no change built from this criterion has a commit yet, so the Tester has
   written no test of it". The query never reads `tests`. A criterion whose
   test sits in an abandoned batch gets the false sentence (reasoned: the
   status filter; night 142 walk 1 is the observed case).
   - It fired in s122, s191, s261, s372 (night 145) and s190, s537 (night
     144), all Terminologist sessions on a park relay, none on the 11 cases
     (observed: `turns` text search, 2026-10-13).
5. **The check line** (`rota/roles/principal.py:1064-1135`,
   `request_block`). It reads `tests WHERE criterion_id = ?`, filtered by
   `batch_id` only when the caller passes `batch`. It never reads
   `batches.status`, so a test of an abandoned batch stays the criterion's
   `check:` line on every page that passes no batch (observed: code).
   `check_line` (`principal.py:487-526`) reads the test body and its own
   batch's last run.
6. **The exhaustion challenge quote** (`sandbox.py:1250-1296`,
   `_quotes_span` at 913). The door requires a 12-character verbatim span of
   the criterion and of the test body without comments. Any span passes. No
   rule asks for the asserting line or the run's `E   ` line, so night 142's
   Architect quoted a line that was not the `.strip()` line and the door
   took it (reasoned: code; observed case is night 142, not re-run). In
   night 145, m164 quoted the `def` line and docstring, and m177 quoted the
   run's `RuntimeError` (observed: `messages`).

## 3. The fix lines, one per site

Each line names the door test that is red today. "Moves" means the
principal's words would reach a Tester wake on that case.

1. **Route A: the Tester's wake carries the ruling's words.** When the
   Tester wakes on a Terminologist `answer` whose cause chain carries a
   principal verdict, the runner resolves `principal_verdict` and
   `principal_said` as it does for a relay. Site: `runner.py` ~1708 (the
   `verb == "relay"` guard), plus one line in the Tester's brief that the
   words are about the test. No new graph edge.
   Red door test: a park or present page ruled `contest` on a criterion,
   relayed, repaired and answered; the Tester's inbound has no
   `principal_said`.
   Moves: m142, m171, m186, m246, m256, m261 (6). Does not move: m182,
   m242, m312, m400 (no Tester wakes), m316 (no ruling).
2. **Route B: a `tests` row of a ruling goes to its criterion's writer.**
   In the relay split, a ref in `tests` maps to its `criterion_id` and
   travels as a criterion relay to the Terminologist, which repairs or
   keeps the criterion and answers the Tester. With fix 1 the Tester reads
   the words. Site: `sandbox.py` relay split and `_owner_of_ref`.
   Red door test: a clarify about a criterion and its test, ruled `revise`
   on the test row (m400's shape); the relay goes to `vision_keeper`.
   Moves: m182, m242, m312, m400 (4). Does not move: route A (already on
   the criterion) and m316.
   The direct form, a Liaison relay to the Tester, needs a new edge in
   `graph.json`. That is "who talks to whom", which is Roman's (reasoned:
   CLAUDE.md, the sprint rule of 2026-10-12 23:52). Law 1 makes the Tester
   the owner of a `tests` row, so the direct form is defensible, but the
   criterion form needs no ruling.
3. **The relay refusal says only what the rows hold.** The query reads
   `tests WHERE criterion_id = ?` first. When a test row exists, the
   sentence names it and its batch's status, and does not say "has written
   no test". Whether the answer is then admitted is the design's choice:
   admit it when the test's batch is abandoned or deferred, because the
   Tester rewrites that test (reasoned: frame 213's night 142 case).
   Red door test: a criterion with a `tests` row in an `abandoned` batch and
   no live batch; the refusal text contains "has written no test of it".
   Moves: 0 of 11.
4. **A cancelled batch's test is no page line's check.** `request_block`
   joins `batches` and drops tests whose batch is `abandoned`, unless the
   page is about that batch. Red door test: a criterion with one test in an
   abandoned batch; a page with no `batch` shows its `check:` line.
   Moves: 0 of 11 (night 145 had 0 cancels; night 144 not counted here).
5. **The exhaustion challenge quotes the failing line.** For a challenge
   with a red test in refs, the test-side span must include the first
   `assert` line that the run's `E   ` line names, or the `E   ` line
   itself. Red door test: night 142's s183 test body with a challenge that
   quotes a non-asserting line; today the door admits it.
   Moves: 0 of 11.
6. **Route C is not this frame.** m316 dies at the batch-line refusal in
   `rulings.rule`. A fix would let the other lines land and return the
   refusal for line 8 alone, or treat "drop the option default tests" on a
   batch line as a touch dispute. That is the territory of frames 196 and
   185 (the protected file and a contest that abandons the batch)
   (reasoned: night 144 read, section 7, names frame 196 for m316). It is a
   residue under the residue rule.

Count: fixes 1 and 2 together move 10 of 11. The original three sites move
0 of 11 and stay on the frame for night 142's shape.

## 4. History

- `git log -S "has written no test of it" -- rota/core/sandbox.py` gives one
  commit: 2dace61b (2026-10-09), "feat(rota): a ruling reaches the item, a
  seat writes no row about a ruled row, and an amended item is sliced
  again". The code comment cites "the delta review of 2c602d1b, finding 5":
  "Off the park page the batch has often not started, and the Tester woke in
  `answer` for a question it never asked". Fix 3 must keep that case
  refused: no test row and no commit (reasoned).
- **Roman's ruling, DECISIONS.md, "The park ask is a page with rows, and
  the principal's words always land on a row (2026-10-08)", point 2,
  verbatim:** "The principal's rulings land on the criterion rows as on
  every page: approve, contest, revise. A contest or a revision moves the
  criterion's version, the Tester rewrites the test from the ruled words,
  and the batch is re-derived from the records. The principal never rules
  on a test."
  - This supports fix 1: the ruling says the Tester rewrites "from the ruled
    words", and today the Tester never sees them.
  - This bears on fix 2 and on candidate C's wording. "The principal never
    rules on a test" makes a ruling keyed on a `tests` row the wrong shape.
    A clarify still lists the test row in `about`, and the Liaison rules it
    (m182, m242, m312, m400). Mapping the test row to its criterion keeps
    the ruling on the criterion row, as point 2 says. A relay keyed on the
    test row to the Tester contradicts the last sentence.
  - Point 4, verbatim: "Every word of the principal is a ruling on a row, or
    it earns one Liaison question that names a row."
- `plans/frame142-design.md:357`: "The expectation is a fact of the test
  row. A line that a model writes is a second reading between the test and
  the principal, and the principal never rules on a test." This is the
  check line's origin. Fix 4 keeps the line mechanical.
- **LAWS.md law 2**, verbatim: "Judgement crosses a role boundary only as
  structured findings — ids and states. ... The reasoning is written into
  the decision record by whoever decided, and reached by following a ref."
  Fix 1 obeys law 2: the words reach the Tester through the ruling's chain
  as `principal_said`, the same resolver the relay uses. The
  Terminologist's answer keeps no text.
- **LAWS.md law 1**: `tests` rows have one writer, the Tester. It supports
  the Tester as the end of the route. It does not by itself rule the edge.
- The relay split's own comments cite "ruled: Roman, 2026-10-08, the park
  ask is a page with rows, point 2" for a criterion going to the
  Terminologist (`sandbox.py:3576-3578`). Fix 2 extends that route and does
  not undo it.
- No archive frame under `plans/archive/` touched this refusal (observed:
  `git log -S` gives one commit, 2026-10-09, after the last archive file
  that names relays).

## 5. Usage

About 95k tokens by this agent's own count. The harness line is the
measure (meta workflow).
