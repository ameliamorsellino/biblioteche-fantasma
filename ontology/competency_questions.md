# Competency Questions - Biblioteche Fantasma

Le competency questions (CQ) guidano il modello RDF e le query SPARQL. Il termine narrativo “Biblioteche Fantasma” non è trattato come classe amministrativa o stato ufficiale.

| CQ | Domanda | Entità/proprietà richieste | Vincolo temporale/semantico |
|---|---|---|---|
| CQ1 | Quali biblioteche temporaneamente chiuse si trovano in una determinata regione? | `cis:Library`, `bf:LibraryStatusObservation`, stato SKOS, `cis:hasSite/cis:hasGeographicalLocation`, `bf:regionName` | Stato osservato allo snapshot ICCU 2026-09-08; non implica data d'inizio della chiusura. |
| CQ2 | Quali biblioteche inagibili possiedono fondi speciali? | `cis:Library`, `bf:LibraryStatusObservation`, `bf:SpecialCollection`, `cis:hasCollection` | “INAGIBILE” resta distinto da sospensione per sisma e riapertura parziale. |
| CQ3 | In quale comune si trova una biblioteca? | `cis:Library → cis:hasSite → cis:Site → cis:hasGeographicalLocation → bf:Municipality` | Il comune è identificato con codice ISTAT a 6 cifre preservato come stringa. |
| CQ4 | In quale biblioteca è confluita una determinata biblioteca? | `bf:mergedInto` tra due `cis:Library` | Relazione asserita solo per target ISIL parseato e presente nello snapshot; 90 record senza target restano senza arco. |
| CQ5 | Quali biblioteche con interruzione del servizio si trovano in comuni con diminuzione demografica 2019–2025? | stato SKOS + municipio + due `bf:DemographicObservation` | Il confronto usa osservazioni 2019-01-01 e 2025-01-01; Trapani/Misiliscemi restano non comparabili quando il valore 2019 manca. |
| CQ6 | Quali biblioteche possiedono una determinata tipologia di patrimonio? | `bf:HoldingObservation`, `bf:materialType`, concetti SKOS | La riga patrimonio è un'osservazione dello snapshot, non una `cis:Collection` per evitare equivalenze improprie. |
| CQ7 | Quali biblioteche locali sono collegate a risorse esterne? | `rdfs:seeAlso`, `owl:sameAs`/altri mapping nei link graph | Le pagine ICCU sono documenti esterni (`rdfs:seeAlso`), non entità RDF equivalenti. |
| CQ8 | Qual è la distribuzione degli stati per regione? | osservazioni di stato + comune + `bf:regionName` + aggregazione | Conteggio distinto per biblioteca; il NULL ICCU resta `NESSUNO_STATO_SPECIALE_REGISTRATO`. |
| CQ9 | Quali comuni con elevata perdita demografica hanno la maggiore quota di biblioteche problematiche? | `bf:populationChangePercent2019_2025`, osservazioni di stato, municipio | “Problematiche” segue esclusivamente il criterio `include_in_main_analysis=True` definito nella pipeline di cleaning. La soglia di “elevata perdita” va passata come filtro esplicito nella query e non è codificata nell'ontologia. |

## Copertura delle RQ

Le CQ coprono RQ1–RQ5 e RQ7 nel knowledge graph; CQ7 supporta RQ6 sull’interlinking. La struttura per età (RQ8 secondaria) è rappresentata nelle osservazioni demografiche (`population0_14`, `population15_64`, `population65Plus`, `share65Plus`) ed è analizzata statisticamente mediante la relazione tra `share65Plus` e quota di biblioteche problematiche; i risultati sono riportati in `reports/analysis_tables/age65_problematic_correlation.csv` e nella visualizzazione `visualizations/age65_scatter.png`.