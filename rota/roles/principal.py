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
    # The rulable rows in the order the page shows them. "2: no" means the
    # second numbered line, not the second ref.
    order: list[str] = field(default_factory=list)


@dataclass
class Answer:
    verb: str                     # converse | verdict | reply
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
        print(f"\n{ask.rendered or ask.refs}")
        if ask.verb in ("confirm", "present"):
            print(REPLY_HELP)
        raw = self._read()
        if not raw:
            return None
        return parse_reply(ask, raw)


REPLY_HELP = ("  Reply in your own words. The Liaison reads the reply against "
              "the page and lands it, or asks. Blank = decide later.")


def parse_reply(ask: Ask, text: str) -> Answer:
    """
    A person's words to an ask, as the Answer that carries them.

    No parser reads the words. Ruled 2026-09-10: the Liaison is the natural
    language seat, and a keyword list ("ok", "lgtm") was the layer that told
    a person "no" is not a reply. A reply to a confirm or a present lands as
    a `reply`: the ask stays open, the words go to the Liaison in `landing`
    mode, and the Liaison records the ruling it read (`rulings.rule`) or
    asks back. A reply to a clarify is the answer, as before.

    Scripts do not come through here. A scripted principal builds a verdict
    `Answer` with `per_item` and lands it through the same door.
    """
    raw = text.strip()
    if ask.verb not in ("confirm", "present"):
        return Answer(verb="converse", text=raw)
    return Answer(verb="reply", text=raw)


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
            rendered=(page := render_page(conn, r["verb"],
                                          json.loads(r["body_refs"]),
                                          r["body_text"]))[0],
            order=page[1])
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


def render_state(conn: sqlite3.Connection) -> str:
    """
    Where the run is, in words, for the person who waits on it.

    Every seat could say what the machine did: wake kinds, role names, row
    counts. No seat could say what happened. Measured as the principal
    (tips9, 2026-09-04): a walk built the code, failed six of seven tests,
    climbed the escalation ladder, and went quiet. Nothing was pending, so
    nothing was shown. A stopped run and a thinking run were the same picture.

    The state is composed here once, like an ask. First what waits on you,
    because that line asks for something. Then what shipped. Then what is
    stuck and what would move it. Read from the rows, so it is true of a
    database opened cold.
    """
    asks = pending_asks(conn)
    if asks:
        head = ("Waiting on you." if len(asks) == 1
                else f"Waiting on you: {len(asks)} things. The first is:")
        return head + chr(10) + asks[0].rendered

    def count(sql):
        row = conn.execute(sql).fetchone()
        return row[0] if row else 0

    merged = count("SELECT COUNT(*) FROM batches WHERE status = 'merged'")
    running = count("SELECT COUNT(*) FROM batches WHERE status = 'running'")
    pending = count("SELECT COUNT(*) FROM batches WHERE status = 'pending'")
    approved = count("SELECT COUNT(*) FROM items WHERE approval = 'approved'")

    out: list[str] = []
    if merged:
        out.append(f"Done: {merged} change{'s' if merged > 1 else ''} built, "
                   "tested and merged.")
    # A tick tried past its cap and quarantined is the team giving up. It
    # outranks "building": on tipsH (2026-09-09) the Critic reviewed six times
    # without a verdict, was quarantined, the batch stayed running, and the
    # seat said "Building" because nothing else was pending.
    gave_up = [r["tick_key"] for r in conn.execute(
        "SELECT tick_key FROM tick_attempts WHERE quarantined = 1 "
        "AND tick_key NOT LIKE '%tick:constraint_zero%'")]
    if gave_up:
        what = ", ".join(
            f"{k.split('|')[1].replace('tick:', '')} for "
            f"{k.split('|')[2] or 'the whole project'}" for k in gave_up)
        out.append(f"Stuck. The team gave up on: {what}. Nothing waits on you, "
                   "and nothing moves until that is cleared. Tell me what to "
                   "change.")
        return chr(10).join(out)
    if running or pending:
        # At the batch's head commit, the harness's own notion of "now". The
        # first version picked the latest run by MAX(id), and ids are strings:
        # 'tr9' sorts after 'tr11', so a run that had gone green still read as
        # "1 test failing" (tipsH, 2026-09-09).
        failing = count(
            "SELECT COUNT(DISTINCT t.test_id) FROM test_runs t "
            "JOIN batches b ON b.id = t.batch_id "
            "WHERE b.status = 'running' AND t.result != 'pass' "
            "AND t.commit_sha = b.head_commit")
        if failing:
            out.append(
                f"Stuck: the code is written, but {failing} test"
                f"{'s are' if failing > 1 else ' is'} still failing, and the "
                "team has run out of things to try. Tell me what to change, "
                "or what the tests should check.")
        else:
            out.append(f"Building: {running + pending} change"
                       f"{'s' if running + pending > 1 else ''} in progress.")
    if not out:
        if approved:
            out.append(f"Nothing waits on you and nothing is building. "
                       f"{approved} thing{'s' if approved > 1 else ''} approved so far.")
        else:
            out.append("Nothing waits on you and nothing is building. "
                       "Tell me what you want. I take it from there.")
    return chr(10).join(out)


