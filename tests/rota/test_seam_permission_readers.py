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


def test_a_later_row_takes_back_an_act_on_the_row_itself(db):
    """An open ruling grants nothing yet, and it hides no landed grant. A
    later plain row takes back an act on the row itself, and a later act
    replaces it (the reviews of pass 4, P4-3, and of pass 4c, P4c-2)."""
    _rule(db, "r1", {"c1": {"verdict": "contest", "act": "drop"}})
    assert granted(db, "c1", "drop")
    _rule(db, "r2", {"c1": {"verdict": "contest", "act": "keep"}},
          status="open", seq=2)
    assert granted(db, "c1", "drop")
    assert not granted(db, "c1", "keep")
    _rule(db, "r3", {"c1": "approve"}, seq=3)
    assert not granted(db, "c1", "drop")
    _rule(db, "r4", {"c1": {"verdict": "contest", "act": "keep"}}, seq=4)
    assert not granted(db, "c1", "drop")
    assert granted(db, "c1", "keep")


# The review of pass 4c. Red on c33c20eb.

def test_a_plain_approve_ends_a_drop_and_a_later_contest_does_not_revive_it(db):
    """P4c-2: a drop's target is the row, and a plain approve on the row
    speaks to it. A later contest with no act retires nothing."""
    _rule(db, "r1", {"c1": {"verdict": "contest", "act": "drop",
                            "target_kind": "row"}})
    _rule(db, "r2", {"c1": "approve"}, seq=2)
    _rule(db, "r3", {"c1": {"verdict": "contest", "words": "line 2 is wrong"}},
          seq=3)
    assert api.criteria_page_acts(db, ["c1"])["retire"] == []
    assert api.ruling_drops_line(_ctx(db), "c1") is None


def test_an_add_on_the_line_does_not_end_its_drop(db):
    """P4c-4: an add rides on any line of the item, and it says nothing
    about the line it rides on."""
    _rule(db, "r1", {"c1": {"verdict": "contest", "act": "drop"}})
    _rule(db, "r2", {"c1": {"verdict": "contest", "act": "add",
                            "words": "a new line"}}, seq=2)
    assert granted(db, "c1", "drop")
    assert api.criteria_page_acts(db, ["c1"])["retire"] == ["c1"]


def test_a_plain_approve_of_its_line_does_not_end_an_add(db):
    """The review of pass 4d: the add's target is a new line that is not on
    the page, so a plain approve of the row it rides on says nothing about
    it. A later keep on the row ends it. Red on c5b149cc."""
    said = "the output stays exactly the same as today"
    _rule(db, "r1", {"c1": {"verdict": "approve", "act": "add",
                            "words": said}})
    _rule(db, "r2", {"c1": "approve"}, seq=2)
    assert api.criteria_page_acts(db, ["c1"])["add"] == [(TICKET, said)]
    _rule(db, "r3", {"c1": {"verdict": "contest", "act": "keep",
                            "target_kind": "check"}}, seq=3)
    assert api.criteria_page_acts(db, ["c1"])["add"] == []


def _rule_on(conn, rid: str, page: list, reading: dict, seq: int) -> None:
    """One landed ruling on `page`, for a page that shows a newer row."""
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "body_refs, seq) VALUES (?, 'th', 'liaison', 'principal', "
                 "'present', ?, ?)", (f"ask_{rid}", json.dumps(page), seq))
    flat = {r: v if isinstance(v, str) else v["verdict"] for r, v in reading.items()}
    conn.execute("INSERT INTO rulings (id, ask_id, per_item, words, status) "
                 "VALUES (?, ?, ?, ?, 'landed')",
                 (rid, f"ask_{rid}", json.dumps(flat), WORDS))
    insert_ruling_rows(conn, ruling_rows(conn, rid, page, reading, words=WORDS))
    conn.commit()


def _write_criterion(conn, cid: str, text: str) -> None:
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?, ?, ?)",
                 (cid, TICKET, text))
    conn.commit()


# The review of pass 4d and 4e. Red on e4a06b38.

