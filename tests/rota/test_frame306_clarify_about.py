"""
Frame 306, repair 1: one `about` set for the prompt and the clarify door.

The rows copy night 158's m144, m145 and m146, and night 144's m311, m312
and m313, read from `.rota/clickI_night158.db` and `.rota/clickI_night144.db`
with `mode=ro` on 2026-10-23. The provenance is `plans/frame306-provenance.md`,
sections 1 and 5.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import backfill_ruled_refs, init_db
from rota.core.runner import _mode_key, answer_about, resolve_inbound, run_session
from rota.core.scheduler import Wake, open_tips, park_criterion_relay
from rota.llm.llm import Pins, ScriptedBackend
from rota.testkit.fixtures import seed_provenance

PINS = Pins(model="stub", temperature=0.0)

ITEM = "version_option_show_python"
CR_2 = "cr_2_version_option_shows_python_format"
TST_02 = "tst_version_option_shows_python_02"
CR_2_TEXT = ('The output of show_python must contain the word "Python", followed by '
             "a space, then the version string in major.minor.micro format.")
# Night 158's m146, the principal's words on the clarify m145 (`entries`
# e_m146).
M146_WORDS = ('Add the word "Python", then a space, then the running interpreter\'s '
              "version as major, minor and micro joined by dots, at the end of the "
              'normal version message. Example: "Python 3.12.1". Do not put '
              "parentheses around it.")

# Night 144's m312: a clarify whose refs equal its asker's, the Architect's
# report m311, and whose reply m313 s462 ruled all approve (`rulings`
# r_1096cf2263). The words fault the test, and nothing moved.
CR_1 = "cr_1_confirm_default_on_eof"
TST_EOF = "tst_confirm_default_on_eof"
D_EOF = "d_b9954cfc9b"
M313_WORDS = ("It should return the default the caller passed to confirm, and that "
              "default is False when the caller gives none. The test is wrong to "
              "expect True. Either have it expect False or have it pass a default of "
              "True and then expect True.")


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _message(db, mid: str, sender: str, to: str, verb: str, refs, cause=None,
             status: str = "answered") -> None:
    seq = db.execute("SELECT COALESCE(MAX(seq), 0) + 1 n FROM messages").fetchone()["n"]
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, verb, "
               "body_refs, status, seq) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
               (mid, cause, cause or mid, sender, to, verb, json.dumps(refs), status, seq))


def _entry(db, mid: str, words: str) -> None:
    n = db.execute("SELECT COALESCE(MAX(ts_order), 0) + 1 n FROM entries").fetchone()["n"]
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "(?, 'principal', ?, ?)", (f"e_{mid}", words, n))


def _request(db, item: str, ticket: str, criterion: str, text: str, test: str,
             batch: str) -> None:
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version, "
               "priority, is_description) VALUES (?, 'the request', 'in_scope', "
               "'approved', 1, 1, 1, 0)", (item,))
    seed_provenance(db, "items", item, "decided")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES (?, ?, 'the ticket')",
               (ticket, item))
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?, ?, ?)",
               (criterion, ticket, text))
    db.execute("INSERT INTO batches (id, item_id, status, head_commit) VALUES "
               "(?, ?, 'running', 'aa28d1d')", (batch, item))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES (?, ?)",
               (batch, ticket))
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body, version) "
               "VALUES (?, ?, ?, 'tests/test_x.py', 'def test_x():\\n    pass\\n', 1)",
               (test, batch, criterion))


@pytest.fixture
def n158(db):
    """Night 158 at s286: the Critic's challenge m144 names cr_2 and tst_02,
    the Liaison's clarify m145 names tst_02 alone, and m146 answers it."""
    _request(db, ITEM, "tk_1_version_option_shows_python", CR_2, CR_2_TEXT, TST_02,
             "bg_3")
    _message(db, "m144", "critic", "tester", "challenge", [CR_2, TST_02])
    _message(db, "m145", "liaison", "principal", "clarify", [TST_02], cause="m144")
    _message(db, "m146", "principal", "liaison", "converse", [TST_02], cause="m145",
             status="open")
    _entry(db, "m146", M146_WORDS)
    db.commit()
    return db


