"""Frame 202: the respecify door refuses a surface move to a callable that
the principal named as a comparison.

Night 146, the rota workflow (`plans/night146-read.md`, section 5). The
request was an `echo_json(obj)` helper "next to echo". Terminologist relays
of the principal's corrections moved the criteria's surface from `echo_json`
to `echo`. The Testers then called `echo`, and a Developer rewrote `echo`.
The texts and words below are the night's.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import prompts

ECHO = "src/click/utils.py::echo"
ECHO_JSON = "src/click/utils.py::echo_json"
ITEM_ECHO_JSON = ("Add an echo_json(obj) helper next to echo that prints an "
                  "object as compact JSON on one line, followed by a newline.")
ITEM_SUPPORT = ("Add an echo_json(obj) helper to print an object as compact "
                "JSON on one line, followed by a newline.")
# r_dae83a8c5c, the reply m64 that the relay m67 carried to s160.
WORDS_64 = ("Line 2 is wrong because the helper should write the compact JSON "
            "to the stream the way echo does, not return a string. Line 5 "
            "still lists the pager test, which I asked you to drop.")
# r_5a4cf89060, the reply m146 before s291's restore.
WORDS_146 = ("echo_json should let the TypeError from the json module through "
             "without catching it, and echo itself should not change. The test "
             "fails because it calls echo instead of echo_json, so point the "
             "test at echo_json and keep it in the existing utils tests file.")
# s248's text for echo_json_support_compact.
S248 = ("The callable `echo_json` must write a string containing the compact "
        "JSON representation of the input object followed by exactly one "
        "newline character to the stream.")
# s160's text for echo_json_compact.
S160 = ("The helper function writes an arbitrary Python object directly to "
        "the stream as compact JSON, followed by a single newline character.")
# s291's text for echo_json_support_error_handling.
S291 = ("If the input object cannot be serialized by the standard library "
        "json module, the callable `echo_json` must raise the same exception "
        "type that the standard library json module would raise.")


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    for iid, text in (("echo_json", ITEM_ECHO_JSON),
                      ("echo_json_support", ITEM_SUPPORT)):
        conn.execute("INSERT INTO items (id, text, kind, approval, "
                     "approval_ver, version) VALUES (?, ?, 'in_scope', "
                     "'approved', 1, 1)", (iid, text))
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk_2', "
                 "'echo_json', 'echo_json next to echo')")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk_1_echo_json_support', 'echo_json_support', "
                 "'echo_json support')")
    for grain in (ECHO, ECHO_JSON):
        conn.execute("INSERT INTO code_index (grain, grain_kind, sym_kind) "
                     "VALUES (?, 'symbol', 'function')", (grain,))
    conn.commit()
    return conn


def _criterion(conn, cid: str, ticket: str, text: str, surface: list) -> None:
    conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                 "VALUES (?, ?, ?, ?)", (cid, ticket, text, json.dumps(surface)))
    conn.commit()


def _ruling(conn, rid: str, ask: str, per_item: dict, words: str) -> None:
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                 "verb, body_refs, seq) VALUES (?, ?, 'liaison', 'principal', "
                 "'present', ?, 1)", (ask, ask, json.dumps(list(per_item))))
    conn.execute("INSERT INTO rulings (id, ask_id, per_item, words, status, "
                 "texts) VALUES (?, ?, ?, ?, 'landed', '{}')",
                 (rid, ask, json.dumps(per_item), words))
    conn.commit()


def _respecify(conn, cid: str, text: str, surface_refs=None,
               trigger: str | None = None) -> dict:
    sb = build("terminologist", conn, mode="criterion_repair",
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    if trigger:
        sb.ctx.trigger = trigger
    kw = {} if surface_refs is None else {"surface_refs": surface_refs}
    return sb.call("criteria.respecify", id=cid, text=text, **kw)


def test_a_text_that_names_the_old_callable_keeps_its_surface(db):
    """s248's call: the text names `echo_json`, and the surface moves to
    `echo`."""
    cid = "echo_json_support_compact"
    _criterion(db, cid, "tk_1_echo_json_support", S248, [ECHO_JSON])
    with pytest.raises(ValueError) as refused:
        _respecify(db, cid, S248, [ECHO])
    said = str(refused.value)
    assert "The criterion says `echo_json`" in said
    assert f"Keep `{ECHO_JSON}`" in said


def test_a_callable_named_as_a_comparison_is_not_the_surface(db):
    """s160's call: the text names no callable, and the principal's words
    name `echo` after "the way"."""
    cid = "echo_json_compact"
    _criterion(db, cid, "tk_2", S160, ["echo_json"])
    _ruling(db, "r_dae83a8c5c", "m63",
            {"echo_json": "approve", cid: "contest"}, WORDS_64)
    with pytest.raises(ValueError) as refused:
        _respecify(db, cid, S160, [ECHO])
    said = str(refused.value)
    assert "as a comparison" in said
    assert "the way echo does" in said
    assert "Keep the surface on `echo_json`" in said


def test_a_relay_that_names_a_comparison_is_read(db):
    """The relay's own words carry the comparison, and no ruling does."""
    cid = "echo_json_compact"
    _criterion(db, cid, "tk_2", S160, ["echo_json"])
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, body_text, seq) VALUES ('m67', 'm63', 'liaison', "
               "'terminologist', 'relay', ?, ?, 2)",
               (json.dumps([cid]), "The helper prints the JSON like echo does."))
    db.commit()
    with pytest.raises(ValueError) as refused:
        _respecify(db, cid, S160, [ECHO], trigger="m67")
    assert "as a comparison" in str(refused.value)


def test_a_restore_to_the_item_callable_lands(db):
    """s291's call: the surface moves back from `echo` to `echo_json`."""
    cid = "echo_json_support_error_handling"
    _criterion(db, cid, "tk_1_echo_json_support", S291, [ECHO])
    _ruling(db, "r_5a4cf89060", "m145", {cid: "approve"}, WORDS_146)
    out = _respecify(db, cid, S291, [ECHO_JSON])
    assert out.get("surface_changed") is True
    assert out["to"] == [ECHO_JSON]


def test_a_callable_the_principal_names_as_the_thing_lands(db):
    """The principal asks for `echo` itself, with no comparison cue."""
    cid = "echo_json_compact"
    _criterion(db, cid, "tk_2", S160, [ECHO_JSON])
    _ruling(db, "r_x", "m70", {cid: "contest"},
            "Extend echo itself, do not add echo_json.")
    out = _respecify(db, cid, S160, [ECHO])
    assert out.get("surface_changed") is True
    assert out["to"] == [ECHO]


def test_a_respecify_with_no_surface_is_untouched(db):
    """No surface_refs: the move door never runs, and the old answer
    stands."""
    cid = "echo_json_compact"
    _criterion(db, cid, "tk_2", S160, [ECHO_JSON])
    _ruling(db, "r_dae83a8c5c", "m63", {cid: "contest"}, WORDS_64)
    with pytest.raises(ValueError) as refused:
        _respecify(db, cid, "The helper writes `echo` output as compact JSON.")
    said = str(refused.value)
    assert "names no surface" in said
    assert "comparison" not in said and "The criterion says" not in said
