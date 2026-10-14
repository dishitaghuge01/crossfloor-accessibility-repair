"""One-command verified repair demonstration using an authored branching input."""
import argparse
import hashlib
from pathlib import Path

from cfar.actions import apply_actions
from cfar.certificates import make_certificate, verify_certificate
from cfar.dp_owned_interface import solve_owned_interface
from cfar.interface_recognition import recognize_physical_interface
from cfar.interface_scenarios import branching_rooms_probe
from cfar.io import manifest, write_json
from cfar.obligations import verify_obligations
from cfar.oracle import exact_oracle
from cfar.validation import baseline_active


def run_demo(output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("choose a new empty output directory")
    instance = branching_rooms_probe()
    before = verify_obligations(instance, baseline_active(instance))
    recognition = recognize_physical_interface(instance)
    result = solve_owned_interface(instance)
    oracle = exact_oracle(instance)
    signature = lambda r: (r["status"], r["cost"], r["selected"])
    if signature(result) != signature(oracle):
        raise RuntimeError("demo DP/oracle mismatch")
    certificate = make_certificate(instance, oracle)
    verification = verify_certificate(instance, certificate)
    repair = apply_actions(instance, result["selected"])
    delta = sum(a["delta"] for a in repair["adjacency"].values())
    summary = dict(status=result["status"], cost=result["cost"], selected=result["selected"],
                   before_satisfied=sum(path is not None for path in before["paths"].values()),
                   after_satisfied=sum(path is not None for path in result["reachability"]["paths"].values()),
                   obligations=len(instance["obligations"]), delta_A=delta,
                   certificate_valid=verification["valid"], parameters=recognition["parameters"],
                   statistics=result["statistics"], novelty_status="working contribution; originality provisional")
    for filename, value in (("input.json", instance), ("recognition.json", recognition),
                            ("before.json", before), ("result.json", result), ("oracle.json", oracle),
                            ("certificate.json", certificate), ("verification.json", verification),
                            ("repair.json", repair), ("summary.json", summary)):
        write_json(output/filename, value)
    settings = dict(method="verified_project_demo", variant="SCFAR", generation="deterministic_authored",
                    solver="owned_cell_rooted_interface_dp_v1", compression=True, max_states=100000,
                    max_cut_columns=65536, oracle_max_actions=20, timeout=None,
                    runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    write_json(output/"manifest.json", manifest(instance, settings, result["status"], seed=0))
    lines = ["# Verified cross-floor repair demo", "",
             f"Required routes satisfied: **{summary['before_satisfied']}/{summary['obligations']} before → "
             f"{summary['after_satisfied']}/{summary['obligations']} after**.", "",
             f"Selected original action: **{', '.join(result['selected'])}**. "
             f"Optimal cost: **{result['cost']} abstract action-cost units**. "
             f"Adjacency change: **{delta}**.", "",
             "Two profiles share one installation bundle. An existing door gives baseline access to one "
             "destination only for profile zero; the selected bundle supplies two new lifts for both profiles. "
             "Buying their separate actions costs four; the bundle costs three.", "",
             "| Profile | Required route | Before | After | Repaired room path |",
             "| --- | --- | --- | --- | --- |"]
    for obligation in instance["obligations"]:
        oid = obligation["obligation_id"]
        path = result["reachability"]["paths"][oid]
        lines.append(f"| {obligation['profile_id']} | {obligation['source']} → {obligation['target']} | "
                     f"{'Satisfied' if before['paths'][oid] else 'Unmet'} | "
                     f"{'Satisfied' if path else 'Unmet'} | {' → '.join(path or [])} |")
    lines += ["", "The compressed DP optimum matches the oracle's complete enumeration of eight selections; its certificate "
              "passes separate replay and union-find checking. Geometry/schema predicates are shared. "
              "Frozen rooms and adjacency are preserved.", "",
              "Measured parameters: " + ", ".join(f"{key}={value}" for key,value in recognition["parameters"].items()) + ".", "",
              f"Peak retained DP states: {result['statistics']['peak_retained_states']}.", "",
              "This is an authored fixed-2D demonstration. It is not public BIM or construction evidence. "
              "The working thesis contribution is frozen for development; literature originality remains provisional.", "",
              "Input, recognition, full repair, solver result, oracle ledger, certificate, verification and "
              "fingerprinted manifest are saved beside this report.", ""]
    (output/"report.md").write_text("\n".join(lines), encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description="Create a verified before/after thesis demo")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        summary = run_demo(Path(args.output))
    except ValueError as error:
        parser.exit(2, f"{error}\n")
    print(summary)
    print(f"Report: {(Path(args.output)/'report.md').resolve()}")


if __name__ == "__main__":
    main()
