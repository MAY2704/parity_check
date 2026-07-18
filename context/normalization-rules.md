# Normalization Rules

Applied to **both sides** of every comparison (AI-generated output, golden dataset, and rule-engine output) before any diff runs. Comparing unnormalized output punishes formatting differences as if they were logic errors, which burns reviewer trust in the whole pipeline fast.

## Standard normalization steps

1. **Numeric rounding**: round to the tolerance defined on the rule's knowledge-graph node, not to a global default. A rule with `tolerance: 0` gets no rounding at all.
2. **Date/time format**: canonicalize to ISO 8601 before comparison. Legacy systems routinely emit `MMDDYY`, Julian dates, or locale-specific formats, none of which is a business difference.
3. **Currency representation**: strip symbols and thousands separators, then compare as decimal values, not display strings.
4. **Field ordering**: compare as a set of named fields, never as positional/ordinal output. Column order is a rendering detail, not a value.
5. **Null / empty representation**: `NULL`, `""`, `0`, and `"N/A"` are not interchangeable. Normalize each field to its declared type's canonical empty value and treat mismatches here as real findings, not noise to suppress.
6. **Whitespace and casing**: trim and case-fold only for fields explicitly marked case-insensitive on the knowledge-graph node. Default is case-sensitive; case differences in account IDs or codes are real defects until proven otherwise.
7. **Encoding**: normalize to UTF-8. EBCDIC-origin fields are a common source of false discrepancies if compared byte-for-byte instead of decoded first.

## Why normalization is its own stage

Skipping straight from "run the transformation" to "diff the output" conflates two different failure modes: the AI got the *value* wrong, or the AI got the *format* right but different from whatever golden-dataset extraction happened to produce. Only the first one is a defect. Treating both the same way either buries real errors under a pile of formatting noise, or trains reviewers to stop reading discrepancy reports carefully, which is how a real defect eventually gets waved through.
