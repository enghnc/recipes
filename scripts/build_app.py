#!/usr/bin/env python3
"""Build the web app.

  data/extract.py     book HTML  ->  data/data.json
  this script         app/*      ->  app/data.js  and  dist/fire-and-kettle-app.html

The dist file is a single self-contained HTML page: that is the form the
artifact host requires, and the only reason the inlining step exists.
Develop against app/index.html, never against dist/.
"""
import json
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
APP = ROOT / "app"
DIST = ROOT / "dist"
MEDIA = ROOT / "media"


def run_extract():
    print("· extracting recipes from book/ ...")
    subprocess.run([sys.executable, "extract.py"], cwd=ROOT / "data", check=True)


def sync_images():
    """media/ (the real, checked-in source photos) -> app/images/ (a generated copy,
    same as app/data.js, so `npm run dev`'s static server and the AWS deploy both find
    them at a plain relative path). The single-file artifact build never gets images:
    inlining hundreds of photos as base64 would defeat the point of that build."""
    dest = APP / "images"
    if dest.exists():
        shutil.rmtree(dest)
    if not MEDIA.exists():
        return 0
    n = 0
    for src in MEDIA.rglob("*"):
        if src.is_file() and src.name not in ("manifest.json", "review.html"):
            out = dest / src.relative_to(MEDIA)
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, out)
            n += 1
    return n


def write_data_js(data_text):
    (APP / "data.js").write_text("window.FK_DATA = " + data_text + ";\n", encoding="utf-8")


def inline():
    html = (APP / "index.html").read_text(encoding="utf-8")
    css = (APP / "styles.css").read_text(encoding="utf-8")
    js = (APP / "app.js").read_text(encoding="utf-8")
    data = (ROOT / "data" / "data.json").read_text(encoding="utf-8")

    html = html.replace('<link rel="stylesheet" href="./styles.css">',
                        "<style>\n" + css + "\n</style>")
    html = html.replace('<script src="./data.js"></script>',
                        '<script id="data" type="application/json">'
                        + data.replace("</script>", "<\\/script>") + "</script>")
    html = html.replace('<script src="./app.js"></script>',
                        "<script>\n" + js + "\n</script>")

    DIST.mkdir(exist_ok=True)
    target = DIST / "fire-and-kettle-app.html"
    target.write_text(html, encoding="utf-8")
    return target, data


def main():
    if "--no-extract" not in sys.argv:
        run_extract()
    data = (ROOT / "data" / "data.json").read_text(encoding="utf-8")
    write_data_js(data)
    target, _ = inline()
    n_images = sync_images()

    db = json.loads(data)
    n = (sum(len(m["recipes"]) for m in db["menus"])
         + len(db["library"]) + len(db.get("showpieces", [])))
    print(f"· {len(db['menus'])} menus, {n} recipes")
    print(f"· {n_images} photo(s) synced to app/images/")
    print(f"· {target.relative_to(ROOT)}  ({target.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
