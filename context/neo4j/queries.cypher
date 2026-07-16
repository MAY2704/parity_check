// ---------------------------------------------------------------------------
// Blind spots: rules missing a heuristic check, rule-engine oracle, or
// parity check. Any one missing edge is a finding on its own — nothing has
// to look wrong for a gap to be real. (AISemanticCheck is deliberately not
// part of the blind-spot definition — it can only run once a ParityCheck
// exists, so its absence is downstream of the parity-check gap, not a
// separate blind spot to report twice.)
// ---------------------------------------------------------------------------
MATCH (r:BusinessRule)
WHERE NOT (r)-[:HAS_HEURISTIC_CHECK]->()
   OR NOT (r)-[:HAS_RULE_ENGINE_IMPL]->()
   OR NOT (r)-[:HAS_PARITY_CHECK]->()
RETURN r.uri AS rule, r.description AS description, r.status AS status
ORDER BY r.status DESC;

// ---------------------------------------------------------------------------
// Staleness: parity checks older than the freshness window. Different
// problem from a blind spot — this rule WAS checked, just not recently.
// ---------------------------------------------------------------------------
MATCH (r:BusinessRule)-[:HAS_PARITY_CHECK]->(p:ParityCheck)
WHERE date(p.executedOn) < date() - duration('P30D')
RETURN r.uri AS rule, p.executedOn AS lastChecked;

// ---------------------------------------------------------------------------
// Context assembly: the one- or two-hop neighborhood for a single module —
// this, not the full graph, is what gets serialized into model context.
// ---------------------------------------------------------------------------
MATCH (r:BusinessRule {targetComponent: $module})-[rel]-(n)
RETURN r, rel, n;

// ---------------------------------------------------------------------------
// Precision / recall / accuracy / F1 roll-up for a module. Precision comes
// cheap — flag less, precision goes up. Recall is the number that costs
// something to earn: a rule with no coverage contributes zero, not
// "unknown" — undefined coverage is a recall failure, never excluded from
// the average.
// ---------------------------------------------------------------------------
MATCH (r:BusinessRule {targetComponent: $module})
OPTIONAL MATCH (r)-[:HAS_PARITY_CHECK]->(p:ParityCheck)
RETURN
  r.uri AS rule,
  coalesce(p.hasPrecision, 0.0) AS precision,
  coalesce(p.hasRecall, 0.0)    AS recall,
  coalesce(p.hasAccuracy, 0.0)  AS accuracy,
  coalesce(p.hasF1, 0.0)        AS f1,
  CASE WHEN p IS NULL THEN true ELSE false END AS uncoveredRule;

// ---------------------------------------------------------------------------
// Coincidental-match risk: modules with a high parity match rate but a
// semantic agreement level that isn't "aligned". This is the query that
// catches an artifact passing numerically without implementing the rule —
// the single most important query in this file.
// ---------------------------------------------------------------------------
MATCH (r:BusinessRule)-[:HAS_PARITY_CHECK]->(p:ParityCheck)
MATCH (r)-[:HAS_AI_SEMANTIC_CHECK]->(a:AISemanticCheck)
WHERE p.matchRate >= 0.95 AND a.agreementLevel <> "aligned"
RETURN r.uri AS rule, p.matchRate AS matchRate, a.agreementLevel AS agreementLevel,
       a.coincidentalMatchRisk AS flagged;

// ---------------------------------------------------------------------------
// Confidence-score inputs: aggregated straight from the graph so the score
// is re-derivable by anyone with query access, not a black box. Review
// Status is not graph-resident — pull it from output/evaluation-log.md
// separately and combine at the scoring step.
// ---------------------------------------------------------------------------
MATCH (r:BusinessRule {targetComponent: $module})
OPTIONAL MATCH (r)-[:HAS_PARITY_CHECK]->(p:ParityCheck)
OPTIONAL MATCH (r)-[:HAS_HEURISTIC_CHECK]->(h:HeuristicCheck)
OPTIONAL MATCH (r)-[:HAS_RULE_ENGINE_IMPL]->(e:RuleEngineImpl)
OPTIONAL MATCH (r)-[:HAS_AI_SEMANTIC_CHECK]->(a:AISemanticCheck)
RETURN
  r.uri AS rule,
  CASE WHEN p IS NULL THEN 0 ELSE p.hasF1 END       AS parityF1,
  CASE WHEN p IS NULL THEN 0 ELSE p.hasRecall END    AS recallFloor,
  CASE WHEN h IS NULL THEN 0 ELSE 1 END              AS hasHeuristic,
  CASE WHEN e IS NULL THEN 0 ELSE 1 END              AS hasRuleEngine,
  CASE WHEN a IS NULL THEN 0
       WHEN a.agreementLevel = "aligned" THEN 100
       WHEN a.agreementLevel = "partially-aligned" THEN 50
       ELSE 0 END                                     AS semanticAgreementScore,
  CASE WHEN a IS NULL THEN false ELSE a.coincidentalMatchRisk END AS coincidentalMatchRisk;
