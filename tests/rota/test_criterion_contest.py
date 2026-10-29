"""Frames 226 and 227: the criterion repair keeps the principal's words.

Night 144, walk 3, the rota workflow (`plans/night144-read.md`, sections
1.3, 1.4 and 8). The principal contested `ver_opt_show_py` with ruling
r_c4bf70291d. s537 respecified it in his words. s546 then woke on the
Tester's question m379 with no word of the ruling, and put back the
`--show-python` flag he had contested. Later relays sent the contested
sentence back, and the door answered `unchanged` with a note that did
not name his contest. The texts below are the night's.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import backfill_ruled_refs, init_db
from rota.testkit.fixtures import seed_acts
from rota.core.predicates import Wake
from rota.core.runner import build_prompt
from rota.core.sandbox import build
from rota.roles import prompts

from tests.rota.test_park_page import (  # noqa: F401
    ITEM_132, _landing, _liaison_presents, _reply, n132)

CID = "ver_opt_show_py"
SURFACE = "src/click/decorators.py::version_option"
# Version 14, the text on page m374 when the principal contested line 2.
V14 = ("The `version_option` callable appends the running Python version "
       "string (major.minor.micro) to the output message when invoked with "
       "the `--show-python` flag.")
# Version 15, s537's respecify on the relay m378.
V15 = ("The `version_option` callable appends the running Python version "
       "string (major.minor.micro) to the output message when invoked with "
       "the `show_python` parameter set to True.")
# Version 16, s546's respecify on `tick:criterion_repair`, and s583's call.
V16 = ("The command decorated with `version_option` must be invoked via "
       "`CliRunner` with the flag that enables Python version display (e.g., "
       "`--show-python`). The resulting output must contain the running "
       "Python version string formatted as major.minor.micro.")
# r_c4bf70291d, the reply to page m374.
WORDS_374 = ("Line 2 is wrong because it treats show_python as a new "
             "command-line option that users type. I asked for a parameter "
             "that the developer passes to version_option. When the developer "
             "sets it, the normal version output adds the Python version as "
             "major.minor.micro.")
# r_a9d56cfc45, the reply to page m403, which the relay m407 carried to s583.
WORDS_403 = ("Line 2 is still wrong because show_python is a setting the "
             "developer passes to the decorator, so the test should call the "
             "normal version flag and expect the Python version at the end of "
             "the output. Lines 6 and 9 make the same mistake about a separate "
             "flag, and line 5 is about the first change and does not belong "
             "on this page.")


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('version_option_show_python', 'Give "
                 "version_option a show_python parameter', 'in_scope', "
                 "'approved', 1, 1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk_1', 'version_option_show_python', 'show_python on "
                 "version_option')")
    conn.execute("INSERT INTO code_index (grain, grain_kind, sym_kind) VALUES "
                 "(?, 'symbol', 'function')", (SURFACE,))
    conn.commit()
    return conn


def _criterion(conn, text: str) -> None:
    conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                 "VALUES (?, 'tk_1', ?, ?)", (CID, text, json.dumps([SURFACE])))
    conn.commit()


def _ruling(conn, rid: str, ask: str, verdict: str, words: str,
            contested: str | None) -> None:
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                 "verb, body_refs, seq) VALUES (?, ?, 'liaison', 'principal', "
                 "'present', ?, 1)", (ask, ask, json.dumps([CID])))
    texts = {CID: contested} if contested is not None else {}
    conn.execute("INSERT INTO rulings (id, ask_id, per_item, words, status, "
                 "texts) VALUES (?, ?, ?, ?, 'landed', ?)",
                 (rid, ask, json.dumps({CID: verdict}), words, json.dumps(texts)))
    backfill_ruled_refs(conn)
    conn.commit()


def _respecify(conn, text: str) -> dict:
    sb = build("terminologist", conn, mode="criterion_repair",
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    return sb.call("criteria.respecify", id=CID, text=text,
                   surface_refs=[SURFACE])


# --- frame 226, the door ----------------------------------------------------

def test_a_repair_that_puts_back_a_contested_flag_is_refused(db):
    """s546's call: version 15 is current, and version 14 is the text the
    principal contested. The flag `--show-python` comes back."""
    _criterion(db, V15)
    _ruling(db, "r_c4bf70291d", "m374", "contest", WORDS_374, V14)
    with pytest.raises(ValueError) as refused:
        _respecify(db, V16)
    said = str(refused.value)
    assert "--show-python" in said
    assert WORDS_374 in said


def test_a_repair_that_changes_other_words_is_admitted(db):
    """The same contest, and a rewrite that keeps the flag out."""
    _criterion(db, V15)
    _ruling(db, "r_c4bf70291d", "m374", "contest", WORDS_374, V14)
    out = _respecify(db, "The command decorated with `version_option` and "
                         "`show_python=True` prints the running Python version "
                         "as major.minor.micro at the end of the normal "
                         "version message.")
    assert out["respecified"]


def test_a_name_the_principal_asked_for_is_admitted(db):
    """The review of 33cd99b2, probe p3 case C: the current text dropped
    `version_option`, and WORDS_374 asks for a parameter of
    `version_option`. V15 names it again and lands. s546's `--show-python`
    is not in his words, so it stays refused."""
    _criterion(db, "The decorator appends the running Python version "
                   "(major.minor.micro) when the `show_python` parameter is "
                   "True.")
    _ruling(db, "r_c4bf70291d", "m374", "contest", WORDS_374, V14)
    # Fact F3: the Liaison's row records the name as the act's target.
    seed_acts(db, "r_c4bf70291d", {CID: {
        "act": "rewrite", "target_kind": "identifier",
        "target": "version_option", "words": WORDS_374}})
    assert _respecify(db, V15)["respecified"]
    with pytest.raises(ValueError, match="--show-python"):
        _respecify(db, V16)


def test_his_words_alone_never_let_a_contested_name_back(db):
    """Fact F3: the door reads the grant on the row, not a phrase of his
    words. WORDS_374 names `version_option`, and no row grants an act on
    it, so V15 is refused. The old token match admitted it."""
    _criterion(db, "The decorator appends the running Python version "
                   "(major.minor.micro) when the `show_python` parameter is "
                   "True.")
    _ruling(db, "r_c4bf70291d", "m374", "contest", WORDS_374, V14)
    with pytest.raises(ValueError, match="version_option"):
        _respecify(db, V15)


def test_the_name_must_sit_in_the_contest_rows_own_words(db):
    """Pass 4, P9: the door reads the words of the contest row, the span
    that rules this criterion, and not the whole reply. The reply names
    `version_option`, and the row's span does not, so V15 is refused."""
    _criterion(db, "The decorator appends the running Python version "
                   "(major.minor.micro) when the `show_python` parameter is "
                   "True.")
    _ruling(db, "r_c4bf70291d", "m374", "contest", WORDS_374, V14)
    seed_acts(db, "r_c4bf70291d", {CID: {
        "act": "rewrite", "words": "Line 2 is wrong because it treats "
                                   "show_python as a new command-line option "
                                   "that users type."}})
    with pytest.raises(ValueError, match="version_option"):
        _respecify(db, V15)


