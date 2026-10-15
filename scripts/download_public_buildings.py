"""Download the pinned source catalogue to ignored storage; verify every hash."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request


def download(output):
    registry = Path(__file__).resolve().parents[1]/"docs/public_ifc_sources.json"
    output.mkdir(parents=True, exist_ok=True)
    for row in json.loads(registry.read_text())["sources"]:
        target = output/(row["building"]+".ifc")
        if target.exists():
            data = target.read_bytes()
        else:
            with urllib.request.urlopen(row["url"], timeout=60) as response:
                data = response.read()
        if hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise ValueError("source hash mismatch: "+row["building"])
        target.write_bytes(data)
        (output/(row["building"]+".source.json")).write_text(json.dumps(row, indent=2)+"\n")
        print(row["building"], len(data), flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, default=Path("data/external/public-buildings"))
    download(p.parse_args().output)
