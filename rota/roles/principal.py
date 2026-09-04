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
            rendered=render_ask(conn, r["verb"], json.loads(r["body_refs"]),
                                r["body_text"]))
        for r in conn.execute(
            "SELECT id, verb, body_refs, body_text FROM messages "
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


def render_ask(conn: sqlite3.Connection, verb: str, refs: list[str],
               question: str | None = None) -> str:
    """
    An ask, as a message to a person: what is being asked, why, and what
    happens when they answer.

    `render_refs` reads the rows out; this is the page around them. Measured
    on the tips runs (2026-09-03), as the principal: every ask arrived as a
    verb name and a list of ids -- "confirm: s1: tip calculator pls",
    "present: k0: Nobody has read this area yet...", "l_a69ad6edd4: assumed:
    ..." -- and a newcomer could not tell what was being asked, what
    approving would start, or which of the words were theirs. Liaison's brief
    has the translate rule ("the principal does not know your roles'
    vocabulary") and the mechanical presents route around it, because the
    system composes them. So the composing happens here, once, for every
    seat: no ids in the prose (the CLI keeps them in its header for `rota
    sign`), the principal's own words quoted as theirs, the account before
    the behaviours, what was assumed in its own place, and one closing line
    that says what the answer does. SEAT.md's rules: asked specifically,
    the bargain stated, never a form.
    """
    from ..core.runner import _resolve_refs
    from ..onboarding.boot import ZERO

    resolved = _resolve_refs(conn, refs)
    said: list[str] = []
    account: list[str] = []
    does: list[str] = []
    does_not: list[str] = []
    terms: list[str] = []
    assumed: list[str] = []
    touches: list[str] = []
    other: list[str] = []
    zero = False
    for ref in refs:
        row = resolved.get(ref)
        if not row:
            words = touch_words(conn, ref)
            if words:
                touches.append(words)
            continue
        if row.get("id") == ZERO:
            zero = True
            continue
        if row.get("term"):
            terms.append(": ".join(x for x in (row["term"], row.get("sense_short")) if x))
            continue
        if row.get("default_taken"):
            assumed.append(row["default_taken"])
            continue
        text = next((row[k] for k in ("text", "headline", "body") if row.get(k)), "")
        kind = row.get("kind")
        if kind == "in_scope":
            (account if row.get("id") == "how_it_works" else does).append(text)
        elif kind == "out_of_scope":
            does_not.append(text)
        elif "approval" not in row and row.get("status") in (
                "proposed", "ratified", "superseded", "contradicted", "clarified"):
            said.append(text)
        elif text:
            other.append(text)

    out: list[str] = []
    if verb == "confirm":
        n = len(said) or len(other) or len(refs)
        out.append("Did I hear you right? I've taken this as "
                   + ("one request:" if n == 1 else f"{n} separate requests:"))
        out += [f'  "{s}"' for s in said] or [f"  {o}" for o in other]
        out.append("Approve if that's what you meant, or tell me what's wrong. "
                   "Once you approve, I'll work out what to build and show you "
                   "before anything is written.")
    elif verb == "present" and touches:
        out.append("Before I build this, here's what I expect to touch.")
        for d in does + account:
            out.append(f"  For: {d}")
        out += [f"  {t}" for t in touches]
        if zero:
            out.append("  Some of that code hasn't been read yet, so I can't say "
                       "what a change there might break.")
        out.append("This is a prediction, not a promise. Approve to go ahead, "
                   "or say what concerns you.")
    elif verb == "present" and zero and not (said or account or does or does_not):
        out.append("Nothing here has been read yet, so I can't say what a change "
                   "might break. That's normal for a new or unread project.")
        out.append("Approve to go ahead; I'll flag anything I touch that I "
                   "haven't read.")
    elif verb == "present":
        out.append("Here's what I understand you want, on one page.")
        if said:
            out.append("You asked:")
            out += [f'  "{s}"' for s in said]
        if account:
            out.append("What we're building:")
            out += [f"  {a}" for a in account]
        if does:
            out.append("It would:")
            out += [f"  - {d}" for d in does]
        if does_not:
            out.append("It would not:")
            out += [f"  - {d}" for d in does_not]
        if assumed:
            out.append("Where you didn't say, I assumed:")
            out += [f"  - {a}" for a in assumed]
        if terms:
            out.append("A word that means more than one thing here:")
            out += [f"  - {t}" for t in terms]
        if other:
            out += [f"  {o}" for o in other]
        if zero:
            out.append("Some of this code hasn't been read yet; I'll flag anything "
                       "I touch there.")
        out.append("Approve to start building. Or say what's wrong in your own "
                   "words, and I'll correct it before anything is built.")
    elif verb == "clarify":
        out.append("I need one thing from you before I can continue.")
        if question:
            out.append(f"  {question.strip()}")
        context = said + account + does + does_not + assumed + terms + other + touches
        if context:
            out.append("This is about:")
            out += [f"  - {c}" for c in context]
        out.append("A sentence is enough; I'll take it from there.")
    else:
        out += [f"  {x}" for x in said + account + does + does_not + assumed + terms + touches + other]
    return chr(10).join(out)


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
            # A batch is the one ref with no words of its own: what it means
            # to the seat is its predicted touch, read out here at the edge
            # the same way a term's two senses are (P4, 2026-09-03).
            words = touch_words(conn, ref)
            lines.append(f"  {ref}: {words}" if words else f"  {ref}")
            continue
        # The readable column differs by table and the principal does not need
        # to know which table they are looking at. A term is the one row where
        # two columns are needed: the whole reason two glossary rows reach the
        # principal at all is that the word is the same and the sense is not, so
        # rendering the word alone shows them "delete" and "delete".
        if row.get("term"):
            words = ": ".join(x for x in (row["term"], row.get("sense_short")) if x)
        elif row.get("default_taken"):
            # An assumption, read out as one: the sentence a desk wrote where
            # the principal's words were silent, and what it costs to be wrong.
            words = f"assumed: {row['default_taken']}"
        else:
            words = next((row[k] for k in ("text", "headline") if row.get(k)), "")
        lines.append(f"  {ref}: {words}" if words else f"  {ref}")
    return "\n".join(lines)


def touch_words(conn: sqlite3.Connection, batch_id: str) -> str:
    """The batch's predicted touch as words, or '' when the id is no batch."""
    from ..core.lifecycle import touch_set

    t = touch_set(conn, batch_id)
    if not t:
        return ""
    item = t["item"]
    parts = ["the batch for " + item["id"]
             + (f" ({item['text']})" if item.get("text") else "")]
    parts.append("expected to touch "
                 + (", ".join(t["expected"]) if t["expected"] else "nothing named"))
    if t["possible"]:
        parts.append("might touch " + ", ".join(t["possible"]))
    if t["unsurveyed"]:
        parts.append("unsurveyed ground: " + ", ".join(t["unsurveyed"]))
    if t["commitments"]:
        parts.append("commitments: " + ", ".join(
            f"{c['id']} {c['headline']} (bound to {c['bound_to']})"
            for c in t["commitments"]))
    return "; ".join(parts)


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
        msg_id = land(conn, ask, answer)
        if msg_id:
            created.append(msg_id)

    return created


def land(conn: sqlite3.Connection, ask: Ask, answer: Answer) -> str | None:
    """
    Land one answer as a message, if the ask is still open.

    The answer's door, split from `pump` so it can be hurt on its own
    (`test_chaos_confirm.py`, loop 3's injuries). Two principals can read the
    same open present -- two consoles, one checkout -- and both answer it; the
    first to land wins and the second is refused here rather than stacked,
    because two rulings on one present relay two rulings to the owner, and
    which one it applied would be decided by arrival order. And a present the
    world moved past is `superseded` at the door every present lands through
    (`db.py`, where a session's messages are inserted: a later present of the
    same row is the one to answer), so it is no longer open, and a ruling for
    it from a screen that never refreshed lands nothing -- it would approve a
    version of the row the principal never saw. Returns the new message id,
    or None when the ask was no longer open.
    """
    closed = conn.execute(
        "UPDATE messages SET status = 'answered' "
        "WHERE id = ? AND status = 'open'", (ask.message_id,)).rowcount
    if not closed:
        return None

    # A touch note is read, not ruled on (P4, R7: nothing waits on it). The
    # batch's ref is never a row the principal rules, so it leaves the
    # ruling; what is left, if it is all approve, is an acknowledgement --
    # the note closes and wakes nobody. A contest or revise on the item lands
    # as any ruling does: the owner amends it, the version moves, and the
    # revocation is what ends the batch (loop 6) -- the lever the note is for.
    per_item = dict(answer.per_item or {})
    if ask.verb == "present" and answer.verb == "verdict":
        batches = {r["id"] for r in conn.execute("SELECT id FROM batches")}
        if batches & set(ask.refs):
            per_item = {k: v for k, v in per_item.items() if k not in batches}
            if all(v == "approve" for v in per_item.values()):
                return None

    msg_id = new_id("m", conn)
    seq = conn.execute(
        "SELECT COALESCE(MAX(seq), 0) + 1 n FROM messages").fetchone()["n"]
    thread = conn.execute(
        "SELECT thread_id FROM messages WHERE id = ?", (ask.message_id,)
    ).fetchone()["thread_id"]

    # A ruling on an assumption closes here, at the keypress, whichever way
    # it went: a decision row under the principal's name that resolves the
    # ledger entry -- the two writes `decisions.author` makes, made by the one
    # author a ruling has. Law 11 (an entry is resolved by a decision that
    # names it, in the same commit, and by nothing else) and SEAT.md's
    # contract (a decided row enters the record only from a keypress).
    # Approve takes the default. Contest overrules it, with the words, and
    # contests the row the assumption was about: the principal rejected the
    # reading, so the row is amended by its owner through the contested
    # loop, with `principal_said` in front of it. Either way the ledger id
    # leaves the relay's refs -- the owner has nothing to apply to it, and
    # told to `set_approval` a ledger id it would only be refused. Measured
    # first the other way (2026-09-03): `decisions.author` handed to the
    # relay mode drew fourteen decisions a session, five of five, on the
    # plain approve case too. The tool in the list was the invitation.
    # (`per_item` is the ruling less any batch ref -- see the touch-note
    # door above.)
    closed_here: list[str] = []
    for ref, ruling in list(per_item.items()):
        if ruling not in ("approve", "contest", "revise"):
            continue
        row = conn.execute(
            "SELECT id, about_ref, default_taken FROM ledger "
            "WHERE id = ? AND status = 'open'", (ref,)).fetchone()
        if row is None:
            continue
        if ruling == "approve":
            text = f"default taken at signoff: {row['default_taken']}"
        else:
            said = answer.text.strip() if answer.text else "contested at signoff"
            text = f"overruled at signoff: {said} (was assumed: {row['default_taken']})"
            per_item[row["about_ref"]] = "contest"
        conn.execute(
            "INSERT INTO decisions (id, author, text, refs, resolves_ledger) "
            "VALUES (?, 'principal', ?, ?, ?)",
            (new_id("d", conn), text, json.dumps([row["about_ref"]]), ref))
        conn.execute("UPDATE ledger SET status = 'resolved' WHERE id = ?", (ref,))
        closed_here.append(ref)

    refs = [r for r in (list(per_item) or ask.refs) if r not in closed_here]
    conn.execute(
        "INSERT INTO messages (id, cause_id, cause_kind, thread_id, from_role, "
        "to_role, verb, body_refs, seq) "
        "VALUES (?, ?, 'message', ?, 'principal', 'liaison', ?, ?, ?)",
        (msg_id, ask.message_id, thread, answer.verb, json.dumps(refs), seq),
    )

    # Per-item verdicts travel as refs; the ruling itself is recorded so
    # Liaison can relay it without re-asking.
    if per_item:
        conn.execute(
            "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
            (f"verdict:{msg_id}", json.dumps(per_item)),
        )
    if answer.text:
        conn.execute(
            "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
            (f"entry:{msg_id}", json.dumps(answer.text)),
        )
        record_entry(conn, msg_id, answer.text)
    return msg_id


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
