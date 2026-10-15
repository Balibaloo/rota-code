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

import pytest

from rota.core.db import init_db
from rota.core.predicates import Wake
from rota.core.sandbox import build
from rota.roles import prompts
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


def _contest(conn, item, said, mid):
    """The shape the contested tick reads: a verdict and its entry."""
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "body_refs, seq) VALUES (?, 'th', 'principal', 'liaison', "
                 "'verdict', ?, 5)", (mid, json.dumps([item])))
    conn.execute("INSERT INTO config (key, value) VALUES (?, ?)",
                 (f"verdict:{mid}", json.dumps({item: "contest"})))
    conn.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
                 "(?, 'principal', ?, 1)", (f"e_{mid}", said))
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
