/* ============================================================
   Sub-page header scenes — small, solid 3D objects
   ring     : Muon g−2 superconducting storage ring with circulating muons
   muonium  : μ⁺ e⁻ bound state — nucleus, orbitals, electron cloud
   module   : a three-layer scintillator tracker module hit by cosmic muons
   ============================================================ */
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const CYAN = 0x2fc8ff;

function glow() {
  const c = document.createElement('canvas'); c.width = c.height = 64;
  const g = c.getContext('2d'), r = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(0.3, 'rgba(140,220,255,.8)'); r.addColorStop(1, 'rgba(0,100,255,0)');
  g.fillStyle = r; g.fillRect(0, 0, 64, 64);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}

// Probe once with a throwaway canvas so browsers without WebGL fall back quietly
// instead of three.js logging "Error creating WebGL context".
let _gl;
export function hasWebGL() {
  if (_gl !== undefined) return _gl;
  try {
    const c = document.createElement('canvas');
    const g = window.WebGLRenderingContext && (c.getContext('webgl2') || c.getContext('webgl'));
    _gl = !!g;
    if (g) g.getExtension('WEBGL_lose_context')?.loseContext();
  } catch (e) { _gl = false; }
  return _gl;
}

function stage(canvas) {
  let renderer;
  if (!hasWebGL()) return null;
  try { renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true }); } catch (e) { return null; }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.shadowMap.enabled = true;
  const scene = new THREE.Scene();
  const pm = new THREE.PMREMGenerator(renderer);
  scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.45;
  scene.add(new THREE.HemisphereLight(0x9cc4ff, 0x04060a, 0.6));
  const key = new THREE.DirectionalLight(0xe6f1ff, 2.2); key.position.set(5, 9, 6); key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024); Object.assign(key.shadow.camera, { left: -7, right: 7, top: 7, bottom: -7, near: 1, far: 30 });
  key.shadow.bias = -0.0005; key.shadow.normalBias = 0.02;
  scene.add(key);
  const rim = new THREE.DirectionalLight(0x2f6bff, 3); rim.position.set(-7, 2, -6); scene.add(rim);
  const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 100);
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(new THREE.Vector2(1, 1), 0.6, 0.4, 0.8);
  composer.addPass(bloom); composer.addPass(new OutputPass());
  const resize = () => {
    const w = canvas.clientWidth, h = canvas.clientHeight; if (!w || !h) return;
    renderer.setSize(w, h, false); composer.setSize(w, h); bloom.setSize(w, h);
    camera.aspect = w / h; camera.updateProjectionMatrix();
  };
  new ResizeObserver(resize).observe(canvas); resize();
  return { renderer, scene, camera, composer, key };
}

const cast = (m) => { m.castShadow = m.receiveShadow = true; return m; };
const M = {
  steel: () => new THREE.MeshStandardMaterial({ color: 0x2a3341, metalness: 0.9, roughness: 0.38 }),
  alu: () => new THREE.MeshStandardMaterial({ color: 0xbcc6d4, metalness: 1, roughness: 0.26 }),
  chrome: () => new THREE.MeshStandardMaterial({ color: 0xe6edf6, metalness: 1, roughness: 0.12 }),
  copper: () => new THREE.MeshStandardMaterial({ color: 0xc98a4b, metalness: 1, roughness: 0.3 }),
  dark: () => new THREE.MeshStandardMaterial({ color: 0x0b1018, metalness: 0.5, roughness: 0.45 }),
};

function shadowFloor(scene, y) {
  const f = new THREE.Mesh(new THREE.PlaneGeometry(40, 40), new THREE.ShadowMaterial({ opacity: 0.45 }));
  f.rotation.x = -Math.PI / 2; f.position.y = y; f.receiveShadow = true; scene.add(f);
  const g = new THREE.GridHelper(30, 30, 0x1c3a66, 0x0e1c33); g.position.y = y + 0.002;
  g.material.transparent = true; g.material.opacity = 0.35; scene.add(g);
}

