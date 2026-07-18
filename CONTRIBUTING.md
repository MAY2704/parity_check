# Contributing

## Before changing a skill

Read `BEST_PRACTICES.md` first. It explains the design rules (single writer to the graph, fail-closed defaults, the confidence-propagation asymmetry) that a change should not silently break.

1. Bump the `version` in that skill's `SKILL.md` frontmatter per the semver rule in `SKILLS_CHANGELOG.md` (MAJOR/MINOR/PATCH), and add a line to that file's `Current versions` table and `Change history`.
2. If the change alters a skill's output shape, check every other skill's `depends_on` for one that reads it. The agent's pinned version ranges in `parity-auditor.chatmode.md` may need updating too.
3. Every skill's "Output message" JSON example must stay valid against `context/schemas/skill-message.schema.json`.

## Validating locally

```
pip install -r scripts/requirements.txt
python scripts/validate_skills.py
```

This checks that every `SKILL.md`'s frontmatter version matches `SKILLS_CHANGELOG.md`, and that every embedded "Output message" example plus every `output/reports/*.json` file validates against the schema. CI runs the same script on every push and PR.

## Adding a new skill

Follow the shape of an existing `skills/{name}/{SKILL.md,REFERENCE.md}` pair: frontmatter contract (`inputs`, `outputs`, `depends_on`) in `SKILL.md`, formulas/catalogs/worked examples in `REFERENCE.md`. Wire it into `parity-auditor.chatmode.md` or `blindspot-scout.chatmode.md` explicitly. Skills never call each other.

## Pull requests

Keep them scoped to one skill or one doc at a time where possible. This repo's whole premise is that a change to one skill's contract can silently break another, so smaller diffs are easier to check against `depends_on`.
