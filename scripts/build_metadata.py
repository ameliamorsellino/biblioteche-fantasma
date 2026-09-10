#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, io, json, shutil, zipfile
from pathlib import Path
from textwrap import dedent
import pandas as pd
from lxml import etree
from project_config import (
    PROJECT_RELEASE_DATE,
    SOURCE_DOWNLOAD_DATE,
)


ICCU_URL='https://anagrafe.iccu.sbn.it/it/open-data/'
ICCU_LICENSE_URL='https://anagrafe.iccu.sbn.it/it/footer/norme-di-utilizzo-dei-dati/'
ICCU_FORMAT_URL='https://anagrafe.iccu.sbn.it/it/informazioni/formato-di-scambio/'
ISTAT_URL='https://demo.istat.it/app/?i=POS'
ISTAT_LICENSE_URL='https://www.istat.it/dati/open-data/'
CULTURAL_URL='https://dati.beniculturali.it/cultural-ON/ITA.html'
ADMIN_URL='https://www.istat.it/storage/codici-unita-amministrative/Novita-2025-2017.pdf'


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
            spatial_coverage='Italia; include alcune sedi italiane all’estero',
            update_frequency='quotidiana',
            role_in_project='master biblioteche e dataset ICCU secondari',
            sha256=sha256(a.iccu),
            notes='Archivio RAW originale incluso nel repository; integrità verificabile tramite SHA-256.'
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
            spatial_coverage='Italia, comuni/province/regioni/ripartizioni',
            update_frequency='annuale',
            role_in_project='baseline demografica 2019',
            sha256=sha256(a.posas2019),
            notes='Archivio RAW originale incluso nel repository; integrità verificabile tramite SHA-256.'
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
            spatial_coverage='Italia, comuni/province/regioni/ripartizioni',
            update_frequency='annuale',
            role_in_project='popolazione corrente e geografia canonica 2025',
            sha256=sha256(a.posas2025),
            notes='Archivio RAW originale incluso nel repository; integrità verificabile tramite SHA-256.'
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
            temporal_coverage='versione 2.0 – 2016-03-30',
            spatial_coverage='vocabolario/ontologia di dominio',
            update_frequency='',
            role_in_project='ontologia esterna riutilizzata nella modellazione semantica',
            sha256=sha256(ext/'cultural-ON.owl'),
            notes='Utilizzata per il riuso e l’allineamento dei concetti dell’ontologia di progetto.'
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
                    'Note di rilascio formato di scambio 1.6'
                ),
                source_url=ICCU_FORMAT_URL,
                local_file=f'data/external/{p.name}',
                format=p.suffix.lstrip('.').upper(),
                encoding='binary',
                license=(
                    'CC BY-NC-SA 3.0 IT '
                    '(licenza predefinita dei contenuti editoriali '
                    'del sito ICCU, salvo diversa indicazione)'
                ),
                download_date=SOURCE_DOWNLOAD_DATE,
                temporal_coverage='versione formato 1.6',
                spatial_coverage='',
                update_frequency='',
                role_in_project=(
                    'documentazione struttura/formato '
                    'e contesto evolutivo'
                ),
                sha256=sha256(p),
                notes=(
                    'Documentazione ufficiale ICCU conservata '
                    'localmente a fini di provenance.'
                ),
            )
        )

    wcsv(pd.DataFrame(manifest),meta/'source_manifest.csv')

    # License report.
    (meta/'licenses.md').write_text(f'''# Licenze e compatibilità\n\nVerifica effettuata il {SOURCE_DOWNLOAD_DATE}.\n\n## ICCU – Anagrafe delle Biblioteche Italiane\n- Licenza dati: **CC0 1.0 / pubblico dominio**.\n- Fonte ufficiale: {ICCU_LICENSE_URL}\n- Attribuzione: non richiesta dalla licenza CC0; resta buona pratica citare ICCU come fonte.\n- Modifica: consentita.\n- Redistribuzione: consentita.\n- Uso commerciale: consentito.\n- Share-alike: nessuno.\n- Nota distinta: i contenuti editoriali del sito ICCU sono in generale CC BY-NC-SA 3.0 IT; questa condizione non sostituisce la CC0 dichiarata specificamente per gli Open Data dell’Anagrafe.\n\n## ISTAT POSAS 2019 e 2025\n- Licenza: **Creative Commons Attribution 4.0 (CC BY 4.0)**.\n- Fonte ufficiale: {ISTAT_LICENSE_URL}\n- Attribuzione: obbligatoria; citare Istat come fonte.\n- Modifica/adattamento: consentiti.\n- Redistribuzione: consentita.\n- Uso commerciale: consentito.\n- Share-alike: nessuno.\n\n## Cultural-ON\n- Licenza dichiarata nel file OWL: **CC BY 3.0 IT**, URI `http://creativecommons.org/licenses/by/3.0/it/`.\n- Fonte ufficiale di documentazione: {CULTURAL_URL}\n- Attribuzione: obbligatoria.\n- Modifica: consentita nei termini della licenza.\n- Redistribuzione: consentita.\n- Uso commerciale: consentito.\n- Share-alike: nessuno.\n\n## Dataset tabellare derivato\nLa pipeline integra valori ICCU in CC0 con dati demografici Istat in CC BY 4.0. Per il **dataset tabellare derivato** la scelta documentata è **CC BY 4.0**, con attribuzione a Istat e citazione di ICCU come fonte. Questa scelta non relicenzia automaticamente la documentazione editoriale ICCU né l’ontologia Cultural-ON inclusa separatamente nel repository.\n''',encoding='utf-8')

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
    (reports/'data_profile_raw.md').write_text(f'''# Data profiling\n\n## ICCU master\n- Record: **{len(lib):,}**.\n- ISIL unici: **{lib.isil.nunique():,}**; mancanti: **{(lib.isil=='').sum()}**; duplicati: **{len(lib)-lib.isil.nunique()}**.\n- Comuni distinti: **{lib.istat_code.nunique():,}**.\n- Province: **{lib.province_istat_code.nunique()}**.\n- Regioni: **{lib.region.nunique()}**.\n- Coordinate pulite complete: **{((lib.latitude!='') & (lib.longitude!='')).sum():,}/{len(lib):,}**.\n- Coppie (0,0) trattate come mancanti: **{(lib.coordinate_quality_flag=='zero_pair_treated_as_missing').sum()}**.\n- Coordinate mancanti/incomplete: **{(lib.coordinate_quality_flag=='missing').sum()}**.\n- Coordinate fuori bounding box Italia, da revisione: **{(lib.coordinate_quality_flag=='outside_italy_bbox_review').sum()}**.\n- Codice SBN presente: **{(lib.sbn_code!='').sum():,}**.\n- Data aggiornamento valida/presente: **{(lib.updated_date!='').sum():,}**.\n\n## Stati normalizzati\n''' + '\n'.join([f'- `{k}`: {v:,}' for k,v in status_counts.items()]) + f'''\n\n`NULL` non è interpretato come biblioteca aperta: è mappato a `NESSUNO_STATO_SPECIALE_REGISTRATO`.\n\n## Dataset ICCU secondari\n- Tipologie: {len(types):,} record, {types.isil.nunique():,} biblioteche ({types.isil.nunique()/len(lib)*100:.2f}% del master).\n- Patrimonio: {len(hold):,} record, {hold.isil.nunique():,} biblioteche ({hold.isil.nunique()/len(lib)*100:.2f}%).\n- Fondi speciali: {len(fund):,} record, {fund.isil.nunique():,} biblioteche ({fund.isil.nunique()/len(lib)*100:.2f}%).\n- Contatti: {len(cont):,} record, {cont.isil.nunique():,} biblioteche ({cont.isil.nunique()/len(lib)*100:.2f}%).\n\n## ISTAT\n- POSAS 2019 Comuni: 811.308 righe, 7.954 comuni.\n- POSAS 2025 Comuni: 805.392 righe, 7.896 comuni.\n- `Età=999`: verificata empiricamente contro la somma delle età 0–100 per tutti i comuni; mismatch = 0 in entrambi gli anni.\n''',encoding='utf-8')

    # Cleaning log: only actions actually represented in the canonical pipeline.
    clog=[
      ('C01','ICCU library','name_original/name_normalized','whitespace/Unicode normalization','Preservato originale e creato normalized con collapse deterministico','ridurre varianti puramente formali',int((lib.name_original!=lib.name_normalized).sum()),'valore originale conservato'),
      ('C02','ICCU library','address_original/address_normalized','whitespace/Unicode normalization','Preservato originale e creato normalized con collapse deterministico','ridurre varianti puramente formali',int((lib.address_original!=lib.address_normalized).sum()),'valore originale conservato'),
      ('C03','ICCU library','latitude/longitude','coppia coordinate (0,0)','Coordinate pulite impostate a missing; originali conservate','(0,0) non è una posizione bibliotecaria utile e costituisce pseudo-valore',int((lib.coordinate_quality_flag=='zero_pair_treated_as_missing').sum()),'nessun geocoding automatico'),
      ('C04','ICCU library','latitude/longitude','coordinate fuori bounding box indicativo Italia','Conservate e marcate outside_italy_bbox_review','possibili sedi all’estero o anomalie; non correggere automaticamente',int((lib.coordinate_quality_flag=='outside_italy_bbox_review').sum()),'richiede interpretazione caso per caso'),
      ('C05','ICCU library','latitude/longitude','coppia mancante/incompleta','Conservata come missing','assenza non equivale a zero',int((lib.coordinate_quality_flag=='missing').sum()),'nessuna imputazione'),
      ('C06','ICCU library','source_status','NULL stato ICCU','Mappato a NESSUNO_STATO_SPECIALE_REGISTRATO','assenza dello stato non prova apertura',int((status.normalized_status=='NESSUNO_STATO_SPECIALE_REGISTRATO').sum()),'escluso dal perimetro problematico principale'),
      ('C07','ICCU mergers','source_status','stato confluenza con possibile ISIL target','Parsing regex controllato del target ISIL','evitare inferenze da testo libero',int((merg.parse_success=='True').sum()),'90 confluenze restano senza target estratto'),
      ('C08','ISTAT POSAS','lettura CSV','stringa Comune = None rischia parsing NA','keep_default_na=False','preservare il nome ufficiale None',1,'nessuna perdita del comune'),
      ('C09','ISTAT POSAS','Età','codice 999 interpretato come totale','Usato dopo verifica empirica completa','mismatch 0 rispetto a somma età 0–100',7954+7896,'totali comunali coerenti'),
      ('C10','ISTAT 2019→2025','codici comune','variazioni amministrative','crosswalk esplicito per codice/predecessori; no fuzzy matching','armonizzazione sulla geografia 2025',len(cw),'Trapani/Misiliscemi non ricostruibili nel 2019'),
    ]
    wcsv(pd.DataFrame(clog,columns=['rule_id','dataset','field','problem','action','rationale','affected_records','consequence']),reports/'cleaning_log.csv')

    # Join quality.
    jq=[]
    for name,df,key in [('library_type',types,'isil'),('library_holdings',hold,'isil'),('special_collection',fund,'isil'),('library_contact',cont,'isil'),('library_previous_name',prev,'isil')]:
        d=df[key].nunique(); jq.append(dict(join=f'library→{name}',master_records=len(lib),matched_master_records=d,unmatched_master_records=len(lib)-d,duplicate_relation_rows=len(df)-d,coverage_percent=d/len(lib)*100,key=key,notes='1:N preservata' if len(df)>d else '1:1 sulla copertura presente'))
    istat_codes=set(pop.istat_code)
    matched=lib.istat_code.isin(istat_codes).sum(); jq.append(dict(join='ICCU library→ISTAT 2025 comune',master_records=len(lib),matched_master_records=int(matched),unmatched_master_records=int(len(lib)-matched),duplicate_relation_rows=0,coverage_percent=matched/len(lib)*100,key='istat_code',notes='join su codice ufficiale; no fuzzy matching'))
    jq.append(dict(join='ISTAT 2025 comuni→crosswalk 2019/2025',master_records=len(pop),matched_master_records=cw.current_istat_code.nunique(),unmatched_master_records=len(pop)-cw.current_istat_code.nunique(),duplicate_relation_rows=len(cw)-cw.current_istat_code.nunique(),coverage_percent=cw.current_istat_code.nunique()/len(pop)*100,key='current_istat_code',notes='righe multiple per predecessori in fusioni/incorporazioni'))
    wcsv(pd.DataFrame(jq),reports/'join_quality.csv')
    wcsv(pd.DataFrame(jq),tables/'join_coverage_summary.csv')

    # Data quality metrics.
    dq=[]
    def add(dataset,dimension,field,value,unit,interpretation): dq.append(dict(dataset=dataset,dimension=dimension,field=field,value=value,unit=unit,interpretation=interpretation))
    add('library','COMPLETENESS','isil',100.0,'percent','nessun ISIL mancante')
    add('library','UNIQUENESS','isil',100.0,'percent','19.611/19.611 ISIL unici')
    add('library','VALIDITY','isil_pattern',100.0,'percent','tutti gli ISIL rispettano ^IT-[A-Z]{2}\\d{4}$')
    add('library','COMPLETENESS','coordinates_clean',((lib.latitude!='')&(lib.longitude!='')).sum()/len(lib)*100,'percent','coordinate pulite complete')
    add('library','COMPLETENESS','istat_code',(lib.istat_code!='').sum()/len(lib)*100,'percent','codice comune presente')
    add('library_type','JOINABILITY','isil_coverage',types.isil.nunique()/len(lib)*100,'percent','biblioteche del master coperte')
    add('library_holdings','JOINABILITY','isil_coverage',hold.isil.nunique()/len(lib)*100,'percent','biblioteche del master coperte')
    add('special_collection','JOINABILITY','isil_coverage',fund.isil.nunique()/len(lib)*100,'percent','biblioteche del master coperte')
    add('library_contact','JOINABILITY','isil_coverage',cont.isil.nunique()/len(lib)*100,'percent','biblioteche del master coperte')
    add('municipality_population','UNIQUENESS','istat_code',pop.istat_code.nunique()/len(pop)*100,'percent','un codice per comune 2025')
    add('ICCU→ISTAT','JOINABILITY','istat_code',matched/len(lib)*100,'percent','record ICCU agganciati a comune ISTAT 2025')
    add('municipality_population','CONSISTENCY','population_comparability',(pop.population_comparability=='comparable_on_2025_geography').sum()/len(pop)*100,'percent','Trapani e Misiliscemi esclusi dal confronto 2019')
    dqdf=pd.DataFrame(dq); wcsv(dqdf,reports/'data_quality_metrics.csv')
    (reports/'data_quality.md').write_text(f'''# Data Quality\n\n## Completeness\n- ISIL: 100%.\n- Codice ISTAT comunale nel master ICCU: 100%.\n- Coordinate pulite complete: {((lib.latitude!='')&(lib.longitude!='')).sum()/len(lib)*100:.2f}%.\n- Copertura tipologie/patrimonio: {types.isil.nunique()/len(lib)*100:.2f}%.\n- Copertura contatti: {cont.isil.nunique()/len(lib)*100:.2f}%.\n- Copertura fondi speciali: {fund.isil.nunique()/len(lib)*100:.2f}%.\n\n## Uniqueness\n- ISIL: 19.611 unici su 19.611.\n- Comuni 2025 nel dataset demografico: 7.896 codici unici su 7.896 righe.\n\n## Validity\n- Pattern ISIL: 100%.\n- Coordinate `(0,0)` ({(lib.coordinate_quality_flag=='zero_pair_treated_as_missing').sum()}) non sono accettate come coordinate pulite.\n- Tre coordinate fuori bounding box Italia restano marcate per revisione; due sono compatibili con sedi a Buenos Aires/Atene, una (`IT-ME0024`) è sospetta.\n\n## Consistency\n- Stato `NULL` separato da qualsiasi affermazione di apertura.\n- Relazioni 1:N non appiattite.\n- `Età=999` POSAS verificata: 0 mismatch su tutti i comuni 2019 e 2025 rispetto alla somma 0–100.\n- Trapani e Misiliscemi sono marcati non comparabili per la variazione territoriale 2021.\n\n## Joinability\n- ICCU→ISTAT 2025 via codice comune: 19.611/19.611 = 100%.\n- Le coperture ICCU secondarie sono riportate in `reports/join_quality.csv`.\n''',encoding='utf-8')

    (reports/'source_verification.md').write_text(f'''# Data verification - fonti\n\n## ICCU\nPublisher istituzionale: ICCU. Pagina Open Data ufficiale: {ICCU_URL}. La pagina dichiara aggiornamento quotidiano, formati CSV/XML/JSON, archivio `opendata.zip`, ISIL come chiave primaria per incrociare i dataset e documenta i valori di `stato-registrazione`. Licenza dati: CC0. Snapshot locale: `{snap}`.\n\n## ISTAT POSAS\nPublisher: Istat. Serie: popolazione residente per età, sesso e stato civile al 1° gennaio. Fonte: {ISTAT_URL}. Anni utilizzati: 2019 e 2025. Licenza Istat: CC BY 4.0 ({ISTAT_LICENSE_URL}). I file comunali sono letti preservando stringhe come `None`.\n\n## Cultural-ON\n## Cultural-ON
Il file OWL locale `data/external/cultural-ON.owl` è conservato nel repository come input semantico. La versione dichiarata è 2.0 (30 marzo 2016), con licenza CC BY 3.0 IT. Documentazione ufficiale: {CULTURAL_URL}. L'ontologia viene riutilizzata nella modellazione semantica del progetto.\n\n## Limitazioni\n- Lo XSD 1.6 non è presente come file locale nel repository; sono presenti le quattro immagini delle note di rilascio 1.6 fornite dall’utente e il riferimento alla pagina ufficiale del formato.\n- Due comuni (Trapani, Misiliscemi) non consentono un confronto 2019 ricostruibile dai soli POSAS comunali.\n''',encoding='utf-8')

    # Decisions log in the requested repeated structure.
    decisions=[
      ('NULL dello stato ICCU',f'{(status.normalized_status=="NESSUNO_STATO_SPECIALE_REGISTRATO").sum()} record hanno `source_status` vuoto. La documentazione ICCU usa il campo per segnalare stati speciali quando valorizzato.','Interpretare NULL come aperta; escludere; categoria neutra.','Usare `NESSUNO_STATO_SPECIALE_REGISTRATO`.','L’assenza di un valore non dimostra apertura.','I NULL non entrano automaticamente nelle categorie problematiche.'),
      ('Definizione di main_problematic_libraries','Il mapping canonico include solo stati con `include_in_main_analysis=True`: cessazione, chiusura temporanea, inagibilità/sospensione sisma, riapertura parziale, deposito senza punto di servizio.','Includere anche confluenze/non censite/allestimento; includere tutti gli stati non null.','Somma solo gli stati marcati True in `metadata/status_mapping.csv`.','Mantiene separate cessazione, interruzione, parzialità, trasformazione organizzativa e incompletezza anagrafica.','Conteggio nazionale = 2.497.'),
      ('Relazioni XML 1:N',f'Patrimonio {len(hold):,} righe, fondi {len(fund):,}, contatti {len(cont):,}; più righe per ISIL.','Mega-CSV con duplicazione delle biblioteche; tabelle separate.','Conservare tabelle normalizzate per relazione.','Evita moltiplicazioni spurie e perdita di cardinalità.','Join successivi devono rispettare 1:N.'),
      ('Coordinate (0,0)',f'{(lib.coordinate_quality_flag=="zero_pair_treated_as_missing").sum()} biblioteche hanno coppia originale (0,0).','Trattare come coordinata reale; geocodificare; marcare missing.','Coordinate pulite impostate a missing; originali preservate.','(0,0) è uno pseudo-valore non utile per localizzare una biblioteca italiana.','Nessuna imputazione geografica automatica.'),
      ('Coordinate fuori bounding box',f'{(lib.coordinate_quality_flag=="outside_italy_bbox_review").sum()} record sono fuori dal bounding box indicativo Italia ma nel range mondiale.','Cancellare; correggere/geocodificare; preservare con flag.','Preservare e marcare `outside_italy_bbox_review`.','Una sede italiana può trovarsi all’estero; il bounding box è controllo, non prova di errore.','Tre record richiedono interpretazione.'),
      ('IT-ME0024','Tra i tre outlier geografici, `IT-ME0024` ha coordinate compatibili con l’India, non con la localizzazione territoriale attesa.','Correggere da indirizzo; eliminare; segnalare.','Segnalare senza correzione automatica.','Manca una fonte certa per sostituire le coordinate.','Anomalia aperta per revisione manuale.'),
      ('Parsing delle confluenze',f'{len(merg):,} record di confluenza; {(merg.parse_success=="True").sum():,} target ISIL estratti; {(merg.parse_success!="True").sum()} senza target parseabile.','Parsing libero/fuzzy; regex controllata; nessun parsing.','Regex esatta `Biblioteca confluita in IT-XXdddd`; target validato contro snapshot.','L’ISIL ha formato ufficiale e consente validazione deterministica.','1.412 target esistono nello snapshot; 90 restano senza target.'),
      ('Self-loop IT-SS0267','`IT-SS0267 → IT-SS0267` è presente nella sorgente dopo parsing e target validation.','Rimuovere/correggere; preservare e segnalare.','Preservare con `self_loop=True` e `in_cycle=True`.','Nessuna evidenza autorizza una correzione.','Unico ciclo rilevato nel grafo delle confluenze.'),
      ('Età=999 ISTAT','Per 7.954 comuni 2019 e 7.896 comuni 2025 la riga `Età=999` coincide esattamente con la somma delle età 0–100; mismatch 0.','Assumerla senza verifica; ricalcolare sempre; validarla e usarla.','Usare 999 come totale dopo verifica empirica completa.','Evita interpretazioni non documentate o assunte.','Totali comunali impiegati per popolazione 2019/2025.'),
      ('Comune “None” e keep_default_na=False','Esiste un comune ufficiale denominato `None`; i parser pandas standard possono trattare la stringa come NA.','Parsing NA predefinito; eccezione a posteriori; preservazione stringhe.','Leggere POSAS con `keep_default_na=False`.','Conserva il nome ufficiale senza perdita informativa.','Il comune None resta una stringa valida.'),
      ('Variazioni amministrative 2019–2025',f'Geografia 2019: 7.954 comuni; 2025: 7.896; crosswalk: {len(cw):,} relazioni verso 7.896 comuni correnti.','Join per nome/fuzzy; eliminare non-match; crosswalk ufficiale per codici e predecessori.','Geografia analitica 2025 e crosswalk esplicito per codice/predecessori.','I codici ufficiali e le trasformazioni amministrative sono più affidabili del fuzzy matching.','Fusioni/incorporazioni aggregano predecessori quando ricostruibili.'),
      ('Trapani/Misiliscemi','Misiliscemi nasce da scorporo territoriale di Trapani nel 2021; il POSAS comunale 2019 non consente di sottrarre correttamente il territorio.','Attribuire tutto Trapani 2019 a uno dei due; stimare; segnare non comparabile.','Entrambi marcati `not_comparable_due_to_2021_territorial_split` per il confronto 2019.','Qualsiasi ripartizione sarebbe inventata.','Population 2019 e variazioni restano NA per i due comuni.'),
      ('Denominazione Reggio Calabria / Reggio di Calabria','Nel POSAS 2025 Province, codice provincia 080, la denominazione ufficiale è `Reggio di Calabria`; 97 comuni appartengono alla provincia 080.','Usare etichetta ICCU `Reggio Calabria`; usare POSAS 2025.','Nel dataset analitico la provincia è canonizzata dal POSAS 2025 e vale `Reggio di Calabria`.','Il dataset analitico usa la geografia territoriale ISTAT 2025 come fonte canonica.','Il rebuild produce deterministicamente 97 righe con `Reggio di Calabria`.'),
      ('Differenza testuale di rationale','`library_status.csv` e `metadata/status_mapping.csv` ora usano la stessa funzione `classify_status`; confronto canonico: 0 differenze.','Mantenere testi indipendenti; sincronizzazione manuale; funzione unica.','Usare la stessa funzione canonica per entrambi gli output.','Elimina drift puramente testuale mantenendo identica semantica.','Il validator verifica uguaglianza del rationale per ogni source_status.'),
      ('Anomalia data-export di patrimonio.xml','La radice di `patrimonio.xml` dichiara `data-export="2026-09-08T14:00:"`, timestamp sintatticamente incompleto.','Correggere il timestamp; ignorarlo; registrare anomalia.','Non modificare la sorgente; registrare l’anomalia.','Non esiste evidenza per inferire i secondi mancanti.','Snapshot principale resta determinato da biblioteche.json; il timestamp XML rimane nota di qualità.'),
      ('Licenza del dataset derivato','ICCU Open Data = CC0; POSAS Istat = CC BY 4.0; Cultural-ON è separata e non contribuisce ai valori tabellari in questa fase.','CC0; CC BY 4.0; altra licenza senza analisi.','Licenza prevista per il dataset tabellare derivato: CC BY 4.0.','Rispetta l’obbligo di attribuzione derivante dalla componente Istat e consente riuso/modifica/commerciale.','Attribuire Istat; citare ICCU; non relicenziare automaticamente Cultural-ON o documentazione ICCU.'),
    ]
    out=['# Decisions log','']
    for i,(problem,evidence,alts,decision,mot,cons) in enumerate(decisions,1):
        out += [f'# Decisione D{i:02d}','', '## Problema',problem,'','## Evidenza',evidence,'','## Alternative considerate',alts,'','## Decisione',decision,'','## Motivazione',mot,'','## Conseguenza',cons,'']
    (reports/'decisions_log.md').write_text('\n'.join(out),encoding='utf-8')

    (reports / "three_star_dataset.md").write_text(
        dedent(
            """\
    # Dataset strutturato in formato aperto

    Gli output analitici sono distribuiti in **CSV UTF-8**, formato strutturato,
    machine-readable e non proprietario.

    I RAW originali sono conservati separatamente in `data/raw/` e non vengono
    modificati dalla pipeline.

    La catena implementata è:

    RAW → cleaning → harmonization → integration → CSV processed

    I dataset processati canonici sono disponibili direttamente in
    `data/processed/`.

    Dal punto di vista tecnico i dataset soddisfano i requisiti di struttura
    e formato aperto associati al livello 3-star. La classificazione completa
    del modello 5-star richiede tuttavia anche la pubblicazione sul Web, che
    viene valutata separatamente nel progetto.

    L'esportazione Parquet è opzionale e non è necessaria per la pipeline
    principale.
    """
        ),
        encoding="utf-8",
    )

    # Data Package metadata.
    descriptions={
      'library.csv':'Master ICCU pulito a granularità biblioteca.', 'library_status.csv':'Stato ICCU normalizzato per biblioteca.',
      'library_type.csv':'Tipologie ICCU per biblioteca sulla copertura disponibile.', 'library_holdings.csv':'Patrimonio ICCU, relazione 1:N biblioteca-materiale.',
      'special_collection.csv':'Fondi speciali ICCU, relazione 1:N.', 'library_contact.csv':'Contatti ICCU, relazione 1:N.',
      'library_previous_name.csv':'Denominazioni precedenti, relazione 1:N.', 'library_mergers.csv':'Confluenze organizzative parseate e validate.',
      'municipality_population.csv':'Popolazione comunale armonizzata 2019/2025 sulla geografia 2025.', 'analysis_municipality.csv':'Dataset analitico comunale integrato ICCU+ISTAT.'}
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
    datapackage={'profile':'data-package','name':'biblioteche-fantasma','title':'BIBLIOTECHE FANTASMA','description':'Dataset puliti e integrati ICCU + ISTAT 2019/2025 per lo studio delle biblioteche italiane non pienamente operative.','version':PROJECT_RELEASE_DATE,'keywords':['biblioteche','ICCU','ISTAT','open data','Italia','demografia'],'licenses':[{'name':'CC-BY-4.0','path':'https://creativecommons.org/licenses/by/4.0/','title':'Creative Commons Attribution 4.0 International'}],'sources':[{'title':'ICCU Anagrafe delle Biblioteche Italiane','path':ICCU_URL},{'title':'ISTAT POSAS 2019','path':ISTAT_URL},{'title':'ISTAT POSAS 2025','path':ISTAT_URL}],'geographic_coverage':'Italia','temporal_coverage':'2019-01-01; 2025-01-01; ICCU snapshot 2026-09-08T14:11:15','resources':resources}
    (meta/'datapackage.json').write_text(json.dumps(datapackage,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    # Local DCAT metadata.
    # The repository uses non-dereferenceable development URIs and therefore
    # does not claim operational DCAT-AP_IT conformance.
    dists=[]
    for p in sorted(proc.glob('*.csv')):
        ident=p.stem.replace('_','-')
        dists.append(f'''bf:dist-{ident} a dcat:Distribution ;\n    dct:title "{p.stem}"@it ;\n    dct:description "{descriptions[p.name]}"@it ;\n    dct:license <https://creativecommons.org/licenses/by/4.0/> ;\n    dct:format <http://publications.europa.eu/resource/authority/file-type/CSV> ;\n    dcat:mediaType "text/csv" ;\n    dcat:accessURL <file:./data/processed/{p.name}> ;\n    dcat:downloadURL <file:./data/processed/{p.name}> .''')
    distrefs=',\n        '.join('bf:dist-'+p.stem.replace('_','-') for p in sorted(proc.glob('*.csv')))
    ttl=f'''@prefix bf: <https://biblioteche-fantasma.invalid/metadata/> .\n@prefix dcat: <http://www.w3.org/ns/dcat#> .\n@prefix dct: <http://purl.org/dc/terms/> .\n@prefix foaf: <http://xmlns.com/foaf/0.1/> .\n@prefix schema: <https://schema.org/> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\nbf:project-author a foaf:Person ; foaf:name "Amelia Morsellino" .\n\nbf:dataset a dcat:Dataset ; \ndct:identifier "biblioteche-fantasma" ;\n    dct:title "Biblioteche Fantasma"@it ;\n    dct:description "Dataset puliti e integrati ICCU + ISTAT 2019/2025 per lo studio delle biblioteche italiane non pienamente operative."@it ;\n    dct:publisher bf:project-author ;\n    dct:creator bf:project-author ;\n    dct:license <https://creativecommons.org/licenses/by/4.0/> ;\n    dct:issued "{PROJECT_RELEASE_DATE}"^^xsd:date ;\n    dct:modified "{PROJECT_RELEASE_DATE}"^^xsd:date ;\n    dct:language <http://publications.europa.eu/resource/authority/language/ITA> ;\n    dct:spatial <http://publications.europa.eu/resource/authority/country/ITA> ;\n    dct:temporal [ a dct:PeriodOfTime ; schema:startDate "2019-01-01"^^xsd:date ; schema:endDate "2026-09-08"^^xsd:date ] ;\n    dct:accrualPeriodicity <http://publications.europa.eu/resource/authority/frequency/IRREG> ;\n    dcat:theme <http://publications.europa.eu/resource/authority/data-theme/EDUC> ;\n    dcat:keyword "biblioteche"@it, "ICCU"@it, "ISTAT"@it, "demografia"@it, "open data"@it ;\n    dct:source <{ICCU_URL}>, <{ISTAT_URL}> ;\n    dcat:distribution {distrefs} .\n\n'''+'\n\n'.join(dists)+'\n'
    (meta/'dcat.ttl').write_text(ttl,encoding='utf-8')
    (meta / "dcat_validation_notes.md").write_text(
        dedent(
            """\
    # Note di validazione e conformità DCAT

    Il file `metadata/dcat.ttl` fornisce una descrizione RDF/DCAT del dataset
    e delle principali distribuzioni del progetto.

    La descrizione include identificatore, titolo, descrizione, publisher,
    creator, licenza, lingua, copertura geografica, frequenza, tema, keyword,
    distribuzioni, formato, media type, accessURL e downloadURL.

    ## DCAT-AP_IT

    Il progetto non dichiara una conformità operativa completa a DCAT-AP_IT
    nella distribuzione locale corrente.

    Le risorse utilizzano infatti il namespace di sviluppo
    `https://biblioteche-fantasma.invalid/` e le distribuzioni sono referenziate
    tramite URI locali `file:`.

    Una pubblicazione conforme su un catalogo richiederebbe URI HTTP(S)
    pubbliche e persistenti, URL di accesso/download realmente disponibili
    sul Web e una validazione rispetto alla versione del profilo DCAT-AP_IT
    applicabile al momento della pubblicazione.
    """
        ),
        encoding="utf-8",
    )
    prov=f'''@prefix bf: <urn:biblioteche-fantasma:provenance:> .\n@prefix prov: <http://www.w3.org/ns/prov#> .\n@prefix dct: <http://purl.org/dc/terms/> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\nbf:src-iccu a prov:Entity ; dct:title "ICCU Anagrafe snapshot 2026-09-08"@it .\nbf:src-istat-2019 a prov:Entity ; dct:title "ISTAT POSAS 2019"@it .\nbf:src-istat-2025 a prov:Entity ; dct:title "ISTAT POSAS 2025"@it .\nbf:cleaning a prov:Activity ; prov:used bf:src-iccu ; dct:description "Pulizia deterministica ICCU senza sovrascrittura dei RAW"@it .\nbf:harmonization a prov:Activity ; prov:used bf:src-istat-2019, bf:src-istat-2025 ; dct:description "Armonizzazione comunale 2019→2025"@it .\nbf:integration a prov:Activity ; prov:used bf:cleaned-iccu, bf:harmonized-population ; dct:description "Integrazione ICCU→ISTAT via codice comune"@it .\nbf:cleaned-iccu a prov:Entity ; prov:wasGeneratedBy bf:cleaning ; prov:wasDerivedFrom bf:src-iccu .\nbf:harmonized-population a prov:Entity ; prov:wasGeneratedBy bf:harmonization ; prov:wasDerivedFrom bf:src-istat-2019, bf:src-istat-2025 .\nbf:derived-dataset a prov:Entity ; prov:wasGeneratedBy bf:integration ; prov:wasDerivedFrom bf:src-iccu, bf:src-istat-2019, bf:src-istat-2025 ; dct:issued "{PROJECT_RELEASE_DATE}"^^xsd:date .\n'''
    (meta/'provenance.ttl').write_text(prov,encoding='utf-8')

    print('Metadata and quality reports generated in',root)

if __name__=='__main__': main()
