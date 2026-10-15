# Frame 244, the try: a stronger model on the turn, and the two-step shape on replay

Run: 2026-10-15 13:23 to 13:27 local, by a meta-workflow agent on Opus.
Databases `.rota/clickI_night148.db`, `clickI_night147.db` and
`clickI_night146.db`, opened read-only. Script `try.py`, scorer `score.py`,
raw samples `res8b.jsonl` and `res14b.jsonl`, all in the scratchpad folder
`C:\Users\roman\AppData\Local\Temp\claude\d--repos-rota\dae006d1-0f15-4df0-b329-c022767b2f08\scratchpad\f244\`.
No file in the repository changed except this report. No test and no gate ran.

The night's model for both seats is `qwen3:8b`, think off, temperature 0.0,
seed null, `num_ctx` 16384 (observed: `sessions` rows of s152 and s119).
Every sample below runs at temperature 0.0 with the session's `num_ctx`.

**Caution on the sample count.** At temperature 0 the samples of one prompt
are identical text in 10 of 11 qwen3:8b groups and in 2 of 2 qwen2.5:14b
groups (observed: `score.py`, `distinct_texts`). So five samples at the
night's temperature hold about one sample of information. The one group
that moved is the placebo, where the first, cold call differs from the four
after it.

## Part 1. Be sure

| Seat | Model | Samples | Keep the declined file | Drop the declined file |
|---|---|---|---|---|
| s152 | qwen3:8b (night) | 5 | 5 | 0 |
| s119 | qwen3:8b (night) | 5 | 5 | 0 |
| s152 | qwen2.5:14b-instruct-q3_K_M | 3 | 0 | 3 |
| s119 | qwen2.5:14b-instruct-q3_K_M | 3 | 0 | 3 |

- qwen3:8b reproduces the night's call in all ten samples. s152 keeps the ten
  `tests/test_defaults.py` grains. s119 keeps
  `tests/test_utils/test_echo_via_pager.py`.
- qwen2.5:14b, s152, three identical samples:
  `TOOL: batches.annotate(batch_id="bg_2", paths=['src/click/termui.py::confirm', 'src/click/testing.py::EchoingStdin'], symbols=['confirm', 'EchoingStdin'])`.
  This is the principal's ruling exactly: drop the defaults tests, keep
  confirm and the stdin helper.
- qwen2.5:14b, s119, three identical samples, verbatim:

  ```
  TOOL: batches.annotate(batch_id="bg_1", paths=["src/click/utils.py"], symbols=["echo", "echo_json"])

  TOOL: artefact.verb(key="principal_said")
  TOOL: batches.annotate(batch_id="bg_1", paths=["tests/test_utils/test_echo.py"])
  ```

  The judgement is right: the pager file is dropped, and `utils.py` and the
  echo test file are named. The form is wrong: two annotate calls, and one
  copy of the brief's placeholder line `artefact.verb`. On the runner the
  second annotate probably replaces the first (reasoned: one annotate per
  batch; not run on the runner).
- gemma3:12b was not run. The brief names it only when the first model is
  not pulled, and `ollama list` shows qwen2.5:14b-instruct-q3_K_M pulled.
- Fit beside the gate: the gate ran in the checkout from 13:18. Ollama held
  only the models these replays loaded, with expiry times set by these
  calls, so the gate made no Ollama call in the window (observed: `/api/ps`,
  13:22 to 13:25). qwen2.5:14b loaded at 10.8 GB, 8.4 GB of it in VRAM on
  the 10 GB card, and evicted qwen3:8b.

## Part 2. The two-step shape, on replay (qwen3:8b, temperature 0.0)

### The exact substitution text

Two edits in the turn-1 `system` text. Every other byte stays. The `user`
text is unchanged.

1. `TOOL: batches.annotate(batch_id, paths, symbols=None)` becomes
   `TOOL: batches.annotate(batch_id, disputed, paths, symbols=None)`.
2. In the ruling paragraph, `keep every path\nthey do not dispute.` becomes
   ``keep every path\nthey do not dispute. `disputed`: the paths his words decline. Leave them out of `files`.``

The placebo replaces `disputed` with `notes` in both edits. The sentence
says `files`, as the brief gives it. The tool's argument is named `paths`.

Note: the `user` text of these turns already holds a field
`"disputed": [...]` inside `touch.bg_<n>`, with another meaning. For s152
the field is empty. For s119 it is
`["src/click/utils.py::echo", "tests/test_utils/test_echo.py::test_echo"]`.

### 2.1 The two seats, five samples each

| Seat | Right path in `disputed` | Declined path dropped from the files list |
|---|---|---|
| s152 | 0 of 5 | 0 of 5 |
| s119 | 0 of 5 | 5 of 5 |

- s152, five identical samples:
  `batches.annotate(bg_2, ["tests/test_utils/test_confirm.py"], [...the twelve grains, the ten test_defaults.py grains included...])`.
  The `disputed` list names the file the principal wants. The files list is
  the night's list unchanged.
- s119, five identical samples, verbatim:
  `TOOL: batches.annotate(bg_1, disputed, ["src/click/utils.py::echo", "tests/test_utils/test_echo.py::test_echo"], ["src/click/utils.py", "tests/test_utils/test_echo.py"])`.
  The files list drops the pager file. The `disputed` list is the prompt's
  own `touch.bg_1.disputed` list, copied, and not the pager file. The list
  holds `tests/test_utils/test_echo.py`, which the files list also holds, so
  the door of the second half refuses this call. The call also carries a
  bare word `disputed` as an argument.

### 2.2 Three right calls, five samples each

Nights 147 and 148 hold right annotates after a files contest in two
distinct sessions only, s235 and s345 (observed: `judge.py` verdicts on
`after.json`). The third call is from night 146, s124, the mirror of s119
that dropped the pager file. All three are turn 1. The unchanged replay
gives the right files list in 5 of 5 for each.

| Call | Words decline | `disputed` | Files list | False refusal |
|---|---|---|---|---|
| night 147 s235 | defaults tests, short-help helper | utils short-help grain, the defaults grains | right, 5 of 5 | 0 of 5 |
| night 147 s345 | nothing ("Ok, go ahead.") | `[]` | right, 5 of 5 | 0 of 5 |
| night 146 s124 | pager tests | `tests/test_utils/test_echo.py` grains | right, 5 of 5 | **5 of 5** |

- s124's `disputed` puts the kept echo test file in the list, and the files
  list keeps the same file. The door refuses this call.
- s235's `disputed` names `tests/test_defaults.py` and `src/click/utils.py`.
  The list leaves out `tests/test_utils/test_make_default_short_help.py`,
  which the files list also leaves out. No refusal.
- No sample drops a right path from the files list.

So 5 of 15 samples, one call of three, are false refusals.

### 2.3 Placebo, `notes`, s152, five samples

| Sample | `notes` | Files list | Change from the night's list |
|---|---|---|---|
| 0 (cold) | `["tests/test_defaults.py"]` | the twelve grains | none |
| 1 to 4 | the ten `tests/test_defaults.py` grains | confirm and `EchoingStdin` only | declined file dropped |

The placebo moves the files list in 4 of 5 samples, and puts the declined
file in its field in 5 of 5. The field named `disputed` moves the list in
0 of 5. Samples 1 to 4 are identical text, so the placebo holds two
distinct replies, one each way.

## What the counts say

On the night's turn, qwen3:8b keeps the declined file in 10 of 10 samples
and qwen2.5:14b drops it in 6 of 6, so cause 5's two conditions hold for
these two seats, with each group about one distinct reply at temperature 0.
The `disputed` field fills right in 0 of 10 samples on the two seats and
refuses a right call in 5 of 15, while the same sentence under the name
`notes` drops the declined file in 4 of 5 on s152, so the field name and the
prompt's own `disputed` field move the seat more than the judgement does.

## What was not run

- gemma3:12b, because the first stronger model was pulled.
- The two-step shape on qwen2.5:14b.
- Samples at a temperature above 0. The brief asked for the night's
  temperature, and at 0 the samples repeat.
- A wording of the sentence with `paths` in place of `files`.
- No test and no gate, by the brief.
