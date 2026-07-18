# Parity Checklist & Confidence Rubric

## Pass criteria per module

- [ ] Context check run: required knowledge-graph node present and fresh
- [ ] **Heuristic check** run and cleared before any comparison
- [ ] **Normalization** applied to artifact output, golden dataset, and rule-engine output alike
- [ ] **Dual comparison** run against both the golden dataset and the rule-engine oracle (or the single-oracle gap explicitly reported)
- [ ] Golden dataset covers real historical production data, not synthetic samples only
- [ ] Every output field compared, not a sample of fields
- [ ] Every discrepancy classified: tolerance-acceptable / transformation-error / legacy-defect-now-fixed
- [ ] Oracle disagreement (golden dataset vs. rule engine) noted explicitly, not silently resolved
- [ ] Precision, recall, accuracy, and F1 all computed and logged, not just a raw match rate
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
