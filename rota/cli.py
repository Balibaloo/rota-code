"""
One way in.

Everything this exposes already worked and was reachable by four module paths
with three different ideas of where the database is: `onboard_run` defaulting to
`<repo>/.rota/oauthlib.db`, the TUI to `.rota/rota.db`, and the cockpit to a
path it *derives* from a project root and cannot be told. `.rota/` has eleven
files in it, five of them named `probe2` or `.old2` or `.pre-vocab-rework`,
which is what a wipe-and-rerun loop looks like when it is done by hand.

Two ideas hold the rest together.

**A run has a name.** `rota onboard ctn_v3 --root <checkout>` and every verb
afterwards takes `ctn_v3`. Two runs against the same checkout are two names, not
two wipes -- which is what comparing a branch against its main actually needs,
and was done last time by remembering two paths.

**The run records the project, not the other way round.** `project_root` has
been in `config` since onboarding wrote it; nothing downstream read it, so the
root was passed again to every tool that needed it and the two could disagree.
Here it is read. You name a run, and what it is about comes out of it.

The consequence worth having is negative: **nothing here creates a database
because it could not find one.** That was the cockpit's behaviour and it is the
one failure this file was written for -- pointed at a checkout it booted an
empty database and served that, which renders as a system that ran and produced
nothing rather than as a wrong path. Refusing is the whole feature.

    rota ls                                    what runs exist, and their state
    rota onboard ctn_v3 --root <checkout>      index, partition, constraint zero
    rota run ctn_v3                            turn the crank to quiescence
    rota tui ctn_v3                            talk to it, register beside you
    rota cockpit ctn_v3                        the rows, the graph, the trace
    rota report ctn_v3                         what came out, and the audit
    rota diff ctn_v3 ctn_v3-2                  what two runs disagree about
    rota wipe ctn_v3                           worktrees, processes, then the file
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from pathlib import Path

from . import paths

# Where named runs live. This repository's state directory, not the target
# project's: the databases are about work *on* a checkout and several of them
# can be about the same one, so they cannot be identified by it.
RUNS = paths.REPO / ".rota"


# ---------------------------------------------------------------------------
# Naming
# ---------------------------------------------------------------------------

def resolve(name: str) -> Path:
    """
    A name is a run; anything that looks like a path is a path.

    Both spellings stay, because both are in use -- every recorded invocation in
    the docs and in my own shell history passes `--db .rota/something.db`, and
    breaking those to introduce a convenience would make this the fifth idea of
    where the database is rather than the last.
    """
    text = str(name)
    if text.endswith(".db") or "/" in text or "\\" in text:
        return Path(text)
    return RUNS / f"{text}.db"


def existing() -> list[str]:
    if not RUNS.is_dir():
        return []
    return sorted(p.stem for p in RUNS.glob("*.db"))


def require(name: str) -> Path:
    """
    The path, or a refusal that names what is there instead.

    A refusal that does not list the alternatives sends you to `ls` and back,
    and the mistake this catches is nearly always a typo or a run you wiped --
    both of which are answered by the list.
    """
    path = resolve(name)
    if path.exists():
        return path
    known = existing()
    raise SystemExit(
        f"no run named {name!r} at {path}\n" +
        (f"  runs: {', '.join(known)}" if known else
         "  no runs yet: rota onboard <name> --root <checkout>"))


# ---------------------------------------------------------------------------
# Listing
# ---------------------------------------------------------------------------

COUNTED = ("glossary_terms", "constraints", "items", "survey_records",
           "batches", "sessions")


def _read(path: Path) -> dict:
    from .core.db import connect_readonly

    row: dict = {"name": path.stem, "path": str(path), "root": "", "error": "",
                 "counts": {}, "state": "", "branch": "", "commit": "",
                 "moved": False}
    try:
        conn = connect_readonly(path)
    except sqlite3.Error as exc:
        row["error"] = str(exc)
        return row
    try:
        recorded = {r["key"]: (r["value"] or "").strip('"') for r in conn.execute(
            "SELECT key, value FROM config WHERE key IN "
            "('project_root', 'project_branch', 'project_commit')")}
        row["root"] = recorded.get("project_root", "")
        row["branch"] = recorded.get("project_branch", "")
        row["commit"] = recorded.get("project_commit", "")
        # Has the tree moved past the receipt? The same comparison
        # `boot.reconcile_worktrees` makes for a batch, one level up. Runs
        # onboarded before the commit was recorded simply do not answer.
        if row["commit"] and row["root"]:
            _, now = checkout_of(row["root"])
            row["moved"] = bool(now) and now != row["commit"]
        for table in COUNTED:
            got = conn.execute(f"SELECT COUNT(*) n FROM {table}").fetchone()
            row["counts"][table] = got["n"]
        from .core.scheduler import is_quiescent_readonly

        row["state"] = "quiescent" if is_quiescent_readonly(conn) else "ready"
    except sqlite3.Error as exc:
        # A database written against a schema that has since moved is the
        # normal case in a directory nothing prunes, and it is still worth
        # listing -- knowing a name is taken is most of what `ls` is for.
        #
        # **Named, not blanked.** The first version left `state` empty here and
        # seven of eight runs printed an empty column, which reads as "no state
        # yet" and is the same silent shape as the cockpit booting a database it
        # could not find. A row that cannot answer says why it cannot.
        row["state"] = "stale"
        row["error"] = str(exc)
    finally:
        conn.close()
    return row


def runs() -> list[dict]:
    if not RUNS.is_dir():
        return []
    return [_read(p) for p in sorted(RUNS.glob("*.db"))]


def cmd_ls(args: argparse.Namespace) -> int:
    rows = runs()
    if not rows:
        print(f"no runs in {RUNS}")
        return 0
    head = ("run", "state", "terms", "cons", "items", "surv", "sess")
    print(f"{head[0]:22s} {head[1]:10s} {head[2]:>5s} {head[3]:>5s} "
          f"{head[4]:>5s} {head[5]:>5s} {head[6]:>5s}  project")
    for row in rows:
        if row["error"] and not row["counts"]:
            print(f"{row['name']:22s} {'unreadable':10s} {row['error'][:60]}")
            continue
        c = row["counts"]
        where = row["root"]
        if row["branch"]:
            where = (f"{row['branch']}@{row['commit'][:7]}"
                     + (" · tree has moved" if row["moved"] else "")
                     + f"  {row['root']}")
        print(f"{row['name']:22s} {row['state']:10s} "
              f"{c.get('glossary_terms', 0):5d} {c.get('constraints', 0):5d} "
              f"{c.get('items', 0):5d} {c.get('survey_records', 0):5d} "
              f"{c.get('sessions', 0):5d}  {where}")
        if row["state"] == "stale":
            # Said, and not acted on. Databases here are throwaway and rebuilt
            # by `init_db` at boot; a migration path would be a promise the
            # design deliberately does not make, so the counts above are still
            # true and only the derived state is unavailable.
            print(f"{'':22s} [behind schema: {row['error'][:50]}]")
    return 0


# ---------------------------------------------------------------------------
# Wiping
# ---------------------------------------------------------------------------

def _refuse_if_held(path: Path) -> None:
    """
    Is another process holding this run? Asked *before* anything is destroyed.

    You will do this: a seat is open on a run and you wipe it from a terminal.
    Windows refuses to unlink an open file, and the old order made that a
    **partial** wipe -- worktrees and processes went first, then the unlink
    raised, so the run lost the things only it could prove it owned and kept
    the file that recorded them. The traceback was the polite part.

    Renaming aside and back is the probe. On Windows it fails exactly when
    another process has the file open; on POSIX it succeeds, which is the right
    answer there because the unlink would have succeeded too.
    """
    probe = path.with_name(path.name + ".wipecheck")
    try:
        os.rename(path, probe)
    except OSError:
        raise SystemExit(
            f"{path.name} is open in another process -- close the seat or "
            f"cockpit holding it, then wipe again. Nothing was removed.")
    try:
        os.rename(probe, path)
    except OSError as exc:                                      # pragma: no cover
        raise SystemExit(
            f"could not put {path.name} back after checking it ({exc}). "
            f"It is at {probe}.")


def _teardown(conn) -> dict:
    """
    The two things a run owns that are not in its file, each stopped by the
    code that already knows how to prove ownership.
    """
    from .core import environments, worktrees

    out: dict = {"worktrees": [], "pids": []}
    for r in conn.execute("SELECT id FROM batches").fetchall():
        batch = r["id"]
        try:
            if worktrees.destroy(conn, batch):
                out["worktrees"].append(batch)
        except Exception as exc:                               # noqa: BLE001
            print(f"  worktree {batch}: {exc}")
        try:
            out["pids"] += environments.teardown(conn, batch, release_ports=True)
        except Exception as exc:                               # noqa: BLE001
            print(f"  processes {batch}: {exc}")
    return out


def wipe(path: Path) -> dict:
    """
    Check it is ours to remove, then worktrees, then processes, then the file.

    This is a command rather than an `rm` because two of the three things a run
    owns are not in the file. A worktree lives in the *project*, and the only
    record that it is ours is a row in this database -- delete the database
    first and the directory is unreachable by anything that checks ownership,
    so it stays on disk permanently. A spawned process is the same shape with a
    worse ending.

    Both teardowns are the ones already written: `worktrees.destroy` refuses
    anything outside the state directory, and `environments.teardown` kills only
    what it can prove is ours on two independent facts. Nothing new is allowed
    to delete anything here.
    """
    from .core.db import connect

    removed: dict = {"worktrees": [], "pids": [], "files": []}
    if path.exists():
        _refuse_if_held(path)
        conn = connect(path)
        try:
            removed |= _teardown(conn)
            conn.commit()
        except sqlite3.Error as exc:
            # An unreadable database owns nothing we can prove, so there is
            # nothing to tear down and the file is still ours to remove.
            print(f"  {path.name}: {exc}")
        finally:
            conn.close()

    # The journal goes with it. `connect` turns WAL on for every run, so `rm
    # run.db` leaves `run.db-wal` and `run.db-shm` behind and the next run of
    # that name opens a file with somebody else's uncommitted tail.
    for suffix in ("", "-wal", "-shm"):
        target = path.with_name(path.name + suffix)
        if target.exists():
            target.unlink()
            removed["files"].append(target.name)
    return removed


def cmd_wipe(args: argparse.Namespace) -> int:
    path = require(args.name)
    if not args.yes:
        print(f"wipe {path}")
        print("  its worktrees, its recorded processes, and the file")
        if input("  type the run name to confirm: ").strip() != path.stem:
            print("  not wiped")
            return 1
    removed = wipe(path)
    print(f"wiped {path.stem}: {len(removed['worktrees'])} worktree(s), "
          f"{len(removed['pids'])} process(es), {', '.join(removed['files'])}")
    return 0


# ---------------------------------------------------------------------------
# The verbs that do the work. Each one is the existing tool, given a run.
# ---------------------------------------------------------------------------

def checkout_of(root: str | Path) -> tuple[str, str]:
    """
    The branch and commit a checkout is on, or two empty strings.

    Not an error when there is no git: a directory can be onboarded without
    being a repository, and the run then honestly records that it is about a
    tree rather than about a commit.
    """
    import subprocess

    out = []
    for args in (("rev-parse", "--abbrev-ref", "HEAD"), ("rev-parse", "HEAD")):
        try:
            got = subprocess.run(["git", "-C", str(root), *args],
                                 capture_output=True, text=True, timeout=10)
            out.append(got.stdout.strip() if got.returncode == 0 else "")
        except (OSError, subprocess.SubprocessError):
            out.append("")
    return out[0], out[1]


def onboard(path: Path, root: str | Path):
    """
    Index a checkout into a run, and record *which* checkout.

    The commit is written here rather than inside `onboarding.boot` because it
    is a fact about the operator's choice — this tree, at this moment — and not
    about the indexing. Every other piece of evidence in this system records the
    commit it was gathered at (`batches.head_commit`, `test_runs.commit_sha`,
    `findings.commit_sha`, `verdicts.commit_sha`); the understanding side never
    did, so two runs against different branches were on the record identical.
    """
    from .core.db import init_db
    from .onboarding import boot as onboarding_boot

    root = Path(root).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = init_db(path)
    try:
        report = onboarding_boot.onboard(conn, root)
        branch, commit = checkout_of(root)
        for key, value in (("project_branch", branch), ("project_commit", commit)):
            if value:
                conn.execute("INSERT OR REPLACE INTO config (key, value) "
                             "VALUES (?, ?)", (key, value))
        conn.commit()
    finally:
        conn.close()
    return report


def cmd_onboard(args: argparse.Namespace) -> int:
    path = resolve(args.name)
    if path.exists():
        if not args.force:
            raise SystemExit(
                f"{path} exists. `rota run {args.name}` continues it, "
                f"`rota onboard {args.name} --force` starts over, "
                f"`rota onboard <other-name>` keeps both")
        wipe(path)

    root = Path(args.root).resolve()
    if not (root / ".git").exists():
        print(f"note: {root} is not a git checkout; batches will have no worktree")
    report = onboard(path, root)
    print(f"{args.name}: {report.areas} areas, {report.unsurveyed} under "
          f"constraint zero, {len(report.leaky)} leaky  ({path})")
    print(f"next: rota run {args.name}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    from .tools.onboard_run import drive

    path = require(args.name)
    drive(str(path), args.model, args.limit, survey_only=not args.all)
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    from . import compare

    print(compare.render(compare.runs(require(args.a), require(args.b))))
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    from .tools.onboard_run import audit, report

    path = require(args.name)
    if args.audit_only:
        return 1 if audit(str(path)) else 0
    report(str(path))
    return 0


def cmd_tui(args: argparse.Namespace) -> int:
    from .cockpit.tui import main as tui_main

    # No name is not an error. It is the first thing you ever type, and it lands
    # on the run list -- which is the screen that makes a run. Requiring a name
    # here left creating your first one as a command, which is the one trip to
    # the terminal the list exists to remove.
    if not args.name:
        return tui_main(["--model", args.model])
    path = resolve(args.name) if args.new else require(args.name)
    argv = ["--db", str(path), "--model", args.model]
    root = args.root or _root_of(path)
    if root:
        argv += ["--root", str(root)]
    return tui_main(argv)


def cmd_cockpit(args: argparse.Namespace) -> int:
    from .cockpit import server

    path = require(args.name)
    runner = server.serve if args.no_reload else server.serve_reloading
    runner(db=path, port=args.port, open_browser=args.open)
    return 0


def _root_of(path: Path) -> str:
    from .core.db import connect_readonly

    if not path.exists():
        return ""
    try:
        conn = connect_readonly(path)
    except sqlite3.Error:
        return ""
    try:
        row = conn.execute(
            "SELECT value FROM config WHERE key = 'project_root'").fetchone()
        return (row["value"] if row else "").strip('"')
    except sqlite3.Error:
        return ""
    finally:
        conn.close()


# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    from .llm.llm import DEFAULT_MODEL

    ap = argparse.ArgumentParser(prog="rota", description=__doc__.strip(),
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("ls", help="what runs exist, and what state each is in")
    p.set_defaults(func=cmd_ls)

    p = sub.add_parser("onboard", help="index a checkout into a new run")
    p.add_argument("name")
    p.add_argument("--root", required=True, help="the checkout to onboard")
    p.add_argument("--force", action="store_true",
                   help="wipe an existing run of this name first")
    p.set_defaults(func=cmd_onboard)

    p = sub.add_parser("run", help="turn the crank until quiescent")
    p.add_argument("name")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--limit", type=int, default=40)
    p.add_argument("--all", action="store_true",
                   help="do not stop when the survey wakes run out")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("tui", help="talk to it, with the register beside you")
    p.add_argument("name", nargs="?", help="omit to open the run list")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--root", help="override the project recorded in the run")
    p.add_argument("--new", action="store_true",
                   help="allow creating this run rather than opening one")
    p.set_defaults(func=cmd_tui)

    p = sub.add_parser("cockpit", help="the rows, the graph and the trace")
    p.add_argument("name")
    p.add_argument("--port", type=int, default=8899)
    p.add_argument("--open", action="store_true", help="open a browser tab")
    p.add_argument("--no-reload", action="store_true")
    p.set_defaults(func=cmd_cockpit)

    p = sub.add_parser("report", help="what came out, and the mechanical audit")
    p.add_argument("name")
    p.add_argument("--audit-only", action="store_true")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("diff", help="two runs, side by side, unscored")
    p.add_argument("a")
    p.add_argument("b")
    p.set_defaults(func=cmd_diff)

    p = sub.add_parser("wipe", help="worktrees, processes, then the file")
    p.add_argument("name")
    p.add_argument("--yes", action="store_true", help="do not ask")
    p.set_defaults(func=cmd_wipe)

    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":                                  # pragma: no cover
    sys.exit(main())