// ------------------------------------------------------------ g−2 storage ring
function ring(S) {
  const { scene } = S, R = 3.2, G = new THREE.Group(); scene.add(G);
  const steel = M.steel(), coil = M.copper(), alu = M.alu(), dark = M.dark();
  // C-shaped yoke cross-section (r, y), open toward the ring centre
  const prof = [[R - 0.25, 0.55], [R + 0.75, 0.55], [R + 0.75, -0.55], [R - 0.25, -0.55], [R - 0.25, -0.34],
                [R + 0.38, -0.34], [R + 0.38, 0.34], [R - 0.25, 0.34], [R - 0.25, 0.55]].map(([x, y]) => new THREE.Vector2(x, y));
  const SEG = 12, gap = 0.035;
  for (let i = 0; i < SEG; i++) {
    const a0 = (i / SEG) * Math.PI * 2 + gap, len = (Math.PI * 2) / SEG - gap * 2;
    G.add(cast(new THREE.Mesh(new THREE.LatheGeometry(prof, 1, a0, len).toNonIndexed(), steel)));
    // flux-return bolt heads
    const b = cast(new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.05, 10), alu));
    const am = a0 + len / 2; b.position.set(Math.sin(am) * (R + 0.25), 0.58, Math.cos(am) * (R + 0.25)); G.add(b);
  }
  // superconducting coils + vacuum chamber
  for (const y of [0.42, -0.42]) {
    const c = cast(new THREE.Mesh(new THREE.TorusGeometry(R - 0.42, 0.07, 12, 160), coil));
    c.rotation.x = Math.PI / 2; c.position.y = y; G.add(c);
  }
  const ch = cast(new THREE.Mesh(new THREE.TorusGeometry(R, 0.17, 16, 200), alu)); ch.rotation.x = Math.PI / 2; G.add(ch);
  const beam = new THREE.Mesh(new THREE.TorusGeometry(R, 0.03, 8, 200), new THREE.MeshBasicMaterial({ color: CYAN, transparent: true, opacity: 0.5 }));
  beam.rotation.x = Math.PI / 2; G.add(beam);
  // calorimeter stations on the inner radius
  const cals = [];
  for (let i = 0; i < 24; i++) {
    const a = (i / 24) * Math.PI * 2;
    const m = new THREE.MeshStandardMaterial({ color: 0x0c1422, metalness: 0.4, roughness: 0.4, emissive: CYAN, emissiveIntensity: 0 });
    const c = cast(new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.3, 0.22), m));
    c.position.set(Math.sin(a) * (R - 0.85), 0, Math.cos(a) * (R - 0.85)); c.rotation.y = a; G.add(c);
    cals.push({ m, g: 0 });
  }
  // support legs + platform
  for (let i = 0; i < 6; i++) {
    const a = (i / 6) * Math.PI * 2 + 0.26;
    const l = cast(new THREE.Mesh(new THREE.BoxGeometry(0.22, 1.1, 0.22), dark));
    l.position.set(Math.sin(a) * (R + 0.25), -1.1, Math.cos(a) * (R + 0.25)); G.add(l);
  }
  shadowFloor(scene, -1.65);
  // circulating muons
  const tex = glow(), mu = [];
  for (let i = 0; i < 36; i++) {
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, color: 0xd8f4ff, blending: THREE.AdditiveBlending, depthWrite: false }));
    sp.scale.setScalar(i % 6 === 0 ? 0.32 : 0.16); G.add(sp);
    mu.push({ sp, a: (i / 36) * Math.PI * 2 * 0.35, ph: Math.random() * 6.28 });
  }
  return {
    cam: { r: 12.5, el: 0.55, target: new THREE.Vector3(0, -0.3, 0) },
    tick(dt, t) {
      G.rotation.y += dt * 0.08;
      for (const m of mu) {
        m.a += dt * 1.6;
        const rr = R + Math.sin(m.a * 3.1 + m.ph) * 0.08, y = Math.sin(m.a * 5.3 + m.ph) * 0.05;
        m.sp.position.set(Math.sin(m.a) * rr, y, Math.cos(m.a) * rr);
      }
      if (Math.random() < dt * 4) cals[(Math.random() * 24) | 0].g = 1; // decay positron hits a calorimeter
      for (const c of cals) { c.g = Math.max(0, c.g - dt * 1.5); c.m.emissiveIntensity = c.g * c.g * 3; }
    },
  };
}

