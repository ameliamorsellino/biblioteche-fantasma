# Valutazione 5-Star Open Data - Biblioteche Fantasma

## Perimetro della valutazione

La valutazione considera sia le caratteristiche tecniche degli artefatti sia
la loro effettiva pubblicazione sul Web.

La pubblicazione Web è disponibile a:

`https://ameliamorsellino.github.io/biblioteche-fantasma/`

Il knowledge graph RDF completo è distribuito come GitHub Release asset a:

`https://github.com/ameliamorsellino/biblioteche-fantasma/releases/latest/download/data.ttl`

Le principali evidenze utilizzate sono:

* `metadata/licenses.md`;
* `metadata/source_manifest.csv`;
* i dataset processati in CSV;
* `ontology/ontology.ttl`;
* `rdf/data.ttl`;
* `rdf/links.ttl`;
* `rdf/metadata.ttl`;
* i risultati di validazione RDF e SHACL;
* il report di interlinking;
* le query SPARQL e i relativi risultati;
* la pubblicazione GitHub Pages generata da `scripts/build_web_publication.py`;
* la release GitHub `v1.0.0`.

## Valutazione

| Livello | Requisito | Evidenza nel progetto | Valutazione |
| --- | --- | --- | --- |
| 1 STAR | Dati disponibili sul Web con licenza aperta | Dataset derivato documentato con CC BY 4.0, sito Web pubblico e distribuzioni scaricabili. | **Soddisfatto** |
| 2 STAR | Dati strutturati e machine-readable | Dataset processati in CSV strutturati e knowledge graph RDF. | **Soddisfatto** |
| 3 STAR | Formato aperto e non proprietario | CSV, RDF/Turtle/N-Triples e file SPARQL testuali. | **Soddisfatto** |
| 4 STAR | URI Web per identificare le risorse | URI HTTPS sotto `https://ameliamorsellino.github.io/biblioteche-fantasma/`; pagine Web generate per biblioteche e comuni. | **Soddisfatto** |
| 5 STAR | Collegamento verso dati esterni | Biblioteche verso ICCU con `rdfs:seeAlso`; comuni compatibili verso Linked ISPRA con `owl:sameAs`. | **Soddisfatto** |

## Pubblicazione Web

Il namespace pubblico è:

`https://ameliamorsellino.github.io/biblioteche-fantasma/`

Il deployment GitHub Pages è generato automaticamente dalla pipeline Web del
progetto. Sono generate pagine HTML per:

* 19.611 biblioteche;
* 7.896 comuni;
* 27.507 entità core complessive.

Esempi di risorse Web:

* `https://ameliamorsellino.github.io/biblioteche-fantasma/resource/library/IT-RM0267/`
* `https://ameliamorsellino.github.io/biblioteche-fantasma/resource/municipality/058091/`

Sono inoltre pubblicati:

* ontologia Turtle e RDF/XML;
* metadati DCAT;
* `rdf/links.ttl`;
* `rdf/metadata.ttl`.

Il knowledge graph completo `data.ttl` è distribuito tramite la release
GitHub `v1.0.0`. L'asset pubblicato ha dimensione 380.296.920 byte e digest:

`sha256:953ada1f4309cafcadd7562cef14eded4dd92e1f0585e223cbc787fee939be2f`

## Licenze

* **ICCU Anagrafe Open Data:** CC0 1.0.
* **ISTAT POSAS 2019 e 2025:** CC BY 4.0.
* **Cultural-ON:** CC BY 3.0 IT.
* **Dataset derivato del progetto:** CC BY 4.0, con attribuzione a ISTAT e citazione di ICCU tra le fonti.

## Interlinking

La pipeline genera collegamenti basati su identificatori ufficiali e non su
fuzzy matching:

* biblioteche verso ICCU: **19.611/19.611 = 100%**;
* comuni verso Linked ISPRA: **7.893/7.896 = 99,9620%**.

I tre comuni senza `owl:sameAs` sono mantenuti come non-match temporalmente
motivati invece di forzare collegamenti semanticamente scorretti.

Le URI Linked ISPRA sono costruite deterministicamente dal codice ISTAT
secondo la URI policy documentata. La percentuale rappresenta la copertura
di generazione dei link; la pipeline offline non effettua un controllo HTTP
individuale di tutti i 7.893 target.

## Limiti della pubblicazione statica

La pubblicazione usa GitHub Pages e pertanto non implementa un server Linked
Data dinamico con content negotiation completa basata sull'header HTTP
`Accept` o redirect 303 personalizzati.

Le entità core biblioteca e comune dispongono di rappresentazioni HTML
pubbliche. Altre risorse interne del knowledge graph, come osservazioni di
stato, holdings, address e geometry, possiedono URI HTTPS nel grafo ma non
necessariamente una pagina HTML dedicata.

Il knowledge graph completo e le distribuzioni RDF rimangono comunque
accessibili tramite URL Web pubblici.

## SPARQL

Le 11 query SPARQL vengono eseguite localmente con PyOxigraph.

Il progetto non pubblica un endpoint SPARQL pubblico. Questa è una scelta
architetturale e non impedisce il raggiungimento del quinto livello del
modello 5-star: il requisito centrale del livello 5 è il collegamento dei
dati locali verso altri dati sul Web.

## Valutazione finale

La versione pubblicata del progetto soddisfa i cinque livelli del modello
5-star Open Data: dati aperti sul Web, dati strutturati, formati aperti,
identificatori HTTP(S) e collegamenti verso risorse esterne.

La dichiarazione non implica che il progetto implementi tutte le
caratteristiche possibili di una piattaforma Linked Data server-side:
content negotiation completa, endpoint SPARQL pubblico e rappresentazioni
HTML dedicate per ogni URI interna restano estensioni possibili.
