// The graph. Hand-rolled SVG rather than a library: the layout is fixed, ~22
// nodes and ~110 edges draw comfortably, the cockpit stays offline, and we keep
// full control of the overlays — which are the whole reason for drawing it.
//
// Two graphs share this renderer:
//   team     roles, artefacts and the edges between them — the structure
//   chat     the message DAG — the conversation that structure produced
//
// Styling keys off node *properties* rather than ids, so when the vocabulary
// work reclassifies things the visual language already covers it.

const GV = {graph:null, layout:null, stories:null, trace:null, msgs:null,
            mode:'team', source:'design', storyIx:0, stepIx:0,
            focus:null, inhabit:null, blast:null, keyhl:null,
            view:{x:0,y:0,k:1}, dragNode:null, dirty:false,
            settings:{collapse:'auto', labels:'auto', far:0.62}};

try {
  Object.assign(GV.settings, JSON.parse(localStorage.getItem('rota.gv') || '{}'));
} catch {}

function gvSet(k, v) {
  GV.settings[k] = v;
  try { localStorage.setItem('rota.gv', JSON.stringify(GV.settings)); } catch {}
  gvControls(); gvDraw();
}

// The threshold slider. Deliberately *not* gvSet: rebuilding the popover on
// every input event replaces the range element mid-drag, and the pointer is
// then holding something that no longer exists. So this writes the readout in
// place and redraws the canvas only.
function gvFar(v) {
  GV.settings.far = +v;
  try { localStorage.setItem('rota.gv', JSON.stringify(GV.settings)); } catch {}
  gvFarNote(); gvDraw();
}

// Where the fold sits, and where you are. Called on drag and on every draw, so
// zooming moves the readout under a stationary slider — which is the thing that
// makes the number legible.
function gvFarNote() {
  const now = document.getElementById('gfarnow');
  const note = document.getElementById('gfarnote');
  if (!now || !note) return;
  const auto = GV.settings.collapse === 'auto';
  now.textContent = `${far().toFixed(2)}×`;
  note.innerHTML = auto
    ? `Folds below <b>${far().toFixed(2)}×</b>. Now at
       <b>${GV.view.k.toFixed(2)}×</b> — ${collapsing()
         ? 'folded' : 'every verb drawn separately'}.`
    : `Threshold applies to <em>when far out</em> only.`;
}

// Below this the labels are unreadable and the parallel edges are a smudge, so
// both fold away. 0.62 was measured by eye — the zoom at which a 10px label
// stops being a word and starts being texture — but "by eye" depends on whose
// eye and what screen, so it is a setting with that number as its default.
const FAR_DEFAULT = 0.62;
const far = () => GV.settings.far ?? FAR_DEFAULT;

const collapsing = () => GV.settings.collapse === 'always'
  || (GV.settings.collapse === 'auto' && GV.view.k < far());
const labelling = () => GV.settings.labels === 'always'
  || (GV.settings.labels === 'auto' && GV.view.k >= far());

// Light canvas, dark chrome. On a light ground the edge colours can be
// saturated enough to tell four relationships apart without shouting, which
// they could not on the dark one.
const ESTYLE = {
  writes:   {c:'#2563eb', dash:'',    head:true,  label:'#1d4ed8'},
  reads:    {c:'#15803d', dash:'5 3', head:true,  label:'#166534'},
  messages: {c:'#c2410c', dash:'',    head:true,  label:'#9a3412'},
  refs:     {c:'#64748b', dash:'',    head:false, label:'#475569'},
};

const esc = s => String(s ?? '').replace(/[<>&]/g,c=>({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]));
const ek = e => `${e[0]}|${e[1]}|${e[2]}`;

// Entity kinds get different containers: a person is not a document is not a
// journal, and the eye should not have to read the label to know which.
// Where a ray leaves a node's box, in its own dimensions. Nodes are not one
// size -- a role is 152x50 against a record's 152x42 -- so a shared constant
// puts the point inside one of them.
function onBox(id, dx, dy) {
  const p = GV.layout[id];
  const node = GV.graph.nodes.find(x => x.id === id);
  const sh = SHAPE[node ? kindOf(node) : 'record'] || SHAPE.record;
  const hw = sh.w / 2 + 2, hh = sh.h / 2 + 2;      // 2px so the head clears
  const ax = Math.abs(dx) || 1e-6, ay = Math.abs(dy) || 1e-6;
  const t = Math.min(hw / ax, hh / ay);
  return { x: p.x + dx * t, y: p.y + dy * t };
}

function kindOf(n) {
  if (n.type === 'principal') return 'principal';
  if (n.type === 'role') return 'role';
  if (n.contact === false) return 'journal';   // fact artefact: read, never asked
  if (n.owner === 'scheduler') return 'derived';
  return 'record';
}

// State colours live here and nowhere else. The renderer and the legend had
// drifted to different values for the same three states -- the legend claimed
// #d97706 for "ready" while the graph drew #e6b25a -- which makes a legend worse
// than none: it teaches a colour the picture does not use.
// ---------------------------------------------------------------------------
// The visual language, stated once.
//
// **One channel answers one question.** The rule the picture had lost: states
// were added to whichever channel was free, so `live` and `gap` ended up the
// same red meaning different things, `ready` and `now` two ambers apart, and
// violet meant "cascade reach" in one lens and "given" in another.
//
//   node shape + fill   what kind of thing this is        never varies by lens
//   node border colour  what this lens says about it      never varies by kind
//   node border weight  emphasis
//   edge colour + dash  what kind of relationship         never varies by lens
//   edge halo           the lens making a claim about it
//   edge weight         how strongly the lens points at it
//   opacity             in scope for this lens, or not
//
// Edges keep their type colour under every lens, because that colour *is* their
// identity — a read is green whether or not a case forbids it. When a lens has
// something to say about an edge it says it with a halo underneath, so the
// claim and the identity are both readable instead of overwriting each other.
//
// **Five meanings, one colour each, the same in every lens.** That is what
// makes a second lens learnable rather than a second vocabulary.
//
//            live tab        coverage      story / run    case
//   ACTOR    mid-session     --            --             role under test
//   INPUT    cascade reach   --            steps so far   given to the role
//   OUTPUT   ready to wake   --            current step   watched / required
//   PROVEN   --              exercised     --             --
//   DENIED   --              untested      --             forbidden
//   INERT    --              --            --             scaffolding
//
// `exercised` was OUTPUT for a while and it was a stretch: a covered edge is
// not "what comes out", it is "this has been checked and it holds". That is a
// meaning of its own, and it pairs with DENIED the way a pass pairs with a
// fail -- which is also why a coverage picture with no positive mark read as
// broken. Eighty-four red halos and nothing saying the other thirty-four were
// fine.
// ---------------------------------------------------------------------------
const LENS = {
  actor:  '#7c3aed',   // who is acting
  input:  '#0891b2',   // what it was given, or what a change would reach
  output: '#d97706',   // what it produces, and what we are watching for
  denied: '#dc2626',   // what must not happen, or has not happened
  proven: '#15803d',   // checked, and satisfied
  inert:  '#94a3b8',   // present, and out of reach for this lens
};

const STATE = {
  ready:  LENS.output,
  live:   LENS.actor,
  blast:  LENS.input,
  gap:    LENS.denied,
  now:    LENS.output,
  ink:    '#334155',
  faint:  '#94a3b8',
  grid:   '#dde5ee',
  arrow:  '#475569',
};

const SHAPE = {
  principal:  {w:140, h:52, rx:26, fill:'#fdf1dc', stroke:'#b45309', dash:'', ink:'#7c2d12'},
  role:    {w:152, h:50, rx:10, fill:'#ffffff', stroke:'#3b6ea5', dash:'', ink:'#132a44'},
  record:  {w:152, h:42, rx:4,  fill:'#e4f3e8', stroke:'#2f855a', dash:'', ink:'#14532d'},
  journal: {w:152, h:42, rx:4,  fill:'#eef7f0', stroke:'#4b9e74', dash:'4 3', ink:'#166534'},
  derived: {w:152, h:42, rx:4,  fill:'#f1f5f2', stroke:'#94a3a0', dash:'2 4', ink:'#475569'},
};

// ---------------------------------------------------------------------------
// One router, for every edge.
//
// There used to be two. `refs` went through an orthogonal router -- channels,
// obstacle avoidance, anchors on box faces -- and reads, writes and messages
// bowed: a bezier offset by `rank * 30`, clipped against the box using its own
// control point. Every fix the arcs needed was a fix to make them behave like
// the elbows: which side to bow to, where to clip, how to keep labels apart,
// when to draw straight instead. Three geometries in one frame, none of them
// agreeing about where an edge leaves a node.
//
// Orthogonal wins on the things this picture is for:
//
//   arrival angle   perpendicular to the face, so a head always reads as
//                   arriving rather than passing
//   separation      parallel edges leave from different *points on the box*,
//                   which is what they are: different relationships, not one
//                   relationship drawn unsteadily
//   labels          sit on an axis-aligned run, horizontal, centred. The
//                   collision problem disappears instead of being managed
//   obstacles       a run can be routed around a node; an arc sails over it
//
// Ports are assigned once per draw, for the whole graph, because a slot is a
// position among *all* the edges using that face -- a read and a write and a
// message leaving one node's right side have to know about each other.
// ---------------------------------------------------------------------------

