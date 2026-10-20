#!/usr/bin/env python3
"""Static site builder for the TDLI Muon Physics Group website.

    python3 tools/build.py

Reads   content/home.html            – home page body (hand-written, bilingual)
        content/pages/*.html         – page bodies (research, people, teaching, …)
        content/news/*.html + news.json
        content/publications.json    – refresh with tools/update_publications.py
Writes  index.html, *.html, news/*.html, muons/*.html
Local links inside content use the {ROOT} prefix, replaced per page depth.
"""
import html, json, os, re
from datetime import date
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, 'content')
YEAR = date.today().year

def bi(en, zh=None):
    """Bilingual span pair (zh falls back to en)."""
    return f'<span class="en">{en}</span><span class="zh">{zh if zh is not None else en}</span>'

# ------------------------------------------------------------------ navigation
NAV = [
    ('research.html', 'research', 'Research', '研究'),
    ('muons/index.html', 'muons', 'About Muons', '缪子科普'),
    ('people.html', 'people', 'People', '团队'),
    ('news/index.html', 'news', 'News', '动态'),
    ('publications.html', 'publications', 'Publications', '论文'),
    ('teaching.html', 'teaching', 'Teaching', '教学'),
    ('gallery.html', 'gallery', 'Gallery', '照片'),
    ('index.html#contact', 'contact', 'Contact', '联系'),
]
FOOT = [
    ('talks.html', 'Talks', '学术报告'), ('posters.html', 'Posters', '学术海报'),
    ('kim.html', 'PI profile', '个人主页'), ('index.html#joinus', 'Join us', '加入我们'),
]

def layout(path, title, desc, body, active='', home=False):
    depth = path.count('/')
    R = '../' * depth
    nav = '\n    '.join(
        f'<a href="{R}{h}"{" class=\"active\" aria-current=\"page\"" if k == active else ""}>{bi(en, zh)}</a>'
        for h, k, en, zh in NAV)
    foot = '\n      '.join(f'<a href="{R}{h}">{bi(en, zh)}</a>' for h, en, zh in FOOT)
    full_title = 'TDLI Muon Physics Group | TDLI缪子物理课题组 — 上海交通大学李政道研究所' if home else f'{title} · TDLI Muon Physics Group'
    out = f'''<!DOCTYPE html>
<html lang="en" data-lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(full_title)}</title>
  <meta name="description" content="{html.escape(desc)}">
  <meta name="theme-color" content="#04070c">
  <meta property="og:title" content="{html.escape(full_title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="TDLI Muon Physics Group">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="preload" href="{R}assets/fonts/space-grotesk-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="{R}assets/fonts/inter-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{R}assets/css/style.css">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='18' fill='%2304070c'/><text x='50' y='70' font-size='64' text-anchor='middle' fill='%232fc8ff' font-family='sans-serif'>μ</text></svg>">
  <script>try {{ var l = localStorage.getItem('lang'); if (l === 'zh' || l === 'en') {{ document.documentElement.dataset.lang = l; document.documentElement.lang = l === 'zh' ? 'zh-CN' : 'en'; }} }} catch (e) {{}}</script>
</head>
<body class="{"home" if home else "sub"}">

<a class="skip" href="#main">{bi('Skip to content', '跳到正文')}</a>

<header class="nav" id="nav">
  <a href="{R}index.html" class="brand" aria-label="TDLI Muon Physics Group — home">
    <span class="brand-mark">μ</span>
    <span class="brand-text"><b>TDLI</b> Muon Physics<small>{bi('Group', '缪子物理课题组')}</small></span>
  </a>
  <nav class="nav-links" id="nav-links" aria-label="Main">
    {nav}
  </nav>
  <div class="nav-right">
    <button class="lang" id="lang-toggle" type="button" aria-label="Switch language / 切换语言">
      <span data-l="en">EN</span><i></i><span data-l="zh">中文</span>
    </button>
    <a href="{R}index.html#joinus" class="btn btn-sm btn-primary nav-cta">{bi('Join us', '加入我们')}</a>
    <button class="burger" id="burger" type="button" aria-label="Menu" aria-expanded="false" aria-controls="nav-links"><i></i><i></i></button>
  </div>
</header>

<main id="main">
{body}
</main>

<footer class="foot">
  <div class="wrap foot-in">
    <div class="brand small"><span class="brand-mark">μ</span><span>© {YEAR} TDLI Muon Physics Group · {bi('Tsung-Dao Lee Institute · Shanghai Jiao Tong University', '李政道研究所 · 上海交通大学')}</span></div>
    <nav aria-label="Footer">
      {foot}
    </nav>
  </div>
</footer>

<script src="{R}assets/js/main.js" defer></script>
</body>
</html>
'''
    out = out.replace('{ROOT}', R)
    dest = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, 'w').write(out)
    return out

