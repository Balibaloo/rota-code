"""
Two runs, side by side. The step the evaluation loop ends in.

`run, look, judge, change something, run again, compare` — and the last step had
no home in any interface. Forking made "again, beside it" cheap; this is what
forking is for.

Three things it refuses to do, and each is the reason it is worth having.

**It does not diff rows.** Ids differ by construction — `g1` in one run and
`g1` in another are rarely even the same word — so an id diff reports everything
as changed, which is the same as reporting nothing. What is compared is what
each run *found*, matched on content: the term string, the constraint headline,
the area.

**It does not score.** "Does the term exist" is a query; "does it mean the right
thing" is either an exact string, brittle enough that the key gets rewritten to
fit each run, or a judgement, which is another model. So the interesting row —
*same term, two senses* — is printed as two strings for a person to read.
`intent` came back from a real run as "a specific action or task": present,
fluent, wrong, and invisible to anything asking only whether the term is there.

**It does not compare what it cannot read.** Seven of eight runs in `.rota/` are
behind the schema, and half a comparison reads as a difference — the one thing a
diff must never invent.

The header carries what differed in the *inputs*, because without that the rest
is two numbers with no cause. A difference between runs on different trees is
not evidence about a prompt edit.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

CONFIG_KEYS = ("project_root", "project_branch", "project_commit")


def _open(path: Path) -> sqlite3.Connection:
    from .core.db import connect_readonly

    try:
        conn = connect_readonly(path)
        # Touch what the comparison needs, here, so a database that cannot
        # answer is refused before anything is reported rather than showing up
        # later as an absence indistinguishable from a real difference.
        for table in ("glossary_terms", "constraints", "survey_records", "sessions"):
            conn.execute(f"SELECT COUNT(*) FROM {table}")
    except sqlite3.Error as exc:
        raise SystemExit(
            f"cannot read {Path(path).stem}: {exc}\n"
            f"  a half-read run reports as a difference. Wipe it, or compare "
            f"two runs that are both current.")
    return conn


def _config(conn: sqlite3.Connection) -> dict[str, str]:
    return {r["key"]: (r["value"] or "").strip('"') for r in conn.execute(
        "SELECT key, value FROM config")}


def _terms(conn: sqlite3.Connection) -> dict[str, str]:
    """Keyed by the word, lowercased. The word is the identity, not the row."""
    return {r["term"].strip().lower(): r["sense_short"]
            for r in conn.execute(
                "SELECT term, sense_short FROM glossary_terms ORDER BY id")}


def _constraints(conn: sqlite3.Connection) -> dict[str, str]:
    return {r["headline"].strip().lower(): r["headline"]
            for r in conn.execute("SELECT headline FROM constraints")}


def _areas(conn: sqlite3.Connection) -> dict[str, str]:
    return {r["area"]: r["outcome"] for r in conn.execute(
        "SELECT area, outcome FROM survey_records ORDER BY area")}


def _briefs(conn: sqlite3.Connection) -> set[str]:
    """Which composed briefs this run's sessions actually ran against."""
    try:
        return {r["briefs_hash"] for r in conn.execute(
            "SELECT DISTINCT briefs_hash FROM sessions "
            "WHERE briefs_hash IS NOT NULL AND briefs_hash != ''")}
    except sqlite3.Error:
        return set()


def _cost(conn: sqlite3.Connection) -> dict[str, int]:
    """
    How long, and how much of it got anywhere.

    Sessions alone say how long it took. **Barren** sessions — ones that
    committed and left no receipt — say whether it was getting anywhere, which
    is the number that made the livelock visible when a log could not.
    """
    total = conn.execute("SELECT COUNT(*) n FROM sessions").fetchone()["n"]
    wrote = conn.execute(
        "SELECT COUNT(DISTINCT session_id) n FROM receipts").fetchone()["n"]
    return {"sessions": total, "wrote": wrote, "barren": total - wrote}


def _side(path: Path, conn: sqlite3.Connection) -> dict[str, Any]:
    cfg = _config(conn)
    return {
        "name": Path(path).stem,
        "path": str(path),
        **{k: cfg.get(k, "") for k in CONFIG_KEYS},
    }


def _split(a: dict, b: dict) -> tuple[list, list, list, list]:
    """Present in one, present in both and agreeing, present in both and not."""
    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))
    agree, differ = [], []
    for key in sorted(set(a) & set(b)):
        (agree if a[key] == b[key] else differ).append(key)
    return only_a, only_b, agree, differ


