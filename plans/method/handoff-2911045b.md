# Momentum note of session 2911045b, peer name rota-24

Message rota-24 for anything this note withholds or you doubt. I keep the last of my context to answer, and I stop when you message the word released. Written on 2026-10-28 at the hand-off, after night 172 launched. Read `CLAUDE.md` first, then `python -m rota.tools.state --sid <your sid>`, then this note, then frame 344's status lines of 2026-10-28 from 02:06 onward. Meta workflow.

## Roman's ask, met

Every fix of sprints 28 to 31, W3 and the `how_it_works` cause lands before night 172, with a gate on each (ruled: 2026-10-26 23:4x and 2026-10-27 19:32, on frame 344). Done at de1203a9: 37 of 37 facts stand on `rota/foundation`, each with a review record in `plans/f<n>-review-p1.md` and a touched-file run, and two full gates on the head. The second gate, 873s, gave the six known case reds and nothing else, stale 0. Partial gates per land and one full gate before the night were his ruling of 2026-10-28 01:05.

## Night 172

Launched from `.rota/launch_night172.sh` at de1203a9, cold, items 163 rotated, profile local, log `.rota/night172_launch.log`. Night 1 of 3 for frames 330, 339, 340, 324, 341, 343 and 344 on the new baseline. The read is yours, by fact, against each frame's Ends-when. Read `plans/night171-read.md` for the shape of a read. Candidates the day left for the read: night 170 W1's 12 refusals at the Tester's test-file door, which F35 did not touch because that door reads `tests` and not the prediction (the F35 review, finding 1); the tree walk of `project_tests` (the F8 review, finding 6); the F12 route text, which now names the body's own library, so a recorded refusal with the old click text can differ.

## Debts on frame 344, each named in a pin or a review

- F15: `_is_request_item` keeps its own description check. The swap turned 119 fixture tests in 17 files red, because their items cite no statement, and night 37 held such an item. A fixture pass decides whether an item with no statement belongs to a request.
- F10: the pin passes an own-regex item reader (the F10 review, finding 4).
- F13: `_vet_surface`, `_program_modules` and the `module_of` calls in `tests_encode` pass no staged writes, and `staged_writes` runs `git ls-files` and hashes every `.py` file per call, unmeasured on a large tree.
- Frame 233's store: 358 recorded prompts hold the runner's cut note and 0 rows a reason until a re-record, and the litellm backend returns no raw (the F33 review, findings 2 and 3).
- F11: 5 pair splits of index rows stay, named in the pin.
- F33's ceiling list holds 28 debts that name frame 144 or no frame, 8 with a line number that moves on an edit above it.

## Judgements I made in place of a question to Roman

Each is on frame 344's status lines with its reason. The ones that touch his rulings: conftest.py is test-shaped by his basename ruling of 2026-10-26 20:37; `code.commit` keeps its old acceptance by his ruling of 2026-10-17 against a new commit refusal; frame 301's click literal test changed by his rule against over fitting. One question rota-33 left is still not asked: should a later request reword the approved account? Recommended: no, it stays, and the `how_it_works` build enforces that.

## What to doubt

Doubt first the merges: ten branches landed through api.py in one day, four by hand-resolved conflicts (f8root, f26root, f10root, and f13root by a builder), and one of mine dropped an import that the pins caught. The second full gate is the check. Doubt second the one-reader pins: three reviews found a plant that passed a pin, and each was fixed, but a pin by name is weaker than a pin by behaviour. Doubt third the night's model: two Developer cases were red before any land today and are in the known set, so a Developer wall on night 172 may be older than the day's fixes.

## Worktrees

`rota_f2`, `rota_f35`, `rota_f15`, `rota_f22`, `rota_f13`, `rota_f10`, `rota_f8`, `rota_f24`, `rota_f26` under `C:/Users/roman/` are landed and can be removed with `git worktree remove`. `rota_g328` on `land28` is the gate worktree at de1203a9, and its `cassettes.db` is the newer register. `rota_n172` is the night's.
