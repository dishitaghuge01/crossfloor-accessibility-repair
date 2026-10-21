# Building-network and event-lifetime study

This is a new, separate campaign; earlier unfavorable results remain frozen.
No new literature or replacement solver direction. Existing physical actions,
owned-interface DP, shared geometry, CP-SAT, greedy and replay are reused.

## Construction fixed before confirmatory timing

Use clinic and Molio inventories already fingerprinted in revised-source-audit.
Retain the largest consecutive run of occupied original storeys. Exact maximum
nonoverlap selection preserves room rings and IDs. All conservative source
background envelopes remain. Baseline doors use the existing shared-wall
annotation routine, not inferred IFC traversability. Profiles, reservations,
permissions and integer action costs are hypothetical.

A fixed1.6m grid supplies0.7m squares, at most two positions per consecutive
room pair. Select columns round-robin over endpoint pairs, before prices or
solving. Counts16,48,96 saturate at the available column count; duplicate
saturated catalogues are removed. Seeds0,1,2 vary integer abstract prices.
Each original column segment is a complete purchasable action; a multi-segment
column also offers one discounted indivisible bundle. Preserve all paid effects.
Demand every room in the largest potential connected network from its lowest
storey root, for both profiles. Save all rooms excluded from these obligations.
This is a source-derived controlled network, not real intervention validation.

## Exact implementation changes and proof obligation

Optional last-use cell deletion occurs only after a COMPLETE ownership unit
and only when no future available unit can occupy the cell. Original purchase
labels and full replay are retained. Optional last-use vertex deletion occurs
after its last baseline event/whole-unit event. Reject a partition block that
vanishes, exactly as in floor forgetting; the anchor is never deleted. These
are earlier safe forgetting transitions inside the same floor-interface DP.
They do not improve the published worst-case upper bound or establish priority.
The unchanged schedule/modes remain available for an ablation.

Compilation-scoped geometry memoization reuses successful fixed-connection,
fixed-pair, room/profile free-space and landing-access predicates. The cache
is local to ONE compile call and immutable input; ordinary replay is uncached.
All methods use the same current recognizer, so this is not a DP-only benefit.

## Measurement

Fresh processes; three repetitions; repeat-major, rotated method order; one
CP-SAT worker and seed0;100000 DP states and65536 cut columns. Function time
includes recognition and solve replay, excludes imports; parent wall time
includes imports. Timeouts include the entire worker. Use30s for confirmatory
runs and27s internal CP-SAT budget. Preserve every error/cap/timeout/incumbent.
Report CP-SAT cost-stage time separately from its exact count/ID completion.
No claim that identifier overhead establishes harder minimum-cost optimization.

Primary comparison: last-use uncompressed DP and CP-SAT, three repetitions
on seed0 at each source/size. Seeds1/2 are one-run price-robustness checks for
those two methods. Original uncompressed DP and improved greedy run once on
seed0 at each source/size. These deterministic comparisons assess status,
state counts and repair quality; single-run timings are explicitly descriptive.
Compressed last-use and cell-only modes run once on seed0 at each source/size
as secondary ablations. This policy avoids repeating deterministic capped
controls and is fixed before the clean campaign.
Do not drop failed cases or tune the schedule after observing final outcomes.
All methods replay paid boxes, exact cost, obligations and delta_A=0. Small
exhaustive correctness cases and the full regression suite precede the clean
campaign; large optimality is cross-method agreement, not exhaustive proof.

Development probe folders are explicitly excluded; they include changing code
and do not count as confirmatory measurements. Practical advantage is assessed
from the new data, never assumed. Report active components, unique contracted
network edges/cycle rank, obligations and genuine purchase interactions in
addition to room/action counts. An expanded but structurally simple catalogue
is not relabeled a difficult optimization success.
