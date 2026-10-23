"""Frame 307: three counters of the night instruments, on rows of night 158.

Night 158's read, W7, found three counters wrong before any ratio rests on
them. Section 12's M0 missed a page shown again, M1 and M2 read the first
guess and not the last one shown, and the nightcount counted a commit that
landed before the invention. Each test holds rows copied from
`.rota/clickI_night158.db`. A prompt is cut to the lines the counter reads.
"""
from __future__ import annotations

import json

from rota.core.db import connect_readonly, init_db
from rota.tools import nightreport
from rota.tools.nightcount import count

GUESS = "frame 298: the guess"


def _section(lines: list[str], name: str) -> list[str]:
    start = next(i for i, l in enumerate(lines) if l.startswith(f"== {name}"))
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("== ")),
               len(lines))
    return lines[start + 1:end]


# Night 158's items: four description items and three requests.
ITEMS = (("how_it_works", 1), ("defines_commands_and_options", 1),
         ("parses_and_executes_inputs", 1), ("provides_command_line_interface", 1),
         ("echo_json", 0), ("confirm_default_on_eof", 0),
         ("version_option_show_python", 0))
BATCHES = (("bg_1", "echo_json", "5b6c54836f372dcf924743177c3d372afa64b576", "merged"),
           ("bg_2", "confirm_default_on_eof", "f7bb9d5f9a63fa72584a3ded919342efd61929cc",
            "deferred"),
           ("bg_3", "version_option_show_python",
            "ea03bf63563d28860fbf4d0e1ac3ab3b84784b98", "merged"))
DESC = ["defines_commands_and_options", "how_it_works", "parses_and_executes_inputs",
        "provides_command_line_interface"]
# The presents of night 158 and their causes, in order. The glossary page m6
# is cut to two refs.
MESSAGES = (
    ("m1", None, "vision_keeper", "liaison", "submit", DESC),
    ("m2", "m1", "liaison", "principal", "present", DESC),
    ("m6", None, "liaison", "principal", "present", ["argument", "how_it_works"]),
    ("m11", None, "liaison", "principal", "present", ["l_07c5d7845c", "how_it_works"]),
    ("m23", None, "vision_keeper", "liaison", "submit", ["echo_json"]),
    ("m24", "m23", "liaison", "principal", "present",
     ["echo_json", "how_it_works", "l_6d47c2386a", "guess:echo_json"]),
    ("m29", None, "liaison", "principal", "present", ["bg_1", "echo_json", "echo_json_helper"]),
    ("m49", None, "vision_keeper", "liaison", "submit", ["confirm_default_on_eof"]),
    ("m50", "m49", "liaison", "principal", "present",
     ["confirm_default_on_eof", *DESC, "l_79905828a5", "l_e7c6ed5501",
      "guess:confirm_default_on_eof"]),
    ("m61", None, "liaison", "principal", "present",
     ["bg_2", "confirm_default_on_eof", "cr_1_confirm_default_on_eof"]),
    ("m89", None, "liaison", "principal", "present",
     ["command#root", "option#root", "parameter#root", "confirm_default_on_eof",
      "cr_1_confirm_default_on_eof", "guess:confirm_default_on_eof"]),
    ("m_shift_confirm_default_on_eof_m_p3", None, "liaison", "principal", "present",
     ["confirm_default_on_eof", "s3"]),
    ("m103", None, "vision_keeper", "liaison", "submit", ["version_option_show_python"]),
    ("m104", "m103", "liaison", "principal", "present",
     [*DESC, "version_option_show_python", "l_e7c6ed5501", "l_b093572e02",
      "guess:version_option_show_python"]),
    ("m106", "m104", "principal", "liaison", "verdict", ["guess:version_option_show_python"]),
    ("m122", None, "liaison", "principal", "present",
     ["how_it_works", "version_option_show_python", "guess:version_option_show_python"]),
)
# The send door's records of what each code line showed.
STAMPS = {"m24": {"guess:echo_json": {"guess": [1, ""]}},
          "m50": {"guess:confirm_default_on_eof": {"guess": [1, ""]}},
          "m89": {"guess:confirm_default_on_eof": {"batch": "bg_2"}},
          "m104": {"guess:version_option_show_python": {"guess": [1, ""]}},
          "m122": {"guess:version_option_show_python": {"guess": [1, "m106"]}}}
