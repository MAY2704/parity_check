---
name: confidence-scoring
version: 2.0.0
description: >
  Aggregates evidence from every other skill's JSON message into a single,
  transparent confidence score with a visible component breakdown — never a
  bare number. Enforces the propagation rule: self-reported confidence
  (from ai-semantic-validation) may only lower the composite, never raise
  it. Trigger as the final step before writing a report, once
  heuristic-validation, parity-evaluation, and ai-semantic-validation have
  all produced results for the module.
inputs:
  - JSON messages (per context/schemas/skill-message.schema.json) from
    heuristic-validation, parity-evaluation, ai-semantic-validation, and
    knowledge-graph-builder for this module
  - review_status (from output/evaluation-log.md)
depends_on: [parity-evaluation, ai-semantic-validation, knowledge-graph-builder]
outputs:
  - JSON message per context/schemas/skill-message.schema.json, with
    result.component_breakdown showing all six components individually
output_schema: ../../context/schemas/skill-message.schema.json
reference: REFERENCE.md
---

# Skill: Confidence Scoring

## What this skill does

Arithmetic over evidence, not a model and not a judgment call. Every input to this skill was produced and logged by another skill; this skill's only job is to combine them per a fixed, published rubric and report the breakdown alongside the total, so a reviewer can re-derive the score by hand from the evaluation log.

## Procedure

1. Pull the JSON message most recently logged for the module from each source skill — never estimate a component with no logged message behind it.
2. Apply the weights in `REFERENCE.md` to compute the weighted composite from each message's `result` fields.
3. **Enforce the propagation rule.** `ai-semantic-validation`'s message has `confidence.source: "self-reported"`. If its `agreement_level` is `aligned`, do not add score beyond what the Semantic Agreement component already awards for that classification — a high self-reported confidence value does not add bonus weight on top. If `agreement_level` is `partially-aligned` or `contradicts`, or `coincidentalMatchRisk` is true, apply the full downgrade the rubric specifies, regardless of the self-reported confidence value attached to that finding — a *low-confidence* bad finding still triggers the override, because the finding itself, not the skill's certainty about it, is what matters here.
4. **Check override conditions before finalizing.** Any of the following caps the composite at the Low band regardless of the weighted total:
   - Context Completeness = 0
   - Blind-Spot Coverage = 0 on a financial or regulatory-reporting rule
   - Recall Floor = 0
   - `ai-semantic-validation` reported `coincidental_match_risk: true`, **even if parity accuracy is 100%**
5. Report all six components individually, the override applied (if any), the composite, and the band, as a JSON message per the schema, plus a human-readable rendering for the report. Never output a single number with no breakdown.
6. Hand off to the reporting step (see the agent's `run-full-evaluation` prompt) to write the score into `output/reports/`.

## Output message

```json
{
  "skill": "confidence-scoring",
  "skill_version": "2.0.0",
  "module": "interest-accrual",
  "run_id": "run-2026-07-17T09:41:00Z-interest-accrual",
  "timestamp": "2026-07-17T09:45:00Z",
  "status": "pass",
  "confidence": {
    "value": 0.94,
    "band": "high",
    "basis": "Composite of all six weighted components; no override triggered.",
    "source": "calibrated"
  },
  "result": {
    "component_breakdown": {
      "context_completeness": 15,
      "parity_f1": 24,
      "semantic_agreement": 20,
      "blind_spot_coverage": 20,
      "recall_floor": 9.2,
      "review_status": 6
    },
    "composite": 94.2,
    "band": "High",
    "override_applied": null
  },
  "evidence_refs": ["rule:RULE-0001"],
  "gaps": []
}
```

See `REFERENCE.md` for the full weighting table and the reasoning behind each override.
