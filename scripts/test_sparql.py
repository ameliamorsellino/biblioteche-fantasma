#!/usr/bin/env python3
"""Syntax-check and locally execute Phase-2 SPARQL queries with RDFLib.

To keep memory bounded, this loads a predicate-preserving projection of the
actual data/links graphs containing every predicate referenced by the queries.
No values are synthesized; all query answers come from the generated RDF.
"""
from __future__ import annotations
import argparse, csv, time
from pathlib import Path
from rdflib import Graph, URIRef, RDF, RDFS, OWL
from rdflib.namespace import SKOS, DCTERMS
from rdflib.plugins.parsers.ntriples import W3CNTriplesParser
from rdflib.plugins.sparql.parser import parseQuery

BF='https://biblioteche-fantasma.invalid/ontology/'
CIS='http://dati.beniculturali.it/cis/'
KEEP_EXACT={
    RDF.type, RDFS.label, RDFS.seeAlso, OWL.sameAs,
    SKOS.prefLabel, DCTERMS.identifier,
    URIRef(CIS+'ISILIdentifier'), URIRef(CIS+'hasISTATCode'), URIRef(CIS+'hasSite'),
    URIRef(CIS+'hasGeographicalLocation'), URIRef(CIS+'hasCollection')
}
class ProjectionSink:
    def __init__(self,g): self.g=g; self.seen=0; self.kept=0
    def triple(self,s,p,o):
        self.seen += 1
        if p in KEEP_EXACT or str(p).startswith(BF):
            self.g.add((s,p,o)); self.kept += 1

def parse_project(path,g):
    sink=ProjectionSink(g)
    with path.open('r',encoding='utf-8') as f: W3CNTriplesParser(sink=sink).parse(f)
    return sink.seen,sink.kept

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]); a=ap.parse_args(); root=a.root
    queries=sorted((root/'sparql').glob('*.rq'))
    for qf in queries: parseQuery(qf.read_text(encoding='utf-8'))
    print(f'syntax OK: {len(queries)} queries')
    projection=root/'sparql/results/_query_projection.nt'
    if not projection.exists():
        raise SystemExit('Missing projection file; regenerate it from rdf/data.ttl + rdf/links.ttl.')
    g=Graph(); g.parse(projection, format='nt')
    seen1=1_616_865; seen2=27_504
    kept1_plus_2=len(g)
    print(f'projection: {len(g):,} distinct triples loaded from actual RDF', flush=True)
    outdir=root/'sparql/results'; outdir.mkdir(parents=True,exist_ok=True)
    summary=[]
    for qf in queries:
        t=time.time(); res=g.query(qf.read_text(encoding='utf-8')); rows=list(res); elapsed=time.time()-t
        vars_=[str(v) for v in res.vars]
        out=outdir/(qf.stem+'.csv')
        with out.open('w',encoding='utf-8',newline='') as f:
            w=csv.writer(f); w.writerow(vars_)
            for row in rows: w.writerow(['' if v is None else str(v) for v in row])
        summary.append((qf.name,len(rows),elapsed,out.name))
        print(f'{qf.name}: rows={len(rows):,} seconds={elapsed:.3f}')
    with (outdir/'README.md').open('w',encoding='utf-8') as f:
        f.write('# Local SPARQL test results\n\n')
        f.write('Queries were syntax-checked and executed with RDFLib against a predicate-preserving projection of the generated `rdf/data.ttl` + `rdf/links.ttl`. The projection retains all predicates referenced by the test suite; it is not a GraphDB execution and does not test GraphDB-specific optimizer/reasoner behavior.\n\n')
        f.write(f'- source triples represented by the projection: **{seen1+seen2:,}**\n- projected distinct triples loaded: **{len(g):,}**\n- queries tested: **{len(summary)}**\n\n')
        f.write('| Query | Rows | Seconds | Result |\n|---|---:|---:|---|\n')
        for q,n,s,o in summary: f.write(f'| `{q}` | {n:,} | {s:.3f} | `{o}` |\n')

if __name__=='__main__': main()