def render_ask(conn: sqlite3.Connection, verb: str, refs: list[str],
               question: str | None = None) -> str:
    """The page alone. `render_page` also returns the numbered rows' order."""
    return render_page(conn, verb, refs, question)[0]


def render_page(conn: sqlite3.Connection, verb: str, refs: list[str],
                question: str | None = None) -> tuple[str, list[str]]:
    """
    An ask as a message to a person, and the rows it numbers, in order.

    The page and the input are one contract. The page shows no ids, so the
    input cannot ask for ids. Each rulable row gets a number. A reply of
    "2: <words>" means the second numbered line. `parse_reply` reads the
    same order this returns.

    Measured as the principal (2026-09-04): asks arrived as a verb and a list
    of ids, and a newcomer could not tell what was asked or what approving
    would start. Then the ids were removed from the page while the parser
    still demanded them, and the only reply that worked was "lgtm". This
    function and `parse_reply` fix both faults together.
    """
    from ..core.runner import _resolve_refs
    from ..onboarding.boot import ZERO

    resolved = _resolve_refs(conn, refs)
    said: list[tuple[str, str]] = []
    account: list[tuple[str, str]] = []
    does: list[tuple[str, str]] = []
    does_not: list[tuple[str, str]] = []
    terms: list[tuple[str, str]] = []
    assumed: list[tuple[str, str]] = []
    touches: list[tuple[str, str]] = []
    other: list[tuple[str, str]] = []
    zero = False
    for ref in refs:
        row = resolved.get(ref)
        if not row:
            words = touch_words(conn, ref)
            if words:
                touches.append((ref, words))
            continue
        if row.get("id") == ZERO:
            zero = True
            continue
        if row.get("term"):
            terms.append((ref, ": ".join(
                x for x in (row["term"], row.get("sense_short")) if x)))
            continue
        if row.get("default_taken"):
            assumed.append((ref, row["default_taken"]))
            continue
        text = next((row[k] for k in ("text", "headline", "body") if row.get(k)), "")
        kind = row.get("kind")
        if kind == "in_scope":
            (account if row.get("id") == "how_it_works" else does).append((ref, text))
        elif kind == "out_of_scope":
            does_not.append((ref, text))
        elif "approval" not in row and row.get("status") in (
                "proposed", "ratified", "superseded", "contradicted", "clarified"):
            said.append((ref, text))
        elif text:
            other.append((ref, text))

    out: list[str] = []
    order: list[str] = []

    def numbered(rows: list[tuple[str, str]], quote: bool = False) -> None:
        for ref, text in rows:
            order.append(ref)
            shown = f'"{text}"' if quote else text
            out.append(f"  {len(order)}. {shown}")

    if verb == "confirm":
        n = len(said) or len(other) or len(refs)
        out.append("Did I hear you right? I have taken this as "
                   + ("one request:" if n == 1 else f"{n} separate requests:"))
        numbered(said, quote=True)
        numbered(other)
        out.append("Reply 'ok' if that is what you meant. Reply with words if "
                   "it is wrong. After 'ok', I work out what to build and show "
                   "you the plan before anything is written.")
    elif verb == "present" and touches:
        out.append("Before I build this, here is what I expect to touch.")
        numbered(does + account)
        numbered(touches)
        if zero:
            out.append("  Some of that code has not been read yet. I cannot say "
                       "what a change there might break.")
        out.append("This is a prediction, not a promise. Reply 'ok' to go "
                   "ahead. Reply with words if something concerns you.")
    elif verb == "present" and zero and not (said or account or does or does_not):
        out.append("Nothing here has been read yet, so I cannot say what a "
                   "change might break. That is normal for a new or unread "
                   "project.")
        out.append("Reply 'ok' to go ahead. I will flag anything I touch that "
                   "I have not read.")
    elif verb == "present":
        out.append("Here is what I understand you want, on one page.")
        if said:
            out.append("You asked:")
            numbered(said, quote=True)
        if account:
            out.append("What we are building:")
            numbered(account)
        if does:
            out.append("It would:")
            for ref, text in does:
                numbered([(ref, text)])
                near = near_code(conn, text)
                if near:
                    out.append("     code that names these words: " + ", ".join(near))
        if does_not:
            out.append("It would not:")
            numbered(does_not)
        if assumed:
            out.append("Where you did not say, I assumed:")
            numbered(assumed)
        if terms:
            out.append("A word that means more than one thing here:")
            numbered(terms)
        numbered(other)
        if zero:
            out.append("Some of this code has not been read yet. I will flag "
                       "anything I touch there.")
        out.append("Reply in your own words. 'ok' approves all of this and "
                   "starts building. Name a line to correct only that line. "
                   "Ask, if something here is unclear.")
    elif verb == "clarify":
        out.append("I need one thing from you before I can continue.")
        if question:
            out.append(f"  {question.strip()}")
        context = [t for _, t in said + account + does + does_not + assumed
                   + terms + other + touches]
        if context:
            out.append("This is about:")
            out += [f"  - {c}" for c in context]
        out.append("Reply in a sentence. I take it from there.")
    else:
        out += [f"  {t}" for _, t in said + account + does + does_not + assumed
                + terms + touches + other]
    return chr(10).join(out), order


