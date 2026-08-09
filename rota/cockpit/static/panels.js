// The sidebar: the actual rows, the actual prompts, the actual calls.
//
// Grouped by the *question being asked*, not by where the data happens to live —
// so the grouping survives the vocabulary work:
//
//   WIRING   what the graph says about this thing
//   STATE    what is true of it right now
//   BRIEF    what a role is told (roles only)
//
// Nothing is shown for every node kind. A journal has no approval state; a
// derived artefact has no writer. Showing empty sections to be consistent is how
// a panel becomes noise.

const P = () => document.getElementById('pbody');

function table(rows, cols) {
  if (!rows || !rows.length) return '<div class="empty">none</div>';
  const use = cols || Object.keys(rows[0]);
  return `<div class="tw"><table><tr>${use.map(c=>`<th>${esc(c)}</th>`).join('')}</tr>${
    rows.map(r=>`<tr>${use.map(c=>{
      const v=r[c], s = typeof v==='object' ? JSON.stringify(v) : String(v ?? '');
      return `<td title="${esc(s)}">${esc(s.length>140?s.slice(0,140)+'…':s)}</td>`;
    }).join('')}</tr>`).join('')}</table></div>`;
}

const group = (title, body) =>
  `<div class="grp"><div class="grphead">${esc(title)}</div>${body}</div>`;

const sec = (title, count, body, open) =>
  `<details class="sec" ${open?'open':''}><summary>${esc(title)}
    <span class="sig">${count ?? ''}</span></summary><div class="body">${body}</div></details>`;

function phead(title, sub, actions) {
  document.getElementById('phead').innerHTML =
    `<h2>${esc(title)}</h2><span class="sig">${sub}</span>
     ${actions?`<div class="pacts">${actions}</div>`:''}`;
}

// ---------------------------------------------------------------- dispatch
async function showNode(id) {
  const n = GV.graph.nodes.find(x=>x.id===id);
  if (!n) return;
  showTab('detail');
  return n.type==='role' ? showRole(id) : showArtefact(id);
}

// ---------------------------------------------------------------- roles
async function showRole(id) {
  phead(id, 'loading…');
  const r = await (await fetch(`/role.json?id=${encodeURIComponent(id)}`)).json();

  const contacts = r.contacts.map(c=>`
    <div class="row"><span class="link" onclick="gvFocus('${c.role}')">${esc(c.role)}</span>
      <span class="sig">${esc(c.verbs.join(', ')||'no verb')}</span>
      <div class="sig sub">${c.clause==='ask'
        ? `may ask — reads ${esc(c.because_reads.join(', '))}, which ${esc(c.role)} writes`
        : `may inform — ${esc(c.role)} reads ${esc(c.because_writes.join(', '))}`}</div>
    </div>`).join('');

  const wiring = group('WIRING',
    sec('working set', r.working_set.length,
        `<pre>${r.working_set.map(s=>'TOOL: '+esc(s)).join('<br>')}</pre>`, true) +
    sec('contacts', r.contacts.length, contacts||'<div class="empty">none</div>') +
    sec('reads / writes', `${r.reads.length}r ${r.writes.length}w`,
      `<b class="sig">reads</b><div>${r.reads.map(a=>
        `<span class="link" onclick="showArtefact('${a}')">${esc(a)}</span>`).join(' · ')||'—'}</div>
       <b class="sig">writes</b><div>${r.writes.map(a=>
        `<span class="link" onclick="showArtefact('${a}')">${esc(a)}</span>`).join(' · ')||'—'}</div>`) +
    sec('coverage', `${r.coverage.covered}/${r.coverage.total}`,
      r.coverage.missing.length
        ? `<b class="fail">untested edges</b><pre>${r.coverage.missing.map(esc).join('<br>')}</pre>`
        : '<span class="pass">every edge exercised</span>'));

  const sessions = r.sessions.map(s=>`
    <div class="row">${s.committed?'<span class="pass">✓</span>':'<span class="fail">✗</span>'}
      <span class="sig">${esc(s.mode)} · ${esc(s.model||'—')}</span>
      <div class="sig sub">${esc(s.calls.join(' ')||'no calls')}</div>
      ${s.writes.length?`<div class="sig sub">wrote ${esc(
        s.writes.map(w=>w.table_name+':'+w.row_id).join(', '))}</div>`:''}
    </div>`).join('') || '<div class="empty">no sessions yet</div>';

  const state = group('STATE', sec('sessions', r.sessions.length, sessions, true));

  // Mode first. A mode is the unit a session actually runs in — it decides the
  // prompt *and* the tools, and the two only make sense read together. Grouping
  // by artefact kind and listing modes underneath had it backwards.
  // The base is the mode a session runs in when nothing more specific applies,
  // so it belongs in the list rather than beside it — collapsed, because it is
  // the one you read least often.
  const modes = group('MODES',
    sec('base — when no mode applies', `${r.working_set.length} tools`,
      `<b class="sig">full working set</b>
       <pre>${r.working_set.map(t=>'TOOL: '+esc(t)).join('<br>')}</pre>
       <b class="sig">what it is told</b>
       <pre>${esc(r.base_prompt)}</pre>`) +
    Object.entries(r.modes).map(([m,v])=>sec(
      m, `${v.tools.length} tools`,
      `<b class="sig">tools in this mode</b>
       <pre>${v.tools.map(t=>'TOOL: '+esc(t)).join('<br>')}</pre>
       <b class="sig">what it is told</b>
       <pre>${esc(v.piece)}</pre>
       <details><summary class="sig">full composed prompt</summary>
         <pre>${esc(v.composed)}</pre></details>`)).join('')
    );

  phead(r.label, `role · woken by ${esc(r.inbound_verbs.join(', ')||'ticks only')}`,
    `<span class="link" onclick="gvInhabit('${id}')">show only what it reaches</span>`);
  P().innerHTML = `<div class="note">${esc(r.note)}</div>${modes}${wiring}${state}`;
}

