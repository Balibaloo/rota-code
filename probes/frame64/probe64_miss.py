"""
Why does a case that hits on turn 1 miss on a later turn?

Runs one case against a capturing replay, keeps the user text of the turn
that missed, finds the recorded cassette with the same system text whose user
text is nearest, and prints the first difference.
"""
import difflib
import hashlib
import os
import shutil
import sqlite3
import stat
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "D:/repos/rota")
os.environ.setdefault("ROTA_MODEL", "qwen3:8b")

from rota import paths                                        # noqa: E402
from rota.llm.cassettes import ReplayOnlyBackend, key_for     # noqa: E402
from rota.testkit import fixtures                             # noqa: E402
from rota.tools import casestatus                             # noqa: E402

CASE_ID = sys.argv[1]
reg = sqlite3.connect(str(paths.DEV_DB))
reg.row_factory = sqlite3.Row
LOG: list = []


class Capture(ReplayOnlyBackend):
    def complete(self, system, user, pins, tools=None):
        protocol = "native" if tools else "text"
        key = key_for(system, user, pins, protocol)
        hit = reg.execute("SELECT 1 FROM cassettes WHERE key = ?",
                          (key,)).fetchone() is not None
        LOG.append({"turn": len(LOG) + 1, "hit": hit, "system": system,
                    "user": user, "model": pins.model})
        return super().complete(system, user, pins, tools)


def _rm(path: Path) -> None:
    def onerror(fn, p, exc):
        try:
            os.chmod(p, stat.S_IWRITE)
            fn(p)
        except OSError:
            pass
    shutil.rmtree(path, onerror=onerror)


case = next(c for c in casestatus._cases() if c["id"] == CASE_ID)
pins = casestatus.wanted_pins(case, os.environ["ROTA_MODEL"])
tmp = Path(tempfile.mkdtemp(prefix="probe64_"))
try:
    fixtures.run_case(case, tmp / "case.db", Capture(reg), pins=pins,
                      instructions=fixtures.instructions_for(case))
finally:
    _rm(tmp)

print(f"{CASE_ID}: turns {len(LOG)}, hits {[t['hit'] for t in LOG]}")
miss = next((t for t in LOG if not t["hit"]), None)
if miss is None:
    sys.exit(0)
rows = reg.execute(
    "SELECT user FROM cassettes WHERE model = ? AND system = ?",
    (miss["model"], miss["system"])).fetchall()
print(f"turn {miss['turn']} missed; {len(rows)} cassettes share its system text")
best, ratio = None, 0.0
for r in rows:
    q = difflib.SequenceMatcher(None, miss["user"], r["user"], autojunk=False).quick_ratio()
    if q > ratio:
        best, ratio = r["user"], q
if best is None:
    sys.exit(0)
print(f"nearest recorded user text: ratio {ratio:.3f}, "
      f"lengths {len(miss['user'])} vs {len(best)}")
a, b = miss["user"].splitlines(), best.splitlines()
diff = list(difflib.unified_diff(b, a, "recorded", "composed", lineterm="", n=1))
for line in diff[:60]:
    print(line[:200])
