"""
The rows a night's read asks for, as plain text.

    python -m rota.tools.nightreport <path to a run database> [--since <UTC time>] [--full]

The build session read every night's run database on an agent, and each
read cost 85k to 103k tokens to answer the same questions (observed: frame
105's brief, 2026-10-01). The answers are rows, so this tool prints them.
The read then becomes a summary over facts.

The tool is read-only. It opens the file with `mode=ro` and never calls
`init_db`, because `init_db` refuses a database on an old schema mark, and
the report must open old nights. A section that reads an absent table or
column prints `absent: <table>` or `absent: <table>.<column>` under its
header, and an absent column's value prints as `?`. A zero from an absent
table read as a fact on the frame 105 diff review (2026-10-01).

The tool prints facts only. It names no stall and no cause.

`turns.user` holds the whole assembled prompt, so one feedback line
persists into every later turn of the session (`rota/tools/nightcount.py`).
A window cut also drops old copies, so a count that compares two prompts
misses a new copy (frame 105 diff review, s88 and s132 of night 101). A
turn holds a phrase when the newest feedback or the completion holds it.
The newest feedback is the part of the prompt after the previous turn's
completion. The model's own completion can quote a runner phrase, so the
newest feedback never includes that completion.

`--since` filters `finding_rulings.at` only. No other reported table
stores a time: `sessions`, `turns` and `messages` order by `seq` alone.

A wake run of one role and one wake kind, outside a batch, all committed
and contiguous in `seq`, prints as one line. The 39 reconcile ticks of
night 101 made the report too long to read otherwise. `--full` prints one
line per session.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from collections import Counter, OrderedDict
from pathlib import Path

PHRASES = (
    "CUT the result",
    "dropped to fit the window",
    "served three times this session",
    "not served again",
    "already holds this text",
    "named an act and did not perform it",
    "Your work for this session is complete",
)
COMPLETE = "Your work for this session is complete"
# `code.code_commit` writes the sha to `batches.head_commit` only, and a
# later commit overwrites it. The runner's feedback line keeps each sha.
COMMIT_RE = re.compile(r'OK code\.commit -> \{"committed": true, "head_commit": "([0-9a-f]{7,40})"')
# `db.session_fail` and `db.session_note` add a turn that the model never ran.
RUNNER_PREFIXES = ("SESSION FAILED", "SESSION ENDED")
SHA = 10
WAKE_WIDTH = 120
# The value of a column that the database lacks.
ABSENT = "?"
# A prompt can hold a long completion cut short. The search then uses the
# completion's start.
HEAD_PROBE = 60


def cut(text, n: int) -> str:
    """One line, at most `n` characters. The report cuts text and never wraps it."""
    s = " ".join(str("" if text is None else text).split())
    return s if len(s) <= n else s[: n - 3] + "..."


def short(sha) -> str:
    if sha == ABSENT:
        return ABSENT
    return (sha or "-")[:SHA]


def open_ro(path: str | Path) -> sqlite3.Connection:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"no run database at {p}")
    conn = sqlite3.connect(f"file:{p.resolve().as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


class Night:
    """The run database. An absent column reads as `?`, and an absent table as no rows."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.columns: dict[str, set[str]] = {}
        for (name,) in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'"):
            self.columns[name] = {r[1] for r in conn.execute(f"PRAGMA table_info({name})")}

    def has(self, table: str, column: str | None = None) -> bool:
        if table not in self.columns:
            return False
        return column is None or column in self.columns[table]

    def absent(self, table: str, cols: tuple[str, ...]) -> list[str]:
        """The `absent:` lines for a read of `cols` from `table`."""
        if not self.has(table):
            return [f"absent: {table}"]
        return [f"absent: {table}.{c}" for c in cols if c not in self.columns[table]]

    def rows(self, table: str, cols: tuple[str, ...], order: tuple[str, ...] = ()) -> list[dict]:
        if not self.has(table):
            return []
        have = self.columns[table]
        sel = ", ".join(c if c in have else f"'{ABSENT}' AS {c}" for c in cols)
        keys = [c for c in order if c in have] or ["rowid"]
        sql = f"SELECT {sel} FROM {table} ORDER BY {', '.join(keys)}"
        return [dict(r) for r in self.conn.execute(sql)]


