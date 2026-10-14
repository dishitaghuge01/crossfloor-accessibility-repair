# Handover: fixed project direction through the research paper

Prepared 14 October 2026. This is a continuation contract, not a new research brainstorming task.

## 1. User instructions: follow these first

- The project direction is FINAL: topology-preserving cross-floor accessibility repair with shared physical assets, owned collision cells, original-action costs and the implemented floor-interface DP.
- Do not restart research, suggest alternative thesis topics, reopen rejected solver directions, add neural/LLM/GPU components, or explore other approaches in parallel.
- Do only necessary correctness/originality checks. Prioritize implementation, controlled evaluation, building evidence and manuscript completion.
- Commit reviewable milestones. Do not push automatically: the user pushes from PowerShell when they choose.
- Be truthful. The direction is fixed, but literature originality has not been established conclusively. Do not reinterpret the user's decision as proof of priority. Continue the same project while wording claims according to evidence.
- Use targeted tests for bounded changes. Repeat the full suite only for material solver/geometry changes, failures, or release verification. Do not rerun every previous checkpoint at every step.
- No outside messages, author contacts, public submissions or publication without explicit user authorization. Do not create another chat merely because this file is a handover.

## 2. Repository and environment

Repository: `https://github.com/dishitaghuge01/crossfloor-accessibility-repair`.

Actual local Git checkout:

`C:\Users\HP\Documents\Codex\crossfloor-accessibility-repair`

The previous chat's working/output folder is a different directory:

`C:\Users\HP\Documents\Codex\2026-10-13\https-github-com-dishitaghuge01-crossfloor-accessibility-2`

Do code/research work in the actual checkout. Review copies live in the chat folder's `outputs` directory. The project uses Windows PowerShell, Python 3.12 in `.venv`, an editable package, jsonschema and Shapely. No GPU or architect team is assumed. Read the checkout's `AGENTS.md`; raw PDFs, BIM inputs, generated runs and secrets must not enter Git. `runs/`, `data/external/`, `data/derived/` and `*.pdf` are ignored.

At handover inspection, branch was `main`, origin was `https://github.com/dishitaghuge01/crossfloor-accessibility-repair.git`, the tree was clean and latest implementation/result commit was `1326913`. This handover is committed afterward; inspect `git log -1` for the final current HEAD. No pushes were performed by the assistant.

```powershell
Set-Location 'C:\Users\HP\Documents\Codex\crossfloor-accessibility-repair'
git status --short
git log -5 --oneline
$env:TEMP = (Resolve-Path runs/tmp).Path
$env:TMP = $env:TEMP
```

Use `.\.venv\Scripts\python.exe`, not an unrelated system environment. If `runs/tmp` is absent on a fresh checkout, create it before `Resolve-Path`. Installation instructions and `requirements-dev.lock.txt` are in README.

## 3. Read these, in this order

1. `AGENTS.md`, `README.md`, `PROGRESS.md`.
2. `docs/thesis_contribution.md`: frozen working claim and decision to proceed.
3. `docs/owned_interface_solver.md`: full implementation, transition argument and checkpoints.
4. `docs/modern_connectivity_comparison.md`: corrected direct published-method comparison.
5. `docs/asset_unit_interface_theorem.md` and `docs/owner_multiplicity_refinement.md`: precise proof/parameter assumptions.
6. `docs/implementation_contract.md`, `spec/instance.schema.json`: input and strict-model contract.
7. `docs/novelty_claim_registry.md`, `docs/source_ledger.json`: claims, prior evidence and exact inspection limits.

`docs/master_plan.md` and older research files preserve milestone history. Some old checkpoint paragraphs describe what was absent then. M15 implemented the solver; M16 corrected M11's generic encoding; M17 froze the working claim and delivered the project demo. Do not treat historical absence statements as current blockers.

## 4. Frozen thesis claim and scope

Working statement:

> This thesis develops and evaluates exact strict cross-floor accessibility repair with frozen rooms and adjacency, geometric asset ownership and indivisible action costs. Its specific algorithmic contribution under development is an owned-cell floor-interface dynamic program that preserves complete physical interventions while compressing profile-specific route witnesses.

Proposed bound:

