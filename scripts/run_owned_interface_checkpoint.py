"""Three-way DP/oracle correctness comparisons with independent replay."""
import argparse
import hashlib
from pathlib import Path
import random

from cfar.certificates import make_certificate, verify_certificate
from cfar.dp_owned_interface import solve_owned_interface
from cfar.interface_scenarios import (authored_interface_scenarios, branching_interface_probe,
                                     dense_alternative_probe,coupled_owner_probe,branching_rooms_probe)
from cfar.io import manifest, write_json
from cfar.oracle import exact_oracle
from cfar.resource_logic import compile_resource_logic, evaluate_resource_logic
from cfar.synthetic_shaft import make_shaft_instance


def cases():
    for name, instance in authored_interface_scenarios().items():
        yield name, 0, instance
    yield "cyclic", 0, branching_interface_probe()
    yield "branching-rooms", 0, branching_rooms_probe()
    for owners in (2,3,4):
        yield f"coupled-owners{owners}", 0, coupled_owner_probe(owners)
    for seed in range(40):
        rng = random.Random(seed)
        edges, profiles, count = rng.randint(1,4), rng.randint(1,3), rng.randint(1,6)
        intervals = []
        for _ in range(count):
            left = rng.randrange(edges)
            intervals.append((left,rng.randrange(left,edges),rng.randint(1,profiles)))
        instance = make_shaft_instance(edges,intervals,[rng.randrange(5)/4 for _ in range(count)],
                                      profiles=profiles,physical=True,
                                      asset_groups=[rng.randrange(8) for _ in range(count)])
        yield f"seed{seed:02d}", seed, instance


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True,exist_ok=True)
    if any(output.iterdir()):
        parser.error("choose a new empty output directory")
    rows = []
    for name, seed, instance in cases():
        oracle = exact_oracle(instance)
        compressed = solve_owned_interface(instance)
        full = solve_owned_interface(instance,compress=False)
        logic = compile_resource_logic(instance)
        for selection in oracle["ledger"]:
            logical = evaluate_resource_logic(logic,selection["selected"])
            if logical["admissible"] != (selection["status"] != "invalid") or logical["satisfied"] != (selection["status"] == "feasible"):
                raise RuntimeError(f"resource logic mismatch: {name}/{selection['selected']}")
        signature = lambda r: (r["status"],r["cost"],r["selected"])
        if signature(oracle) != signature(compressed) or signature(oracle) != signature(full):
            raise RuntimeError(f"DP mismatch: {name}")
        certificate = make_certificate(instance,oracle)
        verified = verify_certificate(instance,certificate)
        folder = output/name
        for filename,value in (("input.json",instance),("resource-logic.json",logic),("oracle.json",oracle),("compressed.json",compressed),
                               ("uncompressed.json",full),("certificate.json",certificate),("verification.json",verified)):
            write_json(folder/filename,value)
        for method,result in (("oracle",oracle),("compressed",compressed),("uncompressed",full)):
            settings = dict(method="owned_interface_three_way_correctness", compared_method=method,
                            variant="SCFAR",max_actions=20,max_states=100000,max_cut_columns=65536,
                            compression=method == "compressed",timeout=None,
                            runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
            write_json(folder/f"manifest-{method}.json",manifest(instance,settings,result["status"],seed))
        write_json(folder/"manifest-resource-logic.json",manifest(instance,
                   dict(method="owner_cell_resource_logic_v1",comparison="all_oracle_selections",
                        selections_checked=len(oracle["ledger"]),variant="SCFAR",timeout=None,
                        runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),"all_selections_matched",seed))
        rows.append(dict(case=name,seed=seed,status=oracle["status"],cost=oracle["cost"],
                         subsets=len(oracle["ledger"]),parameters=compressed["parameters"],
                         compressed_statistics=compressed["statistics"],uncompressed_statistics=full["statistics"]))
    write_json(output/"summary.json",rows)
    dense = dense_alternative_probe()
    dense_result = solve_owned_interface(dense)
    if (dense_result["cost"],dense_result["selected"]) != ("1",["A0000"]):
        raise RuntimeError("dense analytic optimum mismatch")
    write_json(output/"dense64"/"input.json",dense)
    write_json(output/"dense64"/"result.json",dense_result)
    write_json(output/"dense64"/"manifest.json",manifest(dense,
               dict(method=dense_result["method"],variant="SCFAR",max_states=100000,max_cut_columns=65536,
                    compression=True,timeout=None,comparison="analytic unit-cost lower bound and one-action witness",
                    runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),dense_result["status"],0))
    print(dict(cases=len(rows),subsets=sum(r["subsets"] for r in rows),
               rank_rows_removed=sum(r["compressed_statistics"]["representative_rows_removed"] for r in rows)))


if __name__ == "__main__":
    main()
