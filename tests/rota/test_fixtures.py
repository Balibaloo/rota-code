"""
The case machinery itself.

Everything else asserts what a role did. These assert that the thing asking the
question asked it fairly — the failure a passing suite cannot show you, because
a case that can pass for the wrong reason passes silently.
"""
from __future__ import annotations

import pathlib
import re
import tempfile

import yaml

from rota.core.db import init_db
from rota.testkit import fixtures

CASES = pathlib.Path(__file__).parent / "cases"


def _files():
    return sorted(CASES.glob("l*.yaml"))


def _case(case_id: str) -> dict:
    for path in _files():
        for case in fixtures.load_case(path) or []:
            if case["id"] == case_id:
                return case
    raise AssertionError(f"no case {case_id}")


def test_a_case_file_is_valid_yaml_before_anything_fills_it():
    """
    The reason the holes are `<name>` and not `{{name}}`.

    Fixture rows are YAML *flow* mappings — `- {id: X, text: "..."}` — and in
    flow context `{ } [ ] ,` are indicators, so a plain scalar cannot contain
    them. `{{i1}}` produced a file that was invalid YAML and happened to parse
    once the holes were filled, which costs editor validation, `--raw` loading,
    and every tool that reads a case without going through the loader.
    """
    for path in _files():
        yaml.safe_load(path.read_text(encoding="utf-8"))


def test_no_case_leaves_a_reference_unwrapped():
    """
    A bare `tk1` beside a filled `<tk1>` is a foreign key pointing at a row that
    no longer exists under that name — a fixture that seeds broken, and a role
    blamed for a situation that never existed. Twenty-two cases were in exactly
    that state after the first migration, because the regex doing it refused to
    match an id immediately before a `}`.
    """
    bare = []
    for path in _files():
        text = path.read_text(encoding="utf-8")
        for name in set(re.findall(r"<([A-Za-z0-9_]+)>", text)):
            for n, line in enumerate(text.splitlines(), 1):
                if re.search(rf"(?<![\w<]){re.escape(name)}(?![\w>])", line):
                    bare.append(f"{path.name}:{n} {name}")
    assert not bare, bare


def test_ids_the_model_could_have_guessed_are_gone():
    """
    Cases are written readable. The cost is that they are predictable: in a
    fixture with one item, `problem.set_approval(id='i1')` is right every time
    without reading anything, so a case that ought to fail can pass and running
    it more times will never say which happened.
    """
    ids = {r["id"] for r in _case("L1-CR-fail-names-its-criterion")["fixture"]["items"]}
    assert ids and all(re.fullmatch(r"[a-z]+_[0-9a-f]{6}", i) for i in ids), ids


def test_filling_is_the_same_every_time():
    """Deterministic, or every cassette becomes single-use — the bug that left
    1140 of 1419 recordings never replayed once."""
    assert fixtures.fill("<i1>", "L1-X") == fixtures.fill("<i1>", "L1-X")


def test_two_cases_do_not_share_a_filling():
    """Keyed by case as well as by name, so a model cannot learn one mapping and
    apply it to the next case."""
    assert fixtures.fill("<i1>", "L1-X") != fixtures.fill("<i1>", "L1-Y")


def test_a_derived_id_follows_the_id_it_derives_from():
    """
    The case that broke the inference-based version, and the argument for
    declaring holes instead.

    `e_m_in` is an entry id that *encodes* a message id, because the runtime
    looks up `f"e_{message_id}"`. Inference renamed the entry and left the
    message alone, `ctx.entry_id` came back None, and Liaison — which had passed
    for weeks — silently stopped being able to segment anything. Written as
    `e_<m_in>` the two move together, because the author said they were the same
    thing and nothing had to guess.
    """
    case = _case("L1-LI-segment")
    assert case["fixture"]["entries"][0]["id"] == f"e_{case['inbound']['id']}"


def test_every_case_seeds():
    """Applied to all of them: a case that will not seed is a case that never
    ran, however green the file looks."""
    seen = 0
    for path in _files():
        for case in fixtures.load_case(path) or []:
            conn = init_db(pathlib.Path(tempfile.mkdtemp()) / "rota.db")
            fixtures.seed(conn, case.get("fixture") or {})
            seen += 1
    assert seen > 50


def test_a_forbidden_row_fails_the_touch_and_only_the_touch():
    """
    The harness extension Track B's intake segments waited on. `forbidden:
    writes: [items]` cannot serve the wrong-answer-from-the-seat cases,
    because there the right action and the wrong action write to the same
    table -- what separates them is *which row*. The assertion must be able
    to fail (the seeded row was amended) and to pass (only new rows appeared),
    the same both-ways rule the bench applies to its graders.
    """
    delta = fixtures.Delta(session_id="s", committed=True,
                           writes={"items": ["i_seeded", "i_new"]})
    hit = fixtures.check(
        {"expect": {}, "forbidden": {"rows": ["items:i_seeded"]}}, delta)
    assert hit == ["forbidden change to items:i_seeded"]
    clean = fixtures.check(
        {"expect": {}, "forbidden": {"rows": ["items:i_other",
                                              "tickets:i_seeded"]}}, delta)
    assert clean == []
