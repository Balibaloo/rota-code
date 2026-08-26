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

// A truth column reads as one glyph everywhere. `committed` arrived as ✓/✗ in
// the role panel and as a raw 0/1 in the live tables — the same fact in two
// notations, which reads as two facts. TEXT columns like `default_taken` stay
// words: they carry which default, not whether.
const FLAG_COLS = new Set(['committed', 'valid']);

// Into an attribute, so quotes must go too — `esc` only covers text nodes.
const attr = v => esc(v).replace(/"/g, '&quot;');
const flag = v => (v === null || v === undefined || v === '')
  ? '<span class="empty">—</span>'
  : (+v ? '<span class="pass">✓</span>' : '<span class="fail">✗</span>');

const cell = (c, v) => {
  const s = typeof v==='object' ? JSON.stringify(v) : String(v ?? '');
  const body = FLAG_COLS.has(c) ? flag(v)
    : esc(s.length>140 ? s.slice(0,140)+'…' : s);
  return `<td title="${esc(s)}">${body}</td>`;
};

function table(rows, cols) {
  if (!rows || !rows.length) return '<div class="empty">none</div>';
  const use = cols || Object.keys(rows[0]);
  return `<div class="tw"><table><tr>${use.map(c=>`<th>${esc(c)}</th>`).join('')}</tr>${
    rows.map(r=>`<tr>${use.map(c=>cell(c, r[c])).join('')}</tr>`).join('')}</table></div>`;
}

// A table whose rows ask "why is this here". Identical to `table` except each
// row carries its table name and key, which is exactly what `provenance` wants.
// The key travels as data attributes and is picked up by one delegated
// listener: an id quoted into an inline onclick string is an id that breaks
// the handler the day it contains a quote.
function rowTable(tableName, rows, cols) {
  if (!rows || !rows.length) return '<div class="empty">none</div>';
  const use = cols || Object.keys(rows[0]);
  const key = use.includes('id') ? 'id' : use[0];
  return `<div class="tw"><table><tr>${use.map(c=>`<th>${esc(c)}</th>`).join('')}</tr>${
    rows.map(r=>{
      const id = String(r[key] ?? '');
      return `<tr class="prov" title="why is this here?" data-t="${
        esc(tableName)}" data-r="${esc(id)}">${
        use.map(c=>cell(c, r[c])).join('')}</tr>`;
    }).join('')}</table></div>`;
}

document.addEventListener('click', e => {
  const tr = e.target && e.target.closest ? e.target.closest('tr.prov') : null;
  if (tr) showProvenance(tr.dataset.t, tr.dataset.r);
});

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
  // With a case open, clicking a node asks about *this case*, not about the
  // design in general. The design view is one click away and always was; what
  // was missing is the answer to "what did this case put here".
  if (GV.source==='case' && GV.caseId) return showCaseNode(id, n);
  return n.type==='role' ? showRole(id) : showArtefact(id);
}

function showCaseNode(id, n){
  const c = CASES.find(x=>x.id===GV.caseId);
  const back = `<div class="link" onclick="showCase('${GV.caseId}')">&larr; ${esc(c.id)}</div>`;

  if (n.type === 'role') {
    const mine = e => e[0]===id;
    document.getElementById('phead').innerHTML =
      back + `<h2>${esc(n.label)}</h2><span class="sig">in ${esc(c.id)},
        mode <b>${esc(c.mode)}</b></span>`;
    document.getElementById('pbody').innerHTML = `
      <h4>required of it</h4>${edgeList(c.edges.required.filter(mine),'req')}
      <h4>forbidden to it</h4>${edgeList(c.edges.forbidden.filter(mine),'forb')}
      <h4>everything the mode offers</h4>${edgeList(c.edges.offered.filter(mine))}
      <p class="sig link" onclick="showRole('${id}')">read its composed prompt &rarr;</p>`;
    return;
  }

  const seeded = (c.situation.seeded||[]).find(sd=>sd.artefact===id);
  const expected = Object.entries((c.expect||{}).writes||{});
  const denied = ((c.forbidden||{}).writes||[]);
  const rows = seeded ? seeded.sample.map(r=>
    `<pre>${esc(JSON.stringify(r,null,1))}</pre>`).join('') : '';

  document.getElementById('phead').innerHTML =
    back + `<h2>${esc(n.label)}</h2><span class="sig">${
      seeded ? `${seeded.rows} row(s) seeded across ${esc(seeded.tables.join(', '))}`
             : 'nothing seeded here'}</span>`;
  document.getElementById('pbody').innerHTML = `
    <h4>seeded by the case</h4>
    ${rows || '<p class="empty">no rows — this artefact is scenery for this case</p>'}
    <h4>expected of it</h4>
    ${expected.length ? expected.map(([t,spec])=>
        `<div class="row"><span class="tag req">write</span> ${esc(t)}
         <span class="sig">${esc(JSON.stringify(spec))}</span></div>`).join('')
      : '<p class="empty">nothing</p>'}
    <h4>forbidden</h4>
    ${denied.length ? denied.map(t=>
        `<div class="row"><span class="tag forb">write</span> ${esc(t)}</div>`).join('')
      : '<p class="empty">nothing</p>'}
    ${(c.situation.links||[]).some(l=>l[0]===id||l[1]===id)
      ? `<h4>linked</h4>` + (c.situation.links||[]).filter(l=>l[0]===id||l[1]===id)
          .map(l=>`<div class="row">${esc(l[0])} <span class="sig">&rarr;</span>
             ${esc(l[1])} <span class="sig">${esc(l[2])}</span></div>`).join('')
      : ''}`;
}

// ---------------------------------------------------------------- roles

