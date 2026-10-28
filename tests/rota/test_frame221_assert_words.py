"""
Frame 221: the assert door keeps the principal's words on a decided item.

Night 146: s354, woken by a challenge, rewrote `confirm_default_on_eof`
with its own text, and the scheduler abandoned bg_5. s399, woken by
`tick:contested`, wrote "without requiring a flag" where the principal
said nothing of the kind. Night 145's s328 answered a challenge with a new
id, and the page showed the new item as the principal's own ask
(plans/night146-read.md section 4, plans/night145-read.md candidate G).
"""
from __future__ import annotations

import json
import re

import pytest

from rota.core.db import backfill_ruled_refs, init_db
from rota.testkit.fixtures import seed_acts
from rota.core.predicates import Wake
from rota.core.sandbox import build
from rota.roles import prompts
from rota.roles.api import _wake_mode_tools
from rota.testkit.fixtures import seed_provenance

CONFIRM = ("Let confirm() take a default_on_eof flag: when stdin is closed, "
           "confirm() returns the default instead of raising an error.")
VOPT = ("The `version_option` will include a `show_python` flag that "
        "appends the running Python version to the message.")
VOPT_SAID = ("Ok, that's what I asked for. Line 2 just repeats line 1, so it "
             "doesn't add anything. The Python version should come from the "
             "running interpreter's version info, shown as major.minor.micro.")


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    for iid, text, approval in (
            ("confirm_default_on_eof", CONFIRM, "approved"),
            ("version_option_show_python", VOPT, "contested"),
            ("tip_split", "Calculate tips based on bill amount and service "
                          "quality", "contested")):
        conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                     "version) VALUES (?, ?, 'in_scope', ?, 1, 1)",
                     (iid, text, approval))
        seed_provenance(conn, "items", iid, "decided")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('reads_flags', 'the program reads flags "
                 "from the command line', 'in_scope', 'approved', 1, 1)")
    seed_provenance(conn, "items", "reads_flags", "reasoned")
    # The Architect's challenge that woke s354 (m213).
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "body_refs, body_text, seq) VALUES ('m213', 't1', 'architect', "
                 "'vision_keeper', 'challenge', ?, 'the criteria do not match "
                 "the implementation', 1)",
                 (json.dumps(["confirm_default_on_eof"]),))
    conn.commit()
    return conn


def _contest(conn, item, said, mid, acts=None):
    """The shape the contested tick reads: a verdict and its entry. `acts`
    gives rows the act the Liaison's object form writes (pass 4)."""
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "body_refs, seq) VALUES (?, 'th', 'principal', 'liaison', "
                 "'verdict', ?, 5)", (mid, json.dumps([item])))
    conn.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
                 "(?, 'principal', ?, 1)", (f"e_{mid}", said))
    # The verdict lands as a ruling, as `principal.land` writes it, so the
    # contest reader finds the record (the seam design, 3.4).
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "body_refs, seq) VALUES (?, 'th', 'liaison', 'principal', "
                 "'present', ?, 4)", (f"ask_{mid}", json.dumps([item])))
    conn.execute("INSERT INTO rulings (id, ask_id, per_item, words, status, "
                 "verdict_id) VALUES (?, ?, ?, ?, 'landed', ?)",
                 (f"r_{mid}", f"ask_{mid}", json.dumps({item: "contest"}), said,
                  mid))
    backfill_ruled_refs(conn)
    if acts:
        seed_acts(conn, f"r_{mid}", acts)
    conn.commit()


def _challenged(conn):
    sb = build("vision_keeper", conn, mode="challenge",
               allow=prompts.mode_tools("vision_keeper", "challenge"),
               wake=Wake("vision_keeper", "message", message_id="m213",
                         detail="challenge"))
    sb.ctx.trigger = "m213"
    return sb


def _contested(conn, item):
    return build("vision_keeper", conn, mode="contested",
                 allow=prompts.mode_tools("vision_keeper", "contested"),
                 wake=Wake("vision_keeper", "tick:contested", refs=(item,)))


def _item_writes(sb):
    return [w for w in sb.ctx.writes if w[0] == "items"]


