#!/usr/bin/env python3
"""Execute the SHACL Core subset used by shacl/shapes.ttl.

pySHACL is not installed in the execution environment. This validator reads the
actual SHACL shapes and applies the SHACL Core constraints used in this project:
targetClass, targetSubjectsOf, property/path, minCount, maxCount, datatype,
pattern, nodeKind IRI, class and minInclusive. It is intentionally not claimed
as a general SHACL implementation.
"""
from __future__ import annotations
import argparse, re
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from rdflib import Graph, RDF, URIRef, Literal
from rdflib.namespace import SH, XSD
from rdflib.plugins.parsers.ntriples import W3CNTriplesParser

class Sink:
    def __init__(self, relevant_preds):
        self.relevant = relevant_preds | {RDF.type}
        self.values = defaultdict(lambda: defaultdict(list))
        self.types = defaultdict(set)
        self.subjects_by_pred = defaultdict(set)
    def triple(self, s,p,o):
        if p == RDF.type:
            self.types[s].add(o)
        if p in self.relevant:
            self.values[s][p].append(o)
            self.subjects_by_pred[p].add(s)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]); args=ap.parse_args()
    root=args.root
    sg=Graph(); sg.parse(root/'shacl/shapes.ttl',format='turtle')
    prop_nodes=set(sg.objects(None, SH.property))
    paths={pn: sg.value(pn,SH.path) for pn in prop_nodes}
    relevant={p for p in paths.values() if isinstance(p,URIRef)}
    sink=Sink(relevant)
    with (root/'rdf/data.ttl').open('r',encoding='utf-8') as f:
        W3CNTriplesParser(sink=sink).parse(f)
    results=[]; checked=0
    for shape in sg.subjects(RDF.type,SH.NodeShape):
        targets=set()
        for tc in sg.objects(shape,SH.targetClass):
            targets |= {s for s,ts in sink.types.items() if tc in ts}
        for pred in sg.objects(shape,SH.targetSubjectsOf):
            targets |= sink.subjects_by_pred.get(pred,set())
        for focus in targets:
            checked += 1
            for pn in sg.objects(shape,SH.property):
                path=sg.value(pn,SH.path); vals=sink.values[focus].get(path,[])
                mn=sg.value(pn,SH.minCount); mx=sg.value(pn,SH.maxCount)
                if mn is not None and len(vals) < int(mn): results.append((shape,focus,path,'minCount',f'{len(vals)} < {int(mn)}'))
                if mx is not None and len(vals) > int(mx): results.append((shape,focus,path,'maxCount',f'{len(vals)} > {int(mx)}'))
                dt=sg.value(pn,SH.datatype)
                if dt is not None:
                    for v in vals:
                        if not isinstance(v,Literal) or v.datatype != dt:
                            results.append((shape,focus,path,'datatype',f'{v.n3()} datatype != {dt}'))
                pat=sg.value(pn,SH.pattern)
                if pat is not None:
                    rx=re.compile(str(pat))
                    for v in vals:
                        if not rx.search(str(v)): results.append((shape,focus,path,'pattern',str(v)))
                nk=sg.value(pn,SH.nodeKind)
                if nk == SH.IRI:
                    for v in vals:
                        if not isinstance(v,URIRef): results.append((shape,focus,path,'nodeKind','not IRI'))
                cls=sg.value(pn,SH['class'])
                if cls is not None:
                    for v in vals:
                        if cls not in sink.types.get(v,set()): results.append((shape,focus,path,'class',f'{v} lacks rdf:type {cls}'))
                mi=sg.value(pn,SH.minInclusive)
                if mi is not None:
                    threshold=Decimal(str(mi))
                    for v in vals:
                        try:
                            if Decimal(str(v)) < threshold: results.append((shape,focus,path,'minInclusive',str(v)))
                        except Exception: results.append((shape,focus,path,'minInclusive','non-numeric'))
    report=root/'reports/shacl_validation.md'
    with report.open('w',encoding='utf-8') as f:
        f.write('# SHACL validation\n\n')
        f.write('## Execution engine\n\n')
        f.write('`pyshacl` was not available in the runtime. The project therefore executed the actual `shacl/shapes.ttl` with `scripts/validate_shacl.py`, a project-local executor for the SHACL Core features used by these shapes (`targetClass`, `targetSubjectsOf`, `sh:property`, `sh:path`, `minCount`, `maxCount`, `datatype`, `pattern`, `nodeKind`, `class`, `minInclusive`). It is **not** a complete SHACL engine and this limitation must be retained when publishing the project.\n\n')
        f.write(f'- focus nodes checked: **{checked:,}**\n')
        f.write(f'- constraint violations: **{len(results):,}**\n')
        f.write(f'- conforms for the executed subset: **{"YES" if not results else "NO"}**\n\n')
        if results:
            f.write('## First violations\n\n')
            for r in results[:100]: f.write(f'- shape `{r[0]}` focus `{r[1]}` path `{r[2]}` constraint `{r[3]}`: {r[4]}\n')
    print(f'focus nodes checked: {checked:,}; violations: {len(results):,}; conforms={not results}')
    if results: raise SystemExit(1)

if __name__=='__main__': main()
