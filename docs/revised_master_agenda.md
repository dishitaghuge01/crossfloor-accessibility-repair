# Revised-master improvement agenda (16 October 2026)

The user supplied a thirteen-page revised master and seventeen improvement
requests. The merged revision at 56dcb66 is the baseline; its CP-SAT, physical
hardness, pruning and multi-source evidence must be preserved. Attached prose
is an improvement agenda, not authority to assert missing priority or results.

## Reviewable milestones

| Items | Required deliverable | Current status |
| --- | --- | --- |
| 1 | Model-by-model expressibility / applicable algorithm / parameter dependence comparison | Existing concrete generic comparison retained; priority OPEN |
| 2 | One multi-room, two-profile ownership/full-paid-effect example | Existing examples cover features separately; integrated example pending |
| 3–4 | Parameter/lemma/pseudocode map and inspectable physical hardness proof | Existing proof and physical construction retained; presentation audit pending |
| 5–6 | Multi-room multi-floor source subsets with nontrivial adjacency and source denominators | Highest empirical priority; existing two-room source subsets insufficient |
| 7–8 | Fixed generator settings and genuine representative-compression stress | Pending; small row reduction must not become a speedup claim |
| 9 | Fair common-class CP-SAT comparison with bounds, censoring and memory | Existing comparison retained; expanded evidence schema pending |
| 10 | Whole-action pruning and bounded exchange | Implemented, targeted tests pass; clean benchmark evidence pending |
| 11–13 | Direct phase timing, fixed repeats, focused valid ablations | Pending; do not subtract independent timing measurements |
| 14 | Independent/hand-derived and metamorphic checks | Existing checks retained; additional metamorphisms pending |
| 15 | Standardized nullable evidence and smoke/full regeneration | Existing manifests retained; normalization pending |
| 16–17 | Contribution-led manuscript and explicit release gates | Existing revised master retained; new final manuscript pending |

## Improved greedy protocol

Historical `solve_greedy(instance)` remains unchanged in decision behavior.
`solve-greedy INPUT --improve --exchange-budget 100 --output runs/NEW` enables
postprocessing only after a feasible construction. It removes replay-redundant
actions, then deterministically first-improves by removing one or two selected
actions and inserting one unselected action. Each accepted selection strictly
improves exact cost, action count, then sorted original IDs. Every proposal uses
full action materialization and physical/reachability replay. No witness-only
occupancy is used. Pruning follows each accepted exchange.

The budget counts replayed exchange proposals, including physical failures;
non-improving labels are skipped. Pruning trials and removed actions are reported
separately. Construction makes at most catalogue-size selections. Exhausting
this local neighborhood or budget is not an optimality certificate. A failed
construction stays `heuristic_failed`; this milestone does not implement restart
or dead-end recovery. Settings are included in CLI manifests. Existing benchmark
results continue to mean historical greedy until explicitly rerun with the new
method label `whole_action_greedy_improved_v1`.

Targeted validation: 12 tests passed in 2.64 seconds, including full replay,
non-worsening, determinism, exact profile-case improvement, redundant deletion,
zero budget, invalid budgets and failure semantics. No full-regression or new
performance claim. Test observations include shared-asset cost 11 to 10 (exact
5) and separate-profile cost 4 to 3; these are not benchmark timing evidence.
