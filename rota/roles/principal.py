"""
The principal seam.

The principal is a node in the graph but not a role in the system — it is a person
at a terminal. Arc tests, however, need a *scripted* principal keyed to step index.
Both must satisfy one protocol, or T2 can never run without retrofitting one.

The protocol is deliberately narrow, and mirrors exactly the edges the graph
grants Liaison toward the principal:

    receive : confirm | clarify | present   (Liaison -> principal)
    emit    : converse | verdict            (principal -> Liaison)

Nothing else crosses. A principal backend cannot write an artefact, cannot address
another role, and cannot see the frontier — it answers questions and holds final
authority, which is the whole of its power.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from typing import Protocol

from ..core.runner import new_id


@dataclass
class Ask:
    """Something Liaison has put to the principal and is waiting on."""
    message_id: str
    verb: str                     # confirm | clarify | present
    refs: list[str] = field(default_factory=list)
    rendered: str = ""


@dataclass
class Answer:
    verb: str                     # converse | verdict
    text: str = ""
    per_item: dict[str, str] = field(default_factory=dict)   # ref -> approve|contest|revise


class PrincipalBackend(Protocol):
    name: str

    def respond(self, ask: Ask) -> Answer | None:
        """Answer, or None to defer. Deferring is always allowed."""


class ScriptedPrincipal:
    """
    Canned answers keyed by step index, for arc tests.

    Deferral is representable — a `None` in the script means the principal saw the
    ask and chose not to answer yet, which the system must survive rather than
    treat as an error.
    """

    name = "scripted"

    def __init__(self, script: list[Answer | None]):
        self.script = list(script)
        self.seen: list[Ask] = []

    def respond(self, ask: Ask) -> Answer | None:
        self.seen.append(ask)
        return self.script.pop(0) if self.script else None


class TranscriptPrincipal:
    """
    Answers from a fixed mapping of verb -> answer, replaying indefinitely.

    Useful for the T1 cases that need *a* principal without caring which one; the
    scripted variant is for arcs where the sequence is the point.
    """

    name = "transcript"

    def __init__(self, answers: dict[str, Answer]):
        self.answers = answers
        self.seen: list[Ask] = []

    def respond(self, ask: Ask) -> Answer | None:
        self.seen.append(ask)
        return self.answers.get(ask.verb)


class ConsolePrincipal:                                    # pragma: no cover
    """The human. Same protocol, stdin instead of a script."""

    name = "console"

    def _read(self) -> str | None:
        """
        None on a closed stdin, which is a deferral rather than a crash.

        Piping a single line in took a whole run down with an `EOFError` raised
        inside `pump` -- the loop reached the point of asking the principal,
        which was the thing being proved, and died on the way to the question.
        """
        try:
            return input("> ").strip()
        except EOFError:
            print("(stdin closed — deferred)")
            return None

    def respond(self, ask: Ask) -> Answer | None:
        print(f"\n[{ask.verb}] {ask.rendered or ask.refs}")
        if ask.verb in ("confirm", "present"):
            print("  per-item: 'id=approve id2=contest', 'lgtm' for all, blank to defer")
            raw = self._read()
            if not raw:
                return None
            if raw.lower() in ("lgtm", "ok", "yes"):
                return Answer(verb="verdict",
                              per_item={r: "approve" for r in ask.refs})
            per_item = dict(
                part.split("=", 1) for part in raw.split() if "=" in part)
            return Answer(verb="verdict", per_item=per_item)
        raw = self._read()
        return Answer(verb="converse", text=raw) if raw else None


# ---------------------------------------------------------------------------
# The pump: move asks to the principal and answers back onto the frontier.
# ---------------------------------------------------------------------------

def pending_asks(conn: sqlite3.Connection) -> list[Ask]:
    """Open questions addressed to the principal.

    `converse` replies from Liaison are displayed, not asked — they carry prose
    rather than a decision, so they do not become a principal gate.
    """
    return [
        Ask(message_id=r["id"], verb=r["verb"],
            refs=json.loads(r["body_refs"]),
            rendered=render_refs(conn, json.loads(r["body_refs"])))
        for r in conn.execute(
            "SELECT id, verb, body_refs FROM messages "
            "WHERE status = 'open' AND to_role = 'principal' "
            "  AND verb != 'converse' ORDER BY seq")
    ]


def pending_replies(conn: sqlite3.Connection) -> list[Ask]:
    """Open Liaison `converse` replies that should be displayed to the principal."""
    return [
        Ask(message_id=r["id"], verb=r["verb"],
            refs=json.loads(r["body_refs"]),
            rendered=r["body_text"] or "")
        for r in conn.execute(
            "SELECT id, verb, body_refs, body_text FROM messages "
            "WHERE status = 'open' AND to_role = 'principal' AND verb = 'converse' "
            "ORDER BY seq")
    ]


def render_refs(conn: sqlite3.Connection, refs: list[str]) -> str:
    """
    Refs as words, for the one reader who cannot follow an id.

    `Ask.rendered` has existed since the beginning and nothing ever filled it,
    so `rendered or refs` fell through to the ids every time and the principal
    -- a person -- was shown `[clarify] ['g_69d1e1', 'g_2d422b']` and asked to
    rule on it. Every role downstream of a ref can dereference it; the principal
    is the only one who cannot, which makes them the only one for whom an
    unresolved ref is the whole message.

    Roles are still forbidden to send prose. This is not prose from a role: it
    is the rows the refs already point at, read out at the edge where ids stop
    working. Law 2 governs what travels between roles, and the principal is not
    one.

    A tempting corollary is false, and was tried: that a question to the
    principal must carry something they themselves said, because the glossary is
    our filing and not theirs. `_bind_send` refused a clarify whose refs were all
    glossary terms for about an hour. `L1-LI-relay-an-answer-without-improving-it`
    expects exactly that message -- two senses of one word, no statement -- and
    had passed 335 of 340 recorded runs. "Which of these two meanings did you
    intend" is a complete question, and this function is why: the senses arrive
    as words. The rule refuted the case, so the rule went.
    """
    from ..core.runner import _resolve_refs

    resolved = _resolve_refs(conn, refs)
    lines = []
    for ref in refs:
        row = resolved.get(ref)
        if not row:
            lines.append(f"  {ref}")
            continue
        # The readable column differs by table and the principal does not need
        # to know which table they are looking at. A term is the one row where
        # two columns are needed: the whole reason two glossary rows reach the
        # principal at all is that the word is the same and the sense is not, so
        # rendering the word alone shows them "delete" and "delete".
        if row.get("term"):
            words = ": ".join(x for x in (row["term"], row.get("sense_short")) if x)
        else:
            words = next((row[k] for k in ("text", "headline") if row.get(k)), "")
        lines.append(f"  {ref}: {words}" if words else f"  {ref}")
    return "\n".join(lines)


def pump(conn: sqlite3.Connection, backend: PrincipalBackend) -> list[str]:
    """
    Offer every pending ask to the principal; land any answers as new messages.

    Returns the ids of messages created. A deferred ask stays open — that is the
    agenda tick's material next time the principal shows up, and it is why deferral
    costs nothing now and reappears at the lineage's gates later.
    """
    created: list[str] = []

    for ask in pending_asks(conn):
        answer = backend.respond(ask)
        if answer is None:
            continue                       # deferral is always allowed

        msg_id = new_id("m", conn)
        seq = conn.execute(
            "SELECT COALESCE(MAX(seq), 0) + 1 n FROM messages").fetchone()["n"]
        thread = conn.execute(
            "SELECT thread_id FROM messages WHERE id = ?", (ask.message_id,)
        ).fetchone()["thread_id"]

        refs = list(answer.per_item) or ask.refs
        conn.execute(
            "INSERT INTO messages (id, cause_id, cause_kind, thread_id, from_role, "
            "to_role, verb, body_refs, seq) "
            "VALUES (?, ?, 'message', ?, 'principal', 'liaison', ?, ?, ?)",
            (msg_id, ask.message_id, thread, answer.verb, json.dumps(refs), seq),
        )
        conn.execute("UPDATE messages SET status = 'answered' WHERE id = ?",
                     (ask.message_id,))

        # Per-item verdicts travel as refs; the ruling itself is recorded so
        # Liaison can relay it without re-asking.
        if answer.per_item:
            conn.execute(
                "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                (f"verdict:{msg_id}", json.dumps(answer.per_item)),
            )
        if answer.text:
            conn.execute(
                "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                (f"entry:{msg_id}", json.dumps(answer.text)),
            )
            record_entry(conn, msg_id, answer.text)

        created.append(msg_id)

    return created


def record_entry(conn: sqlite3.Connection, message_id: str, text: str) -> str:
    """
    Append the principal's words to the transcript mechanically.

    The transcript is the one un-interpreted thing in the system — it exists so
    later interpretations can be checked against something. Routing it through an
    interpreter to get there is self-defeating: asking a model to retype text
    verbatim creates a paraphrase risk with no upside, costs a turn, and in
    practice produced wrong ids and a fabricated second entry.

    Liaison still *owns* the artefact; the write is attributed to its session.
    It is authored by the system on the role's behalf, the way a receipt is.
    What Liaison keeps is the part that needs judgement: segmentation.
    """
    existing = conn.execute(
        "SELECT id FROM entries WHERE id = ?", (f"e_{message_id}",)).fetchone()
    if existing:
        return existing["id"]

    uid = f"e_{message_id}"
    nxt = conn.execute(
        "SELECT COALESCE(MAX(ts_order), 0) + 1 n FROM entries").fetchone()["n"]
    conn.execute(
        "INSERT INTO entries (id, author, text, ts_order) VALUES (?, 'principal', ?, ?)",
        (uid, text, nxt))
    conn.execute(
        "INSERT INTO artefact_versions(table_name, version) VALUES ('entries', 1) "
        "ON CONFLICT(table_name) DO UPDATE SET version = version + 1")
    return uid


def verdict_for(conn: sqlite3.Connection, message_id: str) -> dict[str, str]:
    row = conn.execute(
        "SELECT value FROM config WHERE key = ?", (f"verdict:{message_id}",)).fetchone()
    return json.loads(row["value"]) if row else {}


def entry_for(conn: sqlite3.Connection, message_id: str) -> str:
    """
    What the principal said, from the table that owns it.

    This read a `config` key, `entry:<message_id>`, written by exactly one of
    the two paths that record an entry. The reply path above writes it.
    `talk.open_with` -- which is intake, the CLI and the TUI -- writes the
    `entries` row and not the key, so **the first thing anybody typed was
    invisible and every follow-up was visible.**

    What that looked like from outside: Liaison woken to segment a requirement,
    shown three empty lists and no sentence, answering "Hello! What would you
    like to build?" -- the correct response to an empty message. It read as a
    role choosing to chat, and it took `L1-LI-segment` and
    `L1-LI-no-report-no-question` to 0/5.

    `record_entry` names the row `e_<message_id>`, so the join needs nothing
    stored. One fact in one place: the config key is still read as a fallback
    for databases written before this, and it is no longer the authority.
    """
    row = conn.execute(
        "SELECT text FROM entries WHERE id = ?", (f"e_{message_id}",)).fetchone()
    if row is not None and row["text"]:
        return row["text"]

    legacy = conn.execute(
        "SELECT value FROM config WHERE key = ?", (f"entry:{message_id}",)).fetchone()
    return json.loads(legacy["value"]) if legacy else ""
