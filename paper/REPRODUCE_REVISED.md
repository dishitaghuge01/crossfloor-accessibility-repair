# Reproduce the revised master

Use Python 3.12. The final package records the actual environment and compiler.
Create a fresh environment and install the tested Windows locks:

```text
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-dev.lock.txt -r requirements-ifc.lock.txt -r requirements-figures.lock.txt -r requirements-evaluation.lock.txt
.venv/Scripts/python -m pip install -e . --no-deps
```

Use that environment's Python for the commands below. On Windows, set TEMP/TMP
to a writable workspace directory and give pytest a workspace --basetemp. On
another platform, preserve direct versions where supported and record the
actual package/GEOS/platform manifest; do not treat cross-platform times as
hardware-isolated replications.

Full workflow, using fresh output paths:

```text
python scripts/download_public_buildings.py
python scripts/public_building_controlled.py --sources data/external/public-buildings --output runs/source-inventory
python scripts/assemble_multiroom_dataset.py --audit runs/source-inventory --output runs/source-dataset
```

The assembly command performs maximum-cardinality eligible nonoverlapping room
selection, constructs two-storey variants, attempts the immediate next original
storey, checks original room rings/IDs and consecutive-storey admission, and
writes a dataset/source/script fingerprint manifest. Hypothetical access and
intervention assumptions remain explicit. Commit tracked source before timing;
run performance studies sequentially. Routine inputs use five fresh workers; structurally expensive cases (at least 100 actions, rooms or background obstacles per floor, or seven connectivity floors) use three. The source-size criteria are fixed before the final source timing campaign.

```text
python scripts/run_revised_evaluation.py --output runs/authored --repetitions 5
python scripts/run_revised_evaluation.py --instances runs/source-dataset/instances --output runs/building --repetitions 5
python scripts/export_portable_evidence.py runs/authored runs/authored-portable
python scripts/export_portable_evidence.py runs/building runs/building-portable
python scripts/audit_revised_evidence.py runs/authored-portable
python scripts/audit_revised_evidence.py runs/building-portable
python scripts/profile_recognition_operations.py --evidence runs/authored-portable runs/building-portable --output runs/geometry-profile
python scripts/run_revised_semantic_controls.py --evidence runs/authored-portable --output runs/semantic-controls
python scripts/make_revised_figures.py --controlled runs/authored-portable --building runs/building-portable --source-audit runs/source-dataset/two-storey --output runs/figures
python scripts/build_revised_master.py --controlled runs/authored-portable --building runs/building-portable --source-audit runs/source-dataset/two-storey --three-audit runs/source-dataset/three-storey --controls runs/semantic-controls --geometry-profile runs/geometry-profile --figures runs/figures --output runs/master
```

The audits validate the formal results schema, input/manifest/raw correspondence,
exact labels, independent paid rectangle/cost/owner arithmetic and every small
oracle certificate with the separate replay/enumeration checker. The manuscript
builder checks certificate audit hashes instead of blindly trusting filenames.
Read summary.csv alongside full records.json: statuses distinguish completion,
heuristic failure, internal cap, unsupported scope, timeout and internal error.
Summary min/median/max describe recorded termination times; completed-solve
comparisons in the paper explicitly filter for completed outcomes.

Compile master.tex from its generated folder with the unchanged IEEEtran.cls
and vector figures. Use repeated pdfLaTeX reference passes or Tectonic. The
release report names the tested engine/version and diagnostics. No external PDF
checker upload or conference submission is part of this workflow.

Smaller smoke workflow:

```text
python scripts/run_revised_evaluation.py --smoke --repetitions 1 --output runs/smoke
python scripts/export_portable_evidence.py runs/smoke runs/smoke-portable
python scripts/audit_revised_evidence.py runs/smoke-portable
```

This uses the complete ownership example and one small input per structural
family, including valid pruning/cache paths where applicable. It intentionally
cannot replace full manuscript evidence: selected-table completeness/source
coverage checks must fail rather than invent missing results.

For offline review, audit the supplied portable evidence and inspect raw results,
certificates, source screening, original-room inventories, extraction exclusions,
licence notices and normalization provenance. Export changes only path separators
and certificate paths; original record bytes remain included and audited, with
no measurement/selection/status edits. Raw IFC files are omitted; the pinned
downloader and recorded SHA256 values reproduce them. Generated runs and PDFs
stay outside Git. Source-derived experiments are hypothetical controlled inputs,
not validated actual-building repairs, permission records or construction prices.
