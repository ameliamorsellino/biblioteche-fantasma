# BIBLIOTECHE FANTASMA

**Analisi, integrazione e modellazione semantica delle biblioteche italiane non pienamente operative**

## Abstract

Il progetto sviluppa una pipeline completa di **Open Data Management** a partire da dati reali dell'**Anagrafe delle Biblioteche Italiane (ICCU)** e della popolazione residente **ISTAT POSAS 2019 e 2025**.

La pipeline comprende:

**selezione e verifica delle fonti → conservazione dei RAW → profiling e controllo qualità → cleaning → armonizzazione territoriale → integrazione e arricchimento → dataset strutturati → metadati → modellazione ontologica → RDF → validazione SHACL → interlinking → SPARQL → analisi statistica → visualizzazione.**

“Biblioteche Fantasma” è un'etichetta narrativa del progetto, **non una categoria ufficiale ICCU**. L'assenza di uno stato speciale nel registro non viene interpretata come certificazione di piena operatività.

Il progetto adotta inoltre un approccio conservativo nella gestione delle anomalie: i valori mancanti non vengono automaticamente trasformati in zero, le anomalie non vengono corrette senza evidenza documentale e le variazioni amministrative tra annualità ISTAT vengono trattate esplicitamente.

---

## Research Questions

* **RQ1** - Dove sono distribuite le biblioteche caratterizzate da stati di non piena operatività?
* **RQ2** - Quali stati di registrazione sono più frequenti e come variano territorialmente?
* **RQ3** - Quali tipologie funzionali/amministrative risultano associate ai diversi stati?
* **RQ4** - Esiste un'associazione tra variazione demografica comunale 2019–2025 e quota di record bibliotecari con stato ICCU incluso nel perimetro problematico?
* **RQ5** - Quale patrimonio e quali fondi speciali risultano documentati presso biblioteche problematiche?
* **RQ6** - Quale copertura raggiunge la generazione dei collegamenti verso risorse esterne?
* **RQ7** - Quale struttura presenta la rete delle confluenze?
* **RQ8** - Quale relazione descrittiva emerge tra quota di popolazione 65+ e biblioteche problematiche?

---

## Fonti Open Data

Le sorgenti principali sono:

* **ICCU - Anagrafe delle Biblioteche Italiane**, snapshot del 2026-09-08;
* **ISTAT POSAS 2019** - popolazione residente per sesso, età e stato civile;
* **ISTAT POSAS 2025** - popolazione residente per sesso, età e stato civile;
* **Cultural-ON 2.0** - ontologia utilizzata per il riuso semantico nel dominio culturale.

Gli archivi RAW originali sono conservati separatamente in:

```text
data/raw/iccu/opendata.zip
data/raw/istat/POSAS_2019_it_Tutti_i_file.zip
data/raw/istat/POSAS_2025_it_Tutti_i_file.zip
```

La pipeline **non modifica mai i RAW**.

`metadata/source_manifest.csv` documenta per ciascuna sorgente:

* publisher;
* URL;
* ruolo nel progetto;
* data di acquisizione;
* licenza;
* percorso locale;
* SHA-256.

Questo consente di verificare l'identità delle sorgenti utilizzate e di ricostruire gli artefatti derivati a partire dai file originali inclusi nel repository.

---

## Licenze

Le condizioni di riuso sono documentate in `metadata/licenses.md`.

* **ICCU Open Data:** CC0 1.0.
* **ISTAT POSAS 2019/2025:** CC BY 4.0.
* **Cultural-ON 2.0:** CC BY 3.0 IT.
* **Dataset tabellare derivato e documentazione originale del progetto:** CC BY 4.0, salvo dove diversamente indicato.

La licenza del progetto è disponibile in `LICENSE`.

La licenza del progetto non sostituisce né modifica le condizioni applicabili ai materiali di terze parti inclusi o referenziati.

---

## Verifica, cleaning e integrazione

La preparazione dei dati comprende controlli sulla struttura, sui tipi, sui valori mancanti, sugli identificatori, sulle coordinate e sulla coerenza territoriale.

Tra le principali decisioni metodologiche:

* conservazione separata dei RAW;
* normalizzazione degli identificatori ISIL e ISTAT;
* distinzione tra valore mancante e valore numerico zero;
* coordinate `(0, 0)` trattate come mancanti;
* esclusione dal perimetro analitico degli istituti ICCU classificati come altre tipologie di istituzione quando non pertinenti alla definizione operativa di biblioteca;
* nessun fuzzy matching per i comuni;
* armonizzazione esplicita delle variazioni amministrative tra la geografia ISTAT 2019 e quella 2025;
* conservazione della struttura 1:N per patrimonio, fondi speciali e altre informazioni multivalore;
* modellazione dello stato ICCU come osservazione riferita allo snapshot, non come proprietà atemporale;
* utilizzo prudente di `owl:sameAs` e `rdfs:seeAlso` in funzione della reale equivalenza semantica delle risorse.

Le principali scelte progettuali e i relativi trade-off sono documentati in:

```text
reports/decisions_log.md
reports/data_quality.md
reports/limitations.md
```

---

## Dataset processati

La pipeline produce **10 dataset tabellari canonici** in formato CSV UTF-8 direttamente in:

```text
data/processed/
```

I CSV sono strutturati, machine-readable e in formato non proprietario.

Il formato Parquet è opzionale e può essere prodotto tramite:

```bash
pip install pyarrow
python scripts/export_parquet.py --root .
```

Gli eventuali file Parquet vengono salvati in:

```text
data/processed/parquet/
```

L'esportazione Parquet non è necessaria per la pipeline principale, per la generazione RDF, per SPARQL, per le analisi o per le visualizzazioni.

---

## Metadati

Il repository include metadati sia tabellari sia RDF.

### Frictionless Data Package

```text
metadata/datapackage.json
```

descrive le risorse processate, i relativi percorsi e lo schema dei campi.

### DCAT

```text
metadata/dcat.ttl
```

fornisce una descrizione RDF/DCAT locale del dataset e delle relative distribuzioni.

Il progetto **non dichiara una conformità operativa completa a DCAT-AP_IT** nella distribuzione locale corrente.

Le distribuzioni utilizzano infatti URI `file:` e il namespace del progetto usa il dominio riservato `.invalid`. Una pubblicazione su un catalogo reale richiederebbe URL HTTP(S) pubblici e persistenti e una validazione rispetto al profilo DCAT-AP_IT applicabile.

Ulteriori dettagli sono disponibili in:

```text
metadata/dcat_validation_notes.md
metadata/provenance.ttl
metadata/uri_policy.md
```

---

## Ontologia e modellazione semantica

L'ontologia del progetto è disponibile in:

```text
ontology/ontology.ttl
ontology/ontology.owl
```

La progettazione segue il principio:

**reuse → extend → create**

e riutilizza, dove semanticamente appropriato:

* Cultural-ON;
* SKOS;
* PROV-O;
* DCAT / DCTERMS;
* GeoSPARQL;
* LOCN;
* Schema.org.

Gli stati ICCU sono modellati come `skos:Concept`.

Le osservazioni sullo stato delle biblioteche sono modellate separatamente dalle biblioteche stesse, così da esplicitare la natura temporale dello snapshot.

Le competency questions e le scelte di riuso sono documentate in:

```text
ontology/competency_questions.md
ontology/vocabulary_reuse.csv
```

---

## URI policy

Il progetto mantiene distinti il namespace ontologico e quello delle risorse.

Namespace ontologico:

```text
https://biblioteche-fantasma.invalid/ontology/
```

Namespace delle risorse:

```text
https://biblioteche-fantasma.invalid/resource/
```

Le URI vengono costruite deterministicamente utilizzando, quando disponibili, identificatori ufficiali quali:

* ISIL per le biblioteche;
* codice ISTAT per i comuni;
* identificatori derivati e documentati per osservazioni e altre entità.

Il dominio `.invalid` è utilizzato intenzionalmente come namespace di sviluppo e **non è dereferenziabile sul Web**.

---

## Knowledge graph RDF

La generazione RDF è implementata in:

```text
scripts/generate_rdf.py
scripts/generate_links.py
```

Gli output principali sono:

```text
rdf/data.ttl
rdf/links.ttl
rdf/metadata.ttl
```

Il knowledge graph contiene:

* `rdf/data.ttl`: **1.616.865 triple**;
* `rdf/links.ttl`: **27.504 triple**;
* `rdf/metadata.ttl`: **38 triple**;
* `ontology/ontology.ttl`: **195 triple**.

Totale esplicito:

**1.644.602 triple**

La validazione strutturale controlla, tra le altre cose:

* parsing RDF;
* URI malformate;
* forme lessicali dei datatype;
* classi e proprietà locali non dichiarate;
* risorse locali pendenti;
* soggetti dei link non presenti nel grafo;
* duplicati serializzati.

