# Fire & Kettle

A live-fire cookbook in two forms, built from one source.

**34 menus · 314 recipes · 424 pages.** Every dish is cooked over charcoal or
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

npm run validate   # check content/*.json without writing anything
npm run vocab      # print the current facet vocabulary
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

## Adding a menu, a recipe or a library item

There are two ways in. Writing chapter HTML by hand is still the way to author
for print, and it is described in `CLAUDE.md`. The quicker way, and the one that
needs no edits to any Python table, is to drop a JSON file into `content/`.

```bash
# 1. Open a Claude conversation and paste in two files:
#      content/PROMPT.md                  the authoring brief
#      data/schema/content.schema.json    the payload contract
#    Then describe the menu or recipe you want.
#
# 2. Save the JSON it returns as content/<something>.json
#
# 3. Build it
npm run validate       # fast, writes nothing — iterate here until clean
npm run build          # app/data.js + dist/
npm test
npm run dev            # look at it: http://localhost:8000
```

Four kinds of payload, set by the `kind` field:

| `kind` | What it adds |
|---|---|
| `menu` | A whole new chapter: facets, grill plan, timeline, shopping list, recipes |
| `recipe` | One dish into a menu chapter that already exists |
| `library` | A shared sauce, dough, rub or marinade other menus can reference |
| `patch` | Facet changes to an existing menu — the way to re-categorise without touching recipe text |

There is a complete worked example of each in `content/examples/`. Those live
outside the build glob, so they are reference material and are never published.

### Why there is no upload endpoint

The build is the database. `extract.py` reads source files and produces
`data/data.json`; adding content means adding a source file and rebuilding. A
checked-in `content/` folder gives you what an API would — structured input,
validation, authoring in a chat window — plus version control, review before
publish, and nothing to run or secure. If you ever need to publish from a device
with no checkout, the cheap version is a GitHub Action on push that builds and
syncs to S3, still with no server.

### What validation catches

`npm run validate` fails the build rather than letting a payload through, on:

- a recipe with no plating note, or a menu with no shopping block
- a value outside a closed vocabulary — `complexity`, `cost`, `kettles` and
  `heat` have filter lists hardcoded in the app, so a new value there would
  render on the page but be unfilterable
- a facet value that is new to the book and not declared in `newFacetValues`,
  and any value differing from an existing one only in case or punctuation
  (`Cast Iron` next to `Cast iron` would quietly split one filter into two)
- a capacity entry whose `match` hits no recipe, or two
- a duplicate recipe title, which would break cart membership and permalinks
- a library title that would hijack a `((Chapter 22))` cross-reference
- raw HTML, a literal `\uXXXX` escape, or a mistyped field name
- a course that would classify differently from the one declared — the failure
  that otherwise leaves a recipe in search but invisible on its own menu page

Warnings print without blocking: a near-duplicate facet value, a main with no
pull temperature, a dish that mentions a Dutch oven or a stone with no matching
capacity entry, and a shopping line that repeats something already listed.

### Photos

New content needs no image data in the payload. Once it is in `data.json`, the
new manifest keys exist as gaps and the existing fetcher fills them:

```bash
npm run fetch-images -- --only ch65
npm run review-images        # look at every match before trusting it
npm run build
```

### The PDF

`content/*.json` feeds the web app only — `build_pdf.py` still assembles `book/`
alone, so the app will report more menus than the book prints. `npm run emit-html`
writes the generated chapters to `book/_generated/` in the book's own markup, to
paste into a `book/` file when you next reprint.

## How the build works

`book/*.html` is the source of truth for the PDF and for everything written by
hand; `content/*.json` is an additive second source that feeds the app.
`data/extract.py` parses both into `data/data.json`, which both builds consume.
The app is developed as three separate files in `app/` and inlined into one file
for publishing.

See `CLAUDE.md` for the data model, conventions and the traps.

## Layout

```
book/     chapter HTML — edit this to change the printed book
content/  JSON payloads that add menus/recipes/library items to the app
          PROMPT.md   the brief to paste into Claude
          examples/   one worked payload per kind
data/     extraction and the hand-written metadata that annotates it
          content.py  loads, validates and renders content/*.json
          schema/     content.schema.json, the payload contract
app/      index.html, styles.css, app.js — edit these to change the app
scripts/  build_app.py, build_pdf.py
tests/    smoke.mjs
dist/     build output
```
