"""One wording for every cut, and every cut names a call the seat can make."""
import re

from rota.core import runner as R
from rota.core.runner import _render

# What was cut, how much is not shown, then the call that returns it.
FORM = re.compile(r"CUT [^:]+: [\d,]+ of [\d,]+ (characters|rows) are not shown\. \S")


def _cuts() -> dict[str, str]:
    """One cut of each kind, from the site that writes it."""
    rows = [{"id": f"d{i}", "author": "architect",
             "headline": f"the scope ruling {i}", "supersedes": None}
            for i in range(40)]
    span = {"path": "src/a.py", "start": 420, "end": 627, "lines": 627,
            "text": "".join(f"line {i}: " + "x" * 40 + chr(10) for i in range(300))}
    return {
        "a capped result": _render({"body": "y" * 9000}, 2000),
        "a capped span": _render(span, 2000),
        "a cut wake": R._render_cut("W" * 9000, 2000),
        "a cut exchange": R._exchange_cut("E" * 9000, 2000),
        "a budgeted push": R._budget_decision_hits({"scope": rows}, 2000)["not shown"][0],
    }


def test_a_cut_span_names_the_line_and_the_next_call():
    """Night 74 (2026-09-15): the 9B read a 207-line function six times and
    saw the same first 6000 characters each time. The note names the line
    the cut fell at and the call that fetches the rest."""
    body = "".join(f"line {i}: " + "x" * 40 + chr(10) for i in range(300))
    result = {"path": "src/a.py", "start": 420, "end": 627, "lines": 627, "text": body}
    out = _render(result, limit=2000)
    assert "CUT the result:" in out and "characters are not shown" in out, out[-300:]
    assert "The cut fell at line 4" in out and "code.source(path='src/a.py', start=4" in out, out[-300:]
    assert "end=627)" in out


def test_one_wording_for_every_cut():
    """
    Six wordings said the same thing (frame 46's design review, section 2.6,
    2026-09-20). A seat that reads two cuts in one prompt read two forms, and
    neither form was the one its brief describes. One form now, from
    `cut_note`: a capped result, a cut transcript and a budgeted push all say
    what was cut, how much is not shown, and what to call.
    """
    for kind, cut in _cuts().items():
        assert FORM.search(cut), f"{kind} does not use the one form: {cut[-200:]}"


def test_no_cut_offers_a_range_the_seat_does_not_have():
    """
    Four of eighteen strings named a call that works. A pushed read was told to
    ask for the next range, and a push has no range to ask for, so the recovery
    sentence named nothing. A cut now names an op, or says plainly that nothing
    returns the rest.
    """
    for kind, cut in _cuts().items():
        assert "next range" not in cut, f"{kind} offers a range it does not have"
        call = cut.split("are not shown. ", 1)[1].strip()
        assert call.startswith("Nothing returns") or re.search(r"[a-z_]+\.[a-z_]+", call), \
            f"{kind} names no call and does not say that none exists: {call}"
        assert call.endswith("."), f"{kind} ends mid-sentence: {call}"
