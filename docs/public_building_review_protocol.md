# Public IFC controlled-subset protocol

This protocol expands source screening and independent optimization evidence.
It does not turn source IFC files into validated building-wide renovations.

## Sources and sampling

The pinned catalogue is `public_ifc_sources.json`, with source URLs, original
attribution, revision, licence notice and SHA256. The first screen included
Duplex, Clinic, Esplanades and Schependomlaan. After two failed eligibility,
Molio was added as a disclosed feasibility follow-up, not a preregistered sample.
All five outcomes must be reported. Root CC BY 4.0 and each folder notice are
recorded; Schependomlaan additionally specifies scientific/academic use.
Source bytes, projections, audits and runs stay outside Git.

## Admission contract

Use IfcOpenShell world-coordinate meshes in metres. Retain every source space
inventory and geometry exclusion. Admit simple, hole-free XY polygons accepted
by the existing orthogonal kernel. Preserve their exact projected rings and
GlobalIds; do not straighten or resize them to force admission. Audit every stair
and transport element. An unmapped physical background prevents admission.
The conservative XY envelopes of all such assets remain obstacles on both
experimental floors, including assets outside the chosen subset.

Rank different-storey room pairs by decreasing common projected area, then
GlobalIds. Use the first pair that passes recognition, square-body room access,
background checks and two fixed-grid, aligned 0.7m lift patches. Grid spacing is
0.8m. Record earlier pair rejections. This is a deterministic feasibility rule,
not selection by solver runtime, optimum or learned quality.

Only two rooms enter each controlled instance. Per-floor adjacency is empty
and remains empty; this does not test nontrivial whole-floor preservation.
Storey and space counts in the inventory must not be presented as solver input
size. The enclosing domain, reservations, profiles, prices and proposed lifts
are declared experimental annotations. No actual source portal is asserted.

## Reference and corruptions

Two square profiles (width/clearance 0.4m and 0.5m) have no stair capability.
Action D enables both profile routes on one supplied lift and costs four.
Materialize it as a hypothetical feasible reference, saving its active graph,
geometry checks and independently evaluated obligation paths. The corrupted
baseline has those activations removed while source polygons stay unchanged.
This supplies known finite-model feasibility, not original IFC accessibility
truth; D is not necessarily optimal.

Four catalogues are deterministic: bundle A buys two profile-specific portal
effects for three; B/C buy each separately for two; D buys one both-profile effect
for four. The separate variant raises A to five and removes D; the infeasible
variant retains only B; the single variant retains only D. Recognition checks
every emitted input. Every variant belongs to its source building; four variants
do not count as four independent buildings.

## Commands

Install the optional IFC dependencies from `requirements-ifc.lock.txt` and the
package with `.[test,optimization]`.

```bash
python scripts/download_public_buildings.py
python scripts/public_building_controlled.py --sources data/external/public-buildings --output data/derived/public-review
python scripts/run_optimization_benchmark.py --instances data/derived/public-review/instances --output runs/public-review
```

Run the measurement command from a clean revision. Each measurement records
input fingerprints, seed zero, environment, source code hashes, solver settings
and status. Run compressed/uncompressed DP and CP-SAT three times, greedy once,
and the exhaustive oracle once per eligible case. Public BIM tests are optional
integration checks; raw models are never test fixtures committed to Git.

## Remaining breadth gate

Several admitted sources improve geometry provenance breadth, but the current
protocol still has one room per selected floor and authored portals. Full
multi-storey extraction with evidenced original doors/vertical links, multiple
room obligations and nontrivial adjacency preservation remains a separate
research deliverable. This limitation must appear in the manuscript. A rejection
cannot be excluded by either this experiment or polished wording.
