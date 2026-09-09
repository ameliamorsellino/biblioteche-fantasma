# Checkpoint 2 — final control

## Core RDF parsing

- `ontology/ontology.ttl`: PASS, **195** triples.
- `ontology/ontology.owl`: PASS, **195** triples.
- `rdf/data.ttl`: PASS as strict N-Triples/Turtle subset, **1,616,865** triples.
- `rdf/links.ttl`: PASS as strict N-Triples/Turtle subset, **27,504** triples.
- `rdf/metadata.ttl`: PASS, **38** triples.
- `shacl/shapes.ttl`: PASS, **80** shape-graph triples.
- total explicit import graph: **1,644,602** triples.
- distinct predicates across ontology/data/links/metadata: **79**.
- malformed URI errors found by the final streaming control: **0**.
- local namespace anomalies: **0**.

## Required artifacts

- mandatory core files non-empty: **PASS**.
- mandatory processed files for Prompt 3 non-empty: **PASS**.
- empty files detected in the working checkpoint before release packaging: **0**.

## SPARQL

- queries found: **11**.
- queries passing RDFLib parser: **11/11**.
- `01_status_distribution.rq` was actually executed on the existing local projection and returned **11** rows; result saved in `sparql/results/01_status_distribution.csv`.
- `02_status_by_region.rq` was attempted but did not complete within the RDFLib operational budget; it is not marked executed.
- remaining queries are syntax-validated only in the final closure.

## Interlinking

- library link rows: **19,611**; exact ISIL lookup: **19,611**.
- municipality link rows: **7,896**; exact ISTAT-code identity links: **7,893**; temporal-scope non-match: **3**.
- non-matches: Castegnero (`024027`), Lirio (`018082`), Nanto (`024071`).

## SHACL

`pyshacl` was not available. `shacl/shapes.ttl` was nevertheless executed with the project-local validator implementing the SHACL Core features used by the shapes. The executed subset checked **82,519 focus nodes** and found **0 violations**. This is not equivalent to a complete pySHACL or GraphDB SHACL validation.

## Release warnings

1. project URIs use the reserved `.invalid` development authority and are not dereferenceable;
2. GraphDB was not executed;
3. SHACL validation is limited to the implemented Core subset;
4. SPARQL execution coverage is partial because RDFLib performance was insufficient for the full suite;
5. three 2025 municipalities are intentionally not linked to current 2026 Linked ISPRA municipality resources;
6. external Web resources can change after the checkpoint date and should be rechecked before publication.
