# Decisions log

# Decision D01

## Problem
NULL ICCU status

## Evidence
13200 records have an empty `source_status`. ICCU documentation uses the field to indicate special statuses when populated.

## Alternatives considered
Interpret NULL as open; exclude; neutral category.

## Decision
Use `NESSUNO_STATO_SPECIALE_REGISTRATO`.

## Rationale
The absence of a value does not prove that the library is open.

## Consequence
NULL values do not automatically fall into the problematic categories.

# Decision D02

## Problem
Definition of main_problematic_libraries

## Evidence
The canonical mapping includes only statuses with `include_in_main_analysis=True`: cessation, temporary closure, inaccessibility/earthquake-related suspension, partial reopening, repository without a service point.

## Alternatives considered
Also include mergers/not surveyed/under setup; include all non-null statuses.

## Decision
Sum only the statuses marked True in `metadata/status_mapping.csv`.

## Rationale
Keeps cessation, interruption, partial operation, organizational transformation and registry incompleteness separate.

## Consequence
National count = 2,497.

# Decision D03

## Problem
1:N XML relationships

## Evidence
Holdings 93,512 rows, special collections 9,737, contacts 62,804; multiple rows per ISIL.

## Alternatives considered
Mega-CSV with duplicated libraries; separate tables.

## Decision
Keep normalized tables for each relationship.

## Rationale
Avoids spurious multiplication and loss of cardinality.

## Consequence
Subsequent joins must preserve 1:N relationships.

# Decision D04

## Problem
Coordinates (0,0)

## Evidence
63 libraries have the original pair (0,0).

## Alternatives considered
Treat as a real coordinate; geocode; mark as missing.

## Decision
Set cleaned coordinates to missing; preserve originals.

## Rationale
(0,0) is a pseudo-value that is not useful for locating an Italian library.

## Consequence
No automatic geographic imputation.

# Decision D05

## Problem
Coordinates outside the bounding box

## Evidence
3 records fall outside the indicative Italy bounding box but within the global range.

## Alternatives considered
Delete; correct/geocode; preserve with a flag.

## Decision
Preserve and flag as `outside_italy_bbox_review`.

## Rationale
An Italian institution may be located abroad; the bounding box is a check, not proof of an error.

## Consequence
Three records require interpretation.

# Decision D06

## Problem
IT-ME0024

## Evidence
Among the three geographic outliers, `IT-ME0024` has coordinates compatible with India, not with the expected territorial location.

## Alternatives considered
Correct from address; remove; flag.

## Decision
Flag without automatic correction.

## Rationale
There is no reliable source for replacing the coordinates.

## Consequence
Open anomaly for manual review.

# Decision D07

## Problem
Parsing of mergers

## Evidence
1,502 merger records; 1,412 target ISILs extracted; 90 without a parseable target.

## Alternatives considered
Free/fuzzy parsing; controlled regex; no parsing.

## Decision
Exact regex `Biblioteca confluita in IT-XXdddd`; target validated against the snapshot.

## Rationale
ISIL has an official format and allows deterministic validation.

## Consequence
1,412 targets exist in the snapshot; 90 remain without a target.

# Decision D08

## Problem
Self-loop IT-SS0267

## Evidence
`IT-SS0267 → IT-SS0267` is present in the source after parsing and target validation.

## Alternatives considered
Remove/correct; preserve and flag.

## Decision
Preserve with `self_loop=True` and `in_cycle=True`.

## Rationale
No evidence justifies a correction.

## Consequence
Only cycle detected in the merger graph.

# Decision D09

## Problem
ISTAT Età=999

## Evidence
For 7,954 municipalities in 2019 and 7,896 municipalities in 2025, the `Età=999` row exactly matches the sum of ages 0–100; mismatch 0.

## Alternatives considered
Assume it without verification; always recalculate; validate and use it.

## Decision
Use 999 as the total after complete empirical verification.

## Rationale
Avoids undocumented or assumed interpretations.

## Consequence
Municipal totals used for 2019/2025 population.

# Decision D10

## Problem
Municipality “None” and keep_default_na=False

## Evidence
There is an official municipality named `None`; standard pandas parsers may treat the string as NA.

## Alternatives considered
Default NA parsing; ex-post exception; preserve strings.

## Decision
Read POSAS with `keep_default_na=False`.

## Rationale
Preserves the official name without information loss.

## Consequence
The municipality None remains a valid string.

# Decision D11

## Problem
2019–2025 administrative changes

## Evidence
2019 geography: 7,954 municipalities; 2025: 7,896; crosswalk: 7,955 relationships toward 7,896 current municipalities.

## Alternatives considered
Join by name/fuzzy matching; remove non-matches; official crosswalk by codes and predecessors.

## Decision
Use 2025 analytical geography and an explicit crosswalk by code/predecessors.

## Rationale
Official codes and administrative transformations are more reliable than fuzzy matching.

## Consequence
Mergers/incorporations aggregate predecessors when reconstructible.

# Decision D12

## Problem
Trapani/Misiliscemi

## Evidence
Misiliscemi was created through a territorial split from Trapani in 2021; municipal POSAS 2019 does not allow the territory to be correctly subtracted.

## Alternatives considered
Assign all of Trapani 2019 to one of the two; estimate; mark as non-comparable.

## Decision
Both marked `not_comparable_due_to_2021_territorial_split` for the 2019 comparison.

## Rationale
Any allocation would be invented.

## Consequence
Population 2019 and changes remain NA for the two municipalities.

# Decision D13

## Problem
Name Reggio Calabria / Reggio di Calabria

## Evidence
In POSAS 2025 Provinces, province code 080, the official name is `Reggio di Calabria`; 97 municipalities belong to province 080.

## Alternatives considered
Use ICCU label `Reggio Calabria`; use POSAS 2025.

## Decision
In the analytical dataset the province is canonicalized from POSAS 2025 and is `Reggio di Calabria`.

## Rationale
The analytical dataset uses ISTAT 2025 territorial geography as the canonical source.

## Consequence
The rebuild deterministically produces 97 rows with `Reggio di Calabria`.

# Decision D14

## Problem
Textual difference in rationale

## Evidence
`library_status.csv` and `metadata/status_mapping.csv` now use the same `classify_status` function; canonical comparison: 0 differences.

## Alternatives considered
Keep independent texts; manual synchronization; single function.

## Decision
Use the same canonical function for both outputs.

## Rationale
Eliminates purely textual drift while preserving identical semantics.

## Consequence
The validator checks rationale equality for every source_status.

# Decision D15

## Problem
patrimonio.xml export-date anomaly

## Evidence
The root of `patrimonio.xml` declares `data-export="2026-09-08T14:00:"`, a syntactically incomplete timestamp.

## Alternatives considered
Correct the timestamp; ignore it; record the anomaly.

## Decision
Do not modify the source; record the anomaly.

## Rationale
There is no evidence from which to infer the missing seconds.

## Consequence
The main snapshot remains determined by biblioteche.json; the XML timestamp remains a quality note.

# Decision D16

## Problem
License of the derived dataset

## Evidence
ICCU Open Data = CC0; Istat POSAS = CC BY 4.0; Cultural-ON is separate and does not contribute to tabular values at this stage.

## Alternatives considered
CC0; CC BY 4.0; another license without analysis.

## Decision
Planned license for the derived tabular dataset: CC BY 4.0.

## Rationale
Complies with the attribution requirement arising from the Istat component and allows reuse/modification/commercial use.

## Consequence
Attribute Istat; cite ICCU; do not automatically relicense Cultural-ON or ICCU documentation.
