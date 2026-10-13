# M01 complexity memo: boundaries and a controlled exact case

14 October 2026. These are self-contained deductions for explicitly defined restrictions. They are not novelty claims, external peer review, or a completed general bounded-interface algorithm. G2 has an initial proof obligation documented; G3 remains open.

## 1. Formal decision boundary

An instance specifies frozen room polygons, evidenced physical connections, active access relations, profiles, source-target obligations, candidate typed actions, and nonnegative action costs. Given budget B, ask whether a selected set of actions satisfies all obligations, evidence/geometric conditions, and the chosen topology contract within B. Dependencies/exclusions are checked on the selected set. Activation is monotone and idempotent; overlapping bundles may restore the same relation, but every selected action incurs its own cost. Room-geometry replacement is atomic and exclusive per floor and is supported only in RCFAR.

The mathematical statements below concern rational-coordinate controlled instances. All connections in the proofs have constant-size, explicitly feasible geometry, so no unproved general continuous-geometric optimization assumption is needed. The implementation uses floating-point GEOS predicates and a stated tolerance; exact optimality refers to the finite selection problem under those acceptance predicates.

## 2. What exhaustive enumeration establishes

For k actions, enumerate all 2^k subsets. A complete ledger reports invalid selections, valid but unsatisfied selections, and feasible selection costs. With a polynomial-time subset verifier of cost T, enumeration takes O(2^k T), plus witness/ledger storage. The implementation stores every record and is deliberately limited by a caller-visible action-count guard. Its independent certificate checker repeats enumeration using a separate replay implementation and union-find reachability.

This proves optimum or infeasibility only for the supplied finite catalogue and specified geometry model. It does not search all conceivable renovations, verify building safety, or establish a thesis-level algorithmic contribution. FPT in the total supplied action count k by enumeration is immediate and should not be presented as a new result.

## 3. Proposition: general coupled corrections are NP-hard even with two floors

**Scope.** SCFAR allows an action to restore an arbitrary supplied bundle of physically evidenced missing access relations. One profile, unit action costs, two floors, one already active vertical lift, and no geometry edits suffice. This is a boundary for unrestricted bundles; it does not establish hardness when coupling is restricted to one physical shaft.

**Reduction from Set Cover.** Let U={1,...,m}, nonempty supplied subsets S_1,...,S_k, and budget B be a Set Cover instance. Empty sets can be discarded. Construct floor 0 with one source room s, and floor 1 with a rectangular hub room c and m target rooms t_i. An evidenced, active lift connects s to c. Each t_i has an evidenced door to c, whose model access relation is missing. There are no other active links to a target. Every room polygon and every shared-boundary adjacency is frozen.

