# Decisions log — Checkpoint 1

# Decisione D01

## Problema
NULL dello stato ICCU

## Evidenza
13200 record hanno `source_status` vuoto. La documentazione ICCU usa il campo per segnalare stati speciali quando valorizzato.

## Alternative considerate
Interpretare NULL come aperta; escludere; categoria neutra.

## Decisione
Usare `NESSUNO_STATO_SPECIALE_REGISTRATO`.

## Motivazione
L’assenza di un valore non dimostra apertura.

## Conseguenza
I NULL non entrano automaticamente nelle categorie problematiche.

# Decisione D02

## Problema
Definizione di main_problematic_libraries

## Evidenza
Il mapping canonico include solo stati con `include_in_main_analysis=True`: cessazione, chiusura temporanea, inagibilità/sospensione sisma, riapertura parziale, deposito senza punto di servizio.

## Alternative considerate
Includere anche confluenze/non censite/allestimento; includere tutti gli stati non null.

## Decisione
Somma solo gli stati marcati True in `metadata/status_mapping.csv`.

## Motivazione
Mantiene separate cessazione, interruzione, parzialità, trasformazione organizzativa e incompletezza anagrafica.

## Conseguenza
Conteggio nazionale = 2.497.

# Decisione D03

## Problema
Relazioni XML 1:N

## Evidenza
Patrimonio 93,512 righe, fondi 9,737, contatti 62,804; più righe per ISIL.

## Alternative considerate
Mega-CSV con duplicazione delle biblioteche; tabelle separate.

## Decisione
Conservare tabelle normalizzate per relazione.

## Motivazione
Evita moltiplicazioni spurie e perdita di cardinalità.

## Conseguenza
Join successivi devono rispettare 1:N.

# Decisione D04

## Problema
Coordinate (0,0)

## Evidenza
63 biblioteche hanno coppia originale (0,0).

## Alternative considerate
Trattare come coordinata reale; geocodificare; marcare missing.

## Decisione
Coordinate pulite impostate a missing; originali preservate.

## Motivazione
(0,0) è uno pseudo-valore non utile per localizzare una biblioteca italiana.

## Conseguenza
Nessuna imputazione geografica automatica.

# Decisione D05

## Problema
Coordinate fuori bounding box

## Evidenza
3 record sono fuori dal bounding box indicativo Italia ma nel range mondiale.

## Alternative considerate
Cancellare; correggere/geocodificare; preservare con flag.

## Decisione
Preservare e marcare `outside_italy_bbox_review`.

## Motivazione
Una sede italiana può trovarsi all’estero; il bounding box è controllo, non prova di errore.

## Conseguenza
Tre record richiedono interpretazione.

# Decisione D06

## Problema
IT-ME0024

## Evidenza
Tra i tre outlier geografici, `IT-ME0024` ha coordinate compatibili con l’India, non con la localizzazione territoriale attesa.

## Alternative considerate
Correggere da indirizzo; eliminare; segnalare.

## Decisione
Segnalare senza correzione automatica.

## Motivazione
Manca una fonte certa per sostituire le coordinate.

## Conseguenza
Anomalia aperta per revisione manuale.

# Decisione D07

## Problema
Parsing delle confluenze

## Evidenza
1,502 record di confluenza; 1,412 target ISIL estratti; 90 senza target parseabile.

## Alternative considerate
Parsing libero/fuzzy; regex controllata; nessun parsing.

## Decisione
Regex esatta `Biblioteca confluita in IT-XXdddd`; target validato contro snapshot.

## Motivazione
L’ISIL ha formato ufficiale e consente validazione deterministica.

## Conseguenza
1.412 target esistono nello snapshot; 90 restano senza target.

# Decisione D08

## Problema
Self-loop IT-SS0267

## Evidenza
`IT-SS0267 → IT-SS0267` è presente nella sorgente dopo parsing e target validation.

## Alternative considerate
Rimuovere/correggere; preservare e segnalare.

