// The graph. Hand-rolled SVG rather than a graph library: the layout is fixed
// (layout.json holds it), 22 nodes and ~110 edges draw comfortably, the cockpit
// stays offline, and we keep full control of the overlays — which are the whole
// reason for drawing it.
//
// One renderer, three sources: authored stories, a real run, and edge coverage.
// That is the point — a story firing an edge the implementation never touches,
// or a run lighting one no story anticipated, becomes visible rather than
// arguable.

const GV = {graph:null, layout:null, stories:null, trace:null,
            source:'coverage', storyIx:0, stepIx:0, focus:null, inhabit:null,
            blast:null, view:{x:0, y:0, k:1}};

const ESTYLE = {
  writes:   {c:'#6ea8fe', dash:'',    head:true},
  reads:    {c:'#55d187', dash:'4 3', head:true},
  messages: {c:'#e6b25a', dash:'',    head:true},
  refs:     {c:'#3b4454', dash:'2 4', head:false},
};

const esc = s => String(s ?? '').replace(/[<>&]/g, c => ({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]));
const ek = e => `${e[0]}|${e[1]}|${e[2]}`;

async function gvLoad() {
  const [g,l,st,tr] = await Promise.all([
    fetch('/graph.json').then(r=>r.json()),
    fetch('/layout.json').then(r=>r.json()),
    fetch('/stories.json').then(r=>r.json()),
    fetch('/trace.json').then(r=>r.json()),
  ]);
  GV.graph=g; GV.layout=l; GV.stories=st; GV.trace=tr;
  gvControls(); gvFit(); gvDraw();
}

const gvSteps = () =>
  GV.source==='story' ? (GV.stories[GV.storyIx]?.steps||[])
: GV.source==='run'   ? (GV.trace.steps||[]) : [];

function gvLit() {
  const lit = new Map();
  if (GV.source === 'coverage') {
    (GV.trace.coverage.covered||[]).forEach(e => lit.set(ek(e), 'covered'));
    return lit;
  }
  const steps = gvSteps();
  for (let i=0; i<=GV.stepIx && i<steps.length; i++)
    (steps[i].edges||[]).forEach(e => lit.set(ek(e), i===GV.stepIx?'now':'past'));
  return lit;
}

// Inhabit: the graph collapses to exactly what a role can reach. Not
// "neighbours" — namespace. Double-click Critic and the system model is not
// dimmed, it is gone, which is the design's central claim made visual.
function gvVisible(id) {
  if (!GV.inhabit) return true;
  if (id === GV.inhabit) return true;
  const g = GV.graph;
  return g.edges.some(e =>
    (e.s===GV.inhabit && e.t===id && e.type!=='refs') ||
    (e.s===id && e.t===GV.inhabit && e.type==='messages'));
}

function gvDraw() {
  const lit = gvLit();
  const ready = new Set((GV.trace.overlay.ready||[]).map(r=>r.role));
  const claimed = GV.trace.overlay.claimed||{};
  const vol = GV.trace.overlay.volume||{};
  const uncovered = new Set((GV.trace.coverage.missing||[]).map(ek));
  const blast = GV.blast ? new Set(GV.blast.artefacts) : null;

  let edges='', nodes='';
  for (const e of GV.graph.edges) {
    const a=GV.layout[e.s], b=GV.layout[e.t];
    if (!a||!b) continue;
    if (!gvVisible(e.s)||!gvVisible(e.t)) continue;
    const st=ESTYLE[e.type]||ESTYLE.refs, key=ek([e.s,e.t,e.type]), state=lit.get(key);
    const incident = GV.focus && (e.s===GV.focus||e.t===GV.focus);

    let op=0.12, w=1.2, col=st.c;
    if (GV.source==='coverage') {
      if (state==='covered') {op=.8; w=2;}
      else if (uncovered.has(key)) {op=.28; col='#e8746a'; w=1.4;}
    } else if (state==='now') {op=1; w=3.2;}
    else if (state==='past') {op=.42; w=1.8;}
    if (GV.focus) op = incident ? Math.max(op,.95) : .05;
    if (GV.inhabit) op = Math.max(op,.7);

    const mx=(a.x+b.x)/2, my=(a.y+b.y)/2, dx=b.x-a.x, dy=b.y-a.y;
    const len=Math.hypot(dx,dy)||1, bow=Math.min(46,len*.13);
    const cx=mx-(dy/len)*bow, cy=my+(dx/len)*bow;

    edges += `<path d="M${a.x} ${a.y} Q${cx} ${cy} ${b.x} ${b.y}" fill="none"
      stroke="${col}" stroke-width="${w}" stroke-dasharray="${st.dash}" opacity="${op}"
      ${st.head?'marker-end="url(#head)"':''} class="gedge"
      data-e="${e.s}|${e.t}|${e.type}|${esc(e.v||'')}"/>`;
    if ((state==='now'||incident) && e.v)
      edges += `<text x="${cx}" y="${cy-5}" class="elabel">${esc(e.v)}</text>`;
  }

  for (const n of GV.graph.nodes) {
    const p=GV.layout[n.id];
    if (!p || !gvVisible(n.id)) continue;
    const role=n.type==='role', client=n.type==='client';
    const w=role||client?152:170, h=role||client?46:40;
    const dim = GV.focus && n.id!==GV.focus &&
      !GV.graph.edges.some(e=>(e.s===GV.focus&&e.t===n.id)||(e.t===GV.focus&&e.s===n.id));
    const ring = ready.has(n.id) ? '#e6b25a' : claimed[n.id] ? '#e8746a'
      : blast&&blast.has(n.id) ? '#c07ae8' : role ? '#3d5680' : '#2a3140';

    nodes += `<g class="gnode" data-n="${n.id}" opacity="${dim?.22:1}"
      transform="translate(${p.x-w/2},${p.y-h/2})">
      <rect width="${w}" height="${h}" rx="8" stroke-width="${ready.has(n.id)||claimed[n.id]||(blast&&blast.has(n.id))?2.5:1.2}"
        fill="${client?'#2a2418':role?'#1b2333':'#181d26'}" stroke="${ring}"/>
      <text x="${w/2}" y="${h/2+1}" class="nlabel">${esc(n.label)}</text>
      ${vol[n.id]?`<text x="${w-8}" y="14" class="nvol">${vol[n.id]}</text>`:''}
    </g>`;
  }

  const v=GV.view;
  document.getElementById('gsvg').innerHTML =
    `<defs><marker id="head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5"
      markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z"
      fill="#6b7688"/></marker></defs>
     <g transform="translate(${v.x},${v.y}) scale(${v.k})">${edges}${nodes}</g>`;

  document.querySelectorAll('.gnode').forEach(el=>{
    el.onclick = ev => {ev.stopPropagation(); gvFocus(el.dataset.n);};
    el.ondblclick = ev => {ev.stopPropagation(); gvInhabit(el.dataset.n);};
  });
  document.querySelectorAll('.gedge').forEach(el=>{
    el.onclick = ev => {ev.stopPropagation(); showEdge(el.dataset.e);};
  });
  gvNarrate();
}

