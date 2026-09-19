import json, os, sys, glob, sqlite3
WT = "C:/Users/roman/rota_review43"
sys.path.insert(0, WT)
g = json.load(open(WT + "/rota/design/graph.json"))
# every role that is granted code.probe
granted = set()
for e in g.get("edges", g if isinstance(g, list) else []):
    pass
print("graph top keys:", list(g)[:8])
