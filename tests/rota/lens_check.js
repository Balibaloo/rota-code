// What each lens would actually light, without a browser.
//
// The coverage lens looked broken twice for two unrelated reasons -- once
// because covered edges carried no positive mark, once because the mark was
// five pixels at 22% opacity on a near-white canvas -- and both times the
// logic underneath was correct. Reading the code proved nothing either time.
// This answers "how many edges does this lens light, and in what states" in a
// second, which is the question that would have settled both.
//
//   node tests/rota/lens_check.js        (needs the cockpit running)
const fs = require('fs');
const vm = require('vm');
const { execSync } = require('child_process');

const HOST = process.env.ROTA_COCKPIT || 'http://127.0.0.1:8899';
const get = (u) => JSON.parse(execSync(`curl -s --max-time 10 ${HOST}${u}`,
                                       { maxBuffer: 64 * 1024 * 1024 }).toString());

const ctx = vm.createContext({
  document: { addEventListener() {}, getElementById() { return null; },
              querySelectorAll() { return []; } },
  window: {}, console,
  fetch: () => Promise.reject(new Error('no network in here')),
  localStorage: { getItem() { return null; }, setItem() {} },
  DATA: { trace: get('/trace.json'), graph: get('/graph.json'),
          cases: get('/cases.json'), stories: get('/stories.json') },
});

vm.runInContext(
  fs.readFileSync(`${__dirname}/../../rota/cockpit/static/graphview.js`, 'utf8'),
  ctx);

const probe = `
  GV.trace = DATA.trace;
  GV.graph = DATA.graph;
  GV.stories = DATA.stories;

  const report = (name) => {
    const lit = gvLit();
    const by = {};
    for (const e of GV.graph.edges) {
      const st = lit.get(ek([e.s, e.t, e.type]));
      if (st) by[st] = (by[st] || 0) + 1;
    }
    const shown = Object.values(by).reduce((a, b) => a + b, 0);
    console.log('  ' + name.padEnd(26) + String(shown).padStart(3)
                + '/' + GV.graph.edges.length + '  ' + JSON.stringify(by));
    return shown;
  };

  console.log('edges lit, per lens:');
  let bad = [];

  GV.source = 'coverage';
  if (report('coverage') === 0 && GV.trace.coverage.covered.length) bad.push('coverage');

  // A story's first step is a title card and lights nothing, which is correct.
  // Walk to a step that has edges before judging the lens.
  GV.source = 'story';
  const steps = GV.stories[0]?.steps || [];
  GV.stepIx = Math.max(0, steps.findIndex(s => (s.edges || []).length));
  if (report('story @ step ' + GV.stepIx) === 0 && steps.some(s => s.edges.length))
    bad.push('story');

  // An empty run is an empty database, not a broken lens.
  GV.source = 'run';
  const n = report('run');
  if (n === 0 && (GV.trace.steps || []).length) bad.push('run');
  else if (!(GV.trace.steps || []).length) console.log('    (no sessions recorded)');

  GV.source = 'design';
  if (report('design') !== 0) bad.push('design lights something and should not');

  const c = DATA.cases.find(x => x.edges.reading.length) || DATA.cases[0];
  GV.source = 'case';
  GV.caseEdges = c.edges;
  GV.caseSituation = c.situation;
  if (report('case ' + c.id.slice(0, 20)) === 0) bad.push('case');

  if (bad.length) {
    console.log('\\nLENSES LIGHTING NOTHING: ' + bad.join(', '));
  } else {
    console.log('\\nevery lens lights something');
  }
  bad.length;
`;

process.exitCode = vm.runInContext(probe, ctx) ? 1 : 0;
