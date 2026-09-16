"""
Two runs, side by side. The operation the evaluation loop ends in.

`run, look, judge, change something, run again, compare` — and the last step had
no home in any interface. Forking made "again, beside it" cheap; this is what
forking is *for*.

**Not a row diff.** Ids differ by construction, so comparing them reports
everything as changed and nothing as interesting. What is compared is what each
run *found*, matched on content: the term string, the constraint headline, the
area.

**And it reports rather than scores.** "Does the term exist" is a query; "does
it mean the right thing" is either an exact string — brittle enough that the key
gets rewritten to fit each run — or a judgement, which is another model. So the
interesting row, *same term, two senses*, is printed side by side for a person
to read. Scoring that is the answer-key question and deserves its own argument.

The header is what makes any of it mean something. Two runs against different
commits are not evidence about a prompt edit, and until the commit was recorded
they were indistinguishable.
"""
from __future__ import annotations

import pytest

from rota import compare
from rota.core.db import init_db
from rota.testkit.fixtures import seed_provenance


def _run(tmp_path, name, *, terms=(), constraints=(), areas=(), config=None):
    path = tmp_path / f"{name}.db"
    conn = init_db(path)
    for key, value in (config or {}).items():
        conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                     (key, value))
    for i, (term, sense) in enumerate(terms, start=1):
        conn.execute(
            "INSERT INTO glossary_terms (id, term, sense_short) "
            "VALUES (?,?,?)", (f"g{i}", term, sense))
        seed_provenance(conn, "glossary_terms", f"g{i}", "observed")
    for i, head in enumerate(constraints, start=1):
        conn.execute(
            "INSERT INTO constraints (id, headline, text, is_global) "
            "VALUES (?,?,?,0)", (f"c{i}", head, head))
        seed_provenance(conn, "constraints", f"c{i}", "observed")
    for i, (area, outcome) in enumerate(areas, start=1):
        conn.execute(
            "INSERT INTO survey_records (id, area, outcome) VALUES (?,?,?)",
            (f"terminologist:{area}", area, outcome))
    conn.commit()
    conn.close()
    return path


# ---------------------------------------------------------------------------
# What was found
# ---------------------------------------------------------------------------

def test_terms_are_matched_on_the_word_not_the_id(tmp_path):
    """
    Ids differ by construction. `g1` in one run and `g1` in another are not the
    same term and often are not even the same word, so an id diff reports
    everything as changed — which is the same as reporting nothing.
    """
    a = _run(tmp_path, "a", terms=[("intent", "a stated goal"), ("folder", "a dir")])
    b = _run(tmp_path, "b", terms=[("intent", "a stated goal"), ("template", "a form")])

    got = compare.runs(a, b)

    assert got["terms"]["only_a"] == ["folder"]
    assert got["terms"]["only_b"] == ["template"]
    assert [d["term"] for d in got["terms"]["agree"]] == ["intent"]


def test_the_same_term_with_two_senses_is_the_interesting_row(tmp_path):
    """
    The failure this whole loop exists to catch, and the one an existence check
    cannot see.

    `intent` came back from a real run as *"a specific action or task"* — the
    dictionary sense. Present, fluent, wrong, and invisible to anything asking
    only whether the term is there. It is reported first and it is reported as
    two strings, because deciding which is right is a judgement.
    """
    a = _run(tmp_path, "a", terms=[("intent", "what the user asked to happen")])
    b = _run(tmp_path, "b", terms=[("intent", "a specific action or task")])

    got = compare.runs(a, b)

    assert got["terms"]["only_a"] == [] and got["terms"]["only_b"] == []
    differ = got["terms"]["differ"]
    assert [d["term"] for d in differ] == ["intent"]
    assert differ[0]["a"] == "what the user asked to happen"
    assert differ[0]["b"] == "a specific action or task"
    assert "verdict" not in differ[0], "it scored something it cannot score"


def test_constraints_match_on_headline_and_areas_on_outcome(tmp_path):
    a = _run(tmp_path, "a", constraints=["Commitment to esbuild"],
             areas=[("src", "found"), ("tests", "found")])
    b = _run(tmp_path, "b", constraints=["Commitment to esbuild", "Bundling"],
             areas=[("src", "found"), ("tests", "none_found")])

    got = compare.runs(a, b)

    assert got["constraints"]["only_b"] == ["Bundling"]
    assert [d["area"] for d in got["areas"]["differ"]] == ["tests"]
    assert got["areas"]["differ"][0]["a"] == "found"


