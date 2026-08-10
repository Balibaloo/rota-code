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
            mode:'team', source:'coverage', storyIx:0, stepIx:0,
            focus:null, inhabit:null, blast:null, keyhl:null,
            view:{x:0,y:0,k:1}, dragNode:null, dirty:false};

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
const STATE = {
  ready:  '#d97706',   // a wake is pending for this role
  live:   '#dc2626',   // mid-session, holding a claim
  blast:  '#9333ea',   // in the cascade path of the selected artefact
  gap:    '#dc2626',   // an edge no test exercises
  now:    '#b45309',   // the edge lit by the current step
  ink:    '#334155',
  faint:  '#94a3b8',
  grid:   '#dde5ee',
  arrow:  '#475569',
};

const SHAPE = {
  principal:  {w:140, h:52, rx:26, fill:'#fdf1dc', stroke:'#b45309', dash:'', ink:'#7c2d12'},
  role:    {w:152, h:50, rx:10, fill:'#ffffff', stroke:'#3b6ea5', dash:'', ink:'#132a44'},
  record:  {w:172, h:42, rx:4,  fill:'#e4f3e8', stroke:'#2f855a', dash:'', ink:'#14532d'},
  journal: {w:172, h:42, rx:4,  fill:'#eef7f0', stroke:'#4b9e74', dash:'4 3', ink:'#166534'},
  derived: {w:172, h:42, rx:4,  fill:'#f1f5f2', stroke:'#94a3a0', dash:'2 4', ink:'#475569'},
};

