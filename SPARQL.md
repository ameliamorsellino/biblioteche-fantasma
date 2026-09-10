# Eseguire SPARQL in VS Code senza GraphDB

Il progetto usa **PyOxigraph**, uno store RDF embedded richiamato direttamente da Python. Non serve installare GraphDB, avviare un server o configurare un endpoint SPARQL.

## 1. Aprire il repository

Aprire in VS Code la cartella `biblioteche-fantasma` (non la cartella ZIP e non una sottocartella).

## 2. Creare un ambiente virtuale

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

In VS Code selezionare lo stesso interprete `.venv` con **Python: Select Interpreter**.

## 3. Controllare le query disponibili

```bash
python scripts/run_sparql.py --root . --list
```

Devono comparire le query da `01_status_distribution` a `11_library_municipality`.

## 4. Eseguire una query di prova

```bash
python scripts/run_sparql.py --root . --query 01_status_distribution
```

Al primo avvio lo script:

1. controlla la sintassi della query con RDFLib;
2. calcola gli hash degli RDF sorgente;
3. crea `.cache/oxigraph/`;
4. importa `ontology/ontology.ttl`, `rdf/data.ttl`, `rdf/links.ttl` e `rdf/metadata.ttl`;
5. controlla il numero di triple esplicite;
6. esegue la query;
7. salva il CSV in `sparql/results/`.

Lo store è persistente: le esecuzioni successive non reimportano i circa 1,64 milioni di triple se i file RDF non sono cambiati.

## 5. Eseguire tutta la suite

```bash
python scripts/run_sparql.py --root .
```

Al termine devono essere presenti:

- `sparql/results/01_status_distribution.csv`
- ...
- `sparql/results/11_library_municipality.csv`
- `sparql/results/README.md`
- `reports/sparql_execution_report.md`
- `reports/sparql_execution_report.json`

## 6. Esecuzione dai task di VS Code

Usare **Terminale → Esegui attività...** e scegliere:

- `SPARQL: esegui tutte le query`
- `SPARQL: ricostruisci store ed esegui tutte`
- `SPARQL: elenca query`

I task sono definiti in `.vscode/tasks.json`.

## 7. Quando ricostruire lo store

Normalmente non serve: lo script rileva automaticamente le modifiche tramite SHA-256. Per forzare la ricostruzione:

```bash
python scripts/run_sparql.py --root . --rebuild-store
```

La directory `.cache/` è esclusa da Git perché è un indice locale rigenerabile, non un artefatto scientifico da consegnare.

## 8. Errore `PyOxigraph is not installed`

Eseguire, con l'ambiente virtuale attivo:

```bash
python -m pip install -r requirements.txt
```

Poi verificare:

```bash
python -c "import pyoxigraph; print('PyOxigraph OK')"
```

## 9. Nota metodologica

PyOxigraph sostituisce GraphDB **solo come motore locale di interrogazione**. Il knowledge graph, le query SPARQL, l'ontologia e i risultati non cambiano. Le analisi statistiche finali restano in Pandas/Scipy/NetworkX, mentre SPARQL viene usato per le competency questions e la navigazione semantica.
