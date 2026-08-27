// Runs inside the viewer's own context, beside the real graphview.js.
//
// Kept in its own file rather than as a string in the harness: nesting a
// template literal inside a template literal meant every backtick, backslash
// and dollar sign in here had to be escaped for a language it was not written
// in, and two of them silently were not.
//
// `DATA` and the viewer's globals are provided by lens_check.js.

GV.trace = DATA.trace;
GV.graph = DATA.graph;
GV.stories = DATA.stories;
GV.layout = DATA.layout;

const problems = [];

function report(name) {
  const lit = gvLit();
  const by = {};
  for (const e of GV.graph.edges) {
    const st = lit.get(ek([e.s, e.t, e.type]));
    if (st) by[st] = (by[st] || 0) + 1;
  }
  const shown = Object.values(by).reduce((a, b) => a + b, 0);
  console.log('  ' + name.padEnd(26) + String(shown).padStart(3) + '/'
              + GV.graph.edges.length + '  ' + JSON.stringify(by));
  return shown;
}

// ---- what each lens lights -------------------------------------------------

console.log('edges lit, per lens:');

GV.source = 'coverage';
if (report('coverage') === 0 && GV.trace.coverage.covered.length)
  problems.push('coverage lights nothing');

// A story's first step is a title card and lights nothing, which is correct.
// Walk to a step that has edges before judging the lens.
GV.source = 'story';
const steps = (GV.stories[0] || {}).steps || [];
GV.stepIx = Math.max(0, steps.findIndex(s => (s.edges || []).length));
if (report('story @ step ' + GV.stepIx) === 0 && steps.some(s => s.edges.length))
  problems.push('story lights nothing');

// An empty run is an empty database, not a broken lens. And a run recorded
// before a vocabulary change produces keys that match nothing in today's
// graph — the lens is fine, the data is from another era; only a lens that
// produces NO keys from real steps is broken.
GV.source = 'run';
const runLit = report('run');
if (!(GV.trace.steps || []).length) console.log('    (no sessions recorded)');
else if (runLit === 0) {
  if (gvLit().size > 0)
    console.log('    (steps recorded against an older vocabulary — '
                + 'no key matches today\'s graph)');
  else problems.push('run lights nothing');
}

GV.source = 'design';
if (report('design') !== 0) problems.push('design lights something and should not');

const withReads = DATA.cases.find(c => c.edges.reading.length) || DATA.cases[0];
GV.source = 'case';
GV.caseEdges = withReads.edges;
GV.caseSituation = withReads.situation;
if (report('case ' + withReads.id.slice(0, 20)) === 0)
  problems.push('case lights nothing');

// ---- what each key row selects ---------------------------------------------
//
// Hovering a row that resolves to nothing dims the whole picture and looks
// exactly like a broken lens. It did, for the five case rows, and then again
// for the two coverage rows, because the resolver only understood kind and
// edge selectors and silently returned nothing for the rest.

const rows = [];
for (const [group, items] of LEGEND)
  for (const r of items) rows.push(['design', group, r]);
for (const src of ['coverage', 'story', 'run']) {
  const g = LENS_KEY_FOR(src);
  if (g) for (const r of g[1]) rows.push([src, g[0], r]);
}
for (const r of CASE_LEGEND[1]) rows.push(['case', CASE_LEGEND[0], r]);

// The failure worth catching is a selector the resolver does not *understand*
// -- it returns null for both nodes and edges, matches nothing, and dims the
// picture. A row that resolves correctly to an empty set is data: "mid-session"
// selects nothing when no role holds a claim, and that is the honest answer.
const unknown = [], empty = [];
for (const [src, group, row] of rows) {
  GV.source = src;
  const sel = keySelects(row[1]);
  if (sel.nodes === null && sel.edges === null) {
    unknown.push(group + ' / ' + row[0] + '  ' + JSON.stringify(row[1]));
    continue;
  }
  const n = (sel.nodes ? sel.nodes.size : 0)
          + (sel.edges ? GV.graph.edges.filter(sel.edges).length : 0);
  if (!n) empty.push(group + ' / ' + row[0]);
}