def _refs(text) -> list[str]:
    try:
        val = json.loads(text or "[]")
    except (TypeError, ValueError):
        return []
    return [str(v) for v in val] if isinstance(val, list) else []


def _names_batch(refs: list[str], batch_ids: set[str]) -> str | None:
    """The batch a ref list names. A verdict id `critic:<batch>:<sha>` names its batch."""
    for ref in refs:
        if ref in batch_ids:
            return ref
        for part in ref.split(":"):
            if part in batch_ids:
                return part
    return None


def _newest_feedback(user: str, prev_completion: str | None) -> tuple[str, bool]:
    """
    The part of a prompt that follows the previous turn's completion.

    The second value is False when the prompt holds no copy of that
    completion, even cut short. The whole prompt is then the feedback.
    """
    if prev_completion is None:
        return user, True
    if not prev_completion:
        return user, False
    i = user.rfind(prev_completion)
    if i >= 0:
        return user[i + len(prev_completion):], True
    i = user.rfind(prev_completion[:HEAD_PROBE])
    if i < 0:
        return user, False
    k = 0
    while k < len(prev_completion) and i + k < len(user) and prev_completion[k] == user[i + k]:
        k += 1
    return user[i + k:], True


def _is_runner(turn: dict) -> bool:
    return str(turn["completion"] or "").startswith(RUNNER_PREFIXES)


