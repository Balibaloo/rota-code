"""
The revert door of `code.commit` reads the runs of both commits (frame 149).

The door refuses a commit whose tree equals the tree before the last commit.
Its sentence said "The tests pass both ways" and it read no run. Night 124
(2026-10-05): the head 35211b40e4 failed at import, 37 of 37 `error`, and
the door refused the Developer's repair 3 times. The batch was given up at
that head. The door now admits a commit that turns no test red and one test
green, and its refusal states the runs that it read.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from rota.core import sandbox
from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import api, prompts
from rota.testkit.gitfixture import copy_template

FIXTURE = Path(__file__).parent / "fixtures" / "night124_utils_617055787d.txt"

# The old sentence, copied from the door at 483cba6, up to its step. Where both
# commits truly pass, the refusal keeps these bytes. The old step named two
# calls with no refs, and the review of 9278be2, finding 5, replaced it.
OLD = ("this commit puts the tree back where it stood before your last "
       "commit: you are undoing yourself. The tests pass both ways, so "
       "the disagreement is not in the code. Say what stands and why "
       "(a decision)")

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
    # A copy of the tree built once per process for these values. The git
    # calls per test were the file's cost (frame 206's count, 2026-10-11).
    if root.exists():
        raise FileExistsError(root)
    return list(copy_template(("revert_door_repo", root.name, path, texts),
                              lambda base: _build_repo(base / root.name, path, *texts),
                              root.parent))


def _build_repo(root: Path, path: str, *texts: str) -> list[str]:
    """Build `_repo`'s worktree at `root`, and return the shas."""
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


def _tests(db, rows: list[tuple[str, str | None]], body: str = "assert True") -> None:
    for tid, crit in rows:
        db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                   "VALUES (?, 'b1', ?, ?, ?)", (tid, crit, f"tests/test_{tid}.py", body))


def _runs(db, sha: str, attempt: int, results: dict, batch: str = "b1") -> None:
    for tid, res in results.items():
        db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, attempt) "
                   "VALUES (?, ?, ?, ?, ?, ?)",
                   (f"r_{batch}_{sha[:8]}_{attempt}_{tid}", batch, tid, sha, res, attempt))


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
    assert str(exc.value) == f"{OLD}, and do not flip."
    assert sb.ctx.offers == []
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
        "Going back makes no test pass that fails at the head. Change the code that "
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


def _refused(sb, path: str, text: str) -> str:
    sb.call("code.write", path=path, text=text)
    with pytest.raises(ValueError) as exc:
        sb.call("code.commit", message="back")
    return str(exc.value)


A = "def close_account(x):\n    return 1\n"
B = "def close_account(x):\n    return 2\n"
HEAD_SAID = ("this commit puts the tree back where it stood before your last commit: "
             "you are undoing yourself.")


def test_the_revert_of_a_fix_that_turned_other_tests_red_is_refused(db, tmp_path):
    """The review of 9278be2, finding 1, state `unrelated_two_red_at_head`:
    the seat's own test goes green at the head and two project tests go red.
    A net count admitted the revert of the fix. Going back turns the own
    test red, so the door refuses and names it."""
    root = tmp_path / "wt"
    back, head = _repo(root, "script.py", A, B)
    _tests(db, [("tst1", "c1"), ("p1", None), ("p2", None)])
    _runs(db, back, 1, {"tst1": "fail", "p1": "pass", "p2": "pass"})
    _runs(db, head, 2, {"tst1": "pass", "p1": "fail", "p2": "fail"})
    sb = _developer(db, root)
    said = _refused(sb, "script.py", A)
    assert said == (
        f"{HEAD_SAID} The runs at the head {head[:10]}: 1 pass, 2 red, 0 error. "
        f"The runs at {back[:10]}, the tree this commit puts back: 2 pass, 1 red, 0 error. "
        f"Of the 3 tests that ran at both, the head fails 2 and {back[:10]} fails 1. "
        "Going back turns 1 test red that passes at the head: tst1. Change the code "
        "that the red tests call, then commit. Do not flip.")
    kinds = sorted(f.kind for f in sb.ctx.facts)
    assert kinds == ["both", "runs", "runs", "turns_red"]
    assert all(r["ok"] for r in sandbox.check_facts(sb, sb.ctx.facts))


