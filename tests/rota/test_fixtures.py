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

    A comment line and a `- id:` line hold no foreign key. The YAML parse
    drops a comment, and the case id is a name, so `m53` in
    `L3R-n174-m53-m55` is no reference (frame 353, wall 2).
    """
    bare = []
    for path in _files():
        lines = [(n, line) for n, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), 1)
            if not line.lstrip().startswith("#")
            and not line.startswith("- id:")]
        names = fixtures.holes(chr(10).join(line for _, line in lines))
        for name in names:
            for n, line in lines:
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
    1140 of 1419 recordings never replayed once. Run 1, which is the run every
    recording in the register was made under."""
    assert fixtures.fill("<i1>", "L1-X") == fixtures.fill("<i1>", "L1-X")


def test_run_one_keeps_the_ids_every_recording_was_made_under():
    """
    The salt starts at run 2 (frame 66, 2026-09-23).

    Run 1's digest is the unsalted one, byte for byte, so every cassette and
    every register row recorded before the salt stays evidence about run 1.
    The report replays a chain on run 1's keys for the same reason.
    """
    import hashlib

    plain = hashlib.sha1(b"L1-X:i1").hexdigest()[:6]
    assert fixtures.fill("<i1>", "L1-X") == f"i_{plain}"
    assert fixtures.fill("<i1>", "L1-X", 1) == f"i_{plain}"
    assert fixtures.fill("<i1>", "L1-X", 2) == (
        "i_" + hashlib.sha1(b"L1-X:i1:2").hexdigest()[:6])


def test_two_runs_of_one_case_are_two_problems():
    """
    Five runs were five copies of one reply, and now they are five problems.

    Every tier pins `temperature=0.0` and the ids were the same every run, so
    run 1 recorded and runs 2 to 5 replayed it inside one process. No
    invocation of five runs ever split (observed: the register, 2026-09-23).

    The system text does not move, because no fixture id reaches it: 0 of 121
    single-session cases compose one that holds a filled id. So the salt moves
    the user half of the cassette key alone, and the report keeps matching a
    case on its system digest.
    """
    from rota.llm.llm import ScriptedBackend

    case = _case("L1-LI-segment")
    seen = []
    for run_no in (1, 2):
        backend = ScriptedBackend([""])
        work = pathlib.Path(tempfile.mkdtemp())
        fixtures.run_case(fixtures.for_run(case, run_no), work / "rota.db",
                          backend, instructions=fixtures.instructions_for(case),
                          run_no=run_no)
        assert backend.calls, f"run {run_no} reached no prompt"
        seen.append(backend.calls[0])
    assert seen[0][1] != seen[1][1], "the user half carries the filled ids"
    assert seen[0][0] == seen[1][0], "and the system half carries none"


def test_a_case_nobody_loaded_runs_as_it_is():
    """
    `for_run` fills a registered block and returns anything else unchanged.

    A test that builds a case by hand never went through `load_case`, so no
    block is kept for it. Returning it as it is keeps every such test running
    exactly as it ran before the salt.
    """
    built = {"id": "not-a-loaded-case", "role": "liaison"}
    assert fixtures.for_run(built, 3) is built
    loaded = _case("L1-LI-segment")
    assert fixtures.for_run(loaded, 1) == loaded, "run 1 is today's case"


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


def test_a_junction_table_loads_the_rows_its_receipt_labels_name():
    """
    A junction table has no `id`, so `SELECT ... WHERE id IN` raised and the
    rows came back empty. A `text_excludes` on `batch_touch` then passed on no
    rows, and the re-annotate case scored a path written back as green
    (frame 190, pass 3c).
    """
    conn = init_db(pathlib.Path(tempfile.mkdtemp()) / "rota.db")
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("INSERT INTO sessions (id, role, seq) VALUES ('s1', 'architect', 1)")
    for grain in ("src/click/termui.py", "tests/test_defaults.py",
                  "tests/test_other.py"):
        conn.execute(
            "INSERT INTO batch_touch (batch_id, grain, grain_kind, confidence) "
            "VALUES ('b1', ?, 'path', 'expected')", (grain,))
    conn.execute(
        "INSERT INTO touch_strays (batch_id, commit_sha, path, status) "
        "VALUES ('b1', 'abc', 'src/x.py', 'open')")
    # "b1:tests/gone.py" names no row: it loads nothing, not the rows of b1.
    for label in ("b1:*", "b1:src/click/termui.py", "b1:tests/test_defaults.py",
                  "b1:tests/gone.py"):
        conn.execute(
            "INSERT INTO receipts (session_id, table_name, row_id, new_version) "
            "VALUES ('s1', 'batch_touch', ?, 1)", (label,))
    conn.execute(
        "INSERT INTO receipts (session_id, table_name, row_id, new_version) "
        "VALUES ('s1', 'touch_strays', 'b1:abc:src/x.py', 1)")
    delta = fixtures.capture(conn, "s1", {})
    assert sorted(r["grain"] for r in delta.rows["batch_touch"]) == [
        "src/click/termui.py", "tests/test_defaults.py"]
    assert [r["path"] for r in delta.rows["touch_strays"]] == ["src/x.py"]
    hit = fixtures.check({"expect": {"writes": {"batch_touch": {
        "text_excludes": ["tests/test_defaults.py"]}}}}, delta)
    assert hit and "tests/test_defaults.py" in hit[0]


def test_each_text_includes_any_reads_every_row_and_not_the_ids():
    """
    Frame 322, review 2, finding 2. Night 166's s185 wrote two behaviour
    criteria and one docstring criterion on the docstring ticket. The blob
    of `text_includes_any` passes that turn, because one row and every id
    hold "docstring". The per-row field refuses it.
    """
    s185 = [
        {"id": "c_1_docstring", "text": "When shorten=True, format_filename "
         "strips the directory prefix from the path."},
        {"id": "c_2_docstring", "text": "When shorten=True, format_filename "
         "returns only the basename of the provided path."},
        {"id": "c_3_docstring", "text": "The docstring of format_filename must "
         "include an example demonstrating that with shorten=True, a/b/c.txt "
         "is displayed as c.txt."},
    ]
    delta = fixtures.Delta(session_id="s", committed=True,
                           writes={"criteria": [r["id"] for r in s185]},
                           rows={"criteria": s185})
    words = ["docstring", "documentation"]
    assert fixtures.check({"expect": {"writes": {"criteria": {
        "text_includes_any": words}}}, "forbidden": {}}, delta) == []
    hit = fixtures.check({"expect": {"writes": {"criteria": {
        "each_text_includes_any": words}}}, "forbidden": {}}, delta)
    assert [h.split(" names")[0] for h in hit] == [
        "a criteria row c_1_docstring", "a criteria row c_2_docstring"]
    delta.rows["criteria"] = s185[2:]
    delta.writes["criteria"] = ["c_3_docstring"]
    assert fixtures.check({"expect": {"writes": {"criteria": {
        "each_text_includes_any": ["DocString"]}}}, "forbidden": {}}, delta) == []
