#!/usr/bin/env python3
"""Build the static Linked Data Web publication served through GitHub Pages."""

from __future__ import annotations

import csv
import html
import os
import shutil
from pathlib import Path

from project_config import (
    GITHUB_REPO,
    PUBLIC_BASE,
    RDF_DATA_DOWNLOAD_URL,
)


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

# Default: namespace pubblico GitHub Pages.
# Per la preview locale:
# BF_SITE_BASE=http://localhost:8000/
SITE_BASE = os.environ.get(
    "BF_SITE_BASE",
    PUBLIC_BASE,
).rstrip("/") + "/"
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
  <meta
    name="description"
    content="Biblioteche Fantasma — analisi, integrazione e pubblicazione Linked Open Data delle biblioteche italiane non pienamente operative."
  >
  <title>{esc(title)}</title>
  <link rel="stylesheet" href="{SITE_BASE}style.css">
</head>
<body>

<header class="site-header">
  <nav class="nav-shell" aria-label="Navigazione principale">
    <a class="brand" href="{SITE_BASE}">
      Biblioteche Fantasma
    </a>

    <div class="nav-links">
      <a href="{SITE_BASE}#overview">Overview</a>
      <a href="{SITE_BASE}#metodo">Metodo</a>
      <a href="{SITE_BASE}#risultati">Risultati</a>
      <a href="{SITE_BASE}#knowledge-graph">Knowledge Graph</a>
      <a href="{SITE_BASE}#linked-data">Linked Data</a>
      <a href="{SITE_BASE}#limiti">Limiti</a>
      <a href="{SITE_BASE}#riproducibilita">Riproducibilità</a>
    </div>
  </nav>
</header>

<main>
{body}
</main>

<footer class="site-footer">
  <div class="footer-inner">
    <div>
      <strong>Biblioteche Fantasma</strong><br>
      <span>
        Progetto universitario di Open Data Management
      </span>
    </div>

    <div class="footer-links">
      <a href="{GITHUB_REPO}">Repository GitHub</a>
      <a href="{RDF_DATA_DOWNLOAD_URL}">Knowledge graph RDF</a>
    </div>
  </div>
</footer>

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
:root {
  --background: #fbfaf7;
  --surface: #ffffff;
  --surface-soft: #f3f1eb;
  --text: #20201d;
  --muted: #65645f;
  --border: #ddd9cf;
  --accent: #7a2f2f;
  --accent-dark: #542020;
  --accent-soft: #f2e6e2;
  --max-width: 1180px;
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
  scroll-padding-top: 5.5rem;
}

body {
  margin: 0;
  background: var(--background);
  color: var(--text);
  font-family:
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    sans-serif;
  line-height: 1.65;
}

a {
  color: var(--accent);
  text-underline-offset: .15em;
}

a:hover {
  color: var(--accent-dark);
}

.site-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: rgba(251, 250, 247, .96);
  border-bottom: 1px solid var(--border);
  backdrop-filter: blur(10px);
}

.nav-shell {
  max-width: var(--max-width);
  margin: 0 auto;
  min-height: 4.5rem;
  padding: .8rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
}

.brand {
  color: var(--text);
  font-family: Georgia, "Times New Roman", serif;
  font-weight: 700;
  font-size: 1.08rem;
  text-decoration: none;
  white-space: nowrap;
}

.nav-links {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: .35rem 1rem;
  font-size: .88rem;
}

.nav-links a {
  color: var(--muted);
  text-decoration: none;
}

.nav-links a:hover {
  color: var(--accent);
}

main {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0 1.5rem 5rem;
}

.hero {
  padding: 6.5rem 0 4.5rem;
  border-bottom: 1px solid var(--border);
}

.eyebrow {
  margin: 0 0 .8rem;
  color: var(--accent);
  font-weight: 750;
  font-size: .76rem;
  letter-spacing: .12em;
  text-transform: uppercase;
}

.section-kicker {
  margin: 0 0 .55rem;
  color: var(--accent);
  font-family: Georgia, "Times New Roman", serif;
  font-weight: 700;
  font-size: clamp(1.65rem, 2.4vw, 2.15rem);
  line-height: 1.15;
  letter-spacing: .01em;
  text-transform: uppercase;
}

.hero h1,
.section h2,
.editorial-title {
  font-family: Georgia, "Times New Roman", serif;
  color: var(--text);
}

.hero h1 {
  max-width: 900px;
  margin: 0;
  font-size: clamp(3rem, 7vw, 6.6rem);
  line-height: .98;
  letter-spacing: -.045em;
}

.hero-subtitle {
  max-width: 820px;
  margin: 1.8rem 0 0;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(1.3rem, 2.2vw, 1.85rem);
  line-height: 1.4;
  color: #45433e;
}

.lede {
  max-width: 780px;
  margin: 1.5rem 0 0;
  color: var(--muted);
  font-size: 1.05rem;
}

.button-row {
  display: flex;
  flex-wrap: wrap;
  gap: .75rem;
  margin-top: 2rem;
}

.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.8rem;
  padding: .65rem 1rem;
  border: 1px solid var(--accent);
  border-radius: .35rem;
  background: var(--accent);
  color: white;
  font-weight: 650;
  text-decoration: none;
}

.button:hover {
  background: var(--accent-dark);
  color: white;
}

.button.secondary {
  background: transparent;
  color: var(--accent);
}

.button.secondary:hover {
  background: var(--accent-soft);
}

.stats {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 1px;
  margin-top: 3.5rem;
  border: 1px solid var(--border);
  background: var(--border);
}

.stat {
  min-height: 8.5rem;
  padding: 1.2rem;
  background: var(--surface);
}

.stat strong {
  display: block;
  margin-bottom: .35rem;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(1.65rem, 3vw, 2.45rem);
  line-height: 1;
}

.stat span {
  color: var(--muted);
  font-size: .87rem;
}

.section {
  padding: 5rem 0;
  border-bottom: 1px solid var(--border);
}

.section:last-child {
  border-bottom: 0;
}

.section h2 {
  max-width: 850px;
  margin: 0 0 1.4rem;
  font-size: clamp(1.65rem, 2.4vw, 2.15rem);
  line-height: 1.15;
  letter-spacing: -.015em;
}

.section-intro {
  max-width: 780px;
  margin: 0 0 2.4rem;
  color: var(--muted);
  font-size: 1.08rem;
}

.grid-2,
.grid-3,
.grid-4 {
  display: grid;
  gap: 1rem;
}

