# Frame 170, the design: a pass names a line per criterion

**Design of 2026-10-07 09:05, meta workflow. It designs a door and a brief for the Critic seat, which is the rota workflow.**

**`verdicts.emit` gains `lines`, a dict from criterion id to one added line of the diff, copied verbatim. On `result='pass'` the door refuses a criterion of the batch with no line, a key that is not a criterion of the batch, and a line that no added line of the batch's diff holds.** A fail keeps today's shape. The lines go in a new `lines` column on `verdicts`, and the cockpit's `verdicts` rows show them beside `reason`. The door cannot see whether a named line meets its criterion. On night 127's s279 a pass with three true lines lands, and the `NameError` still merges (reasoned: section 2). Six recorded Critic cases change their prompt and need a re-record, 30 runs (observed: section 6).

Ruling designed for: a pass names a line per criterion. The Critic writes, for each criterion, the line of the change that meets it, before it signs, and the door refuses a pass that leaves a criterion unnamed (ruled: Roman, 2026-10-07 08:57). Sources: `plans/stack.md` frame 170, `plans/frame170-merges-read.md`, `plans/frame170-history-read.md`. Script: `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/6cc11c8b-d798-4ba5-a74f-23bdd33674c1/scratchpad/d170/parse.py`. No model call.

## 1. The argument

**Name and type.** The new argument is `lines: dict[str, str] | None = None`, the last parameter of `verdicts_emit` (reasoned: the plural names what it holds, and a last parameter keeps every recorded positional call bound as today).

