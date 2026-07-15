# ParityKit

A minimal, markdown-native framework for catching parity failures and regression blind spots in legacy modernization work — built to run inside GitHub Copilot, using the same markdown-as-config pattern as GitHub Spec Kit and BMAD-METHOD, scoped to one job: don't let AI-assisted transformation claim confidence it can't prove.

## Why this exists

Spec Kit gives you Specify → Plan → Tasks → Implement as markdown artifacts. BMAD gives you markdown personas with commands and dependencies. Neither is built for the specific failure mode of modernization work: an agent that transforms legacy logic fluently and confidently, with no way to prove the output actually matches. ParityKit borrows the same primitives — markdown personas, reusable prompts, a shared context file — and points them entirely at that problem.

## How it maps to what you already know

| Spec Kit / BMAD concept | ParityKit equivalent |
|---|---|
| `.specify/` spec artifacts | `parity/knowledge-graph.md` — the shared source of truth |
| BMAD agent persona (`bmad-core/agents/*.md`) | `.github/chatmodes/*.chatmode.md` — Parity Auditor, Blind-Spot Scout |
| BMAD tasks / Spec Kit commands | `.github/prompts/*.prompt.md` — repeatable, scoped operations |
| Checklists | `parity/checklists/*.md` — pass criteria and open gaps |
| — (no direct equivalent) | `parity/evaluation-log.md` — the audit trail every run writes to |

## The four things this framework enforces

1. **Context check.** No module gets assessed until the relevant knowledge-graph nodes are confirmed present and fresh. Missing context is reported, never silently filled in by inference.
2. **Reliability (parity).** Every claim of "correct" traces to a field-by-field diff against a golden dataset — not a read-through that "looks right."
3. **Confidence score.** A transparent, four-component rubric (context completeness, parity match, blind-spot coverage, review status) — always shown with its breakdown, never as a bare number. One critical gap caps the score regardless of the average.
4. **Evaluation pipeline.** Every run — parity check, blind-spot scan, confidence score — writes to `evaluation-log.md`. That log, not a demo or a verbal summary, is what a human reviewer signs off against.

## Folder structure

```
.github/
  copilot-instructions.md          # loaded on every request — short, points to everything else
  chatmodes/
    parity-auditor.chatmode.md     # validates modules against golden data
    blindspot-scout.chatmode.md    # finds what isn't being checked at all
  prompts/
    run-parity-check.prompt.md
    scan-blindspots.prompt.md
    score-confidence.prompt.md
  instructions/
    migration-context.instructions.md   # scoped to src/migration/**
parity/
  knowledge-graph.md                # legacy rule -> target component -> tolerance -> evidence links
  golden-datasets/                  # historical production data, one set per module
  checklists/
    parity-checklist.md             # pass criteria + confidence rubric
    regression-blindspot-checklist.md
  evaluation-log.md                 # audit trail, append-only
```

## Quickstart

1. Copy this folder into your repo. In VS Code with Copilot, the chat modes appear in the mode dropdown automatically once `.github/chatmodes/` exists.
2. Populate `parity/knowledge-graph.md` with your first handful of extracted business rules before transforming any code — the graph comes first, not after.
3. Drop real historical batch data into `parity/golden-datasets/`, one set per module. Synthetic data misses the edge cases production already generated.
4. Switch to **Parity Auditor** mode and run `*context-check {module}`, then `*run-parity {module}`.
5. Switch to **Blind-Spot Scout** mode and run `*scan-blindspots {scope}` — do this even for modules that just passed parity. Passing and covered are different claims.
6. Check `parity/evaluation-log.md` before any sign-off conversation. If it's not in the log, it wasn't evaluated.

## What this is deliberately not

Not a scoring model, not an ML classifier, not an autonomous approver. The confidence score is arithmetic over evidence a human can re-check by hand. Sign-off authority stays with a named human owner at every tier above Low risk. The framework's only job is to make sure that when someone claims a migrated module is reliable, there's a paper trail proving it — and to make silence (missing tests, missing checks, missing context) visible instead of invisible.
