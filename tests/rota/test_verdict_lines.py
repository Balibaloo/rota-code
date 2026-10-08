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


@pytest.fixture
def s279(tmp_path):
    """Night 127's bg_3: a repository whose one batch commit adds the four
    added lines of s279's diff to `src/click/decorators.py`."""
    repo = tmp_path / "repo"
    path = repo / "src" / "click" / "decorators.py"
    path.parent.mkdir(parents=True)
    _git(tmp_path, "init", "-q", str(repo))
    path.write_bytes(_BEFORE.format(flag="", version="",
                                    message=OLD_MESSAGE).encode())
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "click")
    path.write_bytes(_BEFORE.format(
        flag=L_FLAG + "\n", version=L_NOTE + "\n" + L_VERSION + "\n",
        message=L_MESSAGE + "\n").encode())
    _git(repo, "commit", "-q", "-am", "show python")
    head = _git(repo, "rev-parse", "HEAD").strip()
    conn = init_db(tmp_path / "rota.db")
    _seed(conn, "bg_3", S279_IDS, worktree=str(repo), head=head)
    return conn


def _critic(conn, batch_id="bg_3", mode="review"):
    return build("critic", conn, batch_id=batch_id, mode=mode)


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
    out = sb.call("verdicts.emit", batch_id="bg_3", result="pass",
                  lines=dict(S279_LINES))
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
    out = _critic(s279).call("verdicts.emit", batch_id="bg_3", result="pass",
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


def test_a_block_for_every_criterion_is_refused(s279):
    """Frame 170's review of 845e0b80: a 4-line dump given for all three
    criteria landed, so the lines named nothing."""
    block = "\n".join(ln.strip() for ln in (L_FLAG, L_NOTE, L_VERSION, L_MESSAGE))
    said = _refused(_critic(s279), batch_id="bg_3", result="pass",
                    lines={cid: block for cid in S279_IDS})
    assert said == (
        "the value for cr_1_version_option_show_python_flag holds 4 lines, and "
        "a pass names one added line per criterion. Copy the one line of the "
        "[diff] block that meets cr_1_version_option_show_python_flag, without "
        "the +, and send the pass again")


def test_a_value_of_two_lines_lands(s279):
    """A statement that wraps is two lines, and the door admits two."""
    two = L_NOTE.strip() + "\n" + L_VERSION.strip()
    out = _critic(s279).call("verdicts.emit", batch_id="bg_3", result="pass",
                             lines={**S279_LINES, CR3: two})
    assert out["result"] == "pass"


def test_a_value_of_three_lines_is_refused(s279):
    """The limit is two lines. A third line is refused."""
    three = "\n".join(ln.strip() for ln in (L_NOTE, L_VERSION, L_FLAG))
    said = _refused(_critic(s279), batch_id="bg_3", result="pass",
                    lines={**S279_LINES, CR3: three})
    assert said.startswith(f"the value for {CR3} holds 3 lines")


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
    out = _critic(conn).call("verdicts.emit", batch_id="bg_3", result="pass",
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
    out = _critic(s279).call(call.name, **call.args)
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

def _no_behaviour(cid, quote, kind) -> str:
    return (
        f"the line for {cid}, {quote!r}, is {kind}, and a blank line, `pass`, "
        f"`...`, a comment, a plain import or a docstring line does nothing "
        f"that a criterion asks for. Copy the added line that does what "
        f"{cid} says, without the +, and send the pass again. If no added line meets "
        f"{cid}, that is a fail on it: `verdicts.claim_encodes({cid!r}, "
        f"encodes=...)` first, as for any fail")


def _repo_of(tmp_path, rel, before: str, after: str) -> tuple[str, str]:
    """A repository whose one batch commit turns `before` into `after` in
    the file `rel`. Returns the path and the head commit."""
    repo = tmp_path / "repo"
    path = repo / rel
    path.parent.mkdir(parents=True)
    _git(tmp_path, "init", "-q", str(repo))
    path.write_bytes(before.encode())
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    path.write_bytes(after.encode())
    _git(repo, "commit", "-q", "-am", "the batch")
    return str(repo), _git(repo, "rev-parse", "HEAD").strip()


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


def test_s134_pass_naming_import_json_is_refused(s134):
    (call,) = toolproto.extract(S134_CALL)
    said = _refused(_critic(s134, "bg_1"), **call.args)
    assert said == _no_behaviour("echo_json_compact_3", "import json",
                                 "a plain import")


def test_s134_pass_naming_the_dumps_line_lands(s134):
    """`json.dumps` raises the TypeError, so its line meets the criterion."""
    (call,) = toolproto.extract(S134_CALL)
    lines = {**call.args["lines"],
             "echo_json_compact_3": call.args["lines"]["echo_json_compact"]}
    out = _critic(s134, "bg_1").call(call.name, **{**call.args, "lines": lines})
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
    assert said == _no_behaviour("cr_1", quote, kind)


@pytest.mark.parametrize("value", [
    "return total  # the sum of a and one",
    "total = a + 1",
    "if a:",
])
def test_a_line_that_does_something_lands(kinds, value):
    out = _critic(kinds, "bg_1").call("verdicts.emit", batch_id="bg_1",
                                      result="pass", lines={"cr_1": value})
    assert out["result"] == "pass"


def test_the_s279_comment_alone_is_refused(s279):
    """s279's diff adds a comment line. Named alone, it is refused."""
    said = _refused(_critic(s279), batch_id="bg_3", result="pass",
                    lines={**S279_LINES, CR3: L_NOTE.strip()})
    assert said == _no_behaviour(CR3, L_NOTE.strip(), "a comment")


# Frame 180, pass 2: the findings of the diff review of 7b25da26.

def _one_criterion(tmp_path, rel, before, after):
    repo, head = _repo_of(tmp_path, rel, before, after)
    conn = init_db(tmp_path / "rota.db")
    _seed(conn, "bg_1", ["cr_1"], worktree=repo, head=head)
    return conn


def _pass(conn, value):
    return _critic(conn, "bg_1").call("verdicts.emit", batch_id="bg_1",
                                      result="pass", lines={"cr_1": value})


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
                                 "a docstring line")
