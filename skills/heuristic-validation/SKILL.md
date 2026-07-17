---
name: heuristic-validation
version: 2.0.0
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
  - JSON message per context/schemas/skill-message.schema.json
depends_on: [knowledge-graph-builder]
output_schema: ../../context/schemas/skill-message.schema.json
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

## Output message

Confidence for this skill is always `calibrated`, and its basis is the heuristic's own track record, not just whether this one run passed — a brand-new heuristic passing once is weaker evidence than one that's cleared a hundred prior batches:

```json
{
  "skill": "heuristic-validation",
  "skill_version": "2.0.0",
  "module": "fee-waiver",
  "run_id": "run-2026-07-17T09:41:00Z-fee-waiver",
  "timestamp": "2026-07-17T09:41:05Z",
  "status": "blocked",
  "confidence": {
    "value": 0.3,
    "band": "low",
    "basis": "No HeuristicCheck node is linked to this rule at all — nothing to evaluate, not a pass.",
    "source": "calibrated"
  },
  "result": {
    "checks_run": [],
    "violated_bound": null
  },
  "evidence_refs": ["rule:RULE-0002"],
  "gaps": ["No linked HeuristicCheck node — coverage gap, report to blind-spot checklist"]
}
```

See `REFERENCE.md` for the heuristic-type catalog and guidance on writing new heuristics for a rule that doesn't have one yet.
