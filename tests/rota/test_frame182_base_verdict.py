"""Frames 182 and 171, dry run 8 (2026-11-08): the test was the only
arbiter between the Tester and the Developer, and no record judged it.
tst_c1 v2 passed on the unchanged fold, and tst_c3 failed on a fold that
already kept 75 octets. The base verdict of a criterion test is a fact:
the encode door reads it, and the Tester's challenge wake states it."""
import json
import subprocess

import pytest

from rota.core import harness
from rota.core.db import init_db
from rota.core.runner import _base_verdict_lines
from rota.core.sandbox import build
from rota.roles import api
from rota.roles.api import Wall

# The base fold of icalendar 99619246, cut to its behaviour: a fold every
# 75 octets, inside a word, with CRLF and a space.
BASE_FOLD = '''def _foldline(line, limit=75, fold_sep="\\r\\n "):
    if len(line.encode("utf-8")) <= limit:
        return line
    parts, current, size = [], "", 0
    for ch in line:
        n = len(ch.encode("utf-8"))
        if size + n > limit:
            parts.append(current)
            current, size = " ", 1
        current += ch
        size += n
    parts.append(current)
    return "\\r\\n".join(parts)
'''
# s198's bent fold, 4d42947d: one octet less after each fold.
BENT_FOLD = BASE_FOLD.replace("if size + n > limit:", "if size + n >= limit:")

C1 = ("The _foldline function must not split a word at any point; it may "
      "only insert a CRLF followed by a space between existing characters.")
C3 = ("The function must return a string where every line is at most 75 "
      "octets long, excluding the line break.")
KEPT = "cw_7039d1d2d899"

# tst_c1 version 2, s166's rewrite under m36, as `tests` stores it. The
# import names this fixture's module.
TST_C1_V2 = (
    'from fold import _foldline\n\n'
    'def test_foldline_inserts_crlf_space_between_words():\n'
    '    text = "word1 word2 word3" * 50\n'
    '    result = _foldline(text)\n'
    '    lines = result.split("\\n")\n'
    '    for i, line in enumerate(lines[:-1]):\n'
    '        assert line.endswith("\\r"), f"Line {i} should end with CRLF: {line!r}"\n')
# tst_c1 version 1, rebuilt from the read's W1: a folded line ends with a
# space, on an LF split. The night kept the run's tail and not the body.
TST_C1_V1 = TST_C1_V2.replace('line.endswith("\\r")', 'line.endswith(" ")')
# tst_c3 as `tests` stores it, its first function: the LF split counts the CR.
TST_C3 = (
    'from fold import _foldline\n\n'
    'def test_foldline_returns_lines_at_most_75_octets():\n'
    '    text = "A" * 100\n'
    '    result = _foldline(text)\n'
    '    lines = result.split("\\n")\n'
    '    for line in lines:\n'
    '        assert len(line.encode("utf-8")) <= 75, f"Line exceeds 75 octets: {len(line)}"\n')
# The right c3 test splits on CRLF.
RIGHT_C3 = TST_C3.replace('result.split("\\n")', 'result.split("\\r\\n")')


def _git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), "-c", "user.name=t",
                           "-c", "user.email=t@t", *args], check=True,
                          capture_output=True, text=True).stdout.strip()


@pytest.fixture
def db(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "fold.py").write_bytes(BASE_FOLD.encode("utf-8"))
    _git(proj, "init", "-q")
    _git(proj, "add", "fold.py")
    _git(proj, "commit", "-q", "-m", "base")
    wt = tmp_path / "wt"
    _git(proj, "worktree", "add", "-q", "-b", "batch/bg_1", str(wt))
    # The Developer's commit: the head is not the base.
    (wt / "fold.py").write_bytes(BENT_FOLD.encode("utf-8"))
    _git(wt, "commit", "-q", "-am", "bend")
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
                 "('project_root', ?)", (json.dumps(str(proj)),))
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1','fold at a space','in_scope',"
                 "'approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk_1','i1','fold long lines at a space')")
    for cid, text in (("c1", C1), ("c3", C3)):
        conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                     "VALUES (?, 'tk_1', ?, '[\"fold.py::_foldline\"]')",
                     (cid, text))
    conn.execute("INSERT INTO batches (id, item_id, status, worktree, "
                 "head_commit) VALUES ('bg_1','i1','running',?,?)",
                 (str(wt), _git(wt, "rev-parse", "HEAD")))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) "
                 "VALUES ('bg_1','tk_1')")
    conn.commit()
    return conn


@pytest.fixture
def kept_c3(monkeypatch):
    """c3's text is the text of a commitment that binds the batch."""
    row = {"id": KEPT, "headline": f"fold.py: {C3}", "text": C3,
           "party": "parser", "behaviour": C3}
    monkeypatch.setattr(api, "_bound_rows",
                        lambda conn, bid, diff: (["fold.py"], [row]))


def _encode(db, cid, path, body):
    sb = build("tester", db, batch_id="bg_1", mode="tests_missing")
    sb.call("tests.triage", criterion_id=cid, verdict="encodable")
    return sb.call("tests.encode", id=f"tst_{cid}", criterion_id=cid,
                   path=path, body=body)


