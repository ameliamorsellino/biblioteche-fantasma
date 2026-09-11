#!/usr/bin/env python3
"""Build the static Linked Data Web publication served through GitHub Pages."""

from __future__ import annotations

import csv
import html
import shutil
from pathlib import Path

from project_config import (
    GITHUB_REPO,
    PUBLIC_BASE,
    RDF_DATA_DOWNLOAD_URL,
)


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PROCESSED = ROOT / "data" / "processed"
EXTERNAL = ROOT / "data" / "external"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def esc(value: str | None) -> str:
    return html.escape(value or "")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <link rel="stylesheet" href="{PUBLIC_BASE}style.css">
</head>
<body>
<main>
{body}
</main>
</body>
</html>
"""


def field(label: str, value: str) -> str:
    if not value:
        return ""
    return (
        "<tr>"
        f"<th>{esc(label)}</th>"
        f"<td>{esc(value)}</td>"
        "</tr>"
    )


def external_field(label: str, url: str, relation: str = "") -> str:
    if not url:
        return ""
    relation_text = f" <small>({esc(relation)})</small>" if relation else ""
    return (
        "<tr>"
        f"<th>{esc(label)}</th>"
        f'<td><a href="{esc(url)}">{esc(url)}</a>{relation_text}</td>'
        "</tr>"
    )


def build_static_assets() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)

    write(DOCS / ".nojekyll", "")

    write(
        DOCS / "style.css",
        """
body {
  margin: 0;
  background: #ffffff;
  color: #202124;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.6;
}
main {
  max-width: 960px;
  margin: 3rem auto;
  padding: 0 1.25rem 4rem;
}
h1, h2 {
  line-height: 1.2;
}
code {
  overflow-wrap: anywhere;
  background: #f3f4f6;
  padding: .15rem .35rem;
  border-radius: .25rem;
}
a {
  color: #0645ad;
}
table {
  border-collapse: collapse;
  width: 100%;
  margin: 1.5rem 0;
}
th, td {
  border-bottom: 1px solid #ddd;
  padding: .6rem;
  text-align: left;
  vertical-align: top;
}
th {
  width: 28%;
}
.note {
  padding: .8rem 1rem;
  background: #f6f8fa;
  border-left: 4px solid #888;
}
small {
  color: #555;
}
""".strip()
        + "\n",
    )

    copy_file(
        ROOT / "ontology/ontology.ttl",
        DOCS / "ontology/ontology.ttl",
    )
    copy_file(
        ROOT / "ontology/ontology.owl",
        DOCS / "ontology/ontology.owl",
    )
    copy_file(
        ROOT / "rdf/links.ttl",
        DOCS / "distribution/links.ttl",
    )
    copy_file(
        ROOT / "rdf/metadata.ttl",
        DOCS / "distribution/metadata.ttl",
    )
    copy_file(
        ROOT / "metadata/dcat.ttl",
        DOCS / "metadata/dcat.ttl",
    )


def build_main_pages() -> None:
    write(
        DOCS / "index.html",
        page(
            "Biblioteche Fantasma",
            f"""
<h1>Biblioteche Fantasma</h1>

<p>
Pubblicazione Web e Linked Open Data del progetto dedicato
all'analisi delle biblioteche italiane non pienamente operative.
</p>

<h2>Risorse</h2>

<ul>
  <li><a href="ontology/">Ontologia del progetto</a></li>
  <li><a href="metadata/dataset/">Dataset e metadati</a></li>
  <li><a href="resource/dataset/biblioteche-fantasma/">Risorsa dataset</a></li>
  <li><a href="distribution/links.ttl">RDF interlinking</a></li>
  <li><a href="distribution/metadata.ttl">RDF metadata</a></li>
  <li><a href="{RDF_DATA_DOWNLOAD_URL}">Knowledge graph completo</a></li>
</ul>

<h2>Namespace</h2>

<p><code>{PUBLIC_BASE}</code></p>

<p>
Le URI di biblioteche e comuni sono pubblicate come pagine HTML
statiche generate automaticamente dai dati processati.
</p>

<p>
Repository:
<a href="{GITHUB_REPO}">{GITHUB_REPO}</a>
</p>
""",
        ),
    )

    write(
        DOCS / "ontology/index.html",
        page(
            "Ontologia — Biblioteche Fantasma",
            f"""
<h1>Ontologia Biblioteche Fantasma</h1>

<p>
Vocabolario locale del knowledge graph, con riuso di Cultural-ON,
SKOS, PROV-O, GeoSPARQL e altri vocabolari standard.
</p>

<table>
<tr>
  <th>IRI</th>
  <td><code>{PUBLIC_BASE}ontology</code></td>
</tr>
<tr>
  <th>Turtle</th>
  <td><a href="ontology.ttl">ontology.ttl</a></td>
</tr>
<tr>
  <th>RDF/XML</th>
  <td><a href="ontology.owl">ontology.owl</a></td>
</tr>
</table>

<p><a href="../">Torna alla pubblicazione</a></p>
""",
        ),
    )

    write(
        DOCS / "metadata/dataset/index.html",
        page(
            "Dataset — Biblioteche Fantasma",
            f"""
<h1>Dataset Biblioteche Fantasma</h1>

<p>
Dataset derivato da Open Data ICCU e ISTAT, corredato da metadati,
knowledge graph RDF e collegamenti verso dati esterni.
</p>

<table>
<tr>
  <th>URI</th>
  <td><code>{PUBLIC_BASE}metadata/dataset</code></td>
</tr>
<tr>
  <th>DCAT</th>
  <td><a href="../dcat.ttl">dcat.ttl</a></td>
