# Final Analysis by Research Question

## RQ1 - territorial distribution

The main scope contains **2,497 problematic libraries** out of **18,956 libraries** (13.17%). The highest regional shares are Molise **43.72% (80/183)**, Liguria **31.81% (209/657)**, Abruzzo **22.20% (93/419)** and Umbria **17.94% (73/407)**. In absolute terms, Lombardy ranks first with 366 cases. The map uses only the already cleaned ICCU coordinates.

## RQ2 - statuses

Out of 19,611 records: no special status registered 13,200 (67.31%), no longer existing 1,827 (9.32%), not surveyed 1,723 (8.79%), merged 1,502 (7.66%), other institution 655 (3.34%), temporarily closed 619 (3.16%). Mergers and non-surveyed records are not treated as cessation.

## RQ3 - types

The analysis uses the functional and administrative types present in the `library.csv` master, avoiding defining the sample through `library_type.csv`, whose coverage is selective with respect to ICCU status. After excluding the 655 records classified as “other ICCU-linked institution”, the sample includes **18,956 libraries**.

Among functional types, `NON SPECIFICATA` has 452 problematic libraries out of 1,233 (36.66%). Among the informative categories: conservation 78/554 (14.08%), specialized 630/4,694 (13.42%), higher education institution 367/2,774 (13.23%), public 903/8,162 (11.06%) and school 65/1,275 (5.10%).

Considering all categories, the association between functional type and inclusion in the problematic scope has **corrected Cramér's V = 0.196**; for administrative type **V = 0.193**.

The result is, however, sensitive to the `NON SPECIFICATA` category. Excluding it, Cramér's V decreases to **0.077** for functional type (`N=17,723`) and to **0.095** for administrative type (`N=17,844`). The residual association is therefore weak and the inferential results should be interpreted together with the descriptive distributions, also because some cells have expected frequencies below 5.

## RQ4 - demography

Primary analysis: **N=6,659** comparable municipalities with at least one library. Pearson `r=-0.1064`, Spearman `rho=-0.0670`: negative but weak association. Excluding 115 IQR outliers in population change: `r=-0.0956`, `rho=-0.0584`. Municipalities with population decline have an average problematic share of 12.42%, while stable/growing municipalities have 8.48%. This is not causal evidence.

## RQ5 - holdings and special collections

**627/2,497** problematic libraries have at least one holdings row, for a total of 2,828 rows. Quantities are missing in 461 rows and positive in 2,367; there are no explicit zeros. The sum of known positive quantities alone is 7,500,259, but it is not a complete inventory because coverage is partial and some categories may be aggregates. No problematic library appears in `special_collection.csv`: this is an absence of records in the subset, not evidence of the actual absence of special collections.

## RQ6 - interlinking

The pipeline generates links for **19,611/19,611 libraries = 100%** to ICCU through `rdfs:seeAlso` and for **7,893/7,896 municipalities = 99.9620%** to Linked ISPRA through `owl:sameAs`. Links are constructed deterministically from official identifiers, without fuzzy matching. The three cases without a link are Lirio, Castegnero and Nanto, intentionally left unlinked because of administrative changes that occurred in 2026. The pipeline does not individually dereference all external URIs during the offline rebuild, so the percentage expresses link-generation coverage according to the documented URI policy.

## RQ7 - mergers

The validated network contains **1,412 edges**, **1,821 nodes**, **410 weakly connected components**; the largest component has 40 nodes. The only cycle is the self-loop `IT-SS0267 -> IT-SS0267`. The target with the highest in-degree is `IT-CT0337` (39). The visualization shows only the largest component to avoid a spaghetti chart.

## RQ8 - 65+ share

Across N=6,659 municipalities: Pearson `r=0.1454`, Spearman `rho=0.1054`. The association is positive but weak and is retained as a secondary non-causal analysis.
