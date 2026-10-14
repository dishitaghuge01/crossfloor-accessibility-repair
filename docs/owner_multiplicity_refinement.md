# M14: per-cell ownership refinement and executable rank checks

## A sharper positive result

M09 gives each live cell g+2 states during a unit: empty, external, or one of all g internal owners. Most owners cannot occupy most cells. For unit J and cell c, let h(J,c) count distinct available owners of J whose complete union of available action footprints includes c. The only valid internal labels for c belong to this set. Consequently the resource-state bound in a window W is

`product_(c in W) (h(J,c)+2)`.

The two extra states remain empty and externally occupied. If h=max_(J,c) h(J,c), the in-unit resource bound is at most `(h+2)^(zL)`. The outside-unit bound remains `2^(zL)`. All connectivity, original-action accounting and owner-erasure arguments of M09 are unchanged. Its proposed total bound therefore sharpens to

`recognition_time + 2^O(prL + zL log(h+2)) * polynomial(input_bit_size)`.

This is a conditional refinement of the working theorem, not independent verification or an established literature novelty. h is measured per unit and cell, not across all competing units. Arbitrarily many private alternatives can share a cell while each of their units still has h=1. All owner identities needed for future reuse remain explicit in their permitted cells; no two distinct assets are renamed or merged.

The unit construction, support bound L and all physical recognition assumptions remain necessary. g is still returned as a descriptive measurement but need not appear separately in this refined exponent. Every available unit asset occupies at least one supported cell, so g<=zLh for nonempty units; that observation alone yields a much weaker generic width bound, not the logarithmic state dependence above.

For the authored atomic bundle and unused-paid-geometry cases, g=2 but h=1: their two internal owners occupy disjoint cells. At each such cell the owner map has three possible statuses, not four. This is a measured structural improvement, not observed compressed-solver state counts or a speedup benchmark. Broad unit actions can still have large L or z, and h need not be small in arbitrary inputs.

The recognizer now returns h, per-unit cell owner counts and an exact product upper bound for the known cells in that unit's look-ahead window. It retains all original action support and EPS/collision-equivalence checks. Cells with no possible current-unit owner still contribute two states for past occupancy.

## Executable product-profile rank validation

`src/cfar/representative_partitions.py` constructs anchored compatible-cut rows, tensors their profile rows, and greedily retains a minimum-label GF(2) basis. Callers must group by the same event, occupancy and selected boundary vertices. The reducer retains original history indices and never changes their witness labels.

This implements established rank-based ingredients, explicitly attributed to [Bodlaender/Cygan/Kratsch/Nederlof](https://pure.tue.nl/ws/portalfiles/portal/57608658/journaldeterministic_complete.pdf), section 3.6. The project contribution under development is their valid ownership/physical-action transfer and explicit parameterization, not the invention of row bases or tensor products.

Twenty-seven tests check single-profile cut factorization for every pair of partitions on 1–5 vertices, and minimum-label preservation for every completion in boundary families (4), (3,3), (2,2,2) and (1,3), across five fixed label seeds. Completion checking uses separate union-find on joined partitions and does not use cut rows or elimination. Additional tests reject mixed boundary dimensions and preserve the cheaper witness among duplicate rows. These are finite checks of the algebraic component; they do not test the whole floor-transition/compression theorem or establish originality.

## Newly resolved direct comparison

Cornet and Laforest's [2017 primary paper](https://dmtcs.episciences.org/4154/pdf), introduction and section 4, defines conflict-free Steiner selection on support vertices and conflict edges. Their Theorem 7 establishes hardness even with conflict stretch two and a matching conflict graph; its proof was inspected. Stretch measures support-graph distance, not floor-interface occupancy. Thus local conflicts alone are insufficient, and the candidate must retain its measured interface/unit assumptions. This source does not state the owned-cell repair bound being developed here. That scoped difference does not exclude an equivalent reduction or another prior algorithm.

The paper's selected support-vertex model cannot be used as a faithful atomic disconnected-bundle encoding merely by inserting one purchase vertex adjacent to every endpoint: such a vertex can create graph paths between disconnected supplied components. A cost-preserving reduction needs separate effect occurrences and shared selection constraints, while still retaining all paid physical occupancy. This is a concrete comparison obligation, not a claimed impossibility of reduction.

## Current novelty decision

The candidate has been strengthened rather than abandoned: exact physical recognition is executable, product-profile compression is separately checked, and per-cell owner multiplicity sharpens the proposed exponent. The direct resource-incidence baseline remains applicable; raw conflict density and reuse of rank machinery are not originality claims. A positive literature decision still requires a complete floor-transition implementation/proof check and a direct comparison with explicit constrained-resource connectivity algorithms. G3 remains OPEN; **novelty is not yet established**.
