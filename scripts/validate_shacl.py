#!/usr/bin/env python3
"""Validate the project knowledge graph with pySHACL.

The validator reuses the same persistent PyOxigraph store used by
scripts/run_sparql.py.  This avoids loading the complete knowledge graph into
an in-memory RDFLib graph and removes the need for GraphDB.

Validation characteristics:
- SHACL engine: pySHACL
- data backend: PyOxigraph
- shapes: shacl/shapes.ttl
- inference: none
- Meta-SHACL: enabled
- all validation results are collected
"""
from __future__ import annotations

import argparse
from importlib.metadata import version
from pathlib import Path

from pyshacl import validate
from rdflib import RDF
from rdflib.namespace import SH

from run_sparql import EXPECTED_EXPLICIT_TRIPLES, open_or_build_store


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate Biblioteche Fantasma RDF with pySHACL."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root.",
    )
    parser.add_argument(
        "--rebuild-store",
        action="store_true",
        help="Force reconstruction of the local Oxigraph store before validation.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable verbose pySHACL diagnostic output.",
    )
    args = parser.parse_args()

    root = args.root.resolve()

    shapes_path = root / "shacl" / "shapes.ttl"
    if not shapes_path.exists():
        raise SystemExit(f"SHACL shapes not found: {shapes_path}")

    # Reuse the exact same local persistent RDF store used for SPARQL.
    store, triple_count, rebuilt = open_or_build_store(
        root,
        rebuild=args.rebuild_store,
    )

    status = "rebuilt" if rebuilt else "reused"

    print(f"pySHACL version: {version('pyshacl')}")
    print(f"Local Oxigraph store {status}: {triple_count:,} explicit triples")
    print(f"Shapes graph: {shapes_path.relative_to(root)}")
    print("Meta-SHACL: enabled")
    print("Inference: none")
    print("Running SHACL validation...")

    if triple_count != EXPECTED_EXPLICIT_TRIPLES:
        print(
            f"WARNING: expected {EXPECTED_EXPLICIT_TRIPLES:,} explicit triples, "
            f"found {triple_count:,}."
        )

    conforms, results_graph, results_text = validate(
        store,
        shacl_graph=str(shapes_path),
        inference="none",
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
        meta_shacl=True,
        advanced=False,
        js=False,
        debug=args.debug,
    )

    validation_results = set(
        results_graph.subjects(RDF.type, SH.ValidationResult)
    )

    violations = 0
    warnings = 0
    infos = 0

    for result in validation_results:
        severity = results_graph.value(result, SH.resultSeverity)

        if severity == SH.Violation:
            violations += 1
        elif severity == SH.Warning:
            warnings += 1
        elif severity == SH.Info:
            infos += 1

    reports_dir = root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    ttl_report = reports_dir / "shacl_validation.ttl"
    text_report = reports_dir / "shacl_validation.txt"
    md_report = reports_dir / "shacl_validation.md"

    # Machine-readable standard SHACL ValidationReport.
    results_graph.serialize(
        destination=str(ttl_report),
        format="turtle",
    )

    # Human-readable report produced directly by pySHACL.
    text_report.write_text(
        results_text + ("\n" if not results_text.endswith("\n") else ""),
        encoding="utf-8",
    )

    md_lines = [
        "# SHACL validation",
        "",
        "## Execution",
        "",
        f"- engine: **pySHACL {version('pyshacl')}**",
        "- RDF backend: **PyOxigraph persistent store**",
        "- shapes graph: `shacl/shapes.ttl`",
        f"- explicit triples validated: **{triple_count:,}**",
        "- inference: **none**",
        "- Meta-SHACL validation of the shapes graph: **enabled**",
        "- abort on first violation: **no**",
        "",
        "## Result",
        "",
        f"- conforms: **{'YES' if conforms else 'NO'}**",
        f"- validation results: **{len(validation_results):,}**",
        f"- violations: **{violations:,}**",
        f"- warnings: **{warnings:,}**",
        f"- infos: **{infos:,}**",
        "",
        "## Generated reports",
        "",
        "- `reports/shacl_validation.md` - validation summary",
        "- `reports/shacl_validation.txt` - pySHACL human-readable report",
        "- `reports/shacl_validation.ttl` - standard RDF SHACL ValidationReport",
        "",
        "## Reproduction",
        "",
        "```bash",
        "python -m pip install -r requirements.txt",
        "python scripts/validate_shacl.py --root .",
        "```",
        "",
        "The validator reuses the persistent `.cache/oxigraph/` store also used "
        "by the local SPARQL runner. GraphDB is not required.",
    ]

    md_report.write_text(
        "\n".join(md_lines) + "\n",
        encoding="utf-8",
    )

    print()
    print(f"Conforms: {'YES' if conforms else 'NO'}")
    print(f"Validation results: {len(validation_results):,}")
    print(f"Violations: {violations:,}")
    print(f"Warnings: {warnings:,}")
    print(f"Infos: {infos:,}")
    print(f"Markdown report: {md_report}")
    print(f"RDF report: {ttl_report}")
    print(f"Text report: {text_report}")

    if not conforms:
        print()
        print("SHACL validation FAILED.")
        print("See reports/shacl_validation.txt for details.")
        raise SystemExit(1)

    print()
    print("SHACL validation PASS.")


if __name__ == "__main__":
    main()