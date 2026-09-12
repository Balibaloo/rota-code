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
    """If any marker is present, a call mentioned inline in prose is prose."""
    text = ("TOOL: criteria.load(batch_id='b1')\n"
            "and here is prose mentioning transcript.append(id='x') inline")
    calls = extract_lenient(text, ALLOWED)
    assert [c.name for c in calls] == ["criteria.load"]


def test_a_bare_call_on_its_own_line_is_taken_beside_marked_ones():
    """
    The orientation session wrote four complete `problem.assert(...)` lines as
    bullets under its account and one marked attest at the end. Marked calls
    winning outright meant the attest ran and the four items did not, and the
    record said the program had nothing in it. A complete call at the start of
    its own line is a call; the inline mention above stays prose.
    """
    text = ("1. **intake**\n"
            "\t* transcript.append(id='u1', author='principal', text='hello')\n"
            "- transcript.append(id='u2', author='principal', text='again')\n"
            "TOOL: criteria.load(batch_id='b1')\n")
    calls = extract_lenient(text, ALLOWED)
    assert [c.name for c in calls] == ["transcript.append", "transcript.append",
                                       "criteria.load"]
    assert calls[0].args["id"] == "u1"


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
    """A label with arguments beside a marked call is taken too, in order:
    per-area sessions wrote every amend as a labelled block under a marked
    `code.area`, and "markers win" made all of them narration. A label with
    no arguments is still narration (`_labelled` requires some)."""
    text = "GLOSSARY.AMEND: id = 1\nTOOL: glossary.consult()"
    calls = extract_lenient(text, {"glossary.amend", "glossary.consult"})
    assert [c.name for c in calls] == ["glossary.amend", "glossary.consult"]
    text = "GLOSSARY.AMEND: and then I will consult\nTOOL: glossary.consult()"
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


def test_square_brackets_are_read_as_the_parentheses_they_stand_for():
    """
    A define session wrote `TOOL: glossary.amend [term="note", ...]` twelve
    turns running and was refused twelve times with a message naming the
    missing argument that was right there. The shape comes from the prompt's
    own `[code.concordance]` labels. Unambiguous, so parsed; a bare path in a
    bracket is still the parse error it always was, now saying how to write it.
    """
    from rota.llm.toolproto import ToolCall, ToolError, extract

    got = extract('TOOL: glossary.amend [term="note", sense_body="a", sense_short="b"]')
    assert [type(g) for g in got] == [ToolCall]
    assert got[0].name == "glossary.amend" and got[0].args["term"] == "note"

    got = extract("TOOL: code.concordance [term='note'] [limit=3]")
    assert isinstance(got[0], ToolCall) and got[0].args == {"term": "note", "limit": 3}

    got = extract("TOOL: code.source [src/intents/index.ts]")
    assert isinstance(got[0], ToolError) and "round brackets" in got[0].reason


def test_a_labelled_block_with_colon_keys_is_a_call_beside_marked_ones():
    """
    `glossary.amend:` then `term: ...`, `sense_body: ...`, `sense_short: ...`
    -- the shape every amend in one per-area run took, beside a marked
    `code.area`. The labelled fallback knew `key = value` and ran only when no
    marker was present, so all of it was narration.
    """
    text = ("TOOL: criteria.load(batch_id='b1')\n\n"
            "transcript.append:\n"
            "id: u7\n"
            "author: principal\n"
            "text: a note about: colons, and a URL http://x.test/path\n\n"
            "and then prose.")
    calls = extract_lenient(text, ALLOWED)
    assert [c.name for c in calls] == ["criteria.load", "transcript.append"]
    assert calls[1].args["id"] == "u7"
    assert calls[1].args["text"].startswith("a note about: colons")


