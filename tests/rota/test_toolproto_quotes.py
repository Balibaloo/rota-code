"""
A prose argument has to be able to carry code, and code is made of quotes.

`msg.challenge_tester(reason=...)` asks the Developer to quote the test body it
disputes. Test bodies are code. Code contains string literals. So the argument
the brief asks for reliably looks like this:

    reason='"line_total applies the highest band" and "assert
             line_total('SKU-1', 25) == round(price_for('SKU-1') * 25 * 0.9)"'

and `ast.parse` stops at `'SKU-1'`, because the inner quote closes the outer
one. The call became a `ToolError`, the message was never sent, and
`L1-DV-fix-the-code-not-the-test` went green *because the model could not
speak* — a case passing for the accident rather than the reason.

The instruction and the protocol disagreed, and the instruction was the new
one. Hardening the protocol is the fix that leaves the instruction sayable:
outside a quoted value the syntax is Python; inside one, the outermost quote is
the delimiter and everything up to its partner is literal, however many quotes
are in between.

Strict parsing is still tried first. This is a fallback, so nothing that parsed
before parses differently now.
"""
from __future__ import annotations

import pytest

from rota.llm import toolproto


REAL = (
    "TOOL: msg.challenge_tester(refs=[\"tst_6719e7\", \"c_d1f8db\"], "
    "reason='\"line_total applies the highest band the quantity qualifies for\" "
    "and \"assert line_total('SKU-1', 25) == round(price_for('SKU-1') * 25 * 0.9)\"')"
)


def test_the_call_that_could_not_be_spoken(  ):
    """
    The exact completion out of the cassette, which parsed to a `ToolError` and
    silently turned a red case green.
    """
    got = toolproto.extract(REAL)

    assert len(got) == 1, got
    call = got[0]
    assert not isinstance(call, toolproto.ToolError), call
    assert call.name == "msg.challenge_tester"
    assert call.args["refs"] == ["tst_6719e7", "c_d1f8db"]
    assert "SKU-1" in call.args["reason"]
    assert "line_total applies the highest band" in call.args["reason"]


@pytest.mark.parametrize("raw, key, want", [
    # The outermost quote is the delimiter; inner ones are content.
    ("""f(reason='he said "no" twice')""", "reason", 'he said "no" twice'),
    ("""f(reason="it's fine")""", "reason", "it's fine"),
    ("""f(reason='a['b'] == c')""", "reason", "a['b'] == c"),
    # And the value still ends where the next argument begins.
    ("""f(reason='x's and y's', n=2)""", "reason", "x's and y's"),
])
def test_a_quoted_value_ends_at_its_partner_not_at_the_first_inner_quote(
        raw, key, want):
    args, _ = toolproto.parse_args(raw[raw.index("(") + 1:raw.rindex(")")])
    assert args[key] == want


def test_the_other_arguments_still_parse_as_themselves(  ):
    """
    The fallback must not turn everything into strings. `refs` is a list and
    `round_no` is an integer, and a recipient resolving `"0"` as a round is a
    different bug wearing this one's clothes.
    """
    args, _ = toolproto.parse_args(
        "refs=[\"a\", \"b\"], reason='it's complicated', round_no=3")

    assert args["refs"] == ["a", "b"]
    assert args["round_no"] == 3
    assert isinstance(args["round_no"], int)


def test_strict_parsing_is_tried_first_and_unchanged(  ):
    """
    A fallback that changes what already worked is a rewrite. Everything
    well-formed must parse exactly as it did, including the escapes the strict
    path understands.
    """
    args, pos = toolproto.parse_args(
        "path='src/a.py', body='line one\nline two', keep=True, n=None")

    assert args == {"path": "src/a.py", "body": "line one\nline two",
                    "keep": True, "n": None}
    assert pos == ()


def test_something_genuinely_malformed_is_still_an_error(  ):
    """
    The point is to accept prose containing quotes, not to accept anything. A
    parser that never refuses cannot report a misparse, and a misparse that
    travels is the failure this protocol exists to prevent.
    """
    got = toolproto.extract("TOOL: msg.challenge_tester(refs=[unclosed, 'x'")

    assert any(isinstance(g, toolproto.ToolError) for g in got), got

def test_a_namespace_label_is_the_call_it_names():
    """`MODEL: amend(...)`: the namespace as the marker (the survey spike,
    2026-09-15, qwen3:8b, every call in prose). Read as model.amend when the
    session has that function; `NOTE: x(` with no such function stays prose."""
    from rota.llm import toolproto
    sigs = {"model.amend": None, "model.describe": None}
    calls = toolproto.extract("MODEL: describe(account='x')\n" + "MODEL: amend(headline='h', text='t')\n" + "NOTE: nothing(here)", sigs)
    names = [c.name for c in calls if hasattr(c, "name")]
    assert names == ["model.describe", "model.amend"], calls

def test_an_argument_list_the_first_scan_cannot_close_is_read_again():
    """
    Night 72 (2026-09-15): the Developer's challenge carried a test's source
    in a quoted argument and died as unterminated three sessions running.
    The scanner counts quotes by parity, and a lone quote inside triple
    quotes, the very form the refusal recommends, breaks it. A second scan
    reads triple quotes as one token; its answer stands only when the
    arguments parse."""
    raw1 = "TOOL: msg.challenge_tester(refs=['c1', 't1'], quotes=['''it's a test''', 'def f():'], round_no=0)"
    got = toolproto.extract(raw1)
    assert len(got) == 1 and not isinstance(got[0], toolproto.ToolError), got
    assert got[0].args["refs"] == ["c1", "t1"] and got[0].args["round_no"] == 0
    raw2 = "TOOL: tests.encode(id='t', criterion_id='c1', path='tests/test_x.py', body='''x = 'y'\ndef test_x():\n    assert x\n''')"
    got = toolproto.extract(raw2)
    assert len(got) == 1 and not isinstance(got[0], toolproto.ToolError), got
    assert "def test_x" in got[0].args["body"]
