# BIBLIOTECHE FANTASMA

**Analysis, integration and semantic modelling of Italian libraries that are not fully operational**

## Abstract

The project develops a complete **Open Data Management** pipeline based on real data from the **Anagrafe delle Biblioteche Italiane (ICCU)** and **ISTAT POSAS 2019 and 2025 resident population** data.

The pipeline includes:

**source selection and verification → RAW preservation → profiling and quality control → cleaning → territorial harmonization → integration and enrichment → structured datasets → metadata → ontology modelling → RDF → SHACL validation → interlinking → SPARQL → statistical analysis → visualization.**

“Biblioteche Fantasma” is a narrative label of the project, **not an official ICCU category**. The absence of a special status in the registry is not interpreted as certification of full operational status.

The project also adopts a conservative approach to anomaly management: missing values are not automatically converted to zero, anomalies are not corrected without documentary evidence, and administrative changes between ISTAT years are handled explicitly.

---

## Research Questions

* **RQ1** - Where are libraries characterized by statuses of non-full operation distributed?

* **RQ2** - Which registration statuses are most frequent and how do they vary territorially?

* **RQ3** - Which functional/administrative types are associated with the different statuses?

* **RQ4** - Is there an association between municipal demographic change from 2019 to 2025 and the share of library records with an ICCU status included in the problematic scope?

* **RQ5** - Which holdings and special collections are documented at problematic libraries?

* **RQ6** - What coverage is achieved by the generation of links to external resources?

* **RQ7** - What structure does the merger network exhibit?

* **RQ8** - What descriptive relationship emerges between the share of the population aged 65+ and problematic libraries?

---

## Open Data sources

The main sources are:

* **ICCU - Anagrafe delle Biblioteche Italiane**, snapshot dated 2026-09-08;

* **ISTAT POSAS 2019** - resident population by sex, age and marital status;

* **ISTAT POSAS 2025** - resident population by sex, age and marital status;

* **Cultural-ON 2.0** - ontology used for semantic reuse in the cultural domain.

The original RAW archives are stored separately in:

```text
data/raw/iccu/opendata.zip
data/raw/istat/POSAS_2019_it_Tutti_i_file.zip
data/raw/istat/POSAS_2025_it_Tutti_i_file.zip
```

The pipeline **never modifies the RAW files**.

`metadata/source_manifest.csv` documents the following for each source:

* publisher;

* URL;

* role in the project;

* acquisition date;

* license;

* local path;

* SHA-256.

This makes it possible to verify the identity of the sources used and to reconstruct the derived artifacts from the original files included in the repository.

---

## Licenses

Reuse conditions are documented in `metadata/licenses.md`.

* **ICCU Open Data:** CC0 1.0.

* **ISTAT POSAS 2019/2025:** CC BY 4.0.

* **Cultural-ON 2.0:** CC BY 3.0 IT.

* **Derived tabular dataset and original project documentation:** CC BY 4.0, unless otherwise stated.

The project license is available in `LICENSE`.

The project license does not replace or modify the conditions applicable to third-party materials included or referenced.

---

## Verification, cleaning and integration

Data preparation includes checks on structure, types, missing values, identifiers, coordinates and territorial consistency.

The main methodological decisions include:

* separate preservation of RAW files;

* normalization of ISIL and ISTAT identifiers;

* distinction between a missing value and the numeric value zero;

* `(0, 0)` coordinates treated as missing;

* exclusion from the analytical scope of ICCU institutions classified as other types of institution when they are not relevant to the operational definition of a library;

* no fuzzy matching for municipalities;

* explicit harmonization of administrative changes between the 2019 and 2025 ISTAT geographies;

* preservation of the 1:N structure for holdings, special collections and other multi-valued information;

* modelling the ICCU status as an observation referring to the snapshot, rather than as an atemporal property;

* cautious use of `owl:sameAs` and `rdfs:seeAlso` according to the actual semantic equivalence of the resources.

The main design choices and their trade-offs are documented in:

```text
reports/decisions_log.md
reports/data_quality.md
reports/limitations.md
```

---

## Processed datasets

