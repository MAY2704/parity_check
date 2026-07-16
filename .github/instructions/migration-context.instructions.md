---
applyTo: "src/migration/**"
---

# Migration Module Context

When working in this path, before generating or modifying any transformation logic:

- Query the knowledge graph (`context/knowledge-graph.ttl` / Neo4j) for the `BusinessRule` node tagged to this module. Use its description, not the raw legacy source, as the source of truth once a node exists.
- If no node exists yet, say so explicitly and recommend the `legacy-rule-extraction` skill be run and the result human-confirmed — do not transform undocumented logic silently.
- If a node has no linked `RuleEngineImpl`, flag that a deterministic second oracle is missing before treating any parity result as strong evidence.
- Never state that transformed logic is "equivalent" to legacy behavior on a match rate alone — an `ai-semantic-validation` check confirming the logic itself, not just the sampled output, is required first.
- Keep context small: load only the node(s) relevant to the current file, not the full graph or the full legacy module.