def test_a_name_his_landed_words_ask_for_is_admitted(db):
    """Fact F3, the F2 review, finding 2: his words ask for a parameter of
    `version_option`, and the ruling lands with no target from the seat.
    The parser's reading writes the grant row, so the Architect's V15
    lands. s546's `--show-python` is not in his words and stays refused."""
    from rota.roles.principal import Answer, Ask, land

    _criterion(db, V14)
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m374', 'm374', 'liaison', "
               "'principal', 'present', ?, 1, 'open')", (json.dumps([CID]),))
    db.commit()
    land(db, Ask(message_id="m374", verb="present", refs=[CID]),
         Answer(verb="verdict", text=WORDS_374, per_item={CID: "contest"}))
    # An earlier repair dropped the name from the criterion.
    db.execute("UPDATE criteria SET text = ? WHERE id = ?",
               ("The decorator appends the running Python version "
                "(major.minor.micro) when the `show_python` parameter is "
                "True.", CID))
    db.commit()
    grants = {tuple(r) for r in db.execute(
        "SELECT act, target FROM ruled_refs WHERE ref = ? AND "
        "target_kind = 'identifier'", (CID,))}
    assert ("rewrite", "version_option") in grants
    assert _respecify(db, V15)["respecified"]
    with pytest.raises(ValueError, match="No row of ruling"):
        _respecify(db, V16)


