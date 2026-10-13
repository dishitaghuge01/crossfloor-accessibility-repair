"""Execute the fixed exploratory plan in docs/partition_benchmark_plan.md."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import random
import statistics
import time

from cfar.dp_partition import solve_partition
from cfar.io import manifest, write_json
from cfar.oracle import exact_oracle
from cfar.schema import ROOT
from cfar.synthetic_chain import make_chain_instance


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        parser.error("choose a new empty output directory")
    plan = ROOT/"docs/partition_benchmark_plan.md"
    experiment_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in (plan, Path(__file__).resolve())}
    rows = []
    for k in (4, 8, 10, 32, 64, 128):
        for seed in (0, 1, 2):
            rng = random.Random(seed)
            pairs = [(edge, pid) for edge in range(3) for pid in ("profile0", "profile1")]
            bundles = [pairs] + [[pair for pair in pairs if rng.random() < .35] for _ in range(k-1)]
            instance = make_chain_instance(3, bundles, [rng.randint(1, 9) for _ in range(k)])
            folder = output/f"k{k}-seed{seed}"
            write_json(folder/"input.json", instance)
            answers = {}
            methods = ("oracle", "partition") if k <= 10 else ("partition",)
            for method in methods:
                started = time.perf_counter()
                result = exact_oracle(instance, max_actions=10) if method == "oracle" else solve_partition(instance)
                elapsed = time.perf_counter()-started
                answers[method] = result
                settings = {"method": method, "variant": "SCFAR", "timeout": None,
                            "elapsed_seconds": elapsed, "max_actions": 10 if method == "oracle" else None,
                            "max_components": 16, "max_states": 100000, "experiment_fingerprints": experiment_hashes}
                write_json(folder/method/"result.json", result)
                write_json(folder/method/"manifest.json", manifest(instance, settings, result["status"], seed))
                row = {"actions": k, "seed": seed, "method": method, "seconds": elapsed,
                       "status": result["status"], "cost": result["cost"], "selected": result["selected"],
                       "states": result.get("states"), "transitions": result.get("transitions")}
                rows.append(row)
                print(f"k={k} seed={seed} {method}: {elapsed:.4f}s cost={result['cost']}", flush=True)
            if "oracle" in answers:
                if any(answers["oracle"][key] != answers["partition"][key] for key in ("status", "cost", "selected")):
                    raise RuntimeError(f"oracle disagreement k={k} seed={seed}")
    medians = [{"actions": k, "method": method,
                "median_seconds": statistics.median(r["seconds"] for r in rows if r["actions"] == k and r["method"] == method)}
               for k in (4, 8, 10, 32, 64, 128) for method in ("oracle", "partition")
               if any(r["actions"] == k and r["method"] == method for r in rows)]
    write_json(output/"summary.json", {"paired_instances_agree": 9, "dp_only_instances": 9,
                                       "rows": rows, "medians": medians, "experiment_fingerprints": experiment_hashes,
                                       "scope": "exploratory fixed-size controlled graph; one measurement per seed"})


if __name__ == "__main__":
    main()
