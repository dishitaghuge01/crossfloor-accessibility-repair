from __future__ import annotations

import argparse
from decimal import InvalidOperation
import json
import time
from pathlib import Path

from .certificates import make_certificate, verify_certificate
from .errors import ValidationError
from .io import manifest, write_json
from .oracle import exact_oracle
from .dp_partition import solve_partition
from .schema import load_instance


def main() -> None:
    parser = argparse.ArgumentParser(description="Controlled CFAR exhaustive oracle and replay verifier")
    subparsers = parser.add_subparsers(dest="command", required=True)
    solve = subparsers.add_parser("solve")
    solve.add_argument("instance")
    solve.add_argument("--variant", choices=("SCFAR","RCFAR"), default="SCFAR")
    solve.add_argument("--topology-weight", default="1")
    solve.add_argument("--max-actions", type=int, default=20)
    solve.add_argument("--output", required=True, help="directory for ignored runtime artifacts")
    partition = subparsers.add_parser("solve-partition", help="strict jointly feasible activation catalogue only")
    partition.add_argument("instance")
    partition.add_argument("--max-components", type=int, default=16)
    partition.add_argument("--max-states", type=int, default=100000)
    partition.add_argument("--output", required=True)
    verify = subparsers.add_parser("verify")
    verify.add_argument("instance")
    verify.add_argument("certificate")
    verify.add_argument("--max-actions", type=int, default=20)
    validate = subparsers.add_parser("validate")
    validate.add_argument("instance")
    args = parser.parse_args()
    try:
        instance = load_instance(args.instance)
        if args.command == "validate":
            print(json.dumps({"valid":True,"building_id":instance["building_id"]}))
        elif args.command == "verify":
            certificate = json.loads(Path(args.certificate).read_text(encoding="utf-8"))
            print(json.dumps(verify_certificate(instance, certificate, args.max_actions)))
        else:
            output = Path(args.output)
            output.mkdir(parents=True, exist_ok=True)
            if any(output.iterdir()):
                raise ValidationError("OUTPUT_NOT_EMPTY", "choose a new run directory")
            started = time.perf_counter()
            if args.command == "solve-partition":
                result = solve_partition(instance, args.max_components, args.max_states)
                settings = {"method": result["method"], "variant": "SCFAR",
                            "max_components": args.max_components, "max_states": args.max_states,
                            "timeout": None, "elapsed_seconds": time.perf_counter()-started}
                write_json(output/"result.json", result)
                write_json(output/"manifest.json", manifest(instance, settings, result["status"]))
                print(json.dumps({"status": result["status"], "cost": result["cost"],
                                  "selected": result["selected"], "optimality_evidence": result["optimality_evidence"]}))
                return
            result = exact_oracle(instance,args.variant,args.topology_weight,args.max_actions)
            certificate = make_certificate(instance,result)
            verification = verify_certificate(instance,certificate,args.max_actions)
            settings = {"method":"exhaustive_oracle","variant":args.variant,
                        "topology_weight":args.topology_weight,"max_actions":args.max_actions,
                        "timeout":None,"elapsed_seconds":time.perf_counter()-started}
            write_json(output/"result.json",result)
            write_json(output/"certificate.json",certificate)
            write_json(output/"verification.json",verification)
            write_json(output/"manifest.json",manifest(instance,settings,result["status"]))
            (output/"ledger.jsonl").write_text("".join(json.dumps(r,sort_keys=True)+"\n" for r in result["ledger"]),encoding="utf-8")
            print(json.dumps({"status":result["status"],"cost":result["cost"],"selected":result["selected"],"certificate_valid":True}))
    except (ValidationError, KeyError, TypeError, ValueError, InvalidOperation) as error:
        parser.exit(2,f"{error}\n")


if __name__ == "__main__":
    main()
