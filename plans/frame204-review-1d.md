# Frame 204, pass 1d review: commit 6a80be2c

Reviewer: Opus, read-only, worktree C:/Users/roman/rota_rv204d at 6a80be2c, 2026-10-12.
Verdict: the pass stands. No finding is high. Four low findings follow, and none needs a pass before the re-record.

## (a) Verdicts

1. Tester sentence: stands. It says both things the read's fix 1 asked, and it has no imperative. One word boundary stays open (finding 1). It does not contradict the encode door, with one soft tension (finding 2).
2. Reconcile sentence: stands. Section 8 puts a README-against-code disagreement in the cell "owed to the principal, could not", as "a conflict of two project sources", so `kind="conflict"` agrees. The missing-claim case fits the word "disagreement" only weakly (finding 3).
3. STE: the two Tester sentences pass at 22 and 20 words. The reconcile bullet runs past 25 words, but it did so before the pass (finding 4).

## (b) Findings

1. `rota/roles/prompts/tester/tests_missing.md:46-49`, low, PLAUSIBLE. The sentence splits "a string" from "a format", and a guessed header name such as `"signature"` is both. The case `L1-TS-an-outside-fact-is-the-researchers` fails on exactly that string. The seat can read the header as "a string the material does not fix" and encode it, and the literal door then stages it as `invented` (`api.py:7058-7081`). Fix: if the re-record still drops that case, add "a name from somebody else's spec" to the `cannot` side, or take the read's fix 2.
2. `rota/roles/api.py:6728-6737` against `tests_missing.md:48-49`, low, CONFIRMED by a read. The invented-import door tells the seat that a missing helper is "the Developer's to add and the criterion's to name", and it offers `msg.question_terminologist`. The prompt now says such a function makes the criterion `cannot`. Both routes reach an owner, and `cannot` with `ambiguous_word` routes to the Terminologist too, so the two texts do not conflict on the outcome. The constant door (`api.py:6518-6523`) and the literal door (`api.py:7072-7081`, "the door stages the row itself") agree with the new text. Fix: none now. Align the import door's offer with `tests.triage(verdict='cannot')` if a re-record shows a seat torn between the two.
3. `rota/roles/prompts/vision_keeper/reconcile.md:12-17`, low, PLAUSIBLE. "A disagreement to log" names a contradiction well. For "the README says something the code did not show" with an empty account, the seat can again find nothing that disagrees. The dictated template "README says <X>; the code shows <Y>" also needs a Y that the missing-claim case lacks. Section 8 gives no separate kind for a claim the code does not show. The table's row 9, `finding`, covers a judgement on an onboarding claim, and the old bullet used that word. Fix: if the one replay of `L1-VK-reconcile-the-readme` stays at 0 of 1, let the template allow "the code shows nothing for it".
4. `rota/roles/prompts/vision_keeper/reconcile.md:12-22`, low, CONFIRMED by a count. The first clause of the bullet is about 25 words, and the bullet holds three topics: the case, the reason, the call. The last paragraph still says "not findings", so the file now uses two words for one thing. Both facts are older than the pass except the word change. Fix: change "not findings" to "not disagreements" in the next pass that touches the file.

Outside the points: none found in the diff. The read's fix 4, the encode door at `api.py:6120` that offers `encodable` after a `contradicts_request` refusal, is untouched, as the brief expects.

## (c) Probes

- `git show 6a80be2c` in the worktree: the diff, two prompt files, five lines.
- `sed` reads of `plans/frame204-gate-read.md:104-200` and `plans/frame204-design.md:76-100, 341-390`.
- `python -m rota.tools.map fn tests_encode`, `fn _literal`, `fn _factory_misuse`. `_literal` is in `rota/llm/toolproto.py`, a parser, and not an encode door.
- `grep` and `sed` reads of `rota/roles/api.py:6510-6525, 6715-6740, 7058-7085`.
- No pytest, no model call, no file edited.

## (d) Usage

Input tokens about 30k, output tokens about 4k, total about 34k (estimate; read the harness line for the true figure).
