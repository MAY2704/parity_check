# Output

Every run of the agent against an artifact in `input/artifacts/` produces two things here:

```
output/
  reports/
    {module}-{YYYY-MM-DD}.md      <- full, human-readable test report for that run
    {module}-{YYYY-MM-DD}.json     <- the full chain of JSON skill messages for that run, same run_id
  evaluation-log.md                <- append-only audit trail, one entry per run
```

## `reports/{module}-{date}.md`

The full, human-readable output of a single evaluation: heuristic result, normalization notes, dual-comparison discrepancies, semantic-agreement finding, precision/recall/accuracy/F1, and the six-component confidence score with its breakdown. This is what gets attached to a sign-off request.

## `reports/{module}-{date}.json`

The machine-readable companion: every JSON message emitted by every skill during the run, in order, sharing one `run_id`, each carrying its own `confidence` (`value`/`band`/`basis`/`source`) per `context/schemas/skill-message.schema.json`. This is what lets a run be re-validated, diffed against a later run, or audited programmatically — the `.md` report is for a human to read, this file is for tooling to check.

## `evaluation-log.md`

The audit trail. Every report also gets a compact entry appended here — this is the file a reviewer scans across many modules to see program-wide status, and it's what `confidence-scoring` reads `review_status` from. Never delete or edit prior entries; append only.

Nothing in `output/` is an input to another evaluation run — it's a record of what happened, not a source of truth the agent reads back from (that's what `context/` and the knowledge graph are for).
