"""
Fact F33 of `plans/rootfix-audit-2026-10-27-b.md`: a debt names its open frame.

A debt is a test that the suite excuses today. It is a strict xfail, an id
in `OWED`, or a line of `KNOWN_REFUSED_OFFERS`. Each debt names the frame
that owes its fix. `state.open_frames` is the one reader that says a frame
is still open. A debt that names a closed frame, or no frame, owes work that
no frame holds, so a later session cannot find the owner.
"""
from __future__ import annotations

import ast
import re
import warnings
from dataclasses import dataclass
from pathlib import Path

import pytest

from rota.testkit import fixtures, scenes
from rota.tools import state
from rota.tools.casestatus import red_by_construction
from tests.rota import conftest
from tests.rota.test_case_reachability import OWED, OWED_FRAME

ROOT = Path(__file__).resolve().parents[2]
TESTS = ROOT / "tests"
STACK = ROOT / "plans" / "stack.md"
FRAME = re.compile(r"\bframe (\d+)\b", re.IGNORECASE)
XFAIL = {"pytest.mark.xfail", "pytest.xfail"}


@dataclass
class Mark:
    """One xfail call in the source of the suite."""

    rel: str
    line: int
    func: str
    reason: ast.expr | None
    tree: ast.Module


def _dotted(node: ast.expr) -> str:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def _parse(path: Path) -> ast.Module:
    # A test file with a bad escape in a plain string warns on each parse.
    # The warning belongs to that file's own run, not to this reader.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        return ast.parse(path.read_bytes())


def marks() -> list[Mark]:
    """Every `pytest.mark.xfail(...)` and `pytest.xfail(...)` under tests/."""
    out = []
    for path in sorted(TESTS.rglob("*.py")):
        tree = _parse(path)
        rel = path.relative_to(ROOT).as_posix()

        def visit(node: ast.AST, func: str) -> None:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func = node.name
            if isinstance(node, ast.Call) and _dotted(node.func) in XFAIL:
                reason = next((k.value for k in node.keywords if k.arg == "reason"), None)
                if reason is None and _dotted(node.func) == "pytest.xfail" and node.args:
                    reason = node.args[0]
                out.append(Mark(rel, node.lineno, func, reason, tree))
            for child in ast.iter_child_nodes(node):
                visit(child, func)

        visit(tree, "")
    return out


def _static(node: ast.expr | None) -> tuple[str, bool]:
    """The constant words of a reason, and whether a part of it is computed."""
    if node is None:
        return "", False
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value, False
    if isinstance(node, ast.JoinedStr):
        words = "".join(v.value for v in node.values
                        if isinstance(v, ast.Constant) and isinstance(v.value, str))
        return words, any(isinstance(v, ast.FormattedValue) for v in node.values)
    return "", True


def _module_dict(tree: ast.Module, name: str) -> dict[str, str] | None:
    """A module-level dict literal of string keys and values, by its name."""
    for node in tree.body:
        targets = (node.targets if isinstance(node, ast.Assign)
                   else [node.target] if isinstance(node, ast.AnnAssign) else [])
        if any(isinstance(t, ast.Name) and t.id == name for t in targets):
            if isinstance(node.value, ast.Dict):
                return {ast.literal_eval(k): ast.literal_eval(v)
                        for k, v in zip(node.value.keys, node.value.values)}
    return None


def _subscript_debts(mark: Mark) -> list[tuple[str, str]] | None:
    """A reason `TABLE[key]` reads each value of the module's TABLE."""
    node = mark.reason
    if not (isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name)):
        return None
    table = _module_dict(mark.tree, node.value.id)
    if table is None:
        return None
    return [(f"{mark.rel} {node.value.id}[{k!r}]", v) for k, v in table.items()]


def _scene_calls() -> list[tuple[str, str]]:
    return [(f"scenes.{c.scene}: {c.name}", c.held)
            for c in scenes.catalogue() + scenes.sweep() if c.held]


def _scene_invariants() -> list[tuple[str, str]]:
    """The `known=` dicts that the scene test files give to `make`."""
    out = []
    for path in sorted(TESTS.rglob("*.py")):
        for node in ast.walk(_parse(path)):
            if isinstance(node, ast.keyword) and node.arg == "known" \
                    and isinstance(node.value, ast.Dict):
                rel = path.relative_to(ROOT).as_posix()
                out += [(f"{rel} known[{ast.literal_eval(k)!r}]", ast.literal_eval(v))
                        for k, v in zip(node.value.keys, node.value.values)]
    return out


def _red_cases() -> list[tuple[str, str]]:
    out = []
    for path in sorted((TESTS / "rota" / "cases").glob("l*.yaml")):
        for case in fixtures.load_case(path) or []:
            red = red_by_construction(case)
            if red:
                out.append((f"case {case['id']} red:", red))
    return out


