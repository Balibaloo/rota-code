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


def test_a_call_without_parentheses_is_a_call():
    """
    This asserted the opposite, and the opposite cost a session.

    An Architect woken to write a constraint spent every one of its twelve turns
    on `TOOL: model.consult` — seven rejections reading "missing argument list",
    for a function whose arguments are all optional — and never reached the
    write it was woken for. A format complaint that cannot name the thing it
    wants teaches nothing, and the model duly did not learn.

    Parsed as `name()`, so a call genuinely missing a required argument fails at
    `validate`, which knows the signature and can say which one.
    """
    result = only("TOOL: glossary.lookup")
    assert isinstance(result, ToolCall)
    assert result.name == "glossary.lookup" and result.args == {}


def test_the_marker_is_not_a_function_name():
    """
    The dot is what keeps the above honest. Every function is `artefact.verb`,
    and without that check `TOOL: TOOL: TOOL:` parsed its own marker as a
    zero-argument call to `TOOL`.
    """
    result = only("TOOL: notdotted")
    assert isinstance(result, ToolError) and "missing argument list" in result.reason


def test_garbage_arguments_are_an_error():
    result = only("TOOL: glossary.lookup(term=)")
    assert isinstance(result, ToolError) and "could not parse" in result.reason


def test_positional_arguments_are_carried_not_rejected():
    """
    This used to assert a rejection. The rule did not disappear, it moved to
    the sandbox, which is the only layer that knows the signature the call has
    to satisfy — see test_t0_sandbox for where it now lives.
    """
    result = only("TOOL: glossary.lookup('account')")
    assert isinstance(result, ToolCall)
    assert result.pos == ("account",) and result.args == {}


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
    assert parse_args("") == ({}, ())


# ---------------------------------------------------------------------------
# Tolerances. Each of these was a real rejection, counted in the cassette
# database, and each cost whole cases: the role spends its remaining turns
# apologising to an error message instead of doing the work.
# ---------------------------------------------------------------------------

def test_json_spelling_of_the_keywords():
    """`true` is what half the tool-calling world writes, and it is not ambiguous."""
    args, _ = parse_args("id='l1', default_taken=true, other=false, gone=null")
    assert args == {"id": "l1", "default_taken": True,
                    "other": False, "gone": None}


def test_a_bare_word_is_a_string_that_lost_its_quotes():
    args, _ = parse_args("refs=m_dead_75b4f6")
    assert args == {"refs": "m_dead_75b4f6"}


def test_positional_arguments_survive_to_the_binder():
    """The parser does not know the signature, so it is not the parser's call."""
    args, pos = parse_args("'t1', 'c1', path='test_close.py'")
    assert args == {"path": "test_close.py"}
    assert pos == ("t1", "c1")


def test_nested_calls_are_still_refused():
    """Tolerance is not evaluation. `body=criteria.load(id='b1')[0]['body']`."""
    with pytest.raises(Exception):
        parse_args("body=criteria.load(id='b1')[0]['body']")


def test_keywords_inside_containers_too():
    args, _ = parse_args("flags=[true, false], m={'a': true}")
    assert args == {"flags": [True, False], "m": {"a": True}}


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


# ---------------------------------------------------------------------------
# The marker used as a label. Taken verbatim from a Terminologist survey that
# committed empty five times out of five with no error logged anywhere.
# ---------------------------------------------------------------------------

LABELLED = """CODE.SURVEY: The top grains are the ones with the highest fan-in.
I will start by looking at the terms used in this file and its imports.

GLOSSARY.AMEND: id = 1 term = "Charge" sense_short = billing entity
sense_body = "A Charge represents a billing entity."

GLOSSARY.AMEND: id = 2 term = "Invoice" sense_short = "billing document"
"""


def test_the_marker_used_as_a_label_is_still_a_call():
    calls = extract_lenient(LABELLED, {"glossary.amend", "code.survey",
                                       "glossary.consult"})
    assert [c.name for c in calls] == ["glossary.amend", "glossary.amend"]
    assert calls[0].args == {
        "id": "1",                          # unquoted, so it stays text
        "term": "Charge",
        "sense_short": "billing entity",    # a bare value can be two words
        "sense_body": "A Charge represents a billing entity.",
    }


def test_a_label_on_prose_is_not_a_call():
    """
    `CODE.SURVEY: The top grains are the ones with the highest fan-in.`

    From the same completion, and deliberately *not* recovered. A name followed
    by arguments is an intention; a name followed by a sentence is the model
    narrating. Recovering the second would let prose dispatch, which is the one
    thing the lenient path must never do — and the price of declining it is a
    read that goes uncalled, not a write that should not have happened.
    """
    assert extract_lenient("CODE.SURVEY: The top grains have the highest fan-in.",
                           {"code.survey"}) == []


def test_a_label_outside_the_working_set_is_not_a_call():
    """`NOTE:` and `SUMMARY:` are prose, and prose must never dispatch."""
    assert extract_lenient("NOTE: id = 1 term = 'Charge'",
                           {"glossary.amend"}) == []


def test_markers_win_over_labels():
    text = "GLOSSARY.AMEND: id = 1\nTOOL: glossary.consult()"
    calls = extract_lenient(text, {"glossary.amend", "glossary.consult"})
    assert [c.name for c in calls] == ["glossary.consult"]


def test_ellipsis_is_a_placeholder_not_a_value():
    """
    `literal_eval` is delighted to return Python's Ellipsis for `...`, which
    then survives the sandbox and the write and dies at commit with `Object of
    type ellipsis is not JSON serializable` -- one placeholder, one lost
    session. Found in L1 after the parser was made more tolerant, which is
    exactly when to look for it.
    """
    result = only("TOOL: criteria.specify(id='c1', text=...)")
    assert isinstance(result, ToolError) and "placeholder" in result.reason
