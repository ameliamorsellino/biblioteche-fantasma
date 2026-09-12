# Data verification - sources

## ICCU
Institutional publisher: ICCU. Official Open Data page: https://anagrafe.iccu.sbn.it/it/open-data/. The page states daily updates, CSV/XML/JSON formats, the `opendata.zip` archive, ISIL as the primary key for cross-referencing datasets, and documents the values of `stato-registrazione`. Data license: CC0. Local snapshot: `2026-09-08T14:11:15`.

## ISTAT POSAS
Publisher: Istat. Series: resident population by age, sex and marital status as of January 1. Source: https://demo.istat.it/app/?i=POS. Years used: 2019 and 2025. Istat license: CC BY 4.0 (https://www.istat.it/dati/open-data/). Municipal files are read while preserving strings such as `None`.

## Cultural-ON
The local OWL file `data/external/cultural-ON.owl` is stored in the repository as a semantic input. The declared version is 2.0 (March 30, 2016), licensed under CC BY 3.0 IT. Official documentation: https://dati.beniculturali.it/cultural-ON/ITA.html. The ontology is reused in the semantic modeling of the project.

## Limitations
- XSD 1.6 is not present as a local file in the repository; the four images of the 1.6 release notes provided by the user and the reference to the official format page are present.
- Two municipalities (Trapani, Misiliscemi) do not allow a 2019 comparison to be reconstructed from municipal POSAS data alone.