// ------------------------------------------------------------ muonium
function muonium(S) {
  const { scene } = S, G = new THREE.Group(); scene.add(G);
  const core = cast(new THREE.Mesh(new THREE.SphereGeometry(0.62, 64, 48), new THREE.MeshPhysicalMaterial({
    color: 0x1c4fd8, metalness: 0.2, roughness: 0.15, clearcoat: 1, clearcoatRoughness: 0.08, emissive: 0x0a3fff, emissiveIntensity: 0.6 })));
  G.add(core);
  const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: glow(), color: 0x6fd6ff, blending: THREE.AdditiveBlending, depthWrite: false, opacity: 0.6 }));
  halo.scale.setScalar(2.6); G.add(halo);
  // spin arrow
  const spin = new THREE.Group(), arrowM = M.chrome();
  const shaft = cast(new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 1.6, 16), arrowM)); shaft.position.y = 0.8; spin.add(shaft);
  const head = cast(new THREE.Mesh(new THREE.ConeGeometry(0.14, 0.34, 24), arrowM)); head.position.y = 1.75; spin.add(head);
  G.add(spin);
  // orbitals
  const orbs = [], chrome = M.chrome();
  for (let i = 0; i < 3; i++) {
    const o = new THREE.Group();
    o.add(cast(new THREE.Mesh(new THREE.TorusGeometry(2.3 + i * 0.08, 0.025, 10, 220), chrome)));
    o.rotation.set(Math.PI / 2 + (i - 1) * 0.9, i * 1.1, 0);
    G.add(o); orbs.push(o);
  }
  const e = new THREE.Mesh(new THREE.SphereGeometry(0.16, 32, 24), new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: CYAN, emissiveIntensity: 2.2 }));
  orbs[0].add(e);
  // 1s electron cloud
  const N = window.innerWidth < 860 ? 900 : 1800, pos = new Float32Array(N * 3);
  for (let i = 0; i < N; i++) {
    const r = -Math.log(1 - Math.random() * 0.97) * 0.9 + 0.7, th = Math.acos(2 * Math.random() - 1), ph = Math.random() * 6.283;
    pos.set([r * Math.sin(th) * Math.cos(ph), r * Math.cos(th), r * Math.sin(th) * Math.sin(ph)], i * 3);
  }
  const cg = new THREE.BufferGeometry(); cg.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const cloud = new THREE.Points(cg, new THREE.PointsMaterial({ color: 0x7cc8ff, size: 0.03, transparent: true, opacity: 0.55, depthWrite: false, blending: THREE.AdditiveBlending }));
  G.add(cloud);
  // pedestal
  const ped = cast(new THREE.Mesh(new THREE.CylinderGeometry(1.4, 1.6, 0.25, 64), M.steel())); ped.position.y = -3.0; G.add(ped);
  const ring2 = new THREE.Mesh(new THREE.TorusGeometry(1.5, 0.02, 8, 128), new THREE.MeshBasicMaterial({ color: CYAN })); ring2.rotation.x = Math.PI / 2; ring2.position.y = -2.86; G.add(ring2);
  shadowFloor(scene, -3.13);
  let ea = 0;
  return {
    cam: { r: 12, el: 0.32, target: new THREE.Vector3(0, -0.4, 0) },
    tick(dt, t) {
      G.rotation.y += dt * 0.12; cloud.rotation.y -= dt * 0.05;
      ea += dt * 2.1; e.position.set(Math.cos(ea) * 2.3, Math.sin(ea) * 2.3, 0);
      spin.rotation.z = 0.35 * Math.sin(t * 0.9); spin.rotation.x = 0.35 * Math.cos(t * 0.9);
      halo.material.opacity = 0.5 + 0.1 * Math.sin(t * 2);
    },
  };
}

