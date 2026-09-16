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
from rota import paths
conn = connect(paths.RUNS / f"{run}.db")

last = conn.execute("SELECT text FROM entries WHERE author = 'principal' "
                    "AND id LIKE 'e_p%' ORDER BY ts_order DESC LIMIT 1").fetchone()
ONBOARD_ONLY = bool(os.environ.get("WALK_ONBOARD_ONLY"))
import progress as _progress
PHASE = os.environ.get("WALK_PHASE") or ("onboarding" if ONBOARD_ONLY else "sentence ?")
NIGHT = os.environ.get("WALK_NIGHT", "")
_last_page = ""
   # onboarding alone, then the snapshot
if not ONBOARD_ONLY and (not last or last["text"] != first):
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
    global _last_page
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
        global _last_page
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
                    _last_page = f"[{ask.message_id}] {ask.verb}: {head[:90]}  -> '{said}'"
                    print(_last_page)
                return Answer(verb="reply", text=said)
            _last_page = f"[{ask.message_id}] {ask.verb}: {head[:90]}  -> ok"
            print(_last_page)
            return Answer(verb="verdict", per_item={r: "approve" for r in ask.refs})
        # Once per ask. An empty answer lands nothing and the ask stays
        # open (clickI, 2026-09-16: the same clarify pumped seventeen
        # times); a second visit is a deferral.
        if ask.message_id in replied:
            return None
        replied.add(ask.message_id)
        q = ask.rendered.splitlines()[1].strip() if ask.rendered else ""
        _last_page = f"[{ask.message_id}] clarify: {q[:110]}  -> {answer[:50]}"
        print(_last_page)
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
    with open(REPO / "tests" / "rota" / "walks.jsonl", "a", encoding="utf-8", newline="\n") as fh:
        fh.write(_json.dumps(row) + chr(10))


def write_snapshot() -> None:
    """The database as it stands, and its stamp (probes/warm_stamp.py). A
    warm night starts here. In onboard-only mode (WALK_ONBOARD_ONLY=1) no
    sentence has been posted, so the snapshot holds onboarding and nothing
    else and a night can start at any sentence (night 51, 2026-09-14: the
    snapshot taken at the first slicing wake carried sentence one, and
    GAUNTLET_FROM=2 re-ran it)."""
    warm = paths.RUNS / f"{run}_warm.db"
    if conn.execute("SELECT COUNT(*) FROM batches").fetchone()[0] != 0:
        return
    # A cold onboarding is the freshest snapshot there is, so it replaces
    # the one on disk. Nights 60 and 61 (2026-09-14) onboarded cold on new
    # profiles and left the snapshot of 12:14 in place; night 62 started
    # warm from it with the Developer on the wrong model.
    if warm.exists():
        if not ONBOARD_ONLY:
            return
        warm.unlink()
    import sqlite3 as _sq
    conn.commit()
    dst = _sq.connect(str(warm)); conn.backup(dst); dst.close()
    import warm_stamp
    warm_stamp.write(run)
    print(f"warm snapshot written: {warm}", flush=True)


asked = 0
import time as _time
_last_n, _last_change = -1, _time.time()
_n0 = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
_t0 = _time.time()
_outcome = "stalled"
_progress.write(run, PHASE, _n0, _t0, _last_page)
for i in range(cap):
    _progress.write(run, PHASE, _n0, _t0, _last_page)
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
        _last_page = f"[{rep.message_id}] liaison said: {(rep.rendered or '')[:100]}  -> {answer[:50]}"
        print(_last_page)
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
    # The warm snapshot: the database at the first slicing wake, before any
    # batch exists. Onboarding is 119 of a night's first 150 sessions and
    # twenty of its thirty-five minutes (night 46, 2026-09-14); a night that
    # measures the delivery loop starts from here (GAUNTLET_WARM=1).
    if (s is not None and s.wake is not None and s.wake.kind == "tick:slicing"
            and not os.environ.get("WALK_FROM_WARM") and not ONBOARD_ONLY):
        write_snapshot()
    if s is not None and s.outcome is not None and not s.outcome.committed:
        # Said at once and flushed: night 31 ran 98 minutes on one failing
        # wake and the log held nothing, because the failure was silent and
        # stdout was block-buffered into a file.
        print(f"FAILED {s.wake}: {(s.outcome.errors or ['?'])[-1][:200]}", flush=True)
    if s is None or s.wake is None:
        if ONBOARD_ONLY:
            write_snapshot()
            print(f"ONBOARDED after {i} steps, {asked} asks", flush=True)
            _outcome = "onboarded"
            break
        print(f"quiet after {i} steps, {asked} asks")
        _outcome = "stuck"
        record(0, i, asked, "quiet")
        break
    if s.wake.kind in ("do:harness", "do:merge"):
        print(f"  {s.wake.kind}: {s.note}")
    merged_now = conn.execute(
        "SELECT COUNT(*) FROM batches WHERE status = 'merged'").fetchone()[0]
    if merged_now > merged_before and os.environ.get("WALK_STOP_AT_MERGE", "1") == "1":
        print(f"MERGED ({merged_now} total) after {i} steps, {asked} asks")
        _outcome = "merged"
        record(1, i, asked, "merged")
        break
else:
    print(f"step cap {cap}, {asked} asks")
conn.commit()
print("---")
print(render_state(conn))

_progress.write(run, PHASE, _n0, _t0, _last_page)
_progress.finish(run, PHASE, conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0] - _n0,
                 (_time.time() - _t0) / 60, _outcome, NIGHT)