const STUB = 15;          // how far a run leaves the face before it may turn
const SLOT_MAX = 15;      // widest gap between neighbouring ports
const CORNER = 7;         // corner rounding

function faceOf(a, b) {
  // The face an edge leaves by: whichever axis separates the two nodes more.
  // Ties go horizontal, because the layout is wider than it is tall and a
  // sideways departure crosses fewer rows.
  const dx = b.x - a.x, dy = b.y - a.y;
  if (Math.abs(dx) >= Math.abs(dy)) return dx >= 0 ? 'right' : 'left';
  return dy >= 0 ? 'bottom' : 'top';
}

const OPPOSITE = {right: 'left', left: 'right', top: 'bottom', bottom: 'top'};
const OUTWARD  = {right: [1, 0], left: [-1, 0], top: [0, -1], bottom: [0, 1]};

function shapeOf(id) {
  const n = GV.graph.nodes.find(x => x.id === id);
  return SHAPE[n ? kindOf(n) : 'record'] || SHAPE.record;
}

// Every (node, face) gets its edges in an order that does not cross: sorted by
// where the other end sits along the face's free axis. Two edges leaving the
// right side towards nodes above and below each other keep that relationship,
// so the lines run parallel instead of swapping over.
function computePorts(list) {
  GV.port = {};
  const byFace = {};
  for (const e of list) {
    const a = GV.layout[e.s], b = GV.layout[e.t];
    if (!a || !b) continue;
    const sf = faceOf(a, b), tf = OPPOSITE[sf];
    for (const [node, face, other] of [[e.s, sf, b], [e.t, tf, a]]) {
      const k = `${node}|${face}`;
      (byFace[k] = byFace[k] || []).push({e, other, node, face});
    }
  }
  for (const [k, entries] of Object.entries(byFace)) {
    const [, face] = k.split('|');
    const along = (face === 'left' || face === 'right') ? 'y' : 'x';
    entries.sort((p, q) => p.other[along] - q.other[along]
                        || String(p.e.v || '').localeCompare(String(q.e.v || '')));
    entries.forEach((p, i) => {
      GV.port[`${p.e.s}|${p.e.t}|${p.e.type}|${p.e.v}|${p.node}`] =
        {i, n: entries.length, face};
    });
  }
}

// The point on the box, and the direction the run leaves in.
function portPoint(node, face, i, n) {
  const p = GV.layout[node], sh = shapeOf(node);
  const vertical = face === 'left' || face === 'right';
  const extent = (vertical ? sh.h : sh.w) - 12;
  const gap = n > 1 ? Math.min(SLOT_MAX, extent / (n - 1)) : 0;
  const off = (i - (n - 1) / 2) * gap;
  const [ox, oy] = OUTWARD[face];
  return {
    x: p.x + ox * sh.w / 2 + (vertical ? 0 : off),
    y: p.y + oy * sh.h / 2 + (vertical ? off : 0),
    ox, oy,
  };
}

// Boxes to route around: every node except the two being joined. The old ref
// router looked at artefacts only, so a run could pass straight through a role.
function obstacles(skip) {
  const M = 14;
  return GV.graph.nodes
    .filter(n => GV.layout[n.id] && !skip.includes(n.id) && gvVisible(n.id))
    .map(n => {
      const p = GV.layout[n.id], sh = SHAPE[kindOf(n)];
      return {x1: p.x - sh.w / 2 - M, x2: p.x + sh.w / 2 + M,
              y1: p.y - sh.h / 2 - M, y2: p.y + sh.h / 2 + M};
    });
}

const crossesV = (boxes, x, ya, yb) => boxes.filter(b =>
  x > b.x1 && x < b.x2 && Math.max(ya, yb) > b.y1 && Math.min(ya, yb) < b.y2).length;
const crossesH = (boxes, y, xa, xb) => boxes.filter(b =>
  y > b.y1 && y < b.y2 && Math.max(xa, xb) > b.x1 && Math.min(xa, xb) < b.x2).length;

// A polyline with its corners rounded, and the segments collapsed first: a
// zero-length jog leaves a stray quarter-circle where the line should be flat.
function polyPath(pts, r) {
  const p = [pts[0]];
  for (const q of pts.slice(1))
    if (Math.abs(q.x - p[p.length - 1].x) > 0.5 || Math.abs(q.y - p[p.length - 1].y) > 0.5)
      p.push(q);
  if (p.length < 2) return {d: '', pts: p};

  let d = `M${p[0].x.toFixed(1)} ${p[0].y.toFixed(1)}`;
  for (let i = 1; i < p.length - 1; i++) {
    const a = p[i - 1], b = p[i], c = p[i + 1];
    const inLen = Math.hypot(b.x - a.x, b.y - a.y);
    const outLen = Math.hypot(c.x - b.x, c.y - b.y);
    const rr = Math.min(r, inLen / 2, outLen / 2);
    const i1 = {x: b.x + (a.x - b.x) / inLen * rr, y: b.y + (a.y - b.y) / inLen * rr};
    const i2 = {x: b.x + (c.x - b.x) / outLen * rr, y: b.y + (c.y - b.y) / outLen * rr};
    d += ` L${i1.x.toFixed(1)} ${i1.y.toFixed(1)}`
       + ` Q${b.x.toFixed(1)} ${b.y.toFixed(1)} ${i2.x.toFixed(1)} ${i2.y.toFixed(1)}`;
  }
  const last = p[p.length - 1];
  d += ` L${last.x.toFixed(1)} ${last.y.toFixed(1)}`;
  return {d, pts: p};
}

// The longest axis-aligned run, and its middle. A label wants the most room and
// a direction it can be read along -- which for an orthogonal path is always
// one of the segments, never a point on a curve chosen by parameter.
function longestRun(pts) {
  let best = null, bestLen = -1;
  for (let i = 1; i < pts.length; i++) {
    const a = pts[i - 1], b = pts[i];
    const len = Math.hypot(b.x - a.x, b.y - a.y);
    if (len > bestLen) { bestLen = len; best = {a, b}; }
  }
  if (!best) return {x: pts[0].x, y: pts[0].y, len: 0, vertical: false};
  return {
    x: (best.a.x + best.b.x) / 2,
    y: (best.a.y + best.b.y) / 2,
    len: bestLen,
    dx: best.b.x - best.a.x,
    dy: best.b.y - best.a.y,
    vertical: Math.abs(best.b.y - best.a.y) > Math.abs(best.b.x - best.a.x),
  };
}

/**
 * Route one edge. Returns {d, pts, label} or null.
 *
 * Straight when the ports line up, one turn when they do not, and a channel
 * between them when the straight-through would cross a node.
 */
function route(e) {
  const a = GV.layout[e.s], b = GV.layout[e.t];
  if (!a || !b) return null;
  const key = `${e.s}|${e.t}|${e.type}|${e.v}`;
  const sp = GV.port[`${key}|${e.s}`], tp = GV.port[`${key}|${e.t}`];
  if (!sp || !tp) return null;

  const A = portPoint(e.s, sp.face, sp.i, sp.n);
  const B = portPoint(e.t, tp.face, tp.i, tp.n);
  const horiz = sp.face === 'left' || sp.face === 'right';

  // Out of the face before turning, so a line never leaves along the box edge
  // it is attached to.
  const A2 = {x: A.x + A.ox * STUB, y: A.y + A.oy * STUB};
  const B2 = {x: B.x + B.ox * STUB, y: B.y + B.oy * STUB};

  let pts;
  if (horiz ? Math.abs(A.y - B.y) < 1 : Math.abs(A.x - B.x) < 1) {
    pts = [A, B];                                  // the ports agree: no turn
  } else {
    const boxes = obstacles([e.s, e.t]);
    // Candidate channels: halfway, and the clear lanes between rows or columns
    // of boxes. Scored by how many nodes the run would cross.
    const lo = horiz ? Math.min(A2.x, B2.x) : Math.min(A2.y, B2.y);
    const hi = horiz ? Math.max(A2.x, B2.x) : Math.max(A2.y, B2.y);
    const mid = (lo + hi) / 2;
    const lanes = [mid];
    for (const box of boxes) {
      const before = horiz ? box.x1 : box.y1, after = horiz ? box.x2 : box.y2;
      for (const c of [before - 10, after + 10])
        if (c > lo + 4 && c < hi - 4) lanes.push(c);
    }
    let best = mid, bestCost = Infinity;
    for (const c of lanes) {
      const cost = horiz
        ? crossesH(boxes, A2.y, A2.x, c) + crossesV(boxes, c, A2.y, B2.y)
          + crossesH(boxes, B2.y, c, B2.x)
        : crossesV(boxes, A2.x, A2.y, c) + crossesH(boxes, c, A2.x, B2.x)
          + crossesV(boxes, B2.x, c, B2.y);
      // Ties go to the channel nearest halfway: a detour needs a reason.
      const score = cost * 1000 + Math.abs(c - mid);
      if (score < bestCost) { bestCost = score; best = c; }
    }
    // Parallel edges get parallel channels. Every edge between one pair scores
    // the lanes identically and so picks the same one -- their end segments
    // differ because the ports differ, but the long middle run would land on
    // exactly the same line, which is the collision ports were meant to end,
    // reappearing in the middle of the path instead of at the box.
    const spread = (sp.i - (sp.n - 1) / 2) * 13;
    const ch = Math.max(lo + 6, Math.min(hi - 6, best + spread));

    pts = horiz
      ? [A, A2, {x: ch, y: A2.y}, {x: ch, y: B2.y}, B2, B]
      : [A, A2, {x: A2.x, y: ch}, {x: B2.x, y: ch}, B2, B];
  }

  const path = polyPath(pts, CORNER);
  return {d: path.d, pts: path.pts, label: longestRun(path.pts),
          startFace: sp.face, endFace: tp.face};
}


