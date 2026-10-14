# M10: typed background extension and transition audit

14 October 2026. Constructive extension of the M09 working argument, conditional on that argument. This is research, not an implemented solver, independent proof review, or established literature originality.

## Positive extension: corrections need not create ownership units

M09 restricts its main statement to newly installed assets. A strict repair also needs permission or metadata corrections for assets that physically exist already. Treating every correction referencing the same existing shaft as one installation unit can make L grow with the building height unnecessarily. The following evidence contract removes that artificial coupling.

Supply an authenticated, fixed physical background B, independently of which graph permissions are currently recorded. B includes existing asset identities, full footprints and physical-profile capabilities. Validate B once. Every correction has a fixed, evidence-backed graph activation bundle, a nonnegative original cost, and no physical change. Its permissions must be supported by B; a correction cannot assert an absent landing, a new profile capability, or a new connection merely because doing so would improve reachability.

New installations use identities disjoint from B. Check each installation against the whole physical background, including existing assets whose route permissions are missing. Remove installations that collide with B. Remaining installations satisfy M09's exact cell and unit assumptions. Corrections and installations have no prerequisites or exclusions and cannot modify one another's physical validity. Graph activation is monotone; costs belong to original actions, even when effects duplicate another action.

This is a stronger input contract than inferring background geometry from currently traversable graph edges. It is not a claim that the current schema/kernel already implements this distinction.

## Proposed typed corollary

In addition to M09's installation class, admit arbitrarily many corrections as above, each with graph-effect support in at most L consecutive floors. Include their nonloop endpoints in the definition of relevant components and r. Existing physical assets may span arbitrarily many floors; existing baseline graph edges must still individually have endpoint span at most L. No bound is imposed on how many corrections reference one background asset.

Process each correction once at its earliest effect floor, as an atomic take/skip event. A take charges its full original cost/count/ID and branches over its supplied profile graph components for the route witness. It leaves every collision cell unchanged. A correction involving several existing assets remains one original action and one charge.

The proposed bound remains

`recognition_time + 2^O(prL + zL log(g+2)) * polynomial(input_bit_size)`.

Here g bounds newly installed owners in an installation unit, not the number of existing background owners mentioned across correction records. L must bound each correction's complete effect support, each installation unit's complete support, and individual baseline edge support. This does not allow a single correction activating a building-wide shaft to evade L by splitting its effects and cost.

**Argument.** Fixed B and evidence validation make correction feasibility independent of the selected prefix. Background ownership can never be acquired or lost. Reusing its ID therefore creates no future collision exemption that a state must remember. A correction only adds witness edges and a fixed original label increment. The M09 state, witness-thinning argument, completion tests and weighted representative rows consequently apply unchanged. Only installation actions participate in action/new-asset coupling units. Future original IDs remain disjoint from the processed prefix, including corrections, so cost/count/lexical tie preservation also remains unchanged. Recognition of fixed background interactions occurs before optimization and is charged to recognition time.

This establishes a conditional reduction to the M09 transition system; it does not independently establish M09 or priority over earlier constrained-connectivity methods.

## Why this extension matters

Consider a supplied existing shaft serving F consecutive floor interfaces. Each interface has a separate evidence-backed permission correction costing one, with effect span two floors. One anchored profile must reach floor F from floor zero; no baseline route or alternative action supplies those missing edges. All F corrections are necessary and sufficient, giving optimum F. They can be processed locally with p=1, r=1 and L=2, independent of F, even though they reference the same existing physical shaft. There are no new owners or new collision resources in this example.

By contrast, two installation actions sharing a newly acquired asset must remain in one complete unit: selecting its identity changes compatibility with later installations. The difference is fixed physical presence versus selected installation, not the spelling of an action type. This analytical graph/evidence example is not a geometry-validated building experiment.

## Explicit transition invariants

1. Introduce all vertices/cells of a look-ahead window before processing an event whose complete support is there. Mark targets selected at introduction, even if they initially form singleton witness blocks. Attach actual roots to permanent virtual anchors.
2. For a taken installation, validate and fill its **entire** occupied cell set before making witness choices. A witness using none of its graph components still pays its original cost and occupies all of its cells. For a correction, verify background evidence during recognition and change no cells during selection.
3. Process every original action exactly once. Within an installation unit, keep owner identities until its final action; afterward erase owners to occupied bits. A correction referencing B cannot reuse or clear a newly installed owner.
4. Reduce partition rows only within a fixed event index, cell map and selected boundary sets. Never merge different cell maps merely because the current route witness is identical.
5. Forget a floor only after all events incident to it have been processed. Reject disappearance of the last boundary vertex of a selected non-anchor block. An isolated required target is therefore never silently discarded.
6. For rank reduction, a continuation can use only unprocessed event effects and witness choices. Ignored past physical edges are present in the actual repair but cannot be retroactively used to justify the compressed witness. Completeness relies instead on the root-component witness chosen for an optimum.
7. Accept only anchored witnesses containing all targets. Materialize all selected original actions and independently replay strict topology, profile reachability and geometry against B plus the complete installation set.

These invariants specify the necessary implementation behavior; they are not executable tests. In particular, successful graph replay alone would not validate the physical background contract.

## Failure cases that delimit the corollary

- A permission correction whose claimed physical capability is absent in B fails evidence recognition.
- A shaft is physically present but its missing-permission footprint is omitted from B: a colliding installation could be falsely admitted. B must be complete for the physical region considered, or recognition must return unsupported.
- An action conditionally installs an asset if another action was not selected is outside this fixed-cost/fixed-effect model.
- A correction requires a newly installed lift, modifies its footprint, or changes selection-dependent collision validity: the independence proof does not apply.
- One original action mixes correction and installation effects. It must be processed as an installation-unit action, retaining all effects, occupancy and its single cost; the separately processed correction rule cannot split that action.

## Evidence and novelty decision

This pass supplies a precise typed extension and event invariants, with an analytical long-background-shaft separation. No new solver, test execution, timing, or public BIM evidence is reported. Originality remains provisional; G3 stays open. The active target is the explicit ownership-aware physical decomposition and parameter dependence for typed rooted repair. Next compare a fully specified resource-incidence encoding and its weighted algorithm with this bound, and validate authored physical scenarios against the existing oracle.