// ------------------------------------------------------------ tracker module
function module(S) {
  const { scene } = S, G = new THREE.Group(); scene.add(G);
  const alu = M.alu(), dark = M.dark(), Y = [0.75, 0, -0.75], bars = [];
  Y.forEach((y, p) => {
    const L = new THREE.Group(); L.position.y = y;
    const alongX = p % 2 === 1;
    for (let i = 0; i < 8; i++) {
      const m = new THREE.MeshPhysicalMaterial({ color: 0x16233a, metalness: 0.1, roughness: 0.5, clearcoat: 0.4, emissive: CYAN, emissiveIntensity: 0 });
      const b = cast(new THREE.Mesh(alongX ? new THREE.BoxGeometry(3.4, 0.2, 0.4) : new THREE.BoxGeometry(0.4, 0.2, 3.4), m));
      if (alongX) b.position.z = -1.5 + i * 0.43; else b.position.x = -1.5 + i * 0.43;
      L.add(b); bars.push({ m, g: 0, p, i, alongX });
    }
    for (const s of [-1, 1]) {
      const a = cast(new THREE.Mesh(new THREE.BoxGeometry(3.9, 0.3, 0.14), alu)); a.position.z = s * 1.85; L.add(a);
      const c = cast(new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.3, 3.56), alu)); c.position.x = s * 1.88; L.add(c);
    }
    const ro = cast(new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.26, 0.36), dark));
    if (alongX) { ro.rotation.y = Math.PI / 2; ro.position.x = 2.2; } else ro.position.z = 2.2;
    L.add(ro); G.add(L);
  });
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) {
    const p = cast(new THREE.Mesh(new THREE.BoxGeometry(0.2, 2.6, 0.2), alu)); p.position.set(sx * 2.0, -0.2, sz * 1.97); G.add(p);
  }
  const base = cast(new THREE.Mesh(new THREE.BoxGeometry(4.8, 0.2, 4.8), M.steel())); base.position.y = -1.55; G.add(base);
  shadowFloor(scene, -1.65);
  const tex = glow(), tr = [];
  for (let k = 0; k < 6; k++) {
    const line = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 1, 6, 1, true), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }));
    const head = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, color: 0xd8f4ff, blending: THREE.AdditiveBlending, depthWrite: false, opacity: 0 }));
    head.scale.setScalar(0.35); G.add(line, head); tr.push({ line, head, on: false });
  }
  let spawnT = 0;
  const UP = new THREE.Vector3(0, 1, 0);
  return {
    cam: { r: 13, el: 0.45, target: new THREE.Vector3(0, -0.2, 0) },
    tick(dt) {
      G.rotation.y += dt * 0.1;
      spawnT -= dt;
      if (spawnT < 0) {
        spawnT = 0.5 + Math.random() * 0.8;
        const t = tr.find((x) => !x.on);
        if (t) {
          const th = Math.acos(Math.pow(Math.random(), 1 / 3)), ph = Math.random() * 6.28;
          t.dir = new THREE.Vector3(Math.sin(th) * Math.cos(ph), -Math.cos(th), Math.sin(th) * Math.sin(ph));
          t.p0 = new THREE.Vector3((Math.random() - 0.5) * 3, 0, (Math.random() - 0.5) * 3).addScaledVector(t.dir, -4 / Math.max(0.3, -t.dir.y));
          t.s = 0; t.on = true; t.hit = new Set(); t.line.material.opacity = 0.9; t.head.material.opacity = 1;
        }
      }
      for (const t of tr) if (t.on) {
        const prev = t.p0.clone().addScaledVector(t.dir, t.s); t.s += dt * 8;
        const cur = t.p0.clone().addScaledVector(t.dir, t.s);
        Y.forEach((y, p) => {
          if (prev.y > y && cur.y <= y && !t.hit.has(p)) {
            t.hit.add(p);
            const k = (prev.y - y) / (prev.y - cur.y), x = prev.x + (cur.x - prev.x) * k, z = prev.z + (cur.z - prev.z) * k;
            const alongX = p % 2 === 1, c = alongX ? z : x, i = Math.round((c + 1.5) / 0.43);
            if (Math.abs(x) < 1.75 && Math.abs(z) < 1.75 && i >= 0 && i < 8) bars.find((b) => b.p === p && b.i === i).g = 1;
          }
        });
        const tail = t.p0.clone().addScaledVector(t.dir, Math.max(0, t.s - 2));
        const d = cur.clone().sub(tail), L = d.length();
        t.line.position.copy(tail); t.line.quaternion.setFromUnitVectors(UP, d.normalize()); t.line.scale.set(1, L, 1);
        t.line.translateY(L / 2);
        t.head.position.copy(cur);
        if (cur.y < -4) { t.on = false; t.line.material.opacity = 0; t.head.material.opacity = 0; }
      }
      for (const b of bars) { b.g = Math.max(0, b.g - dt * 1.2); b.m.emissiveIntensity = b.g * b.g * 2.4; }
    },
  };
}

