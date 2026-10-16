# Finite-domain comparison: what the owner factor does and does not establish

Assessment date: 16 October 2026. This is a project derivation, not a newly
located published theorem or a priority certificate. It uses the existing
recognizer, complete-unit schedule and representative-partition argument.

## Explicit construction

Let b <= prL be the live profile-component boundary and c <= zL the live
collision-cell count. During a complete action-owner unit, associate a finite
variable with every live cell. Its domain contains empty, occupied by a
completed unit, and each current-unit owner capable of covering that cell.
There are at most h+2 values per variable. A selected action checks and updates
every cell of every paid effect. Equal owners may reuse a cell; another owner
or a completed-unit occupant rejects the action. A skipped action has no
effects. At unit completion, replace all current owner values by occupied.
No future action can use one of those owners: complete action-owner incidence
components, rather than collision components, define the units.

These are finite-domain transition constraints, with at most (h+2)^c resource
assignments. The ownership part alone consequently costs
2^O(zL log(h+2)) states. Calling this a generic resource-variable treatment
instead of an owned-cell map does not change that count.

For connectivity, attach selected boundary vertices and a separate partition
for each profile. Ordinary partition enumeration can contribute
2^O(b log(b+2)); resource variables by themselves do not improve it. Applying
the already attributed weighted representative-partition machinery, grouped
at equal event/resource assignment/selected sets, yields the same
single-exponential connectivity factor used by our construction. This is a
description of the existing proof in generic state language, not an
independently implemented second algorithm.

Original action selection remains the transition decision. Pay its original
cost once and preserve count/ID tie-breaking. Full occupancy and thin route
witnesses remain separate; a generic local variable must not erase unused
paid effects. Arbitrary declared exclusions/dependencies are not introduced.

## Consequence

The logarithmic owner-domain term is not evidence of a separation from all
generic connectivity-plus-resource methods. Such a method, if supplied this
same valid schedule and rank reduction, can use the same resource domain.
The paper's comparison with its particular Boolean Usage-object logic
encoding remains a comparison of two explicit transferred upper bounds.
It does not establish an inherent advantage over generic finite-domain
methods. This resolves the conceptual part of the previously open comparison
risk against a broad superiority claim; it does not identify a prior paper
that already gives our complete physical-to-interface construction.

The surviving contribution is the explicit recognized physical construction,
its preservation of complete actions and exact objective, its proof under
stated assumptions, and its implementation/evaluation. Literature priority
for that complete construction remains unconfirmed. The derivation does not
establish a published CSP metatheorem, a new complexity lower bound, or
independent human proof review.

## Necessary verification

This note was checked against docs/modern_connectivity_comparison.md,
docs/supported_contribution_boundary.md and the handover invariants. No solver
or benchmark changed; no new timed observation or regression claim is made.
