# Why generic constraint width is not a new floor-interface result

14 October 2026. This checkpoint is an explicit feasibility encoding and prior-work boundary, not a new algorithm. The subsequent [M11 resource-incidence comparison](resource_incidence_comparison.md) supplies a concrete compact decomposition and weighted objective transfer for the recognized M09/M10 subclass; it does not automatically extend that decomposition to this more general dependency/exclusion model.

## Relational encoding

After fixed-geometry activation constraints are compiled, construct a finite structure with three unary object types: Action, Vertex and Edge.

- A Vertex is a separate room/profile copy. Thus a route cannot switch profiles.
- An Edge is a connection/profile copy, with binary Incidence to its two endpoint Vertices. Mark Baseline edges that already exist in that profile's access graph.
- Covers(a,e) means action a activates edge e. Overlapping actions may cover the same Edge; a bundle may cover many Edges. Action weights remain attached once to a.
- Demand(u,v) is the binary relation containing all profile-specific obligation endpoint pairs.
- Unavailable(a) records unary geometric failures. Conflict(a,b) includes compiled geometric conflicts and declared exclusions. Requires(a,b) records action implications.

Let X be a selected set of Action objects. An Edge e is active iff Baseline(e) or some a in X has Covers(a,e). Feasible selection is expressed by:

1. Every member of X is an available Action.
2. For every Requires(a,b), membership of a in X implies membership of b in X.
3. For every Conflict(a,b), a and b are not both in X.
4. For every Demand(s,t) and every set Z of Vertex objects with s in Z and t outside Z, some active Edge has one incident endpoint in Z and one outside Z.

This is one fixed monadic second-order formula over the structure: X and Z are set variables, and all remaining quantifiers range over individual objects. It does not need one separate formula variable per profile or obligation. Condition 4 is the usual undirected cut characterization of reachability: if disconnected, take Z as the component containing s; if connected, any such cut meets an s–t path. Thus the formula is true exactly when a geometry/constraint-admissible repair meets all obligations, within the compiled kernel's scope.

## Width that actually matters

The structure's Gaifman graph connects objects that occur together in a relation: room/profile vertices to candidate edge objects; actions to covered edge objects; obligation endpoints to one another; and actions related by conflicts/dependencies. A floor decomposition must control **all** these incidences, not only portal vertices.

Existing bounded-treewidth MSO-on-structures machinery already covers fixed-formula feasibility at bounded width. Bodlaender/Jansen/Kratsch's [preprint](https://pure.tue.nl/ws/portalfiles/portal/48172370/1106.4141v2), manuscript p. 24/Proposition 6, uses the analogous relational approach for forbidden-pair paths. German's [Appendix 0.B](https://arxiv.org/html/2605.12457v1) writes the cut formulation and Gaifman-graph argument explicitly. Our extension to these action/edge/demand relations is a project encoding, not a new general logic theorem.

This checkpoint does **not** prove a concrete Bell-number frontier recurrence, transfer a weighted MSO runtime, obtain a practical solver, or bound Gaifman width by portal count. Numeric weighted optimization and witness tie-breaking require an appropriate optimization theorem or explicit DP. An implementation that only materializes this known bounded-width machinery would be an adaptation, with novelty still to be justified.

## Remaining useful question

Does a physically justified restriction on vertical assets, reserved alternatives, access graphs, demands and bundle spans yield a width/parameter bound substantially sharper than generic relational width, or another independently new result? Any positive answer needs a concrete decomposition and proof, with counterexamples outside scope. Until then, a claimed floor-interface FPT algorithm is premature.
