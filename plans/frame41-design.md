# Frame 41, a sub-agent drives the walk as the principal: the design

Status: written by session 225aec9c on 2026-10-08, before any code. Meta
workflow unless a line says rota workflow.

## 1. What the walk does today

`probes/walk.py` holds the principal's seat for a night (observed: the file
at 5783cb24, 2026-10-08). `class Principal.respond(ask)` answers every
`present` and `confirm` with `WALK_WORDS`, the sentence `yes that all looks
right, go ahead`, as an `Answer(verb="reply")`. It answers every `clarify`
with the walk's one prepared sentence, the third argument of the walk, as an
`Answer(verb="converse")`. A Liaison chat turn with no page under it, read
by `pending_replies`, gets the same prepared sentence as a new principal
entry and a `converse` message. Each ask is answered once. A second visit
returns `None`, which the seam reads as a deferral.

The cost of that script on night 132 (observed: `plans/night132-read.md`,
section 5, 2026-10-08). Rota workflow. bg_2 was parked, and the Liaison
asked `commit or contest?`. The script answered with the Python-version
sentence. The Liaison took the sentence as chat and replied with a question,
and the script answered the question with the sentence again. Three rounds,
27 chat sessions, 9 rulings on a chat entry, and the sentence reached two
decisions. Night 92 (observed: `plans/stack.md`, frame 41's status of
2026-09-24) merged a helper that returns a string where the request said
`prints`, because the script approved every page.

## 2. The change

One new backend behind the same protocol. `probes/agent_principal.py`
holds `class AgentPrincipal` with `respond(ask)` and `chat(reply)`. The
walk picks it when `WALK_AGENT` names a model, and keeps the script
otherwise, so every recorded night and every case stays as it is.

### The model call

The backend runs the Claude Code binary headless, one process per page:

```
claude -p --bare --model <WALK_AGENT> --output-format json --tools "" --no-session-persistence --system-prompt <the brief>
```

The page goes on stdin. The binary is `CLAUDE_BIN` when set, else the
newest `claude.exe` under
`~/.vscode/extensions/anthropic.claude-code-*/resources/native-binary/`,
else `claude` on the path. The subprocess environment drops `CLAUDECODE`
and `CLAUDE_CODE_ENTRYPOINT`, because a nested session can refuse
(observed: a call with those two unset answered `ready` in 1.3 seconds on
Opus at a cost line of 0.09 dollars, 2026-10-08 09:58; a call with them set
is not tried). The result's `result` field is the person's words. The
fields `is_error`, `duration_ms` and `total_cost_usd` go to the record.

### The person

`probes/principal_brief.md` is the system prompt. It says who the person
is: a careful engineer who runs rota alone on the click repository and
reads what it sends. It holds what the person wants: the three sentences
of the gauntlet, with the walk's current sentence marked, and the three
prepared facts the person holds, one per sentence, which today are the
walk's third argument. It says how the person answers each page kind, in
the words a person uses, with no identifiers:

- A `present` or a `confirm`: approve when every line says what the person
  asked for. Name the one line that does not, and say what is wrong, in
  one sentence. Ask when a line is unclear.
- A `clarify`: answer the question in one sentence from the facts the
  person holds. When the page offers choices, pick one and name it.
- A park ask: choose between the ways the page names. The person prefers a
  fix over giving up on a change they asked for.
- A chat turn with no question under it: say that nothing else is needed,
  once. After that, say nothing, which the backend sends as the one token
  `(nothing)`.

The person answers in one to three sentences, in plain words, and never
writes identifiers, code or lists. The brief carries the last pages and
answers of this walk, up to five, so a second page on one thing reads as a
follow-up and not as a new request (reasoned: `recent_chat` in the Liaison's
converse brief does the same job on the other side).

### Landing

The words land through the same doors as the script's words. A `present`
or `confirm` lands as `Answer(verb="reply", text=words)`. A `clarify` lands
as `Answer(verb="converse", text=words)`. A chat turn lands as the same
entry and `converse` message the walk writes today, except `(nothing)`,
which marks the Liaison's reply answered and writes no entry. Once per ask
stays: a second visit returns `None`.

A failed call, `is_error` or a non-zero exit, returns `None` and prints
`PRINCIPAL ERROR <message id>: <first line of the error>`. A second failure
on the same ask ends the walk with `PRINCIPAL DOWN` and the walk's
`record(..., "principal down")`, so a night never runs on a half-dead
principal (reasoned: a deferred ask is survivable by design, and a walk
that keeps stepping with every ask deferred measures nothing).

### The record

`$ROTA_RUNS/<run>.principal.jsonl`, one row per call: the night, the phase,
the message id, the verb, the page verbatim, the words, `duration_ms`,
`total_cost_usd`, the model, and the clock. The log line keeps today's
shape, `[<id>] <verb>: <head>  -> '<words>'`, so `progress.py` and the
night reads keep working. The walk's end prints the count of calls and the
sum of the cost line.

### The gauntlet

`probes/gauntlet_click.sh` exports `WALK_AGENT="${GAUNTLET_AGENT:-}"`. A
night with `GAUNTLET_AGENT=opus` runs the agent principal in every walk.
Nothing else in the gauntlet changes.

## 3. What this is not

- Not a replacement. The script stays the default (ruled: Roman,
  2026-09-18, a diagnostic).
- Not a designed principal. Frame 42 builds that from what this one shows.
- Not a fix of the Liaison's chat loop. Frame 142 keeps its two doors.
- Not consistent across nights. Two nights on the agent principal differ
  where the person's words differ. The record is what makes a night
  readable.

## 4. Tests

`tests/rota/test_agent_principal.py`, with the subprocess stubbed:

1. The prompt for a `present` holds the brief, the current sentence, the
   page verbatim and the last answers.
2. A `present` lands as `reply`, a `clarify` as `converse`, and a chat turn
   with `(nothing)` writes no entry.
3. A failed call returns `None` once and the second failure on the same ask
   raises the walk's stop.
4. The record row holds the page, the words, the cost and the model.
5. The binary search: `CLAUDE_BIN` first, the extension folder second.

## 5. Ends when

Frame 41's line, unchanged: a night runs with the agent principal and its
record says, per page, what the agent answered and what the system did with
it; the night reaches at least one path the yes-only principal never
reaches. The measure on that night: pages shown, answers by kind, the
paths reached, a contest, a park-ask choice or a chat turn that ends, and
whether frame 142's loop recurs. Price: one implementer pass on Opus, about
80k, one diff review of about 40k, and the night.
