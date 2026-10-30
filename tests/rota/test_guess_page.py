"""
Frame 298, pass 2: the code line on the page.

The design is `plans/frame298-design.md`, section 2, with 1.3 and 3.3. The
send door stamps what each request's code line shows, once, in the door row
`code:<message id>`. The page renders the line from the stamp only: a guess
set frozen, or a live batch's plan. A page sent before the guess says the
team has not guessed yet. The index line "code that names these words"
leaves every page.

The scene is night 156's m191, bg_3's sign-off page, rebuilt from the rows
`test_guess_route.py` copied from `.rota/clickI_night156.db` read with
`mode=ro`. Here the page goes out through the real send door.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.runner import push_working_set, run_session
from rota.core.sandbox import build
from rota.core.scheduler import Wake
from rota.llm.llm import Pins, ScriptedBackend
from rota.roles import prompts
from rota.roles.principal import land, parse_reply, pending_asks, render_page
from rota.testkit.fixtures import seed_provenance

from .test_guess_route import CRITERIA, ITEM, M192, NOTES, TICKET, TOUCH

PINS = Pins(model="stub", temperature=0.0)
KEY = f"guess:{ITEM}"
TEXT = ("Give version_option a show_python flag that appends the running "
        "Python version to the message.")
# bg_3's guess as the Architect wrote it on night 156: the wrong test files.
GUESS = ("src/click/decorators.py", "tests/test_options.py", "tests/test_defaults.py")
INDEX_LINE = "code that names these words"
PAGES: list[str] = []


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _state(db, batch: str | None = None, guess: bool = False, head: str | None = None):
    """m191's rows before the send: the item approved at version 1, its
    criteria and notes, the index, bg_3 when `batch`, the guess when `guess`."""
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version, "
               "priority) VALUES (?, ?, 'in_scope', 'approved', 1, 1, 1)", (ITEM, TEXT))
    seed_provenance(db, "items", ITEM, "decided")
    db.execute("INSERT INTO tickets (id, item_id, text, version, item_ver) "
               "VALUES (?, ?, ?, 1, 1)", (TICKET, ITEM, TEXT.lower()))
    for cid, text in CRITERIA:
        db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?, ?, ?)",
                   (cid, TICKET, text))
    for lid, author, kind, table, about, taken in NOTES:
        db.execute("INSERT INTO ledger (id, author, kind, about_table, about_ref, "
                   "default_taken, status) VALUES (?, ?, ?, ?, ?, ?, 'open')",
                   (lid, author, kind, table, about, taken))
    for grain in sorted(set(TOUCH) | set(GUESS)):
        db.execute("INSERT INTO code_index (grain, grain_kind) VALUES (?, 'path')",
                   (grain,))
    if batch:
        db.execute("INSERT INTO batches (id, item_id, head_commit, status, version) "
                   "VALUES ('bg_3', ?, ?, ?, 1)", (ITEM, head, batch))
        db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('bg_3', ?)",
                   (TICKET,))
        for grain in TOUCH:
            db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind, "
                       "confidence) VALUES ('bg_3', ?, 'path', 'expected')", (grain,))
    if guess:
        _guess(db, GUESS)
    db.commit()


def _guess(db, paths, ruling: str = "", symbols=()):
    for grain in paths:
        db.execute("INSERT INTO touch_guesses (item_id, item_ver, ruling_id, grain, "
                   "grain_kind) VALUES (?, 1, ?, ?, 'path')", (ITEM, ruling, grain))
    for grain in symbols:
        db.execute("INSERT INTO touch_guesses (item_id, item_ver, ruling_id, grain, "
                   "grain_kind, confidence) VALUES (?, 1, ?, ?, 'symbol', 'possible')",
                   (ITEM, ruling, grain))
    db.commit()


def _send(db, refs: list[str]) -> str:
    """The Liaison's present, scripted, through the real send door."""
    wake = Wake("liaison", "tick:agenda", refs=(ITEM,), detail="ledger=1")
    call = f"TOOL: msg.present_principal(refs={json.dumps(refs)})"
    out = run_session(db, wake, backend=ScriptedBackend([call, "done"]), pins=PINS,
                      instructions="present")
    assert out.committed, out.errors
    return db.execute("SELECT id FROM messages WHERE verb = 'present' "
                      "ORDER BY seq DESC LIMIT 1").fetchone()["id"]


