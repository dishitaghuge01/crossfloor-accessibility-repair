# Reproduce the permission-backed CAD pilot

Read user_cad_protocol.md and user_cad_results.md first. This additional
12-observation campaign is separate from the frozen2274 observations.
It is one manually reconstructed room pair with four catalogue variants.

The private source DWG is intentionally not distributed. Its required SHA256
is0399309c5d19218bad44329471745354098b28431548ccf9a1bff5bd8a779acc.
An authorized researcher with the identical file can decode it using GNU
LibreDWG0.14 from https://github.com/LibreDWG/libredwg/releases/tag/0.14:

```text
dwgread -O JSON -o path/to/decoded.json path/to/source.dwg
python scripts/adapt_user_cad.py --source path/to/source.dwg --decoded path/to/decoded.json --output runs/new-cad-dataset
python scripts/run_user_cad_pilot.py --dataset runs/new-cad-dataset --output runs/new-cad-evaluation
```

Use the existing release Python environment and a clean Git checkout. The
adapter checks the pinned source, selected label/coordinate dimensions,
registration, columns, slots and recognizer. Run tests/test_user_cad_adapter.py
for block-transform/external-reference/source guards. The adapter does not
recover a full semantic BIM automatically and does not infer construction
permissions. Never distribute private-selected-source.json or decoded.json.

The private review package includes authorized derived instance inputs and
evaluation records, so those input-level checks can be repeated without the
original DWG. Source-level reconstruction requires the original source.

Generate the integrated manuscript using the delivered paper folder as base:

```text
python scripts/build_user_cad_master.py --dataset runs/new-cad-dataset --evaluation runs/new-cad-evaluation --base path/to/paper --output runs/new-cad-master
```

For the already supplied evidence use evidence/user-cad-dataset and
evidence/user-cad-evaluation. The figure builder uses the private source-wall
extract when available, or the delivered cad-wall-underlay.json with only
anonymized wall segments clipped to the two plotted room crops. Figure and
source regeneration therefore need no full drawing or private extract;
source-level reconstruction still requires the DWG. The
builder selects pre-cad-master.tex automatically to avoid duplication.
For a full sequential manuscript rebuild, supply the preceding gap-assessment
stage as --base. Compile with Tectonic0.17.0/XeTeX, then check fonts/references,
letter pages and rendered layout.
