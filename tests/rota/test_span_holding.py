"""
A span refusal names a span of whole statements that holds the seat's lines
(frame 313).

Night 161: s317 sent the right repair of `version_option` at a6ed327861 in
the click repository as 540..560 and 537..560, three times each. The door
said "falls inside raise" and "crosses from one block to another". It
offered the raise or the whole callback, and no span that held the seat's
lines, so no Developer committed. s237's docstring refusal held both
boundaries in one statement, and its words stay.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from rota.roles import api
from tests.rota.test_offers_followed import _developer

FIXTURES = Path(__file__).parent / "fixtures"
# `git show a6ed327861:src/click/decorators.py` in the clickI sample repository.
DECORATORS = (FIXTURES / "night161_decorators_a6ed327861.txt").read_text()
# `git show ff776a1:src/click/termui.py`, the file s237 met.
TERMUI = (FIXTURES / "night161_termui_ff776a1.txt").read_text()
LINES = DECORATORS.splitlines()


def _refusal(sb, **kwargs):
    with pytest.raises(ValueError) as exc:
        sb.call("code.write", path="m.py", **kwargs)
    return str(exc.value), list(sb.ctx.offers)


_BLOCK = [
    "        # Build the base message first",
    '        base_message = message % {"prog": prog_name, "package": package_name, '
    '"version": version}',
    "{blank}",
    "        # Append Python version if show_python is True",
    "        if show_python:",
    "            import sys",
    '            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.'
    '{sys.version_info.micro}"',
    '            base_message += f" (Python {python_version})"']
# s317's own texts at night 161, read from `.rota/clickI_night161.db`:
# turn 2 sent start=540, turn 4 sent start=537. Both had end=560.
S317 = {
    540: "\n".join(["                    ) from None"]
                   + [x.replace("{blank}", "        ") for x in _BLOCK]),
    537: "\n".join(["                else:"] + LINES[537:541]
                   + [x.replace("{blank}", "") for x in _BLOCK]),
}
# The lines of each text that are the file's own lines, so the offer's text
# starts at the line before start for 537.
KEEP = {540: 540, 537: 536}


@pytest.mark.parametrize("start", [540, 537])
def test_s317_takes_the_offered_span_and_its_text_lands(tmp_path, start):
    sb = _developer(tmp_path, DECORATORS)
    said, offers = _refusal(sb, start=start, end=560, text=S317[start])
    assert ("Lines 515 to 560 hold start=%d and end=560 in whole statements "
            "of the body of callback." % start) in said
    assert "A write to start=515, end=560 replaces every line from 515 to 559." in said
    sent = ("To make your change there send start=515, end=560 with lines 515 to "
            "%d of the file, then your text." % (KEEP[start] - 1))
    assert sent in said
    held = [o for o in offers if o.said == sent]
    assert [(o.op, o.args["start"], o.args["end"]) for o in held] == [
        ("code.write", 515, 560)]
    assert held[0].args["text"] == "\n".join(LINES[515:KEEP[start]]) + "\n" + S317[start] + "\n"
    res = sb.call("code.write", **held[0].args)
    landed = (tmp_path / "wt" / "m.py").read_text().splitlines()
    ast.parse("\n".join(landed))
    # Only the seat's own span changes: the lines before it and after 560
    # are the file's own.
    assert landed[:KEEP[start]] == LINES[:KEEP[start]]
    assert landed[KEEP[start]:KEEP[start] + len(S317[start].splitlines())] == \
        S317[start].splitlines()
    assert landed[-(len(LINES) - 560):] == LINES[560:]
    # Frame 140's note names only what s317's own text drops from its own
    # span, the `if version is None:` check at line 547. It names no line
    # that the offer added around the text.
    assert res["dropped"] == ("This write removes or rewrites 1 statement that your text does "
                              "not hold: `if version is None:` at line 547.")


def test_a_cut_at_the_end_of_a_def_is_offered_the_statement_once(tmp_path):
    """The review of 50412ca8, finding 2: a cut in the last `return h(` of
    a def got "To replace f whole" twice and no span of the return."""
    src = ("def f(xs):\n    for x in xs:\n        w = 3\n    return h(\n"
           "        2,\n    )\n")
    sb = _developer(tmp_path, src)
    said, offers = _refusal(sb, start=4, end=6, text="        3,\n    )\n")
    assert said.count("To replace f whole send start=0, end=6.") == 1
    assert "Lines 3 to 6 hold start=4 and end=6 in whole statements of the body of f." in said
    assert "send start=3, end=6 with line 3 of the file, then your text." in said
    held = [o for o in offers if o.said.startswith("To make your change")]
    assert held[0].args["text"] == "    return h(\n        3,\n    )\n"
    assert sb.call("code.write", **held[0].args)
    assert "h(\n        3," in (tmp_path / "wt" / "m.py").read_text()


def test_the_new_span_facts_name_their_statements(tmp_path):
    """The review of 50412ca8, finding 3: a span fact with no type or name
    was held to its bounds only."""
    from rota.core import sandbox
    sb = _developer(tmp_path, DECORATORS)
    _refusal(sb, start=537, end=560, text=S317[537])
    named = [f for f in sb.ctx.facts if f.kind == "span" and dict(f.where).get("node")]
    spans = {(f.value, dict(f.where)["node"]) for f in named}
    assert {((515, 541), "If"), ((556, 560), "If"), ((537, 541), "Raise"),
            ((557, 558), "Import"), ((559, 560), "AugAssign")} <= spans, spans
    assert all(f["ok"] for f in sandbox.check_facts(sb, named))


def test_a_crossing_span_names_the_span_of_both_blocks(tmp_path):
    sb = _developer(tmp_path, DECORATORS)
    said, _ = _refusal(sb, start=537, end=560,
                       text="\n".join(LINES[537:560]) + "\n")
    assert said.startswith(
        "start=537, end=560 crosses from one block to another. start=537 is in "
        "the else block of elif (lines 537 to 541). end=560 is in the body of if "
        "(lines 557 to 560).")
    assert said.endswith("To replace callback whole send start=503, end=566.")


def test_s237_docstring_refusal_keeps_its_words(tmp_path):
    sb = _developer(tmp_path, TERMUI)
    said, offers = _refusal(sb, start=316, end=325,
                            text="    # Check for EOF at function entry.\n")
    assert said == (
        "start=316, end=325: start=316 falls inside docstring (lines 297 to 327 "
        "in code.source numbering). Line 316 is '        Added the "
        "``default_on_eof`` parameter.'. Line 324 is '    .. versionadded:: 4.0'. "
        "Line 325 is '        Added the `err` parameter.'. To replace docstring "
        "whole send start=297, end=327. To add after it send start=327, end=327.")
    assert [(o.said, o.args["start"], o.args["end"]) for o in offers] == [
        ("To replace docstring whole send start=297, end=327.", 297, 327),
        ("To add after it send start=327, end=327.", 327, 327)]