def test_a_call_written_one_argument_per_line_parses_strictly():
    """qwen2.5 writes every call this way. Newlines between arguments are
    whitespace; newlines inside a quoted argument are escaped and restored."""
    from rota.llm.toolproto import ToolCall, extract

    text = ('TOOL: transcript.append(\n'
            '     id="u1",\n'
            '     author="principal",\n'
            '     text="a line\nand another"\n'
            ' )')
    got = extract(text)
    assert isinstance(got[0], ToolCall), got
    assert got[0].args == {"id": "u1", "author": "principal", "text": "a line\nand another"}


def test_a_push_label_with_colon_keys_is_a_call():
    """`[glossary.amend]` then `term: ...` lines: the prompt's own push-block
    label, reproduced by qwen2.5:14b for every call. Nothing parsed, and the
    word was abandoned after three silent sessions."""
    from rota.llm.toolproto import ToolCall, extract_lenient

    text = ("In this project, a prompt is a text input.\n\n"
            "[transcript.append]\n"
            "id: u9\n"
            "author: principal\n"
            "text: A text input guiding user input during note creation.\n")
    got = extract_lenient(text, ALLOWED)
    assert [type(g) for g in got] == [ToolCall] and got[0].name == "transcript.append"
    assert got[0].args["id"] == "u9" and got[0].args["author"] == "principal"



def test_bare_argument_lines_name_the_only_function_that_takes_them():
    """qwen2.5:14b ends a survey with `outcome="found"` and `citations=[...]`
    and no function name. The arguments name the function when only one
    function in the working set takes them; two candidates is ambiguity and
    is not parsed."""
    from rota.llm.toolproto import ToolCall, extract_lenient

    sigs = {"surveys.attest": ({"outcome"}, {"outcome", "citations"}),
            "glossary.amend": ({"term"}, {"term", "sense_body", "sense_short", "sense"}),
            "other.thing": ({"outcome"}, {"outcome", "citations", "extra"})}
    text = ('The area defines types.\n\n'
            'outcome="found"\n'
            'citations=["src/a.py", "src/b.py"]\n')
    got = extract_lenient(text, {"surveys.attest", "glossary.amend", "other.thing"}, signatures=sigs)
    assert got == [], "two functions take these keys: not parsed"
    del sigs["other.thing"]
    got = extract_lenient(text, {"surveys.attest", "glossary.amend"}, signatures=sigs)
    assert [type(g) for g in got] == [ToolCall] and got[0].name == "surveys.attest"
    assert got[0].args == {"outcome": "found", "citations": ["src/a.py", "src/b.py"]}
    # beside a marked call, same rule
    text2 = "TOOL: glossary.amend(term='x', sense_body='b', sense_short='s')\n\n" + text
    got = extract_lenient(text2, {"surveys.attest", "glossary.amend"}, signatures=sigs)
    assert [g.name for g in got] == ["glossary.amend", "surveys.attest"]



def test_a_labelled_blocks_key_lines_are_not_also_an_unlabelled_call():
    """`glossary.amend:` followed by `term = ...` lines is one call, parsed by
    the label; the same lines must not be read a second time as an unlabelled
    block naming glossary.amend by its keys."""
    from rota.llm.toolproto import extract_lenient

    sigs = {"surveys.attest": ({"outcome"}, {"outcome", "citations"}),
            "glossary.amend": ({"term"}, {"term", "sense_body", "sense_short", "sense"})}
    text = ('glossary.amend:\n'
            'term = "intent"\n'
            'sense_body = "a named thing"\n'
            'sense_short = "thing"\n'
            '\n'
            '[glossary.amend]\n'
            'term: provider\n'
            'sense_body: a table\n'
            '\n'
            'outcome="found"\n'
            'citations=["src/a.py"]\n')
    got = extract_lenient(text, set(sigs), signatures=sigs)
    assert [g.name for g in got] == ["glossary.amend", "glossary.amend", "surveys.attest"]
    assert [g.args.get("term") for g in got[:2]] == ["intent", "provider"]