// ---------------------------------------------------------------- artefacts
async function showArtefact(id) {
  phead(id, 'loading…');
  const a = await (await fetch(`/artefact.json?id=${encodeURIComponent(id)}`)).json();
  const isJournal = a.contact === false;

  // STATE first for artefacts: the rows are what you came for.
  const tables = (a.tables||[]).map(t=> t.error
    ? `<div class="fail">${esc(t.error)}</div>`
    : sec(t.name, `${t.count} rows · v${t.version}`,
          table(t.rows, t.columns), t.count>0 && t.count<50)).join('');

  const state = group('STATE',
    (tables || '<div class="empty">no rows yet</div>') +
    ((a.receipts||[]).length
      ? sec('recent writes', a.receipts.length,
            table(a.receipts, ['role','table_name','row_id','new_version']))
      : ''));

  const wiring = group('WIRING',
    sec('who touches it', (a.operations||[]).length,
        table(a.operations, ['role','type','verb','rows','depth','actor']), true) +
    (((a.refs_out||[]).length + (a.refs_in||[]).length)
      ? sec('refs', (a.refs_out||[]).length+(a.refs_in||[]).length,
          `<b class="sig">points at</b>${table(a.refs_out,['to','rel','card'])}
           <b class="sig">pointed at by</b>${table(a.refs_in,['from','rel','card'])}`)
      : ''));

  phead(a.label, `artefact · written by ${esc(a.written_by.join(', ')||'the system')}`,
    `<span class="link" onclick="showBlast('${id}')">what this wakes</span>`);
  P().innerHTML =
    `<div class="note">${esc(a.note)}
      ${isJournal?`<div class="sub sig"><b>Fact artefact.</b> ${esc(a.contact_why)}</div>`:''}
     </div>${state}${wiring}`;
}

