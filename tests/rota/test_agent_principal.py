"""probes/agent_principal.py: a model in the walk's principal seat (frame 41).

The model call is stubbed. The tests read what the backend sends, where the
words land, and what the record holds.
"""
import importlib.util
import json
import sys

import pytest

from rota import paths
from rota.core.db import init_db
from rota.roles.principal import Ask, pending_asks, pending_replies

PARK = "m_park_" + "x" * 11 + "b1"


def _mod():
    sys.path.insert(0, str(paths.REPO / "probes"))
    spec = importlib.util.spec_from_file_location(
        "agent_principal", paths.REPO / "probes" / "agent_principal.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


class Stub:
    """The model: a queue of results, and every prompt it was sent."""

    def __init__(self, *results):
        self.results = list(results)
        self.sent = []

    def __call__(self, model, system, page, cwd):
        self.sent.append({"model": model, "system": system, "page": page, "cwd": cwd})
        r = self.results.pop(0)
        if isinstance(r, str):
            return {"ok": True, "words": r, "error": "", "duration_ms": 1200,
                    "total_cost_usd": 0.05}
        return r


FAIL = {"ok": False, "words": "", "error": "Not logged in\nmore", "duration_ms": None,
        "total_cost_usd": None}


def _db(tmp_path):
    return init_db(tmp_path / "r.db")


def _msg(conn, mid, verb, to_role="principal", from_role="liaison", cause=None,
         text=None, status="open"):
    seq = 1 + (conn.execute("SELECT MAX(seq) FROM messages").fetchone()[0] or 0)
    conn.execute(
        "INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, verb, "
        "body_refs, body_text, seq, status) VALUES (?,?,?,?,?,?,'[]',?,?,?)",
        (mid, cause, "t1", from_role, to_role, verb, text, seq, status))
    conn.commit()


def _agent(m, conn, tmp_path, stub, phase="sentence 2"):
    out = []
    a = m.AgentPrincipal(conn, "opus", "r", set(), phase=phase, night="133",
                         runs=tmp_path, call=stub,
                         say=lambda s, flush=False: out.append(s))
    return a, out


def _rows(tmp_path):
    return [json.loads(l) for l in (tmp_path / "r.principal.jsonl").read_text(
        encoding="utf-8").splitlines()]


def test_the_prompt_holds_the_brief_the_sentence_the_page_and_the_last_answers(tmp_path):
    m = _mod()
    stub = Stub("yes, go ahead", "fine")
    a, _ = _agent(m, _db(tmp_path), tmp_path, stub)
    a.respond(Ask(message_id="m1", verb="present", rendered="1. first page line"))
    a.respond(Ask(message_id="m2", verb="present", rendered="1. second page line"))
    first, second = stub.sent
    assert "You maintain click" in first["system"]
    assert "{{" not in first["system"]
    assert ("You work on change 2 now: Let confirm() take a default_on_eof flag"
            in first["system"])
    assert first["page"].endswith("1. first page line")
    assert "Nothing yet" in first["system"]
    assert "1. first page line" in second["system"] and "You answered: yes, go ahead" in second["system"]
    assert first["cwd"] == tmp_path / "r.principal"


def test_a_present_lands_as_reply_a_clarify_as_converse_and_nothing_writes_no_entry(tmp_path):
    m = _mod()
    conn = _db(tmp_path)
    _msg(conn, "m1", "present", text="the page")
    _msg(conn, "m2", "clarify", text="which name?")
    stub = Stub("looks right", "call it echo_json", "(nothing)")
    a, out = _agent(m, conn, tmp_path, stub)
    asks = {x.message_id: x for x in pending_asks(conn)}
    assert a.respond(asks["m1"]).verb == "reply"
    assert a.respond(asks["m2"]).verb == "converse"
    assert a.respond(asks["m1"]) is None, "once per ask"
    _msg(conn, "m3", "converse", text="done, anything else?")
    before = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    a.chat(conn, pending_replies(conn)[0])
    assert conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0] == before
    assert conn.execute("SELECT status FROM messages WHERE id='m3'").fetchone()[0] == "answered"
    head = asks["m1"].rendered.splitlines()[0][:90]
    assert out[0] == f"[m1] present: {head}  -> 'looks right'"


def test_a_failed_call_defers_once_and_the_second_stops_the_walk(tmp_path):
    m = _mod()
    stub = Stub(FAIL, FAIL)
    a, out = _agent(m, _db(tmp_path), tmp_path, stub)
    ask = Ask(message_id="m1", verb="present", rendered="p")
    assert a.respond(ask) is None
    assert out == ["PRINCIPAL ERROR m1: Not logged in"]
    with pytest.raises(m.PrincipalDown):
        a.respond(ask)


def test_nothing_on_a_page_is_a_failed_call_and_the_page_stays_unanswered(tmp_path):
    m = _mod()
    a, out = _agent(m, _db(tmp_path), tmp_path, Stub("(nothing)", "(nothing)"))
    ask = Ask(message_id="m1", verb="present", rendered="p")
    assert a.respond(ask) is None
    assert "m1" not in a.replied
    assert out == ["PRINCIPAL ERROR m1: (nothing) on a page"]
    with pytest.raises(m.PrincipalDown):
        a.respond(ask)


def test_a_page_asked_again_after_nothing_says_that_it_needs_words(tmp_path):
    m = _mod()
    stub = Stub("(nothing)", "looks right")
    a, _ = _agent(m, _db(tmp_path), tmp_path, stub)
    ask = Ask(message_id="m1", verb="present", rendered="p")
    assert a.respond(ask) is None
    assert a.respond(ask).text == "looks right"
    first, retry = stub.sent
    assert m.AGAIN not in first["page"]
    assert m.AGAIN in retry["page"] and retry["page"].endswith("\n\np")


