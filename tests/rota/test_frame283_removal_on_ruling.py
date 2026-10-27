"""
A removal of a base statement lands on a ruling, never on a note alone
(frame 283, W1 a).

Night 158 (2026-10-21): the Developer s279 of batch bg_3 wrote lines 540
to 555 of `src/click/decorators.py`, and the write dropped `ctx.exit()`
from the callback of `version_option`. The commit door refused. The seat
then logged "ctx.exit() at line 550 was unreachable after echo() call",
the note closed the `drop_notes` row as `restored`, and bb7c4492 landed
the removal. `echo` returns, so `--version` then ran the command body. A
note is the seat's own claim. Only a criterion, the request or the
principal's words admit the removal.

Frame 339: an unadmitted removal lands, and one open `touch_strays` row asks
the Architect before any merge (law 12; ruled: Roman, 2026-10-17). The
admitted removal lands with no row.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import api, prompts
from rota.roles.principal import insert_ruling_rows, ruling_rows

PATH = "src/click/decorators.py"

# The file at 7856ed8, the head s279 wrote on, and at 75cf8ed, the commit
# bg_3 forked from. Both from `D:/repos/_AI/sample_repos/clickI` by
# `git show <sha>:src/click/decorators.py`.
BASE = (Path(__file__).parent / "fixtures"
        / "night158_decorators_7856ed8.txt").read_bytes()
FORK = (Path(__file__).parent / "fixtures"
        / "night158_decorators_75cf8ed.txt").read_bytes()

# s279's texts, from `tool_calls` and `turns` of `.rota/clickI_night158.db`.
ECHO = ('        echo(\n'
        '            message % {"prog": prog_name, "package": package_name, '
        '"version": version} + (f" Python {python_version}" if python_version '
        'else ""),\n'
        '            color=ctx.color,\n'
        '        )')
BACK = ('        if version is None:\n'
        '            raise RuntimeError(\n'
        '                f"Could not determine the version for {package_name!r} '
        'automatically."\n'
        '            )\n'
        '\n'
        '        # Append Python version if show_python is True\n'
        '        python_version = ""\n'
        '        if show_python:\n'
        '            import sys\n'
        '            python_version = f"{sys.version_info.major}.'
        '{sys.version_info.minor}.{sys.version_info.micro}"\n'
        '\n' + ECHO + '\n'
        '        ctx.exit()\n')
NOTE = "removed ctx.exit() at line 550 which was unreachable after echo()"
SCOPE = "ctx.exit() at line 550 was unreachable after echo() call, removed in write"
MESSAGE = ("Fix show_python output format to include 'Python' prefix and "
           "restore ctx.exit()")

ROUTE = ("A note does not close a removal. To undo the change, put "
         "the line back with code.write, then commit in your next reply. To keep "
         "the change, commit in your next reply. The Architect then judges the "
         "removal before the batch merges.")
LEDGER = ("src/click/decorators.py holds an uncommitted write that removes "
          "`ctx.exit()` at line 550, so this note closes nothing. " + ROUTE)
# The stray of night 158's removal (frame 339).
STRAY = ("src/click/decorators.py::version_option.callback", "open",
         "removal: `ctx.exit()` at line 550")


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
                 "VALUES ('version_option_show_python','version_option shows the "
                 "Python version','in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','version_option_show_python','show_python')")
    # cr_3 of bg_3, as night 158 holds it in substance.
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('cr_3','tk1','Without show_python, the option must behave "
                 "exactly as it does today.')")
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) VALUES "
                 "('bg_3','version_option_show_python','running','abc123')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('bg_3','tk1')")
    # The night's index held the path, so `about_ref` resolves to it.
    conn.execute("INSERT INTO code_index (grain, grain_kind, sym_kind) VALUES "
                 "(?, 'path', 'file')", (PATH,))
    conn.commit()
    return conn


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t",
                           "-c", "user.email=t@t", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


def _developer(db, tmp_path):
    """bg_3's worktree: the fork 75cf8ed, then the batch's head 7856ed8 as
    one commit, and the Developer's sandbox. With no project root the base
    is HEAD~1, the fork, so the batch's own duplicate lines open no note."""
    root = tmp_path / "wt"
    (root / PATH).parent.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / PATH).write_bytes(FORK)
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "75cf8ed")
    (root / PATH).write_bytes(BASE)
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "7856ed8")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'bg_3'", (str(root),))
    db.commit()
    sb = build("developer", db, batch_id="bg_3", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    return sb, root


def _call(sb, fn, **args):
    """One call of the record. A refusal is a result, as the seat read it."""
    try:
        return sb.call(fn, **args)
    except ValueError as err:
        return {"refused": str(err)}


def _replay(sb):
    """s279's tool calls, seq 15 to 26, one reply per turn of the record.
    Returns the results by seq.

    The record's three writes back, seq 18, 24 and 25, were refused at the
    span and changed nothing. The replay leaves them out: their "To add
    after it" offer fails the follow check of frame 144, the cut door's
    finding 2, which is not this frame's door."""
    out = {}
    out[15] = _call(sb, "code.write", path=PATH, start=540, end=555, text=ECHO)
    assert out[15]["dropped"] == ("This write removes or rewrites 1 statement that your text "
                                  "does not hold: `ctx.exit()` at line 550.")
    sb.begin_reply()
    out[16] = _call(sb, "code.commit", message=MESSAGE)
    sb.begin_reply()
    log = {"about_ref": PATH, "about_table": "version_option callback"}
    out[17] = _call(sb, "ledger.log", kind="assumption", assumption=NOTE, **log)
    out[19] = _call(sb, "code.commit", message=MESSAGE)
    sb.begin_reply()
    out[20] = _call(sb, "ledger.log", kind="fault", assumption=NOTE, **log)
    sb.begin_reply()
    out[23] = _call(sb, "ledger.log", kind="scope", assumption=SCOPE, **log)
    sb.begin_reply()
    out[26] = _call(sb, "code.commit", message=MESSAGE)
    return out


def _staged(sb) -> list[dict]:
    """The staged `drop_notes` values of the path."""
    return [w[2] for w in sb.ctx.writes
            if w[0] == "drop_notes" and w[2]["path"] == PATH]


def _strays(sb) -> list[tuple]:
    """The staged `touch_strays` rows: grain, status and note."""
    return [(w[2]["path"], w[2]["status"], w[2].get("note"))
            for w in sb.ctx.writes if w[0] == "touch_strays"]


def test_s279s_removal_reaches_the_architect_as_an_open_stray_before_a_merge(db, tmp_path):
    """s279's sequence. The commit of seq 16, in the reply after the write,
    lands with one open stray that names `ctx.exit()`. The stray holds the
    merge of the head until the Architect judges it. The note stays open,
    and no row reads `restored` (review 1, findings 2 and 4)."""
    sb, root = _developer(db, tmp_path)
    out = _replay(sb)
    assert out[16]["committed"] is True, out[16]
    assert _git(root, "rev-parse", "HEAD") == out[16]["head_commit"]
    assert _strays(sb) == [STRAY]
    assert PATH in api._open_notes(sb.ctx)
    assert [v["status"] for v in _staged(sb)] == ["open"]
    # Review 2, finding 1, kept by frame 339's review 1, finding 6: the
    # fault note of seq 20 lands in `faults`, as on the night.
    assert "fault" in out[20], out[20]
    assert [w for w in sb.ctx.writes if w[0] == "faults"]
    sha = out[16]["head_commit"]
    db.execute("UPDATE batches SET head_commit = ? WHERE id = 'bg_3'", (sha,))
    db.execute("INSERT INTO touch_strays (batch_id, commit_sha, path, status, note) "
               "VALUES ('bg_3', ?, ?, ?, ?)", (sha, *STRAY))
    db.execute("INSERT INTO verdicts (id, batch_id, commit_sha, result) VALUES "
               "('v1','bg_3',?,'pass')", (sha,))
    db.commit()
    from rota.core import lifecycle
    from rota.core import predicates as P
    assert lifecycle.mergeable(db, "bg_3") == f"touch strayed, unjudged: {STRAY[0]}"
    assert [(w.role, w.kind, w.detail) for w in P.touch_strayed(db)] == [
        ("architect", "tick:touch_strayed", f"{STRAY[0]} ({STRAY[2]})")]


def test_s279s_seq_17_note_from_the_night_database_is_refused(db, tmp_path):
    """The note of seq 17 as `tool_calls` and `turns` of
    `.rota/clickI_night158.db` hold it. The kind door answered it on the
    night. The drop note's door now answers first, and the note stays open."""
    sb, _root = _developer(db, tmp_path)
    _call(sb, "code.write", path=PATH, start=540, end=555, text=ECHO)
    sb.begin_reply()
    with pytest.raises(ValueError) as err:
        sb.call("ledger.log", about_ref="src/click/decorators.py",
                about_table="version_option callback",
                assumption="removed ctx.exit() at line 550 which was "
                           "unreachable after echo()", kind="assumption")
    assert str(err.value) == LEDGER
    assert PATH in api._open_notes(sb.ctx)
    assert not [w for w in sb.ctx.writes if w[0] == "ledger"]


def test_the_removal_lands_when_a_criterion_asks_for_it(db, tmp_path):
    """A criterion of the batch names `ctx.exit()` and asks for its removal.
    The criterion is a ruling, so the commit of seq 16 lands, and the notes land.
    Pass 4: the criterion asks in the request form. "the callback no longer
    calls ctx.exit()" states a fact, as the bug shape of review 3 does."""
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('cr_4','tk1',"
               "'After --version, the callback must no longer call ctx.exit(), so "
               "the command body runs.')")
    db.commit()
    sb, _root = _developer(db, tmp_path)
    out = _replay(sb)
    assert out[16]["committed"] is True
    assert "refused" not in out[23]
    assert _strays(sb) == []


def _ruling(db, per_item: dict, words: str) -> None:
    """One landed ruling. A value is a verdict word or the object form of
    `rulings.rule`, with its act and target (the seam design, 2.1)."""
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_text, seq) VALUES ('m1','t1','principal','liaison','answer',"
               "'x',1)")
    flat = {r: v if isinstance(v, str) else v["verdict"] for r, v in per_item.items()}
    db.execute("INSERT INTO rulings (id, ask_id, per_item, words, status) VALUES "
               "('r1','m1',?,?,'landed')", (json.dumps(flat), words))
    insert_ruling_rows(db, ruling_rows(db, "r1", None, per_item, words=words))
    db.commit()