def test_tst_c1_v2_green_at_the_base_is_refused(db):
    """W1: v2 passes on the unchanged fold, so it proves nothing."""
    with pytest.raises(Wall) as got:
        _encode(db, "c1", "test_foldline.py", TST_C1_V2)
    said = str(got.value)
    assert api.BASE_GREEN_WORDS in said
    assert "The base run ended with: 1 passed" in said
    # The run put the Developer's fold back.
    wt = db.execute("SELECT worktree FROM batches").fetchone()["worktree"]
    from pathlib import Path
    assert (Path(wt) / "fold.py").read_bytes() == BENT_FOLD.encode("utf-8")
    assert not (Path(wt) / "test_foldline.py").exists()


def test_tst_c1_v1_red_at_the_base_lands(db):
    assert _encode(db, "c1", "test_foldline.py", TST_C1_V1)["id"] == "tst_c1"


def test_tst_c3_red_at_the_base_on_a_kept_commitment_is_refused(db, kept_c3):
    """W2: the base keeps 75 octets, and tst_c3 counts the CR. The head's
    bent fold passes it, so only the base run shows the test is wrong."""
    db.execute("INSERT INTO claim_runs (id, batch_id, commit_sha, program, "
               "stdout, returncode) VALUES ('cr1','bg_1','x',"
               "'print(_foldline(\"A\" * 100))', ?, 0)",
               (("A" * 75 + "\r\n " + "A" * 25).encode("utf-8"),))
    db.commit()
    with pytest.raises(Wall) as got:
        _encode(db, "c3", "test_foldline_75octets.py", TST_C3)
    said = str(got.value)
    assert api.BASE_RED_WORDS.format(commitment=KEPT) in said
    assert "The base run ended with: 1 failed" in said
    assert api.claim_run_words(db, "bg_1") in said
    assert f"Make the test check only what c3 says: {C3}" in said


def test_a_right_c3_test_green_at_the_base_lands(db, kept_c3):
    assert _encode(db, "c3", "test_foldline_75octets.py",
                   RIGHT_C3)["id"] == "tst_c3"


def test_a_change_criterion_test_red_at_the_base_is_not_a_kept_refusal(db):
    """Without a tie in the rows, c3 is a change criterion: dry run 8's c3
    words differ from cw_99502ef494ad's, so tst_c3 lands."""
    assert api.criterion_commitment(db, "bg_1", "c3") is None
    assert _encode(db, "c3", "test_foldline_75octets.py",
                   TST_C3)["id"] == "tst_c3"


def test_a_test_row_that_cites_a_commitment_makes_the_criterion_kept(db):
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, commitment_id, "
               "path, body) VALUES ('tst_g','bg_1','c3',?,'g.py','')", (KEPT,))
    assert api.criterion_commitment(db, "bg_1", "c3") == KEPT
    assert api.criterion_commitment(db, "bg_1", "c1") is None


def _store(db, tid, cid, path, body):
    db.execute("INSERT OR REPLACE INTO tests (id, batch_id, criterion_id, "
               "path, body) VALUES (?, 'bg_1', ?, ?, ?)", (tid, cid, path, body))


def test_the_reader_says_none_before_the_base_run_and_after_a_replace(db):
    _store(db, "tst_c1", "c1", "test_foldline.py", TST_C1_V1)
    assert harness.base_verdict(db, "bg_1", "tst_c1") == ("none", "")
    harness.record_criterion_bases(db, "bg_1")
    verdict, last = harness.base_verdict(db, "bg_1", "tst_c1")
    assert verdict == "fail" and last.startswith("1 failed")
    # W1: a replace of the body leaves no verdict for the new body.
    _store(db, "tst_c1", "c1", "test_foldline.py", TST_C1_V2)
    assert harness.base_verdict(db, "bg_1", "tst_c1") == ("none", "")
    harness.record_criterion_bases(db, "bg_1")
    assert harness.base_verdict(db, "bg_1", "tst_c1")[0] == "pass"


def test_the_challenge_wake_carries_the_base_verdict(db):
    """Frame 171: m39 challenged tst_c3, and s171 held it. The wake now
    says that the test is red on the code before the change."""
    _store(db, "tst_c3", "c3", "test_foldline_75octets.py", TST_C3)
    inbound = {"resolved_refs": {"c3": {}, "tst_c3": {}}}
    assert _base_verdict_lines(db, inbound) == []
    harness.record_criterion_bases(db, "bg_1")
    lines = _base_verdict_lines(db, inbound)
    assert len(lines) == 1
    assert lines[0].startswith("\ntst_c3: at the base this test is red. "
                               "The base run ended with: 1 failed")


def test_a_batch_with_no_git_worktree_has_no_base_run(db, tmp_path):
    bare = tmp_path / "bare"
    bare.mkdir()
    db.execute("UPDATE batches SET worktree = ?", (str(bare),))
    assert harness.run_at_base(db, "bg_1", "test_foldline.py", TST_C1_V2) is None
    sb = build("tester", db, batch_id="bg_1", mode="tests_missing")
    assert api._base_verdict_refusal(sb.ctx, "bg_1", "c1", "test_foldline.py",
                                     TST_C1_V2) is None
