"""Reproducible M01 acceptance run; all artifacts belong in ignored runs/."""
import argparse
import json
from pathlib import Path
import time

from cfar.certificates import make_certificate, verify_certificate
from cfar.io import manifest, write_json
from cfar.oracle import exact_oracle
from cfar.schema import ROOT, load_instance


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    output=Path(args.output)
    output.mkdir(parents=True,exist_ok=True)
    if any(output.iterdir()):
        parser.error("choose a new empty output directory")
    expected=json.loads((ROOT/"examples/expected.json").read_text())
    records=[]
    for name,answers in sorted(expected.items()):
        instance=load_instance(ROOT/"examples/micro"/(name+".json"))
        for variant in ("SCFAR","RCFAR"):
            start=time.perf_counter()
            result=exact_oracle(instance,variant,answers["topology_weight"])
            answer=answers[variant]
            actual={key:result.get(key) for key in answer}
            if actual != answer:
                raise AssertionError(f"{name}/{variant}: {actual} != {answer}")
            certificate=make_certificate(instance,result)
            verified=verify_certificate(instance,certificate)
            target=output/name/variant
            write_json(target/"result.json",result)
            write_json(target/"certificate.json",certificate)
            write_json(target/"verification.json",verified)
            settings={"method":"exhaustive_oracle","variant":variant,"topology_weight":answers["topology_weight"],
                      "max_actions":20,"timeout":None,"elapsed_seconds":time.perf_counter()-start}
            write_json(target/"manifest.json",manifest(instance,settings,result["status"]))
            (target/"ledger.jsonl").write_text("".join(json.dumps(r,sort_keys=True)+"\n" for r in result["ledger"]),encoding="utf-8")
            records.append({"instance":name,"variant":variant,"status":result["status"],"cost":result["cost"],
                            "delta_A":result.get("delta_A"),"subsets":len(result["ledger"]),
                            "input_fingerprint":result["input_fingerprint"],"certificate_valid":verified["valid"]})
    write_json(output/"summary.json",{"cases":len(records),"all_manual_answers_match":True,"records":records})
    print(json.dumps({"cases":len(records),"optimal":sum(r["status"]=="optimal" for r in records),
                      "infeasible":sum(r["status"]=="infeasible" for r in records),"all_certificates_valid":True}))


if __name__ == "__main__":
    main()
