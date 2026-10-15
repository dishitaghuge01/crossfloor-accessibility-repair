# Review revision: same-model optimization and structural scope

This milestone implements work requested by the manuscript review. It does not
declare literature priority, architectural constructibility or acceptance.

## Independent external optimizer

Install `.[test,optimization]`. `cfar solve-cp-sat INPUT --output runs/NEW`
uses OR-Tools 9.14.6206, one worker and an explicit total wall budget. The flow
formulation shares the geometry/interface recognizer with the DP, but does not
reuse its partitions, witnesses, representative reduction or floor sweep.

For each original action use a Boolean x. For each owner/cell use a Boolean y
equal to the OR of all actions using that pair; at most one distinct owner may
occupy each cell. These usages include every purchased effect. For each profile,
send integer flow from its root to every distinct required target. A baseline
edge is always enabled; a candidate edge is enabled iff at least one supplying
action is selected. The capacity is the number of non-root targets. Flow stays
on actual room edges. Purchase decisions never introduce route vertices.

Path decomposition proves equivalence to rooted reachability: routes supply an
integral flow, while each target receiving a unit must belong to the root's
enabled connected component (sum conservation over any other component).
Recognition's checked cell equivalence supplies the physical contract.

Optimize exact integer-scaled decimal cost, then action count, then maximize
inclusion of each ascending ID with all earlier optima fixed. With count fixed,
this produces the lexicographically smallest sorted selected tuple. Every stage
must be OPTIMAL; a budget expiration returns `limit_exceeded`, with a separately
replayed incumbent when available. Costs outside the safe integer range are
explicitly unsupported, rather than rounded. This is an executed standard
optimization baseline, not a novel flow algorithm or independent geometry proof.

`cfar solve-greedy` selects admissible whole actions by cost per newly reached
profile-room pair. It respects complete occupancy and same-owner reuse. A dead
end is `heuristic_failed`, never proof of infeasibility. It need not approximate
the optimum or solve cases requiring a non-gaining intermediate purchase.

## Structural improvement

Optional `solve-owned-interface --prune-irrelevant` removes unmarked contracted
baseline components from the connectivity abstraction. Mark sources, targets,
active cross-floor baseline endpoints and all available action endpoints,
separately per profile. An unmarked component has no possible external incident
edge and no obligation. Deleting it leaves reachability invariant for every
action subset. Complete physical action cells, prices, source room polygons and
IDs are preserved. The parameter r may therefore count marked components.

The full original map is still used for final materialization/certificates.
Default mode retains the historical all-component behavior for reproducibility.
This simple safe preprocessing is not claimed as a new algorithmic primitive.
A test adds ten isolated rooms per floor and checks r decreases from 11 to 1
without changing the exact label, input geometry or full footprint map.

## Hardness boundary in the actual physical class

`physical_set_cover.py` gives a two-floor, one-profile, collision-free physical
construction. Each Set Cover incidence gets its own aligned rectangular lift
patch on both floors, in a common source room below and the corresponding target
room above. Each nonempty set buys exactly its incidence portals as one unit-cost
action. No door or metadata action is used; all owners are private, so h=1 and
L=2. A target is reachable iff a selected set contains its element. Therefore
budgeted repair is NP-hard even with two floors, one profile and no collisions.
Membership in NP holds for the represented finite model with polynomial subset
verification. The construction has polynomial coordinates and size. It is
implemented and every subset is checked on several small witnesses.

This is a classical Set Cover transfer, not new hardness machinery. It rules out
floor-count-only polynomial/FPT claims unless P=NP. The component and collision
cell widths remain unbounded in this reduction, so it does not contradict the
bounded-interface theorem or prove its exponent optimal. It assumes arbitrary
multi-asset action bundles; no hardness for single-shaft actions is asserted.

## Evaluation requirements

Run `scripts/run_controlled_benchmark.py --output runs/NEW --optimizers` from a
clean committed checkout. This retains all 37 historical recipes and adds
three CP-SAT samples and one greedy sample per case. Recognition, compressed DP,
uncompressed DP and CP-SAT include recognition/replay in their timed functions;
imports and process startup are excluded. Oracle runs once on eligible <=8-action
cases. Store every status, seed, source fingerprint and environment manifest.
State limits and unsupported inputs remain distinct from infeasibility.

For public building inputs use the separately documented source audit and
controlled corruption protocol. Repaired subsets are evaluated under declared
experimental reservations/profiles/costs. An original IFC is not automatically
a valid accessibility ground truth or an optimal repair. Do not report a
multi-building result until the source inventories and strict replays execute.
