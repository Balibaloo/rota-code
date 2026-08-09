/*
 * Extract the design graph from team-graph.html into JSON.
 *
 * The HTML authored NODES / EDGES / STORIES as JS object literals. Those are the
 * single source of truth for the system's wiring, so they must be machine
 * readable by the Python side (sandbox loader, contact derivation, lints) and by
 * the viewer alike. This slices the three declarations out of the <script> block
 * and evaluates them in isolation — no regex parsing of object literals.
 *
 * Output (written next to this script's --out target):
 *   graph.json    nodes (semantics only) + edges          <- the wiring
 *   layout.json   node id -> {x, y}                       <- viewer only
 *   stories.json  the three narrated traversals           <- arc test source
 *
 * Usage: node extract_graph.js <team-graph.html> <out-dir>
 */
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const [, , htmlPath, outDir] = process.argv;
if (!htmlPath || !outDir) {
  console.error("usage: node extract_graph.js <team-graph.html> <out-dir>");
  process.exit(2);
}

const html = fs.readFileSync(htmlPath, "utf8");

/** Slice from `startMarker` up to and including the matching terminator line. */
function slice(source, startMarker, endMarker) {
  const start = source.indexOf(startMarker);
  if (start === -1) throw new Error(`marker not found: ${startMarker}`);
  const end = source.indexOf(endMarker, start);
  if (end === -1) throw new Error(`terminator not found for: ${startMarker}`);
  return source.slice(start, end + endMarker.length);
}

const nodesSrc = slice(html, "const NODES = [", "\n];");
const edgesSrc = slice(html, "const EDGES = [", "\n];");

// STORIES is `const STORIES = [];` followed by N push() calls, ending before the
// viewer's runtime state. Take everything up to the first `let si`.
const storiesStart = html.indexOf("const STORIES = [];");
const storiesEnd = html.indexOf("let si", storiesStart);
if (storiesStart === -1 || storiesEnd === -1) throw new Error("STORIES block not found");
const storiesSrc = html.slice(storiesStart, storiesEnd);

const sandbox = {};
vm.createContext(sandbox);
// `const` is lexical and does not land on the context object, so export explicitly.
vm.runInContext(
  `${nodesSrc}\n${edgesSrc}\n${storiesSrc}\n;globalThis.__out = { NODES, EDGES, STORIES };`,
  sandbox
);

const { NODES, EDGES, STORIES } = sandbox.__out;
if (!Array.isArray(NODES) || !Array.isArray(EDGES) || !Array.isArray(STORIES)) {
  throw new Error("extraction produced non-arrays");
}

// Split layout (x/y) away from semantics: editing what the graph *means* must
// never touch geometry, and the lints must never see coordinates.
const layout = {};
const nodes = NODES.map((n) => {
  const { x, y, ...rest } = n;
  layout[n.id] = { x, y };
  return rest;
});

fs.mkdirSync(outDir, { recursive: true });
const write = (name, data) =>
  fs.writeFileSync(path.join(outDir, name), JSON.stringify(data, null, 2) + "\n", "utf8");

write("graph.json", { nodes, edges: EDGES });
write("layout.json", layout);
write("stories.json", STORIES);

console.log(
  `nodes=${nodes.length} edges=${EDGES.length} stories=${STORIES.length} ` +
    `steps=${STORIES.reduce((a, s) => a + s.steps.length, 0)}`
);
