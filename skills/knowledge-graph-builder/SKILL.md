---
name: knowledge-graph-builder
version: 2.0.0
description: >
  Writes confirmed business rules and evidence (heuristic checks,
  rule-engine links, AI-semantic checks, parity-check results) as RDF/Turtle
  triples into context/knowledge-graph.ttl, and syncs the graph into Neo4j
  for querying. Trigger when a candidate rule has been confirmed by a human
  reviewer, or when any other skill has produced evidence that needs to be
  persisted back to the graph.
inputs:
  - confirmed_rule (from human review of a legacy-rule-extraction candidate), or
  - JSON skill message (per context/schemas/skill-message.schema.json) from
    heuristic-validation, ai-semantic-validation, or parity-evaluation
outputs:
  - updated context/knowledge-graph.ttl (git-tracked diff)
  - Neo4j graph in sync with the TTL via context/neo4j/import.cypher
  - JSON message per context/schemas/skill-message.schema.json confirming the write
requires_human_review: true for new BusinessRule nodes; false for evidence write-backs from other skills
depends_on: []
output_schema: ../../context/schemas/skill-message.schema.json
reference: REFERENCE.md
---

# Skill: Knowledge Graph Builder

## What this skill does

This is the only skill permitted to write to `context/knowledge-graph.ttl`. Every other skill produces evidence; this skill turns that evidence into a persisted, queryable graph node or edge. Centralizing writes here, rather than letting each skill touch the TTL directly, keeps the ontology consistent instead of drifting into six slightly different shapes.

## Procedure

1. **New rule nodes require a human-confirmed input.** Never write a `BusinessRule` node from a `legacy-rule-extraction` candidate directly. A human reviewer confirms the rule description, tolerance, and target mapping first.
2. **Evidence nodes (HeuristicCheck, RuleEngineImpl, AISemanticCheck, ParityCheck) can be written automatically** by this skill when called by another skill reporting a completed run. These are evidence records, not claims about the business, so they don't require the same human gate.
3. **TTL is the source of truth; Neo4j is derived.** Write the triple to `knowledge-graph.ttl` first, commit it, then re-run `context/neo4j/import.cypher` to sync. Never edit the Neo4j graph directly and let it diverge from the git-tracked file.
4. **Every write includes a timestamp.** `lastVerified` for rule confirmations, `executedOn` for evidence nodes. Staleness detection depends on these being accurate, not defaulted.
5. **Removing or superseding a node is a visible diff, not a silent overwrite.** If a rule's understanding changes, add a note and update the node in place so the git history shows what changed and why. Don't delete and re-add silently.
6. **This skill consumes the JSON message another skill emits, and writes back only the `result` and `evidence_refs` fields as triples.** It does not re-derive or reinterpret the finding. If the incoming message's `confidence.band` is `low`, write the node anyway (evidence is evidence) but carry the confidence forward into the triple so a graph query can surface low-confidence evidence separately from high-confidence evidence. One mechanical exception: JSON field names are `snake_case` (per the schema) and RDF predicates are `camelCase` (per the ontology in `REFERENCE.md`). Translating `coincidental_match_risk` to `mig:coincidentalMatchRisk` on write is serialization, not reinterpretation; the value and meaning must carry over unchanged.

## Output message

Confirms the write, per `context/schemas/skill-message.schema.json`:

```json
{
  "skill": "knowledge-graph-builder",
  "skill_version": "2.0.0",
  "module": "interest-accrual",
  "run_id": "run-2026-07-17T09:41:00Z-interest-accrual",
  "timestamp": "2026-07-17T09:44:30Z",
  "status": "pass",
  "confidence": {
    "value": 1.0,
    "band": "high",
    "basis": "TTL write and Neo4j re-sync both completed with no constraint violations.",
    "source": "calibrated"
  },
  "result": {
    "nodes_written": ["rule:PCHK-0003", "rule:ASEM-0002"],
    "sync_status": "ok"
  },
  "evidence_refs": ["rule:RULE-0001"],
  "gaps": []
}
```

If the Neo4j sync step fails while the TTL write succeeds, `status` is `partial`, `confidence.value` drops accordingly, and `gaps` states plainly that the graph in git and the graph in Neo4j are currently out of sync. Never treat a partial write as complete.

See `REFERENCE.md` for the full ontology (classes, properties, required fields per node type) and the Neo4j sync commands.
