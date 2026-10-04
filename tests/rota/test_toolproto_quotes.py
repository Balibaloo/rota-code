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


# Night 105, `.rota/clickI_night105.db`, session s141: the `quotes=` value of
# turns 4 and 5, byte for byte. The `\n` and `\"` are text, as the seat wrote.
NIGHT105_BODY = r"""Criterion echo_json_compact_3: The callable `echo_json` must handle non-serializable objects by raising a `TypeError` consistent with the behavior of standard library JSON serialization, rather than silently failing or printing a fallback.\n\nTest inh_echo_json_03 body: def test_echo_json_non_serializable():\n    from click.testing import CliRunner\n    from src.click.utils import echo_json\n    \n    runner = CliRunner()\n    # Pass a non-serializable object (e.g., a custom class instance without __dict__ or __repr__ that JSON can't handle)\n    class BadObj:\n        def __init__(self):\n            self.value = \"test\"\n    \n    result = runner.invoke(echo_json, [str(BadObj())], catch_exceptions=False)\n    # It should raise TypeError because json.dumps cannot serialize it\n    assert result.exit_code != 0\n    assert 'TypeError' in result.output"""

NIGHT105_HEAD = "TOOL: msg.challenge_tester(refs=['echo_json_compact_3', 'inh_echo_json_03'], "


def test_a_triple_quoted_value_the_first_scan_closes_early_is_read_again():
    """
    Frame 109, night 105, s141 turn 5 with the stray outer `"` removed. The
    first scan reads `can't` as an opening quote and closes the list at the
    `)` after it. The arguments up to there do not parse, so the rescan runs
    and reads `'''` as one token.
    """
    raw = NIGHT105_HEAD + "quotes='''" + NIGHT105_BODY + "''', round_no=0)"
    got = toolproto.extract(raw)
    assert len(got) == 1 and isinstance(got[0], toolproto.ToolCall), got
    assert got[0].args["refs"] == ["echo_json_compact_3", "inh_echo_json_03"]
    assert "can't handle" in got[0].args["quotes"]
    assert got[0].args["quotes"].endswith("'TypeError' in result.output")
    assert got[0].args["round_no"] == 0


def test_a_stray_quote_after_the_value_is_still_the_same_door():
    """
    Night 105, s141 turn 4 as written: the seat opened a second string at
    `", "round_no=0)`. No parser can tell that quote from a real one, so the
    refusal and its hint stay, byte for byte (frame 109's review: 217
    cassette prompts carry the door text).
    """
    raw = NIGHT105_HEAD + 'quotes="' + NIGHT105_BODY + '", "round_no=0)'
    got = toolproto.extract(raw)
    assert len(got) == 1 and isinstance(got[0], toolproto.ToolError), got
    assert got[0].raw == "TOOL: msg.challenge_tester(..."
    assert got[0].reason == (
        "unterminated argument list: a quote inside a quoted argument "
        "ended the string early, or a bracket is unbalanced. Source "
        "has quotes of its own: put it between triple quotes, "
        "text='''...''', with the lines as they are, no escaping")


# Night 115, `.rota/clickI_night115.db`, Critic s86: the call of turns 1
# to 4, byte for byte. Turns 5 and 6 repeat turn 4. Each `\n`, `\"` and
# `\'` is text, as the seat wrote it.
S86_T1 = r"""TOOL: challenge.uphold(citation='examples/validation/validation.py', quote='def validate_count(ctx, param, value):\n    if value < 0 or value % 2 != 0:\n        raise click.BadParameter("Should be a positive, even integer.")\n    return value', why='The claim cites `click.ParamType` as the mechanism for validation in this file. The code explicitly implements a custom class `URL(click.ParamType[urlparse.ParseResult])` which inherits from `click.ParamType`. This confirms that `click.ParamType` is indeed used and instantiated (via `type=URL()`) to handle parameter conversion and validation logic, supporting the claim's reference to it.')"""
S86_T2 = r"""TOOL: challenge.uphold(citation='examples/validation/validation.py', quote="'''def validate_count(ctx, param, value):\n    if value < 0 or value % 2 != 0:\n        raise click.BadParameter(\"Should be a positive, even integer.\")\n    return value'''\", why='The claim cites `click.ParamType` as the mechanism for validation in this file. The code explicitly implements a custom class `URL(click.ParamType[urlparse.ParseResult])` which inherits from `click.ParamType`. This confirms that `click.ParamType` is indeed used and instantiated (via `type=URL()`) to handle parameter conversion and validation logic, supporting the claim\'s reference to it.')"""
S86_T3 = r"""TOOL: challenge.uphold(citation='examples/validation/validation.py', quote="'''def validate_count(ctx, param, value):
    if value < 0 or value % 2 != 0:
        raise click.BadParameter(\"Should be a positive, even integer.\")
    return value'''\", why='The claim cites `click.ParamType` as the mechanism for validation in this file. The code explicitly implements a custom class `URL(click.ParamType[urlparse.ParseResult])` which inherits from `click.ParamType`. This confirms that `click.ParamType` is indeed used and instantiated (via `type=URL()`) to handle parameter conversion and validation logic, supporting the claim\'s reference to it.')"""
S86_T4 = r"""TOOL: challenge.uphold(citation='examples/validation/validation.py', quote="'''def validate_count(ctx, param, value):
    if value < 0 or value % 2 != 0:
        raise click.BadParameter(\"Should be a positive, even integer.\")
    return value'''\", why='The claim cites `click.ParamType` as the mechanism for validation in this file. The code explicitly implements a custom class `URL(click.ParamType[urlparse.ParseResult])` which inherits from `click.ParamType`. This confirms that `click.ParamType` is indeed used and instantiated (via `type=URL()`) to handle parameter conversion and validation logic, supporting the claim\'s reference to it.')")"""

