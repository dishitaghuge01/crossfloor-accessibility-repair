# M09: owned collision cells and shared-asset interface compression

14 October 2026. **Proposed theorem with a constructive working proof; originality and independent verification remain pending.** This develops the active physical-interface direction. It does not close it or declare the underlying rank-based machinery new. No solver implementation or timing result is claimed.

## Positive development beyond M08

M08 retained representative action identities and required complete exclusive slots and private complete bundles. Here the proposed floor state retains resource occupancy and a connectivity witness, while asset identities are kept only during their complete coupling unit. This supports partial slot footprints when an exact collision-cell representation exists, repeated use of one asset across actions, and shared-cost actions affecting several assets. A rank-based construction improves the proposed parameter dependence from the M08 menu/Bell bound to

`recognition_time + 2^O(prL + zL log(g+2)) * polynomial(input_bit_size)`.

The possible contribution is the physical/cost-preserving decomposition and its explicit interface bound. Weighted partition compression is prior work. This is a concrete result to develop and compare, not an established originality claim.

## Recognized class and measured parameters

- Strict frozen room polygons/IDs/adjacency; fixed-shape portal activation actions with nonnegative rational costs. No action implications, arbitrary exclusions, shape changes or selection-dependent opaque obstructions. Each successful repair is materialized using its complete original actions.
- p profiles, one permanent accessibility anchor per profile, and any number of anchor-to-target obligations. Profiles remain separate graph layers; a coupled action may activate edges in several layers for one cost.
- At most r relevant within-floor baseline components per profile per floor, including obligation components. Components containing neither anchor/target nor an endpoint of a nonloop candidate/baseline inter-floor quotient edge may be omitted from the access graph; original rooms remain in geometry/topology validation. Baseline inter-floor connections remain explicit and have endpoint span at most L consecutive floors.
- At most z collision cells per floor. Every proposed asset footprint is exactly a union of whole cells, up to zero-area boundaries. Distinct proposed assets collide iff their selected occupied cell sets intersect. Uses of the same asset may share a cell when its kind and fixed per-floor footprint are consistent, as required by the asset exemption. Geometry recognition verifies this equivalence; a named reserved zone is not itself a collision cell.
- Baseline geometry is fixed. Candidate new-asset IDs do not coincide with baseline asset IDs. Drop unary-infeasible actions, including collisions with baseline. This theorem's main statement is for physical portal interventions. The [M10 typed background corollary](typed_background_interface_extension.md) separately admits local evidence-backed corrections using a fixed physical background independently of missing graph permissions; it does not silently broaden this main statement.
- Build the bipartite incidence graph between available original actions and their asset IDs. Its connected components are **coupling units**. An action involving several assets joins those assets into its unit; all actions sharing an asset belong to the same unit. Physical collisions between different units do not merge units. A unit has at most g assets and its complete geometry/effect support lies in at most L consecutive floors.

The unit bound is on all effects of all its available actions, not merely one action. The number of units, actions in a unit, competing alternatives in a cell, floors and obligations is unrestricted. Assets are consistently identified by authenticated input records; renaming a shared asset to make the parameter smaller is invalid.

Full catalogue validation precedes this construction. In the current implementation it includes global consistency of an asset's footprint, kind, width and physical-profile set. The cell/owner abstraction does not relax those checks or authorize a bending/inconsistent shaft.

### An exact geometric realization

Grid-aligned rectangular footprints give a sufficient realization: partition the relevant reserved areas into positive-area rectangular cells using supplied grid coordinates, require each footprint to be a union of cells, and require each cell area to exceed the kernel's EPS. Sharing a cell then implies overlap area above EPS; footprints with no common cell intersect only on zero-area boundaries. Partial footprints within the same reserved zone are allowed and are never resized or replaced by subinterval aliases.

An arbitrary rectangle arrangement with tiny cells does not automatically satisfy this condition: several individually small overlaps can sum past EPS. Either verify exact pairwise equivalence to the implemented collision predicates or reject the proposed cell abstraction. Cell count is a measured geometric-complexity parameter, not an assertion that arbitrary layouts have small z.

## Lemma 1: all identity-dependent reuse is local to one unit

Distinct units have disjoint asset sets and disjoint original action IDs. If a future action could share an asset with an action already processed as a complete unit, their incidence components would coincide. Hence outside a completed unit, a selected occupied cell conflicts with any newly occupied cell at that position, regardless of which old asset occupied it.

Inside a unit, identity matters: filling a cell already used by the same asset is allowed, while filling one used by another asset is forbidden. Owner labels 1,...,g therefore suffice locally. After the whole unit is processed, only occupied/unoccupied cells are needed. This proves the ownership-forgetting rule and addresses the M08 shared-asset counterexample without discarding the direction.

