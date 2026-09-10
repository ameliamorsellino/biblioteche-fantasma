# Scripts

Gli script della directory `scripts/` implementano la pipeline riproducibile del progetto Biblioteche Fantasma.

## 1. Generazione dei dataset processati

Dalla root del repository:

```bash
python scripts/build_processed_data.py \
  --iccu data/raw/iccu/opendata.zip \
  --posas2019 data/raw/istat/POSAS_2019_it_Tutti_i_file.zip \
  --posas2025 data/raw/istat/POSAS_2025_it_Tutti_i_file.zip \
  --out-root .
```

Lo script non modifica gli archivi RAW e genera deterministicamente i dataset processati in `data/processed/`.

## 2. Generazione di metadati e report di qualità

```bash
python scripts/build_metadata.py \
  --root . \
  --iccu data/raw/iccu/opendata.zip \
  --posas2019 data/raw/istat/POSAS_2019_it_Tutti_i_file.zip \
  --posas2025 data/raw/istat/POSAS_2025_it_Tutti_i_file.zip \
  --cultural-on data/external/cultural-ON.owl
```

## 3. Validazione degli output tabellari

```bash
python scripts/validate_outputs.py --root .
```

Il controllo verifica struttura degli output, metadati, file sorgente e SHA-256 dichiarati nel source manifest.

## 4. Generazione RDF

```bash
python scripts/generate_rdf.py --root .
python scripts/generate_links.py
```

Gli script producono il knowledge graph locale e i collegamenti verso risorse esterne.

## 5. Validazione RDF e SHACL

```bash
python scripts/validate_rdf.py --root .
python scripts/validate_shacl.py --root .
```

La validazione SHACL utilizza pySHACL sullo store persistente PyOxigraph.

## 6. SPARQL locale

Per eseguire tutte le query:

```bash
python scripts/run_sparql.py --root .
```

Il primo avvio costruisce automaticamente uno store RDF persistente in `.cache/oxigraph/` a partire da:

* `ontology/ontology.ttl`
* `rdf/data.ttl`
* `rdf/links.ttl`
* `rdf/metadata.ttl`

Lo store viene riutilizzato finché gli RDF sorgente non cambiano.

Per eseguire una singola query:

```bash
python scripts/run_sparql.py --root . --query 09_temporary_closed_by_region
```

Per ricostruire lo store:

```bash
python scripts/run_sparql.py --root . --rebuild-store
```

Per elencare le query:

```bash
python scripts/run_sparql.py --root . --list
```

I risultati vengono salvati in `sparql/results/` e il report di esecuzione in `reports/sparql_execution_report.md`.

## 7. Analisi e visualizzazioni

```bash
python scripts/run_analysis.py --root .
python scripts/run_visualizations.py --root .
```

Le tabelle analitiche sono salvate in `reports/analysis_tables/` e le visualizzazioni in `visualizations/`.

## Ambiente

Installazione delle dipendenze:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Su Windows l'attivazione dell'ambiente virtuale varia in base alla shell utilizzata.
