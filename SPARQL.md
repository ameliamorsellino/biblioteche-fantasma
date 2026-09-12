# Running SPARQL in VS Code without GraphDB

The project uses **PyOxigraph**, an embedded RDF store invoked directly from Python. There is no need to install GraphDB, start a server, or configure a SPARQL endpoint.

## 1. Open the repository

Open the `biblioteche-fantasma` folder in VS Code (not the ZIP archive and not a subfolder).

## 2. Create a virtual environment

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

In VS Code, select the same `.venv` interpreter using **Python: Select Interpreter**.

## 3. Check the available queries

```bash
python scripts/run_sparql.py --root . --list
```

The queries from `01_status_distribution` to `11_library_municipality` should appear.

## 4. Run a test query

```bash
python scripts/run_sparql.py --root . --query 01_status_distribution
```

On the first run, the script:

1. checks the query syntax with RDFLib;

2. calculates the hashes of the source RDF files;

3. creates `.cache/oxigraph/`;

4. imports `ontology/ontology.ttl`, `rdf/data.ttl`, `rdf/links.ttl` and `rdf/metadata.ttl`;

5. checks the number of explicit triples;

6. executes the query;

7. saves the CSV in `sparql/results/`.

The store is persistent: subsequent runs do not reimport the approximately 1.64 million triples if the RDF files have not changed.

## 5. Run the full suite

```bash
python scripts/run_sparql.py --root .
```

At the end, the following should be present:

* `sparql/results/01_status_distribution.csv`

* ...

* `sparql/results/11_library_municipality.csv`

* `sparql/results/README.md`

* `reports/sparql_execution_report.md`

* `reports/sparql_execution_report.json`

## 6. Running from VS Code tasks

Use **Terminal → Run Task...** and choose:

* `SPARQL: run all queries`

* `SPARQL: rebuild store and run all`

* `SPARQL: list queries`

The tasks are defined in `.vscode/tasks.json`.

## 7. When to rebuild the store

Normally this is not necessary: the script automatically detects changes using SHA-256. To force a rebuild:

```bash
python scripts/run_sparql.py --root . --rebuild-store
```

The `.cache/` directory is excluded from Git because it is a regenerable local index, not a scientific artifact to be delivered.

## 8. `PyOxigraph is not installed` error

Run the following with the virtual environment active:

```bash
python -m pip install -r requirements.txt
```

Then verify:

```bash
python -c "import pyoxigraph; print('PyOxigraph OK')"
```

## 9. Methodological note

PyOxigraph replaces GraphDB **only as the local query engine**. The knowledge graph, SPARQL queries, ontology and results do not change. The final statistical analyses remain in Pandas/Scipy/NetworkX, while SPARQL is used for the competency questions and semantic navigation.
