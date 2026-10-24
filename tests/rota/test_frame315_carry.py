"""Frame 315, repair 1: the criteria wake and the slicing wake carry the
principal's landed words and the old ticket's criteria.

Night 161: his correction landed on tk_1's criteria at version 4 (s274).
The item was amended, tk_2 was sliced, and s282's criteria wake showed the
statement s3 only. The rows below are night 161's, copied from
`.rota/clickI_night161.db`.
"""
import json

from rota.core.db import init_db
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


def test_an_item_with_no_old_ticket_wakes_unchanged(tmp_path):
    db = _night161(tmp_path, sliced=True)
    db.execute("UPDATE tickets SET item_ver = 4")
    db.commit()
    sb = build("terminologist", db, mode="criteria",
               allow=prompts.mode_tools("terminologist", "criteria"))
    pushed = push_working_set("terminologist", sb, Wake("terminologist", "tick:criteria", refs=(ITEM,)))
    assert set(pushed["the item"]) == {"text", "the principal said"}
