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

// One object owns every piece of graph state, and each piece has one writer:
// the lens changes only through `setLens`, the mode only through `gvMode`, the
// layout only through `applyLayout`. The tabs used to feel "overlapping"
// because four call sites each set `source` directly and each remembered a
// different subset of the cleanup — the case option stayed in the dropdown,
// the cascade overlay outlived the panel that explained it, and picking any
// lens threw you onto the story subtab whether or not it applied.
const GV = {graph:null, layout:null, stories:null, trace:null, msgs:null,
            mode:'team', source:'design', storyIx:0, stepIx:0,
            focus:null, inhabit:null, blast:null, keyhl:null, edgeSel:null,
            caseId:null, caseEdges:null, caseSituation:null,
            layouts:['main'], wired:false,
            view:{x:0,y:0,k:1}, dragNode:null, dirty:false,
            settings:{collapse:'auto', labels:'auto', far:0.62, layout:'main'}};

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
  role:    {w:152, h:50, rx:6,  fill:'#ffffff', stroke:'#3b6ea5', dash:'', ink:'#132a44'},
  record:  {w:152, h:42, rx:4,  fill:'#e4f3e8', stroke:'#2f855a', dash:'', ink:'#14532d'},
  journal: {w:152, h:42, rx:4,  fill:'#eef7f0', stroke:'#4b9e74', dash:'4 3', ink:'#166534'},
  derived: {w:152, h:42, rx:4,  fill:'#f1f5f2', stroke:'#94a3a0', dash:'2 4', ink:'#475569'},
};

