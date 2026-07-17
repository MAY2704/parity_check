---
description: 'Compute the six-component confidence score for a module from logged evidence, via the confidence-scoring skill.'
---

Run the `confidence-scoring` skill for `${input:module}`.

1. Pull Context Completeness, Parity F1, Semantic Agreement, Blind-Spot Coverage, Recall Floor, and Review Status from the most recent logged evidence for this module — via `context/neo4j/queries.cypher` and `output/evaluation-log.md`. Do not estimate a component with no logged evidence.
2. Apply the weights and overrides in `skills/confidence-scoring/REFERENCE.md`.
3. Output all six components individually, the weighted composite, the band, and which override (if any) applied — never a bare number.
