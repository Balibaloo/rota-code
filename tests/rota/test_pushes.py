"""What a wake pushes, read as the person doing the job would (the wake
audit, plans/wake-audit.md)."""
import json
import pytest

from rota.core.db import init_db
from rota.core.runner import push_working_set
from rota.core.sandbox import build
from rota.core.scheduler import Wake
from rota.roles import prompts
from rota.testkit.fixtures import seed_provenance, seed_ref


def test_the_slicing_wake_sets_its_item_apart_from_the_account(tmp_path):
    """clickI night 35 (2026-09-13): woken for one item and shown five, the
    Vision Keeper sliced all five and four were refused."""
    db = init_db(tmp_path / "rota.db")
    for i, text in (("how_it_works", "the program is a CLI toolkit"),
                    ("echo_json", "add an echo_json helper next to echo")):
        db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
                   "VALUES (?, ?, 'in_scope', 'approved', 1, 1)", (i, text))
    db.commit()
    sb = build("vision_keeper", db, mode="slicing",
               allow=prompts.mode_tools("vision_keeper", "slicing"))
    pushed = push_working_set("vision_keeper", sb, Wake("vision_keeper", "tick:slicing", refs=("echo_json",)))
    account = pushed["problem.consult"]
    assert [r["id"] for r in account["to slice, this wake"]] == ["echo_json"]
    assert account["the rest of the account, not this wake's"] == ["how_it_works"]


def test_the_criteria_wake_carries_the_item_and_the_module_the_ticket_names(tmp_path):
    """clickI night 35 (2026-09-13): the ticket said "next to echo", the lens
    listed `src/click/utils.py::echo`, and the criteria invented "without
    buffering delays" without reading it."""
    root = tmp_path / "proj"; (root / "src" / "click").mkdir(parents=True)
    (root / "src" / "click" / "utils.py").write_text("def echo(message):\n    print(message)\n")
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('project_root', ?)", (str(root),))
    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES ('e1','principal',1,'Add an echo_json helper next to echo.')")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, status) VALUES "
               "('s1','e1',0,40,'Add an echo_json helper next to echo.','ratified')")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) VALUES "
               "('echo_json','Add an echo_json helper next to echo','in_scope','approved',1,1)")
    seed_ref(db, "items", "echo_json", "statement", "s1")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','echo_json','add an echo_json helper next to echo')")
    db.execute("INSERT INTO code_index (grain, grain_kind, sym_kind) VALUES ('src/click/utils.py::echo','symbol','function')")
    db.execute("INSERT INTO code_index (grain, grain_kind, sym_kind) VALUES ('tests/test_echo.py::test_echo','symbol','function')")
    seed_provenance(db, "items", "echo_json", "decided")
    db.commit()
    sb = build("terminologist", db, mode="criteria",
               allow=prompts.mode_tools("terminologist", "criteria"))
    pushed = push_working_set("terminologist", sb, Wake("terminologist", "tick:criteria", refs=("echo_json",)))
    assert pushed["the item"]["text"] == "Add an echo_json helper next to echo"
    assert pushed["the item"]["the principal said"] == ["Add an echo_json helper next to echo."]
    assert list(pushed["code.source"]) == ["src/click/utils.py"], pushed.get("code.source")
    assert "def echo" in str(pushed["code.source"]["src/click/utils.py"])


def test_the_agenda_wake_pushes_the_pages_seven_and_counts_the_rest(tmp_path):
    """clickI night 35 (2026-09-13): 51 open ledger rows, 15,500 characters,
    pushed into a wake whose refs named seven."""
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind) VALUES ('i1','x','in_scope')")
    for k in range(10):
        db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, author) "
                   "VALUES (?, 'i1', 'items', ?, 'developer')", (f"l_{k}", f"assumed {k}"))
    db.commit()
    sb = build("liaison", db, mode="agenda", allow=prompts.mode_tools("liaison", "agenda"))
    page = tuple(f"l_{k}" for k in range(7))
    pushed = push_working_set("liaison", sb, Wake("liaison", "tick:agenda", refs=page))
    shown = pushed["ledger.list"]
    assert [r["id"] for r in shown["this page"]] == list(page)
    assert shown["open and not on this page"].startswith("3 more")


# Six words the subject says, each with more matching rulings than the budget
# holds. Every word is its own `decisions.search` query at the push site.
_DECISION_WORDS = ("scope", "budget", "window", "latency", "cache", "retry")


