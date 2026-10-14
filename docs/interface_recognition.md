# M13: executable physical-interface recognition

`recognize_physical_interface` now recognizes a conservative rectangular subclass of M09 and reports p,r,z,L,g, exact occupied-cell ownership, complete action–asset coupling units, unary-blocked actions, per-profile baseline components and canonical floor order. It does not solve reachability or optimization and does not establish novelty.

## Recognition contract

The input first passes complete schema/semantic/asset consistency and baseline geometry validation. Candidate actions must be independent physical interventions containing only nonempty-profile portal activations, without doors, dependencies or exclusions. Every profile must have obligations with one common source. Distinct floor elevations define their order. Candidate asset identities must be disjoint from all existing catalogue assets.

The existing geometry compiler identifies unary failures and admissible actions. Available footprints must be exact axis-aligned rectangles. On each floor, their coordinate arrangement gives cells covered by at least one candidate asset; cells must have area above the kernel EPS. This sufficient condition rejects tiny arrangements conservatively rather than claiming they always lack another valid representation. Predicted distinct-owner cell collisions must equal the geometry compiler's pair failures exactly. Full selected-action footprints are retained, including geometry outside a required route.

Each action's occupancy includes only the footprint floors of its own effects. A shared asset's full catalogue footprint cannot be charged to every individual action. Complete action–asset incidence components define units; collision edges do not merge units. Unit span covers the geometry and endpoint support of all available actions in that unit. Unary-blocked actions are excluded from units and cell construction, but returned with their failure reasons.

Baseline within-floor connections are contracted independently for each profile. The current r counts **all** resulting components per floor, giving a safe conservative upper bound rather than pruning irrelevant components. L is the maximum complete unit span and active baseline inter-floor edge span, with minimum one. g is maximum unit asset count, zero for no available units. z counts occupied arrangement cells on the busiest floor. Parameter values are measured without applying any tractability threshold.

M10's independent fixed physical-background contract and representation corrections remain unsupported. Recognition is polynomial preprocessing with pairwise geometry compilation and rectangular arrangements; no linear-runtime or practical scaling claim is made. Doors require a separate opening-collision model.

## Usage and evidence

```powershell
.venv\Scripts\python.exe -m cfar.cli recognize-interface runs/m12-interface/atomic_bundle/input.json --output runs/interface-recognition
```

The CLI requires a fresh output directory and writes `recognition.json` plus a fingerprinted manifest with status `recognized`. That status means the stated structural contract passed, not that obligations are feasible or a repair is optimal.

The enhanced `scripts/run_interface_checkpoint.py` records recognition alongside the five authored oracle/certificate cases. Tests compare cell ownership with actual action application for all 44 selections, inspect shared-asset and multi-asset units, and reject dependencies, non-rooted obligations and unsafe EPS cells. Additional tests check unary filtering and the CLI manifest contract.

Next implement and verify original-action unit transitions and rooted route-witness states, then add representative compression. Existing exhaustive results remain the correctness baseline. Originality and independent proof validation remain pending; G3 stays OPEN.