console.log('');
if (unknown.length) {
  console.log('KEY ROWS THE RESOLVER DOES NOT UNDERSTAND:');
  unknown.forEach(d => console.log('  ' + d));
  problems.push.apply(problems, unknown);
} else {
  console.log(rows.length + ' key rows, all understood');
}
if (empty.length) {
  console.log('  (empty right now, which is data not a fault: '
              + empty.join(', ') + ')');
}

// ---- collapsing parallel edges ---------------------------------------------
//
// Folding is per source, target *and type*. Seventeen pairs here carry more
// than one type -- liaison to brief is both a read and a write -- and one line
// standing for two kinds of relationship is the single thing the colour system
// must never say. This asserts no fold group ever mixes them.

const groups = {};
for (const e of GV.graph.edges) {
  const gk = e.s + '|' + e.t + '|' + e.type;
  (groups[gk] = groups[gk] || []).push(e);
}
const all = Object.values(groups);
const folds = all.filter(g => g.length > 1);
const mixed = all.filter(g => new Set(g.map(e => e.type)).size > 1);

console.log('');
console.log('collapsing: ' + GV.graph.edges.length + ' edges -> ' + all.length
            + ' lines (' + folds.length + ' groups fold, biggest '
            + Math.max.apply(null, all.map(g => g.length)) + ')');
if (mixed.length) {
  console.log('  FOLD GROUPS MIXING EDGE TYPES: ' + mixed.length);
  problems.push('fold groups mix types');
}

// ---- the fold threshold ----------------------------------------------------
//
// The zoom that triggers folding is a setting now, so exercise the real
// predicate rather than trust that the slider is wired to anything. A slider
// bound to a misspelled key looks perfectly fine on screen: it slides.

const kWas = GV.view.k, setWas = Object.assign({}, GV.settings);
GV.settings.collapse = 'auto';
const at = (threshold, k) => {
  GV.settings.far = threshold; GV.view.k = k; return collapsing();
};
const honoured = at(0.60, 0.40) && !at(0.60, 0.80)     // default-ish
              && at(1.20, 0.80) && !at(0.30, 0.40)     // moving it moves the fold
              && (GV.settings.collapse = 'never', !at(0.6, 0.1));  // and 'never' still wins
GV.view.k = kWas; Object.assign(GV.settings, setWas);

console.log('fold threshold: ' + (honoured ? 'follows the setting' : 'IGNORED'));
if (!honoured) problems.push('fold threshold not honoured');

// ---- off-screen destination chips ------------------------------------------
//
// A chip placed by a sign error points confidently at the wrong side of the
// screen, which is worse than no chip at all, and it is not something reading
// the code proves. Eight directions from the middle of an 800x600 canvas, and
// each one has to leave through the side it is heading for.

const W = 800, H = 600, m = 34, mid = {x: 400, y: 300};
const compass = [
  ['east',       {x: 5000, y: 300},   p => Math.abs(p.x - (W - m)) < .01],
  ['west',       {x: -5000, y: 300},  p => Math.abs(p.x - m) < .01],
  ['south',      {x: 400, y: 5000},   p => Math.abs(p.y - (H - m)) < .01],
  ['north',      {x: 400, y: -5000},  p => Math.abs(p.y - m) < .01],
  ['south-east', {x: 5000, y: 5000},  p => p.x > mid.x && p.y > mid.y],
  ['north-west', {x: -5000, y: -5000},p => p.x < mid.x && p.y < mid.y],
];

let wrongWay = [];
for (const [name, to, ok] of compass) {
  const at = ghostAnchor(mid, to, W, H, m);
  if (!at || !ok(at) || at.x < 0 || at.x > W || at.y < 0 || at.y > H)
    wrongWay.push(name + (at ? ` -> ${at.x.toFixed(0)},${at.y.toFixed(0)}` : ' -> null'));
}

