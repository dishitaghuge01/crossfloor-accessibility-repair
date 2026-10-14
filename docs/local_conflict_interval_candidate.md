# Candidate: original-interval DP with local shaft conflicts

14 October 2026. **Implemented and differentially verified; novelty unestablished.** This is an exact recurrence for a narrowly stated class. The structural lemma and two-active-interval state framework have identified prior work. It is not a general profile/interface theorem or an originality result.

## Class to recognize

One profile. After universally free baseline contraction, the candidate access graph is a path with edges 0,...,n-1. Obligations require every edge of that path. Each action activates a contiguous nonempty interval [l(a),r(a)] of those edges, with fixed original geometry and nonnegative cost. Unary infeasible actions are unavailable. No action dependencies are allowed. Compile geometric and declared pairwise exclusions using the established kernel.

Every remaining conflict (a,b) must be local: their **closed node-support intervals** [l(a),r(a)+1] and [l(b),r(b)+1] intersect. This is a recognizer condition on actual compiled conflicts, not an assumed consequence of the word shaft. It is automatically satisfied by simple one-room-per-floor consecutive-floor assets whose only pairwise collisions occur on a common endpoint floor, but contractions or extra effects can break it. Reject nonlocal conflicts, disconnected/unrequired path edges, noncontiguous bundles and additional profiles.

## Structural lemma

From any optimum choose an inclusion-minimal cover. Removing redundant actions cannot increase cost, cannot create a pairwise collision and preserves all obligations. Such a cover contains no interval contained in another selected interval. Therefore order its intervals by increasing left endpoint; their right endpoints also increase strictly. Equal endpoints imply redundancy and can be removed.

For three consecutive selected intervals A,B,C, one must have l(C)>r(A)+1. Otherwise A and C together cover every edge of B, so B is redundant. Consecutive cover intervals must satisfy l(B)<=r(A)+1 to leave no uncovered edge. It follows that all **nonconsecutive** selected intervals have disjoint closed node supports: l(C)>r(A)+1. By the locality condition, they cannot conflict. Hence only consecutive selected intervals require explicit compatibility checks. This uses a full single-priority cover; it is false for priority valleys or dependencies.

## State and recurrence

A state records the last two original action IDs (A,B), including a dummy predecessor for a one-action prefix, and the best cost/witness of a cover prefix ending at r(B). Start with every action B with l(B)=0. Append C only if:

- l(C)>l(B), r(C)>r(B), and l(C)<=r(B)+1;
- B and C are compatible;
- if A is real, l(C)>r(A)+1.

The new state is (B,C), charging c(C) once. Accept a state whose last interval ends at n-1. A one-action cover is included. Costs/counts/lexical action IDs use the repository tie convention; no synthetic subinterval is selected.

**Sufficiency.** All older selected intervals end no later than r(A). The last condition makes C's node support disjoint from all of them, so it cannot conflict with any older action. Future admissibility and coverage depend only on A,B and the fixed catalogue. Thus retaining the best prefix for the same state loses no completion. Adding the same future IDs preserves exact cost/count order and, at tied counts, sorted lexical set order.

**Correctness.** Every transition produces a gap-free cover prefix whose selected actions are pairwise compatible: the newest action is checked against B and cannot conflict with older intervals by locality. Conversely the structural lemma gives an optimum whose action sequence obeys every transition. The graph of states is acyclic because right endpoints strictly increase. A minimum accepting path therefore has exactly the optimum repair cost in the recognized class. Geometry/topology/reachability must still be replayed at the end.

There are O(k^2) pair states and at most O(k^3) transitions. Cost-only arithmetic/pointer DP is polynomial, excluding numeric bit costs and compilation. Storing and comparing full lexical witness tuples adds up to a factor k in work and storage. No timing or general scaling benchmark has been collected.

## Counterexamples outside scope

- Nonlocal conflicts: three unit intervals [0,0],[1,1],[2,2] cover a path, but a forbidden pair between the first and third would be missed by consecutive-only compatibility.
- Multiple priorities: demands [1,2,1] need a supply-1 interval [0,2] plus a supply-2 interval [1,1]. Both are essential despite containment, violating the structural lemma.
- Dependencies: B=[0,2] may require A=[0,1] even though A is coverage-redundant. Deleting A invalidates the repair.
- Additional geometric obstructions that are not captured by the proved unary/pairwise kernel invalidate the compilation premise.

## Mandatory originality audit before a positive claim

Existing Priority Line Cover does not handle these conflicts, but that alone is insufficient. Compare direct conflict-free interval-cover and geometric conflict-cover methods, weighted set covering with hard conflicts, and compatible-path/cover reductions. Banik et al.'s Algorithmica 2020 conflict-cover paper currently has publisher preview evidence only; Saffari/Fathi's hard-conflict weighted formulation remains incompletely inspected. M07 resolved Jacob/Majumdar/Raman's institutional full-text route and inspected the relevant hardness and interval/chordal conflict-graph recurrences; see [profile boundary](priority_profile_boundary.md). Soft-penalty conflict-cover methods are distinct and cannot substitute for hard exclusions.