def phero(code, eyebrow_en, eyebrow_zh, title_html, lead_html='', crumbs='', scene='module'):
    return f'''<section class="phero">
  <div class="phero-grid" aria-hidden="true"></div>
  <div class="phero-floor" aria-hidden="true"></div>
  <canvas class="phero-3d" data-scene="{scene}" aria-hidden="true"></canvas>
  <div class="wrap">
    {crumbs}
    <p class="label"><span class="idx">{code}</span>{bi(eyebrow_en, eyebrow_zh)}</p>
    <h1 class="h1">{title_html}</h1>
    {f'<p class="lead">{lead_html}</p>' if lead_html else ''}
  </div>
</section>'''

# ------------------------------------------------------------------ prose transforms
def slug(t):
    t = re.sub(r'[^\w\s-]', '', t.lower()).strip()
    return re.sub(r'[\s_]+', '-', t)[:60] or 'section'

def prose(raw, ids=None, people=False):
    soup = BeautifulSoup(raw, 'html.parser')
    # headings: unwrap inline emphasis, add ids
    seen = set()
    for h in soup.find_all(['h2', 'h3', 'h4', 'h5']):
        for t in h.find_all(['strong', 'em']): t.unwrap()
        txt = h.get_text(' ', strip=True)
        hid = None
        for key, val in (ids or {}).items():
            if key.lower() in txt.lower() and val not in seen: hid = val; break
        hid = hid or slug(txt)
        while hid in seen: hid += '-2'
        seen.add(hid); h['id'] = hid
    # figcaption <code> -> text
    for fc in soup.find_all('figcaption'):
        for c in fc.find_all('code'): c.unwrap()
    # images: make zoomable
    for im in soup.find_all('img'):
        if im.parent.name != 'a':
            a = soup.new_tag('a', href=im['src'], **{'class': 'zoom'})
            im.wrap(a)
        else:
            im.parent['class'] = ['zoom']
            im.parent['href'] = im['src']
        # thumbnails in galleries use the small version
        if im.find_parent('div', class_='pgal'):
            im['src'] = im['src'].replace('.webp', '-sm.webp')
    # galleries: flatten to figures
    for g in soup.find_all('div', class_='pgal'):
        figs = g.find_all('figure')
        g.clear()
        for f in figs: g.append(f)
    # tables
    for t in soup.find_all('table'):
        w = soup.new_tag('div', **{'class': 'table-wrap'}); t.wrap(w)
    # external links
    for a in soup.find_all('a', href=True):
        if a['href'].startswith('http'):
            a['target'] = '_blank'; a['rel'] = 'noopener'
    if people:
        # figure (portrait) followed by <p> → person card
        for fig in list(soup.find_all('figure')):
            if fig.find_parent('div', class_='pgal'): continue
            nxt = fig.find_next_sibling()
            if nxt is not None and nxt.name == 'p':
                card = soup.new_tag('div', **{'class': 'pcard'})
                fig.insert_before(card)
                card.append(fig.extract()); card.append(nxt.extract())
        # group consecutive cards
        for card in list(soup.find_all('div', class_='pcard')):
            if card.parent.name == 'div' and 'pcards' in (card.parent.get('class') or []): continue
            box = soup.new_tag('div', **{'class': 'pcards'})
            card.insert_before(box)
            sib = card
            while sib is not None and sib.name == 'div' and 'pcard' in (sib.get('class') or []):
                nxt = sib.find_next_sibling()
                box.append(sib.extract())
                sib = nxt
        for hr in soup.find_all('hr'): hr.decompose()
    return str(soup)

def toc(raw, level='h2'):
    soup = BeautifulSoup(raw, 'html.parser')
    hs = soup.find_all(level)
    if len(hs) < 3: return ''
    items = ''.join(f'<li><a href="#{h["id"]}">{h.get_text(" ", strip=True)}</a></li>' for h in hs)
    return f'<nav class="toc" aria-label="On this page"><p class="mono">{bi("On this page", "本页目录")}</p><ol>{items}</ol></nav>'

