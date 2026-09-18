#!/usr/bin/env python3
"""Extract every menu chapter and recipe from the book HTML into structured JSON."""

import json, pathlib, re
from bs4 import BeautifulSoup
from capacity import CAPACITY, KETTLE
try:
    from plating_a import PLATING_A as _PA
except ImportError:
    _PA = {}
try:
    from plating_b import PLATING_B as _PB, PLATING_LIB as _PL
except ImportError:
    _PB, _PL = {}, {}
PLATING = {**_PA, **_PB}
try:
    from impress import IMPRESS_MENUS, IMPRESS_RECIPES
except ImportError:
    IMPRESS_MENUS, IMPRESS_RECIPES = {}, {}

HERE = pathlib.Path(__file__).resolve().parent
BOOK = HERE.parent / "book"
MENU_FILES = ["03_part4_menus.html", "04_part5_menus.html",
              "05_part6_menus.html", "06_part7_menus.html",
              "10_part11_steak_bistro.html",
              "11_part12_sauces_sandwiches.html",
              "12_part13_14.html",
              "13_ch62_deli.html",
              "14_brunch.html"]
LIB_FILES = ["02_part2_part3.html", "09_part10_sauces.html", "10_part11_steak_bistro.html",
             "11_part12_sauces_sandwiches.html"]
SHOW_FILE = "08_part9_impress.html"

