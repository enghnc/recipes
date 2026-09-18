# Fire &amp; Kettle — project notes

A live-fire cookbook that exists in two forms built from one source: a 433-page
PDF and a searchable web app. **The book HTML in `book/` is the single source of
truth.** The app is generated from it. Never hand-edit `app/data.js`,
`data/data.json` or anything in `dist/` — they are build artefacts and will be
overwritten.

## The rule the whole book obeys

Every recipe is cooked over charcoal or wood on **no more than two 22-inch Weber
kettles**, using at most three accessories: a heat deflector, a rotisserie and a
pizza stone. No oven, no stovetop. If a proposed recipe cannot be cooked that
way, it does not belong here — or it goes in the showpiece chapter with an
explicit note that it breaks the rule (see `asado al palo`, Ch 50).

## Layout

```
book/          chapter HTML, numbered in reading order. The source of truth.
  print.css    stylesheet for the PDF only
data/          Python modules that annotate and extract the book
  extract.py   parses book/ -> data/data.json          (run by both builds)
  capacity.py  equipment limits per menu (vessels, grate area, spit loads)
  plating_a.py  plating_b.py   "To the table" notes, keyed chapter -> recipe
  impress.py   which menus and recipes carry a showpiece moment
app/           the web app, edit these three
  index.html   markup only
  styles.css
  app.js
  data.js      GENERATED
scripts/       build_app.py, build_pdf.py
tests/         smoke.mjs
dist/          GENERATED output
```

## Commands

```bash
npm run build        # extract, then build the web app into dist/
npm run build:pdf    # extract, then build the PDF into dist/
npm test             # run the smoke tests against dist/
npm run dev          # serve app/ at http://localhost:8000
```

`npm run dev` needs `npm run build` first, because the app reads `app/data.js`.

## Data model

`extract.py` produces `{menus, library, showpieces, kettle}`.

A **menu** is a book chapter with `id` (`ch25`), `title`, `lead`, `part`,
`blocks` (raw HTML for menu / grill / timeline / shopping), `recipes`, plus the
facets hand-written in `extract.py`'s `META` dict: `region`, `continent`,
`season[]`, `occasion[]`, `proteins[]`, `complexity`, `kettles`,
`accessories[]`, `leadHours`, `activeMin`, `totalMin`, `wood[]`, `cost`,
`heat`, `coldOK`, `diet[]`, `special[]`, `technique[]`. Plus `cap`,
`maxServes` and `fuel` from `capacity.py`, and `impress` / `impressWhy`.

A **recipe** has `title`, `native`, `meta`, `course`, `headnote`,
`ingredients[]` (`{type: 'item'|'sub', text}`), `method[]`, `notes[]`,
`plating` and `cap`. Course is derived from the `meta` line by `classify()`.

**Library** entries are the shared doughs, sauces, rubs and marinades
(chapters 19–24, 51–53, 56). **Showpieces** are chapter 50.

## Adding to the book

To add a **menu**: write the chapter HTML into a new or existing `book/` file
using the markup of an existing chapter, add the file to `MENU_FILES` and the
chapter to `META` and `PART_OF` in `extract.py`, add an entry to `CAPACITY` in
`capacity.py`, add plating notes in `plating_b.py` (or an inline
`<div class="plate">` in the chapter), add the file to `MANIFEST` in
`build_pdf.py`, and add TOC entries in `book/01_front_part1.html`. Then
`npm run build && npm test`.

To add a **recipe** to an existing menu: add a `<div class="recipe">` block in
the right course order. Give it a `.plate` block or an entry in `plating_b.py` —
`npm run build` prints any recipe missing one.

## Conventions that matter

- **Every recipe needs a plating note.** The extractor reports gaps; keep the
  count at zero.
- **Temperatures are instructions, times are estimates.** Write pull
  temperatures, not just minutes.
- **Prose style:** plain, direct, no em-dash asides stacked up, no "not X but Y"
  constructions. Name the specific failure mode of a dish rather than saying it
  is tricky.
- **Metadata is not decoration.** `capacity.py` drives real answers about what
  fits on two kettles at 12 and 16 servings. If you add a Dutch-oven dish and do
  not give it a `dutch` entry with `qt8`, the app will silently tell the user it
  scales fine.

## Traps worth knowing

- **Do not write the app as one file again.** The CSS and JS were previously in
  a single HTML template and shared comment markers like
  `/* ---------- shopping ---------- */`. Two separate patches matched the CSS
  copy first and injected ~130 lines of JavaScript into the stylesheet. That is
  why `app/` is split.
- **`window.print()` does nothing** inside the artifact sandbox. The app copies
  a plain-text export to the clipboard instead (`exportText`).
- **Browser storage is per viewer and may be unavailable.** Everything goes
  through the `store` helper, which swallows exceptions. Never call
  `localStorage` directly.
- **A syntax check is not a test.** Both serious bugs so far parsed cleanly and
  failed at runtime. `tests/smoke.mjs` executes every view; run it.
- **Publishing needs the single file.** The artifact host requires one
  self-contained HTML document, which is the only reason `build_app.py` inlines
  everything into `dist/`.

## Shopping-list engine

The most intricate part of `app.js`, in this order:

1. `splitIngredient` — one written line can name several purchases
   (`"1 tbsp each granulated garlic and onion"`, `"salt and pepper"`).
2. `libraryRef` — expands `"Chimichurri (Chapter 22)"` into that recipe's own
   ingredients. There are 111 such cross-references in the book.
3. `recipeEntries` — applies the serving multiplier. Sections headed
   **per glass** multiply by the number of servings; everything else scales by
   `servings / 8`.
4. `aggregate` — merges by normalised name across units.
5. `shoppingLine` — converts to something a shop sells: bottles for drinks,
   jars and bags for spices and dry goods, bunches and heads for loose produce.

When editing it, re-run the tests and eyeball a whole-menu list. The failure
mode is not a crash, it is a list that quietly says `50 ml Fernet Branca`.
