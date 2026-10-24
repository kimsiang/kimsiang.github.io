/* ============================================================
   About Muons — interactive calculators
   <div class="calc" data-calc="dilation"></div>  time dilation & survival
   <div class="calc" data-calc="depth"></div>     cosmic-muon flux vs depth
   Models are educational approximations (see notes in each widget).
   ============================================================ */
(function () {
  const bi = (en, zh) => `<span class="en">${en}</span><span class="zh">${zh}</span>`;
  const fmt = (x, d = 2) => {
    if (!isFinite(x)) return '∞';
    if (x === 0) return '0';
    const a = Math.abs(x);
    if (a >= 1e5 || a < 1e-3) { const e = Math.floor(Math.log10(a)); return `${(x / 10 ** e).toFixed(d)}×10<sup>${e}</sup>`; }
    return a >= 100 ? x.toFixed(0) : a >= 10 ? x.toFixed(1) : x.toFixed(d);
  };
  const row = (id, en, zh, unit = '') => `<div class="calc-out"><span>${bi(en, zh)}</span><b id="${id}"></b><small>${unit}</small></div>`;

  /* ---------- 1. time dilation ---------- */
  const M = 0.1056584, CT = 658.6, TAU = 2.197, H = 15000;   // GeV, m, µs, m
  const dilation = (el) => {
    el.innerHTML = `
      <div class="calc-head"><span class="mono">CALC 01</span><h4>${bi('How far does a muon get?', '缪子能飞多远？')}</h4></div>
      <label class="calc-in">${bi('Muon momentum', '缪子动量')} <output id="c1-p"></output> GeV/c
        <input type="range" id="c1-r" min="-1" max="2.3" step="0.01" value="0.6"></label>
      <div class="calc-grid">
        ${row('c1-g', 'Time-dilation factor γ', '时间膨胀因子 γ')}
        ${row('c1-b', 'Speed', '速度', 'c')}
        ${row('c1-l', 'Mean distance before decay', '平均衰变前飞行距离', 'm')}
        ${row('c1-t', 'Trip from 15 km, muon\'s own clock', '从15 km高空出发，缪子自身时钟', 'µs')}
        ${row('c1-s', 'Fraction surviving to the ground', '到达地面的比例', '%')}
        ${row('c1-n', '… without relativity', '……若没有相对论', '%')}
      </div>
      <p class="calc-note">${bi('Lifetime 2.197 µs, so cτ = 659 m. γ = E/mc², mean decay length = γβcτ, survival = exp(−15 km / decay length). Energy loss in the atmosphere (about 2 GeV) is ignored.',
                                '寿命2.197 µs，故cτ = 659 m。γ = E/mc²，平均衰变长度 = γβcτ，存活比例 = exp(−15 km / 衰变长度)。忽略大气中约2 GeV的能量损失。')}</p>`;
    const r = el.querySelector('#c1-r');
    const upd = () => {
      const p = 10 ** parseFloat(r.value), E = Math.hypot(p, M), g = E / M, b = p / E, L = g * b * CT;
      el.querySelector('#c1-p').textContent = p >= 10 ? p.toFixed(0) : p.toFixed(2);
      el.querySelector('#c1-g').innerHTML = fmt(g);
      el.querySelector('#c1-b').innerHTML = b.toFixed(b > 0.999 ? 6 : 4);
      el.querySelector('#c1-l').innerHTML = fmt(L, 0);
      el.querySelector('#c1-t').innerHTML = fmt(H / (b * 299792458) * 1e6 / g);
      el.querySelector('#c1-s').innerHTML = fmt(100 * Math.exp(-H / L));
      el.querySelector('#c1-n').innerHTML = fmt(100 * Math.exp(-H / (b * CT)), 1);
    };
    r.addEventListener('input', upd); upd();
  };

  /* ---------- 2. flux vs depth ---------- */
  // Vertical sea-level spectrum: Gaisser (1990) with the low-energy correction of Guan et al. (2015).
  const spec = (E) => { const Ee = E * (1 + 3.64 / Math.pow(E, 1.29)); return 0.14 * Math.pow(Ee, -2.7) * (1 / (1 + 1.1 * E / 115) + 0.054 / (1 + 1.1 * E / 850)); };
  const A = 2.2e-3, B = 4.0e-6;   // GeV cm²/g, (g/cm²)⁻¹ — standard rock
  const intensity = (depthM, rho) => {
    const X = depthM * 100 * rho, Emin = (A / B) * (Math.expm1(B * X));
    let lo = Math.log(Math.max(Emin, 0.1)), hi = Math.log(1e6), n = 800, h = (hi - lo) / n, s = 0;
    for (let i = 0; i <= n; i++) { const E = Math.exp(lo + i * h), w = (i === 0 || i === n) ? 0.5 : 1; s += w * spec(E) * E; }   // ∫f dE = ∫ f E d(lnE)
    return s * h;   // cm⁻² s⁻¹ sr⁻¹ (vertical)
  };
  const MAT = [['rock', 'Standard rock', '标准岩石', 2.65], ['water', 'Water', '水', 1.0], ['concrete', 'Concrete', '混凝土', 2.3], ['soil', 'Wet soil / sediment', '湿土 / 沉积物', 1.8]];
  const depth = (el) => {
    el.innerHTML = `
      <div class="calc-head"><span class="mono">CALC 02</span><h4>${bi('How many muons reach a depth?', '多深处还有多少缪子？')}</h4></div>
      <label class="calc-in">${bi('Depth below the surface', '地表以下深度')} <output id="c2-d"></output> m
        <input type="range" id="c2-r" min="0" max="3" step="0.01" value="1.3"></label>
      <div class="calc-row">
        <label class="calc-sel">${bi('Material', '材质')} <select id="c2-m">${MAT.map(([k, en, zh, d]) => `<option value="${k}">${en} / ${zh} · ${d} g/cm³</option>`).join('')}</select></label>
        <label class="calc-sel">${bi('Detector area', '探测器面积')} <select id="c2-a"><option value="0.01">10 × 10 cm</option><option value="0.0625">25 × 25 cm</option><option value="0.25" selected>50 × 50 cm</option><option value="1">1 m²</option></select></label>
      </div>
      <div class="calc-grid">
        ${row('c2-x', 'Overburden', '覆盖层厚度', 'm w.e.')}
        ${row('c2-e', 'Minimum muon energy to get there', '到达该深度所需最低能量', 'GeV')}
        ${row('c2-i', 'Vertical intensity', '垂直强度', 'm⁻² s⁻¹ sr⁻¹')}
        ${row('c2-f', 'Compared with the surface', '相对地表', '')}
        ${row('c2-n', 'Rate on your detector', '探测器计数率', '')}
        ${row('c2-t', 'Time to collect 10 000 muons', '收集一万个缪子所需时间', '')}
      </div>
      <p class="calc-note">${bi('Educational model: sea-level spectrum of Gaisser with the Guan et al. (2015) correction, muon energy loss −dE/dX = a + bE with a = 2.2 MeV cm²/g and b = 4.0×10⁻⁶ cm²/g, and a cos²θ angular distribution for the detector rate. Good to a factor of about two; real surveys use full simulation.',
                                '教学模型：Gaisser海平面能谱加Guan等（2015）修正，缪子能量损失 −dE/dX = a + bE（a = 2.2 MeV cm²/g，b = 4.0×10⁻⁶ cm²/g），探测器计数率假设cos²θ角分布。精度约在两倍以内；实际勘测使用完整模拟。')}</p>`;
    const r = el.querySelector('#c2-r'), m = el.querySelector('#c2-m'), a = el.querySelector('#c2-a');
    const I0 = intensity(0, 1);
    const upd = () => {
      const d = Math.round(10 ** parseFloat(r.value)) - 1, rho = MAT.find((x) => x[0] === m.value)[3], area = parseFloat(a.value);
      const X = d * 100 * rho, Emin = (A / B) * Math.expm1(B * X), I = intensity(d, rho);
      const rate = I * 1e4 * area * 2 * Math.PI / 3;   // per second
      el.querySelector('#c2-d').textContent = d;
      el.querySelector('#c2-x').innerHTML = fmt(d * rho, 0);
      el.querySelector('#c2-e').innerHTML = fmt(Emin, 1);
      el.querySelector('#c2-i').innerHTML = fmt(I * 1e4);
      el.querySelector('#c2-f').innerHTML = I / I0 > 0.5 ? '≈ 1' : `1 / ${fmt(I0 / I, 1)}`;
      el.querySelector('#c2-n').innerHTML = rate >= 1 ? `${fmt(rate)} /s` : rate * 60 >= 1 ? `${fmt(rate * 60)} /min` : rate * 3600 >= 1 ? `${fmt(rate * 3600)} /h` : `${fmt(rate * 86400)} /day`;
      const t = 1e4 / rate;
      el.querySelector('#c2-t').innerHTML = t < 60 ? `${fmt(t)} s` : t < 3600 ? `${fmt(t / 60)} min` : t < 86400 ? `${fmt(t / 3600)} h` : t < 86400 * 365 ? `${fmt(t / 86400)} d` : `${fmt(t / 86400 / 365)} yr`;
    };
    [r, m, a].forEach((x) => x.addEventListener('input', upd)); upd();
  };

  document.querySelectorAll('.calc[data-calc]').forEach((el) => ({ dilation, depth }[el.dataset.calc] || (() => {}))(el));
})();
