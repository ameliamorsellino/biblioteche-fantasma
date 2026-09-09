#!/usr/bin/env python3
"""Generate reproducible external links from checkpoint-1 identifiers.

No fuzzy matching is used. Library links target the ICCU Anagrafe exact-ISIL
search page and are therefore expressed with rdfs:seeAlso. Municipality links
target Linked ISPRA municipality resources whose URI path embeds the six-digit
ISTAT code. Three 2025 municipalities suppressed in 2026 are deliberately not
linked to the current (2026) Linked ISPRA place dataset.
"""
from pathlib import Path
from urllib.parse import urlencode
import csv
import pandas as pd
from rdflib import URIRef
from rdflib.namespace import OWL, RDFS

DEV = "https://biblioteche-fantasma.invalid/resource/"
ICCU_RESULTS = "https://anagrafe.iccu.sbn.it/it/ricerca/risultati.html"
ISPRA_MUNI = "https://w3id.org/italia/env/ld/place/municipality/00201_{}"
RETIRED_2026 = {
    "018082": "Lirio: incorporato in Montalto Pavese il 2026-01-31",
    "024027": "Castegnero: soppresso nella fusione Castegnero Nanto il 2026-02-21",
    "024071": "Nanto: soppresso nella fusione Castegnero Nanto il 2026-02-21",
}


def n3(u): return URIRef(u).n3()


def main():
    root = Path(__file__).resolve().parents[1]
    processed = root / "data" / "processed"
    ext = root / "data" / "external"
    rdf = root / "rdf"
    ext.mkdir(parents=True, exist_ok=True); rdf.mkdir(parents=True, exist_ok=True)

    libs = pd.read_csv(processed / "library.csv", dtype=str, keep_default_na=False)
    munis = pd.read_csv(processed / "municipality_population.csv", dtype=str, keep_default_na=False)

    lib_rows = []
    with (rdf / "links.ttl").open("w", encoding="utf-8", newline="\n") as ttl:
        triple_count = 0
        for _, row in libs.iterrows():
            isil = row["isil"]
            local = DEV + "library/" + isil
            external = ICCU_RESULTS + "?" + urlencode({"codice_isil": isil, "start": "0"})
            ttl.write(f"{n3(local)} {RDFS.seeAlso.n3()} {n3(external)} .\n")
            triple_count += 1
            lib_rows.append({
                "isil": isil,
                "local_uri": local,
                "external_uri": external,
                "relation": str(RDFS.seeAlso),
                "match_status": "exact_identifier_lookup",
                "linking_method": "ISIL exact query; no fuzzy matching",
                "verification": "ICCU result-page pattern verified on official Anagrafe; target is an HTML record/search document, not an RDF entity",
            })

        muni_rows = []
        for _, row in munis.iterrows():
            code = row["istat_code"]
            local = DEV + "municipality/" + code
            if code in RETIRED_2026:
                muni_rows.append({
                    "istat_code": code,
                    "municipality_name": row["municipality_name"],
                    "local_uri": local,
                    "external_uri": "",
                    "relation": "",
                    "match_status": "unmatched_temporal_scope",
                    "linking_method": "ISTAT code + 2026 Linked ISPRA URI policy",
                    "verification": RETIRED_2026[code],
                })
                continue
            external = ISPRA_MUNI.format(code)
            ttl.write(f"{n3(local)} {OWL.sameAs.n3()} {n3(external)} .\n")
            triple_count += 1
            muni_rows.append({
                "istat_code": code,
                "municipality_name": row["municipality_name"],
                "local_uri": local,
                "external_uri": external,
                "relation": str(OWL.sameAs),
                "match_status": "exact_identifier_match",
                "linking_method": "six-digit ISTAT code in Linked ISPRA municipality URI; no name/fuzzy matching",
                "verification": "URI scheme verified on multiple live Linked ISPRA municipality resources; 2026 administrative changes excluded explicitly",
            })

    with (ext / "library_links.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=lib_rows[0].keys()); w.writeheader(); w.writerows(lib_rows)
    with (ext / "municipality_links.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=muni_rows[0].keys()); w.writeheader(); w.writerows(muni_rows)
    print(f"links triples: {triple_count:,}")
    print(f"library rows: {len(lib_rows):,}")
    print(f"municipality exact: {sum(r['match_status']=='exact_identifier_match' for r in muni_rows):,}; unmatched: {sum(r['match_status']!='exact_identifier_match' for r in muni_rows):,}")

if __name__ == "__main__": main()
