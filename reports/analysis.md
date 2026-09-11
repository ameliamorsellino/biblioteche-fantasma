# Analisi finale per Research Question

## RQ1 - distribuzione territoriale

Il perimetro principale contiene **2.497 biblioteche problematiche** su **18.956 biblioteche** (13,17%). Le quote regionali più alte sono Molise **43,72% (80/183)**, Liguria **31,81% (209/657)**, Abruzzo **22,20% (93/419)** e Umbria **17,94% (73/407)**. In valore assoluto prevale la Lombardia con 366 casi. La mappa usa esclusivamente le coordinate ICCU già pulite.

## RQ2 - stati

Su 19.611 record: nessuno stato speciale registrato 13.200 (67,31%), non più esistente 1.827 (9,32%), non censita 1.723 (8,79%), confluita 1.502 (7,66%), altro istituto 655 (3,34%), temporaneamente chiusa 619 (3,16%). Confluenza e non-censimento non sono assimilati a cessazione.

## RQ3 - tipologie

L'analisi utilizza le tipologie funzionali e amministrative presenti nel master `library.csv`, evitando di definire il campione attraverso `library_type.csv`, la cui copertura è selettiva rispetto allo stato ICCU. Dopo l'esclusione dei 655 record classificati come “altro istituto collegato ICCU”, il campione comprende **18.956 biblioteche**.

Tra le tipologie funzionali, `NON SPECIFICATA` presenta 452 biblioteche problematiche su 1.233 (36,66%). Tra le categorie informative: conservazione 78/554 (14,08%), specializzata 630/4.694 (13,42%), istituto di insegnamento superiore 367/2.774 (13,23%), pubblica 903/8.162 (11,06%) e scolastica 65/1.275 (5,10%).

Considerando tutte le categorie, l'associazione tra tipologia funzionale e appartenenza al perimetro problematico ha **Cramér V corretto = 0,196**; per la tipologia amministrativa **V = 0,193**.

Il risultato è tuttavia sensibile alla categoria `NON SPECIFICATA`. Escludendola, il Cramér V scende a **0,077** per la tipologia funzionale (`N=17.723`) e a **0,095** per quella amministrativa (`N=17.844`). L'associazione residua è quindi debole e i risultati inferenziali vanno interpretati insieme alle distribuzioni descrittive, anche perché alcune celle hanno frequenze attese inferiori a 5.

## RQ4 - demografia

Analisi primaria: **N=6.659** comuni comparabili con almeno una biblioteca. Pearson `r=-0,1064`, Spearman `rho=-0,0670`: associazione negativa ma debole. Escludendo 115 outlier IQR della variazione demografica: `r=-0,0956`, `rho=-0,0584`. I comuni in calo hanno quota problematica media 12,42%, i comuni stabili/in crescita 8,48%. Non è evidenza causale.

## RQ5 - patrimonio e fondi speciali

**627/2.497** biblioteche problematiche hanno almeno una riga patrimonio, per 2.828 righe. Le quantità sono mancanti in 461 righe e positive in 2.367; nessuno zero esplicito. La somma delle sole quantità positive note è 7.500.259, ma non è un inventario complessivo perché la copertura è parziale e alcune categorie possono essere aggregati. Nessuna biblioteca problematica compare in `special_collection.csv`: è un'assenza di record nel sottoinsieme, non prova dell'assenza reale di fondi speciali.

## RQ6 - interlinking

La pipeline genera collegamenti per **19.611/19.611 biblioteche = 100%** verso ICCU tramite `rdfs:seeAlso` e per **7.893/7.896 comuni = 99,9620%** verso Linked ISPRA tramite `owl:sameAs`. I collegamenti sono costruiti deterministicamente a partire da identificatori ufficiali, senza fuzzy matching. I tre casi senza collegamento sono Lirio, Castegnero e Nanto, mantenuti intenzionalmente non collegati a causa delle variazioni amministrative intervenute nel 2026. La pipeline non dereferenzia individualmente tutte le URI esterne durante il rebuild offline, quindi la percentuale esprime la copertura di generazione dei collegamenti secondo la URI policy documentata.

## RQ7 - confluenze

La rete validata contiene **1.412 archi**, **1.821 nodi**, **410 componenti deboli**; la componente maggiore ha 40 nodi. L'unico ciclo è il self-loop `IT-SS0267 -> IT-SS0267`. Il target con grado entrante maggiore è `IT-CT0337` (39). La visualizzazione mostra solo la componente maggiore per evitare uno spaghetti chart.

## RQ8 - quota 65+

Su N=6.659 comuni: Pearson `r=0,1454`, Spearman `rho=0,1054`. L'associazione è positiva ma debole e viene mantenuta come analisi secondaria non causale.
