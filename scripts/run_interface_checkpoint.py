"""Exhaustive authored interface correctness checkpoint, not a benchmark."""
import argparse
import hashlib
from pathlib import Path

from cfar.certificates import make_certificate, verify_certificate
from cfar.interface_scenarios import EXPECTED_OPTIMA, authored_interface_scenarios
from cfar.interface_recognition import recognize_physical_interface
from cfar.io import manifest, write_json
from cfar.oracle import exact_oracle


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        parser.error("choose a new empty output directory")
    rows = []
    for name, instance in authored_interface_scenarios().items():
        recognition = recognize_physical_interface(instance)
        result = exact_oracle(instance)
        if (result["cost"], result["selected"]) != EXPECTED_OPTIMA[name]:
            raise RuntimeError(f"unexpected optimum: {name}")
        certificate = make_certificate(instance, result)
        verification = verify_certificate(instance, certificate)
        folder = output / name
        for filename, value in (("input.json", instance), ("recognition.json", recognition), ("result.json", result),
                                ("certificate.json", certificate), ("verification.json", verification)):
            write_json(folder / filename, value)
        settings = dict(method="authored_interface_exhaustive_checkpoint", variant="SCFAR",
                        generation="deterministic_authored", max_actions=20, timeout=None,
                        runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
        write_json(folder / "manifest.json", manifest(instance, settings, result["status"], seed=0))
        rows.append(dict(scenario=name, status=result["status"], cost=result["cost"],
                         selected=result["selected"], subsets=len(result["ledger"]), delta_A=result["delta_A"],
                         parameters=recognition["parameters"]))
    write_json(output / "summary.json", rows)
    print(rows)


if __name__ == "__main__":
    main()
