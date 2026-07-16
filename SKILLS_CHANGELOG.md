# Skills Changelog

Every skill is versioned independently (semantic versioning: MAJOR.MINOR.PATCH). This file is the single place to see current versions and history across the whole skill library — individual skills don't carry their own changelog file, to avoid fragmenting a six-skill project across a dozen extra files.

**Versioning convention, applied consistently across every skill:**
- **MAJOR** — breaking change to a skill's input/output contract, scoring formula, or classification scheme. Anything depending on this skill (the agent, another skill, or a human reading its output) may need to change.
- **MINOR** — new capability added, backward-compatible. Existing inputs/outputs still work unchanged.
- **PATCH** — bug fix, corrected pattern/threshold/formula implementation, no contract change.

## Current versions

| Skill | Version | Last change |
|---|---|---|
| legacy-rule-extraction | 1.1.0 | Added date-arithmetic pattern to catalog (MINOR) |
| knowledge-graph-builder | 1.3.0 | Added AISemanticCheck node type (MINOR); added export-to-TTL sync path (MINOR) |
| heuristic-validation | 1.0.0 | Initial release |
| ai-semantic-validation | 1.0.0 | Initial release |
| parity-evaluation | 1.2.0 | Added accuracy metric alongside precision/recall/F1 (MINOR); added oracle-disagreement reporting (MINOR) |
| confidence-scoring | 1.1.0 | Added Semantic Agreement component and the coincidental-match-risk override (MINOR — new component, reweighted, no existing component removed) |

## Compatibility

The agent (`.github/chatmodes/parity-auditor.chatmode.md`) declares which skill version ranges it expects — see that file's frontmatter-equivalent dependency notes. A skill upgraded past a MAJOR boundary requires the agent definition to be reviewed before use, not assumed compatible.

## Change history

- **2026-07-16** — Introduced `ai-semantic-validation` (1.0.0) and the coincidental-match-risk override in `confidence-scoring` (1.0.0 → 1.1.0), specifically to catch artifacts that pass numeric parity by matching the golden dataset's specific values rather than implementing the general rule. `parity-evaluation` bumped 1.1.0 → 1.2.0 to add the `accuracy` metric and oracle-disagreement reporting. `knowledge-graph-builder` bumped 1.2.0 → 1.3.0 to add the `AISemanticCheck` node type.
- **2026-07-15** — Initial skill set: `legacy-rule-extraction` (1.0.0), `knowledge-graph-builder` (1.2.0), `heuristic-validation` (1.0.0), `parity-evaluation` (1.1.0), `confidence-scoring` (1.0.0).
