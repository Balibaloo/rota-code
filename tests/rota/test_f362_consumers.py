"""
Frame 362, slice pass 3: the consumers of a stated commitment.

Pass 2 lets the Architect state a harvested commitment as a `constraints`
row with `party`, `behaviour` and `witness`. This pass pushes the stated
commitments to the Developer, the Tester and the Critic, and lets the
Critic fail a diff that breaks one. The design is
`plans/design-onboarding-2026-11-03.md`, section 4.2, steps 3 and 4.
Ruling 3 of 2026-11-03 makes a broken promise to outside programs a fail,
and it amends 13d138b2.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from rota.core.db import init_db
from rota.core.runner import BOUND_KEY, TESTER_BOUND_KEY, bound_key, build_prompt, push_working_set, session_sandbox
from rota.core.scheduler import Wake
from rota.onboarding import harvest
from rota.onboarding.boot import ZERO, refresh_constraint_zero
from rota.roles import api

FOLD = '''"""Lines as RFC 5545 folds them."""


def fold(line, limit=75):
    """Fold the line.

    A line holds at most 75 octets.
    """
    return line
'''
# A second witness of the same limit in another unit, so the harvest keeps
# the two lines side by side.
DOC = ("Folding\n=======\n\n"
       "A content line holds at most 75 characters, as RFC 5545 says.\n")
THING = "def keep(x):\n    return x\n"
SEATS = (("developer", "tick:batch_start"), ("tester", "tick:tests_missing"),
         ("critic", "tick:review"))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


@pytest.fixture
def proj(tmp_path):
    """Two areas. Batch `b1` touches `src/pkg/fold.py`, and the harvest runs
    at commit `c1`."""
    root = tmp_path / "proj"
    _write(root / "src/pkg/fold.py", FOLD)
    _write(root / "src/other/thing.py", THING)
    _write(root / "docs/fold.rst", DOC)
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)",
               (str(root),))
    for grain, kind, area in (("src/pkg/fold.py", "path", "src/pkg"),
                              ("src/pkg/fold.py::fold", "symbol", "src/pkg"),
                              ("src/other/thing.py", "path", "src/other")):
        db.execute("INSERT INTO code_index (grain, grain_kind, area) "
                   "VALUES (?, ?, ?)", (grain, kind, area))
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES ('it', 'fold at a space', 'in_scope', 'approved', 1, 1)")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1', 'it', 'running')")
    db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind) "
               "VALUES ('b1', 'src/pkg/fold.py', 'path')")
    harvest.record(db, root, "c1")
    for area in ("src/pkg", "src/other"):
        db.execute("INSERT INTO survey_records (id, area, outcome) "
                   "VALUES (?, ?, 'none_found')", (f"sv_{area}", area))
    refresh_constraint_zero(db)
    db.commit()
    yield root, db
    db.close()


def _candidate(db, kind, path):
    return dict(db.execute(
        "SELECT * FROM commitment_candidates WHERE kind = ? AND path = ?",
        (kind, path)).fetchone())


def _state(db, cid="fold_octets", grain="src/pkg/fold.py", kind="numeric_default",
           path="src/pkg/fold.py"):
    """A stated commitment, as `model.amend` lands one, bound to `grain`."""
    c = _candidate(db, kind, path)
    db.execute(
        "INSERT INTO constraints (id, headline, text, is_global, party, behaviour, "
        "witness) VALUES (?, ?, ?, 0, ?, ?, ?)",
        (cid, f"{path}: lines fold at 75 octets",
         "Other calendar programs read the folded lines.",
         "other calendar programs", "a folded line holds at most 75 octets",
         harvest.witness_key(c["kind"], c["path"], c["text"])))
    db.execute("INSERT INTO constraint_bindings (constraint_id, grain, grain_kind, "
               "resolves) VALUES (?, ?, 'path', 1)", (cid, grain))
    db.commit()
    return c


def _push(db, role, kind):
    wake = Wake(role, kind, refs=("b1",))
    sb = session_sandbox(db, wake, batch_id="b1")
    pushed = push_working_set(role, sb, wake)
    return sb, pushed


def _falsify(db, cid="fold_octets"):
    db.execute("INSERT INTO challenges (id, verdict, citation, quote) VALUES "
               "(?, 'falsified', 'src/pkg/fold.py', 'return line')",
               (f"constraints:{cid}",))
    db.commit()


# ---------------------------------------------------------------------------
# The shared rule
# ---------------------------------------------------------------------------

def test_the_rule_reaches_a_bound_stated_commitment_with_its_line(proj):
    _, db = proj
    c = _state(db)
    rows, falsified = api.stated_commitments(db, ["src/pkg/fold.py"])
    assert [r["id"] for r in rows] == ["fold_octets"]
    assert rows[0]["line"]["id"] == c["id"]
    assert falsified == {}


def test_a_falsified_commitment_reaches_no_seat(proj):
    """The review of pass 2, medium 3: the exclusion lived in the survey
    push only, so `bound_constraints` still pushed the row."""
    _, db = proj
    c = _state(db)
    _falsify(db)
    rows, falsified = api.stated_commitments(db, ["src/pkg/fold.py"])
    assert rows == []
    assert falsified == {"fold_octets": harvest.witness_key(c["kind"], c["path"],
                                                            c["text"])}
    for role, kind in SEATS:
        sb, pushed = _push(db, role, kind)
        assert "fold_octets" not in json.dumps(pushed.get(BOUND_KEY)), role
    assert c["id"] not in [w["id"] for w in api.witness_push(db, "src/pkg")[0]]
    sb, _ = _push(db, "critic", "tick:review")
    with pytest.raises(ValueError, match="not a commitment that the push showed"):
        sb.call("verdicts.emit", batch_id="b1", result="fail",
                failed_criterion="fold_octets", reason="it counts characters")


def test_a_commitment_with_no_binding_to_the_touch_is_not_pushed(proj):
    _, db = proj
    _state(db, cid="keep_whole", grain="src/other/thing.py")
    assert api.stated_commitments(db, ["src/pkg/fold.py"])[0] == []
    for role, kind in SEATS:
        _, pushed = _push(db, role, kind)
        assert "keep_whole" not in json.dumps(pushed.get(BOUND_KEY)), role


def test_a_lost_witness_is_marked_and_cannot_carry_a_fail(proj):
    root, db = proj
    _state(db)
    _write(root / "src/pkg/fold.py", FOLD.replace("limit=75", "limit=76"))
    harvest.record(db, root, "c2")
    db.commit()
    sb, pushed = _push(db, "critic", "tick:review")
    row = next(r for r in pushed[BOUND_KEY] if r["id"] == "fold_octets")
    assert row["witness"] == api.LOST_WITNESS
    with pytest.raises(ValueError, match="is lost"):
        sb.call("verdicts.emit", batch_id="b1", result="fail",
                failed_criterion="fold_octets", reason="it counts characters")


# ---------------------------------------------------------------------------
# The push
# ---------------------------------------------------------------------------

def test_the_three_pushes_carry_the_same_commitments(proj):
    _, db = proj
    c = _state(db)
    seen = []
    for role, kind in SEATS:
        sb, pushed = _push(db, role, kind)
        # The key reads the pushed rows, which carry the witness and the
        # party (pass 4f, high B).
        key = next(k for k in pushed if k.startswith(BOUND_KEY))
        bound = pushed[key]
        assert key == bound_key(role, bound)
        assert ZERO not in [r["id"] for r in bound], role
        _, user = build_prompt(role, sb, Wake(role, kind, refs=("b1",)), pushed,
                               instructions="")
        assert f"[{key}]" in user
        seen.append(bound)
    assert seen[0] == seen[1] == seen[2]
    row = seen[0][0]
    assert row["party"] == "other calendar programs"
    assert row["behaviour"] == "a folded line holds at most 75 octets"
    assert row["witness"] == f'src/pkg/fold.py line {c["line"]}: "{c["text"].strip()}"'


def test_two_contradicting_witnesses_both_show(proj):
    _, db = proj
    c = _state(db)
    other = json.loads(c["contradicts"])
    assert other, "the fixture needs a contradiction"
    _, pushed = _push(db, "tester", "tick:tests_missing")
    row = pushed[TESTER_BOUND_KEY][0]
    assert row["witness"].startswith("src/pkg/fold.py line ")
    assert len(row["contradicts"]) == 1
    assert row["contradicts"][0].startswith("docs/fold.rst line 4: ")
    assert "75 characters" in row["contradicts"][0]


def test_an_ordinary_constraint_keeps_its_three_fields(proj):
    _, db = proj
    _state(db)
    db.execute("INSERT INTO constraints (id, headline, text, is_global) VALUES "
               "('plain', 'a plain row', 'Programs read it.', 0)")
    db.execute("INSERT INTO constraint_bindings (constraint_id, grain, grain_kind, "
               "resolves) VALUES ('plain', 'src/pkg/fold.py', 'path', 1)")
    db.commit()
    _, pushed = _push(db, "developer", "tick:batch_start")
    plain = next(r for r in pushed[BOUND_KEY] if r["id"] == "plain")
    assert plain == {"id": "plain", "headline": "a plain row",
                     "text": "Programs read it."}


# ---------------------------------------------------------------------------
# The Critic's fail
# ---------------------------------------------------------------------------

def test_a_fail_on_a_pushed_commitment_names_it_and_quotes_the_witness(proj):
    _, db = proj
    c = _state(db)
    sb, _ = _push(db, "critic", "tick:review")
    out = sb.call("verdicts.emit", batch_id="b1", result="fail",
                  failed_criterion="fold_octets",
                  reason="The fold counts characters, not octets.")
    assert out["result"] == "fail"
    row = [v for t, _, v in sb.ctx.writes if t == "verdicts"][0]
    assert row["failed_criterion"] is None
    assert row["failed_commitment"] == "fold_octets"
    assert row["reason"].startswith("The fold counts characters, not octets.")
    assert "fold_octets" in row["reason"]
    assert c["text"].strip() in row["reason"]
    assert f'src/pkg/fold.py line {c["line"]}' in row["reason"]


def test_a_reason_that_quotes_the_witness_is_kept_as_it_is(proj):
    _, db = proj
    c = _state(db)
    sb, _ = _push(db, "critic", "tick:review")
    said = f'fold_octets breaks: "{c["text"].strip()}" and the diff counts characters.'
    sb.call("verdicts.emit", batch_id="b1", result="fail",
            failed_criterion="fold_octets", reason=said)
    row = [v for t, _, v in sb.ctx.writes if t == "verdicts"][0]
    assert row["reason"] == said


def test_the_critic_brief_carries_the_two_exceptions():
    from rota import paths

    base = (paths.PROMPTS / "critic" / "base.md").read_text(encoding="utf-8")
    flat = " ".join(base.split())
    assert ("Do not fail a diff for a purpose you read in a docstring or a "
            "comment, except a pushed commitment, whose witness the push "
            "quotes.") in flat
    assert ("Anything the diff does outside the criteria is a remark in the "
            "verdict's reason, never a fail, except a broken pushed "
            "commitment, which is a fail.") in flat
    # The Tester's ask is in the header of its bound block, and its brief
    # is the one from before the slice (frame 362, pass 4c).
    tester = (paths.PROMPTS / "tester" / "tests_missing.md").read_text(
        encoding="utf-8")
    ask = ("Write a test that guards each pushed commitment whose behaviour "
           "the change can reach, from its witness's input and output.")
    assert ask not in tester
    assert ask in TESTER_BOUND_KEY
    assert bound_key("tester", []) == bound_key("critic", [{"id": "k"}]) == BOUND_KEY


# ---------------------------------------------------------------------------
# The citation rule
# ---------------------------------------------------------------------------

def test_one_candidate_binds_per_cited_standard_and_the_root_file_first(tmp_path):
    """The review of pass 1, low 4: 22 of 31 pushed lines in
    `src/icalendar/parser` restated RFC 5545 from docs files."""
    root = tmp_path / "proj"
    _write(root / "README.rst", "Pkg\n===\n\nPkg is compatible with RFC 5545.\n")
    _write(root / "docs/a.rst", "A\n=\n\nThe parser supports :rfc:`5545`.\n")
    _write(root / "docs/b.rst", "B\n=\n\nPkg conforms to RFC 5545 and RFC 7265.\n")
    _write(root / "src/pkg/fold.py", FOLD)
    _write(root / "src/pkg/jcal.py", '"""jCal, as RFC 7265 says."""\n')
    db = init_db(tmp_path / "rota.db")
    harvest.record(db, root, "c1")
    db.commit()
    rows = {r["path"]: r["rule"] for r in db.execute(
        "SELECT c.path, b.rule FROM commitment_candidates c "
        "LEFT JOIN candidate_bindings b ON b.witness_id = c.id "
        "WHERE c.path IN ('README.rst', 'docs/a.rst', 'docs/b.rst')")}
    # The README binds RFC 5545. The docs restatement of 5545 is unbound,
    # and docs/b.rst binds only for RFC 7265, which no root file cites.
    assert rows == {"README.rst": "standard", "docs/a.rst": None,
                    "docs/b.rst": "standard"}
    bound = {r["witness_id"]: set() for r in db.execute(
        "SELECT witness_id FROM candidate_bindings WHERE rule = 'standard'")}
    for r in db.execute("SELECT witness_id, path FROM candidate_bindings "
                        "WHERE rule = 'standard'"):
        bound[r["witness_id"]].add(r["path"])
    by_path = {db.execute("SELECT path FROM commitment_candidates WHERE id = ?",
                          (k,)).fetchone()["path"]: v for k, v in bound.items()}
    assert by_path == {"README.rst": {"src/pkg/fold.py"},
                       "docs/b.rst": {"src/pkg/jcal.py"}}
    db.close()


# ---------------------------------------------------------------------------
# Pass 3b: the review of pass 3
# ---------------------------------------------------------------------------

def test_a_statement_copies_only_the_bindings_inside_the_surveyed_area(tmp_path):
    """High 1: one statement of the RFC 5545 line copied 49 bindings over 8
    areas on icalendar. A statement now binds the surveyed area's files."""
    from rota.core.db import Write, _apply_write

    root = tmp_path / "proj"
    _write(root / "README.rst", "Pkg\n===\n\nPkg is compatible with RFC 5545.\n")
    _write(root / "src/pkg/fold.py", FOLD)
    _write(root / "src/other/thing.py", '"""As RFC 5545 says."""\n' + THING)
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)",
               (str(root),))
    for grain, area in (("src/pkg/fold.py", "src/pkg"),
                        ("src/other/thing.py", "src/other")):
        db.execute("INSERT INTO code_index (grain, grain_kind, area) "
                   "VALUES (?, 'path', ?)", (grain, area))
    harvest.record(db, root, "c1")
    db.commit()
    readme = _candidate(db, "doc_claim", "README.rst")
    assert {r["path"] for r in db.execute(
        "SELECT path FROM candidate_bindings WHERE witness_id = ?",
        (readme["id"],))} == {"src/pkg/fold.py", "src/other/thing.py"}

    def state(area):
        sb = session_sandbox(db, Wake("architect", "tick:survey", refs=(area,)))
        out = sb.call("model.amend", headline="README.rst: RFC 5545 calendars",
                      text="Other calendar programs read the files.",
                      party="other calendar programs",
                      behaviour="the files follow RFC 5545", witness=readme["id"])
        for table, row_id, values in sb.ctx.writes:
            _apply_write(db, Write(table, row_id, values), "architect")
        db.commit()
        return out

    out = state("src/pkg")
    assert out["bindings"] == ["src/pkg/fold.py"]
    # A statement of the same line in the other area adds that area's file.
    again = state("src/other")
    assert again["id"] == out["id"]
    assert {r["grain"] for r in db.execute(
        "SELECT grain FROM constraint_bindings WHERE constraint_id = ?",
        (out["id"],))} == {"src/pkg/fold.py", "src/other/thing.py"}
    db.close()


