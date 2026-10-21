# Reproduce the corrected research-first manuscript

The current main paper and separate evidence supplement are generated from
the frozen combined source in reproduction-base/ and the saved baseline
records. This revision changes reporting/organization,not solver measurements.
Three targeted table-completion regression tests pass. Solver/kernel source
and all2286 delivered observations remain unchanged.

From the extracted current source-code.zip root, with paths adjusted to your
research-package extraction:

```text
python scripts/build_focused_master.py --base path/to/reproduction-base --controlled path/to/evidence/controlled --building path/to/evidence/building --output runs/new-focused
```

The builder verifies stored record fingerprints; checks the displayed timing
rows against their raw statuses/times; includes feasible greedy completions;
regenerates TableVIII; reconciles final implemented ablations; states the
negative practical findings; and separates documentary/CAD material.
reporting-audit.json records the source hashes,corrected cells,statuses,
15 connectivity ratios and source-catalogue action counts. No benchmark is
rerun. The corrected upstream table generator and evaluation-text source also
prevent the old errors from being reintroduced.

Compile main/master.tex and supplement/master.tex independently with
Tectonic0.17.0 or another XeTeX-capable engine. Each directory has its own
IEEEtran.cls and only the figures it uses. The supplied source ZIP compiles
the main master.tex at its root and the supplement in supplementary-evidence/.
Check fonts,references,US-letter pages and rendered layout before distribution.

The archival reproduction-base source retains previous-stage text solely as
a deterministic input. It is not the current manuscript. Historical stage
reproduction guides/data remain for provenance; they do not supersede this
final transformation. Documentary/CAD evidence resides in supplementary-evidence/.
Raw CAD/IFC/PDF sources and private extracts are excluded. Source-level
reconstruction requires the corresponding authorized source files.
