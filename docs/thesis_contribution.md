# Working thesis contribution and development decision

## Contribution statement to use now

This thesis develops and evaluates exact strict cross-floor accessibility repair with frozen rooms and adjacency, geometric asset ownership and indivisible action costs. Its specific algorithmic contribution under development is an owned-cell floor-interface dynamic program that preserves complete physical interventions while compressing profile-specific route witnesses. Under the recognized rooted, rectangular, independent-activation model, its proposed complexity is

`recognition_time + 2^O(prL + zL log(h+2)) * polynomial(input_bit_size)`.

Here p counts profiles, r bounds retained within-floor baseline components per profile, z bounds collision cells per floor, L bounds complete asset-unit and baseline-edge floor spans, and h bounds the possible owners of one cell inside one unit. These are measured model parameters, not guaranteed small for all buildings.

The physical recognizer, solver, action replay and reproducible comparisons are implemented. The contribution includes exact original-action cost/count/ID accounting, same-asset reuse, partial-footprint compatibility, atomic multi-asset purchases, and separate profile reachability. It uses established representative-partition machinery with attribution.

This is the **working contribution**, not an assertion of first-ever repair, invention of rank-based DP, or established literature originality. That distinction must stay in thesis drafts and presentations until the remaining precise equivalent-method question is settled.

## Necessary evidence: current status

| Check | Evidence and outcome |
| --- | --- |
| Precise model and sufficient state | M09/M14 proof and M15 implemented transitions; full geometry never shortened to the route witness. |
| Solver correctness on controlled inputs | 616 regression tests; clean M16 comparison covers 50 cases and 1,306 selections with oracle/certificate replay and a separate resource-logic evaluator. |
| Larger catalogue behavior | Dense64 has an analytical cost-one optimum and five peak raw states; this is a scoped example, not a broad performance claim. |
| Closest explicit weighted baseline | M16 gives a cost-preserving owner–cell usage encoding and transferred published bound with linear h in its exponent, versus the proposed logarithmic h term. |
| Literature originality | Provisional: a better generic encoding or equivalent constrained-resource algorithm has not been excluded. Do not claim a universal lower bound or guaranteed priority. |

The implemented method supports independent physical portal actions, rooted obligations and the fixed 2D kernel. It does not yet support candidate doors, dependencies or the proposed independent-background correction extension. Public-building evaluation and complete construction geometry are separate work.

## Decision: proceed with the project

The user has explicitly asked to minimize further novelty-only work and proceed with development. Freeze the working claim above and stop broad speculative literature searches. Keep G3 OPEN for the bounded originality question; that status does not prevent authorized demo and controlled evaluation work. Do not silently convert implementation permission into a positive originality decision.

Next deliverables are a one-command verified demo, controlled benchmark summaries using the frozen algorithms/parameters, and then the input/evidence workflow needed for real building cases. Reuse existing checkpoints. Run targeted checks for each change; rerun broad regressions only for material solver/geometry changes. Revisit the claim if new evidence identifies an equivalent result or exposes a correctness/scope failure.

Evidence: [solver and checkpoint](owned_interface_solver.md), [closest modern comparison](modern_connectivity_comparison.md), [claim registry](novelty_claim_registry.md). No new theorem or originality declaration is made by this development decision.
