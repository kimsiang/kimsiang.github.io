# TDLI Muon Physics Group Website

> TDLI缪子物理课题组 — 上海交通大学李政道研究所

Official website for the Muon Physics Group led by Prof. Kim Siang Khaw (许金祥) at the Tsung-Dao Lee Institute (TDLI), Shanghai Jiao Tong University.

© 2026 TDLI Muon Physics Group · Tsung-Dao Lee Institute · Shanghai Jiao Tong University

## Development

Static site for GitHub Pages — no build needed to edit text: change `index.html` (every string has an English `.en` and Chinese `.zh` version) and `assets/css/style.css`.

The 3D hero (a simulated cosmic-muon tracker) lives in `src/hero.js` and is bundled with Three.js into `assets/js/hero.bundle.js`:

```bash
npm install
npm run build
```

Fonts (Space Grotesk, Inter, JetBrains Mono) are self-hosted in `assets/fonts/` so the site loads quickly inside mainland China.