An atom used by two owners within one original action makes that action unary-infeasible. Same-owner exemption also requires the verified fixed-shape/kind consistency; owner labels alone do not establish it.

## Lemma 2: thin the route witness, never the physical intervention

For any feasible complete repair, consider the root-connected component of its materialized access graph separately in every profile. Every required target lies in that component. For each original action, each connected component of its supplied profile-edge graph lies wholly inside or wholly outside that materialized root component. Retain its graph components lying inside, and ignore the others in the connectivity witness. Treat baseline edges similarly.

The union of these witness edges connects every required target to its anchor. All chosen witness vertices can be required to connect to that anchor, including auxiliary vertices. No original action is shortened: its full cost, full activation bundle and all occupied cells remain in the actual repair and geometry state. Only a proof-of-reachability subgraph is thinned.

Conversely any such rooted witness uses edges of the complete selected actions/baseline. Its target paths remain valid in the materialized graph. Thus introducing witness choices changes neither optimal repair cost nor geometric admissibility. This distinction is essential: shortening the occupied intervention, rather than just its route witness, would be unsound.

Selecting any subset of an action's supplied connected graph components is sufficient for completeness. There are at most 2^(prL) such choices. It is unnecessary to enumerate every edge subset or to claim that every possible route witness is generated; the root-component witness above is enough to represent an optimum.

## Floor and unit transitions

Use a look-ahead window f,...,f+L-1, with at most rL component vertices per profile and a permanent virtual anchor in each layer. Attach the virtual anchor to its actual anchor component with a zero-cost witness edge when that component enters the window. Targets are mandatory witness vertices. Other component vertices are optional until used by witness edges.

Process baseline edges at their earliest endpoint floor, choosing whether to use them in the witness; baseline materialization remains fixed either way. Process a coupling unit at its earliest touched floor. Its whole support is now in the window, so all of its original actions can be considered sequentially before advancing the floor. This is an order for computation, not a construction schedule.

At the start of a unit, mark cells occupied by earlier units as external. For each original action, branch:

1. Skip it.
2. Take it, charge its original cost and count once, and retain its ID. Reject if any cell it occupies is external or is internally owned by another asset. Fill unused cells with its owner; permit verified same-owner reuse. Choose a subset of its supplied graph components for each profile, introduce their witness vertices and merge their partition blocks.

After every original action in the unit has been considered, erase internal owner identities, mapping all nonempty cells to ordinary occupied bits. No later action outside this unit can share those assets, by Lemma 1. Importantly, take/skip remains at the original action level even when one action purchases several assets for one shared cost.

When a floor leaves the window, forget its component vertices. Reject if a selected witness component loses its last boundary vertex without containing its permanent anchor. Forgetting inactive optional vertices imposes no condition. Drop expired collision cells. All future incident effects have already been processed before forgetting, because complete unit/baseline supports obey L.

An accepting final state has no non-anchor selected component and every introduced target has been part of the witness. Replay its original action IDs against strict graph/geometry/topology checks.

## Lemma 3: a sufficient state and exact accounting

During a unit the state records:

- each live cell's status in {empty,external,owner 1,...,owner g};
- each profile's selected boundary vertex set U_q, containing its permanent anchor;
- a connectivity partition pi_q of U_q.

Outside a unit, cell status is just occupied/unoccupied. The label is `(exact total cost, original action count, sorted original IDs)`. It is not part of the state identity.

For a fixed event index, original actions still available in the continuation are the same for every history. No original ID is charged twice: actions are considered sequentially once within their unique unit. Remaining unit identity reuse is captured by the owner map; completed-unit reuse is impossible. Geometry's remaining conflicts depend only on this map. Witness connectivity through processed vertices is captured by the partitions. Every forgotten selected vertex remains attached to a live block or its anchor; otherwise its history was rejected.

Consequently a completion depends on the state, not on the identities of previously paid actions. Adding the same continuation preserves exact cost/count order and sorted-ID order at tied counts because its IDs are disjoint from processed IDs. This justifies labels and standard minimum-label dominance.

Without algebraic compression there are at most `(g+2)^(zL)` owner maps times `product_q sum_(U_q containing root) Bell(|U_q|)` connectivity states. This already removes the catalogue-sized identity factor, but still has the usual partition exponent. The next lemma supplies the sharper bound.

## Lemma 4: product-profile representative partitions