def runs(path_a: str | Path, path_b: str | Path) -> dict[str, Any]:
    """Everything two runs disagree about, and nothing about who is right."""
    path_a, path_b = Path(path_a), Path(path_b)
    ca, cb = _open(path_a), _open(path_b)
    try:
        out: dict[str, Any] = {"a": _side(path_a, ca), "b": _side(path_b, cb)}

        commit_a, commit_b = out["a"]["project_commit"], out["b"]["project_commit"]
        # Two silences are not agreement. A run onboarded before the commit was
        # recorded answers nothing, and saying so beats implying a match.
        out["same_source"] = (None if not (commit_a and commit_b)
                              else commit_a == commit_b)

        briefs_a, briefs_b = _briefs(ca), _briefs(cb)
        out["same_prompts"] = (None if not (briefs_a and briefs_b)
                               else briefs_a == briefs_b)

        ta, tb = _terms(ca), _terms(cb)
        only_a, only_b, agree, differ = _split(ta, tb)
        out["terms"] = {
            "only_a": only_a, "only_b": only_b,
            "agree": [{"term": t, "sense": ta[t]} for t in agree],
            # First, because it is the row an existence check cannot see and
            # the one a fluent wrong answer hides in.
            "differ": [{"term": t, "a": ta[t], "b": tb[t]} for t in differ],
        }

        ka, kb = _constraints(ca), _constraints(cb)
        only_a, only_b, agree, _ = _split(ka, kb)
        out["constraints"] = {
            "only_a": [ka[k] for k in only_a], "only_b": [kb[k] for k in only_b],
            "agree": [ka[k] for k in agree],
        }

        aa, ab = _areas(ca), _areas(cb)
        only_a, only_b, agree, differ = _split(aa, ab)
        out["areas"] = {
            "only_a": only_a, "only_b": only_b, "agree": agree,
            "differ": [{"area": x, "a": aa[x], "b": ab[x]} for x in differ],
        }

        out["cost"] = {"a": _cost(ca), "b": _cost(cb)}
        out["header"] = _header(out)
        return out
    finally:
        ca.close()
        cb.close()


def _header(out: dict) -> str:
    """
    What differed in the *inputs*. Without it the rest is two numbers and no
    cause: a difference between runs on different trees is not evidence about
    anything you changed.
    """
    a, b = out["a"], out["b"]
    if out["same_source"] is None:
        source = ("the commit is not recorded for both runs, so whether they "
                  "are about the same tree is unknown")
    elif out["same_source"]:
        source = (f"same source — {a['project_branch'] or '?'}@"
                  f"{a['project_commit'][:7]}")
    else:
        source = (f"DIFFERENT sources — {a['name']} on "
                  f"{a['project_branch'] or '?'}@{a['project_commit'][:7]}, "
                  f"{b['name']} on {b['project_branch'] or '?'}@"
                  f"{b['project_commit'][:7]}. Differences below are about the "
                  f"code, not about anything you changed")

    if out["same_prompts"] is None:
        prompts = "prompt versions not recorded for both"
    elif out["same_prompts"]:
        prompts = "same prompts"
    else:
        prompts = "different prompts"
    return f"{source} · {prompts}"


# ---------------------------------------------------------------------------
# Printing, for the command line
# ---------------------------------------------------------------------------

def render(out: dict) -> str:
    """One screen. The differences first, because agreement is the background."""
    a, b = out["a"]["name"], out["b"]["name"]
    lines = [f"{a}  vs  {b}", f"  {out['header']}", ""]

    differ = out["terms"]["differ"]
    if differ:
        lines.append(f"SAME TERM, DIFFERENT SENSE  ({len(differ)})")
        for d in differ:
            lines.append(f"  {d['term']}")
            lines.append(f"    {a}: {d['a']}")
            lines.append(f"    {b}: {d['b']}")
        lines.append("")

    for label, key, fmt in (
            ("TERMS", "terms", lambda x: x),
            ("CONSTRAINTS", "constraints", lambda x: x),
            ("AREAS", "areas", lambda x: x)):
        only_a = [fmt(x) for x in out[key]["only_a"]]
        only_b = [fmt(x) for x in out[key]["only_b"]]
        agree = out[key]["agree"]
        lines.append(f"{label}  ({len(agree)} in both)")
        for x in only_a:
            lines.append(f"  only {a}:  {x}")
        for x in only_b:
            lines.append(f"  only {b}:  {x}")
        if not only_a and not only_b:
            lines.append("  no difference")
        lines.append("")

    for area in out["areas"]["differ"]:
        lines.append(f"  {area['area']}: {a}={area['a']}  {b}={area['b']}")

    ca, cb = out["cost"]["a"], out["cost"]["b"]
    lines.append("COST")
    lines.append(f"  {a}: {ca['sessions']} sessions, {ca['barren']} wrote nothing")
    lines.append(f"  {b}: {cb['sessions']} sessions, {cb['barren']} wrote nothing")
    lines.append("")
    lines.append("Nothing here is scored. Which sense is right is a judgement, "
                 "and it is yours.")
    return "\n".join(lines)