def test_s354_a_challenge_does_not_rewrite_a_decided_item(db):
    sb = _challenged(db)
    with pytest.raises(ValueError, match="decisions.author") as err:
        sb.call("problem.assert", id="confirm_default_on_eof", kind="in_scope",
                text="The `confirm()` function now accepts an optional boolean "
                     "argument `default_on_eof`, which defaults to `False`.")
    assert "confirm_default_on_eof is the principal's own words" in str(err.value)
    assert not _item_writes(sb)
    # The route the refusal names lands in the same mode.
    sb.call("decisions.author", id="confirm_asks_for_the_flag",
            text="The item asks for the default_on_eof flag on confirm.",
            refs=["confirm_default_on_eof"])
    assert any(w[0] == "decisions" for w in sb.ctx.writes)


def test_s399_a_contest_admits_only_the_principals_words(db):
    _contest(db, "version_option_show_python", VOPT_SAID, "m250")
    sb = _contested(db, "version_option_show_python")
    with pytest.raises(ValueError, match="the principal said") as err:
        sb.call("problem.assert", id="version_option_show_python",
                kind="in_scope",
                text="The `version_option` will display the running Python "
                     "version as major.minor.micro without requiring a flag.")
    msg = str(err.value)
    assert "version_option_show_python is the principal's own words" in msg
    assert "drops `show_python`" in msg
    assert not _item_writes(sb)


def test_s328_a_challenge_creates_no_request(db):
    sb = _challenged(db)
    with pytest.raises(ValueError, match="decisions.author") as err:
        sb.call("problem.assert", id="cr_3_show_python_append", kind="in_scope",
                text="Append the running Python version to the version message.")
    assert "cr_3_show_python_append" in str(err.value)
    assert not _item_writes(sb)


def test_a_contest_that_carries_the_principals_words_lands(db):
    _contest(db, "tip_split", "no service quality. just bill + tip %", "m10")
    sb = _contested(db, "tip_split")
    out = sb.call("problem.assert", id="tip_split", kind="in_scope",
                  text="Calculate tips based on bill amount and tip percentage")
    assert out == {"id": "tip_split"}
    assert _item_writes(sb)[-1][2]["approval"] == "draft"


def test_the_contested_briefs_own_example_lands(db):
    _contest(db, "tip_split", "no service quality, just bill and tip percent",
             "m11")
    sb = _contested(db, "tip_split")
    out = sb.call("problem.assert", id="tip_split", kind="in_scope",
                  text="Calculate the tip from the bill and the tip percent")
    assert out == {"id": "tip_split"}


def test_a_ruling_row_carries_the_words_too(db):
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "seq) VALUES ('m249', 'th', 'liaison', 'principal', 'present', 4)")
    db.execute("INSERT INTO rulings (id, ask_id, per_item, words, status) "
               "VALUES ('r_1', 'm249', ?, ?, 'landed')",
               (json.dumps({"version_option_show_python": "contest"}), VOPT_SAID))
    backfill_ruled_refs(db)
    db.commit()
    sb = _contested(db, "version_option_show_python")
    out = sb.call("problem.assert", id="version_option_show_python",
                  kind="in_scope",
                  text="The `version_option` will include a `show_python` "
                       "flag that appends the running Python version from "
                       "the interpreter's version info, shown as "
                       "major.minor.micro.")
    assert out == {"id": "version_option_show_python"}


def test_an_item_the_principal_did_not_decide_lands_on_a_challenge(db):
    sb = _challenged(db)
    out = sb.call("problem.assert", id="reads_flags", kind="in_scope",
                  text="the program reads short and long flags from the "
                       "command line")
    assert out == {"id": "reads_flags"}


def test_the_items_own_words_stay_unchanged_on_a_challenge(db):
    sb = _challenged(db)
    out = sb.call("problem.assert", id="confirm_default_on_eof",
                  kind="in_scope", text=CONFIRM)
    assert out.get("unchanged"), out
    assert not _item_writes(sb)


def _ruling(conn, rid, per_item, said):
    conn.execute("INSERT OR IGNORE INTO messages (id, thread_id, from_role, "
                 "to_role, verb, seq) VALUES ('m249', 'th', 'liaison', "
                 "'principal', 'present', 4)")
    conn.execute("INSERT INTO rulings (id, ask_id, per_item, words, status) "
                 "VALUES (?, 'm249', ?, ?, 'landed')",
                 (rid, json.dumps(per_item), said))
    backfill_ruled_refs(conn)
    conn.commit()


