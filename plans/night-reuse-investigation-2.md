# Frame 231, the second investigation: where the card's minutes go in the walks

Read-only investigation by an agent on Fable, 2026-10-13. Meta workflow for
the instruments, rota workflow for the seats. Code read at `ccef6f0a`.
Databases opened `mode=ro`. Scripts in the scratchpad of session e669185f:
`r2_part1.py`, `r2_part1b.py`, `r2_part4.py`, `r2_gen.py`, `r2_f.py`.

Roman's ask, 2026-10-13 19:05: "Just investigate how to reuse, all the time
is spent on the card generating tokens. Investigate with fable."

## 0. The result

Roman is right about the card, and reuse is not the lever. On night 145 the
walks cost 262.9 model minutes. Generation of completion tokens is about 154
of them, a fixed cost per turn is about 79, prompt evaluation is about 18
and the model swaps are about 12 (reasoned: a least-squares fit over 1,915
turns, section 1.1). No key finds repeats worth replaying in a walk: the
whole-prompt key replays 1.7 minutes across nights, and a canonical key that
folds every id, sha, timestamp and number replays 4.6 minutes within a night
and 3.9 across (observed: `r2_part4.py`, section 1.4). The time goes to
tokens the night throws away. 78 completions over 2,000 tokens hold 52
percent of the walks' generated tokens, 86 minutes. The seats wrote their
own tool results in 150 turns, 179k tokens, about 35 minutes, and the runner
discards those by design. 35 turns ran past 60 seconds and cost 58.6
minutes together (observed: `r2_gen.py`, section 1.6).

Order by card minutes saved per cycle of build:

1. J, an output cap of 4,096 tokens in a night-only profile: 1 cycle, about
   28 minutes a night on both nights.
2. I, the stream stops at a fabricated result: 1 cycle, about 29 to 36
   minutes a night. With J, about 45 to 55 minutes.
3. F, the refusal cap at three turns: 1 cycle, about 15 minutes. It changes
   a measured count, so it needs a ruling.
4. The fixed cost measured: 1 cycle, no code. Ollama's own timing lines on
   night 146 say what the 60 to 80 fixed minutes are. The saving is unknown
   until then.
5. G, one walk from a walk snapshot: 4 to 5 cycles, 106 to 174 model
   minutes when the frame's count sits in walk 3.
6. H, llama.cpp's server with a draft model: 3 to 4 cycles, up to 50 to 75
   minutes, and every ratio against nights 143 to 145 resets.
7. A, B, C, D and E: under 10 minutes each, or nothing.

## 1. Where the card's minutes go in a walk, measured

Nights 144 and 145, `sessions` and `turns` of `clickI_night144.db` and
`clickI_night145.db`. The phase cut is the first investigation's session
counts per phase: night 145 onboarding is s1 to s104, walk 1 s105 to s169,
walk 2 s170 to s235, walk 3 s236 to s439. Tokens are characters over 3.97,
the ratio `llm.py:468` measured for these models. `turns.ms` wraps the whole
backend call, `runner.py:3539-3546`, so it holds Ollama's load, prompt
evaluation and generation, and the live-view writes. Ollama's server log
stops on 2026-10-07 at 18:40, because `gauntlet_click.sh:13` starts
`ollama serve` hidden with no log (observed: `%LOCALAPPDATA%\Ollama\
server.log` and the script). So the split below is a fit, not Ollama's own
counters.

### 1.1 Prompt evaluation against generation

Per turn, in the card's order: the new tokens are the prompt's length minus
its common prefix with the last prompt the same model saw, or the whole
prompt after a swap. Fit `ms = a + b*new_tok + c*gen_tok + d*swap` per
model (observed: `r2_part1b.py`, 2026-10-13).