Fix a cell map and selected boundary sets U_1,...,U_p. For one profile, let C_q[pi,c] indicate that every block of partition pi lies wholly on one side of cut c, with the anchor forced to the first side. The existing weighted-partition factorization says, over GF(2),

`M_q[pi,tau] = [pi joined with tau has one block] = (C_q C_q^T)[pi,tau]`.

This is prior machinery from Bodlaender/Cygan/Kratsch/Nederlof, not a new lemma attributed to this project. For a partition tuple define its row as the tensor product of its p cut rows. Inner products factor, giving

`M[(pi_q),(tau_q)] = product_q M_q[pi_q,tau_q]`.

Thus the number of cut columns is `D = 2^(sum_q(|U_q|-1))`. Sort history rows by the repository label order and greedily keep a GF(2) row basis. At most D histories remain.

**Minimum-label preservation.** A discarded row is a sum of previously kept rows, all with no worse label. For any completion tuple tau for which the discarded row's inner product is one, at least one summand has inner product one. That kept history admits the same completion and has no worse final label. This argument uses only total label ordering and its stability under adding disjoint continuation IDs; it does not require pseudo-polynomial cost enumeration.

**Why actual repair completions fit this matrix.** A legal remaining witness induces connectivity partitions on the current selected boundary sets. If it contains a terminal component unable to reach that boundary or its anchor, it is infeasible independently of the prefix. Otherwise it completes the prefix exactly when every selected boundary vertex joins its profile anchor. This is the product of the one-block tests above. Only witness choices already committed by the prefix are used; ignored physical edges are not secretly reinstated by a continuation. Completeness remains guaranteed by Lemma 2.

The representation is therefore valid across the insert/glue/cost-shift/forget operations and simultaneous shared-cost profile transitions. Source weighted-partition theory supplies the underlying operations; the ownership/accounting and multi-profile completion correspondence are argued here explicitly.

Summing the representative limit over optional boundary subsets gives at most `3^(prL)` rows per cell map, since each of at most rL non-anchor vertices per profile is absent, present on one of the cut sides, with the anchor fixed. More formally, `sum_(U containing anchor) 2^(|U|-1) = 3^(rL)` for a full rL-sized optional set. Mandatory target choices only reduce this upper bound.

## Proposed theorem and parameter dependence

Under the recognized assumptions, the proposed deterministic algorithm preserves optimum original-action cost, count and lexical witness, with at most

- `2^(zL) * 3^(prL)` representative histories between units;
- `(g+2)^(zL) * 3^(prL)` histories during a unit.

Every action has at most 2^(prL) witness branches; constructing cut rows and ordinary Gaussian elimination takes a further factor 2^O(prL). Baseline and floor shifts also have bounded per-state work. Therefore a loose total bound is

`recognition_time + 2^O(prL + zL log(g+2)) * polynomial(input_bit_size)`.

Physical recognition includes validation, unary tests, asset consistency, the exact cell/conflict check and coupling-unit construction. It can be polynomial and may dominate measured runtime. The state argument does not claim all geometry compilation is linear in catalogue size. Exact rational arithmetic and full witness comparisons add polynomial bit work.

This is single-exponential in the stated interface encoding size, not an assertion of `2^O(p+r+z+L+g)`. It is a working algorithmic result, not a tested implementation or an independent optimality certificate. The dependence on floors, raw actions and raw asset alternatives remains polynomial.

## Analytical shared-asset repair example

Four frozen floors have one room component each. X-left activates path edges 0,1 for cost 4; X-right activates 1,2 for cost 1. Both use the same consistent asset X. Y-left activates 0,1 for cost 1 using a different asset in the same footprint. Z activates 0,1,2 for cost 10 in a disjoint footprint. One profile requires floor 0 to reach floor 3.

The X coupling unit admits X-left+X-right at cost 5. Y-left cannot coexist with either X segment at the overlapping floors, and cannot cover edge 2 alone. Z is feasible at cost 10. Thus optimum is the two original X actions at cost 5. A cheapest-first-transition replacement would discard X-left in favor of Y-left and lose that optimum. The unit transitions preserve it. This is an analytical example, not a reported experiment.

### Partial footprint and shared-cost scenarios

A supplied reserved region `[0,4] x [0,1]` can contain footprints A=`[0,2] x [0,1]`, B=`[2,4] x [0,1]` and C=`[1,3] x [0,1]`. Four unit-width cells encode them exactly. A and B share only a boundary and can coexist; C overlaps each in positive area. Treating the entire region as one exclusive slot would reject A+B incorrectly. This is a collision-model example; a full repair input must additionally supply valid room endpoints, reservations, profiles and landings.