@pytest.fixture
def n144(db):
    """Night 144 at s462: the Architect's report m311, the clarify m312 with
    the same three refs, and the reply m313."""
    _request(db, "confirm_default_on_eof", "tk_1_confirm_default_on_eof", CR_1,
             "confirm() returns the default on EOF.", TST_EOF, "bg_4")
    db.execute("INSERT INTO decisions (id, author, text, refs) VALUES "
               "(?, 'architect', 'the default is False', '[]')", (D_EOF,))
    refs = [CR_1, TST_EOF, D_EOF]
    _message(db, "m311", "architect", "liaison", "report", refs)
    _message(db, "m312", "liaison", "principal", "clarify", refs, cause="m311")
    _message(db, "m313", "principal", "liaison", "converse", refs, cause="m312",
             status="open")
    _entry(db, "m313", M313_WORDS)
    db.commit()
    return db


def _sandbox(db, trigger: str):
    from rota.core.sandbox import build
    from rota.roles import prompts

    sb = build("liaison", db, mode="answering",
               allow=prompts.mode_tools("liaison", "answering"))
    sb.ctx.trigger = trigger
    return sb


def _prompt_about(db, reply: str) -> list[str]:
    inbound = resolve_inbound(db, Wake("liaison", "message", refs=(), detail="converse",
                                       message_id=reply))
    return inbound["answering"]["about"]


def test_the_prompt_and_the_door_read_one_about_set(n158):
    """s286 turn 1 read `about: [cr_2, tst_02]`, from the asker m144."""
    assert answer_about(n158, "m145") == [CR_2, TST_02]
    assert _prompt_about(n158, "m146") == [CR_2, TST_02]


def test_a_criterion_the_asker_named_is_a_key_of_the_clarify_door(n158):
    """s286 turn 2: the door refused cr_2 with "is not a row of this
    question", because it keyed on m145's `[tst_02]` alone. The ruling now
    lands. The check of an approve against the words is held (frame 306,
    repair 1, change 3)."""
    sb = _sandbox(n158, "m146")
    out = sb.call("rulings.rule", rulings={CR_2: "approve", TST_02: "approve"},
                  words=M146_WORDS)
    assert out["per_item"] == {CR_2: "approve", TST_02: "approve"}


def test_a_revise_of_the_criterion_lands_and_wakes_the_repair_mode(n158):
    """The revise of cr_2 on m146 lands, its relay keys `criterion_repair`,
    and tst_02, left out, is parked as today."""
    from rota.roles import prompts

    (wake,) = [w for w in open_tips(n158) if w.message_id == "m146"]
    calls = [f"TOOL: rulings.rule(rulings={json.dumps({CR_2: 'revise'})}, "
             f"words={M146_WORDS!r})",
             f'TOOL: msg.relay_terminologist(refs=["{CR_2}"])', "done"]
    out = run_session(n158, wake, backend=ScriptedBackend(calls), pins=PINS,
                      instructions="answering")
    assert out.committed, out.errors
    (ruling,) = n158.execute("SELECT per_item, status FROM rulings "
                             "WHERE reply_id = 'm146'").fetchall()
    assert (json.loads(ruling["per_item"]), ruling["status"]) == (
        {CR_2: "revise"}, "landed")
    assert n158.execute("SELECT 1 FROM ledger WHERE about_ref = ?",
                        (TST_02,)).fetchone()
    # The split stages this relay twice on HEAD d2b4f79a too, once under
    # each terminologist key. Each copy keys the repair mode.
    relays = n158.execute("SELECT id, to_role, body_refs FROM messages WHERE "
                          "cause_id = 'm146' AND verb = 'relay'").fetchall()
    assert relays
    for relay in relays:
        assert (relay["to_role"], json.loads(relay["body_refs"])) == (
            "terminologist", [CR_2])
        assert park_criterion_relay(n158, relay["id"])
        mode = _mode_key(Wake("terminologist", "message", refs=(), detail="relay",
                              message_id=relay["id"]), n158)
        assert mode == "criterion_repair"
        assert "criteria.respecify" in set(prompts.mode_tools("terminologist", mode))


