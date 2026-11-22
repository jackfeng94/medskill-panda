"""Repository checks: skill frontmatter, manifests, file references and Python syntax."""
from __future__ import annotations

import json
import py_compile
import re
import tempfile
import unittest

from helpers import ROOT

READMES = ("README.md", "README.vi.md")
SKILLS = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def frontmatter(path):
    m = FRONTMATTER.match(path.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def field(fm, name):
    m = re.search(rf"^{name}:\s*(.+)$", fm, re.M)
    return m.group(1).strip().strip('"') if m else None


class SkillsTest(unittest.TestCase):
    def test_every_skill_has_valid_frontmatter(self):
        for skill in SKILLS:
            with self.subTest(skill=skill.name):
                md = skill / "SKILL.md"
                self.assertTrue(md.is_file(), "missing SKILL.md")
                fm = frontmatter(md)
                self.assertIsNotNone(fm, "missing frontmatter")
                self.assertEqual(field(fm, "name"), skill.name)
                desc = field(fm, "description")
                self.assertTrue(desc, "missing description")
                self.assertLessEqual(len(desc), 1024, "description over 1024 characters")

    def test_skill_names_are_unique_and_kebab_case(self):
        for skill in SKILLS:
            self.assertRegex(skill.name, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

    def test_referenced_skill_files_exist(self):
        ref = re.compile(r"`((?:scripts|references|assets|roles|templates)/[\w./-]+\.\w+)`")
        for skill in SKILLS:
            text = (skill / "SKILL.md").read_text(encoding="utf-8")
            for rel in set(ref.findall(text)):
                with self.subTest(skill=skill.name, ref=rel):
                    self.assertTrue((skill / rel).exists())

    def test_no_reference_to_removed_skills(self):
        removed = ("scientific-slides", "market-research-reports", "scholar-evaluation")
        for path in ROOT.rglob("*"):
            if ".git" in path.parts or path.suffix not in (".md", ".py", ".json", ".yaml", ".sh"):
                continue
            if path.name == "CHANGELOG.md" or "tests" in path.relative_to(ROOT).parts:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for name in removed:
                with self.subTest(path=str(path.relative_to(ROOT)), name=name):
                    self.assertFalse(name in text, f"{path.name} still mentions {name}")

    def test_readmes_list_every_skill(self):
        for name in READMES:
            readme = (ROOT / name).read_text(encoding="utf-8")
            for skill in SKILLS:
                with self.subTest(readme=name, skill=skill.name):
                    self.assertTrue(f"`{skill.name}`" in readme, f"{skill.name} missing from {name}")
            m = re.search(r"skills-(\d+)-", readme)
            self.assertIsNotNone(m, f"skills badge missing in {name}")
            self.assertEqual(int(m.group(1)), len(SKILLS), f"skills badge count is stale in {name}")

    def test_readme_translations_stay_in_step(self):
        """English and Vietnamese READMEs: same version, commands, images; each links the other."""
        texts = {n: (ROOT / n).read_text(encoding="utf-8") for n in READMES}
        version = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
        commands = {n: set(re.findall(r"/medskill-panda:[a-z-]+", t)) for n, t in texts.items()}
        self.assertEqual(commands["README.md"], commands["README.vi.md"])
        for name, text in texts.items():
            with self.subTest(readme=name):
                self.assertIn(f"version-{version}-", text)
                for other in READMES:
                    if other != name:
                        self.assertIn(f"]({other})", text)
                for img in re.findall(r'src="(assets/[^"]+)"', text):
                    self.assertTrue((ROOT / img).is_file(), img)


class GuideTest(unittest.TestCase):
    GUIDES = ("docs/GUIDE.md", "docs/HUONG-DAN.md")

    def test_guides_link_each_other_and_from_readmes(self):
        self.assertIn("](docs/GUIDE.md)", (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn("](docs/HUONG-DAN.md)", (ROOT / "README.vi.md").read_text(encoding="utf-8"))
        self.assertIn("](HUONG-DAN.md)", (ROOT / "docs/GUIDE.md").read_text(encoding="utf-8"))
        self.assertIn("](GUIDE.md)", (ROOT / "docs/HUONG-DAN.md").read_text(encoding="utf-8"))

    def test_guide_commands_and_images_exist(self):
        skills = {p.name for p in SKILLS}
        for name in self.GUIDES:
            text = (ROOT / name).read_text(encoding="utf-8")
            for cmd in set(re.findall(r"/medskill-panda:([a-z-]+)", text)):
                with self.subTest(guide=name, command=cmd):
                    self.assertTrue((ROOT / "commands" / f"{cmd}.md").is_file() or cmd in skills)
            for img in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
                with self.subTest(guide=name, image=img):
                    self.assertTrue((ROOT / "docs" / img).resolve().is_file())

    def test_guides_cover_the_same_sections(self):
        heads = [re.findall(r"^## (\d+)\.", (ROOT / g).read_text(encoding="utf-8"), re.M) for g in self.GUIDES]
        self.assertEqual(heads[0], heads[1])


class ArtworkTest(unittest.TestCase):
    """README/guide images carry a content hash in their name (no stale browser copies) and are all used."""

    def test_images_are_hashed_and_referenced(self):
        docs = " ".join(p.read_text(encoding="utf-8") for p in
                        [ROOT / "README.md", ROOT / "README.vi.md", *(ROOT / "docs").glob("*.md")])
        for png in (ROOT / "assets").glob("*.png"):
            if png.name == "logo.png":
                continue
            with self.subTest(image=png.name):
                self.assertRegex(png.name, r"\.[0-9a-f]{8}\.png$", "publish with assets/src/publish_art.py")
                self.assertIn(png.name, docs, "image not used by any README or guide")


class ManifestTest(unittest.TestCase):
    def test_versions_agree(self):
        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(plugin["version"], market["plugins"][0]["version"])
        self.assertIn(f"## {plugin['version']}", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))

    def test_hooks_json_points_at_existing_scripts(self):
        hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        for event in hooks["hooks"].values():
            for entry in event:
                for h in entry["hooks"]:
                    script = h["command"].split()[-1]
                    with self.subTest(script=script):
                        self.assertTrue((ROOT / "hooks" / script).is_file())

    def test_commands_have_descriptions(self):
        for cmd in (ROOT / "commands").glob("*.md"):
            with self.subTest(cmd=cmd.name):
                fm = frontmatter(cmd)
                self.assertTrue(fm and field(fm, "description"))


class PythonTest(unittest.TestCase):
    def test_all_python_compiles(self):
        with tempfile.TemporaryDirectory() as d:
            for i, path in enumerate(ROOT.rglob("*.py")):
                if ".git" in path.parts:
                    continue
                with self.subTest(path=str(path.relative_to(ROOT))):
                    py_compile.compile(str(path), cfile=f"{d}/{i}.pyc", doraise=True)


if __name__ == "__main__":
    unittest.main()