def test_the_developer_fix_wake_carries_the_commitment_of_the_fail(proj):
    """Medium 2: the fix wake after a commitment fail had no commitment
    block, and its brief said that a fail names a criterion."""
    _, db = proj
    _state(db)
    _, pushed = _push(db, "developer", "tick:verdict_failed")
    assert BOUND_KEY not in pushed
    db.execute("INSERT INTO verdicts (id, batch_id, result, failed_commitment, "
               "reason) VALUES ('critic:b1:None', 'b1', 'fail', 'fold_octets', "
               "'It counts characters.')")
    db.commit()
    _, pushed = _push(db, "developer", "tick:verdict_failed")
    assert [r["id"] for r in pushed[BOUND_KEY]] == ["fold_octets"]
    from rota import paths
    brief = (paths.PROMPTS / "developer" / "verdict_failed.md").read_text(
        encoding="utf-8")
    assert "A fail names a criterion in `failed_criterion` or a pushed commitment" in brief


def test_the_tester_files_a_test_that_guards_a_pushed_commitment(proj):
    """Medium 3: `tests.encode` took a criterion only, so the Tester's
    line had no door."""
    _, db = proj
    _state(db)
    sb, _ = _push(db, "tester", "tick:tests_missing")
    out = sb.call("tests.encode", id="tst_octets", criterion_id="fold_octets",
                  path="tests/test_fold_octets.py",
                  body="from pkg.fold import fold\n"
                       "def test_octets():\n"
                       "    assert all(len(p.encode()) <= 75 for p in [fold('a' * 80)])\n")
    assert out == {"id": "tst_octets", "guards": "fold_octets"}
    row = [v for t, _, v in sb.ctx.writes if t == "tests"][0]
    assert row["criterion_id"] is None and row["commitment_id"] == "fold_octets"
    _falsify(db)
    sb, _ = _push(db, "tester", "tick:tests_missing")
    with pytest.raises(ValueError, match="not a commitment that the push showed"):
        sb.call("tests.encode", id="tst_octets", criterion_id="fold_octets",
                path="tests/test_fold_octets.py",
                body="def test_octets():\n    assert True\n")


