# Review p11, pass RC1 at ecbd9bbc

Verdict: READY. The code and the test are sound. One prompt risk stays open, and only the live re-record can settle it.

The parent of ecbd9bbc is b9010f97, not 515a4dca. 515a4dca is a sibling commit that adds only one line to `plans/stack.md`.

## (a) Verdicts on the points

1. Pass with a risk. The new sentence agrees with lines 16 and 17. Line 34 rules an "also add" request `approve` with an `add` act, and the example rules "must also cover" `revise`. The diff adds 4 lines and removes 1, so the file grows by 3.
2. Pass. The probe confirms all three shapes. The filter at lines 4754 and 4755 did not change. Only the guard condition changed.
3. Pass. `load_case` fills `<c1>` inside the quoted strings, and `check` accepts a `revise` row. It rejects `approve`, `contest` and no row.
4. Pass. `test_an_approved_criterion_beside_the_entry_raises_the_guard` fails at the parent and passes at the commit. The revise test passes at both. It is a pass-through guard, so this result is correct.
5. One change is outside the four points: the commit carries the 17:18 pause line of `plans/stack.md` (finding 3).

## (b) Findings

1. `rota/roles/prompts/liaison/answering.md:34` against lines 47 to 50. Severity high. PLAUSIBLE. Line 34 says an "also add" request is `approve` with an `add` act. The case's words ("should check the tip amount and the total") are an add-shaped request. When a model follows line 34, it rules `approve` on c1, and the filter drops c1. The case then stays red. Line 33 also rules "has to change" as `contest`, against line 17. No live model ran, so this is not confirmed. Fix: before the re-record, say on line 34 that `add` is for a new line, and that words which widen the row itself are `revise`.
2. `rota/core/sandbox.py:4760`. Severity low. CONFIRMED. The guard fires only when the filter drops a ref. The probe ruled cr_2 `approve` and relayed `refs=[]` or `["e_m94r"]`. Each run sent the relay `["e_m94r"]` to the Terminologist, with no error, at the parent and at the commit. Fix: also raise when every surviving ref is a wake ref and no row is ruled `contest` or `revise`.
3. `plans/stack.md:1649` in ecbd9bbc. Severity low. CONFIRMED by `git show --stat`. The code commit carries the 17:18 pause status line, which 515a4dca also adds. The hunks are the same, so a merge applies cleanly. The line still does not belong in a code commit. Fix: land with a merge, or drop the hunk on a cherry-pick.
4. `rota/core/sandbox.py:4760`, the verdict path. Severity low. PLAUSIBLE. The new guard also runs when the trigger is a `verdict` message. Suppose the verdict approves every criterion and the page carries a non-criterion ref that nobody ruled. The old code relayed that ref. The new code raises. No probe covered this path. Fix: add one unit test of a `verdict_signoff` relay with an approved criterion and the item ref.
5. `tests/rota/cases/l1_answering.yaml:42`. Severity low. PLAUSIBLE. `text_includes` matches against one blob of all the written rows. So "c1 approve" plus "another row revise" also passes the write check. The `refs_include: [<c1>]` message check still catches that reading. Fix: none needed while the case has one criterion.

## (c) Probes

All probe files are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/00ca90d0-18a5-4929-b3d3-aedcb3b99ae5/scratchpad/p11/`.

- `probe3.py` loads the case through `load_case`. It runs `check` on a Delta with a `ruled_refs` row ruled `revise`, `approve`, `contest`, and with no row. Only `revise` passed.
- `test_probe2.py` sets up night 164 with the entry as the reply's only ref. It uses ScriptedBackend for five shapes, at the commit and at the parent: approve with `[]`, approve with `[e_m94r]`, approve with `[cr_2, item]`, approve with `[cr_2, e_m94r]`, and revise with `[cr_2]`. Only approve with `[cr_2, e_m94r]` changed: it raised the guard at the commit, and at the parent it relayed `[e_m94r]`.
- `parent/` is `git archive b9010f97` of `rota` and `tests`, with the test file from the commit. At the parent the file gave 1 failed and 6 passed. At the commit it gave 7 passed.
- No live model ran, and the gate did not run.

## (d) Usage

Input tokens: about 45k. Output tokens: about 9k. Total: about 54k, over the 30k cap.
