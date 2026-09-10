# SHACL validation

## Execution

- engine: **pySHACL 0.40.1**
- RDF backend: **PyOxigraph persistent store**
- shapes graph: `shacl/shapes.ttl`
- explicit triples validated: **1,644,602**
- inference: **none**
- Meta-SHACL validation of the shapes graph: **enabled**
- abort on first violation: **no**

## Result

- conforms: **YES**
- validation results: **0**
- violations: **0**
- warnings: **0**
- infos: **0**

## Generated reports

- `reports/shacl_validation.md` - validation summary
- `reports/shacl_validation.txt` - pySHACL human-readable report
- `reports/shacl_validation.ttl` - standard RDF SHACL ValidationReport

## Reproduction

```bash
python -m pip install -r requirements.txt
python scripts/validate_shacl.py --root .
```

The validator reuses the persistent `.cache/oxigraph/` store also used by the local SPARQL runner. GraphDB is not required.