def test_the_structural_review_readers_drop_a_falsified_commitment(proj):
    """Medium 4: `_reaching_constraints` and `constraints_for_grains` still
    returned the falsified row."""
    from rota.core.scheduler import constraints_for_grains

    _, db = proj
    _state(db)
    assert "fold_octets" in api._reaching_constraints(db, ["src/pkg/fold.py"])
    assert "fold_octets" in constraints_for_grains(db, ["src/pkg/fold.py"])
    _falsify(db)
    assert "fold_octets" not in api._reaching_constraints(db, ["src/pkg/fold.py"])
    assert "fold_octets" not in constraints_for_grains(db, ["src/pkg/fold.py"])


def test_every_fail_sentence_of_the_critic_names_the_commitment_route():
    from rota import paths

    for name in ("base.md", "review.md"):
        text = " ".join((paths.PROMPTS / "critic" / name).read_text(
            encoding="utf-8").split())
        assert "the pushed commitment it breaks" in text, name


# ---------------------------------------------------------------------------
# B2: a pushed commitment is a row of the Critic's pass hold
# ---------------------------------------------------------------------------

LIMIT_LINE = "def fold(line, limit=80):"
CUT_LINE = "    return line[:limit]"


@pytest.fixture
def review(proj, tmp_path):
    """Batch `b1` moves the fold limit to 80 and cuts the line at it. One
    criterion asks for the cut, and the stated commitment says 75."""
    from tests.rota.test_verdict_lines import _git

    root, db = proj
    _git(root, "init", "-q")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    tree = tmp_path / "batch"
    _git(root, "worktree", "add", "-q", "-b", "batch/b1", str(tree))
    after = FOLD.replace("def fold(line, limit=75):", LIMIT_LINE).replace(
        "    return line\n", CUT_LINE + "\n")
    (tree / "src/pkg/fold.py").write_bytes(after.encode())
    _git(tree, "commit", "-q", "-am", "cut at the limit")
    db.execute("UPDATE batches SET worktree = ?, head_commit = 'abc123' "
               "WHERE id = 'b1'", (str(tree),))
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('tk1', 'it', 'cut the line')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
               "('b1', 'tk1')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c1', 'tk1', 'fold cuts the line at its limit')")
    db.commit()
    c = _state(db)
    sb, _ = _push(db, "critic", "tick:review")
    return db, sb, c


