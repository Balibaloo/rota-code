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


@pytest.mark.parametrize("start", [540, 537])
def test_a_span_of_s317_is_offered_the_span_that_holds_its_lines(tmp_path, start):
    sb = _developer(tmp_path, DECORATORS)
    said, offers = _refusal(sb, start=start, end=560,
                            text="\n".join(LINES[start:560]) + "\n")
    assert ("Lines 515 to 560 hold start=%d and end=560 in whole statements "
            "of the body of callback." % start) in said
    assert "To replace lines 515 to 560 send start=515, end=560." in said
    held = [o for o in offers if o.said.startswith("To replace lines 515 to 560")]
    assert [(o.op, o.args["start"], o.args["end"]) for o in held] == [
        ("code.write", 515, 560)]
    assert held[0].args["text"] is api.INVENT
    # The offered span with the right body: the block that appends to
    # base_message before it exists, lines 541 to 546, goes.
    body = "\n".join(LINES[515:541] + LINES[547:560]) + "\n"
    assert sb.call("code.write", path="m.py", start=515, end=560, text=body)
    landed = (tmp_path / "wt" / "m.py").read_text()
    ast.parse(landed)
    assert landed.count('base_message += f" (Python {python_version})"') == 1


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
