// The panel: the actual rows, the actual prompts, the actual calls.
//
// Summaries are what you build when you cannot serve the real thing. Here we
// can, so nothing is aggregated away — click `glossary` and you get the
// glossary, not a count of it. Everything in the panel links back into the
// graph, so reading is navigation.

const P = () => document.getElementById('gpanel');

function table(rows, cols) {
  if (!rows || !rows.length) return '<div class="empty">none</div>';
  const use = cols || Object.keys(rows[0]);
  return `<div style="overflow:auto"><table><tr>${
    use.map(c=>`<th>${esc(c)}</th>`).join('')}</tr>${
    rows.map(r=>`<tr>${use.map(c=>{
      const v = r[c];
      const s = typeof v === 'object' ? JSON.stringify(v) : String(v ?? '');
      return `<td>${esc(s.length>160 ? s.slice(0,160)+'…' : s)}</td>`;
    }).join('')}</tr>`).join('')}</table></div>`;
}

const sec = (title, count, body, open) =>
  `<details class="sec" ${open?'open':''}><summary>${esc(title)}
    <span class="sig">${count ?? ''}</span></summary>
   <div class="body">${body}</div></details>`;

async function showNode(id) {
  const node = GV.graph.nodes.find(n=>n.id===id);
  if (!node) return;
  if (node.type === 'role') return showRole(id);
  return showArtefact(id);
}

async function showRole(id) {
  P().innerHTML = `<div class="phead"><h2>${esc(id)}</h2>
    <span class="sig">loading…</span></div>`;
  const r = await (await fetch(`/role.json?id=${encodeURIComponent(id)}`)).json();

  const contacts = r.contacts.map(c => `
    <div><span class="link" onclick="gvFocus('${c.role}')">${esc(c.role)}</span>
      <span class="sig">${esc(c.verbs.join(', ')||'no verb')}</span><br>
      <span class="sig">${c.clause==='ask'
        ? `may ask, because it reads ${esc(c.because_reads.join(', '))} which ${esc(c.role)} writes`
        : `may inform, because ${esc(c.role)} reads ${esc(c.because_writes.join(', '))} which it writes`}</span>
    </div>`).join('');

  const modes = Object.entries(r.modes).map(([m,v]) => sec(
    `mode: ${m}`, `${v.tools.length} tools`,
    `<pre>${esc(v.piece)}</pre><b class="sig">tools in this mode</b>
     <pre>${v.tools.map(t=>'TOOL: '+esc(t)).join('<br>')}</pre>`)).join('');

  const sessions = r.sessions.map(s => `
    <div><span class="sig">${esc(s.mode)} · ${esc(s.model||'—')}</span>
      ${s.committed?'<span class="pass">committed</span>':'<span class="fail">failed</span>'}
      <br><span class="sig">calls: ${esc(s.calls.join(', ')||'none')}</span>
      ${s.writes.length?`<br><span class="sig">wrote: ${
        esc(s.writes.map(w=>w.table_name+':'+w.row_id).join(', '))}</span>`:''}
    </div>`).join('') || '<div class="empty">no sessions yet</div>';

  P().innerHTML = `
    <div class="phead"><h2>${esc(r.label)}</h2>
      <span class="sig">role · woken by ${esc(r.inbound_verbs.join(', ')||'ticks only')}</span>
      <div style="margin-top:6px"><span class="link" onclick="gvInhabit('${id}')">
        inhabit — show only its world</span></div></div>
    <div class="sec"><div class="body sig">${esc(r.note)}</div></div>
    ${sec('working set', r.working_set.length,
      `<pre>${r.working_set.map(s=>'TOOL: '+esc(s)).join('<br>')}</pre>`, true)}
    ${sec('contacts', r.contacts.length, contacts||'<div class="empty">none</div>')}
    ${sec('reads / writes',
      `${r.reads.length}r ${r.writes.length}w`,
      `<b class="sig">reads</b><div>${r.reads.map(a=>
        `<span class="link" onclick="showArtefact('${a}')">${esc(a)}</span>`).join(' · ')||'—'}</div>
       <b class="sig">writes</b><div>${r.writes.map(a=>
        `<span class="link" onclick="showArtefact('${a}')">${esc(a)}</span>`).join(' · ')||'—'}</div>`)}
    ${sec('base prompt', '', `<pre>${esc(r.base_prompt)}</pre>`)}
    ${modes}
    ${sec('sessions', r.sessions.length, sessions)}
    ${sec('coverage', `${r.coverage.covered}/${r.coverage.total}`,
      r.coverage.missing.length
        ? `<b class="fail">untested edges</b><pre>${r.coverage.missing.map(esc).join('<br>')}</pre>`
        : '<span class="pass">every edge exercised</span>')}`;
}

