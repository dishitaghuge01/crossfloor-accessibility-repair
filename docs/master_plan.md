# Cross-Floor Accessibility Repair: master development plan

Updated 13 October 2026. This document is the operational source of truth.

## 1. Thesis question and claim boundary

### Active question

Given frozen, individually valid floor plans and profile-specific cross-floor access obligations, can a solver find a minimum-disruption combination of representation corrections and physically feasible portal or local-access edits that restores all obligations while preserving each floor's original room-adjacency topology?

### Eventual claim boundary

Only after all gates pass, the project may claim a formal repair problem, verified implementation, and an algorithmic result for a defined class. It may not claim first multi-floor generation, general code compliance, physical safety, or optimality without an exact proof or certified solver bound.

## 2. Formal model

### 2.1 Instance schema

Each derived instance is one JSON document in data/derived/instances/<id>.json.

Required top-level fields:

- schema_version: string
- building_id: string
- floors: floor records
- portals: portal records
- obligations: source-target-profile records
- actions: typed candidate edit records

A floor record contains floor_id, elevation_m, rooms, adjacency_edges, and access_edges. A room has room_id, label, and an orthogonal polygon in metres in a shared building coordinate system. An access edge has edge_id, endpoints, kind, and permitted mobility profiles.

A portal has portal_id, kind, a footprint or named footprint reference per participating floor, and permitted profiles. An obligation has id, source room, target room, and profile.

Every action has action_id, type, cost, and action-specific evidence.

### 2.2 Graph definitions

- A_i^0 is the undirected original room-adjacency graph on floor i. An edge means identified original rooms share a boundary.
- D_i^0 is the traversable-access graph. An edge means a valid door, corridor, or opening exists for one or more profiles.
- H_p is the building-wide profile graph formed from permitted D_i edges and certified portal transitions.
- mu_i maps original rooms to post-repair rooms. In strict repair it must be identity.

### 2.3 Typed actions

A representation_correction restores a missing or erroneous model relation for a physically evidenced connection. It must include evidence_id and may not alter geometry.

A physical_intervention changes a door, connector, portal, or footprint. It must include a geometry_certificate with containment, clearance, non-overlap, endpoint, and profile checks. Metadata alone can never satisfy a physical obligation.

## 3. Two distinct optimization problems

### Strict Cross-Floor Accessibility Repair (SCFAR)

Minimize sum of selected action costs subject to:

1. every obligation has a path in H_p;
2. every physical action is geometrically feasible;
3. A_i(R) equals A_i^0 for every floor i;
4. mu_i is identity.

A door through an existing shared wall may change D_i without changing A_i. Corridors, shafts, room splits, and room merges are forbidden.

### Relaxed Cross-Floor Accessibility Repair (RCFAR)

Allow declared topology-changing actions and minimize:

representation_cost + physical_cost + lambda times Delta_A.

Delta_A is the symmetric-difference distance between original and repaired adjacency graphs under mu_i. Strict and relaxed results must never be mixed.

## 4. Evidence contract

Each solver output must include four separate records:

1. reachability and preservation verification: one profile-valid path per obligation plus exact adjacency equality checks;
2. geometric candidate feasibility: an action-level certificate under a stated geometry model;
3. optimality evidence: exact optimum, theorem bound, or lower bound plus optimality gap;
4. recovery evidence: agreement with original BIM restoration, explicitly separate because the original need not be optimal.

## 5. Research gates

### G0 - closest-work boundary

13 October 2026 checkpoint: see [closest-work matrix](closest_work_matrix.md). G0 remains OPEN. The Al-Harasis/Jabi DFBI method has been inspected and distinguishes evaluation-only graph completion from physically realized repair. Overall separation is unestablished pending full-text gaps, including the same-title eCAADe version. MANSION task editing must be compared alongside its generation pipeline. Restricted independent single-profile edge repair must be tested against existing Steiner-forest/network-design formulations before claiming algorithmic novelty.

Compare full methods against MANSION, EPSAP, PlanFix, Al-Harasis and Jabi graph repair, BIM cross-level analysis, connectivity augmentation, Steiner-network, and graph-repair theory.