| Night, model | Fit | r2 | Walk minutes = fixed + prompt + generation + swap |
|---|---|---|---|
| 145 qwen3.5:9b | 2696 + 0.37 new + 11.6 gen + 8118 swap | 0.98 | 205.8 = 58.0 + 12.5 + 128.8 + 6.6 |
| 145 qwen3:8b | 2043 + 0.60 new + 11.8 gen + 6772 swap | 0.91 | 57.1 = 21.3 + 5.9 + 25.1 + 5.4 |
| 144 qwen3.5:9b | 2983 + 0.40 new + 11.7 gen + 11036 swap | 0.86 | 157.4 = 48.7 + 10.4 + 90.1 + 8.1 |
| 144 qwen3:8b | 2037 + 0.46 new + 13.0 gen + 8214 swap | 0.93 | 94.8 = 39.6 + 7.5 + 43.7 + 6.0 |

- Night 145's walks: generation 153.9 minutes, 59 percent. Fixed 79.3, 30
  percent. Prompt evaluation 18.4, 7 percent. Swaps 12.0, 5 percent. Night
  144: 133.8, 88.3, 17.9 and 14.1 of 252.2 (reasoned: the fit's terms summed
  over the walk turns).
- Generation runs at 85 to 86 tokens a second on both models, 11.6 to 11.8
  ms a token. Prompt evaluation of the new tokens runs at 1,700 to 2,700
  tokens a second. The older server log of 2026-09-22 shows 2,104 tokens a
  second on a 1,828-token prompt, which agrees (observed: `server-1.log`
  line 263).
- The prefix cache works inside a session. Consecutive turns of one session
  share 85 percent of the prompt on night 145 and 88 on night 144. A fit of
  `ms` on the whole prompt's size gives a slope of about zero, so the cached
  part costs no evaluation (observed: `r2_part1.py`, the tiny-completion
  fit, n 379: `ms = 4237 - 0.067*prompt_tok`).
- The fixed cost is 2.0 to 3.0 seconds a turn and it is not explained. With
  a cached-tokens term the fit gives 1.5 to 1.9 seconds a turn plus 0.2 ms
  per cached token on qwen3.5:9b, about 0.9 seconds a turn at its 4,500
  cached tokens, and 0.06 ms on qwen3:8b (observed: `r2_gen.py`). The
  candidates are Ollama's request handling and its attention over the cache
  during generation. The live view writes 80 characters at a time and
  buffers, so it is not the cost (observed: `llm.py:236-256`). Ollama's
  `print_timing` lines, prompt eval time, eval time and total, settle it in
  one night with a log.

### 1.2 Thinking

Nothing to cut. `THINK_DEFAULT = False` (`llm.py:51`), the backend sends
`think: false` whenever the pin is `None` (`llm.py:405`), and the night's
profile `rota/llm/profiles/local.toml` has no `[think]` table, so
`pins_json`'s `think: null` means `false` on the wire (observed: the code
and the file). 0 of 2,515 completions of night 145 carry `<think>`, 14
carry a stray `</think>`, and those 14 are ordinary replies (observed:
`turns`). Option B saves 0 minutes.

### 1.3 The model swaps

- Swaps between consecutive sessions: 103 of 438 boundaries on night 145,
  94 of 617 on night 144. The logs print 106 and 102 `CARD FITS` lines
  (observed: `sessions` by `seq`, and the logs).
- A session's first turn after a swap: mean 18.1 s, median 11.6 s, against
  8.8 s and 4.3 s when the model stayed, at the same prompt size, night 145.
  Night 144: 16.3 and 12.6 against 6.1 and 3.6 (observed: `r2_part1.py`).
  The fit prices a swap at 6.8 to 11.6 seconds, 12 minutes on night 145 and
  14 on night 144.
- The card holds 10 GB, about 8 GB in practice beside the desktop
  (`plans/operating-facts.md`, Hardware, and Models line 95). qwen3:8b is
  6.89 GB resident at 16384 and qwen3.5:9b 5.50 GB, 12.39 GB together
  (observed: the `CARD FITS` lines). Both resident on the 3080 is not
  possible. `OLLAMA_MAX_LOADED_MODELS` is set nowhere in the repo and the
  backend sends no `keep_alive`, so the default five minutes holds, and no
  session idles that long between two on one model (observed: grep of the
  repo, `llm.py:395-410`). The Titan holds 12 GB at 27 tokens a second and
  gives other bytes to the same prompt (facts line 75), so one model there
  is a slower night with new recordings.

