"""
The map answers where a thing is. A wrong answer is worse than no answer,
because the reader stops looking.

Every pin here is a fact an agent asked for and paid tool calls to find:
who writes `refs`, who reads `item_provenance`, which function a mode's
tool line reaches. The pins name a function and a file, never a line
number. Every line of the scope report of 2026-09-17 moved within a day,
and a test that pins a line fails on an edit that changes nothing.

The map runs in this process, on the real tree, and opens no database.
"""
from __future__ import annotations

import ast
import re

import pytest

from rota.tools import map as map_tool


@pytest.fixture(scope="module")
def index():
    return map_tool.build_index()


TABLES = {"items": map_tool.Table("x.sql", 1, ("id",), False)}


def _read(source: str) -> map_tool._Reader:
    """One synthetic file, read by the real visitor."""
    reader = map_tool._Reader("x.py", {map_tool.VIEW_DICT})
    reader.visit(ast.parse(source))
    return reader


def _sites(source: str) -> list[map_tool.Site]:
    """The table sites of one synthetic file, by the real resolution."""
    out = []
    for text, line, dynamic, where in _read(source).statements:
        out.extend(map_tool._statement_sites("x.py", text, line, dynamic,
                                             where, TABLES))
    return out


def _lines(answer: str, header: str) -> list[str]:
    """The lines under one header of an answer."""
    out, under = [], False
    for line in answer.splitlines():
        if under:
            if line.startswith(("writers (", "readers (", "callers (", "...")):
                break
            out.append(line)
        elif line.startswith(header + " ("):
            under = True
    return out


def _where(line: str) -> tuple[str, str]:
    """The file and the enclosing definition of a site line."""
    place, definition = line.split()[0], line.split()[1]
    return place.split(":")[0], definition


def test_the_scope_is_the_package_without_the_fixture_project(index):
    # A fixture project's schema is not this system's schema, and the map
    # holds the patterns that name SQL rather than SQL.
    assert "rota/testkit/samplerepo.py" not in index.files
    assert "rota/tools/map.py" not in index.files
    assert "rota/roles/api.py" in index.files
    assert "rota/core/db.py" in index.files


def test_the_other_tools_are_in_scope(index):
    assert "rota/tools/audit.py" in index.files
    readers = [_where(line) for line
               in _lines(map_tool.query_table(index, "refs"), "readers")]
    assert ("rota/tools/audit.py", "audit") in readers


def test_refs_has_two_write_paths(index):
    answer = map_tool.query_table(index, "refs")
    assert answer.startswith("schema rota/core/schema.sql:")
    writers = _lines(answer, "writers")

    pipeline = [line for line in writers if "(pipeline cols" in line]
    assert {_where(line) for line in pipeline} == {
        ("rota/roles/api.py", "stage_ref"), ("rota/roles/api.py", "retire_ref")}

    # The second path: raw SQL at boot, with no receipt and no version bump.
    raw = {_where(line) for line in writers if line.endswith("(raw)")}
    assert ("rota/onboarding/boot.py", "refresh_constraint_zero") in raw

    inside = [line for line in writers if line.startswith("rota/core/db.py:")]
    assert inside
    for line in inside:
        assert line.endswith("(pipeline internal)")
        assert _where(line)[1] == "_apply_ref"


def test_stage_ref_callers_are_one_hop(index):
    answer = map_tool.query_fn(index, "stage_ref")
    assert answer.startswith("def stage_ref rota/roles/api.py:")
    assert "writes refs (pipeline)" in answer

    callers = {line.split(" in ")[-1] for line in _lines(answer, "callers")}
    assert {"glossary_amend", "problem_assert", "model_amend", "frame_assign",
            "_adopt_rows"} <= callers
    # `model_describe` reaches `stage_ref` through `stage_grain_refs`, and
    # the usage says a caller is one hop.
    assert "model_describe" not in callers


def test_a_qualified_name_keeps_its_callers(index):
    answer = map_tool.query_fn(index, "cascade_rows.hop")
    assert answer.startswith("def cascade_rows.hop rota/core/scheduler.py:")
    callers = _lines(answer, "callers")
    assert len(callers) == 2
    assert all(line.startswith("rota/core/scheduler.py:") for line in callers)