def test_a_revised_criterion_beside_an_approved_test_wakes_the_terminologist_once(n158):
    """Pass 1b. The relay takes m146's `[tst_02]` as well, and the split sent
    cr_2 under both Terminologist keys. Two relays meant two repair wakes."""
    (wake,) = [w for w in open_tips(n158) if w.message_id == "m146"]
    calls = [f"TOOL: rulings.rule(rulings="
             f"{json.dumps({CR_2: 'revise', TST_02: 'approve'})}, "
             f"words={M146_WORDS!r})",
             f'TOOL: msg.relay_terminologist(refs=["{CR_2}"])', "done"]
    out = run_session(n158, wake, backend=ScriptedBackend(calls), pins=PINS,
                      instructions="answering")
    assert out.committed, out.errors
    (relay,) = n158.execute("SELECT id, to_role, body_refs FROM messages WHERE "
                            "cause_id = 'm146' AND verb = 'relay'").fetchall()
    assert (relay["to_role"], json.loads(relay["body_refs"])) == ("terminologist", [CR_2])
    assert _mode_key(Wake("terminologist", "message", refs=(), detail="relay",
                          message_id=relay["id"]), n158) == "criterion_repair"


def test_an_approved_criterion_on_a_clarify_keeps_relay_mode(n158):
    """A clarify ruling that approves the criterion is no ruling on its words,
    so a relay of it keeps `relay`."""
    n158.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, status) "
                 "VALUES ('r_x', 'm145', 'm146', ?, 'ok', 'landed')",
                 (json.dumps({CR_2: "approve", TST_02: "approve"}),))
    backfill_ruled_refs(n158)
    _message(n158, "m147", "liaison", "terminologist", "relay", [CR_2], cause="m146",
             status="open")
    assert not park_criterion_relay(n158, "m147")


def test_a_ruled_test_row_on_a_clarify_routes_as_today(n158):
    """Frame 213's route B on this shape: a revise of tst_02 travels as cr_2
    and keys `criterion_repair` through `ruled_test_criteria`."""
    (wake,) = [w for w in open_tips(n158) if w.message_id == "m146"]
    calls = [f"TOOL: rulings.rule(rulings={json.dumps({TST_02: 'revise'})}, "
             f"words={M146_WORDS!r})",
             f'TOOL: msg.relay_vision_keeper(refs=["{TST_02}"])', "done"]
    out = run_session(n158, wake, backend=ScriptedBackend(calls), pins=PINS,
                      instructions="answering")
    assert out.committed, out.errors
    (relay,) = n158.execute("SELECT id, body_refs FROM messages WHERE "
                            "cause_id = 'm146' AND verb = 'relay'").fetchall()
    assert json.loads(relay["body_refs"]) == [CR_2]
    assert _mode_key(Wake("terminologist", "message", refs=(), detail="relay",
                          message_id=relay["id"]), n158) == "criterion_repair"


def test_m313_all_approve_lands_and_a_revise_of_the_test_lands(n144):
    """Night 144's m312 and m313, a probe of changes 1 and 2. The asker's
    refs equal the clarify's, so the set does not move. s462's all-approve
    ruling lands today, and "The test is wrong to expect True" reaches
    nobody. The check that would refuse it is held (frame 306, repair 1,
    change 3). A revise of the test row lands."""
    assert answer_about(n144, "m312") == [CR_1, TST_EOF, D_EOF]
    sb = _sandbox(n144, "m313")
    out = sb.call("rulings.rule", rulings={CR_1: "approve", TST_EOF: "approve",
                                           D_EOF: "approve"}, words=M313_WORDS)
    assert set(out["per_item"].values()) == {"approve"}
    sb = _sandbox(n144, "m313")
    out = sb.call("rulings.rule", rulings={CR_1: "approve", TST_EOF: "revise",
                                           D_EOF: "approve"}, words=M313_WORDS)
    assert out["per_item"][TST_EOF] == "revise"


def test_a_clarify_with_no_asker_refs_keys_on_its_own_refs(db):
    """A clarify whose asker named no row keys on its own refs, as before."""
    _request(db, ITEM, "tk_1_version_option_shows_python", CR_2, CR_2_TEXT, TST_02,
             "bg_3")
    _message(db, "m10", "tester", "liaison", "report", [])
    _message(db, "m11", "liaison", "principal", "clarify", [TST_02], cause="m10")
    _message(db, "m12", "principal", "liaison", "converse", [TST_02], cause="m11",
             status="open")
    _entry(db, "m12", "Fix it.")
    db.commit()
    assert answer_about(db, "m11") == [TST_02]
    sb = _sandbox(db, "m12")
    with pytest.raises(ValueError, match=f"is not a row of this question.*: {TST_02}$"):
        sb.call("rulings.rule", rulings={CR_2: "revise"}, words="Fix it.")


