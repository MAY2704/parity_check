---
name: parity-evaluation
version: 2.0.0
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
  - JSON message per context/schemas/skill-message.schema.json
output_schema: ../../context/schemas/skill-message.schema.json
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

## Output message

Confidence here is `calibrated` from **oracle coverage**, not from the match rate — a perfect match against one oracle is weaker evidence than a good-but-imperfect match against two, and the basis field must say so explicitly:

```json
{
  "skill": "parity-evaluation",
  "skill_version": "2.0.0",
  "module": "interest-accrual",
  "run_id": "run-2026-07-17T09:41:00Z-interest-accrual",
  "timestamp": "2026-07-17T09:43:50Z",
  "status": "pass",
  "confidence": {
    "value": 0.9,
    "band": "high",
    "basis": "Both golden-dataset and rule-engine oracles present and in agreement with each other and with the artifact; all fields compared, no sampling.",
    "source": "calibrated"
  },
  "result": {
    "discrepancies": [],
    "oracle_disagreement": [],
    "precision": 1.0,
    "recall": 0.92,
    "accuracy": 0.97,
    "f1": 0.96
  },
  "evidence_refs": ["rule:RULE-0001"],
  "gaps": []
}
```

See `REFERENCE.md` for the full normalization rule set and the precision/recall/accuracy/F1 definitions used across this framework.
