"""
Frame 321: the prints door reads prose words only, and a sentence about a
docstring does not count.

Night 164's cr_1 said "the path a/b/c.txt shows as c.txt" about the
docstring of `format_filename`. The door of `tests.encode` refused s210's
return-value test as "the criterion says it prints". Over nights 100 to
164 the refusal fired on 57 criteria through a piece of an identifier such
as `echo_json` (plans/frame321-provenance.md, section 4). The ten readings
of that section are the shapes here.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.llm import toolproto

NIGHT164 = Path("D:/repos/rota/.rota/clickI_night164.db")
NL = chr(10)

SCRIPT = ("import json" + NL + "def echo_json(obj, indent=None):" + NL
          + "    print(json.dumps(obj, indent=indent))" + NL)
RETURN_TEST = ("from script import echo_json" + NL + "def test_x():" + NL
               + "    result = echo_json({'a': 1})" + NL
               + "    assert result.startswith('{')" + NL)
REFUSAL = ("the test uses what echo_json returns, and the criterion c1 says "
           "it prints: `echo_json` is a plain function in `script.py`")


def _db(tmp_path: Path, item: str, ticket: str, crit: str, refs: str,
        files: dict[str, str]) -> sqlite3.Connection:
    wt = tmp_path / "wt"
    for rel, text in files.items():
        (wt / rel).parent.mkdir(parents=True, exist_ok=True)
        (wt / rel).write_bytes(text.encode())
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1',?,'in_scope','approved',1,1)", (item,))
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1',?)",
                 (ticket,))
    conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                 "VALUES ('c1','tk1',?,?)", (crit, refs))
    conn.execute("INSERT INTO batches (id, item_id, status, worktree) VALUES "
                 "('b1','i1','running',?)", (str(wt),))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('b1','tk1')")
    conn.commit()
    return conn


def _outcome(conn: sqlite3.Connection, path: str, body: str) -> str:
    sb = build("tester", conn, batch_id="b1", mode="tests_missing")
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    try:
        sb.call("tests.encode", id="tst_1", criterion_id="c1", path=path,
                body=body)
    except ValueError as exc:
        return str(exc)
    return "landed"


# The ten readings of the provenance's section 4. Each text is the shape of
# the sampled criterion, and the value is the door's answer after frame 321.
READINGS = {
    "1": ("`echo_json` writes its JSON to the stream with no indent.", REFUSAL),
    "2": ("If `show_python` is not explicitly set, it defaults to false.",
          "landed"),
    "3": ("echo_json must not emit any ANSI codes, so the output is pure JSON.",
          REFUSAL),
    "4": ("When `version_option` is invoked, the output message must include "
          "the Python version.", REFUSAL),
    "5": ("On an object it cannot serialise, echo_json raises a `TypeError` "
          "rather than printing a fallback.", REFUSAL),
    "6": ("echo_json serialises the object, then prints it on a single line.",
          REFUSAL),
    "7": ("echo_json must not print any additional text.", REFUSAL),
    "8": ("echo_json must write a string of compact JSON to the stream.",
          REFUSAL),
    "9": ("`echo_json(obj)` must not introduce any new dependencies.", "landed"),
}


@pytest.mark.parametrize("reading", sorted(READINGS))
def test_the_sampled_readings_meet_the_prose_door(tmp_path, reading):
    """Readings 2 and 9 fired on a piece of an identifier only, and they
    land now. Readings 1 and 3 to 8 say the surface prints, writes or puts
    out, and the refusal keeps its text."""
    text, want = READINGS[reading]
    conn = _db(tmp_path, "a compact mode for the JSON helper",
               "add a compact mode to the JSON helper", text, '["echo_json"]',
               {"script.py": SCRIPT})
    assert _outcome(conn, "tests/test_r.py", RETURN_TEST) == want


def test_a_writes_after_an_identifier_still_counts(tmp_path):
    """Both sides go through `_stem`. "writes" stems to "writ", and the set
    holds "writes", so reading 1 stays refused once "echo" is gone."""
    from rota.roles.api import PRINTS, _family_hits, _plain_words
    words = _plain_words("`echo_json` writes its JSON", frozenset())
    assert "echo" not in words
    assert _family_hits(words, PRINTS) == ["writes"]


def test_a_docstring_sentence_holds_no_prints_word():
    """Candidate D reads the sentence. A sentence that names a docstring,
    documentation or a comment is about text. A help text is what a command
    prints, so it is not on the list (review 1, finding 1)."""
    from rota.roles.api import _about_text
    assert _about_text("The docstring of f includes an example.")
    assert not _about_text("The command prints the help text and exits.")
    assert not _about_text("the output message must include the version")


# Review 1 of frame 321: a help text is printed output, and "e.g." or a
# stop with no space must not cut the sentence.
REVIEW_1 = {
    "help": ("The command prints the help text and exits.", REFUSAL),
    "docstring": ("The docstring of f shows the path as c.txt.", "landed"),
    "eg": ("The docstring of f, e.g. shows the path as c.txt.", "landed"),
    "ie": ("The docstring of f, i.e. shows the path as c.txt.", "landed"),
    "nospace": ("The docstring of f has an example.The helper prints the "
                "value.", REFUSAL),
}


@pytest.mark.parametrize("case", sorted(REVIEW_1))
def test_review_1_shapes(tmp_path, case):
    """Finding 1: "prints the help text" counts. Findings 2 and 5: the door
    splits no sentence at "e.g." or "i.e.", and a stop
    before a capital ends a sentence with or without a space."""
    text, want = REVIEW_1[case]
    conn = _db(tmp_path, "a compact mode for the JSON helper",
               "add a compact mode to the JSON helper", text, '["echo_json"]',
               {"script.py": SCRIPT})
    assert _outcome(conn, "tests/test_r.py", RETURN_TEST) == want


def _night164() -> tuple[tuple[str, str], str] | None:
    if not NIGHT164.is_file():
        return None
    conn = sqlite3.connect(f"file:{NIGHT164.as_posix()}?mode=ro", uri=True)
    try:
        crit = conn.execute("SELECT text, surface_refs FROM criteria WHERE "
                            "id = 'cr_1_format_filename_example'").fetchone()
        completion = conn.execute("SELECT completion FROM turns WHERE "
                                  "session_id = 's210' AND seq = 5").fetchone()[0]
    finally:
        conn.close()
    bodies = [c.args["body"] for c in toolproto.extract(completion)
              if getattr(c, "name", None) == "tests.encode"]
    return crit, bodies[0]


def test_night164_cr_1_admits_s210s_return_value_test(tmp_path):
    """The criterion and the item name the docstring of `format_filename`.
    "shows" there is what the docstring says, not what the function does."""
    got = _night164()
    if got is None:
        pytest.skip("night 164's database is absent")
    (crit, refs), body = got
    assert "== \"c.txt\"" in body
    item = ("With shorten set to True, the path a/b/c.txt shows as c.txt in "
            "the docstring of format_filename")
    utils = ("def format_filename(filename, shorten=False):" + NL
             + "    if shorten:" + NL
             + "        filename = filename.rsplit('/', 1)[-1]" + NL
             + "    return filename" + NL)
    conn = _db(tmp_path, item, item.lower(), crit, refs,
               {"src/click/__init__.py": "", "src/click/utils.py": utils})
    assert _outcome(conn, "tests/test_utils/test_format_filename.py",
                    body) == "landed"