# ---------------------------------------------------------------- metadata
# Hand-curated facets keyed by chapter id. Everything the UI filters on.
META = {
 "ch25": dict(slug="asado", region="Argentina", continent="South America",
   season=["Spring","Summer"], occasion=["Family gathering"], proteins=["Beef","Pork"],
   complexity="Moderate", kettles=2, accessories=[], leadHours=24, activeMin=120,
   totalMin=240, wood=["Oak"], cost="$$$", heat=1, coldOK=False,
   diet=["No shellfish"], special=[], technique=["Direct","Two-zone","Cast iron"]),
 "ch26": dict(slug="fourth-of-july", region="United States · South", continent="North America",
   season=["Summer"], occasion=["Holiday","Crowd"], proteins=["Beef","Pork","Chicken"],
   complexity="All day", kettles=2, accessories=["Deflector","Vortex"], leadHours=12,
   activeMin=150, totalMin=840, wood=["Oak","Hickory","Cherry"], cost="$$$", heat=1,
   coldOK=False, diet=["No shellfish"], special=[], technique=["Snake","Vortex","Dutch oven"]),
 "ch27": dict(slug="yakitori", region="Japan", continent="Asia",
   season=["Summer"], occasion=["Birthday","Casual"], proteins=["Chicken","Fish"],
   complexity="Moderate", kettles=2, accessories=[], leadHours=24, activeMin=90,
   totalMin=150, wood=[], cost="$$", heat=1, coldOK=False,
   diet=["Dairy-free","No pork"], special=[], technique=["Direct","Skewers","Robata"]),
 "ch28": dict(slug="aegean", region="Greece", continent="Europe",
   season=["Summer"], occasion=["Dinner party"], proteins=["Fish","Shellfish","Lamb"],
   complexity="Light", kettles=2, accessories=[], leadHours=24, activeMin=75,
   totalMin=120, wood=["Olive","Oak"], cost="$$$", heat=1, coldOK=False,
   diet=["No pork","Pescatarian-adaptable"], special=[], technique=["Direct","Flatbread","Skewers"]),
 "ch29": dict(slug="taquiza", region="Mexico", continent="North America",
   season=["Summer","Fall"], occasion=["Fiesta","Crowd"], proteins=["Pork","Beef"],
   complexity="Moderate", kettles=2, accessories=["Rotisserie"], leadHours=12,
   activeMin=120, totalMin=240, wood=["Mesquite"], cost="$$", heat=3, coldOK=False,
   diet=["Dairy-free-adaptable","Gluten-free-adaptable"], special=["Achiote paste"],
   technique=["Rotisserie","Direct","Cast iron"]),
 "ch30": dict(slug="mechoui", region="Morocco", continent="Africa",
   season=["Fall","Winter"], occasion=["Harvest feast","Crowd"], proteins=["Lamb","Chicken"],
   complexity="All day", kettles=2, accessories=["Deflector"], leadHours=24,
   activeMin=120, totalMin=330, wood=["Oak","Apple"], cost="$$$", heat=2, coldOK=True,
   diet=["No pork","No shellfish"], special=["Ras el hanout"],
   technique=["Deflector","Direct","Flatbread","Cast iron"]),

 "ch31": dict(slug="tuscan", region="Italy", continent="Europe",
   season=["Fall"], occasion=["Dinner party"], proteins=["Pork"],
   complexity="Moderate", kettles=2, accessories=["Rotisserie","Stone"], leadHours=24,
   activeMin=110, totalMin=240, wood=["Oak","Olive"], cost="$$", heat=1, coldOK=True,
   diet=["No shellfish"], special=["Fennel pollen"],
   technique=["Rotisserie","Stone","Dutch oven","Baking"]),
 "ch32": dict(slug="pollo-a-la-brasa", region="Peru", continent="South America",
   season=["Spring","Summer"], occasion=["Birthday","Casual"], proteins=["Chicken","Beef"],
   complexity="Light", kettles=1, accessories=["Rotisserie"], leadHours=12,
   activeMin=60, totalMin=120, wood=[], cost="$", heat=2, coldOK=False,
   diet=["Dairy-free-adaptable","No pork"], special=["Ají panca","Ají amarillo","Huacatay"],
   technique=["Rotisserie","Direct","Frying"]),
 "ch33": dict(slug="tandoori", region="India · Punjab", continent="Asia",
   season=["Winter"], occasion=["Celebration"], proteins=["Chicken","Vegetarian"],
   complexity="Heavy", kettles=2, accessories=["Stone","Deflector"], leadHours=48,
   activeMin=180, totalMin=300, wood=[], cost="$$", heat=3, coldOK=True,
   diet=["No pork","No shellfish","Vegetarian options"], special=["Kasoori methi","Kashmiri chilli","Mochiko-free"],
   technique=["Stone","Deflector","Skewers","Dutch oven","Flatbread"]),
 "ch34": dict(slug="jerk", region="Jamaica", continent="Caribbean",
   season=["Summer"], occasion=["Cookout","Crowd"], proteins=["Pork","Chicken"],
   complexity="All day", kettles=2, accessories=["Deflector"], leadHours=24,
   activeMin=120, totalMin=480, wood=["Pimento","Oak","Cherry"], cost="$$", heat=5,
   coldOK=False, diet=["No shellfish","Dairy-free-adaptable"], special=["Pimento wood","Scotch bonnet"],
   technique=["Deflector","Direct","Dutch oven","Frying"]),
 "ch35": dict(slug="alsatian", region="France · Alsace", continent="Europe",
   season=["Winter"], occasion=["Holiday","Dinner party"], proteins=["Poultry","Pork"],
   complexity="Moderate", kettles=2, accessories=["Rotisserie","Stone"], leadHours=24,
   activeMin=120, totalMin=240, wood=["Apple","Cherry"], cost="$$$", heat=1, coldOK=True,
   diet=["No shellfish"], special=["Fromage blanc"],
   technique=["Rotisserie","Stone","Dutch oven","Baking"]),
 "ch36": dict(slug="bun-cha", region="Vietnam", continent="Asia",
   season=["Summer"], occasion=["Casual"], proteins=["Pork"],
   complexity="Light", kettles=1, accessories=[], leadHours=12, activeMin=45,
   totalMin=60, wood=[], cost="$", heat=2, coldOK=False,
   diet=["Dairy-free","No shellfish-adaptable"], special=["Banana leaves"],
   technique=["Direct"]),

 "ch37": dict(slug="clambake", region="United States · New England", continent="North America",
   season=["Summer"], occasion=["Coastal","Crowd"], proteins=["Shellfish","Pork"],
   complexity="Heavy", kettles=2, accessories=["Deflector"], leadHours=24,
   activeMin=150, totalMin=240, wood=["Oak"], cost="$$$$", heat=1, coldOK=False,
   diet=["Pescatarian-adaptable"], special=["Rockweed"],
   technique=["Steaming","Deflector","Baking","Direct"]),
 "ch38": dict(slug="santa-maria", region="United States · California", continent="North America",
   season=["Spring","Summer"], occasion=["Ranch party","Dinner party"], proteins=["Beef"],
   complexity="Moderate", kettles=2, accessories=["Deflector"], leadHours=24,
   activeMin=100, totalMin=240, wood=["Red oak"], cost="$$$", heat=1, coldOK=False,
   diet=["No pork-adaptable","No shellfish"], special=["Pinquito beans","Red oak"],
   technique=["Two-zone","Deflector","Dutch oven","Baking"]),
 "ch39": dict(slug="new-orleans", region="United States · Louisiana", continent="North America",
   season=["Winter"], occasion=["Mardi Gras","Dinner party"], proteins=["Shellfish","Chicken","Pork"],
   complexity="Moderate", kettles=2, accessories=["Deflector"], leadHours=24,
   activeMin=110, totalMin=180, wood=["Pecan"], cost="$$$", heat=3, coldOK=True,
   diet=[], special=["Creole mustard","Chicory coffee"],
   technique=["Direct","Deflector","Dutch oven","Cast iron"]),
 "ch40": dict(slug="pacific-northwest", region="United States · Pacific NW", continent="North America",
   season=["Fall"], occasion=["Dinner party"], proteins=["Fish","Shellfish"],
   complexity="Light", kettles=1, accessories=["Stone"], leadHours=6, activeMin=70,
   totalMin=120, wood=["Alder","Cedar planks"], cost="$$$", heat=1, coldOK=True,
   diet=["Pescatarian","No pork"], special=["Cedar planks","Marionberries"],
   technique=["Planking","Two-zone","Stone","Baking"]),
 "ch41": dict(slug="wisconsin", region="United States · Midwest", continent="North America",
   season=["Fall","Winter"], occasion=["Tailgate","Crowd"], proteins=["Pork","Beef"],
   complexity="Moderate", kettles=2, accessories=["Deflector","Plancha"], leadHours=12,
   activeMin=110, totalMin=180, wood=["Apple","Maple"], cost="$$", heat=1, coldOK=True,
   diet=["No shellfish"], special=["Fresh cheese curds"],
   technique=["Two-zone","Holding bath","Plancha","Baking"]),
 "ch42": dict(slug="luau", region="Hawaii", continent="Pacific",
   season=["Summer"], occasion=["Graduation","Birthday","Crowd"], proteins=["Pork","Chicken","Fish"],
   complexity="All day", kettles=2, accessories=["Rotisserie","Deflector"], leadHours=24,
   activeMin=150, totalMin=540, wood=["Kiawe","Mesquite"], cost="$$$", heat=1, coldOK=False,
   diet=[], special=["Mochiko","Banana leaves","Kiawe"],
   technique=["Deflector","Rotisserie","Baking","Direct"]),

 "ch43": dict(slug="duck", region="China", continent="Asia",
   season=["Winter"], occasion=["Lunar New Year","Dinner party"], proteins=["Duck"],
   complexity="Moderate", kettles=2, accessories=["Rotisserie","Stone"], leadHours=48,
   activeMin=120, totalMin=240, wood=["Apple","Pear"], cost="$$$", heat=2, coldOK=True,
   diet=["No pork-adaptable","No shellfish"], special=["Maltose","Chinkiang vinegar"],
   technique=["Rotisserie","Stone","Flatbread","Baking"]),
 "ch44": dict(slug="thanksgiving", region="United States", continent="North America",
   season=["Fall"], occasion=["Thanksgiving","Holiday","Crowd"], proteins=["Turkey","Pork"],
   complexity="Moderate", kettles=2, accessories=["Deflector","Stone"], leadHours=48,
   activeMin=130, totalMin=270, wood=["Apple","Cherry"], cost="$$", heat=1, coldOK=True,
   diet=["No shellfish"], special=[],
   technique=["Deflector","Spatchcock","Dutch oven","Baking","Embers"]),
 "ch45": dict(slug="owensboro", region="United States · Kentucky", continent="North America",
   season=["Summer","Fall"], occasion=["Church picnic","Crowd"], proteins=["Mutton","Chicken"],
   complexity="All day", kettles=2, accessories=["Deflector","Stone"], leadHours=24,
   activeMin=140, totalMin=660, wood=["Hickory"], cost="$$", heat=2, coldOK=True,
   diet=["No pork-adaptable","No shellfish"], special=["Mutton","Ale-8-One"],
   technique=["Snake","Deflector","Dutch oven","Baking","Direct"]),
 "ch46": dict(slug="nordic", region="Scandinavia", continent="Europe",
   season=["Winter"], occasion=["Dinner party"], proteins=["Venison","Fish"],
   complexity="Moderate", kettles=2, accessories=["Deflector","Stone"], leadHours=48,
   activeMin=110, totalMin=210, wood=["Birch","Oak","Juniper"], cost="$$$$", heat=1,
   coldOK=True, diet=["No pork","No shellfish"], special=["Lingonberry","Juniper","Aquavit"],
   technique=["Two-zone","Deflector","Stone","Baking","Curing"]),
 "ch47": dict(slug="calcotada", region="Spain · Catalonia", continent="Europe",
   season=["Spring"], occasion=["Festival","Crowd"], proteins=["Rabbit","Quail","Pork"],
   complexity="Light", kettles=2, accessories=["Stone"], leadHours=24, activeMin=90,
   totalMin=150, wood=["Vine cuttings","Oak"], cost="$$", heat=1, coldOK=False,
   diet=["No shellfish"], special=["Calçots","Ñora peppers","Tiger nuts"],
   technique=["Embers","Direct","Stone"]),
 "ch48": dict(slug="lechon", region="Cuba", continent="Caribbean",
   season=["Winter"], occasion=["Christmas Eve","Holiday","Crowd"], proteins=["Pork"],
   complexity="All day", kettles=2, accessories=["Rotisserie","Stone"], leadHours=24,
   activeMin=140, totalMin=360, wood=["Guava","Oak","Pecan"], cost="$$", heat=1,
   coldOK=True, diet=["Dairy-free-adaptable","No shellfish"], special=["Sour orange","Guava paste"],
   technique=["Rotisserie","Frying","Dutch oven","Stone","Baking"]),
 "ch63": dict(slug="southern-brunch", region="United States \u00b7 South", continent="North America",
   season=["Fall","Winter"], occasion=["Brunch","Leftovers"], proteins=["Beef","Pork","Eggs"],
   complexity="Moderate", kettles=2, accessories=["Deflector"], leadHours=12,
   activeMin=90, totalMin=150, wood=["Hickory"], cost="$$", heat=2, coldOK=True,
   diet=["No shellfish"], special=["Stone-ground grits","Country ham"],
   technique=["Deflector","Cast iron","Baking"]),
 "ch64": dict(slug="almuerzo", region="Mexico", continent="North America",
   season=["Summer","Spring"], occasion=["Brunch","Casual"], proteins=["Eggs","Pork"],
   complexity="Moderate", kettles=2, accessories=[], leadHours=12,
   activeMin=90, totalMin=150, wood=[], cost="$", heat=3, coldOK=False,
   diet=["No shellfish","Vegetarian options","Gluten-free-adaptable"],
   special=["Masa harina","Piloncillo","Tortilla press"],
   technique=["Comal","Cast iron","Direct","Frying","Embers"]),
 "ch62": dict(slug="deli", region="United States \u00b7 New York", continent="North America",
   season=["Winter","Fall"], occasion=["Crowd","Project"], proteins=["Beef","Chicken"],
   complexity="All day", kettles=2, accessories=["Deflector","Stone"], leadHours=192,
   activeMin=160, totalMin=660, wood=["Oak","Cherry"], cost="$$", heat=1, coldOK=True,
   diet=["No pork","No shellfish"], special=["Pink curing salt #1","Matzo meal","Rye flour"],
   technique=["Curing","Snake","Steaming","Stone","Frying","Baking"]),
 "ch59": dict(slug="gua-bao", region="Taiwan", continent="Asia",
   season=["Spring","Fall"], occasion=["Casual"], proteins=["Pork","Chicken"],
   complexity="Moderate", kettles=2, accessories=["Deflector"], leadHours=48,
   activeMin=110, totalMin=240, wood=["Oak"], cost="$$", heat=2, coldOK=True,
   diet=["No shellfish","Dairy-free-adaptable"], special=["Sweet potato starch","Bao flour","L\u00e1 lot-free"],
   technique=["Deflector","Steaming","Frying","Direct"]),
 "ch60": dict(slug="banh-mi", region="Vietnam", continent="Asia",
   season=["Summer"], occasion=["Casual","Lunch"], proteins=["Pork","Shellfish"],
   complexity="Moderate", kettles=1, accessories=["Stone"], leadHours=48,
   activeMin=110, totalMin=240, wood=[], cost="$", heat=2, coldOK=False,
   diet=["Dairy-free-adaptable"], special=["L\u00e1 l\u1ed1t leaves","Rice flour","Maggi seasoning"],
   technique=["Stone","Baking","Direct","Deflector"]),
 "ch61": dict(slug="kahvalti", region="Turkey", continent="Europe",
   season=["Spring","Summer"], occasion=["Brunch","Long morning"], proteins=["Sausage","Eggs"],
   complexity="Light", kettles=2, accessories=["Stone"], leadHours=12,
   activeMin=75, totalMin=150, wood=[], cost="$$", heat=2, coldOK=True,
   diet=["No shellfish","Vegetarian options"], special=["Pekmez","Kaymak","Sucuk","Aleppo pepper"],
   technique=["Stone","Cast iron","Embers","Baking"]),
 "ch57": dict(slug="carolina", region="United States \u00b7 Carolinas", continent="North America",
   season=["Summer","Fall"], occasion=["Crowd","Pig picking"], proteins=["Pork"],
   complexity="All day", kettles=2, accessories=["Deflector"], leadHours=48,
   activeMin=140, totalMin=780, wood=["Hickory","Oak"], cost="$", heat=3, coldOK=True,
   diet=["No shellfish"], special=["Green peanuts","Cheerwine"],
   technique=["Snake","Deflector","Dutch oven","Frying"]),
 "ch58": dict(slug="philly", region="United States \u00b7 Philadelphia", continent="North America",
   season=["Fall"], occasion=["Casual"], proteins=["Pork"],
   complexity="Moderate", kettles=2, accessories=["Rotisserie","Stone"], leadHours=24,
   activeMin=130, totalMin=300, wood=["Oak"], cost="$$", heat=3, coldOK=True,
   diet=["No shellfish"], special=["Long hots","Food-grade lye","Birch beer"],
   technique=["Rotisserie","Stone","Baking","Direct"]),
 "ch54": dict(slug="bistro", region="France · Paris", continent="Europe",
   season=["Winter"], occasion=["Dinner party"], proteins=["Beef"],
   complexity="Heavy", kettles=2, accessories=["Deflector","Stone"], leadHours=48,
   activeMin=150, totalMin=270, wood=["Oak"], cost="$$$$", heat=1, coldOK=True,
   diet=["No shellfish"], special=["Demi-glace","Gruy\u00e8re"],
   technique=["Two-zone","Stone","Deflector","Frying","Baking"]),
 "ch55": dict(slug="grand-aioli", region="France · Provence", continent="Europe",
   season=["Summer"], occasion=["Long lunch","Crowd"], proteins=["Fish"],
   complexity="Light", kettles=1, accessories=[], leadHours=48,
   activeMin=75, totalMin=120, wood=["Vine cuttings","Olive"], cost="$$", heat=1,
   coldOK=False, diet=["Pescatarian","No pork","Dairy-free-adaptable"],
   special=["Salt cod","Lavender honey"], technique=["Embers","Direct"]),
}

