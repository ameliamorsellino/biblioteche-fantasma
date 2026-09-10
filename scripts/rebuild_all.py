#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run(*args: str) -> None:
    print("\n>", " ".join(args))
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> None:
    run(
        PYTHON,
        "scripts/build_processed_data.py",
        "--iccu", "data/raw/iccu/opendata.zip",
        "--posas2019", "data/raw/istat/POSAS_2019_it_Tutti_i_file.zip",
        "--posas2025", "data/raw/istat/POSAS_2025_it_Tutti_i_file.zip",
        "--out-root", ".",
    )

    run(
        PYTHON,
        "scripts/build_metadata.py",
        "--root", ".",
        "--iccu", "data/raw/iccu/opendata.zip",
        "--posas2019", "data/raw/istat/POSAS_2019_it_Tutti_i_file.zip",
        "--posas2025", "data/raw/istat/POSAS_2025_it_Tutti_i_file.zip",
        "--cultural-on", "data/external/cultural-ON.owl",
    )

    run(PYTHON, "scripts/validate_outputs.py", "--root", ".")

    run(PYTHON, "scripts/generate_rdf.py", "--root", ".")
    run(PYTHON, "scripts/generate_links.py")

    run(PYTHON, "scripts/validate_rdf.py", "--root", ".")

    run(
        PYTHON,
        "scripts/run_sparql.py",
        "--root", ".",
        "--rebuild-store",
    )

    run(PYTHON, "scripts/validate_shacl.py", "--root", ".")

    run(PYTHON, "scripts/run_analysis.py", "--root", ".")
    run(PYTHON, "scripts/run_visualizations.py", "--root", ".")

    print("\nFull rebuild completed successfully.")


if __name__ == "__main__":
    main()