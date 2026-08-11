"""
The settings the principal owns, declared in one place.

Two rules make this file worth having rather than a scattering of literals.

**Every cap is here, or it is not a cap.** A number written into a predicate is a
decision made by whoever typed it, at a moment nobody remembers, that nobody can
change without reading code. `tests_failing` had a `< 10` in it; `boot` took its
attempt cap as an argument nobody passed. Both were policy wearing the clothes of
an implementation detail.

**A cap says what it spends.** `loop_cap` and `interrupt_cap` are both "how many
times before we stop", and it is tempting to make them one number. They are not:
one spends compute and the other spends the principal's attention. Different
resource, different scarcity, different right answer — and the moment they share
a name someone will tune one and break the other.

Run state lives here too, because stopping is a decision, not an event. Two verbs
that are easy to confuse and must not be:

    stop   drain — finish what is running, dispatch nothing more
    halt   preempt — stop now, mid-flight

Neither resumes on its own. An automatic resume would make "halted" a slow
version of "running", which is the one thing it must never be. Both leave intake
alone: recording what the principal said and answering their questions read-only
are always free, and a system that stops listening because it stopped working is
just broken.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Setting:
    key: str
    default: Any
    why: str
    values: tuple = ()          # empty means "any value of the default's type"

    def validate(self, value: Any) -> str | None:
        if self.values and value not in self.values:
            return f"{self.key}={value!r} is not one of {list(self.values)}"
        if not self.values and not isinstance(value, type(self.default)):
            return (f"{self.key} takes {type(self.default).__name__}, "
                    f"got {type(value).__name__}")
        return None


SETTINGS: dict[str, Setting] = {s.key: s for s in [
    Setting("loop_cap", 10,
            "Developer<->Tester bounces on one batch before it escalates. "
            "Spends compute, which is the cheap resource — hence generous."),

    Setting("interrupt_cap", 3,
            "Consecutive non-closing touches on the principal for one blocker "
            "before it becomes their problem to answer rather than ours to ask. "
            "Spends the principal, which is the scarce one — hence small. Every "
            "touch after the first must reframe: decompose, or offer a concrete "
            "default they can veto. Never repeat the question."),

    Setting("merge_gate", "auto",
            "Does a passing verdict merge, or wait for the principal to look? "
            "A setting they toggle, deliberately not derived from a phase — "
            "trust should not increase on a schedule.",
            values=("auto", "review")),

    Setting("contest_defences", 1,
            "How many times Gatekeeper may defend a contested item with a "
            "decision before it must amend instead. One, by default: the "
            "principal contested it, and arguing twice is not a dialogue."),

    Setting("ledger_signoff", False,
            "Whether a decision that resolves a ledger entry needs the "
            "principal's sign-off. Off by default — the ledger records "
            "assumptions taken, and most are closed by the role that took one."),

    Setting("message_attempt_cap", 3,
            "Infrastructure failures on one message before it is quarantined. "
            "Semantic failures resolve themselves; these are model evictions and "
            "dead streams, and without a bound the same message is retried "
            "across restarts forever."),

    Setting("research_cap", 6,
            "Fetches in one Researcher session before it must answer with what "
            "it has. A third scarcity, and deliberately not `loop_cap`: that one "
            "spends compute and this one spends the outside world — rate limits, "
            "and the trust surface of every page read. Sharing a name with either "
            "existing cap would let someone tune the cheap thing and change how "
            "hard this system leans on somebody else's server."),

    Setting("research_allowlist", [],
            "Domains the Researcher may fetch. Empty means it may fetch nothing, "
            "which is the right default for a capability that reaches outside the "
            "engagement: it has to be granted, never merely not-forbidden. "
            "Configuration rather than an artefact, so the principal sets it "
            "directly and 'humans do not edit artefacts' never comes under "
            "pressure. An unlisted domain is not an error — the Researcher "
            "reports what it could not reach, like any other dead end."),

    Setting("tick_attempt_cap", 3,
            "Dispatches of the same tick, unchanged, before it is quarantined. "
            "Law 4 bounds failure and bounded only messages until a real "
            "repository found the hole: a survey session that never attested "
            "left its predicate undrained, so the identical wake was produced "
            "forever -- busy, committing, writing artefacts, and never reaching "
            "area two of twelve. Worse than a dead end, which at least reports "
            "quiescence. The counter resets the moment the wake stops being "
            "produced, so a loop that is making progress is never touched."),

    Setting("run_state", "running",
            "running dispatches; stopping finishes what is running and "
            "dispatches nothing more; halted stops now. Resume is explicit.",
            values=("running", "stopping", "halted")),
]}


class UnknownSetting(KeyError):
    """A key nobody declared. Almost always a typo, and silently accepting it
    would mean the caller reads a default forever while believing otherwise."""


def get(conn: sqlite3.Connection, key: str) -> Any:
    if key not in SETTINGS:
        raise UnknownSetting(f"{key!r} is not a declared setting")
    row = conn.execute("SELECT value FROM config WHERE key = ?", (key,)).fetchone()
    return json.loads(row["value"]) if row else SETTINGS[key].default


def set(conn: sqlite3.Connection, key: str, value: Any) -> None:
    if key not in SETTINGS:
        raise UnknownSetting(f"{key!r} is not a declared setting")
    problem = SETTINGS[key].validate(value)
    if problem:
        raise ValueError(problem)
    conn.execute(
        "INSERT INTO config(key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, json.dumps(value)))


def current(conn: sqlite3.Connection) -> dict[str, Any]:
    """Every setting and its effective value — what the cockpit shows."""
    return {key: get(conn, key) for key in SETTINGS}


# ---------------------------------------------------------------------------
# Run state
# ---------------------------------------------------------------------------

def stop(conn: sqlite3.Connection) -> None:
    """Drain. Sessions in flight finish; nothing new is dispatched."""
    set(conn, "run_state", "stopping")


def halt(conn: sqlite3.Connection) -> None:
    """Preempt. Nothing further runs, including whatever was about to."""
    set(conn, "run_state", "halted")


def resume(conn: sqlite3.Connection) -> None:
    set(conn, "run_state", "running")


def dispatchable(conn: sqlite3.Connection) -> bool:
    return get(conn, "run_state") == "running"
