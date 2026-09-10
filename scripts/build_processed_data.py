#!/usr/bin/env python3
"""Build processed tabular datasets from the original ICCU and ISTAT raw archives.

The script is deterministic and idempotent. It never modifies the raw archives.
"""
from __future__ import annotations
import argparse, io, json, re, unicodedata, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from lxml import etree

ADMIN_CHANGE_SOURCE = "https://www.istat.it/storage/codici-unita-amministrative/Novita-2025-2017.pdf"


def collapse_ws(x):
    if x is None:
        return None
    s = unicodedata.normalize("NFC", str(x))
    s = re.sub(r"\s+", " ", s).strip()
    return s or None


def read_posas(path: Path, year: int, level: str = "Comuni") -> pd.DataFrame:
    with zipfile.ZipFile(path) as z:
        raw = z.read(f"POSAS_{year}_it_{level}.csv")
    df = pd.read_csv(
        io.BytesIO(raw), sep=";", encoding="utf-8-sig", skiprows=1,
        dtype=str, keep_default_na=False, low_memory=False
    )
    df.loc[:, "Età_num"] = pd.to_numeric(df["Età"], errors="coerce")
    df.loc[:, "Totale_num"] = pd.to_numeric(df["Totale"], errors="coerce")
    return df


def classify_status(raw):
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return (
            "NESSUNO_STATO_SPECIALE_REGISTRATO",
            "NESSUNO_STATO_SPECIALE_REGISTRATO",
            False, None,
            "Valore NULL nel campo ICCU: indica assenza di stato speciale registrato; non viene interpretato come biblioteca aperta."
        )
    st = collapse_ws(raw)
    if st == "Biblioteca non più esistente":
        return ("BIBLIOTECA_NON_PIU_ESISTENTE", "CESSAZIONE", True, None,
                "ICCU documenta la cessazione dell'istituzione/servizi/posseduto senza confluenza del patrimonio.")
    if st == "Temporaneamente chiusa":
        return ("TEMPORANEAMENTE_CHIUSA", "INTERRUZIONE_DEL_SERVIZIO", True, None,
                "Stato ICCU che segnala una chiusura temporanea.")
    if st == "Inagibile":
        return ("INAGIBILE", "INTERRUZIONE_DEL_SERVIZIO", True, None,
                "Stato ICCU di inagibilità; servizi non pienamente fruibili.")
    if st == "Servizi sospesi causa sisma":
        return ("SERVIZI_SOSPESI_CAUSA_SISMA", "INTERRUZIONE_DEL_SERVIZIO", True, None,
                "Sospensione esplicita dei servizi a seguito di sisma.")
    if st == "Riapertura con agibilità parziale":
        return ("RIAPERTURA_AGIBILITA_PARZIALE", "OPERATIVITA_PARZIALE", True, None,
                "ICCU specifica che i servizi all'utenza sono solo parzialmente accessibili.")
    if st == "Deposito librario senza punto di servizio":
        return ("DEPOSITO_SENZA_PUNTO_DI_SERVIZIO", "ASSENZA_PUNTO_DI_SERVIZIO", True, None,
                "Struttura senza servizi al pubblico; inclusa nel perimetro principale come assenza di punto di servizio.")
    if st.startswith("Biblioteca confluita"):
        m = re.search(r"\b(IT-[A-Z]{2}\d{4})\b", st)
        return ("BIBLIOTECA_CONFLUITA", "TRASFORMAZIONE_ORGANIZZATIVA", False,
                m.group(1) if m else None,
                "Confluenza/assorbimento organizzativo; non assimilata automaticamente a chiusura o cessazione.")
    if st == "Biblioteca in via di allestimento":
        return ("BIBLIOTECA_IN_VIA_DI_ALLESTIMENTO", "AVVIO", False, None,
                "Biblioteca registrata ma non ancora in attività ordinaria; categoria distinta dalle chiusure.")
    if st == "Biblioteca non censita":
        return ("BIBLIOTECA_NON_CENSITA", "INCOMPLETEZZA_STATO_ANAGRAFICO", False, None,
                "ICCU indica insufficienza informativa oltre nome/indirizzo; non è evidenza di chiusura.")
    if st == "Altri istituti collegati ad attività dell'ICCU":
        return ("ALTRO_ISTITUTO_COLLEGATO_ICCU", "ALTRO", False, None,
                "ICCU chiarisce che l'istituzione non è una biblioteca vera e propria ma una struttura di servizio collegata.")
    return (re.sub(r"[^A-Z0-9]+", "_", st.upper()).strip("_"), "ALTRO", False, None,
            "Valore reale non ricondotto ai gruppi principali; conservato senza inferenze ulteriori.")


