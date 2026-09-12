# Scripts

The scripts in the `scripts/` directory implement the reproducible pipeline of the Biblioteche Fantasma project.

## 1. Processed dataset generation

From the repository root:

```bash
python scripts/build_processed_data.py \
  --iccu data/raw/iccu/opendata.zip \
  --posas2019 data/raw/istat/POSAS_2019_it_Tutti_i_file.zip \
  --posas2025 data/raw/istat/POSAS_2025_it_Tutti_i_file.zip \
  --out-root .
```

The script does not modify the RAW archives and deterministically generates the processed datasets in `data/processed/`.

## 2. Metadata and quality report generation

```bash
python scripts/build_metadata.py \
  --root . \
  --iccu data/raw/iccu/opendata.zip \
  --posas2019 data/raw/istat/POSAS_2019_it_Tutti_i_file.zip \
  --posas2025 data/raw/istat/POSAS_2025_it_Tutti_i_file.zip \
  --cultural-on data/external/cultural-ON.owl
```

## 3. Tabular output validation

```bash
python scripts/validate_outputs.py --root .
```

The validation checks the output structure, metadata, source files, and the SHA-256 hashes declared in the source manifest.

## 4. RDF generation

```bash
python scripts/generate_rdf.py --root .
python scripts/generate_links.py
```

The scripts generate the local knowledge graph and the links to external resources.

## 5. RDF and SHACL validation

```bash
python scripts/validate_rdf.py --root .
python scripts/validate_shacl.py --root .
```

SHACL validation uses pySHACL on the persistent PyOxigraph store.

## 6. Local SPARQL

To run all queries:

```bash
python scripts/run_sparql.py --root .
```

On the first run, the script automatically builds a persistent RDF store in `.cache/oxigraph/` from:

* `ontology/ontology.ttl`
* `rdf/data.ttl`
* `rdf/links.ttl`
* `rdf/metadata.ttl`

The store is reused as long as the source RDF files do not change.

To run a single query:

```bash
python scripts/run_sparql.py --root . --query 09_temporary_closed_by_region
```

To rebuild the store:

```bash
python scripts/run_sparql.py --root . --rebuild-store
```

To list the queries:

```bash
python scripts/run_sparql.py --root . --list
```

Results are saved in `sparql/results/`, and the execution report is saved in `reports/sparql_execution_report.md`.

## 7. Analysis and visualizations

```bash
python scripts/run_analysis.py --root .
python scripts/run_visualizations.py --root .
```

The analytical tables are saved in `reports/analysis_tables/`, and the visualizations are saved in `visualizations/`.

## Environment

Install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, virtual environment activation varies depending on the shell being used.
