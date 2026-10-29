# Frame 345 review p6: seam4root at 102adb0d, parent ae7ed0ec

READY. All four points hold. Two low findings sit outside the points.

## (a) Verdicts

1. CONFIRMED. The diff touches 11 files. The profile rows, 65 added and 27 removed `model:` lines in 8 case files, and two assertions in `tests/rota/test_profile.py`. No expectation, prompt or door changed.
2. CONFIRMED. All 41 T1 and 24 l3_rulings Liaison cases pin `gemma4:12b-it-qat`. No case of another role changed its pin. No miss.
3. CONFIRMED. `Profile.find("local").model_for("liaison")` returns `gemma4:12b-it-qat`. `think_for("gemma4:12b-it-qat")` returns False. The `[think]` table on the local profile is empty.
4. CONFIRMED. 32 passed in 3.61s with `ROTA_L1` unset. One cassette recorded, one replayed.

## (b) Findings

1. Outside. `tests/rota/cases/l1_exhausted.yaml:198` (`L2-LI-carry-the-block-to-the-principal`, tier T2, role liaison). Low. PLAUSIBLE. The case carries no `model:` pin. `tests/rota/test_l1.py:152` reads `case.get("model", MODEL)`, so the gate runs this Liaison case on `qwen3:8b`, not on the seat's model. Fix: pin `model: gemma4:12b-it-qat` or record why T2 stays on the gate model.
2. Outside. `tests/rota/cases/g1_segments.yaml:95`, `:131`, `:162` (three G1 Liaison cases). Low. PLAUSIBLE. Line 131 pins `qwen3:8b`. Lines 95 and 162 carry no pin. The G1 cases measure the Liaison on a model the seat no longer uses. Fix: pin the three to `gemma4:12b-it-qat` in the next pass, or note the G1 tier as out of scope in the sprint row.

No finding on the points. The builder's scope was T1 and l3_rulings only, so findings 1 and 2 are a follow-up, not a block.

## (c) Probes

- `git diff --stat ae7ed0ec 102adb0d` and `git diff ae7ed0ec 102adb0d -- rota/ tests/rota/test_profile.py` in `C:/Users/roman/rota_seam4`. Showed the 11 files and the non-case hunks.
- `git diff ae7ed0ec 102adb0d -- tests/rota/cases/ | grep '^[+-]' | sort | uniq -c`. Showed 65 `+  model: gemma4:12b-it-qat` and 27 `-  model: qwen3:8b`, and nothing else.
- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0ce92518-cd4c-46c5-8db2-374566fad335/scratchpad/p6_probe_pins.py`. Parsed every case file at 102adb0d and at ae7ed0ec. Listed each case whose `model:` changed. All 65 changed cases carry `role: liaison`.
- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0ce92518-cd4c-46c5-8db2-374566fad335/scratchpad/p6_probe_pins2.py`. Counted 69 Liaison cases: 41 T1, 24 l3_rulings, 3 G1, 1 T2. Listed the 4 not on gemma4.
- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0ce92518-cd4c-46c5-8db2-374566fad335/scratchpad/p6_probe_profile.py` with `PYTHONPATH` on the worktree. Printed `model_for liaison: gemma4:12b-it-qat`, `Pins(... think=None)`, and `think -> {}`.
- `python -c` on `rota.llm.llm.think_for`. Printed `think_for gemma4: False` and `THINK_DEFAULT False`.
- `env -u ROTA_L1 python -m pytest tests/rota/test_profile.py tests/rota/test_native_calls.py -q -p no:cacheprovider`. Printed `32 passed in 3.61s`.

## (d) Usage

Input about 36k tokens across 9 tool turns. Output about 4k tokens. Total about 40k.