</tr>
<tr>
  <th>Knowledge graph</th>
  <td><a href="{RDF_DATA_DOWNLOAD_URL}">data.ttl</a></td>
</tr>
<tr>
  <th>Interlinking</th>
  <td><a href="../../distribution/links.ttl">links.ttl</a></td>
</tr>
<tr>
  <th>RDF metadata</th>
  <td><a href="../../distribution/metadata.ttl">metadata.ttl</a></td>
</tr>
</table>

<p><a href="../../">Torna alla pubblicazione</a></p>
""",
        ),
    )

    write(
        DOCS / "resource/dataset/biblioteche-fantasma/index.html",
        page(
            "Risorsa dataset — Biblioteche Fantasma",
            f"""
<h1>Biblioteche Fantasma</h1>

<p>
Risorsa RDF che identifica il dataset Biblioteche Fantasma.
</p>

<table>
<tr>
  <th>URI</th>
  <td><code>{PUBLIC_BASE}resource/dataset/biblioteche-fantasma</code></td>
</tr>
<tr>
  <th>Metadati</th>
  <td><a href="../../../metadata/dataset/">Dataset metadata</a></td>
</tr>
<tr>
  <th>Knowledge graph</th>
  <td><a href="{RDF_DATA_DOWNLOAD_URL}">data.ttl</a></td>
</tr>
</table>

<p><a href="../../../">Torna alla pubblicazione</a></p>
""",
        ),
    )


def build_library_pages() -> int:
    target = DOCS / "resource" / "library"
    if target.exists():
        shutil.rmtree(target)

    libraries = read_rows(PROCESSED / "library.csv")

    statuses = {
        row["isil"]: row
        for row in read_rows(PROCESSED / "library_status.csv")
    }

    links = {
        row["isil"]: row
        for row in read_rows(EXTERNAL / "library_links.csv")
    }

    for row in libraries:
        isil = row["isil"]
        status = statuses.get(isil, {})
        link = links.get(isil, {})

        uri = PUBLIC_BASE + f"resource/library/{isil}"

        body = f"""
<h1>{esc(row["name_original"])}</h1>

<p class="note">
URI persistente della risorsa:<br>
<code>{esc(uri)}</code>
</p>

<table>
{field("ISIL", isil)}
{field("Nome", row["name_original"])}
{field("Tipologia funzionale", row["functional_type"])}
{field("Tipologia amministrativa", row["administrative_type"])}
{field("Indirizzo", row["address_original"])}
{field("CAP", row["postal_code"])}
{field("Codice ISTAT comune", row["istat_code"])}
{field("Stato normalizzato", status.get("normalized_status", ""))}
{field("Gruppo analitico", status.get("analytical_group", ""))}
{field("Stato sorgente ICCU", status.get("source_status", ""))}
{field("Ultimo aggiornamento ICCU", row["updated_date"])}
{external_field(
    "Risorsa ICCU",
    link.get("external_uri", ""),
    "rdfs:seeAlso",
)}
</table>

<p>
<a href="{RDF_DATA_DOWNLOAD_URL}">
Knowledge graph RDF completo
</a>
</p>

<p><a href="{PUBLIC_BASE}">Torna alla pubblicazione</a></p>
"""

        write(
            target / isil / "index.html",
            page(row["name_original"] or isil, body),
        )

    return len(libraries)


def build_municipality_pages() -> int:
    target = DOCS / "resource" / "municipality"
    if target.exists():
        shutil.rmtree(target)

    municipalities = read_rows(
        PROCESSED / "analysis_municipality.csv"
    )

    links = {
        row["istat_code"]: row
        for row in read_rows(EXTERNAL / "municipality_links.csv")
    }

    for row in municipalities:
        code = row["istat_code"]
        link = links.get(code, {})

        uri = PUBLIC_BASE + f"resource/municipality/{code}"

        body = f"""
<h1>{esc(row["municipality_name"])}</h1>

<p class="note">
URI persistente della risorsa:<br>
<code>{esc(uri)}</code>
</p>

<table>
{field("Codice ISTAT", code)}
{field("Comune", row["municipality_name"])}
{field("Regione", row["region"])}
{field("Provincia", row["province"])}
{field("Codice ISTAT provincia", row["province_istat_code"])}
{field("Popolazione 2019", row["population_2019"])}
{field("Popolazione 2025", row["population_2025"])}
{field(
    "Variazione popolazione 2019–2025 (%)",
    row["population_change_percent"],
)}
{field(
    "Comparabilità demografica",
    row["population_comparability"],
)}
{external_field(
    "Linked ISPRA",
    link.get("external_uri", ""),
    "owl:sameAs" if link.get("external_uri", "") else "",
)}
{field("Stato interlinking", link.get("match_status", ""))}
</table>

<p>
<a href="{RDF_DATA_DOWNLOAD_URL}">
Knowledge graph RDF completo
</a>
</p>

<p><a href="{PUBLIC_BASE}">Torna alla pubblicazione</a></p>
"""

        write(
            target / code / "index.html",
            page(row["municipality_name"] or code, body),
        )

    return len(municipalities)


def main() -> None:
    build_static_assets()
    build_main_pages()

    library_count = build_library_pages()
    municipality_count = build_municipality_pages()

    print(f"Library pages: {library_count:,}")
    print(f"Municipality pages: {municipality_count:,}")
    print(
        "Core dereferenceable entity pages: "
        f"{library_count + municipality_count:,}"
    )
    print(f"Static Web publication generated in {DOCS}")


if __name__ == "__main__":
    main()