STOP_WORDS = frozenset("""
the a an and or of to in on for with from by at as is are be can could
should will would that this these those it its their there user users
program system when where what which who how not no into over under
""".split())


def near_code(conn, text: str, cap: int = 3) -> list[str]:
    """
    The files whose symbols carry a word of this item's text.

    P4 piece 2 (plans/p4-scope-disclosure.md), in its mechanical form: at
    signoff nothing is sliced, so the Architect's guess is judgement the 8B
    tier has not earned. This is not a guess. It is the index, read for the
    item's own words, and the page labels it as that. A symbol `Invoice`
    names the word "invoices", and the file that defines it is where a
    change about invoices is likely to look.
    """
    words = set()
    for raw in text.lower().split():
        w = "".join(ch for ch in raw if ch.isalnum() or ch == "_")
        if len(w) >= 4 and w not in STOP_WORDS:
            words.add(w)
            if w.endswith("s"):
                words.add(w[:-1])
    if not words:
        return []
    hits: dict[str, int] = {}
    for row in conn.execute(
            "SELECT grain FROM code_index WHERE grain_kind = 'symbol'"):
        grain = row["grain"]
        path, _, name = grain.partition("::")
        lname = name.lower()
        if any(w in lname for w in words):
            hits[path] = hits.get(path, 0) + 1
    ranked = sorted(hits.items(), key=lambda kv: (-kv[1], kv[0]))
    return [path for path, _ in ranked[:cap]]


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
    # Words, not a ruling. The ask stays open: the Liaison reads the words
    # in `landing` mode and records the ruling, and the ruling lands here
    # through `apply_rulings` after that session commits. The reply is a
    # principal `converse` whose cause is the ask, which is what keys the
    # mode. The words go on the message and into the transcript.
    if answer.verb == "reply":
        still_open = conn.execute(
            "SELECT 1 FROM messages WHERE id = ? AND status = 'open'",
            (ask.message_id,)).fetchone()
        if not still_open or not answer.text.strip():
            return None
        msg_id = new_id("m", conn)
        seq = conn.execute(
            "SELECT COALESCE(MAX(seq), 0) + 1 n FROM messages").fetchone()["n"]
        thread = conn.execute(
            "SELECT thread_id FROM messages WHERE id = ?", (ask.message_id,)
        ).fetchone()["thread_id"]
        conn.execute(
            "INSERT INTO messages (id, cause_id, cause_kind, thread_id, from_role, "
            "to_role, verb, body_refs, body_text, seq, status) "
            "VALUES (?, ?, 'message', ?, 'principal', 'liaison', 'converse', "
            "?, ?, ?, 'open')",
            (msg_id, ask.message_id, thread, json.dumps(ask.refs),
             answer.text.strip(), seq))
        record_entry(conn, msg_id, answer.text.strip())
        return msg_id

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

    # The ruling lands on the rows it names, here, at the keypress.
    #
    # The owner used to apply it. The owner was woken with the verdict and
    # told to write the state for each ruling, from a lookup table in its own
    # brief. Measured as the principal (tips7, tips8, 2026-09-04): given five
    # refs, the model applied two, invented a third on a statement, and
    # dropped `how_it_works`. The account never left `draft`. `tick_signoff`
    # fired again. The principal got the same page again, with no exit.
    #
    # The state that follows from a ruling is not a judgement. So the state
    # lands here. The relay still goes out for the judgement half: an
    # amendment the words demand, and the order of the approved items.
    # `approval_ver` is stamped against the current version. That keeps law
    # 9 true: no batch schedules unless its approval postdates its last
    # amendment.
    for ref, ruling in per_item.items():
        if ref in closed_here:
            continue
        state = {"approve": "approved", "contest": "contested",
                 "revise": "contested"}.get(ruling)
        if state is None:
            continue
        conn.execute(
            "UPDATE items SET approval = ?, approval_ver = version "
            "WHERE id = ? AND approval IS NOT ?", (state, ref, state))

    refs = [r for r in (list(per_item) or ask.refs) if r not in closed_here]
    # A page whose every row closed at the keypress leaves nothing for an
    # owner to do. The verdict is the record and lands answered. Relayed,
    # it woke the Terminologist with a ruling on a done row; it adopted the
    # ledger id, was refused, logged the refusal as a new assumption, and
    # the agenda put that row to the principal: 36 rounds (tipsQ,
    # 2026-09-09).
    approved_here = [r for r in closed_here if per_item.get(r) == "approve"]
    settled = per_item and not refs and closed_here and len(approved_here) == len(closed_here)
    conn.execute(
        "INSERT INTO messages (id, cause_id, cause_kind, thread_id, from_role, "
        "to_role, verb, body_refs, seq, status) "
        "VALUES (?, ?, 'message', ?, 'principal', 'liaison', ?, ?, ?, ?)",
        (msg_id, ask.message_id, thread, answer.verb, json.dumps(refs), seq,
         "answered" if settled else "open"),
    )

    # Per-item verdicts travel as refs; the ruling itself is recorded so
    # Liaison can relay it without re-asking. An approved row closed here is
    # not in it: a taken default needs no relay. A contested one stays: its
    # author has to hear the words.
    remaining = {r: v for r, v in per_item.items() if r not in approved_here}
    if remaining:
        conn.execute(
            "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
            (f"verdict:{msg_id}", json.dumps(remaining)),
        )
    if answer.text:
        conn.execute(
            "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
            (f"entry:{msg_id}", json.dumps(answer.text)),
        )
        record_entry(conn, msg_id, answer.text)
    return msg_id