// A destination already on screen must not get a chip: the ray never reaches
// the border inside one step.
if (ghostAnchor(mid, {x: 450, y: 320}, W, H, m) !== null)
  wrongWay.push('an on-screen node was given a chip');

console.log('\noff-screen chips: ' + (wrongWay.length
  ? 'WRONG SIDE: ' + wrongWay.join(', ')
  : compass.length + ' directions all exit through the right side'));
if (wrongWay.length) problems.push('ghost chips point the wrong way');

// Chips cluster where their edges exit, and edges do not leave a node evenly:
// four artefacts stacked in a column all leave through the same short stretch
// of border. Six landing within twelve pixels of each other is the real case.
const packed = [{y: 300}, {y: 304}, {y: 306}, {y: 309}, {y: 311}, {y: 312}];
ghostSpread(packed, 20, H - 20, 30, 'y');
let tooClose = 0, offCanvas = 0;
for (let i = 0; i < packed.length; i++) {
  if (i && packed[i].y - packed[i - 1].y < 29.99) tooClose++;
  if (packed[i].y < 20 || packed[i].y > H - 20) offCanvas++;
}
console.log('  separation: 6 chips within 12px -> gaps '
  + packed.map(c => c.y.toFixed(0)).join(', ')
  + (tooClose || offCanvas ? '  OVERLAPPING' : '  all clear'));
if (tooClose || offCanvas) problems.push('ghost chips still overlap');

// A side with more chips than it has room for. Forty at thirty pixels needs
// twice the canvas, so they *will* overlap -- the property being asserted is
// which way it fails. An overlapping chip is still half-readable and still
// clickable; one pushed past the border is neither.
const crowded = Array.from({length: 40}, (_, i) => ({y: 300 + i}));
ghostSpread(crowded, 20, H - 20, 30, 'y');
const spill = crowded.filter(c => c.y < 19.99 || c.y > H - 19.99).length;
console.log('  overflow: 40 chips where 19 fit -> ' + spill
            + ' pushed off the canvas (they crowd instead)');
if (spill) problems.push('ghost chips overflow the canvas');

// ---- the arcs -----------------------------------------------------------
//
// Parallel edges are separated by bowing each one further out, so the property
// that matters is that no two edges between a pair get the same offset -- that
// was the bug the whole spread pass exists to prevent, and it looks exactly
// like a single relationship where there are three.

computeSpread();
let sameSlot = 0, parallelPairs = 0;
const byPair = {};
for (const e of GV.graph.edges) {
  if (e.type === 'refs') continue;
  const k = e.s + '|' + e.t;
  (byPair[k] = byPair[k] || []).push(
    GV.spread[e.s + '|' + e.t + '|' + e.type + '|' + e.v]);
}
for (const ranks of Object.values(byPair)) {
  if (ranks.length < 2) continue;
  parallelPairs++;
  if (new Set(ranks).size < ranks.length) sameSlot++;
}
console.log('\narcs: ' + parallelPairs + ' pairs carry parallel edges, '
            + sameSlot + ' with two on the same offset');
if (sameSlot) problems.push('parallel edges share an offset');

// ---- off-screen edges are replaced, not added to ----------------------------
//
// The point of the stand-ins: an edge whose far end has left the canvas is not
// drawn at all. A line heading off the screen says a relationship exists and
// then abandons you halfway, and at the zoom where that starts happening there
// are a dozen of them fanning out to nowhere.
//
// Needs a viewport, so the probe supplies one: a small window, zoomed in on a
// node with neighbours in every direction.

const vp = {clientWidth: 500, clientHeight: 360, innerHTML: '',
            getBoundingClientRect: () => ({left: 0, top: 0, width: 500, height: 360})};
const realGet = document.getElementById;
document.getElementById = (id) => id === 'gsvg' ? vp : null;

GV.mode = 'team';
GV.source = 'design';
GV.focus = 'vision_keeper';
GV.view = {k: 1.4, x: 250 - GV.layout.vision_keeper.x * 1.4,
                   y: 180 - GV.layout.vision_keeper.y * 1.4};

