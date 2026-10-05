"""
The revert door of `code.commit` reads the runs of both commits (frame 149).

The door refuses a commit whose tree equals the tree before the last commit.
Its sentence said "The tests pass both ways" and it read no run. Night 124
(2026-10-05): the head 35211b40e4 failed at import, 37 of 37 `error`, and
the door refused the Developer's repair 3 times. The batch was given up at
that head. The door now admits a commit that restores a tree where fewer of
the tests fail, and its refusal states the runs that it read.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from rota.core import sandbox
from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import api, prompts

FIXTURE = Path(__file__).parent / "fixtures" / "night124_utils_617055787d.txt"

# The old sentence, copied from the door at 483cba6. Where both commits truly
# pass, the refusal stays equal to it, because the recorded cases key on it.
OLD = ("this commit puts the tree back where it stood before your last "
       "commit: you are undoing yourself. The tests pass both ways, so "
       "the disagreement is not in the code. Say what stands and why "
       "(a decision), challenge the test (msg.challenge_tester) or "
       "escalate the criterion (msg.escalate_architect); do not flip")

# s143's commit 35211b40e4 on night 124: these 20 lines at the end of
# src/click/utils.py. No line of the module binds `click`.
S143_TAIL = '''

@click.command()
def echo_json_cmd(obj: object) -> None:
    """Print an object as compact JSON to the stream.

    .. versionadded:: 8.5

    :param obj: The object to serialize and print.
    """
    import json

    try:
        out = json.dumps(obj, separators=(",", ":"))
    except (TypeError, ValueError) as e:
        raise TypeError(str(e)) from None

    file = _default_text_stdout()
    file.write(out + "\\n")
    file.flush()
'''

# s144's write at turn 13 of night 124, as the seat sent it.
S144_TEXT = r'''def echo_json(obj: object) -> None:
    """Print an object as compact JSON to the stream.

    .. versionadded:: 8.5

    :param obj: The object to serialize and print.
    """
    import json

    try:
        out = json.dumps(obj, separators=(",", ":"))
    except (TypeError, ValueError) as e:
        raise TypeError(str(e)) from None

    file = _default_text_stdout()
    file.write(out + "\n")
    file.flush()'''


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
                 "VALUES ('i1','echo json','in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1','echo json')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('c1','tk1','echo_json prints the object as compact JSON')")
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) VALUES "
                 "('b1','i1','running','abc123')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    conn.commit()
    return conn


def _repo(root: Path, path: str, *texts: str) -> list[str]:
    """A worktree with one commit per text of `path`. Returns the shas."""
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    shas = []
    for n, text in enumerate(texts):
        f = root / path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(text.encode("utf-8"))
        subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t",
                        "commit", "-q", "-m", f"c{n}"], check=True)
        shas.append(subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                                   capture_output=True, text=True, check=True).stdout.strip())
    return shas


def _tests(db, rows: list[tuple[str, str | None]]) -> None:
    for tid, crit in rows:
        db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                   "VALUES (?, 'b1', ?, ?, 'assert True')", (tid, crit, f"tests/test_{tid}.py"))


def _runs(db, sha: str, attempt: int, results: dict) -> None:
    for tid, res in results.items():
        db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, attempt) "
                   "VALUES (?, 'b1', ?, ?, ?, ?)", (f"r_{sha[:8]}_{attempt}_{tid}", tid, sha, res, attempt))


def _developer(db, root: Path):
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    return build("developer", db, batch_id="b1", mode="tests_failing",
                 allow=prompts.mode_tools("developer", "tests_failing"))


def test_the_repair_of_a_head_that_fails_at_import_is_admitted(db, tmp_path):
    """s144 turn 13, night 124: the write puts back 617055787d, where 34 of
    37 tests pass. The head 35211b40e4 is 37 of 37 `error`. The door refused
    the commit with "The tests pass both ways"."""
    parent = FIXTURE.read_bytes().decode("utf-8")
    root = tmp_path / "wt"
    back, head = _repo(root, "src/click/utils.py", parent, parent + S143_TAIL)
    own = [("inh_echo_json_01", "c1"), ("inh_echo_json_02", "c1"), ("inh_echo_json_03", "c1")]
    project = [(f"inh_p{k:02d}", None) for k in range(34)]
    _tests(db, own + project)
    _runs(db, back, 3, {**{t: "fail" for t, _ in own}, **{t: "pass" for t, _ in project}})
    _runs(db, head, 4, {t: "error" for t, _ in own + project})
    sb = _developer(db, root)
    sb.call("code.write", path="src/click/utils.py", text=S144_TEXT, start=688, end=725)
    # code.write writes the platform's line ends, so the bytes compare as lines.
    written = (root / "src/click/utils.py").read_bytes().replace(b"\r\n", b"\n")
    assert written == FIXTURE.read_bytes()
    out = sb.call("code.commit", message="Remove echo_json_cmd to avoid import cycle")
    assert out.get("committed") is True


def test_where_both_commits_pass_the_refusal_is_the_old_sentence(db, tmp_path):
    a = "def close_account(x):\n    return 1\n"
    b = a + "\n"
    root = tmp_path / "wt"
    back, head = _repo(root, "script.py", a, b)
    _tests(db, [("tst1", "c1"), ("tst2", None)])
    _runs(db, back, 1, {"tst1": "pass", "tst2": "pass"})
    _runs(db, head, 2, {"tst1": "pass", "tst2": "pass"})
    sb = _developer(db, root)
    sb.call("code.write", path="script.py", text=a)
    with pytest.raises(ValueError) as exc:
        sb.call("code.commit", message="back to a")
    assert str(exc.value) == f"code.commit: {OLD}" or str(exc.value) == OLD
    # The sentence is the old one, and the runs it rests on are now facts
    # that frame 144's fact check reads.
    facts = [f for f in sb.ctx.facts if f.kind == "runs"]
    assert [dict(f.where)["at"] for f in facts] == ["HEAD", "HEAD~1"]
    assert all(r["ok"] for r in sandbox.check_facts(sb, facts))


def test_a_revert_where_the_head_is_not_worse_states_the_runs(db, tmp_path):
    """Night 123 (2026-10-05): 7 refusals at 70723b7576, 35 pass and 2 red,
    and the tree put back was 35 pass and 2 red too. The door refuses, and
    it no longer says that the tests pass."""
    a = "def close_account(x):\n    return 1\n"
    b = "def close_account(x):\n    return 2\n"
    root = tmp_path / "wt"
    back, head = _repo(root, "script.py", a, b)
    _tests(db, [("tst1", "c1"), ("tst2", None), ("tst3", None)])
    _runs(db, back, 1, {"tst1": "fail", "tst2": "pass"})
    _runs(db, head, 2, {"tst1": "fail", "tst2": "pass", "tst3": "fail"})
    sb = _developer(db, root)
    sb.call("code.write", path="script.py", text=a)
    with pytest.raises(ValueError) as exc:
        sb.call("code.commit", message="back to a")
    said = str(exc.value)
    assert "pass both ways" not in said
    assert said.endswith(
        "this commit puts the tree back where it stood before your last commit: you are "
        f"undoing yourself. The runs at the head {head[:10]}: 1 pass, 2 red, 0 error. "
        f"The runs at {back[:10]}, the tree this commit puts back: 1 pass, 1 red, 0 error. "
        f"Of the 2 tests that ran at both, the head fails 1 and {back[:10]} fails 1. "
        "Going back does not lower that count. Change the code that "
        "the red tests call, then commit. Do not flip. To dispute the criterion, send "
        "msg.escalate_architect(refs=['c1']).")
    # The escalation is the step the sentence names, and the follow check of
    # the conftest sends it through the doors.
    assert [(o.op, o.args) for o in sb.ctx.offers] == [
        ("msg.escalate_architect", {"refs": ["c1"]})]


def test_a_runs_fact_that_the_state_contradicts_reads_false(db, tmp_path):
    root = tmp_path / "wt"
    back, head = _repo(root, "script.py", "x = 1\n", "x = 2\n")
    _tests(db, [("tst1", "c1")])
    _runs(db, head, 1, {"tst1": "error"})
    _runs(db, head, 2, {"tst1": "fail"})
    sb = _developer(db, root)
    fact = lambda value, at, sha: api.Fact("runs", value, (("at", at), ("sha", sha)))
    got = sandbox.check_facts(sb, [fact({"tst1": "fail"}, "HEAD", head),
                                   fact({"tst1": "error"}, "HEAD", head),
                                   fact({"tst1": "fail"}, "HEAD~1", head),
                                   fact({}, "HEAD~1", back)])
    assert [r["ok"] for r in got] == [True, False, False, True]
