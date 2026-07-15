---
description: 'Run a full parity check for a specified module against its golden dataset.'
mode: agent
---

Run a parity check for `${input:module}`.

1. Load **only** the knowledge-graph nodes tagged to this module from `parity/knowledge-graph.md` — do not pull the full graph into context.
2. Confirm each required node's `Last Verified` date is within the freshness window. If any node is stale or missing, stop here and report the gap as the result — do not proceed on an assumed rule.
3. Load the golden dataset for this module from `parity/golden-datasets/`.
4. Execute the transformation/target output and diff against the golden dataset, field by field. Do not sample — cover every field defined for the module.
5. Classify every discrepancy as one of: `tolerance-acceptable`, `transformation-error`, or `legacy-defect-now-fixed`.
6. Write the result to `parity/evaluation-log.md` using the standard entry format. A verbal summary is not a substitute for the log entry.
7. Call `*score-confidence {module}` and include the result.
8. Output a single status line: `PASS / FAIL / NEEDS-REVIEW — confidence {score}/100 ({band})`.
