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

Two limits, stated where the record states them. The spans are verified against
Python only, so the other grammars in `languages.LANGUAGES` are unexercised. The
`_fit` fuzz uses random text, not real transcripts, so it bounds the shape and
not the content.
