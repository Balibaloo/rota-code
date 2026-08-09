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

from .runner import new_id


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
    per_item: dict[str, str] = field(default_factory=dict)   # ref -> approve|contest|amend


class PrincipalBackend(Protocol):
    name: str

    def respond(self, ask: Ask) -> Answer | None:
        """Answer, or None to defer. Deferring is always allowed."""


class ScriptedClient:
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


class TranscriptClient:
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


class ConsoleClient:                                    # pragma: no cover
    """The human. Same protocol, stdin instead of a script."""

    name = "console"

    def respond(self, ask: Ask) -> Answer | None:
        print(f"\n[{ask.verb}] {ask.rendered or ask.refs}")
        if ask.verb in ("confirm", "present"):
            print("  per-item: 'id=approve id2=contest', 'lgtm' for all, blank to defer")
            raw = input("> ").strip()
            if not raw:
                return None
            if raw.lower() in ("lgtm", "ok", "yes"):
                return Answer(verb="verdict",
                              per_item={r: "approve" for r in ask.refs})
            per_item = dict(
                part.split("=", 1) for part in raw.split() if "=" in part)
            return Answer(verb="verdict", per_item=per_item)
        raw = input("> ").strip()
        return Answer(verb="converse", text=raw) if raw else None


# ---------------------------------------------------------------------------
# The pump: move asks to the principal and answers back onto the frontier.
# ---------------------------------------------------------------------------

def pending_asks(conn: sqlite3.Connection) -> list[Ask]:
    """Open messages addressed to the principal. These never wake anything — the
    principal is not schedulable — so they sit until answered or deferred."""
    return [
        Ask(message_id=r["id"], verb=r["verb"], refs=json.loads(r["body_refs"]))
        for r in conn.execute(
            "SELECT id, verb, body_refs FROM messages "
            "WHERE status = 'open' AND to_role = 'principal' ORDER BY seq")
    ]


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

        msg_id = new_id("m")
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
                (f"utterance:{msg_id}", json.dumps(answer.text)),
            )
            record_utterance(conn, msg_id, answer.text)

        created.append(msg_id)

    return created


def record_utterance(conn: sqlite3.Connection, message_id: str, text: str) -> str:
    """
    Append the principal's words to the transcript mechanically.

    The transcript is the one un-interpreted thing in the system — it exists so
    later interpretations can be checked against something. Routing it through an
    interpreter to get there is self-defeating: asking a model to retype text
    verbatim creates a paraphrase risk with no upside, costs a turn, and in
    practice produced wrong ids and a fabricated second utterance.

    Liaison still *owns* the artefact; the write is attributed to its session.
    It is authored by the system on the role's behalf, the way a receipt is.
    What Liaison keeps is the part that needs judgement: segmentation.
    """
    existing = conn.execute(
        "SELECT id FROM utterances WHERE id = ?", (f"u_{message_id}",)).fetchone()
    if existing:
        return existing["id"]

    uid = f"u_{message_id}"
    nxt = conn.execute(
        "SELECT COALESCE(MAX(ts_order), 0) + 1 n FROM utterances").fetchone()["n"]
    conn.execute(
        "INSERT INTO utterances (id, author, text, ts_order) VALUES (?, 'principal', ?, ?)",
        (uid, text, nxt))
    conn.execute(
        "INSERT INTO artefact_versions(table_name, version) VALUES ('utterances', 1) "
        "ON CONFLICT(table_name) DO UPDATE SET version = version + 1")
    return uid


def verdict_for(conn: sqlite3.Connection, message_id: str) -> dict[str, str]:
    row = conn.execute(
        "SELECT value FROM config WHERE key = ?", (f"verdict:{message_id}",)).fetchone()
    return json.loads(row["value"]) if row else {}


def utterance_for(conn: sqlite3.Connection, message_id: str) -> str:
    row = conn.execute(
        "SELECT value FROM config WHERE key = ?", (f"utterance:{message_id}",)).fetchone()
    return json.loads(row["value"]) if row else ""
