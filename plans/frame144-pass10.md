# Frame 144, pass 10: the five findings of the delta review of b43b99d6

Meta workflow. Pass 10 of frame 144, the night databases are not a test tier, and the frame's last pass. An implementing agent on Opus wrote this record on 2026-10-07, on the branch `f144p10` in the worktree `C:/Users/roman/rota_f144p10`, from 2eaee7f3. Roman ruled on 2026-10-07 that the frame takes no new item. The pass builds the review's one medium and four lows, and nothing else. The review is the status of 2026-10-06 17:41 in `plans/stack.md` and `scratchpad/review144i/REPORT.md` of session 488d31af.

No file under `rota/` outside `rota/testkit/scenes.py` and `rota/tools/invariants.py` changed. So a night meets no line of this pass.

## What changed

| File | Lines | The change |
|---|---|---|
| `rota/tools/invariants.py` | +48, -12 | I5 reads only the park that owes an ask. `_replaced` reads the session that the challenge woke. I9's line names frame 174 |
| `rota/testkit/scenes.py` | +37, -16 | The s156 row holds the night's bytes and pins no first words. `blocks` keeps only a header of the runner's form |
| `tests/rota/test_invariants.py` | +57, -3 | Two I5 tests, two I9 tests, a helper that changes several rows |
| `tests/rota/test_scene_large_module.py` | +11 | One test: the diff's own headers are not blocks |

### 1. Medium: I5 reads only the park that owes an ask

`scheduler.parked` is true for two parks. A deferred batch with a quarantined key waits for the principal, and `predicates.park_ask` owes it one ask. A batch at or past `loop_cap` with a red run at its head climbs the ladder, and nothing asks the principal. I5 read `scheduler.parked`, so it found every batch that exhausted.

The new `_owes_ask` reads the same three conditions as `predicates.park_ask`: the batch is deferred, `scheduler.given_up` names a key, and the item is not contested. A contested item's batch goes to `do:cancel`, and no ask opens. I5 now finds a batch that owes an ask and holds none, or more than one. It also finds an open park ask on a batch that owes none. The sentence in `INVARIANTS` says the narrower proposition.

The park state on the two nights (observed: `scheduler.parked`, `given_up` and `failing_attempt` on the read-only databases, 2026-10-07):

| Night | Batch | Status | `parked` | `given_up` | `failing_attempt` | Open park ask |
|---|---|---|---|---|---|---|
| 126 | bg_1 | deferred | true | none | 11 | none |
| 127 | bg_1 | deferred | true | none | 12 | none |
| 127 | bg_2 | deferred | true | none | 13 | none |

`loop_cap` is 10 on both nights. Each of the three is a loop-cap park, so each is by design. Night 126's 1 and night 127's 2 do not stay.

Two tests prove the line. `test_i5_a_batch_parked_on_a_quarantined_key_with_no_ask` defers b2 with a quarantined key and finds `b2, parked on a quarantined key, holds 0 open park asks`. `test_i5_a_batch_past_the_loop_cap_owes_no_ask` defers b2 with a red run at attempt 10 at its head. It checks that `scheduler.parked` is true and `given_up` is empty, and then finds nothing. The scene `two_batches` keeps its strict xfail on I5, held by frame 142. Its finding is now `I5: b1, parked on a quarantined key, holds 0 open park asks`, the quarantine park of frame 142 (observed: `--runxfail`, 2026-10-07).

### 2. Low: the s156 row holds the night's bytes

`_S156_SENT` is night 126's s156 turn 2, the `turns.completion` text, 640 characters. A check compares it with the night's row and finds them equal (observed: the read-only database, 2026-10-07). `_S156` replaces the id, the criterion and the path with the scene's, `t_s156`, `c2` and `tests/test_export_json.py`, and drops `batch_id='bg_1'`, because the wake gives the batch. The parsed body is the night's 12 lines, and `_S156_LINE` is the night's line 6:

```
result = runner.invoke(echo_json, ["{"key": "value"}"], catch_exceptions=False)
```

The row's `words` is now empty, and `holds` keeps the line and the quote. Pass 9 pinned the first words `the body is not Python`. A repair of frame 166 that rewrites the start of the sentence then kept the row red, so the xfail never flipped. The refusal today says `line 6`, as on the night. The strict xfail fails for the right reason: the refusal holds neither the line nor `\"` (observed: `--runxfail`, 2026-10-07).

Pass 9's comment said "The line is the seat's, as sent", and pass 9's record said "night 126's s156 line". Both were wrong. The new comment says what is the night's and what is the scene's.

### 3. Low: `_replaced` reads the order

`_replaced` read a version above 1 on any ref of the challenge. A second challenge on a test already at version 2, with no reply, then read as answered. The review's tamper X2 survived that.

`_replaced(conn, msg_id, refs)` now asks for a committed session whose `trigger_msg` is the challenge, with a receipt on `tests` for a ref of the challenge, and the test at a version above 1. The receipt is the replace that the challenge woke, so the replace comes after the challenge.