The pipeline produces **10 canonical tabular datasets** in UTF-8 CSV format directly in:

```text
data/processed/
```

The CSV files are structured, machine-readable and in a non-proprietary format.

Parquet format is optional and can be produced using:

```bash
pip install pyarrow
python scripts/export_parquet.py --root .
```

Any Parquet files are saved in:

```text
data/processed/parquet/
```

Parquet export is not required for the main pipeline, RDF generation, SPARQL, analyses or visualizations.

---

## Metadata

The repository includes both tabular and RDF metadata.

### Frictionless Data Package

```text
metadata/datapackage.json
```

describes the processed resources, their paths and the field schema.

### DCAT

```text
metadata/dcat.ttl
```

provides an RDF/DCAT description of the dataset and its main distributions.

The metadata use public HTTP(S) URIs and provide Web access and download
URLs for the processed datasets.

The project does not claim full formal compliance with DCAT-AP_IT,
because the metadata have not been formally validated against the
applicable DCAT-AP_IT profile.

Further details are available in:

```text
metadata/dcat_validation_notes.md
metadata/provenance.ttl
metadata/uri_policy.md
```

---

## Ontology and semantic modelling

The project ontology is available in:

```text
ontology/ontology.ttl
ontology/ontology.owl
```

The design follows the principle:

**reuse → extend → create**

and reuses, where semantically appropriate:

* Cultural-ON;

* SKOS;

* PROV-O;

* DCAT / DCTERMS;

* GeoSPARQL;

* LOCN;

* Schema.org.

ICCU statuses are modelled as `skos:Concept`.

Observations about library status are modelled separately from the libraries themselves, in order to make the temporal nature of the snapshot explicit.

The competency questions and reuse choices are documented in:

```text
ontology/competency_questions.md
ontology/vocabulary_reuse.csv
```

---

## Web publication and URI policy

The project uses a public HTTPS namespace:

```text
https://ameliamorsellino.github.io/biblioteche-fantasma/
```

Ontology namespace:

```text
https://ameliamorsellino.github.io/biblioteche-fantasma/ontology/
```

Resource namespace:

```text
https://ameliamorsellino.github.io/biblioteche-fantasma/resource/
```

URIs are constructed deterministically using, where available, official identifiers such as:

* ISIL for libraries;

* ISTAT code for municipalities;

* derived and documented identifiers for observations and other entities.

The Web publication is generated reproducibly by:

```text
scripts/build_web_publication.py
```

and automatically deployed through GitHub Pages and GitHub Actions.

The public site is available at:

```text
https://ameliamorsellino.github.io/biblioteche-fantasma/
```

Public HTML pages are generated for the main entities:

* **19,611 libraries**;

* **7,896 municipalities**;

* **27,507 core entities overall**.

Examples of published URIs:

```text
https://ameliamorsellino.github.io/biblioteche-fantasma/resource/library/IT-RM0267/
https://ameliamorsellino.github.io/biblioteche-fantasma/resource/municipality/058091/
```

The ontology, metadata and RDF interlinking distributions are also available on the Web.

The complete `data.ttl` knowledge graph, which is too large for the normal Git repository, is distributed as an asset of GitHub release `v1.0.0`:

```text
https://github.com/ameliamorsellino/biblioteche-fantasma/releases/latest/download/data.ttl
```

Hosting through GitHub Pages is static. The project therefore does not implement a Linked Data server with full HTTP content negotiation or `303` redirects based on the `Accept` header. HTML representations of the core entities and RDF distributions are nevertheless published through explicit and stable Web URLs.

---

## RDF knowledge graph

RDF generation is implemented in:

```text
scripts/generate_rdf.py
scripts/generate_links.py
```

The main outputs are:

```text
rdf/data.ttl
rdf/links.ttl
rdf/metadata.ttl
```

The knowledge graph contains:

* `rdf/data.ttl`: **1,628,669 triples**;

* `rdf/links.ttl`: **27,504 triples**;

* `rdf/metadata.ttl`: **39 triples**;

* `ontology/ontology.ttl`: **195 triples**.

Explicit total:

**1,656,407 triples**