def _hold(sb, lines) -> str:
    with pytest.raises(api.PassHeld) as got:
        sb.call("verdicts.emit", batch_id="b1", result="pass", lines=lines)
    assert not [w for w in sb.ctx.writes if w[0] == "verdicts"]
    return str(got.value)


def test_a_pass_line_on_a_pushed_commitment_is_accepted(review):
    """Rule 1. The pass door refused `lines={k: ...}`. It now accepts the
    entry, and the pass lands after the hold with the line on record."""
    db, sb, _ = review
    lines = {"c1": CUT_LINE.strip(), "fold_octets": LIMIT_LINE}
    _hold(sb, lines)
    out = sb.call("verdicts.emit", batch_id="b1", result="pass", lines=lines)
    assert out["result"] == "pass"
    row = [v for t, _, v in sb.ctx.writes if t == "verdicts"][0]
    assert json.loads(row["lines"])["fold_octets"] == LIMIT_LINE
    # The routes stay the criteria's.
    assert set(json.loads(row["routes"])) == {"c1"}
    # A key that is neither a criterion nor a pushed commitment still fails.
    sb2, _ = _push(db, "critic", "tick:review")
    with pytest.raises(api.LinesRefusal, match="is not a criterion of batch"):
        sb2.call("verdicts.emit", batch_id="b1", result="pass",
                 lines={"c1": CUT_LINE.strip(), "nothing": LIMIT_LINE})


