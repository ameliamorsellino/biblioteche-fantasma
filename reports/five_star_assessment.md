# 5-Star Open Data Assessment — Biblioteche Fantasma

## Scope

This assessment distinguishes the technical characteristics of the checkpoint from an actual Web publication. The evidence is taken from `HANDOFF_1.md`, `metadata/licenses_phase1.md`, the processed CSV files, and the Phase-2 RDF/interlinking artifacts.

| Level | Requirement | Concrete project evidence | Satisfied | Limitation |
|---|---|---|---|---|
| 1 STAR | Data available on the Web under an open licence | Phase 1 verifies ICCU Open Data as CC0 1.0 and ISTAT POSAS 2019/2025 as CC BY 4.0; the derived dataset is documented as CC BY 4.0 in `metadata/licenses_phase1.md` and `rdf/metadata.ttl`. | **Partially** | The licensing condition is satisfied, but this checkpoint is a local artifact and is not itself published at a public Web URL. |
| 2 STAR | Structured, machine-readable data | The checkpoint contains structured processed CSVs plus RDF serializations (`rdf/data.ttl`, `rdf/links.ttl`, `rdf/metadata.ttl`). | **Yes, technically** | This is a property of the released files, not proof of public Web availability. |
| 3 STAR | Non-proprietary open format | The processed datasets are CSV; ontology/data/links/metadata are Turtle/N-Triples-compatible RDF; SPARQL queries are plain text. | **Yes, technically** | Public hosting remains absent. |
| 4 STAR | Use RDF standards and URI identifiers | The graph uses RDF/OWL/SKOS/DCAT/PROV/GeoSPARQL/LOCN and deterministic HTTP(S)-shaped identifiers under `https://biblioteche-fantasma.invalid/`. | **Partially** | The `.invalid` authority is deliberately non-resolvable. Local URI identifiers are not public, dereferenceable Web URIs. |
| 5 STAR | Link local entities to external data | `rdf/links.ttl` contains real identifier-based links: libraries to official ICCU Anagrafe result pages via `rdfs:seeAlso`; municipalities to Linked ISPRA municipality resources via `owl:sameAs` where the six-digit ISTAT code identifies the same municipality. | **Partially** | External links exist, but the local side of the graph is not yet published/dereferenceable, so this is not an operational 5-star Linked Open Data publication. |

## Licensing evidence inherited from Phase 1

- **ICCU Anagrafe Open Data:** CC0 1.0 / public domain dedication.
- **ISTAT POSAS 2019 and 2025:** CC BY 4.0.
- **Cultural-ON ontology file:** CC BY 3.0 IT; included separately from the derived tabular data.
- **Derived tabular/RDF dataset:** project licensing decision is CC BY 4.0, with ISTAT attribution and ICCU source citation.

## What is missing for an operational 5-star publication

A real publication still requires all of the following operational steps:

1. acquisition/control of a real domain;
2. minting of stable public HTTP(S) URIs under that domain;
3. dereferencing of entity URIs, ideally with content negotiation between human-readable HTML and RDF representations;
4. Web exposure of the RDF distributions and dataset metadata at working `dcat:accessURL`/`dcat:downloadURL` locations;
5. stable publication and maintenance of the external links;
6. optionally, a public SPARQL endpoint or another public RDF access mechanism. A SPARQL endpoint is useful but is not by itself the defining requirement of the 5-star model.

## Final assessment

**The project is an interlinked RDF dataset technically prepared for a 5-star publication, but it is not yet published as a dereferenceable 5-star Linked Open Dataset on the Web.**

The limiting factor is not the absence of RDF or external links; it is the absence of a real Web publication layer for the project's own URI space.
