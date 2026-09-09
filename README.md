# BIBLIOTECHE FANTASMA

**Analisi, integrazione e modellazione semantica delle biblioteche italiane non pienamente operative**

## Abstract

Il progetto applica un ciclo completo di Open Data Management a uno snapshot reale dell'**Anagrafe delle Biblioteche Italiane (ICCU)**, integrato con la popolazione comunale **ISTAT POSAS 2019 e 2025**. La pipeline delle Fasi 1-2 ha prodotto dataset tabellari normalizzati, metadati, un'ontologia che riusa Cultural-ON, un knowledge graph RDF, SHACL, interlinking e query SPARQL. La Fase 3 usa esclusivamente il checkpoint canonico per l'analisi statistica, la visualizzazione, la data story e la relazione finale.

“Biblioteche Fantasma” è un'etichetta narrativa del progetto, **non** una categoria ufficiale ICCU. L'assenza di uno stato speciale non viene interpretata come certificazione di piena operatività.

## Research Questions

- **RQ1** — Dove sono distribuite le biblioteche caratterizzate da stati di non piena operatività?
- **RQ2** — Quali stati di registrazione sono più frequenti e come variano territorialmente?
- **RQ3** — Quali tipologie funzionali/amministrative risultano associate ai diversi stati?
- **RQ4** — Esiste un'associazione tra variazione demografica comunale 2019-2025 e quota di biblioteche problematiche?
- **RQ5** — Quale patrimonio e quali fondi speciali risultano documentati presso biblioteche problematiche?
- **RQ6** — Quale copertura ha raggiunto l'interlinking verso risorse esterne?
- **RQ7** — Quale struttura presenta la rete delle confluenze?
- **RQ8** — Quale relazione descrittiva emerge tra quota 65+ e biblioteche problematiche?

## Fonti e licenze

Le fonti complete sono in `metadata/source_manifest.csv` e le condizioni in `metadata/licenses.md`.

- ICCU Anagrafe: snapshot 2026-09-08, dati CC0 1.0.
- ISTAT POSAS 2019 e 2025: CC BY 4.0.
- Cultural-ON 2.0: CC BY 3.0 IT.
- Dataset tabellare derivato: CC BY 4.0, con attribuzione a ISTAT e citazione ICCU.

Gli archivi RAW non sono inclusi nel checkpoint 2 e **non sono stati ricostruiti** nella Fase 3. I loro hash e riferimenti restano nel manifest.

## Risultati principali

Il master contiene **19.611 record ICCU**; escludendo 655 record classificati come “altro istituto collegato ICCU”, il denominatore biblioteche è **18.956**. Le biblioteche nel perimetro `include_in_main_analysis=True` sono **2.497**, cioè **13,17%** delle biblioteche (12,73% dei record del registro).

Gli stati più frequenti sono: nessuno stato speciale registrato 13.200 (67,31% dei record), biblioteca non più esistente 1.827 (9,32%), biblioteca non censita 1.723 (8,79%), biblioteca confluita 1.502 (7,66%) e temporaneamente chiusa 619 (3,16%).

A livello regionale la quota problematica è più alta in **Molise (43,72%; 80/183)** e **Liguria (31,81%; 209/657)**; in valore assoluto la Lombardia ha 366 biblioteche problematiche. Il confronto demografico su **N=6.659** comuni comparabili con almeno una biblioteca produce una relazione debole: Pearson `r=-0,106` e Spearman `rho=-0,067`. I comuni in calo demografico hanno una quota problematica media del 12,42%, contro 8,48% nei comuni stabili/in crescita, ma il disegno è osservazionale e non dimostra causalità.

Per RQ5, **627/2.497** biblioteche problematiche hanno almeno una riga di patrimonio documentata (2.828 righe): 461 quantità sono mancanti e 2.367 positive. Nessuna biblioteca problematica compare in `special_collection.csv`; questo descrive la **copertura documentaria del dataset**, non l'assenza reale di fondi speciali.

La rete delle confluenze contiene **1.412 archi validati**, 1.821 nodi e 410 componenti; la componente maggiore ha 40 nodi. L'unico ciclo è il self-loop già noto `IT-SS0267 -> IT-SS0267`. L'interlinking del checkpoint 2 raggiunge **100%** per le biblioteche verso ICCU (`rdfs:seeAlso`) e **99,9620%** per i comuni verso Linked ISPRA (`owl:sameAs`), con tre non-match temporalmente motivati.

## Struttura del repository

