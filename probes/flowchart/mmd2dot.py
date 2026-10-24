"""Translate a Mermaid flowchart with subgraph lanes to Graphviz DOT.

Copied from the frame 314 scratchpad. Run: python mmd2dot.py in.mmd out.dot
"""
import re
import sys

src = open(sys.argv[1], encoding="utf-8").read().splitlines()
# Changed for frame 314 probe 5: the direction comes from the "flowchart XX" line.
direction = next((l.split()[1] for l in src if l.strip().startswith("flowchart")), "LR")
out = ["digraph G {", f"  rankdir={direction}; node [shape=box, fontsize=10]; edge [fontsize=8];",
       "  compound=true; ranksep=0.6; nodesep=0.2;"]
lane = None
nodes = {}
edges = []
sub_re = re.compile(r'^\s*subgraph\s+(\w+)\["([^"]*)"\]')
node_re = re.compile(r'^\s*(\w+)(\(\[|\[\[|\[\(|\(\(|\[|\()"?([^"\]\)]*)"?')
edge_re = re.compile(r'^\s*(\w+)\s*(-->|-\.->|==>)\s*(?:\|"([^"]*)"\|)?\s*(\w+)')
for line in src:
    s = line.strip()
    if not s or s.startswith("%%") or s.startswith("flowchart"):
        continue
    m = sub_re.match(line)
    if m:
        lane = m.group(1)
        out.append(f'  subgraph cluster_{lane} {{ label="{m.group(2)}"; style=filled; fillcolor="#f3f3f3";')
        continue
    if s == "end":
        out.append("  }")
        lane = None
        continue
    m = edge_re.match(line)
    if m:
        a, kind, label, b = m.groups()
        style = "dashed" if kind == "-.->" else "solid"
        lab = f' label="{label}"' if label else ""
        # A dashed arrow is a loop back: it does not set the rank (probe 5).
        rank = ", constraint=false" if kind == "-.->" else ""
        edges.append(f'  {a} -> {b} [style={style}{lab}{rank}];')
        continue
    m = node_re.match(line)
    if m:
        nid, shape, label = m.groups()
        sh = {"([": "ellipse", "[[": "box", "[(": "cylinder", "((": "circle",
              "[": "box", "(": "oval"}[shape]
        label = label.replace("&lt;", "<").replace("&gt;", ">")
        out.append(f'    {nid} [label="{label}", shape={sh}];')
        nodes[nid] = True
        continue
out.extend(edges)
out.append("}")
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(out))
print(len(nodes), "nodes", len(edges), "edges")