def _sent(db, mid: str) -> tuple[list[str], dict, str, list[str]]:
    refs = json.loads(db.execute("SELECT body_refs FROM messages WHERE id = ?",
                                 (mid,)).fetchone()["body_refs"])
    row = db.execute("SELECT value FROM config WHERE key = ?",
                     (f"code:{mid}",)).fetchone()
    stamp = json.loads(row["value"]) if row else {}
    page, order = render_page(db, "present", refs, ask_id=mid)
    PAGES.append(page)
    return refs, stamp, page, order


def _lines(page: str) -> list[str]:
    return page.split("\n")


# ---------------------------------------------------------------------------
# 1. A live batch with rows: the line is the plan
# ---------------------------------------------------------------------------

def test_m191_with_a_live_batch_stamps_the_batch_and_shows_its_plan(db):
    _state(db, batch="running", guess=True)
    mid = _send(db, [ITEM])
    refs, stamp, page, order = _sent(db, mid)
    assert stamp == {KEY: {"batch": "bg_3"}}
    assert KEY in refs
    stamped = json.loads(db.execute("SELECT value FROM config WHERE key = ?",
                                    (f"stamped:{mid}",)).fetchone()["value"])
    assert KEY in stamped
    assert order[:2] == [ITEM, KEY]
    lines = _lines(page)
    at = lines.index(f"  1. {TEXT}")
    assert lines[at + 1] == ("  2. The team's plan of the code this touches: expected "
                             "to touch src/click/decorators.py, tests/test_basic.py")
    assert lines[at + 2] == "It must:"
    assert "To correct the code it touches, name line 2." in page


# ---------------------------------------------------------------------------
# 2. No batch, a guess set: the line is the guess, frozen
# ---------------------------------------------------------------------------

def test_m191_with_a_guess_stamps_the_set_and_a_later_set_does_not_move_it(db):
    _state(db, guess=True)
    mid = _send(db, [ITEM])
    refs, stamp, page, order = _sent(db, mid)
    assert stamp == {KEY: {"guess": [1, ""]}}
    assert order[:2] == [ITEM, KEY]
    shown = ("  2. The team's guess at the code this touches: src/click/decorators.py, "
             "tests/test_options.py, tests/test_defaults.py.")
    assert shown in _lines(page)
    _guess(db, ("src/click/decorators.py", "tests/test_basic.py"), ruling="m192",
           symbols=("src/click/decorators.py::version_option",))
    _, _, later, later_order = _sent(db, mid)
    assert shown in _lines(later)
    assert later_order == order


def test_a_guess_with_symbols_names_what_it_might_touch(db):
    _state(db)
    _guess(db, ("src/click/decorators.py", "tests/test_basic.py"),
           symbols=("src/click/decorators.py::version_option",))
    _, _, page, _ = _sent(db, _send(db, [ITEM]))
    assert ("  2. The team's guess at the code this touches: src/click/decorators.py, "
            "tests/test_basic.py. It might touch src/click/decorators.py::version_option."
            ) in _lines(page)


# ---------------------------------------------------------------------------
# 3. Before the guess
# ---------------------------------------------------------------------------

def test_a_page_before_the_guess_says_so_unnumbered(db):
    _state(db)
    mid = _send(db, [ITEM])
    refs, stamp, page, order = _sent(db, mid)
    assert stamp == {}
    assert db.execute("SELECT 1 FROM config WHERE key = ?", (f"code:{mid}",)).fetchone() is None
    assert not any(r.startswith("guess:") for r in refs)
    lines = _lines(page)
    at = lines.index(f"  1. {TEXT}")
    assert lines[at + 1] == "     The team has not guessed the code this touches yet."
    assert order[1] == CRITERIA[0][0]
    assert "To correct the code" not in page


# ---------------------------------------------------------------------------
# 4. A touch page: the batch line as today, no code line
# ---------------------------------------------------------------------------

def test_a_touch_page_has_no_code_line_and_no_stamp(db):
    _state(db, batch="pending", guess=True)
    mid = _send(db, [ITEM, "bg_3"])
    refs, stamp, page, order = _sent(db, mid)
    assert stamp == {}
    assert KEY not in refs and KEY not in order
    assert page.startswith("Before I build this")
    assert "The team has not guessed" not in page
    assert "The team's guess" not in page and "The team's plan" not in page
    assert any("expected to touch src/click/decorators.py" in l for l in _lines(page))


