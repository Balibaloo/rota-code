"""
A model in the principal's seat, for a walk (frame 41, plans/frame41-design.md).

The walk picks this backend when WALK_AGENT names a model. The script stays
the default (ruled: Roman, 2026-09-18, the walk is a diagnostic). Each page
goes to the Claude Code binary, headless, one process per page. The words
land through the same doors as the script's words.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import shutil
import sqlite3
import subprocess
from pathlib import Path

from rota.roles.principal import Answer, Ask, land, parse_reply
from rota.roles.principal import pump as principal_pump
from rota.core.scheduler import park_ask_batch

BRIEF = Path(__file__).resolve().parent / "principal_brief.md"
NOTHING = "(nothing)"
RECENT = 5
# A page in the recent list is cut, because the system prompt goes on the
# command line, and Windows caps a command line at 32767 characters.
RECENT_CHARS = 1500
# Two hops reach the ask: the Liaison's question, the principal's reply, the
# ask. The cap stops a cycle in a broken cause chain.
CHAIN_CAP = 8


class PrincipalDown(RuntimeError):
    """The model failed twice on one ask. The walk stops."""


def find_binary(env=None, home: Path | None = None) -> str:
    """CLAUDE_BIN, else the newest extension binary, else `claude` on the path."""
    env = os.environ if env is None else env
    if env.get("CLAUDE_BIN"):
        return env["CLAUDE_BIN"]
    home = Path.home() if home is None else home
    found = sorted(home.glob(".vscode/extensions/anthropic.claude-code-*/"
                             "resources/native-binary/claude.exe"),
                   key=lambda p: p.stat().st_mtime)
    if found:
        return str(found[-1])
    return shutil.which("claude") or "claude"


def call_model(model: str, system: str, page: str, cwd: Path,
               run=subprocess.run) -> dict:
    """
    One headless call. Returns ok, words, error, duration_ms, total_cost_usd.

    No `--bare`: with it the call exits 1, `Not logged in` (design 4a, point
    3). The child runs in a scratch folder, so rota's CLAUDE.md and hooks do
    not load. The environment drops the two variables of the parent session,
    because a nested session can refuse to start.
    """
    cmd = [find_binary(), "-p", "--model", model, "--output-format", "json",
           "--tools", "", "--no-session-persistence", "--max-budget-usd", "1",
           "--system-prompt", system]
    env = {k: v for k, v in os.environ.items()
           if k not in ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT")}
    cwd.mkdir(parents=True, exist_ok=True)
    out = {"ok": False, "words": "", "error": "", "duration_ms": None,
           "total_cost_usd": None}
    try:
        p = run(cmd, input=page, capture_output=True, text=True,
                encoding="utf-8", errors="replace", env=env, cwd=str(cwd),
                timeout=600)
    except (OSError, subprocess.TimeoutExpired) as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
        return out
    try:
        data = json.loads(p.stdout or "")
    except ValueError:
        data = {}
    out["duration_ms"] = data.get("duration_ms")
    out["total_cost_usd"] = data.get("total_cost_usd")
    words = str(data.get("result") or "").strip()
    if p.returncode != 0 or data.get("is_error") or not data:
        out["error"] = (words or (p.stderr or "").strip() or (p.stdout or "").strip()
                        or f"exit {p.returncode}")
        return out
    out["ok"], out["words"] = True, words
    return out


def _first_line(text: str) -> str:
    return (text or "").strip().splitlines()[0] if (text or "").strip() else ""


def _flat(text: str) -> str:
    return " ".join((text or "").split())


class AgentPrincipal:
    """
    The pump's backend and the walk's chat answerer, on one model.

    `replied` is the walk's own set, so the walk's filter and this backend
    agree on which asks have their answer.
    """
    name = "agent"

    def __init__(self, conn: sqlite3.Connection, model: str, run: str,
                 replied: set, phase: str = "", night: str = "",
                 runs: Path | None = None, call=call_model, say=print):
        from rota import paths
        self.conn, self.model, self.run = conn, model, run
        self.replied, self.phase, self.night = replied, phase, night
        self.runs = Path(runs) if runs is not None else paths.RUNS
        self.call, self.say = call, say
        self.scratch = self.runs / f"{run}.principal"
        self.record_path = self.runs / f"{run}.principal.jsonl"
        self.failures: dict[str, int] = {}
        self.recent: list[tuple[str, str]] = []
        self.landed: list[tuple[str, str]] = []     # (ask id, landed id)
        self.calls, self.cost = 0, 0.0
        self.last_line = ""
        self._answered: dict[str, str] = {}         # ask id -> answer verb

    # -- the prompt --------------------------------------------------------

    def system_prompt(self) -> str:
        brief = BRIEF.read_text(encoding="utf-8")
        m = re.match(r"sentence (\d+)", self.phase or "")
        line = None
        if m:
            line = re.search(rf"^{m.group(1)}\. (.*)$", brief, re.M)
        if line:
            current = (f"You work on change {m.group(1)} now: "
                       f"{line.group(1).strip()}")
        elif (self.phase or "") == "onboarding":
            current = ("The team still learns your project. You have not "
                       "asked for a change yet.")
        else:
            current = "You work on one of these changes now."
        if self.recent:
            recent = "\n\n".join(
                f"The lead sent:\n{page[:RECENT_CHARS]}\nYou answered: {words}"
                for page, words in self.recent[-RECENT:])
        else:
            recent = "Nothing yet. This is the first page of this walk."
        return brief.replace("{{CURRENT}}", current).replace("{{RECENT}}", recent)

    # -- the call ----------------------------------------------------------

    def _ask_model(self, key: str, verb: str, label: str, page: str,
                   nothing_fails: bool = False) -> str | None:
        """The person's words, or None on a failure. A second failure stops.

        With `nothing_fails`, the words `(nothing)` count as a failure. A page
        always asks something, and a page left unanswered keeps the walk
        waiting on it (frame 41 pass 1 review, the medium finding)."""
        system = self.system_prompt()
        res = self.call(self.model, system, f"{label}\n\n{page}", self.scratch)
        self.calls += 1
        self.cost += float(res.get("total_cost_usd") or 0.0)
        self._write({"kind": "call", "night": self.night, "phase": self.phase,
                     "message_id": key, "verb": verb, "page": page,
                     "words": res.get("words", ""), "ok": bool(res.get("ok")),
                     "error": res.get("error", ""),
                     "duration_ms": res.get("duration_ms"),
                     "total_cost_usd": res.get("total_cost_usd"),
                     "model": self.model})
        words = res.get("words") or ""
        silent = nothing_fails and words.strip() == NOTHING
        if res.get("ok") and words and not silent:
            self.recent.append((page, words))
            return words
        self.failures[key] = self.failures.get(key, 0) + 1
        error = (f"{NOTHING} on a page" if silent
                 else _first_line(res.get("error", "")) or "no words")
        self.say(f"PRINCIPAL ERROR {key}: {error}", flush=True)
        if self.failures[key] >= 2:
            raise PrincipalDown(key)
        return None

    def _write(self, row: dict) -> None:
        row["clock"] = datetime.datetime.now().isoformat(timespec="seconds")
        self.record_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.record_path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(row) + "\n")

    def _log(self, line: str) -> None:
        self.last_line = line
        self.say(line, flush=True)

    # -- pages -------------------------------------------------------------

    def respond(self, ask: Ask) -> Answer | None:
        # Once per ask: a second visit is a deferral (clickI, 2026-09-16).
        if ask.message_id in self.replied:
            return None
        if ask.verb in ("confirm", "present"):
            label = "The lead sends you a page for your approval."
        elif park_ask_batch(ask.message_id or ""):
            label = "The lead sends you a stopped change. Choose a way forward."
        else:
            label = "The lead asks you a question."
        words = self._ask_model(ask.message_id, ask.verb, label,
                                ask.rendered or "", nothing_fails=True)
        if words is None:
            return None
        self.replied.add(ask.message_id)
        lines = (ask.rendered or "").splitlines()
        if ask.verb == "clarify" and len(lines) > 1:
            head = lines[1].strip()[:110]
        else:
            head = (lines[0] if lines else ask.verb)[:90]
        self._log(f"[{ask.message_id}] {ask.verb}: {head}  -> '{_flat(words)}'")
        # The words land as the script's words do. A clarify, park asks
        # included, goes through parse_reply: a `converse` closes a park ask
        # with an empty ruling (design 4a, point 1: night 132, m117).
        if ask.verb in ("confirm", "present"):
            answer = Answer(verb="reply", text=words)
        else:
            answer = parse_reply(ask, words)
        self._answered[ask.message_id] = answer.verb
        return answer

    def pump(self, conn: sqlite3.Connection) -> list[str]:
        """`principal.pump`, then the second record row for each answer.

        The pump returns the new message ids only, so each id's cause names
        the ask it landed on."""
        self._answered = {}
        created = principal_pump(conn, self)
        landed = {}
        for mid in created:
            row = conn.execute("SELECT cause_id FROM messages WHERE id = ?",
                               (mid,)).fetchone()
            if row and row["cause_id"]:
                landed[row["cause_id"]] = mid
        for ask_id, verb in self._answered.items():
            mid = landed.get(ask_id)
            self._write({"kind": "land", "ask_id": ask_id, "as": verb,
                         "landed_id": mid})
            if mid:
                self.landed.append((ask_id, mid))
        return created

    # -- chat --------------------------------------------------------------

    def open_ask_under(self, conn: sqlite3.Connection, message_id: str) -> sqlite3.Row | None:
        """The open principal ask that a Liaison reply answers, through its causes."""
        cur = conn.execute("SELECT cause_id FROM messages WHERE id = ?",
                           (message_id,)).fetchone()
        cause = cur["cause_id"] if cur else None
        for _ in range(CHAIN_CAP):
            if not cause:
                return None
            row = conn.execute(
                "SELECT id, verb, body_refs, status, to_role, cause_id "
                "FROM messages WHERE id = ?", (cause,)).fetchone()
            if row is None:
                return None
            if (row["status"] == "open" and row["to_role"] == "principal"
                    and row["verb"] != "converse"):
                return row
            cause = row["cause_id"]
        return None

    def chat(self, conn: sqlite3.Connection, reply: Ask) -> None:
        """
        Answer one Liaison `converse` turn.

        A question asked back on an open page lands on that page as a
        `reply` (design 4a, point 2). A turn with no page under it gets a
        new principal entry, as the script's path writes. `(nothing)` writes
        no entry.
        """
        if reply.message_id in self.replied:
            return
        under = self.open_ask_under(conn, reply.message_id)
        label = ("The lead asks about your answer to a page."
                 if under is not None else "The lead sends you a chat message.")
        words = self._ask_model(reply.message_id, "converse", label,
                                reply.rendered or "")
        if words is None:
            return
        self.replied.add(reply.message_id)
        self._log(f"[{reply.message_id}] liaison said: "
                  f"{_flat(reply.rendered)[:100]}  -> '{_flat(words)}'")
        conn.execute("UPDATE messages SET status = 'answered' WHERE id = ?",
                     (reply.message_id,))
        if words.strip() == NOTHING:
            self._write({"kind": "land", "ask_id": reply.message_id,
                         "as": "nothing", "landed_id": None})
            return
        if under is not None:
            ask = Ask(message_id=under["id"], verb=under["verb"],
                      refs=json.loads(under["body_refs"] or "[]"))
            # The same door as a page answer: words on a plain clarify close
            # it, as the script's words do (frame 41 pass 1 review).
            answer = parse_reply(ask, words)
            mid = land(conn, ask, answer)
            self._write({"kind": "land", "ask_id": under["id"], "as": answer.verb,
                         "landed_id": mid, "via": reply.message_id})
            if mid:
                self.landed.append((under["id"], mid))
            return
        n = 1 + conn.execute("SELECT COUNT(*) FROM entries WHERE id LIKE 'e_p%'").fetchone()[0]
        seq = 1 + (conn.execute("SELECT MAX(seq) FROM messages").fetchone()[0] or 0)
        ts = 1 + (conn.execute("SELECT MAX(ts_order) FROM entries").fetchone()[0] or 0)
        conn.execute("INSERT INTO entries (id, author, ts_order, text) VALUES (?,'principal',?,?)",
                     (f"e_p{n}", ts, words))
        conn.execute("INSERT INTO messages (id, cause_id, cause_kind, thread_id, from_role, to_role, verb, "
                     "body_refs, seq) VALUES (?,?,'message','t_p1','principal','liaison','converse',?,?)",
                     (f"m_p{n}", reply.message_id, f'["e_p{n}"]', seq))
        self._write({"kind": "land", "ask_id": reply.message_id, "as": "entry",
                     "landed_id": f"m_p{n}"})
        self.landed.append((reply.message_id, f"m_p{n}"))

    # -- the end -----------------------------------------------------------

    def finish(self, quiet: bool = False) -> None:
        """One row per answered ask with the Liaison's next move, and the totals."""
        conn = self.conn
        seen: set = set()
        for ask_id, _ in self.landed:
            if ask_id in seen:
                continue
            seen.add(ask_id)
            replies = [r["id"] for r in conn.execute(
                "SELECT id FROM messages WHERE cause_id = ? AND from_role = 'principal'",
                (ask_id,))]
            # The reply id on a ruling and the cause on an ask-back name the
            # landed reply each one answers, so a night read can join them.
            rulings = [dict(id=r["id"], reply_id=r["reply_id"], per_item=r["per_item"],
                            status=r["status"])
                       for r in conn.execute(
                           "SELECT id, reply_id, per_item, status FROM rulings "
                           "WHERE ask_id = ?", (ask_id,))]
            backs = []
            for rid in replies:
                backs += [dict(id=r["id"], cause_id=r["cause_id"], text=r["body_text"])
                          for r in conn.execute(
                    "SELECT id, cause_id, body_text FROM messages WHERE cause_id = ? "
                    "AND from_role = 'liaison' AND to_role = 'principal' "
                    "AND verb = 'converse'", (rid,))]
            nxt = "ruling" if rulings else ("ask back" if backs else "nothing")
            status = conn.execute("SELECT status FROM messages WHERE id = ?",
                                  (ask_id,)).fetchone()
            self._write({"kind": "next", "ask_id": ask_id, "landed_ids": replies,
                         "next": nxt, "rulings": rulings, "ask_backs": backs,
                         "ask_status": status["status"] if status else None})
        self.say(f"principal: {self.calls} calls, {self.cost:.2f} dollars "
                 f"on {self.model}", flush=True)
        if quiet:
            open_ids = [r["id"] for r in conn.execute(
                "SELECT id FROM messages WHERE status = 'open' AND to_role = 'principal'")
                if r["id"] in self.replied]
            # A quiet walk with answered asks still open is a deferral, not
            # a finished night (design 4a, point 4).
            self.say(f"principal: open asks already answered: "
                     f"{', '.join(open_ids) or 'none'}", flush=True)
