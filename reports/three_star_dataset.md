# Structured dataset in an open format

The analytical outputs are distributed in **UTF-8 CSV**, a structured,
machine-readable and non-proprietary format.

The original RAW files are stored separately in `data/raw/` and are not
modified by the pipeline.

The implemented chain is:

RAW → cleaning → harmonization → integration → CSV processed

The canonical processed datasets are available directly in
`data/processed/`.

From a technical perspective, the datasets satisfy the structure
and open-format requirements associated with the 3-star level. The complete
classification under the 5-star model, however, also requires publication
on the Web, which is assessed separately in the project.

Parquet export is optional and is not required for the main
pipeline.

