# Skills Changelog

Every skill is versioned independently (semantic versioning: MAJOR.MINOR.PATCH). This file is the single place to see current versions and history across the whole skill library. Individual skills don't carry their own changelog file, to avoid fragmenting a six-skill project across a dozen extra files.

**Versioning convention, applied consistently across every skill:**
- **MAJOR**: breaking change to a skill's input/output contract, scoring formula, or classification scheme. Anything depending on this skill (the agent, another skill, or a human reading its output) may need to change.
- **MINOR**: new capability added, backward-compatible. Existing inputs/outputs still work unchanged.
- **PATCH**: bug fix, corrected pattern/threshold/formula implementation, no contract change.

## Current versions

| Skill | Version | Last change |
|---|---|---|
| legacy-rule-extraction | 2.0.0 | Output changed from prose description to the JSON message envelope (MAJOR) |
| knowledge-graph-builder | 2.0.0 | Output changed to the JSON envelope; now explicitly consumes upstream messages rather than ad hoc evidence records (MAJOR) |
| heuristic-validation | 2.0.0 | Output changed to the JSON envelope; confidence now reflects the heuristic's own track record, not just pass/fail (MAJOR) |
| ai-semantic-validation | 2.0.0 | Output changed to the JSON envelope; confidence explicitly marked `self-reported` (MAJOR) |
| parity-evaluation | 2.0.0 | Output changed to the JSON envelope; confidence now reflects oracle coverage, not match rate (MAJOR) |
| confidence-scoring | 2.0.0 | Now consumes upstream JSON messages directly and enforces the self-reported propagation rule (MAJOR) |

## Compatibility

The agent (`.github/chatmodes/parity-auditor.chatmode.md`) declares which skill version ranges it expects. All six skills are currently pinned to `^2.0.0` as a set. The 2.0.0 bump on every skill was the same breaking change (adoption of the shared JSON message envelope), so they moved together. A skill still on a 1.x line does not emit that envelope and cannot be wired into the current pipeline without the agent's dependency table being reviewed first.

## Change history

- **2026-07-17**: Introduced the shared JSON message envelope (`context/schemas/skill-message.schema.json`) and `skills/SKILL_MESSAGES.md`. Every skill's output contract changed from prose/ad hoc structure to this schema, requiring a MAJOR bump across the board: all six skills moved to **2.0.0**. Added the confidence `source` distinction (`calibrated` vs. `self-reported`) and the propagation rule (self-reported confidence may lower a downstream score, never raise one), enforced in `confidence-scoring`.
- **2026-07-16**: Introduced `ai-semantic-validation` (1.0.0) and the coincidental-match-risk override in `confidence-scoring` (1.0.0 to 1.1.0), specifically to catch artifacts that pass numeric parity by matching the golden dataset's specific values rather than implementing the general rule. `parity-evaluation` bumped 1.1.0 to 1.2.0 to add the `accuracy` metric and oracle-disagreement reporting. `knowledge-graph-builder` bumped 1.2.0 to 1.3.0 to add the `AISemanticCheck` node type.
- **2026-07-15**: Initial skill set: `legacy-rule-extraction` (1.0.0), `knowledge-graph-builder` (1.2.0), `heuristic-validation` (1.0.0), `parity-evaluation` (1.1.0), `confidence-scoring` (1.0.0).