def read(p): return open(os.path.join(C, p)).read()

def article(body, side=''):
    if side:
        return f'<section class="pbody"><div class="wrap with-side"><aside class="side">{side}</aside><div class="prose doc">{body}</div></div></section>'
    return f'<section class="pbody"><div class="wrap"><div class="prose doc">{body}</div></div></section>'

# ------------------------------------------------------------------ news
news = json.load(open(os.path.join(C, 'news.json')))

def _excerpt(slug, fallback=''):
    """First paragraph of the post body, so previews follow the edited text."""
    try:
        soup = BeautifulSoup(open(os.path.join(C, 'news', slug + '.html')).read(), 'html.parser')
    except FileNotFoundError:
        return fallback
    for p in soup.find_all('p'):
        t = re.sub(r'\s+', ' ', p.get_text(' ', strip=True)).strip()
        if len(t) > 40:
            return t[:240]
    return fallback

for _n in news:
    _n['excerpt'] = _excerpt(_n['slug'], _n.get('excerpt', ''))

def month(d):
    y, m, dd = d.split('-')
    return f'{y}.{m}.{dd}'

def news_rows(items):
    out = []
    for n in items:
        out.append(f'''<li class="rv"><a href="{{ROOT}}news/{n["slug"]}.html"><time datetime="{n["date"]}">{n["date"][:7].replace("-", ".")}</time><span class="n-cat">News</span><span class="n-t">{html.escape(n["title"])}<small>{html.escape(n["excerpt"][:150].rstrip())}{"…" if len(n["excerpt"]) > 150 else ""}</small></span><span class="arr">→</span></a></li>''')
    return '<ul class="news">\n      ' + '\n      '.join(out) + '\n    </ul>'

def build_news():
    years = sorted({n['date'][:4] for n in news}, reverse=True)
    chips = f'<button type="button" class="on" data-y="all">{bi("All", "全部")}</button>' + ''.join(
        f'<button type="button" data-y="{y}">{y}</button>' for y in years)
    cards = []
    for n in news:
        th = f'<img src="{{ROOT}}{n["thumb"]}" alt="" loading="lazy" decoding="async">' if n['thumb'] else '<span class="nc-ph">μ</span>'
        cards.append(f'''<li class="ncard" data-y="{n["date"][:4]}" data-q="{html.escape((n["title"] + " " + n["excerpt"]).lower())}">
        <a href="{{ROOT}}news/{n["slug"]}.html"><span class="nc-img">{th}</span><span class="nc-body"><time datetime="{n["date"]}">{month(n["date"])}</time><h3>{html.escape(n["title"])}</h3><p>{html.escape(n["excerpt"][:180])}</p></span></a></li>''')
    body = phero('NEWS', 'News & events', '新闻动态', bi('News &amp; events', '新闻动态'),
                 bi(f'{len(news)} stories from the group since {years[-1]} — conferences, beam tests, workshops, people and papers.',
                    f'自{years[-1]}年以来的{len(news)}条课题组动态——会议、束流测试、研讨会、成员与论文。'))
    body += f'''<section class="pbody"><div class="wrap">
  <div class="filters">
    <div class="chips" role="group" aria-label="Filter by year">{chips}</div>
    <label class="search"><span class="sr">Search</span><input type="search" id="news-q" placeholder="Search news / 搜索" autocomplete="off"></label>
  </div>
  <ul class="ncards" id="ncards">
      {"".join(cards)}
  </ul>
  <p class="empty" id="news-empty" hidden>{bi("No matching news.", "没有匹配的新闻。")}</p>
</div></section>'''
    layout('news/index.html', 'News', 'News and events from the TDLI Muon Physics Group.', body, 'news')
    for i, n in enumerate(news):
        newer = news[i - 1] if i > 0 else None
        older = news[i + 1] if i + 1 < len(news) else None
        crumbs = f'<p class="crumbs mono"><a href="{{ROOT}}news/index.html">{bi("News", "新闻动态")}</a> / {n["date"][:4]}</p>'
        hero = phero(month(n['date']), 'News', '新闻', html.escape(n['title']), crumbs=crumbs)
        pn = '<nav class="pn">'
        pn += f'<a class="prev" href="{{ROOT}}news/{older["slug"]}.html"><small>{bi("← Older", "← 更早")}</small>{html.escape(older["title"])}</a>' if older else '<span></span>'
        pn += f'<a class="next" href="{{ROOT}}news/{newer["slug"]}.html"><small>{bi("Newer →", "更新 →")}</small>{html.escape(newer["title"])}</a>' if newer else '<span></span>'
        pn += '</nav>'
        b = prose(read(f'news/{n["slug"]}.html'))
        body = hero + f'<section class="pbody"><div class="wrap"><article class="prose doc post">{b}</article>{pn}</div></section>'
        layout(f'news/{n["slug"]}.html', n['title'], n['excerpt'][:160] or n['title'], body, 'news')

