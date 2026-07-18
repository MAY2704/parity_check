# Changelog

All notable changes to ParityKit are recorded here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Individual skill versions move independently and are tracked in `SKILLS_CHANGELOG.md`. This file records the framework as a whole: structure, tooling, and the version stamped in `VERSION`.

## [3.0.0] - 2026-07-18

### Added
- Open-source scaffolding: `LICENSE` (MIT), `CONTRIBUTING.md`, `.gitignore`, and a CI workflow (`.github/workflows/validate.yml`).
- `scripts/validate_skills.py` with `scripts/requirements.txt`: checks that each skill's frontmatter version matches `SKILLS_CHANGELOG.md`, and that every embedded message example and logged report validates against `context/schemas/skill-message.schema.json`. CI runs it on every push and pull request.
- Issue and pull-request templates under `.github/`.
- A worked end-to-end demo module (`interest-accrual-demo`) covering artifact, golden dataset, rule-engine oracle, graph nodes, and a full run report, including a deliberately planted divergence that trips the coincidental-match-risk override.

### Changed
- Every skill moved to the shared JSON message envelope (`context/schemas/skill-message.schema.json`); all six skills bumped to 2.0.0 as a set. See `SKILLS_CHANGELOG.md`.
- Confidence messages now carry a typed `source` (`calibrated` vs `self-reported`) and the propagation rule is enforced in `confidence-scoring`: self-reported confidence may lower a composite score, never raise it.

### Fixed
- Standardized the `coincidental_match_risk` field name across the JSON-message layer (was mixed snake_case / camelCase); the RDF layer keeps `mig:coincidentalMatchRisk` and the snake-to-camel translation on write is documented as serialization only.
- Clarified `depends_on` semantics: it describes persisted graph state that must already exist, not this-run execution order.
- Removed a dangling `mig:hasTest`/`TEST-0001` reference that was never defined in the ontology.
- Aligned `context/neo4j/queries.cypher` relationship types to the TTL predicate local-names that `n10s` produces on import; previously the queries would have matched nothing.
- Corrected the `knowledge-graph-builder` write-back examples to link evidence with the forward predicate the queries traverse, and added the missing `RuleEngineImpl` uniqueness constraint to `schema.cypher`.

[3.0.0]: https://github.com/MAY2704/parity_check/releases/tag/v3.0.0