Structural validation checks, among other things:

* RDF parsing;

* malformed URIs;

* lexical forms of datatypes;

* undeclared local classes and properties;

* dangling local resources;

* link subjects not present in the graph;

* serialized duplicates.

The report is available in:

```text
reports/rdf_validation.md
```

---

## SHACL

The shapes are defined in:

```text
shacl/shapes.ttl
```

Validation is performed with **pySHACL 0.40.1** on the entire knowledge graph.

The latest validated run produced:

```text
Conforms: YES

Validation results: 0

Violations: 0

Warnings: 0

Infos: 0
```

The reports are saved in:

```text
reports/shacl_validation.md
reports/shacl_validation.txt
reports/shacl_validation.ttl
```

Validation can be rerun with:

```bash
python scripts/validate_shacl.py --root .
```

---

## Interlinking

The project generates links to external resources using official identifiers and without fuzzy matching.

### Libraries → ICCU

For the **19,611 ICCU libraries**, a link to the Anagrafe delle Biblioteche Italiane is generated using the ISIL.

Relationship:

```text
rdfs:seeAlso
```

Generation coverage:

```text
19,611 / 19,611 = 100%
```

`rdfs:seeAlso` is used because the ICCU target is a Web resource for consultation and is not assumed to be an RDF individual semantically identical to the local resource.

### Municipalities → Linked ISPRA

For municipalities, Linked ISPRA URIs are generated from the six-digit ISTAT code.

Relationship:

```text
owl:sameAs
```

Generation coverage:

```text
7,893 / 7,896 = 99,9620%
```

The three cases without a link are intentionally left unlinked because of administrative changes that occurred in 2026 relative to the 2025 analytical geography.

The reported percentages describe the **coverage of link generation according to the documented URI policy**.

The external URI pattern was verified on real resources, but the offline pipeline does not individually dereference all Linked ISPRA targets; coverage must therefore not be interpreted as an HTTP response rate verified for every individual URI.

The machine-readable report is:

```text
reports/interlinking_report.csv
```

---

## SPARQL

The competency questions are translated into **11 SPARQL queries** available in:

```text
sparql/
```

Local execution uses **PyOxigraph** as an embedded and persistent RDF store.

The following are not required:

* GraphDB;

* a local SPARQL server;

* an external SPARQL endpoint.

The store is created in:

```text
.cache/oxigraph/
```

and is a regenerable local artifact, so it must not be versioned or included in the final distribution.

To run all queries:

```bash
python scripts/run_sparql.py --root .
```

To explicitly rebuild the store:

```bash
python scripts/run_sparql.py --root . --rebuild-store
```

To run a single query:

```bash
python scripts/run_sparql.py \
  --root . \
  --query 01_status_distribution
```

To display the list:

```bash
python scripts/run_sparql.py --root . --list
```

Results are saved in:

```text
sparql/results/
```

and the overall report in:

```text
reports/sparql_execution_report.md
reports/sparql_execution_report.json
```

The **11 queries are executable** on the local knowledge graph. A query may legitimately return zero rows: for example, the query concerning inaccessible libraries with documented special collections returns an empty result set in the current snapshot without this constituting an execution error.

---

## Quantitative analysis

Statistical analyses are performed mainly with:

* Pandas;

* NumPy;

* SciPy;

* NetworkX.

SPARQL is used to query the knowledge graph and answer the competency questions; Pandas/SciPy are instead used for tabular and statistical processing, while NetworkX is used for the merger network.

This separation avoids using SPARQL for operations for which a tabular representation is more readable and efficient.

Execution:

```bash
python scripts/run_analysis.py --root .
```

Outputs are saved mainly in:

```text
reports/analysis_tables/
reports/analysis_summary.json
reports/rq_results.json
```

---

## Main results

The ICCU master contains **19,611 records**.

Excluding **655 records** classified as other institutions linked to ICCU, the denominator used for the library scope is:

**18,956 libraries**

The libraries included in the main analytical scope of non-full-operation conditions are:

**2,497**, equal to **13,17%** of the libraries considered and **12,73%** of the overall registry records.