REMOVE_EXIT = {"verdict": "approve", "act": "remove", "target": "ctx.exit()",
               "words": "Take ctx.exit() out of the version callback."}


def test_the_removal_lands_when_the_principal_asks_for_it_on_the_items_page(db, tmp_path):
    """A landed ruling on the item's page removes the line by its act and
    target: his ruling grants the removal, so the commit lands."""
    _ruling(db, {"version_option_show_python": REMOVE_EXIT},
            "Take ctx.exit() out of the version callback.")
    sb, _root = _developer(db, tmp_path)
    assert _replay(sb)[16]["committed"] is True
    assert _strays(sb) == []


def test_his_words_with_no_act_grant_no_removal(db, tmp_path):
    """The seam design, pass 4: the words alone grant nothing. A ruling with
    no act leaves the removal a stray for the Architect."""
    _ruling(db, {"version_option_show_python": "approve"},
            "Take ctx.exit() out of the version callback.")
    sb, _root = _developer(db, tmp_path)
    assert _replay(sb)[16]["committed"] is True
    assert _strays(sb) == [STRAY]


@pytest.mark.parametrize("words", [
    "The callback must still call ctx.exit() after the echo.",
    "The callback calls ctx.exit() after the echo.",
])
def test_a_criterion_that_demands_or_mentions_the_line_admits_nothing(db, tmp_path, words):
    """Review 1's probe P2c: a criterion that demands the line, or only
    mentions it, asks for no removal, so the removal is a stray."""
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('cr_4','tk1',?)",
               (words,))
    db.commit()
    sb, _root = _developer(db, tmp_path)
    assert _replay(sb)[16]["committed"] is True
    assert _strays(sb) == [STRAY]


