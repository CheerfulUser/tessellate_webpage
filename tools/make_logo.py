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
assets/favicon.svg. With --preview it writes each variant to tools/logo_variants/ with a
preview page instead, and leaves the site's logo alone. A variant already written there is kept
as it is: to try changes, add a new variant rather than editing an old one.
Usage: python tools/make_logo.py [variant]   variant: a key of VARIANTS (default: the adopted
       dusk_white_edge_center_tight)
       python tools/make_logo.py --preview
"""
import sys
from pathlib import Path

import numpy as np
from shapely.geometry import Polygon

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

# Color schemes. 'colors' gives one fill per drawn camera (outermost first); 'radial' instead
# gives (offset, color) stops of one gradient across the whole mark, from the pole (0) to the
# mark's edge (1), so color follows distance from the pole rather than camera; a stop may add a
# third value, its opacity. 'drawn' gives
# gradient stops from which each tile draws one solid color at random: from the stretch of the
# gradient its camera spans (pick 'span') or from all of it (pick 'any'). Drawn tiles are opaque
# and multiplied together, so overlaps come out darker. 'blend': 'multiply' does the same for
# fixed colors, 'cameras' overrides which cameras are drawn, and 'camera_colors' gives single
# cameras a flat color in place of the palette's. No yellow.
VARIANTS = {
    # catalog accents: transients orange, flares red, asteroids purple
    'catalog': {'colors': ['#e09a5a', '#ff7b7b', '#a78bfa'], 'opacity': [0.36, 0.36, 0.34]},
    'mono': {'colors': ['#8fb4e6'] * 3, 'opacity': [0.36, 0.36, 0.34]},
    # white at the edge to blue in the middle, one step per camera
    'ice': {'colors': ['#ffffff', '#a9c8f2', '#4a86e8'], 'opacity': [0.40, 0.44, 0.50]},
    # the same, as a smooth gradient
    'ice_radial': {'radial': [(0.15, '#2f6fe0'), (0.45, '#6fa0ec'), (0.75, '#c9dcf7'), (1.0, '#ffffff')],
                   'opacity': [0.42, 0.46, 0.52]},
    # brighter and more saturated, deep blue core
    'ice_bold': {'radial': [(0.15, '#1f5bff'), (0.5, '#5c9bff'), (0.8, '#d6e6ff'), (1.0, '#ffffff')],
                 'opacity': [0.55, 0.6, 0.68]},
    # near-opaque, so the edge reads white rather than grey; overlaps barely brighten
    'ice_bright': {'radial': [(0.15, '#1f5bff'), (0.5, '#5c9bff'), (0.8, '#d6e6ff'), (1.0, '#ffffff')],
                   'opacity': [0.85, 0.82, 0.8]},
    # white edge through blue to violet at the pole
    'dusk': {'radial': [(0.15, '#8a63f0'), (0.45, '#4a86e8'), (0.78, '#b9d3f5'), (1.0, '#ffffff')],
             'opacity': [0.42, 0.46, 0.52]},
    # dusk with a whiter outside: dusk's colors, with opacity carried by the gradient too, rising
    # smoothly from the pole to the edge so the outer ring reads white rather than grey
    'dusk_white_edge': {'radial': [(0.15, '#8a63f0', 0.45), (0.45, '#4a86e8', 0.5), (0.78, '#b9d3f5', 0.68),
                                   (1.0, '#ffffff', 0.92)],
                        'opacity': [1.0, 1.0, 1.0]},
    # dusk_white_edge with a highlight at the very center (camera 3's inner edge, ~0.17): lighter,
    # more opaque violet there, back on dusk_white_edge's own gradient by 0.26
    'dusk_white_edge_center': {'radial': [(0.15, '#c4b0ff', 0.82), (0.19, '#a98cf8', 0.65), (0.26, '#7270ed', 0.47),
                                          (0.45, '#4a86e8', 0.5), (0.78, '#b9d3f5', 0.68), (1.0, '#ffffff', 0.92)],
                               'opacity': [1.0, 1.0, 1.0]},
    # dusk_white_edge_center with the highlight pulled in to the center: it peaks at camera 3's inner
    # edge (~0.17) and is back on dusk_white_edge's gradient by 0.21 instead of 0.26
    'dusk_white_edge_center_tight': {'radial': [(0.17, '#c4b0ff', 0.82), (0.185, '#a98cf8', 0.63), (0.21, '#7d6aee', 0.46),
                                                (0.45, '#4a86e8', 0.5), (0.78, '#b9d3f5', 0.68), (1.0, '#ffffff', 0.92)],
                                     'opacity': [1.0, 1.0, 1.0]},
    # dusk_white_edge_center_tight with more white in the outer gradient: light blue by 0.64 (was
    # 0.78) and white by 0.86 (was 1.0), opacity still rising to the edge
    'dusk_white_edge_center_tight_white': {'radial': [(0.17, '#c4b0ff', 0.82), (0.185, '#a98cf8', 0.63), (0.21, '#7d6aee', 0.46),
                                                      (0.45, '#4a86e8', 0.5), (0.64, '#b9d3f5', 0.68), (0.86, '#ffffff', 0.88),
                                                      (1.0, '#ffffff', 0.95)],
                                           'opacity': [1.0, 1.0, 1.0]},
    # dusk_white_edge_center with camera 4 drawn at the pole in dusk's violet; its 13 overlapping
    # pointings build up to near-solid violet there
    'dusk_white_edge_center_cam4': {'radial': [(0.15, '#c4b0ff', 0.82), (0.19, '#a98cf8', 0.65), (0.26, '#7270ed', 0.47),
                                               (0.45, '#4a86e8', 0.5), (0.78, '#b9d3f5', 0.68), (1.0, '#ffffff', 0.92)],
                                    'cameras': range(4), 'camera_colors': {3: '#8a63f0'},
                                    'opacity': [1.0, 1.0, 1.0, 0.35]},
    # its overlaps only (see overlap_only)
    'dusk_white_edge_center_cam4_overlap': {'radial': [(0.15, '#c4b0ff', 0.82), (0.19, '#a98cf8', 0.65), (0.26, '#7270ed', 0.47),
                                                       (0.45, '#4a86e8', 0.5), (0.78, '#b9d3f5', 0.68), (1.0, '#ffffff', 0.92)],
                                            'cameras': range(4), 'camera_colors': {3: '#8a63f0'},
                                            'opacity': [1.0, 1.0, 1.0, 0.35], 'overlap_only': True},
    # white edge through teal to blue at the pole
    'lagoon': {'radial': [(0.15, '#3b6fe0'), (0.45, '#45b8c8'), (0.78, '#c4ece9'), (1.0, '#ffffff')],
               'opacity': [0.42, 0.46, 0.52]},
    # reversed: blue at the edge to white at the pole
    'ice_inverse': {'radial': [(0.15, '#ffffff'), (0.5, '#a9c8f2'), (1.0, '#3b78e0')],
                    'opacity': [0.50, 0.46, 0.46]},
    # white at the edge to blue in the middle, one drawn color per tile, darker where tiles overlap
    'ice_drawn': {'drawn': [(0.0, '#1f5bff'), (0.35, '#5c9bff'), (0.7, '#d6e6ff'), (1.0, '#ffffff')],
                  'pick': 'span', 'seed': 3, 'opacity': [1.0, 1.0, 1.0]},
    'ice_scatter': {'drawn': [(0.0, '#1f5bff'), (0.35, '#5c9bff'), (0.7, '#d6e6ff'), (1.0, '#ffffff')],
                    'pick': 'any', 'seed': 3, 'opacity': [1.0, 1.0, 1.0]},
    # all four cameras, one color each from white (camera 1, outside) to blue (camera 4, pole);
    # opaque and multiplied, so overlapping pointings deepen the color. Blue stays near full in
    # every color, so stacked overlaps deepen toward blue rather than black.
    'camera_depth': {'cameras': range(4), 'colors': ['#eef4ff', '#c6dbff', '#98bcfc', '#6f9ffa'],
                     'blend': 'multiply', 'opacity': [1.0] * 4},
}


def sample(stops, t):
    """Color at position t (0-1) along a gradient of (offset, '#rrggbb') stops, linear in RGB."""
    offs = [o for o, _ in stops]
    rgb = np.array([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for _, c in stops], float)
    return '#' + ''.join(f'{round(np.interp(t, offs, rgb[:, i])):02x}' for i in range(3))


def full(color):
    """Scale a color up until its strongest channel is full, so that multiplying it many times over
    deepens toward its own hue instead of toward black."""
    rgb = np.array([int(color[i:i + 2], 16) for i in (1, 3, 5)], float)
    return '#' + ''.join(f'{round(v):02x}' for v in rgb * 255 / rgb.max())


def camera_depth(scheme):
    """camera_depth treatment of another palette: four camera colors spaced evenly from the
    palette's edge color (camera 1) to its center color (camera 4)."""
    if 'colors' in scheme:
        cols = scheme['colors'][::-1]
        stops = list(zip(np.linspace(0, 1, len(cols)), cols))
    else:
        stops = [st[:2] for st in scheme.get('radial') or scheme['drawn']]
    colors = [full(sample(stops, t)) for t in np.linspace(1, stops[0][0], 4)]
    return {'cameras': range(4), 'colors': colors, 'blend': 'multiply', 'opacity': [1.0] * 4}


