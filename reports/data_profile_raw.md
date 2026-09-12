# Data profiling

## ICCU master
- Records: **19,611**.
- Unique ISILs: **19,611**; missing: **0**; duplicates: **0**.
- Distinct municipalities: **6,660**.
- Provinces: **107**.
- Regions: **20**.
- Complete cleaned coordinates: **19,524/19,611**.
- (0,0) pairs treated as missing: **63**.
- Missing/incomplete coordinates: **24**.
- Coordinates outside the Italy bounding box, to be reviewed: **3**.
- SBN code present: **7,397**.
- Valid/present update date: **16,711**.

## Normalized statuses
- `NESSUNO_STATO_SPECIALE_REGISTRATO`: 13,200
- `BIBLIOTECA_NON_PIU_ESISTENTE`: 1,827
- `BIBLIOTECA_NON_CENSITA`: 1,723
- `BIBLIOTECA_CONFLUITA`: 1,502
- `ALTRO_ISTITUTO_COLLEGATO_ICCU`: 655
- `TEMPORANEAMENTE_CHIUSA`: 619
- `BIBLIOTECA_IN_VIA_DI_ALLESTIMENTO`: 34
- `DEPOSITO_SENZA_PUNTO_DI_SERVIZIO`: 33
- `SERVIZI_SOSPESI_CAUSA_SISMA`: 12
- `INAGIBILE`: 4
- `RIAPERTURA_AGIBILITA_PARZIALE`: 2

`NULL` is not interpreted as an open library: it is mapped to `NESSUNO_STATO_SPECIALE_REGISTRATO`.

## Secondary ICCU datasets
- Types: 13,715 records, 13,715 libraries (69.94% of the master).
- Holdings: 93,512 records, 13,715 libraries (69.94%).
- Special collections: 9,737 records, 2,449 libraries (12.49%).
- Contacts: 62,804 records, 13,630 libraries (69.50%).

## ISTAT
- POSAS 2019 Municipalities: 811,308 rows, 7,954 municipalities.
- POSAS 2025 Municipalities: 805,392 rows, 7,896 municipalities.
- `Età=999`: empirically verified against the sum of ages 0–100 for all municipalities; mismatch = 0 in both years.