The most frequent statuses in the snapshot include:

* no special status registered: 13,200;

* library no longer existing: 1,827;

* library not surveyed: 1,723;

* merged library: 1,502;

* temporarily closed: 619.

At regional level, the problematic share is particularly high in some regions, but each comparison is interpreted together with its corresponding denominator.

For RQ4, the comparison across **6,659 comparable municipalities with at least one library** shows a weak relationship between demographic change from 2019 to 2025 and the share of library records with an ICCU status included in the problematic scope:

```text
Pearson r = -0,106

Spearman ρ = -0,067
```

The result is **observational** and does not allow causal inference.

For RQ5, **627 of the 2,497 problematic libraries** have at least one documented holdings row, for a total of **2,828 rows**. The absence of a library from the special collections dataset is interpreted as an absence of documentation in the dataset, not as evidence of the actual absence of collections.

The merger network includes:

```text
1,412 validated edges

1,821 nodes

410 weakly connected components

40 nodes in the largest component
```

The only detected cycle is the already documented self-loop:

```text
IT-SS0267 -> IT-SS0267
```

For RQ8, the share of the population aged over 65 shows a positive but weak association with the share of library records with an ICCU status included in the problematic scope. The analysis is documented in:

```text
reports/analysis_tables/age65_problematic_correlation.csv
visualizations/age65_scatter.png
```

---

## Visualizations

Visualizations are generated by:

```bash
python scripts/run_visualizations.py --root .
```

The outputs are available in:

```text
visualizations/
```

The main ones include:

* `library_map.html` - clustered interactive map;

* `map_static.png` - geographic distribution of problematic libraries;

* `status_by_region.png` - regional shares;

* `status_distribution.png` - national distribution of statuses;

* `demography_scatter.png` - demographic change vs problematic share;

* `special_collections.png` - documentation coverage of holdings and special collections;

* `problematic_holdings.png` - materials documented at problematic libraries;

* `mergers_network.png` - largest component of the merger network;

* `age65_scatter.png` - 65+ share vs share of library records with an ICCU status included in the problematic scope.

The visualizations are designed to answer the Research Questions and not as an exploratory dashboard without an analytical question.

---

## Assessment against the 5-star Open Data model

The Web version of the project satisfies all five levels of the 5-star Open Data model.

1. **1★ — open license and publication on the Web**

   The derived dataset is documented under a CC BY 4.0 license and is published on the Web.

2. **2★ — structured data**

   The processed datasets are available in structured and machine-readable formats.

3. **3★ — open and non-proprietary formats**

   The project uses CSV and RDF/Turtle/N-Triples.

4. **4★ — Web URIs to identify resources**

   The knowledge graph uses HTTPS URIs under the public GitHub Pages namespace. Libraries and municipalities have automatically generated Web pages.

5. **5★ — links to external data**

   Libraries are linked to the ICCU Anagrafe through `rdfs:seeAlso`; compatible municipalities are linked to Linked ISPRA through `owl:sameAs`.

The operational publication is available at:

```text
https://ameliamorsellino.github.io/biblioteche-fantasma/
```

The complete knowledge graph is distributed through a GitHub Release:

```text
https://github.com/ameliamorsellino/biblioteche-fantasma/releases/latest/download/data.ttl
```

SPARQL queries are instead executed locally with PyOxigraph. A public SPARQL endpoint may be useful in a more advanced Linked Data infrastructure, but it is not a necessary requirement of the 5-star model.

Static publication through GitHub Pages does not provide full HTTP content negotiation and does not generate a dedicated HTML page for every internal graph resource, such as observations, addresses, geometries or holdings. These resources nevertheless remain identified through HTTPS URIs and described in the RDF knowledge graph.

The complete assessment is documented in:

```text
reports/five_star_assessment.md
```

---

## Repository structure

