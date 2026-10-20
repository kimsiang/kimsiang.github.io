#!/usr/bin/env python3
"""Refresh content/member-publications.json from INSPIRE-HEP.

    python3 tools/update_members.py && python3 tools/build.py

For every member in content/members.json a paper is listed when either
  * it is claimed on the member's own INSPIRE author record ("inspire"), or
  * it is one of the PI's papers and an author name matches one of "names"
    exactly (INSPIRE sometimes links group members to the wrong record).
Add a control number to "exclude" in members.json to drop a misattributed paper.
"""
import json, os, urllib.parse, urllib.request
from update_publications import FIELDS, convert, fetch as fetch_pi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, 'content')

def by_record(recid):
    q = urllib.parse.urlencode({'q': f'authors.recid:{recid}', 'size': 250, 'sort': 'mostrecent', 'fields': FIELDS})
    with urllib.request.urlopen(f'https://inspirehep.net/api/literature?{q}', timeout=120) as r:
        return [h['metadata'] for h in json.load(r)['hits']['hits']]

if __name__ == '__main__':
    members = json.load(open(os.path.join(C, 'members.json')))
    pi = fetch_pi()
    out = {}
    for m in members:
        papers = {p['control_number']: p for p in (by_record(m['inspire']) if m.get('inspire') else [])}
        names = {n.lower() for n in m.get('names', [])}
        for p in pi:
            if any(a['full_name'].lower() in names for a in p.get('authors', [])):
                papers.setdefault(p['control_number'], p)
        for x in m.get('exclude', []): papers.pop(x, None)
        items = sorted((convert(p) for p in papers.values()), key=lambda x: (x['year'], x['date']), reverse=True)
        out[m['slug']] = items
        print(f"{m['slug']:16} {len(items):3} papers")
    json.dump(out, open(os.path.join(C, 'member-publications.json'), 'w'), ensure_ascii=False, indent=1)
