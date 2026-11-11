#!/bin/zsh
# Render an asteroid hero image from an exported mesh (tools/hero/export_mesh.py <asteroid repo> <key> writes
# tools/hero/mesh_<key>.json). Needs the site served locally (python -m http.server 8790 from the repo root) and
# Google Chrome.
#   tools/hero/render_hero.sh [mesh file] [output png] [view]
# Renders so far, each with its view:
#   (292) Ludovica, the asteroid card's picture since 2026-11-11 (non-convex model; az 315, el 20, chosen by Ryan
#     from eight azimuths at el 20, silhouette aspect 1.88):
#     tools/hero/render_hero.sh mesh_292_Ludovica.json assets/hero_asteroid_ludovica_az315.png 'az=315&el=20&laz=100&lel=18&ri=1.8&ai=0.45'
#   (32) Pomona, the earlier picture (the defaults; exported before per-object mesh files, as mesh.json):
#     tools/hero/render_hero.sh mesh.json assets/hero_asteroid.png 'az=90&el=20&laz=100&lel=18&ri=1.8&ai=0.45'
# az, el: camera direction; laz, lel: key light relative to the camera; ri, ai: rim and ambient light strength.
set -e
cd "$(dirname "$0")/../.."
MESH=${1:-mesh.json}
OUT=${2:-assets/hero_asteroid.png}
VIEW=${3:-'az=90&el=20&laz=100&lel=18&ri=1.8&ai=0.45'}
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --use-angle=swiftshader \
  --enable-unsafe-swiftshader --default-background-color=00000000 --virtual-time-budget=15000 --hide-scrollbars \
  --window-size=1200,920 --screenshot="$OUT" \
  "http://localhost:8790/tools/hero/render.html?w=1200&h=920&mesh=$MESH&$VIEW" 2>/dev/null
# trim the transparent margin, keeping a small pad
python3 - "$OUT" <<'PY'
import sys
from PIL import Image
out = sys.argv[1]
im = Image.open(out).convert('RGBA')
x0, y0, x1, y1 = im.getchannel('A').getbbox()
p = 24
im.crop((max(x0 - p, 0), max(y0 - p, 0), min(x1 + p, im.width), min(y1 + p, im.height))).save(out, optimize=True)
PY
echo wrote $OUT