def test_a_red_test_outside_both_does_not_stop_the_repair(db, tmp_path):
    """A test red at `HEAD~1` and with no run at the head has no side in the
    rule. The head fails the test that passed before, so the door admits."""
    root = tmp_path / "wt"
    back, head = _repo(root, "script.py", A, B)
    _tests(db, [("tst1", "c1"), ("tst2", "c1")])
    _runs(db, back, 1, {"tst1": "pass", "tst2": "fail"})
    _runs(db, head, 2, {"tst1": "error"})
    sb = _developer(db, root)
    sb.call("code.write", path="script.py", text=A)
    assert sb.call("code.commit", message="back").get("committed") is True


def test_the_runs_of_another_batch_at_the_sha_are_not_read(db, tmp_path):
    root = tmp_path / "wt"
    back, head = _repo(root, "script.py", A, B)
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b2','i1','pending')")
    _tests(db, [("tst1", "c1")])
    _runs(db, back, 1, {"tst1": "pass"})
    _runs(db, head, 2, {"tst1": "error"})
    _runs(db, head, 2, {"tst1": "pass"}, batch="b2")
    sb = _developer(db, root)
    fact = api.Fact("runs", {"tst1": "error"}, (("at", "HEAD"), ("sha", head)))
    assert [r["ok"] for r in sandbox.check_facts(sb, [fact])] == [True]
    sb.call("code.write", path="script.py", text=A)
    assert sb.call("code.commit", message="back").get("committed") is True


def test_a_commit_with_no_run_does_not_get_the_old_sentence(db, tmp_path):
    root = tmp_path / "wt"
    back, head = _repo(root, "script.py", A, B)
    _tests(db, [("tst1", "c1")])
    _runs(db, head, 1, {"tst1": "pass"})
    sb = _developer(db, root)
    said = _refused(sb, "script.py", A)
    assert said == (
        f"{HEAD_SAID} The runs at the head {head[:10]}: 1 pass, 0 red, 0 error. "
        f"No run is stored at {back[:10]}, the tree this commit puts back. So no run "
        "shows that going back makes a test pass. Say what stands and why (a "
        "decision), and do not flip.")
    assert sb.ctx.offers == []


def test_an_escalation_sent_this_session_is_not_named_again(db, tmp_path):
    root = tmp_path / "wt"
    back, head = _repo(root, "script.py", A, B)
    _tests(db, [("tst1", "c1")])
    _runs(db, back, 1, {"tst1": "fail"})
    _runs(db, head, 2, {"tst1": "fail"})
    sb = _developer(db, root)
    sb.call("msg.escalate_architect", refs=["c1"])
    said = _refused(sb, "script.py", A)
    assert said.endswith("Change the code that the red tests call, then commit. Do not flip.")
    assert sb.ctx.offers == []


def test_a_head_with_no_red_names_the_challenge_on_the_red_test_put_back(db, tmp_path):
    """The review of 9278be2, finding 5: the old step named two calls with
    no refs and no record. The step now names the challenge on the test that
    fails at `HEAD~1`, through `_offer`, so the follow check sends it."""
    body = ("from script import close_account\n\n\ndef test_close():\n"
            "    assert close_account('a1') == 2\n")
    root = tmp_path / "wt"
    back, head = _repo(root, "script.py", A, B)
    _tests(db, [("tst1", "c1")], body=body)
    _runs(db, back, 1, {"tst1": "fail"})
    _runs(db, head, 2, {"tst1": "pass"})
    sb = _developer(db, root)
    said = _refused(sb, "script.py", A)
    assert said == (
        f"{HEAD_SAID} The runs at the head {head[:10]}: 1 pass, 0 red, 0 error. "
        f"The runs at {back[:10]}, the tree this commit puts back: 0 pass, 1 red, 0 error. "
        f"Of the 1 test that ran at both, the head fails 0 and {back[:10]} fails 1. "
        "Going back turns 1 test red that passes at the head: tst1. Say what stands "
        "and why (a decision), and do not flip. To dispute the test that fails at "
        f"{back[:10]}, send msg.challenge_tester(refs=['c1', 'tst1'], "
        f"{sandbox.REASON_SLOT}) with quotes= copied from c1 and from tst1.")
    assert [(o.op, o.args["refs"]) for o in sb.ctx.offers] == [
        ("msg.challenge_tester", ["c1", "tst1"])]
    # Frame 200, pass 5, test 17: reason= is a slot that the seat fills.
    assert sb.ctx.offers[0].args["reason"] is api.INVENT
    # The follow check of frame 144, called here as well as by the conftest.
    exc = ValueError(said)
    got = sandbox.follow(sb, "code.commit", {"message": "back"}, exc, list(sb.ctx.offers))
    assert [r["second"] for r in got] == [None]


