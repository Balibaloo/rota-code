"""
Detector one: invented literals are assumptions wearing numbers.

The principal's skepticism set the design: "the assumptions thing always
seemed strange to me because it's hard to enumerate assumptions." Right --
so nothing enumerates. Mechanics locate the divergence (a literal the
material never fixed) and the sentence is written mechanically, one row per
test. The measurement this answers: one ledger row in 134 production-model
sessions, because a model never volunteers what it cannot see itself doing.
"""
from __future__ import annotations

from rota.core.divergence import invented_literals, literals_in, sentence_for

CRIT = "register(u) stores the email lowercased"
BODY = (
    "from app import register, lookup\n"
    "def test_lowercase():\n"
    "    register('u1', 'A@B.co', 72)\n"
    "    assert lookup('u1').email == 'a@b.co'\n"
)


def test_the_invented_values_are_found_and_the_given_ones_are_not():
    """'u1', 'A@B.co' and 72 appear nowhere in the criterion: three choices.
    'a@b.co' IS 'A@B.co' case-folded -- one choice, counted once."""
    out = invented_literals(BODY, CRIT)
    assert "u1" in out and "A@B.co" in out and "72" in out
    assert "a@b.co" not in out, "case-folded duplicates are one choice"


def test_a_literal_the_criterion_fixes_is_not_invented():
    crit = "register('u1', 'A@B.co', 72) stores email 'a@b.co'"
    assert invented_literals(BODY, crit) == [], \
        "the criterion made every choice; the test invented nothing"


def test_trivial_values_carry_no_information():
    body = "def t():\n    assert f(0, 1, True, None, '') == []\n"
    assert invented_literals(body, "anything") == []


def test_a_body_that_is_not_python_still_yields_its_literals():
    body = "expect(register('u9', \"X@Y.io\")).toBe(200)"
    lits = literals_in(body)
    assert "u9" in lits and "X@Y.io" in lits and "200" in lits


def test_the_sentence_is_one_row_and_names_the_values():
    s = sentence_for("ts1", ["u1", "A@B.co", "72"])
    assert "ts1" in s and "'A@B.co'" in s
    assert "choice" in s
    long = sentence_for("ts1", [str(i) * 2 for i in range(10)])
    assert "and 4 more" in long, "one row per test, capped, never ten rows"
