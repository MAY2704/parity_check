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
| parity-evaluation | 3.0.0 | Comparison is now executed by `scripts/parity_eval.py`; degenerate metrics report null, not 1.0; added differential fuzzing, boundary cases, property checks, dataset adequacy (MAJOR) |
| confidence-scoring | 2.1.0 | Added null-metric fallbacks for parity-evaluation ≥ 3.0.0 degenerate runs (MINOR) |

## Compatibility

The agent (`.github/chatmodes/parity-auditor.chatmode.md`) declares which skill version ranges it expects: `parity-evaluation` at `^3.0.0`, the rest at `^2.0.0` (which `confidence-scoring` 2.1.0 satisfies). The 2.0.0 bump on every skill was the same breaking change (adoption of the shared JSON message envelope), so they moved together; the 3.0.0 bump is specific to `parity-evaluation` (deterministic harness + metric conventions), and `confidence-scoring` ≥ 2.1.0 is required to consume its null metrics correctly. A skill still on a 1.x line does not emit the envelope and cannot be wired into the current pipeline without the agent's dependency table being reviewed first.

## Change history

- **2026-07-20**: `parity-evaluation` **2.0.0 → 3.0.0** (MAJOR). The core comparison moved from model-followed prose to a deterministic harness, `scripts/parity_eval.py`: artifact executed via `input/artifacts/{module}/harness.mjs`, rule-engine formula evaluated directly, normalization and dual comparison computed, every run reproducible from its recorded seed. Contract changes: metrics with zero denominators are now **null instead of a fabricated 1.0** (the pre-3.0 demo report showed precision/recall/F1 = 1.0 on a run that flagged nothing — undefined arithmetic); the unit of analysis is pinned to field-per-case; run-time recall counts only known misses (uncovered units + recorded escaped defects) and is recomputed as escaped defects accrue. New evidence layers: differential fuzzing + boundary-case generation against the rule engine over declared `input_domains`, metamorphic `properties` checks (no oracle needed), and a measured golden-dataset adequacy score (volume/range/boundary/provenance) feeding a recalibrated evidence-breadth confidence formula. `confidence-scoring` **2.0.0 → 2.1.0** (MINOR): null-metric fallbacks so degenerate clean runs neither score a free 1.0 nor trip the Recall Floor override; non-null metrics score exactly as before. Rule configs gained `output_fields`, `input_domains`, `properties`, and `adequacy` blocks; golden datasets gained a `provenance` declaration.
- **2026-07-17**: Introduced the shared JSON message envelope (`context/schemas/skill-message.schema.json`) and `skills/SKILL_MESSAGES.md`. Every skill's output contract changed from prose/ad hoc structure to this schema, requiring a MAJOR bump across the board: all six skills moved to **2.0.0**. Added the confidence `source` distinction (`calibrated` vs. `self-reported`) and the propagation rule (self-reported confidence may lower a downstream score, never raise one), enforced in `confidence-scoring`.
- **2026-07-16**: Introduced `ai-semantic-validation` (1.0.0) and the coincidental-match-risk override in `confidence-scoring` (1.0.0 to 1.1.0), specifically to catch artifacts that pass numeric parity by matching the golden dataset's specific values rather than implementing the general rule. `parity-evaluation` bumped 1.1.0 to 1.2.0 to add the `accuracy` metric and oracle-disagreement reporting. `knowledge-graph-builder` bumped 1.2.0 to 1.3.0 to add the `AISemanticCheck` node type.
- **2026-07-15**: Initial skill set: `legacy-rule-extraction` (1.0.0), `knowledge-graph-builder` (1.2.0), `heuristic-validation` (1.0.0), `parity-evaluation` (1.1.0), `confidence-scoring` (1.0.0).
