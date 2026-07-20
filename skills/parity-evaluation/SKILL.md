---
name: parity-evaluation
version: 3.0.0
description: >
  Deterministic dual-oracle comparison, executed by scripts/parity_eval.py
  rather than followed as prose. Normalizes artifact output, golden dataset,
  and rule-engine output; compares field-per-case against both oracles;
  differential-fuzzes the artifact against the rule engine over declared
  input domains (boundary cases included); checks declared metamorphic
  properties; scores golden-dataset adequacy; and computes the confusion
  matrix and precision/recall/accuracy/F1 under explicit degenerate-case
  conventions (a ratio with a zero denominator is null, never 1.0).
  Trigger after heuristic-validation has passed for the module.
inputs:
  - >-
    artifact harness at input/artifacts/{module}/harness.mjs, executed via
    scripts/run_artifact.mjs — or a precomputed output file via
    --artifact-output where node is unavailable
  - "golden_dataset: context/golden-datasets/{module}/golden.json"
  - >-
    rule_config at context/rules-engine/{module}.rules.yaml (formula, rounding,
    output_fields, input_domains, properties, adequacy target)
  - "optional review file: context/golden-datasets/{module}/review.json"
depends_on: [heuristic-validation]
outputs:
  - JSON message per context/schemas/skill-message.schema.json, emitted by
    scripts/parity_eval.py
output_schema: ../../context/schemas/skill-message.schema.json
reference: REFERENCE.md
---

# Skill: Parity Evaluation

## What this skill does

The core empirical/analytical comparison — and as of 3.0.0, it is **executable, not prose**. Every number in this skill's message is computed by `scripts/parity_eval.py`, which a human can re-run with the same seed and get the same answer. The orchestrating agent's job here is to prepare inputs, run the script, and interpret the message; it never re-derives, estimates, or "mentally executes" any comparison itself. If the script cannot run, the result is `status: blocked` with the reason in `gaps` — not a hand-computed substitute.

Three layers of evidence, strongest first:

1. **Golden comparison** (empirical): field-per-case against `golden.json`, both sides normalized. Every declared output field, every case, no sampling of fields.
2. **Differential fuzz + boundary cases** (analytical): the artifact executed against the rule-engine formula over the rule's declared `input_domains` — hundreds of generated cases, including boundary values derived from the documented rule. This is what breaks the golden dataset's coverage ceiling: a divergence anywhere in the domain is caught numerically even if no golden case goes there.
3. **Metamorphic properties** (oracle-free): declared invariants of the documented rule (monotonicity, linearity, zero-cases) checked against the artifact alone. These hold even for rules with no rule-engine implementation.

## Procedure

1. Confirm `heuristic-validation` passed for this module, then run, from the repo root:

   ```
   python scripts/parity_eval.py {module} --run-id {run_id} --out {message_path}
   ```

   Defaults: 500 fuzz cases, seed 1337 (always record the seed; it is in the message). If node is unavailable, execute the artifact externally over the golden inputs and pass `--artifact-output`; the script then skips fuzzing and properties and records that as a gap with reduced confidence — never silently.
2. **Do not adjust the emitted numbers.** The agent may add interpretation around the message, not inside it.
3. **Route discrepancies to humans, not categories.** Every flagged discrepancy defaults to `transformation-error` (a provisional TP — fail-closed). Only a human review recorded in `context/golden-datasets/{module}/review.json` may reclassify a unit to `tolerance-acceptable` or `legacy-defect-now-fixed`; re-running the script then picks the reclassification up.
4. **Report oracle disagreement separately.** If the golden dataset and the rule engine disagree with each other, the message says which one the artifact agreed with; that is a finding about the oracles for a domain expert, never a tie resolved silently.
5. **Read the adequacy block before trusting a clean run.** `result.dataset_adequacy` scores the golden dataset itself (volume, range coverage, boundary coverage, provenance). A 100% match against an inadequate dataset is weak evidence, and the calibrated confidence already reflects that.
6. **Route the message onward**: to `knowledge-graph-builder` to write the `ParityCheck` evidence node, and to `ai-semantic-validation` for the logic-level cross-check. Fuzzing narrows the coincidental-match window but does not close it (a memorized formula variant can survive fuzzing; a memorized golden dataset cannot), so the semantic read remains mandatory. This skill does not invoke either directly; see `BEST_PRACTICES.md` §1.