### 1.4 The repeats

Keys over `system + user`, every live turn of the walks (observed:
`r2_part4.py`, 2026-10-13). Level 0 is the whole prompt. Level 1 folds
session ids, message ids, batch and ticket ids, commit shas, ISO
timestamps and `attempt N of N`. Level 2 folds every run of digits too.

| Key | Night 145 within-night hits | Night 145 hits in night 144 | Night 144 within-night |
|---|---|---|---|
| Level 0 | 3 turns, 0.2 min | 22 turns, 1.7 min | 4 turns, 0.2 min |
| Level 1 | 34 turns, 4.1 min | 30 turns, 2.0 min | 39 turns, 4.2 min |
| Level 2 | 36 turns, 4.6 min | 42 turns, 3.9 min | 47 turns, 4.5 min |

- The same reply came back on only 16 of the 36 level-2 within-night hits
  and 34 of the 42 across. A canonical key that replays would give the
  wrong reply in half of its within-night hits (observed: the same script).
- The refusal loops do not repeat a prompt. Each refused turn's prompt
  grows by the exchange, so the key never matches. 138 turns of night 145
  repeat the completion of the turn before, 9.1 minutes, and 28 of them are
  a third identical turn, 1.8 minutes. Night 144: 232 turns, 13.9 minutes,
  and 58, 3.8 (observed).

### 1.5 The turns per session and how sessions end

- Walk sessions: 335 on night 145, 5.7 turns a session on average, median
  4, cap 24 (`ROTA_MAX_ITERATIONS=24` in the night script). 43 sessions of
  12 or more turns cost 112.6 of 262.9 minutes. Night 144: 446 sessions, 37
  long ones, 113.2 of 252.2 (observed: `r2_part1.py`).
- Ended on "repeated its previous turn verbatim twice": 30 sessions, 30.1
  model minutes, night 145; 60 sessions, 52.2 minutes, night 144. Ended on
  "refused the same way in four turns": 31 sessions, 41.7 minutes; 18
  sessions, 32.4 minutes (observed: the `SESSION ENDED` account rows).
- The same refusal, an `ERROR <fn>:` line in the next prompt, came twice in
  115 sessions of night 145, and the turns from the second refusal on cost
  66.5 minutes. Three times in 71 sessions, 27.8 minutes from the third on.
  Four times in 23 sessions, 12.6 minutes. Night 144: 132 sessions and
  52.0, 63 and 30.4, 14 and 6.3 (observed: the recount in the terminal,
  2026-10-13).
- After a first verbatim repeat, 110 of the 138 next turns differed, so the
  seat moved on. A stop at the first repeat would end 84 sessions and save
  28.3 minutes, with those recoveries lost (observed: `r2_f.py`).

### 1.6 Where the generated tokens go

Night 145's walks generated 793k tokens in 1,915 live turns. Night 144:
663k in 2,146 (observed: `r2_gen.py`).

- By seat and wake, night 145: the Developer on `tick:tests_failing` 544
  turns, 261k tokens, 83.1 minutes. The Tester on a message 287 turns,
  188k, 50.8. The Architect on `tick:annotate` 55 turns, 60k, 14.1. The
  Tester on `tick:tests_missing` 71 turns, 56k, 15.5. The Terminologist on
  a message 111 turns, 53k, 17.7.
- Long completions, night 145: over 500 tokens, 302 turns, 79 percent of
  the tokens, 141 minutes. Over 2,000, 78 turns, 52 percent, 85.8 minutes.
  Over 4,000, 43 turns, 40 percent, 65.8 minutes. Night 144 over 2,000: 58
  turns, 53 percent, 75.5 minutes.
- The 78 over 2,000 on night 145: 26 wrote a fabricated result, `OK ...`
  after a `TOOL:` line, 136k tokens, 28.9 minutes. 28 are prose with no act
  at all, 189k tokens, 38.0 minutes. 24 are acts with prose beside them,
  89k, 18.9 minutes.
