"""
A line break inside a triple-quoted value stays a line break (frame 151).

`_escape_newlines_in_quotes` turns each line break inside a quoted value into
`\\n` and each line break between arguments into a space. Its scan counted each
quote character alone. So after an odd count of the delimiter's own character
inside a `'''` or `\"\"\"` value, the scan stood outside the value and read the
next line break as a space. `ledger.log(note='''a'\\nb''')` read `"a' b"`.
Python reads the source as written, so the source is not ambiguous.

On nights 113 to 124, 12 of 1,719 `code.write` and `tests.encode` calls lost
line breaks in this way. `fixtures/toolproto_triple_nights.json` holds the
smallest faithful cut of each call: the call's head and tail as the seat wrote
them, and the first lines of the value up to the first joined line break.
"""
from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from rota.llm import toolproto
from rota.roles import api

NIGHTS = Path(__file__).parent / "fixtures" / "toolproto_triple_nights.json"
LEDGER = {"ledger.log": ({"note"}, {"note"})}


def _read(raw: str, sig: dict) -> list:
    return [(c.name, c.args) if hasattr(c, "args") else ("refused", c.reason)
            for c in toolproto.extract(raw, sig)]


# Only the delimiter's own character broke the scan. A lone `"` inside `'''`
# and an escaped quote read right before the repair, so they are not here.
@pytest.mark.parametrize("delim, value", [
    ("'''", "a'\nb"),           # the smallest input of the brief
    ('"""', 'a"\nb'),
    ("'''", "'\nb"),            # the lone quote opens the value
    ('"""', '"\nb'),
    ("'''", "a'\nb\nc"),        # every later line break too
    ("'''", "a'b'c'\nd"),       # three lone quotes
    ("'''", "x = 'y\nz"),       # an open string literal in code
])
def test_a_line_break_after_a_lone_quote_in_a_triple_quoted_value_stays(delim, value):
    raw = "TOOL: ledger.log(note=" + delim + value + delim + ")"
    want = eval(delim + value + delim)          # Python's read is the oracle
    assert _read(raw, LEDGER) == [("ledger.log", {"note": want})]


def test_a_value_that_opens_with_four_quotes_keeps_its_line_breaks():
    """Night 115 s131 opened its body with `''''`: the triple quote, then a
    quote that belongs to the value."""
    raw = "TOOL: ledger.log(note=''''a\nb\nc''')"
    assert _read(raw, LEDGER) == [("ledger.log", {"note": "'a\nb\nc"})]


def test_a_line_break_between_arguments_is_still_a_space():
    """The repair moves no line break outside a value. A call written one
    argument per line reads as before."""
    raw = "TOOL: ledger.log(\n    note='''it's\nok''',\n)"
    assert _read(raw, LEDGER) == [("ledger.log", {"note": "it's\nok"})]


def _registry_sig() -> dict:
    """The signatures as the runner's `_param_sets` builds them."""
    out = {}
    for (art, verb), fn in api.REGISTRY.items():
        ps = {k: v for k, v in inspect.signature(fn).parameters.items() if k != "ctx"}
        req = {k for k, v in ps.items() if v.default is inspect.Parameter.empty}
        out[f"{art}.{verb}"] = (req, set(ps))
    return out


_CUTS = json.loads(NIGHTS.read_text(encoding="utf-8"))


@pytest.mark.parametrize("cut", _CUTS, ids=[
    "-".join(f"n{n}{s}q{q}" for n, s, q in c["calls"][:1]) + f"x{len(c['calls'])}"
    for c in _CUTS])
def test_each_night_call_keeps_every_line_break(cut):
    """The fixture's `args` are Python's read of the cut. The runner's path,
    `extract_lenient` with the registry's signatures, reads the same."""
    sig = _registry_sig()
    calls, _, _ = toolproto.extract_lenient(cut["raw"], set(sig), signatures=sig,
                                            with_offsets=True)
    got = [(c.name, c.args) if hasattr(c, "args") else ("refused", c.reason)
           for c in calls]
    assert got == [(cut["op"], cut["args"])]


def test_the_fixture_holds_the_twelve_night_calls():
    calls = [tuple(c) for cut in _CUTS for c in cut["calls"]]
    assert len(calls) == len(set(calls)) == 12
    assert {c[0] for c in calls} == {115, 117, 118, 120}
