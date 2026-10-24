# Frame 311, the provenance: the docstring refusal of `verdicts.emit`

Read on Opus, read-only, at `cab91420` on `rota/foundation`, 2026-10-24.
The night databases were opened with `?mode=ro`.

## 1. The verdict

The docstring refusal is a generalisation that no ruling made and no case
needed. Frame 180 built it on 2026-10-08 from one `import json` case. That
case named no docstring line. The refusal reads the line's kind only and never
the criterion, so on night 160 it refused 40 correct docstring lines under a
criterion that asks for the docstring, and 0 passes landed (observed: sections
2 to 4).

## 2. The commit and its reasoning

- The refusal came in `20ac26ce`, 2026-10-08 04:11, "fix(desks): the lines
  check refuses a line with no behaviour". The body says: "Such a line does
  nothing, so it meets no criterion. On nights 129 and 130 the Critic s134
  named "import json" for the criterion that asks for a TypeError" (observed:
  `git show -s 20ac26ce`).
- The frame was 180, pushed and built by session 18588d6d (rota-a1). The
  sentence that decided the docstring part is the frame's own reasoning, not
  a ruling: "A line that imports, comments, documents or fills holds no
  behaviour, so it can meet no criterion, and the door can know that from
  the line's shape alone" (observed: `plans/archive/stack-2026-10-08.md:82`).
- The order to build frame 180 was "taken by timeout at 02:13 on the
  recommended answer". Roman did not reply (observed:
  `plans/archive/stack-2026-10-08.md:69,87`).
- The case held no docstring line. Night 130's read says "No line is a
  comment or a docstring line" (observed: `plans/night130-read.md:45`). The
  docstring kind was added by analogy (reasoned).
- The ruling under the door is Roman's of 2026-10-07 08:57: "a pass names a
  line per requirement ... the door refuses a pass that leaves a criterion
  unnamed" (observed: `plans/archive/stack-2026-10-08.md:20`). The ruling says
  nothing about line kinds.
- Frame 170's design admitted docstring lines on purpose: "A seat can name a
  comment line, a docstring line ... and the door admits it". It scored such a
  line as a miss by hand, not as a refusal (observed:
  `plans/frame170-design.md:99,221`).
- `e374ecb8`, 2026-10-21, frame 201, put the kind words into the block
  refusal: "they are docstring lines. A docstring line does nothing that a
  criterion asks for". The body says "No predicate changes" (observed:
  `git show -s e374ecb8`).
- `DECISIONS.md` and `LAWS.md` hold no sentence on docstring lines and
  verdicts (observed: grep). No sentence of Roman's decided that a docstring
  line meets no criterion. None exists in the records read.

## 3. The predicate

- The door reads the line's kind alone. The criterion's text is read only by
  `_quotes_a_criterion`, to refuse a quote of the criterion itself (observed:
  `rota/roles/api.py:12523-12541`).
- The kinds come from `_added_kinds` (`api.py:12262`) on a `git diff -W` of
  the batch (`api.py:12436`), and from `_shape_kind` (`api.py:12222`).
- The kinds with one refusal text, `_NO_BEHAVIOUR` (`api.py:12193`): "a blank
  line, `pass`, `...`, a comment, a plain import or a docstring line".
- Two refusals use the kinds.
  1. The block refusal, a value of more than 2 parts that are all of no
     behaviour (`api.py:12460-12486`): "the value for {cid} holds {n} lines,
     and they are {plural}. {Kind} does nothing that a criterion asks for.
     ...". The plurals are "blank lines", "`pass` lines", "`...` lines",
     "comments", "plain imports", "docstring lines" (`api.py:12196`).
  2. The single refusal, a value of 1 or 2 parts that are all of no behaviour
     (`api.py:12543-12557`): "the line for {cid}, {quote!r}, is {kind}, and
     {_NO_BEHAVIOUR} does nothing that a criterion asks for. ...".
- An import in an `__init__.py` hunk and an import with `as` are not plain
  imports (`api.py:12238`, `12298`). No other kind has an exception.

## 4. The count

Nights 140 to 160, all 21 databases exist. Script:
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0cdcac52-3588-4266-b1fb-fc5d7d31b805/scratchpad/f311_count.py`.

The query, per database:

```sql
-- sessions that met the text at all
SELECT COUNT(DISTINCT session_id) FROM turns
 WHERE user LIKE '%does nothing that a criterion%'
    OR completion LIKE '%does nothing that a criterion%';