// ---------------------------------------------------------------- edges
async function showEdge(data) {
  showTab('detail');
  const [s,t,type]=data.split('|');
  const e = await (await fetch(
    `/edge.json?s=${encodeURIComponent(s)}&t=${encodeURIComponent(t)}&type=${type}`)).json();
  if (e.error){ phead('—', esc(e.error)); P().innerHTML=''; return; }

  phead(`${s} → ${t}`, `${esc(type)} · ${e.covered
    ? '<span class="pass">covered by a test</span>'
    : '<span class="fail">no test exercises this</span>'}`,
    `<span class="link" onclick="gvFocus('${s}')">focus ${esc(s)}</span> ·
     <span class="link" onclick="gvFocus('${t}')">focus ${esc(t)}</span>`);

  P().innerHTML =
    group('WIRING', sec('grammar', e.variants.length,
      table(e.variants,['verb','noun','rows','depth','actor','label']), true)) +
    group('STATE', sec(type==='messages'?'messages sent':'calls made',
      (e.evidence||[]).length, table(e.evidence||[]), true));
}

// ---------------------------------------------------------------- messages
async function showMessage(id) {
  showTab('detail');
  const m = (GV.msgs.messages||[]).find(x=>x.id===id);
  if (!m) return;
  const p = m.produced;

  phead(`${m.from_role} → ${m.to_role}`,
    `${esc(m.verb)} · ${m.status==='open'?'<span class="fail">open</span>':esc(m.status)}
     · thread ${esc(m.thread_id)}`);

  P().innerHTML =
    (m.entry ? `<div class="note">“${esc(m.entry)}”</div>` : '') +
    group('WIRING', sec('the message', '', table([{
        id:m.id, cause:m.cause_id||'(root)', cause_kind:m.cause_kind,
        round:m.round_no, attempts:m.attempts, refs:m.body_refs.join(', ')||'—',
      }]), true)) +
    group('STATE', p
      ? sec(`${p.role} session`, p.committed?'committed':'failed',
          `<div class="sig">${esc(p.mode)} · ${esc(p.model||'—')}</div>
           <b class="sig">calls</b><pre>${esc(p.calls.join('\\n')||'none')}</pre>
           <b class="sig">writes</b><pre>${esc(p.writes.join('\\n')||'none')}</pre>`, true)
      : `<div class="empty">${m.status==='open'
          ? 'nothing has answered this yet' : 'no session recorded'}</div>`);
}

async function showBlast(id) {
  const b = await (await fetch(`/blast.json?id=${encodeURIComponent(id)}`)).json();
  GV.blast=b; gvDraw(); showTab('detail');
  phead(`what changing ${id} wakes`, 'the cascade, in the order owners are summoned',
    `<span class="link" onclick="GV.blast=null;gvDraw();showArtefact('${id}')">clear</span>`);
  P().innerHTML = group('WIRING', sec('wake order', b.wakes.length,
    table(b.wakes.map(w=>({artefact:w.artefact, owners:w.owners.join(', ')})),
          ['artefact','owners']), true)) +
    `<div class="note sig">The cascade walks the refs DAG and summons each owner.
      This is that walk, before it happens rather than reconstructed after.</div>`;
}

// ---------------------------------------------------------------- story subtab
function buildStoryTab() {
  const el = document.getElementById('storybody');
  el.innerHTML = `<select id="ststory" style="width:100%;margin-bottom:6px">
      ${GV.stories.map((s,i)=>`<option value="${i}">${esc(s.name)}</option>`).join('')}
    </select>
    <div class="stnav"><button id="stprev">‹ prev</button>
      <span class="sig" id="stpos"></span>
      <button id="stnext">next ›</button></div>
    <div id="ststeps"></div>`;
  document.getElementById('stprev').onclick = ()=>{
    GV.stepIx=Math.max(0,GV.stepIx-1); gvDraw(); syncStoryTab();};
  document.getElementById('stnext').onclick = ()=>{
    GV.stepIx=Math.min(gvSteps().length-1,GV.stepIx+1); gvDraw(); syncStoryTab();};
  document.getElementById('ststory').onchange = e=>{
    GV.storyIx=+e.target.value; GV.stepIx=0; GV.source='story';
    document.getElementById('gsrc').value='story'; gvDraw(); syncStoryTab();
  };
  syncStoryTab();
}

