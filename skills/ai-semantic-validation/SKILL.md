---
name: ai-semantic-validation
version: 2.0.0
description: >
  Uses an independent AI reading of the artifact under test to decipher
  what business logic it actually implements, then cross-checks that
  reading against the rule-based description in the knowledge graph and
  against the numeric results from heuristic-validation and
  parity-evaluation. Exists specifically to catch artifacts that match
  sampled output numerically without actually implementing the documented
  rule. Trigger after heuristic-validation and parity-evaluation have both
  produced results for the module.
inputs:
  - artifact_source: the actual code/logic of the artifact under test, not just its output
  - business_rule: the linked mig:BusinessRule node's description
  - parity_result: output of parity-evaluation for this module
depends_on: [knowledge-graph-builder, parity-evaluation]
outputs:
  - JSON message per context/schemas/skill-message.schema.json. This is the
    ONLY skill in the framework whose confidence.source is "self-reported"
    rather than "calibrated"; see skills/SKILL_MESSAGES.md for why that
    distinction is enforced rather than cosmetic
output_schema: ../../context/schemas/skill-message.schema.json
reference: REFERENCE.md
---

# Skill: AI Semantic Validation

## Why this skill exists

Rule-based checks (heuristic-validation, parity-evaluation) answer "does the output match." They cannot answer "does the *logic* match." An artifact can pass every numeric check against a small golden dataset while implementing something structurally different from the documented rule, simply agreeing on the cases that were tested. This skill checks for that specific failure mode.

## Procedure

1. **Read the artifact blind, first.** Before looking at the knowledge-graph rule description, read the artifact's actual logic and write an independent account of what it appears to compute: inputs, conditionals, output. This ordering matters: reading the documented rule first anchors the description toward confirming it, even when the code doesn't actually match.
2. **Then compare against the documented rule.** Classify agreement as `aligned` (the independent reading matches the rule's description), `partially-aligned` (matches for the common case but diverges on an edge case, boundary condition, or exception path), or `contradicts` (the independent reading describes different logic entirely, regardless of what the numeric output showed).
3. **Cross-reference against parity-evaluation's result.** This is the step that catches the dangerous case: a high numeric match rate combined with `partially-aligned` or `contradicts` semantic agreement means `coincidental_match_risk: true`. Report this explicitly and prominently. It's a more serious finding than a low match rate alone, because it means the existing tests aren't actually exercising the artifact's real behavior.
4. **Name the specific divergence**, don't just flag disagreement. "Implements the rule for standard accounts but has no branch for the fee-waiver exception the rule requires" is actionable; "logic seems different" is not.
5. **This skill's judgment is evidence, not a verdict.** It never overrides a human reviewer and never gets averaged away by a good parity score. See `confidence-scoring`'s override rule for how this is enforced.
6. **Report `confidence.source: "self-reported"` on every message, always.** Never mark this skill's confidence as `calibrated`. That label tells `confidence-scoring` this number can lower a composite score but must never be the reason one goes up. See `skills/SKILL_MESSAGES.md` for the full propagation rule.

## Output message

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

See `REFERENCE.md` for the blind-read methodology, a worked example of a caught coincidental match, and known false-agreement traps.
