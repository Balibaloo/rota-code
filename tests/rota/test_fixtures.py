"""
The case machinery itself.

Everything else asserts what a role did. These assert that the thing asking the
question asked it fairly — which is the failure mode a passing suite cannot show
you, because a case that can pass for the wrong reason passes silently.
"""
from __future__ import annotations

import json

from rota.testkit import fixtures

CASES = fixtures.CASES if hasattr(fixtures, "CASES") else None


def _case(case_id: str) -> dict:
    import pathlib

    root = pathlib.Path(__file__).parent / "cases"
    for path in sorted(root.glob("l*.yaml")):
        for case in fixtures.load_case(path) or []:
            if case["id"] == case_id:
                return case
    raise AssertionError(f"no case {case_id}")


def test_ids_the_model_could_have_guessed_are_rewritten():
    """
    Cases are written with `i1`, `tk1`, `b1` because they have to be readable.
    The cost is that they are predictable: in a fixture with one item,
    `problem.set_approval(id='i1')` is right every time without reading
    anything — so a case that ought to fail can pass, and running it more times
    will never say which happened.
    """
    out = fixtures.obfuscate(_case("L1-CR-fail-names-its-criterion"))

    ids = {r["id"] for r in out["fixture"]["items"]}
    assert ids and not any(i in ("i1", "i2") for i in ids)
    assert all("_" in i and len(i) > 4 for i in ids), ids


def test_the_rewrite_is_the_same_every_time():
    """
    Deterministic, or every cassette becomes single-use — which is the bug that
    left 1140 of 1419 recordings never replayed once.
    """
    case = _case("L1-CR-fail-names-its-criterion")
    assert fixtures.obfuscate(case)["_ids"] == fixtures.obfuscate(case)["_ids"]


def test_two_cases_do_not_share_a_rewrite():
    """Keyed by case as well as by id, so a model cannot learn one mapping and
    apply it to the next case."""
    a = fixtures.obfuscate(_case("L1-CR-fail-names-its-criterion"))["_ids"]
    b = fixtures.obfuscate(_case("L1-CR-pass-a-conforming-diff"))["_ids"]
    shared = {k for k in a if k in b and a[k] == b[k]}
    assert not shared, shared


def test_every_reference_follows_the_row_it_points_at():
    """A rewrite that missed a foreign key would seed a broken fixture, and the
    role would be blamed for a situation that never existed."""
    out = fixtures.obfuscate(_case("L1-CR-fail-names-its-criterion"))
    fx = out["fixture"]

    item = fx["items"][0]["id"]
    ticket = fx["tickets"][0]["id"]
    batch = fx["batches"][0]["id"]

    assert fx["tickets"][0]["item_id"] == item
    assert fx["criteria"][0]["ticket_id"] == ticket
    assert fx["batches"][0]["item_id"] == item
    assert fx["batch_tickets"][0]["batch_id"] == batch
    assert fx["tests"][0]["criterion_id"] == fx["criteria"][0]["id"]
    assert out["refs"] == [batch] and out["repo"]["batch"] == batch


def test_assertions_are_rewritten_with_the_fixture():
    """Otherwise every case with `refs_include` would fail against ids it asked
    for and then renamed."""
    out = fixtures.obfuscate(_case("L1-LI-relay-a-ruling-without-interpreting-it"))
    want = out["expect"]["messages"][0]["refs_include"]
    seeded = {r["id"] for r in out["fixture"]["items"]}
    assert set(want) == seeded

    # And the principal's ruling, which carries ids in a config key *and* inside
    # a JSON value — the two places a structural rewrite is easiest to miss.
    cfg = out["fixture"]["config"][0]
    assert cfg["key"].split(":", 1)[1] == out["inbound"]["id"]
    assert set(json.loads(cfg["value"])) == seeded


def test_every_case_survives_the_rewrite():
    """Applied to all of them, since a case that breaks under it is a case that
    was relying on an id being literally `b1` somewhere the rewrite cannot see."""
    import pathlib
    import tempfile

    from rota.core.db import init_db

    root = pathlib.Path(__file__).parent / "cases"
    seen = 0
    for path in sorted(root.glob("l*.yaml")):
        for case in fixtures.load_case(path) or []:
            out = fixtures.obfuscate(case)
            conn = init_db(pathlib.Path(tempfile.mkdtemp()) / "rota.db")
            fixtures.seed(conn, out.get("fixture") or {})
            seen += 1
    assert seen > 50
