# Parquet non materializzato nell'ambiente di build

I CSV processed canonici sono presenti in `../csv/`. La conversione Parquet non è stata materializzata perché nell'ambiente di esecuzione non erano disponibili `pyarrow`, `fastparquet` o DuckDB e l'installazione di `pyarrow` non è stata possibile senza accesso di rete. Non sono stati creati file `.parquet` fittizi.

Per produrli in un ambiente con `pyarrow`:

```bash
pip install pyarrow
python scripts/export_parquet.py --root .
```