async function showArtefact(id) {
  P().innerHTML = `<div class="phead"><h2>${esc(id)}</h2><span class="sig">loading…</span></div>`;
  const a = await (await fetch(`/artefact.json?id=${encodeURIComponent(id)}`)).json();

  const tables = (a.tables||[]).map(t => t.error
    ? `<div class="fail">${esc(t.error)}</div>`
    : sec(t.name, `${t.count} rows · v${t.version}`,
        table(t.rows, t.columns), t.count>0 && t.count<40)).join('');

  const ops = table(a.operations||[], ['role','type','verb','scope','actor']);
  const refs = `<b class="sig">points at</b>${
      table(a.refs_out||[], ['to','rel','card'])}<b class="sig">pointed at by</b>${
      table(a.refs_in||[], ['from','rel','card'])}`;

  P().innerHTML = `
    <div class="phead"><h2>${esc(a.label)}</h2>
      <span class="sig">artefact · written by ${esc(a.written_by.join(', ')||'nobody')}</span>
      <div style="margin-top:6px"><span class="link" onclick="showBlast('${id}')">
        blast radius — what a change here wakes</span></div></div>
    <div class="sec"><div class="body sig">${esc(a.note)}
      ${a.contact===false?`<br><br><b>Fact artefact.</b> ${esc(a.contact_why)}`:''}</div></div>
    ${tables || '<div class="empty">no rows</div>'}
    ${sec('who touches it', (a.operations||[]).length, ops, true)}
    ${sec('refs', (a.refs_out||[]).length+(a.refs_in||[]).length, refs)}
    ${sec('recent receipts', (a.receipts||[]).length,
      table(a.receipts||[], ['role','table_name','row_id','new_version']))}`;
}

async function showEdge(data) {
  const [s,t,type] = data.split('|');
  const e = await (await fetch(
    `/edge.json?s=${encodeURIComponent(s)}&t=${encodeURIComponent(t)}&type=${type}`)).json();
  if (e.error) { P().innerHTML = `<div class="phead"><h2>${esc(e.error)}</h2></div>`; return; }

  P().innerHTML = `
    <div class="phead"><h2>${esc(s)} → ${esc(t)}</h2>
      <span class="sig">${esc(type)}</span>
      <div style="margin-top:4px" class="${e.covered?'pass':'fail'}">
        ${e.covered?'covered by a test':'no test exercises this edge'}</div></div>
    ${sec('grammar', e.variants.length,
      table(e.variants, ['verb','noun','scope','actor','label']), true)}
    ${sec(type==='messages'?'messages sent':'calls made', (e.evidence||[]).length,
      table(e.evidence||[]), true)}
    <div class="sec"><div class="body">
      <span class="link" onclick="gvFocus('${s}')">focus ${esc(s)}</span> ·
      <span class="link" onclick="gvFocus('${t}')">focus ${esc(t)}</span>
    </div></div>`;
}

async function showBlast(id) {
  const b = await (await fetch(`/blast.json?id=${encodeURIComponent(id)}`)).json();
  GV.blast = b; gvDraw();
  P().innerHTML = `
    <div class="phead"><h2>blast radius: ${esc(id)}</h2>
      <span class="sig">what a change here cascades to, in wake order</span>
      <div style="margin-top:6px"><span class="link"
        onclick="GV.blast=null;gvDraw();showArtefact('${id}')">clear</span></div></div>
    ${sec('wake order', b.wakes.length,
      table(b.wakes.map(w=>({artefact:w.artefact, owners:w.owners.join(', ')})),
            ['artefact','owners']), true)}
    <div class="sec"><div class="body sig">The cascade walks the refs DAG and
      summons each owner. This is that walk, before it happens rather than
      reconstructed afterwards.</div></div>`;
}

// ---- the other tabs -------------------------------------------------------
let view='graph', fingerprint=null, lastSig='', stalled=0;

document.querySelectorAll('.tab').forEach(b => b.onclick = () => {
  view = b.dataset.view;
  document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('on', x===b));
  ['graph','live','prompts','coverage'].forEach(v =>
    document.getElementById(v).classList.toggle('on', v===view));
  if (view==='prompts') loadPrompts();
  if (view==='coverage') loadCoverage();
});