## Decisione
Preservare con `self_loop=True` e `in_cycle=True`.

## Motivazione
Nessuna evidenza autorizza una correzione.

## Conseguenza
Unico ciclo rilevato nel grafo delle confluenze.

# Decisione D09

## Problema
Età=999 ISTAT

## Evidenza
Per 7.954 comuni 2019 e 7.896 comuni 2025 la riga `Età=999` coincide esattamente con la somma delle età 0–100; mismatch 0.

## Alternative considerate
Assumerla senza verifica; ricalcolare sempre; validarla e usarla.

## Decisione
Usare 999 come totale dopo verifica empirica completa.

## Motivazione
Evita interpretazioni non documentate o assunte.

## Conseguenza
Totali comunali impiegati per popolazione 2019/2025.

# Decisione D10

## Problema
Comune “None” e keep_default_na=False

## Evidenza
Esiste un comune ufficiale denominato `None`; i parser pandas standard possono trattare la stringa come NA.

## Alternative considerate
Parsing NA predefinito; eccezione a posteriori; preservazione stringhe.

## Decisione
Leggere POSAS con `keep_default_na=False`.

## Motivazione
Conserva il nome ufficiale senza perdita informativa.

## Conseguenza
Il comune None resta una stringa valida.

# Decisione D11

## Problema
Variazioni amministrative 2019–2025

## Evidenza
Geografia 2019: 7.954 comuni; 2025: 7.896; crosswalk: 7,955 relazioni verso 7.896 comuni correnti.

## Alternative considerate
Join per nome/fuzzy; eliminare non-match; crosswalk ufficiale per codici e predecessori.

## Decisione
Geografia analitica 2025 e crosswalk esplicito per codice/predecessori.

## Motivazione
I codici ufficiali e le trasformazioni amministrative sono più affidabili del fuzzy matching.

## Conseguenza
Fusioni/incorporazioni aggregano predecessori quando ricostruibili.

# Decisione D12

## Problema
Trapani/Misiliscemi

## Evidenza
Misiliscemi nasce da scorporo territoriale di Trapani nel 2021; il POSAS comunale 2019 non consente di sottrarre correttamente il territorio.

## Alternative considerate
Attribuire tutto Trapani 2019 a uno dei due; stimare; segnare non comparabile.

## Decisione
Entrambi marcati `not_comparable_due_to_2021_territorial_split` per il confronto 2019.

## Motivazione
Qualsiasi ripartizione sarebbe inventata.

## Conseguenza
Population 2019 e variazioni restano NA per i due comuni.

# Decisione D13

## Problema
Denominazione Reggio Calabria / Reggio di Calabria

## Evidenza
Nel POSAS 2025 Province, codice provincia 080, la denominazione ufficiale è `Reggio di Calabria`; 97 comuni appartengono alla provincia 080.

## Alternative considerate
Usare etichetta ICCU `Reggio Calabria`; usare POSAS 2025.

## Decisione
Nel dataset analitico la provincia è canonizzata dal POSAS 2025 e vale `Reggio di Calabria`.

## Motivazione
Il dataset analitico usa la geografia territoriale ISTAT 2025 come fonte canonica.

## Conseguenza
Il rebuild produce deterministicamente 97 righe con `Reggio di Calabria`.

# Decisione D14

## Problema
Differenza testuale di rationale

## Evidenza
`library_status.csv` e `metadata/status_mapping.csv` ora usano la stessa funzione `classify_status`; confronto canonico: 0 differenze.

## Alternative considerate
Mantenere testi indipendenti; sincronizzazione manuale; funzione unica.

## Decisione
Usare la stessa funzione canonica per entrambi gli output.

## Motivazione
Elimina drift puramente testuale mantenendo identica semantica.

## Conseguenza
Il validator verifica uguaglianza del rationale per ogni source_status.

# Decisione D15

## Problema
Anomalia data-export di patrimonio.xml