def test_the_record_row_holds_the_page_the_words_the_cost_and_the_model(tmp_path):
    m = _mod()
    conn = _db(tmp_path)
    _msg(conn, "m1", "present", text="the page")
    a, out = _agent(m, conn, tmp_path, Stub("looks right", "nothing else, thanks"))
    a.pump(conn)
    page = pending_asks(conn)[0].rendered
    landed_id = conn.execute("SELECT id FROM messages WHERE cause_id='m1'").fetchone()[0]
    # The Liaison rules on the reply and asks back on it.
    conn.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, status) "
                 "VALUES ('r1', 'm1', ?, '{}', 'landed')", (landed_id,))
    _msg(conn, "m9", "converse", cause=landed_id, text="anything else?", status="answered")
    _msg(conn, "m8", "converse", text="all done.")
    a.chat(conn, pending_replies(conn)[0])
    a.finish()
    call, landed, _, _, nxt, chat_nxt = _rows(tmp_path)
    assert call["kind"] == "call" and call["page"] == page
    assert call["words"] == "looks right" and call["total_cost_usd"] == 0.05
    assert call["model"] == "opus" and call["night"] == "133" and call["duration_ms"] == 1200
    assert call["phase"] == "sentence 2" and call["message_id"] == "m1" and call["clock"]
    assert landed["ask_id"] == "m1" and landed["landed_id"] == landed_id and landed["as"] == "reply"
    assert nxt["kind"] == "next" and nxt["ask_id"] == "m1" and nxt["next"] == "ruling"
    assert nxt["rulings"][0]["reply_id"] == landed_id
    assert nxt["ask_backs"] == [{"id": "m9", "cause_id": landed_id, "text": "anything else?"}]
    assert chat_nxt["kind"] == "next" and chat_nxt["ask_id"] == "m8"
    assert out[-1] == "principal: 2 calls, 0.10 dollars on opus"


def test_the_binary_is_claude_bin_first_and_the_extension_folder_second(tmp_path):
    m = _mod()
    assert m.find_binary({"CLAUDE_BIN": "X:/c.exe"}, home=tmp_path) == "X:/c.exe"
    old = tmp_path / ".vscode/extensions/anthropic.claude-code-2.1.1-win32-x64/resources/native-binary"
    new = tmp_path / ".vscode/extensions/anthropic.claude-code-2.1.9-win32-x64/resources/native-binary"
    for d in (old, new):
        d.mkdir(parents=True)
        (d / "claude.exe").write_bytes(b"")
    import os
    os.utime(old / "claude.exe", (1, 1))
    assert m.find_binary({}, home=tmp_path) == str(new / "claude.exe")


def test_an_ask_back_on_an_open_page_lands_on_that_page(tmp_path):
    m = _mod()
    conn = _db(tmp_path)
    _msg(conn, "m1", "present", text="the page")
    _msg(conn, "m2", "converse", to_role="liaison", from_role="principal", cause="m1",
         text="line 2 is wrong")
    _msg(conn, "m3", "converse", cause="m2", text="should line 2 print or return?")
    a, out = _agent(m, conn, tmp_path, Stub("it prints"))
    entries = conn.execute("SELECT COUNT(*) FROM entries WHERE id LIKE 'e_p%'").fetchone()[0]
    a.chat(conn, pending_replies(conn)[0])
    new = conn.execute("SELECT cause_id, verb, body_text, status FROM messages "
                       "WHERE from_role='principal' AND id NOT IN ('m2')").fetchall()
    assert [tuple(r) for r in new] == [("m1", "converse", "it prints", "open")]
    assert conn.execute("SELECT status FROM messages WHERE id='m1'").fetchone()[0] == "open"
    assert conn.execute("SELECT status FROM messages WHERE id='m3'").fetchone()[0] == "answered"
    assert conn.execute("SELECT COUNT(*) FROM entries WHERE id LIKE 'e_p%'").fetchone()[0] == entries
    assert "The lead asks about your answer to a page." in a.call.sent[0]["page"]


def test_an_ask_back_on_a_plain_clarify_closes_it_as_the_script_words_do(tmp_path):
    m = _mod()
    conn = _db(tmp_path)
    _msg(conn, "m1", "clarify", text="which name?")
    _msg(conn, "m2", "converse", to_role="liaison", from_role="principal", cause="m1",
         text="the short one")
    _msg(conn, "m3", "converse", cause="m2", text="echo_json or dump_json?")
    a, _ = _agent(m, conn, tmp_path, Stub("echo json"))
    a.chat(conn, pending_replies(conn)[0])
    assert conn.execute("SELECT status FROM messages WHERE id='m1'").fetchone()[0] == "answered"
    assert _rows(tmp_path)[-1]["as"] == "converse"


def test_a_park_ask_answer_lands_as_reply_and_the_ask_stays_open(tmp_path):
    m = _mod()
    conn = _db(tmp_path)
    _msg(conn, PARK, "clarify", text="b1 stopped. commit or contest?")
    a, _ = _agent(m, conn, tmp_path, Stub("fix it and commit again"))
    ask = pending_asks(conn)[0]
    assert a.respond(ask).verb == "reply"
    a.replied.discard(PARK)
    a.call.results.append("fix it and commit again")
    a.pump(conn)
    assert conn.execute("SELECT status FROM messages WHERE id=?", (PARK,)).fetchone()[0] == "open"
    assert conn.execute("SELECT COUNT(*) FROM messages WHERE cause_id=?", (PARK,)).fetchone()[0] == 1
