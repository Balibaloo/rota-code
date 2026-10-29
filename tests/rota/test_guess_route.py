"""
Frame 298, pass 3: the route of a correction of the code a request touches.

The design is `plans/frame298-design.md`, section 3 as amended (section 10).
A files-only contest of a request line is refused, and the refusal names the
code line or its key `guess:<item>`. A ruling on the code line relays the
words to the Architect's `guess` mode, or to `annotate` through the stamped
batch. No path of this route writes `contested` on the item, so `cancel`
cannot fire.

The wall's scene is night 156's m191, bg_3's sign-off page, and its reply
m192, rebuilt inline from `.rota/clickI_night156.db` read with `mode=ro` on
2026-10-18. The item text is version 1's, the text the page showed. Pass 3
leaves the page without a numbered code line, so the tests write the send
door's stamp `code:<message id>` by hand (design, section 6).
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import SessionResult, init_db, session_commit
from rota.core.predicates import cancel
from rota.core.runner import _as_write, _mode_key, resolve_inbound, run_session
from rota.core.sandbox import build
from rota.core.scheduler import Wake, open_tips
from rota.llm.llm import Pins, ScriptedBackend
from rota.roles import prompts
from rota.roles.api import Ctx, pointer_fault, ref_resolves
from rota.roles.principal import (land, parse_reply, pending_asks, render_page,
                                  verdict_for)
from rota.testkit.fixtures import seed_provenance

PINS = Pins(model="stub", temperature=0.0)

ITEM = "version_option_show_python"
TICKET = "tk_1_version_option_show_python"
HEAD = "2a50023c556245d03a07ba31eb8c5a40e664cb1c"
CRITERIA = (
    ("ver_opt_show_py",
     "When the show_python flag is turned on, the --version output must end with "
     "\"Python\" followed by the major.minor.micro version taken from the running "
     "interpreter."),
    ("ver_opt_show_py_env",
     "When the show_python flag is turned on, the Python version appended to the "
     "--version output is determined by inspecting sys.version_info at runtime."),
    ("ver_opt_show_py_format",
     "When the show_python flag is turned on, the Python version string in the "
     "--version output follows the format \"Python X.Y.Z\" where X, Y, and Z are "
     "the major, minor, and patch versions."),
)
# m191's seven notes, in the page's refs order (night 156, `ledger`).
NOTES = (
    ("l_cfe740352e", "tester", "default", "criteria", "ver_opt_show_py",
     "The principal clarified that show_python flag controls visibility; normal "
     "version stays unchanged. Tests use capsys to capture output and verify "
     "presence/absence of \"Python\" string."),
    ("l_08a201e886", "tester", "default", "criteria", "ver_opt_show_py_env",
     "The principal clarified that Python version is determined by inspecting "
     "sys.version_info at runtime. Tests use capsys to capture output and verify "
     "the version string matches sys.version_info format."),
    ("l_2b9b31b7e7", "tester", "default", "criteria", "ver_opt_show_py_format",
     "The principal clarified that Python version string follows format \"Python "
     "X.Y.Z\". Tests use capsys to capture output and verify the format."),
    ("l_854fbc4d6e", "tester", "default", "criteria", "ver_opt_show_py_format",
     "The test now correctly asserts that without show_python, the output does "
     "not contain the appended Python version string, and with show_python=True, "
     "it ends with \"Python X.Y.Z\"."),
    ("l_a32fe37623", "developer", "scope", "criteria", "ver_opt_show_py",
     "The criterion assumes version_option works with just show_python=True, but "
     "Click requires a callback; without clarification from Vision Keeper, I "
     "cannot proceed."),
    ("l_ada8b7a291", "tester", "default", "criteria", "ver_opt_show_py",
     "The test now correctly asserts that without show_python, the output does "
     "not contain the appended Python version string, and with show_python=True, "
     "it ends with \"Python X.Y.Z\"."),
    ("l_bc2ca6a611", "developer", "scope", "criteria", "ver_opt_show_py",
     "The criterion implies that version_option must accept only show_python=True "
     "without a callback, but Click's version_option requires a callback "
     "function."),
)
# bg_3's `batch_touch` rows (night 156).
TOUCH = ("src/click/decorators.py", "tests/test_basic.py")
# m192, the principal's reply to m191 (night 156, `messages`).
M192 = ("Lines 2 to 4 are still wrong: each check runs with the flag off and looks "
        "for a hard-coded 3.10.0, but each one should turn the flag on and check "
        "that the message ends with \"Python\" and major.minor.micro taken from the "
        "running interpreter's version info. Lines 9 and 11 are wrong too, because "
        "version option already builds its own callback, so show_python only needs "
        "to be a normal keyword argument with no callback from the caller. Line 1 "
        "also names the options and defaults test files, which have nothing to do "
        "with this change, so keep the work to version option and its tests in the "
        "basic tests file.")
# s322's reading of m192 (night 156, `rulings` r_e244215675), by row id.
S322 = {ITEM: "contest", "ver_opt_show_py": "contest",
        "ver_opt_show_py_env": "contest", "ver_opt_show_py_format": "contest",
        "l_cfe740352e": "approve", "l_08a201e886": "approve",
        "l_2b9b31b7e7": "approve", "l_854fbc4d6e": "approve",
        "l_a32fe37623": "contest", "l_ada8b7a291": "approve",
        "l_bc2ca6a611": "contest"}
KEY = f"guess:{ITEM}"
# The reading the refusal asks for: line 1 approved, its files on the key.
S322_MOVED = dict(S322, **{ITEM: "approve", KEY: "contest"})
REFS = [n[0] for n in NOTES] + [ITEM] + [c for c, _ in CRITERIA]


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _page(db, batch: str | None = "running", head: str | None = HEAD,
          stamp: dict | None = None, guess: bool = False):
    """m191 open, the item approved at version 1, and bg_3 when `batch`."""
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version, "
               "priority) VALUES (?, ?, 'in_scope', 'approved', 1, 1, 1)",
               (ITEM, "Give version_option a show_python flag that appends the "
                      "running Python version to the message."))
    seed_provenance(db, "items", ITEM, "decided")
    db.execute("INSERT INTO tickets (id, item_id, text, version, item_ver) "
               "VALUES (?, ?, ?, 1, 1)",
               (TICKET, ITEM, "give version_option a show_python flag that appends "
                              "the running Python version to the message"))
    for cid, text in CRITERIA:
        db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?, ?, ?)",
                   (cid, TICKET, text))
    for lid, author, kind, table, about, taken in NOTES:
        db.execute("INSERT INTO ledger (id, author, kind, about_table, about_ref, "
                   "default_taken, status) VALUES (?, ?, ?, ?, ?, ?, 'open')",
                   (lid, author, kind, table, about, taken))
    for grain in TOUCH:
        db.execute("INSERT INTO code_index (grain, grain_kind) VALUES (?, 'path')",
                   (grain,))
    if batch:
        db.execute("INSERT INTO batches (id, item_id, head_commit, status, version) "
                   "VALUES ('bg_3', ?, ?, ?, 1)", (ITEM, head, batch))
        db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('bg_3', ?)",
                   (TICKET,))
        for grain in TOUCH:
            db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind, "
                       "confidence) VALUES ('bg_3', ?, 'path', 'expected')", (grain,))
    if guess:
        for grain in ("src/click/decorators.py", "tests/test_options.py",
                      "tests/test_defaults.py"):
            db.execute("INSERT INTO touch_guesses (item_id, item_ver, ruling_id, "
                       "grain, grain_kind) VALUES (?, 1, '', ?, 'path')", (ITEM, grain))
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, status, seq) VALUES ('m191', 'm191', 'liaison', "
               "'principal', 'present', ?, 'open', 1)", (json.dumps(REFS),))
    db.execute("INSERT INTO config (key, value) VALUES ('stamped:m191', ?)",
               (json.dumps([ITEM] + [c for c, _ in CRITERIA]),))
    if stamp is not None:
        db.execute("INSERT INTO config (key, value) VALUES ('code:m191', ?)",
                   (json.dumps(stamp),))
    db.commit()
    return db


def _reply(db, words: str) -> str:
    (ask,) = [a for a in pending_asks(db) if a.message_id == "m191"]
    reply = land(db, ask, parse_reply(ask, words))
    db.commit()
    return reply


def _landing(db, trigger: str):
    sb = build("liaison", db, mode="landing",
               allow=prompts.mode_tools("liaison", "landing"))
    sb.ctx.trigger = trigger
    return sb


def _land_ruling(db, words: str, ruling: dict) -> str:
    """The Liaison's session on the reply, scripted, and the verdict it lands."""
    reply = _reply(db, words)
    (wake,) = [w for w in open_tips(db) if w.message_id == reply]
    call = f"TOOL: rulings.rule(rulings={json.dumps(ruling)}, words={words!r})"
    out = run_session(db, wake, backend=ScriptedBackend([call, "done"]),
                      pins=PINS, instructions="land")
    assert out.committed, out.errors
    return db.execute("SELECT id FROM messages WHERE cause_id = 'm191' "
                      "AND verb = 'verdict'").fetchone()["id"]


