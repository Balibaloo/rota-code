# Rota LLM Configuration Proposal

## Purpose

Add configurable LLM provider, model, and generation settings to Rota without
weakening its reproducibility guarantees. A completed run must continue to say
which model settings produced it, and cassette replay must not use a response
recorded with materially different request settings.

This proposal is deliberately scoped to Rota's real-model execution path:

```text
CLI and environment -> request configuration -> Pins and Backend -> runner
    -> session provenance and cassette key
```

The initial supported providers are direct Ollama and LiteLLM. Do not add a UI
for this work. The command-line and environment interfaces are the source of
truth for this milestone.

## Current State

The existing design has a useful separation which must be preserved:

- `rota.llm.llm.Pins` carries `model`, `temperature`, `num_ctx`, and the prompt
  hash. It travels with each completion and is stored with the session.
- `OllamaBackend` constructs the direct `/api/chat` request.
- `LiteLLMBackend` is an optional provider adapter.
- `rota.tools.onboard_run` is the only production-oriented command with a
  `--model` flag today.
- Cassettes are keyed by `(model, temperature, num_ctx, protocol, system, user)`.
- The engagement database stores selected pins in `sessions` as individual
  columns.

Do not place LLM request settings in `rota.core.config.SETTINGS`. Those are
live, database-backed engagement policy controls. Changing an LLM request
setting there halfway through a run would make it unclear which settings
produced an already-recorded session. Model request settings are immutable
per-run provenance and belong in `Pins`.

## Design Decisions

### 1. Separate request pins from transport configuration

`Pins` must contain every setting that can change a model response:

```python
@dataclass(frozen=True)
class Pins:
    model: str = DEFAULT_MODEL
    temperature: float = DEFAULT_TEMPERATURE
    num_ctx: int = DEFAULT_NUM_CTX
    max_tokens: int = DEFAULT_MAX_TOKENS
    top_p: float | None = None
    seed: int | None = None
    repeat_penalty: float | None = None
    prompt_hash: str = ""
```

Use a separate immutable `BackendConfig` for how Rota reaches a provider:

```python
@dataclass(frozen=True)
class BackendConfig:
    provider: str = "ollama"
    endpoint: str | None = None
    timeout_seconds: float = 300.0
```

Do not include API keys in either object. The LiteLLM provider reads provider
credentials through its normal environment variables. Rota may accept a
non-secret `--api-key-env NAME` later only if a concrete provider requires it;
it must record the environment-variable name, never its value.

### 2. Keep portable settings explicit

The initial portable flags are:

| Flag | Environment default | Type | Notes |
| --- | --- | --- | --- |
| `--provider` | `ROTA_PROVIDER=ollama` | choice | `ollama` or `litellm` |
| `--model` | `ROTA_MODEL` | string | Provider model identifier |
| `--temperature` | `ROTA_TEMPERATURE=0.0` | float | Must be `>= 0` |
| `--num-ctx` | `ROTA_NUM_CTX=12288` | integer | Must be `> 0` |
| `--max-tokens` | `ROTA_MAX_TOKENS=2048` | integer | Must be `> 0` |
| `--top-p` | `ROTA_TOP_P` | float | When supplied, must satisfy `0 < top_p <= 1` |
| `--seed` | `ROTA_SEED` | integer | Optional deterministic sampling seed |
| `--repeat-penalty` | `ROTA_REPEAT_PENALTY` | float | Optional; currently Ollama-specific |
| `--endpoint` | `ROTA_ENDPOINT` | URL/string | Provider endpoint override |
| `--timeout` | `ROTA_TIMEOUT=300` | float | Must be `> 0` seconds |

Do not make an unbounded `--param key=value` interface in the first change.
Silent provider-specific no-ops would contaminate experiments. Add a provider
option only after its mapping and validation are covered by a backend test.

### 3. Resolve configuration once per invocation

Add a construction seam in `rota.llm.llm`, for example:

```python
def build_runtime(config: BackendConfig, pins: Pins) -> Backend:
    ...
```

The command parses flags and environment defaults, validates the resulting
objects, creates one backend and one `Pins` value, and passes both into the
loop. A run therefore cannot accidentally change model settings between
sessions.

Retain `default_backend()` and `Pins()` as backward-compatible defaults for
tests and current callers. They should resolve to the same Ollama defaults.

## Provider Request Mapping

`OllamaBackend.complete()` must construct `options` from the supplied pins:

```python
options = {
    "temperature": pins.temperature,
    "num_ctx": pins.num_ctx,
    "num_predict": pins.max_tokens,
}
if pins.top_p is not None:
    options["top_p"] = pins.top_p
if pins.seed is not None:
    options["seed"] = pins.seed
if pins.repeat_penalty is not None:
    options["repeat_penalty"] = pins.repeat_penalty
```

`LiteLLMBackend.complete()` must map portable pins using its named completion
arguments:

```python
kwargs = {
    "model": normalized_model,
    "messages": messages,
    "temperature": pins.temperature,
    "max_tokens": pins.max_tokens,
}
if pins.top_p is not None:
    kwargs["top_p"] = pins.top_p
if pins.seed is not None:
    kwargs["seed"] = pins.seed
if tools:
    kwargs["tools"] = tools
```

Do not pass `num_ctx` to LiteLLM as a portable argument. Different remote
providers handle context-window selection differently, and a parameter that
LiteLLM accepts does not imply the target provider honors it. Continue to keep
the requested `num_ctx` as Rota provenance; document that it is enforced by
Ollama and advisory for LiteLLM unless a provider-specific adapter proves
otherwise.

For Ollama, `--endpoint` replaces the host used for `/api/chat` and `/api/show`.
The `supports_tools` capability lookup must use the instantiated backend's host,
not the module-level default host.

## Required Correctness Repair

Before comparing models or providers, repair the native-tool calling path:

1. `runner.run_session()` calculates `schemas` but currently calls
   `backend.complete(system, user, pins)` without `tools=schemas`.
2. Pass `tools=schemas` into every completion call.
3. Ensure `LiteLLMBackend.complete()` forwards the tool schemas to LiteLLM.
4. Add a deterministic test using `ScriptedBackend` that asserts schemas were
   offered when `native_tools=True`.

This is a prerequisite because otherwise provider/model comparison can differ
only because function calling was not actually enabled.

## Provenance and Migration

Every output-affecting pin must be persisted and used in cassette identity.

### Sessions

Keep existing `sessions.model`, `sessions.temperature`, `sessions.num_ctx`, and
`sessions.prompt_hash` columns for convenient queries. Add:

```sql
pins_json TEXT NOT NULL DEFAULT '{}'
backend   TEXT
```

`pins_json` is `json.dumps(pins.as_dict(), sort_keys=True)`. It makes future
fields additive rather than requiring a schema-column migration for every new
provider feature. `backend` records the adapter used, such as `ollama` or
`litellm`, but never endpoint credentials.

Update the database initialization/migration path so existing databases gain
the new columns using `PRAGMA table_info` followed by `ALTER TABLE` when needed.
Follow the migration pattern already used by `rota.llm.cassettes.open_dev_db`.

### Cassettes

Update cassette key construction to hash the complete canonical pin dictionary
instead of individually listing model, temperature, and context:

```python
blob = json.dumps(
    {"pins": pins.as_dict(), "protocol": protocol, "system": system, "user": user},
    sort_keys=True,
    separators=(",", ":"),
)
```

This intentionally invalidates old cassette keys for configurations whose new
default fields matter. A stale recording must never answer for an unrecorded
configuration. Existing cassette rows may remain readable but will be cache
misses under the new key scheme; no destructive migration is required.

Add `pins_json` to the cassette table as an audit field and migrate it with a
default of `'{}'` for old rows. Preserve the existing queryable columns.

## CLI Work

