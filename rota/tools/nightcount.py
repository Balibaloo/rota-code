"""
The night's four counters: what the model made up, and what the runner ran
anyway.

    python -m rota.tools.nightcount clickI   # one run, by name or by path
    python -m rota.tools.nightcount          # every run in the runs directory

Six lines per run, plain ASCII, so a night log can carry them next to
`GAUNTLET-DONE`. The header names the run, its sessions and its turns. The
four counters follow. A line under the dangling pointers says what the count
means and names the three sessions with the most turns, because the night
106 log printed the term with no definition (frame 105, pass 7).

- made up: turns whose completion carries a tool result the model wrote
  for itself, the distinct sessions of those turns, and the split by role.
- ran anyway: made-up turns whose write call sits after the invention and
  whose next prompt carries a real write result, the same count by turn
  alone, made-up turns whose next prompt carries a landed commit after the
  turn's own echo, and the commits, first eight characters, in the order
  they appear.
- dangling pointers: prompts that evict an earlier result and then refuse
  to run the call again. The session is told to re-read what it cannot
  see.
- repeats: sessions that ran the same prompt hash on the same wake kind as
  an earlier session of the run, or the same role, wake kind, trigger and
  refs on the same tree.

Counter a reads `completion`, and not the feedback line in the prompt.
`db.session_fail` stores the whole assembled prompt in `turns.user`, so the
feedback line of one turn persists into every later turn of the session. A
count over the prompt overcounts the turns and undercounts the sessions
(scope report finding 1, `plans/archive/nightcount-scope-2026-09-23.md`,
2026-09-23).

Counter b reads the next turn, and not the made-up completion. The runner
answers a fabricated call in the prompt of the turn after it. A search
inside the fabricated completion reads zero writes on every night measured,
and the next prompt reads 1, 0, 0 and 8 on nights 86, 88, 89 and 90 (scope
report finding 2, 2026-09-23). A prompt holds the results of the earlier
turns as well, so two made-up turns of one session can count one write
twice. The count is of turns that went on after a fabrication, and not of
distinct files.

Counter b counts two things, because the turn is the wrong unit alone. A
write can precede the invention in the same turn, built on real reads, and
rule 1 of frame 77 leaves that write running by design: in three of night
90's eight turns the write came first (the design review of frame 77,
finding 4, 2026-09-23). So the first number counts the turns whose
`TOOL: code.write` call sits after the first invented result, and the turn
total stays beside it. The first number is what a night after frame 77 must
read as zero. The call test takes the marked form, so a bare `code.write(`
with no marker is not counted: every recorded write of the nights measured
carries the marker. Both numbers need a write call in the made-up turn. The
`written, not committed` result of an earlier write rides forward in every
prompt until the commit, and a turn that sent no write is not a write turn.

The wordings. `feb11d3`, 2026-08-11, added the fabrication feedback and the
`FABRICATED_RESULT` pattern that counter a matches. `5c76af2`, 2026-08-11,
added the eviction notice `re-read anything you still need` and the repeat
refusal `unchanged since you asked`. The second refusal, `was run for you
before you`, came two days later. `59cb2ad`, 2026-09-21, replaced the tail
of both refusals. The two substrings above match every era, so counter b
and counter c read any night since 2026-08-11 (scope report finding 3,
2026-09-23).
"""
from __future__ import annotations

import re
import sqlite3
from collections import Counter

from ..core.runner import FABRICATED_RESULT

# The prompt strings the counters match. Each one is era-free: see the
# module docstring for the commit that wrote it.
EVICTION = "re-read anything you still need"
REPEAT_TAILS = ("unchanged since you asked", "was run for you before you")
WRITE_RESULT = "OK code.write ->"
# A landed commit's head. A read can name `head_commit` with no commit.
COMMIT_HEAD = re.compile(r'"committed":\s*true,\s*"head_commit":\s*"([0-9a-f]+)"')


def landed_heads(text: str) -> list[str]:
    """The head of each landed commit in a prompt, in text order. This is
    the one reader of the landed commit (fact F26). A read result that
    names `head_commit` with no commit is not a landed commit."""
    return COMMIT_HEAD.findall(text or "")
# The write call as the seat sends it, marked and at the start of its line.
WRITE_CALL = re.compile(r"^[ \t]*TOOL:[ \t]*code\.write\b", re.MULTILINE)


def _rows(conn, sql, args=()):
    try:
        return conn.execute(sql, args).fetchall()
    except sqlite3.OperationalError:
        return []          # a database from before the table existed


