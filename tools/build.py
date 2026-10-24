#!/usr/bin/env python3
"""Static site builder for the TDLI Muon Physics Group website.

    python3 tools/build.py

Reads   content/home.html            – home page body (hand-written, bilingual)
        content/pages/*.html         – page bodies (research, people, teaching, …)
        content/news/*.html + news.json
        content/publications.json    – refresh with tools/update_publications.py
        content/members.json         – member sub-pages; papers via tools/update_members.py
Writes  index.html, *.html, news/*.html, muons/*.html, people/*.html
Local links inside content use the {ROOT} prefix, replaced per page depth.
"""
import html, json, os, re
from datetime import date
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, 'content')
YEAR = date.today().year

import hashlib as _h
ASK_V = _h.md5(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "js", "ask.js"), "rb").read()).hexdigest()[:8]
CSS_V = _h.md5(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "css", "style.css"), "rb").read()).hexdigest()[:8]

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
    ('results.html', 'Results', '代表性成果'), ('theses.html', 'Theses', '学位论文'), ('kim.html', 'PI profile', '个人主页'), ('index.html#joinus', 'Join us', '加入我们'),
]

def data_date(name):
    """Date the INSPIRE data was last refreshed: the data file's last commit (uncommitted changes count as today)."""
    import subprocess
    f = os.path.join(C, name)
    try:
        dirty = subprocess.run(['git', 'status', '--porcelain', '--', f], capture_output=True, text=True, cwd=C).stdout.strip()
        d = '' if dirty else subprocess.run(['git', 'log', '-1', '--format=%cs', '--', f], capture_output=True, text=True, cwd=C).stdout.strip()
        if d: return d
    except Exception:
        pass
    return date.today().isoformat()

SITE = 'https://kimsiang.github.io/'
OG_DEFAULT = ('assets/video/group-film-poster.webp?v=6', 960, 540)
PAGES = []   # (url, lastmod) of every page written by layout(); feeds sitemap.xml

def canonical(path):
    """Public URL of an output path: index.html files collapse to their directory."""
    return SITE + (path[:-len('index.html')] if path.endswith('index.html') else path)

def img_size(rel):
    try:
        from PIL import Image
        return Image.open(os.path.join(ROOT, rel.split('?')[0])).size
    except Exception:
        return None

def og_block(path, image):
    """Open Graph url + image for a page, so every shared link renders a card."""
    rel, w, h = OG_DEFAULT
    if image:
        s = img_size(image)
        if s: rel, (w, h) = image, s
    out = f'  <meta property="og:url" content="{canonical(path)}">\n'
    out += f'  <meta property="og:image" content="{SITE}{rel}">\n'
    out += f'  <meta property="og:image:width" content="{w}">\n  <meta property="og:image:height" content="{h}">\n'
    return out

def layout(path, title, desc, body, active='', home=False, image=None, lastmod=None):
    depth = path.count('/')
    R = '../' * depth
    PAGES.append((canonical(path), lastmod))
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
{og_block(path, image)}  <meta name="twitter:card" content="summary_large_image">
  <link rel="canonical" href="{canonical(path)}">
  <link rel="alternate" type="application/atom+xml" title="TDLI Muon Physics Group — news" href="{R}feed.xml">
  <link rel="preload" href="{R}assets/fonts/space-grotesk-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="{R}assets/fonts/inter-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{R}assets/css/style.css?v={CSS_V}">
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
{"<script src=\"assets/js/ask.js?v=" + ASK_V + "\" defer></script>" if home else ""}
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
            if fig.find_parent('div', class_='pgal') or fig.find_parent('div', class_='pcard'): continue
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

# Bilingual news: content/news/<slug>.html is the original post; an optional
# translation lives in content/news/zh/<slug>.html (or content/news/en/<slug>.html
# when the original is in Chinese). news.json may carry title_en / title_zh.
def news_src(slug, lang):
    for f in (os.path.join(C, 'news', lang, slug + '.html'), os.path.join(C, 'news', slug + '.html')):
        if os.path.exists(f): return open(f).read()
    return ''

def _excerpt(raw, fallback=''):
    """First paragraph of the post body, so previews follow the edited text."""
    soup = BeautifulSoup(raw, 'html.parser')
    for p in soup.find_all('p'):
        t = re.sub(r'\s+', ' ', p.get_text(' ', strip=True)).strip()
        if len(t) > 40 or (re.search(r'[\u4e00-\u9fff]', t) and len(t) > 15):
            return t[:240]
    return fallback

