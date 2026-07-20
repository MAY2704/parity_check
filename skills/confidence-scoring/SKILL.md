---
name: confidence-scoring
version: 2.1.0
description: >
  Aggregates evidence from every other skill's JSON message into a single,
  transparent confidence score with a visible component breakdown, never a
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

1. Pull the JSON message most recently logged for the module from each source skill. Never estimate a component with no logged message behind it.
2. Apply the weights in `REFERENCE.md` to compute the weighted composite from each message's `result` fields. If `parity-evaluation` reports null metrics (a degenerate clean run — see its `REFERENCE.md`), apply the null-metric fallbacks in `REFERENCE.md` §"Null-metric fallbacks"; never substitute 1.0 for a null.
3. **Enforce the propagation rule** (full rationale: `REFERENCE.md` §"Self-reported confidence is a downgrade-only input"). `aligned` adds no bonus beyond what Semantic Agreement already scores; `partially-aligned`, `contradicts`, or `coincidental_match_risk: true` triggers the full downgrade regardless of the self-reported confidence value attached.
4. **Check the four override conditions in `REFERENCE.md`** before finalizing. Any one caps the composite at Low regardless of the weighted total, even at 100% parity accuracy.
5. Report all six components individually, the override applied (if any), the composite, and the band, as a JSON message per the schema, plus a human-readable rendering for the report. Never output a single number with no breakdown.
6. Hand off to the reporting step (see the agent's `run-full-evaluation` prompt) to write the score into `output/reports/`.

## Output message

```json
{
  "skill": "confidence-scoring",
  "skill_version": "2.1.0",
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