function gvLit() {
  const lit=new Map();
  // The default lens makes no claim. Opening on coverage meant the first thing
  // anybody saw was a picture half-painted red about a question they had not
  // asked yet â€” the structure, which is what the graph is *for*, was the one
  // thing you had to switch to.
  if (GV.source==='design') return lit;
  // A case lights what it *instantiates*, plus what it asserts on top.
  //
  // The first version lit the edges the mode offered, which is a picture of
  // what the role could do -- identical for every case in that mode. What a
  // case is actually about is the rows it seeds and how they hang together, and
  // the `refs` edges between two seeded artefacts are only drawn where the
  // seeded data really references seeded data.
  if (GV.source==='case' && GV.caseEdges) {
    // How the situation hangs together, then how the role reaches into it,
    // then what the case asserts. Without the middle layer the role node sat
    // unconnected and the picture read as "everything dimmed" -- which it was,
    // because the only lit things were islands.
    (GV.caseSituation?.links||[]).forEach(([a,b])=>lit.set(`${a}|${b}|refs`,'past'));
    (GV.caseEdges.reading||[]).forEach(e=>lit.set(ek(e),'seeded'));
    (GV.caseEdges.writing||[]).forEach(e=>lit.set(ek(e),'now'));
    (GV.caseEdges.required||[]).forEach(e=>lit.set(ek(e),'now'));
    (GV.caseEdges.forbidden||[]).forEach(e=>lit.set(ek(e),'forbidden'));
    return lit;
  }
  if (GV.source==='coverage') {
    (GV.trace.coverage.covered||[]).forEach(e=>lit.set(ek(e),'covered'));
    return lit;
  }
  const steps=gvSteps();
  for (let i=0;i<=GV.stepIx && i<steps.length;i++)
    (steps[i].edges||[]).forEach(e=>lit.set(ek(e), i===GV.stepIx?'now':'past'));
  return lit;
}

const gvSteps = () =>
  GV.source==='story' ? (GV.stories[GV.storyIx]?.steps||[])
: GV.source==='run'   ? (GV.trace.steps||[]) : [];

// The graph collapses to exactly what one role can reach. Not "neighbours" --
// its namespace. Double-click Critic and the system model is not dimmed, it is
// gone, because `sandbox.build` never created a function that could fetch it.
//
// It was called "inhabit", which reads as a mood rather than a filter. The UI
// says "show only what it reaches"; the function keeps the short name because
// it is called from six places and the label is the part people read.
function gvVisible(id) {
  if (!GV.inhabit || id===GV.inhabit) return true;
  return GV.graph.edges.some(e =>
    (e.s===GV.inhabit && e.t===id && e.type!=='refs') ||
    (e.s===id && e.t===GV.inhabit && e.type==='messages'));
}

// ---------------------------------------------------------------- chat graph
// The message log is a DAG: every message refs its cause. Laid out by thread
// across, depth down, so a conversation's shape is legible — where it branched,
// where a round closed, what is still open.
function chatLayout() {
  const pos={}, byThread={};
  (GV.msgs.messages||[]).forEach(m => {
    (byThread[m.thread_id] = byThread[m.thread_id] || []).push(m);
  });
  let col=0;
  for (const th of Object.keys(byThread)) {
    byThread[th].forEach((m,i) => {
      pos[m.id] = {x: 200 + col*330 + (i%2)*90, y: 120 + i*95};
    });
    col++;
  }
  return pos;
}

function drawChat() {
  const pos = chatLayout(), msgs = GV.msgs.messages||[];
  let edges='', nodes='';

  for (const m of msgs) {
    if (!m.cause_id || !pos[m.cause_id] || !pos[m.id]) continue;
    const a=pos[m.cause_id], b=pos[m.id];
    edges += `<path d="M${a.x} ${a.y+18} C${a.x} ${a.y+60} ${b.x} ${b.y-60} ${b.x} ${b.y-18}"
      fill="none" stroke="${ESTYLE.refs.c}" stroke-width="1.6" marker-end="url(#head)"/>`;
  }

  for (const m of msgs) {
    const p=pos[m.id]; if(!p) continue;
    const w=250, h=m.produced?58:38;
    const open = m.status==='open';
    // The chat graph shares the canvas, so it shares the palette. It was still
    // drawn in dark-theme colours and went invisible when the ground changed.
    const stroke = open ? STATE.ready
      : m.produced?.committed ? SHAPE.role.stroke : STATE.faint;
    const fill = m.from_role==='principal' ? SHAPE.principal.fill : '#ffffff';
    const ink  = m.from_role==='principal' ? SHAPE.principal.ink  : SHAPE.role.ink;
    const out = m.produced
      ? `${m.produced.calls.length} call(s)` + (m.produced.writes.length
          ? ` · ${m.produced.writes.length} write(s)` : '')
      : open ? 'awaiting' : '';

    nodes += `<g class="gnode" data-msg="${m.id}" transform="translate(${p.x-w/2},${p.y-h/2})">
      <rect width="${w}" height="${h}" rx="7" fill="${fill}" stroke="${stroke}"
        stroke-width="${open?2.4:1.2}"/>
      <text x="10" y="16" class="mfrom" fill="${ink}">${esc(m.from_role)} → ${esc(m.to_role)}</text>
      <text x="${w-10}" y="16" class="mverb" fill="${ESTYLE.messages.c}">${esc(m.verb)}</text>
      ${m.produced?`<text x="10" y="34" class="mout" fill="${STATE.ink}">${
        esc(m.produced.role)}: ${esc(out)}</text>`:''}
      ${m.produced?`<text x="10" y="50" class="mrefs" fill="${STATE.faint}">${esc(
        (m.produced.calls||[]).slice(0,3).join(' '))}</text>`
       :`<text x="10" y="32" class="mrefs" fill="${STATE.faint}">${esc(out)}</text>`}
    </g>`;
  }
  return {edges, nodes};
}

