# URI Policy - Biblioteche Fantasma

## Policy status

The project uses a public HTTP(S) namespace associated with Web publication through GitHub Pages:

* **base URI**: `https://ameliamorsellino.github.io/biblioteche-fantasma/`
* **ontology namespace**: `https://ameliamorsellino.github.io/biblioteche-fantasma/ontology/`
* **resource namespace**: `https://ameliamorsellino.github.io/biblioteche-fantasma/resource/`
* **metadata namespace**: `https://ameliamorsellino.github.io/biblioteche-fantasma/metadata/`

The previous development namespace
`https://biblioteche-fantasma.invalid/`
was deliberately non-dereferenceable and did not constitute a Web publication.
It was replaced by the public namespace before publication of the dataset.

The public URIs retain the paths and deterministic keys defined during development, changing only the Web authority.

## Deterministic patterns

| Resource                | Pattern                                                                                         |
| ----------------------- | ----------------------------------------------------------------------------------------------- |
| Library                 | `/resource/library/{ISIL}`                                                                      |
| Municipality            | `/resource/municipality/{ISTAT_CODE}`                                                           |
| Status                  | `/resource/status/{NORMALIZED_STATUS_SLUG}`                                                     |
| Status observation      | `/resource/status-observation/{ISIL}/{YYYY-MM-DD}`                                              |
| Demographic observation | `/resource/demography/{ISTAT_CODE}/{YEAR}`                                                      |
| Site                    | `/resource/site/{ISIL}`                                                                         |
| Address                 | `/resource/address/{ISIL}`                                                                      |
| Site geometry           | `/resource/geometry/site/{ISIL}`                                                                |
| Special collection      | `/resource/collection/{ISIL}-special-{COLLECTION_INDEX}`                                        |
| Holdings observation    | `/resource/holding/{ISIL}/{MATERIAL_INDEX}`                                                     |
| Material/type concept   | `/resource/{scheme}/{slug}-{sha1_8}` when the source value does not have an official identifier |

## Rules

1. ISIL and ISTAT codes are strings; leading zeros are not removed.
2. No local URI is derived from fuzzy matching.
3. Textual names are not used as keys when an identifier exists (`ISIL`, ISTAT code, controlled row index).
4. For vocabulary values without an official code, a readable slug + an 8-character truncated SHA-1 hash of the original UTF-8 value is used; the hash serves URI stability and disambiguation, not as proof of external identity.
5. No `/library-merger/...` resource is created: the source does not provide a merger date/event and the query requirement is satisfied by the direct `bf:mergedInto` relation. Cases without a parseable target are not assigned an invented target.
6. The date in the `status-observation` URI is the ICCU snapshot date (`2026-09-08`), not a start date of closure or cessation.
7. External links are maintained in `rdf/links.ttl` and kept separate from the core data.
8. Public URIs are generated from the `PUBLIC_BASE` constant defined in `scripts/project_config.py`, avoiding duplicated hard-coded namespaces in the scripts.

## Web publication strategy

Publication uses GitHub Pages as the project's static Web site.

Public URIs are constructed under:

`https://ameliamorsellino.github.io/biblioteche-fantasma/`

The HTML pages of published resources provide a human-readable representation and links to the corresponding RDF representations when available.

Because GitHub Pages is static hosting, the deployment does not implement a public SPARQL endpoint or full HTTP content negotiation based on the `Accept` header. The availability of a public SPARQL endpoint is not necessary for the project's Linked Data interlinking.

The main RDF file `data.ttl`, whose size exceeds the ordinary limits of a GitHub file, is distributed separately through GitHub Releases. Smaller distributions and metadata can be published directly through GitHub Pages or the public repository.

The DCAT metadata use public HTTP(S) URLs for access to and download of the distributions.

## Interlinking

Local resources are linked to external resources through explicit RDF relations.

Libraries are linked to their respective official ICCU pages through `rdfs:seeAlso`.

Municipalities for which a verified match is available are linked to Linked ISPRA resources through `owl:sameAs`.

These links are maintained separately in the `rdf/links.ttl` file.

## Publication verification

After deployment, the following must be verified:

* reachability of the GitHub Pages site;
* reachability of example URIs;
* availability of the published HTML/RDF representations;
* availability of the distributions indicated in the DCAT metadata;
* RDF syntactic validity;
* SHACL compliance;
* correct functioning of local SPARQL queries;
* correctness of external links.