// Tools, one line each in call shape: `code.commit(msg, amend)`. Parameters
// explain themselves on hover — required or optional-with-default — and the
// line unfolds into the implementation's own docstring, served off the same
// functions the sandbox dispatches to. A tool with nothing to say stays a
// flat line rather than a drawer that opens onto nothing.
function toolList(tools, sigs) {
  // Older payloads carry only signature strings; parse enough to keep lines.
  if ((!tools || !tools.length) && sigs && sigs.length)
    tools = sigs.map(s => {
      const m = String(s).match(/^([^(]+)\((.*)\)$/);
      return {name: m ? m[1] : String(s), doc: '',
              params: m && m[2] ? m[2].split(',').map(p =>
                ({name: p.trim().split('=')[0], default:
                  p.includes('=') ? p.split('=').slice(1).join('=').trim() : null}))
              : []};
    });
  if (!tools || !tools.length) return '<div class="empty">none</div>';
  return tools.map(t => {
    const params = (t.params||[]).map(p =>
      `<span class="tparam" data-tip="${attr(p.default != null
        ? `${p.name} — optional, defaults to ${p.default}`
        : `${p.name} — required`)}">${esc(p.name)}</span>`
    ).join('<span class="lnk">, </span>');
    const line = `<span class="tname">${esc(t.name)}</span><span class="lnk">(</span>${
      params}<span class="lnk">)</span>`;
    const doc = (t.doc||'').trim();
    return doc
      ? `<details class="tline"><summary>${line}</summary>
         <div class="tdoc">${esc(doc)}</div></details>`
      : `<div class="tline flat">${line}</div>`;
  }).join('');
}

// `architect <- code (tree)` back into its parts, so a coverage row can be
// joined against the case files' edge tuples.
function parseEdge(s) {
  const m = String(s).match(/^(\S+) (<-|->|=>) (\S+) \((.+)\)$/);
  if (!m) return null;
  return {role: m[1],
          kind: m[2] === '<-' ? 'reads' : m[2] === '->' ? 'writes' : 'messages',
          target: m[3], verb: m[4]};
}

async function openCase(id) {
  if (!CASES.length) {
    try { CASES = await (await fetch('/cases.json')).json(); } catch {}
  }
  showCase(id);
}

async function showRole(id) {
  phead(id, 'loading…');
  const r = await (await fetch(`/role.json?id=${encodeURIComponent(id)}`)).json();
  // The case files, for joining coverage rows to the cases that earn them.
  if (!CASES.length) {
    try { CASES = await (await fetch('/cases.json')).json(); } catch {}
  }

  // "Architect ROLE" — the kind rides in the title, and the one header action
  // is an icon with its explanation on hover, not a sentence of chrome.
  document.getElementById('phead').innerHTML = `<div class="phrow">
    <h2>${esc(r.label)} <span class="kind">role</span></h2>
    <span class="phact" onclick="gvInhabit('${esc(id)}')"
      data-tip="show only what this role can reach — the namespace its sessions are actually handed">
      <svg width="13" height="13" viewBox="0 0 14 14"><circle cx="7" cy="7" r="4.5"
        fill="none" stroke="currentColor" stroke-width="1.4"/>
        <path d="M7 0 L7 3 M7 11 L7 14 M0 7 L3 7 M11 7 L14 7"
        stroke="currentColor" stroke-width="1.4"/></svg></span></div>`;

  const roledef = group('ROLE DEFINITION',
    sec('Core prompt', `${(r.base_prompt||'').length} chars`,
        `<pre>${esc(r.base_prompt)}</pre>`) +
    sec('Tool definitions', r.working_set.length,
        toolList(r.tools_info, r.working_set)));

  const sessionTypes = group('SESSION TYPES',
    Object.entries(r.modes).map(([m,v])=>sec(
      m, `${v.tools.length} tools`,
      `<b class="sig">Prompt</b>
       <pre>${esc(v.piece)}</pre>
       <b class="sig">Tool definitions</b>${toolList(v.tools_info, v.tools)}
       <details class="cfold"><summary>full composed prompt</summary>
         <pre>${esc(v.composed)}</pre></details>`)).join('')
    || '<div class="note">none beyond the role definition</div>');

  // Contact grammar: "to <role> it may <verbs>", connectives receding. The
  // derivation — which artefact makes the contact lawful — is the hover.
  const contacts = r.contacts.map(c=>{
    const why = c.clause==='ask'
      ? `lawful because ${r.label} reads ${c.because_reads.join(', ')}, which ${c.role} writes`
      : `lawful because ${c.role} reads ${c.because_writes.join(', ')}, which ${r.label} writes`;
    return `<div class="row" style="display:flex;align-items:baseline;gap:6px"
        data-tip="${attr(why)}">
      <span class="lnk">to</span>
      <span class="link" onclick="gvGoto('${esc(c.role)}')">${esc(c.role)}</span>
      <span class="lnk">it may</span>
      ${(c.verbs.length?c.verbs:['—']).map(v=>
        `<span class="vchip link" onclick="showEdge('${esc(id)}|${esc(c.role)}|messages')"
         >${esc(v)}</span>`).join('')}
    </div>`;
  }).join('');

  // Coverage in two drawers, and every tested edge names the case that earns
  // its green — matched against the cases' own required edges.
  const casesFor = e => !e ? [] : CASES.filter(c =>
    (c.edges && c.edges.required || []).some(t =>
      t[0]===e.role && t[1]===e.target && t[2]===e.kind && t[3]===e.verb));
  const tested = (r.coverage.exercised||[]).map(s=>{
    const linked = casesFor(parseEdge(s));
    return `<div class="row" style="display:flex;gap:8px;align-items:baseline">
      <span style="flex:1">${esc(s)}</span>
      ${linked.slice(0,3).map(c=>`<span class="link" style="font-size:11px"
         onclick="openCase('${attr(c.id)}')">${esc(c.id.replace(/^L\d+-\w+-/,''))}</span>`).join('')}
      ${linked.length>3?`<span class="sig">+${linked.length-3}</span>`:''}
    </div>`;
  }).join('');
  const untested = r.coverage.missing.map(s=>
    `<div class="row">${esc(s)}</div>`).join('');

  const miss = r.coverage.missing.length;
  const wiring = group('WIRING',
    sec('contacts', r.contacts.length, contacts||'<div class="empty">none</div>', true) +
    sec('reads / writes', `${r.reads.length}r ${r.writes.length}w`,
      `<b class="sig">reads</b><div>${r.reads.map(a=>
        `<span class="link" onclick="gvGoto('${a}')">${esc(a)}</span>`).join(' · ')||'—'}</div>
       <b class="sig">writes</b><div>${r.writes.map(a=>
        `<span class="link" onclick="gvGoto('${a}')">${esc(a)}</span>`).join(' · ')||'—'}</div>`) +
    sec('coverage', `${r.coverage.covered}/${r.coverage.total}`,
      `<details class="nsec"${miss ? '' : ' open'}><summary>tested
         <span class="sig">${r.coverage.covered}</span></summary>
         ${tested || '<div class="empty">nothing exercised yet</div>'}</details>
       <details class="nsec"${miss ? ' open' : ''}><summary>untested
         <span class="${miss?'fail':'pass'}">${miss || 'none'}</span></summary>
         ${untested || '<div class="pass" style="padding:4px 0">every edge exercised</div>'}
       </details>`, true));

  // Sessions: an aligned summary row that unfolds into the whole session —
  // calls in order, writes, and the verbatim transcript — fetched only when
  // opened, because twenty-five transcripts is not a panel payload.
  const sessions = r.sessions.map(s=>`
    <details class="sec" data-sess="${attr(s.id)}">
      <summary><span class="srow" style="border-bottom:0;padding:0">
        <span class="${s.committed?'pass':'fail'}">${s.committed?'✓':'✗'}</span>
        <span>${esc(s.mode)}</span>
        <span class="sig">${esc(s.model||'—')}</span>
        <span class="sig" style="text-align:right">${s.calls.length} calls</span>
        <span class="sig" style="text-align:right">${s.writes.length
          ? `${s.writes.length} writes` : '—'}</span></span></summary>
      <div class="body"><p class="empty">loading…</p></div>
    </details>`).join('') || '<div class="empty">no sessions yet</div>';

  const state = group('STATE', sec('sessions', r.sessions.length, sessions, true));

  // One sentence per line: the notes are declarative sentences, and a
  // paragraph block made them read as one run-on claim.
  P().innerHTML = `<div class="note">${esc(r.note).replace(/\.\s+/g,'.<br>')}</div>`
    + roledef + sessionTypes + wiring + state;
  wireSessionFolds();
}

// The full session on demand: opened, it fetches once and renders whole.
function wireSessionFolds() {
  P().querySelectorAll('details[data-sess]').forEach(d => {
    d.addEventListener('toggle', async () => {
      if (!d.open || d.dataset.loaded) return;
      d.dataset.loaded = '1';
      const body = d.querySelector('.body');
      try {
        const sx = await (await fetch(
          `/session.json?id=${encodeURIComponent(d.dataset.sess)}`)).json();
        body.innerHTML = sessionBody(sx);
      } catch { body.innerHTML = '<div class="fail">could not load</div>'; }
    });
  });
}

function sessionBody(sx) {
  if (!sx || !sx.found) return '<div class="empty">no record of this session</div>';
  const calls = (sx.calls||[]).map(c=>`<div class="row" style="display:flex;gap:8px">
      <span class="sig" style="width:24px;text-align:right">${c.seq}</span>
      <span>${esc(c.fn)}</span>
      <span class="sig" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap"
        title="${attr(c.args_summary||'')}">${esc(c.args_summary||'')}</span>
    </div>`).join('') || '<div class="empty">no calls</div>';
  const writes = (sx.writes||[]).length
    ? sx.writes.map(w=>`<span class="vchip">${esc(w.table_name)}:${esc(w.row_id)}</span>`).join(' ')
    : '<span class="empty">nothing</span>';
  const turns = (sx.turns||[]).map((t,i)=>`
    <details class="nsec"${i===0?' open':''}><summary>turn ${t.seq ?? i+1}
      <span class="sig">${t.ms ? `${t.ms} ms` : ''}</span></summary>
      ${t.system?`<b class="sig">system</b><pre class="brief">${esc(t.system)}</pre>`:''}
      <b class="sig">user</b><pre class="brief">${esc(t.user||'')}</pre>
      <b class="sig">completion</b><pre class="brief">${esc(t.completion||'')}</pre>
    </details>`).join('');
  return `
    <div class="row"><span class="lnk">woken by</span> ${esc(sx.trigger_msg||'a tick')}
      <span class="lnk" style="margin-left:10px">prompt</span>
      <span class="sig">${esc(String(sx.prompt_hash||'').slice(0,10) || '—')}</span></div>
    <b class="sig">calls, in order</b>${calls}
    <b class="sig" style="display:block;margin-top:8px">writes</b>
    <div style="display:flex;flex-wrap:wrap;gap:4px;padding:4px 0">${writes}</div>
    <b class="sig" style="display:block;margin-top:8px">transcript${
      (sx.turns||[]).length ? ` — ${sx.turns.length} round-trip(s), verbatim` : ''}</b>
    ${turns || '<div class="empty">no transcript recorded for this session</div>'}`;
}

// ---------------------------------------------------------------- artefacts
async function showArtefact(id) {
  phead(id, 'loading…');
  const a = await (await fetch(`/artefact.json?id=${encodeURIComponent(id)}`)).json();
  const isJournal = a.contact === false;

  // STATE first for artefacts: the rows are what you came for.
  const tables = (a.tables||[]).map(t=> t.error
    ? `<div class="fail">${esc(t.error)}</div>`
    // Rows are clickable now. Everything needed to answer "why is this here"
    // was already served and there was no path through it, so the path is the
    // row itself: click it and you get the session, the wake, and the cause.
    : sec(t.name, `${t.count} rows`,
          rowTable(t.name, t.rows, t.columns), t.count>0 && t.count<50)).join('');

  const state = group('STATE',
    (tables || '<div class="empty">no rows yet</div>') +
    ((a.receipts||[]).length
      ? sec('recent writes', a.receipts.length,
            table(a.receipts, ['role','table_name','row_id']))
      : ''));

  const wiring = group('WIRING',
    sec('who touches it', (a.operations||[]).length,
        table(a.operations, ['role','type','verb','rows','depth','actor']), true) +
    (((a.refs_out||[]).length + (a.refs_in||[]).length)
      ? sec('refs', (a.refs_out||[]).length+(a.refs_in||[]).length,
          `<b class="sig">points at</b>${table(a.refs_out,['to','rel','card'])}
           <b class="sig">pointed at by</b>${table(a.refs_in,['from','rel','card'])}`)
      : ''));

  // Same header grammar as roles: "Brief RECORD", the kind riding in the
  // title, and the one action — the cascade — as an icon explained on hover.
  const gnode = GV.graph.nodes.find(x=>x.id===id);
  const kind = gnode ? kindOf(gnode) : 'record';
  document.getElementById('phead').innerHTML = `<div class="phrow">
    <h2>${esc(a.label)} <span class="kind">${esc(kind)}</span></h2>
    <span class="phact" onclick="showBlast('${esc(id)}')"
      data-tip="what changing this would wake — the cascade, in the order owners are summoned">
      <svg width="13" height="13" viewBox="0 0 14 14"><circle cx="3.5" cy="7" r="1.6"
        fill="currentColor"/><path d="M7 3.5 a5 5 0 0 1 0 7 M9.8 1.8 a7.5 7.5 0 0 1 0 10.4"
        fill="none" stroke="currentColor" stroke-width="1.3"/></svg></span></div>`;
  P().innerHTML =
    `<div class="note">${esc(a.note).replace(/\.\s+/g,'.<br>')}
      ${isJournal?`<div class="sub sig"><b>Fact artefact.</b> ${esc(a.contact_why)}</div>`:''}
     </div>${state}${wiring}`;
}

// ---------------------------------------------------------------- edges
async function showEdge(data) {
  showTab('detail');
  const [s,t,type]=data.split('|');
  // Selecting an edge selects it on the map: the edge and its two ends at
  // full light, everything else receded — the same contract a node click has.
  GV.edgeSel = {s, t, type};
  GV.focus = null;
  gvDraw();
  if (typeof syncHash === 'function') syncHash();
  const e = await (await fetch(
    `/edge.json?s=${encodeURIComponent(s)}&t=${encodeURIComponent(t)}&type=${type}`)).json();
  if (e.error){ phead('—', esc(e.error)); P().innerHTML=''; return; }

  phead(`${s} → ${t}`, `${esc(type)} · ${e.covered
    ? '<span class="pass">covered by a test</span>'
    : '<span class="fail">no test exercises this</span>'}`,
    `<span class="link" onclick="gvGoto('${s}')">go to ${esc(s)}</span> ·
     <span class="link" onclick="gvGoto('${t}')">go to ${esc(t)}</span>`);

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
           <b class="sig">calls</b><pre>${esc(p.calls.join('\n')||'none')}</pre>
           <b class="sig">writes</b><pre>${esc(p.writes.join('\n')||'none')}</pre>`, true)
      : `<div class="empty">${m.status==='open'
          ? 'nothing has answered this yet' : 'no session recorded'}</div>`);
}

async function showBlast(id) {
  const b = await (await fetch(`/blast.json?id=${encodeURIComponent(id)}`)).json();
  b.root = id;                  // the status line names what the cascade is from
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
  el.innerHTML = `<div class="dd" id="ststory" style="margin-bottom:6px">${
      dd('ststory', GV.stories.map((s,i)=>
        ({v:String(i), label:s.name, on:i===GV.storyIx})))}</div>
    <div class="stnav"><button id="stprev">‹ prev</button>
      <span class="sig" id="stpos"></span>
      <button id="stnext">next ›</button></div>
    <div id="ststeps"></div>`;
  document.getElementById('stprev').onclick = ()=>{
    GV.stepIx=Math.max(0,GV.stepIx-1); gvDraw(); syncStoryTab();};
  document.getElementById('stnext').onclick = ()=>{
    GV.stepIx=Math.min(gvSteps().length-1,GV.stepIx+1); gvDraw(); syncStoryTab();};
  ddWire('ststory', v=>{ GV.storyIx=+v; setLens('story'); });
  syncStoryTab();
}

function syncStoryTab() {
  // The subtab is restored from localStorage at parse time, before the first
  // load has resolved — nothing to sync against yet, and the load ends by
  // building this tab anyway.
  if (!GV.stories || !GV.trace) return;
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
  // Clicking a step is asking to see it. Under any lens without steps — not
  // just coverage, which was the only one handled — the click used to change
  // the highlight and nothing else, which reads as a broken stepper.
  if (GV.source!=='story' && GV.source!=='run') setLens('story');
  GV.stepIx=i; gvDraw(); syncStoryTab();
}

// ---------------------------------------------------------------- chrome
let view='graph', ptab='detail', fingerprint=null, lastSig='', stalled=0;

function showTab(t, quiet){
  // Showing a subtab is asking something of the inspector, so it opens the
  // panel — except when restoring the remembered tab at load, where nothing
  // was asked yet and the canvas keeps the whole width.
  if (!quiet) panelOpen();
  ptab=t;
  document.querySelectorAll('[data-ptab]').forEach(b=>
    b.classList.toggle('on', b.dataset.ptab===t));
  ['detail','story','cases','coverage'].forEach(n=>
    document.getElementById('p'+n).style.display = t===n?'block':'none');
  try{ localStorage.setItem('rota.ptab', t); }catch{}
  if (t==='story')    syncStoryTab();
  if (t==='cases')    loadCases();
  if (t==='coverage') loadCoverage();
}

function selectView(v){
  view = v;
  document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('on', x.dataset.view===v));
  ['graph','live','progress'].forEach(n=>
    document.getElementById(n).classList.toggle('on', n===v));
  // Which tab you were on survives a reload. The progress view is the one
  // people leave open, and the fingerprint watcher reloads the page whenever
  // the source changes -- so without this, every edit to the tree bounced you
  // back to the graph.
  try{ localStorage.setItem('rota.view', v); }catch{}
  if (v==='progress') loadProgress();
  if (v==='live') refresh();     // paint now, not at the next poll tick
  if (typeof syncHash === 'function') syncHash();
}

document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>selectView(b.dataset.view));

try{
  const saved = localStorage.getItem('rota.view');
  if (saved && document.getElementById(saved)) selectView(saved);
  const savedTab = localStorage.getItem('rota.ptab');
  if (savedTab && document.getElementById('p'+savedTab)) showTab(savedTab, true);
}catch{}

async function refresh() {
  let s; try{ s = await (await fetch('/state.json')).json(); }
  catch{ st_.textContent='server gone'; st_.className='state stuck'; return; }

  const tips=s.frontier.tips, preds=s.frontier.predicates;
  const claims=s.claims||[];
  const sig=JSON.stringify([tips,preds,s.versions]);
  if (sig===lastSig) stalled++; else {stalled=0; lastSig=sig;}
  // Stillness is the server's fact, not this page's. The old counter tallied
  // polls with an unchanged snapshot — a number that reset to zero on every
  // reload (the fingerprint reloads this page on every source edit), changed
  // meaning with the poll cadence, and read "moving" for a session busy
  // writing tool calls. `quiet_secs` is seconds since anything was written to
  // the run, off the file's own clock; the poll counter remains only as the
  // fallback against a server that predates it.
  const quiet = typeof s.quiet_secs === 'number' ? s.quiet_secs : null;
  // Three kinds of "nothing is moving", and only one is a fault. Work pending
  // and changing is a system in motion. Work pending, still, with a claim
  // held is a session wedged mid-flight — stuck, and red; a slow local turn
  // is 40–90s of legitimate silence, so STUCK waits out two of them. Work
  // pending, still, with NO claim held is not stuck at all: nothing is
  // running this database, and the fix is a runner, not a debugger.
  const busy=tips.length+preds.length>0;
  const stuck=busy&&claims.length>0&&(quiet!==null?quiet>180:stalled>6);
  const unrun=busy&&!claims.length&&(quiet!==null?quiet>30:stalled>6);
  st_.textContent = stuck?'STUCK':unrun?'NO RUNNER'
                   :busy?'WORK PENDING':'QUIESCENT';
  st_.className='state '+(stuck?'stuck':busy?'busy':'idle');
  const fmt = se => se>=5400?Math.round(se/3600)+'h':se>=90?Math.round(se/60)+'m'
                   :Math.round(se)+'s';
  tick_.textContent = `${tips.length} tip · ${preds.length} predicate`
    + (quiet!==null ? (quiet>=30?` · last write ${fmt(quiet)} ago`:'')
                    : (stalled?` · still for ${stalled}`:''))
    + (unrun?' · no claim held — start a runner to advance it':'');

  // Header hover: the detail without the real estate.
  //
  // These populate the `.pop` panels. They used to *also* set `title`, which is
  // why hovering produced two things at once — an empty styled box, because
  // nothing ever filled it, and the OS tooltip a second later carrying the
  // content the box was supposed to have. One of them had to go, and the
  // native tooltip is the one that cannot be laid out, coloured or clicked.
  const rows = xs => xs.length ? xs.join('') : '<div class="pnone">none</div>';

  // Each predicate explains itself on hover, off the registry's own
  // docstring — served, never restated here where it could drift. Wakes
  // arrive structured: role plus the refs that tripped it, so a firing row
  // says not just that term_collision fires but *about which rows*.
  const pmeta = s.predicate_meta || {};
  const wakesOf = w => (w||[]).map(x =>
    typeof x === 'string' ? {role:x, refs:[], detail:''} : x);
  const wakeLabel = x => {
    const refs = (x.refs||[]).length ? x.refs
               : (x.detail ? [x.detail] : []);
    return esc(x.role) + (refs.length
      ? ` ← ${esc(refs.slice(0,3).join(', '))}${refs.length>3?` +${refs.length-3}`:''}`
      : '');
  };
  // One predicate list from two sources. The per-tick sweep names the tick
  // functions, mostly quiet; the frontier's wakes come from the wider
  // registry — term_collision fires through the frontier and was never in
  // the tick list, so the pill counted a predicate the popover could not
  // show. Merged and deduped (a tick that fires appears in both), firing
  // rows first.
  const predRows = {};
  for (const [n, w] of Object.entries(s.predicate_status))
    predRows[n] = wakesOf(w);
  for (const p of preds) {
    const n = String(p.kind || '').replace(/^tick:/, '') || 'frontier';
    const list = (predRows[n] = predRows[n] || []);
    const key = p.role + '|' + (p.refs || []).join(',');
    if (!list.some(x => x.role + '|' + (x.refs || []).join(',') === key))
      list.push({role: p.role, refs: p.refs || [], detail: p.detail || ''});
  }
  const predEntries = Object.entries(predRows)
    .sort((a, b) => (b[1].length ? 1 : 0) - (a[1].length ? 1 : 0));

  document.getElementById('pop-tick').innerHTML =
    `<h4>frontier tips</h4>` +
    rows(tips.map(t=>`<div class="prow"><span>${esc(t.role)}</span>
      <em>← ${esc(t.verb)}</em></div>`)) +
    `<h4>predicates</h4>` +
    rows(predEntries.map(([n,wk])=>{
      const m = pmeta[n];
      return `<div class="prow" data-tip="${attr(m ? m.why : '')}"
        data-tipmeta="${attr(m ? `wakes ${m.wakes} · band ${m.band}` : '')}">
        <span class="${wk.length?'pon':'poff'}">${wk.length?'●':'○'}
        ${esc(n)}</span><em>${wk.map(wakeLabel).join(' · ')}</em></div>`;
    }));

  // The pill's hover justifies the pill: what makes the verdict true right
  // now, and what would change it. The row counts that used to live here
  // answered a question nobody was asking of a *status* pill.
  const verdict = st_.textContent;
  const whySentence =
      stuck ? `Work is pending and nothing has been written for ${fmt(quiet||0)},
        while a claim is held — the session below is wedged mid-flight.
        Its transcript is the place to look.`
    : unrun ? `Work is pending, nothing has been written for ${fmt(quiet||0)},
        and no claim is held: nothing is running this database.
        Starting a runner (rota run) advances it.`
    : busy  ? `Work is pending and being worked${claims.length
                ? ' — a claim is held' : ''}${quiet!==null && quiet<30
                ? `; last write ${fmt(quiet)} ago` : ''}.`
    :         `The frontier is empty: no message tip, no predicate firing.
        Nothing to do until something writes.`;
  const pendingRows = [
    ...tips.map(t => `${esc(t.role)} ← ${esc(t.verb)}`),
    ...predEntries.filter(([,wk]) => wk.length).map(([n,wk]) =>
      esc(n) + ((wk[0].refs||[]).length
        ? ` ← ${esc(wk[0].refs.slice(0,2).join(', '))}` : '')),
  ];
  document.getElementById('pop-state').innerHTML =
    `<h4>why ${esc(verdict)}</h4>
     <div style="max-width:300px;line-height:1.55">${whySentence}</div>` +
    (pendingRows.length ? `<h4>pending</h4>` +
      rows(pendingRows.map(b=>`<div class="prow"><span>${b}</span></div>`)) : '') +
    (claims.length ? `<h4>claims held</h4>` +
      rows(claims.map(c=>`<div class="prow"><span>${esc(c.role)}</span>
        <em>${esc(c.session_id)}${c.message_id?` ← ${esc(c.message_id)}`:''}</em></div>`)) : '') +
    (quiet !== null ? `<h4>last write</h4>
      <div class="prow"><span>${fmt(quiet)} ago</span>
        <em>off the file's own clock</em></div>` : '');

  // Everything above feeds the header, which is on every tab. Everything
  // below paints the live grid, which is not — and painting a hidden grid is
  // work spent making nothing different.
  if (view !== 'live') return;

  const set=(id,html)=>{const e=document.getElementById(id); if(e) e.innerHTML=html;};
  set('tips', table(tips,['role','verb','message']));
  set('preds', predEntries.map(([n,wk])=>{
    const m = pmeta[n];
    const firing = wk.map(x =>
      `<div class="sub" style="margin-left:16px">${wakeLabel(x)}</div>`).join('');
    return `<div class="${wk.length?'':'muted'}" style="margin-bottom:7px">${
        wk.length?'●':'○'} ${esc(n)}
      ${firing}
      ${m?`<div class="sig sub">${esc(m.why)}${m.wakes
        ?` <span class="empty">— wakes ${esc(m.wakes)}</span>`:''}</div>`:''}</div>`;
  }).join(''));
  set('sessions', table(s.sessions,['id','role','mode','committed','model']));
  set('receipts', table(s.receipts,['role','table_name','row_id']));
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

// A popover you can enter, not just glimpse. The panel opens ~20px below its
// trigger, and the old wiring closed it the moment the pointer left the
// trigger — the gap was a moat, and `matches(':hover')` at mouseleave time
// races the event order, so the predicate list closed under the cursor on
// the way to it. Closing now waits a beat, and entering the panel cancels
// it; a transparent bridge in the CSS spans the gap so the wait is rarely
// even needed.
const POPS = [[st_, 'pop-state'], [tick_, 'pop-tick']];
for (const [el, pop] of POPS) {
  const box = document.getElementById(pop);
  let hide = null;
  const open = () => {
    clearTimeout(hide); hide = null;
    // One popover at a time: moving from the pill to the counter swaps
    // panels in the same instant, instead of two lingering side by side.
    for (const [, other] of POPS)
      if (other !== pop) document.getElementById(other).classList.remove('on');
    const r = el.getBoundingClientRect();
    box.style.left = Math.max(8, r.left) + 'px';
    box.classList.add('on');
  };
  const close = () => {
    clearTimeout(hide);
    // One breath, not a grace period. A synchronous close hides the panel
    // before its own mouseenter can fire (the original bug), and inside the
    // trigger's mouseleave handler `:hover` lies — but by the time a timer
    // runs, every event from that one pointer move has landed and `:hover`
    // answers truthfully. The bridge does the real work of keeping the
    // crossing unbroken; 60ms is below what a hand can feel.
    hide = setTimeout(() => {
      if (!box.matches(':hover') && !el.matches(':hover'))
        box.classList.remove('on');
    }, 60);
  };
  el.addEventListener('mouseenter', open);
  el.addEventListener('mouseleave', close);
  box.addEventListener('mouseleave', close);
}

async function loadCoverage(){
  const c = await (await fetch('/coverage.json')).json();
  document.getElementById('coveragebody').innerHTML =
    `<h3>${c.covered}/${c.total} edges (${c.percent.toFixed(0)}%)</h3>
     <p class="sig"><span class="link" onclick="setLens('coverage')">paint this
       on the graph &rarr;</span></p>` +
    Object.entries(c.by_role).map(([role,[cov,miss]])=>
      `<div class="barwrap"><span style="width:90px">${esc(role)}</span>
        <span class="sig" style="width:56px">${cov}/${cov+miss}</span>
        ${gbar(cov, cov+miss)}</div>`).join('') +
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

// ---------------------------------------------------------------- inspector
// The right panel starts closed: until something is asked of it, the canvas
// owns the width, and a rail stays on the edge saying what is folded there.
// It opens when it is used — a subtab clicked, a node inspected, the handle
// dragged out — and its width survives as the width it reopens to. The open
// state itself is deliberately not persisted: "collapsed on load" is the
// contract, not "however it was left".
const PANEL = {open:false, w:430};
try { const s = JSON.parse(localStorage.getItem('rota.panel')||'{}');
      if (+s.w >= 280) PANEL.w = +s.w; } catch {}

function panelApply(){
  const wrap=document.getElementById('gwrap'), pan=document.getElementById('gpanel');
  if(!wrap||!pan) return;
  pan.classList.toggle('closed', !PANEL.open);
  wrap.style.gridTemplateColumns = `1fr 6px ${PANEL.open?PANEL.w:34}px`;
  const btn=document.getElementById('pcollapse');
  if(btn){ btn.innerHTML = PANEL.open ? '&raquo;' : '&laquo;';
           btn.setAttribute('title',
             PANEL.open ? 'collapse the panel' : 'expand the panel'); }
}
function panelSave(){
  try{ localStorage.setItem('rota.panel', JSON.stringify({w:PANEL.w})); }catch{}
}
function panelOpen(){
  if (PANEL.open) return;
  PANEL.open = true; panelApply();
  if (window.gvDraw) gvDraw();          // the canvas width just changed
}
function panelToggle(){
  PANEL.open = !PANEL.open; panelApply();
  if (window.gvDraw) gvDraw();
}

(function(){
  const h=document.getElementById('phandle');
  const pan=document.getElementById('gpanel');
  const btn=document.getElementById('pcollapse');
  if (btn) btn.onclick = e=>{ e.stopPropagation(); panelToggle(); };
  if (pan) pan.addEventListener('click', ()=>{ if(!PANEL.open) panelOpen(); });
  let d=null;
  if (h) h.onmousedown=e=>{
    d={x:e.clientX, w:PANEL.open?document.getElementById('gpanel').offsetWidth:34};
    e.preventDefault();};
  window.addEventListener('mousemove',e=>{ if(!d) return;
    const raw = d.w-(e.clientX-d.x);
    // Dragging the handle out of a closed panel is opening it by hand.
    if (!PANEL.open) { if (raw < 60) return; PANEL.open = true; }
    PANEL.w = Math.min(900, Math.max(280, raw));
    panelApply(); gvFit&&gvFit(); gvDraw&&gvDraw();});
  window.addEventListener('mouseup',()=>{ if(d) panelSave(); d=null;});
  panelApply();
})();

document.querySelectorAll('[data-ptab]').forEach(b=>b.onclick=()=>showTab(b.dataset.ptab));
refresh();
// The idle/busy/stuck pill is in the header, on every tab — so it is fed on
// every tab: quickly while the live grid is visible, at a walk otherwise. It
// used to update only while the live tab polled, which made QUIESCENT a claim
// about whenever you last looked at live.
let pillTick = 0;
setInterval(()=>{if(view==='live' || ++pillTick % 4 === 0) refresh();},1500);

// ------------------------------------------------------------- run selector
// Which database this page is about, and the door to its siblings — without
// restarting the server. The mtime shown is the one wall-clock fact a run
// has: rows carry order, not time, by law, so recency lives on the file.
const ago = s => {
  const d = Date.now()/1000 - s;
  return d < 90 ? 'just now' : d < 5400 ? Math.round(d/60)+'m ago'
    : d < 129600 ? Math.round(d/3600)+'h ago' : Math.round(d/86400)+'d ago';
};

async function loadRuns(){
  try {
    const r = await (await fetch('/runs.json')).json();
    const runs = r.runs || [];
    const el = document.getElementById('rundb');
    if (!el || !runs.length) return;
    el.innerHTML = dd('rundb', runs.map(x =>
      ({v:x.name, label:`${x.name} · ${ago(x.mtime)}`, on:!!x.current})));
    ddWire('rundb', async name => {
      const res = await fetch(`/run?name=${encodeURIComponent(name)}`,
                              {method:'POST'});
      // A full reload, not a repaint: every cache, signature and subscription
      // on this page is a claim about the old database.
      if (res.ok) location.reload();
      else alert(`could not open ${name}: ` + (res.status === 409
        ? 'behind schema — rebuild it or pick another run' : 'not found'));
    });
  } catch {}
}
loadRuns();

// ----------------------------------------------------------------- tooltip
// The house tooltip. A native `title` waits half a second, paints in the
// OS's style, and cannot carry structure — this one is instant, set in the
// cockpit's own type, and there is exactly one of it, fed by whatever
// element under the pointer carries `data-tip` (with `data-tipmeta` as a
// dimmer second line). It never traps the pointer: pointer-events is off.
(function(){
  const tip = document.getElementById('tip');
  if (!tip) return;
  document.addEventListener('mouseover', e => {
    const t = e.target && e.target.closest ? e.target.closest('[data-tip]') : null;
    if (!t || !t.dataset.tip) { tip.style.display = 'none'; return; }
    tip.innerHTML = esc(t.dataset.tip) + (t.dataset.tipmeta
      ? `<div class="tipmeta">${esc(t.dataset.tipmeta)}</div>` : '');
    tip.style.display = 'block';
    // Below the row, clamped to the viewport; above it when there is no room.
    const r = t.getBoundingClientRect();
    const w = tip.offsetWidth, h = tip.offsetHeight;
    const x = Math.min(Math.max(8, r.left), window.innerWidth - w - 8);
    let y = r.bottom + 6;
    if (y + h > window.innerHeight - 8) y = r.top - h - 6;
    tip.style.left = x + 'px';
    tip.style.top = y + 'px';
  });
})();

// ---------------------------------------------------------------- url paths
// The address bar is the query — #/graph?lens=coverage&node=critic names a
// view completely enough to reopen it tomorrow or hand to someone — and the
// history is the trail: every selection change is an entry, so the browser's
// back and forward walk your inspection the way they walk pages. While a
// hash is being *applied* (load, back, forward), writes are replaceState so
// re-deriving the state never corrupts the trail being walked.
let navApplying = false;

function syncHash(){
  if (typeof history === 'undefined' || typeof location === 'undefined') return;
  if (!GV.graph) return;
  let h = '#/' + view;
  if (view === 'graph') {
    const q = [];
    if (GV.source !== 'design') q.push('lens=' + encodeURIComponent(GV.source));
    if (GV.caseId) q.push('case=' + encodeURIComponent(GV.caseId));
    if (GV.focus) q.push('node=' + encodeURIComponent(GV.focus));
    if (GV.inhabit) q.push('reach=' + encodeURIComponent(GV.inhabit));
    if (GV.edgeSel) q.push('edge=' + encodeURIComponent(
      `${GV.edgeSel.s}|${GV.edgeSel.t}|${GV.edgeSel.type}`));
    if (q.length) h += '?' + q.join('&');
  }
  if (location.hash === h) return;
  if (navApplying) history.replaceState(null, '', h);
  else history.pushState(null, '', h);
}

// Authoritative, both ways: state named in the hash is applied, state absent
// from it is cleared — without that, back reaches an address the picture
// refuses to match.
async function applyHash(){
  if (typeof location === 'undefined') return;
  const m = (location.hash || '').match(/^#\/(graph|live|progress)(?:\?(.*))?$/);
  if (!m) return;
  navApplying = true;
  try {
    selectView(m[1]);
    if (m[1] !== 'graph') return;
    const q = new URLSearchParams(m[2] || '');
    const caseId = q.get('case');
    if (caseId) {
      if (!CASES.length) {
        try { CASES = await (await fetch('/cases.json')).json(); } catch {}
      }
      if (CASES.some(c => c.id === caseId) && GV.caseId !== caseId)
        showCase(caseId);
    } else {
      const lens = q.get('lens') || 'design';
      if (GV.source !== lens) setLens(lens);
    }
    const node = q.get('node');
    GV.focus = (node && GV.layout && GV.layout[node]) ? node : null;
    const reach = q.get('reach');
    GV.inhabit = (reach && GV.layout && GV.layout[reach]) ? reach : null;
    const edge = q.get('edge');
    GV.edgeSel = null;
    gvDraw();
    if (edge) await showEdge(edge);
    else if (GV.focus) showNode(GV.focus);
  } finally {
    navApplying = false;
  }
  syncHash();
}
window.addEventListener('hashchange', applyHash);

// The trail's buttons live where the trail is walked: in the inspector bar.
(function(){
  const b = document.getElementById('pnavb'), f = document.getElementById('pnavf');
  if (b) b.onclick = () => history.back();
  if (f) f.onclick = () => history.forward();
})();

// The graph's "right now" rings — claims held, predicates firing — were a
// snapshot from page load: the live tab watched the database move while the
// picture beside it stood still. The overlay is re-fetched at a walk and the
// canvas repainted only when it actually changed, so an idle system costs an
// idle poll and nothing else.
let _trSig = null;
async function refreshTrace(){
  if (view !== 'graph' || !GV.trace) return;
  try {
    const tr = await (await fetch('/trace.json')).json();
    const sig = JSON.stringify(tr.overlay) + '|' + (tr.steps||[]).length;
    if (sig === _trSig) return;
    _trSig = sig;
    GV.trace = tr;
    gvLegend();                 // the "right now" key group comes and goes with it
    gvDraw();
  } catch {}
}
setInterval(refreshTrace, 5000);
// Progress moves at the speed of a model run, not a session, so it polls
// slowly. Left open during an L1 run it fills in as cases land.
setInterval(()=>{if(view==='progress') loadProgress();},5000);
setInterval(checkReload,1000);


// ---------------------------------------------------------------------------
// Progress. Every number is derived from something that exists for another
// reason -- the milestone's own checkboxes, the graph, the case files, the
// case-run log. Nothing here is a figure somebody types in and forgets.
// ---------------------------------------------------------------------------

function bar(done, total, cls){
  const pct = total ? 100*done/total : 0;
  return `<span class="bar"><i class="${cls||''}" style="width:${pct}%"></i></span>`;
}

// Progressive colour for a fraction that is a *judgement*, not just progress:
// a coverage bar at 30% is mostly-untested, and mostly-untested is what red
// already means on this cockpit. The ramp interpolates between the palette's
// own three judgement colours — stop, warn, ok — so no bar invents a fourth
// meaning. Milestone bars stay two-tone on purpose: being early in planned
// work is not a fault, and painting it red would say it was.
function gradeColor(f){
  const mix=(a,b,t)=>a.map((v,i)=>Math.round(v+(b[i]-v)*t));
  const stop=[232,116,106], warn=[230,178,90], ok=[85,209,135];
  f = Math.max(0, Math.min(1, f));
  const c = f<=0.5 ? mix(stop,warn,f*2) : mix(warn,ok,(f-0.5)*2);
  return `rgb(${c[0]},${c[1]},${c[2]})`;
}
function gbar(done, total){
  const pct = total ? 100*done/total : 0;
  return `<span class="bar"><i style="width:${pct}%;background:${
    gradeColor(total?done/total:0)}"></i></span>`;
}

let _pgSig = null;

async function loadProgress(){
  const p = await (await fetch('/progress.json')).json();

  // Repainting on a timer would reset the scroll position every five seconds,
  // which makes the one view people leave open the one view they cannot read.
  // The payload is fully derived, so an identical payload means nothing has
  // happened and there is nothing to repaint.
  const sig = JSON.stringify(p);
  if (sig === _pgSig) return;
  _pgSig = sig;
  const keep = document.getElementById('progress').scrollTop;
  setTimeout(()=>{ document.getElementById('progress').scrollTop = keep; }, 0);

  const ms = p.milestone;
  const shipped = ms.reduce((n,s)=>n+s.done,0), owed = ms.reduce((n,s)=>n+s.total,0);
  document.getElementById('pg-milestone').innerHTML =
    `<h3>${shipped}/${owed} across ${ms.length} stages</h3>` +
    ms.map(s=>{
      const done = s.done===s.total;
      return `<div class="barwrap" title="${esc(s.open_items.join(' · '))}">
        <span style="width:34px" class="sig">${esc(s.key)}</span>
        <span style="width:280px;${done?'':'color:var(--ink)'}">${esc(s.title)}</span>
        <span class="sig" style="width:44px">${s.done}/${s.total}</span>
        ${bar(s.done,s.total, done?'':'part')}</div>` +
        (s.open_items.length && !done
          ? `<div class="sig" style="margin:2px 0 8px 320px">${
              s.open_items.map(esc).join('<br>')}</div>` : '');
    }).join('');

  const c = p.coverage;
  document.getElementById('pg-coverage').innerHTML =
    `<h3>${c.cases} cases written</h3>
     <div class="barwrap"><span style="width:110px">prompt modes</span>
       <span class="sig" style="width:56px">${c.modes.done}/${c.modes.total}</span>
       ${gbar(c.modes.done,c.modes.total)}</div>` +
    (c.modes.missing.length
      ? `<div class="sig" style="margin:0 0 8px 118px">no case: ${
          c.modes.missing.map(esc).join(', ')}</div>` : '') +
    c.tiers.map(t=>`<div class="barwrap">
       <span style="width:110px">${t.tier} ${esc(t.label)}</span>
       <span class="sig" style="width:56px">${t.done}/${t.total}</span>
       ${gbar(t.done,t.total)}
       ${t.touched===undefined?'':`<span class="sig muted" style="margin-left:8px"
         title="also credited if a case merely touched the artefact -- a softer question"
         >${t.touched} by implication</span>`}</div>`).join('') +
    `<p class="muted">Modes are one case per prompt piece -- the unit a
      pass-rate drop is attributable to. Obligations are the finer grid the
      graph generates, and the long haul. L1 counts only operations a case
      names outright, because the goal is every tool call tested making the call.
      The greyed figure adds those merely implied by an artefact a case
      touched; the gap is how much of L1 is covered by accident.</p>`;

  const o = p.onboarding;
  // The same chips the live tab's artefact counts wear: one notation for
  // "a label and its number", wherever it appears.
  document.getElementById('pg-onboarding').innerHTML = o.indexed
    ? `<div class="counts">
        <span>grains indexed <b>${o.indexed}</b></span>
        <span>dependency edges <b>${o.edges}</b></span>
        <span>areas <b>${o.areas}</b></span>
        <span>surveyed <b>${o.surveyed}</b></span>
        <span>still under constraint zero <b>${o.under_zero}</b></span></div>`
    : `<p class="muted">Nothing onboarded in this database. Constraint zero
        covers an area until somebody has looked at it -- including a survey
        that finds nothing, which is a result.</p>`;

  const rows = p.l1.cases, t = p.l1.tally||{};
  const chip = s => `<span class="sig">${s}</span>`;
  document.getElementById('pg-l1').innerHTML =
    `<h3><span class="pass">${t.pass||0} passing</span> ·
       <span class="fail">${t.fail||0} failing</span> ·
       <span style="color:var(--accent)">${t.stale||0} stale</span> ·
       <span class="muted">${t['never run']||0} never run</span>
       ${p.l1.model?chip(p.l1.model):''}</h3>
     <p class="muted">A result recorded against a prompt that has since been
       edited is not evidence about the prompt in the tree, so it shows as
       stale rather than green. Green that means "green last week" is the
       number you stop checking.</p>` +
    ['pass','fail','stale','never run'].map(state=>{
      const group = rows.filter(r=>r.state===state);
      if(!group.length) return '';
      return `<h4 style="margin:12px 0 4px">${state} (${group.length})</h4>` +
        table(group.map(r=>({
          role:r.role, mode:r.mode, case:r.id,
          result:r.passed===null?'—':`${r.passed}/${r.runs}`,
          needs:r.threshold,
          why:(r.problems||[]).slice(0,2).join(' · ')
        })),['role','mode','case','result','needs','why']);
    }).join('');
}


// ---------------------------------------------------------------------------
// Cases. They were only ever visible by opening six YAML files, which made
// "what does this system actually check" a question you had to be inside the
// repository to ask -- for the most discussable artefact here.
// ---------------------------------------------------------------------------

// The open case lives in `GV.caseId` with the rest of the graph state, so the
// lens machinery can close it — as `CASE_ID`, a second owner over here, it
// outlived every lens change and kept a case option in a dropdown whose case
// was gone. `CASES` stays: it is a cache of data, not a piece of state.
let CASES = [];

// The list's highlight follows GV.caseId wherever it changes — including
// setLens clearing it when the lens moves off the case.
function caseListSync(){
  document.querySelectorAll('.crow').forEach(
    r => r.classList.toggle('on', r.dataset.case===GV.caseId));
}

function caseState(c){
  if(!c.history.length) return '';
  const p = c.history.filter(h=>h.passed).length;
  return p >= c.threshold ? 'pass' : 'fail';
}

async function loadCases(){
  if(!CASES.length) CASES = await (await fetch('/cases.json')).json();

  // Level, then role. The tiers ask different questions of the same wiring —
  // L1 whether a role can take an action, L2 whether it picks the right one
  // from a situation, L3 whether one role's message makes another act — so a
  // flat list by role puts three unrelated questions side by side.
  const tiers = {};
  CASES.forEach(c => {
    const tier = c.tier || (c.second ? 'T3' : 'T1');
    ((tiers[tier] ||= {})[c.role] ||= []).push(c);
  });

  const TIER = {T1:['L1', 'actions'], T2:['L2', 'situations'], T3:['L3', 'handoffs']};
  document.getElementById('clist').innerHTML =
    Object.keys(tiers).sort().map(tier => {
      const [name, what] = TIER[tier] || [tier, ''];
      const all = Object.values(tiers[tier]).flat();
      const green = all.filter(c => caseState(c)==='pass').length;
      const roles = Object.keys(tiers[tier]).sort().map(role => {
        const mine = tiers[tier][role];
        const ok = mine.filter(c => caseState(c)==='pass').length;
        const holdsRole = mine.some(c => c.id === GV.caseId);
        return `<details class="crole" ${holdsRole?'open':''}>
          <summary>${esc(role)}<span class="sig">${ok}/${mine.length}</span></summary>` +
        mine.map(c => {
          const st = caseState(c);
          const score = c.history.length
            ? `${c.history.filter(h=>h.passed).length}/${c.history.length}` : '—';
          return `<div class="crow ${c.id===GV.caseId?'on':''}" data-case="${esc(c.id)}">
            <span class="dot ${st}"></span>
            <span class="cid">${esc(c.id.replace(/^L\d-\w+-/,''))}</span>
            <span class="sig">${esc(c.mode)}</span>
            <span class="sig">${score}</span></div>`;}).join('') +
          `</details>`;}).join('');
      // Collapsed by default, except the tier holding the open case — so
      // "← all cases" lands you where you left rather than at three shut
      // drawers.
      const holds = all.some(c => c.id === GV.caseId);
      return `<details class="ctier" ${holds?'open':''}><summary>${name} · ${esc(what)}
        <span class="sig">${green}/${all.length}</span></summary>${roles}</details>`;
    }).join('');

  document.querySelectorAll('.crow').forEach(
    r => r.onclick = () => showCase(r.dataset.case));
}

function edgeList(edges, cls){
  if(!edges.length) return '<p class="empty">none</p>';
  return edges.map(e=>`<div class="row"><span class="tag ${cls||''}">${esc(e[2])}</span>
    ${esc(e[0])} <span class="sig">-${esc(e[3])}-&gt;</span> ${esc(e[1])}</div>`).join('');
}

function showCase(id){
  const c = CASES.find(x=>x.id===id); if(!c) return;
  GV.caseId = id;
  caseListSync();

  // Light it on the graph. `offered` is the mode's whole world for this
  // waking; `required` and `forbidden` are what the case asserts on top, and
  // the distinction between those two is the readable one on a picture.
  GV.caseEdges = c.edges;
  GV.caseSituation = c.situation;
  setLens('case');

  // The body of one run, filled into the summary row the history list already
  // drew. It used to be a whole second <details> — same summary, same verdict —
  // nested inside the first, so every run opened onto a copy of itself.
  const runBody = h => `
      ${h.problems.length?`<h4>problems</h4><pre>${esc(h.problems.join('\n'))}</pre>`:''}
      ${h.transcript.map(t=>t.say!==undefined
          ? `<h4>said</h4><pre>${esc(String(t.say).slice(0,4000))}</pre>`
          : t.errors ? `<h4>errors</h4><pre>${esc(t.errors.join('\n'))}</pre>`
          : `<h4>did</h4><pre>${esc(JSON.stringify(t,null,1))}</pre>`).join('')}`;
  const hist = c.history.length
    ? c.history.map((h,i)=>`<details class="sec"><summary>run ${h.run||i+1} — ${
        h.passed?'<span class="pass">pass</span>':'<span class="fail">fail</span>'}
        <span class="sig">${esc((h.problems[0]||'').slice(0,70))}</span></summary>
        <div class="body" id="run-${i}"><p class="empty">loading…</p></div>
      </details>`).join('')
    : '<p class="empty">never run</p>';

  showTab('detail');
  document.getElementById('phead').innerHTML =
    `<div class="link" onclick="showTab('cases')">&larr; all cases</div>` +
    `<h2>${esc(c.id)}</h2><span class="sig">${esc(c.tier)} · ${esc(c.role)}` +
    `${c.second?' → '+esc(c.second):''} · ${esc(c.mode)} · needs ` +
    `${c.threshold}/${c.runs}${c.repo?' · real checkout':''}` +
    `${c.onboarded?' · onboarded':''}</span>`;
  const seededBlocks = (c.situation.seeded||[]).map(sd=>
    fold(`${sd.artefact} — ${sd.rows} row(s)`,
      sd.sample.map(r=>`<pre>${esc(JSON.stringify(r,null,1))}</pre>`).join(''))
    ).join('') || '<p class="empty">nothing seeded</p>';

  document.getElementById('pbody').innerHTML = `
    <h4>situation</h4>
    <p class="pad"><b>${esc(c.woken)}</b>${c.refs.length
      ? ` <span class="sig">carrying ${c.refs.map(esc).join(', ')}</span>` : ''}</p>
    ${c.repo?`<p class="sig pad">in a real checkout${
       c.onboarded?', indexed and partitioned':''}</p>`:''}

    ${fold('role prompt', `<pre id="c-base" class="empty">loading…</pre>`)}
    ${fold(`mode prompt — ${c.mode}`, `<pre id="c-mode" class="empty">loading…</pre>`)}
    ${fold(`tools — ${c.tools.length}`,
       c.tools.map(t=>`<div class="row">${esc(t)}</div>`).join(''))}
    ${fold('message text', `<pre id="c-msg" class="empty">loading…</pre>`)}
    ${fold(`fixtured data — ${c.situation.given.length} given, ${
       c.situation.scaffolding.length} scaffolding`, seededBlocks, true)}
    ${c.situation.scaffolding.length?`<p class="sig pad">scaffolding:
       ${c.situation.scaffolding.map(esc).join(', ')} — seeded because the
       schema demands it, and unreachable from this role</p>`:''}
    ${c.situation.links.length?`<p class="sig pad">linked by
       ${c.situation.links.map(l=>esc(l[2])).join(', ')}</p>`:''}

    <h4>expectations</h4>
    <div class="pad"><b>required</b></div>${edgeList(c.edges.required,'req')}
    <div class="pad"><b>forbidden</b></div>${edgeList(c.edges.forbidden,'forb')}
    ${c.edges.impossible.length?`<div class="pad"><b>impossible by construction</b>
      </div><div class="sig pad">${c.edges.impossible.map(esc).join(', ')}</div>`:''}
    ${fold('the case as written', `<pre id="c-src" class="empty">loading…</pre>`)}

    <h4>runs</h4>${hist}`;

  // The words actually placed in front of the model, assembled by the same
  // functions a session uses. Fetched rather than served with every case: it
  // costs a database and a sandbox each, and nobody wants fifty-nine at once.
  fetch(`/message.json?id=${encodeURIComponent(c.id)}`)
    .then(r => r.json()).then(m => {
      const put = (id, text) => {
        const el = document.getElementById(id);
        if (el) { el.className = ''; el.textContent = text || '(none)'; }
      };
      put('c-msg', (m.user || '') + `

— ${m.tokens} tokens`);
      put('c-base', m.base);
      put('c-mode', m.mode_brief);
      put('c-src', m.source);
      (m.runs || []).forEach((h, i) => {
        const el = document.getElementById(`run-${i}`);
        if (el) el.innerHTML = runBody(h);
      });
    }).catch(()=>{});
}

// Collapsed by default: the panel's job is the shape of the case at a glance,
// and a role's standing brief is two thousand characters of prose that is the
// same for every case it appears in.
function fold(label, body, open){
  return body ? `<details class="sec" ${open?'open':''}>
    <summary>${esc(label)}</summary><div class="body">${body}</div></details>` : '';
}


// ------------------------------------------------------- why is this here
//
// The chain, backwards: row -> the session that wrote it -> what it was shown
// and did -> what woke it -> what caused that. Every piece was already served
// by this cockpit and there was no path through them; both times I have had to
// answer this for real, the method was a throwaway script joining four tables.
async function showProvenance(tableName, rowId) {
  showTab('detail');
  phead(rowId, 'why is this here? loading…');
  const d = await (await fetch(`/provenance.json?table=${
    encodeURIComponent(tableName)}&row=${encodeURIComponent(rowId)}`)).json();

  if (!d.found) {
    phead(rowId, tableName);
    P().innerHTML = `<div class="empty">${esc(d.note || 'no such row')}</div>`;
    return;
  }

  const rowRows = Object.entries(d.row).map(([k, v]) => ({ field: k, value: v }));
  const what = group('WHAT IT SAYS', table(rowRows, ['field', 'value']));

  if (!d.session) {
    phead(rowId, tableName);
    P().innerHTML = what + `<div class="note">${esc(d.note)}</div>`;
    return;
  }

  const w = d.woken_by || {};
  const subject = (w.refs && w.refs.length) ? w.refs.join(', ')
                : (w.detail || w.message || '');
  const woke = group('WHAT WOKE IT',
    `<div class="note"><b>${esc(w.kind || 'unrecorded')}</b>${
      subject ? ' · ' + esc(subject) : ''}</div>` +
    (d.chain.length
      ? sec('and what caused that', d.chain.length,
            table(d.chain, ['id', 'from_role', 'to_role', 'verb', 'status']), true)
      : `<div class="empty">a tick, so there is no message behind it</div>`));

  const who = group('WHO WROTE IT',
    table([{ session: d.session.id, role: d.session.role, mode: d.session.mode,
             model: d.session.model, committed: d.session.committed }]) +
    sec('what it reached for', d.did.length,
        table(d.did, ['seq', 'fn', 'args']), d.did.length > 0) +
    (d.history.length > 1
      ? sec('every session that touched it', d.history.length,
            table(d.history, ['session', 'role', 'wake', 'version']))
      : ''));

  // Two shapes, and the recorded one wins. When the run kept `turns`, the
  // exact context and the exact response are on file and there is nothing to
  // rebuild — the panel used to ignore them and render an empty brief, which
  // presented the best-evidenced sessions as the worst-documented ones. The
  // rebuilt brief is the fallback for runs that recorded nothing, and it says
  // so.
  const s = d.shown || {};
  const turns = s.turns || [];
  const shown = group('WHAT IT WAS SHOWN', turns.length
    ? `<div class="note">${turns.length} round-trip(s) recorded verbatim —
         the exact context and the exact response, nothing rebuilt.</div>` +
      turns.map((t, i) => sec(`turn ${t.seq ?? i + 1}`, t.ms ? `${t.ms} ms` : '',
        (t.system ? `<b class="sig">system</b>
           <pre class="brief">${esc(t.system)}</pre>` : '') +
        `<b class="sig">user</b><pre class="brief">${esc(t.user || '')}</pre>
         <b class="sig">completion</b><pre class="brief">${esc(t.completion || '')}</pre>`,
        i === 0)).join('')
    : `<div class="note">${esc(s.note || '')}</div>` +
      sec('brief', `${(s.brief || '').length} chars`,
          `<pre class="brief">${esc(s.brief || '')}</pre>`) +
      sec('toolkit', (s.tools || []).length,
          `<pre class="brief">${esc((s.tools || []).join(String.fromCharCode(10)))}</pre>`));

  phead(rowId, `${tableName} · why is this here`);
  P().innerHTML = what + woke + who + shown;
}
window.showProvenance = showProvenance;