def _real_write(prompt: str, completion: str = "") -> bool:
    """True when the prompt shows a write the runner really ran.

    The refusal of a repeat carries the same `OK code.write ->` head, and
    its tail sits on the same line. So the line, and not the prompt, is the
    unit of the test.

    The prompt quotes the made-up completion back before the real results,
    so an `OK code.write ->` line the seat invented sits in the prompt too.
    Night 91's `s154` turn 16 and `s157` turn 14 counted that way as writes
    the runner ran, while the NOT RUN line named both writes as held and
    the call record held no write for either turn (observed: 2026-09-24).
    So the scan starts after the echoed completion when the prompt holds it.
    """
    at = prompt.find(completion) if completion else -1
    tail = prompt[at + len(completion):] if at >= 0 else prompt
    for line in tail.splitlines():
        if WRITE_RESULT in line and not any(t in line for t in REPEAT_TAILS):
            return True
    return False


def _write_after(completion: str) -> bool:
    """True when a write call sits after the first invented result.

    Rule 1 of frame 77 holds exactly these calls. A write before the
    invention was built on real reads and still runs, so it belongs to the
    turn total and not to this count.
    """
    made = FABRICATED_RESULT.search(completion)
    if not made:
        return False
    return any(m.start() > made.start() for m in WRITE_CALL.finditer(completion))


def count(conn: sqlite3.Connection) -> dict:
    """Every counter of one run, as numbers. `lines` prints them."""
    turns = _rows(conn,
                  "SELECT t.session_id AS sid, t.seq AS seq, t.user AS user, "
                  "t.completion AS completion, s.role AS role "
                  "FROM turns t LEFT JOIN sessions s ON s.id = t.session_id "
                  "ORDER BY s.seq, t.seq")
    prompts = {(r["sid"], r["seq"]): (r["user"] or "") for r in turns}
    made = [r for r in turns if FABRICATED_RESULT.search(r["completion"] or "")]

    roles: dict[str, set[str]] = {}
    for r in made:
        roles.setdefault(r["role"] or "?", set()).add(r["sid"])

    writes = 0
    after_invention = 0
    commits = 0
    shas: list[str] = []
    for r in made:
        after = prompts.get((r["sid"], r["seq"] + 1))
        if after is None:
            continue           # the fabrication was the session's last turn
        # The turn must send a write of its own. `written, not committed`
        # rides forward in every later prompt until the commit, so a write
        # result alone counted night 90's s141 turns 12 and 14, which sent no
        # write (the diff review of frame 77, 2026-09-23).
        if (_real_write(after, r["completion"] or "")
                and WRITE_CALL.search(r["completion"] or "")):
            writes += 1
            if _write_after(r["completion"] or ""):
                after_invention += 1
        # The prompt carries the session's earlier results, so a commit before
        # the turn's own echo landed before the invention. Night 158 counted
        # 7 such turns, and s170 sent one completion twice, so the scan starts
        # after the last echo (frame 307, from night 158's read, W7).
        comp = r["completion"] or ""
        at = after.rfind(comp) if comp else -1
        tail = after[at + len(comp):] if at >= 0 else after
        heads = landed_heads(tail)
        if heads:
            commits += 1
            for sha in heads:
                if sha[:8] not in shas:
                    shas.append(sha[:8])

    dangling = [r for r in turns
                if EVICTION in (r["user"] or "")
                and any(t in (r["user"] or "") for t in REPEAT_TAILS)]

    groups = _repeats(conn, turns)
    repeated = sum(len(g) for g in groups)

    return {
        "sessions": _total(conn, "sessions"),
        "turns": len(turns),
        "made_turns": len(made),
        "made_sessions": len({r["sid"] for r in made}),
        "made_roles": {role: len(ids) for role, ids in sorted(roles.items())},
        "ran_writes": writes,
        "ran_after_invention": after_invention,
        "ran_commits": commits,
        "shas": shas,
        "dangling_turns": len(dangling),
        "dangling_sessions": len({r["sid"] for r in dangling}),
        # Ties keep the session order, so the line is the same on each run.
        "dangling_most": sorted(Counter(r["sid"] for r in dangling).items(),
                                key=lambda x: -x[1])[:3],
        "repeat_wakes": len(groups),
        "repeat_sessions": repeated,
        "repeats": repeated - len(groups),
        "repeat_groups": groups,
    }