# ------------------------------------------------------------------ publications
def build_publications():
    pubs = json.load(open(os.path.join(C, 'publications.json')))
    raw = read('pages/publications.html')
    soup = BeautifulSoup(raw, 'html.parser')
    # keep popular-science + review sections from the curated page, drop the old paper lists
    keep, on = [], False
    for el in list(soup.children):
        if getattr(el, 'name', None) == 'h2':
            t = el.get_text(strip=True)
            on = ('科普' in t or 'Review' in t)
        if on: keep.append(str(el))
    curated = prose(''.join(keep))
    curated = curated.replace('科普文章/媒体专访</h2>', '<span class="en">Popular science &amp; media</span><span class="zh">科普文章/媒体专访</span></h2>')
    cites = sum(p['cites'] for p in pubs)
    cs = sorted((p['cites'] for p in pubs), reverse=True)
    h = sum(1 for i, c in enumerate(cs, 1) if c >= i)
    kinds = {'journal': ('Journal articles', '期刊论文'), 'proceedings': ('Proceedings', '会议论文'),
             'preprint': ('Preprints', '预印本'), 'report': ('Reports', '报告'), 'thesis': ('Theses', '学位论文')}
    rows, cur = [], None
    for p in pubs:
        if p['year'] != cur:
            cur = p['year']
            rows.append(f'<li class="pyear" data-year="{cur}">{cur}</li>')
        url = p.get('url') or (f'https://doi.org/{p["doi"]}' if p['doi'] else f'https://arxiv.org/abs/{p["arxiv"]}' if p['arxiv'] else f'https://inspirehep.net/literature/{p["id"]}')
        auth = ', '.join(html.escape(a) for a in p['authors'])
        if p['collaboration']:
            auth = f'{html.escape(p["collaboration"])} Collaboration' + (f' ({auth} et al.)' if auth else '')
        elif p['author_count'] > len(p['authors']):
            auth += ' et al.'
        badges = []
        if p['arxiv']: badges.append(f'<a href="https://arxiv.org/abs/{p["arxiv"]}" target="_blank" rel="noopener">arXiv:{p["arxiv"]}</a>')
        if isinstance(p['id'], int): badges.append(f'<a href="https://inspirehep.net/literature/{p["id"]}" target="_blank" rel="noopener">INSPIRE</a>')
        if p['cites']: badges.append(f'<span class="cites" title="Citations (INSPIRE)">{p["cites"]} {bi("citations", "次引用")}</span>')
        big = 'big' if p['author_count'] > 50 else 'small'
        rows.append(f'''<li class="pub" data-kind="{p["kind"]}" data-size="{big}" data-q="{html.escape((p["title"] + " " + auth + " " + p["journal"]).lower())}">
        <span class="pk mono">{bi(*kinds[p["kind"]])}</span>
        <div><a class="pt" href="{url}" target="_blank" rel="noopener">{html.escape(p["title"])}</a>
        <p class="pa">{auth}</p>
        {f'<p class="pj">{html.escape(p["journal"])}</p>' if p["journal"] else ""}
        <p class="pb mono">{" · ".join(badges)}</p></div></li>''')
    chips = f'<button type="button" class="on" data-k="all">{bi("All", "全部")}</button>' + ''.join(
        f'<button type="button" data-k="{k}">{bi(*v)}</button>' for k, v in kinds.items() if any(p['kind'] == k for p in pubs))
    stats = f'''<div class="pstats">
      <div><b>{len(pubs)}</b>{bi("Publications", "论文")}</div>
      <div><b>{cites:,}</b>{bi("Citations", "引用")}</div>
      <div><b>{h}</b>{bi("h-index", "h指数")}</div>
      <div><b>{sum(1 for p in pubs if p["refereed"])}</b>{bi("Peer-reviewed", "同行评审")}</div>
    </div>'''
    body = phero('PUB', 'Publications', '论文发表', bi('Publications', '论文发表'), scene='ring', lead_html=
                 bi('Research output of the group, synced from <a href="https://inspirehep.net/authors/1114795" target="_blank" rel="noopener">INSPIRE-HEP</a> — also on <a href="https://scholar.google.com/citations?user=dyaRjrcAAAAJ" target="_blank" rel="noopener">Google Scholar</a>.',
                    '课题组研究成果，同步自<a href="https://inspirehep.net/authors/1114795" target="_blank" rel="noopener">INSPIRE-HEP</a>，亦可见<a href="https://scholar.google.com/citations?user=dyaRjrcAAAAJ" target="_blank" rel="noopener">Google Scholar</a>。'))
    body += f'''<section class="pbody"><div class="wrap">
  {stats}
  <div class="filters">
    <div class="chips" role="group" aria-label="Filter by type">{chips}</div>
    <label class="check"><input type="checkbox" id="pub-small"> {bi("Hide large-collaboration papers", "隐藏大型合作组论文")}</label>
    <label class="search"><span class="sr">Search</span><input type="search" id="pub-q" placeholder="Search title, author, journal / 搜索" autocomplete="off"></label>
  </div>
  <ol class="pubs" id="pubs">
      {"".join(rows)}
  </ol>
  <p class="empty" id="pub-empty" hidden>{bi("No matching publications.", "没有匹配的论文。")}</p>
  <p class="src mono">{bi(f"Data: INSPIRE-HEP, updated {date.today().isoformat()}", f"数据来源：INSPIRE-HEP，更新于{date.today().isoformat()}")}</p>
  <div class="prose doc curated">{curated}</div>
</div></section>'''
    layout('publications.html', 'Publications', 'Publications of the TDLI Muon Physics Group — Muon g-2, muEDM, SHINE muon source and muography.', body, 'publications')