def _session(conn, sid: str, seq: int, role: str, receipts, calls=()) -> None:
    """A committed session with its receipts and its tool calls."""
    conn.execute("INSERT INTO sessions (id, role, seq) VALUES (?, ?, ?)",
                 (sid, role, seq))
    for table, row_id in receipts:
        conn.execute("INSERT INTO receipts (session_id, table_name, row_id, "
                     "new_version) VALUES (?, ?, ?, 1)", (sid, table, row_id))
    for n, fn in enumerate(calls, 1):
        conn.execute("INSERT INTO tool_calls (session_id, fn, seq) VALUES "
                     "(?, ?, ?)", (sid, fn, n))
    conn.commit()


PARAPHRASE = "The CLI output is unchanged from today."
SAID = "the output stays exactly the same as today"


def test_an_add_is_done_by_a_criterion_written_after_its_ruling(db):
    """P4de-1 and P4f-1: the Terminologist writes in glossary terms, so the
    record of the write decides, not his words. A criteria.specify write of
    the ticket in a session after the ruling's marks the add done. The same
    criterion with no recorded write does not."""
    _rule(db, "r1", {"c1": {"verdict": "approve", "act": "add",
                            "words": SAID}})
    _session(db, "s_liaison", 1, "liaison", [("rulings", "r1")])
    assert api.criteria_page_acts(db, ["c1", "c2"])["add"] == [(TICKET, SAID)]
    _write_criterion(db, "c4", PARAPHRASE)
    assert api.criteria_page_acts(db, ["c1", "c4"])["add"] == [(TICKET, SAID)]
    _session(db, "s_term", 2, "terminologist", [("criteria", "c4")],
             ["criteria.specify"])
    assert api.criteria_page_acts(db, ["c1", "c4"])["add"] == []


def test_a_write_before_the_ruling_does_not_end_the_add(db):
    _write_criterion(db, "c4", PARAPHRASE)
    _session(db, "s_term", 1, "terminologist", [("criteria", "c4")],
             ["criteria.specify"])
    _rule(db, "r1", {"c1": {"verdict": "approve", "act": "add",
                            "words": SAID}})
    _session(db, "s_liaison", 2, "liaison", [("rulings", "r1")])
    assert api.criteria_page_acts(db, ["c1"])["add"] == [(TICKET, SAID)]


@pytest.mark.parametrize("page, ref, target", [
    ([ITEM, TICKET], TICKET, None),       # the page shows no criterion
    ([ITEM, "c1"], "c1", None),           # the page shows some criteria
    (PAGE, "c1", "tk2"),                  # the add targets a ticket not shown
])
def test_no_page_shape_ends_an_add_that_nobody_wrote(db, page, ref, target):
    """P4f-1, the three failing cases of rv4f_add.py. Each page shape ended
    the add on e1b62ab2 with no criterion written after the ruling."""
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk2', ?, "
               "'t2')", (ITEM,))
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('d1', "
               "'tk2', 'the text of d1')")
    db.commit()
    value = {"verdict": "approve", "act": "add", "words": SAID}
    if target:
        value["target"] = target
    _rule_on(db, "r1", page, {ref: value}, seq=1)
    assert api.criteria_page_acts(db, ["c1"])["add"] == [(target or TICKET,
                                                        SAID)]


def test_every_open_add_is_offered_until_each_is_done(db):
    """P4de-2: two adds in other words on c1 from two rulings both stay.
    The first is done by c4, which the page of the second ruling shows, so
    the second stays alone."""
    first, second = "the output stays the same", "the exit code is zero"
    _rule(db, "r1", {"c1": {"verdict": "approve", "act": "add",
                            "words": first}})
    _write_criterion(db, "c4", "The output stays the same.")
    _rule_on(db, "r2", PAGE + ["c4"],
             {"c1": {"verdict": "approve", "act": "add", "words": second}},
             seq=2)
    assert api.criteria_page_acts(db, ["c1"])["add"] == [(TICKET, second)]
    db.execute("DELETE FROM criteria WHERE id = 'c4'")
    db.commit()
    assert api.criteria_page_acts(db, ["c1"])["add"] == [(TICKET, first),
                                                        (TICKET, second)]


