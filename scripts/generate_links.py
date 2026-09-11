#!/usr/bin/env python3
"""Generate reproducible external links from stable ICCU and ISTAT identifiers.

No fuzzy matching is used. Library links target the ICCU Anagrafe exact-ISIL
search page and are therefore expressed with rdfs:seeAlso. Municipality links
target Linked ISPRA municipality resources whose URI path embeds the six-digit
ISTAT code. Three 2025 municipalities suppressed in 2026 are deliberately not
linked to the current (2026) Linked ISPRA place dataset.
"""
from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd
from rdflib import URIRef
from rdflib.namespace import OWL, RDFS
from project_config import PUBLIC_BASE

DEV = PUBLIC_BASE + "resource/"
ICCU_PERMALINK = "https://anagrafe.iccu.sbn.it/isil/{}"
ISPRA_MUNI = "https://w3id.org/italia/env/ld/place/municipality/00201_{}"
RETIRED_2026 = {
    "018082": "Lirio: incorporato in Montalto Pavese il 2026-01-31",
    "024027": "Castegnero: soppresso nella fusione Castegnero Nanto il 2026-02-21",
    "024071": "Nanto: soppresso nella fusione Castegnero Nanto il 2026-02-21",
}


def n3(uri: str) -> str:
    return URIRef(uri).n3()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    processed = root / "data" / "processed"
    external_dir = root / "data" / "external"
    rdf_dir = root / "rdf"
    reports_dir = root / "reports"

    external_dir.mkdir(parents=True, exist_ok=True)
    rdf_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    libraries = pd.read_csv(
        processed / "library.csv",
        dtype=str,
        keep_default_na=False,
    )
    municipalities = pd.read_csv(
        processed / "municipality_population.csv",
        dtype=str,
        keep_default_na=False,
    )

    library_rows: list[dict[str, object]] = []
    municipality_rows: list[dict[str, object]] = []

    with (rdf_dir / "links.ttl").open("w", encoding="utf-8", newline="\n") as ttl:
        triple_count = 0

        for _, row in libraries.iterrows():
            isil = row["isil"]
            local = DEV + "library/" + isil
            external = ICCU_PERMALINK.format(isil)

            ttl.write(f"{n3(local)} {RDFS.seeAlso.n3()} {n3(external)} .\n")
            triple_count += 1

            library_rows.append(
                {
                    "isil": isil,
                    "local_uri": local,
                    "external_uri": external,
                    "relation": str(RDFS.seeAlso),
                    "match_status": "generated_from_identifier",
                    "linking_method": (
                        "Official ICCU permalink generated directly "
                        "from the exact ISIL; no fuzzy matching"
                    ),
                    "verification": (
                        "Official ICCU Anagrafe permalink pattern "
                        "/isil/{ISIL}; target is an HTML resource"
                    ),
                }
            )

        for _, row in municipalities.iterrows():
            code = row["istat_code"]
            local = DEV + "municipality/" + code

            if code in RETIRED_2026:
                municipality_rows.append(
                    {
                        "istat_code": code,
                        "municipality_name": row["municipality_name"],
                        "local_uri": local,
                        "external_uri": "",
                        "relation": "",
                        "match_status": "unmatched_temporal_scope",
                        "linking_method": "ISTAT code + 2026 Linked ISPRA URI policy",
                        "verification": RETIRED_2026[code],
                    }
                )
                continue

            external = ISPRA_MUNI.format(code)
            ttl.write(f"{n3(local)} {OWL.sameAs.n3()} {n3(external)} .\n")
            triple_count += 1

            municipality_rows.append(
                {
                    "istat_code": code,
                    "municipality_name": row["municipality_name"],
                    "local_uri": local,
                    "external_uri": external,
                    "relation": str(OWL.sameAs),
                    "match_status": "generated_from_identifier",
                    "linking_method": (
                        "six-digit ISTAT code in Linked ISPRA municipality URI; "
                        "no name/fuzzy matching"
                    ),
                    "verification": (
                        "URI scheme verified on multiple live Linked ISPRA municipality "
                        "resources; this generation step does not dereference every target; "
                        "2026 administrative changes excluded explicitly"
                    ),
                }
            )

    with (external_dir / "library_links.csv").open(
        "w", encoding="utf-8", newline=""
    ) as f:
        writer = csv.DictWriter(f, fieldnames=library_rows[0].keys())
        writer.writeheader()
        writer.writerows(library_rows)

    with (external_dir / "municipality_links.csv").open(
        "w", encoding="utf-8", newline=""
    ) as f:
        writer = csv.DictWriter(f, fieldnames=municipality_rows[0].keys())
        writer.writeheader()
        writer.writerows(municipality_rows)

    municipality_linked = sum(
        row["match_status"] == "generated_from_identifier"
        for row in municipality_rows
    )
    municipality_unmatched = len(municipality_rows) - municipality_linked

    # Generate the interlinking quality report used by the analysis pipeline.
    interlinking_report = pd.DataFrame(
        [
            {
                "entity_type": "Library",
                "total": len(library_rows),
                "generated_links": len(library_rows),
                "ambiguous": 0,
                "unmatched": 0,
                "invalid": 0,
                "coverage_percent": 100.0,
                "linking_method": (
                    "Official ICCU permalink generated from the exact ISIL; "
                    "rdfs:seeAlso because the target is an external HTML resource"
                ),
                "external_dataset": "ICCU Anagrafe delle Biblioteche Italiane",
            },
            {
                "entity_type": "Municipality",
                "total": len(municipality_rows),
                "generated_links": municipality_linked,
                "ambiguous": 0,
                "unmatched": municipality_unmatched,
                "invalid": 0,
                "coverage_percent": (
                    municipality_linked / len(municipality_rows) * 100
                    if municipality_rows
                    else 0.0
                ),
                "linking_method": (
                    "Link generated from the exact six-digit ISTAT code embedded "
                    "in the Linked ISPRA municipality URI; owl:sameAs"
                ),
                "external_dataset": "Linked ISPRA place dataset",
            },
        ]
    )
    interlinking_report.to_csv(
        reports_dir / "interlinking_report.csv",
        index=False,
        float_format="%.4f",
    )

    print(f"links triples: {triple_count:,}")
    print(f"library rows: {len(library_rows):,}")
    print(
        f"municipality links generated: {municipality_linked:,}; "
        f"unmatched: {municipality_unmatched:,}"
    )
    print(f"interlinking report: {reports_dir / 'interlinking_report.csv'}")


if __name__ == "__main__":
    main()
