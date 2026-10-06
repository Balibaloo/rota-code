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
    """The repair moves no line break outside a value. Python accepts a line
    break between arguments, so a read cannot see the space. The test reads
    the escape's own output (the review of e78545a, finding 3)."""
    text = "\n    note='''it's\nok''',\n    b=1\n"
    want = " " + "    note='''it's\\nok''',     b=1 "
    assert toolproto._escape_newlines_in_quotes(text) == want


def test_a_carriage_return_reads_as_a_line_break():
    """A CRLF or a lone CR inside a value is one line break, and outside a
    value it is one space."""
    text = "note='''it's\r\nok\rnow''',\r\nb=1"
    want = "note='''it's\\nok\\nnow''', b=1"
    assert toolproto._escape_newlines_in_quotes(text) == want


def test_an_escaped_quote_does_not_close_a_triple_quoted_value():
    """`\\'''` inside a `'''` value is a quote and two more, as Python reads
    it. The value goes on, so the next line break is inside it."""
    text = "note='''x\\'''\ny'''"
    want = "note='''x\\'''\\ny'''"
    assert toolproto._escape_newlines_in_quotes(text) == want


def test_the_second_scan_honours_a_backslash_in_a_triple_quoted_value():
    """`_rescan_args` skipped an escape only in a one-character quote, so
    `\\'''` closed the value early and the list never closed (the review of
    e78545a, finding 2). Python reads `\\'` as a quote."""
    raw = "TOOL: ledger.log(note='''can't \\''' x''')"
    assert _read(raw, LEDGER) == [("ledger.log", {"note": "can't ''' x"})]


_GUARD = "a quote inside a value closed it early"
_TF = {"t.f": ({"a"}, {"a", "b", "c", "result", "note"})}


def _read_lenient(raw: str, sig: dict) -> list:
    calls, _, _ = toolproto.extract_lenient(raw, set(sig), signatures=sig,
                                            with_offsets=True)
    return [(c.name, c.args) if hasattr(c, "args") else ("refused", c.reason)
            for c in calls]


@pytest.mark.parametrize("q", ["'''", '"""'])
def test_a_stray_triple_quote_after_a_closed_value_is_refused(q):
    """A stray triple quote on its own line after a closed value, with the
    quote's own character in two values. Python refuses the text. Pass 1
    read a call with a wrong value, `a="it's, c=s\\\\nt"`: the escaped list
    parses, because Python joins the stray string `, c=` and a raw string
    `r's\\nt'` to `a` (the review of e78545a, finding 1). Frame 122's rule:
    a wrong write is worse than a refusal. The seat reads the guard's own
    reason, and not a hint about a value that never ends (the review of
    9cb2bcbc, finding 3)."""
    ch = q[0]
    raw = ("TOOL: t.f(a=" + q + "it" + ch + "s" + q + "\n" + q + ", c=" + q
           + "r" + ch + "s\nt" + q + ")")
    got = _read_lenient(raw, _TF)
    assert len(got) == 1 and got[0][0] == "refused", got
    assert _GUARD in got[0][1]
    with pytest.raises(toolproto.JoinedStrings):
        toolproto.parse_args(raw[len("TOOL: t.f("):-1])


# The guard counted triple quotes before the review of 9cb2bcbc. A count
# also counts a triple quote inside a value of the other kind. Then a line
# break in a one-quoted value, or a bare `pass`, made Python refuse the raw
# list, and the guard refused a right read (finding 1). A Critic's `quote=`
# with one `\"\"\"` and a line break is the live shape.
@pytest.mark.parametrize("args, want", [
    ("a=\"x ''' y\nz\"", {"a": "x ''' y\nz"}),
    ("a='x \"\"\" y\nz'", {"a": 'x """ y\nz'}),
    ("result=pass, note=\"x ''' y\"", {"result": "pass", "note": "x ''' y"}),
    ("a=\"x ''' y\r\nz\"", {"a": "x ''' y\nz"}),
    ("a='''x \"\"\" y''', b='p\nq'", {"a": 'x """ y', "b": "p\nq"}),
    ("a='''x \"\"\" y''', result=pass", {"a": 'x """ y', "result": "pass"}),
])
def test_a_triple_quote_inside_a_value_of_the_other_kind_still_reads(args, want):
    assert _read_lenient("TOOL: t.f(" + args + ")", _TF) == [("t.f", want)]


def test_two_strings_side_by_side_keep_their_read_when_python_reads_the_list():
    """The guard refuses only when Python refuses the list as written. Four
    cassette calls of `criteria.specify` write `hint=''` inside a value, and
    Python joins the two literals. The read stays Python's read."""
    raw = "TOOL: t.f(a='code.surface(hint='')')"
    assert _read_lenient(raw, _TF) == [("t.f", {"a": "code.surface(hint=)"})]


def test_the_lenient_read_keeps_frame_122s_prose_with_apostrophes():
    """The guard stands on the strict path only. Before the lenient fall it
    would refuse this case, because its escaped text holds two string
    literals side by side (the fuzz slice, prose-2-1000-plain #522)."""
    raw = "TOOL: code.commit(message='order(I'm can't,' ': that 'yes', it a.')"
    sig = {"code.commit": ({"message"}, {"message"})}
    assert _read_lenient(raw, sig) == [
        ("code.commit", {"message": "order(I'm can't,' ': that 'yes', it a."})]


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