def test_s399_a_ruling_that_approves_the_item_is_no_contest_on_it(db):
    # r_8b2329d2da: the item approve, a criterion contest (night 146, m250).
    _ruling(db, "r_8b2329d2da", {"version_option_show_python": "approve",
                                 "l_cee175bedd": "contest"}, VOPT_SAID)
    sb = _contested(db, "version_option_show_python")
    with pytest.raises(ValueError, match="rules .* approve, not contest") as err:
        sb.call("problem.assert", id="version_option_show_python",
                kind="in_scope",
                text="The `version_option` will display the running Python "
                     "version as major.minor.micro without requiring a flag.")
    assert "msg.report_liaison" in str(err.value)
    assert not _item_writes(sb)


def test_a_negated_name_is_a_drop(db):
    _contest(db, "version_option_show_python", VOPT_SAID, "m250")
    sb = _contested(db, "version_option_show_python")
    with pytest.raises(ValueError, match="drops `show_python`"):
        sb.call("problem.assert", id="version_option_show_python",
                kind="in_scope",
                text="The `version_option` will not include a `show_python` "
                     "flag and appends the running Python version to the "
                     "message.")


def test_s128_a_criterion_contest_in_the_principals_words_is_refused(db):
    _ruling(db, "r_s128", {"confirm_default_on_eof": "approve",
                           "c_line3": "contest"},
            "Line 3 isn't right: objects should go straight to the json module.")
    sb = _contested(db, "confirm_default_on_eof")
    with pytest.raises(ValueError, match="rules .* approve, not contest"):
        sb.call("problem.assert", id="confirm_default_on_eof", kind="in_scope",
                text=CONFIRM + " Objects go straight to the json module.")


def test_an_exhausted_batch_does_not_rewrite_a_decided_item(db):
    sb = build("vision_keeper", db, mode="exhausted",
               allow=prompts.mode_tools("vision_keeper", "exhausted"),
               wake=Wake("vision_keeper", "tick:exhausted", refs=("bg_5",)))
    with pytest.raises(ValueError) as err:
        sb.call("problem.assert", id="confirm_default_on_eof", kind="in_scope",
                text="confirm() takes a default_on_eof argument.")
    msg = str(err.value)
    assert msg.index("msg.report_liaison") < msg.index("decisions.author")
    assert not _item_writes(sb)


def test_a_removal_in_plain_words_admits_the_drop(db):
    # The second review's probe P3: the words never hold the identifier.
    _ruling(db, "r_p3", {"version_option_show_python": "contest"},
            "I don't want a flag. Always append the running Python version, "
            "shown as major.minor.micro.")
    # The Liaison reads "I don't want a flag" as the removal of the flag
    # (the seam design, pass 4, P2).
    seed_acts(db, "r_p3", {"version_option_show_python": {
        "act": "remove", "target_kind": "identifier", "target": "show_python"}})
    sb = _contested(db, "version_option_show_python")
    out = sb.call("problem.assert", id="version_option_show_python",
                  kind="in_scope",
                  text="The `version_option` always appends the running "
                       "Python version, shown as major.minor.micro.")
    assert out == {"id": "version_option_show_python"}


def test_an_open_ruling_does_not_hide_a_landed_contest(db):
    _ruling(db, "r_landed", {"version_option_show_python": "contest"},
            VOPT_SAID)
    db.execute("INSERT INTO rulings (id, ask_id, per_item, words, status) "
               "VALUES ('r_open', 'm249', ?, 'Ok', 'open')",
               (json.dumps({"version_option_show_python": "approve"}),))
    backfill_ruled_refs(db)
    db.commit()
    sb = _contested(db, "version_option_show_python")
    out = sb.call("problem.assert", id="version_option_show_python",
                  kind="in_scope",
                  text="The `version_option` will include a `show_python` "
                       "flag that appends the running Python version, shown "
                       "as major.minor.micro.")
    assert out == {"id": "version_option_show_python"}


S232 = ("Let confirm() take a default_on_eof flag: when stdin is closed it "
        "returns the default instead of aborting. The flag default is passed "
        "to confirm itself.")


def _proposed(conn):
    # Night 149's walk 3: the Architect's msg.propose_vision_keeper woke s232.
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "body_refs, body_text, seq) VALUES ('m_prop', 't2', "
                 "'architect', 'vision_keeper', 'propose', ?, 'a default "
                 "passed to confirm', 2)",
                 (json.dumps(["confirm_default_on_eof"]),))
    conn.commit()
    sb = build("vision_keeper", conn, mode="propose",
               allow=prompts.mode_tools("vision_keeper", "propose"),
               wake=Wake("vision_keeper", "message", message_id="m_prop",
                         detail="propose"))
    sb.ctx.trigger = "m_prop"
    return sb