Pass condition: no prior work solves frozen-layout, typed-intervention, cross-floor, minimum-disruption repair with equivalent guarantees.

### G1 - model validity

Create spec/instance.schema.json, spec/enums.json, and 12 hand-built micro-instances. Implement schema, action-evidence, geometry, and topology validation.

Pass condition: invalid inputs fail with named errors and expected strict/relaxed repairs match manual ground truth.

### G2 - complexity map

Study one portal chain, tree-shaped floor access, bounded cross-floor interface size b, number of floors f, and action count k.

Pass condition: a written proposition with assumptions, proof, and counterexample outside scope. Enumeration over 2^k is the oracle, not the thesis theorem.

### G3 - structural algorithm

Develop dynamic programming over bounded portal interfaces. A state stores interface-terminal connectivity partitions, selected coupled portal actions, and cost.

Pass condition: exact oracle agreement on all small cases and better scaling than enumeration on a preregistered synthetic family. An alternative pass is a hardness boundary plus a principled approximation or parameterized algorithm.

### G4 - public data

Use only licensed multi-storey IFC/BIM sources. Extract storeys, rooms, access edges, portals, and footprints. Verify original paths under every profile before corruption. Split by original building before generating corruptions.

### G5 - evaluation

Compare enumeration, CP-SAT or MILP, greedy local repair, and an ablation that disables coupled portal edits.

Report obligation recall, strict topology validity, geometry validity, repair cost, exact optimum or gap, runtime, and recovery match separately.

### G6 - paper

Proceed only if G0-G5 yield a nontrivial theorem, hardness boundary, or validated structural algorithm.

## 6. Software architecture

- src/cfar/schema.py: typed models, load_instance
- src/cfar/validation.py: validate_instance, validate_action_evidence
- src/cfar/geometry.py: polygons_touch, portal_feasible, connector_feasible
- src/cfar/graphs.py: build_adjacency_graph, build_access_graph, build_profile_graph
- src/cfar/obligations.py: verify_obligations, shortest_profile_path
- src/cfar/actions.py: apply_actions, classify_action
- src/cfar/objective.py: strict_cost, relaxed_cost, adjacency_delta
- src/cfar/oracle.py: enumerate_action_subsets, exact_oracle
- src/cfar/dp_interface.py: interface_signature, solve_bounded_interface
- src/cfar/corruptions.py: corrupt_portal_link, corrupt_connector, corrupt_profile
- src/cfar/certificates.py: make_certificate, verify_certificate
- src/cfar/io.py: manifest and JSON I/O

All functions are deterministic and typed. apply_actions never mutates input. verify_certificate rebuilds the graph independently.

## 7. First implementation backlog

1. Create schema and controlled vocabularies.
2. Add examples for strict and relaxed repair.
3. Implement loading and validation.
4. Implement A_i, D_i, and H_p construction.
5. Implement profile-aware BFS or Dijkstra obligation verification.
6. Implement typed action application and strict topology equality.
7. Implement enumeration oracle with complete result ledger.
8. Add twelve micro-instances: missing metadata, missing door, disconnected stair, incompatible lift, impossible footprint, coupled portals, strict versus relaxed, and original-not-optimal.
9. Write G2 memo before advanced algorithm code.

## 8. Reproducibility

Raw inputs stay in ignored data/external. Every run stores Git revision, Python and package versions, random seed, machine details, input fingerprints, method settings, timeout, and solver status in runs/<id>/manifest.json. Results are JSON Lines records. Never split corruptions from the same original building across train and test.

## 9. Paper structure

1. Failure mode and motivation.
2. Strict and relaxed definitions.
3. Complexity map and algorithmic result.
4. Certificates and implementation.
5. Controlled benchmark construction.
6. Baselines and evaluation.
7. Limits: geometry assumptions, extraction errors, and no safety or code claim.

## 10. Immediate milestone

M01 completes only after G0 has a full-text comparison matrix and G1 has the schema, twelve instances, validator, oracle, and tests. Do not begin neural generation or LLM work before M01.
