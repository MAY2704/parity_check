# Regression Blind-Spot Checklist

Every row is a `BusinessRule` node missing a linked heuristic check, rule-engine oracle, or parity check, or all three. Added automatically by the Blind-Spot Scout's `*scan-blindspots` command; closed manually once an owner adds the missing evidence.

| Node ID | Gap | Exposure | Owner | Found | Status |
|---|---|---|---|---|---|
| RULE-0002 | No heuristic check, no rule-engine oracle, no parity check | High: fee logic, revenue-impacting | unassigned | 2026-07-10 | Open |
| RULE-0003 | Parity check exists but stale (>30 days) | Medium: sequencing, not value-impacting | unassigned | 2026-07-10 | Open |

## Rules for this list

- **Exposure ranking:** financial and regulatory-reporting nodes are High by default; sequencing/operational nodes are Medium; cosmetic/reporting-only nodes are Low.
- **A row only closes when the missing evidence is actually linked back in `context/knowledge-graph.ttl`** via the `knowledge-graph-builder` skill. Closing this row without updating the graph is not a real fix, just a hidden one.
- **Re-open on drift:** if a module tied to a closed node changes materially, re-run `*scan-blindspots` for that scope before assuming coverage still holds.