# touch_guesses rows 1 to 5 and 10 to 17.
GUESSES = (("echo_json", "", "src/click/utils.py", "path"),
           ("echo_json", "", "tests/test_utils/test_echo.py", "path"),
           ("echo_json", "", "tests/test_utils/test_echo_via_pager.py", "path"),
           ("echo_json", "m26", "src/click/utils.py", "path"),
           ("echo_json", "m26", "tests/test_utils/test_echo.py", "path"),
           ("version_option_show_python", "", "src/click/options.py", "path"),
           ("version_option_show_python", "", "tests/test_options.py", "path"),
           ("version_option_show_python", "", "src/click/decorators.py::version_option",
            "symbol"),
           ("version_option_show_python", "", "src/click/decorators.py::custom_version_option",
            "symbol"),
           ("version_option_show_python", "m106", "src/click/decorators.py", "path"),
           ("version_option_show_python", "m106", "tests/test_options.py", "path"),
           ("version_option_show_python", "m106", "src/click/decorators.py::version_option",
            "symbol"),
           ("version_option_show_python", "m106",
            "tests/test_options.py::test_version_option", "symbol"))
# The merge commits' diffs, from the night's report.
TRUTH = {"bg_1": ["src/click/utils.py", "tests/test_utils/test_echo_via_json.py"],
         "bg_3": ["src/click/decorators.py", "tests/test_version_option.py",
                  "tests/test_version_option_default.py",
                  "tests/test_version_option_format.py"]}


def _night158(tmp_path):
    conn = init_db(tmp_path / "clickI_night158.db")
    conn.execute("PRAGMA foreign_keys = OFF")
    for iid, desc in ITEMS:
        conn.execute("INSERT INTO items (id, text, kind, approval, version, is_description) "
                     "VALUES (?, ?, 'in_scope', 'approved', 1, ?)", (iid, iid, desc))
    for bid, iid, head, status in BATCHES:
        conn.execute("INSERT INTO batches (id, item_id, head_commit, status) "
                     "VALUES (?, ?, ?, ?)", (bid, iid, head, status))
    for seq, (mid, cause, fr, to, verb, refs) in enumerate(MESSAGES, 1):
        conn.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, verb, "
                     "body_refs, seq) VALUES (?, ?, 't', ?, ?, ?, ?, ?)",
                     (mid, cause, fr, to, verb, json.dumps(refs), seq))
    for mid, stamp in STAMPS.items():
        conn.execute("INSERT INTO config (key, value) VALUES (?, ?)",
                     (f"code:{mid}", json.dumps(stamp)))
    for iid, ruling, grain, kind in GUESSES:
        conn.execute("INSERT INTO touch_guesses (item_id, item_ver, ruling_id, grain, "
                     "grain_kind) VALUES (?, 1, ?, ?, ?)", (iid, ruling, grain, kind))
    conn.commit()
    conn.close()
    return tmp_path / "clickI_night158.db"


def _guess_lines(tmp_path, monkeypatch) -> list[str]:
    monkeypatch.setattr(nightreport, "_git_truth",
                        lambda repo, bid, head=None: TRUTH.get(bid))
    conn = nightreport.open_ro(_night158(tmp_path))
    try:
        return _section(nightreport.build(conn, repo=tmp_path), GUESS)
    finally:
        conn.close()


def test_m0_counts_a_page_shown_again_as_a_sign_off_page(tmp_path, monkeypatch):
    """m89 and m122 show a request item again with no submit cause. The
    batch pages, the shift page and the onboarding pages stay out."""
    lines = _guess_lines(tmp_path, monkeypatch)
    assert "M0: 5 of 6 sign-off pages carry a code line" in lines


def test_m1_and_m2_read_the_last_guess_the_principal_saw(tmp_path, monkeypatch):
    """m122 showed the m106 rewrite. The first guess named
    `src/click/options.py`, which click does not have."""
    lines = _guess_lines(tmp_path, monkeypatch)
    assert ("  version_option_show_python guess=src/click/decorators.py,tests/test_options.py "
            "truth=src/click/decorators.py,tests/test_version_option.py,"
            "tests/test_version_option_default.py,tests/test_version_option_format.py "
            "M1=hit M2=hit") in lines
    # No later page showed echo_json's rewrite as a guess, so m24's stays.
    assert ("  echo_json guess=src/click/utils.py,tests/test_utils/test_echo.py,"
            "tests/test_utils/test_echo_via_pager.py "
            "truth=src/click/utils.py,tests/test_utils/test_echo_via_json.py "
            "M1=hit M2=hit") in lines
    assert "M1: 2 of 2 merged items, 0 with no truth, 0 with no own guess" in lines


