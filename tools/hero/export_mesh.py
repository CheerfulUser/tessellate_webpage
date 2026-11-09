"""Copy one asteroid's non-convex mesh out of the asteroid catalogue's shards for the hero render.

Shard layout as the asteroid site's assets/common.js: shard = sum of the key's character codes % 64,
<shard>.json maps key -> [offset, length] of a gzipped JSON record in <shard>.bin.

    python tools/hero/export_mesh.py ~/Documents/work/code/tess/tessellate_asteroid 467_Laura
"""
import gzip
import json
import sys
from pathlib import Path

NSHARD = 64


def main(repo, key):
    shards = Path(repo).expanduser() / 'data' / 'shards'
    k = sum(map(ord, key)) % NSHARD
    off, n = json.loads((shards / f'{k}.json').read_text())[key]
    with open(shards / f'{k}.bin', 'rb') as f:
        f.seek(off)
        rec = json.loads(gzip.decompress(f.read(n)))
    nc = rec['nc']
    out = Path(__file__).resolve().parent / 'mesh.json'
    out.write_text(json.dumps({'key': key, 'name': rec['d'], 's': nc['s'], 'v': nc['v'], 'f': nc['f']}))
    print(f'wrote {out}: {rec["d"]}, {len(nc["v"]) // 3} vertices, {len(nc["f"]) // 3} faces')


if __name__ == '__main__':
    main(*sys.argv[1:])