async function refresh() {
  let s; try { s = await (await fetch('/state.json')).json(); }
  catch { state.textContent='server gone'; state.className='state stuck'; return; }

  const tips=s.frontier.tips, preds=s.frontier.predicates;
  const sig=JSON.stringify([tips,preds,s.versions]);
  if (sig===lastSig) stalled++; else {stalled=0; lastSig=sig;}
  const busy=tips.length+preds.length>0, stuck=busy && stalled>6;
  state.textContent = stuck?'STUCK':busy?'WORK PENDING':'QUIESCENT';
  state.className = 'state '+(stuck?'stuck':busy?'busy':'idle');
  tick.textContent = `${tips.length} tip(s) · ${preds.length} predicate wake(s)`
    + (stalled?` · unchanged for ${stalled}`:'');

  tips_.innerHTML = table(tips,['role','verb','message']);
  preds_.innerHTML = Object.entries(s.predicate_status).map(([n,w])=>
    `<div class="${w.length?'':'muted'}">${w.length?'●':'○'} ${esc(n)}
     <span class="sig">${esc(w.join(', '))}</span></div>`).join('');
  sessions_.innerHTML = table(s.sessions,['id','role','mode','committed','model']);
  receipts_.innerHTML = table(s.receipts,['role','table_name','row_id','new_version']);
  messages_.innerHTML = table(s.messages,['from_role','to_role','verb','status','attempts']);
  calls_.innerHTML = table(s.tool_calls,['fn','args_summary']);
  items_.innerHTML = table(s.items,['id','kind','approval','approval_ver','version','headline']);
  runtime_.innerHTML = '<b>claims</b>'+table(s.claims,['role','session_id'])
    +'<b>checkpoints</b>'+table(s.checkpoints,['session_id','role','valid'])
    +'<b>open ledger</b>'+table(s.ledger,['id','about_ref','default_taken','author']);
  counts_.innerHTML = Object.entries(s.counts).map(([k,v])=>
    `<span>${esc(k)} <b>${v}</b></span>`).join('');
}

const $ = id => document.getElementById(id);
const tips_=()=>0;  // placeholder replaced below
['tips','preds','sessions','receipts','messages','calls','items','runtime','counts']
  .forEach(id => window[id+'_'] = $(id));
window.state = $('state'); window.tick = $('tick');

async function loadPrompts() {
  const p = await (await fetch('/prompts.json')).json();
  $('promptbody').innerHTML = Object.entries(p).map(([role,r])=>`
    <details class="sec"><summary>${esc(role)} — ${r.namespace_size} functions,
      ${Object.keys(r.modes).length} mode(s)</summary><div class="body">
      <b>base</b><pre>${esc(r.base)}</pre>
      ${Object.entries(r.modes).map(([m,v])=>
        `<b>mode: ${esc(m)}</b><pre>${esc(v.piece)}</pre>`).join('')}
      <b>advertised working set</b>
      <pre>${r.signatures.map(s=>'TOOL: '+esc(s)+'<br>').join('')}</pre>
    </div></details>`).join('');
}

async function loadCoverage() {
  const c = await (await fetch('/coverage.json')).json();
  $('coveragebody').innerHTML =
    `<h3>${c.covered}/${c.total} edges (${c.percent.toFixed(0)}%)</h3>` +
    Object.entries(c.by_role).map(([role,[cov,miss]])=>{
      const pct=100*cov/(cov+miss);
      return `<div class="barwrap"><span style="width:90px">${esc(role)}</span>
        <span class="sig" style="width:60px">${cov}/${cov+miss}</span>
        <span class="bar"><i style="width:${pct}%"></i></span></div>`;}).join('') +
    `<p class="muted">Drawing an edge creates a red row. Coverage cannot drift
     from the design, because the design generates it.</p>
     <b>uncovered</b>${table(c.missing.map(m=>({edge:m})),['edge'])}`;
}

async function checkReload() {
  try {
    const fp = (await (await fetch('/fingerprint')).text()).trim();
    if (fingerprint===null) {fingerprint=fp; return;}
    if (fp!==fingerprint) {
      $('reload').textContent='sources changed — reloading…';
      setTimeout(()=>location.reload(), 300);
    }
  } catch {}
}

refresh();
setInterval(()=>{ if(view==='live') refresh(); }, 1500);
setInterval(checkReload, 1000);
