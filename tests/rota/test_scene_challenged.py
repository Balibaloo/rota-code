"""
S5, a test at version 2 after an answered challenge.

The Developer challenges t1 with the criterion's words and the test's,
and the Tester replaces t1 under its stored id. The scene builds its state
and never asserts the same-refs door's refusal.

The second build is in `test_scene_challenged_again.py`.
"""
from __future__ import annotations

from rota.testkit import scenes
from tests.rota.scene_tests import make

NAME = "challenged"


def test_t1_is_at_version_2_and_green_on_the_same_commit(scene):
    conn = scene.conn
    t1 = conn.execute("SELECT version, body FROM tests WHERE id = 't1'").fetchone()
    assert (t1["version"], t1["body"]) == (2, scenes.TEST_BODY)
    head = conn.execute("SELECT head_commit FROM batches WHERE id = 'b1'").fetchone()[0]
    # The harness keeps one run of a test at a commit, so the pass of
    # version 2 replaced the fail of version 1.
    assert [r["result"] for r in conn.execute(
        "SELECT result FROM test_runs WHERE batch_id = 'b1' AND test_id = 't1' "
        "AND commit_sha = ?", (head,))] == ["pass"]
    assert conn.execute("SELECT status FROM messages WHERE id = ?",
                        (scene.ids["challenge"],)).fetchone()[0] != "open"


def test_the_challenge_wake_pushes_the_signature_of_the_callable_that_raised(scene):
    """Frame 223, night 153: no Tester saw the parameters of the callable
    that raised. The scene's run failed on an assertion, so its wake holds
    no traceback frame and no push. The same wake with a frame in the
    project's source pushes that definition's `def` line under its key."""
    from rota.core import runner
    from rota.core.sandbox import build
    from rota.core.scheduler import Wake
    from rota.roles import prompts

    conn = scene.conn
    key = "[code.source src/billing/charges.py::prorate]"
    recorded = scenes.wake_prompt(scene, "tester", "message")
    assert "[code.source " not in recorded

    wake = Wake(role="tester", kind="message", message_id=scene.ids["challenge"],
                detail="challenge")
    lines = (scene.repo.root / "src/billing/charges.py").read_text(
        encoding="utf-8").splitlines()
    at = next(i for i, s in enumerate(lines, 1) if "raise ValueError" in s)
    frame = (f'  File "src\\billing\\charges.py", line {at}, in prorate\n'
             f'    raise ValueError("period must be positive")\n'
             f"ValueError: period must be positive\n")

    def prompt(output: str) -> str:
        inbound = runner.resolve_inbound(conn, wake)
        for row in inbound["resolved_refs"].values():
            if isinstance(row, dict) and row.get("table") == "tests":
                row["last_run"] = {"result": "fail", "output_tail": output}
        sb = build("tester", conn, batch_id="b1", mode="challenge",
                   allow=prompts.mode_tools("tester", "challenge"))
        return runner.build_prompt("tester", sb, wake, {}, "MODE: challenge",
                                   inbound)[1]

    pushed = prompt("E   ValueError\n" + frame)
    assert key in pushed
    assert "def prorate(amount_cents, days_used, days_in_period):" in pushed
    assert pushed.count("[code.source ") == 1
    # Pass 1b: the lines from the guard to the raise, beside the signature.
    raised = pushed.split("[the lines that raised]\n", 1)[1]
    assert raised.startswith("    if days_in_period <= 0:\n")
    assert 'raise ValueError("period must be positive")' in raised
    assert f"raised at: lines {at - 1} to {at}" in pushed
    assert key not in prompt("E   ValueError\nValueError: period must be positive\n")
    # Pass 2: a frame on a line that is no `raise` pushes nothing. Night
    # 142's `strip_ansi` frame was a `return`.
    returns = frame.replace(f"line {at},", f"line {at + 1},")
    assert "[code.source " not in prompt("E   TypeError\n" + returns)