# ------------------------------------------------------------------ pages
MUONS = [
    ('index', 'About Muons', '缪子简介'),
    ('fundamental-muon-physics', 'Fundamental Muon Physics', '缪子基础物理'),
    ('muon-sources', 'Muon Sources', '缪子源'),
    ('muon-detection-techniques', 'Muon Detection Techniques', '缪子探测技术'),
    ('applications-of-muons', 'Applications of Muons', '缪子的应用'),
    ('muonium', 'Muonium', '缪子素'),
    ('muography-applications', 'Muography Applications', '缪子成像应用'),
]

def build_muons():
    for i, (k, en, zh) in enumerate(MUONS):
        side = '<nav class="chap" aria-label="About Muons"><p class="mono">' + bi('About Muons', '缪子科普') + '</p><ol>' + ''.join(
            f'<li><a href="{{ROOT}}muons/{kk}.html"{" class=\"on\" aria-current=\"page\"" if kk == k else ""}><span class="mono">{j + 1:02d}</span>{bi(e, z)}</a></li>'
            for j, (kk, e, z) in enumerate(MUONS)) + '</ol></nav>'
        b = prose(read(f'pages/muons__{k}.html'))
        pn = '<nav class="pn">'
        pn += f'<a class="prev" href="{{ROOT}}muons/{MUONS[i - 1][0]}.html"><small>{bi("← Previous", "← 上一章")}</small>{bi(MUONS[i - 1][1], MUONS[i - 1][2])}</a>' if i > 0 else '<span></span>'
        pn += f'<a class="next" href="{{ROOT}}muons/{MUONS[i + 1][0]}.html"><small>{bi("Next →", "下一章 →")}</small>{bi(MUONS[i + 1][1], MUONS[i + 1][2])}</a>' if i + 1 < len(MUONS) else '<span></span>'
        pn += '</nav>'
        hero = phero(f'{i + 1:02d}/{len(MUONS):02d}', 'About Muons', '缪子科普', bi(en, zh),
                     bi('A primer on the muon — its physics, how we make and detect it, and what it is good for.',
                        '缪子入门——它的物理、产生与探测方式，以及广泛应用。') if k == 'index' else '', scene='muonium')
        body = hero + f'<section class="pbody"><div class="wrap with-side"><aside class="side">{side}</aside><div class="prose doc">{b}{pn}</div></div></section>'
        layout(f'muons/{k}.html', en, f'{en} — muon physics primer by the TDLI Muon Physics Group.', body, 'muons')