for _n in news:
    _n['t_en'] = _n.get('title_en') or _n['title']
    _n['t_zh'] = _n.get('title_zh') or _n['title']
    _n['excerpt'] = _excerpt(news_src(_n['slug'], 'en'), _n.get('excerpt', ''))
    _n['excerpt_zh'] = _excerpt(news_src(_n['slug'], 'zh'), _n['excerpt'])

def ntitle(n):
    return bi(html.escape(n['t_en']), html.escape(n['t_zh']))

def nexc(n, k):
    e, z = n['excerpt'], n['excerpt_zh']
    cut = lambda s: html.escape(s[:k].rstrip()) + ('…' if len(s) > k else '')
    return bi(cut(e), cut(z))

def month(d):
    y, m, dd = d.split('-')
    return f'{y}.{m}.{dd}'

def news_rows(items):
    out = []
    for n in items:
        th = f'<img src="{{ROOT}}{n["thumb"]}" alt="" loading="lazy" decoding="async">' if n.get('thumb') else '<span class="nc-ph">μ</span>'
        out.append(f'''<li class="rv"><a href="{{ROOT}}news/{n["slug"]}.html"><span class="n-img">{th}</span><span class="n-body"><span class="n-meta"><time datetime="{n["date"]}">{n["date"][:7].replace("-", ".")}</time><span class="n-cat">News</span></span><span class="n-t">{ntitle(n)}<small>{nexc(n, 150)}</small></span></span><span class="arr">→</span></a></li>''')
    return '<ul class="news">\n      ' + '\n      '.join(out) + '\n    </ul>'

def build_news():
    years = sorted({n['date'][:4] for n in news}, reverse=True)
    chips = f'<button type="button" class="on" data-y="all">{bi("All", "全部")}</button>' + ''.join(
        f'<button type="button" data-y="{y}">{y}</button>' for y in years)
    cards = []
    for n in news:
        th = f'<img src="{{ROOT}}{n["thumb"]}" alt="" loading="lazy" decoding="async">' if n['thumb'] else '<span class="nc-ph">μ</span>'
        cards.append(f'''<li class="ncard" data-y="{n["date"][:4]}" data-q="{html.escape((n["t_en"] + " " + n["t_zh"] + " " + n["excerpt"] + " " + n["excerpt_zh"]).lower())}">
        <a href="{{ROOT}}news/{n["slug"]}.html"><span class="nc-img">{th}</span><span class="nc-body"><time datetime="{n["date"]}">{month(n["date"])}</time><h3>{ntitle(n)}</h3><p>{nexc(n, 180)}</p></span></a></li>''')
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
    layout('news/index.html', 'News', 'News and events from the TDLI Muon Physics Group.', body, 'news', lastmod=news[0]['date'])
    for i, n in enumerate(news):
        newer = news[i - 1] if i > 0 else None
        older = news[i + 1] if i + 1 < len(news) else None
        crumbs = f'<p class="crumbs mono"><a href="{{ROOT}}news/index.html">{bi("News", "新闻动态")}</a> / {n["date"][:4]}</p>'
        hero = phero(month(n['date']), 'News', '新闻', ntitle(n), crumbs=crumbs)
        pn = '<nav class="pn">'
        pn += f'<a class="prev" href="{{ROOT}}news/{older["slug"]}.html"><small>{bi("← Older", "← 更早")}</small>{ntitle(older)}</a>' if older else '<span></span>'
        pn += f'<a class="next" href="{{ROOT}}news/{newer["slug"]}.html"><small>{bi("Newer →", "更新 →")}</small>{ntitle(newer)}</a>' if newer else '<span></span>'
        pn += '</nav>'
        en, zh = news_src(n['slug'], 'en'), news_src(n['slug'], 'zh')
        b = prose(en) if en == zh else f'<div class="en">{prose(en)}</div><div class="zh">{prose(zh)}</div>'
        body = hero + f'<section class="pbody"><div class="wrap"><article class="prose doc post">{b}</article>{pn}</div></section>'
        layout(f'news/{n["slug"]}.html', n['t_en'], n['excerpt'][:160] or n['t_en'], body, 'news', image=n.get('thumb'), lastmod=n['date'])

