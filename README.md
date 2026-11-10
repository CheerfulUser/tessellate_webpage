# TESSELLATE Sky Survey (TSS)

Landing page for the TESSELLATE Sky Survey (TSS): source catalogs from an untargeted search of every TESS
full-frame image with the TESSELLATE pipeline.
Links the live catalog sites and holds placeholders for those in preparation.

| catalog | site |
|---|---|
| Asteroid rotation & shape | <https://cheerfuluser.github.io/tessellate_asteroid/> |
| Stellar flares | <https://hughroxburgh.github.io/tessellate_flares/> |
| Variable stars, transients, exoplanets | in preparation |

The site is static and served by GitHub Pages from the repository root; there is no build step on GitHub.

## Layout

| path | contents |
|---|---|
| `index.html` | the whole site: catalogs, results, pipeline, team, citation |
| `assets/site.css` | styles; same tokens as the catalog sites, one accent per catalog |
| `assets/logo.svg`, `assets/favicon.svg` | logo and favicon (generated) |
| `data/catalogs.json` | headline numbers shown on the catalog cards (generated) |
| `tools/make_logo.py` | draws the logo from the nominal TESS camera geometry |
| `tools/update_stats.py` | refreshes `data/catalogs.json` from the catalog sites |

The results figures are loaded directly from each catalog's site, so they follow that catalog's rebuilds.
The card numbers do not: rerun `python tools/update_stats.py` after a catalog is rebuilt.

## The logo

The mark is the TESS camera footprints of one hemisphere seen from the ecliptic pole: four 24 deg cameras per
sector at ecliptic latitudes 18, 42, 66 and 90 deg, and 13 sectors around the pole, in an equal-area polar
projection, leaving out the pole camera so the center is open. The adopted coloring (`dusk_white_edge_center_tight_white`)
is one smooth translucent gradient from white across the outer ring through blue to violet at the center, with a
light violet highlight around the open center. `python tools/make_logo.py <variant>` writes another variant to the site;
`python tools/make_logo.py --preview` writes every variant to `tools/logo_variants/` for comparison.

## Adding a catalog

Turn its placeholder card in `index.html` into a link card like the asteroid and flare ones, add its counts
to `tools/update_stats.py`, and add a figure or two to the results section.

## Preview locally

    python -m http.server 8790

then visit <http://localhost:8790/>.
