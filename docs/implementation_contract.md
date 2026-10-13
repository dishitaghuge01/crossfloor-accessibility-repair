# Controlled implementation contract, version 0.1.0

14 October 2026. This implementation is the M01 reference oracle and verifier for controlled inputs. It is a strict subset of the eventual physical-repair problem. It requires no GPU, neural model, LLM, BIM extraction, or architecture expert.

## Input and identity

`spec/instance.schema.json` uses JSON Schema 2020-12 with closed objects and a fixed schema version. All coordinates are metres in a shared building coordinate system. Room IDs are building-wide unique. Floors have orthogonal simple polygons, frozen room polygons, declared shared-boundary adjacency, active door relations, obstacles, and reserved portal zones. Profiles specify experimental width, clear-patch size, stair capability and ramp slope; these values are not building-code thresholds.

The connection catalogue stores immutable endpoint, kind, physical-profile, geometric-template, and evidence-ID records. A catalogue record is evidence supplied by the instance author, not something the solver infers from a label. The `existing` flag alone is insufficient: selected relations must also pass recomputed geometric checks. Catalogue authentication against an IFC model or site survey is outside this version.

Baseline active relations must refer to existing evidenced connections and pass geometry/profile checks. Missing candidate relations may be infeasible; the oracle records those subsets as invalid. Malformed records, unknown IDs, contradictory action references, false representation corrections, and inconsistent declared A are rejected before search with named errors.

## Graphs and actions

- A is rebuilt from positive-length shared polygon boundaries. Point contact is not adjacency; positive-area overlap is invalid. Declared A must equal computed A.
- D contains active within-floor doors, separately from A.
- H_p contains only active connections permitted for profile p, including vertical transitions.
- A representation correction activates only existing, physically evidenced connections. It can restore a profile permission evidenced by the catalogue, but cannot invent a door, stair or lift.
- A physical intervention activates a supplied new geometric connection. Its input `geometry_certificate` declares the template/model scope; its actual certificate is recomputed from that template after selection. No supplied success boolean is trusted.
- Activation is monotone and idempotent, including overlapping bundles. Every selected action is still charged once, and every activation's profile permission must be supported by the physical record.
- Dependencies and exclusions are selected-set constraints, not execution order. A coupled action can contain multiple activations for one cost.
- SCFAR forbids all room-geometry replacements, preserving polygons, identities, and A. RCFAR permits explicitly declared polygon replacements on original IDs, checks final floor geometry, and charges lambda times the symmetric-difference adjacency count. Two replacements of the same floor conflict. Splits, merges and identity mappings beyond the identity are not implemented in either variant.

## Geometry model: reserved_interfaces_2d_v1

This model verifies an abstract straight connector/landing envelope, not an arbitrary constructible renovation. Input reserved portal zones assert that the necessary vertical opening/envelope already exists and may be used without creating a shaft or changing frozen rooms. The code checks the footprint against those supplied zones; it cannot independently establish slab openings from 2D polygons.

Doors need an axis-aligned opening wholly on the existing common wall, opening length equal to declared width, and two rectangular clear patches meeting the opening. Both patches must fit their endpoint rooms and avoid supplied obstacles. Profile width and clear-patch requirements must hold.

Vertical transitions require different floors, correct elevation difference, coincident rectangular footprints, footprint width, rectangular contained landings, obstacle avoidance, and existing reservation. Straight stairs and ramps additionally require the declared horizontal run to fit the long footprint dimension. Ramps must satisfy the profile slope; stairs require explicit profile capability. Lift vertical travel is abstracted by its endpoints. A shared asset ID means one aligned facility, not two competing assets; kind, width, profiles and footprint must agree across its transitions.

Selected distinct portal assets cannot overlap in positive area on a floor, and distinct door openings cannot overlap along a wall. Shared transitions of the same aligned asset may use the same footprint. Selected union geometry is checked, not just individual action geometry.

For required room/profile pairs, accessible centre-space is the room polygon eroded by half the profile width, minus obstacles expanded by the same amount using mitred orthogonal offsets. It must be a single positive-area Polygon; each active connection's landing centre must lie inside it. This assumes an axis-aligned square body and rejects disconnected room space conservatively. Portal envelopes are assumed to be traversable access/landing areas in the supplied model; opaque equipment solids, door-swing obstruction, headroom, stair tread/riser design, structural load, fire safety and actual lift operation are not modeled. Supporting those requires richer geometry and authenticated input evidence before any real-building feasibility claim.

GEOS uses floating point; checks use a fixed 1e-8 metre/area tolerance in the appropriate predicate. Boundary decisions therefore are reproducible under the recorded GEOS version but are not exact symbolic rational geometry proofs.

## Objective and certificate contract

SCFAR cost is the sum of selected action costs. RCFAR cost adds nonnegative lambda times Delta_A. Decimal arithmetic is used for the discrete objective after converting input numbers to their JSON decimal representation. Ties prefer fewer actions, then lexically sorted IDs. The oracle returns `optimal` or `infeasible` only after every subset is evaluated; the action guard raises ACTION_LIMIT before enumeration.

Four certificate sections remain separate:

1. Profile-valid room paths and exact computed adjacency comparisons under the identity map.
2. Recomputed connection-envelope, room-space, and joint geometry checks under the named model.
3. Complete-enumeration evidence, lower bound equal to the optimum, zero discrete gap, and a ledger fingerprint; infeasibility has no fabricated witness or finite optimum.
4. Original-restoration action agreement and, when a reference set is supplied, its independently replayed feasibility/cost. This measures action-set agreement, not recovered IFC geometry or BIM-design identity.

The checker independently materializes the selected set and rebuilds connectivity with union-find. It validates every supplied path against reconstructed profile edges and re-enumerates subsets to check optimality/infeasibility. It shares the schema and geometric predicate kernel with the solver; this is implementation independence for replay and graph checking, not an independently implemented geometry engine. Tests disable the solver, its replay entry point, and BFS while verifying a certificate. Full verification costs exponential time in k and is intended for the micro-oracle.

## Reproducibility and limits

The CLI writes a manifest with Git revision/dirty state, source and input fingerprints, seed, package/GEOS versions, machine, method settings, elapsed time and solver status. Results and the complete ledger are JSON/JSONL. All runtime output belongs in ignored `runs/`; checked-in fixtures under `examples/micro/` are hand-designed source inputs with manual expected answers, not downloaded BIM or generated experiment output.

The small structural solver in `dp_coverage.py` is available as a Python API. It accepts only the recognized contracted-star, one-profile, independent-correction class documented in the complexity memo. Its result is not a general bounded-interface certificate and must not be used as such. A 40-action test demonstrates bounded state count; it is not a preregistered scalability benchmark or evidence that G3 has passed.