def build_crosswalk(t19: pd.DataFrame, t25: pd.DataFrame) -> pd.DataFrame:
    name19 = dict(zip(t19["Codice comune"], t19["Comune"]))
    code25_by_name = {n: c for c, n in zip(t25["Codice comune"], t25["Comune"])}
    rows = []
    for c, n in zip(t25["Codice comune"], t25["Comune"]):
        if c in name19:
            old = name19[c]
            typ = "unchanged" if old == n else "name_string_change_same_code"
            rows.append(dict(
                current_istat_code=c, current_name=n,
                predecessor_istat_code=c, predecessor_name=old,
                transformation_type=typ, effective_date="",
                source="POSAS 2019/2025 direct comparison" if typ == "unchanged" else
                       "POSAS 2019/2025 direct comparison; official administrative-change classification only where separately documented.",
                aggregation_rule="sum",
                notes="" if typ == "unchanged" else f"Denominazione 2019: {old}; denominazione 2025: {n}."
            ))

    def resolve(p):
        if isinstance(p, tuple):
            pc, pn = p
            if name19.get(pc) != pn:
                raise ValueError((pc, pn, name19.get(pc)))
            return pc, pn
        m = t19.loc[t19["Comune"].eq(p), "Codice comune"].tolist()
        if len(m) != 1:
            raise ValueError((p, m))
        return m[0], p

    def add(cur, preds, typ, date, notes=""):
        nonlocal rows
        cc = code25_by_name[cur]
        rows = [r for r in rows if r["current_istat_code"] != cc]
        for p in preds:
            pc, pn = resolve(p)
            rows.append(dict(
                current_istat_code=cc, current_name=cur,
                predecessor_istat_code=pc, predecessor_name=pn,
                transformation_type=typ, effective_date=date,
                source=ADMIN_CHANGE_SOURCE, aggregation_rule="sum", notes=notes
            ))

    maps = [
        ("Gattico-Veruno", ["Gattico", "Veruno"], "fusion", "2019-01-01"),
        ("Quaregna Cerreto", ["Quaregna", "Cerreto Castello"], "fusion", "2019-01-01"),
        ("Valdilana", ["Mosso", "Soprana", "Trivero", "Valle Mosso"], "fusion", "2019-01-01"),
        ("Val di Chy", ["Alice Superiore", "Lugnacco", "Pecco"], "fusion", "2019-01-01"),
        ("Valchiusa", ["Meugliano", "Trausella", "Vico Canavese"], "fusion", "2019-01-01"),
        ("Valle Cannobina", ["Cavaglio-Spoccia", "Cursolo-Orasso", "Falmenta"], "fusion", "2019-01-01"),
        ("Solbiate con Cagno", ["Solbiate", "Cagno"], "fusion", "2019-01-01"),
        ("Colli Verdi", ["Canevino", "Ruino", ("018170", "Valverde")], "fusion", "2019-01-01"),
        ("Piadena Drizzona", ["Piadena", "Drizzona"], "fusion", "2019-01-01"),
        ("Borgocarbonara", ["Borgofranco sul Po", "Carbonara di Po"], "fusion", "2019-01-01"),
        ("Terre d'Adige", ["Nave San Rocco", "Zambana"], "fusion", "2019-01-01"),
        ("Riva del Po", ["Berra", "Ro"], "fusion", "2019-01-01"),
        ("Tresignana", ["Formignana", "Tresigallo"], "fusion", "2019-01-01"),
        ("Sorbolo Mezzani", ["Sorbolo", "Mezzani"], "fusion", "2019-01-01"),
        ("Barberino Tavarnelle", ["Barberino Val d'Elsa", "Tavarnelle Val di Pesa"], "fusion", "2019-01-01"),
        ("Sassocorvaro Auditore", ["Sassocorvaro", "Auditore"], "fusion", "2019-01-01"),
        ("Borgo Valbelluna", ["Lentiai", "Mel", "Trichiana"], "fusion", "2019-01-30"),
        ("Pieve del Grappa", ["Crespano del Grappa", "Paderno del Grappa"], "fusion", "2019-01-30"),
        ("Valbrenta", ["Campolongo sul Brenta", "Cismon del Grappa", "San Nazario", "Valstagna"], "fusion", "2019-01-30"),
        ("Lu e Cuccaro Monferrato", ["Cuccaro Monferrato", "Lu"], "fusion", "2019-02-01"),
        ("Vermezzo con Zelo", ["Vermezzo", "Zelo Surrigone"], "fusion", "2019-02-08"),
        ("Cadrezzate con Osmate", ["Cadrezzate", "Osmate"], "fusion", "2019-02-15"),
        ("Colceresa", ["Mason Vicentino", "Molvena"], "fusion", "2019-02-20"),
        ("Lusiana Conco", ["Lusiana", "Conco"], "fusion", "2019-02-20"),
        ("Presicce-Acquarica", ["Acquarica del Capo", "Presicce"], "fusion", "2019-05-15"),
        ("Borgo d'Anaunia", ["Fondo", "Malosco", "Castelfondo"], "fusion", "2020-01-01"),
        ("Novella", ["Brez", "Cagnò", "Cloz", "Revò", "Romallo"], "fusion", "2020-01-01"),
        ("Ville di Fiemme", ["Carano", "Daiano", "Varena"], "fusion", "2020-01-01"),
        ("Moransengo-Tonengo", ["Moransengo", "Tonengo"], "fusion", "2023-01-01"),
        ("Bardello con Malgesso e Bregano", ["Bardello", "Malgesso", "Bregano"], "fusion", "2023-01-01"),
        ("Uggiate con Ronago", ["Uggiate-Trevano", "Ronago"], "fusion", "2024-01-01"),
        ("Sovizzo", [("024103", "Sovizzo"), "Gambugliano"], "fusion", "2024-01-22"),
        ("Setteville", ["Quero Vas", "Alano di Piave"], "fusion", "2024-01-22"),
        ("Santa Caterina d'Este", ["Vighizzolo d'Este", "Carceri"], "fusion", "2024-01-22"),
        ("Alagna Valsesia", ["Alagna Valsesia", "Riva Valdobbia"], "incorporation", "2019-01-01"),
        ("Saluzzo", ["Saluzzo", "Castellar"], "incorporation", "2019-01-01"),
        ("Santo Stefano Belbo", ["Santo Stefano Belbo", "Camo"], "incorporation", "2019-01-01"),
        ("Busca", ["Busca", "Valmala"], "incorporation", "2019-01-01"),
        ("Torre de' Picenardi", ["Torre de' Picenardi", "Ca' d'Andrea"], "incorporation", "2019-01-01"),
        ("San Giorgio Bigarello", [("020057", "San Giorgio di Mantova"), "Bigarello"], "incorporation_and_rename", "2019-01-01"),
        ("San Michele all'Adige", ["San Michele all'Adige", "Faedo"], "incorporation", "2020-01-01"),
        ("Bellano", ["Bellano", "Vendrogno"], "incorporation", "2020-01-01"),
        ("Pesaro", ["Pesaro", "Monteciccardo"], "incorporation", "2020-07-01"),
        ("Campospinoso Albaredo", [("018026", "Campospinoso"), "Albaredo Arnaboldi"], "incorporation_and_rename", "2023-11-18"),
        ("Montecopiolo", [("041033", "Montecopiolo")], "province_transfer_code_change", "2021-06-17"),
        ("Sassofeltrio", [("041060", "Sassofeltrio")], "province_transfer_code_change", "2021-06-17"),
    ]
    for m in maps:
        add(*m)

    # Upgrade only denomination changes explicitly classified in the official variation summary.
    official_renames = {
        "005014": "2022-08-12", "005020": "2022-03-03", "005056": "2023-01-17",
        "005077": "2023-10-19", "006045": "2019-05-31", "021053": "2023-04-14",
        "021076": "2019-10-11", "023052": "2019-02-23", "068033": "2023-07-13",
    }
    for r in rows:
        if r["current_istat_code"] in official_renames and r["transformation_type"] == "name_string_change_same_code":
            r["transformation_type"] = "denomination_change_official"
            r["effective_date"] = official_renames[r["current_istat_code"]]
            r["source"] = ADMIN_CHANGE_SOURCE

    tc = code25_by_name["Trapani"]
    rows = [r for r in rows if r["current_istat_code"] != tc]
    rows.append(dict(
        current_istat_code=tc, current_name="Trapani", predecessor_istat_code=tc, predecessor_name="Trapani",
        transformation_type="partial_territorial_split_source", effective_date="2021-02-20",
        source=ADMIN_CHANGE_SOURCE, aggregation_rule="not_reconstructible",
        notes="Parte del territorio di Trapani è stata scorporata per istituire Misiliscemi; POSAS 2019 comunale non consente una sottrazione territorialmente corretta."
    ))
    mc = code25_by_name["Misiliscemi"]
    rows.append(dict(
        current_istat_code=mc, current_name="Misiliscemi", predecessor_istat_code=tc, predecessor_name="Trapani",
        transformation_type="partial_territorial_split_new_municipality", effective_date="2021-02-20",
        source=ADMIN_CHANGE_SOURCE, aggregation_rule="not_reconstructible",
        notes="Comune istituito per scorporo di località da Trapani; il 2019 non è ricostruibile correttamente dai soli dati POSAS comunali."
    ))
    return pd.DataFrame(rows).sort_values(["current_istat_code", "predecessor_istat_code"], kind="stable").reset_index(drop=True)