## Evidenza
La radice di `patrimonio.xml` dichiara `data-export="2026-09-08T14:00:"`, timestamp sintatticamente incompleto.

## Alternative considerate
Correggere il timestamp; ignorarlo; registrare anomalia.

## Decisione
Non modificare la sorgente; registrare l’anomalia.

## Motivazione
Non esiste evidenza per inferire i secondi mancanti.

## Conseguenza
Snapshot principale resta determinato da biblioteche.json; il timestamp XML rimane nota di qualità.

# Decisione D16

## Problema
Licenza del dataset derivato

## Evidenza
ICCU Open Data = CC0; POSAS Istat = CC BY 4.0; Cultural-ON è separata e non contribuisce ai valori tabellari in questa fase.

## Alternative considerate
CC0; CC BY 4.0; altra licenza senza analisi.

## Decisione
Licenza prevista per il dataset tabellare derivato: CC BY 4.0.

## Motivazione
Rispetta l’obbligo di attribuzione derivante dalla componente Istat e consente riuso/modifica/commerciale.

## Conseguenza
Attribuire Istat; citare ICCU; non relicenziare automaticamente Cultural-ON o documentazione ICCU.

# Decisione D17

## Problema
Modellazione di biblioteca e localizzazione senza duplicare Cultural-ON.

## Evidenza
Nel file locale `data/external/cultural-ON.owl` esistono `cis:Library`, `cis:CulturalInstituteOrSite`, `cis:Site`, `cis:hasSite`, `cis:hasGeographicalLocation`, `cis:GovernamentalAdministrativeArea` e `cis:hasISTATCode`. Non esiste una classe `cis:Municipality`; inoltre il termine effettivo è `cis:GeographicalFeature`, non `cis:GeographicalArea`.

## Nuova decisione
Riutilizzare integralmente il percorso `cis:Library → cis:hasSite → cis:Site → cis:hasGeographicalLocation → bf:Municipality`, dove `bf:Municipality rdfs:subClassOf cis:GovernamentalAdministrativeArea`.

## Motivazione
Massimizza il riuso e crea solo la specializzazione mancante per il comune.

## Conseguenza
Non viene creata una proprietà locale `locatedIn`; le query di localizzazione usano il percorso Cultural-ON a due salti.

# Decisione D18

## Problema
Rappresentazione temporale degli stati ICCU.

## Evidenza
Lo snapshot ICCU ha data `2026-09-08T14:11:15`, ma non fornisce una data di inizio dello stato. `cis:TemporaryClosure` esiste e `cis:hasDate` indica la data della chiusura temporanea, non la data in cui un record è stato osservato.

## Nuova decisione
Creare `bf:LibraryStatusObservation` con `bf:observationDate`, `bf:observedLibrary` e `bf:hasStatus`; gli 11 stati normalizzati sono `skos:Concept`.

## Motivazione
Evita di trasformare la data dello snapshot in una data di chiusura inesistente e rispetta l'Open World Assumption.

## Conseguenza
`TEMPORANEAMENTE_CHIUSA` e `INAGIBILE` sono concetti di stato osservato; non vengono materializzati come eventi di chiusura con date inventate.

# Decisione D19

## Problema
Modellazione del patrimonio ICCU e dei fondi speciali.

## Evidenza
`cis:Collection` rappresenta collezioni/patrimonio; le 93.512 righe `library_holdings.csv` sono invece righe per tipo di materiale con quantità opzionale, mentre i 9.737 record `special_collection.csv` descrivono fondi identificabili.

## Nuova decisione
Usare `bf:HoldingObservation` per le righe patrimonio e `bf:SpecialCollection rdfs:subClassOf cis:Collection` per i fondi speciali.

## Motivazione
Evita di dichiarare ogni categoria di materiale come collezione autonoma e conserva la cardinalità 1:N del checkpoint 1.

## Conseguenza
CQ6 interroga `bf:materialType`; CQ2 usa `cis:hasCollection` verso `bf:SpecialCollection`.

# Decisione D20