`recognition_time + 2^O(prL + zL log(h+2)) * polynomial(input_bit_size)`.

- p: accessibility profiles.
- r: maximum retained within-floor baseline components per profile/floor. Implementation conservatively counts all components.
- z: collision cells per floor.
- L: maximum complete available action–asset coupling-unit support and active baseline inter-floor edge span, measured in consecutive ordered floors.
- h: maximum number of owners in one unit capable of occupying one cell. g, also reported, counts total assets in one unit; h refines the older g-based bound.

These parameters are measured, not guaranteed small for arbitrary buildings. The single-exponential statement is in the interface encoding above, not in p+r+z+L+h as a plain sum.

Primary implemented solver scope: rooted obligations (one source per profile), independent physical portal activation actions, nonnegative original costs, fixed rectangular footprints and the reserved-interface 2D kernel. Existing baseline connections may include doors; **candidate doors are unsupported**. Dependencies, declared exclusions, room reshaping and representation-correction actions are unsupported by this solver. Its limit errors are not infeasibility results.

SCFAR preserves original room IDs, polygons and shared-boundary adjacency A. No new corridors/shafts/room splits/merges may silently change this contract. Existing-wall opening support elsewhere in the repo is not automatically supported by the chosen DP. RCFAR is a separate prototype with explicit topology changes and delta_A; do not make it the paper's main contribution.

Geometry is a fixed 2D experimental abstraction: footprint/reservation containment, landing access, widths, clearance, profile permission and pair overlap. Equipment envelopes are not dynamic movement obstacles. It does not certify slabs, headroom, structure, moving equipment or building-code compliance.

## 5. Essential semantic invariants

- Costs attach once to complete original actions. Preserve exact cost, then action count, then sorted original IDs. Decimal arithmetic avoids accidental rounding in comparisons.
- Profile graph layers never mix. Shared purchase costs do not allow users to change profiles along a route.
- Same-owner overlap is allowed only after global kind/width/physical-profile/footprint consistency checks.
- Each action occupies its own complete effect footprints. Selecting an asset on one floor does not occupy every unselected catalogue portion of that asset.
- A route witness may omit disconnected/irrelevant supplied graph components. Full paid effects, physical occupancy and cost remain materialized. Never shrink an intervention to its witness.
- Complete action–asset incidence components define units; collision edges do not merge units. Keep owner identities during the whole unit, then erase them to occupancy bits.
- Reject disappearance of a selected non-anchor witness component when its last boundary vertex is forgotten. Required targets are selected on introduction.
- Representative bases are grouped only at the same event, occupancy map and selected profile boundary sets. Rank compression is established prior machinery and must be attributed.
- Cell overlap equivalence must match the kernel. The rectangular arrangement recognizer requires cell area above EPS=1e-8 and checks pair equivalence. Tiny arrangements are conservatively unsupported; do not ignore EPS.

M10 proposes a fixed independent physical-background extension for evidence-backed corrections; it is **not implemented**. Do not enable it during evaluation by merely changing an action's type. Keep the final paper within implemented scope unless a necessary input issue requires a separately proved/tested correction inside this same project direction.

## 6. What already exists: do not rebuild it

Core files:

- `src/cfar/interface_recognition.py`: geometry compilation, exact cells, units, rooted/profile baseline components, p/r/z/L/g/h.
- `src/cfar/dp_owned_interface.py`: complete floor/unit/witness DP; compressed and uncompressed modes; materialization/reachability replay.
- `src/cfar/representative_partitions.py`: cut rows, product-profile rows, weighted GF(2) bases.
- `src/cfar/resource_logic.py`: corrected owner–cell usage graph and separate reachability/cell-count evaluator; polynomial-bit objective weights. It is not the published metatheorem optimizer.
- `src/cfar/actions.py`, `geometry.py`, `validation.py`, `obligations.py`, `objective.py`: shared kernel.
- `src/cfar/oracle.py`, `certificates.py`: exhaustive solver and separate replay/union-find certificate checking. Geometry/schema remain shared; do not call this an independent geometry engine.
- `src/cfar/interface_scenarios.py`: complete authored examples, cyclic graph, dense private alternatives, genuinely coupled owners and multiple-room/profile cases.
- `src/cfar/io.py`: manifests, canonical JSON and fingerprints.
- `src/cfar/cli.py`: recognizer, chosen solver, oracle, verifier and earlier baselines.

