/* ============================================================
   TDLI Muon Physics Group — Scripts v3
   ============================================================ */
(function () {
  const heroSrc = new URL('hero.bundle.js', document.currentScript.src).href;
  const doc = document.documentElement;
  doc.classList.add('js');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Language toggle ---------- */
  const setLang = (l) => {
    doc.dataset.lang = l;
    doc.lang = l === 'zh' ? 'zh-CN' : 'en';
    try { localStorage.setItem('lang', l); } catch (e) {}
  };
  const langBtn = document.getElementById('lang-toggle');
  if (langBtn) langBtn.addEventListener('click', () => setLang(doc.dataset.lang === 'zh' ? 'en' : 'zh'));

  /* ---------- Nav: scrolled state + active section ---------- */
  const nav = document.getElementById('nav');
  const links = [...document.querySelectorAll('.nav-links a')];
  const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 40);
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  const secObs = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      links.forEach((a) => { if (a.getAttribute('href').startsWith('#')) a.classList.toggle('active', a.getAttribute('href') === '#' + e.target.id); });
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  document.querySelectorAll('main section[id]').forEach((s) => secObs.observe(s));

  /* ---------- Mobile menu ---------- */
  const burger = document.getElementById('burger');
  const menu = document.getElementById('nav-links');
  if (burger && menu) {
    const close = () => { menu.classList.remove('open'); burger.setAttribute('aria-expanded', 'false'); };
    burger.addEventListener('click', () => {
      const open = menu.classList.toggle('open');
      burger.setAttribute('aria-expanded', String(open));
    });
    menu.querySelectorAll('a').forEach((a) => a.addEventListener('click', close));
    window.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
  }

  /* ---------- Reveal on scroll (staggered per group) ---------- */
  const groups = new Map();
  document.querySelectorAll('.rv').forEach((el) => {
    const p = el.parentElement;
    const i = groups.get(p) || 0;
    groups.set(p, i + 1);
    el.style.setProperty('--d', Math.min(i, 6) * 0.07 + 's');
  });
  const rvObs = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add('in'); rvObs.unobserve(e.target); }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  document.querySelectorAll('.rv').forEach((el) => rvObs.observe(el));

  /* ---------- Counters ---------- */
  const cObs = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      cObs.unobserve(e.target);
      const el = e.target, end = +el.dataset.count, suf = el.dataset.suffix || '';
      if (reduced) return;
      const t0 = performance.now(), dur = 1400;
      const tick = (t) => {
        const k = Math.min(1, (t - t0) / dur), v = Math.round(end * (1 - Math.pow(1 - k, 3)));
        el.textContent = v + (k === 1 ? suf : '');
        if (k < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  }, { threshold: 0.6 });
  document.querySelectorAll('[data-count]').forEach((el) => cObs.observe(el));

  /* ---------- Timeline arrows ---------- */
  const tl = document.getElementById('timeline');
  document.querySelectorAll('.tl-ctrl button').forEach((b) => b.addEventListener('click', () => {
    const w = tl.querySelector('li').getBoundingClientRect().width;
    tl.scrollBy({ left: +b.dataset.dir * w, behavior: reduced ? 'auto' : 'smooth' });
  }));

  /* ---------- Gallery: filter + lightbox ---------- */
  const chips = document.querySelectorAll('.chips button');
  const gItems = document.querySelectorAll('.g-item');
  chips.forEach((c) => c.addEventListener('click', () => {
    chips.forEach((x) => x.classList.toggle('on', x === c));
    gItems.forEach((it) => { it.hidden = c.dataset.f !== 'all' && it.dataset.cat !== c.dataset.f; });
  }));
  /* generic lightbox for gallery tiles and .zoom links */
  let lb = document.getElementById('lightbox');
  if (!lb && window.HTMLDialogElement) {
    lb = document.createElement('dialog'); lb.className = 'lightbox'; lb.id = 'lightbox';
    lb.innerHTML = '<button type="button" class="lb-close" aria-label="Close">×</button><img alt=""><p class="lb-cap"></p>';
    document.body.appendChild(lb);
  }
  if (lb && lb.showModal) {
    const lbImg = lb.querySelector('img'), lbCap = lb.querySelector('.lb-cap');
    const open = (src, cap, alt) => { lbImg.src = src; lbImg.alt = alt || ''; lbCap.textContent = cap || ''; lbCap.hidden = !cap; lb.showModal(); };
    document.querySelectorAll('.g-item button').forEach((b) => b.addEventListener('click', () => {
      const im = b.querySelector('img');
      const cap = b.querySelector('.g-cap ' + (doc.dataset.lang === 'zh' ? '.zh' : '.en'));
      const yr = b.querySelector('.g-cap small');
      open(b.dataset.full, (cap ? cap.textContent : im.alt) + (yr ? ' · ' + yr.textContent : ''), im.alt);
    }));
    document.querySelectorAll('a.zoom').forEach((a) => a.addEventListener('click', (e) => {
      e.preventDefault();
      const fig = a.closest('figure'), fc = fig && fig.querySelector('figcaption'), im = a.querySelector('img');
      open(a.getAttribute('href'), fc ? fc.textContent.trim() : '', im ? im.alt : '');
    }));
    lb.querySelector('.lb-close').addEventListener('click', () => lb.close());
    lb.addEventListener('click', (e) => { if (e.target === lb) lb.close(); });
  }

  /* ---------- List filters (news archive, publications) ---------- */
  const filterList = (cfg) => {
    const items = [...document.querySelectorAll(cfg.items)];
    if (!items.length) return;
    let chip = 'all', q = '', small = false;
    const run = () => {
      let shown = 0;
      items.forEach((it) => {
        const ok = (chip === 'all' || it.dataset[cfg.key] === chip) && (!q || it.dataset.q.includes(q)) && (!small || it.dataset.size !== 'big');
        it.hidden = !ok; if (ok) shown++;
      });
      document.querySelectorAll(cfg.heads || '_none').forEach((h) => {
        let n = h.nextElementSibling, any = false;
        while (n && !n.matches(cfg.heads)) { if (!n.hidden) any = true; n = n.nextElementSibling; }
        h.hidden = !any;
      });
      const e = document.getElementById(cfg.empty); if (e) e.hidden = shown > 0;
    };
    document.querySelectorAll(cfg.chips).forEach((c) => c.addEventListener('click', () => {
      document.querySelectorAll(cfg.chips).forEach((x) => x.classList.toggle('on', x === c));
      chip = c.dataset[cfg.key]; run();
    }));
    const qi = document.getElementById(cfg.q);
    if (qi) qi.addEventListener('input', () => { q = qi.value.trim().toLowerCase(); run(); });
    const sm = document.getElementById(cfg.small || '_none');
    if (sm) sm.addEventListener('change', () => { small = sm.checked; run(); });
  };
  filterList({ items: '.ncard', chips: '.filters .chips button', key: 'y', q: 'news-q', empty: 'news-empty' });
  filterList({ items: '.pub', chips: '.filters .chips button', key: 'k', q: 'pub-q', empty: 'pub-empty', small: 'pub-small', heads: '.pyear' });

  /* table-of-contents highlight */
  const tocLinks = [...document.querySelectorAll('.toc a')];
  if (tocLinks.length) {
    const tObs = new IntersectionObserver((es) => es.forEach((e) => {
      if (e.isIntersecting) tocLinks.forEach((a) => a.classList.toggle('on', a.getAttribute('href') === '#' + e.target.id));
    }), { rootMargin: '-20% 0px -70% 0px' });
    tocLinks.forEach((a) => { const t = document.getElementById(a.getAttribute('href').slice(1)); if (t) tObs.observe(t); });
  }

  /* ---------- Contact form → compose email ---------- */
  const form = document.getElementById('contact-form');
  if (form) form.addEventListener('submit', (e) => {
    e.preventDefault();
    const d = new FormData(form);
    const subject = `[TDLI Muon] Message from ${d.get('name')}`;
    const body = `Name: ${d.get('name')}\nEmail: ${d.get('email')}\nAffiliation: ${d.get('affiliation') || '-'}\n\n${d.get('message')}`;
    window.location.href = `mailto:kimsiang84@sjtu.edu.cn?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  });

  /* ---------- 3D hero ---------- */
  const canvas = document.getElementById('hero-canvas');
  if (!canvas) return;
  const $ = (id) => document.getElementById(id);
  const pad = (n) => String(n).padStart(6, '0');
  import(heroSrc).then(({ initHero }) => {
    let api;
    api = initHero(canvas, {
      onEvent: ({ evt, hits, planes, theta }) => {
        $('hud-evt').textContent = pad(evt);
        $('hud-hits').textContent = `${hits}/${planes}`;
        $('hud-theta').textContent = theta.toFixed(1) + '°';
        if (api && api.rate) $('hud-rate').textContent = api.rate().toFixed(1) + ' Hz';
      },
    });
    if (api) requestAnimationFrame(() => canvas.classList.add('on'));
  }).catch(() => { /* static fallback remains */ });
})();
