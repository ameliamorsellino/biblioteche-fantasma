# RDF validation

## Result

- overall structural result: **PASS**
- errors: **0**
- warnings: **3**

## Parsing and graph size

- `rdf/data.ttl`: **1,616,865** triples; strict N-Triples parse PASS; therefore valid Turtle subset
- `rdf/links.ttl`: **27,504** triples; strict N-Triples parse PASS; therefore valid Turtle subset
- `rdf/metadata.ttl`: **38** triples; RDFLib Turtle parse PASS
- `ontology/ontology.ttl`: **195** triples; RDFLib Turtle parse PASS
- `ontology/ontology.owl`: **195** triples; RDF/XML parse PASS
- total import graph (ontology + data + metadata + links): **1,644,602** triples
- distinct predicates across ontology/data/metadata/links: **79**
- distinct instance `rdf:type` objects in data: **13**

## Entity counts by RDF type (instance data)

| Type | Count |
|---|---:|
| `https://biblioteche-fantasma.invalid/ontology/HoldingObservation` | 93,512 |
| `http://dati.beniculturali.it/cis/Library` | 19,611 |
| `http://dati.beniculturali.it/cis/Site` | 19,611 |
| `https://biblioteche-fantasma.invalid/ontology/LibraryStatusObservation` | 19,611 |
| `http://www.opengis.net/ont/geosparql#Feature` | 19,524 |
| `http://www.opengis.net/ont/geosparql#Geometry` | 19,524 |
| `http://dati.beniculturali.it/cis/Address` | 18,660 |
| `http://www.w3.org/ns/locn#Address` | 18,660 |
| `https://biblioteche-fantasma.invalid/ontology/DemographicObservation` | 15,790 |
| `https://biblioteche-fantasma.invalid/ontology/SpecialCollection` | 9,737 |
| `https://biblioteche-fantasma.invalid/ontology/Municipality` | 7,896 |
| `http://www.w3.org/2004/02/skos/core#Concept` | 358 |
| `http://www.w3.org/2004/02/skos/core#ConceptScheme` | 7 |

## Integrity checks

- duplicate serialized triples in `data.ttl`: **0**
- duplicate serialized triples in `links.ttl`: **0**
- undefined local predicates used: **0**
- undefined local classes used: **0**
- dangling local resource targets (excluding provisional download URLs): **0**
- link subjects not present in data graph: **0**
- datatype lexical errors detected: **0**
- malformed URI errors detected: **0**


## Warnings / publication limits

- Project resource/ontology IRIs intentionally use the reserved .invalid development domain and are not dereferenceable.
- External targets were generated from identifier-based, documented URI rules; the runtime did not individually dereference all targets.
- N-Triples line serialization is used for data.ttl and links.ttl; N-Triples is a syntactic subset of Turtle.

## Validation scope

The validator checks parsing, URI syntax, selected XML Schema lexical forms, local ontology term declarations, link-subject existence, dangling project resources and exact duplicate serializations. SHACL constraints are reported separately in `reports/shacl_validation.md`.
\n\n## SHACL execution status\n\nSHACL is documented separately from structural RDF parsing:\n\n- `pyshacl` was **not available** in the runtime;\n- `shacl/shapes.ttl` was created and parsed successfully;\n- the actual shapes were executed with `scripts/validate_shacl.py`, the project-local validator for the SHACL Core subset used by this project;\n- **82,519 focus nodes** were checked;\n- **0 constraint violations** were found in the executed subset;\n- this result **does not equal** a complete validation with pySHACL or GraphDB's SHACL engine.\n