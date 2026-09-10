#!/usr/bin/env python3
"""Generate final static visualizations and the interactive map from processed project data."""
from pathlib import Path
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import networkx as nx
import folium
from folium.plugins import MarkerCluster

STATUS_COLORS={
 'BIBLIOTECA_NON_PIU_ESISTENTE':'#9B2226',
 'TEMPORANEAMENTE_CHIUSA':'#EE9B00',
 'INAGIBILE':'#BB3E03',
 'SERVIZI_SOSPESI_CAUSA_SISMA':'#CA6702',
 'RIAPERTURA_AGIBILITA_PARZIALE':'#0A9396',
 'DEPOSITO_SENZA_PUNTO_DI_SERVIZIO':'#6C757D',
}
LABELS={
 'BIBLIOTECA_NON_PIU_ESISTENTE':'Non più esistente',
 'TEMPORANEAMENTE_CHIUSA':'Temporaneamente chiusa',
 'INAGIBILE':'Inagibile',
 'SERVIZI_SOSPESI_CAUSA_SISMA':'Servizi sospesi per sisma',
 'RIAPERTURA_AGIBILITA_PARZIALE':'Riapertura/agibilità parziale',
 'DEPOSITO_SENZA_PUNTO_DI_SERVIZIO':'Deposito senza punto di servizio',
}
SOURCE='Fonte: elaborazione su snapshot ICCU 08/09/2026 e ISTAT POSAS 2019–2025.'

def savefig(fig,path):
    fig.savefig(path,dpi=220,bbox_inches='tight',facecolor='white')
    plt.close(fig)

