"""Frame 306, W2 of night 163: a respecify meets the near-duplicate check.

Night 163's Terminologists s209 to s265 respecified c3_terminal_failure_true
with the words of c2_non_terminal_false. `criteria.specify` refuses such a
text at 0.85 word overlap, and `criteria.respecify` had no such check, so
two rows of one ticket held one fact.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import prompts


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, "
                 "approval_ver, version) VALUES ('i1','clear returns a bool',"
                 "'in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','i1','clear returns a bool')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('c2','tk1','clear() returns False when stdout is not a "
                 "terminal.')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('c3','tk1','clear() returns False when the clear operation "
                 "fails, provided no exception is raised.')")
    conn.commit()
    return conn


# Night 163's c3_terminal_failure_true, version 10, held c2's words. The
# full stop differs here, so the fuzzy guard decides and not the exact one.
TWIN = "clear() returns False when stdout is not a terminal"


def _refusal(db, op: str, mode: str, **kw) -> str:
    sb = build("terminologist", db, mode=mode,
               allow=prompts.mode_tools("terminologist", mode))
    with pytest.raises(ValueError) as caught:
        sb.call(op, **kw)
    return str(caught.value)


def test_a_respecify_into_another_criterions_words_is_refused(db):
    said = _refusal(db, "criteria.respecify", "criterion_repair", id="c3",
                    text=TWIN, surface_refs=["clear"])
    assert "this says what c2 says, in nearly the same words" in said


def test_the_refusal_is_the_text_of_specify(db):
    """The respecify refusal opens with the text of specify. Frame 329's
    repair R2 adds a tail that names the acts of the repair mode."""
    respecify = _refusal(db, "criteria.respecify", "criterion_repair",
                         id="c3", text=TWIN, surface_refs=["clear"])
    specify = _refusal(db, "criteria.specify", "criteria", id="c4",
                       ticket_id="tk1", text=TWIN, surface_refs=["clear"])
    assert respecify.startswith(specify)


def test_a_respecify_close_to_its_own_old_words_is_no_twin(db):
    """The rewritten row is not its own twin: a small repair still lands."""
    sb = build("terminologist", db, mode="criterion_repair",
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    try:
        sb.call("criteria.respecify", id="c3",
                text="clear() returns False when the clear operation fails, "
                     "and no exception is raised.",
                surface_refs=["clear"])
    except ValueError as exc:
        assert "nearly the same words" not in str(exc)
