/* ============================================================
   TDLI Muon Physics Group — 3D hero: cosmic-ray muon tracker
   A 5-plane scintillator-strip tracker (x/y alternating readout)
   with cosmic muons arriving with a cos²θ angular distribution.
   Build: npm run build  →  assets/js/hero.bundle.js
   ============================================================ */
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const CYAN = new THREE.Color(0x2fc8ff);
const BLUE = new THREE.Color(0x2251ff);
const WHITE = new THREE.Color(0xffffff);

const PLANES = 5;
const PLANE_GAP = 1.05;
const STRIPS = 16;
const SIZE_X = 6.0;
const SIZE_Z = 4.2;

function glowTexture() {
  const c = document.createElement('canvas');
  c.width = c.height = 64;
  const g = c.getContext('2d');
  const grd = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  grd.addColorStop(0, 'rgba(255,255,255,1)');
  grd.addColorStop(0.25, 'rgba(160,230,255,0.85)');
  grd.addColorStop(1, 'rgba(0,120,255,0)');
  g.fillStyle = grd;
  g.fillRect(0, 0, 64, 64);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

export function initHero(canvas, opts = {}) {
  const onEvent = opts.onEvent || (() => {});
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const small = () => window.innerWidth < 860;

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
  } catch (e) {
    return null; // no WebGL → CSS fallback stays visible
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, small() ? 1.5 : 1.75));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;

  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x03060b, 0.045);

  const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 200);

  // ---------- Lights ----------
  scene.add(new THREE.AmbientLight(0x6d8cff, 0.35));
  const key = new THREE.DirectionalLight(0xcfe6ff, 0.9);
  key.position.set(6, 10, 7);
  scene.add(key);
  const rim = new THREE.DirectionalLight(0x2251ff, 2.2);
  rim.position.set(-8, 2, -6);
  scene.add(rim);

  // ---------- Detector ----------
  const det = new THREE.Group();
  scene.add(det);
  const planeY = [];
  const strips = []; // strips[p][i] = { mesh, mat, glow }
  const stripW = SIZE_X / STRIPS;

  const frameMat = new THREE.MeshStandardMaterial({ color: 0x8794a8, metalness: 0.9, roughness: 0.35 });
  const boardMat = new THREE.MeshStandardMaterial({ color: 0x0a1a14, metalness: 0.3, roughness: 0.7 });
  const edgeMat = new THREE.LineBasicMaterial({ color: 0x4fbfff, transparent: true, opacity: 0.5 });

  for (let p = 0; p < PLANES; p++) {
    const y = (p - (PLANES - 1) / 2) * PLANE_GAP;
    planeY.push(y);
    const plane = new THREE.Group();
    plane.position.y = y;
    const alongX = p % 2 === 1; // alternate x / z readout
    const row = [];
    for (let i = 0; i < STRIPS; i++) {
      const mat = new THREE.MeshStandardMaterial({
        color: 0x0d1a2c, metalness: 0.25, roughness: 0.78,
        emissive: CYAN, emissiveIntensity: 0,
      });
      const w = alongX ? SIZE_Z / STRIPS : stripW;
      const geo = alongX
        ? new THREE.BoxGeometry(SIZE_X, 0.07, w * 0.9)
        : new THREE.BoxGeometry(w * 0.9, 0.07, SIZE_Z);
      const m = new THREE.Mesh(geo, mat);
      if (alongX) m.position.z = -SIZE_Z / 2 + w * (i + 0.5);
      else m.position.x = -SIZE_X / 2 + w * (i + 0.5);
      plane.add(m);
      row.push({ mat, glow: 0 });
    }
    strips.push({ row, alongX });

    // hairline outline of the active area
    const outline = new THREE.LineSegments(
      new THREE.EdgesGeometry(new THREE.BoxGeometry(SIZE_X + 0.12, 0.09, SIZE_Z + 0.12)), edgeMat);
    plane.add(outline);

    // readout board along one edge with status LEDs
    const board = new THREE.Mesh(
      alongX ? new THREE.BoxGeometry(0.22, 0.05, SIZE_Z) : new THREE.BoxGeometry(SIZE_X, 0.05, 0.22),
      boardMat);
    if (alongX) board.position.x = SIZE_X / 2 + 0.2; else board.position.z = SIZE_Z / 2 + 0.2;
    plane.add(board);
    const ledMat = new THREE.MeshBasicMaterial({ color: 0x3dffb4 });
    for (let k = 0; k < 3; k++) {
      const led = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.03, 0.05), ledMat);
      led.position.copy(board.position);
      led.position.y += 0.04;
      if (alongX) led.position.z = SIZE_Z / 2 - 0.25 - k * 0.15; else led.position.x = SIZE_X / 2 - 0.25 - k * 0.15;
      plane.add(led);
    }
    det.add(plane);
  }

  // support posts
  const postH = PLANE_GAP * (PLANES - 1) + 0.9;
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) {
    const post = new THREE.Mesh(new THREE.BoxGeometry(0.1, postH, 0.1), frameMat);
    post.position.set(sx * (SIZE_X / 2 + 0.12), 0, sz * (SIZE_Z / 2 + 0.12));
    det.add(post);
  }

  // floor grid
  const grid = new THREE.GridHelper(80, 80, 0x1c3a66, 0x0d1a2e);
  grid.position.y = planeY[0] - 1.6;
  grid.material.transparent = true;
  grid.material.opacity = 0.55;
  scene.add(grid);

  // dust / ambient particles
  const dustN = small() ? 250 : 600;
  const dustPos = new Float32Array(dustN * 3);
  for (let i = 0; i < dustN; i++) {
    dustPos[i * 3] = (Math.random() - 0.5) * 30;
    dustPos[i * 3 + 1] = (Math.random() - 0.5) * 14;
    dustPos[i * 3 + 2] = (Math.random() - 0.5) * 30;
  }
  const dustGeo = new THREE.BufferGeometry();
  dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPos, 3));
  const dust = new THREE.Points(dustGeo, new THREE.PointsMaterial({
    color: 0x6fa8ff, size: 0.035, transparent: true, opacity: 0.5, depthWrite: false,
  }));
  scene.add(dust);

  // ---------- Muons ----------
  const tex = glowTexture();
  const POOL = 24;
  const muons = [];
  const unitCyl = new THREE.CylinderGeometry(1, 1, 1, 6, 1, true);
  unitCyl.translate(0, 0.5, 0);
  const UP = new THREE.Vector3(0, 1, 0);

  for (let i = 0; i < POOL; i++) {
    const trailMat = new THREE.MeshBasicMaterial({ color: WHITE, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false });
    const trail = new THREE.Mesh(unitCyl, trailMat);
    const ghostMat = new THREE.MeshBasicMaterial({ color: BLUE, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false });
    const ghost = new THREE.Mesh(unitCyl, ghostMat);
    const head = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, color: 0xd8f4ff, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }));
    head.scale.setScalar(0.45);
    trail.visible = ghost.visible = head.visible = false;
    scene.add(trail, ghost, head);
    muons.push({ active: false, trail, ghost, head, start: new THREE.Vector3(), dir: new THREE.Vector3(), s: 0, len: 0, life: 0, crossed: 0 });
  }

  // hit markers (small flashes at the crossing point)
  const hitSprites = [];
  for (let i = 0; i < 60; i++) {
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, color: 0x7fe0ff, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }));
    sp.visible = false;
    scene.add(sp);
    hitSprites.push({ sp, life: 0 });
  }
  let hitIdx = 0;

  const SPEED = 11; // scene units / s
  const TRAIL = 2.4;
  let evt = 4200 + Math.floor(Math.random() * 800);
  let recent = [];

  function placeCyl(mesh, a, b, r) {
    const d = new THREE.Vector3().subVectors(b, a);
    const L = d.length();
    if (L < 1e-4) { mesh.visible = false; return; }
    mesh.position.copy(a);
    mesh.quaternion.setFromUnitVectors(UP, d.divideScalar(L));
    mesh.scale.set(r, L, r);
  }

  function spawn(base) {
    const m = muons.find(x => !x.active);
    if (!m) return;
    let dir, through;
    if (base) {
      dir = base.dir.clone().add(new THREE.Vector3((Math.random() - 0.5) * 0.04, 0, (Math.random() - 0.5) * 0.04)).normalize();
      through = base.through.clone().add(new THREE.Vector3((Math.random() - 0.5) * 2.2, 0, (Math.random() - 0.5) * 1.6));
    } else {
      const cosT = Math.pow(Math.random(), 1 / 3); // cos²θ flux
      const sinT = Math.sqrt(1 - cosT * cosT);
      const phi = Math.random() * Math.PI * 2;
      dir = new THREE.Vector3(sinT * Math.cos(phi), -cosT, sinT * Math.sin(phi));
      through = new THREE.Vector3((Math.random() - 0.5) * SIZE_X * 1.15, 0, (Math.random() - 0.5) * SIZE_Z * 1.15);
    }
    const back = 9 / Math.max(0.25, -dir.y);
    m.start.copy(through).addScaledVector(dir, -back);
    m.dir.copy(dir);
    m.s = 0;
    m.len = back * 2;
    m.life = 0;
    m.crossed = 0;
    m.theta = Math.acos(-dir.y) * 180 / Math.PI;
    m.active = true;
    m.trail.visible = m.ghost.visible = m.head.visible = true;
    m.trail.material.opacity = 0.9;
    m.ghost.material.opacity = 0;
    m.head.material.opacity = 1;
    return { dir, through };
  }

  function hit(p, x, z, m) {
    const S = strips[p];
    const coord = S.alongX ? z : x;
    const span = S.alongX ? SIZE_Z : SIZE_X;
    const i = Math.floor((coord + span / 2) / span * STRIPS);
    if (i < 0 || i >= STRIPS) return;
    S.row[i].glow = 1;
    const h = hitSprites[hitIdx++ % hitSprites.length];
    h.sp.position.set(x, planeY[p] + 0.06, z);
    h.sp.visible = true;
    h.life = 1;
    m.crossed++;
  }

  function step(m, dt) {
    const prev = m.start.clone().addScaledVector(m.dir, m.s);
    m.s += SPEED * dt;
    const pos = m.start.clone().addScaledVector(m.dir, m.s);
    // plane crossings
    for (let p = 0; p < PLANES; p++) {
      const y = planeY[p];
      if (prev.y > y && pos.y <= y) {
        const t = (prev.y - y) / (prev.y - pos.y);
        const x = prev.x + (pos.x - prev.x) * t;
        const z = prev.z + (pos.z - prev.z) * t;
        if (Math.abs(x) <= SIZE_X / 2 && Math.abs(z) <= SIZE_Z / 2) hit(p, x, z, m);
      }
    }
    const tail = m.start.clone().addScaledVector(m.dir, Math.max(0, m.s - TRAIL));
    placeCyl(m.trail, tail, pos, 0.014);
    m.head.position.copy(pos);
    // reconstructed-track ghost line grows behind the muon
    placeCyl(m.ghost, m.start, pos, 0.006);
    m.ghost.material.opacity = Math.min(0.5, m.ghost.material.opacity + dt * 0.6);

    if (m.s > m.len) {
      m.head.material.opacity = 0;
      m.trail.material.opacity = 0;
      m.life += dt;
      m.ghost.material.opacity = Math.max(0, 0.5 - m.life * 0.35);
      if (m.life === dt) {
        evt++;
        recent.push(performance.now());
        onEvent({ evt, hits: m.crossed, planes: PLANES, theta: m.theta });
      }
      if (m.ghost.material.opacity <= 0) {
        m.active = false;
        m.trail.visible = m.ghost.visible = m.head.visible = false;
      }
    }
  }

  // ---------- Post-processing ----------
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(new THREE.Vector2(1, 1), 0.8, 0.45, 0.42);
  composer.addPass(bloom);
  composer.addPass(new OutputPass());

  // ---------- Camera & interaction ----------
  const target = new THREE.Vector3(0, -0.2, 0);
  const mobileTarget = new THREE.Vector3(0, -5.2, 0);
  let az = 0.75, mouseX = 0, mouseY = 0, mx = 0, my = 0, scrollP = 0;
  window.addEventListener('pointermove', e => {
    mouseX = (e.clientX / window.innerWidth) * 2 - 1;
    mouseY = (e.clientY / window.innerHeight) * 2 - 1;
  }, { passive: true });
  window.addEventListener('scroll', () => {
    scrollP = Math.min(1.5, window.scrollY / window.innerHeight);
  }, { passive: true });

  function resize() {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    composer.setSize(w, h);
    bloom.setSize(w, h);
    camera.aspect = w / h;
    // shift the detector to the right on wide screens so the headline breathes
    if (w >= 860) camera.setViewOffset(w, h, -w * 0.21, 0, w, h);
    else camera.clearViewOffset();
    camera.fov = w < 860 ? 42 : 34;
    camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(canvas);
  resize();

  function placeCamera() {
    mx += (mouseX - mx) * 0.04;
    my += (mouseY - my) * 0.04;
    const portrait = canvas.clientHeight > canvas.clientWidth * 1.1;
    const r = (portrait ? 31 : small() ? 20 : 18.5) + scrollP * 5;
    const el = 0.32 + my * 0.06 + scrollP * 0.25;
    const a = az + mx * 0.18;
    camera.position.set(Math.cos(a) * Math.cos(el) * r, Math.sin(el) * r, Math.sin(a) * Math.cos(el) * r);
    camera.lookAt(portrait ? mobileTarget : target);
  }

  // ---------- Loop ----------
  let running = true, last = performance.now(), spawnT = 0;
  const io = new IntersectionObserver(([e]) => {
    running = e.isIntersecting;
    if (running) { last = performance.now(); requestAnimationFrame(loop); }
  });
  io.observe(canvas);
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden && running) { last = performance.now(); requestAnimationFrame(loop); }
  });

  function update(dt) {
    az += dt * 0.05;
    spawnT -= dt;
    if (spawnT <= 0) {
      const b = spawn();
      if (b && Math.random() < 0.14) { spawn(b); spawn(b); if (Math.random() < 0.5) spawn(b); } // small air shower
      spawnT = 0.25 + Math.random() * 0.55;
    }
    for (const m of muons) if (m.active) step(m, dt);
    for (const S of strips) for (const s of S.row) {
      if (s.glow > 0) { s.glow = Math.max(0, s.glow - dt * 1.1); }
      s.mat.emissiveIntensity = s.glow * s.glow * 3.2;
    }
    for (const h of hitSprites) if (h.life > 0) {
      h.life = Math.max(0, h.life - dt * 1.6);
      h.sp.material.opacity = h.life;
      h.sp.scale.setScalar(0.25 + (1 - h.life) * 0.5);
      if (!h.life) h.sp.visible = false;
    }
    dust.rotation.y += dt * 0.008;
    // rate over the last 10 s
    const now = performance.now();
    recent = recent.filter(t => now - t < 10000);
  }

  function loop(now) {
    if (!running || document.hidden) return;
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    update(dt);
    placeCamera();
    composer.render();
    requestAnimationFrame(loop);
  }

  if (reduced) {
    // static event display: advance the simulation without animating
    for (let i = 0; i < 4; i++) spawn();
    for (let k = 0; k < 60; k++) for (const m of muons) if (m.active && m.s < m.len * 0.62) step(m, 1 / 60);
    placeCamera();
    composer.render();
    window.addEventListener('resize', () => { resize(); composer.render(); });
    return { reduced: true };
  }

  requestAnimationFrame(loop);
  return { rate: () => recent.length / 10 };
}
