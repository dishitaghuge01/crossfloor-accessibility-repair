# Authoritative experiment protocol

## Frozen historical record

`experiments/freeze-2026-10-21.json` pins the code, manuscript, instances and
observations through SHA-256 hashes of the complete release archives. The
annotated local tag `research-freeze-2026-10-21` identifies the manifest commit;
the manifest records the earlier code revision which produced the release.
The archives remain in the ignored local freeze directory. Raw source buildings
and private documents are excluded. Do not overwrite these archives.

`experiments/campaign_registry.csv` gives six campaigns and their measured
revisions and record hashes. `experiments/instance_registry.csv` indexes 110
campaign-instance pairs, not 110 independent geometries. `not_recorded` means
the historical record did not separately identify that experimental dimension;
it must not be silently inferred. Per-run repetitions and solver seeds remain
in the immutable records/manifests. Price seeds are not solver seeds.

Historical totals: 2362 observations; 15 constructive network feasibility
controls are excluded from that denominator. Preliminary and development probes
are excluded. Network extension runs are post hoc, not pooled with the 30-second
core campaign. The historical core's rotation does not counterbalance the relative
order of its two repeated exact methods. No enforced RAM cap was used.

## Required new campaign contract

Freeze input fingerprints, settings, clean code revision and complete execution
schedule before running. Development smoke results never enter final aggregates.
Use sequential fresh workers, equal external deadlines and a recorded balanced
method schedule. Preserve every scheduled run, including errors and limits.
Keep all five DP ablations on one revision and identical inputs. Cold and warm
CP-SAT must remain separate, with preprocessing and initial selections explicit.

Record source_building_id, geometry_subset_id, catalogue_layout_id,
permission_pattern_id, conflict_pattern_id, price_seed, solver_seed and repeat_index.
Never call repeated prices independent layouts. Separate connectivity, resource
interaction and full interaction tiers; report coupled parameters honestly.

Task A reports cost incumbent, lower bound, proof, first/best feasible and proof
times. Task B additionally requires exact count and identifier stages. Persist
stage transitions and incumbent events before worker termination. A checkpoint
selection is unverified until required materialization/replay succeeds.

Primary timing includes model construction and required replay. Report optional
audit replay separately. Record phase timing, states, live vertices/cells/domain
sizes and memory; explicitly state any unmeasured field. Return verified heuristic
incumbents at deadline. Do not average timeout durations as completed runtimes.
Report exact completion, feasible completion, failures by cause, gaps and paired
times only where both methods complete the declared task.
