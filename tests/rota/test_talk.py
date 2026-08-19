"""
The talking seam.

`ConsolePrincipal` has existed since the principal seam was written and was
wired to nothing, called by nothing, and covered by nothing. A capability
nobody can reach is indistinguishable from one that does not work, so these
cover the join rather than the parts: intake lands where the system looks for
it, and a principal backend reaches the loop.
"""
from __future__ import annotations

import json
import sqlite3

import pytest

from rota.core.db import init_db
from rota.tools import talk


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "talk.db")


def test_connect_readonly_rejects_writes(tmp_path):
    """The cockpit may read while the TUI remains the only writer."""
    from rota.core.db import connect_readonly

    db = init_db(tmp_path / "read_only.db")
    db.close()

    ro = connect_readonly(tmp_path / "read_only.db")
    try:
        with pytest.raises(sqlite3.OperationalError):
            ro.execute(
                "INSERT INTO messages (id, from_role, to_role, verb, status, body_refs) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                ("m1", "principal", "liaison", "converse", "open", "[]"),
            )
    finally:
        ro.close()


def test_the_seat_starts_idle_without_saying_so_in_the_run(tmp_path):
    """
    The intent survives -- a new seat waits for you rather than starting to
    turn the crank -- and where it is recorded has moved, because the old place
    was the run.

    Writing `run_state = "stopping"` on open put a fact about *this window*
    into state that `loop.step` reads on every session and every seat shares.
    So opening a second seat halted the loop the first was driving. The seat
    holds its own idleness now, and reads the run's state rather than setting
    it.
    """
    from rota.cockpit import tui
    from rota.core import config

    app = tui.RotaApp(tmp_path / "ui.db", "llama3.1:8b")
    assert app.driving is False
    assert config.get(app.conn, "run_state") == config.SETTINGS["run_state"].default


def test_the_first_sentence_lands_as_an_entry_and_a_message(db):
    """
    Both, and for different reasons: the entry is the record Liaison segments
    statements out of, and every statement keeps a span back into it. The
    message is the only thing that wakes anybody.
    """
    msg_id = talk.open_with(db, "let people export their invoices")

    entry = db.execute("SELECT id, author, text FROM entries").fetchone()
    assert entry["author"] == "principal"
    assert entry["text"] == "let people export their invoices"

    msg = db.execute("SELECT * FROM messages WHERE id = ?", (msg_id,)).fetchone()
    assert (msg["from_role"], msg["to_role"], msg["verb"]) == \
        ("principal", "liaison", "converse")
    assert msg["status"] == "open", "intake that wakes nobody is a transcript"
    assert json.loads(msg["body_refs"]) == [entry["id"]], \
        "the words and the record of them must point at each other"


def test_intake_puts_liaison_on_the_frontier_in_converse(db):
    """
    The join that matters. A `converse` message is what makes Liaison's intake
    mode the next thing the system does, and if it did not, talking to rota
    would be typing into a table.
    """
    from rota.core.scheduler import frontier

    talk.open_with(db, "invoices should be exportable as CSV")

    wakes = [w for w in frontier(db) if w.role == "liaison"]
    assert wakes, "the principal spoke and nobody was woken"
    assert any(w.detail == "converse" for w in wakes), \
        f"woken in the wrong mode: {[w.detail for w in wakes]}"


def test_a_second_sentence_is_a_second_entry_in_order(db):
    """Intake is append-only and ordered; a conversation is a transcript."""
    talk.open_with(db, "first thing")
    talk.open_with(db, "second thing")

    rows = db.execute("SELECT text FROM entries ORDER BY ts_order").fetchall()
    assert [r["text"] for r in rows] == ["first thing", "second thing"]