Existing commands:

```powershell
.\.venv\Scripts\python.exe scripts/run_project_demo.py --output runs/new-demo
.\.venv\Scripts\python.exe -m cfar.cli recognize-interface INPUT.json --output runs/new-recognition
.\.venv\Scripts\python.exe -m cfar.cli solve-owned-interface INPUT.json --output runs/new-repair
.\.venv\Scripts\python.exe -m cfar.cli solve-owned-interface INPUT.json --no-compression --output runs/new-uncompressed
.\.venv\Scripts\python.exe -m cfar.cli solve INPUT.json --variant SCFAR --output runs/new-oracle
.\.venv\Scripts\python.exe -m cfar.cli verify INPUT.json runs/new-oracle/certificate.json
```

Use fresh empty output directories. Default DP limits: 100,000 raw states and 65,536 cut columns. Oracle default cap: 20 actions, exponential enumeration; choose much smaller instances for routine comparisons. Preserve errors/timeouts/limits as explicit statuses.

## 7. Verified evidence at handover

- Latest full suite: **616 tests passed in 46.10 seconds**. A final injective resource-graph ID serialization change was rechecked with all twelve relevant tests. Do not claim a later full run.
- M17 added one demo integration test, passed separately in 2.07 seconds. Do not claim all 617 tests were run together.
- M16 checkpoint at clean revision `62798b3`: compressed/uncompressed DP and oracle agree on **50 cases**, 25 optimal and 25 infeasible. Corrected resource logic matches all **1,306 selections**; oracle certificates separately replay them. All **201 manifests** report the clean revision. Artifacts: `runs/m16-modern-comparison`.
- Cyclic case: four representative rows removed; peak retained states 47 compressed versus 48 uncompressed, same cost-one witness. This is small compression evidence, not a large empirical speedup.
- Dense64: 64 private colliding alternatives, analytical optimum cost one, five peak raw states. It was not exhaustively certified. The algorithm avoids 2^64 enumeration on this family; recognition still does pairwise work.
- Coupled-owner family has genuine h=2,3,4 with p=1,r=1,z=2,L=4 fixed and optimum two. Private alternatives alone have h=1 and are not evidence for variable-h behavior.
- Multi-room case has p=2,r=3,z=2,L=2,g=2,h=1, four destinations/profile obligations and different within-floor contractions by profile.
- M17 demo at clean revision `0b41375`: routes improve **1/4 to 4/4**, original action A costs **3 abstract cost units**, delta_A=0, oracle optimum/certificate valid. Report and full evidence: `runs/m17-project-demo`.

Generated runs are ignored and may not exist after cloning GitHub. Source constructors/runners regenerate them. Report copies are in the old chat's `outputs` directory. None of these are public BIM or general construction evidence. Test durations are not solver benchmarks.

## 8. Literature positioning: bounded check, not another search campaign

Settled prior ingredients:

- Weighted labelled Steiner forest already represents shared-cost bundled graph activation. Bundling/profiles alone are not novel.
- Fixed geometric conflicts compile into unary/pair constraints within the current kernel.
- Priority Line Cover and bounded-active interval sweep machinery already cover earlier shaft-only directions. Do not return to them as new thesis options.
- Bodlaender/Cygan/Kratsch/Nederlof supply weighted rank-based connectivity compression. Neither weighted bases nor tensor products are our invention.
- Generic weighted bounded-width logic already gives optimization baselines.

Closest concrete current comparison:

M16 corrects the old generic whole-asset encoding to **one Usage object per owner/cell**. A fixed A&C distance-neighborhood formula, exact objective transfer and supplied linear clique-width expression apply Bergougnoux/Dreier/Jaffke's weighted theorem. This yields a transferred baseline exponent `O(prL+zL+p+zLh)`, compared with the chosen proposed exponent `O(prL+zL log(h+2))`.

This is a difference between these constructed upper bounds, not a lower bound on every generic method. For fixed h they have the same asymptotic interface exponent. A narrower generic encoding or existing connectivity-plus-resource/CSP state method might match our dependence. That is the **one remaining focused originality question**; do not inflate it into a new broad literature survey.

