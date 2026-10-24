"""
A rewrite is not a removal, and a route names only a call the mode holds
(frame 283, pass 8).

Night 163: s221 wrote `return False` over a bare `return` under `clear`
with a span write. The note door named `return` as dropped, and every
commit after it was refused. The whole-file branch already counts each
statement kind under its owner (25fa18ef), and the span branch did not.
s252, in the Developer's `batch_start` mode, then read a refusal that
named `msg.escalate_architect`, a tool that mode does not hold.
"""
from __future__ import annotations

import pytest

from rota.core.sandbox import build
from rota.roles import api, prompts
from tests.rota.test_frame283_removal_on_ruling import (  # noqa: F401
    ECHO, MESSAGE, PATH, _developer, _git, db)

# The body of `show_version` in the fixture: start=592, end=597, as the
# span door reads them.
GUARD = ("        if not value or ctx.resilient_parsing:\n"
         "            return\n")
REWRITE = ("        if not value or ctx.resilient_parsing:\n"
           "            return False")
KEEP = "To keep the change, send msg.escalate_architect"


def _sandbox(db, mode: str):
    return build("developer", db, batch_id="bg_3", mode=mode,
                 allow=prompts.mode_tools("developer", mode))


def test_a_span_write_that_rewrites_a_bare_return_opens_no_note(db, tmp_path):
    """s221's shape: one `Return` becomes one `Return` with a value under
    the same owner. The kind count holds, so no note opens and the commit
    in the same session lands."""
    sb, root = _developer(db, tmp_path)
    before = (root / PATH).read_text(encoding="utf-8")
    assert GUARD in before
    out = sb.call("code.write", path=PATH, start=592, end=594, text=REWRITE)
    assert "dropped" not in out
    top, cut, rest = before.partition("def show_version")
    assert (root / PATH).read_text(encoding="utf-8") == (
        top + cut + rest.replace(GUARD, REWRITE + "\n", 1))
    assert PATH not in api._open_notes(sb.ctx)
    head = _git(root, "rev-parse", "HEAD")
    sb.begin_reply()
    assert sb.call("code.commit", message="clear returns False")["committed"] is True
    assert _git(root, "rev-parse", "HEAD") != head


def test_a_span_write_that_removes_one_statement_and_rewrites_another(db, tmp_path):
    """The `Expr` count under `show_version` falls by one, so the note
    opens and names `ctx.exit()`. A fallen count keeps today's note whole,
    so the note names the rewritten `return` too."""
    sb, _root = _developer(db, tmp_path)
    out = sb.call("code.write", path=PATH, start=592, end=597,
                  text=REWRITE + "\n\n        echo(callback(ctx), color=ctx.color)")
    assert out["dropped"] == ("This write removes or rewrites 2 statements that "
                              "your text does not hold: `return` at line 593, "
                              "`ctx.exit()` at line 596.")
    assert PATH in api._open_notes(sb.ctx)


def test_the_refusal_in_batch_start_names_no_escalation(db, tmp_path):
    """s252's shape: the Developer's `batch_start` mode lacks
    msg.escalate_architect, so the refusal names the write route alone."""
    _sb, _root = _developer(db, tmp_path)
    sb = _sandbox(db, "batch_start")
    assert "dropped" in sb.call("code.write", path=PATH, start=540, end=555, text=ECHO)
    sb.begin_reply()
    with pytest.raises(ValueError) as err:
        sb.call("code.commit", message=MESSAGE)
    msg = str(err.value)
    assert "msg.escalate_architect" not in msg
    assert msg.endswith("A note does not allow a removal or a rewrite. To undo "
                        "the change, put the line back with code.write, then "
                        "commit in your next reply.")


def test_the_refusal_in_tests_failing_keeps_the_escalation(db, tmp_path):
    """The `tests_failing` mode holds msg.escalate_architect, and no
    escalation went this session, so the route keeps it."""
    sb, _root = _developer(db, tmp_path)
    assert "dropped" in sb.call("code.write", path=PATH, start=540, end=555, text=ECHO)
    sb.begin_reply()
    with pytest.raises(ValueError) as err:
        sb.call("code.commit", message=MESSAGE)
    assert KEEP in str(err.value)
