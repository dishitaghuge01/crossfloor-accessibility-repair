# Joint-interaction campaign protocol, 21 October 2026

The generated dataset has fifteen inputs: five frozen catalogue layouts from two
source buildings, each under three constraint tiers. Price seed is fixed at zero;
these are not fifteen independent geometries. Tiers are connectivity, resource
interaction (duplicate competing-owner footprints with cheaper alternative
segment actions), and full interaction (these alternatives restricted to profile0,
with profile0 demanding every second sorted target and profile1 every target).
Original segment purchases keep both profiles' permissions and form an explicit
feasible control. Compatible reuse and original bundles remain present.
Reservations, permissions, alternative owners, catalogue design and prices are
hypothetical experimental assumptions, not extracted construction facts.

Development smoke on Clinic16: connectivity30 actions/no conflict pairs;
resource42 actions/28 conflict pairs; full42 actions/28 pairs. Recognition succeeds
in all tiers. The cold greedy fails on the full tier in6.287s despite the known
feasible original-segment control: this is a useful trap, not infeasibility.
The separate segment worker replays that control successfully. Smoke observations
are excluded from the main campaign.

The main protocol selects all five layouts' full tier, plus Clinic16 connectivity
and resource tiers: seven catalogue/constraint combinations, two repetitions,
eight methods =112 scheduled observations. It is not a complete factorial study.
Two repetitions use forward then reverse order for every case, counterbalancing
every method pair. All runs are sequential fresh processes on one clean revision.
External pipeline deadline60s; CP and greedy internal deadline55s; no enforced
RAM cap. DP100000 raw-state cap and65536 cut-column cap. Solver seed0.
Five variants: floor, cells, vertices, both, both-rank. Other methods: CP-SAT with
internal preceding-stage hints, cold improved greedy, original-segment control.
No externally warm-started CP comparison is made. Two runs support ranges, not
confidence intervals or a population claim. This is a newly frozen campaign,
separate from all older revisions and the three posthoc CP diagnostics.

The generated protocol.json freezes every input fingerprint and actual run order
before execution. The driver rejects tracked edits/revision changes between runs.
CP candidate events are unverified until full replay; recovered timeout candidates
are audited outside the deadline and do not count as completed pipelines. Only
completed repairs/checkpoints with replay evidence count as verified feasibility.
Missing memory/phase fields on hard-killed workers remain missing. CPU load from
unrelated processes is not controlled; no other solver campaign is run concurrently.

Profile timers separately record generation, dictionary merging, reduction,
objective-label handling and complete phases. Label time is a subset of generation,
so it must not be summed twice. Vertex-union maxima are over observed states;
they are not the potential transient interface needed by a complexity theorem.
The owner-domain maximum includes empty/external/current-unit values. Per-yield
profiling adds overhead, shared by all five DP variants; do not compare these
instrumented times to old revisions as an isolated algorithmic effect.

Ablation changes within the five variants are isolated on identical inputs/code.
Tier changes alter permissions, conflicts, action count and/or demands together;
they do not isolate individual causal parameter effects. Separate eight-family
parameter studies and a final focused manuscript are still required by the wider
revision request. Existing historical parameter results cannot silently be pooled.
