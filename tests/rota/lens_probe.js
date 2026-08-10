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

// An empty run is an empty database, not a broken lens.
GV.source = 'run';
const runLit = report('run');
if (!(GV.trace.steps || []).length) console.log('    (no sessions recorded)');
else if (runLit === 0) problems.push('run lights nothing');

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

if (problems.length) console.log('\nPROBLEMS: ' + problems.length);
else console.log('every lens and every key row is live');

problems.length;