.grid-2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.grid-3 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.grid-4 {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.card {
  padding: 1.4rem;
  border: 1px solid var(--border);
  background: var(--surface);
}

.card h3 {
  margin: 0 0 .65rem;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1.35rem;
}

.card p:last-child {
  margin-bottom: 0;
}

.muted {
  color: var(--muted);
}

.callout {
  margin: 2rem 0;
  padding: 1.4rem 1.5rem;
  border-left: 4px solid var(--accent);
  background: var(--accent-soft);
}

.callout strong {
  font-family: Georgia, "Times New Roman", serif;
}

.pipeline {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: .65rem;
  margin-top: 2rem;
}

.pipeline-step {
  position: relative;
  min-height: 8.2rem;
  padding: 1rem;
  border: 1px solid var(--border);
  background: var(--surface);
}

.pipeline-step strong {
  display: block;
  margin-bottom: .4rem;
  color: var(--accent);
}

.pipeline-step span {
  color: var(--muted);
  font-size: .88rem;
}

.badges {
  display: flex;
  flex-wrap: wrap;
  gap: .5rem;
  margin: 1.3rem 0;
}

.badge {
  padding: .3rem .65rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--surface);
  font-size: .82rem;
  font-weight: 650;
}

.visual {
  margin: 2rem 0;
  padding: 1rem;
  border: 1px solid var(--border);
  background: var(--surface);
}

.visual img {
  display: block;
  width: 100%;
  height: auto;
}

.visual iframe {
  display: block;
  width: 100%;
  min-height: 720px;
  border: 0;
  background: white;
}

figure {
  margin: 0;
}

figcaption {
  padding: .9rem .2rem .2rem;
  color: var(--muted);
  font-size: .88rem;
}

table {
  width: 100%;
  margin: 1.5rem 0;
  border-collapse: collapse;
  background: var(--surface);
}

th,
td {
  padding: .7rem;
  border-bottom: 1px solid var(--border);
  text-align: left;
  vertical-align: top;
}

th {
  width: 28%;
}

code {
  padding: .12rem .3rem;
  border-radius: .2rem;
  background: #eeece6;
  overflow-wrap: anywhere;
}

pre {
  overflow-x: auto;
  padding: 1rem;
  border: 1px solid var(--border);
  background: #252522;
  color: #f6f4ef;
}

pre code {
  padding: 0;
  background: transparent;
}

details {
  margin: 1rem 0;
  padding: 1rem 1.2rem;
  border: 1px solid var(--border);
  background: var(--surface);
}

summary {
  cursor: pointer;
  font-weight: 700;
}

.note {
  padding: .9rem 1rem;
  background: var(--surface-soft);
  border-left: 4px solid #8b887f;
}

small {
  color: var(--muted);
}

.site-footer {
  border-top: 1px solid var(--border);
  background: #efede7;
}

.footer-inner {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 2.5rem 1.5rem;
  display: flex;
  justify-content: space-between;
  gap: 2rem;
  color: var(--muted);
  font-size: .88rem;
}

.footer-links {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}


.result-block {
  margin: 3.5rem 0 5rem;
  padding-top: 2.5rem;
  border-top: 1px solid var(--border);
}

.result-block:first-of-type {
  margin-top: 1rem;
}

.result-header {
  margin-bottom: 1.7rem;
}

.result-label {
  display: inline-block;
  margin-bottom: .5rem;
  color: var(--accent);
  font-size: .76rem;
  font-weight: 800;
  letter-spacing: .1em;
  text-transform: uppercase;
}

.result-header h3 {
  max-width: 820px;
  margin: 0;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(1.7rem, 3.5vw, 2.8rem);
  line-height: 1.12;
}

.result-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(280px, .75fr);
  gap: 2rem;
  align-items: start;
}

.result-copy {
  padding-top: .4rem;
}

.result-copy p:first-child {
  margin-top: 0;
}

.metric-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1px;
  margin: 1.5rem 0;
  border: 1px solid var(--border);
  background: var(--border);
}

.metric-box {
  padding: 1rem;
  background: var(--surface);
}

.metric-box strong {
  display: block;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1.65rem;
}

.metric-box span {
  color: var(--muted);
  font-size: .82rem;
}

.comparison {
  margin: 2rem 0;
  border: 1px solid var(--border);
  background: var(--surface);
}

.comparison-row {
  display: grid;
  grid-template-columns: minmax(170px, .9fr) minmax(190px, 2fr) 90px;
  gap: 1rem;
  align-items: center;
  padding: .85rem 1rem;
  border-bottom: 1px solid var(--border);
}

.comparison-row:last-child {
  border-bottom: 0;
}

.comparison-name {
  font-weight: 650;
}

.bar-track {
  height: .7rem;
  overflow: hidden;
  border-radius: 999px;
  background: #e7e2d8;
}

.bar-fill {
  height: 100%;
  border-radius: inherit;
  background: var(--accent);
}

.comparison-value {
  text-align: right;
  font-variant-numeric: tabular-nums;
  font-weight: 700;
}

.kg-diagram {
  margin: 2rem 0;
  padding: 2rem;
  border: 1px solid var(--border);
  background: var(--surface);
}

.kg-row {
  display: grid;
  grid-template-columns: minmax(150px, 1fr) minmax(120px, .7fr)
                       minmax(170px, 1fr) minmax(120px, .7fr)
                       minmax(170px, 1fr);
  gap: .6rem;
  align-items: center;
  margin: .8rem 0;
}

.kg-node {
  padding: .85rem;
  border: 1px solid var(--border);
  background: var(--surface-soft);
  text-align: center;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: .85rem;
  font-weight: 700;
}

.kg-edge {
  color: var(--muted);
  text-align: center;
  font-size: .76rem;
}

.tech-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1px;
  margin: 2rem 0;
  border: 1px solid var(--border);
  background: var(--border);
}

.tech-stat {
  min-height: 8rem;
  padding: 1.2rem;
  background: var(--surface);
}

.tech-stat strong {
  display: block;
  margin-bottom: .4rem;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1.8rem;
}

.tech-stat span {
  color: var(--muted);
  font-size: .85rem;
}

.star-list {
  margin: 2rem 0;
  border: 1px solid var(--border);
  background: var(--surface);
}

.star-row {
  display: grid;
  grid-template-columns: 130px 1fr;
  gap: 1.3rem;
  align-items: start;
  padding: 1.2rem;
  border-bottom: 1px solid var(--border);
}

.star-row:last-child {
  border-bottom: 0;
}

.star-symbol {
  color: var(--accent);
  font-size: 1.1rem;
  letter-spacing: .05em;
  white-space: nowrap;
}

.star-copy strong {
  display: block;
  margin-bottom: .2rem;
}

.demo-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  margin: 2rem 0;
}

.demo-card {
  display: block;
  padding: 1.3rem;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  text-decoration: none;
}

.demo-card:hover {
  border-color: var(--accent);
  background: var(--accent-soft);
  color: var(--text);
}

.demo-card strong {
  display: block;
  margin-bottom: .4rem;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1.2rem;
}

.demo-card code {
  font-size: .76rem;
}