def _decision_push(tmp_path, per_word=8):
    """The rows the push would have sent whole, and the block it sends now."""
    db = init_db(tmp_path / "rota.db")
    for word in _DECISION_WORDS:
        for k in range(per_word):
            db.execute("INSERT INTO decisions (id, author, text) VALUES "
                       "(?, 'architect', ?)",
                       (f"d_{word}_{k}", f"the {word} ruling {k}: " + "x" * 200))
    db.commit()
    sb = build("architect", db, mode="unresolved",
               allow=prompts.mode_tools("architect", "unresolved"))
    pushed = push_working_set("architect", sb,
                              Wake("architect", "tick:unresolved", refs=()),
                              asked=" ".join(_DECISION_WORDS))
    raw = {w: sb.call("decisions.search", query=w) for w in _DECISION_WORDS}
    return raw, pushed["decisions.search"]


def test_the_decision_push_is_inside_its_own_budget(tmp_path):
    """Night 87 (2026-09-20): `decisions.search` was 55.5 per cent of every
    pushed character, and its median push was `PUSH_CHARS` plus the truncation
    notice. The budget is the record's own, below the backstop."""
    from rota.core import runner
    raw, block = _decision_push(tmp_path)
    assert len(runner._render(raw, runner.PUSH_CHARS)) > 2 * runner.DECISIONS_PUSH_CHARS
    shown = runner._render(block, runner.PUSH_CHARS)     # the cap build_prompt uses
    assert len(shown) <= runner.DECISIONS_PUSH_CHARS, len(shown)
    assert "CUT the result" not in shown, "the backstop cut what the budget should have"


def test_a_row_wider_than_the_budget_does_not_ride_on_the_guarantee(tmp_path):
    """
    The at-least-one-row guarantee sat outside the budget check. A 9,000
    character row rendered the block at 6,123 against a 6,000 limit, the outer
    `_render` cut it again, and the seat read two cuts for one block (the diff
    review of 0cc624b, finding 2). Production stays near 1,700 because the op
    caps its headline at 200 characters, so this was one SELECT away.

    The seed is dropped word by word, last first, and the notices remain: which
    words matched, and what to call for each.
    """
    from rota.core import runner

    wide = [{"id": "d_wide", "author": "architect",
             "headline": "x" * 9000, "supersedes": None}]
    block = runner._budget_decision_hits({"scope": wide, "budget": wide},
                                         runner.DECISIONS_PUSH_CHARS)
    shown = runner._render(block, runner.PUSH_CHARS)

    assert len(shown) <= runner.DECISIONS_PUSH_CHARS, len(shown)
    assert "CUT the result" not in shown, "the renderer cut what the budget should have"
    assert "x" * 9000 not in shown, "the row rode on the guarantee"
    assert [n.split(":")[0] for n in block["not shown"]] == [
        'CUT the rulings for "scope"', 'CUT the rulings for "budget"'], block
    assert not [w for w in ("scope", "budget") if w in block], \
        "a word kept a row the budget could not hold"


def test_every_word_that_matched_keeps_a_row_of_the_decision_push(tmp_path):
    """Round robin by row. First come gave word one every row it had, and the
    other five words' rulings never arrived."""
    _raw, block = _decision_push(tmp_path)
    rows = {w: block[w] for w in _DECISION_WORDS if w in block}
    assert sorted(rows) == sorted(_DECISION_WORDS), sorted(block)
    assert all(len(v) >= 1 for v in rows.values()), {w: len(v) for w, v in rows.items()}
    kept = sum(len(v) for v in rows.values())
    assert len(rows[_DECISION_WORDS[0]]) < kept


def test_the_cut_decision_push_names_the_call_for_the_rest(tmp_path):
    """
    A push has no range to ask for, so the backstop's "ask for the next range"
    named no call a seat could make. The notice names one, in the wording every
    cut uses.

    It promises what the call returns and no count. `decisions.search` comes
    back through `_render` at `RESULT_CHARS`, which is the same 6,000 characters
    the push holds, so "for all 8" was a promise the call could not keep.

    The sentence is an imperative, because `CLAUDE.md` rules the imperative for
    an instruction. No case measures the difference: the wording was suspected
    of breaking `L1-TE-survey-an-area-for-its-terms` and it does not. That case
    records 0/5 on both wordings, and at the commit before this frame
    (2026-09-20, frame 46 line 3).
    """
    _raw, block = _decision_push(tmp_path)
    notes = block["not shown"]
    for word in _DECISION_WORDS:
        dropped = 8 - len(block[word])
        assert dropped > 0, word
        want = (f'CUT the rulings for "{word}": {dropped} of 8 rows are not '
                f'shown. Call decisions.search(query="{word}") for that word\'s '
                f'rows, as far as one result fits.')
        assert want in notes, (word, notes)
        assert notes[0].split(". ", 1)[1].startswith("Call ")


