# M12: executable physical interface proof probes

These five authored strict instances replace several graph-only analytical examples with complete schema-valid inputs: frozen rooms, floor elevations, reserved areas, fixed rectangular portal footprints, landings, profile capabilities, original action effects, costs and geometry certificates. They are controlled research inputs, not public BIM, installation designs or evidence of literature originality.

| Scenario | Expected optimum | What the input probes |
| --- | --- | --- |
| Shared asset | A000+A001, cost 5 | Two actions reuse one asset; a cheaper different owner in the same footprint conflicts with its extension. |
| Partial footprints | A000+A001, cost 2 | Distinct footprints sharing only a boundary coexist; an overlapping alternative conflicts. |
| Atomic bundle | A000, cost 3 | One original action activates two assets for one cost; separate actions cost 4. |
| Unused paid geometry | A000+A003, cost 6 | A000 also installs a disconnected portal beyond the required target; that portal blocks the cheap route extension. Omitting it from a reachability witness cannot remove its geometry. |
| Separate profiles | A001, cost 3 | A cheaper action supplies only one layer and cannot satisfy both profile obligations. |

The atomic example uses consecutive interfaces, rather than claiming to instantiate the earlier two-destination landing example. The partial-footprint example uses full 1 m square footprints with a 0.5 m offset; its existing reserved zone is not one exclusive slot. All cases use the current fixed 2D kernel. Fixed physical background independent of missing permissions, as proposed in M10, is not implemented by these cases.

Source constructor: `src/cfar/interface_scenarios.py`. Regression checks independently assert the expected optimum and key admissibility outcomes in the exhaustive ledger. Certificate checking uses separate replay and union-find reachability, with the schema/geometry kernel shared; its optimality check re-enumerates all subsets. This checks the authored expected outcomes, not the proposed rank-based algorithm, which remains unimplemented.

Run from the repository with its configured environment:

```powershell
.venv\Scripts\python.exe scripts/run_interface_checkpoint.py --output runs/m12-interface
```

The runner requires an empty output directory and writes each input, full oracle ledger, certificate, verification and manifest. Manifests include seed 0 (deterministic generation), input/source fingerprints, runner hash, revision/dirty status, environment and solver status. Generated artifacts remain ignored. There are 44 subsets across the five cases; certificate verification independently re-enumerates the same 44 selections.

This is a reproducible correctness checkpoint, not a timing or scaling benchmark. The next implementation step is a recognizer for exact collision cells, complete asset units and measured floor interfaces, checked against these fixtures and deliberate out-of-scope inputs before implementing compressed optimization. G3 remains open and originality provisional.
