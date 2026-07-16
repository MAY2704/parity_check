# Project Instructions — Modernization Program

This repo is a legacy-to-target modernization effort. The governing rule for any AI-assisted change, review, or claim in this repo:

**Parity before fluency. No confidence claim without logged evidence.**

Before generating, transforming, or approving anything in a migrated module:

1. Query the knowledge graph (`parity/knowledge-graph.ttl`, synced into Neo4j — see `parity/neo4j/queries.cypher`) for the business rules relevant to the module. If the relevant nodes are missing, stale, or unclear, say so — do not infer or guess the rule from raw legacy code.
2. Any parity claim must have gone through all three validation stages — heuristic check, normalization, dual comparison against both the golden dataset and the rule-engine oracle (`parity/rules-engine/`) — not a partial run.
3. Do not mark anything "correct," "safe," or "ready" without a corresponding entry in `parity/evaluation-log.md`, including precision, recall, and F1 — not just a match rate.
4. Use the **Parity Auditor** chat mode (`.github/chatmodes/parity-auditor.chatmode.md`) to validate a module.
5. Use the **Blind-Spot Scout** chat mode (`.github/chatmodes/blindspot-scout.chatmode.md`) to find what is *not* being checked, and to report recall exposure — this is a separate question from whether existing checks pass.
6. Every confidence score must be traceable to the five-component rubric in `parity/checklists/parity-checklist.md` — never state a confidence level without showing the components behind it.

Scoped rules for specific paths live under `.github/instructions/`. Reusable, repeatable tasks live under `.github/prompts/`. This file is the only thing loaded on every request — keep it short on purpose; everything else is pulled in only when relevant, to keep context small and current.
