# Data Quality

## Completeness
- ISIL: 100%.
- Codice ISTAT comunale nel master ICCU: 100%.
- Coordinate pulite complete: 99.56%.
- Copertura tipologie/patrimonio: 69.94%.
- Copertura contatti: 69.50%.
- Copertura fondi speciali: 12.49%.

## Uniqueness
- ISIL: 19.611 unici su 19.611.
- Comuni 2025 nel dataset demografico: 7.896 codici unici su 7.896 righe.

## Validity
- Pattern ISIL: 100%.
- Coordinate `(0,0)` (63) non sono accettate come coordinate pulite.
- Tre coordinate fuori bounding box Italia restano marcate per revisione; due sono compatibili con sedi a Buenos Aires/Atene, una (`IT-ME0024`) è sospetta.

## Consistency
- Stato `NULL` separato da qualsiasi affermazione di apertura.
- Relazioni 1:N non appiattite.
- `Età=999` POSAS verificata: 0 mismatch su tutti i comuni 2019 e 2025 rispetto alla somma 0–100.
- Trapani e Misiliscemi sono marcati non comparabili per la variazione territoriale 2021.

## Joinability
- ICCU→ISTAT 2025 via codice comune: 19.611/19.611 = 100%.
- Le coperture ICCU secondarie sono riportate in `reports/join_quality.csv`.
