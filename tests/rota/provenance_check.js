// Does the "why is this here" panel actually render? Against a live cockpit.
//
// `node --check` proves the file parses and nothing else. The lens panels
// "looked broken" three times with correct logic underneath, and every time
// reading the code proved nothing -- so this runs the real function over real
// data and asserts the panel contains the facts it exists to show.
//
//   node tests/rota/provenance_check.js <table> <row>   (needs the cockpit up)
//
// Exits non-zero when the panel renders without the session, the wake, or the
// admission that the working set is not retained -- the three things that make
// it worth opening.
const fs = require('fs');
const vm = require('vm');
const { execSync } = require('child_process');

const HOST = process.env.ROTA_COCKPIT || 'http://127.0.0.1:8899';
const TABLE = process.argv[2] || 'glossary_terms';
const ROW = process.argv[3] || 'alarm';
const get = (u) => execSync(`curl -s --max-time 15 "${HOST}${u}"`,
                            { maxBuffer: 64 * 1024 * 1024 }).toString();

let panelHTML = '';

// A fake element rich enough for the file's top-level wiring, which runs on
// load and touches listeners, classes and styles before any panel is asked
// for. A thinner stub throws there and never reaches the function under test —
// which would look exactly like the panel being broken.
const makeEl = (id) => {
  const e = {
    id, _html: '',
    addEventListener() {}, removeEventListener() {}, appendChild() {},
    remove() {}, focus() {}, blur() {}, scrollIntoView() {}, click() {},
    getBoundingClientRect: () => ({ top: 0, left: 0, width: 0, height: 0 }),
    classList: { add() {}, remove() {}, toggle() {}, contains: () => false },
    style: {}, dataset: {}, children: [], parentNode: null,
    querySelector: () => null, querySelectorAll: () => [],
    setAttribute() {}, getAttribute: () => null,
  };
  Object.defineProperty(e, 'innerHTML', {
    get() { return e._html; },
    set(v) { e._html = v; if (id === 'pbody') panelHTML = v; },
  });
  Object.defineProperty(e, 'textContent', { get() { return ''; }, set() {} });
  return e;
};
const els = {};
const el = (id) => (els[id] ||= makeEl(id));

const ctx = vm.createContext({
  document: {
    addEventListener() {}, querySelectorAll() { return []; },
    querySelector() { return null; },
    createElement: (tag) => makeEl(tag),
    body: makeEl('body'), documentElement: makeEl('html'),
    getElementById(id) { return el(id); },
  },
  window: { addEventListener() {}, location: { hash: '' },
            requestAnimationFrame(f) { f(); }, matchMedia: () => ({ matches: false }) },
  console,
  fetch: (u) => Promise.resolve({ json: () => Promise.resolve(JSON.parse(get(u))) }),
  localStorage: { getItem() { return null; }, setItem() {} },
  String, Object, JSON, Math, Array, Date, Number, Boolean, Error, Promise,
  encodeURIComponent, decodeURIComponent, setTimeout, clearTimeout,
  // The file starts a live-refresh timer on load. It must exist and must not
  // actually fire: a poll running under the check would race the assertion.
  setInterval: () => 0, clearInterval: () => {},
  DATA: {
    graph: JSON.parse(get('/graph.json')),
    layout: JSON.parse(get('/layout.json')),
    trace: JSON.parse(get('/trace.json')),
    stories: JSON.parse(get('/stories.json')),
    cases: JSON.parse(get('/cases.json')),
  },
});

// Both files, in the order `viewer.html` loads them. `panels.js` uses helpers
// that live in `graphview.js` -- `esc` among them -- so loading it alone throws
// inside the first render and looks exactly like the panel being broken.
for (const f of ['graphview.js', 'panels.js']) {
  vm.runInContext(
    fs.readFileSync(`${__dirname}/../../rota/cockpit/static/${f}`, 'utf8'), ctx);
}

// Which fifth thing the panel owes depends on what the run kept. A session
// with recorded `turns` owes the verbatim transcript; one without owes the
// admission that the rebuilt brief is a reconstruction. Asserting "not
// retained" unconditionally made the check fail on exactly the sessions with
// the *best* evidence.
const prov = JSON.parse(get(`/provenance.json?table=${
  encodeURIComponent(TABLE)}&row=${encodeURIComponent(ROW)}`));
const recorded = !!(((prov.shown || {}).turns) || []).length;

ctx.showProvenance(TABLE, ROW).then(() => {
  const want = [
    ['WHAT IT SAYS', 'the row itself'],
    ['WHAT WOKE IT', 'the wake'],
    ['WHO WROTE IT', 'the session'],
    ['WHAT IT WAS SHOWN', 'the brief'],
    recorded
      ? ['recorded verbatim', 'the transcript the run kept']
      : ['not retained', 'the admission about the working set'],
  ];
  const missing = want.filter(([needle]) => !panelHTML.includes(needle));
  if (!panelHTML) { console.error('the panel rendered nothing at all'); process.exit(1); }
  for (const [needle, what] of missing) console.error(`missing ${what}: ${needle}`);
  console.log(missing.length ? 'FAIL' : `ok — ${panelHTML.length} chars rendered`);
  process.exit(missing.length ? 1 : 0);
}).catch((e) => { console.error('threw:', e.message); process.exit(1); });
