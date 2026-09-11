# Model setup: one modal, one profile

Written 2026-09-11 from a discussion. Not built. Not ruled.

## The vision

One screen in the TUI. The person sees the providers on this machine and any
remote ones they have named, the models each provider can serve, what this
machine can hold, and a recommendation. The screen's product is a profile
file. Nothing below the profile changes.

Local and remote are the same screen because they produce the same file. The
web cockpit reuses the same backend functions later.

## What exists today

A profile is `[provider]` (kind: ollama or litellm, endpoint, timeout),
`[pins]` (temperature, num_ctx), and `[models]` (a default and per-desk
overrides). Shipped profiles live in `rota/llm/profiles/`. User profiles live
in `~/.rota/profiles/` or `<project>/.rota/profiles/`. `rota profile
list|show|check|set`, `rota onboard --profile`, `rota run --model --role`.

`OllamaBackend` reads `/api/tags` and `/api/ps`. `LiteLLMBackend` reaches any
OpenAI-shaped endpoint. `local-openai` proved that path live: 46 sessions
through litellm against Ollama's `/v1`.

The register: cases per role, recorded per model, pass counts in `case_runs`.
Recorded on llama3.1:8b, qwen3:8b, qwen3.5:9b. llama wins most cases; `local`
(qwen) is the profile that merged.

The walks: tipsAP merged cold on `local`. tipsAQ (all llama) and tipsAR (best
per desk) did not merge.

## Backend functions

One module, `rota/llm/discover.py`. The TUI calls it. The cockpit exposes the
same functions as JSON later.

- `providers()`: the local providers found (Ollama, a llama.cpp server on its
  port) and the remote ones named in user profiles or the keys file.
- `models(provider)`: the models a provider can serve. Ollama: `/api/tags`.
  OpenAI-shaped: `/v1/models`. Remote: the same call with a key.
- `system()`: RAM, VRAM total and free, platform. RAM from psutil. VRAM: ask
  the provider first (`/api/ps` reports `size_vram`), then nvidia-smi, then
  None. On Apple Silicon memory is unified: VRAM is RAM. None means "cannot
  say", never zero.
- `recommend(models, system, benchmarks)`: a pure function. Returns one model
  per capability group, with the fit: in VRAM, spills to RAM, does not fit.
  Context is part of it: weight size from the registry (Ollama blob size,
  Hugging Face file size), KV cache from the GGUF metadata (layers, heads,
  head size) at the proposed num_ctx. No model is loaded to get a number.
  `size_vram` from a loaded model is a check only.
- `pull(provider, model)`: the one side effect. Ollama: `/api/pull` with
  streamed progress. llama.cpp: no pull endpoint; show the model name, the
  expected path if documented, and found or not found. Remote: no pull. Never
  guess a folder.

Rules:

- Discovery refuses to run while a run is driving. One GPU. Loads evict the
  walk's models and per-load determinism resets. Same rule as re-indexing.
- The modal writes user profiles only, copied from a shipped one as the start.
- Per-desk overrides stay in the file as an expert option. The recommendation
  fills the groups; a person can override a desk.

## Keys

The profile never holds a key. `[provider]` gets `key_env = "NAME"`. The modal
reads and writes `~/.rota/keys.env` with restricted permissions. Environment
variables win over the file. Local providers usually need none; litellm
demands one for the OpenAI shape, any word does for Ollama. Keychains are on
the long-term list.

At the moment of choosing a remote provider, the screen says in words that
prompts and the repository's code are sent to that endpoint. The profile
records `remote = true` so the run summary can repeat it. `rota onboard`
already says this once; the screen is where the choice is made. AUDIT items 8
and 9.

## Capability groups

Derived from the graph, not hand-written. `obligations.py` lists what each
mode reads and writes. Group modes by shape: read code and write code or
tests; read rows and write rows; read prose and write pages. A mode may sit
in a different group from its role: the Architect's survey reads code, its
grouping reads rows.

The graph gives the partition. It does not give the ranking. Ranking within a
group comes from the benchmark. If the benchmark shows two modes in one group
disagreeing on the best model, the group splits.

## Benchmarks are the ground truth

The recommendation's numbers come from measurement, never from a guess.

- Sources: the register (cases per role, per model), the gauntlet (walks:
  merged or not, steps, per profile per repository), a tool check per
  provider and model, and new cases where a capability has none.
- A table, `benchmarks(model, capability, score, recorded_on)`, written once
  per model from those sources, and shipped with rota. Users never run
  benchmarks. Costly runs happen once, on this machine or a friend's; the
  friend's machine adds models, the set is the same.
- The walks should start writing their own result row now: profile,
  repository, merged, steps. Then the table has its shape before any new
  machine runs.
- Some manual evaluation is needed until the walk table exists, because today
  the register and the walk disagree: llama wins cases, qwen merges.
- An unrecorded model is still an option. The screen shows it with "no
  benchmark on record".

## Providers: a tool check, not a walk

Before a provider and model are listed as supported: one fixed prompt that
must answer with a `TOOL:` line, and one that must answer with a native tool
call. Pass or fail, recorded like a case, its own tier in the register. Local
walks per provider go to the end of the plan.

## Open questions

- Keys: a restricted file for now. Keychain later. Ruled provisionally, not
  finally.
- num_ctx from arithmetic measures one model. The walk profile keeps two
  resident. Fit must be computed for the set, not the model.
- Native tool calling is measured nowhere. The tool check covers the
  transport; a walk with native calls on is a separate item.
- The register cannot vouch for models it has not recorded. Discovery shows
  them; recommendation does not rank them.

## Order

1. Walks write a result row.
2. `discover.py`: providers, models, system, recommend with the fit only.
3. The keys file and the `key_env` field, with the audit sentence on screen.
4. The tool check tier in the register.
5. The benchmarks table from the register and the walk rows; recommend reads
   it.
6. The TUI modal.
7. Capability groups from `obligations.py`.
8. `pull` for Ollama.
9. Cockpit endpoints.
10. Local walks per provider, native tool calls on.
