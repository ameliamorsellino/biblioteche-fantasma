# SHACL validation

## Execution engine

`pyshacl` was not available in the runtime. The project therefore executed the actual `shacl/shapes.ttl` with `scripts/validate_shacl.py`, a project-local executor for the SHACL Core features used by these shapes (`targetClass`, `targetSubjectsOf`, `sh:property`, `sh:path`, `minCount`, `maxCount`, `datatype`, `pattern`, `nodeKind`, `class`, `minInclusive`). It is **not** a complete SHACL engine and this limitation must be retained when publishing the project.

- focus nodes checked: **82,519**
- constraint violations: **0**
- conforms for the executed subset: **YES**

