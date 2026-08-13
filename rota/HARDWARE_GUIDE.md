# Rota Model Menu Reference

**Snapshot date:** 2026-08-11. This is a menu-design reference, not a permanent
ranking. Providers and Ollama tags change. A selected profile becomes usable
only after Rota's native-tool probe and L1 evidence pass on the user's machine.

Rota users are configuring an autonomous team: roles receive a scoped working
set, call only their granted tools, write owned artefacts, and hand work to the
next role. They are not selecting a chat model for casual conversation.

The configuration menu therefore needs to answer three user questions:

| User choice | What Rota configures | What Rota must guarantee |
| --- | --- | --- |
| Run here or use a provider? | Ollama download versus hosted provider connection | The selected provider can execute native tools. |
| How much local capability is available? | A model matched to installed GPU VRAM | The model stays on GPU for the selected Rota context. |
| Standard or extended working set? | A validated `num_ctx` setting | Every role retains its instructions, working set, and room for tool feedback. |

This document deliberately contains **no CPU-only configuration**. CPU-only
execution cannot provide the repeatable, multi-turn latency required by Rota's
intended workflow.

## Non-Negotiable Floors

| Question | Answer | Why |
| --- | --- | --- |
| Is 4K context usable for intended Rota use? | **No.** | Rota's measured largest prompt is about 9.2K tokens. At 4K, the model loses instructions or working-set material before it has room to answer. |
| Minimum selectable Rota context | **12,288 tokens** | It is the first established configuration that holds the known working set plus Rota's 2,048-token output cap. |
| Are models below 7B reliable enough as the primary agent? | **No.** | They can be useful for narrow classification or summarization, but not as Rota's general tool-use worker. Tool syntax may be correct while judgement, constraint following, recovery after a tool error, and multi-turn consistency are not. |
| Minimum local model class | **7B/8B instruct or agent model** | This is the smallest class worth exposing as a primary local profile. |
| Is CPU offload acceptable? | **No.** | A slow single completion multiplies across tool turns; do not present an offloaded profile as a usable Rota configuration. |
| Is advertised model context the Rota context to select? | **No.** | The model's maximum is an upper bound. The selected context must fit weights, KV cache, compute buffers, and the user's actual VRAM. |

`num_ctx` covers the whole request: system instructions, tool schemas, role
working set, tool results, and completion. With Rota's current 2,048-token
output cap, treat about 80% of `num_ctx` as usable input budget.

| Selected context | Approximate input budget | User-facing meaning |
| ---: | ---: | --- |
| 12,288 | ~9.8K | Standard Rota working set; minimum menu option. |
| 16,384 | ~13.1K | Extended working set; show only when the selected model remains `100% GPU`. |
| 24,576 | ~19.7K | Long working set; show only for a model/GPU pair that passed KV-cache validation. |
| 32,768+ | Variable | Advanced server-class option; must be tested for the exact model and GPU. |

## Catalog Readiness

These are catalog-maintenance states. A normal user should see only `verified`
profiles by default; candidates belong in an optional “try and validate” view.

| State | Meaning | Menu behaviour |
| --- | --- | --- |
| `verified` | Probed with Rota's native-tool fixture and real Rota cases on recorded hardware. | Offer normally. |
| `candidate` | Current model claims/tools support; not yet evidenced by Rota. | Optional test view only; never preselect. |
| `experimental` | May work, but hardware fit, latency, or tool reliability is uncertain. | Keep out of the normal configuration menu. |
| `unsupported` | Fails Rota's context, size, or runtime floor. | Do not display as a configuration option. |

## Local Ollama Download Catalog

The future menu uses `pull` as its download action. The context field is the
Rota working-set setting, not the model's advertised maximum context. The
verified models form the initial visible local menu; candidates are current
options to validate as the catalog grows.

