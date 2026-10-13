# M01.1: closest-work comparison and evidence ledger

Reviewed 13 October 2026. **G0 remains OPEN.** This is a reviewable research checkpoint, not a completed full-text gate or a novelty claim. The active candidate remains Cross-Floor Accessibility Repair; no rejected candidate is reactivated.

## Comparison contract

SCFAR takes authored, frozen floors, distinguishes shared-boundary adjacency A from traversable access D, and selects costed, evidence-typed actions to satisfy profile-specific cross-floor obligations. It preserves original room identities and A exactly. RCFAR permits declared topology changes and reports Delta_A separately. Evidence for reachability, geometry, optimality, and original-design recovery remains separate.

Evidence labels below:

- **Method inspected:** relevant full-text method and guarantee sections inspected; does not mean every appendix or implementation was audited.
- **Partial:** abstract, publisher excerpts, or bibliographic record only; unknown features cannot be marked absent.
- **Not established:** the inspected sections do not establish this property; this is narrower than claiming the work cannot support it.

## Architectural comparators

| Work / evidence | Input and operation | Cross-floor / profiles | Topology and geometry | Objective / guarantees | Relationship to SCFAR |
| --- | --- | --- | --- | --- | --- |
| MANSION, Che et al., CVPR 2026; method inspected in arXiv v1, sections 3.1, 3.2, C, D | Generates room partitions; also edits pre-generated scenes for task preconditions | Explicit vertical cores and simulator transitions; SCFAR mobility-profile obligations not established | Conditions synthesis on a target bubble graph; scene edits are distinct from frozen-floor repair | Candidate energy ranking; minimum intervention cost or repair bound not established | Compare BOTH synthesis and task editing. Generation is not the whole method. |
| EPSAP, Rodrigues et al., 2013; partial publisher text | Evolves space positions/sizes and parametric stairs/lifts | Multi-level design; profile obligations unknown | Layout geometry is a search variable; exact frozen adjacency contract unknown | Hybrid evolutionary search; full mathematical appendix unavailable in this review | Generation distinction supported by publisher description; detailed guarantees remain unreviewed. |
| PlanFix, Trinh et al., SSRN 7275102, posted August 2026; partial abstract | Post-hoc geometric/code repair with constraint projectors | Cross-floor obligations and action typing unknown | Preserves layout fidelity; exact A equality unknown | Abstract reports non-increasing violation energy; global minimum edit cost unknown | Closest geometric-repair comparator. Full method required before separation. |
| Al-Harasis and Jabi, DFBI 2026, pp. 45-54; method inspected | IFC-derived door graph; evaluation-only area/edge alignment and synthetic programme completion | Profile-specific cross-floor repair not established | Door-based adjacency is access, not SCFAR shared-boundary A; synthetic graph edits need not have IFC geometry | Benchmark alignment plus GNN evaluation; minimum-cost selection or optimality bound not established | Concrete method-level distinction: graph evaluation/completion versus physically certified repair. |
| Bayraktar Sari and Jabi, Architecture 6(2), 76, 2026; partial bibliographic/abstract record | BIM-embedded spatial graph analysis | Record explicitly mentions multi-level accessibility representation | Detailed vertical-edge extraction and profile semantics unknown | Repair optimization and guarantees unknown | Must inspect journal method; conference slides are not a substitute. |

### Source locators and reading notes

