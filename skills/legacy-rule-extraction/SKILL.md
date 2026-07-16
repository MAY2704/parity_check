---
name: legacy-rule-extraction
version: 1.1.0
description: >
  Parses legacy source (COBOL, JCL, copybooks, and similar) using rule-based
  pattern matching and regular expressions to draft candidate business
  rules. Trigger when a legacy module has no corresponding node in the
  knowledge graph, or when a legacy module has changed since its node was
  last extracted.
inputs:
  - legacy_source_path: one module or file under context/legacy-source/
outputs:
  - candidate_rule: draft rule (description, source location, suspected
    tolerance, suspected data fields), status = unverified
requires_human_review: true
depends_on: []
reference: REFERENCE.md
---

# Skill: Legacy Rule Extraction

## What this skill does

Reads a legacy module and drafts candidate business-rule descriptions using deterministic pattern matching — never a free-form AI summary of "what this code probably does." A regex hit against a known pattern (a `COMPUTE` statement, a conditional block, a level-88 condition name) is traceable to an exact line; a paraphrase is not.

## Procedure

1. **Locate module boundaries.** Identify `PROCEDURE DIVISION` sections and paragraph names — a candidate rule is scoped to one paragraph, never a whole program, so it stays small enough to verify by hand.
2. **Apply the pattern catalog.** Run the regex patterns in `REFERENCE.md` against the paragraph to find calculation statements, conditional branches implying business logic, and level-88 condition names. Each hit becomes one candidate rule.
3. **Draft, don't finalize.** Every candidate rule is written with `status: unverified` and includes the exact source line reference. Never promote a candidate straight into the knowledge graph — that's a separate, human-gated step performed by the **knowledge-graph-builder** skill.
4. **Flag ambiguity instead of guessing.** If a pattern match is structurally ambiguous (nested conditionals, a `COMPUTE` spanning multiple `PERFORM`ed paragraphs), report the ambiguity explicitly rather than picking the most plausible interpretation. An unresolved ambiguity is a better outcome than a confident wrong guess.

## When to stop and ask a human

- A paragraph has no matching pattern at all but is clearly doing calculation (e.g., inline arithmetic without a `COMPUTE` verb) — the catalog has a gap, don't force a match.
- Two patterns overlap on the same lines with conflicting interpretations.

See `REFERENCE.md` for the full pattern catalog, COBOL-specific parsing notes (implied decimal points, sign handling, `PIC` clause interpretation), and worked examples.