@pytest.mark.parametrize("words,lands", [
    ("Do not remove ctx.exit().", False),
    ("Never drop ctx.exit() from the callback.", False),
    ("Without show_python, the option must call ctx.exit().", False),
    ("Remove the ctx.exit() call.", True),
])
def test_a_sentence_that_forbids_the_removal_admits_nothing(db, tmp_path, words, lands):
    """Review 2's finding 2: a negated removal word, or "without" that a
    name does not follow, admits nothing. A plain ask admits the removal.
    Frame 339: both commits land, and only the unadmitted one is a stray."""
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('cr_4','tk1',?)",
               (words,))
    db.commit()
    sb, _root = _developer(db, tmp_path)
    out = _replay(sb)
    assert out[16]["committed"] is True
    assert _strays(sb) == ([] if lands else [STRAY])


def test_a_ruled_removal_commits_in_the_same_reply(db, tmp_path):
    """Review 2's finding 4: a removal that a criterion asks for passes the
    first door in the write's own reply, so the two doors agree."""
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('cr_4','tk1',"
               "'Remove the ctx.exit() call from the version callback.')")
    db.commit()
    sb, _root = _developer(db, tmp_path)
    out = sb.call("code.write", path=PATH, start=540, end=555, text=ECHO)
    assert "dropped" in out
    assert sb.call("code.commit", message=MESSAGE)["committed"] is True


