"""The warm snapshot's stamp: what onboarding depended on when it was taken.

A warm night (GAUNTLET_WARM=1) starts from `.rota/<run>_warm.db`, the
database at the first slicing wake, and skips onboarding. Onboarding is
then never measured again unless something forces it. This stamp is that
force. Roman, 2026-09-14: "we wont forget to rerun onboarding if something
changes right?"

`write(run, conn)` runs when walk.py takes the snapshot. It records a hash
of every file the snapshot's sessions ran under: the brief and tools of
each (role, mode) that committed a session, the graph, the predicates, the
scheduler, the boot, the schema (the hard set), and the runner, the desks
and the sandbox (the soft set).

`check(run)` runs before a warm start. A hard file changed: the snapshot
and the stamp are deleted and the night runs cold, which writes a new
snapshot. A soft file changed: the night stays warm and the log says which
files changed, so the reader knows the pushes may have moved. Four warm
nights in a row: cold, so onboarding is measured at least every fifth
night regardless.

    python probes/warm_stamp.py check clickI     # exit 0 warm, 1 cold
"""
import os
import hashlib
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HARD = ["rota/design/graph.json", "rota/core/boot.py", "rota/core/predicates.py",
        "rota/core/scheduler.py", "rota/core/schema.sql", "rota/core/db.py"]
# The profiles too: onboarding copies the profile's routing into the run
# database, so a warm snapshot keeps the desks' models from the night it was
# taken. Night 60 (2026-09-14) moved the Developer to qwen2.5:14b in the
# profile and a warm start would have run the 9B.
HARD += sorted(str(f.relative_to(REPO)).replace(chr(92), "/")
               for f in (REPO / "rota/llm/profiles").glob("*.toml"))
SOFT = ["rota/core/runner.py", "rota/roles/api.py", "rota/core/sandbox.py"]
MAX_WARM = 4


def _sha(rel: str) -> str:
    p = REPO / rel
    return hashlib.sha1(p.read_bytes()).hexdigest()[:12] if p.exists() else "missing"


def _head() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:                                      # noqa: BLE001
        return "?"


def prompt_files(conn) -> list[str]:
    """The brief and tool list of every (role, mode) the snapshot's
    sessions ran under, plus each role's base brief. The mode is the
    runner's own reading of the wake, so the file is the one the session
    was composed from."""
    sys.path.insert(0, str(REPO))
    from rota.core.runner import _mode_key
    from rota.core.scheduler import Wake

    files = set()
    for role, kind, trigger, detail, refs in conn.execute(
            "SELECT DISTINCT role, wake_kind, trigger_msg, wake_detail, wake_refs "
            "FROM sessions WHERE committed = 1"):
        try:
            refs = tuple(json.loads(refs or "[]"))
        except ValueError:
            refs = ()
        wake = Wake(role, kind or "message", message_id=trigger, refs=refs, detail=detail or "")
        try:
            mode = _mode_key(wake, conn)
        except Exception:                                  # noqa: BLE001
            mode = kind.split(":", 1)[-1] if kind else ""
        for name in (mode, "base"):
            for ext in (".md", ".tools"):
                rel = f"rota/roles/prompts/{role}/{name}{ext}"
                if (REPO / rel).exists():
                    files.add(rel)
    return sorted(files)


def _paths(run: str) -> tuple[Path, Path]:
    runs = Path(os.environ.get("ROTA_RUNS", REPO / ".rota"))
    return runs / f"{run}_warm.db", runs / f"{run}_warm.json"


def write(run: str) -> Path:
    """Stamp the snapshot at `.rota/<run>_warm.db`. Reads the snapshot file
    through its own connection: the walk's connection is the walk's, and
    changing its row factory crashed the next step (night 47, 2026-09-14)."""
    db, stamp = _paths(run)
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        hard = prompt_files(conn) + HARD
    finally:
        conn.close()
    stamp.write_text(json.dumps({
        "rota_head": _head(),
        "hard": {f: _sha(f) for f in hard},
        "soft": {f: _sha(f) for f in SOFT},
        "warm_nights": 0,
    }, indent=1))
    return stamp


def relocate(run: str, root: str) -> int:
    """Point the restored run database at the checkout it runs on. A
    snapshot bakes the project root it was onboarded on; a night on another
    checkout (2026-09-15: the sample repo moved to C:) rewrites that one
    row and is warm. Batches carry worktree paths too, and an onboard-only
    snapshot has none; refuse when it has."""
    db = Path(os.environ.get("ROTA_RUNS", REPO / ".rota")) / f"{run}.db"
    conn = sqlite3.connect(db)
    if conn.execute("SELECT COUNT(*) FROM batches").fetchone()[0]:
        print("COLD: the snapshot holds batches with worktree paths; it cannot move")
        return 1
    old = conn.execute("SELECT value FROM config WHERE key = 'project_root'").fetchone()
    conn.execute("UPDATE config SET value = ? WHERE key = 'project_root'", (str(Path(root)),))
    conn.commit()
    print(f"relocated: project_root {old[0] if old else None!r} -> {str(Path(root))!r}")
    return 0


def check(run: str) -> int:
    """Print one line. Return 0 to start warm, 1 to start cold."""
    db, stamp = _paths(run)
    if not db.exists():
        print("COLD: no warm snapshot")
        return 1
    if not stamp.exists():
        print("COLD: the warm snapshot has no stamp; it predates the check")
        db.unlink()
        return 1
    data = json.loads(stamp.read_text())
    changed = [f for f, h in data["hard"].items() if _sha(f) != h]
    if changed:
        print(f"COLD: onboarding inputs changed since {data['rota_head']}: {', '.join(changed)}")
        db.unlink()
        stamp.unlink()
        return 1
    # The snapshot's routing is the profile it was onboarded on. Night 62
    # (2026-09-14) started warm from a snapshot of another profile and ran
    # the Developer on the wrong model with no error. A named profile that
    # routes differently is a cold start.
    wanted = os.environ.get("GAUNTLET_PROFILE")
    if wanted:
        sys.path.insert(0, str(REPO))
        from rota.llm import profile as profile_mod
        try:
            expected = profile_mod.find(wanted).routing()
        except Exception as exc:
            print(f"COLD: profile {wanted!r} did not load: {exc}")
            return 1
        conn = sqlite3.connect(db)
        row = conn.execute("SELECT value FROM config WHERE key = 'model_routing'").fetchone()
        conn.close()
        have = json.loads(row[0]) if row and row[0] and row[0].startswith('"') else (row[0] if row else None)
        if have != expected:
            print(f"COLD: the snapshot routes {have!r}; profile {wanted!r} routes {expected!r}")
            db.unlink()
            stamp.unlink()
            return 1
    if data.get("warm_nights", 0) >= MAX_WARM:
        print(f"COLD: {data['warm_nights']} warm nights since {data['rota_head']}; onboarding is measured again")
        db.unlink()
        stamp.unlink()
        return 1
    soft = [f for f, h in data["soft"].items() if _sha(f) != h]
    data["warm_nights"] = data.get("warm_nights", 0) + 1
    stamp.write_text(json.dumps(data, indent=1))
    note = f"; changed since the snapshot: {', '.join(soft)}" if soft else ""
    print(f"WARM: snapshot from {data['rota_head']}, warm night {data['warm_nights']} of {MAX_WARM}{note}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "check":
        sys.exit(check(sys.argv[2]))
    if len(sys.argv) == 4 and sys.argv[1] == "relocate":
        sys.exit(relocate(sys.argv[2], sys.argv[3]))
    print(__doc__)
    sys.exit(2)
