#!/usr/bin/env python3
"""Minimum CI check for ParityKit: skill versions agree with the changelog,
and every skill-message JSON example / logged report validates against
context/schemas/skill-message.schema.json. Run from the repo root:

    python scripts/validate_skills.py
"""
import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import validate, ValidationError

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "context" / "schemas" / "skill-message.schema.json"
CHANGELOG_PATH = ROOT / "SKILLS_CHANGELOG.md"

errors = []


def load_frontmatter(md_text: str) -> dict:
    match = re.match(r"^---\n(.*?)\n---\n", md_text, re.DOTALL)
    if not match:
        return {}
    return yaml.safe_load(match.group(1)) or {}


def extract_json_blocks(md_text: str) -> list:
    return [json.loads(block) for block in re.findall(r"```json\n(.*?)\n```", md_text, re.DOTALL)]


def changelog_versions() -> dict:
    text = CHANGELOG_PATH.read_text(encoding="utf-8")
    versions = {}
    for line in text.splitlines():
        m = re.match(r"\|\s*`?([\w-]+)`?\s*\|\s*(\d+\.\d+\.\d+)\s*\|", line)
        if m:
            versions[m.group(1)] = m.group(2)
    return versions


def check_versions():
    changelog = changelog_versions()
    for skill_md in sorted((ROOT / "skills").glob("*/SKILL.md")):
        fm = load_frontmatter(skill_md.read_text(encoding="utf-8"))
        name, version = fm.get("name"), fm.get("version")
        if not name or not version:
            errors.append(f"{skill_md}: frontmatter missing 'name' or 'version'")
            continue
        logged = changelog.get(name)
        if logged is None:
            errors.append(f"{skill_md}: '{name}' has no entry in SKILLS_CHANGELOG.md")
        elif logged != version:
            errors.append(
                f"{skill_md}: frontmatter version {version} != "
                f"SKILLS_CHANGELOG.md version {logged} for '{name}'"
            )


def check_schema_examples(schema):
    for skill_md in sorted((ROOT / "skills").glob("*/SKILL.md")):
        for block in extract_json_blocks(skill_md.read_text(encoding="utf-8")):
            try:
                validate(instance=block, schema=schema)
            except ValidationError as e:
                errors.append(f"{skill_md}: embedded JSON example fails schema — {e.message}")


def check_report_files(schema):
    reports_dir = ROOT / "output" / "reports"
    if not reports_dir.exists():
        return
    for report_json in sorted(reports_dir.glob("*.json")):
        data = json.loads(report_json.read_text(encoding="utf-8"))
        messages = data["messages"] if isinstance(data, dict) and "messages" in data else [data]
        for msg in messages:
            try:
                validate(instance=msg, schema=schema)
            except ValidationError as e:
                errors.append(f"{report_json}: message fails schema — {e.message}")


def main():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    check_versions()
    check_schema_examples(schema)
    check_report_files(schema)

    if errors:
        print(f"FAILED — {len(errors)} issue(s):\n")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print("OK — skill versions match SKILLS_CHANGELOG.md, all schema examples and logged reports validate.")


if __name__ == "__main__":
    main()
