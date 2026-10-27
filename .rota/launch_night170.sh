#!/usr/bin/env bash
# Night 170: sprint 26's night, every row built before it (ruled: Roman, 2026-10-26 23:4x,
# "I want all the fixes in / The walls that arise will be on a new baseline"). Night 1 of 3
# for frames 330, 339, 340, 324 and 335 to 338, and for the rulings seam, from a worktree at
# the gated head. Profile local, qwen3.5:9b in every seat, by Roman's ruling of 2026-10-26.
# The same three click items as night 163 under GAUNTLET_ITEMS=163, rotated as night 169:
# get_app_dir first, clear() second, format_filename last. Cold. The rotation touches the
# gauntlet script and the stand-in principal's brief in the worktree, both checked out first.
set -u
SHA="26a44700"
WT="C:/Users/roman/rota_n170"
MAIN="D:/repos/rota"
export PATH="$MAIN/.venv/Scripts:$PATH"
if [ ! -d "$WT" ]; then
  git -C "$MAIN" worktree add "$WT" "$SHA" || { echo "worktree failed"; exit 3; }
fi
git -C "$WT" checkout -- probes/gauntlet_click.sh probes/principal_brief_163.md
G="$WT/probes/gauntlet_click.sh"
B="$WT/probes/principal_brief_163.md"
python - "$B" <<'EOF'
import sys
p = sys.argv[1]
lines = open(p, encoding="utf-8").read().split("\n")
idx = [i for i, l in enumerate(lines) if l[:3] in ("1. ", "2. ", "3. ")]
a1, a2, a3, f1, f2, f3 = idx[:6]
lines[a1], lines[a2], lines[a3] = "1. " + lines[a2][3:], "2. " + lines[a3][3:], "3. " + lines[a1][3:]
b1, b2, b3 = (lines[i].split(": ", 1)[1] for i in (f1, f2, f3))
lines[f1] = "1. For the first change: " + b2
lines[f2] = "2. For the second change: " + b3
lines[f3] = "3. For the third change: " + b1
open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("brief rotated: 1 get_app_dir, 2 clear, 3 format_filename")
EOF
python - "$G" <<'EOF'
import re, sys
p = sys.argv[1]
t = open(p, encoding="utf-8").read()
def grab(k):
    return re.search(r'^  %s="[^"\n]*"$' % k, t, re.M).group(0)
old = {k: grab(k) for k in ("S1", "F1", "S2", "F2", "S3", "F3")}
for k in old:
    t = t.replace(old[k], "@@%s@@" % k, 1)
def body(k):
    return old[k].split("=", 1)[1]
new = {"S1": body("S2"), "F1": body("F2"), "S2": body("S3"), "F2": body("F3"), "S3": body("S1"), "F3": body("F1")}
for k in new:
    t = t.replace("@@%s@@" % k, "  %s=%s" % (k, new[k]), 1)
open(p, "w", encoding="utf-8", newline="\n").write(t)
print("items rotated: get_app_dir, clear, format_filename")
EOF
export ROTA_REPO="$WT"
export ROTA_RUNS="$MAIN/.rota"
export GAUNTLET_NIGHT=170
export GAUNTLET_AGENT=opus
export GAUNTLET_COLD=1
export GAUNTLET_ITEMS=163
unset CLAUDE_BIN
echo "night 170 launched $(date +%H:%M) from $WT at $SHA, cold, items 163 rotated, profile local, agent principal opus"
bash "$G"
echo "launcher done $(date +%H:%M) exit $?"