// Reference edges route as orthogonal segments, ported from the design viewer.
// A bezier between two artefacts reads as "these are related somehow"; an elbow
// that visibly avoids the boxes in between reads as a *structural* relation,
// which is what a ref is. Channels are chosen so no segment crosses another
// artefact — the same reason the original did it rather than using taxi routing,
// which cannot avoid obstacles.
function refPath(e) {
  const W = SHAPE.record.w, H = SHAPE.record.h, M = 18;
  const boxes = GV.graph.nodes
    .filter(n => n.type === 'artefact' && GV.layout[n.id])
    .map(n => ({id:n.id, x1:GV.layout[n.id].x-W/2-M, x2:GV.layout[n.id].x+W/2+M,
                y1:GV.layout[n.id].y-H/2-M, y2:GV.layout[n.id].y+H/2+M}));
  const hitV=(x,ya,yb,skip)=>boxes.some(b=>!skip.includes(b.id)&&
    x>b.x1&&x<b.x2&&Math.max(ya,yb)>b.y1&&Math.min(ya,yb)<b.y2);
  const hitH=(y,xa,xb,skip)=>boxes.some(b=>!skip.includes(b.id)&&
    y>b.y1&&y<b.y2&&Math.max(xa,xb)>b.x1&&Math.min(xa,xb)<b.x2);

  const s0=GV.layout[e.s], t0=GV.layout[e.t];
  if (!s0||!t0) return null;
  const skip=[e.s,e.t], cand=[];
  const mids=a=>a.slice(1).map((v,i)=>(v+a[i])/2);
  const colCh=mids([...new Set(boxes.map(b=>(b.x1+b.x2)/2))].sort((a,b)=>a-b));
  const rowCh=mids([...new Set(boxes.map(b=>(b.y1+b.y2)/2))].sort((a,b)=>a-b));

  [...colCh,(s0.x+t0.x)/2].forEach(xm=>{
    if (xm<=Math.min(s0.x,t0.x)+10||xm>=Math.max(s0.x,t0.x)-10) return;
    cand.push({o:'h', ch:xm, pref:Math.abs(xm-(s0.x+t0.x)/2),
      cost:(hitH(s0.y,s0.x,xm,skip)?1:0)+(hitV(xm,s0.y,t0.y,skip)?1:0)+(hitH(t0.y,xm,t0.x,skip)?1:0)});
  });
  [...rowCh,(s0.y+t0.y)/2].forEach(ym=>{
    if (ym<=Math.min(s0.y,t0.y)+10||ym>=Math.max(s0.y,t0.y)-10) return;
    cand.push({o:'v', ch:ym, pref:Math.abs(ym-(s0.y+t0.y)/2)+5,
      cost:(hitV(s0.x,s0.y,ym,skip)?1:0)+(hitH(ym,s0.x,t0.x,skip)?1:0)+(hitV(t0.x,ym,t0.y,skip)?1:0)});
  });
  if (Math.abs(s0.y-t0.y)<6) cand.push({o:'s',ch:0,pref:-1,cost:hitH(s0.y,s0.x,t0.x,skip)?1:0});
  if (Math.abs(s0.x-t0.x)<6) cand.push({o:'sv',ch:0,pref:-1,cost:hitV(s0.x,s0.y,t0.y,skip)?1:0});
  cand.sort((a,b)=>a.cost-b.cost||a.pref-b.pref);
  const best=cand[0]||{o:'h',ch:(s0.x+t0.x)/2};

  const horiz = best.o==='h'||best.o==='s';
  const sf = horiz ? (t0.x>s0.x?'right':'left') : (t0.y>s0.y?'bottom':'top');
  const tf = horiz ? (t0.x>s0.x?'left':'right')  : (t0.y>s0.y?'top':'bottom');
  const off = GV.refOffset[`${e.s}|${e.t}|${e.v}`] || 0;
  // Each node's *own* box, not the widest one. `W`/`H` are the record shape,
  // and a role is 152x50 against that 152x42 -- so every arrow into a role
  // landed ten pixels inside it and every vertical one stopped four short.
  // At full opacity the head is simply hidden by the fill, which reads as an
  // edge with no direction.
  const anchor=(n,face)=>{
    const p=GV.layout[n];
    const node=GV.graph.nodes.find(x=>x.id===n);
    const sh=SHAPE[node?kindOf(node):'record']||SHAPE.record;
    return face==='left' ?{x:p.x-sh.w/2, y:p.y+off}
         : face==='right'?{x:p.x+sh.w/2, y:p.y+off}
         : face==='top'  ?{x:p.x+off, y:p.y-sh.h/2}
         :                {x:p.x+off, y:p.y+sh.h/2};
  };
  const A=anchor(e.s,sf), B=anchor(e.t,tf);
  const pts = best.o==='h' ? [A,{x:best.ch,y:A.y},{x:best.ch,y:B.y},B]
            : best.o==='v' ? [A,{x:A.x,y:best.ch},{x:B.x,y:best.ch},B]
            : [A,B];
  // Multiplicity, read off the cardinality: crow's foot for many, bar for one.
  // A ref without it says two things are related; with it, it says how.
  const [sc, tc] = (e.card || 'n:1').split(':');
  return {d:'M'+pts.map(p=>`${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' L'),
          mid:pts[Math.floor(pts.length/2)],
          startMarker: sc.trim()==='1' ? 'one-s' : 'many-s',
          endMarker:   tc.trim()==='1' ? 'one-e' : 'many-e'};
}

// A multigraph draws several edges between the same pair. Without spreading
// them they land on one path and only the last is visible — the picture then
// silently claims a single relationship where there are three.
// One slotting pass over *every* edge between a pair, whatever its type and
// whichever way it points. Slotting per type only moved the collision: a write
// and a read between the same two nodes still landed on the same curve, and a
// b->a edge mirrored onto its a->b twin.
//
// The fix is a canonical side. Every offset is measured against the sorted pair,
// so direction no longer decides which side of the line an edge sits on — the
// slot does.
function computeSpread() {
  const pairs = {}, refs = {};
  for (const e of GV.graph.edges) {
    if (e.type === 'refs') {
      const rk = [e.s, e.t].sort().join('|');
      (refs[rk] = refs[rk] || []).push(e);
      continue;
    }
    // Ordered, not sorted: rank is a position within the edges running the
    // *same way*, because the two directions bow to opposite sides and never
    // need to avoid each other.
    const k = `${e.s}|${e.t}`;
    (pairs[k] = pairs[k] || []).push(e);
  }

  GV.spread = {};
  GV.spreadN = {};
  const ORDER = {writes: 0, reads: 1, messages: 2};
  for (const [k, list] of Object.entries(pairs)) {
    list.sort((a, b) =>
      (ORDER[a.type] ?? 9) - (ORDER[b.type] ?? 9) ||
      (a.v || '').localeCompare(b.v || ''));
    // Rank within the pair, not a signed offset. Which *side* a line bows to
    // is decided at draw time by which way it runs, so direction is readable
    // from position: everything left-to-right rides above the line between the
    // boxes, everything right-to-left below it. Rank only says how far out.
    list.forEach((e, i) => {
      GV.spread[`${e.s}|${e.t}|${e.type}|${e.v}`] = i;
      GV.spreadN[`${e.s}|${e.t}|${e.type}|${e.v}`] = list.length;
    });
  }

  GV.refOffset = {};
  for (const [k, list] of Object.entries(refs)) {
    list.forEach((e, i) => {
      GV.refOffset[`${e.s}|${e.t}|${e.v}`] =
        list.length === 1 ? 0 : (i - (list.length - 1) / 2) * 14;
    });
  }
}

async function gvLoad() {
  const [g,l,st,tr,ms,ly] = await Promise.all([
    fetch('/graph.json').then(r=>r.json()),
    fetch('/layout.json').then(r=>r.json()),
    fetch('/stories.json').then(r=>r.json()),
    fetch('/trace.json').then(r=>r.json()),
    fetch('/messages.json').then(r=>r.json()),
    // Older server, same page: a viewer that refuses to draw because a listing
    // endpoint is missing has made the new feature a regression. `null` marks
    // the server as predating named layouts, and saving under a name is then
    // refused outright — the old POST handler ignores the name and would
    // quietly overwrite main with whatever was on screen.
    fetch('/layouts.json').then(r=>r.ok?r.json():null).catch(()=>null),
  ]);
  GV.graph=g; GV.layout=l; GV.stories=st; GV.trace=tr; GV.msgs=ms;
  GV.layoutApi = !!ly;
  GV.layouts = (ly && ly.names && ly.names.length) ? ly.names : ['main'];

  // The layout you were on survives the fingerprint reload, like the tab does.
  // A generated one is regenerated; a saved one is fetched; a name that no
  // longer exists falls back to main rather than to a blank canvas.
  const want = GV.settings.layout || 'main';
  if (AUTO_LAYOUTS[want]) GV.layout = AUTO_LAYOUTS[want]();
  else if (want !== 'main') {
    if (GV.layouts.includes(want)) {
      try { GV.layout = await (await fetch(
        `/layout.json?name=${encodeURIComponent(want)}`)).json(); }
      catch { GV.settings.layout = 'main'; }
    } else GV.settings.layout = 'main';
  }
  GV.layout = placeStrays(GV.layout);
  computeSpread(); gvControls(); gvWireStage(); gvFit(); gvDraw(); buildStoryTab();
  // The address bar names a view; honoured only once everything it can name
  // (graph, layout, cases) is loadable.
  if (typeof applyHash === 'function') applyHash();
}

const gvSteps = () =>
  GV.source==='story' ? (GV.stories[GV.storyIx]?.steps||[])
: GV.source==='run'   ? (GV.trace.steps||[]) : [];

function gvLit() {
  const lit=new Map();
  // The default lens makes no claim. Opening on coverage meant the first thing
  // anybody saw was a picture half-painted red about a question they had not
  // asked yet — the structure, which is what the graph is *for*, was the one
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

  // Which neighbours have left the screen. Their edges are not drawn at all --
  // a line heading off the canvas tells you a relationship exists and then
  // abandons you, and at the zoom where that happens there are a dozen of them
  // fanning out to nowhere. Each becomes a short local edge to a stand-in at
  // the border instead, drawn by `ghostChips`.
  const away = offscreenNeighbours();

  for (const e of GV.graph.edges) {
    const a=GV.layout[e.s], b=GV.layout[e.t];
    if(!a||!b||!gvVisible(e.s)||!gvVisible(e.t)) continue;
    if (away.has(e.s) || away.has(e.t)) continue;
    const group = groupOf(e);
    const p = fold ? plan[group] : null;
    if (fold) {
      if (p.skip) continue;             // its opposite carries both directions
      if (drawn.has(group)) continue;   // one line stands for the whole group
      drawn.add(group);
    }
    const kin = fold ? p.members : [e];

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
    // A selected edge is the whole subject: it and its two ends at full
    // light, everything else near-gone.
    if (GV.edgeSel) {
      const hit = e.s===GV.edgeSel.s && e.t===GV.edgeSel.t
                  && e.type===GV.edgeSel.type;
      op = hit ? 1 : 0.04;
      if (hit) w = Math.max(w, 2.2);
    }

    // Hovering the key selects rather than annotates: everything else recedes,
    // so "what is a journal" is answered by the picture instead of by the
    // sentence underneath it.
    if (GV.keyhl) {
      const sel = keySelects(GV.keyhl);
      if (sel.edges) op = sel.edges(e) ? Math.max(op, .95) : 0.05;
      else if (sel.nodes) op = (sel.nodes.has(e.s) || sel.nodes.has(e.t))
                             ? Math.max(op, .6) : 0.05;
    }

    let d, lx, ly;
    let markers = '';
    if (e.type === 'refs') {
      const r = refPath(e);
      if (!r) continue;
      d = r.d; lx = r.mid.x; ly = r.mid.y;
      markers = `marker-start="url(#${r.startMarker})" marker-end="url(#${r.endMarker})"`;
    } else {
      // Spread parallel edges so a multigraph does not collapse onto one path.
      const key = `${e.s}|${e.t}|${e.type}|${e.v}`;
      const rank = fold ? p.rank : (GV.spread[key] || 0);
      const n = fold ? (p.solo ? 1 : 2) : (GV.spreadN[key] || 1);
      const mx=(a.x+b.x)/2, my=(a.y+b.y)/2, dx=b.x-a.x, dy=b.y-a.y;
      const len=Math.hypot(dx,dy)||1;
      // Always bow to the left of the direction of travel.
      //
      // The offset added below is `(-dy, dx) * bow / len`. For an edge running
      // rightwards that is `(0, +1)` -- *downwards*, since y grows down the
      // screen -- so a positive bow put every left-to-right edge under the line
      // between its boxes and every right-to-left edge over it, which is the
      // opposite of what it should be. One negative sign fixes both directions
      // at once and gives a consistent rotation for vertical edges too.
      // A pair reduced to a single line has nothing to avoid, so it runs
      // straight. Bowing it would be decoration standing where a fact was.
      const bow = (fold && p.solo) ? 0 : -(Math.min(34, len*.11) + rank * 30);
      const cx=mx-(dy/len)*bow, cy=my+(dx/len)*bow;

      // Start and end on the boxes, not in them. This drew centre to centre,
      // so every arrowhead sat under the node's own fill -- an edge with no
      // visible direction, for every read, write and message in the picture.
      // (`refs` edges route through `refPath` and were always anchored; that
      // is why fixing the anchor there changed nothing anybody could see.)
      // A quadratic leaves A towards its control point and arrives at B from
      // it, so those are the directions to clip along.
      const A = onBox(e.s, cx-a.x, cy-a.y);
      const B = onBox(e.t, cx-b.x, cy-b.y);
      d = `M${A.x} ${A.y} Q${cx} ${cy} ${B.x} ${B.y}`;

      // Slide each parallel edge's label to a different point *along* its
      // curve, instead of putting every one at the midpoint.
      //
      // The bow already separates the lines, and for a horizontal run that
      // separates the labels too. For a vertical one it does not: the offset is
      // sideways, so three labels sit at the same height 30px apart, and
      // `consult` is wider than 30px. They overlapped into a single unreadable
      // stack -- on exactly the edges where knowing which line is which matters
      // most, since a vertical pair is usually a role and the artefact it owns.
      //
      // Staggering along the curve works whichever way the edge runs, and the
      // ends are left alone: past about a third from either box the label
      // drifts under the node it is describing.
      const t = n > 1 ? 0.34 + 0.32 * (rank % n) / (n - 1) : 0.5;
      const u = 1 - t;
      lx = u*u*A.x + 2*u*t*cx + t*t*B.x;
      ly = u*u*A.y + 2*u*t*cy + t*t*B.y;
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
      // A second arrow under the label. The tip head says where the edge ends;
      // this says which way it runs *where you are already looking*, which for
      // a long bowed edge is not the same question. Only on edges that carry a
      // verb — refs get ERD multiplicity markers instead, and a plain arrow on
      // top of a crow's foot would be two different claims about one line.
      const ang = Math.atan2(b.y-a.y, b.x-a.x) * 180/Math.PI;
      edges += `<path d="M-5 -3 L4 0 L-5 3 z" fill="${emph?STATE.now:st.label}"
        opacity="${lop}" transform="translate(${lx},${ly+5}) rotate(${ang})"/>`;
      edges += `<text x="${lx}" y="${ly-4}" class="elabel"
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
    if (GV.edgeSel) dim = !(n.id===GV.edgeSel.s || n.id===GV.edgeSel.t);

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

// The status slot names every piece of state that is currently shaping the
// picture, each with its release beside it. State you can turn on but cannot
// see is how the cascade overlay came to outlive the panel that explained it.
function gvNarrate() {
  const box=document.getElementById('gstatus');
  if (!box) return;
  if (GV.mode==='chat') {
    const m=GV.msgs;
    box.textContent = `${m.messages.length} messages · ${
      Object.keys(m.threads).length} threads · ${m.open.length} open`;
    return;
  }
  const parts=[];
  if (GV.inhabit) {
    parts.push(`showing only what <b>${esc(GV.inhabit)}</b> can reach ·
      <span class="link" onclick="gvInhabit(null)">release</span>`);
  } else if (GV.source==='design') {
    const g=GV.graph;
    parts.push(`${g.nodes.length} nodes · ${g.edges.length} edges · `
      + `no lens — pick one above, or open a case`);
  } else if (GV.source==='coverage') {
    const c=GV.trace.coverage;
    parts.push(`${c.covered.length}/${c.covered.length+c.missing.length}
      edges covered · red has no test`);
  } else if (GV.source==='case') {
    parts.push(GV.caseId
      ? `case <b>${esc(GV.caseId)}</b> — click a node for what the case put there`
      : `no case open — pick one in the cases tab`);
  } else {
    const steps=gvSteps();
    parts.push(steps.length
      ? `step ${GV.stepIx+1}/${steps.length} — narration in the steps tab`
      : 'no steps yet');
  }
  if (GV.blast) parts.push(`cascade from <b>${esc(GV.blast.root||'')}</b> ·
      <span class="link" onclick="GV.blast=null;gvDraw()">clear</span>`);
  box.innerHTML = parts.join(' · ');
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

// Everything in graph coordinates; the caller works in screen pixels.
const gvScreen = p => ({x: p.x * GV.view.k + GV.view.x,
                        y: p.y * GV.view.k + GV.view.y});

/**
 * The neighbours of the focused node that are no longer on the canvas.
 *
 * Their edges are suppressed in the main draw. A line that heads off the screen
 * says a relationship exists and then abandons you halfway; at the zoom where
 * that starts happening there are a dozen of them fanning out to nowhere, and
 * they are the least useful marks on the picture. Replacing each with a short
 * local edge to a stand-in says the same thing in the space available.
 */
function offscreenNeighbours() {
  const gone = new Set();
  const svg = document.getElementById('gsvg');
  if (GV.mode !== 'team' || !GV.focus || !svg || !GV.layout || !GV.layout[GV.focus])
    return gone;
  const W = svg.clientWidth, H = svg.clientHeight;
  const here = gvScreen(GV.layout[GV.focus]);
  if (here.x < 0 || here.x > W || here.y < 0 || here.y > H) return gone;

  for (const e of GV.graph.edges) {
    const other = e.s === GV.focus ? e.t : (e.t === GV.focus ? e.s : null);
    if (!other || other === GV.focus || !GV.layout[other] || !gvVisible(other)) continue;
    const p = gvScreen(GV.layout[other]);
    if (p.x < GHOST_INSET || p.x > W - GHOST_INSET ||
        p.y < GHOST_INSET || p.y > H - GHOST_INSET) gone.add(other);
  }
  return gone;
}

function ghostChips() {
  const away = offscreenNeighbours();
  if (!away.size) return '';
  const svg = document.getElementById('gsvg');
  const W = svg.clientWidth, H = svg.clientHeight;
  const from = gvScreen(GV.layout[GV.focus]);

  // Every distinct neighbour once, carrying the edges that reach it. A node
  // reached three ways is one stand-in with three lines into it.
  const out = new Map();
  for (const e of GV.graph.edges) {
    const other = e.s === GV.focus ? e.t : (e.t === GV.focus ? e.s : null);
    if (!other || !away.has(other)) continue;
    if (!out.has(other)) out.set(other, []);
    out.get(other).push(e);
  }

  // --- place ---------------------------------------------------------------
  const chips = [];
  for (const [id, edges] of out) {
    const at = ghostAnchor(from, gvScreen(GV.layout[id]), W, H, GHOST_INSET);
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
  // A real edge, shortened. It leaves the focused node's box the way any edge
  // does, bows the way any edge does, and arrives at the stand-in -- because
  // it *is* the edge, drawn to where the far end has been brought instead of to
  // where the far end is.
  const sh = shapeOfNode(GV.focus);
  let lines = '', boxes = '';
  for (const c of chips) {
    const kinds = [...new Map(c.edges.map(e =>
      [`${e.type}|${e.s === GV.focus}`, e])).values()];

    kinds.forEach((e, i) => {
      const st = ESTYLE[e.type];
      const dx = c.x - from.x, dy = c.y - from.y;
      const len = Math.hypot(dx, dy) || 1;
      // Leave the focused node on its own box, in screen pixels: the box is
      // drawn inside the zoom transform, so its half-width scales with it.
      const hw = sh.w / 2 * GV.view.k + 2, hh = sh.h / 2 * GV.view.k + 2;
      const t = Math.min(hw / (Math.abs(dx) || 1e-6), hh / (Math.abs(dy) || 1e-6));
      const A = {x: from.x + dx * t, y: from.y + dy * t};
      const edge = 0.5 * (Math.abs(dx) / len * c.w + Math.abs(dy) / len * c.h) + 2;
      const B = {x: c.x - dx / len * edge, y: c.y - dy / len * edge};

      // The same left-of-travel bow as the canvas, so several relationships to
      // one stand-in separate the way they do everywhere else.
      const bow = -(Math.min(20, len * .12) + (i - (kinds.length - 1) / 2) * 16);
      const mx = (A.x + B.x) / 2, my = (A.y + B.y) / 2;
      const cx = mx - (B.y - A.y) / len * bow, cy = my + (B.x - A.x) / len * bow;
      const head = e.s === GV.focus ? 'marker-end' : 'marker-start';
      lines += `<path d="M${A.x.toFixed(1)} ${A.y.toFixed(1)}
        Q${cx.toFixed(1)} ${cy.toFixed(1)} ${B.x.toFixed(1)} ${B.y.toFixed(1)}"
        fill="none" stroke="${st.c}" stroke-width="1.8"
        stroke-dasharray="${st.dash}" opacity=".9"
        ${st.head ? `${head}="url(#head-${e.type})"` : ''}/>`;
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

function shapeOfNode(id) {
  const n = GV.graph.nodes.find(x => x.id === id);
  return SHAPE[n ? kindOf(n) : 'record'] || SHAPE.record;
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
  GV.edgeSel = null;
  gvDraw();
  showNode(id);
  if (typeof syncHash==='function') syncHash();
}

function gvFocus(id){GV.focus = GV.focus===id?null:id; GV.edgeSel=null;
  gvDraw(); if(GV.focus) showNode(id);
  if (typeof syncHash==='function') syncHash();}
function gvInhabit(id){
  if (id) {
    const n = GV.graph.nodes.find(x => x.id === id);
    // Reach is a statement about a namespace, and only roles have one. On an
    // artefact the filter emptied the canvas to a single box — a blank claim.
    // The click that precedes every double-click already focused it, and
    // keeping that focus is the honest answer.
    if (!n || n.type !== 'role') return;
  }
  GV.inhabit = GV.inhabit===id?null:id; GV.focus=null; GV.edgeSel=null; gvDraw();
  if(GV.inhabit) showNode(id);
  if (typeof syncHash==='function') syncHash();}
function gvMode(m){GV.mode=m; GV.focus=null; GV.inhabit=null;
  // The toolbar and the key both change shape with the mode, so both rebuild
  // here rather than being patched — patching is how the lens select stayed
  // visible over a chat graph it could not affect.
  gvControls(); gvLegend(); gvFit(); gvDraw();}

// The one door for the lens. Four call sites used to set `GV.source` directly
// and each remembered a different subset of the cleanup: the injected case
// option outlived its case, the cascade overlay outlived its panel, and every
// lens change threw you onto the story subtab whether it applied or not.
function setLens(src){
  const wasCase = GV.source === 'case';
  GV.source = src;
  GV.stepIx = 0;
  // A cascade overlay is an answer to a question asked under the old lens.
  GV.blast = null;
  GV.edgeSel = null;
  if (wasCase && src !== 'case') {
    GV.caseId = null; GV.caseEdges = null; GV.caseSituation = null;
    if (typeof caseListSync === 'function') caseListSync();
  }
  // A lens is a claim about the team picture; picking one in chat means
  // "show me the team picture under it".
  if (GV.mode === 'chat') gvMode('team');
  else { gvControls(); gvLegend(); gvDraw(); }
  // A lens with a home subtab opens it: story and run live in the stepper,
  // coverage's numbers live in its tab. Design and case force nothing.
  if (typeof showTab === 'function') {
    if (src === 'story' || src === 'run') showTab('story');
    else if (src === 'coverage') showTab('coverage');
    else if (typeof syncStoryTab === 'function') syncStoryTab();
  }
  if (typeof syncHash === 'function') syncHash();
}

function gvFit(){
  const pts = GV.mode==='chat' ? Object.values(chatLayout()) : Object.values(GV.layout);
  if (!pts.length) return;
  const xs=pts.map(p=>p.x), ys=pts.map(p=>p.y), stage=document.getElementById('gstage');
  const w=Math.max(...xs)-Math.min(...xs)+340, h=Math.max(...ys)-Math.min(...ys)+220;
  const k=Math.min(stage.clientWidth/w, stage.clientHeight/h, 1.15);
  GV.view={k, x:(stage.clientWidth-w*k)/2-(Math.min(...xs)-170)*k,
           y:(stage.clientHeight-h*k)/2-(Math.min(...ys)-110)*k};
}

// ---------------------------------------------------------------- layouts
// More than one arrangement of the same graph, because more than one question
// is asked of it: the hand-tended map for daily reading, a layered flow when
// you want "how far from the principal is this", a grid by kind when you want
// the inventory, a force pass to untangle a layout you have half-dragged.
//
// Two kinds, deliberately distinct. A *saved* layout is a file the server
// keeps (`layout.json` for main, `layouts/<name>.json` for the rest). A
// *generated* one is computed here from the graph and owns no file — drag it
// into shape and "save layout" asks for a name, which is the moment it stops
// being generated and starts being yours.

// A layout that omits a node used to make the node silently vanish from the
// canvas — indistinguishable from the node not existing, which is the worst
// thing a picture of the design can claim. Strays get parked in rows under
// the drawing instead: visibly unplaced, waiting to be dragged home.
function placeStrays(pos) {
  const out = {};
  for (const [id, p] of Object.entries(pos || {})) out[id] = {x:p.x, y:p.y};
  const placed = GV.graph.nodes.filter(n => out[n.id]);
  const strays = GV.graph.nodes.filter(n => !out[n.id]);
  if (!strays.length) return out;
  const x0 = placed.length ? Math.min(...placed.map(n => out[n.id].x)) : 0;
  const y0 = placed.length ? Math.max(...placed.map(n => out[n.id].y)) + 180 : 0;
  strays.forEach((n, i) => {
    out[n.id] = {x: x0 + (i % 5) * 200, y: y0 + Math.floor(i / 5) * 90};
  });
  return out;
}

// Columns by kind, alphabetical within each: the inventory view. It answers
// "what records exist" faster than any arrangement optimised for edges can.
function autoGrid() {
  const order = ['principal', 'role', 'record', 'journal', 'derived'];
  const buckets = {};
  for (const n of GV.graph.nodes) (buckets[kindOf(n)] ||= []).push(n);
  const pos = {};
  let col = 0;
  for (const kind of order) {
    const list = buckets[kind];
    if (!list) continue;
    list.sort((a, b) => String(a.label).localeCompare(String(b.label)));
    list.forEach((n, i) =>
      pos[n.id] = {x: col * 420, y: (i - (list.length - 1) / 2) * 110});
    col++;
  }
  return pos;
}

// Layered by distance from the principal, breadth-first over everything but
// refs: column = how many relationships stand between them and the person.
// Within a column, each node sits at the average height of its neighbours in
// the column before — one barycentre sweep, which is most of what a proper
// layered layout buys at none of the cost.
function autoFlow() {
  const root = (GV.graph.nodes.find(n => n.type === 'principal')
                || GV.graph.nodes[0]).id;
  const adj = {};
  for (const e of GV.graph.edges) {
    if (e.type === 'refs') continue;
    (adj[e.s] ||= new Set()).add(e.t);
    (adj[e.t] ||= new Set()).add(e.s);
  }
  const col = {[root]: 0};
  const q = [root];
  while (q.length) {
    const v = q.shift();
    for (const w of adj[v] || [])
      if (!(w in col)) { col[w] = col[v] + 1; q.push(w); }
  }
  // Reached by nothing but refs, or by nothing at all: one column past the end,
  // where being unreachable is what the position says.
  let far = Math.max(0, ...Object.values(col)) + 1;
  for (const n of GV.graph.nodes) if (!(n.id in col)) col[n.id] = far;

  const byCol = {};
  for (const n of GV.graph.nodes) (byCol[col[n.id]] ||= []).push(n);
  const pos = {};
  for (const c of Object.keys(byCol).map(Number).sort((a, b) => a - b)) {
    const list = byCol[c];
    const pull = n => {
      const prev = [...(adj[n.id] || [])].filter(o => col[o] === c - 1 && pos[o]);
      return prev.length ? prev.reduce((s, o) => s + pos[o].y, 0) / prev.length : 0;
    };
    list.sort((a, b) => pull(a) - pull(b)
                        || String(a.label).localeCompare(String(b.label)));
    list.forEach((n, i) =>
      pos[n.id] = {x: c * 470, y: (i - (list.length - 1) / 2) * 130});
  }
  return pos;
}

// Fruchterman–Reingold, seeded from wherever the nodes are now — so it is a
// tidy-up of the current arrangement, not a lottery. No randomness anywhere:
// coincident nodes get a jitter derived from their indices, and the same
// input always settles to the same picture.
function autoForce() {
  const ids = GV.graph.nodes.map(n => n.id);
  const seed = Object.keys(GV.layout || {}).length ? GV.layout : autoGrid();
  const grid = autoGrid();
  const p = {};
  ids.forEach((id, i) => {
    const s = seed[id] || grid[id] || {x: (i % 6) * 180, y: Math.floor(i / 6) * 120};
    p[id] = {x: s.x, y: s.y};
  });
  // One spring per connected pair. The multigraph draws every verb; letting
  // every verb also *pull* would drag chatty pairs into each other.
  const springs = [], seen = new Set();
  for (const e of GV.graph.edges) {
    if (e.type === 'refs') continue;
    const k = [e.s, e.t].sort().join('|');
    if (seen.has(k)) continue;
    seen.add(k);
    springs.push([e.s, e.t]);
  }
  const L = 340;                                  // the length a lone edge settles at
  let t = 90;                                     // max step, cooling each pass
  for (let it = 0; it < 260; it++) {
    const disp = {};
    ids.forEach(id => disp[id] = {x: 0, y: 0});
    for (let i = 0; i < ids.length; i++)
      for (let j = i + 1; j < ids.length; j++) {
        const a = p[ids[i]], b = p[ids[j]];
        let dx = a.x - b.x, dy = a.y - b.y, d = Math.hypot(dx, dy);
        if (d < 1) { dx = ((i * 7 + j) % 13) - 6; dy = ((i * 11 + j) % 7) - 3;
                     d = Math.hypot(dx, dy) || 1; }
        const f = (L * L) / (d * d);
        disp[ids[i]].x += dx * f; disp[ids[i]].y += dy * f;
        disp[ids[j]].x -= dx * f; disp[ids[j]].y -= dy * f;
      }
    for (const [s, tt] of springs) {
      const a = p[s], b = p[tt];
      const dx = a.x - b.x, dy = a.y - b.y, d = Math.hypot(dx, dy) || 1;
      const f = d / L;
      disp[s].x -= dx * f; disp[s].y -= dy * f;
      disp[tt].x += dx * f; disp[tt].y += dy * f;
    }
    for (const id of ids) {
      const d = Math.hypot(disp[id].x, disp[id].y) || 1;
      const step = Math.min(d, t);
      p[id].x += disp[id].x / d * step;
      p[id].y += disp[id].y / d * step;
    }
    t *= 0.985;
  }
  for (const id of ids) { p[id].x = Math.round(p[id].x); p[id].y = Math.round(p[id].y); }
  return p;
}

const AUTO_LAYOUTS = {
  'auto: flow':  autoFlow,
  'auto: grid':  autoGrid,
  'auto: force': autoForce,
};

const layoutUrl = name => '/layout.json'
  + (name === 'main' ? '' : `?name=${encodeURIComponent(name)}`);

async function applyLayout(name) {
  if (AUTO_LAYOUTS[name]) {
    GV.layout = placeStrays(AUTO_LAYOUTS[name]());
  } else {
    try { GV.layout = placeStrays(await (await fetch(layoutUrl(name))).json()); }
    catch { return; }                       // the picture you had beats no picture
  }
  GV.settings.layout = name;
  try { localStorage.setItem('rota.gv', JSON.stringify(GV.settings)); } catch {}
  GV.dirty = false;
  gvControls(); gvFit(); gvDraw();
}

async function saveLayout(){
  const name = GV.settings.layout || 'main';
  // A generated layout has no file to overwrite: saving it *is* naming it.
  if (AUTO_LAYOUTS[name]) return saveLayoutAs();
  await fetch(layoutUrl(name), {method:'POST',
                                body:JSON.stringify(GV.layout, null, 2)});
  GV.dirty=false;
  // Into `gstatus`, the toolbar's status slot. It used to write to `gsaved`,
  // an element that does not exist and never did — so the save worked and the
  // confirmation went nowhere, silently, every time. Found by the check that
  // every id a script writes to is an id something creates.
  const box=document.getElementById('gstatus');
  if (!box) return;
  box.textContent=`layout saved — ${name}`;
  setTimeout(gvNarrate, 1600);
}

async function saveLayoutAs() {
  if (!GV.layoutApi) {
    alert('this cockpit server predates named layouts — restart it first');
    return;
  }
  const name = (prompt('save this arrangement as (letters, digits, - and _):')
                || '').trim();
  if (!name) return;
  if (name === 'main' || !/^[A-Za-z0-9_-]{1,40}$/.test(name)) {
    alert('a layout name is letters, digits, - or _, and not "main"');
    return;
  }
  await fetch(layoutUrl(name), {method:'POST',
                                body:JSON.stringify(GV.layout, null, 2)});
  if (!GV.layouts.includes(name)) { GV.layouts.push(name); GV.layouts.sort(); }
  GV.settings.layout = name;
  try { localStorage.setItem('rota.gv', JSON.stringify(GV.settings)); } catch {}
  GV.dirty = false;
  gvControls();
  const box = document.getElementById('gstatus');
  if (box) { box.textContent = `layout saved — ${name}`; setTimeout(gvNarrate, 1600); }
}

async function deleteLayout(name) {
  name = name || GV.settings.layout;
  if (!name || name === 'main' || AUTO_LAYOUTS[name]) return;  // nothing of theirs to delete
  if (!confirm(`delete the saved layout “${name}”?`)) return;
  await fetch(layoutUrl(name) + '&delete=1', {method: 'POST'});
  GV.layouts = GV.layouts.filter(n => n !== name);
  if (GV.settings.layout === name) applyLayout('main');
  else {
    // Deleting from the list is list-keeping, not switching: the picture
    // stays, and the menu re-opens so a second delete is one click away.
    gvControls();
    const menu = document.getElementById('glay');
    if (menu) menu.classList.add('open');
  }
}

// ---------------------------------------------------------------- dropdowns
// Hand-rolled, like everything else on this canvas. A native <select> cannot
// carry a delete button on a row, a group caption, or an action row at the
// bottom — and the moment one list needs those, every list changes species so
// the chrome stays one vocabulary.
//
// Rows: {v, label, on} an option; {grp} a caption; {act:true} an action row
// (never becomes the selection); {del:true} adds a per-row delete control.
//
// The caller writes the `<div class="dd" id="...">` wrapper itself, with the
// id literal in its own source — the id lint reads source text, and an id
// that only ever exists inside an interpolation is an id it cannot vouch for.
function dd(id, rows) {
  const cur = rows.find(r => r.on);
  return `<button class="ddbtn" onclick="ddToggle(event,'${esc(id)}')">
      <span class="ddcur">${esc(cur ? cur.label : '')}</span>
      <span class="ddcaret">&#9662;</span></button>
    <div class="ddmenu">${rows.map(r =>
      r.grp ? `<div class="ddgrp">${esc(r.grp)}</div>`
            : `<div class="ddrow${r.on?' on':''}${r.act?' ddact':''}"
                 data-v="${esc(r.v)}"><span>${esc(r.label)}</span>${
                 r.del ? `<span class="ddx" data-x="${esc(r.v)}"
                   title="delete this layout">&times;</span>` : ''}</div>`
    ).join('')}</div>`;
}

function ddToggle(ev, id) {
  ev.stopPropagation();
  const el = document.getElementById(id);
  if (!el) return;
  const was = el.classList.contains('open');
  ddCloseAll();
  if (!was) el.classList.add('open');
}

function ddCloseAll() {
  document.querySelectorAll('.dd.open').forEach(d => d.classList.remove('open'));
}

// Picking updates the button in place, so a menu whose owner never rebuilds
// (the story list) still shows what it holds. `onDel` gets the × clicks.
function ddWire(id, onPick, onDel) {
  const el = document.getElementById(id);
  if (!el) return;
  el.querySelectorAll('.ddrow').forEach(row => {
    row.onclick = e => {
      e.stopPropagation();
      ddCloseAll();
      if (!row.classList.contains('ddact')) {
        el.querySelectorAll('.ddrow').forEach(r => r.classList.remove('on'));
        row.classList.add('on');
        const cur = el.querySelector('.ddcur');
        if (cur) cur.textContent = row.querySelector('span').textContent;
      }
      onPick(row.dataset.v);
    };
  });
  el.querySelectorAll('.ddx').forEach(x => {
    x.onclick = e => { e.stopPropagation(); onDel && onDel(x.dataset.x); };
  });
}

function gvControls(){
  // Actions and status only. Everything about *stepping* moved to the steps
  // subtab, which is where the steps themselves live — a control separated from
  // the thing it controls is how a toolbar stops making sense.
  //
  // Rebuilt on every mode or settings change, so nothing here may attach a
  // listener to `window` or `document` — those accumulated once per rebuild,
  // and wheel zoom compounded every time somebody touched a setting. The
  // global wiring lives in `gvWireStage`, which runs exactly once. And the
  // rebuild replaces the settings popover, so its open state is carried
  // across — it used to snap shut on the click that changed a setting in it.
  const hadPrefs = document.getElementById('gprefs');
  const wasOpen = !!(hadPrefs && hadPrefs.classList.contains('on'));
  // Lens and layout are claims about the *team* picture; the chat graph lays
  // itself out and answers to no lens. Chrome that does nothing teaches that
  // chrome here sometimes does nothing.
  const team = GV.mode !== 'chat';
  const curLens = GV.source, curLay = GV.settings.layout || 'main';
  const lensRows = [
    {v:'design',   label:'the design',     on:curLens==='design'},
    {v:'coverage', label:'coverage',       on:curLens==='coverage'},
    {v:'story',    label:'design stories', on:curLens==='story'},
    {v:'run',      label:'this run',       on:curLens==='run'},
  ];
  if (GV.caseId) lensRows.push({v:'case', label:'this case', on:curLens==='case'});
  // Saved layouts are the user's and each carries its delete; main is the one
  // every fallback lands on, so it alone has none. The generated three are
  // recomputed, not stored — nothing of theirs to delete either. The action
  // row is how a new layout is born: it names whatever is on screen.
  const layRows = [
    {grp:'saved'},
    ...GV.layouts.map(n=>({v:n, label:n, on:n===curLay, del:n!=='main'})),
    {grp:'generated'},
    ...Object.keys(AUTO_LAYOUTS).map(n=>({v:n, label:n, on:n===curLay})),
    {v:'__add__', label:'+ add layout…', act:true},
  ];

  // No fit button: double-clicking empty canvas refits (wired in
  // gvWireStage), and every programmatic reason to refit — mode switch,
  // layout change — already calls gvFit itself.
  document.getElementById('gctl').innerHTML=`
    <button data-gmode="team" class="${team?'on':''}" onclick="gvMode('team')">team</button>
    <button data-gmode="chat" class="${team?'':'on'}" onclick="gvMode('chat')">chat</button>` + (team ? `
    <span class="sep"></span>
    <span class="cap">lens</span>
    <div class="dd" id="gsrc">${dd('gsrc', lensRows)}</div>
    <span class="cap">layout</span>
    <div class="dd" id="glay">${dd('glay', layRows)}</div>
    <button id="gsave">save layout</button>` : '') + `
    <span class="sep"></span>
    <button id="gcog" title="display settings">&#9881;</button>
    <span class="sig" id="gstatus"></span>
    <div id="gprefs" class="pop${wasOpen?' on':''}"></div>`;

  const by = id => document.getElementById(id);
  if (team) {
    ddWire('gsrc', v => setLens(v));
    ddWire('glay', v => v === '__add__' ? saveLayoutAs() : applyLayout(v),
           n => deleteLayout(n));
    by('gsave').onclick = saveLayout;
  }

  const prefs = by('gprefs');
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
  by('gcog').onclick = (e) => {
    e.stopPropagation();
    prefs.classList.toggle('on');
  };
  prefs.onclick = (e) => e.stopPropagation();
}

// The stage listeners, attached exactly once per page. They read everything
// through `GV`, so nothing about them needs rebuilding when the chrome is.
function gvWireStage(){
  if (GV.wired) return;
  GV.wired = true;
  const svg=document.getElementById('gsvg');
  if (!svg) return;
  svg.onclick=()=>{if(!GV.dragged){GV.focus=null; GV.edgeSel=null; gvDraw();
    if (typeof syncHash==='function') syncHash();}};
  // Fit lives on the canvas itself: double-click empty ground brings the
  // whole picture back. Node double-clicks stop propagation, so this only
  // fires where there is nothing else to mean.
  svg.ondblclick=()=>{if(!GV.dragged){gvFit(); gvDraw();}};
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
  // Closing popovers looks the elements up at event time, because every
  // toolbar rebuild replaces them.
  document.addEventListener('click', () => {
    const p = document.getElementById('gprefs');
    if (p) p.classList.remove('on');
    ddCloseAll();
  });
  // Escape backs out one layer at a time: an open menu first, then the focus,
  // then the reach filter — the same order the layers were put on.
  document.addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    const prefs = document.getElementById('gprefs');
    const menus = document.querySelector('.dd.open');
    if (menus || (prefs && prefs.classList.contains('on'))) {
      ddCloseAll();
      if (prefs) prefs.classList.remove('on');
    }
    else if (GV.focus) { GV.focus = null; gvDraw(); }
    else if (GV.inhabit) gvInhabit(null);
  });
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
  const holder = document.getElementById('glegend');
  if (!holder) return;

  // The chat graph draws its own vocabulary — message cards, not roles and
  // records — so it gets its own key. The team key used to stay up over it,
  // teaching five shapes the picture never draws.
  if (GV.mode === 'chat') {
    const card = (stroke, wide) => `<svg width="16" height="11"><rect x="1" y="1"
      width="14" height="9" rx="3" fill="#ffffff" stroke="${stroke}"
      stroke-width="${wide?2:1}"/></svg>`;
    const rows = [
      [`<svg width="16" height="11"><rect x="1" y="1" width="14" height="9" rx="3"
         fill="${SHAPE.principal.fill}" stroke="${SHAPE.principal.stroke}"/></svg>`,
       'from the principal'],
      [card(STATE.ready, true), 'open — nothing has answered yet'],
      [card(SHAPE.role.stroke), 'answered — a session committed'],
      [card(STATE.faint), 'answered, but no session committed'],
      [`<svg width="30" height="8"><line x1="1" y1="4" x2="21" y2="4"
         stroke="${ESTYLE.refs.c}" stroke-width="1.6"/>
         <path d="M20 1 L27 4 L20 7 z" fill="${ESTYLE.refs.c}"/></svg>`,
       'caused by — every message refs its cause'],
    ];
    holder.innerHTML = `<div class="lgrp"><b>messages</b>` +
      rows.map(([g, label]) =>
        `<span class="lkey" style="cursor:default">${g} ${esc(label)}</span>`
      ).join('') + `</div>`;
    return;
  }

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