def _verdict(db, vid: str) -> dict:
    return verdict_for(db, vid)


# ---------------------------------------------------------------------------
# The page and the cue
# ---------------------------------------------------------------------------

def test_m191_numbers_the_request_as_line_1(db):
    _page(db)
    _, order = render_page(db, "present", REFS, ask_id="m191")
    assert order[0] == ITEM
    assert order[1:4] == [c for c, _ in CRITERIA]


def test_the_cue_reads_m192_as_a_fault_of_line_1s_files_alone():
    assert pointer_fault(M192, 1)


def test_the_cue_does_not_read_a_request_correction_as_files():
    """A (b) reply: the words correct the request itself (frame 298's count,
    class (b), night 150's shape)."""
    words = ("Line 1 is wrong: the helper should return the string instead of "
             "printing it, and it should say so in my words.")
    assert not pointer_fault(words, 1)


# ---------------------------------------------------------------------------
# The wall: s322 on m192, bg_3 stamped on the code line
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="re-pin to the menu form, frame 345: R2 word form")
def test_the_moved_reading_lands_on_bg_3_and_the_item_stays_approved(db):
    """The reading the refusal asks for lands. bg_3 has a head commit, so the
    code line keeps frame 255's check, and the cue holds it. The item keeps
    its approval, `cancel` stays silent, and bg_3 lives."""
    _page(db, stamp={KEY: {"batch": "bg_3"}})
    vid = _land_ruling(db, M192, S322_MOVED)
    ruled = _verdict(db, vid)
    assert ruled.get("bg_3") == "contest", ruled
    assert KEY not in ruled and ITEM not in ruled, ruled
    assert db.execute("SELECT approval FROM items WHERE id = ?",
                      (ITEM,)).fetchone()["approval"] == "approved"
    assert cancel(db) == []
    assert db.execute("SELECT status FROM batches WHERE id = 'bg_3'"
                      ).fetchone()["status"] == "running"


