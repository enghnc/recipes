# Photos not found

These items don't have a photo. Rather than show a wrong one, `photoTag()` in
`app/app.js` just renders nothing for them — no broken image, no placeholder.

Each was tried through 5 rounds of searches on Openverse (CC-licensed, commercial-use
photos aggregated from Flickr, Wikimedia Commons, etc.), from the literal dish name
down to plain single-word queries. Every attempt returned *something*, but nothing
that was actually a photo of the dish — the queries kept matching unrelated content
that happened to share a word or a loose tag with the title. Listed with what the
searches actually turned up, so a future attempt doesn't retread the same ground.

| Recipe | Chapter | Tried | What kept coming back instead |
|---|---|---|---|
| Smoked Baked Beans · Buttermilk Slaw · Grilled Corn | ch26 Fourth of July Low & Slow | "smoked baked beans", "baked beans bbq side dish", "baked beans" | A baked potato and a cappuccino at an Italian fast-food counter |
| Boiled Peanuts | ch57 Carolina Pulled Pork | "boiled peanuts southern", "boiled peanuts", "peanuts in shell" | A peanut-shaped garden sculpture; a marshmallow s'mores sundae |
| Grilled Apricots with Lavender Honey | ch55 Grand Aïoli | "grilled apricots dessert", "apricots honey", "stone fruit dessert" | An empty restaurant dining room; a bowl of granola with dried apricot pieces |
| Egg Cream | ch62 New York Deli | "egg cream soda drink", "egg cream", "chocolate soda fountain drink" | Vintage Tab/Egg Nog cans; a vintage dairy-shop photo; a box of chocolates |

## To add one later

1. Find (or take) a real photo of the dish, licensed for commercial use.
2. Drop the file at `media/recipes/<chapterId>/<slug>.jpg` (see any existing file
   for the naming pattern `scripts/fetch_images.py`'s `slug()` produces).
3. Add the matching entry to `media/manifest.json` under `"recipes"`, keyed
   `"<chapterId>|<exact recipe title>"` — `{file, credit, creditUrl, license,
   licenseUrl, sourceUrl, query}` (see any existing entry for the shape).
4. Remove this file's row for that dish.
5. `npm run build` picks it up automatically.
