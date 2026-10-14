# M11: constructive resource-incidence baseline and exact objective transfer

14 October 2026. This completes a concrete generic baseline for the active M09/M10 candidate. It does not settle originality or close the physical-interface direction.

## Compact encoding of the recognized repair class

After M09/M10 recognition, use object types Action, Asset, Cell, Vertex and EdgeOccurrence. Vertex objects are separate profile-layer baseline components, with a permanent anchor per layer and marked required targets. Asset objects denote only candidate new installations; authenticated fixed background has already been checked and is not a selected resource. Cell objects retain their floor identity.

Relations are binary: Uses(action,asset), Occupies(asset,cell), Supplies(action,edgeOccurrence), and Endpoint(edgeOccurrence,vertex). Mark baseline edge occurrences separately. Every supplied occurrence belongs to exactly one original action, even if other actions activate the same connection. Parallel occurrences have the same endpoints and do not change undirected reachability. An original action supplying many edges still has one selected Action object and one cost.

This duplication is essential for a local decomposition: one canonical edge object shared by arbitrarily many units could otherwise remain live unnecessarily between its first and last supplying action. The encoded size remains polynomial in explicit input effects. Graph loops can be omitted after recognition; full original interventions remain materialized during replay.

Let X be selected Action objects. An Asset is selected iff some member of X Uses it. An occurrence is active iff it is Baseline or supplied by a member of X. Require:

1. At each Cell, at most one distinct selected Asset Occupies it. Multiple selected actions using the same Asset are allowed.
2. Every required target reaches its own profile anchor through active occurrences. Express reachability by the usual universal vertex-set cut condition.

Targets can be linked to their layer's anchor by a binary RootTarget relation; these relations do not allow profile switching. All recognition failures, background collisions and unavailable actions have already been removed or rejected. Dependencies, arbitrary exclusions and geometry beyond the exact cell kernel remain outside this class.

These are fixed monadic second-order conditions, independent of action count, asset count, profile count or number of targets. Geometry equivalence and asset identity consistency are preprocessing obligations, not assumptions made true by the formula. This encoding is the project's explicit reduction to established bounded-width machinery.

## Constructive path decomposition

Keep the current L-floor look-ahead window: at most prL access vertices and zL collision cells, plus p permanent anchors. Process units in M09 order. During one installation unit, keep its at most g Asset objects throughout all its original action events. Introduce one Action object, then process its Uses relations and its EdgeOccurrence objects one at a time. For an occurrence, both endpoints and its unique supplying action are already in the bag; introduce it, expose its relations, then forget it. After all its occurrences, forget the Action. Process an Asset's Occupies relations while that Asset and all its cells are present. Forget all unit assets only when the unit is complete.

Corrections have no Uses relations and need no Asset objects: their evidence was checked against fixed background. Process their action/occurrences identically. Process baseline occurrences one at a time. Expose each RootTarget relation while its target is in the window and its anchor remains permanently present. Shift floors after all incident events have finished, exactly as in M09.

Every binary relation is covered by a bag; every object's bags are consecutive. Unit support bounded by L puts all its asset cells and action endpoints in the window. Distinct units have disjoint Asset objects, so no forgotten Asset must be reintroduced. EdgeOccurrence duplication avoids nonconsecutive shared-edge lifetimes. Thus the Gaifman graph has a supplied path decomposition with bag size at most

`prL + zL + p + g + 2`.

Its width is at most that quantity minus one. This is a project construction, not a theorem quoted from the literature. Unlike the earlier raw pair-conflict encoding, it has no catalogue-sized clique from many alternative assets sharing a cell.

## Weighted optimization and exact tie-breaking

Courcelle and Mosbah's primary paper, sections 4.7–4.8 (printed pp. 75–77), treats weighted minimization and linear extrema on bounded-treewidth inputs with a supplied decomposition, under a uniform-cost arithmetic convention. Section 3.5 also notes that the auxiliary formula construction can be very large. This provides a general optimization baseline, not the explicit M09 running-time bound. [Author-hosted paper](https://www.labri.fr/perso/courcell/Textes1/BC-Mosbah%281993%29.pdf).

Transfer the repository's cost/count/sorted-ID objective to a single nonnegative integer weight as follows. Sort the K available original IDs, indexed i=1,...,K. Scale rational costs to integers C_i using the product of their positive denominators. This scaling has polynomial bit length; it does not assert small numeric magnitude. For K>=1, put

`Q = K * 2^K + 1`

`w_i = C_i * (K+1) * Q + Q + (2^K - 2^(K-i))`.

For any selected set X, the last term's sum is nonnegative and smaller than Q. Thus a one-unit count difference dominates every possible last-term difference. The entire count-plus-last-term range is smaller than (K+1)Q, so a one-unit scaled-cost difference dominates all lower-priority differences. At equal count, minimizing the last term maximizes the selected binary ID score. At the first differing ID, inclusion of the smaller ID outweighs all later IDs, exactly matching sorted-ID lexical order for equal-size sets. K=0 is trivial.

Consequently minimizing sum of w_i over selected Action objects preserves cost, then count, then the complete lexical witness. Every original action is charged once, regardless of its asset or edge occurrences. Weight bit length is polynomial in input bit size, including the K binary tie bits. Recover a selected optimum by witness reconstruction, or by sequentially constraining each action to test whether the optimum scalar value remains attainable; the latter makes only polynomially many calls and needs no input-wide ordering relation that could inflate width.

The source's arithmetic-operation bound is not automatically a bit-time claim. Here additions/comparisons of these weights have polynomial bit complexity. This yields a generic bound of the form `f(width,formula) * polynomial(input_bit_size)` with a supplied decomposition; no single-exponential expression for f is inferred from that source.

## Precise comparison with the active contribution

| Question | Concrete generic baseline | M09/M10 proposed explicit construction |
| --- | --- | --- |
| Same-asset reuse and complete action bundles | Selected Asset predicates and one Action weight | Local owner maps and original labels |
| High alternative density in a footprint | Asset–Cell incidences avoid conflict cliques | Occupied cells avoid catalogue-sized history keys |
| Local width/parameter | Width at most prL+zL+p+g+1 | Exponent O(prL+zL log(g+2)) |
| Connectivity dependence | Unspecified formula/width function here | Product-profile representative rows, at most 3^(prL) per resource map |
| Existing assets with missing permissions | Fixed background checked before encoding | M10 correction events with no new ownership |
| Geometry and evidence | Requires the same exact preprocessing contract | Physical recognition and complete-action replay are explicit |

This construction means that conflict-clique separation alone cannot distinguish the candidate from a compact generic resource model. It also gives a stronger baseline to develop against: the contribution target is the explicit owner/cell state dependence and its physical recognition/typed-action transfer, rather than the existence of some FPT algorithm.

The baseline's linear g in a width upper bound does **not** prove that every existing explicit algorithm has exponential g dependence or cannot match M09. A width upper bound is not a lower bound. Direct resource-capacity and rank-based algorithms may improve it. Establishing a strict algorithmic advantage requires comparing their actual state spaces and bounds under the same input contract. The M09 working proof remains active, with that precise comparison and independent semantic validation still pending.

## Validation status

The encoding, decomposition and scalar objective were checked by algebra and relation/lifetime inspection in this research pass. These are self-checks, not independent review or experiments. No new solver or test run is reported. Originality remains provisional and G3 stays OPEN. Next substantiate the shared-asset and partial-footprint scenarios with complete authored inputs, while auditing direct resource/connectivity bounds rather than broad keyword matches.
