# Fire &amp; Kettle — project notes

A live-fire cookbook that exists in two forms: a 424-page PDF and a searchable
web app. **The book HTML in `book/` is the source of truth for the PDF, and for
everything written by hand.** `content/*.json` is a second, additive source that
feeds the app only — see "Adding from a JSON payload". Never hand-edit
`app/data.js`, `data/data.json` or anything in `dist/` — they are build artefacts
and will be overwritten.

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
content/       JSON payloads that add menus/recipes/library items to the app
  PROMPT.md    the authoring brief to paste into Claude on the web
  examples/    one worked payload per kind (not built — outside the glob)
data/          Python modules that annotate and extract the book
  extract.py   parses book/ + content/ -> data/data.json   (run by both builds)
  content.py   loads, validates and renders content/*.json into book markup
  schema/      content.schema.json, the payload contract
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
npm run validate     # check content/*.json without writing anything
npm run vocab        # print the current facet vocabulary
npm run emit-html    # write generated chapters to book/_generated/ to paste into book/
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
`maxServes` and `fuel` from `capacity.py`, `impress` / `impressWhy`, and
`image` from `media/manifest.json`.

A **recipe** has `title`, `native`, `meta`, `course`, `headnote`,
`ingredients[]` (`{type: 'item'|'sub', text}`), `method[]`, `notes[]`,
`plating`, `cap` and `image`. Course is derived from the `meta` line by
`classify()`.

**Library** entries are the shared doughs, sauces, rubs and marinades
(chapters 19–24, 51–53, 56). **Showpieces** are chapter 50.

## Photos

`media/` holds real, checked-in photo files plus `media/manifest.json`
(menu id, or `chapterId|title` for a recipe, -> `{file, credit, creditUrl,
license, licenseUrl, sourceUrl, query}`). `extract.py` attaches whichever
entry matches by exact key as each menu/recipe's `image` field — no entry
means no photo, which the app already renders fine (`photoTag` in `app.js`
returns `''` and skips the space entirely).

- `npm run fetch-images [-- --menus|--recipes|--only chNN|--limit N]` sources
  new photos from Openverse (CC-licensed, `license_type=commercial` since
  this book is print-and-sell) and fills gaps in the manifest. Safe to
  re-run — it only fetches keys that aren't already in the manifest, so
  interrupted or rate-limited runs (anonymous Openverse quota) just resume.
- `npm run review-images` builds `media/review.html`, a local-only contact
  sheet grouped by menu, to actually look at every match before trusting it
  — a keyword search matching a specific recipe title is inherently
  imperfect and needs a human's eye, not just a confidence score. Not
  published anywhere; delete a manifest entry (and re-run fetch) to replace
  a bad match.
- `npm run build` copies `media/` into `app/images/` (generated, gitignored,
  same treatment as `app/data.js`) so `npm run dev` and the real AWS-hosted
  app can serve them. The single-file artifact build
  (`dist/fire-and-kettle-app.html`) deliberately never inlines them —
  hundreds of base64 photos would defeat the point of that build — so
  photos simply don't render in that context, by design, not as a bug.
- CC-BY-style licenses require attribution: `photoTag()` always prints the
  photo's credit/license as a link on detail pages. It never does this
  inside a card grid, because those cards are `<button>`s — nesting an `<a>`
  inside one is invalid HTML and the click would also fire the card's own
  navigation (the credit is only omitted there, never dropped altogether).

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

## Adding from a JSON payload

The seven coordinated edits above are the hand-authoring path. The other path is
one JSON file in `content/`, which needs none of them: no `MENU_FILES`, no `META`,
no `PART_OF`, no `CAPACITY`, no plating table, no TOC entry.

```bash
# write content/ch65-whatever.json (see content/PROMPT.md and content/examples/)
npm run validate && npm run build && npm test
```

Four payload kinds: `menu` (a whole chapter), `recipe` (one dish into an existing
chapter), `library` (a shared sauce/dough/rub), `patch` (facet edits to an existing
menu, which is how you change categories without touching recipe text).

`content/PROMPT.md` is the brief to paste into Claude on the web along with
`data/schema/content.schema.json`. It carries the two-kettle rule, the prose style,
the closed enums and a live snapshot of the open facet vocabulary — regenerate that
snapshot with `npm run vocab` when the book has grown.

**How it works.** `data/content.py` renders each payload into the same chapter
markup `parse_recipe` and `parse_menu_chapter` already read, in memory, and
`extract.py` parses it like any other chapter. One parser, one data model. Payload
facets are merged into `META` / `PART_OF` / `CAPACITY` / `IMPRESS_*` at extract
time, so those tables stop being the complete inventory — `npm run build` prints
what it merged.

**Generated HTML is never written into `book/`.** A machine-generated file in there
would become a second place to fix content that the next build silently overwrites.

**The PDF does not see `content/`.** `build_pdf.py` still assembles `book/` only, so
the app will report more menus than the book prints. `npm run emit-html` writes the
generated chapters to `book/_generated/` to paste into a `book/` file when you next
reprint. Full parity later is small: `build_pdf.py` would call
`content.insert_chapters(soup)` and `content.splice_into(soup)` on the assembled
document, plus a TOC `<li>` and a glance-table `<tr>`.

**Validation is the point.** `npm run validate` fails on a missing plating note, a
closed-enum violation (`complexity`, `cost`, `kettles`, `heat` — the app hardcodes
those filter lists), a capacity `match` that hits zero or two recipe titles, a
duplicate recipe key, raw HTML or a literal `\uXXXX` in prose, a course that
`classify()` would read differently from the one declared, a library title that
would hijack a `((Chapter NN))` cross-reference, and any facet value not already in
the book that is not declared in `newFacetValues`. That last gate is what stops a
`Cast Iron` typo becoming a duplicate one-item filter chip alongside `Cast iron`.

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
4. `aggregate` — merges by normalised name across units. **Called exactly
   once, on the concatenation of every cart item's raw entries** (see
   `viewList`) — never per-recipe/per-menu, or items that two different
   recipes both call for show up as separate, unmerged lines.
5. `shoppingLine` — converts to something a shop sells: bottles for drinks,
   jars and bags for spices and dry goods, bunches and heads for loose produce.
   The `PACKS` table is ordered and first-match-wins — a compound name like
   `"garlic salt"` must match a specific jar/bag/bottle pattern *before* it
   falls through to a generic bare-word rule (e.g. `/\bsalt\b/`), or it gets
   sized like the generic rule's container instead of its own.
6. `buyLinks` — turns the aggregated item's plain name into an Amazon search
   link and a "near me" local-store search link, rendered next to each row
   in `viewList`. Both are plain search URLs (no API key, no affiliate
   integration), so they degrade gracefully — worst case is a broad search
   rather than a dead link.

When editing it, re-run the tests and eyeball a whole-menu list. The failure
mode is not a crash, it is a list that quietly says `50 ml Fernet Branca`.

## Glossary links

`GLOSSARY` + `glossify()` in `app.js` link a small, hand-picked set of
technique/ingredient terms (headnote and method text on recipe pages) out to
Wikipedia. Every URL in `GLOSSARY` was verified to actually resolve before
being added — never guess one in. `glossify()` runs on already-`esc()`/`hl()`-
escaped HTML and splits on existing tags before matching, so it's safe to
chain after `hl()` without corrupting a `<mark>` or leaving a term linked
twice.
