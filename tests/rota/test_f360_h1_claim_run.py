"""
Frame 360, slice 2, shape H1: the Architect's run at the touch is the fact
of a claim.

Roman ruled on 2026-11-08 at 10:01 that a claim of "already done" closes by
itself with a seat's approval, and that the approval is a check that runs,
not a seat's word (`plans/stack.md`, frame 360). The design is
`plans/design-false-claim-2026-11-06.md`, "Amendment of 2026-11-08", H1 as
revised in RA to RD.

The programs below are the probe's own, samples A1 to A4 of
`p360c/arch/live/results.json`. The project is a small copy of icalendar's
`_foldline` at the fork 99619246, which splits a word at the fold.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from rota.core import predicates
from rota.core.db import SessionResult, init_db, session_commit
from rota.core.runner import _as_write
from rota.core.sandbox import build
from tests.rota.test_critic_kept_route import db  # noqa: F401

FORK = "99619246f9c685ff407ab2559a12c18f6dbec9de"
BATCH = "fold_long_lines_in_icalendar_batch"
REQUEST = ("When icalendar writes a long line, fold it at a space where it "
           "can, so that a word is not split, and keep everything else as "
           "before.")
SOURCE = "src/icalendar/parser/string.py"
TEST_FILE = "src/icalendar/tests/test_icalendar.py"


def _claim_rows(db, claimed=FORK):
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('folds_long_lines', ?, 'in_scope', "
               "'approved', 1, 1)", (REQUEST,))
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('t1', 'folds_long_lines', 'fold at a space')")
    for cid in ("c1", "c2", "c3"):
        db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                   "(?, 't1', ?)", (cid, f"criterion {cid}"))
    db.execute("INSERT INTO batches (id, item_id, status, head_commit, "
               "claimed_head) VALUES (?, 'folds_long_lines', 'running', ?, ?)",
               (BATCH, FORK, claimed))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES (?, 't1')",
               (BATCH,))
    for path in (SOURCE, TEST_FILE):
        db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind) "
                   "VALUES (?, ?, 'path')", (BATCH, path))
    for name in ("_escape_char", "_foldline"):
        db.execute("INSERT INTO code_index (grain, grain_kind) VALUES (?, "
                   "'symbol')", (f"{SOURCE}::{name}",))
    db.commit()


@pytest.fixture
def rows(tmp_path):
    """The rows of dry6b.db at the claim of s152, before s153 woke."""
    db = init_db(tmp_path / "rota.db")
    _claim_rows(db)
    yield db
    db.close()


def _end_claim_session(db, sid="s_arch"):
    """An Architect session on `tick:claim` that ended with no run."""
    session_commit(db, SessionResult(session_id=sid, role="architect",
                                     wake_kind="tick:claim",
                                     wake_refs=(BATCH,)))
    db.commit()


def _claim_wakes(db):
    return [w for w in predicates.claim(db) if w.refs == (BATCH,)]


def _tester_wakes(db):
    return [w for w in predicates.tests_missing(db) if w.refs == (BATCH,)]


# ---------------------------------------------------------------------------
# Part 1: the predicate and the wake
# ---------------------------------------------------------------------------

def test_a_batch_with_a_diff_gets_no_claim_wake(rows):
    """A real commit is a change, and so is a claim that a later commit
    replaced. Neither wakes the Architect, and the Tester wakes at once."""
    for claim in (None, "an_older_head"):
        rows.execute("UPDATE batches SET claimed_head = ? WHERE id = ?",
                     (claim, BATCH))
        rows.commit()

        assert _claim_wakes(rows) == []
        assert len(_tester_wakes(rows)) == 1


def test_a_claimed_batch_wakes_the_architect_once_before_the_tester(rows):
    wakes = _claim_wakes(rows)
    assert [(w.role, w.kind) for w in wakes] == [("architect", "tick:claim")]
    assert _tester_wakes(rows) == [], "the Tester must wait for the run"

    _end_claim_session(rows)

    assert _claim_wakes(rows) == [], "a claim wakes the Architect once"
    assert len(_tester_wakes(rows)) == 1


def test_a_quarantined_claim_key_settles_the_claim(rows):
    """Review p1 of frame 360, finding 8: the attempt cap can quarantine
    the key before any session row exists. The Tester must still wake."""
    assert _tester_wakes(rows) == []
    rows.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined) "
                 "VALUES (?, 3, 1)", (f"architect|tick:claim|{BATCH}",))
    rows.commit()

    assert _claim_wakes(rows) == []
    assert len(_tester_wakes(rows)) == 1


def test_a_claim_run_row_settles_the_claim(rows):
    rows.execute("INSERT INTO claim_runs (id, batch_id, commit_sha, program, "
                 "returncode) VALUES ('cr_1', ?, ?, 'print(1)', 0)",
                 (BATCH, FORK))
    rows.commit()

    assert _claim_wakes(rows) == []
    assert len(_tester_wakes(rows)) == 1


def test_the_claim_wake_names_the_request_and_the_touch(rows):
    detail = _claim_wakes(rows)[0].detail

    assert REQUEST in detail, detail
    assert SOURCE in detail and TEST_FILE in detail, detail
    assert f"`_foldline` in {SOURCE}" in detail, detail
    # A name with no word of the request is not the touch's function.
    assert "_escape_char" not in detail, detail
    # The bare `code.run(text)` was copied as the word "text" (pass 2b).
    assert "code.run(text)" not in detail, detail
    assert "inside the call, as step 5 of the claim mode shows" in detail, detail


def test_the_claim_wake_selects_the_claim_mode(rows):
    from rota.core import runner
    from rota.core.scheduler import Wake
    from rota.roles.principal import TICK_WORDS

    wake = Wake("architect", "tick:claim", refs=(BATCH,), detail="x")
    assert runner._mode_key(wake, rows) == "claim"
    assert "tick:claim" in runner.DETAIL_SHOWN
    assert TICK_WORDS["claim"] == "the team could not run the code"
    assert runner._wake_allow(wake, rows) == ["code.source", "code.probe",
                                              "code.run"]


# ---------------------------------------------------------------------------
# Part 2: the door `code.run`
# ---------------------------------------------------------------------------

# `_foldline` of icalendar at 99619246, without the escape rule. It cuts a
# word at the fold, which is the fault of the false claim.
STRING_PY = '''"""Functions for manipulating strings."""

DEFAULT_ENCODING = "utf-8"


def _escape_char(text):
    return text.replace("\\\\", "\\\\\\\\")


def _foldline(line, limit=75, fold_sep="\\r\\n "):
    assert isinstance(line, str)
    assert "\\n" not in line
    folded_lines = []
    current_chars = []
    byte_count = 0
    for char in line:
        char_byte_len = len(char.encode(DEFAULT_ENCODING))
        if current_chars and byte_count + char_byte_len >= limit:
            folded_lines.append("".join(current_chars))
            current_chars = []
            byte_count = 0
        current_chars.append(char)
        byte_count += char_byte_len
    if current_chars:
        folded_lines.append("".join(current_chars))
    return fold_sep.join(folded_lines)


foldline = _foldline
'''

# The probe's programs, to the byte (`results.json`, `runs[n].text`).
A1_RUN2 = r'''import sys
sys.path.insert(0, '.')
from icalendar.parser.string import _foldline

# Test case: a long line with spaces (single line)
long_line = 'A very long event name that should be folded properly without splitting words like calendarization or internationalization'

result = _foldline(long_line)
print('Input length:', len(long_line))
print('Output length:', len(result))
print('--- Output ---')
print(repr(result))
'''

A2_RUN3 = r'''import sys
sys.path.insert(0, '.')
from icalendar.parser.string import _foldline

# Test case from request: long line with spaces to avoid splitting words
long_text = "DT;TZID=UTC:20231225T090000Z\nSUMMARY:This is a very long event title that should be folded at a space where it can, so that a word is not split, and keep everything else as before."
lines = long_text.split('\n')
for line in lines:
    try:
        result = _foldline(line)
        print(f'Input: {repr(line)}')
        print(f'Output: {repr(result)}')
    except AssertionError as e:
        print(f'AssertionError raised for: {repr(line)}')
'''

A3_RUN1 = r'''import sys
sys.path.insert(0, '.')
from icalendar.parser.string import _foldline

# Test case: a long line with spaces that should be folded
test_input = "This is a very long line that needs to be folded at a space so that words are not split but keep everything else as before."
result = _foldline(test_input, 75)
print(f"Input length: {len(test_input)}")
print(f"Output:\n{result}")
'''

A4_RUN1 = r'''def _foldline(line):
    if len(line) > 75:
        words = line.split()
        result = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= 75:
                current_line += (word if not current_line else " " + word)
            else:
                result.append(current_line)
                current_line = word
        if current_line:
            result.append(current_line)
        return "\n".join(result)
    return line

long_text = "This is a very long line that should be folded at some point to ensure it does not exceed the maximum length allowed by the mail client or protocol specification which often limits lines to 75 characters."
print(_foldline(long_text))
'''


def _git(at, *args):
    return subprocess.run(["git", "-C", str(at), *args], capture_output=True,
                          text=True, check=True).stdout


@pytest.fixture
def project(tmp_path):
    """A clone of the touch at the fork, as the claimed batch's worktree."""
    root = tmp_path / "icalendarI"
    files = {"src/icalendar/__init__.py": "",
             "src/icalendar/parser/__init__.py": "",
             SOURCE: STRING_PY,
             TEST_FILE: "def test_nothing():\n    pass\n"}
    for rel, body in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(body.encode("utf-8"))
    _git(tmp_path, "init", "-q", str(root))
    _git(root, "config", "core.autocrlf", "false")
    _git(root, "add", "-A")
    _git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
         "-m", "fork")
    head = _git(root, "rev-parse", "HEAD").strip()
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)",
               (str(root),))
    _claim_rows(db)
    db.execute("UPDATE batches SET head_commit = ?, claimed_head = ?, "
               "worktree = ? WHERE id = ?", (head, head, str(root), BATCH))
    db.commit()
    yield db, root
    db.close()