@pytest.mark.skip(reason="re-pin to the menu form, frame 345: R2 word form")
def test_the_verdict_on_bg_3_relays_to_annotate(db):
    _page(db, stamp={KEY: {"batch": "bg_3"}})
    vid = _land_ruling(db, M192, S322_MOVED)
    (wake,) = [w for w in open_tips(db) if w.message_id == vid]
    out = run_session(db, wake, backend=ScriptedBackend(
        ['TOOL: msg.relay_architect(refs=["bg_3"])', "done"]), pins=PINS,
        instructions="relay")
    assert out.committed, out.errors
    relay = db.execute("SELECT id FROM messages WHERE cause_id = ? AND verb = "
                       "'relay' AND to_role = 'architect'", (vid,)).fetchone()
    assert _mode_key(Wake("architect", "message", message_id=relay["id"],
                          detail="relay"), db) == "annotate"


# ---------------------------------------------------------------------------
# No batch: the guess
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="re-pin to the menu form, frame 345: R2 word form")
def test_a_request_correction_still_lands_on_line_1(db):
    """The cue refuses no (b) reply: 43 of 43 in-sample."""
    _page(db, batch=None, guess=True)
    words = ("Line 1 is wrong: the flag should print the Python version on its "
             "own line instead of appending it to the message.")
    sb = _landing(db, _reply(db, words))
    out = sb.call("rulings.rule", rulings={**{r: "approve" for r in REFS},
                                           ITEM: "contest"}, words=words)
    assert out["per_item"][ITEM] == "contest"


