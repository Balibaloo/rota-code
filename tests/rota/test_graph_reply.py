"""
Every asking verb has a reply, and the mode that receives it can send one.

Finding 73 (night 69, 2026-09-14): the Critic challenged the Tester and the
Tester's challenge mode had no answer verb to the Critic. The graph had no
tester-to-critic answer edge, so the sandbox dropped every answer verb, and the
review re-fired until quarantined. The data was there; the assertion was not
(Roman, 2026-09-15). An asking edge carries `expects: answer` in the graph.
"""
import json

import pytest

from rota import paths
from rota.roles import prompts


def _edges():
    g = json.loads((paths.REPO / "rota/design/graph.json").read_text(encoding="utf-8"))
    return [e for e in g["edges"] if e.get("type") == "messages"]


def _asking():
    return [e for e in _edges() if e.get("expects")]


REPLY_TOOL = {"commit": "code.commit", "decision": "decisions.author"}


def test_asking_verbs_are_marked():
    """question, challenge and escalate expect a reply; the mark on the edge says
    which kind: an answer message, the next commit (the Developer's challenge
    brief: a judge that can be talked round is not one), or a decision (the
    Vision Keeper's challenge brief: amend, or author a decision saying why)."""
    unmarked = [(e["s"], e["t"], e["v"]) for e in _edges()
                if e["v"] in ("question", "challenge", "escalate") and e.get("expects") not in ("answer", "commit", "decision")]
    assert not unmarked, unmarked


@pytest.mark.parametrize("edge", _asking(), ids=lambda e: f"{e['s']}-{e['v']}-{e['t']}")
def test_an_asking_edge_has_its_reply(edge):
    """A message wake is keyed by its verb (runner._mode_key), so the mode that
    receives a challenge is `challenge`. For `answer`: an answer edge back, and
    msg.answer_<sender> in the mode's list when it is narrowed (the sandbox
    keeps that one and drops the rest). For `commit` and `decision`: the tool
    that makes the reply is in the list."""
    role, verb, sender, kind = edge["t"], edge["v"], edge["s"], edge["expects"]
    assert verb in prompts.available(role), f"{role} has no mode for a {verb} from {sender}"
    tools = prompts.mode_tools(role, verb)
    if kind == "answer":
        answers = {(e["s"], e["t"]) for e in _edges() if e["v"] == "answer"}
        assert (role, sender) in answers, (
            f"{sender} sends {verb} to {role} and the graph has no {role} -> {sender} "
            f"answer edge: the question can never be answered")
        want = f"msg.answer_{sender}"
    else:
        want = REPLY_TOOL[kind]
    if tools is not None:
        assert want in tools, (
            f"{role}/{verb} offers {sorted(tools)}; a {verb} from {sender} expects "
            f"{kind} and {want} is not in the list")
