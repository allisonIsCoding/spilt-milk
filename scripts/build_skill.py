#!/usr/bin/env python3
"""Assemble the Claude skill from this repo and zip it to dist/milk-carton-schematics.skill.

The repo is the source of truth: the skill bundles a copy of src/milk_carton, the docs
and the default config, so rebuild whenever those change.
Usage: python scripts/build_skill.py
"""

import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = "milk-carton-schematics"
DIST = ROOT / "dist"
DOCS = ["design-decisions.md", "stair-analysis.md", "open-questions.md", "image-prompts.md"]


def build() -> Path:
    out = DIST / NAME
    if out.exists():
        shutil.rmtree(out)
    for sub in ("scripts", "references", "assets"):
        (out / sub).mkdir(parents=True)

    shutil.copy(ROOT / "skill" / "SKILL.md", out / "SKILL.md")
    shutil.copy(ROOT / "skill" / "run.py", out / "scripts" / "run.py")
    shutil.copytree(ROOT / "src" / "milk_carton", out / "scripts" / "milk_carton",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for doc in DOCS:
        shutil.copy(ROOT / "docs" / doc, out / "references" / doc)
    shutil.copy(ROOT / "config" / "default.json", out / "assets" / "default.json")

    text = (out / "SKILL.md").read_text()
    match = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", text)
    if not match or match.group(1).strip() != NAME:
        raise SystemExit("SKILL.md frontmatter must start with name and description")

    target = DIST / f"{NAME}.skill"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(out.rglob("*")):
            if path.is_file():
                z.write(path, Path(NAME) / path.relative_to(out))
    print(f"Built {target}")
    return target


if __name__ == "__main__":
    build()