// ---------------------------------------------------------------- team graph
function drawTeam() {
  const lit=gvLit();
  const ready=new Set((GV.trace.overlay.ready||[]).map(r=>r.role));
  const claimed=GV.trace.overlay.claimed||{};
  const vol=GV.trace.overlay.volume||{};
  const uncovered=new Set((GV.trace.coverage.missing||[]).map(ek));
  const blast=GV.blast?new Set(GV.blast.artefacts):null;
  let edges='', nodes='';

  // Collapsed groups are per (source, target, *type*). Not per pair: seventeen
  // pairs carry more than one type -- `liaison -> brief` is both a read and a
  // write -- and fusing those would put one line where two different kinds of
  // relationship are, which is the one thing the colour system must never do.
  const fold = collapsing();
  const groupOf = e => `${e.s}|${e.t}|${e.type}`;
  const plan = fold ? foldPlan() : null;
  const drawn = new Set();

  // Which lines exist is settled before any of them is placed, because a port
  // is a position among *all* the edges using a face. Deciding that edge by
  // edge would give the first one a slot chosen without knowing how many were
  // coming -- and folding changes the count, so it cannot be cached either.
  const lines = [];
  for (const e of GV.graph.edges) {
    if(!GV.layout[e.s]||!GV.layout[e.t]||!gvVisible(e.s)||!gvVisible(e.t)) continue;
    const group = groupOf(e);
    const p = fold ? plan[group] : null;
    if (fold) {
      if (p.skip) continue;             // its opposite carries both directions
      if (drawn.has(group)) continue;   // one line stands for the whole group
      drawn.add(group);
    }
    lines.push({e, p, kin: fold ? p.members : [e]});
  }
  computePorts(lines.map(l => l.e));

  for (const {e, p, kin} of lines) {
    const a=GV.layout[e.s], b=GV.layout[e.t];

    const st=ESTYLE[e.type]||ESTYLE.refs, key=ek([e.s,e.t,e.type]), state=lit.get(key);
    const incident = GV.focus && (e.s===GV.focus||e.t===GV.focus);

    // The line keeps its type colour under every lens; the lens speaks with a
    // halo. Recolouring meant a forbidden read and an untested write looked
    // like the same thing, and neither looked like a read or a write.
    let op=0.16, w=1.2, col=st.c, halo=null;
    if (GV.source==='design') { op=.5; w=1.5; }
    else if (GV.source==='coverage') {
      if (state==='covered'){op=.9;w=2;halo=LENS.proven;}
      else if (uncovered.has(key)){op=.55;w=1.6;halo=LENS.denied;}
    } else if (state==='now'){op=1;w=2.6;halo=LENS.output;}
    else if (state==='seeded'){op=.8;w=2;halo=LENS.input;}
    else if (state==='forbidden'){op=.85;w=2;halo=LENS.denied;}
    else if (state==='past'){op=.45;w=1.8;}
    if (GV.focus) op = incident?Math.max(op,.95):.05;
    if (GV.inhabit) op = Math.max(op,.7);

    // Hovering the key selects rather than annotates: everything else recedes,
    // so "what is a journal" is answered by the picture instead of by the
    // sentence underneath it.
    if (GV.keyhl) {
      const sel = keySelects(GV.keyhl);
      if (sel.edges) op = sel.edges(e) ? Math.max(op, .95) : 0.05;
      else if (sel.nodes) op = (sel.nodes.has(e.s) || sel.nodes.has(e.t))
                             ? Math.max(op, .6) : 0.05;
    }

    // One router for every edge type. Refs keep their crow's feet, because
    // multiplicity is a claim only a ref makes; the geometry is now shared.
    const r = route(e);
    if (!r) continue;
    const d = r.d;
    const lx = r.label.x, ly = r.label.y;
    let markers = '';
    if (e.type === 'refs') {
      const [sc, tc] = (e.card || 'n:1').split(':');
      markers = `marker-start="url(#${sc.trim() === '1' ? 'one-s' : 'many-s'})"`
              + ` marker-end="url(#${tc.trim() === '1' ? 'one-e' : 'many-e'})"`;
    }

    // Arrowheads are per type and match the edge colour. They were there all
    // along and invisible: one slate-grey marker, and `opacity` on a path
    // applies to its markers too — so at the resting opacity of 0.16 the head
    // was a grey smudge on a coloured line. A direction you have to zoom in to
    // read is a direction the picture is not carrying.
    const headId = markers ? ''
      : (fold && p.bidir
          ? `marker-start="url(#head-${e.type})" marker-end="url(#head-${e.type})"`
          : `marker-end="url(#head-${e.type})"`);
    // Wide and clearly tinted. The first version was five pixels at 22%
    // opacity, which on a near-white canvas is nothing at all -- the coverage
    // lens looked switched off because its whole signal was invisible.
    if (halo) edges += `<path d="${d}" fill="none" stroke="${halo}"
      stroke-width="${w + 7}" opacity="${Math.min(.55, op * .7)}"
      stroke-linecap="round"/>`;
    edges += `<path d="${d}" fill="none"
      stroke="${col}" stroke-width="${w}" stroke-dasharray="${st.dash}" opacity="${op}"
      ${markers || (st.head?headId:'')} class="gedge"
      data-e="${e.s}|${e.t}|${e.type}|${esc(e.v||'')}"/>`;

    // Edge names on while they are readable — the grammar is the content, not
    // a hover reward, but at a distance a 10px label is texture rather than a
    // word and a dozen of them is a smudge over the structure.
    const total = fold ? kin.length + (p.back || []).length : 1;
    const label = total > 1 ? `${total} ${e.type}` : e.v;
    if (label && op > 0.12 && labelling()) {
      const emph = state==='now'||incident;
      const lop = emph?1:Math.min(1,op+.35);
      // A second arrow under the label, saying which way the line runs *where
      // you are already looking*. It used to be angled from one node centre to
      // the other, which an orthogonal path does not follow: on a route that
      // leaves rightwards and turns down, the centre-to-centre angle points
      // diagonally through empty space. It takes the direction of the run the
      // label is actually sitting on.
      //
      // Only on edges carrying a verb — refs get ERD multiplicity markers, and
      // a plain arrow on a crow's foot would be two claims about one line.
      const run = r.label;
      const ang = run.vertical ? (run.dy > 0 ? 90 : -90) : (run.dx > 0 ? 0 : 180);
      // Text stays horizontal whichever way the line runs. A rotated label is a
      // label you tilt your head for, and it is beside a vertical run rather
      // than along it, so there is nothing to align with anyway.
      const off = run.vertical ? {tx: 9, ty: 3, ax: 0, ay: 0}
                               : {tx: 0, ty: -6, ax: 0, ay: 5};
      edges += `<path d="M-5 -3 L4 0 L-5 3 z" fill="${emph?STATE.now:st.label}"
        opacity="${lop}" transform="translate(${lx+off.ax},${ly+off.ay}) rotate(${ang})"/>`;
      edges += `<text x="${lx+off.tx}" y="${ly+off.ty}" class="elabel"
        text-anchor="${run.vertical ? 'start' : 'middle'}"
        fill="${emph?STATE.now:st.label}" opacity="${lop}"
        font-size="${emph?11:9.5}">${esc(label)}</text>`;
    }
  }

  for (const n of GV.graph.nodes) {
    const p=GV.layout[n.id];
    if(!p||!gvVisible(n.id)) continue;
    const k=kindOf(n), sh=SHAPE[k];
    let dim = GV.focus && n.id!==GV.focus &&
      !GV.graph.edges.some(e=>(e.s===GV.focus&&e.t===n.id)||(e.t===GV.focus&&e.s===n.id));
    // In case mode the situation *is* the picture, and it keeps three things
    // apart: who is under test, what they were *given*, and what is being
    // *watched*. An artefact can be given and watched at once, and which it is
    // changes what a failure there means -- a wrong read is a briefing problem,
    // a wrong write is a judgement problem.
    const sit = GV.source==='case' ? GV.caseSituation : null;
    const roles   = new Set(sit?.roles||[]);
    const given   = new Set(sit?.given||[]);
    const scaff   = new Set(sit?.scaffolding||[]);
    const watched = new Set(sit?.watched||[]);
    const touched = new Set();
    if (sit) for (const k of ['reading','writing','required','forbidden'])
      (GV.caseEdges?.[k]||[]).forEach(e=>{touched.add(e[0]); touched.add(e[1]);});
    const inCase = id => roles.has(id)||given.has(id)||scaff.has(id)
                      || watched.has(id)||touched.has(id);
    if (sit) dim = !inCase(n.id);
    // Scaffolding is present and unreachable, and should look it: a ticket
    // needs an item to exist, and Developer cannot read `problem` at all.
    if (sit && scaff.has(n.id) && !watched.has(n.id)) dim = true;

    const ring = sit && roles.has(n.id)    ? LENS.actor
      : sit && watched.has(n.id)           ? LENS.output
      : sit && given.has(n.id)             ? LENS.input
      : sit && scaff.has(n.id)             ? LENS.inert
      : sit && touched.has(n.id)           ? LENS.output
      : claimed[n.id] ? LENS.actor
      : ready.has(n.id) ? LENS.output
      : blast&&blast.has(n.id) ? LENS.input
      : sh.stroke;
    const hot = (sit && (roles.has(n.id)||given.has(n.id)||watched.has(n.id)
                         ||touched.has(n.id)))
      || ready.has(n.id)||claimed[n.id]||(blast&&blast.has(n.id));

    // Key hover selects nodes the same way it selects edges — by kind, or by
    // the state ring they are currently wearing.
    if (GV.keyhl) {
      const sel = keySelects(GV.keyhl);
      // A row that says nothing about nodes leaves them alone rather than
      // hiding them: hovering "untested" is a question about edges.
      dim = sel.nodes ? !sel.nodes.has(n.id) : dim;
    }

    nodes += `<g class="gnode" data-n="${n.id}" opacity="${dim?.2:1}"
      transform="translate(${p.x-sh.w/2},${p.y-sh.h/2})">
      <rect width="${sh.w}" height="${sh.h}" rx="${sh.rx}" fill="${sh.fill}"
        stroke="${ring}" stroke-width="${hot?2.5:1.3}" stroke-dasharray="${sh.dash}"/>
      ${k==='record'||k==='journal'?`<line x1="1" y1="12" x2="${sh.w-1}" y2="12"
        stroke="${sh.stroke}" stroke-width=".9" opacity=".5"/>`:''}
      <text x="${sh.w/2}" y="${sh.h/2+(k==='record'||k==='journal'?4:1)}"
        class="nlabel" fill="${sh.ink}">${esc(n.label)}</text>
      ${vol[n.id]?`<text x="${sh.w-7}" y="9" class="nvol">${vol[n.id]}</text>`:''}
    </g>`;
  }
  return {edges, nodes};
}

