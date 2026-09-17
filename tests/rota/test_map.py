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

import re

import pytest

from rota.tools import map as map_tool


@pytest.fixture(scope="module")
def index():
    return map_tool.build_index()


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
    # A fixture project's schema is not this system's schema.
    assert "rota/testkit/samplerepo.py" not in index.files
    assert not [f for f in index.files if f.startswith("rota/tools/")]
    assert "rota/roles/api.py" in index.files
    assert "rota/core/db.py" in index.files


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
    assert len(pairs) == 87
    joined = map_tool.ops(index)
    assert set(pairs) == set(joined)
    # The five `cite` ops register in a loop with no decorator.
    assert ("problem", "cite") in joined


def test_mode_lists_its_base_file_and_joins_every_line(index):
    answer = map_tool.query_mode(index, "terminologist/unresolved")
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


def test_mode_keeps_the_one_registered_verb_with_an_underscore(index):
    answer = map_tool.query_mode(index, "architect/touch_strayed")
    found = [x for x in answer.splitlines() if x.startswith("batches.judge_touch")]
    assert len(found) == 1
    assert found[0].startswith("batches.judge_touch -> batches_judge_touch "
                               "rota/roles/api.py:")


def test_mode_lists_a_variant_file_and_does_not_resolve_it(index):
    answer = map_tool.query_mode(index, "terminologist/survey")
    overrides = [x for x in answer.splitlines() if x.startswith("override ")]
    assert ("override rota/roles/prompts/terminologist/account/survey.tools"
            in overrides)
    assert len(overrides) == 4


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


def test_a_shared_name_says_so_and_each_caller_carries_its_chain(index):
    answer = map_tool.query_fn(index, "get", callers=5)
    head = answer.splitlines()[0]
    assert re.fullmatch(r"\d+ definitions share the name", head)
    definitions = [x for x in answer.splitlines() if x.startswith("def get ")]
    assert len(definitions) == int(head.split()[0])

    callers = _lines(answer, "callers")
    assert len(callers) == 5
    assert [x for x in callers if ".get in " in x]


def test_an_unknown_name_exits_one(capsys):
    assert map_tool.main(["fn", "no_such_function"]) == 1
    assert capsys.readouterr().out.strip() == "no fn named no_such_function"


def test_no_argument_prints_the_usage(capsys):
    assert map_tool.main([]) == 2
    assert "usage: python -m rota.tools.map" in capsys.readouterr().out