def test_the_hold_asks_the_commitment_its_own_question(review):
    """Rule 2. One question per commitment inside the one hold. It quotes
    the witness line, the seat's line and the behaviour."""
    _, sb, c = review
    said = _hold(sb, {"c1": CUT_LINE.strip(), "fold_octets": LIMIT_LINE})
    assert said.startswith("before the pass lands, answer for c1 and fold_octets.")
    assert 'Criterion c1 says: "fold cuts the line at its limit".' in said
    assert (f"Commitment fold_octets rests on src/pkg/fold.py line {c['line']}: "
            in said)
    assert c["text"].strip() in said
    assert (f"Your line holds '{LIMIT_LINE}'. Does that line keep "
            f"\"a folded line holds at most 75 octets\"?") in said
    assert said.count("Commitment fold_octets") == 1
    # A pass that names no line for the commitment still gets its question.
    sb2, _ = _push(sb.ctx.conn, "critic", "tick:review")
    said = _hold(sb2, {"c1": CUT_LINE.strip()})
    assert ("Does the diff keep that line and \"a folded line holds at most "
            "75 octets\"?") in said


def test_a_claim_on_a_pushed_commitment_is_kept_under_its_id(review):
    """Rule 3. `claim_encodes` refused the commitment id as no criterion.
    It now keeps the claim under the commitment and writes no row."""
    db, sb, _ = review
    out = sb.call("verdicts.claim_encodes", criterion_id="fold_octets",
                  encodes=True)
    assert out["commitment_id"] == "fold_octets"
    assert sb.ctx.verdict_claims["fold_octets"] is True
    assert not db.execute("SELECT 1 FROM criteria WHERE id = 'fold_octets'"
                          ).fetchone()
    assert not sb.ctx.writes
    with pytest.raises(ValueError):
        sb.call("verdicts.claim_encodes", criterion_id="no_such_row",
                encodes=True)