def test_bare_amends_then_a_one_line_attest_with_no_marker_keeps_both():
    """The 14B's second shape: bare `glossary.amend(...)` lines, then
    `outcome="found", citations=[...]` on one line, no marker anywhere. The
    amends are calls and so is the attest; neither may cost the other. And
    the inner lines of a call written one argument per line are that call's
    arguments, not a second call."""
    from rota.llm.toolproto import extract_lenient

    sigs = {"surveys.attest": ({"outcome"}, {"outcome", "citations"}),
            "glossary.amend": ({"term"}, {"term", "sense_body", "sense_short", "sense"})}
    text = ("The area defines types.\n\n"
            "glossary.amend(term='intent_properties', sense_body='Defines it.', "
            "sense_short='Creation properties.')\n\n"
            "glossary.amend(\n"
            "    term='note_destination',\n"
            "    sense_body='Where the note goes.',\n"
            "    sense_short='Folder and filename.'\n"
            ")\n\n"
            'outcome="found", citations=["src/intents/index.ts", "src/variables/index.ts"]\n')
    got = extract_lenient(text, set(sigs), signatures=sigs)
    assert [g.name for g in got] == ["glossary.amend", "glossary.amend", "surveys.attest"]
    assert got[1].args["term"] == "note_destination"
    assert got[2].args == {"outcome": "found",
                           "citations": ["src/intents/index.ts", "src/variables/index.ts"]}



def test_a_key_repeated_once_per_line_is_that_keys_list():
    """`citations="a"` / `citations="b"` / `citations="c"` under `outcome=`:
    one key written once per value is the list, not the last value."""
    from rota.llm.toolproto import extract_lenient

    sigs = {"surveys.attest": ({"outcome"}, {"outcome", "citations"})}
    text = ('outcome="found"\n'
            'citations=".github/ISSUE_TEMPLATE/feature_request.md"\n'
            'citations=".github/workflows/release.yml"\n'
            'citations=".github/ISSUE_TEMPLATE/bug_report.md"\n')
    got = extract_lenient(text, set(sigs), signatures=sigs)
    assert [g.name for g in got] == ["surveys.attest"]
    assert got[0].args["citations"] == [".github/ISSUE_TEMPLATE/feature_request.md",
                                        ".github/workflows/release.yml",
                                        ".github/ISSUE_TEMPLATE/bug_report.md"]



def test_a_word_glued_to_a_label_is_the_calls_first_positional_argument():
    """`glossary.amend:template_select_modal sense_body='...' sense_short='...'`:
    the token between the label and the first `key=` is positional, bound by
    the sandbox -- `term`, here. The ordinary `glossary.amend: term = "x"`
    shape is untouched."""
    from rota.llm.toolproto import extract_lenient

    text = ("glossary.amend:template_select_modal sense_body='A modal for templates.' "
            "sense_short='Modal for selecting templates.'\n"
            "glossary.amend: term = \"filtered_opener\" sense_body = \"a plugin\" sense_short = \"plugin\"\n")
    got = extract_lenient(text, {"glossary.amend"})
    assert [g.name for g in got] == ["glossary.amend", "glossary.amend"]
    assert got[0].pos == ("template_select_modal",) and "term" not in got[0].args
    assert got[0].args["sense_short"] == "Modal for selecting templates."
    assert got[1].pos == () and got[1].args["term"] == "filtered_opener"



def test_backticked_labels_and_keys_and_a_comma_after_the_name_still_parse():
    """`` `glossary.amend`: `sense_body`='...', `sense_short`='...', term=x `` and
    `` `surveys.attest`, outcome="found", citations=[...] ``: one session's
    whole output, and none of it parsed."""
    from rota.llm.toolproto import extract_lenient

    text = ("`glossary.amend`: `sense_body`='A function to calculate a relative path.', "
            "`sense_short`='Calculates a relative path.', term=getRelativePath\n\n"
            "`surveys.attest`, outcome=\"found\", citations=[\"src/variables/index.ts\", "
            "\"src/variables/suggest.ts\"]\n")
    got = extract_lenient(text, {"glossary.amend", "surveys.attest"})
    assert [g.name for g in got] == ["glossary.amend", "surveys.attest"], got
    assert got[0].args["term"] == "getRelativePath"
    assert got[0].args["sense_short"] == "Calculates a relative path."
    assert got[1].args["outcome"] == "found"
    assert got[1].args["citations"] == ["src/variables/index.ts", "src/variables/suggest.ts"] \
        or got[1].args["citations"] == '["src/variables/index.ts", "src/variables/suggest.ts"]'