| Hardware | Menu profile | Ollama tag | Pull command | Context | State | Notes |
| --- | --- | --- | --- | ---: | --- | --- |
| 8 GB+ VRAM | Llama 3.1 8B | `llama3.1:8b` | `ollama pull llama3.1:8b` | 12K | `verified` | Rota's current default; 4.9 GB download; native tools passed 3/3. |
| 8 GB+ VRAM | Qwen 2.5 7B | `qwen2.5:7b` | `ollama pull qwen2.5:7b` | 12K | `verified` | Rota alternate; native tools passed 3/3. |
| 8 GB+ VRAM | Qwen 2.5 Coder 7B | `qwen2.5-coder:7b` | `ollama pull qwen2.5-coder:7b` | 12K | `candidate` | 4.7 GB code-focused model with tool capability; validate against Rota roles. |
| 8 GB+ VRAM | Qwen 3 8B | `qwen3:8b` | `ollama pull qwen3:8b` | 12K | `candidate` | 5.2 GB; current general reasoning/agent model. |
| 10 GB+ VRAM | Ministral 3 8B | `ministral-3:8b` | `ollama pull ministral-3:8b` | 12K | `candidate` | 6.0 GB, tools/JSON/vision; requires the Ollama version listed by its model card. |
| 12-16 GB VRAM | Qwen 3 14B | `qwen3:14b` | `ollama pull qwen3:14b` | 12K | `candidate` | 9.3 GB; do not present as fully GPU-resident on a 10 GB card. |
| 12-16 GB VRAM | Ministral 3 14B | `ministral-3:14b` | `ollama pull ministral-3:14b` | 12K | `candidate` | 9.1 GB; tool capable; validate GPU headroom before offering 16K. |
| 16 GB+ VRAM | Gemma 3 12B | `gemma3:12b` | `ollama pull gemma3:12b` | 12K | `candidate` | 8.1 GB multimodal option. Do not use Rota's old `gemma3:4b` native-tool result to infer this model's behaviour. |
| 24 GB+ VRAM | GPT-OSS 20B | `gpt-oss:20b` | `ollama pull gpt-oss:20b` | 16K | `candidate` | 14 GB MXFP4 MoE model designed for reasoning and agents; validate actual tool calls and latency. |
| 24 GB+ VRAM | Devstral 24B | `devstral:24b` | `ollama pull devstral:24b` | 16K | `candidate` | 14 GB coding-agent model. Prefer for code-heavy roles after Rota validation. |
| 24 GB+ VRAM | Qwen 3 30B-A3B | `qwen3:30b` | `ollama pull qwen3:30b` | 16K | `candidate` | 19 GB MoE; strong agent candidate but needs a 24 GB-class card. |
| 24 GB+ VRAM | Qwen 3 Coder 30B-A3B | `qwen3-coder:30b` | `ollama pull qwen3-coder:30b` | 16K | `candidate` | 19 GB code-agent model; use when coding quality outranks local latency. |
| 80 GB+ VRAM | GPT-OSS 120B | `gpt-oss:120b` | `ollama pull gpt-oss:120b` | 32K | `experimental` | 65 GB; server-class profile, not a common desktop configuration. |
| 80 GB+ VRAM | Qwen 3 Coder 480B | `qwen3-coder:480b` | `ollama pull qwen3-coder:480b` | 32K | `experimental` | Requires at least 250 GB memory for local use; include as a discovery entry only. |

### Explicit Local Exclusions

| Model/tag | Why it is not a primary Rota profile |
| --- | --- |
| Any 0.5B-4B model, including `qwen3:4b`, `llama3.2:3b`, and `gemma3:4b` | Below the 7B/8B reliability floor for general tool-agent work. |
| `command-r7b:7b` | The Ollama tag exposes only 8K context, below Rota's 12K minimum. |
| `qwen3.5:9b` on the measured RTX 3080 | Rota measured CPU spill and more than 100 seconds per turn. |
| `gemma4:31b` on the measured RTX 3080 | Rota measured swapping; it does not fit the intended loop. |
| 14B models on 10 GB VRAM | Weight files nearly consume the card before context/KV/compute buffers. |

## Hardware to Local-Profile Lookup

The menu should detect VRAM, then present only the rows viable for that machine.
It should not make the user reason from model parameter counts or quant names.

| GPU VRAM | Local profile shown | Default context | Next capability step | Notes |
| ---: | --- | ---: | --- | --- |
| 8 GB | 7B/8B Ollama model | 12K | Hosted | Validate the desktop has enough free VRAM. |
| 10 GB | 7B/8B fully GPU-resident | 12K | Hosted | The repository's RTX 3080 profile. 14B is not a normal local option. |
| 12 GB | 7B/8B; measured 14B candidate | 12K | Hosted | Only advertise a 14B profile after `ollama ps` shows no CPU split. |
| 16 GB | 14B | 12K, then 16K | 24B/30B hosted or local if measured | Useful quality step without hybrid execution. |
| 24 GB | 20B/24B/30B MoE | 16K | Hosted frontier | Still run one Rota session at a time. |
| 48 GB | 32B-class and selected larger models | 16K-32K | Hosted frontier | Context growth still consumes substantial KV memory. |
| 80 GB+ | 70B/120B/server models | 32K+ | Hosted frontier | Treat as server deployment, with concurrency budgeting. |

## Hosted Provider Catalog

