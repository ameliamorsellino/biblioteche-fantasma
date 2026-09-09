# Analisi finale per Research Question

## RQ1 - distribuzione territoriale

Il perimetro principale contiene **2.497 biblioteche problematiche** su **18.956 biblioteche** (13,17%). Le quote regionali più alte sono Molise **43,72% (80/183)**, Liguria **31,81% (209/657)**, Abruzzo **22,20% (93/419)** e Umbria **17,94% (73/407)**. In valore assoluto prevale la Lombardia con 366 casi. La mappa usa esclusivamente le coordinate ICCU già pulite.

## RQ2 - stati

Su 19.611 record: nessuno stato speciale registrato 13.200 (67,31%), non più esistente 1.827 (9,32%), non censita 1.723 (8,79%), confluita 1.502 (7,66%), altro istituto 655 (3,34%), temporaneamente chiusa 619 (3,16%). Confluenza e non-censimento non sono assimilati a cessazione.

## RQ3 - tipologie

Nel sottoinsieme con tipologia (N=13.715), la quota problematica è 7,65% per biblioteche di conservazione, 5,28% per pubbliche, 4,70% per specializzate, 2,37% per istituti di insegnamento superiore e 1,66% per scolastiche. L'associazione funzionale è statisticamente significativa ma piccola: Cramér V=0,066. Per la tipologia amministrativa V=0,059 e molte celle hanno frequenze attese basse, quindi l'interpretazione è soprattutto descrittiva.

## RQ4 - demografia

Analisi primaria: **N=6.659** comuni comparabili con almeno una biblioteca. Pearson `r=-0,1064`, Spearman `rho=-0,0670`: associazione negativa ma debole. Escludendo 115 outlier IQR della variazione demografica: `r=-0,0956`, `rho=-0,0584`. I comuni in calo hanno quota problematica media 12,42%, i comuni stabili/in crescita 8,48%. Non è evidenza causale.

## RQ5 - patrimonio e fondi speciali

**627/2.497** biblioteche problematiche hanno almeno una riga patrimonio, per 2.828 righe. Le quantità sono mancanti in 461 righe e positive in 2.367; nessuno zero esplicito. La somma delle sole quantità positive note è 7.500.259, ma non è un inventario complessivo perché la copertura è parziale e alcune categorie possono essere aggregati. Nessuna biblioteca problematica compare in `special_collection.csv`: è un'assenza di record nel sottoinsieme, non prova dell'assenza reale di fondi speciali.

## RQ6 - interlinking

Senza rieseguire i match, il checkpoint 2 registra: biblioteche verso ICCU **19.611/19.611 = 100%** (`rdfs:seeAlso`); comuni verso Linked ISPRA **7.893/7.896 = 99,9620%** (`owl:sameAs`). I tre non-match sono Lirio, Castegnero e Nanto, motivati da cambi amministrativi del 2026.

## RQ7 - confluenze

La rete validata contiene **1.412 archi**, **1.821 nodi**, **410 componenti deboli**; la componente maggiore ha 40 nodi. L'unico ciclo è il self-loop `IT-SS0267 -> IT-SS0267`. Il target con grado entrante maggiore è `IT-CT0337` (39). La visualizzazione mostra solo la componente maggiore per evitare uno spaghetti chart.

## RQ8 - quota 65+

Su N=6.659 comuni: Pearson `r=0,1454`, Spearman `rho=0,1054`. L'associazione è positiva ma debole e viene mantenuta come analisi secondaria non causale.
