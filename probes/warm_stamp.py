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
import hashlib
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HARD = ["rota/design/graph.json", "rota/core/boot.py", "rota/core/predicates.py",
        "rota/core/scheduler.py", "rota/core/schema.sql", "rota/core/db.py"]
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
    return REPO / ".rota" / f"{run}_warm.db", REPO / ".rota" / f"{run}_warm.json"


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
    if len(sys.argv) != 3 or sys.argv[1] != "check":
        print(__doc__)
        sys.exit(2)
    sys.exit(check(sys.argv[2]))
