#!/usr/bin/env python3
"""Turn JSON payloads in content/ into book markup the existing parsers understand.

A payload is one JSON file describing one addition: a whole menu chapter, a recipe
for an existing chapter, a library entry, or a patch to an existing menu's facets.
Nothing here writes to book/ — the HTML is rendered in memory and handed to
extract.py's parse_recipe / parse_menu_chapter, so there is still exactly one
parser and one data model.

    content/*.json -> render_chapter() -> BeautifulSoup -> parse_menu_chapter()

Prose fields are plain text with three markers and no HTML:

    **bold**            -> <strong>bold</strong>
    *italic*            -> <em>italic</em>
    ((Chapter 22))      -> <span class="drop">(Chapter 22)</span>

Validation runs in two passes. check_structure() needs nothing but the payload and
runs at load time, so a malformed file cannot reach the table merge. check() runs
after the book is parsed and sees the assembled data, so it can tell whether a
capacity match actually hit a recipe and whether a course survived classify().
"""

import difflib, html, json, pathlib, re, unicodedata
from bs4 import BeautifulSoup

HERE = pathlib.Path(__file__).resolve().parent
CONTENT = HERE.parent / "content"

KINDS = ("menu", "recipe", "library", "patch")

# ---------------------------------------------------------------- vocabulary
# Closed because app.js hardcodes the filter option list; a value outside these
# renders fine on the page but can never be filtered for.
SEASONS = ("Spring", "Summer", "Fall", "Winter")
COMPLEXITY = ("Light", "Moderate", "Heavy", "All day")
COST = ("$", "$$", "$$$", "$$$$")
KETTLES = (1, 2)
HEAT = (1, 2, 3, 5)  # 4 is unrepresentable: app.js maps it to a blank label
COURSES = ("Starter", "Main", "Side", "Sauce", "Dessert", "Drink")
NOTE_KINDS = ("note", "warn", "ahead")
ZONES = ("direct", "indirect", "full")

# The word classify() must find in the assembled .meta line for each course.
COURSE_WORD = {"Starter": "Appetizer", "Main": "Main", "Side": "Side",
               "Sauce": "Sauce", "Dessert": "Dessert", "Drink": "Drink"}

# Every facet key a menu must carry. A missing one prints "undefined" in the app.
FACET_KEYS = ("slug", "region", "continent", "season", "occasion", "proteins",
              "complexity", "kettles", "accessories", "leadHours", "activeMin",
              "totalMin", "wood", "cost", "heat", "coldOK", "diet", "special",
              "technique")
LIST_FACETS = ("season", "occasion", "proteins", "accessories", "wood", "diet",
               "special", "technique")
SCALAR_FACETS = ("region", "continent", "complexity", "kettles", "leadHours",
                 "activeMin", "totalMin", "cost", "heat", "coldOK", "slug")
# Facets whose values become filter chips, so a typo becomes a stray one-item chip.
GATED_FACETS = ("region", "continent", "occasion", "proteins", "accessories",
                "wood", "diet", "special", "technique")

# Per capacity type, the numeric fields capacity.py's model requires.
CAP_FIELDS = {"dutch": ("qt8",), "skillet": ("loads8",), "grate": ("sqin8", "zone"),
              "spit": ("lb8", "len8"), "stone": ("units8", "minEach"),
              "vortex": ("pieces8",), "steamer": ("qt8",), "fry": ("qt8",),
              "pan": ("name", "count8", "perUnit")}

# Kit a method can mention that ought to have a matching capacity item.
KIT_HINTS = ((r"dutch oven", "dutch"), (r"pizza stone|\bstone\b", "stone"),
             (r"rotisserie|\bspit\b", "spit"), (r"frying oil|deep-fry|deep fry", "fry"),
             (r"cast[- ]iron|skillet", "skillet"))


# Known keys per object, so a typo like "headnotes" is caught instead of dropped.
PAYLOAD_KEYS = {
    "menu": {"kind", "chapterId", "afterChapter", "title", "lead", "part", "partLabel",
             "intro", "facets", "blocks", "capacity", "impress", "recipes", "newFacetValues"},
    "recipe": {"kind", "menuId", "placement", "recipe", "menuLine", "shoppingAdds",
               "capacity", "facetAdds", "timelineAdds", "impress", "newFacetValues"},
    "library": {"kind", "chapterId", "placement", "recipe", "newFacetValues"},
    "patch": {"kind", "target", "set", "add", "remove", "newFacetValues"},
}
RECIPE_KEYS = {"title", "native", "course", "serves", "time", "metaExtra", "headnote",
               "ingredients", "method", "notes", "plating", "context", "yield"}


def _unknown(obj, allowed, where, out, f):
    for key in obj:
        if key == "_file" or key in allowed:
            continue
        close = difflib.get_close_matches(key, sorted(allowed), n=1, cutoff=0.7)
        hint = f"; did you mean {close[0]!r}?" if close else ""
        out.append(f"{f}: {where} has unknown key {key!r}{hint}")


class ContentError(Exception):
    """Raised when a payload is malformed enough that merging it would crash."""


# ---------------------------------------------------------------- inline markup
_MARKER = re.compile(r"\*\*(.+?)\*\*|\*(.+?)\*|\(\((.+?)\)\)")


