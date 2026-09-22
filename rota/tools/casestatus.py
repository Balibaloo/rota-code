"""
Where every model-facing case actually stands, without running anything.

    python -m rota.tools.casestatus            # everything, worst first
    python -m rota.tools.casestatus --red      # only what is not green

The report reads one model's recordings and says which on its second line.
`--model` names it, `ROTA_MODEL` sets it, and the last resort is the model the
gate replays. A count read under a model the suite does not run is a true
number about nothing, and one was quoted for two days as prompt drift.

The distinction this exists for is **stale versus failing**, and it is not
cosmetic. A case with no recording against the current prompt is *unmeasured*:
the role may be doing the job perfectly and nobody has looked since the brief
was edited. A case that failed is a case that was measured and got it wrong.
The suite prints them differently and I still read a run of seven failures as
seven failures when three of them were unknowns -- because the count is on the
last line and the reason is thirty lines up, and I quoted the count.

So the count is the thing that has to carry the distinction:

    4 failing, 3 stale, 61 green

`case_runs` records the prompt hash each result was earned against, which makes
this a query rather than a test run. Recomposing the brief here costs
milliseconds and is the same composition the tier uses, so a case is stale here
exactly when it is stale there.

**The report also composes the whole system text** (frame 63, 2026-09-22). The
brief is only a prefix of what the model receives, and the cassette key covers
all of it, so a tools edit left a case green that the suite could not replay.
A single session composes its text in about 8 ms. A chain's text is whatever
its legs reached, so a chain is replayed against the recordings. The whole
report costs 6.0 seconds: 0.9 for 121 compositions and 4.0 for 7 chains
(observed: this machine, 2026-09-22).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import tempfile
from pathlib import Path

from .. import paths
from ..llm.cassettes import MISS_MARKERS, UNBUILT, system_hash, trust
from ..llm.llm import DEFAULT_NUM_CTX, Pins, think_for

from ..testkit import fixtures


def _cases() -> list[dict]:
    out = []
    for pattern in ("l*.yaml", "g*.yaml"):
        for path in sorted(paths.CASES.glob(pattern)):
            out.extend(fixtures.load_case(path) or [])
    return out


def model_for(named: str = "") -> str:
    """
    Which model's recordings this report reads. Named, then ambient, then the
    gate's.

    The default was `llama3.1:8b` and `status` read no environment at all, so
    the same register answered two ways: the bare command printed 67 stale and
    50 green, and `--model qwen3:8b` printed 0 stale and 107 green (observed:
    frame 54's run of both commands, 2026-09-21). Both numbers were right.
    Frame 49 then carried a 72-case obligation that was an artefact of this
    default, and no reader could see it, because the report never said which
    model it had read.

    The last resort is the gate's model and never `DEFAULT_MODEL`, whose own
    fallback is the `llama3.1:8b` that caused this.
    """
    if named:
        return named
    # Lazily, and from the gate, because the gate declares the model the suite
    # replays. One declaration: a second copy here would be the same fault in
    # a new place.
    from .gate import FALLBACK_MODEL

    return os.environ.get("ROTA_MODEL") or FALLBACK_MODEL


def wanted_pins(case: dict, model: str) -> Pins:
    """
    The pins a tier would run this case under, field by field.

    The one-model ruling: a case that declares `model:` is held by that model,
    and a report must read the same recordings the suite replays. A qwen-held
    green rendering as a llama STALE would be the report contradicting the
    register it exists to show.

    `num_ctx` comes from `DEFAULT_NUM_CTX`, which is what a tier runs at: all
    three tier files deliberately pin no window. The temperature is 0.0, and
    every cassette in the register is at 0.0. `think` comes from
    `ROTA_PROFILE`, through the one rule the tier stamps with.
    """
    pinned = case.get("model", model)
    return Pins(model=pinned, temperature=0.0,
                think=think_for(pinned)).with_prompt(
        fixtures.instructions_for(case))


def carries_the_key(conn: sqlite3.Connection) -> bool:
    """
    Whether this register's results carry the cassette key's own fields.

    A reader that connects without `open_dev_db` never migrates, and a
    checkout can hold a register written before frame 54. Asking the table
    beats catching `no such column`, because that error would also hide a
    typo in a column name.
    """
    from ..llm.cassettes import KEY_COLUMNS

    have = {row[1] for row in conn.execute("PRAGMA table_info(case_runs)")}
    return bool(have) and {name for name, _ in KEY_COLUMNS} <= have


def records_misses(conn: sqlite3.Connection) -> bool:
    """
    Whether this register can say that a look measured nothing.

    `key_misses` arrives with frame 64, and `open_dev_db` is its only creator.
    A reader that connects raw never creates it, and the cockpit's panel is
    such a reader. Its `except sqlite3.Error` would turn a missing table into
    `never run` for every case, in silence, so the table is asked for by name
    rather than caught.
    """
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        ("key_misses",)).fetchone() is not None


def holds_a_system_hash(conn: sqlite3.Connection) -> bool:
    """
    Whether this register can answer about the system text at all.

    **`carries_the_key` is not the guard for this**, and using it would report
    every case stale (observed: frame 63's design review, probe 5,
    2026-09-22). It asks whether the columns exist. `open_dev_db` adds them
    with `DEFAULT ''` and backfills nothing, so a register written before
    frame 54 answers True with an empty hash on every row. And
    `tests/rota/cassettes.db` is gitignored and pulled from a published
    snapshot that carries no schema version, so this is a live case and not a
    theory.

    `''` is a row written before the column existed. `unbuilt` is a session
    that died before it composed a prompt. Neither row says what the model was
    told, so neither turns the widened match on.

    **The predicate is global, and not per case.** So a mixed register stales
    every case that carries only legacy rows, because a legacy row cannot say
    what text it measured.
    """
    if not carries_the_key(conn):
        return False
    return conn.execute(
        "SELECT 1 FROM case_runs WHERE system_hash NOT IN ('', ?) LIMIT 1",
        (UNBUILT,)).fetchone() is not None


def matching_runs(conn: sqlite3.Connection, case: dict, want: Pins,
                  *, keyed: bool = True, system: str = "",
                  limit: int | None = None) -> list:
    """
    The rows that are evidence about this case under these pins, newest first.

    **One definition, because two instruments read this table.** This report
    and the cockpit's L1 panel disagreed on the migrated register: the panel
    said `llama3.1:8b` with 98 pass and 19 fail, while the report said 20
    failing and 103 green under `qwen3:8b` (observed: frame 54's diff review,
    2026-09-21). The panel matched on `prompt_hash` alone and took the model
    from the first row it happened to read. The panel is the one a person
    reads, so a second copy of this match is frame 60's fault in a new place.

    A run that died for want of a cassette is not a result, and until
    `record_case_run` refused to write those there were three thousand of
    them. They are excluded rather than deleted: the rows are somebody's
    history even when they are not evidence.

    They can carry a *current* prompt hash, which is what made them
    dangerous. `prompt_hash` covers the composed brief, the mode prompt
    included, so a brief edit does stale a case. What it does not cover is
    the runner's session prose and the working set's `TOOL:` lines, which are
    the rest of the system text and are in the cassette key -- so a tools
    edit left every hash current and the case read green while the suite
    could not replay it.

    `system` closes that hole. It is the system text the tree composes for
    this case now, and the caller passes it: `compose_system` builds it for a
    single session, and only a replay builds it for a chain. It is empty when
    the register carries no hash to match, which `holds_a_system_hash`
    decides.

    `load_id` stays out for two reasons. It is `model@epoch//7200`, so
    matching on it would stale every case two hours after its recording, and
    `trust` reads several loads to tell `provisional` from `earned`.

    `keyed` is False for a register written before frame 54, which has no
    columns to match the key on. Such a register answers the narrow question
    only, and a reader that widens the match against it would raise rather
    than report.
    """
    sql = ["SELECT passed, problems, seq FROM case_runs"]
    clauses, args = _key_clauses(case, want, keyed=keyed, system=system)
    sql += clauses
    # A row from before the write-time guard, matched on the markers the
    # writer owns. One copy of the rule: the second copy named one of the two
    # markers, so a run that could not reach the model entered the window and
    # read as a red (observed: frame 64's scope report, R9, 2026-09-22).
    dead = " OR ".join("problems LIKE ? OR transcript LIKE ?"
                       for _ in MISS_MARKERS)
    sql.append(f" AND NOT (passed = 0 AND ({dead})) ORDER BY seq DESC LIMIT ?")
    for marker in MISS_MARKERS.values():
        args += [f"%{marker}%", f"%{marker}%"]
    args.append(case.get("runs", 5) if limit is None else limit)
    return list(conn.execute("".join(sql), args))


def _key_clauses(case: dict, want: Pins, *, keyed: bool,
                 system: str) -> tuple[list[str], list]:
    """
    The clauses that say a row is about this case under these pins.

    One definition, because two tables carry the same key columns. A miss must
    match the key the runs match, or the report reads a false STALE twice:
    after a person reverts a system-half edit the old runs match again while a
    miss at the other `system_hash` is newer, and a local run under another
    profile writes misses that would stale the suite's read.
    """
    sql = [" WHERE case_id = ? AND prompt_hash = ? AND model = ?"]
    args: list = [case["id"], want.prompt_hash, want.model]
    if system:
        # The whole text the model was sent, which is what the cassette key
        # covers. The two sentinels are named rather than left to the
        # equality: `''` is a row written before frame 54 added the column,
        # and `unbuilt` is a session that died before it had a prompt. A row
        # that cannot say what the model was told is not evidence about this
        # text.
        sql.append(" AND system_hash = ? AND system_hash NOT IN ('', ?)")
        args += [system_hash(system), UNBUILT]
    if keyed:
        sql.append(" AND num_ctx = ? AND temperature = ? AND protocol = ? "
                   "AND extras = ?")
        # Text, because 18570 of the register's 18604 cassettes key as text
        # and none as native (observed: the design review's probe 5,
        # 2026-09-21). A tier offers the model no native schemas.
        args += [want.num_ctx, want.temperature, "text",
                 json.dumps(want.extras(), sort_keys=True)]
    return sql, args


def latest_miss(conn: sqlite3.Connection, case: dict, want: Pins,
                *, keyed: bool = True, system: str = "") -> sqlite3.Row | None:
    """
    The newest look at this key that measured nothing, or None.

    A replay that finds no cassette at the current key writes one of these and
    no run. Until frame 64 it wrote nothing at all, so the report read the
    older rows at the same hashes and the case read green while the suite
    could not replay it. The two instruments then contradicted each other: the
    gate's stale line stayed at zero and its red count carried a case nobody
    had measured.

    `records_misses` guards the call, because a register pulled from a
    published snapshot carries no schema version and may predate the table.
    """
    sql = ["SELECT * FROM key_misses"]
    clauses, args = _key_clauses(case, want, keyed=keyed, system=system)
    sql += clauses
    sql.append(" ORDER BY seq DESC LIMIT 1")
    return conn.execute("".join(sql), args).fetchone()


def miss_line(miss: sqlite3.Row) -> str:
    """
    The one sentence that says somebody looked and the key missed.

    The time leads, because `render` cuts the line at 96 characters and the
    reason is what may be cut. The kind comes second: `no cassette` is a
    prompt that moved, and `unreachable` is a stopped server.
    """
    return f"looked {miss['at']}, {miss['kind']}: {miss['reason']}"


#: What a chain's text is when the replay could not produce one. It is not a
#: system text and no row can carry its digest, so the case reads STALE. A
#: sentinel and not `''`, because `''` means "do not match on the text" and
#: would hand the case back to the narrow match.
REPLAY_FAILED = "<the chain did not replay>"


def replayed_chain_text(conn: sqlite3.Connection, case: dict,
                        want: Pins) -> tuple[str, str]:
    """
    The system texts a chain actually reaches, by replaying it, and the reason
    when it reaches none.

    A chain's recorded hash is not always over both legs. `run_chain` returns
    leg one's text alone when leg two never wakes, and
    `L3-a-challenge-reaches-the-role-that-can-answer-it` carries such a
    one-leg digest (observed: frame 63's read of the register, 2026-09-22).
    So the column means the system texts the run reached, and only a replay
    reproduces how far a chain got. Composing leg one and calling it the chain
    would compare a one-leg digest against a two-leg digest for six of the
    seven chains and force all seven to re-record.

    **A failed replay is loud.** The first version fell back to the narrow
    match, so a chain that nothing could replay read green and the gate's
    stale set stayed empty (observed: frame 63's diff review, 2026-09-22).
    Silence is what made that dangerous. The sentinel matches no row, the case
    reads STALE, and the reason travels with it to the report's own line.

    The report stays alive either way, because the gate reads this line and a
    report that dies takes the gate with it.

    The replay runs here and in the gate, and never in the cockpit's panel. A
    chain that declares `repo:` shells out to git, and an HTTP request must
    not make a worktree.
    """
    from ..llm.cassettes import ReplayOnlyBackend

    work = tempfile.mkdtemp()
    text, problem = "", ""
    try:
        result = fixtures.run_chain(case, Path(work) / "chain.db",
                                    lambda: ReplayOnlyBackend(conn), pins=want)
        text = result.system_text()
        if not text:
            problem = "the replay reached no system text"
    except Exception as exc:
        problem = f"the chain could not be replayed: {exc}"

    try:
        # No `ignore_errors`: a directory that will not delete means something
        # still holds the database inside it. That leak ran on every report
        # and every gate, and the flag is what hid it.
        shutil.rmtree(work)
    except OSError as exc:
        leaked = f"the replay's working directory did not delete: {exc}"
        problem = f"{problem}. {leaked}" if problem else leaked
    return (text or REPLAY_FAILED), problem


def status(model: str = "") -> list[dict]:
    # Through the one opener that migrates: a raw connect here read the
    # committed db from before `load_id` existed and died inside `trust`.
    from ..llm.cassettes import open_dev_db

    model = model_for(model)
    conn = open_dev_db(paths.DEV_DB)
    # Only a register that carries a hash can answer about the system text.
    widen = holds_a_system_hash(conn)
    # `open_dev_db` creates the table, so this is true here for every register
    # the report opens. It is asked anyway, once, because the panel below
    # shares the reader and connects raw.
    misses = records_misses(conn)

    rows = []
    for case in _cases():
        role = case.get("role") or (case.get("then") or {}).get("role")
        if not role:
            continue
        want = wanted_pins(case, model)
        system, replay_problem = "", ""
        if widen:
            if case.get("first"):
                system, replay_problem = replayed_chain_text(conn, case, want)
            else:
                system = fixtures.system_text_for(case)
        here = matching_runs(conn, case, want, system=system)
        ever = conn.execute(
            "SELECT COUNT(*) n FROM case_runs WHERE case_id = ?",
            (case["id"],)).fetchone()["n"]

        threshold = case.get("pass", 3)
        # What the narrow match would have counted, for the one question the
        # widened match cannot answer by itself: did the register shrink?
        narrow = matching_runs(conn, case, want) if system else here

        if not here:
            state = "STALE" if ever else "NEW"
            passed = None
        elif len(here) < threshold <= len(narrow):
            # A shrunk denominator is unmeasured, and never a failure. This is
            # the distinction frame 54 exists for: stale means nobody has
            # looked since the text moved, and failing means somebody looked
            # and the role got it wrong. A partly migrated register holds
            # legacy rows the widened match drops, and a case with 3 legacy
            # rows and 2 current ones rendered as a red on 2 of 2 (observed:
            # frame 63's diff review, 2026-09-22).
            state = "STALE"
            passed = None
        else:
            passed = sum(r["passed"] for r in here)
            state = "green" if passed >= threshold else "FAIL"
            # The ruling (2026-08-27): a green that flipped from red counts
            # as fixed only after a second load confirms it. `trust` reads
            # the same rows; a provisional green renders as its own state so
            # a lucky load cannot be quoted as a fix.
            if state == "green" and trust(conn, case["id"]) == "provisional":
                state = "PROV"

        # A look that measured nothing, and newer than the evidence. Whatever
        # state the rows reached, nobody has measured this case at the key the
        # tree composes now, so the case is unmeasured and says which look
        # missed. With no matching row the state stays NEW or STALE: `NEW`
        # keeps its meaning, nobody has measured this case at all.
        miss = (latest_miss(conn, case, want, system=system) if misses
                else None)
        newest = max((r["seq"] for r in here), default=None)
        if miss is not None and (newest is None or miss["seq"] > newest):
            if here:
                # No score on a stale line. A score names a measurement, and
                # this case has none at the current key.
                state, passed = "STALE", None
        else:
            miss = None

        why = ""
        if replay_problem:
            # A chain that could not replay says so on its own line, whatever
            # state it reached. The report prints `why` for every state.
            why = replay_problem
        elif miss is not None:
            why = miss_line(miss)
        elif state == "FAIL":
            problems = [p for r in here for p in json.loads(r["problems"] or "[]")]
            why = problems[0] if problems else ""

        rows.append({"id": case["id"], "state": state, "passed": passed,
                     "of": len(here), "need": threshold, "why": why,
                     "role": role, "ever": ever})
    return rows


def render(rows: list[dict], red_only: bool = False, model: str = "") -> str:
    order = {"FAIL": 0, "PROV": 1, "STALE": 2, "NEW": 3, "green": 4}
    rows = sorted(rows, key=lambda r: (order[r["state"]], r["id"]))
    counts = {k: sum(1 for r in rows if r["state"] == k) for k in order}

    out = [f"{counts['FAIL']} failing, {counts['PROV']} provisional, "
           f"{counts['STALE']} stale, {counts['NEW']} never measured, "
           f"{counts['green']} green"]
    if model:
        # The key these counts were read under, printed with them. A count
        # quoted without its model is the 72 of frame 49: a true number about
        # a model the suite does not run.
        extras = json.dumps(Pins(model=model, think=think_for(model)).extras(),
                            sort_keys=True)
        out.append(f"  read under {model}, window {DEFAULT_NUM_CTX}, "
                   f"protocol text" + (f", pins {extras}" if extras != "{}" else ""))
    if counts["PROV"]:
        out.append("  provisional greened on one load after being red: "
                   "re-earn on a second load before quoting it as fixed")
    if counts["STALE"] or counts["NEW"]:
        # Through the one definition the tiers print, because this footer was
        # the last place that still named no model. Frame 60 repaired the
        # tiers' own STALE message and their usage lines, and the report's
        # advice line was a fourth site nobody had read: it told the reader to
        # re-earn a case under whatever was ambient, which is how two cases
        # flipped from fail to pass on the model alone (observed: frame 60,
        # the same 20 case ids run twice, 2026-09-21).
        out.append("  stale is unmeasured, not bad: " + fixtures.rerecord_command(
            Pins(model=model or "", num_ctx=DEFAULT_NUM_CTX,
                 think=think_for(model) if model else None),
            "tests/rota/test_l1.py"))
    out.append("")

    for r in rows:
        if red_only and r["state"] in ("green", "PROV"):
            continue
        score = f"{r['passed']}/{r['of']}" if r["passed"] is not None else "  -"
        line = f"  {r['state']:<5} {score:>5} (need {r['need']})  {r['id']}"
        out.append(line)
        if r["why"]:
            out.append(f"              {r['why'][:96]}")
    return "\n".join(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--red", action="store_true", help="hide green cases")
    ap.add_argument("--model", default="",
                    help="the model the recordings are held by; the default "
                         "is ROTA_MODEL, then the model the gate replays")
    args = ap.parse_args()
    model = model_for(args.model)
    print(render(status(model), red_only=args.red, model=model))
