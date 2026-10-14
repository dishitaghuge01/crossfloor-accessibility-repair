# M07: profile-count boundary for local conflicting priority intervals

14 October 2026. These are scoped structural/transfer arguments and executable witnesses, not established originality. They resolve two proposed directions before another solver is built. Overall novelty is unestablished; G3 remains open.

## Model

Use the common quotient path and uniform permission prefixes from the shaft compilation. Edge i has required priority d_i >= 0. Original action a has contiguous edge span [l_a,r_a], supply h_a and nonnegative cost. It covers i exactly when l_a <= i <= r_a and h_a >= d_i. Unavailable actions may be removed. Every remaining forbidden pair must have intersecting closed node supports [l_a,r_a+1]. Dependencies and selection-dependent shapes are excluded. Let p be the profile count and d the number of distinct positive priorities actually required, so d <= p.

The conflicts can include declared exclusions or compiled geometric collisions. The upper bound below covers either. The lower-bound transfer below uses declared exclusions only; these must not be described as physically realized collision graphs.

## Irredundant covers have closed-support ply at most 2d

Choose a feasible minimum-cost cover that uses the fewest actions among minimum-cost solutions. Every selected action has a private required edge: after deleting that action, some edge is no longer covered. Otherwise removal preserves coverage and cannot introduce a forbidden pair, and nonnegative costs contradict cost/count minimality. Assign each action one private edge and its priority q.

Partition selected actions by assigned q. Every action in that class has supply at least q. No class interval can be contained in another class interval, including equal endpoints: the contained action's private q-edge would be covered by the other. Hence ordering the class by increasing left endpoint also orders right endpoints strictly.

Suppose three class intervals A,B,C contain the same floor coordinate in their closed node supports, ordered by left endpoint. Then l_C <= r_A+1. Their integer edge spans A and C therefore leave no gap across B and jointly cover every edge of B. Both have supply at least q, so one covers B's private q-edge. This is a contradiction. Thus at every floor coordinate at most two class intervals are active; the same bound applies between floors. Summing over the at most d witness classes gives ply at most 2d.

This proof allows zero-priority gaps and containment across different witness classes. It does not reinstate the single-profile last-two recurrence: a low-supply outer interval and a high-supply inner interval can both be essential. Dependencies break the deletion argument.

### The closed-floor bound is tight

For p levels, take 2p edges with priorities [1,2,...,p,p,...,2,1]. For each q in 1,...,p define L_q=[q-1,p-1] and R_q=[p,2p-q], each with supply q and cost 1. The left q-edge is covered only by L_q, and the right q-edge only by R_q: lower-supply actions cannot serve it and higher-supply spans do not reach it. All 2p actions are essential. All their closed supports contain floor p. Therefore a universal bound below 2p on simultaneous original supports is false, even without conflicts. This is not a construction-feasibility assertion about putting all these assets at one location.

## Consequence: prior-framework XP, not profile-only FPT

The endpoint sweep can retain up to 2d active original IDs, enforce supply at required-point events, filter forbidden pairs, and charge cost on introduction. Completeness follows from the bound; locality ensures ended actions cannot conflict with future starts. At most sum(j=0,...,2d) binomial(k,j) active sets occur at each of O(k+n) events. Straightforward processing has O((k+n)(d+1)k^(2d)) arithmetic/state work for k >= 2, excluding witness tuple work, bit costs and geometry compilation. It is polynomial for each fixed d, but its exponent depends on d: this is an XP bound. It does not establish an f(d) times polynomial(k+n) FPT bound.

This is a project-derived extension of prior bounded-active-set sweeps. Biedl/Biniaz/Lubiw's 2019 manuscript section 2 uses bounded active subsets and add/remove events, while section 5.2 specializes to two active intervals. Their geometric problem and objective differ. [Primary manuscript](https://www.khoury.northeastern.edu/home/vip/teach/Algorithms/5_greedy/notes/Min-Ply-Cover.pdf). No source runtime is transferred and no multi-profile sweep solver is implemented at this checkpoint. Raising the active-set cap alone is not a supported originality claim.

## Profile-only FPT is obstructed when declared conflicts are unrestricted

Jacob/Majumdar/Raman's November 18, 2020 institutional manuscript defines conflict-free set cover with indexed duplicate sets and an independent-set constraint. Theorem 3, section 3.2.1 (printed pp. 11-12), proves W[1]-hardness by universe size even for bipartite conflicts using duplicate singleton sets. Section 4.2 gives interval/chordal **conflict-graph** algorithms (Theorems 8/9); having interval coverage alone is different. [Inspected primary full text](https://pure.royalholloway.ac.uk/ws/portalfiles/portal/40220434/conflict_free_set_cover.pdf). The table calls the hardness result Lemma 3, but the inspected proof body calls it Theorem 3; use the proof-body locator.

Here is the separate parameter-preserving transfer. Given the duplicate-singleton family over universe {1,...,m}, create m path edges with priorities d_i=i+1 for zero-based i. A singleton alternative of group q becomes original interval [q-1,m-1] with supply q and unit cost. At an edge of priority t, it reaches that edge only if q <= t, and supplies enough only if q >= t. Thus it covers exactly the requirement t=q. Preserve every original forbidden pair and the decision budget. Indexed alternatives remain separate IDs even when their coverage is identical.

All resulting node supports contain the last floor m, so every preserved forbidden pair is local. The conflict graph remains bipartite when the source graph is bipartite. Feasible selections and costs correspond subset by subset; m profiles and m edges suffice. Consequently the abstract nested-priority interval class with local declared exclusions is W[1]-hard parameterized by profile count. A profile-only FPT exact method for this class would imply FPT=W[1]. This is a transfer of prior hardness, not a novel hardness claim.

The executable frozen-floor witness uses one evidenced existing shaft and representation actions with prefix permissions, plus declared `excludes`. Each profile obligation is between the endpoints of its corresponding edge. There are no geometric collisions and no new physical asset. This demonstrates consistency with the repository's model without manufacturing a physical origin for the input conflict graph. It does **not** prove hardness for geometry-only reserved alternatives, fixed profile count, bounded conflict degree, fixed candidate density, or independently bounded full constraint width.

## Evidence and next decision

`priority_boundaries.py` builds the tight-support and singleton-transfer witnesses. 83 new tests check every irredundant cover in 64 seeded small priority systems, six tight families, every subset in 12 declared-conflict shaft mappings, their exhaustive-oracle answers, and rejected witness inputs. Tests corroborate the arguments; they are not a substitute for the proofs above.

The fixed-profile extension remains a known-framework baseline; the unrestricted declared-conflict extension has a transferred parameterized obstruction. Neither justifies a new solver as a thesis novelty result. The remaining useful distinction is **geometrically realizable** conflicts under a justified asset/space bound. Before claiming that result, inspect geometric independent-set/cover lower bounds and prove any construction obeys the exact frozen-layout evidence contract. The Marx unit-square source was located but not successfully fetched; a later primary paper states the rectangle hardness, which alone is not a completed physical reduction. Do not promote that lead to a theorem.