// A canvas that fails should say so. Anything thrown between here and setting
// `innerHTML` leaves the SVG exactly as it was -- empty on first draw -- and an
// empty canvas is indistinguishable from a graph with nothing in it, from a
// stale cached script, from a fetch that never resolved. It cost a quarter of
// an hour once, and the information was sitting in a console nobody had open.
function gvDraw() {
  try {
    gvDrawInner();
  } catch (err) {
    console.error('gvDraw', err);
    const svg = document.getElementById('gsvg');
    if (svg) svg.innerHTML = `<text x="24" y="40" fill="#b91c1c"
      style="font:13px ui-monospace,monospace">the graph could not be drawn:
      ${esc(err && err.message)}</text>
      <text x="24" y="62" fill="#64748b" style="font:11px ui-monospace,monospace">
      ${esc(String((err && err.stack || '').split('\n')[1] || '').trim())}</text>
      <text x="24" y="84" fill="#64748b" style="font:11px ui-monospace,monospace">
      a hard reload (ctrl-shift-r) rules out a stale script</text>`;
  }
}

function gvDrawInner() {
  const {edges, nodes} = GV.mode==='chat' ? drawChat() : drawTeam();
  const v=GV.view;
  gvFarNote();                    // the readout tracks zoom, not just the drag
  const R = ESTYLE.refs.c;
  document.getElementById('gsvg').innerHTML = `<defs>
      <!-- One head per edge type, in the edge's own colour, and sized in user
           units rather than stroke widths. markerUnits defaults to strokeWidth,
           so the old single head shrank with the line: on a 1.2px resting edge
           it drew six pixels of grey, under the path's own 0.16 opacity. -->
      ${['writes','reads','messages'].map(t=>`
      <marker id="head-${t}" viewBox="0 0 10 10" refX="8.5" refY="5"
        markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11"
        orient="auto-start-reverse">
        <path d="M0.5 0.5 L10 5 L0.5 9.5 z" fill="${ESTYLE[t].c}"/></marker>`).join('')}
      <marker id="head" viewBox="0 0 10 10" refX="9" refY="5"
        markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11"
        orient="auto-start-reverse">
        <path d="M0 0 L10 5 L0 10 z" fill="${STATE.arrow}"/></marker>
      <marker id="one-e" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="9"
        markerHeight="9" orient="auto">
        <path d="M7 1 L7 11" stroke="${R}" stroke-width="1.6" fill="none"/></marker>
      <marker id="one-s" viewBox="0 0 12 12" refX="1" refY="6" markerWidth="9"
        markerHeight="9" orient="auto">
        <path d="M5 1 L5 11" stroke="${R}" stroke-width="1.6" fill="none"/></marker>
      <marker id="many-e" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="10"
        markerHeight="10" orient="auto">
        <path d="M11 6 L2 1 M11 6 L2 6 M11 6 L2 11" stroke="${R}"
          stroke-width="1.4" fill="none"/></marker>
      <marker id="many-s" viewBox="0 0 12 12" refX="1" refY="6" markerWidth="10"
        markerHeight="10" orient="auto">
        <path d="M1 6 L10 1 M1 6 L10 6 M1 6 L10 11" stroke="${R}"
          stroke-width="1.4" fill="none"/></marker>
      <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
        <circle cx="1" cy="1" r="1" fill="${STATE.grid}"/></pattern>
    </defs>
    <rect width="100%" height="100%" fill="url(#dots)"/>
    <g transform="translate(${v.x},${v.y}) scale(${v.k})">${edges}${nodes}</g>
    ${ghostChips()}`;

  document.querySelectorAll('.ghost').forEach(el=>{
    el.onclick = ev=>{ev.stopPropagation(); gvGoto(el.dataset.ghost);};
    el.onmousedown = ev=>ev.stopPropagation();   // a chip is not the canvas to pan
  });

  document.querySelectorAll('.gnode').forEach(el=>{
    if (el.dataset.msg) { el.onclick = ev=>{ev.stopPropagation(); showMessage(el.dataset.msg);}; return; }
    el.onclick = ev=>{ev.stopPropagation(); if(!GV.dragged) gvFocus(el.dataset.n);};
    el.ondblclick = ev=>{ev.stopPropagation(); gvInhabit(el.dataset.n);};
    el.onmousedown = ev=>{
      if (GV.mode!=='team') return;
      ev.stopPropagation();
      GV.dragNode={id:el.dataset.n, sx:ev.clientX, sy:ev.clientY,
                   ox:GV.layout[el.dataset.n].x, oy:GV.layout[el.dataset.n].y};
      GV.dragged=false;
    };
  });
  document.querySelectorAll('.gedge').forEach(el=>{
    el.onclick = ev=>{ev.stopPropagation(); showEdge(el.dataset.e);};
  });
  gvNarrate();
}

function gvNarrate() {
  const box=document.getElementById('gstatus');
  if (!box) return;
  if (GV.mode==='chat') {
    const m=GV.msgs;
    box.textContent = `${m.messages.length} messages · ${
      Object.keys(m.threads).length} threads · ${m.open.length} open`;
    return;
  }
  if (GV.inhabit) {
    box.innerHTML = `showing only what <b>${esc(GV.inhabit)}</b> can reach ·
      <span class="link" onclick="gvInhabit(null)">release</span>`;
    return;
  }
  if (GV.source==='design') {
    const g=GV.graph;
    box.textContent = `${g.nodes.length} nodes · ${g.edges.length} edges · `
      + `no lens — pick one above, or open a case`;
    return;
  }
  if (GV.source==='coverage') {
    const c=GV.trace.coverage;
    box.textContent = `${c.covered.length}/${c.covered.length+c.missing.length}
      edges covered · red has no test`;
    return;
  }
  const steps=gvSteps();
  box.textContent = steps.length
    ? `step ${GV.stepIx+1}/${steps.length} — narration in the story tab`
    : 'no steps yet';
}

// ---------------------------------------------------------------------------
// Where the arrows go when the arrows leave the screen.
//
// Focusing a node lights its neighbourhood, and then you zoom in far enough to
// read it and the neighbourhood is gone -- edges run off every side to nodes
// you cannot see, and the only way to find out what is out there is to zoom
// back out, which loses the thing you zoomed in for.
//
// So each off-screen neighbour gets a chip on the border where its edge exits,
// carrying the node's own colours, its name, and which way the relationship
// runs. Clicking one focuses that node exactly as clicking the node itself
// would -- and brings it into view, because focusing something off-screen is a
// dead end rather than a navigation.
// ---------------------------------------------------------------------------
const GHOST_INSET = 34;

// Where the line from `from` to `to` leaves the inset rectangle: the smallest
// positive step along the ray that lands on one of its four edges.
//
// Split out from the drawing because it is the only part with arithmetic in it,
// and the drawing needs a DOM to run. A chip placed by a sign error points
// confidently at the wrong side of the screen, which is worse than no chip.
function ghostAnchor(from, to, W, H, m) {
  const dx = to.x - from.x, dy = to.y - from.y;
  if (from.x < 0 || from.x > W || from.y < 0 || from.y > H) return null;
  let t = Infinity;
  if (dx > 0) t = Math.min(t, (W - m - from.x) / dx);
  if (dx < 0) t = Math.min(t, (m - from.x) / dx);
  if (dy > 0) t = Math.min(t, (H - m - from.y) / dy);
  if (dy < 0) t = Math.min(t, (m - from.y) / dy);
  if (!isFinite(t) || t <= 0 || t > 1) return null;
  return {x: from.x + dx * t, y: from.y + dy * t};
}

// Which side of the canvas an anchor landed on. Separation is a one-dimensional
// problem per side, and knowing the side is what makes it one.
function ghostSide(at, W, H, m) {
  const d = [['left', at.x - m], ['right', W - m - at.x],
             ['top', at.y - m], ['bottom', H - m - at.y]];
  return d.sort((a, b) => a[1] - b[1])[0][0];
}

// Rectangles the chips must stay out of: the controls, the key, the settings
// popover when it is open. They sit on top of the canvas, so a chip placed
// underneath one is a chip that does not exist -- and between them they cover
// the top edge and the left edge, which is where chips land most.
function ghostBlockers() {
  const svg = document.getElementById('gsvg');
  if (!svg) return [];
  const base = svg.getBoundingClientRect();
  const out = [];
  // `gprefs` is a child of `gctl` but absolutely positioned, so it hangs below
  // its parent's rectangle and has to be measured on its own.
  for (const id of ['gctl', 'glegend', 'gprefs']) {
    const el = document.getElementById(id);
    if (!el || el.offsetParent === null) continue;     // not laid out: not in the way
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    out.push({x1: r.left - base.left - 8, y1: r.top - base.top - 8,
              x2: r.right - base.left + 8, y2: r.bottom - base.top + 8});
  }
  return out;
}

