# Candidate: original-interval DP with local shaft conflicts

14 October 2026. **Unestablished novelty; not implemented or benchmarked at this checkpoint.** This is a proposed exact recurrence with a correctness argument for a narrowly stated class. It is not a general profile/interface theorem.

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

There are O(k^2) pair states and at most O(k^3) transitions. Cost-only arithmetic/pointer DP is polynomial, excluding numeric bit costs and compilation. Storing and comparing full lexical witness tuples adds up to a factor k in work and storage. No resource or empirical performance claim has been tested yet.

## Counterexamples outside scope

- Nonlocal conflicts: three unit intervals [0,0],[1,1],[2,2] cover a path, but a forbidden pair between the first and third would be missed by consecutive-only compatibility.
- Multiple priorities: demands [1,2,1] need a supply-1 interval [0,2] plus a supply-2 interval [1,1]. Both are essential despite containment, violating the structural lemma.
- Dependencies: B=[0,2] may require A=[0,1] even though A is coverage-redundant. Deleting A invalidates the repair.
- Additional geometric obstructions that are not captured by the proved unary/pairwise kernel invalidate the compilation premise.

## Mandatory originality audit before a positive claim

Existing Priority Line Cover does not handle these conflicts, but that alone is insufficient. Compare direct conflict-free interval-cover and geometric conflict-cover methods, weighted set covering with hard conflicts, and compatible-path/cover reductions. Banik et al.'s Algorithmica 2020 conflict-cover paper currently has publisher preview evidence only; Jacob/Majumdar/Raman's full manuscript and Saffari/Fathi's hard-conflict weighted formulation remain required direct-method comparators. Soft-penalty conflict-cover methods are distinct and cannot substitute for hard exclusions.

The next implementation checkpoint should first test this abstract recurrence against complete subset enumeration on local-conflict intervals, then recognize/build genuine strict geometry cases and validate them. Even successful tests would establish correctness of an implementation, not novelty. G3 remains open.