function gvNarrate() {
  const box=document.getElementById('gnarr');
  if (GV.inhabit) {
    box.innerHTML = `<b>Inhabiting ${esc(GV.inhabit)}</b>
      <span class="sig">— its entire world. Everything else does not exist to it.</span>
      <span class="link" onclick="gvInhabit(null)">release</span>`;
    return;
  }
  if (GV.source==='coverage') {
    const c=GV.trace.coverage;
    box.innerHTML=`<b>Edge coverage</b> <span class="sig">${c.covered.length}/${c.covered.length+c.missing.length}
      edges exercised. Red edges have no test; drawing an edge creates one.</span>`;
    return;
  }
  const steps=gvSteps(), s=steps[GV.stepIx];
  box.innerHTML = s ? `<b>${esc(s.title)}</b> <span class="sig">${esc(s.round||'')} ·
    ${GV.stepIx+1}/${steps.length}</span><p>${esc(s.text||'')}</p>`
    : '<i class="empty">no steps — run the loop, or pick a story</i>';
}

function gvFocus(id){ GV.focus = GV.focus===id?null:id; gvDraw();
  if (GV.focus) showNode(id); }
function gvInhabit(id){ GV.inhabit = GV.inhabit===id?null:id; GV.focus=null; gvDraw();
  if (GV.inhabit) showNode(id); }

function gvFit(){
  const xs=Object.values(GV.layout).map(p=>p.x), ys=Object.values(GV.layout).map(p=>p.y);
  const stage=document.getElementById('gstage');
  const w=Math.max(...xs)-Math.min(...xs)+300, h=Math.max(...ys)-Math.min(...ys)+200;
  const k=Math.min(stage.clientWidth/w, stage.clientHeight/h, 1.2);
  GV.view={k, x:(stage.clientWidth-w*k)/2-(Math.min(...xs)-150)*k,
           y:(stage.clientHeight-h*k)/2-(Math.min(...ys)-100)*k};
}

function gvControls(){
  document.getElementById('gctl').innerHTML = `
    <select id="gsrc"><option value="coverage">coverage</option>
      <option value="story">design stories</option>
      <option value="run">this run</option></select>
    <select id="gstory">${GV.stories.map((s,i)=>
      `<option value="${i}">${esc(s.name)}</option>`).join('')}</select>
    <button id="gprev">‹</button><button id="gnext">›</button>
    <button id="gfit">fit</button>`;
  gsrc.onchange=e=>{GV.source=e.target.value; GV.stepIx=0; gvDraw();};
  gstory.onchange=e=>{GV.storyIx=+e.target.value; GV.stepIx=0; GV.source='story';
    gsrc.value='story'; gvDraw();};
  gprev.onclick=()=>{GV.stepIx=Math.max(0,GV.stepIx-1); gvDraw();};
  gnext.onclick=()=>{GV.stepIx=Math.min(gvSteps().length-1,GV.stepIx+1); gvDraw();};
  gfit.onclick=()=>{gvFit(); gvDraw();};

  const svg=document.getElementById('gsvg');
  svg.onclick=()=>{GV.focus=null; gvDraw();};
  let drag=null;
  svg.onmousedown=e=>{drag={x:e.clientX,y:e.clientY,vx:GV.view.x,vy:GV.view.y};};
  window.addEventListener('mousemove',e=>{ if(!drag) return;
    GV.view.x=drag.vx+(e.clientX-drag.x); GV.view.y=drag.vy+(e.clientY-drag.y); gvDraw();});
  window.addEventListener('mouseup',()=>{drag=null;});
  svg.addEventListener('wheel',e=>{e.preventDefault();
    const f=e.deltaY<0?1.12:0.89; GV.view.k*=f; gvDraw();},{passive:false});
}

document.addEventListener('DOMContentLoaded', gvLoad);
