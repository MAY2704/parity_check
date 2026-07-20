# Parity Checklist & Confidence Rubric

## Pass criteria per module

- [ ] Context check run: required knowledge-graph node present and fresh
- [ ] **Heuristic check** run and cleared before any comparison
- [ ] **Deterministic harness used**: numbers come from `scripts/parity_eval.py` output (seed recorded), not from a model following prose
- [ ] **Normalization** applied to artifact output, golden dataset, and rule-engine output alike
- [ ] **Dual comparison** run against both the golden dataset and the rule-engine oracle (or the single-oracle gap explicitly reported)
- [ ] Golden dataset covers real historical production data, not synthetic samples only — and `dataset_adequacy` (volume / range / boundary / provenance) reported, not assumed
- [ ] **Differential fuzz + boundary cases** run against the rule-engine oracle over declared `input_domains` (or the gap explicitly reported when no engine/domains exist)
- [ ] **Metamorphic property checks** run for every property declared on the rule (or none declared, stated explicitly)
- [ ] Every output field compared, not a sample of fields
- [ ] Every discrepancy classified: tolerance-acceptable / transformation-error / legacy-defect-now-fixed — reclassifications recorded in `review.json` by a human, never defaulted
- [ ] Oracle disagreement (golden dataset vs. rule engine) noted explicitly, not silently resolved
- [ ] Precision, recall, accuracy, and F1 computed and logged per the degenerate-case conventions (null when undefined, never a substituted 1.0), alongside match_rate and oracle_coverage
- [ ] **AI semantic validation run**: artifact's actual logic independently read and compared against the documented rule, not just its output
- [ ] `coincidental_match_risk` explicitly reported true or false
- [ ] Financial variance is zero above the documented rounding rule
- [ ] Result written to `output/evaluation-log.md` and a full report to `output/reports/`

A module cannot be marked PASS if any box above is unchecked, regardless of how clean the diff looks.

## Confidence score rubric

See `skills/confidence-scoring/REFERENCE.md` for the authoritative weighting table and override rules, summarized here:

| Component | Weight |
|---|---|
| Context Completeness | 15% |
| Parity F1 | 25% |
| Semantic Agreement | 20% |
| Blind-Spot Coverage | 20% |
| Recall Floor | 10% |
| Review Status | 10% |

**Overrides that cap the score at Low regardless of the weighted total:** Context Completeness = 0; Blind-Spot Coverage = 0 on a financial/regulatory rule; Recall Floor = 0; `coincidental_match_risk: true`. Rationale for each: `skills/confidence-scoring/REFERENCE.md`.
