---
name: Bug report
about: A skill, agent, schema, or query behaves differently from what its contract documents
title: "[bug] "
labels: bug
---

## What happened

A clear description of the behavior you saw.

## What the contract says should happen

Point to the relevant file: the skill's `SKILL.md`, `BEST_PRACTICES.md`, the message schema, or a Cypher query.

## Which component

- [ ] A skill (name and version from its `SKILL.md` frontmatter):
- [ ] An agent / chat mode:
- [ ] The message schema (`context/schemas/skill-message.schema.json`)
- [ ] The knowledge graph / Neo4j queries
- [ ] The validator (`scripts/validate_skills.py`) or CI
- [ ] Docs

## Reproduction

Steps, the module or artifact involved, and any run report (`output/reports/`) or log entry that shows the problem.

## Environment

- ParityKit version (`VERSION`):
- Where it ran (Copilot chat mode, local validator, CI):