def test_a_ruling_of_another_item_admits_nothing(db, tmp_path):
    """Review 1's probe P2b: only the rulings of the batch's own item count."""
    db.execute("INSERT INTO items (id, text, kind) VALUES "
               "('echo_json', 'Add echo_json.', 'in_scope')")
    _ruling(db, {"echo_json": REMOVE_EXIT}, "Take ctx.exit() out of the version callback.")
    sb, _root = _developer(db, tmp_path)
    assert _replay(sb)[16]["committed"] is True
    assert _strays(sb) == [STRAY]


def _restored_row(db, root, line, owner, gone_text, note=""):
    (root / PATH).write_bytes(gone_text.encode("utf-8"))
    db.execute("INSERT INTO drop_notes (batch_id, path, status, note, lines, defs, "
               "whole, noted) VALUES ('bg_3', ?, 'restored', ?, ?, '[]', '[]', '')",
               (PATH, note, json.dumps([[owner, line, 1]])))
    db.commit()
    return build("developer", db, batch_id="bg_3", mode="tests_failing",
                 allow=prompts.mode_tools("developer", "tests_failing"))


def test_a_restored_row_with_the_line_gone_from_the_tree_lands_as_a_stray(db, tmp_path):
    """The door reads the tree, not the row. A landed row at `restored`
    with `ctx.exit()` absent from the uncommitted tree was refused on
    b889c93d. Frame 339: the commit lands with one open stray."""
    _sb, root = _developer(db, tmp_path)
    text = BASE.decode("utf-8")
    gone = text.replace("        )\n        ctx.exit()\n", "        )\n", 1)
    assert gone != text
    sb = _restored_row(db, root, "ctx.exit()", "version_option.callback", gone,
                       "This write removes or rewrites 1 statement that your text does not "
                       "hold: `ctx.exit()` at line 550.")
    out = sb.call("code.commit", message="micro")
    assert out["committed"] is True
    assert _git(root, "rev-parse", "HEAD") == out["head_commit"]
    assert _strays(sb) == [STRAY]


def test_a_removal_of_an_earlier_commit_is_raised_on_the_new_head(db, tmp_path):
    """Review 1's finding 3, probe P5b: HEAD already lacks the line. An
    unrelated edit of the path lands, and the removal is raised again on
    the new head, so the merge of that head waits for the Architect."""
    _sb, root = _developer(db, tmp_path)
    text = BASE.decode("utf-8")
    gone = text.replace("        )\n        ctx.exit()\n", "        )\n", 1)
    (root / PATH).write_bytes(gone.encode("utf-8"))
    _git(root, "commit", "-q", "-am", "the removal")
    sb = _restored_row(db, root, "ctx.exit()", "version_option.callback",
                       gone + "\n# kept\n",
                       "This write removes or rewrites 1 statement that your text does not "
                       "hold: `ctx.exit()` at line 550.")
    out = sb.call("code.commit", message="micro")
    assert out["committed"] is True
    assert _strays(sb) == [STRAY]