## Problema
URI locali senza un dominio di pubblicazione controllato.

## Evidenza
Il progetto non dispone di un dominio reale; usare `example.org` o un dominio inventato simulerebbe dereferenziazione.

## Nuova decisione
Usare in sviluppo `https://biblioteche-fantasma.invalid/` e documentare una futura migrazione dell'autorità, mantenendo path e chiavi deterministiche.

## Motivazione
`.invalid` rende esplicito che le URI non sono pubblicate sul Web.

## Conseguenza
Il dataset è RDF con URI, ma non soddisfa pienamente il requisito Web/dereferenziazione per una dichiarazione 4/5-star operativa.

# Decisione D21

## Problema
Confluenze con target incompleto.

## Evidenza
`library_mergers.csv` contiene 1.502 record: 1.412 target parseati ed esistenti nello snapshot, 90 senza target parseabile; è presente il self-loop `IT-SS0267 → IT-SS0267`.

## Nuova decisione
Asserire `bf:mergedInto` solo per i 1.412 target validati, preservando anche il self-loop sorgente; nessun arco per i 90 casi senza target.

## Motivazione
Non inventa identità o destinazioni e conserva l'evidenza del checkpoint 1.

## Conseguenza
Il grafo delle confluenze contiene esattamente 1.412 archi RDF, incluso un self-loop noto.
\n\n# Phase 2 — closure decisions\n\n# Decisione D22 — riuso di `cis:Library` e dei termini Cultural-ON verificati\n\n## Problema\nEvitare di ricreare localmente concetti già coperti da Cultural-ON e, allo stesso tempo, non assumere termini inesistenti.\n\n## Evidenza\nIl file locale `data/external/cultural-ON.owl` è stato parsato e contiene realmente `cis:Library`, `cis:CulturalInstituteOrSite`, `cis:ISILIdentifier`, `cis:Site`, `cis:Address`, `cis:Collection`, `cis:hasSite`, `cis:hasAddress`, `cis:hasGeographicalLocation`, `cis:hasCollection`, `cis:hasISTATCode`, `cis:institutionalName`, `cis:description`, `cis:GovernamentalAdministrativeArea`, `cis:TemporaryClosure` e `cis:TemporaryClosureType`.\n\n## Alternative considerate\nCreare classi/proprietà locali equivalenti; usare Schema.org come vocabolario primario; riusare Cultural-ON selettivamente.\n\n## Decisione\nRiutilizzare Cultural-ON come base dove la semantica coincide; `cis:Library` resta la classe delle biblioteche.\n\n## Motivazione\nSegue il principio REUSE > EXTEND > CREATE e riduce duplicazione semantica.\n\n## Conseguenza\nLe query e i dati usano direttamente i termini Cultural-ON verificati; i termini locali sono limitati ai concetti mancanti.\n\n# Decisione D23 — osservazioni temporali di stato\n\n## Problema\nLo stato ICCU è noto a uno snapshot, ma la sorgente non fornisce l'inizio/fine dello stato.\n\n## Evidenza\nLo snapshot ICCU è datato 2026-09-08; `cis:TemporaryClosure`/`cis:hasDate` descrivono una chiusura e la sua data, non una generica osservazione temporale.\n\n## Alternative considerate\nAsserire `Library → status` atemporalmente; usare `cis:TemporaryClosure` per ogni stato; introdurre un nodo osservazione.\n\n## Decisione\nCreare `bf:LibraryStatusObservation` con `bf:observedLibrary`, `bf:hasStatus`, `bf:observationDate` e provenance.\n\n## Motivazione\nPreserva il significato dello snapshot e non inventa date di inizio/fine.\n\n## Conseguenza\nLe CQ sullo stato interrogano osservazioni datate; l'assenza di altre osservazioni non è interpretata come negazione.\n\n# Decisione D24 — stati come concetti SKOS\n\n## Problema\nGli 11 valori di stato sono categorie controllate eterogenee, non tipi ontologici di biblioteca.\n\n## Evidenza\nIl mapping della Fase 1 distingue cessazione, confluenza, chiusura temporanea, inagibilità, sospensione sisma, riapertura parziale e altri stati.\n\n## Alternative considerate\nUna classe OWL per ogni stato; un literal libero; risorse SKOS.\n\n## Decisione\nRappresentare gli stati come `skos:Concept` in un `skos:ConceptScheme`.\n\n## Motivazione\nEvita proliferazione di classi e mantiene etichette/codici interrogabili.\n\n## Conseguenza\n`bf:hasStatus` punta a risorse concettuali; nessuna categoria narrativa “Biblioteche Fantasma” viene introdotta come classe ufficiale.\n\n# Decisione D25 — namespace provvisorio `.invalid`\n\n## Problema\nNon esiste un dominio di pubblicazione controllato dal progetto.\n\n## Evidenza\nNessun endpoint o dominio reale è disponibile nel checkpoint.\n\n## Alternative considerate\nUsare `example.org`; inventare un dominio plausibile; usare `.invalid` e dichiarare la natura di sviluppo.\n\n## Decisione\nUsare `https://biblioteche-fantasma.invalid/ontology/` e `https://biblioteche-fantasma.invalid/resource/`.\n\n## Motivazione\nIl TLD riservato rende esplicita la non-dereferenziazione e impedisce di simulare una pubblicazione Web.\n\n## Conseguenza\nIl grafo è tecnicamente RDF/URI ma la valutazione 4/5-star resta parziale finché non esiste un namespace HTTP(S) pubblico e dereferenziabile.\n\n# Decisione D26 — separazione ontology/data/links/metadata\n\n## Problema\nMescolare schema, istanze, interlinking e metadati ridurrebbe tracciabilità e facilità d'import.\n\n## Evidenza\nGli artefatti hanno ruoli distinti e vengono validati separatamente.\n\n## Alternative considerate\nUn solo file RDF monolitico; quattro componenti separati.\n\n## Decisione\nConservare `ontology/ontology.ttl`, `rdf/data.ttl`, `rdf/links.ttl` e `rdf/metadata.ttl` separati.\n\n## Motivazione\nSupporta provenance, named graph e test indipendenti.\n\n## Conseguenza\nGraphDB può importarli in grafi separati; il totale esplicito è la somma dei quattro file.\n\n# Decisione D27 — duplicati dei nomi precedenti\n\n## Problema\n`library_previous_name.csv` contiene ripetizioni esatte che produrrebbero asserzioni RDF identiche.\n\n## Evidenza\nIl processed file contiene 9.507 righe; sulla coppia (`isil`, `previous_name_original`) sono presenti **46 righe duplicate oltre la prima**, distribuite in 44 gruppi.\n\n## Alternative considerate\nDuplicare serialmente la stessa tripla; modificare il processed data; deduplicare soltanto l'asserzione RDF.\n\n## Decisione\nPreservare il CSV della Fase 1 e sopprimere solo le asserzioni RDF esattamente duplicate durante la serializzazione.\n\n## Motivazione\nUn grafo RDF è un insieme di triple e la ripetizione non aggiunge informazione.\n\n## Conseguenza\n`rdf/data.ttl` contiene 0 triple serializzate duplicate; la sorgente processed resta invariata.\n\n# Decisione D28 — link delle biblioteche verso ICCU\n\n## Problema\nLa pagina ICCU identificata per ISIL è un documento HTML di consultazione, non una risorsa RDF dimostrata equivalente all'entità locale biblioteca.\n\n## Evidenza\n`library_links.csv` contiene 19.611 lookup esatti per ISIL verso la pagina ufficiale Anagrafe e nessun fuzzy matching.\n\n## Alternative considerate\n`owl:sameAs`; `skos:exactMatch`; `rdfs:seeAlso`.\n\n## Decisione\nUsare `rdfs:seeAlso` per i collegamenti ICCU.\n\n## Motivazione\nEvita di affermare identità ontologica tra la biblioteca e una pagina HTML/documento di ricerca.\n\n## Conseguenza\nCoverage biblioteche: 19.611/19.611 = 100%; il link è informativo/verificabile ma non è un'asserzione di identità.\n\n# Decisione D29 — link dei comuni verso Linked ISPRA\n\n## Problema\nStabilire quando sia semanticamente giustificato `owl:sameAs`.\n\n## Evidenza\nLinked ISPRA usa risorse comunali con URI che incorporano il codice ISTAT a sei cifre. Per 7.893 comuni della geografia 2025 il codice identifica la medesima unità amministrativa.\n\n## Alternative considerate\nMatching per nome; `skos:closeMatch`; `rdfs:seeAlso`; identità per codice ISTAT.\n\n## Decisione\nUsare `owl:sameAs` solo per i 7.893 comuni con identità deterministica per codice ISTAT.\n\n## Motivazione\nIl codice ufficiale consente un'identità di entità più forte del semplice collegamento documentale.\n\n## Conseguenza\nCoverage comuni: 7.893/7.896 = 99,9620%; nessun `owl:sameAs` è prodotto per i tre casi temporalmente non allineati.\n\n# Decisione D30 — nessun fuzzy matching nell'interlinking\n\n## Problema\nI nomi di biblioteche e comuni possono essere ambigui o variare nel tempo.\n\n## Evidenza\nSono disponibili ISIL e codici ISTAT ufficiali.\n\n## Alternative considerate\nFuzzy matching testuale; matching esatto sugli identificatori.\n\n## Decisione\nEscludere il fuzzy matching dall'interlinking della Fase 2.\n\n## Motivazione\nGli identificatori ufficiali sono più riproducibili e riducono falsi positivi.\n\n## Conseguenza\nI non-match non vengono forzati artificialmente.\n\n# Decisione D31 — tre comuni 2025 senza match Linked ISPRA 2026\n\n## Problema\nLirio, Castegnero e Nanto appartengono alla geografia analitica 2025 ma non devono essere forzati verso risorse comunali correnti del 2026.\n\n## Evidenza\nI CSV di interlinking riportano `unmatched_temporal_scope` per i codici 018082, 024027 e 024071. Fonti istituzionali 2026 confermano: Lirio incorporato in Montalto Pavese con decorrenza 31-01-2026; Castegnero e Nanto fusi nel nuovo Comune “Castegnero Nanto” dal 21-02-2026.\n\n## Alternative considerate\nAggiornare retroattivamente la geografia 2025; collegare ai successori con `owl:sameAs`; lasciare non-match temporalmente motivati.\n\n## Decisione\nMantenere la geografia analitica 2025 invariata e lasciare i tre comuni senza `owl:sameAs` corrente.\n\n## Motivazione\nIl cambio amministrativo è successivo al periodo analitico e il successore non è la stessa entità amministrativa nel medesimo assetto temporale.\n\n## Conseguenza\nCoverage 99,9620%, con tre non-match documentati invece di un 100% artificiale.\n\n# Decisione D32 — limite SHACL\n\n## Problema\n`pyshacl` non è disponibile nell'ambiente.\n\n## Evidenza\nIl modulo non è installato; `shacl/shapes.ttl` esiste e il validatore locale implementa solo le feature SHACL Core effettivamente usate dalle shape.\n\n## Alternative considerate\nDichiarare SHACL non eseguito; simulare pySHACL; eseguire realmente il sottoinsieme implementato e documentarne il perimetro.\n\n## Decisione\nEseguire `scripts/validate_shacl.py` sulle shape reali e qualificare il risultato come validazione del sottoinsieme SHACL Core implementato.\n\n## Motivazione\nProduce un controllo reale senza sovrastimare la capacità del motore.\n\n## Conseguenza\n82.519 focus nodes controllati, 0 violazioni nel sottoinsieme; non equivale a una validazione completa pySHACL/GraphDB.\n\n# Decisione D33 — GraphDB non eseguito\n\n## Problema\nL'ambiente non fornisce un'istanza GraphDB eseguita e verificata.\n\n## Evidenza\nNon esistono log, repository o output GraphDB prodotti nella sessione.\n\n## Alternative considerate\nInventare risultati; omettere GraphDB; consegnare un progetto import-ready con istruzioni operative.\n\n## Decisione\nDichiarare GraphDB **IMPORT-READY ma NON ESEGUITO** e creare `graphdb/README.md`.\n\n## Motivazione\nMantiene verificabilità e separa preparazione da esecuzione.\n\n## Conseguenza\nNessun conteggio o risultato query viene attribuito a GraphDB.\n\n# Decisione D34 — limite di esecuzione SPARQL con RDFLib\n\n## Problema\nIl projection graph locale è sufficiente per il parsing e per alcuni test, ma query con join/aggregazioni possono essere lente in RDFLib.\n\n## Evidenza\nTutte le 11 query passano `parseQuery`; `01_status_distribution.rq` è stata eseguita e ha prodotto 11 righe. Il tentativo di eseguire `02_status_by_region.rq` non si è concluso entro il budget operativo, e ulteriori esecuzioni massicce non sono state forzate.\n\n## Alternative considerate\nTentare indefinitamente tutte le query; dichiarare il solo parsing; eseguire soltanto test rapidi e documentare separatamente parsing/esecuzione.\n\n## Decisione\nRegistrare 11/11 query sintatticamente valide, 1/11 eseguita e salvata nella chiusura finale; rinviare il collaudo completo a GraphDB o a un motore RDF più adatto.\n\n## Motivazione\nEvita di confondere correttezza sintattica con esecuzione e non consuma la sessione in query non terminate.\n\n## Conseguenza\n`reports/sparql_test_report.md` riporta lo stato per ciascun file; nessun risultato non ottenuto è inventato.\n
# Phase 3 - analisi, visualizzazione e relazione finale

