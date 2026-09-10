#!/usr/bin/env python3
"""Final quantitative analysis for Biblioteche Fantasma.

The analysis uses the processed datasets and the interlinking report generated
by the reproducible project pipeline.
"""

from __future__ import annotations
import argparse, json, math
from pathlib import Path
import pandas as pd
import numpy as np
import networkx as nx
from scipy import stats

MAIN_STATUSES = {
    'BIBLIOTECA_NON_PIU_ESISTENTE',
    'TEMPORANEAMENTE_CHIUSA',
    'INAGIBILE',
    'SERVIZI_SOSPESI_CAUSA_SISMA',
    'RIAPERTURA_AGIBILITA_PARZIALE',
    'DEPOSITO_SENZA_PUNTO_DI_SERVIZIO',
}

def num(s): return pd.to_numeric(s, errors='coerce')

def boolish(s):
    return s.astype(str).str.strip().str.lower().isin({'true','1','yes','y'})

def save(df, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def cramers_v(table: pd.DataFrame):
    arr = table.to_numpy()
    chi2, p, dof, expected = stats.chi2_contingency(arr)
    n = arr.sum(); r, k = arr.shape
    phi2 = chi2/n
    phi2corr = max(0, phi2 - ((k-1)*(r-1))/(n-1)) if n > 1 else 0
    rcorr = r - ((r-1)**2)/(n-1) if n > 1 else r
    kcorr = k - ((k-1)**2)/(n-1) if n > 1 else k
    denom = min(kcorr-1, rcorr-1)
    v = math.sqrt(phi2corr/denom) if denom > 0 else np.nan
    return chi2, p, dof, v, expected


def main(root: Path):
    d = root/'data'/'processed'
    out = root/'reports'/'analysis_tables'
    out.mkdir(parents=True, exist_ok=True)

    lib = pd.read_csv(d/'library.csv', low_memory=False)
    st = pd.read_csv(d/'library_status.csv', low_memory=False)
    typ = pd.read_csv(d/'library_type.csv', low_memory=False)
    hold = pd.read_csv(d/'library_holdings.csv', low_memory=False)
    sc = pd.read_csv(d/'special_collection.csv', low_memory=False)
    mer = pd.read_csv(d/'library_mergers.csv', low_memory=False)
    mun = pd.read_csv(d/'analysis_municipality.csv', low_memory=False)
    ilink = pd.read_csv(root/'reports'/'interlinking_report.csv')

    st.loc[:, 'include_main'] = boolish(st['include_in_main_analysis'])
    libst = lib.merge(st[['isil','normalized_status','analytical_group','include_main']], on='isil', how='left')
    n_registry = len(lib)
    n_libraries = int(num(mun['total_libraries']).sum())
    n_problematic = int(st['include_main'].sum())

    # RQ1/RQ2 status and territory
    status = (st.groupby(['normalized_status','analytical_group','include_main'], dropna=False)
              .size().rename('count').reset_index())
    status.loc[:, 'share_registry_percent'] = (
    status['count'] / n_registry * 100
)
    status = status.sort_values('count', ascending=False)
    save(status, out/'status_distribution.csv')

    region = mun.assign(total_libraries=num(mun.total_libraries), problematic=num(mun.main_problematic_libraries)) \
                .groupby('region', dropna=False)[['total_libraries','problematic']].sum().reset_index()
    region.loc[:, 'problematic_share'] = np.where(
        region['total_libraries'] > 0,
        region['problematic'] / region['total_libraries'],
        np.nan
    )
    region.loc[:, 'problematic_share_percent'] = (
        region['problematic_share'] * 100
    )
    region.loc[:, 'problematic_per_100k_population'] = mun.assign(pop=num(mun.population_2025),prob=num(mun.main_problematic_libraries)).groupby('region').apply(
        lambda g: g['prob'].sum()/g['pop'].sum()*100000 if g['pop'].sum()>0 else np.nan, include_groups=False).values
    region = region.sort_values('problematic_share', ascending=False)
    save(region, out/'region_problematic_summary.csv')

    prov = mun.assign(total_libraries=num(mun.total_libraries), problematic=num(mun.main_problematic_libraries)) \
              .groupby(['region','province','province_istat_code'], dropna=False)[['total_libraries','problematic']].sum().reset_index()
    prov.loc[:, 'problematic_share'] = np.where(prov.total_libraries>0, prov.problematic/prov.total_libraries, np.nan)
    save(prov.sort_values(['problematic_share','problematic'], ascending=[False,False]), out/'province_problematic_summary.csv')

    top_mun = mun[['istat_code','municipality_name','province','region','population_2025','total_libraries','main_problematic_libraries','problematic_share','problematic_libraries_per_100k']].copy()
    top_mun.loc[:, 'population_2025'] = num(top_mun['population_2025'])
    top_mun.loc[:, 'total_libraries'] = num(top_mun['total_libraries'])
    top_mun.loc[:, 'main_problematic_libraries'] = num(
        top_mun['main_problematic_libraries']
    )
    top_mun.loc[:, 'problematic_share'] = num(
        top_mun['problematic_share']
    )
    top_mun.loc[:, 'problematic_libraries_per_100k'] = num(
        top_mun['problematic_libraries_per_100k']
    )
    save(top_mun.sort_values(['main_problematic_libraries','problematic_share'],ascending=[False,False]).head(100), out/'municipalities_top_problematic_absolute.csv')

    # RQ3 types x status: descriptive + association
    ts = typ.merge(st[['isil','normalized_status','include_main']], on='isil', how='inner')
    ftab = pd.crosstab(ts['functional_type'].fillna('MISSING'), ts['normalized_status'])
    save(ftab.reset_index(), out/'functional_type_by_status_counts.csv')
    fshare = ftab.div(ftab.sum(axis=1), axis=0)
    save((fshare*100).reset_index(), out/'functional_type_by_status_row_percent.csv')
    atab = pd.crosstab(ts['administrative_type'].fillna('MISSING'), ts['normalized_status'])
    save(atab.reset_index(), out/'administrative_type_by_status_counts.csv')
    # association main problematic vs not main is more interpretable, and less sparse.
    f2 = pd.crosstab(ts['functional_type'].fillna('MISSING'), ts['include_main'])
    a2 = pd.crosstab(ts['administrative_type'].fillna('MISSING'), ts['include_main'])
    fchi, fp, fdof, fv, fexp = cramers_v(f2)
    achi, ap, adof, av, aexp = cramers_v(a2)
    assoc = pd.DataFrame([
        {'dimension':'functional_type','N':int(f2.to_numpy().sum()),'rows':f2.shape[0],'columns':f2.shape[1],'chi_square':fchi,'dof':fdof,'p_value':fp,'cramers_v_bias_corrected':fv,'min_expected':float(fexp.min()),'cells_expected_lt5':int((fexp<5).sum())},
        {'dimension':'administrative_type','N':int(a2.to_numpy().sum()),'rows':a2.shape[0],'columns':a2.shape[1],'chi_square':achi,'dof':adof,'p_value':ap,'cramers_v_bias_corrected':av,'min_expected':float(aexp.min()),'cells_expected_lt5':int((aexp<5).sum())},
    ])
    save(assoc, out/'type_status_association_tests.csv')
    type_main = (ts.groupby('functional_type').agg(total=('isil','size'),problematic=('include_main','sum')).reset_index())
    type_main.loc[:, 'problematic_share'] = (
        type_main['problematic'] / type_main['total']
    )
    save(type_main.sort_values(['problematic_share','total'],ascending=[False,False]), out/'functional_type_problematic_summary.csv')

    # RQ4 demography. Municipality unit, at least one library, comparable only.
    dm = mun.copy()
    for c in ['population_change_percent','problematic_share','total_libraries','main_problematic_libraries','population_2025','share_65_plus_2025']:
        dm.loc[:,c]=num(dm[c])
    eligible = dm[(dm.population_comparability=='comparable_on_2025_geography') & (dm.total_libraries>0) & dm.population_change_percent.notna() & dm.problematic_share.notna()].copy()
    x=eligible.population_change_percent; y=eligible.problematic_share
    pear=stats.pearsonr(x,y); spear=stats.spearmanr(x,y)
    q1,q3=x.quantile([.25,.75]); iqr=q3-q1; lo=q1-1.5*iqr; hi=q3+1.5*iqr
    eligible.loc[:, 'pop_change_outlier_iqr'] = (x < lo) | (x > hi)
    sens=eligible[~eligible.pop_change_outlier_iqr]
    pear_s=stats.pearsonr(sens.population_change_percent,sens.problematic_share); spear_s=stats.spearmanr(sens.population_change_percent,sens.problematic_share)
    corr = pd.DataFrame([
        {'analysis':'primary_all_eligible','N':len(eligible),'pearson_r':pear.statistic,'pearson_p':pear.pvalue,'spearman_rho':spear.statistic,'spearman_p':spear.pvalue,'pop_change_iqr_low':lo,'pop_change_iqr_high':hi,'outlier_count':int(eligible.pop_change_outlier_iqr.sum())},
        {'analysis':'sensitivity_excluding_population_change_IQR_outliers','N':len(sens),'pearson_r':pear_s.statistic,'pearson_p':pear_s.pvalue,'spearman_rho':spear_s.statistic,'spearman_p':spear_s.pvalue,'pop_change_iqr_low':lo,'pop_change_iqr_high':hi,'outlier_count':0},
    ])
    save(corr, out/'demography_correlations.csv')
    save(eligible.sort_values('population_change_percent'), out/'demography_analysis_dataset.csv')
    groups=[]
    for name,g in eligible.assign(population_group=np.where(eligible.population_change_percent<0,'decline','stable_or_growth')).groupby('population_group'):
        groups.append({'population_group':name,'N':len(g),'mean_problematic_share':g.problematic_share.mean(),'median_problematic_share':g.problematic_share.median(),'municipalities_with_any_problematic':int((g.main_problematic_libraries>0).sum()),'share_municipalities_with_any_problematic':(g.main_problematic_libraries>0).mean(),'mean_population_change_percent':g.population_change_percent.mean()})
    gdf=pd.DataFrame(groups)
    dec=eligible[eligible.population_change_percent<0].problematic_share
    gro=eligible[eligible.population_change_percent>=0].problematic_share
    mw=stats.mannwhitneyu(dec,gro,alternative='two-sided')
    gdf['mannwhitney_u']=np.nan; gdf['mannwhitney_p']=np.nan
    if len(gdf): gdf.loc[gdf.index[0],['mannwhitney_u','mannwhitney_p']]=[mw.statistic,mw.pvalue]
    save(gdf, out/'demography_decline_vs_growth.csv')

    # RQ8 age structure secondary
    age = eligible[eligible.share_65_plus_2025.notna()].copy()
    agep=stats.pearsonr(age.share_65_plus_2025, age.problematic_share); ages=stats.spearmanr(age.share_65_plus_2025, age.problematic_share)
    save(pd.DataFrame([{'N':len(age),'pearson_r':agep.statistic,'pearson_p':agep.pvalue,'spearman_rho':ages.statistic,'spearman_p':ages.pvalue}]), out/'age65_problematic_correlation.csv')

    # RQ5 holdings. Distinguish missing quantity, explicit zero, positive.
    prob_isil=set(st.loc[st.include_main,'isil'])
    ph=hold[hold.isil.isin(prob_isil)].copy(); ph.loc[:, 'quantity_num'] = num(ph['quantity'])
    ph.loc[:, 'quantity_state'] = np.select(
        [
            ph['quantity_num'].isna(),
            ph['quantity_num'].eq(0),
            ph['quantity_num'].gt(0)
        ],
        [
            'missing',
            'explicit_zero',
            'positive'
        ],
        default='other_numeric'
    )
    h_summary=pd.DataFrame([{
        'problematic_libraries_total':n_problematic,
        'problematic_libraries_with_holding_rows':ph.isil.nunique(),
        'holding_rows_problematic':len(ph),
        'holding_rows_quantity_missing':int(ph.quantity_num.isna().sum()),
        'holding_rows_quantity_zero':int(ph.quantity_num.eq(0).sum()),
        'holding_rows_quantity_positive':int(ph.quantity_num.gt(0).sum()),
        'known_positive_quantity_sum':float(ph.loc[ph.quantity_num.gt(0),'quantity_num'].sum()),
    }])
    save(h_summary,out/'problematic_holdings_summary.csv')
    hcat=(ph.groupby(['category','quantity_state'],dropna=False).size().rename('rows').reset_index())
    save(hcat,out/'problematic_holdings_by_category_quantity_state.csv')
    hmat=(ph.groupby(['category','material'],dropna=False).agg(rows=('isil','size'),libraries=('isil','nunique'),known_quantity_sum=('quantity_num',lambda s:s[s>0].sum()),known_quantity_n=('quantity_num',lambda s:s.gt(0).sum()),missing_quantity_n=('quantity_num',lambda s:s.isna().sum())).reset_index())
    save(hmat.sort_values(['libraries','rows'],ascending=False),out/'problematic_holdings_by_material.csv')

    psc=sc[sc.isil.isin(prob_isil)].copy()
    sc_fields=['consistenza','descrizione','datazione','tipologia_fondo','catalogazione_inventario','tipologia_documentaria','provenienza','soggetto_produttore']
    sc_summary={'problematic_libraries_total':n_problematic,'problematic_libraries_with_special_collections':psc.isil.nunique(),'special_collection_records_problematic':len(psc)}
    for c in sc_fields: sc_summary[f'{c}_documented_records']=int(psc[c].notna().sum())
    save(pd.DataFrame([sc_summary]),out/'problematic_special_collections_summary.csv')
    sct=(psc.groupby('tipologia_fondo',dropna=False).agg(records=('isil','size'),libraries=('isil','nunique')).reset_index().sort_values('records',ascending=False))
    save(sct,out/'problematic_special_collections_by_type.csv')
    # A qualitative sample is deterministic: first 30 records with richest documentation.
    score=psc[sc_fields].notna().sum(axis=1); sample=psc.assign(documented_field_count=score).sort_values(['documented_field_count','isil'],ascending=[False,True]).head(30)
    save(sample,out/'problematic_special_collections_documented_sample.csv')

    # RQ6: use existing interlinking results only; do NOT rerun matching.
    save(ilink, out/'interlinking_coverage.csv')

    # RQ7 merger network from the processed merger table.
    valid=mer[boolish(mer.parse_success)&boolish(mer.target_exists_in_snapshot)&mer.target_isil.notna()].copy()
    G=nx.DiGraph(); G.add_edges_from(valid[['source_isil','target_isil']].itertuples(index=False,name=None))
    comps=sorted(nx.weakly_connected_components(G), key=len, reverse=True)
    scc=sorted(nx.strongly_connected_components(G), key=len, reverse=True)
    cycles=list(nx.simple_cycles(G))
    net_summary=pd.DataFrame([{
        'merger_records_total':len(mer),'valid_edges':len(valid),'nodes':G.number_of_nodes(),'weak_components':len(comps),'largest_component_nodes':len(comps[0]) if comps else 0,'strong_components':len(scc),'cycles':len(cycles),'self_loops':nx.number_of_selfloops(G),'unparsed_or_unvalidated_records':len(mer)-len(valid)
    }])
    save(net_summary,out/'merger_network_summary.csv')
    hubs=pd.DataFrame(sorted(G.in_degree,key=lambda z:z[1],reverse=True),columns=['target_isil','in_degree'])
    hubs=hubs[hubs.in_degree>0].merge(lib[['isil','name_original','municipality_name','province_name','region']],left_on='target_isil',right_on='isil',how='left').drop(columns='isil')
    save(hubs.head(100),out/'merger_targets_top.csv')
    comp_rows=[]
    for i,c in enumerate(comps,1):
        comp_rows.append({'component_id':i,'nodes':len(c),'edges':G.subgraph(c).number_of_edges(),'max_in_degree':max((G.in_degree(n) for n in c),default=0)})
    save(pd.DataFrame(comp_rows),out/'merger_components.csv')
    valid_geo=valid.merge(lib[['isil','region']],left_on='source_isil',right_on='isil',how='left')
    save(valid_geo.groupby('region',dropna=False).size().rename('merger_edges_from_region').reset_index().sort_values('merger_edges_from_region',ascending=False),out/'merger_edges_by_region.csv')

    # Overall descriptive table
    summary = {
        'registry_records':n_registry,
        'libraries_excluding_other_iccu_institutions':n_libraries,
        'main_problematic_libraries':n_problematic,
        'problematic_share_of_libraries_percent':n_problematic/n_libraries*100,
        'problematic_share_of_registry_records_percent':n_problematic/n_registry*100,
        'municipalities_2025':len(mun),
        'municipalities_with_libraries':int((num(mun.total_libraries)>0).sum()),
        'population_2025_total':int(num(mun.population_2025).sum()),
        'problematic_libraries_per_100k_national':n_problematic/num(mun.population_2025).sum()*100000,
        'coordinates_complete_clean':int(lib.latitude.notna().sum() & lib.longitude.notna().sum()) if False else int((lib.latitude.notna() & lib.longitude.notna()).sum()),
        'functional_type_coverage_libraries':typ.isil.nunique(),
        'holding_rows':len(hold),
        'special_collection_records':len(sc),
    }
    (root/'reports'/'analysis_summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')

    # Machine-readable RQ results for report generation.
    rq={
      'RQ1': {'problematic_libraries':n_problematic,'problematic_share_libraries_percent':summary['problematic_share_of_libraries_percent'],'top_regions_by_share':region.head(5).to_dict('records')},
      'RQ2': {'status_distribution':status.to_dict('records'),'top_regions_by_problematic_absolute':region.sort_values('problematic',ascending=False).head(5).to_dict('records')},
      'RQ3': {'functional_association':assoc.iloc[0].to_dict(),'administrative_association':assoc.iloc[1].to_dict(),'functional_type_problematic':type_main.sort_values('problematic',ascending=False).head(10).to_dict('records')},
      'RQ4': {'primary':corr.iloc[0].to_dict(),'sensitivity':corr.iloc[1].to_dict(),'decline_vs_growth':gdf.to_dict('records')},
      'RQ5': {'holdings':h_summary.iloc[0].to_dict(),'special_collections':sc_summary},
      'RQ6': {'interlinking_report':ilink.to_dict('records')},
      'RQ7': {'network':net_summary.iloc[0].to_dict(),'top_targets':hubs.head(10).to_dict('records')},
      'RQ8': {'age65': {'N':len(age),'pearson_r':agep.statistic,'pearson_p':agep.pvalue,'spearman_rho':ages.statistic,'spearman_p':ages.pvalue}},
    }
    (root/'reports'/'rq_results.json').write_text(json.dumps(rq,indent=2,ensure_ascii=False,default=lambda o: float(o) if hasattr(o,'item') else str(o)),encoding='utf-8')
    print(json.dumps(summary,indent=2,ensure_ascii=False))

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]); args=ap.parse_args(); main(args.root.resolve())
