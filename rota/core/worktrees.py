"""
A worktree per batch. Created, kept, and destroyed by the scheduler.

The Developer never makes one. Law 9 puts every decision about a worktree's life
outside the role: one is created when a batch is dispatched, it survives
deferral with its commits intact, and it is destroyed only when the batch
merges. A role that could create its own would be deciding where its work lives,
which is a scheduling question wearing a tool.

**Nothing here removes a worktree it did not create.** The rule is the one the
test fixture uses and it exists for the same reason: this repository has 107
live worktrees. A removal is refused unless the path is recorded on the batch
*and* is under the state directory — two conditions, because either alone can be
satisfied by an accident.
"""
from __future__ import annotations

import shutil
import sqlite3
import subprocess

# Every git command rota runs. Hooks are the repository's code, and a
# checkout's hooks run on commit and merge with the user's rights; rota
# commits and merges what a model wrote, so its git runs with no hooks.
# The path names a directory that does not exist, which git treats as no
# hooks at all. Audit item 3 (rota/AUDIT.md, 2026-09-10).
GIT = ["git", "-c", "core.hooksPath=.rota/hooks-off"]
from pathlib import Path


class WorktreeError(RuntimeError):
    """Git refused, or the path was not ours to touch."""


def grain_path(grain: str) -> str:
    """
    The file a grain lives in, normalised for comparison.

    Grains come in two shapes — `oauth1/rfc5849/signature.py` and
    `oauth1/rfc5849/signature.py::sign_hmac` — and a session that read the file
    has read the symbol. Backslashes fold to forward, because the index is built
    on one platform and read on another.

    The fold lives in core because `batch_furniture` folds the test paths
    by it, and the roles layer reads it as `api._grain_path` (F27).
    """
    g = grain.split("::", 1)[0].replace("\\", "/").strip()
    # Prefixes, not a character set: `lstrip("./")` made `.github/ci.py`
    # into `github/ci.py`, which no index row holds (frame 91's diff review).
    while g.startswith(("./", "/")):
        g = g[2:] if g.startswith("./") else g[1:]
    return g


def batch_furniture(conn: sqlite3.Connection, batch_id: str) -> set[str]:
    """
    The batch's materialised test files, folded by `grain_path`.

    The harness writes these files at run time, and the Developer's commits
    leave them out. So no commit owns them, and no discard removes them.
    This is the one reader of that set (F27). `code.diff`, `code.write`,
    `code.commit`, the batch's file list and the discard at a session's end
    all read it, so they keep the same files.

    law 4: an uncommitted change never existed. The furniture is no change
    of the session, so it stays.
    """
    return {grain_path(r[0]) for r in conn.execute(
        "SELECT path FROM tests WHERE batch_id = ?", (batch_id,)) if r[0]}


def _git(root: Path, *args: str, check: bool = True) -> str:
    out = subprocess.run([*GIT, "-C", str(root), *args],
                         capture_output=True, text=True)
    if check and out.returncode != 0:
        raise WorktreeError(f"git {' '.join(args)}: {out.stderr.strip()}")
    return out.stdout


def project_root(conn: sqlite3.Connection) -> Path:
    """
    The project this database is about. **No default.**

    It used to fall back to `Path(".")`, which means the current working
    directory — so any session run without a configured root created a git
    worktree *in whatever repository the process happened to be started from*.
    That is exactly what happened: a test called `lifecycle.start` with no
    config and left a `batch/b1` worktree inside this repo, alongside the 107
    real ones.

    A missing root is a configuration error, and creating a worktree is not the
    kind of operation that gets to guess.
    """
    row = conn.execute(
        "SELECT value FROM config WHERE key = 'project_root'").fetchone()
    if not row or not (row["value"] or "").strip():
        raise WorktreeError(
            "no project_root in config: refusing to guess which repository to "
            "create a worktree in")
    return Path(row["value"].strip('"'))


def worktree_home(conn: sqlite3.Connection) -> Path:
    """
    Where batch worktrees live: `<project>/.rota/worktrees`.

    Inside the state directory rather than beside the project, so everything the
    system created is in one place and the boundary of "ours" is a path prefix
    rather than a naming convention.
    """
    return project_root(conn) / ".rota" / "worktrees"


