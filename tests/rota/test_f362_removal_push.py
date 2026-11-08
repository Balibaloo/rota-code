"""Frame 362, the removal wall of dry run 7: his reply reaches the seat that
acts on the batch.

On dry run 7 his answer m42 said "Do not remove that branch in _foldline.
Keep everything else as before." It landed as ruling r_m42. The one push
that shows his whole reply fired on `tick:batch_start` only, and no start
wake followed m42. So 0 of 22 Developer sessions and 0 of 4 Architect
`touch_strayed` sessions read his words (`plans/dry7-removal-read-2026-11-08.md`,
the Result and section 5).

The rows are copied from the dry run 7 copy `w6.db`, read with `mode=ro`:
the batch b1, its ticket and criteria, the page m29, the reply m42, the
ruling r_m42 with its 23 `ruled_refs` rows, and one `mistake` stray row.
The copy is about 70 MB, so the rows are rebuilt inline. The tree is a
fixture of `_foldline`, so the test needs no icalendar checkout.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from rota.core import predicates as P
from rota.core.db import init_db
from rota.core.loop import _batch_of
from rota.core.runner import (START_RULED_KEY, build_prompt, push_working_set,
                              resolve_inbound, session_sandbox)
from rota.core.scheduler import Wake

PATH = "src/icalendar/parser/string.py"
GRAIN = f"{PATH}::_foldline"
# The branch that dry run 7's commits removed, and the base lines around it.
BASE = '''"""Functions for content lines."""

DEFAULT_ENCODING = "utf-8"


def _foldline(line, limit=75, fold_sep="\\r\\n "):
    """Make a string folded as defined in RFC5545."""
    folded_lines = []
    current_chars = []
    byte_count = 0
    for char in line:
        char_byte_len = len(char.encode(DEFAULT_ENCODING))
        if byte_count + char_byte_len > limit:
            # 1501: an escaped value is never split across a fold.
            if len(current_chars) > 1 and current_chars[-1] in r"\\^":
                escaped_prefix = current_chars.pop()
                folded_lines.append("".join(current_chars))
                current_chars = [escaped_prefix]
                byte_count = len(escaped_prefix.encode(DEFAULT_ENCODING))
            else:
                folded_lines.append("".join(current_chars))
                current_chars = []
                byte_count = 0
        current_chars.append(char)
        byte_count += char_byte_len
    folded_lines.append("".join(current_chars))
    return fold_sep.join(folded_lines)
'''
BRANCH = '''            # 1501: an escaped value is never split across a fold.
            if len(current_chars) > 1 and current_chars[-1] in r"\\^":
                escaped_prefix = current_chars.pop()
                folded_lines.append("".join(current_chars))
                current_chars = [escaped_prefix]
                byte_count = len(escaped_prefix.encode(DEFAULT_ENCODING))
            else:
                folded_lines.append("".join(current_chars))
                current_chars = []
                byte_count = 0
'''
HEAD_BRANCH = '''            folded_lines.append("".join(current_chars))
            current_chars = []
            byte_count = 0
'''
ITEM = "folds_long_lines"
ITEM_TEXT = ("When icalendar writes a long line, fold it at a space where it can, "
             "so that a word is not split, and keep everything else as before.")
CRITERIA = {
    "c1": "The parser must fold long lines at a space character that does not "
          "split a word.",
    "c2": "Folding must occur only where the line length exceeds the limit and a "
          "valid folding point exists.",
    "c3": "The folded output must preserve all original characters except for "
          "the inserted newline at the fold point.",
    "c_1": "The parser must fold long lines at a space where a word is not split, "
           "preserving the original tokenization of parameter values.",
    "c_2": "The parser must not split parameter values at spaces that are part of "
           "an unescaped semicolon or comma delimiter sequence.",
    "c_3": "The parser must fold lines within component definitions without "
           "altering the semantic meaning of parameters.",
}
REMOVAL = "Do not remove that branch in _foldline."
KEEP = "Keep everything else as before."
Q_SPLIT = ("The checks on lines 5, 7, 9 and 12 call q_split, and that is the wrong "
           "function: the fold is _foldline.")
NOT_MINE = "Lines 8, 10 and 11 are not my request."
M42 = (f"{REMOVAL} {KEEP} {Q_SPLIT} {NOT_MINE} I did not ask about parameter values.")
PAGE = ["b1", ITEM, "c1", "c2", "c3", "c_1", "c_2", "c_3", "reading:m5", "reading:m24"]
PER_ITEM = {ITEM: "approve", "c1": "approve", "tst_fold_c1": "approve",
            "c2": "approve", "tst_fold_c2": "contest", "c3": "approve",
            "tst_fold_c3": "contest", "c_1": "contest", "tst_fold_c_1": "contest",
            "c_2": "contest", "c_3": "contest", "tst_fold_c_3": "contest",
            "b1": "approve", "reading:m5": "approve", "reading:m24": "approve"}
# r_m42's rows: (ref, line, verdict, act, words). The reading wrote 15, and
# the landing wrote the 8 that change a row.
_READ = (
    (ITEM, 1, "approve", None, KEEP), ("c1", 2, "approve", None, KEEP),
    ("tst_fold_c1", 3, "approve", None, KEEP), ("c2", 4, "approve", None, KEEP),
    ("tst_fold_c2", 5, "contest", "rewrite", Q_SPLIT),
    ("c3", 6, "approve", None, KEEP),
    ("tst_fold_c3", 7, "contest", "rewrite", Q_SPLIT),
    ("c_1", 8, "contest", "drop", NOT_MINE),
    ("tst_fold_c_1", 9, "contest", "rewrite", Q_SPLIT),
    ("c_2", 10, "contest", "drop", NOT_MINE),
    ("c_3", 11, "contest", "drop", NOT_MINE),
    ("tst_fold_c_3", 12, "contest", "rewrite", Q_SPLIT),
    ("b1", 13, "approve", None, KEEP), ("reading:m5", 14, "approve", None, KEEP),
    ("reading:m24", 15, "approve", None, KEEP),
)
RULED_ROWS = ([(*r, "reading") for r in _READ]
              + [(*r, "landed") for r in _READ if r[0] in (
                  "tst_fold_c1", "tst_fold_c2", "tst_fold_c3", "c_1",
                  "tst_fold_c_1", "c_2", "c_3", "tst_fold_c_3")])
# The `mistake` row of 21bbe661, the Architect's judgement on dry run 7.
NOTE = ("removal: `escaped_prefix = current_chars.pop()` at line 141, "
        "`folded_lines.append(\"\".join(current_chars))` at line 142, "
        "`current_chars = [escaped_prefix]` at line 143 The removal of the code "
        "in _foldline is a mistake because the request and approved criteria do "
        "not ask for this behaviour to be removed.")


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t",
                           "-c", "user.email=t@t", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


def _tree(tmp_path: Path) -> tuple[Path, Path, str]:
    """The base tree as the project root, and b1's worktree at a head that
    removed the escape branch."""
    assert BASE.count(BRANCH) == 1
    root = tmp_path / "wt"
    (root / PATH).parent.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / PATH).write_bytes(BASE.encode("utf-8"))
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    proj = tmp_path / "proj"
    subprocess.run(["git", "clone", "-q", str(root), str(proj)], check=True)
    (root / PATH).write_bytes(BASE.replace(BRANCH, HEAD_BRANCH).encode("utf-8"))
    _git(root, "commit", "-q", "-am", "Fold long lines at a space")
    return proj, root, _git(root, "rev-parse", "HEAD")


def _rule(conn, rid: str, ask: str, reply: str, words: str, per_item: dict,
          rows, refs: list[str]) -> None:
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "seq, status, body_refs) VALUES (?, ?, 'liaison', 'principal', "
                 "'present', ?, 'answered', ?)",
                 (ask, ask, int(ask[1:]), json.dumps(refs)))
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "seq, status, cause_id, body_refs, body_text) VALUES (?, ?, "
                 "'principal', 'liaison', 'converse', ?, 'answered', ?, ?, ?)",
                 (reply, ask, int(reply[1:]), ask, json.dumps(refs), words))
    conn.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, "
                 "status) VALUES (?, ?, ?, ?, ?, 'landed')",
                 (rid, ask, reply, json.dumps(per_item), words))
    for n, (ref, line, verdict, act, said, source) in enumerate(rows):
        conn.execute("INSERT INTO ruled_refs (id, ruling_id, ref, line, verdict, "
                     "act, words, source) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                     (f"rr_{rid}_{n}", rid, ref, line, verdict, act, said, source))


def _dry7(tmp_path: Path, *, ruled: bool = True):
    """b1 at its head with the `mistake` row, and r_m42 landed when `ruled`."""
    proj, root, head = _tree(tmp_path)
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)",
                 (str(proj),))
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES (?, ?, 'in_scope', 'approved', 1, 1)",
                 (ITEM, ITEM_TEXT))
    conn.execute("INSERT INTO tickets (id, item_id, text, item_ver) VALUES "
                 "('tk_1', ?, ?, 1)", (ITEM, ITEM_TEXT))
    for cid, text in CRITERIA.items():
        conn.execute("INSERT INTO criteria (id, ticket_id, text, version) VALUES "
                     "(?, 'tk_1', ?, 1)", (cid, text))
    conn.execute("INSERT INTO batches (id, item_id, status, worktree, "
                 "head_commit) VALUES ('b1', ?, 'running', ?, ?)",
                 (ITEM, str(root), head))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('b1', 'tk_1')")
    conn.execute("INSERT INTO touch_strays (batch_id, commit_sha, path, status, "
                 "note) VALUES ('b1', ?, ?, 'mistake', ?)", (head, GRAIN, NOTE))
    if ruled:
        _rule(conn, "r_m42", "m29", "m42", M42, PER_ITEM, RULED_ROWS, PAGE)
    conn.commit()
    return conn


def _prompt(conn, wake: Wake) -> tuple[dict, str]:
    """The pushed blocks and the user prompt, composed as `run_session`
    composes them."""
    sb = session_sandbox(conn, wake, batch_id=_batch_of(conn, wake))
    pushed = push_working_set(wake.role, sb, wake)
    _, user = build_prompt(wake.role, sb, wake, pushed, "",
                           resolve_inbound(conn, wake))
    return pushed, user


# Fix 1: his whole reply reaches the fix wake and the stray judgement.

def test_the_restore_wake_holds_his_words_on_the_removal(tmp_path):
    """Red at 70e8e9b2: the block fired on `tick:batch_start` only, and
    s191's restore wake held no word of m42."""
    conn = _dry7(tmp_path)
    [wake] = P.touch_mistaken(conn)
    pushed, user = _prompt(conn, wake)
    assert list(pushed)[0] == START_RULED_KEY
    assert REMOVAL in pushed[START_RULED_KEY]
    assert f'His answer m42 to page m29: "{M42}"' in user
    # At the front, so the cut of a long wake takes it last.
    assert user.index(REMOVAL) < user.index("[code.diff]")


