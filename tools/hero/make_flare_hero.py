"""Make the flare card's star image (assets/hero_flare.webp) from an SDO/AIA 304 Angstrom image of the Sun.

Fetches the full-disc image from Helioviewer (public domain; credit "NASA/SDO and the AIA science team", given in the
page footer), crops a square of MARGIN disc radii around the disc, makes the black sky transparent (alpha from
brightness, faded out beyond the limb so the Helioviewer label and stray light go), and deepens the color a little
toward the flare site's red. The flare card (index.html) shows it as its picture, like the asteroid render.

Chosen image: 2024-05-14 16:51 UT, the X8.7 flare on the west limb (right-hand edge, ~0.28 disc radii below center).

Edit the CONFIG block, then:  python tools/hero/make_flare_hero.py  (from anywhere; it writes into this repository)
"""
import io
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image

# ---- CONFIG ----
DATE = '2024-05-14T16:51:00Z'
URL = ('https://api.helioviewer.org/v2/takeScreenshot/?date={date}&imageScale=2.4'
       '&layers=%5BSDO,AIA,304,1,100%5D&x0=0&y0=0&width=1024&height=1024&display=true')
SIZE = 900                  # output square, pixels
MARGIN = 1.12               # crop half-width in disc radii (room for the corona and the limb flare)
FADE = (1.02, 1.11)         # alpha fades from full to zero between these radii
GREEN, BLUE = 0.86, 0.75    # color grade toward red
OUT = Path(__file__).resolve().parent.parent.parent / 'assets' / 'hero_flare.webp'
# ----------------

with urllib.request.urlopen(URL.format(date=DATE), timeout=120) as r:
    im = np.asarray(Image.open(io.BytesIO(r.read())).convert('RGB')).astype(float) / 255
disc = im.max(axis=2) > 0.25
yy, xx = np.nonzero(disc)
cy, cx, rad = yy.mean(), xx.mean(), np.sqrt(disc.sum() / np.pi)
h = MARGIN * rad
box = tuple(int(round(v)) for v in (cx - h, cy - h, cx + h, cy + h))
crop = Image.fromarray((im * 255).astype(np.uint8)).crop(box).resize((SIZE, SIZE), Image.LANCZOS)
a = np.asarray(crop).astype(float) / 255
a[..., 1] *= GREEN
a[..., 2] *= BLUE
n = SIZE / 2
y, x = np.mgrid[0:SIZE, 0:SIZE]
rr = np.hypot(x - n + .5, y - n + .5) / (n / MARGIN)
bright = np.clip(a.max(axis=2) / 0.35, 0, 1) ** 0.8
fade = np.clip((FADE[1] - rr) / (FADE[1] - FADE[0]), 0, 1)
alpha = np.where(rr <= 1, 1, bright * fade)
Image.fromarray((np.dstack([a, alpha]) * 255).astype(np.uint8), 'RGBA').save(OUT, quality=82, method=6)
print(f'disc r = {rad:.0f} px at ({cx:.0f}, {cy:.0f}) -> {OUT} ({OUT.stat().st_size // 1024} KB)')