#: The xfail sites whose reason the code computes, and the reader of the data
#: that the reason comes from. A new computed reason must join this table, or
#: the completeness test goes red.
DYNAMIC = {
    ("tests/rota/scene_tests.py", "_param"): _scene_calls,
    ("tests/rota/scene_tests.py", "_invariant"): _scene_invariants,
    ("tests/rota/test_l1.py", "test_l1_case"): _red_cases,
}


def debts() -> list[tuple[str, str]]:
    """Every debt of the suite: its name, and the words that name its frame."""
    out: list[tuple[str, str]] = []
    for mark in marks():
        if (mark.rel, mark.func) in DYNAMIC:
            continue
        resolved = _subscript_debts(mark)
        if resolved is not None:
            out += resolved
            continue
        words, _ = _static(mark.reason)
        out.append((f"{mark.rel}:{mark.line}", words))
    for read in DYNAMIC.values():
        out += read()
    out.append((f"OWED ({len(OWED)} ids) tests/rota/test_case_reachability.py",
                OWED_FRAME))
    out += [(f"KNOWN_REFUSED_OFFERS {test} :: {words}", frame)
            for (test, words), frame in conftest.KNOWN_REFUSED_OFFERS.items()]
    return out


def faults(found: list[tuple[str, str]], open_: set[int]) -> dict[str, list[str]]:
    """The debts that name no frame, and the debts that name a closed frame.

    Every frame a debt names must be open. A debt that cites a closed frame
    as its owner points a later session at work that nobody holds.
    """
    out: dict[str, list[str]] = {"no frame": [], "closed frame": []}
    for name, words in found:
        named = {int(n) for n in FRAME.findall(words)}
        if not named:
            out["no frame"].append(name)
        elif named - open_:
            out["closed frame"].append(
                f"{name} (frame {', '.join(map(str, sorted(named - open_)))})")
    return out


