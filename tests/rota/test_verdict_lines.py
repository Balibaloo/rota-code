"""
Frame 170: a pass names an added line of the diff for each criterion.

Ruled by Roman, 2026-10-07 08:57: the Critic writes, for each criterion, the
line of the change that meets it, before it signs, and the door refuses a
pass that leaves a criterion unnamed. The design is
`plans/frame170-design.md`. Every test calls the real door through the
sandbox.

Night 127's bg_3 (s279) is the worked case. Its batch merged a `NameError`,
because `sys` is not imported outside the hunks. A pass with three true lines
still lands here, which is the gap the door cannot see.
"""
from __future__ import annotations

import json
import subprocess

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.core.worktrees import GIT
from rota.llm import toolproto
from rota.testkit.gitfixture import copy_template

CR1 = "cr_1_version_option_show_python_flag"
CR2 = "cr_2_version_option_show_python_false"
CR3 = "cr_3_version_option_show_python_true"
S279_IDS = (CR1, CR2, CR3)

# The batch's added lines, verbatim from s279's first prompt.
L_FLAG = "    show_python: bool = False,"
L_NOTE = "        # Append Python version if show_python is True"
L_VERSION = '        python_version = sys.version.split()[0] if show_python else ""'
L_MESSAGE = ('            message % {"prog": prog_name, "package": package_name, '
             '"version": version} + (f" ({python_version})" if python_version else ""),')

_BEFORE = (
    "import typing as t\n"
    "\n"
    "\n"
    "def version_option(\n"
    "    version: str | None = None,\n"
    "    *param_decls: str,\n"
    "    package_name: str | None = None,\n"
    "    prog_name: str | None = None,\n"
    "    message: str | None = None,\n"
    "{flag}"
    "    **kwargs: t.Any,\n"
    ") -> t.Callable[[FC], FC]:\n"
    "    def callback(ctx, param, value):\n"
    "        if not value or ctx.resilient_parsing:\n"
    "            return\n"
    "{version}"
    "        echo(\n"
    "{message}"
    "            color=ctx.color,\n"
    "        )\n"
    "        ctx.exit()\n"
)
OLD_MESSAGE = ('            message % {"prog": prog_name, "package": package_name, '
               '"version": version},\n')

# The TOOL: line of the design, section 1.
S279_CALL = (
    "TOOL: verdicts.emit(batch_id='bg_3', result='pass', lines={"
    f"'{CR1}': 'show_python: bool = False,', "
    f"'{CR2}': "
    "'message % {\"prog\": prog_name, \"package\": package_name, \"version\": version} "
    "+ (f\" ({python_version})\" if python_version else \"\"),', "
    f"'{CR3}': "
    "'python_version = sys.version.split()[0] if show_python else \"\"'})"
)
S279_LINES = {
    CR1: "show_python: bool = False,",
    CR2: L_MESSAGE.strip(),
    CR3: L_VERSION.strip(),
}


def _git(path, *args) -> str:
    return subprocess.run([*GIT, "-C", str(path), *args], check=True,
                          capture_output=True, text=True).stdout


def a_batch_repo(root, added: str) -> str:
    """A repository whose last commit adds the line `added` to `work.py`. A
    scripted pass in another test names `added` as its criterion's line."""
    repo = root / "batch_repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    (repo / "work.py").write_bytes(b"")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    (repo / "work.py").write_bytes((added + "\n").encode())
    _git(repo, "commit", "-q", "-am", "the batch")
    return str(repo)


def _seed(conn, batch_id: str, ids, *, worktree=None, head="abc123"):
    """A batch with one ticket whose criteria are `ids`."""
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1','the item','in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','i1','the ticket')")
    for cid in ids:
        conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                     "(?, 'tk1', ?)", (cid, f"the words of {cid}"))
    conn.execute("INSERT INTO batches (id, item_id, status, worktree, "
                 "head_commit) VALUES (?, 'i1', 'running', ?, ?)",
                 (batch_id, worktree, head))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "(?, 'tk1')", (batch_id,))
    conn.commit()


def _s279_repo(base) -> str:
    """Build s279's repository at `base / "repo"`, and return its head."""
    repo = base / "repo"
    path = repo / "src" / "click" / "decorators.py"
    path.parent.mkdir(parents=True)
    _git(base, "init", "-q", str(repo))
    path.write_bytes(_BEFORE.format(flag="", version="",
                                    message=OLD_MESSAGE).encode())
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "click")
    path.write_bytes(_BEFORE.format(
        flag=L_FLAG + "\n", version=L_NOTE + "\n" + L_VERSION + "\n",
        message=L_MESSAGE + "\n").encode())
    _git(repo, "commit", "-q", "-am", "show python")
    return _git(repo, "rev-parse", "HEAD").strip()


@pytest.fixture
def s279(tmp_path):
    """Night 127's bg_3: a repository whose one batch commit adds the four
    added lines of s279's diff to `src/click/decorators.py`."""
    # A copy of a repository built once per process. The git calls per test
    # cost this file 36.9s against 22.0s (frame 203's count, 2026-10-11).
    head = copy_template("s279", _s279_repo, tmp_path)
    conn = init_db(tmp_path / "rota.db")
    _seed(conn, "bg_3", S279_IDS, worktree=str(tmp_path / "repo"), head=head)
    return conn


def _critic(conn, batch_id="bg_3", mode="review"):
    return build("critic", conn, batch_id=batch_id, mode=mode)


def _land(sb, name: str = "verdicts.emit", **kwargs):
    """Send a pass twice, as a seat does on a night. Frame 201, pass 3: the
    first pass of a session is held, and the same pass sent again lands."""
    with pytest.raises(ValueError, match="before the pass lands, answer for"):
        sb.call(name, **kwargs)
    assert not [w for w in sb.ctx.writes if w[0] == "verdicts"]
    return sb.call(name, **kwargs)


def _refused(sb, **kwargs) -> str:
    with pytest.raises(ValueError) as exc:
        sb.call("verdicts.emit", **kwargs)
    assert not [w for w in sb.ctx.writes if w[0] == "verdicts"], \
        "a refused pass stages no verdict"
    return str(exc.value)


def _unnamed(missing, ids) -> str:
    verb = "has" if len(missing) == 1 else "have"
    return (
        f"a pass names, for each criterion, the added line of the diff that "
        f"meets it, and {', '.join(missing)} {verb} no line. Send verdicts.emit "
        f"again with lines={{'<criterion id>': '<the line>'}} for each of "
        f"{', '.join(ids)}, each line copied from a line of the [diff] block "
        f"that starts with +. If no added line meets {missing[0]}, that is a "
        f"fail on it: `verdicts.claim_encodes({missing[0]!r}, encodes=...)` "
        f"first, as for any fail")


def test_s279_pass_with_a_line_per_criterion_lands(s279):
    sb = _critic(s279)
    head = s279.execute("SELECT head_commit FROM batches").fetchone()[0]
    out = _land(sb, batch_id="bg_3", result="pass", lines=dict(S279_LINES))
    assert out == {"id": f"critic:bg_3:{head}", "result": "pass"}
    (_, _, row), = [w for w in sb.ctx.writes if w[0] == "verdicts"]
    assert json.loads(row["lines"]) == S279_LINES


def test_s279_pass_with_cr_3_unnamed_is_refused(s279):
    lines = {k: v for k, v in S279_LINES.items() if k != CR3}
    said = _refused(_critic(s279), batch_id="bg_3", result="pass", lines=lines)
    assert said == (
        "a pass names, for each criterion, the added line of the diff that "
        "meets it, and cr_3_version_option_show_python_true has no line. Send "
        "verdicts.emit again with lines={'<criterion id>': '<the line>'} for "
        "each of cr_1_version_option_show_python_flag, "
        "cr_2_version_option_show_python_false, "
        "cr_3_version_option_show_python_true, each line copied from a line of "
        "the [diff] block that starts with +. If no added line meets "
        "cr_3_version_option_show_python_true, that is a fail on it: "
        "`verdicts.claim_encodes('cr_3_version_option_show_python_true', "
        "encodes=...)` first, as for any fail")


def test_s279_pass_with_a_line_the_diff_does_not_add_is_refused(s279):
    said = _refused(_critic(s279), batch_id="bg_3", result="pass",
                    lines={**S279_LINES, CR3: "import sys"})
    assert said == (
        "the line for cr_3_version_option_show_python_true, 'import sys', is "
        "not an added line of the diff of batch bg_3. Copy one line of the "
        "[diff] block that starts with +, without the +, and send the pass "
        "again. The added lines of code are "
        + ", ".join(repr(ln.strip()) for ln in (L_FLAG, L_VERSION, L_MESSAGE))
        + ". If no added line meets cr_3_version_option_show_python_true, "
        "that is a fail on it: "
        "`verdicts.claim_encodes('cr_3_version_option_show_python_true', "
        "encodes=...)` first, as for any fail")


def test_a_near_line_is_named(s279):
    """Name the set, do not merely reject the guess: a line close to an
    added line gets that line back."""
    said = _refused(_critic(s279), batch_id="bg_3", result="pass",
                    lines={**S279_LINES, CR1: "show_python: bool = True,"})
    assert ("The added line nearest to it: 'show_python: bool = False,'. "
            "If no added line meets cr_1_version_option_show_python_flag") in said


def test_s279_pass_with_an_unknown_key_is_refused(s279):
    said = _refused(_critic(s279), batch_id="bg_3", result="pass",
                    lines={**S279_LINES, "cr_4": "show_python: bool = False,"})
    assert said == (
        "'cr_4' is not a criterion of batch bg_3. Its criteria are "
        "cr_1_version_option_show_python_flag, "
        "cr_2_version_option_show_python_false, "
        "cr_3_version_option_show_python_true. Send the pass again with "
        "lines= naming each of them once")


