# Decisions log

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
