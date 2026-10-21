/* ============================================================
   TDLI Muon Physics Group — "Ask the group" (client-side RAG)
   ------------------------------------------------------------
   Retrieval: BM25 over assets/data/ask-index.json (papers with
   INSPIRE abstracts, site pages, news, members), fully in the
   browser so it works on GitHub Pages with no backend.
   Answer:    extractive — the best-matching sentences, each
   with a numbered citation back to the source.
   Optional:  set window.MUON_ASK_ENDPOINT to a small proxy
   (see tools/ask-worker.example.js) and the same retrieved
   passages are sent to an LLM for a written synthesis.
   ============================================================ */
(function () {
  const bar = document.getElementById('ask');
  if (!bar) return;
  const input = bar.querySelector('input');
  const panel = document.getElementById('ask-panel');
  const chips = bar.querySelectorAll('.ask-chips button');
  const INDEX_URL = new URL('../data/ask-index.json', document.currentScript.src).href;
  const lang = () => document.documentElement.dataset.lang === 'zh' ? 'zh' : 'en';
  const PH = { en: ['Ask the group’s papers anything…', 'e.g. how does the frozen-spin muEDM method work?', 'e.g. what muon rate will SHINE deliver?'],
               zh: ['向课题组的论文提问…', '例如：缪子成像如何探测地下结构？', '例如：SHINE缪子源能提供多高的缪子通量？'] };
  const setPH = () => { input.placeholder = PH[lang()][window.innerWidth < 640 ? 0 : 1 + (Date.now() / 7000 | 0) % 2]; };
  setPH(); document.getElementById('lang-toggle')?.addEventListener('click', () => setTimeout(setPH, 0));
  const T = (en, zh) => `<span class="en">${en}</span><span class="zh">${zh}</span>`;
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  /* ---------- tokeniser ---------- */
  const STOP = new Set('a an the of in on at to for and or is are was were be been by with from as that this these those it its we our us you your their they them his her he she i do does did how what which who whom why when where can could would should will may might not no into over under about than then there here also such more most very based using used use between among within across both each other some any all'.split(' '));
  const stem = (w) => {
    if (w.length <= 4) return w;
    if (w.endsWith('ies')) return w.slice(0, -3) + 'y';
    if (w.endsWith('ing') && w.length > 6) return w.slice(0, -3);
    if (w.endsWith('ed') && w.length > 5) return w.slice(0, -2);
    if (w.endsWith('es') && w.length > 5) return w.slice(0, -2);
    if (w.endsWith('s') && !w.endsWith('ss')) return w.slice(0, -1);
    return w;
  };
  const norm = (s) => s.toLowerCase()
    .replace(/g\s*[-−–]\s*2|g2\b|\(g-2\)/g, ' g2 ')
    .replace(/mu\s*edm|μedm|muon edm/g, ' muedm edm ')
    .replace(/μ/g, 'mu').replace(/[’'`]/g, '');
  const tokens = (s) => {
    const out = [];
    norm(s).replace(/[一-鿿]+|[a-z0-9]+/g, (m) => {
      if (/[一-鿿]/.test(m)) {               // CJK: unigrams + bigrams
        for (let i = 0; i < m.length; i++) { out.push(m[i]); if (i + 1 < m.length) out.push(m.slice(i, i + 2)); }
      } else if (m.length > 1 && !STOP.has(m)) out.push(stem(m));
      return '';
    });
    return out;
  };
  /* query expansion — physics jargon + a small zh→en bridge so Chinese questions reach English abstracts */
  const SYN = {
    g2: ['anomalou', 'magnetic', 'moment', 'fermilab'], anomalou: ['g2'], fermilab: ['g2'],
    edm: ['electric', 'dipole', 'muedm', 'psi'], dipole: ['edm'], muedm: ['edm', 'psi'], psi: ['muedm', 'scherrer'],
    muography: ['imaging', 'tomography', 'radiography', 'cosmic'], imaging: ['muography'], tomography: ['muography'],
    shine: ['source', 'linac', 'electron'], 'source': ['shine'], muonium: ['antimuon', 'electron'],
    frozen: ['spin', 'edm'], detector: ['scintillator', 'tracker'], scintillator: ['detector'],
    thesi: ['phd', 'master'], paper: ['publication'], publication: ['paper'],
    // zh → en
    '缪子': ['muon'], '缪': ['muon'], '反常磁矩': ['g2', 'anomalou', 'magnetic'], '磁矩': ['g2', 'magnetic'],
    '电偶极矩': ['edm', 'dipole'], '偶极': ['edm'], '成像': ['muography', 'imaging'], '缪子成像': ['muography'],
    '缪子源': ['shine', 'source'], '源': ['source'], '探测器': ['detector'], '探测': ['detector', 'detection'],
    '闪烁': ['scintillator'], '宇宙线': ['cosmic', 'ray'], '宇宙': ['cosmic'], '标准模型': ['standard', 'model'],
    '新物理': ['new', 'physic', 'beyond'], '加速器': ['accelerator', 'linac'], '模拟': ['simulation', 'geant4'],
    '论文': ['paper', 'publication'], '最新': ['recent'], '学生': ['student'], '博士': ['phd'], '硕士': ['master'],
    '谁': ['who'], '成员': ['member', 'people'], '课题组': ['group'], '地下': ['underground'], '上海': ['shanghai'],
    '费米': ['fermilab'], '缪子素': ['muonium'], '自旋': ['spin'], '冻结自旋': ['frozen', 'spin'],
    '束流': ['beam'], '实验': ['experiment'], '精密': ['precision'], '测量': ['measurement'],
  };
  const GENERIC = new Set(['muon', 'mu', 'who', 'work', 'group', 'member', 'student', 'people', 'research', 'physic', 'experiment', 'team', 'doe', 'current', 'on',
    '缪', '子', '缪子', '谁', '在', '做', '成员', '学生', '课题', '组', '课题组', '研究', '谁在', '在做', '做缪', '子的', '的', '是', '哪', '哪些', '些', '人', '有']);
  const expand = (q) => {
    const base = tokens(q), extra = [];
    base.forEach((t) => (SYN[t] || []).forEach((x) => extra.push(x)));
    // multi-char zh keys
    Object.keys(SYN).forEach((k) => { if (k.length > 2 && /[一-鿿]/.test(k) && q.includes(k)) SYN[k].forEach((x) => extra.push(x)); });
    return { base, extra: extra.filter((x) => !base.includes(x)) };
  };

  /* ---------- BM25 index ---------- */
  let DOCS = null, META = {}, IDX = null, loading = null;
  const build = (docs) => {
    const df = new Map(), tf = [], len = [];
    docs.forEach((d, i) => {
      const m = new Map();
      const add = (s, w) => tokens(s).forEach((t) => m.set(t, (m.get(t) || 0) + w));
      add(d.title, 2.5); add((d.kw || []).join(' '), 1.5); add(d.text, 1);
      if (d.authors) add(d.authors, 1.2);
      let L = 0; m.forEach((v) => { L += v; });
      len[i] = L; tf[i] = m;
      m.forEach((_, t) => df.set(t, (df.get(t) || 0) + 1));
    });
    const avg = len.reduce((a, b) => a + b, 0) / len.length;
    return { df, tf, len, avg, N: docs.length };
  };
  const load = () => loading || (loading = fetch(INDEX_URL).then((r) => r.json()).then((j) => { DOCS = j.docs; META = j; IDX = build(DOCS); }));

  const search = (q) => {
    const { base, extra } = expand(q);
    if (!base.length) return { hits: [], base, extra };
    const wantRecent = /\b(latest|recent|newest|new)\b|最新|最近|新/.test(q.toLowerCase());
    const wantPaper = /\bpapers?\b|publication|article|preprint|arxiv|论文|文章|预印本/.test(q.toLowerCase());
    const wantWho = /\bwho\b|\bmembers?\b|students?|postdoc|谁|成员|学生/.test(q.toLowerCase());
    const L = lang(), k1 = 1.4, b = 0.75;
    const terms = base.map((t) => [t, 1]).concat(extra.map((t) => [t, 0.35]));
    const scores = new Float64Array(IDX.N);
    terms.forEach(([t, w]) => {
      const n = IDX.df.get(t); if (!n) return;
      const idf = Math.log(1 + (IDX.N - n + 0.5) / (n + 0.5));
      for (let i = 0; i < IDX.N; i++) {
        const f = IDX.tf[i].get(t); if (!f) continue;
        scores[i] += w * idf * (f * (k1 + 1)) / (f + k1 * (1 - b + b * IDX.len[i] / IDX.avg));
      }
    });
    const hits = [];
    for (let i = 0; i < IDX.N; i++) {
      if (scores[i] <= 0) continue;
      const d = DOCS[i]; let s = scores[i];
      if (d.lang && d.lang !== L) s *= 0.55;            // prefer passages in the reader's language
      if (d.type === 'page') s *= 1.1;
      if (d.type === 'news') s *= 0.85;
      if (d.type === 'member') s *= wantWho ? 2.2 : 0.7;
      if (wantPaper) s *= d.type === 'paper' ? 1.8 : 0.4;
      if (d.type === 'paper' && wantRecent) s *= 1 + Math.max(0, (+d.year - 2018)) * 0.12;
      hits.push({ d, s });
    }
    hits.sort((a, c) => c.s - a.s);
    // coverage gate: the best document must contain most of the asker's own words
    const cjk = /[\u4e00-\u9fff]/.test(q);
    if (hits.length) {
      const top = IDX.tf[DOCS.indexOf(hits[0].d)];
      if (cjk) {
        // Chinese: bigrams straddle word boundaries, so just require one meaningful term (Latin word or a known zh term, via its English synonyms) in the top doc
        const ok = base.some((t) => /^[a-z0-9]+$/.test(t) ? top.has(t) : (SYN[t] || []).some((x) => top.has(x)) || (t.length > 1 && top.has(t)));
        if (!ok) return { hits: [], base, extra };
      } else {
        const cov = base.filter((t) => top.has(t)).length / base.length;
        if (cov < 0.6 && base.length > 1) return { hits: [], base, extra };
      }
    }
    if (wantWho) {
      const spec = new Set(base.concat(extra).filter((t) => !GENERIC.has(t)));
      let mem = hits.filter((h) => h.d.type === 'member');
      if (spec.size) { const m2 = mem.filter((h) => { const tf = IDX.tf[DOCS.indexOf(h.d)]; return [...spec].some((t) => tf.has(t)); }); if (m2.length) mem = m2; }
      const rest = hits.filter((h) => h.d.type !== 'member');
      return { hits: mem.concat(rest).slice(0, 40), base, extra, who: mem.map((h) => h.d) };
    }
    return { hits: hits.slice(0, 40), base, extra };
  };

  /* ---------- extractive answer ---------- */
  const sentences = (t) => t.split(/(?<=[.!?。！？])\s+|(?<=[。！？])/).map((s) => s.trim()).filter((s) => s.length > 25 && !/https?:|arXiv:|doi\.org/.test(s));
  const answer = (res, q) => {
    const want = new Set(res.base), soft = new Set(res.extra);
    const cands = [];
    res.hits.slice(0, 8).forEach((h, rank) => {
      sentences(h.d.text).forEach((s) => {
        const tk = new Set(tokens(s)); let ov = 0;
        tk.forEach((t) => { if (want.has(t)) ov += 1; else if (soft.has(t)) ov += 0.3; });
        if (!ov) return;
        const sc = (ov / Math.sqrt(want.size + 1)) * h.s / (1 + rank * 0.25) * (s.length > 260 ? 0.8 : 1);
        cands.push({ s, sc, doc: h.d });
      });
    });
    cands.sort((a, c) => c.sc - a.sc);
    const picked = [], used = new Map();
    for (const c of cands) {
      if (picked.length >= 4) break;
      if ((used.get(c.doc.id) || 0) >= 2) continue;
      if (picked.some((p) => p.s === c.s)) continue;
      picked.push(c); used.set(c.doc.id, (used.get(c.doc.id) || 0) + 1);
    }
    // keep source order stable: first appearance = [1]
    const order = []; picked.forEach((p) => { if (!order.includes(p.doc)) order.push(p.doc); });
    res.hits.slice(0, 6).forEach((h) => { if (!order.includes(h.d) && order.length < 6) order.push(h.d); });
    return { picked, order };
  };

  /* ---------- rendering ---------- */
  const srcCard = (d, n) => {
    const kind = { paper: T('Paper', '论文'), page: T('Page', '页面'), news: T('News', '新闻'), member: T('Member', '成员') }[d.type];
    const meta = d.type === 'paper'
      ? `${esc(d.authors)}${d.coll ? ' (' + esc(d.coll) + ')' : ''} · ${esc(d.venue)} · ${esc(d.year)}${d.cites ? ' · ' + d.cites + ' cit.' : ''}`
      : d.type === 'news' ? esc(d.date) : esc(d.text.slice(0, 110)) + '…';
    const ext = /^https?:/.test(d.url);
    return `<li class="ask-src" id="ask-src-${n}"><a href="${esc(d.url)}"${ext ? ' target="_blank" rel="noopener"' : ''}>
      <span class="ask-n">${n}</span><span class="ask-src-b"><span class="ask-kind">${kind}</span><b>${esc(d.title)}</b><small>${meta}</small></span><span class="arr">${ext ? '↗' : '→'}</span></a></li>`;
  };
  const render = (q, res) => {
    panel.hidden = false;
    if (!res.hits.length) {
      panel.innerHTML = `<div class="ask-ans"><p class="ask-empty">${T(`Nothing in the group's papers or pages matches “${esc(q)}”. Try other words, or browse the <a href="publications.html">publications</a>.`, `课题组的论文和页面中没有与“${esc(q)}”相关的内容。换个说法试试，或浏览<a href="publications.html">论文列表</a>。`)}</p></div>`;
      return;
    }
    let { picked, order } = answer(res, q);
    if (res.who && res.who.length) { order = res.who.slice(0, 6).concat(order.filter((d) => !res.who.includes(d))).slice(0, 8); picked = []; }
    const cite = (d) => `<sup><a href="#ask-src-${order.indexOf(d) + 1}" class="ask-cite">${order.indexOf(d) + 1}</a></sup>`;
    const who = res.who && res.who.length
      ? res.who.slice(0, 6).map((d) => { const role = (d.text.split(' · ')[2] || '').split('. ')[0]; return `<b>${esc(d.title)}</b>${role ? ' (' + esc(role) + ')' : ''}${cite(d)}`; }).join(', ')
      : '';
    const body = who
      ? T('Members working on this: ', '相关成员：') + who + '.'
      : picked.length
      ? picked.map((p) => `${esc(p.s)}${cite(p.doc)}`).join(' ')
      : T('Here is what the group has on that:', '课题组相关内容如下：');
    panel.innerHTML = `
      <div class="ask-ans">
        <p class="ask-tag mono"><span class="live"></span>${T('Answer · drawn from the group’s own papers &amp; pages', '回答 · 来自课题组论文与页面')}</p>
        <p class="ask-text" id="ask-text">${body}</p>
        <p class="ask-llm mono" id="ask-llm" hidden></p>
      </div>
      <ol class="ask-srcs">${order.map((d, i) => srcCard(d, i + 1)).join('')}</ol>
      <p class="ask-foot mono">${T(`${res.hits.length} matches · index built ${META.built || ''} · retrieval runs in your browser, nothing is sent anywhere`, `${res.hits.length} 条结果 · 索引更新于 ${META.built || ''} · 检索在浏览器本地完成，不上传任何数据`)}</p>`;
    if (window.MUON_ASK_ENDPOINT) synth(q, order.slice(0, 6));
  };

  /* ---------- optional LLM synthesis ---------- */
  const synth = async (q, ctx) => {
    const el = document.getElementById('ask-llm'); if (!el) return;
    el.hidden = false; el.textContent = lang() === 'zh' ? '正在生成综合回答…' : 'Writing a synthesis…';
    try {
      const r = await fetch(window.MUON_ASK_ENDPOINT, {
        method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ question: q, lang: lang(), contexts: ctx.map((d, i) => ({ n: i + 1, title: d.title, text: d.text, url: d.url })) }),
      });
      if (!r.ok) throw new Error(r.status);
      const j = await r.json();
      const out = document.getElementById('ask-text');
      if (!j.answer || !out) { el.hidden = true; return; }
      out.innerHTML = esc(j.answer).replace(/\[(\d+)\]/g, (_, n) => `<sup><a href="#ask-src-${n}" class="ask-cite">${n}</a></sup>`);
      el.textContent = lang() === 'zh' ? 'AI 综合回答 · 仅基于上列来源 · 请核对原文' : 'AI synthesis · from the sources below only · please verify against them';
    } catch (e) { el.hidden = true; }
  };

  /* ---------- wiring ---------- */
  let timer = null, last = '';
  const run = async (q) => {
    q = q.trim(); if (!q) { panel.hidden = true; last = ''; return; }
    if (q === last) return; last = q;
    bar.classList.add('busy');
    await load();
    render(q, search(q));
    bar.classList.remove('busy');
    if (window.innerWidth < 760) setTimeout(() => panel.scrollIntoView({ block: 'start', behavior: 'smooth' }), 50);
    try { history.replaceState(null, '', '#ask?q=' + encodeURIComponent(q)); } catch (e) {}
  };
  input.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(() => run(input.value), 280); });
  input.addEventListener('focus', load, { once: true });
  input.addEventListener('mouseenter', load, { once: true });
  bar.addEventListener('submit', (e) => { e.preventDefault(); clearTimeout(timer); run(input.value); });
  chips.forEach((c) => c.addEventListener('click', () => {
    input.value = c.querySelector(lang() === 'zh' ? '.zh' : '.en').textContent; input.focus(); run(input.value);
  }));
  window.addEventListener('keydown', (e) => {
    if (e.key === '/' && !/input|textarea/i.test(document.activeElement.tagName)) { e.preventDefault(); input.focus(); input.select(); }
    if (e.key === 'Escape' && document.activeElement === input) { input.blur(); }
  });
  document.getElementById('lang-toggle')?.addEventListener('click', () => { if (last) { const q = last; last = ''; run(q); } });
  const m = location.hash.match(/^#ask\?q=(.+)/);
  if (m) { input.value = decodeURIComponent(m[1]); run(input.value); setTimeout(() => bar.scrollIntoView({ block: 'start' }), 300); }
})();
