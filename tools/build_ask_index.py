#!/usr/bin/env python3
"""Build the corpus behind the home-page "Ask the group" bar.

    python3 tools/build_ask_index.py        # writes assets/data/ask-index.json
    python3 tools/build_ask_index.py --offline   # skip INSPIRE, reuse cached abstracts

Sources
  * content/publications.json (+ publications-extra.json) — every paper, with the
    abstract and keywords fetched from INSPIRE-HEP (cached in content/abstracts.json)
  * content/pages/*.html  — Research, About Muons chapters, Teaching, PI profile
  * content/news/*.html   — news posts
  * content/members.json  — one short entry per member

The index is plain JSON; assets/js/ask.js does BM25 retrieval in the browser, so the
feature works on GitHub Pages with no server. Keep the file small (< ~600 kB).
"""
import json, os, re, sys, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, 'content')
OUT = os.path.join(ROOT, 'assets', 'data', 'ask-index.json')
CACHE = os.path.join(C, 'abstracts.json')
OFFLINE = '--offline' in sys.argv

try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit('pip install beautifulsoup4')

# ------------------------------------------------------------------ helpers
def clean(t):
    t = re.sub(r'\$[^$]{1,40}\$', lambda m: m.group(0).strip('$'), t)   # drop $...$ TeX fences
    t = re.sub(r'\\[a-zA-Z]+', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()

def text_of(node):
    return clean(node.get_text(' ', strip=True))

def split_lang(html_src):
    """Return (english_text, chinese_text) of a bilingual content file."""
    soup = BeautifulSoup(html_src, 'html.parser')
    for s in soup.select('figure, script, style, nav'): s.decompose()
    zh = BeautifulSoup(str(soup), 'html.parser')
    for s in soup.select('.zh'): s.decompose()
    for s in zh.select('.en'): s.decompose()
    return soup, zh

def chunks(soup, min_len=120, max_len=900):
    """Split a page into (heading, text) chunks at h2/h3 boundaries, merging short paragraphs."""
    out, head, buf = [], '', []
    def flush():
        t = clean(' '.join(buf))
        if len(t) >= min_len:
            # split very long sections on sentence boundaries
            while len(t) > max_len:
                cut = t.rfind('. ', 0, max_len)
                cut = cut + 1 if cut > min_len else max_len
                out.append((head, t[:cut].strip())); t = t[cut:].strip()
            out.append((head, t))
        buf.clear()
    for el in soup.find_all(['h2', 'h3', 'p', 'li', 'blockquote']):
        if el.name in ('h2', 'h3'):
            flush(); head = text_of(el)
        else:
            if el.find_parent(['h2', 'h3']): continue
            t = text_of(el)
            if t: buf.append(t)
    flush()
    return out

# ------------------------------------------------------------------ papers
def fetch_abstracts(ids):
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    need = [i for i in ids if str(i) not in cache]
    if need and not OFFLINE:
        for k in range(0, len(need), 40):
            batch = need[k:k + 40]
            q = urllib.parse.urlencode({'q': ' or '.join(f'control_number:{i}' for i in batch), 'size': 50,
                                        'fields': 'control_number,abstracts.value,keywords.value,titles.title'})
            with urllib.request.urlopen(f'https://inspirehep.net/api/literature?{q}', timeout=120) as r:
                for h in json.load(r)['hits']['hits']:
                    m = h['metadata']
                    abs_ = max((a.get('value', '') for a in m.get('abstracts', [])), key=len, default='')
                    cache[str(m['control_number'])] = {'abstract': clean(abs_), 'keywords': [kw['value'] for kw in m.get('keywords', [])][:12]}
            print(f'  fetched abstracts {min(k + 40, len(need))}/{len(need)}')
        json.dump(cache, open(CACHE, 'w'), indent=1, ensure_ascii=False)
    return cache

def papers():
    pubs = json.load(open(os.path.join(C, 'publications.json')))
    extra = json.load(open(os.path.join(C, 'publications-extra.json')))
    cache = fetch_abstracts([p['id'] for p in pubs if isinstance(p['id'], int)])
    docs = []
    for p in pubs + extra:
        a = cache.get(str(p['id']), {})
        url = p.get('url') or (f'https://doi.org/{p["doi"]}' if p.get('doi') else f'https://arxiv.org/abs/{p["arxiv"]}' if p.get('arxiv') else f'https://inspirehep.net/literature/{p["id"]}')
        auth = ', '.join(p['authors'][:3]) + (' et al.' if p.get('author_count', 0) > 3 else '')
        docs.append({
            'id': f'p{p["id"]}', 'type': 'paper', 'title': clean(p['title']),
            'text': a.get('abstract', ''), 'kw': a.get('keywords', []),
            'authors': auth, 'coll': p.get('collaboration', ''), 'year': p['year'],
            'venue': p.get('journal') or (f'arXiv:{p["arxiv"]}' if p.get('arxiv') else p.get('kind', '')),
            'cites': p.get('cites', 0), 'url': url,
        })
    return docs

# ------------------------------------------------------------------ pages & news
PAGES = [  # (content file, public url, title en, title zh)
    ('research.html', 'research.html', 'Research', '研究方向'),
    ('teaching.html', 'teaching.html', 'Teaching', '教学'),
    ('kim.html', 'kim.html', 'Kim Siang Khaw — PI profile', '许金祥 — 课题组长'),
    ('people.html', 'people.html', 'People', '团队成员'),
    ('talks.html', 'talks.html', 'Selected talks', '学术报告'),
    ('muons__index.html', 'muons/index.html', 'About Muons', '缪子科普'),
    ('muons__fundamental-muon-physics.html', 'muons/fundamental-muon-physics.html', 'Fundamental muon physics', '缪子基础物理'),
    ('muons__muon-sources.html', 'muons/muon-sources.html', 'Muon sources', '缪子源'),
    ('muons__muon-detection-techniques.html', 'muons/muon-detection-techniques.html', 'Muon detection techniques', '缪子探测技术'),
    ('muons__applications-of-muons.html', 'muons/applications-of-muons.html', 'Applications of muons', '缪子的应用'),
    ('muons__muography-applications.html', 'muons/muography-applications.html', 'Muography applications', '缪子成像应用'),
    ('muons__muonium.html', 'muons/muonium.html', 'Muonium', '缪子素'),
]

def anchor(head):
    s = re.sub(r'[^a-z0-9]+', '-', head.lower()).strip('-')
    return f'#{s}' if s else ''

def pages():
    docs = []
    for f, url, en, zh in PAGES:
        src = open(os.path.join(C, 'pages', f)).read()
        s_en, s_zh = split_lang(src)
        for i, (head, t) in enumerate(chunks(s_en)):
            docs.append({'id': f'g-{f}-{i}', 'type': 'page', 'title': f'{en}{" › " + head if head else ""}', 'text': t, 'url': url + anchor(head), 'lang': 'en'})
        for i, (head, t) in enumerate(chunks(s_zh, min_len=60, max_len=500)):
            if not re.search(r'[一-鿿]', t): continue   # page has no Chinese version of this chunk
            docs.append({'id': f'gz-{f}-{i}', 'type': 'page', 'title': f'{zh}{" › " + head if head else ""}', 'text': t, 'url': url + anchor(head), 'lang': 'zh'})
    return docs

def news():
    docs = []
    for n in json.load(open(os.path.join(C, 'news.json'))):
        try: src = open(os.path.join(C, 'news', n['slug'] + '.html')).read()
        except FileNotFoundError: continue
        s_en, _ = split_lang(src)
        t = clean(' '.join(text_of(p) for p in s_en.find_all('p')))[:1200]
        if len(t) < 60: continue
        docs.append({'id': f'n-{n["slug"]}', 'type': 'news', 'title': n['title'], 'text': t, 'url': f'news/{n["slug"]}.html', 'date': n['date']})
    return docs

def members():
    docs = []
    for m in json.load(open(os.path.join(C, 'members.json'))):
        def flat(v): return ' '.join(flat(x) for x in v) if isinstance(v, list) else str(v or '')
        bits = [m.get('name', ''), m.get('zh', ''), flat(m.get('role')), 'since ' + str(m.get('since', '')), flat(m.get('topics'))]
        edu = ' '.join(flat(e) for e in m.get('education', []))
        awards = ' '.join(flat(a) for a in m.get('awards', []))
        t = clean(' · '.join(b for b in bits if b) + '. ' + edu + ' ' + awards)[:900]
        if len(t) < 20: continue
        docs.append({'id': f'm-{m["slug"]}', 'type': 'member', 'title': m.get('name', m['slug']), 'text': t, 'url': f'people/{m["slug"]}.html'})
    return docs

if __name__ == '__main__':
    docs = papers() + pages() + news() + members()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({'built': __import__('datetime').date.today().isoformat(), 'docs': docs}, open(OUT, 'w'), ensure_ascii=False, separators=(',', ':'))
    kinds = {}
    for d in docs: kinds[d['type']] = kinds.get(d['type'], 0) + 1
    print('ask-index:', kinds, f'{os.path.getsize(OUT) // 1024} kB')