Il report è disponibile in:

```text
reports/rdf_validation.md
```

---

## SHACL

Le shape sono definite in:

```text
shacl/shapes.ttl
```

La validazione è eseguita con **pySHACL 0.40.1** sull'intero knowledge graph.

L'ultima esecuzione validata ha prodotto:

```text
Conforms: YES
Validation results: 0
Violations: 0
Warnings: 0
Infos: 0
```

I report vengono salvati in:

```text
reports/shacl_validation.md
reports/shacl_validation.txt
reports/shacl_validation.ttl
```

La validazione può essere rieseguita con:

```bash
python scripts/validate_shacl.py --root .
```

---

## Interlinking

Il progetto genera collegamenti verso risorse esterne utilizzando identificatori ufficiali e senza fuzzy matching.

### Biblioteche → ICCU

Per le **19.611 biblioteche ICCU** viene generato un collegamento verso l'Anagrafe delle Biblioteche Italiane utilizzando l'ISIL.

Relazione:

```text
rdfs:seeAlso
```

Copertura di generazione:

```text
19.611 / 19.611 = 100%
```

`rdfs:seeAlso` viene utilizzato perché il target ICCU è una risorsa Web di consultazione e non viene assunto come individuo RDF semanticamente identico alla risorsa locale.

### Comuni → Linked ISPRA

Per i comuni vengono generate URI Linked ISPRA a partire dal codice ISTAT a sei cifre.

Relazione:

```text
owl:sameAs
```

Copertura di generazione:

```text
7.893 / 7.896 = 99,9620%
```

I tre casi senza collegamento sono mantenuti intenzionalmente non collegati a causa di variazioni amministrative intervenute nel 2026 rispetto alla geografia analitica 2025.

Le percentuali riportate descrivono la **copertura di generazione dei collegamenti secondo la URI policy documentata**.

Lo schema delle URI esterne è stato verificato su risorse reali, ma la pipeline offline non dereferenzia individualmente tutti i target Linked ISPRA; la coverage non deve quindi essere interpretata come tasso di risposta HTTP verificato su ogni singola URI.

Il report machine-readable è:

```text
reports/interlinking_report.csv
```

---

## SPARQL

Le competency questions vengono tradotte in **11 query SPARQL** disponibili in:

```text
sparql/
```

L'esecuzione locale utilizza **PyOxigraph** come store RDF embedded e persistente.

Non sono necessari:

* GraphDB;
* un server SPARQL locale;
* un endpoint SPARQL esterno.

Lo store viene creato in:

```text
.cache/oxigraph/
```

ed è un artefatto locale rigenerabile, quindi non deve essere versionato né incluso nella distribuzione finale.

Per eseguire tutte le query:

```bash
python scripts/run_sparql.py --root .
```

Per ricostruire esplicitamente lo store:

```bash
python scripts/run_sparql.py --root . --rebuild-store
```

Per eseguire una singola query:

```bash
python scripts/run_sparql.py \
  --root . \
  --query 01_status_distribution
```

Per visualizzare l'elenco:

```bash
python scripts/run_sparql.py --root . --list
```

I risultati vengono salvati in:

```text
sparql/results/
```

e il report complessivo in:

```text
reports/sparql_execution_report.md
reports/sparql_execution_report.json
```

Le **11 query risultano eseguibili** sul knowledge graph locale. Una query può legittimamente restituire zero righe: ad esempio la query relativa alle biblioteche inagibili con fondi speciali documentati restituisce un insieme vuoto nello snapshot corrente senza che ciò costituisca un errore di esecuzione.

---

## Analisi quantitativa

Le analisi statistiche sono eseguite principalmente con:

* Pandas;
* NumPy;
* SciPy;
* NetworkX.

SPARQL viene utilizzato per interrogare il knowledge graph e rispondere alle competency questions; Pandas/SciPy vengono invece utilizzati per le elaborazioni tabellari e statistiche, mentre NetworkX viene utilizzato per la rete delle confluenze.

Questa separazione evita di utilizzare SPARQL per operazioni per cui una rappresentazione tabellare risulta più leggibile ed efficiente.

Esecuzione:

```bash
python scripts/run_analysis.py --root .
```

Gli output vengono salvati principalmente in:

```text
reports/analysis_tables/
reports/analysis_summary.json
reports/rq_results.json
```

---

## Risultati principali