def test_the_console_principal_answers_the_verbs_it_is_offered(monkeypatch):
    """
    The human end of the seam, driven without a human.

    `confirm` and `present` take a per-item ruling; anything else is answered in
    words. That split is the whole protocol, and it was never exercised.
    """
    from rota.roles.principal import Ask, ConsolePrincipal

    monkeypatch.setattr("builtins.input", lambda *a: "lgtm")
    answer = ConsolePrincipal().respond(
        Ask(message_id="m1", verb="confirm", refs=["s1", "s2"]))
    assert answer.verb == "verdict"
    assert answer.per_item == {"s1": "approve", "s2": "approve"}

    monkeypatch.setattr("builtins.input", lambda *a: "s1=approve s2=contest")
    answer = ConsolePrincipal().respond(
        Ask(message_id="m2", verb="confirm", refs=["s1", "s2"]))
    assert answer.per_item == {"s1": "approve", "s2": "contest"}

    monkeypatch.setattr("builtins.input", lambda *a: "a purchase, not a sequence")
    answer = ConsolePrincipal().respond(
        Ask(message_id="m3", verb="clarify", refs=["g1"]))
    assert answer.verb == "converse"
    assert answer.text == "a purchase, not a sequence"


def test_deferral_is_always_allowed(monkeypatch):
    """
    Blank is not a non-answer. A deferred ask stays open and comes back on the
    agenda, which is why deferring costs nothing now and reappears later.
    """
    from rota.roles.principal import Ask, ConsolePrincipal

    monkeypatch.setattr("builtins.input", lambda *a: "")
    assert ConsolePrincipal().respond(
        Ask(message_id="m1", verb="confirm", refs=["s1"])) is None


def test_open_with_survives_a_message_id_gap(db):
    """new_id must use the max numeric suffix, not the row count."""
    # Simulate a prior session that minted m1 and m2, then dropped m2 before
    # commit (e.g. runner guard). The next id must be m3, not m2.
    db.execute(
        "INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
        "body_refs, body_text, seq, status) "
        "VALUES ('m1','t1','principal','liaison','converse','[]','hi',1,'open')")
    db.execute(
        "INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
        "body_refs, body_text, seq, status) "
        "VALUES ('m3','t1','liaison','principal','converse','[]','reply',2,'open')")
    db.commit()

    talk.open_with(db, "next")

    ids = [r["id"] for r in db.execute("SELECT id FROM messages ORDER BY seq")]
    assert ids == ["m1", "m3", "m4"], ids


def test_liaison_converse_sees_recent_chat(db):
    """A follow-up chat wake carries the prior turns as context."""
    from rota.core.runner import resolve_inbound
    from rota.core.scheduler import Wake

    db.execute(
        "INSERT INTO entries (id, author, text, ts_order) VALUES ('e_m1','principal','hi',1)")
    db.execute(
        "INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
        "body_refs, body_text, seq, status) "
        "VALUES ('m1','t1','principal','liaison','converse','[\"e_m1\"]','hi',1,'open')")
    db.execute(
        "INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
        "body_refs, body_text, seq, status) "
        "VALUES ('m2','t1','liaison','principal','converse','[]','Hello!',2,'open')")
    db.execute(
        "INSERT INTO entries (id, author, text, ts_order) VALUES ('e_m3','principal','how are you',2)")
    db.execute(
        "INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
        "body_refs, body_text, seq, status) "
        "VALUES ('m3','t2','principal','liaison','converse','[\"e_m3\"]','how are you',3,'open')")
    db.commit()

    wake = Wake(role="liaison", kind="message", message_id="m3", detail="converse")
    inbound = resolve_inbound(db, wake)

    assert inbound.get("recent_chat") == [
        {"from": "principal", "text": "hi"},
        {"from": "liaison", "text": "Hello!"},
    ]


# ---------------------------------------------------------------------------
# The UI, tested where it joins rather than where it paints.
# ---------------------------------------------------------------------------

def test_the_ui_principal_satisfies_the_same_protocol():
    """
    The seam was built so a backend could be a person, a script or a widget
    without any of them knowing about the others. This is the third, and it
    holds only if it answers the same protocol -- receive confirm/clarify/
    present, emit converse/verdict, defer by returning None.
    """
    import inspect

    from rota.cockpit.tui import QueuedPrincipal
    from rota.roles.principal import Ask, ConsolePrincipal

    seen = []

    class FakeApp:
        def call_from_thread(self, fn, *a):
            seen.append(a)

        def show_ask(self, ask):
            pass

    p = QueuedPrincipal(FakeApp())
    # Structurally, not by isinstance: `PrincipalBackend` is a Protocol and not
    # runtime-checkable, which is correct -- the seam is a shape, and a shape is
    # what should be compared.
    assert list(inspect.signature(QueuedPrincipal.respond).parameters) == \
        list(inspect.signature(ConsolePrincipal.respond).parameters), \
        "the widget backend and the human one must answer the same call"

    ask = Ask(message_id="m1", verb="confirm", refs=["s1"])
    assert p.respond(ask) is None, "an unanswered ask must defer, not block"
    assert p.pending == [ask], "a deferred ask has to be recoverable"
    assert seen, "the principal was asked and the interface never showed it"


