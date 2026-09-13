"""
Every session of a run, in order, as the role saw it.

    python probes/wake_dump.py <run> [out_dir]

One markdown file per session: the wake, what was pushed, every turn's
reply with the calls it made, and every refusal the next turn carried. This
is the reader for the wake audit (2026-09-13): a person reads each session
against the rows the database held at that moment and says what the role
should have been shown and was not.
"""
import re
import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
run = sys.argv[1]
out = Path(sys.argv[2]) if len(sys.argv) > 2 else REPO / ".rota" / f"wakes_{run}"
out.mkdir(parents=True, exist_ok=True)
conn = sqlite3.connect(REPO / ".rota" / f"{run}.db")
conn.row_factory = sqlite3.Row

index = []
for s in conn.execute("SELECT * FROM sessions ORDER BY seq"):
    turns = conn.execute("SELECT seq, user, completion, ms FROM turns WHERE session_id = ? ORDER BY seq",
                         (s["id"],)).fetchall()
    lines = [f"# {s['id']} {s['role']} {s['wake_kind']} {s['wake_detail'] or ''} "
             f"refs={s['wake_refs']} trigger={s['trigger_msg']} model={s['model']} "
             f"committed={s['committed']}", ""]
    for t in turns:
        if t["seq"] == 1:
            lines += ["## the wake, as pushed", "", "```", t["user"], "```", ""]
        else:
            errs = [l for l in (t["user"] or "").splitlines() if l.startswith("ERROR")]
            oks = [l[:160] for l in (t["user"] or "").splitlines() if l.startswith("OK ")]
            lines += [f"## feedback before turn {t['seq']}", ""]
            lines += [f"- {e}" for e in errs] + [f"- {o}" for o in oks] + [""]
        calls = re.findall(r"TOOL: ([a-z_.]+\(.{0,200})", t["completion"] or "")
        lines += [f"## turn {t['seq']} reply ({t['ms']} ms)", ""]
        lines += [f"- call: {c}" for c in calls] or ["- (no call)"]
        say = re.sub(r"TOOL: [^\n]*", "", t["completion"] or "").strip()
        if say:
            lines += ["", "```", say[:1500], "```"]
        lines.append("")
    path = out / f"{s['seq']:03d}_{s['role']}_{s['wake_kind'].replace(':', '_')}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    index.append(f"{s['seq']:03d} {s['role']:14} {s['wake_kind']:24} {s['wake_detail'] or '':30} turns={len(turns)} committed={s['committed']}")
(out / "INDEX.md").write_text("\n".join(index) + "\n", encoding="utf-8")
print(f"{len(index)} sessions -> {out}")
