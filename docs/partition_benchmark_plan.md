# Controlled partition-DP timing checkpoint

Declared 14 October 2026 before measurements. This exploratory checkpoint cannot pass G3 or establish novelty, a general performance advantage, or real-building validity.

- Family: synthetic_chain.make_chain_instance, three chain edges above one baseline lift, two experimental profiles, frozen room geometry. One obligation from the lower source to the chain end per profile.
- Seeds: 0, 1, 2, independently for each action count.
- Counts: 4, 8, 10 for paired exhaustive-oracle/partition-DP agreement and timing; 32, 64, 128 for DP-only timings. No oracle timeout claim for unrun sizes.
- Construction: action zero activates all six profile-edge pairs, ensuring feasible instances. Each subsequent pair is included independently with probability 0.35; empty bundles idempotently activate the baseline lift. Costs are independent integers 1 through 9 from Python random.Random(seed). Actions are representation corrections and may overlap.
- One timed solve per method/instance, oracle first at paired sizes, without certificate generation. Timings include solver recognition/validation, exclude generation and file writes; no warmup or repeated-timing statistical claim. State counts, transition counts, statuses, costs and selected IDs are retained. Every paired answer must agree exactly before a summary is written.
- Fixed caps: total components 16, live states 100000, oracle actions 10. No adaptive family changes after seeing results.
- Save inputs, results, environment/seed/input/source manifests, generator and runner fingerprints, and plan fingerprint under ignored runs/. Source and plan are committed before measurement. Report per-count median over seeds, raw measurements and limitations.

This family has at most eight retained components and a small state space. It deliberately tests growth in candidate action count at fixed graph size, not growth in floors, geometry complexity, interface width or profile count. Prior acceptance cases supply physical activations; this timing family supplies no construction validation evidence.
