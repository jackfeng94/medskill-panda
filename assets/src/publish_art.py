"""Publish README artwork under content-hashed names, so browsers and GitHub never show a stale copy.

    python assets/src/publish_art.py <render-dir>

<render-dir> holds the screenshots from shoot.js: hi-en-<section>.png and hi-vi-<section>.png.
Each one is copied to assets/<name>[.vi].<hash8>.png, older versions of that image are deleted,
and every reference in README.md, README.vi.md and docs/*.md is rewritten to the new name.
"""
import hashlib
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"
SECTIONS = {"pipeline": "pipeline", "slides": "example-slides", "pptx": "example-pptx",
            "manuscript": "example-manuscript", "charts": "chart-gallery"}
DOCS = [ROOT / "README.md", ROOT / "README.vi.md", *sorted((ROOT / "docs").glob("*.md"))]


def publish(render: Path) -> dict:
    renamed = {}
    for section, base in SECTIONS.items():
        for lang, suffix in (("en", ""), ("vi", ".vi")):
            src = render / f"hi-{lang}-{section}.png"
            if not src.is_file():
                continue
            digest = hashlib.sha256(src.read_bytes()).hexdigest()[:8]
            name = f"{base}{suffix}.{digest}.png"
            pattern = re.compile(rf"^{re.escape(base + suffix)}(\.[0-9a-f]{{8}})?\.png$")
            for old in ASSETS.iterdir():
                if pattern.match(old.name) and old.name != name:
                    old.unlink()
            shutil.copy(src, ASSETS / name)
            renamed[pattern] = name
    for doc in DOCS:
        text = doc.read_text(encoding="utf-8")
        new = text
        for pattern, name in renamed.items():
            stem = pattern.pattern[1:-1]  # same expression, without the ^…$ anchors
            new = re.sub(rf"(?<=assets/){stem}", name, new)
        if new != text:
            doc.write_text(new, encoding="utf-8")
    return {p.pattern: n for p, n in renamed.items()}


if __name__ == "__main__":
    for name in publish(Path(sys.argv[1])).values():
        print("assets/" + name)