def build(conn: sqlite3.Connection, since: str | None = None, full: bool = False) -> list[str]:
    n = Night(conn)
    out: list[str] = []
    w = out.append

    S_COLS = ("id", "role", "trigger_msg", "committed", "seq", "wake_kind", "wake_detail",
              "wake_refs")
    T_COLS = ("session_id", "seq", "user", "completion")
    C_COLS = ("session_id", "fn", "args_summary", "seq")
    M_COLS = ("id", "from_role", "to_role", "verb", "body_refs", "body_text",
              "unresolved_note", "status", "seq")
    B_COLS = ("id", "item_id", "head_commit", "status")
    R_COLS = ("session_id", "table_name", "row_id")

    sessions = n.rows("sessions", S_COLS, ("seq",))
    have_turns = n.has("turns")
    turns_by: dict[str, list[dict]] = {}
    for t in n.rows("turns", T_COLS, ("session_id", "seq")):
        turns_by.setdefault(t["session_id"], []).append(t)
    calls_by: dict[str, list[dict]] = {}
    for c in n.rows("tool_calls", C_COLS, ("session_id", "seq")):
        calls_by.setdefault(c["session_id"], []).append(c)
    messages = n.rows("messages", M_COLS, ("seq",))
    msg_by = {m["id"]: m for m in messages}
    items = {r["id"]: r for r in n.rows("items", ("id", "text"))}
    batches = n.rows("batches", B_COLS)
    batch_ids = {b["id"] for b in batches}
    receipts = n.rows("receipts", R_COLS)
    receipt_sessions: dict[str, list[str]] = {}
    batch_by_receipt: dict[str, str] = {}
    for r in receipts:
        if r["table_name"] == "batches" and r["row_id"] in batch_ids:
            receipt_sessions.setdefault(r["row_id"], []).append(r["session_id"])
            batch_by_receipt.setdefault(r["session_id"], r["row_id"])
    batch_re = (re.compile(r"(?<![\w])(" + "|".join(map(re.escape, sorted(batch_ids, key=len,
                                                                          reverse=True)))
                           + r")(?![\w])") if batch_ids else None)

    # A session belongs to a batch when one of these names it, in this order:
    # its wake refs, its trigger message's refs, a receipt on the batch row,
    # or the arguments of a tool call. A Developer woken by an answer carries
    # `[]` as wake refs. s150 of night 101 committed to bg_1 through a receipt,
    # and s144 named bg_1 in `tests.encode` (frame 105 diff review).
    batch_of: dict[str, str | None] = {}
    for s in sessions:
        b = _names_batch(_refs(s["wake_refs"]), batch_ids)
        if b is None and s["trigger_msg"] in msg_by:
            b = _names_batch(_refs(msg_by[s["trigger_msg"]]["body_refs"]), batch_ids)
        if b is None:
            b = batch_by_receipt.get(s["id"])
        if b is None and batch_re is not None:
            for c in calls_by.get(s["id"], []):
                m = batch_re.search(str(c["args_summary"] or ""))
                if m:
                    b = m.group(1)
                    break
        batch_of[s["id"]] = b

    nturns = sum(len(v) for v in turns_by.values()) if have_turns else ABSENT
    w(f"night report: {len(sessions) if n.has('sessions') else ABSENT} sessions, "
      f"{nturns} turns, {len(batches) if n.has('batches') else ABSENT} batches. "
      f"Commits show their first {SHA} characters.")
    if since:
        w(f"--since {since} (UTC) filters finding_rulings.at only.")

    def model_turns(sid: str):
        if not have_turns:
            return ABSENT
        return sum(1 for t in turns_by.get(sid, []) if not _is_runner(t))

    # 1. Batches.
    w("== batches")
    for line in (n.absent("batches", B_COLS) + n.absent("items", ("id", "text"))
                 + n.absent("receipts", R_COLS) + n.absent("turns", T_COLS)):
        w(line)
    seq_of = {s["id"]: s["seq"] for s in sessions}
    committed_of = {s["id"]: s["committed"] for s in sessions}
    for b in batches:
        sids = set(receipt_sessions.get(b["id"], []))
        sids |= {sid for sid, bb in batch_of.items() if bb == b["id"]}
        seen: set[str] = set()
        steps: list[tuple[str, list[str]]] = []
        for sid in sorted(sids, key=lambda x: (seq_of.get(x) if isinstance(seq_of.get(x), int)
                                               else 0, x)):
            shas = []
            for t in turns_by.get(sid, []):
                for text in (str(t["user"] or ""), str(t["completion"] or "")):
                    for sha in COMMIT_RE.findall(text):
                        if sha not in seen:
                            seen.add(sha)
                            shas.append(sha)
            if shas:
                steps.append((sid, shas))
            elif sid in receipt_sessions.get(b["id"], []):
                # The session wrote the batch row, and no commit line shows the sha.
                steps.append((sid, []))
        head = b["head_commit"]
        if head and head != ABSENT and head not in seen:
            steps.append(("(row)", [head]))
        count = sum(len(x) for _, x in steps) if have_turns else ABSENT
        item = items.get(b["item_id"], {}).get("text")
        w(f"{b['id']} status={b['status']} head={short(head)} "
          f"commits={count} item={b['item_id']}: {cut(item, 80)}")
        for sid, shas in steps:
            c = committed_of.get(sid)
            flag = f" committed={c}" if sid != "(row)" and c != 1 else ""
            w(f"  {sid}{flag} " + (" ".join(short(x) for x in shas) or f"sha={ABSENT}"))

    # 2. Wakes, in order.
    w("== wakes")
    for line in (n.absent("sessions", S_COLS) + n.absent("turns", T_COLS)
                 + n.absent("tool_calls", C_COLS)):
        w(line)

    def last_call(sid: str):
        if not n.has("tool_calls"):
            return ABSENT
        cs = calls_by.get(sid, [])
        return f"{cs[-1]['fn']}({cs[-1]['args_summary']})" if cs else "-"

    def wake_line(s: dict) -> str:
        ts = turns_by.get(s["id"], [])
        # An agenda wake names seven ledger rows, and the full list pushed the
        # turn count and the committed flag past the line's cut.
        refs = (ABSENT if s["wake_refs"] == ABSENT
                else cut(",".join(_refs(s["wake_refs"])), 40))
        if s["committed"] == 0:
            if not have_turns:
                tail = f"error={ABSENT}"
            else:
                err = str(ts[-1]["completion"]) if ts else ""
                tail = "error=" + (err[len("SESSION FAILED: "):]
                                   if err.startswith("SESSION FAILED: ") else err)
        else:
            tail = f"last={last_call(s['id'])}"
        head = (f"{s['id']} {s['role']} {s['wake_kind']} [{refs}] "
                f"t={model_turns(s['id'])} c={s['committed']} ")
        return cut(head + tail, WAKE_WIDTH)

    by_batch: "OrderedDict[str, list[dict]]" = OrderedDict((b["id"], []) for b in batches)
    loose: list[dict] = []
    for s in sessions:
        b = batch_of.get(s["id"])
        (by_batch[b] if b else loose).append(s)
    for bid, group in by_batch.items():
        w(f"-- batch {bid}: {len(group)} sessions")
        for s in group:
            w(wake_line(s))
    w(f"-- no batch: {len(loose)} sessions")
    pos_of = {s["id"]: i for i, s in enumerate(sessions)}
    # Without the wake kind, two sessions of one role cannot be told apart.
    can_collapse = not full and n.has("sessions", "wake_kind") and n.has("sessions", "committed")
    i = 0
    while i < len(loose):
        s = loose[i]
        j = i
        if can_collapse and s["committed"] == 1:
            # A run is contiguous in seq, so the range hides no session of
            # another kind (s145..s147 hid s146 on night 100).
            while (j + 1 < len(loose) and loose[j + 1]["committed"] == 1
                   and pos_of[loose[j + 1]["id"]] == pos_of[loose[j]["id"]] + 1
                   and loose[j + 1]["role"] == s["role"]
                   and loose[j + 1]["wake_kind"] == s["wake_kind"]):
                j += 1
        if j == i:
            w(wake_line(s))
        else:
            run = loose[i:j + 1]
            ts = (sum(model_turns(x["id"]) for x in run) if have_turns else ABSENT)
            w(cut(f"{s['id']}..{run[-1]['id']} {s['role']} {s['wake_kind']} x{len(run)} "
                  f"t={ts} c={len(run)} last={last_call(run[-1]['id'])}", WAKE_WIDTH))
        i = j + 1

    # 3. Verdicts.
    w("== verdicts")
    V_COLS = ("id", "batch_id", "commit_sha", "result", "failed_criterion", "reason")
    for line in n.absent("verdicts", V_COLS) + n.absent("batches", ("id", "head_commit")):
        w(line)
    heads = {b["id"]: b["head_commit"] for b in batches}

    def at_head(bid, sha) -> str:
        head = heads.get(bid)
        if sha == ABSENT or head == ABSENT or bid not in heads:
            return ABSENT
        return "head" if sha and sha == head else "old"

    for v in n.rows("verdicts", V_COLS):
        w(f"{cut(v['id'], 40)} batch={v['batch_id']} commit={short(v['commit_sha'])} "
          f"{at_head(v['batch_id'], v['commit_sha'])} "
          f"result={v['result']} failed={v['failed_criterion'] or '-'} "
          f"reason={cut(v['reason'], 100) or '-'}")

    # 4. Test runs.
    w("== test runs")
    TR_COLS = ("batch_id", "commit_sha", "result")
    for line in n.absent("test_runs", TR_COLS):
        w(line)
    tally: "OrderedDict[tuple, list]" = OrderedDict()
    for r in n.rows("test_runs", TR_COLS):
        k = (r["batch_id"], r["commit_sha"])
        tally.setdefault(k, [0, 0])
        tally[k][0] += 1
        if r["result"] == ABSENT:
            tally[k][1] = ABSENT
        elif tally[k][1] != ABSENT:
            tally[k][1] += r["result"] != "pass"
    for (bid, sha), (runs, bad) in tally.items():
        mark = at_head(bid, sha)
        at = " head" if mark == "head" else (f" {ABSENT}" if mark == ABSENT else "")
        w(f"{bid} {short(sha)}{at} runs={runs} not_pass={bad}")

    # 5. Findings and rulings.
    w("== findings and rulings")
    F_COLS = ("id", "batch_id", "constraint_id", "commit_sha", "status", "grain")
    FR_COLS = ("finding_id", "commit_sha", "ruling", "reason", "session_id", "at")
    for line in n.absent("findings", F_COLS) + n.absent("finding_rulings", FR_COLS):
        w(line)
    # `finding_rulings.at` is `datetime('now')`, with a space and no `T`. A
    # `T` sorts after the space and dropped every ruling of the date.
    floor = since.replace("T", " ") if since else None
    rulings: dict[str, list[dict]] = {}
    for r in n.rows("finding_rulings", FR_COLS):
        if floor and r["at"] != ABSENT and str(r["at"] or "").replace("T", " ") < floor:
            continue
        rulings.setdefault(r["finding_id"], []).append(r)
    for f in n.rows("findings", F_COLS):
        base = (f"{f['id']} batch={f['batch_id']} constraint={f['constraint_id']} "
                f"commit={short(f['commit_sha'])} {f['status']} grain={cut(f['grain'], 40)}")
        rs = rulings.get(f["id"], [])
        if not rs:
            w(base + (f" ruling={ABSENT}" if not n.has("finding_rulings") else " ruling=-"))
        for r in rs:
            w(base + f" ruling={r['ruling']} at={r['at']} by={r['session_id'] or '-'} "
                     f"commit={short(r['commit_sha'])} reason={cut(r['reason'], 80)}")

    # 6. Attempts. `clear_dispatch` deletes rows during the run, so the
    # table holds the end state only.
    w("== tick attempts (at the end of the night)")
    A_COLS = ("tick_key", "attempts", "quarantined", "reported")
    for line in n.absent("tick_attempts", A_COLS):
        w(line)
    for a in n.rows("tick_attempts", A_COLS):
        w(f"{cut(a['tick_key'], 80)} attempts={a['attempts']} quarantined={a['quarantined']} "
          f"reported={a['reported']}")

    # 7. Quarantine and deferral.
    w("== quarantine and deferral")
    CP_COLS = ("session_id", "role", "batch_id", "working_set", "valid")
    for line in (n.absent("batches", ("id", "status")) + n.absent("receipts", R_COLS)
                 + n.absent("messages", ("id", "status")) + n.absent("checkpoints", CP_COLS)):
        w(line)
    # The schema stores no time on a batch, so the last session with a
    # receipt on the row is the nearest record of who set the status.
    for b in batches:
        if b["status"] not in ("running", "merged"):
            writers = receipt_sessions.get(b["id"], [])
            last = writers[-1] if writers else ("-" if n.has("receipts") else ABSENT)
            w(f"{b['id']} status={b['status']} last_write={last}")
    for m in messages:
        if m["status"] == "quarantined":
            w(f"message {m['id']} {m['from_role']}->{m['to_role']} {m['verb']} status=quarantined")
    cps = n.rows("checkpoints", CP_COLS)
    w(f"checkpoints: {len(cps) if n.has('checkpoints') else ABSENT}")
    for c in cps:
        w(f"{c['session_id']} {c['role']} batch={c['batch_id'] or '-'} valid={c['valid']} "
          f"working_set={cut(c['working_set'], 60)}")

    # 8. Messages.
    w("== messages")
    for line in n.absent("messages", M_COLS):
        w(line)
    counts = Counter((m["from_role"], m["to_role"], m["verb"]) for m in messages)
    for (fr, to, verb), k in sorted(counts.items(), key=lambda x: tuple(map(str, x[0]))):
        w(f"{fr}->{to} {verb} {k}")
    for m in messages:
        if m["status"] in ("open", "unresolved"):
            text = m["unresolved_note"] or m["body_text"] or m["body_refs"]
            w(f"{m['id']} {m['status']} {m['from_role']}->{m['to_role']} {m['verb']}: {cut(text, 80)}")

    # 9. Window and door phrases.
    w("== window and door phrases (turns, sessions)")
    for line in n.absent("turns", T_COLS):
        w(line)
    holding: dict[str, list[tuple[str, int, bool]]] = {p: [] for p in PHRASES}
    from_first: list[tuple[str, int, int]] = []
    unmatched = 0
    for sid, ts in turns_by.items():
        first_complete = None
        prev_completion: str | None = None
        for t in ts:
            completion = str(t["completion"] or "")
            runner = _is_runner(t)
            if runner:
                # The runner's turn has no prompt. Its completion is the runner's text.
                fresh = ""
            else:
                fresh, matched = _newest_feedback(str(t["user"] or ""), prev_completion)
                unmatched += not matched
            for p in PHRASES:
                if p in fresh or p in completion:
                    holding[p].append((sid, t["seq"], runner))
                    if p == COMPLETE and first_complete is None:
                        first_complete = t["seq"]
            if not runner:
                prev_completion = completion
        if first_complete is not None:
            # The runner puts the line in the feedback, so the turn that first
            # holds it is the model's first reply after it.
            at_or_after = sum(1 for t in ts if t["seq"] >= first_complete and not _is_runner(t))
            if at_or_after:
                from_first.append((sid, first_complete, at_or_after))
    for p in PHRASES:
        if not have_turns:
            w(f"{p!r}: turns={ABSENT} sessions={ABSENT}")
            continue
        hits = holding[p]
        runner_hits = sum(1 for _, _, r in hits if r)
        mark = f" (runner) runner_turns={runner_hits}" if runner_hits else ""
        w(f"{p!r}: turns={len(hits)} sessions={len({s for s, _, _ in hits})}{mark}")
    if have_turns:
        w(f"prompts holding no copy of the previous completion: {unmatched}")
    from_first.sort(key=lambda x: (seq_of.get(x[0]) if isinstance(seq_of.get(x[0]), int)
                                   else 0, x[0]))
    w(f"sessions with model turns at or after the first turn holding {COMPLETE!r}: "
      f"{len(from_first) if have_turns else ABSENT}")
    for sid, first, count in from_first:
        w(f"  {sid} first_turn={first} turns_from={count}")

    # 10. Failures.
    w("== failures")
    for line in n.absent("sessions", ("id", "role", "wake_kind", "committed")) + \
            n.absent("turns", ("session_id", "completion")):
        w(line)
    for s in sessions:
        if s["committed"] == 0:
            ts = turns_by.get(s["id"], [])
            last = (ts[-1]["completion"] if ts else "") if have_turns else ABSENT
            w(f"{s['id']} {s['role']} {s['wake_kind']}: {cut(last, 160)}")
    # A section with no rows says so, so an empty section and a cut report differ.
    filled: list[str] = []
    for i, line in enumerate(out):
        filled.append(line)
        if line.startswith("== ") and (i + 1 == len(out) or out[i + 1].startswith("== ")):
            filled.append("(none)")
    return filled


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m rota.tools.nightreport")
    ap.add_argument("db", help="path to a run database")
    ap.add_argument("--since", help="a UTC time, as `datetime('now')` stores it; a T is read "
                                    "as a space; filters finding_rulings.at only")
    ap.add_argument("--full", action="store_true", help="one line per session, no runs")
    args = ap.parse_args(argv)
    try:
        conn = open_ro(args.db)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        return 2
    try:
        lines = build(conn, args.since, args.full)
    finally:
        conn.close()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