@pytest.mark.parametrize("words,lands", [
    ("Drop the return.", False),
    ("In callback, drop the early return.", True),
])
def test_a_bare_return_needs_its_function_named(db, tmp_path, words, lands):
    """Review 1's probe P2d: a bare `return` is admitted only on a sentence
    that names its function and asks for the removal. An unadmitted one is
    a stray (frame 339)."""
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('cr_4','tk1',?)",
               (words,))
    db.commit()
    _sb, root = _developer(db, tmp_path)
    text = BASE.decode("utf-8")
    gone = text.replace("ctx.resilient_parsing:\n            return\n",
                        "ctx.resilient_parsing:\n            pass\n", 1)
    assert gone != text
    sb = _restored_row(db, root, "return", "version_option.callback", gone)
    assert sb.call("code.commit", message="micro")["committed"] is True
    assert [r[0] for r in _strays(sb)] == (
        [] if lands else ["src/click/decorators.py::version_option.callback"])


def test_a_restored_row_with_the_line_in_the_tree_lets_the_commit_land(db, tmp_path):
    """A row at `restored` whose line the tree holds blocks nothing."""
    _sb, root = _developer(db, tmp_path)
    sb = _restored_row(db, root, "ctx.exit()", "version_option.callback",
                       BASE.decode("utf-8") + "\n# kept\n")
    assert sb.call("code.commit", message="micro")["committed"] is True


GONE = {"line": "ctx.exit()", "owner": "version_option.callback", "no": "550",
        "def": False}


@pytest.mark.parametrize("words,asks", [
    # Review 3's finding 1: a negation before the clause break does not count.
    ("The ctx.exit() call is not reached after echo, so please remove ctx.exit().", True),
    ("Keep the echo, and take ctx.exit() out of the callback.", True),
    ("The callback still calls ctx.exit(), which I asked you to drop.", True),
    ("It isn't needed after echo, so you can drop ctx.exit().", True),
    ("Please remove ctx.exit() and keep the echo.", True),
    ("The callback must no longer call ctx.exit().", True),
    # Review 3's finding 2: a removal named as a fault or a consequence.
    ("Removing ctx.exit() is a bug.", False),
    ("Fix the callback rather than drop ctx.exit().", False),
    ("You were wrong to drop ctx.exit().", False),
    ("Without ctx.exit(), the program runs the command after it prints the version.", False),
    ("The callback no longer calls ctx.exit() after echo, and that is the bug.", False),
])
def test_a_removal_is_read_in_its_own_clause_and_in_the_request_form(words, asks):
    """Review 3's probe Q2: the principal's shapes from nights 140 to 158,
    rewritten to name `ctx.exit()`. Only a request in the removal word's
    own clause asks for the removal."""
    assert api._asks_removal(words, GONE) is asks


@pytest.mark.parametrize("words,asks", [
    # Review 4's finding 1: the name of the kept line sits outside the
    # request clause.
    ("Keep ctx.exit(), and remove the extra echo.", False),
    ("Do not remove ctx.exit(), but drop the blank line.", False),
    ("Do not touch ctx.exit(); remove the comment above it.", False),
    ("ctx.exit() must stay, so please delete the debug print.", False),
    # Review 4's finding 3: "stop" asks for a removal only before a gerund.
    ("Stop the command after ctx.exit() runs.", False),
    ("Please stop calling ctx.exit() after the echo.", True),
    # A pronoun takes its name from the clause before the request.
    ("ctx.exit() is dead, so drop it.", True),
])
def test_the_name_sits_in_the_request_clause(words, asks):
    """Review 4's findings 1 and 3: the request clause names the statement,
    or its pronoun refers to the clause before it."""
    assert api._asks_removal(words, GONE) is asks


@pytest.mark.parametrize("words", [
    # Review 5's finding 1: a verb after "and" or a comma starts a new clause.
    "Remove the echo and make sure ctx.exit() runs.",
    "Remove the echo and then call ctx.exit().",
    "Drop echo(message), call ctx.exit() last.",
    # Review 5's finding 2: a name after a position or an exception word is
    # not the target.
    "Remove the line above ctx.exit().",
    "Remove echo(message) before ctx.exit().",
    "Remove the echo next to ctx.exit().",
    "Remove echo(message) instead of ctx.exit().",
    "Remove echo(message) rather than ctx.exit().",
    "Remove echo(message) except ctx.exit().",
    "Remove echo(message), not ctx.exit().",
])
def test_a_name_past_the_request_is_not_its_target(words):
    """Review 5's findings 1 and 2: `ctx.exit()` sits after the request
    clause ends, so the sentence asks for no removal of `ctx.exit()`."""
    assert api._asks_removal(words, GONE) is False