def test_a_contest_that_land_writes_keeps_the_text_it_contested(db):
    """The review of 33cd99b2, finding 3: a verdict straight from the seat
    lands through `land`, whose raw INSERT wrote no texts."""
    from rota.roles.principal import Answer, Ask, land

    _criterion(db, V14)
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m374', 'm374', 'liaison', "
               "'principal', 'present', ?, 1, 'open')", (json.dumps([CID]),))
    db.commit()
    msg = land(db, Ask(message_id="m374", verb="present", refs=[CID]),
               Answer(verb="verdict", text=WORDS_374, per_item={CID: "contest"}))
    assert msg is not None
    (row,) = db.execute("SELECT texts FROM rulings WHERE ask_id = 'm374'").fetchall()
    assert json.loads(row["texts"]) == {CID: V14}


def test_any_repair_is_admitted_when_no_ruling_contested_the_criterion(db):
    """No ruling names the criterion, so s546's text lands as today."""
    _criterion(db, V15)
    assert _respecify(db, V16)["respecified"]


# --- frame 227, the silent unchanged note --------------------------------------

def test_the_contested_sentence_sent_back_is_refused(db):
    """s583's call on the relay m407: version 16 is current, the principal
    contested version 16 on page m403, and the call sends version 16."""
    _criterion(db, V16)
    _ruling(db, "r_a9d56cfc45", "m403", "contest", WORDS_403, V16)
    with pytest.raises(ValueError) as refused:
        _respecify(db, V16)
    said = str(refused.value)
    assert "the principal contested these words" in said
    assert WORDS_403 in said
    assert "Write what he asked for" in said


def test_the_same_words_with_no_contest_keep_the_unchanged_note(db):
    _criterion(db, V16)
    out = _respecify(db, V16)
    assert out["unchanged"]
    assert "those are the criterion's own words" in out["note"]


# --- frame 226, pass 1c: the surface before the text -------------------------

CUSTOM = "src/click/decorators.py::custom_version_option"
# cr_1_show_python_flag on night 145, the text every repair sent back.
CR1 = ("The `version_option` decorator with `show_python=True` appends the "
       "running Python version as major.minor.micro to the version output.")
# r_b33e2979e0, the reply to page m170.
WORDS_170 = ("Line 3's check is wrong because the flag belongs to the "
             "decorator, not the command line.")


def _on_custom_surface(conn, text: str) -> None:
    conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                 "VALUES (?, 'tk_1', ?, ?)", (CID, text, json.dumps([CUSTOM])))
    conn.commit()


