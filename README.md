# Fire & Kettle

A live-fire cookbook in two forms, built from one source.

**34 menus · 314 recipes · 433 pages.** Every dish is cooked over charcoal or
wood on no more than two 22-inch Weber kettles, using at most a heat deflector,
a rotisserie and a pizza stone. No oven, no stovetop.

- **`dist/Fire-and-Kettle.pdf`** — the book, 6×9, print and tablet ready
- **`dist/fire-and-kettle-app.html`** — the web app, a single self-contained file

## Quick start

```bash
pip install beautifulsoup4 weasyprint pypdf
npm run build      # web app  -> dist/fire-and-kettle-app.html
npm run build:pdf  # the book -> dist/Fire-and-Kettle.pdf
npm test
npm run dev        # http://localhost:8000
```

Python 3.10+ and Node 18+. Only the PDF build needs WeasyPrint.

## What the app does

- Browse 34 menus or search 314 recipes by ingredient, technique or region
- **17 filters** — season, meat, country, occasion, complexity, total and lead
  time, kettles required, accessory, technique, wood, dietary, cost, spice
  level, cold-weather, special-order ingredients, serving style, showpiece
- **Capacity model** — change the serving count and it tells you what no longer
  fits on two kettles: which Dutch oven size you need, how many spit loads,
  how many rounds, and how much more charcoal
- **Menu builder** — pick a main and it ranks every other recipe against it,
  weighing tradition, season and which piece of equipment each dish is already
  competing for
- **Shopping list** — whole menus or single recipes, merged by ingredient,
  grouped by aisle, converted into things a shop actually sells

## How the build works

`book/*.html` is the source of truth. `data/extract.py` parses it into
`data/data.json`, which both builds consume. The app is developed as three
separate files in `app/` and inlined into one file for publishing.

See `CLAUDE.md` for the data model, conventions and the traps.

## Layout

```
book/     chapter HTML — edit this to change the book
data/     extraction and the hand-written metadata that annotates it
app/      index.html, styles.css, app.js — edit these to change the app
scripts/  build_app.py, build_pdf.py
tests/    smoke.mjs
dist/     build output
```