- The binder admits a dict here. `validate_args` refuses a dict or a list only where the annotation does not name `list`, `dict` or `Any`. It unwraps a one-element list around a scalar (observed: `rota/core/sandbox.py:330-351`, 2026-10-07). The scalar door converts text only for `int`, `bool` and `float` (observed: `rota/core/sandbox.py:171-218`, 2026-10-07). So `lines={...}` reaches the door as a dict, and the door checks each value itself.
- The signature renders as `verdicts.emit(batch_id, result, failed_criterion=None, reason='', diff_ref='', lines=None)` in every prompt whose mode holds the op (observed: `_render_signature`, `rota/core/sandbox.py:130-139`, and `Sandbox.signatures`, `rota/core/sandbox.py:455-470`, 2026-10-07).
- The write pipeline cannot store a dict in a column. A dict "dies at the database as `type 'dict' is not supported`" (observed: the comment at `rota/core/sandbox.py:331-334`, 2026-10-07). So the door stores `json.dumps(lines)` (reasoned: the `refs` columns hold JSON text the same way).
- Two tolerances, each a shape whose intent is fully determined (reasoned: the binder's own rule at `rota/core/sandbox.py:345-350`). A value that is a list of strings is read as several lines, and each must hold. A value with line breaks is split, and each non-empty part must hold.

**What a line is.** A line is the text of one added line of the batch's diff, copied verbatim, with or without the leading `+`. It is not a line number (reasoned: from what the Critic sees, below).

- The Critic's whole view of the code is `code.read`: `batch`, `touched`, `removed lines` and `diff`, the unified diff since the batch's fork (observed: `code_read`, `rota/roles/api.py:9358-9406`, and s279's first prompt, 2026-10-07). The review mode holds no `code.source` (observed: `rota/roles/prompts/critic/review.tools`, 2026-10-07).
- The diff gives a line number only in each hunk's `@@` header. A line number in the file is a count the seat must make from that header. Frame 162 refused a line counted from 1, so a small model's count is a known fault (observed: frame 162's heading, `plans/stack.md:374`, 2026-10-07).
- A verbatim copy is the act the seat already does: the challenge brief asks for `quotes=` copying the exact span, verbatim (observed: `rota/roles/prompts/critic/review.md:37-39`, 2026-10-07). A person who reads the verdict reads the code itself and not a number to look up (reasoned).
- An added line, and not a context line or a removed line. The ruling says "the line of the change". A context line is code the batch did not write, and a removed line is code the batch took away (reasoned).

**Worked example: night 127, bg_3, s279.** The batch has three criteria (observed: `criteria` joined to `batch_tickets`, `.rota/clickI_night127.db`, 2026-10-07):

| Criterion | Text |
|---|---|
| `cr_1_version_option_show_python_flag` | The version_option callable must accept a show_python boolean flag. |
| `cr_2_version_option_show_python_false` | When show_python is False (or omitted), the version_option callable must not append any Python version information to the message. |
| `cr_3_version_option_show_python_true` | When show_python is True, the appended Python version string must be derived from sys.version or equivalent runtime inspection. |

The diff's added code lines, verbatim from s279's first prompt (observed: `n170/r127_control.user.txt`, 2026-10-07):

```
+    show_python: bool = False,
+        # Append Python version if show_python is True
+        python_version = sys.version.split()[0] if show_python else ""
+            message % {"prog": prog_name, "package": package_name, "version": version} + (f" ({python_version})" if python_version else ""),
```

The seat writes one `TOOL:` line:

```
TOOL: verdicts.emit(batch_id='bg_3', result='pass', lines={'cr_1_version_option_show_python_flag': 'show_python: bool = False,', 'cr_2_version_option_show_python_false': 'message % {"prog": prog_name, "package": package_name, "version": version} + (f" ({python_version})" if python_version else ""),', 'cr_3_version_option_show_python_true': 'python_version = sys.version.split()[0] if show_python else ""'})
```

The parser reads it back as `{'batch_id': 'bg_3', 'result': 'pass', 'lines': {...}}` with the three values unchanged, the double quotes and the braces inside them included (observed: `toolproto.extract` in `d170/parse.py`, 2026-10-07 09:03). `_literal` reads an `ast.Dict` key by key (observed: `rota/llm/toolproto.py:93-98`, 2026-10-07). The new door admits this call, and the merge still raises `NameError`, because `sys` is not imported in a part of the file the hunks do not show (reasoned: section 2, last point, and section 7).

## 2. The door's checks

The checks run in `verdicts_emit` after the duplicate-verdict check and the fail-claim check, and only when `result == 'pass'` (reasoned: a second verdict on one commit keeps its own refusal first, and the desk guard at `tests/rota/test_desk_guards.py:284-297` keeps its words). On a fail the door reads no `lines` and stores none (reasoned: an optional argument that one branch needs is ignored on the others, never refused, `plans/operating-facts.md` line 338).

**What the door compares.**

- The criteria: the ids that `criteria.load` returns for the batch, `criteria c JOIN batch_tickets bt ON bt.ticket_id = c.ticket_id WHERE bt.batch_id = ?` (observed: `criteria_load`, `rota/roles/api.py:4146-4151`, 2026-10-07). The same query gives the seat its `[criteria.load]` block, so the door and the prompt name the same set (reasoned).
- The diff: the text `code.read` gives under `diff`, `worktrees.diff(row["worktree"], _batch_base(ctx, row["worktree"]))` (observed: `rota/roles/api.py:9388-9397`, 2026-10-07). The pass moves those lines into one helper, `_batch_diff(ctx, batch_id) -> str`, and both `code_read` and the door call it. One computation means the door reads the same diff that the push gave the seat (reasoned). The Critic writes no code, so the worktree does not move inside its session (reasoned: `review.tools` holds no write to code).
- The added lines: every diff line that starts with `+` and not with `+++`, with the `+` removed and the ends stripped.
- The cut: the prompt can cut a long diff, because the runner puts `code.read` last (observed: `rota/core/runner.py:2306-2311`, 2026-10-07). The door checks against the whole diff. So every line the seat saw is admitted, and a line past the cut cannot be named (reasoned).

**Check 1: every criterion of the batch has a line, and every key is a criterion.**

- `lines` absent, `None` or `{}` counts as every criterion unnamed. The ten recorded passes take this branch (observed: the merges read, section 1).
- A batch with no criteria rows needs no line, and the check admits the pass (reasoned: no criterion can be unnamed. A batch with no criteria is not this door's matter).
- A value that is not text, or not a list of text, is an unnamed criterion.

Refusal for a key that is not a criterion of the batch, checked first:

```
{key!r} is not a criterion of batch {batch_id}. Its criteria are {', '.join(ids)}. Send the pass again with lines= naming each of them once
```

Refusal for unnamed criteria:

```
a pass names, for each criterion, the added line of the diff that meets it, and {', '.join(missing)} {has|have} no line. Send verdicts.emit again with lines={'<criterion id>': '<the line>'} for each of {', '.join(ids)}, each line copied from a line of the [diff] block that starts with +. If no added line meets {missing[0]}, that is a fail on it: `verdicts.claim_encodes({missing[0]!r}, encodes=...)` first, as for any fail
```

Refusal for `lines` given as text and not as a dict:

```
lines= maps each criterion id to its line, as lines={'<criterion id>': '<the line>', '<criterion id>': '<the line>'}, one entry for each of {', '.join(ids)}
```

**Check 2: each line is an added line of the diff.** A named line holds when, stripped and with one leading `+` removed, it equals an added line, or it is part of one added line and holds at least 12 characters (reasoned: a small model cuts a long line, and s279's line for `cr_2` is 128 characters stripped (observed: `len` of the line, 2026-10-07). 12 characters keep out `)`, `else:` and `return x`).

Refusal:

```
the line for {cid}, {quote!r}, is not an added line of the diff of batch {batch_id}. Copy one line of the [diff] block that starts with +, without the +, and send the pass again. {nearest}If no added line meets {cid}, that is a fail on it: `verdicts.claim_encodes({cid!r}, encodes=...)` first, as for any fail
```

`{nearest}` is `The added line nearest to it: {best!r}. ` when `difflib.SequenceMatcher` gives some added line a ratio of at least 0.6, and empty otherwise (reasoned: the house rule "name the set, do not merely reject the guess", `verdicts_rule` at `rota/roles/api.py:6862-6863`). A batch with no diff refuses every line with these words.

**Offers.** Each refusal that names `verdicts.claim_encodes` records it with `_offer`, `encodes=True`, `then=(AGAIN,)`, as the fail-claim refusal does (observed: `rota/roles/api.py:6801-6809`, 2026-10-07). The pass form with `lines=` is named in words and not offered, because the door cannot fill the lines (reasoned: frame 135's law, a refusal names only a call the doors admit, `_offer`'s docstring at `rota/roles/api.py:264-270`).

**Two hints.** `ARG_HINTS_BY_OP[("verdicts", "emit")]` gains `line` and `quotes`, each pointing to `lines=` as a dict of criterion id to line (reasoned: the Critic's brief teaches `quotes=` for a challenge, so a seat may send it here. The hint table exists for a word the seat misreads, `rota/core/sandbox.py:118-127`).

**What the door cannot see.** The door proves that the seat named a line of the change for each criterion. It does not prove that the line meets the criterion. A seat can name a comment line, a docstring line, or any added line beside the criterion's code, and the door admits it. On s279 three true lines land, and the merge still stops with `NameError` on `--version`, because the import block is outside the hunks (observed: `plans/night127-read.md`, section 6, 2026-10-07). The ratio by hand in section 6 measures this gap, and the door does not close it (reasoned).

## 3. The brief

`rota/roles/prompts/critic/review.md` grows from 46 lines to 52 (reasoned: the new text below, counted at 80 columns).

Step 1, lines 9 to 13. Old:

```
1. **Does the diff satisfy each criterion?** For each one that looks like it
   fails, the branch is not yours to skip: `verdicts.claim_encodes` first —
   does this criterion's own test actually encode it? `True` and the code is
   what's wrong; `False` and the test is. A fail you have not claimed for
   does not land — the tool refuses it.
```

New:

```
1. **Does the diff satisfy each criterion?** For each criterion, find the
   added line of the diff that meets it, a line that starts with `+`, and copy
   it without the `+`. A criterion with no such line looks like it fails. For
   each one that looks like it fails, the branch is not yours to skip:
   `verdicts.claim_encodes` first — does this criterion's own test actually
   encode it? `True` and the code is what's wrong; `False` and the test is. A
   fail you have not claimed for does not land — the tool refuses it.
```

The emit paragraph, lines 30 to 33. Old:

```
Then `verdicts.emit` — `pass`, or `fail` with the criterion that failed. One
verdict per batch. A fail carries `reason=`: the criterion's words the diff does
not meet as written and what the diff does instead, so the Developer reads the
objection and not only the ref. A remark goes in `reason=` on either result.
```

New:

```
Then `verdicts.emit` — `pass`, or `fail` with the criterion that failed. One
verdict per batch. A pass carries `lines=`: every criterion's id and the line
you copied for it in step 1, as `lines={'<criterion id>': '<the line>'}` with
one entry per criterion. The tool refuses a pass with a criterion that has no
line, or a line the diff does not add. A fail carries `reason=`: the
criterion's words the diff does not meet as written and what the diff does
instead, so the Developer reads the objection and not only the ref. A remark
goes in `reason=` on either result, beside the lines of a pass.
```

- The lines come before the verdict in two ways. Step 1 asks for them first, and they travel inside the one `verdicts.emit` call, so no pass lands without them (reasoned: 8 of 10 Critics sent the verdict in a first turn of calls only, the merges read, section 2).
- The example form holds no `...`, because the parser refuses `...` as a placeholder (observed: `rota/llm/toolproto.py:120-126`, 2026-10-07).
- Line 35, "You are not writing a review; you are answering a question", stays. It is under "A fail names its criterion and stops" and speaks of a fail (reasoned).

`rota/roles/prompts/critic/answer.md` changes too, although the brief of this record names only `review.md`. The answer mode holds `verdicts.emit` (observed: `rota/roles/prompts/critic/answer.tools`, 2026-10-07), and 2 of the 10 recorded passes came from answer wakes, s149 on night 116 and s148 on night 120 (observed: the merges read, section 1). Without the change, the door refuses the answer mode's pass and its brief does not say why (reasoned). Step 2, lines 19 and 20. Old:

```
2. `verdicts.emit`: pass if the diff satisfies every criterion, fail naming the
   criterion the diff does not satisfy.
```

New:

```
2. `verdicts.emit`: pass if the diff satisfies every criterion, fail naming the
   criterion the diff does not satisfy. A pass carries `lines=`: for every
   criterion, its id and the added line of the diff that meets it, copied
   without the `+`.
```

The push does not change. `code.read` already gives the diff with its `+` lines in both modes (observed: `rota/roles/prompts/critic/answer.tools` and `review.tools`, 2026-10-07).

## 4. The storage and the read

**A column, `verdicts.lines TEXT`, holding the JSON object.** NULL on a fail and on every older row (reasoned: below).

- The `reason` column is the precedent. `init_db` adds it in place with `ALTER TABLE verdicts ADD COLUMN reason TEXT`, behind `_has_column`, with no move of `SCHEMA_MARK` (observed: `rota/core/db.py:233-236`, 2026-10-07). The pass adds `lines` the same way, and adds it to the `CREATE TABLE verdicts` in `rota/core/schema.sql:591-600` for a fresh database.
- A table of rows, `verdict_lines(verdict_id, criterion_id, line)`, would carry a foreign key to `criteria`. The door already checks each key against the batch's criteria, so the key adds no guarantee (reasoned). A table also needs a second write in the op and a reader join in every view, for one verdict's data (reasoned).
- Law 2 holds. The lines are quotes of the diff keyed by criterion id, not reasoning (reasoned: law 2 sends "the reasoning" to the decision record, `rota/LAWS.md`, as quoted in the history read, section 1).
- No reader breaks. Every reader of `verdicts` selects named columns or `1` (observed: `rota/core/lifecycle.py:463`, `rota/core/predicates.py:1168,1233,1262,1420`, `rota/roles/api.py:6785,6839`, `rota/testkit/scenes.py:1034`, 2026-10-07).

**Who reads the lines.**

- The Developer does not. `verdicts.load` selects `id, batch_id, commit_sha, result, failed_criterion, reason` (observed: `rota/roles/api.py:6838-6839`, 2026-10-07), and the select stays as it is. The Developer wakes after a fail, and a fail has no lines (reasoned). The Developer's prompts and their cassettes stay the same (reasoned). The frame's ends-when line says "the Developer's and the person's read". No Developer wake reads a merged batch, so the Developer's part is empty (reasoned: the predicates wake the Developer on `verdict_failed`, `rota/core/predicates.py:1262`).
- The person does. The one place a person reads a merged batch's review today is the cockpit's `verdicts` artefact, the rows that `inspect_api.artefact` serves with the lead columns `id, batch_id, result, failed_criterion, reason` first and every other column after (observed: `rota/cockpit/inspect_api.py:24-46` and `105-135`, 2026-10-07; operating facts line 146, "Inspect with the cockpit"). Today a merged batch's row shows `result=pass` and an empty `reason`. After the change, `lines` joins the lead columns after `reason`, and the row shows each criterion id with the added line the Critic named for it.
- The build session's night report shows `reason` per verdict (observed: `rota/tools/nightreport.py:367-385`, 2026-10-07). The pass adds `lines` to `V_COLS` and prints the count of criteria named per pass. That is the meta workflow's read, and it feeds the measure of section 6 (reasoned).

## 5. The tests

One new file, `tests/rota/test_verdict_lines.py`. Every test calls the real door through `build("critic", db, batch_id=..., mode="review")` and `sb.call`, as `tests/rota/test_desk_guards.py:284` does. The s279 tests need a real batch worktree. The fixture makes a repository whose `src/click/decorators.py` holds the three hunks' context lines, and a batch commit that adds the four added lines of section 1 verbatim (reasoned: the door reads `_batch_diff`, so the diff must come from git, and the added lines are what the door compares).

1. `test_s279_pass_with_a_line_per_criterion_lands`. The call of section 1, the three criterion ids of bg_3. It returns `{"id": "critic:bg_3:<sha>", "result": "pass"}`, and the staged write holds `lines` as JSON with the three keys.
2. `test_s279_pass_with_cr_3_unnamed_is_refused`. The same call without the `cr_3_version_option_show_python_true` entry. `ValueError` with the check 1 words exactly: `a pass names, for each criterion, the added line of the diff that meets it, and cr_3_version_option_show_python_true has no line. Send verdicts.emit again with lines={'<criterion id>': '<the line>'} for each of cr_1_version_option_show_python_flag, cr_2_version_option_show_python_false, cr_3_version_option_show_python_true, each line copied from a line of the [diff] block that starts with +. If no added line meets cr_3_version_option_show_python_true, that is a fail on it: \`verdicts.claim_encodes('cr_3_version_option_show_python_true', encodes=...)\` first, as for any fail`. No verdict staged.
3. `test_s279_pass_with_a_line_the_diff_does_not_add_is_refused`. The `cr_3` value is `import sys`, the line whose absence is the `NameError`. `ValueError` with the check 2 words, `the line for cr_3_version_option_show_python_true, 'import sys', is not an added line of the diff of batch bg_3.` and the rest verbatim. No verdict staged.
4. `test_s279_pass_with_an_unknown_key_is_refused`. A fourth key `cr_4`. The unknown-key words. Optional, because it guards the third shape of check 1.
5. `test_fail_ignores_lines`. A claimed fail with `lines={'x': 'y'}` lands, and the staged write holds no `lines`.
6. `test_the_parser_reads_lines_back`. `toolproto.extract` on the `TOOL:` line of section 1 returns `lines` as a dict equal to the three strings, byte for byte (observed shape: `d170/parse.py`, 2026-10-07 09:03).
7. `test_ten_recorded_passes_are_refused`. Parametrised on the ten `verdicts.emit` texts of the merges read, section 1, verbatim, each with its batch's criteria ids from the night databases (observed: `.rota/clickI_night<n>.db`, 2026-10-07):

| Night, Critic | Batch | Criteria |
|---|---|---|
| 114 s202 | bg_2 | `cr_1`, `cr_2`, `cr_3` |
| 116 s149 | bg_1 | `echo_json_compact`, `echo_json_compact_2`, `echo_json_compact_3` |
| 118 s144 | echo_json_group | `echo_json_compact`, `_2` to `_6`, 6 in all |
| 119 s218 | bg_2 | `cr_1` to `cr_4` |
| 120 s148 | bg_1 | `echo_json_compact`, `_2`, `_3` |
| 120 s180 | bg_2 | `cr_1_confirm_eof_default`, `cr_2_confirm_eof_state`, `cr_3_confirm_eof_default_map` |
| 126 s225 | bg_2 | `cr_1`, `cr_2` |
| 127 s279 | bg_3 | the three of section 1 |
| 128 s142 | bg_1 | `echo_json_compact`, `_2`, `_3` |
| 128 s195 | bg_2 | `cr_1_confirm_eof_default`, `cr_2_confirm_eof_default_false`, `cr_3_confirm_eof_default_value_type` |

Each text goes through `toolproto.extract` and then the sandbox, in the mode the session had: `answer` for s149 and s148, `review` for the rest. Each is refused with the check 1 words, naming all of its batch's criteria as unnamed, 30 of 30. Check 1 reads no diff, so these rows need no worktree (reasoned). All ten refused is right: each pass names no line for any criterion, which is the exact shape the ruling refuses, and the ten are the whole record of what a pass was (reasoned).

Scripted passes that change with the door, so the suite stays green: `judge()` in `rota/testkit/scenes.py:539-542`, used at lines 705 and 1033; `tests/rota/test_arc_seam.py:190` and `405`; `tests/rota/test_delivery.py:589`; `tests/rota/test_desk_guards.py:284-297` (observed: `grep "result='pass'\|result=\"pass\""`, 2026-10-07). Each carries `lines=` for its fixture's criteria, or stands where its batch has no criteria. The implementer reads each fixture to decide which.

## 6. The night

**The measure, from the frame's ends-when line, with this mechanism named.**

1. Mechanism: `verdicts.emit` with `result='pass'` carries `lines`, one added line of the diff per criterion of the batch. The door refuses an unnamed criterion, a key outside the batch and a line the diff does not add, with the words of section 2. `review.md` and `answer.md` ask for the lines in the order of section 3. The cockpit's `verdicts` rows show `lines`.
2. Ratio one: Critic review and answer sessions on a night that land a verdict, from 10 of 10 on nights 114 to 128 to at least 4 in 5. Read from `verdicts` against the Critic's `sessions` rows of the night database. The ratio guards against a door that loops the seat (reasoned: the frame 81 loop, operating facts line 338).
3. Ratio two: of the lines named on a night's passes, those that touch the criterion's words on a read by hand, from 0 of 0 to at least 3 in 4. Read from `verdicts.lines` beside `criteria.text`. A comment line or a docstring line counts as a miss (reasoned: section 2, what the door cannot see).
4. Residue: a Critic session that ends with no verdict is read, turn by turn. The frame closes when its cause is not the new door.

**The recorded Critic cases.** The brief's grep, `grep -o "L1-CR[^\"']*\|ACT-CR[^\"' ]*" tests/rota/*.py | sort -u`, names 2 ids: `L1-CR-fail-names-its-criterion` in `test_fixtures.py` and `L1-CR-challenge-a-claim` in `test_register_key.py` (observed: 2026-10-07 09:04). The grep reads only the test modules. The cases live in `tests/rota/cases/*.yaml`, and 8 Critic cases hold runs in `tests/rota/cassettes.db` (observed: `case_runs` grouped by `case_id`, and `^- id:` in the YAML, 2026-10-07).

| Case | File | Mode | Prompt changes | Change |
|---|---|---|---|---|
| `L1-CR-pass-a-conforming-diff` | `l1_judgement.yaml:6` | review | yes | re-record. A pass now lands only with `lines`, so the case's `verdicts: {count: 1}` measures the new door |
| `L1-CR-fail-names-its-criterion` | `l1_judgement.yaml:70` | review | yes | re-record, expect unchanged |
| `L1-CR-a-test-that-encodes-nothing-is-a-challenge` | `l1_judgement.yaml:296` | review | yes | re-record, expect unchanged |
| `L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist` | `l1_judgement.yaml:384` | review | yes | re-record, expect unchanged |
| `ACT-CR-quote-the-tests-code` | `l1_acts.yaml:315` | review | yes | re-record, expect unchanged |
| `L1-CR-finish-the-review-with-the-answer-in-hand` | `l1_answers.yaml:265` | answer | yes | re-record. `writes: {verdicts: [1, 1]}` now needs a pass with `lines` |
| `L1-CR-dismiss-a-finding-on-a-falsified-constraint` | `l1_judgement.yaml:134` | finding_review | no | none |
| `L1-CR-challenge-a-claim` | `l1_survey.yaml:160` | challenge | no | none |

- A prompt changes where the mode holds `verdicts.emit`, because the advertised signature gains `lines=None`, and where the mode's brief changes (reasoned: `Sandbox.signatures`, section 1). `verdicts.emit` is in `review.tools` and `answer.tools` only (observed: `grep -l verdicts.emit rota/roles/prompts/critic/*.tools`, 2026-10-07).
- Six cases re-record at 5 runs each, 30 runs. The gate classifies them stale first (reasoned: the memory note "rota re-records are cheap").
- The gate's known red `L1-CR` stays a known red until its re-record. The handover of 05:04 names it among the known reds (observed: frame 170's status of 05:04, `plans/stack.md`, 2026-10-07).

## 7. What this design does not do

- The lost `f1`: `findings_find` still writes a second batch's `f1` over the first. Frame 178 holds it.
- The `k0` survey gap: the survey still binds no constraint to `termui.py`, `utils.py` or `decorators.py`. Frame 179 holds it.
- `claim_encodes` with no check: `verdicts_claim_encodes` still records a claim of `True` with no test of it, 29 of 29 on nights 114 to 128.
- The Critic's view limited to the hunks: the review mode still has no `code.source`, so a defect outside the hunks, as s279's missing `import sys`, still passes with three true lines.
