# Exact slot-boundary subclass and independent reference

This is an elementary finite-state specialization used to independently validate
the authored local-band family. It is not a replacement general solver or a new
generic DP technique.

The recognized route graph for each profile is a chain of rooms, with common
left root and a terminal at a prefix endpoint. Divide it into consecutive bands.
Actions have complete support within one band; all physical owners belong to one
band. Different bands can collide only on common boundary landing cells, indexed
by at most s aligned slots. Within a band, exact owner equality permits reuse;
different owners in the same slot conflict. Distinct slots are disjoint fixed
rectangles. No dependencies, exclusions or nonlocal paid effects are admitted.
All unused paid effects still contribute occupancy. At most a actions belong to
one band; nonnegative costs and the original cost/count/sorted-ID objective apply.

Enumerate each band's2^a original-action subsets. Retain those with admissible
complete local occupancy and a permitted edge for each still-demanded profile on
each chain segment. For each retained subset compute left and right paid-slot
masks and its full objective label. Any global repair must satisfy exactly these
local requirements: a chain provides no route around a missing required segment.
Conversely these local conditions and disjoint consecutive boundary masks imply
complete global reachability and physical compatibility; no other inter-band
interaction is admitted.

For each outgoing mask retain the minimum label over prior masks disjoint from
the candidate left mask. Labels combine by exact cost/count addition and disjoint
ID union. The existing common-suffix order argument justifies one label per mask.
There are at most2^s incoming masks and2^a local choices, giving

    O(m 2^(a+s) poly(B))

time for m bands. This states a tractable subclass, not a hardness separation from
general decomposition algorithms. Standard finite-domain/path decomposition can
derive the same recurrence. In the released family a=8 and s=3; adjacent-band
conflicts and Q/U profile-specific purchases actually affect selected optima.

`scripts/local_band_reference.py` admits the generated chain/fixed-rectangle class,
enumerates256 local subsets and propagates at most eight masks. It does not call
the geometry compiler, recognizer, CP-SAT or owned-interface DP. It reads the
actual input costs/effects and emits complete selected IDs and a per-band ledger.
The generator's fixed geometry is checked separately, including rectangle shape,
owner-slot consistency, room containment by the declared six-by-four rectangles,
local support and common-root prefix demands. General input validation and replay
are supplied by the measured solvers and audit, not inferred from this reference.

Small tests compare its entire label to the exhaustive physical oracle and to
the general owned-interface DP on multiple seeds; malformed rectangles are rejected.
Larger input matches are untimed independent checks and excluded from measured
observation totals. No construction suitability or general spatial-kernel correctness
follows from this restricted reference.
