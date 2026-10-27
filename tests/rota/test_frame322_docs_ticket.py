"""Frame 322, pass 2: a ticket whose headline names documentation takes
documentation criteria only.

Night 166's s185 wrote two behaviour criteria and one docstring criterion on
the docstring ticket of `format_filename` in its first turn. His m77 called
the two wrong: "only the docstring changes and the code stays the same".
The texts below are the quotes of `plans/frame322-we-read.md`, section 1.
s116's three `get_app_dir` criteria are a behaviour ticket's, and the door
leaves them alone.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import prompts

_DOC_ITEM = ("Give format_filename one example in its docstring: with shorten "
             "set to True, the path a/b/c.txt shows as c.txt.")
_DOC_TK = "tk_1_format_filename_example"
_DOC_HEAD = ("with shorten set to true, the path a/b/c.txt shows as c.txt in "
             "the docstring of format_filename")
_APP_HEAD = ("in get_app_dir on Windows, when APPDATA or LOCALAPPDATA is not "
             "set, use the AppData Roaming or AppData Local folder under the "
             "user's profile")

# s185's turn 1, in its order.
_S185 = (
    ("c_1_format_filename_example", "When shorten=True, format_filename strips "
     "the directory prefix from the path."),
    ("c_2_format_filename_example", "When shorten=True, format_filename returns "
     "only the basename of the provided path."),
    ("c_3_format_filename_example", "The docstring of format_filename must "
     "include an example demonstrating that with shorten=True, a/b/c.txt is "
     "displayed as c.txt."),
)

# s116's turn 1 on night 166, from its completion. The read names the turn
# and does not quote it.
_S116 = (
    ("c_1", "When get_app_dir is invoked on Windows with roaming=True and "
     "APPDATA/LOCALAPPDATA are unset, the returned path must be under the "
     "user's home directory (e.g., C:\\Users\\<user>) rather than a bare home "
     "root."),
    ("c_2", "When get_app_dir is invoked on Windows with roaming=False and "
     "APPDATA/LOCALAPPDATA are unset, the returned path must be under the "
     "user's home directory (e.g., C:\\Users\\<user>) rather than a bare home "
     "root."),
    ("c_3", "The fallback logic in get_app_dir for Windows must explicitly "
     "check if the environment variable (APPDATA or LOCALAPPDATA) is None "
     "before falling back to os.path.expanduser(\"~\")."),
)

_MARK = "The headline names the documentation"


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    for item, text in (("format_filename_example", _DOC_ITEM),
                       ("get_app_dir_windows", _APP_HEAD)):
        conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                     "version) VALUES (?, ?, 'in_scope', 'approved', 1, 1)",
                     (item, text))
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES (?, ?, ?)",
                 (_DOC_TK, "format_filename_example", _DOC_HEAD))
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES (?, ?, ?)",
                 ("tk_1", "get_app_dir_windows", _APP_HEAD))
    conn.commit()
    return conn


def _seat(db, mode="criteria"):
    return build("terminologist", db, mode="normal",
                 allow=prompts.mode_tools("terminologist", mode))


def _specify(sb, cid, text, ticket_id=_DOC_TK, surface="format_filename"):
    return sb.call("criteria.specify", id=cid, ticket_id=ticket_id, text=text,
                   term_refs=[], surface_refs=[surface])


def _landed(sb):
    return [w[1] for w in sb.ctx.writes if w[0] == "criteria"]


def test_s185_behaviour_criteria_are_refused_and_the_docstring_one_lands(db):
    sb = _seat(db)
    for cid, text in _S185[:2]:
        with pytest.raises(ValueError) as exc:
            _specify(sb, cid, text)
        assert _MARK in str(exc.value)
    _specify(sb, *_S185[2])
    assert _landed(sb) == ["c_3_format_filename_example"]


def test_s116_get_app_dir_criteria_are_untouched(db):
    sb = _seat(db)
    for cid, text in _S116:
        try:
            _specify(sb, cid, text, ticket_id="tk_1", surface="get_app_dir")
        except ValueError as exc:
            assert _MARK not in str(exc)
    assert {"c_1", "c_3"} <= set(_landed(sb))


def test_respecify_into_behaviour_is_refused_with_the_same_text(db):
    db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
               "VALUES (?, ?, ?, '[\"format_filename\"]')",
               ("c_3_format_filename_example", _DOC_TK, _S185[2][1]))
    db.commit()
    with pytest.raises(ValueError) as first:
        _specify(_seat(db), *_S185[0])
    sb = _seat(db, mode="criterion_repair")
    with pytest.raises(ValueError) as again:
        sb.call("criteria.respecify", id="c_3_format_filename_example",
                text=_S185[0][1], surface_refs=["format_filename"])
    assert str(again.value) == str(first.value)
    assert not _landed(sb)


_REWRITE = "Write the criterion on the documentation and send it again."


def test_the_refusal_names_the_headline_and_ends_on_the_rewrite(db):
    """Pass 3: on 5 of 5 runs of the register case, the seat obeyed the
    refusal's last instruction, a Vision Keeper challenge, and the session
    ended before a retry (`plans/frame322-case-read.md`, section 2)."""
    with pytest.raises(ValueError) as exc:
        _specify(_seat(db), *_S185[1])
    said = str(exc.value)
    assert _DOC_HEAD in said
    assert "The headline names the documentation" in said
    assert "the docstring, the docs or the help text must say" in said
    assert "challenge_vision_keeper" not in said
    assert said.endswith(_REWRITE)
    assert said.count("Write ") == 1


def test_the_criteria_brief_routes_a_mixed_ticket_once():
    """Pass 3: the brief holds the Vision Keeper route, and the seat reads
    it before any refusal (`plans/frame322-case-read.md`, the repair)."""
    brief = prompts.compose("terminologist", "criteria")
    head = ("**A ticket whose headline names the docstring or the documentation "
            "takes documentation")
    assert brief.count(head) == 1
    line = brief[brief.index(head):].split("\n\n", 1)[0]
    assert "msg.challenge_vision_keeper" in line
    assert "after its criteria land" in line


def _ticket(db, tid, headline):
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES (?, ?, ?)",
               (tid, "get_app_dir_windows", headline))
    db.commit()


def test_a_headline_with_load_document_takes_a_behaviour_criterion(db):
    """Review 2, finding 1: a substring made this behaviour ticket read as a
    documentation ticket."""
    _ticket(db, "tk_2", "load_document raises ValueError on an empty file")
    sb = _seat(db)
    _specify(sb, "c_9", "load_document raises ValueError when the file is "
             "empty.", ticket_id="tk_2", surface="load_document")
    assert _landed(sb) == ["c_9"]


def test_a_headline_with_the_docstring_of_refuses_a_behaviour_criterion(db):
    _ticket(db, "tk_2", "fix the example in The Docstring of load_document")
    with pytest.raises(ValueError) as exc:
        _specify(_seat(db), "c_9", "The loader raises ValueError when the "
                 "file is empty.", ticket_id="tk_2", surface="load_document")
    assert "The headline names the documentation" in str(exc.value)


def test_an_identifier_with_document_admits_no_behaviour_criterion(db):
    """F31: the ruled words match as words, so `load_document` in a
    criterion names no documentation."""
    _ticket(db, "tk_2", "fix the example in The Docstring of load_document")
    with pytest.raises(ValueError) as exc:
        _specify(_seat(db), "c_9", "load_document raises ValueError when the "
                 "file is empty.", ticket_id="tk_2", surface="load_document")
    assert "The headline names the documentation" in str(exc.value)


@pytest.mark.parametrize("text", [
    "The help text of format_filename names the shorten flag.",
    "format_filename is documented with one example.",
    "The docs of format_filename show one example.",
])
def test_a_criterion_in_the_ruled_words_lands_on_a_docstring_ticket(db, text):
    sb = _seat(db)
    _specify(sb, "c_9", text)
    assert _landed(sb) == ["c_9"]


# Pass 3b: the gate at 1277b6b4 recorded the docstring case green 5 of 5 on
# qwen3.5:9b. The follow check still read it red: the criteria mode sent
# msg.answer_tester(refs=['tk_c4d9c0']), and the door offered
# msg.report_liaison, which the mode does not hold.
_NO_TERM = ("an answer from the glossary carries a term, and "
            f"refs=['{_DOC_TK}'] names none. The glossary does not carry this")


def test_the_criteria_mode_is_offered_no_call_it_does_not_hold(db):
    sb = _seat(db)
    with pytest.raises(ValueError) as exc:
        sb.call("msg.answer_tester", refs=[_DOC_TK], round_no=0)
    said = str(exc.value)
    assert said == f"{_NO_TERM}.", said
    assert "msg.report_liaison" not in sb.functions()


def test_a_mode_that_holds_the_report_is_offered_it_unchanged(db):
    sb = _seat(db, mode="question")
    assert "msg.report_liaison" in sb.functions()
    with pytest.raises(ValueError) as exc:
        sb.call("msg.answer_tester", refs=[_DOC_TK], round_no=0)
    assert str(exc.value) == (f"{_NO_TERM}: send msg.report_liaison"
                              f"(refs=['{_DOC_TK}']) with the same refs.")
