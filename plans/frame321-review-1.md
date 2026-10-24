# Frame 321, review 1: the prints door reads prose words only

Verdict: stands, with two mediums. Worktree `C:/Users/roman/rota_r321` at cb4ed2c9, read-only. The old door is the one in `D:/repos/rota` (2acadc36, no door line differs from 7b8a5f27).

## (a) The points

1. Stands. `PRINTS` and `RETURNS` have two readers: `_contradiction_offer` (api.py 7260 to 7267) and the `uses_return` block (10019 to 10058). Both read through `_plain_words` and `_family_hits`. `_verb_words` is gone.
2. Stands, by design. An index symbol `show` or `display` stays prose (7356 to 7360): "show defaults to false." with `src/x.py::show` indexed is refused on "show", and the same text with the name backticked lands. "display displays the value." is refused on "displays" in both forms. `HelpFormatter.write` in the index leaves "write" prose, and reading 8 stays refused.
3. Stands for the sentence rule, and the prints sentence wins. "The docstring of f includes an example. The helper prints the value." is refused. The same text under an item "fix the docstring of f" lands. See finding 3.
4. Stands. The ten readings match the table: 1 and 3 to 8 refused with the full text, 2, 9 and 10 landed. On the old door 2, 9 and 10 are refused.
5. Stands, with one correction to the brief. "echo_json prints an object as JSON." with a return-value test is refused on both doors with the same text and no `ledger.log` offer: the criterion's own word takes the law 11 branch (10059). The `ledger.log` offer belongs to the material branch (10063). The night 28 test in `test_desk_guards.py` 4001 passes.
6. Stands. `test_l1.py -k TS` on cb4ed2c9 against a copy of the cassettes: 23 failed, 134 passed, 1 skipped. Three by name fail on the old door too: `L1-TS-fix-a-test-that-asserts-more-than-its-criterion`, `L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner`, `L1-TS-act-on-the-reason-of-a-challenge`. No STALE count: `casestatus` against the main database printed nothing in 280 s, twice. The worktree holds no cassettes and reports 0 stale, 166 never measured.
7. Does not stand on "e.g." and "i.e.". See finding 2. A colon does not split. A text with no full stop is one sentence.

## (b) Findings

1. Medium, CONFIRMED. api.py 7324 to 7335 and 10017 to 10020. `_about_text` reads the whole sentence, so a text word in the object cancels a true prints verb. "The command prints the help text and exits." lands a return-value test. So do "echo_json shows the error message text on a bad object." and "echo_json prints each comment line of the file." Click criteria say "prints the help text" often. Fix: cancel the prints word only when the text word stands before the verb in the sentence.
2. Medium, CONFIRMED. api.py 10014, `re.split(r"(?<=\.)\s+", ...)`. The split cuts after "e.g." and "i.e.", so "The docstring of f, e.g. shows the path as c.txt." is refused on "shows". The same with "i.e." is refused. This is the wall of night 164 in a common shape. Fix: split on a stop that a capital letter follows, or exclude a token of one letter before the stop.
3. Low, CONFIRMED. api.py 10011 and 10018. An item that names a docstring cancels every prints word in the criterion, the ticket and the statements. "The helper prints the value." under "fix the docstring of f" lands. The report names this deviation. Fix: let the item cancel only the sentences of the criterion that share its text word.
4. Low, CONFIRMED. api.py 7354 to 7360. A surface ref strips a prints word as a name, the index does not. "show defaults to false." is refused when `show` is only indexed and lands when `show` is backticked. The report chose this limit. Fix: none, or state the asymmetry in the docstring.
5. Low, CONFIRMED, outside the points. api.py 10014. "has an example.The helper prints the value." with no space after the stop is one sentence, and the docstring word cancels "prints". Fix: the same splitter change as finding 2 does not cover this. Split on a stop before a capital letter with or without a space.

## (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/48122667-6b95-4100-a43b-30ec9c6540dd/scratchpad/f321_probe.py`: the ten readings, points 2, 3, 5 and 7, run from both roots. Night 164's database gave reading 10.
- A second inline probe printed the full refusal texts for 2a, 2b, 3f to 3h and 7a.
- `pytest tests/rota/test_frame321_prints_prose.py`: 12 passed. `pytest tests/rota/test_desk_guards.py -k printing_surfaces_return_value_logs_the_assumption`: 1 passed.
- `ROTA_DEV_DB=<copy> pytest tests/rota/test_l1.py -k TS` on cb4ed2c9: 23 failed, 134 passed, 1 skipped in 13 min. The three names above on the old door: 3 failed. The copy is deleted.
- `casestatus` from the worktree, from the main root with `timeout 280`: no output. The output file `f321_casestatus.txt` beside the probe is empty.

## (d) Usage

About 70k on the counter: about 60k input and about 10k output. No gate, no model.