# ---------------------------------------------------------------------------
# 5. A closed batch target
# ---------------------------------------------------------------------------

def test_a_closed_batch_target_says_the_plan_is_closed_and_keeps_its_number(db):
    _state(db, batch="running")
    mid = _send(db, [ITEM])
    _, _, _, order = _sent(db, mid)
    db.execute("UPDATE batches SET status = 'merged' WHERE id = 'bg_3'")
    db.commit()
    _, _, page, later = _sent(db, mid)
    assert later == order
    assert "  2. The team's plan for this change is closed." in _lines(page)


# ---------------------------------------------------------------------------
# 6. The index line leaves every page
# ---------------------------------------------------------------------------

def test_no_page_renders_the_index_line(db):
    """The pages of the tests above, and every recorded case's fixture."""
    from pathlib import Path

    from rota.roles import principal

    assert not hasattr(principal, "near_code")
    assert not hasattr(principal, "STOP_WORDS")
    _state(db, guess=True)
    db.execute("INSERT INTO code_index (grain, grain_kind) VALUES "
               "('src/click/decorators.py::version_option', 'symbol')")
    db.commit()
    _sent(db, _send(db, [ITEM]))
    assert PAGES and not any(INDEX_LINE in p for p in PAGES)
    cases = Path(__file__).parent / "cases"
    held = [p.name for p in cases.glob("*.yaml") if INDEX_LINE in p.read_text("utf-8")]
    assert held == []


# ---------------------------------------------------------------------------
# 7. The cue's text 1 names the line number
# ---------------------------------------------------------------------------

# m192's last sentence. Its other sentences number m191's lines, and the code
# line moves those numbers on this page.
M192_LINE_1 = M192[M192.index("Line 1 also"):]


# ---------------------------------------------------------------------------
# 8. The seed: the annotate wake reads the guess
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="menu_ruling quote home: a quote in a clause that "
                         "names another line cannot change an unnumbered line")
def test_the_cue_names_the_code_line_by_its_number_on_a_stamped_page(db):
    _state(db, guess=True)
    mid = _send(db, [ITEM])
    (ask,) = [a for a in pending_asks(db) if a.message_id == mid]
    land(db, ask, parse_reply(ask, M192_LINE_1))
    db.commit()
    sb = build("liaison", db, mode="landing",
               allow=prompts.mode_tools("liaison", "landing"))
    sb.ctx.trigger = db.execute("SELECT id FROM messages WHERE cause_id = ? "
                                "AND from_role = 'principal'", (mid,)).fetchone()["id"]
    every = {str(n): "approve" for n in range(1, len(ask.order) + 1)}
    # The menu form (frame 345, R6): line 2 is the code line, and the
    # refusal of the files cue went with the word form.
    out = sb.call("rulings.rule", rulings=dict(every, **{"2": "rewrite"}))
    assert out["per_item"][KEY] == "contest"
    assert out["per_item"][ITEM] == "approve"


def _annotate_set(db):
    sb = build("architect", db, mode="annotate",
               allow=prompts.mode_tools("architect", "annotate"))
    return push_working_set("architect", sb, Wake("architect", "tick:annotate",
                                                  refs=("bg_3",)))


def test_the_annotate_wake_reads_the_items_guess(db):
    _state(db, batch="pending", guess=True)
    db.execute("DELETE FROM batch_touch")
    db.commit()
    pushed = _annotate_set(db)
    assert pushed["the item's guess"] == {"paths": list(GUESS), "symbols": []}


def test_the_annotate_wake_reads_the_rulings_words_with_the_guess(db):
    _state(db, batch="pending", guess=True)
    db.execute("DELETE FROM batch_touch")
    db.execute("INSERT INTO config (key, value) VALUES ('entry:m193', ?)",
               (json.dumps(M192),))
    _guess(db, ("src/click/decorators.py", "tests/test_basic.py"), ruling="m193")
    pushed = _annotate_set(db)
    assert pushed["the item's guess"] == {
        "paths": ["src/click/decorators.py", "tests/test_basic.py"], "symbols": [],
        "the principal said": M192}