Primary source records, URLs and inspected sections are in `docs/source_ledger.json`. M16 source: arXiv:2202.13335v2, Theorem 1.2 and weighted membership-pattern definition. In that source, do not confuse the tree-width A&C quadratic entry with the DN-only linear entry; the transferred linear bound uses the supplied clique-width expression. Choice-network full proofs remain partially accessible; don't describe them as fully audited.

Do one bounded comparison/proof pass needed for final claims while evaluation progresses. Write exact source/model/result correspondence. If equivalence is found, narrow the wording honestly and continue this fixed project as a specialized repair method/evaluation contribution. Do not invent originality, abandon the project or brainstorm replacement topics. A venue decision must reflect the eventual supported contribution.

## 9. EXACT starting point for the receiving chat

**Start at controlled evaluation, not novelty exploration and not solver reimplementation.**

1. Read the short source-of-truth files in section 3 and inspect Git status.
2. Reuse the M17 demo/checkpoint; run it once only if ignored artifacts are unavailable or needed for inspection.
3. Implement a reproducible benchmark driver and summary generator around the existing recognizer, compressed solver, uncompressed solver and small-instance oracle. This is the first new implementation milestone.
4. Keep the working claim frozen. Integrate the one focused originality/proof check into theory/related-work drafting, not as an indefinite prerequisite to engineering.

## 10. Fixed roadmap through the research paper

### Step 1 — Freeze benchmark protocol and make results usable

Create a concise evaluation protocol and runner, with fixed recipes, seed list, method settings, input/source hashes, environment, clean revision, timeout/resource statuses and output paths. Summarize results automatically into reviewable tables. Avoid a new framework or frontend.

Compare compressed versus uncompressed owned-interface DP on the same recognized class. Use the oracle only on small inputs; retain its independently replayed certificates. The resource-logic evaluator is a semantic check, **not a generic optimization runtime baseline**. Earlier partition/shaft solvers apply only on their documented subclasses; record unsupported scope rather than presenting rejection as a performance loss.

Measure end-to-end solver time, recognition time separately, peak raw/retained states, row removal, status, cost and witness agreement. `solve_owned_interface` currently performs recognition internally: do not subtract separately measured recognition time and call the difference an accurately measured DP-only time. Instrument properly if that split is necessary. Report single-run measurements as such; use a fixed small repetition count for comparative timing claims, not unbounded repeats.

### Step 2 — Controlled parameter evaluation

Reuse and extend authored generators within the same fixed model. Vary candidate count, floors, p/r/z/L and **genuine h**, with shared assets, disconnected bundles, partial overlaps and multiple destinations. Ensure generated geometry validates and parameters are measured; do not rename assets or delete necessary rooms to manufacture favorable bounds.

Include feasible, infeasible, limit-exceeded and conservative-recognition-rejected inputs. Include known analytical families for larger action counts; do not label them exhaustively certified. Use meaningful seeds and separate correctness-small from scaling-large sets. Save failures and reduce counterexamples if one appears; correct the method before continuing claims.

Produce plots/tables showing where recognition dominates, where compression helps, where it adds overhead and where the model/limits stop it. Do not manufacture a speedup if the observed row reduction is modest. Commit protocol, generators, scripts and concise conclusions; keep raw run artifacts ignored.

### Step 3 — Building-input/evidence workflow

Use public, explicitly licensed IFC/building data, with a small multi-floor case first. Preserve source URLs/licenses/hashes and original IDs. Keep raw source files in ignored storage. Build an auditable extraction/adaptation path to the existing JSON schema: rooms/floors, baseline traversable connections, profile evidence, reserved areas and candidate fixed templates.

Inspect extraction and candidate evidence. Geometric adjacency is not traversability. Physical presence is not permission metadata. Do not invent missing routes, reservations or connector capabilities from proximity alone. The chosen solver handles new physical actions; metadata-only repair belongs to the separate existing oracle/proposed extension and must not be silently mixed into the main algorithm.

