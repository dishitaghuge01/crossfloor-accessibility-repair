"""Independent small-case certificate replay after optimization measurements."""
import argparse
import hashlib
import json
from pathlib import Path

from cfar.certificates import make_certificate, verify_certificate
from cfar.io import fingerprint, write_json


def replay(root):
    summary = []
    for folder in sorted(p for p in root.iterdir() if p.is_dir()):
        sample = folder/"oracle-0.json"
        if not sample.exists():
            continue
        instance = json.loads((folder/"input.json").read_text())
        result = json.loads(sample.read_text())["result"]
        metadata = json.loads(sample.with_suffix(".manifest.json").read_text())
        if metadata["git_dirty"] or metadata["input_fingerprint"] != fingerprint(instance):
            raise ValueError("oracle provenance mismatch")
        certificate = make_certificate(instance, result)
        verification = verify_certificate(instance, certificate, max_actions=8)
        if not verification["valid"]:
            raise ValueError("certificate failed: "+folder.name)
        write_json(folder/"oracle-certificate.json", certificate)
        row = dict(case=folder.name, valid=True, verification=verification,
                   input_fingerprint=fingerprint(instance), oracle_sha256=hashlib.sha256(sample.read_bytes()).hexdigest(),
                   checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
        write_json(folder/"oracle-replay.json", row)
        summary.append(row)
    write_json(root/"certificate-replay-summary.json", summary)
    print(len(summary), "certificates independently replayed")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--evidence", type=Path, required=True)
    replay(p.parse_args().evidence)