# ---------------------------------------------------------------------------
# The header, which is what makes the rest mean anything
# ---------------------------------------------------------------------------

def test_two_runs_on_one_commit_are_comparable_and_say_so(tmp_path):
    a = _run(tmp_path, "a", config={"project_root": "/src/x",
                                    "project_branch": "main",
                                    "project_commit": "abc123"})
    b = _run(tmp_path, "b", config={"project_root": "/src/x",
                                    "project_branch": "main",
                                    "project_commit": "abc123"})

    got = compare.runs(a, b)

    assert got["same_source"] is True
    assert "same source" in got["header"].lower()


def test_two_runs_on_different_commits_say_so_loudly(tmp_path):
    """
    A difference between runs on different trees is not evidence about anything
    you changed. Until the commit was recorded these two were indistinguishable,
    which is how a branch comparison got made from memory.
    """
    a = _run(tmp_path, "a", config={"project_commit": "aaa", "project_branch": "main"})
    b = _run(tmp_path, "b", config={"project_commit": "bbb", "project_branch": "v3"})

    got = compare.runs(a, b)

    assert got["same_source"] is False
    assert "different" in got["header"].lower()
    assert "main" in got["header"] and "v3" in got["header"]


def test_an_unrecorded_commit_is_unknown_and_not_assumed_equal(tmp_path):
    """
    Runs onboarded before the commit was recorded answer nothing, and two
    silences are not agreement.
    """
    a = _run(tmp_path, "a")
    b = _run(tmp_path, "b")

    got = compare.runs(a, b)

    assert got["same_source"] is None
    assert "not recorded" in got["header"].lower()


def test_the_prompts_a_run_used_are_reported_when_recorded(tmp_path):
    """
    The other half of the header, and the half that answers *did that edit
    help*. A session records `briefs_hash` — what the composed briefs said when
    it ran — so two runs on one commit can be told apart by the only other
    thing that shapes an artefact.
    """
    a = _run(tmp_path, "a", config={"project_commit": "abc"})
    b = _run(tmp_path, "b", config={"project_commit": "abc"})
    for path, digest in ((a, "brief-v1"), (b, "brief-v2")):
        conn = init_db(path)
        conn.execute(
            "INSERT INTO sessions (id, role, mode, committed, seq, briefs_hash) "
            "VALUES ('s1','terminologist','normal',1,1,?)", (digest,))
        conn.commit()
        conn.close()

    got = compare.runs(a, b)

    assert got["same_prompts"] is False
    assert "prompts" in got["header"].lower()


# ---------------------------------------------------------------------------
# Cost, and refusing what cannot be read
# ---------------------------------------------------------------------------

def test_cost_counts_the_sessions_that_wrote_nothing(tmp_path):
    """
    Sessions alone say how long it took. Barren sessions say whether it was
    getting anywhere, which is the number that made the livelock visible.
    """
    a = _run(tmp_path, "a")
    conn = init_db(a)
    for i in range(3):
        conn.execute(
            "INSERT INTO sessions (id, role, mode, committed, seq) "
            "VALUES (?,'terminologist','normal',1,?)", (f"s{i}", i))
    conn.execute("INSERT INTO receipts (session_id, table_name, row_id, "
                 "new_version) VALUES ('s0','glossary_terms','g1',1)")
    conn.commit()
    conn.close()

    got = compare.runs(a, _run(tmp_path, "b"))

    assert got["cost"]["a"]["sessions"] == 3
    assert got["cost"]["a"]["barren"] == 2


def test_a_run_it_cannot_read_is_refused_rather_than_half_compared(tmp_path):
    """
    Seven of eight runs in `.rota/` are behind the schema. Half a comparison
    reads as a difference, which is the one thing a diff must never invent.
    """
    a = _run(tmp_path, "a")
    b = _run(tmp_path, "b")
    conn = init_db(b)
    conn.execute("DROP TABLE glossary_terms")
    conn.commit()
    conn.close()

    with pytest.raises(SystemExit) as exc:
        compare.runs(a, b)
    assert "b" in str(exc.value)
