# Hand-built micro-instances

These 18 JSON inputs are source-controlled, synthetic, author-designed test cases. `expected.json` contains manually specified strict and relaxed answers at topology weight 1. Regenerate the files with `python examples/build_micro_instances.py`; no random seed or external dataset is involved in their construction.

| ID | Failure or boundary | SCFAR answer | RCFAR answer (lambda=1) |
| --- | --- | --- | --- |
| 01 | Missing lift metadata | Restore relation, cost 1 | Same |
| 02 | Missing physical door on shared wall | Add door, cost 2 | Same, Delta_A=0 |
| 03 | Disconnected stair landing | Restore connector relation, cost 1 | Same |
| 04 | Profile-incompatible lift | Add distinct reserved lift, cost 4 | Same |
| 05 | Portal footprint outside room | Infeasible | Infeasible |
| 06 | Coupled three-floor portal relations | One bundle, cost 3 | Same |
| 07 | Topology-changing room extension | Infeasible | Cost 5, Delta_A=1 |
| 08 | Original design is feasible but dearer | Alternative cost 2; reference cost 5 | Same |
| 09 | Already accessible | Empty set, cost 0 | Same |
| 10 | No obligations | Empty set, cost 0 | Same |
| 11 | Action dependency | Both actions, cost 3 | Same |
| 12 | Necessary actions exclude one another | Infeasible | Infeasible |
| 13 | Portal/landing obstacle | Infeasible | Infeasible |
| 14 | Profile width failure | Infeasible | Infeasible |
| 15 | Free equal-cost alternatives | Single lexical-first action, cost 0 | Same |
| 16 | Local-only obligation | Door, cost 2 | Same |
| 17 | Joint overlap of profile-specific assets | Infeasible despite individual feasibility | Same |
| 18 | Ramp slope failure | Infeasible | Infeasible |

Invalid-input, geometric-boundary, forged-certificate, and seeded structural-DP checks are in `tests/`. The controlled coverage witness family in `synthetic_star.py` is separate from these 18 manual cases.
