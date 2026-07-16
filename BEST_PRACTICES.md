# Best Practices for This Agent Setup

Written down once, here, instead of re-explained inside every skill file — these are the rules that make the difference between a skills library and a pile of markdown files an agent happens to read.

## 1. The agent orchestrates; skills don't call each other directly

`parity-auditor.chatmode.md` owns the sequence. A skill's `depends_on` field documents what evidence it *expects to already exist*, not permission to invoke another skill itself. This keeps the execution path visible in one place — reading the agent file tells you the whole pipeline, instead of having to trace hidden calls across six skill files to reconstruct what actually runs.

## 2. Every skill declares an explicit contract

`inputs`, `outputs`, and `depends_on` in the frontmatter aren't documentation flavor — they're what makes a skill safely upgradable. A skill that changes its output shape without a MAJOR version bump breaks every consumer silently. Treat the frontmatter contract as seriously as a function signature.

## 3. Keep SKILL.md lean; put depth in REFERENCE.md

The body of a SKILL.md is what an agent needs to decide *whether* and *how* to invoke the skill. The regex catalog, the ontology spec, the metric formulas — the material only needed once the skill is actually running — lives in `REFERENCE.md` and is loaded on demand. This is a token-efficiency discipline, not just a filing convention: a session that touches three skills should carry three lean SKILL.md bodies in context, not the full depth of all six.

## 4. Fail closed, not open

A heuristic failure halts the pipeline for that module. A missing oracle is reported as reduced evidence strength, not silently treated as full confidence. An uncovered rule counts as a recall failure (zero), not an excluded unknown. At every decision point in this framework, the default when evidence is missing or a check fails is to stop and surface the gap — never to proceed on an assumption and let a later stage catch it.

## 5. Evidence has one writer

Only `knowledge-graph-builder` writes to the knowledge graph. Every other skill produces evidence and hands it off. This is what keeps the ontology consistent — six skills independently deciding how to shape a triple would drift within a month.

## 6. Human review gates stay with humans

New `BusinessRule` nodes require human confirmation. Sign-off above Low risk requires a named human owner. No skill or agent in this framework has authority to mark a module production-ready on its own — every skill's output is evidence for a person to review, never a decision.

## 7. Two independent oracles beat one, and disagreement is itself a finding

Comparing against only a golden dataset means a bad batch of historical data becomes ground truth. Comparing against only a rule-engine implementation means a bug in that implementation goes uncaught. When both exist and agree, confidence is earned from two directions. When they disagree, that disagreement is reported — never silently resolved by picking whichever one the artifact happened to match.

## 8. Numeric agreement is necessary, not sufficient

This is the single most important practice in the framework and the reason `ai-semantic-validation` and the coincidental-match-risk override exist. A high parity match rate proves the artifact agrees with what was tested. It does not prove the artifact implements the rule in general. Treat a semantic cross-check as mandatory before any module reaches a High confidence band, not as an optional nice-to-have layered on top of numbers that already looked fine.

## 9. Version skills independently, and let the agent pin ranges

A bug fix in `heuristic-validation` shouldn't force a review of `confidence-scoring`. A change to what `agreement_level` means in `ai-semantic-validation`, on the other hand, changes what `confidence-scoring` is reading — that's a MAJOR bump on the producing skill, and the consuming skill's `depends_on` should be checked before either is deployed. See `SKILLS_CHANGELOG.md` for current versions and the semver convention.

## 10. Input is for artifacts under test; context is for everything the framework already trusts

`input/artifacts/` is the only folder a new artifact drops into. `context/` (golden datasets, rule-engine implementations, the knowledge graph, legacy source) is treated as trusted, curated, and change-controlled separately from whatever's currently being evaluated. Mixing the two — for instance, letting a golden dataset live next to the artifact under test — makes it too easy for a normalization or comparison step to accidentally read the wrong side of the check.