def _guess_verdict(db) -> str:
    _page(db, batch=None, guess=True, stamp={KEY: {"guess": [1, ""]}})
    return _land_ruling(db, M192, S322_MOVED)


@pytest.mark.skip(reason="re-pin to the menu form, frame 345: R2 word form")
def test_a_guess_ruling_keeps_the_key_and_the_set_the_principal_read(db):
    vid = _guess_verdict(db)
    assert _verdict(db, vid).get(KEY) == "contest"
    shown = json.loads(db.execute("SELECT value FROM config WHERE key = ?",
                                  (f"guess_target:{vid}",)).fetchone()["value"])
    assert shown == {KEY: [1, ""]}
    assert db.execute("SELECT approval FROM items WHERE id = ?",
                      (ITEM,)).fetchone()["approval"] == "approved"
    assert cancel(db) == []


@pytest.mark.skip(reason="re-pin to the menu form, frame 345: R2 word form")
def test_an_off_page_key_lands_with_no_stamp(db):
    """A page sent before the guess carries no stamp. The key's target is
    then the current guess (design 3.1, point 5)."""
    _page(db, batch=None, guess=True)
    vid = _land_ruling(db, M192, S322_MOVED)
    assert _verdict(db, vid).get(KEY) == "contest"
    shown = json.loads(db.execute("SELECT value FROM config WHERE key = ?",
                                  (f"guess_target:{vid}",)).fetchone()["value"])
    assert shown == {KEY: [1, ""]}


def _relay(db, vid: str) -> str:
    (wake,) = [w for w in open_tips(db) if w.message_id == vid]
    out = run_session(db, wake, backend=ScriptedBackend(
        [f'TOOL: msg.relay_architect(refs=["{KEY}"])', "done"]), pins=PINS,
        instructions="relay")
    assert out.committed, out.errors
    return db.execute("SELECT id FROM messages WHERE cause_id = ? AND verb = 'relay' "
                      "AND to_role = 'architect'", (vid,)).fetchone()["id"]


@pytest.mark.skip(reason="re-pin to the menu form, frame 345: R2 word form")
def test_the_guess_relay_passes_the_send_door_and_keys_the_guess_mode(db):
    rid = _relay(db, _guess_verdict(db))
    wake = Wake("architect", "message", message_id=rid, detail="relay")
    assert _mode_key(wake, db) == "guess"


@pytest.mark.skip(reason="re-pin to the menu form, frame 345: R2 word form")
@pytest.mark.parametrize("key_ruling, disputed", [
    ({"verdict": "contest", "act": "exclude", "target": "tests/test_options.py",
      # A span is a run of whole clauses of his reply (review p7 p1, 3).
      "words": "Line 1 also names the options and defaults test files, which "
               "have nothing to do with this change"},
     ["tests/test_options.py"]),
    ("contest", []),
])
def test_the_guess_relay_carries_the_item_the_set_and_the_disputed_paths(
        db, key_ruling, disputed):
    """Pass 4, P10: the path his ruling removes leaves the guess. The act
    `exclude` and its target say it. A contest with no act disputes no path,
    and the Architect reads his words."""
    _page(db, batch=None, guess=True, stamp={KEY: {"guess": [1, ""]}})
    vid = _land_ruling(db, M192, dict(S322_MOVED, **{KEY: key_ruling}))
    rid = _relay(db, vid)
    wake = Wake("architect", "message", message_id=rid, detail="relay")
    inbound = resolve_inbound(db, wake)
    assert inbound["item"]["id"] == ITEM
    shown = ["src/click/decorators.py", "tests/test_options.py",
             "tests/test_defaults.py"]
    assert inbound["disputed"] == disputed
    assert inbound["guess"] == [p for p in shown if p not in disputed]


