# SPARQL execution report

## Engine

All queries reported below were actually executed with **PyOxigraph** against a local persistent store built from:

- `ontology/ontology.ttl`
- `rdf/data.ttl`
- `rdf/links.ttl`
- `rdf/metadata.ttl`

PyOxigraph runs inside Python and implements SPARQL 1.1; GraphDB is not required.
The source RDF is loaded into the default graph with no reasoning, so results refer to explicit triples only.

Explicit triples in store: **1,656,407**.

## Executed queries

| Query | Syntax | Execution | Rows | Seconds | Saved result |
|---|---|---|---:|---:|---|
| `01_status_distribution.rq` | PASS | PASS | 11 | 0.274 | `sparql/results/01_status_distribution.csv` |
| `02_status_by_region.rq` | PASS | PASS | 154 | 0.421 | `sparql/results/02_status_by_region.csv` |
| `03_inaccessible_special_collections.rq` | PASS | PASS | 0 | 0.287 | `sparql/results/03_inaccessible_special_collections.csv` |
| `04_demography_and_status.rq` | PASS | PASS | 538 | 0.962 | `sparql/results/04_demography_and_status.csv` |
| `05_library_mergers.rq` | PASS | PASS | 1,412 | 0.161 | `sparql/results/05_library_mergers.csv` |
| `06_external_links.rq` | PASS | PASS | 27,504 | 0.485 | `sparql/results/06_external_links.csv` |
| `07_demographic_filter.rq` | PASS | PASS | 98 | 0.466 | `sparql/results/07_demographic_filter.csv` |
| `08_region_aggregation.rq` | PASS | PASS | 20 | 0.343 | `sparql/results/08_region_aggregation.csv` |
| `09_temporary_closed_by_region.rq` | PASS | PASS | 44 | 0.421 | `sparql/results/09_temporary_closed_by_region.csv` |
| `10_material_type.rq` | PASS | PASS | 2,420 | 0.118 | `sparql/results/10_material_type.csv` |
| `11_library_municipality.rq` | PASS | PASS | 1 | 0.000 | `sparql/results/11_library_municipality.csv` |

## Reproduction

```bash
python -m pip install -r requirements.txt
python scripts/run_sparql.py --root .
```

To execute only one query:

```bash
python scripts/run_sparql.py --root . --query 01_status_distribution
```

The first run creates `.cache/oxigraph/`; subsequent runs reuse it unless one of the RDF source files changes.