# camera_depth versions of the other palettes. ice_bright, ice_drawn and ice_scatter share
# ice_bold's colors, so their versions would match ice_bold_depth and are left out. The catalog
# palette has no camera-4 color, so camera 4 takes the variable-star teal.
for _v in ['catalog', 'mono', 'ice', 'ice_radial', 'ice_bold', 'dusk', 'lagoon', 'ice_inverse']:
    VARIANTS[f'{_v}_depth'] = camera_depth(VARIANTS[_v])
VARIANTS['catalog_depth']['colors'] = [full(c) for c in VARIANTS['catalog']['colors'] + ['#5ec8b4']]
# dusk_depth with a lavender camera 4: red and blue both full, so the 13 overlapping pointings at
# the pole deepen to purple; dusk_depth's violet loses its red there and comes out blue
VARIANTS['dusk_depth_purple'] = dict(VARIANTS['dusk_depth'], colors=VARIANTS['dusk_depth']['colors'][:3] + ['#ffccff'])
# darker purple at the pole: red and blue just below full (red a little lower), so 13 overlaps
# come out about #620098 instead of saturating to magenta
VARIANTS['dusk_depth_purple_dark'] = dict(VARIANTS['dusk_depth'], colors=VARIANTS['dusk_depth']['colors'][:3] + ['#eda8f5'])
# only where two or more pointings overlap: dusk_depth_purple_dark clipped to the overlaps, and
# the mark cropped to them (camera 1 never overlaps, so the outer ring drops out)
VARIANTS['overlap_only'] = dict(VARIANTS['dusk_depth_purple_dark'], overlap_only=True)
# the same for every other camera-depth palette
for _v in ['camera_depth', 'catalog_depth', 'mono_depth', 'ice_depth', 'ice_radial_depth', 'ice_bold_depth',
           'dusk_depth', 'dusk_depth_purple', 'lagoon_depth', 'ice_inverse_depth']:
    VARIANTS[f'{_v}_overlap'] = dict(VARIANTS[_v], overlap_only=True)


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


