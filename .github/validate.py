#!/usr/bin/env python3
"""Repo self-checks for the ai-app-blueprints skill.

Guards the properties a Claude Code skill quietly depends on: parseable frontmatter, a
description within the ~1024-char budget, referenced files that actually exist, evals with
negative cases, a changelog entry matching metadata.version, and no German residue from the
repo's translation history.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
errors: list[str] = []

skill = (ROOT / "SKILL.md").read_text()
match = re.match(r"^---\n(.*?)\n---\n", skill, re.S)
if not match:
    errors.append("SKILL.md: frontmatter block missing")
frontmatter = match.group(1) if match else ""

name = re.search(r"^name: (.+)$", frontmatter, re.M)
if not name or name.group(1).strip() != "ai-app-blueprints":
    errors.append("frontmatter: name must be ai-app-blueprints")

description = re.search(r"^description: (.+)$", frontmatter, re.M)
if not description:
    errors.append("frontmatter: description missing")
elif len(description.group(1)) > 1024:
    errors.append(f"description is {len(description.group(1))} chars (budget: 1024)")

version = re.search(r'version: "([^"]+)"', frontmatter)
if not version:
    errors.append("frontmatter: metadata.version missing")
else:
    readme = (ROOT / "README.md").read_text()
    if f"**{version.group(1)}**" not in readme:
        errors.append(f"version {version.group(1)} has no README changelog entry")

for ref in sorted(set(re.findall(r"`((?:references|assets|evals)/[A-Za-z0-9._\-]+)`", skill))):
    if not (ROOT / ref).exists():
        errors.append(f"SKILL.md references a missing file: {ref}")

evals = json.loads((ROOT / "evals/evals.json").read_text())
if evals.get("skill_name") != "ai-app-blueprints":
    errors.append("evals.json: skill_name mismatch")
negatives = [e for e in evals["evals"] if "NOT trigger" in e["expected_output"]]
if len(negatives) < 2:
    errors.append(f"evals.json: need at least 2 negative cases, found {len(negatives)}")

for path in ROOT.rglob("*"):
    if path.is_file() and ".git" not in path.parts and path.suffix in {".md", ".json", ".svg", ".yml"}:
        if re.search(r"[äöüßÄÖÜ]", path.read_text(errors="ignore")):
            errors.append(f"German umlauts in {path.relative_to(ROOT)}")

if errors:
    print("\n".join(f"FAIL: {e}" for e in errors))
    sys.exit(1)
print(f"all checks passed ({len(evals['evals'])} evals, description {len(description.group(1))} chars)")
