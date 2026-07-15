# Knowledge Graph — Legacy-to-Target Rule Map

This is the shared source of truth for both AI tooling and human reviewers. Every business rule extracted from the legacy estate becomes one row. AI tooling should query nodes here instead of re-deriving rules from raw legacy source once a node exists and is fresh.

**Freshness window:** a node older than 30 days without re-verification is stale and must be re-checked before use.

| Node ID | Rule (plain description) | Source (legacy) | Target component | Tolerance | Linked test | Linked parity check | Last verified | Status |
|---|---|---|---|---|---|---|---|---|
| RULE-0001 | Daily interest accrual, simple interest, 30/360 convention | `INTCALC.CBL` line 210 | `interest-accrual.service.ts` | Zero variance above 0.005 rounding | `TEST-0001` | `PCHK-0001` | 2026-07-01 | Verified |
| RULE-0002 | Overdraft fee waiver for accounts with balance > $X for 90 consecutive days | `FEEWAIV.CBL` line 88 | `fee-waiver.rules.ts` | Exact match | — | — | — | **Blind spot — no test, no parity check** |
| RULE-0003 | End-of-day batch posting order: fees before interest | `EODBATCH.JCL` step 4 | `eod-batch-orchestrator.ts` | Exact sequence match | `TEST-0014` | `PCHK-0007` | 2026-06-20 | Stale — re-verify |

## How to use this file

- **AI tooling:** query only the node(s) relevant to the module in scope. Do not load this entire table into context for a single-module task.
- **Adding a node:** every new node needs a Rule description, Source, Target, and Tolerance before it's usable — an empty Tolerance means "undefined," not "exact match by default."
- **Updating a node:** re-verifying a rule updates `Last Verified` and should reference the parity check that confirmed it, not just a manual read-through.
- **Blind spots:** any node missing a Linked test or Linked parity check is flagged by the Blind-Spot Scout automatically — see `checklists/regression-blindspot-checklist.md`.