const gone = offscreenNeighbours();
const incident = GV.graph.edges.filter(
  e => e.s === 'vision_keeper' || e.t === 'vision_keeper');
const suppressed = incident.filter(e => gone.has(e.s) || gone.has(e.t));
const drawn = drawTeam().edges;
const chips = ghostChips();
const chipCount = (chips.match(/class="ghost"/g) || []).length;
const localLines = (chips.match(/<path/g) || []).length;

// Nothing incident to a vanished neighbour may appear in the canvas edges.
let leaked = 0;
for (const e of suppressed)
  if (drawn.includes('data-e="' + e.s + '|' + e.t + '|' + e.type)) leaked++;

console.log('');
console.log('off-screen substitution, zoomed on vision_keeper at 1.4x in 500x360:');
console.log('  ' + gone.size + ' neighbours off canvas, ' + suppressed.length
            + ' of its ' + incident.length + ' edges suppressed');
console.log('  ' + chipCount + ' stand-ins drawn, carrying ' + localLines
            + ' local edges');
if (leaked) { console.log('  ' + leaked + ' SUPPRESSED EDGES STILL DRAWN');
              problems.push('off-screen edges still drawn'); }
else if (gone.size && !chipCount) {
  console.log('  NEIGHBOURS VANISHED WITH NOTHING PUT IN THEIR PLACE');
  problems.push('off-screen neighbours have no stand-in');
} else if (gone.size) {
  console.log('  nothing runs off the canvas; every lost end has a stand-in');
}
document.getElementById = realGet;
GV.focus = null;

// ---- the cable and the straight solo ----------------------------------------
//
// A pair carrying both a read and a write rides as one cable: exactly two
// strands, one per kind, at every zoom — including collapse:never, which is
// the setting that used to fan every verb out. And a pair carrying exactly
// one line draws it straight: no Q command in its path.

{
  const both = {};
  for (const e of GV.graph.edges)
    if (e.type === 'reads' || e.type === 'writes')
      (both[e.s + '|' + e.t] ||= new Set()).add(e.type);
  // Only pairs the probe's raw layout can place — the page itself parks
  // unplaced nodes via placeStrays, but DATA.layout here is the bare file.
  const cablePairs = Object.keys(both).filter(k => both[k].size === 2
    && k.split('|').every(id => GV.layout[id]));

  const kWas2 = GV.view.k, setWas2 = Object.assign({}, GV.settings);
  GV.mode = 'team'; GV.source = 'design'; GV.focus = null;
  GV.settings.collapse = 'never'; GV.view = {k: 1, x: 0, y: 0};
  const drawnE = drawTeam().edges;
  GV.view.k = kWas2; Object.assign(GV.settings, setWas2);

  const broken = [];
  for (const pair of cablePairs) {
    const [s, t] = pair.split('|');
    const re = new RegExp('data-e="' + s + '\\|' + t + '\\|', 'g');
    const strands = (drawnE.match(re) || []).length;
    if (strands !== 2) broken.push(pair + ' -> ' + strands + ' strands');
  }
  console.log('\ncable: ' + cablePairs.length
    + ' read+write pairs, two strands each even at collapse:never'
    + (broken.length ? '  BROKEN: ' + broken.join(', ') : ''));
  if (broken.length) problems.push('cable pairs not unified');

  // Solo pairs: one line, straight. Find a pair with load 1 and assert its
  // drawn path is M...L..., not a quadratic.
  const load = {};
  for (const e of GV.graph.edges) {
    if (e.type === 'refs') continue;
    const k = [e.s, e.t].sort().join('|');
    load[k] = (load[k] || 0) + 1;
  }
  let soloChecked = 0, soloCurved = 0;
  for (const e of GV.graph.edges) {
    if (e.type === 'refs') continue;
    if (load[[e.s, e.t].sort().join('|')] !== 1) continue;
    const m = drawnE.match(new RegExp(
      '<path d="(M[^"]+)"[^>]*data-e="' + e.s + '\\|' + e.t + '\\|' + e.type));
    if (!m) continue;
    soloChecked++;
    if (m[1].includes('Q')) soloCurved++;
  }
  console.log('solo lines: ' + soloChecked + ' checked, '
    + (soloCurved ? soloCurved + ' STILL CURVED' : 'all straight'));
  if (soloCurved) problems.push('solo pairs still bow');
}

