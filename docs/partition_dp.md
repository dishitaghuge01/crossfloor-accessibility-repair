# Exact partition DP for jointly feasible activation catalogues

14 October 2026. This is a controlled algorithm specification and proof, not a novelty claim or a bounded portal-interface theorem.

## Recognized class

SCFAR only. Actions may be evidenced corrections or certified physical activations, with arbitrary bundles across profiles. Every effect activates a connection; room replacement, dependencies and exclusions are rejected. The geometry of the union of all actions must pass the existing strict verifier. Under the documented fixed-geometry model, removing activations cannot introduce a collision, an invalid landing, or a new room-accessibility requirement. Thus every subset is geometrically feasible. This conservative recognizer rejects a catalogue containing even one infeasible or conflicting candidate; it does not pronounce the original optimization instance infeasible.

For each obligation profile, contract its baseline connected components. Keep every component incident to a candidate activation for that profile, and every obligation endpoint component. Other components cannot mediate a new route and may be omitted. Components with no obligations remain when incident to candidates: they can be intermediate vertices. Unused profiles still participate in the geometry precheck, but need no optimization state.

## State and recurrence

Order actions lexically. A state is a tuple of canonical connectivity partitions, one on each retained profile-specific component set. Initially every contracted component is a singleton. Skipping an action leaves this tuple unchanged. Taking an action joins endpoint blocks for every activation and every affected obligation profile, and charges its cost once. For each resulting tuple retain the best `(exact cost, action count, lexical action IDs)` value. At the final stage accept states in which every obligation's endpoints share a block.

**State sufficiency.** Two partial selections with the same tuple have the same connectivity response to every future action bundle: adding undirected edges depends only on the current equivalence relations. Future subset admissibility is identical because there are no dependencies, exclusions or geometry conflicts. Final obligation truth therefore agrees. Keeping the smaller value loses no optimal completion. The cost and count orders survive adding the same future selection; for tied counts, sorted lexical IDs do too, because all future IDs follow processed IDs.

**Correctness.** Induction on the processed action prefix establishes that each table value is the best selection producing its partition tuple. Each subset of the next prefix either skips or takes the next action, precisely the two transitions. State sufficiency justifies dominance. Final filtering is exactly profile reachability. Thus the returned selection is the oracle optimum, including its deterministic tie rule, over this recognized class. The selected repair is replayed through the geometry/topology/path verifier as an implementation check.

## Bound and limits

Let n_p be retained baseline components for profile p, N=sum n_p, k actions, and L the total number of profile-edge activations. There are at most S=product Bell(n_p) partition tuples. A straightforward canonical union costs O(N) per activation. With tuple witnesses, a conservative bound is O((k+L) S N + k^2 S) operations and O((N+k) S) live storage, excluding validation and exact-number bit costs. This is fixed-parameter tractable in N, not in the number of portals alone. Component and state caps stop oversized requests with named limit errors; they never convert unfinished search into infeasibility.

The implementation keeps complete contracted graphs rather than forgetting vertices along a floor sweep. It therefore proves no bound in floor-interface width, offers no rank-based compression, and produces no independent scalable optimality certificate. A DP status relies on this recurrence; exhaustive certificates remain available only for small instances. A later frontier algorithm needs additional proofs about forgotten obligations and live action commitments.

## Prior-work boundary

Connectivity partitions are established DP machinery. Bodlaender, Cygan, Kratsch and Nederlof describe representative families of weighted partitions for connectivity problems in their [primary preprint abstract](https://arxiv.org/abs/1211.1505); this checkpoint inspects the abstract, not the full proof or a transferable theorem. Their result prevents presenting the state representation itself as novel. This implementation adapts elementary partition enumeration to shared-cost, profile-specific activation bundles. Whether equivalent labelled or simultaneous network-design results already cover the exact class remains open. The standard independent single-profile case is already network design.

## Required verification

Compare small supported microcases and seeded bundles against complete enumeration, including selected IDs. Include a path requiring two individually insufficient actions, a shared action affecting two profiles, overlapping bundles, physical activations, empty obligations, zero-cost ties, scope rejection and resource limits. A many-action check on few components establishes action-count independence, not a published scaling advantage. Record manifests for any timing experiment and preregister its family before collecting measurements.
