"""Frame 306, W-C1 of night 165: the pass door skips a retired criterion.

Night 165, walk 3: s412 retired crit_2 and crit_3 of item 3 on his m244.
The Critics s415 to s417 then could not pass bg_3. The door said
"crit_2_format_invalid_bytes, crit_3_format_default_full_path have no
line", because it still counted the retired rows.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.runner import push_working_set
from rota.core.sandbox import build
from rota.roles.api import RETIRED_KEY
from tests.rota.test_verdict_lines import _git, a_batch_repo

LIVE = "crit_1_format_basename"
RETIRED = ("crit_2_format_invalid_bytes", "crit_3_format_default_full_path")
LINE = "    return os.path.basename(filename)"


@pytest.fixture
def bg_3(tmp_path):
    """bg_3 with one live criterion and the two that s412 retired."""
    repo = a_batch_repo(tmp_path, LINE)
    head = _git(repo, "rev-parse", "HEAD").strip()
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i3','the item','in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk3','i3','the ticket')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "(?, 'tk3', 'format_filename returns the basename')", (LIVE,))
    for cid in RETIRED:
        conn.execute("INSERT INTO criteria (id, ticket_id, text, retired_by) "
                     "VALUES (?, 'tk3', ?, 'r_m244')",
                     (cid, f"the words of {cid}"))
    conn.execute("INSERT INTO batches (id, item_id, status, worktree, "
                 "head_commit) VALUES ('bg_3', 'i3', 'running', ?, ?)",
                 (repo, head))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('bg_3', 'tk3')")
    conn.commit()
    return conn


def test_s415_pass_names_the_live_criterion_only_and_lands(bg_3):
    sb = build("critic", bg_3, batch_id="bg_3", mode="review")
    lines = {LIVE: LINE.strip()}
    # The first pass of a session is held once (frame 201, pass 3). The
    # hold must not name a retired criterion.
    with pytest.raises(ValueError) as held:
        sb.call("verdicts.emit", batch_id="bg_3", result="pass", lines=lines)
    assert "before the pass lands, answer for" in str(held.value)
    assert not any(cid in str(held.value) for cid in RETIRED)
    out = sb.call("verdicts.emit", batch_id="bg_3", result="pass",
                  lines=lines)
    assert out["result"] == "pass"
    assert [w for w in sb.ctx.writes if w[0] == "verdicts"]


def test_a_line_for_a_retired_criterion_is_refused(bg_3):
    sb = build("critic", bg_3, batch_id="bg_3", mode="review")
    with pytest.raises(ValueError) as exc:
        sb.call("verdicts.emit", batch_id="bg_3", result="pass",
                lines={LIVE: LINE.strip(), RETIRED[0]: LINE.strip()})
    assert f"{RETIRED[0]!r} is not a criterion of batch bg_3" in str(exc.value)


def test_criteria_load_lists_the_live_criterion(bg_3):
    sb = build("critic", bg_3, batch_id="bg_3", mode="review")
    rows = sb.call("criteria.load")
    assert [r["id"] for r in rows] == [LIVE]


def test_the_push_says_in_one_line_that_two_are_retired(bg_3):
    sb = build("critic", bg_3, batch_id="bg_3", mode="review")
    pushed = push_working_set("critic", sb, None)
    assert [r["id"] for r in pushed["criteria.load"]] == [LIVE]
    keys = list(pushed)
    assert keys[keys.index("criteria.load") + 1] == RETIRED_KEY
    note = pushed[RETIRED_KEY]
    assert "\n" not in note
    assert note == (
        "crit_2_format_invalid_bytes, crit_3_format_default_full_path are "
        "retired by the principal's ruling r_m244. They stay on his page, "
        "and a pass or a review does not name them.")


def test_a_batch_with_no_retired_criterion_pushes_no_note(bg_3):
    bg_3.execute("UPDATE criteria SET retired_by = NULL")
    bg_3.commit()
    sb = build("critic", bg_3, batch_id="bg_3", mode="review")
    pushed = push_working_set("critic", sb, None)
    assert RETIRED_KEY not in pushed
