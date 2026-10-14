# Candidate structural result: bounded physical repair menus

14 October 2026. Research-only working proof. **Originality is not established.** This is a proposed structural theorem for a restricted SCFAR class, not a new general dynamic-programming technique. No solver or empirical performance claim accompanies it.

## Precise proposed claim

For rooted profile obligations, bounded per-floor baseline interfaces, bounded action span and exclusive fixed reserved slots, exact minimum-cost repair admits a catalogue reduction and an FPT algorithm in (p,r,z,L), independent of the total number of floors and catalogue alternatives in its exponential factor. Here p is profile count, r bounds baseline components per floor per profile, z bounds reserved slots per floor, and L bounds the number of consecutive floors touched by one action or baseline connection.

The possible contribution is the **physical assumptions-to-catalogue-bound argument** with original-action witnesses. Neither cheapest-twin reduction nor connectivity partitions are themselves new. This claim must be compared with existing local-type, labelled-connectivity and structural metatheorems before a novelty decision.

## Recognition assumptions

1. Frozen rooms, identities and shared-boundary adjacency; immutable connection geometry under the current unary/pairwise kernel. Every action is a complete physical portal-installation bundle with nonnegative cost. No dependencies, declared exclusions, reshaping, door interventions or opaque equipment obstruction.
2. Contract only within-floor baseline connectivity, separately for each profile. There are at most r resulting components per floor per profile, including components containing obligation endpoints. Arbitrarily many rooms may belong to a component. Keep baseline inter-floor edges rather than contracting the whole building.
3. Each profile has one fixed accessibility anchor. Every obligation in that profile connects that anchor to a target. Different profiles may have different anchors. Arbitrary independent terminal pairs are outside this claim.
4. Every action's geometry and graph effects are contained in a window of at most L consecutive floors. Baseline inter-floor edges also have endpoint span at most L. L includes all occupied endpoint floors, not only activated graph edges.
5. Each floor has at most z supplied, disjoint reserved slot polygons. A candidate occupies the complete fixed polygon of every slot it uses. Two different selected action bundles conflict exactly when they occupy a common (floor,slot). Slots are supplied reservations, not newly created shafts. Unary violations against fixed baseline assets are removed first.
6. Asset IDs and candidate connection IDs are private to their complete action bundle. Within a bundle, consecutive transitions of one asset may share its footprint consistently. Distinct actions do not activate portions of the same asset. This makes the complete-slot conflict rule valid; merely assigning a zone name is insufficient.

These are a checkable restriction, not a description of all building renovations. In particular, bounded r, complete-slot occupancy and rooted obligations must be justified on relevant inputs rather than silently assumed.

## Signature count

For an action starting at floor f, pad its window to L floors. Record:

- the occupied (relative-floor,slot) pairs, at most zL bits;
- the set of activated pairs of baseline components, separately for each profile, using at most p(rL)^2 bits as a loose bound.

The absolute floor f is part of the class identity. Components and slots use their actual identities within this window; equal signatures are not identified across different starts. The signature need not retain a raw catalogue connection ID because its profile-layer endpoints are recorded, while the representative retains all original IDs for final materialization. Kind/width/clearance checks are not inferred from this signature: unary feasibility has already been verified.

There are at most T = 2^(zL + p(rL)^2) signatures per start floor. Unavailable actions and actions with no effect on contracted reachability may be removed. Every remaining physical bundle occupies a nonempty slot set.

## Safe cheapest-original representative

For each signature, retain the action with minimum (cost,action-ID) order. Two actions of the same class have identical profile reachability effects and identical occupied slots. Since they are distinct complete assets and the occupied slot set is nonempty, they cannot both occur in a feasible selection. Against every other action, their conflicts are identical by the complete-slot rule.

If an optimum contains a discarded action a, replace it by the retained representative b. No other selected action has that signature. Unary feasibility, all external conflicts, contracted connectivity and frozen topology are preserved. Cost does not increase and action count is unchanged. At equal cost, replacing by the smaller original ID cannot worsen the sorted-ID tie convention. Repeating this yields an optimum using only representatives. Conversely every retained selection is an original catalogue selection and can be replayed without aliases.

This is a cost/witness-preserving reduction, not preservation of every original subset identity: discarded alternatives have a replacement mapping. It does not produce a global kernel of size bounded by (p,r,z,L), since the number of floor positions remains unrestricted. At most F*T original actions remain for F floors.