def is_ours(conn: sqlite3.Connection, path: str | Path) -> bool:
    home = worktree_home(conn).resolve()
    try:
        target = Path(path).resolve()
    except OSError:
        return False
    return home == target or home in target.parents


def create(conn: sqlite3.Connection, batch_id: str) -> Path:
    """
    A branch and a worktree for one batch.

    A batch that already has one keeps it — that is what makes resuming a
    deferred batch a cold session in its *surviving* worktree rather than a
    fresh start, which is the whole reason commit-first bounds the loss.
    """
    row = conn.execute(
        "SELECT worktree FROM batches WHERE id = ?", (batch_id,)).fetchone()
    if row is None:
        raise WorktreeError(f"no such batch: {batch_id}")
    if row["worktree"] and Path(row["worktree"]).is_dir():
        return Path(row["worktree"])

    root = project_root(conn)
    path = worktree_home(conn) / batch_id
    path.parent.mkdir(parents=True, exist_ok=True)

    branch = f"batch/{batch_id}"
    # A batch with no worktree on record never had one, so whatever stands
    # at its path is another run's. Two runs on one root name their first
    # batch b_1: the second's `worktree add` failed on the first's
    # directory, the failure was swallowed, and the Developer wrote and
    # committed on the project's master (tipsP, 2026-09-09). The stale
    # worktree goes; its branch is kept under a dated name as the record.
    if path.exists():
        _git(root, "worktree", "remove", "--force", str(path), check=False)
        shutil.rmtree(path, ignore_errors=True)
        _git(root, "worktree", "prune", check=False)
        old_sha = _git(root, "rev-parse", "--short", branch, check=False).strip()
        if old_sha:
            _git(root, "branch", "-m", branch, f"{branch}@{old_sha}", check=False)
    existing = _git(root, "branch", "--list", branch, check=False).strip()
    # A batch that has not started yet never inherits a branch. clickI
    # (2026-09-11): `onboard --force` wiped the database and not the
    # repository, the old `batch/batch_1` stayed, the new batch checked it
    # out and the old run's `__future__.py` broke every test again.
    started = conn.execute(
        "SELECT head_commit FROM batches WHERE id = ?", (batch_id,)).fetchone()
    if existing and not (started and started["head_commit"]):
        old_sha = _git(root, "rev-parse", "--short", branch, check=False).strip()
        _git(root, "branch", "-m", branch, f"{branch}@{old_sha or 'old'}", check=False)
        existing = ""
    args = ["worktree", "add", "-q"]
    args += [str(path), branch] if existing else ["-b", branch, str(path)]
    _git(root, *args)

    conn.execute("UPDATE batches SET worktree = ? WHERE id = ?",
                 (str(path), batch_id))
    return path


def destroy(conn: sqlite3.Connection, batch_id: str) -> bool:
    """
    Remove a merged batch's worktree. Refused for anything not ours.

    The branch is left behind on purpose: it is the record of what was built,
    and deleting it would make a merged batch harder to inspect than an
    abandoned one.
    """
    row = conn.execute(
        "SELECT worktree FROM batches WHERE id = ?", (batch_id,)).fetchone()
    path = row and row["worktree"]
    if not path:
        return False
    if not is_ours(conn, path):
        raise WorktreeError(
            f"refusing to remove a worktree outside {worktree_home(conn)}: {path}")

    _git(project_root(conn), "worktree", "remove", "--force", str(path), check=False)
    shutil.rmtree(path, ignore_errors=True)
    conn.execute("UPDATE batches SET worktree = NULL WHERE id = ?", (batch_id,))
    return True


def head(path: str | Path) -> str | None:
    out = subprocess.run([*GIT, "-C", str(path), "rev-parse", "HEAD"],
                         capture_output=True, text=True)
    return out.stdout.strip() or None if out.returncode == 0 else None


