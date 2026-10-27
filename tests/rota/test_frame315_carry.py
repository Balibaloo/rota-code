"""Frame 315, repair 1: the criteria wake and the slicing wake carry the
principal's landed words and the old ticket's criteria.

Night 161: his correction landed on tk_1's criteria at version 4 (s274).
The item was amended, tk_2 was sliced, and s282's criteria wake showed the
statement s3 only. The rows below are night 161's, copied from
`.rota/clickI_night161.db`.
"""
import json

from rota.core.db import backfill_ruled_refs, init_db
from rota.core.runner import push_working_set
from rota.core.sandbox import build
from rota.core.scheduler import Wake
from rota.roles import prompts
from rota.testkit.fixtures import seed_provenance, seed_ref

ITEM = "version_option_show_python"
S3 = ("Give version_option a show_python flag that appends the running "
      "Python version to the message")
ITEM_TEXT = (S3 + ". The Python version should also be shown as "
             "major.minor.micro from sys.version_info.")
C1 = ("The version_option accepts a boolean argument `show_python` that the "
      "developer passes to the command. When `show_python` is True, the output "
      "message includes the running Python version string formatted as "
      "major.minor.micro from sys.version_info. When `show_python` is False or "
      "omitted, the output message does not include the Python version.")
C2 = ("When the developer passes `show_python=True` to version_option, the "
      "output message includes the running Python version string formatted as "
      "major.minor.micro from sys.version_info.")
C3 = ("When the developer passes `show_python=False` or does not pass it to "
      "version_option, the output message does not include the Python version string.")
M118 = ("Ok, that's what I meant. The Python version should come from "
        "sys.version_info, shown as major.minor.micro.")
M128 = ("There's no specific command, so write the test against a small "
        "throwaway command defined inside the test.")
M131 = ("Line 2 is wrong. I meant show_python as a true-or-false argument that "
        "the developer passes to version_option, not a new show-python flag that "
        "the user types on the command line, so lines 3 and 4 should also say the "
        "version message has the Python version when show_python is on and leaves "
        "it out when it is off. The Python version should also be shown as "
        "major.minor.micro from sys.version_info.")
M137 = ("Yes, show_python is a true-or-false argument that the developer passes "
        "to version_option, and when it is on the version message ends with the "
        "running Python version as major.minor.micro from sys.version_info. When "
        "it is off, the message stays exactly as it is today.")
RULED_KEY = "the principal ruled on this item, newest last"
RETIRED_KEY = "criteria of an old ticket, written before the item changed"
TK1 = "tk_1_version_option_show_python"
TK2 = "tk_2_version_option_show_python"


def _night161(tmp_path, *, sliced: bool):
    """Night 161 at the start of s282, or of s281 when `sliced` is False."""
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES ('e1','principal',1,?)", (S3,))
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, status) "
               "VALUES ('s3','e1',0,?,?,'ratified')", (len(S3), S3))
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES (?, ?, 'in_scope', 'approved', 4, 4)", (ITEM, ITEM_TEXT))
    seed_ref(db, "items", ITEM, "statement", "s3")
    seed_provenance(db, "items", ITEM, "decided")
    db.execute("INSERT INTO tickets (id, item_id, text, item_ver) VALUES (?, ?, ?, 3)",
               (TK1, ITEM, S3.lower()))
    for n, text in ((1, C1), (2, C2), (3, C3)):
        db.execute("INSERT INTO criteria (id, ticket_id, text, version) VALUES (?, ?, ?, 4)",
                   (f"c_{n}_{ITEM}", TK1, text))
    if sliced:
        db.execute("INSERT INTO tickets (id, item_id, text, item_ver) VALUES (?, ?, ?, 4)",
                   (TK2, ITEM, S3.lower()))
    rulings = (
        ("r_210e7c6912", "m117", "m118", {ITEM: "approve"}, M118),
        ("r_83a0b075a0", "m127", "m128", {f"c_{n}_{ITEM}": "approve" for n in (1, 2, 3)}, M128),
        ("r_5346319ecc", "m130", "m131", {ITEM: "contest", f"c_1_{ITEM}": "contest",
                                          f"c_2_{ITEM}": "revise", f"c_3_{ITEM}": "revise",
                                          "b_4": "approve"}, M131),
        ("r_206b20c23b", "m136", "m137", {ITEM: "approve", "e_m132": "approve"}, M137),
    )
    for rid, ask, reply, per_item, words in rulings:
        for mid in (ask, reply):
            db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
                       "VALUES (?, 't1', 'liaison', 'principal', 'ask', ?)", (mid, int(mid[1:])))
        db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, status) "
                   "VALUES (?, ?, ?, ?, ?, 'landed')", (rid, ask, reply, json.dumps(per_item), words))
    # A ruling on another item stays out of this item's wake.
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
               "VALUES ('m900', 't1', 'liaison', 'principal', 'ask', 900)")
    db.execute("INSERT INTO rulings (id, ask_id, per_item, words, status) VALUES "
               "('r_other', 'm900', '{\"other_item\": \"approve\"}', 'not about show_python', 'landed')")
    backfill_ruled_refs(db)
    db.commit()
    return db


