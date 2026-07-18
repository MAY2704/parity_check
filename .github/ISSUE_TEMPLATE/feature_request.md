---
name: Feature request
about: Propose a new skill, check, override, or capability
title: "[feature] "
labels: enhancement
---

## The gap

What can't the framework do today, or what does it do in a way that hides a real risk?

## Proposed change

- [ ] New skill
- [ ] New heuristic / check type
- [ ] New confidence-score component or override
- [ ] Ontology / schema addition
- [ ] Tooling or docs

Describe the change and where it fits in the pipeline (`.github/chatmodes/parity-auditor.chatmode.md`).

## Impact on existing contracts

Does this change a skill's input/output shape, the message schema, or a classification scheme? If so, note the version bump it would require (see `SKILLS_CHANGELOG.md`) and which consumers' `depends_on` would need review.

## How it keeps the framework honest

ParityKit's premise is that no number is trusted without evidence a human can re-derive. Explain how the proposed change preserves that (fail-closed defaults, single writer to the graph, human sign-off gates). See `BEST_PRACTICES.md`.
