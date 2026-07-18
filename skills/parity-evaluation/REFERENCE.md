# Reference: Parity Evaluation Metrics

Normalization rules themselves live in `context/normalization-rules.md`. This file covers the comparison methodology and the metric formulas, the part that doesn't change per module.

## Field-level classification

Every compared field, for every record, is classified into exactly one of:

| Class | Definition |
|---|---|
| **True Positive (TP)** | Flagged as a discrepancy by the comparison, and confirmed on review to be a real transformation error |
| **False Positive (FP)** | Flagged as a discrepancy, but reclassified as `tolerance-acceptable` or `legacy-defect-now-fixed`, not a real defect |
| **False Negative (FN)** | Not flagged by the comparison, but later confirmed to be a real defect: either discovered downstream (an escaped defect) or, by design, any field belonging to a rule with no oracle coverage at all (see below) |
| **True Negative (TN)** | Not flagged, and confirmed correct: the field matched across the available oracles and stayed matched |

**Coverage rule:** a `BusinessRule` node with no linked `RuleEngineImpl` and no `ParityCheck` contributes its fields to **FN**, not to an excluded/unknown bucket. Treating an unchecked field as a missed defect is what stops an unevaluated module from silently scoring as "no discrepancies found."

## Formulas

```
Precision = TP / (TP + FP)
Recall    = TP / (TP + FN)
Accuracy  = (TP + TN) / (TP + TN + FP + FN)
F1        = 2 × (Precision × Recall) / (Precision + Recall)
```

- **Precision** answers: of what we flagged, how much was real. Cheap to inflate; flag less and precision rises even as real defects go uncaught.
- **Recall** answers: of what's actually wrong, how much did we catch. This is the number that costs real effort. Every additional oracle, every additional heuristic, every rule that gets a `RuleEngineImpl` written for it, raises recall. Nothing raises it for free.
- **Accuracy** is useful as a single-glance module health number but is the metric most easily distorted by class imbalance: a module with very few real defects can show high accuracy while still missing most of them. Never report accuracy without precision and recall alongside it.
- **F1** is the balance point between precision and recall, used as the "Parity Match" component in confidence scoring rather than the raw match rate, so a system can't game the score by only flagging the easy, obvious discrepancies.

## Worked example

Module has 40 fields checked. 3 are flagged as discrepancies; 2 of those are confirmed real transformation errors (TP=2), 1 is reclassified as tolerance-acceptable (FP=1). Of the 37 not flagged, 35 are confirmed correct (TN=35) and 2 belong to a sibling rule with no rule-engine oracle, so they count as missed (FN=2).

```
Precision = 2 / (2 + 1) = 0.67
Recall    = 2 / (2 + 2) = 0.50
Accuracy  = (2 + 35) / 40 = 0.925
F1        = 2 × (0.67 × 0.50) / (0.67 + 0.50) = 0.57
```

Accuracy alone (92.5%) would look like a clean module. Recall (50%) tells the real story: the module is only catching half of what it should, and the two uncovered fields, not a low match rate, are the finding that actually matters here.

## Versioning note for this skill

- **PATCH**: a corrected formula implementation, a fixed rounding bug in the calculation itself.
- **MINOR**: a new field classification added (e.g., distinguishing severity within transformation-error).
- **MAJOR**: a change to the coverage rule (how uncovered rules count toward FN) or to which formulas are reported, since `confidence-scoring` consumes these values directly.
