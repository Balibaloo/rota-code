# Frame 237, the interview of the Terminologist on s187 turn 1

Rota workflow, the Terminologist's survey after a merge. Written 2026-10-14 19:18 by the probe agent of the meta workflow.

## Verdict

The prose list does not reproduce on a replay of s187 turn 1. The unchanged prompt writes 0 of 3 prose lists and 0 amend calls (observed: 2026-10-14). Candidate A turns the seat to `TOOL: glossary.amend(...)` lines in 3 of 3 runs, 54 lines each (observed: 2026-10-14). The interview names no new line. It names the system prompt's generic `TOOL:` rule as the line that tells the form, and it says no call was shown for `glossary.amend` (observed: 2026-10-14).

## 1. The command and the pins

Interview command, run three times, outputs in `interview-1.txt` to `interview-3.txt` of the scratchpad folder `f237`:

```
.venv/Scripts/python.exe probes/frame37/interview_turn.py --db .rota/clickI_night147.db --sid s187 --seq 1 --questions <scratchpad>/q237.txt --timeout 600
```

Pins from `sessions.pins_json` of s187: model `qwen3.5:9b`, num_ctx 16384, temperature 0.0, think null. A null think pin sends `think: false`, as `rota/llm/llm.py` `THINK_DEFAULT` does. The interview prompt is 4884 tokens, and each answer is 410 tokens.

Caution: `interview_turn.py` sends the turn's system and user text only. It does not send the recorded completion. So the seat in that interview never sees the reply it is asked about (observed: the tool's request body, lines 77 to 80). I ran one more interview, `interview_seen.py`, that adds the recorded completion as the assistant message before the questions. Its output is `interview-seen.txt`.

## 2. The three interviews, verbatim

Runs 2 and 3 are byte-identical to run 1 in the answer section (observed: `diff`, 2026-10-14). Run 1 answers, verbatim:

```
1. I did not write the line "`glossary.amend`:" followed by a list; that format was never generated in my response. The instruction requires each `glossary.amend` call to be written on its own line as a tool invocation, not as a description or batched list.

2. The brief states: "Call one per line. `TOOL:` is a literal marker — write those five characters, then the function name from the list above, then its arguments in brackets:" and gives the example format:  
   `TOOL: artefact.verb(key='value')`  
   This tells me that each tool call must be on its own line, starting with `TOOL:`, followed by the function name and arguments exactly as shown.

3. I did not write "`code.source`:" followed by a list of file paths in my reply. The brief instructs to call `code.source` for anything `[code.area]` says it left out — but since no words were unexplained, no such calls were needed. If they had been needed, each path would be its own line under `TOOL: code.source(path=...)`.

4. The line in the brief that specifies the exact form of a call is:  
   `"Call one per line. `TOOL:` is a literal marker — write those five characters, then the function name from the list above, then its arguments in brackets:"`  
   This tells me to write each tool call as a separate line starting with `TOOL:` followed by the function and arguments.

5. No part of the brief shows an example of a full `glossary.amend` call written out like:  
   `TOOL: glossary.amend(term=..., sense_body=..., sense_short=...)`  
   The only example given is for `artefact.verb(key='value')`, which illustrates the general format but not specifically for `glossary.amend`.
```

The added interview with the completion in view (`interview-seen.txt`, 5148 prompt tokens, 278 out), verbatim:

```
1. I meant those list lines to be descriptions of what I would record, not runnable calls. The format `glossary.amend:` followed by indented terms is a description, not a tool invocation.

2. The brief states: "Call one per line. `TOOL:` is a literal marker — write those five characters, then the function name from the list above, then its arguments in brackets:" and gives examples like `TOOL: artefact.verb(key='value')`. It also says "Emit no tool calls when you are done."

3. I meant that as one call per path, but formatted incorrectly because I did not include the `TOOL:` prefix or bracketed arguments. The correct format would be separate lines like `TOOL: code.source(path="src/click/core.py")`.

4. The line "Call one per line. `TOOL:` is a literal marker — write those five characters, then the function name from the list above, then its arguments in brackets:" tells me the form a call takes.

5. No. There was no example of a full call written out in the brief; only the format description and examples like `TOOL: artefact.verb(key='value')` which use a placeholder function name (`artefact.verb`) not present in my working set.
```

## 3. Where the runs agree