// Spread chips that landed on the same side until none of them touch.
//
// They cluster because they are placed where their edges exit, and the edges
// leaving one node are not evenly spread -- four artefacts stacked in a column
// all leave through the same short stretch of border. Sorted along the side,
// pushed apart, then pushed back inside it.
function ghostSpread(list, lo, hi, step, axis) {
  list.sort((a, b) => a[axis] - b[axis]);
  for (let i = 1; i < list.length; i++)
    list[i][axis] = Math.max(list[i][axis], list[i - 1][axis] + step);
  const over = list.length ? list[list.length - 1][axis] - hi : 0;
  if (over > 0) for (const c of list) c[axis] -= over;
  for (let i = list.length - 2; i >= 0; i--)
    list[i][axis] = Math.min(list[i][axis], list[i + 1][axis] - step);
  for (const c of list) c[axis] = Math.max(lo, c[axis]);
}

function ghostChips() {
  if (GV.mode !== 'team' || !GV.focus || !GV.layout[GV.focus]) return '';
  const svg = document.getElementById('gsvg');
  const W = svg.clientWidth, H = svg.clientHeight;
  const v = GV.view;
  const screen = p => ({x: p.x * v.k + v.x, y: p.y * v.k + v.y});
  const from = screen(GV.layout[GV.focus]);
  const inside = (p, m) => p.x >= m && p.x <= W - m && p.y >= m && p.y <= H - m;

  // Every distinct neighbour once, carrying the edges that reach it. A node
  // reached three ways is one destination with three lines into it, not three
  // destinations.
  const out = new Map();
  for (const e of GV.graph.edges) {
    const other = e.s === GV.focus ? e.t : (e.t === GV.focus ? e.s : null);
    if (!other || other === GV.focus || !GV.layout[other] || !gvVisible(other)) continue;
    if (!out.has(other)) out.set(other, []);
    out.get(other).push(e);
  }

  // --- place ---------------------------------------------------------------
  const chips = [];
  for (const [id, edges] of out) {
    const p = screen(GV.layout[id]);
    if (inside(p, GHOST_INSET)) continue;              // visible: no stand-in
    const at = ghostAnchor(from, p, W, H, GHOST_INSET);
    if (!at) continue;
    const node = GV.graph.nodes.find(n => n.id === id);
    if (!node) continue;
    const sh = SHAPE[kindOf(node)];
    const name = String(node.label || id);
    const short = name.length > 18 ? name.slice(0, 17) + '…' : name;
    chips.push({id, node, sh, short, edges,
                w: Math.max(56, Math.min(148, 16 + short.length * 6.4)),
                h: 24, x: at.x, y: at.y, side: ghostSide(at, W, H, GHOST_INSET)});
  }

  const blockers = ghostBlockers();
  const clear = c => {
    for (let i = 0; i < 8; i++) {
      const hit = blockers.find(r =>
        c.x - c.w / 2 < r.x2 && c.x + c.w / 2 > r.x1 &&
        c.y - c.h / 2 < r.y2 && c.y + c.h / 2 > r.y1);
      if (!hit) return;
      // Pushed *inward* from the border it is pinned to, which walks it out
      // from under the panel rather than off the canvas.
      if (c.side === 'top')         c.y = hit.y2 + c.h / 2;
      else if (c.side === 'bottom') c.y = hit.y1 - c.h / 2;
      else if (c.side === 'left')   c.x = hit.x2 + c.w / 2;
      else                          c.x = hit.x1 - c.w / 2;
    }
  };
  chips.forEach(clear);

  for (const side of ['top', 'bottom', 'left', 'right']) {
    const mine = chips.filter(c => c.side === side);
    if (mine.length < 2) continue;
    const vertical = side === 'left' || side === 'right';
    const step = vertical ? 30 : Math.max(...mine.map(c => c.w)) + 10;
    ghostSpread(mine, vertical ? 20 : 80, vertical ? H - 20 : W - 80,
                step, vertical ? 'y' : 'x');
  }
  chips.forEach(clear);                        // spreading can walk one back under

  // --- draw ----------------------------------------------------------------
  //
  // Lines first, boxes on top of them, exactly as the canvas proper does it. An
  // arrowhead on its own read as pointing *past* the destination; a line
  // arriving at a box reads as arriving.
  let lines = '', boxes = '';
  for (const c of chips) {
    // Inward, along the axis of the border it is pinned to. It used to aim at
    // the focused node, which put a diagonal stub on a canvas where every other
    // line is axis-aligned -- the chip then read as belonging to a different
    // drawing. Where the destination is is already said by which border it sits
    // on; the stub only has to say that the line continues.
    const [nx, ny] = c.side === 'top'    ? [0, 1]
                   : c.side === 'bottom' ? [0, -1]
                   : c.side === 'left'   ? [1, 0]
                   :                       [-1, 0];
    const px = -ny, py = nx;                          // and its perpendicular

    // One line per relationship, in its own colour and dash, spread across the
    // chip's inward face: the same grammar as the canvas, at a smaller size.
    const kinds = [...new Map(c.edges.map(e =>
      [`${e.type}|${e.s === GV.focus}`, e])).values()];
    kinds.forEach((e, i) => {
      const st = ESTYLE[e.type];
      const off = (i - (kinds.length - 1) / 2) * 6;
      const edge = 0.5 * (Math.abs(nx) * c.w + Math.abs(ny) * c.h) + 1;
      const ax = c.x + nx * edge + px * off, ay = c.y + ny * edge + py * off;
      const bx = c.x + nx * (edge + 34) + px * off;
      const by = c.y + ny * (edge + 34) + py * off;
      // Outbound from the focus arrives *at* the chip, so the head goes on the
      // chip end. Inbound points the other way, back to the node you are
      // standing on. Direction is carried by the arrow, as it is everywhere.
      const head = e.s === GV.focus ? 'marker-end' : 'marker-start';
      lines += `<path d="M${bx} ${by} L${ax} ${ay}" fill="none"
        stroke="${st.c}" stroke-width="1.8" stroke-dasharray="${st.dash}"
        ${st.head ? `${head}="url(#head-${e.type})"` : ''} opacity=".85"/>`;
    });

    boxes += `<g class="ghost" data-ghost="${esc(c.id)}"
        transform="translate(${c.x},${c.y})">
      <rect x="${-c.w / 2}" y="${-c.h / 2}" width="${c.w}" height="${c.h}"
        rx="${c.sh.rx}" fill="${c.sh.fill}" stroke="${c.sh.stroke}"
        stroke-width="1.6" stroke-dasharray="${c.sh.dash}"/>
      <text x="0" y="4" text-anchor="middle" class="glabel"
        fill="${c.sh.ink}">${esc(c.short)}</text>
    </g>`;
  }
  return lines + boxes;
}

// Focus, and put it where it can be seen. Focusing alone is what clicking the
// real node does, but a chip only exists because its node is off-screen.
function gvGoto(id) {
  const p = GV.layout[id];
  const svg = document.getElementById('gsvg');
  if (p && svg) {
    GV.view.x = svg.clientWidth / 2 - p.x * GV.view.k;
    GV.view.y = svg.clientHeight / 2 - p.y * GV.view.k;
  }
  GV.focus = id;                       // set, never toggled: you came here to arrive
  gvDraw();
  showNode(id);
}

function gvFocus(id){GV.focus = GV.focus===id?null:id; gvDraw(); if(GV.focus) showNode(id);}
function gvInhabit(id){GV.inhabit = GV.inhabit===id?null:id; GV.focus=null; gvDraw();
  if(GV.inhabit) showNode(id);}
function gvMode(m){GV.mode=m; GV.focus=null; GV.inhabit=null; gvFit(); gvDraw();
  document.querySelectorAll('[data-gmode]').forEach(b=>
    b.classList.toggle('on', b.dataset.gmode===m));}

function gvFit(){
  const pts = GV.mode==='chat' ? Object.values(chatLayout()) : Object.values(GV.layout);
  if (!pts.length) return;
  const xs=pts.map(p=>p.x), ys=pts.map(p=>p.y), stage=document.getElementById('gstage');
  const w=Math.max(...xs)-Math.min(...xs)+340, h=Math.max(...ys)-Math.min(...ys)+220;
  const k=Math.min(stage.clientWidth/w, stage.clientHeight/h, 1.15);
  GV.view={k, x:(stage.clientWidth-w*k)/2-(Math.min(...xs)-170)*k,
           y:(stage.clientHeight-h*k)/2-(Math.min(...ys)-110)*k};
}

async function saveLayout(){
  if (!GV.dirty) return;
  await fetch('/layout.json', {method:'POST', body:JSON.stringify(GV.layout, null, 2)});
  GV.dirty=false;
  // Into `gstatus`, the toolbar's status slot. It used to write to `gsaved`,
  // an element that does not exist and never did — so the save worked and the
  // confirmation went nowhere, silently, every time. Found by the check that
  // every id a script writes to is an id something creates.
  const box=document.getElementById('gstatus');
  if (!box) return;
  box.textContent='layout saved';
  setTimeout(gvNarrate, 1600);
}

