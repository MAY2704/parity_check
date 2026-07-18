# Reference: Legacy Rule Extraction Pattern Catalog

Loaded only when the legacy-rule-extraction skill actually runs, kept out of the main SKILL.md so a routine invocation doesn't carry this whole catalog into context.

## Regex pattern catalog

| Pattern intent | Regex (illustrative) | Extracts |
|---|---|---|
| COMPUTE statement | `COMPUTE\s+([A-Z0-9-]+)\s*=\s*(.+?)\.` | target field, expression |
| Conditional business rule | `IF\s+(.+?)\s+(THEN)?\s*\n?\s*(.+?)(?=ELSE\|END-IF)` | condition, consequent |
| Level-88 condition name | `88\s+([A-Z0-9-]+)\s+VALUE(S)?\s+(.+?)\.` | named boolean condition and its underlying values |
| EVALUATE / WHEN branch | `WHEN\s+(.+?)\n\s*(.+?)(?=WHEN\|END-EVALUATE)` | case condition, action |
| PERFORM ... UNTIL (loop bound) | `PERFORM\s+(.+?)\s+UNTIL\s+(.+?)\.` | loop body reference, termination condition |
| Date arithmetic | `(ADD\|SUBTRACT)\s+(.+?)\s+(TO\|FROM)\s+([A-Z0-9-]+)` | operands, target; flag for calendar-convention review (30/360 vs actual/365 vs business-day) |

These are illustrative starting patterns, not an exhaustive grammar. COBOL dialects vary by mainframe vendor and shop-specific coding conventions. Extend the catalog as new constructs are encountered, and version-bump the skill (PATCH for a corrected pattern, MINOR for a new pattern category, MAJOR only if the candidate-rule output shape changes).

## COBOL-specific parsing notes

- **Implied decimal points.** A `PIC 9(7)V99` field has no literal decimal point in storage. A naive string extraction will misread the value by orders of magnitude. Always resolve `PIC` clauses before interpreting a numeric literal.
- **Sign handling.** `PIC S9(7)` fields can carry sign in a trailing overpunch character depending on `USAGE` (`COMP-3`, `DISPLAY`, etc.). Flag any extracted rule involving a signed field for explicit sign-convention confirmation.
- **Level-88 conditions often ARE the business rule.** `88 HIGH-RISK-ACCOUNT VALUE 'H' 'X'.` is frequently the clearest, most literal statement of a business rule anywhere in the program. Prioritize these matches over inferring the same logic from a scattered `IF` chain elsewhere.
- **Copybooks are shared state.** A field defined in a copybook may be used differently by every program that includes it. A candidate rule about a copybook field must record which program's usage it describes. Do not assume the rule generalizes across every program including that copybook.

## Worked example

Source (illustrative):
```cobol
       COMPUTE WS-ACCRUED-INT = WS-PRINCIPAL * WS-RATE * WS-DAYS / 360.
```

Candidate rule drafted:
```
id: candidate-rule-draft
description: "Simple interest accrual using a 360-day year convention"
source: "INTCALC.CBL, paragraph 2100-CALC-INTEREST, line 210"
suspected_fields: [WS-PRINCIPAL, WS-RATE, WS-DAYS, WS-ACCRUED-INT]
suspected_tolerance: unknown, requires domain SME input
status: unverified
```

Note what isn't claimed: no tolerance is guessed, no target-system mapping is proposed. Those come from a human reviewer and the knowledge-graph-builder skill, not from this extraction step.