```text
biblioteche-fantasma/

├── README.md

├── LICENSE

├── requirements.txt

├── .gitignore

├── SPARQL.md

│

├── data/

│   ├── raw/

│   │   ├── iccu/

│   │   │   └── opendata.zip

│   │   └── istat/

│   │       ├── POSAS_2019_it_Tutti_i_file.zip

│   │       └── POSAS_2025_it_Tutti_i_file.zip

│   │

│   ├── external/

│   │   ├── cultural-ON.owl

│   │   ├── library_links.csv

│   │   └── municipality_links.csv

│   │

│   └── processed/

│       ├── *.csv

│       └── parquet/

│

├── metadata/

│   ├── source_manifest.csv

│   ├── licenses.md

│   ├── datapackage.json

│   ├── dcat.ttl

│   ├── dcat_validation_notes.md

│   ├── provenance.ttl

│   └── uri_policy.md

│

├── ontology/

│   ├── ontology.ttl

│   ├── ontology.owl

│   ├── competency_questions.md

│   └── vocabulary_reuse.csv

│

├── shacl/

│   └── shapes.ttl

│

├── rdf/

│   ├── data.ttl  # generated locally; distributed via GitHub Release

│   ├── links.ttl

│   └── metadata.ttl

│

├── sparql/

│   ├── *.rq

│   └── results/

│

├── scripts/

│   ├── build_processed_data.py

│   ├── build_metadata.py

│   ├── validate_outputs.py

│   ├── generate_rdf.py

│   ├── generate_links.py

│   ├── validate_rdf.py

│   ├── validate_shacl.py

│   ├── run_sparql.py

│   ├── run_analysis.py

│   ├── run_visualizations.py

│   ├── build_web_publication.py

│   ├── export_parquet.py

│   └── rebuild_all.py

│

├── notebooks/

│   ├── 01_*.ipynb

│   ├── 02_*.ipynb

│   ├── 03_*.ipynb

│   ├── 04_*.ipynb

│   ├── 05_*.ipynb

│   ├── 06_*.ipynb

│   ├── 07_*.ipynb

│   └── 08_*.ipynb

│

├── reports/

│   ├── analysis_tables/

│   ├── analysis.md

│   ├── data_quality.md

│   ├── decisions_log.md

│   ├── five_star_assessment.md

│   ├── interlinking_report.csv

│   ├── limitations.md

│   ├── rdf_validation.md

│   ├── shacl_validation.md

│   └── sparql_execution_report.md

│

├── visualizations/

│   ├── *.png

│   └── library_map.html

│

└── report/

    ├── relazione.tex

    ├── bibliography.bib

    └── relazione.pdf
```

Regenerable local artifacts such as `.venv/`, `.cache/`, `__pycache__/` and temporary LaTeX files are not part of the final distribution.

`rdf/data.ttl` is generated by the reproducible pipeline but is not tracked
in Git because of its size. The complete file is distributed as an asset
of the GitHub release and can also be regenerated locally from the
processed datasets.
---

## Setup

The project was executed in the current development environment with **Python 3.14**.

Create a virtual environment:

```bash
python -m venv .venv
```

On Linux/macOS:

```bash
source .venv/bin/activate
```

On Windows, activation depends on the shell being used.

Then install the dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The main dependencies include:

* pandas;

* numpy;

* scipy;

* networkx;

* matplotlib;

* folium;

* RDFLib;

* PyOxigraph;

* pySHACL;

* JupyterLab.

`pyarrow` is optional and is used exclusively for Parquet export.

---

## Complete reproduction from RAW files

The recommended way to rebuild the project is:

```bash
python scripts/rebuild_all.py
```

The script executes, in order:

```text
RAW

 ↓

build_processed_data.py

 ↓

build_metadata.py

 ↓

validate_outputs.py

 ↓

generate_rdf.py

 ↓

generate_links.py

 ↓

validate_rdf.py

 ↓

run_sparql.py --rebuild-store

 ↓

validate_shacl.py

 ↓

run_analysis.py

 ↓

run_visualizations.py
```

The RAW archives are not modified.

---

## Manual reproduction of the pipeline

The same steps can be executed individually.

### 1. Processed datasets

```bash
python scripts/build_processed_data.py \
  --iccu data/raw/iccu/opendata.zip \
  --posas2019 data/raw/istat/POSAS_2019_it_Tutti_i_file.zip \
  --posas2025 data/raw/istat/POSAS_2025_it_Tutti_i_file.zip \
  --out-root .
```

