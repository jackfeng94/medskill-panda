#!/usr/bin/env python3
"""Search and fetch scientific icons from Bioicons (https://bioicons.com), with attribution.

Bioicons collects ~2,800 SVG icons for biology and medicine (cells, antibodies, receptors,
organs, lab equipment), each with its own licence: CC0, CC BY 3.0/4.0, MIT, BSD, and a few
CC BY-SA. Many come from Servier Medical Art.

  search  TERM [TERM …] [--category C] [--allow-sa]     list matching icons (licence, author)
  get     NAME|PATH [… ] -o figures/icons [--prefix id]  download, clean, write ATTRIBUTION.md

`get` cleans each SVG for inlining (drops Inkscape metadata and fixed width/height, prefixes
ids so several icons can share one page) and appends a credit line for each icon to
<out>/ATTRIBUTION.md and <out>/attribution.json. Put the credit on the slide that uses it.

Share-alike (CC BY-SA) icons are hidden unless --allow-sa: they impose their licence on the
slide that uses them.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TREE = "https://api.github.com/repos/duerrsimon/bioicons/git/trees/main?recursive=1"
RAW = "https://raw.githubusercontent.com/duerrsimon/bioicons/main/"
CACHE = Path(tempfile.gettempdir()) / "medskill-panda-bioicons-tree.json"
UA = {"User-Agent": "medskill-panda/1.0"}
LICENCE_URL = {
    "cc-0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "cc-by-3.0": "https://creativecommons.org/licenses/by/3.0/",
    "cc-by-4.0": "https://creativecommons.org/licenses/by/4.0/",
    "cc-by-sa-3.0": "https://creativecommons.org/licenses/by-sa/3.0/",
    "cc-by-sa-4.0": "https://creativecommons.org/licenses/by-sa/4.0/",
    "mit": "https://opensource.org/licenses/MIT",
    "bsd": "https://opensource.org/licenses/BSD-3-Clause",
}


def http(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()


def icons() -> list[dict]:
    """All icons, parsed from the repository tree (cached for a day)."""
    if CACHE.exists() and time.time() - CACHE.stat().st_mtime < 86400:
        paths = json.loads(CACHE.read_text(encoding="utf-8"))
    else:
        tree = json.loads(http(TREE))["tree"]
        paths = [t["path"] for t in tree if t["path"].startswith("static/icons/") and t["path"].endswith(".svg")]
        CACHE.write_text(json.dumps(paths), encoding="utf-8")
    out = []
    for p in paths:
        parts = p.split("/")
        if len(parts) != 6:
            continue
        _, _, lic, cat, author, file = parts
        out.append({"path": p, "licence": lic, "category": cat, "author": author.replace("-", " ").strip(),
                    "name": file[:-4]})
    return out


def search(terms: list[str], category: str | None, allow_sa: bool) -> list[dict]:
    terms = [t.lower() for t in terms]
    hits = []
    for ic in icons():
        hay = f"{ic['name']} {ic['category']}".lower().replace("_", " ").replace("-", " ")
        if not all(t in hay for t in terms):
            continue
        if category and category.lower() not in ic["category"].lower():
            continue
        if "sa" in ic["licence"] and not allow_sa:
            continue
        hits.append(ic)
    return hits


def clean(svg: str, prefix: str) -> str:
    svg = re.sub(r"<\?xml[^>]*\?>|<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r"<sodipodi:namedview\b[^>]*/>", "", svg)                       # self-closing
    svg = re.sub(r"<sodipodi:namedview\b.*?</sodipodi:namedview>", "", svg, flags=re.S)  # with children
    svg = re.sub(r"</?(?:sodipodi|inkscape):[^>]*>", "", svg)                     # any leftovers
    svg = re.sub(r"<metadata\b.*?</metadata>", "", svg, flags=re.S)
    svg = re.sub(r'\s(?:inkscape|sodipodi):[\w-]+="[^"]*"', "", svg)
    svg = re.sub(r'\sxmlns:(?:inkscape|sodipodi|svg)="[^"]*"', "", svg)
    svg = re.sub(r'(<svg\b[^>]*?)\s(?:width|height)="[^"]*"', r"\1", svg)
    svg = re.sub(r'(<svg\b[^>]*?)\s(?:width|height)="[^"]*"', r"\1", svg)
    svg = re.sub(r'id="([^"]+)"', lambda m: f'id="{prefix}-{m.group(1)}"', svg)
    svg = re.sub(r"url\(#([^)]+)\)", lambda m: f"url(#{prefix}-{m.group(1)})", svg)
    svg = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{prefix}-{m.group(1)}"', svg)
    return svg.strip() + "\n"


def credit(ic: dict) -> str:
    lic = ic["licence"].upper().replace("CC-", "CC ").replace("-", " ")
    return f'"{ic["name"]}" by {ic["author"]} (Bioicons), {lic}'


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("terms", nargs="+")
    s.add_argument("--category")
    s.add_argument("--allow-sa", action="store_true")
    g = sub.add_parser("get")
    g.add_argument("names", nargs="+", help="icon name (e.g. t-lymphocyte) or its path from `search`")
    g.add_argument("-o", "--out", required=True)
    g.add_argument("--prefix", help="id prefix (default: the icon name)")
    g.add_argument("--allow-sa", action="store_true")
    a = ap.parse_args(argv)

    if a.cmd == "search":
        hits = search(a.terms, a.category, a.allow_sa)
        for ic in hits[:60]:
            print(f"{ic['licence']:12} {ic['category']:22} {ic['author'][:22]:22} {ic['name']}")
        print(f"{len(hits)} match(es)" + (" (first 60 shown)" if len(hits) > 60 else ""))
        return 0

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    index = {ic["path"]: ic for ic in icons()}
    by_name: dict[str, list[dict]] = {}
    for ic in index.values():
        by_name.setdefault(ic["name"], []).append(ic)
    att_json = out / "attribution.json"
    record = json.loads(att_json.read_text(encoding="utf-8")) if att_json.exists() else {"icons": []}
    for nm in a.names:
        cands = [index[nm]] if nm in index else by_name.get(nm, [])
        if not cands:
            print(f"not found: {nm} (use `search`)", file=sys.stderr)
            return 1
        if len(cands) > 1:
            print(f"ambiguous: {nm} → " + ", ".join(c["path"] for c in cands) + " (pass the path)", file=sys.stderr)
            return 1
        ic = cands[0]
        if "sa" in ic["licence"] and not a.allow_sa:
            print(f"{nm} is {ic['licence']} (share-alike): pass --allow-sa if that licence is acceptable", file=sys.stderr)
            return 1
        prefix = a.prefix or re.sub(r"[^a-z0-9]+", "-", ic["name"].lower()).strip("-")
        svg = clean(http(RAW + ic["path"]).decode("utf-8"), prefix)
        (out / f"{ic['name']}.svg").write_text(svg, encoding="utf-8")
        entry = {**ic, "file": f"{ic['name']}.svg", "url": RAW + ic["path"],
                 "licence_url": LICENCE_URL.get(ic["licence"], ""), "credit": credit(ic)}
        record["icons"] = [x for x in record["icons"] if x["file"] != entry["file"]] + [entry]
        print(f"{out / entry['file']}  {entry['credit']}")
    att_json.write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
    lines = ["# Icon credits", "", "Icons from Bioicons (https://bioicons.com). Show these credits on the slides that use them.", ""]
    lines += [f"- {x['credit']}: {x['licence_url']}" for x in record["icons"]]
    (out / "ATTRIBUTION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
