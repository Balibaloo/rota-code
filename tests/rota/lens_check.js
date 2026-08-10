// What each lens lights, and what each key row selects — without a browser.
//
// The coverage lens "looked broken" three times: once because covered edges
// carried no positive mark, once because the mark was five pixels at 22%
// opacity on a near-white canvas, and once because hovering its key rows
// resolved to nothing and dimmed everything. Every time the logic underneath
// was correct, and every time reading the code proved nothing.
//
//   node tests/rota/lens_check.js        (needs the cockpit running)
//
// Exits non-zero when a lens lights nothing it should, or a key row selects
// nothing — the two failures indistinguishable from a broken lens on screen.
const fs = require('fs');
const vm = require('vm');
const { execSync } = require('child_process');

const HOST = process.env.ROTA_COCKPIT || 'http://127.0.0.1:8899';
const get = (u) => JSON.parse(execSync(`curl -s --max-time 15 ${HOST}${u}`,
                                       { maxBuffer: 64 * 1024 * 1024 }).toString());

const ctx = vm.createContext({
  document: { addEventListener() {}, getElementById() { return null; },
              querySelectorAll() { return []; } },
  window: {}, console,
  fetch: () => Promise.reject(new Error('no network in here')),
  localStorage: { getItem() { return null; }, setItem() {} },
  DATA: {
    trace: get('/trace.json'),
    graph: get('/graph.json'),
    cases: get('/cases.json'),
    stories: get('/stories.json'),
  },
});

vm.runInContext(
  fs.readFileSync(`${__dirname}/../../rota/cockpit/static/graphview.js`, 'utf8'), ctx);
process.exitCode = vm.runInContext(
  fs.readFileSync(`${__dirname}/lens_probe.js`, 'utf8'), ctx) ? 1 : 0;
