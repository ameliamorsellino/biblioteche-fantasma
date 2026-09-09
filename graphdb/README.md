# GraphDB import guide — Biblioteche Fantasma

## Status

This checkpoint is **IMPORT-READY**, but GraphDB was **not executed in the production session**. No GraphDB screenshot, repository statistic, inference result, or query result is claimed here.

## 1. Create a repository

Using GraphDB Workbench:

1. open **Setup → Repositories → Create new repository**;
2. choose a repository ID such as `biblioteche-fantasma`;
3. for the reproducibility baseline, select **no inference / empty ruleset** (or the GraphDB equivalent that does not materialize inferred triples);
4. create the repository.

The baseline recommendation is no inference because the dataset already materializes the types and relations used by the supplied queries. Enabling an RDFS/OWL ruleset can legitimately create inferred statements and therefore make triple counts differ from the validated raw-import count of **1,644,602**. If reasoning is scientifically useful, use a separate repository or clearly distinguish explicit from inferred counts.

## 2. Files to import

Recommended order:

1. `ontology/ontology.ttl`
2. `rdf/data.ttl`
3. `rdf/links.ttl`
4. `rdf/metadata.ttl`

All four files have been parsed successfully in the checkpoint's local validation.

## 3. Named-graph strategy

For maximum provenance and easier count checks, import each artifact into a distinct named graph:

- ontology: `https://biblioteche-fantasma.invalid/graph/ontology`
- data: `https://biblioteche-fantasma.invalid/graph/data`
- links: `https://biblioteche-fantasma.invalid/graph/links`
- metadata: `https://biblioteche-fantasma.invalid/graph/metadata`

These graph IRIs are internal development identifiers and are not public Web endpoints. Importing everything into the default graph is also possible, but named graphs make provenance and explicit-triple counts clearer.

Expected explicit triple counts before inference:

| File | Triples |
|---|---:|
| `ontology/ontology.ttl` | 195 |
| `rdf/data.ttl` | 1,616,865 |
| `rdf/links.ttl` | 27,504 |
| `rdf/metadata.ttl` | 38 |
| **Total** | **1,644,602** |

## 4. Import in Workbench

1. select the repository;
2. open **Import → User data**;
3. upload each file in the order above;
4. when using named graphs, set the target context explicitly for each upload;
5. execute the import and check that no parser error is reported.

The large `rdf/data.ttl` file is serialized as strict N-Triples syntax, which is a valid subset of Turtle even though the extension is `.ttl`.

## 5. Verify triple counts

Without reasoning and with all data in the default graph:

```sparql
SELECT (COUNT(*) AS ?triples)
WHERE { ?s ?p ?o }
```

With named graphs:

```sparql
SELECT ?graph (COUNT(*) AS ?triples)
WHERE {
  GRAPH ?graph { ?s ?p ?o }
}
GROUP BY ?graph
ORDER BY ?graph
```

To count only explicit instance data in the proposed data graph:

```sparql
SELECT (COUNT(*) AS ?triples)
WHERE {
  GRAPH <https://biblioteche-fantasma.invalid/graph/data> { ?s ?p ?o }
}
```

Expected result: `1616865` if no inference and no duplicate import has occurred.

## 6. Execute the supplied SPARQL queries

Files are in `sparql/`. In Workbench:

1. open **SPARQL**;
2. paste a `.rq` file;
3. execute against the repository;
4. if named graphs are used and GraphDB is configured not to merge them into the active default dataset, either configure the dataset in Workbench or add the appropriate `FROM` clauses / `GRAPH` patterns.

The queries were authored to work over the union of ontology/data/links/metadata. They do not require GraphDB-specific syntax.

## 7. Example Competency Question tests

- CQ1 — temporarily closed libraries in a region: `sparql/09_temporary_closed_by_region.rq`
- CQ2 — inaccessible libraries with special collections: `sparql/03_inaccessible_special_collections.rq`
- CQ3 — municipality of a library: `sparql/11_library_municipality.rq`
- CQ4 — merger/confluence target: `sparql/05_library_mergers.rq`
- CQ5 — service interruption plus demographic decline: `sparql/04_demography_and_status.rq`
- CQ6 — material type: `sparql/10_material_type.rq`
- CQ7 — external links: `sparql/06_external_links.rq`
- CQ8 — state distribution by region: `sparql/02_status_by_region.rq` / `08_region_aggregation.rq`
- CQ9 — high population loss and problematic-library share: `sparql/07_demographic_filter.rq`

Replace `VALUES` parameters in parameterized queries only when the CQ requires a specific region, ISIL, or material type.

## 8. Reasoning recommendation

For the reproducibility baseline, **do not enable reasoning**. The explicit graph is the validated scientific artifact and the published counts refer to explicit triples. If inference is evaluated later, run it as a separate experiment and document:

- GraphDB ruleset;
- inferred triple count;
- effect on query answers;
- any ontology inconsistencies.

## 9. SHACL in GraphDB

`shacl/shapes.ttl` is available for a later validation with GraphDB's SHACL engine if the chosen GraphDB edition/configuration supports it. The checkpoint itself did not execute GraphDB SHACL. The local Phase-2 SHACL result used the project-local SHACL Core subset executor described in `reports/shacl_validation.md`.

## 10. Session limitation

GraphDB was not installed/executed in this session. Therefore the repository creation, imports, reasoning and queries described above are operational instructions, **not recorded GraphDB execution results**.