## Output message

Confidence is `calibrated` from **evidence breadth** — oracle coverage, dataset adequacy, and fuzz coverage — never from the match rate. Metrics with zero denominators are `null` with an explanatory note, and downstream scoring must apply the null-metric fallback in `skills/confidence-scoring/REFERENCE.md` rather than substituting 1.0. Example (abridged from a real demo run; full field definitions in `REFERENCE.md`):

```json
{
  "skill": "parity-evaluation",
  "skill_version": "3.0.0",
  "module": "interest-accrual-demo",
  "run_id": "run-2026-07-20T00:00:00Z-interest-accrual-demo",
  "timestamp": "2026-07-20T00:01:00Z",
  "status": "fail",
  "confidence": {
    "value": 0.7864,
    "band": "medium",
    "basis": "Calibrated from evidence breadth, not the match rate: oracles=2/2 (golden-dataset, rule-engine), dataset adequacy 0.15 (volume 0.10, range 0.05, boundary 0.23, provenance synthetic), differential fuzz 551 cases (seed 1337).",
    "source": "calibrated"
  },
  "result": {
    "unit_of_analysis": "field-per-case",
    "oracles_present": ["golden-dataset", "rule-engine"],
    "golden_comparison": { "cases": 5, "units_compared": 5, "matches": 5 },
    "discrepancies": [],
    "oracle_disagreement": [],
    "metrics": {
      "unit_of_analysis": "field-per-case",
      "tp": 0, "fp": 0, "fn": 0, "tn": 5,
      "comparison_units": 5,
      "match_rate": 1.0,
      "oracle_coverage": 1.0,
      "precision": null, "recall": null, "accuracy": 1.0, "f1": null,
      "degenerate_notes": [
        "precision undefined: nothing was flagged (TP+FP=0)",
        "recall undefined: no known or presumed defects (TP+FN=0)",
        "f1 undefined: see precision/recall; downstream scoring must use the null-metric fallback, not substitute 1.0"
      ]
    },
    "differential_fuzz": {
      "oracle": "rule-engine",
      "seed": 1337,
      "cases_run": 551,
      "boundary_cases": 51,
      "random_cases": 500,
      "divergence_count": 531,
      "divergence_rate": 0.9637,
      "examples": [
        { "inputs": { "principal": 500000.0, "annual_rate": 0.248911, "days_elapsed": 1603 }, "artifact": 15556.94, "rule_engine": 554172.68 }
      ]
    },
    "property_checks": [
      { "type": "monotonic_nondecreasing", "over": "days_elapsed", "trials": 60, "violation_count": 0, "status": "pass", "examples": [] },
      { "type": "linear_in", "over": "days_elapsed", "trials": 16, "violation_count": 8, "status": "fail",
        "examples": [ { "inputs": { "principal": 443079.67, "annual_rate": 0.06265 }, "days_elapsed": [103, 515], "expected_ratio": 5, "accrued_interest": [3469.87, 3469.87] } ] }
    ],
    "dataset_adequacy": {
      "case_count": 5, "target_case_count": 50,
      "volume": 0.1, "range_coverage": 0.0499, "boundary_coverage": 0.2323,
      "provenance": "synthetic", "provenance_factor": 0.3, "score": 0.1455
    }
  },
  "evidence_refs": ["rule:RULE-DEMO-001"],
  "gaps": []
}
```

This is the run the framework exists for: a **100% golden match** and a **failed evaluation**, because the differential fuzz and the linearity property both caught, numerically and reproducibly, a divergence the five golden cases could not see.

See `REFERENCE.md` for the metric conventions (including the degenerate-case rules and the run-time vs. retrospective recall split), the fuzz/boundary/property methodology, the adequacy formula, and the calibrated-confidence formula.