def _architect(db):
    return build("architect", db, batch_id=BATCH,
                 allow=["code.source", "code.probe", "code.run"])


def _land(db, sb, sid="s_claim_run"):
    session_commit(db, SessionResult(
        session_id=sid, role="architect", wake_kind="tick:claim",
        wake_refs=(BATCH,), writes=[_as_write(w) for w in sb.ctx.writes]))
    db.commit()


def _refusal(sb, text):
    with pytest.raises(ValueError) as exc:
        sb.call("code.run", text=text)
    assert sb.ctx.writes == []
    return str(exc.value)


def _row(db):
    return db.execute("SELECT * FROM claim_runs WHERE batch_id = ? "
                      "ORDER BY rowid DESC", (BATCH,)).fetchone()


def test_a4_defines_its_own_foldline_and_is_refused(project):
    """A4 tested its own `_foldline`, and its record said that the claim
    holds (the amendment, H1)."""
    db, _ = project

    said = _refusal(_architect(db), A4_RUN1)

    assert "`_foldline`" in said, said
    assert said == ("The program defines `_foldline`, and "
                    "src/icalendar/parser/string.py already defines it, so "
                    "send a program that imports `_foldline` from "
                    "icalendar.parser.string and calls it."), said


def test_a_program_that_patches_the_touch_is_refused(project):
    db, _ = project
    text = ("import icalendar.parser.string as s\n"
            "s._foldline = lambda line: line\n"
            "print(s._foldline('x'))\n")

    said = _refusal(_architect(db), text)

    assert said.startswith("The program changes `icalendar.parser.string."
                           "_foldline`"), said


