# Writing a Fire & Kettle content payload

You are writing a recipe chapter for **Fire & Kettle**, a live-fire cookbook that
exists as a 424-page PDF and a searchable web app. Your output is a single JSON
file that gets dropped into the book's `content/` folder and built.

Read all of this before writing anything. At the end, output **one JSON object and
nothing else** — no commentary, no markdown fences.

---

## 1. The rule the whole book obeys

> Every recipe is cooked over charcoal or wood on **no more than two 22-inch Weber
> kettles**, using at most three accessories: a heat deflector, a rotisserie and a
> pizza stone. No oven, no stovetop.

If a dish cannot be cooked that way, it does not belong in the book. Do not write a
menu that quietly assumes a hob for a sauce or an oven for bread. A pan on the grate
over the coals is fine and is how the book does it — say so explicitly in the method.

The book is written for **eight people**. Every quantity is for eight.

---

## 2. How to write

The book has a voice. Match it.

- **Plain and direct.** No stacked em-dash asides. No "not X, but Y" constructions.
- **Name the specific failure.** Never write that a dish is tricky or needs care.
  Write what actually goes wrong: "The garlic milk splits if it boils." "Cold sausage
  splits before the middle is warm." "A sweet plum makes a chutney."
- **Temperatures are instructions, times are estimates.** Write pull temperatures,
  in bold, for anything where doneness matters: `**145°F**`. Times get a range.
- **No filler.** If a step is obvious, cut it.
- **Headnotes are two or three sentences** and earn their place by saying something
  the method cannot.

## 3. Markup inside prose

Prose fields are plain text. **No HTML.** Three markers are expanded:

| You write | Renders as | Use it for |
|---|---|---|
| `**145°F**` | bold | pull temperatures, key quantities |
| `*mtsvadi*` | italic | foreign words on first use |
| `Chimichurri ((Chapter 22))` | a grey cross-reference | pointing at a shared library recipe |

The cross-reference marker is load-bearing: the app expands it to pull that library
recipe's own ingredients into the shopping list. Only use it for a recipe that really
is in the shared library, and give the right chapter number (see §7).

Never write a literal `\uXXXX` escape. Write the character: `—`, `·`, `°`, `ñ`.

---

## 4. Which payload to write

| `kind` | Use when |
|---|---|
| `menu` | Adding a whole new chapter: a menu with its own recipes, grill plan and shopping list. |
| `recipe` | Adding one dish to a chapter that already exists. |
| `library` | Adding a shared sauce, dough, rub or marinade that several menus can reference. |
| `patch` | Only changing the facets of an existing menu. Touches no recipe text. |

The full field list is in `data/schema/content.schema.json`, and there is a complete
worked example of each kind in `content/examples/`. Read the schema — every field has
a description explaining what it is for.

---

## 5. Closed vocabularies

These four are hardcoded in the app's filter sidebar. A value outside them renders on
the page but can never be filtered for, so it is rejected at build time.

- `complexity`: `Light` · `Moderate` · `Heavy` · `All day`
- `cost`: `$` · `$$` · `$$$` · `$$$$`
- `kettles`: `1` or `2` — this is the book's central rule, not an oversight
- `heat`: `1` mild · `2` medium · `3` hot · `5` fierce. **There is no 4** — the app
  renders it with a blank label.

Also closed: `season` is `Spring` `Summer` `Fall` `Winter`; `course` is `Starter`
`Main` `Side` `Sauce` `Dessert` `Drink`; a note's `kind` is `note` `warn` `ahead`.

---

## 6. Open vocabularies — reuse before you invent

These grow as the book grows, and every distinct value becomes a filter chip. A near
miss like `Cast Iron` when the book already says `Cast iron` creates a duplicate chip
that splits the filter in two. **Reuse an existing value whenever one fits.**

Current vocabulary (run `npm run vocab` for the live list):