def test_item_provenance_readers_include_a_column_fragment(index):
    answer = map_tool.query_table(index, "item_provenance")
    assert answer.startswith("view rota/core/schema.sql:")
    assert "columns id, provenance, basis" in answer
    readers = [_where(line) for line in _lines(answer, "readers")]

    assert ("rota/core/scheduler.py", "tick_slicing") in readers
    # The name sits in a column fragment that starts with `id,`, so a
    # verb-prefix gate misses it.
    assert ("rota/core/runner.py", "_resolve_refs") in readers
    assert ("rota/roles/api.py", "problem_assert") in readers

    indirect = [_where(line) for line in _lines(answer, "readers")
                if "indirect via PROVENANCE_VIEW_OF_TABLE" in line]
    assert ("rota/core/predicates.py", "observed_entries") in indirect


def test_every_op_of_the_graph_joins_a_function(index):
    pairs = map_tool.op_table()
    assert len(pairs) == 88
    joined = map_tool.ops(index)
    assert set(pairs) == set(joined)
    # The five `cite` ops register in a loop with no decorator.
    assert ("problem", "cite") in joined


def test_every_op_joins_a_definition(index):
    joined = map_tool.ops(index)
    assert None not in joined.values()
    # `REGISTRY` names the function `problem_cite`, the source names it
    # `cite`, so the line inside `_cite_op` is what joins the two.
    assert joined[("problem", "cite")].qual == "_cite_op.cite"

    # A join the line made and the name did not says so, so a wrapper
    # whose `__code__` points elsewhere stays visible.
    assert "op problem.cite (by line)" in map_tool.query_fn(index, "cite").splitlines()
    assert ("problem", "cite") in index.ops_by_line
    named = map_tool.query_fn(index, "problem_assert").splitlines()
    assert "op problem.assert" in named
    assert not [x for x in named if x.endswith("(by line)")]


def test_mode_lists_its_base_file_and_joins_every_line():
    answer = map_tool.query_mode("terminologist/unresolved")
    lines = answer.splitlines()
    assert lines[0] == "tools rota/roles/prompts/terminologist/unresolved.tools"

    entries = lines[1:]
    assert len(entries) == 9
    ops_lines = [line for line in entries if not line.startswith("msg.")]
    assert len(ops_lines) == 4
    assert not [line for line in ops_lines if "not in REGISTRY" in line]
    assert [line for line in ops_lines
            if line.startswith("glossary.consult -> glossary_consult "
                               "rota/roles/api.py:")]

    # The 119 `msg.` lines join the messages edges of the graph, never
    # `REGISTRY`.
    messages = [line for line in entries if line.startswith("msg.")]
    assert len(messages) == 5
    assert all(" -> message " in line for line in messages)
    assert "msg.report_liaison -> message report to liaison" in messages


def test_mode_keeps_the_one_registered_verb_with_an_underscore():
    answer = map_tool.query_mode("architect/touch_strayed")
    found = [x for x in answer.splitlines() if x.startswith("batches.judge_touch")]
    assert len(found) == 1
    assert found[0].startswith("batches.judge_touch -> batches_judge_touch "
                               "rota/roles/api.py:")


def test_mode_lists_a_variant_file_and_does_not_resolve_it():
    answer = map_tool.query_mode("terminologist/survey")
    overrides = [x for x in answer.splitlines() if x.startswith("override ")]
    assert ("override rota/roles/prompts/terminologist/account/survey.tools"
            in overrides)
    assert len(overrides) == 4


def test_mode_builds_no_index(monkeypatch, capsys):
    """The mode query reads two files. Parsing the tree for it cost 0.9 s."""
    def refuse(*args, **kwargs):
        raise AssertionError("the mode query must not build the index")

    monkeypatch.setattr(map_tool, "build_index", refuse)
    assert map_tool.main(["mode", "architect/touch_strayed"]) == 0
    assert "batches.judge_touch" in capsys.readouterr().out


def test_the_fixture_project_contributes_no_table(index, capsys):
    assert "accounts" not in index.tables
    assert map_tool.main(["table", "accounts"]) == 1
    assert capsys.readouterr().out.strip() == "no table named accounts"


def test_a_regex_pattern_is_not_a_schema(index):
    assert all(name.isidentifier() for name in index.tables)
    owners = {table.file for table in index.tables.values()}
    assert "rota/design/graph.py" not in owners
    # The files that hold a schema in a string constant.
    assert index.tables["cassettes"].file == "rota/llm/cassettes.py"
    assert index.tables["web_cache"].file == "rota/core/web.py"
    assert index.tables["case_interviews"].file == "rota/testkit/interview.py"
    # `config_history` is declared twice, in the schema and in
    # `rota/core/config.py`. The schema is the owner.
    assert index.tables["config_history"].file == "rota/core/schema.sql"