def _assert_carry(carry: dict) -> None:
    assert M131 in carry[RULED_KEY]
    assert M137 in carry[RULED_KEY]
    # The cap keeps the last three, newest last.
    assert carry[RULED_KEY] == [M128, M131, M137]
    old = {c["id"]: c for c in carry[RETIRED_KEY]}
    assert old[f"c_1_{ITEM}"] == {"old ticket": TK1, "id": f"c_1_{ITEM}",
                                  "version": 4, "text": C1}
    assert sorted(old) == [f"c_{n}_{ITEM}" for n in (1, 2, 3)]


def test_s282_criteria_wake_carries_his_words_and_the_old_criteria(tmp_path):
    db = _night161(tmp_path, sliced=True)
    sb = build("terminologist", db, mode="criteria",
               allow=prompts.mode_tools("terminologist", "criteria"))
    pushed = push_working_set("terminologist", sb, Wake("terminologist", "tick:criteria", refs=(ITEM,)))
    item = pushed["the item"]
    assert item["the principal said"] == [S3]
    _assert_carry(item)


def test_the_slicing_wake_carries_the_same_keys(tmp_path):
    for sliced in (False, True):
        sub = tmp_path / str(sliced)
        sub.mkdir()
        db = _night161(sub, sliced=sliced)
        sb = build("vision_keeper", db, mode="slicing",
                   allow=prompts.mode_tools("vision_keeper", "slicing"))
        pushed = push_working_set("vision_keeper", sb, Wake("vision_keeper", "tick:slicing", refs=(ITEM,)))
        [row] = pushed["problem.consult"]["to slice, this wake"]
        _assert_carry(row)


def test_an_item_with_no_old_ticket_carries_his_words_and_no_old_criteria(tmp_path):
    """Frame 322, proposal line 2: his words on the item travel on every
    generation. A ruling on the live criteria stays out (review 1,
    finding 1), so r_83a0b075a0 and r_5346319ecc give none."""
    db = _night161(tmp_path, sliced=True)
    db.execute("UPDATE tickets SET item_ver = 4")
    db.commit()
    sb = build("terminologist", db, mode="criteria",
               allow=prompts.mode_tools("terminologist", "criteria"))
    pushed = push_working_set("terminologist", sb, Wake("terminologist", "tick:criteria", refs=(ITEM,)))
    assert set(pushed["the item"]) == {"text", "the principal said", RULED_KEY}
    assert pushed["the item"][RULED_KEY] == [M118, M137]


def _ruling(db, rid: str, seq: int, per_item: dict, words: str) -> None:
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
               "VALUES (?, 't1', 'liaison', 'principal', 'ask', ?)", (f"m{seq}", seq))
    db.execute("INSERT INTO rulings (id, ask_id, per_item, words, status) "
               "VALUES (?, ?, ?, ?, 'landed')", (rid, f"m{seq}", json.dumps(per_item), words))
    backfill_ruled_refs(db)


def _criteria_wake(db) -> dict:
    sb = build("terminologist", db, mode="criteria",
               allow=prompts.mode_tools("terminologist", "criteria"))
    return push_working_set("terminologist", sb,
                            Wake("terminologist", "tick:criteria", refs=(ITEM,)))["the item"]


