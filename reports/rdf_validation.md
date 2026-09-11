# RDF validation

## Result

- overall structural result: **PASS**
- errors: **0**
- warnings: **3**

## Parsing and graph size

- `rdf/data.ttl`: **1,628,669** triples; strict N-Triples parse PASS; therefore valid Turtle subset
- `rdf/links.ttl`: **27,504** triples; strict N-Triples parse PASS; therefore valid Turtle subset
- `rdf/metadata.ttl`: **39** triples; RDFLib Turtle parse PASS
- `ontology/ontology.ttl`: **195** triples; RDFLib Turtle parse PASS
- `ontology/ontology.owl`: **195** triples; RDF/XML parse PASS
- total import graph (ontology + data + metadata + links): **1,656,407** triples
- distinct predicates across ontology/data/metadata/links: **79**
- distinct instance `rdf:type` objects in data: **13**

## Entity counts by RDF type (instance data)

| Type | Count |
|---|---:|
| `https://ameliamorsellino.github.io/biblioteche-fantasma/ontology/HoldingObservation` | 93,512 |
| `http://dati.beniculturali.it/cis/Library` | 19,611 |
| `http://dati.beniculturali.it/cis/Site` | 19,611 |
| `https://ameliamorsellino.github.io/biblioteche-fantasma/ontology/LibraryStatusObservation` | 19,611 |
| `http://www.opengis.net/ont/geosparql#Feature` | 19,524 |
| `http://www.opengis.net/ont/geosparql#Geometry` | 19,524 |
| `http://dati.beniculturali.it/cis/Address` | 18,660 |
| `http://www.w3.org/ns/locn#Address` | 18,660 |
| `https://ameliamorsellino.github.io/biblioteche-fantasma/ontology/DemographicObservation` | 15,790 |
| `https://ameliamorsellino.github.io/biblioteche-fantasma/ontology/SpecialCollection` | 9,737 |
| `https://ameliamorsellino.github.io/biblioteche-fantasma/ontology/Municipality` | 7,896 |
| `http://www.w3.org/2004/02/skos/core#Concept` | 362 |
| `http://www.w3.org/2004/02/skos/core#ConceptScheme` | 7 |

## Integrity checks

- duplicate serialized triples in `data.ttl`: **0**
- duplicate serialized triples in `links.ttl`: **0**
- undefined local predicates used: **0**
- undefined local classes used: **0**
- dangling local resource targets (excluding distribution document URLs): **0**
- link subjects not present in data graph: **0**
- datatype lexical errors detected: **0**
- malformed URI errors detected: **0**


## Warnings / publication limits

- Project resource/ontology IRIs use the public GitHub Pages namespace; Web dereferenceability is verified separately after deployment.
- External targets were generated from identifier-based, documented URI rules; the runtime did not individually dereference all targets.
- N-Triples line serialization is used for data.ttl and links.ttl; N-Triples is a syntactic subset of Turtle.

## Validation scope

The validator checks parsing, URI syntax, selected XML Schema lexical forms, local ontology term declarations, link-subject existence, dangling project resources and exact duplicate serializations. SHACL constraints are reported separately in `reports/shacl_validation.md`.