def test_s232_a_propose_wake_does_not_rewrite_a_decided_item(db):
    # Frame 129: s232's assert landed, the item went to version 3 and draft,
    # and the scheduler cancelled the batch (plans/night149-read.md, W1).
    sb = _proposed(db)
    with pytest.raises(ValueError) as err:
        sb.call("problem.assert", id="confirm_default_on_eof",
                kind="in_scope", text=S232)
    msg = str(err.value)
    assert "confirm_default_on_eof is the principal's own words" in msg
    assert "A propose wake does not rewrite them" in msg
    assert msg.index("msg.report_liaison") < msg.index("decisions.author")
    assert not _item_writes(sb)
    row = db.execute("SELECT text, version FROM items "
                     "WHERE id = 'confirm_default_on_eof'").fetchone()
    assert (row["text"], row["version"]) == (CONFIRM, 1)


def test_s232_text_on_a_landed_contest_takes_the_words_branch(db):
    _ruling(db, "r_s232", {"confirm_default_on_eof": "contest"},
            "Let confirm take a default. The flag defaults to False.")
    sb = _contested(db, "confirm_default_on_eof")
    with pytest.raises(ValueError, match="The new text says") as err:
        sb.call("problem.assert", id="confirm_default_on_eof",
                kind="in_scope", text=S232)
    assert "the principal said" in str(err.value)
    assert not _item_writes(sb)


def _woken(conn, mid, sender, verb):
    """A Vision Keeper session on a message wake, in the verb's mode."""
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "body_refs, body_text, seq) VALUES (?, 't3', ?, "
                 "'vision_keeper', ?, ?, 'the default on EOF', 3)",
                 (mid, sender, verb, json.dumps(["confirm_default_on_eof"])))
    conn.commit()
    sb = build("vision_keeper", conn, mode=verb,
               allow=prompts.mode_tools("vision_keeper", verb),
               wake=Wake("vision_keeper", "message", message_id=mid,
                         detail=verb))
    sb.ctx.trigger = mid
    return sb


def test_a_deliver_wake_amends_a_decided_item(db):
    # The review of 0bf6a5ea, finding 3: a deliver wake carries a newly
    # ratified statement, and its brief keeps the existing id.
    sb = _woken(db, "m_del", "liaison", "deliver")
    out = sb.call("problem.assert", id="confirm_default_on_eof",
                  kind="in_scope", text=CONFIRM + " The flag defaults to False.")
    assert out == {"id": "confirm_default_on_eof"}
    assert _item_writes(sb)


def test_an_answer_wake_names_only_calls_the_mode_offers(db):
    # The review of 0bf6a5ea, findings 1 and 4.
    sb = _woken(db, "m_ans", "researcher", "answer")
    with pytest.raises(ValueError) as err:
        sb.call("problem.assert", id="confirm_default_on_eof",
                kind="in_scope", text=S232)
    msg = str(err.value)
    assert "An answer wake does not rewrite them" in msg
    offered = set(_wake_mode_tools(sb.ctx))
    named = set(re.findall(r"\b[a-z]+\.[a-z_]+\b", msg))
    assert named <= offered, named - offered
    assert not _item_writes(sb)


HOW = ("The program is a command-line interface toolkit called Click. Users "
       "write scripts that define commands and options, and Click parses "
       "command-line arguments and options, then executes the corresponding "
       "Python functions with the provided inputs.")
M25 = ("Ok, this matches what I asked for. Please build it with the standard "
       "library json module only.")
JSON_ONLY = ("The program is built using the standard library json module only, "
             "without the Click toolkit.")
# r_c38db1262c, his reply to the page m90 (night 150).
M91 = ("Lines 2 through 7 are about the echo_json helper, which I put aside "
       "until the confirm change is merged, so please take them off this page. "
       "The page should cover only the confirm flag. It should also say that "
       "the flag defaults to False, so nothing changes for people who already "
       "call confirm().")
