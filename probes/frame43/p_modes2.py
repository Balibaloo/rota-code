import json, os, sys, glob
WT = "C:/Users/roman/rota_review43"
sys.path.insert(0, WT)
g = json.load(open(WT + "/rota/design/graph.json"))
roles = sorted({e["s"] for e in g["edges"]
                if e.get("t") == "code" and e.get("v") == "probe"})
print("roles granted code.probe in the graph:", roles)

P = WT + "/rota/roles/prompts"
tools = sorted(glob.glob(P + "/**/*.tools", recursive=True))
print("total .tools files:", len(tools))
has_tool, has_line, lines = [], [], {}
for t in tools:
    rel = os.path.relpath(t, P).replace(os.sep, "/")
    names = [n.strip() for n in open(t, encoding="utf-8").read().split() if n.strip()]
    md = t[:-6] + ".md"
    text = open(md, encoding="utf-8").read() if os.path.exists(md) else ""
    brief = [l for l in text.splitlines() if "code.probe" in l]
    if "code.probe" in names:
        has_tool.append(rel)
    if brief:
        has_line.append(rel)
        lines[rel] = tuple(brief)
print()
print("modes whose .tools names code.probe (%d):" % len(has_tool))
for m in has_tool:
    print("   ", m)
print()
print("files whose .md mentions code.probe (%d):" % len(has_line))
only_tool = set(has_tool) - set(has_line)
only_line = set(has_line) - set(has_tool)
print("tool but no brief line:", sorted(only_tool))
print("brief line but no tool:", sorted(only_line))
uniq = set(lines.values())
print("distinct brief line blocks:", len(uniq))
for u in uniq:
    print("   ", [s[:120] for s in u], "used by", sorted(k for k, v in lines.items() if v == u))

# the role the mode belongs to, against the graph grant
print()
for m in has_tool:
    role = m.split("/")[0]
    print("  %-40s role=%-14s granted=%s" % (m, role, role in roles))

# the three held out
print()
for held in ("terminologist/criteria", "terminologist/survey", "architect/survey"):
    t = P + "/" + held + ".tools"
    md = P + "/" + held + ".md"
    names = open(t, encoding="utf-8").read().split() if os.path.exists(t) else ["<no .tools>"]
    text = open(md, encoding="utf-8").read() if os.path.exists(md) else ""
    print("  %-26s probe in tools=%s  probe in md=%s"
          % (held, "code.probe" in names, "code.probe" in text))