def test_the_stray_judgement_holds_his_words_on_the_removal(tmp_path):
    """s190, s192, s205 and s208 judged the strays with no word of m42."""
    conn = _dry7(tmp_path)
    wake = Wake("architect", "tick:touch_strayed", refs=("b1",))
    pushed, user = _prompt(conn, wake)
    assert list(pushed)[0] == START_RULED_KEY
    assert REMOVAL in user


def test_every_developer_wake_on_the_batch_holds_the_same_block(tmp_path):
    """10 of 10 Developer modes. The block is one block in every mode."""
    conn = _dry7(tmp_path)
    blocks = set()
    for kind in ("batch_start", "tests_failing", "touch_mistaken", "exhausted",
                 "finding_violated", "findings_exhausted", "reopen",
                 "verdict_failed"):
        wake = Wake("developer", f"tick:{kind}", refs=("b1",))
        sb = session_sandbox(conn, wake, batch_id="b1")
        blocks.add(push_working_set("developer", sb, wake).get(START_RULED_KEY))
    for detail in ("answer", "challenge"):
        wake = Wake("developer", "message", refs=("m1",), detail=detail)
        sb = session_sandbox(conn, wake, batch_id="b1")
        blocks.add(push_working_set("developer", sb, wake).get(START_RULED_KEY))
    [block] = blocks
    assert block and REMOVAL in block