def test_the_ui_principal_deduplicates_an_open_ask_and_accepts_lgtm():
    """A deferred ask is displayed once, then becomes a verdict when answered."""
    from rota.cockpit.tui import QueuedPrincipal
    from rota.roles.principal import Ask

    shown = []

    class FakeApp:
        def call_from_thread(self, fn, *args):
            shown.append(args[0])

        def show_ask(self, ask):
            pass

    principal = QueuedPrincipal(FakeApp())
    ask = Ask(message_id="m1", verb="confirm", refs=["s1", "s2"])

    assert principal.respond(ask) is None
    assert principal.respond(ask) is None
    assert len(shown) == 1

    principal.submit("lgtm")
    answer = principal.respond(ask)
    assert answer is not None
    assert answer.verb == "verdict"
    assert answer.per_item == {"s1": "approve", "s2": "approve"}


def test_the_sidebar_shows_what_the_register_owes(tmp_path):
    """
    The pane that did not exist in any form until today. Sessions scroll past
    and are gone; what is outstanding is the state, and it is the fold over the
    register rather than anything the UI computes for itself.
    """
    from rota.core.db import init_db
    from rota.core.predicates import outstanding

    db = init_db(tmp_path / "ui.db")
    assert outstanding(db) == []

    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1','order','a purchase','decided')")
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g2','order','a sequence','decided')")

    rows = outstanding(db)
    assert [r["obligation"] for r in rows] == ["term_collision"]
    assert rows[0]["owners"] == ["terminologist"], \
        "the pane must say who owes it, or it is a list of complaints"


def test_the_loop_runs_on_a_connection_its_own_thread_owns(tmp_path, monkeypatch):
    """
    The failure this was shipped with, written before the fix.

    `sqlite3.connect` is thread-bound unless told otherwise, and `db.connect`
    does not tell it otherwise -- deliberately, because a connection shared
    across threads by default is a race nobody declared. The app builds its
    connection on the main thread for the sidebar and intake, then hands it to a
    worker thread for the loop, and SQLite refuses on the first statement.

    Tested where it joins, which is the same claim the other tests here make and
    the one place I did not make good on it: the join is the thread boundary.
    """
    import threading

    from rota.cockpit import tui

    used: list[Exception | None] = []

    def fake_run(conn, **kw):
        # Whatever connection the worker was given has to work *here*, in this
        # thread. That is the whole assertion.
        try:
            conn.execute("SELECT COUNT(*) FROM messages").fetchone()
            used.append(None)
        except Exception as exc:                            # noqa: BLE001
            used.append(exc)

    monkeypatch.setattr(tui.loop_mod, "run", fake_run)

    app = tui.RotaApp(tmp_path / "ui.db", "llama3.1:8b")
    tui.open_with(app.conn, "let people export their invoices")

    t = threading.Thread(target=app._turn_the_crank)
    t.start()
    t.join(timeout=20)

    assert used, "the worker never reached the loop"
    assert used[0] is None, f"the loop got a connection its thread cannot use: {used[0]}"


