---
description: 'Compute a transparent, evidence-based confidence score for a module — no black-box scoring.'
mode: agent
---

Compute the confidence score for `${input:module}` using the rubric defined in `parity/checklists/parity-checklist.md`. Do not estimate — pull each component from logged evidence:

1. **Context Completeness (25%)** — % of required knowledge-graph nodes present and fresh for this module.
2. **Parity Match (35%)** — % of golden-dataset fields matching within tolerance, from the most recent `*run-parity` entry.
3. **Blind-Spot Coverage (25%)** — % of relevant nodes with both a linked test and a linked parity check, from the most recent `*scan-blindspots` entry.
4. **Review Status (15%)** — 0 if unreviewed, 60 if reviewed and pending sign-off, 100 if signed off by a named accountable owner.

**Override rule:** if any single component is 0 — missing critical context, zero blind-spot coverage on a financial/regulatory node, or no review at all — cap the composite score in the Low band regardless of the weighted total. A strong average must never mask one critical gap.

Bands: **90–100 High** (eligible for sign-off track) · **60–89 Medium** (targeted remediation required) · **below 60 Low** (not eligible, returns to remediation queue).

Output the four component scores, the weighted composite, the band, and which override (if any) was applied. Do not output a single number with no breakdown.
