# Reproduce the focused research revision

The research package separates the current paper, included campaigns, explicit
development exclusions and immutable historical archive. No raw IFC/DWG or source
article PDF is required to inspect/rebuild the saved-data results. Source building
attribution/license/revision metadata remain attached to the derived inputs.

Unzip `source-code.zip` to a source directory. Use Python3.12 and the repository's
locked development requirements (README). The measurement commits are separately
recorded in every campaign; `measured-joint-source.zip` is the exact primary Git
snapshot. measured-kernel-bytes.zip preserves exact measured module/spec bytes for fingerprint checks when Git line-ending normalization differs. Timing will vary by machine; regenerate inputs/figures from saved data
to check artifact consistency without rerunning optimization.

## Inputs

From the extracted source directory, substitute the research-package root for
`PACKAGE` and new, nonexistent output directories for `NEW_*`:

```powershell
python scripts/build_joint_network_study.py --source PACKAGE/reproduction-base-network --output NEW_JOINT_INPUTS
python scripts/build_parameter_study.py --output NEW_PARAMETER_INPUTS
python scripts/build_event_width_followup.py --output NEW_EVENT_WIDTH_INPUTS
python scripts/run_matched_permissions.py --source NEW_JOINT_INPUTS/instances/clinic-network-16-s0-full.json --dataset NEW_MATCHED_INPUTS
python scripts/build_local_band_study.py --output NEW_LOCAL_INPUTS --sizes 8 24 48 --seeds 0 1 2
python scripts/build_private_bay_study.py --output NEW_BAY_INPUTS --sizes 2 8 16 32
```

Joint inputs are fifteen tier variants from five catalogue layouts/two buildings,
not fifteen independent layouts. The primary schedule measures seven combinations.
The parameter dataset has23 authored levels/eight families. A separate posthoc dataset has two event-width controls. All intervention
reservations, profile permissions and costs are experimental assumptions.

## Saved-data figures and manuscript

```powershell
python scripts/summarize_joint_network_study.py --campaign PACKAGE/evidence/joint-primary --output NEW_JOINT_SUMMARY --reuse-audit PACKAGE/evidence/joint-summary/summary.json
python scripts/summarize_joint_network_study.py --campaign PACKAGE/evidence/parameters --output NEW_PARAMETER_SUMMARY --reuse-audit PACKAGE/evidence/parameter-summary/summary.json
python scripts/summarize_joint_network_study.py --campaign PACKAGE/evidence/event-width-followup --output NEW_EVENT_WIDTH_SUMMARY --reuse-audit PACKAGE/evidence/event-width-summary/summary.json --no-plots
python scripts/summarize_joint_network_study.py --campaign PACKAGE/evidence/matched-permissions --output NEW_MATCHED_SUMMARY --reuse-audit PACKAGE/evidence/matched-permissions-summary/summary.json --no-plots
python scripts/summarize_joint_network_study.py --campaign PACKAGE/evidence/local-band-scaling --output NEW_LOCAL_SUMMARY --reuse-audit PACKAGE/evidence/local-band-summary/summary.json --no-plots
python scripts/summarize_joint_network_study.py --campaign PACKAGE/evidence/private-bay-scaling --output NEW_BAY_SUMMARY --reuse-audit PACKAGE/evidence/private-bay-summary/summary.json --no-plots
python scripts/summarize_frontier_scaling.py --local NEW_LOCAL_SUMMARY --bays NEW_BAY_SUMMARY --certificates PACKAGE/evidence/frontier-certificates --output NEW_SCALING_SUMMARY
python scripts/summarize_joint_network_study.py --campaign PACKAGE/evidence/structural-band-locality --output NEW_STRUCTURAL_AUDIT --reuse-audit PACKAGE/evidence/structural-band-audit/summary.json --no-plots
python scripts/summarize_structural_bands.py --source NEW_STRUCTURAL_AUDIT --campaign PACKAGE/evidence/structural-band-locality --output NEW_STRUCTURAL_SUMMARY
python scripts/plot_asynchronous_retirement.py --output NEW_EXPLANATORY_FIGURE
python scripts/build_structural_revision.py --base PACKAGE/reproduction-base --summary NEW_JOINT_SUMMARY --parameter-summary NEW_PARAMETER_SUMMARY --asynchronous-figure NEW_EXPLANATORY_FIGURE/asynchronous-retirement.pdf --segment-controls PACKAGE/evidence/relevant-segment-controls/controls.json --event-width-summary NEW_EVENT_WIDTH_SUMMARY --matched-summary NEW_MATCHED_SUMMARY --scaling-summary NEW_SCALING_SUMMARY --local-summary NEW_LOCAL_SUMMARY --structural-summary NEW_STRUCTURAL_SUMMARY --output NEW_PAPER
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
python scripts/run_parameter_study.py --dataset NEW_EVENT_WIDTH_INPUTS --output NEW_EVENT_WIDTH
python scripts/run_matched_permissions.py --dataset NEW_MATCHED_INPUTS --output NEW_MATCHED
python scripts/run_frontier_scaling.py --dataset NEW_LOCAL_INPUTS --output NEW_LOCAL_RUNS
python scripts/run_frontier_scaling.py --dataset NEW_BAY_INPUTS --output NEW_BAY_RUNS --private-bays
```

