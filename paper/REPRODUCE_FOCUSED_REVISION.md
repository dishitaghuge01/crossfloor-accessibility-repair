# Reproduce the focused research revision

The research package separates the current paper, included campaigns, explicit
development exclusions and immutable historical archive. No raw IFC/DWG or source
article PDF is required to inspect/rebuild the saved-data results. Source building
attribution/license/revision metadata remain attached to the derived inputs.

Unzip `source-code.zip` to a source directory. Use Python3.12 and the repository's
locked development requirements (README). The measurement commits are separately
recorded in every campaign; `measured-joint-source.zip` is the exact primary Git
snapshot. Timing will vary by machine; regenerate inputs/figures from saved data
to check artifact consistency without rerunning optimization.

## Inputs

From the extracted source directory, substitute the research-package root for
`PACKAGE` and new, nonexistent output directories for `NEW_*`:

```powershell
python scripts/build_joint_network_study.py --source PACKAGE/reproduction-base-network --output NEW_JOINT_INPUTS
python scripts/build_parameter_study.py --output NEW_PARAMETER_INPUTS
```

Joint inputs are fifteen tier variants from five catalogue layouts/two buildings,
not fifteen independent layouts. The primary schedule measures seven combinations.
The parameter dataset has23 authored levels/eight families. All intervention
reservations, profile permissions and costs are experimental assumptions.

## Saved-data figures and manuscript

```powershell
python scripts/summarize_joint_network_study.py --campaign PACKAGE/evidence/joint-primary --output NEW_JOINT_SUMMARY --reuse-audit PACKAGE/evidence/joint-summary/summary.json
python scripts/summarize_joint_network_study.py --campaign PACKAGE/evidence/parameters --output NEW_PARAMETER_SUMMARY --reuse-audit PACKAGE/evidence/parameter-summary/summary.json
python scripts/plot_asynchronous_retirement.py --output NEW_EXPLANATORY_FIGURE
python scripts/build_focused_revision.py --base PACKAGE/reproduction-base --summary NEW_JOINT_SUMMARY --parameter-summary NEW_PARAMETER_SUMMARY --asynchronous-figure NEW_EXPLANATORY_FIGURE/asynchronous-retirement.pdf --segment-controls PACKAGE/evidence/relevant-segment-controls/controls.json --output NEW_PAPER
```

Compile `NEW_PAPER/master.tex` with Tectonic0.17 or an appropriate TeX distribution.
The archived reproduction-base supplies preserved theory and schematics; it is not the current manuscript. The source ZIP includes IEEEtran.cls and the eight referenced PDF figures.
The supplied compile used TeX Gyre Termes/embedded fonts; `pdf-qa.json` records
structural checks. `audit_research_pdf.py` additionally requires pypdf and checks
letter size, embedded fonts, no Type3, overflow, reference order and unresolved
references. Render pages for visual QA; structural checks alone are insufficient.
PDF metadata may vary on recompilation; source/input/figure hashes are the stronger
deterministic checks. A clean source archive reconstruction was checked locally.

The cache-reuse option verifies raw and manifest hashes before reusing prior
full-replay audits. Use `--audit` instead for fresh replay of each distinct selection.
Relevant-S checks are untimed feasibility controls, not optimum certificates.

## Fresh optimization campaigns

Run in a clean Git checkout; never edit/commit during a campaign. Parent pipeline
includes fresh-process startup, recognition, model construction, solve and required
replay. Internal stages have a five-second reserve; hard termination can still
interrupt replay. Recovered timeout candidates are separately audited after the
deadline and do not count as completed full-objective pipelines.

```powershell
python scripts/run_joint_network_study.py --dataset NEW_JOINT_INPUTS --output NEW_PRIMARY --timeout 60 --cases clinic-network-16-s0-connectivity clinic-network-16-s0-resource clinic-network-16-s0-full clinic-network-48-s0-full clinic-network-96-s0-full molio-network-16-s0-full molio-network-36-s0-full
python scripts/run_parameter_study.py --dataset NEW_PARAMETER_INPUTS --output NEW_STRUCTURAL
```

These produce112 and276 observations respectively, each with two forward/reverse
repetitions and a frozen actual schedule. No RAM cap is imposed. Keep the separate
three-run stage diagnostic, all historical observations and excluded development
records out of these timing aggregates. `registries/campaign_registry.csv` marks
inclusion explicitly; `archive.zip!member` locates a historical nested record.
The included timed total2753 includes2362 historical observations and3 separate
diagnostics; it is not one homogeneous experiment. Seven additional relevant-S
controls are untimed and excluded from that denominator.

Neither human proof review, literature priority nor actual construction validation
is certified by reproduction. A chosen conference's page/anonymity/artifact rules
must be applied when adapting this detailed master.
