"""
Frame 193, pass 3: the precondition of the shift question, on night 138's
turns.

The rows are copied from `.rota/clickI.db` of night 138, read with
`mode=ro`, and rebuilt inline, as the pass 1 and pass 2 tests do. The design
is `plans/frame193-design.md`, section 2.G.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import backfill_ruled_refs, init_db
from rota.core.runner import CURRENT_REQUEST_RELATION, resolve_inbound
from rota.core.scheduler import Wake
from rota.roles.principal import contested_statement, ratified_request
from rota.testkit.fixtures import seed_verdict

S1 = ("Add an echo_json(obj) helper next to echo that prints an object as compact "
      "JSON on one line, followed by a newline.")
P2 = ("Let confirm() take a default_on_eof flag: when stdin is closed it returns the "
      "default instead of aborting.")
P3 = ("Give version_option a show_python flag that appends the running Python "
      "version to the message.")
M138 = ("They are two separate changes, and I am on the confirm change now. Please "
        "restate the request as letting confirm take a default_on_eof flag that "
        "returns the default when stdin is closed instead of aborting.")
CONTEST = "r_4212749ea1"


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _msg(db, mid: str, seq: int, frm: str, to: str, verb: str, refs: list,
         cause: str | None = None, status: str = "answered") -> None:
    db.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, to_role, "
               "verb, body_refs, seq, status) VALUES (?, 't_p1', ?, ?, ?, ?, ?, ?, ?)",
               (mid, cause, frm, to, verb, json.dumps(refs), seq, status))


def _entry(db, eid: str, text: str, ts: int) -> None:
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES (?, "
               "'principal', ?, ?)", (eid, text, ts))


def _night138(db, *, upto: str) -> None:
    """Night 138's rows. `upto` is `m_p2`, the wake of s270, `m139`, the
    wake of s273, or `m_p3`, the wake of s353."""
    _entry(db, "e_p1", S1, 6)
    _msg(db, "m_p1", 13, "principal", "liaison", "converse", ["e_p1"])
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, "
               "status) VALUES ('s1', 'e_p1', 0, ?, ?, 'ratified')", (len(S1), S1))
    _msg(db, "m14", 15, "liaison", "principal", "confirm", ["s1"], cause="m_p1")
    _msg(db, "m15", 16, "principal", "liaison", "converse", ["s1"], cause="m14")
    _msg(db, "m17", 18, "principal", "liaison", "verdict", ["s1"], cause="m14")
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, status, "
               "verdict_id) VALUES ('r_9cb52c76c6', 'm14', 'm15', '{\"s1\": "
               "\"approve\"}', 'ok', 'landed', 'm17')")
    backfill_ruled_refs(db)
    _entry(db, "e_p2", P2, 38)
    _msg(db, "m_p2", 136, "principal", "liaison", "converse", ["e_p2"],
         status="open" if upto == "m_p2" else "answered")
    if upto == "m_p2":
        db.commit()
        return
    _msg(db, "m135", 137, "liaison", "principal", "confirm", ["s1"], cause="m_p2")
    _entry(db, "e_m138", M138, 40)
    _msg(db, "m138", 140, "principal", "liaison", "converse", ["s1"], cause="m135")
    _msg(db, "m139", 141, "principal", "liaison", "verdict", ["s1"], cause="m135",
         status="open" if upto == "m139" else "answered")
    seed_verdict(db, "m139", '{\"s1\": \"contest\"}')
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, status, "
               "verdict_id) VALUES (?, 'm135', 'm138', '{\"s1\": \"contest\"}', ?, "
               "'landed', 'm139')", (CONTEST, M138))
    backfill_ruled_refs(db)
    if upto == "m139":
        db.commit()
        return
    _entry(db, "e_p3", P3, 66)
    _msg(db, "m_p3", 217, "principal", "liaison", "converse", ["e_p3"], status="open")
    db.commit()


def _sandbox(db, mode: str, trigger: str, entry: str | None):
    from rota.core.sandbox import build
    from rota.roles import prompts

    sb = build("liaison", db, mode="normal", session_id="sess_p3",
               allow=prompts.mode_tools("liaison", mode))
    sb.ctx.trigger = trigger
    sb.ctx.entry_id = entry
    return sb


# 2.G.1: the wake says what `current_request` is.

def test_the_wake_says_what_current_request_is(db):
    """s270's wake: s1 is the request before the new words, and the block
    carries the sentence that says when the words continue it."""
    _night138(db, upto="m_p2")
    out = resolve_inbound(db, Wake("liaison", "message", "m_p2"))
    assert out["current_request"] == {
        "statement": "s1", "text": S1, "relation": CURRENT_REQUEST_RELATION}
    assert CURRENT_REQUEST_RELATION == (
        "This is the request before these words. The new words continue it only "
        "when they name the same function or the same feature. Otherwise they are "
        "a new request, and you leave `supersedes` out.")


def test_the_converse_brief_has_no_night_request_in_its_example():
    from rota.roles import prompts

    text = prompts.compose("liaison", "converse")
    start = text.index("The wake carries `current_request`")
    para = text[start:text.index("When the wake has no `current_request`", start)]
    for word in ("version_option", "echo_json", "default_on_eof"):
        assert word not in para
    assert "--color" in para and "--quiet" in para
    assert ('After a request about `echo`,\n"let confirm take a flag" names another '
            'function, so it is a new request with no\n`supersedes`.') in para


# 2.G.2: the confirm door reads the trigger entry.

def test_s270s_confirm_of_the_earlier_statement_is_refused(db):
    _night138(db, upto="m_p2")
    sb = _sandbox(db, "converse", "m_p2", "e_p2")
    sb.call("brief.intake", verdict="work")
    with pytest.raises(ValueError) as err:
        sb.call("msg.confirm_principal", refs=["s1"])
    assert str(err.value) == (
        "The words that woke you, `e_p2`, have no statement. Segment them with "
        "`brief.segment` and confirm that statement. If they ask for nothing, "
        "call no confirm.")
    assert not sb.ctx.outbound


def test_a_confirm_of_the_new_words_statement_is_admitted(db):
    _night138(db, upto="m_p2")
    sb = _sandbox(db, "converse", "m_p2", "e_p2")
    sb.call("brief.intake", verdict="work")
    sb.call("brief.segment", id="s2", span_start=0, span_end=len(P2), text=P2)
    sb.call("msg.confirm_principal", refs=["s2"])
    assert [m["body_refs"] for m in sb.ctx.outbound] == [["s2"]]


def test_a_staged_statement_of_the_entry_admits_the_earlier_one_beside_it(db):
    """The door asks for a statement of the trigger entry, staged or stored.
    With one, an earlier statement may ride beside it."""
    _night138(db, upto="m_p2")
    sb = _sandbox(db, "converse", "m_p2", "e_p2")
    sb.call("brief.intake", verdict="work")
    sb.call("brief.segment", id="s2", span_start=0, span_end=len(P2), text=P2)
    sb.call("msg.confirm_principal", refs=["s1", "s2"])
    assert len(sb.ctx.outbound) == 1


def test_words_said_again_confirm_the_earlier_statement(db):
    """The segment door refuses words already on file as a proposed statement
    and names the confirm. This door admits that confirm."""
    _night138(db, upto="m_p2")
    db.execute("UPDATE entries SET text = ? WHERE id = 'e_p2'", (S1,))
    db.execute("UPDATE statements SET status = 'proposed' WHERE id = 's1'")
    db.commit()
    sb = _sandbox(db, "converse", "m_p2", "e_p2")
    sb.call("brief.intake", verdict="work")
    with pytest.raises(ValueError) as err:
        sb.call("brief.segment", id="s2", span_start=0, span_end=len(S1), text=S1)
    assert str(err.value) == ("these words are s1, which waits for the principal. "
                              "Send msg.confirm_principal(refs=['s1'])")
    sb.call("msg.confirm_principal", refs=["s1"])
    assert len(sb.ctx.outbound) == 1


def test_words_of_another_entry_are_not_said_again(db):
    """s270's shape: the earlier statement's words are not in the trigger
    entry, so the segment door names the entry and never the confirm that
    the confirm door would refuse (the review of a9de65d5, finding 1)."""
    _night138(db, upto="m_p2")
    db.execute("UPDATE statements SET status = 'proposed' WHERE id = 's1'")
    db.commit()
    sb = _sandbox(db, "converse", "m_p2", "e_p2")
    sb.call("brief.intake", verdict="work")
    with pytest.raises(ValueError) as err:
        sb.call("brief.segment", id="s2", span_start=0, span_end=len(S1), text=S1)
    assert "does not appear in the entry you are segmenting" in str(err.value)
    assert "msg.confirm_principal" not in str(err.value)


def test_the_earlier_entrys_words_point_back_to_the_trigger_entry(db):
    """The pass 3c re-record: the seat segmented s1's words with span_entry set
    to the earlier entry. The refusal names the entry that woke it and no
    confirm of s1."""
    _night138(db, upto="m_p2")
    sb = _sandbox(db, "converse", "m_p2", "e_p2")
    sb.call("brief.intake", verdict="work")
    with pytest.raises(ValueError) as err:
        sb.call("brief.segment", id="s1", span_start=0, span_end=len(S1), text=S1,
                span_entry="e_p1", supersedes="s1")
    assert str(err.value) == ("these words are s1, from another entry. Leave "
                              "span_entry out. Segment the words of `e_p2` with "
                              "brief.segment.")


def test_every_ref_from_another_entry_must_be_said_again(db):
    """One ref said again does not carry a second one that was not, and a
    statement inside a longer word is not said again (finding 4)."""
    _night138(db, upto="m_p2")
    db.execute("UPDATE entries SET text = ? WHERE id = 'e_p2'", (S1,))
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, "
               "status) VALUES ('s0', 'e_p1', 0, 4, 'echo', 'proposed')")
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES ('e_p0', "
               "'principal', 'Add a json helper.', 1)")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, "
               "status) VALUES ('s5', 'e_p0', 0, 18, 'Add a json helper.', 'proposed')")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, "
               "status) VALUES ('s6', 'e_p0', 0, 3, 'echo_', 'proposed')")
    db.commit()
    sb = _sandbox(db, "converse", "m_p2", "e_p2")
    sb.call("brief.intake", verdict="work")
    with pytest.raises(ValueError, match="have no statement"):
        sb.call("msg.confirm_principal", refs=["s1", "s5"])
    # "echo_" sits inside "echo_json", so it is no whole word of the entry.
    with pytest.raises(ValueError, match="have no statement"):
        sb.call("msg.confirm_principal", refs=["s6"])
    sb.call("msg.confirm_principal", refs=["s1", "s0"])
    assert len(sb.ctx.outbound) == 1


# 2.G.3: verdict mode has a contest branch, and the ratify door holds it.

def test_s273s_ratify_of_the_contested_statement_is_refused(db):
    _night138(db, upto="m139")
    sb = _sandbox(db, "verdict", "m139", None)
    with pytest.raises(ValueError) as err:
        sb.call("brief.ratify", id="s1")
    assert str(err.value) == (
        f"the principal contested s1 in {CONTEST}, so s1 is not ratified and not "
        "delivered. Ratify only what they accepted. When they accepted nothing, "
        "end the session with no call")
    assert not sb.ctx.writes


def test_a_newer_approve_lifts_the_contest(db):
    """An approve on a later confirm page lifts the doors and offers the wake
    the statement again."""
    _night138(db, upto="m139")
    _msg(db, "m300", 300, "liaison", "principal", "confirm", ["s1"], cause="m_p2")
    _msg(db, "m301", 301, "principal", "liaison", "converse", ["s1"], cause="m300")
    _msg(db, "m302", 302, "principal", "liaison", "verdict", ["s1"], cause="m300",
         status="open")
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, status, "
               "verdict_id) VALUES ('r_ok', 'm300', 'm301', '{\"s1\": \"approve\"}', "
               "'ok', 'landed', 'm302')")
    backfill_ruled_refs(db)
    db.commit()
    assert ratified_request(db, before_seq=301) is None
    assert ratified_request(db, before_seq=400)["statements"] == ["s1"]
    sb = _sandbox(db, "verdict", "m302", None)
    sb.call("brief.ratify", id="s1")
    sb.call("msg.deliver_vision_keeper", refs=["s1"])
    assert [w[1] for w in sb.ctx.writes] == ["s1"]
    assert len(sb.ctx.outbound) == 1


def test_an_approve_off_a_confirm_page_lifts_nothing(db):
    """The doors read the confirm pages, as the wake does. A clarify's approve
    after the contest leaves all three refusing (finding 3)."""
    _night138(db, upto="m139")
    _msg(db, "m400", 400, "liaison", "principal", "clarify", ["s1"])
    _msg(db, "m401", 401, "principal", "liaison", "converse", ["s1"], cause="m400")
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, status) "
               "VALUES ('r_cl', 'm400', 'm401', '{\"s1\": \"approve\"}', 'no', 'landed')")
    backfill_ruled_refs(db)
    db.commit()
    assert ratified_request(db, before_seq=500) is None
    sb = _sandbox(db, "verdict", "m139", None)
    with pytest.raises(ValueError, match=CONTEST):
        sb.call("brief.ratify", id="s1")
    with pytest.raises(ValueError, match=CONTEST):
        sb.call("msg.deliver_vision_keeper", refs=["s1"])


def test_the_verdict_brief_has_the_contest_branch():
    from rota.roles import prompts

    text = prompts.compose("liaison", "verdict")
    one, two = text.index("**Step 1"), text.index("**Step 2")
    branch = text.index("**A contested statement is not ratified and not delivered.**")
    assert one < branch < two
    assert "When every statement on the page is contested, end the session with no\ncall." in text
    assert "always" not in text[two:]


# 2.G.4: `ratified_request` skips a statement the principal called separate.

def test_after_m138s_contest_the_wake_has_no_current_request(db):
    _night138(db, upto="m_p3")
    assert contested_statement(db, "s1", confirm_only=True) == CONTEST
    assert ratified_request(db, before_seq=217) is None
    out = resolve_inbound(db, Wake("liaison", "message", "m_p3"))
    assert "current_request" not in out


def test_before_the_contest_the_request_stands(db):
    """The contest's reply came at seq 140, so a read before it keeps s1."""
    _night138(db, upto="m_p3")
    assert ratified_request(db, before_seq=136)["statements"] == ["s1"]