def test_an_add_that_a_live_criterion_holds_is_not_offered_again(db):
    """P4c-1: m112's add, then the criterion that criteria.specify wrote.
    The add is done, so the relay wake offers it no more."""
    said = "the output stays exactly the same as today"
    _rule(db, "r1", {"c1": {"verdict": "approve", "act": "add",
                            "words": said}})
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c4', ?, 'The output stays exactly the same as today.')",
               (TICKET,))
    db.commit()
    assert api.criteria_page_acts(db, ["c1", "c4"])["add"] == []


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


# Seam pass 3b: the act `exclude` takes a path off the guess. A `remove`
# deletes code and disputes no path.
@pytest.mark.parametrize("act, expected", [("exclude", ["tests/test_x.py"]),
                                           ("remove", []), (None, [])])
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
    config. It reads the landed rows of `ruled_refs_live` now. A verdict
    message with no ruling behind it is no contest, and a landed contest row
    is one. Fact F1 removed the map."""
    from rota.core.runner import _resolve_contest

    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES ('m5', 'th', 'principal', 'liaison', "
               "'verdict', '[]', 5)")
    db.commit()
    assert _resolve_contest(db, ITEM) == {}
    _rule(db, "r1", {ITEM: "contest"})
    assert _resolve_contest(db, ITEM)["principal_verdict"] == {ITEM: "contest"}


def _brief(name: str) -> str:
    from pathlib import Path

    return (Path(api.__file__).parent / "prompts" / "liaison"
            / name).read_text(encoding="utf-8")


# The brief that offers `rulings.rule` with acts. The clarify brief named
# `remove` only (the review of pass 4b, P4b-4). The landing brief offers
# the menu options instead (frame 345, pass R2), and the tests below it pin
# them.
_RULE_BRIEFS = ["answering.md"]


def _menu_names() -> set[str]:
    """The option names of every menu, and the clause options."""
    names = {api._menu_option(o)[0] for opts in api._MENU_BASE.values()
             for o in opts}
    return names | {api._menu_option(api._MENU_OTHER)[0], "exclude", "none",
                    "held"}


def test_the_landing_brief_names_every_menu_option():
    """Frame 345, R6: an option that the brief does not name is an option
    that no live Liaison chooses."""
    brief = _brief("landing.md")
    for opts in api._MENU_BASE.values():
        for option in opts:
            assert f"`{option}`" in brief, option
    assert f"`{api._MENU_OTHER}`" in brief
    assert "`exclude <path>`" in brief


def test_every_menu_example_of_the_landing_brief_names_an_option():
    """Frame 345, R6: each value of a `rulings=` example in the landing
    brief is a menu option, keyed by a line, a clause or `rest`."""
    import re

    seen = 0
    for line in _brief("landing.md").splitlines():
        for found in re.findall(r"rulings=(\{.*?\})(?:\)|`)", line):
            for key, value in json.loads(found).items():
                assert key.isdigit() or re.fullmatch(r"c\d+", key) or (
                    key == "rest"), found
                option = value["option"] if isinstance(value, dict) else value
                assert api._menu_option(option)[0] in _menu_names(), found
                seen += 1
    assert seen >= 5, seen


@pytest.mark.parametrize("name", _RULE_BRIEFS)
def test_the_landing_brief_names_every_act_and_target_kind(name):
    """The review of pass 4, P4-2: an act no brief names is an act no live
    Liaison writes, so its reader grants nothing. Red on fbce68db, whose
    brief showed `remove` only."""
    from rota.roles.principal import RULED_ACTS, TARGET_KINDS

    brief = _brief(name)
    for word in RULED_ACTS + TARGET_KINDS:
        assert f"- `{word}`" in brief or f"`{word}` is" in brief, word


@pytest.mark.parametrize("name", _RULE_BRIEFS)
def test_every_example_of_the_brief_passes_the_door(name):
    """The review of pass 4b, P4b-2: four examples had no verdict, and the
    door refuses an object value with no verdict. Each example passes
    `_ruling_shape` in the form its line names. A line that puts the
    change in `acts` names the flat form, where the verdict comes from
    `rulings`. A `rulings=` example is the whole map, and each of its values
    passes (pass 4h). Every other example is a value of `rulings`."""
    import re

    seen = 0
    for line in _brief(name).splitlines():
        for whole, found in re.findall(r"`(rulings=)?(\{[^`]*\})`", line):
            value = json.loads(found)
            if "in `acts`" in line:
                value = {"verdict": "contest", **value}
            for key, one in (value.items() if whole else [("3", value)]):
                assert key.isdigit(), found
                # A line with no act takes the verdict word alone (the gate
                # on 76e18948: the small model copied `keep` onto approves).
                if isinstance(one, str):
                    assert one in ("approve", "contest", "revise", "later",
                                   "now", "drop"), found
                else:
                    api._ruling_shape(key, one)
                seen += 1
    assert seen >= 8, seen


def test_m112s_add_on_an_approved_line_reaches_the_page_acts(db):
    """The review of pass 4b, P4b-5. Night 163's m112 held an act on every
    contested line, so its add rode on an approved line. The reader read
    the add only behind a contest or a revise. Red on 0736f9dd."""
    said = "the output stays exactly the same as today"
    _rule(db, "r1", {"c1": {"verdict": "approve", "act": "add",
                            "words": said}})
    assert api.criteria_page_acts(db, ["c1"])["add"] == [(TICKET, said)]
    assert api.criteria_page_acts(db, ["c1"])["retire"] == []


# Pass 4h. Red on 7efdee6a.

def test_the_shift_page_reads_that_act_names_are_not_verdicts():
    """L1-LI-a-separate-request-is-later, 0 of 5: the shift page reads the
    landing piece, and the model wrote the act `drop` as its verdict. One
    file serves both pages, so the act list opens with the sentence."""
    from rota.roles import prompts

    piece = prompts.piece("liaison", "landing")
    # The gate on e3b171e5: the model still read "a separate request" as
    # the act drop. The menu brief keeps the point in its own words
    # (frame 345, R6).
    sentence = "\"It is a separate request\" is `later`, never `drop`."
    assert sentence in piece


def test_each_recorded_write_ends_one_add_the_oldest_first(db):
    """P4g-1: one write on the ticket ended every open add. Now it ends the
    oldest, and a second write ends the next."""
    first, second = "the output stays the same", "the exit code is zero"
    _rule(db, "r1", {"c1": {"verdict": "approve", "act": "add",
                            "words": first}})
    _session(db, "s_l1", 1, "liaison", [("rulings", "r1")])
    _rule(db, "r2", {"c1": {"verdict": "approve", "act": "add",
                            "words": second}}, seq=2)
    _session(db, "s_l2", 2, "liaison", [("rulings", "r2")])
    _write_criterion(db, "c4", "The program output is unchanged.")
    _session(db, "s_t1", 3, "terminologist", [("criteria", "c4")],
             ["criteria.specify"])
    assert api.criteria_page_acts(db, ["c1"])["add"] == [(TICKET, second)]
    _write_criterion(db, "c5", "The program exits with code 0.")
    _session(db, "s_t2", 4, "terminologist", [("criteria", "c5")],
             ["criteria.specify"])
    assert api.criteria_page_acts(db, ["c1"])["add"] == []


def test_a_criterion_in_his_words_counts_for_its_own_add_only(db):
    """P4g-1: a write that holds the second add's words ends the second
    add, and it does not count against the first."""
    first, second = "the output stays the same", "the exit code is zero"
    _rule(db, "r1", {"c1": {"verdict": "approve", "act": "add",
                            "words": first}})
    _session(db, "s_l1", 1, "liaison", [("rulings", "r1")])
    _rule(db, "r2", {"c1": {"verdict": "approve", "act": "add",
                            "words": second}}, seq=2)
    _session(db, "s_l2", 2, "liaison", [("rulings", "r2")])
    _write_criterion(db, "c4", "The exit code is zero.")
    _session(db, "s_t1", 3, "terminologist", [("criteria", "c4")],
             ["criteria.specify"])
    assert api.criteria_page_acts(db, ["c1"])["add"] == [(TICKET, first)]
