"""
Why the failing cases failed, grouped by mechanism rather than by role.

A pass rate says a case is failing. It does not say whether the case was unfair,
the role under-briefed, or the model out of its depth — and answering that by
reading transcripts one at a time is how a whole afternoon disappears.

This reads the recorded transcripts and sorts every tool error into the shape of
mistake it is. The shapes are not a taxonomy invented in advance; each one is
here because it was found in the data and cost whole cases:

    parse            the harness refused a call whose intent was determined
    working set      the role reached for something its mode took away
    signature        wrong or missing arguments against a signature it was given
    invented id      an id the role made up, for a row that changes in place
    ordering         committed after a read, in the same breath, unseen
    protocol         already sent, no entry to segment, nothing to act on
    session          the session itself died

The last column is what makes it useful: **the same mechanism across several
cases is one bug, and fixing it moves the whole group.** Sorting by role hides
that — the `true` parse error looked like a Vision Keeper problem and a
Terminologist problem and a chain problem, and it was one line in the parser.

    python -m rota.tools.triage             # the last run of every case
    python -m rota.tools.triage --failing   # only cases that did not pass
    python -m rota.tools.triage L1-TS       # cases matching a prefix
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sqlite3
import sys

from rota import paths

# Read verbs, by suffix. Used to spot a role that committed in the same
# completion as a read it could not yet have seen.
READS = ("consult", "load", "lookup", "list", "search", "scan", "source",
         "survey", "quote", "read", "find")

# Each rule is (mechanism, pattern, what a fix would have to change). The third
# is the point: a mechanism you cannot act on is a label, not a diagnosis.
RULES: list[tuple[str, re.Pattern, str]] = [
    ("parse", re.compile(r"could not parse arguments|unterminated argument|"
                         r"no function name after|missing argument list"),
     "the parser, or the protocol description"),
    ("working set", re.compile(r"is not in this role's working set"),
     "the mode's .tools file, or the graph"),
    ("signature", re.compile(r"unexpected argument|missing required argument|"
                             r"is not one of"),
     "the signature, its name, or the prompt that describes it"),
    ("invented id", re.compile(r"no \w+ row with id="),
     "the fixture, or what the wake hands the role"),
    ("protocol", re.compile(r"you have already sent|no entry to segment|"
                            r"no batch in this session"),
     "the mode, or the case's premise"),
    ("session", re.compile(r"session failed|prompt did not fit"),
     "the harness"),
]


def mechanism(text: str) -> tuple[str, str]:
    for name, pattern, fix in RULES:
        if pattern.search(text):
            return name, fix
    return "other", "unknown - read the transcript"


def _live_case_ids() -> set[str]:
    """Case ids the suite still has. Empty if the files cannot be read, which
    leaves the old behaviour rather than silently reporting nothing."""
    try:
        from ..testkit import fixtures

        return {c["id"] for p in sorted(paths.CASES.glob("*.yaml"))
                for c in (fixtures.load_case(p) or [])}
    except Exception:
        return set()


def last_runs(conn: sqlite3.Connection, prefix: str = "") -> list[sqlite3.Row]:
    """The most recent execution of each case, and nothing older.

    "Most recent" means one pass of the sampler — five runs, numbered 1..5 —
    not every row sharing the newest prompt hash. Pooling several passes reports
    0/30 where the threshold is 3-of-5, and a case that has been re-run four
    times then looks four times worse than one that has not.

    Older rows are also a different harness. Mixing them in makes a fixed bug
    look like a live one, which is exactly the mistake this exists to prevent.

    A case that has been renamed or deleted keeps its rows forever, and they read
    as a live 0/5 that no suite can ever turn green. One of those sat at the top
    of the failing list and cost a debugging session before it turned out to be
    the *old name* of a case sitting two lines below it, passing. The case files
    are the authority for what a case is.
    """
    rows = conn.execute(
        "SELECT case_id, run_no, passed, problems, transcript, seq, "
        "       model, prompt_hash FROM case_runs ORDER BY seq DESC").fetchall()
    live = _live_case_ids()
    seen: dict[str, set[int]] = collections.defaultdict(set)
    out = []
    for r in rows:                                   # newest first
        cid = r["case_id"]
        if prefix and not cid.startswith(prefix):
            continue
        if live and cid not in live:                 # renamed or deleted
            continue
        if r["run_no"] in seen[cid]:                 # the pass before this one
            continue
        seen[cid].add(r["run_no"])
        out.append(r)
    return out


def _acted(transcript: list) -> bool:
    """Did the session write or send anything at all?"""
    for turn in transcript:
        if turn.get("wrote") or turn.get("sent"):
            return True
    return False


def blind_commits(transcript: list) -> int:
    """Completions that acted on a read they had not seen come back."""
    n = 0
    for turn in transcript:
        say = turn.get("say")
        if not say:
            continue
        calls = re.findall(r"TOOL:\s*([\w.]+)\s*\(", say)
        for i, fn in enumerate(calls):
            if fn.split(".")[-1] in READS and any(
                    a.startswith("msg.") or a.split(".")[-1] not in READS
                    for a in calls[i + 1:]):
                n += 1
                break
    return n


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("prefix", nargs="?", default="", help="case id prefix")
    ap.add_argument("--failing", action="store_true",
                    help="only cases that did not reach their threshold")
    ap.add_argument("--db", default=str(paths.DEV_DB))
    args = ap.parse_args(argv)

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    rows = last_runs(conn, args.prefix)
    if not rows:
        print("no recorded runs" + (f" matching {args.prefix!r}" if args.prefix else ""))
        return 1

    # per case: runs, passes, mechanisms seen, blind commits
    cases: dict[str, dict] = collections.defaultdict(
        lambda: {"runs": 0, "passed": 0, "mech": collections.Counter(),
                 "blind": 0, "problems": collections.Counter()})
    by_mech: dict[str, set[str]] = collections.defaultdict(set)
    fixes: dict[str, str] = {}

    for r in rows:
        c = cases[r["case_id"]]
        c["runs"] += 1
        c["passed"] += r["passed"]
        for p in json.loads(r["problems"] or "[]"):
            c["problems"][p] += 1
        transcript = json.loads(r["transcript"] or "[]")
        c["blind"] += blind_commits(transcript)
        errors = 0
        for turn in transcript:
            for e in turn.get("errors", []):
                errors += 1
                name, fix = mechanism(str(e))
                c["mech"][name] += 1
                by_mech[name].add(r["case_id"])
                fixes[name] = fix

        # Nothing went wrong and nothing happened. This is its own mechanism and
        # the most important one to name, because it is invisible in an error
        # log: the role read what it was given, understood it well enough to
        # raise no complaint, and then did not act. Every survey case looks like
        # this. It points at the mode's brief, never at the plumbing.
        if not r["passed"] and not errors and not _acted(transcript):
            c["mech"]["silent"] += 1
            by_mech["silent"].add(r["case_id"])
            fixes["silent"] = "the mode's brief - nothing broke, the role just stopped"

    shown = {k: v for k, v in cases.items()
             if not args.failing or v["passed"] < v["runs"]}

    print(f"{len(cases)} cases, {sum(c['runs'] for c in cases.values())} runs"
          f"  ({rows[0]['model']})\n")

    for cid in sorted(shown, key=lambda k: (cases[k]["passed"] / max(cases[k]["runs"], 1), k)):
        c = shown[cid]
        mech = " ".join(f"{k}:{v}" for k, v in c["mech"].most_common())
        print(f"  {c['passed']}/{c['runs']}  {cid}")
        if c["problems"]:
            worst = c["problems"].most_common(1)[0][0]
            print(f"          {worst[:100]}")
        if mech or c["blind"]:
            bits = [b for b in (mech, f"blind:{c['blind']}" if c["blind"] else "")
                    if b]
            print(f"          [{'  '.join(bits)}]")

    if by_mech:
        print("\nmechanisms, by how many cases they touch - the top row is the"
              "\none bug whose fix moves the most:\n")
        for name, ids in sorted(by_mech.items(), key=lambda kv: -len(kv[1])):
            print(f"  {len(ids):3} cases  {name:14} fix: {fixes[name]}")
            print(f"             {', '.join(sorted(ids)[:4])}"
                  f"{' ...' if len(ids) > 4 else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
