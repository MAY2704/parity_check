---
name: knowledge-graph-builder
version: 1.3.0
description: >
  Writes confirmed business rules and evidence (heuristic checks,
  rule-engine links, AI-semantic checks, parity-check results) as RDF/Turtle
  triples into context/knowledge-graph.ttl, and syncs the graph into Neo4j
  for querying. Trigger when a candidate rule has been confirmed by a human
  reviewer, or when any other skill has produced evidence that needs to be
  persisted back to the graph.
inputs:
  - confirmed_rule (from human review of a legacy-rule-extraction candidate), or
  - evidence_record (from heuristic-validation, ai-semantic-validation, or parity-evaluation)
outputs:
  - updated context/knowledge-graph.ttl (git-tracked diff)
  - Neo4j graph in sync with the TTL via context/neo4j/import.cypher
requires_human_review: true for new BusinessRule nodes; false for evidence write-backs from other skills
depends_on: []
reference: REFERENCE.md
---

# Skill: Knowledge Graph Builder

## What this skill does

This is the only skill permitted to write to `context/knowledge-graph.ttl`. Every other skill produces evidence; this skill is what turns that evidence into a persisted, queryable graph node or edge. Centralizing writes here — rather than letting each skill touch the TTL directly — is what keeps the ontology consistent instead of drifting into six slightly different shapes.

## Procedure

1. **New rule nodes require a human-confirmed input.** Never write a `BusinessRule` node from a `legacy-rule-extraction` candidate directly — a human reviewer confirms the rule description, tolerance, and target mapping first.
2. **Evidence nodes (HeuristicCheck, RuleEngineImpl, AISemanticCheck, ParityCheck) can be written automatically** by this skill when called by another skill reporting a completed run — these are evidence records, not claims about the business, so they don't require the same human gate.
3. **TTL is the source of truth; Neo4j is derived.** Write the triple to `knowledge-graph.ttl` first, commit it, then re-run `context/neo4j/import.cypher` to sync. Never edit the Neo4j graph directly and let it diverge from the git-tracked file.
4. **Every write includes a timestamp.** `lastVerified` for rule confirmations, `executedOn` for evidence nodes — staleness detection depends on these being accurate, not defaulted.
5. **Removing or superseding a node is a visible diff, not a silent overwrite.** If a rule's understanding changes, add a note and update the node in place so the git history shows what changed and why — don't delete and re-add silently.

See `REFERENCE.md` for the full ontology (classes, properties, required fields per node type) and the Neo4j sync commands.
