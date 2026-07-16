// ---------------------------------------------------------------------------
// Blind spots: rules with no heuristic check, no rule-engine oracle, and/or
// no parity check linked. Any missing edge is a finding on its own — nothing
// has to look wrong for a gap to be real.
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
// Precision / recall / F1 roll-up for a module across its evaluation
// history. Precision comes cheap — flag less, precision goes up. Recall is
// the number that actually costs something to earn, because a rule with no
// coverage contributes zero, not "unknown" — undefined coverage is treated
// as a recall failure, not left out of the average.
// ---------------------------------------------------------------------------
MATCH (r:BusinessRule {targetComponent: $module})
OPTIONAL MATCH (r)-[:HAS_PARITY_CHECK]->(p:ParityCheck)
RETURN
  r.uri AS rule,
  coalesce(p.hasPrecision, 0.0) AS precision,
  coalesce(p.hasRecall, 0.0)    AS recall,
  coalesce(p.hasF1, 0.0)        AS f1,
  CASE WHEN p IS NULL THEN true ELSE false END AS uncoveredRule;

// ---------------------------------------------------------------------------
// Confidence-score inputs: aggregated straight from the graph so the score
// is re-derivable by anyone with query access, not a black box.
// ---------------------------------------------------------------------------
MATCH (r:BusinessRule {targetComponent: $module})
OPTIONAL MATCH (r)-[:HAS_PARITY_CHECK]->(p:ParityCheck)
OPTIONAL MATCH (r)-[:HAS_TEST]->(t:Test)
OPTIONAL MATCH (r)-[:HAS_HEURISTIC_CHECK]->(h:HeuristicCheck)
RETURN
  r.uri AS rule,
  CASE WHEN p IS NULL THEN 0 ELSE p.matchRate END AS parityMatch,
  CASE WHEN t IS NULL THEN 0 ELSE 1 END AS hasTest,
  CASE WHEN h IS NULL THEN 0 ELSE 1 END AS hasHeuristic,
  CASE WHEN p IS NULL THEN 0 ELSE p.hasRecall END AS recall;
