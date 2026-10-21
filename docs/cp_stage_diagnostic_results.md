# Clean CP-SAT stage diagnostic, 21 October 2026

This is a separate post-hoc campaign, not a replacement for historical outcomes.
Code aad70e4; all three manifests report a clean tree. Input is the unchanged
Clinic 48-column, 78-action, price-seed-zero network instance. Settings: one
CP worker, solver seed zero, 27-second internal budget, 30-second external
pipeline deadline; no enforced RAM cap. Stage hints use the preceding optimum;
there is no external initial repair.

| Repeat | Cost stage | Cost search (s) | Count stage | Count search (s) | Finished ID stages / 78 | Pipeline status | Pipeline (s) |
|---|---|---:|---|---:|---:|---|---:|
| 0 | OPTIMAL,267 | 0.428 | OPTIMAL | 4.913 | 78 | optimal | 16.749 |
| 1 | OPTIMAL,267 | 0.967 | OPTIMAL | 10.941 | 51 | timeout | 30.025 |
| 2 | OPTIMAL,267 | 0.869 | OPTIMAL | 11.121 | 6 | timeout | 30.027 |

All three prove cost 267 and minimum action count. The two incomplete pipelines
reach identifier optimization; their callback selections are verified afterward
by the parent audit. That audit is outside the deadline and does not convert a
timeout into completed Task B. Search times exclude recognition/model/replay;
primary pipeline includes them. The completed pipeline includes solver replay.

The historical DP's three completions cannot be presented as minimum-cost
superiority over this baseline. The historical 30-second CP timeouts themselves
still lack their lost stage traces; this rerun explains current behavior rather
than retrospectively reconstructing erased evidence. A final one-revision paired
campaign with the DP is still required. The three diagnostic observations are
not included in the frozen 2362-observation total.

Artifacts: `runs/cp-stage-diagnostic-clean-2026-10-21/records.json`, individual
JSONL events and manifests; record hash in
`experiments/cp-stage-diagnostic-2026-10-21.json`. The earlier overlapping
development diagnostic remains invalidated and excluded.
