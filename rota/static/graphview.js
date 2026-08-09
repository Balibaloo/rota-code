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
            focus:null, inhabit:null, blast:null,
            view:{x:0,y:0,k:1}, dragNode:null, dirty:false};

const ESTYLE = {
  writes:   {c:'#6ea8fe', dash:'',    head:true,  label:'#7d9fd6'},
  reads:    {c:'#55d187', dash:'5 3', head:true,  label:'#5fa87c'},
  messages: {c:'#e6b25a', dash:'',    head:true,  label:'#c99a52'},
  refs:     {c:'#3b4454', dash:'2 5', head:false, label:'#4d566a'},
};

const esc = s => String(s ?? '').replace(/[<>&]/g,c=>({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]));
const ek = e => `${e[0]}|${e[1]}|${e[2]}`;

// Entity kinds get different containers: a person is not a document is not a
// journal, and the eye should not have to read the label to know which.
function kindOf(n) {
  if (n.type === 'client') return 'client';
  if (n.type === 'role') return 'role';
  if (n.contact === false) return 'journal';   // fact artefact: read, never asked
  if (n.owner === 'scheduler') return 'derived';
  return 'record';
}

const SHAPE = {
  client:  {w:140, h:52, rx:26, fill:'#2b2517', stroke:'#8a7233', dash:''},
  role:    {w:152, h:50, rx:10, fill:'#1b2333', stroke:'#3d5680', dash:''},
  record:  {w:172, h:42, rx:4,  fill:'#191e28', stroke:'#33405a', dash:''},
  journal: {w:172, h:42, rx:4,  fill:'#15191f', stroke:'#333a46', dash:'4 3'},
  derived: {w:172, h:42, rx:4,  fill:'#12161c', stroke:'#2b3340', dash:'2 4'},
};

async function gvLoad() {
  const [g,l,st,tr,ms] = await Promise.all([
    fetch('/graph.json').then(r=>r.json()),
    fetch('/layout.json').then(r=>r.json()),
    fetch('/stories.json').then(r=>r.json()),
    fetch('/trace.json').then(r=>r.json()),
    fetch('/messages.json').then(r=>r.json()),
  ]);
  GV.graph=g; GV.layout=l; GV.stories=st; GV.trace=tr; GV.msgs=ms;
  gvControls(); gvFit(); gvDraw(); buildStoryTab();
}

const gvSteps = () =>
  GV.source==='story' ? (GV.stories[GV.storyIx]?.steps||[])
: GV.source==='run'   ? (GV.trace.steps||[]) : [];

function gvLit() {
  const lit=new Map();
  if (GV.source==='coverage') {
    (GV.trace.coverage.covered||[]).forEach(e=>lit.set(ek(e),'covered'));
    return lit;
  }
  const steps=gvSteps();
  for (let i=0;i<=GV.stepIx && i<steps.length;i++)
    (steps[i].edges||[]).forEach(e=>lit.set(ek(e), i===GV.stepIx?'now':'past'));
  return lit;
}

// Inhabit: the graph collapses to exactly what a role can reach. Not
// "neighbours" — namespace. Double-click Critic and the system model is not
// dimmed, it is gone.
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
      fill="none" stroke="#3d4757" stroke-width="1.6" marker-end="url(#head)"/>`;
  }

  for (const m of msgs) {
    const p=pos[m.id]; if(!p) continue;
    const w=250, h=m.produced?58:38;
    const open = m.status==='open';
    const stroke = open ? '#e6b25a' : m.produced?.committed ? '#3d5680' : '#3a3040';
    const fill = m.from_role==='client' ? '#2b2517' : '#181d26';
    const out = m.produced
      ? `${m.produced.calls.length} call(s)` + (m.produced.writes.length
          ? ` · ${m.produced.writes.length} write(s)` : '')
      : open ? 'awaiting' : '';

    nodes += `<g class="gnode" data-msg="${m.id}" transform="translate(${p.x-w/2},${p.y-h/2})">
      <rect width="${w}" height="${h}" rx="7" fill="${fill}" stroke="${stroke}"
        stroke-width="${open?2.4:1.2}"/>
      <text x="10" y="16" class="mfrom">${esc(m.from_role)} → ${esc(m.to_role)}</text>
      <text x="${w-10}" y="16" class="mverb">${esc(m.verb)}</text>
      ${m.produced?`<text x="10" y="34" class="mout">${esc(m.produced.role)}: ${esc(out)}</text>`:''}
      ${m.produced?`<text x="10" y="50" class="mrefs">${esc(
        (m.produced.calls||[]).slice(0,3).join(' '))}</text>`
       :`<text x="10" y="32" class="mrefs">${esc(out)}</text>`}
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
      else if (uncovered.has(key)){op=.3;col='#e8746a';w=1.4;}
    } else if (state==='now'){op=1;w=3.2;}
    else if (state==='past'){op=.42;w=1.8;}
    if (GV.focus) op = incident?Math.max(op,.95):.05;
    if (GV.inhabit) op = Math.max(op,.7);

    const mx=(a.x+b.x)/2,my=(a.y+b.y)/2,dx=b.x-a.x,dy=b.y-a.y;
    const len=Math.hypot(dx,dy)||1, bow=Math.min(46,len*.13);
    const cx=mx-(dy/len)*bow, cy=my+(dx/len)*bow;
    const lx=(a.x+2*cx+b.x)/4, ly=(a.y+2*cy+b.y)/4;

    edges += `<path d="M${a.x} ${a.y} Q${cx} ${cy} ${b.x} ${b.y}" fill="none"
      stroke="${col}" stroke-width="${w}" stroke-dasharray="${st.dash}" opacity="${op}"
      ${st.head?'marker-end="url(#head)"':''} class="gedge"
      data-e="${e.s}|${e.t}|${e.type}|${esc(e.v||'')}"/>`;

    // Edge names always on — the grammar is the content, not a hover reward.
    if (e.v && op > 0.12) {
      const emph = state==='now'||incident;
      edges += `<text x="${lx}" y="${ly-4}" class="elabel"
        fill="${emph?'#e6b25a':st.label}" opacity="${emph?1:Math.min(1,op+.35)}"
        font-size="${emph?11:9.5}">${esc(e.v)}</text>`;
    }
  }

  for (const n of GV.graph.nodes) {
    const p=GV.layout[n.id];
    if(!p||!gvVisible(n.id)) continue;
    const k=kindOf(n), sh=SHAPE[k];
    const dim = GV.focus && n.id!==GV.focus &&
      !GV.graph.edges.some(e=>(e.s===GV.focus&&e.t===n.id)||(e.t===GV.focus&&e.s===n.id));
    const ring = ready.has(n.id)?'#e6b25a' : claimed[n.id]?'#e8746a'
      : blast&&blast.has(n.id)?'#c07ae8' : sh.stroke;
    const hot = ready.has(n.id)||claimed[n.id]||(blast&&blast.has(n.id));

    nodes += `<g class="gnode" data-n="${n.id}" opacity="${dim?.2:1}"
      transform="translate(${p.x-sh.w/2},${p.y-sh.h/2})">
      <rect width="${sh.w}" height="${sh.h}" rx="${sh.rx}" fill="${sh.fill}"
        stroke="${ring}" stroke-width="${hot?2.5:1.3}" stroke-dasharray="${sh.dash}"/>
      ${k==='role'?`<rect width="4" height="${sh.h}" rx="2" fill="${ring}" opacity=".8"/>`:''}
      ${k==='record'||k==='journal'?`<line x1="0" y1="11" x2="${sh.w}" y2="11"
        stroke="${ring}" stroke-width=".8" opacity=".45"/>`:''}
      <text x="${sh.w/2}" y="${sh.h/2+(k==='record'||k==='journal'?4:1)}"
        class="nlabel">${esc(n.label)}</text>
      ${vol[n.id]?`<text x="${sh.w-7}" y="9" class="nvol">${vol[n.id]}</text>`:''}
    </g>`;
  }
  return {edges, nodes};
}