# r_20d87b3d5e, his reply to the page m37 (night 150).
M38 = ("Line 1 is wrong, because I never asked for anything to be built "
       "without Click. What I asked for is an echo_json helper inside Click, "
       "next to echo, that uses the standard library json module to print an "
       "object as compact JSON on one line, followed by a newline. Lines 2 "
       "through 5 come from that misreading, so please drop them.")


def _night150_item(conn, iid, text):
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version, is_description) VALUES (?, ?, 'in_scope', "
                 "'contested', 1, 1, 0)", (iid, text))
    seed_provenance(conn, "items", iid, "decided")
    conn.commit()


def test_s112_a_contested_wake_makes_no_new_item(db):
    # Frame 129: s112, woken by tick:contested on how_it_works after m25,
    # asserted the new item json_only in turn 7, and both batches of
    # night 150 were cancelled on it (plans/night150-read.md, section 7).
    _night150_item(db, "how_it_works", HOW)
    _ruling(db, "r_38e7b457e9", {"echo_json": "approve",
                                 "how_it_works": "contest"}, M25)
    sb = _contested(db, "how_it_works")
    with pytest.raises(ValueError) as err:
        sb.call("problem.assert", id="json_only", kind="in_scope",
                text=JSON_ONLY)
    msg = str(err.value)
    assert msg.startswith("json_only is not an item")
    assert "how_it_works" in msg
    offered = set(_wake_mode_tools(sb.ctx))
    named = set(re.findall(r"\b[a-z]+\.[a-z_]+\b", msg))
    assert named and named <= offered, (named, offered)
    assert {"problem.assert", "decisions.author"} <= named
    assert not _item_writes(sb)
    assert db.execute("SELECT 1 FROM items WHERE id = 'json_only'"
                      ).fetchone() is None


def test_s112_turn_6_his_reply_word_for_word_is_refused(db):
    # Frame 263: s112 turn 6 asserted how_it_works as his m25 reply.
    _night150_item(db, "how_it_works", HOW)
    _ruling(db, "r_38e7b457e9", {"echo_json": "approve",
                                 "how_it_works": "contest"}, M25)
    sb = _contested(db, "how_it_works")
    with pytest.raises(ValueError) as err:
        sb.call("problem.assert", id="how_it_works", kind="in_scope", text=M25)
    msg = str(err.value)
    assert "his reply word for word" in msg
    assert "Write what the principal said" not in msg
    assert not _item_writes(sb)


def test_s205_his_instruction_about_the_page_is_refused(db):
    # Frame 263: s205 rewrote json_only with his m91 sentence about the page,
    # "The page should cover only the confirm flag", the page made the
    # program (plans/night150-read.md, section 7).
    _night150_item(db, "json_only", JSON_ONLY)
    _ruling(db, "r_c38db1262c", {"json_only": "contest",
                                 "confirm_default_on_eof": "approve"}, M91)
    # His sentence about the page is the span of his row on another line.
    seed_acts(db, "r_c38db1262c", {"confirm_default_on_eof": {
        "line": 1, "words": "The page should cover only the confirm flag."}})
    sb = _contested(db, "json_only")
    with pytest.raises(ValueError) as err:
        sb.call("problem.assert", id="json_only", kind="in_scope",
                text="The program should cover only the confirm flag. It "
                     "should also say that the flag defaults to False, so "
                     "nothing changes for people who already call confirm().")
    msg = str(err.value)
    assert "The page should cover only the confirm flag." in msg
    assert "about the page" in msg
    assert "Write what the principal said" not in msg
    assert not _item_writes(sb)


def test_s404_a_text_that_names_lines_of_the_page_is_refused(db):
    # s404 rewrote json_only with "Lines 4 to 8 describe the JSON echo
    # helper", his m310 reply.
    _night150_item(db, "json_only", JSON_ONLY)
    said = ("Line 3 is wrong because it limits the work to the confirm flag, "
            "and this change is only the show_python flag for version_option. "
            "Lines 4 to 8 describe the JSON echo helper instead of this "
            "change, so please replace them with requirements for the "
            "version flag.")
    _ruling(db, "r_071c6da0de", {"json_only": "contest"}, said)
    sb = _contested(db, "json_only")
    with pytest.raises(ValueError, match="about the page"):
        sb.call("problem.assert", id="json_only", kind="in_scope",
                text="The program should cover only the version flag. Lines 4 "
                     "to 8 describe the JSON echo helper instead of this "
                     "change, so please replace them with requirements for "
                     "the version flag.")
    assert not _item_writes(sb)


