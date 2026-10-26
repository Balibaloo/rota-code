# Frame 336, the agency read: does the check-line fix sit at the source

Date: 2026-10-26. Read at 46e5c88b on `rota/foundation`. Read-only. The night
databases were read from a copy in the session scratchpad with `?mode=ro`. No
pytest ran. Brief: `agency_336.md` in session 8db3a3f9's scratchpad.

## The result

**At one door of 4: the fix covers 2 of 4 one-line readers that show the
first `E ` line of a red run as its error.** The 2 that it covers both read
`_failure_line`, the page's check line and the builder's last attempt. The 2
that it leaves are Developer and Tester texts in `rota/core/sandbox.py`
(observed: section 3). A fifth reader already took the last `E ` line of a
collection error 12 hours before the frame was pushed, with its own detector
(observed: `rota/roles/api.py` 17603 to 17617, 5ae7f5f5). So the frame
re-derived a rule that the code held (reasoned: section 2). The harm that
the fix leaves is small, because the seats also get the whole output
(reasoned: section 4).

## 1. The purpose

`_failure_line` and the `Fails: {why}` tail came in b0a2086e, 2026-10-09
00:48, frame 142, "A park ask gets an answer that names no option"
(observed: `plans/c5-check-line-provenance.md` section 1). Frame 142 served
Roman's ruling that the park ask is a page with rows, where a row shows its
test's expectation and whether that test is red (ruled: Roman, 2026-10-08
23:25, `rota/DECISIONS.md` 1459 to 1465). The choice of the first `E   `
line is frame 142's design, not his words. The design took it because pytest
cuts the `FAILED` line to the terminal width, as tr248 of night 132 showed
(observed: `plans/frame142-design.md` 343 to 345 and 751 to 756). The design
had only assertion reds in view (observed: the same file, line 327).

## 2. What exists

| Reader | File and line | Rule on a red run | Who reads the text |
|---|---|---|---|
| `_failure_line` | `rota/roles/principal.py` 512 to 524 | first `E   `; last when the first is `File "...", line N` (3380cebf, 1cd3fb39) | Roman: check line 564, builder's last attempt 1537 |
| `_note_collection_error` | `rota/roles/api.py` 17603 to 17629 | pytest's `ERROR collecting` header marks a collection error; last `E ` line | Tester, the encode note (frame 328, 5ae7f5f5, 2026-10-26 07:51) |
| `_base_quote` | `rota/core/sandbox.py` 2062 to 2066 | first `E ` line, strips one period | Developer, "The base run said: ..." at 2097 |
| `_red_line_refusal`, `said` | `rota/core/sandbox.py` 1212 to 1213 | first line that matches `E\s{2,}\S` | a seat, "its run names the line it fails at" at 1226 |
| `_first_error`, `_red_of` | `rota/core/db.py` 762 to 773 | first `E ` line, addresses blanked | no reader; the red's identity |
| `_tail` | `rota/core/harness.py` 189 to 201 | keeps the first `E ` line at a cut | no reader; the red's identity (frame 318) |
| `tests_load` `said` | `rota/roles/api.py` 10923 | whole output | Developer and Tester |
| `_failed_run_blocks` | `rota/core/runner.py` 3446 to 3467 | whole output tail, raising line first | a challenged seat |

No shared helper names "the error of a run" (observed: grep for
`startswith("E` and `E\s` in `rota/`). Each reader scans the stored output
with its own rule (observed: the table).

## 3. The reach

The cause by the code: each one-line reader of `test_runs.output` takes the
first `E ` line as the error. On a SyntaxError at collection, that line is
the traceback frame (observed: tr35 of night 168, its four `E` lines). The
instances with the same gap:

1. `rota/roles/principal.py` 564, `check_line`, through `_failure_line`.
2. `rota/roles/principal.py` 1537, the builder's last attempt, through
   `_failure_line`.
3. `rota/core/sandbox.py` 2065, `_base_quote`. 0 base reds on nights 160 to
   169, so the instance is latent (observed: the `base_run:` rows of
   `config`).
4. `rota/core/sandbox.py` 1213, `_red_line_refusal`. Its `said` is the
   traceback frame on 8 of 8 traceback-frame runs (observed: a scan of
   `test_run_journal`, nights 160 to 169).

Count: 4. Readers that I checked and that are not instances:

- `db.py` 762 and `harness.py` 200 want the first line, for a stable
  identity (observed: `plans/c5-check-line-provenance.md` section 1).
- `runner.py` 3116 shows the frame and the source line, and the 700 tail
  holds the error (reasoned: tr35 is 1,835 characters).
- `runner.py` 3324 needs a location line of the test file, and tr35 has
  none (observed: tr35).
- `runner.py` 3433 labels the run "failed before any assertion", which is
  right for a collection error (reasoned: no assert line is named).
- `api.py` 17039 needs a `>` mark, and `api.py` 17483 reads only an
  `AssertionError` (observed: tr35 has neither).

The scan over 318 reds: 8 have a traceback frame first, 12 carry the
`ERROR collecting` header, and all 8 are among the 12. The other 4 are
ImportErrors whose first and last `E ` lines are equal. So the header rule
and the frame rule give the same line on all 318 (observed: the scan).
No test or scene encodes `Fails: File` (observed: pass 1 report, part b).

## 4. The fix against the reach

The built fix covers instances 1 and 2, because both read `_failure_line`.
It leaves 3 and 4 (observed: 3380cebf, 04fd2bfa, 1cd3fb39 touch
`principal.py` and `tests/rota/test_park_page.py` only). It also adds a
second detector of a collection error beside `_COLLECT_HEADER` in
`api.py` 17603 (observed: principal.py 522). That is two rules for one fact
of one record, the shape of cause 12 (reasoned: `plans/wall-guide.md`).
The harm that remains is smaller than the harm fixed. The page is his only
view of the run, and a seat also gets the whole output from `tests_load`
and `_failed_run_blocks` (reasoned: section 2).

## 5. My proposal

Not the same fix. One reader at the record, used by every one-line reader:

1. Add `error_line(output)` to `rota/core/harness.py`, beside `_tail`,
   because harness writes `test_runs.output` (observed: harness.py 180 to 183).
2. Its rule: pytest's `ERROR collecting` header or a frame-first `E ` line
   gives the last `E ` line, else the first (observed: api.py 17603, 17617).
3. `_failure_line` keeps its period strip and calls it (observed:
   principal.py 512 to 524).
4. `_base_quote` and the `said` of `_red_line_refusal` call it (observed:
   sandbox.py 2065, 1213).
5. `_note_collection_error` calls it, `_first_error` and `_tail` stay, and
   one test per reader seeds tr35 (observed: db.py 762; test_park_page.py).

Price: one resumed implementer pass, 24k to 40k on its line, and one
resumed review, about 18k. That is 2 cycles, about 20k of the holding
session (observed: `plans/operating-facts.md` 239 onward, cost anchors).

## 6. The doubt

- I did not count whether the refusal of instance 4 fired on nights 167 or
  168, so its harm on a night is not measured.
- I did not run the four readers on the 8 runs. The equality of the two
  detectors comes from a scan of mine, not a test.
- Cause 11 says "Escalate. Always" (observed: `plans/wall-guide.md`). The
  frame did not escalate, and I did not check whether the provenance's
  "no departure" exempts it.

## Verdict

`at one door of 4`: the fix covers 2 of 4. It leaves `_base_quote`
(`rota/core/sandbox.py` 2065, latent) and the `said` of `_red_line_refusal`
(`rota/core/sandbox.py` 1213, 8 of 8 runs). It also leaves a second rule for
a collection error beside `api.py` 17603.