# Decisione D35 - unità di analisi demografica

## Problema
La relazione tra dinamica demografica e biblioteche può essere distorta dai comuni senza biblioteche e dalle variazioni amministrative non comparabili.

## Evidenza
`analysis_municipality.csv` contiene 7.896 comuni; 6.660 hanno almeno una biblioteca e due comuni (Trapani e Misiliscemi) sono marcati non comparabili per il 2019.

## Alternative considerate
Correlare tutti i comuni includendo quote mancanti; imputare zero ai comuni senza biblioteche; limitare l'analisi ai comuni comparabili con almeno una biblioteca.

## Decisione
Per RQ4 usare come analisi primaria i 6.659 comuni comparabili con almeno una biblioteca e valori disponibili di `population_change_percent` e `problematic_share`.

## Motivazione
La quota problematica non è definita quando il denominatore biblioteche è zero e i due comuni dello split 2021 non hanno una baseline omogenea.

## Conseguenza
Pearson e Spearman sono calcolati su N=6.659; è prodotta anche una sensitivity analysis che esclude 115 outlier IQR della variazione demografica.

# Decisione D36 - correlazione non causale e robustezza

## Problema
`problematic_share` è una variabile limitata a [0,1], con molti zeri e valori discreti nei comuni con poche biblioteche.