# ------------------------------------------------------------------ publications
KINDS = {'journal': ('Journal articles', '期刊论文'), 'proceedings': ('Proceedings', '会议论文'),
         'preprint': ('Preprints', '预印本'), 'report': ('Reports', '报告'), 'thesis': ('Theses', '学位论文')}

SHANGHAI = '2020'   # first full year after the PI moved to TDLI, Shanghai

def pub_rows(pubs, era=False):
    rows, cur = [], None
    for i, p in enumerate(pubs):
        if era and i == 0 and p['year'] >= SHANGHAI:
            rows.append('<li class="pera">' + bi('Since moving to Shanghai (TDLI) · 2020 –', '来到上海（李政道研究所）之后 · 2020 –') + '</li>')
        if era and cur is not None and cur >= SHANGHAI > p['year']:
            rows.append('<li class="pera pre">' + bi('Before Shanghai · 2012 – 2019', '来上海之前 · 2012 – 2019') + '</li>')
        if p['year'] != cur:
            cur = p['year']
            tag = ('<span class="sh-pill mono">' + bi('Shanghai', '上海') + '</span>') if era and cur >= SHANGHAI else ''
            rows.append(f'<li class="pyear" data-year="{cur}">{cur}{tag}</li>')
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
        rows.append(f'''<li class="pub" data-kind="{p["kind"]}" data-size="{big}" data-era="{'sh' if p['year'] >= SHANGHAI else 'pre'}" data-q="{html.escape((p["title"] + " " + auth + " " + p["journal"]).lower())}">
        <span class="pk mono">{bi(*KINDS[p["kind"]])}</span>
        <div><a class="pt" href="{url}" target="_blank" rel="noopener">{html.escape(p["title"])}</a>
        <p class="pa">{auth}</p>
        {f'<p class="pj">{html.escape(p["journal"])}</p>' if p["journal"] else ""}
        <p class="pb mono">{" · ".join(badges)}</p></div></li>''')
    return rows

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
    rows = pub_rows(pubs, era=True)
    n_sh = sum(1 for p in pubs if p['year'] >= SHANGHAI)
    chips = f'<button type="button" class="on" data-k="all">{bi("All", "全部")}</button>' + ''.join(
        f'<button type="button" data-k="{k}">{bi(*v)}</button>' for k, v in KINDS.items() if any(p['kind'] == k for p in pubs))
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
    <label class="check"><input type="checkbox" id="pub-sh"> {bi(f"Since moving to Shanghai (2020 –) · {n_sh}", f"来上海后（2020 –）· {n_sh} 篇")}</label>
    <label class="check"><input type="checkbox" id="pub-small"> {bi("Hide large-collaboration papers", "隐藏大型合作组论文")}</label>
    <label class="search"><span class="sr">Search</span><input type="search" id="pub-q" placeholder="Search title, author, journal / 搜索" autocomplete="off"></label>
  </div>
  <ol class="pubs" id="pubs">
      {"".join(rows)}
  </ol>
  <p class="empty" id="pub-empty" hidden>{bi("No matching publications.", "没有匹配的论文。")}</p>
  <p class="src mono">{bi(f"Data: INSPIRE-HEP, updated {data_date('publications.json')}", f"数据来源：INSPIRE-HEP，更新于{data_date('publications.json')}")}</p>
  <div class="prose doc curated">{curated}</div>
