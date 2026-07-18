## What this changes

A short description, and the issue it closes (if any).

## Scope

- [ ] One skill or one doc where possible (smaller diffs are easier to check against `depends_on`)

## Contract and versioning

- [ ] If a skill's output shape, scoring formula, or classification scheme changed, I bumped its `version` in `SKILL.md` per the semver rule in `SKILLS_CHANGELOG.md`
- [ ] I updated the `Current versions` table and `Change history` in `SKILLS_CHANGELOG.md`
- [ ] If the change affects the framework as a whole, I added an entry to `CHANGELOG.md`
- [ ] I checked every other skill's `depends_on` for a consumer of the changed output, and updated the agent's pinned ranges in `parity-auditor.chatmode.md` if needed

## Validation

- [ ] `python scripts/validate_skills.py` passes locally
- [ ] Every "Output message" JSON example still validates against `context/schemas/skill-message.schema.json`

## Design

- [ ] I read `BEST_PRACTICES.md` and this change does not weaken a fail-closed default, the single-writer rule, or the human sign-off gates
