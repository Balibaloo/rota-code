import os, subprocess, sys
WT = "C:/Users/roman/rota_review43"
out = subprocess.run(["git", "-C", WT, "diff", "90cd57e..34c3e72", "--unified=0",
                      "--", "rota/roles/prompts"], capture_output=True, text=True).stdout
blocks, cur, cur_file = {}, [], None
for line in out.splitlines():
    if line.startswith("+++ b/"):
        if cur_file and cur:
            blocks[cur_file] = tuple(cur)
        cur_file, cur = line[6:], []
    elif line.startswith("+") and not line.startswith("+++"):
        cur.append(line[1:])
if cur_file and cur:
    blocks[cur_file] = tuple(cur)
md = {k: v for k, v in blocks.items() if k.endswith(".md")}
tl = {k: v for k, v in blocks.items() if k.endswith(".tools")}
print("md files changed:", len(md), " tools files changed:", len(tl))
distinct = set(md.values())
print("distinct added .md blocks:", len(distinct))
for d in distinct:
    print("--- used by %d files" % sum(1 for v in md.values() if v == d))
    for line in d:
        print("   ", line)
print()
print("distinct added .tools lines:", set(tl.values()))
print()
print("files:", sorted(k.split("prompts/")[1] for k in md))