def test_an_amend_with_his_ruling_sentence_lands(db):
    # The contested mode's first case: his sentence about the item, on the
    # item's own id, lands.
    _night150_item(db, "json_only", JSON_ONLY)
    _ruling(db, "r_20d87b3d5e", {"json_only": "contest"}, M38)
    sb = _contested(db, "json_only")
    out = sb.call("problem.assert", id="json_only", kind="in_scope",
                  text="An echo_json helper inside Click, next to echo, uses "
                       "the standard library json module to print an object "
                       "as compact JSON on one line, followed by a newline.")
    assert out == {"id": "json_only"}
    assert _item_writes(sb)


def test_the_words_repair_says_what_an_items_text_is(db):
    # Frame 263: the old step, "Write what the principal said", sent s205
    # and s404 to write his reply into the item.
    _ruling(db, "r_s232", {"confirm_default_on_eof": "contest"},
            "Let confirm take a default. The flag defaults to False.")
    sb = _contested(db, "confirm_default_on_eof")
    with pytest.raises(ValueError, match="The new text says") as err:
        sb.call("problem.assert", id="confirm_default_on_eof",
                kind="in_scope", text=S232)
    msg = str(err.value)
    assert "Write what the principal said" not in msg
    assert "never his instruction about the page or the team" in msg
    assert repr(CONFIRM) in msg
    assert "'Let confirm take a default.'" in msg


def test_an_item_the_wake_did_not_name_is_refused(db):
    _ruling(db, "r_landed", {"version_option_show_python": "contest"},
            VOPT_SAID)
    sb = _contested(db, "tip_split")
    with pytest.raises(ValueError, match="names no contest on "
                                         "version_option_show_python"):
        sb.call("problem.assert", id="version_option_show_python",
                kind="in_scope",
                text="The `version_option` will include a `show_python` "
                     "flag, shown as major.minor.micro.")


# Night 167, walk 1: s161 seq 9 amended get_app_dir_windows with his m57
# sentence about the test, and no seat could take it out again
# (plans/night167-walk1-loop.md, section 1).
APPDIR = ("In get_app_dir on Windows, when APPDATA or LOCALAPPDATA is not "
          "set, use the AppData Roaming or AppData Local folder under the home "
          "folder instead of the bare home folder.")
APPDIR_CHECK = ("Its check calls the function without an app name, so it "
                "fails before it tests anything.")
APPDIR_RULE = ("Use the Roaming folder when the roaming flag is True, and the "
               "Local folder otherwise.")
M57 = f"Line 10 is still wrong. {APPDIR_CHECK}"
# His recorded reply form to the pages m66 to m118 (plans/stack.md, frame
# 315). It points at no sentence of the item.
TAKE_OUT = ("Line 1 still has the extra sentence about which tests to run, so "
            "please take it out and keep only what I asked for.")
CHANGE = ("Remove the fallback to the bare home folder and use the Local "
          "folder.")
M24 = ("Replace it with the rule I want: use the Roaming folder when the "
       "roaming flag is True, and the Local folder otherwise.")
# s161's own paraphrase, refused for new words (s161 turn 5).
APPDIR_PARA = ("In get_app_dir on Windows, use the AppData folders when the "
               "variables are missing.")


def test_s161_his_sentence_about_the_test_is_not_the_items(db):
    _night150_item(db, "get_app_dir_windows", APPDIR)
    # m57's sentence about the check is his contest of line 10, another row.
    _contest(db, "get_app_dir_windows", M57, "m58", {
        "confirm_default_on_eof": {"verdict": "contest", "line": 10,
                                   "words": APPDIR_CHECK}})
    sb = _contested(db, "get_app_dir_windows")
    with pytest.raises(ValueError) as err:
        sb.call("problem.assert", id="get_app_dir_windows", kind="in_scope",
                text=APPDIR_PARA)
    step = str(err.value)
    assert f"with his sentence {APPDIR_CHECK!r}" not in step
    assert "line 10" in step
    with pytest.raises(ValueError) as err:
        sb.call("problem.assert", id="get_app_dir_windows", kind="in_scope",
                text=f"{APPDIR} {APPDIR_CHECK}")
    msg = str(err.value)
    assert "line 10" in msg and "not the item" in msg
    assert f"with his sentence {APPDIR_CHECK!r}" not in msg
    assert not _item_writes(sb)


