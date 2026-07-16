---
name: heuristic-validation
version: 1.0.0
description: >
  Runs cheap, deterministic sanity checks (range, sign, sum-to-total,
  calendar validity, format/regex) against the artifact under test, using
  the HeuristicCheck linked to the relevant knowledge-graph rule. Trigger
  first, before any comparison-based evaluation — a heuristic failure means
  there's no point diffing output that's already out of bounds.
inputs:
  - artifact_output: the field(s) produced by the artifact under test for one module
  - heuristic_check: the linked mig:HeuristicCheck node from the knowledge graph
outputs:
  - pass_fail: block-level result
  - violated_bound: which specific bound failed, if any
depends_on: [knowledge-graph-builder]
reference: REFERENCE.md
---

# Skill: Heuristic Validation

## What this skill does

Before any expensive comparison against a golden dataset or a rule-engine oracle, run the cheapest possible check: is the output even in a plausible range. This catches an entire class of obviously broken output — negative interest, a date outside the business calendar, a field that doesn't sum to its stated total — without needing any comparison data at all.

## Procedure

1. **Look up the linked `HeuristicCheck`.** If the rule has no linked heuristic node, report that as a coverage gap — do not skip the stage silently and proceed as if it passed.
2. **Evaluate the bound.** Each `HeuristicCheck` defines a boolean expression over the artifact's output fields (see `REFERENCE.md` for the catalog of check types).
3. **Severity determines what happens next.** `severity: block` — a failure halts the pipeline for this module; do not proceed to normalization or comparison. `severity: warn` — a failure is logged and the pipeline continues, but the warning must appear in the final report regardless of what later stages find.
4. **Report the specific bound that failed**, not just "heuristic failed" — a reviewer needs to know whether it was a sign error, a range error, or a sum mismatch to triage efficiently.

See `REFERENCE.md` for the heuristic-type catalog and guidance on writing new heuristics for a rule that doesn't have one yet.
