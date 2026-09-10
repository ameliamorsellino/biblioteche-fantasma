# URI Policy - Biblioteche Fantasma

## Stato della policy

Il progetto non dispone, in questa fase, di un dominio Web controllato. Per non simulare pubblicazione o dereferenziazione, le URI di sviluppo usano il TLD riservato `.invalid`:

- **ontology namespace (sviluppo)**: `https://biblioteche-fantasma.invalid/ontology/`
- **resource namespace (sviluppo)**: `https://biblioteche-fantasma.invalid/resource/`

Queste URI sono deliberatamente **provvisorie e non dereferenziabili**. Non sono presentate come URI finali 4/5-star. In pubblicazione va sostituita l'autorità con un dominio realmente controllato, mantenendo i path e le chiavi deterministiche; prima della pubblicazione va congelata una migration map tra namespace di sviluppo e namespace definitivo.

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
4. Per valori di vocabolario privi di codice ufficiale si usa slug leggibile + hash SHA-1 troncato a 8 caratteri del valore UTF-8 originale; l'hash serve solo alla stabilità/disambiguazione della URI, non come prova d'identità esterna.
5. Non viene creata una risorsa `/library-merger/...`: la sorgente non fornisce una data/evento di fusione e il requisito interrogativo è soddisfatto dalla relazione diretta `bf:mergedInto`. I 90 casi senza target parseabile non ricevono un target inventato.
6. La data nella URI `status-observation` è la data dello snapshot ICCU (`2026-09-08`), non una data di inizio della chiusura/cessazione.
7. Link esterni sono mantenuti in `rdf/links.ttl` e separati dai dati core.

## Strategia di pubblicazione

Quando sarà disponibile un dominio reale:

- assegnare namespace HTTP(S) permanenti e dereferenziabili;
- pubblicare content negotiation (HTML/RDF) per le risorse;
- conservare una tabella di redirect/migrazione dalle URI di sviluppo se queste sono state usate esternamente;
- aggiornare `dcat:downloadURL`, `dcat:accessURL` e metadati di distribuzione;
- rieseguire RDF validation, SHACL e test SPARQL sul deployment effettivo.