function gvControls(){
  // Actions and status only. Everything about *stepping* moved to the story
  // subtab, which is where the steps themselves live — a control separated from
  // the thing it controls is how a toolbar stops making sense.
  document.getElementById('gctl').innerHTML=`
    <button data-gmode="team" class="on" onclick="gvMode('team')">team</button>
    <button data-gmode="chat" onclick="gvMode('chat')">chat</button>
    <span class="sep"></span>
    <select id="gsrc"><option value="design">the design</option>
      <option value="coverage">coverage</option>
      <option value="story">design stories</option>
      <option value="run">this run</option></select>
    <span class="sep"></span>
    <button id="gfit">fit</button><button id="gsave">save layout</button>
    <span class="sep"></span>
    <button id="gcog" title="display settings">&#9881;</button>
    <span class="sig" id="gstatus"></span>
    <div id="gprefs" class="pop"></div>`;

  gsrc.onchange=e=>{GV.source=e.target.value; GV.stepIx=0; gvLegend(); gvMode('team');
    showTab('story'); syncStoryTab();};
  gfit.onclick=()=>{gvFit(); gvDraw();};
  gsave.onclick=saveLayout;

  const prefs = document.getElementById('gprefs');
  const choice = (key, value, label, why) =>
    `<button class="${GV.settings[key]===value?'on':''}"
       onclick="gvSet('${key}','${value}')" title="${why}">${label}</button>`;
  prefs.innerHTML = `
    <h4>parallel edges</h4>
    <div class="prow"><span>
      ${choice('collapse','auto','when far out',
               'fold below the zoom where labels stop being readable')}
      ${choice('collapse','always','always','one line per relationship, always')}
      ${choice('collapse','never','never','every verb its own line')}
    </span>
    <span class="slide">
      <input type="range" id="gfar" min="0.2" max="1.6" step="0.02"
             value="${far()}" oninput="gvFar(this.value)"
             ${GV.settings.collapse === 'auto' ? '' : 'disabled'}
             title="the zoom below which parallel edges fold together">
      <span class="now" id="gfarnow"></span>
    </span></div>
    <p class="sig" id="gfarnote"></p>
    <p class="sig">Folded per source, target and *type* — never across types.
      Seventeen pairs here carry both a read and a write, and one line for two
      kinds of relationship is the one thing the colours must not say.</p>
    <h4>edge labels</h4>
    <div class="prow"><span>
      ${choice('labels','auto','when readable','hide below the same zoom')}
      ${choice('labels','always','always','keep them at every zoom')}
      ${choice('labels','never','never','structure only')}
    </span></div>`;
  document.getElementById('gcog').onclick = (e) => {
    e.stopPropagation();
    prefs.classList.toggle('on');
  };
  prefs.onclick = (e) => e.stopPropagation();
  document.addEventListener('click', () => prefs.classList.remove('on'));

  const svg=document.getElementById('gsvg');
  svg.onclick=()=>{if(!GV.dragged){GV.focus=null; gvDraw();}};
  let pan=null;
  svg.onmousedown=e=>{pan={x:e.clientX,y:e.clientY,vx:GV.view.x,vy:GV.view.y}; GV.dragged=false;};
  window.addEventListener('mousemove',e=>{
    if (GV.dragNode) {
      const d=GV.dragNode;
      GV.layout[d.id]={x:d.ox+(e.clientX-d.sx)/GV.view.k, y:d.oy+(e.clientY-d.sy)/GV.view.k};
      GV.dirty=true; GV.dragged=true; gvDraw(); return;
    }
    if (pan){GV.view.x=pan.vx+(e.clientX-pan.x); GV.view.y=pan.vy+(e.clientY-pan.y);
      if(Math.abs(e.clientX-pan.x)>3) GV.dragged=true; gvDraw();}
  });
  window.addEventListener('mouseup',()=>{pan=null; GV.dragNode=null;
    setTimeout(()=>{GV.dragged=false;},50);});
  // Zoom about the cursor: the point under the pointer stays put, which is what
  // every map does and what the hand expects. Scaling about the origin makes the
  // thing you were looking at slide away, so you chase it with the pan.
  svg.addEventListener('wheel', e => {
    e.preventDefault();
    const r = svg.getBoundingClientRect();
    const mx = e.clientX - r.left, my = e.clientY - r.top;
    const f = e.deltaY < 0 ? 1.12 : 0.89;
    const k2 = Math.min(4, Math.max(0.15, GV.view.k * f));
    const scale = k2 / GV.view.k;
    GV.view.x = mx - (mx - GV.view.x) * scale;
    GV.view.y = my - (my - GV.view.y) * scale;
    GV.view.k = k2;
    gvDraw();
  }, {passive:false});
}

// Every key row: how to draw it, what it *is*, and what it selects when hovered.
//
// The third field is the point. A key that only names things tells you which
// colour is which; this one also answers "what is a journal", which is the
// question someone actually has, and it lights the matching elements so the
// answer is in the picture rather than in the sentence.
const LEGEND = [
  ["edges", [
    ["writes",   {edge:"writes"},   "who may change this artefact. Exactly one role per row — that is law 1"],
    ["reads",    {edge:"reads"},    "what a role may look at, and how much of it: every edge declares rows and depth"],
    ["messages", {edge:"messages"}, "who may speak to whom. Derived from the read/write structure, never designed"],
    ["refs",     {edge:"refs"},     "what points at what. The cascade walks these, so they are the blast path of any change"],
  ]],
  ["nodes", [
    ["principal", {kind:"principal"}, "the person who wants it and rules on it. Not a role — nothing wakes them"],
    ["role",      {kind:"role"},      "woken by one message, acts, ends. No memory of having been woken before"],
    ["record",    {kind:"record"},    "state with one writer per row. Amending one revokes what depended on it"],
    ["journal",   {kind:"journal"},   "append-only, many writers, one author per entry. Nothing is ever edited"],
    ["derived",   {kind:"derived"},   "computed from the rest. No role writes it, so it carries no judgement"],
  ]],
  ["right now", [
    ["mid-session",   {ring:"live"},  "holding a claim. Roles are single-instance, so nothing else can wake it. Violet is ‘this is acting’ in every lens"],
    ["ready to wake", {ring:"ready"}, "a predicate is firing for this role right now. Amber is ‘what comes out’ in every lens"],
    ["cascade reach", {ring:"blast"}, "what a change to the selected artefact would wake, following refs. Cyan is ‘what goes in’ in every lens"],
  ]],
];

// Shown only with a case open, because the three states mean nothing without
// one — and with one open they are the whole picture.
const CASE_LEGEND = ["this case", [
  ["role under test", {group:"roles"},       "who this case wakes. A chain case wakes two, and the same violet means ‘this is acting’ in every lens"],
  ["given",           {group:"given"},       "seeded by the fixture and reachable from the role. What it was handed before it acted"],
  ["watched",         {group:"watched"},     "the case asserts on writes here. A wrong read is a briefing problem; a wrong write is a judgement one"],
  ["forbidden",       {group:"forbidden"},   "the case fails if this happens. Halo, not recolour — a forbidden read is still a read"],
  ["scaffolding",     {group:"scaffolding"}, "seeded because the schema demands it — a ticket needs an item — and unreachable from this role. Present, not given"],
]];

// Which nodes and edges a case-key row is about. One place, so the key and the
// picture cannot disagree about what "given" means.
// Which swatch a case-key row wears. Named here rather than inline so the key
// and `LENS` cannot drift: both answer "what colour is `given`" from one place.
const GROUP_RING = {
  roles: 'live', given: 'blast', watched: 'now',
  forbidden: 'denied', scaffolding: 'gap',
};


// What a key row selects, whatever kind of row it is.
//
// One resolver, because the alternative kept costing the same bug. The node
// loop tested `ring` against live state and the edge loop tested `edge`
// against type, so every row using neither -- the five case rows, then the two
// coverage rows -- matched nothing and dimmed the whole picture. Adding a
// branch per row-set fixed it twice and would have gone on failing for the
// next lens.
//
// Returns the nodes to keep lit and a predicate over edges. Either may be
// null, meaning "this row says nothing about those".
// How the folded view draws: one line per relationship, and as few of them as
// the structure allows.
//
// Three reductions, in order. Parallel edges of one type between one pair
// become a line. Two lines of the same type running opposite ways become one
// line with a head at each end -- ten pairs here, all of them messages, and
// "these two talk to each other" is what the picture was trying to say with
// two arcs. What is left is a straight line whenever a pair has only one,
// which is seventy-four of ninety-one: bowing those would be decoration
// standing where a fact was.
function foldPlan() {
  const groups = {};
  for (const e of GV.graph.edges) {
    const k = `${e.s}|${e.t}|${e.type}`;
    (groups[k] = groups[k] || []).push(e);
  }

  const plan = {}, byPair = {};
  for (const k of Object.keys(groups)) {
    const [src, dst, type] = k.split('|');
    const rev = `${dst}|${src}|${type}`;
    // Keep one of the two directions and let it carry both. Which one is
    // arbitrary but must be stable, so it is the alphabetically first.
    if (groups[rev] && dst < src) { plan[k] = {skip: true}; continue; }

    const pair = [src, dst].sort().join('|');
    (byPair[pair] = byPair[pair] || []).push(k);
    plan[k] = {members: groups[k], back: groups[rev] || [],
               bidir: !!groups[rev], skip: false};
  }
  for (const keys of Object.values(byPair))
    keys.forEach((k, i) => { plan[k].rank = i; plan[k].solo = keys.length === 1; });
  return plan;
}


