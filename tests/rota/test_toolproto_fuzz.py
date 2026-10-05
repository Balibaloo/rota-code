"""
The gate's slice of frame 122's parser fuzz (frame 144, item 2).

`probes/frame122/fuzz.py` writes calls with random values and knows the
arguments of each. The full fuzz runs outside the gate. This test runs a
fixed-seed slice of it, about 9300 calls in a few seconds, with no model.

`fixtures/toolproto_fuzz_slice.json` holds, for each case, a digest of all
that the parser reads: each call with its arguments, each refusal sentence,
and each start offset. A case whose digest moves is red, unless it now
reads right and did not before. Right is the exact list of calls that the
case wrote. After a parser change that the fuzz judged,
`python -m probes.frame122.fuzz record` writes the file again and prints
what moved.

The slices reach these landed fixes of the parser, each proved by its
removal (frame 144, pass 4): fb1bdba's third reading, 65ca902's hash in a
bare id, 2b07533's unquoted path, cf0aecb's `MODEL:` label, b79882e's
offset of a call that the source does not hold, and the second reading of
dc34dcd with 3b92f9e. b79882e's other half, the carried write line, is in
`rota/tools/nightcount.py` and not in the parser, so no generator reaches
it.
"""
from __future__ import annotations

import json
from itertools import islice

from probes.frame122 import fuzz
from rota.llm import toolproto


def _case(key: str, i: int):
    s = next(s for s in fuzz.SLICES if fuzz.slice_key(*s) == key)
    cases, sig = fuzz.slice_cases(*s)
    case = next(islice(cases, i, None))
    return case, toolproto.extract(case.raw, sig)


def test_the_parser_keeps_its_reads_on_the_fuzz_slice():
    want = json.loads(fuzz.SLICE_FILE.read_text(encoding="utf-8"))
    now = fuzz.slice_outcomes(toolproto)
    assert set(now) == set(want), "the slices changed: run the record command"
    moved = fuzz.slice_changes(want, now)
    shown = []
    for key, i, what in moved[:4]:
        case, got = _case(key, i)
        shown.append(f"{what}: {key} #{i} {case.raw!r} -> {got}")
    assert not moved, f"{len(moved)} cases moved:\n" + "\n".join(shown)


def test_a_moved_raw_text_moves_the_slice():
    """The runner writes `call.raw` into a seat's `ERROR` line
    (`runner.py`, the two `feedback.append` of an error), so the raw text
    is part of the prompt. A parser that keeps every call and every
    sentence and moves only `raw` must turn the slice red (the review of
    ee17f70, low 1)."""
    import dataclasses
    import types

    def moved(text, sig=None, **kw):
        return [dataclasses.replace(c, raw="another text " + c.raw)
                for c in toolproto.extract(text, sig, **kw)]

    want = json.loads(fuzz.SLICE_FILE.read_text(encoding="utf-8"))
    now = fuzz.slice_outcomes(types.SimpleNamespace(extract=moved))
    assert fuzz.slice_changes(want, now)


def test_the_slice_holds_frame_122s_prose_with_apostrophes():
    """Frame 122 read a quote with apostrophes, such as claim's, as text
    (fb1bdba). The slice holds such cases, so a lost reading turns it red."""
    want = json.loads(fuzz.SLICE_FILE.read_text(encoding="utf-8"))
    key = fuzz.slice_key("prose", 1, 2500, True)
    case, got = _case(key, want[key]["right"][0])
    assert "'s" in case.raw or "n't" in case.raw or "I'm" in case.raw, case.raw
    assert [(c.name, c.args) for c in got] == [(case.fn, case.want)]
