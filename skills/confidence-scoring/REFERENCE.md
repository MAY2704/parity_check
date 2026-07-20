# Reference: Confidence Score Weighting

## Component weights

| Component | Weight | Source | What it measures |
|---|---|---|---|
| Context Completeness | 15% | knowledge-graph-builder / graph query | % of required nodes present and fresh |
| Parity F1 | 25% | parity-evaluation | Balance of precision and recall on the numeric comparison |
| Semantic Agreement | 20% | ai-semantic-validation | Does the artifact's actual logic match the documented rule, not just its sampled output |
| Blind-Spot Coverage | 20% | graph query across heuristic / rule-engine / parity links | % of relevant nodes with all three evidence links present |
| Recall Floor | 10% | parity-evaluation | Recall in isolation, so a strong precision number can't hide weak coverage |
| Review Status | 10% | output/evaluation-log.md | 0 unreviewed / 60 pending sign-off / 100 signed off by a named owner |

`Semantic Agreement` scoring: `aligned` = 100, `partially-aligned` = 50, `contradicts` = 0.

## Bands

- **90–100 High**: eligible for sign-off / cutover track
- **60–89 Medium**: targeted remediation required before sign-off
- **< 60 Low**: not eligible; returns to remediation queue

**Note on Review Status and first-pass runs:** `review_status` is worth 10% and scores 0 until a named human has signed off (see the table above). This means a module's very first evaluation, before any human has reviewed it, can score at most 90 even if the other five components are all perfect, capping it at the bottom edge of High rather than excluding it from High outright. This is intentional, not a bug: it reflects that a run with all evidence pointing to correctness still hasn't cleared the framework's human sign-off gate (`BEST_PRACTICES.md` §6). Don't read a first-pass 90 as "somehow made it to High without review." It means every other signal is clean and review is the only thing left.

## Null-metric fallbacks (parity-evaluation ≥ 3.0.0)

A degenerate clean run — nothing flagged, no known or presumed defects — reports `precision`, `recall`, and `f1` as **null**, with the reason in `metrics.degenerate_notes`. Null is not 1.0 and not 0. Substituting 1.0 launders "we found nothing and had nothing to find it against" into a perfect score; substituting 0 wrongly triggers the Recall Floor override on every clean first pass. Instead:

| Component | When its metric is null, use |
|---|---|
| Parity F1 (25%) | `match_rate × (0.5·oracle_factor + 0.25·dataset_adequacy + 0.25·fuzz_factor)` — plain agreement, scaled by the same evidence-breadth terms parity-evaluation calibrates its own confidence from (uncapped). `oracle_factor`: 1.0 both oracles, 0.5 golden only. `fuzz_factor`: min(1, fuzz cases / 100), 0 if fuzzing didn't run. |
| Recall Floor (10%) | `oracle_coverage × (0.5 + 0.5·fuzz_factor)` — coverage stands in for recall, at half credit unless a differential fuzz swept the domain. |

Consequences worth stating plainly: a clean run against a thin synthetic golden dataset with no fuzzing earns roughly half credit on these components, not full marks — the missing evidence is priced in rather than assumed. And the **Recall Floor = 0 override applies to a *computed* zero** (defects existed or units were uncovered, and none were caught: `oracle_coverage = 0` under the fallback), never to a null that fell back to a positive coverage value.

`result.dataset_adequacy` (volume, range coverage, boundary coverage, provenance) enters the composite through these fallbacks. A reviewer should still read the adequacy block directly before sign-off: it is the measured answer to the checklist's "real historical production data, not synthetic samples only."

## Override rules and why each one exists

| Override | Why |
|---|---|
| Context Completeness = 0 | Nothing downstream is trustworthy if the agent never had the right rule in front of it to begin with |
| Blind-Spot Coverage = 0 on a financial/regulatory rule | A module with zero coverage on money-moving logic cannot be Medium just because other modules pull the average up |
| Recall Floor = 0 | Perfect precision on a module that's barely been checked is not evidence of correctness, it's evidence of not looking |
| `coincidental_match_risk: true` | The specific failure mode where every other number can look perfect (100% parity match, full context, full blind-spot coverage) while the artifact doesn't actually implement the rule. Without this override, it would be the easiest way for a bad artifact to score High. |

The last override matters most: **a 100% parity match rate is not sufficient evidence on its own, ever, in this framework.** It's necessary, not sufficient. Semantic agreement is what turns a numeric match into a claim about correctness.

## Self-reported confidence is a downgrade-only input

`ai-semantic-validation`'s message carries `confidence.source: "self-reported"`, the skill's own certainty in its blind read, not a formula over external evidence. This framework never lets that value push a score up. A high self-reported confidence attached to `agreement_level: aligned` earns exactly the 100 points the Semantic Agreement component already assigns for "aligned," no bonus on top. A *low* self-reported confidence attached to `contradicts` or `coincidentalMatchRisk: true` still triggers the full downgrade and the override. The skill being unsure of its own reading is not a reason to discount a red flag it raised. See `skills/SKILL_MESSAGES.md` for the general rule this follows across the framework.

## Versioning note for this skill

- **PATCH**: a corrected weight typo, a clarified band boundary.
- **MINOR**: a new override condition added, or a new component added without removing an existing one (requires reweighting, which is why this is MINOR not PATCH).
- **MAJOR**: removal of a component, a change to what "High/Medium/Low" means, or a change to which overrides exist. Any change that would make a previously-computed score not directly comparable to a new one.
- **2.1.0**: added the null-metric fallbacks for parity-evaluation ≥ 3.0.0 degenerate runs (MINOR: messages with non-null metrics score exactly as before).
