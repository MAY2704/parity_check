# Reference: Parity Evaluation Metrics & Methodology

Normalization rules themselves live in `context/normalization-rules.md`. This file covers the comparison methodology and the metric formulas — the part that doesn't change per module. Everything here is implemented in `scripts/parity_eval.py`; if this document and the script disagree, that is a bug, and fixing it is a PATCH on whichever side was wrong.

## Unit of analysis

One comparison unit is **one declared output field of one golden case** ("field-per-case"). "Every field compared, no sampling" is enforced over *fields*: all declared `output_fields` of every golden case are compared. It is deliberately **not** a claim about the input space — a 5-case golden dataset is still a 5-point sample of the domain, which is exactly what the dataset-adequacy score and differential fuzzing (below) exist to expose and compensate for.

## Field-level classification

Every comparison unit is classified into exactly one of:

| Class | Definition |
|---|---|
| **True Positive (TP)** | Flagged as a discrepancy. At run time every flag is a **provisional TP** (fail-closed: a flag is treated as a real defect until a human says otherwise). It stays TP if review confirms it as a real transformation error. |
| **False Positive (FP)** | Flagged, but reclassified by a recorded human review as `tolerance-acceptable` or `legacy-defect-now-fixed`. |
| **False Negative (FN)** | A missed defect: (a) any declared output field with no golden value for a case — no oracle coverage counts as *missed*, not *excluded*; (b) any escaped defect recorded in the review file (found downstream after a run that didn't flag it). |
| **True Negative (TN)** | Matched across every available oracle after normalization, within the field's tolerance. |

**Review file.** Human reclassifications and escaped defects live in `context/golden-datasets/{module}/review.json`:

```json
{
  "reclassifications": { "3:accrued_interest": "tolerance-acceptable" },
  "escaped_defects": [ { "unit": "n/a", "note": "rounding defect found in UAT 2026-08-02" } ]
}
```

Keys are `"{case_index}:{field}"` unit ids from the message's `discrepancies` array. Re-running the harness picks reclassifications up; nothing is reclassified by default.

**Coverage rule (unchanged in spirit from 2.x):** a unit with no oracle coverage contributes to **FN**, not to an excluded/unknown bucket. Treating an unchecked field as a missed defect is what stops an unevaluated module from silently scoring as "no discrepancies found." At module scope, a `BusinessRule` with no oracle at all still contributes its fields to FN in module-level reporting.

## Formulas and the degenerate-case conventions

```
Precision = TP / (TP + FP)        null when TP+FP = 0  (nothing was flagged)
Recall    = TP / (TP + FN)        null when TP+FN = 0  (no known or presumed defects)
Accuracy  = (TP + TN) / total     null when total = 0
F1        = 2PR / (P + R)         null when P or R is null, or P+R = 0
```

**A ratio whose denominator is zero is `null`, never 1.0.** This matters because the common case for a *good* artifact — clean run, nothing flagged, nothing known missed — is exactly the degenerate case. Reporting fabricated 1.0s there (as pre-3.0.0 runs did) laundered "we found nothing and had nothing to find it against" into "perfect score," and F1 fed 25% of the confidence composite. A null metric carries an explanatory entry in `metrics.degenerate_notes`, and `confidence-scoring` (≥2.1.0) applies an explicit fallback (see its `REFERENCE.md`) instead of substituting a number.

Two values are therefore always reported alongside, and are never null on a run that compared anything:

- **`match_rate`** = TN / (TP + FP + TN): plain agreement over the units actually compared.
- **`oracle_coverage`** = covered units / total units: how much of the module the oracles could see at all.

**Run-time vs. retrospective recall.** Recall as classically defined needs ground truth nobody has at evaluation time. The framework splits it honestly: at run time, FN counts only *known* misses (uncovered units + recorded escaped defects) — a computable, fail-closed proxy. Retrospectively, as escaped defects get recorded in `review.json`, re-running the harness recomputes recall against the growing FN set. Recall can therefore *drop* after a run is signed off. That is the metric working, not breaking.

- **Precision** answers: of what we flagged, how much was real. Cheap to inflate; flag less and precision rises even as real defects go uncaught.
- **Recall** is the number that costs real effort. Every additional oracle, heuristic, declared property, and fuzz case raises what it can see. Nothing raises it for free.
- **Accuracy** is the metric most easily distorted by class imbalance. Never report it without precision and recall alongside.
- **F1**, when defined, is the "Parity" component input in confidence scoring, so a system can't game the score by only flagging easy discrepancies.

## Worked example

Module has 40 units. 3 are flagged; review confirms 2 as real transformation errors (TP=2) and reclassifies 1 as tolerance-acceptable (FP=1). Of the 37 not flagged, 35 matched (TN=35) and 2 belong to a sibling rule with no oracle (FN=2).

```
Precision = 2 / (2 + 1)  = 0.67
Recall    = 2 / (2 + 2)  = 0.50
Accuracy  = (2 + 35) / 40 = 0.925
F1        = 2 × (0.67 × 0.50) / (0.67 + 0.50) = 0.57
```

Accuracy alone (92.5%) would look clean. Recall (50%) tells the real story. And a fully clean variant of this module (0 flagged, 0 uncovered) reports precision/recall/F1 = null with match_rate 1.0 — not a row of 1.0s.

## Differential fuzzing and boundary cases

When the rule config declares a `formula` (or `formulas`) and `input_domains`, the harness executes the artifact and the rule-engine formula over generated inputs and diffs the normalized outputs:

- **Boundary cases**: for every input, the domain min, max, midpoint, and any declared `boundary_values` (derived from the *documented rule* — day-count convention edges, thresholds — never from suspected artifact behavior), each pinned while other inputs are filled randomly, several fills per value.
- **Random cases**: `--fuzz N` (default 500) uniform draws over the declared domains, integer-aware, from a recorded `--seed` (default 1337) so any run is exactly reproducible.

Any divergence beyond the field's tolerance fails the run and appears (first 10) in `differential_fuzz.examples`. Fuzz divergences are reported separately from the golden confusion matrix: they are *caught* defects against the analytical oracle, pending the same human classification as any other discrepancy — not TNs, and not golden-comparison TPs.

This is the layer that breaks the golden dataset's coverage ceiling. In the demo module, five golden cases (all ≤ 45 days) match perfectly while 531 of 551 fuzz cases diverge — the planted day-count cap, caught numerically instead of only by the semantic read.

## Metamorphic property checks

Declared per rule in the config's `properties` list and checked against the artifact alone — no oracle values needed, so they hold even where no rule-engine implementation exists:

| Type | Declaration | Checks |
|---|---|---|
| `monotonic_nondecreasing` | `over: <input>` | Output never decreases as the input sweeps upward (random fills for the others). |
| `linear_in` | `over: <input>` | f(k·x) ≈ k·f(x) within rounding-scaled tolerance. |
| `zero_when` | `input: <name>`, `value: v` | Output is 0 whenever the pinned input equals `v`. |

Choose properties from the documented rule, and note their blind spots: a silent **cap produces a plateau, which still satisfies `monotonic_nondecreasing`** — it is `linear_in` over the same input that catches it (f(515 days) = f(103 days) fails k-scaling immediately). Declare both when the rule supports both. A property violation fails the run with a concrete counterexample.

## Golden-dataset adequacy

A clean comparison is only as strong as the dataset it ran against, so the dataset itself is scored (0–1):

```
adequacy = 0.25·volume + 0.35·range_coverage + 0.25·boundary_coverage + 0.15·provenance

volume            = min(1, case_count / target_case_count)      target: rule config `adequacy.target_case_count`, default 50
range_coverage    = mean over inputs of (observed span / declared domain span)
boundary_coverage = fraction of boundary values hit by some golden case (±0.5% of span)
provenance        = production 1.0 · mixed 0.7 · synthetic 0.3 · undeclared 0.0 (and a gap)
```

`provenance` is declared in `golden.json` — the parity checklist's "real historical production data, not synthetic samples only" is now a measured input, not an honor-system checkbox.

## Calibrated confidence

```
confidence = min(0.95,  0.50·oracle_factor + 0.25·adequacy + 0.25·fuzz_factor)

oracle_factor = 1.0 both oracles · 0.5 golden only
fuzz_factor   = min(1, fuzz_cases_run / 100), 0 when fuzzing didn't run
bands: ≥ 0.80 high · ≥ 0.50 medium · < 0.50 low
```

Confidence measures **evidence breadth, never the match rate**: a perfect match on a thin synthetic dataset with no fuzzing scores *low*, and nothing reaches `high` without either a strong dataset or a fuzzed second oracle on top of dual-oracle coverage. The 0.95 cap is deliberate: this skill never certifies; the semantic check and a named human remain downstream.

## Versioning note for this skill

- **PATCH**: a corrected formula implementation in `parity_eval.py`, or doc/script drift fixes.
- **MINOR**: a new property type, a new adequacy component, or a new field classification added.
- **MAJOR**: a change to the coverage rule, the degenerate-case conventions, the confidence formula, or which metrics are reported — `confidence-scoring` consumes these values directly.
- **3.0.0**: comparison moved from model-followed prose to `scripts/parity_eval.py`; degenerate metrics became null instead of fabricated 1.0s; added differential fuzzing, boundary generation, property checks, and dataset adequacy; confidence recalibrated to evidence breadth.
