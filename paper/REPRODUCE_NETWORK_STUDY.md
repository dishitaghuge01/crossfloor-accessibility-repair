# Reproduce the building-network / event-lifetime study

The current detailed master is paper/master.pdf. Start with
network_study_results.md. Its new study is separate from the earlier frozen
campaigns; the documentary/CAD report remains a separate supplement.

## Inputs and scope

Use source-code.zip (current clean source) and requirements-dev.lock.txt.
The network source inventories in evidence/building-network-source-inventories
are frozen derived IFC projections with original source URLs, SHA256 and
attribution. Reproduction from these inventories needs no licensed/private
CAD file or IFC download. Regenerating projections from original IFC is a
separate source-level step using public_building_controlled.py and the pinned
public_ifc_sources.json registry; source geometry/IFC engine versions matter.
Raw IFC/DWG/source PDFs are intentionally not redistributed.

All source room polygons and IDs remain frozen; candidate reservations, doors,
profiles, permissions and action prices are hypothetical. The fixed grid is
0.7m-square experimental equipment, not a certified lift design. The two
profile layers have identical route demands/permissions in this campaign.
Five catalogue layouts/15 price variants come from TWO source buildings.

## Regenerate the exact15 input variants

From the extracted source-code.zip directory:

```text
python scripts/build_building_network_study.py --audits path/to/evidence/building-network-source-inventories --output runs/new-network-data
```

Compare every generated input_fingerprint against the supplied dataset.json.
The source inventories preserve original rings/elevations and the derived
nonoverlap selection; exclusions and unreachable-demand omissions are explicit.
Original source hashes/attribution are included in each dataset record.
All15 inputs also have explicit nonoptimal feasible segment controls:

```text
python scripts/check_network_witnesses.py --instances runs/new-network-data/instances --output runs/new-network-summary/feasible-witnesses.json
```

For a single input, the new exact mode is available through the existing CLI:

```text
python -m cfar.cli solve-owned-interface INPUT.json --no-compression --release-dead-cells --release-dead-vertices --output runs/new-repair
```

## Recollect the primary70 observations

Commit local source first; the runner rejects a dirty tracked tree. Fresh
output directories are required. Performance measurements vary by machine.

```text
python scripts/run_network_study.py --instances runs/new-network-data/instances --output runs/new-network-evidence --repeats 3 --timeout 30 --methods uncompressed cells-uncompressed lifetime-compressed lifetime-uncompressed cp-sat greedy-improved --confirmatory
```

Seed0 has three lifetime-uncompressed and CP-SAT observations per layout;
other primary/control modes have one. Price seeds1/2 have one observation per
primary method. This yields70 observations, not90/270. Solver seed0 is
separate from the price-generator seed recorded in dataset.json.
Failures, caps, timeouts and partial incumbents must remain in the records.
The rotation of the six-method list does not reverse the primary DP/CP-SAT
relative order in these three repetitions; timings are descriptive.

## Matched larger-budget boundary check

The post-hoc extension retains the original30s failures for the largest clinic
case and runs both exact methods three times with90s parent deadlines. CP-SAT
gets75s internally; lifetime DP gets500000 raw states. This changes resources,
not the input/problem, and must not be pooled into the30s timing table.

```text
python scripts/run_network_budget_extension.py --source runs/new-network-data/instances/clinic-network-96-s0.json --output runs/new-network-extension
```

## Rebuild tables, figures and the detailed manuscript from saved measurements

No benchmark rerun is needed for this stage:

```text
python scripts/summarize_network_study.py --evidence path/to/evidence/building-network --dataset path/to/evidence/building-network-dataset --audits path/to/evidence/building-network-source-inventories --output runs/new-network-summary
python scripts/audit_network_extension.py --evidence path/to/evidence/building-network-budget-extension --output runs/new-network-summary/extension-summary.json
python scripts/build_network_master.py --base path/to/network-reproduction-base --summary runs/new-network-summary --extension runs/new-network-summary/extension-summary.json --output runs/new-network-paper
```

The summary audits every raw status/time/manifest and original room ring, and
independently rechecks paid rectangle costs/overlaps. Large optima use
cross-method agreement; the new transitions also have small exhaustive tests.
No large oracle claim is made. The preserved incomplete earlier clean campaign
is preliminary only and excluded from final measurements; no timing splicing.

Compile master.tex using Tectonic0.17 or a XeTeX-capable engine. Check embedded
fonts, references, page bounds and rendered layout. The supplied standalone
paper source ZIP compiles directly. network-reproduction-base/ is ONLY the
previous19-page main source used by the builder; the current main is at the
source ZIP root or research package paper/. Old reproduction guides refer
to their own frozen historical stages.

Core implementation validation:765 regression tests passed72.93s after the
final lifetime/geometry changes. Later reporting scripts do not change solver
semantics. Full raw manifests identify measured solver/source fingerprints;
release.json separately identifies the current archive commit and measurement
commit. Source-level priority and actual-building intervention validation
remain unconfirmed. No public push or submission is performed by these steps.
