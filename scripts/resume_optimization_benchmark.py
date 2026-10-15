"""Complete interrupted measurements using the original frozen runner bytes.

Existing samples are reused only with matching fingerprints, method and status.
The original runner must remain byte-identical to its protocol. The coordinator
hash is additionally recorded; results are never silently rewritten.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

from cfar.io import fingerprint, manifest, write_json


def resume(output, runner, instances=None):
    protocol = json.loads((output/"protocol.json").read_text())
    if hashlib.sha256(runner.read_bytes()).hexdigest() != protocol["runner_sha256"]:
        raise ValueError("frozen runner bytes changed")
    sys.path.insert(0, str(runner.parent.resolve()))
    if instances:
        recipes = [(p.stem, 0, "building-derived-controlled", json.loads(p.read_text()))
                   for p in sorted(instances.glob("*.json"))]
    else:
        from run_controlled_benchmark import cases
        recipes = list(cases())
    if subprocess.check_output(["git", "status", "--porcelain"], text=True).strip():
        raise ValueError("clean original checkout required")
    if subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip() != protocol["git_revision"]:
        raise ValueError("revision differs from frozen protocol")
    coordinator = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    summary = []
    for name, seed, category, instance in recipes:
        folder = output/name
        input_file = folder/"input.json"
        if input_file.exists():
            if fingerprint(json.loads(input_file.read_text())) != fingerprint(instance):
                raise ValueError("input changed: "+name)
        else:
            write_json(input_file, instance)
        methods = list(protocol["methods"])
        if set(methods) & {"compressed", "uncompressed"} and len(instance["actions"]) <= 8 and category not in {"scope-control", "limit-control"}:
            methods.append("oracle")
        signatures = []
        for method in methods:
            for repeat in range(1 if method in {"greedy", "oracle"} else protocol["repetitions"]):
                target = folder/f"{method}-{repeat}.json"
                metadata = target.with_suffix(".manifest.json")
                cap = 1 if category == "limit-control" else 100000
                settings = dict(protocol, method=method, repetition=repeat, category=category, max_states=cap)
                if target.exists() and metadata.exists():
                    payload, old = json.loads(target.read_text()), json.loads(metadata.read_text())
                    if (old["git_dirty"] or old["git_revision"] != protocol["git_revision"] or
                        old["input_fingerprint"] != fingerprint(instance) or old["solver_status"] != payload["status"] or
                        old["settings"]["method"] != method or old["settings"]["repetition"] != repeat):
                        raise ValueError("existing measurement invalid: "+str(target))
                else:
                    if target.exists() or metadata.exists():
                        raise ValueError("orphaned measurement needs explicit review: "+str(target))
                    command = [sys.executable, str(runner.resolve()), "--worker", str(input_file.resolve()), method,
                               str(target.resolve()), str(cap), str(seed), str(protocol["cp_sat_total_budget_seconds"])]
                    try:
                        process = subprocess.run(command, capture_output=True, text=True, timeout=protocol["timeout_seconds"])
                        if process.returncode:
                            raise RuntimeError(process.stderr)
                        payload = json.loads(target.read_text())
                    except subprocess.TimeoutExpired:
                        payload = dict(status="timeout", timeout_seconds=protocol["timeout_seconds"])
                        write_json(target, payload)
                    settings["resume_coordinator_sha256"] = coordinator
                    write_json(metadata, manifest(instance, settings, payload["status"], seed))
                row = dict(case=name, category=category, method=method, repetition=repeat,
                           status=payload["status"], elapsed_seconds=payload.get("elapsed_seconds"))
                if "result" in payload:
                    r = payload["result"]
                    row.update(cost=r.get("cost"), selected=r.get("selected"), parameters=r.get("parameters"))
                    if r["status"] in {"optimal", "infeasible"}:
                        signatures.append((r["status"], r["cost"], r["selected"]))
                summary.append(row)
        if signatures and any(s != signatures[0] for s in signatures):
            raise RuntimeError("exact solver disagreement: "+name)
        write_json(output/"summary.json", summary)
        print(name, "complete", flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--runner", type=Path, required=True)
    p.add_argument("--instances", type=Path)
    a = p.parse_args()
    resume(a.output, a.runner, a.instances)
