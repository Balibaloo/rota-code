"""
The rows a night's read asks for, as plain text.

    python -m rota.tools.nightreport <path to a run database> [--since <iso time>] [--full]

The build session read every night's run database on an agent, and each
read cost 85k to 103k tokens to answer the same questions (observed: frame
105's brief, 2026-10-01). The answers are rows, so this tool prints them.
The read then becomes a summary over facts.

The tool is read-only. It opens the file with `mode=ro` and never calls
`init_db`, because `init_db` refuses a database on an old schema mark, and
the report must open old nights. A table or a column that an old night
lacks prints as absent or as an empty value.

The tool prints facts only. It names no stall and no cause.

`turns.user` holds the whole assembled prompt, so one feedback line
persists into every later turn of the session (`rota/tools/nightcount.py`).
A turn holds a phrase when its prompt carries more copies than the prompt
before it, or when its completion carries the phrase.

`--since` filters `finding_rulings.at` only. No other reported table
stores a time: `sessions`, `turns` and `messages` order by `seq` alone.

A wake run of one role and one wake kind, outside a batch and all
committed, prints as one line. The 39 reconcile ticks of night 101 made
the report too long to read otherwise. `--full` prints one line per
session.
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


def cut(text, n: int) -> str:
    """One line, at most `n` characters. The report cuts text and never wraps it."""
    s = " ".join(str("" if text is None else text).split())
    return s if len(s) <= n else s[: n - 3] + "..."


def short(sha) -> str:
    return (sha or "-")[:SHA]


def open_ro(path: str | Path) -> sqlite3.Connection:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"no run database at {p}")
    conn = sqlite3.connect(f"file:{p.resolve().as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


class Night:
    """The run database, with absent tables and columns read as empty."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.columns: dict[str, set[str]] = {}
        for (name,) in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'"):
            self.columns[name] = {r[1] for r in conn.execute(f"PRAGMA table_info({name})")}

    def has(self, table: str) -> bool:
        return table in self.columns

    def rows(self, table: str, cols: tuple[str, ...], tail: str = "") -> list[dict]:
        if not self.has(table):
            return []
        have = self.columns[table]
        sel = ", ".join(c if c in have else f"NULL AS {c}" for c in cols)
        return [dict(r) for r in self.conn.execute(f"SELECT {sel} FROM {table} {tail}")]


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


def _new_turn_text(turns: list[dict]) -> list[tuple[dict, str, str]]:
    """Each turn with its prompt and completion, beside the prompt before it."""
    out, prev = [], ""
    for t in turns:
        user = t["user"] or ""
        out.append((t, prev, t["completion"] or ""))
        prev = user
    return out


def _holds(turn: dict, prev_user: str, completion: str, phrase: str) -> bool:
    user = turn["user"] or ""
    return user.count(phrase) > prev_user.count(phrase) or phrase in completion


def _is_runner(turn: dict) -> bool:
    return (turn["completion"] or "").startswith(RUNNER_PREFIXES)