- Fabricated results in all turns: 150 turns, 179k tokens, 23 percent,
  about 35 minutes, night 145; 173 turns, 220k, 33 percent, 43 minutes,
  night 144. The runner names it "wrote its own tool results", runs nothing
  behind the fabricated line, and tells the seat so (`runner.py:3822-3830`).
  That account line heads the list: 74 sessions and 128.1 minutes on night
  145, 68 and 128.2 on night 144.
- "your reply was cut at the output budget": 29 sessions, 92.0 minutes;
  24 sessions, 84.3 minutes. The budget is `num_predict` 8192 (`llm.py:372,
  387`) and the cut is `done_reason == "length"` (`runner.py:3575`). A cut
  reply ran about 95 to 120 seconds (observed: the ten longest, 86 to 122
  seconds each).
- Turns over 60 seconds: 35 turns, 58.6 minutes, 288k tokens, night 145;
  43, 68.0, 303k, night 144. These are the runaways.
- Clean act bodies, no fabricated line: the longest `code.write` is 7,636
  tokens (s423#12), `batches.annotate` 7,426 (s117#20), `tests.encode` 364.
  8 clean act completions exceed 4,000 tokens on each night, and 24 exceed
  2,000 on night 145, 14 on night 144 (observed).
- Prose beside `TOOL:` lines, over 200 characters: 448 turns, 262k tokens,
  33 percent, about 51 minutes. Completions with no `TOOL:` line: 267 turns,
  241k tokens, 59.5 minutes, night 145.

## 2. The options

Each option: what, exists, build, saves, invalidates, risk. Savings are per
night from section 1.

### A. Recorded wakes with a canonical key

- What: a walk wake replays a recorded reply when the canonical prompt
  matches.
- Exists: `key_for`, `RecordingBackend`, the `turns` rows (first report).
- Build: 3 cycles, `rota/llm/cassettes.py` and a key module.
- Saves: under 5 minutes within a night and under 4 across (section 1.4).
- Invalidates: any byte outside the folded ids.
- Risk: high. Half the within-night hits got another reply, so a replay
  puts a wrong reply on a seat and hides the wall. Do not build for walks.

### B. No thinking

- What: `think: false` on the seats.
- Exists: it is the wire's value already (section 1.2).
- Build: 0. Saves: 0. Invalidates: nothing. Risk: none.

### C. Both models resident

- What: no swaps.
- Exists: nothing. 12.39 GB does not fit 10 GB (section 1.3).
- Build: not on the 3080. The alternatives are one model for every seat,
  which reverses finding 81's quality ruling, or a scheduler that groups
  ready wakes by model, 2 cycles in `rota/core/scheduler.py`.
- Saves: at most 12 to 14 minutes.
- Invalidates: not applicable.
- Risk: grouping changes the order the seats run in, which is the night's
  dynamics. Not recommended.

### D. Prefix cache

- What: Ollama reuses the KV cache of a shared prefix.
- Exists: it works inside a session today, one slot per model, 85 to 88
  percent of each prompt cached (section 1.1). Across sessions on one model
  the shared prefix is 11 to 14 percent, because four roles share
  qwen3.5:9b and the slot holds the last prompt only.
- Build: more slots cost about 2.4 GB of KV each at 16384, so no. The open
  item is the fixed 60 to 80 minutes a night: 1 cycle, no code. Start
  `ollama serve` with its output to a file for night 146, in `ollama_up` of
  `probes/gauntlet_click.sh` or by hand, and read the `print_timing` lines
  against `turns.ms`.
- Saves: prompt evaluation is 18 minutes, and the fixed cost is the prize
  if it sits in a setting.
- Invalidates: not applicable.
- Risk: none to a measurement.

### E. Shorter prompts

- What: a wake carries less text.
- Exists: the CUT notes and the per-result budgets in `runner.py`.
- Build: 3 or more cycles in `rota/core/runner.py`, the implementer's site.
- Saves: at most the 18 minutes of prompt evaluation plus the cached term,
  about 19 minutes on qwen3.5:9b (section 1.1). A halved prompt saves about
  15 to 20.
- Invalidates: the prompt is the key of every recording.
- Risk: the prompt is what the seat reads, so every count moves. Not for a
  measured night.

### F. Fewer wasted turns

- What: the refusal loop ends at the third same refusal instead of the
  fourth, or at the second.
- Exists: `runner.py:4248-4275`, the NOTE at three and the stop at four.
- Build: 1 cycle in `rota/core/runner.py`, after the implementer's commit.
- Saves: a cap at three, about 15 minutes, the 27.8 minutes from the third
  refusal on minus the 12.6 the fourth already ends. A cap at two, up to
  66.5 minutes, but 44 of the 115 sessions moved on after the second
  refusal. A stop at the first verbatim repeat, 28.3 minutes, with 110 of
  138 recoveries lost (section 1.5).
- Invalidates: nothing.
- Risk: the refusal count is the three-part ends-when of a door frame
  (ruled: Roman, 2026-10-03), so a lower cap changes what a night measures.
  A ruling before the cap.

### G. Walk-boundary snapshots

- What: a frame re-runs only the walk its door sits in (first report, C
  and G).
- Exists: `GAUNTLET_FROM`, the seam restore for batches.
- Build: 4 to 5 cycles, `probes/walk.py`, `probes/seam_start.py`,
  `probes/gauntlet_click.sh`.
- Saves: walks 1 and 2 of night 145 are 105.9 model minutes and 133 wall;
  of night 144, 174.2 model and 214 wall (first report, section 1).
- Invalidates: a change to any seat that woke before the boundary.
- Risk: lost counts in the skipped walks, as the first report says.

### H. A faster backend

- What: the same models behind llama.cpp's server, with a draft model, or
  two sessions in flight.
- Exists: `LiteLLMBackend` speaks to an OpenAI-shaped server and sends
  `enable_thinking` (`llm.py:503-556`). Ollama 0.33.3 runs here, and its
  release notes name speculative decoding for MLX only, v0.34.2 and v0.40.4
  (observed: github.com/ollama/ollama/releases, 2026-10-13). llama.cpp's
  server runs a draft model. The loop wakes one role per step
  (`loop.py:202`), so nothing is in flight twice.
- Build: 3 to 4 cycles for llama.cpp's server with a 0.6B draft behind
  `LiteLLMBackend`, with a card-fit check. Two in flight needs the
  scheduler and the record order, and that is a ruling.
- Saves: generation is 154 minutes at 85 tokens a second. The 3080 is
  bandwidth-bound near 140 tokens a second for a 5.5 GB model, so a leaner
  server alone buys under 1.3 times. A draft model buys 1.5 to 2.5 times on
  code and tool lines at temperature 0, so 50 to 75 minutes (reasoned:
  speculative decoding keeps greedy output, and the walks' replies are
  mostly tool lines and code).
- Invalidates: a new server gives other bytes to the same prompt (facts
  line 75), so every recording and every ratio against nights 143 to 145
  resets.
- Risk: medium. The night after the switch is a new baseline, not a
  measurement of a door.

### I. Added: the stream stops at a fabricated result

- What: `_consume_stream` ends the reply at the first line that begins
  `OK <fn> ->` or `ERROR <fn>:` after a `TOOL:` line, keeps that line, and
  closes the connection, as it does for a cycling reply.
- Exists: the cycling stop in `llm.py:265-346`, and the runner's
  `FABRICATED_RESULT` check that runs nothing behind that line and tells
  the seat (`runner.py:3822-3830`).
- Build: 1 cycle in `rota/llm/llm.py`, not the implementer's site. The
  kept line keeps the runner's account "wrote its own tool results" and
  its feedback unchanged.
- Saves: about 29 to 35 minutes on night 145 and 36 to 43 on night 144
  (section 1.6). With J, about 45 to 55 minutes, because the fabricated
  runaways are 26 of the 78 long completions.
- Invalidates: nothing. The reply the runner acts on is the same.
- Risk: low. The runner already runs nothing after the line, so the night
  loses no act and the count of the sign holds.

### J. Added: a lower output cap on the night

- What: `max_tokens = 4096` in a night-only profile, so `num_predict` cuts
  a runaway at 4,096 tokens instead of 8,192.
- Exists: `max_tokens` is a profile pin (`profile.py:34`) and reaches
  `num_predict` (`llm.py:387`). The runner already tells the seat about a
  cut (`runner.py:3575`).
- Build: 1 cycle. Copy `local.toml` to `local-night.toml` with the pin and
  name it in the launcher. Not `local.toml` itself: `max_tokens` is in the
  cassette key, and `casestatus` wants the register's pins from
  `ROTA_PROFILE`, so a changed `local.toml` reads every case as stale.
- Saves: 43 turns over 4,000 tokens become 4,096 each: about 145k tokens,
  28 minutes on night 145, 27 on night 144. At 2,048: about 254k tokens, 50
  minutes, but 24 clean acts over 2,000 tokens on night 145 would be cut.
- Invalidates: nothing in the records. The night's key differs from the
  register's.
- Risk: at 4,096, 8 clean act completions a night are cut, among them a
  `code.write` of 7,636 tokens and a `batches.annotate` of 7,426. The seat
  gets the cut note and sends less, which is the runner's design. The
  prose-only runaways, 28 turns and 38 minutes, have no other stop.

## 3. The recommendation

1. J, the night profile with `max_tokens = 4096`: 1 cycle. Site:
   `rota/llm/profiles/local-night.toml`, `probes/gauntlet_click.sh`.
2. I, the stream stop at a fabricated result: 1 cycle. Site:
   `rota/llm/llm.py`, `tests/rota/test_llm*.py`. J and I combine, about 45
   to 55 minutes of night 145's 263.
3. The fixed cost's measurement: 0 code, night 146 with Ollama's log.
   Whatever it names is the next frame.
4. F at three, after a ruling, because the count is a measure. 1 cycle,
   after the implementer's commit on `runner.py`.
5. G per frame, by choice, 4 to 5 cycles, when a frame's count sits in
   walk 3.
6. H when the sprint can afford a new baseline, 3 to 4 cycles.
7. Not A, not B, not C, not E.

The measurement that proves each saving is night 146 against night 145,
from `turns.ms` and the accounts:

- J: turns over 60 seconds, 35 to under 10; the walks' generated tokens,
  793k to under 650k; "cut at the output budget" sessions rise, and that is
  the design.
- I: fabricated tokens after a `TOOL:` line, 179k to under 20k; the
  account "wrote its own tool results" stays at about 74 sessions, which
  proves the sign still counts.
- Both: the walks' model minutes, 262.9 to about 210, at the same swap
  count, about 103.
- The fixed cost: the sum of Ollama's `total time` against the sum of
  `turns.ms`, and `prompt eval time` against the fit's 18 minutes.

Combinations: J and I combine. Either combines with G and with the first
report's D and E in onboarding. H replaces the measurement baseline, so it
runs alone on its first night. F combines with all, after the ruling.

Onboarding: J and I cut onboarding generation a little, about 15 of its 31
minutes are generation, and fabricated results there were not counted. The
first report's D, recorded wakes, and E, the principal replayed, stay first
for onboarding, 27 of 31 minutes.

Composition lines: I and J touch no line of `plans/composition.md`. A cap
and a stop are limits on the acting register, and the seat still restarts
from records. F changes a door's attempt count, which is in the ends-when
rule of 2026-10-03, so it is a ruling and not a composition line. H with
two sessions in flight crosses the record order, one session commits at a
time, and that is a question for Roman before any build.

## 4. Register lines

The frame writes none. The closing session can add two lines to
`plans/operating-facts.md`, the models section: generation runs at 85
tokens a second on both night models at 16384, and the prefix cache holds
inside a session, 85 to 88 percent of each prompt (observed: the fits,
2026-10-13); and the night's `ollama serve` writes no log, so a timing
question needs a launched server with its output to a file (observed:
`gauntlet_click.sh:13` and the log's date, 2026-10-13).
