"""Fixed correctness checkpoint: seeds 0,1,2; four edges, seven physical actions.

No timing benchmark. Geometry compilation is shared; optimization is independent.
"""
import argparse
import hashlib
from pathlib import Path
import random

from cfar.actions import apply_actions
from cfar.dp_interval_sweep import solve_interval_sweep
from cfar.dp_local_intervals import solve_local_shaft
from cfar.io import manifest, write_json
from cfar.obligations import verify_obligations
from cfar.oracle import exact_oracle
from cfar.priority_cover import _compile_priority_structure
from cfar.synthetic_shaft import make_shaft_instance


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        parser.error("choose a new empty output directory")
    rows = []
    runner_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    for seed in (0, 1, 2):
        rng = random.Random(seed)
        spans = [(0, 3, 1)]
        for _ in range(6):
            left = rng.randrange(4)
            spans.append((left, rng.randrange(left, 4), 1))
        instance = make_shaft_instance(4, spans, [10]+[rng.randint(1,5) for _ in range(6)],
                                       profiles=1, physical=True,
                                       asset_groups=[0]+[rng.randrange(8) for _ in range(6)])
        folder = output/f"seed{seed}"
        write_json(folder/"input.json", instance)
        local = solve_local_shaft(instance)
        constraints = local["compiled_constraints"]
        structure = _compile_priority_structure(instance, ["profile0"], validated=True)
        sweep = solve_interval_sweep(4, structure["intervals"],
                                    [c["actions"] for c in constraints["geometry_conflicts"]]+constraints["excludes"],
                                    list(constraints["blocked"]))
        if sweep["selected"] is not None:
            repair = apply_actions(instance, sweep["selected"], validated=True)
            paths = verify_obligations(instance, repair["active"])
            assert paths["satisfied"]
            sweep["verification"] = dict(reachability=paths, adjacency=repair["adjacency"], geometry=repair["geometry"])
        oracle = exact_oracle(instance)
        answers = dict(last_two=local, sweep=sweep, oracle=oracle)
        for method, result in answers.items():
            assert tuple(result[key] for key in ("status","cost","selected")) == tuple(oracle[key] for key in ("status","cost","selected"))
            write_json(folder/method/"result.json", result)
            write_json(folder/method/"manifest.json", manifest(instance,
                       dict(method=method, variant="SCFAR", checkpoint="three_way_correctness",
                            runner_sha256=runner_hash, max_actions=100 if method != "oracle" else 20,
                            max_states=100000 if method != "oracle" else None, timeout=None), result["status"], seed))
        rows.append(dict(seed=seed, cost=oracle["cost"], selected=oracle["selected"],
                         geometry_conflicts=len(constraints["geometry_conflicts"]), all_answers_equal=True))
    write_json(output/"summary.json", rows)
    print(rows)


if __name__ == "__main__":
    main()