def commit(path: str | Path, message: str, exclude: tuple[str, ...] = (),
           only: tuple[str, ...] = ()) -> str | None:
    """
    Stage everything and commit. Returns the sha, or None if nothing changed.

    `only` names the paths to stage and commit, and nothing else goes in.
    The structure's restore commits its own paths only. A Developer's
    untracked file stays out of that commit (law 1, frame 173 review p1).

    None is not a failure. A Developer session that reasoned, read and concluded
    the code was already right has nothing to commit, and inventing an empty
    commit to have something to report would be worse than saying so.
    """
    # Everything but the harness's own furniture. The batch's venv and the
    # run's state live inside the worktree and are not the project's:
    # under WSL (2026-09-10) `add -A` staged 952 files of `.venv` into the
    # first commit and the Critic reviewed them as the diff.
    # `exclude` names paths the caller does not own: the Tester's test
    # files under a Developer commit (2026-09-14). They stay in the
    # worktree and out of the commit.
    named = [p.replace(chr(92), "/") for p in only if p]
    if named:
        subprocess.run([*GIT, "-C", str(path), "add", "--", *named],
                       capture_output=True, text=True)
    else:
        specs = [":(exclude)" + p.replace(chr(92), "/") for p in exclude if p]
        subprocess.run([*GIT, "-C", str(path), "add", "-A", "--", ".",
                        ":(exclude).venv", ":(exclude).rota", *specs],
                       capture_output=True, text=True)
    staged = subprocess.run([*GIT, "-C", str(path), "diff", "--cached", "--name-only",
                             "--", *named], capture_output=True, text=True).stdout.strip()
    if not staged:
        return None
    # A pathspec on the commit takes those paths only, so an index entry
    # that another writer staged stays out too.
    out = subprocess.run([*GIT, "-C", str(path), "commit", "-q", "-m", message,
                          *(["--", *named] if named else [])],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise WorktreeError(f"commit failed: {out.stderr.strip()}")
    return head(path)


def changed_since(path: str | Path, sha: str | None) -> list[str]:
    """
    The files that differ between a commit and the working tree now, the
    working tree's uncommitted and untracked files included.

    The fact behind finding 66 (2026-09-14): a test run is a statement about
    one commit, and a Developer that wrote a file and loaded the tests read
    the old red as the present. An unknown `sha` (a fixture's, or a
    rewritten history) counts the working tree alone. The harness's own
    furniture, `.venv` and `.rota`, is never a change.
    """
    root = str(path)
    out: set[str] = set()
    if sha:
        run = subprocess.run([*GIT, "-C", root, "diff", "--name-only", sha],
                             capture_output=True, text=True)
        if run.returncode == 0:
            out.update(line.strip() for line in run.stdout.splitlines() if line.strip())
    run = subprocess.run([*GIT, "-C", root, "status", "--porcelain", "--untracked-files=all"],
                         capture_output=True, text=True)
    if run.returncode == 0:
        for line in run.stdout.splitlines():
            if len(line) > 3:
                out.add(line[3:].strip().strip('"'))
    return sorted(p for p in out
                  if not p.startswith((".venv/", ".rota/")) and p not in (".venv", ".rota"))


def _git_paths(root: Path, args: list[str], paths: list[str]) -> bool:
    """Run a git command on `paths` through a NUL-separated pathspec file
    on stdin, each path literal. True when git succeeds. A quoted or
    non-ASCII name holds, and a glob character is no pattern (frame 297's
    review 3, finding 5)."""
    run = subprocess.run(
        [*GIT, "--literal-pathspecs", "-C", str(root), *args,
         "--pathspec-from-file=-", "--pathspec-file-nul"],
        input=b"\0".join(p.encode("utf-8") for p in paths), capture_output=True)
    return run.returncode == 0


def discard(path: str | Path, keep: set[str] = frozenset(),
            failed_out: list[str] | None = None) -> list[str]:
    """
    Put every file that differs from HEAD back to HEAD, and remove each new
    file. Return the paths put back. `keep` names paths the caller does not
    own, and they stay. `failed_out` gets each path git could not put back.

    law 4: an uncommitted change never existed. Frame 297: night 156's s214
    ended with its write in bg_2's tree, and s215 inherited it.
    """
    root = Path(path)
    if not head(root):
        return []
    # `-z` gives each name raw, with no quotes and no octal escapes.
    run = subprocess.run([*GIT, "-C", str(root), "status", "--porcelain", "-z",
                          "--untracked-files=all"], capture_output=True)
    if run.returncode != 0:
        return []
    tokens = run.stdout.decode("utf-8", "surrogateescape").split("\0")
    tracked: list[str] = []
    staged: list[str] = []
    new: list[str] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        i += 1
        if len(tok) <= 3:
            continue
        code = tok[:2]
        # A rename or a copy gives the new side, then the old side, which
        # HEAD holds.
        sides = [(tok[3:], "new" if code[0] in "RC" else None)]
        if code[0] in "RC" and i < len(tokens):
            sides.append((tokens[i], "old"))
            i += 1
        for s, side in sides:
            if s.startswith((".venv/", ".rota/")) or s in (".venv", ".rota"):
                continue
            # `keep` holds `batch_furniture`'s folded paths, so the path
            # folds by the same rule (F27).
            if grain_path(s) in keep:
                continue
            if code == "??":
                new.append(s)
            elif code[0] == "A" or side == "new":
                # Staged and absent from HEAD: unstage it, then remove it.
                staged.append(s)
            else:
                tracked.append(s)
    failed: list[str] = []
    if tracked or staged:
        _git_paths(root, ["reset", "-q", "HEAD"], tracked + staged)
    if tracked and not _git_paths(root, ["checkout", "-q", "HEAD"], tracked):
        # The tree's own `core.autocrlf` applies, so a file comes back as a
        # checkout of this tree gives it (ruled: the coordinator, frame 297,
        # pass 4b). One bad path refuses the whole list, so each path goes
        # on its own.
        failed = [s for s in tracked
                  if not _git_paths(root, ["checkout", "-q", "HEAD"], [s])]
    for s in staged + new:
        try:
            (root / s).unlink(missing_ok=True)
        except OSError:
            failed.append(s)
    if failed_out is not None:
        failed_out.extend(sorted(set(failed)))
    return sorted((set(tracked) | set(staged) | set(new)) - set(failed))


def batch_files(conn: sqlite3.Connection, batch_id: str) -> list[str] | None:
    """The files the batch's diff changed: the worktree, committed and not,
    against its merge base with the project's HEAD. None when the batch has
    no worktree. A batch can hold several commits, so HEAD~1 is not it."""
    row = conn.execute("SELECT worktree FROM batches WHERE id = ?", (batch_id,)).fetchone()
    if not row or not row["worktree"] or not Path(row["worktree"]).is_dir():
        return None
    wt = Path(row["worktree"])
    try:
        base = _git(project_root(conn), "rev-parse", "HEAD").strip()
        mb = _git(wt, "merge-base", "HEAD", base).strip()
        files = set(_git(wt, "diff", "--name-only", mb).split())
        files |= set(changed_since(wt, None))
    except Exception:
        return None
    # The batch's materialised test files are the harness's furniture, not
    # the diff (night 66, 2026-09-14: the review moved its findings onto
    # them once the project's own tests were refused).
    furniture = batch_furniture(conn, batch_id)
    return sorted(f for f in files if grain_path(f) not in furniture)


def base(path: str | Path, root: str | Path | None) -> str:
    """
    The commit the batch forked from: its merge base with the project root.

    Frame 97. Night 100 (2026-09-30): bg_2's Developer committed a stray line
    and then removed it. The tree equalled HEAD~1, so three sessions read an
    empty diff and never saw the batch's real change. A batch holds several
    commits, so HEAD~1 is not the batch. The root can be a detached HEAD, so
    the base comes from its sha and never from a branch name. A path that is
    the root itself has no fork, and HEAD~1 stays the answer there.
    """
    if root is None:
        return "HEAD~1"
    try:
        if Path(path).resolve() == Path(root).resolve():
            return "HEAD~1"
        sha = _git(Path(root), "rev-parse", "HEAD").strip()
        fork = _git(Path(path), "merge-base", "HEAD", sha).strip() if sha else ""
    except (WorktreeError, OSError):
        return "HEAD~1"
    # A fork equal to the batch's HEAD means no commit yet. The diff of the
    # working tree against it is still the batch's change.
    return fork or "HEAD~1"


# The funcname of rota's diff driver: a `def`, an `async def` or a `class`
# in column 0. Git's own Python driver also matches an indented `def`, and
# an example `def` in a docstring then opens a hunk inside the docstring
# (frame 201's review 2, finding 1, probe p4). A method's hunk opens at its
# class line instead, and the kinds walk reads the class from there.
_ROTA_FUNCNAME = r"^((class|(async[ \t]+)?def)[ \t].*)$"


def _python_attributes() -> str | None:
    """A git attributes file that gives `*.py` rota's diff driver, or None
    when rota cannot write the file.

    The file lives outside every repository, so no file of a batch changes.
    A unique name and `os.replace` keep a concurrent git from reading a
    half-written file (frame 201's review 2, finding 4).
    """
    import os
    import tempfile
    want = b"*.py diff=rota\n"
    try:
        path = Path(tempfile.gettempdir()) / "rota-diff-python.gitattributes"
        if path.exists() and path.read_bytes() == want:
            return path.as_posix()
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name)
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(want)
            os.replace(tmp, path)
        except OSError:
            Path(tmp).unlink(missing_ok=True)
            raise
        return path.as_posix()
    except OSError:
        return None


