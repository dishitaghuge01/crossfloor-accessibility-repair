# Cross-Floor Accessibility Repair

Research repository for minimum-disruption repair of frozen multi-floor layouts.

Status: active candidate. Novelty is not established until the closest-work and algorithmic-result gates pass.

The M01 controlled implementation includes a versioned schema, 18 micro-instances, profile graphs, typed action replay, exhaustive oracle, independent graph/certificate checker, and an initial complexity memo. The five named architectural full-text comparisons are complete; broader novelty and thesis gates remain conditional. See [progress](PROGRESS.md) and [closest-work comparison](docs/closest_work_matrix.md).

## Run locally

Python 3.11 or later is required. No GPU is needed.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m cfar.cli validate examples/micro/01_missing_metadata_link.json
.\.venv\Scripts\python.exe -m cfar.cli solve examples/micro/08_original_not_optimal.json --variant SCFAR --output runs/demo-original
.\.venv\Scripts\python.exe -m cfar.cli verify examples/micro/08_original_not_optimal.json runs/demo-original/certificate.json
.\.venv\Scripts\python.exe -m cfar.cli solve examples/micro/07_strict_vs_relaxed.json --variant RCFAR --topology-weight 1 --output runs/demo-relaxed
```

Use a new empty output directory per run. The CLI creates result, certificate, verification, manifest, and JSONL ledger files; `runs/` is ignored. The oracle guard defaults to at most 20 candidate actions and still takes exponential time. A successful certificate proves the supplied finite model, not all possible building renovations.

`requirements-dev.lock.txt` records the tested Windows/Python 3.12 environment; install it before the editable package for exact versions on a compatible interpreter. The dependency ranges in `pyproject.toml` permit other supported Python versions.

Read [implementation contract](docs/implementation_contract.md), [case catalogue](examples/README.md), [complexity memo](docs/complexity_memo.md), and [master plan](docs/master_plan.md) before extending the model. RCFAR currently supports polygon reshaping with original room IDs; general splits/merges and richer physical construction are deferred explicitly.
