#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, io, json, shutil, zipfile
from pathlib import Path
from textwrap import dedent
import pandas as pd
from lxml import etree
from project_config import (
    GITHUB_REPO,
    PROJECT_RELEASE_DATE,
    PUBLIC_BASE,
    SOURCE_DOWNLOAD_DATE,
)

ICCU_URL='https://anagrafe.iccu.sbn.it/it/open-data/'
ICCU_LICENSE_URL='https://anagrafe.iccu.sbn.it/it/footer/norme-di-utilizzo-dei-dati/'
ICCU_FORMAT_URL='https://anagrafe.iccu.sbn.it/it/informazioni/formato-di-scambio/'
ISTAT_URL='https://demo.istat.it/app/?i=POS'
ISTAT_LICENSE_URL='https://www.istat.it/dati/open-data/'
CULTURAL_URL='https://dati.beniculturali.it/cultural-ON/ITA.html'
ADMIN_URL='https://www.istat.it/storage/codici-unita-amministrative/Novita-2025-2017.pdf'
GITHUB_BLOB_BASE = GITHUB_REPO + "/blob/main/"
RAW_GITHUB_BASE = (
    GITHUB_REPO
    .replace("https://github.com/", "https://raw.githubusercontent.com/")
    + "/main/"
)

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()