def pointings(scheme):
    """Projected outline (x, y) of every drawn camera pointing, with its camera index."""
    for k in range(NSECT):
        # one sector points straight up
        lon = 90.0 + k * 360.0 / NSECT
        for c in scheme.get('cameras', CAMERAS):
            yield c, footprint(lon, LATS[c], INSET)


def overlaps(scheme):
    """Regions covered by two or more pointings, as one polygon per overlapping pair."""
    polys = [Polygon(np.column_stack(xy)) for _, xy in pointings(scheme)]
    pairs = (a.intersection(b) for i, a in enumerate(polys) for b in polys[i + 1:])
    return [g for g in pairs if g.geom_type == 'Polygon' and g.area > 0]


def tiles(scheme, half):
    out = []
    if 'radial' in scheme:
        stops = ''.join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a[0]}"' if a else '') + '/>'
                        for o, c, *a in scheme['radial'])
        out.append(f'<defs><radialGradient id="tint" gradientUnits="userSpaceOnUse" cx="0" cy="0" '
                   f'r="{half}">{stops}</radialGradient></defs>')
    rng = np.random.default_rng(scheme.get('seed'))
    paths = []
    for c, (x, y) in pointings(scheme):
        if 'drawn' in scheme:
            r = SCALE * np.hypot(x, y) / half
            t = rng.uniform(r.min(), r.max()) if scheme['pick'] == 'span' else rng.uniform()
            fill = sample(scheme['drawn'], t)
        else:
            fill = 'url(#tint)' if 'radial' in scheme else scheme['colors'][c]
            fill = scheme.get('camera_colors', {}).get(c, fill)
        paths.append(f'<path d="{path(x, y)}" fill="{fill}" fill-opacity="{scheme["opacity"][c]}"/>')
    if scheme.get('overlap_only'):
        # pairwise overlaps as one clip; the clip is their union
        clip = ''.join(f'<path d="{path(*g.exterior.xy)}"/>' for g in overlaps(scheme))
        out.append(f'<defs><clipPath id="overlap">{clip}</clipPath></defs>')
    if 'drawn' in scheme or scheme.get('blend') == 'multiply':
        # multiply inside an isolated group: tiles darken each other, not the page behind
        clip = ' clip-path="url(#overlap)"' if scheme.get('overlap_only') else ''
        return out + [f'<g style="isolation:isolate"{clip}>'] + [
            p.replace('<path ', '<path style="mix-blend-mode:multiply" ') for p in paths] + ['</g>']
    if scheme.get('overlap_only'):
        return out + ['<g clip-path="url(#overlap)">'] + paths + ['</g>']
    return out + paths


