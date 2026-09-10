# Dataset strutturato in formato aperto

Gli output analitici sono distribuiti in **CSV UTF-8**, formato strutturato,
machine-readable e non proprietario.

I RAW originali sono conservati separatamente in `data/raw/` e non vengono
modificati dalla pipeline.

La catena implementata è:

RAW → cleaning → harmonization → integration → CSV processed

I dataset processati canonici sono disponibili direttamente in
`data/processed/`.

Dal punto di vista tecnico i dataset soddisfano i requisiti di struttura
e formato aperto associati al livello 3-star. La classificazione completa
del modello 5-star richiede tuttavia anche la pubblicazione sul Web, che
viene valutata separatamente nel progetto.

L'esportazione Parquet è opzionale e non è necessaria per la pipeline
principale.