def diff(path: str | Path, against: str = "HEAD~1", *,
         function_context: bool = False) -> str:
    """The diff of `path` from `against` to HEAD.

    `function_context` gives each hunk its whole function, `git diff -W`.
    A sample repository often has no `.gitattributes`, so rota's driver
    comes from a file rota writes. With no file, `-W` runs with git's
    default funcname, which finds each `def` in column 0 too.
    """
    extra: list[str] = []
    attributes = _python_attributes() if function_context else None
    if attributes:
        extra = ["-c", f"core.attributesFile={attributes}",
                 "-c", f"diff.rota.xfuncname={_ROTA_FUNCNAME}"]
    cmd = [*GIT, *extra, "-C", str(path), "diff"]
    if function_context:
        cmd.append("-W")
    out = subprocess.run([*cmd, against, "HEAD"],
                         capture_output=True, text=True)
    return out.stdout


def touched(path: str | Path, against: str = "HEAD~1") -> list[str]:
    """The paths a batch's diff changed — the grains structural review joins on."""
    out = subprocess.run(
        [*GIT, "-C", str(path), "diff", "--name-only", against, "HEAD"],
        capture_output=True, text=True)
    return [line for line in out.stdout.splitlines() if line.strip()]


def integrate(conn: sqlite3.Connection, batch_id: str) -> str:
    """
    Merge the batch's branch into the branch the project is on.

    S0 walk thirty-seven: the first batch the story ever delivered was
    marked merged, its worktree removed, and the project's main branch still
    held only the initial commit -- `merge` had never merged anything. The
    branch is the record; the base branch is the deliverable. A clean merge
    returns the new head. An unclean one is aborted and raised, because a
    conflict is a wake, never a silent resolution.
    """
    root = project_root(conn)
    branch = f"batch/{batch_id}"
    if not _git(root, "branch", "--list", branch, check=False).strip():
        raise WorktreeError(f"no branch {branch} to merge")
    out = subprocess.run(
        [*GIT, "-C", str(root), "-c", "user.email=rota@local", "-c", "user.name=rota",
         "merge", "--no-ff", "--no-edit", "-m", f"rota: deliver {batch_id}", branch],
        capture_output=True, text=True)
    if out.returncode != 0:
        subprocess.run([*GIT, "-C", str(root), "merge", "--abort"],
                       capture_output=True, text=True)
        raise WorktreeError(f"merge of {branch} is not clean: {out.stderr.strip()[:300]}")
    return _git(root, "rev-parse", "HEAD").strip()