def md(text):
    """Escape a prose string and expand the three inline markers."""
    s = "" if text is None else str(text)
    out, pos = [], 0
    for m in _MARKER.finditer(s):
        out.append(html.escape(s[pos:m.start()], quote=False))
        if m.group(1) is not None:
            out.append("<strong>" + html.escape(m.group(1), quote=False) + "</strong>")
        elif m.group(2) is not None:
            out.append("<em>" + html.escape(m.group(2), quote=False) + "</em>")
        else:
            out.append('<span class="drop">(' + html.escape(m.group(3), quote=False) + ')</span>')
        pos = m.end()
    out.append(html.escape(s[pos:], quote=False))
    return "".join(out)


def plain(text):
    """Escape with no marker expansion, for titles and table cells."""
    return html.escape("" if text is None else str(text), quote=False)


def norm(value):
    """Fold a facet value for duplicate detection: 'Cast Iron' == 'Cast iron'."""
    s = unicodedata.normalize("NFKD", str(value))
    s = s.encode("ascii", "ignore").decode("ascii").casefold()
    return re.sub(r"[^a-z0-9]+", "", s)


# ---------------------------------------------------------------- loading
def load(directory=None):
    """Read and structurally validate every content/*.json. Raises ContentError."""
    root = pathlib.Path(directory) if directory else CONTENT
    if not root.is_dir():
        return []
    payloads, errors = [], []
    for path in sorted(root.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{path.name}: not valid JSON ({e})")
            continue
        if not isinstance(data, dict):
            errors.append(f"{path.name}: top level must be a JSON object")
            continue
        data["_file"] = path.name
        payloads.append(data)
    errors.extend(_schema_errors(payloads))
    errors.extend(check_structure(payloads))
    if errors:
        raise ContentError("\n".join("  ! " + e for e in errors))
    return payloads


SCHEMA = HERE / "schema" / "content.schema.json"


def _schema_errors(payloads):
    """A first pass against the JSON Schema, when jsonschema is installed.

    Each payload is validated against its own $defs branch rather than the
    top-level oneOf, because a oneOf failure reports only "is not valid under
    any of the given schemas" and buries the real reason in e.context.

    The schema is primarily a document to hand to a model, so this is a bonus
    rather than the gate: check_structure() below carries the rules the schema
    cannot express, and runs either way.
    """
    try:
        import jsonschema
    except ImportError:
        return []
    if not SCHEMA.exists():
        return []
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    branch = {"menu": "MenuPayload", "recipe": "RecipePayload",
              "library": "LibraryPayload", "patch": "PatchPayload"}
    out = []
    for p in payloads:
        name = branch.get(p.get("kind"))
        if not name:
            continue  # check_structure reports an unknown kind
        validator = jsonschema.Draft202012Validator(
            {"$ref": "#/$defs/" + name, "$defs": schema["$defs"]})
        body = {k: v for k, v in p.items() if k != "_file"}
        for e in sorted(validator.iter_errors(body), key=lambda e: list(e.path))[:6]:
            where = ".".join(str(x) for x in e.path) or "payload"
            out.append(f"{p['_file']}: {where}: {e.message}")
    return out


# ---------------------------------------------------------------- structure pass
def _walk_strings(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "_file":
                continue
            yield from _walk_strings(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk_strings(v, f"{path}[{i}]")
    elif isinstance(node, str):
        yield path, node


def _prose_errors(payload):
    """Reject raw HTML, literal \\uXXXX escapes and unbalanced inline markers."""
    out = []
    f = payload.get("_file", "?")
    for path, s in _walk_strings(payload):
        if "<" in s or ">" in s:
            out.append(f"{f}: {path} contains a raw angle bracket; prose is plain text "
                       f"with **bold**, *italic* and ((Chapter NN)) only")
        if re.search(r"\\u[0-9a-fA-F]{4}", s):
            out.append(f"{f}: {path} contains a literal \\uXXXX escape; write the character itself")
        if re.search(r"&[a-zA-Z]+;|&#\d+;", s):
            out.append(f"{f}: {path} contains an HTML entity; write the character itself")
        stripped = _MARKER.sub("", s)
        if "*" in stripped:
            out.append(f"{f}: {path} has an unbalanced * or ** marker")
        if "((" in stripped or "))" in stripped:
            out.append(f"{f}: {path} has an unbalanced (( )) cross-reference marker")
    return out


def _need(obj, key, kind, where, out, f, types=None):
    if key not in obj:
        out.append(f"{f}: {where} is missing required key '{key}' ({kind})")
        return False
    if types and not isinstance(obj[key], types):
        out.append(f"{f}: {where}.{key} must be {kind}, got {type(obj[key]).__name__}")
        return False
    return True


def _check_recipe(r, where, out, f, need_course=True):
    if not isinstance(r, dict):
        out.append(f"{f}: {where} must be an object")
        return
    _unknown(r, RECIPE_KEYS, where, out, f)
    _need(r, "title", "a string", where, out, f, str)
    _need(r, "ingredients", "a list", where, out, f, list)
    _need(r, "method", "a list", where, out, f, list)
    if need_course:
        c = r.get("course")
        if c not in COURSES:
            out.append(f"{f}: {where}.course is {c!r}; must be one of {', '.join(COURSES)}")
        _need(r, "serves", "a string like 'Serves 8'", where, out, f, str)
    else:
        _need(r, "context", "a string naming where it is used", where, out, f, str)
        _need(r, "yield", "a string like 'Makes 2 cups'", where, out, f, str)
    if len(r.get("ingredients") or []) < 1:
        out.append(f"{f}: {where}.ingredients is empty")
    if len(r.get("method") or []) < 1:
        out.append(f"{f}: {where}.method is empty")
    for i, ing in enumerate(r.get("ingredients") or []):
        if isinstance(ing, dict) and "sub" not in ing:
            out.append(f"{f}: {where}.ingredients[{i}] object must be {{\"sub\": \"Heading\"}}")
        elif not isinstance(ing, (str, dict)):
            out.append(f"{f}: {where}.ingredients[{i}] must be a string or {{\"sub\": ...}}")
    for i, n in enumerate(r.get("notes") or []):
        if not isinstance(n, dict) or n.get("kind") not in NOTE_KINDS:
            out.append(f"{f}: {where}.notes[{i}].kind must be one of {', '.join(NOTE_KINDS)}")
        elif not n.get("label") or not n.get("text"):
            out.append(f"{f}: {where}.notes[{i}] needs both a label and text")
    # The book's zero-gap rule: every recipe carries a plating note.
    pl = r.get("plating")
    if not isinstance(pl, dict) or not str(pl.get("text") or "").strip():
        out.append(f"{f}: {where} has no plating note; every recipe needs "
                   f"{{\"style\": \"board\", \"text\": \"...\"}}")
    elif not str(pl.get("style") or "").strip():
        out.append(f"{f}: {where}.plating.style is empty")
    elif pl["style"] != pl["style"].lower():
        out.append(f"{f}: {where}.plating.style must be lowercase, got {pl['style']!r}")


def _check_capacity(cap, where, out, f, require_totals):
    if not isinstance(cap, dict):
        out.append(f"{f}: {where} must be an object")
        return
    if require_totals:
        for key in ("maxServes", "fuel"):
            _need(cap, key, "a number", where, out, f, (int, float))
        if not (cap.get("notes") or []):
            out.append(f"{f}: {where}.notes is empty; say what actually limits this menu")
        if not (cap.get("items") or []):
            out.append(f"{f}: {where}.items is empty; a menu with no capacity items "
                       f"silently reports that it scales to 16")
    for i, it in enumerate(cap.get("items") or []):
        at = f"{where}.items[{i}]"
        if not isinstance(it, dict):
            out.append(f"{f}: {at} must be an object")
            continue
        if not it.get("match"):
            out.append(f"{f}: {at} is missing 'match' (a substring of a recipe title)")
        t = it.get("type")
        if t not in CAP_FIELDS:
            out.append(f"{f}: {at}.type is {t!r}; must be one of {', '.join(sorted(CAP_FIELDS))}")
            continue
        for field in CAP_FIELDS[t]:
            if field not in it:
                out.append(f"{f}: {at} is type '{t}' so it needs '{field}'")
        if t == "grate" and it.get("zone") not in ZONES:
            out.append(f"{f}: {at}.zone must be one of {', '.join(ZONES)}")


def check_structure(payloads):
    """Errors that need no book context. Run before anything is merged."""
    out = []
    seen_ids = {}
    for p in payloads:
        f = p.get("_file", "?")
        kind = p.get("kind")
        if kind not in KINDS:
            out.append(f"{f}: kind is {kind!r}; must be one of {', '.join(KINDS)}")
            continue
        _unknown(p, PAYLOAD_KEYS[kind], f"a kind:{kind!r} payload", out, f)
        out.extend(_prose_errors(p))
        if "newFacetValues" not in p and kind != "library":
            out.append(f"{f}: missing 'newFacetValues'; use {{}} if this payload only "
                       f"reuses facet values the book already has")

        if kind == "menu":
            for key in ("chapterId", "afterChapter", "title", "lead", "part", "partLabel"):
                _need(p, key, "a string", "payload", out, f, str)
            cid = p.get("chapterId", "")
            if cid and not re.fullmatch(r"ch\d{2,3}", cid):
                out.append(f"{f}: chapterId {cid!r} must look like 'ch65'")
            if cid in seen_ids:
                out.append(f"{f}: chapterId {cid!r} is already used by {seen_ids[cid]}")
            seen_ids[cid] = f
            facets = p.get("facets")
            if not isinstance(facets, dict):
                out.append(f"{f}: 'facets' must be an object with all {len(FACET_KEYS)} keys")
            else:
                out.extend(_check_facets(facets, "facets", f))
            blocks = p.get("blocks")
            if not isinstance(blocks, dict):
                out.append(f"{f}: 'blocks' must be an object")
            else:
                for key in ("menu", "grill", "timeline", "shopping"):
                    if not blocks.get(key):
                        out.append(f"{f}: blocks.{key} is missing or empty")
                if not isinstance(blocks.get("shopping", {}), dict):
                    out.append(f"{f}: blocks.shopping must be an object of category -> [items]")
                for cat, items in (blocks.get("shopping") or {}).items():
                    if not items:
                        out.append(f"{f}: blocks.shopping['{cat}'] is empty")
            _check_capacity(p.get("capacity", {}), "capacity", out, f, require_totals=True)
            recipes = p.get("recipes")
            if not isinstance(recipes, list) or not recipes:
                out.append(f"{f}: 'recipes' must be a non-empty list")
            else:
                titles = {}
                for i, r in enumerate(recipes):
                    _check_recipe(r, f"recipes[{i}]", out, f)
                    t = (r or {}).get("title")
                    if t in titles:
                        out.append(f"{f}: two recipes are both titled {t!r}; titles must be "
                                   f"unique inside a chapter (they key the cart and permalinks)")
                    titles[t] = i

        elif kind == "recipe":
            _need(p, "menuId", "a string", "payload", out, f, str)
            _check_recipe(p.get("recipe", {}), "recipe", out, f)
            for key in ("menuLine", "shoppingAdds", "capacity"):
                if key not in p:
                    out.append(f"{f}: missing '{key}'; pass an empty object if the new dish "
                               f"genuinely adds nothing there")
            _check_capacity(p.get("capacity", {}), "capacity", out, f, require_totals=False)
            for key in p.get("facetAdds", {}) or {}:
                if key in SCALAR_FACETS:
                    out.append(f"{f}: facetAdds.{key} is a scalar facet; changing it is a "
                               f"menu-level judgement, use a 'patch' payload")
                elif key not in LIST_FACETS:
                    out.append(f"{f}: facetAdds.{key} is not a facet key")

        elif kind == "library":
            _need(p, "chapterId", "a string", "payload", out, f, str)
            _check_recipe(p.get("recipe", {}), "recipe", out, f, need_course=False)

        elif kind == "patch":
            _need(p, "target", "a string", "payload", out, f, str)
            if not any(p.get(k) for k in ("set", "add", "remove")):
                out.append(f"{f}: a patch needs at least one of 'set', 'add' or 'remove'")
            for key, val in (p.get("set") or {}).items():
                if key not in FACET_KEYS:
                    out.append(f"{f}: set.{key} is not one of the {len(FACET_KEYS)} facet keys")
                elif key in LIST_FACETS and not isinstance(val, list):
                    out.append(f"{f}: set.{key} is a list facet; pass a list")
                else:
                    out.extend(_check_facets({key: val}, "set", f, partial=True))
            for group in ("add", "remove"):
                for key, val in (p.get(group) or {}).items():
                    if key not in LIST_FACETS:
                        out.append(f"{f}: {group}.{key} must be a list facet "
                                   f"({', '.join(LIST_FACETS)}); use 'set' for scalars")
                    elif not isinstance(val, list):
                        out.append(f"{f}: {group}.{key} must be a list")
    return out


def _check_facets(facets, where, f, partial=False):
    """Type and closed-enum checks on a facets object (or one key of one)."""
    out = []
    if not partial:
        for key in FACET_KEYS:
            if key not in facets:
                out.append(f"{f}: {where}.{key} is missing; all {len(FACET_KEYS)} facet keys "
                           f"are required or the app prints 'undefined'")
    for key in facets:
        if key not in FACET_KEYS:
            out.append(f"{f}: {where}.{key} is not a facet key")
    checks = [("complexity", COMPLEXITY), ("cost", COST), ("kettles", KETTLES), ("heat", HEAT)]
    for key, allowed in checks:
        if key in facets and facets[key] not in allowed:
            extra = (" — app.js renders heat 4 with a blank label, so it is unusable"
                     if key == "heat" and facets[key] == 4 else "")
            out.append(f"{f}: {where}.{key} is {facets[key]!r}; the filter list is hardcoded "
                       f"in app.js so it must be one of {allowed}{extra}")
    if "season" in facets:
        for s in facets["season"] or []:
            if s not in SEASONS:
                out.append(f"{f}: {where}.season has {s!r}; must be one of {', '.join(SEASONS)}")
        if not facets["season"]:
            out.append(f"{f}: {where}.season is empty")
    for key in LIST_FACETS:
        if key in facets and not isinstance(facets[key], list):
            out.append(f"{f}: {where}.{key} must be a list")
    for key in ("leadHours", "activeMin", "totalMin"):
        if key in facets and not isinstance(facets[key], int):
            out.append(f"{f}: {where}.{key} must be a whole number of hours/minutes")
    if "coldOK" in facets and not isinstance(facets["coldOK"], bool):
        out.append(f"{f}: {where}.coldOK must be true or false")
    if isinstance(facets.get("activeMin"), int) and isinstance(facets.get("totalMin"), int):
        if facets["totalMin"] < facets["activeMin"]:
            out.append(f"{f}: {where}.totalMin ({facets['totalMin']}) is less than "
                       f"activeMin ({facets['activeMin']})")
    if "slug" in facets and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", str(facets["slug"])):
        out.append(f"{f}: {where}.slug must be lowercase kebab-case")
    return out


# ---------------------------------------------------------------- rendering
def meta_line(r):
    """Assemble the .meta line. Never authored, so classify() cannot be surprised."""
    parts = [COURSE_WORD[r["course"]], r["serves"]]
    if r.get("time"):
        parts.append(r["time"])
    if r.get("metaExtra"):
        parts.append(r["metaExtra"])
    return " · ".join(str(p) for p in parts)


def library_meta(r):
    return f"{r['context']} · {r['yield']}"


def render_recipe(r, meta):
    """One .recipe div in exactly the markup parse_recipe expects."""
    h = ['<div class="recipe">']
    title = '<div class="rtitle">' + plain(r["title"])
    if r.get("native"):
        title += ' <span class="native">' + plain(r["native"]) + "</span>"
    h.append(title + "</div>")
    h.append('<div class="meta">' + plain(meta) + "</div>")
    if r.get("headnote"):
        h.append('<p class="headnote">' + md(r["headnote"]) + "</p>")

    h.append('<div class="ingredients"><ul>')
    for ing in r["ingredients"]:
        if isinstance(ing, dict):
            h.append('<li class="sub">' + md(ing["sub"]) + "</li>")
        else:
            h.append("<li>" + md(ing) + "</li>")
    h.append("</ul></div>")

    h.append('<ol class="method">')
    for step in r["method"]:
        h.append("<li>" + md(step) + "</li>")
    h.append("</ol>")

    for n in r.get("notes") or []:
        h.append('<div class="' + n["kind"] + '"><span class="lbl">' + plain(n["label"])
                 + "</span><p>" + md(n["text"]) + "</p></div>")

    pl = r["plating"]
    # parse_recipe reads the style back off this label, and build_pdf.py's
    # inject_plating uses the same bare "Keeping" spelling.
    label = "Keeping" if pl["style"] == "keeping" else "To the table · " + pl["style"]
    h.append('<div class="plate"><span class="lbl">' + plain(label) + "</span>"
             + md(pl["text"]) + "</div>")
    h.append("</div>")
    return "\n".join(h)


def render_menu_li(line):
    """One <li> of the 'The menu' list: bolded dish names plus an optional note."""
    dishes = ["<strong>" + md(d) + "</strong>" for d in line["dishes"]]
    if len(dishes) == 1:
        body = dishes[0]
    elif len(dishes) == 2:
        body = dishes[0] + " and " + dishes[1]
    else:
        body = ", ".join(dishes[:-1]) + " and " + dishes[-1]
    if line.get("note"):
        body += " — " + md(line["note"])
    return "<li>" + body + "</li>"


def render_shopping_li(cat, items):
    return ("<li><strong>" + plain(cat) + ":</strong> "
            + " · ".join(md(i) for i in items) + "</li>")


def render_blocks(b):
    """The four h2 sections, always in this order and always before any recipe."""
    h = []
    h.append("<h2>The menu</h2>")
    h.append('<ul class="tight">')
    h.extend(render_menu_li(line) for line in b["menu"])
    h.append("</ul>")

    h.append("<h2>Grill plan &amp; fuel</h2>")
    grill = b["grill"]
    h.append('<p class="flush"><strong>Fuel:</strong> ' + md(grill["fuel"]) + "</p>")
    for para in grill.get("paragraphs") or []:
        lead = "<strong>" + md(para["lead"]) + "</strong> " if para.get("lead") else ""
        h.append("<p>" + lead + md(para["text"]) + "</p>")

    h.append("<h2>Prep countdown</h2>")
    h.append('<table><thead><tr><th style="width:22%">When</th><th>What</th></tr></thead><tbody>')
    for row in b["timeline"]:
        h.append("<tr><td>" + plain(row["when"]) + "</td><td>" + md(row["what"]) + "</td></tr>")
    h.append("</tbody></table>")

    h.append("<h2>Shopping list</h2>")
    h.append('<ul class="tight">')
    h.extend(render_shopping_li(cat, items) for cat, items in b["shopping"].items())
    h.append("</ul>")
    return "\n".join(h)


def render_chapter(p):
    """A whole <section class="chapter"> for a kind:"menu" payload."""
    h = ['<section class="chapter" id="' + plain(p["chapterId"]) + '">']
    h.append('<div class="kicker">' + plain(p["partLabel"]) + " · " + plain(p["part"]) + "</div>")
    h.append("<h1>" + plain(p["title"]) + "</h1>")
    h.append('<p class="lead">' + plain(p["lead"]) + "</p>")
    for i, para in enumerate(p.get("intro") or []):
        h.append('<p class="flush">' + md(para) + "</p>" if i == 0 else "<p>" + md(para) + "</p>")
    h.append(render_blocks(p["blocks"]))
    for r in p["recipes"]:
        h.append(render_recipe(r, meta_line(r)))
    h.append("</section>")
    return "\n".join(h)


def render_payload_recipe(p):
    """The .recipe div for a kind:"recipe" or kind:"library" payload."""
    r = p["recipe"]
    meta = library_meta(r) if p["kind"] == "library" else meta_line(r)
    return render_recipe(r, meta)


# ---------------------------------------------------------------- table merge
def merge_python_tables(payloads, META, PART_OF, CAPACITY, IMPRESS_MENUS, IMPRESS_RECIPES):
    """Fold payload facets into the hand-written tables, in place."""
    for p in payloads:
        kind, f = p["kind"], p["_file"]
        if kind == "menu":
            cid = p["chapterId"]
            if cid in META:
                raise ContentError(f"  ! {f}: chapterId {cid!r} already exists in META")
            META[cid] = dict(p["facets"])
            PART_OF[cid] = p["part"]
            cap = p["capacity"]
            CAPACITY[cid] = dict(maxServes=cap["maxServes"], fuel=cap["fuel"],
                                 items=[dict(i) for i in cap.get("items") or []],
                                 notes=list(cap.get("notes") or []))
            imp = p.get("impress") or {}
            if imp.get("why"):
                IMPRESS_MENUS[cid] = imp["why"]
            if imp.get("recipes"):
                IMPRESS_RECIPES[cid] = list(imp["recipes"])

        elif kind == "recipe":
            cid = p["menuId"]
            entry = CAPACITY.setdefault(cid, dict(maxServes=12, fuel=4, items=[], notes=[]))
            entry.setdefault("items", []).extend(dict(i) for i in (p.get("capacity") or {}).get("items") or [])
            entry.setdefault("notes", []).extend((p.get("capacity") or {}).get("notesAdd") or [])
            meta = META.setdefault(cid, {})
            for key, vals in (p.get("facetAdds") or {}).items():
                have = list(meta.get(key) or [])
                have.extend(v for v in vals if v not in have)
                meta[key] = have
            if p.get("impress"):
                IMPRESS_RECIPES.setdefault(cid, []).append(p["recipe"]["title"])

        elif kind == "patch":
            meta = META.get(p["target"])
            if meta is None:
                raise ContentError(f"  ! {f}: patch target {p['target']!r} is not a menu chapter")
            for key, val in (p.get("set") or {}).items():
                meta[key] = list(val) if isinstance(val, list) else val
            for key, vals in (p.get("add") or {}).items():
                have = list(meta.get(key) or [])
                have.extend(v for v in vals if v not in have)
                meta[key] = have
            for key, vals in (p.get("remove") or {}).items():
                meta[key] = [v for v in (meta.get(key) or []) if v not in vals]


# ---------------------------------------------------------------- soup surgery
def generated_sections(payloads, soup_factory):
    """[(payload, section tag)] for every kind:"menu" payload."""
    out = []
    for p in payloads:
        if p["kind"] == "menu":
            sec = soup_factory(render_chapter(p)).select_one("section.chapter")
            out.append((p, sec))
    return out


def _block_list(sec, word, name="ul"):
    """The first <ul>/<table> under the h2 whose text contains `word`."""
    for h2 in sec.find_all("h2"):
        if word not in h2.get_text(" ", strip=True).lower():
            continue
        for sib in h2.next_siblings:
            tag = getattr(sib, "name", None)
            if tag == "h2":
                break
            if tag == name:
                return sib
    return None


def _recipe_title(div):
    el = div.select_one(".rtitle")
    if not el:
        return ""
    text = " ".join(t for t in el.stripped_strings
                    if not (t and el.select_one(".native")
                            and t == el.select_one(".native").get_text(" ", strip=True)))
    return re.sub(r"\s+", " ", text).strip()


def _place(sec, div, placement, course, classify):
    """Insert `div` among the chapter's existing .recipe blocks."""
    existing = sec.select(".recipe")
    after = (placement or {}).get("after")
    if after:
        for d in existing:
            if after.lower() in _recipe_title(d).lower():
                d.insert_after(div)
                return
    if (placement or {}).get("position") == "end" or not existing or not classify:
        sec.append(div)
        return
    # Default: land in course order, so the printed chapter still reads correctly.
    courses = []
    for d in existing:
        m = d.select_one(".meta")
        courses.append(classify(m.get_text(" ", strip=True) if m else ""))
    order = list(COURSES)
    want = order.index(course) if course in order else len(order) - 1
    for step in range(want, -1, -1):
        target = order[step]
        hits = [d for d, c in zip(existing, courses) if c == target]
        if hits:
            hits[-1].insert_after(div)
            return
    existing[0].insert_before(div)


def splice_into(soup, payloads, classify=None):
    """Apply every recipe/library payload to whatever chapters this soup holds."""
    n = 0
    for p in payloads:
        if p["kind"] not in ("recipe", "library"):
            continue
        cid = p.get("menuId") or p.get("chapterId")
        sec = soup.find("section", id=cid)
        if sec is None:
            continue  # this soup is a different file
        frag = BeautifulSoup(render_payload_recipe(p), "html.parser")
        _place(sec, frag.select_one(".recipe"), p.get("placement"),
               p["recipe"].get("course"), classify)
        n += 1
        if p["kind"] == "library":
            continue

        if p.get("menuLine"):
            ul = _block_list(sec, "menu")
            if ul is not None:
                ul.append(BeautifulSoup(render_menu_li(p["menuLine"]), "html.parser"))
        for cat, items in (p.get("shoppingAdds") or {}).items():
            ul = _block_list(sec, "shopping")
            if ul is None:
                continue
            row = next((li for li in ul.find_all("li") if li.find("strong")
                        and li.find("strong").get_text(strip=True).rstrip(":") == cat), None)
            if row is None:
                ul.append(BeautifulSoup(render_shopping_li(cat, items), "html.parser"))
            else:
                row.append(BeautifulSoup(" · " + " · ".join(md(i) for i in items),
                                         "html.parser"))
        for row in p.get("timelineAdds") or []:
            table = _block_list(sec, "countdown", name="table")
            body = table.find("tbody") if table else None
            if body is None:
                continue
            tr = BeautifulSoup("<tr><td>" + plain(row["when"]) + "</td><td>"
                               + md(row["what"]) + "</td></tr>", "html.parser")
            anchor = None
            for existing in body.find_all("tr"):
                cell = existing.find("td")
                label = cell.get_text(" ", strip=True) if cell else ""
                if row.get("after") and row["after"] in label:
                    anchor = existing
                    break
                if not row.get("after") and label.startswith("T–0"):
                    existing.insert_before(tr)
                    anchor = False
                    break
            if anchor:
                anchor.insert_after(tr)
            elif anchor is None:
                body.append(tr)
    return n


# ---------------------------------------------------------------- output checks
def _facet_inventory(meta_table, skip):
    """Every facet value currently in the book, excluding the chapters we added."""
    inv = {}
    for cid, m in meta_table.items():
        if cid in skip:
            continue
        for key in GATED_FACETS:
            val = m.get(key)
            for v in (val if isinstance(val, list) else [val] if val else []):
                inv.setdefault(key, set()).add(v)
    return inv


def check(data, payloads, meta_table, lib_chapters, book_ids, classify):
    """Errors and warnings that need the assembled data. Returns (errors, warnings)."""
    errors, warnings = [], []
    menus = {m["id"]: m for m in data["menus"]}
    added = {p["chapterId"] for p in payloads if p["kind"] == "menu"}
    inventory = _facet_inventory(meta_table, added)

    for p in payloads:
        f, kind = p["_file"], p["kind"]

        if kind == "menu":
            cid = p["chapterId"]
            if cid in book_ids:
                errors.append(f"{f}: chapterId {cid!r} is already a section in book/")
            if p["afterChapter"] not in menus:
                errors.append(f"{f}: afterChapter {p['afterChapter']!r} is not an existing menu")
            recipes = {r["title"] for r in p["recipes"]}
            for r in p["recipes"]:
                got = classify(meta_line(r))
                if got != r["course"]:
                    errors.append(f"{f}: recipe {r['title']!r} declares course {r['course']!r} "
                                  f"but classify() reads {got!r} from its meta line "
                                  f"{meta_line(r)!r}; check 'metaExtra' for a course word")
            for it in p["capacity"].get("items") or []:
                hits = [t for t in recipes if it["match"].lower() in t.lower()]
                if len(hits) != 1:
                    errors.append(f"{f}: capacity match {it['match']!r} hits {len(hits)} recipe "
                                  f"titles in {cid}; it must hit exactly one")
            errors.extend(_gate(p, p["facets"], inventory, f))
            warnings.extend(_near(p, p["facets"], inventory, f))
            warnings.extend(_kit(p["recipes"], p["capacity"].get("items") or [], f))

        elif kind == "recipe":
            cid = p["menuId"]
            if cid not in menus:
                errors.append(f"{f}: menuId {cid!r} is not an existing menu chapter")
                continue
            r = p["recipe"]
            got = classify(meta_line(r))
            if got != r["course"]:
                errors.append(f"{f}: recipe {r['title']!r} declares course {r['course']!r} "
                              f"but classify() reads {got!r} from {meta_line(r)!r}")
            titles = [x["title"] for x in menus[cid]["recipes"]]
            if titles.count(r["title"]) > 1:
                errors.append(f"{f}: {cid} now has two recipes titled {r['title']!r}")
            if p.get("placement", {}).get("after"):
                want = p["placement"]["after"].lower()
                hits = [t for t in titles if want in t.lower() and t != r["title"]]
                if len(hits) != 1:
                    errors.append(f"{f}: placement.after {p['placement']['after']!r} matches "
                                  f"{len(hits)} existing recipes in {cid}; it must match one")
            for it in (p.get("capacity") or {}).get("items") or []:
                hits = [t for t in titles if it["match"].lower() in t.lower()]
                if len(hits) != 1:
                    errors.append(f"{f}: capacity match {it['match']!r} hits {len(hits)} "
                                  f"recipe titles in {cid}")
            errors.extend(_gate(p, p.get("facetAdds") or {}, inventory, f))
            warnings.extend(_near(p, p.get("facetAdds") or {}, inventory, f))
            warnings.extend(_kit([r], (p.get("capacity") or {}).get("items") or [], f))
            warnings.extend(_dupe_shopping(p, menus[cid], f))

        elif kind == "library":
            cid = p["chapterId"]
            if cid not in lib_chapters:
                errors.append(f"{f}: chapterId {cid!r} is not a library chapter "
                              f"({', '.join(lib_chapters)})")
            title = p["recipe"]["title"]
            for other in data["library"]:
                if other["title"] == title or other.get("chapterId") != cid:
                    if other["title"] != title:
                        continue
                # libraryRef matches fuzzily on the first 10 characters, so a title
                # that shadows another silently expands the wrong ingredients.
                a, b = norm(title), norm(other["title"])
                if a != b and (a.startswith(b[:10]) or b.startswith(a[:10]) or b in a or a in b):
                    errors.append(f"{f}: library title {title!r} shadows the existing "
                                  f"{other['title']!r}; libraryRef would resolve "
                                  f"'(Chapter NN)' references to the wrong one")
                    break

        elif kind == "patch":
            if p["target"] not in menus:
                errors.append(f"{f}: patch target {p['target']!r} is not an existing menu")
                continue
            merged = {k: v for k, v in menus[p["target"]].items() if k in FACET_KEYS}
            errors.extend(_check_facets(merged, "patched facets", f))
            errors.extend(_gate(p, merged, inventory, f))
            warnings.extend(_near(p, merged, inventory, f))

    errors.extend(_integrity(data, added, hard=True))
    warnings.extend(_integrity(data, added, hard=False))
    return errors, warnings


def _declared(p):
    d = p.get("newFacetValues") or {}
    return {k: set(v) for k, v in d.items()}


def _gate(p, facets, inventory, f):
    """Any facet value not already in the book must be declared explicitly."""
    out, declared = [], _declared(p)
    for key in GATED_FACETS:
        val = facets.get(key)
        for v in (val if isinstance(val, list) else [val] if val else []):
            known = inventory.get(key, set())
            if v in known or v in declared.get(key, set()):
                clash = next((k for k in known if norm(k) == norm(v) and k != v), None)
                if clash:
                    out.append(f"{f}: {key} value {v!r} differs only in case or punctuation "
                               f"from the existing {clash!r}; use the existing spelling or "
                               f"the app grows a duplicate one-item filter")
                continue
            clash = next((k for k in known if norm(k) == norm(v)), None)
            if clash:
                out.append(f"{f}: {key} value {v!r} differs only in case or punctuation from "
                           f"the existing {clash!r}; use the existing spelling")
            else:
                out.append(f"{f}: {key} value {v!r} is new to the book. If that is deliberate, "
                           f"add it to newFacetValues: {{\"{key}\": [\"{v}\"]}}")
    return out


def _near(p, facets, inventory, f):
    """Warn when a declared-new value looks like a typo of an existing one."""
    out, declared = [], _declared(p)
    for key, vals in declared.items():
        known = [k for k in inventory.get(key, set())]
        for v in vals:
            if v in known:
                continue
            close = difflib.get_close_matches(v, known, n=1, cutoff=0.82)
            if close:
                out.append(f"{f}: new {key} value {v!r} is very close to the existing "
                           f"{close[0]!r} — reuse it unless they are genuinely different")
    return out


# Units and filler stripped before comparing two shopping entries.
_UNITS = {"lb", "lbs", "oz", "g", "kg", "ml", "l", "quart", "quarts", "pint", "cup",
          "cups", "tbsp", "tsp", "links", "link", "heads", "head", "bunch", "bunches",
          "large", "small", "medium", "about", "or", "and", "the", "a", "of", "in",
          "one", "two", "each", "whole", "piece", "pieces", "loaf", "loaves"}


def _entry_words(text):
    """The identifying words of a shopping entry, with quantities and units dropped."""
    words = re.findall(r"[a-z]+", text.lower())
    return frozenset(w for w in words if w not in _UNITS)


def _dupe_shopping(p, menu, f):
    """Warn when shoppingAdds repeats something the category already lists."""
    out = []
    shopping = (menu.get("blocks") or {}).get("shopping") or ""
    for cat, items in (p.get("shoppingAdds") or {}).items():
        body = next((m.group(2) for m in re.finditer(
            r"<li><strong>([^<]*?):</strong>(.*?)</li>", shopping)
            if m.group(1) == cat), None)
        if body is None:
            continue
        entries = [e.strip() for e in body.split("\u00b7")]
        for item in items:
            want = _entry_words(item)
            if want and sum(1 for e in entries if _entry_words(e) == want) > 1:
                twin = next(e for e in entries if _entry_words(e) == want and e != item)
                out.append(f"{f}: shoppingAdds['{cat}'] adds {item!r} but the list already "
                           f"has {twin!r}; the printed list will show both")
    return out


def _kit(recipes, items, f):
    """Warn when a method mentions kit that has no matching capacity item."""
    out = []
    types = {it.get("type") for it in items}
    for r in recipes:
        text = " ".join(r.get("method") or []).lower()
        for pattern, want in KIT_HINTS:
            if re.search(pattern, text) and want not in types:
                out.append(f"{f}: {r['title']!r} mentions {want} in its method but has no "
                           f"'{want}' capacity item, so the app will say it scales fine")
        if r.get("course") == "Main" and "°f" not in text:
            out.append(f"{f}: {r['title']!r} is a Main with no pull temperature in its "
                       f"method (temperatures are instructions, times are estimates)")
    return out


def _integrity(data, added, hard):
    """Shared data-model checks. hard=True reports only chapters we added."""
    out = []
    which = (lambda cid: cid in added) if hard else (lambda cid: cid not in added)
    label = "" if hard else "book: "
    seen = {}
    for m in data["menus"]:
        for r in m["recipes"]:
            seen.setdefault(m["id"] + "|" + r["title"], []).append(m["id"])
            if not which(m["id"]):
                continue
            if not r.get("plating"):
                out.append(f"{label}{m['id']} {r['title']!r} has no plating note")
            if r["course"] == "Other":
                out.append(f"{label}{m['id']} {r['title']!r} classified as 'Other' and will "
                           f"not appear on its own menu page")
        if hard and which(m["id"]) and not m["blocks"].get("shopping"):
            out.append(f"{label}{m['id']} has no shopping block")
    for r in data["library"] + data["showpieces"]:
        seen.setdefault(r["chapterId"] + "|" + r["title"], []).append(r["chapterId"])
        if not which(r["chapterId"]):
            continue
        if not r.get("plating"):
            out.append(f"{label}{r['chapterId']} {r['title']!r} has no plating note")
    for key, owners in seen.items():
        if len(owners) > 1 and which(owners[0]):
            out.append(f"{label}duplicate recipe key {key!r}; the cart and permalinks "
                       f"cannot tell these apart")
    return out


# ---------------------------------------------------------------- reporting
def report(payloads, data):
    """Say what was merged, and name the photo keys the new content wants."""
    if not payloads:
        return
    menus = {m["id"]: m for m in data["menus"]}
    for p in payloads:
        f, kind = p["_file"], p["kind"]
        if kind == "menu":
            m = menus.get(p["chapterId"], {})
            print(f"  · {f}: +menu {p['chapterId']} {p['title']!r} "
                  f"({len(p['recipes'])} recipes, part {p['part']!r})")
            keys = [p["chapterId"]] + [p["chapterId"] + "|" + r["title"] for r in p["recipes"]]
            missing = [k for k, r in zip(keys, [m] + m.get("recipes", [])) if not r.get("image")]
            if missing:
                print(f"    photos wanted: {len(missing)} keys — "
                      f"npm run fetch-images -- --only {p['chapterId']}")
        elif kind == "recipe":
            print(f"  · {f}: +recipe {p['menuId']} {p['recipe']['title']!r} "
                  f"({p['recipe']['course']})")
        elif kind == "library":
            print(f"  · {f}: +library {p['chapterId']} {p['recipe']['title']!r}")
        elif kind == "patch":
            touched = sorted(set((p.get("set") or {})) | set((p.get("add") or {}))
                             | set((p.get("remove") or {})))
            print(f"  · {f}: patch {p['target']} facets {', '.join(touched)}")


def emit_html(payloads, out_dir):
    """Dump generated chapters to disk so they can be pasted into book/ later."""
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for p in payloads:
        if p["kind"] != "menu":
            continue
        target = out_dir / (p["chapterId"] + ".html")
        target.write_text(render_chapter(p) + "\n", encoding="utf-8")
        written.append(target)
    return written
