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
            "How many times Vision Keeper may defend a contested item with a "
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

    Setting("research_search", "none",
            "Which engine the Researcher may discover urls with, or `none`. It "
            "has `fetch`, which takes an address, and is asked questions, which "
            "are not addresses -- and with no way between the two it generated "
            "one, fetching an invented url for a real RFC and then trying to "
            "cite the page it had just been refused. Discovery is a capability "
            "like reach is, with the same default: granted, never merely "
            "not-forbidden. `cache` searches only what has already been fetched, "
            "which is what the suite uses, because a role whose tests reached "
            "the network would be the one role whose results differ by machine.",
            values=("none", "cache", "google", "brave", "tavily")),

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

    Setting("orient_prose", "off",
            "Whether the orientation's front includes the README. Off, the "
            "account is written from code, schema and manifest alone and the "
            "README is read afterwards, against it, by the reconcile phase -- "
            "prose is a check, not a source. 'on' restores the old front for "
            "comparison runs.",
            values=("on", "off")),

    Setting("onboarding_phases",
            "frame,orient,reconcile,define,survey,reorient,boundaries,"
            "challenge,blindspots",
            "Which understanding phases an onboarding runs, in order: frame "
            "(Architect judges the partition before anything reads it), "
            "orient (Vision Keeper, the whole program, from code alone), "
            "reconcile (Vision Keeper, the README read against the account, "
            "differences to the ledger), define (Terminologist, one word at "
            "a time from the project's own lexicon), survey (the per-area "
            "passes, Terminologist then Architect), reorient (Vision Keeper, "
            "the draft account re-read with the vocabulary and model in "
            "hand), boundaries (Architect, one session per file the outside "
            "touches), challenge (the Critic tries to falsify the "
            "load-bearing claims against source), blindspots (the Liaison "
            "writes what the run could not see to the ledger). Strict: each "
            "phase is written with the previous one's artefact in front of "
            "it. 'survey' alone is the pre-orientation design, kept for "
            "measuring one phase against another."),

    Setting("challenge", "sample",
            "Whether the Critic challenges the understanding artefacts after "
            "the boundaries phase. 'sample' (default) challenges the "
            "load-bearing claims -- constraints and items, capped at twelve, "
            "newest first; 'full' adds every glossary sense and model "
            "account; 'off' skips the pass. A break requires a citation the "
            "session opened: models never adjudicate models.",
            values=("off", "sample", "full")),

    Setting("model_routing", "",
            "Which model drives which tick, as comma-joined `tick=model` "
            "pairs: `frame=gemma3:12b,challenge=llama3.1:8b`. Empty routes "
            "nothing and every session runs on the model the run was "
            "started with. The bakeoff (probes/bench/) is where the pairs "
            "come from -- per-capability scores exist so that per-task "
            "routing is a measurement, not a preference. A tick the string "
            "does not name is untouched, so a recorded case replays on the "
            "model it was recorded with unless it sets this itself."),

    Setting("define_terms", 20,
            "How many words the define phase owes, taken from the top of the "
            "lexicon with the orientation's words promoted. A budget, not a "
            "judgement: the per-area pass still finds an area's own words, and "
            "a word the lexicon ranked below the fold is not lost, only not "
            "asked for up front."),

    Setting("prose_sources", "on",
            "Whether sessions may be shown the repository's prose -- README, "
            "docs/, CHANGELOG and the like. 'off' withholds them from every "
            "context the harness assembles (the front, the concordance, the "
            "area source) and from `code.source` itself, so an onboarding can "
            "be measured on code, schema and manifest alone. A good README is "
            "an easy way to look like understanding; the files stay indexed, "
            "only unread.",
            values=("on", "off")),

    Setting("baseline_election", "",
            "The principal's ruling on which baseline the project adopts, "
            "written by `rota elect` or a chat verdict. Empty means not yet "
            "elected. A ruling, not plumbing: every change is history."),

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


def routed_model(routing: str, wake_kind: str) -> str | None:
    """The model `model_routing` names for this wake, or None for untouched.

    Only ticks route: a wake like `verdict_failed` carries batch context that
    was built by whatever model is already driving, and mid-conversation model
    swaps are exactly the cross-model adjudication the challenge design
    forbids. Model names contain colons, so pairs split on commas and only
    the first `=` binds.
    """
    if not routing or not wake_kind.startswith("tick:"):
        return None
    tick = wake_kind[len("tick:"):]
    for pair in routing.split(","):
        name, _, model = pair.strip().partition("=")
        if name == tick and model:
            return model
    return None


def set(conn: sqlite3.Connection, key: str, value: Any, *,
        author: str = "principal") -> None:
    """
    Write a declared setting, and remember what it displaced.

    The history is the interview's ruling (2026-08-27): config stays the
    principal's direct-edit space, but a knob that forgets its past turns
    "why is this off?" into archaeology. Deliberately memo-free -- a typed
    reason field was designed and removed the same day, on the principal's
    one-line review: "it will never be used". What is recorded is only what
    the machine knows for free. Roles remain config-blind and config-mute,
    and this function is not a tool.
    """
    if key not in SETTINGS:
        raise UnknownSetting(f"{key!r} is not a declared setting")
    problem = SETTINGS[key].validate(value)
    if problem:
        raise ValueError(problem)
    encoded = json.dumps(value)
    prior = conn.execute(
        "SELECT value FROM config WHERE key = ?", (key,)).fetchone()
    if prior is not None and prior["value"] == encoded:
        return                       # nothing moved; history records changes
    conn.execute(
        "CREATE TABLE IF NOT EXISTS config_history ("
        "key TEXT NOT NULL, old_value TEXT, new_value TEXT NOT NULL, "
        "author TEXT NOT NULL DEFAULT 'principal', "
        "at TEXT NOT NULL DEFAULT (datetime('now')))")
    conn.execute(
        "INSERT INTO config_history (key, old_value, new_value, author) "
        "VALUES (?, ?, ?, ?)",
        (key, prior["value"] if prior else None, encoded, author))
    conn.execute(
        "INSERT INTO config(key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, encoded))


def history(conn: sqlite3.Connection, key: str | None = None) -> list[dict]:
    """Every change to declared settings, newest first."""
    try:
        rows = conn.execute(
            "SELECT key, old_value, new_value, author, at "
            "FROM config_history" + (" WHERE key = ?" if key else "")
            + " ORDER BY rowid DESC", (key,) if key else ()).fetchall()
    except sqlite3.OperationalError:
        return []                    # a run from before the table existed
    return [dict(r) for r in rows]


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
