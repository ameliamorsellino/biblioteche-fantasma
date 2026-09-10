#!/usr/bin/env python3
"""Generate the RDF knowledge graph for Biblioteche Fantasma.

Inputs are the processed CSV files produced from the original ICCU and ISTAT
raw archives. The script preserves the cleaning and integration decisions
already encoded in the processed datasets.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import unicodedata
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import quote

import pandas as pd
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef, XSD
from rdflib.namespace import DCTERMS, OWL, PROV, SKOS

DEV_BASE = "https://biblioteche-fantasma.invalid/"
ONTO = Namespace(DEV_BASE + "ontology/")
RES = Namespace(DEV_BASE + "resource/")
GRAPH = Namespace(DEV_BASE + "graph/")
CIS = Namespace("http://dati.beniculturali.it/cis/")
SCHEMA = Namespace("https://schema.org/")
LOCN = Namespace("http://www.w3.org/ns/locn#")
GEO = Namespace("http://www.opengis.net/ont/geosparql#")
DCAT = Namespace("http://www.w3.org/ns/dcat#")

ICCU_SNAPSHOT_DATE = "2026-09-08"
ICCU_SNAPSHOT_DATETIME = "2026-09-08T14:11:15"
PROJECT_RELEASE_DATE = "2026-09-10"
POSAS_2019_DATE = "2019-01-01"
POSAS_2025_DATE = "2025-01-01"


class StreamGraph:
    """Minimal write-only graph. Emits N-Triples syntax, which is valid Turtle."""
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.fh = path.open("w", encoding="utf-8", newline="\n")
        self.count = 0

    def bind(self, *args, **kwargs):
        return None

    @staticmethod
    def _term_nt(term):
        if isinstance(term, URIRef):
            # Generated/project IRIs are URI-safe; escape characters that N-Triples forbids.
            text = str(term)
            out = []
            for ch in text:
                cp = ord(ch)
                if ch in '<>\"{}|^`\\' or cp < 0x20:
                    out.append(f"\\u{cp:04X}" if cp <= 0xFFFF else f"\\U{cp:08X}")
                else:
                    out.append(ch)
            return '<' + ''.join(out) + '>'
        if isinstance(term, Literal):
            text = str(term)
            out = []
            for ch in text:
                cp = ord(ch)
                if ch == '\\': out.append('\\\\')
                elif ch == '"': out.append('\\"')
                elif ch == '\n': out.append('\\n')
                elif ch == '\r': out.append('\\r')
                elif ch == '\t': out.append('\\t')
                elif cp < 0x20 or cp == 0x7F:
                    out.append(f"\\u{cp:04X}")
                else: out.append(ch)
            suffix = ''
            if term.language:
                suffix = '@' + term.language
            elif term.datatype:
                suffix = '^^' + StreamGraph._term_nt(URIRef(term.datatype))
            return '"' + ''.join(out) + '"' + suffix
        raise TypeError(f"Unsupported RDF term for streaming serialization: {type(term)!r}")

    def add(self, triple):
        s, p, o = triple
        self.fh.write(f"{self._term_nt(s)} {self._term_nt(p)} {self._term_nt(o)} .\n")
        self.count += 1

    def close(self):
        self.fh.close()

    def __len__(self):
        return self.count


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def slugify(value: str) -> str:
    s = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "value"


def concept_uri(kind: str, value: str) -> URIRef:
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]
    return URIRef(str(RES) + f"{kind}/{slugify(value)}-{digest}")


def bind(g: Graph) -> None:
    for p, ns in [
        ("bf", ONTO), ("res", RES), ("cis", CIS), ("schema", SCHEMA),
        ("locn", LOCN), ("geo", GEO), ("dcat", DCAT),
        ("dct", DCTERMS), ("prov", PROV), ("skos", SKOS),
        ("owl", OWL), ("rdf", RDF), ("rdfs", RDFS), ("xsd", XSD),
    ]:
        g.bind(p, ns)


def add_it_label(g: Graph, s: URIRef, text: str, predicate=RDFS.label) -> None:
    if text:
        g.add((s, predicate, Literal(text, lang="it")))


def bool_lit(value: str):
    v = value.strip().casefold()
    if v in {"true", "1", "si", "sì", "yes"}:
        return Literal(True, datatype=XSD.boolean)
    if v in {"false", "0", "no"}:
        return Literal(False, datatype=XSD.boolean)
    return None


def int_lit(value: str):
    if value == "":
        return None
    try:
        d = Decimal(value)
    except InvalidOperation:
        return None
    if d != d.to_integral_value():
        return None
    return Literal(int(d), datatype=XSD.integer)


def dec_lit(value: str):
    if value == "":
        return None
    try:
        d = Decimal(value)
    except InvalidOperation:
        return None
    return Literal(str(d), datatype=XSD.decimal)


def add_concept(g: Graph, uri: URIRef, label: str, scheme: URIRef, broader: URIRef | None = None) -> None:
    g.add((uri, RDF.type, SKOS.Concept))
    g.add((uri, SKOS.inScheme, scheme))
    add_it_label(g, uri, label, SKOS.prefLabel)
    if broader:
        g.add((uri, SKOS.broader, broader))


def generate(data_dir: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    g = StreamGraph(out_dir / "data.ttl")
    mg = Graph()
    bind(g); bind(mg)

    # Source entities are defined in metadata.ttl and referenced from observations.
    src_iccu = RES["source/iccu-open-data-2026-09-08"]
    src_posas_2019 = RES["source/istat-posas-2019"]
    src_posas_2025 = RES["source/istat-posas-2025"]

    # --- Controlled concepts -------------------------------------------------
    status_scheme = RES["scheme/library-status"]
    status_group_scheme = RES["scheme/status-analytical-group"]
    functional_scheme = RES["scheme/library-functional-type"]
    administrative_scheme = RES["scheme/library-administrative-type"]
    material_scheme = RES["scheme/holding-material"]
    category_scheme = RES["scheme/holding-category"]
    collection_type_scheme = RES["scheme/special-collection-type"]
    for s, label in [
        (status_scheme, "Stati bibliotecari ICCU normalizzati"),
        (status_group_scheme, "Gruppi analitici degli stati"),
        (functional_scheme, "Tipologie funzionali di biblioteca"),
        (administrative_scheme, "Tipologie amministrative di biblioteca"),
        (material_scheme, "Tipologie di patrimonio bibliotecario"),
        (category_scheme, "Categorie di patrimonio bibliotecario"),
        (collection_type_scheme, "Tipologie di fondi speciali"),
    ]:
        g.add((s, RDF.type, SKOS.ConceptScheme)); add_it_label(g, s, label)

    status_df = read_csv(data_dir / "library_status.csv")
    group_uris: dict[str, URIRef] = {}
    status_uris: dict[str, URIRef] = {}
    for group in sorted(x for x in status_df["analytical_group"].unique() if x):
        u = RES[f"status-group/{slugify(group)}"]
        group_uris[group] = u
        add_concept(g, u, group.replace("_", " ").title(), status_group_scheme)
        g.add((status_group_scheme, SKOS.hasTopConcept, u))
    status_rows = status_df.drop_duplicates("normalized_status")
    for _, row in status_rows.iterrows():
        code = row["normalized_status"]
        u = RES[f"status/{slugify(code)}"]
        status_uris[code] = u
        add_concept(g, u, code.replace("_", " ").title(), status_scheme, group_uris.get(row["analytical_group"]))
        g.add((u, DCTERMS.identifier, Literal(code)))
        inc = bool_lit(row["include_in_main_analysis"])
        if inc is not None:
            g.add((u, ONTO.includedInMainAnalysis, inc))
        if row["rationale"]:
            g.add((u, SKOS.scopeNote, Literal(row["rationale"], lang="it")))

    # --- Municipalities and demographic observations ------------------------
    mdf = read_csv(data_dir / "analysis_municipality.csv")
    for _, row in mdf.iterrows():
        code = row["istat_code"]
        m = RES[f"municipality/{code}"]
        g.add((m, RDF.type, ONTO.Municipality))
        g.add((m, CIS.hasISTATCode, Literal(code, datatype=XSD.string)))
        add_it_label(g, m, row["municipality_name"])
        if row["region"]:
            g.add((m, ONTO.regionName, Literal(row["region"], lang="it")))
        if row["province"]:
            g.add((m, ONTO.provinceName, Literal(row["province"], lang="it")))
        if row["province_istat_code"]:
            g.add((m, ONTO.provinceISTATCode, Literal(row["province_istat_code"], datatype=XSD.string)))
        if row["population_comparability"]:
            g.add((m, ONTO.populationComparability, Literal(row["population_comparability"])))
        pcl = dec_lit(row["population_change_percent"])
        if pcl is not None:
            g.add((m, ONTO.populationChangePercent2019_2025, pcl))
        for year, date, source in [("2019", POSAS_2019_DATE, src_posas_2019), ("2025", POSAS_2025_DATE, src_posas_2025)]:
            pval = row[f"population_{year}"]
            if pval == "":
                continue
            obs = RES[f"demography/{code}/{year}"]
            g.add((obs, RDF.type, ONTO.DemographicObservation))
            g.add((m, ONTO.hasDemographicObservation, obs))
            g.add((obs, ONTO.observedMunicipality, m))
            g.add((obs, ONTO.referenceDate, Literal(date, datatype=XSD.date)))
            g.add((obs, PROV.wasDerivedFrom, source))
            pop = int_lit(pval)
            if pop is not None: g.add((obs, ONTO.population, pop))
            for suffix, prop in [
                ("0_14", ONTO.population0_14),
                ("15_64", ONTO.population15_64),
                ("65_plus", ONTO.population65Plus),
            ]:
                lit = int_lit(row[f"population_{suffix}_{year}"])
                if lit is not None: g.add((obs, prop, lit))
            share = dec_lit(row[f"share_65_plus_{year}"])
            if share is not None: g.add((obs, ONTO.share65Plus, share))

    # --- Libraries, sites, addresses, geometry -------------------------------
    ldf = read_csv(data_dir / "library.csv")
    # lookup type rows and status rows
    type_df = read_csv(data_dir / "library_type.csv")
    type_map = {r["isil"]: r for _, r in type_df.iterrows()}
    stat_map = {r["isil"]: r for _, r in status_df.iterrows()}

    func_concepts: dict[str, URIRef] = {}
    admin_concepts: dict[str, URIRef] = {}
    for value in sorted(x for x in type_df["functional_type"].unique() if x):
        u = concept_uri("functional-type", value); func_concepts[value] = u
        add_concept(g, u, value, functional_scheme)
    for value in sorted(x for x in type_df["administrative_type"].unique() if x):
        u = concept_uri("administrative-type", value); admin_concepts[value] = u
        add_concept(g, u, value, administrative_scheme)

    for _, row in ldf.iterrows():
        isil = row["isil"]
        lib = RES[f"library/{isil}"]
        site = RES[f"site/{isil}"]
        address = RES[f"address/{isil}"]
        g.add((lib, RDF.type, CIS.Library))
        g.add((lib, CIS.ISILIdentifier, Literal(isil, datatype=XSD.string)))
        add_it_label(g, lib, row["name_original"])
        if row["name_original"]:
            g.add((lib, CIS.institutionalName, Literal(row["name_original"], lang="it")))
        if row["updated_date"]:
            g.add((lib, DCTERMS.modified, Literal(row["updated_date"], datatype=XSD.date)))
        if row["sbn_code"]: g.add((lib, ONTO.sbnCode, Literal(row["sbn_code"], datatype=XSD.string)))
        if row["acnp_code"]: g.add((lib, ONTO.acnpCode, Literal(row["acnp_code"], datatype=XSD.string)))
        if row["cei_code"]: g.add((lib, ONTO.ceiCode, Literal(row["cei_code"], datatype=XSD.string)))
        if row["rism_code"]: g.add((lib, ONTO.rismCode, Literal(row["rism_code"], datatype=XSD.string)))
        restricted = bool_lit(row["restricted_access"])
        if restricted is not None: g.add((lib, ONTO.restrictedAccess, restricted))
        if row["disabled_access"]: g.add((lib, ONTO.accessibilityNote, Literal(row["disabled_access"], lang="it")))
        if row["owning_entity"]: g.add((lib, ONTO.owningEntityName, Literal(row["owning_entity"], lang="it")))

        tr = type_map.get(isil)
        if tr is not None:
            if tr["functional_type"]:
                g.add((lib, ONTO.functionalType, func_concepts[tr["functional_type"]]))
            if tr["administrative_type"]:
                g.add((lib, ONTO.administrativeType, admin_concepts[tr["administrative_type"]]))

        g.add((lib, CIS.hasSite, site))
        g.add((site, RDF.type, CIS.Site))
        add_it_label(g, site, f"Sede di {row['name_original']}")
        if row["address_original"]:
            g.add((site, CIS.hasAddress, address))
            g.add((address, RDF.type, CIS.Address))
            # Also type as LOCN Address so locn:fullAddress has its documented domain.
            g.add((address, RDF.type, LOCN.Address))
            g.add((address, LOCN.fullAddress, Literal(row["address_original"])))
            if row["postal_code"]: g.add((address, ONTO.postalCode, Literal(row["postal_code"], datatype=XSD.string)))
        if row["istat_code"]:
            muni = RES[f"municipality/{row['istat_code']}"]
            g.add((site, CIS.hasGeographicalLocation, muni))
        if row["latitude"] and row["longitude"]:
            geom = RES[f"geometry/site/{isil}"]
            g.add((site, RDF.type, GEO.Feature))
            g.add((site, GEO.hasGeometry, geom))
            g.add((geom, RDF.type, GEO.Geometry))
            # GeoSPARQL WKT order is longitude latitude for CRS84/default WKT.
            wkt = f"POINT({row['longitude']} {row['latitude']})"
            g.add((geom, GEO.asWKT, Literal(wkt, datatype=GEO.wktLiteral)))

        sr = stat_map[isil]
        obs = RES[f"status-observation/{isil}/{ICCU_SNAPSHOT_DATE}"]
        g.add((lib, ONTO.hasStatusObservation, obs))
        g.add((obs, RDF.type, ONTO.LibraryStatusObservation))
        g.add((obs, ONTO.observedLibrary, lib))
        g.add((obs, ONTO.hasStatus, status_uris[sr["normalized_status"]]))
        g.add((obs, ONTO.observationDate, Literal(ICCU_SNAPSHOT_DATE, datatype=XSD.date)))
        g.add((obs, PROV.wasDerivedFrom, src_iccu))
        inc = bool_lit(sr["include_in_main_analysis"])
        if inc is not None: g.add((obs, ONTO.includedInMainAnalysis, inc))
        if sr["source_status"]:
            g.add((obs, ONTO.sourceStatusText, Literal(sr["source_status"], lang="it")))

    # --- Previous names ------------------------------------------------------
    pndf = read_csv(data_dir / "library_previous_name.csv")
    seen_alt_names = set()
    for _, row in pndf.iterrows():
        if row["previous_name_original"]:
            key = (row["isil"], row["previous_name_original"])
            if key in seen_alt_names:
                continue  # RDF graphs are sets: remove exact source duplicate assertions.
            seen_alt_names.add(key)
            lib = RES[f"library/{row['isil']}"]
            g.add((lib, SCHEMA.alternateName, Literal(row["previous_name_original"], lang="it")))

    # --- Holdings ------------------------------------------------------------
    hdf = read_csv(data_dir / "library_holdings.csv")
    material_concepts: dict[str, URIRef] = {}
    category_concepts: dict[str, URIRef] = {}
    for value in sorted(x for x in hdf["material"].unique() if x):
        u = concept_uri("material", value); material_concepts[value] = u
        add_concept(g, u, value, material_scheme)
    for value in sorted(x for x in hdf["category"].unique() if x):
        u = concept_uri("holding-category", value); category_concepts[value] = u
        add_concept(g, u, value, category_scheme)
    for _, row in hdf.iterrows():
        lib = RES[f"library/{row['isil']}"]
        rec = RES[f"holding/{row['isil']}/{row['material_index']}"]
        g.add((rec, RDF.type, ONTO.HoldingObservation))
        g.add((lib, ONTO.hasHoldingObservation, rec))
        g.add((rec, ONTO.observedLibrary, lib))
        g.add((rec, ONTO.observationDate, Literal(ICCU_SNAPSHOT_DATE, datatype=XSD.date)))
        g.add((rec, PROV.wasDerivedFrom, src_iccu))
        if row["material"]: g.add((rec, ONTO.materialType, material_concepts[row["material"]]))
        if row["category"]: g.add((rec, ONTO.holdingCategory, category_concepts[row["category"]]))
        qty = int_lit(row["quantity"])
        if qty is not None: g.add((rec, ONTO.quantity, qty))

    # --- Special collections -------------------------------------------------
    scdf = read_csv(data_dir / "special_collection.csv")
    ct_concepts: dict[str, URIRef] = {}
    for value in sorted(x for x in scdf["tipologia_fondo"].unique() if x):
        u = concept_uri("special-collection-type", value); ct_concepts[value] = u
        add_concept(g, u, value, collection_type_scheme)
    for _, row in scdf.iterrows():
        lib = RES[f"library/{row['isil']}"]
        col = RES[f"collection/{row['isil']}-special-{row['collection_index']}"]
        g.add((col, RDF.type, ONTO.SpecialCollection))
        g.add((lib, CIS.hasCollection, col))
        g.add((col, PROV.wasDerivedFrom, src_iccu))
        if row["denominazione"]: add_it_label(g, col, row["denominazione"])
        if row["codice"]: g.add((col, ONTO.collectionCode, Literal(row["codice"], datatype=XSD.string)))
        dep = bool_lit(row["fondo_depositato"])
        if dep is not None: g.add((col, ONTO.depositedCollection, dep))
        if row["tipologia_fondo"]: g.add((col, ONTO.collectionType, ct_concepts[row["tipologia_fondo"]]))
        if row["descrizione"]: g.add((col, CIS.description, Literal(row["descrizione"], lang="it")))
        if row["consistenza"]: g.add((col, ONTO.collectionExtentText, Literal(row["consistenza"], lang="it")))
        if row["datazione"]: g.add((col, ONTO.collectionDatingText, Literal(row["datazione"], lang="it")))
        if row["provenienza"]: g.add((col, ONTO.collectionProvenanceText, Literal(row["provenienza"], lang="it")))
        if row["soggetto_produttore"]: g.add((col, ONTO.producerText, Literal(row["soggetto_produttore"], lang="it")))
        if row["url_o_citazione_bibliografica"]: g.add((col, DCTERMS.references, Literal(row["url_o_citazione_bibliografica"])))

    # --- Mergers -------------------------------------------------------------
    merge_df = read_csv(data_dir / "library_mergers.csv")
    for _, row in merge_df.iterrows():
        if row["parse_success"].casefold() == "true" and row["target_exists_in_snapshot"].casefold() == "true" and row["target_isil"]:
            src = RES[f"library/{row['source_isil']}"]
            tgt = RES[f"library/{row['target_isil']}"]
            g.add((src, ONTO.mergedInto, tgt))

    # --- Metadata graph ------------------------------------------------------
    dataset = RES["dataset/biblioteche-fantasma"]
    mg.add((dataset, RDF.type, DCAT.Dataset))
    mg.add((dataset, DCTERMS.title, Literal("Biblioteche Fantasma - knowledge graph", lang="it")))
    mg.add((dataset, DCTERMS.description, Literal("Knowledge graph derivato dai dataset processati ICCU e ISTAT: biblioteche, stati osservati, patrimonio, fondi speciali e demografia comunale 2019/2025.", lang="it")))
    mg.add((dataset, DCTERMS.license, URIRef("https://creativecommons.org/licenses/by/4.0/")))
    mg.add(
        (
            dataset,
            DCTERMS.modified,
            Literal(PROJECT_RELEASE_DATE, datatype=XSD.date),
        )
    )
    mg.add((dataset, PROV.wasDerivedFrom, src_iccu)); mg.add((dataset, PROV.wasDerivedFrom, src_posas_2019)); mg.add((dataset, PROV.wasDerivedFrom, src_posas_2025))
    for src, typ, label, date in [
        (src_iccu, "ICCU Open Data", "Snapshot ICCU Open Data", ICCU_SNAPSHOT_DATETIME),
        (src_posas_2019, "ISTAT POSAS", "ISTAT POSAS 2019", POSAS_2019_DATE),
        (src_posas_2025, "ISTAT POSAS", "ISTAT POSAS 2025", POSAS_2025_DATE),
    ]:
        mg.add((src, RDF.type, PROV.Entity)); mg.add((src, DCTERMS.title, Literal(label, lang="it")))
        mg.add((src, DCTERMS.type, Literal(typ)))
        if "T" in date:
            mg.add((src, PROV.generatedAtTime, Literal(date, datatype=XSD.dateTime)))
        else:
            mg.add((src, DCTERMS.temporal, Literal(date, datatype=XSD.date)))
    # Official web sources, not local entity identifiers.
    mg.add((src_iccu, DCTERMS.source, URIRef("https://anagrafe.iccu.sbn.it/it/open-data/")))
    mg.add((src_posas_2019, DCTERMS.source, URIRef("https://demo.istat.it/")))
    mg.add((src_posas_2025, DCTERMS.source, URIRef("https://demo.istat.it/")))

    for name, title, media in [
        ("data.ttl", "RDF data", "text/turtle"),
        ("links.ttl", "External links", "text/turtle"),
        ("metadata.ttl", "RDF metadata", "text/turtle"),
    ]:
        dist = RES[f"distribution/{name}"]
        mg.add((dist, RDF.type, DCAT.Distribution)); mg.add((dataset, DCAT.distribution, dist))
        mg.add((dist, DCTERMS.title, Literal(title, lang="en")))
        mg.add((dist, DCAT.mediaType, Literal(media)))
        mg.add((dist, DCAT.downloadURL, URIRef(DEV_BASE + f"distribution/{quote(name)}")))

    g.close()
    mg.serialize(destination=out_dir / "metadata.ttl", format="turtle")
    return g, mg


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args()
    data_dir = args.root / "data" / "processed"
    out_dir = args.root / "rdf"
    g, mg = generate(data_dir, out_dir)
    print(f"data triples: {len(g):,}")
    print(f"metadata triples: {len(mg):,}")


if __name__ == "__main__":
    main()
