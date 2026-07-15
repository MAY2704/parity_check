# Regression Blind-Spot Checklist

Every row is a knowledge-graph node with no linked test, no linked parity check, or both. Added automatically by the Blind-Spot Scout's `*scan-blindspots` command; closed manually once an owner adds coverage.

| Node ID | Gap | Exposure | Owner | Found | Status |
|---|---|---|---|---|---|
| RULE-0002 | No test, no parity check | High — fee logic, revenue-impacting | unassigned | 2026-07-10 | Open |
| RULE-0003 | Parity check exists but stale (>30 days) | Medium — sequencing, not value-impacting | unassigned | 2026-07-10 | Open |

## Rules for this list

- **Exposure ranking:** financial and regulatory-reporting nodes are High by default; sequencing/operational nodes are Medium; cosmetic/reporting-only nodes are Low.
- **A row only closes when both a test and a parity check are linked back in `knowledge-graph.md`** — closing this row without updating the graph is not a real fix, just a hidden one.
- **Re-open on drift:** if a module tied to a closed node changes materially, re-run `*scan-blindspots` for that scope before assuming coverage still holds.
