---
description: 'Compute a transparent, evidence-based confidence score for a module — no black-box scoring. Includes precision, recall, and F1.'
mode: agent
---

Compute the confidence score for `${input:module}` using the rubric defined in `parity/checklists/parity-checklist.md`. Do not estimate — pull each component from logged evidence via `parity/neo4j/queries.cypher`:

1. **Context Completeness (20%)** — % of required knowledge-graph nodes present and fresh for this module.
2. **Parity Match / F1 (30%)** — harmonic mean of precision and recall on discrepancy classification from the most recent `*run-parity` entry, not the raw match rate alone.
3. **Blind-Spot Coverage (25%)** — % of relevant nodes with a linked heuristic check, rule-engine oracle, AND parity check, from the most recent `*scan-blindspots` entry.
4. **Recall Floor (10%)** — recall, isolated on its own, separate from precision. A module can score well on precision while still being barely covered; this component exists so that can't hide.
5. **Review Status (15%)** — 0 if unreviewed, 60 if reviewed and pending sign-off, 100 if signed off by a named accountable owner.

**Override rule:** if any single component is 0 — missing critical context, zero blind-spot coverage on a financial/regulatory node, zero recall, or no review at all — cap the composite score in the Low band regardless of the weighted total. A strong average must never mask one critical gap.

Bands: **90–100 High** (eligible for sign-off track) · **60–89 Medium** (targeted remediation required) · **below 60 Low** (not eligible, returns to remediation queue).

Output all five component scores, the weighted composite, the band, and which override (if any) was applied. Do not output a single number with no breakdown.