PART_OF = {"ch25":"Around the Fire","ch26":"Around the Fire","ch27":"Around the Fire",
 "ch28":"Around the Fire","ch29":"Around the Fire","ch30":"Around the Fire",
 "ch31":"Spit, Stone & Deflector","ch32":"Spit, Stone & Deflector","ch33":"Spit, Stone & Deflector",
 "ch34":"Spit, Stone & Deflector","ch35":"Spit, Stone & Deflector","ch36":"Spit, Stone & Deflector",
 "ch37":"The American Table","ch38":"The American Table","ch39":"The American Table",
 "ch40":"The American Table","ch41":"The American Table","ch42":"The American Table",
 "ch43":"Beasts and Birds","ch44":"Beasts and Birds","ch45":"Beasts and Birds",
 "ch46":"Beasts and Birds","ch47":"Beasts and Birds","ch48":"Beasts and Birds",
 "ch54":"Steak & Bistro","ch55":"Steak & Bistro",
 "ch57":"Sandwiches","ch58":"Sandwiches","ch59":"Sandwiches","ch60":"Sandwiches","ch62":"Sandwiches",
 "ch61":"Brunch","ch63":"Brunch","ch64":"Brunch"}

COURSE_WORDS = [
 ("Drink",  ["drink", "drinks"]),
 ("Sauce",  ["sauce", "marinade", "rub"]),
 ("Dessert",["dessert"]),
 ("Starter",["appetizer", "appetizers"]),
 ("Side",   ["side", "sides", "bread", "centrepiece", "centre of the meal"]),
 ("Main",   ["main"]),
]