Il master ICCU contiene **19.611 record**.

Escludendo **655 record** classificati come altre istituzioni collegate all'ICCU, il denominatore utilizzato per il perimetro bibliotecario è pari a:

**18.956 biblioteche**

Le biblioteche incluse nel perimetro analitico principale delle condizioni di non piena operatività sono:

**2.497**, pari al **13,17%** delle biblioteche considerate e al **12,73%** dei record complessivi del registro.

Gli stati più frequenti nello snapshot comprendono:

* nessuno stato speciale registrato: 13.200;
* biblioteca non più esistente: 1.827;
* biblioteca non censita: 1.723;
* biblioteca confluita: 1.502;
* temporaneamente chiusa: 619.

A livello regionale, la quota problematica risulta particolarmente elevata in alcune regioni, ma ogni confronto viene interpretato insieme al relativo denominatore.

Per RQ4, il confronto su **6.659 comuni comparabili con almeno una biblioteca** mostra una relazione debole tra variazione demografica 2019–2025 e quota di record bibliotecari con stato ICCU incluso nel perimetro problematico:

```text
Pearson r = -0,106
Spearman ρ = -0,067
```

Il risultato è **osservazionale** e non consente inferenze causali.

Per RQ5, **627 delle 2.497 biblioteche problematiche** presentano almeno una riga di patrimonio documentata, per un totale di **2.828 righe**. La mancata presenza di una biblioteca nel dataset dei fondi speciali viene interpretata come assenza di documentazione nel dataset, non come prova dell'assenza reale di fondi.

La rete delle confluenze comprende:

```text
1.412 archi validati
1.821 nodi
410 componenti debolmente connesse
40 nodi nella componente maggiore
```

L'unico ciclo rilevato è il self-loop già documentato:

```text
IT-SS0267 -> IT-SS0267
```

Per RQ8, la quota di popolazione over 65 mostra un'associazione positiva ma debole con la quota di record bibliotecari con stato ICCU incluso nel perimetro problematico. L'analisi è documentata in:

```text
reports/analysis_tables/age65_problematic_correlation.csv
visualizations/age65_scatter.png
```

---

## Visualizzazioni

Le visualizzazioni sono generate da:

```bash
python scripts/run_visualizations.py --root .
```

Gli output sono disponibili in:

```text
visualizations/
```

Tra le principali:

* `library_map.html` - mappa interattiva clusterizzata;
* `map_static.png` - distribuzione geografica delle biblioteche problematiche;
* `status_by_region.png` - quote regionali;
* `status_distribution.png` - distribuzione nazionale degli stati;
* `demography_scatter.png` - variazione demografica vs quota problematica;
* `special_collections.png` - copertura documentaria di patrimonio e fondi speciali;
* `problematic_holdings.png` - materiali documentati presso le biblioteche problematiche;
* `mergers_network.png` - componente maggiore della rete delle confluenze;
* `age65_scatter.png` - quota 65+ vs quota di record bibliotecari con stato ICCU incluso nel perimetro problematico.

Le visualizzazioni sono progettate per rispondere alle Research Questions e non come dashboard esplorativa priva di una domanda analitica.

---

## Valutazione rispetto al modello 5-star Open Data

Il progetto implementa tecnicamente:

* dati sotto licenza aperta;
* dati strutturati;
* formati aperti e machine-readable;
* RDF;
* URI per l'identificazione delle risorse;
* collegamenti verso risorse esterne.

Tuttavia il repository locale **non viene presentato come una pubblicazione Linked Open Data 5-star operativa sul Web**.

Il namespace:

```text
https://biblioteche-fantasma.invalid/
```

è deliberatamente non dereferenziabile e le distribuzioni DCAT fanno riferimento a file locali.

Il progetto dimostra quindi tecnicamente il passaggio verso Linked Open Data e l'interlinking, ma una pubblicazione operativa richiederebbe almeno:

* namespace HTTPS pubblico e persistente;
* URI locali dereferenziabili;
* accesso Web alle distribuzioni;
* content negotiation o rappresentazioni RDF accessibili;
* mantenimento dei link esterni;
* eventuale endpoint SPARQL pubblico o altro meccanismo di interrogazione.

La valutazione completa è documentata in:

```text
reports/five_star_assessment.md
```

---

## Struttura del repository

