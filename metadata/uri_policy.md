# URI Policy - Biblioteche Fantasma

## Stato della policy

Il progetto utilizza un namespace HTTP(S) pubblico associato alla pubblicazione Web tramite GitHub Pages:

- **base URI**: `https://ameliamorsellino.github.io/biblioteche-fantasma/`
- **ontology namespace**: `https://ameliamorsellino.github.io/biblioteche-fantasma/ontology/`
- **resource namespace**: `https://ameliamorsellino.github.io/biblioteche-fantasma/resource/`
- **metadata namespace**: `https://ameliamorsellino.github.io/biblioteche-fantasma/metadata/`

Il precedente namespace di sviluppo
`https://biblioteche-fantasma.invalid/`
era deliberatamente non dereferenziabile e non costituiva una pubblicazione Web.
È stato sostituito dal namespace pubblico prima della pubblicazione del dataset.

Le URI pubbliche mantengono i path e le chiavi deterministiche definite durante lo sviluppo, cambiando soltanto l'autorità Web.

## Pattern deterministici

| Risorsa | Pattern |
|---|---|
| Biblioteca | `/resource/library/{ISIL}` |
| Comune | `/resource/municipality/{ISTAT_CODE}` |
| Stato | `/resource/status/{NORMALIZED_STATUS_SLUG}` |
| Osservazione stato | `/resource/status-observation/{ISIL}/{YYYY-MM-DD}` |
| Osservazione demografica | `/resource/demography/{ISTAT_CODE}/{YEAR}` |
| Sede | `/resource/site/{ISIL}` |
| Indirizzo | `/resource/address/{ISIL}` |
| Geometria sede | `/resource/geometry/site/{ISIL}` |
| Fondo speciale | `/resource/collection/{ISIL}-special-{COLLECTION_INDEX}` |
| Osservazione patrimonio | `/resource/holding/{ISIL}/{MATERIAL_INDEX}` |
| Concetto materiale/tipologia | `/resource/{scheme}/{slug}-{sha1_8}` quando il valore sorgente non possiede un identificatore ufficiale |

## Regole

1. ISIL e codici ISTAT sono stringhe; gli zeri iniziali non vengono rimossi.
2. Nessuna URI locale è ottenuta da fuzzy matching.
3. I nomi testuali non sono usati come chiavi quando esiste un identificatore (`ISIL`, codice ISTAT, indice di riga controllato).
4. Per valori di vocabolario privi di codice ufficiale si usa slug leggibile + hash SHA-1 troncato a 8 caratteri del valore UTF-8 originale; l'hash serve alla stabilità e alla disambiguazione della URI, non come prova d'identità esterna.
5. Non viene creata una risorsa `/library-merger/...`: la sorgente non fornisce una data/evento di fusione e il requisito interrogativo è soddisfatto dalla relazione diretta `bf:mergedInto`. I casi senza target parseabile non ricevono un target inventato.
6. La data nella URI `status-observation` è la data dello snapshot ICCU (`2026-09-08`), non una data di inizio della chiusura o cessazione.
7. I link esterni sono mantenuti in `rdf/links.ttl` e separati dai dati core.
8. Le URI pubbliche vengono generate a partire dalla costante `PUBLIC_BASE` definita in `scripts/project_config.py`, evitando namespace duplicati hard-coded negli script.

## Strategia di pubblicazione Web

La pubblicazione utilizza GitHub Pages come sito Web statico del progetto.

Le URI pubbliche sono costruite sotto:

`https://ameliamorsellino.github.io/biblioteche-fantasma/`

Le pagine HTML delle risorse pubblicate forniscono una rappresentazione leggibile dall'utente e collegamenti alle relative rappresentazioni RDF quando disponibili.

Poiché GitHub Pages è un hosting statico, il deployment non implementa un endpoint SPARQL pubblico né una negoziazione HTTP completa basata sull'header `Accept`. La disponibilità di un endpoint SPARQL pubblico non è necessaria per l'interlinking Linked Data del progetto.

Il file RDF principale `data.ttl`, le cui dimensioni superano i limiti ordinari di un file GitHub, viene distribuito separatamente tramite GitHub Releases. Le distribuzioni più piccole e i metadati possono essere pubblicati direttamente attraverso GitHub Pages o il repository pubblico.

I metadati DCAT utilizzano URL HTTP(S) pubblici per l'accesso e il download delle distribuzioni.

## Interlinking

Le risorse locali sono collegate a risorse esterne mediante relazioni RDF esplicite.

Le biblioteche sono collegate alle rispettive pagine ufficiali ICCU tramite `rdfs:seeAlso`.

I comuni per i quali è disponibile una corrispondenza verificata sono collegati alle risorse Linked ISPRA mediante `owl:sameAs`.

Questi collegamenti sono mantenuti separatamente nel file `rdf/links.ttl`.

## Verifica della pubblicazione

Dopo il deployment devono essere verificati:

- raggiungibilità del sito GitHub Pages;
- raggiungibilità delle URI di esempio;
- disponibilità delle rappresentazioni HTML/RDF pubblicate;
- disponibilità delle distribuzioni indicate nei metadati DCAT;
- validità sintattica RDF;
- conformità SHACL;
- corretto funzionamento delle query SPARQL locali;
- correttezza dei link esterni.