def txt(node):
    return re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()


def classify(meta_line):
    low = (meta_line or "").lower()
    for label, words in COURSE_WORDS:
        for w in words:
            if re.search(r"\b" + w + r"\b", low):
                return label
    return "Other"


def parse_recipe(div):
    title_el = div.select_one(".rtitle")
    native = title_el.select_one(".native")
    native_txt = txt(native) if native else ""
    if native:
        native.extract()
    title = txt(title_el)
    meta_line = txt(div.select_one(".meta")) if div.select_one(".meta") else ""
    head = txt(div.select_one(".headnote")) if div.select_one(".headnote") else ""

    ingredients = []
    box = div.select_one(".ingredients")
    if box:
        for li in box.select("li, .sub"):
            if "sub" in (li.get("class") or []):
                ingredients.append({"type": "sub", "text": txt(li)})
            else:
                ingredients.append({"type": "item", "text": txt(li)})

    method = [txt(li) for li in div.select(".method > li")]

    notes = []
    for cls, label in (("note", "Note"), ("warn", "Watch out"), ("ahead", "Make ahead")):
        for n in div.select("." + cls):
            lbl = n.select_one(".lbl")
            heading = txt(lbl) if lbl else label
            if lbl:
                lbl.extract()
            notes.append({"kind": cls, "label": heading, "text": txt(n)})

    plating = None
    pl = div.select_one(".plate")
    if pl:
        lbl = pl.select_one(".lbl")
        style = "board"
        if lbl:
            raw = txt(lbl)
            style = raw.split("\u00b7")[-1].strip().lower() if "\u00b7" in raw else raw.strip().lower()
            lbl.extract()
        plating = {"style": style, "text": txt(pl)}

    return {
        "plating": plating,
        "title": title, "native": native_txt, "meta": meta_line,
        "course": classify(meta_line), "headnote": head,
        "ingredients": ingredients, "method": method, "notes": notes,
    }


