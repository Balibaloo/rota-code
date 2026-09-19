# Frame 43's probes

Rota workflow. The scripts the frame 43 agents wrote to measure the context
length management system, kept because their conclusions are in
`plans/archive/context-caps-design-2026-09-18.md` and a conclusion without its
probe cannot be re-run.

An agent writes a probe into its own scratchpad, which is deleted with the
session. These were copied out on 2026-09-19 (observed: session 4286e076 had
already found the frame's 536k scope report dead in a closed session's temp
directory).

Run them from the repository root. They are read-only. They import rota, so
they need the virtual environment.

| script | what it measures | which finding |
| --- | --- | --- |
| `p_fit.py`, `p_fit2.py`, `p_fit3.py` | 120000 random transcripts through `_fit`, at 1 to 11 blocks and six budgets. Asserts the wake appears once, the dropped count stays positive, and the total stays inside the budget. | the diff review's F5, the 116-character overrun from `_fit`'s own notice |
| `p_room.py` | the `result_room` and `cap` expressions, copied from the runner. Prints the wake-plus-reply threshold for a whole source read. | F2, a source read cut to 5191 characters |
| `p_stub.py` | four turns of a four-call batch through the repeat memory and the per-turn cap. | F1, a withheld result remembered as an answer |
| `p_lines.py` | the repeat refusal against the line it replaces, at `_call_tag` width, times s71's 331 calls. | F4, the own-goal |
| `p_spans.py`, `p_spans2.py` | every symbol of four real files against Python's `ast`. 77 of 77 matched. | the spans, verified for Python only |
| `p_index.py` | a pre-change database through the new `init_db`, then the probe's render size. | the migration, and the probe at 4415 characters |
| `p_modes.py`, `p_modes2.py`, `p_md.py` | every `.tools` file against the graph's grants, and the 11 brief lines compared for identity. | repair 1's 11 modes |
| `measure_turn.py` | the arithmetic behind `TURN_RESULT_CHARS`. | repair 3's number |
| `p_window.py` | a model's size, its VRAM and its spill at a window, from `/api/ps` after a one-token generate. | ends-when line 1, the evidence that 16384 does not spill |
| `p_night.py` | the four context numbers of a night, from the night's database. Reproduces night 86's 297 of 825, 86, 15 and 179117 exactly. | the frame's ends-when, which compares a night against night 86 |

The window measurement, taken on 2026-09-19 12:55 by session 9a9a20bf on the
3080 at one slot, idle, with nothing else loaded:

| model | window asked | window allocated | size | spill |
| --- | ---: | ---: | ---: | ---: |
| qwen3:8b, the night's default | 16384 | 16384 | 6.89 GB | 0.00 GB |
| qwen3.5:9b, the four judging desks | 16384 | 16384 | 5.50 GB | 0.00 GB |

Three facts from that run. Neither of the night's models spills at 16384. The
second model evicts the first, so the two never sum on this card. Both numbers
are below section 8's table, 6.89 against 7.40 and 5.50 against 5.91, so the
recommended window has more headroom than the design record claimed.

## The baseline of night 86, corrected

`p_night.py` reproduces all four recorded numbers of night 86. It also finds
four faults in them, and two change how a later night is read (observed:
session 9a9a20bf verified the first fault with its own query).

1. **One of the 15 cut sessions was not cut.** s168 reports `used = 12261` and
   `estimate = 12111` against a 12288 window, so the prompt fit. It fired the
   `used >= num_ctx * 0.98` clause at `rota/llm/llm.py:416`, not the overflow
   clause. Its term in the discarded sum is minus 150 tokens. The true figures
   are 14 cuts and 179267 tokens.
2. **So "zero sessions cut" needs both numbers.** Report the note count and
   the count of turns whose estimate exceeds the window. A prompt at 98 per
   cent of the window reads as a cut and is not one. At 16384 that clause
   fires at 16056.
3. **Number 4 has no baseline before night 86.** Night 85's notes carry an
   earlier format with no estimate, so the discarded tokens cannot be summed
   there.
4. **Number 2 compares by text, not by mechanism.** Night 85's two notices sit
   at an offset its own budget explains and the current formula does not.

The count is a floor by design. A session that fails later loses its note
(`rota/core/runner.py:2826`). No cut was lost on either night, and the probe
prints the reconstruction beside the note count so a later night cannot hide
one.

## What the window rise can and cannot buy

The frame's ends-when asks for zero sessions cut by the server. **The window
rise alone cannot deliver it** (observed: session 9a9a20bf, the prompt
estimates in night 86's own 15 notes).

Twelve of the fifteen noted prompts are above 16384 tokens. The rise from
12288 to 16384 clears two of the fourteen real cuts, s24 at 14511 tokens and
s142 at 13967. The largest is s71 at 27155 tokens, then s17 at 26007, and ten
more between 17556 and 19883.

So a night that shows zero cuts shows the four repairs working, not the
window. The window is headroom. This is the prediction to hold the night
against, and it names the sessions to read first if the night still shows a
cut.

The three largest prompts are the sessions the repairs were written from. s71
is cited in repair 2's commit message and in repair 3's comment. s10, at 19216
tokens, is the `vision_keeper/reconcile` session that repair 1 exists for.

Two limits, stated where the record states them. The spans are verified against
Python only, so the other grammars in `languages.LANGUAGES` are unexercised. The
`_fit` fuzz uses random text, not real transcripts, so it bounds the shape and
not the content.
