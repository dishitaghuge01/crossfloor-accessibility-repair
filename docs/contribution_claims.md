# Canonical contribution and evidence map

Revision programme opened 21 October 2026. Status describes evidence, not priority.
Historical numerical claims refer exclusively to the frozen release identified in
`experiments/freeze-2026-10-21.json`. Campaign paths below are inside its research
package. New results must receive new campaign identifiers.

| ID | Claim | Status | Exact evidence / remaining requirement |
|---|---|---|---|
| C1 | Exact owned-interface construction preserves whole purchases while using profile-specific route witnesses | supported | `docs/owned_interface_solver.md`, `docs/asset_unit_interface_theorem.md`, implemented solver and replay; conditional on recognized strict model |
| C2 | Construction has established literature priority | needs_literature_comparison | `docs/novelty_claim_registry.md`; compare full formulations, not title similarity |
| C3 | Last-incident vertex and complete-unit cell retirement preserve feasibility and cost/count/ID labels | supported | `docs/event_lifetime_correctness.md`, `tests/test_cell_lifetime.py`; explicit schedule exposition still required |
| C4 | Last-use forgetting itself is new | remove | Standard sufficient-state forgetting; no priority evidence |
| C5 | A tighter event-interface runtime and separating family are proved | remove | Investigation retains the existing floor theorem; potential/transient widths and eager targets prevent substituting observed row width. See event_schedule_specification.md |
| C6 | Combined lifetime DP completes the 78-purchase seed-zero Clinic case in three trials within the 30-second deadline | supported | `evidence/building-network/records.json`, revision f1e5d18; median function 13.129 s, full exact objective |
| C7 | CP-SAT fails to prove minimum cost on that case | remove | Clean strengthened diagnostic aad70e4 proves cost 267 in 3/3; full objective completes 1/3. Historical erased stages remain unknown. See cp_stage_diagnostic_results.md |
| C8 | Lifetime DP is generally faster or stronger than CP-SAT | remove | Across 15 network price variants DP completes 6 and CP-SAT 8; old compressed DP slower on all 15 seeded connectivity inputs |
| C9 | Representative reduction improves practical runtime | remove | Existing measurements do not support this |
| C10 | Joint building-derived inputs exercise owner conflicts and nonnested profile demands | supported | Clean ce71e6a primary campaign:112 runs, five layouts/two source buildings, Clinic full tier reaches262 actions/103 destinations/168 conflict pairs; Molio36 has226 conflict pairs. Controlled assumptions, not construction validation |
| C11 | Network suite contains 15 independent building layouts | remove | Two source buildings, five catalogue layouts, three price seeds per layout |
| C12 | All 15 network inputs have feasible repairs | supported | `scripts/check_network_witnesses.py`, frozen `feasible-witnesses.json`; constructive controls, not additional timed observations |
| C13 | Larger Clinic case is solved optimally | remove | Separate six-run extension: CP-SAT feasible cost 470, bound 335; DP times out; no optimum proof |
| C14 | Intervention assumptions and abstract costs are verified construction facts | remove | Building-derived controlled experiments only; no verified intervention dataset |
| C15 | Frozen release has 2362 timed observations | supported | `experiments/campaign_registry.csv`; 1918+176+180+12+70+6, six distinct revisions/campaigns |
| C16 | Frozen solver passed 765 tests | supported | Recorded final f1e5d18 checkpoint in `docs/event_lifetime_correctness.md`; not a test result for future changes |
| C17 | Five same-revision ablations isolate retirement effects | supported | ce71e6a: both rules complete4/14; floor/cell-only/vertex-only0/14. One full-interaction input and one connectivity input rescued in both repetitions; no broad CP advantage |
| C18 | Heuristic failure implies no feasible construction | remove | Known all-segment controls exist; timeout loses incumbents in historical runner |

Working scientific statement: We construct an exact owned-interface algorithm
for bundled, profile-dependent connectivity repair with physical ownership
constraints, and establish safe event-lifetime projection preserving the original
optimization objective. This is a supported construction statement; the claim
of an original complete construction remains under focused comparison.

The next manuscript must have at most three contributions: construction and its
guarantee; model-specific asynchronous projection; reproducible evaluation with
bounded findings. Tests, schema, caching and historical surveys are supporting
artifacts. No broad practical or priority claim is currently authorized by evidence.

## New primary numerical claims

| ID | Statement | Status | Source |
|---|---|---|---|
| N1 | Primary112 observations; CP11/14 exact and14/14 verified feasible; cold greedy6/14 feasible; segment control14/14 feasible | supported | runs/joint-network-summary-2026-10-21/summary.json, complete ce71e6a schedule and per-run manifests;17 distinct returned selections reaudited |
| N2 | CP cost/count proved12/14; full objective11/14 | supported | Flushed stage traces, same summary cp_tasks; two Clinic96 cost-stage limits and one Molio36 identifier-stage deadline |
| N3 | Large Clinic feasible385, lower bound258 in both repetitions; optimum unproved | supported | Primary Clinic96 traces plus post-deadline parent audit; recovered candidate is not a completed pipeline |
| N4 | Final solver regression785 passed | supported | Full suite107.82s after asynchronous fixture/zero-cost tie and profiling checks; numerical test count is supporting QA, not a research contribution |
| N5 | Structural eight-family campaign results | supported | Clean3011e30:23 inputs,276 observations; all six exact methods46/46 optimal, identical complete labels;23 distinct selections replayed |

## Theorem and historical numerical trace

| ID | Manuscript statement | Status | Supporting artifact |
|---|---|---|---|
| T1 | Exact recognized construction and floor-interface bit bound | supported | Main conditional theorem and Appendix A; representative reduction is required for the single-exponential connectivity bound; uncompressed exactness does not inherit that time bound |
| T2 | Safe marked-component preprocessing, including eleven-to-one probe | supported | authoritative implementation/test: src/cfar/interface_recognition.py and tests/test_interface_pruning.py |
| T3 | Two-floor bundle hardness boundary | supported | Main reduction proof, src/cfar/physical_set_cover.py and tests/test_physical_set_cover.py; inherited classical hardness, not a new reduction technique |
| N6 | Historical15 seeded inputs favor uncompressed over compressed; CP completes4 natural compressed-cap inputs | supported | Frozen controlled campaign25aa069c, evidence/controlled/records.json and archived paper/scripts; not pooled with current campaign |
| N7 | Historical larger-budget CP incumbent470/bound335, no proof | supported | Frozen six-run network extension7c2a3b2, evidence/building-network-budget-extension/records.json |
| N8 | Current medium Clinic optimum209 selects13 restricted alternatives | supported | ce71e6a primary CP result; plotted directly from complete selected IDs by summarize_joint_network_study.py |
| N9 | Seven relevant-S feasibility controls | supported | runs/relevant-segment-controls-2026-10-21/controls.json and clean be2446a manifests; untimed, not optima or construction validation |