</div></section>'''
    layout('publications.html', 'Publications', 'Publications of the TDLI Muon Physics Group — Muon g-2, muEDM, SHINE muon source and muography.', body, 'publications')

# ------------------------------------------------------------------ member sub-pages
MEMBERS = json.load(open(os.path.join(C, 'members.json')))
PI_SLUG = 'kim-siang-khaw'   # the PI's profile lives at kim.html; people/<PI_SLUG>.html just redirects there
CODES = {'Principal Investigator': 'PI', 'Research Assistant': 'RA', 'Postdoctoral Researcher': 'POSTDOC', 'Doctoral Student': 'PHD', "Master's Student": 'MSC'}

def link_members(raw):
    """On the People page, link each current member's name to their sub-page."""
    soup = BeautifulSoup(raw, 'html.parser')
    for m in MEMBERS:
        href = '{ROOT}kim.html' if m['slug'] == PI_SLUG else '{ROOT}people/' + m['slug'] + '.html'
        for st in soup.find_all('strong'):
            if st.find_parent('a') or not st.get_text(strip=True).startswith(m['name']): continue
            a = soup.new_tag('a', href=href, **{'class': 'plink'})
            st.wrap(a)
            more = BeautifulSoup(f'<a class="pmore mono" href="{href}">{bi("Profile &amp; papers →", "个人主页与论文 →")}</a>', 'html.parser')
            a.find_parent('p').append(more)
            break
    return str(soup)

def build_members():
    pubs = json.load(open(os.path.join(C, 'member-publications.json')))
    today = data_date('member-publications.json')
    for m in MEMBERS:
        if m['slug'] == PI_SLUG:
            open(os.path.join(ROOT, 'people', PI_SLUG + '.html'), 'w').write(
                '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Kim Siang Khaw · TDLI Muon Physics Group</title>'
                '<link rel="canonical" href="https://kimsiang.github.io/kim.html"><meta name="robots" content="noindex">'
                '<meta http-equiv="refresh" content="0; url=../kim.html"></head>'
                '<body><p>This page has moved to <a href="../kim.html">kim.html</a>.</p></body></html>\n')
            continue
        role_en, role_zh = m['role']
        name = html.escape(m['name'])
        title = name + (f' <span class="zh-name">{m["zh"]}</span>' if m['zh'] else '')
        lead_en = f'{role_en} · since {m["since"]}' + (f' · {m["topics"][0]}' if m['topics'] else '')
        lead_zh = f'{role_zh} · {m["since"]} 起' + (f' · {m["topics"][1]}' if m['topics'] else '')
        crumbs = '<p class="crumbs mono"><a href="{ROOT}people.html">' + bi('People', '团队成员') + '</a> / ' + bi(role_en, role_zh) + '</p>'
        hero = phero(CODES.get(role_en, 'TEAM'), 'People', '团队成员', title, bi(lead_en, lead_zh), crumbs=crumbs)

        links = []
        if m.get('orcid'):
            links.append(f'<a href="https://orcid.org/{m["orcid"]}" target="_blank" rel="noopener"><b>ORCID</b><span>{m["orcid"]}</span></a>')
        if m.get('inspire'):
            links.append(f'<a href="https://inspirehep.net/authors/{m["inspire"]}" target="_blank" rel="noopener"><b>INSPIRE-HEP</b><span>{m["inspire"]}</span></a>')
        if m.get('scholar'):
            links.append(f'<a href="https://scholar.google.com/citations?user={m["scholar"]}" target="_blank" rel="noopener"><b>Google Scholar</b><span>{m["scholar"]}</span></a>')
        none = '<span class="faint">' + bi('Not yet available', '暂无') + '</span>'
        photo = '{ROOT}' + m['photo']
        side = ((f'<figure class="mphoto"><a class="zoom" href="{photo}"><img src="{photo}" alt="{name}" loading="lazy" decoding="async"></a></figure>' if m['photo'] else '')
                + '<p class="mono mlabel">' + bi('Profiles', '学术主页') + '</p>'
                + '<div class="mlinks">' + (''.join(links) or none) + '</div>')

        edu = ''.join(f'<li><b>{html.escape(y)}</b><span>{bi(html.escape(en), html.escape(zh))}</span></li>'
                      for y, en, zh in m['education'])
        awards = (f'<ul class="mtl">' + ''.join(f'<li><b>{html.escape(y)}</b><span>{bi(html.escape(en), html.escape(zh))}</span></li>'
                                            for y, en, zh in m.get('awards', [])) + '</ul>'
                  if m.get('awards') else '<p>' + bi('No awards listed yet.', '暂无。') + '</p>')
        mine = json.load(open(os.path.join(C, 'publications.json'))) if m.get('all_pubs') else pubs.get(m['slug'], [])
        if mine:
            cites = sum(p['cites'] for p in mine)
            plist = ('<p class="mcount mono">'
                     + bi(f'{len(mine)} papers · {cites:,} citations (INSPIRE-HEP)', f'{len(mine)} 篇论文 · 引用 {cites:,} 次（INSPIRE-HEP）')
                     + '</p><ol class="pubs">' + ''.join(pub_rows(mine)) + '</ol>')
        else:
            plist = '<p>' + bi('No publications listed yet.', '暂无论文。') + '</p>'
        body = ('<h2 id="background">' + bi('Background', '教育与经历') + '</h2>'
                + f'<ul class="mtl">{edu}</ul>'
                + '<h2 id="awards">' + bi('Awards', '荣誉奖励') + '</h2>' + awards
                + '<h2 id="publications">' + bi('Publications', '论文发表') + '</h2>' + plist
                + '<p class="src mono">' + bi(f'Data: INSPIRE-HEP, updated {today}', f'数据来源：INSPIRE-HEP，更新于{today}') + '</p>')
        out = (hero + '<section class="pbody"><div class="wrap with-side">'
               + f'<aside class="side mside">{side}</aside><div class="prose doc member">{body}</div></div></section>')
        layout(f'people/{m["slug"]}.html', m['name'],
               f'{m["name"]} — {role_en}, TDLI Muon Physics Group, Shanghai Jiao Tong University.', out, 'people')

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
                     bi('Right now, cosmic muons are passing through you. Meet the particle behind them — where it comes from, why physicists love it, and how you can see it yourself.',
                        '此刻，宇宙线缪子正穿过你的身体。来认识这种粒子——它从哪里来，物理学家为何钟爱它，以及你如何亲眼看见它。') if k == 'index' else '', scene='muonium')
        body = hero + f'<section class="pbody"><div class="wrap with-side"><aside class="side">{side}</aside><div class="prose doc mu-doc">{b}{pn}</div></div></section>'
        layout(f'muons/{k}.html', en, f'{en} — muon physics primer by the TDLI Muon Physics Group.', body, 'muons')

def page(path, key, code, en, zh, lead_en='', lead_zh='', active='', ids=None, people=False, with_toc=False, desc=None, pre='', scene='module'):
    b = prose(read(f'pages/{key}.html'), ids=ids, people=people)
    if people: b = link_members(b)
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
    import kim, sys; kim.build_kim(sys.modules[__name__])

def build_home():
    body = read('home.html').replace('{{HOME_NEWS}}', news_rows(news[:6]))
    layout('index.html', 'Home',
           'TDLI Muon Physics Group at Shanghai Jiao Tong University — precision muon physics, Muon g-2, muEDM, SHINE muon source, and muography. Led by Prof. Kim Siang Khaw (许金祥).',
           body, home=True)

# ------------------------------------------------------------------ theses archive
LEVELS = {'phd': ('PhD', '博士'), 'msc': ("Master's", '硕士'), 'bsc': ("Bachelor's", '本科'), 'proj': ('Project', '科研项目')}

def build_theses():
    d = json.load(open(os.path.join(C, 'theses.json')))
    th = sorted(d['theses'], key=lambda t: (t['year'], t.get('date', ''), {'phd': 2, 'msc': 1, 'bsc': 0}[t['level']]), reverse=True)
    slugs = {m['slug'] for m in MEMBERS}

    def who(name, zh='', slug=''):
        n = html.escape(name) + (f'<span class="cjk">【{zh}】</span>' if zh else '')
        return f'<a href="{{ROOT}}people/{slug}.html">{n}</a>' if slug in slugs else n

    def row(k, kind_html, title_html, sub, badges, q):
        return (f'<li class="pub" data-k="{k}" data-q="{html.escape(q.lower())}"><span class="pk mono">{kind_html}</span>'
                f'<div>{title_html}<p class="pa">{sub}</p>'
                + (f'<p class="pb mono">{" · ".join(badges)}</p>' if badges else '') + '</div></li>')

    rows = ['<li class="pyear">' + bi('Completed theses', '已完成学位论文') + '</li>']
    for t in th:
        title = html.escape(t['title']) if t['title'] else ('<span class="faint">' + bi('Title to be added', '题目待补充') + '</span>')
        if t.get('title_zh'):
            title += f'<br><span class="cjk">{html.escape(t["title_zh"])}</span>'
        url = t.get('pdf') or (f'https://doi.org/{t["doi"]}' if t.get('doi') else '')
        title_html = f'<a class="pt" href="{url}" target="_blank" rel="noopener">{title}</a>' if url else f'<p class="pt">{title}</p>'
        sub = who(t['name'], t.get('zh', ''), t.get('slug', '')) + (f' · {html.escape(t["topic"])}' if t.get('topic') else '')
        badges = [str(t.get('date') or t['year'])]
        if t.get('now'):
            badges.append(bi('Now: ', '现：') + html.escape(t['now']))
        if t.get('pdf'):
            badges.append(f'<a href="{t["pdf"]}" target="_blank" rel="noopener">PDF</a>')
        if t.get('doi'):
            badges.append(f'<a href="https://doi.org/{t["doi"]}" target="_blank" rel="noopener">DOI</a>')
        if t.get('news'):
            badges.append(f'<a href="{{ROOT}}news/{t["news"]}.html">' + bi('News', '新闻') + '</a>')
        rows.append(row(t['level'], bi(*LEVELS[t['level']]) + f'<br>{t["year"]}', title_html, sub, badges,
                        ' '.join([t['name'], t.get('zh', ''), t['title'], t.get('topic', ''), t.get('now', '')])))

    cur = [m for m in MEMBERS if m['role'][0] in ('Doctoral Student', "Master's Student")]
    cur.sort(key=lambda m: (m['role'][0] != 'Doctoral Student', m['since']))
    if cur:
        rows.append('<li class="pyear">' + bi('In progress', '在读') + '</li>')
        for m in cur:
            lv = 'phd' if m['role'][0] == 'Doctoral Student' else 'msc'
            topic = bi(*m['topics']) if m['topics'] else bi('Thesis topic to be announced', '课题待定')
            rows.append(row(lv, bi(*LEVELS[lv]) + '<br>' + bi('in progress', '在读'), f'<p class="pt">{topic}</p>',
                            who(m['name'], m['zh'], m['slug']), [bi(f'Since {m["since"]}', f'{m["since"]} 起')],
                            ' '.join([m['name'], m['zh']] + m['topics'])))

    rows.append('<li class="pyear">' + bi('Student research projects', '学生科研项目') + '</li>')
    for p in d['projects']:
        names = ', '.join(who(n, z) for n, z in p['names'])
        badges = [p['period'] + (' · ' + bi('ongoing', '进行中') if p.get('ongoing') else '')]
        if p.get('note'):
            badges.append(html.escape(p['note']))
        if p.get('news'):
            badges.append(f'<a href="{{ROOT}}news/{p["news"]}.html">' + bi('News', '新闻') + '</a>')
        topic = html.escape(p['topic']) if p['topic'] else bi(p['program'], p['program_zh'])
        rows.append(row('proj', bi(*LEVELS['proj']), f'<p class="pt">{topic}</p>',
                        bi(html.escape(p['program']), p['program_zh']) + ' · ' + names, badges,
                        ' '.join([p['program'], p['program_zh'], p['topic']] + [x for n in p['names'] for x in n])))

    n_proj = len(d['projects'])
    n_stu = len({n for p in d['projects'] for n, _ in p['names']})
    stats = ('<div class="pstats">'
             f'<div><b>{len(th)}</b>{bi("Completed theses", "已完成学位论文")}</div>'
             f'<div><b>{len(cur)}</b>{bi("Theses in progress", "在读研究生")}</div>'
             f'<div><b>{n_proj}</b>{bi("Student projects", "学生科研项目")}</div>'
             f'<div><b>{n_stu}</b>{bi("Project students", "参与项目学生")}</div></div>')
    keys = [k for k in LEVELS if k == 'proj' or any(t['level'] == k for t in th) or (k in ('phd', 'msc') and cur)]
    chips = f'<button type="button" class="on" data-k="all">{bi("All", "全部")}</button>' + ''.join(
        f'<button type="button" data-k="{k}">{bi("Projects", "科研项目") if k == "proj" else bi(*LEVELS[k])}</button>' for k in keys)
    body = phero('THESIS', 'People', '团队成员', bi('Theses &amp; student research', '学位论文与学生科研'), scene='ring', lead_html=bi(
        'Bachelor’s, Master’s and PhD theses supervised in the group, the theses now in progress, and the undergraduate and high-school research projects hosted since 2020.',
        '课题组指导完成的本科、硕士与博士学位论文、在读研究生课题，以及2020年以来承担的本科生与高中生科研项目。'))
    join = bi('Want to do your thesis with us? <a href="{ROOT}index.html#joinus">Join us →</a>',
              '想在课题组完成毕业论文？<a href="{ROOT}index.html#joinus">加入我们 →</a>')
    body += ('<section class="pbody"><div class="wrap">' + stats
             + '<div class="filters"><div class="chips" role="group" aria-label="Filter by level">' + chips + '</div>'
             + '<label class="search"><span class="sr">Search</span><input type="search" id="pub-q" placeholder="Search name, title, topic / 搜索" autocomplete="off"></label></div>'
             + '<ol class="pubs" id="pubs">' + ''.join(rows) + '</ol>'
             + '<p class="empty" id="pub-empty" hidden>' + bi('No matching entries.', '没有匹配的条目。') + '</p>'
             + '<p class="src mono">' + join + '</p></div></section>')
    layout('theses.html', 'Theses', 'Theses and student research projects of the TDLI Muon Physics Group, Shanghai Jiao Tong University.', body, 'people')


# ------------------------------------------------------------------ reach: 404, feed, sitemap, robots
def build_404():
    body = phero('404', 'Not found', '未找到', bi('This page has decayed', '这个页面已经衰变了'),
                 bi('Like a muon after 2.2 microseconds, the page you asked for is no longer here. The links below will get you back on track.',
                    '就像缪子在2.2微秒后一样，您要找的页面已不在此处。请通过下方链接返回。'))
    body += f'''<section class="pbody"><div class="wrap">
  <p class="actions"><a class="btn btn-primary" href="/index.html">{bi('Home', '首页')}</a> <a class="btn" href="/news/index.html">{bi('News', '新闻动态')}</a> <a class="btn" href="/publications.html">{bi('Publications', '论文')}</a> <a class="btn" href="/people.html">{bi('People', '团队')}</a></p>
