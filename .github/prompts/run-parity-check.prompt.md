---
description: 'Run a full parity check for a specified module against its golden dataset.'
mode: agent
---

Run a parity check for `${input:module}`.

1. Query `parity/neo4j/queries.cypher` (context-assembly query) for **only** the graph nodes tagged to this module — do not pull the full graph into context.
2. Confirm the node's parity check, if any, is within the freshness window, and that it has linked `HeuristicCheck` and `RuleEngineImpl` nodes. If any required node is missing or stale, stop here and report the gap as the result — do not proceed on an assumed rule.
3. **Stage 1 — heuristic pass.** Run the linked `HeuristicCheck` against the AI-generated output first. If it fails, stop the pipeline here and report the heuristic failure; do not proceed to comparison against output that's already out of bounds.
4. **Stage 2 — normalize.** Apply every applicable rule in `parity/normalization-rules.md` to the AI-generated output, the golden dataset, and the rule-engine output. Do not compare raw, unnormalized values.
5. **Stage 3 — dual comparison.** Diff the normalized AI-generated output against both the golden dataset (`parity/golden-datasets/`) and the rule-engine implementation (`parity/rules-engine/`), field by field, covering every field defined for the module — no sampling.
6. Classify every discrepancy as one of: `tolerance-acceptable`, `transformation-error`, or `legacy-defect-now-fixed`. Note explicitly if the two oracles (golden dataset vs. rule engine) disagreed with each other, separate from whether either agreed with the AI output.
7. Compute **precision** (of discrepancies flagged as transformation-error, what share held up on review) and **recall** (of the rule's full evaluation history, what share of known real defects were caught by a check — a rule missing its heuristic check, rule-engine oracle, or parity check contributes 0, not "unknown"). Report F1 alongside the raw match rate.
8. Write the result to `parity/evaluation-log.md` using the standard entry format, including precision/recall/F1. A verbal summary is not a substitute for the log entry.
9. Call `*score-confidence {module}` and include the result.
10. Output a single status line: `PASS / FAIL / NEEDS-REVIEW — confidence {score}/100 ({band}) — precision {p} / recall {r} / F1 {f1}`.