## Evidenza
La correlazione primaria è Pearson r=-0,1064 e Spearman rho=-0,0670; eliminando gli outlier IQR della variazione demografica i valori restano deboli (r=-0,0956; rho=-0,0584).

## Alternative considerate
Riportare solo Pearson; stimare causalità; usare sia correlazione lineare sia monotona e confronto tra gruppi.

## Decisione
Riportare Pearson, Spearman, N, outlier e confronto comuni in calo vs stabili/in crescita; non attribuire causalità.

## Motivazione
La convergenza tra misure mostra che l'associazione è statisticamente rilevabile ma di entità piccola.

## Conseguenza
RQ4 viene interpretata come relazione debole, non come prova che lo spopolamento provochi cessazioni o interruzioni.

# Decisione D37 - patrimonio e fondi speciali

## Problema
La copertura dei dataset bibliotecari secondari è selettiva e i missing non possono essere trasformati in zero.

## Evidenza
Tra 2.497 biblioteche problematiche, 627 hanno almeno una riga patrimonio (2.828 righe); 461 righe hanno quantità mancante e 2.367 una quantità positiva. Nessuna biblioteca problematica ha un record in `special_collection.csv`; tutti i 9.737 record di fondi speciali appartengono a biblioteche con `NESSUNO_STATO_SPECIALE_REGISTRATO`.

