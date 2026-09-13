"""
One walk, one call, little output.

    python walk.py <run> "<first message>" ["<answer to any clarify>"] [max_steps]

Approves every confirm and present. Answers every clarify with the given
sentence. Stops at merge, at quiet, or at the step cap. Prints each ask's first
line, the harness lines, and the run's state at the end.
"""
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
os.environ.setdefault("ROTA_ONESHOT", "1")

from rota.core.db import connect
from rota.core.loop import step
from rota.llm.llm import Pins
from rota.roles.principal import Answer, pending_asks, pump, render_state

run, first = sys.argv[1], sys.argv[2]
answer = sys.argv[3] if len(sys.argv) > 3 else "yes to all of it. keep it simple."
cap = int(sys.argv[4]) if len(sys.argv) > 4 else 250
conn = connect(REPO / ".rota" / f"{run}.db")

last = conn.execute("SELECT text FROM entries WHERE author = 'principal' "
                    "AND id LIKE 'e_p%' ORDER BY ts_order DESC LIMIT 1").fetchone()
if not last or last["text"] != first:
    # A new sentence into a run that may already have merged: the next
    # principal entry and message, in the same thread, after every seq so far.
    n = 1 + conn.execute("SELECT COUNT(*) FROM entries WHERE id LIKE 'e_p%'").fetchone()[0]
    seq = 1 + (conn.execute("SELECT MAX(seq) FROM messages").fetchone()[0] or 0)
    ts = 1 + (conn.execute("SELECT MAX(ts_order) FROM entries").fetchone()[0] or 0)
    conn.execute("INSERT INTO entries (id, author, ts_order, text) VALUES (?,'principal',?,?)",
                 (f"e_p{n}", ts, first))
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "body_refs, seq) VALUES (?,'t_p1','principal','liaison','converse',?,?)",
                 (f"m_p{n}", f'["e_p{n}"]', seq))
    conn.commit()
merged_before = conn.execute(
    "SELECT COUNT(*) FROM batches WHERE status = 'merged'").fetchone()[0]


WORDS = os.environ.get("WALK_WORDS", "")   # reply in words; the Liaison lands it
# A principal by moment: "regex::words" contests the first numbered page
# line that matches, in words, and approves the rest.
import re as _re
CONTEST = os.environ.get("WALK_CONTEST", "")
C_RE, _, C_WORDS = CONTEST.partition("::")
# Only pages matching this regex are contested; empty means every page.
PAGE_RE = os.environ.get("WALK_CONTEST_PAGE", "")
replied: set = set()


contested_once = False


def reply_for(rendered: str) -> str:
    # One contest a walk: a principal says the correction once, and the
    # page that comes back after it is read as answered (tipsAU, 2026-09-12:
    # the same touch note contested twenty times).
    global contested_once
    if C_RE and not contested_once and (not PAGE_RE or _re.search(PAGE_RE, rendered or "", _re.I)):
        for line in (rendered or "").splitlines():
            m = _re.match(r"\s*(\d+)\.\s+(.*)", line)
            if m and _re.search(C_RE, m.group(2), _re.I):
                contested_once = True
                return f"{m.group(1)} is wrong: {C_WORDS}"
    return WORDS


class Principal:
    name = "walk"

    def respond(self, ask):
        head = ask.rendered.splitlines()[0] if ask.rendered else ask.verb
        if ask.verb in ("confirm", "present"):
            if WORDS:
                if ask.message_id in replied:
                    return None
                replied.add(ask.message_id)
                said = reply_for(ask.rendered)
                if os.environ.get("WALK_FULL"):
                    # The whole page, then the reply: a chat log a person judges.
                    print(chr(10) + f"===== [{ask.message_id}] {ask.verb} =====" + chr(10)
                          + (ask.rendered or "") + chr(10) + f"----- reply: {said}" + chr(10))
                else:
                    print(f"[{ask.message_id}] {ask.verb}: {head[:90]}  -> '{said}'")
                return Answer(verb="reply", text=said)
            print(f"[{ask.message_id}] {ask.verb}: {head[:90]}  -> ok")
            return Answer(verb="verdict", per_item={r: "approve" for r in ask.refs})
        q = ask.rendered.splitlines()[1].strip() if ask.rendered else ""
        print(f"[{ask.message_id}] clarify: {q[:110]}  -> {answer[:50]}")
        return Answer(verb="converse", text=answer)