def test_a_program_that_imports_nothing_from_the_touch_is_refused(project):
    db, _ = project

    said = _refusal(_architect(db), "import textwrap\nprint(textwrap.fill('a b'))\n")

    assert said == ("The program imports nothing from the touch, so send a "
                    "program that imports a name from icalendar.parser.string "
                    "and calls it."), said


def test_a_program_that_calls_no_touch_name_is_refused(project):
    """`import icalendar` with no call of the touch (RA F5)."""
    db, _ = project

    said = _refusal(_architect(db), "import icalendar\nprint('done')\n")

    assert said == ("The program calls no name that it imports from the "
                    "touch, so send a program that calls one, such as "
                    "`_foldline` from icalendar.parser.string."), said


def test_a_name_bound_by_an_import_is_exempt(project):
    db, _ = project
    sb = _architect(db)

    out = sb.call("code.run", text=A1_RUN2)

    assert out["returncode"] == 0, out
    assert out["note"] == "The run is recorded. End the session.", out


def test_a2_is_accepted_and_the_row_holds_the_exact_bytes(project):
    db, _ = project
    sb = _architect(db)

    out = sb.call("code.run", text=A2_RUN3)
    _land(db, sb)

    assert out["returncode"] == 0, out
    row = _row(db)
    assert row["program"] == A2_RUN3
    assert b"as befo\\r\\n re.'" in row["stdout"], row["stdout"]
    assert b"at a space w\\r\\n here" in row["stdout"], row["stdout"]
    assert json.loads(row["imported"]) == ["icalendar.parser.string._foldline"]
    assert row["returncode"] == 0 and row["unfinished"] == 0
    assert row["session_id"] == sb.ctx.session_id or row["session_id"] == ""


