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
RUNS = paths.RUNS


class WipeRefused(Exception):
    """A wipe that changed nothing, and why.

    An ordinary exception rather than `SystemExit`, because `wipe` is a library
    function with two callers and only one of them is a shell. Raised as
    `SystemExit` it travelled out of a Textual callback, through the message
    pump and asyncio, and killed the seat -- so the operator was told the run
    was open in another process *and* lost the window they would have closed it
    from. `SystemExit` inherits from `BaseException`, so every `except
    Exception` that exists to keep a UI alive lets it through by design.

    `cmd_wipe` turns it back into a `SystemExit` at the command line, where
    exiting is the right answer.
    """


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


def _when(text: str) -> float:
    """
    `datetime('now')` text as epoch seconds. 0.0 when it cannot be read.

    SQLite writes these stamps in UTC, so they are read back in UTC. A stamp
    this cannot parse is treated as absent rather than as a date, because a
    wrong date sorts and an absent one does not.
    """
    from datetime import datetime, timezone

    try:
        return (datetime.strptime(text.strip(), "%Y-%m-%d %H:%M:%S")
                .replace(tzinfo=timezone.utc).timestamp())
    except (AttributeError, ValueError):
        return 0.0


def _file_times(path: Path) -> tuple[float, float]:
    """
    What the file system knows, for the runs that were made before the stamps
    existed.

    Every run in `RUNS` today predates `created_at` and `opened_at`, and a
    column of dashes for all of them would make the list's default order
    useless on the day it ships. The file answers approximately. Creation time
    is creation time on Windows, where this runs. Last write is not last open,
    but a run that was worked on was written to.
    """
    try:
        stat = path.stat()
    except OSError:
        return 0.0, 0.0
    return getattr(stat, "st_birthtime", stat.st_ctime), stat.st_mtime


def _read(path: Path, ask_git: bool = True) -> dict:
    from .core.db import connect_readonly, schema_stale

    created, opened = _file_times(path)
    row: dict = {"name": path.stem, "path": str(path), "root": "", "error": "",
                 "counts": {}, "state": "", "branch": "", "commit": "",
                 "moved": False, "created": created, "opened": opened}
    try:
        conn = connect_readonly(path)
    except sqlite3.Error as exc:
        row["error"] = str(exc)
        return row
    try:
        recorded = {r["key"]: (r["value"] or "").strip('"') for r in conn.execute(
            "SELECT key, value FROM config WHERE key IN "
            "('project_root', 'project_branch', 'project_commit', "
            "'created_at', 'opened_at')")}
        # The run's own answer beats the file's, where the run has one.
        for field, key in (("created", "created_at"), ("opened", "opened_at")):
            if recorded.get(key):
                row[field] = _when(recorded[key])
        row["root"] = recorded.get("project_root", "")
        row["branch"] = recorded.get("project_branch", "")
        row["commit"] = recorded.get("project_commit", "")
        # Has the tree moved past the receipt? The same comparison
        # `boot.reconcile_worktrees` makes for a batch, one level up. Runs
        # onboarded before the commit was recorded simply do not answer.
        #
        # `ask_git` is how `runs()` takes this question away and answers it
        # for the whole directory at once. One run asked alone still asks
        # here, because one `git` call is nothing and a caller reading one
        # run wants the answer in the row it gets back.
        if ask_git and row["commit"] and row["root"]:
            _, now = checkout_of(row["root"])
            row["moved"] = bool(now) and now != row["commit"]
        for table in COUNTED:
            got = conn.execute(f"SELECT COUNT(*) n FROM {table}").fetchone()
            row["counts"][table] = got["n"]
        # A run from before the refs relation. `init_db` refuses it with
        # this sentence, and the list says the same sentence, not the
        # first table the frontier fails to find.
        stale = schema_stale(conn)
        if stale:
            row["state"] = "stale"
            row["error"] = stale
            return row
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


