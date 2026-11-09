"""Headline numbers for the landing page, read from each catalog's published site.

The catalog sites are the source of truth; this copies their counts into data/catalogs.json so
the landing page loads one small file instead of each catalog's full index (the asteroid index
is several MB). Counts use the same definitions as each catalog's own home page. Rerun after
either catalog is rebuilt:

    python tools/update_stats.py
"""
import json
from datetime import date
from pathlib import Path
from urllib.request import urlopen

ASTEROID = 'https://cheerfuluser.github.io/tessellate_asteroid/'
FLARES = 'https://hughroxburgh.github.io/tessellate_flares/'


def fetch(url):
    with urlopen(url, timeout=60) as r:
        return json.load(r)


def asteroid():
    j = fetch(ASTEROID + 'data/index.json')
    if isinstance(j, dict):
        # packed index (cols / rows, 2026-11-09 onwards)
        rows = [dict(zip(j['cols'], r)) for r in j['rows']]
        shape = [bool(o['shape_model']) for o in rows]
        nonconvex = sum(bool(o['has_nonconvex']) for o in rows)
        lcdb = [o['lcdb_period_hr'] for o in rows]
        period = [o['period_hr'] for o in rows]
    else:
        # earlier list of short-keyed objects: every object had a shape model (g), none non-convex
        shape = [bool(o.get('g')) for o in j]
        nonconvex = None
        lcdb = [o.get('l') for o in j]
        period = [o.get('p') for o in j]
    return {
        'periods': len(period),
        'shape_models': sum(shape),
        'nonconvex': nonconvex,
        'no_prior_period': sum(v is None for v in lcdb),
        'longer_than_day': sum(p is not None and p > 24 for p in period),
        # stated on the asteroid site's home page; the index does not carry sectors
        'sectors': [27, 55],
    }


def flares():
    j = fetch(FLARES + 'data/summary.json')
    k = j['kpi']
    return {
        'stars': k['stars'],
        'flares': k['flares'],
        'gold': k['gold'],
        'silver_sources': k['silver_sources'],
        'sectors': [min(j['sectors']), max(j['sectors'])],
        'build': j['build'],
    }


def main():
    out = Path(__file__).resolve().parent.parent / 'data' / 'catalogs.json'
    out.parent.mkdir(exist_ok=True)
    stats = {'updated': date.today().isoformat(), 'asteroid': asteroid(), 'flares': flares()}
    out.write_text(json.dumps(stats, indent=1) + '\n')
    print(json.dumps(stats, indent=1))


if __name__ == '__main__':
    main()