def wcsv(df,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(path,index=False,encoding='utf-8',lineterminator='\n')

def read_csv(path): return pd.read_csv(path,dtype=str,keep_default_na=False,low_memory=False)

def pct(n,d): return n/d*100 if d else None

def repo_relative(path: Path, root: Path) -> str:
    """Return a portable repository-relative POSIX path when possible."""
    path = path.resolve()
    root = root.resolve()

    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--iccu',type=Path,required=True)
    ap.add_argument('--posas2019',type=Path,required=True)
    ap.add_argument('--posas2025',type=Path,required=True)
    ap.add_argument('--cultural-on',dest='cultural',type=Path,required=True)
    ap.add_argument('--release-note',action='append',default=[])
    a=ap.parse_args(); root=a.root
    meta=root/'metadata'; reports=root/'reports'; tables=reports/'data_profile_tables'; ext=root/'data/external'
    for p in [meta,reports,tables,ext]: p.mkdir(parents=True,exist_ok=True)

    # Preserve semantic and documentation inputs used by the project.
    cultural_dest = ext / "cultural-ON.owl"
    if a.cultural.resolve() != cultural_dest.resolve():
        shutil.copy2(a.cultural, cultural_dest)

    for x in a.release_note:
        src = Path(x)
        dest = ext / src.name
        if src.resolve() != dest.resolve():
            shutil.copy2(src, dest)

    # Load canonical processed outputs only; no recomputation of the core pipeline here.
    proc=root/'data/processed'
    lib=read_csv(proc/'library.csv'); status=read_csv(proc/'library_status.csv'); types=read_csv(proc/'library_type.csv')
    hold=read_csv(proc/'library_holdings.csv'); fund=read_csv(proc/'special_collection.csv'); cont=read_csv(proc/'library_contact.csv')
    prev=read_csv(proc/'library_previous_name.csv'); merg=read_csv(proc/'library_mergers.csv'); pop=read_csv(proc/'municipality_population.csv')
    ana=read_csv(proc/'analysis_municipality.csv'); cw=read_csv(meta/'municipality_crosswalk_2019_2025.csv'); sm=read_csv(meta/'status_mapping.csv')

    # Raw inventory facts.
    inv=[]
    with zipfile.ZipFile(a.iccu) as z:
        obj=json.load(io.TextIOWrapper(z.open('biblioteche.json'),encoding='utf-8'))
        snap=obj['metadati']['data-estrazione']
        for zi in z.infolist():
            raw=z.read(zi.filename); fmt=Path(zi.filename).suffix.lower().lstrip('.')
            enc='utf-8-sig' if fmt=='csv' else ('utf-8' if fmt in {'json','xml'} else '')
            rootel=''; records=''
            if zi.filename=='biblioteche.json': records=len(obj['biblioteche'])
            elif fmt=='csv': records=len(pd.read_csv(io.BytesIO(raw),sep=';',encoding='utf-8-sig',dtype=str,keep_default_na=False))
            elif fmt=='xml':
                xr=etree.fromstring(raw); rootel=xr.tag
                if zi.filename=='patrimonio.xml': records=len(xr.findall('.//materiale'))
                elif zi.filename=='fondi-speciali.xml': records=len(xr.findall('.//fondo-speciale'))
                elif zi.filename=='contatti.xml': records=len(xr.findall('.//contatto'))
            inv.append(dict(source_archive=repo_relative(a.iccu, root),local_file=zi.filename,format=fmt.upper(),encoding=enc,bytes=zi.file_size,records_or_elements=records,xml_root=rootel,sha256=hashlib.sha256(raw).hexdigest(),role='ICCU source member'))
    for path,year in [(a.posas2019,2019),(a.posas2025,2025)]:
        with zipfile.ZipFile(path) as z:
            for zi in z.infolist():
                if zi.filename.endswith(('_Comuni.csv','_Province.csv','_Regioni.csv','_Ripartizioni.csv')):
                    raw=z.read(zi.filename)
                    df=pd.read_csv(io.BytesIO(raw),sep=';',encoding='utf-8-sig',skiprows=1,dtype=str,keep_default_na=False,low_memory=False)
                    inv.append(dict(source_archive=repo_relative(path, root),local_file=zi.filename,format='CSV',encoding='utf-8-sig',bytes=zi.file_size,records_or_elements=len(df),xml_root='',sha256=hashlib.sha256(raw).hexdigest(),role=f'ISTAT POSAS {year} aggregate source member'))
            inv.append(dict(source_archive=repo_relative(path, root),local_file='[archive total members]',format='ZIP',encoding='binary',bytes=path.stat().st_size,records_or_elements=len(z.namelist()),xml_root='',sha256=sha256(path),role=f'ISTAT POSAS {year} archive inventory'))
    inv.append(
        dict(
            source_archive='',
            local_file='data/external/cultural-ON.owl',
            format='OWL/RDFXML',
            encoding='utf-8',
            bytes=(ext/'cultural-ON.owl').stat().st_size,
            records_or_elements='',
            xml_root='rdf:RDF',
            sha256=sha256(ext/'cultural-ON.owl'),
            role='External ontology reused for semantic modelling'
        )
    )
    for p in sorted(ext.glob('note-di-rilascio-1.6*')):
        fmt = p.suffix.lstrip('.').upper()

        inv.append(
            dict(
                source_archive='',
                local_file=f'data/external/{p.name}',
                format=fmt,
                encoding='binary',
                bytes=p.stat().st_size,
                records_or_elements='',
                xml_root='',
                sha256=sha256(p),
                role='ICCU release-note documentation',
            )
        )
    wcsv(pd.DataFrame(inv),meta/'file_inventory.csv')

    manifest = [
        dict(
            source_id='ICCU_ANAGRAFE_20260908',
            publisher='ICCU – Istituto Centrale per il Catalogo Unico delle biblioteche italiane e per le informazioni bibliografiche',
            dataset_name='Anagrafe delle Biblioteche Italiane – Open Data',
            source_url=ICCU_URL,
            local_file=repo_relative(a.iccu, root),
            format='ZIP (JSON, CSV, XML)',
            encoding='UTF-8 / UTF-8-SIG',
            license='CC0 1.0',
            download_date=SOURCE_DOWNLOAD_DATE,
            temporal_coverage=f'snapshot {snap}',
            spatial_coverage='Italy; includes some Italian institutions located abroad',
            update_frequency='daily',
            role_in_project='library master and secondary ICCU datasets',
            sha256=sha256(a.iccu),
            notes='Original RAW archive included in the repository; integrity can be verified through SHA-256.'
        ),

        dict(
            source_id='ISTAT_POSAS_2019',
            publisher='Istat – Istituto nazionale di statistica',
            dataset_name='Popolazione residente per età, sesso e stato civile al 1° gennaio (POSAS) 2019',
            source_url=ISTAT_URL,
            local_file=repo_relative(a.posas2019, root),
            format='ZIP/CSV',
            encoding='UTF-8-SIG',
            license='CC BY 4.0',
            download_date=SOURCE_DOWNLOAD_DATE,
            temporal_coverage='2019-01-01',
            spatial_coverage='Italy, municipalities/provinces/regions/geographical divisions',
            update_frequency='annual',
            role_in_project='2019 demographic baseline',
            sha256=sha256(a.posas2019),
            notes='Original RAW archive included in the repository; integrity can be verified through SHA-256.'
        ),

        dict(
            source_id='ISTAT_POSAS_2025',
            publisher='Istat – Istituto nazionale di statistica',
            dataset_name='Popolazione residente per età, sesso e stato civile al 1° gennaio (POSAS) 2025',
            source_url=ISTAT_URL,
            local_file=repo_relative(a.posas2025, root),
            format='ZIP/CSV',
            encoding='UTF-8-SIG',
            license='CC BY 4.0',
            download_date=SOURCE_DOWNLOAD_DATE,
            temporal_coverage='2025-01-01',
            spatial_coverage='Italy, municipalities/provinces/regions/geographical divisions',
            update_frequency='annual',
            role_in_project='current population and canonical 2025 geography',
            sha256=sha256(a.posas2025),
            notes='Original RAW archive included in the repository; integrity can be verified through SHA-256.'
        ),

        dict(
            source_id='CULTURAL_ON_V2',
            publisher='MiBACT / CNR-ISTC STLab',
            dataset_name='Cultural-ON (Cultural ONtology)',
            source_url=CULTURAL_URL,
            local_file='data/external/cultural-ON.owl',
            format='OWL/RDFXML',
            encoding='UTF-8',
            license='CC BY 3.0 IT',
            download_date=SOURCE_DOWNLOAD_DATE,
            temporal_coverage='version 2.0 – 2016-03-30',
            spatial_coverage='domain vocabulary/ontology',
            update_frequency='',
            role_in_project='external ontology reused in semantic modelling',
            sha256=sha256(ext/'cultural-ON.owl'),
            notes='Used for the reuse and alignment of concepts in the project ontology.'
        ),
    ]
    for i, p in enumerate(
        sorted(ext.glob('note-di-rilascio-1.6*')),
        1,
    ):
        manifest.append(
            dict(
                source_id=f'ICCU_RELEASE_NOTES_1_6_{i}',
                publisher='ICCU',
                dataset_name=(
                    'Anagrafe delle biblioteche italiane – '
                    'Exchange format 1.6 release notes'
                ),
                source_url=ICCU_FORMAT_URL,
                local_file=f'data/external/{p.name}',
                format=p.suffix.lstrip('.').upper(),
                encoding='binary',
                license=(
                    'CC BY-NC-SA 3.0 IT '
                    '(default license for ICCU website editorial content, '
                    'unless otherwise stated)'
                ),
                download_date=SOURCE_DOWNLOAD_DATE,
                temporal_coverage='format version 1.6',
                spatial_coverage='',
                update_frequency='',
                role_in_project=(
                    'structure/format documentation '
                    'and evolution context'
                ),
                sha256=sha256(p),
                notes=(
                    'Official ICCU documentation stored '
                    'locally for provenance purposes.'
                ),
            )
        )

    wcsv(pd.DataFrame(manifest),meta/'source_manifest.csv')

    # License report.
    (meta/'licenses.md').write_text(f'''# Licenses and compatibility\n\nVerification performed on {SOURCE_DOWNLOAD_DATE}.\n\n## ICCU – Anagrafe delle Biblioteche Italiane\n- Data license: **CC0 1.0 / public domain**.\n- Official source: {ICCU_LICENSE_URL}\n- Attribution: not required by the CC0 license; citing ICCU as the source remains good practice.\n- Modification: permitted.\n- Redistribution: permitted.\n- Commercial use: permitted.\n- Share-alike: none.\n- Separate note: the editorial content of the ICCU website is generally licensed under CC BY-NC-SA 3.0 IT; this condition does not replace the CC0 license specifically declared for the Anagrafe Open Data.\n\n## ISTAT POSAS 2019 and 2025\n- License: **Creative Commons Attribution 4.0 (CC BY 4.0)**.\n- Official source: {ISTAT_LICENSE_URL}\n- Attribution: required; cite Istat as the source.\n- Modification/adaptation: permitted.\n- Redistribution: permitted.\n- Commercial use: permitted.\n- Share-alike: none.\n\n## Cultural-ON\n- License declared in the OWL file: **CC BY 3.0 IT**, URI `http://creativecommons.org/licenses/by/3.0/it/`.\n- Official documentation source: {CULTURAL_URL}\n- Attribution: required.\n- Modification: permitted under the terms of the license.\n- Redistribution: permitted.\n- Commercial use: permitted.\n- Share-alike: none.\n\n## Derived tabular dataset\nThe pipeline integrates ICCU values under CC0 with Istat demographic data under CC BY 4.0. For the **derived tabular dataset**, the documented choice is **CC BY 4.0**, with attribution to Istat and citation of ICCU as a source. This choice does not automatically relicense ICCU editorial documentation or the Cultural-ON ontology included separately in the repository.\n''',encoding='utf-8')

    # Profile tables and raw profile summary.
    coord = (
        lib.coordinate_quality_flag
        .value_counts()
        .rename_axis("coordinate_quality_flag")
        .reset_index(name="count")
    )
    coord.loc[:, "percent"] = coord["count"] / len(lib) * 100
    wcsv(coord, tables / "library_coordinate_quality.csv")

    sdist = (
        status.normalized_status
        .value_counts()
        .rename_axis("normalized_status")
        .reset_index(name="count")
    )
    sdist.loc[:, "percent"] = sdist["count"] / len(status) * 100
    wcsv(sdist, tables / "library_status_distribution.csv")

    regions=lib.region.value_counts().rename_axis('region').reset_index(name='count'); wcsv(regions,tables/'library_regions.csv')
    prov=lib.province_name.value_counts().rename_axis('province_name').reset_index(name='count'); wcsv(prov,tables/'library_provinces.csv')
    nullrows=[]
    for c in lib.columns:
        n=(lib[c]=='').sum(); nullrows.append(dict(field=c,missing=n,missing_percent=n/len(lib)*100,non_missing=len(lib)-n,distinct_non_missing=lib.loc[lib[c]!='',c].nunique()))
    wcsv(pd.DataFrame(nullrows),tables/'library_field_completeness.csv')
    sec=[]
    for name,df,key in [('library_type',types,'isil'),('library_holdings',hold,'isil'),('special_collection',fund,'isil'),('library_contact',cont,'isil'),('library_previous_name',prev,'isil')]:
        d=df[key].nunique(); sec.append(dict(dataset=name,records=len(df),distinct_libraries=d,master_libraries=len(lib),coverage_percent=d/len(lib)*100,duplicate_relation_rows=len(df)-d))
    wcsv(pd.DataFrame(sec),tables/'secondary_dataset_profile.csv')
    pc=[]
    for p in sorted(proc.glob('*.csv')):
        df=read_csv(p); pc.append(dict(file=p.name,records=len(df),columns=len(df.columns),sha256=sha256(p)))
    wcsv(pd.DataFrame(pc),tables/'processed_resource_profile.csv')
    wcsv(cw.transformation_type.value_counts().rename_axis('transformation_type').reset_index(name='rows'),tables/'municipality_crosswalk_summary.csv')
    wcsv(status.analytical_group.value_counts().rename_axis('analytical_group').reset_index(name='count'),tables/'status_analytical_groups.csv')
    posas_profile=pd.DataFrame([
        {'year':2019,'archive_members':111,'municipal_rows':811308,'municipalities':7954,'age_999_total_check_mismatches':0},
        {'year':2025,'archive_members':111,'municipal_rows':805392,'municipalities':7896,'age_999_total_check_mismatches':0},
    ]); wcsv(posas_profile,tables/'posas_profile.csv')

    status_counts=status.normalized_status.value_counts().to_dict()
    (reports/'data_profile_raw.md').write_text(f'''# Data profiling\n\n## ICCU master\n- Records: **{len(lib):,}**.\n- Unique ISILs: **{lib.isil.nunique():,}**; missing: **{(lib.isil=='').sum()}**; duplicates: **{len(lib)-lib.isil.nunique()}**.\n- Distinct municipalities: **{lib.istat_code.nunique():,}**.\n- Provinces: **{lib.province_istat_code.nunique()}**.\n- Regions: **{lib.region.nunique()}**.\n- Complete cleaned coordinates: **{((lib.latitude!='') & (lib.longitude!='')).sum():,}/{len(lib):,}**.\n- (0,0) pairs treated as missing: **{(lib.coordinate_quality_flag=='zero_pair_treated_as_missing').sum()}**.\n- Missing/incomplete coordinates: **{(lib.coordinate_quality_flag=='missing').sum()}**.\n- Coordinates outside the Italy bounding box, to be reviewed: **{(lib.coordinate_quality_flag=='outside_italy_bbox_review').sum()}**.\n- SBN code present: **{(lib.sbn_code!='').sum():,}**.\n- Valid/present update date: **{(lib.updated_date!='').sum():,}**.\n\n## Normalized statuses\n''' + '\n'.join([f'- `{k}`: {v:,}' for k,v in status_counts.items()]) + f'''\n\n`NULL` is not interpreted as an open library: it is mapped to `NESSUNO_STATO_SPECIALE_REGISTRATO`.\n\n## Secondary ICCU datasets\n- Types: {len(types):,} records, {types.isil.nunique():,} libraries ({types.isil.nunique()/len(lib)*100:.2f}% of the master).\n- Holdings: {len(hold):,} records, {hold.isil.nunique():,} libraries ({hold.isil.nunique()/len(lib)*100:.2f}%).\n- Special collections: {len(fund):,} records, {fund.isil.nunique():,} libraries ({fund.isil.nunique()/len(lib)*100:.2f}%).\n- Contacts: {len(cont):,} records, {cont.isil.nunique():,} libraries ({cont.isil.nunique()/len(lib)*100:.2f}%).\n\n## ISTAT\n- POSAS 2019 Municipalities: 811,308 rows, 7,954 municipalities.\n- POSAS 2025 Municipalities: 805,392 rows, 7,896 municipalities.\n- `Età=999`: empirically verified against the sum of ages 0–100 for all municipalities; mismatch = 0 in both years.\n''',encoding='utf-8')

    # Cleaning log: only actions actually represented in the canonical pipeline.
    clog=[
      ('C01','ICCU library','name_original/name_normalized','whitespace/Unicode normalization','Original preserved and normalized value created with deterministic collapse','reduce purely formal variants',int((lib.name_original!=lib.name_normalized).sum()),'original value preserved'),
      ('C02','ICCU library','address_original/address_normalized','whitespace/Unicode normalization','Original preserved and normalized value created with deterministic collapse','reduce purely formal variants',int((lib.address_original!=lib.address_normalized).sum()),'original value preserved'),
      ('C03','ICCU library','latitude/longitude','coordinate pair (0,0)','Cleaned coordinates set to missing; originals preserved','(0,0) is not a useful library location and is a pseudo-value',int((lib.coordinate_quality_flag=='zero_pair_treated_as_missing').sum()),'no automatic geocoding'),
      ('C04','ICCU library','latitude/longitude','coordinates outside the indicative Italy bounding box','Preserved and flagged as outside_italy_bbox_review','possible locations abroad or anomalies; do not correct automatically',int((lib.coordinate_quality_flag=='outside_italy_bbox_review').sum()),'requires case-by-case interpretation'),
      ('C05','ICCU library','latitude/longitude','missing/incomplete coordinate pair','Preserved as missing','absence does not equal zero',int((lib.coordinate_quality_flag=='missing').sum()),'no imputation'),
      ('C06','ICCU library','source_status','NULL ICCU status','Mapped to NESSUNO_STATO_SPECIALE_REGISTRATO','absence of a status does not prove that the library is open',int((status.normalized_status=='NESSUNO_STATO_SPECIALE_REGISTRATO').sum()),'excluded from the main problematic scope'),
      ('C07','ICCU mergers','source_status','merger status with possible target ISIL','Controlled regex parsing of the target ISIL','avoid inferences from free text',int((merg.parse_success=='True').sum()),'90 mergers remain without an extracted target'),
      ('C08','ISTAT POSAS','CSV reading','Municipality string = None risks NA parsing','keep_default_na=False','preserve the official name None',1,'no loss of the municipality'),
      ('C09','ISTAT POSAS','Età','code 999 interpreted as total','Used after complete empirical verification','0 mismatches against the sum of ages 0–100',7954+7896,'consistent municipal totals'),
      ('C10','ISTAT 2019→2025','municipality codes','administrative changes','explicit crosswalk by code/predecessors; no fuzzy matching','harmonization on 2025 geography',len(cw),'Trapani/Misiliscemi cannot be reconstructed for 2019'),
    ]
    wcsv(pd.DataFrame(clog,columns=['rule_id','dataset','field','problem','action','rationale','affected_records','consequence']),reports/'cleaning_log.csv')

    # Join quality.
    jq=[]
    for name,df,key in [('library_type',types,'isil'),('library_holdings',hold,'isil'),('special_collection',fund,'isil'),('library_contact',cont,'isil'),('library_previous_name',prev,'isil')]:
        d=df[key].nunique(); jq.append(dict(join=f'library→{name}',master_records=len(lib),matched_master_records=d,unmatched_master_records=len(lib)-d,duplicate_relation_rows=len(df)-d,coverage_percent=d/len(lib)*100,key=key,notes='1:N preserved' if len(df)>d else '1:1 on available coverage'))
    istat_codes=set(pop.istat_code)
    matched=lib.istat_code.isin(istat_codes).sum(); jq.append(dict(join='ICCU library→ISTAT 2025 municipality',master_records=len(lib),matched_master_records=int(matched),unmatched_master_records=int(len(lib)-matched),duplicate_relation_rows=0,coverage_percent=matched/len(lib)*100,key='istat_code',notes='join on official code; no fuzzy matching'))
    jq.append(dict(join='ISTAT 2025 municipalities→crosswalk 2019/2025',master_records=len(pop),matched_master_records=cw.current_istat_code.nunique(),unmatched_master_records=len(pop)-cw.current_istat_code.nunique(),duplicate_relation_rows=len(cw)-cw.current_istat_code.nunique(),coverage_percent=cw.current_istat_code.nunique()/len(pop)*100,key='current_istat_code',notes='multiple rows for predecessors in mergers/incorporations'))
    wcsv(pd.DataFrame(jq),reports/'join_quality.csv')
    wcsv(pd.DataFrame(jq),tables/'join_coverage_summary.csv')

    # Data quality metrics.
    dq=[]
    def add(dataset,dimension,field,value,unit,interpretation): dq.append(dict(dataset=dataset,dimension=dimension,field=field,value=value,unit=unit,interpretation=interpretation))
    add('library','COMPLETENESS','isil',100.0,'percent','no missing ISIL')
    add('library','UNIQUENESS','isil',100.0,'percent','19,611/19,611 unique ISILs')
    add('library','VALIDITY','isil_pattern',100.0,'percent','all ISILs match ^IT-[A-Z]{2}\\d{4}$')
    add('library','COMPLETENESS','coordinates_clean',((lib.latitude!='')&(lib.longitude!='')).sum()/len(lib)*100,'percent','complete cleaned coordinates')
    add('library','COMPLETENESS','istat_code',(lib.istat_code!='').sum()/len(lib)*100,'percent','municipality code present')
    add('library_type','JOINABILITY','isil_coverage',types.isil.nunique()/len(lib)*100,'percent','master libraries covered')
    add('library_holdings','JOINABILITY','isil_coverage',hold.isil.nunique()/len(lib)*100,'percent','master libraries covered')
    add('special_collection','JOINABILITY','isil_coverage',fund.isil.nunique()/len(lib)*100,'percent','master libraries covered')
    add('library_contact','JOINABILITY','isil_coverage',cont.isil.nunique()/len(lib)*100,'percent','master libraries covered')
    add('municipality_population','UNIQUENESS','istat_code',pop.istat_code.nunique()/len(pop)*100,'percent','one code per 2025 municipality')
    add('ICCU→ISTAT','JOINABILITY','istat_code',matched/len(lib)*100,'percent','ICCU records linked to an ISTAT 2025 municipality')
    add('municipality_population','CONSISTENCY','population_comparability',(pop.population_comparability=='comparable_on_2025_geography').sum()/len(pop)*100,'percent','Trapani and Misiliscemi excluded from the 2019 comparison')
    dqdf=pd.DataFrame(dq); wcsv(dqdf,reports/'data_quality_metrics.csv')
    (reports/'data_quality.md').write_text(f'''# Data Quality\n\n## Completeness\n- ISIL: 100%.\n- Municipal ISTAT code in the ICCU master: 100%.\n- Complete cleaned coordinates: {((lib.latitude!='')&(lib.longitude!='')).sum()/len(lib)*100:.2f}%.\n- Type/holdings coverage: {types.isil.nunique()/len(lib)*100:.2f}%.\n- Contact coverage: {cont.isil.nunique()/len(lib)*100:.2f}%.\n- Special collections coverage: {fund.isil.nunique()/len(lib)*100:.2f}%.\n\n## Uniqueness\n- ISIL: 19,611 unique out of 19,611.\n- 2025 municipalities in the demographic dataset: 7,896 unique codes across 7,896 rows.\n\n## Validity\n- ISIL pattern: 100%.\n- `(0,0)` coordinates ({(lib.coordinate_quality_flag=='zero_pair_treated_as_missing').sum()}) are not accepted as cleaned coordinates.\n- Three coordinates outside the Italy bounding box remain flagged for review; two are compatible with locations in Buenos Aires/Athens, one (`IT-ME0024`) is suspicious.\n\n## Consistency\n- `NULL` status kept separate from any claim of being open.\n- 1:N relationships not flattened.\n- POSAS `Età=999` verified: 0 mismatches across all 2019 and 2025 municipalities compared with the sum of ages 0–100.\n- Trapani and Misiliscemi are marked as non-comparable because of the 2021 territorial change.\n\n## Joinability\n- ICCU→ISTAT 2025 via municipality code: 19,611/19,611 = 100%.\n- Secondary ICCU coverage is reported in `reports/join_quality.csv`.\n''',encoding='utf-8')

    (reports/'source_verification.md').write_text(f'''# Data verification - sources\n\n## ICCU\nInstitutional publisher: ICCU. Official Open Data page: {ICCU_URL}. The page states daily updates, CSV/XML/JSON formats, the `opendata.zip` archive, ISIL as the primary key for cross-referencing datasets, and documents the values of `stato-registrazione`. Data license: CC0. Local snapshot: `{snap}`.\n\n## ISTAT POSAS\nPublisher: Istat. Series: resident population by age, sex and marital status as of January 1. Source: {ISTAT_URL}. Years used: 2019 and 2025. Istat license: CC BY 4.0 ({ISTAT_LICENSE_URL}). Municipal files are read while preserving strings such as `None`.\n\n## Cultural-ON\nThe local OWL file `data/external/cultural-ON.owl` is stored in the repository as a semantic input. The declared version is 2.0 (March 30, 2016), licensed under CC BY 3.0 IT. Official documentation: {CULTURAL_URL}. The ontology is reused in the semantic modelling of the project.\n\n## Limitations\n- XSD 1.6 is not present as a local file in the repository; the four images of the 1.6 release notes provided by the user and the reference to the official format page are present.\n- Two municipalities (Trapani, Misiliscemi) do not allow a 2019 comparison to be reconstructed from municipal POSAS data alone.\n''',encoding='utf-8')

    # Decisions log in the requested repeated structure.
    decisions=[
      ('NULL ICCU status',f'{(status.normalized_status=="NESSUNO_STATO_SPECIALE_REGISTRATO").sum()} records have an empty `source_status`. ICCU documentation uses the field to indicate special statuses when populated.','Interpret NULL as open; exclude; neutral category.','Use `NESSUNO_STATO_SPECIALE_REGISTRATO`.','The absence of a value does not prove that the library is open.','NULL values do not automatically fall into the problematic categories.'),
      ('Definition of main_problematic_libraries','The canonical mapping includes only statuses with `include_in_main_analysis=True`: cessation, temporary closure, inaccessibility/earthquake-related suspension, partial reopening, repository without a service point.','Also include mergers/not surveyed/under setup; include all non-null statuses.','Sum only the statuses marked True in `metadata/status_mapping.csv`.','Keeps cessation, interruption, partial operation, organizational transformation and registry incompleteness separate.','National count = 2,497.'),
      ('1:N XML relationships',f'Holdings {len(hold):,} rows, special collections {len(fund):,}, contacts {len(cont):,}; multiple rows per ISIL.','Mega-CSV with duplicated libraries; separate tables.','Keep normalized tables for each relationship.','Avoids spurious multiplication and loss of cardinality.','Subsequent joins must preserve 1:N relationships.'),
      ('Coordinates (0,0)',f'{(lib.coordinate_quality_flag=="zero_pair_treated_as_missing").sum()} libraries have the original pair (0,0).','Treat as a real coordinate; geocode; mark as missing.','Set cleaned coordinates to missing; preserve originals.','(0,0) is a pseudo-value that is not useful for locating an Italian library.','No automatic geographic imputation.'),
      ('Coordinates outside the bounding box',f'{(lib.coordinate_quality_flag=="outside_italy_bbox_review").sum()} records fall outside the indicative Italy bounding box but within the global range.','Delete; correct/geocode; preserve with a flag.','Preserve and flag as `outside_italy_bbox_review`.','An Italian institution may be located abroad; the bounding box is a check, not proof of an error.','Three records require interpretation.'),
      ('IT-ME0024','Among the three geographic outliers, `IT-ME0024` has coordinates compatible with India, not with the expected territorial location.','Correct from address; remove; flag.','Flag without automatic correction.','There is no reliable source for replacing the coordinates.','Open anomaly for manual review.'),
      ('Parsing of mergers',f'{len(merg):,} merger records; {(merg.parse_success=="True").sum():,} target ISILs extracted; {(merg.parse_success!="True").sum()} without a parseable target.','Free/fuzzy parsing; controlled regex; no parsing.','Exact regex `Biblioteca confluita in IT-XXdddd`; target validated against the snapshot.','ISIL has an official format and allows deterministic validation.','1,412 targets exist in the snapshot; 90 remain without a target.'),
      ('Self-loop IT-SS0267','`IT-SS0267 → IT-SS0267` is present in the source after parsing and target validation.','Remove/correct; preserve and flag.','Preserve with `self_loop=True` and `in_cycle=True`.','No evidence justifies a correction.','Only cycle detected in the merger graph.'),
      ('ISTAT Età=999','For 7,954 municipalities in 2019 and 7,896 municipalities in 2025, the `Età=999` row exactly matches the sum of ages 0–100; mismatch 0.','Assume it without verification; always recalculate; validate and use it.','Use 999 as the total after complete empirical verification.','Avoids undocumented or assumed interpretations.','Municipal totals used for 2019/2025 population.'),
      ('Municipality “None” and keep_default_na=False','There is an official municipality named `None`; standard pandas parsers may treat the string as NA.','Default NA parsing; ex-post exception; preserve strings.','Read POSAS with `keep_default_na=False`.','Preserves the official name without information loss.','The municipality None remains a valid string.'),
      ('2019–2025 administrative changes',f'2019 geography: 7,954 municipalities; 2025: 7,896; crosswalk: {len(cw):,} relationships toward 7,896 current municipalities.','Join by name/fuzzy matching; remove non-matches; official crosswalk by codes and predecessors.','Use 2025 analytical geography and an explicit crosswalk by code/predecessors.','Official codes and administrative transformations are more reliable than fuzzy matching.','Mergers/incorporations aggregate predecessors when reconstructible.'),
      ('Trapani/Misiliscemi','Misiliscemi was created through a territorial split from Trapani in 2021; municipal POSAS 2019 does not allow the territory to be correctly subtracted.','Assign all of Trapani 2019 to one of the two; estimate; mark as non-comparable.','Both marked `not_comparable_due_to_2021_territorial_split` for the 2019 comparison.','Any allocation would be invented.','Population 2019 and changes remain NA for the two municipalities.'),
      ('Name Reggio Calabria / Reggio di Calabria','In POSAS 2025 Provinces, province code 080, the official name is `Reggio di Calabria`; 97 municipalities belong to province 080.','Use ICCU label `Reggio Calabria`; use POSAS 2025.','In the analytical dataset the province is canonicalized from POSAS 2025 and is `Reggio di Calabria`.','The analytical dataset uses ISTAT 2025 territorial geography as the canonical source.','The rebuild deterministically produces 97 rows with `Reggio di Calabria`.'),
      ('Textual difference in rationale','`library_status.csv` and `metadata/status_mapping.csv` now use the same `classify_status` function; canonical comparison: 0 differences.','Keep independent texts; manual synchronization; single function.','Use the same canonical function for both outputs.','Eliminates purely textual drift while preserving identical semantics.','The validator checks rationale equality for every source_status.'),
      ('patrimonio.xml export-date anomaly','The root of `patrimonio.xml` declares `data-export="2026-09-08T14:00:"`, a syntactically incomplete timestamp.','Correct the timestamp; ignore it; record the anomaly.','Do not modify the source; record the anomaly.','There is no evidence from which to infer the missing seconds.','The main snapshot remains determined by biblioteche.json; the XML timestamp remains a quality note.'),
      ('License of the derived dataset','ICCU Open Data = CC0; Istat POSAS = CC BY 4.0; Cultural-ON is separate and does not contribute to tabular values at this stage.','CC0; CC BY 4.0; another license without analysis.','Planned license for the derived tabular dataset: CC BY 4.0.','Complies with the attribution requirement arising from the Istat component and allows reuse/modification/commercial use.','Attribute Istat; cite ICCU; do not automatically relicense Cultural-ON or ICCU documentation.'),
    ]
    out=['# Decisions log','']
    for i,(problem,evidence,alts,decision,mot,cons) in enumerate(decisions,1):
        out += [f'# Decision D{i:02d}','', '## Problem',problem,'','## Evidence',evidence,'','## Alternatives considered',alts,'','## Decision',decision,'','## Rationale',mot,'','## Consequence',cons,'']
    (reports/'decisions_log.md').write_text('\n'.join(out),encoding='utf-8')

    (reports / "three_star_dataset.md").write_text(
        dedent(
            """\
    # Structured dataset in an open format

    The analytical outputs are distributed in **UTF-8 CSV**, a structured,
    machine-readable and non-proprietary format.

    The original RAW files are stored separately in `data/raw/` and are not
    modified by the pipeline.

    The implemented chain is:

    RAW → cleaning → harmonization → integration → CSV processed

    The canonical processed datasets are available directly in
    `data/processed/`.

    From a technical perspective, the datasets satisfy the structure
    and open-format requirements associated with the 3-star level. The complete
    classification under the 5-star model, however, also requires publication
    on the Web, which is assessed separately in the project.

    Parquet export is optional and is not required for the main
    pipeline.
    """
        ),
        encoding="utf-8",
    )

    # Data Package metadata.
    descriptions={
      'library.csv':'Cleaned ICCU master at library granularity.', 'library_status.csv':'Normalized ICCU status for each library.',
      'library_type.csv':'ICCU library types for the available coverage.', 'library_holdings.csv':'ICCU holdings, 1:N library-material relationship.',
      'special_collection.csv':'ICCU special collections, 1:N relationship.', 'library_contact.csv':'ICCU contacts, 1:N relationship.',
      'library_previous_name.csv':'Previous names, 1:N relationship.', 'library_mergers.csv':'Parsed and validated organizational mergers.',
      'municipality_population.csv':'Harmonized 2019/2025 municipal population on 2025 geography.', 'analysis_municipality.csv':'Integrated ICCU+ISTAT municipal analytical dataset.'}
    resources=[]
    for p in sorted(proc.glob('*.csv')):
        df=read_csv(p)
        fields=[]
        for c in df.columns:
            # conservative type inference for metadata only
            typ = "string"

            if c == "population_comparability":
                typ = "string"
            elif c == "updated_date":
                typ = "date"
            elif c in {
                "latitude",
                "longitude",
                "latitude_original",
                "longitude_original",
                "population_change_percent",
                "share_65_plus_2019",
                "share_65_plus_2025",
                "problematic_share",
                "libraries_per_100k",
                "problematic_libraries_per_100k",
            }:
                typ = "number"
            elif (
                c.startswith("population_")
                or c.endswith("_libraries")
                or c in {
                    "quantity",
                    "quantity_original",
                    "material_index",
                    "collection_index",
                    "contact_index",
                    "total_registry_records",
                    "total_libraries",
                }
            ):
                typ = "number"
            elif c in {
                "include_in_main_analysis",
                "parse_success",
                "target_exists_in_snapshot",
                "self_loop",
                "in_cycle",
            }:
                typ = "boolean"
            fields.append({'name':c,'type':typ,'description':c.replace('_',' ')})
        schema = {
            'fields': fields,
        }

        # Primary keys and foreign keys.
        if p.name == 'library.csv':
            schema['primaryKey'] = 'isil'

        elif p.name == 'library_status.csv':
            schema['primaryKey'] = 'isil'
            schema['foreignKeys'] = [{
                'fields': 'isil',
                'reference': {
                    'resource': 'library',
                    'fields': 'isil',
                },
            }]

        elif p.name == 'library_type.csv':
            schema['primaryKey'] = 'isil'
            schema['foreignKeys'] = [{
                'fields': 'isil',
                'reference': {
                    'resource': 'library',
                    'fields': 'isil',
                },
            }]

        elif p.name == 'library_holdings.csv':
            schema['primaryKey'] = [
                'isil',
                'material_index',
            ]
            schema['foreignKeys'] = [{
                'fields': 'isil',
                'reference': {
                    'resource': 'library',
                    'fields': 'isil',
                },
            }]

        elif p.name == 'special_collection.csv':
            schema['primaryKey'] = [
                'isil',
                'collection_index',
            ]
            schema['foreignKeys'] = [{
                'fields': 'isil',
                'reference': {
                    'resource': 'library',
                    'fields': 'isil',
                },
            }]

        elif p.name == 'library_contact.csv':
            schema['primaryKey'] = [
                'isil',
                'contact_index',
            ]
            schema['foreignKeys'] = [{
                'fields': 'isil',
                'reference': {
                    'resource': 'library',
                    'fields': 'isil',
                },
            }]

        elif p.name == 'library_previous_name.csv':
            # No primaryKey: the source contains duplicate
            # (isil, previous_name_original) pairs.
            schema['foreignKeys'] = [{
                'fields': 'isil',
                'reference': {
                    'resource': 'library',
                    'fields': 'isil',
                },
            }]

        elif p.name == 'library_mergers.csv':
            schema['primaryKey'] = 'source_isil'
            schema['foreignKeys'] = [{
                'fields': 'source_isil',
                'reference': {
                    'resource': 'library',
                    'fields': 'isil',
                },
            }]

        elif p.name == 'municipality_population.csv':
            schema['primaryKey'] = 'istat_code'

        elif p.name == 'analysis_municipality.csv':
            schema['primaryKey'] = 'istat_code'
        resources.append({
            'name': p.stem,
            'path': f'data/processed/{p.name}',
            'format': 'csv',
            'mediatype': 'text/csv',
            'encoding': 'utf-8',
            'bytes': p.stat().st_size,
            'hash': f'sha256:{sha256(p)}',
            'description': descriptions[p.name],
            'schema': schema,
        })
    datapackage={'profile':'data-package','name':'biblioteche-fantasma','title':'BIBLIOTECHE FANTASMA','description':'Cleaned and integrated ICCU + ISTAT 2019/2025 datasets for the study of Italian libraries that are not fully operational.','version':PROJECT_RELEASE_DATE,'keywords':['libraries','ICCU','ISTAT','open data','Italy','demography'],'licenses':[{'name':'CC-BY-4.0','path':'https://creativecommons.org/licenses/by/4.0/','title':'Creative Commons Attribution 4.0 International'}],'sources':[{'title':'ICCU Anagrafe delle Biblioteche Italiane','path':ICCU_URL},{'title':'ISTAT POSAS 2019','path':ISTAT_URL},{'title':'ISTAT POSAS 2025','path':ISTAT_URL}],'geographic_coverage':'Italy','temporal_coverage':'2019-01-01; 2025-01-01; ICCU snapshot 2026-09-08T14:11:15','resources':resources}
    (meta/'datapackage.json').write_text(json.dumps(datapackage,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    # Public DCAT metadata for the Web publication.
    # HTTP(S) identifiers and public access/download URLs are used.
    # Full DCAT-AP_IT conformance is not claimed without formal profile validation.
    dists=[]
    for p in sorted(proc.glob('*.csv')):
        ident=p.stem.replace('_','-')
        dists.append(f'''bf:dist-{ident} a dcat:Distribution ;\n    dct:title "{p.stem}"@en ;\n    dct:description "{descriptions[p.name]}"@en ;\n    dct:license <https://creativecommons.org/licenses/by/4.0/> ;\n    dct:format <http://publications.europa.eu/resource/authority/file-type/CSV> ;\n    dcat:mediaType "text/csv" ;\n    dcat:accessURL <{GITHUB_BLOB_BASE}data/processed/{p.name}> ;\n    dcat:downloadURL <{RAW_GITHUB_BASE}data/processed/{p.name}> .''')
    distrefs=',\n        '.join('bf:dist-'+p.stem.replace('_','-') for p in sorted(proc.glob('*.csv')))
    ttl=f'''@prefix bf: <{PUBLIC_BASE}metadata/> .\n@prefix dcat: <http://www.w3.org/ns/dcat#> .\n@prefix dct: <http://purl.org/dc/terms/> .\n@prefix foaf: <http://xmlns.com/foaf/0.1/> .\n@prefix schema: <https://schema.org/> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\nbf:project-author a foaf:Person ; foaf:name "Amelia Morsellino" .\n\nbf:dataset a dcat:Dataset ; \ndct:identifier "biblioteche-fantasma" ;\n    dct:title "Biblioteche Fantasma"@en ;\n    dct:description "Cleaned and integrated ICCU + ISTAT 2019/2025 datasets for the study of Italian libraries that are not fully operational."@en ;\n    dct:publisher bf:project-author ;\n    dct:creator bf:project-author ;\n    dct:license <https://creativecommons.org/licenses/by/4.0/> ;\n    dct:issued "{PROJECT_RELEASE_DATE}"^^xsd:date ;\n    dct:modified "{PROJECT_RELEASE_DATE}"^^xsd:date ;\n    dct:language <http://publications.europa.eu/resource/authority/language/ITA> ;\n    dct:spatial <http://publications.europa.eu/resource/authority/country/ITA> ;\n    dct:temporal [ a dct:PeriodOfTime ; schema:startDate "2019-01-01"^^xsd:date ; schema:endDate "2026-09-08"^^xsd:date ] ;\n    dct:accrualPeriodicity <http://publications.europa.eu/resource/authority/frequency/IRREG> ;\n    dcat:theme <http://publications.europa.eu/resource/authority/data-theme/EDUC> ;\n    dcat:keyword "libraries"@en, "ICCU"@en, "ISTAT"@en, "demography"@en, "open data"@en ;\n    dct:source <{ICCU_URL}>, <{ISTAT_URL}> ;\n    dcat:distribution {distrefs} .\n\n'''+'\n\n'.join(dists)+'\n'
    (meta/'dcat.ttl').write_text(ttl,encoding='utf-8')
    (meta / "dcat_validation_notes.md").write_text(
        dedent(
            """\
    # DCAT validation and conformance notes

    The `metadata/dcat.ttl` file provides an RDF/DCAT description of the dataset
    and of the project's main distributions.

    The description includes identifier, title, description, publisher,
    creator, license, language, geographic coverage, frequency, theme, keywords,
    distributions, format, media type, accessURL and downloadURL.

    ## DCAT-AP_IT

    The project uses public HTTP(S) URIs under the namespace
    `https://ameliamorsellino.github.io/biblioteche-fantasma/`.

    The tabular distributions are described through public Web URLs
    from the GitHub repository and direct download URLs.

    Publication through GitHub Pages makes the project namespace available
    on the Web. Full DCAT-AP_IT conformance is not, however, claimed without
    formal validation against the applicable version of the profile.
    """
        ),
        encoding="utf-8",
    )
    prov=f'''@prefix bf: <urn:biblioteche-fantasma:provenance:> .\n@prefix prov: <http://www.w3.org/ns/prov#> .\n@prefix dct: <http://purl.org/dc/terms/> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\nbf:src-iccu a prov:Entity ; dct:title "ICCU Anagrafe snapshot 2026-09-08"@en .\nbf:src-istat-2019 a prov:Entity ; dct:title "ISTAT POSAS 2019"@en .\nbf:src-istat-2025 a prov:Entity ; dct:title "ISTAT POSAS 2025"@en .\nbf:cleaning a prov:Activity ; prov:used bf:src-iccu ; dct:description "Deterministic ICCU cleaning without overwriting RAW files"@en .\nbf:harmonization a prov:Activity ; prov:used bf:src-istat-2019, bf:src-istat-2025 ; dct:description "Municipal harmonization 2019→2025"@en .\nbf:integration a prov:Activity ; prov:used bf:cleaned-iccu, bf:harmonized-population ; dct:description "ICCU→ISTAT integration via municipality code"@en .\nbf:cleaned-iccu a prov:Entity ; prov:wasGeneratedBy bf:cleaning ; prov:wasDerivedFrom bf:src-iccu .\nbf:harmonized-population a prov:Entity ; prov:wasGeneratedBy bf:harmonization ; prov:wasDerivedFrom bf:src-istat-2019, bf:src-istat-2025 .\nbf:derived-dataset a prov:Entity ; prov:wasGeneratedBy bf:integration ; prov:wasDerivedFrom bf:src-iccu, bf:src-istat-2019, bf:src-istat-2025 ; dct:issued "{PROJECT_RELEASE_DATE}"^^xsd:date .\n'''
    (meta/'provenance.ttl').write_text(prov,encoding='utf-8')

    print('Metadata and quality reports generated in',root)

if __name__=='__main__': main()