def _respecify_staged(conn, text: str):
    """The door's result and the criterion write it staged."""
    from rota.core.runner import _as_write

    sb = build("terminologist", conn, mode="criterion_repair",
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    out = sb.call("criteria.respecify", id=CID, text=text,
                  surface_refs=[SURFACE])
    staged = [_as_write(w) for w in sb.ctx.writes]
    return out, [w for w in staged if w.table == "criteria"]


def test_the_same_words_on_a_new_surface_land_as_a_surface_change(db):
    """s292's call: the criterion's own text, and the surface moved from
    `custom_version_option` to `version_option`."""
    _on_custom_surface(db, CR1)
    out, (crit,) = _respecify_staged(db, CR1)
    assert out.get("surface_changed") is True
    assert out["from"] == [CUSTOM] and out["to"] == [SURFACE]
    assert json.loads(crit.values["surface_refs"]) == [SURFACE]
    assert crit.values["text"] == CR1
    assert crit.amends, "a surface change moves the version"


def test_a_surface_change_lands_under_a_standing_contest(db):
    """s272's call: the principal contested this text, and the relay sent
    the same text with the surface repaired."""
    _on_custom_surface(db, CR1)
    _ruling(db, "r_b33e2979e0", "m170", "contest", WORDS_170, CR1)
    out, (crit,) = _respecify_staged(db, CR1)
    assert out.get("surface_changed") is True
    assert json.loads(crit.values["surface_refs"]) == [SURFACE]


def test_a_contest_of_the_check_names_the_answer_route(db):
    """s321's call: the same text and the same surface, and his words fault
    line 3's check and not the criterion's words."""
    _criterion(db, CR1)
    _ruling(db, "r_b33e2979e0", "m170", "contest", WORDS_170, CR1)
    # The Liaison reads a fault of the check alone as a keep of the words
    # (the seam design, pass 4).
    seed_acts(db, "r_b33e2979e0", {CID: {"act": "keep", "target_kind": "check"}})
    # The door reads his words per line of the page he saw (frame 308, pass
    # 3). His "Line 3" is this criterion, so the record puts it on line 3.
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
               "to_role, verb, body_refs, body_text, seq) VALUES ('m171', "
               "'m170', 'm170', 'principal', 'liaison', 'converse', ?, ?, 2)",
               (json.dumps([CID]), WORDS_170))
    db.execute("UPDATE rulings SET reply_id = 'm171' WHERE id = 'r_b33e2979e0'")
    db.execute("INSERT INTO config (key, value) VALUES ('order:m171', ?)",
               (json.dumps(["line_1", "line_2", CID]),))
    db.commit()
    with pytest.raises(ValueError) as refused:
        _respecify(db, CR1)
    said = str(refused.value)
    assert "faulted the check" in said
    assert "msg.answer_tester" in said
    assert WORDS_170 in said
    assert "Write what he asked for" not in said


def test_a_contested_flag_inside_a_longer_name_of_his_is_refused(db):
    """The review of frame 226, finding 1: `--show` is a substring of the
    `--show-python` his words name, and it is not a name he asked for."""
    contested = ("The command decorated with `version_option` prints the Python "
                 "version when invoked with `--show`.")
    _criterion(db, V15)
    _ruling(db, "r_sub", "m500", "contest",
            "I asked for `--show-python` on the decorator.", contested)
    with pytest.raises(ValueError, match="--show"):
        _respecify(db, "The command decorated with `version_option` and "
                       "`show_python=True` prints the Python version when "
                       "invoked with `--show`.")


# r_c8757431e3 on night 145: it faults line 2's words and asks that the tests
# "check its printed output".
WORDS_C875 = ("Please keep going with this change. Line 2 should say the "
              "command has a fixed program version like 1.0, not a fixed "
              "Python version, and lines 3 and 4 still call the version option "
              "directly when they should run that command and check its printed "
              "output. Line 6 is still wrong because the work should touch only "
              "the version option code and its tests in test_basic, not the "
              "tests for option flags and default maps.")


def test_an_answer_that_faults_the_words_keeps_write_what_he_asked_for(db):
    """The review of 84a06216, finding 1: the verb "check" made this answer
    read as a fault of the check, and the door said the criterion stands."""
    _criterion(db, CR1)
    _ruling(db, "r_c8757431e3", "m255", "contest", WORDS_C875, CR1)
    with pytest.raises(ValueError) as refused:
        _respecify(db, CR1)
    said = str(refused.value)
    assert "Write what he asked for" in said
    assert "The criterion stands" not in said


