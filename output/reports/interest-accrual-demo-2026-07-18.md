---
**SYNTHETIC DEMO RUN.** `interest-accrual-demo` / `RULE-DEMO-001` is a demo module created to walk the ParityKit pipeline end to end. It duplicates RULE-0001's rule but is a self-authored artifact with a deliberately planted divergence; it is not a real migration finding. See `context/knowledge-graph.ttl` for the demo-data disclaimer on `RULE-DEMO-001`.

---

# Parity Evaluation Report — interest-accrual-demo — 2026-07-18

**run_id:** `run-2026-07-18T00:00:00Z-interest-accrual-demo`

## Phase 1 — Read Input

- Artifact located: `input/artifacts/interest-accrual-demo/interest-accrual.service.ts`
- Matching node: `rule:RULE-DEMO-001`, "Daily interest accrual, simple interest, 30/360 convention"
- Existing evidence coverage at start of run: `HeuristicCheck` ✓ (HCHK-DEMO-001), `RuleEngineImpl` ✓ (RENG-DEMO-001), golden dataset ✓ (5 synthetic cases). No prior `ParityCheck` or `AISemanticCheck`; this is a first-time evaluation.

## Phase 2 — Execute Process

### 1. heuristic-validation — PASS
Bound: `accrued_interest >= 0 AND accrued_interest <= principal * 0.15`, severity `block`. All 5 cases cleared with margin (largest ratio ~1% of principal). Confidence `calibrated`, 0.6/medium: brand-new heuristic, first run, no track record yet.

### 2. parity-evaluation — PASS
Normalized (0.005 tolerance, 2-decimal half-up rounding) then dual-compared against the golden dataset and the rule-engine oracle. Both oracles agree with each other and with the artifact on all 5 sampled cases. 0 discrepancies.

| Metric | Value |
|---|---|
| Precision | 1.0 |
| Recall | 1.0 |
| Accuracy | 1.0 |
| F1 | 1.0 |

Confidence `calibrated`, 0.9/high: both oracles present and in full agreement.

### 3. ai-semantic-validation — FLAGGED
Blind read of `interest-accrual.service.ts`, before consulting the documented rule:

> "Computes simple interest as `principal × annual_rate × (min(days_elapsed, 45) / 360)`, rounded half-up to 2 decimals. The day-count factor is silently capped at 45 regardless of the true elapsed days. No error, warning, or flag is raised when the cap engages."

Compared against RULE-DEMO-001 (no cap is part of the documented rule):

- **agreement_level: `partially-aligned`**: matches the documented formula exactly for `days_elapsed ≤ 45`; diverges on the boundary/exception path above it.
- **coincidental_match_risk: `true`**: none of the 5 golden-dataset cases exceed 45 days, so the 100% parity match above cannot detect this. The match is coincidental to what was sampled, not evidence the cap is safe.
- **Divergence:** artifact understates interest on any accrual period longer than 45 days, with no signal to the caller that this happened.

Confidence `self-reported`, 0.8/high: the artifact is a short, single-function file, so there's high confidence in the reading itself, independent of what it implies.

### 4. knowledge-graph-builder — PARTIAL
`ParityCheck` (PCHK-DEMO-001) and `AISemanticCheck` (ASEM-DEMO-001) nodes written to `context/knowledge-graph.ttl` and committed to the TTL, the source of truth. **Neo4j re-sync was not executed in this session; there is no live Neo4j instance connected.** The graph in git and the graph in Neo4j (if one exists in your environment) are out of sync until `context/neo4j/import.cypher` is run against it. This is reported as a gap per the fail-closed rule, not silently treated as a completed sync.

### 5. confidence-scoring — LOW (override applied)

| Component | Weight | Score |
|---|---|---|
| Context Completeness | 15% | 15.0 |
| Parity F1 | 25% | 25.0 |
| Semantic Agreement | 20% | 10.0 *(partially-aligned = 50%)* |
| Blind-Spot Coverage | 20% | 20.0 |
| Recall Floor | 10% | 10.0 |
| Review Status | 10% | 0.0 *(unreviewed)* |
| **Weighted composite** | | **80.0** *(would be Medium)* |

**Override applied: `coincidental_match_risk: true`, capping the result at Low regardless of the 80.0 weighted composite and the 100% parity match.** This is the scenario the override exists for (`confidence-scoring/REFERENCE.md`): every numeric signal looks clean, and the semantic read is the only thing that caught it.

## Phase 3 — Decision

- **Report:** this file, plus full JSON message chain in `output/reports/interest-accrual-demo-2026-07-18.json`
- **Logged:** `output/evaluation-log.md`
- **Reviewer:** unassigned
- **Decision:** Not eligible for cutover. Recommend either (a) confirming with the domain SME whether the 45-day cap is intended business behavior and, if so, adding it to `RULE-DEMO-001`'s documented description and extending the golden dataset with a case beyond 45 days, or (b) treating it as a defect and removing the cap. Either way, the fix is a rule/tolerance decision for a named human owner, not something this pipeline resolves on its own.

**PASS / FAIL / NEEDS-REVIEW — confidence 80/100 weighted, capped to Low by coincidental-match-risk override — precision 1.0 / recall 1.0 / accuracy 1.0 / F1 1.0**

**Status: FAIL.** Not because any single check failed, but because the mandatory semantic cross-check found a real, undocumented divergence that the numeric oracles cannot see. Decision owner: named human reviewer (unassigned) per `BEST_PRACTICES.md` §6. This report is evidence for that person, not a sign-off.