The first three produce112,276 and24 observations respectively, each with two forward/reverse
repetitions and a frozen actual schedule. The separate permission-only comparison produces8
observations with two methods and two conditions. No RAM cap is imposed. Keep the separate
three-run stage diagnostic, all historical observations and excluded development
records out of these timing aggregates. `registries/campaign_registry.csv` marks
inclusion explicitly; `archive.zip!member` locates a historical nested record.
The included timed total2893 includes2362 historical,112 primary,276 structural,24 event-width observations and3 separate
diagnostics,8 permission-only matched observations,36 local-band and24 private-bay observations plus48 separate structural/locality observations; it is not one homogeneous experiment. Seven additional relevant-S
controls are untimed and excluded from that denominator.

Neither human proof review, literature priority nor actual construction validation
is certified by reproduction. A chosen conference's page/anonymity/artifact rules
must be applied when adapting this detailed master.


## Frontier certificates, independent reference and supplementary details

New scaling runs use90s external/85s internal budgets, not the older primary60s
or parameter30s protocols. Their36 and24 rows remain separate. Static certificates
and nine independent family references are untimed:

```powershell
python scripts/event_frontier_certificate.py INPUT.json NEW_CERTIFICATE.json
python scripts/local_band_reference.py LOCAL_BAND_INPUT.json NEW_REFERENCE.json
```

The supplied per-input certificates have deterministic event counts/domain products;
`index.json` collects their non-event fields for plotting. Compare generated JSON
against those supplied files. The independent reference is admitted only for the
fixed local-band rectangles and chain. Its ledgers and clean manifests are at
`evidence/local-band-references`; source details and proof are in
`docs/local_band_subclass.md`. The final source keeps older full paper matrices
rebuildable through `build_focused_revision.py`; the current master promotes the
new result with `build_frontier_revision.py`. The detailed generic-logic transfer
is `source-code.zip!docs/modern_connectivity_comparison.md`, with comparison notes
in the research package. `intervention-benchmark.zip` separately supplies63 input
files and a canonical fingerprint manifest; duplicates are explicit.


## Current structural/locality master

Use `build_structural_revision.py` with the same arguments as the frontier builder
above and additionally `--structural-summary NEW_STRUCTURAL_SUMMARY`. It promotes
the transient theorem, schedule separation and locality-tested bounded regime;
older floor counting is supplementary. See structural_band_protocol.md for the
frozen45/40-second campaign and structural_band_results.md for all outcomes.
The generator/evaluation list is fixed in build_structural_band_study.py. Use the
four structural generation/run/audit/summary commands in INTERVENTION_BENCHMARK.md.
The elementary baseline is timed with recognition and replay, not a bare kernel.
`structural-artifact-reproduction.json` records the new clean-archive reconstruction;
the earlier80-artifact reconstruction remains explicitly historical evidence.
