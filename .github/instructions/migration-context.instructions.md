---
applyTo: "src/migration/**"
---

# Migration Module Context

When working in this path, before generating or modifying any transformation logic:

- Query `parity/knowledge-graph.md` for nodes tagged to this module. Use the node's rule definition, not the raw legacy source, as the source of truth once a node exists.
- If no node exists yet for the logic you're touching, say so explicitly and propose a node be created — do not transform undocumented logic silently.
- Never state that transformed logic is "equivalent" to legacy behavior without a `parity/evaluation-log.md` entry to point to.
- Keep context small: load only the node(s) relevant to the current file, not the full graph or the full legacy module.
