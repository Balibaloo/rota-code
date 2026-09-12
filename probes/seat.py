"""
The seat as an exchange: a run that waits for a person at every page.

    python probes/seat.py <run> "<first sentence>" <exchange dir> [max_steps]

The run steps in the background. Each page the Liaison puts to the
principal is written whole to `<dir>/page_NNN.md` and printed; the driver
then waits for `<dir>/reply_NNN.txt` and lands its text through the same
door the TUI uses (`principal.land`, via `pump`). A Liaison sentence with
no page under it is written the same way and answered the same way. The
whole exchange, pages and replies in order, is `<dir>/exchange.md`.

Replies may be prepared ahead: a file `<dir>/replies.txt`, one reply per
line, is consumed in order before the driver waits on the reply files.
That makes a scripted exchange repeatable and a live one possible.

Stops at merge, at quiet, or at the step cap, and prints the run's state.
"""
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
os.environ.setdefault("ROTA_ONESHOT", "")

from rota.core.db import connect
from rota.core.loop import step
from rota.llm.llm import Pins
from rota.roles.principal import Answer, pending_asks, pending_replies, pump, render_state

run, first, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
cap = int(sys.argv[4]) if len(sys.argv) > 4 else 400
out.mkdir(parents=True, exist_ok=True)
conn = connect(REPO / ".rota" / f"{run}.db")

last = conn.execute("SELECT text FROM entries WHERE author = 'principal' "
                    "AND id LIKE 'e_p%' ORDER BY ts_order DESC LIMIT 1").fetchone()
if not last or last["text"] != first:
    n = 1 + conn.execute("SELECT COUNT(*) FROM entries WHERE id LIKE 'e_p%'").fetchone()[0]
    seq = 1 + (conn.execute("SELECT MAX(seq) FROM messages").fetchone()[0] or 0)
    ts = 1 + (conn.execute("SELECT MAX(ts_order) FROM entries").fetchone()[0] or 0)
    conn.execute("INSERT INTO entries (id, author, ts_order, text) VALUES (?,'principal',?,?)",
                 (f"e_p{n}", ts, first))
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "body_refs, seq) VALUES (?,'t_p1','principal','liaison','converse',?,?)",
                 (f"m_p{n}", f'["e_p{n}"]', seq))
    conn.commit()
merged_before = conn.execute("SELECT COUNT(*) FROM batches WHERE status = 'merged'").fetchone()[0]

scripted = []
if (out / "replies.txt").is_file():
    scripted = [ln.rstrip("\n") for ln in (out / "replies.txt").read_text(encoding="utf-8").splitlines()
                if ln.strip()]
log = out / "exchange.md"
log.write_text(f"# {run}: {first}\n\n", encoding="utf-8")
page_no = 0
replied: set = set()


def _log(text: str) -> None:
    with log.open("a", encoding="utf-8") as fh:
        fh.write(text + "\n")


def reply_to(page_text: str, head: str) -> str:
    """Write the page, then take the next reply: scripted, or from a file a
    person writes beside it."""
    global page_no
    page_no += 1
    (out / f"page_{page_no:03d}.md").write_text(page_text + "\n", encoding="utf-8")
    print(f"\n===== page {page_no} =====\n{page_text}\n", flush=True)
    _log(f"## page {page_no}\n\n{page_text}\n")
    if scripted:
        said = scripted.pop(0)
    else:
        want = out / f"reply_{page_no:03d}.txt"
        print(f"(waiting for {want.name})", flush=True)
        while not want.is_file():
            time.sleep(2)
        said = want.read_text(encoding="utf-8").strip()
    print(f"----- reply {page_no}: {said}\n", flush=True)
    _log(f"**reply {page_no}:** {said}\n")
    return said


class Principal:
    name = "seat"

    def respond(self, ask):
        if ask.message_id in replied:
            return None
        replied.add(ask.message_id)
        head = ask.rendered.splitlines()[0] if ask.rendered else ask.verb
        said = reply_to(ask.rendered or f"[{ask.verb}] {ask.refs}", head)
        if ask.verb == "clarify":
            return Answer(verb="converse", text=said)
        return Answer(verb="reply", text=said)


from rota.llm import profile as profile_mod
_prof = profile_mod.of_run(conn)
if _prof is not None:
    pins, backend = _prof.pins_for(None), _prof.backend()
else:
    pins, backend = Pins(model="qwen3:8b", temperature=0.0), None


def record(merged: int, steps: int, pages: int, note: str) -> None:
    import datetime, json as _json
    row = {"run": run, "profile": _prof.name if _prof is not None else "none",
           "repository": str(conn.execute("SELECT value FROM config WHERE key='project_root'").fetchone()[0]),
           "merged": merged, "steps": steps, "asks": pages, "note": f"seat: {note}"[:120],
           "oneshot": bool(os.environ.get("ROTA_ONESHOT")),
           "date": datetime.date.today().isoformat()}
    with open(REPO / "tests" / "rota" / "walks.jsonl", "a", encoding="utf-8") as fh:
        fh.write(_json.dumps(row) + chr(10))


for i in range(cap):
    if [a for a in pending_asks(conn) if a.message_id not in replied]:
        pump(conn, Principal())
        conn.commit()
        continue
    for rep in pending_replies(conn):
        if rep.message_id in replied:
            continue
        replied.add(rep.message_id)
        said = reply_to(rep.rendered or "", "liaison said")
        conn.execute("UPDATE messages SET status = 'answered' WHERE id = ?", (rep.message_id,))
        n = 1 + conn.execute("SELECT COUNT(*) FROM entries WHERE id LIKE 'e_p%'").fetchone()[0]
        seq = 1 + (conn.execute("SELECT MAX(seq) FROM messages").fetchone()[0] or 0)
        ts = 1 + (conn.execute("SELECT MAX(ts_order) FROM entries").fetchone()[0] or 0)
        conn.execute("INSERT INTO entries (id, author, ts_order, text) VALUES (?,'principal',?,?)",
                     (f"e_p{n}", ts, said))
        conn.execute("INSERT INTO messages (id, cause_id, cause_kind, thread_id, from_role, to_role, verb, "
                     "body_refs, seq) VALUES (?,?,'message','t_p1','principal','liaison','converse',?,?)",
                     (f"m_p{n}", rep.message_id, f'["e_p{n}"]', seq))
        conn.commit()
    s = step(conn, pins=pins, backend=backend)
    if s is None or s.wake is None:
        print(f"quiet after {i} steps, {page_no} pages", flush=True)
        _log(f"\n_quiet after {i} steps, {page_no} pages_\n")
        record(0, i, page_no, "quiet")
        break
    if s.wake.kind in ("do:harness", "do:merge"):
        print(f"  {s.wake.kind}: {s.note}", flush=True)
        _log(f"_{s.wake.kind}: {s.note}_\n")
    merged_now = conn.execute("SELECT COUNT(*) FROM batches WHERE status = 'merged'").fetchone()[0]
    if merged_now > merged_before and os.environ.get("WALK_STOP_AT_MERGE", "1") == "1":
        print(f"MERGED ({merged_now} total) after {i} steps, {page_no} pages", flush=True)
        _log(f"\n_MERGED after {i} steps, {page_no} pages_\n")
        record(1, i, page_no, "merged")
        break
else:
    print(f"step cap {cap}, {page_no} pages", flush=True)
    record(0, cap, page_no, "step cap")
conn.commit()
print("---")
print(render_state(conn))
_log("\n```\n" + render_state(conn) + "\n```\n")