# The Liaison's reading of a request to take a sentence out (pass 4, P3).
REMOVE_SENTENCE = {"act": "remove", "target_kind": "sentence"}


def _amended_on_contest(conn, item):
    """
    The item at version 2: s161, on `tick:contested` after m57, appended his
    test sentence (night 167, s161 seq 9). Its receipt is the record.
    """
    conn.execute("UPDATE items SET text = ?, version = 2 WHERE id = ?",
                 (f"{APPDIR} {APPDIR_CHECK}", item))
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                 "verb, body_refs, seq) VALUES ('m57', 'th', 'principal', "
                 "'liaison', 'reply', '[]', 3)")
    conn.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
                 "('e_m57', 'principal', ?, 0)", (M57,))
    conn.execute("INSERT INTO sessions (id, role, seq, wake_kind) VALUES "
                 "('s161', 'vision_keeper', 161, 'tick:contested')")
    conn.execute("INSERT INTO receipts (session_id, table_name, row_id, "
                 "new_version) VALUES ('s161', 'items', ?, 2)", (item,))
    conn.commit()


def test_his_recorded_removal_drops_what_a_contested_amend_added(db):
    _night150_item(db, "get_app_dir_windows", APPDIR)
    _amended_on_contest(db, "get_app_dir_windows")
    _contest(db, "get_app_dir_windows", TAKE_OUT, "m67",
             {"get_app_dir_windows": REMOVE_SENTENCE})
    sb = _contested(db, "get_app_dir_windows")
    with pytest.raises(ValueError) as err:
        sb.call("problem.assert", id="get_app_dir_windows", kind="in_scope",
                text=APPDIR_PARA)
    step = str(err.value)
    assert f"added, {APPDIR_CHECK!r}" in step
    assert f"Assert {APPDIR!r}" in step
    assert f"with his sentence {TAKE_OUT!r}" not in step
    out = sb.call("problem.assert", id="get_app_dir_windows",
                  kind="in_scope", text=APPDIR)
    assert out == {"id": "get_app_dir_windows", "removed": [APPDIR_CHECK]}
    assert _item_writes(sb)


def test_a_change_request_does_not_drop_the_items_own_sentence(db):
    _night150_item(db, "get_app_dir_windows", APPDIR)
    _amended_on_contest(db, "get_app_dir_windows")
    _contest(db, "get_app_dir_windows", CHANGE, "m67")
    sb = _contested(db, "get_app_dir_windows")
    with pytest.raises(ValueError):
        sb.call("problem.assert", id="get_app_dir_windows", kind="in_scope",
                text=APPDIR_CHECK)
    assert not _item_writes(sb)


def test_m24_a_correction_keeps_the_amend_and_refuses_a_drop(db):
    _night150_item(db, "get_app_dir_windows", f"{APPDIR} {APPDIR_RULE}")
    _contest(db, "get_app_dir_windows", M24, "m25")
    sb = _contested(db, "get_app_dir_windows")
    with pytest.raises(ValueError) as err:
        sb.call("problem.assert", id="get_app_dir_windows", kind="in_scope",
                text=f"{APPDIR} Pick the folder from the profile type.")
    assert f"with his sentence {M24!r}" in str(err.value)
    with pytest.raises(ValueError):
        sb.call("problem.assert", id="get_app_dir_windows", kind="in_scope",
                text=APPDIR)
    assert not _item_writes(sb)


def test_a_removal_with_nothing_added_offers_the_plain_amend(db):
    # No receipt of a contested amend on the item: the second sentence is
    # his, and it stays.
    _night150_item(db, "get_app_dir_windows", f"{APPDIR} {APPDIR_RULE}")
    _contest(db, "get_app_dir_windows", TAKE_OUT, "m67",
             {"get_app_dir_windows": REMOVE_SENTENCE})
    sb = _contested(db, "get_app_dir_windows")
    with pytest.raises(ValueError) as err:
        sb.call("problem.assert", id="get_app_dir_windows", kind="in_scope",
                text=APPDIR_PARA)
    step = str(err.value)
    assert "nothing was added" in step
    assert f"with his sentence {TAKE_OUT!r}" not in step
    with pytest.raises(ValueError, match="The new text drops"):
        sb.call("problem.assert", id="get_app_dir_windows", kind="in_scope",
                text=APPDIR)
    assert not _item_writes(sb)
