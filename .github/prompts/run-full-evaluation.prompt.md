---
description: 'Run the full three-phase evaluation pipeline (read input, execute process, generate output) for one artifact under test.'

---

Evaluate `${input:module}` end to end, following the three-phase pipeline defined in `.github/chatmodes/parity-auditor.chatmode.md`: Phase 1 (Read Input) locates the artifact and the graph node and reports the gap if either is missing or stale; Phase 2 (Execute Process) runs all six skills strictly in the order and with the stop conditions that file specifies, each emitting one JSON message per `context/schemas/skill-message.schema.json` tagged with a shared `run_id`; Phase 3 (Generate Output) writes the results.

Do not skip a phase, reorder Phase 2, or shortcut a stage because an earlier one looks like it obviously passed.

Write the report to `output/reports/${input:module}-{date}.md`, the full message chain to `output/reports/${input:module}-{date}.json`, append a compact entry to `output/evaluation-log.md`, and output: `PASS / FAIL / NEEDS-REVIEW — confidence {score}/100 ({band}) — precision {p} / recall {r} / accuracy {a} / F1 {f1}`.
