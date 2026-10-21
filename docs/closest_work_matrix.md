# Focused formulation comparison

Rechecked primary full texts on 21 October 2026, within the fixed project
direction. The findings below concern the indicated formulations and guarantees;
they are not an exhaustive priority certificate. Geometry recognition precedes
all graph encodings here. Expressibility, applicability and comparable guarantees
are separate questions.

| Reference | Input / purchases / demands | Resources / decomposition / objective | Guarantee and parameter | Relationship and precise support |
|---|---|---|---|---|
| [Bergougnoux, Dreier, Jaffke, A logic-based algorithmic meta-theorem for mim-width, v2](https://arxiv.org/pdf/2202.13335v2) | Typed weighted graph and fixed A&C distance-neighborhood formula; our Action/Usage/Cell/Occurrence encoding represents complete purchases and separate profile demands | Our encoding supplies owner/cell exclusions and an expression; optimize membership-pattern weights; no building recognizer in source | Theorem 1.2, manuscript p.6: for distance one, single-exponential clique-width dependence for fixed formula; weighted definitions pp.11–12 | Expresses: yes, by project reduction in `modern_connectivity_comparison.md`. Applies: yes with supplied expression. Same guarantee: exactness, yes; identical parameter bound, not shown. Explicit Boolean Usage transfer has linear owner term, whereas finite-domain construction has log domain term. This is comparison of upper bounds, not a generic-method lower bound. |
| [Bodlaender, Cygan, Kratsch, Nederlof, deterministic connectivity algorithms, accepted manuscript](https://pure.tue.nl/ws/portalfiles/portal/57608658/journaldeterministic_complete.pdf) | Weighted partitions representing partial connectivity; source applications include Steiner Tree | Supplied decomposition; original applications do not supply our paid-action ownership model; additive weighted optimization | Definition 3.2 project, Proposition 3.3, Lemma 3.6 and Theorem 3.7, manuscript pp.10–11; application forget recurrence p.12; proof section3.6 pp.19–22 | Expresses full model directly: no standalone formulation. Machinery applies after our construction and resource grouping. Provides the representative-set guarantee we use. Vertex deletion rejecting vanished blocks is prior project machinery, not our invention. Our responsibility is the correct schedule and full-occupancy/exact-label transfer. |
| [Wu et al., Connectivity problems on heterogeneous graphs, 2019](https://link.springer.com/article/10.1186/s13015-019-0141-z) | Condition graphs on common vertices; buy underlying edges once; condition-indexed endpoint demands | No physical owner/cell exclusions or indivisible disconnected effect bundle in Definition1; nonnegative edge weight; no owned floor decomposition | Definition1 CSN, Definition4 CST; ILP section gives shared edge activation with condition-specific routing. Approximation/hardness guarantees concern condition-network inputs | Expresses our edge-only permission subcase: yes. Full action/resource model directly: no. Their ILP ideas apply to our flow baseline after added variables/constraints. Their results do not by themselves establish our declared interface bound. Profile-dependent access and shared payment are therefore not standalone new ideas. |
| [Kakimura et al., Simultaneous Network Design with Restricted Link Usage, preprint v1](https://arxiv.org/pdf/2507.09426) | Colored edges/arcs bought once; each color must connect terminals; superset and exact variants distinguished | Color permissions may overlap; no owner cells or atomic multi-edge purchases in stated input; costs on edges/arcs | Formulations pp.1–2, Table1 p.4; Theorems3.4–3.7 give algorithms by multicolored-link count / restricted classes | Expresses a permission/shared-edge subcase: yes, using superset variant. Full repair directly: no. Restricted algorithms require their stated assumptions, not merely a floor order. Different parameters prevent claiming our bound stronger. Exact-path restrictions must not be substituted for our reachability objective. |
| [Cornet, Laforest, Steiner Tree with Conflicts, 2017](https://dmtcs.episciences.org/4154/pdf) | Support graph, terminal connectivity and a conflict graph on selected vertices | Forbidden vertex pairs; stretch measures conflict locality. No original-action bundle payment or profile-layer ownership construction in the stated problem | Introduction model and stretch; section4 Steiner formulation and Theorem7 proof, printed p.10; results include restricted-case hardness | Directly expresses our full model: not established. Pairwise conflicts alone do not encode disconnected effects through a purchase vertex without creating false routes. Source hardness does not transfer to our restricted geometric class without a reduction. No equivalent owned-interface guarantee follows from the cited theorem. |

## Positive distinction and remaining priority question

The supported distinction is an explicit route from the recognized strict
physical model to a complete-unit DP: pay each original action once, retain all
paid occupancy, and select profile-specific thin witnesses separately. The
generic logic encoding can express those same selections. A generic finite-domain
connectivity DP supplied with the same schedule and rank machinery can match the
owner-domain factor (`generic_state_comparison.md`). Consequently the paper must
not sell model expressibility, representative reduction or logarithmic resource
domains as an exclusive capability.

Asynchronous retirement adds a model-specific correctness obligation: deleting
a vertex after its last incident route event does not authorize deleting its
paid occupancy or erasing the owner token before complete-unit closure. The
underlying last-use/project technique is standard. The complete physical
construction and its proof are the contribution being assessed; its priority
remains unconfirmed. This matrix does not certify that every relevant earlier
paper lacks an equivalent construction.