const MODES = { ring, muonium, module };

export function isSoftwareGL(renderer) {
  try {
    const gl = renderer.getContext(), ext = gl.getExtension('WEBGL_debug_renderer_info');
    const name = ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : '';
    return /swiftshader|llvmpipe|softpipe|software|mesa offscreen/i.test(name);
  } catch (e) { return false; }
}

export function initSubScene(canvas, mode = 'module') {
  const S = stage(canvas); if (!S) return null;
  const obj = (MODES[mode] || module)(S);
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let mx = 0, my = 0, tx = 0, ty = 0, az = 0.7, scrollP = 0;
  window.addEventListener('pointermove', (e) => { tx = (e.clientX / innerWidth) * 2 - 1; ty = (e.clientY / innerHeight) * 2 - 1; }, { passive: true });
  window.addEventListener('scroll', () => { scrollP = Math.min(1, scrollY / 600); }, { passive: true });
  const place = () => {
    mx += (tx - mx) * 0.05; my += (ty - my) * 0.05;
    const { r, el, target } = obj.cam, a = az + mx * 0.3, e = el + my * 0.08 + scrollP * 0.2, rr = (r + scrollP * 3) * (S.camera.aspect < 1.4 ? 1.22 : 1);
    S.camera.position.set(Math.cos(a) * Math.cos(e) * rr, Math.sin(e) * rr + target.y, Math.sin(a) * Math.cos(e) * rr);
    S.camera.lookAt(target);
  };
  let last = performance.now(), t = 0, running = true, raf = 0, frames = 0, slow = 0, frozen = false;
  const software = isSoftwareGL(S.renderer);
  const loop = (now) => {
    raf = 0;
    if (!running || document.hidden) return;
    const dt = Math.min(0.05, (now - last) / 1000);
    if (frames < 40) { frames++; if (now - last > 80) slow++; if (software && frames >= 2 || slow >= 12) { running = false; frozen = true; } }
    last = now; t += dt;
    obj.tick(dt, t); place(); S.composer.render(); if (running) raf = requestAnimationFrame(loop);
  };
  const kick = () => { if (raf || !running || document.hidden) return; last = performance.now(); raf = requestAnimationFrame(loop); };
  if (reduced) { obj.tick(0.016, 0); place(); S.composer.render(); return { reduced: true }; }
  new IntersectionObserver(([e]) => { if (!frozen) { running = e.isIntersecting; kick(); } }).observe(canvas);
  document.addEventListener('visibilitychange', kick);
  return { mode };
}