def main(root:Path):
    d=root/'data'/'processed'; v=root/'visualizations'; v.mkdir(exist_ok=True)
    lib=pd.read_csv(d/'library.csv',low_memory=False)
    st=pd.read_csv(d/'library_status.csv',low_memory=False)
    mun=pd.read_csv(d/'analysis_municipality.csv',low_memory=False)
    hold=pd.read_csv(d/'library_holdings.csv',low_memory=False)
    mer=pd.read_csv(d/'library_mergers.csv',low_memory=False)
    reg=pd.read_csv(root/'reports'/'analysis_tables'/'region_problematic_summary.csv')
    status=pd.read_csv(root/'reports'/'analysis_tables'/'status_distribution.csv')
    corr=pd.read_csv(root/'reports'/'analysis_tables'/'demography_correlations.csv')
    hsum=pd.read_csv(root/'reports'/'analysis_tables'/'problematic_holdings_summary.csv').iloc[0]
    scsum=pd.read_csv(root/'reports'/'analysis_tables'/'problematic_special_collections_summary.csv').iloc[0]

    # 1 map static: main-problematic only. Coordinates are already quality-cleaned in the processed dataset.
    m=lib.merge(st[['isil','normalized_status','include_in_main_analysis']],on='isil',how='left')
    main=m[m.include_in_main_analysis.astype(str).str.lower().eq('true')].copy()
    main['latitude']=pd.to_numeric(main.latitude,errors='coerce'); main['longitude']=pd.to_numeric(main.longitude,errors='coerce')
    mp=main.dropna(subset=['latitude','longitude'])
    fig,ax=plt.subplots(figsize=(8,10))
    for s,g in mp.groupby('normalized_status'):
        ax.scatter(g.longitude,g.latitude,s=7,alpha=.55,label=f"{LABELS.get(s,s)} (n={len(g):,})",c=STATUS_COLORS.get(s,'#444444'),linewidths=0)
    ax.set_xlim(6.0,19.0); ax.set_ylim(35.0,47.5); ax.set_aspect('equal',adjustable='box')
    ax.set_xlabel('Longitudine'); ax.set_ylabel('Latitudine')
    ax.grid(alpha=.18,linewidth=.6)
    ax.set_title('Le biblioteche problematiche sono diffuse in tutto il territorio, con concentrazioni nei maggiori sistemi urbani',loc='left',fontsize=13,pad=14)
    ax.text(0,1.01,f"{len(mp):,} biblioteche su {len(main):,} con coordinate pulite disponibili; stati distinti senza geocoding aggiuntivo.",transform=ax.transAxes,fontsize=9)
    ax.legend(loc='lower left',fontsize=7,frameon=True,markerscale=2)
    fig.text(.01,.01,SOURCE+' Nota: una mappa di punti non misura il rischio territoriale; riflette anche la densità di biblioteche registrate.',fontsize=7)
    savefig(fig,v/'map_static.png')

    # interactive map with clustering
    fmap=folium.Map(location=[42.5,12.5],zoom_start=5,tiles='OpenStreetMap',control_scale=True)
    clusters={}
    for s in STATUS_COLORS:
        fg=folium.FeatureGroup(name=LABELS.get(s,s),show=True)
        cluster=MarkerCluster(name=LABELS.get(s,s)).add_to(fg)
        clusters[s]=cluster; fg.add_to(fmap)
    for _,r in mp.iterrows():
        s=r.normalized_status; popup=f"<b>{r['name_original']}</b><br>{r['isil']}<br>{r['municipality_name']} ({r['province_abbrev']})<br>{LABELS.get(s,s)}"
        folium.CircleMarker(location=[r.latitude,r.longitude],radius=3,color=STATUS_COLORS.get(s,'#444'),fill=True,fill_opacity=.75,weight=1,popup=popup).add_to(clusters[s])
    folium.LayerControl(collapsed=False).add_to(fmap)
    fmap.save(v/'library_map.html')

    # 2 regional share bar
    rr=reg.sort_values('problematic_share_percent',ascending=True)
    fig,ax=plt.subplots(figsize=(10,8))
    bars=ax.barh(rr.region,rr.problematic_share_percent)
    for b,(_,r) in zip(bars,rr.iterrows()):
        ax.text(b.get_width()+.5,b.get_y()+b.get_height()/2,f"{r.problematic_share_percent:.1f}%  ({int(r.problematic)}/{int(r.total_libraries)})",va='center',fontsize=7)
    ax.set_xlim(0,max(rr.problematic_share_percent)*1.28)
    ax.set_xlabel('Biblioteche problematiche / biblioteche, %')
    ax.set_title('Molise e Liguria hanno le quote regionali più alte, ma su basi assolute molto diverse',loc='left',fontsize=13,pad=14)
    ax.text(0,1.01,'Etichette: quota percentuale e conteggio problematiche/totale; denominator esclude 655 “altri istituti ICCU”.',transform=ax.transAxes,fontsize=9)
    ax.grid(axis='x',alpha=.2)
    fig.text(.01,.01,SOURCE,fontsize=7)
    savefig(fig,v/'status_by_region.png')

    # 3 status distribution
    ss=status.sort_values('count',ascending=True).copy(); ss['label']=ss.normalized_status.map(LABELS).fillna(ss.normalized_status.str.replace('_',' ').str.title())
    fig,ax=plt.subplots(figsize=(10,7))
    bars=ax.barh(ss.label,ss['count'])
    for b,val,pct in zip(bars,ss['count'],ss.share_registry_percent):
        ax.text(b.get_width()+80,b.get_y()+b.get_height()/2,f"{int(val):,} ({pct:.1f}%)",va='center',fontsize=7)
    ax.set_xlabel('Record ICCU')
    ax.set_xlim(0,ss['count'].max()*1.19)
    ax.set_title('Due terzi dello snapshot non hanno uno stato speciale registrato; cessazione e non-censimento sono le categorie successive',loc='left',fontsize=13,pad=14)
    ax.text(0,1.01,'“Nessuno stato speciale registrato” non equivale a piena operatività certificata.',transform=ax.transAxes,fontsize=9)
    ax.grid(axis='x',alpha=.2)
    fig.text(.01,.01,SOURCE,fontsize=7)
    savefig(fig,v/'status_distribution.png')

    # 4 demography scatter
    dm=mun[(mun.population_comparability=='comparable_on_2025_geography')].copy()
    for c in ['population_change_percent','problematic_share','total_libraries']:
        dm[c]=pd.to_numeric(dm[c],errors='coerce')
    dm=dm[(dm.total_libraries>0)&dm.population_change_percent.notna()&dm.problematic_share.notna()]
    fig,ax=plt.subplots(figsize=(9,7))
    ax.scatter(dm.population_change_percent,dm.problematic_share*100,s=12,alpha=.25,edgecolors='none')
    x=np.linspace(dm.population_change_percent.min(),dm.population_change_percent.max(),200); coef=np.polyfit(dm.population_change_percent,dm.problematic_share*100,1); ax.plot(x,coef[0]*x+coef[1],linewidth=1.5)
    r=corr.iloc[0]
    ax.set_xlabel('Variazione popolazione 2019–2025 (%)'); ax.set_ylabel('Quota biblioteche problematiche (%)')
    ax.set_ylim(-2,102); ax.axvline(0,linewidth=.8,alpha=.4)
    ax.set_title('La perdita demografica è associata solo debolmente a una quota più alta di biblioteche problematiche',loc='left',fontsize=13,pad=14)
    ax.text(0,1.01,f"N={int(r.N):,}; Pearson r={r.pearson_r:.3f}; Spearman ρ={r.spearman_rho:.3f}. Associazione osservazionale, non causalità.",transform=ax.transAxes,fontsize=9)
    ax.grid(alpha=.18)
    fig.text(.01,.01,SOURCE+' Comuni con almeno una biblioteca; Trapani/Misiliscemi esclusi perché non comparabili.',fontsize=7)
    savefig(fig,v/'demography_scatter.png')

    # 5 documentation coverage of holdings/special collections for main problematic libraries
    n=int(hsum.problematic_libraries_total); hv=int(hsum.problematic_libraries_with_holding_rows); sv=int(scsum.problematic_libraries_with_special_collections)
    labels=['Patrimonio: almeno una riga documentata','Fondi speciali: almeno un record documentato']; vals=[hv/n*100,sv/n*100]
    fig,ax=plt.subplots(figsize=(9,4.8)); bars=ax.barh(labels,vals)
    for b,val,count in zip(bars,vals,[hv,sv]): ax.text(max(val,.4)+.4,b.get_y()+b.get_height()/2,f"{count:,}/{n:,} ({val:.1f}%)",va='center',fontsize=9)
    ax.set_xlim(0,max(vals+[30])*1.2); ax.set_xlabel('% delle biblioteche problematiche')
    ax.set_title('Il patrimonio è documentato per un quarto delle biblioteche problematiche; i fondi speciali non compaiono nel relativo sottoinsieme',loc='left',fontsize=12,pad=14)
    ax.text(0,1.01,f"Patrimonio: {int(hsum.holding_rows_problematic):,} righe, di cui {int(hsum.holding_rows_quantity_missing):,} con quantità mancante. Lo zero sui fondi speciali indica assenza di record, non assenza certa di fondi.",transform=ax.transAxes,fontsize=8.5)
    ax.grid(axis='x',alpha=.2)
    fig.text(.01,.01,SOURCE,fontsize=7)
    savefig(fig,v/'special_collections.png')

    # extra: top holding materials by libraries
    hm=pd.read_csv(root/'reports'/'analysis_tables'/'problematic_holdings_by_material.csv').head(15).sort_values('libraries')
    fig,ax=plt.subplots(figsize=(10,7)); ax.barh(hm.material.fillna('(materiale non specificato)'),hm.libraries)
    ax.set_xlabel('Biblioteche problematiche con il materiale documentato')
    ax.set_title('Periodici e monografie sono i materiali più spesso documentati nel sottoinsieme problematico coperto dal patrimonio',loc='left',fontsize=12,pad=14)
    ax.text(0,1.01,'Conteggio di biblioteche, non somma delle consistenze; evita di trattare quantità mancanti come zero.',transform=ax.transAxes,fontsize=9)
    ax.grid(axis='x',alpha=.2); fig.text(.01,.01,SOURCE,fontsize=7)
    savefig(fig,v/'problematic_holdings.png')

    # 6 network: largest component only, readable by construction.
    valid=mer[mer.parse_success.astype(str).str.lower().eq('true') & mer.target_exists_in_snapshot.astype(str).str.lower().eq('true') & mer.target_isil.notna()]
    G=nx.DiGraph(); G.add_edges_from(valid[['source_isil','target_isil']].itertuples(index=False,name=None)); comps=sorted(nx.weakly_connected_components(G),key=len,reverse=True)
    H=G.subgraph(comps[0]).copy(); pos=nx.spring_layout(H,seed=42,k=1.1/np.sqrt(max(1,H.number_of_nodes())))
    fig,ax=plt.subplots(figsize=(10,9)); sizes=[45+25*H.in_degree(n) for n in H.nodes()]
    nx.draw_networkx_edges(H,pos,ax=ax,arrows=True,arrowstyle='-|>',arrowsize=8,width=.8,alpha=.35)
    nx.draw_networkx_nodes(H,pos,ax=ax,node_size=sizes,alpha=.85)
    labels={n:n for n in H.nodes() if H.in_degree(n)>=3}; nx.draw_networkx_labels(H,pos,labels=labels,font_size=7,ax=ax)
    ax.set_axis_off(); ax.set_title(f'La componente di confluenza più grande ha {H.number_of_nodes()} nodi e converge verso pochi target',loc='left',fontsize=13,pad=14)
    ax.text(0,1.01,'Visualizzata solo la componente debole maggiore per evitare uno spaghetti chart; dimensione nodo ∝ grado entrante.',transform=ax.transAxes,fontsize=9)
    fig.text(.01,.01,SOURCE+' La rete completa: 1.412 archi validati, 410 componenti.',fontsize=7)
    savefig(fig,v/'mergers_network.png')

    # 7 age structure secondary
    age=dm.copy(); age['share_65_plus_2025']=pd.to_numeric(age.share_65_plus_2025,errors='coerce'); age=age.dropna(subset=['share_65_plus_2025'])
    ac=pd.read_csv(root/'reports'/'analysis_tables'/'age65_problematic_correlation.csv').iloc[0]
    fig,ax=plt.subplots(figsize=(9,7)); ax.scatter(age.share_65_plus_2025,age.problematic_share*100,s=12,alpha=.25,edgecolors='none')
    x=np.linspace(age.share_65_plus_2025.min(),age.share_65_plus_2025.max(),200); coef=np.polyfit(age.share_65_plus_2025,age.problematic_share*100,1); ax.plot(x,coef[0]*x+coef[1],linewidth=1.5)
    ax.set_xlabel('Quota popolazione 65+ nel 2025 (%)'); ax.set_ylabel('Quota biblioteche problematiche (%)'); ax.set_ylim(-2,102)
    ax.set_title('La quota over 65 mostra un’associazione positiva ma debole con la quota di biblioteche problematiche',loc='left',fontsize=13,pad=14)
    ax.text(0,1.01,f"N={int(ac.N):,}; Pearson r={ac.pearson_r:.3f}; Spearman ρ={ac.spearman_rho:.3f}. Analisi secondaria, non causale.",transform=ax.transAxes,fontsize=9)
    ax.grid(alpha=.18); fig.text(.01,.01,SOURCE,fontsize=7)
    savefig(fig,v/'age65_scatter.png')

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]); a=ap.parse_args(); main(a.root.resolve())
