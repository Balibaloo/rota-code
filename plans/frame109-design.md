# Frame 109, the Developer's challenge that never parses: scope read

Revision 1, 2026-10-02. Read-only scope read, meta workflow. Subagents: 0.

## Summary

The stated cause is not quite the cause. A `'` inside the `"`-quoted
`quotes=` value parses without error. The turn 4 call fails because the seat
opens a second string at `", "round_no=0)`, and that string never closes.
Turns 5 to 7 fail for a second reason, a parser defect: the first scan
closes the list early inside a `'''` value, and the rescan never runs.
(observed: the runs in Q1 below, 2026-10-02)

## Q1. The parser

- The door: `extract`, `rota/llm/toolproto.py:624-635`, when both scans find no end (observed).
- First scan, `toolproto.py:587-614`: `'`, `"` and backslash only, no
  triple quotes (observed).
- Rescan: `_rescan_args`, `toolproto.py:128-168`. It treats `'''` and `"""`
  as one token. It runs only when the first scan found no end,
  `toolproto.py:617-623`. It accepts its end only if `parse_args` parses the
  enclosed text (observed).
- `parse_args`, `toolproto.py:171-231`: a JSON object, or Python keyword
  form through `ast`. Real newlines inside quotes are escaped first
  (`_escape_newlines_in_quotes`, `toolproto.py:276`). A `SyntaxError` falls
  to `_parse_args_lenient` (`rota/llm/_lenient.py:50`) (observed).
- Accepted forms: `'...'`, `"..."`, backslash escapes, `'''...'''` and
  `"""..."""` with real newlines, and the label block `quotes=[quotes]` as
  the last item on its line with the raw text on the lines below
  (`_inline_blocks`, `toolproto.py:354-401`) (observed: probe calls below).
- Not accepted: a fenced block of three backticks, `could not parse
  arguments` (observed: probe call, 2026-10-02).

Runs through `extract` (query: `turns` where `session_id` in s141, s142,
s143 and the completion holds `challenge`; all observed 2026-10-02):

| Input | Result |
|---|---|
| s141 turn 4 as written, 963 chars, one line, `\n` as text | ToolError, the door |
| turn 4 with `", "round_no=0)` changed to `", round_no=0)` | ToolCall with refs, quotes, round_no |
| s141 turns 5 to 7, `quotes="'''...'''` with no closing `"` | ToolError, the door |
| turn 5 with the stray `"` removed, a clean `'''...'''` | ToolError: `quotes= opens with ' and never closes` |
| a `'''` value with real newlines and both quote kinds | ToolCall |
| `round_no=0, quotes=[quotes]` and a raw block below | ToolCall |

- s142 and s143 wrote s141's turn 4 byte for byte (observed: query).
- The clean `'''` failure has a site. The first scan reads `can't` in the
  value as an opening `'`, then closes the list at the `)` after
  `can't handle` (offset 633 of 966). `parse_args` fails on that prefix, so
  the call is a ToolError at `toolproto.py:640-643`. `_rescan_args` finds
  the true end at 965, and the full argument text parses. The rescan is
  never asked, because the first scan returned an end (observed: a
  scratch replica of the first scan, and `_rescan_args` called directly).
- The door hint names `text='''...'''`, not `quotes=`, and never says to
  drop the outer `"`. The seat kept it on turns 5 to 7 (observed).
- The system prompt holds no triple-quote form. "Call one per line" in
  `rota/core/runner.py:293` pushes the seat to put a multi-line body on one
  line as `\n` text (observed: `system` of s141 turn 1 counts no `'''`;
  reasoned for the push).

## Q2. The brief

- Developer, `rota/roles/prompts/developer/tests_failing.md:25-28`: the call
  example is `quotes="..."`, and the text says copy "the exact words of both
  rows, the span of the criterion and the span of the test, verbatim". The
  example's `"` is what the seat copied (observed: text; reasoned: copy).
- Developer, `developer/exhausted.md:14-15`: "`quotes=` copying each
  verbatim". `findings_exhausted.tools:9` lists the tool too (observed).
- Tool line in the prompt: `TOOL: msg.challenge_tester(refs, quotes,
  round_no=0)`, from the `.tools` files `tests_failing.tools:8`,
  `exhausted.tools:8` (observed: s141 turn 4 `system` at offset 4145).
- Critic, `critic/review.md:17-18` "Quote the test's line", and
  `review.md:37-39` "the exact span of each, verbatim". One line holds less
  risk (reasoned). Tester, `tester/challenge.md:9`, quotes prose: low risk.
- `toolproto.py:202-212` records that the protocol widens to carry the
  test body. That widening misses night 105's shape (observed).

## Q3. The cases

Developer cases on `tick: tests_failing` (observed: yaml query,
2026-10-02):

- `L1-DV-challenge-a-test-that-contradicts-its-criterion`
  (`tests/rota/cases/l1_developer.yaml:232`) expects a challenge. The test
  body is one line, `assert invoices_for(account_id) == []`, with no quote.
- `L1-DV-fix-the-code-not-the-test` (`l1_developer.yaml:97`) and
  `ACT-DV-edit-inside-the-function` (`l1_acts.yaml:184`) forbid
  `msg.challenge_tester`.