def test_a_quarantined_tick_names_the_batch_it_stalled_on(tmp_path):
    """clickI night 37 (2026-09-13): the wake said "1 abandoned" and nothing
    else, and the Liaison sent refs=["tick:quarantined"] three times."""
    from rota.core import predicates as P
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind) VALUES ('i1','x','in_scope')")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('bg_2','i1','running')")
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, reported) "
               "VALUES ('developer|tick:batch_start|bg_2', 3, 1, 0)")
    db.commit()
    wakes = P.quarantined(db)
    assert wakes and wakes[0].refs == ("bg_2",)
    assert "batch_start for bg_2 (developer), 3 attempts" in wakes[0].detail


# --- frame 243, the contest words beside the criterion ------------------------

# Night 148's rows, copied verbatim from `.rota/clickI_night148.db` on
# 2026-10-15, so the tests run in a checkout without the run's database
# (frame 243, review 1, finding 4).
CRIT148 = "ver_opt_show_py"
# The criterion's text when s190 woke, after s188's respecify.
TEXT148 = ('If the show_python flag is enabled on version_option, the output '
           'format must be "{command} {python_version}" where python_version '
           'is obtained from sys.version_info.major.minor.micro and appended '
           'to the end of the normal version message.')
# r_4c8fd5d3ad, the reply m71 to page m70.
RULING148 = {
    "id": "r_4c8fd5d3ad", "ask_id": "m70", "reply_id": "m71",
    "per_item": json.dumps({"version_option_show_python": "approve",
                            CRIT148: "contest", "bg_3": "approve"}),
    "words": ("Line 2 is wrong because the Python version should come from "
              "sys.version_info as major.minor.micro, not from sys.version. It "
              "should also be added to the end of the normal version message, "
              "not replace that message with just the command name and the "
              "Python version."),
    "texts": json.dumps({CRIT148: (
        'If the show_python flag is enabled, the output format must be '
        '"{command} {python_version}" where python_version is obtained from '
        'sys.version.')}),
}
# A second criterion of the batch that he never contested. Not the night's.
OTHER148 = ("ver_opt_plain", "Without show_python the version message is unchanged.")
# The block's key and lines are the wake's text, so the tests name them whole.
CONTESTS_KEY = "the principal contested these criteria"


def _contested(cid: str, text: str, live: str) -> str:
    """The block's lines for one contested text. Frame 328, item 5: a text
    that the live row replaced says so, and the live text stands under it."""
    if " ".join(text.split()) == " ".join(live.split()):
        return f"{cid}: He contested this text: {text}\n"
    return (f"{cid}: He contested this text, and it is replaced now: {text}\n"
            f"{cid}: The live text is: {live}\n")


def _seed148(tmp_path, contested: bool):
    """Night 148's bg_3 with its two criteria, and r_4c8fd5d3ad when
    `contested`."""
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES ('version_option_show_python', 'show_python on version_option', "
               "'in_scope', 'approved', 1, 1)")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES "
               "('bg_3', 'version_option_show_python', 'running')")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('tk_1', 'version_option_show_python', 'show_python on version_option')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('bg_3', 'tk_1')")
    for cid, text in ((CRIT148, TEXT148), OTHER148):
        db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?, 'tk_1', ?)",
                   (cid, text))
    if contested:
        r = RULING148
        for mid, verb in ((r["ask_id"], "present"), (r["reply_id"], "reply")):
            db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                       "body_refs, seq) VALUES (?, ?, 'liaison', 'principal', ?, ?, 1)",
                       (mid, r["ask_id"], verb, json.dumps([CRIT148])))
        db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, "
                   "status, texts) VALUES (?, ?, ?, ?, ?, 'landed', ?)",
                   (r["id"], r["ask_id"], r["reply_id"], r["per_item"], r["words"],
                    r["texts"]))
    db.commit()
    return db


def _push148(db, role: str, mode: str, kind: str) -> dict:
    sb = build(role, db, batch_id="bg_3", mode=mode,
               allow=prompts.mode_tools(role, mode))
    pushed = push_working_set(role, sb, Wake(role, kind, refs=("bg_3",)))
    assert "criteria.load" in pushed, sorted(pushed)
    return pushed