def test_the_facts_of_a_name_git_cannot_resolve_or_a_wrong_count_read_false(db, tmp_path):
    """The review of 9278be2, findings 3 and 4, and mutant m12."""
    root = tmp_path / "wt"
    back, head = _repo(root, "script.py", A, B)
    _tests(db, [("tst1", "c1"), ("tst2", None)])
    _runs(db, back, 1, {"tst1": "fail", "tst2": "pass"})
    _runs(db, head, 2, {"tst1": "pass", "tst2": "pass"})
    sb = _developer(db, root)
    runs = lambda value, at, sha: api.Fact("runs", value, (("at", at), ("sha", sha)))
    pair = (("back", back), ("head", head))
    got = sandbox.check_facts(sb, [
        runs({}, "HEAD~5", None),
        runs({"tst1": "fail", "tst2": "pass"}, "HEAD~1", "0" * 40),
        api.Fact("both", (2, 0, 1), pair),
        api.Fact("both", (2, 1, 1), pair),
        api.Fact("turns_red", ["tst1"], pair),
        api.Fact("turns_red", [], pair),
    ])
    assert [r["ok"] for r in got] == [False, False, True, False, True, False]
    assert "HEAD~5" in got[0]["why"]


def test_a_test_that_errors_at_the_tree_put_back_turns_red_too(db, tmp_path):
    """Mutant m5: `error` at `HEAD~1` counts as red, the same as `fail`.
    tst2 goes green, and tst1 goes from pass to `error`, so the door refuses."""
    root = tmp_path / "wt"
    back, head = _repo(root, "script.py", A, B)
    _tests(db, [("tst1", "c1"), ("tst2", None)])
    _runs(db, back, 1, {"tst1": "error", "tst2": "pass"})
    _runs(db, head, 2, {"tst1": "pass", "tst2": "fail"})
    sb = _developer(db, root)
    said = _refused(sb, "script.py", A)
    assert said == (
        f"{HEAD_SAID} The runs at the head {head[:10]}: 1 pass, 1 red, 0 error. "
        f"The runs at {back[:10]}, the tree this commit puts back: 1 pass, 0 red, 1 error. "
        f"Of the 2 tests that ran at both, the head fails 1 and {back[:10]} fails 1. "
        "Going back turns 1 test red that passes at the head: tst1. Change the code "
        "that the red tests call, then commit. Do not flip.")


def test_the_count_at_the_tree_put_back_reads_only_the_tests_at_both(db, tmp_path):
    """Mutant m9: tst2 is red at `HEAD~1` and has no run at the head. The
    count of the tests at both leaves tst2 out."""
    root = tmp_path / "wt"
    back, head = _repo(root, "script.py", A, B)
    _tests(db, [("tst1", "c1"), ("tst2", "c1")])
    _runs(db, back, 1, {"tst1": "fail", "tst2": "fail"})
    _runs(db, head, 2, {"tst1": "fail"})
    sb = _developer(db, root)
    sb.call("msg.escalate_architect", refs=["c1"])
    said = _refused(sb, "script.py", A)
    assert said == (
        f"{HEAD_SAID} The runs at the head {head[:10]}: 0 pass, 1 red, 0 error. "
        f"The runs at {back[:10]}, the tree this commit puts back: 0 pass, 2 red, 0 error. "
        f"Of the 1 test that ran at both, the head fails 1 and {back[:10]} fails 1. "
        "Going back makes no test pass that fails at the head. Change the code "
        "that the red tests call, then commit. Do not flip.")
    assert [f.value for f in sb.ctx.facts if f.kind == "both"] == [(1, 1, 1)]


