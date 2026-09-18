#!/usr/bin/env python3
"""Assemble Fire & Kettle from HTML fragments and render to PDF."""

import sys, pathlib
from weasyprint import HTML, CSS

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOOK = ROOT / "book"
DATA = ROOT / "data"
OUT = ROOT / "dist"
OUT.mkdir(parents=True, exist_ok=True)

# Fragments render in this order. Add menu parts here as they're written.
MANIFEST = [
    "01_front_part1.html",
    "02_part2_part3.html",
    "03_part4_menus.html",
    "04_part5_menus.html",
    "05_part6_menus.html",
    "06_part7_menus.html",
    "07_part8_plating.html",
    "08_part9_impress.html",
    "09_part10_sauces.html",
    "10_part11_steak_bistro.html",
    "11_part12_sauces_sandwiches.html",
    "12_part13_14.html",
    "13_ch62_deli.html",
    "14_brunch.html",
]

def inject_plating(html):
    """Append a 'To the table' block to every recipe that has plating notes."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return html
    import json as _json, pathlib as _p, re as _re
    data_path = DATA / "data.json"
    if not data_path.exists():
        return html
    data = _json.loads(data_path.read_text(encoding="utf-8"))
    lookup = {}
    for m in data["menus"]:
        for r in m["recipes"]:
            if r.get("plating"):
                lookup[(m["id"], r["title"])] = r["plating"]
    for r in data.get("library", []):
        if r.get("plating"):
            lookup[(r["chapterId"], r["title"])] = r["plating"]
    if not lookup:
        return html
    soup = BeautifulSoup(html, "html.parser")
    n = 0
    for sec in soup.select("section.chapter"):
        cid = sec.get("id")
        for div in sec.select(".recipe"):
            el = div.select_one(".rtitle")
            if not el:
                continue
            el2 = BeautifulSoup(str(el), "html.parser")
            nat = el2.select_one(".native")
            if nat:
                nat.extract()
            title = _re.sub(r"\s+", " ", el2.get_text(" ", strip=True)).strip()
            pl = lookup.get((cid, title))
            if not pl:
                continue
            block = BeautifulSoup(
                '<div class="plate"><span class="lbl">' + ("Keeping" if pl["style"] == "keeping" else "To the table \u00b7 " + pl["style"]) + '</span>' + pl["text"] + '</div>', "html.parser")
            div.append(block)
            n += 1
    print(f"  · plating blocks injected: {n}")
    return str(soup)


SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Fire &amp; Kettle</title>
</head>
<body>
{body}
</body>
</html>"""


def build(outname="Fire-and-Kettle.pdf"):
    parts = []
    for name in MANIFEST:
        p = BOOK / name
        if not p.exists():
            print(f"  ! missing fragment: {name}", file=sys.stderr)
            continue
        parts.append(p.read_text(encoding="utf-8"))
        print(f"  + {name}")

    html = SHELL.format(body="\n\n".join(parts))
    html = inject_plating(html)
    (BOOK / "_assembled.html").write_text(html, encoding="utf-8")

    doc = HTML(filename=str(BOOK / "_assembled.html"))
    css = CSS(filename=str(BOOK / "print.css"))
    target = OUT / outname
    doc.write_pdf(str(target), stylesheets=[css])

    from pypdf import PdfReader
    pages = len(PdfReader(str(target)).pages)
    size_mb = target.stat().st_size / 1_048_576
    print(f"\n  {target.name}: {pages} pages, {size_mb:.1f} MB")
    return target


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "Fire-and-Kettle.pdf")
