"""
A `default` row after intent under `merge_gate = auto` is listed, not
numbered, in the request's quiet section (frame 325, repair K, second step).

Frame 204's design, section 5, row 2, ruled "Start as written" on
2026-10-11 15:44: before intent a default is "a numbered line"; after
intent under `auto` it is "listed, not numbered, in the request's quiet
section"; under `review` it is "a numbered line on the review page". The
agenda tick keeps `default` "only when `merge_gate = review`". Night 165's
m239 put a Developer's account of its own work as line 6 under "Where you
did not say, I assumed:", on a page after intent.
"""
from __future__ import annotations

import pytest

from rota.core import config
from rota.core.db import init_db
from rota.core.scheduler import tick_agenda
from rota.roles.principal import render_page

ACCOUNT = "The greet command now calls click.echo, and its tests pass"
CONFLICT = "The criterion says stderr, and the test reads stdout"

# The page of `_seed(approved=True, account=False)` at 73e1cf69. A page
# with no default row keeps these bytes.
BEFORE = (
    "Here is what I understand you want, on one page.\n"
    "The team's notes. A seat wrote each of these where your words were "
    "silent. They are not your request.\n"
    "Where you did not say, I assumed:\n"
    f"  1. {CONFLICT}\n"
    "Reply in your own words. 'ok' approves all of this and starts building. "
    "Name a line to correct only that line. Ask, if something here is unclear."
)


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _seed(db, approved: bool, account: bool = True,
          conflict: bool = True) -> list[str]:
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('greet','The program greets the user.',"
               "'in_scope',?,1,1)", ("approved" if approved else "draft",))
    refs = []
    if conflict:
        db.execute("INSERT INTO ledger (id, about_ref, about_table, "
                   "default_taken, kind, status, author) VALUES ('l_c',"
                   "'greet','items',?,'conflict','open','tester')", (CONFLICT,))
        refs.append("l_c")
    if account:
        db.execute("INSERT INTO ledger (id, about_ref, about_table, "
                   "default_taken, kind, status, author) VALUES ('l_d',"
                   "'greet','items',?,'default','open','developer')",
                   (ACCOUNT,))
        refs.append("l_d")
    db.commit()
    return refs


def _render(db, refs):
    return render_page(db, "present", refs, ask_id="m239", returned=False)


def test_after_intent_a_default_is_listed_with_no_number(db):
    refs = _seed(db, approved=True)
    page, order = _render(db, refs)
    assert order == ["l_c"], order
    assert f"  1. {CONFLICT}" in page, page
    assert f"  - {ACCOUNT}" in page, page
    assert not any(line.lstrip()[:1].isdigit() and ACCOUNT in line
                   for line in page.splitlines()), page


def test_before_intent_a_default_keeps_its_numbered_line(db):
    refs = _seed(db, approved=False)
    page, order = _render(db, refs)
    assert order == ["l_c", "l_d"], order
    assert f"  2. {ACCOUNT}" in page, page


def test_under_review_a_default_keeps_its_numbered_line(db):
    config.set(db, "merge_gate", "review")
    refs = _seed(db, approved=True)
    page, order = _render(db, refs)
    assert order == ["l_c", "l_d"], order
    assert f"  2. {ACCOUNT}" in page, page


def test_after_intent_a_default_alone_wakes_no_page(db):
    _seed(db, approved=True, conflict=False)
    assert tick_agenda(db, principal_present=True) == []


def test_after_intent_a_default_rides_the_page_a_conflict_wakes(db):
    _seed(db, approved=True)
    wakes = tick_agenda(db, principal_present=True)
    assert len(wakes) == 1, wakes
    refs = list(wakes[0].refs)
    assert refs == ["l_c", "l_d"], refs
    page, order = _render(db, refs)
    assert order == ["l_c"] and f"  - {ACCOUNT}" in page, page


def test_before_intent_a_default_alone_still_wakes_a_page(db):
    _seed(db, approved=False, conflict=False)
    wakes = tick_agenda(db, principal_present=True)
    assert len(wakes) == 1 and wakes[0].refs == ("l_d",), wakes


def test_a_page_with_no_default_row_is_byte_equal_to_before(db):
    refs = _seed(db, approved=True, account=False)
    page, order = _render(db, refs)
    assert page.encode() == BEFORE.encode(), page
    assert order == ["l_c"]
