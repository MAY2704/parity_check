---
description: 'Run the full three-phase evaluation pipeline (read input, execute process, generate output) for one artifact under test.'
mode: agent
---

Evaluate `${input:module}` end to end.

**Phase 1 — Read Input**
1. Load the artifact from `input/artifacts/${input:module}/`.
2. Query `context/knowledge-graph.ttl` (via `context/neo4j/queries.cypher`, context-assembly query) for the matching `BusinessRule` node.
3. If missing or stale, stop and report the gap as the result. Do not infer the rule.
4. Report existing evidence coverage (heuristic check / rule-engine oracle / prior parity check / prior semantic check) before proceeding.

**Phase 2 — Execute Process**
5. Run `heuristic-validation`. Stop on a `block`-severity failure.
6. Run `parity-evaluation`: normalize, dual-compare against the golden dataset and the rule-engine oracle, classify discrepancies, compute precision/recall/accuracy/F1.
7. Run `ai-semantic-validation`: independent blind read of the artifact's logic, compare against the documented rule and against the parity result, flag `coincidental_match_risk` explicitly if relevant.
8. Run `knowledge-graph-builder` to write all evidence nodes back to the graph and re-sync Neo4j.
9. Run `confidence-scoring` to compute the six-component score, applying overrides — remember that `coincidental_match_risk: true` caps the result at Low regardless of the numeric match rate.

**Phase 3 — Generate Output**
10. Write the full report to `output/reports/${input:module}-{date}.md`.
11. Append a compact entry to `output/evaluation-log.md`.
12. Output: `PASS / FAIL / NEEDS-REVIEW — confidence {score}/100 ({band}) — precision {p} / recall {r} / accuracy {a} / F1 {f1}`.

Do not skip a phase or run stages out of order, even if an earlier stage looks like it obviously passed.