def _mark_moved(rows: list[dict]) -> None:
    """
    Ask each checkout where it is now, once per checkout and all at once.

    This is what listing costs. Reading 67 runs took 6.5 seconds, and 6.2 of
    them were `git`: `checkout_of` spawns two processes, `_read` called it
    once per run, and a process costs about 45ms to start on Windows.

    Two facts make that cheap. **A tree has one HEAD**, so 55 runs against 24
    checkouts is 24 questions and not 55. And **a question about another
    process is a wait**, so the questions go together rather than in turn.

    Deliberately per call, not a cache with a life of its own. A listing is a
    photograph of the directory, and the whole point of the column is that it
    is true when it is shown.
    """
    from concurrent.futures import ThreadPoolExecutor

    asking = {row["root"] for row in rows if row["commit"] and row["root"]}
    if not asking:
        return
    roots = sorted(asking)
    with ThreadPoolExecutor(max_workers=min(8, len(roots))) as pool:
        heads = dict(zip(roots, pool.map(lambda r: checkout_of(r)[1], roots)))
    for row in rows:
        now = heads.get(row["root"], "")
        row["moved"] = bool(now) and bool(row["commit"]) and now != row["commit"]


def runs() -> list[dict]:
    if not RUNS.is_dir():
        return []
    rows = [_read(p, ask_git=False) for p in sorted(RUNS.glob("*.db"))]
    _mark_moved(rows)
    return rows


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
        raise WipeRefused(
            f"{path.name} is open in another process -- close the seat or "
            f"cockpit holding it, then wipe again. Nothing was removed.")
    try:
        os.rename(probe, path)
    except OSError as exc:                                      # pragma: no cover
        raise WipeRefused(
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
    try:
        removed = wipe(path)
    except WipeRefused as exc:
        # A sentence, not a traceback. Exiting is the right answer *here*.
        raise SystemExit(str(exc)) from None
    print(f"wiped {path.stem}: {len(removed['worktrees'])} worktree(s), "
          f"{len(removed['pids'])} process(es), {', '.join(removed['files'])}")
    return 0


# ---------------------------------------------------------------------------
# The verbs that do the work. Each one is the existing tool, given a run.
# ---------------------------------------------------------------------------

def checkout_of(root: str | Path) -> tuple[str, str]:
    """
    The branch and commit a checkout is on. One implementation, in onboarding.

    This was a second copy here, which is how the recording ended up happening
    on some paths and not others in the first place.
    """
    from .onboarding.boot import checkout_of as _checkout_of

    return _checkout_of(root)


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
    from .llm import profile as profile_mod
    from .core.db import connect as _connect

    prof = profile_mod.find(args.profile or profile_mod.default_name(), root)
    problems = prof.check()
    if problems:
        wipe(path)
        raise SystemExit("profile " + prof.name + ": " + "; ".join(problems))
    _conn = _connect(path)
    profile_mod.bind(_conn, prof)
    _conn.commit(); _conn.close()
    where = prof.endpoint or ("local ollama" if prof.provider == "ollama" else prof.provider)
    print(f"profile: {prof.name}  sends prompts and this repository's code to "
          f"{where} ({prof.provider}); from a file under "
          f"{'the project' if '.rota' in str(getattr(prof, 'source', '') or '') else 'rota or your home'}")
    print(f"profile: {prof.name}  default {prof.default_model}"
          + (f"  roles {prof.routing()}" if prof.roles else ""))
    if getattr(args, "no_prose", False):
        from .core import config
        from .core.db import connect

        conn = connect(path)
        config.set(conn, "prose_sources", "off")
        conn.commit(); conn.close()
    print(f"{args.name}: {report.areas} areas, {report.unsurveyed} under "
          f"constraint zero, {len(report.leaky)} leaky  ({path})"
          + ("  [prose withheld]" if getattr(args, "no_prose", False) else ""))
    for line in getattr(report, "stresses", []):
        print(f"  {line}")
    print(f"next: rota run {args.name}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    import os

    from .tools.onboard_run import drive

    path = require(args.name)
    # A filter on the phase order that already exists, for measuring one phase
    # without paying for the two behind it. Set in the environment rather than
    # threaded through `drive` because it is a debug affordance and should not
    # become an argument the system takes seriously.
    if getattr(args, "until", None):
        os.environ["ROTA_SURVEY_UNTIL"] = args.until
    from .core.db import connect as _connect, schema_stale
    from .llm import profile as profile_mod

    conn = _connect(path)
    stale = schema_stale(conn)
    if stale:
        conn.close()
        raise SystemExit(f"{args.name}: {stale}")
    prof = profile_mod.of_run(conn) or profile_mod.find(profile_mod.default_name())
    roles = {}
    for item in getattr(args, "role", []) or []:
        role, _, model = item.partition("=")
        if not model:
            raise SystemExit(f"--role wants ROLE=MODEL, got {item!r}")
        roles[role] = model
    if args.model or roles:
        prof = prof.with_override(model=args.model, roles=roles)
        profile_mod.bind(conn, prof)      # recorded, with history
        conn.commit()
    conn.close()
    drive(str(path), prof.default_model, args.limit, survey_only=not args.all,
          profile=prof)
    return 0


def cmd_cassettes(args: argparse.Namespace) -> int:
    """
    The cassette database is published as a release asset and fetched on
    demand; `rota/testkit/cassette_store.py` says why and what is checked.
    """
    from pathlib import Path as _Path

    from .testkit import cassette_store as store

    if args.action == "status":
        return store.status()
    if args.action == "pull":
        store.pull(force=args.force)
        return 0
    out = _Path(args.out).resolve() if args.out else None
    if args.action == "pack":
        gz, m = store.pack(out_dir=out, tag=args.tag)
        print(f"{gz}  {m.bytes_gz/1e6:.0f} MB gzip of {m.bytes_db/1e6:.0f} MB, "
              f"{m.cassettes} cassettes, {m.case_runs} case runs")
        print(f"manifest written: {store.MANIFEST}")
        return 0
    if args.action == "publish":
        gz, m = store.pack(out_dir=out, tag=args.tag)
        return store.publish(gz, m)
    raise SystemExit(f"rota cassettes: unknown action {args.action}")


def cmd_profile(args: argparse.Namespace) -> int:
    import json as _json

    from .llm import profile as profile_mod

    root = Path(args.root).resolve() if getattr(args, "root", None) else None
    if args.action == "list":
        for name, src in profile_mod.available(root):
            print(f"{name:20} {src}")
        return 0
    if not args.target:
        raise SystemExit(f"rota profile {args.action} needs a name")
    if args.action == "set":
        if not args.assignment or "=" not in args.assignment:
            raise SystemExit("rota profile set <run> dotted.key=value")
        from .core.db import connect as _connect

        conn = _connect(require(args.target))
        key, _, value = args.assignment.partition("=")
        prof = profile_mod.set_field(conn, key, value)
        conn.commit(); conn.close()
        print(f"{args.target}: {key} = {value}  (profile {prof.name}, new snapshot)")
        return 0
    run_path = resolve(args.target)
    if run_path.exists():
        from .core.db import connect as _connect

        conn = _connect(run_path)
        prof = profile_mod.of_run(conn)
        conn.close()
        if prof is None:
            raise SystemExit(f"run {args.target} has no profile bound")
    else:
        prof = profile_mod.find(args.target, root)
    if args.action == "show":
        print(_json.dumps(prof.to_dict(), indent=1))
        return 0
    if args.action == "toolcheck":
        # Two fixed prompts against every model the profile names, recorded
        # like cases under their own tier (plans/model-setup.md, step 4).
        from . import paths
        from .llm import cassettes, toolcheck

        backend = prof.backend()
        dev = cassettes.open_dev_db(paths.DEV_DB)
        failed = 0
        for model in sorted({prof.default_model, *prof.roles.values()}):
            pins = prof.pins_for(None)
            pins = pins.__class__(**{**pins.__dict__, "model": model})
            res = toolcheck.check(backend, pins)
            line_id, native_id = toolcheck.case_ids(prof.name)
            cassettes.record_case_run(dev, line_id, pins, 1, res.tool_line,
                                      [] if res.tool_line else [res.problems[0]],
                                      [{"say": res.tool_line_said}])
            cassettes.record_case_run(dev, native_id, pins, 1, res.native_call,
                                      [] if res.native_call else [res.problems[-1]],
                                      [{"say": res.native_said}])
            dev.commit()
            print(f"{model:24} TOOL: line {'ok' if res.tool_line else 'FAIL'}   "
                  f"native call {'ok' if res.native_call else 'FAIL'}")
            failed += (not res.tool_line) + (not res.native_call)
        dev.close()
        print(f"{prof.name}: " + ("supported" if not failed else f"{failed} check(s) failed"))
        return 1 if failed else 0
    problems = prof.check()
    for line in problems:
        print(f"  {line}")
    print(f"{prof.name}: " + ("ok" if not problems else f"{len(problems)} problem(s)"))
    return 1 if problems else 0


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


def cmd_refresh(args: argparse.Namespace) -> int:
    """
    Stay true: re-index the checkout and reopen what changed.

    The index is rebuilt at the tree as it stands, the partition and
    constraint zero re-derived over it, and every survey record whose stamped
    view no longer matches its area's content stops counting -- the same
    machinery that surveyed re-surveys, and an unchanged area stays closed.
    """
    from .core.db import connect
    from .core.scheduler import tick_survey
    from .onboarding import indexer

    path = require(args.name)
    conn = connect(path)
    try:
        root = args.root or _root_of(path)
        if not root:
            raise SystemExit("this run records no project root; pass --root")
        # The same function the lifecycle calls when a batch stops running, so
        # the operator's refresh and the loop's cannot drift apart.
        done = indexer.refresh(conn, root, main=True)
        report, branch, commit = done.index, done.branch, done.commit
        conn.commit()
        reopened = sorted({w.refs[0] for w in tick_survey(conn)})
        from .tools.audit import orphaned_grain_refs

        orphans = orphaned_grain_refs(conn)
    finally:
        conn.close()
    print(f"{args.name}: {report.files} files re-indexed"
          + (f" at {branch}@{commit[:7]}" if commit else ""))
    if reopened:
        print(f"reopened: {', '.join(reopened)}")
        print(f"next: rota run {args.name}")
    else:
        print("nothing changed since the last survey")
    # A rebuilt index can strand references to grains that vanished. Not the
    # refresh's to fix -- rebinding is the owner's judgement -- but a silently
    # disarmed tripwire must never be silent.
    for line in orphans:
        print(f"orphaned: {line}")
    return 0


def cmd_agenda(args: argparse.Namespace) -> int:
    """What is waiting on the principal, and what the system does not know."""
    from .core.db import connect_readonly
    from .core.predicates import outstanding
    from .roles.principal import pending_asks

    from .roles.principal import pending_replies, render_state

    conn = connect_readonly(require(args.name))
    asks = pending_asks(conn)
    if not asks:
        # "nothing is waiting on you" was the whole answer. A finished run, a
        # run stuck with red tests, and a run nobody started printed the same
        # line. The agenda is where a person looks to learn what happened.
        print(render_state(conn))
    for a in asks:
        print(f"[{a.message_id}] {a.verb} · rule by id: {', '.join(a.refs)}")
        if a.rendered:
            for line in a.rendered.splitlines()[:args.limit]:
                print(f"  {line}")
            if len(a.rendered.splitlines()) > args.limit:
                print(f"  ... {len(a.rendered.splitlines()) - args.limit} more")
    # Liaison's own words. They are displayed, not asked. "Displayed" meant
    # displayed by the TUI only, so the command line never saw them.
    replies = pending_replies(conn)
    if replies:
        print("\nsaid to you (no answer needed, but you can reply):")
        for r in replies:
            for line in (r.rendered or "").splitlines()[:args.limit]:
                print(f"  {line}")
            print(f"  reply with: rota sign {args.name} {r.message_id} --say '...'")

    # Only what is outstanding. Every obligation printed at n=0 hid the real
    # rows in a table of zeroes.
    rows = [r for r in outstanding(conn) if r["count"]]
    if rows:
        print("\noutstanding:")
        for r in rows:
            print(f"  {r['obligation']:22s} n={r['count']:<4} "
                  f"owners={','.join(r['owners'])}")
    return 0


def cmd_elect(args: argparse.Namespace) -> int:
    """
    The election, recorded verbatim. It is the principal's call and nothing
    else's -- no session decides it, interprets it, or writes it -- so the
    seat writes the config row directly and the register does the rest:
    `eager` presents the baseline for signoff, `lazy` defers every observed
    row to the ledger in its own words, awaiting first touch.
    """
    from .core.db import connect

    conn = connect(require(args.name))
    try:
        from .core import config as config_mod

        config_mod.set(conn, "baseline_election", args.choice,
                       author="principal")
        conn.commit()
    finally:
        conn.close()
    print(f"baseline election: {args.choice}  (next: rota run {args.name})")
    return 0


def cmd_interrupt(args: argparse.Namespace) -> int:
    """The principal stops the running batch. A pause, not a verdict: the
    worktree and its commits survive, and `batch_start` re-offers the batch
    the moment nothing outranks it. Cancelling is a ruling and goes through
    scope; this is the brake pedal."""
    from .core import lifecycle
    from .core.db import connect

    conn = connect(require(args.name))
    try:
        row = conn.execute(
            "SELECT id FROM batches WHERE status = 'running'").fetchone()
        if not row:
            print("nothing is running")
            return 0
        lifecycle.defer(conn, row["id"])
        conn.commit()
        print(f"deferred {row['id']}: it resumes when scheduled again "
              f"(rota run {args.name})")
    finally:
        conn.close()
    return 0


def cmd_sign(args: argparse.Namespace) -> int:
    """
    Answer one gate. Through `pump`, deliberately: every principal backend
    records a ruling the same way, so the CLI cannot invent a second one.
    """
    from .core.db import connect
    from .roles.principal import Answer, pump

    approve = [x for x in (args.approve or "").split(",") if x]
    contest = [x for x in (args.contest or "").split(",") if x]
    if not (approve or contest or args.say):
        raise SystemExit("say what you rule: --approve ids, --contest ids, "
                         "or --say 'words'")

    class OneShot:
        name = "cli"

        def respond(self, ask):
            if ask.message_id != args.ask:
                return None                       # defer everything else
            # Words alone are a reply. Words with a ruling are its reason.
            # `--say` returned before the ruling was read, so a contest and
            # its reason were two commands and two unrelated acts.
            if args.say and not (approve or contest):
                # Words on a page are a reply the Liaison reads (landing).
                verb = "reply" if ask.verb in ("confirm", "present") else "converse"
                return Answer(verb=verb, text=args.say)
            per_item = {i: "approve" for i in approve}
            per_item.update({i: "contest" for i in contest})
            unknown = [i for i in per_item if i not in ask.refs]
            if unknown:
                raise SystemExit(f"{unknown} are not on this gate; it asks "
                                 f"about {ask.refs}")
            return Answer(verb="verdict", per_item=per_item,
                          text=args.say or "")

    conn = connect(require(args.name))
    try:
        created = pump(conn, OneShot())
        conn.commit()
    finally:
        conn.close()
    if not created:
        raise SystemExit(f"{args.ask} is not an open gate; `rota agenda "
                         f"{args.name}` lists them")
    print(f"ruling recorded: {created[0]}  (next: rota run {args.name})")
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

    runner = server.serve if args.no_reload else server.serve_reloading
    if args.name is None:
        # No name means the run you were just working on. The server owns
        # that guess — newest sibling that will actually open, said aloud —
        # so there is one chooser, not two ideas of "latest".
        runner(project_root=str(paths.REPO), port=args.port,
               open_browser=args.open)
        return 0
    path = require(args.name)
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
    p.add_argument("--no-prose", action="store_true",
                   help="withhold README/docs from every session: measure "
                        "understanding on code, schema and manifest alone")
    p.add_argument("--profile", default=None,
                   help="the run profile to freeze into the run "
                        "(default: $ROTA_PROFILE or 'local'; rota profile list)")
    p.set_defaults(func=cmd_onboard)

    p = sub.add_parser("run", help="turn the crank until quiescent")
    p.add_argument("name")
    p.add_argument("--model", default=None,
                   help="override the profile's default model for this run")
    p.add_argument("--role", action="append", default=[], metavar="ROLE=MODEL",
                   help="override one desk's model for this run; repeatable")
    p.add_argument("--limit", type=int, default=40)
    p.add_argument("--all", action="store_true",
                   help="do not stop when the survey wakes run out")
    p.add_argument("--until", choices=("terminologist", "architect", "vision_keeper"),
                   help="stop after this survey phase (debugging)")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("refresh", help="re-index the checkout; reopen what changed")
    p.add_argument("name")
    p.add_argument("--root", help="override the project recorded in the run")
    p.set_defaults(func=cmd_refresh)

    p = sub.add_parser("agenda", help="what is waiting on you")
    p.add_argument("name")
    p.add_argument("--limit", type=int, default=12,
                   help="rendered lines per gate")
    p.set_defaults(func=cmd_agenda)

    p = sub.add_parser("interrupt",
                       help="stop the running batch; it resumes when scheduled")
    p.add_argument("name")
    p.set_defaults(fn=cmd_interrupt)

    p = sub.add_parser("adopt", aliases=["elect"],
                   help="adopt the onboarded understanding as the baseline")
    p.add_argument("name")
    p.add_argument("choice", choices=("eager", "lazy"))
    p.set_defaults(func=cmd_elect)

    p = sub.add_parser("sign", help="answer one gate from the agenda")
    p.add_argument("name")
    p.add_argument("ask", help="the gate's message id, from `rota agenda`")
    p.add_argument("--approve", help="comma-separated row ids")
    p.add_argument("--contest", help="comma-separated row ids")
    p.add_argument("--say", help="answer a clarify in words instead")
    p.set_defaults(func=cmd_sign)


    p = sub.add_parser("profile", help="run profiles: list, show, check, set")
    p.add_argument("action", choices=("list", "show", "check", "set", "toolcheck"))
    p.add_argument("target", nargs="?", help="a profile name, or a run name for set")
    p.add_argument("assignment", nargs="?", help="set: dotted.key=value")
    p.add_argument("--root", help="a project whose .rota/profiles to include")
    p.set_defaults(func=cmd_profile)

    p = sub.add_parser("cassettes", help="the recorded model turns: status, pull, pack, publish")
    p.add_argument("action", choices=("status", "pull", "pack", "publish"))
    p.add_argument("--force", action="store_true",
                   help="pull: replace a local database (it may hold unpublished recordings)")
    p.add_argument("--tag", help="pack/publish: release tag, default cassettes-YYYYMMDD")
    p.add_argument("--out", help="pack/publish: directory for the gzip, default the temp dir")
    p.set_defaults(func=cmd_cassettes)

    p = sub.add_parser("tui", help="talk to it, with the register beside you")
    p.add_argument("name", nargs="?", help="omit to open the run list")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--root", help="override the project recorded in the run")
    p.add_argument("--new", action="store_true",
                   help="allow creating this run rather than opening one")
    p.set_defaults(func=cmd_tui)

    p = sub.add_parser("cockpit", help="the rows, the graph and the trace")
    p.add_argument("name", nargs="?",
                   help="a run name; omitted, the most recently touched run")
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