def test_after_the_contest_supersedes_is_told_to_leave_it_out(db):
    """s353 set `supersedes='s1'`. The door reads the same function as the
    wake, so it refuses s1 once the principal contested it."""
    _night138(db, upto="m_p3")
    sb = _sandbox(db, "converse", "m_p3", "e_p3")
    sb.call("brief.intake", verdict="work")
    with pytest.raises(ValueError) as err:
        sb.call("brief.segment", id="s2", span_start=0, span_end=len(P3), text=P3,
                supersedes="s1")
    assert str(err.value) == ("There is no earlier request on the page, so leave "
                              "supersedes out.")


# 2.G.5: the supersedes door reads the words.

def _follow_up(db, earlier: str, words: str):
    """A ratified request `s1` with the text `earlier`, and an open uncaused
    converse `m_p9` whose entry holds `words`."""
    _entry(db, "e_p1", earlier, 1)
    _msg(db, "m_p1", 1, "principal", "liaison", "converse", ["e_p1"])
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, "
               "status) VALUES ('s1', 'e_p1', 0, ?, ?, 'ratified')",
               (len(earlier), earlier))
    _entry(db, "e_p9", words, 2)
    _msg(db, "m_p9", 9, "principal", "liaison", "converse", ["e_p9"], status="open")
    db.commit()
    sb = _sandbox(db, "converse", "m_p9", "e_p9")
    sb.call("brief.intake", verdict="work")
    return sb


