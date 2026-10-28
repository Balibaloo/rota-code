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
newest feedback never includes that completion. A prompt that holds no copy
of the previous completion counts nothing, and the report counts those
prompts.

The eviction notice is the one phrase read from the whole prompt. `_fit`
writes `[N earlier exchange(s) dropped to fit the window ...]` in the middle
of the prompt, before the newest feedback, so the feedback rule never sees
the notice (frame 105 second review, s132 and s88 of night 101). A turn
counts `dropped to fit the window` when its prompt holds the notice. The
prompt of that turn lacks the exchanges the notice names.

The notice's N does not show a new drop. `_fit` writes N as the new drops
plus one for the old notice, so one new drop after a notice of 2 writes 2
again. The count by a new N read 20 turns on night 105, and the prompts hold
43 notices (frame 105, pass 5). The text after the notice does not show a
new drop either, because a tier drops a block from anywhere in the middle.

`--since` filters `finding_rulings.at` only. No other reported table
stores a time: `sessions`, `turns` and `messages` order by `seq` alone.

By default, the sessions outside a batch print as one line per role and
wake kind, and the completion-line list keeps its ten largest counts.
`--full` prints one line per session and the whole list.
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
# `db.session_fail` and `db.session_note` add a turn that the model never ran.
RUNNER_PREFIXES = ("SESSION FAILED", "SESSION ENDED")
SHA = 10
WAKE_WIDTH = 120
# The value of a column that the database lacks.
ABSENT = "?"
# A prompt can hold a long completion cut short. The search then uses the
# completion's start.
HEAD_PROBE = 60
WINDOW = "dropped to fit the window"
# The bracket anchors the notice that `_fit` writes, so a model's prose that
# names earlier exchanges does not match.
EVICT_RE = re.compile(r"\[(\d+) earlier exchange")


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
    # A night from before fact F4 has no `latest_runs` view. A read script
    # that opens a night here and calls a rota reader then still reads.
    from ..core.db import latest_runs_view
    latest_runs_view(conn)
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
    completion, even cut short. The feedback is then empty, so the turn
    counts nothing. The runner follows a completion with a blank line, so
    that form is searched first. A copy of the completion inside the
    feedback then cannot move the boundary.
    """
    if prev_completion is None:
        return user, True
    if not prev_completion:
        return "", False
    i = user.rfind(prev_completion + "\n\n")
    if i >= 0:
        return user[i + len(prev_completion):], True
    i = user.rfind(prev_completion)
    if i >= 0:
        return user[i + len(prev_completion):], True
    i = user.rfind(prev_completion[:HEAD_PROBE])
    if i < 0:
        return "", False
    k = 0
    while k < len(prev_completion) and i + k < len(user) and prev_completion[k] == user[i + k]:
        k += 1
    return user[i + k:], True


def _is_runner(turn: dict) -> bool:
    return str(turn["completion"] or "").startswith(RUNNER_PREFIXES)


def _ruled_rows(n: Night, ruling_id: str) -> dict:
    """The verdict per ref of one ruling: its `landed` rows, else its
    keypress rows, else all its rows, the order of `verdict_for`. Empty
    when the night has no `ruled_refs` table.

    The last two tiers take the filters of `verdict_for`: no `reading:`
    ref, and no approve of a resolved ledger row (fact F1, review 1,
    finding 6). A night opens without the schema mark, so this reader keeps
    its own query and does not call `verdict_for`."""
    if not n.has("ruled_refs", "source"):
        return {}
    rows = n.conn.execute(
        "SELECT ref, verdict, source FROM ruled_refs WHERE ruling_id = ? "
        "ORDER BY rowid", (ruling_id,)).fetchall()
    landed = [x for x in rows if x["source"] == "landed"]
    if landed:
        return {x["ref"]: x["verdict"] for x in landed}
    resolved = set()
    if n.has("ledger", "status"):
        resolved = {r["id"] for r in n.conn.execute(
            "SELECT id FROM ledger WHERE status = 'resolved'")}
    chosen = [x for x in rows if x["source"] == "keypress"] or rows
    return {x["ref"]: x["verdict"] for x in chosen
            if not str(x["ref"]).startswith("reading:")
            and not (x["verdict"] == "approve" and x["ref"] in resolved)}


def _config(n: Night, key: str):
    """A `config` value, JSON-decoded when it can be, or None."""
    if not n.has("config", "value"):
        return None
    row = n.conn.execute("SELECT value FROM config WHERE key = ?", (key,)).fetchone()
    if row is None:
        return None
    try:
        return json.loads(row["value"])
    except (TypeError, ValueError):
        return row["value"]


def _stamp(n: Night, message_id) -> dict:
    """The send door's code stamp of a page. `api.code_stamp` is the one
    reader of the stamp (fact F26). A night with no `config` table has no
    stamp."""
    from ..roles.api import code_stamp

    return code_stamp(n.conn, message_id) if n.has("config", "value") else {}


def _git_truth(repo: Path | None, batch_id: str, head: str | None = None) -> list[str] | None:
    """The paths of the merge commit "rota: deliver <batch id>", or None.

    `worktrees.integrate` writes that message, and neither the guess nor
    `annotate` writes git, so the diff is a truth independent of both
    (frame 298's design, 5.1). One sample repository serves many nights, and
    batch ids repeat across nights. So a known head commit must be an
    ancestor of the merge's second parent, and two candidates name no single
    truth. The head is the Developer's last commit, and the Tester's commit
    "rota: tests of <batch id>" can follow it (observed: night 156's bg_1)."""
    import subprocess

    if repo is None or not (Path(repo) / ".git").exists():
        return None
    log = subprocess.run(["git", "-C", str(repo), "log", "--all", "--merges",
                          "--format=%H%x00%P%x00%s"], capture_output=True, text=True)
    if log.returncode != 0:
        return None
    shas = []
    for line in log.stdout.splitlines():
        sha, parents, subject = (line.split("\x00") + ["", ""])[:3]
        if subject != f"rota: deliver {batch_id}":
            continue
        second = (parents.split()[1:2] or [""])[0]
        if head and head != ABSENT and not (second and subprocess.run(
                ["git", "-C", str(repo), "merge-base", "--is-ancestor", head, second],
                capture_output=True).returncode == 0):
            continue
        shas.append(sha)
    if len(shas) != 1:
        return None
    diff = subprocess.run(["git", "-C", str(repo), "diff", "--name-only",
                           f"{shas[0]}^1", shas[0]], capture_output=True, text=True)
    if diff.returncode != 0:
        return None
    return sorted(p for p in diff.stdout.splitlines() if p.strip())


def _request_items(n: Night) -> set[str]:
    """The request items by the count's rule: `_is_request_item` without the
    `delivered:` check (`plans/frame298-count.md`, section 1)."""
    if not n.has("items", "kind"):
        return set()
    cols = n.columns["items"]
    sql = "SELECT id FROM items WHERE kind = 'in_scope' AND id != 'how_it_works'"
    if "is_description" in cols:
        sql += " AND COALESCE(is_description, 0) = 0"
    ids = {r["id"] for r in n.conn.execute(sql)}
    views = {r[0] for r in n.conn.execute("SELECT name FROM sqlite_master WHERE type = 'view'")}
    if "item_provenance" in views:
        ids -= {r[0] for r in n.conn.execute(
            "SELECT id FROM item_provenance WHERE provenance = 'observed'")}
    return ids


def _cancel_after(log_lines: list[str] | None, ask_id: str, words: str,
                  batches_of_item: set[str]) -> str:
    """"yes" when the night log holds a `do:cancel` of the item's batch after
    the ruling's reply line, "no" when it does not, and "?" with no log.

    A cancel writes only `batches.status`, so the log is its one record of
    order. The reply line is `[<page>] <verb>: <page text>  -> '<words>`."""
    if log_lines is None:
        return ABSENT
    head = " ".join(str(words or "").split())[:40]
    # A reply to the Liaison's question about a page logs under the
    # question's id, so the words alone find it when the page's id does not.
    hits = [i for i, line in enumerate(log_lines)
            if line.startswith("[") and f"-> '{head}" in line]
    at = next((i for i in hits if log_lines[i].startswith(f"[{ask_id}]")),
              hits[0] if hits else None)
    if at is None:
        return ABSENT
    # The next reply of any page ends the scan. A later cancel belongs to a
    # later ruling (review 4 of frame 298, finding 1).
    for line in log_lines[at + 1:]:
        if line.startswith("["):
            break
        m = re.match(r"\s*do:cancel: abandoned (\S+?):", line)
        if m and m.group(1) in batches_of_item:
            return "yes"
    return "no"


HAND_CAP = 30
WORDS_CUT = 120


def _guess_section(n: Night, messages: list[dict], batches: list[dict],
                   repo: Path | None, log: Path | None) -> list[str]:
    """
    Frame 298's measures, from rows and the git truth (its design, 5.3).

    M0 counts the sign-off pages that carry a code line, a page shown again
    included. M1 and M2 count the merged items whose last shown guess names
    a path of the merge commit's diff, and M2 counts only paths outside
    `tests/`. The hand list serves
    M3 and M4, which a reader classes into the count's (a) to (d).
    """
    from ..roles.api import _grain_path

    out = ["== frame 298: the guess"]
    w = out.append
    for line in (n.absent("touch_guesses", ("item_id", "item_ver", "ruling_id", "grain"))
                 + n.absent("rulings", ("id", "ask_id", "per_item", "words", "status",
                                        "verdict_id"))
                 + n.absent("messages", ("cause_id",))):
        w(line)
    if repo is None:
        root = _config(n, "project_root")
        repo = Path(str(root).strip('"')) if root else None
    w(f"repository: {repo if repo else '-'}; log: {log if log else '-'}")

    # M0: a present whose cause is a submit, and whose door row maps a code key.
    verb_of = {m["id"]: m["verb"] for m in messages}
    cause_of = ({r["id"]: r["cause_id"] for r in n.conn.execute(
        "SELECT id, cause_id FROM messages")} if n.has("messages", "cause_id") else {})
    # A page shown again has no submit cause, and it is a sign-off page too.
    # Night 158's m89 and m122 showed a request again and carried a code line
    # (frame 307, from night 158's read, W7). A batch page, a shift page and a
    # park page are other pages. A description item alone is onboarding.
    from ..core.scheduler import PARK_ASK
    from ..roles.principal import SHIFT_ASK

    requests = ({r["id"] for r in n.conn.execute(
        "SELECT id FROM items WHERE is_description = 0")}
        if n.has("items", "is_description") else
        {r["id"] for r in n.conn.execute("SELECT id FROM items")} if n.has("items") else set())
    batch_ids = {b["id"] for b in batches}

    # A page shown again counts only when a code line showed a guess. Night
    # 157's m134, m139, m205 and m210 showed a batch plan, which M0 does not
    # measure (frame 307, pass 1b).
    def _showed_guess(stamp) -> bool:
        return isinstance(stamp, dict) and any(
            isinstance(v, dict) and "guess" in v for v in stamp.values())

    signoff: list[dict] = []
    shown: set[str] = set()
    for m in messages:
        if m["verb"] != "present":
            continue
        refs = set(_refs(m["body_refs"]))
        if verb_of.get(cause_of.get(m["id"])) == "submit":
            signoff.append(m)
            shown |= refs & requests
        elif (m["to_role"] == "principal" and refs & shown and not refs & batch_ids
              and not str(m["id"]).startswith((SHIFT_ASK, PARK_ASK))
              and _showed_guess(_stamp(n, m['id']))):
            signoff.append(m)
    with_line = 0
    for m in signoff:
        stamp = _stamp(n, m['id'])
        if any(str(k).startswith("guess:") for k in stamp):
            with_line += 1
    w(f"M0: {with_line} of {len(signoff)} sign-off pages carry a code line")

    # M1 and M2: the last guess a page showed the principal, else the item's
    # own guess, its first version with no ruling. The Architect rewrote a
    # guess up to four times on night 157, so the first one is a guess he
    # never saw last (frame 307, from night 158's read, W7). The truth needs
    # no guess table, so old nights print it (design 5.1 and 5.2, review 4 of
    # frame 298, finding 4).
    has_guesses = n.has("touch_guesses")
    seq_of = {m["id"]: i for i, m in enumerate(messages)}
    stamps = [(m["id"], _stamp(n, m["id"])) for m in messages
              if m["verb"] == "present"] if has_guesses else []

    def _seen(item: str) -> tuple | None:
        """The guess set `(item_ver, ruling_id)` the last page showed, or None."""
        page = None
        for mid, stamp in reversed(stamps):
            line = stamp.get(f"guess:{item}") if isinstance(stamp, dict) else None
            if line is None:
                continue
            ref = line.get("guess") if isinstance(line, dict) else None
            if isinstance(ref, list) and len(ref) == 2:
                return ref[0], ref[1]
            page = page or mid
        if page is None:
            return None
        # A code line with no guess reference: the latest set before the page.
        for r in n.conn.execute("SELECT item_ver, ruling_id FROM touch_guesses "
                                "WHERE item_id = ? ORDER BY rowid DESC", (item,)):
            if not r["ruling_id"] or seq_of.get(r["ruling_id"], len(seq_of)) < seq_of[page]:
                return r["item_ver"], r["ruling_id"]
        return None

    merged = [b for b in batches if b["status"] == "merged"]
    lines: list[str] = []
    m1 = m2 = withtruth = absent = no_own = 0
    for b in merged:
        truth = _git_truth(repo, b["id"], b["head_commit"])
        shown_truth = ",".join(truth) if truth is not None else "absent"
        if not has_guesses:
            lines.append(f"  {b['item_id']} guess=absent truth={shown_truth}")
            continue
        seen = _seen(b["item_id"])
        rows = n.conn.execute(
            "SELECT grain FROM touch_guesses WHERE item_id = ? AND item_ver = ? "
            "AND ruling_id = ? ORDER BY rowid", (b["item_id"], *seen)).fetchall() if seen else []
        rows = rows or n.conn.execute(
            "SELECT grain FROM touch_guesses WHERE item_id = ? AND ruling_id = '' "
            "AND item_ver = (SELECT MIN(item_ver) FROM touch_guesses WHERE item_id = ? "
            "AND ruling_id = '') ORDER BY rowid", (b["item_id"], b["item_id"])).fetchall()
        # A set under a ruling and no own set: the Architect never guessed, so
        # the item is no miss (review 4 of frame 298, finding 2).
        if not rows and n.conn.execute(
                "SELECT 1 FROM touch_guesses WHERE item_id = ? AND ruling_id != ''",
                (b["item_id"],)).fetchone():
            no_own += 1
            lines.append(f"  {b['item_id']} no own guess truth={shown_truth}")
            continue
        guess: list[str] = []
        for r in rows:
            p = _grain_path(r["grain"])
            if p not in guess:
                guess.append(p)
        shown = ",".join(guess) or "-"
        if truth is None:
            absent += 1
            lines.append(f"  {b['item_id']} guess={shown} truth absent")
            continue
        withtruth += 1
        hit = set(guess) & set(truth)
        src = {p for p in hit if not p.replace("\\", "/").startswith("tests/")}
        m1 += bool(hit)
        m2 += bool(src)
        lines.append(f"  {b['item_id']} guess={shown} truth={','.join(truth)} "
                     f"M1={'hit' if hit else 'miss'} M2={'hit' if src else 'miss'}")
    if not has_guesses:
        w("M1: absent")
        w("M2: absent")
    else:
        w(f"M1: {m1} of {withtruth} merged items, {absent} with no truth, "
          f"{no_own} with no own guess")
        w(f"M2: {m2} of {withtruth} merged items, {absent} with no truth, "
          f"{no_own} with no own guess")
    out.extend(lines)

    # The hand list for M3 and M4: contest or revise on a request line or a
    # code line, oldest first. The landed verdict map is what `land` wrote.
    if n.has("rulings"):
        requests = _request_items(n)
        log_lines = (Path(log).read_text("utf-8", errors="replace").splitlines()
                     if log and Path(log).exists() else None)
        by_item: dict[str, set[str]] = {}
        for b in batches:
            by_item.setdefault(b["item_id"], set()).add(b["id"])
        listed: list[str] = []
        for r in n.rows("rulings", ("id", "ask_id", "per_item", "words", "status",
                                    "verdict_id")):
            if r["status"] != "landed":
                continue
            # His keypress rows are his verdict, else the reading's rows
            # (fact F1). A night from before `ruled_refs` has `per_item` only.
            landed = _ruled_rows(n, r["id"])
            if not landed:
                try:
                    landed = json.loads(r["per_item"] or "{}")
                except (TypeError, ValueError):
                    landed = {}
            stamp = _stamp(n, r["ask_id"])
            planned = ({v.get("batch") for v in stamp.values() if isinstance(v, dict)}
                       if isinstance(stamp, dict) else set())
            for key, ruling in landed.items():
                if ruling not in ("contest", "revise"):
                    continue
                if key in requests:
                    kind, item = "request line", key
                elif str(key).startswith("guess:"):
                    kind, item = "code line", str(key)[len("guess:"):]
                elif key in planned:
                    kind = "code line"
                    item = next((b["item_id"] for b in batches if b["id"] == key), "")
                else:
                    continue
                contested = "yes" if landed.get(item) in ("contest", "revise") else "no"
                cancel = _cancel_after(log_lines, r["ask_id"], r["words"],
                                       by_item.get(item, set()))
                listed.append(f"  {r['id']} page={r['ask_id']} verdict={r['verdict_id']} "
                              f"{key} {ruling} ({kind}) contested={contested} "
                              f"cancel={cancel}: {cut(r['words'], WORDS_CUT)}")
        w(f"hand list: {len(listed)} rulings, the first {HAND_CAP} shown")
        out.extend(listed[:HAND_CAP])
        if len(listed) > HAND_CAP:
            w(f"{len(listed) - HAND_CAP} more unread")
        w(_unconfirmed_line(n))
    return out


def _unconfirmed_line(n: Night) -> str:
    """The rows of the Liaison's reading that he had not confirmed at the
    night's end, one line. A reading he never confirmed is no record of his
    (the seam design, 2.4)."""
    if not n.has("ruled_refs"):
        return f"read-back: {ABSENT}"
    try:
        row = n.conn.execute(
            "SELECT COUNT(*) AS rows, COUNT(DISTINCT reply_id) AS replies "
            "FROM ruled_refs_live WHERE source = 'reading' "
            "AND ruling_status = 'landed' AND confirmed_by IS NULL "
            "AND substr(ref, 1, 8) != 'reading:'").fetchone()
    except sqlite3.OperationalError:
        return f"read-back: {ABSENT}"
    return (f"read-back: {row['rows']} rows of {row['replies']} replies "
            f"unconfirmed at the night's end")


def build(conn: sqlite3.Connection, since: str | None = None, full: bool = False,
          repo: str | Path | None = None, log: str | Path | None = None) -> list[str]:
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
    # or a tool call's `batch_id=` argument. A Developer woken by an answer
    # carries `[]` as wake refs. s150 of night 101 committed to bg_1 through a
    # receipt, and s144 named bg_1 in `tests.encode` (frame 105 diff review).
    # A batch id inside free text, such as a message body, does not count.
    batch_of: dict[str, str | None] = {}
    for s in sessions:
        b = _names_batch(_refs(s["wake_refs"]), batch_ids)
        if b is None and s["trigger_msg"] in msg_by:
            b = _names_batch(_refs(msg_by[s["trigger_msg"]]["body_refs"]), batch_ids)
        if b is None:
            b = batch_by_receipt.get(s["id"])
        if b is None and batch_re is not None:
            for c in calls_by.get(s["id"], []):
                args = str(c["args_summary"] or "")
                m = batch_re.search(args) if "batch_id=" in args else None
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
    from .nightcount import landed_heads

    for b in batches:
        sids = set(receipt_sessions.get(b["id"], []))
        sids |= {sid for sid, bb in batch_of.items() if bb == b["id"]}
        seen: set[str] = set()
        steps: list[tuple[str, list[str]]] = []
        for sid in sorted(sids, key=lambda x: (seq_of.get(x) if isinstance(seq_of.get(x), int)
                                               else 0, x)):
            shas = []
            for t in turns_by.get(sid, []):
                # `code.code_commit` writes the sha to `batches.head_commit`
                # only, and a later commit overwrites it. The runner's
                # feedback line keeps each sha. `nightcount.landed_heads` is
                # the one reader of that line (fact F26).
                for text in (str(t["user"] or ""), str(t["completion"] or "")):
                    for sha in landed_heads(text):
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
            # `?` means an absent table, so a session with turns and no
            # commit line says so in words.
            none = "no commit line" if have_turns else f"sha={ABSENT}"
            w(f"  {sid}{flag} " + (" ".join(short(x) for x in shas) or none))

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
    # Without the wake kind, two sessions of one role cannot be told apart.
    can_group = not full and n.has("sessions", "wake_kind")
    if not can_group:
        for s in loose:
            w(wake_line(s))
    else:
        # Night 102's read spent 39k of 73.5k on the print before its first
        # query, and 130 of the lines were no-batch wakes (frame 105, pass 4).
        groups: "OrderedDict[tuple, list[dict]]" = OrderedDict()
        for s in loose:
            groups.setdefault((s["role"], s["wake_kind"]), []).append(s)
        for (role, kind), group in groups.items():
            ts = sum(model_turns(x["id"]) for x in group) if have_turns else ABSENT
            done = (sum(1 for x in group if x["committed"] == 1)
                    if n.has("sessions", "committed") else ABSENT)
            w(cut(f"{role} {kind} x{len(group)} t={ts} c={done} "
                  f"first={group[0]['id']} last={group[-1]['id']}", WAKE_WIDTH))
        for s in loose:
            if s["committed"] == 0:
                w(wake_line(s))

    # 3. Verdicts.
    w("== verdicts")
    V_COLS = ("id", "batch_id", "commit_sha", "result", "failed_criterion", "reason",
              "lines")
    for line in n.absent("verdicts", V_COLS) + n.absent("batches", ("id", "head_commit")):
        w(line)
    heads = {b["id"]: b["head_commit"] for b in batches}

    def at_head(bid, sha) -> str:
        head = heads.get(bid)
        if sha == ABSENT or head == ABSENT or bid not in heads:
            return ABSENT
        return "head" if sha and sha == head else "old"

    def named(v) -> str:
        """The count of criteria a pass named a line for (frame 170)."""
        if v["lines"] == ABSENT:
            return ABSENT
        if v["result"] != "pass":
            return "-"
        try:
            return str(len(json.loads(v["lines"] or "{}")))
        except (ValueError, TypeError):
            return ABSENT

    for v in n.rows("verdicts", V_COLS):
        w(f"{cut(v['id'], 40)} batch={v['batch_id']} commit={short(v['commit_sha'])} "
          f"{at_head(v['batch_id'], v['commit_sha'])} "
          f"result={v['result']} failed={v['failed_criterion'] or '-'} "
          f"named={named(v)} reason={cut(v['reason'], 100) or '-'}")

    # 4. Test runs.
    w("== test runs")
    TR_COLS = ("batch_id", "commit_sha", "result")
    for line in n.absent("test_runs", TR_COLS) + n.absent("test_run_journal", TR_COLS):
        w(line)
    # `test_runs` holds the live run per test, and the journal holds every
    # run (frame 309). The brief names the word `absent` for a database from
    # before the journal, so a zero never stands for a missing table.
    journal = n.has("test_run_journal")
    # A key holds four counts: the live rows and their not-pass rows, then
    # the same two for the journal.
    tally: "OrderedDict[tuple, list]" = OrderedDict()

    def count(table: str, at: int) -> None:
        for r in n.rows(table, TR_COLS):
            k = (r["batch_id"], r["commit_sha"])
            pair = tally.setdefault(k, [0, 0, 0, 0])
            pair[at] += 1
            if r["result"] == ABSENT:
                pair[at + 1] = ABSENT
            elif pair[at + 1] != ABSENT:
                pair[at + 1] += r["result"] != "pass"

    count("test_runs", 0)
    count("test_run_journal", 2)
    for (bid, sha), (runs, bad, jruns, jbad) in tally.items():
        mark = at_head(bid, sha)
        at = " head" if mark == "head" else (f" {ABSENT}" if mark == ABSENT else "")
        if not journal:
            jruns = jbad = "absent"
        w(f"{bid} {short(sha)}{at} runs={runs} journal={jruns} not_pass={bad} "
          f"journal_not_pass={jbad}")

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
            evicted = False
            if runner:
                # The runner's turn has no prompt. Its completion is the runner's text.
                fresh = ""
            else:
                user = str(t["user"] or "")
                fresh, matched = _newest_feedback(user, prev_completion)
                unmatched += not matched
                evicted = EVICT_RE.search(user) is not None
            for p in PHRASES:
                if p in fresh or p in completion or (p == WINDOW and evicted):
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
    # The largest counts first. Night 102 listed 49 sessions, so the brief
    # print keeps ten.
    from_first.sort(key=lambda x: (-x[2], seq_of.get(x[0]) if isinstance(seq_of.get(x[0]), int)
                                   else 0, x[0]))
    shown = from_first if full else from_first[:10]
    of = f" ({len(shown)} of {len(from_first)} shown)" if len(shown) < len(from_first) else ""
    w(f"sessions with model turns at or after the first turn holding {COMPLETE!r}: "
      f"{len(from_first) if have_turns else ABSENT}{of}")
    for sid, first, count in shown:
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
    # A committed session that ended on refusals is not a failure, but the
    # runner's account turn is its only record. Night 173's s130 shape
    # left no line here once it stopped failing (the W11 review, finding 1).
    reasons: Counter = Counter()
    ended = 0
    for s in sessions:
        if s["committed"] != 1:
            continue
        said = [ln[2:] for t in turns_by.get(s["id"], [])
                if str(t["completion"] or "").startswith("SESSION ENDED")
                for ln in str(t["completion"]).splitlines() if ln.startswith("- ")]
        if said:
            ended += 1
            reasons.update(said)
    if ended:
        top, k = sorted(reasons.items(), key=lambda x: (-x[1], x[0]))[0]
        w(f"committed sessions that ended with refusals in the runner's account: "
          f"{ended}, {sum(reasons.values())} lines, the most common {k}x: {cut(top, 100)}")

    # 11. Open faults, per refused call (frame 204's design, section 7). A
    # seat's fault report reaches the build session here after a night.
    w("== open faults")
    FT_COLS = ("call", "kind", "status")
    for line in n.absent("faults", FT_COLS):
        w(line)
    per_call = Counter((f["call"], f["kind"]) for f in n.rows("faults", FT_COLS, ("seq",))
                       if f["status"] == "open")
    for (call, kind), k in sorted(per_call.items(), key=lambda x: (-x[1], str(x[0]))):
        w(f"{call} {kind} {k}")

    # 12. Frame 298's measures (its design, section 5).
    out.extend(_guess_section(n, messages, batches, repo, log))
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
    ap.add_argument("--full", action="store_true",
                    help="one line per session, and the whole completion-line list")
    ap.add_argument("--repo", help="the night's project repository; the default is "
                                   "config.project_root")
    ap.add_argument("--log", help="the night's log, for the cancel order; the default is "
                                  "night<N>.log beside a database named ..._night<N>.db")
    args = ap.parse_args(argv)
    log = args.log
    if log is None:
        m = re.search(r"night(\d+)\.db$", Path(args.db).name)
        beside = Path(args.db).with_name(f"night{m.group(1)}.log") if m else None
        log = beside if beside is not None and beside.exists() else None
    try:
        conn = open_ro(args.db)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        return 2
    try:
        lines = build(conn, args.since, args.full,
                      repo=Path(args.repo) if args.repo else None, log=log)
    finally:
        conn.close()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
