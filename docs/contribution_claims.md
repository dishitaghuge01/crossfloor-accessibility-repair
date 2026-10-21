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
| C5 | A tighter event-interface runtime and separating family are proved | needs_new_experiment | Requires derivation from actual enumeration/reduction, and formal family; current floor bound remains authoritative |
| C6 | Combined lifetime DP completes the 78-purchase seed-zero Clinic case in three trials within the 30-second deadline | supported | `evidence/building-network/records.json`, revision f1e5d18; median function 13.129 s, full exact objective |
| C7 | CP-SAT fails to prove minimum cost on that case | needs_new_experiment | Historical parent timeout discards stage trace; cannot infer the failed stage |
| C8 | Lifetime DP is generally faster or stronger than CP-SAT | remove | Across 15 network price variants DP completes 6 and CP-SAT 8; old compressed DP slower on all 15 seeded connectivity inputs |
| C9 | Representative reduction improves practical runtime | remove | Existing measurements do not support this |
| C10 | Network suite validates simultaneous owner competition and profile heterogeneity at building scale | needs_new_experiment | Current layouts use disjoint owner patches and identical route permissions/demands |
| C11 | Network suite contains 15 independent building layouts | remove | Two source buildings, five catalogue layouts, three price seeds per layout |
| C12 | All 15 network inputs have feasible repairs | supported | `scripts/check_network_witnesses.py`, frozen `feasible-witnesses.json`; constructive controls, not additional timed observations |
| C13 | Larger Clinic case is solved optimally | remove | Separate six-run extension: CP-SAT feasible cost 470, bound 335; DP times out; no optimum proof |
| C14 | Intervention assumptions and abstract costs are verified construction facts | remove | Building-derived controlled experiments only; no verified intervention dataset |
| C15 | Frozen release has 2362 timed observations | supported | `experiments/campaign_registry.csv`; 1918+176+180+12+70+6, six distinct revisions/campaigns |
| C16 | Frozen solver passed 765 tests | supported | Recorded final f1e5d18 checkpoint in `docs/event_lifetime_correctness.md`; not a test result for future changes |
| C17 | Vertices-only ablation isolates the observed gain | needs_new_experiment | Missing in historical core campaign |
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
