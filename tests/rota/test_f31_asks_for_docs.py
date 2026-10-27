"""
F31: one reader decides whether a criterion's words ask for documentation.

Roman ruled at 2026-10-24 01:05 that a criterion asks for the code's
documentation with the words "docstring", "document" or "help text"
(DECISIONS.md, "A docstring line counts for a criterion that asks for one").
He ruled the same words again on 2026-10-27. Five word lists in api.py
decided the question before, and they disagreed
(`plans/rootfix-audit-2026-10-27-b.md`, F31).
"""
from __future__ import annotations

import pytest

from rota.core.harness import inherited_id
from rota.core.sandbox import build
from tests.rota.test_t0_sandbox import db  # noqa: F401


@pytest.mark.parametrize("text", [
    "The docstring of work names its argument.",
    "The DOCSTRINGS name their arguments.",
    "The documentation of work names its argument.",
    "work is documented.",
    "The function must document its return value.",
    "The --version flag help text must document the new show_python flag.",
    "The Help  Text names the flag.",
])
def test_the_ruled_words_ask_for_documentation(text):
    from rota.roles.api import asks_for_docs
    assert asks_for_docs(text)


@pytest.mark.parametrize("text", [
    "load_document raises ValueError when the file is empty.",
    "format_filename_docstring is a constant.",
    "The command explains and describes its effect.",
    "The command prints help when asked.",
    "",
])
def test_other_words_ask_for_no_documentation(text):
    """The words match as words, so an identifier that holds one asks for
    nothing (frame 322, review 2, finding 1: `load_document`)."""
    from rota.roles.api import asks_for_docs
    assert not asks_for_docs(text)


# Verbatim from the `criteria` tables of nights 142 and 157. Each mentions a
# ruled word under a negation and asks for behaviour (F31 review, finding 1).
_N142_C2 = ("The show_python argument passed to version_option is a boolean "
            "flag that, when True, triggers the inclusion of the Python "
            "version string in the --version output; it does not affect help "
            "text or act as a user-facing command-line option.")
_N157 = ("The help text for the version_option must not describe a "
         "--show-python flag, as it is a setting passed to the option, not a "
         "command-line flag.")


@pytest.mark.parametrize("text", [
    _N142_C2, _N157,
    "The loader has no document cache.",
    "The command never prints the docstring.",
], ids=["night142_c2", "night157", "no", "never"])
def test_a_negated_mention_asks_for_no_documentation(text):
    from rota.roles.api import asks_for_docs
    assert not asks_for_docs(text)


@pytest.mark.parametrize("text", [
    "The function does not raise, and its docstring names the example.",
    "The docstring shows a/b/c.txt as c.txt.",
    "The loader reads all documents in the folder.",
], ids=["other_clause", "dotted_path", "noun_documents"])
def test_an_ask_beside_a_negation_or_a_dot_still_counts(text):
    """A negation counts in its own clause only. The noun "documents"
    counts, because the ruled word is "document" and no word class is
    ruled."""
    from rota.roles.api import asks_for_docs
    assert asks_for_docs(text)


# Night 170's c_1, verbatim from the `criteria` table
# (`plans/night170-read.md`, section 3). Its surface is the function.
_CRIT = "c_1_format_filename_example"
_C1 = ("The docstring for format_filename must include an example "
       "demonstrating that when shorten=True, the path a/b/c.txt is displayed "
       "as c.txt.")
_PROJECT = "tests/test_formatting.py"
# The shape of s196's bodies: they asserted on the return value, so they
# tested the code and not the docstring (`plans/frame343-read.md`, 66).
_S196 = ("from click.utils import format_filename\n"
         "def test_format_filename_example():\n"
         "    assert format_filename('a/b/c.txt', shorten=True) == 'c.txt'\n")


def _batch(db, text=_C1):
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i1','format_filename example','in_scope',"
               "'approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) "
               "VALUES ('tk1','i1','the docstring of format_filename')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
               "VALUES (?, 'tk1', ?, '[\"src/click/utils.py::format_filename\"]')",
               (_CRIT, text))
    db.execute("INSERT INTO batches (id, item_id, status) "
               "VALUES ('b1','i1','running')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) "
               "VALUES ('b1','tk1')")
    # The row `harness.inherit` writes: the derived id, and no criterion.
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES (?, 'b1', NULL, ?, 'def test_old():\n    pass\n')",
               (inherited_id(_PROJECT), _PROJECT))
    db.commit()


def _refusal(db):
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    sb.call("tests.triage", criterion_id=_CRIT, verdict="encodable")
    with pytest.raises(ValueError) as exc:
        sb.call("tests.encode", id="t_c1", criterion_id=_CRIT, path=_PROJECT,
                body=_S196, batch_id="b1")
    return str(exc.value)


def test_the_test_file_door_names_the_docstring_for_night_170s_c_1(db):
    """Night 170 W1: twelve encodes for c_1 met the test-file door, and each
    body asserted on what the code returns. The door says what a test of a
    documentation criterion reads, before the path it offers."""
    _batch(db)
    said = _refusal(db)
    note = (f"{_CRIT} asks for documentation, so its test asserts on the "
            f"documentation, such as `format_filename.__doc__`, and not on "
            f"what the code does.")
    assert note in said, said
    assert said.index(note) < said.index("send this encode again"), said


def test_the_test_file_door_says_nothing_of_docs_for_a_behaviour_criterion(db):
    _batch(db, text="When shorten=True, format_filename returns only the "
                    "basename of the provided path.")
    said = _refusal(db)
    assert "asks for documentation" not in said, said
    assert "holds the project's own tests" in said, said
