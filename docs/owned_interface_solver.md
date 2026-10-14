# M15: complete owned-cell route-witness solver

The working M09/M14 method is now implemented in `src/cfar/dp_owned_interface.py`, with CLI `solve-owned-interface`. It recognizes its physical class first, keeps full original geometry and costs, and uses optional rooted route witnesses plus product-profile representative bases. It supports compression-disabled comparisons. This is a scoped exact DP implementation, not a claim of established literature novelty or public-building performance.

## Implemented transitions and correctness argument

Introduce all component vertices in the current look-ahead window conceptually; mark required target components selected and attach each actual root to a permanent profile anchor. Other vertices become selected only through chosen witness components. Partitions record selected vertices and their connectivity separately by profile.

Process baseline edges at their first endpoint floor, branching on witness inclusion while leaving physical baseline materialization fixed. Process each complete installation unit at its first support floor. Within the unit, consider every original action once: skip, or pay its complete original cost and reserve all of its actual footprint cells. Reject a take overlapping an external or different-owner occupied cell. Verified same-owner reuse is allowed. Branch over subsets of the action's complete connected profile-graph components; these choices affect partitions only, never physical occupancy or charged effects. Erase owner identities only after the last action of that unit.

Forget a floor after every incident unit/baseline event. Reject when a selected non-anchor block loses its last live vertex; retain every block that still meets the boundary or permanent anchor. Drop expired occupied cells. Introduce the next look-ahead floor. At the end only anchored blocks survive, and all targets have been mandatory. Materialize the complete selected original actions and replay geometry and obligations before returning an optimal result.

For an optimum feasible repair, choose in each layer the root-connected components of its complete materialized graph as the witness. Every supplied connected component is wholly inside or outside that root component. Its inside components give a branch of these transitions; full geometry is retained on that branch. This proves completeness. Conversely, an accepting witness is contained in the fully materialized repair and contains every required target, proving soundness. Monotone fixed activations and exact recognized ownership ensure ignored graph edges cannot invalidate reachability and their paid geometry cannot escape checking.

At a fixed event, occupancy and partitions describe future compatibility; future original IDs are disjoint from processed IDs. Exact cost/count/sorted-ID labels therefore support ordinary dominance. Representative reduction groups only histories with identical occupancy and identical selected boundary sets. Anchored tensor cut rows preserve minimum labels for every joint rooted completion, using the M09 argument and attributed prior rank machinery. This gives the proposed h-based interface exponent; the implementation also imposes explicit raw-state and cut-column limits and raises named errors instead of reporting an unexplored optimum.

This is a self-contained project correctness argument supplemented by finite oracle comparisons, not independent theorem review. Baseline events are optional only in the route witness. The algorithm never shortens an original intervention, mixes profiles, splits atomic costs, or treats an ignored paid component as physically absent.

## Checks and reproducibility

Fifty new tests compare compressed and uncompressed modes with the oracle on the five authored examples and 40 deterministic seeded physical catalogs. Seeds vary profiles, spans, overlapping alternatives, same-asset reuse, zero/fractional costs and feasible/infeasible outcomes. A four-level cyclic access graph with six actions demonstrates actual representative row removal while preserving optimum cost and original IDs. Limit tests and CLI manifest checks cover operational behavior.

A 64-action private-alternative input has an analytically certified optimum: every feasible repair needs at least one action of cost at least one, and A0000 supplies the whole required route for cost one. All alternatives collide in one footprint. The DP keeps at most five raw states, rather than enumerating 2^64 selections. This demonstrates the intended catalogue-density behavior on that family, not general performance or a novel objective; geometry recognition still uses pairwise work.

`scripts/run_owned_interface_checkpoint.py` writes 46 small comparison cases, three manifests per case, full inputs/results and oracle certificates with separate replay verification. It also writes the dense-64 input/result/manifest with an explicit analytical comparison description. Generated artifacts remain ignored. The dense case is not exhaustively certified; the small cases are. Manifests include clean/dirty revision, source/input hashes, deterministic seed, runner hash, environment and method limits.

```powershell
.venv\Scripts\python.exe -m cfar.cli solve-owned-interface runs/m12-interface/atomic_bundle/input.json --output runs/owned-solve
.venv\Scripts\python.exe scripts/run_owned_interface_checkpoint.py --output runs/m15-owned-interface
```

The full regression suite passes 604 tests in 44.05 seconds before this implementation commit. Test duration is not a solver timing comparison. Existing fixed-background M10 corrections and candidate doors remain unsupported by recognition.

## Novelty gate

This completes a missing algorithm implementation and supplies comparative correctness evidence, including actual compression and a large-action analytical family. The positive target is the explicit physical owned-cell/unit parameterization, h-based bound, and full-action witness semantics. Weighted labelled connectivity, incidence-width optimization and representative bases are known methods. The combination requires a direct equivalent-method audit before calling it original. Choice-network full proofs remain only partially accessible; their path-cost/forbidden-edge model must not be silently treated as the same atomic installation model. G3 remains OPEN and novelty unestablished.
