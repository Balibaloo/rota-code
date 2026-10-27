"""
The readers of what his ruling permits read `act` and `target` of the record
(the seam design, pass 4).

Each reader of P1 to P11 (`plans/frame339-reach.md`, section 2) read his
words by a phrase. Now each one reads the newest landed row of
`ruled_refs_live` on its ref through `principal.granted`. A row with no act
grants nothing, because silence is not consent (`composition.md`, Flows).
"""
from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from rota.core.db import init_db
from rota.core.runner import disputed_paths
from rota.roles import api
from rota.roles.principal import grant, granted, insert_ruling_rows, ruling_rows

ITEM = "it"
TICKET = "tk"
PAGE = [ITEM, "c1", "c2", "c3"]
WORDS = "the whole reply"


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES (?, 'the item', 'in_scope', 'approved', 1, 1)",
                 (ITEM,))
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES (?, ?, 't')",
                 (TICKET, ITEM))
    for cid in PAGE[1:]:
        conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                     "(?, ?, ?)", (cid, TICKET, f"the text of {cid}"))
    conn.commit()
    return conn


def _rule(conn, rid: str, reading: dict, status: str = "landed",
          seq: int = 1) -> None:
    """One ruling on the page PAGE, with its rows from the one builder."""
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "body_refs, seq) VALUES (?, 'th', 'liaison', 'principal', "
                 "'present', ?, ?)", (f"ask_{rid}", json.dumps(PAGE), seq))
    flat = {r: v if isinstance(v, str) else v["verdict"] for r, v in reading.items()}
    conn.execute("INSERT INTO rulings (id, ask_id, per_item, words, status) "
                 "VALUES (?, ?, ?, ?, ?)",
                 (rid, f"ask_{rid}", json.dumps(flat), WORDS, status))
    insert_ruling_rows(conn, ruling_rows(conn, rid, PAGE, reading, words=WORDS))
    conn.commit()


def test_a_row_with_no_act_grants_nothing(db):
    """The words of a row are no permission. Only its act is."""
    _rule(db, "r1", {"c1": {"verdict": "contest", "words": "remove line 2"}})
    assert grant(db, "c1", "remove") is None
    assert not granted(db, "c1", "drop")


@pytest.mark.parametrize("target, asked, expected", [
    (None, None, True),
    (None, "tests/test_x.py", False),
    ("tests/test_x.py", None, True),
    ("tests/test_x.py", "tests/test_x.py", True),
    ("`tests/test_x.py`", "Tests/test_x.py", True),
    ("--show-python", "show-python", True),
    ("tests/test_x.py", ["a.py", "tests/test_x.py"], True),
    ("tests/test_x.py", "tests/test_y.py", False),
])
def test_the_grant_names_its_target(db, target, asked, expected):
    """A call with a target needs the row's target. A call with none takes
    the act on any target."""
    value = {"verdict": "contest", "act": "remove"}
    if target is not None:
        value["target"] = target
    _rule(db, "r1", {"c1": value})
    assert granted(db, "c1", "remove", asked) is expected
    assert not granted(db, "c1", "add", asked)


def test_only_the_newest_landed_row_grants(db):
    """A newer landed ruling takes the grant back. An open ruling grants
    nothing yet, and it hides no landed grant."""
    _rule(db, "r1", {"c1": {"verdict": "contest", "act": "drop"}})
    assert granted(db, "c1", "drop")
    _rule(db, "r2", {"c1": {"verdict": "contest", "act": "keep"}},
          status="open", seq=2)
    assert granted(db, "c1", "drop")
    assert not granted(db, "c1", "keep")
    _rule(db, "r3", {"c1": "approve"}, seq=3)
    assert not granted(db, "c1", "drop")


# One test per reader, on its own target kind. Each case is the reading
# with the act, then the same reading with no act.

def _ctx(conn):
    return SimpleNamespace(conn=conn)


@pytest.mark.parametrize("act, expected", [("drop", 3), (None, None)])
def test_p6_a_drop_of_a_row_gives_its_page_line(db, act, expected):
    _rule(db, "r1", {"c2": {"verdict": "contest", "act": act,
                            "target_kind": "row"}})
    assert api.ruling_drops_line(_ctx(db), "c2") == expected


