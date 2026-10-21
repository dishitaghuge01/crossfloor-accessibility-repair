# Controlled cross-floor intervention benchmark

The artifact supports repeatable exact-optimization experiments. It is not a
collection of verified construction projects. Files retain explicit source,
catalogue, permission, conflict, price-seed, solver-seed and repetition identifiers.
Prices are abstract objective weights; a solver's feasible/optimal status is
relative to the represented intervention catalogue and checked2D geometry model.

## Populations and intended uses

| Dataset | Files | Use and independence boundary |
|---|---:|---|
| Joint building-derived tiers |15| Five catalogue layouts/two licensed source buildings; three coupled interaction tiers, fixed price seed. Reservations, permissions and costs hypothetical. |
| Structural families |23| Eight authored families with per-family fixed/varied/coupled metadata; not independent building observations. |
| Original event-order followup |2| Same authored graph and geometry, renamed action event order. |
| Permission-only matched pair |2| One identical Clinic catalogue; only alternative-purchase permissions differ. Restricted input duplicates an existing joint-tier input. |
| Local bands |9| Three authored sizes, three price seeds each. Adjacent-band physical conflicts, bundles and profile-specific routes. |
| Private bays |4| Four authored sizes; a tractability/state-space separating witness, not a difficult application validation. |

These are55 instance files, not55 independent geometries or buildings. A content
manifest gives canonical instance fingerprints and duplicate counts.

## Reproduce

Extract the accompanying source archive into a source directory and install the
locked requirements from its README. All commands below run there. The benchmark
ZIP also contains the machine-readable inputs and their dataset metadata. No raw
IFC, DWG, licensed article PDF or private source extract is included.

```powershell
python scripts/build_local_band_study.py --output NEW_LOCAL_INPUTS --sizes 8 24 48 --seeds 0 1 2
python scripts/build_private_bay_study.py --output NEW_BAY_INPUTS --sizes 2 8 16 32
python scripts/event_frontier_certificate.py INPUT.json NEW_CERTIFICATE.json
python scripts/local_band_reference.py LOCAL_BAND_INPUT.json NEW_REFERENCE.json
python scripts/run_frontier_scaling.py --dataset NEW_LOCAL_INPUTS --output NEW_LOCAL_RUNS
python scripts/run_frontier_scaling.py --dataset NEW_BAY_INPUTS --output NEW_BAY_RUNS --private-bays
```

The main research package supplies saved raw runs, manifests, event traces,
full-replay audits, static certificates and independent family-reference ledgers.
Fresh runs require clean source; method order and schedules are persisted before
solving. All outcome rows, including caps and unfinished objectives, are retained.
No RAM cap is imposed. New local/bay campaigns use90s external/85s CP budgets,
different from the earlier60s primary and30s parameter campaigns; never pool their
wall-time denominators. Source/input/kernel hashes support inspection independently
of machine-dependent timings.

## Static certificates and independent validation

`b` counts potential profile vertices including anchors and eager targets, through
transient action branching. `max_resource_domain_product` is a conservative
simultaneous domain product through complete-unit closure. These differ from
post-solve selected-state counts. The local-band reference is restricted to its
admitted fixed rectangles and chain catalogue; it independently enumerates local
purchase subsets and propagates three-slot masks. It is not a general BIM or
physical repair validator. Private bays additionally have a closed-form full-label
optimum. All returned general-solver repairs are separately replayed.

## Domain-evidence admission boundary

| Evidence | Current status |
|---|---|
| Frozen geometry/provenance | Available for building-derived cases; public-source attribution retained. Authored family coordinates are generated. |
| Spatial admissibility | Checked against the declared reserved2D kernel; complete paid effects retained. |
| Actual reservation availability and asset ownership | Hypothetical experimental annotations; no authenticated site/design reservation evidence. |
| Actual profile permissions and access policy | Experimental profiles/permissions; not an accessibility certification. |
| Structural/MEP/headroom/fire/capacity suitability | Outside the represented kernel; not verified. |
| Construction intervention catalogue and prices | Abstract authored choices and costs; not quotations or verified actual alternatives. |
| Qualified domain acceptance or observed retrofit outcome | Not supplied or inferred. |

The reusable benchmark and computational validation do not close actual-building
validation. Admitting a verified application requires source-linked existing and
proposed geometry, authenticated candidate availability/permissions and complete
intervention definitions; if monetary utility is claimed, comparable dated cost
evidence is additionally required. Missing fields must remain explicitly unknown,
not filled with generated assumptions and relabelled as facts.

Source license/attribution notices remain in dataset metadata and source docs.
This artifact does not grant additional rights to third-party drawings or adopt
a new project license on the authors' behalf.
