# Exact event and retirement specification

This specifies the existing canonical/reverse solver schedule, not an additional
solver. Names are profile-component vertices after baseline floor contraction.
Each profile has a permanent `anchor`; its physical source vertex may retire
after being glued to that anchor. Complete units are connected components of
action–asset incidence among available purchases, not collision components.

## Ordered events

Number every operation below consecutively e1,...,em. Floors use recognized
elevation order; units use the recognizer's stable order. Initialize an anchor
block per profile. Introduce the first min(L,number of floors) floors in order.
At floor f:

1. Process baseline quotient edges whose earliest endpoint floor is f, in
   catalogue/profile enumeration order. Either omit from the thin witness or
   glue its two endpoints. No purchase is charged.
2. Process the complete units whose first support floor is f, in stable order.
   For each unit process its sorted original action IDs. Either skip or purchase;
   a purchase updates every paid cell before choosing independently a subset of
   the supplied connected effect components in each profile witness. Charge once.
   After the final action perform a distinct unit-close event.
3. Perform floor-forget f, then introduce floor f+L if it exists.

Reverse mode reverses baseline lists, unit lists at each floor and action lists
inside each unit. It does not reverse floors or split units. Intro creates every
required target on that floor, and glues the source to its anchor; optional
vertices enter only when a chosen witness uses them. All endpoints of an event
are inside the L-window because L covers complete unit supports and baseline
edges. The permanent anchor is never forgotten.

## Last use and owner identity

For a profile vertex v, lambda_V(v) is the largest edge/action event index that
can introduce an incident nonloop quotient edge, irrespective of selection.
After that event project v from all partitions, discarding any row in which a
whole unanchored block vanishes. Nodes with no such event retain ordinary floor
forgetting. This includes unreachable required targets; they must not disappear
without rejection. No selected witness can introduce v later, since all its
incident catalogue events have already occurred. Introduction of required
vertices occurs before these events and is performed exactly once.

For cell c, include unit-close events as physical tests/conversions. Define
lambda_C(c) as the final unit-close index among complete units containing any
available action that occupies c. Keeping c through that index is conservative
even if the unit's final action touching c occurred earlier. Before unit closure
its value is empty or the actual owner token (or external occupancy). After unit
closure surviving occupied values become external; no later unit contains that
owner, by the incidence-component definition. After lambda_C(c), erase c.
Thus owner retirement is never inferred from a connectivity retirement.

Floor forgetting remains a valid earlier boundary only because every relevant
support has finished before its earliest floor leaves the L-window. It erases
that floor's cells and projects its vertices with the same vanished-block test.

## State projection and objective

The state is occupancy plus one partition per profile. Its label is exact
nonnegative rational cost, original action count and sorted original ID tuple.
Projection never changes this label. Full selected effects remain available for
final materialization even when absent from a witness or retired from the key.
Identical projected keys merge by minimum label. Every future selection uses
unprocessed IDs disjoint from the prefix; union with a fixed disjoint suffix
preserves cost/count/lexicographic order. This justifies label dominance and
weighted representative selection after projection.

Any continuation can inspect only remaining vertices and cells. Partition
restriction preserves their connectivity; a vanished nonroot block can never
reach the root later. Resource erasure occurs only after the last relevant unit.
Conversely every original feasible repair has a thin root-connected witness and
passes these projections. Induction over the stated events therefore preserves
the minimum complete label, subject to the recognized model's existing proof.
Operational state/cut caps may stop execution; they never certify infeasibility.

## Event-width investigation: boundary of the present claim

A sound live width must count the union of all *potential* live vertices across
rows, not the size of a single selected witness. It must include eager target
introductions, transient action endpoints before projection, and physical owner
values through unit-close. Otherwise a large action/intro transition can be
hidden behind an artificially small post-projection width.

For b such potential vertices (excluding permanent anchors), and live domains
D(c) including empty/external/current owners, ordinary enumeration gives at most
product_c |D(c)| times 2^O(b log(b+2)) partition keys. Weighted representative
grouping is the route to a single-exponential connectivity term, but a final
runtime statement must also bound pre-reduction generation and the actual cut
row operations, not merely retained table size. No measured post-projection
maximum is substituted into a theorem without that derivation.

The preceding revision retained only the floor-interface theorem. This checkpoint
is superseded by docs/transient_frontier_theorem.md: the new bound explicitly
counts all eager/transient potential vertices and complete-unit cell domains, and
the private-bay family separates the two implemented state schedules. It is not
a priority claim over general decomposition algorithms. Eager target
introduction and complete-unit cell retention in particular prevent assuming
that short individual edge lifetimes always yield a smaller interface. This
fulfils the conservative branch of the requested investigation; an empirical
implementation refinement does not require inventing an additional theorem.