async def test_the_app_mounts_and_shows_an_ask(tmp_path):
    """
    The two paths I called rough and left untested, driven headless.

    `show_ask` and `refresh_owed` both reach into the widget tree, and nothing
    had ever mounted it -- so every claim about them was a claim about code I
    had read rather than run. Textual's pilot mounts it for real.
    """
    from rota.cockpit import tui
    from rota.core import config
    from rota.roles.principal import Ask

    app = tui.RotaApp(tmp_path / "ui.db", "llama3.1:8b")
    async with app.run_test() as pilot:
        # The sidebar renders on mount, against an empty project.
        assert "nothing outstanding" in str(app.query_one("#owed").content)

        # A question from Liaison arrives as a bubble, refs rendered.
        app.show_ask(Ask(message_id="m1", verb="clarify", refs=["g_1", "g_2"]))
        await pilot.pause()
        assert len(app.query_one("#conversation").children) == 1

        # And the sidebar follows the register rather than a cache.
        app.conn.execute(
            "INSERT INTO glossary_terms (id, term, sense_short, provenance) "
            "VALUES ('g1','order','a purchase','decided')")
        app.conn.execute(
            "INSERT INTO glossary_terms (id, term, sense_short, provenance) "
            "VALUES ('g2','order','a sequence','decided')")
        app.refresh_owed()
        await pilot.pause()
        assert "term_collision" in str(app.query_one("#owed").content)


async def test_the_footer_offers_onboarding_for_the_displayed_root(tmp_path):
    """Onboarding is a footer action, not a message the Liaison must parse."""
    from rota.cockpit import tui

    root = tmp_path / "project"
    root.mkdir()
    app = tui.RotaApp(tmp_path / "ui.db", "llama3.1:8b", root=root)
    started = []
    app.run_worker = lambda fn, thread=True: started.append((fn, thread))

    async with app.run_test() as pilot:
        # The project moved to the subtitle when the run moved into the title:
        # two runs against one checkout is the normal case, so the project
        # alone never said which of them was on screen. Both are still shown.
        assert app.title == "rota — ui"
        assert app.sub_title == f"{root.name} — llama3.1:8b"
        # `alt+o` now. `ctrl+shift+o` can only reach a program under the Kitty
        # keyboard protocol; in a terminal without it the chord collapses to
        # `ctrl+o` and the footer advertised a key that did nothing.
        assert any(key == "alt+o" and action == "onboard"
                   for key, action, _ in app.BINDINGS)

        await pilot.press("alt+o")

    assert app._pending_root == root
    assert started == [(app._do_onboard, True)]


async def test_resume_triggers_the_loop(tmp_path):
    """Resuming should start the engine, not just flip the database flag."""
    from rota.cockpit import tui
    from rota.core import config

    app = tui.RotaApp(tmp_path / "ui.db", "llama3.1:8b")
    started = []
    app.run_worker = lambda fn, thread=True: started.append((fn, thread))

    async with app.run_test() as pilot:
        app.action_toggle_run_state()
        await pilot.pause()

    assert config.get(app.conn, "run_state") == "running"
    assert started == [(app._turn_the_crank, True)]


async def test_the_ticker_stays_bounded(tmp_path):
    """The cap, mounted rather than argued: forty sessions, thirty lines."""
    from rota.cockpit import tui

    app = tui.RotaApp(tmp_path / "ui.db", "llama3.1:8b")
    async with app.run_test() as pilot:
        for i in range(40):
            app.note_step(f"· step {i}")
        await pilot.pause()
        assert len(app.query_one("#sessions").children) == app.SESSION_LINES


def test_converse_replies_are_not_pending_asks(db):
    """Liaison prose replies are displayed, not offered as questions."""
    from rota.roles.principal import pending_asks, pending_replies

    db.execute(
        "INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
        "body_refs, body_text, seq, status) "
        "VALUES ('m1','t1','liaison','principal','converse','[]',"
        "'Hi there!',1,'open')")

    assert pending_asks(db) == []
    assert len(pending_replies(db)) == 1
    assert pending_replies(db)[0].rendered == "Hi there!"


async def test_the_tui_displays_and_consumes_liaison_replies(tmp_path):
    """A Liaison converse reply appears in the conversation pane once."""
    from rota.cockpit import tui

    app = tui.RotaApp(tmp_path / "ui.db", "llama3.1:8b")
    async with app.run_test() as pilot:
        app.conn.execute(
            "INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
            "body_refs, body_text, seq, status) "
            "VALUES ('m1','t1','liaison','principal','converse','[]',"
            "'Hello from Liaison',1,'open')")

        app.show_replies()
        await pilot.pause()
        assert len(app.query_one("#conversation").children) == 1

        # Calling again should not duplicate the reply.
        app.show_replies()
        await pilot.pause()
        assert len(app.query_one("#conversation").children) == 1
        row = app.conn.execute(
            "SELECT status FROM messages WHERE id = 'm1'").fetchone()
        assert row["status"] == "answered"


