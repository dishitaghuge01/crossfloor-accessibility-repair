# M04: contiguous shaft repair and Priority Line Cover

14 October 2026. This is a transfer/equivalence checkpoint, not an original polynomial-time algorithm or established thesis novelty.

## Recognized repair restriction

Start with the jointly feasible independent SCFAR activation catalogue from M02. The caller supplies an explicit ordering of all profiles; no universal ordering of human mobility is assumed. A permission prefix of height h means exactly the first h profiles in that ordering.

Contract baseline room-pair links that are traversable by **every** profile. Parallel baseline connections may collectively supply those permissions. These universally free components are common to every profile and can be contracted safely. Form the simple quotient graph from remaining baseline and candidate-action links. Require that this graph be a connected path (or a single vertex). This is a combinatorial restriction; a vertical shaft with universally connected local access is one possible realization.

For each action, union its permissions on each affected quotient edge. Require the nonloop edges to form a contiguous path interval, and their permission sets to be the same nonempty prefix of height h. An action entirely inside universally free components is irrelevant to reachability and retains its cost as a no-op. This rules out noncontiguous bundles, variable permissions along one bundle, branching access, dependencies and collisions. Geometry/evidence is still checked by the strict kernel before optimization is compiled.

## Reduction and proof

Number path edges 0 through n-1. An obligation for profile p requires every edge on the unique path between its endpoint components. If baseline access already traverses an edge in profile p, that edge imposes no repair requirement for this obligation. Otherwise the obligation requires some selected action whose interval contains the edge and whose prefix height is at least rank(p).

For each edge e, set priority pi(e) to the maximum profile rank among all obligations requiring repair at e, or zero if none. Each action a becomes a costed interval [l(a),r(a)] with supply h(a). A selected set covers the repair requirements iff every positive-priority edge e belongs to an interval with h(a) >= pi(e). Cost is charged once per original action.

**Proof.** Universal baseline contraction preserves all profile paths. On the quotient path there is one possible simple route between obligation endpoints, so every missing profile-edge on it must be activated. The permitted profiles of an action are prefixes. Hence satisfying the largest missing profile rank at an edge also satisfies all smaller missing ranks there. These are exactly the priority-cover constraints. Conversely a priority cover activates every missing edge required by every obligation; adding their baseline edges gives the unique profile-valid route. Complete-union geometry and independence ensure that every selected subset remains admissible. Costs agree. This proves subset-level feasibility/cost correspondence for the recognized class.

Zero-priority edges may be removed and the remaining edge order compressed. The intersection of an original interval with the retained edges is still contiguous in that order. Retain the mapping to the full original action; an action that covers no retained edge is redundant. Thus the resulting instance is ordinary Priority Line Cover with positive priorities.

## Direct prior method and transfer boundary

Chakrabarty, Grant and Koenemann's [author-hosted full manuscript](https://www.cs.dartmouth.edu/~deepc/PUBS/CGK-full.pdf), dated 24 November 2009, defines this coverage rule and gives an exact polynomial-time algorithm (section 3.2, manuscript pp. 15-19, Theorem 10; IPCO 2010 bibliographic record, DOI 10.1007/978-3-642-13036-6_27). The definition and full recurrence/valley-minimality argument were inspected; this is not final-typesetting reconciliation. The restricted shaft model therefore does not establish a new polynomial-time result.

Their segment-completion step introduces subintervals at the original segment's cost. In this repair setting such subintervals can be used only as mathematical aliases: map each back to its original action, deduplicate IDs and replay the complete activation bundle. In the jointly feasible independent class, this cannot increase cost or destroy feasibility. These aliases are never permission to invent shorter physical interventions or assume their construction costs.

**Conflicts invalidate that transfer.** Consider priorities [2,1,1], interval A=[0,1] with supply 2/cost 1, B=[1,2] with supply 1/cost 1, and C=[0,2] with supply 2/cost 10. Plain cover chooses A+B at cost 2. If A and B are incompatible physical shaft alternatives, strict repair instead costs 10 using C. Shortening A's mathematical interval to edge 0 does not remove the conflict of its original physical action with B. The controlled geometric witness uses four frozen floors, overlapping reserved footprints for A/B and a separate footprint for C. This shows an actual scope obstruction, not novelty of the conflict problem.

## Implementation/evidence scope

Implement a recognizer/compiler and compare every subset against strict replay and profile reachability. Do not implement the prior polynomial-time algorithm as a supposedly new solver. The existing oracle can verify small mappings; a future PLC baseline must preserve original action provenance and explicitly handle the source's aliases.

Next research focus: constrained priority interval cover under physically justified reserved-asset incompatibility, with direct prior-work checks. Arbitrary conflicts or a generic bounded-width algorithm are not automatically new. G3 remains open and the overall thesis direction remains provisional.