function gvDraw() {
  const {edges, nodes} = GV.mode==='chat' ? drawChat() : drawTeam();
  const v=GV.view;
  document.getElementById('gsvg').innerHTML =
    `<defs><marker id="head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5"
      markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z"
      fill="#6b7688"/></marker></defs>
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
  const box=document.getElementById('gnarr');
  if (GV.mode==='chat') {
    const m=GV.msgs;
    box.innerHTML=`<b>The conversation</b> <span class="sig">${m.messages.length} message(s),
      ${Object.keys(m.threads).length} thread(s), ${m.open.length} open. Every
      message refs its cause; roots are client utterances, gates and ticks.</span>`;
    return;
  }
  if (GV.inhabit) {
    box.innerHTML=`<b>Inhabiting ${esc(GV.inhabit)}</b> <span class="sig">— its
      entire world. Everything else does not exist to it.</span>
      <span class="link" onclick="gvInhabit(null)">release</span>`;
    return;
  }
  if (GV.source==='coverage') {
    const c=GV.trace.coverage;
    box.innerHTML=`<b>Edge coverage</b> <span class="sig">${c.covered.length}/${
      c.covered.length+c.missing.length} exercised. Red edges have no test;
      drawing an edge creates one.</span>`;
    return;
  }
  const steps=gvSteps(), s=steps[GV.stepIx];
  box.innerHTML = s
    ? `<b>${esc(s.title)}</b> <span class="sig">${esc(s.round||'')} · ${GV.stepIx+1}/${steps.length}</span>
       <p>${esc(s.text||'')}</p>`
    : '<i class="empty">no steps — run the loop, or pick a story</i>';
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
  document.getElementById('gsaved').textContent='layout saved';
  setTimeout(()=>document.getElementById('gsaved').textContent='', 1600);
}

function gvControls(){
  document.getElementById('gctl').innerHTML=`
    <button data-gmode="team" class="on" onclick="gvMode('team')">team</button>
    <button data-gmode="chat" onclick="gvMode('chat')">chat</button>
    <span class="sep"></span>
    <select id="gsrc"><option value="coverage">coverage</option>
      <option value="story">design stories</option>
      <option value="run">this run</option></select>
    <button id="gprev">‹</button><button id="gnext">›</button>
    <button id="gfit">fit</button><button id="gsave">save layout</button>
    <span class="sig" id="gsaved"></span>`;

  gsrc.onchange=e=>{GV.source=e.target.value; GV.stepIx=0; GV.mode='team'; gvMode('team');};
  gprev.onclick=()=>{GV.stepIx=Math.max(0,GV.stepIx-1); gvDraw(); syncStoryTab();};
  gnext.onclick=()=>{GV.stepIx=Math.min(gvSteps().length-1,GV.stepIx+1); gvDraw(); syncStoryTab();};
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
  svg.addEventListener('wheel',e=>{e.preventDefault();
    GV.view.k*= e.deltaY<0?1.12:0.89; gvDraw();},{passive:false});
}

document.addEventListener('DOMContentLoaded', gvLoad);