Set Cover's classical hardness is the starting fact, not a result attributed to this project. [Nederlof's primary Set Cover paper](https://arxiv.org/html/1608.03439v1), introduction and relevant-previous-work section, records both NP-completeness and the established universe-subset DP. The project's restricted coverage method adapts that existing structure.

For each S_j, provide a representation-correction action of cost 1 activating exactly the doors c-t_i for i in S_j. Set obligations s-to-t_i for every i. A selection reaches t_i if and only if some selected subset contains i. Therefore a feasible repair of cost at most B exists if and only if a set cover of size at most B exists. No action changes A or room identity, invents a route, or installs a shaft. The construction size is polynomial in the Set Cover encoding.

**Geometric realization.** Use floor-1 hub [0,2m] x [0,2], target t_i=[2i,2i+2] x [2,4] (zero-based i), floor-0 source [0,2m] x [0,4], and elevations 0 and 3. Door openings are one-unit segments on y=2, centered in each target's lower boundary, with one-unit clear rectangular patches on both sides. A unit lift footprint [1/4,5/4] x [1/4,5/4] lies in s and c and in pre-reserved zones. A controlled profile has width and clearance at most 1. Additional shared boundaries between successive target rooms do not create traversable edges and remain unchanged throughout repair. The full physically evidenced access graph is a tree (lift plus hub star). The schema realization is `src/cfar/synthetic_star.py`.

**Conclusion.** This restricted decision problem is NP-hard. It is also in NP: a selected action set determines the active edges; cost and profile reachability are checked in polynomial time, with fixed feasible geometry and unchanged topology. Thus this restricted problem is NP-complete. The optimization version is NP-hard. This is a standard coverage reduction, not a claim of a new hardness technique.

**Implication for proposed parameters.** Hardness persists with f=2 floors, one cross-floor portal, and a tree-shaped physical access graph on the upper floor when arbitrary door bundles and unbounded obligations are allowed. Those parameters alone do not justify a polynomial-time repair solver. This does not rule out FPT in a combined parameter that includes obligation count, action span, or local coupling complexity.

## 4. Proposition: coverage DP is exact for a recognized contracted-star class

**Assumptions.** One profile. Contract baseline active-access components. All obligation sources lie in one root component r. All candidate edges that cross components are incident to r; candidates otherwise stay within a baseline component. Every action is an independent representation correction with no exclusions/dependencies or room edits. The union of all candidate activations passes the geometry verifier, so any subset is jointly feasible. Let m be the number of distinct target components outside r, and C(a) the subset of those components connected directly to r by action a.

For this class, all obligations hold exactly when the selected coverage sets union to all m terminal components. This equivalence fails for arbitrary paths with intermediate candidate edges.

**Recurrence.** Order actions a_1,...,a_k. Let D_j[M] be the least cost among subsets of the first j actions covering exactly mask M. Set D_0[0]=0 and every other entry to infinity. For each reachable M, carry forward D_{j-1}[M], and update D_j[M union C(a_j)] with D_{j-1}[M]+cost(a_j). Return the full-mask value, or infeasible if absent.

**Proof.** Every subset of the first j actions either excludes a_j (the carry transition), or includes it (the union transition from its subset of the first j-1). These cases exhaust all subsets and preserve exact coverage masks. Induction on j establishes D_j's definition. Since coverage is sufficient and necessary under the assumptions, the final full-mask value is the exact repair optimum. Nonnegative costs permit redundant edits but never require them. Selecting each action at most once is enforced by the stage index.

**Bounds.** Cost-only arithmetic work is O(k 2^m), with O(2^m) rolling cost storage and input preprocessing. This is FPT in m even when k grows. The Python reference stores selected tuples for deterministic cost/cardinality/lexical tie breaking: its worst-case tuple work is O(k^2 2^m) and live witness storage O(k 2^m), in addition to polynomial recognition and geometry checks. Do not attribute the cost-only bound to the tuple implementation without this qualification.

**Implementation and validation.** `dp_coverage.py` recognizes the assumptions, rejects unsupported instances with STAR_SCOPE, checks the selected solution, and reports states/transitions. Tests compare with the exhaustive oracle on seeded controlled instances and exercise 40 candidate actions with three terminal components. This is an adaptation of classical weighted Set Cover DP to a verified repair subclass, not evidence of algorithmic novelty or a general portal-interface DP.

## 5. Counterexamples outside the coverage scope

- **Intermediate action coupling:** baseline components r, x, t, with one candidate r-x and another x-t. Neither action alone directly covers t, but together they restore reachability. A coverage mask of directly linked obligations loses necessary intermediate connectivity. The recognizer rejects the non-star link.
- **Mutual exclusion:** two terminal-covering actions exclude one another. The coverage recurrence might select both; the restricted solver rejects this input. A broader state must retain relevant action commitments.
- **Joint geometry:** two profile-specific lifts have valid individual footprints but overlap. Subset feasibility is no longer guaranteed by per-action checks; micro-instance 17 rejects their union.
- **Profile sharing:** a paid lift action may enable edges for several profiles. Solving independently per profile double charges a shared action or misses coupled requirements; the structural solver accepts only one profile.

## 6. Roadmap for general bounded-interface DP

At a floor cut, a sufficient state may need per-profile connectivity partitions of portal terminals, unresolved obligation endpoints, action activation commitments spanning the cut, and summaries of geometry conflicts. A bound b on portal endpoints alone does not bound those other quantities.

Study a class with bounds on: profile count q; terminal/obligation representatives crossing any cut t; coupled actions simultaneously crossing a cut c; and the size g of an explicitly modeled conflict interface. Require local actions to have bounded contiguous floor span, and finite prevalidated candidate geometry with declared conflicts. Derive the state transition and prove that two partial repairs with the same state have identical feasible completions. Do not code a general DP before this sufficiency argument.

Tree-shaped per-floor D can simplify local path constraints, but the unrestricted-bundle reduction above already uses a tree. Number of floors f is not sufficient alone. Action count k supplies the small-instance oracle. Obligation-component count m gives the exact controlled coverage case. These are different parameters and should be reported separately.

## 7. Research gate status

The initial complexity map now has a precise hardness boundary, an exact restricted method, and counterexamples. It has not established that realistic shaft/local-access coupling yields a new parameterized result. All five named architectural full-text comparisons are now available, but broader theory equivalence remains unresolved, so neither these proofs nor successful micro-tests finalize the thesis direction. Next work must tighten the physical coupling class and compare its algorithmic structure with existing network design and Set Cover theory.
