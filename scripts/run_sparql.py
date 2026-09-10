#!/usr/bin/env python3
"""Run the project SPARQL suite locally from VS Code without GraphDB.

The script uses PyOxigraph as an *embedded* persistent RDF store: there is no
server, Web UI, repository setup or external triplestore to configure.  On the
first execution it imports the RDF artifacts into ``.cache/oxigraph``; later
runs reuse the store while the source files are unchanged.

Examples
--------
Run every query and save CSV results::

    python scripts/run_sparql.py --root .

Run only one query::

    python scripts/run_sparql.py --root . --query 01_status_distribution

Force reconstruction of the local store::

    python scripts/run_sparql.py --root . --rebuild-store

List available queries::

    python scripts/run_sparql.py --root . --list
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from rdflib.plugins.sparql.parser import parseQuery

try:
    from pyoxigraph import QuerySolutions, RdfFormat, Store
except ImportError:  # pragma: no cover - exercised only on an unprepared env
    QuerySolutions = None  # type: ignore[assignment]
    RdfFormat = None  # type: ignore[assignment]
    Store = None  # type: ignore[assignment]


STORE_SCHEMA_VERSION = 1
EXPECTED_EXPLICIT_TRIPLES = 1_644_602


@dataclass(frozen=True)
class SourceFile:
    relative_path: str
    rdf_format_name: str


SOURCE_FILES = (
    SourceFile("ontology/ontology.ttl", "TURTLE"),
    # data.ttl and links.ttl are intentionally serialized as strict N-Triples
    # even though their extension is .ttl (N-Triples is a Turtle subset).
    SourceFile("rdf/data.ttl", "N_TRIPLES"),
    SourceFile("rdf/links.ttl", "N_TRIPLES"),
    SourceFile("rdf/metadata.ttl", "TURTLE"),
)


def sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def source_manifest(root: Path) -> dict:
    files = []
    for source in SOURCE_FILES:
        path = root / source.relative_path
        if not path.exists():
            raise FileNotFoundError(f"RDF source not found: {path}")
        stat = path.stat()
        files.append(
            {
                "path": source.relative_path,
                "format": source.rdf_format_name,
                "bytes": stat.st_size,
                "sha256": sha256(path),
            }
        )
    return {"schema_version": STORE_SCHEMA_VERSION, "files": files}


def require_pyoxigraph() -> None:
    if Store is not None:
        return
    raise SystemExit(
        "PyOxigraph is not installed. From the repository root run:\n"
        "  python -m pip install -r requirements.txt\n"
        "Then rerun this command."
    )


def count_explicit_triples(store: "Store") -> int:
    result = store.query("SELECT (COUNT(*) AS ?triples) WHERE { ?s ?p ?o }")
    row = next(iter(result))
    term = row["triples"]
    return int(term.value) if term is not None else 0


def open_or_build_store(root: Path, rebuild: bool = False) -> tuple["Store", int, bool]:
    require_pyoxigraph()

    cache_root = root / ".cache"
    store_dir = cache_root / "oxigraph"
    manifest_path = cache_root / "oxigraph_manifest.json"
    current_manifest = source_manifest(root)

    cached_manifest = None
    if manifest_path.exists():
        try:
            cached_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cached_manifest = None

    cached_source_manifest = None
    if isinstance(cached_manifest, dict):
        cached_source_manifest = {
            'schema_version': cached_manifest.get('schema_version'),
            'files': cached_manifest.get('files'),
        }

    must_rebuild = rebuild or not store_dir.exists() or cached_source_manifest != current_manifest

    if must_rebuild:
        if store_dir.exists():
            shutil.rmtree(store_dir)
        cache_root.mkdir(parents=True, exist_ok=True)

        store = Store(str(store_dir))
        print("Creating local embedded SPARQL store...", flush=True)
        for source in SOURCE_FILES:
            path = root / source.relative_path
            rdf_format = getattr(RdfFormat, source.rdf_format_name)
            print(f"  importing {source.relative_path}", flush=True)
            store.bulk_load(path=str(path), format=rdf_format)
        store.flush()
        store.optimize()

        triple_count = count_explicit_triples(store)
        current_manifest["explicit_triples"] = triple_count
        # The stored comparison manifest intentionally includes the triple count.
        manifest_path.write_text(
            json.dumps(current_manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return store, triple_count, True

    store = Store(str(store_dir))
    triple_count = int(cached_manifest.get("explicit_triples", 0))
    if not triple_count:
        triple_count = count_explicit_triples(store)
    return store, triple_count, False


def discover_queries(root: Path) -> list[Path]:
    return sorted((root / "sparql").glob("*.rq"))


def select_queries(all_queries: list[Path], selectors: list[str] | None) -> list[Path]:
    if not selectors:
        return all_queries

    selected: list[Path] = []
    for selector in selectors:
        normalized = selector.removesuffix(".rq")
        matches = [
            q
            for q in all_queries
            if q.stem == normalized or q.stem.startswith(normalized)
        ]
        if not matches:
            available = ", ".join(q.stem for q in all_queries)
            raise SystemExit(f"Unknown query '{selector}'. Available: {available}")
        if len(matches) > 1:
            choices = ", ".join(q.stem for q in matches)
            raise SystemExit(f"Ambiguous query '{selector}'. Matches: {choices}")
        if matches[0] not in selected:
            selected.append(matches[0])
    return selected


def term_to_csv(term) -> str:
    if term is None:
        return ""
    value = getattr(term, "value", None)
    return str(value if value is not None else term)


def execute_select(store: "Store", query_text: str, output_csv: Path) -> tuple[int, list[str]]:
    result = store.query(query_text)
    if QuerySolutions is not None and not isinstance(result, QuerySolutions):
        raise TypeError("The project query suite is expected to contain SELECT queries only.")

    variables = [var.value for var in result.variables]
    rows = 0
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(variables)
        for solution in result:
            writer.writerow([term_to_csv(solution[var]) for var in variables])
            rows += 1
    return rows, variables


def write_reports(
    root: Path,
    summaries: Iterable[dict],
    triple_count: int,
    store_rebuilt: bool,
) -> None:
    summaries = list(summaries)
    results_dir = root / "sparql" / "results"
    reports_dir = root / "reports"
    results_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    readme_lines = [
        "# Local SPARQL results",
        "",
        "The `.rq` files were executed locally with PyOxigraph, an embedded disk-based RDF store.",
        "No GraphDB server or external SPARQL endpoint is required.",
        "",
        f"- explicit triples in the local store: **{triple_count:,}**",
        f"- queries executed in this run: **{len(summaries)}**",
        f"- local store rebuilt in this run: **{'yes' if store_rebuilt else 'no'}**",
        "",
        "| Query | Rows | Seconds | Result |",
        "|---|---:|---:|---|",
    ]
    for item in summaries:
        readme_lines.append(
            f"| `{item['query']}` | {item['rows']:,} | {item['seconds']:.3f} | `{item['result']}` |"
        )
    (results_dir / "README.md").write_text("\n".join(readme_lines) + "\n", encoding="utf-8")

    report_lines = [
        "# SPARQL execution report",
        "",
        "## Engine",
        "",
        "All queries reported below were actually executed with **PyOxigraph** against a local persistent store built from:",
        "",
        "- `ontology/ontology.ttl`",
        "- `rdf/data.ttl`",
        "- `rdf/links.ttl`",
        "- `rdf/metadata.ttl`",
        "",
        "PyOxigraph runs inside Python and implements SPARQL 1.1; GraphDB is not required.",
        "The source RDF is loaded into the default graph with no reasoning, so results refer to explicit triples only.",
        "",
        f"Explicit triples in store: **{triple_count:,}**.",
        "",
        "## Executed queries",
        "",
        "| Query | Syntax | Execution | Rows | Seconds | Saved result |",
        "|---|---|---|---:|---:|---|",
    ]
    for item in summaries:
        report_lines.append(
            f"| `{item['query']}` | PASS | PASS | {item['rows']:,} | {item['seconds']:.3f} | `sparql/results/{item['result']}` |"
        )
    report_lines.extend(
        [
            "",
            "## Reproduction",
            "",
            "```bash",
            "python -m pip install -r requirements.txt",
            "python scripts/run_sparql.py --root .",
            "```",
            "",
            "To execute only one query:",
            "",
            "```bash",
            "python scripts/run_sparql.py --root . --query 01_status_distribution",
            "```",
            "",
            "The first run creates `.cache/oxigraph/`; subsequent runs reuse it unless one of the RDF source files changes.",
        ]
    )
    (reports_dir / "sparql_execution_report.md").write_text(
        "\n".join(report_lines) + "\n", encoding="utf-8"
    )

    (reports_dir / "sparql_execution_report.json").write_text(
        json.dumps(
            {
                "engine": "PyOxigraph",
                "reasoning": False,
                "explicit_triples": triple_count,
                "store_rebuilt": store_rebuilt,
                "queries": summaries,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Execute the Biblioteche Fantasma SPARQL suite locally without GraphDB."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root (default: inferred from this script).",
    )
    parser.add_argument(
        "--query",
        action="append",
        help="Query stem/prefix to execute; repeat for multiple queries. Default: all queries.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available .rq files and exit without opening the RDF store.",
    )
    parser.add_argument(
        "--rebuild-store",
        action="store_true",
        help="Delete and rebuild the embedded local RDF store before querying.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    all_queries = discover_queries(root)
    if not all_queries:
        raise SystemExit(f"No SPARQL queries found in {root / 'sparql'}")

    if args.list:
        for query in all_queries:
            print(query.stem)
        return

    queries = select_queries(all_queries, args.query)

    # Keep the existing RDFLib parser as an independent syntax check before
    # touching the store. This gives a clear error tied to the .rq file.
    for query in queries:
        try:
            parseQuery(query.read_text(encoding="utf-8"))
        except Exception as exc:
            raise SystemExit(f"SPARQL syntax error in {query.name}: {exc}") from exc
    print(f"SPARQL syntax OK: {len(queries)} query/queries", flush=True)

    store, triple_count, rebuilt = open_or_build_store(root, args.rebuild_store)
    status = "rebuilt" if rebuilt else "reused"
    print(f"Local store {status}: {triple_count:,} explicit triples", flush=True)
    if triple_count != EXPECTED_EXPLICIT_TRIPLES:
        print(
            f"WARNING: expected {EXPECTED_EXPLICIT_TRIPLES:,} explicit triples, "
            f"found {triple_count:,}. Queries will still run.",
            file=sys.stderr,
        )

    outdir = root / "sparql" / "results"
    summaries: list[dict] = []
    failures: list[str] = []

    for query in queries:
        output = outdir / f"{query.stem}.csv"
        started = time.perf_counter()
        try:
            rows, _ = execute_select(store, query.read_text(encoding="utf-8"), output)
        except Exception as exc:
            failures.append(query.name)
            print(f"FAIL {query.name}: {exc}", file=sys.stderr, flush=True)
            continue
        elapsed = time.perf_counter() - started
        item = {
            "query": query.name,
            "rows": rows,
            "seconds": round(elapsed, 6),
            "result": output.name,
        }
        summaries.append(item)
        print(f"PASS {query.name}: {rows:,} rows -> {output}", flush=True)

    write_reports(root, summaries, triple_count, rebuilt)

    if failures:
        raise SystemExit(
            "One or more queries failed: " + ", ".join(failures) +
            ". Successful query results and the execution report were still saved."
        )

    print(
        f"Completed: {len(summaries)}/{len(queries)} queries. "
        f"Report: {root / 'reports/sparql_execution_report.md'}"
    )


if __name__ == "__main__":
    main()
