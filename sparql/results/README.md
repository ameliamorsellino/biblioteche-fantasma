# Local SPARQL results

The `.rq` files were executed locally with PyOxigraph, an embedded disk-based RDF store.
No GraphDB server or external SPARQL endpoint is required.

- explicit triples in the local store: **1,656,407**
- queries executed in this run: **11**
- local store rebuilt in this run: **yes**

| Query | Rows | Seconds | Result |
|---|---:|---:|---|
| `01_status_distribution.rq` | 11 | 0.274 | `01_status_distribution.csv` |
| `02_status_by_region.rq` | 154 | 0.421 | `02_status_by_region.csv` |
| `03_inaccessible_special_collections.rq` | 0 | 0.287 | `03_inaccessible_special_collections.csv` |
| `04_demography_and_status.rq` | 538 | 0.962 | `04_demography_and_status.csv` |
| `05_library_mergers.rq` | 1,412 | 0.161 | `05_library_mergers.csv` |
| `06_external_links.rq` | 27,504 | 0.485 | `06_external_links.csv` |
| `07_demographic_filter.rq` | 98 | 0.466 | `07_demographic_filter.csv` |
| `08_region_aggregation.rq` | 20 | 0.343 | `08_region_aggregation.csv` |
| `09_temporary_closed_by_region.rq` | 44 | 0.421 | `09_temporary_closed_by_region.csv` |
| `10_material_type.rq` | 2,420 | 0.118 | `10_material_type.csv` |
| `11_library_municipality.rq` | 1 | 0.000 | `11_library_municipality.csv` |
