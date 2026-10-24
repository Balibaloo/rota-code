# Frame 258, review 1 of f77bf455 (parent a3f2f96e)

Verdict: accept with one fix. 0 high, 3 low. The fix is finding 1.

## (a) The verdict on each point

1. Holds. The predicate changes only in the last branch of the line-1 refusal, and no other line's reading changes.
2. A false refusal exists and is CONFIRMED on the full door path. The cost is low: the correction still reaches the criteria.
3. Every changed assertion changes the refusal text only. No ruling path changes. Frame 234 judged the old text. Nobody ruled it or measured it.
4. None. No recorded case holds the old text or "have no ruling".
5. One wrong match, CONFIRMED: "Do not keep the change." now reads as a keep.
6. `11 passed in 0.77s`.

Point 1, the predicate in one sentence: an unnumbered sentence spares a line-1 contest only when it opens with a build verb, or when it shares a content word with the request that no faulted line's text holds.

Point 1, the reach. `faulted_texts` is read in one place only, `_names_request`, at `rota/roles/api.py:10675`. That call is past every earlier exit of `_line_refusal`: `request_first`, `1 in contested`, `not quoted`, `named` non-empty, `1 not in faulted`, and no reference to line 1. So an approve, a park or a question on line 1 never reaches it. `faulted`, `matched`, `contested` and `_unnamed_contest` take the same inputs as at the parent. The new SQL at `api.py:11507` reads the texts and writes nothing. The new text replaces the old one only where the old text fired.

Point 2. A false refusal is easy to make on a page whose criteria restate the request. On m66, cr_1 holds every request word except "let" and "take". The probe sent "Lines 2 to 4 are wrong. The default on a closed stdin should always be False, not a flag." with line 1 contested. The full door path refused line 1 with the new text, and the parent admitted it. "Actually confirm should raise a clear error when stdin is closed instead." gave the same result. These sentences change the request itself. "Make the flag default to True." still lands, because it opens with a build verb. The chance on a real page is moderate. A request correction in the request's own words usually has no word of its own. The seat then approves line 1 and contests lines 2 to 4. The criteria writer gets his words, the item text stays the old one, and the batch goes on. A later page can show the item and let him contest line 1 by number. No night count measures the rate. Provenance section 6 already names that gap.

Point 3. The diff has 8 hunks. The 3 tests through `_rule_request` run the full path with the subtraction, and they were refusals before and stay refusals. The 5 tests through the helper `_refusal` pass no `faulted_texts`, so the subtraction cannot fire there. Each hunk swaps "Line 1 is the request" or "approve the rest" for the new text, and keeps the raise or the not-None. Frame 234's block is in `plans/archive/stack-2026-10-15.md`, not in `plans/stack.md`. The block says the session judged the text at pass 1 and changed only its pronoun. No ruling and no measurement stand behind it. Night 159's s241 and night 161's s181 then measured harm from "approve the rest".

## (b) Findings

1. `rota/roles/api.py:10700`, `_KEEP_CHANGE`. Low. CONFIRMED. The new pattern is `\b(?:don['’]?t|do not)(?: want to)? (?:drop|give up)\b|\bkeep going\b|\bkeep the change\b`. The branch `\bkeep the change\b` has no guard for a negation. "Do not keep the change. Abandon it, I asked for something else." with line 1 contested and no line faulted gives the refusal "The words do not fault line 1, and they ask to keep the change. Approve line 1." The parent admitted that contest. `_CUE_KEEP` at `api.py:10724` copies the pattern, so the cue reader inherits the match. Fix: put a negative lookbehind for "not " and "n't " before `keep the change`, and add the probe sentence as a test.
2. `rota/roles/api.py:10860`, the subtraction in `_names_request`. Low. CONFIRMED on the full door path, as point 2 says. A request correction in the criteria's words is refused, and the route says approve line 1. Fix: none for this frame. Count the shape over the nights' records before a later pass widens the spare.
3. `tests/rota/test_frame234_verdict_lines.py:339`, the helper `_refusal`. Low. CONFIRMED by a read. The helper passes no `faulted_texts`, so 5 of the 8 changed tests run the old spare and not the new one. Only `test_frame258_request_line.py` covers the subtraction. Fix: let `_refusal` take `faulted_texts`, and pass the criteria texts on the m167 and night 155 tests.

Outside the points: none at high. The neighbour files `test_request_page.py`, `test_frame250_verdict_faults.py`, `test_frame296_revise_note_text.py` and `test_park_page.py` give `144 passed, 5 xfailed`. `test_frame234_verdict_lines.py` gives `89 passed, 4 xfailed`. No prompt under `rota/roles/prompts` quotes the old text.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b00cc646-4611-4fd9-8f73-b6b404eeda3a/scratchpad/f258r1/`.

- `probe_false_refusal.py`: five request corrections through `_line_refusal`, with and without the criteria texts. The script also checks `_KEEP_CHANGE` on six sentences.
- `probe_full_path.py`: a spy on `_line_refusal` under the m66 fixture. The spy showed the door refuses REST, M67 and the false-refusal sentence on the full path.
- `probe_keep.py`: the negated keep through `_line_refusal`.
- pytest with `-n 0` on the 6 test files above, in `C:/Users/roman/rota_p258`.
- Greps: `tests/rota/cases/*.yaml` and `rota/roles/prompts` for the old text and for "have no ruling".

## (d) Usage

Input about 60k tokens, output about 9k tokens, total about 69k.
