#!/usr/bin/env python3
"""Source CC-licensed photos for menus and recipes via the Openverse API.

  python3 scripts/fetch_images.py --menus            # just the 34 menu hero photos
  python3 scripts/fetch_images.py --recipes          # every recipe (menus + library + showpieces)
  python3 scripts/fetch_images.py                    # both
  python3 scripts/fetch_images.py --only ch25        # one chapter only
  python3 scripts/fetch_images.py --limit 150        # stop after N successful fetches this run

Writes media/manifest.json — id -> {file, credit, creditUrl, license, licenseUrl,
sourceUrl, query} — plus the actual jpgs under media/menus/ and media/recipes/<chapterId>/.
`data/extract.py` picks up any entry here by exact key on the next `npm run build`.

Every result is filtered to license_type=commercial (this book is print-and-sell, not just
a hobby site) via Openverse (api.openverse.org), which aggregates CC-licensed/public-domain
photos from Flickr, Wikimedia Commons, museums, etc. with real creator/license/source URLs
attached — never guessed.

Openverse's anonymous quota is 200 requests/day, 20/min. This script is safe to re-run:
existing manifest entries are left alone, so picking up where a previous run stopped (or
continuing tomorrow once the quota resets) just fills in whatever is still missing.
"""
import argparse, io, json, pathlib, re, sys, time, urllib.error, urllib.parse, urllib.request
from PIL import Image

MAX_DIM = 1600   # long edge, px — plenty for a hero image or a print page, not a full-res original
JPEG_QUALITY = 82

ROOT = pathlib.Path(__file__).resolve().parent.parent
MEDIA = ROOT / "media"
DATA = ROOT / "data" / "data.json"
API = "https://api.openverse.org/v1/images/"
UA = "fire-and-kettle-cookbook/1.0 (personal project; contact via github)"


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (s[:60] or "photo").strip("-")