Extend `python -m rota.tools.onboard_run` first. It is the existing real-model
execution entrypoint and provides a bounded surface for the implementation.

Example:

```powershell
python -m rota.tools.onboard_run --root D:\src\target --db .rota\target.db `
  --provider ollama --model qwen3.5:9b --temperature 0.15 --num-ctx 16384 `
  --max-tokens 3072 --top-p 0.9 --seed 42 --timeout 600
```

Flags override environment defaults. Parser errors must be clear and happen
before a database is modified or a network request occurs.

For the first implementation, `--repeat-penalty` must fail with a clear parser
or validation error when `--provider litellm` is selected. Do not silently drop
it.

## Files Expected to Change

- `rota/llm/llm.py`: pin fields and validation, backend configuration/factory,
  Ollama and LiteLLM request mapping, tool forwarding.
- `rota/core/runner.py`: pass native tool schemas to `Backend.complete`; use the
  configured Ollama host for tool-capability detection.
- `rota/llm/cassettes.py`: canonical pin-based key and cassette audit storage.
- `rota/core/schema.sql`: additive session provenance columns.
- `rota/core/db.py`: store serialized pins and backend name; migrate existing
  session tables if database initialization owns schema migration here.
- `rota/tools/onboard_run.py`: parser flags, environment precedence, creation
  and passing of `Pins` and `BackendConfig`.
- `tests/rota/`: focused unit tests for the above behavior.
- `rota/README.md`: concise usage example and reproducibility note.

Avoid unrelated changes to graph design, scheduler policy, cockpit layout, or
role prompts.

## Test Plan

Add focused tests before relying on a live provider:

1. `Pins.with_prompt()` preserves all added fields, and `Pins.as_dict()` is
   complete and JSON-serializable.
2. Invalid values fail clearly: negative temperature, non-positive context or
   token limits, invalid `top_p`, and non-positive timeout.
3. Ollama request payload has the expected `options`; optional keys are absent
   when unset.
4. LiteLLM receives portable arguments and tool schemas; its model
   normalization remains compatible with `ollama/<model>` inputs.
5. The runner passes tool schemas when native tools are enabled.
6. Two cassettes differing only in each new output-affecting pin have different
   keys; identical settings retain a key.
7. Session commit records legacy columns, sorted `pins_json`, and backend name.
8. Existing databases migrate without losing existing `sessions` data.
9. CLI flags override environment variables; unsupported provider/option pairs
   fail before `drive()` starts.

Run at minimum:

```powershell
python -m pytest tests/rota/test_runner.py tests/rota/test_config.py -q
python -m pytest tests/rota/ -q
```

After deterministic tests pass, perform one manual Ollama smoke run with an
existing local model. Do not make live LLM calls part of the deterministic test
suite.

## Acceptance Criteria

- A user can select Ollama or LiteLLM and configure the documented portable
  request controls through CLI flags or environment defaults.
- All response-affecting settings are immutable `Pins`, are visible in session
  provenance, and affect cassette identity.
- Backend transport settings do not contain secrets and do not enter cassette
  keys.
- Unsupported provider-specific controls fail loudly rather than being ignored.
- Native tool schemas are passed through the runner to both supported backends.
- Existing deterministic Rota tests remain green, and the added focused tests
  cover parsing, validation, payload mapping, cassette identity, migration, and
  persistence.
- No live model call is required by the normal test suite.

## Implementation Order

1. Add `Pins` fields, validation, canonical serialization, and backend request
   mapping tests.
2. Repair native tool forwarding and validate it with a deterministic runner
   test.
3. Change cassette keying and storage, then add collision/differentiation tests.
4. Add session provenance schema/migration and commit tests.
5. Add `BackendConfig`, provider factory, and `onboard_run` flags with CLI/env
   precedence tests.
6. Update the README and run the full deterministic Rota suite.

Keep commits logically separated by those stages where practical. Do not turn
this into a generic provider framework until a second real provider exposes a
concrete incompatibility that the two-adapter design cannot express.