# Fix 1, the guard.

def test_a_batch_with_no_ruling_of_his_carries_no_block(tmp_path):
    conn = _dry7(tmp_path, ruled=False)
    [wake] = P.touch_mistaken(conn)
    pushed, user = _prompt(conn, wake)
    assert START_RULED_KEY not in pushed
    assert "His answer" not in user


def test_a_ruling_on_another_batch_does_not_appear(tmp_path):
    conn = _dry7(tmp_path, ruled=False)
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('other_item', 'Another request.', "
                 "'in_scope', 'approved', 1, 1)")
    conn.execute("INSERT INTO tickets (id, item_id, text, item_ver) VALUES "
                 "('tk_2', 'other_item', 'Another request.', 1)")
    conn.execute("INSERT INTO criteria (id, ticket_id, text, version) VALUES "
                 "('c9', 'tk_2', 'Another criterion.', 1)")
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES "
                 "('b2', 'other_item', 'running')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('b2', 'tk_2')")
    words = "Do not touch the other module."
    _rule(conn, "r_m50", "m49", "m50", words,
          {"b2": "approve", "c9": "approve"},
          [("b2", 1, "approve", None, words, "reading"),
           ("c9", 2, "approve", None, words, "reading")], ["b2", "c9"])
    conn.commit()
    [wake] = P.touch_mistaken(conn)
    pushed, user = _prompt(conn, wake)
    assert START_RULED_KEY not in pushed
    assert words not in user
