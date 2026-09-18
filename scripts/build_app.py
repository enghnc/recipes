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
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
APP = ROOT / "app"
DIST = ROOT / "dist"


def run_extract():
    print("· extracting recipes from book/ ...")
    subprocess.run([sys.executable, "extract.py"], cwd=ROOT / "data", check=True)


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

    db = json.loads(data)
    n = (sum(len(m["recipes"]) for m in db["menus"])
         + len(db["library"]) + len(db.get("showpieces", [])))
    print(f"· {len(db['menus'])} menus, {n} recipes")
    print(f"· {target.relative_to(ROOT)}  ({target.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