def test_a_label_token_with_a_quoted_headline_and_key_lines_under_it():
    """`glossary.amend: normalizedIntentName "A standardized name ..."` then
    `sense_body:` and `sense_short:` lines: the token is `term`, the headline
    is dropped, the lines are the sense. Three refusals for a missing `term`
    and an open area, before."""
    from rota.llm.toolproto import extract_lenient

    text = ('glossary.amend: normalizedIntentName "A standardized name derived from an intent."\n'
            "sense_body: `normalizedIntentName` is a version of an intent's name with spaces "
            "made hyphens, used for command ids.\n"
            "sense_short: A consistent format for intent names used as command identifiers.\n\n"
            'surveys.attest(outcome="found", citations=["src/main.ts"])\n')
    got = extract_lenient(text, {"glossary.amend", "surveys.attest"})
    assert [g.name for g in got] == ["glossary.amend", "surveys.attest"], got
    assert got[0].pos == ("normalizedIntentName",)
    assert got[0].args["sense_short"].startswith("A consistent format")
    assert got[0].args["sense_body"].startswith("`normalizedIntentName` is a version")
    # the ordinary `label: term = x` and `label:` + `term: x` shapes are untouched
    text2 = 'glossary.amend: term = "a" sense_body = "b" sense_short = "c"\n\nglossary.amend:\nterm: d\nsense_body: e\nsense_short: f\n'
    got2 = extract_lenient(text2, {"glossary.amend"})
    assert [(g.pos, g.args["term"]) for g in got2] == [((), "a"), ((), "d")]



def test_a_backticked_label_token_with_a_dash_headline():
    """`` glossary.amend: `intentnote` -- A file containing ... `` then
    `sense_body:` / `sense_short:` lines: the token is `term`, backticks and
    headline dropped."""
    from rota.llm.toolproto import extract_lenient

    text = ("glossary.amend: `intentnote` \u2014 A file containing definitions of intents.\n"
            "sense_body: An intent note is a file within an Obsidian vault whose front matter "
            "defines how new notes are created.\n"
            "sense_short: A file with front matter specifying intents.\n\n"
            'outcome="found"\ncitations="/src/main.ts"\n')
    sigs = {"surveys.attest": ({"outcome"}, {"outcome", "citations"}),
            "glossary.amend": ({"term"}, {"term", "sense_body", "sense_short", "sense"})}
    got = extract_lenient(text, set(sigs), signatures=sigs)
    assert [g.name for g in got] == ["glossary.amend", "surveys.attest"], got
    assert got[0].pos == ("intentnote",)
    assert got[0].args["sense_short"] == "A file with front matter specifying intents."
    assert got[1].args == {"outcome": "found", "citations": "/src/main.ts"}



def test_a_working_set_name_in_capitals_is_that_name():
    """`MODEL.AMEND(headline=..., text=..., bindings=[...])` at line start is
    `model.amend`; one session wrote two that way and closed its area empty."""
    from rota.llm.toolproto import extract_lenient

    text = ('MODEL.AMEND(headline="PTPlugin.manifest.id", text="Obsidian knows the plugin by it", '
            'bindings=["manifest.json"])\n\n'
            'surveys.attest(outcome="found", citations=["manifest.json"])\n')
    got = extract_lenient(text, {"model.amend", "surveys.attest"})
    assert [g.name for g in got] == ["model.amend", "surveys.attest"], got
    assert got[0].args["headline"] == "PTPlugin.manifest.id"