- `exhausted`: `L2-DV-name-the-block-rather-than-retry`,
  `L2-DV-name-the-deferred-batch-not-the-running-one`.
- Critic: `ACT-CR-quote-the-tests-code`,
  `L1-CR-a-test-that-encodes-nothing-is-a-challenge`.

No case passes a long or multi-line quote. The longest Developer
`tests_failing` challenge call in `tests/rota/cassettes.db` is 657 chars.
Night 105's is 963 chars, nine body lines (observed: cassette query).

## Q4. The repeat

- Counter: `tick_attempts`, `rota/core/schema.sql:745`, key from
  `tick_key`, `scheduler.py:1570`. `note_dispatch`, `scheduler.py:1574-1591`,
  counts up before the session runs, `rota/core/loop.py:303` (observed).
- Cap: `tick_attempt_cap` = 3, `rota/core/config.py:122`. Quarantine at
  `quarantine_stalled`, `scheduler.py:1723-1771` (observed). Night 105 holds
  `developer|tick:tests_failing|bg_1`, attempts 3, quarantined 1 (observed:
  `tick_attempts` query).
- Attempt 2 and later carry one sentence, "Do something the earlier attempt
  did not", `rota/core/runner.py:367-380`. s142 got it, and still wrote the
  same turn 4 (observed: s142 turn 1 `user`).
- `runner.py:2679` ends a session that repeats a turn verbatim twice
  (observed: s141 turn 8).
- No rule stops a second dispatch when the tree, the rows and the last
  session's tool errors are unchanged. The count only caps it at three
  (reasoned: no other reader of `tick_attempts` gates dispatch in the sites
  above). The site for such a rule is `note_dispatch` and `loop.py:303`.

## Q5. Options and prices

Anchors, `plans/operating-facts.md:214-222`: an Opus pass is 40k to 77k.
A reviewer pass is about 70k.

- (a) Brief only. `tests_failing.md:25-28`, `exhausted.md:14-15`: quote one
  line, name the test by id. The body is in `[tests.load]` (observed: s141).
  Price: one implementer pass of about 50k, one diff review of about 70k.
  Re-records: the three `tests_failing` cases and the two `exhausted` cases
  above, since their prompts move. Buys: a short, one-line value with less
  room for a stray quote. It does not fix the `'''` parser defect, and the
  seat may still quote a long body (reasoned).
- (b) Parser only. In `toolproto.py:636-643`, when `parse_args` fails on the
  first scan's end, try `_rescan_args` before the ToolError. Optionally
  accept a fenced block. Turn 4's stray `"` stays a ToolError, because no
  parser can tell a stray quote from a real one (reasoned). Price: one pass
  of about 60k with new tests in `test_toolproto_quotes`, one review of
  about 70k. Re-records: none, because the prompt does not move. A case
  whose recorded completion now parses changes its verdict on replay, and
  the gate shows it (reasoned).
- (c) Both. Price: about 110k of passes and about 140k of review, or one
  pass of about 80k and one review of about 70k if done together.
  Re-records: the five Developer cases of (a), plus one new case that
  carries a multi-line body with `can't` and `'TypeError'`, to pin
  night 105's shape.

Recommendation: (c), done as one pass. The night shows two separate faults,
a stray quote that only the brief can prevent and a `'''` defect that only
the parser can fix. Either alone leaves one of the two observed failures
open (reasoned: the Q1 table). Turns 5 to 7 as written still fail under
(b), because each keeps the outer `"`. So (b) should also make the door say
"open the value with three quotes and no other quote" (reasoned). If Roman
wants one change only, take (b), since it costs no re-record.

## Revision 2, 2026-10-02 09:45: the review's corrections and pass 1

Corrections from the design review, honoured by pass 1 (meta workflow):

- The door text stays unchanged this frame. 217 cassette prompts carry it.
- The brief keeps the criterion's span beside the test line, as two strings.
  `_challenge_evidence`, `rota/core/sandbox.py:700-848`, needs 12 contiguous
  characters from each row and drops comments (reasoned: the review's read).
- `_resolve_refs` in `rota/core/runner.py` sends the test body to the
  Tester, so one quoted line loses nothing (reasoned: the review's read).

Pass 1 built these:

- Parser: in `extract`, when `parse_args` fails on the first scan's slice,
  `_rescan_args` runs. Its end replaces the first end only when it differs.
  Every door text is unchanged.
- Tests in `tests/rota/test_toolproto_quotes.py`: s141 turn 5 with the outer
  `"` removed parses to `refs`, `quotes` and `round_no`. Turn 4 as written
  still gives the `unterminated argument list` door, byte for byte. The
  literals equal the night 105 completions (observed: a scratch compare).
- Briefs: `developer/tests_failing.md` and `developer/exhausted.md` show
  `quotes=["<the criterion's words>", "<one code line of the test>"]`.
- Case: `L1-DV-challenge-a-test-with-a-long-body` in `l1_developer.yaml`
  carries night 105's body shape. It has no recording yet.

Open: the five Developer cases of Q3 and the new case need recordings.
