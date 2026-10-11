"""
Frame 204, pass 1: the build session discharges a seat's fault reports.

`rota.tools.faults close` closes every open row of one refused call and
writes the build frame's number in `closed_by` (design, section 7). A seat
never closes a fault, and the principal is never asked to.
"""
from __future__ import annotations

from rota.core.db import init_db
from rota.tools import faults


def _run(tmp_path):
    path = tmp_path / "run.db"
    conn = init_db(path)
    rows = (("f_1", "glossary.adopt", "open"), ("f_2", "glossary.adopt", "open"),
            ("f_3", "model.adopt", "open"), ("f_4", "glossary.adopt", "resolved"))
    for seq, (fid, call, status) in enumerate(rows, start=1):
        conn.execute("INSERT INTO faults (id, call, text, author, seq, status, closed_by) "
                     "VALUES (?, ?, 'the door refused a ruled row', 'terminologist', ?, ?, ?)",
                     (fid, call, seq, status, "197" if status == "resolved" else None))
    conn.close()
    return path


def test_close_closes_the_rows_of_one_call_and_writes_the_frame(tmp_path, capsys):
    path = _run(tmp_path)
    assert faults.main(["close", "--db", str(path), "--call", "glossary.adopt",
                        "--frame", "204"]) == 0
    assert capsys.readouterr().out.strip() == (
        "closed 2 open faults of glossary.adopt by frame 204")
    conn = init_db(path)
    got = {r["id"]: (r["status"], r["closed_by"]) for r in conn.execute(
        "SELECT id, status, closed_by FROM faults")}
    conn.close()
    assert got == {"f_1": ("resolved", "204"), "f_2": ("resolved", "204"),
                   "f_3": ("open", None), "f_4": ("resolved", "197")}


def test_list_counts_the_open_faults_per_call(tmp_path, capsys):
    path = _run(tmp_path)
    assert faults.main(["list", "--db", str(path)]) == 0
    assert capsys.readouterr().out.splitlines() == ["glossary.adopt 2", "model.adopt 1"]
