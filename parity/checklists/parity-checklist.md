# Parity Checklist & Confidence Rubric

## Parity check — pass criteria per module

- [ ] Context check run — all required knowledge-graph nodes present and fresh
- [ ] Golden dataset covers real historical production data, not synthetic samples only
- [ ] Every output field compared, not a sample of fields
- [ ] Every discrepancy classified: tolerance-acceptable / transformation-error / legacy-defect-now-fixed
- [ ] Financial variance is zero above the documented rounding rule
- [ ] Result written to `parity/evaluation-log.md`

A module cannot be marked PASS if any box above is unchecked, regardless of how clean the diff looks.

## Confidence score rubric

| Component | Weight | What it measures | Source of evidence |
|---|---|---|---|
| Context Completeness | 25% | % of required graph nodes present & fresh | `knowledge-graph.md` |
| Parity Match | 35% | % of golden-dataset fields matching within tolerance | latest `*run-parity` entry |
| Blind-Spot Coverage | 25% | % of relevant nodes with linked test + parity check | latest `*scan-blindspots` entry |
| Review Status | 15% | 0 unreviewed / 60 pending sign-off / 100 signed off | `evaluation-log.md` |

**Override:** any single component at 0 caps the composite in the Low band. A high average never overrides one critical gap.

**Bands:**
- **90–100 High** — eligible for sign-off / cutover track
- **60–89 Medium** — targeted remediation required before sign-off
- **< 60 Low** — not eligible; returns to remediation queue

The score is always reported with its four components visible — never as a single number with no breakdown. A confidence score nobody can trace back to evidence is exactly the kind of unearned trust this framework exists to prevent.
