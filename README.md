# TDLI Muon Physics Group Website

> TDLI缪子物理课题组 — 上海交通大学李政道研究所

Official website for the Muon Physics Group led by Prof. Kim Siang Khaw (许金祥) at the Tsung-Dao Lee Institute (TDLI), Shanghai Jiao Tong University.

---

## Sections

| Section | Content |
|---------|---------|
| **Hero** | Group identity, affiliation, CTA |
| **About** | Group mission, "Who ordered that?", stats |
| **Research** | 4 pillars: Muon g-2, muEDM, SHINE Muon Source, Muography |
| **Team** | PI + 3 postdocs + 1 RA + 7 PhD students with real data |
| **Join Us** | Bilingual recruitment section — undergrad through postdoc |
| **News** | 6 latest highlights linking to existing WordPress site |
| **Education** | PHY1950, PHY6009, AI course, summer internships, Cosmic Watch |
| **Collaborations** | Fermilab, PSI, J-PARC, CERN, Swinburne/mDetect |
| **Timeline** | 2019–2026 milestones including NuFact 2026 |
| **Contact** | Formspree form + email + address + academic profile links |

---

## Quick Start

### 1. Deploy to GitHub Pages

```bash
git init
git add .
git commit -m "TDLI Muon Physics Group website v2"
git branch -M main
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

**Settings → Pages → Source:** Deploy from `main` / `/ (root)`.

### 2. Set Up Contact Form (Formspree)

1. Sign up at [formspree.io](https://formspree.io) (free: 50 submissions/month)
2. Create a form → copy the Form ID
3. In `index.html`, replace `YOUR_FORM_ID`:

```html
action="https://formspree.io/f/YOUR_ACTUAL_ID"
```

### 3. Custom Domain (Optional)

Create a `CNAME` file with your domain, e.g.:
```
muon.tdli.sjtu.edu.cn
```

---

## Project Structure

```
├── index.html              # Full single-page site
├── assets/
│   ├── css/style.css       # All styles
│   ├── js/main.js          # Nav, animations, form handler
│   └── img/                # Team photos, detector images (add here)
├── README.md
└── .gitignore
```

## Tech Stack

- **Pure HTML/CSS/JS** — no build step, no dependencies
- **Google Fonts** — Noto Sans SC + DM Sans + JetBrains Mono
- **Formspree** — serverless form backend
- **GitHub Pages** — free static hosting with HTTPS

## Updating Content

- **News**: Edit the `#news` section in `index.html` — each item links to the WordPress site
- **Team**: Edit the `#team` section — add photos to `assets/img/` and replace avatar divs with `<img>` tags
- **Timeline**: Add milestones to the `#journey` section

---

© 2026 TDLI Muon Physics Group · Tsung-Dao Lee Institute · Shanghai Jiao Tong University