def _challenge_prompt(scene, output: str) -> str:
    """The Tester's challenge wake of the scene, with `output` as the run."""
    from rota.core import runner
    from rota.core.sandbox import build
    from rota.core.scheduler import Wake
    from rota.roles import prompts

    wake = Wake(role="tester", kind="message", message_id=scene.ids["challenge"],
                detail="challenge")
    inbound = runner.resolve_inbound(scene.conn, wake)
    for row in inbound["resolved_refs"].values():
        if isinstance(row, dict) and row.get("table") == "tests":
            row["last_run"] = {"result": "fail", "output_tail": output}
    sb = build("tester", scene.conn, batch_id="b1", mode="challenge",
               allow=prompts.mode_tools("tester", "challenge"))
    return runner.build_prompt("tester", sb, wake, {}, "MODE: challenge",
                               inbound)[1]


def test_a_raise_in_a_method_pushes_the_methods_def_line(scene):
    """Review 1 of frame 223, medium 2: a raise inside a method shows the
    method's `def` line, not the class header. A nested closure still shows
    the outer function, as `version_option` and its `callback` do."""
    from pathlib import Path

    conn = scene.conn
    tree = Path(conn.execute(
        "SELECT worktree FROM batches WHERE id = 'b1'").fetchone()[0])
    rel = "src/billing/ledger_book.py"
    source = ('class Book:\n'
              '    """A ledger."""\n'
              '\n'
              '    def post(self, cents, *, currency=None):\n'
              '        """Post an amount."""\n'
              '        def check():\n'
              '            if currency is None:\n'
              '                raise LookupError("no currency")\n'
              '        check()\n'
              '\n'
              '\n'
              'def total(book, *, scale=1):\n'
              '    """Sum the book."""\n'
              '    def each(x):\n'
              '        if x < 0:\n'
              '            raise ValueError("negative")\n'
              '    return each\n')
    (tree / rel).write_bytes(source.encode("utf-8"))
    conn.execute("INSERT INTO code_index (grain, grain_kind) VALUES (?, 'path')", (rel,))
    try:
        method = _challenge_prompt(scene, (
            f'  File "{rel}", line 8, in check\n'
            '    raise LookupError("no currency")\nLookupError: no currency\n'))
        assert f"[code.source {rel}::Book.post]" in method
        assert "    def post(self, cents, *, currency=None):" in method
        assert "class Book:" not in method
        raised = method.split("[the lines that raised]\n", 1)[1]
        assert raised.startswith("            if currency is None:\n")

        closure = _challenge_prompt(scene, (
            f'  File "{rel}", line 16, in each\n'
            '    raise ValueError("negative")\nValueError: negative\n'))
        assert f"[code.source {rel}::total]" in closure
        assert "def total(book, *, scale=1):" in closure
    finally:
        conn.execute("DELETE FROM code_index WHERE grain = ?", (rel,))
        (tree / rel).unlink()


globals().update(make(NAME, end=["critic|tick:review|b1"], attempts=[], asks=[]))


def test_a_tester_wake_pushes_the_source_of_the_criterions_surface(scene):
    """Frame 143, night 154: s199 asserted `confirm(...) == "y"` with no line
    of `confirm` in its prompt. The wake of a criterion with a surface pushes
    that surface's `def` line and its return lines under one key. A surface
    that does not resolve pushes nothing."""
    conn = scene.conn
    key = "[surface src/billing/charges.py::prorate]"
    conn.execute("UPDATE criteria SET surface_refs = ?",
                 ('["src/billing/charges.py::prorate"]',))
    pushed = _challenge_prompt(scene, "E   AssertionError\n")
    assert key in pushed
    block = pushed.split(key + "\n", 1)[1]
    assert "def prorate(amount_cents, days_used, days_in_period):" in block
    assert "    return " in block
    assert pushed.count("[surface ") == 1
    conn.execute("UPDATE criteria SET surface_refs = ?",
                 ('["src/billing/charges.py::no_such_name"]',))
    assert "[surface " not in _challenge_prompt(scene, "E   AssertionError\n")
