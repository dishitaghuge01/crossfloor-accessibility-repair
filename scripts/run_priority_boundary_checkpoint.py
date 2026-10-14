"""Fixed subset-transfer correctness checkpoint, not a timing experiment."""
import argparse
import hashlib
from itertools import combinations
from pathlib import Path
import random

from cfar.certificates import make_certificate, verify_certificate
from cfar.conflict_compilation import compile_activation_constraints, selection_admissibility
from cfar.io import manifest, write_json
from cfar.oracle import exact_oracle
from cfar.priority_boundaries import singleton_priority_shaft
from cfar.priority_cover import _compile_priority_structure, evaluate_priority_cover


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        parser.error("choose a new empty output directory")
    rows = []
    for seed in (0,1,2):
        rng = random.Random(seed)
        groups = [1,1,2,2,3,3]
        conflicts = [(i,j) for i in range(2) for j in range(2,6) if rng.random() < .5]
        instance = singleton_priority_shaft(groups,conflicts,3)
        structure = _compile_priority_structure(instance,[f"profile{i}" for i in range(3)])
        constraints = compile_activation_constraints(instance)
        checked = 0
        for size in range(7):
            for indices in combinations(range(6),size):
                selected = [instance["actions"][i]["action_id"] for i in indices]
                source = set(groups[i] for i in indices)=={1,2,3} and not any(i in indices and j in indices for i,j in conflicts)
                target = evaluate_priority_cover(structure,selected)["satisfied"] and selection_admissibility(constraints,selected)["admissible"]
                if source != target:
                    raise RuntimeError("subset transfer failed")
                checked += 1
        result = exact_oracle(instance)
        certificate = make_certificate(instance,result)
        verification = verify_certificate(instance,certificate)
        folder = output/f"seed{seed}"
        for filename, value in (("input.json",instance),("source.json",dict(groups=groups,conflicts=conflicts)),
                                ("result.json",result),("certificate.json",certificate),("verification.json",verification)):
            write_json(folder/filename,value)
        settings = dict(method="singleton_priority_subset_transfer",variant="SCFAR",subsets_checked=checked,
                        max_actions=20,timeout=None,runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
        write_json(folder/"manifest.json",manifest(instance,settings,result["status"],seed))
        rows.append(dict(seed=seed,subsets_checked=checked,status=result["status"],cost=result["cost"],
                         declared_conflicts=len(conflicts),geometry_conflicts=len(constraints["geometry_conflicts"])))
    write_json(output/"summary.json",rows)
    print(rows)


if __name__ == "__main__":
    main()