def test_a_table_under_a_label_is_one_call_per_row():
    """`[glossary.amend]` then `term | sense_body | sense_short` and rows: the
    header names the keys; each row is a call. llama wrote a whole survey
    that way, three times, and the area was abandoned."""
    from rota.llm.toolproto import extract_lenient

    text = ("The area defines the variable providers.\n\n"
            "[glossary.amend]\n"
            "term | sense_body | sense_short\n"
            "TemplateVariableVariables_Note | An object representing a note variable. | A dictionary of filter properties.\n"
            "parseNoteVariableFrontmatter | A function that parses a note variable's frontmatter. | Parses note frontmatter.\n\n"
            'surveys.attest(outcome="found", citations=["src/variables/providers/note.ts"])\n')
    got = extract_lenient(text, {"glossary.amend", "surveys.attest"})
    assert [g.name for g in got] == ["glossary.amend", "glossary.amend", "surveys.attest"], got
    assert got[0].args == {"term": "TemplateVariableVariables_Note",
                           "sense_body": "An object representing a note variable.",
                           "sense_short": "A dictionary of filter properties."}
    assert got[1].args["term"] == "parseNoteVariableFrontmatter"
    # a pipe-bordered table with a separator row is the same table
    text2 = ("glossary.amend:\n| term | sense_body | sense_short |\n|---|---|---|\n"
             "| x | a body | a short |\n")
    got2 = extract_lenient(text2, {"glossary.amend"})
    assert [g.args["term"] for g in got2] == ["x"]


def test_a_whole_call_inside_one_bracket_is_a_labelled_call():
    """`[glossary.amend term="..." sense_body="..." sense_short="..."]` -- the
    14B wrote a define word this way three sessions running and the word was
    quarantined. The opening bracket becomes a label; the trailing one is
    inert."""
    from rota.llm.toolproto import extract_lenient

    text = ('In this project, an `exclude_folder_name` is a string.\n\n'
            '[glossary.amend term="exclude_folder_name" sense_body="A string that '
            'specifies a folder name to be excluded by configuration." '
            'sense_short="A string specifying a folder to exclude."]\n')
    got = extract_lenient(text, {"glossary.amend", "surveys.attest"})
    assert [g.name for g in got] == ["glossary.amend"], got
    assert got[0].args["term"] == "exclude_folder_name"
    assert got[0].args["sense_short"].rstrip("]") == "A string specifying a folder to exclude."


def test_a_label_token_followed_by_a_comma_still_binds():
    """`glossary.amend: is_under, sense_body="..." sense_short="..."` inside a
    yaml fence: the comma between the glued word and the keywords cost a
    define word its three attempts."""
    from rota.llm.toolproto import extract_lenient

    text = ('```yaml\n'
            'glossary.amend: is_under, sense_body="A numerical constraint: another '
            'value must be less than it." sense_short="A less-than validation constraint."\n'
            '```\n')
    got = extract_lenient(text, {"glossary.amend"})
    assert [g.name for g in got] == ["glossary.amend"], got
    assert got[0].pos == ("is_under",)
    assert got[0].args["sense_short"].startswith("A less-than")


def test_the_block_form_the_prompt_teaches_is_accepted():
    """
    `_as_block` renders every long text result as `[text]` + raw lines, and
    the Developer mirrored the shape back when *sending* long text:
    `code.write(path=..., text=[text]` with the source following in the open.
    The paren scan cannot survive arbitrary code, so the call was a ToolError
    every time -- five runs of five, twice, with the model saying on its own
    turn that its write had been rejected and retrying the identical shape,
    while the session ended committing an untouched tree.

    Same lineage as the square-bracket acceptance, whose comment already says
    "the brackets come from the prompt itself".
    """
    from rota.llm.toolproto import extract

    completion = (
        "TOOL: code.write(path='src/notify/formatting.py', text=[text]\n"
        "ELLIPSIS = chr(8230)\n\n\n"
        "def money(cents):\n"
        "    dollars = cents / 100\n"
        "    return f\"${dollars:,.2f}\"\n"
    )
    call = extract(completion)[0]
    assert call.name == "code.write"
    assert call.args["path"] == "src/notify/formatting.py"
    assert "def money" in call.args["text"]
    assert call.args["text"].count("\n") >= 4, "real newlines, not escapes"

    # A following call bounds the block.
    two = extract(completion + "\nTOOL: code.commit(message='add money')\n")
    assert [c.name for c in two] == ["code.write", "code.commit"]


