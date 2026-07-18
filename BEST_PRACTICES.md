# Best Practices for This Agent Setup

These rules live here once instead of being re-explained inside every skill file. They're what separates a skills library from a pile of markdown files an agent happens to read.

## 1. The agent orchestrates; skills don't call each other directly

`parity-auditor.chatmode.md` owns the sequence. A skill's `depends_on` field documents what evidence it *expects to already exist*, not permission to invoke another skill itself. Reading the agent file tells you the whole pipeline, instead of tracing hidden calls across six skill files to reconstruct what actually runs.

Because of this, `depends_on` never describes this-run execution order. It describes persisted graph state, which may have been written by a prior run. Read it as "this evidence must already be sitting in the graph when I start," not "this skill runs after that one." For example, `heuristic-validation` lists `depends_on: [knowledge-graph-builder]` and runs first in Phase 2, step 1, before `knowledge-graph-builder` runs in this run's step 4. That's not a cycle: the `HeuristicCheck` node it reads must already have been written by an earlier run of `knowledge-graph-builder`, back when the rule was first confirmed. Likewise `ai-semantic-validation` lists `depends_on: [knowledge-graph-builder, parity-evaluation]` and runs at step 3: the `knowledge-graph-builder` half refers to a `BusinessRule` description already persisted from an earlier run, while the `parity-evaluation` half refers to this run's step 2, which does precede it. If a `depends_on` entry can't be satisfied by either "already in the graph" or "already emitted earlier in this run's Phase 2," that's a real gap. Report it per the fail-closed rule (§4) rather than inferring an execution order to make it fit.

## 2. Every skill declares an explicit contract

`inputs`, `outputs`, and `depends_on` in the frontmatter aren't documentation flavor. They're what makes a skill safely upgradable. A skill that changes its output shape without a MAJOR version bump breaks every consumer silently. Treat the frontmatter contract as seriously as a function signature.

## 3. Keep SKILL.md lean; put depth in REFERENCE.md

The body of a SKILL.md is what an agent needs to decide *whether* and *how* to invoke the skill. The regex catalog, the ontology spec, the metric formulas, all the material only needed once the skill is actually running, lives in `REFERENCE.md` and loads on demand. This is a token-efficiency discipline, not just a filing convention: a session that touches three skills should carry three lean SKILL.md bodies in context, not the full depth of all six.

## 4. Fail closed, not open

A heuristic failure halts the pipeline for that module. A missing oracle is reported as reduced evidence strength, not silently treated as full confidence. An uncovered rule counts as a recall failure (zero), not an excluded unknown. When evidence is missing or a check fails, the default at every decision point is to stop and surface the gap, not to proceed on an assumption and let a later stage catch it.

## 5. Evidence has one writer

Only `knowledge-graph-builder` writes to the knowledge graph. Every other skill produces evidence and hands it off. Six skills independently deciding how to shape a triple would drift within a month; this is what keeps the ontology consistent instead.

## 6. Human review gates stay with humans

New `BusinessRule` nodes require human confirmation. Sign-off above Low risk requires a named human owner. No skill or agent in this framework can mark a module production-ready on its own. Every skill's output is evidence for a person to review, not a decision.

## 7. Two independent oracles beat one, and disagreement is itself a finding

Comparing against only a golden dataset means a bad batch of historical data becomes ground truth. Comparing against only a rule-engine implementation means a bug in that implementation goes uncaught. When both exist and agree, confidence is earned from two directions. When they disagree, report the disagreement rather than silently resolving it by picking whichever oracle the artifact happened to match.

## 8. Numeric agreement is necessary, not sufficient

This is why `ai-semantic-validation` and the coincidental-match-risk override exist. A high parity match rate proves the artifact agrees with what was tested; it does not prove the artifact implements the rule in general. Treat a semantic cross-check as mandatory before any module reaches a High confidence band, not as an optional layer on top of numbers that already looked fine.

## 9. Version skills independently, and let the agent pin ranges

A bug fix in `heuristic-validation` shouldn't force a review of `confidence-scoring`. A change to what `agreement_level` means in `ai-semantic-validation`, on the other hand, changes what `confidence-scoring` reads: that's a MAJOR bump on the producing skill, and the consuming skill's `depends_on` should be checked before either is deployed. See `SKILLS_CHANGELOG.md` for current versions and the semver convention.

## 10. Input is for artifacts under test; context is for everything the framework already trusts

`input/artifacts/` is the only folder a new artifact drops into. `context/` (golden datasets, rule-engine implementations, the knowledge graph, legacy source) is trusted, curated, and change-controlled separately from whatever's currently being evaluated. Mixing the two, for instance letting a golden dataset live next to the artifact under test, makes it too easy for a normalization or comparison step to read the wrong side of the check.

## 11. Every inter-skill handoff is a typed message with a confidence indicator, never a bare result

A skill that returns "PASS" or a plain-text summary gives the next skill, and the human reading the final report, nothing to check its own trust in that result against. Every skill emits one JSON object per `context/schemas/skill-message.schema.json`, and that object always carries a `confidence` block: a numeric `value`, a `band`, a plain-language `basis`, and a `source` marked `calibrated` or `self-reported`. The two source types are not interchangeable: a calibrated number is reproducible from a formula over measured evidence, while a self-reported number is a model's own certainty in its own read. One asymmetry is enforced consistently: self-reported confidence can lower a downstream score, but it can never raise one. See `skills/SKILL_MESSAGES.md` for the full rule and worked examples. It's the same principle as §8, applied to individual messages rather than the final composite.
