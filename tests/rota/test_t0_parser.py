"""
T0-S10 — `TOOL:` protocol round-trip.

The load-bearing property is negative: malformed input must produce an *error*,
never a misparse. Everything else here supports that.
"""
from __future__ import annotations

import pytest

from rota.llm.toolproto import ToolCall, ToolError, extract, parse_args, validate


def only(text: str):
    results = extract(text)
    assert len(results) == 1, results
    return results[0]


def test_keyword_form():
    call = only("TOOL: glossary.lookup(term='account')")
    assert isinstance(call, ToolCall)
    assert call.name == "glossary.lookup" and call.args == {"term": "account"}


def test_json_form():
    call = only('TOOL: glossary.lookup({"term": "account"})')
    assert isinstance(call, ToolCall) and call.args == {"term": "account"}


def test_mixed_quotes_and_apostrophes():
    call = only("""TOOL: problem.assert(id='i1', text="the user's account")""")
    assert call.args["text"] == "the user's account"


def test_parens_inside_a_string_do_not_truncate():
    call = only("TOOL: criteria.specify(id='c1', text='delete (soft) the row')")
    assert call.args["text"] == "delete (soft) the row"


def test_crlf_and_newlines_survive():
    """CRLF scars are inherited deliberately: Windows completions contain them."""
    call = only("TOOL: tests.encode(id='t1', body='line one\r\nline two')")
    assert call.args["body"] == "line one\nline two"


def test_multiple_calls_in_order():
    results = extract(
        "thinking...\n"
        "TOOL: glossary.lookup(term='a')\n"
        "more thinking\n"
        "TOOL: glossary.lookup(term='b')\n"
    )
    assert [r.args["term"] for r in results] == ["a", "b"]


def test_list_and_int_arguments():
    call = only("TOOL: model.amend(id='c1', headline='x', bindings=['a.py','b.py'])")
    assert call.args["bindings"] == ["a.py", "b.py"]
    call = only("TOOL: problem.prioritize(id='b1', priority=3)")
    assert call.args["priority"] == 3


# ---- the half that matters -------------------------------------------------

def test_unterminated_args_is_an_error_not_a_misparse():
    result = only("TOOL: glossary.lookup(term='account'")
    assert isinstance(result, ToolError) and "unterminated" in result.reason


def test_missing_arglist_is_an_error():
    result = only("TOOL: glossary.lookup")
    assert isinstance(result, ToolError) and "missing argument list" in result.reason


def test_garbage_arguments_are_an_error():
    result = only("TOOL: glossary.lookup(term=)")
    assert isinstance(result, ToolError) and "could not parse" in result.reason


def test_positional_arguments_rejected():
    result = only("TOOL: glossary.lookup('account')")
    assert isinstance(result, ToolError)
    assert "positional" in result.reason


def test_no_code_execution_via_arguments():
    """literal_eval, never eval: the argument list is untrusted input."""
    result = only("TOOL: glossary.lookup(term=__import__('os').system('echo pwned'))")
    assert isinstance(result, ToolError)


def test_bare_marker_does_not_hang():
    results = extract("TOOL: TOOL: TOOL:")
    assert results and all(isinstance(r, ToolError) for r in results)


def test_prose_mentioning_tools_is_ignored():
    assert extract("I could call a tool here, but I will not.") == []


def test_validate_rejects_outside_working_set():
    call = ToolCall(name="model.amend", args={}, raw="model.amend()")
    err = validate(call, allowed={"criteria.load", "code.read"})
    assert isinstance(err, ToolError) and "working set" in err.reason


def test_validate_accepts_inside_working_set():
    call = ToolCall(name="criteria.load", args={}, raw="criteria.load()")
    assert validate(call, allowed={"criteria.load"}) is None


def test_parse_args_empty():
    assert parse_args("") == {}


# ---------------------------------------------------------------------------
# Lenient extraction — the fallback for completions that drop the marker
# ---------------------------------------------------------------------------

from rota.llm.toolproto import extract_lenient

ALLOWED = {"transcript.append", "brief.segment", "msg.confirm_principal", "criteria.load"}


def test_lenient_recovers_bare_calls():
    """
    Small models omit the TOOL: prefix constantly. Strict parsing turns that into
    a silent no-op session that commits empty — success-shaped failure, the worst
    kind.
    """
    text = ("transcript.append(id='u1', author='principal', text='hello')\n"
            "msg.confirm_principal(refs=['s1'])")
    calls = extract_lenient(text, ALLOWED)
    assert [c.name for c in calls] == ["transcript.append", "msg.confirm_principal"]


def test_marked_calls_always_win():
    """If any marker is present, the fallback never runs — no double-parsing."""
    text = ("TOOL: criteria.load(batch_id='b1')\n"
            "and here is prose mentioning transcript.append(id='x') inline")
    calls = extract_lenient(text, ALLOWED)
    assert [c.name for c in calls] == ["criteria.load"]


def test_lenient_ignores_names_outside_the_working_set():
    """The fallback is safe because the name must already be granted."""
    text = "model.amend(id='c1', headline='sneaky')"
    assert extract_lenient(text, ALLOWED) == []


def test_lenient_ignores_prose():
    assert extract_lenient("I will now append to the transcript.", ALLOWED) == []


def test_lenient_does_not_match_a_longer_identifier():
    assert extract_lenient("my_transcript.append(id='x')", ALLOWED) == []