@pytest.mark.skip(reason="re-pin to the menu form, frame 345: R2 word form")
def test_the_rewrite_rests_on_the_ruling_and_clears_its_set_first(db):
    vid = _guess_verdict(db)
    rid = _relay(db, vid)
    sb = build("architect", db, mode="guess", session_id="s9",
               allow=prompts.mode_tools("architect", "guess"))
    sb.ctx.trigger = rid
    sb.call("batches.guess", item_id=KEY,
            paths=["src/click/decorators.py", "tests/test_basic.py"])
    assert sb.ctx.writes[0] == ("touch_guesses", f"{ITEM}:1:{vid}:*", {
        "item_id": ITEM, "item_ver": 1, "ruling_id": vid}, "clear")
    session_commit(db, SessionResult(
        session_id="s9", role="architect", trigger_msg=rid,
        writes=[_as_write(w) for w in sb.ctx.writes]))
    sets = [tuple(r) for r in db.execute(
        "SELECT ruling_id, grain FROM touch_guesses ORDER BY rowid")]
    assert sets[-2:] == [(vid, "src/click/decorators.py"), (vid, "tests/test_basic.py")]
    assert ("", "tests/test_options.py") in sets, "the Architect's own guess stays"


def test_the_ref_door_resolves_a_request_items_key_only(db):
    _page(db, batch=None)
    ctx = Ctx(conn=db, role="liaison", writes=[], outbound=[])
    assert ref_resolves(ctx, KEY)
    assert not ref_resolves(ctx, "guess:nothing_here")
    assert not ref_resolves(ctx, "guess:ver_opt_show_py")


# ---------------------------------------------------------------------------
# The op's review lows
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="re-pin to the menu form, frame 345: R2 word form")
def test_the_send_door_refuses_a_relay_of_a_key_that_names_no_item(db):
    vid = _guess_verdict(db)
    (wake,) = [w for w in open_tips(db) if w.message_id == vid]
    out = run_session(db, wake, backend=ScriptedBackend(
        ['TOOL: msg.relay_architect(refs=["guess:nothing_here"])', "done"]),
        pins=PINS, instructions="relay")
    assert any("'guess:nothing_here' names no row" in e for e in out.errors)
    relayed = [json.loads(r["body_refs"]) for r in db.execute(
        "SELECT body_refs FROM messages WHERE cause_id = ? AND verb = 'relay'", (vid,))]
    assert not any("guess:nothing_here" in r for r in relayed), relayed


def test_the_op_names_the_woken_item_for_an_unknown_id(db):
    _page(db, batch=None)
    sb = build("architect", db, mode="guess", session_id="s1",
               allow=prompts.mode_tools("architect", "guess"),
               wake=Wake("architect", "tick:guess", refs=(ITEM,)))
    with pytest.raises(ValueError, match=f"no item i1. The request is `item` in "
                                         f"your working set, {ITEM}"):
        sb.call("batches.guess", item_id="i1", paths=["tests/test_basic.py"])


def test_the_op_refuses_a_symbol_under_a_directory_the_index_lacks(db):
    _page(db, batch=None)
    sb = build("architect", db, mode="guess", session_id="s1",
               allow=prompts.mode_tools("architect", "guess"))
    with pytest.raises(ValueError, match="nowhere/x.py is under a directory"):
        sb.call("batches.guess", item_id=ITEM, paths=["tests/test_basic.py"],
                symbols=["nowhere/x.py::y"])