def _supersede(sb, words: str):
    return sb.call("brief.segment", id="s9", span_start=0, span_end=len(words),
                   text=words, supersedes="s1")


SHARE_NO_WORD = (
    "`supersedes` names `s1`, and the new words share no word with it. A "
    "follow-up names the function or the feature it continues. Leave "
    "`supersedes` out when the words are about another function.")


def test_night138s_pair_shares_no_word_and_is_refused(db):
    """s353 set s2's supersedes to s1: version_option against echo_json."""
    sb = _follow_up(db, S1, P3)
    with pytest.raises(ValueError) as err:
        _supersede(sb, P3)
    assert str(err.value) == SHARE_NO_WORD
    assert not [w for w in sb.ctx.writes if w[0] == "statements"]
    # The same words with supersedes left out are admitted.
    sb.call("brief.segment", id="s9", span_start=0, span_end=len(P3), text=P3)


def test_the_brief_follow_up_pair_is_admitted(db):
    sb = _follow_up(db, P3, "also show the version as major.minor")
    out = _supersede(sb, "also show the version as major.minor")
    assert out["id"] == "s9"
    (row,) = [w for w in sb.ctx.writes if w[0] == "statements"]
    assert row[2]["supersedes"] == "s1"


def test_the_confirm_words_share_no_word_with_echo_json(db):
    """m_p2's words against s1, the pair of s270."""
    sb = _follow_up(db, S1, P2)
    with pytest.raises(ValueError) as err:
        _supersede(sb, P2)
    assert str(err.value) == SHARE_NO_WORD


