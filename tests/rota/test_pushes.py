"""What a wake pushes, read as the person doing the job would (the wake
audit, plans/wake-audit.md)."""
import json
import sqlite3
from pathlib import Path

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

NIGHT148 = Path(__file__).resolve().parents[2] / ".rota" / "clickI_night148.db"
CRIT148 = "ver_opt_show_py"
# The label is the wake's text, so the test names it whole.
CONTEST_WORDS_KEY = "the principal said, contesting it"


def _night148_ruling() -> dict:
    """Ruling r_4c8fd5d3ad of night 148, read from the run's database."""
    if not NIGHT148.exists():
        pytest.skip("night 148's database is not in this checkout")
    conn = sqlite3.connect(f"file:{NIGHT148.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        ruling = dict(conn.execute("SELECT * FROM rulings WHERE id = "
                                   "'r_4c8fd5d3ad'").fetchone())
        text = conn.execute("SELECT text FROM criteria WHERE id = ?",
                            (CRIT148,)).fetchone()["text"]
    finally:
        conn.close()
    return {**ruling, "criterion_text": text}


def _seed148(tmp_path, ruled: dict | None):
    """Night 148's bg_3 with its criterion, and the contest ruling when one
    is given."""
    db = init_db(tmp_path / "rota.db")
    text = ruled["criterion_text"] if ruled else "the version message ends with the Python version"
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES ('version_option_show_python', 'show_python on version_option', "
               "'in_scope', 'approved', 1, 1)")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES "
               "('bg_3', 'version_option_show_python', 'running')")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('tk_1', 'version_option_show_python', 'show_python on version_option')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('bg_3', 'tk_1')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?, 'tk_1', ?)",
               (CRIT148, text))
    if ruled:
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                   "body_refs, seq) VALUES (?, ?, 'liaison', 'principal', 'present', "
                   "?, 1)", (ruled["ask_id"], ruled["ask_id"], json.dumps([CRIT148])))
        db.execute("INSERT INTO rulings (id, ask_id, per_item, words, status, texts) "
                   "VALUES (?, ?, ?, ?, 'landed', ?)",
                   (ruled["id"], ruled["ask_id"], ruled["per_item"], ruled["words"],
                    ruled["texts"]))
    db.commit()
    return db


def _criteria_push(db, role: str, mode: str, kind: str) -> list:
    sb = build(role, db, batch_id="bg_3", mode=mode,
               allow=prompts.mode_tools(role, mode))
    pushed = push_working_set(role, sb, Wake(role, kind, refs=("bg_3",)))
    assert "criteria.load" in pushed, sorted(pushed)
    return pushed["criteria.load"]


WAKES148 = [("developer", "batch_start", "tick:batch_start"),
            ("tester", "tests_missing", "tick:tests_missing")]


@pytest.mark.parametrize("role,mode,kind", WAKES148, ids=["developer", "tester"])
def test_night148_the_builders_wake_carries_his_contest_words(tmp_path, role, mode, kind):
    """Frame 243, night 148: s190 built bg_3 from the criterion alone, and
    its prompt held no word of r_4c8fd5d3ad. The words now sit beside the
    criterion's text, verbatim, in the Developer's and the Tester's wake."""
    ruled = _night148_ruling()
    db = _seed148(tmp_path, ruled)
    (row,) = _criteria_push(db, role, mode, kind)
    keys = list(row)
    assert keys[keys.index("text") + 1] == CONTEST_WORDS_KEY
    assert row[CONTEST_WORDS_KEY] == [ruled["words"]]
    assert ("not replace that message with just the command name and the "
            "Python version") in row[CONTEST_WORDS_KEY][0]


@pytest.mark.parametrize("role,mode,kind", WAKES148, ids=["developer", "tester"])
def test_a_criterion_with_no_contest_ruling_shows_nothing_new(tmp_path, role, mode, kind):
    """Frame 243: a criterion the principal never contested keeps the row
    the wake pushed before."""
    db = _seed148(tmp_path, None)
    (row,) = _criteria_push(db, role, mode, kind)
    assert CONTEST_WORDS_KEY not in row
    assert set(row) <= {"id", "ticket_id", "text", "term_refs", "surface_refs",
                        "tested_by"}
