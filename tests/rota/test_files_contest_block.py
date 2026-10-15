"""
Frame 244: the Architect's re-annotate after a files contest.

On night 148, s152 kept the ten `tests/test_defaults.py` grains after the
principal said that they have nothing to do with confirm. Try 2's shape E
moved s152 in 5 of 5 and s119 in 3 of 5, and broke 0 of 15 right calls
(`plans/frame244-try-2.md`, 2026-10-15). Shape E puts his words in a block
under the touch list and gives the annotate brief one sentence on a dispute.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.runner import build_prompt
from rota.core.sandbox import build
from rota.core.scheduler import Wake
from rota.roles import prompts


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    yield conn
    conn.close()


# s152's wake on m53, night 148: the message as the night's turn 1 shows it
# (`.rota/clickI_night148.db`, `turns` seq 1, read on 2026-10-15).
S152_SAID = (
    "Line 5 looks wrong. The tests it lists in the defaults test file are about "
    "default maps for options, and they have nothing to do with confirm, so I'd "
    "expect the new tests to go with the other confirm and prompt tests instead. "
    "Touching confirm itself and the testing stdin helper makes sense to me.")
S152_EXPECTED = [
    "src/click/termui.py::confirm",
    "src/click/testing.py::EchoingStdin",
    "tests/test_defaults.py::test_basic_defaults",
    "tests/test_defaults.py::test_default_map_nargs",
    "tests/test_defaults.py::test_default_map_source",
    "tests/test_defaults.py::test_default_map_with_callable_flag_value",
    "tests/test_defaults.py::test_flag_default_map",
    "tests/test_defaults.py::test_lookup_default_override_respected",
    "tests/test_defaults.py::test_lookup_default_returns_hides_sentinel",
    "tests/test_defaults.py::test_multiple_defaults",
    "tests/test_defaults.py::test_multiple_flag_default",
    "tests/test_defaults.py::test_shared_param_prefers_first_default",
]


def _s152_inbound(verdict: str = "contest") -> dict:
    return {
        "from": "liaison",
        "verb": "relay",
        "refs": ["bg_2"],
        "principal_verdict": {"bg_2": verdict},
        "principal_said": S152_SAID,
        "touch": {
            "bg_2": {
                "batch": "bg_2",
                "status": "pending",
                "item": {
                    "id": "confirm_default_on_eof",
                    "text": ("Let confirm() take a default_on_eof flag: when stdin "
                             "is closed it returns the default instead of aborting."),
                },
                "expected": list(S152_EXPECTED),
                "possible": [],
                "unsurveyed": [],
                "commitments": [],
                "disputed": [],
            },
        },
    }


PUSHED = {"batches.consult": [
    {"id": "bg_2", "item_id": "confirm_default_on_eof", "status": "pending",
     "priority": 1}]}


def _user(db, inbound: dict) -> str:
    sb = build("architect", db, mode="annotate",
               allow=prompts.mode_tools("architect", "annotate"))
    wake = Wake("architect", "message", message_id="m53", detail="relay")
    _system, user = build_prompt("architect", sb, wake, PUSHED,
                                 "MODE: annotate", inbound=inbound)
    return user


NO_DISPUTED = ("The principal said that some of the files above have nothing "
               "to do with this change. His words name them. Leave them out.")
DISPUTED = ("The principal said these files have nothing to do with this "
            "change. Leave them out:")


def test_s152s_wake_shows_his_words_under_the_touch_list(db):
    """The words leave `principal_said` and stand under the touch list. Pass 2
    of frame 244 lists no path of `expected`: the night-149 interview found the
    old list read as his own list (`plans/frame244-interview-2.md`)."""
    inbound = _s152_inbound()
    user = _user(db, inbound)
    shown = {k: v for k, v in inbound.items() if k != "principal_said"}
    block = "\n".join([NO_DISPUTED, f"He said: {S152_SAID}"])
    assert ("The message that woke you:\n" + json.dumps(shown, indent=2)
            + "\n\n" + block + "\n\nAlready run for you") in user
    assert '"principal_said"' not in user
    assert user.count(S152_SAID) == 1
    # The run keeps the words for the session row: the render moves them.
    assert inbound["principal_said"] == S152_SAID


# s172's wake on m76, night 149: the message as the night's turn 1 shows it
# (`turns` seq 1, copied by session cd6300cd to `f244/i2_s172_user.txt`,
# 2026-10-15). The parser found no disputed path in his words.
S172_SAID = (
    "Lines 2, 3, 5 and 7 are wrong: today confirm aborts when stdin is closed, "
    "it doesn't raise a usage error. Lines 4 and 6 are also wrong, because it "
    "should return the default that was passed to confirm itself, not an "
    "option's default. Line 8 lists the defaults tests and the short help code "
    "in utils, which have nothing to do with this change, and it leaves out the "
    "termui tests where confirm is actually tested.")
S172_EXPECTED = [
    "src/click/termui.py",
    "src/click/termui.py::confirm",
    "src/click/utils.py",
    "src/click/utils.py::_make_default_short_help",
    "tests/test_defaults.py",
    "tests/test_defaults.py::test_basic_defaults",
    "tests/test_defaults.py::test_default_map_nargs",
    "tests/test_defaults.py::test_default_map_source",
    "tests/test_defaults.py::test_default_map_with_callable_flag_value",
    "tests/test_defaults.py::test_flag_default_map",
    "tests/test_defaults.py::test_lookup_default_callable_in_default_map",
    "tests/test_defaults.py::test_lookup_default_override_respected",
    "tests/test_defaults.py::test_lookup_default_returns_hides_sentinel",
    "tests/test_defaults.py::test_multiple_defaults",
    "tests/test_defaults.py::test_multiple_flag_default",
    "tests/test_defaults.py::test_shared_param_prefers_first_default",
    "tests/test_defaults.py::test_unset_in_default_map",
]


def _s172_inbound(disputed: list[str] | None = None,
                  expected: list[str] | None = None) -> dict:
    return {
        "from": "liaison",
        "verb": "relay",
        "refs": ["bg_2"],
        "principal_verdict": {"bg_2": "contest"},
        "principal_said": S172_SAID,
        "touch": {
            "bg_2": {
                "batch": "bg_2",
                "status": "pending",
                "item": {
                    "id": "confirm_default_on_eof",
                    "text": ("Let confirm() take a default_on_eof flag: when stdin "
                             "is closed it returns the default instead of "
                             "aborting. The flag defaults to False, so nothing "
                             "changes for people who already call confirm."),
                },
                "expected": list(S172_EXPECTED if expected is None else expected),
                "possible": [],
                "unsurveyed": [],
                "commitments": [],
                "disputed": list(disputed or []),
            },
        },
    }


def _block(user: str) -> str:
    """The text between the shown message and the pushed results."""
    head = user.split("\n\nAlready run for you", 1)[0]
    return head.rsplit("\n}\n\n", 1)[1]


def test_s172s_wake_names_no_path_when_the_parser_found_none(db):
    """Night 149: s172 read the 17 listed paths as his own list and kept the
    declined ones. With no disputed path, the block lists no path."""
    inbound = _s172_inbound()
    user = _user(db, inbound)
    block = _block(user)
    assert block == "\n".join([NO_DISPUTED, f"He said: {S172_SAID}"])
    for path in S172_EXPECTED:
        assert path not in block
    assert user.count(NO_DISPUTED) == 1
    assert user.count(S172_SAID) == 1
    assert '"principal_said"' not in user
    assert "he contested these files" not in user


def test_the_block_lists_the_disputed_paths_alone(db):
    """The parser's disputed paths are the only paths the block lists."""
    declined = ["tests/test_defaults.py", "src/click/utils.py"]
    kept = ["src/click/termui.py", "src/click/termui.py::confirm"]
    inbound = _s172_inbound(disputed=declined, expected=kept)
    user = _user(db, inbound)
    block = _block(user)
    assert block == "\n".join([DISPUTED, *declined, f"He said: {S172_SAID}"])
    for path in kept:
        assert path not in block
    assert '"principal_said"' not in user


