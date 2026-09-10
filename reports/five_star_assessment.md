# Valutazione 5-Star Open Data - Biblioteche Fantasma

## Perimetro della valutazione

La valutazione distingue le caratteristiche tecniche degli artefatti prodotti dalla loro effettiva pubblicazione sul Web.

Le evidenze utilizzate sono:

* `metadata/licenses.md`;
* `metadata/source_manifest.csv`;
* i dataset processati in CSV;
* `ontology/ontology.ttl`;
* `rdf/data.ttl`;
* `rdf/links.ttl`;
* `rdf/metadata.ttl`;
* i risultati di validazione RDF e SHACL;
* il report di interlinking;
* le query SPARQL e i relativi risultati.

| Livello | Requisito                                        | Evidenza nel progetto                                                                                                                 | Valutazione                                                                                                                |
| ------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| 1 STAR  | Dati disponibili sul Web con licenza aperta      | Le fonti ICCU e ISTAT sono Open Data; il dataset derivato è documentato con licenza CC BY 4.0.                                        | **Parziale**: la condizione giuridica è soddisfatta, ma il dataset derivato non è ancora pubblicato a un URL Web pubblico. |
| 2 STAR  | Dati strutturati e machine-readable              | I dataset processati sono distribuiti in CSV strutturati.                                                                             | **Tecnicamente soddisfatto**, ferma restando l'assenza della pubblicazione Web.                                            |
| 3 STAR  | Formato aperto e non proprietario                | CSV per i dati tabellari; RDF/Turtle per il knowledge graph; query SPARQL in file testuali.                                           | **Tecnicamente soddisfatto**, ferma restando l'assenza della pubblicazione Web.                                            |
| 4 STAR  | Uso di RDF e URI per identificare le risorse     | Il progetto usa RDF, OWL, SKOS, DCAT, PROV-O, GeoSPARQL e URI deterministiche.                                                        | **Parziale**: le URI locali utilizzano `https://biblioteche-fantasma.invalid/` e non sono dereferenziabili.                |
| 5 STAR  | Collegamento delle risorse locali a dati esterni | Le biblioteche sono collegate a ICCU tramite `rdfs:seeAlso`; i comuni compatibili sono collegati a Linked ISPRA tramite `owl:sameAs`. | **Parziale**: l'interlinking esiste ed è riproducibile, ma le URI locali non sono ancora pubblicate sul Web.               |

## Licenze

* **ICCU Anagrafe Open Data:** CC0 1.0.
* **ISTAT POSAS 2019 e 2025:** CC BY 4.0.
* **Cultural-ON:** CC BY 3.0 IT.
* **Dataset derivato del progetto:** CC BY 4.0, con attribuzione a ISTAT e citazione di ICCU tra le fonti.

## Interlinking

La pipeline genera collegamenti basati su identificatori ufficiali e non su fuzzy matching:

* biblioteche verso ICCU: **19.611/19.611 = 100%** di collegamenti generati;
* comuni verso Linked ISPRA: **7.893/7.896 = 99,9620%** di collegamenti generati.

I tre comuni senza `owl:sameAs` sono mantenuti come non-match temporalmente motivati invece di forzare collegamenti semanticamente scorretti.

Le URI Linked ISPRA sono costruite deterministicamente dal codice ISTAT secondo la URI policy documentata. Lo schema delle URI è stato verificato su risorse esterne reali, ma la pipeline offline non dereferenzia individualmente tutti i 7.893 target; la percentuale va quindi interpretata come copertura di generazione dei collegamenti, non come tasso di risposta HTTP verificato singolarmente.

## Passaggi necessari per una pubblicazione 5-star operativa

Per completare una vera pubblicazione Linked Open Data sul Web occorrerebbe:

1. utilizzare un namespace HTTP(S) reale, stabile e controllato;
2. pubblicare URI dereferenziabili per le risorse locali;
3. esporre sul Web dataset, RDF e metadati tramite URL funzionanti;
4. aggiornare `dcat:accessURL` e `dcat:downloadURL` con URL HTTP(S) pubblici;
5. mantenere nel tempo i collegamenti alle risorse esterne.

Un endpoint SPARQL pubblico sarebbe utile, ma non è di per sé un requisito necessario del modello 5-star.

## Valutazione finale

Il progetto implementa tecnicamente dati strutturati in formato aperto, modellazione RDF, URI e interlinking verso Linked Open Data esterni.

Non viene tuttavia dichiarato come pubblicazione 5-star operativa, perché il namespace locale `.invalid` non è pubblico né dereferenziabile.