## Constructive bounded-state argument

Use a look-ahead window consisting of current floor f through f+L-1. Introduce future component vertices as they first enter this window; keep one permanent virtual anchor per profile, connected by a zero-cost edge to that profile's actual anchor component when its floor is present. Process baseline edges at their earliest endpoint floor, when both endpoints are available.

Decide the retained actions whose first touched floor is f; all their effect endpoints are in the window. Charge each once and introduce its profile edges. Remember selected representatives from earlier start positions until their last occupied/effect floor passes. There are at most L*T relevant representative IDs, irrespective of original catalogue density. Their occupied slot patterns determine all conflicts with new actions. Older actions whose last touched floor precedes f cannot conflict with future actions or activate future endpoints.

Maintain a connectivity partition of the window's profile-component vertices plus the p permanent anchors. Layer copies never receive cross-profile edges. Mark components containing a required target. When the last vertex of a component is forgotten, reject if it contains a target and is not connected to its anchor. All future incident effects have already been processed before forgetting, so a rejected closed component cannot be repaired later. A component connected to a permanent anchor cannot disappear entirely from the state. At the end, every target must lie in its profile anchor's component.

A state therefore needs the active representative choices, a connectivity partition, and target flags on its blocks. Costs are labels, not state dimensions. Identical states have exactly the same future effects/conflicts and remaining obligations; retain the best exact cost/count/sorted-ID witness.

With W <= prL+p retained component/anchor vertices, a loose state bound is 2^(LT) * Bell(W) * 2^W. At a start floor, consider at most 2^T subsets of its menu and reject resource conflicts. Processing has f(p,r,z,L) times polynomial(input-size) arithmetic work, plus polynomial geometric recognition and numeric/witness bit costs. This is a constructive FPT argument; its constants can be enormous. It is not a practicality or benchmark result, and the working proof still requires independent review.

## Why the premise differs from bounding the raw graph width

Take arbitrarily many two-floor installation alternatives with identical endpoint permissions and the same complete reserved slot, but distinct asset IDs and costs. They create a clique in the raw action-conflict graph, whose width grows with catalogue size, while p,r,z,L remain fixed. The signature reduction keeps one cheapest original action. Thus raw full-constraint width is not bounded before reduction merely from the physical parameters.

This demonstrates a potentially useful representation difference. It does not establish originality: these alternatives are constraint twins, and equivalent-vertex compression is established machinery. A positive claim must concern a genuinely useful physical characterization or a stronger result than a routine application of that machinery.

## Failure witnesses outside the class

- **Shared asset across actions:** expensive A and cheap B activate the same first transition using assets X and Y in the same slot. A later action C extends X through the next transition. A+C is consistent, while B+C collides at their shared floor. Dropping A solely because B has the same effect/slot signature is unsound. Complete private bundles are essential to this reduction.
- **Partial footprints in one named zone:** two candidates can have the same endpoint permissions and zone name, but different compatibility with a third footprint. A zone label alone cannot stand in for actual collision neighborhoods.
- **Declared exclusions or dependencies:** identical physical signatures may have different external constraints; those identities must be retained or a richer bounded signature proved.
- **Long bundles:** unbounded L permits arbitrarily many distant effects and long-lived choices. A claimed floor-width bound that ignores them is unsupported.
- **Arbitrary demands:** a boolean pending-target flag does not remember which distant terminal must join which component. Rooted demand semantics are essential; ordinary Steiner Forest width hardness is a direct warning.

## Originality audit still required

Compare against weighted twin/type compression, local finite-domain constraint optimization, labelled Steiner networks, and rooted connectivity DP. Lampis's arXiv:0910.0582v2 defines equivalent neighborhood types and proves exchange properties; the compression idea has prior art. Feldmann/Lampis ICALP 2024 explains why arbitrary active demands defeat width-only exact Steiner Forest methods. Fellows/Guo/Kanj 2010 shows that labels can remain hard at pathwidth two, making the bounded-span/signature premise material.

No inspected source yet directly states the entire proposed physical-menu theorem, but failure to locate that exact statement is **not evidence sufficient to establish novelty**. The unresolved question is whether the physical characterization is substantive enough for the thesis and survives a more direct equivalent-model audit. Until then this is the strongest concrete candidate from this pass, not an accepted originality claim.