@pytest.mark.parametrize("words", [
    # Review 6's finding 1: any word that is not a noun ends the clause.
    "Remove the echo and ensure ctx.exit() runs.",
    "Remove the echo and move ctx.exit() to the end.",
    "Remove the echo and test that ctx.exit() still runs.",
    "Remove the echo, move ctx.exit() to the end.",
    "Remove the echo and just call ctx.exit() last.",
    # Review 6's finding 2.
    "Remove the echo that ctx.exit() follows.",
    "Remove the echo near ctx.exit().",
])
def test_a_clause_continues_past_and_only_onto_a_noun(words):
    """Review 6: after "and", "and then" or a comma, only a noun-like word
    keeps the request clause open."""
    assert api._asks_removal(words, GONE) is False


def test_that_as_a_determiner_keeps_the_target():
    """"that" ends the target only after a noun. Nights 143, 144 and 154
    say "please drop that line"."""
    assert api._asks_removal("Please remove that ctx.exit() call.", GONE) is True


def test_night_152_and_just_say_ends_the_request():
    """Review 6's probe N, night 152: "and just say" starts a new clause."""
    s = ('Line 4 contradicts itself: if stdin is still open there is no end of '
         'input, so drop "regardless of EOF state" and just say confirm '
         'prompts as usual.')
    assert [c.strip() for c in api._removal_spans(s)] == [
        'drop "regardless of EOF state"']


@pytest.mark.parametrize("words", [
    "Remove echo(message) and ctx.exit().",
    "Remove the echo(message) line and the ctx.exit() call.",
])
def test_remove_two_names_admits_both(words):
    """Review 5 and 6: "Remove X and Y" still asks for both removals."""
    echo = {"line": "echo(message)", "owner": "version_option.callback",
            "no": None, "def": False}
    assert api._asks_removal(words, GONE) is True
    assert api._asks_removal(words, echo) is True


def test_a_later_line_after_a_comma_and_a_verb_is_not_asked():
    """Review 5's finding 1, probe M: the line of the second clause stays."""
    third = {"line": "x = 3", "owner": "f", "no": "3", "def": False}
    first = {"line": "x = 1", "owner": "f", "no": "1", "def": False}
    words = "Please drop x = 1, rewrite x = 3 in plain words."
    assert api._asks_removal(words, first) is True
    assert api._asks_removal(words, third) is False


def test_drop_one_and_keep_the_other_admits_the_dropped_one_only():
    """Review 4's finding 2: "Drop X, and keep Y" admits X only."""
    words = "Drop ctx.exit(), and keep echo(message)."
    echo = {"line": "echo(message)", "owner": "version_option.callback",
            "no": None, "def": False}
    assert api._asks_removal(words, GONE) is True
    assert api._asks_removal(words, echo) is False


def test_the_same_reply_refusal_says_its_fact_once_and_gives_the_route(db, tmp_path):
    """Review 3's finding 3: the same-reply refusal says once that the seat
    did not read the note. Frame 339: its step ends on the commit route,
    which keeps the change for the Architect."""
    sb, _root = _developer(db, tmp_path)
    assert "dropped" in sb.call("code.write", path=PATH, start=540, end=555, text=ECHO)
    with pytest.raises(ValueError) as err:
        sb.call("code.commit", message=MESSAGE)
    msg = str(err.value)
    assert "You sent this commit" not in msg
    assert msg.count("you had not read it") == 1
    assert msg.endswith("If the tree holds those lines again, commit in your "
                        "next reply. A note does not close a removal. To undo "
                        "the change, put the lines back with code.write, then "
                        "commit in your next reply. To keep the change, commit "
                        "in your next reply. The Architect then judges the "
                        "removal before the batch merges.")


