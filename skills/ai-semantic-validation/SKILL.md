---
name: ai-semantic-validation
version: 1.0.0
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
  - independent_description: the AI's own account of what the logic does, produced before reading the documented rule
  - agreement_level: aligned / partially-aligned / contradicts
  - coincidental_match_risk: boolean — true if numeric parity is high but semantic agreement is low
reference: REFERENCE.md
---

# Skill: AI Semantic Validation

## Why this skill exists

Rule-based checks (heuristic-validation, parity-evaluation) answer "does the output match." They cannot answer "does the *logic* match" — an artifact can pass every numeric check against a small golden dataset while implementing something structurally different from the documented rule, and simply happening to agree on the cases that were tested. This skill is the check against that specific failure mode.

## Procedure

1. **Read the artifact blind, first.** Before looking at the knowledge-graph rule description, read the artifact's actual logic and write an independent account of what it appears to compute — inputs, conditionals, output. This ordering matters: reading the documented rule first anchors the description toward confirming it, even when the code doesn't actually match.
2. **Then compare against the documented rule.** Classify agreement as `aligned` (the independent reading matches the rule's description), `partially-aligned` (matches for the common case but diverges on an edge case, boundary condition, or exception path), or `contradicts` (the independent reading describes different logic entirely, regardless of what the numeric output showed).
3. **Cross-reference against parity-evaluation's result.** This is the step that catches the dangerous case: **high numeric match rate + `partially-aligned` or `contradicts` semantic agreement = `coincidental_match_risk: true`.** Report this explicitly and prominently — it is a more serious finding than a low match rate alone, because it means the existing tests are not actually exercising the artifact's real behavior.
4. **Name the specific divergence**, don't just flag disagreement. "Implements the rule for standard accounts but has no branch for the fee-waiver exception the rule requires" is actionable; "logic seems different" is not.
5. **This skill's judgment is evidence, not a verdict.** It never overrides a human reviewer and never gets averaged away by a good parity score — see `confidence-scoring`'s override rule for how this is enforced.

See `REFERENCE.md` for the blind-read methodology, a worked example of a caught coincidental match, and known false-agreement traps.
