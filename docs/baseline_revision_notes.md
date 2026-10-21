# Baseline revision, 21 October 2026

## Measured motivation

A bounded development profile on clinic-network-16-s0 stopped after five calls
of the old heuristic materializer: total 19.519 s, apply_actions 17.694 s
(90.65%). This is a development diagnostic, not an optimization observation.
The raw profile is runs/greedy-profile-2026-10-21.json. Proposal materialization
repeated input validation, unchanged-floor adjacency, geometry and graph checks.

The revised heuristic uses the same recognized action-cell equivalence as the
exact solvers for complete paid effects and rebuilds active permissions for
proposal reachability. It never uses thin witnesses to waive occupancy. Final
repairs still undergo full materialization. Exhaustive proposal tests compare
compiled predicates and replay for every subset of the five authored scenarios.
An optional verified initial repair is distinguished from a cold start. Internal
deadlines preserve feasible repairs during local search; callbacks persist the
verified initial incumbent before improvement. External runners must preserve
those callbacks to retain a repair after hard termination.

## CP-SAT stages

Each stage now receives a purchase-variable hint from the preceding optimum.
This is internal stage continuation, not an externally supplied warm repair.
Blocked purchases already fixed to zero are omitted from identifier optimization.
Cost, count and the sorted-ID objective remain unchanged. Trace callbacks emit
unverified candidates; only completed full replay emits replay_verified=true.
Task A and Task B statuses/times are separate. No initial repair has been added
to cold CP-SAT runs.

The first diagnostic directory, runs/cp-stage-diagnostic-2026-10-21, is explicitly
INVALIDATED/development-only because source edits overlapped execution. Its
traces are preserved but must not enter final aggregates or support manuscript
claims. The runner now rejects code changes both before and after each run.
A clean diagnostic rerun is required. Historical timeouts remain untouched.

Checks before this milestone: 49 focused CP-SAT/heuristic tests passed in 4.25 s;
six exhaustive proposal/deadline tests passed in 0.86 s. A final material-change
regression run remains necessary before the final campaign.
