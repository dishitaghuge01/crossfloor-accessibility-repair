# M16: exact modern connectivity baseline and genuine owner competition

## Correcting a concrete model error

M11's generic encoding selected an Asset object whenever any action used it, then reserved its complete catalogue cell set. That overstates occupancy if two actions using one owner expose different floor portions. M13/M15 already use action-specific footprint floors and are unaffected. The corrected [resource encoding](resource_incidence_comparison.md) has one Usage object per (owner,cell). An action selects only the usages of its own full effects. Same-owner reuse at a cell shares its unique Usage object; other owners give different usages at that cell.

`src/cfar/resource_logic.py` compiles this graph and evaluates selections using cell-neighbor counts and separate graph traversal. It does not invoke the owned-interface DP or its representative rows. It shares the physical recognizer, so it is an independent encoding/graph check within that recognized geometry contract, not an independent geometry engine.

## A fixed published-logic formulation

Use unary types Action, Usage, Cell, Vertex, Occurrence and Hub. Edges join Action to its used Usage objects, Usage to its one Cell, Action to its supplied Occurrences, and Occurrence to its two profile-layer endpoint Vertices. Add one artificial Hub adjacent to each actual profile anchor. Mark Target, Anchor and Baseline as unary sets. Profile vertices remain disjoint; the Hub is a proof device, not a physical route or permission to switch profiles.

Write N(X) for ordinary open neighborhood and N_2(X) for vertices with at least two neighbors in X. With selected action set X, selected usage set Z and route witness set Y, the fixed formula is:

```
X subset Action
Z = Usage intersect N(X)
Cell intersect N_2(Z) = empty
Y subset (Vertex union Occurrence union Hub)
(Target union Anchor union Hub) subset Y
(Y intersect Occurrence) subset (Baseline union N(X))
(Vertex intersect N(Y intersect Occurrence)) subset Y
con(Y)
```

These are neighborhood terms, set comparisons and one induced-connectivity predicate. Formula length is constant, distance radius is one, neighbor-count threshold is two, and no variable size measurement is needed. The p profiles and all targets are encoded in graph objects/unary marks, rather than extra formula variables. Unknown/unary-blocked actions are excluded before this graph construction.

**Subset equivalence.** Selected usages impose exactly the recognized cell conflicts, preserving same-owner co-use and full action occupancy. Every occurrence in Y is baseline or supplied by a paid action; its two endpoints belong to Y. Actions/usages/cells are excluded from Y, so a purchase vertex cannot invent a route between disconnected components of one atomic bundle. Paths from a target to the Hub must reach its own layer anchor, because that layer has no other exit. Conversely, take each profile's materialized root component, its active occurrences and the Hub: these form a valid Y whenever obligations hold. Thus this fixed formula preserves admissibility and reachability for every original selection, and charges each original action once.

## Primary algorithm and precise transferred bound

[Bergougnoux, Dreier and Jaffke, full version v2](https://arxiv.org/pdf/2202.13335), manuscript dated December 9, 2022, supplies weighted A&C distance-neighborhood optimization. Inspected locators: sections 1.1 and 3 syntax; Theorem 1.2, manuscript p. 6; weighted graph definition pp. 11–12; Table 1; Theorem 4.5 framework. For constant distance-one formula its stated clique-width running time is single-exponential. Its weighted definition permits a nonnegative weight for each vertex/membership pattern. The tree-width A&C entry in Table 1 is quadratic in width; do not confuse it with the linear-width DN entry without induced connectivity.

The corrected resource graph has a supplied path decomposition with bag size `prL+zL+p+zLh+2`, plus one permanently retained Hub when using this formula. Convert its event order into a linear clique-width expression: keep each live object in its own label; introduce a fresh singleton, join it to precisely its already introduced neighbors by their singleton labels, then retire an object to a finished label once it has no future incident relation. No later join addresses finished labels. Constantly many finished labels can preserve unary type signatures if needed. This gives O(prL+zL+p+zLh) labels and a polynomial-size supplied expression. This conversion is a project construction, not a statement quoted from the paper.

Transfer M11's polynomial-bit integer objective w_i by assigning weight w_i to an Action vertex when it is **outside X**, and zero when it is in X; all other vertices have weight zero. The source's permitted nonnegative membership weights then maximize `sum_i w_i - sum_(i in X) w_i`, exactly minimizing original cost/count/IDs. No negative weights or global ordering relation are required.

Combining this expression, fixed formula and published weighted algorithm gives a direct generic baseline bound

`recognition_time + 2^O(prL + zL + p + zLh) * polynomial(input_bit_size)`.

For recognized nonempty rooted profiles, p<=prL and h>=1 when candidates are present. Compare this explicit transfer with M14's proposed

`recognition_time + 2^O(prL + zL log(h+2)) * polynomial(input_bit_size)`.

This is now a concrete algorithm-bound comparison rather than comparing against an unspecified MSO function. For fixed h the expressions have the same asymptotic interface exponent. For variable h the displayed specialized bound is sharper than this particular transferred upper bound. It does **not** prove a lower bound for all generic algorithms, rule out a narrower expression, or establish literature priority. Keep the physical-interface direction active and investigate that precise variable-h gap.

## Inputs that test the distinction

`coupled_owner_probe(t)` uses four frozen floors. For each owner i, action L_i installs its edge 0 and a disjoint shared bridge edge 2; M_i activates edge 1 using that same owner. L_i actions all reference the bridge, so all 2t actions belong to one unit. Each action individually is geometrically feasible. Alternative owners overlap in one footprint; L_i+M_i can share it, whereas cross-owner choices collide. A complete route needs one L_i and one M_i. Nonnegative unit costs give optimum two, with lexical witness L000+M000.

Measured p=1,r=1,z=2,L=4 remain fixed, while g=t+1 and h=t grow. This is a genuine within-unit owner family; the earlier 64 private alternatives instead have h=1. It supports an O(log t) versus O(t) comparison of the **displayed exponential parameter terms**, with polynomial input/recognition work retained. It is not a runtime separation experiment or a lower bound.

`branching_rooms_probe()` supplies two floors, two profiles and two upstairs destinations. An existing door contracts two rooms only in profile zero; baseline lift access exists in both profiles. New disjoint lifts can be purchased as a cost-three atomic bundle or separately for total cost four. Recognition measures p=2,r=3,z=2,L=2,g=2,h=1. Both DP modes and the oracle select the bundle. This finally exercises multiple within-floor components, profile-specific baseline contraction and multiple rooted destinations together.

Twelve tests compare the corrected logic evaluator with all oracle selections on the five original probes, t=2,3,4 owner families and the room-branching case. They also detect purchase-vertex shortcuts and action-specific occupancy. An exact scalar-weight check orders all subsets by fractional/huge-integer cost, then count, then IDs and compares that order with the nonnegative unselected-membership reward. The graph compiler records these weights; it still does not run the published optimizer. These finite checks strengthen semantics; they do not establish originality. G3 remains OPEN, with an explicit surviving variable-h result to audit rather than a closed direction.
