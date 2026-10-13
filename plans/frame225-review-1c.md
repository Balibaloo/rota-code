# Frame 225, review 1c: commit df474208, the two-case fold of a contested note

Verdict: does not stand as written. One high finding. The commit closes review 1's high on the plain sign-off page. On a page that carries a batch ref, the batch filter drops the principal's approve before `ruled` is taken. A contested scope note then contests the approved item again. That is night 144's shape. The fix is one line.

Rota workflow throughout. Worktree C:/Users/roman/rota_rv225c at df474208. Reviewer: read-only agent, 2026-10-13.

## (a) Verdicts on the numbered points

1. Holds on the sign-off page. CONFIRMED by probe: a conflict note contested with no ruling on its item contests the item, and the relay refs are ["echo_json"]. The same note with an approve on the item leaves the item approved.
2. The resume case is rare and does no harm by itself. A resume needs a page ref whose items are all set aside (api.py:7786-7791). The pop before `ruled` has a sibling that matters more: see finding 1.
3. `ruled` is the wrong source, but not because of its extra keys. A ledger id or a batch id in `ruled` only stops a note about that row from adding a contest that the answer already rules. The defect is the keys that `ruled` lacks: see finding 1.
4. All four tests pass at df474208 (CONFIRMED, pytest -k, 4 passed). By reading the code: the scope test is red on the grandparent only. The default test is red on neither. The conflict test with no ruling is red on fca24dbc only. The conflict test with an approve is red on the grandparent only. The scope test and the conflict-with-approve test test the same thing with a different kind.
5. Three of four sentences hold. Sentence 2, "only when the answer gives no ruling on that item", is false where land() drops the ruling before the fold (finding 1). Sentence 1, "always", omits the observed and stamped guards below it.
6. Holds. `git show df474208 | grep -c $'\r'` printed 0.

## (b) Findings

1. rota/roles/principal.py:1797, with the filter at 1739-1744. Severity high. CONFIRMED.
   `ruled = set(per_item)` reads per_item after two filters and the resume pop. The batch filter removes every item approve when the page carries a batch ref. The stamped filter removes approves of stamped rows, but the fold guards those separately. The probe built a page [b1, echo_json, L9] with echo_json approved and batch b1 pending. The answer {"echo_json": "approve", "L9": "contest"} on a scope note gave verdict {"L9": "contest", "echo_json": "contest"} and approval contested. A contested item revokes the batch, which is the loss night 144 showed. The same pop makes a resumed item count as not named (point 2).
   Whether a live page carries a batch ref and a ledger note together is not checked here. The touch-note page carries a batch ref.
   Fix: take the set from the principal's own answer: `ruled = set(answer.per_item or {})`.

2. tests/rota/test_signoff_assumptions.py:283 and 295. Severity low. CONFIRMED by reading.
   The docstring "The test is green on the parent of fca24dbc and red on fca24dbc" is a history note, and it goes stale at the next commit. It says nothing about the behaviour the test checks. The conflict-with-approve test duplicates the scope test with another kind. No test covers a page with a batch ref.
   Fix: state the behaviour in the docstring, and replace the duplicate with the batch-page case of finding 1.

3. rota/roles/principal.py:1772-1778. Severity low. CONFIRMED by reading.
   Review 1's finding 3 is still open. The block comment still says that every contested assumption contests its row. The new comment's sentence 2 is false on the batch page until finding 1 is fixed.
   Fix: in the block comment, name the two cases and the guards, and point to the comment at the fold.

4. Outside the points. rota/roles/principal.py:1830. Severity low. PLAUSIBLE.
   A Critic row has about_ref "items:X". That ref never equals an answer key, so it is never in `ruled`. If review 1's finding 2 fix stamps the Critic rows as finding, each contest writes per_item["items:X"], which updates no item and goes into the relay refs.
   Fix: resolve a table-prefixed about_ref to the bare id before the `ruled`, observed and stamped checks.

## (c) Probes

- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/80cae596-3d3e-44f8-a0fe-b9ff034a378c/scratchpad/rv225c/probe.py. The probe loads land() from the worktree at df474208. It builds the test file's fixtures on a fresh init_db and lands four answers. A: conflict note, {L9: contest}: echo_json contested, refs ["echo_json"]. B: conflict note with an approve: echo_json approved. C: scope note, page [b1, echo_json, L9], item approved, batch pending, with an approve: echo_json contested. D: the same with a default note: echo_json contested, as A1 says.
- pytest on tests/rota/test_signoff_assumptions.py -k "note_s_contest or default_s_contest" at df474208: 4 passed.
- git show df474208 piped to grep -c for CR: 0.

## (d) Usage

Input tokens: about 35k. Output tokens: about 5k. Total: about 40k. The harness line holds the exact count.
