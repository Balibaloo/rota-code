# Tool calling: what was measured, and what follows

`python -m rota.tools.probe_tools --runs 3`, on the target box, one fixture put
to every model twice — once with native tools, once with the `TOOL:` text
protocol. The fixture is Gatekeeper asserting one scope item, which is the
simplest thing any role does, and it is graded on the same terms both ways: a
call named right, with a legal enum, carrying an id and text.

| model | protocol | honoured | median | note |
|---|---|---|---|---|
| `gemma3:4b` | native | **0/3** | — | HTTP 400: rejects the `tools` field |
| `gemma3:4b` | text | 3/3 | 0.4s | |
| `qwen2.5:7b` | native | **3/3** | **0.4s** | |
| `qwen2.5:7b` | text | 3/3 | 0.3s | |
| `llama3.1:8b` | native | **3/3** | **0.4s** | |
| `llama3.1:8b` | text | 3/3 | 0.3s | |
| `qwen3.5:9b` | native | 3/3 | 12.7s | spills to CPU |
| `qwen3.5:9b` | text | 3/3 | 7.3s | |
| `gemma4:31b` | native | 3/3 | 79.9s | |
| `gemma4:31b` | text | 3/3 | 101.0s | |

## This corrects an earlier finding

A previous session recorded that *"all three advertise tool support, only
`qwen3.5:9b` honours it"*. That is wrong: **`llama3.1:8b` honours native tool
calls 3/3 at 0.4s**, and so does `qwen2.5:7b`. Whatever the earlier probe
measured, it was not this.

It matters because the conclusion drawn from it — that the fast models could not
do native calling — is what left `TOOL:` as the only path.

## What follows

**Native is primary.** `llama3.1:8b` stays the default: fastest, and it honours
tools. The runner passes schemas whenever the backend is Ollama and the model
advertises the capability, and reads `completion.tool_calls` before falling back
to the text parser.

**`TOOL:` stays, for models that cannot.** `gemma3:4b` returns a 400 with a
`tools` field present — that is precisely the case the text protocol was written
for, and it is 3/3 on it.

**Neither is faster.** 0.3s against 0.4s is noise at this size. The reason to
prefer native is not speed:

- **no marker to drop.** The failure that cost the most was a model omitting
  `TOOL:` and the session committing *empty* — success-shaped failure.
  `extract_lenient` exists only to soften it, and it cannot be needed here
- **no quoting.** Arguments arrive as a structure rather than as text that has
  to survive a hand-rolled parser
- **trained behaviour.** A bespoke protocol competes with what the model was
  taught; the schemas are generated from `inspect.signature`, so the
  advertisement cannot drift from what is callable

## What this leaves open

The native path was **built and never wired**: `llm.py` parsed `tool_calls`,
`toolschema.py` generated the schemas, `runner.py` computed them into a variable
and then called `complete()` without passing them. Two lines. It is wired now,
and this is the fourth instance of the pattern the edge audit named — a
capability that exists, is reachable, and is connected to nothing.

Cassettes are keyed per model **and per protocol**. Native and text are different
evidence about different things, and a recording of one is not evidence about the
other.
