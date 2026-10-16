# Supported contribution boundary and proof map

## Precise positive claim

The project establishes a semantics-preserving transfer from its recognized
physical action catalogue to an owned-cell floor interface, and evaluates that
specialized algorithm. It does not claim that shared-cost connectivity,
resource states, weighted bases or general exact optimization are new. The
positive result is the construction and its full-action/thin-witness proof
under explicit assumptions. Priority of an equivalent construction is not
established. This is a precise supported boundary, not an absence assertion.

| Comparator | Input / purchase | Compatibility / demands | Decomposition and objective | Expressibility / applicable algorithm / same dependence |
| --- | --- | --- | --- | --- |
| Weighted labelled connectivity (Hassin–Monnot–Segev) | Graph edges sharing paid labels | Labelled connectivity demands; owner geometry not native | Original label costs; its stated approximation/hardness results | Encodes shared purchase graph effects; current physical constraints require augmentation; no automatic transfer of this paper's exact interface bound |
| Heterogeneous / simultaneous network design | Infrastructure shared across condition-specific graphs | Condition-specific allowed edges/demands; physical owner consistency not identified as native in inspected formulations | Work-specific graph parameters and infrastructure objective | Profiles alone are expressible prior ideas; matching full physical/action contract or the same parameter bound is not established |
| Steiner selection with conflicts (Cornet–Laforest) | Vertex/support selection | Declared conflicts and connectivity | Inspected conflict-graph restrictions; selected-support objective | Distinct-owner clashes can be compiled, but naive purchase vertices invent routes; bundle, profile and objective transfer still needs an explicit construction |
| Weighted rank connectivity (Bodlaender et al.) | Connectivity partitions on a supplied decomposition | Preserves minimum-weight completion by representative bases | Boundary size; weighted representative rows | Applicable as a subroutine here; it supplies neither original physical ownership accounting nor a priority claim for this transfer |
| A&C distance-neighborhood logic (Bergougnoux et al. v2) | Our explicit Action/Occurrence/Usage/Cell graph | Formula encodes whole purchases, cell capacity and rooted profile connectivity | Supplied linear clique-width expression; weighted membership objective | Full expression and algorithm transfer established in Appendix B; constructed exponent O(prL+zL+p+zLh), versus O(prL+zL log(h+2)) here; not a lower bound on tighter generic encodings |
| CP-SAT flow formulation | Original action Booleans and original route edges | Owner/cell OR-capacity; separate profile flow | No supplied bounded-width decomposition; exact lexicographic stages | Full finite-model encoding implemented and executed; no matching worst-case interface guarantee asserted |

Direct primary source/version locators remain in source_ledger.json and the
existing encoding/proof files. The 16 October bounded check reconfirmed the
logic paper's v2 identity at https://arxiv.org/abs/2202.13335v2. No broad new
literature campaign or proof of nonexistence was undertaken. For fixed h, the
two displayed upper bounds have the same asymptotic interface exponent.

## Parameters: all computed except represented bit size

p is counted from supplied profiles; r from per-profile contracted within-floor
baseline components (all or safely marked); z from checked rectangular cells;
L from complete action-owner units and active baseline inter-floor edges;
h from unit owners intersecting each cell; g from unit owner counts. The
recognizer constructs these, rather than receiving a promised decomposition.
B is the represented input bit size, including costs, IDs and supplied geometry.
p,r,L control optional boundary sets and connectivity rows; z,L,h control owner
maps; g is descriptive and is not a separate exponent term. Recognition time
includes validation and construction; no free decomposition oracle is assumed.

## Operational pseudocode and proof obligations

1. RecognizeStrictInstance: validate frozen input and global owner consistency;
   compile unary/pair feasibility. This is the kernel/collision-equivalence
   assumption, not a construction-engineering certificate.
2. BuildOwnedCollisionCells: split represented rectangles at all x/y boundaries;
   require cell area > EPS and check predicted vs compiled conflicts.
3. BuildActionAssetUnits: incidence components of all available actions and
   owners; measure complete supports, including unused graph effects.
4. BuildFloorEventSchedule: construct the L-floor look-ahead and baseline-edge
   events. Every unit is processed at its first support floor.
5. IntroduceAction / UpdatePhysicalOccupancy: skip or pay once and occupy ALL
   effect cells; reject external/different owners. Ownership-locality lemma.
6. UpdateProfileWitnesses: choose supplied connected components per profile;
   glue partitions without inserting purchase vertices. Thin-witness lemma.
7. ReduceRepresentativePartitions: at the same event and equal occupancy and
   selected sets, retain minimum-label product cut-row bases. Representative
   preservation lemma; established weighted rank machinery is attributed.
8. ForgetCompletedInterface: erase owner IDs only after its complete unit;
   forget floors only after all incident events; reject disappearing selected
   nonanchor components. Locality and thin-witness completeness.
9. ReconstructAndReplayRepair: minimum accepting label; materialize original
   IDs, complete effects/occupancy, topology and separate profile routes.

After every event, each retained state describes a realizable selected-action
prefix and a partial rooted witness with exactly its live cell occupancy,
selected boundary sets and connectivity. Every feasible continuation's minimum
label has an at-least-as-good retained representative. Deduplication compares
only identical states at identical events. Future actions have not been
processed, so their IDs are disjoint from prefix IDs. Adding the same future
set preserves cost, cardinality and equal-cardinality sorted-ID ordering.

A cell has <=h+2 statuses during a unit; <=zL cells are live. Summing cut-row
bounds over selected boundary subsets gives <=3^(prL) rows per resource map.
Original-action witness choices and elimination add 2^O(prL); polynomially many
events and polynomial-bit exact labels yield the displayed bound. Original
costs are represented finite JSON numbers interpreted through their decimal
text, with exact sum/comparison; ID tuples and accumulated cost bit lengths
are polynomial in B. Caps are absent from this mathematical argument.

An empty surviving state set after exhaustive transitions means infeasible;
a state/cut/time cap never does. The implemented recognizer requires exactly
one supplied source per profile: an empty obligation list or a profile without
an obligation is unsupported. A trivial source=target obligation supplies a
root and requires no purchase. The theorem is restricted accordingly; it does
not pretend that unsupported empty-demand inputs were implemented.

The physical Set Cover decision threshold is sum(cost)<=k. Two floors, p=1,
L=2,h=1 and no collisions remain fixed, while target components r, private
cells z and bundle/catalogue size grow. Each incidence is a private aligned
rectangle and each set a unit-cost whole action. Cover iff every target is
reachable, preserving the budget exactly; coordinates/verification are
polynomial. This rules out floor-count-only tractability unless P=NP, not
single-shaft tractability, exponent optimality or superiority over CP-SAT.
