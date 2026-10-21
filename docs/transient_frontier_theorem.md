# Static transient event-frontier bound

22 October 2026. A project derivation for the existing recognized strict model,
not a claim of priority over general decomposition DP. It applies to **uncompressed,
minimum-label-merged DP with both lifetime projections**, without operational caps.
No representative reduction is needed for this bound.

## Parameter and certificate

Fix the implemented canonical or reverse complete-unit schedule. Each profile
has its permanent anchor. A required/root vertex is potentially present from its
actual eager floor introduction; an optional vertex is potentially present from
its first available incident edge/action. Presence lasts through the final
incident event (or ordinary floor exit for a required vertex with no incidence).
Count endpoints **during** an action, before projection, not just after it. Keep
each anchor permanently. Let b be the maximum number of potentially present
profile vertices plus anchors at any such event. This counts a union over all
possible states, not one selected witness or one observed run.

A cell is potentially present from its first touching action through closure
of its final touching complete unit. During current unit J its conservative
domain contains empty, external occupancy and each owner in J that covers that
cell; outside a unit its domain is empty/external. Let

    rho = max_t sum_{c potentially live at t} log2 |D_t(c)|.

Both parameters include transient states before vertex/cell projection. The
certificate also records introductions, floor exits and unit closures. Constructing
it scans the recognized catalogue and schedule in polynomial time. Its explicit
per-event output can itself be polynomial in input size. `event_frontier_certificate.py`
implements this conservative calculation; it does not run optimization.

## Theorem

Subject to the previously proved recognized-model equivalence and lifetime
projection lemma, the merged uncompressed both-projection algorithm returns
the complete exact cost/count/sorted-ID optimum in

    T_rec + 2^{O(b log(b+2) + rho)} poly(B)

time, with additional DP working memory

    2^{O(b log(b+2) + rho)} poly(B).

Here B is the represented input bit size. Recognition and final materialization
remain charged; permanent anchors and eagerly introduced required targets cannot
be omitted from b. The bound is not asserted for floor-only mode, no-merging
history mode or capped execution. It is a sufficient tractability criterion,
not a practical prediction from post-solve peak measurements.

### Derivation

At each fixed event, the physical occupancy vector has at most product_c |D(c)|
possibilities. Complete-unit closure prevents a still-reusable owner's identity
from being mistaken for external occupancy, and prevents identities from former
units from surviving as independent domain values. Cells not yet touched are
empty; erased cells have no possible future physical test.

The profile-specific selected subsets and partitions inject into a partition of
the at-most-b potential vertices plus one distinguished absent-element marker:
put every absent optional vertex in the marker block; retain each profile's
partition blocks otherwise. Thus there are at most Bell(b+1) <= (b+1)^(b+1)
possible connectivity keys. Forbidden cross-profile blocks merely reduce this
upper bound. Every event table therefore has at most
2^rho Bell(b+1) keys. Equal keys keep one minimum complete objective label.

For an action, each supplied connected witness component contains at least one
potential profile vertex. There are at most b such components across profiles,
so at most2^b choices per input key (in addition to skip). Whole paid occupancy
is updated before witness choice, and all action endpoints/cells are included
in the transient parameter. Baseline/intro/close/floor transitions have polynomial
work per key. Projection and merging inspect polynomial-length keys and labels.
The number of schedule events is polynomial. The two consecutive tables, streamed
branching and materialized choice lists fit the stated memory bound. Exact cost
arithmetic, stored original IDs and the final replay add polynomial factors.
The existing projection/label proof supplies feasibility and full-objective
preservation; the counting argument alone is not a replacement for that proof.

## Strict improvement over the coarse floor-bound description

Consider `build_private_bay_study.py`: three floors, source below, target above,
n optional middle rooms. Bay i has a private owner, two consecutive edges and
one optional atomic two-edge bundle, all confined to that bay's three cells.
Process complete bays consecutively. The source and target are eagerly introduced;
at most one middle vertex is available at once. Thus b=4 including the anchor,
and rho<=log2(27), independent of n. The recognized coarse parameters have
p=1, r=z=n, L=3, h=1. Consequently the earlier floor theorem's exponential
argument grows linearly with n while this event-frontier argument is constant.
This is a strict separation of **the two stated bounds**, not an exponential
lower bound on actual floor-DP runtime or on every other graph representation.
The graph is K(2,n); its small standard decomposition is not new.

## Applicable prior methods and what is distinct

The Bell-number argument is conventional frontier partition DP. Bodlaender et al.'s
weighted project/forget and representative machinery remains prior work (their
Definitions3.2/Proposition3.3 and Sections3.3,3.6 in the inspected accepted text).
A generic finite-domain connectivity DP supplied this same physical catalogue
encoding and valid schedule can match the bound; representative methods may improve
the connectivity exponent. This theorem does not distinguish itself as a stronger
generic connectivity algorithm. Its additional output is a directly computable
certificate from complete physical actions, with owner retirement, all paid cells,
eager targets and transient action branching included, and an explicit class
where the previously stated floor guarantee is unnecessarily coarse.

Generic A&C logic can express the complete selection after the existing
Action/Occurrence/Usage/Cell reduction and supplied decomposition. No lower bound
on that generic method follows. The executed CP-SAT model is a practical baseline,
not an algorithm whose theoretical capability is ruled out by this parameter.
Consequently the present work strengthens a model-specific guarantee and tests
a computational regime; **exclusive literature novelty remains unestablished**.
## Exponential retained-state separation from floor retirement

In the private-bay family, immediately after the n complete units at floor0
have closed but before floor0 exits, the uncapped floor-only merged DP has
at least2^n distinct resource/partition keys. For every subset X of bays, take
exactly its two-edge bundles and choose the empty thin witness for every purchase.
All these prefixes have the same permanent-root and eagerly introduced target
partition; no optional middle vertex is selected. Their full paid occupancy differs
on the private cells of precisely X. Distinct occupancy keys are never merged or
removed by representative selection across resource groups. The required target's
unrooted block has not vanished and no floor has exited, so these prefixes have
not been rejected. Thus the keys are all present. Positive costs do not remove
them because minimum-label dominance is only at equal state key.

With both projections, b=4 and product domain<=27, so the event theorem gives
constant tables and polynomial total work (plus recognition/input factors).
This proves an exponential key-space separation for the specified implemented
floor vs lifetime schedules on one identical recognized physical family. It is
not a lower bound on all ways to optimize that family. A standard small-width
decomposition also solves K(2,n); no generic prior algorithm is separated by this
argument. The family is a mechanism witness, not application validation.
