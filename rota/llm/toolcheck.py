"""
The provider tool check: two fixed prompts, pass or fail, before a provider
and model are listed as supported. plans/model-setup.md, step 4.

The first must answer with a `TOOL:` line, the transport every desk uses.
The second must answer with a native tool call, the transport native
function calling uses when it is on. A walk measures judgement; this
measures only that the words reach the model and a call comes back in the
shape rota reads. It is recorded like a case, under its own tier, so the
register can vouch for the provider before any walk.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import llm, toolproto

SYSTEM = (
    "You are a desk in a team. You act by calling exactly one function from "
    "your working set and nothing else.\n\n"
    "Your working set is exactly these functions. Nothing else exists:\n"
    "  TOOL: ledger.log(about_ref, about_table, assumption)\n\n"
    "Call one per line. `TOOL:` is a literal marker: write those five "
    "characters, then the function name, then its arguments in brackets, "
    "for example TOOL: artefact.verb(key='value')."
)
USER = (
    "You were woken by: tick:check\n"
    "Log one assumption about the row i_1 in the table items: that the "
    "check is running. Call ledger.log once and end."
)
SCHEMA = [{
    "type": "function",
    "function": {
        "name": "ledger.log",
        "description": "Log one assumption about a row.",
        "parameters": {
            "type": "object",
            "properties": {
                "about_ref": {"type": "string"},
                "about_table": {"type": "string"},
                "assumption": {"type": "string"},
            },
            "required": ["about_ref", "about_table", "assumption"],
        },
    },
}]

TIER = "T0-PROVIDER"


@dataclass(frozen=True)
class Result:
    tool_line: bool
    native_call: bool
    tool_line_said: str
    native_said: str

    @property
    def problems(self) -> list[str]:
        out = []
        if not self.tool_line:
            out.append("no TOOL: ledger.log line came back")
        if not self.native_call:
            out.append("no native ledger.log call came back")
        return out


def check(backend: llm.Backend, pins: llm.Pins) -> Result:
    """Run both prompts against one backend and model."""
    first = backend.complete(SYSTEM, USER, pins)
    tool_line = any(c.name == "ledger.log" for c in _lines(first.text))
    native_call = False
    native_said = ""
    try:
        second = backend.complete(SYSTEM, USER, pins, tools=SCHEMA)
        native_said = second.text
        native_call = any(getattr(c, "name", "") == "ledger.log"
                          for c in (second.tool_calls or []))
    except TypeError:
        native_said = "backend takes no tools"
    except Exception as exc:  # the provider refused the schema: a fail, recorded
        native_said = f"error: {exc}"[:300]
    return Result(tool_line, native_call, first.text[:300], native_said[:300])


def _lines(text: str) -> list:
    try:
        return toolproto.extract(text)
    except Exception:
        return []


def case_ids(profile_name: str) -> tuple[str, str]:
    return (f"{TIER}-{profile_name}-tool-line", f"{TIER}-{profile_name}-native-call")