// Reference edges route as orthogonal segments, ported from the design viewer.
// A bezier between two artefacts reads as "these are related somehow"; an elbow
// that visibly avoids the boxes in between reads as a *structural* relation,
// which is what a ref is. Channels are chosen so no segment crosses another
// artefact — the same reason the original did it rather than using taxi routing,
// which cannot avoid obstacles.
function refPath(e) {
  const W = 172, H = 42, M = 18;
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
  const anchor=(n,face)=>{
    const p=GV.layout[n];
    return face==='left' ?{x:p.x-W/2, y:p.y+off}
         : face==='right'?{x:p.x+W/2, y:p.y+off}
         : face==='top'  ?{x:p.x+off, y:p.y-H/2}
         :                {x:p.x+off, y:p.y+H/2};
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
    const k = [e.s, e.t].sort().join('|');
    (pairs[k] = pairs[k] || []).push(e);
  }

  GV.spread = {};
  const ORDER = {writes: 0, reads: 1, messages: 2};
  for (const [k, list] of Object.entries(pairs)) {
    const [first] = k.split('|');
    list.sort((a, b) =>
      (ORDER[a.type] ?? 9) - (ORDER[b.type] ?? 9) ||
      (a.v || '').localeCompare(b.v || ''));
    list.forEach((e, i) => {
      const slot = list.length === 1 ? 0 : (i - (list.length - 1) / 2) * 30;
      // Canonical side: mirror when the edge runs against the sorted order, so
      // both directions read off the same ruler.
      GV.spread[`${e.s}|${e.t}|${e.type}|${e.v}`] = e.s === first ? slot : -slot;
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
  const [g,l,st,tr,ms] = await Promise.all([
    fetch('/graph.json').then(r=>r.json()),
    fetch('/layout.json').then(r=>r.json()),
    fetch('/stories.json').then(r=>r.json()),
    fetch('/trace.json').then(r=>r.json()),
    fetch('/messages.json').then(r=>r.json()),
  ]);
  GV.graph=g; GV.layout=l; GV.stories=st; GV.trace=tr; GV.msgs=ms;
  computeSpread(); gvControls(); gvFit(); gvDraw(); buildStoryTab();
}

const gvSteps = () =>
  GV.source==='story' ? (GV.stories[GV.storyIx]?.steps||[])
: GV.source==='run'   ? (GV.trace.steps||[]) : [];

function gvLit() {
  const lit=new Map();
  // A case lights what it *instantiates*, plus what it asserts on top.
  //
  // The first version lit the edges the mode offered, which is a picture of
  // what the role could do -- identical for every case in that mode. What a
  // case is actually about is the rows it seeds and how they hang together, and
  // the `refs` edges between two seeded artefacts are only drawn where the
  // seeded data really references seeded data.
  if (GV.source==='case' && GV.caseEdges) {
    (GV.caseSituation?.links||[]).forEach(([a,b])=>lit.set(`${a}|${b}|refs`,'seeded'));
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

  for (const e of GV.graph.edges) {
    const a=GV.layout[e.s], b=GV.layout[e.t];
    if(!a||!b||!gvVisible(e.s)||!gvVisible(e.t)) continue;
    const st=ESTYLE[e.type]||ESTYLE.refs, key=ek([e.s,e.t,e.type]), state=lit.get(key);
    const incident = GV.focus && (e.s===GV.focus||e.t===GV.focus);

    let op=0.16, w=1.2, col=st.c;
    if (GV.source==='coverage') {
      if (state==='covered'){op=.8;w=2;}
      else if (uncovered.has(key)){op=.42;col=STATE.gap;w=1.5;}
    } else if (state==='now'){op=1;w=3.2;}
    else if (state==='seeded'){op=.85;w=2.2;col=STATE.blast;}
    else if (state==='forbidden'){op=.95;w=2.4;col=STATE.gap;}
    else if (state==='past'){op=.42;w=1.8;}
    if (GV.focus) op = incident?Math.max(op,.95):.05;
    if (GV.inhabit) op = Math.max(op,.7);

    // Hovering the key selects rather than annotates: everything else recedes,
    // so "what is a journal" is answered by the picture instead of by the
    // sentence underneath it.
    if (GV.keyhl) op = GV.keyhl.edge===e.type ? Math.max(op,.95) : 0.05;

    let d, lx, ly;
    let markers = '';
    if (e.type === 'refs') {
      const r = refPath(e);
      if (!r) continue;
      d = r.d; lx = r.mid.x; ly = r.mid.y;
      markers = `marker-start="url(#${r.startMarker})" marker-end="url(#${r.endMarker})"`;
    } else {
      // Spread parallel edges so a multigraph does not collapse onto one path.
      const off = GV.spread[`${e.s}|${e.t}|${e.type}|${e.v}`] || 0;
      const mx=(a.x+b.x)/2, my=(a.y+b.y)/2, dx=b.x-a.x, dy=b.y-a.y;
      const len=Math.hypot(dx,dy)||1, bow=Math.min(46,len*.13)+off;
      const cx=mx-(dy/len)*bow, cy=my+(dx/len)*bow;
      d = `M${a.x} ${a.y} Q${cx} ${cy} ${b.x} ${b.y}`;
      lx=(a.x+2*cx+b.x)/4; ly=(a.y+2*cy+b.y)/4;
    }

    // Arrowheads are per type and match the edge colour. They were there all
    // along and invisible: one slate-grey marker, and `opacity` on a path
    // applies to its markers too — so at the resting opacity of 0.16 the head
    // was a grey smudge on a coloured line. A direction you have to zoom in to
    // read is a direction the picture is not carrying.
    const headId = markers ? '' : `marker-end="url(#head-${e.type})"`;
    edges += `<path d="${d}" fill="none"
      stroke="${col}" stroke-width="${w}" stroke-dasharray="${st.dash}" opacity="${op}"
      ${markers || (st.head?headId:'')} class="gedge"
      data-e="${e.s}|${e.t}|${e.type}|${esc(e.v||'')}"/>`;

    // Edge names always on — the grammar is the content, not a hover reward.
    if (e.v && op > 0.12) {
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
        font-size="${emph?11:9.5}">${esc(e.v)}</text>`;
    }
  }

  for (const n of GV.graph.nodes) {
    const p=GV.layout[n.id];
    if(!p||!gvVisible(n.id)) continue;
    const k=kindOf(n), sh=SHAPE[k];
    let dim = GV.focus && n.id!==GV.focus &&
      !GV.graph.edges.some(e=>(e.s===GV.focus&&e.t===n.id)||(e.t===GV.focus&&e.s===n.id));
    // In case mode the situation *is* the picture: an artefact with rows is
    // part of what the case set up, and one without is scenery. Everything not
    // in the situation dims, so the shape of the case reads without a caption.
    const seeded = GV.source==='case' && GV.caseSituation
      ? new Set([...(GV.caseSituation.seeded||[]).map(x=>x.artefact),
                 ...(GV.caseSituation.roles||[])])
      : null;
    if (seeded) dim = !seeded.has(n.id);

    const ring = seeded && seeded.has(n.id) ? STATE.blast
      : ready.has(n.id)?STATE.ready : claimed[n.id]?STATE.live
      : blast&&blast.has(n.id)?STATE.blast : sh.stroke;
    const hot = (seeded && seeded.has(n.id))
      || ready.has(n.id)||claimed[n.id]||(blast&&blast.has(n.id));

    // Key hover selects nodes the same way it selects edges — by kind, or by
    // the state ring they are currently wearing.
    if (GV.keyhl) {
      const h = GV.keyhl;
      dim = !(h.kind ? k===h.kind
            : h.ring==='ready' ? ready.has(n.id)
            : h.ring==='live'  ? !!claimed[n.id]
            : h.ring==='blast' ? !!(blast && blast.has(n.id))
            : false);
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

function gvDraw() {
  const {edges, nodes} = GV.mode==='chat' ? drawChat() : drawTeam();
  const v=GV.view;
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
    <g transform="translate(${v.x},${v.y}) scale(${v.k})">${edges}${nodes}</g>`;

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
    <select id="gsrc"><option value="coverage">coverage</option>
      <option value="story">design stories</option>
      <option value="run">this run</option></select>
    <span class="sep"></span>
    <button id="gfit">fit</button><button id="gsave">save layout</button>
    <span class="sig" id="gstatus"></span>`;

  gsrc.onchange=e=>{GV.source=e.target.value; GV.stepIx=0; gvMode('team');
    showTab('story'); syncStoryTab();};
  gfit.onclick=()=>{gvFit(); gvDraw();};
  gsave.onclick=saveLayout;

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
  ["state", [
    ["ready to wake", {ring:"ready"}, "a predicate is firing for this role right now"],
    ["mid-session",   {ring:"live"},  "holding a claim. Roles are single-instance, so nothing else can wake it"],
    ["cascade reach", {ring:"blast"}, "what a change to the selected artefact would wake, following refs"],
  ]],
];

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
    ready: `<i class="ring" style="border-color:${STATE.ready}"></i>`,
    live:  `<i class="ring" style="border-color:${STATE.live}"></i>`,
    blast: `<i class="ring" style="border-color:${STATE.blast}"></i>`,
  };

  const el = document.getElementById('glegend');
  el.innerHTML =
    `<div style="display:flex;gap:16px">` +
    LEGEND.map(([group, items]) => `<div class="lgrp"><b>${group}</b>` +
      items.map(([label, sel, why], i) => {
        const glyph = mark[sel.edge || sel.kind || sel.ring];
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