Hosted profiles are the way a Rota user obtains higher capability without a
larger local GPU. They are **not implemented in Rota's production path yet**:
the current LiteLLM adapter does not forward tool schemas or expose the planned
provider/configuration flags. The future menu must enable a provider only after
that provider passes the same Rota native-tool test as a local model.

| Provider | Menu profile | Current provider model ID | Context | Intended use |
| --- | --- | --- | ---: | --- |
| OpenAI | Frontier reasoning/coding | `gpt-5.6-sol` | 1.05M | Hardest agentic coding and recovery. |
| OpenAI | Balanced reasoning/cost | `gpt-5.6-terra` | 1.05M | General hosted escalation. |
| OpenAI | High-throughput | `gpt-5.6-luna` | 1.05M | Cost-sensitive routine roles. |
| Anthropic | Frontier agent | `claude-fable-5` | 1M | Highest-capability long-running agents. |
| Anthropic | Complex coding | `claude-opus-5` | 1M | Difficult coding and independent review. |
| Anthropic | Balanced agent | `claude-sonnet-5` | 1M | Default high-quality hosted profile. |
| Anthropic | Fast agent | `claude-haiku-4-5` | 200K | Routine, latency-sensitive hosted roles. |
| Google | Fast agentic/coding | `gemini-3.6-flash` | Query provider at runtime | Low-latency hosted work. |
| Google | Sustained agentic/coding | `gemini-3.5-flash` | Query provider at runtime | Balanced Google profile. |
| Google | High-throughput | `gemini-3.5-flash-lite` | Query provider at runtime | Cheap routine roles. |
| Google | Complex reasoning | `gemini-3.1-pro-preview` | Query provider at runtime | Experimental frontier escalation. |
| Mistral | Frontier agentic/coding | Mistral Medium 3.5 | Query provider at runtime | Current Mistral frontier choice. |
| Mistral | Efficient hybrid coding | Mistral Small 4 | Query provider at runtime | Cost-conscious hosted coding. |

Hosted model IDs, capabilities, output caps, context windows, pricing, and
availability must be refreshed from each provider API or model catalog when the
menu is opened or released. A menu selection must store the exact resolved ID,
not an evergreen marketing label.

## Configuration Data and Validation Rules

Every profile should carry this data, whether it is an Ollama download or hosted
provider selection:

| Field | Why the menu needs it |
| --- | --- |
| `kind` (`ollama` or `hosted`) | Chooses download versus credential/provider flow. |
| Provider and exact model ID/tag | Reproducibility and cassette identity. |
| Minimum VRAM and recommended context | Stops the menu offering configurations that cannot work. |
| Context choices | Restrict local Rota profiles to 12K+; show only validated values. |
| Native-tools state | Prevents a tool-incompatible model becoming default. |
| Download command or provider route | Turns catalog data into a configuration action. |
| Temperature, output cap, seed, cache controls | Response-affecting pins that must be persisted with the session. |
| Benchmark/probe date and result | Makes stale catalog entries visible rather than silently trusted. |

Do not auto-download a model merely because its parameter count fits. Before a
new local profile becomes `verified`, run:

```powershell
ollama pull <tag>
$env:ROTA_MODEL = "<tag>"
$env:ROTA_NUM_CTX = "12288"

ollama ps
python -m rota.tools.probe_tools --runs 3
ROTA_L1=1 ROTA_REFRESH=1 python -m pytest tests/rota/test_l1.py -q
```

Promotion checks:

| Check | Required result |
| --- | --- |
| Context fit | Rota records no prompt-window overflow. |
| GPU fit | `ollama ps` reports the chosen profile as `100% GPU`. |
| Native tools | The Rota probe repeatedly returns the legal structured call. |
| Behaviour | L1 transcript/case result is acceptable and failures are classified. |
| Provenance | Save model tag/digest, Ollama version, context, runtime cache settings, and hardware. |

## Current Rota Implementation Boundary

| Capability | Status today |
| --- | --- |
| Direct Ollama model and context selection | Implemented through `ROTA_MODEL` and `ROTA_NUM_CTX`. |
| Onboarding model argument | Implemented: `python -m rota.tools.onboard_run --model <tag>`. |
| Temperature and output cap | Internal only: temperature `0.0`, output cap `2048`. |
| Native Ollama tool schemas | Implemented; validate per model with `probe_tools`. |
| Model download/configuration menu | Planned; this catalog is its starting data. |
| Hosted provider tool use | Planned; LiteLLM exists as a seam but is not yet a complete Rota backend. |
| Provider/cache/output/seed configuration flags | Planned in [the LLM configuration proposal](../plans/rota-llm-configuration-proposal.md). |