def test_the_block_sentinel_is_the_name_in_brackets_and_nothing_else():
    """The bound: `refs=[...]` is a list, `x=[y]` is not a sentinel, and both
    parse exactly as they always have."""
    from rota.llm.toolproto import extract

    assert extract("TOOL: msg.answer_liaison(refs=['g1'])")[0].args["refs"] == ["g1"]
    call = extract("TOOL: model.load(ids=['a'])\nplain prose after")[0]
    assert call.args["ids"] == ["a"]


def test_bare_names_and_the_pass_keyword_are_the_words_they_spell():
    """S0 walk thirty-three: `verdicts.emit(b1, pass, diff_ref='script.py')`
    three sessions running, and the verdict on a green batch never landed.
    A bare identifier where a value goes is the string it spells; the
    keyword `pass` outside quotes is the word; prose that mentions passing
    is untouched."""
    from rota.llm import toolproto

    kwargs, pos = toolproto.parse_args("b1, pass, diff_ref='script.py'")
    assert pos == ("b1", "pass") and kwargs == {"diff_ref": "script.py"}
    kwargs, pos = toolproto.parse_args(
        "batch_id=b1, result=pass, failed_criterion=None, diff_ref='x'")
    assert kwargs == {"batch_id": "b1", "result": "pass",
                      "failed_criterion": None, "diff_ref": "x"}
    kwargs, _ = toolproto.parse_args("text='all tests pass now', refs=['a']")
    assert kwargs["text"] == "all tests pass now"


def test_a_quote_that_swallows_the_next_argument_is_named():
    """L1-DV-apply-the-answer (2026-09-12): a possessive inside single-quoted
    source closed the string, `text=` rode along inside `path`, and the
    refusal said only that `text` was missing."""
    say = ("TOOL: code.write(path='a.py', text='x = singular + \\'s'}\"', "
           "start=11, end=-1)")
    out = extract(say)
    assert len(out) == 1 and isinstance(out[0], ToolError)
    assert "text=[text]" in out[0].reason
    # The lenient path parses the same call into arguments, with `text=`
    # riding inside `path`; the door names the quote and the swallowed key.
    from rota.llm import toolproto
    params = {"path", "text", "start", "end"}
    swallowed = toolproto._swallowed_argument(
        {"path": "a.py', text='x = singular + ", "start": "11", "end": "-1"}, params)
    assert swallowed == ("path", "text")
    assert toolproto._swallowed_argument({"path": "a.py", "text": "x = 1"}, params) is None
    # Source carries keywords of its own (clickI night 20: `", nargs=-1`);
    # only a name in the signature is a swallowed argument, and without the
    # signature the door stays shut.
    src = {"path": "a.py", "text": "click.argument('src', nargs=-1)\n"}
    assert toolproto._swallowed_argument(src, params) is None
    assert toolproto._swallowed_argument(
        {"path": "a.py', text='x", "start": "1", "end": "2"}, None) is None
    # The block form carries the same source with no quoting at all.
    block = "TOOL: code.write(path='a.py', text=[text]\nx = singular + 's'\ny = f\"{x}\"\n"
    call = extract(block)[0]
    assert isinstance(call, ToolCall) and call.args["text"] == "x = singular + 's'\ny = f\"{x}\""

