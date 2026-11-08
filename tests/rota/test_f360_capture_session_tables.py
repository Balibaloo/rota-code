"""
Frame 360, pass 2e: a case counts the rows a door writes with no receipt.

The register case `L1-AR-run-the-code-at-a-claim` recorded 0 of 5 on
qwen3:8b. A replay with `-n 0` showed that the `code.run` door ran in all
5 runs, returned code 0, and landed a `claim_runs` row. The case still
counted 0, because `capture` read the receipts only, and `session_commit`
gives no receipt to a table that is not an artefact table. An earlier spy
saw no call because xdist ran the case in a worker process.
"""
from __future__ import annotations

import re
from pathlib import Path

from rota.core.db import ARTEFACT_TABLES, REFS_TABLE
from rota.testkit.fixtures import SESSION_TABLES, capture
from tests.rota.test_f360_h1_claim_run import (  # noqa: F401
    A2_RUN3, _architect, _land, project)

API = Path(__file__).resolve().parents[2] / "rota" / "roles" / "api.py"


def test_capture_counts_the_claim_run_row_of_the_session(project):
    db, _ = project
    sb = _architect(db)
    sb.ctx.session_id = "s_claim_run"

    sb.call("code.run", text=A2_RUN3)
    _land(db, sb, sid="s_claim_run")

    delta = capture(db, "s_claim_run", {})
    assert len(delta.writes.get("claim_runs", [])) == 1, delta.writes
    assert delta.rows["claim_runs"][0]["program"] == A2_RUN3


def test_capture_reads_no_claim_run_row_of_another_session(project):
    db, _ = project
    sb = _architect(db)
    sb.ctx.session_id = "s_claim_run"

    sb.call("code.run", text=A2_RUN3)
    _land(db, sb, sid="s_claim_run")

    assert "claim_runs" not in capture(db, "s_other", {}).writes


def test_every_door_table_with_no_receipt_is_read_by_capture():
    """A door that stages a row in a new table with no receipt makes the
    same blind case. `messages` and `ruled_refs` have their own reads in
    `capture`, and a refs row is receipted under its source row."""
    staged = set(re.findall(r'ctx\.writes\.append\(\(\s*"([a-z_]+)"',
                            API.read_text(encoding="utf-8")))
    assert "claim_runs" in staged, sorted(staged)
    unread = staged - set(ARTEFACT_TABLES) \
        - {REFS_TABLE, "messages", "ruled_refs"} - set(SESSION_TABLES)
    assert not unread, sorted(unread)
