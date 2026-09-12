# Data Quality

## Completeness
- ISIL: 100%.
- Municipal ISTAT code in the ICCU master: 100%.
- Complete cleaned coordinates: 99.56%.
- Type/holdings coverage: 69.94%.
- Contact coverage: 69.50%.
- Special collections coverage: 12.49%.

## Uniqueness
- ISIL: 19,611 unique out of 19,611.
- 2025 municipalities in the demographic dataset: 7,896 unique codes across 7,896 rows.

## Validity
- ISIL pattern: 100%.
- `(0,0)` coordinates (63) are not accepted as cleaned coordinates.
- Three coordinates outside the Italy bounding box remain flagged for review; two are compatible with locations in Buenos Aires/Athens, one (`IT-ME0024`) is suspicious.

## Consistency
- `NULL` status kept separate from any claim of being open.
- 1:N relationships not flattened.
- POSAS `Età=999` verified: 0 mismatches across all 2019 and 2025 municipalities compared with the sum of ages 0–100.
- Trapani and Misiliscemi are marked as non-comparable because of the 2021 territorial change.

## Joinability
- ICCU→ISTAT 2025 via municipality code: 19,611/19,611 = 100%.
- Secondary ICCU coverage is reported in `reports/join_quality.csv`.
