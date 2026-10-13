# M01.1: closest-work comparison and evidence ledger

Reviewed 14 October 2026. **The five named architectural comparisons now have full-text method evidence**, including PlanFix's 63-page preprint. No inspected architectural method establishes the complete SCFAR contract with equivalent guarantees. **G0 remains conditional on a broader algorithmic-equivalence audit**, not a missing named paper. This supports continuing formal algorithm research, not a universal novelty claim or a final thesis decision. The active candidate remains Cross-Floor Accessibility Repair; no rejected candidate is reactivated.

## Comparison contract

SCFAR takes authored, frozen floors, distinguishes shared-boundary adjacency A from traversable access D, and selects costed, evidence-typed actions to satisfy profile-specific cross-floor obligations. It preserves original room identities and A exactly. RCFAR permits declared topology changes and reports Delta_A separately. Evidence for reachability, geometry, optimality, and original-design recovery remains separate.

Evidence labels below:

- **Method inspected:** relevant full-text method and guarantee sections inspected; does not mean every appendix or implementation was audited.
- **Partial:** abstract, publisher excerpts, or bibliographic record only; unknown features cannot be marked absent.
- **Not established:** the inspected sections do not establish this property; this is narrower than claiming the work cannot support it.

## Architectural comparators

| Work / evidence | Input and operation | Cross-floor / profiles | Topology and geometry | Objective / guarantees | Relationship to SCFAR |
| --- | --- | --- | --- | --- | --- |
| MANSION, Che et al., CVPR 2026; final method and supplement D inspected | Generates room partitions; later object placement/removal for task preconditions | Explicit vertical cores and simulator transitions; SCFAR mobility-profile obligations not established | Target bubble graph conditions generation; editing tool cards manipulate scene objects | Candidate energy ranking; minimum architectural intervention cost or repair bound not established | Generation and scene task editing are both compared. |
| EPSAP, Rodrigues et al., 2013; author-manuscript method and Appendix A inspected in thesis RP3 | Evolves room polygons/openings and parametric stairs/lifts | Multi-level design; SCFAR profile obligations not established | Geometry, stair positions and adjacent room shapes change; topology swap/dissection operators are described | Weighted feasibility penalties and evolutionary/local search; global repair bound not established | Does not impose the frozen-polygon SCFAR contract in inspected formulation. |
| PlanFix, Trinh et al., SSRN 7275102; full method/guarantees inspected | Post-hoc repair of mutable room geometry | Global accessibility routing outside stated projector scope | Translates/scales polygons; adjacency projector aligns shared boundaries | Squared-displacement objective; proven energy monotonicity, without general feasibility/global-minimum guarantee | Direct geometric-repair comparator, with a different decision space and guarantee contract. |
| Al-Harasis and Jabi, DFBI 2026, pp. 45-54; method inspected | IFC-derived door graph; evaluation-only area/edge alignment and synthetic programme completion | Profile-specific cross-floor repair not established | Door-based adjacency is access, not SCFAR shared-boundary A; synthetic graph edits need not have IFC geometry | Benchmark alignment plus GNN evaluation; minimum-cost selection or optimality bound not established | Concrete method-level distinction: graph evaluation/completion versus physically certified repair. |
| Bayraktar Sari and Jabi, Architecture 6(2), 76, 2026; author-uploaded journal method inspected | Revit/Dynamo/AVA spatial graph analysis | Existing BIM stairs, ramps and lifts incorporated as graph links | Geometry tagging and grid sampling; vertical facilities are not separately redesigned | Metric/topological shortest paths and spatial measures; minimum architectural repair selection not established | Analysis distinction is now method-supported, rather than abstract-only. |

### Source locators and reading notes

