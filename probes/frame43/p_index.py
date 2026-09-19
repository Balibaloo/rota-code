import os, sqlite3, sys, subprocess
WT = "C:/Users/roman/rota_review43"
SCRATCH = "C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4286e076-bf12-4642-ad8b-d2bc9c82a7db/scratchpad"
sys.path.insert(0, WT)
from rota.core import db as dbm, runner as R
from rota.onboarding import indexer
from rota.roles import api

# --- 1. the migration, on a database created before the change -------------
old_schema = subprocess.run(["git", "-C", WT, "show", "90cd57e:rota/core/schema.sql"],
                            capture_output=True, text=True).stdout
p = SCRATCH + "/old.db"
if os.path.exists(p):
    os.remove(p)
c = sqlite3.connect(p)
c.executescript(old_schema)
c.execute("INSERT INTO config (key, value) VALUES ('schema', 'ledger-kind')")
c.execute("INSERT INTO code_index (grain, grain_kind, fan_in, sym_kind) "
          "VALUES ('a/b.py::f', 'symbol', 0, 'function')")
c.commit()
cols_before = [r[1] for r in c.execute("pragma table_info(code_index)")]
c.close()
print("old db columns:", "line_start" in cols_before, "line_end" in cols_before)
conn = dbm.init_db(p)
cols_after = [r[1] for r in conn.execute("pragma table_info(code_index)")]
print("after init_db:", "line_start" in cols_after, "line_end" in cols_after)
print("pre-existing row spans:",
      dict(conn.execute("SELECT line_start, line_end FROM code_index "
                        "WHERE grain='a/b.py::f'").fetchone()))

# --- 2. build a real index over this worktree and round-trip a span ---------
rep = indexer.build(conn, WT)
conn.commit()
print("index built: symbols=%d" % rep.symbols)
zero = conn.execute("SELECT COUNT(*) AS n FROM code_index WHERE grain_kind='symbol' "
                    "AND line_start=0 AND line_end=0").fetchone()["n"]
tot = conn.execute("SELECT COUNT(*) AS n FROM code_index WHERE grain_kind='symbol'").fetchone()["n"]
print("symbol grains with no span: %d of %d" % (zero, tot))

row = conn.execute("SELECT grain, line_start, line_end FROM code_index "
                   "WHERE grain LIKE '%::_cap_exchange'").fetchone()
print("probe row:", dict(row))
path, name = row["grain"].split("::")
lines = open(os.path.join(WT, path), encoding="utf-8").read().splitlines()
body = lines[row["line_start"]:row["line_end"]]
print("  code.source(path=%r, start=%d, end=%d) first line: %r"
      % (path, row["line_start"], row["line_end"], body[0]))
print("  last line: %r" % body[-1])
print("  line after: %r" % lines[row["line_end"]])

# --- 3. what a 60-row probe renders to -------------------------------------
def probe_rows(conn, pattern):
    hits = [dict(r) for r in conn.execute(
        "SELECT grain, grain_kind, area, fan_in, line_start, line_end "
        "FROM code_index WHERE grain LIKE ? "
        "ORDER BY CASE grain_kind WHEN 'symbol' THEN 0 ELSE 1 END, "
        "fan_in DESC, grain LIMIT ?", ("%" + pattern + "%", api.PROBE_ROWS))]
    total = conn.execute("SELECT COUNT(*) AS n FROM code_index WHERE grain LIKE ?",
                         ("%" + pattern + "%",)).fetchone()[0]
    if hits and total > len(hits):
        hits.insert(0, {"grain": "%d grains match '%s' and the %d with the most "
                                 "fan-in are below. The pattern is too broad. "
                                 "Probe a longer name to reach the rest."
                                 % (total, pattern, len(hits)),
                        "grain_kind": "", "area": "", "fan_in": "",
                        "line_start": "", "line_end": ""})
    return hits, total

print()
for pat in ("test", "run", "code", "_fit", "cap_exchange", "e"):
    hits, total = probe_rows(conn, pat)
    shown = R._render(hits, R.RESULT_CHARS)
    tbl = R._as_table(hits)
    print("pattern=%-14s total=%5d rows=%3d table=%s chars=%6d truncated=%s"
          % (pat, total, len(hits), tbl is not None, len(shown),
             "TRUNCATED" in shown))
    syms = sum(1 for h in hits if h["grain_kind"] == "symbol")
    print("     symbol rows shown: %d   note row: %s" % (syms, hits[0]["grain_kind"] == ""))
conn.close()
