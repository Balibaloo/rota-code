# Candidate C2, the provenance read: the escape level of a body in the call

Date: 2026-10-26, read at 18:05 to 18:25. Read at commit b2f72131 on
`rota/foundation`, dated 2026-10-26 18:20. Read-only. The night databases
were opened with `?mode=ro`. No model call ran and no pytest ran. Meta
workflow for the read, by the rule of 2026-10-18 (provenance before a fix).
Sprint 25, row 2.

Sources:

- The symptom records, cited and not repeated: `plans/night168-read.md`
  section 2 rows W1 and W2 (lines 104 and 105) and section 5 row 2 (line
  274); `plans/night167-read.md` section 2 row W2 (line 95) and section 5
  row 2 (line 280).
- `rota/llm/toolproto.py`: `_literal` 81 to 136, `parse_args` 791 to 848
  (the strict parse 818 to 819, the fallback 820 to 836),
  `_escape_newlines_in_quotes` 947 to 983, the call-form refusals 1440 to
  1447, 1524 to 1534 and 1537 to 1544.
- `rota/llm/_lenient.py`: `parse_args_lenient` 50 to 93 (the raw quoted
  value 73 to 77, the decoded unquoted value 90).
- `rota/core/sandbox.py`: `_unescaped` 1331 to 1350, `_quote_refusal` 1376
  to 1414, `_cites` inside `_challenge_evidence` 1643 to 1648.
- `rota/roles/api.py`: the parse check of `tests_encode` 9310 to 9328,
  `_note_collection_error` 17429 to 17455, `tests_load` 10879.
- `rota/core/harness.py` lines 69 and 237 to 241.
  `D:/repos/_AI/sample_repos/clickI/pyproject.toml` lines 83 to 87.
- Commits: 231afe4c, 4951ca08, 7edfeea6, 5f445aab, 1e878553, bfd149d1,
  45541e92, 4bb2656b, 5ae7f5f5.
- `.rota/clickI_night160.db` to `.rota/clickI_night168.db`, with
  `night164a`: `sessions`, `turns`, `tests`, `test_runs`. The counts came
  from a scratch script that runs today's `toolproto.extract_lenient` with
  the two signatures over each stored completion.
- `rota/DECISIONS.md`, `rota/LAWS.md`, `plans/composition.md`,
  `plans/method/intent.md`, `plans/method/reference.md`,
  `plans/operating-facts.md`, searched for a ruling on escapes.

## The result

**Gap: no design names the escape level of a value in the call, so the
level is the default of the parse path that reads the call, and no
refusal, brief line or note tells a seat which level it needs.**

The two records state part of the mechanism in a form the code does not
hold. The parser does not read `body` and `quotes` differently in one
strict call. Both go through one function. The difference that the seats
met comes from two other places. The first is the strict path and the
fallback path, which read a quoted value at two levels. The second is the
`tests.load` view, which shows one backslash as `\\` in JSON, next to a
refusal that shows two backslashes as `\\` (observed: question 2). The
night 168 brief also says that qwen3.5:9b wrote one backslash on night
166 and went green. The record shows four backslashes in the call that
went green (observed: question 5).

## 1. The design that gave the call one escape level