def parse_menu_chapter(sec):
    cid = sec.get("id")
    out = {"id": cid, "title": txt(sec.select_one("h1")),
           "lead": txt(sec.select_one(".lead")) if sec.select_one(".lead") else "",
           "part": PART_OF.get(cid, ""), "blocks": {}, "recipes": []}

    # walk h2 sections for menu / grill plan / timeline / shopping
    for h2 in sec.find_all("h2"):
        key = txt(h2).lower()
        chunk = []
        for sib in h2.next_siblings:
            if getattr(sib, "name", None) in ("h2", None):
                if getattr(sib, "name", None) == "h2":
                    break
                continue
            if getattr(sib, "name", None) == "div" and "recipe" in (sib.get("class") or []):
                break
            chunk.append(sib)
        html = "".join(str(c) for c in chunk)
        if "menu" in key:
            out["blocks"]["menu"] = html
        elif "grill" in key:
            out["blocks"]["grill"] = html
        elif "countdown" in key or "timeline" in key:
            out["blocks"]["timeline"] = html
        elif "shopping" in key:
            out["blocks"]["shopping"] = html

    for div in sec.select(".recipe"):
        out["recipes"].append(parse_recipe(div))

    out.update(META.get(cid, {}))
    cap = CAPACITY.get(cid, {})
    out["maxServes"] = cap.get("maxServes", 12)
    out["fuel"] = cap.get("fuel", 4)
    out["capNotes"] = cap.get("notes", [])
    # attach each constraint to the recipe whose title contains its match string
    items = []
    for it in cap.get("items", []):
        target = next((r["title"] for r in out["recipes"] if it["match"].lower() in r["title"].lower()), None)
        rec = dict(it); rec["recipe"] = target or ""
        rec["label"] = target or it.get("label") or it["match"]
        items.append(rec)
    out["cap"] = items
    out["impress"] = cid in IMPRESS_MENUS
    out["impressWhy"] = IMPRESS_MENUS.get(cid, "")
    imp = IMPRESS_RECIPES.get(cid, [])
    plate = PLATING.get(cid, {})
    for r in out["recipes"]:
        r["cap"] = [i for i in items if i["recipe"] == r["title"]]
        hit = next((v for k, v in plate.items() if k.lower() in r["title"].lower()), None)
        r["plating"] = hit or r.get("plating")
        r["impress"] = any(k.lower() in r["title"].lower() for k in imp)
    return out


