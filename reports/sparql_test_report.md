# SPARQL test report

All 11 `.rq` files were re-read from disk and parsed with RDFLib 7.5.0 `parseQuery`. Parsing succeeded for every query. Execution status is deliberately reported separately from syntax status.

The local execution aid is a predicate-preserving projection of the actual `rdf/data.ttl` + `rdf/links.ttl`; it contains no synthesized values. It is not GraphDB and it does not test GraphDB reasoning or optimizer behavior.

| File | Purpose | CQ / RQ | Parsing | Actually executed in final closure | Saved result | Limitation |
|---|---|---|---|---|---|---|
| `01_status_distribution.rq` | National distribution of observed states | CQ8; supports RQ1–RQ2 | PASS | **Yes** | `sparql/results/01_status_distribution.csv` (11 rows) | Executed with RDFLib on the existing projection, not GraphDB. |
| `02_status_by_region.rq` | State distribution by region | CQ1, CQ8; RQ1–RQ2 | PASS | **No (attempt did not complete)** | none | RDFLib execution exceeded the operational time budget; not reported as executed. |
| `03_inaccessible_special_collections.rq` | Inaccessible libraries with special collections | CQ2; RQ5 | PASS | No | none | Syntax only in final closure. |
| `04_demography_and_status.rq` | Service interruption joined with 2019–2025 population decline | CQ5; RQ4 | PASS | No | none | Syntax only; multi-join query left for GraphDB/Prompt 3 validation. |
| `05_library_mergers.rq` | Validated merger/confluence targets | CQ4; RQ7 | PASS | No | none | Execution attempt through the full RDFLib projection workflow was not completed within the operational budget. |
| `06_external_links.rq` | External ICCU/Linked ISPRA links | CQ7; RQ6 | PASS | No | none | Syntax only in final closure. |
| `07_demographic_filter.rq` | Municipalities with ≥10% loss ranked by problematic-library share | CQ9; RQ4 | PASS | No | none | Aggregation/subqueries not run locally in final closure. |
| `08_region_aggregation.rq` | Regional aggregation of libraries/problematic states | CQ8; RQ1–RQ2 | PASS | No | none | Aggregation not run locally in final closure. |
| `09_temporary_closed_by_region.rq` | Parameterized temporarily closed libraries for a region | CQ1; RQ1–RQ2 | PASS | No | none | Syntax only; `VALUES` currently uses Lazio as example parameter. |
| `10_material_type.rq` | Libraries possessing a selected material type | CQ6; RQ5 | PASS | No | none | Syntax only; material parameter is explicit in `VALUES`. |
| `11_library_municipality.rq` | Municipality of a selected library | CQ3 | PASS | No | none | Syntax only; ISIL parameter is explicit in `VALUES`. |

## Verified execution result

`01_status_distribution.rq` was executed during checkpoint closure after loading the existing projection graph. It returned **11 rows**, consistent with the 11 normalized status concepts in the processed status table. The result file was rewritten from that execution.

## Interpretation

- **Syntax coverage:** 11/11 PASS.
- **Execution coverage in final closure:** 1/11 completed and saved.
- GraphDB execution: **not performed**.
- No result is claimed for a query whose execution did not complete.
