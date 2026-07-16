# Evaluation Log

The audit trail. Every full evaluation run appends an entry here — nothing is assessed off the record. Newest entries at the top.

---

## Entry: RULE-0001 / interest-accrual — 2026-07-16

- **Phase 1 (Read Input):** Node found, fresh. Existing coverage: HeuristicCheck ✓, RuleEngineImpl ✓, prior ParityCheck (2026-07-01)
- **Heuristic check:** Cleared (`accrued_interest >= 0 AND <= principal * 0.15`)
- **Normalization:** Applied (0.005 tolerance, ISO 8601 dates)
- **Dual comparison:** Matches golden dataset AND rule-engine oracle; oracles agree with each other. 0 discrepancies.
- **Precision / Recall / Accuracy / F1:** 1.0 / 0.92 / 0.97 / 0.96
- **AI semantic validation:** Independent read aligned with documented rule. `coincidental_match_risk: false`
- **Blind-spot coverage:** 100%
- **Confidence score:** 15/15 + 24/25 + 20/20 + 20/20 + 9.2/10 + 6/10 (pending review) ≈ **94/100 — High**
- **Report:** `output/reports/interest-accrual-2026-07-16.md`
- **Reviewer:** unassigned
- **Decision:** Ready for sign-off — pending reviewer assignment

---

## Entry: RULE-0002 / fee-waiver — 2026-07-10

- **Phase 1 (Read Input):** Node found, but no HeuristicCheck, RuleEngineImpl, or ParityCheck linked
- **Heuristic check:** Not run — no `HeuristicCheck` node exists
- **Normalization / Dual comparison:** Not run — no golden dataset and no rule-engine implementation exist for this node
- **Precision / Recall / Accuracy / F1:** N/A / 0.0 / N/A / N/A — recall counted as zero, not unknown
- **AI semantic validation:** Not run — blocked on missing evidence chain
- **Blind-spot coverage:** 0% — flagged to `checklists/regression-blindspot-checklist.md`
- **Confidence score:** Override applied — Blind-Spot Coverage = 0, Recall Floor = 0 → capped **Low**
- **Reviewer:** unassigned
- **Decision:** Not eligible for transformation work until a heuristic check, rule-engine implementation, and golden dataset exist

---

<!-- New entries go above this line. Do not delete prior entries — this file is the audit trail. -->