- The call's keyword form is a Python argument list. `parse_args` runs
  `ast.parse(f"_f({safe})")` and reads each value with `_literal`, which
  ends in `ast.literal_eval` (observed: `toolproto.py` 818 to 819 and
  131). So a quoted value is a Python string literal, and the parse
  removes one escape level from it (reasoned: Python's literal rules).
- The commit that added the design is 231afe4c, 2026-08-09 10:48, "the
  TOOL: protocol". Its docstring says "Keyword form goes through
  `ast.literal_eval`, never `eval`" (observed: the diff, line 892). The
  reason it names is safety against untrusted input. It names no escape
  level (observed: the commit body). It served the S0 build, before the
  frame numbers, in the build workflow (observed: the commit body names
  no frame).
- The commits that changed the string reading since:
  - 4951ca08, 2026-08-10: `_literal` adds two tolerances and keeps
    `literal_eval` (observed: `git log -S "ast.literal_eval(node)"`).
  - 7edfeea6, 2026-08-20: the fallback `parse_args_lenient`. A quoted
    value is the raw text between its outer quotes, with only `\n`
    read as a line break (observed: `_lenient.py` 77). The body says
    "nothing that parsed before parses differently". It names no escape
    level for the fallback (observed: the commit body).
  - 5f445aab, 2026-08-24: `_escape_newlines_in_quotes` turns a line break
    inside a quoted value into `\n` before the parse (observed: the
    function, 947 to 983).
  - 1e878553, 2026-10-04: the third reading never guesses for a function
    that writes a file (observed: `git log -S` on the strict parse).
- `_unescaped` came on 2026-10-26 in 45541e92 (06:54, frame 328 pass 3).
  4bb2656b, the same day, frame 328 pass 3b, cut it to an escape that
  gives a control character (observed: `git log -L` and the commit
  body). It reads `\xNN`, `\uNNNN` and `\NNN` only, and never `\\`
  (observed: `sandbox.py` 1336 and 1341 to 1344).
- What a seat must write in the call (reasoned: the two paths above):
  - Strict path: `\\` for one stored backslash, `\\\\` for two, and a line
    break or `\n` for a newline. A single `\R` stays `\R` with a warning.
  - Fallback path: `\` for one, `\\` for two, and a line break or `\n` for
    a newline.
  - The strict path runs when the whole argument list parses. A seat
    cannot see which path read its call (reasoned: `parse_args` 818 to
    836 returns no mark of the path).

## 2. Why `body` and `quotes` met two levels

- In the strict path, each keyword value goes through `_literal`
  (observed: `toolproto.py` 841 to 846). No function unescapes `body` or
  `quotes` on its own. They read `\\` at one level (reasoned: one call of
  `literal_eval` per value).
- In the fallback path, a quoted scalar such as `body='...'` keeps its raw
  text (observed: `_lenient.py` 73 to 77). An unquoted value such as
  `quotes=[...]` goes back through `literal` and is decoded (observed:
  `_lenient.py` 90). So in one fallback call `body` keeps `\\` as two and
  `quotes` reads `\\` as one. This direction is the reverse of the
  records' sentence (reasoned: the two lines).
- The case of W2 is not one call. s146 wrote `"AppData\\Roaming"` in a
  strict `tests.encode` call, and the row holds one backslash (observed:
  night 168, s146 turn 2, `tests` row tst_crit_1 version 2). s147 then
  wrote `AppData\\\\Roaming` in `quotes` (observed: night 168, s147
  `turns.completion` seq 3). The parse gave two backslashes, and the
  quote check refused it (observed: s147 `turns.user` seq 4).
- The cause of the four backslashes is the view. `tests_load` returns
  JSON, and JSON shows one backslash as `\\` (observed: s147
  `turns.user` seq 2, `"assert \"AppData\\Roaming\" in result"`). The
  refusal in `_quote_refusal` prints the parsed quote with no encoding, so
  its `\\` is two backslashes (observed: `sandbox.py` 1395 to 1397, s147
  seq 4). The seat sees one surface for two values (reasoned).
- The test half of `_cites` compares the quote as written, then both sides
  through `_unescaped` (observed: `sandbox.py` 1646 to 1648). Neither
  comparison reads `\\` as `\`.
- The difference is a default nobody named (reasoned: no commit body,
  docstring or ruling names an escape level for either path or either
  view).

## 3. The parse check of `tests_encode`

- The check is `_ast.parse(body)` with no warnings filter (observed:
  `api.py` 9323). Only a `SyntaxError` is refused, as "the body is not
  Python" (observed: 9324 to 9328). An invalid escape such as `"\R"` is a
  `SyntaxWarning` in Python 3.12 and later, so `ast.parse` returns a tree
  (reasoned: Python's rules; the nights run on Python 3.14, observed in
  the traceback paths of s147 `turns.user` seq 2).
- The commit is bfd149d1, 2026-09-01 20:14, "a test is Python the harness
  can run". Its body says the check asks "whether anything can execute"
  and has "no opinion about quality" (observed: the commit body). It did
  not consider warnings (reasoned: the body and the code name none).
- The project's pytest turns every warning into an error:
  `filterwarnings = ["error"]` (observed: clickI `pyproject.toml` 85 to
  87). The rota harness adds only `-W ignore::DeprecationWarning`, and only
  for rota's own tests (observed: `harness.py` 241). Its comment at line
  69 names the project's `filterwarnings = error`. So pytest's assertion
  rewrite raises the warning as `SyntaxError` at collection (observed:
  s147 `turns.user` seq 2, `tree = ast.parse(source, ...)` in
  `_pytest`).
- The collection note is `_note_collection_error` (observed: `api.py`
  17429 to 17455), added in 5ae7f5f5, 2026-10-26 07:51, frame 328 pass 4.
  The note copies pytest's last `E ` line (observed: 17440 to 17441). So
  it says `Did you mean "\\R"?` (observed: s146 `turns.user` seq 2, and
  s128 `turns.user` seq 2). That advice is at the level of the source
  file. In the strict path it is one level too few for the call
  (reasoned: question 1).

## 4. What the Tester's brief and the refusals say

- The Tester's system text has no word on escapes, backslashes or triple
  quotes (observed: night 168, s146 `turns.system` seq 1, 5595
  characters). Its only call form is `TOOL: artefact.verb(key='value')`.
- The call-form refusals say:
  - "Write the value as it is, with no backslashes:" then
    `{key}='''the text, with its quotes and line breaks as they are'''`
    (observed: `toolproto.py` 1440 to 1447).
  - "{write}, with no backslashes:" then the same line, and "No escaping,
    and no placeholder" (observed: 1524 to 1534).
  - "open {longest} with three single quotes, write every line of the
    value as it is ... No escaping" (observed: 1537 to 1544).
- The "not Python" refusal names only Python's message and the line
  (observed: `api.py` 9326).
- No line shows a body with a backslash in the form the call needs
  (observed: the lines above). "As it is" is wrong for a body with a
  backslash, because a triple-quoted value is still a literal that is not
  raw, and the strict path decodes it (reasoned: question 1).

## 5. How often the form appeared

Counted with today's parser, so nights 160 to 166 are read with the code of
2026-10-26 (reasoned: the parser changed little after 2026-10-04).

| Night | Model | `tests.encode` calls | Calls whose body holds an invalid escape | Stored rows with one | Challenge refusals on `\\` |
|---|---|---|---|---|---|
| 160 to 165, 164a | qwen3.5:9b | 1456 | 0 | 0 | 0 |
| 166 | qwen3.5:9b | 53 | 8 | 0 | 0 |
| 167 | gemma4:12b-it-qat | 65 | 9 | 1 (tst_c4 v1) | 3 of 20 |
| 168 | gemma4:12b-it-qat | 68 | 32 | 2 (tst_crit_1 v2, tst_crit_2 v1) | 14 of 24 |

- The refusal count is the distinct refusal texts per Developer session
  (observed: the scratch count). The night 168 record counts 21 of 37
  quote halves by another method (observed: `night168-read.md` 105).
- No stored body with an invalid escape ran green. None of the three rows
  has a `pass` in `test_runs` (observed: the three nights).
- Night 166: qwen3.5:9b s133 wrote two backslashes on turn 1, and that
  encode was refused for a missing triage. It wrote four on turns 2 and 3.
  The rows tst_c1_get_app_dir_roaming and tst_c3_get_app_dir_local hold
  `\\`, and both ran `pass` on attempt 2 (observed: night 166 `turns`,
  `tests`, `test_runs`). So qwen went green on the strict form, four in
  the call, and not on one.

## 6. Whether a departure stands

No ruling of Roman's covers the call form, the escape level, or what the
encode check reads (observed: the searched files name no such ruling; the
"escape" hits in `DECISIONS.md` 384 to 411 are routes out of a role, and
`reference.md` 317 is the build session's own patches).

## The repair

1. The encode face. `tests_encode` runs its parse with `SyntaxWarning` as
   an error and refuses an invalid escape. The refusal names the raw
   string form, `r"AppData\Roaming"`. Written with one backslash in the
   call, it parses on both paths (reasoned: question 1).
   The collection note gives the same form in place of pytest's `Did you
   mean "\\R"?`. Red tests: night 168 s128 turn 2 (the note on
   tst_crit_3), night 167 s142 turn 2.
2. The quote face. The test half of `_cites` also reads each `\\` of the
   quote as `\` when the written form misses, as the criterion half does
   with `_seat_forms`. The refusal then names that reading. Red test:
   night 168 s147 turn 4 (the call in `turns.completion` seq 3).

No question for Roman stands, because question 6 found no ruling to
depart from.
