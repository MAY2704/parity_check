# Project Instructions: Modernization Program

This repo is a legacy-to-target modernization effort. The governing rule for any AI-assisted change, review, or claim in this repo:

**Parity before fluency. No confidence claim without logged evidence, and a numeric match is never sufficient on its own.**

## Where things live

- `input/artifacts/`: drop an artifact under test here. Nowhere else.
- `output/reports/` + `output/evaluation-log.md`: every generated report and the append-only audit trail. Nothing else writes here.
- `context/`: the knowledge graph (`knowledge-graph.ttl`, synced to Neo4j), golden datasets, rule-engine implementations, legacy source. Trusted and change-controlled separately from `input/`.
- `skills/`: the reusable capability library (rule-based extraction, graph building, heuristic validation, AI semantic validation, parity evaluation, confidence scoring). Each skill is independently versioned; see `SKILLS_CHANGELOG.md`.
- `.github/chatmodes/`: the two agent personas that orchestrate the skills: **Parity Auditor** (per-module evaluation) and **Blind-Spot Scout** (coverage/recall exposure across a scope).
- `BEST_PRACTICES.md`: the operating principles behind this setup; read before modifying any skill or agent file.

## Before generating, transforming, or approving anything in a migrated module

1. Query the knowledge graph for the relevant `BusinessRule` node. If missing, stale, or unclear, say so. Never infer or guess the rule from raw legacy code.
2. A parity claim requires all three pipeline stages: heuristic check, then normalization, then dual comparison against both the golden dataset and the rule-engine oracle.
3. A numeric match, on its own, is not evidence of correctness. `ai-semantic-validation` must confirm the artifact's actual logic matches the documented rule before a module is eligible for a High confidence band.
4. Do not mark anything "correct," "safe," or "ready" without a corresponding entry in `output/evaluation-log.md`, including precision, recall, accuracy, and F1, not just a match percentage.
5. Every confidence score must show all six rubric components, never a bare number. See `skills/confidence-scoring/REFERENCE.md`.

This file is the only thing loaded on every request, kept short on purpose. Skill depth lives in each skill's `REFERENCE.md`, loaded only when that skill actually runs.
