#!/bin/zsh
# Render the asteroid hero image (assets/hero_asteroid.png) from tools/hero/mesh.json.
# Needs the site served locally (python -m http.server 8790 from the repo root) and Google Chrome.
# Chosen view: (32) Pomona's non-convex model (export with tools/hero/export_mesh.py <asteroid repo> 32_Pomona),
# an elongated body with a mild concavity; camera az 90 el 20, key light 100 deg to the side and 18 deg up.
set -e
cd "$(dirname "$0")/../.."
VIEW='az=90&el=20&laz=100&lel=18&ri=1.8&ai=0.45'
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --use-angle=swiftshader \
  --enable-unsafe-swiftshader --default-background-color=00000000 --virtual-time-budget=15000 --hide-scrollbars \
  --window-size=1200,920 --screenshot=assets/hero_asteroid.png \
  "http://localhost:8790/tools/hero/render.html?w=1200&h=920&$VIEW" 2>/dev/null
# trim the transparent margin, keeping a small pad
python3 - <<'PY'
from PIL import Image
im = Image.open('assets/hero_asteroid.png').convert('RGBA')
x0, y0, x1, y1 = im.getchannel('A').getbbox()
p = 24
im.crop((max(x0 - p, 0), max(y0 - p, 0), min(x1 + p, im.width), min(y1 + p, im.height))).save('assets/hero_asteroid.png', optimize=True)
PY
echo wrote assets/hero_asteroid.png