## Alternative considerate
Interpretare assenza di record come assenza di patrimonio/fondo; imputare quantità; descrivere la sola copertura documentaria.

## Decisione
Separare esplicitamente dato documentato, quantità mancante, zero esplicito e assenza di record. Non inferire assenza di fondi speciali.

## Motivazione
Rispetta l'Open World Assumption e il principio metodologico `missing != zero`.

## Conseguenza
La visualizzazione RQ5 comunica copertura documentaria, non inventario completo.

# Decisione D38 - visualizzazione della rete di confluenze

## Problema
La rete completa ha 1.821 nodi, 1.412 archi e 410 componenti: visualizzarla integralmente produrrebbe uno spaghetti chart.

## Evidenza
La componente debole più grande contiene 40 nodi; l'unico ciclo è il self-loop IT-SS0267.

## Alternative considerate
Disegnare tutta la rete; omettere completamente la rete; visualizzare solo la componente maggiore e fornire tabelle complete degli hub/componenti.

## Decisione
Visualizzare la sola componente debole maggiore con etichette limitate agli hub e accompagnarla con `merger_network_summary.csv`, `merger_components.csv` e `merger_targets_top.csv`.

## Motivazione
Preserva leggibilità senza nascondere le statistiche della rete completa.

## Conseguenza
`visualizations/mergers_network.png` è una vista illustrativa della struttura, non la totalità degli archi.

