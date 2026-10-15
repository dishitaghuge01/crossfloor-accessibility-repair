"""Same-model external baseline comparison; all timings remain in ignored runs.

Default recipes are precisely the existing 37 authored cases. --instances
accepts a directory of recognized public-building controlled inputs instead.
"""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter

from cfar.io import manifest, write_json
from cfar.errors import ValidationError


def worker(source, method, target, cap, seed, budget):
    instance = json.loads(Path(source).read_text())
    started = perf_counter()
    try:
        if method == "cp-sat":
            from cfar.cp_sat import solve_cp_sat
            result = solve_cp_sat(instance, time_limit=budget, seed=seed)
        elif method == "greedy":
            from cfar.greedy import solve_greedy
            result = solve_greedy(instance)
        elif method == "oracle":
            from cfar.oracle import exact_oracle
            result = exact_oracle(instance, max_actions=8)
        else:
            from cfar.dp_owned_interface import solve_owned_interface
            result = solve_owned_interface(instance, compress=method == "compressed", max_states=cap)
        payload = dict(status=result["status"], result=result, elapsed_seconds=perf_counter()-started)
    except ValidationError as e:
        payload = dict(status="limit_exceeded" if "LIMIT" in e.code else "unsupported",
                       error_code=e.code, error=str(e), elapsed_seconds=perf_counter()-started)
    write_json(target, payload)


def run(output, instances=None, repetitions=3, timeout=60):
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("fresh empty output required")
    if subprocess.check_output(["git", "status", "--porcelain"], text=True).strip():
        raise ValueError("commit source before collecting evidence")
    if instances:
        recipes = [(p.stem, 0, "building-derived-controlled", json.loads(p.read_text()))
                   for p in sorted(instances.glob("*.json"))]
    else:
        from run_controlled_benchmark import cases
        recipes = list(cases())
    protocol = dict(version=1, repetitions=repetitions, timeout_seconds=timeout,
        cp_sat_total_budget_seconds=max(.001, timeout-5), cp_sat_workers=1, oracle_max_actions=8,
        git_revision=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        ortools=importlib.metadata.version("ortools"), timing="function wall time including recognition and replay; excluding process startup/imports")
    write_json(output/"protocol.json", protocol)
    summary = []
    for name, seed, category, instance in recipes:
        folder = output/name
        write_json(folder/"input.json", instance)
        signatures = []
        methods = ["compressed", "uncompressed", "cp-sat", "greedy"]
        if len(instance["actions"]) <= 8 and category not in {"scope-control", "limit-control"}:
            methods.append("oracle")
        rows = []
        for method in methods:
            for repeat in range(1 if method in {"oracle", "greedy"} else repetitions):
                target = folder/f"{method}-{repeat}.json"
                cap = 1 if category == "limit-control" else 100000
                command = [sys.executable, str(Path(__file__).resolve()), "--worker", str(folder/"input.json"),
                           method, str(target), str(cap), str(seed), str(protocol["cp_sat_total_budget_seconds"])]
                try:
                    process = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
                    if process.returncode:
                        raise RuntimeError(process.stderr)
                    payload = json.loads(target.read_text())
                except subprocess.TimeoutExpired:
                    payload = dict(status="timeout", timeout_seconds=timeout)
                    write_json(target, payload)
                settings = dict(protocol, method=method, repetition=repeat, category=category, max_states=cap)
                write_json(target.with_suffix(".manifest.json"), manifest(instance, settings, payload["status"], seed))
                row = dict(case=name, category=category, method=method, repetition=repeat,
                           status=payload["status"], elapsed_seconds=payload.get("elapsed_seconds"))
                if "result" in payload:
                    result = payload["result"]
                    row.update(cost=result.get("cost"), selected=result.get("selected"), parameters=result.get("parameters"))
                    if result["status"] in {"optimal", "infeasible"}:
                        signatures.append((result["status"], result["cost"], result["selected"]))
                rows.append(row)
        if signatures and any(s != signatures[0] for s in signatures):
            raise RuntimeError("exact solver disagreement saved: " + name)
        summary.extend(rows)
        write_json(output/"summary.json", summary)
        print(name, ", ".join(f"{m}:{next(r['status'] for r in rows if r['method']==m)}" for m in methods), flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    p.add_argument("--instances", type=Path)
    p.add_argument("--repetitions", type=int, choices=[1, 3], default=3)
    p.add_argument("--timeout", type=float, default=60)
    p.add_argument("--worker", nargs=6)
    args = p.parse_args()
    if args.worker:
        worker(*args.worker[:3], int(args.worker[3]), int(args.worker[4]), float(args.worker[5]))
    elif args.output and args.timeout > 5:
        run(args.output, args.instances, args.repetitions, args.timeout)
    else:
        p.error("output and timeout greater than five seconds required")