// ---- the layout generators ---------------------------------------------------
//
// Every generator must place every node, at finite coordinates, with no two
// nodes stacked on one spot — a generated layout that omits a node makes the
// node vanish from the canvas, which is the picture claiming it does not
// exist. And `placeStrays` is the guard for the same failure in *saved*
// layouts, so it is exercised on a layout with a hole cut in it.

for (const [name, fn] of Object.entries(AUTO_LAYOUTS)) {
  const pos = fn();
  const ids = Object.keys(pos);
  const missing = GV.graph.nodes.filter(n => !pos[n.id]);
  const bad = ids.filter(id => !isFinite(pos[id].x) || !isFinite(pos[id].y));
  let stacked = 0;
  for (let i = 0; i < ids.length; i++)
    for (let j = i + 1; j < ids.length; j++) {
      const d = Math.hypot(pos[ids[i]].x - pos[ids[j]].x,
                           pos[ids[i]].y - pos[ids[j]].y);
      if (d < 24) stacked++;
    }
  console.log('layout ' + name.padEnd(14) + ' places ' + ids.length + '/'
              + GV.graph.nodes.length + ' nodes'
              + (stacked ? '  ' + stacked + ' STACKED PAIRS' : ''));
  if (missing.length)
    problems.push(name + ' omits ' + missing.map(n => n.id).join(', '));
  if (bad.length) problems.push(name + ' places nodes at non-finite coordinates');
  if (stacked) problems.push(name + ' stacks nodes on one spot');
}

const dropped = GV.graph.nodes[GV.graph.nodes.length - 1].id;
const holed = {};
for (const [id, p] of Object.entries(GV.layout))
  if (id !== dropped) holed[id] = p;
const healed = placeStrays(holed);
if (!healed[dropped])
  problems.push('placeStrays leaves a node the layout omits invisible');
else console.log('placeStrays: a node the layout omits is parked, not vanished');

// ---- the entry points still exist -------------------------------------------
//
// Twice in one session a function was deleted by accident, carried out inside a
// block that was being removed for other reasons. `node --check` passes -- the
// file is valid JavaScript with a hole in it -- and every headless check here
// passed too, because they call the drawing functions directly and never the
// ones the *page* calls. The canvas went white and the reason was a
// ReferenceError no test was positioned to see.
//
// The second time, the check that was supposed to catch it grepped for
// `^-function` and missed `async function gvLoad`.

const ENTRY = ['gvLoad', 'gvDraw', 'gvControls', 'gvFit', 'gvFocus', 'gvGoto',
               'gvInhabit', 'gvMode', 'gvSet', 'gvFar', 'gvLegend', 'gvNarrate',
               'gvDrawInner', 'offscreenNeighbours',
               'drawTeam', 'drawChat', 'refPath', 'computeSpread', 'foldPlan',
               'keySelects', 'gvLit', 'gvSteps', 'gvVisible', 'ghostChips',
               'setLens', 'gvWireStage', 'applyLayout', 'saveLayout',
               'saveLayoutAs', 'deleteLayout', 'placeStrays',
               'autoFlow', 'autoGrid', 'autoForce',
               'dd', 'ddToggle', 'ddCloseAll', 'ddWire'];

const missing = ENTRY.filter(name => {
  try { return typeof eval(name) !== 'function'; }
  catch (err) { return true; }          // ReferenceError: it is not there at all
});
console.log('\nentry points: ' + (missing.length
  ? 'MISSING ' + missing.join(', ')
  : ENTRY.length + ' defined'));
if (missing.length) problems.push('entry points missing: ' + missing.join(', '));

if (problems.length) console.log('\nPROBLEMS: ' + problems.length);
else console.log('every lens and every key row is live');

problems.length;
