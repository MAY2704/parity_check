# Reference: Heuristic Check Catalog

## Check types

| Type | Example expression | Catches |
|---|---|---|
| `range` | `accrued_interest >= 0 AND accrued_interest <= principal * 0.15` | negative or implausibly large values |
| `sign` | `fee_amount <= 0` | a fee that's positive when it should represent a deduction, or vice versa |
| `sum_to_total` | `sum(line_items) == statement_total` | a total that doesn't reconcile with its components |
| `calendar_validity` | `posting_date IN business_calendar` | a posting date falling on a weekend/holiday when the legacy system never would have |
| `format` | regex against the field | a field that doesn't match its expected shape (account number length, currency code) |
| `referential` | `account_id EXISTS IN accounts_master` | output referencing an account that doesn't exist in the target system |

## Writing a new heuristic for an uncovered rule

1. Ask a domain expert for the *cheapest possible* sanity bound on the rule's output, not the full rule logic, just "what would obviously be wrong."
2. Prefer a bound that's robust to legitimate edge cases. A fee-waiver rule might legitimately produce a zero fee; don't write a heuristic that treats zero as always invalid.
3. Default new heuristics to `severity: warn` until they've run clean against a batch of known-good historical output, and promote to `block` only once the false-positive rate is understood. A heuristic that blocks the pipeline on a false positive is worse than no heuristic at all, because it trains reviewers to override warnings without reading them.

## Versioning note for this skill

- **PATCH**: a corrected threshold or expression for an existing heuristic.
- **MINOR**: a new check type added to the catalog.
- **MAJOR**: a change to how severity levels are interpreted, or a change that would alter pass/fail outcomes for existing heuristics without their expressions changing.