def test_rulings_on_the_live_ticket_do_not_push_his_correction_out(tmp_path):
    """Review 1, finding 1: at night 161's end, r_40c94b2c6d, r_288739e866
    and r_810ee68dc8 said "take the confirm lines off this page" on tk_2's
    rows, and filled the cap of three."""
    db = _night161(tmp_path, sliced=True)
    live = f"c_2_{ITEM}_format"
    db.execute("INSERT INTO criteria (id, ticket_id, text, version) VALUES (?, ?, 'x', 1)", (live, TK2))
    for n, rid in enumerate(("r_40c94b2c6d", "r_288739e866", "r_810ee68dc8")):
        _ruling(db, rid, 218 + n, {ITEM: "approve", live: "approve", f"l_{n}": "contest"},
                "Lines 8 to 12 are about the confirm change, not this one, so please take them off this page.")
    db.commit()
    carry = _criteria_wake(db)
    assert carry[RULED_KEY] == [M128, M131, M137]


def test_a_ruling_that_names_only_the_old_ticket_is_carried(tmp_path):
    """Review 1, finding 5."""
    db = _night161(tmp_path, sliced=True)
    _ruling(db, "r_tk1", 300, {TK1: "contest"}, "The old ticket said flag.")
    db.commit()
    assert _criteria_wake(db)[RULED_KEY][-1] == "The old ticket said flag."


def test_the_criteria_wake_never_counts_the_live_ticket_old(tmp_path):
    """Review 1, finding 4: an amend raises the item above every ticket."""
    db = _night161(tmp_path, sliced=True)
    db.execute("UPDATE items SET version = 5 WHERE id = ?", (ITEM,))
    db.execute("INSERT INTO criteria (id, ticket_id, text, version) VALUES ('c_live', ?, 'live', 1)", (TK2,))
    db.commit()
    shown = [c["id"] for c in _criteria_wake(db)[RETIRED_KEY]]
    assert shown == [f"c_{n}_{ITEM}" for n in (1, 2, 3)]


def test_the_old_criteria_keep_the_newest_old_generation(tmp_path):
    """Review 1, finding 6: one slicing wake holds every item due a slice."""
    db = _night161(tmp_path, sliced=True)
    db.execute("INSERT INTO tickets (id, item_id, text, item_ver) VALUES ('tk_0', ?, 'first', 2)", (ITEM,))
    db.execute("INSERT INTO criteria (id, ticket_id, text, version) VALUES ('c_0', 'tk_0', 'first', 1)")
    db.commit()
    shown = [c["id"] for c in _criteria_wake(db)[RETIRED_KEY]]
    assert shown == [f"c_{n}_{ITEM}" for n in (1, 2, 3)]


# Night 166's m69 on the guess page m68, landed as r_1ec1beb146 at 19:32:27.
# s185's criteria prompt at 19:36 did not carry it, because the item had no
# old ticket (`plans/frame322-we-read.md`, section 1).
M69 = "only the docstring changes while the code stays the same"
DOC_ITEM = "format_filename_example"


def test_s185s_first_criteria_wake_carries_r_1ec1beb146(tmp_path):
    """Frame 322, proposal line 5. Red on 624621eb: the window held the
    statement and no word of his ruling."""
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES (?, 'Add an example to the docstring of format_filename', "
               "'in_scope', 'approved', 1, 1)", (DOC_ITEM,))
    seed_provenance(db, "items", DOC_ITEM, "decided")
    db.execute("INSERT INTO tickets (id, item_id, text, item_ver) VALUES "
               "('tk_1_doc', ?, 'the docstring example', 1)", (DOC_ITEM,))
    for mid, seq in (("m68", 68), ("m69", 69)):
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
                   "VALUES (?, 't1', 'liaison', 'principal', 'ask', ?)", (mid, seq))
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, status) "
               "VALUES ('r_1ec1beb146', 'm68', 'm69', ?, ?, 'landed')",
               (json.dumps({DOC_ITEM: "approve", f"guess:{DOC_ITEM}": "contest"}), M69))
    backfill_ruled_refs(db)
    db.commit()
    sb = build("terminologist", db, mode="criteria",
               allow=prompts.mode_tools("terminologist", "criteria"))
    pushed = push_working_set("terminologist", sb,
                              Wake("terminologist", "tick:criteria", refs=(DOC_ITEM,)))
    assert pushed["the item"][RULED_KEY] == [M69]
    assert RETIRED_KEY not in pushed["the item"]