def build(conn: sqlite3.Connection, since: str | None = None, full: bool = False) -> list[str]:
    n = Night(conn)
    out: list[str] = []
    w = out.append

    sessions = n.rows("sessions", ("id", "role", "trigger_msg", "committed", "seq",
                                   "wake_kind", "wake_detail", "wake_refs"), "ORDER BY seq")
    turns_by: dict[str, list[dict]] = {}
    for t in n.rows("turns", ("session_id", "seq", "user", "completion"), "ORDER BY session_id, seq"):
        turns_by.setdefault(t["session_id"], []).append(t)
    last_call: dict[str, dict] = {}
    for c in n.rows("tool_calls", ("session_id", "fn", "args_summary", "seq"), "ORDER BY session_id, seq"):
        last_call[c["session_id"]] = c
    messages = n.rows("messages", ("id", "from_role", "to_role", "verb", "body_refs",
                                   "body_text", "unresolved_note", "status", "seq"), "ORDER BY seq")
    msg_by = {m["id"]: m for m in messages}
    items = {r["id"]: r for r in n.rows("items", ("id", "text"))}
    batches = n.rows("batches", ("id", "item_id", "head_commit", "status"), "ORDER BY rowid")
    batch_ids = {b["id"] for b in batches}
    receipts = n.rows("receipts", ("session_id", "table_name", "row_id", "new_version"),
                      "ORDER BY rowid")

    # A session belongs to a batch when its wake refs, or its trigger
    # message's refs, name the batch. A Developer woken by an answer carries
    # `[]` as wake refs, and the answer's refs name the batch.
    batch_of: dict[str, str | None] = {}
    for s in sessions:
        b = _names_batch(_refs(s["wake_refs"]), batch_ids)
        if b is None and s["trigger_msg"] in msg_by:
            b = _names_batch(_refs(msg_by[s["trigger_msg"]]["body_refs"]), batch_ids)
        batch_of[s["id"]] = b

    w(f"night report: {len(sessions)} sessions, "
      f"{sum(len(v) for v in turns_by.values())} turns, {len(batches)} batches. "
      f"Commits show their first {SHA} characters.")
    if since:
        w(f"--since {since} filters finding_rulings.at only.")

    # 1. Batches.
    w("== batches")
    receipt_sessions: dict[str, list[str]] = {}
    for r in receipts:
        if r["table_name"] == "batches":
            receipt_sessions.setdefault(r["row_id"], []).append(r["session_id"])
    seq_of = {s["id"]: s["seq"] for s in sessions}
    committed_of = {s["id"]: s["committed"] for s in sessions}
    history: dict[str, list[tuple[str, list[str]]]] = {}
    for b in batches:
        sids = set(receipt_sessions.get(b["id"], []))
        sids |= {sid for sid, bb in batch_of.items() if bb == b["id"]}
        seen: set[str] = set()
        steps: list[tuple[str, list[str]]] = []
        for sid in sorted(sids, key=lambda x: seq_of.get(x, 0)):
            shas = []
            for t in turns_by.get(sid, []):
                for text in (t["user"] or "", t["completion"] or ""):
                    for sha in COMMIT_RE.findall(text):
                        if sha not in seen:
                            seen.add(sha)
                            shas.append(sha)
            if shas:
                steps.append((sid, shas))
        if b["head_commit"] and b["head_commit"] not in seen:
            steps.append(("(row)", [b["head_commit"]]))
        history[b["id"]] = steps
        item = items.get(b["item_id"], {}).get("text")
        w(f"{b['id']} status={b['status']} head={short(b['head_commit'])} "
          f"commits={sum(len(x) for _, x in steps)} item={b['item_id']}: {cut(item, 80)}")
        for sid, shas in steps:
            flag = "" if sid == "(row)" or committed_of.get(sid) else " committed=0"
            w(f"  {sid}{flag} " + " ".join(short(x) for x in shas))

    # 2. Wakes, in order.
    w("== wakes")

    def wake_line(s: dict) -> str:
        ts = turns_by.get(s["id"], [])
        model_turns = sum(1 for t in ts if not _is_runner(t))
        # An agenda wake names seven ledger rows, and the full list pushed the
        # turn count and the committed flag past the line's cut.
        refs = cut(",".join(_refs(s["wake_refs"])), 40)
        if s["committed"]:
            c = last_call.get(s["id"])
            tail = f"last={c['fn']}({c['args_summary']})" if c else "last=-"
        else:
            err = ts[-1]["completion"] if ts else ""
            tail = "error=" + (err[len("SESSION FAILED: "):] if err.startswith("SESSION FAILED: ") else err)
        head = (f"{s['id']} {s['role']} {s['wake_kind']} [{refs}] "
                f"t={model_turns} c={s['committed']} ")
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
    i = 0
    while i < len(loose):
        s = loose[i]
        j = i
        if not full and s["committed"]:
            while (j + 1 < len(loose) and loose[j + 1]["committed"]
                   and loose[j + 1]["role"] == s["role"]
                   and loose[j + 1]["wake_kind"] == s["wake_kind"]):
                j += 1
        if j == i:
            w(wake_line(s))
        else:
            run = loose[i:j + 1]
            nturns = sum(1 for x in run for t in turns_by.get(x["id"], []) if not _is_runner(t))
            c = last_call.get(run[-1]["id"])
            last = f"{c['fn']}({c['args_summary']})" if c else "-"
            w(cut(f"{s['id']}..{run[-1]['id']} {s['role']} {s['wake_kind']} x{len(run)} "
                  f"t={nturns} c={len(run)} last={last}", WAKE_WIDTH))
        i = j + 1

    # 3. Verdicts.
    w("== verdicts")
    heads = {b["id"]: b["head_commit"] for b in batches}
    for v in n.rows("verdicts", ("id", "batch_id", "commit_sha", "result",
                                 "failed_criterion", "reason"), "ORDER BY rowid"):
        at = "head" if v["commit_sha"] and v["commit_sha"] == heads.get(v["batch_id"]) else "old"
        w(f"{cut(v['id'], 40)} batch={v['batch_id']} commit={short(v['commit_sha'])} {at} "
          f"result={v['result']} failed={v['failed_criterion'] or '-'} "
          f"reason={cut(v['reason'], 100) or '-'}")

    # 4. Test runs.
    w("== test runs")
    tally: "OrderedDict[tuple, list[int]]" = OrderedDict()
    for r in n.rows("test_runs", ("batch_id", "commit_sha", "result"), "ORDER BY rowid"):
        k = (r["batch_id"], r["commit_sha"])
        tally.setdefault(k, [0, 0])
        tally[k][0] += 1
        tally[k][1] += r["result"] != "pass"
    for (bid, sha), (runs, bad) in tally.items():
        at = " head" if sha and sha == heads.get(bid) else ""
        w(f"{bid} {short(sha)}{at} runs={runs} not_pass={bad}")

    # 5. Findings and rulings.
    w("== findings and rulings")
    rulings: dict[str, list[dict]] = {}
    tail = "ORDER BY rowid"
    for r in n.rows("finding_rulings", ("finding_id", "commit_sha", "ruling", "reason",
                                        "session_id", "at"), tail):
        if since and (r["at"] or "") < since:
            continue
        rulings.setdefault(r["finding_id"], []).append(r)
    for f in n.rows("findings", ("id", "batch_id", "constraint_id", "commit_sha",
                                 "status", "grain"), "ORDER BY rowid"):
        base = (f"{f['id']} batch={f['batch_id']} constraint={f['constraint_id']} "
                f"commit={short(f['commit_sha'])} {f['status']} grain={cut(f['grain'], 40)}")
        rs = rulings.get(f["id"], [])
        if not rs:
            w(base + " ruling=-")
        for r in rs:
            w(base + f" ruling={r['ruling']} at={r['at']} by={r['session_id'] or '-'} "
                     f"commit={short(r['commit_sha'])} reason={cut(r['reason'], 80)}")

    # 6. Attempts.
    w("== tick attempts")
    for a in n.rows("tick_attempts", ("tick_key", "attempts", "quarantined", "reported"),
                    "ORDER BY rowid"):
        w(f"{cut(a['tick_key'], 80)} attempts={a['attempts']} quarantined={a['quarantined']} "
          f"reported={a['reported']}")

    # 7. Quarantine and deferral.
    w("== quarantine and deferral")
    last_writer: dict[str, str] = {}
    for r in receipts:
        if r["table_name"] == "batches":
            last_writer[r["row_id"]] = r["session_id"]
    # The schema stores no time on a batch, so the last session with a
    # receipt on the row is the nearest record of who set the status.
    for b in batches:
        if b["status"] not in ("running", "merged"):
            w(f"{b['id']} status={b['status']} last_write={last_writer.get(b['id'], '-')}")
    for m in messages:
        if m["status"] == "quarantined":
            w(f"message {m['id']} {m['from_role']}->{m['to_role']} {m['verb']} status=quarantined")
    cps = n.rows("checkpoints", ("session_id", "role", "batch_id", "working_set", "valid"),
                 "ORDER BY rowid")
    w(f"checkpoints: {len(cps)}")
    for c in cps:
        w(f"{c['session_id']} {c['role']} batch={c['batch_id'] or '-'} valid={c['valid']} "
          f"working_set={cut(c['working_set'], 60)}")

    # 8. Messages.
    w("== messages")
    counts = Counter((m["from_role"], m["to_role"], m["verb"]) for m in messages)
    for (fr, to, verb), k in sorted(counts.items()):
        w(f"{fr}->{to} {verb} {k}")
    for m in messages:
        if m["status"] in ("open", "unresolved"):
            text = m["unresolved_note"] or m["body_text"] or m["body_refs"]
            w(f"{m['id']} {m['status']} {m['from_role']}->{m['to_role']} {m['verb']}: {cut(text, 80)}")

    # 9. Window and door phrases.
    w("== window and door phrases (turns, sessions)")
    holding: dict[str, list[tuple[str, int]]] = {p: [] for p in PHRASES}
    after: list[tuple[str, int, int]] = []
    for sid, ts in turns_by.items():
        first_complete = None
        for t, prev, comp in _new_turn_text(ts):
            for p in PHRASES:
                if _holds(t, prev, comp, p):
                    holding[p].append((sid, t["seq"]))
                    if p == COMPLETE and first_complete is None:
                        first_complete = t["seq"]
        if first_complete is not None:
            later = sum(1 for t in ts if t["seq"] > first_complete and not _is_runner(t))
            if later:
                after.append((sid, first_complete, later))
    for p in PHRASES:
        w(f"{p!r}: turns={len(holding[p])} sessions={len({s for s, _ in holding[p]})}")
    after.sort(key=lambda x: seq_of.get(x[0], 0))
    w(f"sessions with turns after the first turn holding {COMPLETE!r}: {len(after)}")
    for sid, first, later in after:
        w(f"  {sid} first_turn={first} turns_after={later}")

    # 10. Failures.
    w("== failures")
    for s in sessions:
        if not s["committed"]:
            ts = turns_by.get(s["id"], [])
            last = ts[-1]["completion"] if ts else ""
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
    ap.add_argument("--since", help="ISO time; filters finding_rulings.at")
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
