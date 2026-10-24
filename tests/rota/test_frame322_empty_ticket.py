"""Frame 322: the criteria wake and the exact-twin refusal name the empty ticket.

Night 163, item `clear()`: the Terminologist s199 wrote three criteria on
tk_1 and none on tk_2. The wake named the item only, and the twin refusal
said to write "a second sentence". Three attempts wrote invented cases on
tk_1, and the third inverted tk_2's headline (`plans/night163-w7w8-read.md`
section 1). The state below is s199's after its turn 2, read from the
night's database.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from rota.core.db import SCHEMA_KEY, SCHEMA_MARK, init_db
from rota.core.runner import build_prompt, push_working_set
from rota.core.sandbox import build
from rota.core.scheduler import Wake, tick_criteria
from rota.roles import prompts
from rota.testkit.fixtures import seed_ref

NIGHT = Path(__file__).resolve().parents[2] / ".rota" / "clickI_night163.db"
if not NIGHT.exists():
    NIGHT = Path("D:/repos/rota/.rota/clickI_night163.db")

ITEM = "clear_returns_bool"
TK1 = "tk_1_clear_returns_bool"
TK2_HEAD = "clear() returns False when stdout is not a terminal"
S199 = ("c1_clear_terminal_check", "c2_non_terminal_false", "c3_terminal_true")
C2 = "clear() returns False when stdout is not a terminal."


@pytest.fixture
def s199(tmp_path):
    if not NIGHT.exists():
        pytest.skip("the night 163 database is not on this machine")
    src = sqlite3.connect(f"file:{NIGHT.as_posix()}?mode=ro", uri=True)
    dst = sqlite3.connect(tmp_path / "rota.db")
    src.backup(dst)
    src.close()
    # The night ran under an older schema mark. The rows this test reads
    # are the same under the current one, and `init_db` adds what is new.
    dst.execute("UPDATE config SET value = ? WHERE key = ?", (SCHEMA_MARK, SCHEMA_KEY))
    dst.commit()
    dst.close()
    conn = init_db(tmp_path / "rota.db")
    marks = ",".join("?" * len(S199))
    later = [r[0] for r in conn.execute(
        f"SELECT id FROM criteria WHERE ticket_id IN (?, 'tk_2') "
        f"AND id NOT IN ({marks})", (TK1, *S199))]
    for cid in later:
        conn.execute("DELETE FROM refs WHERE src_table = 'criteria' AND src_id = ?", (cid,))
        conn.execute("DELETE FROM criteria WHERE id = ?", (cid,))
    conn.commit()
    return conn


def _wake(conn):
    return next(w for w in tick_criteria(conn) if w.refs == (ITEM,))


def _seat(conn):
    return build("terminologist", conn, mode="criteria",
                 allow=prompts.mode_tools("terminologist", "criteria"))


def test_s199_wake_names_tk_2_and_its_headline_first(s199):
    detail = _wake(s199).detail
    assert detail.startswith(f"No criterion yet: tk_2 ({TK2_HEAD})."), detail
    assert f"Covered: {TK1}" in detail
    assert _wake(s199).refs == (ITEM,)


def test_s199_wake_detail_reaches_the_prompt(s199):
    wake = _wake(s199)
    sb = _seat(s199)
    _, user = build_prompt("terminologist", sb, wake, {}, "")
    assert f"No criterion yet: tk_2 ({TK2_HEAD})." in user


def test_s199_twin_refusal_of_c2_names_tk_2(s199):
    with pytest.raises(Exception) as err:
        _seat(s199).call("criteria.specify", id="c2_non_terminal_false_again",
                         ticket_id=TK1, text=C2, term_refs=[],
                         surface_refs=["examples/termui/termui.py::clear"])
    said = str(err.value)
    assert "c2_non_terminal_false's words already" in said, said
    assert f"tk_2, {TK2_HEAD}, has no criterion yet" in said, said
    assert "second sentence" not in said


def test_the_push_shows_every_ratified_statement_of_the_items_entries(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    words = "Make f() return 1. Keep its output as it is."
    conn.execute("INSERT INTO entries (id, author, ts_order, text) "
                 "VALUES ('e1', 'principal', 1, ?)", (words,))
    for sid, start, end, status in (("s1", 0, 18, "ratified"), ("s2", 19, 44, "ratified"),
                                    ("s3", 19, 44, "superseded")):
        conn.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, "
                     "status) VALUES (?, 'e1', ?, ?, ?, ?)",
                     (sid, start, end, words[start:end] + (" old" if sid == "s3" else ""),
                      status))
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
                 "VALUES ('f_one', 'f() returns 1', 'in_scope', 'approved', 1, 1)")
    seed_ref(conn, "items", "f_one", "statement", "s1")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk_1', 'f_one', 'f() returns 1')")
    conn.commit()
    pushed = push_working_set("terminologist", _seat(conn),
                              Wake("terminologist", "tick:criteria", refs=("f_one",)))
    assert pushed["the item"]["the principal said"] == [
        "Make f() return 1.", "Keep its output as it is."]


@pytest.fixture
def covered(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
                 "VALUES ('f_one', 'f() returns 1', 'in_scope', 'approved', 1, 1)")
    for tid, head in (("tk_1", "f() returns 1"), ("tk_2", "f() prints nothing")):
        conn.execute("INSERT INTO tickets (id, item_id, text) VALUES (?, 'f_one', ?)",
                     (tid, head))
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('c1', 'tk_1', 'f() returns 1.'), ('c2', 'tk_2', 'f() prints nothing.')")
    conn.commit()
    return conn


def test_every_ticket_covered_no_wake_and_old_twin_text(covered):
    assert tick_criteria(covered) == []
    with pytest.raises(Exception) as err:
        _seat(covered).call("criteria.specify", id="c3", ticket_id="tk_1",
                            text="f() returns 1.", term_refs=[], surface_refs=[])
    said = str(err.value)
    assert said.endswith("those are c1's words already, on the same ticket. The "
                         "same words are the same criterion; if the ticket needs a "
                         "second criterion, it needs a second sentence"), said
