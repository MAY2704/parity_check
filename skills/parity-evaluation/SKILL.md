---
name: parity-evaluation
version: 1.2.0
description: >
  Normalizes and then compares the artifact under test's output against
  two independent oracles — the golden dataset (empirical) and the
  rule-engine implementation (analytical) — and computes precision,
  recall, accuracy, and F1 from the resulting field-level classifications.
  Trigger after heuristic-validation has passed for the module.
inputs:
  - artifact_output: normalized-ready output from the artifact under test
  - golden_dataset: context/golden-datasets/{module}
  - rule_engine_output: computed from context/rules-engine/{module}, if present
depends_on: [heuristic-validation]
outputs:
  - discrepancy_list: classified as tolerance-acceptable / transformation-error / legacy-defect-now-fixed
  - oracle_disagreement: cases where golden dataset and rule engine disagree with each other
  - precision, recall, accuracy, f1
reference: REFERENCE.md
---

# Skill: Parity Evaluation

## What this skill does

The core empirical/analytical comparison. Two stages, always in this order: normalize, then compare against both oracles. Skipping normalization and diffing raw output punishes formatting differences as if they were logic errors; comparing against only one oracle means a golden-dataset artifact from a bad batch, or a rule-engine implementation with its own bug, goes uncaught.

## Procedure

1. **Normalize all three sides** — artifact output, golden dataset, rule-engine output — using `context/normalization-rules.md` (rounding per the rule's tolerance, ISO 8601 dates, canonical currency representation, typed null handling, case-sensitivity per field declaration). Never compare unnormalized values.
2. **Compare against the golden dataset**, field by field, every field defined for the module — no sampling.
3. **Compare against the rule-engine output**, if a `RuleEngineImpl` is linked. If none exists, report that explicitly as reduced evidence strength — a match against one oracle is weaker than a match against two, and the report must say so rather than presenting a single-oracle match as full confidence.
4. **Note oracle disagreement separately.** If the golden dataset and the rule engine disagree with each other, that's a finding about the oracles, not a tie to resolve silently in the artifact's favor — report which one the artifact agreed with and flag the discrepancy for a domain expert.
5. **Classify every discrepancy**: `tolerance-acceptable`, `transformation-error`, or `legacy-defect-now-fixed`.
6. **Compute precision, recall, accuracy, F1** at the module level, per the formulas and TP/FP/FN/TN definitions in `REFERENCE.md`. A rule with no oracle coverage contributes to recall as a hard zero, not as an excluded/unknown value.
7. **Hand off to knowledge-graph-builder** to write the `ParityCheck` evidence node, and to `ai-semantic-validation` for the logic-level cross-check.

See `REFERENCE.md` for the full normalization rule set and the precision/recall/accuracy/F1 definitions used across this framework.
