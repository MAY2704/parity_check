# Evaluation Log

The audit trail. Every full evaluation run appends an entry here; nothing is assessed off the record. Newest entries at the top.

---

## Entry: RULE-DEMO-001 / interest-accrual-demo — 2026-07-18 — SYNTHETIC DEMO RUN

- **Purpose:** Pipeline walkthrough after fixing the `coincidental_match_risk` casing mismatch, the `depends_on` ambiguity, and the direct-handoff wording in `parity-evaluation/SKILL.md`. Artifact and rule are self-authored demo data, not a real migration finding. See disclaimer in `output/reports/interest-accrual-demo-2026-07-18.md`.
- **Phase 1 (Read Input):** Node found (`RULE-DEMO-001`, demo-only, operator-confirmed). Existing coverage: HeuristicCheck ✓, RuleEngineImpl ✓, golden dataset ✓ (5 synthetic cases). No prior ParityCheck/AISemanticCheck; first evaluation.
- **Heuristic check:** Cleared (`accrued_interest >= 0 AND <= principal * 0.15`), brand-new heuristic, confidence 0.6/medium.
- **Normalization:** Applied (0.005 tolerance, half-up 2-decimal rounding).
- **Dual comparison:** Matches golden dataset AND rule-engine oracle; oracles agree with each other. 0 discrepancies. Gap noted: no sampled case exceeds 45 days.
- **Precision / Recall / Accuracy / F1:** 1.0 / 1.0 / 1.0 / 1.0
- **AI semantic validation:** `partially-aligned`; artifact silently caps the day-count factor at 45 days, undocumented in the rule. `coincidental_match_risk: true`.
- **Knowledge-graph write:** TTL updated (`PCHK-DEMO-001`, `ASEM-DEMO-001`); Neo4j sync **not executed**, no live instance connected this session.
- **Confidence score:** 15/15 + 25/25 + 10/20 + 20/20 + 10/10 + 0/10 = 80.0 weighted, **overridden to Low** by `coincidental_match_risk: true`, despite 100% parity match.
- **Report:** `output/reports/interest-accrual-demo-2026-07-18.md`
- **Reviewer:** unassigned
- **Decision:** FAIL, not eligible for cutover. Route to a named human owner to confirm whether the 45-day cap is intended (then document it and extend the golden dataset) or is a defect (then remove it).

---

## Entry: RULE-0001 / interest-accrual — 2026-07-16

- **Phase 1 (Read Input):** Node found, fresh. Existing coverage: HeuristicCheck ✓, RuleEngineImpl ✓, prior ParityCheck (2026-07-01)
- **Heuristic check:** Cleared (`accrued_interest >= 0 AND <= principal * 0.15`)
- **Normalization:** Applied (0.005 tolerance, ISO 8601 dates)
- **Dual comparison:** Matches golden dataset AND rule-engine oracle; oracles agree with each other. 0 discrepancies.
- **Precision / Recall / Accuracy / F1:** 1.0 / 0.92 / 0.97 / 0.96
- **AI semantic validation:** Independent read aligned with documented rule. `coincidental_match_risk: false`
- **Blind-spot coverage:** 100%
- **Confidence score:** 15/15 + 24/25 + 20/20 + 20/20 + 9.2/10 + 6/10 (pending review) ≈ **94/100, High**
- **Report:** `output/reports/interest-accrual-2026-07-16.md`
- **Reviewer:** unassigned
- **Decision:** Ready for sign-off, pending reviewer assignment

---

## Entry: RULE-0002 / fee-waiver — 2026-07-10

- **Phase 1 (Read Input):** Node found, but no HeuristicCheck, RuleEngineImpl, or ParityCheck linked
- **Heuristic check:** Not run; no `HeuristicCheck` node exists
- **Normalization / Dual comparison:** Not run; no golden dataset and no rule-engine implementation exist for this node
- **Precision / Recall / Accuracy / F1:** N/A / 0.0 / N/A / N/A. Recall counted as zero, not unknown.
- **AI semantic validation:** Not run; blocked on missing evidence chain
- **Blind-spot coverage:** 0%, flagged to `checklists/regression-blindspot-checklist.md`
- **Confidence score:** Override applied. Blind-Spot Coverage = 0, Recall Floor = 0, capped **Low**.
- **Reviewer:** unassigned
- **Decision:** Not eligible for transformation work until a heuristic check, rule-engine implementation, and golden dataset exist

---

<!-- New entries go above this line. Do not delete prior entries; this file is the audit trail. -->
