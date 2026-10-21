# Safe early forgetting inside the owned-interface DP

This is an implementation refinement of the existing floor/unit schedule,
not a new repair model or a priority claim. Both switches default off.

For a fixed immutable recognized catalogue and actual canonical/reverse
schedule, count for each collision cell the complete unprocessed ownership
units with at least one available action occupying it. After processing a
whole unit, decrement exactly its cells. When a count becomes zero, erase
that cell from every state. Any continuation has no effect occupying it;
therefore its value cannot affect compatibility of a continuation. Previous
paid effects remain in the exact original-action label and final replay.
Before zero, preserve owner tokens within the unit and occupied bits across
units. In particular, never release a cell merely because the selected thin
witness omits an effect or because the current action is its last purchase.

For each profile/component vertex, similarly count remaining baseline edge
events and individual available actions with a permitted effect incident to
that vertex. After an event/action, when its count becomes zero, delete that
vertex from each witness partition. Reject a state if a non-anchor block
vanishes. The permanent anchor is never deleted. Every permitted continuation
can touch only other vertices, so a disappearing unanchored component could
never be connected to the root. For surviving blocks deletion preserves all
relations among vertices that a continuation can touch. This is the same
sufficient-state argument as ordinary floor forgetting, applied earlier.
Connectivity retirement can occur inside a complete unit; physical ownership
tokens are retained until unit completion. Required targets are still
introduced before all incident events because
complete-unit/baseline support defines L; no vertex can be reintroduced after
its last incident event. Vertices with no events retain ordinary floor
forgetting, so unreachable required targets still reject the state.

Merge only identical occupancy/partition keys with the original exact cost,
action count and sorted-ID ordering. Weighted representative reduction is
unchanged and is still prior machinery. Neither switch alters costs, complete
paid occupancy, fixed topology, profile separation or feasibility semantics.
The worst-case existing interface bound remains unchanged.

Geometry memoization is shared by every method using the recognizer. A cache
is created inside one compile call. Successful connection checks are keyed
by connection ID and full permitted profile set; pair overlap is independent
of profiles after those checks. Fixed room/profile centre space, obstacle
buffers and individual landing checks are reused. Failed predicates are not
cached. Rooms and obstacles do not depend on selected equipment in this
fixed kernel. No cache persists across edits/instances or replaces final
uncached materialization. This rationale does not extend to dynamic movement
obstacles or geometry-changing actions.

Validation before the clean campaign:760 tests passed111.18s after the main
change; following the obstacle-buffer cache,76 focused geometry/compiler/
lifetime tests passed12.21s. New lifetime tests compare both compression
modes and canonical/reverse schedules against exhaustive outcomes on authored
physical edge cases;30 seeded owner/profile/cost catalogues compare exact
status,cost and original IDs. Cache tests compare uncached predicate results
and error codes across selections of authored physical cases.

Final action-granularity refinement: full suite765 passed in72.93s.