WAKES148 = [("developer", "batch_start", "tick:batch_start"),
            ("tester", "tests_missing", "tick:tests_missing")]


@pytest.mark.parametrize("role,mode,kind", WAKES148, ids=["developer", "tester"])
def test_night148_the_builders_wake_carries_his_contest_words(tmp_path, role, mode, kind):
    """Frame 243, night 148: s190 built bg_3 from the criterion alone, and
    its prompt held no word of r_4c8fd5d3ad. The words now follow the
    criteria, verbatim, after the text he contested."""
    from rota.core.runner import _render, PUSH_CHARS
    pushed = _push148(_seed148(tmp_path, True), role, mode, kind)
    keys = list(pushed)
    assert keys[keys.index("criteria.load") + 1] == CONTESTS_KEY
    contested = json.loads(RULING148["texts"])[CRIT148]
    assert pushed[CONTESTS_KEY] == (
        f"ruling r_4c8fd5d3ad:\n"
        f"He contested {CRIT148}.\n"
        + _contested(CRIT148, contested, TEXT148) +
        f"He said: {RULING148['words']}")
    # The criteria keep their table: a contest adds no key to any row.
    assert _render(pushed["criteria.load"], PUSH_CHARS).startswith(
        "id | ticket_id | text | term_refs")


@pytest.mark.parametrize("role,mode,kind", WAKES148, ids=["developer", "tester"])
def test_a_criterion_with_no_contest_ruling_shows_nothing_new(tmp_path, role, mode, kind):
    """Frame 243: a batch whose criteria he never contested keeps the push
    it had before, with the same rows."""
    pushed = _push148(_seed148(tmp_path, False), role, mode, kind)
    assert CONTESTS_KEY not in pushed
    assert [list(r) for r in pushed["criteria.load"]] == [
        ["id", "ticket_id", "text", "term_refs"]] * 2


# --- frame 243, pass 2: the seat that writes the text reads his words --------

# Night 149's rows, copied verbatim from `.rota/clickI_night149.db` on
# 2026-10-15. s190 is the Terminologist's relay wake m88. It held the relay's
# paraphrase alone and wrote "instead of raising UsageError" back into the
# criteria (frame 243, interview 2).
CR149 = [f"cr_{n}_confirm_default_on_eof" for n in range(1, 7)]
# The criteria's text when s190 woke, from the wake's `resolved_refs`.
TEXTS149 = dict(zip(CR149, [
    "When 'default_on_eof' is True and stdin is closed, confirm() returns the "
    "default passed to confirm itself (not an option's default).",
    "The 'default_on_eof' argument defaults to False; when it is True and stdin "
    "is closed, confirm() returns the default passed to confirm itself instead "
    "of raising UsageError.",
    "When 'default_on_eof' is True and stdin is closed, confirm() returns the "
    "default passed to confirm itself (not the option's default).",
    "The 'default_on_eof' parameter defaults to False; when it is True and stdin "
    "is closed, confirm() returns the default passed to confirm itself instead "
    "of raising UsageError.",
    "When default_on_eof is True and stdin is closed, confirm() returns the "
    "default passed to confirm itself (not the option's default).",
    "When default_on_eof is True and stdin is closed, confirm() returns the "
    "default passed to confirm itself instead of raising UsageError.",
]))
# The two rulings that had landed when s190 woke, oldest first.
RULINGS149 = [
    {"id": "r_3aa5b4358e", "ask_id": "m73", "reply_id": "m74",
     "per_item": {"confirm_default_on_eof": "approve", **{c: "contest" for c in CR149},
                  "bg_2": "contest"},
     "words": ("Lines 2, 3, 5 and 7 are wrong: today confirm aborts when stdin is "
               "closed, it doesn't raise a usage error. Lines 4 and 6 are also "
               "wrong, because it should return the default that was passed to "
               "confirm itself, not an option's default. Line 8 lists the defaults "
               "tests and the short help code in utils, which have nothing to do "
               "with this change, and it leaves out the termui tests where confirm "
               "is actually tested."),
     "texts": dict(zip(CR149, [
         "confirm() accepts an optional 'default_on_eof' boolean argument; when "
         "True and stdin is closed, it returns the configured default value "
         "instead of raising UsageError.",
         "The 'default_on_eof' argument defaults to False; existing callers "
         "without this flag continue to raise UsageError on EOF as before.",
         "When 'default_on_eof' is True and stdin is closed, confirm() returns "
         "the value specified by the option's default (or None if no default "
         "exists).",
         "The 'default_on_eof' parameter defaults to False, maintaining backward "
         "compatibility where EOF raises UsageError.",
         "When default_on_eof is True and stdin is closed, confirm() returns the "
         "option's configured default value (or None if unset).",
         "When default_on_eof is True and stdin is closed, confirm() must not "
         "raise UsageError.",
     ]))},
    {"id": "r_cb56c527ea", "ask_id": "m85", "reply_id": "m86",
     "per_item": {"confirm_default_on_eof": "approve", **{c: "contest" for c in CR149},
                  "bg_2": "approve"},
     "words": ("Please keep working on this rather than drop it. The tests fail "
               "because they call confirm with no input stream at all, so they "
               "should run it through the test runner with empty input to act "
               "like a closed stdin. Lines 3, 5 and 7 still say it raises a usage "
               "error when today it aborts, and line 8 should touch only termui "
               "and the termui tests, not utils, the defaults tests or a new test "
               "file."),
     "texts": dict(TEXTS149)},
]