# The run's frozen profile, when the run was onboarded with one; the old
# hard-coded model otherwise.
from rota.llm import profile as profile_mod
_prof = profile_mod.of_run(conn)
if _prof is not None:
    pins, backend = _prof.pins_for(None), _prof.backend()
    print(f"profile {_prof.name}: default {_prof.default_model}; roles {_prof.routing()}")
else:
    pins, backend = Pins(model="qwen3:8b", temperature=0.0), None
def record(merged: int, steps: int, asks: int, note: str) -> None:
    """The walk's own result row (plans/model-setup.md, step 1)."""
    import datetime, json as _json
    row = {"run": run, "profile": _prof.name if _prof is not None else "none",
           "repository": str(conn.execute("SELECT value FROM config WHERE key='project_root'").fetchone()[0]),
           "merged": merged, "steps": steps, "asks": asks, "note": note[:120],
           "oneshot": bool(os.environ.get("ROTA_ONESHOT")),
           "date": datetime.date.today().isoformat()}
    with open(REPO / "tests" / "rota" / "walks.jsonl", "a", encoding="utf-8") as fh:
        fh.write(_json.dumps(row) + chr(10))


asked = 0
import time as _time
_last_n, _last_change = -1, _time.time()
for i in range(cap):
    # A walk that writes no committed session for thirty minutes is stalled,
    # whatever the card is doing. Night 31 (2026-09-13) ran 98 minutes on
    # one failing wake with nothing in the log. Thirty, because one honest
    # session on the slow card can run twenty.
    _n = conn.execute("SELECT COUNT(*) FROM sessions WHERE committed = 1").fetchone()[0]
    if _n != _last_n:
        _last_n, _last_change = _n, _time.time()
    elif _time.time() - _last_change > 1800:
        print(f"STALLED: no committed session in 30 min after {i} steps", flush=True)
        record(0, i, asked, "stalled")
        break
    if [a for a in pending_asks(conn) if a.message_id not in replied]:
        pump(conn, Principal())
        conn.commit()
        asked += 1
        continue
    # A Liaison sentence back with no page under it is a chat turn a person
    # would answer. Answer it once with the clarify sentence, as a new turn.
    from rota.roles.principal import pending_replies
    for rep in pending_replies(conn):
        if rep.message_id in replied:
            continue
        replied.add(rep.message_id)
        print(f"[{rep.message_id}] liaison said: {(rep.rendered or '')[:100]}  -> {answer[:50]}")
        conn.execute("UPDATE messages SET status = 'answered' WHERE id = ?", (rep.message_id,))
        n = 1 + conn.execute("SELECT COUNT(*) FROM entries WHERE id LIKE 'e_p%'").fetchone()[0]
        seq = 1 + (conn.execute("SELECT MAX(seq) FROM messages").fetchone()[0] or 0)
        ts = 1 + (conn.execute("SELECT MAX(ts_order) FROM entries").fetchone()[0] or 0)
        conn.execute("INSERT INTO entries (id, author, ts_order, text) VALUES (?,'principal',?,?)",
                     (f"e_p{n}", ts, answer))
        conn.execute("INSERT INTO messages (id, cause_id, cause_kind, thread_id, from_role, to_role, verb, "
                     "body_refs, seq) VALUES (?,?,'message','t_p1','principal','liaison','converse',?,?)",
                     (f"m_p{n}", rep.message_id, f'["e_p{n}"]', seq))
        conn.commit()
    s = step(conn, pins=pins, backend=backend)
    if s is not None and s.outcome is not None and not s.outcome.committed:
        # Said at once and flushed: night 31 ran 98 minutes on one failing
        # wake and the log held nothing, because the failure was silent and
        # stdout was block-buffered into a file.
        print(f"FAILED {s.wake}: {(s.outcome.errors or ['?'])[-1][:200]}", flush=True)
    if s is None or s.wake is None:
        print(f"quiet after {i} steps, {asked} asks")
        record(0, i, asked, "quiet")
        break
    if s.wake.kind in ("do:harness", "do:merge"):
        print(f"  {s.wake.kind}: {s.note}")
    merged_now = conn.execute(
        "SELECT COUNT(*) FROM batches WHERE status = 'merged'").fetchone()[0]
    if merged_now > merged_before and os.environ.get("WALK_STOP_AT_MERGE", "1") == "1":
        print(f"MERGED ({merged_now} total) after {i} steps, {asked} asks")
        record(1, i, asked, "merged")
        break
else:
    print(f"step cap {cap}, {asked} asks")
conn.commit()
print("---")
print(render_state(conn))