`test_i9_a_challenge_on_a_test_replaced_before_it` is the tamper X2: t1 at version 2, a challenge, and nothing after it. It finds the challenge. `test_i9_a_challenge_answered_by_the_replace_it_woke` adds the session and its receipt, and finds nothing.

On nights 119 to 127, 21 challenges to the Tester have no answer row, and both rules exclude the same 21 (observed: a script over the nine read-only databases, 2026-10-07). So the change hides nothing new and finds nothing new on the nights.

### 4. Low: the block reader matches the runner's form

`runner.build_prompt` writes a pushed block as a blank line, `[key]` and the value. The key is a function name, `artefact.fn`, or `the item`. Pass 9's reader took any line in brackets after the push sentence. So `[diff]` and `[removed lines]` inside `code.diff`, and `[text]` inside `code.prose`, read as blocks.

`_BLOCK` now matches a header after a blank line whose key is dotted or `the item`. A TOML table in a pushed source, such as `[project.scripts]` or `[tool.uv]`, is dotted too. So `blocks` keeps a dotted key only when its first part is an artefact of `api.REGISTRY` or `msg`.

On night 127's first turns, the old reader gave 82 distinct keys and the new reader gives 37, each a function name or `the item`. The 45 keys that the new reader drops are text inside a block, such as `text`, `diff`, `removed lines`, `source`, `not_shown`, `the README's first lines` from `code.tree`, `project.scripts` and `tool.flit.module`. The new reader adds no key (observed: a script over `turns.user`, 2026-10-07).

`test_the_diffs_own_headers_are_not_blocks` reads S6's fix wake. The prompt holds `[diff]` and `[removed lines]`, the reader gives neither, and the last block is `code.diff`, not whole. The three green wake tests and the strict xfail of the fix wake keep their result.

### 5. The I9 rows go to frame 174

The I9 rows are seat faults: a Vision Keeper or an Architect that answered with no reply, and `db.session_commit` stamped the message answered. The pass builds no check for them. The I9 line of the checker's output now ends `(the rest are seat faults, frame 174)`.

## The checker's counts, before and after

Observed: `python -m rota.tools.invariants D:/repos/rota/.rota/clickI_night126.db` and `clickI_night127.db`, from the worktree, read-only, 2026-10-07. I2 reads clickI's HEAD of the hour.

| Invariant | Night 126 before | Night 126 after | Night 127 before | Night 127 after |
|---|---|---|---|---|
| I1 | 0 | 0 | 0 | 0 |
| I2 | 6 | 6 | 6 | 6 |
| I3 | 0 | 0 | 0 | 0 |
| I4 | 34 | 34 | 68 | 68 |
| I5 | 1 | 0 | 2 | 0 |
| I6 | 0 | 0 | 0 | 0 |
| I7 | 0 | 0 | 0 | 0 |
| I8 | 0 | 0 | 0 | 0 |
| I9 | 3 | 3 | 8 | 8 |
| I10 | 1 | 1 | 0 | 0 |
| Total | 45 | 44 | 84 | 82 |

The before counts equal pass 9's record for night 126 and `plans/night127-read.md`, section 4, for night 127.

## The tests

`tests/rota/test_invariants.py`, `test_scene_large_module.py` and `test_scene_two_batches.py` gave 93 passed, 2 skipped and 6 xfailed (observed: `pytest -n 3`, 2026-10-07). `test_invariants.py` holds 18 tests, 14 before. `test_scene_large_module.py` holds one more.

## The gate

Observed: `python -m rota.tools.gate` in the worktree, 2026-10-07, 02:29 to 02:41.

```
suite: 23 failed, 3148 passed, 35 skipped, 17 xfailed, 25 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 658.7s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The three new reds are three of the brief's known four, the same three as pass 9. No case was stale, so no re-record ran. The xfailed count is 17, pass 9's 18 less one: the priority row turned green when frame 164 landed, before this pass (copied: `plans/night127-read.md`, section 4).

## Deviations

- **The s156 row pins no first words.** The review offered two fixes: move the first words to `holds`, or add the step to `holds`. Frame 166's ends-when names the step as "the other quote kind or an escape", and no words for the step are decided. The first words in `holds` would still keep the row red after a repair that rewrites them. So the row pins the line and the quote, and the door by name.
- **The s156 row keeps the scene's id, criterion and path.** The body is the night's bytes. The scene holds no criterion `echo_json_compact` and no batch `bg_1`. `_S156_SENT` keeps the night's whole line, so a reader can compare it with the night.
- **Pass 9's record is not edited.** Its "night 126's s156 line" is wrong. This record states the correction, and a record of a pass stays as the pass wrote it.
- **`_replaced` reads a receipt, not only a session.** The review's fix asked for a committed session with the challenge as its trigger, and a version above 1. Each answered challenge has such a session, because `db.session_commit` stamps the trigger answered. So the session alone reads no order. The receipt on the named test is the write that follows the challenge.
- **I5 also excludes a contested item.** `predicates.park_ask` asks nothing for a contested item's batch, so I5 reads the same condition.

## Usage

The harness line of this agent carries the tokens. The agent's own estimate is about 110k in context, under the cap of 150k. No sub-agent ran. No model call ran outside the gate.
