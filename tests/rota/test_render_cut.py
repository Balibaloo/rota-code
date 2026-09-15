"""A truncated source span says the line the cut fell at (finding 77)."""
from rota.core.runner import _render


def test_a_cut_span_names_the_line_and_the_next_call():
    """Night 74 (2026-09-15): the 9B read a 207-line function six times and
    saw the same first 6000 characters each time. The note names the line
    the cut fell at and the call that fetches the rest."""
    body = "".join(f"line {i}: " + "x" * 40 + chr(10) for i in range(300))
    result = {"path": "src/a.py", "start": 420, "end": 627, "lines": 627, "text": body}
    out = _render(result, limit=2000)
    assert "TRUNCATED after 2000" in out
    assert "The cut fell at line 4" in out and "code.source(path='src/a.py', start=4" in out, out[-300:]
    assert "end=627)" in out
