# Reference: Knowledge Graph Ontology & Neo4j Sync

## Node types

| Class | Written by | Required fields | Human-gated? |
|---|---|---|---|
| `mig:BusinessRule` | this skill, from a confirmed extraction | description, sourceModule, targetComponent, tolerance, status | Yes |
| `mig:HeuristicCheck` | heuristic-validation skill | heuristicType, heuristicRule, severity | No |
| `mig:RuleEngineImpl` | this skill, from a domain-SME-authored rule-engine file | implementationRef, deterministic | Yes (authorship), No (linking) |
| `mig:AISemanticCheck` | ai-semantic-validation skill | independentDescription, agreementLevel, coincidentalMatchRisk, executedOn | No |
| `mig:ParityCheck` | parity-evaluation skill | matchRate, discrepancyCount, precision, recall, accuracy, f1, executedOn | No |

## Example write-back triples

Each write-back does two things: it creates the evidence node, and it links the `BusinessRule` to that node with the forward predicate (`hasParityCheck`, `hasAISemanticCheck`, and so on). The link edge points *from* the rule *to* the evidence, which is the direction the graph queries in `context/neo4j/queries.cypher` traverse. Writing only the node without the forward edge leaves the evidence unreachable from its rule.

A completed AI-semantic-validation run, written by this skill:

```turtle
rule:RULE-0001 mig:hasAISemanticCheck rule:ASEM-0001 .

rule:ASEM-0001 a mig:AISemanticCheck ;
    mig:independentDescription "Computes accrued interest as principal times rate times a day-count fraction" ;
    mig:agreementLevel          "aligned" ;
    mig:coincidentalMatchRisk   false ;
    mig:executedOn                "2026-07-16"^^xsd:date .
```

A completed parity-evaluation run:

```turtle
rule:RULE-0001 mig:hasParityCheck rule:PCHK-0002 .

rule:PCHK-0002 a mig:ParityCheck ;
    mig:comparedAgainst    "golden-dataset", "rule-engine" ;
    mig:matchRate            "1.0"^^xsd:decimal ;
    mig:discrepancyCount     0 ;
    mig:hasPrecision            "1.0"^^xsd:decimal ;
    mig:hasRecall                 "0.92"^^xsd:decimal ;
    mig:hasAccuracy                "0.97"^^xsd:decimal ;
    mig:hasF1                        "0.96"^^xsd:decimal ;
    mig:executedOn                    "2026-07-16"^^xsd:date .
```

## Neo4j sync

**Schema (run once, idempotent):**

```cypher
CREATE CONSTRAINT rule_uri_unique IF NOT EXISTS
FOR (r:BusinessRule) REQUIRE r.uri IS UNIQUE;

CREATE CONSTRAINT parity_uri_unique IF NOT EXISTS
FOR (p:ParityCheck) REQUIRE p.uri IS UNIQUE;
```

**Import (re-run after every TTL commit):**

```cypher
CALL n10s.graphconfig.init({handleVocabUris: "SHORTEN"});
CALL n10s.rdf.import.fetch("file:///data/knowledge-graph.ttl", "Turtle");
```

**Export (only if Neo4j was used as an editing surface for some workflow; TTL must stay authoritative):**

```cypher
CALL n10s.rdf.export.cypher(
  "MATCH (r:BusinessRule) RETURN r", {}, {}
) YIELD subject, predicate, object
RETURN subject, predicate, object;
```

Redirect the export output back into `context/knowledge-graph.ttl` and commit. Never let Neo4j hold state that isn't reflected in git.

## Versioning note for this skill

- **PATCH**: a fix to a Cypher query, a corrected constraint, a typo in the ontology doc.
- **MINOR**: a new node type or property added, backward-compatible with existing nodes (existing nodes remain valid without changes).
- **MAJOR**: an existing property is renamed, removed, or its meaning changes. Any change that would make an existing TTL file fail to import cleanly or import with different semantics.
