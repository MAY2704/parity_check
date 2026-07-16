---
description: 'Scan a scope of the knowledge graph for regression blind spots and report recall exposure — nodes with no linked heuristic check, rule-engine oracle, or parity check.'
mode: agent
---

Scan `${input:scope}` for regression blind spots.

1. Query `parity/neo4j/queries.cypher` (blind-spot query) for every `BusinessRule` node in scope.
2. For each node, check for a linked `HeuristicCheck`, a linked `RuleEngineImpl`, and a linked `ParityCheck`. Any node missing one or more is a blind spot.
3. Do not treat a passing parity check as evidence of heuristic or rule-engine coverage, or vice versa — each is separate evidence and all three are required for a node to count as covered.
4. Rank the resulting list by exposure: financial and regulatory-reporting nodes first, cosmetic/informational nodes last.
5. Compute **recall exposure** for the scope: the percentage of nodes with zero coverage across all three checks. Report this as a standalone figure, separate from the blind-spot list itself.
6. Append each new finding to `parity/checklists/regression-blindspot-checklist.md` with `Owner: unassigned` and today's date.
7. Output a summary: total nodes scanned, number of blind spots found, recall exposure %, and number newly added to the checklist.

Do not attempt to close any blind spot in this run — this prompt only finds, scores, and logs gaps.
