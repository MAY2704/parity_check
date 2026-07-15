---
description: 'Scan a scope of the knowledge graph for regression blind spots — nodes with no linked test or parity check.'
mode: agent
---

Scan `${input:scope}` for regression blind spots.

1. Enumerate every knowledge-graph node in scope.
2. For each node, check for a linked test and a linked parity check. Any node missing either is a blind spot.
3. Do not treat a passing parity check as evidence of test coverage, or vice versa — they are separate forms of evidence and both are required.
4. Rank the resulting list by exposure: financial and regulatory-reporting nodes first, cosmetic/informational nodes last.
5. Append each new finding to `parity/checklists/regression-blindspot-checklist.md` with `Owner: unassigned` and today's date.
6. Output a one-line summary: total nodes scanned, number of blind spots found, number newly added to the checklist.

Do not attempt to close any blind spot in this run — this prompt only finds and logs gaps.
