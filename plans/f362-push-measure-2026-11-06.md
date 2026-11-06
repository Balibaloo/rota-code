# Frame 362, the measurement of the push: does the Developer open the file that he named

Scratch directory: `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/029756dd-9273-4a54-95d8-2da05a2bfe52/scratchpad/push_measure/` (below: `SCR`). Measured 2026-11-06, finished 09:43 (observed: `date`).

## Result

- **OLD: 0 of 10 go to `string.py` first. 10 of 10 go to `property.py`** (observed: `SCR/raw/OLD_01.txt` to `OLD_10.txt`).
- **NEW: 0 of 10 go to `string.py` first. 10 of 10 go to `property.py`** (observed: `SCR/raw/NEW_01.txt` to `NEW_10.txt`).
- No reply of the 20 names `src/icalendar/parser/string.py` or `_foldline` (observed: `SCR/analyse.py`).
- The change of `86ca7e23` does not move the first reply of s152 to the file that he named (observed: the counts above).
- The NEW reply is worse in one way. OLD logs a conflict and asks the Vision Keeper. NEW logs a "default" assumption that the instruction means "other files named property.py". Then NEW sends `code.write(path='src/icalendar/parser/property.py', text='', start=0, end=-1)` and `code.commit` (observed: `NEW_01.txt`).
- The 10 replies of each prompt are one reply, byte for byte (observed: 2 distinct md5 sums in 20 files). At temperature 0 with no seed, the 10 runs are one sample of each prompt, not ten (reasoned: the run's pins fix the reply, and the server gives the same bytes each call).
- The OLD reply is the recorded first completion of s152, byte for byte, 10 of 10 (observed: a compare against `turns.completion` of s152, seq 1). So the server, the model and the options reproduce the run.

What the measurement cannot show: it reads one first reply of one wake, not a whole session (reasoned). A later turn can read the block again and change course. The measurement does not show whether the runner refuses the empty `code.write`. It does not show s155 or s156, which had the same block (observed: `p362b/replay3.out`) but other wakes around it.

The probable cause, for the next frame (reasoned, not measured): the NEW prompt still names `src/icalendar/parser/property.py` 5 times, and `string.py` once. `batches.expect` says `"expected to touch": ["src/icalendar/parser/property.py", ...]`, and `"might touch"` names two functions of `property.py`. The bound constraint `cw_985d42272f1e` has a headline on `property.py` (observed: `SCR/new_user.txt`). That touch set is the guess line that he called wrong. The legend says "line 2 is wrong: rewrite", but the batch's own touch set still carries the old guess. The model then reads his "Do not touch property.py" as a conflict with the ticket (OLD) or as a typo (NEW).

## 1. Prompt OLD

The first turn of s152 in `dry6b.db`, opened with `immutable=1`: `turns.system`, 6,833 characters, and `turns.user`, 20,955 characters (observed: `SCR/q1.py`, written to `SCR/old_system.txt` and `SCR/old_user.txt`). The ruled block is the last key of the push, lines 26 and 27, with 65 characters of value:

```
[the principal's words on this change, newest last]
["Do not touch parameter.py or property.py.", "Line 2 is wrong."]
```

(observed: `old_user.txt`.)

## 2. Prompt NEW, and how it differs

The builder could not give the whole wake (reasoned: `push_working_set` needs a live sandbox over the run's project worktree, the run's code is older than `86ca7e23`, and the brief forbids writes). So NEW is OLD with only the ruled block replaced by the block of the code at `86ca7e23` (observed: `SCR/build_new.py`).

How the block was built (observed: `build_new.py`):

1. `runner._ruled_block(conn, api.batch_ruled_refs(conn, 'b_1'), item=<b_1's item>)`, the call of `push_working_set` at `runner.py` 4635 of the worktree.
2. `principal.ruled` filtered to the rulings that landed before s152, by the replay's rule: a ruling counts when its Liaison session ran before the wake. The window is `r_m5`, `r_m6`, `r_m13`, `r_m16`, `r_m22`, `r_m27`. The later rulings `r_m40` to `r_m54` are out.
3. `runner._render(block, runner.PUSH_CHARS)`, the render of every pushed key at `runner.py` 1145.
4. The block goes first, right after the "Already run for you" line, as the code places it: `pushed = {START_RULED_KEY: said, **pushed}`. The old block at the end is removed. No other byte changes.

The block that the builder gives has 337 characters, the same as `p362b/replay3.out` gives for s152 (observed). The prompts differ by +272 characters, 20,955 to 21,227, and by +77 prompt tokens, 9,063 to 9,140 (observed: `prompt_eval_count`). The wake fits the turn budget of 25,689 characters for `num_ctx` 16,384, so no cut applies (observed: `runner._fit_budget`). The system text is the same for both (reasoned: frame 362 changes no prompt file, by the code comment at `runner.py` 4646).

The diff (observed: `SCR/diff.txt`, with long lines kept whole here):

```
@@ -4,2 +4,6 @@
 Already run for you, with the results below. Calling any of these again returns the same thing and costs you a turn:
+
+[the principal's words on this change, newest last]
+His answer m27 to page m26: "Line 2 is wrong. The fold is _foldline in src/icalendar/parser/string.py, and its tests are in src/icalendar/tests/test_icalendar.py. Do not touch parameter.py or property.py."
+On his page, line 2 is wrong: rewrite. The line was the team's guess at the code this touches, guess:folds_long_lines_in_icalendar.
 
@@ -24,4 +28 @@
 [{"id": "tk_1", "item_id": "folds_long_lines_in_icalendar", "text": "fold long lines in iCalendar output at spaces to avoid splitting words"}]
-
-[the principal's words on this change, newest last]
-["Do not touch parameter.py or property.py.", "Line 2 is wrong."]
```

## 3. The calls

The server is the 3080's Ollama at `http://127.0.0.1:11434`, version 0.33.3 (observed: `plans/operating-facts.md` line 79 names it the default for `qwen3.5:9b`, and `/api/version`). `/api/ps` listed no model before the first call, and the script checked it before each call (observed: `SCR/call.py`).

The payload is the payload of `OllamaBackend.complete`, `rota/llm/llm.py` 450, with `stream: false` (observed: the code). Streaming joins chunks and does not change the tokens (reasoned). The options come from `sessions.pins_json` of s152 and the run's `config.profile` (observed):

- model `qwen3.5:9b`, `think: false` (`THINK_DEFAULT`, because the profile's `think` is empty)
- `temperature` 0.0, `num_ctx` 16384, `num_predict` 8192 (`max_tokens` is null, so the transport cap applies)
- no `seed`, no `top_p`, no `repeat_penalty` (all null in the pins), so the seed did not vary
- no `tools` (`native_tools: false`)

The 20 calls ran in the foreground, one after another: OLD 1 to 10, then NEW 1 to 10. Each call took 2.3 to 2.5 s after the first load. The first call of each set took 10.8 s and 5.0 s. Every reply ended with `done_reason: stop` (observed: `SCR/raw/*.json`).

## 4. Each reply

Each raw reply is in `SCR/raw/<OLD|NEW>_<nn>.txt`, with its metadata in the `.json` file beside it. The table holds one row per prompt, because the 10 replies of a prompt are the same bytes (observed: md5 sums).

| Prompt | Runs | Tool calls, in order | File paths named | Names `string.py` | `property.py` as a file to change | Length |
|---|---|---|---|---|---|---|
| OLD | 10 | `code.probe`, `code.source`, `ledger.log` (kind `conflict`), `msg.question_vision_keeper` | `src/icalendar/parser/property.py`, `parameter.py`, `property.py` | no | yes: probes and reads it, and asks whether to "proceed with modifying property.py" | 850 |
| NEW | 10 | `code.probe`, `code.source`, `ledger.log` (kind `default`), `code.write`, `code.commit` | `src/icalendar/parser/property.py`, `parameter.py`, `property.py` | no | yes: probes, reads, then writes `text=''` over it and commits | 862 |

(observed: `SCR/analyse.py` over `SCR/raw/`.)

The first call of every reply is `code.probe(pattern='src/icalendar/parser/property.py')` (observed). No reply opens `parameter.py` (observed).

## 5. Usage

20 model calls used about 60 s of card time (observed: `wall_s`). No tracked file in `D:/repos/rota` or in the worktree changed, except this new report (observed: the scripts write in `SCR` only).
