# Controllo finale - repository Biblioteche Fantasma

## Integrità del checkpoint

Sono stati confrontati via SHA-256 **34 artefatti critici** del checkpoint 2 (processed data, ontologia, RDF, SHACL, SPARQL, link/interlinking) con il manifest originale: **34/34 invariati**, 0 discrepanze. Questo conferma che la Fase 3 non ha rigenerato o modificato ontologia, RDF o interlinking.

## Checklist

- [x] fonti documentate (`metadata/source_manifest.csv`)
- [x] licenze verificate/documentate (`metadata/licenses.md`)
- [ ] RAW inclusi/preservati nel repository finale: **non inclusi nel checkpoint 2**; hash e riferimenti sono documentati
- [x] manifest sorgenti disponibile
- [x] profiling della Fase 1 documentato; non rieseguito sui RAW
- [x] cleaning log finale ricostruito dal checkpoint (`reports/cleaning_log.csv`), esplicitamente non event-level originale
- [x] ISIL validati nel checkpoint: 19.611 completi/unici
- [x] stati normalizzati: 11 categorie
- [x] confluenze parse: 1.412 target validati su 1.502
- [x] join ICCU->ISTAT misurato: 100%
- [x] ISTAT 2019 documentato e integrato
- [x] ISTAT 2025 documentato e integrato
- [x] crosswalk amministrativo presente
- [x] dataset 3-star CSV
- [x] Data Package (`metadata/datapackage.json`)
- [x] DCAT-AP_IT locale (`metadata/dcat-ap_it.ttl`) con limiti di pubblicazione documentati
- [x] provenance
- [x] competency questions
- [x] Cultural-ON riutilizzato
- [x] ontologia invariata e presente
- [x] URI policy
- [x] RDF presente e invariato
- [x] RDF validation PASS dal checkpoint canonico; hash invariati in Fase 3
- [x] SHACL eseguito nel sottoinsieme Core locale: 82.519 focus node, 0 violazioni
- [x] interlinking e coverage preservati dal checkpoint
- [x] 5-star assessment
- [x] GraphDB import-ready
- [ ] GraphDB eseguito: **no**
- [x] 11 query SPARQL sintatticamente valide nel checkpoint
- [ ] esecuzione completa delle 11 query SPARQL: **no** (1 eseguita; una seconda non completata nel budget RDFLib)
- [x] analisi quantitativa finale: 24 tabelle in `reports/analysis_tables/`
- [x] visualizzazioni: 8 PNG + mappa HTML
- [x] interpretazione RQ1-RQ8
- [x] data story
- [x] limiti
- [x] README
- [x] bibliography
- [x] relazione LaTeX
- [x] PDF compilato: 20 pagine
- [x] repository riproducibile per la Fase 3
- [ ] Parquet materializzati: **no**, motore Parquet non disponibile offline; script di export fornito
- [ ] JSON-LD materializzato: **no**, non presente nel checkpoint e non rigenerato

## Controllo PDF

`report/relazione.tex` è stato compilato con `latexmk`/`biber` senza errori. Il PDF è stato renderizzato integralmente in 20 pagine per verifica visiva; non sono emersi clipping o overlap evidenti.

## Risultati chiave

- 19.611 record ICCU; 18.956 biblioteche nel denominatore analitico.
- 2.497 biblioteche problematiche = 13,17%.
- RQ4: N=6.659; Pearson r=-0,1064; Spearman rho=-0,0670.
- RQ5: 627 biblioteche problematiche con patrimonio documentato; 0 con record di fondi speciali nel dataset secondario.
- RQ6: 100% interlinking biblioteche; 99,9620% comuni.
- RQ7: 1.412 archi, 1.821 nodi, 410 componenti, un self-loop.
- Knowledge graph: 1.644.602 triple esplicite.

## Operazioni manuali residue

1. Fornire/ricollocare gli archivi RAW originali per una riproduzione end-to-end della Fase 1.
2. Installare `pyarrow` ed eseguire `python scripts/export_parquet.py --root .` per i Parquet.
3. Pubblicare le URI su un dominio HTTPS controllato e sostituire `.invalid`/URL `file:`.
4. Eseguire import e query in GraphDB.
5. Eseguire una validazione SHACL completa con pySHACL o GraphDB.
6. Se richiesto, materializzare JSON-LD a partire dal grafo canonico, documentando che è una nuova distribuzione.