```text
biblioteche-fantasma/
├── README.md, LICENSE, requirements.txt, .gitignore
├── HANDOFF_1.md, HANDOFF_2.md
├── data/
│   ├── external/
│   └── processed/
│       ├── csv/              # 10 dataset canonici
│       └── parquet/          # istruzioni; Parquet non materializzato nell'ambiente
├── metadata/                 # manifest, licenze, crosswalk, Data Package, DCAT, provenance, URI policy
├── ontology/                 # ontology.ttl/.owl, competency questions, vocabulary reuse
├── shacl/                    # shapes.ttl
├── rdf/                      # data.ttl, links.ttl, metadata.ttl
├── sparql/                   # 11 query e risultati disponibili
├── graphdb/                  # istruzioni di import
├── scripts/                  # analisi, visualizzazione, export Parquet, RDF/SHACL già esistenti
├── notebooks/                # wrapper 07/08 per eseguire gli script
├── reports/analysis_tables/  # tabelle quantitative della Fase 3
├── visualizations/           # PNG + mappa HTML
└── report/                   # relazione.tex, bibliography.bib, relazione.pdf
```

## Setup

Testato con Python 3.11. Installare le dipendenze:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

`pyarrow` è opzionale ed è necessario solo per materializzare i Parquet:

```bash
pip install pyarrow
python scripts/export_parquet.py --root .
```

## Ordine esatto di esecuzione

La Fase 3 **non** richiede di rigenerare RDF/interlinking. Per riprodurre analisi e figure a partire dal checkpoint:

```bash
python scripts/run_analysis.py --root .
python scripts/run_visualizations.py --root .
```

I controlli semantici sugli artefatti esistenti possono essere rilanciati senza rigenerazione:

```bash
python scripts/validate_rdf.py --root .
python scripts/validate_shacl.py --root .
python scripts/test_sparql.py --root .   # vedere i limiti nel report SPARQL
```

Per GraphDB seguire `graphdb/README.md`: importare ontologia, data, links e metadata. Il conteggio esplicito atteso senza reasoning è **1.644.602 triple**.

## Dataset 3-star e metadati

I CSV in `data/processed/csv/` costituiscono la distribuzione tabellare 3-star: licenza aperta, struttura machine-readable e formato non proprietario. `metadata/datapackage.json` descrive risorse e campi; `metadata/dcat-ap_it.ttl` fornisce una descrizione RDF locale. Le `downloadURL file:` e il namespace `.invalid` vanno sostituiti in una pubblicazione Web reale.

## Ontologia, RDF e SHACL

L'ontologia riusa Cultural-ON, SKOS, PROV-O, DCAT/DCTERMS, GeoSPARQL, LOCN e Schema.org. Gli stati sono `skos:Concept`; lo stato ICCU è modellato come osservazione temporale con data dello snapshot, non come proprietà atemporale.

Statistiche del knowledge graph: `rdf/data.ttl` 1.616.865 triple, `rdf/links.ttl` 27.504, `rdf/metadata.ttl` 38 e ontologia 195, per **1.644.602** triple esplicite importabili. La validazione RDF ha dato PASS. SHACL ha verificato 82.519 focus node senza violazioni nel sottoinsieme Core implementato localmente; non equivale a una validazione completa pySHACL/GraphDB.

## SPARQL e uso degli strumenti

SPARQL è usato per navigazione semantica e competency questions. Le aggregazioni statistiche finali sono invece eseguite con Pandas/Scipy e la rete con NetworkX: questo evita di forzare SPARQL su operazioni tabellari più leggibili e robuste. Le 11 query passano il parser RDFLib; una è stata eseguita nel controllo finale del checkpoint, mentre l'esecuzione completa è rimandata a un triplestore più adatto.

## Visualizzazioni

- `visualizations/library_map.html` — mappa interattiva clusterizzata.
- `visualizations/map_static.png` — distribuzione geografica delle biblioteche problematiche.
- `visualizations/status_by_region.png` — quote regionali con numeratori/denominatori.
- `visualizations/status_distribution.png` — distribuzione nazionale degli stati.
- `visualizations/demography_scatter.png` — variazione demografica vs quota problematica.
- `visualizations/special_collections.png` e `problematic_holdings.png` — copertura documentaria del patrimonio/fondi.
- `visualizations/mergers_network.png` — sola componente maggiore della rete, per leggibilità.
- `visualizations/age65_scatter.png` — analisi secondaria RQ8.

## Limiti essenziali

Lo snapshot ICCU non è una serie storica completa; lo stato non fornisce automaticamente date di inizio/fine; l'assenza di stato speciale non certifica operatività; la completezza ICCU è eterogenea; patrimonio/fondi mancanti non equivalgono a zero; la relazione demografica è osservazionale; le variazioni amministrative complicano il confronto; URI ed endpoint esterni sono volatili; “Biblioteche Fantasma” non è una categoria ufficiale. Inoltre il checkpoint finale non contiene gli archivi RAW e l'ambiente di build non ha consentito la materializzazione Parquet.

## Citazione

Citare il progetto indicando titolo, anno 2026, fonti ICCU e ISTAT, e la licenza CC BY 4.0 per il dataset derivato. Per i dati ISTAT è obbligatoria l'attribuzione; per Cultural-ON mantenere l'attribuzione prevista da CC BY 3.0 IT.
