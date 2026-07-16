# Parity Checklist & Confidence Rubric

## Parity check — pass criteria per module

- [ ] Context check run — all required knowledge-graph nodes present and fresh (queried from Neo4j / `knowledge-graph.ttl`)
- [ ] **Stage 1 — heuristic pass** run and cleared before any comparison
- [ ] **Stage 2 — normalization** applied to AI output, golden dataset, and rule-engine output alike
- [ ] **Stage 3 — dual comparison** run against both the golden dataset and the rule-engine oracle
- [ ] Golden dataset covers real historical production data, not synthetic samples only
- [ ] Every output field compared, not a sample of fields
- [ ] Every discrepancy classified: tolerance-acceptable / transformation-error / legacy-defect-now-fixed
- [ ] Oracle disagreement (golden dataset vs. rule engine) noted explicitly, not silently resolved
- [ ] Precision, recall, and F1 computed and logged, not just a raw match rate
- [ ] Financial variance is zero above the documented rounding rule
- [ ] Result written to `parity/evaluation-log.md`

A module cannot be marked PASS if any box above is unchecked, regardless of how clean the diff looks.

## Confidence score rubric

| Component | Weight | What it measures | Source of evidence |
|---|---|---|---|
| Context Completeness | 20% | % of required graph nodes present & fresh | Neo4j context-assembly query |
| Parity Match (F1) | 30% | Harmonic mean of precision and recall on discrepancy classification, not raw match rate alone | latest `*run-parity` entry |
| Blind-Spot Coverage | 25% | % of relevant nodes with linked heuristic check + rule-engine oracle + parity check | latest `*scan-blindspots` entry |
| Recall Floor | 10% | Recall specifically, isolated from precision — a module can have perfect precision and still be dangerously under-covered | `*run-parity` entry |
| Review Status | 15% | 0 unreviewed / 60 pending sign-off / 100 signed off | `evaluation-log.md` |

**Override:** any single component at 0 caps the composite in the Low band. A high average never overrides one critical gap.

### Why precision and recall are scored separately, not folded into one number

Precision is cheap to inflate — flag less, and precision goes up on paper while real defects slide through unflagged. Recall is what actually costs effort to earn, and it's the number a demo will never volunteer, because a high-recall system finds more of its own problems, which looks worse in a two-minute walkthrough than a system that simply stopped looking. Scoring Recall Floor as its own component stops a strong precision number from quietly buying a Medium or High confidence band on a module that's barely been checked at all.

**Bands:**
- **90–100 High** — eligible for sign-off / cutover track
- **60–89 Medium** — targeted remediation required before sign-off
- **< 60 Low** — not eligible; returns to remediation queue

The score is always reported with its four components visible — never as a single number with no breakdown. A confidence score nobody can trace back to evidence is exactly the kind of unearned trust this framework exists to prevent.
