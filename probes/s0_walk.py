"""
S0 walk: the greeter story end to end on a live model.

    python s0_walk.py 8 > s0_walk8.log 2>&1

Temp repo with one README -> boot.onboard (empty program closes the phases)
-> the principal's request injected as a converse -> loop.step on qwen3:8b
with a scripted Yes-principal approving every confirm/present -> stop at the
first merge, a quiet frontier, or the step cap. Prints the world's counts,
the test-run results, the batches and the worktree's Python at the end.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Runnable from anywhere: the repo root is one up from probes/.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
FLAGS = {a for a in sys.argv[1:] if a.startswith("--")}
CAP = int(ARGS[1]) if len(ARGS) > 1 else 140
MODEL = ARGS[2] if len(ARGS) > 2 else "qwen3:8b"

# The onboarding stretch is ~60 steps and reproduces step for step within
# a model load; the delivery stretch is what the walks measure. `--snap`
# saves the world at the first slicing tick (delivery about to start);
# `--restore` starts the next walk from it, at the same absolute path so
# every path the database holds still resolves. Onboarding code changes
# invalidate the snapshot -- delete it and walk cold.
SNAP = Path(tempfile.gettempdir()) / "rota_s0_snapshot"

from rota.core.db import init_db          # noqa: E402
from rota.onboarding import boot          # noqa: E402
from rota.core.loop import step           # noqa: E402
from rota.roles.principal import pump, Answer   # noqa: E402
from rota.llm.llm import Pins             # noqa: E402

def _rmtree(path):
    """Git objects are read-only on Windows; clear the bit and retry."""
    import os
    import stat

    def _onerror(fn, p, _exc):
        os.chmod(p, stat.S_IWRITE)
        fn(p)
    shutil.rmtree(path, onerror=_onerror)



if "--restore" in FLAGS and (SNAP / "root.txt").exists():
    base = Path((SNAP / "root.txt").read_text(encoding="utf-8").strip())
    if base.exists():
        _rmtree(base)
    shutil.copytree(SNAP / "tree", base)
    root = base / "proj"
    db = init_db(base / "rota.db")
    print(f"restored snapshot into {base}", flush=True)
else:
    root = Path(tempfile.mkdtemp(prefix="rota_s0g_")) / "proj"
    root.mkdir(parents=True)
    (root / "README.md").write_text("# greeter\n", encoding="utf-8")
    for cmd in (["git", "init", "-q"], ["git", "add", "-A"],
                ["git", "-c", "user.email=t@t", "-c", "user.name=t",
                 "commit", "-qm", "init"]):
        subprocess.run(cmd, cwd=root, check=True, capture_output=True)
    db = init_db(root.parent / "rota.db")
    boot.onboard(db, root)
    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
               "('e_m1','principal',1,?)",
               ('Hello, Please build a python script that asks for the users '
                'name, and then shows "Hellow User!"',))
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES ('m1','t1','principal','liaison',"
               "'converse','[\"e_m1\"]',1)")
    db.commit()


def _snapshot():
    db.execute("PRAGMA wal_checkpoint(FULL)")
    if SNAP.exists():
        _rmtree(SNAP)
    shutil.copytree(root.parent, SNAP / "tree")
    (SNAP / "root.txt").write_text(str(root.parent), encoding="utf-8")
    print(f"snapshot saved from {root.parent}", flush=True)


class Yes:
    """Approves everything, and answers a clarification the way a patient
    principal would on walk twelve -- where the tests asserted that greet()
    returns the greeting and the Developer made it print, and the dispute
    climbed honestly to the seat. One canned answer, topic-agnostic on
    purpose: it names a convention, not a fact about the program."""
    name = "scripted-yes"

    def respond(self, ask):
        if ask.verb in ("confirm", "present"):
            return Answer(verb="verdict",
                          per_item={r: "approve" for r in ask.refs})
        if ask.verb == "clarify":
            # Non-directive on purpose: walk twenty-one segmented a
            # convention-shaped reply into three new criteria.
            return Answer(verb="converse", text=(
                "Either reading is fine by me -- go with whichever you "
                "already have. Nothing new to add."))
        return None


pins = Pins(model=MODEL, temperature=0.0)
seat = Yes()
print("db:", root.parent / "rota.db", flush=True)
for i in range(CAP):
    s = step(db, pins=pins)
    if s is None or s.wake is None:
        print(f"step {i}: quiet", flush=True)
        break
    o = s.outcome
    print(f"step {i:2}: {s.wake.role or '(sched)':13} {s.wake.kind:20} "
          f"ok={bool(o and o.committed)} e={len(o.errors) if o else '-'} "
          f"{(s.note or '')[:44]}", flush=True)
    pump(db, seat)
    if "--snap" in FLAGS and s.wake.kind == "tick:slicing":
        _snapshot()
    b = db.execute("SELECT id FROM batches WHERE status='merged'").fetchone()
    if b:
        print(f"*** MERGED: {b['id']} ***", flush=True)
        break

print("world:", {t: db.execute(f"SELECT COUNT(*) n FROM {t}").fetchone()["n"]
                 for t in ("statements", "items", "tickets", "criteria",
                           "tests")})
for r in db.execute("SELECT result, COUNT(*) n FROM test_runs GROUP BY result"):
    print("runs:", dict(r))
for row in db.execute("SELECT id, status FROM batches"):
    print("batch:", dict(row))
for row in db.execute("SELECT tick_key, attempts, quarantined FROM tick_attempts "
                      "WHERE quarantined = 1"):
    print("quarantined:", dict(row))
for row in db.execute("SELECT id, from_role, to_role, verb, status FROM messages "
                      "WHERE verb = 'question' ORDER BY seq"):
    print("question:", dict(row))
b = db.execute("SELECT worktree FROM batches WHERE worktree IS NOT NULL").fetchone()
if b:
    wt = Path(b["worktree"])
    if wt.is_dir():
        for f in sorted(wt.glob("*.py")) + sorted((wt / "tests").glob("*.py")):
            print("---", f.relative_to(wt), "---")
            print(f.read_text(encoding="utf-8")[:400], flush=True)
print("db:", root.parent / "rota.db")