def svg(body, hw, hh):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-hw} {-hh} {2 * hw} {2 * hh}" '
            f'role="img" aria-label="TESSELLATE Sky Survey">\n' + '\n'.join(body) + '\n</svg>\n')


def mark(variant):
    # mark radius: the projected camera-1 corners, or the outermost overlap
    half = round(SCALE * np.hypot(*footprint(90.0, LATS[0], INSET)).max() * 1.03, 1)
    body = tiles(VARIANTS[variant], half)
    if VARIANTS[variant].get('overlap_only'):
        half = round(SCALE * max(np.hypot(*g.exterior.xy).max() for g in overlaps(VARIANTS[variant])) * 1.03, 1)
    return svg(body, half, half)


PREVIEW_ROW = """<div class="row"><p>{v}</p>
  <div class="lockup"><img class="big" src="{v}.svg"><h1>TESSELLATE <span>Sky Survey</span></h1></div>
  <div class="small"><span class="brand"><img src="{v}.svg">TSS</span><img class="fav" src="{v}.svg"></div></div>"""
PREVIEW = """<!doctype html><meta charset="utf-8"><title>TSS logo variants</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;600;700&family=Azeret+Mono&display=swap">
<style>body{{margin:0;padding:28px;background:#000;color:#e8ecf3;font-family:"Instrument Sans",sans-serif}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
.row{{border:1px solid #232936;border-radius:10px;padding:14px 20px 18px}}
.row p{{font-family:"Azeret Mono",monospace;font-size:12px;color:#8f99ab;margin:0 0 8px}}
.lockup{{display:flex;align-items:center;gap:20px}} .big{{height:96px}}
h1{{font-size:34px;margin:0;letter-spacing:-0.02em}}
.small{{display:flex;align-items:center;gap:22px;margin-top:14px;padding-top:12px;border-top:1px solid #1c212c}}
.brand{{display:flex;align-items:center;gap:9px;font-weight:600;letter-spacing:.14em;font-size:13px}}
.brand img{{height:22px}} .fav{{height:16px}}</style>
<div class="grid">
{rows}
</div>
"""


def main(variant='dusk_white_edge_center_tight'):
    root = Path(__file__).resolve().parent.parent
    if variant == '--preview':
        out = root / 'tools' / 'logo_variants'
        out.mkdir(exist_ok=True)
        for v in VARIANTS:
            f = out / f'{v}.svg'
            if f.exists():
                if f.read_text() != mark(v):
                    print(f'kept the existing {f.name}; its definition has changed, so add it as a new variant')
                continue
            f.write_text(mark(v))
        (out / 'preview.html').write_text(PREVIEW.format(rows='\n'.join(PREVIEW_ROW.format(v=v) for v in VARIANTS)))
        print(f'wrote {len(VARIANTS)} variants and preview.html to {out}')
        return
    m = mark(variant)
    (root / 'assets' / 'logo.svg').write_text(m)
    (root / 'assets' / 'favicon.svg').write_text(m)
    print(f'wrote {root / "assets/logo.svg"} and {root / "assets/favicon.svg"} ({variant})')


if __name__ == '__main__':
    main(*sys.argv[1:])