def test_a_plain_print_of_a_fold_keeps_its_cr_lf(project):
    """RA F3: the pipe's decode turned A3's fold into two line feeds."""
    db, _ = project
    sb = _architect(db)

    sb.call("code.run", text=A3_RUN1)
    _land(db, sb)

    stdout = _row(db)["stdout"]
    assert b"so that words \r\n are not split" in stdout, stdout
    assert b"\r\r\n" not in stdout, stdout


def test_a1_leaves_the_worktree_clean(project):
    db, root = project

    _architect(db).call("code.run", text=A1_RUN2)

    assert _git(root, "status", "--porcelain", "--untracked-files=all") == ""
    assert not (root / ".rota").exists()


def test_the_door_puts_back_what_the_program_wrote(project):
    """A4's first try wrote over string.py (RA F13)."""
    db, root = project
    text = ("from icalendar.parser.string import _foldline\n"
            "print(_foldline('a b'))\n"
            "open('src/icalendar/parser/string.py', 'w').write('x = 1\\n')\n"
            "open('notes.txt', 'w').write('hello')\n")
    sb = _architect(db)

    out = sb.call("code.run", text=text)
    _land(db, sb)

    assert _git(root, "status", "--porcelain", "--untracked-files=all") == ""
    assert (root / SOURCE).read_bytes() == STRING_PY.encode("utf-8")
    row = _row(db)
    assert row["wrote_tree"] == 1
    assert sorted(json.loads(row["wrote_paths"])) == ["notes.txt", SOURCE]
    assert "the door put them back" in out["note"], out


def test_a_failing_program_is_recorded_with_its_error(project):
    """A1's first run: `_foldline` asserts on a line feed (RC)."""
    db, _ = project
    text = ("from icalendar.parser.string import _foldline\n"
            "print(_foldline('a\\nb'))\n")
    sb = _architect(db)

    out = sb.call("code.run", text=text)
    _land(db, sb)

    row = _row(db)
    assert row["returncode"] == 1, out
    assert row["stderr"].rstrip().splitlines()[-1] == "AssertionError", row["stderr"]


def test_the_row_holds_stderr_as_the_program_wrote_it(project):
    """Review p1 of frame 360, finding 1: `read_text` turned CR LF into LF."""
    db, _ = project
    text = ("import sys\n"
            "from icalendar.parser.string import _foldline\n"
            "print(_foldline('a b'))\n"
            "sys.stderr.write('one\\r\\ntwo\\r\\n')\n")
    sb = _architect(db)

    sb.call("code.run", text=text)
    _land(db, sb)

    assert "one\r\ntwo\r\n" in _row(db)["stderr"], repr(_row(db)["stderr"])


def test_a_program_that_patches_vars_of_the_touch_is_refused(project):
    """Review p1 of frame 360, finding 2: a subscript store on `vars(s)`
    passed all four refusals, and the run printed "patched"."""
    db, _ = project
    text = ("import icalendar.parser.string as s\n"
            "vars(s)['_foldline'] = lambda line: 'patched'\n"
            "print(s._foldline('x'))\n")

    said = _refusal(_architect(db), text)

    assert said == ("The program changes `vars(icalendar.parser.string)`, the "
                    "names of a module of the touch, so send a program that "
                    "calls the code of the touch as it is."), said


