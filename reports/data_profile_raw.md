# Data profiling

## ICCU master
- Record: **19,611**.
- ISIL unici: **19,611**; mancanti: **0**; duplicati: **0**.
- Comuni distinti: **6,660**.
- Province: **107**.
- Regioni: **20**.
- Coordinate pulite complete: **19,524/19,611**.
- Coppie (0,0) trattate come mancanti: **63**.
- Coordinate mancanti/incomplete: **24**.
- Coordinate fuori bounding box Italia, da revisione: **3**.
- Codice SBN presente: **7,397**.
- Data aggiornamento valida/presente: **16,711**.

## Stati normalizzati
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

`NULL` non è interpretato come biblioteca aperta: è mappato a `NESSUNO_STATO_SPECIALE_REGISTRATO`.

## Dataset ICCU secondari
- Tipologie: 13,715 record, 13,715 biblioteche (69.94% del master).
- Patrimonio: 93,512 record, 13,715 biblioteche (69.94%).
- Fondi speciali: 9,737 record, 2,449 biblioteche (12.49%).
- Contatti: 62,804 record, 13,630 biblioteche (69.50%).

## ISTAT
- POSAS 2019 Comuni: 811.308 righe, 7.954 comuni.
- POSAS 2025 Comuni: 805.392 righe, 7.896 comuni.
- `Età=999`: verificata empiricamente contro la somma delle età 0–100 per tutti i comuni; mismatch = 0 in entrambi gli anni.
