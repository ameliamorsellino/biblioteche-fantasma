# Local SPARQL results

The `.rq` files were executed locally with PyOxigraph, an embedded disk-based RDF store.
No GraphDB server or external SPARQL endpoint is required.

- explicit triples in the local store: **1,656,407**
- queries executed in this run: **11**
- local store rebuilt in this run: **yes**

| Query | Rows | Seconds | Result |
|---|---:|---:|---|
| `01_status_distribution.rq` | 11 | 0.284 | `01_status_distribution.csv` |
| `02_status_by_region.rq` | 154 | 0.459 | `02_status_by_region.csv` |
| `03_inaccessible_special_collections.rq` | 0 | 0.313 | `03_inaccessible_special_collections.csv` |
| `04_demography_and_status.rq` | 538 | 1.017 | `04_demography_and_status.csv` |
| `05_library_mergers.rq` | 1,412 | 0.163 | `05_library_mergers.csv` |
| `06_external_links.rq` | 27,504 | 0.514 | `06_external_links.csv` |
| `07_demographic_filter.rq` | 98 | 0.469 | `07_demographic_filter.csv` |
| `08_region_aggregation.rq` | 20 | 0.357 | `08_region_aggregation.csv` |
| `09_temporary_closed_by_region.rq` | 44 | 0.455 | `09_temporary_closed_by_region.csv` |
| `10_material_type.rq` | 2,420 | 0.129 | `10_material_type.csv` |
| `11_library_municipality.rq` | 1 | 0.000 | `11_library_municipality.csv` |