def test_the_door_removes_what_the_program_wrote_in_hidden_paths(project):
    """Review p1 of frame 360, finding 3: a write to an ignored path and to
    `.rota/` stayed after the run."""
    db, root = project
    exclude = root / _git(root, "rev-parse", "--git-path",
                          "info/exclude").strip()
    exclude.parent.mkdir(parents=True, exist_ok=True)
    exclude.write_bytes(b"build/\n")
    (root / ".rota").mkdir()
    (root / ".rota" / "kept.txt").write_bytes(b"kept")
    text = ("import os\n"
            "from icalendar.parser.string import _foldline\n"
            "print(_foldline('a b'))\n"
            "os.makedirs('build', exist_ok=True)\n"
            "open('build/left.txt', 'w').write('x')\n"
            "open('.rota/left.txt', 'w').write('x')\n")
    sb = _architect(db)

    out = sb.call("code.run", text=text)
    _land(db, sb)

    assert not (root / "build").exists()
    assert not (root / ".rota" / "left.txt").exists()
    assert (root / ".rota" / "kept.txt").read_bytes() == b"kept"
    assert sorted(json.loads(_row(db)["wrote_paths"])) == [
        ".rota/left.txt", "build/left.txt"]
    assert "the door put them back" in out["note"], out


def test_a_batch_with_no_worktree_is_refused(project):
    """Second look of review p1, fix 2: with no worktree row the cleanup
    would reach rota's own .rota/ folder."""
    db, _ = project
    db.execute("UPDATE batches SET worktree = NULL WHERE id = ?", (BATCH,))
    db.commit()

    said = _refusal(_architect(db), A1_RUN2)

    assert said == (f"Batch {BATCH} has no worktree, so the door cannot run a "
                    f"program apart from the project. End the session."), said


def test_one_run_per_session_and_only_on_a_claim(project):
    db, _ = project
    sb = _architect(db)
    sb.call("code.run", text=A1_RUN2)

    with pytest.raises(ValueError, match="recorded already. End the session"):
        sb.call("code.run", text=A2_RUN3)

    db.execute("UPDATE batches SET claimed_head = NULL WHERE id = ?", (BATCH,))
    db.commit()
    with pytest.raises(ValueError, match="is not a claim"):
        _architect(db).call("code.run", text=A1_RUN2)


def test_the_claim_tools_hold_no_door_that_takes_an_output():
    """Measure 6 of H2: the seat types no output and no verdict."""
    tools = Path("rota/roles/prompts/architect/claim.tools").read_text(
        encoding="utf-8").split()
    assert tools == ["code.source", "code.probe", "code.run"]


# ---------------------------------------------------------------------------
# Part 3: the readers of the run
# ---------------------------------------------------------------------------

def _a3_on_record(db):
    sb = _architect(db)
    sb.call("code.run", text=A3_RUN1)
    _land(db, sb)


def _tester_prompt(db):
    from rota.core.runner import build_prompt
    from rota.core.scheduler import Wake

    [wake] = _tester_wakes(db)
    _, user = build_prompt("tester", build("tester", db, batch_id=BATCH),
                           wake, {}, "")
    return user


def test_the_tester_of_a_claim_reads_the_printout_with_fold_marks(project):
    db, _ = project
    _a3_on_record(db)

    user = _tester_prompt(db)

    # The Tester interview of 2026-11-08: the call shows the input and the
    # width, the literal in place of the program's name `test_input`.
    assert ("The architect called `_foldline('This is a very long line that "
            "needs to be folded at a space so that words are not split but "
            "keep everything else as before.', 75)` on the code, and it "
            "printed: Input length: 123") in user, user
    # The fold's own space becomes the mark, and the word's space stays.
    assert "so that words  ⏎ are not split" in user, user
    assert ("as before.. A ⏎ marks a fold: a line break and then a space. "
            "The run shows what the code does") in user, user
    assert "Write the result that the criterion's words give" in user, user
    assert user.count("The architect called") == 1, user