</div></section>'''
    out = layout('404.html', 'Page not found', 'The page you asked for is not on the TDLI Muon Physics Group site.', body)
    PAGES.pop()   # not for the sitemap
    # GitHub Pages serves 404.html from any depth, so every relative link must become site-absolute.
    out = re.sub(r'(href|src)="(?!https?:|#|/|data:|mailto:)', r'\1="/', out)
    out = out.replace('<meta name="theme-color"', '<meta name="robots" content="noindex">\n  <meta name="theme-color"')
    open(os.path.join(ROOT, '404.html'), 'w').write(out)

def build_feed(limit=30):
    """Atom feed of the latest news posts (feed.xml)."""
    items = []
    for n in news[:limit]:
        url = canonical(f'news/{n["slug"]}.html')
        img = f'\n    <link rel="enclosure" type="image/webp" href="{SITE}{n["thumb"]}"/>' if n.get('thumb') else ''
        items.append(f'''  <entry>
    <title>{html.escape(n["t_en"])}</title>
    <link href="{url}"/>{img}
    <id>{url}</id>
    <updated>{n["date"]}T00:00:00+08:00</updated>
    <summary>{html.escape(n["excerpt"])}</summary>
  </entry>''')
    feed = f'''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>TDLI Muon Physics Group — news</title>
  <subtitle>News and events from the Muon Physics Group at the Tsung-Dao Lee Institute, Shanghai Jiao Tong University</subtitle>
  <link href="{SITE}feed.xml" rel="self"/>
  <link href="{SITE}news/"/>
  <id>{SITE}</id>
  <updated>{news[0]["date"]}T00:00:00+08:00</updated>
  <author><name>TDLI Muon Physics Group</name></author>
{chr(10).join(items)}
</feed>
'''
    open(os.path.join(ROOT, 'feed.xml'), 'w').write(feed)

def build_sitemap():
    seen, rows = set(), []
    for url, lastmod in PAGES:
        if url in seen: continue
        seen.add(url)
        lm = f'<lastmod>{lastmod}</lastmod>' if lastmod else ''
        rows.append(f'  <url><loc>{html.escape(url)}</loc>{lm}</url>')
    open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + '\n'.join(rows) + '\n</urlset>\n')
    open(os.path.join(ROOT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nDisallow: /content/\nDisallow: /tools/\n\nSitemap: {SITE}sitemap.xml\n')
    return len(rows)


if __name__ == '__main__':
    build_home(); build_pages(); build_muons(); build_news(); build_publications(); build_members(); build_theses()
    import results, sys; results.build_results(sys.modules[__name__])
    build_404(); build_feed(); print('sitemap:', build_sitemap(), 'urls')
    n = sum(1 for d, _, fs in os.walk(ROOT) if not any(x in os.path.relpath(d, ROOT).split(os.sep) for x in ('.git', 'node_modules', 'content', 'tools')) for f in fs if f.endswith('.html'))
    print('built', n, 'html files')