```text
biblioteche-fantasma/
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
├── SPARQL.md
│
├── data/
│   ├── raw/
│   │   ├── iccu/
│   │   │   └── opendata.zip
│   │   └── istat/
│   │       ├── POSAS_2019_it_Tutti_i_file.zip
│   │       └── POSAS_2025_it_Tutti_i_file.zip
│   │
│   ├── external/
│   │   ├── cultural-ON.owl
│   │   ├── library_links.csv
│   │   └── municipality_links.csv
│   │
│   └── processed/
│       ├── *.csv
│       └── parquet/
│
├── metadata/
│   ├── source_manifest.csv
│   ├── licenses.md
│   ├── datapackage.json
│   ├── dcat.ttl
│   ├── dcat_validation_notes.md
│   ├── provenance.ttl
│   └── uri_policy.md
│
├── ontology/
│   ├── ontology.ttl
│   ├── ontology.owl
│   ├── competency_questions.md
│   └── vocabulary_reuse.csv
│
├── shacl/
│   └── shapes.ttl
│
├── rdf/
│   ├── data.ttl
│   ├── links.ttl
│   └── metadata.ttl
│
├── sparql/
│   ├── *.rq
│   └── results/
│
├── scripts/
│   ├── build_processed_data.py
│   ├── build_metadata.py
│   ├── validate_outputs.py
│   ├── generate_rdf.py
│   ├── generate_links.py
│   ├── validate_rdf.py
│   ├── validate_shacl.py
│   ├── run_sparql.py
│   ├── run_analysis.py
│   ├── run_visualizations.py
│   ├── export_parquet.py
│   └── rebuild_all.py
│
├── notebooks/
│   ├── 01_*.ipynb
│   ├── 02_*.ipynb
│   ├── 03_*.ipynb
│   ├── 04_*.ipynb
│   ├── 05_*.ipynb
│   ├── 06_*.ipynb
│   ├── 07_*.ipynb
│   └── 08_*.ipynb
│
├── reports/
│   ├── analysis_tables/
│   ├── analysis.md
│   ├── data_quality.md
│   ├── decisions_log.md
│   ├── five_star_assessment.md
│   ├── interlinking_report.csv
│   ├── limitations.md
│   ├── rdf_validation.md
│   ├── shacl_validation.md
│   └── sparql_execution_report.md
│
├── visualizations/
│   ├── *.png
│   └── library_map.html
│
└── report/
    ├── relazione.tex
    ├── bibliography.bib
    └── relazione.pdf
```

Gli artefatti locali rigenerabili quali `.venv/`, `.cache/`, `__pycache__/` e i file temporanei LaTeX non fanno parte della distribuzione finale.

---

## Setup

Il progetto è stato eseguito nell'ambiente di sviluppo corrente con **Python 3.14**.

Creare un ambiente virtuale:

```bash
python -m venv .venv
```

Su Linux/macOS:

```bash
source .venv/bin/activate
```

Su Windows, l'attivazione dipende dalla shell utilizzata.

Installare quindi le dipendenze:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Le principali dipendenze includono:

* pandas;
* numpy;
* scipy;
* networkx;
* matplotlib;
* folium;
* RDFLib;
* PyOxigraph;
* pySHACL;
* JupyterLab.

`pyarrow` è opzionale e serve esclusivamente per l'esportazione Parquet.

---

## Riproduzione completa dai RAW

La modalità raccomandata per ricostruire il progetto è:

```bash
python scripts/rebuild_all.py
```

Lo script esegue nell'ordine:

```text
RAW
 ↓
build_processed_data.py
 ↓
build_metadata.py
 ↓
validate_outputs.py
 ↓
generate_rdf.py
 ↓
generate_links.py
 ↓
validate_rdf.py
 ↓
run_sparql.py --rebuild-store
 ↓
validate_shacl.py
 ↓
run_analysis.py
 ↓
run_visualizations.py
```

Gli archivi RAW non vengono modificati.

---

## Riproduzione manuale della pipeline

Gli stessi passaggi possono essere eseguiti singolarmente.

### 1. Dataset processati

```bash
python scripts/build_processed_data.py \
  --iccu data/raw/iccu/opendata.zip \
  --posas2019 data/raw/istat/POSAS_2019_it_Tutti_i_file.zip \
  --posas2025 data/raw/istat/POSAS_2025_it_Tutti_i_file.zip \
  --out-root .
```

### 2. Metadati e report di qualità

