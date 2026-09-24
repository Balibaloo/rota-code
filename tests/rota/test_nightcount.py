"""rota/tools/nightcount.py: the night's four counters over a run database."""
from rota.core.db import connect_readonly, init_db
from rota.tools.nightcount import count, main

# A fabricated result, as the model writes it into its completion.
# The write call comes first, so the turn counts in the turn total and not in
# the after-invention count.
FABRICATED = ('I will write the helper now.\n'
              "TOOL: code.write(path='src/click/utils.py', text='x')\n"
              'OK code.write -> {"path": "src/click/utils.py", "bytes": 100}\n')
# The runner's own result, as it lands in the next turn's prompt.
REAL_WRITE = ('OK code.write -> {"path": "src/click/utils.py", '
              '"bytes": 22087, "written, not committed": '
              '["src/click/utils.py"], "lands with": "code.commit"}')
LANDED = ('OK code.commit -> {"committed": true, "head_commit": '
          '"4473c3542b46c8e71909f0daed0fe22a5db11074", "touched": '
          '["src/click/utils.py"]}')
# The refusal of a repeat. The head is the same, the tail is on the line.
REFUSED = ("OK code.write -> unchanged since you asked earlier this session. "
           "What code.write returned then still stands.")
NOTICE = ("[3 earlier exchange(s) were dropped. Your instructions and your "
          "latest results are intact; re-read anything you still need.]")


def session(conn, sid, role="developer", kind="tick:write", prompt_hash=None):
    conn.execute(
        "INSERT INTO sessions (id, role, wake_kind, wake_detail, committed, "
        "seq, mode, model, prompt_hash) VALUES (?, ?, ?, '', 1, ?, 'normal', "
        "'m', ?)",
        (sid, role, kind, int(sid[1:]), prompt_hash))


def turn(conn, sid, seq, user="", completion=""):
    conn.execute(
        "INSERT INTO turns (session_id, seq, system, user, completion, ms) "
        "VALUES (?, ?, 'brief', ?, ?, 0)", (sid, seq, user, completion))


def counted(tmp_path, build):
    conn = init_db(tmp_path / "clickI.db")
    build(conn)
    conn.commit()
    return count(connect_readonly(tmp_path / "clickI.db"))


def test_a_made_up_result_is_counted_from_the_completion(tmp_path):
    """The fabrication is in the completion. The role split names the seat."""
    def build(conn):
        session(conn, "s1", role="developer")
        session(conn, "s2", role="tester")
        turn(conn, "s1", 1, user="the brief", completion=FABRICATED)
        turn(conn, "s1", 2, user="the brief\n" + REAL_WRITE, completion="done")
        turn(conn, "s2", 1, user="the brief", completion=FABRICATED)
        turn(conn, "s2", 2, user="the brief\n" + REFUSED, completion="done")

    c = counted(tmp_path, build)
    assert c["made_turns"] == 2 and c["made_sessions"] == 2
    assert c["made_roles"] == {"developer": 1, "tester": 1}


def test_the_ran_anyway_count_reads_the_next_turn(tmp_path):
    """A real write after a fabrication counts. A refused repeat does not."""
    def build(conn):
        session(conn, "s1")
        session(conn, "s2")
        turn(conn, "s1", 1, user="the brief", completion=FABRICATED)
        turn(conn, "s1", 2, user="the brief\n" + REAL_WRITE + "\n" + LANDED,
             completion="done")
        turn(conn, "s2", 1, user="the brief", completion=FABRICATED)
        turn(conn, "s2", 2, user="the brief\n" + REFUSED, completion="done")

    c = counted(tmp_path, build)
    assert c["made_turns"] == 2
    assert c["ran_writes"] == 1 and c["ran_commits"] == 1
    assert c["shas"] == ["4473c354"]


def test_a_write_before_the_invention_counts_only_in_the_turn_total(tmp_path):
    """
    Rule 1 of frame 77 holds the calls after the invention and leaves the
    ones before it running. A write that precedes the invention was built on
    real reads, so a night after the frame still counts it by turn. The
    after-invention count is the one that must read zero (the design review
    of frame 77, finding 4).
    """
    before = ("TOOL: code.write(path='src/click/utils.py', text='x')\n"
              "OK code.write -> {\"path\": \"src/click/utils.py\"}\n"
              "I will commit it now.")
    after = ("OK code.source -> def main(): pass\n"
             "TOOL: code.write(path='src/click/core.py', text='y')")

    def build(conn):
        session(conn, "s1")
        session(conn, "s2")
        turn(conn, "s1", 1, user="the brief", completion=before)
        turn(conn, "s1", 2, user="the brief\n" + REAL_WRITE, completion="done")
        turn(conn, "s2", 1, user="the brief", completion=after)
        turn(conn, "s2", 2, user="the brief\n" + REAL_WRITE, completion="done")

    c = counted(tmp_path, build)
    assert c["made_turns"] == 2
    assert c["ran_writes"] == 2, "both turns went on to a real write result"
    assert c["ran_after_invention"] == 1, \
        "the write before the invention was counted as run after it"