LIB_CHAPTERS = ("ch19", "ch20", "ch21", "ch22", "ch23", "ch24", "ch51", "ch52", "ch53", "ch56")


def parse_library():
    lib = []
    secs = []
    for fn in LIB_FILES:
        soup = BeautifulSoup((BOOK / fn).read_text(encoding="utf-8"), "html.parser")
        secs.extend(soup.select("section.chapter"))
    for sec in secs:
        cid = sec.get("id")
        if cid not in LIB_CHAPTERS:
            continue
        chapter = txt(sec.select_one("h1"))
        for div in sec.select(".recipe"):
            r = parse_recipe(div)
            r["chapter"] = chapter
            r["chapterId"] = cid
            r["course"] = "Library"
            r["plating"] = next((v for k, v in _PL.items() if k.lower() in r["title"].lower()), None) or r.get("plating")
            lib.append(r)
    return lib


def parse_showpieces():
    soup = BeautifulSoup((BOOK / SHOW_FILE).read_text(encoding="utf-8"), "html.parser")
    out = []
    for sec in soup.select("section.chapter"):
        for div in sec.select(".recipe"):
            r = parse_recipe(div)
            r["chapter"] = "Cook to Impress"
            r["chapterId"] = sec.get("id")
            r["course"] = "Showpiece"
            r["impress"] = True
            pl = div.select_one(".plate")
            if pl:
                lbl = pl.select_one(".lbl")
                style = txt(lbl).split("\u00b7")[-1].strip().lower() if lbl else "board"
                if lbl:
                    lbl.extract()
                r["plating"] = {"style": style, "text": txt(pl)}
            else:
                r["plating"] = None
            out.append(r)
    return out


def main():
    menus = []
    for fn in MENU_FILES:
        soup = BeautifulSoup((BOOK / fn).read_text(encoding="utf-8"), "html.parser")
        for sec in soup.select("section.chapter"):
            if sec.get("id") in META:
                menus.append(parse_menu_chapter(sec))
    data = {"menus": menus, "library": parse_library(),
            "showpieces": parse_showpieces(), "kettle": KETTLE}
    (HERE / "data.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    nrec = sum(len(m["recipes"]) for m in menus)
    print(f"menus: {len(menus)}  menu recipes: {nrec}  library recipes: {len(data['library'])}")
    print("showpieces:", len(data["showpieces"]))
    print("total recipes:", nrec + len(data["library"]) + len(data["showpieces"]))
    missing = [m["id"] for m in menus if not m["blocks"].get("shopping")]
    if missing:
        print("! missing shopping block:", missing)


if __name__ == "__main__":
    main()