### 2. Metadata and quality reports

```bash
python scripts/build_metadata.py \
  --root . \
  --iccu data/raw/iccu/opendata.zip \
  --posas2019 data/raw/istat/POSAS_2019_it_Tutti_i_file.zip \
  --posas2025 data/raw/istat/POSAS_2025_it_Tutti_i_file.zip \
  --cultural-on data/external/cultural-ON.owl
```

Any ICCU release notes can be added through repeated options:

```text
--release-note FILE
```

### 3. Tabular validation and metadata validation

```bash
python scripts/validate_outputs.py --root .
```

### 4. RDF generation

```bash
python scripts/generate_rdf.py --root .
```

### 5. Interlinking

```bash
python scripts/generate_links.py
```

### 6. RDF validation

```bash
python scripts/validate_rdf.py --root .
```

### 7. SPARQL

```bash
python scripts/run_sparql.py --root . --rebuild-store
```

### 8. SHACL

```bash
python scripts/validate_shacl.py --root .
```

### 9. Analysis

```bash
python scripts/run_analysis.py --root .
```

### 10. Visualizations

```bash
python scripts/run_visualizations.py --root .
```

---

## Analysis and validation of already generated artifacts

If it is not necessary to rebuild the datasets from the RAW files, the existing artifacts can be checked separately.

Tabular validation:

```bash
python scripts/validate_outputs.py --root .
```

RDF validation:

```bash
python scripts/validate_rdf.py --root .
```

SHACL validation:

```bash
python scripts/validate_shacl.py --root .
```

SPARQL:

```bash
python scripts/run_sparql.py --root .
```

Analysis:

```bash
python scripts/run_analysis.py --root .
```

Visualizations:

```bash
python scripts/run_visualizations.py --root .
```

---

## Notebooks

Notebooks `01`–`08` document and make inspectable the main components of the pipeline, from source profiling through analysis and visualization.

Deterministic and reproducible transformations are implemented in the scripts in the `scripts/` directory; the notebooks do not replace the automated pipeline.

To open them:

```bash
jupyter lab notebooks/
```

---

## Reproducibility and integrity

The repository keeps the following separate:

```text
RAW

processed

metadata

RDF

validation reports

analysis

visualizations
```

Source hashes are recorded in:

```text
metadata/source_manifest.csv
```

The final distribution also includes:

```text
MANIFEST.sha256
```

which allows the integrity of the release files to be verified.

Verification:

```bash
sha256sum -c MANIFEST.sha256
```

`MANIFEST.sha256` must be regenerated only after the final modification to the release.

---

## Main limitations

The main limitations of the project are:

* the ICCU snapshot represents an observed state and not a complete historical series;

* ICCU statuses do not necessarily provide start and end dates;

* the absence of a special status does not certify full operational status;

* the informational completeness of the registry is not uniform;

* the absence of holdings or special collections in the dataset does not automatically correspond to an actual value of zero;

* territorial administrative changes complicate the 2019–2025 comparison;

* demographic analyses are observational and do not allow causal inference;

* external URIs and datasets may change over time;

* the offline pipeline does not individually dereference all Linked ISPRA targets;

* the local `.invalid` namespace does not constitute a dereferenceable Web publication;

* “Biblioteche Fantasma” is a project label and not an official classification.

The detailed list is available in:

```text
reports/limitations.md
```

---

## Final report

The complete report is available in:

```text
report/relazione.pdf
```

The LaTeX source and bibliography are stored in:

```text
report/relazione.tex
report/bibliography.bib
```

---

## Citation

Cite the project by indicating:

* **Biblioteche Fantasma**;

* year 2026;

* ICCU - Anagrafe delle Biblioteche Italiane;

* ISTAT POSAS 2019 and 2025.

For ISTAT data, the attribution required by the CC BY 4.0 license must be retained.

Cultural-ON retains its own CC BY 3.0 IT license.

The derived tabular dataset and the original project documentation are distributed, unless otherwise stated, under **CC BY 4.0**.