- **region** (31): "Argentina", "China", "Cuba", "France · Alsace", "France · Paris", "France · Provence", "Greece", "Hawaii", "India · Punjab", "Italy", "Jamaica", "Japan", "Mexico", "Morocco", "Peru", "Scandinavia", "Spain · Catalonia", "Taiwan", "Turkey", "United States", "United States · California", "United States · Carolinas", "United States · Kentucky", "United States · Louisiana", "United States · Midwest", "United States · New England", "United States · New York", "United States · Pacific NW", "United States · Philadelphia", "United States · South", "Vietnam"
- **continent** (7): "Africa", "Asia", "Caribbean", "Europe", "North America", "Pacific", "South America"
- **occasion** (27): "Birthday", "Brunch", "Casual", "Celebration", "Christmas Eve", "Church picnic", "Coastal", "Cookout", "Crowd", "Dinner party", "Family gathering", "Festival", "Fiesta", "Graduation", "Harvest feast", "Holiday", "Leftovers", "Long lunch", "Long morning", "Lunar New Year", "Lunch", "Mardi Gras", "Pig picking", "Project", "Ranch party", "Tailgate", "Thanksgiving"
- **proteins** (16): "Beef", "Chicken", "Duck", "Eggs", "Fish", "Lamb", "Mutton", "Pork", "Poultry", "Quail", "Rabbit", "Sausage", "Shellfish", "Turkey", "Vegetarian", "Venison"
- **accessories** (5): "Deflector", "Plancha", "Rotisserie", "Stone", "Vortex"
- **wood** (18): "Alder", "Apple", "Birch", "Cedar planks", "Cherry", "Guava", "Hickory", "Juniper", "Kiawe", "Maple", "Mesquite", "Oak", "Olive", "Pear", "Pecan", "Pimento", "Red oak", "Vine cuttings"
- **diet** (10): "Dairy-free", "Dairy-free-adaptable", "Gluten-free-adaptable", "No pork", "No pork-adaptable", "No shellfish", "No shellfish-adaptable", "Pescatarian", "Pescatarian-adaptable", "Vegetarian options"
- **special** (62): "Achiote paste", "Ají amarillo", "Ají panca", "Ale-8-One", "Aleppo pepper", "Aquavit", "Banana leaves", "Bao flour", "Birch beer", "Calçots", "Cedar planks", "Cheerwine", "Chicory coffee", "Chinkiang vinegar", "Country ham", "Creole mustard", "Demi-glace", "Fennel pollen", "Food-grade lye", "Fresh cheese curds", "Fromage blanc", "Green peanuts", "Gruyère", "Guava paste", "Huacatay", "Juniper", "Kashmiri chilli", "Kasoori methi", "Kaymak", "Kiawe", "Lavender honey", "Lingonberry", "Long hots", "Lá lot-free", "Lá lốt leaves", "Maggi seasoning", "Maltose", "Marionberries", "Masa harina", "Matzo meal", "Mochiko", "Mochiko-free", "Mutton", "Pekmez", "Piloncillo", "Pimento wood", "Pink curing salt #1", "Pinquito beans", "Ras el hanout", "Red oak", "Rice flour", "Rockweed", "Rye flour", "Salt cod", "Scotch bonnet", "Sour orange", "Stone-ground grits", "Sucuk", "Sweet potato starch", "Tiger nuts", "Tortilla press", "Ñora peppers"
- **technique** (22): "Baking", "Cast iron", "Comal", "Curing", "Deflector", "Direct", "Dutch oven", "Embers", "Flatbread", "Frying", "Holding bath", "Plancha", "Planking", "Robata", "Rotisserie", "Skewers", "Snake", "Spatchcock", "Steaming", "Stone", "Two-zone", "Vortex"
- **plating.style** (13): "basket", "board", "bowl", "communal", "glass", "hand", "in the dish", "in the molcajete", "in the pan", "keeping", "newspaper", "plate", "platter"

Any value you use that is **not** in these lists must also be declared in
`newFacetValues`, keyed by facet:

```json
"newFacetValues": { "region": ["Georgia"], "special": ["Blue fenugreek"] }
```

Use `{}` when you have reused only existing values. This is a deliberate speed bump:
it makes inventing a new category a decision rather than a typo. The build rejects an
undeclared new value, and rejects a value that differs from an existing one only in
case or punctuation.

---

## 7. The shared library

Chapters 19–24 and 51–56 hold doughs, sauces, rubs and marinades that menus reference
rather than repeat:

- **19** enriched bun dough · **20** flatbread doughs · **21** pastry, biscuit, batter
- **22** sauces · **23** rubs and spice blends · **24** brines and marinades
- **51** stock, demi-glace and small sauces · **52** more sauces · **53** steak and
  bistro · **56** sandwich components