def test_the_challenge_goes_to_the_first_red_test_that_its_doors_admit(db, tmp_path):
    """The review of 9278be2, finding 5. tst0's criterion is not of this
    batch, so the challenge door refuses tst0. The step names tst1."""
    body = ("from script import close_account\n\n\ndef test_close():\n"
            "    assert close_account('a1') == 2\n")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk9','i1','other')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c9','tk9','close returns 2')")
    root = tmp_path / "wt"
    back, head = _repo(root, "script.py", A, B)
    _tests(db, [("tst0", "c9"), ("tst1", "c1")], body=body)
    _runs(db, back, 1, {"tst0": "fail", "tst1": "fail"})
    _runs(db, head, 2, {"tst0": "pass", "tst1": "pass"})
    sb = _developer(db, root)
    said = _refused(sb, "script.py", A)
    assert said.endswith(
        f"To dispute the test that fails at {back[:10]}, send "
        f"msg.challenge_tester(refs=['c1', 'tst1'], {sandbox.REASON_SLOT}) with "
        "quotes= copied from c1 and from tst1.")
    assert [o.args["refs"] for o in sb.ctx.offers] == [["c1", "tst1"]]


# Frame 200, change 2: a landed challenge closes the write doors for that
# session. Night 139's s274 sent challenge m152, wrote that the test was
# wrong, and then changed the code to fit it.
DISPUTED = "def test_x():\n    assert close_account(1) == 3\n"
QUOTES = ("the criterion says 'prints the object as compact JSON' and the "
          "test asserts close_account(1) == 3")
# The Developer's reason of a challenge (frame 200, pass 5).
REASON = ("right code prints compact JSON, so the test must assert the "
          "printed object and not close_account")


def _challenged(db, tmp_path):
    root = tmp_path / "wt"
    _repo(root, "script.py", A)
    _tests(db, [("tst1", "c1")], body=DISPUTED)
    sb = _developer(db, root)
    return root, sb


def test_a_session_that_challenged_the_test_writes_and_commits_nothing(db, tmp_path):
    root, sb = _challenged(db, tmp_path)
    sb.call("msg.challenge_tester", reason=REASON, refs=["c1", "tst1"], quotes=QUOTES)
    mid = sb.ctx.outbound[-1]["id"]
    said = (f"you sent challenge to tester in this session ({mid}): you "
            f"challenged the test, and a change now builds on the disputed "
            f"test. {sandbox.END_STEP} Your whole next reply is this one "
            f"line, and no TOOL: line: Nothing more is owed on tst1 in this "
            f"session.")
    with pytest.raises(api.EndRefusal) as exc:
        sb.call("code.write", path="script.py", text=B)
    assert str(exc.value) == said
    assert (root / "script.py").read_bytes() == A.encode()
    with pytest.raises(api.EndRefusal) as exc:
        sb.call("code.commit", message="fit the test")
    assert str(exc.value) == said


def test_a_session_with_no_challenge_still_writes(db, tmp_path):
    root, sb = _challenged(db, tmp_path)
    sb.call("code.write", path="script.py", text=B)
    assert sb.call("code.commit", message="the change")["committed"] is True


def test_the_two_sandbox_steps_end_after_a_challenge(db, tmp_path):
    """The review of the design, section 2: `_code_step` and
    `_waits_refusal` asked for a change that the write doors now refuse."""
    _root, sb = _challenged(db, tmp_path)
    refs = ["c1", "tst1"]
    before = sandbox._waits_refusal("challenge", "tester", "m1", sb.ctx, refs)
    assert sandbox._code_step(sb.ctx) == ("Make one real change to the code "
                                          "the test calls.")
    assert not isinstance(before, sandbox._Ending)
    assert "write the change that makes it pass" in before
    sb.call("msg.challenge_tester", reason=REASON, refs=refs, quotes=QUOTES)
    after = sandbox._waits_refusal("challenge", "tester", "m1", sb.ctx, refs)
    assert sandbox._code_step(sb.ctx) == sandbox.END_STEP
    assert isinstance(after, sandbox._Ending)
    assert after == (
        "you sent challenge to tester on exactly these refs already (m1) and "
        "it waits for an answer. The answer comes to a later wake. "
        f"{sandbox.END_STEP} Your whole next reply is this one line, and no "
        "TOOL: line: Nothing more is owed on tst1 in this session.")