def test_a_clarify_with_no_asker_keys_on_its_own_refs(db):
    """Liaison's own question has no asker. `answer_about` says so, and the
    door keys on the clarify's refs, as before."""
    _request(db, ITEM, "tk_1_version_option_shows_python", CR_2, CR_2_TEXT, TST_02,
             "bg_3")
    _message(db, "m11", "liaison", "principal", "clarify", [TST_02])
    _message(db, "m12", "principal", "liaison", "converse", [TST_02], cause="m11",
             status="open")
    _entry(db, "m12", "Fix it. That is fine.")
    db.commit()
    assert answer_about(db, "m11") is None
    assert _prompt_about(db, "m12") == [TST_02]
    sb = _sandbox(db, "m12")
    with pytest.raises(ValueError, match="is not a row of this question"):
        sb.call("rulings.rule", rulings={CR_2: "revise"}, words="Fix it.")
    out = sb.call("rulings.rule", rulings={TST_02: "approve"}, words="That is fine.")
    assert out["per_item"] == {TST_02: "approve"}


# Pass 1c, review 1 findings 2 to 4.
def test_a_message_id_in_the_askers_refs_is_not_a_key(n158):
    """Finding 2: night 144's m399 door admitted `m385`, a message id, from the
    asker's refs, and landed it in `per_item`."""
    _message(n158, "m20", "critic", "tester", "challenge", [CR_2, "m144"])
    _message(n158, "m21", "liaison", "principal", "clarify", [TST_02], cause="m20")
    _message(n158, "m22", "principal", "liaison", "converse", [TST_02], cause="m21",
             status="open")
    _entry(n158, "m22", "Fix it.")
    n158.commit()
    assert answer_about(n158, "m21") == [CR_2, TST_02]
    sb = _sandbox(n158, "m22")
    with pytest.raises(ValueError, match="is not a row of this question"):
        sb.call("rulings.rule", rulings={"m144": "revise"}, words="Fix it.")


def test_a_prior_answer_is_found_on_the_askers_criterion(n158):
    """Finding 3: a later report that names only cr_2 did not see m146,
    because the match read m145's own `[tst_02]`."""
    _message(n158, "m150", "terminologist", "liaison", "report", [CR_2],
             status="open")
    n158.commit()
    inbound = resolve_inbound(n158, Wake("liaison", "message", refs=(), detail="report",
                                         message_id="m150"))
    (prior,) = inbound["prior_answers"]
    assert prior["principal_said"] == M146_WORDS
    assert CR_2 in prior["about"]


def test_a_relay_after_a_ruling_on_the_askers_criterion_carries_it(n158):
    """Finding 4: the relay added the reply's refs and not a criterion ruled
    from the asker's refs. Here no test row of the reply covers cr_2."""
    _message(n158, "m20", "critic", "tester", "challenge", [CR_2, ITEM])
    _message(n158, "m21", "liaison", "principal", "clarify", [ITEM], cause="m20")
    _message(n158, "m22", "principal", "liaison", "converse", [ITEM], cause="m21",
             status="open")
    _entry(n158, "m22", M146_WORDS)
    n158.commit()
    (wake,) = [w for w in open_tips(n158) if w.message_id == "m22"]
    calls = [f"TOOL: rulings.rule(rulings="
             f"{json.dumps({CR_2: 'revise', ITEM: 'approve'})}, "
             f"words={M146_WORDS!r})",
             f'TOOL: msg.relay_vision_keeper(refs=["{ITEM}"])', "done"]
    out = run_session(n158, wake, backend=ScriptedBackend(calls), pins=PINS,
                      instructions="answering")
    assert out.committed, out.errors
    relays = {r["to_role"]: json.loads(r["body_refs"]) for r in n158.execute(
        "SELECT to_role, body_refs FROM messages WHERE cause_id = 'm22' "
        "AND verb = 'relay'")}
    assert relays.get("terminologist") == [CR_2]
