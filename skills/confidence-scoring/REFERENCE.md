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

- **90–100 High** — eligible for sign-off / cutover track
- **60–89 Medium** — targeted remediation required before sign-off
- **< 60 Low** — not eligible; returns to remediation queue

## Override rules and why each one exists

| Override | Why |
|---|---|
| Context Completeness = 0 | Nothing downstream is trustworthy if the agent never had the right rule in front of it to begin with |
| Blind-Spot Coverage = 0 on a financial/regulatory rule | A module with zero coverage on money-moving logic cannot be Medium just because other modules pull the average up |
| Recall Floor = 0 | Perfect precision on a module that's barely been checked is not evidence of correctness, it's evidence of not looking |
| `coincidental_match_risk: true` | This is the specific failure mode where every other number can look perfect — 100% parity match, full context, full blind-spot coverage — while the artifact doesn't actually implement the rule. If this override didn't exist, it would be the single easiest way for a bad artifact to score High. |

The last override is the one most worth remembering: **a 100% parity match rate is not sufficient evidence on its own, ever, in this framework.** It's necessary, not sufficient — semantic agreement is what turns a numeric match into a claim about correctness.

## Self-reported confidence is a downgrade-only input

`ai-semantic-validation`'s message carries `confidence.source: "self-reported"` — the skill's own certainty in its blind read, not a formula over external evidence. This framework never lets that value push a score up. A high self-reported confidence attached to `agreement_level: aligned` earns exactly the 100 points the Semantic Agreement component already assigns for "aligned," no bonus on top. A *low* self-reported confidence attached to `contradicts` or `coincidentalMatchRisk: true` still triggers the full downgrade and the override — the skill being unsure of its own reading is not a reason to discount a red flag it raised. See `skills/SKILL_MESSAGES.md` for the general rule this follows across the framework.

## Versioning note for this skill

- **PATCH** — a corrected weight typo, a clarified band boundary.
- **MINOR** — a new override condition added, or a new component added without removing an existing one (requires reweighting, which is why this is MINOR not PATCH).
- **MAJOR** — removal of a component, a change to what "High/Medium/Low" means, or a change to which overrides exist — any change that would make a previously-computed score not directly comparable to a new one.
