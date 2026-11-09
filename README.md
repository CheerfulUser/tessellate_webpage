# TESSELLATE

Landing page for the TESSELLATE source catalogues: an untargeted search of every TESS full-frame image.
Links the live catalogue sites and holds placeholders for those in preparation.

| catalogue | site |
|---|---|
| Asteroid rotation & shape | <https://cheerfuluser.github.io/tessellate_asteroid/> |
| Stellar flares | <https://hughroxburgh.github.io/tessellate_flares/> |
| Variable stars, transients, exoplanets | in preparation |

The site is static and served by GitHub Pages from the repository root; there is no build step on GitHub.

## Layout

| path | contents |
|---|---|
| `index.html` | the whole site: catalogues, results, pipeline, team, citation |
| `assets/site.css` | styles; same tokens as the catalogue sites, one accent per catalogue |
| `assets/logo.svg`, `assets/favicon.svg` | logo and favicon (generated) |
| `data/catalogs.json` | headline numbers shown on the catalogue cards (generated) |
| `tools/make_logo.py` | draws the logo from the nominal TESS camera geometry |
| `tools/update_stats.py` | refreshes `data/catalogs.json` from the catalogue sites |

The results figures are loaded directly from each catalogue's site, so they follow that catalogue's rebuilds.
The card numbers do not: rerun `python tools/update_stats.py` after a catalogue is rebuilt.

## The logo

The mark is the TESS camera footprints of one hemisphere seen from the ecliptic pole: four 24 deg cameras per
sector at ecliptic latitudes 18, 42, 66 and 90 deg, and 13 sectors around the pole, in an equal-area polar
projection, leaving out the pole camera so the centre is open. The camera rings take the catalogue colours. `python tools/make_logo.py mono` draws a
single-colour version.

## Adding a catalogue

Turn its placeholder card in `index.html` into a link card like the asteroid and flare ones, add its counts
to `tools/update_stats.py`, and add a figure or two to the results section.

## Preview locally

    python -m http.server 8790

then visit <http://localhost:8790/>.