@pytest.mark.parametrize("act, expected", [("keep", True), ("rewrite", False),
                                           (None, False)])
def test_p7_a_keep_of_the_words_asks_no_new_words(db, act, expected):
    """A fault of the check alone keeps the words. A rewrite asks for new
    words, and no act asks for nothing the door can act on."""
    _rule(db, "r1", {"c1": {"verdict": "contest", "act": act,
                            "target_kind": "check"}})
    assert api.ruling_asks_no_new_words(_ctx(db), "c1") is expected


@pytest.mark.parametrize("act, expected", [("add", [(TICKET, "a new line")]),
                                           (None, [])])
def test_p8_an_add_on_the_ticket_adds_the_rows_words(db, act, expected):
    _rule(db, "r1", {"c1": "contest",
                     TICKET: {"verdict": "revise", "act": act,
                              "words": "a new line"}})
    assert api.criteria_page_acts(db, ["c1"])["add"] == expected


@pytest.mark.parametrize("act, expected", [("remove", ["tests/test_x.py"]),
                                           (None, [])])
def test_p10_a_removed_path_leaves_the_guess(db, act, expected):
    key = f"guess:{ITEM}"
    _rule(db, "r1", {key: {"verdict": "contest", "act": act,
                           "target_kind": "path", "target": "tests/test_x.py"}})
    paths = ["src/x.py", "tests/test_x.py"]
    assert disputed_paths(db, key, paths) == expected


@pytest.mark.parametrize("verdict, expected", [("contest", "3"),
                                               ("approve", None)])
def test_p4_the_other_line_is_the_line_of_a_contest_row(db, verdict, expected):
    """The line comes from the row's `line`, not from "line N" in his
    words."""
    _rule(db, "r1", {ITEM: {"verdict": "contest", "words": "line 9 is wrong"},
                     "c2": verdict})
    assert api._other_line(db, ITEM) == expected


def test_p5_his_span_on_another_line_is_about_the_page(db):
    """A text that copies his span on another page line is his words about
    the page. A row that carries only the whole reply gives no span."""
    _rule(db, "r1", {ITEM: "contest",
                     "c2": {"verdict": "contest",
                            "words": "the page should cover only the flag"}})
    said = api._page_reply_fault(db, ITEM, "The item should cover only the "
                                 "flag.", WORDS)
    assert "about line 3 of the page" in said
    assert api._page_reply_fault(db, ITEM, "Something else entirely here.",
                                 WORDS) is None


def test_the_contest_reader_reads_the_rows_and_not_the_verdict_map(db):
    """The review of pass 2: `_resolve_contest` read the `verdict:` maps of
    config. It reads the landed rows of `ruled_refs_live` now. A map with no
    ruling behind it is no contest, and a landed contest row is one."""
    from rota.core.runner import _resolve_contest

    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES ('m5', 'th', 'principal', 'liaison', "
               "'verdict', '[]', 5)")
    db.execute("INSERT INTO config (key, value) VALUES ('verdict:m5', ?)",
               (json.dumps({ITEM: "contest"}),))
    db.commit()
    assert _resolve_contest(db, ITEM) == {}
    _rule(db, "r1", {ITEM: "contest"})
    assert _resolve_contest(db, ITEM)["principal_verdict"] == {ITEM: "contest"}


def test_the_landing_brief_names_every_act_and_target_kind():
    """The review of pass 4, P4-2: an act no brief names is an act no live
    Liaison writes, so its reader grants nothing. Red on fbce68db, whose
    brief showed `remove` only."""
    from pathlib import Path

    from rota.roles.principal import RULED_ACTS, TARGET_KINDS

    brief = (Path(api.__file__).parent / "prompts" / "liaison"
             / "landing.md").read_text(encoding="utf-8")
    for word in RULED_ACTS + TARGET_KINDS:
        assert f"- `{word}`" in brief or f"`{word}` is" in brief, word
