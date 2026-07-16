# Evaluation Log

The audit trail. Every `*run-parity`, `*scan-blindspots`, and `*score-confidence` run appends an entry here — nothing is assessed off the record. Newest entries at the top.

---

## Entry: RULE-0001 / interest-accrual.service.ts — 2026-07-14

- **Context check:** Complete — node fresh, heuristic check + rule-engine oracle + parity check all linked
- **Stage 1 — heuristic pass:** Cleared (`accrued_interest >= 0 AND <= principal * 0.15`)
- **Stage 2 — normalization:** Applied (rounding to 0.005 tolerance, ISO 8601 dates)
- **Stage 3 — dual comparison:** AI output matches golden dataset AND rule-engine oracle; oracles agree with each other
- **Discrepancies:** 0
- **Precision / Recall / F1:** 1.0 / 0.92 / 0.96
- **Blind-spot coverage:** 100% — heuristic, rule-engine, and parity check all linked
- **Confidence score:** 20/20 (context) + 30/30 (F1) + 25/25 (blind-spot) + 9.2/10 (recall floor) + 15/15 (review pending) = **~99/100 — High**
- **Reviewer:** unassigned
- **Decision:** Ready for sign-off — pending reviewer assignment

---

## Entry: RULE-0002 / fee-waiver.rules.ts — 2026-07-10

- **Context check:** Incomplete — node exists but has no linked heuristic check, rule-engine oracle, or parity check
- **Stage 1 — heuristic pass:** Not run — no `HeuristicCheck` node exists for this rule
- **Stage 2 — normalization:** N/A
- **Stage 3 — dual comparison:** Not run — no golden dataset and no rule-engine implementation exist for this node
- **Precision / Recall / F1:** N/A / 0.0 / N/A — recall counted as zero, not "unknown"
- **Blind-spot coverage:** 0% — flagged to `regression-blindspot-checklist.md`
- **Confidence score:** Override applied — Blind-Spot Coverage = 0 and Recall Floor = 0 → capped **Low**, regardless of other components
- **Reviewer:** unassigned
- **Decision:** Not eligible for transformation work until a golden dataset, heuristic check, and rule-engine implementation exist

---

<!-- New entries go above this line. Do not delete prior entries — this file is the audit trail. -->