def _repeats(conn: sqlite3.Connection, turns: list) -> list[list[str]]:
    """The sessions of each repeated wake, in session order.

    Two sessions are one wake when they share the prompt hash and the wake
    kind. They are also one wake when they share the role, the wake kind,
    the trigger message and the wake refs on one known tree. The prompt
    names the attempt and the size of a cut, so the hash differs between
    attempts. Night 105's s141, s142 and s143 woke on one tree with three
    hashes, and the hash rule counted no repeat (frame 105, pass 5).

    The union links whole groups, so a group can span trees through the
    hash rule. On night 101, s146 to s167 form one group across seven heads.

    The tree is the head of the newest landed commit in an earlier session's
    prompts. A session with no earlier landed commit has no known tree, so
    the second rule never joins it. The read skips the completion, because
    a seat can type an `OK code.commit` line itself. Night 101 holds 3 such
    completions, and night 90 holds 14. The newest head is the newest by
    turn order. A middle eviction can drop the newest result from a later
    prompt and leave an older one.

    The second rule needs the `trigger_msg` and `wake_refs` columns. Without
    them, the key joins every session of one role and kind on one tree.
    """
    have = {r[1] for r in _rows(conn, "PRAGMA table_info(sessions)")}
    if not have:
        return []
    keyed = {"trigger_msg", "wake_refs"} <= have
    cols = ("id", "seq", "role", "wake_kind", "trigger_msg", "wake_refs", "prompt_hash")
    sel = ", ".join(c if c in have else f"NULL AS {c}" for c in cols)
    sessions = _rows(conn, f"SELECT {sel} FROM sessions ORDER BY seq")
    landed: dict[str, str] = {}
    seen: dict[str, set[str]] = {}
    for r in turns:
        known = seen.setdefault(r["sid"], set())
        for sha in landed_heads(r["user"]):
            # A head that an earlier turn showed is older than a new one.
            if sha not in known:
                known.add(sha)
                landed[r["sid"]] = sha
    parent = {s["id"]: s["id"] for s in sessions}

    def root(sid: str) -> str:
        while parent[sid] != sid:
            sid = parent[sid]
        return sid

    first: dict[tuple, str] = {}
    tree = None
    for s in sessions:
        keys = []
        if s["prompt_hash"]:
            keys.append(("hash", s["prompt_hash"], s["wake_kind"]))
        if keyed and tree is not None:
            keys.append(("wake", s["role"], s["wake_kind"], s["trigger_msg"],
                         s["wake_refs"], tree))
        for k in keys:
            if k in first:
                parent[root(s["id"])] = root(first[k])
            else:
                first[k] = s["id"]
        # The session's own commits move the tree for the sessions after it.
        tree = landed.get(s["id"], tree)
    members: dict[str, list[str]] = {}
    for s in sessions:
        members.setdefault(root(s["id"]), []).append(s["id"])
    return [g for g in members.values() if len(g) > 1]


def _total(conn: sqlite3.Connection, table: str) -> int:
    rows = _rows(conn, f"SELECT COUNT(*) AS n FROM {table}")
    return rows[0]["n"] if rows else 0


def lines(name: str, c: dict) -> list[str]:
    """The six lines of one run."""
    roles = ", ".join(f"{r} {n}" for r, n in c["made_roles"].items()) or "none"
    shas = " ".join(c["shas"]) or "none"
    return [
        f"NIGHTCOUNT {name}: {c['sessions']} sessions, {c['turns']} turns",
        f"made up: {c['made_turns']} turns, {c['made_sessions']} sessions "
        f"({roles})",
        f"ran anyway: {c['ran_after_invention']} writes after an invention "
        f"({c['ran_writes']} turns with a write result), "
        f"{c['ran_commits']} with a landed commit, shas {shas}",
        f"dangling pointers: {c['dangling_turns']} turns, "
        f"{c['dangling_sessions']} sessions",
        "  A dangling pointer is a turn whose prompt holds the eviction notice "
        "and a refusal to run a call again. Most such turns: "
        + (", ".join(f"{sid} ({n})" for sid, n in c["dangling_most"]) or "none"),
        f"repeats: {c['repeat_wakes']} wakes repeated, "
        f"{c['repeat_sessions']} sessions, {c['repeats']} of them repeats",
    ]


def main(argv: list[str]) -> int:
    from ..cli import RUNS, require
    from ..core.db import connect_readonly

    paths = [require(argv[0])] if argv else sorted(RUNS.glob("*.db"))
    for p in paths:
        try:
            counted = count(connect_readonly(p))
        except sqlite3.Error as e:
            print(f"NIGHTCOUNT {p.stem}: unreadable: {e}")
            continue
        for line in lines(p.stem, counted):
            print(line)
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))