def test_a_follow_up_that_names_default_on_eof_is_admitted(db):
    """The stoplist erased `default_on_eof`. A shared whole identifier now
    admits the follow-up (the review of f55c3030, finding 1)."""
    words = "Let default_on_eof default to False."
    sb = _follow_up(db, P2, words)
    out = _supersede(sb, words)
    assert out["id"] == "s9"


def test_content_words_split_on_underscore_and_drop_the_stoplist():
    from rota.roles.api import _content_words

    assert _content_words("Give version_option a show_python flag") == {
        "version", "show", "python"}
    assert _content_words("also take that instead, please") == set()
    # The confirm request and the version_option request share only "flag",
    # a feature noun on the stoplist (the review of a9de65d5, finding 2).
    assert not _content_words(P2) & _content_words(P3)


# 2.G.6: the deliver door in verdict mode.

@pytest.mark.parametrize("desk", ["vision_keeper", "terminologist", "architect"])
def test_s273s_delivery_of_the_contested_statement_is_refused(db, desk):
    _night138(db, upto="m139")
    sb = _sandbox(db, "verdict", "m139", None)
    with pytest.raises(ValueError) as err:
        sb.call(f"msg.deliver_{desk}", refs=["s1"])
    assert str(err.value) == (
        f"the principal contested s1 in {CONTEST}, so s1 is not ratified and not "
        "delivered. Ratify only what they accepted. When they accepted nothing, "
        "end the session with no call")
    assert not sb.ctx.outbound


def test_an_accepted_statement_is_delivered(db):
    _night138(db, upto="m139")
    db.execute("INSERT INTO rulings (id, ask_id, per_item, words, status) VALUES "
               "('r_later', 'm135', '{\"s1\": \"approve\"}', 'ok', 'landed')")
    backfill_ruled_refs(db)
    db.commit()
    sb = _sandbox(db, "verdict", "m139", None)
    sb.call("msg.deliver_vision_keeper", refs=["s1"])
    assert len(sb.ctx.outbound) == 1


def test_the_verdict_brief_says_nothing_segments_the_reply():
    from rota.roles import prompts

    text = prompts.compose("liaison", "verdict")
    assert ("The principal's reply is already recorded as an entry. Nothing in this\n"
            "mode segments it.") in text
    assert "converse\nwake" not in text
