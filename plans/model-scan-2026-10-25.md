# Model scan, 2026-10-25

For Roman, 2026-10-25 00:56. Scope: open-weight 4B to 15B models of 2026 under ollama.

## Result

1. Short list, in order: `granite4.2:8b`, then `gemma4:12b-it-qat`, then
   `bonsai-2:9b`. Compare each on one measure: the recorded cases pass
   rate per role against `qwen3.5:9b` and `qwen3:8b` on the same card.
2. The newest Qwen in the size range is still Qwen3.5-9B of 2026-03-02.
   Qwen3.6 and Qwen3.8 ship at 27B and 35B only.
3. Only `bonsai-2:9b` fits beside `qwen3:8b` inside the 12.5 GB that the
   two resident models take today. `granite4.2:8b` fits beside
   `qwen3.5:9b` at the margin. `gemma4:12b` fits alone or not at all.
4. Top risk: ollama's Gemma 4 renderer has an open bug that drops tool
   parameters named `type`, `description`, `properties`, `required` or
   `nullable`. Rota's tool schemas carry none of these names, so the bug
   does not bite today (reasoned: `rota/llm/toolschema.py` builds the
   schema from function signatures, and no sandbox tool has such a
   parameter).

Caution on the budget: the 3080 has 10 GB and a practical 8 GB (observed:
`plans/operating-facts.md`, lines 60 and 97). Two models at 12.5 GB do
not both sit in VRAM. The fit table ranks by file size plus a cache
estimate at 16k, and does not promise residence.

## Question 1: candidates better than Qwen3 8B or Qwen3.5 9B

