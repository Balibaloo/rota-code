# Review p7: frame 345 pass 5, commit 96b303ea on seam5root

READY. Five points hold. Two low findings, none blocks.

## (a) Verdicts

1. Holds. The diff maps `keep` to approve in `RULING_WORDS`, removes it from `WORD_ACTS` and `_WORD_KINDS`. No other word moves.
2. Holds. `ruling_rows` (principal.py 1121-1129) writes one row per page line of a ref. Both rows copy `own`, so both carry the ref's verdict. The new test asserts lines, verdicts and two ids. Two different words on two lines of one ref collapse to one verdict, because the door holds one value per ref. No case of the 24 has that shape: m47-m48 is the only repeat, and lines 8 and 47 both expect contest with drop.
3. Holds. `landing.md` is 40 lines. The `keep` bullet is gone. The approve bullet adds "keep line 4". The revise, exclude and add bullets carry the brief's sentences, and the exclude example is one of the two quotes.
4. The fall is the seat's variance, not the change's. The words are "Line 5 is wrong: ... should be named as expected". The new revise sentence forbids revise on those words. No sentence of this pass pulls toward revise. The case's history swings: 3/3 (l3r_gemma_2c), 0/3 (l3r_main_2c), 0/3 (l3r_main_3), 2/3 (dfec94a6), 1/3 now.
5. Holds. The three files give `72 passed in 5.71s` with `ROTA_L1` unset.

## (b) Findings

1. `rota/roles/prompts/liaison/landing.md`, lines 14 and 20. Low. PLAUSIBLE: "keep line 4" sits under approve, and "Keep line 5 to the terminal module" sits under exclude. The seat reads one verb in two bullets. The report shows the exclude lines still get revise in 3 of 3. Fix: use the other quote, "drop the utils file" is there already, so take "remove the five formatting tests" as the second example, or leave it and watch pass 6.
2. `rota/roles/api.py`, about line 11692, the `_ruling_word` refusal. Low. CONFIRMED: the refusal text names drop, remove and strike as contest and does not name keep as approve. A seat that reads the refusal learns no route for keep. The builder names this as a deviation. Fix: add "keep is approve" when a recorded case does not re-earn.

## (c) Probes

- `git diff e98b8785 96b303ea -- rota/ tests/` from the worktree: the four files above, +50 -10.
- `grep -c "" landing.md`: 40 at the commit, 41 at the parent.
- `sed -n 1085,1135p rota/roles/principal.py`: the loop over `order` that writes the repeat rows.
- `grep m61-m62` over the scratchpad logs: the five run histories in (a) 4.
- `sed -n 469,534p seam5_after.txt`: runs 2 and 3 give line 5 revise, act None.
- A Python read of `tests/rota/cases/l3_rulings.yaml`: m61-m62 words and expect, m47-m48 expect for lines 8 and 47.
- `pytest tests/rota/test_seam2_word_per_line.py tests/rota/test_f2_rulings_words.py tests/rota/test_ruled_refs.py -q -p no:cacheprovider`: 72 passed.

## (d) Usage

Input about 60k tokens over seven calls. Output about 3k. Total about 63k. Under the 20k output cap.
