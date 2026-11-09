"""TESSELLATE Sky Survey (TSS) logo: the TESS camera footprints of one hemisphere, seen from the ecliptic pole.

Nominal TESS observing geometry (Ricker et al. 2015): each sector points a strip of four
24 x 24 deg cameras along one ecliptic meridian, with boresights at ecliptic latitudes 18, 42, 66
and 90 deg, and 13 sectors step around the pole in ecliptic longitude. Each footprint is a square
in its camera's tangent (gnomonic) plane, drawn here in a Lambert azimuthal equal-area projection
centered on the pole, so the outer cameras leave the real gaps near the ecliptic.

Tiles are inset slightly so each camera reads as its own tile, and drawn as translucent fills so
overlapping sectors build up brightness the way TESS coverage depth does. Camera 4, which sits on
the pole, is left out so the center stays open.

Writes assets/logo.svg (mark only; the wordmark is set in HTML) and the same mark as
assets/favicon.svg.
Usage: python tools/make_logo.py [variant]   variant in {catalog, mono}
"""
import sys
from pathlib import Path

import numpy as np

# camera half-width in the tangent plane
HALF = np.tan(np.radians(12.0))
# camera 1-4 boresight ecliptic latitudes
LATS = [18.0, 42.0, 66.0, 90.0]
NSECT = 13
# points per tile edge; edges curve after projection
EDGE_SAMPLES = 16
INSET = 0.88
SCALE = 100.0

# cameras drawn, outermost first; camera 4 (on the pole) is left out
CAMERAS = range(3)
# one color per drawn camera. Catalog accents: transients orange, flares red, asteroids purple;
# no yellow
CATALOG = ['#e09a5a', '#ff7b7b', '#a78bfa']
MONO = ['#8fb4e6'] * 3
FILL_OPACITY = [0.36, 0.36, 0.34]


def footprint(lon, lat, inset=1.0):
    """Projected outline of one camera footprint centered at (lon, lat), in degrees; inset < 1
    shrinks it about its boresight so neighboring tiles separate."""
    lo, la = np.radians(lon), np.radians(lat)
    b = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    e = np.array([-np.sin(lo), np.cos(lo), 0.0])
    n = np.array([-np.sin(la) * np.cos(lo), -np.sin(la) * np.sin(lo), np.cos(la)])
    h = HALF * inset
    t = np.linspace(-h, h, EDGE_SAMPLES, endpoint=False)
    xs = np.concatenate([t, np.full_like(t, h), -t, np.full_like(t, -h)])
    ys = np.concatenate([np.full_like(t, -h), t, np.full_like(t, h), -t])
    v = b[None] + xs[:, None] * e[None] + ys[:, None] * n[None]
    v /= np.linalg.norm(v, axis=1)[:, None]
    colat = np.arccos(np.clip(v[:, 2], -1, 1))
    r = 2 * np.sin(colat / 2)
    az = np.arctan2(v[:, 1], v[:, 0])
    return r * np.cos(az), -r * np.sin(az)


def path(x, y):
    pts = ' '.join(f'{SCALE * a:.1f},{SCALE * c:.1f}' for a, c in zip(x, y))
    return f'M{pts}Z'


def tiles(colors):
    out = []
    for k in range(NSECT):
        # one sector points straight up
        lon = 90.0 + k * 360.0 / NSECT
        for c in CAMERAS:
            x, y = footprint(lon, LATS[c], INSET)
            out.append(f'<path d="{path(x, y)}" fill="{colors[c]}" fill-opacity="{FILL_OPACITY[c]}"/>')
    return out


def svg(body, hw, hh):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-hw} {-hh} {2 * hw} {2 * hh}" '
            f'role="img" aria-label="TESSELLATE Sky Survey">\n' + '\n'.join(body) + '\n</svg>\n')


def main(variant='catalog'):
    out = Path(__file__).resolve().parent.parent / 'assets'
    colors = CATALOG if variant == 'catalog' else MONO
    # mark radius: the projected camera-1 corners
    half = round(SCALE * np.hypot(*footprint(90.0, LATS[0], INSET)).max() * 1.03, 1)
    mark = svg(tiles(colors), half, half)
    (out / 'logo.svg').write_text(mark)
    (out / 'favicon.svg').write_text(mark)
    print(f'wrote {out / "logo.svg"} and {out / "favicon.svg"} ({variant})')


if __name__ == '__main__':
    main(*sys.argv[1:])
