# M02 controlled partition-DP checkpoint

Measured 14 October 2026 against committed implementation `b72316e`. All 28 solver/CLI manifests record that revision and a clean working tree. Runtime inputs, raw results and manifests remain in ignored `runs/m02-partition-checkpoint` and `runs/m02-partition-cli`. The source/plan hashes are retained in each benchmark manifest.

All nine paired instances agree with the exhaustive oracle on status, exact cost and selected IDs. Nine larger instances were run with the DP only. The separate coupled-portal CLI smoke returned cost 3 and action `coupled_chain`.

| Actions | Oracle median seconds | Partition DP median seconds |
| ---: | ---: | ---: |
| 4 | 0.0599 | 0.0150 |
| 8 | 0.9991 | 0.0168 |
| 10 | 4.1056 | 0.0204 |
| 32 | Not run | 0.0277 |
| 64 | Not run | 0.0425 |
| 128 | Not run | 0.0793 |

Medians are across three seeds, with one timed solve per seed/method and no warmup. These exploratory measurements include solver validation but exclude certificate generation and file writes. No variance, repeated-timing confidence interval or timeout result is claimed.

The graph is fixed at three chain edges, one existing lift and two experimental profiles: eight retained baseline components. At 128 actions the final tables contain [64, 64, 64] states for seeds 0, 1, 2. This demonstrates candidate-count growth at fixed graph size; it does not test floor-interface width or state growth on larger graphs.

All 152 tests pass, including cycles, different profile baselines, arbitrary obligation endpoints, jointly feasible physical activations, overlapping bundles, unsupported scopes, resource caps and exact large-integer costs. The unit suite has 49 additional partition cases beyond M01.

G3 remains open. This baseline uses established connectivity-partition machinery, supports only independent jointly feasible activation catalogues, keeps complete component graphs, and has no scalable independent optimality certificate. Public BIM extraction/evaluation and theory-equivalence review remain outstanding. See [fixed measurement plan](partition_benchmark_plan.md) and [algorithm scope/proof](partition_dp.md).
