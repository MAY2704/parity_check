// One-time / per-sync import. TTL in git is the source of truth;
// this script is how it becomes queryable. Re-run on every merge to
// parity/knowledge-graph.ttl. Do not hand-edit the graph in Neo4j directly,
// or Neo4j and the reviewable git history will drift apart.

CALL n10s.graphconfig.init({handleVocabUris: "SHORTEN"});

CALL n10s.rdf.import.fetch(
  "file:///data/knowledge-graph.ttl",
  "Turtle"
);

// Sanity check after import: every BusinessRule should be reachable.
MATCH (r:BusinessRule) RETURN count(r) AS ruleCount;
