"""
The gate's slice of frame 122's parser fuzz (frame 144, item 2).

`probes/frame122/fuzz.py` writes calls with random values and knows the
arguments of each. The full fuzz runs outside the gate. This test runs a
fixed-seed slice of it, about 7500 calls in about a second, with no model.

`fixtures/toolproto_fuzz_slice.json` holds the slice's outcomes: the cases
that the parser reads right, and the cases that it reads wrong. A case that
reads right must stay right. A case may read wrong only when the file names
it. A refused case may become right. After a parser change that the fuzz
judged, `python -m probes.frame122.fuzz record` writes the file again.
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
    return case, fuzz.read(toolproto, case, sig)


def test_the_parser_keeps_its_reads_on_the_fuzz_slice():
    want = json.loads(fuzz.SLICE_FILE.read_text(encoding="utf-8"))
    now = fuzz.slice_outcomes(toolproto)
    assert set(now) == set(want), "the slices changed: run the record command"
    lost, wrong = [], []
    for key, got in now.items():
        lost += [(key, i) for i in sorted(set(want[key]["right"]) - set(got["right"]))]
        wrong += [(key, i) for i in sorted(set(got["wrong"]) - set(want[key]["wrong"]))]
    shown = []
    for what, cases in (("no longer read right", lost), ("read wrong", wrong)):
        for key, i in cases[:3]:
            case, calls = _case(key, i)
            shown.append(f"{what}: {key} #{i} {case.raw!r} -> {calls}")
    assert not lost and not wrong, (
        f"{len(lost)} cases no longer read right, {len(wrong)} cases read wrong:\n"
        + "\n".join(shown))


def test_the_slice_holds_frame_122s_prose_with_apostrophes():
    """Frame 122 read a quote with apostrophes, such as claim's, as text
    (fb1bdba). The slice holds such cases, so a lost reading turns it red."""
    want = json.loads(fuzz.SLICE_FILE.read_text(encoding="utf-8"))
    key = fuzz.slice_key("prose", 1, 2500, True)
    case, calls = _case(key, want[key]["right"][0])
    assert "'s" in case.raw or "n't" in case.raw or "I'm" in case.raw, case.raw
    assert calls == [(case.fn, case.want)]