def test_a_change_batch_wake_holds_no_printout(project):
    db, _ = project
    _a3_on_record(db)
    db.execute("UPDATE batches SET claimed_head = NULL WHERE id = ?", (BATCH,))
    db.commit()

    user = _tester_prompt(db)

    assert "The architect " not in user, user
    assert "⏎" not in user, user


def test_the_critic_note_names_the_run(project):
    from rota.roles.api import critic_claim_note

    db, _ = project
    _a3_on_record(db)

    note = critic_claim_note(db, BATCH)

    assert note.startswith(
        "No code changed on this batch. The Developer claims the criteria "
        "are met. The tests and one run of the code are the evidence. The "
        "architect called `_foldline('This is a very long line"), note
    assert "words  ⏎ are not split" in note, note
    assert build("critic", db, batch_id=BATCH).call("code.read")["note"] == note


def test_the_critic_note_with_no_run_stays_as_it_was(project):
    from rota.roles.api import CRITIC_CLAIM_NOTE, critic_claim_note

    db, _ = project

    assert critic_claim_note(db, BATCH) == CRITIC_CLAIM_NOTE


def test_each_state_of_the_run_has_its_sentence(project):
    from rota.roles.api import claim_run_words

    db, _ = project
    assert claim_run_words(db, BATCH) == "No run of the code is on record."
    sb = _architect(db)
    sb.call("code.run", text="from icalendar.parser.string import _foldline\n"
                             "_foldline('a\\nb')\n")
    _land(db, sb)
    assert claim_run_words(db, BATCH) == (
        "The architect called `_foldline('a\\nb')` on the code, and it "
        "stopped with an error: AssertionError.")
    db.execute("UPDATE claim_runs SET returncode = 0, stdout = x'', "
               "stderr = ''")
    assert claim_run_words(db, BATCH).endswith("and it printed nothing.")
    db.execute("UPDATE claim_runs SET unfinished = 1")
    assert claim_run_words(db, BATCH).endswith(
        "and it did not finish in 60 seconds.")


def test_a_run_with_no_readable_call_shows_its_last_line(project):
    """With no call of a touch name on record, the sentence quotes the
    program's last line. A printout with no fold has no mark phrase."""
    from rota.roles.api import claim_run_words

    db, _ = project
    sb = _architect(db)
    sb.call("code.run", text=A1_RUN2)
    _land(db, sb)
    db.execute("UPDATE claim_runs SET imported = '[]', stdout = CAST(? AS BLOB)",
               ("short\n",))

    assert claim_run_words(db, BATCH) == (
        "The architect ran a program that ends with `print(repr(result))` on "
        "the code, and it printed: short.")


def test_the_shift_page_no_longer_says_the_tests_check_the_claim(rows):
    from rota.roles.principal import _built_words

    batch = rows.execute("SELECT * FROM batches WHERE id = ?", (BATCH,)).fetchone()

    said = _built_words(rows, batch)

    assert "check the claim" not in said, said
    assert said.startswith(f" The change {BATCH} changes no code. The team "
                           f"claims that the code already does this."), said


# ---------------------------------------------------------------------------
# Part 4: the P1 door defect (the amendment, H8)
# ---------------------------------------------------------------------------

def test_a_pass_on_a_test_the_critic_said_does_not_encode_is_refused(db):
    """P1 sample 1 claimed `encodes=False` for c2 and then passed with
    `test: tst_fold_c2`. The `test:` route did not read the claim."""
    from tests.rota.test_critic_kept_route import C1, C3, _critic, _refused

    sb = _critic(db)
    sb.call("verdicts.claim_encodes", criterion_id=C3, encodes=False)

    said = _refused(sb, {C1: "return True", C3: "test: tst_c3"})

    assert said.startswith(
        f"you claimed in this session that the test of {C3} does not encode "
        f"{C3}, so send msg.challenge_tester with refs naming {C3} and "
        f"tst_c3, not a pass that rests on it."), said


def test_the_same_pass_with_no_claim_still_lands(db):
    """The control: the route holds the test when no claim says otherwise.
    The pass lands, as review p1 of frame 360 (finding 5) asked."""
    from tests.rota.test_critic_kept_route import C1, C3, _critic, _land

    sb = _critic(db)
    lines = {C1: "return True", C3: "test: tst_c3"}
    with pytest.raises(ValueError) as exc:
        sb.call("verdicts.emit", batch_id="bg_2", result="pass", lines=lines)
    assert "does not encode" not in str(exc.value)
    row = _land(sb, lines, held=False)
    assert row["result"] == "pass", row
    assert json.loads(row["routes"]) == {C1: "added", C3: "test"}, row


