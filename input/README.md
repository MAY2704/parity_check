# Input

Drop the artifact you want evaluated into `artifacts/`, one module per subfolder:

```
input/artifacts/
  interest-accrual/
    interest-accrual.service.ts     <- the artifact under test
    harness.mjs                     <- execution adapter for scripts/parity_eval.py
  fee-waiver/
    fee-waiver.rules.ts
    harness.mjs
```

The subfolder name should match the `targetComponent` used on the corresponding `BusinessRule` node in `context/knowledge-graph.ttl`. This is how the agent finds the right rule, oracle, and golden dataset for the artifact without you having to specify them by hand.

## The execution harness

`harness.mjs` is a small adapter that lets the deterministic parity harness actually *run* the artifact instead of anyone simulating it. It exports one function mapping ParityKit's named case inputs (the fields declared in the rule config and used in the golden dataset) onto the artifact's real call signature:

```js
import { computeAccruedInterest } from "./interest-accrual.service.ts";

export function runCase({ principal, annual_rate, days_elapsed }) {
  return { accrued_interest: computeAccruedInterest(principal, annual_rate, days_elapsed) };
}
```

`scripts/run_artifact.mjs` invokes it under node (≥ 22.6 for TypeScript artifacts; async `runCase` is fine). Without a harness, `scripts/parity_eval.py` can still compare a precomputed output file via `--artifact-output`, but differential fuzzing and property checks are skipped and reported as a gap — a module with a harness earns strictly stronger evidence.

If no matching `BusinessRule` node exists yet, the agent will report that as a context-completeness gap rather than guessing. Extract the rule first (`legacy-rule-extraction` skill) and get it human-confirmed before expecting a meaningful evaluation.

This folder is for the artifact under test only. Golden datasets, rule-engine implementations, and legacy source live in `context/`. Keeping them separate is deliberate; see `BEST_PRACTICES.md` §10.