-- per session: turns ordered by seq; the refusals are the "ERROR verdicts.emit"
-- lines in `user` that match
--   the line for (\S+?), .*?, is a docstring line, and .*does nothing that a criterion asks for
--   the value for (\S+?) holds \d+ lines, and they are docstring lines\.
-- counted as the larger of the highest count in one prompt and the count in
-- the "SESSION ENDED" account; checked against tool_calls fn='verdicts.emit'.
-- The criterion text is the row of [criteria.load] in the session's first prompt.
SELECT seq, user, completion FROM turns WHERE session_id = ? ORDER BY seq;
SELECT COUNT(*) FROM tool_calls WHERE session_id = ? AND fn = 'verdicts.emit';
```

Results:

- Nights 140 to 159: 0 docstring refusals. The text met sessions on nights
  144 (s337), 154 (s132, s135), 158 (s135) and 159 (s127, s128), each on
  `import json`, a plain import (observed: the databases).
- Night 160: 42 docstring refusals in 16 Critic sessions, 17 session and
  criterion rows (observed: `clickI_night160.db`).
- Of the 42, 40 are under `cr_3_confirm_default_on_eof`, whose text names a
  docstring or documentation: v7 "confirm()'s docstring explains the
  'default_on_eof' flag" and, for s188, "must be documented in the help text
  of confirm()". The sessions are s188, s198, s200, s205, s206, s207, s213,
  s214, s215, s221, s222, s223, s229, s231 and s248.
- The other 2 are right refusals: s146 quoted the docstring of `echo_json`
  for `echo_json_helper`, "must not print any additional text", and s231
  quoted a docstring line once for `cr_1`.
- Review ticks quarantined after such refusals: 3, `critic|tick:review|bg_2`,
  reported by s208, s216 and s224 (observed: `plans/night160-cycle3.md:5,21`,
  `plans/night160-cycle4.md:11`).
- Of the 15 sessions under the documentation criterion, 13 ended with no
  verdict and 2 landed a fail on `cr_3`: s188 at 6ed4f8b4 and s248 at
  905345ed. 0 landed a pass (observed: `verdicts` rows of bg_2).
- A correction to the brief: s248 got the docstring refusal once, not 6
  times. Its `tool_calls` show one pass at seq 7, then 8 challenges, then 5
  fails at seq 20 to 24, 1 landed and 4 "already landed". The read counted the
  refusal shown again in each prompt of turns 2 to 7 (observed:
  `clickI_night160.db` s248; `plans/night160-cycle4.md:12`).
- Outside this text: before `e374ecb8` the block refusal named no kind. Night
  144 (s335 to s337), 152 (s133) and 157 (s324 to s326) met that older block
  text. Frame 201 records the night-157 values as docstring blocks (observed:
  the databases; `plans/stack.md:1775`).

## 5. The neighbours

- The Critic's brief tells the seat to name "the added line of the diff that
  meets it, a line that starts with `+`" and says that the tool refuses "a
  line the diff does not add" (observed: `rota/roles/prompts/critic/review.md:9-11,33-36`).
  It says nothing about line kinds. The only docstring sentence is "Do not
  fail a diff for a purpose you read in a docstring or a comment" (observed:
  `rota/roles/prompts/critic/base.md:10-11`). So the brief admits the line
  that the door refuses.
- The order of the doors on a pass, in `verdicts_emit` (`api.py:12054`):
  1. the argument checks, `ValueError` (`api.py:12097-12135`);
  2. `_pass_lines_check` (`api.py:12386`, called at `12147`): frame 170's
     shape and missing-line refusals; then frame 170's block cap of 2 parts,
     with frame 201's kind words; then frame 180's not-in-diff and quote
     refusals; then frame 180's single no-behaviour refusal, with frame
     201's code-line list;
  3. `_first_pass_hold` (`api.py:12571`, called at `12148`), frame 201's hold.
- Frame 201's hold fires only after the lines check admits the pass. It never
  fired on these 42 calls (reasoned: the order). Frame 170's block cap fires
  before the kind check, so s205's 5-line value meets the cap in any repair.

## 6. The repair

- A. In `_pass_lines_check`, the single and the block refusals skip the kind
  "a docstring line" when that criterion's own text names the code's
  documentation ("docstring", "document", "help text"). File:
  `rota/roles/api.py`, function `_pass_lines_check`.
- B. The door reads the criterion's `surface_refs` and admits a docstring line
  inside that surface. Rejected: cr_1, cr_2 and cr_3 share
  `src/click/termui.py::confirm`, so B admits s231's `cr_1` line and s146's
  line, the 2 right refusals.
- C. Drop the docstring kind from `_NO_BEHAVIOUR`. Rejected for the same 2
  right refusals.

**Recommend A.** It keeps frame 180's refusal for every criterion that asks
for behaviour, and it keeps Roman's ruling of 2026-10-07, a line per
criterion. It keeps frame 170's design reading that a docstring line can be
the line. The word list names one concept, the code's documentation, and the
same concept applies to the kind "a comment". So the general rule reads: a
kind meets a criterion only when the criterion asks for that kind
(reasoned). Leave out "explain" and "describe". They occur in behaviour
criteria, and the 40 refusals need only "docstring" and "document".

Per-criterion text is needed. The query at `api.py:12515` joins all criteria
of the batch, so A reads `c.id, c.text` into a dict.

The red tests, on bg_2's diff at 905345ed (observed: `clickI_night160.db`,
`turns` s205 seq 1 completion; `tool_calls` s205 seq 7):

```python
verdicts.emit(batch_id='bg_2', result='pass', failed_criterion=None, reason='', diff_ref='', lines={'cr_1_confirm_default_on_eof': '    default_on_eof: bool = False,', 'cr_2_confirm_default_on_eof': '            if default_on_eof and default is not None:', 'cr_3_confirm_default_on_eof': ':param default_on_eof: If True, when stdin is closed (EOF), return the\n        provided default value instead of raising :exc:`Abort`. Callers who\ndoes not enable this flag will still abort at end of input, just as\nthey do now. When enabled, confirm() returns the default value on\nEOF rather than waiting for further input or aborting.'})
```

- s205's call holds 5 parts, so after A it still gets frame 170's block
  refusal. The red assertion: the text has no "does nothing that a criterion
  asks for" and tells the seat to copy one line of the docstring.
- The landing test is s206's call, `turns` s206 seq 1: the same `lines=` with
  `'cr_3_confirm_default_on_eof': '    :param default_on_eof: If True, when stdin is closed (EOF), return the'`.
  After A it lands. s198's call is the same with 8 leading spaces.
- The guard tests: s146's call on night 160 stays refused, and s134's
  `import json` on night 130 stays refused.

## 7. Usage

About 63k tokens on this reader against the cap of 40k (reasoned: the
harness's token counter before and after).