def test_an_invented_write_result_echoed_in_the_prompt_is_not_a_run(tmp_path):
    """
    The prompt quotes the made-up completion back before the real results.

    Night 91 (2026-09-24): `s154` turn 16 invented a source result, then sent
    a write, then wrote the write's `OK` line itself. The next prompt held
    that line inside the echo and the NOT RUN line after it, and the counter
    read a write the runner ran. The call record held none.
    """
    invented = ("TOOL: code.source(path='src/click/utils.py', start=1, end=9)\n"
                "OK code.source -> path: src/click/utils.py, lines: 9\n"
                "TOOL: code.write(path='src/click/utils.py', text='x')\n"
                "OK code.write -> path: src/click/utils.py, text: 'x'\n")
    held = ("NOT RUN, because you wrote a tool result of your own ahead of "
            "them: code.write(path='src/click/utils.py', text='x'). The real "
            "results of the calls that did run follow.")

    def build(conn):
        session(conn, "s1")
        turn(conn, "s1", 1, user="the brief", completion=invented)
        turn(conn, "s1", 2, user="the brief\n" + invented + "\n" + held,
             completion="done")
        # The same echo, and a real write result after it: that one counts.
        session(conn, "s2")
        turn(conn, "s2", 1, user="the brief", completion=invented)
        turn(conn, "s2", 2, user="the brief\n" + invented + "\n" + REAL_WRITE,
             completion="done")

    c = counted(tmp_path, build)
    assert c["made_turns"] == 2
    assert c["ran_writes"] == 1, "the echoed invention counted as a run"
    assert c["ran_after_invention"] == 1


def test_a_carried_forward_write_result_counts_in_neither_number(tmp_path):
    """
    `written, not committed` rides forward in every prompt until the commit.
    Night 90's s141 invented a result at turns 12 and 14, sent no write, and
    counted as a write turn twice on the carried line alone (the diff review
    of frame 77, 2026-09-23).
    """
    carried = "OK code.source -> def main(): pass\nI will commit next."

    def build(conn):
        session(conn, "s1")
        turn(conn, "s1", 1, user="the brief", completion=carried)
        turn(conn, "s1", 2, user="the brief\n" + REAL_WRITE, completion="done")

    c = counted(tmp_path, build)
    assert c["made_turns"] == 1
    assert c["ran_writes"] == 0, "a carried write result counted as a write turn"
    assert c["ran_after_invention"] == 0


def test_a_fabrication_in_the_last_turn_runs_nothing(tmp_path):
    """No next turn, so nothing ran anyway. The fabrication still counts."""
    def build(conn):
        session(conn, "s1")
        turn(conn, "s1", 1, user="the brief", completion=FABRICATED)

    c = counted(tmp_path, build)
    assert c["made_turns"] == 1
    assert c["ran_writes"] == 0 and c["ran_commits"] == 0 and c["shas"] == []


def test_a_dangling_pointer_needs_the_notice_and_the_refusal(tmp_path):
    """The eviction notice alone is not a dangling pointer."""
    def build(conn):
        session(conn, "s1")
        session(conn, "s2")
        turn(conn, "s1", 1, user=NOTICE + "\n" + REFUSED)
        turn(conn, "s1", 2, user=NOTICE + "\nOK code.read -> was run for you "
                                 "before you started.")
        turn(conn, "s2", 1, user=NOTICE + "\n" + REAL_WRITE)

    c = counted(tmp_path, build)
    assert c["dangling_turns"] == 2 and c["dangling_sessions"] == 1


def test_a_repeat_shares_the_prompt_hash_and_the_wake_kind(tmp_path):
    """The same hash on another wake kind is another wake, not a repeat."""
    def build(conn):
        session(conn, "s1", kind="tick:write", prompt_hash="h1")
        session(conn, "s2", kind="tick:write", prompt_hash="h1")
        session(conn, "s3", kind="tick:survey", prompt_hash="h1")
        session(conn, "s4", kind="tick:write", prompt_hash="h2")

    c = counted(tmp_path, build)
    assert c["repeat_wakes"] == 1
    assert c["repeat_sessions"] == 2 and c["repeats"] == 1


def test_main_prints_five_lines_of_facts(tmp_path, capsys):
    conn = init_db(tmp_path / "clickI.db")
    session(conn, "s1", role="developer", prompt_hash="h1")
    session(conn, "s2", role="developer", prompt_hash="h1")
    turn(conn, "s1", 1, user="the brief", completion=FABRICATED)
    turn(conn, "s1", 2, user=NOTICE + "\n" + REAL_WRITE + "\n" + LANDED,
         completion="done")
    turn(conn, "s2", 1, user=NOTICE + "\n" + REFUSED, completion=FABRICATED)
    turn(conn, "s2", 2, user="the brief\n" + REFUSED, completion="done")
    conn.commit()

    assert main([str(tmp_path / "clickI.db")]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0] == "NIGHTCOUNT clickI: 2 sessions, 4 turns"
    assert out[1] == "made up: 2 turns, 2 sessions (developer 2)"
    assert out[2] == ("ran anyway: 0 writes after an invention (1 turns with "
                      "a write result), 1 with a landed commit, shas 4473c354")
    assert out[3] == "dangling pointers: 1 turns, 1 sessions"
    assert out[4] == "repeats: 1 wakes repeated, 2 sessions, 1 of them repeats"


def test_a_clean_run_prints_zeros(tmp_path, capsys):
    conn = init_db(tmp_path / "clickI.db")
    session(conn, "s1", prompt_hash="h1")
    turn(conn, "s1", 1, user="the brief", completion="TOOL: code.read(path='a')")
    conn.commit()

    assert main([str(tmp_path / "clickI.db")]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out == [
        "NIGHTCOUNT clickI: 1 sessions, 1 turns",
        "made up: 0 turns, 0 sessions (none)",
        "ran anyway: 0 writes after an invention (0 turns with a write "
        "result), 0 with a landed commit, shas none",
        "dangling pointers: 0 turns, 0 sessions",
        "repeats: 0 wakes repeated, 0 sessions, 0 of them repeats",
    ]