.limit-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 1px;
  margin: 2rem 0;
  border: 1px solid var(--border);
  background: var(--border);
}

.limit-item {
  padding: 1.1rem;
  background: var(--surface);
}

.limit-item strong {
  display: block;
  margin-bottom: .4rem;
  font-family: Georgia, "Times New Roman", serif;
}

.limit-item span {
  color: var(--muted);
  font-size: .84rem;
}

.repro-flow {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: .5rem;
  margin: 2rem 0;
}

.repro-step {
  padding: 1rem .7rem;
  border: 1px solid var(--border);
  background: var(--surface);
  text-align: center;
  font-size: .82rem;
}

.repro-step strong {
  display: block;
  margin-bottom: .25rem;
  color: var(--accent);
}

.conclusion {
  margin-top: 3rem;
  padding: 2rem;
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(1.3rem, 2.5vw, 2rem);
  line-height: 1.45;
}

@media (max-width: 800px) {
  .result-grid,
  .demo-grid {
    grid-template-columns: 1fr;
  }

  .tech-stats,
  .limit-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .repro-flow {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .kg-row {
    grid-template-columns: 1fr;
  }

  .kg-edge {
    padding: .2rem 0;
  }
}

@media (max-width: 560px) {
  .metric-strip,
  .tech-stats,
  .limit-grid,
  .repro-flow {
    grid-template-columns: 1fr;
  }

  .comparison-row {
    grid-template-columns: 1fr;
  }

  .comparison-value {
    text-align: left;
  }
}

@media (max-width: 980px) {
  .stats {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .pipeline {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .grid-4 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .nav-shell {
    align-items: flex-start;
    flex-direction: column;
    gap: .65rem;
  }

  .nav-links {
    justify-content: flex-start;
  }
}

@media (max-width: 680px) {
  .hero {
    padding-top: 4rem;
  }

  .stats,
  .grid-2,
  .grid-3,
  .grid-4,
  .pipeline {
    grid-template-columns: 1fr;
  }

  .nav-links {
    display: none;
  }

  .visual iframe {
    min-height: 560px;
  }

  .footer-inner {
    flex-direction: column;
  }
}
""".strip()
        + "\n",
    )

    # Linked Data distributions
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

    # Visualizzazioni selezionate per la relazione Web
    visualization_files = [
        "library_map.html",
        "status_by_region.png",
        "status_distribution.png",
        "demography_scatter.png",
        "special_collections.png",
        "problematic_holdings.png",
        "mergers_network.png",
        "age65_scatter.png",
    ]

    for filename in visualization_files:
        copy_file(
            ROOT / "visualizations" / filename,
            DOCS / "visualizations" / filename,
        )

def build_main_pages() -> None:
    write(
        DOCS / "index.html",
        page(
            "Biblioteche Fantasma — Linked Open Data",
            f"""
<section class="hero" id="overview">

<p class="eyebrow">
Open Data Management · Linked Open Data · Knowledge Graph
</p>

<h1>Biblioteche<br>Fantasma</h1>

<p class="hero-subtitle">
Analisi, integrazione e pubblicazione Linked Open Data
delle biblioteche italiane non pienamente operative.
</p>

<p class="lede">
Il progetto integra lo snapshot dell'Anagrafe delle biblioteche
italiane ICCU con i dati demografici ISTAT POSAS 2019–2025,
trasformando sorgenti eterogenee in un dataset analitico,
un knowledge graph RDF validato e una pubblicazione Web
interconnessa con risorse esterne.
</p>

<div class="button-row">
  <a class="button" href="visualizations/library_map.html">
    Esplora la mappa
  </a>

  <a class="button secondary" href="ontology/">
    Esplora il Knowledge Graph
  </a>

  <a class="button secondary" href="{RDF_DATA_DOWNLOAD_URL}">
    Scarica data.ttl
  </a>
</div>

<div class="stats">

  <div class="stat">
    <strong>19.611</strong>
    <span>record nello snapshot ICCU</span>
  </div>

  <div class="stat">
    <strong>18.956</strong>
    <span>biblioteche nel denominatore analitico</span>
  </div>

  <div class="stat">
    <strong>2.497</strong>
    <span>biblioteche nel perimetro problematico</span>
  </div>

  <div class="stat">
    <strong>13,17%</strong>
    <span>quota problematica</span>
  </div>

  <div class="stat">
    <strong>1.656.407</strong>
    <span>triple RDF esplicite validate</span>
  </div>

  <div class="stat">
    <strong>27.507</strong>
    <span>pagine Web per entità core</span>
  </div>

</div>
</section>


<section class="section" id="problema">

<p class="section-kicker">01 · Il problema di ricerca</p>

<h2>Che cosa significa davvero “Biblioteca Fantasma”?</h2>

<p class="section-intro">
“Biblioteche Fantasma” è un'etichetta narrativa del progetto:
non è una categoria amministrativa ufficiale ICCU.
L'obiettivo non è trasformare ogni anomalia in una generica
“biblioteca chiusa”, ma distinguere condizioni operative,
amministrative e documentarie diverse.
</p>

<div class="grid-3">

  <article class="card">
    <h3>1.827</h3>
    <p>Biblioteche non più esistenti</p>
  </article>

  <article class="card">
    <h3>619</h3>
    <p>Temporaneamente chiuse</p>
  </article>

  <article class="card">
    <h3>33</h3>
    <p>Depositi senza punto di servizio</p>
  </article>

  <article class="card">
    <h3>12</h3>
    <p>Servizi sospesi a causa del sisma</p>
  </article>

  <article class="card">
    <h3>4</h3>
    <p>Biblioteche inagibili</p>
  </article>

  <article class="card">
    <h3>2</h3>
    <p>Riapertura o agibilità parziale</p>
  </article>

</div>

<div class="callout">
  <strong>Una distinzione fondamentale.</strong>
  L'assenza di uno stato speciale nel record ICCU non certifica
  che la biblioteca sia pienamente operativa.
  Per questo il progetto usa la categoria neutra
  <code>NESSUNO_STATO_SPECIALE_REGISTRATO</code>.
</div>

<p class="muted">
Sono invece mantenuti distinti dal perimetro principale fenomeni
come confluenza, non-censimento e allestimento, perché descrivono
trasformazioni o condizioni anagrafiche differenti.
</p>

</section>


<section class="section" id="fonti">

<p class="section-kicker">02 · Fonti e provenance</p>

<h2>Tre livelli di informazione, una sola pipeline</h2>

<p class="section-intro">
Le sorgenti non hanno la stessa granularità, struttura o funzione.
L'integrazione richiede quindi identificatori stabili,
regole temporali e provenance esplicita.
</p>

<div class="grid-3">

  <article class="card">
    <h3>ICCU</h3>

    <p>
      Anagrafe delle biblioteche italiane.
      È la fonte principale per identificazione ISIL,
      denominazione, localizzazione, stato,
      tipologie e informazioni bibliografiche accessorie.
    </p>

    <p class="muted">
      Snapshot analizzato: 8 settembre 2026.<br>
      Licenza sorgente: CC0.
    </p>
  </article>

  <article class="card">
    <h3>ISTAT POSAS</h3>

    <p>
      Popolazione residente per comune,
      utilizzata per confrontare il territorio
      nel 2019 e nel 2025 e per costruire indicatori
      demografici e struttura per età.
    </p>

    <p class="muted">
      Geografia analitica: 2025.<br>
      Licenza sorgente: CC BY 4.0.
    </p>
  </article>

  <article class="card">
    <h3>Cultural-ON e standard RDF</h3>

    <p>
      Il knowledge graph riusa ontologie e vocabolari esistenti
      invece di ridefinire concetti già disponibili.
    </p>

    <div class="badges">
      <span class="badge">Cultural-ON</span>
      <span class="badge">SKOS</span>
      <span class="badge">PROV-O</span>
      <span class="badge">GeoSPARQL</span>
      <span class="badge">DCAT</span>
    </div>
  </article>

</div>

<div class="callout">
  <strong>Integrazione, non semplice concatenazione.</strong>
  ICCU descrive istituzioni culturali; ISTAT descrive popolazione
  e territorio. Collegare le due sorgenti significa riconciliare
  identificatori, temporalità e variazioni amministrative,
  non soltanto eseguire un join tra file.
</div>

</section>


<section class="section" id="metodo">

<p class="section-kicker">03 · Pipeline</p>

<h2>Dal dato grezzo alla pubblicazione Linked Data sul Web</h2>

<p class="section-intro">
L'intero processo è riproducibile.
La pipeline conserva le sorgenti originali, produce dataset
normalizzati e termina con validazione, analisi e pubblicazione.
</p>

<div class="pipeline">

  <div class="pipeline-step">
    <strong>01 · Raw Data</strong>
    <span>ICCU + ISTAT POSAS 2019/2025</span>
  </div>

  <div class="pipeline-step">
    <strong>02 · Cleaning</strong>
    <span>stati, coordinate, missing e normalizzazione</span>
  </div>

  <div class="pipeline-step">
    <strong>03 · Integration</strong>
    <span>ISIL, codici ISTAT e crosswalk territoriale</span>
  </div>

  <div class="pipeline-step">
    <strong>04 · Metadata</strong>
    <span>licenze, provenance, DCAT e URI policy</span>
  </div>

  <div class="pipeline-step">
    <strong>05 · RDF</strong>
    <span>ontologia e knowledge graph</span>
  </div>

  <div class="pipeline-step">
    <strong>06 · Interlinking</strong>
    <span>ICCU e Linked ISPRA</span>
  </div>

  <div class="pipeline-step">
    <strong>07 · Validation</strong>
    <span>controlli RDF e SHACL</span>
  </div>

  <div class="pipeline-step">
    <strong>08 · SPARQL</strong>
    <span>competency questions su PyOxigraph</span>
  </div>

  <div class="pipeline-step">
    <strong>09 · Analysis</strong>
    <span>RQ1–RQ8 e sensitivity analysis</span>
  </div>

  <div class="pipeline-step">
    <strong>10 · Web</strong>
    <span>visualizzazioni, URI HTTPS e GitHub Pages</span>
  </div>

</div>

<div class="button-row">
  <a
    class="button secondary"
    href="{GITHUB_REPO}/blob/main/scripts/rebuild_all.py"
  >
    Vedi la pipeline riproducibile
  </a>
</div>

</section>


<section class="section" id="cleaning">

<p class="section-kicker">04 · Data cleaning</p>

<h2>Le decisioni che cambiano il significato dei risultati</h2>

<p class="section-intro">
La qualità del progetto dipende soprattutto da ciò che
non viene assunto automaticamente.
Le trasformazioni più importanti sono documentate
come decisioni esplicite e riproducibili.
</p>

<div class="grid-2">

  <article class="card">
    <h3>NULL ≠ biblioteca aperta</h3>
    <p>
      Un campo stato vuoto viene trasformato nella categoria
      neutra <code>NESSUNO_STATO_SPECIALE_REGISTRATO</code>.
      Non viene interpretato come prova di apertura.
    </p>
  </article>

  <article class="card">
    <h3>655 record fuori dal denominatore</h3>
    <p>
      Gli “altri istituti collegati ad attività dell'ICCU”
      sono conservati nel dataset, ma esclusi dal denominatore
      principale delle biblioteche.
    </p>
  </article>

  <article class="card">
    <h3>Geografia 2019 → 2025</h3>
    <p>
      Il confronto demografico usa una geografia analitica 2025
      e un crosswalk esplicito dei cambi amministrativi,
      evitando join fuzzy sui nomi dei comuni.
    </p>
  </article>

  <article class="card">
    <h3>Missing ≠ zero</h3>
    <p>
      L'assenza di quantità patrimoniali o record di fondi speciali
      viene mantenuta come informazione mancante,
      non trasformata artificialmente in zero.
    </p>
  </article>

</div>

<div class="callout">
  <strong>Il caso Trapani / Misiliscemi.</strong>
  Misiliscemi nasce dallo scorporo territoriale di Trapani nel 2021.
  I dati comunali POSAS 2019 non permettono di ricostruire
  correttamente la popolazione dei due territori secondo
  i confini 2025. Per questo entrambi sono marcati
  come non comparabili nel confronto 2019–2025,
  invece di introdurre una stima inventata.
</div>

<p class="muted">
Queste decisioni sono registrate nel
<a href="{GITHUB_REPO}/blob/main/reports/decisions_log.md">
decisions log
</a>
del progetto.
</p>

</section>


<section class="section" id="risultati">

<p class="section-kicker">05 · Risultati</p>

<h2>Le Research Questions, dai dati all'interpretazione</h2>

<p class="section-intro">
I risultati non vengono letti soltanto attraverso conteggi e
significatività statistica. Ogni analisi distingue denominatore,
copertura informativa, robustezza e limiti interpretativi.
</p>


<div class="result-block">

  <div class="result-header">
    <span class="result-label">RQ1 · Distribuzione territoriale</span>
    <h3>Il fenomeno è nazionale, ma quota e numerosità raccontano storie diverse</h3>
  </div>

  <figure class="visual">
    <iframe
      src="visualizations/library_map.html"
      title="Mappa interattiva delle biblioteche problematiche"
      loading="lazy"
    ></iframe>

    <figcaption>
      Mappa interattiva delle biblioteche nel perimetro problematico.
      I marker sono raggruppati tramite clustering e possono essere
      filtrati per stato ICCU.
    </figcaption>
  </figure>

  <div class="button-row">
    <a
      class="button secondary"
      href="visualizations/library_map.html"
    >
      Apri la mappa a schermo intero
    </a>
  </div>

  <div class="result-grid">

    <figure class="visual">
      <img
        src="visualizations/status_by_region.png"
        alt="Quota di biblioteche problematiche per regione"
        loading="lazy"
      >
      <figcaption>
        Quota regionale di biblioteche problematiche con
        conteggio problematiche/totale.
      </figcaption>
    </figure>

    <div class="result-copy">

      <p>
        Il Molise registra la quota regionale più elevata:
        <strong>43,72%</strong>, cioè 80 biblioteche problematiche
        su 183. La Liguria raggiunge il 31,81%.
      </p>

      <p>
        In valore assoluto, invece, il massimo è in Lombardia:
        <strong>366 casi</strong>. Una regione con molti istituti
        ha più opportunità di produrre un conteggio elevato,
        anche senza avere la quota maggiore.
      </p>

      <div class="metric-strip">

        <div class="metric-box">
          <strong>43,72%</strong>
          <span>Molise · 80/183</span>
        </div>

        <div class="metric-box">
          <strong>31,81%</strong>
          <span>Liguria · 209/657</span>
        </div>

        <div class="metric-box">
          <strong>366</strong>
          <span>Lombardia · massimo assoluto</span>
        </div>

      </div>

      <div class="callout">
        <strong>Messaggio metodologico.</strong>
        Un conteggio assoluto e una proporzione non sono
        intercambiabili. La lettura territoriale deve sempre
        dichiarare il denominatore.
      </div>

    </div>
  </div>

</div>


<div class="result-block">

  <div class="result-header">
    <span class="result-label">RQ2 · Stati ICCU</span>
    <h3>Non esiste un'unica categoria di “biblioteca chiusa”</h3>
  </div>

  <div class="result-grid">

    <figure class="visual">
      <img
        src="visualizations/status_distribution.png"
        alt="Distribuzione degli stati ICCU normalizzati"
        loading="lazy"
      >
      <figcaption>
        Distribuzione degli stati normalizzati nello snapshot ICCU.
      </figcaption>
    </figure>

    <div class="result-copy">

      <p>
        Il gruppo numericamente maggiore è costituito da
        <strong>13.200 record senza uno stato speciale registrato</strong>.
        Seguono 1.827 biblioteche non più esistenti,
        1.723 non censite e 1.502 confluite.
      </p>

      <p>
        Le confluenze non vengono conteggiate come cessazioni:
        rappresentano una trasformazione organizzativa.
        Analogamente, il non-censimento descrive una condizione
        anagrafica e non prova una chiusura.
      </p>

      <div class="callout">
        <strong>13.200 non significa “13.200 aperte”.</strong>
        L'assenza di uno stato speciale è assenza di informazione
        positiva su quello stato, non una certificazione
        di piena operatività.
      </div>

    </div>
  </div>

</div>


<div class="result-block">

  <div class="result-header">
    <span class="result-label">RQ3 · Tipologie</span>
    <h3>La significatività statistica non coincide con una forte associazione</h3>
  </div>

  <p>
    L'analisi finale utilizza le tipologie presenti nel master ICCU
    e mantiene lo stesso denominatore analitico di
    <strong>18.956 biblioteche</strong>.
    La categoria <code>NON SPECIFICATA</code> è fortemente associata
    al perimetro problematico e influenza il risultato complessivo.
  </p>

  <div class="comparison">

    <div class="comparison-row">
      <div class="comparison-name">
        Funzionale · tutte le categorie
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="width:100%"></div>
      </div>
      <div class="comparison-value">V = 0,196</div>
    </div>

    <div class="comparison-row">
      <div class="comparison-name">
        Funzionale · senza NON SPECIFICATA
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="width:39%"></div>
      </div>
      <div class="comparison-value">V = 0,077</div>
    </div>

    <div class="comparison-row">
      <div class="comparison-name">
        Amministrativa · tutte le categorie
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="width:98%"></div>
      </div>
      <div class="comparison-value">V = 0,193</div>
    </div>

    <div class="comparison-row">
      <div class="comparison-name">
        Amministrativa · senza NON SPECIFICATA
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="width:49%"></div>
      </div>
      <div class="comparison-value">V = 0,095</div>
    </div>

  </div>

  <div class="callout">
    <strong>Sensitivity analysis.</strong>
    Quando viene rimossa la categoria non informativa
    <code>NON SPECIFICATA</code>, l'associazione residua
    diventa debole. Il p-value da solo non descrive
    l'importanza sostantiva dell'effetto.
  </div>

</div>


<div class="result-block">

  <div class="result-header">
    <span class="result-label">RQ4 · Demografia</span>
    <h3>La perdita di popolazione mostra soltanto un'associazione debole</h3>
  </div>

  <div class="result-grid">

    <figure class="visual">
      <img
        src="visualizations/demography_scatter.png"
        alt="Variazione demografica e quota di biblioteche problematiche"
        loading="lazy"
      >
      <figcaption>
        Variazione della popolazione 2019–2025 e quota
        di biblioteche problematiche nei comuni comparabili.
      </figcaption>
    </figure>

    <div class="result-copy">

      <div class="metric-strip">

        <div class="metric-box">
          <strong>6.659</strong>
          <span>comuni analizzati</span>
        </div>

        <div class="metric-box">
          <strong>−0,106</strong>
          <span>Pearson r</span>
        </div>

        <div class="metric-box">
          <strong>−0,067</strong>
          <span>Spearman ρ</span>
        </div>

      </div>

      <p>
        I coefficienti indicano una relazione negativa,
        ma di ampiezza molto ridotta.
      </p>

      <p>
        Inoltre, aumentando il numero minimo di biblioteche
        richiesto per includere un comune, il segno e
        l'ampiezza della relazione non rimangono stabili.
      </p>

      <div class="callout">
        <strong>Correlazione ≠ causalità.</strong>
        Lo spopolamento può essere parte del contesto territoriale,
        ma questi dati non dimostrano che provochi
        la condizione delle biblioteche.
      </div>

    </div>
  </div>

</div>


<div class="result-block">

  <div class="result-header">
    <span class="result-label">RQ5 · Patrimonio e fondi speciali</span>
    <h3>Il risultato principale è un problema di copertura informativa</h3>
  </div>

  <div class="result-grid">

    <figure class="visual">
      <img
        src="visualizations/special_collections.png"
        alt="Copertura di patrimonio e fondi speciali"
        loading="lazy"
      >
      <figcaption>
        Copertura documentaria nel sottoinsieme delle biblioteche
        appartenenti al perimetro problematico.
      </figcaption>
    </figure>

    <div class="result-copy">

      <p>
        Soltanto <strong>627 delle 2.497</strong> biblioteche
        problematiche possiedono almeno una riga di patrimonio
        nel dataset secondario.
      </p>

      <p>
        Le 2.828 righe disponibili includono
        <strong>461 quantità mancanti</strong>.
        La somma delle quantità positive note è 7.500.259,
        ma non rappresenta un inventario complessivo.
      </p>

      <p>
        Nessuna biblioteca problematica compare nel dataset
        dei fondi speciali. Questo significa
        <strong>assenza di record nel sottoinsieme</strong>,
        non prova dell'assenza reale di fondi.
      </p>

    </div>
  </div>

  <details>
    <summary>
      Approfondisci: quali materiali sono documentati?
    </summary>

    <figure class="visual">
      <img
        src="visualizations/problematic_holdings.png"
        alt="Materiali documentati nelle biblioteche problematiche"
        loading="lazy"
      >
      <figcaption>
        Conteggio delle biblioteche problematiche per tipologia
        di materiale documentato. Le quantità mancanti non vengono
        trattate come zero.
      </figcaption>
    </figure>
  </details>

</div>


<div class="result-block">

  <div class="result-header">
    <span class="result-label">RQ7 · Confluenze</span>
    <h3>“Sparire” dall'anagrafe può significare trasformazione istituzionale</h3>
  </div>

  <div class="result-grid">

    <figure class="visual">
      <img
        src="visualizations/mergers_network.png"
        alt="Rete delle confluenze bibliotecarie"
        loading="lazy"
      >
      <figcaption>
        Componente debole maggiore della rete delle confluenze.
        La rete completa non viene mostrata per evitare
        uno spaghetti chart.
      </figcaption>
    </figure>

    <div class="result-copy">

      <div class="metric-strip">

        <div class="metric-box">
          <strong>1.412</strong>
          <span>archi validati</span>
        </div>

        <div class="metric-box">
          <strong>1.821</strong>
          <span>nodi</span>
        </div>

        <div class="metric-box">
          <strong>410</strong>
          <span>componenti deboli</span>
        </div>

      </div>

      <p>
        La componente maggiore contiene 40 nodi.
        Il target con grado entrante più elevato è
        <code>IT-CT0337</code>, con 39 archi in ingresso.
      </p>

      <p>
        La relazione <code>bf:mergedInto</code> descrive
        una riorganizzazione osservata nello snapshot:
        non deve essere interpretata automaticamente
        come una chiusura.
      </p>

    </div>
  </div>

</div>


<details>

  <summary>
    RQ8 · Analisi secondaria: quota di popolazione 65+
  </summary>

  <div class="result-grid">

    <figure class="visual">
      <img
        src="visualizations/age65_scatter.png"
        alt="Quota over 65 e biblioteche problematiche"
        loading="lazy"
      >
      <figcaption>
        Quota di popolazione 65+ e quota problematica nei comuni.
      </figcaption>
    </figure>

    <div class="result-copy">
      <p>
        Su 6.659 comuni, Pearson è <strong>0,1454</strong>
        e Spearman <strong>0,1054</strong>.
      </p>

      <p>
        L'associazione è positiva ma debole e viene mantenuta
        come risultato descrittivo secondario, senza
        interpretazione causale.
      </p>
    </div>

  </div>

</details>

</section>


<section class="section" id="knowledge-graph">

<p class="section-kicker">06 · Ontologia e Knowledge Graph</p>

<h2>Dal dato tabellare a un modello semantico interrogabile</h2>

<p class="section-intro">
Il knowledge graph identifica biblioteche, sedi, comuni,
osservazioni di stato, demografia e patrimonio tramite URI
persistenti e collega le entità attraverso proprietà esplicite.
</p>

<div class="kg-diagram">

  <div class="kg-row">
    <div class="kg-node">cis:Library</div>
    <div class="kg-edge">cis:hasSite →</div>
    <div class="kg-node">cis:Site</div>
    <div class="kg-edge">cis:hasGeographicalLocation →</div>
    <div class="kg-node">bf:Municipality</div>
  </div>

  <div class="kg-row">
    <div class="kg-node">cis:Library</div>
    <div class="kg-edge">bf:hasStatusObservation →</div>
    <div class="kg-node">bf:LibraryStatusObservation</div>
    <div class="kg-edge">bf:hasStatus →</div>
    <div class="kg-node">skos:Concept</div>
  </div>

  <div class="kg-row">
    <div class="kg-node">bf:Municipality</div>
    <div class="kg-edge">← bf:observedMunicipality</div>
    <div class="kg-node">bf:DemographicObservation</div>
    <div class="kg-edge"></div>
    <div class="kg-node">2019 / 2025</div>
  </div>

  <div class="kg-row">
    <div class="kg-node">cis:Library</div>
    <div class="kg-edge">→</div>
    <div class="kg-node">bf:HoldingObservation</div>
    <div class="kg-edge">/</div>
    <div class="kg-node">bf:SpecialCollection</div>
  </div>

</div>

<div class="badges">
  <span class="badge">Cultural-ON</span>
  <span class="badge">SKOS</span>
  <span class="badge">PROV-O</span>
  <span class="badge">GeoSPARQL</span>
  <span class="badge">LOCN</span>
  <span class="badge">DCAT</span>
</div>

<div class="button-row">

  <a class="button secondary" href="ontology/">
    Esplora l'ontologia
  </a>

  <a
    class="button secondary"
    href="ontology/ontology.ttl"
  >
    Apri ontology.ttl
  </a>

</div>

</section>


<section class="section" id="scelte-semantiche">

<p class="section-kicker">07 · Scelte semantiche</p>

<h2>Quattro decisioni che evitano equivalenze sbagliate</h2>

<div class="grid-2">

  <article class="card">
    <h3>Lo stato è un'osservazione</h3>
    <p>
      Una biblioteca non viene definita ontologicamente
      “temporaneamente chiusa” per sempre.
      Lo stato è collegato a una
      <code>LibraryStatusObservation</code>
      riferita allo snapshot ICCU.
    </p>
  </article>

  <article class="card">
    <h3>Gli stati sono concetti SKOS</h3>
    <p>
      Gli stati costituiscono un vocabolario controllato.
      Non vengono trasformati in classi ontologiche
      di biblioteche.
    </p>
  </article>

  <article class="card">
    <h3>HoldingObservation ≠ Collection</h3>
    <p>
      Una riga del patrimonio descrive una consistenza
      osservata nello snapshot; non viene assimilata
      automaticamente a una collezione culturale.
    </p>
  </article>

  <article class="card">
    <h3>seeAlso ≠ sameAs</h3>
    <p>
      ICCU è collegato tramite <code>rdfs:seeAlso</code>
      perché il target è una pagina informativa.
      Per i comuni Linked ISPRA si usa invece
      <code>owl:sameAs</code> quando viene identificata
      la stessa entità amministrativa.
    </p>
  </article>

</div>

<div class="callout">
  <strong>Principio generale.</strong>
  Nel Linked Data la precisione delle relazioni è parte
  della qualità del dato: collegare due URI non significa
  necessariamente dichiararle identiche.
</div>

</section>


<section class="section" id="validazione">

<p class="section-kicker">08 · SPARQL, SHACL e validazione</p>

<h2>Il grafo non è soltanto generato: viene verificato e interrogato</h2>

<div class="tech-stats">

  <div class="tech-stat">
    <strong>1.656.407</strong>
    <span>triple esplicite caricate nello store</span>
  </div>

  <div class="tech-stat">
    <strong>11 / 11</strong>
    <span>query SPARQL eseguite</span>
  </div>

  <div class="tech-stat">
    <strong>Conforms: YES</strong>
    <span>validazione SHACL</span>
  </div>

  <div class="tech-stat">
    <strong>0</strong>
    <span>violazioni SHACL</span>
  </div>

</div>

<p>
Le competency questions vengono eseguite localmente su
<strong>PyOxigraph</strong>, un triplestore embedded.
La scelta rende la pipeline riproducibile senza richiedere
un server SPARQL esterno.
</p>

<details>

  <summary>
    Esempio SPARQL: biblioteche temporaneamente chiuse nel Lazio
  </summary>

<pre><code>PREFIX cis: &lt;http://dati.beniculturali.it/cis/&gt;
PREFIX bf: &lt;https://ameliamorsellino.github.io/biblioteche-fantasma/ontology/&gt;
PREFIX dct: &lt;http://purl.org/dc/terms/&gt;
PREFIX rdfs: &lt;http://www.w3.org/2000/01/rdf-schema#&gt;

SELECT DISTINCT ?region ?library ?isil ?libraryName ?municipalityName
WHERE &#123;
  VALUES ?targetRegion &#123; "Lazio" &#125;

  ?library
      a cis:Library ;
      cis:ISILIdentifier ?isil ;
      rdfs:label ?libraryName ;
      cis:hasSite/cis:hasGeographicalLocation ?municipality ;
      bf:hasStatusObservation/bf:hasStatus ?status .

  ?municipality
      bf:regionName ?region ;
      rdfs:label ?municipalityName .

  ?status dct:identifier "TEMPORANEAMENTE_CHIUSA" .

  FILTER(
    LCASE(STR(?region)) = LCASE(STR(?targetRegion))
  )
&#125;</code></pre>

  <p>
    La query traduce direttamente una competency question
    in un percorso sul grafo:
    biblioteca → sede → comune e biblioteca →
    osservazione di stato → concetto di stato.
  </p>

  <p>
    <a
      href="{GITHUB_REPO}/blob/main/sparql/09_temporary_closed_by_region.rq"
    >
      Apri la query originale nel repository
    </a>
  </p>

</details>

<div class="callout">
  <strong>Una query con zero righe non è necessariamente un errore.</strong>
  La query sulle biblioteche inagibili con fondi speciali
  restituisce legittimamente un insieme vuoto nello snapshot:
  il risultato descrive la copertura dei dati disponibili.
</div>

</section>


<section class="section" id="linked-data">

<p class="section-kicker">09 · Linked Open Data</p>

<h2>Dalle cinque stelle teoriche a una pubblicazione Web reale</h2>

<p class="section-intro">
La versione finale utilizza URI HTTPS pubbliche,
distribuzioni RDF accessibili sul Web e collegamenti
verso dataset esterni.
</p>

<div class="star-list">

  <div class="star-row">
    <div class="star-symbol">★</div>
    <div class="star-copy">
      <strong>Open license + Web</strong>
      Il dataset derivato è pubblicato sul Web con licenza
      compatibile con il riuso e attribuzione.
    </div>
  </div>

  <div class="star-row">
    <div class="star-symbol">★★</div>
    <div class="star-copy">
      <strong>Dati strutturati</strong>
      CSV, RDF e metadati sono machine-readable.
    </div>
  </div>

  <div class="star-row">
    <div class="star-symbol">★★★</div>
    <div class="star-copy">
      <strong>Formati non proprietari</strong>
      CSV e RDF/Turtle non dipendono da software proprietario.
    </div>
  </div>

  <div class="star-row">
    <div class="star-symbol">★★★★</div>
    <div class="star-copy">
      <strong>URI HTTP(S) per identificare le risorse</strong>
      Biblioteche e comuni utilizzano URI pubbliche sotto
      <code>{PUBLIC_BASE}</code>.
    </div>
  </div>

  <div class="star-row">
    <div class="star-symbol">★★★★★</div>
    <div class="star-copy">
      <strong>Link verso altri dati</strong>
      Le risorse locali sono collegate a ICCU e Linked ISPRA
      tramite relazioni RDF esplicite.
    </div>
  </div>

</div>

<div class="metric-strip">

  <div class="metric-box">
    <strong>19.611 / 19.611</strong>
    <span>biblioteche → ICCU · rdfs:seeAlso</span>
  </div>

  <div class="metric-box">
    <strong>7.893 / 7.896</strong>
    <span>comuni → Linked ISPRA · owl:sameAs</span>
  </div>

  <div class="metric-box">
    <strong>27.504</strong>
    <span>triple nel grafo di interlinking</span>
  </div>

</div>

<div class="callout">
  <strong>Un endpoint SPARQL pubblico non è una “sesta stella”.</strong>
  Il modello 5-star richiede identificatori Web e collegamenti
  verso altri dati, non l'esposizione obbligatoria
  di un endpoint SPARQL.
</div>

<p class="muted">
GitHub Pages è un hosting statico: non implementa content negotiation
HTTP completa e non tutte le risorse interne del grafo dispongono
di una pagina HTML dedicata. Le entità core biblioteca/comune
sono invece pubblicate come pagine Web dereferenziabili,
mentre il grafo RDF completo è distribuito tramite GitHub Release.
</p>

</section>


<section class="section" id="esplora">

<p class="section-kicker">10 · Esplora i dati</p>

<h2>Una demo del Linked Data, non soltanto una descrizione</h2>

<p class="section-intro">
Le risorse seguenti consentono di passare direttamente
dalla relazione Web alle rappresentazioni pubblicate,
all'ontologia e alle distribuzioni RDF.
</p>

<div class="demo-grid">

  <a
    class="demo-card"
    href="resource/library/IT-RM0267/"
  >
    <strong>Biblioteca reale</strong>
    Biblioteca nazionale centrale — Roma
    <br>
    <code>IT-RM0267</code>
  </a>

  <a
    class="demo-card"
    href="resource/municipality/058091/"
  >
    <strong>Comune</strong>
    Roma
    <br>
    <code>058091</code>
  </a>

  <a class="demo-card" href="ontology/ontology.ttl">
    <strong>Ontologia Turtle</strong>
    Classi, proprietà e riuso semantico
    <br>
    <code>ontology.ttl</code>
  </a>

  <a
    class="demo-card"
    href="distribution/links.ttl"
  >
    <strong>Interlinking RDF</strong>
    Collegamenti ICCU e Linked ISPRA
    <br>
    <code>links.ttl</code>
  </a>

  <a
    class="demo-card"
    href="metadata/dataset/"
  >
    <strong>Metadati</strong>
    Dataset e distribuzioni
    <br>
    <code>DCAT</code>
  </a>

  <a
    class="demo-card"
    href="{RDF_DATA_DOWNLOAD_URL}"
  >
    <strong>Knowledge Graph completo</strong>
    Distribuzione RDF versionata
    <br>
    <code>data.ttl</code>
  </a>

</div>

</section>


<section class="section" id="limiti">

<p class="section-kicker">11 · Limiti</p>

<h2>Cosa questi dati non permettono di concludere</h2>

<div class="limit-grid">

  <div class="limit-item">
    <strong>Temporalità</strong>
    <span>
      Lo snapshot ICCU fotografa una data:
      non costituisce una serie storica completa.
    </span>
  </div>

  <div class="limit-item">
    <strong>Missingness</strong>
    <span>
      Assenza di stato, quantità o fondo speciale
      non equivale automaticamente a zero o assenza reale.
    </span>
  </div>

  <div class="limit-item">
    <strong>Causalità</strong>
    <span>
      Le associazioni demografiche sono osservazionali
      e non dimostrano meccanismi causali.
    </span>
  </div>

  <div class="limit-item">
    <strong>Geografia</strong>
    <span>
      Fusioni e variazioni territoriali rendono alcuni
      confronti 2019–2025 non direttamente ricostruibili.
    </span>
  </div>

  <div class="limit-item">
    <strong>Web statico</strong>
    <span>
      GitHub Pages non offre content negotiation completa
      né un endpoint SPARQL pubblico.
    </span>
  </div>

</div>

<div class="callout">
  <strong>“Biblioteche Fantasma” resta un'etichetta narrativa.</strong>
  Nessuna conclusione del progetto deve trasformarla
  in una categoria ufficiale ICCU.
</div>

</section>


<section class="section" id="riproducibilita">

<p class="section-kicker">12 · Riproducibilità</p>

<h2>Ogni livello della pubblicazione può essere rigenerato</h2>

<p class="section-intro">
Dati processati, RDF, interlinking, validazione,
query, analisi, visualizzazioni e sito Web
derivano da una pipeline versionata.
</p>

<pre><code>python scripts/rebuild_all.py</code></pre>

<div class="repro-flow">

  <div class="repro-step">
    <strong>01</strong>
    sorgenti raw
  </div>

  <div class="repro-step">
    <strong>02</strong>
    processing
  </div>

  <div class="repro-step">
    <strong>03</strong>
    RDF + validation
  </div>

  <div class="repro-step">
    <strong>04</strong>
    analysis + plots
  </div>

  <div class="repro-step">
    <strong>05</strong>
    GitHub Actions
  </div>

  <div class="repro-step">
    <strong>06</strong>
    Pages + Release
  </div>

</div>

<div class="grid-3">

  <article class="card">
    <h3>Version control</h3>
    <p>
      Codice, ontologia, metadati, query e risultati
      sono versionati nel repository Git.
    </p>
  </article>

  <article class="card">
    <h3>Integrità</h3>
    <p>
      <code>MANIFEST.sha256</code> registra gli hash
      degli artefatti versionati e della distribuzione RDF.
    </p>
  </article>

  <article class="card">
    <h3>Deploy</h3>
    <p>
      GitHub Actions rigenera la pubblicazione statica
      e la distribuisce tramite GitHub Pages.
    </p>
  </article>

</div>

<div class="button-row">

  <a class="button" href="{GITHUB_REPO}">
    Repository GitHub
  </a>

  <a
    class="button secondary"
    href="{GITHUB_REPO}/releases/tag/v1.0.0"
  >
    Release v1.0.0
  </a>

  <a
    class="button secondary"
    href="{GITHUB_REPO}/blob/main/MANIFEST.sha256"
  >
    MANIFEST.sha256
  </a>

</div>

<div class="conclusion">
Dalla sorgente Open Data alla risorsa Linked Data pubblicata sul Web:
il progetto conserva provenance, esplicita le decisioni di cleaning,
verifica il knowledge graph e rende le entità principali
esplorabili tramite URI HTTPS pubbliche.
</div>

</section>
""",
        ),
    )

    write(
        DOCS / "ontology/index.html",
        page(
            "Ontologia — Biblioteche Fantasma",
            f"""
<section class="section">
<p class="section-kicker">Knowledge Graph</p>

<h2>Ontologia Biblioteche Fantasma</h2>

<p class="section-intro">
Vocabolario locale del knowledge graph con riuso di Cultural-ON,
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

<p><a href="{SITE_BASE}">Torna alla pubblicazione</a></p>
</section>
""",
        ),
    )

    write(
        DOCS / "metadata/dataset/index.html",
        page(
            "Dataset — Biblioteche Fantasma",
            f"""
<section class="section">
<p class="section-kicker">Metadata</p>

<h2>Dataset Biblioteche Fantasma</h2>

<p>
Dataset derivato da Open Data ICCU e ISTAT,
corredato da metadati, knowledge graph RDF
e collegamenti verso dati esterni.
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

<p><a href="{SITE_BASE}">Torna alla pubblicazione</a></p>
</section>
""",
        ),
    )

    write(
        DOCS / "resource/dataset/biblioteche-fantasma/index.html",
        page(
            "Risorsa dataset — Biblioteche Fantasma",
            f"""
<section class="section">
<p class="section-kicker">Dataset resource</p>

<h2>Biblioteche Fantasma</h2>

<p>
Risorsa RDF che identifica il dataset Biblioteche Fantasma.
</p>

<table>
<tr>
  <th>URI</th>
  <td>
    <code>
      {PUBLIC_BASE}resource/dataset/biblioteche-fantasma
    </code>
  </td>
</tr>
<tr>
  <th>Metadati</th>
  <td>
    <a href="../../../metadata/dataset/">
      Dataset metadata
    </a>
  </td>
</tr>
<tr>
  <th>Knowledge graph</th>
  <td>
    <a href="{RDF_DATA_DOWNLOAD_URL}">
      data.ttl
    </a>
  </td>
</tr>
</table>

<p><a href="{SITE_BASE}">Torna alla pubblicazione</a></p>
</section>
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

<p><a href="{SITE_BASE}">Torna alla pubblicazione</a></p>
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

<p><a href="{SITE_BASE}">Torna alla pubblicazione</a></p>
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