def test_the_empty_commit_note_after_a_message_names_the_end_alone(db, tmp_path):
    """s274 turn 11 read "the change comes first: code.write, then commit"
    after its message, and turn 12 wrote the change."""
    _root, sb = _challenged(db, tmp_path)
    note = sb.call("code.commit", message="nothing")["note"]
    assert note.endswith("the change comes first: code.write, then commit")
    sb.call("msg.escalate_architect", refs=["c1"])
    out = sb.call("code.commit", message="nothing")
    assert out["committed"] is False
    assert out["note"] == ("the tree is exactly as you found it. You have "
                           "sent your message: end the session")


def test_a_scope_question_keeps_the_note_that_names_the_change(db, tmp_path):
    """`batch_start.md` says a scope question never ends the session, so the
    note keeps its branch toward the change (the review of 2e6afd1c,
    finding 6)."""
    root = tmp_path / "wt"
    _repo(root, "script.py", A)
    _tests(db, [("tst1", "c1")])
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    sb.call("msg.question_vision_keeper", refs=["c1"],
            question="is the logging change in scope?")
    note = sb.call("code.commit", message="nothing")["note"]
    assert note.endswith("the change comes first: code.write, then commit")


def _prior_escalation(db, answer_refs: str) -> None:
    """An escalation on c1 and tst1 that the Architect answered."""
    seq = db.execute("SELECT coalesce(max(seq), 0) FROM messages").fetchone()[0]
    db.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, "
               "to_role, verb, body_refs, status, round_no, seq) VALUES "
               "('m900', 'm900', NULL, 'developer', 'architect', 'escalate', "
               "'[\"c1\", \"tst1\"]', 'answered', 0, ?)", (seq + 1,))
    db.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, "
               "to_role, verb, body_refs, status, round_no, seq) VALUES "
               "('m901', 'm900', 'm900', 'architect', 'developer', 'answer', "
               "?, 'answered', 0, ?)", (answer_refs, seq + 2))
    db.commit()


ENDS_ON_TST1 = (f"{sandbox.END_STEP} Your whole next reply is this one line, "
                "and no TOOL: line: Nothing more is owed on tst1 in this "
                "session.")


@pytest.mark.parametrize("answer_refs,fact", [
    ('["c1", "tst1", "d1"]', "the answer points at d1."),
    ('["c1", "tst1"]', "with no row beyond your own refs. Sending it again "
                       "is the same argument again."),
], ids=["answer-adds-a-row", "answer-adds-none"])
def test_an_escalation_after_a_challenge_ends_on_the_end_step(
        db, tmp_path, answer_refs, fact):
    """The escalation door told the seat to write, and the write door then
    refused (the review of 2e6afd1c, finding 3, `test_p5_escalate.py`)."""
    _root, sb = _challenged(db, tmp_path)
    _prior_escalation(db, answer_refs)
    before = sandbox._same_refs_refusal(sb.ctx, "architect", "escalate",
                                        ["c1", "tst1"])
    assert not isinstance(before, sandbox._Ending)
    sb.call("msg.challenge_tester", reason=REASON, refs=["c1", "tst1"], quotes=QUOTES)
    with pytest.raises(api.EndRefusal) as exc:
        sb.call("msg.escalate_architect", refs=["c1", "tst1"])
    said = str(exc.value)
    assert said.startswith("you sent escalate to architect on exactly these "
                           "refs already (m900) and they answered")
    assert said.endswith(f"{fact} {ENDS_ON_TST1}")
    assert "code.source" not in said and "change" not in said