function keySelects(sel) {
  const none = {nodes: null, edges: null};
  if (!sel) return none;

  if (sel.kind) return {
    nodes: new Set(GV.graph.nodes.filter(n => kindOf(n) === sel.kind).map(n => n.id)),
    edges: null,
  };
  if (sel.edge) return {nodes: null, edges: e => e.type === sel.edge};

  if (sel.group) {
    const g = caseGroup(sel.group);
    const list = g.edges ? (GV.caseEdges ? GV.caseEdges[g.edges] || [] : []) : [];
    const keys = new Set(list.map(x => ek(x) + '|' + (x[3] || '')));
    return {nodes: g.nodes,
            edges: g.edges ? (e => keys.has(ek([e.s, e.t, e.type]) + '|' + (e.v || '')))
                           : null};
  }

  if (sel.lens) {
    const cov = (GV.trace && GV.trace.coverage) || {};
    const keys = new Set((cov[sel.lens] || []).map(ek));
    return {nodes: null, edges: e => keys.has(ek([e.s, e.t, e.type]))};
  }

  if (sel.ring) {
    const overlay = (GV.trace && GV.trace.overlay) || {};
    const ready = new Set((overlay.ready || []).map(w => w.role));
    const claimed = overlay.claimed || {};
    const blast = GV.blast ? new Set(GV.blast.artefacts) : null;
    const pick = sel.ring === 'ready' ? id => ready.has(id)
               : sel.ring === 'live'  ? id => !!claimed[id]
               : sel.ring === 'blast' ? id => !!(blast && blast.has(id))
               : () => false;
    return {nodes: new Set(GV.graph.nodes.map(n => n.id).filter(pick)), edges: null};
  }
  return none;
}


function caseGroup(name) {
  const sit = GV.caseSituation || {}, ce = GV.caseEdges || {};
  const ends = k => new Set((ce[k]||[]).flatMap(e=>[e[0], e[1]]));
  switch (name) {
    case 'roles':       return {nodes:new Set(sit.roles||[]),        edges:null};
    case 'given':       return {nodes:new Set(sit.given||[]),        edges:'reading'};
    case 'watched':     return {nodes:new Set(sit.watched||[]),      edges:'writing'};
    case 'scaffolding': return {nodes:new Set(sit.scaffolding||[]),  edges:null};
    case 'forbidden':   return {nodes:ends('forbidden'),             edges:'forbidden'};
    default:            return {nodes:new Set(),                     edges:null};
  }
}

// Per-lens key groups, reachable outside `gvLegend` so a check can walk every
// row and assert it selects something.
function LENS_KEY_FOR(src) { return (LENS_KEY_FOR.all || {})[src]; }

function gvLegend() {
  const swatch = (c,dash) => `<svg width="30" height="8">
    <line x1="1" y1="4" x2="21" y2="4" stroke="${c}" stroke-width="2"
      stroke-dasharray="${dash}"/>
    <path d="M20 1 L27 4 L20 7 z" fill="${c}"/></svg>`;
  const box = (fill,stroke,dash) => `<svg width="16" height="11"><rect x="1" y="1"
    width="14" height="9" rx="2" fill="${fill}" stroke="${stroke}"
    stroke-dasharray="${dash}"/></svg>`;

  const mark = {
    writes:   swatch(ESTYLE.writes.c,''),
    reads:    swatch(ESTYLE.reads.c,'5 3'),
    messages: swatch(ESTYLE.messages.c,''),
    refs:     `<svg width="30" height="8"><line x1="1" y1="4" x2="21" y2="4"
                 stroke="${ESTYLE.refs.c}" stroke-width="2"/>
               <path d="M28 4 L21 1 M28 4 L21 4 M28 4 L21 7" stroke="${ESTYLE.refs.c}"
                 stroke-width="1.3" fill="none"/></svg>`,
    principal: box(SHAPE.principal.fill,SHAPE.principal.stroke,''),
    role:      box(SHAPE.role.fill,SHAPE.role.stroke,''),
    record:    box(SHAPE.record.fill,SHAPE.record.stroke,''),
    journal:   box(SHAPE.journal.fill,SHAPE.journal.stroke,'4 3'),
    derived:   box(SHAPE.derived.fill,SHAPE.derived.stroke,'2 4'),
    ready: `<i class="ring" style="border-color:${LENS.output}"></i>`,
    live:  `<i class="ring" style="border-color:${LENS.actor}"></i>`,
    blast: `<i class="ring" style="border-color:${LENS.input}"></i>`,
    now:   `<i class="ring" style="border-color:${LENS.output}"></i>`,
    gap:   `<i class="ring" style="border-color:${LENS.inert}"></i>`,
    denied:`<i class="ring" style="border-color:${LENS.denied}"></i>`,
    proven:`<i class="ring" style="border-color:${LENS.proven}"></i>`,
  };

  const LENS_KEY = LENS_KEY_FOR.all = {
    coverage: ["coverage", [
      ["exercised", {lens:"covered", ring:"proven"}, "some test drives this edge. Drawing an edge creates the obligation, so this cannot drift from the design"],
      ["untested",  {lens:"missing", ring:"denied"}, "no test touches it. A capability nothing exercises is a claim nobody has checked"],
    ]],
    story: ["this story", [
      ["current step", {ring:"ready"}, "the edge this step of the story uses"],
      ["so far",       {ring:"blast"}, "everything the story has used up to here"],
    ]],
    run: ["this run", [
      ["current step", {ring:"ready"}, "the edge the selected session used"],
      ["so far",       {ring:"blast"}, "everything the run has done up to here"],
    ]],
    case: CASE_LEGEND,
  };
  // "Right now" is live database state -- claims and firing predicates -- not
  // a lens. It is drawn under every lens *except* case, where the ring is
  // overridden by what the case says. So it belongs in the key when those
  // rings can actually appear and something is actually wearing one; an idle
  // database with three unexplained rows in the key is three rows of noise.
  const overlay = GV.trace?.overlay || {};
  const anythingLive = (overlay.ready||[]).length
                       || Object.keys(overlay.claimed||{}).length || GV.blast;
  const base = LEGEND.filter(([name]) =>
    name !== 'right now' || (GV.source !== 'case' && anythingLive));

  const extra = LENS_KEY[GV.source];
  const groups = extra ? [...base, extra] : base;

  // A row whose swatch does not resolve renders the string "undefined" beside
  // its label, which is what happened the moment case rows started selecting
  // by `group` while the lookup still only knew `edge`, `kind` and `ring`.
  for (const [, items] of [...LEGEND, CASE_LEGEND, ...Object.values(LENS_KEY)])
    for (const [label, sel] of items)
      if (!mark[sel.edge || sel.kind || sel.ring || GROUP_RING[sel.group]])
        console.error('legend row has no swatch:', label, sel);

  const el = document.getElementById('glegend');
  el.innerHTML =
    `<div style="display:flex;gap:16px">` +
    groups.map(([group, items]) => `<div class="lgrp"><b>${group}</b>` +
      items.map(([label, sel, why], i) => {
        // Case rows select by `group`, not by `ring` -- the swatch has to
        // follow, or the row renders the string "undefined" beside its label.
        const glyph = mark[sel.edge || sel.kind || sel.ring
                           || GROUP_RING[sel.group]];
        return `<span class="lkey" data-sel='${JSON.stringify(sel)}'
          data-why="${esc(why)}">${glyph} ${esc(label)}</span>`;
      }).join('') + `</div>`).join('') +
    `</div><div id="lwhat"></div>`;

  const what = document.getElementById('lwhat');
  for (const row of el.querySelectorAll('.lkey')) {
    row.addEventListener('mouseenter', () => {
      what.textContent = row.dataset.why;
      GV.keyhl = JSON.parse(row.dataset.sel);
      gvDraw();
    });
  }
  // One leave handler on the whole key rather than one per row: moving between
  // adjacent rows fires leave-then-enter, and per-row clearing made the
  // highlight flicker off between them.
  el.addEventListener('mouseleave', () => {
    what.textContent = ''; GV.keyhl = null; gvDraw();
  });
}

document.addEventListener('DOMContentLoaded', () => gvLoad().then(gvLegend));
