"""
The exit interview: what a failed session *had*, asked of the session itself.

Not a mode, deliberately. A mode is something the system wakes a role into, so
it becomes part of that role's vocabulary -- and a role that can be woken into
"explain yourself" is prose on the wire, which is the thing Law 2 forbids. This
runs in the harness, after the case has already been scored, with no tools, no
writes, no session and no commit. Nothing it produces reaches an artefact.

**It asks about inputs, never about reasons.** A model asked why it did
something writes a plausible story, and the story is convincing precisely when
it is wrong. `L1-LI-the-reports-came-back-clean` said, in its own words:

    there are some reports that have already been settled and can be crossed
    off ... status "ratified" ... this can be struck out

which reads as a role that understood its brief, and there were no reports in
its prompt at all -- the round never resolved, and it was pattern-matching the
brief's wording back at us. Taken as a self-report it would have confirmed a
brief that was doing nothing.

So every question here has an answer already on the record: the ids it held are
in `outcome.user`, the tools it had are in the sandbox, what it read is in the
call log. The interview is not evidence. The *disagreement* between the
interview and the record is evidence, and it is the cheap way to find a case
that was never possible to pass.

The expectation is withheld on purpose. Told "you should have challenged the
Gatekeeper", a model reliably answers "yes, and I lacked X" -- for any X. Ask
first, disclose second, and only the first answer counts.
"""
from __future__ import annotations

import json
import sqlite3

QUESTIONS = [
    "In one sentence, what were you asked to do?",
    "List every id you were given, exactly as they appeared. If you were given "
    "none, say `none`.",
    "Name any tool you looked for and did not have.",
    "Was there anything you needed in order to decide, and could not find? "
    "Name it, or say `nothing`.",
]

PREAMBLE = (
    "That session has ended and nothing you say now is recorded as work. "
    "You are not being asked to continue it, to justify it, or to do it "
    "better. Answer only from what was actually in front of you, and say "
    "you do not know rather than reconstructing something plausible.\n\n"
    "Answer each question on its own numbered line."
)


def build(outcome, called: list[str]) -> tuple[str, str]:
    """
    The interview prompt: its own wake, its own calls, then the questions.

    Its own prompt is quoted back rather than summarised, because the question
    being asked is what was in it -- a summary would supply the answer.
    """
    calls = ", ".join(called) or "none"
    body = [
        "This is what you were shown when you were woken:",
        "-------- 8< --------",
        outcome.user.strip(),
        "-------- >8 --------",
        f"This is what you called, in order: {calls}",
        "",
        PREAMBLE,
        "",
    ]
    body += [f"{i}. {q}" for i, q in enumerate(QUESTIONS, 1)]
    return outcome.system, "\n".join(body)


def conduct(outcome, called: list[str], backend, pins) -> str:
    """One call, no tools. Failure to answer is not a test failure."""
    system, user = build(outcome, called)
    try:
        return backend.complete(system, user, pins).text
    except Exception as exc:                      # noqa: BLE001 - diagnostics only
        return f"[interview unavailable: {exc}]"


def ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS case_interviews ("
        "  case_id TEXT, run_no INTEGER, model TEXT, prompt_hash TEXT,"
        "  problems TEXT, answers TEXT, ids_in_prompt TEXT, called TEXT,"
        "  seq INTEGER PRIMARY KEY AUTOINCREMENT)")


def record(conn: sqlite3.Connection, case_id: str, run_no: int, pins,
           problems: list[str], answers: str, ids_in_prompt: list[str],
           called: list[str]) -> None:
    """
    Stored beside the run, with the ids the prompt *actually* held.

    Both halves are kept because neither is worth much alone: the answer is a
    claim, the id list is the fact, and the whole point is reading them against
    each other.
    """
    ensure_table(conn)
    conn.execute(
        "INSERT INTO case_interviews (case_id, run_no, model, prompt_hash, "
        "problems, answers, ids_in_prompt, called) VALUES (?,?,?,?,?,?,?,?)",
        (case_id, run_no, pins.model, pins.prompt_hash, json.dumps(problems),
         answers, json.dumps(ids_in_prompt), json.dumps(called)))


def ids_in(text: str) -> list[str]:
    """
    The ids a prompt actually carried, by the shape the id generator makes.

    Deliberately mechanical. This is the side of the comparison that must not
    involve judgement, or it stops being a check on the interview and becomes a
    second opinion.
    """
    import re

    return sorted(set(re.findall(r"\b(?:[a-z]{1,3}_[0-9a-f]{6}|[a-z]{1,2}\d+)\b",
                                 text or "")))