**MANSION.** [Final paper](https://openaccess.thecvf.com/content/CVPR2026/papers/Che_MANSION_Multi-floor_lANguage-to-3D_Scene_generatIOn_for_loNg-horizon_tasks_CVPR_2026_paper.pdf); [final supplement](https://openaccess.thecvf.com/content/CVPR2026/supplemental/Che_MANSION_Multi-floor_lANguage-to-3D_CVPR_2026_supplemental.pdf); [arXiv v1](https://arxiv.org/html/2603.11554v1). Final sections 3.1-3.2, pp. 37177-37179, retain generation and scene-task editing. Supplement D.2, PDF pp. 9-10, specifies CheckPath and object placement/removal tools; F.1 describes floor-transition skills. These do not establish minimum-cost selection of architectural portal/door interventions. Relevant method scope agrees with the earlier v1 reading; this is not a byte-level reconciliation of every result or reference.

**EPSAP.** [Publisher article](https://www.sciencedirect.com/science/article/pii/S0926580513001027), DOI 10.1016/j.autcon.2013.06.005; [institutional author thesis](https://hdl.handle.net/10316/25438). Thesis Appendix C identifies RP3 and its DOI on PDF p. 209; the included manuscript is dated 28 May 2013. Sections 2.1-2.4, PDF pp. 213-217, describe mutable room and vertical-facility geometry, weighted penalties, and transformation operators. Appendix A, PDF pp. 227-230, supplies connectivity/adjacency, overlap, dimensions and area evaluators. These support a method-level generation distinction. Publisher excerpts agree with that scope; exact agreement with the final typeset equations remains unaudited. The earlier CiteSeer access failure was resolved through the university repository.

**PlanFix.** [SSRN record and download](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7275102), DOI 10.2139/ssrn.7275102. Browser access resolved the earlier HTTP 403 failures; the complete 63-page preprint was retrieved. Sections 3.1-3.2, pp. 10-12, formulate squared geometric displacement and distinguish energy convergence from feasibility. Sections 3.4-3.7, pp. 13-18, describe geometric projectors and the trust-region loop; adjacency uses translation/snap and egress uses learned displacement. Appendix A, p. 33, explicitly does not prove convergence to a global minimizer. Section 6, pp. 30-31, excludes global egress/accessibility routing from current projector scope. Section 4.1 and Appendix D.9-D.10 compare geometric optimization baselines. None of these establish frozen-floor, profile-specific, typed-subset cross-floor repair with SCFAR guarantees. The formal minimum-modification objective alone is not an optimality certificate.

**Al-Harasis and Jabi.** [Published full text](https://submission.dfbi.org/index.php/dfbi/article/download/26347/35/797); [ORCA record](https://orca.cardiff.ac.uk/id/eprint/186310/), DOI 10.66408/dfbi.2026.26347. Sections 3.1-3.2, pp. 48-49, extract an openings-only graph. Sections 3.5-3.7, p. 49, align areas/edges and add programme nodes. Sections 4.5 and 5.4, pp. 51-52, distinguish synthetic evaluation graphs from physical IFC elements. This supports a limited distinction, not overall novelty. **Bibliographic correction:** the earlier search snapshot associated eCAADe DOI 10.52842/conf.ecaade.2026.1.021 with this title; the current [institutional record](https://orca.cardiff.ac.uk/id/eprint/187075/) identifies a different GA-SA generative-optimization paper. It must not be presented as a same-title version. That adjacent paper is currently abstract-only in this ledger.

**Bayraktar Sari and Jabi.** [Architecture article](https://www.mdpi.com/2673-8945/6/2/76), DOI 10.3390/architecture6020076; [author-uploaded journal full text](https://www.researchgate.net/publication/405171783_A_BIM-Embedded_Computational_Workflow_for_Spatial_Graph_Analysis_of_Architectural_Floor_Plans). Publisher HTML/XML access failed, but the author's uploaded text was available. Sections 3.3-3.5, pp. 8-10, specify obstacle tagging, grid graphs, and existing vertical-circulation links; section 4.4, p. 15, demonstrates a cross-floor stair route. Section 5.4, pp. 20-21, limits validation. These sections support analysis of existing facilities rather than minimum-cost physical repair. The separate Rome presentation was not used as a substitute.

## Algorithmic comparators

| Work / inspected locator | Existing problem and guarantee | SCFAR overlap and transfer limit |
| --- | --- | --- |
| Goemans and Williamson, 1995, constrained forests; cut formulation/algorithm, sections 1-2, pp. 296-299 | Minimum-cost edges covering cuts for proper requirement functions; primal-dual approximation and dual lower bound | Restricted single-profile independent edge additions can match terminal-pair network design. Geometry, coupled actions and profile sharing require separate arguments. |
| Marx and Vegh, arXiv:1304.6593v2; introduction, Theorems 1.1-1.2 | Minimum-cost connectivity augmentation by one under a bound p on added links; FPT and polynomial kernels | Strong comparator for candidate-link selection. Global edge-connectivity targets differ from named profile obligations; kernel transformations need not preserve feasible physical actions. |
| Golovach, arXiv:1308.1802v2; problem definition and stated results, introduction | Edge addition/deletion to achieve connected prescribed degrees; kernel in d+k, FPT in k for connected regular targets | Establishes that connectivity-constrained graph editing has existing parameterized theory. Degree targets differ from floor topology and obligations; results do not automatically transfer. |
| Nederlof, ESA 2016 / arXiv:1608.03439v1; introduction and previous-work section | Existing Set Cover universe-subset DP and faster randomized algorithms for special solution-size regimes | The controlled bundled-star repair DP is an adaptation of established coverage DP, not algorithmic novelty. |

Primary texts: [constrained forests, author-hosted paper](https://math.mit.edu/~goemans/PAPERS/GoemansWilliamson-1995-AGeneralApproximationTechniqueForConstrainedForestProblems.pdf), DOI 10.1137/S0097539793242618; [minimum-cost augmentation full text](https://arxiv.org/html/1304.6593v2); [connected-degree editing full text](https://arxiv.org/pdf/1308.1802). Preprint versions are identified explicitly; theorem transfer requires checking the final versions and assumptions.

Coverage comparator: [Nederlof full text](https://arxiv.org/html/1608.03439v1). Its discussion explicitly places the simple universe-subset dynamic program in prior work. See [complexity memo](complexity_memo.md) for the project's restricted reduction, proof, and claim limits.

The theory rows identify formulations and stated guarantees, not completed proof audits or demonstrated transfers. Extending them to realistic coupled multi-profile repair remains a separate research obligation.

## Implications for the formal gate (project analysis, not a claimed theorem)

1. **Test the network-design reduction first.** For one profile, nonnegative additive costs, independent monotone edge additions, and prevalidated geometry with no joint conflicts, encode existing access as zero-cost edges and candidate additions as costed edges. Requiring terminal pairs to connect gives a Steiner-forest-style formulation. Keep parallel action identities or choose the least-cost equivalent edge where justified. This interpretation needs a formal equivalence proof; it is not new solely because vertices represent rooms.
2. **Coupling must be real.** Shared lift actions can activate multiple transitions/profiles for one charge. Independent per-edge costs may overcount or undercount. Mutually incompatible physical candidates can make individually valid certificates insufficient; verify their union too.
3. **Bounded portal count is not yet a DP theorem.** Arbitrarily many unresolved obligation endpoints, nonlocal coupled actions, and geometry conflicts can survive a floor boundary. State sufficiency must include obligation status and action commitments, or restrict those quantities explicitly. Connectivity partitions alone are a proposal.
4. **Do not equate preserving IFC with preserving A.** Evaluation-only graph edits may leave source files untouched yet introduce relations with no physical realization. SCFAR needs independent A, D, physical evidence, and reachability checks.
5. **Architectural comparison complete; broader novelty unestablished.** The named methods support concrete distinctions, including PlanFix's explicitly narrower routing/guarantee scope. Existing graph optimization may already subsume substantial restrictions of SCFAR. Audit coupled/multi-profile network-design equivalence before a final novelty decision. Exact final EPSAP-equation reconciliation and optional adjacent GA-SA full-text coverage remain recorded limitations.

## Completion ledger

- [x] Read governing repository files and clean baseline; remote HEAD confirmed at aa51926.
- [x] Inspect MANSION generation and task-editing method sections (arXiv v1).
- [x] Inspect mandatory Al-Harasis/Jabi DFBI full text, with page-level method locators and visual check of p. 49.
- [x] Add primary-source constrained-forest, augmentation, and graph-editing comparators.
- [x] Inspect final MANSION method and supplement/tool cards; relevant scope checked against v1.
- [x] Obtain/read EPSAP author-manuscript method and Appendix A in institutional thesis RP3.
- [ ] Reconcile EPSAP author-manuscript equations with final publisher typesetting if accessible.
- [x] Obtain/read PlanFix complete preprint; inspect objective, projectors, guarantees/proof, limitations and baseline comparison appendices.
- [x] Read Architecture 6(2), 76 journal method from the author's uploaded full text.
- [x] Resolve eCAADe bibliographic ambiguity: DOI identifies a different generative GA-SA paper.
- [ ] Optional adjacent-work review: inspect that GA-SA paper's full text, currently abstract-only.
- [x] Reassess the five named architectural methods from full-text evidence; none establishes the entire supplied SCFAR contract with equivalent guarantees.
- [ ] Broader algorithmic-equivalence audit of coupled, multi-profile and conflict-constrained repair; no universal absence claim.

Raw PDF and render intermediates stay outside the thesis repository in the current chat's work directory. Only original notes, stable source URLs/fingerprints, and status records enter Git. Temporary signed download URLs are excluded. The controlled M01 implementation is complete within its stated scope; no public dataset, neural model or paper draft has been started.