Qwen3.5-9B is the bar. Its card claims IFEval 91.5, BFCL-V4 66.1,
TAU2-Bench 79.1, LiveCodeBench v6 65.6, context 262,144, Apache 2.0
(observed: https://huggingface.co/Qwen/Qwen3.5-9B).

**Gemma 4 12B Unified.** Google, June 2026. 11.95B dense, 256K context,
Apache 2.0. Card: LiveCodeBench v6 72.0, Tau2 average 69.0, MMLU Pro
77.2, Codeforces 1659. The card gives no IFEval and no BFCL (observed:
https://huggingface.co/google/gemma-4-12b-it). Ollama tags:
`gemma4:12b-it-q4_K_M` 8.0 GB, `gemma4:12b-it-qat` 7.2 GB (observed:
https://ollama.com/library/gemma4/tags). Beats Qwen3.5-9B on code. The
two Tau2 figures average different sub-sets (reasoned: Google names three
domains, Qwen names one score).

**Granite 4.2 8B.** IBM, 2026-08-25. 8B dense, 128K context, Apache 2.0.
Card: LiveCodeBench v6 73.24, SWE-bench Verified 47.67, BFCL v4 52.39,
tau3-bench 58.06, IFBench prompt 79.33. Thinking is on by default and
`enable_thinking=False` turns it off (observed:
https://huggingface.co/ibm-granite/granite-4.2-8b). Ollama: `granite4.2:8b`
5.3 GB, Q4_K_M (observed: https://ollama.com/library/granite4.2). Beats
Qwen3.5-9B on code, trails on BFCL v4 by 14 points. The two IFBench
figures use different scoring, so instruction following is open.

**Bonsai 2 9B.** Prism ML, 2026-10-15. A ternary build of Qwen3.5-9B,
262,144 context, Apache 2.0, 3.2 GB on ollama with tools and thinking
(observed: https://ollama.com/library/bonsai-2 and
https://huggingface.co/prism-ml/Ternary-Bonsai-2-9B-gguf). Neither page
gives one benchmark number. It is a size candidate, not a quality one.

**Nemotron 3.5 Bolt E4B.** NVIDIA, 2026-10-23. Post-trained from Gemma 4
E4B, 8B total and 4B effective, 128K context, OpenMDW 1.1, 7.2 to 7.9 GB
(observed: https://ollama.com/library/nemotron-3.5-bolt). No card and no
benchmark was found on 2026-10-25. Too new to rank.

Scanned and excluded: Gemma 4 E4B, April 2026, LiveCodeBench 52.0 and
Tau2 42.2, below the bar (observed: https://ollama.com/library/gemma4).
Ministral 3, released 2025-12-02. MiniCPM5, 1B and 2B only. Mistral
Small 4, 119B. GLM-4.7-Flash, 30B-A3B. `nimble-v3`, `tev1`, `d3` and
`clef-flash` are decision models without chat or tool calling (observed:
https://ollama.com/library/nimble-v3). No Phi-5, Olmo 3.5 or Llama 5 was
found in the range.

## Question 2: newer Qwen than Qwen3.5

No. No Qwen3.6 or Qwen3.8 repo is under 20B (observed:
https://huggingface.co/Qwen). Ollama's `qwen3.6` has 35 tags, all 27B or
35B-A3B, 17 GB and up (observed: https://ollama.com/library/qwen3.6/tags).
`qwen3.8` is 27B at 18 GB (observed: https://ollama.com/library/qwen3.8).
The `qwen3.5:9b` tags were re-pushed two to three weeks ago with `-mtp`
and `-nvfp4` variants and no new weights (observed:
https://ollama.com/library/qwen3.5/tags).

## Question 3: fit on the card, 16k context

Today: `qwen3:8b` 6.9 GB and `qwen3.5:9b` 5.5 GB resident, 12.4 GB
together (observed: the caller's figures). Estimates below are file size
plus a KV cache at 16k in f16 (reasoned: ollama's default cache type).

| Pair | Estimate | Fits 12.5 GB |
|---|---|---|
| `qwen3:8b` + `bonsai-2:9b` (3.2 + about 1.3 cache) | 11.4 GB | yes |
| `qwen3.5:9b` + `granite4.2:8b` (5.3 + about 2.6 cache) | 13.4 GB | at the margin |
| `qwen3:8b` + `granite4.2:8b` | 14.8 GB | no |
| `qwen3.5:9b` + `gemma4:12b-it-qat` (7.2 + about 2 cache) | 14.7 GB | no |
| `gemma4:12b-it-qat` alone | 9.2 GB | alone only |
| `qwen3.5:9b` + `nemotron-3.5-bolt:e4b` (7.5 + cache) | 14.5 GB | no |

Granite's cache: 40 layers, 8 KV heads, head size 128, 160 KB a token
(reasoned: architecture figures from secondary coverage). Bonsai 2 keeps
Qwen3.5's hybrid attention and its small cache (reasoned: same
architecture as the base, per the gguf card). Gemma 4 12B is a guess.

## Question 4: risk, one sentence each

- Gemma 4 12B: ollama issue 18468 is open at 0.40.0, and Gemma 4's native
  call format uses unquoted keys, so a quote fault at the parser is live
  (observed: https://github.com/ollama/ollama/issues/18468).
- Granite 4.2 8B: thinking is on by default and every number is IBM's
  own, so rota must send the think flag off and re-measure.
- Bonsai 2 9B: no published number, and lower precision widens the spread
  on close word senses (reasoned: that is rota's wrong-sense fault).
- Nemotron Bolt E4B: no card, no benchmark, and OpenMDW is not Apache.

## Question 5: recommendation

1. `granite4.2:8b` on the Critic, Developer and Tester desks. Smallest
   file of the three, Apache 2.0, code above the bar.
2. `gemma4:12b-it-qat` on the Critic desk alone. The 2026-09-12 lever was
   gemma3:12b on that desk (observed: `plans/operating-facts.md`, line 111).
3. `bonsai-2:9b` in place of `qwen3.5:9b` only if it holds the pass rate.

One measure: the recorded cases pass rate per role, re-recorded on the
same card and ollama version, against the `qwen3.5:9b` baseline.
