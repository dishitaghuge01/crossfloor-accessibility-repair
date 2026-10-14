# Novelty claim registry

Updated 14 October 2026. **Novelty is not established.** This registry records falsifiable claims; it is not a promise that some claim will pass.

| Candidate claim | Current evidence | Decision |
| --- | --- | --- |
| First repair of multi-floor architectural layouts | Five named architectural methods inspected, but the broad literature contains repair/analysis/generation contributions | Do not claim first or universal absence. |
| New minimum-cost formulation because actions bundle transitions and profiles | Explicit cost-preserving compilation into weighted labelled Steiner forest; subset-level executable witness | Ruled out for M02's jointly feasible activation class. |
| Novel exact solver using profile connectivity partitions | Established partition-DP machinery; M02 proof and oracle comparisons validate an adaptation | Do not claim algorithmic novelty. |
| New optimization class because candidates collide geometrically | Current 2D kernel compiles into unavailable labels, forbidden label pairs and action implications | Distinction from plain monotone labels exists; novelty remains open against constrained-network prior work. |
| New FPT result from bounded floor/portal interfaces | No proved floor-frontier state yet; union/constraint-width MSO and forbidden-pair results already exist | Open; must bound action, demand and conflict incidence and show a contribution beyond a generic width result. |
| New reproducible, evidence-typed BIM repair benchmark and verification pipeline | Controlled schema, graph/geometry replay and exhaustive certificates exist; no public BIM evaluation yet | Potential application/method contribution, unestablished. |

## What would support a positive decision

Before saying novelty is established, write a precise claim and assumptions, identify the closest applicable theory and architectural methods, and explain a demonstrated difference in result or method. A proposed algorithm requires a sufficient-state/correctness proof and reproducible comparisons beyond trivial enumeration. A benchmark/pipeline claim requires licensed public inputs, authenticated baseline evidence, documented extraction/corruption procedures and comparative evaluation. Respect the master plan's requirement for a substantive algorithmic result; an application reinterpretation alone does not pass that gate.

Positive novelty evidence is scoped and provisional: a literature audit cannot guarantee that no unlocated work exists, and neither a passing test suite nor a paper title establishes originality. The user must be told the precise supported claim and remaining uncertainty.

## Next focused work

1. Finish the direct constrained-labelled connectivity audit, especially edge/label forbidden-pair models with shared costs and multiple demands; the choice-network paper currently has excerpts only.
2. Extend the completed [relational feasibility encoding](constraint_width_boundary.md) with an audited weighted-optimization argument and compare any proposed floor decomposition with known constraint-width methods. Record demand/action/conflict lifetimes explicitly.
3. Test whether physically local bundles/reserved portal alternatives impose a stronger structure that admits a useful result not already obtained by the generic encoding. Do not add arbitrary constraints merely to manufacture a difference.
4. If no substantive algorithmic gap survives, report that finding and reassess the candidate against the user's thesis gate instead of relabelling an existing algorithm as novel.

See [network-design equivalence](network_design_equivalence.md) and [geometric conflict compilation](geometry_conflict_compilation.md) for the completed proofs and their exact limits.