function syncStoryTab() {
  const steps = GV.source==='run' ? (GV.trace.steps||[])
              : (GV.stories[GV.storyIx]?.steps||[]);
  const el = document.getElementById('ststeps');
  if (!el) return;
  const pos = document.getElementById('stpos');
  if (pos) pos.textContent = steps.length
    ? `${GV.stepIx+1} / ${steps.length}${GV.source==='run'?' · this run':''}` : '—';
  el.innerHTML = steps.map((s,i)=>`
    <div class="step ${i===GV.stepIx?'on':''}" onclick="jumpStep(${i})">
      <b>${i+1}. ${esc(s.title)}</b>
      <span class="sig">${esc(s.round||'')}</span>
      ${i===GV.stepIx?`<p>${esc(s.text||'')}</p>`:''}
    </div>`).join('') || '<div class="empty">no steps</div>';
  const cur = el.querySelector('.step.on');
  if (cur) cur.scrollIntoView({block:'nearest'});
}

function jumpStep(i){
  if (GV.source==='coverage'){GV.source='story'; document.getElementById('gsrc').value='story';}
  GV.stepIx=i; gvDraw(); syncStoryTab();
}

// ---------------------------------------------------------------- chrome
let view='graph', ptab='detail', fingerprint=null, lastSig='', stalled=0;

function showTab(t){
  ptab=t;
  document.querySelectorAll('[data-ptab]').forEach(b=>
    b.classList.toggle('on', b.dataset.ptab===t));
  document.getElementById('pdetail').style.display = t==='detail'?'block':'none';
  document.getElementById('pstory').style.display  = t==='story'?'block':'none';
  if (t==='story') syncStoryTab();
}

document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{
  view=b.dataset.view;
  document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('on',x===b));
  ['graph','live','coverage'].forEach(v=>
    document.getElementById(v).classList.toggle('on', v===view));
  if (view==='coverage') loadCoverage();
});

async function refresh() {
  let s; try{ s = await (await fetch('/state.json')).json(); }
  catch{ st_.textContent='server gone'; st_.className='state stuck'; return; }

  const tips=s.frontier.tips, preds=s.frontier.predicates;
  const sig=JSON.stringify([tips,preds,s.versions]);
  if (sig===lastSig) stalled++; else {stalled=0; lastSig=sig;}
  const busy=tips.length+preds.length>0, stuck=busy&&stalled>6;
  st_.textContent = stuck?'STUCK':busy?'WORK PENDING':'QUIESCENT';
  st_.className='state '+(stuck?'stuck':busy?'busy':'idle');
  tick_.textContent = `${tips.length} tip · ${preds.length} predicate`
    + (stalled?` · still for ${stalled}`:'');

  // Header hover: the detail without the real estate.
  //
  // These populate the `.pop` panels. They used to *also* set `title`, which is
  // why hovering produced two things at once — an empty styled box, because
  // nothing ever filled it, and the OS tooltip a second later carrying the
  // content the box was supposed to have. One of them had to go, and the
  // native tooltip is the one that cannot be laid out, coloured or clicked.
  const rows = xs => xs.length ? xs.join('') : '<div class="pnone">none</div>';

  document.getElementById('pop-tick').innerHTML =
    `<h4>frontier tips</h4>` +
    rows(tips.map(t=>`<div class="prow"><span>${esc(t.role)}</span>
      <em>← ${esc(t.verb)}</em></div>`)) +
    `<h4>predicates</h4>` +
    rows(Object.entries(s.predicate_status).map(([n,w])=>
      `<div class="prow"><span class="${w.length?'pon':'poff'}">${w.length?'●':'○'}
        ${esc(n)}</span><em>${esc(w.join(', '))}</em></div>`)) +
    `<h4>versions</h4>` +
    rows(s.versions.map(v=>`<div class="prow"><span>${esc(v.table_name)}</span>
      <em>v${v.version}</em></div>`));

  document.getElementById('pop-state').innerHTML =
    `<h4>rows on record</h4>` +
    rows(Object.entries(s.counts).map(([k,v])=>
      `<div class="prow"><span>${esc(k)}</span><em>${v}</em></div>`));

  const set=(id,html)=>{const e=document.getElementById(id); if(e) e.innerHTML=html;};
  set('tips', table(tips,['role','verb','message']));
  set('preds', Object.entries(s.predicate_status).map(([n,w])=>
    `<div class="${w.length?'':'muted'}">${w.length?'●':'○'} ${esc(n)}
      <span class="sig">${esc(w.join(', '))}</span></div>`).join(''));
  set('sessions', table(s.sessions,['id','role','mode','committed','model']));
  set('receipts', table(s.receipts,['role','table_name','row_id','new_version']));
  set('messages', table(s.messages,['from_role','to_role','verb','status','attempts']));
  set('calls', table(s.tool_calls,['fn','args_summary']));
  set('items', table(s.items,['id','kind','approval','approval_ver','version','headline']));
  set('runtime', '<b>claims</b>'+table(s.claims,['role','session_id'])
    +'<b>checkpoints</b>'+table(s.checkpoints,['session_id','role','valid'])
    +'<b>open ledger</b>'+table(s.ledger,['id','about_ref','default_taken','author']));
  set('counts', Object.entries(s.counts).map(([k,v])=>
    `<span title="${esc(k)}">${esc(k)} <b>${v}</b></span>`).join(''));
}

