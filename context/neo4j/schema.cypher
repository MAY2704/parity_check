// Run once, idempotent. Re-run safely after any import.

CREATE CONSTRAINT rule_uri_unique IF NOT EXISTS
FOR (r:BusinessRule) REQUIRE r.uri IS UNIQUE;

CREATE CONSTRAINT parity_uri_unique IF NOT EXISTS
FOR (p:ParityCheck) REQUIRE p.uri IS UNIQUE;

CREATE CONSTRAINT heuristic_uri_unique IF NOT EXISTS
FOR (h:HeuristicCheck) REQUIRE h.uri IS UNIQUE;

CREATE CONSTRAINT semantic_uri_unique IF NOT EXISTS
FOR (a:AISemanticCheck) REQUIRE a.uri IS UNIQUE;

CREATE CONSTRAINT ruleengine_uri_unique IF NOT EXISTS
FOR (e:RuleEngineImpl) REQUIRE e.uri IS UNIQUE;

// Helpful for the context-assembly query, which filters by targetComponent
CREATE INDEX rule_target_component IF NOT EXISTS
FOR (r:BusinessRule) ON (r.targetComponent);
