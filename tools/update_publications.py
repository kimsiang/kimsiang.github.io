#!/usr/bin/env python3
"""Refresh content/publications.json from INSPIRE-HEP.

    python3 tools/update_publications.py && python3 tools/build.py

Author record: https://inspirehep.net/authors/1114795  (Kim.Siang.Khaw.1)
Items INSPIRE does not know about go in content/publications-extra.json.
"""
import json, os, re, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAI = 'Kim.Siang.Khaw.1'
FIELDS = ('titles,authors.full_name,author_count,collaborations,publication_info,dois,arxiv_eprints,'
          'earliest_date,citation_count,document_type,refereed,control_number,thesis_info')

def fetch():
    out, page = [], 1
    while True:
        q = urllib.parse.urlencode({'q': f'a {BAI}', 'size': 250, 'page': page, 'sort': 'mostrecent', 'fields': FIELDS})
        with urllib.request.urlopen(f'https://inspirehep.net/api/literature?{q}', timeout=120) as r:
            d = json.load(r)
        hits = d['hits']['hits']
        out += [h['metadata'] for h in hits]
        if len(out) >= d['hits']['total'] or not hits: return out
        page += 1

def name(full):
    # "Khaw, Kim Siang" -> "K.S. Khaw"
    if ',' not in full: return full
    last, first = [x.strip() for x in full.split(',', 1)]
    ini = '.'.join(p[0] for p in re.split(r'[\s-]+', first) if p) + '.'
    return f'{ini} {last}'

def journal(m):
    for p in m.get('publication_info', []):
        if p.get('journal_title'):
            s = p['journal_title']
            if p.get('journal_volume'): s += f" {p['journal_volume']}"
            if p.get('year'): s += f" ({p['year']})"
            if p.get('journal_issue'): s += f" {p['journal_issue']}"
            if p.get('artid'): s += f", {p['artid']}"
            elif p.get('page_start'): s += f", {p['page_start']}" + (f"–{p['page_end']}" if p.get('page_end') else '')
            return s
    return ''

def kind(m):
    t = m.get('document_type', [])
    if 'thesis' in t: return 'thesis'
    if 'conference paper' in t and not journal(m): return 'proceedings'
    if 'conference paper' in t: return 'proceedings'
    if 'report' in t: return 'report'
    return 'journal' if journal(m) or m.get('refereed') else 'preprint'

def convert(m):
    authors = [name(a['full_name']) for a in m.get('authors', [])]
    n = m.get('author_count', len(authors))
    colls = [c['value'] for c in m.get('collaborations', [])]
    year = (m.get('earliest_date') or '0000')[:4]
    for p in m.get('publication_info', []):
        if p.get('year'): year = str(p['year']); break
    return {
        'id': m['control_number'],
        'title': re.sub(r'\s+', ' ', m['titles'][0]['title']).strip(),
        'authors': authors[:3], 'author_count': n,
        'collaboration': colls[0] if colls else '',
        'year': year, 'date': m.get('earliest_date', ''),
        'journal': journal(m),
        'doi': (m.get('dois') or [{}])[0].get('value', ''),
        'arxiv': (m.get('arxiv_eprints') or [{}])[0].get('value', ''),
        'cites': m.get('citation_count', 0),
        'kind': kind(m), 'refereed': bool(m.get('refereed')),
    }

if __name__ == '__main__':
    items = [convert(m) for m in fetch()]
    extra_path = os.path.join(ROOT, 'content', 'publications-extra.json')
    if os.path.exists(extra_path):
        items += json.load(open(extra_path))
    items.sort(key=lambda x: (x['year'], x['date']), reverse=True)
    json.dump(items, open(os.path.join(ROOT, 'content', 'publications.json'), 'w'), ensure_ascii=False, indent=1)
    print(len(items), 'publications,', sum(i['cites'] for i in items), 'citations')