def test_a_no_at_the_hold_is_the_seats_fail_on_the_commitment(review):
    """Rule 4. The hold names the fail on the commitment. The seat's fail
    takes the route that a fail on a commitment takes today."""
    _, sb, c = review
    said = _hold(sb, {"c1": CUT_LINE.strip(), "fold_octets": LIMIT_LINE})
    assert said.endswith("send the pass again or your own fail on the "
                         "criterion or the commitment.")
    sb.call("verdicts.emit", batch_id="b1", result="fail",
            failed_criterion="fold_octets",
            reason="The diff moves the limit to 80.")
    row = [v for t, _, v in sb.ctx.writes if t == "verdicts"][0]
    assert row["failed_commitment"] == "fold_octets"
    assert row["failed_criterion"] is None
    assert c["text"].strip() in row["reason"]


# ---------------------------------------------------------------------------
# Pass 3c: a guard test is the batch's own test
# ---------------------------------------------------------------------------

GUARD = "commitment fold_octets: a folded line holds at most 75 octets"


def _red_guard(db, merged_other=False):
    """A guard test of `fold_octets`, red at the batch's head."""
    _state(db)
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, commitment_id, path, "
               "body) VALUES ('tst_octets', 'b1', NULL, 'fold_octets', "
               "'tests/test_fold_octets.py', 'def test_octets():\n    assert False\n')")
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, "
               "output) VALUES ('r1', 'b1', 'tst_octets', NULL, 'fail', "
               "'tests/test_fold_octets.py:2: AssertionError')")
    db.commit()


