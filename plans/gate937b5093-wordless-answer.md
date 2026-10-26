# Gate 937b5093: why the wordless-answer case fell to 2 of 5

Case `L1-DV-a-wordless-answer-leaves-a-wrong-test-alone`, model qwen3:8b,
case file `tests/rota/cases/l1_answers.yaml` line 45, `runs: 5`, `pass: 4`.
Register `C:/Users/roman/rota_g328/tests/rota/cassettes.db`, read-only.
The gate tree `C:/Users/roman/rota_g328` is at 937b5093. `rota/core/sandbox.py`
has no change from 937b5093 to HEAD.

## Result

The cause is B. The seat changes the test line it quotes, and the strict
check refuses the quote as ruled. The comment strip is not the cause. In
the 3 failing runs, the seat writes `custom_version_option(cmd, show,
show_python=True)`. The row says `custom_version_option(cmd,
show_python=True)`. The seat inserted the token `show, `. With that token
removed, the quote is the whole test body, and the door admits it,
comment lines included.

Recommendation: hold the case as a measure of the model under the ruling.
Do not change `_challenge_evidence`.

## The recordings

| Recording | Seqs | Time | Passed |
|---|---|---|---|
| Before frame 328 | 560857-560861 | 2026-10-26 01:06 | runs 1, 2, 4, 5 (4 of 5) |
| Gate 937b5093 | 562638-562642 | 2026-10-26 02:48 | runs 3, 5 (2 of 5) |

Both recordings have the prompt hash `eb168e091a115290`. Seqs 562643-562647
replay the new recording with the same results.

## 1. The 3 failing runs (562638, 562639, 562641)

The grader expects one message to the Tester, verb `challenge`, with the
decision row `<d1>` in its refs. The forbidden calls are `code.write` and
`code.commit`. Each failing run reports `got 0 match(es)`.

The seat sent the same shape in all three runs:

1. Call 1 sends refs `[criterion, test, decision]` and `quotes=` as one
   string. The string is the whole test body, with escaped line breaks and
   the token `show, ` inserted. The door refuses it against the criterion:
   "it is not in the live text of c_...".
2. Calls 2 to 4 send `quotes=` as a list of two strings. The first string
   is the criterion, verbatim. The second string is the whole test body
   with `show, ` inserted. The door refuses the second string: "it is not
   in the live text of tst_... A comment of the test does not count. Quote,
   not paraphrase".
3. The seat repeats call 2 verbatim twice. The loop ends with "repeated its
   previous turn verbatim twice; ended". No message goes out and no
   decision row is written.

The seat's `reason=` carries the same inserted token in all three runs. The
seat reads the line wrongly. It does not only copy the line wrongly.

## 2. Is the refused quote verbatim from the row?

No. A check with the gate tree's own functions shows this:

| Check | Quote as sent | Quote without `show, ` |
|---|---|---|
| `_span_of(q, body)`, row with comments | False | not run |
| `_span_of(_code_only(q), _code_only(body))`, the door's check | False | True |
| quote equals the body after `strip()` | False | True |

So the only change the seat made is the inserted `show, `. The comment strip
is symmetric. `_cites` in `_challenge_evidence` (sandbox.py line 1545)
applies `_code_only` to the quote and to the row. A verbatim quote that
holds comment lines passes. The passing runs show this too (see section 3).

The review `plans/frame328-review-p2b.md`, point 8, named lines after a `#`
comment as the risk. The register does not show that risk in this case. The
old door admitted these quotes because the old check found any 12-character
window of the row in the message. The new check needs the whole quote to be
a span of its own row, so the one inserted token now fails the quote.

## 3. The 2 passing runs (562640, 562642)

The seat copied a short span of 2 to 4 lines, verbatim, and did not insert
the token. Both spans start with a `#` comment line, and the door admitted
them.

- Run 3 (562640) first sent bad refs and a quote that was its own reason.
  Then it quoted `# Apply decorator ...` and the `decorated = ...` line,
  verbatim. The door refused that quote because the run names the red line
  `result = decorated()`. The seat then quoted the `# Call the decorated
  function ...` comment and `result = decorated()`. The door admitted it,
  and the challenge went to the Tester. In the old recording, run 3 failed
  because `reason=` copied the quotes.
- Run 5 (562642) first named no criterion, then sent a quote that was its
  own reason. Its third call quoted the comment line and the last three
  lines of the test, verbatim. The door admitted it.

The difference is the size of the copy. A short span stays verbatim. A copy
of the whole 16-line body picks up the inserted token, and qwen3:8b does
the same in 3 of 5 runs.

## 4. Cause and recommendation

Cause: B. The seat changes the quoted line, and the ruled check (DECISIONS
1290, a contiguous span of the disputed row, verbatim) refuses it. There is
no door gap at the comment strip.

Recommendation: hold the case as a measure of qwen3:8b under the ruling.

A note for the frame that owns the door, not a fix: the refusal says "A
comment of the test does not count" in all three runs, and comments were
not the fault. The refusal does not name the first word where the quote
leaves the row, and the seat sent the same call again twice. A refusal that
names the departing word is a possible lever. It is a change to the door's
text, so it needs a frame of its own.