Check that physically present background is accounted for in collision validity, even when graph permissions are missing. The current chosen recognizer does not implement M10's independent-background contract. If a public input needs it, either supply a documented faithful baseline satisfying current scope or implement only the necessary evidence/geometry handling with explicit proof/tests. Never omit an existing asset to admit a candidate. This is a fidelity obligation within the fixed project, not permission to explore another topic.

Declare any evaluated building subset and missing evidence. Document manual annotations; do not call them automated extraction. Maintain frozen polygons/IDs/adjacency. Reserve construction/compliance claims for evidence the kernel actually supports.

### Step 4 — Building-grounded evaluation and ablations

Apply the same algorithms/protocol to recognized building-derived cases and documented controlled variants. Keep variants from one source building together rather than treating them as independent buildings. Report measured parameters, repair cost, original action IDs, reachable destinations, strict topology preservation and geometry checks.

Compare compressed/uncompressed modes and small oracle cases. Include ownership/cost/geometry semantic ablations only as clearly invalid simplifications or explicit experimental controls, not alternative valid repairs. Keep reachability, geometry, optimality and original-restoration agreement separate. Restoration metrics require a real documented reference and are secondary; an original reference is not automatically optimal.

### Step 5 — Finalize theory and focused related work

Consolidate the model, recognition assumptions, witness-thinning lemma, unit ownership, sufficient-state/dominance argument, product-row preservation, floor transitions, bit complexity and final bound into one coherent proof. Check terminology against the actual implementation. The theorem excludes unsupported dependencies, arbitrary demand pairs and construction geometry.

Integrate only the focused comparison from section 8. Attribute all reused rank/logic/network machinery. State the exact physical representation/parameter/semantics distinction supported by evidence. Do not claim universal priority, unconditional superiority or a generic lower bound from an upper-bound comparison. Keep any unsettled originality wording qualified instead of restarting research.

### Step 6 — Write the paper

Working title: **Exact Topology-Preserving Cross-Floor Accessibility Repair with Shared Physical Assets**. Adjust phrasing only to match final verified scope; do not switch topics.

Write, in order: problem/model; algorithm/proof; experimental protocol/results; related work; introduction/contributions; limitations; conclusion; abstract. Use the advisor/venue template if supplied, otherwise a conventional conference-style LaTeX draft. No venue-shopping campaign is needed now.

Include: a motivating before/after case, frozen-topology/access distinction, full-action versus thin-witness diagram, owned-cell/unit example, measured parameter definitions, algorithm pseudocode, theorem assumptions/proof, direct baseline comparison, correctness/scaling/building tables and honest limitations. Every experimental number must trace to a saved manifest. Every literature claim must have a verified source locator. Do not advertise the number of unit tests as algorithmic novelty.

### Step 7 — Reproduce and prepare delivery

Run appropriate full regression and a fixed clean-revision reproduction suite for final algorithm/geometry code. Regenerate figures/tables from saved protocol, verify costs/witnesses/geometry/adjacency and audit source licenses. Confirm failure/limit statuses and scope are reported accurately. Check the manuscript's text, references, figures and cross-references against actual results.

Deliver: manuscript source, compiled PDF, reproducibility README, frozen benchmark/extraction scripts, dataset provenance/license list and concise results/claim limitations. Generated PDFs/runs/raw inputs remain outside tracked source as required by AGENTS. Preserve a final clean commit and tell the user exactly how to regenerate the results.

### Step 8 — Submission boundary

The endpoint is a complete, reproducible research-paper package ready for advisor/venue review, not a promise of acceptance. Do not submit, upload publicly or send it to anyone without explicit user authorization. The user decides when to push Git. If the supported contribution does not justify the intended venue's claims, explain that specifically while preserving this fixed project direction.

## 11. Milestone discipline and done criteria

Commit at protocol/runner, controlled-results, input-workflow, building-results, consolidated-theory, manuscript and final-reproduction milestones. Update `PROGRESS.md` and `docs/master_plan.md` when evidence/gates change. Do not produce a series of novelty-only milestone documents without progressing the implementation/evaluation/manuscript.

Done means: recognized scope is explicit; algorithm and proof agree; reproducible controlled and building-grounded evidence support final claims; reused methods are attributed; limitations/uncertainties are honest; manuscript compiles and all tables match manifests; user has the final paper package. Neither a working demo nor a passing test count alone meets this endpoint.