## Implemented checkpoint

`src/cfar/dp_local_intervals.py` implements the abstract recurrence and the strict geometry recognizer; `solve-local-shaft` emits a result and reproducibility manifest. It compiles unary/pairwise constraints before recognizing the path, allows local declared exclusions, and replays successful repairs through geometry, adjacency and obligation checks. Resource-limit failures remain errors. The result's optimality evidence is the recurrence, not an independent exhaustive certificate.

89 new tests include 64 seeded abstract comparisons against complete enumeration, 12 strict declared-conflict comparisons, six generated physical reserved-asset comparisons, the physical cost-10 collision witness, unavailable geometry, exact large costs/ties, invalid scope and caps. A 100-identical-action regression proves that the DP does not call the oracle; it is not a scaling benchmark. The complete suite passes 322 tests. Geometry compilation now memoizes identical activated connection/profile unions within one immutable instance; it separately reports requests, actual geometry calls and cache hits.

## Prior state framework and adaptation boundary

Biedl, Biniaz and Lubiw, *Minimum Ply Covering of Points with Disks and Squares*, June 7, 2019 author manuscript, section 5.2 (printed pp. 9-12), uses a 0/1/2-active-interval sweep DAG after a non-dominance/ply-two lemma (Lemma 3, attributed there to earlier work). Its objective is maximum weighted membership/ply, solved by a bottleneck path; it does not state our minimum-sum hard-conflict model. [Full manuscript](https://www.khoury.northeastern.edu/home/vip/teach/Algorithms/5_greedy/notes/Min-Ply-Cover.pdf), [arXiv record](https://arxiv.org/abs/1905.00790).

The following is a project-derived adaptation argument, not a theorem attributed to that paper. Represent action [l,r] by node-support interval [l,r+1], with required points i+1/2 for each path edge. Expand endpoints by distinct offsets of magnitude less than 1/10, moving left endpoints left and right endpoints right. This preserves required-point incidence and integer-support intersections, including contact at a floor. It also preserves disjointness of nonconsecutive intervals in the irredundant optimum proved above. Equal-endpoint actions cannot both occur in that optimum, so their perturbation order is immaterial to completeness.

Sweep these distinct endpoints, retaining at most two selected active original IDs. At a start event, either skip or introduce the interval; at its end event, remove it if selected. Forbid active pairs that are compiled conflicts and forbid empty states at required points. Charge an action's cost only when introduced. Each interval has one start and one end, so it is charged once. Any accepted sweep path covers every required point and obeys all local conflicts: conflicting supports overlap in some sweep strip, where the pair would be rejected. Conversely an irredundant feasible optimum has ply at most two and is represented by these states. An ordinary minimum-sum DAG path therefore solves the same recognized cost problem. Repository count/lexical tie handling can be retained on labels.

This derives the narrow polynomial solvability using an established state framework with changed weights and compatibility filtering. It is substantial prior-method overlap and defeats a positive originality claim based merely on two retained intervals or the structural lemma. We do not transfer the source's faster complexity bound to our implementation. Remaining direct hard-conflict comparators remain incompletely inspected. G3 stays OPEN.

## Independent sweep implementation

`src/cfar/dp_interval_sweep.py` independently implements endpoint events rather than the last-two recurrence. Its state is the set of at most two active action IDs, with a best exact cost/count/sorted-ID witness. At an integer floor coordinate all starts are processed before all ends, so touching supports coexist and conflicts are checked; required edge-midpoint events occur between floor coordinates. Multiple starts and ends are ordered deterministically by ID. This event convention implements the relevant perturbation semantics without floating-point coordinates.

Every action is selectable only at its start; selecting charges its cost once. Future choices depend only on currently active IDs and the event index. An ended interval cannot conflict with a later-starting one because nonlocal conflicts are rejected. The best-prefix rule therefore preserves all feasible completions and the repository tie convention. The complete witness is retained for output and tie comparison, not as part of the state identity. The proof above ensures an irredundant optimum has at most two simultaneous supports even at floor contacts.

There are O(k+n) events and O(k^2) active-set possibilities per event: an O((k+n)k^2) bound on state visits/transitions, excluding full witness comparisons, numeric bit costs and geometry compilation. This deliberately simple implementation retains uncompressed per-event states; it does not implement the source paper's compressed DAG or claim its faster bound. `max_states` caps cumulative sweep state visits, whereas the last-two solver caps distinct action-pair states. Their raw state counts must not be interpreted as the same quantity.

107 added tests include 100 seeded three-way abstract comparisons (sweep, last-two, complete subsets), six three-way physical compiled-constraint comparisons, and boundary contact, zero-cost tie, large-cost, empty-input and resource-limit checks. Neither solver calls the other to compute its answer. Physical compilation is shared and both use the same exact arithmetic helper: agreement is independent evidence for the optimization recurrences, not for an independently implemented geometry engine. This confirms the prior-framework adaptation as an executable baseline; it does not pass the algorithmic originality gate.