def test_the_generic_write_is_dynamic(index):
    answer = map_tool.query_file(index, "rota/core/db.py")
    lines = answer.splitlines()
    assert [x for x in lines if x.startswith("def _apply_write ")]
    assert [x for x in lines if x.startswith("writes dynamic INSERT _apply_write:")]
    # The table is named by the pipeline, not by the statement.
    assert [x for x in lines if x.startswith("writes refs (")]


def test_a_bare_file_name_finds_its_path(index):
    # The first agent to use the map gave a bare name in five of its nine
    # `file` calls. One match answers as if the path were given.
    assert map_tool.query_file(index, "paths.py") == (
        map_tool.query_file(index, "rota/paths.py"))
    # `rota/paths.py` holds constants only, and an empty answer reads as a
    # failure.
    assert map_tool.query_file(index, "paths.py") == (
        "rota/paths.py: no definition, no table, no op")
    answer = map_tool.query_file(index, "casestatus.py")
    assert answer == map_tool.query_file(index, "rota/tools/casestatus.py")
    assert [x for x in answer.splitlines() if x.startswith("def status ")]


def test_a_shared_file_name_lists_the_candidates(capsys):
    assert map_tool.main(["file", "__init__.py"]) == 1
    printed = capsys.readouterr().out.splitlines()
    assert re.fullmatch(r"\d+ files named __init__\.py:", printed[0])
    assert len(printed) - 1 == int(printed[0].split()[0])
    assert "rota/core/__init__.py" in printed


def test_a_shared_name_groups_the_facts_under_each_definition(index):
    answer = map_tool.query_fn(index, "get", callers=5)
    lines = answer.splitlines()
    assert re.fullmatch(r"\d+ definitions share the name", lines[0])

    heads = [i for i, x in enumerate(lines) if x.startswith("def get ")]
    assert len(heads) == int(lines[0].split()[0]) == 2
    # The table belongs to the definition that reads it, not to the name.
    assert lines[heads[0]].startswith("def get rota/core/config.py:")
    assert lines[heads[0] + 1] == "reads config (raw)"
    assert not lines[heads[1] + 1].startswith("reads ")

    # One caller list, after the last block. A call is matched by the bare
    # name and never resolved, so the list cannot be split.
    totals = [x for x in lines if x.startswith("callers (")]
    assert len(totals) == 1
    assert re.fullmatch(r"callers \(\d+\) by name, shared by 2 definitions",
                        totals[0])
    callers = [x for x in lines if re.match(r"rota/\S+:\d+ ", x)]
    assert len(callers) == 5
    assert [x for x in callers if ".get in " in x]
    assert lines.index(totals[0]) > max(heads)


def test_prose_is_not_a_reader():
    # Twelve docstrings read as readers of a table they only talk about.
    assert _sites('def f():\n    """Slices tickets from items."""\n') == []
    assert _sites('X = "taken from items"\n') == []

    # A statement is a statement whatever its case.
    lower = _sites('Y = "select id from items"\n')
    assert [(s.table, s.role, s.kind) for s in lower] == [("items", "reads", "raw")]

    # An upper-case slot word is SQL wherever it sits, which is how a
    # column fragment with no leading verb keeps its table.
    fragment = _sites('Z = "id, text, (SELECT 1 FROM items) AS n"\n')
    assert [(s.table, s.role) for s in fragment] == [("items", "reads")]


def test_the_first_dict_holds_the_written_columns():
    reader = _read('def f(ctx):\n'
                   '    ctx.writes.append(("refs", rid, {"a": 1}, {"b": 2}))\n')
    assert reader.pipeline == [("refs", 2, ("a",), "f")]


def test_a_lower_case_statement_with_a_slot_is_dynamic():
    sites = _sites('def f(t, ids):\n'
                   '    q = f"select * from {t} where id in ({ids})"\n')
    assert [(s.kind, s.role, s.table) for s in sites] == [("dynamic", "reads", "")]


def test_a_slot_statement_keeps_a_table_it_also_names():
    sites = _sites('def f(t):\n    q = f"SELECT 1 FROM items JOIN {t} ON 1"\n')
    assert [(s.kind, s.table) for s in sites] == [("dynamic", ""), ("raw", "items")]


def test_an_unknown_name_exits_one(capsys):
    assert map_tool.main(["fn", "no_such_function"]) == 1
    assert capsys.readouterr().out.strip() == "no fn named no_such_function"


def test_no_argument_prints_the_usage(capsys):
    assert map_tool.main([]) == 2
    assert "usage: python -m rota.tools.map" in capsys.readouterr().out