def age_table(df: pd.DataFrame, year: int) -> pd.DataFrame:
    d = df[df["Età_num"].between(0, 100)].copy()
    d.loc[:, "band"] = pd.cut(
        d["Età_num"],
        [-1, 14, 64, 100],
        labels=["0_14", "15_64", "65_plus"],
    )
    p = d.pivot_table(index="Codice comune", columns="band", values="Totale_num", aggfunc="sum", observed=False).reset_index()
    p.columns = ["istat_code", f"population_0_14_{year}", f"population_15_64_{year}", f"population_65_plus_{year}"]
    return p


def write_csv(df: pd.DataFrame, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8", lineterminator="\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iccu", required=True, type=Path)
    ap.add_argument("--posas2019", required=True, type=Path)
    ap.add_argument("--posas2025", required=True, type=Path)
    ap.add_argument("--out-root", default=Path("."), type=Path)
    a = ap.parse_args()
    out = a.out_root
    proc = out / "data/processed"
    meta = out / "metadata"

    for p in [proc, meta]:
        p.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(a.iccu) as z:
        obj = json.load(io.TextIOWrapper(z.open("biblioteche.json"), encoding="utf-8"))
        tdf = pd.read_csv(io.BytesIO(z.read("tipologie.csv")), sep=";", encoding="utf-8-sig", dtype=str, keep_default_na=False)
        proot = etree.fromstring(z.read("patrimonio.xml"))
        froot = etree.fromstring(z.read("fondi-speciali.xml"))
        croot = etree.fromstring(z.read("contatti.xml"))

    libs, prev = [], []
    for r in obj["biblioteche"]:
        ids = r.get("codici-identificativi") or {}; den = r.get("denominazioni") or {}; addr = r.get("indirizzo") or {}
        com = addr.get("comune") or {}; prov = addr.get("provincia") or {}; acc = r.get("accesso") or {}
        co = addr.get("coordinate")
        lat = lon = None
        if isinstance(co, list) and len(co) >= 2: lat, lon = co[0], co[1]
        libs.append(dict(
            isil=ids.get("isil"), sbn_code=ids.get("sbn"), acnp_code=ids.get("acnp"), cei_code=ids.get("cei"),
            cmbs_code=ids.get("cmbs"), rism_code=ids.get("rism"), census_year=r.get("anno-censimento"),
            updated_date=r.get("data-aggiornamento"), name_original=den.get("ufficiale"), name_normalized=collapse_ws(den.get("ufficiale")),
            address_original=addr.get("via-piazza"), address_normalized=collapse_ws(addr.get("via-piazza")), hamlet=collapse_ws(addr.get("frazione")),
            postal_code=collapse_ws(addr.get("cap")), municipality_name=com.get("nome"), istat_code=com.get("istat"),
            province_name=prov.get("nome"), province_istat_code=prov.get("istat"), province_abbrev=prov.get("sigla"), region=addr.get("regione"),
            latitude_original=lat, longitude_original=lon, restricted_access=acc.get("riservato"), disabled_access=acc.get("portatori-handicap"),
            administrative_type=r.get("tipologia-amministrativa"), functional_type=r.get("tipologia-funzionale"),
            owning_entity=collapse_ws(r.get("ente")), source_status=r.get("stato-registrazione")
        ))
        for n in den.get("precedenti") or []:
            prev.append(dict(isil=ids.get("isil"), previous_name_original=n, previous_name_normalized=collapse_ws(n)))
    lib = pd.DataFrame(libs)
    lat = pd.to_numeric(lib.latitude_original, errors="coerce"); lon = pd.to_numeric(lib.longitude_original, errors="coerce")
    zero = lat.eq(0) & lon.eq(0); invalid = (~lat.between(-90, 90) | ~lon.between(-180, 180)) & lat.notna() & lon.notna()
    outit = (~lat.between(35, 48) | ~lon.between(6, 19)) & lat.notna() & lon.notna() & ~zero

    lib.loc[:, "latitude"] = lat.mask(zero | invalid)
    lib.loc[:, "longitude"] = lon.mask(zero | invalid)

    lib.loc[:, "coordinate_quality_flag"] = np.select(
        [
            zero,
            invalid,
            outit,
            lat.isna() | lon.isna(),
        ],
        [
            "zero_pair_treated_as_missing",
            "world_range_invalid",
            "outside_italy_bbox_review",
            "missing",
        ],
        default="valid_world_range",
    )

    lib.loc[:, "updated_date"] = (
        pd.to_datetime(lib["updated_date"], errors="coerce")
        .dt.strftime("%Y-%m-%d")
    )

    stat = []
    for r in lib[["isil", "source_status"]].itertuples(index=False):
        raw = r.source_status if pd.notna(r.source_status) else None
        n, g, inc, t, why = classify_status(raw)
        stat.append(dict(isil=r.isil, source_status=raw, normalized_status=n, analytical_group=g,
                         include_in_main_analysis=inc, target_isil=t, rationale=why))
    status = pd.DataFrame(stat)

    maprows = []
    for raw, count in lib.source_status.value_counts(dropna=False).items():
        rawv = None if pd.isna(raw) else raw
        n, g, inc, t, why = classify_status(rawv)
        maprows.append(dict(source_status=rawv, normalized_status=n, analytical_group=g,
                            include_in_main_analysis=inc, target_isil=t, rationale=why, source_count=int(count)))
    status_mapping = pd.DataFrame(maprows).sort_values("source_status", key=lambda s: s.fillna("").astype(str), kind="stable").reset_index(drop=True)
    write_csv(status_mapping, meta/"status_mapping.csv")

    holds = []
    for b in proot.findall("biblioteca"):
        for i, m in enumerate(b.findall("materiale"), 1):
            q = m.get("posseduto")
            holds.append(dict(isil=b.get("codice-isil"), material_index=i, library_name_source=b.get("denominazione"),
                              category=collapse_ws(m.get("categoria")), material=collapse_ws(m.text), quantity_original=q,
                              quantity=pd.to_numeric(q, errors="coerce") if q is not None else np.nan))
    funds = []
    for b in froot.findall("biblioteca"):
        for i, fs in enumerate(b.findall("fondo-speciale"), 1):
            rr = dict(isil=b.get("codice-isil"), collection_index=i, library_name_source=b.get("denominazione"))
            for ch in fs:
                key = ch.tag.replace("-", "_"); val = collapse_ws(ch.text)
                if key in rr and rr[key] not in (None, ""):
                    rr[key] = f"{rr[key]} | {val}" if val else rr[key]
                else: rr[key] = val
            funds.append(rr)
    contacts = []
    for b in croot.findall("biblioteca"):
        for i, c in enumerate(b.findall("contatto"), 1):
            contacts.append(dict(isil=b.get("codice-isil"), contact_index=i, contact_type=collapse_ws(c.get("tipo")),
                                 contact_value=collapse_ws(c.text), source="contatti.xml"))
    types = tdf.rename(columns={"codice isil": "isil", "denominazione biblioteca": "library_name_source", "tipologia funzionale": "functional_type",
                                "denominazione ente": "owning_entity", "tipologia amministrativa": "administrative_type"})
    for c in types.columns: types.loc[:, c] = types[c].map(collapse_ws)

    isils = set(lib.isil); mr = []; rx = re.compile(r"^Biblioteca confluita in (IT-[A-Z]{2}\d{4})$")
    for r in lib[["isil", "source_status"]].itertuples(index=False):
        if isinstance(r.source_status, str) and collapse_ws(r.source_status).startswith("Biblioteca confluita"):
            st = collapse_ws(r.source_status); m = rx.match(st); target = m.group(1) if m else None
            mr.append(dict(source_isil=r.isil, target_isil=target, source_status=r.source_status, parse_success=bool(m),
                           target_exists_in_snapshot=target in isils if target else False, self_loop=target == r.isil if target else False))
    mergers = pd.DataFrame(mr)
    edges = {r.source_isil: r.target_isil for r in mergers.itertuples() if r.parse_success and pd.notna(r.target_isil)}
    cyc = set()
    for start in edges:
        seen = {}; path = []; cur = start
        while cur in edges:
            if cur in seen: cyc.update(path[seen[cur]:]); break
            seen[cur] = len(path); path.append(cur); cur = edges[cur]
            if len(path) > len(edges) + 1: break
    mergers.loc[:, "in_cycle"] = mergers["source_isil"].isin(cyc)

    p19 = read_posas(a.posas2019, 2019); p25 = read_posas(a.posas2025, 2025)
    t19 = p19[p19.Età_num.eq(999)][["Codice comune", "Comune", "Totale_num"]].rename(columns={"Totale_num": "population_2019_raw"})
    t25 = p25[p25.Età_num.eq(999)][["Codice comune", "Comune", "Totale_num"]].rename(columns={"Totale_num": "population_2025"})
    cw = build_crosswalk(t19, t25); write_csv(cw, meta/"municipality_crosswalk_2019_2025.csv")
    a19 = age_table(p19, 2019); a25 = age_table(p25, 2025)
    hm = cw[cw.aggregation_rule.eq("sum")].merge(t19.rename(columns={"Codice comune": "predecessor_istat_code"}), on="predecessor_istat_code")
    hm = hm.merge(a19.rename(columns={"istat_code": "predecessor_istat_code"}), on="predecessor_istat_code")
    agg19 = hm.groupby(["current_istat_code", "current_name"], as_index=False, sort=True).agg(
        population_2019=("population_2019_raw", "sum"), population_0_14_2019=("population_0_14_2019", "sum"),
        population_15_64_2019=("population_15_64_2019", "sum"), population_65_plus_2019=("population_65_plus_2019", "sum"))
    pop = t25.rename(columns={"Codice comune": "istat_code", "Comune": "municipality_name"}).merge(a25, on="istat_code")
    pop = pop.merge(agg19.rename(columns={"current_istat_code": "istat_code"}).drop(columns="current_name"), on="istat_code", how="left")
    nonrec = set(cw.loc[cw.aggregation_rule.eq("not_reconstructible"), "current_istat_code"])
    for c in ["population_2019", "population_0_14_2019", "population_15_64_2019", "population_65_plus_2019"]:
        pop.loc[pop["istat_code"].isin(nonrec), c] = np.nan

    pop.loc[:, "population_change_absolute"] = (
        pop["population_2025"] - pop["population_2019"]
    )

    pop.loc[:, "population_change_percent"] = np.where(
        pop["population_2019"].gt(0),
        pop["population_change_absolute"] / pop["population_2019"] * 100,
        np.nan,
    )

    pop.loc[:, "share_65_plus_2019"] = np.where(
        pop["population_2019"].gt(0),
        pop["population_65_plus_2019"] / pop["population_2019"] * 100,
        np.nan,
    )

    pop.loc[:, "share_65_plus_2025"] = np.where(
        pop["population_2025"].gt(0),
        pop["population_65_plus_2025"] / pop["population_2025"] * 100,
        np.nan,
    )

    pop.loc[:, "population_comparability"] = np.where(
        pop["istat_code"].isin(nonrec),
        "not_comparable_due_to_2021_territorial_split",
        "comparable_on_2025_geography",
    )

    # Province denomination in the analytical dataset is canonicalized from ISTAT POSAS 2025 Province,
    # not from ICCU. This deterministically preserves the official label "Reggio di Calabria".
    pp25 = read_posas(a.posas2025, 2025, "Province")
    prov25 = pp25[pp25.Età_num.eq(999)][["Codice provincia", "Provincia"]].drop_duplicates().rename(
        columns={"Codice provincia": "province_istat_code", "Provincia": "province"})
    regmap = lib[["province_istat_code", "region"]].drop_duplicates()
    if regmap.groupby("province_istat_code").region.nunique().max() != 1:
        raise ValueError("Non-deterministic ICCU province→region mapping")
    prov_lookup = prov25.merge(regmap, on="province_istat_code", how="left", validate="one_to_one")

    work = lib.merge(status[["isil", "normalized_status", "include_in_main_analysis"]], on="isil")
    work.loc[:, "is_library_like"] = ~work["normalized_status"].eq(
        "ALTRO_ISTITUTO_COLLEGATO_ICCU"
    )
    specs = {
        "total_libraries": work.is_library_like,
        "ceased_libraries": work.normalized_status.eq("BIBLIOTECA_NON_PIU_ESISTENTE"),
        "temporarily_closed_libraries": work.normalized_status.eq("TEMPORANEAMENTE_CHIUSA"),
        "inaccessible_libraries": work.normalized_status.eq("INAGIBILE"),
        "earthquake_suspended_libraries": work.normalized_status.eq("SERVIZI_SOSPESI_CAUSA_SISMA"),
        "partial_reopening_libraries": work.normalized_status.eq("RIAPERTURA_AGIBILITA_PARZIALE"),
        "merged_libraries": work.normalized_status.eq("BIBLIOTECA_CONFLUITA"),
        "no_service_point_libraries": work.normalized_status.eq("DEPOSITO_SENZA_PUNTO_DI_SERVIZIO"),
        "main_problematic_libraries": work.include_in_main_analysis,
        "not_censused_libraries": work.normalized_status.eq("BIBLIOTECA_NON_CENSITA"),
        "setup_libraries": work.normalized_status.eq("BIBLIOTECA_IN_VIA_DI_ALLESTIMENTO"),
    }
    for col, expr in specs.items(): work.loc[:, col] = expr.astype(int)
    aggcols = list(specs)
    ag = work.groupby("istat_code", sort=True).agg(total_registry_records=("istat_code", "size"), **{c: (c, "sum") for c in aggcols}).reset_index()
    analysis = pop.copy(); analysis.loc[:, "province_istat_code"] = analysis["istat_code"].str[:3]
    analysis = analysis.merge(prov_lookup, on="province_istat_code", how="left", validate="many_to_one")
    analysis = analysis.merge(ag, on="istat_code", how="left")
    cnt = ["total_registry_records"] + aggcols
    analysis.loc[:, cnt] = analysis[cnt].fillna(0).astype(int)
    analysis.loc[:, "problematic_share"] = np.where(
        analysis["total_libraries"].gt(0),
        analysis["main_problematic_libraries"] / analysis["total_libraries"],
        np.nan,
    )

    analysis.loc[:, "libraries_per_100k"] = np.where(
        analysis["population_2025"].gt(0),
        analysis["total_libraries"] / analysis["population_2025"] * 100000,
        np.nan,
    )

    analysis.loc[:, "problematic_libraries_per_100k"] = np.where(
        analysis["population_2025"].gt(0),
        analysis["main_problematic_libraries"]
        / analysis["population_2025"]
        * 100000,
        np.nan,
    )

    analysis_front = [
        "istat_code", "municipality_name", "province", "region", "province_istat_code",
        "population_2019", "population_2025", "population_change_absolute", "population_change_percent",
        "population_0_14_2019", "population_15_64_2019", "population_65_plus_2019", "share_65_plus_2019",
        "population_0_14_2025", "population_15_64_2025", "population_65_plus_2025", "share_65_plus_2025",
        "population_comparability", "total_registry_records", "total_libraries", "ceased_libraries",
        "temporarily_closed_libraries", "inaccessible_libraries", "earthquake_suspended_libraries",
        "partial_reopening_libraries", "merged_libraries", "no_service_point_libraries", "main_problematic_libraries",
        "not_censused_libraries", "setup_libraries", "problematic_share", "libraries_per_100k", "problematic_libraries_per_100k"
    ]
    analysis = analysis[analysis_front]

    outputs = {
        "library.csv": lib, "library_status.csv": status, "library_type.csv": types,
        "library_holdings.csv": pd.DataFrame(holds), "special_collection.csv": pd.DataFrame(funds),
        "library_contact.csv": pd.DataFrame(contacts), "library_previous_name.csv": pd.DataFrame(prev),
        "library_mergers.csv": mergers, "municipality_population.csv": pop, "analysis_municipality.csv": analysis
    }
    for fn, df in outputs.items():
      write_csv(df, proc / fn)
    print("Built", len(outputs), "processed resources in", proc)

if __name__ == "__main__":
    main()