def test_follow_up_chat_without_pending_ask_opens_new_message(
        tmp_path, monkeypatch):
    """After Liaison replies, the user's next sentence is a new chat turn."""
    from rota.cockpit import tui

    runs = []
    monkeypatch.setattr(tui.loop_mod, "run", lambda *a, **k: runs.append(True))

    app = tui.RotaApp(tmp_path / "ui.db", "llama3.1:8b")
    tui.open_with(app.conn, "first thing")
    app.started = True
    app.say = lambda *a, **k: None          # don't paint during unit test

    captured = {}

    def fake_run_worker(fn, thread=True):
        captured["thread"] = thread
        return fn()

    app.run_worker = fake_run_worker

    class FakeEvent:
        def __init__(self, value):
            self.value = value
            self.input = type("Input", (), {"value": value})()

    app.on_input_submitted(FakeEvent("second thing"))

    msgs = app.conn.execute(
        "SELECT body_text FROM messages WHERE verb = 'converse' ORDER BY seq"
    ).fetchall()
    assert [m["body_text"] for m in msgs] == ["first thing", "second thing"]
    assert len(runs) == 1
    assert captured.get("thread") is True


def test_liaison_is_shown_the_sentence_it_was_woken_to_segment(db):
    """
    The first thing you type was invisible to the role that has to read it.

    `principal_said` is how the sentence reaches the session's prompt, and it
    comes from `entry_for`, which read a *config* key — `entry:<message_id>` —
    written by exactly one of the two paths that record an entry. The reply path
    writes it. `talk.open_with`, which is intake, the CLI and the TUI, writes the
    `entries` row and not the key.

    So a follow-up reply was visible and the opening sentence was not. Woken to
    segment nothing, Liaison answered "Hello! What would you like to build?" —
    which is the correct response to an empty message, and took
    `L1-LI-segment` and `L1-LI-no-report-no-question` to 0/5 while reading
    exactly like a role that had decided to chat.

    The entry text has an owning table. Reading it from a second place that only
    half the writers fill is the failure `paths.py` exists to prevent, one table
    down.
    """
    from rota.roles.principal import entry_for

    msg_id = talk.open_with(db, "we need SSO, but only if it works with our LDAP")

    assert db.execute("SELECT text FROM entries WHERE id = ?",
                      (f"e_{msg_id}",)).fetchone()["text"], "intake records it"
    assert entry_for(db, msg_id) == "we need SSO, but only if it works with our LDAP", \
        "and the session woken to segment it has to be able to see it"


def test_the_sentence_reaches_the_prompt(db):
    """
    One level up from the lookup: what the session is actually shown.

    Tested here rather than trusted, because the lookup returning the right
    string is not the claim -- the claim is that the words are in the prompt.
    Three empty lists and no sentence is what Liaison had, and it answered
    accordingly.

    `principal_said` travels in `resolve_inbound` and not in the pushed working
    set: the wake *is* the message, so it is resolved rather than fetched.
    """
    from rota.core import runner, sandbox as sandbox_mod
    from rota.core.scheduler import Wake
    from rota.design import graph as graph_mod

    msg_id = talk.open_with(db, "we need SSO, but only if it works with our LDAP")
    wake = Wake("liaison", "message", msg_id, detail="converse")
    sb = sandbox_mod.build("liaison", db, mode="converse")

    inbound = runner.resolve_inbound(db, wake)
    assert inbound.get("principal_said"), "woken to read something it was not given"
    assert inbound.get("entry_id") == f"e_{msg_id}",         "and it needs the id, because the spans are offsets into that entry"

    pushed = runner.push_working_set("liaison", sb, wake, graph_mod.load())
    _, user = runner.build_prompt("liaison", sb, wake, pushed, "INSTRUCTIONS",
                                  inbound=inbound)
    assert "SSO" in user and "LDAP" in user, user[:800]
