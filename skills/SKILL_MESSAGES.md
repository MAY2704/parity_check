# Skill Messages: Format and Confidence Semantics

Every skill in this framework hands off its result the same way: as a JSON object matching `context/schemas/skill-message.schema.json`. This file covers the parts of that schema that need judgment, not just structure: what `confidence` means, why it's split into two `source` types, and how those types are allowed to interact.

## Why an envelope, not just a return value

Six skills run in a fixed order, each depending on the one before. Without a shared shape, "what heuristic-validation hands to parity-evaluation" is whatever prose the last edit happened to describe, and nothing downstream can check it. With a shared envelope, every message is machine-parseable, every message is addressable by `run_id` for reassembling the full chain, and every message states how much it trusts itself, not just what it found.

## Two kinds of confidence, and they are not interchangeable

**`calibrated`**: a number derived by formula from measured evidence. `heuristic-validation`'s confidence reflects how proven the heuristic itself is (a brand-new, never-tested heuristic reports lower confidence than one that's run clean against a hundred historical batches). `parity-evaluation`'s confidence reflects oracle coverage: a module checked against both the golden dataset and the rule engine reports higher confidence than one checked against only the golden dataset, independent of what the match rate says. These numbers are reproducible: given the same inputs, the same formula produces the same confidence every time.

**`self-reported`**: used by exactly one skill, `ai-semantic-validation`. When the skill reads an artifact's logic blind and describes what it thinks the code does, its confidence in that reading is a model's own self-assessment, not a formula over external evidence. That's softer by nature, and treating it as equivalent to a calibrated number would be the kind of false precision this framework is built to avoid.

## The propagation rule

**Self-reported confidence can lower a downstream score. It can never raise one.**

Concretely, in `confidence-scoring`: if `ai-semantic-validation` reports `agreement_level: aligned` with high self-reported confidence, that does not add points beyond what the Semantic Agreement component already awards for "aligned." But if it reports `contradicts` or flags `coincidentalMatchRisk`, that self-assessment is what triggers the Low-band override, regardless of how confident the skill was. A downgrade signal is trusted; an upgrade signal from the same source is not. This mirrors the framework's core thesis: a positive numeric match is necessary but not sufficient, while a negative semantic finding is sufficient on its own to stop the pipeline.

## Message example: heuristic-validation → parity-evaluation

```json
{
  "skill": "heuristic-validation",
  "skill_version": "2.0.0",
  "module": "interest-accrual",
  "run_id": "run-2026-07-17T09:41:00Z-interest-accrual",
  "timestamp": "2026-07-17T09:41:02Z",
  "status": "pass",
  "confidence": {
    "value": 0.95,
    "band": "high",
    "basis": "Heuristic HCHK-0001 has run clean against 118 prior batches with zero false positives; bound cleared on this run with no near-miss.",
    "source": "calibrated"
  },
  "result": {
    "checks_run": ["HCHK-0001"],
    "violated_bound": null
  },
  "evidence_refs": ["rule:RULE-0001", "rule:HCHK-0001"],
  "gaps": []
}
```

## Message example: ai-semantic-validation → confidence-scoring

```json
{
  "skill": "ai-semantic-validation",
  "skill_version": "2.0.0",
  "module": "fee-waiver",
  "run_id": "run-2026-07-17T09:41:00Z-fee-waiver",
  "timestamp": "2026-07-17T09:44:18Z",
  "status": "pass",
  "confidence": {
    "value": 0.55,
    "band": "medium",
    "basis": "Blind read was straightforward for the main branch but the artifact's exception-path logic was sparse; moderate confidence in completeness of the independent description.",
    "source": "self-reported"
  },
  "result": {
    "independent_description": "Returns a fixed waiver flag for a hard-coded list of six account IDs; no date or balance calculation present.",
    "agreement_level": "contradicts",
    "coincidental_match_risk": true,
    "divergence_notes": ["Documented rule requires a 90-consecutive-day balance check; no such logic exists in the artifact."]
  },
  "evidence_refs": ["rule:RULE-0002"],
  "gaps": ["No rule-engine oracle exists yet to cross-check this finding analytically."]
}
```

The `confidence.value` here (0.55) reflects how sure the skill is in its *own reading*. It isn't softened by, and doesn't get overridden by, the severity of what it found. A skill can be highly confident in a bad finding, or moderately confident in a good one; the two numbers answer different questions and both get reported.

## Where the full message chain lives

The orchestrating agent writes every message from a run, in order, to `output/reports/{module}-{date}.json`, the machine-readable companion to the human-readable `output/reports/{module}-{date}.md`. The `.md` report is what a reviewer reads; the `.json` chain is what lets the same run be re-validated, replayed, or audited programmatically later.
