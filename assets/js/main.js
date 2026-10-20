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
      links.forEach((a) => a.classList.toggle('active', a.getAttribute('href') === '#' + e.target.id));
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