def test_lines_as_text_is_refused_with_the_shape(s279):
    said = _refused(_critic(s279), batch_id="bg_3", result="pass",
                    lines="show_python: bool = False,")
    assert said == (
        "lines= maps each criterion id to its line, as lines={'<criterion "
        "id>': '<the line>', '<criterion id>': '<the line>'}, one entry for "
        "each of cr_1_version_option_show_python_flag, "
        "cr_2_version_option_show_python_false, "
        "cr_3_version_option_show_python_true")


@pytest.mark.parametrize("value", [
    "+    show_python: bool = False,",
    "show_python: bool",
    ["show_python: bool = False,", L_NOTE.strip()],
    "show_python: bool = False,\n" + L_NOTE.strip() + "\n",
], ids=["plus", "part", "list", "breaks"])
def test_the_tolerated_shapes_land(s279, value):
    """A leading +, a part of 12 characters or more, a list of lines and
    lines split by breaks each have one reading."""
    out = _land(_critic(s279), batch_id="bg_3", result="pass",
                lines={**S279_LINES, CR1: value})
    assert out["result"] == "pass"


def test_a_short_part_is_not_a_line(s279):
    """`else ""),` is in an added line, and it is under 12 characters."""
    said = _refused(_critic(s279), batch_id="bg_3", result="pass",
                    lines={**S279_LINES, CR2: 'else ""),'})
    assert said.startswith("the line for cr_2_version_option_show_python_false, "
                           "'else \"\"),', is not an added line")


def test_a_context_line_is_not_an_added_line(s279):
    said = _refused(_critic(s279), batch_id="bg_3", result="pass",
                    lines={**S279_LINES, CR1: "message: str | None = None,"})
    assert said.startswith("the line for cr_1_version_option_show_python_flag")


# The code lines of s279's diff, as a refusal lists them. The comment line
# does nothing, so the list leaves it out.
_S279_CODE = ("The added lines of code are "
              + ", ".join(repr(ln.strip()) for ln in (L_FLAG, L_VERSION, L_MESSAGE))
              + ". ")


def _s279_sent(*held) -> str:
    """The block refusal names the seat's own code lines first (frame 201's
    review 1, finding 2). Two or more lines get their own sentence (review
    2, finding 5)."""
    shown = ", ".join(repr(ln.strip()) for ln in held)
    if len(held) == 1:
        return f"One of the lines you sent is the line: {shown}. Copy that one. "
    return (f"The lines you sent hold these added lines: {shown}. Copy the "
            f"one that does what the criterion says. ")


def test_a_block_for_every_criterion_is_refused(s279):
    """Frame 170's review of 845e0b80: a 4-line dump given for all three
    criteria landed, so the lines named nothing."""
    block = "\n".join(ln.strip() for ln in (L_FLAG, L_NOTE, L_VERSION, L_MESSAGE))
    said = _refused(_critic(s279), batch_id="bg_3", result="pass",
                    lines={cid: block for cid in S279_IDS})
    # Frame 201: the refusal names the added code lines, then the fail route.
    assert said == (
        "the value for cr_1_version_option_show_python_flag holds 4 lines, and "
        "a pass names one added line per criterion. Copy the one line of the "
        "[diff] block that meets cr_1_version_option_show_python_flag, without "
        "the +, and send the pass again. " + _s279_sent(L_FLAG, L_VERSION,
                                                        L_MESSAGE)
        + _S279_CODE + "If no added line "
        "meets cr_1_version_option_show_python_flag, that is a fail on it: "
        "`verdicts.claim_encodes('cr_1_version_option_show_python_flag', "
        "encodes=...)` first, as for any fail")


def test_a_value_of_two_lines_lands(s279):
    """A statement that wraps is two lines, and the door admits two."""
    two = L_NOTE.strip() + "\n" + L_VERSION.strip()
    out = _land(_critic(s279), batch_id="bg_3", result="pass",
                lines={**S279_LINES, CR3: two})
    assert out["result"] == "pass"


def test_a_value_of_three_lines_is_refused(s279):
    """The limit is two lines. A third line is refused."""
    three = "\n".join(ln.strip() for ln in (L_NOTE, L_VERSION, L_FLAG))
    said = _refused(_critic(s279), batch_id="bg_3", result="pass",
                    lines={**S279_LINES, CR3: three})
    # Frame 201: a comment among code lines keeps the block sentence.
    assert said == (
        f"the value for {CR3} holds 3 lines, and a pass names one added line "
        f"per criterion. Copy the one line of the [diff] block that meets "
        f"{CR3}, without the +, and send the pass again. "
        f"{_s279_sent(L_VERSION, L_FLAG)}{_S279_CODE}If no "
        f"added line meets {CR3}, that is a fail on it: "
        f"`verdicts.claim_encodes({CR3!r}, encodes=...)` first, as for any "
        f"fail")


def test_an_empty_line_is_no_line(s279):
    said = _refused(_critic(s279), batch_id="bg_3", result="pass",
                    lines={**S279_LINES, CR3: ""})
    assert said == _unnamed([CR3], S279_IDS)


def test_the_door_reads_the_diff_from_the_fork(tmp_path):
    """A batch of two commits: the line of the first commit is in the diff
    from the fork and not in the diff from HEAD~1. The door admits it."""
    root = tmp_path / "root"
    root.mkdir()
    _git(root, "init", "-q")
    (root / "work.py").write_bytes(b"")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    tree = tmp_path / "batch"
    _git(root, "worktree", "add", "-q", "-b", "batch/bg_3", str(tree))
    first = "def first_commit_line(): return 1"
    second = "def second_commit_line(): return 2"
    (tree / "work.py").write_bytes((first + "\n").encode())
    _git(tree, "commit", "-q", "-am", "one")
    (tree / "work.py").write_bytes((first + "\n" + second + "\n").encode())
    _git(tree, "commit", "-q", "-am", "two")
    from rota.roles.api import _added_lines
    assert first not in _added_lines(_git(tree, "diff", "HEAD~1", "HEAD")), \
        "the first commit's line is only context from HEAD~1"
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)",
                 (str(root),))
    _seed(conn, "bg_3", S279_IDS, worktree=str(tree))
    out = _land(_critic(conn), batch_id="bg_3", result="pass",
                lines={CR1: first, CR2: second, CR3: second})
    assert out["result"] == "pass"


PASS_NOTE = ("NOTE verdicts.emit(result='pass') has been refused the same way "
             "in two turns. It lands with lines={'<criterion id>': '<the added "
             "line>'} for each criterion, or as a fail after "
             "verdicts.claim_encodes on the criterion it fails")


def _critic_session(conn, calls):
    from rota.core.predicates import Wake
    from rota.core.runner import run_session
    from rota.llm.llm import Pins, ScriptedBackend

    backend = ScriptedBackend(calls + ["Done."])
    outcome = run_session(conn, Wake("critic", "tick:review", refs=("bg_3",)),
                          backend=backend, pins=Pins(model="scripted"),
                          batch_id="bg_3")
    return outcome, backend


def test_the_second_refusal_of_a_pass_names_the_routes_that_land(s279):
    """Frame 170's reviews of 845e0b80 and a4cb5cfa: the general note says
    the op will not be accepted again, and a verdict still lands by two
    routes. The note comes on the second refusal. The fourth turn ends the
    session as for any op."""
    calls = [f"TOOL: verdicts.emit(batch_id='bg_3', result='pass', reason='turn {k}')"
             for k in range(6)]
    outcome, backend = _critic_session(s279, calls)
    assert outcome.iterations == 4, outcome.iterations
    assert any("refused the same way in four turns" in e for e in outcome.errors)
    assert PASS_NOTE not in backend.calls[1][1]
    assert PASS_NOTE in backend.calls[2][1]
    assert all("will not be accepted again" not in c[1] for c in backend.calls)


def test_a_seat_that_repeats_itself_reads_the_note_before_the_stop(s279):
    """Byte-identical turns meet the verbatim stop at turn 3, before a third
    refusal. The note on the second refusal reaches the seat first."""
    call = "TOOL: verdicts.emit(batch_id='bg_3', result='pass')"
    outcome, backend = _critic_session(s279, [call] * 6)
    assert any("repeated its previous turn verbatim" in e for e in outcome.errors)
    assert PASS_NOTE in backend.calls[2][1]


def test_a_landed_pass_sent_again_gets_the_general_note(s279):
    """Night 120's s148 and night 128's s142 and s195 sent a landed pass
    again. The pass note would name routes that cannot land, so the refusal
    "already landed" gets the general note."""
    lines = repr(dict(S279_LINES))
    calls = [f"TOOL: verdicts.emit(batch_id='bg_3', result='pass', "
             f"reason='turn {k}', lines={lines})" for k in range(6)]
    outcome, backend = _critic_session(s279, calls)
    prompts = [c[1] for c in backend.calls]
    assert any("already landed" in p for p in prompts)
    assert all("It lands with lines=" not in p for p in prompts)
    assert any("NOTE verdicts.emit has been refused the same way in three "
               "turns and will not be accepted again" in p for p in prompts)


def test_a_refused_fail_gets_the_general_note(s279):
    """A fail refused for want of a claim is not a pass: the note of a pass
    would name the wrong routes."""
    calls = [f"TOOL: verdicts.emit(batch_id='bg_3', result='fail', "
             f"failed_criterion='{CR3}', reason='turn {k}')" for k in range(6)]
    outcome, backend = _critic_session(s279, calls)
    assert all("result='pass'" not in c[1] for c in backend.calls)
    assert ("NOTE verdicts.emit has been refused the same way in three turns "
            "and will not be accepted again") in backend.calls[3][1]