**MANSION.** [Official CVPR record](https://openaccess.thecvf.com/content/CVPR2026/html/Che_MANSION_Multi-floor_lANguage-to-3D_Scene_generatIOn_for_loNg-horizon_tasks_CVPR_2026_paper.html); [arXiv v1 full text](https://arxiv.org/html/2603.11554v1). Section 3.1 reserves vertical-core footprints before room synthesis and ranks sampled feasible partitions. Section 3.2 and Appendix D describe connectivity checks and object provisioning in pre-generated buildings. These overlap with task executability, so dismissing the entire work as generation would be inaccurate. The inspected formulation does not establish a minimum-cost subset of certified architectural interventions on frozen floors. Check the final CVPR supplement and complete tool cards before closing this row.

**EPSAP.** [Publisher article](https://www.sciencedirect.com/science/article/pii/S0926580513001027), DOI 10.1016/j.autcon.2013.06.005. Available introduction/method excerpts describe mutable space and vertical-circulation allocation. Full methodology and Appendix A remain required. [Author thesis containing RP3](https://citeseerx.ist.psu.edu/document?doi=b39e5a5563a71a5786fde9661d19c13a4ee71f0a&repid=rep1&type=pdf) was identified, but access returned HTTP 403. An available copy must be checked against the published article; the thesis is not treated as read.

**PlanFix.** [SSRN record](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7275102), DOI 10.2139/ssrn.7275102. Abstract supports projection-based post-hoc repair and a monotone acceptance rule. Monotonicity does not itself certify global repair optimality. Both record and delivery requests returned HTTP 403 through direct retrieval; indexed delivery content was the abstract, not the 63-page paper. Required checks: variables, fidelity objective, egress formulation, topology invariants, exact-solver comparators, and guarantee assumptions.

**Al-Harasis and Jabi.** [Publisher article](https://submission.dfbi.org/index.php/dfbi/article/view/26347); [published full text](https://submission.dfbi.org/index.php/dfbi/article/download/26347/35/797); [ORCA record](https://orca.cardiff.ac.uk/id/eprint/186310/), DOI 10.66408/dfbi.2026.26347. Sections 3.1-3.2, pp. 48-49, extract an openings-only graph. Sections 3.5-3.7, p. 49, adjust areas and insert/remove required benchmark edges, then optionally add programme nodes. Sections 4.5 and 5.4, pp. 51-52, explicitly separate synthetic evaluation graphs from physical IFC elements. This is evidence of a limited distinction, not proof of overall novelty. A same-title eCAADe record also appears in the author profile (DOI 10.52842/conf.ecaade.2026.1.021); inspect that version separately before treating the DFBI paper as exhaustive coverage.

**Bayraktar Sari and Jabi.** Correct journal target: [Architecture article](https://www.mdpi.com/2673-8945/6/2/76), DOI 10.3390/architecture6020076; [ORCA record](https://orca.cardiff.ac.uk/id/eprint/187116/). Journal HTML/XML requests failed with HTTP 429/403. The separately discovered Rome conference presentation (ORCA 187120) is not equivalent evidence. Inspect the journal's graph construction, stair/lift modelling, update workflow, accessibility definition, and limitations before assigning a repair/non-repair verdict.

## Algorithmic comparators

| Work / inspected locator | Existing problem and guarantee | SCFAR overlap and transfer limit |
| --- | --- | --- |
| Goemans and Williamson, 1995, constrained forests; sections 1-3, pp. 296-309 | Minimum-cost edges covering cuts for proper requirement functions; primal-dual approximation and dual lower bound | Restricted single-profile independent edge additions can match terminal-pair network design. Geometry, coupled actions and profile sharing require separate arguments. |
| Marx and Vegh, arXiv:1304.6593v2; sections 1-3, Theorems 1.1-1.2 | Minimum-cost connectivity augmentation by one under a bound p on added links; FPT and polynomial kernels | Strong comparator for candidate-link selection. Global edge-connectivity targets differ from named profile obligations; kernel transformations need not preserve feasible physical actions. |
| Golovach, arXiv:1308.1802v2; sections 1-4 | Edge addition/deletion to achieve connected prescribed degrees; kernel in d+k, FPT in k for connected regular targets | Establishes that connectivity-constrained graph editing has existing parameterized theory. Degree targets differ from floor topology and obligations; results do not automatically transfer. |

Primary texts: [constrained forests, author-hosted paper](https://math.mit.edu/~goemans/PAPERS/GoemansWilliamson-1995-AGeneralApproximationTechniqueForConstrainedForestProblems.pdf), DOI 10.1137/S0097539793242618; [minimum-cost augmentation full text](https://arxiv.org/html/1304.6593v2); [connected-degree editing full text](https://arxiv.org/pdf/1308.1802). Preprint versions are identified explicitly; theorem transfer requires checking the final versions and assumptions.

## Implications for the formal gate (project analysis, not a claimed theorem)

1. **Test the network-design reduction first.** For one profile, nonnegative additive costs, independent monotone edge additions, and prevalidated geometry with no joint conflicts, encode existing access as zero-cost edges and candidate additions as costed edges. Requiring terminal pairs to connect gives a Steiner-forest-style formulation. Keep parallel action identities or choose the least-cost equivalent edge where justified. This interpretation needs a formal equivalence proof; it is not new solely because vertices represent rooms.
2. **Coupling must be real.** Shared lift actions can activate multiple transitions/profiles for one charge. Independent per-edge costs may overcount or undercount. Mutually incompatible physical candidates can make individually valid certificates insufficient; verify their union too.
3. **Bounded portal count is not yet a DP theorem.** Arbitrarily many unresolved obligation endpoints, nonlocal coupled actions, and geometry conflicts can survive a floor boundary. State sufficiency must include obligation status and action commitments, or restrict those quantities explicitly. Connectivity partitions alone are a proposal.
4. **Do not equate preserving IFC with preserving A.** Evaluation-only graph edits may leave source files untouched yet introduce relations with no physical realization. SCFAR needs independent A, D, physical evidence, and reachability checks.
5. **No gate pass from this checkpoint.** The DFBI distinction is supported. The overall frozen-layout typed-action guarantee comparison remains incomplete, especially PlanFix, the journal accessibility method, and the eCAADe version.

## Completion ledger

- [x] Read governing repository files and clean baseline; remote HEAD confirmed at aa51926.
- [x] Inspect MANSION generation and task-editing method sections (arXiv v1).
- [x] Inspect mandatory Al-Harasis/Jabi DFBI full text, with page-level method locators and visual check of p. 49.
- [x] Add primary-source constrained-forest, augmentation, and graph-editing comparators.
- [ ] Inspect final MANSION supplement/tool cards and reconcile with v1.
- [ ] Obtain/read EPSAP published method and Appendix A.
- [ ] Obtain/read PlanFix complete paper and appendices.
- [ ] Obtain/read Architecture 6(2), 76 full text.
- [ ] Obtain/read same-title eCAADe 2026 version and compare with DFBI.
- [ ] Close remaining cells and reassess G0; do not infer absence from inaccessible text.

Raw PDF and render intermediates are outside the thesis repository in the current chat's work directory. Only original notes, source URLs, and status records belong in this commit. No dataset, neural model, solver implementation, or paper drafting was started in this checkpoint.
