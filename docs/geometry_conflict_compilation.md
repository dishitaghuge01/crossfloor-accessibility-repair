# Fixed-geometry constraint compilation checkpoint

14 October 2026. This is a proof about the implemented reserved_interfaces_2d_v1 kernel, not general architectural geometry or a novelty claim.

## Scope and proposition

Validate the instance, retain original room polygons and obstacles, and require every action effect to be activate_connection. Representation and physical evidence contracts remain validated. Unlike M02, dependencies, declared exclusions, individually invalid candidates and mutually incompatible candidates are allowed in the catalogue.

Let B be baseline activations. For each action a, test joint_geometry(B union effects(a)); a failure makes a unavailable. For each pair of individually available actions a,b, test joint_geometry(B union effects(a) union effects(b)); a failure creates a forbidden pair. Keep action implications and declared exclusions as separate Boolean constraints.

**Proposition (current kernel only).** A selected activation set passes the strict geometry kernel iff it contains no unavailable action and no compiled forbidden pair. Including the explicit implication/exclusion constraints makes selection admissibility equivalent to apply_actions for SCFAR. Reachability is a separate requirement and is not part of this proposition.

**Proof.** Baseline geometry passes validation. The room shapes, obstacles, profile widths, connection geometry and asset identifiers never change with selection. Inspect each predicate in joint_geometry:

1. Connection containment, wall contact, reservation, footprint, rise/run, obstacle and endpoint predicates depend on that connection's fixed record. Profile width/clearance/stairs/slope predicates are conjunctions of independent tests for each permitted profile. Every activated connection/profile pair comes from B or at least one selected action, so a violated single-connection predicate has a baseline or one-action witness.
2. Door-opening collisions and distinct portal-asset overlap are tested on pairs of connection records. If two offending records come from the same action, its unary test fails; if from different actions, their pair test fails; collisions with B appear in unary tests. Repeated activation of one connection is a set union, not a collision with itself.
3. The room/profile centre-space is computed solely from the fixed room, fixed obstacles and profile width. Which room/profile pairs are requested is the union of baseline/obligation requests and selected-effect requests. A failure is baseline-wide or introduced by one action. Landing-centre tests likewise concern one fixed connection/profile endpoint. Selected portal envelopes do **not** become new obstacles in this kernel.

Thus every possible geometry failure has a witness using at most two selected actions. Conversely a witnessed unary or pair failure persists after further activations because all relevant geometry is fixed and tests are conjunctive. Those are exactly the compiled constraints. Identity and A-preservation are automatic for activation-only effects, and apply_actions adds precisely the recorded dependency/exclusion tests. This proves the stated equivalence.

With k actions, compilation makes at most 1+k+k(k-1)/2 geometry calls, including a baseline check, each with at most the baseline plus two action bundles. Store the original named failure codes and input fingerprint. The compiler has an explicit action-count guard and does not optimize or certify a final solution. The graph/constraints representation must be replayed against the input before a final repair claim.

## Important failure boundary

This proof stops applying if installed equipment becomes an obstacle, footprints/rooms move, candidate geometry depends on previously selected edits, or continuous clearance is tested through the union of interventions. Three individually/pairwise harmless obstacles can collectively disconnect motion space in a richer model. Polygon-replacement effects are rejected; dependency effects do not secretly change geometry.

The result therefore narrows the potential algorithmic gap: **current geometric validity is a unary/pairwise incompatibility system on labels, not arbitrary continuous geometric optimization.** An exact solver for it would be constrained labelled connectivity. Merely adding conflict bits to a partition DP would not establish novelty.

## Prior-work audit status

- Kolman and Pangrac, [author-hosted 2009 manuscript](https://kam.mff.cuni.cz/~kolman/papers/fpath3.pdf), *On the Complexity of Paths Avoiding Forbidden Pairs*: abstract and introductory definition inspected. It already studies paths with incompatible vertex pairs; its directed/DAG structure and single-path objective are not automatically the bundled undirected multi-demand repair class.
- German, [arXiv:2605.12457v1](https://arxiv.org/html/2605.12457v1), *Layer-Based Width for PAFP* (2026): definitions, background and Appendix 0.B relational formulation inspected. It explicitly places forbidden-pair constraints in a union/constraint graph for bounded-width reasoning. Its directed BFS-layer results are not floor-layer results.
- Bodlaender/Jansen/Kratsch, *Kernel bounds for path and cycle problems* (2013), [institutional preprint arXiv:1106.4141v2](https://pure.tue.nl/ws/portalfiles/portal/48172370/1106.4141v2), manuscript pp. 23–25, Proposition 6 and Theorem 10 proof inspected. It already derives bounded union-graph treewidth tractability via relational MSO and guesses a cover of forbidden-pair vertices for shortest paths. These single-path results do not directly prove the bundled multi-demand case; generic constraint-width reasoning is nonetheless established prior machinery.
- Wojciechowski, Subramani and Velasquez, *Reachability in choice networks*, Discrete Optimization 48, Part 1, 100761 (2023), DOI [10.1016/j.disopt.2023.100761](https://www.sciencedirect.com/science/article/pii/S1572528623000038): publisher-indexed definition/introduction/principal-results excerpts only. Edge-pair constraints and pathwidth claims make it a required comparator, but full proof access remains unaudited.

The application/evidence pipeline remains worth testing, but a new algorithmic result must survive these comparisons. No novelty decision has passed.