def test_fail_ignores_lines(s279):
    sb = _critic(s279)
    sb.call("verdicts.claim_encodes", criterion_id=CR3, encodes=True)
    out = sb.call("verdicts.emit", batch_id="bg_3", result="fail",
                  failed_criterion=CR3, lines={"x": "y"})
    assert out["result"] == "fail"
    (_, _, row), = [w for w in sb.ctx.writes if w[0] == "verdicts"]
    assert "lines" not in row


def test_a_batch_with_no_criteria_passes_with_no_lines(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    _seed(conn, "b1", ())
    out = _critic(conn, "b1").call("verdicts.emit", batch_id="b1", result="pass")
    assert out["result"] == "pass"


def test_the_lines_column_is_stored(s279):
    """The pipeline stores the JSON text in `verdicts.lines`."""
    cols = [r[1] for r in s279.execute("PRAGMA table_info(verdicts)")]
    assert "lines" in cols


def test_an_older_database_gains_the_lines_column(tmp_path):
    import sqlite3
    path = tmp_path / "old.db"
    init_db(path).close()
    old = sqlite3.connect(path)
    old.execute("ALTER TABLE verdicts DROP COLUMN lines")
    old.commit()
    old.close()
    conn = init_db(path)
    assert "lines" in [r[1] for r in conn.execute("PRAGMA table_info(verdicts)")]


def test_the_night_report_counts_the_named_criteria(tmp_path):
    from rota.tools import nightreport
    conn = init_db(tmp_path / "rota.db")
    _seed(conn, "bg_3", S279_IDS)
    conn.execute("INSERT INTO verdicts (id, batch_id, commit_sha, result, "
                 "lines) VALUES ('critic:bg_3:abc123', 'bg_3', 'abc123', "
                 "'pass', ?)", (json.dumps(S279_LINES),))
    conn.commit()
    report = nightreport.build(conn)
    (row,) = [ln for ln in report if ln.startswith("critic:bg_3:abc123")]
    assert " named=3 " in row


def test_the_parser_reads_lines_back():
    (call,) = toolproto.extract(S279_CALL)
    assert call.name == "verdicts.emit"
    assert call.args == {"batch_id": "bg_3", "result": "pass",
                         "lines": S279_LINES}


def test_the_parsed_call_lands(s279):
    (call,) = toolproto.extract(S279_CALL)
    out = _land(_critic(s279), call.name, **call.args)
    assert out["result"] == "pass"


def test_the_hints_name_lines():
    from rota.core.sandbox import ARG_HINTS_BY_OP
    hints = ARG_HINTS_BY_OP[("verdicts", "emit")]
    assert set(hints) == {"line", "quotes"}
    assert all("lines={'<criterion id>': '<the line>'}" in h for h in hints.values())


# The ten recorded passes of nights 114 to 128, verbatim from
# `plans/frame170-merges-read.md`, section 1, with each batch's criteria from
# the night's database (observed: `.rota/clickI_night<n>.db`, 2026-10-07).
_ECHO3 = ("echo_json_compact", "echo_json_compact_2", "echo_json_compact_3")
RECORDED = [
    ("114-s202", "review", "bg_2", ("cr_1", "cr_2", "cr_3"),
     "verdicts.emit(batch_id='bg_2', result='pass', failed_criterion=None, "
     "reason='', diff_ref='')"),
    ("116-s149", "answer", "bg_1", _ECHO3,
     "verdicts.emit(batch_id='bg_1', result='pass', failed_criterion=None, "
     "reason='', diff_ref='src/click/utils.py')"),
    ("118-s144", "review", "echo_json_group",
     _ECHO3 + ("echo_json_compact_4", "echo_json_compact_5", "echo_json_compact_6"),
     "verdicts.emit(batch_id='echo_json_group', result='pass', reason='', "
     "diff_ref='')"),
    ("119-s218", "review", "bg_2", ("cr_1", "cr_2", "cr_3", "cr_4"),
     "verdicts.emit(batch_id='bg_2', result='pass', reason='', diff_ref='')"),
    ("120-s148", "answer", "bg_1", _ECHO3,
     "verdicts.emit(batch_id='bg_1', result='pass', failed_criterion=None, "
     "reason='', diff_ref='src/click/utils.py')"),
    ("120-s180", "review", "bg_2",
     ("cr_1_confirm_eof_default", "cr_2_confirm_eof_state",
      "cr_3_confirm_eof_default_map"),
     "verdicts.emit(batch_id='bg_2', result='pass', reason='', diff_ref='')"),
    ("126-s225", "review", "bg_2", ("cr_1", "cr_2"),
     "verdicts.emit(batch_id='bg_2', result='pass', reason='', diff_ref='')"),
    ("127-s279", "review", "bg_3", S279_IDS,
     "verdicts.emit(batch_id='bg_3', result='pass', reason='', diff_ref='')"),
    ("128-s142", "review", "bg_1", _ECHO3,
     "verdicts.emit(batch_id='bg_1', result='pass', reason='', diff_ref='')"),
    ("128-s195", "review", "bg_2",
     ("cr_1_confirm_eof_default", "cr_2_confirm_eof_default_false",
      "cr_3_confirm_eof_default_value_type"),
     "verdicts.emit(batch_id='bg_2', result='pass', failed_criterion=None, "
     "reason='', diff_ref='')"),
]


@pytest.mark.parametrize("name,mode,batch_id,ids,text", RECORDED,
                         ids=[r[0] for r in RECORDED])
def test_ten_recorded_passes_are_refused(tmp_path, name, mode, batch_id, ids, text):
    """Each recorded pass names no line, so each names all of its batch's
    criteria as unnamed. Check 1 reads no diff, so no worktree is needed."""
    conn = init_db(tmp_path / "rota.db")
    _seed(conn, batch_id, ids)
    (call,) = toolproto.extract("TOOL: " + text)
    sb = _critic(conn, batch_id, mode)
    said = _refused(sb, **call.args)
    assert said == _unnamed(list(ids), ids)


# Frame 180: a line with no behaviour meets no criterion. Night 130's s134
# named `import json` for the criterion that asks for a TypeError.

def _no_behaviour(cid, quote, kind, code=()) -> str:
    """The refusal of a line with no behaviour. `code` holds the diff's
    code lines, which the refusal lists before the fail route (frame 201)."""
    listed = ("The added lines of code are "
              + ", ".join(repr(c) for c in code) + ". ") if code else ""
    if kind in ("a docstring line", "a comment"):
        why = (f"A docstring or comment line counts only for a criterion "
               f"that asks for documentation, and {cid} asks for behaviour.")
    else:
        why = (f"{kind[0].upper()}{kind[1:]} does nothing that a criterion "
               f"asks for.")
    return (
        f"the line for {cid}, {quote!r}, is {kind}. {why} "
        f"Copy the added line that does what "
        f"{cid} says, without the +, and send the pass again. {listed}If no "
        f"added line meets {cid}, that is a fail on it: "
        f"`verdicts.claim_encodes({cid!r}, encodes=...)` first, as for any "
        f"fail")


def _repo_of(tmp_path, rel, before: str, after: str) -> tuple[str, str]:
    """A repository whose one batch commit turns `before` into `after` in
    the file `rel`. Returns the path and the head commit."""
    # A copy of the repository built once per process for these three values,
    # as `s279` copies its own (frame 203).
    head = copy_template(("repo_of", rel, before, after),
                         lambda base: _build_repo_of(base, rel, before, after),
                         tmp_path)
    return str(tmp_path / "repo"), head


def _build_repo_of(base, rel, before: str, after: str) -> str:
    """Build `_repo_of`'s repository at `base / "repo"`, and return its
    head."""
    repo = base / "repo"
    path = repo / rel
    path.parent.mkdir(parents=True)
    _git(base, "init", "-q", str(repo))
    path.write_bytes(before.encode())
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    path.write_bytes(after.encode())
    _git(repo, "commit", "-q", "-am", "the batch")
    return _git(repo, "rev-parse", "HEAD").strip()


S134_IDS = ("echo_json_compact", "echo_json_compact_2", "echo_json_compact_3")
# s134's call on night 130, verbatim from the `turns` table of
# `.rota/clickI_night130.db`, turn 1.
S134_CALL = r"""TOOL: verdicts.emit(batch_id='bg_1', result='pass', failed_criterion=None, reason='', diff_ref='', lines={'echo_json_compact': '    out = json.dumps(obj, separators=(",", ":"))', 'echo_json_compact_2': '    file.write(out + "\\n")', 'echo_json_compact_3': '    import json'})"""
# The end of `src/click/utils.py` before bg_1, the hunk's context lines.
S134_BEFORE = (
    "def __getattr__(name: str) -> object:\n"
    "    if name in _deprecated:\n"
    '        return globals()[f"_{name}"]\n'
    "\n"
    "    raise AttributeError(name)\n"
)
# The 14 lines that commit 9a4bddfd adds, verbatim.
S134_ADDED = (
    "def echo_json(obj: object) -> None:\n"
    '    """Print an object as compact JSON to the stream.\n'
    "\n"
    "    .. versionadded:: 8.5\n"
    "\n"
    "    :param obj: The object to serialize and print.\n"
    '    """\n'
    "    import json\n"
    "\n"
    '    out = json.dumps(obj, separators=(",", ":"))\n'
    "    file = _default_text_stdout()\n"
    r'    file.write(out + "\n")' "\n"
    "    file.flush()\n"
    "\n"
)


@pytest.fixture
def s134(tmp_path):
    """Night 130's bg_1: the batch adds `echo_json` to `src/click/utils.py`."""
    repo, head = _repo_of(tmp_path, "src/click/utils.py", S134_BEFORE,
                          S134_BEFORE + S134_ADDED)
    conn = init_db(tmp_path / "rota.db")
    _seed(conn, "bg_1", S134_IDS, worktree=repo, head=head)
    return conn


# The code lines of S134_ADDED, as a refusal lists them.
S134_CODE = ["def echo_json(obj: object) -> None:",
             'out = json.dumps(obj, separators=(",", ":"))',
             "file = _default_text_stdout()",
             r'file.write(out + "\n")',
             "file.flush()"]


def test_s134_pass_naming_import_json_is_refused(s134):
    (call,) = toolproto.extract(S134_CALL)
    said = _refused(_critic(s134, "bg_1"), **call.args)
    assert said == _no_behaviour("echo_json_compact_3", "import json",
                                 "a plain import", S134_CODE)


def test_s134_pass_naming_the_dumps_line_lands(s134):
    """`json.dumps` raises the TypeError, so its line meets the criterion."""
    (call,) = toolproto.extract(S134_CALL)
    lines = {**call.args["lines"],
             "echo_json_compact_3": call.args["lines"]["echo_json_compact"]}
    out = _land(_critic(s134, "bg_1"), call.name,
                **{**call.args, "lines": lines})
    assert out["result"] == "pass"


KIND_ADDED = (
    "from x import y\n"
    "\n"
    "\n"
    "def work(a):\n"
    '    """Do the work.\n'
    "\n"
    "    The prose line of the docstring.\n"
    '    """\n'
    "    # the comment line of the work\n"
    "    total = a + 1\n"
    "    if a:\n"
    "        pass\n"
    "    ...\n"
    "    return total  # the sum of a and one\n"
)
# The code lines of KIND_ADDED, as a refusal lists them.
KIND_CODE = ["def work(a):", "total = a + 1", "if a:",
             "return total  # the sum of a and one"]


@pytest.fixture
def kinds(tmp_path):
    repo, head = _repo_of(tmp_path, "work.py", "", KIND_ADDED)
    conn = init_db(tmp_path / "rota.db")
    _seed(conn, "bg_1", ["cr_1"], worktree=repo, head=head)
    return conn


@pytest.mark.parametrize("value,quote,kind", [
    ("+", "+", "a blank line"),
    ("pass", "pass", "`pass`"),
    ("...", "...", "`...`"),
    ("# the comment line of the work", "# the comment line of the work",
     "a comment"),
    ("from x import y", "from x import y", "a plain import"),
    ('"""', '"""', "a docstring line"),
    ('"""Do the work.', '"""Do the work.', "a docstring line"),
    ("The prose line of the docstring.", "The prose line of the docstring.",
     "a docstring line"),
], ids=["blank", "pass", "ellipsis", "comment", "import", "fence", "opening",
        "prose"])
def test_a_line_with_no_behaviour_is_refused(kinds, value, quote, kind):
    said = _refused(_critic(kinds, "bg_1"), batch_id="bg_1", result="pass",
                    lines={"cr_1": value})
    assert said == _no_behaviour("cr_1", quote, kind, KIND_CODE)


@pytest.mark.parametrize("value", [
    "return total  # the sum of a and one",
    "total = a + 1",
    "if a:",
])
def test_a_line_that_does_something_lands(kinds, value):
    out = _land(_critic(kinds, "bg_1"), batch_id="bg_1", result="pass",
                lines={"cr_1": value})
    assert out["result"] == "pass"


def test_the_s279_comment_alone_is_refused(s279):
    """s279's diff adds a comment line. Named alone, it is refused."""
    said = _refused(_critic(s279), batch_id="bg_3", result="pass",
                    lines={**S279_LINES, CR3: L_NOTE.strip()})
    assert said == _no_behaviour(
        CR3, L_NOTE.strip(), "a comment",
        [ln.strip() for ln in (L_FLAG, L_VERSION, L_MESSAGE)])


# Frame 180, pass 2: the findings of the diff review of 7b25da26.

def _one_criterion(tmp_path, rel, before, after):
    repo, head = _repo_of(tmp_path, rel, before, after)
    conn = init_db(tmp_path / "rota.db")
    _seed(conn, "bg_1", ["cr_1"], worktree=repo, head=head)
    return conn


def _pass(conn, value):
    return _land(_critic(conn, "bg_1"), batch_id="bg_1", result="pass",
                 lines={"cr_1": value})


@pytest.mark.parametrize("rel,line", [
    ("src/click/utils.py", "from .utils import echo_json as echo_json"),
    ("src/click/__init__.py", "from .utils import echo_json"),
], ids=["alias", "init"])
def test_a_re_export_lands(tmp_path, rel, line):
    """G4: a re-export is the one line that meets "echo_json is available
    from click". An `as` alias or an `__init__.py` file marks it."""
    conn = _one_criterion(tmp_path, rel, "", line + "\n")
    assert _pass(conn, line)["result"] == "pass"


def test_a_line_not_in_the_diff_names_the_code_lines(s134):
    """s134's natural next value, `raise TypeError`, is not in the diff.
    The refusal lists the code lines the seat can name."""
    said = _refused(_critic(s134, "bg_1"), batch_id="bg_1", result="pass",
                    lines={"echo_json_compact": "out = json.dumps(obj",
                           "echo_json_compact_2": "file.flush()",
                           "echo_json_compact_3": "raise TypeError"})
    code = ["def echo_json(obj: object) -> None:",
            'out = json.dumps(obj, separators=(",", ":"))',
            "file = _default_text_stdout()",
            r'file.write(out + "\n")',
            "file.flush()"]
    assert ("is not an added line of the diff of batch bg_1. Copy one line "
            "of the [diff] block that starts with +, without the +, and send "
            "the pass again. The added lines of code are "
            + ", ".join(repr(c) for c in code) + ". If no added line") in said


@pytest.mark.parametrize("after,value", [
    # G1: a one-line header opens no body.
    ('class A(B): pass\nTABLE = {\n    "help":\n        """usage text\n'
     '        """.strip(),\n}\n', '""".strip(),'),
    # G2: a call on a string is not a docstring.
    ('def f():\n    """a""".join(x)\n    return 1\n', '"""a""".join(x)'),
    # G6: code after the closing fence.
    ('def f():\n    """doc\n    """; x = call()\n    y = 2\n',
     '"""; x = call()'),
    # G3: lines inside a string that is not a docstring.
    ('TEMPLATE = """\n# Title\nimport os\n"""\n', "import os"),
    ('TEMPLATE = """\n# Title\nimport os\n"""\n', "# Title"),
    # Mutant M10: a second statement after an import.
    ("import x; y()\n", "import x; y()"),
], ids=["G1", "G2", "G6", "G3-import", "G3-comment", "semicolon"])
def test_code_shapes_land(tmp_path, after, value):
    conn = _one_criterion(tmp_path, "work.py", "", after)
    assert _pass(conn, value)["result"] == "pass"


def test_a_docstring_opened_in_a_context_line_marks_its_lines(tmp_path):
    """Mutant M5: the opening fence is a context line of the hunk."""
    before = ('def work():\n    """The doc.\n    old prose.\n    """\n'
              "    return 1\n")
    after = before.replace('"""The doc.\n',
                           '"""The doc.\n    new prose of the doc.\n')
    conn = _one_criterion(tmp_path, "work.py", before, after)
    said = _refused(_critic(conn, "bg_1"), batch_id="bg_1", result="pass",
                    lines={"cr_1": "new prose of the doc."})
    assert said == _no_behaviour("cr_1", "new prose of the doc.",
                                 "a docstring line")


def test_a_docstring_left_open_ends_at_the_next_hunk():
    """Mutant M6: the first hunk opens a docstring and shows no close. The
    second hunk's code line is code."""
    from rota.roles.api import _added_kinds
    diff = "\n".join([
        "@@ -1,1 +1,3 @@", " def f():", '+    """Open doc.', "+    prose",
        "@@ -40,1 +42,2 @@", " x = 1", "+    total = compute(x)"])
    assert _added_kinds(diff) == [('"""Open doc.', "a docstring line"),
                                  ("prose", "a docstring line"),
                                  ("total = compute(x)", None)]


def test_a_header_over_two_lines_opens_a_docstring(tmp_path):
    """Mutant M7: the colon of the header is on its second line."""
    after = ('def work(\n    a,\n):\n    """Doc line one.\n\n'
             '    the prose of the doc.\n    """\n    return a\n')
    conn = _one_criterion(tmp_path, "work.py", "", after)
    said = _refused(_critic(conn, "bg_1"), batch_id="bg_1", result="pass",
                    lines={"cr_1": "the prose of the doc."})
    assert said == _no_behaviour("cr_1", "the prose of the doc.",
                                 "a docstring line",
                                 ["def work(", "a,", "):", "return a"])


# Frame 180, pass 3: the findings of the delta review of 6a2381f6.

# Run 1 of the re-recorded `L1-CR-finish-the-review-with-the-answer-in-hand`,
# verbatim from the worktree's `cassettes.db`, read-only. The seat quoted the
# criterion's text, took the fail route and failed a correct batch.
RUN1_CALL = ('TOOL: verdicts.emit(batch_id="b_0e7a52", result="pass", '
             'diff_ref="src/billing/prorate.py", '
             'lines={"c_78356e": "prorate(999, 1, 3) returns 333"})')
# The six code lines that run 1's refusal listed, in a module.
PRORATE = (
    "def prorate(cents, days_used, days_in_period):\n"
    "    if days_in_period <= 0:\n"
    '        raise ValueError("days_in_period must be positive")\n'
    "    if days_used <= 0:\n"
    "        return 0\n"
    "    return round(cents * days_used / days_in_period)\n"
)


def test_a_quoted_criterion_is_named_as_the_criterion_text(tmp_path):
    repo, head = _repo_of(tmp_path, "src/billing/prorate.py", "", PRORATE)
    conn = init_db(tmp_path / "rota.db")
    _seed(conn, "b_0e7a52", ["c_78356e"], worktree=repo, head=head)
    conn.execute("UPDATE criteria SET text = ? WHERE id = 'c_78356e'",
                 ("prorate(999, 1, 3) returns 333",))
    conn.commit()
    (call,) = toolproto.extract(RUN1_CALL)
    sb = _critic(conn, "b_0e7a52", "answer")
    said = _refused(sb, **call.args)
    code = [ln.strip() for ln in PRORATE.splitlines()]
    assert said == (
        "the line for c_78356e, 'prorate(999, 1, 3) returns 333': that is "
        "the criterion's text, not a line of the diff. Copy the added line "
        "that does what c_78356e says, without the +, and send the pass "
        "again. The added lines of code are "
        + ", ".join(repr(c) for c in code) + ". If no added line meets "
        "c_78356e, that is a fail on it: "
        "`verdicts.claim_encodes('c_78356e', encodes=...)` first, as for any "
        "fail")
    # The criterion's text is named before the fail route (frame 180, pass 4).
    assert said.index("the criterion's text") < said.index("claim_encodes")


def test_prose_shaped_as_a_header_opens_no_docstring():
    """N1b: the hunk starts inside a docstring. The prose line `class Foo
    is the base, see:` does not parse, so the bare fence after it opens no
    docstring over the code."""
    from rota.roles.api import _added_kinds
    q = '"""'
    diff = "\n".join(["@@ -10,6 +10,9 @@ def f(x):",
                      "+    class Foo is the base, see:", "+    " + q,
                      "+    y = x + 1", "+    return y"])
    kinds = dict(_added_kinds(diff))
    assert kinds["y = x + 1"] is None
    assert kinds["return y"] is None


def test_a_docstring_closed_by_a_fence_and_a_comma_is_a_docstring_line():
    """Mutant R2: a `,` after the closing fence holds no code."""
    from rota.roles.api import _added_kinds
    diff = "\n".join(["@@ -1 +1,4 @@", "+def f():", '+    """Doc.',
                      "+    prose", '+    """,'])
    assert _added_kinds(diff)[-1] == ('""",', "a docstring line")


def test_the_code_list_stops_at_eight(tmp_path):
    """Mutant R4: nine code lines list eight and the count of the rest."""
    body = "".join(f"value_{i} = compute({i})\n" for i in range(9))
    conn = _one_criterion(tmp_path, "work.py", "", body)
    said = _refused(_critic(conn, "bg_1"), batch_id="bg_1", result="pass",
                    lines={"cr_1": "zz"})
    assert "'value_7 = compute(7)', and 1 more. If no added line" in said
    assert "value_8" not in said


def test_the_block_refusal_lists_eight_code_lines(tmp_path):
    """The block refusal reads the same list, so it stops at the same eight."""
    body = "".join(f"value_{i} = compute({i})\n" for i in range(9))
    conn = _one_criterion(tmp_path, "work.py", "", body)
    block = "\n".join(f"value_{i} = compute({i})" for i in range(3))
    said = _refused(_critic(conn, "bg_1"), batch_id="bg_1", result="pass",
                    lines={"cr_1": block})
    assert said.startswith("the value for cr_1 holds 3 lines")
    assert "'value_7 = compute(7)', and 1 more. If no added line" in said
    assert "value_8" not in said


# Frame 201: night 157's W3. Three Critics named the docstring of bg_2 for
# crit_show_python_version, and the block refusal named no line of code.

BG2_IDS = ("crit_show_python_help", "crit_show_python_version",
           "crit_show_python_default")
BG2_HELP = ('    kwargs.setdefault("help", _("Show the version and exit." if not '
            'show_python else _("Show the version and exit. (appends the '
            'running Python version)")))\n')
BG2_DOC = (
    "    :param show_python: If True, append the running Python interpreter\n"
    "        version string (major.minor.micro from sys.version_info) to the\n"
    "        message. Defaults to False.\n")
BG2_CODE = (
    "    if show_python:\n"
    "        import sys\n"
    '        python_version = f"{sys.version_info.major}.'
    '{sys.version_info.minor}.{sys.version_info.micro}"\n'
    '        message = message + f" (Python {python_version})"\n')
# A short `version_option`. The nine added lines of bg_2 fall in one hunk
# with the docstring's opening fence, so the walk marks the docstring.
BG2_BEFORE = (
    "def version_option(\n"
    "    message: str | None = None,\n"
    "{flag}"
    "    **kwargs: t.Any,\n"
    ") -> t.Callable[[FC], FC]:\n"
    '    """Add a ``--version`` option.\n'
    "\n"
    "    :param message: The message to show.\n"
    "{doc}"
    '    """\n'
    "    if message is None:\n"
    '        message = _("%(prog)s, version %(version)s")\n'
    "{code}"
    "{help}"
    "    return option(**kwargs)\n"
)
BG2_OLD_HELP = '    kwargs.setdefault("help", _("Show the version and exit."))\n'
# s324's call on night 157, verbatim from the `turns` table of
# `.rota/clickI_night157.db`.
S324_CALL = r"""verdicts.emit(batch_id='bg_2', result='pass', reason='', lines={'crit_show_python_help': 'Show the version and exit. (appends the running Python version)', 'crit_show_python_version': 'If True, append the running Python interpreter\n    version string (major.minor.micro from sys.version_info) to\n    the message.', 'crit_show_python_default': 'Defaults to False.'})"""
# The code lines of bg_2's diff. `import sys` is a plain import, so the
# list leaves it out.
BG2_LISTED = ("The added lines of code are "
              + ", ".join(repr(ln.strip()) for ln in (
                  "    show_python: bool = False,",
                  *BG2_CODE.splitlines()[0:1], *BG2_CODE.splitlines()[2:],
                  BG2_HELP.rstrip("\n")))
              + ". ")


@pytest.fixture
def bg2(tmp_path):
    """Night 157's bg_2: the batch adds `show_python` to `version_option`."""
    before = BG2_BEFORE.format(flag="", doc="", code="", help=BG2_OLD_HELP)
    after = BG2_BEFORE.format(flag="    show_python: bool = False,\n",
                              doc=BG2_DOC, code=BG2_CODE, help=BG2_HELP)
    repo, head = _repo_of(tmp_path, "src/click/decorators.py", before, after)
    conn = init_db(tmp_path / "rota.db")
    _seed(conn, "bg_2", BG2_IDS, worktree=repo, head=head)
    return conn


def _bg2_fail_route(cid) -> str:
    return (f"If no added line meets {cid}, that is a fail on it: "
            f"`verdicts.claim_encodes({cid!r}, encodes=...)` first, as for "
            f"any fail")


def test_s324_docstring_block_names_the_code_lines(bg2):
    """s324 sent three docstring lines, and the old refusal named no code
    line. The refusal says that the lines are docstring lines, then lists
    the code lines, then the fail route."""
    (call,) = toolproto.extract("TOOL: " + S324_CALL)
    said = _refused(_critic(bg2, "bg_2"), **call.args)
    cid = "crit_show_python_version"
    assert said == (
        f"the value for {cid} holds 3 lines, and they are docstring lines. "
        f"A docstring or comment line counts only for a criterion that asks "
        f"for documentation, and {cid} asks for behaviour. A pass "
        f"names one added line per criterion. Copy the one added line of "
        f"code that does what {cid} says, without the +, and send the pass "
        f"again. " + BG2_LISTED + _bg2_fail_route(cid))
    assert "'show_python: bool = False,'" in said
    assert repr('message = message + f" (Python {python_version})"') in said
    assert said.endswith("first, as for any fail")


def test_s326_two_docstring_lines_name_the_code_lines(bg2):
    """The first two lines of s326's value are two docstring lines. The
    no-behaviour refusal lists the same code lines before the fail route."""
    cid = "crit_show_python_version"
    two = ("    :param show_python: If True, append the running Python "
           "interpreter\n        version string (major.minor.micro from "
           "sys.version_info) to the")
    said = _refused(_critic(bg2, "bg_2"), batch_id="bg_2", result="pass",
                    lines={"crit_show_python_help": BG2_HELP.strip(),
                           cid: two,
                           "crit_show_python_default":
                               "show_python: bool = False,"})
    quote = ":param show_python: If True, append the running Python interpreter"
    assert said == (
        f"the line for {cid}, {quote!r}, is a docstring line. A docstring or "
        f"comment line counts only for a criterion that asks for "
        f"documentation, and {cid} asks for behaviour. Copy the added line "
        f"that does what {cid} says, without the +, and send the pass again. "
        + BG2_LISTED + _bg2_fail_route(cid))


# Frame 201, pass 2: review 1's finding 1. The real hunk of night 157's bg_2
# starts inside the docstring of `version_option`, so the plain diff shows
# no opening fence. The fixture is the real file, so the shape is the
# night's shape.

CLICKI = "D:/repos/_AI/sample_repos/clickI"
# Night 157's fork of bg_2. Its `decorators.py` is the file at clickI's
# head on 2026-10-21. A pinned commit keeps the fixture still when a later
# night moves the head.
CLICKI_FORK = "2c8cd3ac958a7eb316d67f2d316c27086c4c0369"


def _clicki_decorators() -> str | None:
    out = subprocess.run([*GIT, "-C", CLICKI, "show",
                          f"{CLICKI_FORK}:src/click/decorators.py"],
                         capture_output=True)
    return out.stdout.decode() if out.returncode == 0 else None


REAL_BEFORE = _clicki_decorators()


def _once(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, old
    return text.replace(old, new)


def _real_bg2_after(before: str) -> str:
    """The nine added lines of bg_2, in the places night 157's diff put
    them, and the old help line removed. Each edit stays inside the
    function, because the file repeats some of its lines."""
    start = before.index("\ndef version_option(")
    end = before.index("\ndef ", start + 1)
    return before[:start] + _bg2_body(before[start:end]) + before[end:]


def _bg2_body(before: str) -> str:
    after = _once(before,"    message: str | None = None,\n"
                  "    **kwargs: t.Any,\n) -> t.Callable[[FC], FC]:\n"
                  '    """Add a ``--version`` option',
                  "    message: str | None = None,\n"
                  "    show_python: bool = False,\n"
                  "    **kwargs: t.Any,\n) -> t.Callable[[FC], FC]:\n"
                  '    """Add a ``--version`` option')
    after = _once(after, '        ``"%(prog)s, version %(version)s"``.\n',
                  '        ``"%(prog)s, version %(version)s"``.\n' + BG2_DOC)
    after = _once(after, '        message = _("%(prog)s, version %(version)s")\n'
                  "\n",
                  '        message = _("%(prog)s, version %(version)s")\n'
                  "\n" + BG2_CODE)
    tail = '\n    if not param_decls:\n        param_decls = ("--version",)\n'
    after = _once(after, "        ctx.exit()\n" + tail,
                  "        ctx.exit()\n" + BG2_HELP + tail)
    return _once(after, BG2_OLD_HELP, "")


needs_clicki = pytest.mark.skipif(
    REAL_BEFORE is None, reason=f"no {CLICKI} at {CLICKI_FORK[:8]}")


@pytest.fixture
def real_bg2(tmp_path):
    """Night 157's bg_2 on the real `decorators.py` of clickI."""
    repo, head = _repo_of(tmp_path, "src/click/decorators.py", REAL_BEFORE,
                          _real_bg2_after(REAL_BEFORE))
    conn = init_db(tmp_path / "rota.db")
    _seed(conn, "bg_2", BG2_IDS, worktree=repo, head=head)
    return conn


@needs_clicki
def test_the_real_hunk_starts_inside_the_docstring(real_bg2, tmp_path):
    """The plain diff has the night's shape: the hunk of the three
    `:param show_python:` lines shows no docstring fence."""
    from rota.core import worktrees as _wt
    plain = _wt.diff(tmp_path / "repo", "HEAD~1")
    hunks = plain.split("\n@@ ")
    (hunk,) = [h for h in hunks if "+    :param show_python:" in h]
    assert hunk.startswith("-461,6 +462,9 @@")
    assert '"""' not in hunk
    # The walk's diff opens the function, and the seat's diff is plain.
    whole = _wt.diff(tmp_path / "repo", "HEAD~1", function_context=True)
    assert "\n def version_option(\n" in whole
    from rota.roles.api import _added_kinds
    assert [a for a, _ in _added_kinds(whole)] == \
        [a for a, _ in _added_kinds(plain)]


@needs_clicki
def test_s324_on_the_real_diff_gets_the_docstring_text(real_bg2):
    """s324's exact call on the real diff: the three lines are docstring
    lines, the list holds no docstring line, then the fail route."""
    (call,) = toolproto.extract("TOOL: " + S324_CALL)
    said = _refused(_critic(real_bg2, "bg_2"), **call.args)
    cid = "crit_show_python_version"
    assert said == (
        f"the value for {cid} holds 3 lines, and they are docstring lines. "
        f"A docstring or comment line counts only for a criterion that asks "
        f"for documentation, and {cid} asks for behaviour. A pass "
        f"names one added line per criterion. Copy the one added line of "
        f"code that does what {cid} says, without the +, and send the pass "
        f"again. " + BG2_LISTED + _bg2_fail_route(cid))
    assert ":param show_python" not in said


@needs_clicki
def test_one_real_docstring_line_is_refused(real_bg2):
    """One docstring line alone lands no pass on the real diff."""
    cid = "crit_show_python_version"
    quote = ":param show_python: If True, append the running Python interpreter"
    said = _refused(_critic(real_bg2, "bg_2"), batch_id="bg_2", result="pass",
                    lines={"crit_show_python_help": BG2_HELP.strip(),
                           cid: quote,
                           "crit_show_python_default":
                               "show_python: bool = False,"})
    assert said == (
        f"the line for {cid}, {quote!r}, is a docstring line. A docstring or "
        f"comment line counts only for a criterion that asks for "
        f"documentation, and {cid} asks for behaviour. Copy the added line "
        f"that does what {cid} says, without the +, and send the pass again. "
        + BG2_LISTED + _bg2_fail_route(cid))


def test_the_block_text_names_the_held_code_lines_first(tmp_path):
    """Review 1's probe e1: forty code lines and a block of three. The
    capped list omits all three, so the text names them first."""
    body = "".join(f"value_{i} = compute({i})\n" for i in range(40))
    conn = _one_criterion(tmp_path, "work.py", "", body)
    block = "\n".join(f"value_{i} = compute({i})" for i in (10, 20, 30))
    said = _refused(_critic(conn, "bg_1"), batch_id="bg_1", result="pass",
                    lines={"cr_1": block})
    shown = ", ".join(repr(f"value_{i} = compute({i})") for i in range(8))
    assert said == (
        "the value for cr_1 holds 3 lines, and a pass names one added line "
        "per criterion. Copy the one line of the [diff] block that meets "
        "cr_1, without the +, and send the pass again. The lines you sent "
        "hold these added lines: 'value_10 = compute(10)', 'value_20 = "
        "compute(20)', 'value_30 = compute(30)'. Copy the one that does what "
        "the criterion says. The added "
        f"lines of code are {shown}, and 32 more. If no added line meets "
        "cr_1, that is a fail on it: `verdicts.claim_encodes('cr_1', "
        "encodes=...)` first, as for any fail")


# Frame 201, pass 2b: review 2. The walk's diff opens each hunk at a `def`
# or a `class` in column 0, and the header goes on while its brackets are
# open.

def _clicki_file(rel: str) -> str | None:
    out = subprocess.run([*GIT, "-C", CLICKI, "show", f"{CLICKI_FORK}:{rel}"],
                         capture_output=True)
    return out.stdout.decode() if out.returncode == 0 else None


REAL_CORE = _clicki_file("src/click/core.py")
STRICT_DOC = ("    :param strict: if set to `True`, a missing object raises\n"
              "                   an error.\n")


def _walk_of(tmp_path, rel, before, after):
    """The plain diff and the walk's diff of one batch commit."""
    from rota.core import worktrees as _wt
    repo, _ = _repo_of(tmp_path, rel, before, after)
    return (_wt.diff(repo, "HEAD~1"),
            _wt.diff(repo, "HEAD~1", function_context=True))


def _hunk_of(diff_text: str, added: str) -> list[str]:
    """The lines of the hunk that adds `added`, from its `@@` line."""
    hunk: list[str] = []
    for ln in diff_text.splitlines():
        if ln.startswith("@@"):
            hunk = []
        hunk.append(ln)
        if ln == "+" + added:
            return hunk
    raise AssertionError(f"no hunk adds {added!r}")


@needs_clicki
def test_an_example_def_in_a_docstring_opens_no_hunk(tmp_path):
    """Review 2, finding 1, probe p4: the docstring of `make_pass_decorator`
    holds an example `def decorator(f):`. The walk's hunk must not open
    there."""
    old = ("    :param ensure: if set to `True`, a new object will be created and\n"
           "                   remembered on the context if it's not there yet.\n")
    after = _once(REAL_BEFORE, old, old + STRICT_DOC)
    plain, whole = _walk_of(tmp_path, "src/click/decorators.py",
                            REAL_BEFORE, after)
    hunk = _hunk_of(whole, STRICT_DOC.splitlines()[0])
    assert hunk[1] == " def make_pass_decorator("
    from rota.roles.api import _added_kinds
    assert _added_kinds(whole) == [
        (ln.strip(), "a docstring line") for ln in STRICT_DOC.splitlines()]


def test_a_header_with_open_brackets_goes_on():
    """Review 2, finding 2: a signature that wraps with no trailing comma
    still opens a docstring."""
    from rota.roles.api import _added_kinds
    diff = "\n".join(["@@ -1,6 +1,7 @@", " def f(", "     a, b", " ) -> int:",
                      '     """Add two numbers.', "+    :param a: the first",
                      '     """', "     return a + b"])
    assert _added_kinds(diff) == [(":param a: the first", "a docstring line")]


@pytest.mark.skipif(REAL_CORE is None, reason=f"no {CLICKI} at {CLICKI_FORK[:8]}")
def test_a_method_docstring_hunk_opens_at_its_class(tmp_path):
    """Review 2, finding 3: the change is in a method's docstring. The plain
    hunk starts inside it, and the walk's hunk opens at the class line."""
    old = ("                        temporarily pushed in which case this can "
           "be disabled.\n")
    new = "        :param strict: raise when no context is pushed.\n"
    after = _once(REAL_CORE, old, old + new)
    plain, whole = _walk_of(tmp_path, "src/click/core.py", REAL_CORE, after)
    hunk = _hunk_of(plain, new.rstrip("\n"))
    assert '"""' not in "\n".join(hunk)
    assert not any(ln[1:].lstrip().startswith(("def ", "class "))
                   for ln in hunk[1:])
    assert _hunk_of(whole, new.rstrip("\n"))[1].startswith(" class Context")
    from rota.roles.api import _added_kinds
    assert _added_kinds(whole) == [(new.strip(), "a docstring line")]


def test_a_missing_temp_directory_still_gives_kinds(s279, tmp_path,
                                                     monkeypatch):
    """Review 2, finding 4: rota cannot write the attributes file. The walk
    runs `-W` without it, and the pass still lands."""
    import tempfile
    monkeypatch.setattr(tempfile, "gettempdir",
                        lambda: str(tmp_path / "no such directory"))
    out = _land(_critic(s279), batch_id="bg_3", result="pass",
                lines=S279_LINES)
    assert out["result"] == "pass"


# Frame 311: a docstring line counts when the criterion asks for one (ruled:
# Roman, 2026-10-24 01:05). Night 160's bg_2 at 905345ed: 40 docstring lines
# were refused under cr_3, whose own words name the docstring. The texts are
# verbatim from `.rota/clickI_night160.db`, s205's first prompt.

N160_IDS = ("cr_1_confirm_default_on_eof", "cr_2_confirm_default_on_eof",
            "cr_3_confirm_default_on_eof")
N160_TEXTS = {
    "cr_1_confirm_default_on_eof":
        "confirm() must accept an optional 'default_on_eof' argument which "
        "is False by default. When this flag is True and stdin is closed "
        "(EOF), confirm() returns the provided default value instead of "
        "raising UsageError or aborting. Callers who do not turn it on still "
        "abort at end of input, just as they do now.",
    "cr_2_confirm_default_on_eof":
        "Line 3's check must close stdin first to show that confirm() "
        "returns the default at end of input without waiting.",
    # Version 7, the text the night's seats read.
    "cr_3_confirm_default_on_eof":
        "Line 4's check must verify that confirm()'s docstring explains the "
        "'default_on_eof' flag and its effect on EOF behavior.",
}
N160_FLAG = "    default_on_eof: bool = False,\n"
N160_DOC = (
    "    :param default_on_eof: If True, when stdin is closed (EOF), return the\n"
    "        provided default value instead of raising :exc:`Abort`. Callers who\n"
    "        do not enable this flag will still abort at end of input, just as\n"
    "        they do now. When enabled, confirm() returns the default value on\n"
    "        EOF rather than waiting for further input or aborting.\n")
N160_VERSION = ("\n"
                "    .. versionadded:: 8.5.0\n"
                "        Added the ``default_on_eof`` parameter.\n")
N160_CODE = ("            if default_on_eof and default is not None:\n"
             "                return default\n")
# A short `confirm`. The added lines fall where bg_2's diff put them.
N160_BEFORE = (
    "def confirm(\n"
    "    text: str,\n"
    "    default: bool | None = False,\n"
    "    err: bool = False,\n"
    "{flag}"
    ") -> bool:\n"
    '    """Prompts for confirmation (yes/no question).\n'
    "\n"
    "    :param err: if set to true the file defaults to ``stderr`` instead of\n"
    "                ``stdout``, the same as with echo.\n"
    "{doc}"
    "\n"
    "    .. versionadded:: 4.0\n"
    "        Added the ``err`` parameter.\n"
    "{version}"
    '    """\n'
    "    while True:\n"
    "        try:\n"
    "            value = _readline_prompt(text, err).lower().strip()\n"
    "        except (KeyboardInterrupt, EOFError):\n"
    "{code}"
    "            raise Abort() from None\n"
    '        if value in ("y", "yes"):\n'
    "            rv = True\n"
    "    return rv\n"
)
# s205's call, `tool_calls` s205 seq 7, verbatim from turn 1's completion.
S205_CALL = r"""TOOL: verdicts.emit(batch_id='bg_2', result='pass', failed_criterion=None, reason='', diff_ref='', lines={'cr_1_confirm_default_on_eof': '    default_on_eof: bool = False,', 'cr_2_confirm_default_on_eof': '            if default_on_eof and default is not None:', 'cr_3_confirm_default_on_eof': ':param default_on_eof: If True, when stdin is closed (EOF), return the\n        provided default value instead of raising :exc:`Abort`. Callers who\ndoes not enable this flag will still abort at end of input, just as\nthey do now. When enabled, confirm() returns the default value on\nEOF rather than waiting for further input or aborting.'})"""
# s206's call, `turns` s206 seq 1, verbatim.
S206_CALL = r"""TOOL: verdicts.emit(batch_id='bg_2', result='pass', failed_criterion=None, reason='', diff_ref='', lines={'cr_1_confirm_default_on_eof': '    default_on_eof: bool = False,', 'cr_2_confirm_default_on_eof': '            if default_on_eof and default is not None:', 'cr_3_confirm_default_on_eof': '    :param default_on_eof: If True, when stdin is closed (EOF), return the'})"""
N160_LISTED = ("The added lines of code are 'default_on_eof: bool = False,', "
               "'if default_on_eof and default is not None:', "
               "'return default'. ")


def _seed_texts(conn, texts: dict) -> None:
    for cid, text in texts.items():
        conn.execute("UPDATE criteria SET text = ? WHERE id = ?", (text, cid))
    conn.commit()


@pytest.fixture
def n160(tmp_path):
    """Night 160's bg_2: the batch adds `default_on_eof` to `confirm`."""
    before = N160_BEFORE.format(flag="", doc="", version="", code="")
    after = N160_BEFORE.format(flag=N160_FLAG, doc=N160_DOC,
                               version=N160_VERSION, code=N160_CODE)
    repo, head = _repo_of(tmp_path, "src/click/termui.py", before, after)
    conn = init_db(tmp_path / "rota.db")
    _seed(conn, "bg_2", N160_IDS, worktree=repo, head=head)
    _seed_texts(conn, N160_TEXTS)
    return conn


def test_s206_docstring_line_lands_for_the_docstring_criterion(n160):
    """cr_3's text names the docstring, so its one `:param` line lands."""
    (call,) = toolproto.extract(S206_CALL)
    out = _land(_critic(n160, "bg_2"), call.name, **call.args)
    assert out["result"] == "pass"


def test_s205_docstring_block_meets_the_cap_and_no_kind_words(n160):
    """s205's five parts still meet frame 170's block cap. The text does not
    call the docstring useless, and it tells the seat to copy one line of
    the docstring."""
    cid = "cr_3_confirm_default_on_eof"
    (call,) = toolproto.extract(S205_CALL)
    said = _refused(_critic(n160, "bg_2"), **call.args)
    held = ", ".join(repr(ln.strip()) for ln in (
        N160_DOC.splitlines()[0:2] + N160_DOC.splitlines()[3:5]))
    assert "does nothing that a criterion asks for" not in said
    assert said == (
        f"the value for {cid} holds 5 lines, and a pass names one added line "
        f"per criterion. Copy the one line of the [diff] block that meets "
        f"{cid}, without the +, and send the pass again. The lines you sent "
        f"hold these lines of the docstring: {held}. Copy the one that does "
        f"what the criterion says. " + N160_LISTED + _bg2_fail_route(cid))


def test_a_docstring_line_for_another_criterion_stays_refused(n160):
    """cr_1 asks for behaviour, so the same docstring line meets nothing."""
    cid = "cr_1_confirm_default_on_eof"
    quote = N160_DOC.splitlines()[0].strip()
    said = _refused(_critic(n160, "bg_2"), batch_id="bg_2", result="pass",
                    lines={cid: quote,
                           "cr_2_confirm_default_on_eof":
                               "if default_on_eof and default is not None:",
                           "cr_3_confirm_default_on_eof": quote})
    assert said == _no_behaviour(cid, quote, "a docstring line", [
        "default_on_eof: bool = False,",
        "if default_on_eof and default is not None:", "return default"])


@pytest.mark.parametrize("words", [
    "The docstring of work names its argument.",
    "The documentation of work names its argument.",
    "The DOCUMENTATION of work names its argument.",
])
def test_the_words_that_ask_for_documentation(kinds, words):
    """Each word of the ruling admits a docstring line and a comment."""
    _seed_texts(kinds, {"cr_1": words})
    for value in ("The prose line of the docstring.",
                  "# the comment line of the work"):
        out = _land(_critic(kinds, "bg_1"), batch_id="bg_1", result="pass",
                    lines={"cr_1": value})
        assert out["result"] == "pass"


# Night 160's ver_opt_show_py_help, verbatim from the `criteria` table. A
# help string is code the user sees, so a docstring line does not meet it
# (frame 311, pass 1b).
HELP_TEXT = ("The --version flag help text must document the new show_python "
             "flag and describe its effect on the output message.")


@pytest.mark.parametrize("words", [HELP_TEXT, "work is documented."],
                         ids=["help_text", "documented"])
def test_a_help_text_criterion_refuses_a_docstring_line(kinds, words):
    _seed_texts(kinds, {"cr_1": words})
    value = "The prose line of the docstring."
    said = _refused(_critic(kinds, "bg_1"), batch_id="bg_1", result="pass",
                    lines={"cr_1": value})
    assert said == _no_behaviour("cr_1", value, "a docstring line", KIND_CODE)


@pytest.mark.parametrize("value,kind", [
    ("from x import y", "a plain import"),
    ("pass", "`pass`"),
])
def test_a_documentation_criterion_still_refuses_other_kinds(kinds, value,
                                                             kind):
    """Only the kinds that document the code meet a documentation
    criterion."""
    _seed_texts(kinds, {"cr_1": "The docstring of work names its argument."})
    said = _refused(_critic(kinds, "bg_1"), batch_id="bg_1", result="pass",
                    lines={"cr_1": value})
    assert said == _no_behaviour("cr_1", value, kind, KIND_CODE)


# Night 160's s146 quoted the docstring of `echo_json` for a criterion that
# asks for behaviour. Its refusals stay as they were. The texts are verbatim
# from s146's first prompt and its session account.
S146_TEXT = ("The function `echo_json` must not print any additional text "
             "(such as labels or prompts) before or after the JSON output.")
S146_ADDED = (
    "def echo_json(obj: object) -> None:\n"
    '    """Print an object as compact JSON on one line, followed by a newline.\n'
    "\n"
    "    :param obj: The object to serialize and print.\n"
    '    """\n'
    "    import json\n"
    "    file = _default_text_stdout()\n"
    "    file.write(json.dumps(obj, separators=(',', ':')))\n"
    "    file.write('\\n')\n"
    "    file.flush()\n"
    "\n")
S146_CODE = ["def echo_json(obj: object) -> None:",
             "file = _default_text_stdout()",
             "file.write(json.dumps(obj, separators=(',', ':')))",
             "file.write('\\n')",
             "file.flush()"]


@pytest.fixture
def s146(tmp_path):
    """Night 160's bg_1: the batch adds `echo_json` to `src/click/utils.py`."""
    repo, head = _repo_of(tmp_path, "src/click/utils.py", S134_BEFORE,
                          S134_BEFORE + S146_ADDED)
    conn = init_db(tmp_path / "rota.db")
    _seed(conn, "bg_1", ["echo_json_helper"], worktree=repo, head=head)
    _seed_texts(conn, {"echo_json_helper": S146_TEXT})
    return conn


@pytest.mark.parametrize("call,quote,kind", [
    ("TOOL: verdicts.emit(batch_id='bg_1', result='pass', reason='', "
     "lines={'echo_json_helper': '    import json'})",
     "import json", "a plain import"),
    ("TOOL: verdicts.emit(batch_id='bg_1', result='pass', reason='', "
     "lines={'echo_json_helper': '    \"\"\"Print an object as compact JSON "
     "on one line, followed by a newline.'})",
     '"""Print an object as compact JSON on one line, followed by a newline.',
     "a docstring line"),
], ids=["import", "docstring"])
def test_s146_calls_stay_refused(s146, call, quote, kind):
    (c,) = toolproto.extract(call)
    said = _refused(_critic(s146, "bg_1"), **c.args)
    assert said == _no_behaviour("echo_json_helper", quote, kind, S146_CODE)


# F37, night 171: the Critic gave no verdict in s128 to s130, because the door
# refused the 4-line `if roaming:` block for c_1, a criterion of two cases.
# The texts and the added lines are verbatim from s128's first prompt.
N171_C1 = (r"When get_app_dir is invoked on Windows with APPDATA or "
           r"LOCALAPPDATA unset:   - If roaming=True, the returned path must "
           r"be under C:\Users\<user>\AppData\Roaming.   - If roaming=False, "
           r"the returned path must be under C:\Users\<user>\AppData\Local.")
N171_C3 = ("The get_app_dir function must not raise an exception when APPDATA "
           "or LOCALAPPDATA environment variables are unset on Windows; it "
           "must fall back to the appropriate AppData subfolder.")
N171_BEFORE = (
    "import os\n"
    "\n"
    "\n"
    "def get_app_dir(app_name: str, roaming: bool = True) -> str:\n"
    "    if WIN:\n"
    '        key = "APPDATA" if roaming else "LOCALAPPDATA"\n'
    "        folder = os.environ.get(key)\n"
    "        if folder is None:\n"
    "{body}"
    "        return os.path.join(folder, app_name)\n"
    "    return app_name\n"
)
N171_OLD = '            folder = os.path.expanduser("~")\n'
N171_ADDED = [
    "            # If APPDATA/LOCALAPPDATA is unset, fall back to the appropriate",
    "            # AppData subfolder under the user profile instead of the bare "
    "home folder.",
    '            appdata_roaming = os.path.join(os.path.expanduser("~"), '
    '"AppData", "Roaming")',
    '            appdata_local = os.path.join(os.path.expanduser("~"), '
    '"AppData", "Local")',
    "            if roaming:",
    "                folder = appdata_roaming",
    "            else:",
    "                folder = appdata_local",
]
N171_BLOCK = "\n".join(N171_ADDED[4:])
N171_EIGHT = "\n".join(N171_ADDED)


@pytest.fixture
def n171(tmp_path):
    """Night 171's bg_1: the batch replaces the bare home folder with the
    AppData folder of the roaming flag in `src/click/utils.py`."""
    repo, head = _repo_of(tmp_path, "src/click/utils.py",
                          N171_BEFORE.format(body=N171_OLD),
                          N171_BEFORE.format(body="".join(
                              ln + "\n" for ln in N171_ADDED)))
    conn = init_db(tmp_path / "rota.db")
    _seed(conn, "bg_1", ["c_1", "c_3"], worktree=repo, head=head)
    _seed_texts(conn, {"c_1": N171_C1, "c_3": N171_C3})
    return conn


def test_n171_the_criteria_count_their_cases():
    """c_1 names a Roaming case and a Local case. c_3 names one case."""
    from rota.roles.api import _names_cases
    assert _names_cases(N171_C1)
    assert not _names_cases(N171_C3)


def test_n171_the_if_block_lands_for_a_criterion_of_two_cases(n171):
    out = _land(_critic(n171, "bg_1"), batch_id="bg_1", result="pass",
                lines={"c_1": N171_BLOCK, "c_3": N171_ADDED[3].strip()})
    assert out["result"] == "pass"


def test_n171_the_hold_quotes_every_line_of_the_block(n171):
    """The hold reads the same parts as the door, so it asks about the whole
    `if` statement and not only its first line (frame 201, pass 3)."""
    sb = _critic(n171, "bg_1")
    with pytest.raises(ValueError) as exc:
        sb.call("verdicts.emit", batch_id="bg_1", result="pass",
                lines={"c_1": N171_BLOCK, "c_3": N171_ADDED[3].strip()})
    assert ("Your lines hold 'if roaming:', then 'folder = appdata_roaming', "
            "then 'else:', then 'folder = appdata_local'. Do those lines do "
            "what the criterion says, or the opposite?") in str(exc.value)


def test_n171_the_eight_lines_are_refused_and_the_block_is_named(n171):
    """s129's value for c_1: two comments, two assignments and the block. It
    is four statements, so frame 170's rule still refuses it."""
    said = _refused(_critic(n171, "bg_1"), batch_id="bg_1", result="pass",
                    lines={"c_1": N171_EIGHT, "c_3": N171_ADDED[3].strip()})
    assert said.startswith(
        "the value for c_1 holds 8 lines, and a pass names one added line per "
        "criterion. Copy the one line of the [diff] block that meets c_1, "
        "without the +, and send the pass again. c_1 names more than one "
        "case, so one `if`, `try`, `match` or conditional expression of "
        "added lines that covers every case also counts as one line. Copy "
        "that one statement whole, with no other line. Lines 5 to 8 of your "
        "value are one `if` statement: 'if roaming:', 'folder = "
        "appdata_roaming', 'else:', 'folder = appdata_local'. Send those 4 "
        "lines alone for c_1. The added lines of code are ")
    assert "Copy the one that does what the criterion says" not in said
    assert said.endswith("`verdicts.claim_encodes('c_1', encodes=...)` "
                         "first, as for any fail")


def test_n171_s128_call_is_refused_on_the_one_case_criterion(n171):
    """s128's third value: the block for c_1 and the eight lines for c_3. c_1
    now lands, and c_3 names one case, so its words do not change."""
    said = _refused(_critic(n171, "bg_1"), batch_id="bg_1", result="pass",
                    lines={"c_1": N171_BLOCK, "c_3": N171_EIGHT})
    assert said.startswith(
        "the value for c_3 holds 8 lines, and a pass names one added line per "
        "criterion. Copy the one line of the [diff] block that meets c_3, "
        "without the +, and send the pass again. The lines you sent hold "
        "these added lines: ")
    assert "more than one case" not in said


def test_n171_the_block_is_refused_for_a_criterion_of_one_case(n171):
    """The rule is the criterion's: one case is met by one line."""
    _seed_texts(n171, {"c_1": "The returned path is under AppData Roaming "
                              "when roaming is True."})
    said = _refused(_critic(n171, "bg_1"), batch_id="bg_1", result="pass",
                    lines={"c_1": N171_BLOCK, "c_3": N171_ADDED[3].strip()})
    assert said.startswith("the value for c_1 holds 4 lines")
    assert "more than one case" not in said


def test_n171_lines_that_are_not_one_run_are_refused(n171):
    """The block lines out of their order are no statement of the diff."""
    swapped = "\n".join(N171_ADDED[i] for i in (4, 7, 6, 5))
    said = _refused(_critic(n171, "bg_1"), batch_id="bg_1", result="pass",
                    lines={"c_1": swapped, "c_3": N171_ADDED[3].strip()})
    assert said.startswith("the value for c_1 holds 4 lines")


# Frame 170's fault under a criterion of two cases: a whole added function
# is one statement, and it lands on any batch, so it names nothing.
TWO_CASES = "If a is set, work returns a + 1. Otherwise work returns 0."
FN_ADDED = (
    "def work(a):\n"
    "    total = a + 1\n"
    "    if a:\n"
    "        return total\n"
    "    else:\n"
    "        return 0\n"
)


def test_a_whole_function_stays_refused_for_a_criterion_of_two_cases(tmp_path):
    conn = _one_criterion(tmp_path, "work.py", "", FN_ADDED)
    _seed_texts(conn, {"cr_1": TWO_CASES})
    said = _refused(_critic(conn, "bg_1"), batch_id="bg_1", result="pass",
                    lines={"cr_1": FN_ADDED})
    assert said.startswith("the value for cr_1 holds 6 lines")
    assert ("Lines 3 to 6 of your value are one `if` statement: 'if a:', "
            "'return total', 'else:', 'return 0'.") in said


def test_the_if_inside_the_function_lands_for_two_cases(tmp_path):
    conn = _one_criterion(tmp_path, "work.py", "", FN_ADDED)
    _seed_texts(conn, {"cr_1": TWO_CASES})
    block = "\n".join(FN_ADDED.splitlines()[2:])
    assert _pass(conn, block)["result"] == "pass"


def test_a_wrapped_conditional_expression_lands_for_two_cases(tmp_path):
    after = ("def work(a):\n"
             "    return (\n"
             "        a + 1\n"
             "        if a else 0)\n")
    conn = _one_criterion(tmp_path, "work.py", "", after)
    _seed_texts(conn, {"cr_1": TWO_CASES})
    block = "\n".join(after.splitlines()[1:])
    assert _pass(conn, block)["result"] == "pass"
