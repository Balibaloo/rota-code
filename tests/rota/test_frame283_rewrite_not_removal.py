"""
A rewrite is not a removal, and a route names only a call the mode holds
(frame 283, pass 8).

Night 163: s221 wrote `return False` over a bare `return` under `clear`
with a span write. The note door named `return` as dropped, and every
commit after it was refused. The whole-file branch already counts each
statement kind under its owner (25fa18ef), and the span branch did not.
s252, in the Developer's `batch_start` mode, then read a refusal that
named `msg.escalate_architect`, a tool that mode does not hold.
Frame 339: the route to keep the change is the commit of the next
reply, which every mode holds.
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
KEEP = ("To keep the change, commit in your next reply. The Architect "
        "then judges the removal before the batch merges.")


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
    """The note opens and names `ctx.exit()`. Pass 8c: the owner's count
    of statements falls, so no place pairs, and the note names the
    rewritten `return` too (review 8's finding 5)."""
    sb, _root = _developer(db, tmp_path)
    out = sb.call("code.write", path=PATH, start=592, end=597,
                  text=REWRITE + "\n\n        echo(callback(ctx), color=ctx.color)")
    assert out["dropped"] == ("This write removes or rewrites 2 statements that "
                              "your text does not hold: `return` at line 593, "
                              "`ctx.exit()` at line 596.")
    assert PATH in api._open_notes(sb.ctx)


@pytest.mark.parametrize("mode,escalated", [
    ("batch_start", False),
    ("tests_failing", False),
    ("tests_failing", True),
])
def test_the_refusal_names_the_commit_route_in_every_mode(db, tmp_path, mode, escalated):
    """s252's shape: the Developer's `batch_start` mode lacks
    msg.escalate_architect, and review 8's finding 3 refuses a second
    escalation in one session. Frame 339: the commit of the next reply
    keeps the change for the Architect, and every mode holds code.commit,
    so the route names that commit and no escalation. The commit lands."""
    _sb, root = _developer(db, tmp_path)
    sb = _sandbox(db, mode)
    if escalated:
        sb.call("msg.escalate_architect", refs=["cr_3"])
        sb.begin_reply()
    assert "dropped" in sb.call("code.write", path=PATH, start=540, end=555, text=ECHO)
    with pytest.raises(ValueError) as err:
        sb.call("code.commit", message=MESSAGE)
    msg = str(err.value)
    assert "msg.escalate_architect" not in msg
    assert msg.endswith(KEEP), msg
    sb.begin_reply()
    out = sb.call("code.commit", message=MESSAGE)
    assert out["committed"] is True
    assert [w[2]["status"] for w in sb.ctx.writes if w[0] == "touch_strays"] == ["open"]


# Review 8's probe file: two owners, nine lines, in code.write numbering.
SMALL = ["def clear(self, x):",
         "    if x:",
         "        self.log(x)",
         "    validate(x)",
         "    return",
         "",
         "def other(x):",
         "    go(x)",
         "    return x"]
LOGS = ["def f(x):", "    log(x)", "    log(x, 2)", "    return x"]


@pytest.mark.parametrize("start,stop,new,named", [
    # E0, s221's shape: the new statement at the same place holds `return`.
    (4, 5, ["    return False"], None),
    # E4: `print(x)` at the same place does not hold `validate`.
    (3, 4, ["    print(x)"], "`validate(x)` at line 3"),
    # E5: a second `self.log(x)` takes the place of `validate(x)`.
    (2, 4, ["        self.log(x)", "        self.log(x)"], "`validate(x)` at line 3"),
    # E6: `pass` is no statement the walk counts, so `return` is dropped.
    (4, 5, ["    pass"], "`return` at line 4"),
    # E8 of the re-check: with `log(x)` gone, `log(x, 2)` moves into its
    # place and holds its tokens. The owner's count falls, so no pairing.
    (1, 3, ["    log(x, 2)"], "`log(x)` at line 1"),
])
def test_a_rewrite_is_paired_by_its_place_under_the_owner(start, stop, new, named):
    """Pass 8b, review 8's finding 1: a held count of a kind let
    `validate(x)` go with no note. A dropped statement is a rewrite only
    when the new statement at its place under its owner holds its tokens."""
    old = LOGS if "log(x, 2)" in new[0] else SMALL
    note = api._drop_note(old, start, stop, chr(10).join(new), lines_out=[])
    if named is None:
        assert note is None
    else:
        assert named in note


# Night 165, walk 2, bg_2: `clear` as the Developers found it, in code.write
# numbering. The bare `return` is line 4.
CLEAR = ["import sys",
         "",
         "def clear() -> None:",
         "    if not isatty(sys.stdout):",
         "        return",
         "",
         "    echo(\"[2J\", nl=False)",
         "",
         "",
         "def other(x):",
         "    return x"]
CLEARED = ["def clear() -> bool:",
           "    if not isatty(sys.stdout):",
           "        return False",
           "",
           "    echo(\"[2J\", nl=False)",
           "",
           "    return True"]


@pytest.mark.parametrize("start,stop", [(2, 7), (2, 8), (3, 7)])
def test_a_rewrite_beside_an_added_statement_opens_no_note(start, stop):
    """W-B of night 165: `return` became `return False`, and `return True`
    was added after the `echo` line. The owner's count grew from 3 to 4.
    The new statement at the old place holds `return`, so no note opens."""
    new = CLEARED if start == 2 else CLEARED[1:]
    assert api._drop_note(CLEAR, start, stop, chr(10).join(new),
                          lines_out=[]) is None


def test_the_whole_file_write_of_the_night_opens_no_note():
    """The same `clear` as a whole-file write opens no note."""
    full = CLEAR[:2] + CLEARED + ["", ""] + CLEAR[9:]
    assert api._whole_lost(CLEAR, chr(10).join(full), None, []) is None


def test_a_return_rewritten_with_one_added_return_opens_no_note():
    """`return` to `return False` plus an added `return True`."""
    old = ["def f(x):", "    if x:", "        return", "    go(x)"]
    new = ["    if x:", "        return False", "    go(x)", "    return True"]
    assert api._drop_note(old, 1, 4, chr(10).join(new), lines_out=[]) is None


def test_a_removal_beside_an_added_statement_opens_a_note():
    """Review W-B, finding 1: with `log(x)` gone, `log(x, 2)` moves into
    its place, and two added statements grow the count. The next old
    statement also fits the place, so the place does not pair."""
    new = ["    log(x, 2)", "    z()", "    w()", "    return x"]
    note = api._drop_note(LOGS, 1, 4, chr(10).join(new), lines_out=[])
    assert "`log(x)` at line 1" in note


@pytest.mark.parametrize("old,new", [
    (["def f(a, x):", "    a(x)"], ["    log(a, x)", "    c()"]),
    (["def f(y):", "    return"], ["    return y", "    stop()"]),
])
def test_a_rewrite_that_holds_the_old_tokens_beside_an_add_is_accepted(old, new):
    """Review W-B, finding 2, accepted: each new line holds the old
    statement's tokens, and no next old statement fits its place."""
    assert api._drop_note(old, 1, 2, chr(10).join(new), lines_out=[]) is None


TAIL = ["def f(x):", "    if x:", "        log(x)", "        log(x, 2)",
        "        go(x)", "        return x", "    done(x)"]


def test_a_tail_drop_beside_added_statements_keeps_the_tail_note():
    """Review W-B, finding 3: the text stops at `return x`, drops `done(x)`,
    and adds `z()` and `w()`. The tail note stays, and the shifted
    `log(x)` is named."""
    new = ["    if x:", "        log(x, 2)", "        z()", "        w()",
           "        return x"]
    note = api._drop_note(TAIL, 1, 7, chr(10).join(new), lines_out=[])
    assert note.startswith("This write drops 1 line that came after "
                           "`return x`, from `done(x)`.")
    assert "`log(x)` at line 2" in note


def test_a_tail_line_rewritten_at_its_place_clears_the_tail_note():
    """Review W-B, finding 3, pinned as the door does it: `done(x)` moves
    above `return x` as `done(x, 1)`, at its old place under the owner.
    The place pairs, so the tail note clears."""
    new = ["    if x:", "        log(x)", "        log(x, 2)", "        go(x)",
           "        z()", "        done(x, 1)", "        return x"]
    assert api._drop_note(TAIL, 1, 7, chr(10).join(new), lines_out=[]) is None