def search(query):
    qs = urllib.parse.urlencode({"q": query, "license_type": "commercial", "page_size": 5})
    req = urllib.request.Request(API + "?" + qs, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.load(resp)


def candidates_in(results):
    return [r for r in results.get("results", []) if r.get("url") and r.get("license")]


def download(url, dest):
    """Fetch, then downsize/recompress — sourced originals run 1-5+ MB each (many megapixels
    of Flickr/Wikimedia full-res), and this site only ever shows them as a card thumbnail or
    a hero image. Re-encoding to a sane max dimension cuts total storage/bandwidth by ~10x
    with no visible loss at the sizes this app actually displays them."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read()
    img = Image.open(io.BytesIO(body))
    img = img.convert("RGB")
    if max(img.size) > MAX_DIM:
        img.thumbnail((MAX_DIM, MAX_DIM), Image.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "JPEG", quality=JPEG_QUALITY, optimize=True)


# library/showpiece chapters cover very specific technique names ("Santa Maria Rub",
# "Café de Paris Butter") that a title-only search rarely matches — a plain category
# term is a far better fallback than guessing at proper nouns in the title.
CATEGORY_FALLBACK = {
    "ch19": "bread dough", "ch20": "flatbread", "ch21": "pastry dough",
    "ch22": "sauce", "ch23": "spice rub", "ch24": "marinade",
    "ch51": "brown sauce", "ch52": "compound butter", "ch53": "steak dinner",
    "ch56": "barbecue sauce", "ch50": "fine dining plated food",
}


def query_candidates(title, region, proteins, chapter_id=None):
    """Book titles are often stylized ("Kettle Thanksgiving", "Café de Paris Butter")
    rather than real-world search terms. Try the title first, then its first clause (the
    part before "&"/"·", which is often the actual dish name), then a plain
    protein+region description, then the chapter's general category — each tier trades
    specificity for a better chance of turning up something food-related at all."""
    cands = [title + " food"]
    first_clause = re.split(r"\s*[&·]\s*", title)[0].strip()
    if first_clause and first_clause.lower() != title.lower():
        cands.append(first_clause + " food")
    # a lone, ordinary-English capitalized word from the title is sometimes the real dish
    # name buried in a stylized title ("Down East Clambake" -> "Clambake") — try it before
    # the generic protein/category fallbacks, since a specific real noun usually beats a
    # generic combo even when the combo also happens to return *a* result
    for w in re.findall(r"[A-Z][a-z]{4,}", title):
        if w not in cands:
            cands.append(w)
    if proteins:
        country = (region or "").split(" · ")[0]
        cands.append((proteins[0] + " " + country + " barbecue").strip())
        cands.append(proteins[0] + " barbecue")
    if chapter_id in CATEGORY_FALLBACK:
        cands.append(CATEGORY_FALLBACK[chapter_id])
    return cands


def fetch_one(queries, dest_rel, key, table):
    if key in table:
        return "skip (already have one)", None
    if isinstance(queries, str):
        queries = [queries]
    hit = used_query = None
    dest = MEDIA / dest_rel
    for q in queries:
        try:
            results = search(q)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                return "RATE_LIMITED", None
            continue
        except Exception:
            continue
        for cand in candidates_in(results):
            try:
                download(cand["url"], dest)
            except Exception:
                continue  # stale/dead link on this candidate — try the next one
            hit, used_query = cand, q
            break
        if hit:
            break
    if not hit:
        return "no licensed (or all dead-linked) result (tried: " + " / ".join(queries) + ")", None
    lic = (hit.get("license") or "").upper()
    if hit.get("license_version"):
        lic += " " + hit["license_version"]
    table[key] = {
        "file": dest_rel,
        "credit": hit.get("creator") or hit.get("provider") or "unknown",
        "creditUrl": hit.get("creator_url") or "",
        "license": lic,
        "licenseUrl": hit.get("license_url") or "",
        "sourceUrl": hit.get("foreign_landing_url") or hit["url"],
        "query": used_query,
    }
    return "OK", used_query


def load_manifest():
    if (MEDIA / "manifest.json").exists():
        m = json.loads((MEDIA / "manifest.json").read_text(encoding="utf-8"))
    else:
        m = {}
    m.setdefault("menus", {})
    m.setdefault("recipes", {})
    return m


def save_manifest(m):
    MEDIA.mkdir(exist_ok=True)
    (MEDIA / "manifest.json").write_text(
        json.dumps(m, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--menus", action="store_true")
    ap.add_argument("--recipes", action="store_true")
    ap.add_argument("--only", help="restrict to one chapter id, e.g. ch25")
    ap.add_argument("--limit", type=int, default=0, help="stop after N successful fetches (0 = unlimited)")
    args = ap.parse_args()
    if not args.menus and not args.recipes:
        args.menus = args.recipes = True

    db = json.loads(DATA.read_text(encoding="utf-8"))
    manifest = load_manifest()
    counts = {"OK": 0, "skip": 0, "fail": 0}
    stop = False

    def budget_ok():
        return args.limit <= 0 or counts["OK"] < args.limit

    def do_item(kind, key, title, queries, dest_rel, table):
        nonlocal stop
        status, _ = fetch_one(queries, dest_rel, key, table)
        bucket = "OK" if status == "OK" else "skip" if status.startswith("skip") else "fail"
        counts[bucket] += 1
        mark = {"OK": "OK  ", "skip": "--  ", "fail": "??  "}[bucket]
        print(f"{mark}[{kind:6}] {key:55.55} {title:35.35} {status}")
        if status == "RATE_LIMITED":
            save_manifest(manifest)
            print("\nHit Openverse's anonymous rate limit. Manifest saved with progress so far —")
            print("re-run this script later (quota resets daily) to pick up where it left off.")
            stop = True
        elif status == "OK":
            save_manifest(manifest)
            time.sleep(0.4)

    for m in db["menus"]:
        if stop or (args.only and m["id"] != args.only):
            continue
        if args.menus and budget_ok():
            do_item("menu", m["id"], m["title"],
                    query_candidates(m["title"], m.get("region"), m.get("proteins")),
                    f"menus/{m['id']}.jpg", manifest["menus"])
        if args.recipes:
            for r in m["recipes"]:
                if stop or not budget_ok():
                    break
                key = m["id"] + "|" + r["title"]
                do_item("recipe", key, r["title"],
                        query_candidates(r["title"], m.get("region"), m.get("proteins"), m["id"]),
                        f"recipes/{m['id']}/{slug(r['title'])}.jpg", manifest["recipes"])

    if args.recipes and not args.only and not stop:
        for r in db["library"] + db.get("showpieces", []):
            if stop or not budget_ok():
                break
            key = r["chapterId"] + "|" + r["title"]
            do_item("recipe", key, r["title"], query_candidates(r["title"], None, None, r["chapterId"]),
                    f"recipes/{r['chapterId']}/{slug(r['title'])}.jpg", manifest["recipes"])

    save_manifest(manifest)
    print(f"\n{counts['OK']} fetched, {counts['skip']} already had one, {counts['fail']} failed/no-match this run.")


if __name__ == "__main__":
    main()