def test_tests_load_names_the_commitment_of_a_guard_test(proj):
    _, db = proj
    _red_guard(db)
    sb, _ = _push(db, "developer", "tick:tests_failing")
    row = next(r for r in sb.call("tests.load") if r["id"] == "tst_octets")
    assert row["guards"] == GUARD
    assert row["criterion_id"] is None
    assert "assert False" in row["body"]


def test_the_fix_wake_lists_a_red_guard_test_as_the_batchs_own(proj):
    _, db = proj
    _red_guard(db)
    _, pushed = _push(db, "developer", "tick:tests_failing")
    shown = pushed["tests.load"]
    assert [r["id"] for r in shown["the batch's tests, not passing"]] == ["tst_octets"]
    assert "the project's own tests, not passing at your commit" not in shown


def test_the_scheduler_readers_count_a_guard_test_as_the_batchs_own(proj):
    from rota.core import scheduler

    _, db = proj
    _red_guard(db)
    own, project = scheduler.park_reds(db, "b1")
    assert [r["test_id"] for r in own] == ["tst_octets"] and project == []
    assert "t:tst_octets:" in scheduler._park_versions(db, "b1")


def test_the_harness_keeps_the_filter_of_a_merged_guard_test(proj):
    from rota.core.harness import tester_paths

    _, db = proj
    _red_guard(db)
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b0', 'it', 'merged')")
    db.execute("UPDATE tests SET batch_id = 'b0' WHERE id = 'tst_octets'")
    db.commit()
    assert tester_paths(db, "b1") == {"tests/test_fold_octets.py"}


def test_the_green_at_head_refusal_names_the_commitment(proj):
    from rota.core.sandbox import _green_at_head_refusal

    _, db = proj
    _red_guard(db)
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES "
               "('tst_green', 'b1', NULL, 'tests/test_g.py', 'x')")
    db.execute("UPDATE batches SET head_commit = 'h1' WHERE id = 'b1'")
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, "
               "output) VALUES ('r2', 'b1', 'tst_green', 'h1', 'pass', '1 passed')")
    db.commit()
    sb, _ = _push(db, "developer", "tick:tests_failing")
    said = _green_at_head_refusal(sb.ctx, ["tst_green"])
    assert said and f"tst_octets ({GUARD})" in said


def test_the_park_page_shows_the_commitment_beside_the_guard_test(proj):
    from rota.roles.principal import _park_page

    _, db = proj
    _red_guard(db)
    text, _ = _park_page(db, "b1", ["b1", "it"])
    assert "tests/test_fold_octets.py, which guards commitment fold_octets, failed" in text


def test_the_testers_ask_needs_a_row_with_a_witness_and_a_party():
    """The second look at passes 4c to 4e, high B. `bound_constraints` lists
    survey surfaces and decided rows too, and a batch that only a surface
    binds got the ask to guard a pushed commitment."""
    surface = {"id": "k1", "headline": "price_for keeps its signature",
               "text": "callers rely on this"}
    assert bound_key("tester", [surface]) == BOUND_KEY
    stated = {"id": "k2", "headline": "pyproject.toml: Python 3.10",
              "party": "installers", "behaviour": "Python 3.10 or later",
              "witness": 'pyproject.toml line 3: "requires-python"'}
    assert bound_key("tester", [surface, stated]) == TESTER_BOUND_KEY
    assert bound_key("tester", [{**stated, "party": ""}]) == BOUND_KEY