# ---------------------------------------------------------------------------
# Pass 2b: the call form of the run, and the run sentence at the prints door
# ---------------------------------------------------------------------------

def test_the_bare_word_text_is_refused_with_its_cause(project):
    """On the register case the Architect sent `code.run(text)` three times
    per run. The protocol binds the bare name to the word "text", and the
    refusal named the import, not the missing program."""
    db, _ = project

    said = _refusal(_architect(db), "text")

    assert said == ("The door got `text`, which is not a program with an "
                    "import and a call, so send the program's source inside "
                    "the call, from its import line to its last print "
                    "line."), said
    # A text with an import or a call keeps the refusal of the touch, which
    # names the part that it lacks.
    assert _refusal(_architect(db), "_foldline\n").startswith(
        "The door got `_foldline`"), "_foldline"
    assert _refusal(_architect(db), "print('x')\n").startswith(
        "The program imports nothing from the touch")


def test_the_claim_prompt_shows_a_program_inside_the_call():
    """The prompt's step 5 said `code.run(text)`, and the seat copied it.
    The example call parses to a text of four lines at most that holds an
    import and a call."""
    import ast
    import textwrap

    from rota.llm.toolproto import extract

    prompt = Path("rota/roles/prompts/architect/claim.md").read_text(
        encoding="utf-8")
    assert "code.run(text)" not in prompt, prompt
    lines = prompt.splitlines()
    start = next(i for i, ln in enumerate(lines) if "code.run(text=" in ln)
    end = next(i for i in range(start, len(lines)) if lines[i].endswith("')"))
    [call] = extract("TOOL: " + textwrap.dedent("\n".join(lines[start:end + 1])))
    program = call.args["text"]
    nodes = list(ast.walk(ast.parse(program)))
    assert call.name == "code.run" and not call.pos, call
    assert len(program.splitlines()) <= 4, program
    assert any(isinstance(n, ast.ImportFrom) for n in nodes), program
    assert any(isinstance(n, ast.Call) for n in nodes), program


def test_the_run_sentence_does_not_reach_the_prints_door(rows):
    """The prints door of `tests.encode` reads the criterion, its ticket and
    item, the glossary, the statements, the principal's entries and the
    ledger. The run sentence says "printed", and it is in none of them, so
    an encode on the return value lands."""
    from rota.roles.api import claim_run_words

    rows.execute("UPDATE items SET text = 'When icalendar folds a long line, "
                 "fold it at a space so that a word is not split.'")
    rows.execute("UPDATE criteria SET text = 'Each fold of _foldline falls at "
                 "a space.', surface_refs = ? WHERE id = 'c1'",
                 (json.dumps([f"{SOURCE}::_foldline"]),))
    rows.execute(
        "INSERT INTO claim_runs (id, batch_id, commit_sha, session_id, "
        "program, stdout, stderr, returncode, unfinished, imported, "
        "wrote_tree, wrote_paths) VALUES ('cr1', ?, ?, 's_arch', ?, ?, '', 0, "
        "0, ?, 0, '[]')",
        (BATCH, FORK, "from icalendar.parser.string import _foldline\n"
                      "print(_foldline('wo rds', 3))\n",
         b"wo\r\n rds\n", json.dumps(["icalendar.parser.string._foldline"])))
    rows.commit()
    assert " printed: " in claim_run_words(rows, BATCH)
    tb = build("tester", rows, batch_id=BATCH)
    tb.call("tests.triage", criterion_id="c1", verdict="encodable")

    out = tb.call("tests.encode", id="tst_fold", criterion_id="c1",
                  path="src/icalendar/tests/test_fold.py",
                  body="from icalendar.parser.string import _foldline\n\n"
                       "def test_fold():\n"
                       "    out = _foldline('aaa bbb ' * 20, 75)\n"
                       "    assert 'aa\\r\\n a' not in out\n")

    assert out.get("id") == "tst_fold", out
