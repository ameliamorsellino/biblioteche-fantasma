# Note di validazione e conformità DCAT

Il file `metadata/dcat.ttl` fornisce una descrizione RDF/DCAT del dataset
e delle principali distribuzioni del progetto.

La descrizione include identificatore, titolo, descrizione, publisher,
creator, licenza, lingua, copertura geografica, frequenza, tema, keyword,
distribuzioni, formato, media type, accessURL e downloadURL.

## DCAT-AP_IT

Il progetto non dichiara una conformità operativa completa a DCAT-AP_IT
nella distribuzione locale corrente.

Le risorse utilizzano infatti il namespace di sviluppo
`https://biblioteche-fantasma.invalid/` e le distribuzioni sono referenziate
tramite URI locali `file:`.

Una pubblicazione conforme su un catalogo richiederebbe URI HTTP(S)
pubbliche e persistenti, URL di accesso/download realmente disponibili
sul Web e una validazione rispetto alla versione del profilo DCAT-AP_IT
applicabile al momento della pubblicazione.
