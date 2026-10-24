"""
A criterion's id holds one text: a second `criteria.specify` of an id on
the same ticket with other words is refused (frame 257, option A of
`plans/frame310-provenance.md`).

Night 160's Terminologist s111 wrote four texts under `echo_json_helper` on
`tk_1`, and each returned OK. The last text won at commit. The third text
held the principal's "followed by a newline", the Tester never saw it, and
bg_1 died. a9cb55de refused a reused id on another ticket only. Its own
sentence is "An id you invent is yours once".
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import prompts

# The item and the ticket of nights 149 and 160, from their databases.
_ITEM = ("Add an echo_json(obj) helper next to echo that prints an object as "
         "compact JSON on one line, followed by a newline.")

# s111's calls at seq 7 and 8 on night 160. s114's calls at seq 7 and 8 on
# night 149 are the same to the byte.
_FIRST = ('The function `echo_json` accepts any Python object and outputs its '
          'string representation using `json.dumps(obj, separators=(",", ":"))`, '
          'ensuring compact formatting with no spaces.')
_SECOND = ('The output of `echo_json` must end with exactly one newline '
           'character (`\n`) after the JSON string, regardless of whether the '
           'input object is empty or not.')


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('echo_json', ?, 'in_scope', 'approved', 1, 1)",
                 (_ITEM,))
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk_1', 'echo_json', ?)", (_ITEM,))
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk_2', 'echo_json', 'the second slice')")
    conn.commit()
    return conn


def _seat(db):
    return build("terminologist", db, mode="normal",
                 allow=prompts.mode_tools("terminologist", "criteria"))


def _specify(sb, text, term_refs, ticket_id="tk_1"):
    return sb.call("criteria.specify", id="echo_json_helper",
                   ticket_id=ticket_id, text=text, term_refs=term_refs,
                   surface_refs=["echo_json"])


def _texts(sb, cid):
    return [w[2]["text"] for w in sb.ctx.writes
            if w[0] == "criteria" and w[1] == cid]


@pytest.mark.parametrize("night", ["160 s111", "149 s114"])
def test_a_second_text_under_one_id_is_refused_with_the_new_id_route(db, night):
    sb = _seat(db)
    _specify(sb, _FIRST, ["stream"])
    with pytest.raises(ValueError) as exc:
        _specify(sb, _SECOND, ["line"])
    said = str(exc.value)
    assert "echo_json_helper" in said
    assert "The function `echo_json` accepts any Python object" in said
    assert "criteria.specify" in said and "new id" in said
    assert "criteria.respecify" not in said
    # The first text stands, and no second write replaces it at commit.
    assert _texts(sb, "echo_json_helper") == [_FIRST]


def test_the_refused_text_lands_under_a_new_id(db):
    sb = _seat(db)
    _specify(sb, _FIRST, ["stream"])
    with pytest.raises(ValueError):
        _specify(sb, _SECOND, ["line"])
    out = sb.call("criteria.specify", id="echo_json_newline", ticket_id="tk_1",
                  text=_SECOND, term_refs=["line"], surface_refs=["echo_json"])
    assert out["id"] == "echo_json_newline"
    assert _texts(sb, "echo_json_newline") == [_SECOND]


def test_a_landed_criterion_is_replaced_through_the_vision_keeper(db):
    db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
               "VALUES ('echo_json_helper', 'tk_1', ?, '[]')", (_FIRST,))
    db.commit()
    sb = _seat(db)
    with pytest.raises(ValueError) as exc:
        _specify(sb, _SECOND, ["line"])
    said = str(exc.value)
    assert "msg.challenge_vision_keeper" in said
    assert "criteria.respecify" not in said
    assert _texts(sb, "echo_json_helper") == []


def test_the_same_text_twice_keeps_the_twin_refusal(db):
    sb = _seat(db)
    _specify(sb, _FIRST, ["stream"])
    with pytest.raises(ValueError, match=r"^those are echo_json_helper's words "
                       r"already, on the same ticket\. The same words are the "
                       r"same criterion; if the ticket needs a second "
                       r"criterion, it needs a second sentence$"):
        _specify(sb, _FIRST, ["stream"])
    assert _texts(sb, "echo_json_helper") == [_FIRST]


def test_the_same_id_on_another_ticket_keeps_its_refusal(db):
    sb = _seat(db)
    _specify(sb, _FIRST, ["stream"])
    with pytest.raises(ValueError, match=r"'echo_json_helper' is already "
                       r"tk_1's criterion\. An id you invent is yours once "
                       r"-- tk_2 needs its own"):
        _specify(sb, _SECOND, ["line"], ticket_id="tk_2")