If your menu needs a sauce that already exists there, reference it with
`((Chapter 22))` instead of writing it out. If it needs a genuinely new shared
component, write a separate `kind: "library"` payload for it.

A new library title must not be a prefix or substring of an existing one. Cross-
references resolve fuzzily, so adding `Chimichurri Rojo` would hijack every existing
`Chimichurri (Chapter 22)` reference and pull the wrong ingredients into shopping
lists.

---

## 8. Capacity — the part that is easy to get wrong

`capacity` is not decoration. The app uses it to answer honestly whether a menu scales
from 8 to 12 or 16 people on two kettles. **A dish with no capacity entry is silently
reported as scaling fine**, which is the single worst failure this file can have.

Give every dish that occupies a vessel or a stretch of grate an entry. `match` is a
substring of exactly one recipe title in the chapter, and the numbers are all *at 8
servings* — the app scales them itself.

| `type` | Fields | For |
|---|---|---|
| `grate` | `sqin8`, `zone` (`direct`/`indirect`/`full`) | anything cooked on the bars |
| `skillet` | `loads8` | 12-inch cast-iron pan loads |
| `dutch` | `qt8` | Dutch oven volume |
| `spit` | `lb8`, `len8` | rotisserie weight and inches of spit |
| `stone` | `units8`, `minEach` | pizza stone, one item at a time |
| `vortex` | `pieces8` | pieces ringed around a vortex |
| `steamer` | `qt8` | the big steaming pan |
| `fry` | `qt8` | pot of frying oil |
| `pan` | `name`, `count8`, `perUnit` | foil pans, muffin tins, loaf pans |

For reference, one 22-inch kettle gives about 210 sq in of direct grate, 250 indirect,
350 full; the rotisserie takes 15 lb over 17 inches; the stone is 15 inches.

`notes` must say what actually limits the menu — usually one vessel, not the grate.

---

## 9. The four chapter blocks

A `menu` payload needs all four, written as structured data (the build renders the
HTML):

- **`menu`** — one line per dish in serving order, with a short clause saying what it is.
- **`grill`** — the fuel, then one paragraph per kettle explaining what happens on it,
  then a paragraph giving charcoal quantity. Be concrete about zones and timing.
- **`timeline`** — a prep countdown in `T–24 hr` / `T–45 min` / `T–0` form, ending at
  `T–0`. It should be genuinely followable, not decorative.
- **`shopping`** — categories to items. Use `Meat`, `Seafood`, `Produce`, `Dairy`,
  `Bakery`, `Pantry`, `Drinks`, `Fuel`, and `Special` for anything that needs ordering
  ahead. `Special` is load-bearing: the app flags those items for the user.

---

## 10. Every recipe needs a plating note

No exceptions — the book's gap count is zero and the build enforces it. `plating` says
how the dish physically arrives in front of people:

```json
"plating": {"style": "board", "text": "Straight onto the flatbread it rested on, carried to the table on a board, no plates until people ask."}
```

`style` is lowercase. Existing styles: `board` `platter` `plate` `bowl` `communal`
`in the pan` `in the dish` `hand` `newspaper` `glass` `basket` `keeping`. Use
`keeping` for something stored rather than served, which is normal for library items.

---

## 11. Before you output

Check each of these:

- [ ] Every dish can be cooked on at most two kettles with at most a deflector,
      rotisserie and stone. Nothing needs an oven or a hob.
- [ ] Every recipe has a `plating` note.
- [ ] Every Main has a pull temperature in bold in its method.
- [ ] Every recipe `title` is unique within its chapter.
- [ ] `course` is declared on every recipe, and `metaExtra` (if used) contains no
      course word — `main`, `side`, `sauce`, `drink`, `dessert`, `appetizer`, `rub`,
      `marinade`, `bread`. A stray "with a pan sauce" reclassifies a Main as a Sauce.
- [ ] Every `capacity.items[].match` matches exactly one recipe title.
- [ ] Every vessel-bound dish has a capacity entry.
- [ ] All 19 facet keys are present on a `menu` payload.
- [ ] Every new facet value is declared in `newFacetValues`.
- [ ] `totalMin` ≥ `activeMin`.
- [ ] No HTML, no `\uXXXX` escapes, no unbalanced `**` or `((`.
- [ ] `chapterId` is a number not already used in the book, and `afterChapter` is an
      existing menu chapter.

Then output the JSON object alone.