def _stack(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "stack.md"
    path.write_bytes(text.encode("utf-8"))
    return path


def test_open_frames_reads_every_frame_of_the_stack_held_or_parked(tmp_path):
    stack = _stack(tmp_path, (
        "# Stack page\n## Stack\n### 5. A held frame (aaaaaaaa)\n- Site: x.\n"
        "## The batches\n### 6. A frame under another section\n"
        "## Parked\n### 7. A parked frame\n- Status 2026-10-28 01:00 (aaaaaaaa): parked\n"))
    assert state.open_frames(stack) == {5, 6, 7}


def test_a_debt_that_names_a_closed_frame_or_none_is_a_fault():
    found = [("held", "held by frame 130: a wall"), ("closed", "finding of frame 144"),
             ("none", "residue: a build verb"), ("mixed", "frame 130 and frame 9")]
    assert faults(found, {130}) == {"no frame": ["none"],
                                    "closed frame": ["closed (frame 144)", "mixed (frame 9)"]}


def test_the_debt_readers_find_the_owed_set_and_the_refused_offers():
    names = [name for name, _ in debts()]
    assert any(n.startswith("OWED ") for n in names)
    assert sum(n.startswith("KNOWN_REFUSED_OFFERS ") for n in names) \
        == len(conftest.KNOWN_REFUSED_OFFERS)
    assert all(FRAME.fullmatch(v) for v in conftest.KNOWN_REFUSED_OFFERS.values())
    assert FRAME.fullmatch(OWED_FRAME)


def test_every_computed_xfail_reason_has_a_reader():
    """The completeness pin. A computed reason that no reader resolves would
    hide its frame from the test below."""
    sites = {(m.rel, m.func) for m in marks()}
    assert set(DYNAMIC) <= sites, f"DYNAMIC names no mark at {sorted(set(DYNAMIC) - sites)}"
    unread = [f"{m.rel}:{m.line}" for m in marks()
              if (m.rel, m.func) not in DYNAMIC and _static(m.reason)[1]
              and _subscript_debts(m) is None]
    assert not unread, f"add a reader to DYNAMIC for the computed reason at {unread}"


def test_one_reader_of_the_stack_frames():
    """The one-reader pin. Only `rota/tools/state.py` reads a frame heading
    of the stack, and it defines `open_frames` once."""
    needle = "### " + "(" + "\\d"
    holders = sorted(p.relative_to(ROOT).as_posix()
                     for top in ("rota", "tests") for p in (ROOT / top).rglob("*.py")
                     if needle in p.read_bytes().decode("utf-8", "replace"))
    assert holders == ["rota/tools/state.py"], holders
    defs = sorted(p.relative_to(ROOT).as_posix()
                  for top in ("rota", "tests") for p in (ROOT / top).rglob("*.py")
                  if "def " + "open_frames(" in p.read_bytes().decode("utf-8", "replace"))
    assert defs == ["rota/tools/state.py"], defs


#: The debts that name a closed frame or no frame, at 5b59b63a. The F33 pass
#: names each one in its report, and a later session moves each debt to an
#: open frame and takes its name out of this list. A new name goes red here,
#: as `OWED_CEILING` does. A strict xfail hid a new debt until all 28 moved
#: (the F33 review, finding 1).
FRAMELESS_CEILING = frozenset({
    'KNOWN_REFUSED_OFFERS tests/rota/test_desk_guards.py::test_a_span_from_a_blank_line_before_else_is_refused_with_an_offer :: m.py is not valid Python (frame 144)',
    'KNOWN_REFUSED_OFFERS tests/rota/test_desk_guards.py::test_a_span_from_the_top_into_the_first_statement_gets_no_moved_boundary :: m.py is not valid Python (frame 144)',
    'KNOWN_REFUSED_OFFERS tests/rota/test_desk_guards.py::test_a_start_on_a_decorated_def_line_names_the_decorators :: m.py defines f twice (frame 144)',
    'KNOWN_REFUSED_OFFERS tests/rota/test_offers_followed.py::test_a_crash_of_one_offer_keeps_the_records_of_the_others :: MemoryError (frame 144)',
    'KNOWN_REFUSED_OFFERS tests/rota/test_offers_followed.py::test_a_cut_at_deep_decorators_gets_the_refusal_of_b2ed55b[attr2000] :: m.py defines a twice (frame 144)',
    'KNOWN_REFUSED_OFFERS tests/rota/test_offers_followed.py::test_a_cut_at_deep_decorators_gets_the_refusal_of_b2ed55b[minus400] :: m.py defines a twice (frame 144)',
    'KNOWN_REFUSED_OFFERS tests/rota/test_offers_followed.py::test_a_cut_at_deep_decorators_gets_the_refusal_of_b2ed55b[spaced] :: m.py defines a twice (frame 144)',
    'KNOWN_REFUSED_OFFERS tests/rota/test_offers_followed.py::test_a_cut_refusal_quotes_lines_that_are_true :: m.py is not valid Python (frame 144)',
    'KNOWN_REFUSED_OFFERS tests/rota/test_offers_followed.py::test_a_decorator_line_off_by_one_reads_false_on_a_twin_decorator :: m.py defines a twice (frame 144)',
    'KNOWN_REFUSED_OFFERS tests/rota/test_offers_followed.py::test_a_session_records_no_offer_and_a_test_records_frames :: m.py is not valid Python (frame 144)',
    'KNOWN_REFUSED_OFFERS tests/rota/test_offers_followed.py::test_a_text_that_breaks_the_parser_gets_the_cut_refusal :: MemoryError (frame 144)',
    'KNOWN_REFUSED_OFFERS tests/rota/test_offers_followed.py::test_the_add_after_offer_of_a_cut_span_is_admitted :: m.py defines f twice (frame 144)',
    'case L1-TE-log-the-word-you-took-one-way red:',
    'tests/rota/test_chaos_confirm.py:163',
    "tests/rota/test_f25_offers_in_mode.py KNOWN_UNHELD['_revert_refusal:msg.challenge_tester']",
    "tests/rota/test_f25_offers_in_mode.py KNOWN_UNHELD['_revert_refusal:msg.escalate_architect']",
    "tests/rota/test_f25_offers_in_mode.py KNOWN_UNHELD['glossary_amend:surveys.attest']",
    "tests/rota/test_f25_offers_in_mode.py KNOWN_UNHELD['ledger_log:surveys.attest']",
    "tests/rota/test_f25_offers_in_mode.py KNOWN_UNHELD['surveys_attest:problem.assert']",
    "tests/rota/test_f25_offers_in_mode.py KNOWN_UNHELD['tests_encode:ledger.log']",
    "tests/rota/test_f25_offers_in_mode.py KNOWN_UNHELD['tests_encode:schedule.reask']",
    'tests/rota/test_frame234_verdict_lines.py:885',
    'tests/rota/test_frame234_verdict_lines.py:898',
    'tests/rota/test_frame234_verdict_lines.py:939',
    'tests/rota/test_frame234_verdict_lines.py:945',
    'tests/rota/test_offers_followed.py:186 (frame 144)',
    'tests/rota/test_offers_followed.py:226 (frame 144)',
    'tests/rota/test_toolproto_quotes.py:757',
})


def test_each_debt_names_an_open_frame():
    found = faults(debts(), state.open_frames(STACK))
    new = {kind: [n for n in names if n not in FRAMELESS_CEILING]
           for kind, names in found.items()}
    assert new == {"no frame": [], "closed frame": []}, (
        "a debt must name an open frame of plans/stack.md:\n"
        + "\n".join(f"{kind}: {name}" for kind, names in new.items() for name in names))