A two-floor repair can also have two independent landing destinations above a baseline-connected lower-floor circulation area. X and Y occupy disjoint reserved cells. Original action A installs both for cost 3; actions B and C install X and Y separately for costs 2 each. All three actions lie in one unit with g=2. The unit processing can select A once at cost 3, instead of charging once per asset or selecting B+C at cost 4. This is an analytical graph/cost scenario, not a field-validated construction claim.

### Manual proof checks performed

- The old same-asset extension counterexample is represented by one unit and cannot be lost by an early cheapest-action substitution.
- A witness may ignore a disconnected edge of a paid bundle, but its occupied cells remain present. Any later different asset colliding with that unused part is still rejected.
- No compression merges histories with different internal owner maps or selected boundary sets. Owner erasure occurs only after every original action in that complete incidence component has been considered.
- A mandatory target is selected on introduction even when currently isolated; it must survive in a live witness block until a valid anchor connection is established.
- Two different profiles share action costs and physical cells, while their witness connectivity remains separate. The representative test is a conjunction, not permission to switch profiles.
- Full action IDs remain in labels. Same-asset overlap is not duplicate action purchase, and neither internal reuse nor rank reduction adds a second charge for an already processed ID.

These are a self-audit of the working argument, not independent proof review or executable regression tests.

## Structural parameter separation and illustrative bounds

For the four-floor one-profile example, use r=1, L=4, z=2 and g=1. The proposed representative limits are at most `2^8 * 3^4 = 20,736` outer histories and `3^8 * 3^4 = 531,441` in-unit histories. For a two-floor g=2 bundle with r=2, z=2, p=1, both prL and zL equal four: the limits become 1,296 and 20,736. These are loose theoretical maxima, not observed state counts or runtime predictions.

More importantly, arbitrarily many private alternatives for one two-floor footprint create an arbitrarily large conflict clique, although p,r,z,L,g remain fixed. Its pair-conflict graph treewidth and conflict vertex-cover size both grow with the alternative count. The owned-cell state bound does not. A direct algorithm parameterized by those raw graph measures therefore does not supply the same physical parameter bound without an additional encoding/reduction argument.

Global neighborhood diversity is also different from the local parameter. A chain of F floor interfaces can have many private alternatives per interface; alternate two disjoint footprint positions so neighboring interfaces do not collide. Each interface's alternatives form one conflict clique with a distinct neighborhood type, making global conflict-graph neighborhood diversity grow with F. Yet p=1, r=1, z<=2, L=2 and g=1 remain fixed. All rooms and footprint reservations in this example are supplied, and geometry still obeys the stated fixed 2D model. This is an analytical parameter family, not a public-building evaluation or a claim of global constructability.

These separations support the usefulness of a local physical parameter. They do not by themselves prove originality. Resource-incidence representations can be substantially narrower than pair-conflict graphs, and established structural metatheorems remain relevant baselines. The positive claim should concern the exact ownership-aware representation and sharper explicit bound, not first FPT existence from generic logic.

## Active novelty claim and next positive development

The candidate contribution is an **owned-cell/asset-unit interface theorem for exact rooted shared-cost repair**, with original-action accounting, a physical cell recognizer, and the explicit bound above. It is stronger than the M08 private-bundle/full-slot construction and explains how to handle its most relevant failure case.

The use of weighted bases, tensor products, resource capacity states and connectivity witnesses has prior art. The originality comparison must ask whether an existing constrained-labelled/resource-connectivity result already yields this entire ownership-aware bound with the same physical assumptions and complete-action witness semantics. If it does, refine the theorem's structural parameter, admissible geometry or evidence contribution; do not abandon the physical-interface direction merely because a proof ingredient is established.

Next: independently check the physical-to-resource recognition and completion-preservation proof; compare exact resource/owner formulations rather than keyword titles; and develop documented local-ramp, short-lift and shared-asset scenarios satisfying the measured bounds. Arbitrary terminal pairs, unrestricted dependencies, unbounded unit span and higher-order moving geometry remain future extensions, not present guarantees.

Primary algebraic source: [Bodlaender/Cygan/Kratsch/Nederlof accepted manuscript](https://pure.tue.nl/ws/portalfiles/portal/57608658/journaldeterministic_complete.pdf), dated March 11, 2014, published Information and Computation 243 (2015), 86-111, DOI 10.1016/j.ic.2014.12.008. Relevant locators: section 3.6, Definitions 3.11-3.12, Lemmas 3.13-3.15 and Theorem 3.7 proof, printed pp. 19-22. Multi-profile ownership/cost transfer is the project argument above, not a theorem stated by that source.
