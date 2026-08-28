"""
Chaos, loop 5: staying true, hurt the ways operations would hurt it.

The ledger names two injuries. A refresh killed mid-reindex must leave the
world before or after, never between -- and the first draft of this test
found "between" existed: the swap ran on an autocommit connection, so the
DELETE landed instantly and a kill during the inserts left a half-empty
index that read as a mostly-deleted tree, reopening every area at once.
And a survey attested against a tree that moved mid-session must not stamp
the new tree's hash over an old tree's reading -- the record would claim
currency for content nobody surveyed, which is the freshness view lying in
the exact direction it exists to prevent.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build as build_sandbox
from rota.onboarding import indexer
from rota.roles.api import area_content_hash
from rota.testkit import gitfixture


@pytest.fixture
def repo(tmp_path):
    return gitfixture.make(tmp_path, name="staytrue_repo")


class _DiesMidWrite:
    """A connection that survives the parse and dies during the swap."""

    def __init__(self, conn, after: int):
        self._conn = conn
        self._after = after
        self._writes = 0

    def execute(self, sql, *args):
        if sql.lstrip().upper().startswith("INSERT INTO CODE_INDEX"):
            self._writes += 1
            if self._writes > self._after:
                raise ConnectionError("the machine went away mid-swap")
        return self._conn.execute(sql, *args)

    def __getattr__(self, name):
        return getattr(self._conn, name)


def test_a_reindex_killed_mid_swap_never_happened(tmp_path, repo):
    """The old index survives a death during the write phase whole -- the
    swap is a transaction, not a hopeful sequence."""
    conn = init_db(tmp_path / "rota.db")
    indexer.build(conn, repo.root)
    before = {r["grain"] for r in conn.execute("SELECT grain FROM code_index")}
    assert before, "the fixture indexed something"

    with pytest.raises(ConnectionError):
        indexer.build(_DiesMidWrite(conn, after=3), repo.root)

    after = {r["grain"] for r in conn.execute("SELECT grain FROM code_index")}
    assert after == before, (
        "a killed reindex left a world in between: "
        f"{len(before)} grains before, {len(after)} after")


def test_an_attest_stamps_the_tree_the_session_read(tmp_path, repo):
    """The tree moves between the session's read and its attest. The record
    must carry the hash of what was read, so the freshness view reopens the
    area instead of crediting a survey of content nobody saw."""
    from rota.onboarding import boot

    conn = init_db(tmp_path / "rota.db")
    boot.onboard(conn, repo.root)      # the partition assigns areas
    area = conn.execute(
        "SELECT area FROM code_index WHERE area LIKE 'src/%' "
        "AND grain_kind = 'path' LIMIT 1").fetchone()["area"]
    hash_at_wake = area_content_hash(conn, area)

    sb = build_sandbox("terminologist", conn, mode="survey", area=area)
    # The session does its reading -- the half that happens before the world
    # moves, and what makes the attest legal.
    sb.call("code.area")
    rel = conn.execute(
        "SELECT grain FROM code_index WHERE area = ? AND grain_kind = 'path' "
        "LIMIT 1", (area,)).fetchone()["grain"]
    repo.edit(repo.root, rel, "# the tree moved\n" +
              (repo.root / rel).read_text(encoding="utf-8"))
    repo.commit_in(repo.root, "moved under a running survey")
    indexer.build(conn, repo.root)
    assert area_content_hash(conn, area) != hash_at_wake, \
        "the fixture's move must actually change the area"

    sb.call("surveys.attest", outcome="none_found", citations=[rel])
    for table, rid, payload, *_ in sb.ctx.writes:
        if table == "survey_records":
            assert payload["area_hash"] == hash_at_wake, (
                "the attest stamped the moved tree over the one the session "
                "read -- claiming currency for content nobody surveyed")
            break
    else:
        pytest.fail("no survey record staged")