const st_=document.getElementById('state'), tick_=document.getElementById('tick');

for (const [el, pop] of [[st_, 'pop-state'], [tick_, 'pop-tick']]) {
  const box = document.getElementById(pop);
  const place = () => {
    const r = el.getBoundingClientRect();
    box.style.left = Math.max(8, r.left) + 'px';
  };
  el.addEventListener('mouseenter', () => {place(); box.classList.add('on');});
  el.addEventListener('mouseleave', e => {
    if (!box.matches(':hover')) box.classList.remove('on');
  });
  box.addEventListener('mouseleave', () => box.classList.remove('on'));
}

async function loadCoverage(){
  const c = await (await fetch('/coverage.json')).json();
  document.getElementById('coveragebody').innerHTML =
    `<h3>${c.covered}/${c.total} edges (${c.percent.toFixed(0)}%)</h3>` +
    Object.entries(c.by_role).map(([role,[cov,miss]])=>{
      const pct=100*cov/(cov+miss);
      return `<div class="barwrap"><span style="width:90px">${esc(role)}</span>
        <span class="sig" style="width:56px">${cov}/${cov+miss}</span>
        <span class="bar"><i style="width:${pct}%"></i></span></div>`;}).join('') +
    `<p class="muted">Drawing an edge creates a red row. Coverage cannot drift
      from the design, because the design generates it.</p>
     <b>uncovered</b>${table(c.missing.map(m=>({edge:m})),['edge'])}`;
}

async function checkReload(){
  try{
    const fp=(await (await fetch('/fingerprint')).text()).trim();
    if (fingerprint===null){fingerprint=fp; return;}
    if (fp!==fingerprint){
      document.getElementById('reload').textContent='sources changed — reloading…';
      setTimeout(()=>location.reload(),300);
    }
  }catch{}
}

// resizable sidebar
(function(){
  const h=document.getElementById('phandle'), wrap=document.getElementById('gwrap');
  let d=null;
  h.onmousedown=e=>{d={x:e.clientX,w:document.getElementById('gpanel').offsetWidth};
    e.preventDefault();};
  window.addEventListener('mousemove',e=>{ if(!d) return;
    const w=Math.min(900,Math.max(280, d.w-(e.clientX-d.x)));
    wrap.style.gridTemplateColumns=`1fr 6px ${w}px`; gvFit&&gvFit(); gvDraw&&gvDraw();});
  window.addEventListener('mouseup',()=>{d=null;});
})();

document.querySelectorAll('[data-ptab]').forEach(b=>b.onclick=()=>showTab(b.dataset.ptab));
refresh();
setInterval(()=>{if(view==='live') refresh();},1500);
setInterval(checkReload,1000);