def apply_rulings(conn: sqlite3.Connection) -> list[str]:
    """
    Land every ruling the Liaison has read and nothing has landed yet.

    Called after each session commits. The Liaison's `rulings.rule` stages
    a row; this turns the row into the verdict through `land`, the one door
    a ruling has. A ruling whose ask closed meanwhile is `stale`: the page
    the principal answered is gone, and a ruling on a page nobody sees lands
    nothing. Returns the verdict message ids created.
    """
    created: list[str] = []
    for r in conn.execute(
            "SELECT id, ask_id, per_item, words FROM rulings "
            "WHERE status = 'open' ORDER BY rowid").fetchall():
        ask_row = conn.execute(
            "SELECT id, verb, body_refs, body_text FROM messages WHERE id = ?",
            (r["ask_id"],)).fetchone()
        msg_id = None
        if ask_row is not None:
            ask = Ask(message_id=ask_row["id"], verb=ask_row["verb"],
                      refs=json.loads(ask_row["body_refs"] or "[]"))
            msg_id = land(conn, ask, Answer(
                verb="verdict", per_item=json.loads(r["per_item"] or "{}"),
                text=r["words"] or ""))
        closed = conn.execute(
            "SELECT status FROM messages WHERE id = ?", (r["ask_id"],)).fetchone()
        landed = msg_id is not None or (closed and closed["status"] != "open")
        conn.execute(
            "UPDATE rulings SET status = ?, verdict_id = ? WHERE id = ?",
            ("landed" if landed else "stale", msg_id, r["id"]))
        if msg_id:
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
