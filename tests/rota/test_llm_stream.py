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
