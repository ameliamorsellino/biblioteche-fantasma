# Esportazione Parquet opzionale

I dataset processati canonici sono disponibili in formato CSV direttamente in `data/processed/`.

La serializzazione Parquet è opzionale e non è necessaria per eseguire la pipeline principale, le analisi, la generazione RDF o le visualizzazioni.

Per produrre anche le versioni Parquet è necessario installare `pyarrow`:

```bash
pip install pyarrow
python scripts/export_parquet.py --root .