- The three `interview_turn.py` runs agree word for word. Temperature 0 on this prompt is deterministic here (observed).
- Without the completion, the seat denies that it wrote the list (answers 1 and 3). The denial is true of its context, which holds no reply. So answers 1 and 3 of those runs carry no information (reasoned: the tool sends no completion).
- With the completion in view, the seat says the `glossary.amend`: list was "descriptions of what I would record, not runnable calls". It says the `code.source`: list was "one call per path, but formatted incorrectly because I did not include the `TOOL:` prefix" (observed).
- All four interviews quote the same line for the form of a call: "Call one per line. `TOOL:` is a literal marker ... then its arguments in brackets:". All four say that no full call of `glossary.amend` was shown. The only example is `TOOL: artefact.verb(key='value')`, a placeholder name "not present in my working set" (observed).
- Question 4: no run names a new line. Each run names the generic line already in the system prompt.

## 4. The candidates and the substituted paragraph

The amend sentence is in the `system` field of `turns`, at character 633 of 2910. The `user` field (15186 characters) does not hold it (observed).

The original paragraph, as the seat read it:

```
Then record only the words your account needed that the
glossary does not already carry, with `glossary.amend`: `sense_body` the
explanation, `sense_short` one clause summarising it, both saying something you
could only know from having read this code.
```

Candidate A, substituted for that span (`cand-A.txt`; full prompt in `system-A.txt`):

```
Then record only the words your account needed that the glossary does not already carry. Write each word as one call on its own line: `TOOL: glossary.amend(term="...", sense_body="...", sense_short="...")`, `sense_body` the explanation, `sense_short` one clause summarising it, both saying something you could only know from having read this code. A list under a call name runs nothing.
```

Candidate B is skipped. The answer to question 4 names the generic `TOOL:` line, which A's shape already carries. It names no line that differs from A (reasoned: brief rule "Skip B when the answers name A's shape or name nothing").

Script: `f237/replay.py`. It opens the night database read-only, replaces the span by regex, asserts one match, and sends `/api/chat` with model, num_ctx, temperature 0 and think false. It does not send `num_predict` 8192, which the runner sends. That option caps length only and does not change the sampled tokens (reasoned).

## 5. The replay counts

| Candidate | Runs | Runs with a `TOOL: glossary.amend(` line with `term=` | Such lines per run | Runs with a "`glossary.amend`:" prose list | Files |
|---|---|---|---|---|---|
| Baseline, unchanged | 3 | 0 | 0, 0, 0 | 0 | `replay-base-1.txt` to `-3.txt` |
| A | 3 | 3 | 54, 54, 54 | 0 | `replay-A-1.txt` to `-3.txt` |

Log: `f237/replay-log.txt`. All files are in the scratchpad folder `f237`.

The baseline replay does not reproduce the night. Each baseline run writes two sentences, then five correct `TOOL: code.source(path=..., start=0, end=400)` lines, and no amend (observed). The recorded completion starts with the same 80 characters and then diverges: "from invocation to completion" on the night, "from initialization to execution" on the replay (observed). The night's divergence is GPU nondeterminism or a request difference that this probe does not hold (reasoned, not run).

Candidate A has two side effects (observed in `replay-A-1.txt`):

- It writes 54 amend calls, most of them for names that are only identifiers from the code (`INT`, `_ansi_re`, `__version__`). The brief says "Two you have understood beats eight you have named". So A moves the form and breaks the count.
- The last line is `surveys.attest(outcome="found", ...)` with no `TOOL:` prefix. That call would not run either.

## 6. My reading of what moved the seat

- The form of the call is not the seat's gap in general. On the same prompt, at the same pins, the seat writes `TOOL: code.source(...)` correctly in 3 of 3 runs (observed).
- The seat reads the brief sentence "with `glossary.amend`: `sense_body` ..., `sense_short` ..." as the shape of a description. With its reply in view, it says the list was a description of what it would record (observed: `interview-seen.txt`, answer 1).
- The only call example in the prompt uses a placeholder verb. The seat says that example is "not present in my working set" (observed). So the seat has no `glossary.amend` call to copy, and it copies the brief sentence's shape instead (reasoned).
- A written-out `TOOL: glossary.amend(term=...)` example moves the form in 3 of 3 runs (observed). The cause the read named holds for the form (reasoned from both facts above).
- A alone is not ready to ship. It needs a line that keeps the count small, for example "Write one call for each word your account used, at most a few", and the attest line needs the `TOOL:` prefix shown too (reasoned, not run).
- The baseline is 0 of 3 for the prose list. So a replay of s187 turn 1 cannot prove a fix against the defect. A proof needs the defect on a replay first: more seeds, `num_predict` set, or another of the 8 sessions (reasoned).

## 7. Tokens

About 40k tokens of this agent's context. GPU time is about 4 minutes for 3 interviews, 1 added interview and 6 replays.
