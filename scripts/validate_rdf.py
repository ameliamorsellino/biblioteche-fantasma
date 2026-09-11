#!/usr/bin/env python3
"""Validate the Phase-2 RDF serialization and report structural graph metrics.

The large instance files are streamed as strict N-Triples (a valid Turtle subset),
while the compact ontology/metadata files are parsed with RDFLib.
"""
from __future__ import annotations
import argparse, hashlib, re
from collections import Counter
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlsplit
from rdflib import Graph, Literal, URIRef, RDF, RDFS, OWL, XSD
from rdflib.namespace import SKOS
from rdflib.plugins.parsers.ntriples import W3CNTriplesParser
from project_config import PUBLIC_BASE

BASE = PUBLIC_BASE
ONTO = BASE + 'ontology/'
RES = BASE + 'resource/'
CIS='http://dati.beniculturali.it/cis/'
DCAT='http://www.w3.org/ns/dcat#'

class MetricsSink:
    def __init__(self):
        self.triples=0; self.predicates=set(); self.types=Counter(); self.uri_errors=[]; self.datatype_errors=[]
        self.local_subjects=set(); self.local_objects=set(); self.link_local_subjects=set(); self.external_link_targets=Counter()
        self.local_predicates=set(); self.local_class_objects=set()
    def _check_uri(self,u):
        s=str(u); parts=urlsplit(s)
        if not parts.scheme or (parts.scheme in {'http','https'} and not parts.netloc) or re.search(r'[\x00-\x20<>"{}|\\^`]',s):
            if len(self.uri_errors)<100: self.uri_errors.append(s)
    def _check_literal(self,l):
        dt=l.datatype
        if not dt: return
        v=str(l)
        try:
            if dt==XSD.integer: int(v)
            elif dt==XSD.decimal: Decimal(v)
            elif dt==XSD.boolean:
                if v not in {'true','false','1','0'}: raise ValueError(v)
            elif dt==XSD.date: date.fromisoformat(v)
            elif dt==XSD.dateTime: datetime.fromisoformat(v.replace('Z','+00:00'))
        except Exception:
            if len(self.datatype_errors)<100: self.datatype_errors.append((v,str(dt)))
    def triple(self,s,p,o):
        self.triples+=1; self.predicates.add(p)
        for u in (s,p,o):
            if isinstance(u,URIRef): self._check_uri(u)
        if isinstance(o,Literal): self._check_literal(o)
        if isinstance(s,URIRef) and str(s).startswith(BASE): self.local_subjects.add(s)
        if isinstance(o,URIRef) and str(o).startswith(BASE): self.local_objects.add(o)
        if isinstance(p,URIRef) and str(p).startswith(ONTO): self.local_predicates.add(p)
        if p==RDF.type:
            self.types[o]+=1
            if isinstance(o,URIRef) and str(o).startswith(ONTO): self.local_class_objects.add(o)
        if p in {OWL.sameAs, RDFS.seeAlso, SKOS.exactMatch, SKOS.closeMatch}:
            if isinstance(s,URIRef) and str(s).startswith(RES): self.link_local_subjects.add(s)
            if isinstance(o,URIRef) and not str(o).startswith(BASE): self.external_link_targets[p]+=1

def stream_parse(path:Path,sink:MetricsSink):
    with path.open('r',encoding='utf-8') as f: W3CNTriplesParser(sink=sink).parse(f)

