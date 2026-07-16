# Output

Every run of the agent against an artifact in `input/artifacts/` produces two things here:

```
output/
  reports/
    {module}-{YYYY-MM-DD}.md    <- full test report for that run
  evaluation-log.md              <- append-only audit trail, one entry per run
```

## `reports/{module}-{date}.md`

The full, human-readable output of a single evaluation: heuristic result, normalization notes, dual-comparison discrepancies, semantic-agreement finding, precision/recall/accuracy/F1, and the six-component confidence score with its breakdown. This is what gets attached to a sign-off request.

## `evaluation-log.md`

The audit trail. Every report also gets a compact entry appended here — this is the file a reviewer scans across many modules to see program-wide status, and it's what `confidence-scoring` reads `review_status` from. Never delete or edit prior entries; append only.

Nothing in `output/` is an input to another evaluation run — it's a record of what happened, not a source of truth the agent reads back from (that's what `context/` and the knowledge graph are for).
