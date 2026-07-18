---
description: 'Scan a scope of the knowledge graph for regression blind spots and report recall exposure: nodes missing a heuristic check, rule-engine oracle, or parity check.'

---

Scan `${input:scope}` for regression blind spots.

1. Query `context/neo4j/queries.cypher` (blind-spot query) for every `BusinessRule` node in scope.
2. A node is a blind spot if it's missing a linked `HeuristicCheck`, `RuleEngineImpl`, or `ParityCheck`. Any one missing counts, not just all three.
3. Rank by exposure: financial/regulatory-reporting nodes first, cosmetic/informational nodes last.
4. Compute **recall exposure**: the percentage of nodes in scope with zero coverage across all three checks. Report this as a standalone figure.
5. Append new findings to `checklists/regression-blindspot-checklist.md` with `Owner: unassigned` and today's date.
6. Output: total nodes scanned, blind spots found, recall exposure %, newly logged findings.

This prompt only finds and logs gaps. It never closes one, and it never invokes `legacy-rule-extraction` or `knowledge-graph-builder` to fill a gap on its own authority.
