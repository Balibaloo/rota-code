"""
The page and the input are one contract.

Measured as the principal (2026-09-04): the page had stopped showing ids, the
parser still demanded them, and the page promised "say what's wrong in your
own words" while no input could carry words with a verdict. The only reply
that worked was "lgtm". `render_page` numbers the rulable rows and returns
their order; `parse_reply` reads a reply against that order. Both seats use
them.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.roles.principal import Ask, parse_reply, pending_asks


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _present(db):
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e1','principal','tip calculator pls',1)")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, "
               "status) VALUES ('s1','e1',0,18,'tip calculator pls','ratified')")
    for iid, kind, text in (
        ("how_it_works", "in_scope", "The user types the bill and a percentage."),
        ("calculate_tip", "in_scope", "The software calculates the tip."),
    ):
        db.execute("INSERT INTO items (id, text, kind, approval, "
                   "approval_ver, version) VALUES (?,?,?,'draft',0,1)",
                   (iid, text, kind))
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, status, "
               "author) VALUES ('l_1','how_it_works','items',"
               "'the percentage is typed each time','open','vision_keeper')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m9','th','liaison','principal',"
               "'present',?,1,'open')",
               (json.dumps(["calculate_tip", "how_it_works", "s1", "l_1"]),))
    db.commit()
    return pending_asks(db)[0]


def test_the_page_numbers_its_rows_in_the_order_it_shows_them(db):
    ask = _present(db)
    page = ask.rendered
    assert '1. "tip calculator pls"' in page
    assert "2. The user types the bill" in page
    assert "3. The software calculates the tip." in page
    assert "4. the percentage is typed each time" in page
    assert ask.order == ["s1", "how_it_works", "calculate_tip", "l_1"], ask.order
    assert "Name a line to correct only that line." in page
    assert "how_it_works" not in page and "l_1" not in page


def test_words_land_as_a_reply_and_the_page_stays_open(db):
    """
    Ruled 2026-09-10: no parser reads the principal's words. "ok", "no",
    "4: wrong" and a sentence all land the same way: a reply the Liaison
    reads in `landing` mode, with the page still open under it.
    """
    from rota.roles.principal import land

    ask = _present(db)
    for word in ("ok", "no", "4: a fixed 15 percent", "just bill and a percent"):
        a = parse_reply(ask, word)
        assert a.verb == "reply" and a.text == word
    msg = land(db, ask, parse_reply(ask, "4: a fixed 15 percent, nobody types it"))
    row = db.execute("SELECT * FROM messages WHERE id = ?", (msg,)).fetchone()
    assert row["from_role"] == "principal" and row["verb"] == "converse"
    assert row["cause_id"] == "m9" and row["status"] == "open"
    assert row["body_text"] == "4: a fixed 15 percent, nobody types it"
    assert json.loads(row["body_refs"]) == ask.refs
    assert db.execute("SELECT status FROM messages WHERE id = 'm9'").fetchone()[0] == "open"
    assert pending_asks(db)[0].message_id == "m9"
    # The words are on the transcript, mechanically.
    assert db.execute("SELECT count(*) FROM entries WHERE author = 'principal' "
                      "AND text LIKE '4: a fixed%'").fetchone()[0] == 1
    # A blank reply lands nothing.
    assert land(db, ask, parse_reply(ask, "   ")) is None


def _reply(db, ask, text):
    from rota.roles.principal import land

    return land(db, ask, parse_reply(ask, text))


def test_the_reply_wakes_the_liaison_in_landing_with_the_page(db):
    from rota.core.predicates import Wake
    from rota.core.runner import _mode_key, resolve_inbound

    ask = _present(db)
    msg = _reply(db, ask, "2 is wrong, the percentage is fixed")
    wake = Wake(role="liaison", kind="message", detail="converse",
                message_id=msg, refs=ask.refs)
    assert _mode_key(wake, db) == "landing"
    inbound = resolve_inbound(db, wake)
    landing = inbound["landing"]
    assert landing["page_kind"] == "present"
    assert landing["reply"] == "2 is wrong, the percentage is fixed"
    assert landing["lines"] == {"1": "s1", "2": "how_it_works",
                                "3": "calculate_tip", "4": "l_1"}
    assert landing["line_rows"]["l_1"]["table"] == "ledger"
    assert "2. The user types the bill" in landing["page"]
    assert "earlier_exchange" not in landing
    # A page this size fits, so the rows travel whole and nothing says they
    # were cut.
    assert "rows_not_shown" not in landing


def _big_present(db, lines=77):
    """A page the size of night 85's: twelve senses, sixty constraints and
    four items, one statement at the top."""
    refs = ["s1"]
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e1','principal','a command line tool like click',1)")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
               "text, status) VALUES ('s1','e1',0,29,'a command line tool "
               "like click','ratified')")
    for i in range(12):
        db.execute("INSERT INTO glossary_terms (id, term, sense_short, "
                   "sense_body) VALUES (?,?,?,?)",
                   (f"g{i}", f"term_{i}",
                    f"The {i}th word the code uses for a command line idea.",
                    f"A `term_{i}` is the object the decorator builds when a "
                    f"function is marked as a command. It carries the name, "
                    f"the parameters and the callback, and the runner invokes "
                    f"it with a context."))
        refs.append(f"g{i}")
    for i in range(lines - 17):
        db.execute("INSERT INTO constraints (id, headline, text) VALUES (?,?,?)",
                   (f"k{i}", f"the {i}th decorator keeps its name",
                    f"Users of the `option_{i}` decorator in "
                    f"`src/click.decorators` would break if this were renamed."))
        refs.append(f"k{i}")
    for i in range(4):
        db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                   "version) VALUES (?,?,'in_scope','draft',0,1)",
                   (f"i{i}", f"The tool reads argument {i} from the line."))
        refs.append(f"i{i}")
    assert len(refs) == lines
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m9','th','liaison',"
               "'principal','present',?,1,'open')", (json.dumps(refs),))
    db.commit()
    return pending_asks(db)[0]


def _prompt_tokens(system: str, user: str) -> int:
    """The real tokeniser when the server answers, the measured ratio when it
    does not. A character count alone is what hid this: the wake was 64,294
    characters and nobody had a token number for it until night 85."""
    import random
    import urllib.request

    payload = {"model": "qwen3:8b", "stream": False,
               "messages": [{"role": "system",
                             "content": "zz%d " % random.randrange(10 ** 9) + system},
                            {"role": "user", "content": user}],
               "options": {"num_ctx": 40960, "num_predict": 1,
                           "temperature": 0}}
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            count = json.loads(resp.read().decode("utf-8")).get("prompt_eval_count")
        if count:
            return int(count)
    except Exception:                                          # noqa: BLE001
        pass
    # 3.97 characters to the token, measured against qwen3:8b on 2026-09-18.
    return int((len(system) + len(user)) / 3.97)


def test_the_landing_wake_for_a_77_line_present_fits_the_window(db):
    """
    The wall of night 85 (2026-09-18). The landing wake for a 77-line present
    measured 17,220 tokens against a 12,288 window. Ollama collapses an
    oversized prompt to `num_ctx / 2 + 2` and keeps the tail, so the brief at
    the front is what dies: both seats answered as generic assistants, made no
    tool call, and the present stayed open. The budget is half the window.
    """
    from rota.core.predicates import Wake
    from rota.core.runner import build_prompt, push_working_set, resolve_inbound
    from rota.core.sandbox import build
    from rota.roles import prompts

    ask = _big_present(db)
    msg = _reply(db, ask, "line 3 is not what I meant")
    wake = Wake(role="liaison", kind="message", detail="converse",
                message_id=msg, refs=ask.refs)
    sb = build("liaison", db, mode="normal", session_id="sess_big",
               allow=prompts.mode_tools("liaison", "landing"))
    inbound = resolve_inbound(db, wake)
    system, user = build_prompt(
        "liaison", sb, wake, push_working_set("liaison", sb, wake),
        prompts.compose("liaison", "landing"), inbound)

    landing = inbound["landing"]
    assert "line_rows" not in landing, "the rows did not fit and travelled anyway"
    assert "resolved_refs" not in inbound, "the same rows, under the wake's key"
    assert "refs" not in inbound, "the same 77 ids, a third time"
    assert "rulings.line" in landing["rows_not_shown"], "the cut must say what to call"
    assert landing["lines"]["1"].endswith("(statements)"), landing["lines"]["1"]

    tokens = _prompt_tokens(system, user)
    assert tokens < 6100, f"the landing wake is {tokens} tokens: half a 12,288 window"


def test_the_landing_seat_reads_a_row_it_was_not_sent(db):
    """The row behind a numbered line, on demand. The wake no longer carries
    the rows, so the one question the page does not answer has a tool."""
    ask = _present(db)
    sb, _ = _landing(db, ask, "what is line 4 about?")

    out = sb.call("rulings.line", line="4")
    assert out["ref"] == "l_1"
    assert out["row"]["table"] == "ledger"
    assert out["row"]["about_ref"] == "how_it_works"
    # By id as well as by number, and nothing else.
    assert sb.call("rulings.line", line="s1")["row"]["table"] == "statements"
    with pytest.raises(ValueError, match="not a line of the page"):
        sb.call("rulings.line", line="9")


def _landing(db, ask, text):
    from rota.core.sandbox import build
    from rota.roles import prompts

    msg = _reply(db, ask, text)
    sb = build("liaison", db, mode="normal", session_id="sess_land",
               allow=prompts.mode_tools("liaison", "landing"))
    sb.ctx.trigger = msg
    return sb, msg


def test_the_liaison_records_the_ruling_by_line_and_the_door_lands_it(db):
    from rota.roles.principal import apply_rulings

    ask = _present(db)
    sb, msg = _landing(db, ask, "4 is wrong: a fixed 15 percent, nobody types it")
    out = sb.call("rulings.rule",
                  rulings={"1": "approve", "2": "approve", "3": "approve", "4": "contest"},
                  words="4 is wrong: a fixed 15 percent, nobody types it")
    assert out["per_item"] == {"s1": "approve", "how_it_works": "approve",
                               "calculate_tip": "approve", "l_1": "contest"}
    w = [w for w in sb.ctx.writes if w[0] == "rulings"]
    assert len(w) == 1 and w[0][2]["ask_id"] == "m9" and w[0][2]["reply_id"] == msg
    # One reading per reply.
    with pytest.raises(ValueError, match="already read"):
        sb.call("rulings.rule", rulings={"1": "approve", "2": "approve",
                                         "3": "approve", "4": "approve"})
    # The row lands after the commit, through the one door.
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words) "
               "VALUES ('r1', 'm9', ?, ?, ?)",
               (msg, json.dumps(out["per_item"]), w[0][2]["words"]))
    created = apply_rulings(db)
    assert len(created) == 1
    verdict = db.execute("SELECT * FROM messages WHERE id = ?", (created[0],)).fetchone()
    assert verdict["from_role"] == "principal" and verdict["verb"] == "verdict"
    assert verdict["cause_id"] == "m9"
    assert db.execute("SELECT status FROM messages WHERE id = 'm9'").fetchone()[0] == "answered"
    assert db.execute("SELECT status FROM rulings WHERE id = 'r1'").fetchone()[0] == "landed"
    # The contested assumption is overruled at the keypress, with the words.
    assert db.execute("SELECT status FROM ledger WHERE id = 'l_1'").fetchone()[0] == "resolved"
    d = db.execute("SELECT text FROM decisions WHERE resolves_ledger = 'l_1'").fetchone()
    assert "overruled at signoff: 4 is wrong" in d["text"]
    assert db.execute("SELECT approval FROM items WHERE id = 'how_it_works'").fetchone()[0] == "contested"
    assert db.execute("SELECT approval FROM items WHERE id = 'calculate_tip'").fetchone()[0] == "approved"
    # Landing twice lands nothing more: the ask is closed.
    assert apply_rulings(db) == []


def test_the_ruling_door_holds_the_page(db):
    ask = _present(db)
    sb, _ = _landing(db, ask, "fine")
    with pytest.raises(ValueError, match="not a line of the page"):
        sb.call("rulings.rule", rulings={"1": "approve", "2": "approve",
                                         "3": "approve", "9": "approve"})
    with pytest.raises(ValueError, match="lines 3, 4 have no ruling"):
        sb.call("rulings.rule", rulings={"1": "approve", "2": "approve"})
    with pytest.raises(ValueError, match="not a ruling"):
        sb.call("rulings.rule", rulings={"1": "yes", "2": "approve",
                                         "3": "approve", "4": "approve"})
    with pytest.raises(ValueError, match="words is empty"):
        sb.call("rulings.rule", rulings={"1": "approve", "2": "contest",
                                         "3": "approve", "4": "approve"})
    # A row id names a line as well as its number does.
    out = sb.call("rulings.rule", rulings={"s1": "approve", "how_it_works": "approve",
                                           "3": "approve", "l_1": "approve"})
    assert set(out["per_item"].values()) == {"approve"}


def test_no_open_page_means_no_ruling(db):
    from rota.core.sandbox import build
    from rota.roles import prompts

    _present(db)
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, body_text, seq, status) VALUES ('m_free','th','principal',"
               "'liaison','converse','[]','hello',5,'open')")
    sb = build("liaison", db, mode="normal", session_id="sess_x",
               allow=prompts.mode_tools("liaison", "landing"))
    sb.ctx.trigger = "m_free"
    with pytest.raises(ValueError, match="no open page"):
        sb.call("rulings.rule", rulings={"1": "approve"})


def test_a_stale_ruling_lands_nothing(db):
    from rota.roles.principal import apply_rulings

    ask = _present(db)
    msg = _reply(db, ask, "ok")
    db.execute("UPDATE messages SET status = 'answered' WHERE id = 'm9'")
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item) VALUES "
               "('r_old', 'm9', ?, ?)", (msg, json.dumps({"s1": "approve"})))
    assert apply_rulings(db) == []
    assert db.execute("SELECT status FROM rulings WHERE id = 'r_old'").fetchone()[0] == "landed"


def test_a_clarify_reply_is_the_answer(db):
    ask = Ask(message_id="m1", verb="clarify", refs=["c_1"])
    a = parse_reply(ask, "exactly what the criteria say")
    assert a.verb == "converse" and a.text == "exactly what the criteria say"


def test_a_page_with_no_line_takes_an_empty_ruling(db):
    """tipsAS (2026-09-11): the touch note has no numbered line; the Liaison's
    empty map was refused and the page stayed open."""
    from rota.core.sandbox import build
    from rota.roles import prompts

    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i1','split','in_scope','approved',1,1)")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1','i1','pending')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, body_refs, "
               "body_text, seq, status) VALUES ('m_t','th','liaison','principal','present',"
               "'[\"b1\"]','Nothing here has been read yet.',1,'open')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, body_refs, "
               "body_text, seq, status, cause_id) VALUES ('m_r','th','principal','liaison',"
               "'converse','[\"b1\"]','ok',2,'open','m_t')")
    db.commit()
    sb = build("liaison", db, mode="normal", session_id="s_l",
               allow=prompts.mode_tools("liaison", "landing"))
    sb.ctx.trigger = "m_r"
    out = sb.call("rulings.rule", rulings={}, words="ok")
    assert out["per_item"] == {"b1": "approve"} and "acknowledged" in out["note"]
