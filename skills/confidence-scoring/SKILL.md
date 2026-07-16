---
name: confidence-scoring
version: 1.1.0
description: >
  Aggregates evidence from every other skill into a single, transparent
  confidence score with a visible component breakdown — never a bare
  number. Trigger as the final step before writing a report, once
  heuristic-validation, parity-evaluation, and ai-semantic-validation have
  all produced results for the module.
inputs:
  - context_completeness (from knowledge-graph-builder / graph query)
  - parity_result (from parity-evaluation: precision, recall, accuracy, F1)
  - semantic_result (from ai-semantic-validation: agreement_level, coincidental_match_risk)
  - blind_spot_coverage (from a graph query for linked evidence nodes)
  - review_status (from output/evaluation-log.md)
depends_on: [parity-evaluation, ai-semantic-validation, knowledge-graph-builder]
outputs:
  - composite_score: 0-100
  - band: High / Medium / Low
  - component_breakdown: all six components shown individually
reference: REFERENCE.md
---

# Skill: Confidence Scoring

## What this skill does

Arithmetic over evidence, not a model and not a judgment call. Every input to this skill was produced and logged by another skill; this skill's only job is to combine them per a fixed, published rubric and report the breakdown alongside the total, so a reviewer can re-derive the score by hand from the evaluation log.

## Procedure

1. Pull the five raw inputs from their source skills' most recent logged output for the module — never estimate a component that has no logged evidence behind it.
2. Apply the weights in `REFERENCE.md` to compute the weighted composite.
3. **Check override conditions before finalizing.** Any of the following caps the composite at the Low band regardless of the weighted total:
   - Context Completeness = 0
   - Blind-Spot Coverage = 0 on a financial or regulatory-reporting rule
   - Recall Floor = 0
   - `ai-semantic-validation` reported `coincidental_match_risk: true`, **even if parity accuracy is 100%**
4. Report all six components individually, the override applied (if any), the composite, and the band. Never output a single number with no breakdown.
5. Hand off to the reporting step (see the agent's `run-full-evaluation` prompt) to write the score into `output/reports/`.

See `REFERENCE.md` for the full weighting table and the reasoning behind each override.
