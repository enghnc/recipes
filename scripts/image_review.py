#!/usr/bin/env python3
"""Generate a local, unpublished contact sheet of every sourced photo, grouped by
menu, so a human can actually eyeball whether each match is any good — a stock
photo matched to a specific recipe title by keyword search needs a human's
judgment, not just a search API's confidence score.

  python3 scripts/image_review.py   ->  media/review.html  (open it in a browser)

Not part of the app; nothing here is deployed. It reads media/manifest.json and
data/data.json only.
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
MEDIA = ROOT / "media"
DATA = ROOT / "data" / "data.json"


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def card(key, title, entry):
    if not entry:
        return f'<div class="card missing"><div class="ph">no photo</div><div class="t">{esc(title)}</div></div>'
    src = "../media/" + entry["file"]
    credit = esc(entry.get("credit", ""))
    lic = esc(entry.get("license", ""))
    q = esc(entry.get("query", ""))
    src_url = esc(entry.get("sourceUrl", "#"))
    return (f'<div class="card"><a href="{src_url}" target="_blank"><img loading="lazy" src="{src}"></a>'
            f'<div class="t">{esc(title)}</div>'
            f'<div class="c">{credit} · {lic}</div>'
            f'<div class="q">query: “{q}”</div></div>')


def main():
    db = json.loads(DATA.read_text(encoding="utf-8"))
    manifest = json.loads((MEDIA / "manifest.json").read_text(encoding="utf-8")) if (MEDIA / "manifest.json").exists() else {"menus": {}, "recipes": {}}
    menus_m, recipes_m = manifest.get("menus", {}), manifest.get("recipes", {})

    sections = []
    n_have = n_missing = 0
    for m in db["menus"]:
        cards = [card(m["id"], m["title"] + "  (menu photo)", menus_m.get(m["id"]))]
        for r in m["recipes"]:
            key = m["id"] + "|" + r["title"]
            cards.append(card(key, r["title"], recipes_m.get(key)))
        for c in [menus_m.get(m["id"])] + [recipes_m.get(m["id"] + "|" + r["title"]) for r in m["recipes"]]:
            n_have += 1 if c else 0
            n_missing += 0 if c else 1
        sections.append(f'<h2>{esc(m["title"])} <span class="cid">{m["id"]}</span></h2><div class="grid">{"".join(cards)}</div>')

    lib_cards = []
    for r in db["library"] + db.get("showpieces", []):
        key = r["chapterId"] + "|" + r["title"]
        entry = recipes_m.get(key)
        n_have += 1 if entry else 0
        n_missing += 0 if entry else 1
        lib_cards.append(card(key, r["title"], entry))
    sections.append(f'<h2>Library &amp; showpieces</h2><div class="grid">{"".join(lib_cards)}</div>')

    html = f"""<!doctype html><meta charset="utf-8"><title>Fire & Kettle — photo review</title>
<style>
body{{font-family:-apple-system,sans-serif;background:#f7f4ee;color:#241d16;margin:0;padding:24px 32px}}
h1{{margin:0 0 4px}} .sub{{color:#7a7268;margin-bottom:24px}}
h2{{font-size:15px;text-transform:uppercase;letter-spacing:.06em;color:#b3431f;border-bottom:1px solid #e4ddd0;padding-bottom:6px;margin-top:36px}}
.cid{{color:#a89f8e;font-weight:400;text-transform:none;letter-spacing:0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px;margin-top:12px}}
.card{{background:#fff;border:1px solid #e4ddd0;border-radius:8px;overflow:hidden;font-size:11px}}
.card img{{width:100%;height:110px;object-fit:cover;display:block;background:#eee}}
.card .ph{{width:100%;height:110px;display:flex;align-items:center;justify-content:center;background:#f0ebe0;color:#a89f8e}}
.card.missing{{border-style:dashed}}
.card .t{{padding:6px 8px 2px;font-weight:600;line-height:1.25}}
.card .c,.card .q{{padding:0 8px;color:#7a7268}}
.card .q{{padding-bottom:6px;font-style:italic}}
</style>
<h1>Photo review</h1>
<p class="sub">{n_have} sourced, {n_missing} still missing. Click any photo to open its source page and double-check the license/attribution. This page is local only — nothing here is published.</p>
{"".join(sections)}
"""
    (MEDIA / "review.html").write_text(html, encoding="utf-8")
    print(f"· {n_have} photos, {n_missing} missing -> media/review.html")


if __name__ == "__main__":
    main()