@pytest.mark.parametrize("inbound", [
    pytest.param(_s152_inbound("approve"), id="approve on the batch"),
    pytest.param({k: v for k, v in _s152_inbound().items() if k != "touch"},
                 id="no touch list"),
    pytest.param({"from": "liaison", "verb": "relay", "refs": ["cr_1"],
                  "principal_verdict": {"cr_1": "contest"},
                  "principal_said": "Line 1 is wrong."}, id="a criterion contest"),
])
def test_a_wake_with_no_files_contest_is_as_before(db, inbound):
    """Only a contest of a batch's files moves the prompt."""
    user = _user(db, inbound)
    assert user.startswith(
        "You were woken by: message\nInbound message: m53 (relay)\n"
        "\nThe message that woke you:\n"
        + json.dumps(inbound, indent=2, default=str)
        + "\n\nAlready run for you")
    assert "he contested these files" not in user


def test_the_annotate_brief_says_what_a_dispute_is():
    """Try 2's shape C, the sentence copied as the count measured it."""
    text = prompts.piece("architect", "annotate")
    assert ("Call\n`batches.annotate` once with the paths the words name.\n"
            "A path he says has nothing to do with the item is disputed. Drop it. "
            "Keep the others. Then stop.") in text
    assert "do not dispute" not in text