S86_QUOTE = (
    'def validate_count(ctx, param, value):\n'
    '    if value < 0 or value % 2 != 0:\n'
    '        raise click.BadParameter("Should be a positive, even integer.")\n'
    '    return value')
UPHOLD = {"challenge.uphold": ({"citation", "quote"}, {"citation", "quote", "why"})}


@pytest.mark.parametrize("raw", [S86_T1, S86_T2, S86_T3, S86_T4],
                         ids=["t1-apostrophe", "t2-wrapped-triple",
                              "t3-wrapped-triple-lines", "t4-stray-close"])
def test_each_form_the_critic_sent_on_night_115_is_read(raw):
    """
    Frame 122. Turn 1 broke on `claim's` in `why`: an apostrophe between two
    letters is text. Turns 2 to 6 wrapped the quote as `"'''...'''\\"`, and
    turn 4 added `")` after the call. Each has one reading, and the third
    reading takes it.
    """
    got = toolproto.extract(raw, UPHOLD)
    assert len(got) == 1 and isinstance(got[0], toolproto.ToolCall), got
    assert got[0].args["citation"] == "examples/validation/validation.py"
    assert got[0].args["quote"] == S86_QUOTE
    assert got[0].args["why"].endswith("supporting the claim's reference to it.")


def test_the_refusal_names_the_value_that_never_ends_and_shows_a_form():
    """
    Frame 122: the old refusal named `text=`, and the Critic put triple
    quotes on `quote`. The value that broke was `why`. The refusal now names
    it, and its example parses.
    """
    got = toolproto.extract(
        "TOOL: challenge.uphold(citation='a.py', quote='x', why='it is done)",
        UPHOLD)
    assert len(got) == 1 and isinstance(got[0], toolproto.ToolError), got
    assert got[0].reason == (
        "unterminated argument list: the value of why never ends. Either a "
        "quote inside why closed it early, or its closing quote has a "
        "backslash before it. Put a value with quotes or line breaks between "
        "triple quotes, three single quotes at each end. Write the value as "
        "it is, with no backslashes:\n"
        "why='''the text, with its quotes and line breaks as they are'''")
    form = got[0].reason.split(":\n", 1)[1]
    shown = toolproto.extract(f"TOOL: challenge.uphold(citation='a.py', quote='x', {form})",
                              UPHOLD)
    assert shown[0].args["why"] == "the text, with its quotes and line breaks as they are"


def test_the_refusal_names_no_value_that_opens_inside_a_tuple():
    """Frame 122's review: the open quote of `a.b(x=(1, 'y)` sits inside a
    tuple, so it is not the value of `x`. The old refusal stays."""
    got = toolproto.extract("TOOL: a.b(x=(1, 'y)")
    assert len(got) == 1 and isinstance(got[0], toolproto.ToolError), got
    assert got[0].reason.startswith(
        "unterminated argument list: a quote inside a quoted argument")


WRITE = {
    "code.write": ({"path", "text"}, {"path", "text", "start", "end"}),
    "tests.encode": ({"id", "criterion_id", "path", "body"},
                     {"id", "criterion_id", "path", "body", "batch_id"}),
}


@pytest.mark.parametrize("raw", [
    # A quote that opens right after a quote closes. fb1bdba's third
    # reading joined the two strings into `why="ab it's"`.
    "TOOL: challenge.uphold(citation='a.py', quote='x', why='a''b it's')",
    # A tail after `')`: the value did not end at the first `')`.
    "TOOL: challenge.uphold(citation='a.py', quote='x', why='it's f(x')\nmore')",
], ids=["adjacent-quotes", "tail-after-close"])
def test_a_doubtful_third_reading_is_a_refusal(raw):
    """A refusal is safe, and a wrong value is not. The third reading gives
    up when a value is not one token or the call has a tail."""
    got = toolproto.extract(raw, UPHOLD)
    assert got and all(isinstance(g, toolproto.ToolError) for g in got), got


@pytest.mark.parametrize("raw", [
    # Frame 122's first review: pass 1 joined `''` into nothing and wrote
    # `return ` where the seat wrote `return ''`.
    "TOOL: code.write(path='a.py', text='def name(x):\\n    if not x:\\n"
    "        return ''\\n    return f\"it's {x}\"\\n')",
    # Frame 122's second review: each wrote a wrong value at 78ed236.
    "TOOL: code.write(path='a.py', text='a', end='it's')",
    "TOOL: code.write(text='x = 1', path='it's.py')",
    "TOOL: tests.encode(id='t1', criterion_id='c1', body='f(x', path='it's')",
    "TOOL: code.write(path='a.py', text='', path='a'it')",
], ids=["empty-string", "end-its", "path-its", "body-path-its", "path-twice"])
def test_a_function_that_writes_never_gets_a_wrong_write(raw):
    """Each call is a refusal before frame 122, and it stays a refusal."""
    got = toolproto.extract(raw, WRITE)
    assert got and all(isinstance(g, toolproto.ToolError) for g in got), got


def test_only_a_function_that_writes_nothing_gets_the_third_reading():
    """A wrong `why` is a sentence that a door checks. A wrong `text` is a
    file on disk. The same broken value parses for the one and not the
    other."""
    value = "='the claim's reference')"
    sigs = dict(UPHOLD, **{"notes.add": ({"text"}, {"text"})})
    uphold = toolproto.extract(
        "TOOL: challenge.uphold(citation='a.py', quote='x', why" + value, sigs)
    assert isinstance(uphold[0], toolproto.ToolCall), uphold
    assert uphold[0].args["why"] == "the claim's reference"
    write = toolproto.extract("TOOL: notes.add(text" + value, sigs)
    assert isinstance(write[0], toolproto.ToolError), write
