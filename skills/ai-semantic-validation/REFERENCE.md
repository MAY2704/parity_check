# Reference: AI Semantic Validation Methodology

## The blind-read discipline

Order matters more than thoroughness here. Reading the documented rule first and then checking whether the code "seems consistent with it" produces confirmation-shaped answers almost every time: plausible-sounding code will always seem to match a rule you already have in front of you. Reading the code first, describing it cold, and only then comparing against the documented rule is what actually surfaces divergence.

Structure the independent read around three questions, answered from the code alone:
1. What are the actual inputs and where do they come from?
2. What is the branching structure? Every `if`/`case`/exception path, not just the main line.
3. What does each branch actually compute or return?

## Known false-agreement traps

- **Golden-dataset memorization.** The pattern most worth checking for in AI-generated migration code: special-cased handling of specific account numbers, specific date ranges, or specific values that happen to appear in the golden dataset, instead of a general implementation of the rule. This produces a perfect parity match rate while implementing nothing generalizable, and it's a failure mode numeric comparison alone cannot detect, because the numbers are correct. Look explicitly for literal values, ID lists, or conditionals keyed on data that looks like it came from the test set rather than from the business rule.
- **Narrow-case coverage.** An implementation that handles the common path correctly but silently no-ops or falls through on an exception path the golden dataset didn't happen to exercise (e.g., the fee-waiver rule's 90-day condition, if the golden dataset only contains accounts already past day 90 or accounts nowhere close).
- **Right answer, wrong mechanism.** Logic that arrives at matching output through an unrelated calculation: coincidentally close for the tested range, but not the same function, and not guaranteed to hold outside it.

## Worked example: a caught coincidental match

**Independent read (blind):** "This function returns a fixed waiver flag of `true` for account IDs in a hard-coded list of six values, and `false` otherwise. No date or balance calculation is present."

**Documented rule (RULE-0002):** "Overdraft fee waiver for accounts with balance above threshold for 90 consecutive days."

**Agreement level:** `contradicts`

**Parity result:** 100% match against the golden dataset (which happened to contain exactly those six accounts).

**Coincidental match risk:** `true`, flagged as the primary finding, ahead of and independent from the 100% match rate. A confidence score built from the match rate alone would have shown this module as fully reliable.

## Versioning note for this skill

- **PATCH**: refinement to the blind-read question set, an additional worked example.
- **MINOR**: a new category added to the false-agreement trap catalog.
- **MAJOR**: a change to the `agreement_level` classification scheme itself, since `confidence-scoring` reads that value directly.