def _seed149(tmp_path, contested: bool):
    """Night 149's ticket with its six criteria and the relay m88 to the
    Terminologist. The two rulings land when `contested`."""
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES ('confirm_default_on_eof', 'default_on_eof on confirm', "
               "'in_scope', 'approved', 1, 1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('tk_1_confirm_default_on_eof', 'confirm_default_on_eof', "
               "'let confirm() take a default_on_eof flag')")
    for cid in CR149:
        db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                   "(?, 'tk_1_confirm_default_on_eof', ?)", (cid, TEXTS149[cid]))
    refs = json.dumps(CR149)
    if contested:
        for n, r in enumerate(RULINGS149):
            for mid, verb in ((r["ask_id"], "present"), (r["reply_id"], "reply")):
                db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                           "verb, body_refs, seq) VALUES (?, ?, 'liaison', "
                           "'principal', ?, ?, ?)", (mid, r["ask_id"], verb, refs, n))
            db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, "
                       "status, texts) VALUES (?, ?, ?, ?, ?, 'landed', ?)",
                       (r["id"], r["ask_id"], r["reply_id"], json.dumps(r["per_item"]),
                        r["words"], json.dumps(r["texts"])))
    else:
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                   "body_refs, seq) VALUES ('m85', 'm85', 'liaison', 'principal', "
                   "'present', ?, 87)", (refs,))
    # The principal's verdict m87, which the Liaison relayed as m88.
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
               "verb, body_refs, seq) VALUES ('m87', 'm85', 'm85', 'principal', "
               "'liaison', 'verdict', ?, 89)", (refs,))
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
               "verb, body_refs, seq) VALUES ('m88', 'm87', 'm85', 'liaison', "
               "'terminologist', 'relay', ?, 90)", (refs,))
    db.commit()
    return db


def _relay149(db) -> str:
    """The user prompt of s190's wake, the Terminologist on the relay m88."""
    from rota.core.runner import build_prompt, resolve_inbound
    wake = Wake("terminologist", "message", message_id="m88", detail="relay")
    sb = build("terminologist", db, mode="relay",
               allow=prompts.mode_tools("terminologist", "relay"))
    inbound = resolve_inbound(db, wake)
    _, user = build_prompt("terminologist", sb, wake,
                           push_working_set("terminologist", sb, wake), "", inbound)
    return user


def test_night149_the_terminologists_relay_wake_carries_his_contest_words(tmp_path):
    """Frame 243, night 149: s190 respecified the six criteria from the
    relay's paraphrase. His words now follow the message, whole, after the
    text each ruling contested, as on the builders' wakes."""
    user = _relay149(_seed149(tmp_path, True))
    head = f"\n[{CONTESTS_KEY}]\n"
    assert head in user
    message = user.index("The message that woke you:")
    assert message < user.index(head)
    if "Already run for you" in user:
        assert user.index(head) < user.index("Already run for you")
    # Pass 2b: the block lists each ruling once, oldest first (review 2,
    # finding 2). The texts stand under the ruling, one per criterion.
    for r in RULINGS149:
        assert (f"ruling {r['id']}:\n"
                f"He contested {', '.join(CR149)}.\n"
                + "".join(_contested(c, r['texts'][c], TEXTS149[c])
                          for c in CR149)
                + f"He said: {r['words']}") in user
    assert user.index(f"ruling {RULINGS149[0]['id']}:") < user.index(
        f"ruling {RULINGS149[1]['id']}:")


