# Input

Drop the artifact you want evaluated into `artifacts/`, one module per subfolder:

```
input/artifacts/
  interest-accrual/
    interest-accrual.service.ts     <- the artifact under test
  fee-waiver/
    fee-waiver.rules.ts
```

The subfolder name should match the `targetComponent` used on the corresponding `BusinessRule` node in `context/knowledge-graph.ttl`. This is how the agent finds the right rule, oracle, and golden dataset for the artifact without you having to specify them by hand.

If no matching `BusinessRule` node exists yet, the agent will report that as a context-completeness gap rather than guessing. Extract the rule first (`legacy-rule-extraction` skill) and get it human-confirmed before expecting a meaningful evaluation.

This folder is for the artifact under test only. Golden datasets, rule-engine implementations, and legacy source live in `context/`. Keeping them separate is deliberate; see `BEST_PRACTICES.md` §10.