```bash
python scripts/build_metadata.py \
  --root . \
  --iccu data/raw/iccu/opendata.zip \
  --posas2019 data/raw/istat/POSAS_2019_it_Tutti_i_file.zip \
  --posas2025 data/raw/istat/POSAS_2025_it_Tutti_i_file.zip \
  --cultural-on data/external/cultural-ON.owl
```

Le eventuali note di rilascio ICCU possono essere aggiunte mediante opzioni ripetute:

```text
--release-note FILE
```

### 3. Validazione tabellare e metadatazione

```bash
python scripts/validate_outputs.py --root .
```

### 4. Generazione RDF

```bash
python scripts/generate_rdf.py --root .
```

### 5. Interlinking

```bash
python scripts/generate_links.py
```

### 6. Validazione RDF

```bash
python scripts/validate_rdf.py --root .
```

### 7. SPARQL

```bash
python scripts/run_sparql.py --root . --rebuild-store
```

### 8. SHACL

```bash
python scripts/validate_shacl.py --root .
```

### 9. Analisi

```bash
python scripts/run_analysis.py --root .
```

### 10. Visualizzazioni

```bash
python scripts/run_visualizations.py --root .
```

---

## Analisi e validazione degli artefatti già generati

Se non è necessario ricostruire i dataset dai RAW, gli artefatti esistenti possono essere controllati separatamente.

Validazione tabellare:

```bash
python scripts/validate_outputs.py --root .
```

Validazione RDF:

```bash
python scripts/validate_rdf.py --root .
```

Validazione SHACL:

```bash
python scripts/validate_shacl.py --root .
```

SPARQL:

```bash
python scripts/run_sparql.py --root .
```

Analisi:

```bash
python scripts/run_analysis.py --root .
```

Visualizzazioni:

```bash
python scripts/run_visualizations.py --root .
```

---

## Notebook

I notebook `01`–`08` documentano e rendono ispezionabili le principali componenti della pipeline, dal profiling delle sorgenti fino all'analisi e alla visualizzazione.

Le trasformazioni deterministiche e riproducibili sono implementate negli script della directory `scripts/`; i notebook non sostituiscono la pipeline automatica.

Per aprirli:

```bash
jupyter lab notebooks/
```

---

## Riproducibilità e integrità

Il repository mantiene separati:

```text
RAW
processed
metadata
RDF
report di validazione
analisi
visualizzazioni
```

Gli hash delle sorgenti sono registrati in:

```text
metadata/source_manifest.csv
```

La distribuzione finale include inoltre:

```text
MANIFEST.sha256
```

che consente di verificare l'integrità dei file della release.

Verifica:

```bash
sha256sum -c MANIFEST.sha256
```

`MANIFEST.sha256` deve essere rigenerato soltanto dopo l'ultima modifica alla release.

---

## Limiti principali

I principali limiti del progetto sono:

* lo snapshot ICCU rappresenta uno stato osservato e non una serie storica completa;
* gli stati ICCU non forniscono necessariamente date di inizio e fine;
* l'assenza di uno stato speciale non certifica la piena operatività;
* la completezza informativa del registro non è uniforme;
* l'assenza di patrimonio o fondi speciali nel dataset non equivale automaticamente a valore reale zero;
* le variazioni amministrative territoriali complicano il confronto 2019–2025;
* le analisi demografiche sono osservazionali e non permettono inferenze causali;
* URI e dataset esterni possono cambiare nel tempo;
* la pipeline offline non dereferenzia individualmente tutti i target Linked ISPRA;
* il namespace locale `.invalid` non costituisce una pubblicazione Web dereferenziabile;
* “Biblioteche Fantasma” è un'etichetta progettuale e non una classificazione ufficiale.

L'elenco dettagliato è disponibile in:

```text
reports/limitations.md
```

---

## Relazione finale

La relazione completa è disponibile in:

```text
report/relazione.pdf
```

Il sorgente LaTeX e la bibliografia sono conservati in:

```text
report/relazione.tex
report/bibliography.bib
```

---

## Citazione

Citare il progetto indicando:

* **Biblioteche Fantasma**;
* anno 2026;
* ICCU - Anagrafe delle Biblioteche Italiane;
* ISTAT POSAS 2019 e 2025.

Per i dati ISTAT deve essere mantenuta l'attribuzione richiesta dalla licenza CC BY 4.0.

Cultural-ON mantiene la propria licenza CC BY 3.0 IT.

Il dataset tabellare derivato e la documentazione originale del progetto sono distribuiti, salvo dove diversamente indicato, secondo **CC BY 4.0**.