# Decisione D39 - Pandas/Scipy/NetworkX vs SPARQL

## Problema
Le aggregazioni statistiche e i test di associazione sono più diretti sui processed data, mentre SPARQL è necessario per dimostrare la modellazione semantica e le competency questions.

## Evidenza
La suite SPARQL è sintatticamente valida ma l'esecuzione RDFLib completa è stata limitata da performance; i processed data contengono già le misure necessarie alle RQ quantitative.

## Alternative considerate
Forzare tutte le analisi in SPARQL; usare solo tabelle e ignorare il knowledge graph; separare i compiti.

## Decisione
Usare Pandas/Scipy per analisi quantitative, NetworkX per confluenze e RDF/SPARQL per interrogazione semantica/competency questions.

## Motivazione
Ogni strumento viene usato nel dominio in cui è più robusto e leggibile.

## Conseguenza
La relazione distingue esplicitamente analisi statistica e interrogazione del knowledge graph.

# Decisione D40 - Parquet nell'ambiente di build

## Problema
Il requisito di consegna include CSV/Parquet, ma l'ambiente non dispone di un motore Parquet.

## Evidenza
`pyarrow`, `fastparquet` e DuckDB non sono installati; il tentativo di installare `pyarrow` è fallito perché l'ambiente non ha accesso di rete.

## Alternative considerate
Creare file `.parquet` non validi; omettere il problema; fornire uno script deterministico di esportazione.

## Decisione
Non creare file Parquet fittizi. Conservare i CSV canonici, aggiungere `scripts/export_parquet.py` e documentare la dipendenza opzionale `pyarrow`.

## Motivazione
Un artefatto invalido sarebbe peggiore di una limitazione dichiarata.

## Conseguenza
La consegna contiene CSV e una procedura riproducibile per Parquet; la materializzazione Parquet resta un'operazione manuale residua.