def duplicate_lines(path:Path):
    seen=set(); dup=0; lines=0
    with path.open('rb') as f:
        for line in f:
            if not line.strip(): continue
            lines+=1; h=hashlib.blake2b(line,digest_size=8).digest()
            if h in seen: dup+=1
            else: seen.add(h)
    return lines,dup

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]); a=ap.parse_args(); root=a.root
    errors=[]; warnings=[]
    ont=Graph(); ont.parse(root/'ontology/ontology.ttl',format='turtle')
    owlxml=Graph(); owlxml.parse(root/'ontology/ontology.owl',format='xml')
    if set(ont)!=set(owlxml): warnings.append('ontology.ttl and ontology.owl parse but are not triple-identical after format conversion.')
    meta=Graph(); meta.parse(root/'rdf/metadata.ttl',format='turtle')
    shapes=Graph(); shapes.parse(root/'shacl/shapes.ttl',format='turtle')

    data_sink=MetricsSink(); stream_parse(root/'rdf/data.ttl',data_sink)
    links_sink=MetricsSink(); stream_parse(root/'rdf/links.ttl',links_sink)
    data_lines,data_dups=duplicate_lines(root/'rdf/data.ttl'); link_lines,link_dups=duplicate_lines(root/'rdf/links.ttl')
    if data_dups: errors.append(f'data.ttl contains {data_dups} duplicate serialized triples')
    if link_dups: errors.append(f'links.ttl contains {link_dups} duplicate serialized triples')
    if data_lines!=data_sink.triples: errors.append('data.ttl line/triple count mismatch')
    if link_lines!=links_sink.triples: errors.append('links.ttl line/triple count mismatch')

    # URI/datatype checks
    for name,s in [('data',data_sink),('links',links_sink)]:
        if s.uri_errors: errors.append(f'{name}: invalid URI samples: {s.uri_errors[:5]}')
        if s.datatype_errors: errors.append(f'{name}: invalid datatype lexical forms: {s.datatype_errors[:5]}')

    # Ontology term use checks.
    property_defs=set(ont.subjects(RDF.type,OWL.ObjectProperty))|set(ont.subjects(RDF.type,OWL.DatatypeProperty))|set(ont.subjects(RDF.type,RDF.Property))
    class_defs=set(ont.subjects(RDF.type,OWL.Class))|set(ont.subjects(RDF.type,RDFS.Class))
    unresolved_props=(data_sink.local_predicates|links_sink.local_predicates)-property_defs
    unresolved_classes=(data_sink.local_class_objects|links_sink.local_class_objects)-class_defs
    if unresolved_props: errors.append('Undefined local predicates: '+', '.join(map(str,sorted(unresolved_props,key=str))))
    if unresolved_classes: errors.append('Undefined local classes: '+', '.join(map(str,sorted(unresolved_classes,key=str))))

    # Local resource targets used from data must be defined somewhere in data/metadata/ontology.
    meta_local_subjects={s for s in meta.subjects() if isinstance(s,URIRef) and str(s).startswith(BASE)}
    ont_local_subjects={s for s in ont.subjects() if isinstance(s,URIRef) and str(s).startswith(BASE)}
    defined=data_sink.local_subjects|meta_local_subjects|ont_local_subjects
    # Distribution document URLs are Web resources, not necessarily RDF entities in the instance graph.
    dangling={u for u in data_sink.local_objects if u not in defined and not str(u).startswith(BASE+'distribution/')}
    if dangling: errors.append(f'Dangling local object resources: {len(dangling)}; samples: '+', '.join(map(str,list(dangling)[:10])))

    # Every local subject occurring in links must exist as an RDF instance in data.
    missing_link_subjects=links_sink.link_local_subjects-data_sink.local_subjects
    if missing_link_subjects: errors.append(f'Link subjects absent from data graph: {len(missing_link_subjects)}')

    warnings += [
        'Project resource/ontology IRIs use the public GitHub Pages namespace; Web dereferenceability is verified separately after deployment.',
        'External targets were generated from identifier-based, documented URI rules; the runtime did not individually dereference all targets.',
        'N-Triples line serialization is used for data.ttl and links.ttl; N-Triples is a syntactic subset of Turtle.',
    ]

    # Counts for compact graphs and all predicates.
    all_preds=set(data_sink.predicates)|set(links_sink.predicates)|set(p for _,p,_ in meta)|set(p for _,p,_ in ont)
    all_types=Counter(data_sink.types); all_types.update(links_sink.types); all_types.update(o for _,_,o in meta.triples((None,RDF.type,None)))
    total=len(ont)+len(meta)+data_sink.triples+links_sink.triples

    report=root/'reports/rdf_validation.md'
    with report.open('w',encoding='utf-8') as f:
        f.write('# RDF validation\n\n')
        f.write('## Result\n\n')
        f.write(f'- overall structural result: **{"PASS" if not errors else "FAIL"}**\n')
        f.write(f'- errors: **{len(errors)}**\n- warnings: **{len(warnings)}**\n\n')
        f.write('## Parsing and graph size\n\n')
        f.write(f'- `rdf/data.ttl`: **{data_sink.triples:,}** triples; strict N-Triples parse PASS; therefore valid Turtle subset\n')
        f.write(f'- `rdf/links.ttl`: **{links_sink.triples:,}** triples; strict N-Triples parse PASS; therefore valid Turtle subset\n')
        f.write(f'- `rdf/metadata.ttl`: **{len(meta):,}** triples; RDFLib Turtle parse PASS\n')
        f.write(f'- `ontology/ontology.ttl`: **{len(ont):,}** triples; RDFLib Turtle parse PASS\n')
        f.write(f'- `ontology/ontology.owl`: **{len(owlxml):,}** triples; RDF/XML parse PASS\n')
        f.write(f'- total import graph (ontology + data + metadata + links): **{total:,}** triples\n')
        f.write(f'- distinct predicates across ontology/data/metadata/links: **{len(all_preds):,}**\n')
        f.write(f'- distinct instance `rdf:type` objects in data: **{len(data_sink.types):,}**\n\n')
        f.write('## Entity counts by RDF type (instance data)\n\n| Type | Count |\n|---|---:|\n')
        for t,n in sorted(data_sink.types.items(),key=lambda x:(-x[1],str(x[0]))): f.write(f'| `{t}` | {n:,} |\n')
        f.write('\n## Integrity checks\n\n')
        f.write(f'- duplicate serialized triples in `data.ttl`: **{data_dups:,}**\n')
        f.write(f'- duplicate serialized triples in `links.ttl`: **{link_dups:,}**\n')
        f.write(f'- undefined local predicates used: **{len(unresolved_props):,}**\n')
        f.write(f'- undefined local classes used: **{len(unresolved_classes):,}**\n')
        f.write(f'- dangling local resource targets (excluding distribution document URLs): **{len(dangling):,}**\n')
        f.write(f'- link subjects not present in data graph: **{len(missing_link_subjects):,}**\n')
        f.write(f'- datatype lexical errors detected: **{len(data_sink.datatype_errors)+len(links_sink.datatype_errors):,}**\n')
        f.write(f'- malformed URI errors detected: **{len(data_sink.uri_errors)+len(links_sink.uri_errors):,}**\n\n')
        if errors:
            f.write('## Errors\n\n'); [f.write(f'- {e}\n') for e in errors]
        f.write('\n## Warnings / publication limits\n\n'); [f.write(f'- {w}\n') for w in warnings]
        f.write('\n## Validation scope\n\nThe validator checks parsing, URI syntax, selected XML Schema lexical forms, local ontology term declarations, link-subject existence, dangling project resources and exact duplicate serializations. SHACL constraints are reported separately in `reports/shacl_validation.md`.\n')
    print(f'total={total:,} data={data_sink.triples:,} links={links_sink.triples:,} ontology={len(ont):,} metadata={len(meta):,}')
    print(f'instance_types={len(data_sink.types)} predicates={len(all_preds)} errors={len(errors)} warnings={len(warnings)}')
    for t,n in data_sink.types.most_common(): print(f'{n:>8} {t}')
    if errors: raise SystemExit(1)

if __name__=='__main__': main()
