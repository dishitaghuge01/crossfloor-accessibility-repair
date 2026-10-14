# M03: the current activation solver is labelled network design

14 October 2026. **The M02 activation-only class cannot establish novelty of the optimization formulation through profile sharing or action bundles.** The reduction below is project analysis, independently tested in software; it is not a new algorithmic theorem. The broader geometry-constrained repair problem remains provisional.

## Primary evidence inspected

- Hassin, Monnot and Segev, *Approximation Algorithms and Hardness Results for Labeled Connectivity Problems*, Journal of Combinatorial Optimization 14(4), 437–453 (2007), DOI [10.1007/s10878-007-9044-x](https://doi.org/10.1007/s10878-007-9044-x). The [author-uploaded manuscript](https://www.researchgate.net/publication/48445000_Approximation_Algorithms_and_Hardness_Results_for_Labeled_Connectivity_Problems), uploaded by Monnot, was read at its introduction and section 6, manuscript p. 14. It defines nonnegative costs on labels that purchase classes of edges together, and explicitly describes minimum-label Steiner forest with prescribed terminal pairs. This is a formulation-level comparison, not an audit or transfer of its approximation proof. Final typeset page reconciliation is not claimed.
- Wu, Khodaverdian, Weitz and Yosef, *Connectivity problems on heterogeneous graphs*, Algorithms for Molecular Biology 14, 4 (2019), DOI [10.1186/s13015-019-0141-z](https://link.springer.com/article/10.1186/s13015-019-0141-z). Full publisher HTML Definition 1, condition-problem section and flow formulation were inspected. Condition Steiner Network uses condition-specific edge availability and terminal-pair demands with shared edge costs. Arbitrary bundled actions are not represented directly by one ordinary costed edge in that definition.
- Kakimura, Madarasi, Matuschke and Varga, *Simultaneous Network Design With Restricted Link Usage*, Networks (2026), DOI [10.1002/net.70059](https://onlinelibrary.wiley.com/doi/10.1002/net.70059). Published HTML sections 1, 1.2 and the full proof of Theorem 3.4 were inspected. The undirected superset variant requires a path inside each availability class; it does not require the chosen subgraph itself to be a path. Theorem 3.4 guesses multi-colored edges and completes with per-color shortest paths. Neither this single-edge result nor its parameter bound automatically transfers to arbitrary bundles or multiple same-profile terminal demands.

## Exact compilation of the M02 class

Assume the recognized M02 scope: fixed rooms; independent activation-only actions; no dependencies/exclusions; the complete action union passes strict geometry. Therefore geometry and A-preservation impose no further subset-dependent restriction. Keep the evidence types as provenance, but both types contribute activations to the optimization graph.

1. For every profile p, compute the connected components of its baseline access graph. Create a **separate** vertex `(p,C)` for every such component C. Never identify vertices across profiles, even when they contain the same room.
2. For each action a, each of its activated connections uv, and each permitted profile p, add an edge from `(p,C(u))` to `(p,C(v))` with label a. Parallel edge copies represent overlapping actions; selecting either activates that route. Edges internal to a baseline component are unnecessary for connectivity.
3. Give label a cost c(a), paid once across all copies and all profile layers. Thus profile coupling lives in shared labels, without allowing travelers to switch profile layers.
4. Map each obligation `(s,t,p)` to the terminal pair `((p,C(s)),(p,C(t)))`. Already-satisfied pairs have equal endpoints and require no selected edge.
5. A label with no remaining nonloop edge can be omitted when considering minimum cost. To preserve every original selection, including redundant zero-cost actions, the executable adapter instead attaches that label to a private isolated dummy edge, with no demands on its endpoints. This edge cannot affect obligation reachability.

**Subset correspondence.** Select action set R and precisely its labels. The activated graph in each profile is the quotient of that repaired profile graph by baseline components. Quotienting pre-existing connected components preserves connectivity of all room pairs. Parallel copies and dummy components change no reachability. Consequently all repaired obligations hold iff all translated terminal pairs connect. Costs agree exactly because both pay once per selected action/label. This holds for every subset, not just the optimum. All subsets meet strict topology/geometry by the recognition assumptions. The compiler is polynomial in rooms, profiles and activated profile-edge incidences.

**Input conventions.** The layered labelled graph may be disconnected. If a formulation insists that the full input graph be connected, add a new label z of cost M=1+sum_a c(a) on a chain joining all original vertices. Any original feasible repair costs less than M; any solution using z costs at least M. Solving that connected instance and testing whether the optimum is less than M exactly detects original feasibility and recovers its optimum when feasible. The executable comparison uses the disconnected graph directly. The auxiliary z is a mathematical encoding device, never a physical intervention.

The generic prior objective proves equality of minimum **cost**. The repository's action-count/lexical tie rule is an additional deterministic convention; the adapter evaluates it explicitly rather than assuming prior approximation algorithms enforce it.

## What this rules out

- Multiple mobility profiles alone do not make the M02 combinatorial problem new: separate layers encode their permissions and shared labels encode one-charge bundles.
- Distinguishing physical and representation actions is essential evidence semantics, but after geometry is prevalidated it does not alter this optimizer's combinatorial class.
- The star hardness argument and elementary partition DP remain useful implementation baselines; they are not sufficient originality evidence.
- A geometry verifier or benchmark may support an application contribution, but that claim still requires an explicit method comparison and public-data evidence. It is not an established algorithmic novelty claim.

## Limits and next research target

This compilation does not eliminate subset-dependent geometry conflicts, action implications/exclusions, geometry modifications or continuous candidate generation. Plain labelled Steiner forest is monotone in selected labels; dependencies/conflicts can destroy that property. However, finding this distinction is **not** proof of novelty: forbidden-pair paths, conflict-constrained network design and bounded-width constraint/connectivity algorithms must be compared before claiming a new result.

The next focused class is strict, fixed-geometry activation with explicitly certified candidate incompatibilities and local physical bundles. First establish whether the current geometric kernel admits a sound and complete unary/pairwise conflict compilation. Then audit existing constrained-labelled connectivity and structural algorithms. A floor-frontier algorithm would need a parameter including live actions, demands and conflicts; simply renaming graph width as portal width is inadequate. No general solver is started until those assumptions and state sufficiency are proved.

**Gate decision:** G0's named architectural distinction remains supported. G0's algorithmic novelty route for the M02 activation-only formulation is closed by this cost-preserving encoding. G3 stays OPEN. No overall thesis-novelty claim has been established.
