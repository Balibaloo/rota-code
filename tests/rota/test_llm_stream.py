"""The streamed reply's two guards: the socket timeout for a silent
connection, and the wall clock for one that keeps trickling."""
from __future__ import annotations

import json
import time
from types import SimpleNamespace

import pytest

from rota.llm.llm import _consume_stream


def _live():
    return SimpleNamespace(token=lambda s: None, close=lambda s: None)


def _chunks(n, pause=0.0):
    for i in range(n):
        if pause:
            time.sleep(pause)
        yield json.dumps({"message": {"role": "assistant", "content": f"t{i} "},
                          "done": i == n - 1, "eval_count": n}).encode()


def test_a_stream_within_its_deadline_is_joined():
    body = _consume_stream(_chunks(3), _live(), deadline=time.monotonic() + 10)
    assert body["message"]["content"] == "t0 t1 t2 "
    assert body["done"] is True


def test_a_stream_past_its_deadline_is_a_timeout():
    """Night 27 and seat1 (2026-09-12): one generation held a card for two
    hours on the 3080 and twenty-five minutes on the Titan. The socket
    timeout never tripped because bytes kept trickling."""
    with pytest.raises(TimeoutError, match="ran past the time allowed"):
        _consume_stream(_chunks(50, pause=0.01), _live(), deadline=time.monotonic() + 0.05)


def test_a_cycle_of_lines_three_times_over_is_repeating():
    """clickI night 40 (2026-09-13): a reconcile reply cycled five
    `code.source` calls for 84 seconds to the output cap."""
    from rota.llm.llm import _cycling
    line = "TOOL: code.source(path='click/utils.py', start=0, end=400)"
    assert _cycling([line] * 3)
    cycle = [f"TOOL: code.source(path='click/{n}.py', start=0, end=400)" for n in ("a", "b", "c", "d", "e")]
    assert not _cycling(cycle * 2), "twice is a re-read; three times is a loop"
    assert _cycling(cycle * 3)
    assert not _cycling(["x)"] * 6), "short lines never count"


def _pieces(pieces, pulled):
    """Each piece is one streamed chunk. `pulled` records the chunks the
    reader took, so a test sees where the stream was left."""
    for i, piece in enumerate(pieces):
        pulled.append(i)
        yield json.dumps({"message": {"role": "assistant", "content": piece},
                          "done": False}).encode()
    pulled.append(len(pieces))
    yield json.dumps({"message": {"role": "assistant", "content": ""},
                      "done": True}).encode()


def test_an_invented_result_after_a_call_stops_the_stream_at_its_head():
    """Night 145's s117#4 (frame 232): one `TOOL:` line, a blank line, then
    `OK code.source -> ["import click...` as one line that never ends, 8,269
    tokens. The head of the line is enough, so the rule tests the partial
    line and the stream is left on the chunk that completes `->`."""
    from rota.llm.toolproto import INVENTED_RESULT
    pulled = []
    pieces = ['TOOL: code.source("a.py", 0, 40)\n', "\n", "OK code", ".source -",
              "> [", *(["'import click', "] * 200)]
    out = _consume_stream(_pieces(pieces, pulled), _live())
    assert out.get("done_reason") == "invented_result"
    text = out["message"]["content"]
    assert text == 'TOOL: code.source("a.py", 0, 40)\n\nOK code.source -> ['
    assert INVENTED_RESULT.match(text.splitlines()[-1])
    assert len(pulled) < 10, pulled


def test_result_like_lines_with_no_call_before_them_run_to_the_end():
    """A clean act body or prose can start a line with `OK`. With no `TOOL:`
    line before it, no result was invented, so the stream runs on."""
    from rota.llm.toolproto import INVENTED_RESULT
    assert INVENTED_RESULT.match("OK code.write -> done"), \
        "the line matches the rule, so only the missing call keeps it"
    pulled = []
    pieces = ["OK, the tests pass.\n", "OK code.write -> done\n",
              *[f"line {n} of the plain reply\n" for n in range(20)], "done"]
    out = _consume_stream(_pieces(pieces, pulled), _live())
    assert out.get("done_reason") != "invented_result"
    assert out["message"]["content"] == "".join(pieces)
    assert len(pulled) == len(pieces) + 1


def test_calls_with_no_result_line_run_to_the_end():
    """Three calls and no result line: nothing is invented, so every call
    stays in the reply."""
    from rota.llm.toolproto import INVENTED_RESULT
    lines = ['TOOL: code.source(path="a.py", start=0, end=40)\n',
             'TOOL: code.probe(expr="a.f(1)")\n',
             "TOOL: tests.run()\n", "done"]
    assert not any(INVENTED_RESULT.match(l) for l in lines)
    pulled = []
    out = _consume_stream(_pieces(lines, pulled), _live())
    assert out.get("done_reason") != "invented_result"
    assert out["message"]["content"] == "".join(lines)
    assert len(pulled) == len(lines) + 1