def test_a_terminologist_relay_with_no_contest_shows_no_block(tmp_path):
    """Frame 243: a relay on criteria he never contested keeps its wake."""
    user = _relay149(_seed149(tmp_path, False))
    assert f"[{CONTESTS_KEY}]" not in user


# --- frame 243, pass 2b: review 2's high and lows -----------------------------

# Night 149's r_ba8ce505c0, the reply m132 to the clarify m131. He approved
# cr_5, and the Liaison relayed the approve as m133. The words are cut here.
APPROVE149 = {
    "id": "r_ba8ce505c0", "ask_id": "m131", "reply_id": "m132",
    "per_item": {CR149[4]: "approve", "test_cr5": "revise"},
    "words": ("Change the implementation, not the line: when the flag is on and "
              "confirm reads end of input, it should return the default it was "
              "given rather than abort, and it should only abort when the flag "
              "is off."),
}


def test_night149_a_relay_of_his_approve_shows_no_old_contest(tmp_path):
    """Review 2, finding 1: m133 relayed his approve on cr_5. Its wake showed
    two old contests on cr_5 as if the criterion were still open."""
    from rota.core.runner import build_prompt, resolve_inbound
    db = _seed149(tmp_path, True)
    r = APPROVE149
    ref = json.dumps([CR149[4]])
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES ('m131', 'm131', 'liaison', 'principal', "
               "'clarify', ?, 130)", (ref,))
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
               "verb, body_refs, seq) VALUES ('m132', 'm131', 'm131', 'principal', "
               "'liaison', 'converse', ?, 131)", (ref,))
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
               "verb, body_refs, seq) VALUES ('m133', 'm132', 'm131', 'liaison', "
               "'terminologist', 'relay', ?, 132)", (ref,))
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, status) "
               "VALUES (?, ?, ?, ?, ?, 'landed')",
               (r["id"], r["ask_id"], r["reply_id"], json.dumps(r["per_item"]),
                r["words"]))
    db.commit()
    wake = Wake("terminologist", "message", message_id="m133", detail="relay")
    sb = build("terminologist", db, mode="relay",
               allow=prompts.mode_tools("terminologist", "relay"))
    inbound = resolve_inbound(db, wake)
    assert inbound["principal_verdict"] == {CR149[4]: "approve"}
    _, user = build_prompt("terminologist", sb, wake,
                           push_working_set("terminologist", sb, wake), "", inbound)
    assert f"[{CONTESTS_KEY}]" not in user
    assert RULINGS149[0]["texts"][CR149[4]] not in user


def test_night149_the_block_says_each_ruling_once(tmp_path):
    """Review 2, finding 2: s190's block said each ruling's words once per
    criterion, 12 entries. Grouped, each ruling heads one entry."""
    user = _relay149(_seed149(tmp_path, True))
    block = user[user.index(f"[{CONTESTS_KEY}]"):]
    for r in RULINGS149:
        assert block.count(f"ruling {r['id']}:") == 1
        assert block.count(r["words"]) == 1
        for c in CR149:
            assert _contested(c, r['texts'][c], TEXTS149[c]) in block


def test_night149_the_criterion_repair_wake_shows_the_block(tmp_path):
    """Review 2, finding 5: s178 woke on the Tester's question m78 with his
    words six times and no text he contested. It kept "UsageError" in 3 of
    6 criteria. The wake now shows the block, as the relay wake does."""
    from rota.core.runner import build_prompt
    db = _seed149(tmp_path, True)
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m78', 'm78', 'tester', "
               "'terminologist', 'question', ?, 91, 'unresolved')",
               (json.dumps(CR149),))
    db.commit()
    sb = build("terminologist", db, mode="criterion_repair",
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    wake = Wake("terminologist", "tick:criterion_repair", refs=("m78",))
    _, user = build_prompt("terminologist", sb, wake, {}, "MODE: criterion_repair")
    head = f"\n[{CONTESTS_KEY}]\n"
    assert head in user
    block = user[user.index(head):]
    old = RULINGS149[0]
    assert (f"ruling {old['id']}:\nHe contested {', '.join(CR149)}.\n") in block
    for c in CR149:
        assert _contested(c, old['texts'][c], TEXTS149[c]) in block