# ---------------------------------------------------------------------------
# The nightcount's landed commit

def _commit(sha: str, path: str) -> str:
    return (f'OK code.commit -> {{"committed": true, "head_commit": "{sha}", '
            f'"touched": ["{path}"]}}')


FEEDBACK = ("You wrote tool results into your own reply -- the lines beginning "
            "`OK ...` or `ERROR ...`. Those did not come from me and nothing behind them ran.")
# s170 turns 4 and 8 sent the same completion, and the commit f791bcbf
# landed between them.
S170 = ("TOOL: code.source(path='tests/test_utils/test_confirm.py', start=0, end=-1)\n\n"
        "OK code.source ->")
# s134 turn 10. The commit 5b6c5483, which the merge took, landed at turn 4.
S134 = ("Let me confirm the current state of `echo_json` in `src/click/utils.py`:\n\n"
        "TOOL: code.source(path='src/click/utils.py', start=688, end=703)\n\n"
        "OK code.source ->")
# s279 turn 23 ends in an empty invented write result.
S279 = ("TOOL: code.write(path='src/click/decorators.py', text='        echo(', "
        "start=540, end=544)\n\nOK code.write ->")


def _session(conn, sid, seq):
    conn.execute("INSERT INTO sessions (id, role, wake_kind, wake_detail, committed, seq, "
                 "mode, model) VALUES (?, 'developer', 'tick:write', '', 1, ?, 'normal', 'm')",
                 (sid, seq))


def _turn(conn, sid, seq, user, completion):
    conn.execute("INSERT INTO turns (session_id, seq, system, user, completion, ms) "
                 "VALUES (?, ?, 'brief', ?, ?, 0)", (sid, seq, user, completion))


def _count(tmp_path, build):
    conn = init_db(tmp_path / "clickI.db")
    build(conn)
    conn.commit()
    conn.close()
    return count(connect_readonly(tmp_path / "clickI.db"))


def test_a_commit_before_the_invention_is_not_a_landed_commit(tmp_path):
    """Night 158 counted 7 turns, and each commit sat before the turn's own
    echo. s170's first echo is turn 4's identical completion, so the scan
    starts after the last echo."""
    def build(conn):
        _session(conn, "s170", 170)
        _turn(conn, "s170", 8, "the brief", S170)
        _turn(conn, "s170", 9, "\n\n".join([
            "the brief", S170, FEEDBACK,
            _commit("f791bcbf1ade040090ea75288a85100f44594e59", "src/click/termui.py"),
            S170, "OK code.source -> unchanged since you asked earlier this session.",
            FEEDBACK]), "TOOL: code.write(path='tests/test_utils/test_confirm.py')")
        _session(conn, "s134", 134)
        _turn(conn, "s134", 10, "the brief", S134)
        _turn(conn, "s134", 11, "\n\n".join([
            "the brief", "TOOL: code.commit(message='Fix echo_json duplication')",
            _commit("5b6c54836f372dcf924743177c3d372afa64b576", "src/click/utils.py"),
            S134, FEEDBACK]), "done")

    c = _count(tmp_path, build)
    assert c["made_turns"] == 2
    assert c["ran_commits"] == 0 and c["shas"] == []


def test_the_commit_after_the_invention_is_counted_and_not_an_earlier_one(tmp_path):
    """s279's rows with the merge's commit ea03bf63 moved after the echo.
    The batch's earlier commit bb7c4492 stays before it and is not counted."""
    def build(conn):
        _session(conn, "s279", 279)
        _turn(conn, "s279", 23, "the brief", S279)
        _turn(conn, "s279", 24, "\n\n".join([
            "the brief",
            _commit("bb7c449216e9292d5a63585a42713a142e4f5032", "src/click/decorators.py"),
            S279, FEEDBACK,
            _commit("ea03bf63563d28860fbf4d0e1ac3ab3b84784b98", "src/click/decorators.py")]),
            "done")

    c = _count(tmp_path, build)
    assert c["ran_commits"] == 1 and c["shas"] == ["ea03bf63"]