def page(path, key, code, en, zh, lead_en='', lead_zh='', active='', ids=None, people=False, with_toc=False, desc=None, pre='', scene='module'):
    b = prose(read(f'pages/{key}.html'), ids=ids, people=people)
    side = toc(b, 'h2' if people else 'h3') if with_toc else ''
    body = phero(code, en, zh, bi(en, zh), bi(lead_en, lead_zh) if lead_en else '', scene=scene) + pre + article(b, side)
    layout(path, en, desc or f'{en} — TDLI Muon Physics Group, Shanghai Jiao Tong University.', body, active)

def build_pages():
    page('research.html', 'research', 'R&D', 'Research', '研究方向',
         'Precision muon physics from Fermilab to PSI, a new muon source at SHINE, and muography beneath Shanghai.',
         '从费米实验室到PSI的精密缪子物理、SHINE新型缪子源，以及上海地下空间的缪子成像。',
         'research', ids={'Muon g-2': 'muon-g-2', 'Dipole': 'muon-edm', 'SHINE': 'shine-muon-source', 'Muography': 'muography'},
         with_toc=True, scene='ring')
    page('people.html', 'people', 'TEAM', 'People', '团队成员',
         'Current members, students and alumni of the TDLI Muon Physics Group.', '课题组现任成员、学生与校友。',
         'people', ids={'Former': 'former-members'}, people=True, with_toc=True)
    page('teaching.html', 'teaching', 'EDU', 'Teaching', '教学',
         'Courses, journal clubs, study groups, schools and the international summer research internship.',
         '课程、文献阅读会、教材研读、暑期/冬季学校与国际暑期科研实习。', 'teaching', with_toc=True)
    page('talks.html', 'talks', 'TALKS', 'Selected talks', '学术报告',
         'Talks by group members at national and international workshops, conferences and universities.',
         '课题组成员在国内外研讨会、学术会议及高校所作的报告。', 'publications', with_toc=False, scene='ring')
    page('posters.html', 'posters', 'POSTERS', 'Posters', '学术海报',
         'Posters presented by group members at national and international conferences.', '课题组成员在国内外会议上展示的海报。', 'publications', scene='ring')
    page('gallery.html', 'gallery', 'PHOTO', 'Photo gallery', '照片集',
         'Life in the lab and around the world — from building the Muon Tech Lab to Fermilab, PSI and KEK.',
         '实验室内外的点滴——从建设缪子技术实验室，到费米实验室、PSI与KEK。', 'gallery', with_toc=True)
    intro = '''<section class="pbody tight"><div class="wrap"><div class="prose doc"><div class="en-only">
<p><strong>Kim Siang Khaw (许金祥)</strong> is a Tenured Fellow of the Tsung-Dao Lee Institute and Tenured Associate Professor in the School of Physics and Astronomy, Shanghai Jiao Tong University, where he leads the Muon Physics Group. His research uses the muon as a probe — precision measurements of its anomalous magnetic moment and electric dipole moment — to test the Standard Model and search for new physics, alongside a new high-repetition-rate muon source at SHINE and muography for underground space in Shanghai.</p>
<p>Born in Penang, Malaysia, he studied and worked for 16 years in Japan (Osaka University of Foreign Studies, Kyoto University, University of Tokyo), Switzerland (ETH Zurich) and the USA (University of Washington) before moving to Shanghai, and works in Malay, Japanese, German, English and Chinese. Outside physics he enjoys badminton, guitar, cooking, durian and travel — more than 25 countries so far. The profile below is in Chinese.</p>
</div></div></div></section>'''
    page('kim.html', 'kim', 'PI', 'Kim Siang Khaw', '许金祥',
         'Principal Investigator · Tenured Associate Professor, TDLI & SPA, Shanghai Jiao Tong University',
         '课题组长 · 上海交通大学李政道研究所 / 物理与天文学院 长聘副教授', 'people', pre=intro)

def build_home():
    body = read('home.html').replace('{{HOME_NEWS}}', news_rows(news[:6]))
    layout('index.html', 'Home',
           'TDLI Muon Physics Group at Shanghai Jiao Tong University — precision muon physics, Muon g-2, muEDM, SHINE muon source, and muography. Led by Prof. Kim Siang Khaw (许金祥).',
           body, home=True)

if __name__ == '__main__':
    build_home(); build_pages(); build_muons(); build_news(); build_publications()
    n = sum(1 for d, _, fs in os.walk(ROOT) if not any(x in os.path.relpath(d, ROOT).split(os.sep) for x in ('.git', 'node_modules', 'content', 'tools')) for f in fs if f.endswith('.html'))
    print('built', n, 'html files')
