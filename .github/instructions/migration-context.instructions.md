---
applyTo: "src/migration/**"
---

# Migration Module Context

Adds to `.github/copilot-instructions.md` (read that first: it's always loaded and already covers graph-first sourcing and the semantic-check requirement, both of which apply here too). This file adds only what's specific to transformation logic under this path:

- If the tagged `BusinessRule` node has no linked `RuleEngineImpl`, flag that the second oracle is missing before treating any parity result as strong evidence.
- Keep context small: load only the node(s) relevant to the current file, not the full graph or the full legacy module.
