"""
S5, a test at version 2 after an answered challenge.

The Developer challenges t1 with the criterion's words and the test's,
and the Tester replaces t1 under its stored id. The scene builds its state
and never asserts the same-refs door's refusal.
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


globals().update(make(NAME, end=["critic|tick:review|b1"], attempts=[]))