def test_an_empty_surface_on_a_greenfield_index_clears_nothing(db):
    """The review of 84a06216, finding 3: with no symbols in the index the
    door vets `[]`, and a same-text call cleared the surface on file."""
    db.execute("DELETE FROM code_index")
    db.commit()
    _on_custom_surface(db, CR1)
    sb = build("terminologist", db, mode="criterion_repair",
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    out = sb.call("criteria.respecify", id=CID, text=CR1, surface_refs=[])
    assert out.get("unchanged"), out
    assert not any(w[0] == "criteria" for w in sb.ctx.writes)


# --- frame 226, the wake ----------------------------------------------------

def test_the_repair_wake_carries_the_principals_last_word(db):
    """s546's wake: the Tester's question m379 names the criterion, and the
    prompt now quotes the ruling r_c4bf70291d word for word."""
    _criterion(db, V15)
    _ruling(db, "r_c4bf70291d", "m374", "contest", WORDS_374, V14)
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status, unresolved_note) VALUES ('m379', "
               "'m379', 'tester', 'terminologist', 'question', ?, 2, "
               "'unresolved', 'the answer did not change the criterion; "
               "encoding it still parrots')", (json.dumps([CID]),))
    db.commit()
    sb = build("terminologist", db, mode="criterion_repair",
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    wake = Wake("terminologist", "tick:criterion_repair", refs=("m379",),
                detail="the answer did not change the criterion; encoding it "
                       "still parrots")
    _system, user = build_prompt("terminologist", sb, wake, {},
                                 "MODE: criterion_repair")
    assert (f"The principal's last word on this criterion, {CID} "
            f"(ruling r_c4bf70291d, contest):\n{WORDS_374}") in user
    assert "Do not send the sentence he contested." in user


@pytest.mark.parametrize("approve", [False, True], ids=["no ruling", "approve"])
def test_a_repair_wake_with_no_contest_keeps_todays_prompt(db, approve):
    """An approve's words are about other lines of its page. Night 144's
    r_373fbae7da approved the criterion and asked about line 3 (the review
    of 33cd99b2, finding 4)."""
    _criterion(db, V15)
    if approve:
        _ruling(db, "r_373fbae7da", "m439", "approve",
                "Lines 2 and 4 are right now. I don't follow line 3. What is "
                "\"custom_version_option\"?", None)
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m379', 'm379', 'tester', "
               "'terminologist', 'question', ?, 2, 'unresolved')",
               (json.dumps([CID]),))
    db.commit()
    sb = build("terminologist", db, mode="criterion_repair",
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    wake = Wake("terminologist", "tick:criterion_repair", refs=("m379",))
    _system, user = build_prompt("terminologist", sb, wake, {},
                                 "MODE: criterion_repair")
    assert "last word" not in user


# --- frame 226, the store -----------------------------------------------------

def test_a_contest_of_a_criterion_line_keeps_the_text_it_contested(n132):  # noqa: F811
    """The ruling keeps the text the principal read, because a criterion
    keeps no history. Night 132's page, line 4 is `cr_2`."""
    mid = _liaison_presents(n132, ITEM_132)
    reply = _reply(n132, mid, "line 4 is wrong: it must not hang")
    ruling = {str(n): "approve" for n in (1, 2, 4, 6, 8, 10, 12)}
    ruling["4"] = "contest"
    text = n132.execute("SELECT text FROM criteria WHERE id = "
                        "'cr_2_confirm_eof_behavior'").fetchone()["text"]
    out = _landing(n132, reply, f"TOOL: rulings.rule(rulings={json.dumps(ruling)}, "
                                "words='line 4 is wrong: it must not hang')")
    assert out.committed, out.errors
    (row,) = n132.execute("SELECT texts FROM rulings WHERE ask_id = ?",
                          (mid,)).fetchall()
    assert json.loads(row["texts"]) == {"cr_2_confirm_eof_behavior": text}


# --- frame 243, a seat's supersede of the principal's decision -----------------

# Night 148's two decisions rows, copied verbatim from
# `.rota/clickI_night148.db` on 2026-10-15, so the tests run in a checkout
# without the run's database (frame 243, review 1, finding 4).
DECISIONS148 = {
    "d_565d2845d4": {
        "id": "d_565d2845d4", "author": "principal",
        "text": ("default taken at signoff: The version_option includes a "
                 "show_python flag that appends the running Python version to "
                 "the message."),
        "supersedes": None, "refs": '["version_option_show_python"]'},
    "d_74_challenge_ver_opt_show_py": {
        "id": "d_74_challenge_ver_opt_show_py", "author": "vision_keeper",
        "text": ("The version_option's show_python flag must append the running "
                 'Python version to the message in the format "{command} '
                 '{python_version}" where python_version is derived from '
                 "sys.version_info.major.minor.micro."),
        "supersedes": "d_565d2845d4",
        "refs": '["ver_opt_show_py", "tk_1_version_option_show_python"]'},
}


def _night148_decisions() -> dict:
    """The principal's d_565d2845d4 and s189's d_74_challenge_ver_opt_show_py."""
    return {k: dict(v) for k, v in DECISIONS148.items()}


def _seed_decision(conn, row: dict) -> None:
    conn.execute("INSERT INTO decisions (id, author, text, refs) VALUES "
                 "(?, ?, ?, ?)", (row["id"], row["author"], row["text"],
                                  row["refs"]))
    conn.commit()


def test_night148_s189_supersedes_the_principals_decision_is_refused(db):
    """Frame 243, night 148: s189, turn 1, wrote its decision with
    supersedes on d_565d2845d4, the principal's signoff decision, and the
    call landed. The door refuses it and offers the call without
    supersedes."""
    rows = _night148_decisions()
    principal, s189 = rows["d_565d2845d4"], rows["d_74_challenge_ver_opt_show_py"]
    assert principal["author"] == "principal"
    _seed_decision(db, principal)
    vk = build("vision_keeper", db, mode="normal")
    refs = json.loads(s189["refs"])
    with pytest.raises(ValueError) as exc:
        vk.call("decisions.author", id=s189["id"], text=s189["text"],
                refs=refs, supersedes=s189["supersedes"])
    assert str(exc.value) == (
        "`d_565d2845d4` is the principal's decision. A seat's decision does "
        "not replace his. Send the same call again without supersedes.")
    assert not [w for w in vk.ctx.writes if w[0] == "decisions"]
    [offer] = [o for o in vk.ctx.offers if o.op == "decisions.author"]
    assert offer.args == {"id": s189["id"], "text": s189["text"], "refs": refs}
    assert "supersedes" not in offer.args


def test_a_seats_supersedes_on_another_seats_decision_is_admitted(db):
    """Frame 243: the door reads the author. A Vision Keeper that supersedes
    an Architect's decision lands as before."""
    _seed_decision(db, {"id": "d_arch_1", "author": "architect",
                        "text": "the flag is a keyword argument", "refs": "[]"})
    vk = build("vision_keeper", db, mode="normal")
    out = vk.call("decisions.author", id="d_vk_1",
                  text="the flag is a keyword argument of version_option",
                  refs=[CID], supersedes="d_arch_1")
    assert out["id"] == "d_vk_1"
    [(_t, _id, row, *_)] = [w for w in vk.ctx.writes if w[0] == "decisions"]
    assert row["supersedes"] == "d_arch_1"


# These tests pin the doors of the word form of a page call. Pass R2
# retires the doors and these pins (frame 345, the R1 brief, step 5).
pytestmark = pytest.mark.usefixtures("old_page_form")
