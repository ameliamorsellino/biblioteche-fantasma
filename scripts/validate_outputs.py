#!/usr/bin/env python3
"""Validate the reproducible tabular outputs and project metadata."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
from rdflib import Graph, URIRef
from rdflib.namespace import DCTERMS
from project_config import PUBLIC_BASE


def sha256(path: Path) -> str:
    """Return the SHA-256 digest of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("."))
    args = ap.parse_args()
    root = args.root.resolve()

    required = [
        "data/raw/iccu/opendata.zip",
        "data/raw/istat/POSAS_2019_it_Tutti_i_file.zip",
        "data/raw/istat/POSAS_2025_it_Tutti_i_file.zip",
        "data/processed/library.csv",
        "data/processed/library_status.csv",
        "data/processed/library_type.csv",
        "data/processed/library_holdings.csv",
        "data/processed/special_collection.csv",
        "data/processed/library_contact.csv",
        "data/processed/library_previous_name.csv",
        "data/processed/library_mergers.csv",
        "data/processed/municipality_population.csv",
        "data/processed/analysis_municipality.csv",
        "metadata/status_mapping.csv",
        "metadata/municipality_crosswalk_2019_2025.csv",
        "metadata/source_manifest.csv",
        "metadata/file_inventory.csv",
        "metadata/licenses.md",
        "metadata/datapackage.json",
        "metadata/dcat.ttl",
        "metadata/provenance.ttl",
        "reports/decisions_log.md",
        "reports/cleaning_log.csv",
        "reports/join_quality.csv",
        "reports/data_quality.md",
        "reports/data_quality_metrics.csv",
        "scripts/build_processed_data.py",
        "scripts/build_metadata.py",
        "requirements.txt",
        "data/external/cultural-ON.owl",
    ]

    missing = [item for item in required if not (root / item).exists()]
    if missing:
        raise SystemExit("Missing: " + ", ".join(missing))

    # Verify that every local source declared in the manifest exists and that
    # its SHA-256 matches the recorded provenance value.
    manifest = pd.read_csv(
        root / "metadata/source_manifest.csv",
        dtype=str,
        keep_default_na=False,
    )
    for _, row in manifest.iterrows():
        local_file = row.get("local_file", "").strip()
        expected_hash = row.get("sha256", "").strip()
        if not local_file:
            continue

        source_path = root / local_file
        assert source_path.exists(), f"Missing source file: {local_file}"
        if expected_hash:
            actual_hash = sha256(source_path)
            assert actual_hash == expected_hash, (
                f"SHA-256 mismatch for {local_file}: "
                f"expected {expected_hash}, got {actual_hash}"
            )

    lib = pd.read_csv(
        root / "data/processed/library.csv",
        dtype=str,
        keep_default_na=False,
        low_memory=False,
    )
    assert len(lib) == 19611
    assert lib.isil.nunique() == 19611
    assert (lib.isil != "").all()
    assert lib.isil.str.match(r"^IT-[A-Z]{2}\d{4}$").all()
    assert lib.istat_code.nunique() == 6660
    assert lib.province_istat_code.nunique() == 107
    assert lib.region.nunique() == 20
    assert (lib.coordinate_quality_flag == "zero_pair_treated_as_missing").sum() == 63
    assert (lib.coordinate_quality_flag == "missing").sum() == 24
    assert (lib.coordinate_quality_flag == "outside_italy_bbox_review").sum() == 3

    status = pd.read_csv(
        root / "data/processed/library_status.csv",
        dtype=str,
        keep_default_na=False,
        low_memory=False,
    )
    status_mapping = pd.read_csv(
        root / "metadata/status_mapping.csv",
        dtype=str,
        keep_default_na=False,
        low_memory=False,
    )
    rationale_by_source = status_mapping.set_index("source_status")["rationale"].to_dict()
    assert all(
        rationale_by_source.get(source_status, "") == rationale
        for source_status, rationale in zip(status.source_status, status.rationale)
    )

    expected_status_counts = {
        "NESSUNO_STATO_SPECIALE_REGISTRATO": 13200,
        "BIBLIOTECA_NON_PIU_ESISTENTE": 1827,
        "BIBLIOTECA_NON_CENSITA": 1723,
        "BIBLIOTECA_CONFLUITA": 1502,
        "ALTRO_ISTITUTO_COLLEGATO_ICCU": 655,
        "TEMPORANEAMENTE_CHIUSA": 619,
        "BIBLIOTECA_IN_VIA_DI_ALLESTIMENTO": 34,
        "DEPOSITO_SENZA_PUNTO_DI_SERVIZIO": 33,
        "SERVIZI_SOSPESI_CAUSA_SISMA": 12,
        "INAGIBILE": 4,
        "RIAPERTURA_AGIBILITA_PARZIALE": 2,
    }
    assert status.normalized_status.value_counts().to_dict() == expected_status_counts
    assert (status.include_in_main_analysis == "True").sum() == 2497

    mergers = pd.read_csv(
        root / "data/processed/library_mergers.csv",
        dtype=str,
        keep_default_na=False,
    )
    assert len(mergers) == 1502
    assert (mergers.parse_success == "True").sum() == 1412
    assert (mergers.target_exists_in_snapshot == "True").sum() == 1412
    assert (mergers.self_loop == "True").sum() == 1
    assert (mergers.in_cycle == "True").sum() == 1
    self_loop = mergers.loc[
        mergers.self_loop == "True", ["source_isil", "target_isil"]
    ]
    assert self_loop.to_dict("records") == [
        {"source_isil": "IT-SS0267", "target_isil": "IT-SS0267"}
    ]

    population = pd.read_csv(
        root / "data/processed/municipality_population.csv",
        dtype=str,
        keep_default_na=False,
    )
    assert len(population) == 7896
    assert population.istat_code.nunique() == 7896
    assert (
        population.population_comparability
        == "not_comparable_due_to_2021_territorial_split"
    ).sum() == 2

    analysis = pd.read_csv(
        root / "data/processed/analysis_municipality.csv",
        dtype=str,
        keep_default_na=False,
    )
    assert len(analysis) == 7896
    assert analysis.istat_code.nunique() == 7896
    assert set(analysis.loc[analysis.province_istat_code.eq("080"), "province"]) == {
        "Reggio di Calabria"
    }
    assert analysis.province_istat_code.eq("080").sum() == 97
    assert int(pd.to_numeric(analysis.total_registry_records).sum()) == 19611
    assert int(pd.to_numeric(analysis.main_problematic_libraries).sum()) == 2497
    assert int(pd.to_numeric(analysis.total_libraries).sum()) == 18956

    # ICCU -> ISTAT 2025 joinability.
    assert lib.istat_code.isin(set(population.istat_code)).all()


    # Metadata serializations must parse.
        
    with (root / "metadata/datapackage.json").open(encoding="utf-8") as f:
        datapackage = json.load(f)

    resources = datapackage.get("resources", [])
    assert len(resources) == 10

    resource_by_name = {
        resource["name"]: resource
        for resource in resources
    }

    for resource_name in [
        "analysis_municipality",
        "municipality_population",
    ]:
        fields = {
            field["name"]: field["type"]
            for field in resource_by_name[resource_name]["schema"]["fields"]
        }
        assert fields["population_comparability"] == "string"

    dcat_graph = Graph().parse(
        root / "metadata/dcat.ttl",
        format="turtle",
    )

    dataset_uri = URIRef(
        PUBLIC_BASE + "metadata/dataset"
    )

    assert (
        str(dcat_graph.value(dataset_uri, DCTERMS.identifier))
        == "biblioteche-fantasma"
    )

    Graph().parse(root / "metadata/provenance.ttl", format="turtle")
    Graph().parse(root / "data/external/cultural-ON.owl", format="xml")

    print("Validation OK")


if __name__ == "__main__":
    main()
